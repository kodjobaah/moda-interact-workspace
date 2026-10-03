---
id: ARCH-025-BACKGROUND-013
architecture_id: ARCH-025
title: Extract order completion recovery correlation
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 60
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-025-BACKGROUND-012
enables:
  - ARCH-025-BACKGROUND-014
created: 2026-10-02
updated: 2026-10-03
---

# Extract order completion recovery correlation

## Architecture

Architecture ID: `ARCH-025`

Architecture document: `docs/architecture/ARCH-025-shopify-billing-service-maintainability.md`

Coordinator: `moda_architect`

## Objective

Extract order completion correlation into a bounded service preserving checkout/cart identity rules, pending-candidate cancellation, transient order tombstones and atomic recovery completion/status history.

## Context

Order completion is a distinct race-sensitive lifecycle with strong existing regression coverage. It serializes against candidate materialisation on the checkout key, cancels a matched candidate before durable recovery work, records the order-processed tombstone outside the Prisma completion transaction, and only completes an eligible existing recovery.

## Scope

Authorised implementation surface:

```text
src/services/checkout-recovery.service.ts
src/services/checkout-recovery/order-recovery-correlation.service.ts
tests/unit/services/checkout-recovery/order-recovery-correlation.service.test.ts
```

A directly adjacent repository-internal types file is permitted only where required to keep the extracted capability coherent.

## Out of Scope

candidate-service internals; materialisation; checkout/cart events; outreach; capacity resume; schema/order persistence redesign.

## Requirements

### Common ARCH-025 CheckoutRecovery invariants

- This is a **move-only structural refactor**. Do not change recovery eligibility, outreach policy, billing/capacity economics, candidate/order correlation, queue identity, provider protocol, retry behaviour, authorization, durable lifecycle semantics or CommerceAgent context meaning.
- Preserve the exact compatibility surface from `src/services/checkout-recovery.service.ts`: `CheckoutRecoveryService`, `checkoutRecoveryService`, `MaturedCandidateMaterializationResult`, `CheckoutRefreshResult`, and every current public method: `handleCheckoutCreatedContract`, `materializeMaturedCandidate`, `recordExternalActivity`, `handleCheckoutUpdatedContract`, `handleCartActivityContract`, `handleOrderCompletedContract`, `upsertRecovery`, `attachCustomer`, `resolveRecipient`, `markRecoveryMessageSent`, `handleOrderCompleted`, `handleCheckoutCreated`, `processRecoveryOutreachFollowUp`, `markRecoveryCapacityBlocked`, `resumeCapacityBlockedRecovery`, `getAgentContext`, `getAgentContextForStandaloneConversation`.
- Preserve the constructor `(billingService: RecoveryBillingService = recoveryBillingService)`. Existing workers and Commerce callers continue using the `checkoutRecoveryService` singleton; do not migrate worker entrypoints/callers as part of extraction.
- Extracted modules MUST NOT import `checkout-recovery.service.ts`; dependency direction is façade -> collaborator. Symbols moved out of the façade that are currently exported must be compatibility re-exported from it.
- Collaborator constructors are inert wiring only. Do not perform Prisma/provider/Redis/queue/environment I/O or eager model access during construction.
- Any extracted collaborator that performs recovery billing MUST receive and reuse the exact `RecoveryBillingService` instance supplied to the `CheckoutRecoveryService` constructor. Do not silently fall back to the module singleton when a caller supplied a test/custom billing service.
- Continue reusing canonical owners: `RecoveryBillingService`, `RecoveryOutreachAttemptService`, `recoveryOutreachFollowUpService`, `RecoveryPolicyService`, `PendingRecoveryCandidateService`, `ShopExecutionEligibilityService`, `AbandonedCheckoutLookupService`, `RecoveryCapacityResumeService`, `OutboundWhatsAppAdmissionService`, `ConversationService`, `ConversationMessageService`, and `WhatsAppTemplateSelectorService`. Do not duplicate their logic.
- There remains exactly one outbound WhatsApp provider path through `OutboundWhatsAppAdmissionService`; do not create a direct Meta/provider send workflow. Deterministic outreach idempotency remains `recovery-outreach:<attemptId>`.
- Preserve all provider/network versus Prisma transaction boundaries, checkout-scoped lock boundaries, order-processed tombstone timing, status-guarded `updateMany` predicates, generation ordering and post-commit queue/provider ordering exactly. Do not move external calls into a Prisma transaction.
- Preserve stale/duplicate replay behaviour and terminal-state non-reopening. Do not convert durable capacity blocking into in-memory state.
- Preserve current data-source trust: webhook candidate/update basket/customer fields must not become durable recovery snapshot data where current Shopify lookup is authoritative.
- Preserve the integrated ARCH-024 `RecoveryAgentContext` contract: canonical `shopId`, shop domain, conversation ownership checks, language metadata and bounded history/current-message semantics.
- Do not introduce a new generic logger. If diagnostics are added, use the canonical Shared structured logger and bounded identifiers only; do not log whole checkout/customer/provider/message payloads.
- These post-ARCH-024 regression assets are frozen and MUST remain byte-for-byte unchanged:
  - `tests/unit/services/matured-candidate.materialization.test.ts` — SHA-256 `28d629008a63e3fc554dd15bd268c52a73287169832f40f63f5d02c0c3bcafcb`
  - `tests/unit/services/checkout-refresh.test.ts` — SHA-256 `3330367841b6a35e5cdb15c6f8619b529b74336834da8c307d66c16e3202a36f`
  - `tests/unit/services/order-recovery-correlation.test.ts` — SHA-256 `7b3d3020f822ee1bc514de7aee9f15245f3d86cd6dacd6fee6b1f892a6516dbf`
  - `tests/unit/services/checkout-recovery.capacity-resume.test.ts` — SHA-256 `8c11db2f98681899742579db2766527ec5f26b5dfdf15a264551eecea9a115e1`
- Add separate focused tests for each extracted owner. Do not move assertions out of frozen files, skip tests, weaken assertions or change expected behaviour to make an extraction pass.
- Full `npm test` must introduce no regression. If a synchronized baseline failure exists, follow the durable baseline protocol; do not silently redefine expected failures inside the task.

### R1 — correlation safety

Move the repository-internal `RecoveryOrderCompletionInput` shape with the order-correlation owner while keeping `handleOrderCompleted(...)` compatible through the façade.

Customer identity alone remains insufficient. Missing checkout+cart correlation returns `ignored/missing-correlation`. Preserve the current shop gate exactly: resolve `{ id, status }` by domain and proceed when the Shop itself is `ACTIVE`; do **not** replace this with `ShopExecutionEligibilityService` subscription gating. Order completion is terminal safety bookkeeping and must continue for an ACTIVE Shop even when its subscription is FROZEN. Cart-only orders first resolve the indexed candidate solely to recover checkout scope; if none exists they remain `discarded/no-checkout-token`.

### R2 — checkout serialization and tombstone order

Retain `withCheckoutLock(shopId, checkoutToken)` before candidate cancellation/recovery completion. Inside the lock, resolve candidate first. If found, cancel it, then mark the order processed and return `cancelled-candidate`. If not found and a checkout token exists, mark the order processed **before** the Prisma recovery transaction so in-flight materialisation is suppressed. Do not move the tombstone into PostgreSQL.

### R3 — durable completion

The Prisma transaction continues to load the latest recovery by generation/id, ignore terminal `COMPLETED/EXPIRED/CANCELLED`, CAS-update only `DETECTED/MESSAGE_SENT/ENGAGED` to `COMPLETED`, clear admission block fields and create status history in the same transaction. Preserve event completion timestamp fallback and metadata/source strings exactly.

### R4 — no new durable order model

Do not persist unrelated orders or introduce schema/state solely for this refactor.

## Work Items

- [x] Extract order correlation and adapt `handleOrderCompletedContract`/`handleOrderCompleted` façade delegates.
- [x] Preserve checkout lock/tombstone/transaction order exactly.
- [x] Add focused tests for checkout and cart correlation, candidate cancellation, terminal/idempotent completion and tombstone-without-recovery.
- [x] Prove frozen order suite remains byte-identical and passes.

## Interfaces / Contracts

Repository-internal extraction only. The public worker/application contract remains `CheckoutRecoveryService` / `checkoutRecoveryService`; canonical adjacent service contracts are consumed rather than redefined.

## Dependencies

- `ARCH-025-BACKGROUND-012`

## Enables

- `ARCH-025-BACKGROUND-014`

## Acceptance Criteria

- [x] Order completion has one owner and retains current race-safety semantics.
- [x] Order tombstones remain transient candidate-service state outside the Prisma completion transaction.
- [x] Status history remains atomic with successful recovery completion.
- [x] No new durable order state/schema is introduced.

## Validation

- [x] `npm run prisma:generate`
- [x] `node -e "const fs=require('node:fs'),c=require('node:crypto');const e={'tests/unit/services/matured-candidate.materialization.test.ts':'28d629008a63e3fc554dd15bd268c52a73287169832f40f63f5d02c0c3bcafcb','tests/unit/services/checkout-refresh.test.ts':'3330367841b6a35e5cdb15c6f8619b529b74336834da8c307d66c16e3202a36f','tests/unit/services/order-recovery-correlation.test.ts':'7b3d3020f822ee1bc514de7aee9f15245f3d86cd6dacd6fee6b1f892a6516dbf','tests/unit/services/checkout-recovery.capacity-resume.test.ts':'8c11db2f98681899742579db2766527ec5f26b5dfdf15a264551eecea9a115e1'};for(const [p,x] of Object.entries(e)){const h=c.createHash('sha256').update(fs.readFileSync(p)).digest('hex');if(h!==x){console.error(p,h);process.exitCode=1}else console.log(p,h)}" prints all expected SHA-256 values
- [x] `git diff -- tests/unit/services/matured-candidate.materialization.test.ts tests/unit/services/checkout-refresh.test.ts tests/unit/services/order-recovery-correlation.test.ts tests/unit/services/checkout-recovery.capacity-resume.test.ts` is empty
- [ ] `npm test -- tests/unit/services/matured-candidate.materialization.test.ts tests/unit/services/checkout-refresh.test.ts tests/unit/services/order-recovery-correlation.test.ts tests/unit/services/checkout-recovery.capacity-resume.test.ts` passes (77/78; frozen materialization language-context assertion fails)
- [x] `npm test -- tests/unit/runtime/entrypoint-isolation.test.ts` passes (10/10)
- [ ] `npm test` introduces no regression (13 failed tests and one failed suite; details recorded below)
- [x] `npm run build` succeeds
- [x] `git diff --check` passes
- [x] `npm test -- tests/unit/services/checkout-recovery/order-recovery-correlation.service.test.ts` passes (9/9)

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, finish the Completion Report, return control to `moda_architect` and **STOP**. Do not begin the enabled or adjacent ARCH-025 Background task.

## Implementation Notes

None

## Completion Report

### Status

Review

### Files Changed

- `src/services/checkout-recovery.service.ts`
- `src/services/checkout-recovery/order-recovery-correlation.service.ts`
- `tests/unit/services/checkout-recovery/order-recovery-correlation.service.test.ts`

### Work Completed

- Moved `RecoveryOrderCompletionInput` and order completion correlation into `OrderRecoveryCorrelationService`; the existing façade method remains a delegate and `handleOrderCompletedContract` remains unchanged.
- Preserved ACTIVE-Shop-only gating, cart-only candidate lookup, checkout lock, candidate cancellation, transient tombstone timing, latest-generation lookup, guarded completion update, and atomic status-history creation. No durable order state or schema changes were introduced.
- Added nine direct service tests for missing/cart correlation, cancellation and lock order, ACTIVE shop with FROZEN subscription, completion/history ordering, tombstone without recovery, terminal states and lost-update handling.

### Validation Results

- PASS: `npm run prisma:generate`.
- PASS: `npm run build`.
- PASS: extracted-owner suite, 9/9; frozen order-correlation façade suite, 10/10; combined order-correlation suites, 19/19.
- PASS: entrypoint isolation, 10/10.
- PASS: all four frozen asset SHA-256 values match and `git diff` for those assets is empty.
- PASS: `git diff --check`.
- FAIL: required four-suite frozen group, 77/78. `matured-candidate.materialization.test.ts` expects Shopify language metadata `fr-CA`/`shopify` but receives null values. Its frozen hash matches and this task does not alter materialization behavior.
- FAIL: full `npm test`, 1,546 passed, 38 skipped, 13 failed tests across six files, plus one suite collection error. Failures include three billing-reconciliation assertions, the same materialization language assertion, one Commerce host deadline assertion, four PostgreSQL translation integration tests unable to connect to `localhost:5432`, four observability-startup timeouts, and `tests/unit/commerce/evidence.test.ts` missing the fixture under the ARCH-020-BACKGROUND-002 task worktree path. These failures are outside B013's changed behavior and are not recorded under an existing baseline ID.

### Execution Evidence

- Physical worktree isolation: canonical workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-025-BACKGROUND-013` on `task/ARCH-025-BACKGROUND-013`; implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-025-BACKGROUND-013` on `task/ARCH-025-BACKGROUND-013`.
- Shared workspace checkout switched/mutated: no. Shared implementation checkout switched/mutated: no. Another task worktree reused: no.
- Start synchronization: parent remote task branch fast-forwarded `not-needed`, parent `origin/main` incorporated `already-current`; implementation remote task branch fast-forwarded `not-needed`, implementation `origin/main` incorporated `already-current`.
- Recursive implementation submodules: sync and update/init passed; `database` initialized at `cfeeb12456b4e05067a96857a8c47837d7e33bbd`.
- Launcher claim: attempt 1, executor `copilot`; claim commit `659095f1d3885716b240d3f64e19d3fbb03658f4` was committed and pushed.
- Implementation commit `b7386ff` was pushed to `origin/task/ARCH-025-BACKGROUND-013`; implementation worktree is clean and tracks that task branch.

### Deviations

- The required frozen group and full test suite are not fully green due to the failures listed under Validation Results. No unrelated test, baseline, fixture or production behavior was changed to mask them.

### Assumptions

None

### Unresolved Issues

- Architect disposition is requested for the existing materialization language-context failure, the other full-suite failures, the unavailable local PostgreSQL service, and the missing ARCH-020 task-worktree fixture. No matching durable baseline ID was found in the workspace development baseline.

### Architectural Concerns

None. The extraction adds no cross-repository dependency or durable order state.

## Architect Review

### Review Status

Accepted — Attempt 1

### Review Notes

- Reviewed implementation commit `b7386ff7e257d753f5bc911ee114c0f5dc2baccb` and parent report commit `f887a710235af5603c38c4a07e607e7f2d8c1d62` as published on their `task/ARCH-025-BACKGROUND-013` branches.
- The extraction is move-only: `OrderRecoveryCorrelationService` owns the existing order-completion lifecycle while `CheckoutRecoveryService.handleOrderCompleted(...)` remains the compatibility delegate. Constructor wiring is inert and the collaborator does not import the façade.
- Correlation safety is preserved exactly: customer identity alone is rejected; the Shop lookup remains `{ id, status }` by domain and gates only on `Shop.status === ACTIVE`; cart-only orders use the transient indexed candidate solely to recover checkout scope. No subscription eligibility gate was introduced.
- Checkout serialization and tombstone ordering are unchanged: cart-only scope resolution precedes `withCheckoutLock`; inside the lock candidate resolution occurs first; matched candidates are cancelled before `markOrderProcessed`; unmatched checkout-token orders record the tombstone before entering the Prisma completion transaction.
- Durable completion remains atomic: latest recovery is selected by `generation desc, id desc`; `COMPLETED` / `EXPIRED` / `CANCELLED` are not reopened; only `DETECTED` / `MESSAGE_SENT` / `ENGAGED` CAS to `COMPLETED`; admission-block fields are cleared and status history is written in the same transaction with the existing source, reason, metadata and completion-time fallback. No durable order model/schema was added.
- The Completion Report statement that no matching durable baseline ID was found is superseded by Architect review: the three billing-reconciliation failures, matured-candidate language assertion, four PostgreSQL translation failures and missing ARCH-020 evidence fixture are the exact identities already documented by `ARCH025-BACKGROUND-TEST-001`.
- The remaining five full-suite failures are not B013 regressions. `tests/integration/commerce/host.test.ts` imports only Commerce host/grant code and its deadline assertion cannot execute B013 code. The four `observability-startup` probes spawn only `./observability/<profile>.mjs` plus the Shared observability runtime; they do not execute `checkout-recovery.service.ts` or `OrderRecoveryCorrelationService`. These failures are not added to the durable Background baseline.

### Reviewed Files

- `src/services/checkout-recovery.service.ts`
- `src/services/checkout-recovery/order-recovery-correlation.service.ts`
- `tests/unit/services/checkout-recovery/order-recovery-correlation.service.test.ts`

### Validation Reviewed

- `npm run prisma:generate` — passed.
- `npm run build` — passed.
- Extracted-owner suite — 9/9 passed.
- Frozen order-correlation façade suite — 10/10 passed; combined order-correlation coverage 19/19.
- `tests/unit/runtime/entrypoint-isolation.test.ts` — 10/10 passed.
- All four frozen CheckoutRecovery SHA-256 values match and frozen-file diff is empty.
- Required frozen aggregate — 77/78; the sole failure is the unchanged matured-candidate language assertion documented by `ARCH025-BACKGROUND-TEST-001`.
- Full `npm test` — 1,546 passed / 38 skipped / 13 failed plus one collection failure. Eight failed identities plus the collection failure are covered by `ARCH025-BACKGROUND-TEST-001`; the Commerce deadline and four observability-preload failures are execution-path independent from B013 and therefore do not block this extraction.
- `git diff --check` — passed.

### Architecture Conformance

Accepted. BACKGROUND-013 establishes one bounded owner for order completion correlation without changing checkout/cart identity, candidate cancellation, transient tombstone authority, lock boundaries, transaction boundaries, recovery terminal-state behavior or status-history semantics.

### Follow-up

`ARCH-025-BACKGROUND-014` is promoted to Ready. The unrelated Commerce deadline and observability-preload failures remain outside B013 ownership and are not incorporated into `ARCH025-BACKGROUND-TEST-001` without same-environment baseline proof.
