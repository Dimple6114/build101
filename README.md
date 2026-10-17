# build101

An owner-facing AI operations assistant for small businesses, living in the chat app the owner already uses.

> Status: **idea refinement**. Only the backend stack is decided so far ([decisions](docs/decisions/README.md)) — start in [`docs/`](docs/).

## Repository layout

| Path | What lives there |
|---|---|
| [`docs/`](docs/) | The business side: problem, users, competitors, open questions, decisions |
| [`backend/`](backend/) | Agent, integrations and APIs (Python + FastAPI, [ADR 0001](docs/decisions/0001-backend-python-fastapi.md); database TBD) |
| [`frontend/`](frontend/) | Owner-facing UI / demo surface (stack TBD) |
| [`.github/`](.github/) | Issue and PR templates, CI later |
| [`.claude/skills/`](.claude/skills/) | Shared agent skills: grilling, domain modeling, issues, PR review, dependencies, docs conventions |
| [`.claude/rules/`](.claude/rules/) | Path-scoped agent rules (Python, database, Docker, CI) that load when matching files are touched |
| [`AGENTS.md`](AGENTS.md) | How we work: the shared workflow and conventions, for humans and any AI tool |

## How we work

Read [`AGENTS.md`](AGENTS.md): one workflow (capture, research, decide, plan, build, review, close the loop) that keeps what we learn in [`docs/`](docs/README.md). It applies whether you use Claude Code, another AI tool, or none.
