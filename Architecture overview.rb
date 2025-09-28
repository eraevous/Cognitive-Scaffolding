Architecture overview
The Kairos Typer CLI aggregates commands for parsing, classification, embedding, search, and agent orchestration, and the pipeline.run_all wrapper sequences ingestion with clustering by delegating to the shared workflow backends.
Document ingestion copies uploads, extracts text, and seeds stub metadata before classification segments content semantically or by fallback chunking and summarizes it through the LLM helper.
Embedding generation and clustering rely on the OpenAI embedding API and a FAISS-backed vector store, producing artifacts consumed by semantic search, agent sessions, and downstream analytics.
Retrieval feeds into summarization, CLI search, and lightweight agent loops, with optional memory injection from the frame store.
Path configuration, logging, and budget tracking are shared cross-cutting services that supply directory resolutions, logging defaults, and API spend limits to the rest of the stack.

Diagram
flowchart LR
    subgraph UX
        CLI["Kairos CLI (Typer)\nparse/classify/embed/pipeline/search"]
    end
    subgraph Ingestion
        Upload["Upload & parse\ncore.storage.upload_local\ncore.parsing.*"]
        Classify["Metadata classification\ncore.workflows.main_commands"]
    end
    subgraph VectorPipeline
        Embed["Embedding generator\ncore.embeddings.embedder"]
        Index["Vector index & id map\ncore.vectorstore.faiss_store"]
    end
    subgraph Retrieval
        Retrieve["Retriever\ncore.retrieval.retriever"]
        Summ["Synthesis\ncore.synthesis.summarizer"]
        Agents["Agent hub & CLI\ncore.agent_hub / cli.agent"]
    end
    subgraph Analytics
        Cluster["Clustering & export\ncore.clustering.clustering_steps"]
    end
    subgraph Support
        Config["Path & remote config\nconfig_registry + path_config"]
        Logger["Logging & budget guard\ncore.logger + budget_tracker"]
        Memory["Frame store\ncore.memory.frame_store"]
    end
    LLM["LLM summarization\ncore.llm.invoke → OpenAI"]
    EmbedAPI["Embedding API\nOpenAI"]

    CLI --> Upload --> Classify --> Embed --> Index
    Index --> Retrieve --> Summ
    Retrieve --> Agents
    Index --> Cluster
    Summ -->|results| CLI
    Agents -->|context| CLI
    Memory -->|inject context| Summ
    Classify -->|prompt| LLM
    LLM -->|metadata JSON| Classify
    Summ -->|prompt| LLM
    LLM -->|summary text| Summ
    Embed -->|requests| EmbedAPI
    EmbedAPI -->|vectors| Embed
    Config -.-> CLI
    Config -.-> Upload
    Config -.-> Classify
    Config -.-> Embed
    Logger -.-> Classify
    Logger -.-> Embed
    Logger -.-> Retrieve
    Logger -.-> Agents