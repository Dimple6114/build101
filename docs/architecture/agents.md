# Agents

The "agency" is one **orchestrator** (the account manager the owner talks to) plus a **fixed catalog of specialist agents** that become personal to each business through its **Brand Brain**. We don't generate agents per business. Every business gets the same team, and the Brand Brain plus the business's assets and history make their work specific. See [ADR 0006](../decisions/0006-fixed-agent-catalog-brand-brain.md).

## Catalog

| Agent | Kind | Called by | Input → Output | Effort |
|---|---|---|---|---|
| **Orchestrator** | Tool-use loop | Inbound handler | Conversation + context → reply text + tool calls | `low` |
| **Asset Analyst** | Single call, vision, structured | `analyze_asset` job | Image → description, tags, palette, usable-for | `low` |
| **Brand Strategist** | Single call, structured | `generate_brand` job | Onboarding data + asset descriptions (+ correction) → Brand Brain | `high` |
| **Content Strategist** | Single call, structured | `generate_plan` job | Brand Brain + recent posts + date + notes → weekly plan | `medium` |
| **Copywriter** | Single call, structured | `generate_post` job | Brand Brain + brief (+ feedback, previous version) → copy | `medium` |
| **Art Director** | Single call, vision, structured | `generate_post` job | Brand Brain + copy + candidate photos + template catalog → render spec | `medium` |
| **Feedback Classifier** | Single call, structured | `revise_post` job | Feedback text → `copy` / `image` / `both` + normalized instruction | `low` |

Not agents (deterministic services): **Renderer** (render spec → JPEG), **Publisher** (approved post → provider API), **Scheduler** (delegated to the provider).

## LLM client conventions

All Claude calls go through `app/llm/client.py`. It's the only module that imports `anthropic`.

- SDK: official `anthropic` Python SDK, `AsyncAnthropic` client. Read the key from `ANTHROPIC_API_KEY`.
- Model: `claude-opus-5-5` for every agent (configurable per agent in `config.py`). Tune **effort** per agent (table above) rather than switching models. Thinking is always on in this model, so don't send `thinking: disabled` or `budget_tokens` (both return 400). Control depth with `output_config={"effort": ...}`.
- **Structured output** for every specialist: Pydantic model → `output_config={"format": {"type": "json_schema", "schema": Model.model_json_schema()}}` (or `client.messages.parse(output_format=Model)`), then `Model.model_validate_json(...)`. Keep schemas simple: objects, strings, ints, enums, lists. Set `additionalProperties: false` and put every field in `required`.
- **Refusal fallback**: enable server-side fallbacks on every call (`betas=["server-side-fallback-2026-07-01"]`, `fallbacks="default"` on `client.beta.messages.create`). Always check `stop_reason` (`refusal`, `max_tokens`) before reading content.
- **Prompt caching**: top-level `cache_control={"type": "ephemeral"}`. Order the prompt stable → volatile: system prompt (static) → Brand Brain (per business) → dynamic context. Never put timestamps in the system prompt.
- **Images**: pass by URL (`{"type": "image", "source": {"type": "url", "url": signed_url}}`) using a short-lived signed Supabase URL, or base64 for small files. Resize to max 1568 px on the long side before upload to save tokens.
- **Timeouts/retries**: SDK defaults (2 retries). Per-call timeout 90 s for specialists, 30 s per orchestrator step.
- **Logging**: each call writes `agent_runs` (business_id, agent, model, effort, input JSON, output JSON, input/output/cache tokens, latency_ms, stop_reason, error).
- **Max tokens**: 16000 for specialists, 4000 for orchestrator steps.

Before changing any of this, check the current Claude API docs. Model IDs and parameters change.

## Brand Brain

The single source of truth about a business, consumed by every agent. Stored as versioned JSON in `brand_brains` (each change = new version; agents read the latest).

```python
class Voice(BaseModel):
    descriptors: list[str]            # 3–5 adjectives, e.g. ["cercano", "cálido", "artesanal"]
    formality: int                    # 1 (muy informal) – 5 (muy formal)
    humor: int                        # 1 (serio) – 5 (divertido)
    emoji_policy: Literal["many", "few", "none"]
    do: list[str]                     # "Hablar de vos", "Mencionar que es hecho a mano"
    dont: list[str]                   # "No hablar de precios", "No usar 'barato'"
    sample_phrases: list[str]         # 3–5 phrases in the brand's voice (Rioplatense)

class Audience(BaseModel):
    name: str                         # "Parejas jóvenes armando su primera casa"
    description: str
    pains: list[str]
    motivations: list[str]

class ContentPillar(BaseModel):
    id: str                           # slug: "a-medida"
    name: str                         # "Piezas a medida"
    description: str
    example_ideas: list[str]

class Product(BaseModel):
    name: str
    description: str
    price: str | None                 # free text as the owner wrote it
    asset_ids: list[str]              # photos that show it

class VisualIdentity(BaseModel):
    primary_color: str                # hex
    secondary_color: str
    accent_color: str
    background_color: str
    text_color: str
    font_pair: Literal["modern", "classic", "warm", "bold"]   # maps to bundled fonts
    logo_asset_id: str | None
    photo_style: str                  # "luz natural, madera, ambientes cálidos"

class BrandBrain(BaseModel):
    business_name: str
    one_liner: str
    description: str
    category: str
    location: str
    goal: Literal["sales", "awareness", "launch", "loyalty"]
    audiences: list[Audience]         # 1–3
    value_props: list[str]            # 3–5
    voice: Voice
    pillars: list[ContentPillar]      # 3–5
    products: list[Product]
    current_offers: list[str]
    ctas: list[str]                   # "Escribinos por WhatsApp", "Visitá el showroom"
    hashtags: list[str]               # 10–20, mix of niche + local
    posting: PostingPrefs             # posts_per_week, preferred_days, preferred_time ("19:00")
    constraints: list[str]            # hard "never" rules from the owner
    whatsapp_summary: str             # ≤ 600 chars, WhatsApp-formatted, for brand_summary message
```

`PostingPrefs`: `posts_per_week: int`, `preferred_days: list[Literal["mon",...,"sun"]]`, `preferred_time: str` (HH:MM, local).

Agents receive the Brand Brain rendered as compact JSON inside a `<brand_brain>` tag in the system prompt. It sits right after the static instructions so it's cached per business.

## Specialist agents

Each agent lives in `app/agents/<name>.py` with:

- `Input` and `Output` Pydantic models (in `app/agents/schemas.py`),
- a system prompt in `app/agents/prompts/<name>.md`,
- one public function `async def run(input: Input, *, business_id: UUID) -> Output`.

Prompts are written in English (instructions) and require output content in Rioplatense Spanish. Every prompt includes the voice rules from [../product/conversation-design.md](../product/conversation-design.md) where relevant.

### Asset Analyst

**Purpose:** understand each uploaded image so other agents can choose photos without looking at every image again.

- Input: `asset_id`, image (URL), `kind` (`logo` | `photo`), owner-provided hint (optional, e.g. product name).
- Output:

  ```python
  class AssetAnalysis(BaseModel):
      description: str                 # 1–2 sentences in Spanish: what's in the photo
      subjects: list[str]              # ["mesa de comedor", "roble", "living"]
      product_guess: str | None        # matches a Product.name if obvious
      quality: Literal["high", "ok", "low"]   # blur, lighting, framing
      orientation: Literal["portrait", "landscape", "square"]
      has_people: bool
      has_text: bool
      dominant_colors: list[str]       # hex, from the model (logo: refined by Pillow palette)
      best_for: list[Literal["hero", "background", "detail", "behind_the_scenes"]]
      safe_crop_focus: Literal["center", "top", "bottom", "left", "right"]
  ```

- Logo special case: also run a deterministic palette extraction (Pillow quantize to 5 colors, ignore near-white/near-black/transparent) and store both. The web wizard shows the Pillow palette as editable swatches.

### Brand Strategist

**Purpose:** turn onboarding inputs into the Brand Brain. Also handles corrections.

- Input: business fields, products, questionnaire answers, owner's "3 words", asset analyses (descriptions only, not images), Pillow palette + owner-confirmed colors, optional `previous_brand_brain` + `correction` (revise mode).
- Output: `BrandBrain`.
- Rules in the prompt:
  - Use only facts given by the owner; mark nothing as fact that wasn't provided (no invented awards, years, locations).
  - Owner-confirmed colors win over model guesses.
  - `constraints` must include every "no quiero que..." answer verbatim.
  - In revise mode: change only what the correction implies; keep everything else.
  - `whatsapp_summary` follows the 4-bullet format in conversation-design.md.

### Content Strategist

**Purpose:** weekly plan.

- Input: Brand Brain, `week_start` (date), `posts_count`, today's date, last 10 posts (title, pillar, date), owner notes ("cambiá la 2 por algo de la promo de sillas"), previous plan (revise mode), list of available assets (id + description + best_for).
- Output:

  ```python
  class PlanItem(BaseModel):
      scheduled_for: datetime          # local time, within the week, uses preferred days/time
      pillar_id: str
      title: str                       # ≤ 40 chars, internal + shown in plan list
      idea: str                        # 1–2 sentences: what the post says
      angle: str                       # why it works for the audience
      suggested_asset_ids: list[str]   # 1–3 candidates from available assets
      suggested_template: TemplateId
  class WeeklyPlan(BaseModel):
      items: list[PlanItem]
      whatsapp_text: str               # numbered list for plan_preview, ≤ 900 chars
  ```

- Rules: rotate pillars, don't repeat a product two posts in a row, use `current_offers` at most once per week unless asked, only reference assets that exist, respect `constraints`. Commercial dates may be used only when they fall in the plan week and come from the `commercial_dates` list passed in the input (a small static list per country in `app/agents/data/commercial_dates_uy.json`, so the model never guesses dates).

### Copywriter

**Purpose:** write the caption and on-image text.

- Input: Brand Brain, brief (plan item or ad-hoc request text), platform (`instagram`), optional `previous` copy + `feedback` (revise mode).
- Output:

  ```python
  class PostCopy(BaseModel):
      title: str                       # internal title, ≤ 40 chars
      headline: str                    # on-image, ≤ 40 chars, no hashtags/emojis
      subheadline: str | None          # on-image, ≤ 60 chars
      caption: str                     # 150–900 chars, Instagram-ready, line breaks allowed
      cta: str                         # included at the end of the caption too
      hashtags: list[str]              # 5–10, without '#' duplicates, lowercase, no spaces
  ```

- Rules: voice from the Brand Brain; first line must hook (≤ 80 chars); no invented facts (prices, discounts, dates only if in brief or Brand Brain); respect emoji policy; Rioplatense *vos*; never mention AI. In revise mode, apply the feedback literally and change as little else as possible.

### Art Director

**Purpose:** decide what the image looks like. It picks, it doesn't draw.

- Input: Brand Brain (visual identity), `PostCopy`, candidate assets (IDs + analyses + **the images themselves**, max 4, as URLs), template catalog (IDs, slots, best-for — see [../design/post-templates.md](../design/post-templates.md)), optional feedback + previous spec (revise mode), optional `force_asset_id`.
- Output (`RenderSpec`):

  ```python
  class RenderSpec(BaseModel):
      template_id: TemplateId          # "product_hero" | "promo_band" | "quote_card" | "split_story"
      photo_asset_id: str | None       # required unless template is text-only
      crop_focus: Literal["center", "top", "bottom", "left", "right"]
      slots: dict[str, str]            # template slot → text, e.g. {"headline": "...", "badge": "15% OFF"}
      color_roles: ColorRoles          # background, text, accent: hex from the brand palette only
      show_logo: bool
  ```

- Rules: only colors from `visual_identity`; text in slots must fit template max lengths (validated after the call, see below); prefer `quality=high` photos; for promos use `promo_band`; for tips/quotes without a strong photo use `quote_card`.
- **Post-validation (code):** check slot lengths, color hex membership, asset ownership. On violation, retry once with the error list appended; if it fails again, fall back to `product_hero` with the copy headline.

### Feedback Classifier

- Input: feedback text, current copy, current render spec summary.
- Output: `{"target": "copy" | "image" | "both", "instruction": str}` (instruction = normalized, explicit version of the feedback, e.g. "Acortar el caption a 2 líneas y mencionar envío gratis en Montevideo").

## Orchestrator

A manual tool-use loop in `app/orchestrator/orchestrator.py` (we need async, DB persistence and our own guards, so we don't use the SDK's beta tool runner).

### Per-turn algorithm

```text
run_turn(business, inbound_text):
    context = build_context(business)        # brand summary, pending posts, awaiting state, now
    history = last 20 messages (role user/assistant, text only)
    messages = history + [user: inbound_text (+ pending-state note)]
    for step in range(MAX_STEPS = 5):
        resp = llm.create(system=[static_prompt, brand_block, dynamic_block], tools=TOOLS, messages)
        handle stop_reason: refusal → send generic fallback text; max_tokens → truncate safely
        append resp.content (all blocks, including thinking) to messages
        if no tool_use blocks: break
        execute all tool_use blocks (concurrently), append ONE user message with all tool_results
    reply = concatenated text blocks of the last response
    if reply: channel.send_text(reply); store assistant message
```

- History rebuilt from the DB each turn contains **text only** (no tool or thinking blocks from earlier turns). Within a turn, pass `resp.content` back unchanged (thinking blocks included).
- Tools are defined with `strict: true` and `additionalProperties: false`.
- `tool_choice` stays `auto`. Forced tool choice is not supported on this model.
- If the model returns text **and** a long-running tool, send the text (the acknowledgement) and let the job send the result.

### Tools

| Tool | Input | Does | Returns |
|---|---|---|---|
| `plan_week` | `notes?: str`, `week_start?: date` | Enqueue `generate_plan` | `{job_id, status: "started"}` |
| `revise_plan` | `plan_id`, `feedback` | Enqueue `generate_plan` (revise mode) | `{job_id}` |
| `create_post` | `brief: str`, `scheduled_for?: datetime`, `asset_id?: str` | Create post row + enqueue `generate_post` | `{post_id, job_id}` |
| `revise_post` | `post_id`, `feedback` | Enqueue `revise_post` | `{job_id}` |
| `approve_post` | `post_id` | Same handler as `[Aprobar]` button (sends `publish_when`) | `{status}` |
| `publish_post` | `post_id`, `when: "now" \| ISO datetime` | Guard: status must be `approved`; enqueue `publish_post` | `{job_id}` or error |
| `discard_post` | `post_id` | Status → `discarded` | `{status}` |
| `list_posts` | `statuses?: list[str]`, `limit?: int` | Query posts | `[{id, title, status, scheduled_for, permalink}]` |
| `get_brand_summary` | — | Read latest Brand Brain | `{whatsapp_summary, pillars, offers, constraints}` |
| `update_brand_brain` | `change: str` | Enqueue `generate_brand` revise mode (silent: no summary message unless asked) | `{job_id}` |
| `cancel_pending` | — | Clear `conversation_state.awaiting` | `{ok}` |

Guards are in the tool implementations, not in the prompt: `publish_post` returns `{"error": "post_not_approved"}` if the status is wrong, and the model must relay that.

### Context block (dynamic, after the cache breakpoint)

```text
<now>2026-10-20T14:32:00-03:00 (lunes)</now>
<awaiting>post_feedback for post 7f3c… ("Mesa Nórdica")</awaiting>
<pending_posts>
- 7f3c… "Mesa Nórdica" — pending_approval — mar 21 19:00
- 1a9e… "Promo sillas" — approved — sin fecha
</pending_posts>
<instagram_connected>true</instagram_connected>
```

## Job pipelines

| Job | Steps | Sends to owner |
|---|---|---|
| `analyze_asset(asset_id)` | Asset Analyst → save analysis (+ Pillow palette for logos) | nothing (or `photo_saved` for WhatsApp photos) |
| `generate_brand(business_id, correction?)` | wait for pending `analyze_asset` → Brand Strategist → save new version | `brand_summary` (onboarding/correction) |
| `generate_plan(business_id, notes?, plan_id?)` | Content Strategist → save plan + items | `plan_preview` |
| `generate_post(post_id)` | Copywriter → Art Director → validate → Renderer → upload → save | `post_preview` |
| `revise_post(post_id, feedback)` | Feedback Classifier → (Copywriter) → (Art Director) → Renderer → save revision | `post_preview` |
| `publish_post(post_id, when)` | guard → Publisher (now / schedule) → save external id + permalink | `published` / `scheduled` / `publish_failed` |

Posts from an approved plan are generated **sequentially** in plan order, so previews arrive in order and we stay under rate limits.

## Quality checks (cheap, deterministic)

Run after every agent call, before saving:

- Caption length 150–900 chars; headline ≤ 40; hashtags 5–10, no duplicates.
- No phrase from `constraints` appears in caption/headline (case-insensitive substring).
- No price/discount numbers in copy unless they appear in the brief or Brand Brain (regex for `%`, `$`, `USD`, `UYU`).
- Referenced asset IDs belong to the business.

On failure: one retry with the violations listed; then accept and log a warning (demo shouldn't block).
