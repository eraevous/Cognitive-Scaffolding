#__________________________________________________________________
# File: ast_dependency_extractor.py
"""
Module: tools/ast_dependency_cli.py
@ai-path: tools.ast_dependency_cli
@ai-source-file: tools/ast_dependency_cli.py
@ai-module: ast_dependency_cli
@ai-role: dependency_analyzer_cli
@ai-entrypoint: analyze()
@ai-intent: "Extract and optionally visualize function-level call graphs from a Python codebase using static AST parsing."

🔍 Summary:
This CLI tool uses static analysis to parse Python source code and extract function-level dependency graphs. It supports recursive scanning, directory exclusion, and optional export as either an edge list or adjacency matrix. Output can be directed to CSV, and a reusable `.graphconfig.json` file allows for consistent configuration. The tool integrates AST traversal with basic module naming resolution and supports future visualization extensions.

📦 Inputs:
- source_dir (str): Directory to scan for `.py` files.
- recursive (bool): Whether to include subdirectories in the search.
- ignore_dirs (str): Comma-separated list of folders to exclude.
- output (Path): Optional CSV file path to write results.
- matrix (bool): Whether to export as an adjacency matrix instead of edge list.
- config (Path): Optional path to a `.graphconfig.json` file.

📤 Outputs:
- Printed or exported CSV table of dependency edges or adjacency matrix.

🔗 Related Modules:
- graph_tools.variable_graph → for rendering shared variable graphs
- graph_tools.method_graph → for plotting function call graphs
- json, os, ast, pandas, typer, pathlib

🧠 For AI Agents:
- @ai-dependencies: ast, os, typer, pandas, json, pathlib, networkx
- @ai-calls: ast.parse, os.walk, Path.glob, Path.rglob, typer.echo, json.load, pd.DataFrame.to_csv
- @ai-uses: Path, Dict, List, DataFrame, typer.Option, networkx.DiGraph
- @ai-tags: cli, static-analysis, AST, call-graph, visualization, modularity

⚙️ Meta:
@ai-version: 0.2.0
@ai-generated: true
@ai-verified: false

📝 Human Collaboration:
@human-reviewed: false
@human-edited: false
@last-commit: Added --ignore-dirs and .graphconfig.json support (2024-05-01)
@change-summary: Refactored CLI to support reusable config and selective file traversal.
@notes: Ready for integration with graph plotting and docstring verification pipelines.
"""

"""
Module: tools/ast_dependency_cli.py
@ai-path: tools.ast_dependency_cli
@ai-source-file: tools/ast_dependency_cli.py
@ai-module: ast_dependency_cli
@ai-role: dependency_analyzer_cli
@ai-entrypoint: analyze()
@ai-intent: "Extract and optionally visualize function-level call graphs from a Python codebase using static AST parsing."

🔍 Summary:
This CLI tool uses static analysis to parse Python source code and extract function-level dependency graphs. It supports recursive scanning, directory exclusion, and optional export as either an edge list or adjacency matrix. Output can be directed to CSV, and a reusable `.graphconfig.json` file allows for consistent configuration. The tool integrates AST traversal with basic module naming resolution and supports future visualization extensions.

📦 Inputs:
- source_dir (str): Directory to scan for `.py` files.
- recursive (bool): Whether to include subdirectories in the search.
- ignore_dirs (str): Comma-separated list of folders to exclude.
- output (Path): Optional CSV file path to write results.
- matrix (bool): Whether to export as an adjacency matrix instead of edge list.
- config (Path): Optional path to a `.graphconfig.json` file.

📤 Outputs:
- Printed or exported CSV table of dependency edges or adjacency matrix.

🔗 Related Modules:
- graph_tools.variable_graph → for rendering shared variable graphs
- graph_tools.method_graph → for plotting function call graphs
- json, os, ast, pandas, typer, pathlib

🧠 For AI Agents:
- @ai-dependencies: ast, os, typer, pandas, json, pathlib, networkx
- @ai-calls: ast.parse, os.walk, Path.glob, Path.rglob, typer.echo, json.load, pd.DataFrame.to_csv
- @ai-uses: Path, Dict, List, DataFrame, typer.Option, networkx.DiGraph
- @ai-tags: cli, static-analysis, AST, call-graph, visualization, modularity

⚙️ Meta:
@ai-version: 0.2.0
@ai-generated: true
@ai-verified: false

📝 Human Collaboration:
@human-reviewed: false
@human-edited: false
@last-commit: Added --ignore-dirs and .graphconfig.json support (2024-05-01)
@change-summary: Refactored CLI to support reusable config and selective file traversal.
@notes: Ready for integration with graph plotting and docstring verification pipelines.
"""

import ast
import json
import os
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

import networkx as nx
import pandas as pd
import typer

app = typer.Typer()

class ASTDependencyExtractor:
    def __init__(self):
        self.defined_functions: Dict[str, Tuple[str, int]] = {}
        self.imports: Dict[str, str] = {}  # alias or name → full module
        self.edges: List[Tuple[str, str]] = []
        self.current_module: str = ""

    def process_file(self, filepath: str, module_name: str):
        self.current_module = module_name
        self.imports = {}  # reset for each file
        with open(filepath, "r", encoding="utf-8") as f:
            try:
                tree = ast.parse(f.read(), filename=filepath)
                self._walk_tree(tree)
            except SyntaxError:
                typer.echo(f"⚠️  Skipping {filepath} due to syntax error.")

    def _walk_tree(self, tree: ast.AST):
        class ImportResolver(ast.NodeVisitor):
            def __init__(self, extractor):
                self.extractor = extractor

            def visit_Import(self, node):
                for alias in node.names:
                    self.extractor.imports[alias.asname or alias.name] = alias.name

            def visit_ImportFrom(self, node):
                module = node.module
                for alias in node.names:
                    name = alias.name
                    full_name = f"{module}.{name}" if module else name
                    self.extractor.imports[alias.asname or name] = full_name

        class CallVisitor(ast.NodeVisitor):
            def __init__(self, extractor):
                self.extractor = extractor
                self.current_func = None

            def visit_FunctionDef(self, node: ast.FunctionDef):
                full_name = f"{self.extractor.current_module}.{node.name}"
                self.extractor.defined_functions[full_name] = (self.extractor.current_module, node.lineno)
                self.current_func = full_name
                self.generic_visit(node)
                self.current_func = None

            def visit_Call(self, node: ast.Call):
                if self.current_func:
                    callee_name = self._resolve_name(node.func)
                    if callee_name:
                        self.extractor.edges.append((self.current_func, callee_name))
                self.generic_visit(node)

            def _resolve_name(self, node):
                name = self._get_name(node)
                if name is None:
                    return None
                root = name.split(".")[0]
                if root in self.extractor.imports:
                    resolved = self.extractor.imports[root]
                    return name.replace(root, resolved, 1)
                return f"{self.extractor.current_module}.{name}"

            def _get_name(self, node):
                if isinstance(node, ast.Name):
                    return node.id
                elif isinstance(node, ast.Attribute):
                    value = self._get_name(node.value)
                    return f"{value}.{node.attr}" if value else node.attr
                elif isinstance(node, ast.Call):
                    return self._get_name(node.func)
                return None

        ImportResolver(self).visit(tree)
        CallVisitor(self).visit(tree)

    def get_function_edges(self) -> List[Tuple[str, str]]:
        return self.edges

    def get_function_defs(self) -> Dict[str, Tuple[str, int]]:
        return self.defined_functions


def build_adjacency_matrix(edges: List[Tuple[str, str]]) -> pd.DataFrame:
    nodes = sorted(set([src for src, _ in edges] + [dst for _, dst in edges]))
    matrix = pd.DataFrame(0, index=nodes, columns=nodes)
    for src, dst in edges:
        if dst in matrix.columns:
            matrix.loc[src, dst] = 1
    return matrix


def should_ignore_dir(dir_name: str, ignore_dirs: List[str]) -> bool:
    """Check if a directory should be ignored based on its name."""
    return dir_name in ignore_dirs


def collect_py_files(root_dir: Path, ignore_dirs: List[str]):
    py_files = {}
    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if not should_ignore_dir(d, ignore_dirs)]
        files = [f for f in filenames if f.endswith(".py")]
        if files:
            rel_path = Path(dirpath).relative_to(root_dir)
            py_files[rel_path] = [Path(dirpath) / f for f in files]
    return py_files


def load_graph_config(path: Path) -> Dict:
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


@app.command("analyze")
def analyze(
    source_dir: str = typer.Option(".", help="Directory to scan for Python files."),
    recursive: bool = typer.Option(True, help="Recursively scan subdirectories."),
    ignore_dirs: str = typer.Option("venv,.git,.pytest_cache,Scratch,tests,env,Combined_Scripts", help="Comma-separated list of directories to ignore."),
    output: Path = typer.Option(None, help="Optional CSV output file."),
    matrix: bool = typer.Option(False, help="Output as adjacency matrix instead of edge list."),
    config: Path = typer.Option(Path(".graphconfig.json"), help="Optional path to graph config JSON file.")
):
    """Extract function call dependencies from Python code."""
    config_data = load_graph_config(config)
    source_path = Path(config_data.get("source_dir", source_dir))
    ignore_dirs_list = config_data.get("ignore_dirs", ignore_dirs).split(",")

    extractor = ASTDependencyExtractor()
    files = collect_py_files(source_path, ignore_dirs_list)
    for rel_path, py_paths in files.items():
        for file_path in py_paths:
            mod_name = str(rel_path / file_path.name).replace("/", ".").replace(".py", "")
            extractor.process_file(str(file_path), module_name=mod_name)

    edges = extractor.get_function_edges()

    if matrix:
        df = build_adjacency_matrix(edges)
    else:
        df = pd.DataFrame(edges, columns=["Source", "Call"])

    if output:
        df.to_csv(output, index=(matrix is True))
        typer.echo(f"✅ Output written to {output}")
    else:
        typer.echo(df)

if __name__ == "__main__":
    app()
#__________________________________________________________________
# File: combine_scripts.py
"""
Module: tools/combine_scripts.py
@ai-path: tools.combine_scripts
@ai-source-file: tools/combine_scripts.py
@ai-module: combine_scripts
@ai-role: source_aggregator
@ai-entrypoint: combine_scripts()
@ai-intent: "Combine Python source files from multiple directories into aggregated scripts with docstring extraction and summary logging."

🔍 Summary:
This module provides a CLI tool for recursively scanning Python files under a specified root directory and combining them into single monolithic scripts per subdirectory. Each file is prepended with its module-level docstring (if present) and clearly separated with a marker line. The tool supports directory exclusion, creates a summary CSV log with line counts, and writes all outputs into a user-defined folder.

📦 Inputs:
- root (Path): Root directory to search for `.py` files.
- ignore_dirs (str): Comma-separated list of directories to exclude (e.g., `env,tests`).
- output_dir (str): Folder where combined scripts will be written.
- log_csv (str): CSV filename for output statistics.

📤 Outputs:
- Combined `.combined.py` files written to the output directory
- A CSV summary log of file counts and total lines per bundle

🔗 Related Modules:
- tools.ast_dependency_cli → for analyzing call graphs post-combination
- csv, pathlib, typer, os

🧠 For AI Agents:
- @ai-dependencies: os, csv, pathlib, typer
- @ai-calls: collect_py_files, extract_module_docstring, combine_files, csv.writer
- @ai-uses: SEPARATOR, Path, List, open, readlines, mkdir, write_text
- @ai-tags: cli, code-combiner, docstring-parser, logging, directory-walker

⚙️ Meta:
@ai-version: 0.2.0
@ai-generated: true
@ai-verified: false

📝 Human Collaboration:
@human-reviewed: false
@human-edited: false
@last-commit: Added inline docstring extraction and summary logging support (2024-05-01)
@change-summary: Builds a monolithic script per directory, prepends file docstrings, logs summary stats to CSV
@notes: Ideal for bundling source files into reviewable or AI-trainable scripts.
"""

"""
Module: tools/combine_scripts.py
@ai-path: tools.combine_scripts
@ai-source-file: tools/combine_scripts.py
@ai-module: combine_scripts
@ai-role: source_aggregator
@ai-entrypoint: combine_scripts()
@ai-intent: "Combine Python source files from multiple directories into aggregated scripts with docstring extraction and summary logging."

🔍 Summary:
This module provides a CLI tool for recursively scanning Python files under a specified root directory and combining them into single monolithic scripts per subdirectory. Each file is prepended with its module-level docstring (if present) and clearly separated with a marker line. The tool supports directory exclusion, creates a summary CSV log with line counts, and writes all outputs into a user-defined folder.

📦 Inputs:
- root (Path): Root directory to search for `.py` files.
- ignore_dirs (str): Comma-separated list of directories to exclude (e.g., `env,tests`).
- output_dir (str): Folder where combined scripts will be written.
- log_csv (str): CSV filename for output statistics.

📤 Outputs:
- Combined `.combined.py` files written to the output directory
- A CSV summary log of file counts and total lines per bundle

🔗 Related Modules:
- tools.ast_dependency_cli → for analyzing call graphs post-combination
- csv, pathlib, typer, os

🧠 For AI Agents:
- @ai-dependencies: os, csv, pathlib, typer
- @ai-calls: collect_py_files, extract_module_docstring, combine_files, csv.writer
- @ai-uses: SEPARATOR, Path, List, open, readlines, mkdir, write_text
- @ai-tags: cli, code-combiner, docstring-parser, logging, directory-walker

⚙️ Meta:
@ai-version: 0.2.0
@ai-generated: true
@ai-verified: false

📝 Human Collaboration:
@human-reviewed: false
@human-edited: false
@last-commit: Added inline docstring extraction and summary logging support (2024-05-01)
@change-summary: Builds a monolithic script per directory, prepends file docstrings, logs summary stats to CSV
@notes: Ideal for bundling source files into reviewable or AI-trainable scripts.
"""


import csv
import os
from pathlib import Path
from typing import List

import typer

app = typer.Typer()

SEPARATOR = "#" + "_" * 66 + "\n"


def should_ignore_dir(dir_name: str, ignore_dirs: List[str]) -> bool:
    """Check if a directory should be ignored based on its name."""
    return dir_name in ignore_dirs


def collect_py_files(root_dir: Path, ignore_dirs: List[str]):
    py_files = {}
    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if not should_ignore_dir(d, ignore_dirs)]
        files = [f for f in filenames if f.endswith(".py")]
        if files:
            rel_path = Path(dirpath).relative_to(root_dir)
            py_files[rel_path] = [Path(dirpath) / f for f in files]
    return py_files


def extract_module_docstring(file_path: Path) -> str:
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        lines = content.splitlines()
        if lines and (lines[0].startswith('"""') or lines[0].startswith("'''")):
            doc = []
            delim = lines[0][:3]
            for line in lines:
                doc.append(line)
                if line.endswith(delim) and len(doc) > 1:
                    break
            return "\n".join(doc)
    except Exception:
        pass
    return "# No docstring found"


def combine_files(file_paths: List[Path]) -> (str, int):
    combined = []
    total_lines = 0
    for file_path in sorted(file_paths):
        combined.append(SEPARATOR)
        combined.append(f"# File: {file_path.name}\n")
        docstring = extract_module_docstring(file_path)
        combined.append(docstring + "\n\n")
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
            total_lines += len(lines)
            combined.extend(lines)
    return "".join(combined), total_lines


@app.command()
def combine_scripts(
    root: Path = typer.Argument(..., help="Root directory to search"),
    ignore_dirs: str = typer.Option("env", help="Comma-separated list of directory names to ignore"),
    output_dir: str = typer.Option("Combined_Scripts", help="Output directory for combined files"),
    log_csv: str = typer.Option("combined_log.csv", help="CSV file to store summary log")
):
    """
    Combine all Python files in subdirectories of ROOT into one script per subdirectory.
    Adds separator and docstring for each file. Logs stats in CSV.
    """
    ignore_list = [d.strip() for d in ignore_dirs.split(",") if d.strip()]
    typer.echo(f"🔍 Ignoring Python files in {ignore_list}...")

    root_path = root.resolve()
    output_path = root_path / output_dir
    output_path.mkdir(exist_ok=True)

    file_map = collect_py_files(root_path, ignore_list)
    log_rows = [("Combined_File", "Num_Source_Files", "Total_Lines")]

    for rel_dir, files in file_map.items():
        if not files:
            continue
        filename = f"{'.'.join(rel_dir.parts)}.combined.py"
        combined_code, line_count = combine_files(files)
        output_file = output_path / filename
        output_file.write_text(combined_code, encoding="utf-8")
        log_rows.append((filename, len(files), line_count))

    with open(output_path / log_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(log_rows)

    typer.echo(f"✅ Combined {len(file_map)} script groups. Output in: {output_path}")


if __name__ == "__main__":
    app()#__________________________________________________________________
# File: method_graph.py
# No docstring found

from pathlib import Path
from typing import List, Optional

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import typer

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
#__________________________________________________________________
# File: variable_graph.py
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

import matplotlib.pyplot as plt
import networkx as nx


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
