# Roadmap

## Phase 0: Hackathon demo (now)

One live loop for Katei: photos on WhatsApp → post on Instagram → comment/DM → sale → owner notified. See [demo-plan.md](demo-plan.md).

## Phase 1: Katei pilot (2–4 weeks)

- Run it on Katei's real account every day; log every correction the owner makes
- Brand voice learns from corrections, not only from past posts
- Designer agent: before/after layouts and carousel templates from real photos (no invented images of the product)
- Reels v1: before/after video built from the photos (with royalty-free audio; Instagram's music library isn't available through the API)
- Weekly plan sent proactively every Monday, with Uruguayan commercial dates
- Basic metrics: weekly WhatsApp summary from Instagram Insights
- **Success metric**: hours per week the owner spends on social media, before vs. after; plus DMs answered and sales closed by the bot

## Phase 2: Many businesses (2–3 months)

- Self-serve onboarding in WhatsApp: "connect your Instagram" link → official Instagram Login (OAuth). We never handle passwords
- Meta **App Review** for Advanced Access (needed once accounts outside our team connect) + Business Verification + a production WhatsApp number
- Approval levels per business: approve everything / approve only posts / fully autonomous
- Payment links in the sales flow (e.g. Mercado Pago in Uruguay)
- Billing + tiers

## Phase 3: Grow

- Facebook, TikTok, Marketplace
- Paid ads suggestions based on what performs
- Back-office operations (the original "chief of staff" idea)

## Pricing (draft)

| Tier | ~USD/month | Includes |
|---|---|---|
| Basic | 8 | Content from photos + scheduled publishing + weekly plan |
| Pro | 20 | + replies to comments and DMs, sales + owner notifications, metrics |
| Plus | TBD | + reels, more posts, multiple accounts |

To validate: WhatsApp and LLM costs per active business must fit well under the Basic price.
