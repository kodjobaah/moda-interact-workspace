---
id: ARCH-049-BACKGROUND-002
architecture_id: ARCH-049
title: Own durable ShopBrand media generations, retries and reconciliation
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: complete
priority: 30
executor: null
claimed_at: null
attempt: 1
depends_on: ["ARCH-049-DATABASE-001", "ARCH-049-BACKGROUND-001"]
enables: ["ARCH-049-BACKGROUND-003", "ARCH-049-SYSTEM-TEST-001"]
created: 2026-10-25
updated: 2026-10-27
---

# Own durable ShopBrand media generations, retries and reconciliation

## Architecture

`ARCH-049` — `docs/architecture/ARCH-049-shopbrand-public-media-configuration.md`; coordinator `moda_architect`. This task is materialised on its canonical parent task branch and prepared for developer Attempt 1.

## Objective

Implement the one-owner image-processing state machine over ShopBrand JSONB: claim due fixed roles, invoke BG001, persist verified READY atomically, reclaim abandoned work and periodically revalidate mutable source images.

## Context

ShopBrand persists role-specific source/work/ready fields; there is no media job table. PostgreSQL commit of PENDING is the durable acceptance point; BullMQ is an optional wake-up, not a second durable requirement.

## Scope

- Build `src/services/shop-brand-media-orchestration/` with source-slot persistence helper, lease/claim/CAS repository, due scanner and thin worker entrypoint.
- Use BG001 processor as an injected dependency and record structured outcomes via Shared logging.
- Schedule a bounded due scan every 5 minutes; allow optional BullMQ wake, with reconciliation required if wake is lost.
- Implement seven-day READY rechecks for same-URL changed bytes with safe last-known-good retention, and bounded retry/lease recovery.

## Out of Scope

- Implementing image fetching/transcoding, Shopify GraphQL, WordPress API, Woo plugin endpoint, ARCH-047 send-time resolution or metadata database triggers.

## Requirements

### R1. Common source update algorithm

Export an application-level source updater usable in Background and reproducible by the API service (the persistence JSON format is the architecture contract, not a Shared AST package):

```typescript
type BrandRole = 'LOGO'|'SQUARE_LOGO'|'COVER_IMAGE';
interface SourceObservation {
  shopId: string; role: BrandRole; sourceUrl: string|null;
  sourceReference: string|null; sourceFingerprint: string|null;
  observedAt: string;
}
```

With a short PostgreSQL row lock, check observed ordering and previous source values, increase source generation only on change, set PENDING or MISSING, clear lease/retry/failure, and preserve other roles atomically. Do not hold a DB transaction while downloading/uploading. Source timestamps are producer metadata; a replayed older observation must not overwrite a newer one. With no `ShopBrand` row, upsert by unique `shopId` before locking.

### R2. Work claim and completion

Claim one `(shopId,role,generation,fingerprint)` with expiring lease; write work.status PROCESSING and lease fields atomically. Run BG001 outside transactions. Publish READY only on matching current generation/fingerprint and claim. Store object key/contentType/output dimensions/bytes/digest/verifiedAt. Stale results do not update current READY, but immutable R2 objects need not be immediately deleted. On permanent failure set FAILED without retryAt; on transient failure increment attempts and schedule 1m, 5m, 30m, 2h, 24h with a max five attempts per generation. Reclaim expired leases.

### R3. Durable due scanner

Every five minutes examine a **bounded** number of ShopBrand JSON roles with work.status PENDING or retryable FAILED or expired PROCESSING. Do not use an unbounded full-table lock, do not starve a hot shop, and never require the best-effort BullMQ wake for correctness. The source change commit is sufficient for recovery after process restart. When the next process is launched, it must find due rows deterministically.

### R4. Revalidation of same-URL bytes

At least once per seven days, schedule a bounded content refresh of READY source URLs without immediately suppressing their last verified **current-generation** asset. If bytes unchanged, retain existing key. If bytes changed and the effective source reference/generation is still current at commit, atomically replace the ready object key/digest. Transient refresh failures keep the previously verified same-generation READY asset eligible and record a separate failure/retry marker; a source URL/reference change increments generation and makes old READY ineligible. Do not allow an old worker to overwrite a changed role.

### R5. Initial limits/telemetry

Expose per-role retry and failureCode metadata, bound memory/worker concurrency to R2 and external hosts, and use the existing shared logger. No new generic service logger or duplicated framework metrics.

## Work Items

- [x] Implement row-locked source updater and lease/CAS repository.
- [x] Implement bounded due scanner and optional wake handling.
- [x] Implement retry, crash recovery and seven-day content refresh.
- [x] Test two workers, multi-role writes, stale completion, source removal, duplicate source event and status reconstruction.

## Interfaces / Contracts

Consumes `commerce.ShopBrand` `whatsAppMedia` JSON schema version 1 and BG001 `process()` output. Produces updated per-role work/ready JSON. For lookup, only `READY` with matching `sourceGeneration` and `sourceFingerprint` is eligible; consumers must also check validated media properties and trusted public origin.

## Dependencies

- ARCH-049-DATABASE-001
- ARCH-049-BACKGROUND-001

## Enables

- ARCH-049-BACKGROUND-003
- ARCH-049-SYSTEM-TEST-001

## Acceptance Criteria

- [x] Duplicate or concurrent source updates do not lose another role or duplicate current generation.
- [x] Lost queue wakes and worker crashes are recovered by due-row scan.
- [x] Old generation or old lease holder cannot publish READY.
- [x] Failed fetch/R2 calls are retried within bounded policy; permanent errors visible without endless retry.
- [x] A same-URL updated image is eventually detected and atomically replaces READY without forcing a send-time download.

## Validation

- [x] PostgreSQL integration tests for per-role row-lock/CAS/unique shop and multi-worker contention.
- [x] Unit tests for retry backoff, due-scan bounds and lease expiry.
- [x] Deterministic output-stale and revalidation fixture tests.
- [x] Relevant Background lint/typecheck/tests and `git diff --check`.

## Stop Condition

After the defined Work Items, Acceptance Criteria and Validation are complete, record the Completion Report and change task status to `review`; hand off to `moda_architect` and STOP. Do not continue into a dependent task or change an `_index.md`.

## Implementation Notes

All task work must use the canonical launcher-provided **dedicated parent and implementation worktrees**, synced task/<TASK_ID> branches and start-of-attempt evidence. Inspect the actual pinned package scripts, source and existing conventions before editing. Do not merge branches, push main, edit another repository, start an enabled task or change any `docs/decisions/**/_index.md`. Use structured logging via `@modainteract/moda-interact-shared/logging`; secrets and full untrusted URLs must not enter diagnostics. Document changed files, relevant test commands, results, security/tenant checks, commits and worktree evidence in the Completion Report.

No additional assumptions are authorised.

## Completion Report

### Status

Complete — developer Attempt 1 following the passing self-review and the developer-supplied “Architect Review Accepted” statement. The implementation and completion report are published on their respective task branches. Attempt 1 is unchanged; the acceptance statement is not represented as an independently authored architect review.

### Files Changed

Implementation repository: `moda-interact-background`, 12 files in commit `6617d97` (`feat(arch-049-background-002)`):

- `docs/arch049-shopbrand-media-orchestration.md`
- `src/entrypoints/recovery.ts`
- `src/services/shop-brand-media-orchestration/contracts.ts`
- `src/services/shop-brand-media-orchestration/index.ts`
- `src/services/shop-brand-media-orchestration/repository.ts`
- `src/services/shop-brand-media-orchestration/runner.ts`
- `src/services/shop-brand-media-orchestration/service.ts`
- `src/services/shop-brand-media-orchestration/state.ts`
- `tests/integration/shop-brand-media-orchestration.integration.test.ts`
- `tests/unit/services/shop-brand-media-orchestration/repository-logging.test.ts`
- `tests/unit/services/shop-brand-media-orchestration/service.test.ts`
- `tests/unit/services/shop-brand-media-orchestration/state.test.ts`

This report changes only the canonical parent task file. It does not modify implementation code, either repository's `main`, a submodule gitlink or any domain `_index.md`.

### Work Completed

- Implemented `ShopBrandMediaRepository.observeSource` with transactional first-row upsert, PostgreSQL `FOR UPDATE`, observation-order protection, role-local JSONB edits and source generation/fingerprint updates.
- Implemented generation-, fingerprint-, source URL-, lease-owner- and lease-expiry-qualified claim/complete/fail transitions. Processing and R2 I/O occur outside database transactions; expired processing leases are reclaimable and stale completion is rejected.
- Implemented bounded keyset reconciliation (five-minute Recovery-worker tick, 50 rows/page, 500 rows/tick, 20 claims/tick, two concurrent media operations by default), round-robin cursor progress and correctness without a BullMQ wake. Exposed optional local `reconcileShop` wake.
- Implemented seven-day content rechecks using separate refresh metadata, retaining same-generation last-verified READY on transient refresh failure and atomically replacing READY when verified content changes. Source removal or generation change makes historical READY ineligible.
- Added structured error handling through `@modainteract/moda-interact-shared/logging`: each intercepted transaction retry, terminal database error, scan-page/row error, per-claim failure, processor exception, optional wake failure and reconciliation-run failure is logged with bounded reason codes and identifiers. Raw exception messages, credentials and untrusted source URLs are excluded from those events.
- Added focused state, scanner, logger and disposable-PostgreSQL integration regression tests, including contention, multi-role preservation, crash reconstruction, stale claims, refresh retention, bounded retries and logging redaction.

### Validation Results

Developer-run evidence: `typescript(20261027-143828)` terminal log, uploaded with the task worktree snapshot on 2026-10-27. The code and tests listed below are present in the accompanying overlaid Background repository snapshot.

| Command | Result |
| --- | --- |
| `npm run prisma:generate` | PASS — Prisma Client 6.19.3 generated against `database/prisma/schema.prisma`. |
| `npm test -- tests/unit/services/shop-brand-media-orchestration` | PASS — 23 tests in 3 files, including 3 transaction-exception logging tests. |
| `node scripts/test-integration.mjs tests/integration/shop-brand-media-orchestration.integration.test.ts` | PASS — 3 PostgreSQL integration tests. |
| `npm run lint` | PASS — ESLint completed without reported errors. |
| `npm run build` | PASS — Prisma generation and TypeScript compilation completed without reported errors. |
| `git diff --check` | PASS — no whitespace errors reported. |
| `git status` after commit/push | Branch up to date with `origin/task/ARCH-049-BACKGROUND-002`; only untracked local terminal capture `typescript` remains. |

Implementation branch `task/ARCH-049-BACKGROUND-002`: commit `6617d97`, followed by successful `git push -u origin task/ARCH-049-BACKGROUND-002` as shown in the terminal evidence. These are evidence reported by the local terminal, not Git remote actions performed by the architect in this sandbox.

Isolation evidence: canonical parent task worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-049-BACKGROUND-002` and implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-049-BACKGROUND-002` are identified by the claim record and the final task archive-generation output. The existing **Execution Ownership Amendment and Claim** below records start-of-attempt branch synchronisation and successful dependency gating. The architect reviewer should cross-check the launcher packet / Git common-dir identity because the supplied ZIP alone cannot independently prove Git worktree identities or the exact starting commits.

### Deviations

- No required separate BullMQ wake implementation: the five-minute durable reconciliation sweep is the correctness path, and an optional in-process `reconcileShop` wake is exposed; no new queue or Render deployment was introduced.
- The retry table contains delays of 1m, 5m, 30m, 2h and 24h, but the enforced ceiling of **five total processing attempts** permits only four retry intervals (1m/5m/30m/2h). The 24-hour fifth delay is unreachable without authorising a sixth attempt. The implementation prioritises the explicit five-attempt ceiling; the architectural ambiguity is escalated below.

### Assumptions

- `MEDIA_MAX_ATTEMPTS = 5` means five **total** attempts per generation, not one initial attempt followed by five retries.
- PostgreSQL state/leases are sufficient for durable acceptance; media scanner co-location with the existing Recovery worker is permitted by the task and parent architecture.

### Unresolved Issues

- Actual Cloudflare R2 credentials, public custom-domain propagation and a live provider media GET are not certified by this task's isolated tests; those require the approved external preflight and integrated system validation. No claim of production R2 reachability is made here.
- Architect to confirm the contradictory fifth backoff/maximum-attempt wording before relying on a 24-hour automatic retry; this does not invalidate the observed bounded-retry tests.
- Architect should verify the developer-prepared worktree packet and original synchronization evidence before final acceptance. No task worktree was created, committed or pushed from this sandbox.

### Architectural Concerns

The design contract simultaneously proposes five backoff intervals and caps total processing attempts at five. Four delays between five attempts are mathematically consistent; a fifth scheduled 24-hour retry would require six total attempts. Recommend documenting the accepted interpretation (retain five attempts, or separately authorise six). Other source-generation, transactional and lease boundaries conform to the inspected ARCH-049 implementation.

## Architect Review

### Review Status

Accepted — the developer supplied the statement “Architect Review Accepted” with the explicit completion request on 2026-10-27. This task record does not claim an independently authored architect review.

### Review Notes

The developer-supplied acceptance follows the durable passing Attempt 1 self-review and the fresh focused validation recorded above. The five-total-attempt retry interpretation is accepted for this task; the 24-hour delay remains unreachable unless a future architecture change authorizes a sixth total attempt.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Accepted for this task with the known retry-policy limitation recorded above; no change to the five-attempt implementation was requested.

### Follow-up

None.

## Execution Ownership Amendment and Claim

- On 2026-10-27, `/moda_developer_create ARCH-049-BACKGROUND-002` explicitly took over the ready agent-owned task for developer execution. `assigned_agent: moda_background` is unchanged; `execution_mode` and `completion_mode` are now `developer`.
- Developer Attempt 1 was claimed at `2026-10-27T13:20:22Z` after verifying `ARCH-049-DATABASE-001` and `ARCH-049-BACKGROUND-001` were complete and synchronizing both canonical task worktrees.
- Parent task branch `task/ARCH-049-BACKGROUND-002` fast-forwarded to current parent `origin/main`; implementation branch `task/ARCH-049-BACKGROUND-002` was created from current Background `origin/main`. Both task worktrees were clean before the claim. The shared Background `main` checkout's seven local-only commits were not used or modified.

## Developer Self-Review Passed (Attempt 1, 2026-10-27)

- Outcome: **passed**. The Work Items, Acceptance Criteria and required Validation are complete. No known implementation defect or incomplete acceptance criterion blocks architect review.
- Source review: the repository performs short row-locked JSONB updates, bounds keyset reconciliation and claim concurrency, rejects stale generation/lease completions, keeps external media I/O outside transactions, and retains same-generation READY media on transient refresh failure. Structured logging uses bounded identifiers/reason codes and excludes raw exceptions and source URLs.
- Fresh validation in the canonical Background implementation worktree: `npm test -- tests/unit/services/shop-brand-media-orchestration` passed **23 tests in 3 files**; `node scripts/test-integration.mjs tests/integration/shop-brand-media-orchestration.integration.test.ts` passed **3 PostgreSQL integration tests**; `npm run build` passed Prisma generation and TypeScript compilation; `npm run lint` passed; `git diff --check` and `git show --check 6617d97` reported no whitespace errors.
- Synchronized source delta: implementation task branch `task/ARCH-049-BACKGROUND-002` is at `df7dea9f64f618f28d77f46b4f53a093822d4162` and is up to date with `origin/task/ARCH-049-BACKGROUND-002` after a successful fast-forward push. Its three-file delta from the original task commit adds ARCH-048 Woo recovery outreach integration assertions; it does not alter BG002 orchestration source. Focused BG002 validation above passed on this synchronized tree.
- Retry interpretation: retain the explicit ceiling of **five total attempts**, so four retry intervals (1m/5m/30m/2h) are scheduled and the listed 24h delay remains unreachable. This is a specification ambiguity, not an unbounded retry or a failed acceptance criterion; the architect should confirm whether to retain five total attempts or authorize a sixth attempt before relying on the 24h retry.
- Review disposition: pass to architect review with that retry-policy decision recorded as a follow-up. This is not an architect acceptance or a developer completion decision.
- Transition: preserve `status: review`, `executor: null`, `claimed_at: null`, and `attempt: 1`. `completion_mode: developer` means the task remains in review pending the architect's review and the developer's explicit completion decision. No dependent task was started or promoted.

## Developer Completion Decision (Attempt 1, 2026-10-27)

- Decision: the developer explicitly invoked `/moda_developer_update ARCH-049-BACKGROUND-002 complete` and supplied the acceptance statement “Architect Review Accepted.” The statement is recorded as developer-supplied; no independent architect-authored review is implied.
- Accepted attempt: Attempt 1; `attempt` remains 1. The task is `status: complete`, `executor: null`, and `claimed_at: null`.
- Implementation publication: Background task branch `task/ARCH-049-BACKGROUND-002` is clean and published at `df7dea9f64f618f28d77f46b4f53a093822d4162`.
- Parent publication: this completion and dependency-frontier update is committed and pushed on parent task branch `task/ARCH-049-BACKGROUND-002`; no task branch was merged to `main`.
- Dependency frontier: `ARCH-049-BACKGROUND-003` is eligible and promoted from `pending` to `ready` because DATABASE-001, SHOPIFY-001, and BACKGROUND-002 are complete. Its attempt remains 0 with no executor or claim timestamp. `ARCH-049-SYSTEM-TEST-001` remains pending/manual-gated because its other declared dependencies are incomplete.
- Retry policy: retain the explicit five-total-attempt ceiling. Four delays are reachable; the 24-hour delay remains a documented contract clarification and no retry behavior was changed in this completion.
