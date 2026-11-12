---
id: ARCH-070-BACKGROUND-001
architecture_id: ARCH-070
title: Verify refreshed recommendation product evidence
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
attempt: 1
depends_on:
  - ARCH-070-SHARED-002
enables: []
created: 2026-11-12
updated: 2026-11-12
---

# Verify refreshed recommendation product evidence

## Architecture

ARCH-070; docs/architecture/ARCH-070-verified-recommendation-terminal-turn-recovery.md; coordinator moda_architect.

## Objective

Verify refreshed recommendation product evidence without relaxing existing production security or lifecycle guarantees.

## Context

Recommendation candidates were refreshed but all three were rejected as PRODUCT_REFRESH_NOT_VERIFIED, ending MISSING_VERIFIED_PRODUCT_SELECTION / INVALID_FINAL. Establish the exact provider response evidence shape before fixing its consumption.

## Scope

src/commerce/host.ts recommendation refresh and product/domain evidence composition; directly related host tests.

## Out of Scope

Other task's owned modules, Shared/MCP implementation, schema changes, provider/model switching, credentials, infrastructure, old-message replay, unrelated refactors and unsolicited customer sends.

## Requirements

A legitimate refreshed product from the connected store is accepted and produces a verified recommendation; mismatched shop/domain/product/variant, missing or malformed evidence stays rejected. Preserve current price, stock and product identity validation. Do not weaken tenant/domain verification or invent a provider contract. If the valid fix requires MCP/Shared changes, stop and return that dependency to the architect.

## Work Items

- [ ] Establish exact source/fixture cause and preserve a failing regression.
- [ ] Implement only the owned correction.
- [ ] Validate positive and failure/recovery behavior and report evidence.

## Interfaces / Contracts

Consume published Shared contracts and existing MCP product evidence / durable conversation lifecycle. No new wire or schema contract is authorized. Cross-repository gaps return to architect.

## Dependencies

ARCH-070-SHARED-002. Retry-policy task BACKGROUND-002 remains independently executable; recommendation adoption waits for the accepted published nullable PRODUCT_ONLY URL contract.

## Enables

Developer integration and production verification after architect acceptance of both tasks.

## Acceptance Criteria

- [ ] Requirements demonstrated with deterministic positive and negative regression tests.
- [ ] Existing tenant, domain, message identity and lifecycle guarantees preserved.
- [ ] No duplicate delivery, live test send, secret logging or unrelated changes.
- [ ] Completion Report records canonical launcher packet, physical isolation, synchronization and recursive submodule evidence.

## Validation

- [ ] Regression reproducing legitimate provider-shaped refresh and negative cross-store/malformed/stale evidence; existing host/composition tests, typecheck, lint and required repository CI. No Meta send in tests.
- [ ] Diff hygiene and exact changed-file scope review.

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

Existing runtime evidence needs corroboration in source and fixtures.

### Unresolved Issues

None known beyond investigation.

### Architectural Concerns

Return contract or schema gaps before implementing outside scope.

## Architect Review

### Review Status

Pending

### Review Notes

Architectural dependency resolved: Shared001 and Shared002 architect-accepted Complete; exact5.13.3 canonical public artifact downloaded and hash verified. Task Ready; preserve attempt1 and next prepared claim increments once. Pin published5.13.3 and accept null URL only PRODUCT_ONLY; mutation URL requirements and all nonnull URL/domain checks remain strict.

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

None
