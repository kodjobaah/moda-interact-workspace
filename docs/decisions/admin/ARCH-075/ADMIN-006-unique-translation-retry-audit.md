---
id: ARCH-075-ADMIN-006
architecture_id: ARCH-075
title: Give each nonempty translation retry its own audit identity
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 5
executor: codex
claimed_at: 2026-11-13T11:41:06Z
attempt: 1
depends_on:
  - ARCH-075-ADMIN-005
enables:
  - ARCH-075-SYSTEM-TEST-002
created: 2026-11-13
updated: 2026-11-13
---

# Give each nonempty translation retry its own audit identity

## Architecture

ARCH-075; docs/architecture/ARCH-075-ordered-recovery-message-layout.md; coordinator moda_architect.

## Objective

Give each nonempty translation retry its own audit identity.

## Context

Actual repeated failed-locale retry hits the unique audit operationId constraint because requestFailedTranslationRetry reuses the same run:retry identity. The transaction rolls back after the second genuine retry. Existing test covers only an immediate empty duplicate, not fail→retry→fail→retry. Preserve the database unique constraint and historical audit records.

## Scope

Existing translations/repository.ts retry action audit identity and focused unit/actual PostgreSQL regressions. Use a server-owned bounded unique identity for each actual nonempty serialized retry decision; no new cross-service contract.

## Out of Scope

Shared/schema/migration, provider output/parser changes, automatic retry policy changes, audit deletion/constraint relaxation, live retry/provider/database action, source merges/deploy or unrelated refactor.

## Requirements

Under the existing definition/run advisory transaction lock, each genuinely nonempty retry transition creates exactly one unique auditable operation identity within existing column bounds. Concurrent/immediate repeated clicks after that transition remain empty no-ops with no extra audit. A later legitimate failure of the same locale/run may be retried with a distinct audit event while preserving earlier audits. Keep source/model/credential/failure eligibility, retry counters/status, completed/reviewed locales and transaction rollback semantics unchanged. Audit insertion failure rolls back all retry changes. Never drop/relax the unique index, delete audits, manually reset provider/item state or recreate runs as workaround. Reuse existing server identifier facilities; no browser-supplied attempt authority or duplicate generic crypto mechanism.

## Work Items

- [x] Reproduce fail/retry/fail/retry unique-audit rollback against existing code.
- [x] Correct only server-owned retry-decision audit identity.
- [x] Prove repeated/concurrent/no-op/rollback and completed-locale preservation, report and stop.

## Interfaces / Contracts

Existing Admin-only failed translation retry transaction and CommerceAuditEvent.operationId unique contract. Background batch processing and stored source hashes unchanged; no Shared release.

## Dependencies

ARCH-075-ADMIN-005

## Enables

ARCH-075-SYSTEM-TEST-002

## Acceptance Criteria

- [x] Two legitimate nonempty retries of the same failed run/locale both commit distinct truthful audits.
- [x] Concurrent/empty duplicate retry remains no-op, immutable completed results and all prior audits/unique constraint preserved.
- [x] Canonical isolation and required passing checks reported, no live mutation.

## Validation

- [x] Meaningful red/green actual PostgreSQL fail→retry→fail→retry, concurrent same cohort, empty replay, audit-failure rollback and completed locales unchanged.
- [x] Relevant translation units/native ESM tests, types/lint/build/security and exact-head repository check evidence.
- [x] Diff/privacy hygiene; no provider/database production writes.

## Stop Condition

After required scope/checks, submit review and STOP. Do not execute live repair, register providers, deploy, merge or begin follow-on tasks.

## Implementation Notes

You are not alone; preserve others. Canonical launcher packet owns startup/claim. Root owns all final integration and live operations. Generic logging uses published shared logging if changed. Return actual dependency gaps rather than inventing alternate protocol or local generic primitives.

## Completion Report

### Status

Ready for Review; source branch `task/ARCH-075-ADMIN-006`. Source commit `6c7ad51e27765d989d7b80caa071ee333344cc3b`; draft PR https://github.com/kodjobaah/moda-interact-admin/pull/94. No merge, deploy, live retry, provider call or live database mutation performed.

### Files Changed

- `src/lib/admin/whatsapp-templates/translations/repository.ts`: existing server UUID facility gives each nonempty locked retry decision its own bounded audit operation identity.
- `tests/integration/arch047-template-translations.postgres.test.ts`: actual repeated failure/retry, three concurrent requests, empty replay, historical audit and completed/reviewed/in-flight row preservation, original English preservation, real audit foreign-key rollback and unique index proof.
- `tests/unit/arch047-template-translations.test.ts`: maximum-length run identifier and distinct bounded retry audits with unchanged metadata/no-op behavior.

### Work Completed

Reproduced the actual PostgreSQL `operationId` unique-constraint failure on the second genuine retry before changing production source. Audit IDs now use at most 80 run-prefix characters plus `:retry:` and a server-generated UUID (maximum 123 characters within varchar128). UUID creation remains inside the existing transaction/advisory lock after the nonempty decision and actor guard. The full run ID remains in metadata. Historical audits, global unique index, retry eligibility/counters, source/model/credential selection and completed results are unchanged. No schema, Shared, UI or provider changes.

### Validation Results

- `npm run test:arch047-admin-translations:postgres`: red reproduced `P2002`/unique `operationId` failure on second genuine retry, green2/2 passed, zero skips (~9.8s test execution; full disposable schema setup also completed).
- `npm run test:arch047-admin-translations:unit`:17/17 passed, zero skips (~4.4s).
- `npm run test:unit`:800/800 passed, zero skips (~185.6s).
- `npx tsc --noEmit`: passed.
- `npm run lint`: passed, zero errors; one existing nested database default-export warning.
- `npm run build`: passed including generated routes; existing BullMQ dynamic/optional Valkey dependency warnings only.
- `npm test`:334/334 passed, zero skips, run after build (~53.0s).
- `git diff --check`: passed; final source worktree clean after commit/push. Temporary validation helper exited0.
- Exact source head contains no `.github/workflows` files; no GitHub Actions configured. Exact-head Vercel and Preview Comments both passed. These remote checks supplement the actual local declared checks.

Evidence logs `/tmp/moda-admin006-{pg-red,pg-green,focused,unit,types,lint,build,security}.log`. The disposable test exercises the actual existing migrations and Prisma transaction; the audit-failure fixture uses a missing actor FK, causing rollback after item/run/definition updates.

### Deviations

No scope deviations. Initial validation needed `/usr/local/bin` added to temporary helper PATH because the restarted tool environment did not resolve the installed Docker binary. One missing brace in the new REVIEWED fixture was corrected before the meaningful red run. No repository launcher or environment configuration was changed. Next bundled server-function guidance was read (same installed repository version); all test environments scrub inherited credentials and use synthetic local URLs. No browser verification is required for this server-only identity change.

### Assumptions

The existing eligible-item policy and advisory transaction lock remain authoritative. UUID identifiers are server-owned; callers supply no retry-attempt authority.

### Unresolved Issues

None. All required checks and supplementary exact-head Vercel/Preview Comments passed.

### Architectural Concerns

None introduced. No live operations or data repair performed; root retains integration/deployment and the authorized UI retry.

### Canonical Execution Evidence

- Prepared packet `/tmp/moda-arch075-admin006-prepare.json`, prepared execution true; claim `5ff67a497bfa9b6a9e21113980c17cd487c5be9c`, attempt1, executor codex. No repeated claim/startup.
- Canonical workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-075-ADMIN-006`, branch `task/ARCH-075-ADMIN-006`.
- Implementation `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-075-ADMIN-006`, same task branch; source base `e52ecdb373a526f07710ecabfb7b3cefabab5018`.
- Parent/implementation remote task fast-forward both not-needed; origin/main both already-current according to the authoritative preparation packet.
- Recursive submodule sync/update passed; database `5329d5390d346042895219663f3a040ea54ae168` initialized. No gitlink change staged.
- No shared/default checkout mutation, no other task worktree reused, no force push or main merge.

## Architect Review

### Review Status

Accepted

### Review Notes

Independently inspected exact implementation `6c7ad51e27765d989d7b80caa071ee333344cc3b` and canonical report `28fbb5c25c1904731425aa7a27f7f10e84c5c9e1`. The only runtime change creates a server-owned UUID audit identity inside the existing locked nonempty retry transaction. Maximum identity length is 123, within varchar128. Concurrent and immediate empty retries remain no-ops; later genuine failures receive distinct audits. Existing authorization, item eligibility, source hashes, counters, completed results, unique constraint and transaction boundaries remain unchanged. No findings.

### Reviewed Files

- `src/lib/admin/whatsapp-templates/translations/repository.ts`
- `tests/integration/arch047-template-translations.postgres.test.ts`
- `tests/unit/arch047-template-translations.test.ts`
- Assigned Completion Report and canonical preparation packet.

### Validation Reviewed

Actual PostgreSQL prior-source P2002 reproduction followed by 2/2 passing cases; real repeated/concurrent retry, empty replay, completed-row preservation and audit-FK rollback assertions inspected. Focused17, full800, security334, types/lint/build/diff and exact-head Vercel/Preview Comments passed as reported. Canonical isolated parent/implementation paths, synchronization, recursive submodules and claim evidence verified. No redundant broad rerun.

### Architecture Conformance

Conforms to bounded Admin-only retry correction and compatible rollout. No Shared/schema/provider changes or live operations. Automatic completion applies; source merge and rollout remain root-owned.

### Follow-up

Root merged PR94 at `e0699c99e82f12fd8c2a778f38a0a44cebb8a2cf`; parent gitlink pins that merged implementation. Deployment verification and the existing authorized UI retry remain root-owned. SYSTEM-TEST002 remains Pending until all implementation dependencies are accepted and the manual checkpoint is satisfied. ARCH-075 remains In Progress pending live operational acceptance.
