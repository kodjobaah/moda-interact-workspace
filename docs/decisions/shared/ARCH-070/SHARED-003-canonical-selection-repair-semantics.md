---
id: ARCH-070-SHARED-003
architecture_id: ARCH-070
title: Align bounded selection repair with canonical semantic validity
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 10
executor: codex
claimed_at: 2026-11-12T13:47:59Z
attempt: 1
depends_on:
  - ARCH-070-SHARED-002
enables: []
created: 2026-11-12
updated: 2026-11-12
---

# Align bounded selection repair with canonical semantic validity

## Architecture

ARCH-070; docs/architecture/ARCH-070-verified-recommendation-terminal-turn-recovery.md; coordinator moda_architect.

## Objective

Align bounded selection repair with canonical semantic validity within existing verified and bounded execution contracts.

## Context

Provider-free reproductions prove schema-valid missing-version/nonempty-list can skip runner repair but host drops the list; truthy null/null shipping without disposition similarly skips repair but host discards it. Fresh production version6 exact raw final shape is unavailable, so historical exact cause is not claimed. Existing accepted null-URL/footer/terminal fixes remain valid.

## Scope

Shared product-selection normalization/semantic validity helper, existing graph-node/invoke repair constraint, public commerce export, directly related tests and approved5.13.4 metadata.

## Out of Scope

Unrelated refactors, provider/model changes, fabricated selections or automatic product choice, new queue retry loop, broader schema/infra/credential/consent changes, live customer sends or resetting processed input.

## Requirements

Own reusable normalized selection parsing once in Shared and use it in runner repair eligibility. Missing recommendation version/list pair, malformed selections or null shipping placeholder without a meaningful disposition must not bypass existing selection repair. Preserve valid paired product IDs and disposition/shipping semantics; preserve bounded existing retry, step/token/tool budgets, cancellation and empty-search behavior. Do not infer version/IDs, auto-select products or create a second repair/queue loop. Preserve Background existing valid-disposition recovery and refusal semantics; export normalization/eligibility helpers so consumer uses identical mechanics. Test provider-free malformed-pair and null-shipping reproductions, corrected model turn with valid fields, bounded exhaustion, valid selections, empty search, ordinary factual answer and publication type/export compatibility.

Compatibility clarification: structural schemas intentionally permit independent optional version/list fields and .extend consumers; do not globally refine that Zod contract. Preserve canonical host semantics for null/null shipping WITH a recognized disposition and partial valid-disposition recovery. In generic runner pinned contracts that do not expose the canonical version/list pair, preserve existing strictly pinned field behavior; never invent unsupported version requirements. Production canonical pair must use normalized semantic validity.

Runtime evidence clarification: static valid STANDARD plus null/null shipping remains a normalized valid selection, but is not by itself sufficient to bypass product selection repair. Qualify shipping bypass and provider forced-schema shipping alternatives with matching successful authorized current-turn shipping observations; product search alone never qualifies. Preserve legitimately observed shipping-only policy answers and exact product/variant matching. Add positive observed-shipping and negative unobserved/mismatched/failed/stale shipping regressions. Keep generic pinned-contract compatibility and existing one-repair/budget limits.

## Work Items

- [ ] Reproduce both semantic gaps deterministically against prior implementation.
- [ ] Implement only owned canonical semantic correction/adoption.
- [ ] Prove compatibility and bounded failure behavior; report exact validation.

## Interfaces / Contracts

Shared owns canonical semantic normalization and repair eligibility; public package @modainteract/moda-interact-shared/commerce. Background consumes published helper and retains tenant/provider/evidence policy. Existing schemas, normal answer contract and budgets remain compatible.

## Dependencies

ARCH-070-SHARED-002. Publication additionally requires developer merge of accepted implementation.

## Enables

Next publication/consumer task in ARCH-070, then developer production verification.

## Acceptance Criteria

- [ ] Requirements hold, including unchanged security and bounded failure behavior.
- [ ] Canonical reusable mechanics are not duplicated across Shared/Background.
- [ ] No private prose, prompts or secret payloads added to diagnostics.
- [ ] Prepared mirrored worktree, start-sync and recursive submodule evidence recorded.

## Validation

- [ ] Focused parser/runner red-green regressions and bounded-budget cases, full Shared suite, types/build and installed immutable package JS+DTS/public exports; record exact candidate hashes.
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
