"""
Module: graph_tools/method_graph.py
@ai-path: graph_tools.method_graph
@ai-source-file: graph_tools/method_graph.py
@ai-module: method_graph
@ai-role: graph_constructor
@ai-entrypoint: build_method_graph()
@ai-intent: "Construct and visualize directed graphs representing method call dependencies across a codebase."

🔍 Summary:
Provides tools to create and visualize directed graphs based on method call relationships, enabling structural analysis and call chain visibility within the system.

📦 Inputs:
- adj_matrix (List[Tuple[str, str]]): List of (from_method, to_method) call relationships.

📤 Outputs:
- networkx.DiGraph: Graph object representing method call dependencies.

🔗 Related Modules:
- variable_graph.py → complementary graph creation for shared variables.

🧠 For AI Agents:
- @ai-dependencies: networkx, matplotlib
- @ai-calls: nx.DiGraph, nx.circular_layout, nx.draw_networkx_*
- @ai-uses: networkx, matplotlib
- @ai-tags: graph, call-tracing, visualization

⚙️ Meta:
@ai-version: 0.2.0
@ai-generated: true
@ai-verified: false

📝 Human Collaboration:
@human-reviewed: false
@human-edited: false
@last-commit: 
@change-summary: Initial extraction of method call graphing utilities
@notes: 
"""

import networkx as nx
import matplotlib.pyplot as plt

def build_method_graph(adj_matrix: list[tuple[str, str]]) -> nx.DiGraph:
    G = nx.DiGraph()
    for source, target in adj_matrix:
        G.add_edge(source, target)
    return G


def plot_method_graph(G: nx.DiGraph, title: str = "Method Call Graph"):
    plt.figure(figsize=(20, 16), dpi=120)
    pos = nx.circular_layout(G)
    nx.draw_networkx_nodes(G, pos, node_size=1100, edgecolors="black")
    nx.draw_networkx_labels(G, pos, font_size=8, font_weight="bold")
    nx.draw_networkx_edges(
        G, pos,
        arrowstyle="->",
        arrowsize=35,
        width=2.5,
        connectionstyle="arc3,rad=0.25"
    )
    plt.title(title, fontsize=18, pad=25)
    plt.axis('off')
    plt.tight_layout()
    plt.show()
