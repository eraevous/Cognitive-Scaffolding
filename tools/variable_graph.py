"""
Module: tools/variable_graph.py
@ai-path: tools.variable_graph
@ai-source-file: tools/variable_graph.py
@ai-module: variable_graph
@ai-role: graph_constructor
@ai-entrypoint: build_variable_graph()
@ai-intent: "Construct and visualize directed graphs representing shared variable dependencies across modules."

🔍 Summary:
Provides tools to create and visualize directed graphs based on shared variable dependencies. Useful for understanding coupling and modular structure across different parts of the codebase.

📦 Inputs:
- adj_matrix (List[Tuple[str, str]]): List of (from_var, to_var) dependencies.

📤 Outputs:
- networkx.DiGraph: Graph object representing variable dependencies.

🔗 Related Modules:
- method_graph.py → similar graph construction for method calls.

🧠 For AI Agents:
- @ai-dependencies: networkx, matplotlib
- @ai-calls: nx.DiGraph, nx.circular_layout, nx.draw_networkx_*
- @ai-uses: networkx, matplotlib
- @ai-tags: graph, visualization, dependency

⚙️ Meta:
@ai-version: 0.2.0
@ai-generated: true
@ai-verified: false

📝 Human Collaboration:
@human-reviewed: false
@human-edited: false
@last-commit: 
@change-summary: Initial extraction of graph generation logic
@notes: 
"""

import networkx as nx
import matplotlib.pyplot as plt

def build_variable_graph(adj_matrix: list[tuple[str, str]]) -> nx.DiGraph:
    G = nx.DiGraph()
    for source, target in adj_matrix:
        G.add_edge(source, target)
    return G


def plot_variable_graph(G: nx.DiGraph, title: str = "Shared Variable Graph"):
    plt.figure(figsize=(18, 14), dpi=120)
    pos = nx.circular_layout(G)
    nx.draw_networkx_nodes(G, pos, node_size=1000, edgecolors="black")
    nx.draw_networkx_labels(G, pos, font_size=8, font_weight="bold")
    nx.draw_networkx_edges(
        G, pos,
        arrowstyle="->",
        arrowsize=30,
        width=2,
        connectionstyle="arc3,rad=0.15"
    )
    plt.title(title, fontsize=16, pad=20)
    plt.axis('off')
    plt.tight_layout()
    plt.show()
