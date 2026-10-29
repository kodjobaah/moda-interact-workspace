---
id: ARCH-052-BACKGROUND-003
architecture_id: ARCH-052
title: Wire independent Shopify and Woo checkout-specific eligibility adapters
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 45
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-052-BACKGROUND-002
- ARCH-052-COMMERCE-001
- ARCH-052-WOOCOMMERCE-001
enables:
- ARCH-052-BACKGROUND-004
- ARCH-052-BACKGROUND-008
created: '2026-10-29'
updated: '2026-10-29'
---

# ARCH-052-BACKGROUND-003: Wire independent Shopify and Woo checkout-specific eligibility adapters

## Architecture

Architecture ID: `ARCH-052`.

Architecture document: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`.

Coordinator: `moda_architect`. This is a **portable canonical definition — defined but not materialised**. No developer Git branch/worktree, commit or push is asserted.

## Objective

Replace noProviderEvaluator defaults with explicitly wired production provider-verification ports, preserving fail-closed evidence validation.

## Context

`src/services/recovery-offers/recovery-offer-providers.ts` defines ShopifyReadOnlyOfferAdapter/WooReadOnlyOfferAdapter but both use `noProviderEvaluator` by default. Positive cases in ARCH-047 tests are injected fixtures, not live proof.

Evidence and paths refer to the 29 October 2026 08:07 uploaded workspace snapshot; implementation must re-read current task/code before claiming.

## Scope

- Add a dedicated Shopify proof adapter to the approved Commerce read boundary; add a separate Woo proof client using existing encrypted authorised read-grant, safe canonical-origin transport and plugin native coupon eligibility route.
- Pin current shop/recovery/checkout fingerprint, provider discount identity, currency, observed time and expiry; map only proven positive results to `CheckoutRuleEvidence`. Ineligible versus unavailable versus transport failure must be explicit.
- Inject production readers into `RecoveryOfferResolver` in the existing composition module, not just test constructors. Reverify constraints on action path with bounded deadlines/concurrency and avoid provider network calls inside PostgreSQL permit transactions.
- Use shared logging, explicit retryable errors and no raw access token, customer PII, provider URL or discount credentials in logs.

## Out of Scope

- No provider coupon rule engine in Background, no new general logger, no checkout changes, no AI recommender.

No out-of-repository modifications, new competing generic logger, uncapped provider operations, or implementation of Enables tasks.

## Requirements

- Do not treat Commerce `QUALIFIES_FOR_KNOWN_RULES` as full proof unless COMMERCE001 explicitly certifies required restrictions.
- Provider unavailable is NEVER reported as an eligible zero-savings or approximate offer.
- Review `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, and task preparation packet. Use dedicated mirrored task worktrees, correct start-of-attempt synchronization, and record both histories.
- Use `@modainteract/moda-interact-shared/logging` for new Node runtime logs. Unexpected exceptions must be logged with bounded, non-sensitive context and propagated to the owning retry/failure boundary; avoid silent catch. Plugin PHP must reuse its existing bounded operational logger.
- Do not send raw checkout URLs, bearer tokens, customer personal data or untrusted media source URLs to logs/telemetry.
- Provider mutation is prohibited except the customer-initiated Woo cart restoration explicitly owned by WOOCOMMERCE-002.

## Work Items

- [ ] Implement two injectable provider adapters and production wiring.
- [ ] Add concurrent/revoked grant, provider failure, expired evidence and cross-shop fixtures.
- [ ] Run PostgreSQL-to-provider integration tests using local simulators.

## Interfaces / Contracts

- `ReadOnlyProviderEligibility.evaluate` and `CheckoutRuleEvidence` from `recovery-offer.types.ts`; Woo uses authenticated grant logic in `src/services/woo-coupon-grant.service.ts` and transport modules.

## Dependencies

- `ARCH-052-BACKGROUND-002` — new ARCH-052 prerequisite (not yet materialised).
- `ARCH-052-COMMERCE-001` — new ARCH-052 prerequisite (not yet materialised).
- `ARCH-052-WOOCOMMERCE-001` — new ARCH-052 prerequisite (not yet materialised).

All dependencies must be `status: complete` in the authoritative individual task YAML immediately before launcher preparation; architect acceptance or Ready alone is insufficient. No non-system-test task depends on a system-test task.

## Enables

- `ARCH-052-BACKGROUND-004`
- `ARCH-052-BACKGROUND-008`

## Acceptance Criteria

- [ ] Default production evaluator no longer silently returns `unavailable` for every valid provider.
- [ ] Unverifiable offers always fall back to NO_OFFER; no provider call within SQL transaction.
- [ ] Woo credential revocation/SSRF, Shopify wrong-shop and currency mismatches cannot produce sendable offers.

## Validation

- [ ] Background unit/provider integration with simulated Commerce/Woo transports and database-bound fixture.
- [ ] Background build/lint and `git diff --check`.

Use actual repository scripts rather than assuming uniform `npm` commands; record required integration harness/environment gaps without claiming unrun tests passed.

## Stop Condition

After all Work Items, Acceptance Criteria and required Validation pass, complete the report, set task `status: review`, hand the implementation branch and parent task report to `moda_architect` and **STOP**. Do not begin a dependent task, merge, push main, or edit architecture indexes as a repository agent.

## Implementation Notes

**Expected owning repository locations (verify paths in the execution worktree; create proposed paths only if appropriate):**

- `moda-interact-background/src/services/recovery-offers/recovery-offer-providers.ts`
- `moda-interact-background/src/services/recovery-offers/recovery-offer-resolver.service.ts`
- `moda-interact-background/src/services/woo-coupon-grant.service.ts`
- `moda-interact-background/tests/integration/`

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
