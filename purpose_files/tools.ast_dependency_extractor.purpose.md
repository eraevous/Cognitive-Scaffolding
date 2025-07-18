# Module: tools.ast_dependency_extractor
# @ai-path: tools.ast_dependency_extractor
# @ai-source-file: ast_dependency_extractor.py
# @ai-role: cli_tool
# @ai-intent: "Trace function and method calls across a package using AST parsing."
# @ai-version: 0.1.1
# @ai-generated: true
# @ai-verified: false
# @human-reviewed: false
# @schema-version: 0.2

### 🎯 Intent & Responsibility
- Parse Python files to map which functions invoke which others.
- Provide a Typer CLI (`analyze`) to export edges or an adjacency matrix.

### 📥 Inputs & 📤 Outputs
| Direction | Name        | Type | Brief Description |
|-----------|------------|------|------------------|
| 📥 In     | source_dir  | str  | Root folder for `.py` files |
| 📥 In     | recursive   | bool | Traverse subdirectories |
| 📥 In     | ignore_dirs | str  | Comma-separated directories to skip |
| 📥 In     | output      | Path | Optional CSV export path |
| 📥 In     | matrix      | bool | Output adjacency matrix if true |
| 📥 In     | config      | Path | `.graphconfig.json` override |
| 📤 Out    | csv         | File | CSV of `Source,Call` pairs or adjacency matrix |

### 🔗 Dependencies
- `ast`, `os`, `tokenize`, `pandas`, `networkx`, `typer`

### 🗣 Dialogic Notes
- Edges can feed into `method_graph` for visualization.
- Useful for QAT modules analyzing package structure.
- Robust to exotic encodings and deep regex patterns via `tokenize.open` and iterative AST walk.
