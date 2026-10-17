---
name: configure-dependency
description: >-
  Fetch official docs and configure a new dependency correctly from the start,
  in backend/ or frontend/, and record significant choices as ADRs in
  docs/decisions/. Use when adding a package, framework, hosted service, LLM
  provider, messaging channel, or other external integration to build101.
  Trigger phrases: "add X", "integrate X", "configure X", "set up X", "should
  we use X".
allowed-tools: WebFetch WebSearch Read Edit Write Bash
---

> Adapted from [guidodinello/claude-dotfiles `configure-dependency`](https://github.com/guidodinello/claude-dotfiles/tree/main/.claude/skills/configure-dependency) (MIT, see [THIRD_PARTY_NOTICES](../THIRD_PARTY_NOTICES.md)).

# Configure Dependency Skill

Before writing any integration code, fetch the official documentation for the dependency so configuration is done correctly from the start. Misconfigurations are the hardest bugs to debug — this skill prevents them.

The build101 stack is still being decided. Never assume a language, framework, or package manager: read what the repo and `docs/decisions/` actually say.

## Instructions

The user provides a dependency name as an argument (e.g. `/configure-dependency <name>`). If no name is given, ask before continuing.

### Step 1 — Identify the dependency and where it lands

Determine:

- The canonical package or service name.
- **Which layer it lives in**: `backend/` (agent, integrations, APIs), `frontend/` (owner-facing UI / demo surface), infrastructure (hosting, database, queue), or an external service (LLM provider, messaging channel, third-party API).
- **The layer's current stack**: read `backend/README.md` or `frontend/README.md` and the index in `docs/decisions/README.md`. Then look for the layer's manifest (e.g. `package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, a compose file) and its lockfile.
  - If the layer still says **Stack: TBD** and has no manifest, this dependency is effectively a stack decision. Stop and treat Step 3's ADR as required, and agree the stack choice with the user before installing anything.
- The version currently pinned, if it is already declared. If not, note that it must be pinned in Step 4.

### Step 2 — Fetch the official documentation

Use WebFetch or WebSearch to retrieve the official setup/configuration guide for this dependency. Prefer:

1. The official docs site
2. The package registry page (npm, PyPI, crates.io, etc.) if no dedicated docs site exists
3. The GitHub README as a last resort

Focus on:

- **Installation** — any extras, peer dependencies, or optional components needed
- **Configuration options** — required vs. optional settings, their defaults, and gotchas
- **Framework integration** — if it integrates with a framework already recorded for that layer, find that specific guide
- **Version-specific notes** — breaking changes or migration notes for the version you would pin
- **Terms and limits** — pricing, rate limits, and usage policies for hosted services (e.g. messaging platform rules on AI assistants; see `docs/open-questions.md`)

Cite every finding with its URL and the date read, per the `docs-index` skill's citation rule.

### Step 3 — Summarize, and decide whether it needs an ADR

Before touching any file, present a short summary:

- What the dependency does and where it fits in build101
- Required configuration (env vars, init calls, connection params, accounts/keys)
- Any gotchas or common mistakes found in the docs
- Recommended version to pin
- Alternatives considered, if the choice is not obvious

Then apply the ADR test from [domain-modeling/ADR-FORMAT.md](../domain-modeling/ADR-FORMAT.md) (hard to reverse, surprising without context, real trade-off). It is almost always met for: the first framework/language of a layer, the messaging channel, the LLM provider, the database, hosting, and auth. It is usually not met for small utility libraries.

- **ADR needed**: draft `docs/decisions/NNNN-short-title.md` using the template in `docs/decisions/README.md` (Status `proposed` until the team agrees) and add it to that README's index table.
- **Research worth keeping** (comparisons, pricing, policy findings): save it under `docs/research/` per the `docs-index` skill and link it from the ADR's Context.

Ask the user to confirm the approach (and the ADR draft, if any) before proceeding to Step 4.

### Step 4 — Implement the configuration

Follow the conventions already established in that layer. If none exist yet, propose them and keep them minimal:

- Add the dependency with the layer's package manager so the manifest **and** lockfile are updated, and pin the version.
- Put configuration behind environment variables read in one place (a single config module per layer). Never commit secrets.
- Document every new env var with a placeholder value in the layer's `.env.example` (create it if missing) and mention it in the layer's `README.md`.
- If it's a local service (database, cache, queue), add it to the project's local dev setup (e.g. a compose file) if one exists, or document how to run it.

### Step 5 — Verify

Run the relevant checks to confirm the dependency is wired up correctly:

- Import / load it once from the layer's runtime to confirm the install.
- If it has a connection (DB, broker, API, channel), make one minimal real call or confirm an existing health check covers it.
- Run the layer's existing lint / typecheck / test commands, if any, to confirm nothing broke.

### Step 6 — Confirm and summarize

Report:

- What was installed, the pinned version, and where it's configured
- Env vars the team needs to set locally (and where they are documented)
- The ADR and research docs created or updated, if any
- Any follow-up steps (e.g. creating an account or API key, running a migration, setting a secret in the deployment environment)
