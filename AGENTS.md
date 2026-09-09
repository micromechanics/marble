# AGENTS.md
Guidance for autonomous coding agents in this repository.

## Project Basics
- Package: `pymarble`
- Language: Python (>=3.10; CI runs Python 3.10)
- Entry points:
  - CLI: `marbleCLI` -> `pymarble.cli:main`
  - GUI: `marbleGUI` -> `pymarble.gui.gui:main`
- Tests live in `tests/`
- Documentation lives in `docs/`
- Use the repository `.venv/` for all local runs, tests, linting, and mypy. Prefer `.venv/bin/python -m ...` and `.venv/bin/pylint` over system tools.

## Build, Lint, and Test Commands
### Lint
Primary (CI-like):
```bash
.venv/bin/pylint $(git ls-files 'pymarble/*')
```
Quick local:
```bash
.venv/bin/pylint pymarble
```
### Type Checking
```bash
.venv/bin/python -m mypy pymarble
```
### Tests
- `tests/` contains both Python tests and bash-based tests; if the user explicitly asks to check all tests, include both categories.
Full suite:
```bash
.venv/bin/python -m pytest tests
```
Coverage run (matches CI):
```bash
.venv/bin/python -m coverage run --source pymarble -m pytest tests
```
Coverage reports:
```bash
.venv/bin/python -m coverage report -m
.venv/bin/python -m coverage html
```
### Running a Single Test (important)
Single file:
```bash
.venv/bin/python -m pytest tests/test_section.py
```
Single test function:
```bash
.venv/bin/python -m pytest tests/test_section.py::testSection
```
Name filter:
```bash
.venv/bin/python -m pytest tests -k testSection
```
### Legacy End-to-End Script
```bash
bash tests/testBackend.sh
```
- Writes generated artifacts under `tests/examples/`; uses external tool `punx`.
- Rerun the full `bash tests/testBackend.sh` suite only when the user explicitly requests it; it is very time-consuming.
- Run pylint and mypy only when the user explicitly requests them.
### Docs Build
```bash
.venv/bin/make -C docs html
```
### Packaging Build
```bash
.venv/bin/python -m pip wheel -w dist/ --no-deps .
```
## Code Style Conventions
Follow existing local style in touched files first, then static checks. Do minimal code changes!
### Formatting
- Indentation: 2 spaces (`.pylintrc` sets `indent-string='  '`)
- Maximum line length: 200
- Avoid broad reformatting of unrelated lines
### Imports
- Existing code often uses compact imports (`import os, io`); stay consistent inside touched files
- Internal modules generally use relative imports (`from .file import BinaryFile`)
### Typing
- Add type annotations for new/changed functions where practical
- MyPy settings in `setup.cfg` are strict for function typing:
- Prefer built-in generics (`list[str]`, `dict[str, Any]`)
### Naming
- Functions, methods, variables, modules: `camelCase`
- Classes: `PascalCase`
- Keep existing public API names unless task explicitly requests renaming
### Error Handling
- Prefer specific exceptions in new logic
- Broad `except Exception` exists at some CLI/GUI boundaries; if used, provide clear user/log context
- Avoid silent swallowing of exceptions unless behavior is intentionally best-effort
- When a missing prerequisite would crash a tool, inform the user about the necessary step and prevent the tool from starting with a single guard `if` statement. Do not presume values or state to continue.
### Logging and User Output
- Use `logging` for library and GUI diagnostics
- CLI uses `print` for interactive user output; follow existing patterns there
### Defaults and Side Effects
- Avoid introducing mutable default arguments
- Legacy code has mutable defaults in some places; adjust carefully to avoid breaking behavior
- Tests and scripts can create temporary/generated files in `tests/examples/`; clean up where needed
## Recommended Agent Workflow
1. Inspect nearby code and keep local conventions.
2. Make minimal, task-scoped edits.
3. Run narrow tests first (single-test commands above).
4. Run broader lint/type/test checks when scope grows.
5. Report what changed, how it was validated, and any remaining risks.
- Do not suggest regression tests, never.
- Never execute git commands; the user handles git operations.
