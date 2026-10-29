---
id: ARCH-052-SHARED-005
architecture_id: ARCH-052
title: Define a typed provider discount-evidence payload for on-demand MCP calls
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 10
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables:
- ARCH-052-SHARED-003
created: '2026-10-29'
updated: '2026-10-29'
---

# ARCH-052-SHARED-005: Define a typed provider discount-evidence payload for on-demand MCP calls

## Architecture

Architecture ID: `ARCH-052`.

Architecture document: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`.

Coordinator: `moda_architect`. This is a **portable canonical definition — defined but not materialised**. No developer Git branch/worktree, commit or push is asserted.

## Objective

Create the narrow, versioned, cross-service data schema for an **on-demand** discount-evaluation result. This task does not define a bulk eligibility scan, create a second MCP result envelope or impose a provider call for every catalogue candidate.

## Context

The 29 October snapshot does not contain `moda-interact-shared/src/recovery-offer-proof.ts` or the proposed `RecoveryDiscountProofRequestSchema`/`RecoveryDiscountProofResultSchema`. This task **creates** those exports; do not describe them as existing. MCP provides read-only provider information through the existing generic `CommerceToolResultSchema` envelope. Background's agent decides which tools to call.

## Scope

- Create `src/recovery-offer-proof.ts` with `RecoveryDiscountProofRequestSchema` and `RecoveryDiscountProofResultSchema`, and export them from the existing browser-safe package entrypoint `/recovery-offer-proof`. This is one **feature-specific `data` schema**: MCP keeps using `CommerceToolResultSchema` for all tools.
- Request carries trusted shop/recovery/attempt identifiers, provider discount ID, checkout fingerprint and a discriminated `target: {kind:"CHECKOUT"} | {kind:"ALTERNATIVE_PRODUCT",productId:string,variantId:string|null}`; never accept model-supplied product URLs or prices as proof.
- Result discriminates `eligible`, `ineligible`, `unsupported`, `unavailable`, `stale`. Positive `eligible` carries exact shop/recovery/attempt, discount and target identifiers, verified code/automatic method, current evidence timestamp, bounded expiration, currency, and positive savings/benefit if the provider can establish it. Alternative promotions must be expressly marked `ALTERNATIVE_PRODUCT` and cannot be rendered as checkout discounts.
- Do not claim that a catalogue row, model output or matching category proves customer eligibility. MCP may perform **targeted** provider verification when requested, without scanning the full catalogue first. Unavailable/unsupported provider rules are never silently treated as eligible.
- Add deterministic positive and negative cross-consumer fixtures: wrong shop/target/fingerprint, malformed expiry, unknown customer rules, truncated/provider failure, ineligible and unavailable; verify no provider mutation.

## Out of Scope

- No network route, HMAC implementation, provider-rule engine or schema migration.

No out-of-repository modifications, new competing generic logger, uncapped provider operations, or implementation of Enables tasks.

## Requirements

- Consumers must parse exact published Shared schema and then re-check current checked identifiers/timestamps; do not define local alternate proof payloads.
- Review `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, and task preparation packet. Use dedicated mirrored task worktrees, correct start-of-attempt synchronization, and record both histories.
- Use `@modainteract/moda-interact-shared/logging` for new Node runtime logs. Unexpected exceptions must be logged with bounded, non-sensitive context and propagated to the owning retry/failure boundary; avoid silent catch. Plugin PHP must reuse its existing bounded operational logger.
- Do not send raw checkout URLs, bearer tokens, customer personal data or untrusted media source URLs to logs/telemetry.
- Provider cart, coupon and order mutation is prohibited in ARCH-052. Checkout-link creation and customer-click cart restoration are upstream/out of scope.

## Work Items

- [ ] Create the new request and outcome schemas and publish the entrypoint metadata in the implementation task.
- [ ] Add cross-service fixtures and negative parsing tests.
- [ ] Run Shared declared tests/typecheck/build; SHARED-003 handles publication separately.

## Interfaces / Contracts

`@modainteract/moda-interact-shared/recovery-offer-proof`: newly created `RecoveryDiscountProofRequestSchema`, `RecoveryDiscountProofResultSchema`, and inferred types for Commerce producer, MCP validator, and Background consumer. They are **payload schemas inside** the existing `CommerceToolResultSchema` response; no second tool-result envelope.

## Dependencies

None.

Dependencies are authoritative in YAML; system tests are terminal validation and must never block implementation.

## Enables

- `ARCH-052-SHARED-003`

## Acceptance Criteria

- [ ] On-demand evaluation returns typed evidence with explicit checkout versus alternative-product target.
- [ ] No new general-purpose MCP envelope, bulk scan runner, Prisma change or private authentication scheme.
- [ ] Unknown/unsupported provider restrictions cannot be interpreted as proof of eligibility.

## Validation

- [ ] Run Shared unit tests and package typecheck/build for new export.
- [ ] `git diff --check`.

Use actual repository scripts rather than assuming uniform `npm` commands; record required integration harness/environment gaps without claiming unrun tests passed.

## Stop Condition

After all Work Items, Acceptance Criteria and required Validation pass, complete the report, set task `status: review`, hand the implementation branch and parent task report to `moda_architect` and **STOP**. Do not begin a dependent task, merge, push main, or edit architecture indexes as a repository agent.

## Implementation Notes

**Expected owning repository locations (verify paths in the execution worktree; create proposed paths only if appropriate):**

- `moda-interact-shared/src/recovery-offer-proof.ts`
- `moda-interact-shared/src/recovery-offer-proof.test.ts`
- `moda-interact-shared/package.json`

Source ownership is restricted to the assigned repository plus this task file. `moda_architect` owns architectural/dependency/index reconciliation. The implementing agent should stop for an architectural connector/schema gap rather than inventing a cross-repository workaround.

## Completion Report

### Status

Not Started — portable definition, no task claim.

### Files Changed

None yet.

### Work Completed

None yet.

### Validation Results

Not run.

### Deviations

None reported.

### Assumptions

Execution will verify its current workspace, source state, dependency versions and test harness.

### Unresolved Issues

None established by implementation.

### Architectural Concerns

Report discovered cross-repository/credential/provider-proof issues to `moda_architect`.


## Architect Review

### Review Status

Pending.

### Review Notes

Planning only; no source implementation accepted.

### Reviewed Files

The task definition was authored from the 29 October 2026 snapshot; a code implementation has not been reviewed.

### Validation Reviewed

None for implementation.

### Architecture Conformance

To be determined after implementation review.

### Follow-up

Materialise with the canonical task launcher after the planning patch is integrated and dependencies become Complete.
