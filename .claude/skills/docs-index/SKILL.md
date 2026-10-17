---
name: docs-index
description: >-
  Conventions for organizing and navigating build101's shared docs/ tree, the
  team's committed knowledge base (idea, competitors, open questions,
  research, decisions, glossary). Use when adding a new doc or subfolder under
  docs/, deciding where an investigation, spike, competitor/market/tech
  research or decision should live, writing or updating a README.md index
  there, or looking for prior context on a topic. Core rule: every folder and
  subfolder under docs/ has a README.md index, so the tree stays discoverable
  without preloading it into context.
---

> Adapted from [guidodinello/claude-dotfiles `dev-docs-index`](https://github.com/guidodinello/claude-dotfiles/tree/main/.claude/skills/dev-docs-index) (MIT, see [THIRD_PARTY_NOTICES](../../THIRD_PARTY_NOTICES.md)).

# docs/ conventions

## Why this exists

`docs/` is the team's shared knowledge base: the business side of build101 (problem, users, competitors, open questions), the research behind it, and the decisions we made. Everything in it is committed and visible to the whole team; there is no private or ignored layer. It is **not code** — nothing here is loaded automatically, and nothing here should be.

The failure mode this skill prevents is a doc that exists but is *unreachable*: written once, never linked from anywhere, and effectively lost the next time someone (a teammate or an agent) needs the context it holds.

The fix is a plain tree convention: **every folder and every subfolder under `docs/` has a `README.md`** that says, in a few lines, what the folder is for and what's in it, and links to each subfolder's own `README.md`. Discovery becomes a walk down READMEs, one level at a time, reading only the branches relevant to the current task.

## Where things go

| What | Where |
|---|---|
| Problem, target user, value proposition | `docs/idea.md` |
| Competitive landscape **summary** (one table, the gap) | `docs/competitors.md` |
| Risks and unknowns still to resolve | `docs/open-questions.md` |
| Domain language (Owner, Business, Channel, ...) | `docs/glossary.md` — format in [GLOSSARY-FORMAT.md](../domain-modeling/GLOSSARY-FORMAT.md) |
| Decisions we made and why (ADRs) | `docs/decisions/NNNN-short-title.md` — format in `docs/decisions/README.md` |
| Investigations, spikes, competitor deep dives, market research, user interviews, tech/vendor evaluations, policy reading (e.g. messaging platform terms) | `docs/research/` |

Rules of thumb:

- **Summary vs. evidence.** The top-level files stay short and current. The evidence behind them lives in `docs/research/` and is linked from the summary. Example: a deep dive on one competitor goes in `docs/research/`, and `docs/competitors.md` gets a one-line row linking to it.
- **Research ends in a decision or a question.** When research settles something, write the ADR in `docs/decisions/` and link the research from its Context. When it raises something, add it to `docs/open-questions.md`.
- **One topic, one place.** Before creating a doc, check the indexes for an existing one and extend it instead.
- **Research file names**: `short-topic.md` for a single doc (e.g. `whatsapp-ai-policy.md`); a `short-topic/` folder with its own `README.md` once a topic grows past one doc.

## The rule

1. **Every folder under `docs/` needs a `README.md`**, recursively, for as many levels as the tree goes.
2. **A folder's `README.md` briefly states its purpose and contents**, then — if it has subfolders — links to each subfolder's own `README.md` rather than re-describing what's inside them. Don't duplicate a child's content in the parent; point to it.
3. **A leaf folder's `README.md` lists its files** with a one-line description of each, so a reader can pick the right file without opening several.
4. **`docs/README.md` is the entry point.** It lists every direct child of `docs/` (files and folders). The root `README.md` links to `docs/`; keep it in sync if a new top-level area appears.
5. **Skip README.md only for** self-contained data files sitting inside an already-indexed folder (e.g. a CSV or JSON next to the doc that uses it). The doc that uses them links to them.

## What goes in a README.md here

Keep it short — a few sentences to a dozen lines for most folders. Don't write a report in the README; write a *map* to the reports.

**Leaf folder** (files, no subfolders):

```markdown
# <Folder purpose, one line>

<One paragraph: what question this folder answers or what work it covers, and current
status/date if the content has a shelf life.>

| File | What it covers | Date |
|---|---|---|
| [foo.md](foo.md) | One line | YYYY-MM-DD |
| [bar.md](bar.md) | One line | YYYY-MM-DD |
```

**Parent folder with subfolders**:

```markdown
# <Folder purpose>

Index of <what>.

- **[subfolder-a/](subfolder-a/README.md)** — <one line, what it's for>.
- **[subfolder-b/](subfolder-b/README.md)** — <one line>.
```

If a folder mixes loose files and subfolders, give the loose files a table and the subfolders their own bullet/link — don't force one format over the other. Once a multi-doc topic grows past 2–3 docs, make its README a routing table ("if you want X, start at Y") plus a status table you keep current, rather than a chronological append-only log.

## Cite the source for every finding

A finding without a source is a claim someone has to re-derive from scratch the next time it matters. Every fact, discovery, or claim written into a doc under `docs/` carries its source right where it's stated:

- **External source** (vendor docs, a pricing page, a competitor's site, an article, a GitHub repo): a markdown link to the exact URL, plus the date it was read if the content changes (pricing, terms, product pages).
- **Internal source** (another doc in this repo, an issue or PR, code): a repo-relative path or the issue/PR number.
- **Direct observation with no URL** (a demo you tried, a conversation with a potential user, a command you ran): say so explicitly — *"direct observation, tried the onboarding flow on 2026-10-17"* — rather than leaving the claim unsourced. Do not put personal data about interviewees in `docs/`; describe them generically (e.g. "owner of a small furniture business").

Put the citation inline, next to the claim, not only in an end-of-document source list. A **Sources** table at the end of a long doc is a good index, but it supplements the inline citations, it doesn't replace them.

When a doc revises or corrects an earlier claim, cite the new source the same way and say what it superseded (e.g. "Corrected 2026-10-20, per the vendor's updated terms: ...").

## Navigating — read only what the task needs

When looking for prior context on a topic:

1. Start at `docs/README.md`.
2. Open the relevant folder's `README.md`. If it points to subfolders and one clearly matches the task, descend into *that one* — don't open every sibling "just in case."
3. Stop descending once a README's file table names the specific doc you need, and read only that doc.

Don't defeat the tree by grepping across all of `docs/` before checking whether a README already points straight there. Grep is the fallback for when the tree doesn't have an obvious entry point, not the first move.

## When adding a doc or subfolder

1. Write the content first.
2. Add the file to its folder's `README.md` table (or, for a new folder, create its `README.md` — even a 3-line one is better than none, and every nested subfolder needs one too).
3. Link the new folder's `README.md` from its **parent's** `README.md`.
4. If it is a new direct child of `docs/`, add it to `docs/README.md`.
5. If it settles or raises something, update `docs/decisions/` or `docs/open-questions.md` as described above.

## Checking for gaps

There's no permanent gap list — it goes stale the moment someone adds a folder. Check on demand from the repo root:

```bash
find docs -type d | while read -r d; do
  [ -f "$d/README.md" ] || echo "$d: NO README"
done
```

If you're already working inside a folder that's missing its README, add it while you're there.
