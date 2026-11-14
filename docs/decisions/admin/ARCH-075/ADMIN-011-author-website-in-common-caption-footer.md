---
id: ARCH-075-ADMIN-011
architecture_id: ARCH-075
title: Author website in saved common caption footer
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 10
executor: codex
claimed_at: 2026-11-14T14:06:20Z
attempt: 1
depends_on: []
enables: []
created: 2026-11-14
updated: 2026-11-14
---

# Author website in saved common caption footer

## Architecture

ARCH-075; docs/architecture/ARCH-075-ordered-recovery-message-layout.md; moda_architect.

## Objective

Author website in saved common caption footer.

## Context

User requests compact one-bubble AI product lists and website in clickable caption footer instead of image header. Published6 reader currently hardcodes website/header and checkout placement business policy; correct ownership once, saved template remains source of truth. No live source/activation changes by agents.

## Scope

Move common-frame business validation into Admin owning app; Shared only structural parser/hash machinery. Require trusted shop.name/site and checkout identity counts and allowed variables; support saved header Shop/name/divider and checkout.available conditional containing website followed by canonical checkout URL last. Retain static footer empty if smallest existing app contract; do not add unsupported variables. Audit every requireCommonLayout/readSaved/eligibility/clone/translation/frozen-review/Meta projection/common activation path. Exact source/prepared/locale/profile hashes and locale equality preserved, no silent old source rewriting. Existing native projection can consume conditional website tokens; test provider preview matches submitted body. App admission remains failclosed for untrusted/duplicate/missing bindings. Preserve reviewed immutable audit reads. No live template edits, registrations or activation.

## Out of Scope

Unrelated refactors, arbitrary user-programmable layouts, new database/infrastructure, main merges/live operations. Preserve all others work.

## Requirements

Move common-frame business validation into Admin owning app; Shared only structural parser/hash machinery. Require trusted shop.name/site and checkout identity counts and allowed variables; support saved header Shop/name/divider and checkout.available conditional containing website followed by canonical checkout URL last. Retain static footer empty if smallest existing app contract; do not add unsupported variables. Audit every requireCommonLayout/readSaved/eligibility/clone/translation/frozen-review/Meta projection/common activation path. Exact source/prepared/locale/profile hashes and locale equality preserved, no silent old source rewriting. Existing native projection can consume conditional website tokens; test provider preview matches submitted body. App admission remains failclosed for untrusted/duplicate/missing bindings. Preserve reviewed immutable audit reads. No live template edits, registrations or activation.

## Work Items

- [ ] Implement only defined owning capability.
- [ ] Add meaningful affected behavior regressions.
- [ ] Record exact source and required checks.

## Interfaces / Contracts

Shared owns technical structure/hash/render safety; applications own trusted bindings/placement/operational authority. Existing Shared6 published source immutable. No duplicated shared codec.

## Dependencies

ARCH-075-SHARED-015

## Enables

None; dependent promotions architect-owned.

## Acceptance Criteria

- [ ] Defined capability and owning-policy boundaries satisfied.
- [ ] Hash/identity/tenant/receipt/permit and mandatory content integrity retained.
- [ ] Required checks and exact immutable reports complete; no live/merge actions.

## Validation

Focused authoring/preview/translation/common activation tests, persisted meaningful common workflow if changed, types/scopedlint/build/browser graph/exact remote check. Local exact accepted Shared pack consumer tests may run before publication; final registry lock/npmci/remote gates required after actual publication.

## Stop Condition

After required work/checks publish matching source and parent report, set review and STOP. Do not continue dependent work.

## Implementation Notes

Normal moda-task canonical sibling isolation/claim required. You are not alone; do not revert others. Pending consumer tasks may perform preparatory source work only after explicit architect Ready amendment; final acceptance requires accepted published dependency. No unpublished sibling imports or fabricated registry lock.

## Preparatory execution and final release gate

Root authorizes concurrent owning source preparation using unchanged public reader signature. No unpublished sibling imports or fabricated registry lock. Shared014 must be accepted and its exact tested pack used for affected consumer validation before requesting publication approval. Final review/acceptance requires actual approved Shared015 publication, real registry dependency/lock/npmci and exact remote checks. Task Ready permits source preparation, not readiness/deployment claims. Desired saved frame puts website inside existing checkout.available conditional before canonical checkout URL; staticfooter empty can stay app policy. No generic checkout contextual-rule widening needed.

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

Pending

### Deviations

None

### Assumptions

None

### Unresolved Issues

None

### Architectural Concerns

None

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
