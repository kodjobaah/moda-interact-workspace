---
id: ARCH-035-SYSTEM-TEST-001
architecture_id: ARCH-035
title: Certify Woo merchant surfaces and Shopify parity
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-035-WOOCOMMERCE-001
  - ARCH-035-WOOCOMMERCE-002
  - ARCH-035-WOOCOMMERCE-003
  - ARCH-035-WOOCOMMERCE-004
  - ARCH-035-WOOCOMMERCE-005
  - ARCH-035-WOOCOMMERCE-006
enables: []
created: 2026-10-11
updated: 2026-10-11
---

# ARCH-035-SYSTEM-TEST-001: Certify Woo merchant surfaces and Shopify parity

## Architecture

- Architecture ID: `ARCH-035`
- Architecture document: `docs/architecture/ARCH-035-woocommerce-merchant-experience-parity.md`
- Coordinator: `moda_architect`
- Source baseline: uploaded `moda-interact-workspace(20261011-185536).zip`; task is a portable definition, not a claimed/materialised worktree.

## Objective

Certify Support, editable recovery settings, feature preferences, knowledge, promotions and usage with trusted Woo installation and platform billing records.

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

**Files:** add a bounded `src/arch035/merchant-surfaces/{fixture,executor,assertions,scenario}.js` module group plus
`test/arch035/merchant-surfaces.test.js` and selected entries in existing `src/scenario-catalogue.js`; reuse
`src/harness/{runner,evidence,redaction}.js`, disposable PostgreSQL/Redis. Do not create one 300+ line all-in-one
test file.

**Matrix:** (1) Support send/read/translation and duplicate actionId; (2) Recovery policy save, 0/10080 bounds, stale
revision and active Admin override; (3) immutable vs optional features across two plan mappings; (4) Knowledge HTTPS
URL, R2 upload intent/finalize, queue failure/reprocess/quota; (5) Promotion eligibility selection
expiry/concurrency; (6) Usage Free lifetime and paid 30-day periods. For each: active Shop A/admin A succeeds, Shop B
data is inaccessible, revoked installation/invalid WP nonce/contributor is denied, locale admin preference vs store
fallback is isolated, disconnect clears stale UI, Shopify counterpart remains unchanged. Exercise **real WordPress
PHP proxy + hosted API + DB**, not only JS mocks, and use 20 translation checks.

**Evidence:** scenario IDs `ARCH035-MERCHANT-01..06`, per-scenario JSON with source commit SHA, API status/payload
redacted, DB pre/post queries, assertions, cleanup; zero leaked Docker resources; classify provider SaaS paid
scenarios BLOCKED not PASS if Woo credentials absent. Parent task must list which prerequisite tasks were actually
accepted, not assume them from ready state.

## High-level scope (non-authoritative summary)

- Provide disposable authenticated WordPress+Moda fixtures and isolate executors, fixtures, assertions and evidence under existing system-test architecture.
- Exercise privilege/nonce failure, tenant separation, locale changes, disconnect/credential rotation, stale responses and invalid write attempts.
- Cover Shopify regression for reused support/feature/knowledge/promotion/usage policy and 20 WordPress admin locales.
- Do not label missing Woo billing SaaS credentials as a successful paid-provider certification.

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

- Owning repository: `moda-interact-system-test`; consume only versioned, accepted cross-repository contracts.
- Hosted Woo identity is the authenticated Shop/installation; no client-controlled `shopId` or Shopify-session authentication. Where browser UI is in scope, transport runs through privileged WordPress REST/PHP with nonce and `manage_woocommerce` capability.
- For merchant display, all 20 supported WordPress UI locales use administrator language with site fallback; this must not change Shop or customer conversation language.
- New or changed externally visible API fields require strict bounded runtime schema validation and a matching OpenAPI/Shared contract owned by the producer.
- No additional external interface is authorised beyond the bounded scope above.

## Dependencies

- `ARCH-035-WOOCOMMERCE-001` must be architect-accepted Complete before this task is claimed.
- `ARCH-035-WOOCOMMERCE-002` must be architect-accepted Complete before this task is claimed.
- `ARCH-035-WOOCOMMERCE-003` must be architect-accepted Complete before this task is claimed.
- `ARCH-035-WOOCOMMERCE-004` must be architect-accepted Complete before this task is claimed.
- `ARCH-035-WOOCOMMERCE-005` must be architect-accepted Complete before this task is claimed.
- `ARCH-035-WOOCOMMERCE-006` must be architect-accepted Complete before this task is claimed.

## Enables

None.

## Acceptance Criteria

- [ ] Independent black-box and integration evidence for each six non-recovery surfaces.
- [ ] No mock-only certification, no 300-line catch-all test files, reproducible evidence paths.
- [ ] WP plugin ZIP and API/service version pin recorded.
- [ ] Scope stays within `moda-interact-system-test` and preserves approved cross-provider and 20-locale contracts.
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
