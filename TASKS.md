# 🛠 Codebase Cleanup & Consistency Roadmap

This repo was largely AI-generated. The following tasks are structured so that AI tools (e.g., Codex) can execute them with minimal human clarification. Tasks are grouped by phase: **Hygiene → Structure → Confidence → Polish**.

---

## Phase 1: Hygiene (Consistency & Automation)

- **Task 1.1: Add Pre-commit Hooks**    
    - Create `.pre-commit-config.yaml`.        
    - Enable `black`, `ruff`, and `isort`.        
    - Command: `pre-commit install`        
- **Task 1.2: Apply Auto-Formatting to Entire Repo**    
    - Run `pre-commit run --all-files`.        
    - Commit results.        
- **Task 1.3: Centralize Logging**    
    - Create `src/core/logger.py` with `logging` config (INFO default, DEBUG option).        
    - Replace all `print()` with `logger.info()`, `logger.error()`, etc.        
- **Task 1.4: Centralize Configuration**    
    - Create `src/core/config.py` that loads `.env` via `dotenv`.        
    - Move all inline constants (AWS buckets, paths, prefixes) into `config.py`.        
    - Replace scattered constants with imports from config.        
- **Task 1.5: Centralize Constants**    
    - Create `src/core/constants.py`.        
    - Move static strings (error messages, prefixes, schema names). 

---

## Phase 2: Structure (Refactors & Modularization)

- **Task 2.1: Refactor Monolithic Pipeline**    
    - Break `scripts/pipeline.py` into helpers:        
        - `upload_file()`            
        - `classify_document()`            
        - `embed_document()`            
    - Keep wrapper function (`run_pipeline()`) to call helpers.        
- **Task 2.2: Refactor Classify Workflow**    
    - Break `classify()` into: `detect()`, `segment()`, `summarize()`, `merge_stubs()`, `persist()`.        
    - Keep wrapper function (`classify()`) that calls helpers.        
- **Task 2.3: Move AWS Lambda Wrapper to Clean Module**    
    - Refactor `lambda_summary.py`:        
        - Remove undefined constants.            
        - Accept config object instead of globals.            
        - Use `logger` instead of `print`.            
- **Task 2.4: Remove Duplicate or Experimental Scripts**    
    - Move `transformers_test.py`, `llama_test.py` → `examples/`. 
    - Delete `Combined_Scripts/` folder unless formalized.        

---

## Phase 3: Confidence (Tests & CI/CD)

- **Task 3.1: Add Test Harness**    
    - Create `tests/` folder with `pytest`.        
    - Add test for `pipeline.run_pipeline()` (happy path).        
    - Add test for `lambda_summary()` error case.        
- **Task 3.2: Mock External Services**    
    - Use `pytest-mock` or `moto` for AWS calls.        
    - Ensure tests do not hit live AWS.        
- **Task 3.3: Add GitHub Actions CI**    
    - Add `.github/workflows/ci.yaml`:        
        - `ruff check .`            
        - `pytest -q`            
        - `black --check .`            

---

## Phase 4: Polish (Open Source Ready)

- **Task 4.1: Update README.md**    
    - Add project description.        
    - Add install instructions.        
    - Add Quickstart example code.        
    - Add badges for CI, coverage (optional).        
- **Task 4.2: Add CONTRIBUTING.md**    
    - Document coding style (black, ruff).        
    - Document test workflow (`pytest`).        
    - Document branching/PR policy.        
- **Task 4.3: Add Purpose Docs**    
    - For each major module (`pipeline`, `lambda`, `cli`), create `purpose.md`.        
    - Explain the module’s role.        
- **Task 4.4: Add Type Hints & Docstrings**    
    - Add return type hints to public functions (`run_pipeline`, `classify_document`, etc.).        
    - Add docstrings explaining parameters and return values.        

---

## Execution Guidelines

- Each task should be completed and committed in a separate branch/PR.    
- Run pre-commit and tests before each commit.    
- Small, atomic changes are preferred (no mega-commits).    
- Human review required for architectural refactors (Phase 2).

# Fixes

src/core/utils/lambda_summary.py, src/core/clustering/cluster_helpers.py
- PARSED_PREFIX, LAMBDA_NAME, BUCKET_NAME, OPENAI_API_KEY, etc are undefined
- Implement new configuration code for these names

