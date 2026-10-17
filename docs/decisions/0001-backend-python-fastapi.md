# 0001: Backend in Python + FastAPI

- Date: 2026-10-17
- Status: accepted

## Context

build101 needs a backend for the agent logic, the messaging channel and LLM integrations, and the APIs behind the demo. The team is most familiar with Python, and Python has a broad AI/LLM ecosystem (provider SDKs and agent tooling) that the agent work will lean on.

## Decision

The backend is written in Python with FastAPI, as a uv project rooted at `backend/`.

## Consequences

- Toolchain follows [`.claude/rules/python.md`](../../.claude/rules/python.md): uv for packaging and environments, ruff for linting and formatting, pytest for tests; commands run from `backend/`.
- Database and ORM are still open; record them in a separate ADR.
- FastAPI-specific conventions (project layout, dependency injection, settings, error handling) are not yet defined; record them when decided.
- The frontend stack is unaffected and still open.
