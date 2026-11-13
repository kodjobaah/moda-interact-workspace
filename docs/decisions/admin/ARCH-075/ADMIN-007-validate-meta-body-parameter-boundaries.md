---
id: ARCH-075-ADMIN-007
architecture_id: ARCH-075
title: Compile provider-valid common Meta body boundaries
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 5
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-075-ADMIN-001
  - ARCH-075-ADMIN-005
enables: []
created: 2026-11-13
updated: 2026-11-13
---

# Compile provider-valid common Meta body boundaries

## Architecture

ARCH-075; `docs/architecture/ARCH-075-ordered-recovery-message-layout.md`; coordinator moda_architect.

## Objective

Reject Meta-invalid leading/trailing BODY parameters while compiling the existing common shop frame and reviewed localized opt-out into provider-valid replacement templates.

## Context

Root read-only production evidence:120 reviewed registrations failed template_create HTTP400/code100/subcode2388299, no approvals/provider IDs. Root verified the official Meta error-code page (`https://developers.facebook.com/documentation/business-messaging/whatsapp/support/error-codes`) states2388299 forbids leading/trailing parameters. Saved private official row receipt is `official-meta-2388299-rule.txt`. Actual commonMetaBody currently concatenates header, scenario body plus static draft.footer, then common checkout conditional. The current common header begins shop.name and conditional must end checkout.url, producing exactly the forbidden provider BODY boundaries. Shared intentionally preserves the final checkout URL contract for ordered AI/human rendering; no Shared release is required for this provider projection correction.

## Scope

Admin-owned pure authoring validation/compiler/common-layout projection, directly related compilation/read/preview/confirmation safety and regression tests. Reuse reviewed localized source text, existing compiler/hash/binding mechanisms and current published Shared contract. Inspect impacted frozen-source verification callsites before changes.

## Out of Scope

Shared/BG/Database/runtime edits or releases; rewriting existing immutable sources/locales/submissions/registrations; live clone/review/submit/retry/activation; blanket120 retries; credentials/providers/branding image selection; Meta product-image headers; new framework or sender-pool work.

## Requirements

- For NEW common-layout Meta compilation, project common header -> scenario body -> common checkout conditional -> existing reviewed static draft.footer opt-out. No untranslated injected English, bare punctuation, invisible padding, inferred URL content, dropped opt-out or duplicated checkout binding. The dynamic checkout link remains the footer link; the localized opt-out is its final provider-safe text tail. Product images remain separate; logo header media role remains shop brand only.
- A new immutable common header may be authored by root with meaningful reviewed localized fixed prefix before shop.name (for example localized Shop:/Website: labels). Do not silently mutate that common source, generate translations or patch the saved hash in this task. Invalid old common headers must be reported with actionable field validation, not prefixed ad hoc at transport time.
- Validate the FINAL projected Meta BODY, including common frame, and ordinary noncommon Meta BODY: after ignoring whitespace, it must not begin/end with a parameter. Require meaningful fixed boundary text; whitespace, punctuation-only or formatting tricks must not satisfy the rule. Do not reject a variable safely surrounded by real text. Keep translated Unicode letters valid. Avoid inventing an unsupported universal variable-ratio rule.
- Reuse one pure final projection/validation path without compiler-validation recursion. Authoring preview, reviewed confirmation and actual submitted prepared components must agree, with same order, examples, sequential binding positions and content hash. Enforce existing1024characters/10parameters on final BODY; fail without truncation or content removal.
- Preserve AST schemaVersion1 and existing binding names. Existing frozen legacy noncommon and submitted common snapshots remain immutable; no recompile-and-rewrite migration. Inspect compilation/reads.ts, translations/source-snapshot.ts and meta/snapshot.ts: new compilation may produce a fresh hash, but old submissions must not silently acquire new content. New sources/locales must be cloned/reviewed/submitted under new immutable identity/hash. If preserving existing read/clone paths needs a contract/version change beyond Admin scope, return concrete evidence before expanding.
- All20 supported locales and all six scenario variants must be exercised with actual reviewed localized static opt-out fixtures and a provider-safe new common header. Preserve trusted common reference/website/name/checkout, media role, example and immutable hash checks. Legacy no-common valid output should remain unchanged.
- Root owns operational canary-first rollout: after source acceptance/deployment, clone/review one corrected English source and common header; inspect exact projected BODY, then submit one canary. Only successful provider response/real approval permits expansion; preserve failed120 history, do not reset it. Activation and actual Eugene Meta/AI/human ordered logo/details/product/footer proof remain later operational gates.

## Work Items

- [ ] Inspect final projection and immutable read/preview/submission paths; capture current boundary failure regression.
- [ ] Implement bounded projection reorder and actionable final BODY validation without changing Shared or saved records.
- [ ] Prove all20 locales/six scenarios plus frozen legacy/preview/hash/binding regressions.
- [ ] Run required validation and publish exact matching source/report for independent review.

## Interfaces / Contracts

Existing published `@modainteract/moda-interact-shared/commerce/presentation` common layout reference/finalURL contract unchanged. Admin owns provider projection and prepared content hashing; Background consumes frozen prepared components/bindings. No contract/version release is authorized.

## Dependencies

ARCH-075-ADMIN-001 and ARCH-075-ADMIN-005 are architect-accepted Complete.

## Enables

Root-owned corrected immutable source review, canary registration and later verified operational activation; no implicit task execution.

## Acceptance Criteria

- [ ] Current leading/trailing common BODY failure captured before fix; corrected new projection has fixed localized boundaries, one checkout binding and preserved opt-out.
- [ ] Common and ordinary invalid boundary input fails before submission; valid Unicode/static-boundary input passes.
- [ ] Preview/confirmation/actual components, examples/bindings/hashes match; final size bounds and immutable legacy behavior are preserved.
- [ ] Required checks pass; no live/source-contract scope mutation, complete preparation/report evidence recorded.

## Validation

- [ ] Focused compiler/common/noncommon boundary tests including current failure RED/GREEN; whitespace/punctuation/empty-tail/Unicode/parameter-order/size negatives.
- [ ] All20 supported locale ×six scenario projections and exact preview/prepared consistency; immutable source/hash/submission/legacy compatibility regressions.
- [ ] Declared Admin full unit/security checks, typecheck/lint/production build; run build-dependent tests after build where necessary. Inspect actual package scripts, no repeated green heavy checks without change.
- [ ] Exact source diff/privacy and parent/implementation isolation/synchronization evidence. Remote exact-head checks before root merge.

## Stop Condition

After scoped validation and exact mirrored source/report publication, set review and return to moda_architect. No self-acceptance, merge, deployment, live submissions or follow-on work.

## Implementation Notes

Use normal launcher-prepared dedicated matching parent/implementation worktrees and durable claim. You are not alone: preserve all newer main behavior and primary originals. Return a concrete ownership/contract gap before expanding. Root owns merges and all live provider operations. Do not claim provider acceptance from local compiler checks.

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

Not run

### Deviations

None

### Assumptions

Root's official provider-rule evidence and read-only production status are authoritative; new immutable header/source review remains root-owned.

### Unresolved Issues

Provider approvals, activation and real delivery proof are not established by this task.

### Architectural Concerns

Return any frozen-read/version incompatibility before widening scope.

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

ARCH075 remains In Progress until required operational/provider and integrated acceptance proof.
