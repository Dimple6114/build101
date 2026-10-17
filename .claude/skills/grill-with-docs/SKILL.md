---
name: grill-with-docs
description: >-
  A relentless interview to sharpen a build101 plan, idea or design (jobs to
  be done, approval rules, demo channel, architecture), which also writes the
  docs as we go: terms into docs/glossary.md and decisions into
  docs/decisions/.
disable-model-invocation: true
---

> Adapted from [mattpocock/skills `grill-with-docs`](https://github.com/mattpocock/skills/tree/49dd158d1076134a641b33efb035946536778336/skills/engineering/grill-with-docs) and [`grilling`](https://github.com/mattpocock/skills/tree/49dd158d1076134a641b33efb035946536778336/skills/productivity/grilling) (MIT, see [THIRD_PARTY_NOTICES](../THIRD_PARTY_NOTICES.md)).

# Grill with docs

Two disciplines run together for the whole session:

1. **Grilling** (below): interview the user until the plan is fully understood.
2. **Domain modeling**: call the Skill tool for `domain-modeling` at the start of the session and follow it throughout. Resolved terms go into `docs/glossary.md` ([format](../domain-modeling/GLOSSARY-FORMAT.md)); decisions that pass the ADR test go into `docs/decisions/` ([format](../domain-modeling/ADR-FORMAT.md)).

Before the first round, read `docs/README.md`, `docs/glossary.md` and the index in `docs/decisions/README.md`, plus whichever of `docs/idea.md`, `docs/open-questions.md` or `docs/research/` the topic touches. Don't ask questions those docs already answer; challenge them instead when the user contradicts them.

## Grilling

Interview the user relentlessly until you reach a shared understanding. Map this as a **design tree**: every decision branches into the decisions that hang off it.

Work the tree in **rounds**. The **frontier** is every decision whose prerequisites are already settled: the questions you can ask _now_ without guessing at answers you haven't heard yet. Ask the whole frontier in one round: number each question and give your recommended answer. Then wait for the user's answers before the next round.

Format a round like so:

```
❓ **Q1** - **<question title>**: <question body, might be multiple paragraphs, including multiple choices>

➡️ <your recommended answer>

---

❓ **Q2** - **<question title>**: <question body, might be multiple paragraphs, including multiple choices>

➡️ <your recommended answer>
```

Word each question so "yes" accepts your recommended answer.

Each round the user answers reshapes the tree: settled decisions push the frontier outward and unblock questions that depended on them. Recompute the frontier and ask the next round. A question whose answer depends on another question still open in this round belongs to a _later_ round, not this one.

Finding _facts_ is your job, never the user's. When a frontier question needs a fact from the environment (the repo, `docs/`, the web, tools), dispatch a sub-agent to find it; don't ask the user for anything you could look up yourself. Don't block on it: a running exploration is an unsettled prerequisite, so only the questions downstream of it wait for the sub-agent to report; ask the rest of the frontier now. The _decisions_ are the user's: put each to them and wait.

The session is done when the frontier is empty: every branch of the design tree visited, nothing left silently assumed. Do not act on it until the user confirms you have reached a shared understanding.

## Writing the docs as you go

- Update `docs/glossary.md` the moment a term is resolved, not at the end.
- Offer an ADR only when the domain-modeling ADR test passes (hard to reverse, surprising without context, real trade-off). Register every new ADR in the index table of `docs/decisions/README.md`.
- When an answer settles an item in `docs/open-questions.md` or a "To refine" checkbox in `docs/idea.md`, tick it and link the ADR or glossary entry that settled it.
- Research findings gathered by sub-agents that are worth keeping go into `docs/research/`, following the `docs-index` skill.
