---
id: ARCH-075-BACKGROUND-018
architecture_id: ARCH-075
title: Consume durable Admin Meta reconciliation requests
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 10
executor: codex
claimed_at: 2026-11-14T16:02:08Z
attempt: 1
depends_on: []
enables: []
created: 2026-11-14
updated: 2026-11-14
---

# Consume durable Admin Meta reconciliation requests

## Architecture

ARCH-075; docs/architecture/ARCH-075-ordered-recovery-message-layout.md; moda_architect.

## Objective

Make the existing Admin reconciliation command durably consumable by the bounded Background timer.

## Context

Normal UI requests remain unprocessed until six-hour scheduling because listDue ignores Admin requests. Root identified actual pending receipts during current rollout. Necessary fix separate from frozen NBSP task.

## Scope

Background owning repository discovery/service/status receipt handling and focused unit/disposable database tests.

## Out of Scope

Admin UI changes, provider submission/registration/activation, Shared/schema/newqueue, manual DB flags, main/live operations.

## Requirements

Existing Admin requestMetaReconciliation writes source ADMIN/eventType RECONCILE_REQUESTED/processedAt null with registration/sender/provider identity and submitted requestDigest. Current bounded timer discovery ignores these and status repository consumes only webhook receipts. Add bounded discovery/handling of eligible pending Admin receipts through EXISTING reconcileRegistration and registration lease/CAS/provider status validation. No provider submission/resend path for an Admin reconcile request. Validate selected receipt registration/WABA/provider name/language/id and frozen submitted hash; stale/malformed identity cannot authorize refresh or be called success. Mark EXACT handled receipt IDs processed atomically with successful authoritative reconciliation where possible; do not consume a newer concurrent request never covered by that observation. Preserve retry/backoff on provider unavailable/busy/stale lease, pending receipt durability and no double-click flood. Concurrent workers may perform bounded at-least-once read-only Graph GET; existing updatedAt CAS decides single authoritative projection/event commit. No duplicate CREATE/sends; tests prove idempotent commit/receipt replay. Keep bounded limit/order fairness and no network inside SQL transaction. Reuse existing worker timer/no new queue/event/table/config/Shared release. Root accepted separate BG017 equivalence fix; this task does not change it or block its deployment. If BG017 main merges meanwhile sync accepted main before final checks, preserve both status event changes. Root service-only canary may occur independently, but old Admin requests remain durable until this consumer handles them.

## Work Items

- [x] Add bounded eligible Admin request discovery and existing-service execution.
- [x] Preserve exact receipt identity/CAS/lease/retry lifecycle.
- [x] Add concurrency/idempotency/stale/failure/newer-request regressions.
- [x] Record exact isolated source/check/report.

## Interfaces / Contracts

Existing database WhatsAppTemplateMetaEvent ADMIN RECONCILE_REQUESTED receipt and existing provider reconciliation service; no wire/schema change.

## Dependencies

None; existing service and Admin producer already integrated. Accepted BG017 main must be preserved if it merges before final validation.

## Enables

Normal root UI reconciliation without operator service fallback.

## Acceptance Criteria

- [x] Pending valid UI request refreshes through normal timer without waiting six-hour due schedule or submitting template.
- [x] Exact covered receipt processed; newer/stale/malformed requests not falsely consumed.
- [x] Lease/concurrent/replay/provider failure/backoff failclosed and retry durable.
- [x] Required checks/report complete; no liveops.

## Validation

- [x] Focused actual timer/repository/service tests.
- [x] Disposable PG actual Admin-shaped receipt→normal consumer→authoritative status+processed receipt, concurrency/newer receipt/providerfailure cases.
- [x] Types/build/scopedlint/exact remote CI and diff/privacy; no unrelated broad local repeat.

## Stop Condition

After checks publish source and matching parent report, set review and STOP. Root owns merge/live.

## Implementation Notes

Normal moda-task canonical sibling worktrees/claim. You are not alone; BG017 owner edits same status repository/service on another branch. Coordinate narrowly, preserve changes, sync accepted main before final. No hidden direct field patching or provider network in SQL.

## Reconciliation concurrency correction

Source inspection proves no existing reconciliation read-lease (CREATE submission lease is separate). Root agrees do NOT add pseudo-lease via failureCode/nextRetryAt, no new claim/schema. Bounded duplicate read-only GET under concurrent timers is acceptable; existing updatedAt CAS remains authoritative single commit and exact receipt idempotency. Preserve backoff/lifecycle, no duplicate CREATE/send. Invalid/stale receipt may be atomically terminal REJECTED with fixed reason and exactreceipt ID, never RECONCILED, after noGET validation failure to avoid oldest-request starvation; newer valid receipts untouched. Provider unavailable/uncertain failure remains retryable with pending durable request. No operational behavior invented beyond this bounded command path.

## Completion Report

### Status

Ready for Review. Implementation, all local required checks and both exact remote CI checks complete.

### Files Changed

- `src/services/meta-template-management/admin-reconciliation.ts`: exact persisted Admin command identity/frozen-hash predicate; no repair/coercion or submission authority.
- `repository.ts`: bounded pending Admin request discovery merged with existing due rows, oldest effective due/request order, registration deduplication, max50 rows/receipts per scan and exact selected receipt IDs.
- `service.ts`: Admin timer items use only existing reconcileRegistration, validate selected receipts before provider verification/read, and count stale/rejected commands separately from successfully handled observations; ordinary submission path unchanged.
- `status-repository.ts`: terminal fixed-reason REJECTED for invalid exact requests, pending/backoff preservation, exact selected receipt revalidation and atomic successful receipt/status CAS; no newer request sweep. Accepted BG017 raw-hash/equivalence event evidence preserved.
- `tests/unit/services/meta-template-management/admin-reconciliation.test.ts`, `meta-management.test.ts`: identity changes, processed/unsubmitted/frozen mismatch, bounded discovery ordering/deduplication and actual normal timer Admin-only/no-CREATE routing.
- `tests/integration/arch075-admin-meta-reconciliation.integration.test.ts`: actual durable Admin-shaped receipt→normal timer→authoritative projection+receipt, concurrency, replay, newer concurrent request, identity rejection, unavailable/backoff, stale row, never-submitted no-CREATE and externally processed receipt cases.

### Work Completed

Exact source `1d01849aa0b1a67f4baca9f9e9eac2828d532a19` pushed on `task/ARCH-075-BACKGROUND-018`, draft PR https://github.com/kodjobaah/moda-interact-background/pull/230. Pending valid requests can refresh a submitted registration despite its normal future six-hour schedule. Discovery stays bounded and FIFO by effective due/request time; no queue, schema, new event type/configuration or Shared/Admin changes. Receipt registration/WABA/provider ID/name/language/submitted hash and locale frozen identity must match before GET. Exact invalid receipts terminate REJECTED with fixed ADMIN_RECONCILE_IDENTITY_STALE, never success; valid newer requests are untouched. Successful authoritative CAS rechecks and marks only selected request IDs in the same transaction; receipt races cannot authorize an uncorrelated projection. Provider exceptions leave the valid command pending and retain existing durable retry/backoff; repeated clicks cannot bypass it.

Source inspection disproved the assumed existing read lease. Root/architect amendment0d20d5dc2 explicitly permits bounded at-least-once read-only GETs and existing updatedAt CAS as single authoritative commit, with no pseudo-lease via failureCode/nextRetryAt and no new claim/schema. Implementation follows that clarification: no network inside SQL transactions, no CREATE/resend for an Admin command. This control timer path adds bounded discovery/identity work only; Shopify hot path and customer messaging/billing are unchanged.

### Validation Results

- Normal launcher packet: primary `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; canonical parent `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-075-BACKGROUND-018`; implementation `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-075-BACKGROUND-018`; mirrored task branches. Attempt1/codex claimed2026-11-14T16:02:08Z, pushed parent claim6d57b7a870ccb4a509a32de0e259e1a0c6dd0abe. Starting parent258541a48171e9856f9316b86eefff539e87f7f4/sourcec041c88757ec6d1ddc583dd2cde6e0cf92755796; database submodule6f42b71112efe7ac63654d55f41cd74ca569b1ae initialized/ready. No primary/other-task modifications or gitlink staging.
- Synced actual accepted BG017 origin/main `c8ee5491d2e6eccd54b0de1dfcf8863d9e373d94` before implementation/final checks. No diff in its contracts/provider-text-equivalence helper; status/service additions preserve its rawhash/equivalence evidence. Parent scope amendment0d20d5dc2 read without a new claim.
- `npm ci` and declared `npm run build`: PASS, including both TypeScript compilations. Scoped ESLint on all7 changed files: PASS. `git diff --check`: PASS.
- `npx vitest run tests/unit/services/meta-template-management`:189PASS/11files, covering timer/service/repository/identity and existing provider/sample/throttle/equivalence paths.
- Actual disposable PostgreSQL combined14unique cases PASS: initial3files12PASS (`arch075-admin-meta-reconciliation`, accepted `arch075-meta-nbsp-equivalence`, existing `arch047-meta-template-management`) plus2 final negative cases added after the first run loaded, bothPASS via targeted `--testNamePattern 'never-submitted|externally handled'`. No failed tests, no waived cases, no redundant broad rerun. Commands use existing `node scripts/test-integration.mjs`; only disposable PostgreSQL/fake provider, no managed DB/network provider operations.
- PG receipts prove normal future-six-hour row is discovered through its Admin request; replay idle; two concurrent read-only GETs but exactly one RECONCILE/status commit; selected receipt processed once; later request not consumed by older observation; exact identity mismatches rejected before provider verification/GET; never-submitted Admin command cannot trigger CREATE; unavailable provider leaves pending/backoff and later retry succeeds; changed row CAS or externally handled receipt cannot commit stale success. Provider create spies remain unused in command processing. BG017 NBSP/raw identity/final-admission regression and existing047 intent/webhook regression PASS.
- Known full-lint4 baseline remains untouched: candidate-index.store.ts:9 readRecoveryExecutionPolicy and recovery-offer-resolver.service.ts:23-25 MAX_CANDIDATES/VERIFICATION_TIMEOUT_MS/AI_TIMEOUT_MS. Starting/current exact blobs8bff21b8514b4449dd326c1c1dac12a3ba4a8dbf /077bcbb76c018428bd5b64c0c82d2a1903b5c6e4 match previously proven BG006/BG007 baseline. No unrelated full-repo cleanup/reinvestigation or full-lint-green claim.
- Exact source CI [43615034048](https://github.com/kodjobaah/moda-interact-background/actions/runs/43615034048) and [43614951519](https://github.com/kodjobaah/moda-interact-background/actions/runs/43614951519): both SUCCESS on1d01849aa0b1a67f4baca9f9e9eac2828d532a19. Parent evidence checkpoint153ba2fcd and draft PR https://github.com/kodjobaah/moda-interact-workspace/pull/1049 pushed before this final review-status commit. Private logs retained under primary `local-backups/arch075-bg018-*` (npm-ci, build, focused, postgres, postgres-negative, scopedlint, preparation packet). Source/report contain only synthetic test identities, no live secrets/raw customer payloads.

### Deviations

Root-authorized correction of nonexistent read-lease assumption recorded above; no new lock/claim/lease mechanism. Two late-added negative tests were executed separately after the original PG run had loaded; combined exact unique receipt reported honestly, with no failures/waivers.

### Assumptions

Root owns accepted merges, deployment and normal Admin UI/worker proof. This agent performs no live calls, provider submission/activation, managed DB flag edits or main merges.

### Unresolved Issues

No local implementation blocker. Existing read-only GET duplication remains bounded at-least-once under concurrent workers by explicit scope; only CAS-authorized projection/receipt commits once. Provider approval/PENDING state and actual UI rollout proof remain external/root-owned.

### Architectural Concerns

No Shared release/schema/queue/Admin edit, no sample/create lease reuse, no pseudo-lease and no new generic logger/transport. Existing service/provider validation/CAS/backoff remain owners of reconciliation.

## Architect Review

### Review Status

Pending

### Review Notes

Pending actual code

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

Root normal UI verification
