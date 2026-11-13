---
id: ARCH-075-SHARED-005
architecture_id: ARCH-075
title: Allow one complete branded main recovery reply
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 5
executor: codex
claimed_at: 2026-11-13T19:58:00Z
attempt: 1
depends_on:
  - ARCH-075-SHARED-004
enables:
  - ARCH-075-SHARED-006
created: 2026-11-13
updated: 2026-11-13
---

# Allow one complete branded main recovery reply

## Architecture

ARCH075; docs/architecture/ARCH-075-ordered-recovery-message-layout.md; coordinator moda_architect.

## Objective

Add the single HEADER order to the existing recovery multipart contract so a complete short branded reply can be delivered in one physical message.

## Context

Actual common AI delivery sends logo/header/footer with no answer, then answer/footer, creating adjacent dividers and duplicate framing. Shared schema currently rejects HEADER-only even though existing HEADER accepts trusted BRAND_IMAGE or TEXT and existing media validation bounds captions. Background cannot emit one logo-bearing complete answer without this additive allowed order. Product images must stay separate; every physical part retains checkout footer.

## Scope

Existing recovery-multipart.ts allowed order plus inseparable tests/docs. One additive HEADER-only order; no new fields/schemaVersion/roles/codecs.

## Out of Scope

Background composition/adoption; version/publication (separate SHARED006); Admin/common source changes; provider/live operations; relaxed image, URL, role, tenant, footer or hash limits.

## Requirements

- Add only HEADER to allowedOrders. Existing HEADER role plan restrictions (TEXT or verified LOGO/SQUARE_LOGO BRAND_IMAGE), caption/body limits and trusted final checkout URL remain unchanged. Do not permit PRODUCT-only, reordered/duplicate parts or arbitrary role/media combinations.
- Existing valid ANSWER, HEADER+ANSWER, HEADER+PRODUCT and HEADER+PRODUCT+ANSWER bytes/digests remain accepted unchanged. A new single HEADER must obey the same trusted footer, provenance and bounded media validation as HEADER in existing plans.
- Browser-safe published entrypoint unchanged. No Node-only import/new validator implementation. No producer use before accepted publication and consumer rollout.
- This is production-compatible additive parsing, but old readers reject HEADER-only. Root must drain/quiesce old workers before new consumer emits this order; frozen old plans remain readable by new consumer. Document limitation, no false universal old-reader compatibility.

## Work Items

- [x] Capture failing single branded HEADER regression.
- [x] Add minimal allowed order preserving all old invariants.
- [x] Run focused/full relevant checks and prepare exact source/report for review; no release.

## Interfaces / Contracts

@modainteract/moda-interact-shared/commerce/presentation RecoveryMultipartDeliveryPlanSchema/parse/build/digest, existing v1 fields and roles unchanged.

## Dependencies

ARCH-075-SHARED-004 Complete.

## Enables

ARCH-075-SHARED-006 publication after independent acceptance.

## Acceptance Criteria

- [x] Single valid branded HEADER and TEXT HEADER pass unchanged footer/provenance limits.
- [x] Old valid order/digest vectors remain exact; invalid roles/orders/media/URLs/size/tenant cases still reject.
- [x] Required checks and normal prepared worktree evidence recorded; no runtime adoption/release.

## Validation

- [x] Focused RED/GREEN contract vectors, caption1024 boundary/Unicode/trusted footer and old digest/order compatibility negatives.
- [x] Declared relevant full tests/lint/type/build and package-browser export checks; inspect actual package scripts.
- [x] Diff/privacy and exact source publication, normal launcher isolation/synchronization evidence.

## Stop Condition

Publish implementation and mirrored report, set review, return and stop. Do not version/publish, merge or implement consumer.

## Implementation Notes

Normal dedicated launcher worktrees; you are not alone, preserve current main and other edits. Return actual dependency gaps before widening. Root owns merges/rollout.

## Completion Report

### Status

Ready for Review; independent architect review required.

### Files Changed

- `src/commerce/presentation/recovery-multipart.ts`: add only `HEADER` to existing allowed orders.
- `src/commerce/presentation/recovery-multipart.test.ts`: single LOGO/SQUARE_LOGO/TEXT HEADER, Unicode caption 1024/+1, trusted footer/media negatives and all old order byte/digest-input compatibility vectors; remove HEADER from invalid-order fixtures.
- `scripts/validate-recovery-multipart.mjs`: installed ESM and browser HEADER-only smoke checks using the existing published entrypoint.
- `README.md`: document single complete header, separate product media and old-reader rollout limitation.

### Work Completed

The existing multipart v1 accepts one complete HEADER without changing fields, role schemas, codecs, digest serialization, provenance/media validation or trusted footer checks. Existing ANSWER and multi-part orders remain unchanged. Known consumers are Background recovery composition/replay; Admin common-source production remains unchanged. Publication (SHARED006) and Background adoption are separate tasks. No version bump, registry publication, runtime consumer or provider operation performed.

### Validation Results

- RED: 12 focused tests, 10 pass and exactly 2 new HEADER-only regressions fail with `RECOVERY_PART_ORDER_INVALID` before the source change.
- GREEN: all 12 focused tests pass after the one-line allowed-order addition.
- `npm run typecheck`: passed.
- `npm test`: 790 tests, 787 passed, 0 failed, 3 declared skips.
- `npm run build`: ESM and DTS passed.
- Local `npm pack --ignore-scripts --pack-destination /tmp`, then `npm run validate:recovery-multipart -- /tmp/modainteract-moda-interact-shared-5.13.9.tgz`: passed installed ESM, installed TypeScript declarations and isolated browser bundle checks, including HEADER-only through the existing entrypoint. Local artifact SHA-256 `35fb4130c1bc8a20f4580bf70f82e1f25d7e61a05eff5d1bc84f85aaefccb20f`; version remains 5.13.9, unpublished candidate only.
- `git diff --check` and source/privacy review: passed; synthetic-only fixtures, no secrets or provider mutations.
- No lint script or lint configuration is declared by this repository; no substitute contract introduced.

### Deviations

None.

### Assumptions

Root controls release and rollout authorization. Old readers reject the newly allowed order; deploy compatible readers and drain/quiesce old workers before producers emit HEADER-only. New readers preserve existing frozen plans.

### Unresolved Issues

Publication, consumer adoption and live delivery proof remain separate.

### Architectural Concerns

No new contract or scope dependency. This is additive for new readers, not universally compatible with old readers.

### Git / VCS

Task branch: `task/ARCH-075-SHARED-005` in both repositories.

Physical worktree isolation (launcher evidence):
- Canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-075-SHARED-005`; branch `task/ARCH-075-SHARED-005`, reused.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-075-SHARED-005`; branch `task/ARCH-075-SHARED-005`, created.
- Shared workspace checkout switched/mutated for task work: no.
- Shared implementation checkout switched/mutated for task work: no.
- Another task worktree reused: no.

Start-of-attempt synchronization (launcher evidence): parent and implementation remote task fast-forward `not-needed`; both `origin/main` incorporated `already-current`. Parent initial head `fb82e912dcc3e5a934da17020a21e887318de678`; implementation initial head `1ca3c5ca4df6620ba3118bb5c5051c4773784e80`. Dependency gate passed (SHARED004 complete).

Recursive implementation submodules: sync/update-init recursive passed; recorded entries none; status ready.

Durable parent claim `1a7f9b949171dd686890e30dad8d6406d42b757a` pushed. Implementation repository `moda-interact-shared` source commit `8276eadb1f2467367e7b1ecb4a1d4e3573048fb6` pushed to `origin/task/ARCH-075-SHARED-005`. Parent report is submitted by the containing commit on the same mirrored branch (exact hash available from Git; no self-referential hash claim). Parent submodule gitlink staged: no. Neither branch merged into main.

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

Pending

### Follow-up

No implicit publication or architecture completion.
