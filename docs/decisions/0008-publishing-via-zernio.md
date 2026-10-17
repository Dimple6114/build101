# 0008: Publish through Zernio (unified publishing API)

- Date: 2026-10-17
- Status: accepted

## Context

Publishing to Instagram directly requires a Meta app with `instagram_content_publish` approved through app review, which isn't feasible in a hackathon for a real owner's account. We compared Zernio (ex-Late), Upload-Post, Ayrshare, Outstand, Post for Me and Blotato: [research/social-publishing-apis.md](../research/social-publishing-apis.md).

## Decision

Use **Zernio**: its free tier includes full API access (first 2 connected accounts free, unlimited posts), a hosted connect link we generate per business, publish-now and scheduling in one endpoint, signed webhooks. Behind a `PublisherPort` with a `MockPublisher` fallback.

## Consequences

- No app review, fast integration, scheduling for free.
- Free tier = 2 connected accounts across the whole team: connect only the demo IG account.
- Vendor dependency and per-account pricing after 2 accounts; the port keeps a switch to Meta's API (or another provider) cheap.
- The connect screen is co-branded, not white-label.
