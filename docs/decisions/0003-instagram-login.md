# 0003: Connect Instagram through Instagram Login

- Date: 2026-10-17
- Status: accepted

## Context

The bot must publish, read comments and answer DMs on the owner's account, securely.

## Decision

Use Meta's Instagram API with Instagram Login (OAuth). The owner authorizes our app; we store a revocable token, never a password. Requires a Business or Creator account.

## Consequences

- Demo/pilot: dev mode with the account added as a tester, no App Review.
- Serving other businesses requires App Review for Advanced Access (estimated at weeks, not days).
