# Backend

Agent logic, integrations (messaging channel, LLM, storage) and APIs.

Stack: **Python + FastAPI**, uv project rooted here ([ADR 0001](../docs/decisions/0001-backend-python-fastapi.md)). Database / ORM: **TBD** — record the choice in [`docs/decisions/`](../docs/decisions/README.md).

Commands run from this folder (`uv run ruff check .`, `uv run pytest tests/ -v`); see [`.claude/rules/python.md`](../.claude/rules/python.md).
