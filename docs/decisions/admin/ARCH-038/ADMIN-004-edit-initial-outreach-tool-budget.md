---
id: ARCH-038-ADMIN-004
architecture_id: ARCH-038
title: Edit the initial outreach tool-call policy
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 10
executor: codex
claimed_at: 2026-11-13T16:06:38Z
attempt: 1
depends_on:
  - ARCH-038-DATABASE-003
  - ARCH-038-ADMIN-003
enables: []
created: 2026-11-13
updated: 2026-11-13
---

# Edit the initial outreach tool-call policy

## Architecture

ARCH-038; docs/architecture/ARCH-038-commerce-agent-execution-budget-policies.md; coordinator moda_architect.

## Objective

Edit the initial outreach tool-call policy without losing current main behavior or the verified local backup.

## Context

Dependency integration verified: Database source PR77 main `2e14f8668346dfc135aa12f8d1fbc94e05c12ce7`, accepted parent PR1016 `5bb98c073fd6c167a89da56f7a899c9dd457af18`. Root verified TEST then PROD hosted rollout on2026-11-13 (16:03:51Z/16:04:20Z):80 finished migrations, zero unfinished/checksum mismatches,10 policy rows/five missing LIVE defaults16, other fields preserved, guard enabled O. The hosted pre-merge schema gate is satisfied; owning Admin validation/review remains mandatory.

Read-only comparison shows12 production files plus9 budget tests missing from current main. Background already resolves/enforces this field. Two other local template-impact edits are already incorporated in current main and must not be reapplied or used to overwrite newer tests.

## Scope

Recover the missing backed-up initialOutreachToolCalls policy controls across existing Platform/Price Plan/Merchant editors and new-plan wizard, with their directly related tests.

## Out of Scope

Template impact changes already in main, database/migration implementation, Background/Commerce source, Shared publication, live policy edits and main integration.

## Requirements

- Reuse existing platform/plan/shop JSON policy, schemaVersion1, authorization, trusted scope/environment, audit reason, CAS/editVersion and per-field inheritance; bounded initialOutreachToolCalls is a positive safe integer1–64, legacy read fallback16. Do not introduce another setting or Shared release.
- Platform writes must not silently reset a saved value when an old cached two-field form omits the new field. Require explicit valid value on the new full Platform form, or preserve the trusted current persisted value under the same CAS; never default a missing writer value to16. Legacy persisted two-field READ compatibility remains16. Add the missing-form regression.
- Third-field-only Platform changes must count as real edits and audit atomically. Plan/shop sparse overrides can inherit/clear independently, label effective source correctly and preserve untouched other budgets. New-plan wizard validates/serializes the optional override with reason in its existing atomic save.
- Preserve current main's template-impact/greeting/providerguard/frozenhash/stalestatus tests; local old whole-file test versions are not authoritative. Port only the missing budget delta from the verified backup.
- Do not raise runtime deadlines, change ordinary conversation turns or merchant billing, mutate live policies, or enable writers before accepted Database003 and root-verified hosted schema rollout. Existing Studio initial-outreach runtime policy semantics remain unchanged.

## Work Items

- [x] Verify task-owned backup provenance and fresh-main overlap classification.
- [x] Incorporate only the missing bounded behavior and necessary regression tests.
- [x] Complete required validation, mirrored publication and truthful report; return review and stop.

## Interfaces / Contracts

Existing architecture-owned contracts and current published dependencies remain authoritative. No new Shared release is required. Original local files are evidence, not a replacement mainline. Root verified all15 Git bundles, staged/unstaged binary patches and nonignored untracked archives at external moda-local-reconciliation-backup-20261113T145749Z before any reconciliation writes; preserve that backup and primary originals. Never publish credential exports, operator scratch scripts, transcripts or generated artifacts as product source.

## Dependencies

ARCH-038-DATABASE-003, ARCH-038-ADMIN-003

## Enables

None

## Acceptance Criteria

- [x] Scoped missing functionality is incorporated with newer main behavior preserved.
- [x] Relevant trust/lifecycle/audit/immutability boundaries and explicit negative behavior remain enforced.
- [x] Required checks and exact source/backup/worktree/synchronization evidence recorded; no live mutation or unrelated publication.

## Validation

- [x] Focused boundary/malformed/missing/stale-form tests; platform third-field-only audit/CAS/no-op checks; sparse inheritance/clear/current-plan switching; wizard validation/atomic save; relevant existing policy/page/drawer/authorization tests, actual declared typecheck/lint/build and exact-head CI. No live writes.
- [x] Diff/privacy hygiene and task-owned file whitelist; original backup/primary changes remain intact.

## Stop Condition

After scoped work and required validation, publish matching task branches, set review and return to moda_architect. Do not self-accept, merge main, deploy, execute hosted writes or start another task.

## Implementation Notes

Root verified the current Admin Blueprint build/start has no migration hook. Updating the nested Database gitlink or building Admin does NOT apply the SQL guard. Root must apply only the accepted tested new migration to TEST then PROD, verify complete ledger/checksum/no-other-pending evidence, and only then merge Admin004 to main (which can auto-deploy new writers). Historical6afd migration is already finished in both environments and must not be replayed. Task executor performs no hosted DDL; record this concrete pre-merge gate in the Completion Report.

You are not alone; do not revert or absorb others' edits. Use normal launcher preparation and dedicated matching parent/implementation task worktrees. No old task worktree reuse or shared checkout mutation. Root owns final integration and operational rollout. Return genuine new cross-repository/schema/contract gaps before widening scope.

## Completion Report

### Status

Ready for Review. Implementation PR95: https://github.com/kodjobaah/moda-interact-admin/pull/95 ; exact pushed source `6547c2d996e719626ccb6c43c0f10c99f712295b`. Main integration remains root-owned.

### Files Changed

12 production budget files under `src/components/admin/commerce-model-policy/`, `src/components/admin/merchant/merchant-pricing-plan-builder.tsx`, its `commerce-agent-policy-step.tsx`, and the five `src/lib/admin/commerce-model-*-policy*.ts` modules. Twelve directly related `tests/unit/commerce-model-*.test.*` files cover controls, parsing, wizard, inheritance and transactional mutations. Nested `database` reference advances to accepted main `2e14f8668346dfc135aa12f8d1fbc94e05c12ce7`. No template publication file/test was changed.

### Work Completed

- Recovered the 21 missing budget file deltas from the verified backup; retained current main's already-incorporated publication behavior and newer provider/frozen-hash/stale-status regressions. The untracked operator install script remains private and preserved.
- Added the positive safe integer 1–64 initial outreach budget to Platform, Price Plan, Merchant and new-plan editors. Reads retain legacy default16; sparse overrides inherit/clear independently and report their effective source, including current-plan switching and no-contract fallback.
- Corrected the recovered writer's unsafe missing-field fallback. Captured two failing regressions before correction: a cached two-field form could reset saved32 to16. Such Platform writes now fail validation before transactions. Third-field-only changes use existing CAS and atomic audit; unchanged forms remain no-ops. Plan/shop explicit clearing is preserved.
- Existing authorization, trusted scope/environment, audit reasons and new-plan atomic policy-save path remain authoritative. No Shared release, hosted mutation, deadline increase or ordinary-conversation/billing change.

### Validation Results

At the exact committed source (no source edits after validation), Node24.19.0/npm11.17.0 from canonical bootstrap:

- Focused `node --conditions=import --import tsx --test tests/unit/commerce-model*.test.ts tests/unit/commerce-model*.test.mjs`:113 passed,0 failed. Includes boundaries, malformed/missing inputs, read compatibility, cached-form rejection, third-field-only changes, stale/CAS loss, atomic audit rollback/no-op, sparse clearing/current-plan inheritance and wizard serialization/reason checks.
- `npm run prisma:generate`: passed against accepted nested Database schema.
- Declared `npm run test:unit`:812 passed,0 failed,0 skipped. Includes newer publication, page/drawer and authorization coverage.
- Declared `npm test`:331 passed,0 failed;3 runtime tests initially skipped because no production build existed. After build, `node --test tests/observability/admin-telemetry-bootstrap.test.mjs`:3 passed,0 skipped (real production server preload/export/failure isolation).
- `npx tsc --noEmit`: passed (no declared typecheck script).
- `npm run lint`: passed,0 errors; one unchanged nested Database anonymous-default-export warning.
- `npm run build`: passed, Next16.3.3 webpack compilation/typecheck/prerender. Optional BullMQ Valkey module warnings remain warnings; no dependency files changed.
- `git diff --check`, task-owned whitelist, clean nested submodule/source worktree and publication-file preservation: passed. No credentials, backups, operator scratch scripts or generated artifacts staged.
- Exact-head remote inventory: no GitHub Actions workflows; Vercel Preview Comments check succeeded. Vercel deployment status pending at report preparation; root must inspect final exact-head status before integration. No claim of completed remote deployment/CI.

Private command logs are retained under primary `local-backups/arch038-admin004-*.log`, not published.

### Preservation / Worktree / Synchronization Evidence

Canonical prepared packet: primary `local-backups/arch038-admin004-prepared.json`; Attempt1 durable parent claim `f85d8b069f21a10f183e69b942dee3432c817a98`. Primary workspace is `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; launcher parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-038-ADMIN-004`; implementation `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-038-ADMIN-004`; matching `task/ARCH-038-ADMIN-004` branches. Launcher fetched/synchronized both repositories and initialized/verified recursive submodules; implementation started from fresh Admin main `e0699c99e82f12fd8c2a778f38a0a44cebb8a2cf`. No shared checkout switch or primary source mutation occurred.

External root backup `moda-local-reconciliation-backup-20261113T145749Z/moda-interact-admin/unstaged.patch` verified SHA256 `e869f5d774e3cd81fd7614d4ad42760f53484e586552affea839c9051c815795`; primary `git diff --binary --full-index` still matches that hash after implementation. Selective budget patch SHA256 `d0a438b07e0cd7ed40fa7640c3af77a8529b2030d18db9bc3e7edd784f9e0d40`, apply-check passed. Root separately verified all105 backup artifacts unchanged. No original local change was discarded.

### Dependencies / Hosted Gate

Accepted DB003 main `2e14f8668346dfc135aa12f8d1fbc94e05c12ce7`; root verified TEST16:03:51Z then PROD16:04:20Z on2026-11-13:80 finished migrations,0 unfinished/checksum mismatch, five missing LIVE budgets initialized16 only, other policy fields preserved, guard enabled O. The hosted schema prerequisite is satisfied by root evidence; this executor did not run hosted DDL or policies. Admin build/reference updates do not apply migrations.

### Deviations

Added three further parser/new-plan test files beyond the nine backed-up test deltas to prove explicit negative boundaries. No product scope expansion. Remote Vercel deployment completion remains an integration gate.

### Assumptions

Root owns final main integration and operational rollout. Existing Background already enforces this exact policy contract; no Shared release is required.

### Unresolved Issues

Await final exact-head Vercel status and architect review; do not merge while a required remote check is pending or failed. No application validation failures remain.

### Architectural Concerns

None newly discovered. Retain existing deployment/migration separation and preserved backup.

## Architect Review

### Review Status

Pending

### Review Notes

None

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending implementation review

### Follow-up

No architecture completion or production capability claim follows from local source incorporation alone.
