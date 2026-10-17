---
id: ARCH-035-API-016
architecture_id: ARCH-035
title: Manage Woo Merchant Knowledge web sources and ordering
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: in_progress
priority: 44
executor: developer
claimed_at: 2026-10-17T08:56:42Z
attempt: 1
depends_on: [ARCH-035-API-015]
enables: [ARCH-035-WOOCOMMERCE-014]
created: 2026-10-16
updated: 2026-10-17
---

# ARCH-035-API-016 — Manage Woo Merchant Knowledge web sources and ordering

## Architecture

- Parent: `docs/architecture/ARCH-035-woocommerce-merchant-experience-parity.md`, approved 16 October functional knowledge extension.
- Owner: `moda_api`, repository `moda-interact-api`; coordinator: `moda_architect`.


## Objective

Provide authenticated, durable web-page source CRUD, refresh and ordering using the existing Merchant Knowledge lifecycle.

## Context

Shopify’s `merchant-knowledge.server.ts` handles HTTPS URL source creation/edit/refresh/delete/reorder with Shop locks, plan/type limits and source revisions. API-015 owns the canonical read/allowed-source projection.

## Scope

- Implement bounded POST source, PATCH/DELETE source/{id}, POST source/{id}/refresh and PUT order endpoints; publish strict OpenAPI input/output and errors.
- Reuse canonical Shop-scoped source/revision models, active subscription/source-type eligibility and limits, HTTPS/SSRF-safe URL policy and accepted language tags from Shared.
- Enforce atomic Shop lock/ordered positions, generation increments and durable revision creation; preserve durable `PENDING` revisions for Background reconciliation; any optional immediate queue hint must be non-blocking, after commit and architecture-approved.
- Retain configured sources when feature toggle is off; do not queue ingestion while off. Protect against duplicate actions, stale IDs and unexpected provider types.
- Add focused conflict, concurrency, SSRF-protection, entitlement and history tests; preserve Shopify data.

## Out of Scope

- Uploaded file lifecycle or R2 signing (API-017).
- Woo interface/feature-preference commands, new DB schema or another repository’s queue processing.

## Requirements

- Preserve existing tenant, credential, platform, entitlement and transaction boundaries; use the source-inspected contracts and Shared package where applicable, not independently guessed interfaces.
- Fail closed on missing or malformed configuration, unauthorised operations and external provider failures. Record bounded structured logging through `@modainteract/moda-interact-shared/logging` when changing generic application logs.
- Keep production components modular and independently testable; no monolithic files or cross-repository implementation changes. Preserve Shopify runtime and existing Woo merchant Billing, recovery and navigation behaviour.
- If implementation discovers a genuine missing Background/Shared/Gateway capability, stop and return the precise evidence to `moda_architect` rather than extending another repository's scope.

## Work Items

- [ ] Implement bounded POST source, PATCH/DELETE source/{id}, POST source/{id}/refresh and PUT order endpoints; publish strict OpenAPI input/output and errors.
- [ ] Reuse canonical Shop-scoped source/revision models, active subscription/source-type eligibility and limits, HTTPS/SSRF-safe URL policy and accepted language tags from Shared.
- [ ] Enforce atomic Shop lock/ordered positions, generation increments and durable revision creation; preserve durable `PENDING` revisions for Background reconciliation; any optional immediate queue hint must be non-blocking, after commit and architecture-approved.
- [ ] Retain configured sources when feature toggle is off; do not queue ingestion while off. Protect against duplicate actions, stale IDs and unexpected provider types.
- [ ] Add focused conflict, concurrency, SSRF-protection, entitlement and history tests; preserve Shopify data.
- [ ] Add focused positive and negative coverage and complete the required validation/Completion Report.

## Interfaces / Contracts

- POST `/v1/merchant/merchant-knowledge/sources`; PATCH/DELETE `/v1/merchant/merchant-knowledge/sources/{id}`; POST `.../{id}/refresh`; PUT `/v1/merchant/merchant-knowledge/order`.
- Use API-015 projection for post-action refresh; immutable Shop authorization from principal.

## Dependencies

- `ARCH-035-API-015` (must be Complete and architect accepted)

## Enables

- `ARCH-035-WOOCOMMERCE-014`

## Acceptance Criteria

- [ ] Create/edit URL yields correct revision/generation and source state; metadata-only edit avoids spurious revisions.
- [ ] Foreign Shop, malformed/restricted URL, exceeded source count, disabled plan/type and stale source reject with no partial writes.
- [ ] Delete/reorder leaves contiguous deterministic positions; duplicate/retried requests cannot create unintended duplicate durable work; feature-off retains editable configuration.
- [ ] No `_index.md` files or unrelated domains modified; canonical dual-worktree/branch validation evidence recorded in real development workspace.

## Validation

- [ ] Focused unit and disposable PostgreSQL concurrency/transaction tests; durable-pending/reconciliation and dedup tests.
- [ ] Typecheck, lint, build and `git diff --check`.
- [ ] Record concrete commands and results, implementation and parent task branch/commit evidence, canonical physical-isolation/synchronisation evidence, plus deviations and unresolved issues.

## Stop Condition

When this bounded task's Work Items, Acceptance Criteria and required Validation are satisfied, update Completion Report, set `status: review`, return to `moda_architect` and STOP. Do not start tasks listed under Enables.

## Implementation Notes

### Reconciled API-structure handoff (2026-10-16 22:56 snapshot)

- Implement the commands under `src/merchant/merchant-knowledge/` using feature-owned routes, bounded input parsers and small source lifecycle services. Register through `src/composition/merchant.ts`, authenticate through `src/auth/woo-installation/`, and reuse `src/http/` conventions. Use the read projection from API-015; do not change the Woo installation connection router or Shopify source files.
- The current API `package.json` has **no BullMQ dependency or knowledge queue producer**. The existing Background `MerchantKnowledgeReconciliationService` scans durable `PENDING` source revisions and publishes the canonical Shared queue contract. Therefore the required correctness outcome is **transactionally durable revision state plus eventual reconciliation**, not a newly invented synchronous Redis/BullMQ dependency in the API. A best-effort producer is optional only if architecture-approved, non-blocking and backed by the durable reconciler; no Redis/network call inside a Prisma transaction. Tests must demonstrate work remains discoverable when direct queue publication is absent or fails.
- Treat HTTPS/SSRF safety as two separate boundaries: API validates/canonicalises submitted URLs using approved shared rules; existing Background fetch protection remains the authority for outbound DNS/IP/redirect enforcement. Preserve atomic shop lock, order/position integrity, version/generation fencing and idempotency for repeated writes.
- Locate unit and PostgreSQL tests at `tests/unit/merchant/merchant-knowledge/` and `tests/integration/merchant/merchant-knowledge/`. Register new integration validation in `package.json`; author the versioned command contracts in `openapi/merchant-knowledge-v1.yaml` alongside API-015's read contract.

The historical superseded ARCH-035-API-003/004/005 must **not** be revived; this task follows the newly agreed architecture amendment and consumes only approved contract owners. An unimplemented API or feature must never be represented as operational. Do not update any `docs/decisions/**/_index.md` until the developer closes the architectural session.

## Developer Execution Ownership Amendment

On 2026-10-17, the developer invoked `/moda_developer_create ARCH-035-API-016`, explicitly taking over this ready agent-executed task. Execution and completion authority are now `developer`/`developer`; `assigned_agent: moda_api`, repository ownership, scope, dependencies, acceptance criteria and validation requirements are unchanged. Attempt 1 will be claimed by `developer` after canonical parent and implementation worktree synchronization.

## Completion Report

### Status

In Progress — Attempt 1 claimed by developer at 2026-10-17T08:56:42Z. Attempt 0 review history is preserved below.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

The uploaded ZIP represents a portable design baseline, not the developer's current on-disk branches. Confirm source, task status and dependency state with the launcher before execution.

### Unresolved Issues

None evidenced beyond the explicit implementation and test dependencies above.

### Architectural Concerns

Report any cross-repository contract, R2 identity, reconciliation or security mismatch to `moda_architect`.

## Architect Review

### Review Status

Pending.

### Review Notes

Awaiting implementation and validation evidence.

### Reviewed Files

None.

### Validation Reviewed

Not run.

### Architecture Conformance

Pending.

### Follow-up

None until implementation submission.
