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
- ARCH-052-COMMERCE-003
- ARCH-052-API-003
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

- In `src/services/recovery-offers/recovery-offer-providers.ts`, inject Shopify adapter that calls **only** Commerce-003 authenticated private `POST /internal/v1/recovery/discount-proof`, and Woo adapter that calls **only** API-003 identically named private path on distinct internal host. Use Shared-004 signature body and Shared-005 response schema; no direct provider credentials or direct plugin endpoints in Background.
- Build strict request from persisted checkout/discount row IDs and freshly computed `checkoutOfferFingerprint`, not client data. Use fixed origins `MODA_RECOVERY_PRIVATE_READ_COMMERCE_HOSTPORT` and `MODA_RECOVERY_PRIVATE_READ_API_HOSTPORT` supplied by Gateway-001; HTTPS not required inside Render service-private URL, but TLS/public customer URLs must never be accepted as origin overrides.
- For eligible evidence verify `shopId`, `checkoutRecoveryId`, `checkoutFingerprint`, `providerDiscountId`, currency, safe positive integer savings, `evaluatedAt <= now < expiresAt`, proof age <=5min, correct provider identity and `verifiedCode` for CODE offer. Mismatch => unavailable/no offer; never accept a proof for another checkout.
- No RPC for NONE; FIXED/AI comply Background-002 shortlist max 24, concurrency <=4, 2s call timeout and 15s total. Network exceptions are retryable with shared structured error log and cause, not a false eligibility result; ineligible skips, unavailable sends no unverified offer.
- Add integration tests with real signed HTTP fixtures for both services, wrong shop/nonce, stale fingerprint, missing HMAC environment, provider unavailable, Meta no-send for invalid proof and duplicate BullMQ initial job.

## Out of Scope

- No new database table, product/offer mutation, Meta send, prompt/schema inventing or independent provider eligibility calculation.

No out-of-repository modifications, new competing generic logger, uncapped provider operations, or implementation of Enables tasks.

## Requirements

- Fail closed on unverified evidence, including provider identity mismatch and unknown customer context.
- Use shared logger from @modainteract/moda-interact-shared/logging, preserving errors and reasons.
- Review `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, and task preparation packet. Use dedicated mirrored task worktrees, correct start-of-attempt synchronization, and record both histories.
- Use `@modainteract/moda-interact-shared/logging` for new Node runtime logs. Unexpected exceptions must be logged with bounded, non-sensitive context and propagated to the owning retry/failure boundary; avoid silent catch. Plugin PHP must reuse its existing bounded operational logger.
- Do not send raw checkout URLs, bearer tokens, customer personal data or untrusted media source URLs to logs/telemetry.
- Provider mutation is prohibited except the customer-initiated Woo cart restoration explicitly owned by WOOCOMMERCE-002.

## Work Items

- [ ] Implement Shopify/ Woo signed proof clients and exact immutable checkout identity checks.
- [ ] Connect both adapters, timeouts and retry classification to existing resolver.
- [ ] Add real HTTP/Redis mock proof and database cross-tenant tests.

## Interfaces / Contracts

- Exact two internal private origins, same fixed discount-proof route, HMAC Shared-004 and proof schema Shared-005.

## Dependencies

- `ARCH-052-BACKGROUND-002` — new ARCH-052 prerequisite (not yet materialised).
- `ARCH-052-COMMERCE-003` — new ARCH-052 prerequisite (not yet materialised).
- `ARCH-052-API-003` — new ARCH-052 prerequisite (not yet materialised).

All dependencies must be `status: complete` in the authoritative individual task YAML immediately before launcher preparation; architect acceptance or Ready alone is insufficient. No non-system-test task depends on a system-test task.

## Enables

- `ARCH-052-BACKGROUND-004`
- `ARCH-052-BACKGROUND-008`

## Acceptance Criteria

- [ ] Only authorised current checkout proof becomes a sendable offer; neither adapter relies on catalogue descriptions as proof.
- [ ] No public provider credentials or silent fault handling.

## Validation

- [ ] Background provider adapter and resolver tests, strict unit and PostgreSQL integration where durable state is read.
- [ ] Background package typecheck/lint and git diff --check.

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
