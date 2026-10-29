---
id: ARCH-052-BACKGROUND-001
architecture_id: ARCH-052
title: Freeze effective selected-discount policy at initial attempt creation
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 35
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-052-SHARED-003
- ARCH-052-SHOPIFY-001
- ARCH-052-API-001
- ARCH-052-BACKGROUND-009
enables:
- ARCH-052-BACKGROUND-002
created: '2026-10-29'
updated: '2026-10-29'
---

# ARCH-052-BACKGROUND-001: Freeze effective selected-discount policy at initial attempt creation

## Architecture

Architecture ID: `ARCH-052`.

Architecture document: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`.

Coordinator: `moda_architect`. This is a **portable canonical definition — defined but not materialised**. No developer Git branch/worktree, commit or push is asserted.

## Objective

Read effective merchant/override selections from existing ShopifyDiscount.isAvailable and freeze the verified permission set in RecoveryOutreachAttempt.offerSnapshot at the first attempt creation.

## Context

Existing `RecoveryPolicyService.resolve` considers only one fixedShopifyDiscountId and puts provider data into offerSnapshot. Existing `RecoveryOutreachAttempt.offerSnapshot Json?` is already persisted and cloned for follow-ups. No new field or table is needed.

Evidence and paths refer to the 29 October 2026 08:07 uploaded workspace snapshot; implementation must re-read current task/code before claiming.

## Scope

- Update `src/services/recovery-policy.service.ts`: if active Admin override use its own selected policy; otherwise FIXED reads at most 51 `ShopifyDiscount` IDs `{shopId,isAvailable:true}` sorted ASCII ascending, fails if >50; NONE and AI set effective `authorisedDiscountIds:[]`, even when dormant merchant flags remain selected. Override FIXED authorises only its one exact same-shop selected ID; never merge merchant flags.
- Keep `fixedShopifyDiscountId` first selected sorted anchor solely for existing EffectiveRecoveryPolicy schema, not authority. Remove provider-eligibility inference from policy reader; only provider proof may establish live applicability.
- In `src/services/recovery-outreach-attempt.service.ts` use existing `RecoveryOutreachAttempt.offerSnapshot Json?` only: on sequence-one INSERT persist Shared `RecoveryOfferSelectionSnapshotSchema` with frozen permission fields and required `sentOffer:null`. `upsert.update:{}` retains original snapshot when same attempt retries. Always parse persisted snapshot before resolving; old/syntax-invalid JSON fails closed and is not auto-upgraded.
- After confirmed initial Meta send, Background-008 atomically sets only `offerSnapshot.sentOffer` using CAS `sentOffer:null` and exact provider-verified offer sent (or `NO_OFFER`); never rewrite source/mode/selected IDs. Do not mark an unconfirmed provider send as a sent offer. On a crash/ambiguous provider response, reconcile the existing durable outbound message idempotency record or block follow-up; never invent a promise.
- On sequence-two creation, clone the original authorised selection and **actual** sentOffer from sequence-one JSON via existing `getOrCreateFollowUp` and API/Background raw SQL copier; never re-read current merchant selection or choose a new coupon. Sequence two with null/ambiguous sentOffer does no promised-offer follow-up.
- Remove resolver fallback from `fixedShopifyDiscountId` as selection authority; `RecoveryOfferPolicy.authorisedDiscountIds` is required whenever FIXED. Cover real Postgres tests for settings change vs attempt INSERT, double BullMQ execution, confirmed sentOffer CAS, unsuccessful send and follow-up clones; assert no new schema.

## Out of Scope

- No separate attempt snapshot field, new Prisma model, data backfill, provider/AI evaluation or meta sends.

No out-of-repository modifications, new competing generic logger, uncapped provider operations, or implementation of Enables tasks.

## Requirements

- Use existing `offerSnapshot Json` for two distinct facts: immutable versioned selection permission and `sentOffer`, which is set only after a provider-confirmed initial message. A selected ID alone is never evidence that an offer was promised; consumers must read the confirmed `sentOffer` field.
- Non-FIXED stored flags must not be interpreted as authorisation.
- Review `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, and task preparation packet. Use dedicated mirrored task worktrees, correct start-of-attempt synchronization, and record both histories.
- Use `@modainteract/moda-interact-shared/logging` for new Node runtime logs. Unexpected exceptions must be logged with bounded, non-sensitive context and propagated to the owning retry/failure boundary; avoid silent catch. Plugin PHP must reuse its existing bounded operational logger.
- Do not send raw checkout URLs, bearer tokens, customer personal data or untrusted media source URLs to logs/telemetry.
- Provider mutation is prohibited except the customer-initiated Woo cart restoration explicitly owned by WOOCOMMERCE-002.

## Work Items

- [ ] Read Shop selections and override correctly, validate against Shared parser.
- [ ] Freeze selected set once in attempt JSON and CAS actual sent offer after confirmed send.
- [ ] Remove implicit anchor fallback and validate follow-up clones in real PostgreSQL races.

## Interfaces / Contracts

- Existing `RecoveryOutreachAttempt.offerSnapshot` stores version-one JSON with `authorisedDiscountIds` and `sentOffer`, Shared-001 exact schema.

## Dependencies

- `ARCH-052-SHARED-003` — new ARCH-052 prerequisite (not yet materialised).
- `ARCH-052-SHOPIFY-001` — new ARCH-052 prerequisite (not yet materialised).
- `ARCH-052-API-001` — new ARCH-052 prerequisite (not yet materialised).
- `ARCH-052-BACKGROUND-009` — new ARCH-052 prerequisite (not yet materialised).

All dependencies must be `status: complete` in the authoritative individual task YAML immediately before launcher preparation; architect acceptance or Ready alone is insufficient. No non-system-test task depends on a system-test task.

## Enables

- `ARCH-052-BACKGROUND-002`

## Acceptance Criteria

- [ ] No new Prisma migration; selected set cannot change on retries and sentOffer cannot appear before provider send confirmation.
- [ ] Follow-up cannot promise any offer not actually included in confirmed sequence-one send.

## Validation

- [ ] Background policy/attempt unit and real PostgreSQL integration tests.
- [ ] Background declared typecheck/lint and `git diff --check`.

Use actual repository scripts rather than assuming uniform `npm` commands; record required integration harness/environment gaps without claiming unrun tests passed.

## Stop Condition

After all Work Items, Acceptance Criteria and required Validation pass, complete the report, set task `status: review`, hand the implementation branch and parent task report to `moda_architect` and **STOP**. Do not begin a dependent task, merge, push main, or edit architecture indexes as a repository agent.

## Implementation Notes

**Expected owning repository locations (verify paths in the execution worktree; create proposed paths only if appropriate):**

- `moda-interact-background/src/services/recovery-policy.service.ts`
- `moda-interact-background/src/services/recovery-outreach-attempt.service.ts`
- `moda-interact-background/src/services/recovery-offers/recovery-offer.types.ts`
- `moda-interact-background/src/services/recovery-offers/recovery-offer-resolver.service.ts`
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
