---
id: ARCH-052-COMMERCE-001
architecture_id: ARCH-052
title: Prove Shopify discount eligibility for a recovery checkout
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: superseded
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables: []
created: '2026-10-29'
updated: '2026-10-30'
---

# ARCH-052-COMMERCE-001: Prove Shopify discount eligibility for a recovery checkout

## Architecture

Architecture ID: `ARCH-052`.

Architecture document: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`.

Coordinator: `moda_architect`. This is a **portable canonical definition — defined but not materialised**. No developer Git branch/worktree, commit or push is asserted.

## Objective

**SUPERSEDED — DO NOT IMPLEMENT.** Checkout discount relevance is assessed by the dedicated Background InitialOutreachOfferAgent from factual MCP catalogue results; no separate Shopify proof engine.

The pre-existing description and completion-report placeholders elsewhere in this file remain historical only. No repository code or validation is authorised by this task.

## Context

`moda-interact-commerce/src/commerce/discounts/evaluator/` already exists. Its `docs/discount-support-matrix.md` explicitly leaves Shopify rounding semantics UNKNOWN, so `QUALIFIES_FOR_KNOWN_RULES` must not be assumed to prove checkout redemption.

Evidence and paths refer to the 29 October 2026 08:07 uploaded workspace snapshot; implementation must re-read current task/code before claiming.

## Scope

None. This task is withdrawn; do not start the original implementation, create new provider verification services or publish obsolete proof contracts.

## Out of Scope

- No cart mutation, discount application, Shopify settings UI, coupon authoring, message dispatch or Woo coupon proof.

No out-of-repository modifications, new competing generic logger, uncapped provider operations, or implementation of Enables tasks.

## Requirements

- Only independently verified provider rule families can return eligible; unknown rounding, usage limit or audience rules must fail closed to unavailable/ineligible, not optimistic discount.
- Use existing Commerce evaluator/reader; the background read-only proof adapter is a bounded contract and should never use checkout mutations.
- Do not invent a cross-service connection here: direct worker consumption is implemented only by the separate Commerce-003 private route.
- Review `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, and task preparation packet. Use dedicated mirrored task worktrees, correct start-of-attempt synchronization, and record both histories.
- Use `@modainteract/moda-interact-shared/logging` for new Node runtime logs. Unexpected exceptions must be logged with bounded, non-sensitive context and propagated to the owning retry/failure boundary; avoid silent catch. Plugin PHP must reuse its existing bounded operational logger.
- Do not send raw checkout URLs, bearer tokens, customer personal data or untrusted media source URLs to logs/telemetry.
- Provider cart, coupon and order mutation is prohibited in ARCH-052. Checkout-link creation and customer-click cart restoration are upstream/out of scope.

## Work Items

None — superseded; retain this historical definition only for audit.

## Interfaces / Contracts

- Existing `discounts.evaluate` and `CommerceEvidence` / rule reader; new narrow read-only recovery proof adapter consumed by BG003, with exact-time and fingerprint checks.

## Dependencies

None — superseded.

## Enables

None — superseded.

## Acceptance Criteria

None — superseded; no code is to be accepted under this task.

## Validation

Not applicable; the superseded implementation must not run.

## Stop Condition

This task is superseded. Do not claim, implement, run tests, publish, merge or unblock dependants from it.

## Implementation Notes

**Expected owning repository locations (verify paths in the execution worktree; create proposed paths only if appropriate):**

- `moda-interact-commerce/src/commerce/discounts/evaluator/`
- `moda-interact-commerce/src/commerce/discounts/reader/`
- `moda-interact-commerce/docs/discount-support-matrix.md`
- `moda-interact-commerce/tests/`

Source ownership is restricted to the assigned repository plus this task file. `moda_architect` owns architectural/dependency/index reconciliation. The implementing agent should stop for an architectural connector/schema gap rather than inventing a cross-repository workaround.

- Support eligibility only for rule families where provider state and currency/rounding/combination can be proven exactly; list unsupported families in fixture matrix.
- Never create generic public Commerce discount-verification endpoint.

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

**Architectural supersession (2026-10-30):** Checkout discount relevance is assessed by the dedicated Background InitialOutreachOfferAgent from factual MCP catalogue results; no separate Shopify proof engine.

Planning only; no source implementation accepted.

### Reviewed Files

The task definition was authored from the 29 October 2026 snapshot; a code implementation has not been reviewed.

### Validation Reviewed

None for implementation.

### Architecture Conformance

To be determined after implementation review.

### Follow-up

Materialise with the canonical task launcher after the planning patch is integrated and dependencies become Complete.
