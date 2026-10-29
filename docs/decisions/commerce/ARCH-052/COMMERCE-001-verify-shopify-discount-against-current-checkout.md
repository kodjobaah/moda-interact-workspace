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
status: ready
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables:
- ARCH-052-COMMERCE-003
- ARCH-052-COMMERCE-008
- ARCH-052-SYSTEM-TEST-001
created: '2026-10-29'
updated: '2026-10-29'
---

# ARCH-052-COMMERCE-001: Prove Shopify discount eligibility for a recovery checkout

## Architecture

Architecture ID: `ARCH-052`.

Architecture document: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`.

Coordinator: `moda_architect`. This is a **portable canonical definition — defined but not materialised**. No developer Git branch/worktree, commit or push is asserted.

## Objective

Provide independent, read-only current Shopify discount eligibility evidence for the supported, provable discount subset.

## Context

`moda-interact-commerce/src/commerce/discounts/evaluator/` already exists. Its `docs/discount-support-matrix.md` explicitly leaves Shopify rounding semantics UNKNOWN, so `QUALIFIES_FOR_KNOWN_RULES` must not be assumed to prove checkout redemption.

Evidence and paths refer to the 29 October 2026 08:07 uploaded workspace snapshot; implementation must re-read current task/code before claiming.

## Scope

- Extend existing Shopify rule reader/evaluator and trusted basket/product-facts adapters; do not create a second discount engine.
- Verify customer eligibility, subscription/market/currency restrictions, product/variant/collection applicability, minimum requirements, code identity/usage where provider supports reliable read proof, combination and price/rounding semantics for each explicitly supported rule family.
- Return narrow proof with current checkout fingerprint, rule fingerprint, evaluated/expires times, currency, positive minor-unit savings, verified code/description and exact unsupported/unknown reasons.
- Return an exact successful/unsupported per-checkout proof to the independent authenticated Commerce-003 private route; the implementing agent must NOT choose a new transport or public API. Commerce-003 is the explicitly assigned endpoint owner.

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
- Provider mutation is prohibited except the customer-initiated Woo cart restoration explicitly owned by WOOCOMMERCE-002.

## Work Items

- [ ] Close provable Shopify calculation/eligibility gaps with evidence.
- [ ] Expose read-only proof on existing approved private boundary.
- [ ] Add real provider fixture plus negative/unknown deterministic tests.

## Interfaces / Contracts

- Existing `discounts.evaluate` and `CommerceEvidence` / rule reader; new narrow read-only recovery proof adapter consumed by BG003, with exact-time and fingerprint checks.

## Dependencies

None.

Dependencies are authoritative in YAML; system tests are terminal validation and must never block implementation.

## Enables

- `ARCH-052-COMMERCE-003`
- `ARCH-052-COMMERCE-008`
- `ARCH-052-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Only positively verified supported offer types return savings proof.
- [ ] Unsupported restrictions or rounding never default to eligible; Shopify product search remains read-only.

## Validation

- [ ] Commerce discount evaluator/reader fixtures, provider snapshot compatibility and bounded access tests.
- [ ] Commerce build/typecheck/lint as declared and `git diff --check`.

Use actual repository scripts rather than assuming uniform `npm` commands; record required integration harness/environment gaps without claiming unrun tests passed.

## Stop Condition

After all Work Items, Acceptance Criteria and required Validation pass, complete the report, set task `status: review`, hand the implementation branch and parent task report to `moda_architect` and **STOP**. Do not begin a dependent task, merge, push main, or edit architecture indexes as a repository agent.

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

Planning only; no source implementation accepted.

### Reviewed Files

The task definition was authored from the 29 October 2026 snapshot; a code implementation has not been reviewed.

### Validation Reviewed

None for implementation.

### Architecture Conformance

To be determined after implementation review.

### Follow-up

Materialise with the canonical task launcher after the planning patch is integrated and dependencies become Complete.
