---
name: ticket-refinement
description: >
  Use this skill whenever the user wants to write, refine, or break down a
  work item for build101 into a GitHub issue in guidodinello/build101 —
  backend endpoints, agent behaviours, channel integrations, frontend/demo
  components, or research spikes. Trigger when the user shares a user story,
  acceptance criteria, an idea from docs/, or an existing issue and asks for a
  subtask, refinement, or implementation breakdown. Also trigger on phrases
  like "help me refine this", "write an issue for X", "break this down", or
  "create a card for the endpoint / component / feature". Produces a
  structured, audience-appropriate issue body and, after confirmation, creates
  or updates the issue with the gh CLI.
---

> Adapted from [guidodinello/claude-dotfiles `ticket-refinement`](https://github.com/guidodinello/claude-dotfiles/tree/main/.claude/skills/ticket-refinement) (MIT, see [THIRD_PARTY_NOTICES](../THIRD_PARTY_NOTICES.md)).

# Ticket Refinement Skill

Produces a structured GitHub issue from a user story, idea, or existing issue,
for the `guidodinello/build101` repository. Audience is mixed: developers,
product-minded teammates, and whoever tests the demo, so keep language clear
and avoid deep implementation jargon unless asked.

---

## Gather context first

- If the user references an existing issue, read it:
  `gh issue view <N> --repo guidodinello/build101 --comments`.
- Skim `docs/README.md` and follow it to whatever the work touches
  (`docs/idea.md`, `docs/open-questions.md`, `docs/decisions/`,
  `docs/glossary.md`). Use the glossary's terms in the issue; don't invent
  synonyms.
- If the work depends on a decision that is not recorded in
  `docs/decisions/`, list it under Open Questions rather than assuming it.

## Clarifying Questions (ask before writing)

If the following are not already clear from the conversation, ask them before
producing the issue. Group them into one message — don't ask one at a time.

1. **What kind of work is this?** (e.g. backend endpoint, agent behaviour,
   channel integration, frontend/demo component, research spike, docs)
2. **What data sources or services are involved?** (e.g. messaging channel,
   LLM provider, storage, third-party API)
3. **What already exists** that this work can build on or integrate with?
4. **What is the relationship model** if any (e.g. how Owner, Staff member,
   Supplier and tasks relate to each other)?

Skip questions that are already answered in the user story, the docs, or the
acceptance criteria.

---

## Output Template

Use this structure for every issue body. Omit a section only if it genuinely
does not apply (e.g. no edge cases for a trivial UI tweak).

Use `##` headings for each section (e.g. `## Context`, `## What Needs to Be Built`).

Always show the draft wrapped in a markdown code block (` ```markdown ... ``` `)
so the user can review the raw markdown, together with a proposed issue title.

Use backticks for:

- File paths and directory names (e.g. `backend/README.md`)
- Route paths (e.g. `/webhooks/message`)
- Field names, parameter names, and HTTP methods (e.g. `POST`, `owner_id`)
- Component or function names when referenced inline

Do NOT use backticks for plain English descriptions, section prose, or AC items.

---

## Context

1–3 sentences explaining _why_ this work exists, what problem it solves, and
where it fits in the bigger feature or demo. Link the relevant docs or ADRs
(repo-relative paths). Written so a non-technical teammate can understand it.

---

## What Needs to Be Built

A clear list of the concrete deliverables. For each item:

- State _what_ it is (route, component, agent capability, etc.)
- State _what it does_ in plain language
- Focus on **what** is being built and **why**, not **how** it is implemented

Keep this section high-level — it should read like a feature spec, not a code
review. Do NOT include:

- Prop names, function signatures, or component internals
- CSS classes, styling tokens, or layout implementation details
- State management wiring, hook usage, or data-fetching patterns
- Any detail that describes the developer's chosen implementation approach

A good test: would this bullet still be valid if a developer chose a completely
different implementation strategy? If yes, keep it. If no, cut it.

---

## Acceptance Criteria

A GitHub task list (`- [ ] ...`) of testable outcomes, written so someone can
verify the demo against them directly. Each item should be a complete,
verifiable statement.

Include both the happy path and edge cases inline. Pull edge cases from:

- Nullable or optional fields
- Empty / zero-result states
- Invalid or mismatched input
- Auth / permission boundaries (e.g. what needs Owner approval vs. what runs
  on its own)
- Re-submission or idempotency behaviour
- Any item marked "(Pending)" or flagged as TBD

---

## Open Questions

List anything that needs a decision before implementation can begin. Frame each
as a question, not a task. Include who is best placed to answer, and link the
matching item in `docs/open-questions.md` if one exists.

Omit this section if there are no blockers.

---

## Creating or updating the issue

Only after the user approves the draft:

1. Check which labels exist: `gh label list --repo guidodinello/build101`.
   Suggest labels only from that list; never create labels implicitly.
2. Create a new issue:

   ```bash
   gh issue create --repo guidodinello/build101 \
     --title "<title>" --label "<label>" --body-file - <<'EOF'
   <approved body>
   EOF
   ```

   Or update an existing one:
   `gh issue edit <N> --repo guidodinello/build101 --body-file -` (same heredoc).
3. For a breakdown into several issues, create them one by one and then add a
   task list linking each child (`- [ ] #<N>`) to the parent issue body.
4. Report the issue URL(s) returned by `gh`.

---

## Tone & Style Rules

- Write for a mixed audience: a non-developer should understand every section.
- Avoid framework names, ORM methods, or architectural patterns unless the user
  explicitly asked for that level of detail. The stack is still being decided;
  don't assume one that is not recorded in `docs/decisions/`.
- When ordering or priority is part of the feature, call the ordering out
  explicitly.
- If a behaviour is marked as out of scope or pending in the original request,
  note it clearly rather than silently omitting it.

---

## Quality Checklist (self-review before responding)

- [ ] Every requirement from the original request is reflected somewhere in the output
- [ ] Acceptance Criteria covers both the happy path and all relevant edge cases
- [ ] Terms match `docs/glossary.md`
- [ ] No section is padded — if a section has nothing to say, omit it
- [ ] Open Questions are genuine blockers, not implementation details
- [ ] Nothing was created on GitHub before the user approved the draft
