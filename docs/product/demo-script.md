# Demo script

~4 minutes. The furniture business owner (our teammate) plays themself on a real phone; the phone screen is mirrored on the projector. Fill in the placeholders once the materials are collected.

| Placeholder | Value |
|---|---|
| `{BUSINESS}` | Name of the teammate's furniture business |
| `{IG_HANDLE}` | Its Instagram handle |
| `{PRODUCT}` | One star product (e.g. a dining table) |
| `{PROMO}` | A real current promo |

## Setup before going on stage

- [ ] Backend deployed, `/health` OK; `PUBLISHER=zernio`; IG connected for `{BUSINESS}`.
- [ ] **Two businesses ready:**
  - *Live onboarding*: the presenter's phone is reset to `new` (`/dev/businesses/{id}/reset`).
  - *Seeded*: `{BUSINESS}` already `active` with a Brand Brain and an approved plan (from `/dev/seed/demo`), used if live onboarding is slow.
- [ ] Wizard photos and logo already in the phone's camera roll, in an album.
- [ ] `/dev/chat` open in a hidden browser tab (fallback channel).
- [ ] Backup video of the full flow ready to play.
- [ ] One older post already published by the system on `{IG_HANDLE}` (proof if the live publish fails).

## Script

### 0:00 – Problem (30 s)

Narrator:
> "{Owner} tiene una mueblería. Sabe que Instagram le trae clientes, pero entre el taller, los proveedores y las ventas no tiene tiempo de planear, escribir ni diseñar posts. Una agencia no le da el presupuesto. Pero WhatsApp lo usa todo el día."

### 0:30 – Onboarding (75 s)

1. Owner sends "Hola" → welcome → types `{BUSINESS}` → magic link arrives.
2. Opens the link: fills step 1 quickly (prefilled name), picks 3 products, uploads the logo (**colors appear automatically**, a visible "wow"), selects 8 photos, taps through the questionnaire, connects Instagram (already authorized; one tap), "Volver a WhatsApp".
3. Narrator while the Brand Brain generates: "Mientras tanto, un equipo de agentes está estudiando su marca: un analista mira cada foto, una estratega arma la identidad de la marca."
4. WhatsApp: brand summary arrives → owner reads one line aloud ("Cercanos, cálidos, artesanales… sí, somos nosotros") → `[Sí, es mi marca]`.

> Fallback: if the summary takes > 60 s, switch to the seeded business ("este es el que preparamos ayer con los mismos datos").

### 1:45 – Weekly plan (30 s)

1. `[Dale]` → plan of 3 posts arrives → narrator points out it uses their real products and promo → `[Aprobar plan]`.
2. The first post preview arrives (image + caption + buttons). Narrator: "Foto real del taller, colores y logo de la marca, texto en su tono."

### 2:15 – Change request (35 s)

1. `[Cambiar]` → owner types: "más corto y decí que hay envío gratis en Montevideo" → revised post arrives in ~20–30 s.

### 2:50 – Ad-hoc + publish (50 s)

1. Owner types: "hacé un post para la promo del finde: {PROMO}" → "¡Dale! Lo armo ⏳" → preview with the `promo_band` template.
2. `[Aprobar]` → `[Publicar ahora]` → "¡Publicado! 🎉 <link>".
3. Open the link on the projector: **the post is live on `{IG_HANDLE}`.**

### 3:40 – Close (20 s)
>
> "Cero dashboards, cero curva de aprendizaje. Una agencia de marketing que vive en el WhatsApp de cada emprendedor, y que no publica nada sin su sí. Hoy es marketing; mañana, proveedores, pedidos y seguimientos."

## What to say if asked

- **"¿Y si el agente se equivoca?"** Nothing is published without the owner's tap; approval is enforced in code, not left to the AI.
- **"¿Inventa cosas?"** The agents only use facts the owner gave; prices and promos only appear if the owner mentioned them; there are automated checks for that.
- **"¿Cómo escala?"** One team of specialized agents shared by all businesses, personalized by each business's brand profile; adding a business costs no setup.
- **"¿Modelo de negocio?"** Monthly subscription by number of posts; the data model already has plans and quotas.
