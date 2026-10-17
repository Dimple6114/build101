---
name: domain-modeling
description: >-
  Build and sharpen build101's domain model (owner, business, channel, staff,
  approvals, and so on). Use when discussing product or codebase terminology,
  writing or editing docs/glossary.md, or recording or editing a decision
  (ADR) in docs/decisions/.
---

> Adapted from [mattpocock/skills `domain-modeling`](https://github.com/mattpocock/skills/tree/49dd158d1076134a641b33efb035946536778336/skills/engineering/domain-modeling) (MIT, see [THIRD_PARTY_NOTICES](../../THIRD_PARTY_NOTICES.md)).

# Domain Modeling

Actively build and sharpen the project's domain model as you design. This is the *active* discipline: challenging terms, inventing edge-case scenarios, and writing the glossary and decisions down the moment they crystallise. (Merely *reading* `docs/glossary.md` for vocabulary is not this skill: that's a one-line habit any skill can do. This skill is for when you're changing the model, not just consuming it.)

## File structure

build101 has a single context. The domain model lives in the shared `docs/` tree:

```
/
├── docs/
│   ├── glossary.md          ← the domain language
│   ├── decisions/           ← ADRs: NNNN-short-title.md
│   │   ├── README.md        ← ADR template + index of all ADRs
│   │   └── 0001-demo-channel.md
│   ├── idea.md
│   └── open-questions.md
├── backend/
└── frontend/
```

Create files lazily: only when you have something to write. If the first ADR is needed, add it to `docs/decisions/` and register it in the index table of `docs/decisions/README.md`.

## During the session

### Challenge against the glossary

When the user uses a term that conflicts with the existing language in `docs/glossary.md`, call it out immediately. "Your glossary defines 'Owner' as X, but you seem to mean Y. Which is it?"

### Sharpen fuzzy language

When the user uses vague or overloaded terms, propose a precise canonical term. "You're saying 'user': do you mean the Owner or a Staff member? Those are different things."

### Discuss concrete scenarios

When domain relationships are being discussed, stress-test them with specific scenarios. Invent scenarios that probe edge cases and force the user to be precise about the boundaries between concepts.

### Cross-reference with docs and code

When the user states how something works, check whether `docs/` (and the code in `backend/` / `frontend/`, once it exists) agrees. If you find a contradiction, surface it: "`docs/idea.md` says the assistant asks for approval before acting, but you just described it sending supplier orders on its own. Which is right?"

### Update docs/glossary.md inline

When a term is resolved, update `docs/glossary.md` right there. Don't batch these up: capture them as they happen. Use the format in [GLOSSARY-FORMAT.md](./GLOSSARY-FORMAT.md).

`docs/glossary.md` should be totally devoid of implementation details. Do not treat it as a spec, a scratch pad, or a repository for implementation decisions. It is a glossary and nothing else.

### Offer ADRs sparingly

Only offer to create an ADR when all three are true:

1. **Hard to reverse**: the cost of changing your mind later is meaningful
2. **Surprising without context**: a future reader will wonder "why did they do it this way?"
3. **The result of a real trade-off**: there were genuine alternatives and you picked one for specific reasons

If any of the three is missing, skip the ADR. Use the format in [ADR-FORMAT.md](./ADR-FORMAT.md).
