---
id: ARCH-070-BACKGROUND-004
architecture_id: ARCH-070
title: Adopt canonical selection semantics and bounded shape diagnostics
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 10
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-070-SHARED-004
enables: []
created: 2026-11-12
updated: 2026-11-12
---

# Adopt canonical selection semantics and bounded shape diagnostics

## Architecture

ARCH-070; docs/architecture/ARCH-070-verified-recommendation-terminal-turn-recovery.md; coordinator moda_architect.

## Objective

Adopt canonical selection semantics and bounded shape diagnostics within existing verified and bounded execution contracts.

## Context

Provider-free reproductions prove schema-valid missing-version/nonempty-list can skip runner repair but host drops the list; truthy null/null shipping without disposition similarly skips repair but host discards it. Fresh production version6 exact raw final shape is unavailable, so historical exact cause is not claimed. Existing accepted null-URL/footer/terminal fixes remain valid.

## Scope

Exact published5.13.4 dependency/lock and existing recommendations/disposition.ts normalization consumer, host shape-only diagnostic and directly related host/selection tests.

## Out of Scope

Unrelated refactors, provider/model changes, fabricated selections or automatic product choice, new queue retry loop, broader schema/infra/credential/consent changes, live customer sends or resetting processed input.

## Requirements

Replace duplicate local semantic parser mechanics with published Shared helper, preserving host domain policy and exact normalized behavior. Add bounded shape-only diagnostics needed to distinguish pair presence/count/type/disposition/shipping eligibility, never reply prose/private prompts, tokens/credentials or full payload. Use existing shared structured logger, no generic logger or duplicate framework telemetry. Keep host fail-closed verified selection/evidence checks; no inferred version/IDs, product auto-selection, new retries, schema or credentials. Exercise malformed pair and null-shipping prior bypass through actual published bounded runner repair, valid corrected selection and refusal on exhaustion. Preserve all accepted nullURL/footer/terminal fixes on final current main.

Runtime evidence clarification: missing-product-selection guard must test actual verified shipping presentation/evidence, not a truthy model shippingInformationSelection object. Valid static STANDARD plus null/null selection alone cannot authorize unsupported prose after product searches. Preserve genuinely verified shipping-only answers and strict domain/identity checks. Test unobserved, failed/mismatched shipping versus positive authorized observation; no additional retry loop.

Shipping evidence precision: selectShippingPresentation may return a truthy limitation for provider/identity mismatch, so object presence alone is insufficient. Use the published canonical shipping-result/selection qualifier on fresh output with known expected platform before allowing shipping evidence to satisfy the missing-product-selection guard. Preserve matched null/null policy-unavailable truthful limitations and no-product-observation shipping-only flow. Reject provider/product/variant mismatch and malformed/unrelated result. Share qualifier mechanics; do not duplicate local parsing or add calls/loops.

## Work Items

- [ ] Reproduce both semantic gaps deterministically against prior implementation.
- [ ] Implement only owned canonical semantic correction/adoption.
- [ ] Prove compatibility and bounded failure behavior; report exact validation.

## Interfaces / Contracts

Shared owns canonical semantic normalization and repair eligibility; public package @modainteract/moda-interact-shared/commerce. Background consumes published helper and retains tenant/provider/evidence policy. Existing schemas, normal answer contract and budgets remain compatible.

## Dependencies

ARCH-070-SHARED-004. Publication additionally requires developer merge of accepted implementation.

## Enables

Next publication/consumer task in ARCH-070, then developer production verification.

## Acceptance Criteria

- [ ] Requirements hold, including unchanged security and bounded failure behavior.
- [ ] Canonical reusable mechanics are not duplicated across Shared/Background.
- [ ] No private prose, prompts or secret payloads added to diagnostics.
- [ ] Prepared mirrored worktree, start-sync and recursive submodule evidence recorded.

## Validation

- [ ] Clean public exact artifact install/hash, semantic compatibility vectors and actual local host/runner tests, no provider/Meta sends, changed-file lint/types and final combined full CI. Existing untouched main lint baseline remains documented; no unrelated cleanup.
- [ ] Exact changed-file scope and diff/secret hygiene.

## Stop Condition

Complete owned work and required validation, set review, return report and STOP. Do not merge, deploy or begin another task.

## Implementation Notes

You are not alone in the codebase. Preserve others' changes. Use the prepared dedicated mirrored worktrees and task branch. Verify actual package scripts before running checks. Existing structured semantic logs suffice; do not introduce competing logging or repeated provider work as a diagnostic mechanism.

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

Historical exact raw final shape remains unconfirmed; deterministic contract gaps are reproduced.

### Unresolved Issues

None beyond owned correction.

### Architectural Concerns

Return cross-owner gaps before modifying outside scope.

## Architect Review

### Review Status

Pending

### Review Notes

Pending actual implementation review.

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

None
