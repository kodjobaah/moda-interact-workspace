---
id: ARCH-075-SHARED-007
architecture_id: ARCH-075
title: Accept one checkout footer per logical delivery group
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-075-SHARED-006
enables:
  - ARCH-075-SHARED-008
created: 2026-11-13
updated: 2026-11-13
---

# Accept one checkout footer per logical delivery group

## Architecture

ARCH-075; docs/architecture/ARCH-075-ordered-recovery-message-layout.md; moda_architect.

## Objective

Add a browser-safe backwards-compatible validation path for an existing multipart logical reply whose checkout footer appears on its final part.

## Context

User explicitly clarified one footer for the whole reply and product photo before the answer. Existing Shared roles/orders already support HEADER,PRODUCT and HEADER,PRODUCT,ANSWER, but trusted-URL parser requires a footer on every part. Existing deployed5.13.10 readers reject the new shape. Definition is Pending under root resource hold until BG012 final checks finish; no implementation preparation yet.

## Scope

Existing recovery-multipart parser/builder and direct compatibility tests only.

## Out of Scope

New roles/fields/schema versions; body/image contract weakening; native Meta templates; publishing; service implementation; source-only URL string-count heuristics; asset composition; new generic telemetry.

## Requirements

- Preserve exact legacy every-part-footer acceptance. Add only the alternative where final part ends exact trusted URL and earlier parts have no appended footer. Existing allowed role orders, max3 parts, body/control/caption/media/tenant checks remain unchanged.
- Do not count occurrences globally or remove/alter authored content. A final answer may already contain the trusted URL verbatim and still append its canonical footer. Host canonical authored boundaries prove one appended footer; Shared validates trusted terminal transport placement, not semantic authorship.
- No arbitrary URL inference, footer relocation, truncation or divider stripping. Missing/wrong final trusted URL fails closed. No empty caption contract needed: long product transport uses existing verified product title before a separate full answer.
- Existing frozen manifests/digests remain unchanged. Browser-safe export stays free of Node/Prisma/service imports. Reuse existing parser/schema, not duplicate validators.
- Explicitly demonstrate old5.13.10 readers reject new shape and new reader accepts old/new. Consumer deployment remains reader-first; this task does not enable any writer.

## Work Items

- [ ] Capture current new-group rejection and preserve legacy compatibility vectors.
- [ ] Implement minimal additive trusted-footer validation.
- [ ] Validate negative/media/Unicode/authored duplicate-URL cases and browser export.
- [ ] Publish exact source/report for review; no npm publication.

## Interfaces / Contracts

Published commerce/presentation RecoveryMultipartDeliveryPlan/parseRecoveryMultipartDeliveryPlan; same schemaVersion1, fields and roles. Background retains canonical composition, receipt, authorization and billing policy.

## Dependencies

ARCH-075-SHARED-006 Complete. Root resource hold keeps this Pending until explicitly promoted; no implementation worktree yet.

## Enables

ARCH-075-SHARED-008 release preparation only after acceptance/integration.

## Acceptance Criteria

- [ ] Exact legacy manifests accepted unchanged; supported final-only footer group accepted.
- [ ] Authored final answer containing checkout URL stays verbatim and valid; no global occurrence count.
- [ ] Invalid last footer, mixed unsupported shapes and existing security/caption/media negatives fail closed.
- [ ] Browser-safe compatibility checks and required repository validation pass, with exact mirrored isolation/report evidence.

## Validation

- [ ] Focused RED/GREEN old/new/negative Unicode and duplicate-authored-URL vectors.
- [ ] Existing declared relevant/full tests, typecheck/build and scoped lint where provided; browser/packed export checks.
- [ ] Diff/privacy review; no source changed outside scope, no new wire fields or version.

## Stop Condition

Set review, publish mirrored branches/report and return architect. Do not publish package, merge or implement consumer.

## Implementation Notes

Normal launcher worktrees; you are not alone, preserve others. Initial definition only; root will release resource hold. No additional framework.

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

Root owns merges and public release approval.

### Unresolved Issues

Consumer rollout and native layout decisions remain separate.

### Architectural Concerns

Return contract gaps before widening.

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

No runtime activation or architectural completion claim.
