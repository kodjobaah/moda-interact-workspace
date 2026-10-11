---
id: ARCH-035-API-004
architecture_id: ARCH-035
title: Expose Woo Merchant Knowledge source catalogue
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 83
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables:
  - ARCH-035-API-005
created: 2026-10-11
updated: 2026-10-11
---

# ARCH-035-API-004: Expose Woo Merchant Knowledge source catalogue

## Architecture

- Architecture ID: `ARCH-035`
- Architecture document: `docs/architecture/ARCH-035-woocommerce-merchant-experience-parity.md`
- Coordinator: `moda_architect`
- Source baseline: uploaded `moda-interact-workspace(20261011-185536).zip`; task is a portable definition, not a claimed/materialised worktree.

## Objective

Expose plan-entitled Merchant Knowledge sources, current revision/processing state, limits and failure summaries through the Woo installation boundary.

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

**Files:** `src/merchant/knowledge/{contract,read.service,routes}.ts`, tests and
`openapi/woocommerce-merchant-knowledge-v1.yaml`, thin registration. Existing authoritative schema:
`MerchantKnowledgeSource`, `MerchantKnowledgeSourceRevision`, `MerchantKnowledgeUploadedAsset`,
`MerchantKnowledgePurpose`, `MerchantKnowledgeDataFormat`; no migration or knowledge vector/embedding API exposure.

**GET `/v1/merchant/knowledge`:** exact `schemaVersion=1`; `revision` deterministic digest of shop-owned source
IDs/currentGeneration/order/status; `quota={limit,used,available}` from existing ARCH-023 plan/feature entitlement
policy; `purposes:[{id,label}]`; `formats:[{id,kind}]`;
`sources:[{id,name,position,languageTag,purposeId,dataFormatId,currentGeneration,latestRevision:{generation,status,requestedAt,completedAt,failureCode,requestedUrl,contentUnits,truncated}|null,originalFileName|null}]`.
Order by `(position,id)`; max 100 displayed sources; do not return chunks, embeddings, normalized content, objectKey,
R2 URLs, credentials, raw asset hash or cross-Shop history. Distinguish PENDING/PROCESSING/READY/FAILED, plan-blocked
and empty catalogue states; no phantom quota grant.

**Constraints:** derive shop from bearer and validate active Woo installation; inspect plan feature's actual
entitlement, not React-supplied limits; reading pending source does not advance a revision or dispatch work. The
`languageTag` belongs to knowledge retrieval settings, not WordPress administrator UI locale or
`Conversation.languageTag`. Tests: Free limit, rejected foreign sources, missing revision, revision status
projection, quotas after replacement, blocked plan, revoked credential, no R2 leakage, Shopify regressions.

## High-level scope (non-authoritative summary)

- Reuse existing Shop-owned Merchant Knowledge models and background reconciliation; do not fork vector/chunk/revision tables.
- Provide bounded read API for URL and uploaded-file source metadata, status, ordering, quotas, language and server-side entitlement.
- Never return raw uploaded files, R2 secrets, internal embeddings or foreign-Shop sources; distinguish empty, blocked and processing states.
- Keep conversation knowledge-language policy separate from administrator UI translation.

## Out of Scope

- Unrelated Shopify or Woo Billing feature changes; changing another repository in this task.
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

No blocking task dependency beyond the accepted ARCH-026/027 foundations in the stated snapshot. Confirm current compatible package/DB pins before claiming.

## Enables

- `ARCH-035-API-005`

## Acceptance Criteria

- [ ] Tenant isolation, plan/feature gating, source-state and bounded pagination tests.
- [ ] Proof existing Merchant Knowledge background consumers can operate for Woo Shops or identify a precise follow-on blocker.
- [ ] Contract/typecheck/Shopify knowledge regression validation.
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
