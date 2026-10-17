# Open questions & risks

## To decide before the hackathon

- [ ] **Product name and assistant name.** Needed for the welcome message, the wizard header and the pitch (`ASSISTANT_NAME`).
- [ ] **Hackathon rules:** is pre-written code allowed? If not, only accounts, materials and these docs are prepared in advance (see [implementation/plan.md](implementation/plan.md#before-the-hackathon-checklist)).
- [ ] **Backend host:** confirm Tenki runs a Docker image with Chromium (≥ 1 GB RAM) and exposes HTTPS; otherwise Railway/Render.
- [ ] **Demo materials** from the furniture business (logo, photos, products, questionnaire answers, promo, permission to publish).

## Channel / platform risk

Meta restricted general-purpose AI chatbots on the WhatsApp Business API starting Jan 15, 2026.

- [x] Demo: use the Cloud API test number ([ADR 0002](decisions/0002-whatsapp-cloud-api-channel.md)).
- [ ] Before a public launch: read the current WhatsApp Business policy and confirm a task-specific marketing assistant for the owner's own business is allowed. Our position: it's not a general-purpose assistant; it only does marketing for the business.
- [ ] Production needs Meta business verification, an own phone number, and approved templates for proactive messages (e.g. "tu plan de la semana está listo").

## Publishing

- [ ] Confirm the exact query params Zernio appends to the connect redirect (log them in the pre-hackathon test).
- [ ] Zernio pricing beyond 2 accounts (per-account) vs. building our own Meta app with app review: decide when we have >10 businesses.

## Product (post-hackathon)

- [ ] Pricing: posts per month per plan? Free trial length?
- [ ] Should owners be able to switch to "auto mode" (approve the plan once, auto-publish)? See [ADR 0007](decisions/0007-approve-every-post.md).
- [ ] Which network after Instagram: Facebook (cheap, same provider) or TikTok (needs video)?
- [ ] Voice notes: owners in the region send many. Make transcription a Must for v1?
- [ ] Measuring results: do we pull Instagram insights to show "this post brought N messages"?
- [ ] How does this evolve back toward the broader "chief of staff" vision (suppliers, orders, follow-ups)? Which second vertical?

## Add yours below
