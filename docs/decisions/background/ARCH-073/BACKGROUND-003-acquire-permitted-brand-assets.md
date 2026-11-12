---
id: ARCH-073-BACKGROUND-003
architecture_id: ARCH-073
title: Acquire permission-gated Shopify brand assets through existing pipeline
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 15
executor: codex
claimed_at: 2026-11-12T19:19:31Z
attempt: 1
depends_on:
  - ARCH-073-BACKGROUND-001
enables: []
created: 2026-11-12
updated: 2026-11-12
---

# Acquire permission-gated Shopify brand assets through existing pipeline

## Architecture

ARCH-073; docs/architecture/ARCH-073-tenant-recovery-shop-headers.md; coordinator moda_architect.

## Objective

Acquire permission-gated Shopify brand assets through existing pipeline.

## Context

User explicitly requests a shop logo where WhatsApp supports it. Existing canonical product-image plans cannot represent a brand image honestly; preserve product identity and the completed text baseline.

## Scope

Stable tokenless Storefront2026-07 public brand-asset acquisition for exact installed tenant domain; selective existing bounded asset scheduler/mapping/orchestration reuse. Keep basic-name and media-source sync lifecycle separate. Tests/docs and recovery-worker lifecycle only; no privileged Admin Brand API or new media processor.

## Out of Scope

Unsupported stable Admin Shop.brand/QueryRoot.branding, unstable Admin API, read_brand scope mutation, Storefront credential/channel creation, password unlock, theme/files scraping, production bootstrap/source writes, logo dispatch, Shared release, other repositories. No wholesale historical branch merge.

## Requirements

Official stable Storefront schema and a single documented public reference-store tokenless read are verified. Query only public brand media via the exact leased installed Shopify domain; send no customer cookies, credentials or authorization token. No fallback to unsupported Admin fields. Label this public provider provenance honestly, not authenticated Admin observation. Revalidate active SHOPIFY domain/install/uninstall under Shop locks at claim/completion; redirects refuse and response/time/error limits remain. Shopify shop.name stays the independent accepted name scheduler; do not overwrite its name merely from public branding.

Use existing independent shopifySourceSync asset lease/cadence/backoff; preserve shopifyNameSync and all concurrent media state. CHANNEL_LOCKED/password-protected or unavailable public API is a bounded operational unavailability, never proof logo absent or authorization failure: retain existing valid assets, do not clear them or create credentials/unlock store. Only successful validated same-domain public response can update explicit present/absent asset observations. Reuse source observation/current-generation fingerprint/R2 transform/verified READY pipeline and safe fetching; no fabricated fingerprint/media IDs or direct READY writes. Public source does not grant authority beyond the exact installed tenant.

Current development store public API is CHANNEL_LOCKED; generic code may be validated on synthetic/reference evidence, but architecture cannot claim that store logo delivery until an authorized supported source is actually ready. Root is separately evaluating a one-time verified Shopify UI source observation; that is not implementation authority to mutate production or bypass pipeline. No additional permission is required for this tokenless route.

## Work Items

- [ ] Implement only the bounded capability and document compatibility/rollout.
- [ ] Add meaningful prior-behavior red and regression/concurrency/security coverage.
- [ ] Complete required validation and mirrored task report/push.

## Interfaces / Contracts

Published @modainteract/moda-interact-shared/commerce/presentation for reusable media schemas/digests; Background owns live provider access, tenant/domain/READY evidence and lifecycle.

## Dependencies

ARCH-073-BACKGROUND-001

## Enables

Dependent tasks only after architect acceptance.

## Acceptance Criteria

- [ ] Required bounded behavior works without hardcoded identity or broader permissions.
- [ ] Tenant/domain, immutable state, authorization and concurrent-update boundaries remain enforced.
- [ ] Existing unrelated media/frozen content is preserved; no secret/private proof committed.
- [ ] Canonical dedicated mirrored worktree/synchronization/recursive submodule evidence recorded.

## Validation

- [ ] Basic-name coexistence; stable tokenless request carries no credentials/cookies, successful asset mapping, CHANNEL_LOCKED/error preservation, explicit absent assets and bounds.
- [ ] Real PostgreSQL duplicate/stale/domain/platform/installation races and media/source JSON preservation.
- [ ] Existing media pipeline unit/integration, types/scoped lint/declared build and exact-head full CI.
- [ ] Diff/secret hygiene and canonical isolated mirrored execution/report evidence.

## Stop Condition

After Work Items, Acceptance Criteria and required Validation complete, submit review report and STOP. Do not merge/deploy or begin enabled work.

## Implementation Notes

You are not alone. Preserve others' changes. Use prepared canonical packet. Root owns final merges/deployment; architect owns acceptance. Read historical code as evidence, not permission to restore unrelated behavior or stale API assumptions.

## Completion Report

### Status

Affected implementation paused pending supported API contract reconciliation; not ready for review.

### Files Changed

Uncommitted isolated prototype only: asset reader/contracts/mapping/repository/service/runner and recovery entrypoint lifecycle. No published implementation PR, main update or production execution. Do not merge the historical Admin query.

### Work Completed

Prepared canonical worktree/branch and selected recovery patterns. Designed selected-Shop-ID/session/domain/installation/read_brand checks and independent shopifySourceSync state while preserving shopifyNameSync. Official query validation revealed the historical provider contract is unsupported at the configured stable Admin API; stopped affected source work before any live privileged request or permission change.

### Validation Results

- Prepared packet `/tmp/moda-arch073-bg003-prepare.json`, base00e143fc1ccf7af11f2fe1eadcb0b236dd422ab0, durable claimdd3e85e5570a7dd99e88487cde5a6d73c12b0380, matching dedicated task/ARCH-073-BACKGROUND-003 branches; recursive database5329d539 initialized and gates passed.
- Shopify skill instrumentation disabled. Official Admin2026-07 validator rejects historical Shop.brand; QueryRoot.branding also invalid. Diagnostic next-stable2026-10 Shop.brand also invalid. Local evidence: /tmp/moda-arch073-assets-validation.log, /tmp/moda-arch073-root-branding-validation.log, /tmp/moda-arch073-brand-stable-validation.log.
- [Admin BrandingBrand](https://shopify.dev/docs/api/admin-graphql/unstable/objects/BrandingBrand) with read_brand exists in unstable documentation; no unstable/version switch is implemented or authorized.
- [Stable Storefront Brand](https://shopify.dev/docs/api/storefront/2026-07/objects/Brand) is a different valid schema: logo/squareLogo/coverImage use MediaImage{id,image{url,width,height}}. Official Storefront2026-07 validation PASS (/tmp/moda-arch073-storefront-validation.log).
- Root-authorized single public no-token/no-cookie/no-customer-field Storefront2026-07 read returned HTTP400 BAD_REQUEST, exact provider message `Online Store channel is locked.` This is not evidence of denied tokenless access or absent assets. Only coarse public metadata reported; full proof is chmod600 /tmp/moda-arch073-public-brand-proof.json. No Admin/Storefront token was sent, created or changed.
- Root-approved single reference-store read: [official Hydrogen documentation](https://shopify.dev/docs/api/hydrogen/2026-04) identifies hydrogen-preview.myshopify.com. Tokenless/cookie-free Storefront2026-07 request returnedHTTP200, version2026-07, no GraphQL errors and all three asset roles present. Protected proof chmod600 /tmp/moda-arch073-reference-brand-proof.json. This proves the generic stable tokenless route; it does not make Eugene's locked channel accessible.
- Locked-store alternative evidence: [Shopify staff](https://community.shopify.dev/t/store-locked-error-when-fetching-storefront-api-on-the-server/23265) documents valid Storefront-token authentication for dev stores; [official Headless setup](https://shopify.dev/docs/storefronts/headless/building-with-the-storefront-api/getting-started) describes token creation/permissions. No token/channel/grant change was requested or performed during this investigation.
- No database-backed tests, provider writes, Meta sends or permission mutation performed. Full implementation validation is deferred until the stable tokenless route is explicitly approved/amended.

### Deviations

Historical Admin query cannot safely be restored. Basic-name/header and independent Shared provenance tasks remain unaffected.

### Assumptions

None about unsupported API availability. Stable tokenless brand capability is proven on the officially documented Hydrogen reference shop; selected Eugene remains channel-locked. Implementation still requires explicit route amendment.

### Architectural Concerns

Required route decision: stable supported Storefront/tokenless source with exact proof; explicit stable Storefront credential/scopes if needed; or existing merchant-provided asset flow. Do not infer a grant, scrape themes/files under extra scopes, or switch to unstable Admin. Root and moda_architect have the concrete validation evidence. Current prototype remains uncommitted so unsupported provider code cannot deploy.

## Architect Review

### Review Status

Pending

### Review Notes

Pending actual source review.

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

None
