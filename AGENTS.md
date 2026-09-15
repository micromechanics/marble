# AGENTS.md

## Project Basics

- Package: `pymarble`; Python 3.10+ (CI uses 3.10).
- Entry points: `marbleCLI` → `pymarble.cli:main`; `marbleGUI` → `pymarble.gui.gui:main`.
- Tests live in `tests/`; documentation in `docs/`.
- Use `.venv/bin/python -m ...` and `.venv/bin/pylint` for local runs.

## Commands

```bash
.venv/bin/pylint $(git ls-files 'pymarble/*')
.venv/bin/pylint pymarble
.venv/bin/python -m mypy pymarble
.venv/bin/python -m pytest tests
.venv/bin/python -m coverage run --source pymarble -m pytest tests
.venv/bin/make -C docs html
.venv/bin/python -m pip wheel -w dist/ --no-deps .
```

Use `.venv/bin/python -m pytest tests/test_section.py`, `...::testSection`, or `-k testSection` for focused runs. `tests/` includes Python and bash tests; when the user asks for all tests, include both. `bash tests/testBackend.sh` uses `punx`, writes under `tests/examples/`, and is very slow; run it only on explicit request. Run pylint and mypy only on explicit user request.

## Project-Specific Style

- Indentation is two spaces; maximum line length is 200.
- Existing code may use compact imports and relative internal imports; preserve those conventions.
- MyPy settings in `setup.cfg` are strict for function typing; prefer built-in generics.
- For new logic, prefer specific exceptions; broad catches at CLI/GUI boundaries need clear user/log context. Do not silently swallow exceptions unless intentionally best-effort.
- Use `logging` for library/GUI diagnostics and `print` for CLI interaction.
- When a prerequisite is missing, report the necessary step and block startup with one guard; do not presume state.
- Temporary/generated files in `tests/examples/` may be cleaned up as needed.
- Do not suggest regression tests. Never execute Git commands; the user handles them.
