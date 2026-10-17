# 0010: Anthropic SDK with our own orchestration

- Date: 2026-10-17
- Status: proposed

## Context

Options were LangGraph, Pydantic AI, or the official Anthropic SDK with our own orchestration.

## Decision

Official `anthropic` Python SDK. The orchestrator is a small manual tool-use loop (async, DB-persisted, with guards in tool code). Specialists are single structured-output calls. Model `claude-opus-5-5` everywhere, with per-agent **effort** tuning; server-side refusal fallbacks and prompt caching on.

## Consequences

- Few dependencies, full control, easy to debug through the `agent_runs` log.
- We own conversation persistence and retries (small amount of code).
- If flows get much more complex (long multi-step graphs with human-in-the-loop checkpoints), revisit LangGraph.
