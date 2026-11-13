---
id: ARCH-075-BACKGROUND-005
architecture_id: ARCH-075
title: Recover proven preclaim missing-app registration blocks
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 5
executor: codex
claimed_at: 2026-11-13T09:07:11Z
attempt: 1
depends_on:
  - ARCH-075-BACKGROUND-004
enables:
  - ARCH-075-SYSTEM-TEST-001
created: 2026-11-13
updated: 2026-11-13
---

# Recover proven preclaim missing-app registration blocks

## Architecture

ARCH-075; docs/architecture/ARCH-075-ordered-recovery-message-layout.md; coordinator moda_architect.

## Objective

Recover proven preclaim missing-app registration blocks.

## Context

Actual staged registration encountered missing worker META_APP_ID before durable creation intent. BLOCKED rows cannot normally recover. Separately Admin confirmation accepts English SOURCE_SAVED while Background correctly requires REVIEWED; reviewing English only after provider approval is circular. These are concrete distinct owned gaps; preserve all accepted content/transport work.

## Scope

Existing Meta management repository/service and a bounded operator-only dry-run/apply recovery command/domain method; immutable manifest/audit and focused unit/PostgreSQL tests. No automatic broad retry of BLOCKED rows.

## Out of Scope

Other repositories, Shared publication/schema, provider guard weakening, uncertain template-create retry, live provider/database/configuration writes, source merges, automatic activation or unrelated refactors.

## Requirements

Recover only exact BLOCKED/META_APP_ID_MISSING_OR_INVALID registrations in reviewed bounded manifest (at most20 IDs per operation), repaired trusted app/WABA configuration and current unchanged frozen reviewed source. Require providerTemplateId/lastSubmittedAt absent and no historical CREATE_INTENT, POST_INTENT or other evidence of submission claim/HTTP creation. Lock/CAS exact id,WABA,state,reason,updatedAt and expected immutable snapshot identity; any mismatch/otherfailure/unknown/submitted row refuses. Atomically audit truthful preclaim recovery and set READY_TO_SUBMIT/due through domain method, without resetting history/counters, sending provider requests or creating a new registration. Dry-run default, explicit apply+manifest digest; repeat no duplicate transition/audit. Keep ordinary claim/reconciliation/provider-absence guards unchanged. Live historical20 recovery root-owned only after source acceptance, trusted config and English review repair; task agent does not execute it.

The repaired META_APP_ID configuration proof must refer to the actual messaging worker process that starts startProductionMetaTemplateDuePoller (accepted src/entrypoints/messaging.ts), not the merchant-communications translation worker. Root owns environment correction; no live repair before the correct process is configured and reviewed-source proof holds.

## Work Items

- [x] Confirm owning defect and implement only bounded capability.
- [x] Prove meaningful failure/race/compatibility behavior.
- [x] Complete checks, mirrored Completion Report and stop.

## Interfaces / Contracts

Existing Admin confirmed Meta registration and Background immutable provider lifecycle; Gateway owns runtime variable declaration. No new cross-service payload, setting, schema or Shared release. Runtime provider config remains server-owned and no secrets enter diagnostics.

## Dependencies

ARCH-075-BACKGROUND-004

## Enables

ARCH-075-SYSTEM-TEST-001

## Acceptance Criteria

- [x] Assigned bounded gap corrected without weakening permission/provider identity or immutable source guards.
- [x] Negative/race/idempotency behavior and unchanged legacy domain semantics proven where applicable.
- [x] Canonical physical isolation/synchronization and exact checks documented; no live action by agent.

## Validation

- [x] Red/green exact missing-app preclaim blocked recovery; dry-run/no mutation, digest/config/source/WABA mismatch, CREATE/POST intent, providerId/lastSubmitted, foreign/uncertain/otherblocked refusal, concurrency/CAS/replay and audit rollback. Real PostgreSQL proof plus focused Meta-management tests/types/scopedlint/exact-head full CI.
- [x] Diff/privacy hygiene and no unauthorized external mutation.

## Stop Condition

After required scope/checks, submit review and STOP. Do not execute live repair, register providers, deploy, merge or begin follow-on tasks.

## Implementation Notes

You are not alone; preserve others. Canonical launcher packet owns startup/claim. Root owns all final integration and live operations. Generic logging uses published shared logging if changed. Return actual dependency gaps rather than inventing alternate protocol or local generic primitives.

## Completion Report

### Status

Ready for Review. Implementation and validation complete; awaiting moda_architect review.

### Files Changed

Implementation `daf7ed60042ff7977c34ef219d6bdcf855e9bb17` on `task/ARCH-075-BACKGROUND-005`; draft PR https://github.com/kodjobaah/moda-interact-background/pull/216:

- `src/services/meta-template-management/preclaim-recovery.ts`: bounded Background-local operator domain method, strict manifest/argument validation, trusted configuration preflight, source/snapshot identity, row/source locks, serializable transaction/CAS and durable audit.
- `scripts/recover-meta-preclaim-app-block.mjs`: explicit operator CLI; planning/dry-run default, apply requires exact digest. Bounded failure receipts contain no credentials/source bodies/raw database errors.
- `docs/operations/recover-meta-preclaim-app-block.md`: concrete operator procedure, reviewed artifact/digest, actual messaging-worker proof and root-only live prerequisites.
- `tests/unit/services/meta-template-management/preclaim-recovery.test.ts`: malformed/unbounded manifests, CLI flags, digest/config and wrong runtime-proof boundary.
- `tests/integration/arch075-preclaim-recovery.integration.test.ts`: disposable PostgreSQL behavior, refusal, legacy compatibility, concurrency, CAS and atomic rollback.

### Work Completed

Confirmed the existing dead end: `submitPreparedRegistration` returns `NOT_READY_TO_SUBMIT` for BLOCKED rows even after configuration repair; normal discovery/claim never retries them. Added only an explicit operator capability for at most 20 unique exact IDs. Plan has no writes and produces a manifest pinning operator, app/WABA, exact updatedAt, immutable registration transport and current reviewed locale/source/reviewer identity. Apply requires the exact manifest digest. Every existing event must be a matching preclaim missing-app SUBMISSION_BLOCKED receipt; CREATE/POST intents, results, webhook/reconciliation/unknown events, request/HTTP/provider evidence, missing provenance, submitted/uncertain/foreign/other-failure rows refuse. Current target and source (including English) must be reviewed and unchanged.

Apply locks registration/source rows, checks state/reason/WABA/updatedAt and frozen identity, and atomically makes only the existing rows READY_TO_SUBMIT/due with a PRECLAIM_APP_RECOVERY audit containing the reviewed manifest/digest. Counters/history are retained. CAS, serialization, stale batch member or audit failure rolls back the batch. Identical replay adds no audit/transition while still unchanged/unclaimed; replay refuses once ordinary submission has advanced. No automatic retries, worker/HTTP wiring, provider requests, new registrations, source review edits or activation were added. Normal claim/reconciliation/provider-absence behavior is unchanged.

Amendment `995f008c7` implemented: the manifest requires a bounded deployment-proof reference with fixed `moda-messaging-worker` identity. Documentation explicitly ties META_APP_ID proof to `src/entrypoints/messaging.ts` / `startProductionMetaTemplateDuePoller`, never the translation worker. The reference is an operator attestation; this command reads its own trusted server configuration and does not inspect a remote deployed process. Root must establish actual messaging-worker runtime proof before live execution.

Self-review: five new owned files only; no existing hot/action worker path modified; all queries are operator-only bounded exact-ID work. No queue, schema, dependency, Shared contract or generic logging change. No live database/provider/configuration mutation or requests by this agent. Latest Architect Review is Pending; no Changes Requested items exist and no architect decision is asserted.

### Validation Results

- Red: disposable PostgreSQL test using the legacy submit retry with repaired synthetic configuration failed exactly once (`BLOCKED` instead of required `READY_TO_SUBMIT`; 19 other tests passed). The same scenario then exercised explicit recovery for green; legacy busy/claim guard assertions remain in the committed test.
- Green: `node scripts/test-integration.mjs tests/integration/arch075-preclaim-recovery.integration.test.ts tests/integration/arch047-meta-template-management.integration.test.ts`: 2 files / 21 tests passed. Real disposable PostgreSQL/Redis only. Proves dry-run no mutation, exact digest, stale source/reviewer/config/WABA, English SOURCE_SAVED refusal, missing/CREATE/POST/other history, providerId/lastSubmitted/uncertain/other failure refusal, concurrent apply, CAS lost, replay, whole-batch rollback and audit rollback, plus unchanged existing Meta intent/webhook semantics.
- `npx vitest run tests/unit/services/meta-template-management`: 7 files / 98 tests passed.
- `npm run prisma:generate`, `npx tsc --noEmit` and `npx tsc`: passed.
- Scoped `npx eslint src/services/meta-template-management/preclaim-recovery.ts tests/unit/services/meta-template-management/preclaim-recovery.test.ts tests/integration/arch075-preclaim-recovery.integration.test.ts scripts/recover-meta-preclaim-app-block.mjs`: passed.
- Compiled CLI smoke `node scripts/recover-meta-preclaim-app-block.mjs --manifest missing.json --apply`: truthful bounded RECOVERY_ARGUMENTS_INVALID refusal before database access because digest is absent.
- `git diff --check`: passed. Five new owned files only; no dependency/schema/runtime-policy expansion or secret/customer content.
- Exact-head full CI passed (Prisma generation, TypeScript and full unit suite: 383 files / 4,197 tests): push run https://github.com/kodjobaah/moda-interact-background/actions/runs/43400908141 and PR run https://github.com/kodjobaah/moda-interact-background/actions/runs/43400968781 for `daf7ed60042ff7977c34ef219d6bdcf855e9bb17`.

### Physical Worktree Isolation and Launcher Evidence

Preparation packet `/tmp/moda-arch075-background005-prepare.json` supplied the following; preparation/claim was not repeated:

- Canonical workspace root `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-075-BACKGROUND-005`, reused; branch `task/ARCH-075-BACKGROUND-005`.
- Implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-075-BACKGROUND-005`, created by launcher; same mirrored task branch.
- Shared workspace/implementation checkouts switched or mutated for task work: no; another task worktree reused: no.
- Parent and implementation remote-task fast-forward: not-needed; both origin/main incorporations: already-current.
- Recursive submodule sync/update: passed; database initialized at recorded `a9b6ab852a8245dfd14447808aac288a23b113d0`, unchanged.
- Explicit dependency gate passed; claim `677b8017b47324bb7da7b1c20441d51424339d5b` pushed, attempt 1, executor codex.

### Deviations

None. Runtime-proof amendment was read and implemented on the same prepared claim/branches.

### Assumptions

The operator evidence reference truthfully points to actual messaging-worker deployment/configuration proof. No command-local check can establish another deployed process's environment; root owns that external proof and all live execution.

### Unresolved Issues

No implementation issue remains. Live recovery was not executed and remains root-owned after source acceptance, correct actual-process configuration and English review repair.

### Architectural Concerns

None requiring schema/Shared changes. Making rows due intentionally permits later ordinary worker submission; operator procedure records this consequence and preserves all ordinary submission guards.

## Architect Review

### Review Status

Pending

### Review Notes

Pending implementation.

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

None
