---
id: ARCH-052-SHARED-005
architecture_id: ARCH-052
title: Define strict version-one verified discount proof request and response
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

# ARCH-052-SHARED-005: Define strict version-one verified discount proof request and response

## Architecture

Architecture ID: `ARCH-052`.

Architecture document: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`.

Coordinator: `moda_architect`. This is a **portable canonical definition — defined but not materialised**. No developer Git branch/worktree, commit or push is asserted.

## Objective

Define one portable request/result schema for Background, Commerce and API provider-verified checkout discount decisions.

## Context

Existing Background `ProviderEligibilityResult` is repository-local; the Commerce evaluator and Woo provider boundary need a single public-package read-only wire contract, not independently invented JSON shapes.

Evidence and paths refer to the 29 October 2026 08:07 uploaded workspace snapshot; implementation must re-read current task/code before claiming.

## Scope

- Create `moda-interact-shared/src/recovery-offer-proof.ts` and published package subpath `/recovery-offer-proof`; export `RecoveryDiscountProofRequestSchema`, `RecoveryDiscountProofResultSchema` and inferred types; validate JSON strictly (no unknown fields).
- Request exactly `{version:1,shopId:string,checkoutRecoveryId:string,checkoutFingerprint:string,discountId:string}` with nonempty bounded IDs <=128 chars; server loads checkout, customer and candidate only from its own trusted database after authorisation. Do not accept caller-supplied prices, lineItems, coupon codes, customer identifiers, eligibility conclusions or provider URLs.
- Result discriminant `{version:1,outcome:"eligible",evidence:{shopId,checkoutRecoveryId,providerDiscountId,checkoutFingerprint,evaluatedAt,expiresAt,currency,savingsMinor,verifiedCode,verifiedDescription,verifiedConstraints}}` OR `{version:1,outcome:"ineligible"|"unavailable",reason:one of ["NOT_ELIGIBLE","UNSUPPORTED_RULE","PROVIDER_UNAVAILABLE","STALE_CHECKOUT","REVOKED_GRANT","UNKNOWN_CUSTOMER"]}`. Times ISO UTC, expiry <=5min after evaluatedAt, valid positive safe-integer savingsMinor, ISO 4217 currency, verified code null only for automatic offer; bound description <=160 chars and each of <=10 constraints <=80 chars.
- Define response refusal on mismatched shop/checkout/fingerprint/discount even if HMAC authentication is valid. Proof is ephemeral decision data, never a merchant-save flag or permission to mutate a provider basket.
- Provide shared fixture vectors for Shopify and Woo PHP parity, a branded data-bound model type, strict parsing and rejection of timestamp/currency/count overflow, false/unknown eligibility, extra fields, mismatched tenant or invalid code.

## Out of Scope

- No network route, HMAC implementation, provider-rule engine or schema migration.

No out-of-repository modifications, new competing generic logger, uncapped provider operations, or implementation of Enables tasks.

## Requirements

- Consumers must parse exact published Shared schema and then re-check current checked identifiers/timestamps; do not define local alternate proof payloads.
- Review `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, and task preparation packet. Use dedicated mirrored task worktrees, correct start-of-attempt synchronization, and record both histories.
- Use `@modainteract/moda-interact-shared/logging` for new Node runtime logs. Unexpected exceptions must be logged with bounded, non-sensitive context and propagated to the owning retry/failure boundary; avoid silent catch. Plugin PHP must reuse its existing bounded operational logger.
- Do not send raw checkout URLs, bearer tokens, customer personal data or untrusted media source URLs to logs/telemetry.
- Provider mutation is prohibited except the customer-initiated Woo cart restoration explicitly owned by WOOCOMMERCE-002.

## Work Items

- [ ] Implement strict request and discriminated response schema.
- [ ] Add cross-producer consumer vector fixtures and negative parsing tests.
- [ ] Publish via dependent SHARED-003, not inside this task.

## Interfaces / Contracts

- `@modainteract/moda-interact-shared/recovery-offer-proof` exports `RecoveryDiscountProofRequestSchema`, `RecoveryDiscountProofResultSchema` and types.

## Dependencies

None.

All dependencies must be `status: complete` in the authoritative individual task YAML immediately before launcher preparation; architect acceptance or Ready alone is insufficient. No non-system-test task depends on a system-test task.

## Enables

- `ARCH-052-SHARED-003`

## Acceptance Criteria

- [ ] One exact contract covers Shopify and Woo without provider-specific payload guesses; invalid/unknown rules cannot produce `eligible`.

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
