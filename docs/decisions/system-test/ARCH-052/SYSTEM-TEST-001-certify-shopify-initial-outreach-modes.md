---
id: ARCH-052-SYSTEM-TEST-001
architecture_id: ARCH-052
title: Certify Shopify initial outreach personalization and all offer modes
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 95
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-052-BACKGROUND-008
- ARCH-052-SHOPIFY-001
- ARCH-052-BACKGROUND-009
- ARCH-052-COMMERCE-001
- ARCH-052-COMMERCE-002
- ARCH-052-ADMIN-001
- ARCH-052-ADMIN-002
- ARCH-052-SHARED-003
enables: []
created: '2026-10-29'
updated: '2026-10-29'
---

# ARCH-052-SYSTEM-TEST-001: Certify Shopify initial outreach personalization and all offer modes

## Architecture

Architecture ID: `ARCH-052`.

Architecture document: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`.

Coordinator: `moda_architect`. This is a **portable canonical definition — defined but not materialised**. No developer Git branch/worktree, commit or push is asserted.

## Objective

Independently certify the customer-visible Shopify initial WhatsApp send with no discount, merchant-selected valid discount and AI-selected verified discount.

## Context

Terminal cross-service validation after architect acceptance and developer manual inspection; do not implement upstream features inside system test.

Evidence and paths refer to the 29 October 2026 08:07 uploaded workspace snapshot; implementation must re-read current task/code before claiming.

## Scope

- Create isolated two-Shopify-shop PostgreSQL/Redis + Meta-simulator fixture, with previously-synced discount rows marked unchecked (`isAvailable:false`) and merchant-selected rows explicitly checked. Use NO/FIXED/AI, selected three-of-twenty and AI unselected product-applicable discounts.
- Verify new sync inserts unchecked, subsequent sync/outage/reinstall preserves selected flags, historical pre-ARCH-052 records are never reused, and ShopSettings first-ID anchor is not the complete selection authority.
- Test provider verified CODE/AUTOMATIC offers, no eligible discount, unknown rule -> NO_OFFER, irrelevant product discount, exact basket text, store category translations and absent category, image verification/fallback and verified checkout link.
- Exercise final WhatsApp send STOP/consent/moderation, duplicate BullMQ, credit reservation, follow-up confirmed promise and ARCH-050 Support notice deep-link. Record that simulator approval != Meta live approval.

## Out of Scope

- No production source modifications or downstream implementation tasks.

No out-of-repository modifications, new competing generic logger, uncapped provider operations, or implementation of Enables tasks.

## Requirements

- Record real test evidence and provider/API limitations; a mocked fixture alone is not a claim of live WhatsApp approval.
- Use architecture-approved test isolation, no customer data or real unauthorized WhatsApp sends.
- Review `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, and task preparation packet. Use dedicated mirrored task worktrees, correct start-of-attempt synchronization, and record both histories.
- Use `@modainteract/moda-interact-shared/logging` for new Node runtime logs. Unexpected exceptions must be logged with bounded, non-sensitive context and propagated to the owning retry/failure boundary; avoid silent catch. Plugin PHP must reuse its existing bounded operational logger.
- Do not send raw checkout URLs, bearer tokens, customer personal data or untrusted media source URLs to logs/telemetry.
- Provider mutation is prohibited except the customer-initiated Woo cart restoration explicitly owned by WOOCOMMERCE-002.

## Work Items

- [ ] Assemble isolated fixture and full initial send flows.
- [ ] Run negative/race/fallback/provider-budget matrix.
- [ ] Return certification and outstanding external Meta/provider checks.

## Interfaces / Contracts

- ARCH-052 accepted runtime, ARCH-047/049 approved templates, existing ARCH-050 Support notice and system test harness.

## Dependencies

- `ARCH-052-BACKGROUND-008` — new ARCH-052 prerequisite (not yet materialised).
- `ARCH-052-SHOPIFY-001` — new ARCH-052 prerequisite (not yet materialised).
- `ARCH-052-BACKGROUND-009` — new ARCH-052 prerequisite (not yet materialised).
- `ARCH-052-COMMERCE-001` — new ARCH-052 prerequisite (not yet materialised).
- `ARCH-052-COMMERCE-002` — new ARCH-052 prerequisite (not yet materialised).
- `ARCH-052-ADMIN-001` — new ARCH-052 prerequisite (not yet materialised).
- `ARCH-052-ADMIN-002` — new ARCH-052 prerequisite (not yet materialised).
- `ARCH-052-SHARED-003` — new ARCH-052 prerequisite (not yet materialised).

All dependencies must be `status: complete` in the authoritative individual task YAML immediately before launcher preparation; architect acceptance or Ready alone is insufficient. No non-system-test task depends on a system-test task.

## Enables

None.

## Acceptance Criteria

- [ ] Exact correct template/data for all three modes and safe no-offer outcomes.
- [ ] No unauthorized outbound, mismatched tenant image, false discount promise, duplicate credit or broken Support notice.

## Validation

- [ ] System-test declared integration commands, PostgreSQL/Redis and Meta simulator checks.
- [ ] Test evidence with logs/traces and `git diff --check`.

Use actual repository scripts rather than assuming uniform `npm` commands; record required integration harness/environment gaps without claiming unrun tests passed.

## Stop Condition

After all Work Items, Acceptance Criteria and required Validation pass, complete the report, set task `status: review`, hand the implementation branch and parent task report to `moda_architect` and **STOP**. Do not begin a dependent task, merge, push main, or edit architecture indexes as a repository agent.

## Implementation Notes

**Expected owning repository locations (verify paths in the execution worktree; create proposed paths only if appropriate):**

- `moda-interact-system-test/ (new ARCH-052 Shopify scenarios/fixtures)`

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
