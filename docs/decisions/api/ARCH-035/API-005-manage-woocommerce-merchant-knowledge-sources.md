---
id: ARCH-035-API-005
architecture_id: ARCH-035
title: Add authenticated Woo Merchant Knowledge source mutations
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 80
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-035-API-004
enables:
  - ARCH-035-WOOCOMMERCE-004
created: 2026-10-11
updated: 2026-10-11
---

# ARCH-035-API-005: Add authenticated Woo Merchant Knowledge source mutations

## Architecture

- Architecture ID: `ARCH-035`
- Architecture document: `docs/architecture/ARCH-035-woocommerce-merchant-experience-parity.md`
- Coordinator: `moda_architect`
- Source baseline: uploaded `moda-interact-workspace(20261011-185536).zip`; task is a portable definition, not a claimed/materialised worktree.

## Objective

Provide the existing safe URL source management and CSV/XLSX upload/reprocess/delete/reorder workflows to authenticated Woo merchants.

## Context

The previous Shopify/Woo merchant-screen parity assessment showed this specific gap. Reuse the already accepted
ARCH-026 WordPress connection, locale and Shop security foundations and ARCH-027 billing components; do not duplicate
provider-neutral Moda domain state. The current capability is not established by this task definition.

## Deterministic implementation specification — mandatory

**Architect contract.** The exact model/column names, paths, API shapes, authentication boundary, state machine and
negative cases below are the implementation target. This section supersedes less-specific high-level text elsewhere
in this task. Agents may split production code into smaller modules, but must not change a public contract, migration
field, ownership rule, or dependency without returning to the architect. If a named existing dependency is absent or
incompatible, **STOP** and report the precise finding; do not silently invent a substitute.

**Files:** new focused `src/merchant/knowledge/{commands.service,upload.service,mutation.routes,validation}.ts`,
tests and matching OpenAPI sections; thin API bootstrap only. Reuse existing R2 client, SHA-256, URL SSRF policy,
source revision generation, asset entitlements and Background merchant-knowledge processing contract. If those
helpers are only in Next.js, extract/adapt pure logic into API-owned modules; never call a Shopify authenticated
route internally.

**Exact authenticated mutations (strict JSON keys and bounded bodies):** `POST /v1/merchant/knowledge/sources`
`{actionId,name,purposeId,dataFormatId,languageTag,url}` (URL sources); `PATCH /v1/merchant/knowledge/sources/:id`
`{expectedGeneration,name,languageTag,url}` (replace/update); `DELETE /v1/merchant/knowledge/sources/:id`
`{expectedGeneration}`; `PUT /v1/merchant/knowledge/order` `{expectedRevision,sourceIds:[...]}`; `POST
/v1/merchant/knowledge/sources/:id/reprocess` `{expectedGeneration}`; `POST /v1/merchant/knowledge/uploads/intent`
`{actionId,originalFileName,contentType,sizeBytes,sha256,dataFormatId}`; `POST
/v1/merchant/knowledge/uploads/:assetId/finalize` `{expectedStatus}`. Return
`{schemaVersion:1,sourceId?,assetId?,generation?,status,revision}` as applicable; on every successful mutation the
GET API-004 read is authoritative. Never accept shopId, external R2 objectKey or browser-provided bucket URL.

**Guards:** Shop row lock + source/asset shop ownership + plan capacity (replacements reconcile, not additive). Only
`https` SSRF-safe URLs with no credentials/loopback/private IP/DNS rebinding; only existing CSV/XLSX accepted
formats; file size/type and SHA-256 verified on **server-side R2 HEAD/finalize**, not trusted from JavaScript. Upload
intent uses short-lived signed direct-to-R2 upload, with credentials kept server-side and no WordPress file
persistence. Source generation is monotonic. For create/upload-intent, derive a deterministic source/intent identity
from Shop+actionId and reject conflicting request bytes; all other writes use expectedGeneration/revision CAS and
current-state equivalence for harmless retries. Do not claim global actionId replay guarantees without a durable
ledger; stale differing expectedGeneration/revision returns 409. Revise/create background work durably before
publishing optional queue hint. Reordering must be an exact permutation under a transaction and preserve unique
`(shopId,position)`. Deletion must never cascade across Shops; no stale upload finalisation can resurrect deleted
sources.

**Tests:** URL SSRF redirects/DNS, malformed CSV/XLSX, oversized body, wrong-Shop asset, forged R2 key, expired
intent and hash mismatch, concurrent replacements/reorders, idempotent retry, quota Free vs paid, background
unavailable but durable PENDING, Shopify R2/knowledge regression. Do not add a second processing worker or new
tables.

## High-level scope (non-authoritative summary)

- Reuse ARCH-023 SSRF-safe URL processing, R2 SHA-256 storage, quotas, revisions, generation and background queue semantics; no WordPress file persistence.
- Provide explicit create/replace/delete/reorder/reprocess and bounded upload-intent/finalise endpoints with shop ownership, generation/revision conflict guards and idempotent retries.
- Do not trust uploaded filenames, MIME, URLs or client-supplied shop IDs; enforce safe storage paths and source entitlement before mutations.
- Preserve operational worker behaviour for Shopify sources and fail closed when queue/storage is unavailable.

## Out of Scope

- New retrieval engine, new vector store, client-side direct bucket credentials.
- Other services' implementation code, `docs/decisions/**/_index.md`, and architecture index reconciliation.

## Implementation work items — mandatory

- [ ] Implement **exactly** the named files, routes/models and public DTO fields in the Deterministic implementation specification; do not widen cross-repository ownership.
- [ ] Enforce every declared shop/platform binding, validation boundary, state transition, CAS/idempotency invariant, denial path and privacy restriction.
- [ ] Implement the **specific negative and concurrency test matrix** named in the specification; record actual commands and real results.
- [ ] Prove that affected Shopify behaviour and current ARCH-026/027 Woo onboarding/billing contracts are preserved.
- [ ] Provide a bounded diff, changed-file list, applied migration/Shared package version where applicable, task Completion Report, and clean synchronised implementation/task worktree evidence.

## Cross-repository boundary (common requirements)

- Owning repository: `moda-interact-api`; consume only versioned, accepted cross-repository contracts.
- Hosted Woo identity is the authenticated Shop/installation; no client-controlled `shopId` or Shopify-session authentication. Where browser UI is in scope, transport runs through privileged WordPress REST/PHP with nonce and `manage_woocommerce` capability.
- For merchant display, all 20 supported WordPress UI locales use administrator language with site fallback; this must not change Shop or customer conversation language.
- New or changed externally visible API fields require strict bounded runtime schema validation and a matching OpenAPI/Shared contract owned by the producer.
- No additional external interface is authorised beyond the bounded scope above.

## Dependencies

- `ARCH-035-API-004` must be architect-accepted Complete before this task is claimed.

## Enables

- `ARCH-035-WOOCOMMERCE-004`

## Acceptance Criteria

- [ ] SSRF, oversized/unsupported upload, R2 failure and cross-Shop security tests.
- [ ] Concurrent reorder/replace/reprocess idempotency and quota tests.
- [ ] Evidence existing background processing and Shopify route regressions remain intact.
- [ ] Scope stays within `moda-interact-api` and preserves approved cross-provider and 20-locale contracts.
- [ ] Baseline, task launcher isolation, implementation commit, parent task report and regression evidence are recorded without false claims for unavailable provider services.
- [ ] `git diff --check` and repository-required build/test/lint commands pass or precise blockers are reported.

## Validation

- [ ] Run repository-declared focused test suites plus full typecheck/lint/build where applicable.
- [ ] Run real integration/black-box provider or disposable database evidence when this task's scope includes that dependency; do not substitute a mocked success.
- [ ] Check tenant isolation, disconnected/revoked credential handling, idempotency and requested negative cases.
- [ ] For Woo UI tasks, run `npm run test:i18n`, `npm run i18n:verify:20`, PHP/JS tests, admin-locale test, `npm run plugin-zip` and manual LocalWP workflow.
- [ ] Verify `git diff --check` and submit the canonical Completion Report; leave all `_index.md` files untouched until explicit reconciliation.

## Stop Condition

When requirements/acceptance and required validation are fulfilled, set the task to `review`, populate the Completion
Report and return to `moda_architect`. Do not begin dependent tasks or change other repositories on this task branch.

## Implementation Notes

Keep production responsibilities in small testable modules; prefer provider-neutral existing ownership to Shopify/Woo
service duplication. Return unexpected cross-repository schema or provider-contract gaps to the architect before
widening scope.

## Completion Report

### Status

Not Started.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

Dependencies will be rechecked at task claim time; no generated task document itself creates a branch, provider credential, tested artifact or release.

### Unresolved Issues

None identified beyond documented dependencies/provider gating.

### Architectural Concerns

None reported at definition time.

## Architect Review

### Review Status

Pending implementation.

### Review Notes

No implementation reviewed.

### Reviewed Files

None.

### Validation Reviewed

Not run.

### Architecture Conformance

Pending.

### Follow-up

Return to architect on implementation submission.
