# Integrations

External services, how we call them, and the gotchas that will bite in a 24h build. Verify shapes against the official docs linked in each section. APIs change; this was written in October 2026.

## WhatsApp Cloud API

Meta's official API, called directly (no BSP). Docs: <https://developers.facebook.com/docs/whatsapp/cloud-api>

### Setup (before the hackathon, ~1 hour)

1. Create a Meta developer app (type *Business*) and add the **WhatsApp** product.
2. Use the free **test phone number**. Add the demo phones (both builders + the furniture owner) as **recipient numbers**. The test number can only message up to 5 verified recipients, which is fine for the demo.
3. Create a **System User** in Meta Business Settings with a **permanent access token** (`whatsapp_business_messaging`, `whatsapp_business_management`). **Don't use the temporary token from the dashboard: it expires after 24 h, i.e. mid-hackathon.**
4. Configure the webhook: callback URL `https://<backend>/webhooks/whatsapp`, verify token = `META_VERIFY_TOKEN`; subscribe to the `messages` field.
5. Record: `META_PHONE_NUMBER_ID`, `META_ACCESS_TOKEN`, `META_APP_SECRET`, `META_VERIFY_TOKEN`, `META_GRAPH_VERSION` (use the latest version shown in the app dashboard), `WHATSAPP_BOT_NUMBER` (for wa.me links).

**Policy note:** since Jan 15, 2026 Meta restricts *general-purpose* AI assistants on the WhatsApp Business API. Our bot is a task-specific business service (marketing for the owner's own business). That fits the allowed use, but confirm before a public launch (see [../open-questions.md](../open-questions.md)). The test number is fine for the demo.

### Sending

`POST https://graph.facebook.com/{META_GRAPH_VERSION}/{META_PHONE_NUMBER_ID}/messages` with `Authorization: Bearer {META_ACCESS_TOKEN}`.

```jsonc
// text
{"messaging_product": "whatsapp", "to": "59899123456", "type": "text",
 "text": {"body": "¡Hola! 👋 ...", "preview_url": true}}

// image (public URL; must be reachable by Meta)
{"messaging_product": "whatsapp", "to": "59899123456", "type": "image",
 "image": {"link": "https://.../renders/abc.jpg", "caption": "..."}}

// reply buttons with image header (post preview)
{"messaging_product": "whatsapp", "to": "59899123456", "type": "interactive",
 "interactive": {
   "type": "button",
   "header": {"type": "image", "image": {"link": "https://.../renders/abc.jpg"}},
   "body": {"text": "📝 Post para el martes 21 — \"Mesa Nórdica\"\n\n..."},
   "action": {"buttons": [
     {"type": "reply", "reply": {"id": "post_approve:7f3c...", "title": "Aprobar"}},
     {"type": "reply", "reply": {"id": "post_change:7f3c...",  "title": "Cambiar"}},
     {"type": "reply", "reply": {"id": "post_discard:7f3c...", "title": "Descartar"}}
   ]}}}

// mark as read (+ typing indicator while we work)
{"messaging_product": "whatsapp", "status": "read", "message_id": "wamid...",
 "typing_indicator": {"type": "text"}}
```

Limits we design around: max **3** reply buttons; button title ≤ **20** chars; button id ≤ 256 chars; interactive body ≤ **1,024** chars; image caption ≤ 1,024 chars.

### Receiving

Webhook payload (simplified). Iterate `entry[].changes[].value`:

```jsonc
{
  "contacts": [{"profile": {"name": "Laura"}, "wa_id": "59899123456"}],
  "messages": [{
    "from": "59899123456", "id": "wamid.HBg...", "timestamp": "1760712000",
    "type": "text", "text": {"body": "hola"}
    // or "type": "interactive", "interactive": {"type": "button_reply", "button_reply": {"id": "post_approve:7f3c", "title": "Aprobar"}}
    // or "type": "image", "image": {"id": "<media_id>", "mime_type": "image/jpeg", "caption": "..."}
    // or "type": "audio" | "sticker" | "video" | "document" | "location" → unsupported_media
  }],
  "statuses": [{"id": "wamid...", "status": "delivered", "recipient_id": "..."}]  // update messages.status
}
```

Handling rules:

- **Verify** `X-Hub-Signature-256` = `sha256=` + HMAC-SHA256(app secret, raw body). Compute on the raw bytes, before JSON parsing.
- **Return 200 fast.** Meta retries on slow or failed responses, and that produces duplicates. Dedupe on `messages.id` (unique `messages.external_id`).
- **Media download:** `GET /{version}/{media_id}` → `{"url": ...}`, then `GET url` with the same bearer token. URLs expire in minutes, so download immediately.
- **24-hour window:** free-form messages can only be sent within 24 h of the owner's last message. Jobs finish within minutes, so this doesn't affect the demo. Outside the window we would need approved templates (Won't for the MVP).

## Publishing provider: Zernio

Unified social publishing API (formerly *Late*, getlate.dev). Chosen because the **free tier includes full API access** (first 2 connected accounts free, unlimited posts) and a **hosted connect link we generate per business**, so we don't need our own Meta app review for Instagram publishing. See [ADR 0008](../decisions/0008-publishing-via-zernio.md) and [research](../research/social-publishing-apis.md). Docs: <https://docs.zernio.com>

### Setup (before the hackathon)

1. Sign up at zernio.com (no card) and create an API key → `ZERNIO_API_KEY`.
2. Make sure the demo Instagram account is **Business or Creator** (Instagram Login is used, so no Facebook Page is needed).
3. Do one end-to-end test the day before: create profile → connect → publish a test image → delete it from IG.
4. Optional: register a webhook (`POST /v1/webhooks/settings`) with our `ZERNIO_WEBHOOK_SECRET` for `post.published`, `post.failed`, `account.connected`.

**Free tier limit:** 2 connected accounts **across the whole team**. IG + Facebook Page for the demo business uses both slots, so connect **Instagram only** unless the FB cross-post is needed. A 3rd account returns `402 PAYMENT_REQUIRED`. Instagram caps: 25 posts/hour and 100/day per account.

### Calls

Base URL `https://zernio.com/api/v1`, header `Authorization: Bearer {ZERNIO_API_KEY}`. Use `httpx` directly (thin, explicit); the `zernio-sdk` PyPI package exists if preferred.

```python
# 1. One Zernio profile per business (store as social_accounts.provider_profile_id)
POST /v1/profiles
{"name": "Muebles Ramírez", "externalId": "<business_id>"}
→ {"profile": {"_id": "prof_..."}}

# 2. Hosted connect link (send the owner's browser to auth_url)
GET /v1/connect/instagram?profileId=prof_...&redirect_url=https://<frontend>/o/<token>?step=instagram&connected=1
→ {"authUrl": "https://..."}
# Zernio redirects back with query params including the connected accountId → store as provider_account_id

# 3. Publish now or schedule
POST /v1/posts
{
  "content": "<caption + hashtags>",
  "mediaItems": [{"type": "image", "url": "https://<supabase>/storage/v1/object/public/renders/<id>.jpg"}],
  "platforms": [{"platform": "instagram", "accountId": "<provider_account_id>"}],
  "publishNow": true
  // or: "scheduledFor": "2026-10-21T19:00:00", "timezone": "America/Montevideo"
}
→ 201 {"post": {"_id": "...", "status": "published", "platforms": [{"platformPostUrl": "https://www.instagram.com/p/..."}]}}
→ 207 = partial failure (check post.status and per-platform errors)
```

Gotchas:

- Media URL must be **public HTTPS returning the raw file**, JPEG/PNG < 8 MB, aspect ratio between 4:5 and 1.91:1. Our renders are 1080×1350 (4:5) JPEG in the public `renders` bucket, which fits.
- Treat `207` and any `post.status != "published"` as failure for "publish now".
- Webhook signature: `X-Zernio-Signature` = HMAC-SHA256 of the raw body with our secret.
- Things not verified by research: the exact query param names on the connect redirect (log the full query on the first test and adapt `instagram/callback`), and whether old getlate.dev URLs still work (build only against `zernio.com/api/v1`).

### Mock publisher

`PUBLISHER=mock` → `MockPublisher` returns `published` with `permalink = https://instagram.com/p/MOCK-<post_id>` after a 2 s delay, and `connect_url` returns a frontend URL that marks the account connected. Used for local dev, the simulator, and the stage fallback.

## Claude API

See [agents.md](agents.md#llm-client-conventions) for the full conventions (model, effort, structured output, caching, fallbacks, logging). Setup: `ANTHROPIC_API_KEY` from console.anthropic.com. Check the account's rate limits before the hackathon; a demo run is roughly 10–15 calls per post-heavy minute.

## Supabase (Postgres + Storage)

- Create a project (free tier). Record `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY` (backend only, never in the frontend), `DATABASE_URL` (use the **session pooler** connection string for asyncpg; the transaction pooler breaks prepared statements unless `statement_cache_size=0`).
- Apply the schema with `uv run alembic upgrade head` (see [data-model.md](data-model.md)).
- Buckets: `assets` (**private**) and `renders` (**public**).
- Python: `supabase` client for storage only (`storage.from_(bucket).upload(path, data, {"content-type": mime})`, `create_signed_url(path, 3600)`, `get_public_url(path)`); SQLAlchemy 2 async + asyncpg for the DB.
- Storage paths: `assets/{business_id}/{asset_id}.{ext}`, `renders/{business_id}/{post_id}-r{revision}.jpg` (new path per revision, so WhatsApp/IG never serve a cached old image).

## Renderer (HTML → image)

- Templates: Jinja2 HTML + CSS in `backend/app/rendering/templates/{template_id}.html`. Specs in [../design/post-templates.md](../design/post-templates.md).
- Engine: Playwright (async, Chromium). Launch **one browser at app startup**; per render: new page, viewport 1080×1350, `set_content(html)`, wait for `document.fonts.ready` and images loaded, `screenshot(type="jpeg", quality=90)`, close page.
- Assets in HTML: embed the photo and logo as **data URIs** (bytes fetched from storage by the backend) and the fonts as base64 `@font-face` (loaded once at startup). No network access during render, so rendering is deterministic.
- Fonts bundled in `backend/app/rendering/fonts/` (Google Fonts, OFL): `modern` = Inter + Inter Tight, `classic` = Playfair Display + Source Sans 3, `warm` = Fraunces + DM Sans, `bold` = Archivo Black + Archivo.
- Docker: follow [`.claude/rules/docker.md`](../../.claude/rules/docker.md) (pinned `python:3.13-slim-*` base, multi-stage, non-root) and install the browser in the final stage with `playwright install --with-deps chromium`. Needs ≥ 1 GB RAM.
- Target: < 3 s per render.

## Optional (Could)

- **Voice notes**: WhatsApp audio is OGG/Opus. Transcribe with `faster-whisper` (`small` model, CPU, `language="es"`) inside the backend container, then treat the transcript as text. Adds ~500 MB to the image and a few seconds per note; only if everything else is done.
- **AI image generation**: `ImageGenPort` with a `NoneImageGen` default. If a Google AI Studio or OpenAI key becomes available, add an implementation used by the Art Director for `background`-only fills (never for products: real photos of real furniture beat generated ones).
