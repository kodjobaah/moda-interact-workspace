---
id: ARCH-049
status: proposed
working_title: ShopBrand media normalisation and WhatsApp-ready R2 derivatives
coordinator: moda_architect
prepared: 2026-10-25
note: Portable session proposal only; identifier is provisional and has not been materialised in a canonical Git branch.
---

# Proposed ARCH-049 — ShopBrand media ingestion and WhatsApp-ready derivatives

## Why this deserves a separate architecture initiative

The ARCH-047 Admin template composer now exposes eight ShopBrand variables, including merchant-controlled logo and cover-image URLs. The current `shopify.ShopBrand` Prisma model stores original `logoUrl`, `squareLogoUrl`, `coverImageUrl`, optional alt text, and optional original logo dimensions, with one row per Shop. Those fields **do not certify that a URL is publicly retrievable, a supported image format, safe to fetch, or suitable for a WhatsApp image-header message**. The current ARCH-047 Background task should not do media downloads, resizing or R2 uploads during a recovery send.

## Goal and target outcome

Create/refresh brand data once; enqueue image processing when a source asset changes; safely fetch and normalise each supported source; store a verified, immutable derivative in an approved Cloudflare R2 media bucket; expose its **READY** metadata to Admin previews and Background template preparation. A template that requires an image header must not send until a corresponding permitted READY derivative exists. Text-only templates must continue without waiting for any media processing.

## Proposed pipeline

```text
Shopify/WooCommerce brand ingestion or refresh
  -> canonical shop-scoped source metadata and fingerprint
  -> durable, deduplicated image-processing request
  -> Background worker: secure fetch / decode / resize / optimise / encode
  -> verify output bytes, MIME, width, height and digest
  -> R2 immutable object key and public HTTPS delivery URL
  -> atomic version-aware READY publication (reject stale completion)
  -> Admin image-header preview / Background read-only media resolver
  -> WhatsApp send (approved Meta image-header template only)
```

## Responsibilities to decide in the new architecture session

| Boundary | Candidate owner | Decision still required |
|---|---|---|
| Shopify brand source and refresh | `moda_app` or existing Shopify owner | Identify actual existing ShopBrand writer and event/refresh triggers; do not assume it already exists |
| WooCommerce brand source and refresh | `moda_woocommerce` through `moda_api` | Define equivalent brand-data availability without exposing merchant WordPress endpoints or credentials to Background |
| Canonical brand media metadata | `moda_database` | Decide whether to extend the existing `shopify.ShopBrand` or use a new platform-neutral metadata model; do not force Woo records into an inappropriate Shopify-owned schema without review |
| Queueing and processing | `moda_background` | Reuse current BullMQ and provider-safe worker structure; maintain retry, stale-source and idempotency semantics |
| R2 configuration and public media delivery | `moda_gateway` and approved owners | Decide media bucket/prefix, service credentials, CDN/custom domain, access/retention and deployment configuration; do not reuse private Merchant Knowledge object URLs as if public |
| Admin preview and image-header selection | `moda_admin` | Offer only READY processed assets as true `IMAGE` header bindings; differentiate them from text URL fields and original source dimensions |
| Meta submission and runtime send | ARCH-047 BG003/BG001/BG006/BG007 | Use a suitable submitted **sample media asset/handle** for Meta approval and shop-specific READY runtime image when sending; do not replace approval content or author a template outside Moda Admin |

## Proposed media contract (illustrative, not a settled database schema)

```json
{
  "shopId": "shop-example",
  "role": "LOGO",
  "sourceFingerprint": "sha256:...",
  "processingGeneration": 4,
  "status": "READY",
  "objectKey": "brand-media/shop-example/logo/<digest>.jpg",
  "publicUrl": "https://media.example.com/brand-media/shop-example/logo/<digest>.jpg",
  "mimeType": "image/jpeg",
  "width": 1125,
  "height": 600,
  "sizeBytes": 175000,
  "contentHash": "sha256:..."
}
```

The exact table/JSON shape, role enumeration, generation field, object-key policy and asset access model must be chosen in the architecture session. This example is **not** permission to create a new table or field without a reviewed contract.

## Normalisation and format design

- Initial roles: logo, square logo, cover image. Distinguish original URLs from processed output keys and from Meta submission sample assets.
- For WhatsApp image media, use JPEG or PNG with the documented 5 MB maximum. Aim for a smaller internally verified output (for example below 1 MB when practical). A roughly 1125 × 600 canvas is a **design proposal**, not a mandatory Meta maximum.
- Preserve aspect ratio: pad logos rather than stretching or destructively cropping; consider reviewed cover-image crop policy separately. Preserve transparency when needed with PNG; otherwise use suitable colour-managed JPEG.
- Validate *decoded* pixel dimensions and output bytes. Strip EXIF/metadata; reject dangerous or malformed content. Bound source response size, redirects, decompression and decoded pixel counts. Protect against SSRF, DNS rebinding and private-network fetches. Do not trust file extensions or remote content-type headers alone.
- Store immutable content-addressed R2 derivative objects and update active metadata only on successful verification. Later stale jobs must not overwrite a newer source generation. Preserve last-known-good derivative as policy permits; do not silently serve it for a newly incompatible source without a decision.
- Use HTTPS media delivery reachable by Meta; URL stability and cache TTL must cover provider fetch semantics. Never log access credentials or unnecessary image URLs.

## ARCH-047 boundary while this proposal is pending

- BG001 resolves ShopBrand text values from the matching shop and uses only **verified processed asset references** for image URL links or separately typed image-header bindings; unprocessed originals are not sendable media.
- BG003 may send an image-header template to Meta only with a valid submission sample/media handle prepared by the authorised authoring/media pipeline; it does not perform R2 normalisation.
- BG006/BG007 pass a prepared media header and approved CTA button parameters through the existing final-send path, without fetching or resizing.
- A missing READY derivative results in a typed unavailable/no-send outcome. All existing consent, STOP, service-window, credit, checkout and moderation checks remain authoritative.

## Out of scope

No CommerceAgent cart/checkout mutation; no new generic user-upload service; no external Meta-template authoring/import; no change to immutable template contents when a shop replaces its logo; no image fetch on every message send; no new public WordPress endpoint solely for Background media access.

## Architecture session decisions to settle before task creation

1. Where and how the current Shopify/WooCommerce ShopBrand data is populated, and whether the existing model is sufficiently platform-neutral.
2. Source image change detection and reliable queue handoff (transactional receipt/outbox vs accepted queue) across writers.
3. Exact processing presets, brand-image roles, URL representation, transform behaviour and source file limits.
4. R2 bucket/public URL topology, cost, lifecycle/GC policy and credentials.
5. Runtime READY contract and how BG001/ADMIN-003/ADMIN-005 recognise it without duplicate image logic.
6. Meta image-header approval sample ownership and acceptable fallback/no-send policy per shop/language.
7. Required system-test fixtures and operational metrics for ingestion failure, retries, source updates and public-media delivery.

## Working dependency plan (not canonical tasks yet)

Source discovery and schema contract → independently owned Shopify/Woo producers and Background processor → R2/Gateway delivery readiness → Admin READY asset selector / ARCH-047 BG media adapter → integrated system test. Do not create task IDs until the architecture is agreed and actual repository ownership/deployment dependencies are confirmed.

## Session handoff

Start a separate ChatGPT conversation, attach this kickoff brief with the latest code snapshot and architect TOML, and ask to design ARCH-049 before defining or executing tasks. The candidate identifier `ARCH-049` is available in the inspected 25 October snapshot but must be rechecked in the current canonical repository before materialisation. Do not modify any `docs/decisions/**/_index.md` until the architect session is explicitly complete.
