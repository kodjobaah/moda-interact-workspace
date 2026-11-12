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

In Progress. Eligible recovery messages need a clear shop-name and website header across AI, HUMAN and service notices. Current trusted wrapper context reads shop.name only from ShopBrand; Shopify source acquisition exists on an unmerged historical task branch, so a newly installed shop may have no brand row. Current production installation lacks read_brand. No logo or new permission is authorized by this baseline.

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
| ARCH-073-BACKGROUND-001 | moda_background | Ready | None |
| ARCH-073-BACKGROUND-002 | moda_background | Pending | ARCH-073-BACKGROUND-001 |

## Open Questions / Change History

Logo is excluded pending an explicit later request and permission. Basic name plus verified website is the approved baseline. No further code/design is authorized beyond these bounded tasks. Public documentation uses coarse proof only.
