# Implementation plan (24h hackathon, 2 builders)

## Strategy

1. **Deploy on hour 1, not hour 20.** A "hello world" backend on Tenki and frontend on Vercel, with the WhatsApp webhook verified, before writing features. Deploy issues are the #1 hackathon killer.
2. **Contracts first.** In hour 1 we commit the shared contracts (Pydantic schemas, `ChannelPort`, `PublisherPort`, button IDs, REST types). After that, the two tracks build in parallel against them.
3. **Simulator before WhatsApp.** The web chat simulator lets Track A test agents and flows without depending on Meta. WhatsApp is just another `ChannelPort`.
4. **Vertical slices at checkpoints.** Three integration checkpoints where *something* works end to end, even if ugly.
5. **Freeze at H21.** The last 3 hours are rehearsal, fallbacks and the pitch. No new features.
6. **Coding agents do the typing.** Each task in [tasks.md](tasks.md) is written to be handed to Claude Code as-is: it names the files, the contract and the acceptance criteria.

## Tracks

| Track | Owner | Scope |
|---|---|---|
| **A: Brain** | Builder 1 (stronger in Python/LLMs) | DB layer, LLM client, all agents, job runner + job pipelines, orchestrator, renderer engine, quality checks, seed data |
| **B: Surface** | Builder 2 (stronger in web/integrations) | FastAPI skeleton, WhatsApp channel + webhook, simulator channel + `/dev/chat`, inbound handler + onboarding/button routers, onboarding REST + storage, Zernio publisher, Next.js wizard + dashboard, HTML post templates |

Shared files (coordinate before editing): `migrations/`, `app/agents/schemas.py`, `app/channels/base.py`, `app/publishing/base.py`, `app/copy/messages_es.py`, `frontend/lib/api.ts`.

## Timeline

| Hour | Track A: Brain | Track B: Surface | Together |
|---|---|---|---|
| **0–1** | — | — | Kickoff: scaffold `backend/` (uv + FastAPI) and `frontend/` (Next.js + shadcn). Apply schema. Commit contracts. Deploy both. Verify the Meta webhook against the deployed URL. **(T00–T03)** |
| **1–6** | LLM client + `agent_runs` (T10). Asset Analyst + Brand Strategist (T11–T12). Copywriter + Art Director (T13–T14). Renderer engine with a placeholder template (T15) | WhatsApp channel + webhook + dedupe (T20). Simulator channel + `/dev/chat` UI (T21–T22). Inbound handler + onboarding router Flow 1 (T23) | |
| **6–7** | | | **Checkpoint 1:** "hola" on real WhatsApp → welcome → name → magic link. A script renders a post for the demo business from its real photos |
| **7–12** | Job runner (T16). Jobs: brand, plan, post, revise (T17). Button router handlers (T18). Orchestrator v1 + tools (T19) | Onboarding REST + uploads to storage + palette (T24). Next.js wizard steps 1–7 (T25). Templates `product_hero` + `promo_band` (T26). Zernio publisher + connect flow (T27) | |
| **12–13** | | | **Checkpoint 2:** in the simulator: onboarding → Brand Brain summary → plan → post preview → change request → revised post |
| **13–17** | Publish job + guards (T30). Quality checks + retries (T31). Prompt tuning with real data (T32). Demo seed (T33) | WhatsApp interactive with image header + media inbound (T28). Zernio callback/webhook (T29). Templates `quote_card` + `split_story` (T34, Should). Dashboard (T35, Should) | |
| **17–18** | | | **Checkpoint 3:** full flow on real WhatsApp, with a real Instagram publish on the demo account |
| **18–21** | Latency pass (parallelize where safe, effort tuning). Orchestrator edge cases (Flow 10) | Mobile QA of the wizard (iOS in-app browser). Error states. Fallback switches tested | Bug bash. Each person runs the demo script once |
| **21** | | | **Code freeze.** Tag `demo-v1`. |
| **21–23** | | | Rehearse the demo ×2 (one with a forced fallback). Record a backup video of the full flow |
| **23–24** | | | Pitch slides, buffer |

Rest: if the hackathon allows it, take staggered 90-minute breaks between H13 and H17 (one person always awake on the integration).

## Before the hackathon (checklist)

Check the hackathon rules first: if pre-written code is not allowed, do only accounts and materials, not scaffolding.

**Accounts and keys** (owner: both, **by the day before**):

- [ ] Anthropic API key with credits; check rate limits for `claude-opus-5-5`.
- [ ] Meta developer app + WhatsApp product + test number; 3 recipient numbers verified; **System User permanent token** (not the 24h one). See [../architecture/integrations.md](../architecture/integrations.md#whatsapp-cloud-api).
- [ ] Zernio account + API key; demo IG account switched to **Business or Creator**; one manual test post via their dashboard.
- [ ] Supabase project; `assets` (private) and `renders` (public) buckets.
- [ ] Vercel project linked to the repo (`frontend/` root).
- [ ] Tenki (or Railway/Render) account; confirm it runs a Docker image with ≥ 1 GB RAM and gives a public HTTPS URL.

**Demo business materials** (from the teammate with the furniture business):

- [ ] Logo (PNG with transparency if possible, or SVG).
- [ ] 12–15 good photos: products, workshop, details, finished rooms. Varied, well lit.
- [ ] 5 star products with a one-line description and price.
- [ ] Their answers to the questionnaire (so the demo answers are realistic and fast to type).
- [ ] One real current promo or news item (makes the plan feel real).
- [ ] Permission to publish 1–3 posts on their real Instagram during the demo (and to delete them after if they want).

**Assets:**

- [ ] Download the 4 font pairs (OFL) into `backend/app/rendering/fonts/`.
- [ ] Product name + assistant name decided (see [../open-questions.md](../open-questions.md)).

## Risk register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Meta webhook/token problems | Medium | High | Permanent token prepared before; simulator as full fallback channel |
| Zernio connect redirect params differ from docs | Medium | Medium | Log the full redirect query on the first test (pre-hackathon); manual `provider_account_id` via `/dev` endpoint as fallback |
| Playwright/Chromium won't run on the host | Medium | High | Deploy the Playwright base image in H0–1 and render a test HTML immediately; fallback host Railway |
| LLM latency too high on stage (> 60 s per post) | Medium | Medium | Effort tuning; pre-seeded Brand Brain + plan; show live generation only for the ad-hoc post |
| Agents produce off-brand or hallucinated content | Medium | High | Real data from the owner, Brand Brain constraints, deterministic quality checks, rehearsal with the owner |
| Free tier limits (Zernio 2 accounts, Meta 5 recipients) | Low | Medium | Use IG only; don't connect test accounts to Zernio |
| Running out of time | High | High | MoSCoW in [../product/mvp.md](../product/mvp.md); freeze at H21; Should/Could only after Checkpoint 3 |

## After the hackathon (product path)

The demo architecture is meant to survive. Next steps in order:

1. Real job queue (arq/Redis or Postgres-based) + multiple backend instances (move locks to Postgres advisory locks).
2. RLS on Supabase; generated frontend API types from OpenAPI.
3. WhatsApp Business verification + own number + approved templates for proactive messages (weekly plan push).
4. Plans/quotas enforcement + billing (Mercado Pago / Stripe).
5. Evals for each agent (golden briefs → graded outputs) before changing prompts or models.
6. More networks (Facebook, TikTok) through the same publisher; carousels; voice notes.
