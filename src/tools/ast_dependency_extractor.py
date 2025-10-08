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
 - ignore_dirs (str): Comma-separated relative paths to exclude under ``source_dir``.
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
import tokenize
from pathlib import Path
from typing import Dict, List, Tuple

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
        try:
            with tokenize.open(filepath) as f:
                source = f.read()
        except (SyntaxError, UnicodeDecodeError, LookupError) as exc:
            typer.echo(f"⚠️  Skipping {filepath} due to decode error: {exc}")
            return
        try:
            tree = ast.parse(source, filename=filepath)
            self._walk_tree(tree)
        except SyntaxError:
            typer.echo(f"⚠️  Skipping {filepath} due to syntax error.")

    def _walk_tree(self, tree: ast.AST):
        """Iteratively process AST nodes to avoid deep recursion."""
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self.imports[alias.asname or alias.name] = alias.name
            elif isinstance(node, ast.ImportFrom):
                module = node.module
                for alias in node.names:
                    name = alias.name
                    full_name = f"{module}.{name}" if module else name
                    self.imports[alias.asname or name] = full_name

        for func in [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]:
            func_name = f"{self.current_module}.{func.name}"
            self.defined_functions[func_name] = (self.current_module, func.lineno)
            for node in ast.walk(func):
                if isinstance(node, ast.Call):
                    callee_name = self._resolve_name(node.func)
                    if callee_name:
                        self.edges.append((func_name, callee_name))

    def _get_name(self, node):
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            value = self._get_name(node.value)
            return f"{value}.{node.attr}" if value else node.attr
        elif isinstance(node, ast.Call):
            return self._get_name(node.func)
        return None

    def _resolve_name(self, node):
        name = self._get_name(node)
        if name is None:
            return None
        root = name.split(".")[0]
        if root in self.imports:
            resolved = self.imports[root]
            return name.replace(root, resolved, 1)
        return f"{self.current_module}.{name}"

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


def should_ignore_dir(rel_dir: Path, ignore_dirs: List[str]) -> bool:
    """Return True if ``rel_dir`` should be skipped based on ignore patterns."""
    return any(rel_dir.as_posix().startswith(entry) for entry in ignore_dirs)


def collect_py_files(root_dir: Path, ignore_dirs: List[str]):
    py_files = {}
    for dirpath, dirnames, filenames in os.walk(root_dir):
        rel_dir = Path(dirpath).relative_to(root_dir)
        dirnames[:] = [
            d for d in dirnames if not should_ignore_dir(rel_dir / d, ignore_dirs)
        ]
        files = [f for f in filenames if f.endswith(".py")]
        if files:
            py_files[rel_dir] = [Path(dirpath) / f for f in files]
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
    ignore_dirs: str = typer.Option(
        "venv,.git,.pytest_cache,Scratch,tests,env,Combined_Scripts,kairos.egg-info, Codex_++, __pycache__, tests,vector,demo_script,.venv",
        help="Comma-separated relative paths to ignore under source_dir.",
    ),
    output: Path = typer.Option(None, help="Optional CSV output file."),
    matrix: bool = typer.Option(
        False, help="Output as adjacency matrix instead of edge list."
    ),
    config: Path = typer.Option(
        Path(".graphconfig.json"), help="Optional path to graph config JSON file."
    ),
):
    """Extract function call dependencies from Python code."""
    config_data = load_graph_config(config)
    source_path = Path(config_data.get("source_dir", source_dir))
    ignore_dirs_list = config_data.get("ignore_dirs", ignore_dirs).split(",")

    extractor = ASTDependencyExtractor()
    files = collect_py_files(source_path, ignore_dirs_list)
    for rel_path, py_paths in files.items():
        for file_path in py_paths:
            mod_name = (
                str(rel_path / file_path.name).replace("/", ".").replace(".py", "")
            )
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
