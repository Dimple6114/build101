# Web app design

The web app is a **side door**. Owners spend 95% of their time in WhatsApp. The web exists for what WhatsApp can't do well: forms, uploads, OAuth. It must feel like a continuation of the chat: mobile, friendly, Spanish, one thing per screen.

## Principles

1. **Mobile first, phone only in practice.** Design at 390×844; desktop is a centered 480 px column.
2. **One question per screen** in the wizard. Big tap targets (≥ 48 px), sticky bottom primary button.
3. **Autosave** every step; returning to the link resumes where the owner left.
4. **No jargon**: "Conectá tu Instagram", not "OAuth"; "Tu marca", not "Brand Brain".
5. **Always a way back to WhatsApp** (header link on every screen).
6. **Rioplatense copy** with the same voice as the bot (see [../product/conversation-design.md](../product/conversation-design.md)).

## Stack and UI kit

- Next.js (App Router) + TypeScript, deployed on Vercel.
- Tailwind CSS + **shadcn/ui** components (Button, Input, Textarea, Select, Slider, RadioGroup, Checkbox, Card, Progress, Badge, Toast/Sonner, Skeleton).
- `lucide-react` icons. No other UI libraries.
- Data: `fetch` wrappers in `lib/api.ts` + React Server Components for initial load, client components for the wizard steps. No global state library; the wizard keeps state in the URL (`?step=`) + server.

## Visual language

| Token | Value | Use |
|---|---|---|
| `--background` | `#FAF7F2` (warm off-white) | Page |
| `--foreground` | `#1F1B16` | Text |
| `--primary` | `#1F6F5C` (deep green, WhatsApp-adjacent but not WhatsApp green) | Primary buttons, progress |
| `--primary-foreground` | `#FFFFFF` | |
| `--accent` | `#F2B84B` (warm amber) | Highlights, "listo" states |
| `--muted` | `#EFE9E0` | Cards, inputs background |
| `--muted-foreground` | `#6B6257` | Helper text |
| `--destructive` | `#C2410C` | Errors |
| `--radius` | `14px` | Cards, buttons, inputs |
| Font | Inter (UI), with `font-feature-settings: "ss01"` | |

Dark mode: not needed for the demo (owners open it from WhatsApp in daylight). Define tokens as CSS variables anyway so it can be added.

Tone of illustrations: none. Use the owner's own photos and logo as soon as they're uploaded. Seeing their brand appear is the delight moment.

## Screens

### `/o/[token]`: onboarding wizard

Header (all steps): small logo of the product · "Paso 2 de 6" · progress bar · "Volver a WhatsApp" link (wa.me).

```text
┌──────────────────────────────┐
│ ◀   Paso 1 de 6   ▓▓░░░░░░  │
│                              │
│ Contanos de tu negocio 🏪    │
│                              │
│ ¿Cómo se llama?              │
│ ┌──────────────────────────┐ │
│ │ Muebles Ramírez          │ │
│ └──────────────────────────┘ │
│ ¿De qué rubro es?            │
│ [Muebles y deco         ▾]   │
│ Contalo en una frase         │
│ ┌──────────────────────────┐ │
│ │ Muebles de madera maciza │ │
│ │ hechos a mano en Mvd     │ │
│ └──────────────────────────┘ │
│ ¿Dónde están?                │
│ [Montevideo              ]   │
│ Instagram (opcional)         │
│ [@mueblesramirez         ]   │
│                              │
│ ┌──────────────────────────┐ │
│ │       Siguiente →        │ │  ← sticky bottom
│ └──────────────────────────┘ │
└──────────────────────────────┘
```

| Step | Title | Content | Validation |
|---|---|---|---|
| 1 | Contanos de tu negocio 🏪 | name, category (Select), one-liner (Textarea, 120 chars), location, IG handle | name, category, one-liner required |
| 2 | ¿Qué es lo que más vendés? | Up to 5 product cards: name, short description, price (optional). "+ Agregar otro" | ≥ 1 product |
| 3 | Tu marca 🎨 | Logo dropzone → after upload shows the logo + **detected color swatches** (tap to edit with a color input, "+" to add); "3 palabras que usarían tus clientes para describirte" (3 inputs) | colors ≥ 1 (defaults if no logo) |
| 4 | Tus fotos 📸 | Grid uploader (camera roll multi-select). Thumbnails with ✕. Hint: "Productos, el taller, el equipo. Mientras más, mejor." Counter "5 de 15" | ≥ 3 photos |
| 5 | ¿Cómo querés que suene? | Questionnaire, one card per question (see [../product/user-flows.md](../product/user-flows.md#flow-2--web-onboarding-form)): chips for options, sliders with labels at both ends | goal, posts/week, emoji required |
| 6 | Conectá tu Instagram | Explanation (2 lines: "Lo usamos solo para publicar lo que vos apruebes"), big button "Conectar Instagram" → redirects to Zernio; on return shows ✅ @handle. Secondary: "Lo hago después" | none |
| 7 | ¡Listo! 🎉 | "Ya tenemos todo. En un minuto te escribimos por WhatsApp con lo que entendimos de tu marca." + big "Volver a WhatsApp" button | calls `/complete` on mount (idempotent) |

Upload UX: show each thumbnail immediately (object URL), upload in the background with a small spinner overlay; retry on failure; HEIC accepted (converted server-side).

Error states: expired/invalid token → friendly screen "Este link venció. Escribinos 'link' por WhatsApp y te mandamos uno nuevo." (the onboarding router handles "link").

### `/b/[token]`: dashboard (Should)

Read-only, single page, mobile:

```text
┌──────────────────────────────┐
│ [logo] Muebles Ramírez       │
│ Instagram ✅ @mueblesramirez  │
├──────────────────────────────┤
│ Esta semana                  │
│ ┌────┐ Mar 21 · Mesa Nórdica │
│ │img │ ● Programado 19:00    │
│ └────┘                       │
│ ┌────┐ Jue 23 · El taller    │
│ │img │ ● Esperando aprobación│
│ └────┘                       │
├──────────────────────────────┤
│ Tu marca                     │
│ Cercanos · cálidos · artesan.│
│ Pilares: A medida · Taller · │
│ Ideas para tu living         │
│ ■ ■ ■  (colores)             │
└──────────────────────────────┘
```

Status badges: Generando (gray), Esperando aprobación (amber), Aprobado (blue), Programado (green outline), Publicado (green, links to IG), Descartado (muted), Error (red).

### `/dev/chat`: WhatsApp simulator (Must)

Desktop layout used for development, rehearsal and as the stage fallback. It must look enough like WhatsApp that the demo still reads as "the owner is chatting".

```text
┌───────────────────────────────────────────┬─────────────────────────┐
│  ◀  Muebles Ramírez (sim-5f2a)   [Reset]  │ Debug                   │
│───────────────────────────────────────────│ state: active           │
│                     hola                ✓ │ awaiting: post_feedback │
│ ¡Hola! 👋 Soy ..., tu agencia ...         │ jobs:                   │
│                                           │  generate_post ✓ 38s    │
│ ┌───────────────┐                         │ agent_runs (latest 10)  │
│ │   [image]     │                         │  copywriter 6.1s 2.3k   │
│ │ 📝 Post para..│                         │  art_director 9.8s 4.1k │
│ │ [Aprobar]     │                         │  ...                    │
│ │ [Cambiar]     │                         │                         │
│ │ [Descartar]   │                         │                         │
│ └───────────────┘                         │                         │
│───────────────────────────────────────────│                         │
│ [📎] [ Escribí un mensaje...      ] [➤]   │                         │
└───────────────────────────────────────────┴─────────────────────────┘
```

- Bubbles: outbound (bot) left/white, inbound (owner) right/green `#D9FDD3`, background `#EFEAE2`, like WhatsApp.
- Interactive messages render buttons under the bubble; clicking sends a `button_reply`.
- 📎 lets you send an image (upload → URL → `{type: "image", url}`).
- Polls `GET /dev/sim/{phone}/messages?after=` every 1 s.
- Right panel (toggleable, hidden during demo): business state, recent jobs, recent agent runs with latency/tokens; click a run to see input/output JSON.
- Query param `?phone=` reuses an existing simulator business; "Reset" creates a fresh one.

## Accessibility and quality bar

- All inputs have labels; color is never the only status signal (badges have text).
- Contrast ≥ 4.5:1 for text (tokens above meet it on `--background`).
- Works on iOS Safari and Android Chrome (the in-app browser that WhatsApp opens links in).
