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
status: review
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

- [x] Implement only the bounded capability and document compatibility/rollout.
- [x] Add meaningful prior-behavior red and regression/concurrency/security coverage.
- [x] Complete required validation and mirrored task report/push.

## Interfaces / Contracts

Published @modainteract/moda-interact-shared/commerce/presentation for reusable media schemas/digests; Background owns live provider access, tenant/domain/READY evidence and lifecycle.

## Dependencies

ARCH-073-BACKGROUND-001

## Enables

Dependent tasks only after architect acceptance.

## Acceptance Criteria

- [x] Required bounded behavior works without hardcoded identity or broader permissions.
- [x] Tenant/domain, immutable state, authorization and concurrent-update boundaries remain enforced.
- [x] Existing unrelated media/frozen content is preserved; no secret/private proof committed.
- [x] Canonical dedicated mirrored worktree/synchronization/recursive submodule evidence recorded.

## Validation

- [x] Basic-name coexistence; stable tokenless request carries no credentials/cookies, successful asset mapping, CHANNEL_LOCKED/error preservation, explicit absent assets and bounds.
- [x] Real PostgreSQL duplicate/stale/domain/platform/installation races and media/source JSON preservation.
- [x] Existing media pipeline unit/integration, types/scoped lint/declared build and exact-head full CI.
- [x] Diff/secret hygiene and canonical isolated mirrored execution/report evidence.

## Stop Condition

After Work Items, Acceptance Criteria and required Validation complete, submit review report and STOP. Do not merge/deploy or begin enabled work.

## Implementation Notes

You are not alone. Preserve others' changes. Use prepared canonical packet. Root owns final merges/deployment; architect owns acceptance. Read historical code as evidence, not permission to restore unrelated behavior or stale API assumptions.

## Completion Report

### Status

Ready for Review. Implementation and final required checks committed/pushed; awaiting moda_architect review.

### Files Changed

Implementation cb7c0ce57feb69ca839342ea4d7ddd57a599ed1e ([PR208](https://github.com/kodjobaah/moda-interact-background/pull/208)): Background-local public brand reader/contracts/mapping/repository/service/runner, recovery-worker start/stop, provider/scheduler/lifecycle units and PostgreSQL source/identity/preservation integration tests; docs/shopify-public-brand-assets.md. No schema, dependency, Shared, credential or permission change. Basic-name/header source untouched.

### Work Completed

- Implemented architect-approved amendment79da45abb: stable tokenless Storefront2026-07 only, exact leased installed Shopify domain, credentials omit, Content-Type-only headers, redirects refuse, pinned response version, bounded deadline/body/parser and originating-error redaction through existing shared logger. Provenance is honestly shopify-storefront plus hash of actual returned MediaImage ID.
- Independent shopifySourceSync asset lease/cadence/backoff preserves shopifyNameSync, authenticated brandName and concurrent media updates. Bounded keyset scans handle absent rows; Shop→ShopBrand locked tenant/platform/domain/installed/uninstalled/reinstall identity revalidation at claim and commit. No provider work in transactions.
- Complete validated present/absent observations reuse existing source generation/fingerprint and safe-fetch/transform/R2/verified-READY pipeline. No direct READY fabrication, new processor or logo dispatch. Newer observations overtake stale network snapshots safely, including square-logo fallback.
- CHANNEL_LOCKED/unavailability retains known valid media and authenticated names; only successful fully validated null observations mark source MISSING. Five-minute sweeps inspect500/claim20, concurrency2, two-minute durable lease, daily refresh; transient1m/5m/30m/2h/24h and bounded Retry-After. No repeated permission requests or credential/channel changes.

### Validation Results

- Prepared packet /tmp/moda-arch073-bg003-prepare.json: canonical workspace and dedicated parent/implementation task/ARCH-073-BACKGROUND-003 branches; no other task checkout reused. Parent/implementation main current at preparation, durable claimdd3e85e5570a7dd99e88487cde5a6d73c12b0380; implementation base00e143fc1ccf7af11f2fe1eadcb0b236dd422ab0; recursive submodule sync/update passed, database5329d5390d346042895219663f3a040ea54ae168. Current main remains accepted base per root; parallel header task will incorporate merged main later.
- Meaningful historical-contract red: official pinned Admin2026-07 schema rejects Shop.brand and QueryRoot.branding; diagnostic next-stable2026-10 also rejects Shop.brand. This prevented publishing the invalid preserved reader. Exact final public-source query validates successfully against stable Storefront2026-07. Skill instrumentation disabled throughout.
- [Stable Storefront Brand](https://shopify.dev/docs/api/storefront/2026-07/objects/Brand) and [official Hydrogen reference](https://shopify.dev/docs/api/hydrogen/2026-04) support the route. Root-approved single credential-free reference read returned200/version2026-07/noerrors with all three asset roles. Private full proofchmod600 /tmp/moda-arch073-reference-brand-proof.json; committed evidence coarse/public only.
- Selected development shop single tokenless probe returned400/BAD_REQUEST, exact `Online Store channel is locked.` No data/credentials/cookies/customer fields sent or returned. Private proofchmod600 /tmp/moda-arch073-public-brand-proof.json. This is an operational limitation, not absent-logo proof; no unlock/Storefront token/read_brand mutation performed.
- Focused media/pipeline run101 assertions passed, one copied lifecycle assertion used wrong stop-handle identifier; corrected final new19/19 passed. Final reader16/16 after added raw-URL-control case; all existing media processing/READY tests passed in the broader run. Task-owned ESLint and source typecheck exit0.
- Actual disposable PostgreSQL final10/10 public asset cases: unique first acquisition, competing/stale/expired claims, successful cadence, CHANNEL_LOCKED/currentREADY/name preservation, retry/explicit null, six installation changes, newer-source/square fallback, concurrent independent name/media/source metadata. Existing basic-name9/9 and media3/3 also passed. One fixture expected first-attempt delay after earlier failure; corrected to actual second-attempt5-minute backoff and rerun green.
- Declared npm run build exit0 after PostgreSQL. Tests use disposable endpoints/synthetic fixtures and mocked providers; no production DB writes, Meta sends or READY bootstrap.
- Exact-head full CI PASS: [push](https://github.com/kodjobaah/moda-interact-background/actions/runs/43293198435)2m37s and [PR](https://github.com/kodjobaah/moda-interact-background/actions/runs/43293296085)1m36s, headcb7c0ce57feb69ca839342ea4d7ddd57a599ed1e. Both include clean dependency install, generated Prisma client, source typecheck and complete unit suite. Diff/secret hygiene clean.

### Deviations

Required provider route amendment was approved before source changes: unsupported historical Admin/read_brand assumptions replaced by stable tokenless public Storefront. No new permissions/credentials or unstable API introduced.

### Assumptions

Only current exact installed tenant-domain public observations enter the existing pipeline. Public asset availability does not authenticate or override basic-name metadata, authorize messages, or prove selected-store logo delivery.

### Unresolved Issues

No unresolved implementation issue. Selected development store remains CHANNEL_LOCKED; root owns separately authorized supported source bootstrap and actual logo/readiness/delivery proof. Text fallback alone does not satisfy that production gate.

### Architectural Concerns

No unresolved implementation contract gap after amendment. Historical Admin prototype was replaced before any commit/provider use. Preserve independent state and old frozen content; do not add unstable/Admin/Storefront credentials, channel unlock, theme scraping or production bootstrap under this task.

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
