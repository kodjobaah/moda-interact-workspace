---
id: ARCH-049
title: ShopBrand public-media configuration and WhatsApp-ready media normalisation
status: agreed
coordinator: moda_architect
created: 2026-10-25
updated: 2026-10-28
---

# ARCH-049 — ShopBrand public media and image normalisation

## Status and source of truth

**Agreed ShopBrand-media direction; implementation remains pending.** The accepted `ARCH-049-ADMIN-001` provides `shopBrand.publicMedia`. In the 26 October 13:43 snapshot, ARCH-047 Admin authoring/compilation, Meta management and automated recovery integration are Complete. `ARCH-047-BACKGROUND-007` is still Ready and is not required for **ARCH-049 automated image-header** certification. The role-aware runtime resolver and Admin IMAGE-header compiler are not implemented yet; these gaps are explicitly owned by ARCH-049-ADMIN-002 and new ARCH-049-BACKGROUND-004. Acceptance of configuration or ARCH-047 text-template modules does not imply image-header integration is complete.

This document supersedes the configuration-only scope of the earlier ARCH-049 plan; it is now the canonical agreed architectural direction. The historical `ARCH-049-ShopBrand-Media-Architecture-Session-Kickoff.md` remains an unmodified proposal/handoff, not a second canonical parent plan. The Admin-domain index reflects the accepted ADMIN-001 review; other domain indexes remain unchanged.

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
- Make `LOGO`, `SQUARE_LOGO`, `COVER_IMAGE` READY metadata available to ARCH-047 Admin image-header selection and Background read-only runtime binding **through ARCH-049-BACKGROUND-004**, with no per-send downloads, resizing or arbitrary-source fallback. Admin must extend its existing TEXT-only authoring/compiler to produce the corresponding frozen IMAGE-header role binding; no duplicate AST compiler.
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
        "objectKey": "shop-brands/store.example.com/logo/sha256-abcdef.jpg",
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
WooCommerce: plugin initial connection / future explicit Sync branding → read WP Site Identity → authenticated API001 writes commerce.ShopBrand
commerce.ShopBrand source generations → BG002 due-row reconciliation/claim
BG002 → BG001 safe fetch/resize/verify/put immutable R2 object
BG002 → ShopBrand.whatsAppMedia READY (atomic version check)
ARCH-049-ADMIN-002 reads READY metadata for ARCH-047 image-header role selection
ARCH-049-BG004 adapts READY metadata to ARCH-047-BG001 media bindings and automated final-send composition
ARCH-047-BG003 accepts a valid Meta image-header sample handle during template creation; its existing implementation does not obtain that handle itself
```

**Responsibility boundaries:** Database only schema/migration; Shopify app only read_brand permission and reauthorisation; Background synchronises Shopify sources, processes images and owns due-state reconciliation; API authenticates and persists Woo brand metadata; Woo plugin sends an initial authenticated Site Identity snapshot and exposes an internal explicit re-sync method (no automatic WordPress brand-change hooks or daily Woo reconciliation); Admin displays processed READY images. None sends checkout messages or edits Meta templates under ARCH-049.

## Processing limits and security policy

- HTTPS source only; resolve DNS at every redirect and pin public destination addresses; block loopback/private/link-local/metadata IPv4/IPv6, redirects back to private networks, unusual ports, credentials in URLs, oversized URLs and DNS rebinding. Reuse the existing Background merchant-knowledge guarded fetch primitives where technically compatible.
- Proposed initial bounds for implementation: max 3 redirects, 10 s end-to-end fetch timeout, 10 MiB compressed source, 40 megapixels decoded, output JPEG/PNG (RGB/RGBA, stripped EXIF), **under 5 MiB** output, target under 1 MiB when possible. Do not trust extension or declared MIME. Limits are explicit ARCH-049 policy choices for review; not claimed as Meta's own pixel/dimension maxima.
- Deterministic internal preset: 1125 × 600 pixel canvas for WhatsApp media headers; fit/pad logos without distortion, cover may centre-crop to fill with preview; preserve transparency using PNG when necessary. `logoWidth` and `logoHeight` are source display fields and do not override output dimensions. Keep original images out of publicly readable R2 objects.
- Use `shop-brands/<normalized-Shop.domain>/<role-lowercase>/sha256-<full-digest>.<jpg|png>` keys. If the current raw `Shop.domain` is an absolute URL, use only its parsed `hostname` (lowercase as provided by `URL.hostname`); otherwise preserve a safe bare host-like value verbatim, including a single label. For example, `https://example.com` and `example.com` both map to `example.com`, while `example` maps to `example`. The resulting segment is restricted to ASCII letters, digits, dots, underscores and hyphens, excludes exact `.` and `..`, and is at most 253 characters. Reject unsafe bare values rather than encoding them; URL credentials, paths, queries and fragments never enter the key. Background retains the raw source `Shop.domain` in each claim and compares it with the current database value at completion, while both Background and Admin apply this same normalized segment for key generation/readiness. Include immutable caching headers. S3-compatible uploads use the target bucket from validated `shopBrand.publicMedia`; the processor never uses `merchant.knowledge.r2.bucket` or private Merchant Knowledge objects. For the explicitly authorized local-main feature test, the R2 endpoint and credentials are read from the validated `merchant.knowledge.r2` purpose. This cross-purpose credential reuse is a local-test configuration choice, not approval for production; production must use dedicated bucket-scoped ShopBrand credentials before enablement. Never expose credentials to Admin, Shopify, WooCommerce, customer content, generated links or logs. Legacy shopId- and base64url-keyed READY records are not delivery-eligible; Background replaces their key only after successful verification, while Admin projects them as stale until then.
- The user's R2 bucket and custom domain already exist; verify domain is Active, public image fetch is 200 with correct image content-type over HTTPS, and minimum TLS is at least 1.2. Disable the public `r2.dev` URL when no longer required for development. These are **preflight/operational checks**, not a new Gateway provisioning task. If modifying the canonical Render Blueprint is demonstrably required, request a narrowly scoped Gateway amendment; do not silently edit Gateway files from Background.
- Refresh schedule (agreed initial defaults subject to runtime validation): source sync for active Shopify shops at most once per 24 hours; BG002 due-row sweep every 5 minutes; media content recheck every 7 days for READY records so changed bytes behind an unchanged URL are detected. Recheck must keep previously valid current-generation READY media available during a transient fetch failure, but must replace it atomically on verified new bytes. Process authenticated Woo source snapshots promptly when sent; the Woo plugin publishes once on first connection/upgrade and later only on an explicit merchant-initiated sync (future UI). This restriction does **not** remove BG002 due-row/media reconciliation or Shopify source refresh. Rate-limit by tenant/provider and bound retries (suggested exponential delays 1m/5m/30m/2h/24h, max 5 attempts per generation) with an explicit operator retry path.
- Retain prior R2 versions for at least 30 days and longer while referenced by in-flight messages; a GC implementation is outside initial task scope unless an existing safe lifecycle mechanism can guarantee these conditions. No deletes on original-source refresh.

## Failure, idempotency and observability

- The durable acceptance point for ingestion is the PostgreSQL commit of source state and PENDING generation. An optional BullMQ wake may be published afterward; failure to publish a wake does not lose work because BG002 scans due rows. Do not make both Redis and PostgreSQL commit prerequisites for an API ACK.
- `BG002` must reclaim expired `PROCESSING` leases, requeue retryable failures after `retryAfter`, stop automatic retries for permanent validation failures after the bounded budget and expose redacted failure codes. One failed role/shop must not block others.
- `BG003` handles Shopify missing scopes, provider throttling and grant changes per shop; it does not reauth outside its ownership. `API001` fails closed on invalid/unauthorised payloads without corrupting existing brand rows. Woo plugin retries only transient publish failures with bounded Action Scheduler retries, not synchronous storefront blocking.
- **WooCommerce PHP logging boundary (architect decision, 2026-10-27):** the Node-only `@modainteract/moda-interact-shared/logging` export cannot run inside merchant-hosted PHP. For the ShopBrand publisher, approve the existing WooCommerce `wc_get_logger()` as the platform-native sink, with the current bounded reason-code context (`source`, `reason`, optional numeric `http_status` and `attempt`) and redacted `error_log` fallback. No raw URLs, payloads, credentials or exception messages; logger failures must not affect publication. This is a scoped runtime exception, not approval to create a service-local generic logger or weaken shared logging in Node services.
- Emit structured source/role/generation identifiers, attempts/duration, image MIME/size/hash and failure categories through existing shared logger; omit tokens, full untrusted URLs and customer information. Use existing framework/BullMQ metrics where equivalent; do not create duplicate generic metrics.

## Deployment and migration

Development/architecture expansion is pre-production for this feature, but existing ShopBrand and merchant-support records must be preserved. Recommended order: implement DB001 and coordinate migration with the Admin merchant-support raw-SQL consumer; reuse accepted ADMIN001 configuration; verify Cloudflare domain + worker credentials; implement the independent BG001 media processor, then BG002 orchestration. Shopify grant task can proceed independently while BG003 awaits accepted BG002 source-updater API. Woo plugin may be developed against the frozen API001 fixture before the hosted endpoint is accepted; activate its publishing only after API001 exists. Admin002 and BG004 can implement in parallel from their fixed IMAGE binding fixture after DB001; permit image-header sends only after the role-aware integration, compliant Meta sample handle and provider approval are demonstrated. Ensure rollback returns table mapping and affected consumer queries coherently; do not strand live Admin queries using the old schema path.

There is **no active GATEWAY-001** and no separate `ShopBrandMediaAsset` table. `ARCH-049-SHOPIFY-001` exists only for the confirmed missing `read_brand` authorisation, **not** for brand-data synchronisation.

## WooCommerce merchant-initiated Store branding sync (ARCH-049-WOOCOMMERCE-002)

Once the one-time plugin connection/upgrade capture is in place, **no WooCommerce daily brand reconciliation or automatic WordPress branding-change publication** is performed. A merchant can update their WordPress Site Name, Site Logo or Site Icon and then explicitly choose **Sync branding** within Moda Interact → Recovery Settings. The new WooCommerce-owned task adds a capability/nonce-protected WordPress REST GET status + POST enqueue command and a connected merchant UI; both reuse the existing `ShopBrand\Publisher::requestSync()` and bounded Action Scheduler delivery. No new Moda hosted API, cross-service payload, schema or public unauthenticated WordPress endpoint is required.

The panel distinguishes *queued*, *retrying*, *failed* and *accepted by hosted Moda API* rather than calling a queued job “synchronised”. A last-accepted timestamp is persisted per installation only after a validated `updated|unchanged` API acknowledgement, never from the one-time bootstrap marker. That timestamp does **not** assert that Background R2 media has reached READY or Meta approved an image template. A failed new request retains any prior successful time, and reconnecting invalidates stale installation status. Clicks coalesce safely without losing changes requested during an in-flight capture. The terminal ARCH-049 system test additionally covers this explicit merchant path. Shopify synchronisation and Background source/media recheck schedules are unaffected.

## Tasks and dependencies

Task YAML is authoritative. `ready` is eligibility of a portable definition, **not** a claim that a task branch or implementation has been materialised. Cross-architecture dependencies below are shown explicitly when they govern source integration; completed ARCH-047 modules are **already satisfied** in the snapshot.

| Task | Owner | State in snapshot/revised plan | Required dependencies |
|---|---|---|---|
| ARCH-049-ADMIN-001 | moda_admin | Complete (architect-accepted) | — |
| ARCH-049-DATABASE-001 | moda_database | Ready (new, not materialised) | — |
| ARCH-049-SHOPIFY-001 | moda_app | Ready (new, not materialised) | — |
| ARCH-049-BACKGROUND-001 | moda_background | Ready (processor-only) | ARCH-049-ADMIN-001 (Complete) |
| ARCH-049-BACKGROUND-002 | moda_background | Pending | ARCH-049-DATABASE-001, ARCH-049-BACKGROUND-001 |
| ARCH-049-BACKGROUND-003 | moda_background | Pending | ARCH-049-DATABASE-001, ARCH-049-BACKGROUND-002, ARCH-049-SHOPIFY-001 |
| ARCH-049-API-001 | moda_api | Pending | ARCH-049-DATABASE-001 |
| ARCH-049-WOOCOMMERCE-001 | moda_woocommerce | In progress (Attempt 1, developer in supplied snapshot) | — |
| ARCH-049-WOOCOMMERCE-002 | moda_woocommerce | Pending (new, not materialised) | ARCH-049-WOOCOMMERCE-001 |
| ARCH-049-ADMIN-002 | moda_admin | Pending | ARCH-049-DATABASE-001, ARCH-049-ADMIN-001, ARCH-047-ADMIN-003, ARCH-047-ADMIN-005 (all prior Admin prerequisites Complete) |
| ARCH-049-BACKGROUND-004 | moda_background | Pending | ARCH-049-DATABASE-001, ARCH-049-ADMIN-001, ARCH-047-BACKGROUND-001, ARCH-047-BACKGROUND-006 (prior prerequisites Complete) |
| ARCH-049-SYSTEM-TEST-001 | moda_system_test | Pending | All ARCH-049 implementations above plus accepted ARCH-047 Admin/compiler, BG001/BG003/BG006; **not** ARCH-047-BACKGROUND-007 |

**Why these edges:** BG001 does not read ShopBrand and therefore needs only the already-accepted public-media settings, not DB001. BG002 owns the versioned source-write helper and depends on DB001 + BG001. BG003 imports that helper, so BG002 is a real module dependency. Woo is a producer of the frozen `woo.shop-brand.v1` API contract and can be built against an independent fixture; production publishing and the terminal System Test still require API001. Admin002 and BG004 each own their half of a published JSON binding contract and can be developed independently with fixed fixtures after DB001.

**Media-provider completion boundary:** the completed ARCH-047 Admin compiler currently builds TEXT headers, and the completed Meta BG003 module rejects IMAGE headers without `example.header_handle`. Admin002 must extend the former using the existing compiler, while the Meta sample-handle acquisition path must be verified before declaring provider IMAGE-template creation usable. If there is no trusted producer of that handle, the architect must define a bounded owning correction rather than silently counting the feature as Complete. BG004 consumes only verified READY R2 asset metadata; it cannot manufacture sample handles. A missing Meta sample is not a reason to weaken runtime media eligibility or create a competing image processor.

Cross-architecture prerequisites use fully qualified task IDs in the individual task definitions. No implementation task depends on the terminal System Test. Independently gated tasks may execute in parallel. `enables` declarations in the new task files reflect the exact current graph and do not automatically start work.

## Open questions / decisions before acceptance

No unknown database tables are needed; the 3 fixed media roles and JSONB row-level versioned writes are the chosen initial design. Before starting a task, verify the canonical task worktree, current implementation repository pins and branch state. If a provider's live API shape or OAuth scope differs materially from the cited Shopify docs, report that as a scoped blocker to moda_architect instead of silently changing ownership or inventing unauthorised access.

## Change history

- 2026-10-25: Agreed Admin platform configuration for the R2 public origin and bucket name (preserved as the existing ADMIN-001 task).
- 2026-10-25: Architect-reviewed and accepted ARCH-049-ADMIN-001; downstream tasks remain gated by their other dependencies.
- 2026-10-25: Proposed consolidated media-normalisation expansion: move ShopBrand into commerce; one JSONB processed-media field; Background-owned Shopify synchronisation; Woo plugin/API ingress; reuse already-created R2 custom domain; no Gateway provisioning implementation.
- 2026-10-26: Reconciled completed ARCH-047 task statuses, removed unnecessary DB001 dependency from pure BG001 processing and unnecessary API001 dependency from Woo producer development, preserved true BG002→BG003 module reuse, added BG004 for missing role-aware READY-media adapter, clarified IMAGE-header compiler/sample boundaries, and removed unrelated ARCH-047 merchant post-window BG007 from ARCH-049 system certification prerequisites.
- 2026-10-27: Revised Woo source initiation: once on first authenticated plugin connection (or one initial capture for existing connected installations), no automatic WordPress change hooks and no daily Woo reconciliation. Preserve bounded delivery retries, clean up legacy schedules and prepare an internal method for a future merchant-triggered Sync branding UI. Background media rechecks and Shopify refresh remain unchanged.
- 2026-10-27: Pre-production scope clarification: ShopBrand reconciliation was never deployed on merchant installations, so there are no legacy recurring Action Scheduler jobs to migrate. Remove cleanup code and tests rather than introducing migration markers or steady-state scheduler lookups. Explicitly approved WooCommerce's bounded native PHP logger for ShopBrand as an exception to the Node-only shared logging entrypoint; redaction and failure isolation remain mandatory.
- 2026-10-28: For local feature testing on the explicitly authorized shared `main` checkout, ARCH-049-BACKGROUND-001 reads the R2 endpoint/credentials from validated `merchant.knowledge.r2` while continuing to use `shopBrand.publicMedia` for the public origin and write bucket. This is not a production credential-isolation decision; dedicated bucket-scoped credentials remain a production prerequisite.
- 2026-10-28: Use the current `Shop.domain`, not internal `shopId`, as the readable ShopBrand R2 path identity. Absolute URLs normalize to `URL.hostname`; safe bare values are preserved verbatim, including single labels. Background and Admin reject unsafe path segments and legacy shopId/base64url-keyed READY keys; existing readable raw-domain keys are canonical. Background re-reads/locks the current raw Shop domain when claim results are committed so a rename invalidates an in-flight result.
