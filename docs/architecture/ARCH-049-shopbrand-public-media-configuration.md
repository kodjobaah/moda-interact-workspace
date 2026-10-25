---
id: ARCH-049
title: ShopBrand public-media configuration and WhatsApp-ready media normalisation
status: proposed
coordinator: moda_architect
created: 2026-10-25
updated: 2026-10-25
---

# ARCH-049 — ShopBrand public media and image normalisation

## Status and source of truth

**Proposed expansion of the existing ARCH-049 initiative.** The Admin configuration decision (`shopBrand.publicMedia`) was previously agreed; task `ARCH-049-ADMIN-001` is `review` in the uploaded 2026-10-25 15:13 snapshot and is **not** reset, edited or implicitly accepted here. The additional media-processing tasks below are **defined but not materialised**: no task branches, implementation or deployment changes have been made.

This document supersedes the configuration-only scope of the prior parent ARCH-049 document when this expanded architecture is explicitly accepted. The historical `ARCH-049-ShopBrand-Media-Architecture-Session-Kickoff.md` remains an unmodified proposal/handoff, not a second canonical parent plan. The `docs/decisions/**/_index.md` files are intentionally unchanged pending explicit session completion.

## Existing, confirmed baseline

- `shopify.ShopBrand` is an existing one-row-per-Shop model with `shopId @unique`, `brandName`, original `logoUrl`, `squareLogoUrl`, `coverImageUrl`, logo alt text and dimensions. `Shop.brand` already references it. Existing Admin merchant-support raw SQL reads `shopify."ShopBrand"`.
- The current code snapshot did not contain an application writer for ShopBrand source metadata. Do not assume Shopify or Woo initial synchronisation already exists.
- `ARCH-049-ADMIN-001` supplies read/default/save of `shopBrand.publicMedia` through the existing platform configuration with defaults `publicOrigin=https://shop-brands.modainteract.com` and `bucketName=moda-interact-shop-brands`; its implementation requires separate review/acceptance.
- The user has already created the Cloudflare R2 bucket and attached the public custom domain. Its screenshot showed the custom domain **Initializing** and minimum TLS **1.0**; neither active HTTPS delivery nor R2 **write** credentials are proven by that screenshot. Do not repeat provisioning.
- The current Shopify app scope string in `moda-interact/shopify.app.toml` does not include `read_brand`. The Admin GraphQL brand resource requires that scope; a minimal Shopify authorisation task is retained, while Shopify brand synchronisation lives in Background.
- Existing Background `merchant-knowledge-network-policy.ts` implements guarded external acquisition and existing private Merchant Knowledge R2 services provide reusable S3 client patterns. Private Merchant Knowledge objects/settings must never become public brand media.

## Problem

The merchant's original logo or cover URL might be SVG/WebP, unreachably hosted, oversized or unsafe to fetch. A source `ShopBrand` URL is **not** a WhatsApp-ready image. Downloads/transforms at message-send time would introduce latency, provider risk and repeated costs. Shopify and WooCommerce need the **same shop-scoped** persisted branding record.

## Goals

- Retain exactly **one ShopBrand row per Shop** and move the existing table from the `shopify` PostgreSQL schema to `commerce`, retaining its identity and all original fields/data. Add exactly one `whatsAppMedia Json @default("{}") @db.JsonB` column; **do not create `ShopBrandMediaAsset` or another ARCH-049 table**.
- Ingest brand source metadata from the authenticated Shopify Admin API via Background and from WordPress-native Site Identity via WooCommerce plugin → authenticated Moda API.
- Normalise each role asynchronously once per change/revalidation into verified JPEG/PNG, with explicit source generations, retries and stale-result rejection.
- Write immutable, content-addressed image derivatives to the user's pre-existing R2 bucket. Expose them only at the configured HTTPS custom domain once proven operational.
- Make `LOGO`, `SQUARE_LOGO`, `COVER_IMAGE` READY metadata available to ARCH-047 Admin image-header selection and Background read-only runtime binding, with no per-send downloads, resizing or arbitrary-source fallback.
- Reuse existing services and keep every module and implementation task bounded and independently testable.

## Non-goals

- Re-provisioning R2, a new Gateway/Render service, new public image proxy, new ShopBrandMediaAsset table, generic merchant uploads, a new Shared package solely for media metadata, AI cart/checkout mutations, Meta template authoring outside Admin, or changing private Merchant Knowledge asset exposure.
- Downloading images from customer messages, fetching merchant WordPress servers directly from Background, performing R2 network operations inside PostgreSQL transactions, or inferring image readiness from a logo URL or source width/height.

## Data model and relationships

```text
commerce.Shop (existing)
   1 ───── 0..1 commerce.ShopBrand (existing id/shopId preserved; moved from shopify)
                      ├── brandName / logoUrl / squareLogoUrl / coverImageUrl (original fields)
                      └── whatsAppMedia JSONB version 1
                            ├── roles.LOGO
                            ├── roles.SQUARE_LOGO
                            └── roles.COVER_IMAGE
                                   source  -> work  -> ready (verified R2 reference)
```

Keep the existing `Shop.brand` and `ShopBrand.shop` Prisma relations and delete behaviour. Move with `ALTER TABLE "shopify"."ShopBrand" SET SCHEMA "commerce"`, add JSONB default, and regenerate Prisma clients in consumers when integrated. Maintain source URLs exactly as source metadata; never overwrite them with the R2 URL. Raw SQL references to `shopify."ShopBrand"` must be updated in the owning Admin consumer before deploying the migration to a running Admin service.

### Exact JSONB persistence contract (application-owned, no DB business checks)

A role may be absent until its first observation. `whatsAppMedia = {"schemaVersion":1,"roles":{...}}` once initialised. Example:

```json
{
  "schemaVersion": 1,
  "roles": {
    "LOGO": {
      "source": {
        "url": "https://merchant.example/logo.png",
        "reference": "shopify:brand-logo-123",
        "fingerprint": "sha256:0123456789abcdef",
        "generation": 2,
        "observedAt": "2026-10-25T12:00:00Z"
      },
      "work": {
        "status": "READY",
        "attempts": 1,
        "retryAfter": null,
        "leaseOwner": null,
        "leaseUntil": null,
        "failureCode": null,
        "lastCheckedAt": "2026-10-25T12:05:00Z"
      },
      "ready": {
        "sourceGeneration": 2,
        "sourceFingerprint": "sha256:0123456789abcdef",
        "objectKey": "shop-brands/shop123/logo/sha256-abcdef.jpg",
        "contentType": "image/jpeg",
        "width": 1125,
        "height": 600,
        "sizeBytes": 185500,
        "contentSha256": "abcdef0123456789",
        "verifiedAt": "2026-10-25T12:05:00Z"
      }
    }
  }
}
```

**Illustrative digests above are deliberately shortened**; real fingerprints/digests must be complete lowercase 64-hex SHA-256 with a `sha256:` prefix only where the field documents it. `status` values are `MISSING`, `PENDING`, `PROCESSING`, `READY`, `FAILED`. Dates are UTC ISO-8601; nullable work fields are present as `null`. `ready` is nullable (or absent) until success and can retain the previous generation for audit, but a resolver must never use a stale ready value.

**READY for delivery** means: role has a non-null effective source URL, work.status=`READY`, `ready.sourceGeneration === source.generation`, `ready.sourceFingerprint === source.fingerprint`, verified output is valid JPEG/PNG below 5 MiB, and the resolved HTTPS URL uses the active configured public origin and immutable key. The **application layer** validates these conditions; PostgreSQL enforces only primary key, foreign key, Shop uniqueness, JSONB storage type and existing structural integrity.

### Source update and concurrency contract

All producers use the same per-role algorithm: in a short transaction, lock the `ShopBrand` row (`SELECT ... FOR UPDATE` or equivalent serialisable/CAS method), read the current role, compare the canonical source `url/reference/fingerprint`, and if changed increment `source.generation` by 1, set `work.status=PENDING` (or `MISSING` if source removed), clear lease/retry/failure for that role, and persist **only that role's new JSON** without clobbering other roles. Keep any old `ready` only as historical metadata: its generation mismatch makes it ineligible. First brand observation creates the row idempotently by unique `shopId`. If unchanged, record an observation timestamp without resetting generations or churning images.

Each worker claim is time-bounded. Only the worker holding the current lease and the current `(shopId, role, generation, fingerprint)` may publish READY. Lost/stale workers cannot overwrite a newer source. An R2 write occurs **outside** the database transaction; the worker then conditionally commits ready metadata. Identical content hashes reuse the same immutable R2 key. No partial role JSON lost updates, even when LOGO and COVER_IMAGE are processed concurrently. Application tests must cover these invariants; no DB trigger enforces them.

For `SQUARE_LOGO`, use `squareLogoUrl` when available; if absent, an explicitly documented fallback may use `logoUrl` as the source to produce a square padded derivative, without inventing an upstream square logo. Source removal makes that role MISSING unless its fallback remains available.

## Runtime and ownership

```text
Shopify: (SH-001 app grant for read_brand) → BG003 brand sync → commerce.ShopBrand
WooCommerce: plugin reads WP Site Identity → authenticated API001 writes commerce.ShopBrand
commerce.ShopBrand source generations → BG002 due-row reconciliation/claim
BG002 → BG001 safe fetch/resize/verify/put immutable R2 object
BG002 → ShopBrand.whatsAppMedia READY (atomic version check)
ARCH-049-ADMIN-002 reads READY metadata for ARCH-047 image-header role selection
ARCH-047-BG001 reads same READY metadata for final pre-send binding
ARCH-047-BG003 supplies separately prepared Meta sample-media during template creation
```

**Responsibility boundaries:** Database only schema/migration; Shopify app only read_brand permission and reauthorisation; Background synchronises Shopify sources, processes images and owns due-state reconciliation; API authenticates and persists Woo brand metadata; Woo plugin reads local WP settings and posts changes; Admin displays processed READY images. None sends checkout messages or edits Meta templates under ARCH-049.

## Processing limits and security policy

- HTTPS source only; resolve DNS at every redirect and pin public destination addresses; block loopback/private/link-local/metadata IPv4/IPv6, redirects back to private networks, unusual ports, credentials in URLs, oversized URLs and DNS rebinding. Reuse the existing Background merchant-knowledge guarded fetch primitives where technically compatible.
- Proposed initial bounds for implementation: max 3 redirects, 10 s end-to-end fetch timeout, 10 MiB compressed source, 40 megapixels decoded, output JPEG/PNG (RGB/RGBA, stripped EXIF), **under 5 MiB** output, target under 1 MiB when possible. Do not trust extension or declared MIME. Limits are explicit ARCH-049 policy choices for review; not claimed as Meta's own pixel/dimension maxima.
- Deterministic internal preset: 1125 × 600 pixel canvas for WhatsApp media headers; fit/pad logos without distortion, cover may centre-crop to fill with preview; preserve transparency using PNG when necessary. `logoWidth` and `logoHeight` are source display fields and do not override output dimensions. Keep original images out of publicly readable R2 objects.
- Use `shop-brands/<shopId>/<role-lowercase>/sha256-<full-digest>.<jpg|png>` keys. Include immutable caching headers. S3-compatible uploads use bucket name from validated `shopBrand.publicMedia` and **worker-only** `SHOPBRAND_R2_ENDPOINT`, `SHOPBRAND_R2_ACCESS_KEY_ID`, `SHOPBRAND_R2_SECRET_ACCESS_KEY` (proposed exact environment variable names). Never expose these secrets to Admin, Shopify, WooCommerce, customer content, generated links or logs.
- The user's R2 bucket and custom domain already exist; verify domain is Active, public image fetch is 200 with correct image content-type over HTTPS, and minimum TLS is at least 1.2. Disable the public `r2.dev` URL when no longer required for development. These are **preflight/operational checks**, not a new Gateway provisioning task. If modifying the canonical Render Blueprint is demonstrably required, request a narrowly scoped Gateway amendment; do not silently edit Gateway files from Background.
- Refresh schedule (proposed defaults): source sync for active Shopify shops at most once per 24 hours; BG002 due-row sweep every 5 minutes; media content recheck every 7 days for READY records so changed bytes behind an unchanged URL are detected. Recheck must keep previously valid current-generation READY media available during a transient fetch failure, but must replace it atomically on verified new bytes. Trigger source updates promptly when receiving authenticated Woo changes. Rate-limit by tenant/provider and bound retries (suggested exponential delays 1m/5m/30m/2h/24h, max 5 attempts per generation) with an explicit operator retry path.
- Retain prior R2 versions for at least 30 days and longer while referenced by in-flight messages; a GC implementation is outside initial task scope unless an existing safe lifecycle mechanism can guarantee these conditions. No deletes on original-source refresh.

## Failure, idempotency and observability

- The durable acceptance point for ingestion is the PostgreSQL commit of source state and PENDING generation. An optional BullMQ wake may be published afterward; failure to publish a wake does not lose work because BG002 scans due rows. Do not make both Redis and PostgreSQL commit prerequisites for an API ACK.
- `BG002` must reclaim expired `PROCESSING` leases, requeue retryable failures after `retryAfter`, stop automatic retries for permanent validation failures after the bounded budget and expose redacted failure codes. One failed role/shop must not block others.
- `BG003` handles Shopify missing scopes, provider throttling and grant changes per shop; it does not reauth outside its ownership. `API001` fails closed on invalid/unauthorised payloads without corrupting existing brand rows. Woo plugin retries only transient publish failures with bounded Action Scheduler retries, not synchronous storefront blocking.
- Emit structured source/role/generation identifiers, attempts/duration, image MIME/size/hash and failure categories through existing shared logger; omit tokens, full untrusted URLs and customer information. Use existing framework/BullMQ metrics where equivalent; do not create duplicate generic metrics.

## Deployment and migration

Development/architecture expansion is pre-production for this feature, but existing ShopBrand and merchant-support records must be preserved. Recommended order: accept DB001 and migrate together with Admin raw-SQL consumer update; accept ADMIN001 configuration; verify Cloudflare domain + worker credentials; deploy BG001/BG002; enable BG003 Shopify reads after the read_brand scope is granted; enable API/Woo ingress; enable Admin READY previews and ARCH-047 image-header sends only after verified integration. Ensure rollback returns table mapping and affected consumer queries coherently; do not strand live Admin queries using the old schema path.

There is **no active GATEWAY-001** and no separate `ShopBrandMediaAsset` table. `ARCH-049-SHOPIFY-001` exists only for the confirmed missing `read_brand` authorisation, **not** for brand-data synchronisation.

## Tasks and dependencies

| Task | Owner | State in snapshot / proposal | Depends on |
|---|---|---|---|
| ARCH-049-ADMIN-001 | moda_admin | Review (existing; unchanged) | — |
| ARCH-049-DATABASE-001 | moda_database | Pending (proposed) | — |
| ARCH-049-SHOPIFY-001 | moda_app | Pending (proposed scope-only) | — |
| ARCH-049-BACKGROUND-001 | moda_background | Pending (proposed) | DATABASE-001, ADMIN-001 |
| ARCH-049-BACKGROUND-002 | moda_background | Pending (proposed) | DATABASE-001, BACKGROUND-001 |
| ARCH-049-BACKGROUND-003 | moda_background | Pending (proposed) | DATABASE-001, BACKGROUND-002, SHOPIFY-001 |
| ARCH-049-API-001 | moda_api | Pending (proposed) | DATABASE-001 |
| ARCH-049-WOOCOMMERCE-001 | moda_woocommerce | Pending (proposed) | API-001 |
| ARCH-049-ADMIN-002 | moda_admin | Pending (proposed) | DATABASE-001, ADMIN-001, ARCH-047-ADMIN-003 |
| ARCH-049-SYSTEM-TEST-001 | moda_system_test | Pending (proposed) | All required ARCH-049 implementations, ARCH-047 image send integrations |

Cross-architecture prerequisites use fully qualified task IDs in the individual task definitions. No implementation task depends on the terminal System Test. Independently gated tasks may execute in parallel. `enables` declarations in the new task files reflect the exact current graph and do not automatically start work.

## Open questions / decisions before acceptance

No unknown database tables are needed; the 3 fixed media roles and JSONB row-level versioned writes are the chosen initial design. Before starting a task, verify the canonical task worktree, current implementation repository pins and branch state. If a provider's live API shape or OAuth scope differs materially from the cited Shopify docs, report that as a scoped blocker to moda_architect instead of silently changing ownership or inventing unauthorised access.

## Change history

- 2026-10-25: Agreed Admin platform configuration for the R2 public origin and bucket name (preserved as the existing ADMIN-001 task).
- 2026-10-25: Proposed consolidated media-normalisation expansion: move ShopBrand into commerce; one JSONB processed-media field; Background-owned Shopify synchronisation; Woo plugin/API ingress; reuse already-created R2 custom domain; no Gateway provisioning implementation.
