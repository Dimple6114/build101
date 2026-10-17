# Backend

FastAPI service: WhatsApp webhook, conversation routing, orchestrator + specialist agents (Claude), background jobs, post rendering (Playwright) and publishing (Zernio).

- Architecture: [docs/architecture/overview.md](../docs/architecture/overview.md)
- Agents: [docs/architecture/agents.md](../docs/architecture/agents.md)
- API: [docs/architecture/api.md](../docs/architecture/api.md)
- Setup: [docs/implementation/setup.md](../docs/implementation/setup.md)

Stack: **Python + FastAPI**, uv project rooted here ([ADR 0001](../docs/decisions/0001-backend-python-fastapi.md)), with SQLAlchemy 2 (async) + asyncpg, Pydantic v2, `anthropic`, Playwright and Supabase ([ADR 0003](../docs/decisions/0003-database-supabase-sqlalchemy.md)).

Commands run from this folder (`uv run ruff check .`, `uv run pytest tests/ -v`); see [`.claude/rules/python.md`](../.claude/rules/python.md).
