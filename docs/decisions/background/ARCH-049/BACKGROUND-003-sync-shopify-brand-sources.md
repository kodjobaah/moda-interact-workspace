---
id: ARCH-049-BACKGROUND-003
architecture_id: ARCH-049
title: Synchronise Shopify Brand API sources into commerce.ShopBrand
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on: ["ARCH-049-DATABASE-001", "ARCH-049-BACKGROUND-002", "ARCH-049-SHOPIFY-001"]
enables: ["ARCH-049-SYSTEM-TEST-001"]
created: 2026-10-25
updated: 2026-10-27
---

# Synchronise Shopify Brand API sources into commerce.ShopBrand

## Architecture

`ARCH-049` — `docs/architecture/ARCH-049-shopbrand-public-media-configuration.md`; coordinator `moda_architect`. **Portable task definition, not materialised in a developer Git worktree.**

## Objective

Use the existing Background authenticated Shopify GraphQL client to read the merchant's Brand data and persist platform-neutral ShopBrand source metadata. No new Shopify app ingestion service is created.

## Context

The Shopify app needs `read_brand`, supplied by the narrow SHOPIFY-001 task. The provided snapshot has a token-fetching service and generic GraphQL client path but no ShopBrand writer. Background source sync must reuse BG002's exported row-locked source-update module, not implement a parallel JSONB state machine. The BG002 prerequisite is intentional: this task imports that implementation across Background module boundaries; Shopify grant configuration alone does not supply its persistence operations.

## Scope

- Add `src/services/shop-brand-media-shopify/` with GraphQL request/parser, canonical source mapping, bounded refresh scheduler and typed error handling.
- Reuse `shopify-session.service.ts` authentication and existing Background Shopify GraphQL conventions.
- Persist `brandName`, logo/alt/dimensions, squareLogo when available or explicit fallback, coverImage source, `fetchedAt` and `lastRefreshedAt` via the canonical ShopBrand row.
- Invoke BG002 source updates for changed/removed per-role source, without downloading any image in this module.

## Out of Scope

- Changing Shopify app scopes (SHOPIFY-001), WooCommerce extraction, R2 object storage, template sending or direct WordPress access.

## Requirements

### R1. Shopify provider reads

Query the authenticated Shopify Admin GraphQL `shop { name brand { ... } }` via an API version supported by the installed Shopify client and the `read_brand` scope, using documented `BrandingBrand` fields. Retrieve available default `logo` and `coverImage` source URL, source ID/dimensions, and brand name. The current Admin `BrandingBrand` may not return a dedicated `squareLogo`; **do not invent a nonexistent GraphQL property**. If no independently supported square source exists, record `squareLogoUrl=null` and let the documented derived square-image fallback process the main logo. Treat `brand=null`, no image, missing grant, GraphQL errors, rate limit and disabled Shop separately.

### R2. Mapping

From the verified authenticated shop context, map:

```text
shop.name / configured Brand display name -> ShopBrand.brandName
brand.logo original or supported transformed URL -> ShopBrand.logoUrl
brand.logo dimensions when returned -> ShopBrand.logoWidth/logoHeight
brand.coverImage source URL -> ShopBrand.coverImageUrl
supported square-logo source (if provided) -> ShopBrand.squareLogoUrl
```

Do not fabricate alt text or width/height for unavailable sources. Use provider image ID/update/reference when available to build a stable source fingerprint; the canonical BG002 observation algorithm increments generation when the effective locator changes. Persist shopId derived from the authenticated Shop record, never from untrusted response properties alone.

### R3. Refresh/ordering

Enqueue initial sync for eligible connected Shopify shops and a bounded daily refresh (at most one per 24 hours by default). Rate-limit and back off on 429 and provider failures; do not overwrite current source with null on an **unsuccessful** API response. On a **successful** response proving source removed, mark the relevant role MISSING. Source changes update PostgreSQL and are recovered by BG002 scan even if a queue wake fails. Never fetch/resize images here.

### R4. No unsupported permission workaround

Missing `read_brand` is a per-shop provider-auth failure; log a bounded code and route to Shopify-authorisation work. Do not scrape storefronts or use merchant WordPress endpoints as a workaround.

## Work Items

- [ ] Add Shopify brand reader/parser with mocked GraphQL fixture.
- [ ] Add initial/daily sync scheduling with per-shop limits.
- [ ] Integrate only with ShopBrand row and BG002 source updater.
- [ ] Cover null/missing/scope error/rate-limit/change/removal with tests.

## Interfaces / Contracts

Consumes existing Shopify app authentication (`getShopifyAccessToken`) and the BG002 `SourceObservation`/CAS repository; produces original source fields in `commerce.ShopBrand`. No new Shared contract or Shopify app service. `ARCH-049-SHOPIFY-001` owns `read_brand` scope; BG003 owns fetch.

## Dependencies

- ARCH-049-DATABASE-001
- ARCH-049-BACKGROUND-002 — owns the source-update helper consumed by this synchroniser.
- ARCH-049-SHOPIFY-001 — owns the `read_brand` permission and reauthorisation.

## Enables

- ARCH-049-SYSTEM-TEST-001

## Acceptance Criteria

- [ ] Shopify brand changes and removals reflect in correct ShopBrand roles without cross-tenant writes.
- [ ] Missing `read_brand`, provider error or rate limit preserves last known source state and produces clear failure, not arbitrary null erasure.
- [ ] Daily sync is bounded and no image decoding/R2 work is duplicated.

## Validation

- [ ] GraphQL fixture tests including data/missing media, 403 missing grant, 429, stale observation and change.
- [ ] Focused authenticated tenant tests and due-scheduling validation.
- [ ] Relevant Background lint/typecheck/tests and `git diff --check`.

## Stop Condition

After the defined Work Items, Acceptance Criteria and Validation are complete, record the Completion Report and change task status to `review`; hand off to `moda_architect` and STOP. Do not continue into a dependent task or change an `_index.md`.

## Implementation Notes

All task work must use the canonical launcher-provided **dedicated parent and implementation worktrees**, synced task/<TASK_ID> branches and start-of-attempt evidence. Inspect the actual pinned package scripts, source and existing conventions before editing. Do not merge branches, push main, edit another repository, start an enabled task or change any `docs/decisions/**/_index.md`. Use structured logging via `@modainteract/moda-interact-shared/logging`; secrets and full untrusted URLs must not enter diagnostics. Document changed files, relevant test commands, results, security/tenant checks, commits and worktree evidence in the Completion Report.

No additional assumptions are authorised.

## Completion Report

### Status

Not Started — defined but not materialised.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

None beyond the explicit architecture/task contract.

### Unresolved Issues

None; live environment availability is a validation prerequisite and must be reported if missing.

### Architectural Concerns

None reported.

## Architect Review

### Review Status

Pending.

### Review Notes

None.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Not reviewed.

### Follow-up

None.
