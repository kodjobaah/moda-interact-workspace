---
id: ARCH-048-BACKGROUND-003
architecture_id: ARCH-048
title: Implement Woo maturity and first-recovery admission service
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: review
priority: 40
executor: developer
claimed_at: 2026-10-24T01:11:20Z
attempt: 1
depends_on:
- ARCH-048-BACKGROUND-006
- ARCH-046-BACKGROUND-001
- ARCH-045-BACKGROUND-005
enables:
- ARCH-046-BACKGROUND-002
- ARCH-048-BACKGROUND-005
created: '2026-10-23'
updated: 2026-10-24
---

## Execution Ownership Amendment

On 2026-10-24, the developer explicitly invoked `/moda_developer_create ARCH-048-BACKGROUND-003` for this ready agent-owned task. Execution is transferred to the developer for the next attempt; the assigned agent remains `moda_background`, and completion is developer-controlled.

# ARCH-048-BACKGROUND-003 — Implement Woo maturity and first-recovery admission service

## Architecture

Architecture ID: `ARCH-048`

Architecture document: `docs/architecture/ARCH-048-woocommerce-checkout-recovery-pipeline.md`

Coordinator: `moda_architect`

Original portable architect definition prepared from the 23 October 2026 snapshot (proposal iteration 5). The developer subsequently materialised and claimed this task as **execution Attempt 1** on 24 October 2026. Background implementation commit `95c108e` was pushed to `origin/task/ARCH-048-BACKGROUND-003`; this submission does **not** represent architect acceptance, parent-task-branch publication or merge to `main`. The developer reports `ARCH-046-BACKGROUND-004` complete after the original snapshot; do not reopen it.

## Objective

Implement `WooRecoveryAdmissionService` that evaluates a mature Woo candidate against successfully received checkout/order evidence, the existing durable recovery record and current exact-recipient consent, and **creates only the first `CheckoutRecovery` row**, never an attempt, charge or message.

## Context

Shopify's present `RecoveryMaterializationService` invokes a Shopify provider checkout lookup and its downstream initiating path can send immediately. Woo must use a provider-specific admission adapter over reusable shop/DB/consent primitives, not trick Shopify's provider resolver with Woo event data. BG006 defines the candidate, guard and admission interfaces. This task implements against injected candidate/terminal adapters and test fixtures, independently of BG001/BG002 concrete services and the Woo producer enhancements. It provides the pre-INSERT consent decision seam consumed by pending ARCH-046-BACKGROUND-002; BG005 wires the actual maturity worker later.

## Scope

- Own `src/services/woocommerce-recovery/woo-recovery-admission.service.ts` and focused tests. Do not redefine BG006 interfaces; add a narrow reusable row-only insert helper only if a genuinely platform-neutral existing helper is insufficient. Do not modify Shopify-only lookup paths to pretend Woo live state is verified.
- Expose `evaluateMatured(candidate: WooPendingCandidate, context): Promise<WooAdmissionOutcome>` returning discriminated outcomes including `created { recoveryId }`, `already-exists`, `superseded`, `denied { reason }`, and `deferred { reason }`. Only `created` may be passed to outbound orchestration.
- Require an explicit Woo-source candidate conforming to BG006 (BG001 provides it at runtime), authenticate shop/platform and installation, check merchant delay from last **successfully received** activity and current bounded snapshot (real nonempty items, amount/currency, exact Customer/CustomerPhone matching); reject incomplete/stale/ambiguous evidence.
- Under shared checkout-scoped lease, compare latest event watermark and BG002 terminal order policy, read existing `CheckoutRecovery` with/without candidate job, and recheck before row INSERT. A `MESSAGE_SENT`/`ENGAGED`/terminal existing row cannot lead to a second initial recovery, including EXPIRED/re-entry without separately approved generation policy.
- Call existing ARCH-046-BACKGROUND-001 current exact-recipient marketing permission/STOP/suppression **before INSERT**; invalid/unavailable/revoked/ambiguous identity or consent yields typed denial/defer and zero row. Prepare an injected denied-admission result hook consumed by ARCH-046-BACKGROUND-002 for one idempotent merchant Support notice without implementing the notice here.
- Create existing `CheckoutRecovery` and applicable `CheckoutRecoveryStatusHistory` transactionally and idempotently under the existing unique `(shopId,checkoutToken,generation)` contract; preserve correct customer, basket and value snapshot. Return only the created recovery ID, never dispatch inline.
- Reconcile crash/retry between candidate maturity and insert; prevent concurrent duplicate generation, idempotent `already-exists`, and do not call Background→Moda API or WooCommerce.

## Out of Scope

- No worker modification, Action Scheduler, billing, initial `RecoveryOutreachAttempt`, WhatsApp, Support notice implementation, Woo guest session read or new Moda database schema.
- No Shopify customer resolver, Shopify abandoned checkout lookup or direct invocation of existing send-and-bill initialisation.

## Requirements

- **Service boundary:** computes admission decision and row-only creation; all sending/billing is BG004 and all wiring BG005.
- Absent/expired BullMQ job is never proof that no recovery exists; check PostgreSQL under transaction/concurrency discipline.
- One initial generation per Woo checkout lineage. If existing status suggests re-entry, fail closed pending separately approved policy rather than auto-increment generation.
- Current consent for exact canonical customer phone and local STOP supersede stale positive evidence. Never create a consent-wait recovery row.
- No claim of live checkout verification: latest *received* event is all that can be known under outbound-only design.
- An accepted `created` result is not a guarantee of send; BG004 performs independent irreversible dispatch guards.

### Mandatory shared logging and failure propagation

- Use `StructuredLogger` from `@modainteract/moda-interact-shared/logging`, injected from the existing process logger (a small child logger with fixed service context is permitted). Follow `docs/observability/shared-logging.md`; do not implement a new logger, serialize JSON manually or log using `console.*`.
- Record `woocommerce.recovery.admission.evaluated` for completed `created`/`already-exists`/`superseded`/`denied` decisions, `woocommerce.recovery.admission.deferred` for **confirmed** expected deferrals and `woocommerce.recovery.admission.failed` for unexpected errors. Use only safe `shopId`, `eventId`/`jobId` where present, `recoveryId` where present, operation, outcome and bounded reason; no raw checkout key, phone/customer data, session token, cart contents, secret or unsanitized provider payload.
- A typed `denied` or `deferred` outcome requires actual evidence from eligibility/consent/state checks (including a dependency explicitly returning an unavailable state). It must **never** be manufactured by catching exceptions from consent readers, PostgreSQL, transactions, candidate/terminal readers, Redis or hooks. Unexpected thrown errors must be logged with bounded context and **re-thrown**; preserving the same error/cause enables Background's BullMQ failure/retry path. No empty catches, best-effort detached promises, ignored rejected results or fabricated `already-exists` on database failure.
- If a transaction or post-transaction operation fails, retain idempotent retry semantics and surface the error; no initial send/charge may be triggered from an unconfirmed INSERT. Shared logger sink-failure isolation does not change the admission result or justify swallowing business exceptions.

## Work Items

- [x] Implement injected service with typed admission result; isolate all provider-specific snapshot/recipient resolution from Shopify-specific functions.
- [x] Exercise default current-consent gating and add stable denial result hook for ARCH-046-BACKGROUND-002 without writing its Support-message logic.
- [x] Test two workers, duplicate delayed job, missing job + existing row, missing items/customer, wrong shop, terminal order, STOP/revocation and consent reader unavailable.
- [x] Prove created service result alone does not enqueue/send/charge; preserve Shopify materialisation tests.
- [x] Add shared-logger instrumentation for real admission decisions, explicit deferrals and unexpected failures, without exposing customer/checkout payloads.
- [x] Test thrown consent/STOP reader, terminal reader, transaction, database and Redis errors; assert rejection propagation, no fabricated denial/defer/creation and no outbound enqueue.

## Interfaces / Contracts

**Owned capability interface (canonical definition in BG006):**

```ts
interface WooRecoveryAdmissionEvaluator {
  evaluateMatured(candidate: WooPendingCandidate, context: { jobId?: string }): Promise<WooAdmissionOutcome>;
}
type WooAdmissionOutcome =
  | { kind: "created"; recoveryId: string }
  | { kind: "already-exists"; recoveryId: string; status: string }
  | { kind: "superseded" | "denied" | "deferred"; reason: string };
```

**Inputs:** BG006 `WooPendingCandidate` and injected `WooObservedOrderStateReader`/coordination interfaces with test fakes; active tenant/installation, shop recovery policy, exact customer/phone and ARCH-046 current marketing consent reader. BG005 later connects accepted BG001/BG002 adapters.

**Output contract to ARCH-046-BACKGROUND-002:** stable denial reasons and an injectible before-INSERT consent-policy/admission-result hook; ARCH-046 owns deduplicated merchant Support notice implementation. BG004 sees only a committed recoveryId. No public cross-service API is added.

**File boundary:** own Woo admission service/adapter, optional reusable *row-only* DB helper, own tests. Do not edit checkout/order workers, pending candidate worker, existing Shopify-only lookup service, initial-send services or `src/entrypoints/*`.

## Dependencies

- `ARCH-048-BACKGROUND-006`
- `ARCH-046-BACKGROUND-001`
- `ARCH-045-BACKGROUND-005`

## Enables

- `ARCH-046-BACKGROUND-002`
- `ARCH-048-BACKGROUND-005`

## Acceptance Criteria

- [x] First-insert occurs exactly once for eligible shop + Woo checkout lineage; no side effects if an existing first recovery or attempt is found even after job deletion.
- [x] No INSERT/attempt/bill/send for missing/ambiguous recipient, empty/oversized basket evidence, placed/paid/cancelled order, immature candidate, STOP or non-GRANTED current marketing consent.
- [x] Explicit row-only result interface enables ARCH-046 missing-consent notices and BG004 outbound service; no premature worker wiring.
- [x] Concurrency and production historical Shopify behaviours pass regressions.
- [x] Unexpected dependency or transaction exceptions reject `evaluateMatured` and remain diagnosable; expected consent denial and explicit unavailable/ambiguous states still return their specified typed outcomes.
- [x] Logs provide safe shop/job/recovery correlation and distinguish denied/deferred from thrown failures without PII or secret leakage.

## Validation

- [x] Focused unit tests with injected current consent and order state/clock; rejection matrix and no network sends.
- [ ] Postgres/Redis idempotency tests for materialise/cancel/update races and existing-sent/no-candidate path.
- [x] Shopify recovery admission regressions, repository-declared typecheck/lint and `git diff --check`.
- [x] Run fault-injection unit tests with injected `StructuredLogger` and rejected consent/database/Redis dependencies; verify rejection, idempotent retry behaviour and absence of false `created`/`denied`/`deferred` results.

## Stop Condition

After completing only the task's scoped service, tests, Acceptance Criteria and Validation, populate the Completion Report, set status to `review`, return control to `moda_architect`, and **STOP**. Do not wire a worker or start a dependent task. Record launcher-prepared parent and implementation dedicated worktree paths, physical isolation, synchronisation, submodule state and both task branch revisions in the Completion Report.

## Implementation Notes

ARCH-046-BACKGROUND-002 may integrate its notice/consent decision implementation directly against this service seam after this task is architect-accepted. That task is distinct from worker composition (BG005).

- Use `/moda-task` launcher preparation and the actual task worktrees on the developer's machine; a portable ZIP is not an execution claim or Git baseline.
- Respect service/file ownership and cross-repository boundaries in this task and the parent architecture. Do not modify `docs/decisions/**/_index.md` before explicit architect session closure.
- Apply the mandatory shared structured-logging and exception-propagation contract in Requirements; inspect the repository `package.json`, use existing domain infrastructure, run only relevant declared checks and record exact evidence (including checks that cannot run).
- All checkout/session/phone/order logging must exclude raw PII, secrets, session tokens and full basket data; record bounded reason codes and structured correlation IDs only.

## Completion Report

### Status

Ready for Review — developer-executed **Attempt 1**, claimed at `2026-10-24T01:11:20Z`. Implementation has been committed and pushed; architect review and explicit developer completion have **not** occurred.

### Files Changed

Implementation repository (`moda-interact-background`, commit `95c108e`):

- `src/services/woocommerce-recovery/woo-recovery-admission.service.ts`
- `src/services/woocommerce-recovery/woo-recovery-admission-evidence.ts`
- `tests/unit/services/woocommerce-recovery/woo-recovery-admission.service.test.ts`
- `tests/integration/woo-recovery-admission.integration.test.ts`

Parent workspace: this `BACKGROUND-003-admit-and-create-first-woo-recovery.md` task report and submission-state update only. No domain `_index.md`, parent architecture, worker wiring or implementation submodule gitlink is authorised by this submission.

### Work Completed

- Implemented injected `WooRecoveryAdmissionService.evaluateMatured` using the BG006 contracts and received Woo evidence, with tenant/installation, merchant delay, candidate watermark, order outcome, valid basket, recipient identity, and exact-recipient current consent checks.
- Checked existing durable recovery (all generations) independently of BullMQ candidate existence, and rechecked before the single generation-1 `DETECTED` row plus initial `CheckoutRecoveryStatusHistory` transaction. Returns typed outcomes only; creates no `RecoveryOutreachAttempt`, credit reservation or outbound message.
- Added a transaction-time consent/STOP fence, proven-unique-constraint collision recovery, and an awaited injectable denied-admission hook for ARCH-046-BACKGROUND-002. Unanticipated reader, database, Redis/coordinator, transaction and hook errors are logged and rethrown.
- Used `@modainteract/moda-interact-shared/logging` structured logs with bounded outcome/reason and hashed event/job correlation, not raw checkout tokens, phone numbers, customer fields or basket content.
- Implemented 28 unit cases and two disposable PostgreSQL/Redis integration cases. The two changes supplied as implementation patch revisions (initial implementation and TypeScript narrowing/lint correction) were committed together in developer workflow **Attempt 1**.

### Validation Results

Executed in the dedicated Background implementation worktree, as shown in the supplied developer terminal recordings (`typescript(20261024-012353)`, `typescript(20261024-012904)` and `typescript(20261024-013300)`):

- **PASS** — `npx vitest run tests/unit/services/woocommerce-recovery/woo-recovery-admission.service.test.ts`: 28/28 tests.
- **PASS** — `npm run test:integration -- tests/integration/woo-recovery-admission.integration.test.ts`: 2/2 disposable PostgreSQL/Redis tests (concurrent first insert and no outbound/charge; consent/STOP revision change before INSERT).
- **PASS** — `npx vitest run tests/unit/services/checkout-recovery/recovery-materialization.service.test.ts tests/unit/services/checkout-recovery/recovery-consent-admission.service.test.ts`: 22/22 Shopify regression tests (17 + 5).
- **PASS (no errors reported)** — `npx tsc --noEmit -p tsconfig.json`, focused `npx eslint` on both BG003 service files and both test files, and `git diff --check`.
- **PASS** — `npm run prisma:generate` after applying the implementation patch; Prisma Client generated from the canonical schema.
- **PASS** — implementation commit `95c108e` (`feat(ARCH-048-BACKGROUND-003): implement Woo first-recovery admission`) pushed to `origin task/ARCH-048-BACKGROUND-003` in `moda-interact-background`. The terminal subsequently shows an unrelated untracked `typescript` recording; it was not part of the commit.
- Earlier attempts to run the integration launcher directly failed with `spawn prisma ENOENT`, and the initial TypeScript/ESLint checks found narrowing/unused-import problems. Running the repository's `npm run test:integration -- ...` and applying the incremental correction resolved those local failures; the passing evidence above is from the corrected source.

**Coverage qualification:** The two BG003 PostgreSQL/Redis integration tests do **not** independently demonstrate the entire `materialise/cancel/update` event-race and existing-`MESSAGE_SENT`/missing-candidate matrix named in the second Validation checkbox. The unit suite covers order-placed/paid/cancelled, event-watermark supersession and existing sent/expired or missing-candidate cases. The broader integration matrix is left unchecked for reviewer disposition rather than claimed as complete.

**Physical worktree / synchronisation evidence:**

- Implementation worktree reported by terminal: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-048-BACKGROUND-003`; branch: `task/ARCH-048-BACKGROUND-003` (confirmed by `git branch --show-current` and commit output).
- The supplied review ZIP is rooted at `moda-interact-workspace-task-ARCH-048-BACKGROUND-003`, but the launcher's absolute canonical primary workspace root, dedicated parent worktree path, parent branch revision and parent remote push are **not verified** by the archive or supplied terminal output.
- The launcher's start-of-attempt parent/implementation fast-forward and `origin/main` reconciliation packet, recursive submodule preparation, and explicit shared-checkout isolation attestations are **not present** in the supplied recordings. Reviewer/developer should attach or verify that evidence; a ZIP alone is not proof of worktree isolation.
- Implementation commit/revision: `95c108e`. Parent task-branch revision and parent report publication: pending the developer's application/commit/push of this patch.

### Deviations

- No change to BG003's approved runtime scope; BG005 owns worker wiring and BG004 owns send/billing.
- The recorded integration validation does not yet cover every scenario described by its original combined checkbox; see Validation Results.
- The materialised task uses `execution_mode: developer` and `completion_mode: developer`; submitting for review does not transfer completion authority or increment `attempt`.

### Assumptions

- BG006 local contracts, current ARCH-046 Woo consent reader, and database uniqueness/migrations are the accepted dependency versions at the implementation branch commit.
- Received Woo events cannot establish live Woo state. BG005 must compose accepted BG001/BG002 adapters; no worker is wired by BG003.
- `ARCH-046-BACKGROUND-004` was reported complete by the developer after the earlier snapshot and is not reopened by this task.

### Unresolved Issues

- Verify and attach launcher-prepared parent/implementation isolation, start-of-attempt synchronisation, implementation submodule and parent task-branch evidence before architect acceptance.
- Determine whether the missing event-race/integration matrix requires another test-only correction in the same task; do not weaken or silently mark the existing Validation requirement satisfied.
- Parent task/report branch must be committed and pushed separately using only this task file (do not stage the submodule gitlink or untracked terminal recording).

### Architectural Concerns

- Upstream `WooRecoveryConsentReader.evaluateRecipient` may map certain database exceptions to a typed `UNAVAILABLE` result. This service rethrows exceptions actually thrown by its dependencies, but cannot preserve errors already converted by the upstream reader. ARCH-046 consent-reader ownership should review that behaviour against the fail-visible exception policy; do not work around it by inventing another reader in BG003.
- Outbound-only Woo checkout/order evidence cannot prove state changes whose events never reach Moda; no live checkout verification, initial send, or billing is claimed by this admission service.

## Architect Review

### Review Status

Pending — no implementation reviewed.

### Review Notes

None.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Not assessed.

### Follow-up

None.
