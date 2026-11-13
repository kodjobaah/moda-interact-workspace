---
id: ARCH-075-ADMIN-004
architecture_id: ARCH-075
title: Make reviewed common layouts selectable from editor workflow
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 5
executor: codex
claimed_at: 2026-11-13T05:56:17Z
attempt: 1
depends_on:
  - ARCH-075-ADMIN-003
  - ARCH-075-SHARED-004
enables:
  - ARCH-075-SYSTEM-TEST-001
created: 2026-11-13
updated: 2026-11-13
---

# Make reviewed common layouts selectable from editor workflow

## Architecture

ARCH-075; docs/architecture/ARCH-075-ordered-recovery-message-layout.md; coordinator moda_architect.

## Objective

Make reviewed common layouts selectable from editor workflow.

## Context

Actual immutable common wrapper has all 20 reviewed projections but definition remains TRANSLATION_QUEUED; selector/eligibility allow only SAVED/PUBLISHED. Separately, editor blank footer becomes one empty text node, while canonical Shared common reference requires a zero-node static footer. Do not rewrite existing saved snapshots or bypass canonical validation.

## Scope

New wrapper draft/editor empty optional-footer AST conversion; wrapper staging selector/eligibility lifecycle parity; actual draft/save/translation/review/selector/activation regressions. Existing compiler output, immutable records and canonical Shared5.13.9 remain unchanged.

## Out of Scope

Live definition edits, translation/provider requests, activation, production replay/reset, source merges, new schemas/packages, broad translation refactors or permission workarounds.

## Requirements

For NEW editable drafts, exactly empty optional static footer becomes [], preserving nonempty and whitespace-only authored bytes. Fix actual editor conversion/default, not old compiler semantics or saved-row normalization. Existing invalid source requires a legitimate new cloned/saved identity and translations/review. Align staging definition statuses with existing Meta source eligibility: SAVED, TRANSLATION_QUEUED, TRANSLATING, PARTIALLY_FAILED, READY_FOR_REVIEW, PUBLISHED. All 20 canonical immutable locale/reviewer/author/hash/protected-token checks remain mandatory; retired/malformed/incomplete sources refuse. Status labels alone never establish readiness. Existing coordinated CAS is the only publication/activation path; final runtime still requires PUBLISHED and active pointer. No DB status workaround, Shared release or Background change. Preserve old snapshots/compiler/hash bytes and provide strict end-to-end actual function/UI draft conversion proof.

## Work Items

- [x] Reproduce both actual editor/lifecycle blockers before correction.
- [x] Correct only new draft empty-footer and reviewed staging eligibility boundaries.
- [x] Prove end-to-end actual owning workflow and strict negative/legacy compatibility; submit report and stop.

## Interfaces / Contracts

Existing Admin authoring AST, immutable compiler/snapshot hashes, wrapper eligibility and coordinated activation. Published Shared5.13.9 common-reference parser unchanged. No new cross-service contract.

## Dependencies

ARCH-075-ADMIN-003; ARCH-075-SHARED-004

## Enables

ARCH-075-SYSTEM-TEST-001

## Acceptance Criteria

- [x] New common wrapper editor workflow yields canonical empty static footer without altering old projections.
- [x] Fully reviewed staged wrapper is selectable and can publish through existing coordinated CAS; incomplete/retired/hash-invalid sources remain refused.
- [x] Actual draft→save→translation/review→selector→activation regression and canonical isolation evidence complete; no live mutation.

## Validation

- [x] Meaningful red/green for blank editor footer and reviewed TRANSLATION_QUEUED definition; actual save/review/selector/coordinator flow with real PostgreSQL where persistence matters.
- [x] Unknown/retired/incomplete/tampered negatives, old saved compiler/hash compatibility and authored whitespace preservation.
- [x] Declared relevant units/types/lint/build/security and exact-head repository check evidence; no live writes.

## Stop Condition

After scope and required checks complete, set review, submit mirrored Completion Report and STOP. No dependent implementation or live action.

## Implementation Notes

You are not alone; preserve other changes. Canonical prepared packet owns startup/claim. Existing accepted tasks must not be rewritten. Root owns merges and live verification.


## Completion Report

### Status

Implementation complete; all local validation passed. Source `d63ba84cca54732c776e9c1be7d5ff4f11c52f34` pushed; draft PR https://github.com/kodjobaah/moda-interact-admin/pull/92. Ready for Review; exact-head Vercel and Preview Comments checks passed. No merge or live mutation performed by this task.

### Files Changed

- `src/lib/admin/whatsapp-templates/authoring/draft-operations.ts`: new wrapper default and editable clone exact-empty footer handling only.
- `src/lib/admin/whatsapp-templates/wrappers/eligibility.ts`: explicit supported staging statuses, preserving all immutable readiness checks.
- `src/lib/admin/whatsapp-templates/authoring/common-layout-repository.ts`: selector repository query uses the same status set and actual strict common-layout reader.
- `src/lib/admin/whatsapp-templates/authoring/common-layout-reads.ts`: existing authenticated SUPER_ADMIN read delegates the tested selector query.
- `tests/unit/arch068-conversation-product-image.test.ts`: historical compatibility fixture now explicitly models the old empty-token footer, retaining the original compiled shape/hash expectations instead of deriving history from new defaults.
- `tests/unit/arch075-reviewed-layout-workflow.test.ts`: red/green producer and staging eligibility, unknown/retired/incomplete/reviewer/hash negatives, whitespace and old compiler preservation.
- `tests/integration/arch075-common-layout.postgres.test.ts`: real draft helpers → immutable old/new clone save → actual translation request → 19 actual locale reviews → actual selector → coordinated empty-cohort activation/replay/audit, with old definition and locale bytes unchanged.

### Work Completed

Both reported blockers were reproduced before correction. New wrappers default to `footer: []`. Cloning an existing wrapper into an editable draft removes the footer only when every node is exactly empty text; whitespace, nonempty text, variables and the original input remain unchanged. `cloneDraft` is called by the actual authoring hook, not immutable saved readers. `parseEditorNodes("")` already returns an empty array and is exercised in the workflow test.

Selector and wrapper eligibility now share the explicit SAVED/TRANSLATION_QUEUED/TRANSLATING/PARTIALLY_FAILED/READY_FOR_REVIEW/PUBLISHED set. This is staging eligibility only: all 20 unique canonical immutable locales, actor/reviewer fields, source and prepared hashes, compiled projection equality and protected bindings remain mandatory. Canonical Shared5.13.9 parser is unchanged. Ordinary activation still refuses common layouts and the coordinator remains the only atomic publication path. Runtime still requires the active PUBLISHED source.

The PostgreSQL provider-boundary fixture supplies completed translated segments without network I/O; all Admin persistence and review functions are real. It proves the actual translation request leaves the definition TRANSLATION_QUEUED, 18 reviewed locales are insufficient, the nineteenth review makes the source selectable, and coordinated activation publishes it without inventing Meta assignments or registrations. Existing old empty-token source remains byte-identical and is not normalized in place.

### Validation Results

- Red: 2/2 new regressions failed on the original empty-token footer and TRANSLATION_QUEUED rejection. Green: 2/2 passed.
- `node scripts/test-arch075-common-layout-postgres.mjs`: 2/2 passed, disposable local pgvector PostgreSQL; container cleaned.
- Initial full unit run: 795/796 passed; one historical product-image fixture coupled to the changed new-draft default was corrected to explicitly retain its historical AST and all old assertions. Final rerun: 796/796 passed, zero skipped (31.1s).
- `npx tsc --noEmit`: passed. `npm run lint`: passed with zero errors and one existing database submodule anonymous-default-export warning.
- `npm run build`: passed; existing BullMQ dynamic-dependency and optional @valkey/valkey-glide warnings retained. `npm test`: 334/334 security/observability tests passed with zero skips (16.0s). `git diff --check`: passed.
- Exact source head contains no `.github/workflows` entries; no GitHub Actions workflow is configured. Vercel and Vercel Preview Comments passed on exact source head at 06:07:14–15 UTC. These are supplementary deployment checks, not a browser visual verification.
- Validation ran sequentially in a scrubbed environment with synthetic authentication secret and localhost-only dummy DB/Redis URLs; real persistence checks provisioned and removed their own disposable local PostgreSQL container. Logs: `/tmp/moda-admin004-{red,green,pg,unit,types,lint,build,security}.log`.

### Deviations

The existing selector loop was moved without semantic relaxation into an injected repository function so disposable PostgreSQL tests exercise the same query used by the authenticated UI read. No new renderer, schema, package or cross-service contract. No compiler changes. No browser visual verification claimed.

A separately authorized bounded production READ ONLY preflight confirmed the user's legitimate new clone has canonical English footer[] and passes the actual Shared common-reference parser; its incomplete 20-language state correctly remained ineligible. No production writes, translation requests, provider calls or activation were performed by this task.

### Assumptions

Translation/provider work in tests is synthetic at the external boundary only. Existing invalid immutable layouts require a new clone followed by translation/review; this task does not repair stored snapshots or preserve review status across changed content.

### Unresolved Issues

None. All required local checks and supplementary exact-head remote checks complete.

### Architectural Concerns

None identified within the bounded implementation. Root retains merges and live UI/deployment/activation ownership.

### Physical Worktree Isolation and Preparation Evidence

- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-075-ADMIN-004`, branch `task/ARCH-075-ADMIN-004`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-075-ADMIN-004`, branch `task/ARCH-075-ADMIN-004`.
- Claim commit: `8d562253b7664e92f0738a544abec50b71ad7c52`, attempt 1, executor codex.
- Parent initial head `55135081db70239c745ba6be93dad72dc8f8dd16`; implementation base `55659a9b6cfca907a88549bb8e818a36e101cef4`.
- Parent/implementation remote fast-forward: not-needed; origin/main incorporation: already-current (launcher evidence).
- Recursive submodule sync/update: passed; `database` initialized at `5329d5390d346042895219663f3a040ea54ae168`.
- Shared workspace/default source checkouts switched or mutated for task: no. Another task worktree reused: no. Startup/claim not repeated.

## Architect Review

### Review Status

Pending

### Review Notes

Pending actual implementation.

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

None
