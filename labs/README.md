# Labs

Standalone Python environment for LLM / RAG lab runs. Kept separate from the
MkDocs docs env so lab dependencies and data never end up in the published site.

## Setup

```bash
cd labs
uv sync                 # creates labs/.venv from labs/uv.lock
uv run jupyter lab      # or point your notebook editor at the labs/.venv kernel
```

## Interpreter

`.python-version` pins CPython 3.12, and `tool.uv.python-preference = "only-managed"`
forces uv to use a uv-managed interpreter. On Apple Silicon this matters: an active
conda base env is x86_64 under Rosetta, and picking it breaks arm64-only wheels such
as `onnxruntime`. If `uv sync` ever reports the wrong interpreter, `conda deactivate`
and re-run.

## Layout

- `pyproject.toml` / `uv.lock` — pinned dependencies
- `.venv/` — this project's virtualenv (gitignored)
- `data/` — PDFs and extracted text (gitignored; copyrighted, never commit)

Notebooks that are published as write-ups live under `docs/labs/` and are
rendered by `mkdocs-jupyter`. Run them with this env's kernel; the code and data
stay here.
