---
id: ARCH-073
title: Tenant-specific recovery shop headers
status: in_progress
coordinator: moda_architect
created: 2026-11-12
updated: 2026-11-12
---

# ARCH-073: Tenant-specific recovery shop headers

## Status / Problem

In Progress. Eligible recovery messages need a clear shop-name and website header across AI, HUMAN and service notices. Current trusted wrapper context reads shop.name only from ShopBrand; Shopify source acquisition exists on an unmerged historical task branch, so a newly installed shop may have no brand row. Current production installation lacks read_brand. The name/text baseline requires no additional permission. User subsequently requested logos; additional permission-gated tasks are defined separately below.

## Goals / Non-Goals

Acquire authenticated basic shop.name without read_brand, then compose a deterministic per-tenant text header using that persisted name and verified stored domain. Preserve footer, authorship, immutable replay, moderation and final permit identity. No hardcoded merchant identity, logo/media activation, privileged Brand query, permission changes, new schema, namespace, package release or historical task reopen.

## Inspected Architecture / Design

Preserved Background branch task/ARCH-049-BACKGROUND-003 at bcac6ed contains bounded Shopify source reader/scheduler and durable sync state. It never entered canonical main. Selectively recover its coherent lifecycle/lease/backoff patterns rather than merge unrelated old changes. Its historical domain-based getShopifyAccessToken call is incompatible with the current selected-Shop-ID API; use current authenticated shop-bound token service. Request only basic shop.name. Revalidate active Shopify platform/domain under row locks at claim and completion; a shop changed during network I/O cannot receive stale metadata. Preserve all existing media/source JSON and concurrent updates.

Second task consumes persisted name and current verified stored domain. Existing wrapper text headers support shop.name but service notices bypass wrappers and domain is not a current wrapper variable. Prefer existing contracts where sufficient; use Background-local verified provenance for mandatory header if no new cross-service contract is necessary. Preserve configured headers/idempotence and authored text; no post-permit append or silent global validation relaxation. Return genuine Shared/schema gaps before expansion.

## Flow / Ownership / State

Recovery-worker bounded shop scan -> durable claim -> authenticated bounded basic-name read outside transaction -> locked current-shop revalidation -> existing ShopBrand metadata persistence -> eligible recovery composition -> name/domain header + existing divider/checkout footer -> freeze/hash/media/moderation/final permit -> identical provider body. Background owns both tasks. PostgreSQL remains durable authority; no new queue or table. Provider calls are not in transactions. No per-message Shopify fetch or broad conversation serialization.

## Security / Failure / Observability / Infrastructure

No additional Shopify scope is required. Current token selection, tenant/platform/domain checks, cancellation, bounded provider responses and safe error handling remain. Missing name cannot fabricate branding or cross-bind another shop; define controlled fallback using verified domain only. Existing shared structured logging suffices with bounded semantic counts/reason codes and no customer/provider secrets. No Gateway, generic telemetry or infrastructure task is required. Preserve consent, STOP/security exclusions and approved Meta templates unchanged.

## Rollout / Compatibility / Validation

PRODUCTION / COMPATIBLE ROLLOUT. Accept name acquisition first, then header composition; developer merges/deploys and verifies genuine new replies after old-worker drain where evidence formats differ. Old frozen applications/commands replay unchanged. No schema migration, Shared publication or queue-data drain is intended. Full relevant PostgreSQL state/concurrency tests, source types/scoped lint/build and exact-head CI required. Same-repository mechanism does not require separate system-test task; developer genuine integrated proof gates Implemented.

## Decisions / Tasks

| Task | Owner | Status | Depends On |
|---|---|---|---|
| ARCH-073-BACKGROUND-001 | moda_background | Complete | None |
| ARCH-073-BACKGROUND-002 | moda_background | Ready | ARCH-073-BACKGROUND-001 |

## Open Questions / Change History

Logo is excluded pending an explicit later request and permission. Basic name plus verified website is the approved baseline. No further code/design is authorized beyond these bounded tasks. Public documentation uses coarse proof only.

- Text-header clarification: name/verified HTTPS website/neutral divider/blank line precede body and existing footer. Background-local identity receipt binds immutable/application/final-permit validation; old absent evidence preserves old bytes. Deduplication is limited to proven pure-identity configured header tokens, never authored body heuristics. User subsequently requested a logo where supported; this requires separate read-only capability/permission assessment and does not expand the first two tasks.

## Optional requested logo extension

User requests shop name, website and logo where WhatsApp supports it. Official Meta ImageMediaObject carries image link/id plus optional caption (https://whatsapp.github.io/WhatsApp-Nodejs-SDK/api-reference/types/ImageMediaObject/); text is not HTML. Preserve product image priority. A verified logo may occupy the single image position only for otherwise-plain eligible responses within caption bounds; full text fallback and no extra send are mandatory.

Current published product-image plan requires genuine product identity; add a separate canonical brand-image provenance/plan export in Shared rather than fabricate product IDs or relax legacy schema. Background consumes exact public package, validates current same-tenant/domain/generation READY output using existing adapter, and binds it through HUMAN/AI frozen preparation and provider permit. Existing HUMAN path is text-only, so media evidence/dispatch is an explicit bounded consumer capability. No new schema is currently authorized; return a demonstrated persistence gap.

| Task | Owner | Status | Depends On |
|---|---|---|---|
| ARCH-073-SHARED-001 | moda_shared | Ready | None |
| ARCH-073-SHARED-002 | moda_shared | Pending | ARCH-073-SHARED-001 |
| ARCH-073-BACKGROUND-003 | moda_background | Complete | ARCH-073-BACKGROUND-001 |
| ARCH-073-BACKGROUND-004 | moda_background | Pending | ARCH-073-BACKGROUND-002, ARCH-073-BACKGROUND-003, ARCH-073-SHARED-002 |

Historical privileged Admin branding was rejected by stable schema; the accepted supported source route is tokenless stable Storefront with no new grant. Shared publication requires explicit user approval for the concrete tested public patch before execution. These gates do not block basic-name acquisition or text headers. Rollout: additive Shared acceptance/publication then consumer acceptance; schema unchanged, old plans/frozen records preserved, old-worker drain before newly incompatible evidence. Final architecture completion also requires genuine text/logo/fallback production proof where available and documented permission/media readiness. No separate generic logger/telemetry or infrastructure capability is introduced.

- State separation clarification: basic-name refresh owns shopifyNameSync in existing ShopBrand JSON; permission-gated assets retain independent historical shopifySourceSync. Parser and transitions preserve both cadences/leases and media roles. A shared lease key would incorrectly suppress or clobber the other capability; no database schema change is needed.

- Basic-name implementation accepted at `1cb77855ec91806081ab1d0fad7d131f5e804e87`; independent name/asset state and real PostgreSQL isolation tests passed. Header and permission-gated source tasks are Ready, but execution preparation must incorporate the actual developer-merged source main.

- Asset route correction: stable Admin2026-07 and2026-10 reject historical Shop.brand/QueryRoot.branding. Stable Storefront2026-07 brand schema and tokenless public reference-store read are verified. BG003 uses that supported public route, with no read_brand/new credential. Current development store reports CHANNEL_LOCKED; retain known media and treat as operational unavailable, never absence or a reason to unlock/create credentials. Current installed tenant/domain/installation locks remain authority; public source is labelled honestly. One-time administrator-verified Shopify UI source bootstrap is under separate root assessment, not task permission for production writes.

- Stable public asset acquisition accepted at `cb7c0ce57feb69ca839342ea4d7ddd57a599ed1e`; provider contract, current-domain persistence/race tests and both clean CI passed. Selected development shop remains CHANNEL_LOCKED; no production logo readiness/delivery is claimed.

## Reconciled execution frontier

| Task | State | Evidence |
|---|---|---|
| ARCH-073-BACKGROUND-001 | Complete | Accepted basic-name source, merged main and genuine production name capture verified; no manual backfill. |
| ARCH-073-BACKGROUND-002 | In Progress | Text header final combined source awaiting review/CI. |
| ARCH-073-BACKGROUND-003 | Complete | Accepted stable public asset source, merged source; production reports controlled CHANNEL_LOCKED without clearing known media. |
| ARCH-073-SHARED-001 | Complete | Additive brand plan accepted and merged46834ef32a945606c92feade5924564ce325b326. |
| ARCH-073-SHARED-002 | Complete | Public5.13.7 exact downloaded bytes match accepted artifact. |
| ARCH-073-BACKGROUND-004 | Pending | Header acceptance/source merge required before preparation. |

No live logo readiness/delivery is claimed. Logo-only role policy excludes cover/banner substitution; root awaits standalone approved asset. Existing JSON evidence and physical IMAGE transport appear sufficient, with current tenant/READY media final-fence verification and legacy exact replay mandatory. Implementation task must return a concrete persistence gap rather than invent schema or weaken provenance. Architecture stays In Progress until genuine text/header/logo-or-explicit-fallback validation and honest operational limitations are recorded.
