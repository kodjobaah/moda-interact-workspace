---
id: ARCH-075-ADMIN-003
architecture_id: ARCH-075
title: Preserve common website binding in translation snapshots
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
claimed_at: 2026-11-13T05:22:11Z
attempt: 1
depends_on:
  - ARCH-075-ADMIN-002
  - ARCH-075-SHARED-004
enables:
  - ARCH-075-SYSTEM-TEST-001
created: 2026-11-13
updated: 2026-11-13
---

# Preserve common website binding in translation snapshots

## Architecture

ARCH-075; docs/architecture/ARCH-075-ordered-recovery-message-layout.md; coordinator moda_architect.

## Objective

Preserve common website binding in translation snapshots.

## Context

A saved common wrapper is valid under authoring/compiler but Admin translation segment validation rejects its canonical shop.websiteUrl protected variable before a run can start. Accepted source/activation tasks remain unchanged. This correction preserves translation transport integrity rather than adding another frame authority.

## Scope

Fix translations/source-snapshot.ts protected semantic allowlist parity for shop.websiteUrl; cover actual canonical common-wrapper extraction, immutable source snapshot, translation reconstruction and failure boundaries. Reuse published semantic contract where directly suitable; do not broaden unknown semantic acceptance or change marker/hash bytes.

## Out of Scope

Live definition edits, translation/provider requests, activation, production replay/reset, source merges, new schemas/packages, broad translation refactors or permission workarounds.

## Requirements

Preserve canonical common source hashes, exact protected marker identity/count and semantic variables. Reject unknown variables at existing strict boundaries, missing/duplicate/unregistered markers, changed hashes and malformed snapshots. No normalization/dropping protected tokens or silent retry. Use synthetic fixtures representing the actual common header name/website and checkout conditional, not private production content. Do not duplicate a generic cross-service parser; report a genuine Shared gap rather than publishing opportunistically.

## Work Items

- [x] Confirm the exact owning producer/consumer boundary and reproduce relevant regression.
- [x] Implement only the bounded parity correction or consumer test coverage.
- [x] Complete validation, mirrored report and stop.

## Interfaces / Contracts

Published Shared 5.13.9 canonical shop.websiteUrl semantic binding; existing Admin translation source snapshot and Background protected-marker transport. Preserve existing versions and hashes; no new contract is authorized.

## Dependencies

ARCH-075-ADMIN-002, ARCH-075-SHARED-004

## Enables

ARCH-075-SYSTEM-TEST-001

## Acceptance Criteria

- [x] Canonical common website binding survives actual translation snapshot/codec path with exact identity.
- [x] Negative marker/hash/unknown semantic boundaries remain strict; legacy supported inputs unchanged.
- [x] Canonical physical isolation, synchronization and exact validation evidence reported with no live writes.

## Validation

- [x] Meaningful focused positive/negative regression through actual owning boundary; Admin must demonstrate red before correction.
- [x] Repository-declared relevant tests, typecheck/lint/build and exact-head CI or documented repository check configuration.
- [x] Diff/privacy hygiene and no live provider/database mutation.

## Stop Condition

After scope and required checks complete, set review, submit mirrored Completion Report and STOP. No dependent implementation or live action.

## Implementation Notes

You are not alone; preserve other changes. Canonical prepared packet owns startup/claim. Existing accepted tasks must not be rewritten. Root owns merges and live verification.

## Completion Report

### Status

Ready for architect review. Implementation committed and pushed; all local and exact-head supplementary validation complete. No live definition changes, translation/provider requests, activation or other live mutations performed.

### Files Changed

- `src/lib/admin/whatsapp-templates/translations/source-snapshot.ts`: adds only `websiteUrl` to the existing exact `shop` semantic allowlist.
- `tests/unit/arch075-common-website-translation.test.ts`: six synthetic regression tests through actual extractor, immutable snapshot creation and reconstruction/compiler boundaries.

### Work Completed

Confirmed on accepted Admin source that the valid canonical common wrapper failed during protected-token validation, before model lookup or translation-run creation. The action intentionally hides the unrecognized internal exception behind its generic message. Reproduced locally without database or provider calls. Background's existing codec accepts bounded semantic hints and preserves exact marker identity; no duplicate parser, Shared contract change or package publication was needed.

The one-line correction admits the published `shop.websiteUrl` binding without changing snapshot version, marker generation, source/content hash algorithms or unknown-variable validation. Tests use the existing synthetic common header (shop name/website), structural response slot and conditional checkout footer; no private production copy or identifiers are included.

Tests assert fixed golden marker bytes, source/prepared integrity and immutable English input; actual French reconstruction preserves website semantic identity, the response slot and final checkout variable. Negative cases retain strict rejection for unknown semantic names, missing/duplicate/unregistered protected markers, changed source/prepared/output hashes, malformed snapshot version and mutated source text. The legacy name/checkout case retains its marker bytes unchanged.

### Validation Results

- Red before correction: five new tests failed at `Unknown protected semantic variable`; the legacy case passed. `/tmp/moda-admin003-red.log`.
- Green focused regression: 6/6 PASS. `/tmp/moda-admin003-green.log`.
- Declared translation suite: 16/16 PASS (`npm run test:arch047-admin-translations:unit`).
- Declared compilation suite: 15/15 PASS (`npm run test:arch047-admin-compilation:unit`).
- Full declared unit suite: 794/794 PASS (`npm run test:unit`).
- TypeScript: PASS (`npx tsc --noEmit`).
- Declared lint: PASS, with the existing nested Database default-export warning only.
- Production build: PASS (`npm run build`).
- Security/observability: 334/334 PASS with zero skips (`npm test`, after build).
- No GitHub Actions workflow is configured in exact source head. Exact-head Vercel and Preview Comments: PASS (root verified `12c86b8ecb4549946ce910bd2d9072832844e0e2`, 2026-11-13 05:30:48 UTC).
- Final diff/privacy hygiene: PASS; exactly the narrow source validator and synthetic regression test changed.

Native ESM runners use the real published dependency and actual compiler/parser functions. Environment was scrubbed to localhost dummy DB/Redis addresses and a synthetic test-only AUTH_SECRET. No new database code was introduced, so no additional PostgreSQL fixture was required by this bounded pure validation correction. No UI was changed and no browser visual-pass claim is made.

### Deviations

None. Repository source changes were made directly in the canonical Admin003 worktree after the updated runtime allowed it. Root installed the existing pinned dependencies/generated Prisma; this agent did not duplicate installation or preparation. No test assertion was weakened and no fixture repair was necessary.

### Assumptions

The existing saved production English source remains immutable and can be retried through the authorized UI after root-owned merge/deployment. Source tests do not constitute provider translation success or live activation approval.

### Unresolved Issues

Live translation retry, review, provider registration and activation remain root-owned operational work after source acceptance/deployment. This task performs none of those actions.

### Architectural Concerns

The owner gap was an Admin-local whitelist lag, not a new Shared capability. Background codec regression is separately owned; no cross-service parser duplication or transport widening was introduced.

### Physical Worktree Isolation

- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-075-ADMIN-003`, branch `task/ARCH-075-ADMIN-003`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-075-ADMIN-003`, branch `task/ARCH-075-ADMIN-003`.
- Prepared packet `/tmp/moda-arch075-admin003-prepare.json`: prepared_execution true, claim attempt1 codex, committed/pushed `a69a396edb26f3c1b127cca72137cb9f67e36a21`.
- Parent remote-task fast-forward not-needed; origin/main already-current; recorded head `6069aee95a74150095e1c3775f4ff63aeb20cd35`.
- Implementation remote-task fast-forward not-needed; origin/main already-current; source base `c2cd4610f399c7356d1607799f5129ac7d2356d3`.
- Recursive submodule sync/update passed; Database commit `5329d5390d346042895219663f3a040ea54ae168`.
- Shared/default checkout switched or mutated: no. Another task worktree reused: no. Startup/claim repeated: no.

### Source Checkpoint

- Source commit: `12c86b8ecb4549946ce910bd2d9072832844e0e2`, pushed; worktree clean.
- Draft source PR: https://github.com/kodjobaah/moda-interact-admin/pull/91.
- Parent report committed/pushed on the assigned feature branch; final hash recorded in handoff.
- No merge to main or force-push by this agent.

## Architect Review

### Review Status

Accepted

### Review Notes

Accepted exact source `12c86b8ecb4549946ce910bd2d9072832844e0e2` and mirrored report `364d8ea5e12e008ba85a4a97507b56293660c008`. The actual producer defect was one missing canonical shop.websiteUrl alternative in the existing strict protected-variable allowlist. Independent source/test inspection confirms no unrelated runtime widening or contract/version change.

### Reviewed Files

`translations/source-snapshot.ts`; `tests/unit/arch075-common-website-translation.test.ts`; actual extraction, snapshot and reconstruction boundaries exercised by those tests.

### Validation Reviewed

Meaningful red proof: five failures and one legacy pass before the correction. Final six regressions, 16 translation tests, 15 compilation tests, 794 full units, types, lint, build and 334 security/observability checks passed. Exact-head Vercel and Preview Comments passed; no Actions workflow exists. Reviewed canonical matching worktrees, prepared claim/synchronization and recursive submodule evidence. Pure parser correction requires no new database validation. No live request or browser visual claim.

### Architecture Conformance

Canonical name/website/checkout protected marker bytes survive actual immutable snapshot and reconstruction. Unknown semantic names, missing/duplicate/unregistered markers and source/prepared/output digest drift remain refused; legacy marker bytes unchanged. No Shared release, schema, frame authority or accepted-task rewrite. Background003 consumer verification is separately Accepted. Architecture remains In Progress.

### Follow-up

Root owns source merge and parent integration. Retry the existing translation workflow only after deployment through the authorized Admin UI; no direct mutation or forged run status. System validation is dependency-eligible again but remains unprepared until the developer manual checkpoint. Live common activation and genuine ordered delivery proof are outstanding.
