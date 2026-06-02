---
name: Python FastAPI on Replit
description: How to run Python FastAPI as a Replit artifact service; path gotcha with artifact run commands
---

The artifact `run` command in artifact.toml executes from the **artifact's own directory**, not workspace root.

**Rule:** Use `run = "python run.py"` — not `run = "python artifacts/api-server/run.py"` (which doubles the path).

**Why:** Replit sets CWD to the artifact directory before running the dev command. Using the full path from workspace root causes a doubled path like `/home/runner/workspace/artifacts/api-server/artifacts/api-server/run.py`.

**How to apply:** Any Python artifact: put entry point (`run.py`) in the artifact root, use `python run.py` in artifact.toml. Add `sys.path.insert(0, os.path.dirname(__file__))` in run.py so relative imports from backend package work.

**Package installation:** Use `installLanguagePackages({language: "python", packages: [...]})` — pip3 is not on PATH directly.
