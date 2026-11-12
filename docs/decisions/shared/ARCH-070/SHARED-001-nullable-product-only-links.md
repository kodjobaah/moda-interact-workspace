---
id: ARCH-070-SHARED-001
architecture_id: ARCH-070
title: Support absent storefront links for verified product-only recommendations
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
claimed_at: 2026-11-12T12:46:04Z
attempt: 1
depends_on: []
enables: []
created: 2026-11-12
updated: 2026-11-12
---

# Support absent storefront links for verified product-only recommendations

## Architecture

ARCH-070; docs/architecture/ARCH-070-verified-recommendation-terminal-turn-recovery.md; coordinator moda_architect.

## Objective

Support absent storefront links for verified product-only recommendations without relaxing existing production security or lifecycle guarantees.

## Context

MCP valid catalogue products can have onlineStoreUrl null, but existing Shared recommendation schema/render requires a link. Background must consume a canonical safe contract rather than weaken verification.

## Scope

Shared recommendation presentation schema/render and directly related tests/types; approved5.13.3 package metadata. Publication task scope is only accepted-artifact release mechanics.

## Out of Scope

Background/MCP implementation, basket mutation URL relaxation, fabricated URLs, credentials, unrelated refactors and live customer sends.

## Requirements

Allow null recommendation product URL only in PRODUCT_ONLY scope while retaining verified product identity, price, stock and image fields. Renderer omits the product link when null; never fabricate a URL. Mutation/actionable recommendation scopes still require URL. Nonnull URLs retain HTTPS, no credentials, no unsafe ports, domain and existing security validation. Apply approved patch version5.13.3. Inspect existing exports before adding any reusable runtime helper.

## Work Items

- [ ] Establish exact source/fixture cause and preserve a failing regression.
- [ ] Implement only the owned correction.
- [ ] Validate positive and failure/recovery behavior and report evidence.

## Interfaces / Contracts

Consume published Shared contracts and existing MCP product evidence / durable conversation lifecycle. No new wire or schema contract is authorized. Cross-repository gaps return to architect.

## Dependencies

None.

## Enables

Developer integration and production verification after architect acceptance of both tasks.

## Acceptance Criteria

- [ ] Requirements demonstrated with deterministic positive and negative regression tests.
- [ ] Existing tenant, domain, message identity and lifecycle guarantees preserved.
- [ ] No duplicate delivery, live test send, secret logging or unrelated changes.
- [ ] Completion Report records canonical launcher packet, physical isolation, synchronization and recursive submodule evidence.

## Validation

- [ ] Focused schema/render tests for null PRODUCT_ONLY link omission, mutation null rejection, unsafe/non-HTTPS/auth/port/offdomain rejection; full Shared suite, typecheck/build, packed installed public exports and immutable artifact hashes.
- [ ] Exact changed-file scope and secret hygiene review.

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

Pending actual implementation review.

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

None
