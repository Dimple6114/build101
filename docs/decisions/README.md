# Decisions

One short file per decision: `NNNN-short-title.md` (e.g. `0001-demo-channel.md`). Number sequentially from the highest existing file; the first is `0001`. Guidance on when a decision deserves a record: [ADR-FORMAT.md](../../.claude/skills/domain-modeling/ADR-FORMAT.md).

```md
# NNNN: Title

- Date: YYYY-MM-DD
- Status: proposed | accepted | superseded

## Context
## Decision
## Consequences
```

When an ADR is superseded, set its Status to `superseded`, add `- Superseded by: [NNNN](NNNN-short-title.md)` under it, and link back from the new ADR's Context.

## Index

| ADR | Title | Status | Date |
|---|---|---|---|
