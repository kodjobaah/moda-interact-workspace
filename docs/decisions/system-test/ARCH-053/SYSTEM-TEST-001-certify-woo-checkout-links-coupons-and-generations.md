---
id: ARCH-053-SYSTEM-TEST-001
architecture_id: ARCH-053
title: Certify core Woo checkout link and recovery-generation lifecycle
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 80
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-053-BACKGROUND-003
- ARCH-053-WOOCOMMERCE-002
- ARCH-053-WOOCOMMERCE-003
- ARCH-048-BACKGROUND-011
- ARCH-046-WOOCOMMERCE-003
enables: []
created: 2026-10-29
updated: 2026-10-31
---

# ARCH-053-SYSTEM-TEST-001 — Certify core Woo checkout link and recovery-generation lifecycle

## Architecture

Architecture ID: `ARCH-053`. Document: `docs/architecture/ARCH-053-woocommerce-checkout-recovery-links-and-cart-restoration.md`. Coordinator: `moda_architect`. **Portable canonical task: defined but not materialised**; no Git branch, worktree, commit, push, review or producer deployment claimed.

## Objective

Certify core Woo checkout link and recovery-generation lifecycle. One bounded outcome in `moda-interact-system-test` owned by `moda_system_test`.

## Context

The inspected snapshot is dated 2026-10-30 07:59. ARCH-052 owns dynamic discount discovery and is not a checkout-URL implementation domain. ARCH-048-BACKGROUND-007..011 task files are present, but none has been accepted Complete in this snapshot (007 Ready, 008–011 Pending). This task is **Pending** from the snapshot/dependency inventory, subject to fresh launcher re-gating.

## Scope

- Add an ARCH-053-specific test runner/fixtures in `moda-interact-system-test` following its existing package scripts and orchestration patterns; run real supported Woo/WordPress Classic + Blocks, hosted API, Redis/BullMQ, Postgres migrations and guarded outbound mocks. Do not modify other repositories' code or task files.
- Verify capture of 1..50 core lines including variations/attributes and **no-applied-coupon** snapshot cases, canonical v1 HTTP schema → existing v1 queue projection, candidate update, admission's immutable `wooRestoreSnapshot` and URL, template CTA safety, authenticated resolution and cross-device customer confirmation. Full applied-coupon lifecycle is assigned to `ARCH-053-SYSTEM-TEST-002`.
- Verify HTTP `woo.activity.v1` with or without phone, preserve canonical phone proof validation and reject `woo.activity.v2`/`woo.activity.v3` after coordinated cutover; none of these may create a second queue envelope.
- Test 2 shops (correct installation auth and hostname), same original checkout with generation 1→resumption→generation 2, independent eligible initial outreach without cross-generation cap, duplicate event and retry suppression, historical URL revocation, order placement/paid suppression, consent withdrawal/STOP, status terminality and delivery retry failures.
- Assert the core restore flow uses *current* Woo pricing/tax/shipping, no historical totals; do not certify coupon-bearing restores under this task. The complete original-coupon matrix and **storefront-silent private diagnostics / correct totals** are terminal SYSTEM-TEST-002 responsibilities.
- Security matrix: WhatsApp preview GET and HEAD no cart mutation, forged POST/nonce, wrong token/wrong tenant, superseded generation, older link with newer shopping basket, existing cart confirmation, unsupported extension item/no silent partial restore, malicious URL host/subpath, no PII/coupon/token in logs/referrer, WordPress offline and API outage.
- Capture manual direct return to original Woo session with unchanged fingerprint and new user interaction; confirm **one new delayed BullMQ candidate** (not an immediate CheckoutRecovery) and no event from idle homepage or passive scanner.

## Out of Scope

No production WhatsApp sending, coupon issuance/dynamic discount tools, non-test service source edits or new runtime capabilities.

No execution of Enabled tasks, unrelated cross-repository implementation, extra database objects or new generic logger.

## Requirements

- System test is terminal: all implementation/publication/infrastructure prerequisite tasks must be accepted **Complete** before running. Developer may first manually test integrations.
- Do not claim true order safety for activity the plugin never delivered; record exact residual risk and monitoring. A test mock of Meta delivery is NOT production send activation.
- Validate token/URL 7-day freshness, revocation, queue lag, retry/dedup boundaries and no cross-generation billing mutation. Do not send real WhatsApp messages.

### Mandatory workflow/security invariants

- Inspect `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, `docs/developer-task-workflow.md`, `docs/task-definition-materialization.md` and the launcher preparation evidence. Use the **dedicated, synchronized parent and implementation task worktrees**; do not operate from a shared checkout or claim a branch was pushed without evidence. Implement only the owning repository and assigned task metadata. No unrelated refactors, migrations, agent handoffs or remote pushes to `main`.
- Read the ARCH-053 parent architecture and all dependency tasks before claiming Ready. Any missing contract or incorrect owner is a blocking architect question; do not invent a local parallel schema or silently change another agent's task. System-test tasks must remain terminal.
- Never swallow unexpected errors: Node uses `@modainteract/moda-interact-shared/logging`; PHP uses the existing safe plugin diagnostics (not a competing generic Node logger). Report bounded event codes, ids and outcomes, propagate retryable failures to their owning boundary, omit tokens, full URLs, coupon codes and customer personal data from logs.
- The plugin cannot access PostgreSQL/Redis. The API cannot mutate merchant WordPress cart sessions. Background cannot directly call an unverified merchant endpoint to mint URLs. Do not enable Woo production WhatsApp sending, relax final consent/STOP/order gates, or add cross-generation outreach caps/cooldowns.

## Work Items

- [ ] Create cross-service fixtures with two merchants and multiple Woo sessions/browsers.
- [ ] Run core product/cross-device/Classic+Blocks restoration with `appliedCouponCodes: []` and recovery-generation scenario matrix.
- [ ] Run security/consent/STOP/terminal/order/error/retry tests: assert technical failures have private diagnostics and **no Moda-generated errors or Woo notices triggered by Moda** in checkout HTML/redirect/session/console; record evidence.
- [ ] Return defects to owning agent tasks with a precise failing reproduction; complete test report; do not mutate implementation.

## Interfaces / Contracts

Consumes accepted ARCH-053 Shared v1 restore, HTTP v1 activity, v1 queue optional restoration, API resolve v1, generation-specific URL and ARCH-048 next-generation lifecycle. No additional implementation contract.

## Dependencies

- `ARCH-053-BACKGROUND-003` (must be architect-accepted Complete)
- `ARCH-053-WOOCOMMERCE-002` (must be architect-accepted Complete)
- `ARCH-053-WOOCOMMERCE-003` (must be architect-accepted Complete)
- `ARCH-048-BACKGROUND-011` (must be architect-accepted Complete)
- `ARCH-046-WOOCOMMERCE-003` (must be architect-accepted Complete)

## Enables

None.

## Acceptance Criteria

- [ ] Create cross-service fixtures with two merchants and multiple Woo sessions/browsers.
- [ ] Run core product/cross-device/Classic+Blocks restoration with `appliedCouponCodes: []` and recovery-generation scenario matrix.
- [ ] Run security/consent/STOP/terminal/order/error/retry tests: assert technical failures have private diagnostics and **no Moda-generated errors or Woo notices triggered by Moda** in checkout HTML/redirect/session/console; record evidence.
- [ ] Return defects to owning agent tasks with a precise failing reproduction; complete test report; do not mutate implementation.
- [ ] No regression in tenant isolation, historical generation preservation, valid shopper cart or consent/STOP/terminal order guards.
- [ ] Tests demonstrate invalid/stale/replayed and unexpected failures never produce false restoration success, malformed URLs or **storefront-visible Moda errors**, while keeping recoverable server-side diagnostics.
- [ ] No change outside assigned domain repository code plus owned task Completion Report; no ARCH-052 work.

## Validation

- [ ] Existing system-test repository declared integration commands; include exact command/version/environment in evidence
- [ ] Cross-browser real Woo tests without previously applied coupons, two-tenant Postgres/Redis integration and deterministic replay
- [ ] `git diff --check` and terminal Completion Report with explicit pass/fail matrix

## Stop Condition

When Work Items, Acceptance Criteria and required Validation are complete, update ONLY this task's authorised execution metadata, checklists and Completion Report, set `status: review` and return to `moda_architect`; **STOP**. Do not begin Enables, merge task branches, push `main` or change Architect Review yourself.

## Implementation Notes

Before Ready, confirm ARCH-048-BACKGROUND-011 and ARCH-046-WOOCOMMERCE-003 have been materialised and accepted; if either is missing, leave this Pending. Do not introduce a dependency from an implementation task to this system test.

## Completion Report

### Status

Not Started

### Files Changed

None — portable task definition only.

### Work Completed

Not Started.

### Validation Results

Not Run — no implementation claimed.

### Deviations

None.

### Assumptions

Design reconciled against uploaded 2026-10-30 07:59 source snapshot; re-check source and prior task acceptance before implementation.

### Unresolved Issues

None asserted as executed; dependencies must be materialised/accepted.

### Architectural Concerns

Return any cross-service schema/provider/transaction concern to `moda_architect` before improvising.

## Architect Review

### Review Status

Pending

### Review Notes

Not Reviewed — task not executed.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

To be assessed after implementation.

### Follow-up

None.
