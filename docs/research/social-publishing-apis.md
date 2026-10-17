# Social publishing APIs for Instagram

Question: which API lets the backend publish image posts to a small business's Instagram (ideally its Facebook Page too) on the Owner's behalf, without going through Meta app review ourselves, on a free tier usable in a 24h hackathon?

Read on 2026-10-17 from each vendor's own docs and pricing pages (links inline). Prices and limits change, so re-check before relying on them. Outcome: [ADR 0008](../decisions/0008-publishing-via-zernio.md).

## Comparison

| | Zernio (ex-Late) | Upload-Post | Ayrshare | Outstand | Post for Me | Blotato |
|---|---|---|---|---|---|---|
| Free tier with API | Yes: first 2 connected accounts free, unlimited posts, full API, no card, 60 req/min; 3rd account → `402` ([pricing](https://docs.zernio.com/pricing)) | Yes: 10 uploads/month, 2 profiles ([pricing & limits](https://docs.upload-post.com/resources/pricing-and-limits)) | No free plan; Premium $149/mo ([pricing](https://www.ayrshare.com/pricing.md)) | No; $19/mo ([homepage](https://www.outstand.so/)) | No; $10/mo ([pricing](https://www.postforme.dev/pricing)) | 7-day trial **without** API ([pricing](https://www.blotato.com/pricing)) |
| Instagram formats | Feed image, carousel (≤ 10), story, reel; Business/Creator; Instagram Login, no Facebook Page needed ([Instagram](https://docs.zernio.com/platforms/instagram)) | Feed image, carousel, stories; Business/Creator, no Page needed ([docs](https://docs.upload-post.com/llm.txt)) | Feed, carousel, stories (Business only); docs conflict on Page requirement ([Instagram](https://www.ayrshare.com/docs/apis/post/social-networks/instagram)) | Supported, not verified | Supported, formats not verified | Not verified |
| Owner connects via a link we generate | **Yes, on free**: `GET /v1/connect/instagram?profileId=…&redirect_url=…` → `authUrl`; hosted or headless; co-branded ([connecting accounts](https://docs.zernio.com/guides/connecting-accounts)) | Only on Professional ($50/mo)+ ([docs](https://docs.upload-post.com/llm.txt)) | Launch/Business plans only ([Business plan](https://www.ayrshare.com/docs/multiple-users/business-plan-overview)) | `POST /v1/social-networks/:network/auth-url` ([llms.txt](https://www.outstand.so/docs/llms.txt)) | `POST /v1/social-accounts/auth-url` ([API docs](https://api.postforme.dev/docs)) | Not documented |
| Publish call | `POST https://zernio.com/api/v1/posts`, JSON `{content, mediaItems, platforms, publishNow \| scheduledFor+timezone}` ([create post](https://docs.zernio.com/posts/create-post)) | `POST /api/upload_photos`, multipart | `POST /api/post` `{post, platforms, mediaUrls}` ([post API](https://www.ayrshare.com/docs/apis/post/post)) | `POST /v1/posts` | `POST /v1/social-posts` (async results) | — |
| Webhooks | `post.published`, `post.failed`, `post.partial`, `account.connected`; HMAC-SHA256 in `X-Zernio-Signature` ([webhooks](https://docs.zernio.com/webhooks)) | `upload_completed`, `social_account_connected` | Exist; event names not verified ([webhooks](https://www.ayrshare.com/docs/apis/webhooks/overview)) | `post.published`, `post.error` | Exist | — |
| Python SDK | `zernio-sdk` ([Python SDK](https://docs.zernio.com/sdks/python)) | `upload-post` | `social-post-api` ([Python](https://www.ayrshare.com/docs/packages-guides/python)) | Not found | Not found | — |

## Zernio details that matter for the build

- `201` returns `post._id` and `post.platforms[].platformPostUrl`; **`207` means partial failure**, so check `post.status` ([create post](https://docs.zernio.com/posts/create-post)).
- Media must be a public HTTPS URL returning the raw file, JPEG/PNG under 8 MB, aspect ratio between 4:5 and 1.91:1; or upload via `POST /v1/media/presign` ([media uploads](https://docs.zernio.com/guides/media-uploads)).
- One Zernio profile per Business: `POST /v1/profiles {"name", "externalId"}` ([multi-tenant](https://docs.zernio.com/multi-tenant)).
- Free-tier accounts count across the whole team (Instagram + Facebook Page of one Business = both free slots); extra accounts cost $6/month each for accounts 3–10 ([pricing](https://docs.zernio.com/pricing)).
- Instagram caps: 25 posts/hour and 100/day per account ([Instagram](https://docs.zernio.com/platforms/instagram)).
- getlate.dev returns a 301 to Zernio; build only against `zernio.com/api/v1`.

## Not verified

- The exact query parameters Zernio appends to the connect redirect (log them in the first test; tracked in [open-questions.md](../open-questions.md)).
- Whether Zernio's connect screen can be fully white-labelled (docs only describe hosted co-branded and headless modes).
- Outstand and Post for Me Instagram formats and SDKs; Ayrshare webhook event names and its conflicting Facebook Page requirement.
