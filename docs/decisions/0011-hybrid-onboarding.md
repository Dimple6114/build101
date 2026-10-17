# 0011: Hybrid onboarding (WhatsApp + magic-link web form)

- Date: 2026-10-17
- Status: proposed

## Context

Uploading a logo and many photos, picking colors, and connecting Instagram (OAuth) are clumsy or impossible inside a WhatsApp chat.

## Decision

Onboarding starts in WhatsApp (welcome + business name), continues in a short mobile web wizard opened by a magic link, and returns to WhatsApp for the Brand Brain confirmation. After onboarding everything happens in WhatsApp.

## Consequences

- Fast, reliable data capture and a natural place for the Instagram connect.
- One context switch for the owner; the wizard must feel like part of the chat (mobile, Spanish, ≤ 5 minutes).
- The magic link is the only web credential (no accounts/passwords in the MVP).
