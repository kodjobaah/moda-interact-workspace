---
id: ARCH-040-SYSTEM-TEST-003
architecture_id: ARCH-040
title: Certify Woo recovery-detail conversation and basket end-to-end
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 40
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-040-WOOCOMMERCE-003
  - ARCH-040-SYSTEM-TEST-001
enables: []
created: 2026-10-14
updated: 2026-10-15
---

# ARCH-040-SYSTEM-TEST-003 — Certify Woo recovery-detail conversation and basket end-to-end

## Architecture

Initiative: `ARCH-040`. Architecture document: `docs/architecture/ARCH-040-merchant-customer-conversations-human-handover.md`. Coordinator: `moda_architect`. **Portable definition only; defined but not materialised, no branch/commit/worktree.**

## Objective

Certify the **existing Woo Recoveries -> Recovery Detail** basket + conversation + human handover experience, using only WordPress REST -> Woo hosted API -> Prisma/Background.

## Context

Woo ARCH-035 provides the recovery detail shell/read baseline. ARCH-040 enriches it with saved basket/control state and human reply controls; no new Conversations menu/list is part of scope.

## Scope

- Woo WP-admin browser and LocalWP/WordPress REST end-to-end tests of existing recovery details plus basket/transcript/ownership.
- Customer service window/approved follow-up and shared credit identity tests across Woo human and CommerceAgent.

## Out of Scope

No new Woo inbox/menu, staff role/assignment, new conversation datastore or JS direct hosted API calls. No `_index.md` changes.

## Requirements

- Preserve two-stage WooCommerce > Moda Interact navigation. Choose recovery using existing list; verify the same detail screen shows basket snapshot, currency, quantity, variants, original conversation and milestones/related.
- Capture desktop + narrow-screen evidence per WOOCOMMERCE-002 ASCII. Missing/partial basket and missing conversation must not break page.
- Verify 20 Woo admin locales/site fallback and keep conversation language untouched.
- Exercise `manage_woocommerce`/REST nonce, installation rotation/disconnect, cross-shop protection, command status and provider receipt reconciliation.
- Verify Take Over/Resume, open-window text, closed-window eligible template, sequence-2 uniqueness, single follow-up credit, and correct HUMAN control retention after inbound customer messages.

## Work Items

- [ ] Validate original Recoveries entry/detail basket/transcript responsive UX and 20 locales.
- [ ] Exercise secure WP proxy and connected hosted API reads/commands, negative auth/disconnect.
- [ ] Validate one-thread follow-up and receipt/credit invariants with provider and PostgreSQL evidence.

## Interfaces / Contracts

Woo WP-admin -> WordPress recovery detail REST -> existing Woo hosted recovery read endpoints enriched by API-002; API-003/004 for commands -> canonical Prisma/Background. No standalone inbox.

## Dependencies

- ARCH-040-WOOCOMMERCE-003
- ARCH-040-SYSTEM-TEST-001

## Enables

None.

## Acceptance Criteria

- [ ] Woo Recoveries detail includes saved basket and real conversation, parity with Shopify without extra menu/navigation.
- [ ] Woo handover/window/follow-up/credit and idempotency match shared Background policy and no second Conversation.

## Validation

- [ ] LocalWP/full WP REST and system-test provider fixtures, responsive screenshots against ASCII.
- [ ] Plugin ZIP, 20-locale coverage, `git diff --check` and task worktree evidence.

## Implementation Notes

Preserve developer-owned ARCH-035 dependencies and existing pending task states; do not implement them from within ARCH-040 tasks.

## Stop Condition

After only this task's Work Items, Acceptance Criteria and Validation are complete, set status `review`, record Completion Report and return to moda_architect. STOP.

## Completion Report

### Status
Not Started

### Files Changed
None.

### Work Completed
None.

### Validation Results
Not run.

### Deviations
None.

### Assumptions
The architecture is proposed; implementation starts only after agreed/materialised task definition.

### Unresolved Issues
None recorded at definition time.

### Architectural Concerns
Return newly discovered contract or ownership gaps to moda_architect.

## Architect Review

### Review Status
Pending

### Review Notes
Not reviewed.

### Reviewed Files
None.

### Validation Reviewed
None.

### Architecture Conformance
Pending.

### Follow-up
None.
