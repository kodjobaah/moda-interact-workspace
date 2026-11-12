---
id: ARCH-073-BACKGROUND-001
architecture_id: ARCH-073
title: Acquire basic Shopify shop name with bounded durable refresh
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 10
executor: codex
claimed_at: 2026-11-12T18:57:35Z
attempt: 1
depends_on: []
enables:
  - ARCH-073-BACKGROUND-002
created: 2026-11-12
updated: 2026-11-12
---

# Acquire basic Shopify shop name with bounded durable refresh

## Architecture

ARCH-073; docs/architecture/ARCH-073-tenant-recovery-shop-headers.md; coordinator moda_architect.

## Objective

Persist authenticated basic Shopify shop names using bounded durable refresh without requiring read_brand.

## Context

Current main lacks preserved Shopify name acquisition; wrappers cannot render a missing ShopBrand name. User requests generic shop branding, never a hardcoded single-shop patch.

## Scope

Selectively adapt preserved BG003 source-reader/scheduler/state/repository patterns into current Background. Own new basic-name reader/service/runner modules or narrowly adapted old module, orchestration JSON preservation/lease helpers, recovery entrypoint lifecycle, tests/package scripts/docs. Do not restore media reads.

## Out of Scope

Logo/media enablement, read_brand/other permission changes, privileged Brand queries, wholesale historical merge, unrelated token refactor, production DB backfill, schema/new namespace/Shared release, other repositories, live sends or deployment. Return genuine cross-owner gaps.

## Requirements

Use current selected-Shop-ID token API (historical getShopifyAccessToken(domain) is now wrong). Basic shop.name query only, bounded response/time/cancellation. Claim and completion lock/revalidate same active SHOPIFY shop/domain; domain/status/platform/installation changes during read reject stale writes. No network in transaction. Durable leases/cadence/backoff must survive multiple workers/restarts; bounded keyset scan handles absent brand row and hot-tenant fairness. Preserve media JSON and source state on every update; no failure may blank known good name or manufacture branding. Current token internals remain unchanged. Basic name succeeds when read_brand is absent. Document source/name refresh cadence and safe retry.

## Work Items

- [x] Implement only the bounded capability and document compatibility/rollout.
- [x] Add meaningful prior-behavior red and regression/concurrency/security coverage.
- [x] Complete required validation and mirrored task report/push.

## Interfaces / Contracts

Background-local current authenticated Shopify token and ShopBrand persistence; existing published Shared schemas/logging remain canonical. No new cross-service wire is planned.

## Dependencies

None

## Enables

ARCH-073-BACKGROUND-002

## Acceptance Criteria

- [x] Required bounded behavior works without hardcoded identity or broader permissions.
- [x] Tenant/domain, immutable state, authorization and concurrent-update boundaries remain enforced.
- [x] Existing unrelated media/frozen content is preserved; no secret/private proof committed.
- [x] Canonical dedicated mirrored worktree/synchronization/recursive submodule evidence recorded.

## Validation

- [x] Provider/parser tests: basic name without read_brand, no privileged fields, malformed/oversize/timeouts/revoked token safe failures.
- [x] Actual PostgreSQL absent-row first sync, duplicate/competing claims, expired lease/stale result, domain/status/platform/installation changes, retry/cadence and concurrent media preservation.
- [x] Recovery-worker startup/shutdown and bounded scans; existing orchestration tests remain green.
- [x] Types, task-owned lint, declared build and exact-head full CI; inspect package scripts first.
- [x] Diff/secret hygiene; synthetic fixtures and mocked providers, no real Meta send or production write.

## Stop Condition

After Work Items, Acceptance Criteria and required Validation complete, submit review report and STOP. Do not merge/deploy or begin enabled work.

## Implementation Notes

You are not alone. Preserve others' changes. Use prepared canonical packet. Root owns final merges/deployment; architect owns acceptance. Read historical code as evidence, not permission to restore unrelated behavior or stale API assumptions.

## Completion Report

### Status

Ready for Review. Implementation and final validation committed/pushed; awaiting moda_architect review.

### Files Changed

Implementation `1cb77855ec91806081ab1d0fad7d131f5e804e87`, [PR207](https://github.com/kodjobaah/moda-interact-background/pull/207): new Background-local shopify-shop-name contracts/reader/repository/service/runner; recovery entrypoint start/stop; two existing media state transitions preserve additive metadata; provider/scheduler/lifecycle unit tests, real PostgreSQL acquisition/concurrency tests and cadence documentation. No dependency, schema, Shared, media acquisition or permission changes.

### Work Completed

- Selectively recovered bounded keyset/cadence/lease/retry patterns from preserved BG003; did not merge historical branch or restore privileged brand/media reads. Basic `shop { name }` alone succeeds without read_brand.
- Current selected-Shop-ID credential snapshot must match both claim Shop ID and stored domain before HTTP. Redirects refuse; token/read/body operations share a bounded cancellation deadline and response-byte limit. Provider failures retain safely bounded originating errors through the shared logger; secrets/PII are redacted before emission, and sink failures cannot change authorization/retries.
- PostgreSQL Shop→ShopBrand locks revalidate active SHOPIFY platform, exact domain/installedAt, and absent uninstalled/reinstall-pending flags at claim and completion. Network work is outside transactions. Expired/replaced leases and changed installation identity refuse writes.
- Absent brand rows are discovered; durable lease arbitrates replicas and survives restarts. Five-minute scans inspect at most500 shops/claim20 reads with concurrency2, fair keyset cursor; successful names refresh24h, transient1m/5m/30m/2h/24h backoff and bounded Retry-After. Failed reads never blank good names.
- Independent basic metadata uses shopifyNameSync, reserving shopifySourceSync for permission-gated assets. Both lease/backoff objects, existing media/source JSON and newer concurrent media updates survive name completion and existing media transitions. Only brandName/fetchedAt and existing JSON sync metadata are written; no per-message provider work or new queue.

### Validation Results

- Prepared launcher packet `/tmp/moda-arch073-bg001-prepare.json`: canonical primary workspace and dedicated parent/implementation worktrees on matching task/ARCH-073-BACKGROUND-001, no shared/other-task checkout reused; parent and implementation origin/main already current, recursive submodule sync/update passed; database pinned5329d5390d346042895219663f3a040ea54ae168; baseae43e0b3f1fa660813f762c32602fb268e1e7c4a, durable claimb916cf64a274284a1e7484dbd15a2aca16403491.
- Shopify skill search/schema validator with OPT_OUT_INSTRUMENTATION=true: basic query valid against Admin2026-07 [Shop documentation](https://shopify.dev/docs/api/admin-graphql/2026-07/objects/Shop). No private credentials/payload sent to skill telemetry.
- Meaningful prior-code red: original media source transition drops persisted name lease metadata; new preservation assertion fails. Temporary prior module/test removed; production source not switched to old behavior.
- Focused46/46 tests across new provider/scheduler/lifecycle and existing orchestration; final new20/20 after cancellation/cause changes. Provider tests include no read_brand, selected identity mismatch/no HTTP, malformed/control/oversized names/body, HTTP/GraphQL/revoked credentials, timeout, safe originating diagnostics and sink failure.
- Disposable PostgreSQL9/9: absent-row first sync, competing claims, successful cadence, retry-after/backoff/known-name preservation, expired/replaced result, six installation changes (domain/status/platform/uninstalled/installed/reinstall-pending) and concurrent media preservation. Existing media orchestration PostgreSQL3/3 also passed. Initial synthetic fingerprint missing required sha256: prefix was corrected; final9/9 green.
- Final task-owned ESLint and source typecheck exit0. Declared npm run build exit0; executed after database tests to avoid concurrent generated-client changes. No production DB/Redis tests or Meta sends.
- Exact-head full CI PASS (push2m36s, PR2m35s), including clean install/Prisma generation/source typecheck/complete unit suite: [push](https://github.com/kodjobaah/moda-interact-background/actions/runs/43287919689), [PR](https://github.com/kodjobaah/moda-interact-background/actions/runs/43287935045), head1cb77855ec91806081ab1d0fad7d131f5e804e87.
- Diff/secret hygiene clean; committed evidence uses synthetic values only.

### Deviations

Root/architect review identified the historical JSON sync-key collision once logo acquisition was added to the architecture. Implemented distinct shopifyNameSync and unit/real PostgreSQL independent-state preservation proof; final corrected-head checks passed locally. Basic name is independent from newly requested logo acquisition, which remains a separate architectural task.

### Assumptions

Current selected-Shop-ID session service remains the credential/tenant authority. No additional grant or protected data is required. Name acquisition does not compose or authorize a customer message.

### Unresolved Issues

No unresolved implementation issue. Root owns merge, deployment and production read verification; enabled header task remains separate.

### Architectural Concerns

No cross-owner gap. Existing workers can read unchanged media JSON schema; new name scheduler is enabled with recovery-worker rollout. Do not enable historical privileged Brand/media sync as part of this task.

## Architect Review

### Review Status

Accepted

### Review Notes

Actual final source `1cb77855ec91806081ab1d0fad7d131f5e804e87` and durable report `f0a975076` reviewed. Basic name query requires no read_brand; current selected-Shop session identity and locked Shop platform/domain/install checks protect claims/completions. Bounded durable shopifyNameSync remains independent of privileged shopifySourceSync and media JSON. No actionable findings.

### Reviewed Files

Reader, repository, service/runner, recovery lifecycle, media metadata-preserving transitions, provider/unit/PostgreSQL tests and cadence document.

### Validation Reviewed

Meaningful prior-behavior red, focused46, disposable PostgreSQL9 plus existing media3, types/scoped lint/build and both exact-head clean CI4028 tests/373 files. Canonical prepared mirrored isolation/base/recursive submodule evidence matches packet. No duplicate architect run needed.

### Architecture Conformance

Conforms to permission-free basic-name capability. No privileged media read, schema/dependency/permission change or per-message provider request. Independent source-state correction is required by approved logo task separation and covered by real persistence tests.

### Follow-up

Developer owns implementation merge/deployment and genuine production read verification. Text header and permission-gated asset tasks become Ready; neither is implemented by this task. Full architecture remains In Progress.
