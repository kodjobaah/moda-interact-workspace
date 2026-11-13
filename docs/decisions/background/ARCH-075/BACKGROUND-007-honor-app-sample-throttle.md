---
id: ARCH-075-BACKGROUND-007
architecture_id: ARCH-075
title: Honor app-wide sample throttle before template intent
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 5
executor: codex
claimed_at: 2026-11-13T11:41:35Z
attempt: 1
depends_on:
  - ARCH-075-DATABASE-002
  - ARCH-075-BACKGROUND-006
enables:
  - ARCH-075-SYSTEM-TEST-002
created: 2026-11-13
updated: 2026-11-13
---

# Honor app-wide sample throttle before template intent

## Architecture

ARCH-075; docs/architecture/ARCH-075-ordered-recovery-message-layout.md; coordinator moda_architect.

## Objective

Honor app-wide sample throttle before template intent.

## Context

Actual Meta sample_session HTTP403/code4 app request limit was classified as permanent blocked. One upload perlocale plus60second local polling and replica overlap can amplify calls; changing classification alone does not give durable cooldown. Existing scheduler leases/config/audit rows are not proper app-scoped lifecycle state. Generic historical rejection events do not carry code4 evidence.

## Scope

Existing sample error classifier, Meta preclaim submit/due path, dedicated app throttle repository/lease policy, bounded exact operator recovery for evidenced historical code4 blocks, related tests/docs and accepted Database gitlink adoption. No Shared release/cache.

## Out of Scope

Other repositories except explicit accepted submodule adoption, provider credentials/grants, live sends/repair/deployment, Shared publication, blind create retry, unsupported caching, generic refactors or implementation-source merges.

## Requirements

Recognize only evidenced numeric Meta code4 from structured provider403 sample_session/sample_upload response as app throttle (no English message substring). Other403 auth/permission rejections remain blocked. Preserve other existing provider error semantics unless directly necessary for safe preclaim deferral. Resolve trusted app/environment and acquire dedicated durable fenced lease BEFORE each sample operation;120seconds covers source fetch and both bounded HTTP phases. No network inside SQL transaction. Verify lease/app identity before sample HTTP, renew only under matching generation if needed; release/finish cannot clear newer ownership/cooldown. After code4, persist specific bounded evidence/reason and cooldown15min doubling to6h cap with saturated count, stop remaining same-app work across loops/replicas, and durably defer only still-unclaimed READY rows until permitted. Check future nextRetryAt and shared app gate before upload; newly created rows also respect cooldown. Genuine successful bounded sample operation may reset consecutive throttle count only under valid ownership, never override a later cooldown. Missing state/database failure is fail-closed for protected upload; no in-memory/Redis-only correctness gate. No singleflight/sample-handle reuse/cache without independently verified provider lifetime/scope (not authorized here). CREATE_INTENT/POST_INTENT/uncertain creates retain existing reconciliation/no-repost safety; never change submitted rows or approved snapshots. Historical generic REJECTED events lack durable code4 metadata: NEVER blanket-reset them. Root-only dry-run/apply operator capability may recover at most20 exact IDs per manifest only with explicit protected external403/code4 evidence digest/reference and truthful operator attestation, exact app/WABA/source/reviewer/updatedAt/transport fingerprint and zero prior claim/post/provider/unknown evidence, reusing existing preclaim guards compatibly. Preserve missing-app recovery behavior. Atomically audit recovery and seed/retain app cooldown (never shorten it or increment perlocale), make rows due no earlier than cooldown; no provider call/reset of history/attempts/unknown state. Live repair belongs to root after deployment/drain; task agent performs no live mutation. Internal policy bounds are conservative safety settings, not a provider guaranteed reset interval.

## Work Items

- [x] Implement only the owning bounded outcome and final contract.
- [x] Prove meaningful failure/concurrency/compatibility behavior.
- [x] Complete mirrored report/checks, return review and stop.

## Interfaces / Contracts

Database002 owns durable Prisma/SQL state. Background007 consumes exact accepted schema and owns provider policy/leases/recovery; no new Shared contract. SystemTest002 is terminal validation. Root owns migration/deployment/operational evidence; no network inside transaction.

## Dependencies

ARCH-075-DATABASE-002, ARCH-075-BACKGROUND-006

## Enables

ARCH-075-SYSTEM-TEST-002

## Acceptance Criteria

- [x] Assigned bounded capability/invariants and explicit negative behavior satisfied.
- [x] Existing provider-intent, tenant/environment, immutable source and legacy lifecycle guards remain intact.
- [x] Canonical matching physical isolation/sync and exact validation evidence reported; no live mutation.

## Validation

- [x] Meaningful red/green classifier403/code4 vs auth403; units plus actual PostgreSQL concurrent replica lease, stale generation/reclaim, persistent cooldown/backoff saturation/expiry and future/new row gates, source-fetch/request deadline, duplicate completion and DB failure. Provider simulator proves no remaining same-app calls after throttle across cycles/replicas; intent/unknown POST never replayed. Exact historical recovery evidence/CAS/batch/replay/audit rollback negatives, no generic REJECTED reset. Relevant types/lint/build/exact-head full CI; no live provider calls.
- [x] Diff/privacy hygiene; no secrets/private production identifiers or unsupported capability claim.

## Stop Condition

When scope/checks complete, submit Completion Report/status review and STOP. No enabled task, source merge, hosted migration or live recovery/provider action.

## Implementation Notes

You are not alone; preserve other work. Canonical launcher packet owns start/claim. Root owns all final merges, test/prod migration, worker rollout/drain and protected live evidence. New domain logs reuse published Shared logging; do not duplicate generic telemetry. Return genuine contract gaps before widening scope.

## Completion Report

### Status

Ready for Review. Implementation and validation complete; awaiting moda_architect review.

### Files Changed

Implementation commit `b3576d7c67c8940f686dd16c1db84d1d3f35c17d` on `task/ARCH-075-BACKGROUND-007`; draft PR https://github.com/kodjobaah/moda-interact-background/pull/218.

- `database` gitlink: explicitly adopted accepted Database002 merge `6f42b71112efe7ac63654d55f41cd74ca569b1ae`; no database source/schema edits.
- `src/services/meta-template-management/app-operation.ts`: dedicated SQL app/environment acquisition, generation/owner fencing, cooldown/backoff and bounded one-upload operation. Uses published Shared CommerceEnvironmentSchema/type, no duplicate environment contract.
- `image-header-sample.ts` and `meta-graph.adapter.ts` in the same service directory: structured numeric403/code4 classification, operation abort propagation, fence and trusted app/environment/credential identity checks before each sample HTTP phase. No cache or handle/session reuse.
- `service.ts`, `repository.ts`, `contracts.ts` in that directory: future-due guard, truthful preclaim deferral/audit, bounded same-WABA due-cohort deferral and stop after throttle/gate denial. Local busy outcome carries retry time/WABA; no queue or cross-service payload changes.
- `preclaim-recovery.ts`: extract/reuse unchanged reviewed-source and row/source lock guards; missing-app policy remains strict and separate.
- `throttle-recovery.ts`: separate exact external-attestation historical recovery, compatible verified BG005 provenance, immutable manifest/CAS/audit, atomic app cooldown seed/retention, strict replay and bounded30s plan/apply transactions.
- `scripts/recover-meta-sample-throttle.mjs` and `docs/operations/recover-meta-sample-throttle.md`: explicit root-only plan/dry-run/apply procedure; protected evidence hashing/reference/exact-ID attestation. No live execution performed.
- `tests/unit/services/meta-template-management/{app-operation,throttle-recovery,image-header-sample,meta-management}.test.ts` and `tests/integration/arch075-app-throttle.integration.test.ts`: directly relevant classifier, operation, operator and real PostgreSQL proofs. One existing adapter transport test explicitly injects a test operation; production uses the SQL gate.

### Work Completed

Only structured numeric Meta code4 on HTTP403 at sample_session/sample_upload is treated as app throttle. String "4", auth/permission403 and English-message lookalikes remain blocked. Existing non-code4 provider semantics are preserved. The production adapter resolves trusted app/environment, durably INSERTs/acquires app state before work, and verifies owner/generation, live lease and app/config identity before each provider HTTP phase. A missing table/state lookup failure or database error never bypasses the SQL gate. Network calls occur outside SQL transactions. Lease is120s for one sample operation; whole source/session/byte operation has90s abort deadline, so no entire-cohort lease or renewal is needed. Failed/stale completion cannot release newer ownership, reset its count or clear a later cooldown.

Recorded code4 sets durable15m cooldown, doubles on consecutive throttles to6h with count saturation31, clears only its valid lease and carries exact app/environment/operation/http/provider-code evidence. Future registration due time is checked before upload. Preclaim deferral changes only still-unclaimed READY rows; monotonic updatedAt/CAS prevents racing an older claim snapshot. The due loop defers a bounded same-WABA cohort and stops. Other replicas and newly created rows read the same durable app gate before sample fetch/upload. Genuine successful sample work resets consecutive count only under current ownership and no newer cooldown. Timings are conservative internal policy, not a Meta reset guarantee. CREATE_INTENT, POST_INTENT, unknown/submitted reconciliation/no-repost paths remain unchanged.

Historical generic rejection events cannot establish provider code4. The new operator capability therefore requires protected external evidence SHA256/reference, explicit truthful403/numeric-code4/exact-ID attestation, max20 exact IDs and pinned app/WABA/environment/current reviewed source/reviewer/updatedAt/frozen transport. It never resets generic rejections automatically. Original missing-app block plus the accepted exact BG005 recovery audit is compatible only when the old manifest/digest/identity/evidence are self-consistent. Unknown, claim/post/result/provider/reconciliation/drift history refuses. A serializable transaction rechecks all rows, seeds one app cooldown or retains an already-active cooldown exactly, never increments per locale or resets existing attempts/history, makes rows due no earlier than cooldown and appends truthful external-attestation audits. Existing expired backoff history is retained conservatively. CAS/audit/serialization/refusal rolls back the batch and app seed. Same-manifest replay adds no audit/transition/extension and revalidates history/source; advanced or unknown state refuses.

Root operational feedback about measured20-24second plans was implemented: both new plan and apply explicitly use bounded30second serializable transactions, tested through actual method option assertions;20-ID cap remains. CLI hashes protected evidence bytes without interpreting private contents, so the operator attestation remains an external trust dependency rather than invented database proof. Root owns actual evidence matching, migration, accepted deployment/drain and live recovery. No provider requests, hosted database/configuration writes, migration, deployment, cache, Shared release or source merge by this agent.

### Validation Results

- Red: restored original uploader solely for `npx vitest run tests/unit/services/meta-template-management/image-header-sample.test.ts -t 'classifies only numeric code4'`:2 expected failures (session and byte-upload403/code4 misclassified as blocked). Candidate source was restored immediately with cleanup trap.
- Green: `npx vitest run tests/unit/services/meta-template-management`:9 files /114 tests passed. Includes numeric vs string/auth403, fence before each HTTP, uncooperative source abort,90s/120s bounds, DB gate failure, due-cohort stop/future date, strict operator evidence/config/20-ID cap and explicit30s transaction options.
- `node scripts/test-integration.mjs tests/integration/arch075-app-throttle.integration.test.ts tests/integration/arch075-preclaim-recovery.integration.test.ts tests/integration/arch047-meta-template-management.integration.test.ts`:3 files /33 tests passed on real disposable PostgreSQL/Redis. Proves concurrent replica admission, expiry/reclaim/stale generation, duplicate finish/throttle, persistent cooldown/saturated backoff/expiry/environment isolation and guarded count reset. Provider simulator proves only one sample request after first code4 across subsequent cycles, replicas and a newly created row, with no CREATE/POST intent. Historical proofs cover BG005 provenance, protected exact evidence/digest/config/source/CAS, concurrent apply, batch/audit rollback, replay/unknown history and active-lease refusal. Existing missing-app recovery and Meta intent/webhook regressions passed.
- Additional PG retention assertion initially caught a sub-second active-cooldown extension. Fixed to retain active cooldown exactly; final33-test rerun passed. No unresolved regression.
- `npx eslint src/services/meta-template-management tests/unit/services/meta-template-management tests/integration/arch075-app-throttle.integration.test.ts scripts/recover-meta-sample-throttle.mjs`: passed.
- `npx tsc --noEmit`, `npm run prisma:generate`, and declared `npm run build`: passed with accepted nested schema/client. No dependency/lockfile change.
- Compiled CLI negative smoke `node scripts/recover-meta-sample-throttle.mjs --manifest absent.json --apply`: bounded RECOVERY_ARGUMENTS_INVALID refusal before database access because digest is absent.
- `git diff --check` and implementation/nested-worktree hygiene: passed; only16 assigned files including accepted nested gitlink. No secrets/private production IDs or real provider output added to fixtures/docs/source.
- Initial disposable-runner launch lacked docker on a non-login process PATH; no tests ran. Verified existing `/usr/local/bin/docker`, supplied that tool directory to the process PATH and reran successfully. No installation, persistent environment change or application workaround.
- Exact-head full CI passed:386 files /4,229 tests, Prisma generation and TypeScript; push run https://github.com/kodjobaah/moda-interact-background/actions/runs/43424471889 and PR run https://github.com/kodjobaah/moda-interact-background/actions/runs/43424645194 at `b3576d7c67c8940f686dd16c1db84d1d3f35c17d`.

### Physical Isolation and Launcher Evidence

Prepared packet `/tmp/moda-arch075-background007-prepare.json` supplied the following; preparation/claim was not repeated:

- Canonical workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-075-BACKGROUND-007`, reused; branch `task/ARCH-075-BACKGROUND-007`.
- Implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-075-BACKGROUND-007`, launcher-created; same mirrored task branch.
- Shared workspace/implementation checkout switched or mutated for task work: no. Another task worktree reused: no.
- Parent/implementation remote task fast-forward: not-needed; both origin/main incorporations: already-current.
- Launcher recursive submodule sync/update passed at recorded database `a9b6ab852a8245dfd14447808aac288a23b113d0`. Task-specific architect instruction then explicitly adopted accepted Database002 merge `6f42b71112efe7ac63654d55f41cd74ca569b1ae` in the dedicated nested checkout and regenerated client; no migration/source edits by this agent.
- Dependency gate passed; durable claim `bf492864a38293c9ec9cf0f23c76043fb4745ba6`, attempt1, executor codex.

### Deviations

None. Root's bounded30s operator plan instruction was implemented within the same task/claim. Latest Architect Review is Pending; no Changes Requested items exist and no architect decision is asserted.

### Assumptions

Protected external evidence and actual messaging-worker deployment/environment proof are truthfully attested by root. Historical generic database events alone cannot prove code4. Internal cooldown timing does not guarantee provider quota reset.

### Unresolved Issues

None for implementation. Both exact-head CI runs passed. Live rollout/drain/repair and post-cooldown verification remain root-owned and were not executed here.

### Architectural Concerns

None requiring further schema/Shared work. Accepted Database002 is the durable carrier; config/audit JSON, in-memory state and Redis are not used as replacement cooldown state.

## Architect Review

### Review Status

Accepted

### Review Notes

Independently inspected exact source `b3576d7c67c8940f686dd16c1db84d1d3f35c17d` and final report `aa54aee64a48e4bd705d49469cec3ec3deb0727f`. Dedicated app/environment SQL state fences acquisition, completion and throttling by owner/generation/unexpired lease. The bounded90s sample operation fits its120s lease; provider HTTP phases recheck current lease/config outside transactions. Numeric403/code4 starts persisted bounded cooldown; other403 remains blocked. Ready-only deferral does not mutate admitted/submitted intent. Historical recovery requires exact operator-attested external evidence and reviewed source/history/CAS; legacy generic rejection is not treated as durable code4 proof. No findings.

### Reviewed Files

- `app-operation.ts`, `image-header-sample.ts`, `meta-graph.adapter.ts`, `service.ts`, `repository.ts`, `contracts.ts` in `src/services/meta-template-management/`.
- `preclaim-recovery.ts`, `throttle-recovery.ts`, operator CLI and operations documentation.
- Actual app-throttle PostgreSQL integration suite, app-operation/operator/classifier units and accepted nested Database gitlink.
- Canonical Completion Report and prepared execution packet.

### Validation Reviewed

Meaningful prior-source classifier red/green,114 focused units,33 actual PostgreSQL cases, lint/types/Prisma generation/build and CLI refusal inspected. Both exact-head CI runs43424471889/43424645194 passed386files/4229tests. Actual tests cover competing replicas, stale ownership, saturated backoff, new rows/cycles, no CREATE/POST intent, source/config/unknown-history refusal, exact recovery/replay and atomic audit/CAS rollback. Canonical physical isolation/synchronization/recursive evidence conforms. No redundant broad rerun.

### Architecture Conformance

Conforms to accepted Database002 contract and production-compatible provider safety. Bounded30s serializable operator transactions retain20-ID cap; no automatic replay, unsupported cache, Shared/schema change or live action. Root retains source merge, rollout/drain and protected operational recovery.

### Follow-up

Root merged PR218 at `ce9d6e1017f553d307f21899c20f713d514189fd`; parent gitlink pins that exact merged implementation. Under the authorized manual checkpoint, promote terminal SYSTEM-TEST002 after dependency reconciliation; preserve accepted SYSTEM-TEST001 evidence. ARCH-075 remains In Progress pending live provider/common-layout operational acceptance.
