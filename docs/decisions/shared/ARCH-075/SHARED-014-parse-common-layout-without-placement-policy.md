---
id: ARCH-075-SHARED-014
architecture_id: ARCH-075
title: Parse common layout structure without application placement policy
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 10
executor: codex
claimed_at: 2026-11-14T14:01:20Z
attempt: 1
depends_on: []
enables: []
created: 2026-11-14
updated: 2026-11-14
---

# Parse common layout structure without application placement policy

## Architecture

ARCH-075; docs/architecture/ARCH-075-ordered-recovery-message-layout.md; moda_architect.

## Objective

Parse common layout structure without application placement policy.

## Context

User requests compact one-bubble AI product lists and website in clickable caption footer instead of image header. Published6 reader currently hardcodes website/header and checkout placement business policy; correct ownership once, saved template remains source of truth. No live source/activation changes by agents.

## Scope

Keep envelope/prepared/hash verification and exact mechanical single response slot; remove shop.name/site header placement, empty footer, checkout conditional/last-line business checks from readCommonRecoveryLayoutReference. No new website footer placement rule. Preserve exact hash integrity, reject malformed shape/tamper/duplicate response slots, no operational authority. Audit exported callers. Explicit application policy must guard Admin/BG consumer paths before new writes. Add tests for structurally intact alternative section placements accepted and tampered/unsafe frames rejected. No renderer or unrelated contract refactor.

## Out of Scope

Unrelated refactors, arbitrary user-programmable layouts, new database/infrastructure, main merges/live operations. Preserve all others work.

## Requirements

Keep envelope/prepared/hash verification and exact mechanical single response slot; remove shop.name/site header placement, empty footer, checkout conditional/last-line business checks from readCommonRecoveryLayoutReference. No new website footer placement rule. Preserve exact hash integrity, reject malformed shape/tamper/duplicate response slots, no operational authority. Audit exported callers. Explicit application policy must guard Admin/BG consumer paths before new writes. Add tests for structurally intact alternative section placements accepted and tampered/unsafe frames rejected. No renderer or unrelated contract refactor.

## Work Items

- [x] Implement only defined owning capability.
- [x] Add meaningful affected behavior regressions.
- [x] Record exact source and required checks.

## Interfaces / Contracts

Shared owns technical structure/hash/render safety; applications own trusted bindings/placement/operational authority. Existing Shared6 published source immutable. No duplicated shared codec.

## Dependencies

None

## Enables

None; dependent promotions architect-owned.

## Acceptance Criteria

- [x] Defined capability and owning-policy boundaries satisfied.
- [x] Hash/identity/tenant/receipt/permit and mandatory content integrity retained.
- [x] Required checks and exact immutable reports complete; no live/merge actions.

## Validation

Focused common reader/contracts tests, types/build/scopedlint/browser boundary and exact installed pack proof. Produce exact tested provisional pack for consumer validation. No publication in this implementation task.

## Stop Condition

After required work/checks publish matching source and parent report, set review and STOP. Do not continue dependent work.

## Implementation Notes

Normal moda-task canonical sibling isolation/claim required. You are not alone; do not revert others. Pending consumer tasks may perform preparatory source work only after explicit architect Ready amendment; final acceptance requires accepted published dependency. No unpublished sibling imports or fabricated registry lock.

## Completion Report

### Status

Ready for Review. Source, required declared checks and exact installed-package proof are complete; no publication, version change, consumer edits, main merge or live action.

### Files Changed

Source `a870977566babb35aac7b38e59efd194b64770b3`, PR https://github.com/kodjobaah/moda-interact-shared/pull/91.

- `src/commerce/presentation/common-recovery-layout.ts`: remove common-specific name/site/header/footer/checkout placement policy, preserving envelope/prepared/hash and mechanical frame validation.
- `src/commerce/presentation/common-recovery-layout.test.ts`: accepted alternate section/variable/formatting snapshots and host-policy distinction; retained/expanded malformed/token/hash/slot/resource rejection.
- `scripts/validate-recovery-multipart.mjs`: exact installed Node/types/browser proof follows structural parser semantics and tests alternate website conditional, hash tamper and duplicate slot.
- `README.md`: documents structural snapshot versus host-owned placement/mandatory content/authority.
- Parent task-owned `SHARED-014-tested-package.json`: exact tested candidate receipt. No runtime consumers were edited.

### Work Completed

- Exported `readCommonRecoveryLayoutReference(raw, sha256)` signature, `CommonRecoveryLayoutReference` type and export path are unchanged. Reader still verifies exact bounded envelope, supported language/version/digest shapes, compiled prepared structure, canonical `sha256(stableJson(prepared))`, optional profile pair/safety/digest through existing prepared reader, separate-media frame and exact single body response slot.
- Removed requiring shop.name/site exactly once in header, common-specific variable section allowlists, empty static footer, exactly one conditional, checkout uniqueness, URL-last/token-last and newline-before-URL formatting. No new website-footer or replacement placement rule was introduced. A valid supplied snapshot can therefore omit or duplicate application-required content; parsing is explicitly not sending/selected-source authority. Admin011/BG016 own semantic variable allowlists, mandatory identities/content and canonical checkout policy before activation/new writes.
- Root/coordinator explicitly narrowed scope after the delegated generic checkout predicate was identified: `readPreparedWrapper` and generic checkout.url-only-conditional context grammar remain unchanged; common exact body slot and separate transport-media prohibition remain mechanical frame constraints. Website can use the existing checkout.available conditional before checkout URL. All renderers, fixed layout geometry, token substitution, hash algorithm, receipt/tenant/permit/source selection and runtime identities remain untouched.
- Regression vectors accept header-independent website/name, website in caption conditional, static website footer, duplicate name/checkout formatting, no checkout conditional and authored text after checkout when structurally valid. Existing rendering proves exact saved shop + complete answer + clickable website caption + checkout caption bytes without a second frame. Snapshot parsing does not infer selected definition, audience, active status or tenant authority.
- Exact negative vectors retain unsupported token/condition rejection, raw token-marker rejection, token/resource bounds, malformed envelope/missing keys/hash mismatch, duplicate/missing/moved response slot and product binding refusal. No digest normalization or trust weakening was added.
- Read-only exported caller audit: Admin `src/lib/admin/whatsapp-templates/authoring/common-layout.ts`; Background `src/services/recovery-template-preparation/recovery-template-common.ts`, `src/services/recovery-multipart/composition.ts`, `src/services/recovery-multipart/common-layout.ts`. Same API compiles; semantic acceptance is deliberately broader, so explicit application policy remains a cross-repository prerequisite for new writes. Consumer owners received the exact provisional pack; no sibling source import or fabricated registry lock is authorized.

### Validation Results

- Isolated `npm ci --ignore-scripts --no-audit --no-fund`: PASS (242 packages), no dependency/lock changes.
- Focused common reader/presentation/composite-profile contract tests: PASS27/27, no skips/failures.
- `npm run typecheck`: PASS. `npm run build`: ESM/DTS PASS. `git diff --check`: PASS.
- Scoped lint capability gap: repository declares no lint script. Reported to architect; no invented validation contract/tooling or unrelated lint configuration added.
- `npm pack --ignore-scripts`: PASS after successful build; exact tested candidate `/tmp/ARCH-075-SHARED-014/shared014-provisional-6618d7c97e99.tgz` is a read-only immutable copy, metadata version6.0.0 unchanged for unpublished consumer tests. Size965126 bytes, unpacked3327095 bytes,161 members. No private actual QA assets/backups/logo/product/header files.
- Candidate SHA256 `6618d7c97e99c1e75ab67240ba940a5a5eade2a37a5661de000f25c5ade3a97a`; npm SHA1 `c5c12158cb71efe5893c1f9aa6513261e584fb80`; integrity `sha512-ac9XAKvQa3pm21n7juEOg9KKIoWSmggb82v2qbKQeHlq6SqEgFe2977gLYCDVwhXRSdR5JIPN7ZMrIPc9843/g==`. Manifest SHA256 `f8545e4d1f8d6398ec830ab8a7635886a6e7a25c2284e504a7d76be94725fbe8` (local manifest under `/tmp/ARCH-075-SHARED-014/`). Durable exact identity/check receipt beside this task.
- `node scripts/validate-recovery-multipart.mjs <exact archive>`: PASS installed Node ESM, installed TypeScript API/contract checks, actual browser bundle/VM with no Node/Sharp/AWS/Prisma/logging/observability/LLM imports; alternate website placement accepted, malformed unsupported token/hash/duplicate-slot rejection retained and established multipart behavior intact.
- Launcher isolation: canonical primary `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent `moda-interact-workspace-task-ARCH-075-SHARED-014` reused, implementation `moda-interact-workspace.worktrees/ARCH-075-SHARED-014` created, both mirrored `task/ARCH-075-SHARED-014`. Parent initial `d66b0615284e69ad357814a763d6309f92314344`; implementation initial `ade292b55e85fbdc38b0810459a7e126493dd620`. Remote task fast-forward not-needed, origin/main already-current both; recursive sync/update passed/statusready/no submodule entries. Durable claim `3c1f93fcf468fdfe7c578ca7f9715fe129eb6129`, attempt1/codex at2026-11-14T14:01:20Z. No primary/shared worktree, another task, main or gitlink writes.

### Deviations

No implementation deviation. Root/coordinator explicitly retained existing generic checkout-context semantics and common single-slot/separate-media frame. Scoped lint unavailable as declared above. Full renderer/native/Alpine tests were not rerun: no renderer changed, and task validation is focused common contracts/type/build/browser/installed package.

### Assumptions

Admin011/BG016 enforce host-owned content/placement/current-reference authority before new writes. Root/architect own source merge, separate Shared015 metadata/publication gate and all deployment/live actions. Root’s planned6.0.1 archive is a later release-only task; this implementation does not change version or publish.

### Unresolved Issues

No source/API/check failure. Declared scoped lint is unavailable; architect receives this explicit validation capability gap. Consumer final service acceptance and separate publication remain independently owned.

### Architectural Concerns

A successful parse proves structural/hash/mechanical snapshot integrity only. Broadening common parser acceptance intentionally removes application policy; callers must not treat `kind:ok` as audience/activation/tenant/content/checkout authority. Existing public6.0.0 stays immutable; exact6.0.1 release requires separate tested archive approval.

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

None
