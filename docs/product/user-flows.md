# User flows

How the product behaves, step by step. Copy for every message lives in [conversation-design.md](conversation-design.md); the code-level contracts live in [../architecture/](../architecture/).

Conventions:

- **Owner** = the business owner on WhatsApp. **Bot** = the orchestrator. **System** = backend jobs and agents.
- `[Botón]` = WhatsApp interactive reply button. Button IDs are listed in [../architecture/api.md](../architecture/api.md#button-ids).
- Anything in *italics* is a background job: the bot acknowledges right away and messages again when the job ends.

## State machines

These three state machines drive everything. They are enforced in code (deterministic), never by the LLM.

### Business onboarding state (`businesses.onboarding_state`)

```mermaid
stateDiagram-v2
    [*] --> new: first inbound message
    new --> awaiting_name: welcome sent
    awaiting_name --> awaiting_web_form: name received, magic link sent
    awaiting_web_form --> generating_brand: web form submitted
    generating_brand --> awaiting_brand_confirmation: Brand Brain ready, summary sent
    awaiting_brand_confirmation --> active: [Sí, es mi marca]
    awaiting_brand_confirmation --> generating_brand: correction in free text
    active --> active
```

While `onboarding_state != active`, inbound messages are handled by the **onboarding router** (deterministic copy + light LLM for free-text answers). Once `active`, they go to the **orchestrator**.

### Post status (`posts.status`)

```mermaid
stateDiagram-v2
    [*] --> generating
    generating --> pending_approval: preview sent
    generating --> failed: agent/render error
    pending_approval --> approved: [Aprobar]
    pending_approval --> revising: [Cambiar] + feedback
    pending_approval --> discarded: [Descartar]
    revising --> pending_approval: new preview sent
    approved --> publishing: publish now
    approved --> scheduled: schedule accepted by provider
    scheduled --> published: provider webhook / poll
    publishing --> published
    publishing --> failed
    scheduled --> failed
    failed --> generating: retry
    published --> [*]
    discarded --> [*]
```

Rule: **the only way into `approved` is the owner's button tap** (or an explicit "sí, aprobalo" that the orchestrator converts into the same `approve_post` handler, see Flow 6). The publish service refuses any post that is not `approved` or `scheduled`.

### Content plan status (`content_plans.status`)

`generating → pending_approval → approved | revising → pending_approval`. Approving a plan creates one `posts` row per item (status `generating`) and starts generation.

### Pending input (`businesses.conversation_state`)

A small JSON object that says what the next free-text message means. It is set by button handlers and cleared after use:

| `awaiting` | Set when | Next free-text message is treated as |
|---|---|---|
| `null` | default | normal orchestrator turn |
| `business_name` | onboarding step 1 | the business name |
| `brand_correction` | owner taps [Corregir algo] on the Brand Brain summary | a correction to the Brand Brain |
| `plan_feedback` | owner taps [Cambiar] on a plan | feedback for the plan (`plan_id`) |
| `post_feedback` | owner taps [Cambiar] on a post | feedback for the post (`post_id`) |
| `schedule_time` | owner taps [Programar] | a date/time in natural language (`post_id`) |

If the owner writes something unrelated while `awaiting` is set (e.g. a new request), the orchestrator gets the message **plus** the pending context and decides; it can call `cancel_pending` and handle the new request.

---

## Flow 1 — First contact

Trigger: a phone number with no `businesses` row sends any message (in the demo: "Hola").

1. System creates `businesses` row (`onboarding_state = new`, `owner_phone`), stores the message.
2. Bot sends the welcome (who it is, what it does, that nothing is published without approval) and asks for the business name. State → `awaiting_name`.
3. Owner replies with the name ("Muebles Ramírez").
4. Bot confirms, creates a magic link (`/o/{token}`, valid 7 days, reusable until the form is submitted) and sends it with a short explanation: "5 minutos, desde el celu". State → `awaiting_web_form`.
5. If the owner writes again before finishing the form, the bot answers briefly and re-sends the link. It doesn't try to run the orchestrator yet.

## Flow 2 — Web onboarding form

Opened from the magic link on the owner's phone. Mobile-first wizard, progress saved after each step (owner can close and come back). Details and wireframes in [../design/web-app.md](../design/web-app.md).

| Step | Fields | Notes |
|---|---|---|
| 1. Tu negocio | Name (prefilled), category (select), one-line description, longer description (optional), city/zone, website or IG handle (optional) | Category list: Muebles y deco, Gastronomía, Indumentaria, Belleza, Servicios, Otro |
| 2. Productos | Up to 5 star products/services: name, short description, price (optional) | "¿Qué es lo que más vendés?" |
| 3. Tu marca | Logo upload; brand colors (auto-detected from logo, editable as swatches); "¿Cómo hablarían de tu marca tus clientes?" (3 words) | Colors are extracted server-side from the logo right after upload |
| 4. Fotos | Upload 3–15 photos (products, workshop, team) | The more, the better; show thumbnails; at least 3 required |
| 5. Preferencias | Questionnaire (see below) | All single taps, no long text |
| 6. Conectá Instagram | Button → provider's hosted connect flow → returns to the wizard with ✅ | Skippable ("Lo hago después"); publishing is then mocked until connected |
| 7. ¡Listo! | Summary + "Volver a WhatsApp" (wa.me deep link) | Submitting triggers Flow 3 |

Questionnaire (step 5):

| Question | Type | Options |
|---|---|---|
| ¿Qué querés lograr con tus redes? | single | Más consultas y ventas · Que me conozca más gente · Lanzar algo nuevo · Fidelizar a mis clientes |
| ¿A quién le vendés? | multi | Familias · Parejas jóvenes · Empresas/oficinas · Arquitectos/decoradores · Otro (texto) |
| ¿Cómo querés sonar? | 2 sliders | Formal ↔ Cercano · Serio ↔ Divertido |
| ¿Cuántas publicaciones por semana? | single | 2 · 3 · 5 |
| ¿Usamos emojis? | single | Sí, bastantes · Pocos · Ninguno |
| ¿Hay algo que NO quieras que digamos o mostremos? | short text (optional) | e.g. "no hablar de precios" |
| ¿Tenés alguna promo o novedad ahora? | short text (optional) | Feeds the first weekly plan |

On submit: `POST /api/onboarding/complete` → state `generating_brand` → Flow 3 starts in the background.

## Flow 3 — Brand Brain generation and confirmation

1. *System runs the Asset Analyst on each uploaded image that doesn't have a description yet (parallel, max 5 concurrent).*
2. *System runs the Brand Strategist with all onboarding data + asset descriptions → Brand Brain v1 (saved, versioned).*
3. Bot sends to WhatsApp: "¡Listo! Esto es lo que entendí de tu marca 👇" + a short summary (tone in 3 words, audience, 3 content pillars, colors as emoji-free text) + buttons `[Sí, es mi marca]` `[Corregir algo]`. State → `awaiting_brand_confirmation`.
4. `[Sí, es mi marca]` → state `active` → bot offers the first plan: "¿Arrancamos con el plan de esta semana?" `[Dale]` `[Más tarde]`.
5. `[Corregir algo]` → `awaiting = brand_correction` → owner writes the correction → *Brand Strategist runs in "revise" mode (Brand Brain v2)* → back to step 3.

Target time from form submit to summary: **< 60 s**.

## Flow 4 — Weekly plan

Trigger: `[Dale]` after onboarding, or free text like "armame el plan de la semana" (orchestrator → `plan_week`).

1. Bot: "Dale, armo el plan de la semana ⏳".
2. *Content Strategist generates N items (N = posts per week from onboarding; demo default 3). Each item: date, pillar, format (single image), idea, angle, suggested photo asset IDs, suggested template.*
3. Bot sends the plan as one message:

   ```text
   📅 Plan semana del 20/10
   1. Mar 21 — Producto estrella: la mesa de roble Nórdica, foco en la madera maciza
   2. Jue 23 — Detrás de escena: así se hace una silla en el taller
   3. Sáb 25 — Promo: 10% off en racks de TV este fin de semana
   ```

   with buttons `[Aprobar plan]` `[Cambiar algo]`.
4. `[Aprobar plan]` → plan `approved`, one `posts` row per item → bot: "¡Genial! Te mando las publicaciones a medida que estén listas" → Flow 5 for each post (sequentially, so previews arrive in order).
5. `[Cambiar algo]` → `awaiting = plan_feedback` → owner: "cambiá la 2 por algo de la promo de sillas" → *Content Strategist revises* → step 3.

## Flow 5 — Post generation and approval

Trigger: plan approval (one per item), ad-hoc request (Flow 7), or revision (Flow 6).

1. *Copywriter* produces: caption (150–900 chars), hashtags (5–10), CTA, `headline` (≤ 40 chars for the image), optional `subheadline` (≤ 60 chars).
2. *Art Director* chooses: template ID, photo asset ID (from the business's photos), text for each template slot, color roles (from the Brand Brain palette). Output is a **render spec** (JSON).
3. *Renderer* (deterministic, no LLM) renders HTML template → JPEG 1080×1350 → uploads to storage → public URL.
4. Bot sends **one interactive message**: image header + body (label line + full caption + hashtags) + buttons:

   ```text
   [image header]
   📝 Post para el martes 21 — "Mesa Nórdica"

   <full caption + hashtags>

   [Aprobar] [Cambiar] [Descartar]
   ```

   WhatsApp limits the interactive body to 1,024 chars. If the body would exceed it, send the full caption first as a plain text message and use a short body ("📝 Post para el martes 21 — ¿lo aprobás?") in the interactive message. See [../architecture/integrations.md](../architecture/integrations.md#whatsapp-cloud-api).
5. Post status → `pending_approval`.

Target time per post: **< 45 s** from start to preview.

## Flow 6 — Change request (revision)

1. Owner taps `[Cambiar]` → bot: "¿Qué le cambio? Podés decirme cosas como 'más corto', 'otra foto', 'mencioná el envío gratis'". `awaiting = post_feedback`.
2. Owner writes feedback.
3. System classifies the feedback (inside the revision job, one LLM call): `copy` / `image` / `both`.
   - `copy` → Copywriter revises with feedback + previous version.
   - `image` → Art Director re-picks photo/template/text; re-render.
   - `both` → both, copy first.
4. `post_revisions` row saved (keeps history); `posts.revision += 1`; Flow 5 step 4 again.
5. After 3 revisions, bot adds: "Si preferís, mandame una foto que te guste para este post 📸".

Free-text approval: if the owner writes "dale, publicalo" while a single post is `pending_approval`, the orchestrator calls `approve_post(post_id)`. If several are pending, it asks which one, showing the list.

## Flow 7 — Ad-hoc post

Trigger: free text like "hacé un post para la promo del finde, 15% en sillas".

1. Orchestrator calls `create_post(brief=..., when=null)`; bot: "¡Dale! Lo armo ⏳".
2. Flow 5 with the brief instead of a plan item. The Copywriter receives the brief verbatim plus the Brand Brain.
3. If the request is missing something essential (e.g. "hacé un post de la promo" and there is no promo in the Brand Brain or chat), the orchestrator asks **one** short question before calling the tool.

## Flow 8 — Publish or schedule

After `[Aprobar]`:

1. If the post has a planned date in the future → bot: "¿Lo programo para el martes 21 a las 19:00 o lo publico ya?" `[Programar]` `[Publicar ahora]`.
   If not (ad-hoc) → `[Publicar ahora]` `[Programar]`.
2. `[Publicar ahora]` → status `publishing` → Publisher service → on success `published`, store `external_post_id` + `permalink` → bot: "¡Publicado! 🎉 <permalink>".
3. `[Programar]` → if planned date exists, use it; otherwise `awaiting = schedule_time` → owner: "el jueves a las 8 de la noche" → orchestrator parses to ISO datetime in the business timezone (`America/Montevideo`) → confirm → provider schedules → status `scheduled` → bot: "Listo, sale el jueves 23 a las 20:00 ✅".
4. No Instagram connected → bot: "Para publicar necesito que conectes tu Instagram, es un toque: <link>". The post stays `approved`.
5. Failure → status `failed` → bot: "Uy, Instagram no me dejó publicarlo (<short reason>). ¿Lo intento de nuevo?" `[Reintentar]`.

## Flow 9 — Owner sends a photo in the chat

1. System downloads the media, stores it as a `brand_assets` row (`kind = photo`, `source = whatsapp`).
2. *Asset Analyst describes it.*
3. If a post is `pending_approval` and `awaiting = post_feedback`, or the caption says "usá esta para el post", the orchestrator uses it for that post (Art Director revision with `force_asset_id`).
4. Otherwise bot: "¡Buenísima! La guardo para próximos posts 📸. ¿Querés que arme un post con esta foto?" `[Sí, armalo]` `[No, guardala]`.

## Flow 10 — Everything else

| Situation | Behavior |
|---|---|
| "¿Qué podés hacer?" / "ayuda" | Orchestrator explains the 4 things it does in ≤ 5 short lines |
| "¿Qué tengo programado?" | `list_posts(status in [scheduled, approved, pending_approval])` → short list |
| Brand change in chat ("ahora tenemos envío gratis a todo el país") | `update_brand_brain(change)` → Brand Brain new version → "Anotado ✍️, lo voy a tener en cuenta" |
| Voice note | MVP: "Por ahora solo puedo leer mensajes de texto 🙏 ¿Me lo escribís?" (Could: transcribe) |
| Sticker, video, location, document | Same polite "solo texto y fotos por ahora" |
| Out-of-scope request ("¿me hacés una factura?") | Explain what it does; no tool call |
| Repeated webhook delivery | Ignored (idempotency on `wa_message_id`) |
| Message while a job is running | Answered normally; jobs post their results when done |
| Agent or render error | Post → `failed`; bot apologizes in one line, offers `[Reintentar]`; full error in `agent_runs` |
