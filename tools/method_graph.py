import typer
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
from typing import Optional, List
from pathlib import Path

app = typer.Typer()

def collapse_to_modules(edge_list: List[tuple[str, str]]) -> List[tuple[str, str]]:
    return [(src.split(".")[0], tgt.split(".")[0]) for src, tgt in edge_list]

def build_method_graph(
    edge_list: List[tuple[str, str]],
    ignore_prefixes: Optional[List[str]] = None,
    collapse_modules: bool = False
) -> nx.DiGraph:
    if collapse_modules:
        edge_list = collapse_to_modules(edge_list)

    G = nx.DiGraph()
    for source, target in edge_list:
        if ignore_prefixes:
            if any(source.startswith(p) or target.startswith(p) for p in ignore_prefixes):
                continue
        G.add_edge(source, target)
    return G

def plot_method_graph(G: nx.DiGraph, title: str = "Method Call Graph", save_path: Optional[Path] = None):
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
    if save_path:
        plt.savefig(save_path)
        typer.echo(f"✅ Graph saved to {save_path}")
    else:
        plt.show()

@app.command()
def visualize(
    input_csv: Path = typer.Argument(..., help="Path to edge list or adjacency matrix CSV file."),
    use_matrix: bool = typer.Option(False, help="Treat input as adjacency matrix instead of edge list."),
    ignore_modules: Optional[str] = typer.Option(None, help="Comma-separated list of module prefixes to ignore."),
    collapse_modules: bool = typer.Option(False, help="Collapse to module-level nodes instead of functions."),
    graph_title: str = typer.Option("Method Call Graph", help="Title of the plot."),
    save_path: Optional[Path] = typer.Option(None, help="Optional path to save the plotted graph image.")
):
    """
    Visualize a method or module call graph from edge list or adjacency matrix.
    """
    if not input_csv.exists():
        raise typer.BadParameter(f"File does not exist: {input_csv}")

    if use_matrix:
        df = pd.read_csv(input_csv, index_col=0)
        edge_list = [(i, j) for i in df.index for j in df.columns if df.loc[i, j] > 0]
    else:
        df = pd.read_csv(input_csv)
        edge_list = list(df.itertuples(index=False, name=None))
        
    if collapse_modules:
        edge_list = [(src.split('.')[0], tgt.split('.')[0]) for src, tgt in edge_list]
        edge_list = [(src, tgt) for src, tgt in edge_list if src != tgt]  # 🔥 remove self-loops


    ignore_prefixes = [x.strip() for x in ignore_modules.split(",")] if ignore_modules else []
    G = build_method_graph(edge_list, ignore_prefixes, collapse_modules=collapse_modules)
    plot_method_graph(G, graph_title, save_path)

if __name__ == "__main__":
    app()
