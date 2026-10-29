---
id: ARCH-052-BACKGROUND-008
architecture_id: ARCH-052
title: Integrate all three offer modes and fallback templates at final initial send
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 65
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-052-BACKGROUND-003
- ARCH-052-BACKGROUND-004
- ARCH-052-BACKGROUND-005
- ARCH-052-BACKGROUND-006
- ARCH-052-BACKGROUND-007
- ARCH-052-ADMIN-001
- ARCH-052-ADMIN-002
enables:
- ARCH-052-SYSTEM-TEST-001
- ARCH-052-SYSTEM-TEST-002
created: '2026-10-29'
updated: '2026-10-29'
---

# ARCH-052-BACKGROUND-008: Integrate all three offer modes and fallback templates at final initial send

## Architecture

Architecture ID: `ARCH-052`.

Architecture document: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`.

Coordinator: `moda_architect`. This is a **portable canonical definition — defined but not materialised**. No developer Git branch/worktree, commit or push is asserted.

## Objective

Compose the existing INITIAL send with authoritative checkout description, verified offer presentation, trusted CTA and optional READY product media.

## Context

ARCH-047 BG006 already integrates `AutomatedRecoveryTemplateService` with initial send and final Meta/credit admission; ARCH-048 Woo outreach and ARCH-050 Support notices are complete. This task extends those, not creates a new send pipeline.

Evidence and paths refer to the 29 October 2026 08:07 uploaded workspace snapshot; implementation must re-read current task/code before claiming.

## Scope

- Use the frozen policy selection snapshot and provider/AI verification outcomes to choose INITIAL_NO_OFFER, INITIAL_CODE_OFFER or INITIAL_AUTOMATIC_OFFER and the correct approved shop/WABA/language template.
- Bind customer first name, brand name, `checkout.itemsSummary`, existing translated `shop.categoryName`, trusted checkout CTA and only verified offer description/code, with no unapproved dynamic text.
- Integrate READY recovery product media with Admin-selected IMAGE role; when absent use a separately approved no-image fallback, preserving immutable registration and final status/age fencing.
- Recheck checkout freshness/evidence expiry immediately before prepare/final send; keep provider verification and R2/network work outside SQL transactions, and never change credit/STOP/consent/reachability/moderation/usage/attempt limits.
- Persist correct sequence-one promise evidence for any later follow-up; retries cannot change offered code or double-send/double-charge.

## Out of Scope

- No new Meta template creation on send path, no independent billing/consent engine, no cart mutations, no reopening ARCH-050 notices or paid follow-up business changes.

No out-of-repository modifications, new competing generic logger, uncapped provider operations, or implementation of Enables tasks.

## Requirements

- Discount-unavailable must select NO_OFFER only if that is a valid separately approved choice under the existing final admission, never fabricate a coupon.
- If no approved matching variant or valid checkout button exists, return a typed non-send; no generic public cart URL substitution.
- Review `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, and task preparation packet. Use dedicated mirrored task worktrees, correct start-of-attempt synchronization, and record both histories.
- Use `@modainteract/moda-interact-shared/logging` for new Node runtime logs. Unexpected exceptions must be logged with bounded, non-sensitive context and propagated to the owning retry/failure boundary; avoid silent catch. Plugin PHP must reuse its existing bounded operational logger.
- Do not send raw checkout URLs, bearer tokens, customer personal data or untrusted media source URLs to logs/telemetry.
- Provider mutation is prohibited except the customer-initiated Woo cart restoration explicitly owned by WOOCOMMERCE-002.

## Work Items

- [ ] Wire production template inputs and selection fallback.
- [ ] Preserve initial promise snapshot, retries and final-send gate semantics.
- [ ] Run failure/race and PostgreSQL/Meta simulator integration suites for both platforms.

## Interfaces / Contracts

- Existing `AutomatedRecoveryTemplateService`, `RecoveryOfferDecision`, frozen ARCH-047/049 Meta `PreparedRecoveryTemplate`, existing `OutboundMessageDeliveryService` and final SQL permit.

## Dependencies

- `ARCH-052-BACKGROUND-003` — new ARCH-052 prerequisite (not yet materialised).
- `ARCH-052-BACKGROUND-004` — new ARCH-052 prerequisite (not yet materialised).
- `ARCH-052-BACKGROUND-005` — new ARCH-052 prerequisite (not yet materialised).
- `ARCH-052-BACKGROUND-006` — new ARCH-052 prerequisite (not yet materialised).
- `ARCH-052-BACKGROUND-007` — new ARCH-052 prerequisite (not yet materialised).
- `ARCH-052-ADMIN-001` — new ARCH-052 prerequisite (not yet materialised).
- `ARCH-052-ADMIN-002` — new ARCH-052 prerequisite (not yet materialised).

All dependencies must be `status: complete` in the authoritative individual task YAML immediately before launcher preparation; architect acceptance or Ready alone is insufficient. No non-system-test task depends on a system-test task.

## Enables

- `ARCH-052-SYSTEM-TEST-001`
- `ARCH-052-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] All three modes produce expected template purpose, no-eligible AI/FIXED fallback and correct return link.
- [ ] No duplicate initial send/credit, existing merchant Support notification and human handover remain correct.
- [ ] No raw product image URL or stale/bogus discount can reach provider payload.

## Validation

- [ ] Background initial-send unit and PostgreSQL tests (Shopify + Woo, duplicate/retry/provider race).
- [ ] Existing ARCH-047/048/050 admission, moderation, STOP, credit and notification suites.
- [ ] Background build/lint and `git diff --check`.

Use actual repository scripts rather than assuming uniform `npm` commands; record required integration harness/environment gaps without claiming unrun tests passed.

## Stop Condition

After all Work Items, Acceptance Criteria and required Validation pass, complete the report, set task `status: review`, hand the implementation branch and parent task report to `moda_architect` and **STOP**. Do not begin a dependent task, merge, push main, or edit architecture indexes as a repository agent.

## Implementation Notes

**Expected owning repository locations (verify paths in the execution worktree; create proposed paths only if appropriate):**

- `moda-interact-background/src/services/recovery-template-integration/automated-recovery-template.service.ts`
- `moda-interact-background/src/services/recovery-template-preparation/`
- `moda-interact-background/src/services/checkout-recovery/recovery-initiation.service.ts`
- `moda-interact-background/src/services/woocommerce-recovery/`
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
