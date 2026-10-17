# ADR Format

ADRs (decision records) live in `docs/decisions/` and use sequential numbering: `0001-short-title.md`, `0002-short-title.md`, etc.

The template is defined once, in [`docs/decisions/README.md`](../../../docs/decisions/README.md). Do not invent a second format; this file only adds guidance on numbering, length and when to write one.

## Template (mirrors docs/decisions/README.md)

```md
# NNNN: Title

- Date: YYYY-MM-DD
- Status: proposed | accepted | superseded

## Context
## Decision
## Consequences
```

Keep each section short. An ADR can be a few sentences per section. The value is in recording *that* a decision was made and *why*, not in filling out sections.

- **Context**: what forced the decision, including the alternatives that were genuinely considered when the rejection is non-obvious.
- **Decision**: what we chose, in one or two sentences.
- **Consequences**: what follows from it, including non-obvious downstream effects. One line is fine.

## Status

- `proposed`: written, not yet agreed by the team (e.g. open in a PR).
- `accepted`: agreed.
- `superseded`: replaced by a later ADR. Add a line under Status: `- Superseded by: [NNNN](NNNN-short-title.md)`, and link back from the new ADR's Context.

## Numbering and index

1. Scan `docs/decisions/` for the highest existing `NNNN-*.md` number (ignore `README.md`) and increment by one. The first ADR is `0001`.
2. Add a row for the new ADR to the index table in `docs/decisions/README.md`. An ADR that is not in the index is hard to find.

## When to offer an ADR

All three of these must be true:

1. **Hard to reverse**: the cost of changing your mind later is meaningful
2. **Surprising without context**: a future reader will look at the code and wonder "why on earth did they do it this way?"
3. **The result of a real trade-off**: there were genuine alternatives and you picked one for specific reasons

If a decision is easy to reverse, skip it: you'll just reverse it. If it's not surprising, nobody will wonder why. If there was no real alternative, there's nothing to record beyond "we did the obvious thing."

### What qualifies

- **Architectural shape.** "Agent logic runs in a single backend service." "Conversations are stored as an append-only log."
- **Integration patterns.** "The agent reaches suppliers through the owner's own chat account, not a separate business number."
- **Technology choices that carry lock-in.** Messaging channel, LLM provider, database, hosting, auth. Not every library: just the ones that would be painful to swap out.
- **Boundary and scope decisions.** "The assistant is owner-facing only; it never talks to end customers." The explicit no-s are as valuable as the yes-s.
- **Deliberate deviations from the obvious path.** Anything where a reasonable reader would assume the opposite. These stop the next teammate from "fixing" something that was deliberate.
- **Constraints not visible in the code.** "We can't demo on the WhatsApp Business API because of Meta's AI chatbot restrictions."
- **Rejected alternatives when the rejection is non-obvious.** If you considered one option and picked another for subtle reasons, record it; otherwise someone will suggest it again next week.
