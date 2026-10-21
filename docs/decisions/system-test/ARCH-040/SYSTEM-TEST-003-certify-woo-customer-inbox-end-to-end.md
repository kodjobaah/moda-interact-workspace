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
  - ARCH-040-WOOCOMMERCE-001
  - ARCH-040-API-005
  - ARCH-040-BACKGROUND-002
  - ARCH-040-BACKGROUND-006
  - ARCH-040-BACKGROUND-007
  - ARCH-040-BACKGROUND-008
enables: []
created: 2026-10-14
updated: 2026-10-18
---

# ARCH-040-SYSTEM-TEST-003 — Certify Woo recovery-detail conversation and basket end-to-end

## Architecture

Initiative: `ARCH-040`. Architecture document: `docs/architecture/ARCH-040-merchant-customer-conversations-human-handover.md`. Coordinator: `moda_architect`. **Portable definition only; defined but not materialised, no branch/commit/worktree.**

## Objective

Certify the **existing Woo Recoveries -> Recovery Detail** basket + conversation + human handover experience, using only WordPress REST -> Woo hosted API -> Prisma/Background.

## Context

Woo ARCH-035 provides the recovery detail shell/read baseline. ARCH-040 enriches it with saved basket/control state and human reply controls; no new Conversations menu/list is part of scope. This WooCommerce certification is independently executable after the consolidated WooCommerce feature and shared Background corrections, regardless of Shopify or SYSTEM-TEST-001 status.

## Scope

- Woo WP-admin browser and LocalWP/WordPress REST end-to-end tests of existing recovery details plus basket/transcript/ownership.
- Customer service window/approved follow-up and shared credit identity tests across Woo human and CommerceAgent.

## Out of Scope

No new Woo inbox/menu, staff role/assignment, new conversation datastore or JS direct hosted API calls. No `_index.md` changes.

## Requirements

### WooCommerce moderation acceptance scenario

Within the existing Woo Recovery Detail and WP REST facade, verify pending/blocked/review/no-send feedback, flagged inbound retained but not sent to AI, permitted next message, WordPress nonce/capability and installation tenant isolation, and 20-locale status coverage. Use fake Moderation/Meta services. No Shopify dependency or new queue.

- Verify the combined WOOCOMMERCE-001 read and write feature: API-002 enriched recovery reads plus API-003/004 control/send/status through the existing WordPress REST and Recovery Detail components. No dependency on Shopify UI or server actions.

- Preserve two-stage WooCommerce > Moda Interact navigation. Choose recovery using existing list; verify the same detail screen shows basket snapshot, currency, quantity, variants, original conversation and milestones/related.
- Capture desktop + narrow-screen evidence per the desktop and narrow-screen ASCII in consolidated WOOCOMMERCE-001. Missing/partial basket and missing conversation must not break page.
- Verify 20 Woo admin locales/site fallback and keep conversation language untouched.
- Exercise `manage_woocommerce`/REST nonce, installation rotation/disconnect, cross-shop protection, command status and provider receipt reconciliation.
- Verify Take Over/Resume, open-window text, closed-window eligible template, sequence-2 uniqueness, single follow-up credit, and correct HUMAN control retention after inbound customer messages.

### Woo-only abuse-protection scenarios

- Exercise WordPress admin -> WP REST -> installation-authenticated hosted API with suspended shop: basket/transcript readable, Take Over and human composer/template disabled, forged direct HTTP commands rejected with typed `human_messaging_suspended`, Resume AI allowed. Verify prior queued command blocked by Background and safe error status transported by WordPress facade.
- Include WP nonce/capability and cross-installation spoof negatives; this certification does not depend on Shopify tasks/system tests.


### WooCommerce producer boundary certification

Verify WordPress uses only authenticated REST/hosted Woo API submission and status reads; it never calls Meta, PostgreSQL or BullMQ directly. The hosted API writes the same canonical persisted command/attempt contract as Shopify, and a single Background database poller consumes it. Cover reused/claimed sequence-2 attempts, closed/open windows, human-suspended shops and correct command-state feedback. Assert the existing 20-locale and Recovery Detail layouts remain intact; no Shopify implementation/system-test prerequisite.


### Service-window and configured follow-up certification (2026-10-20 policy)

- Verify only provider-verified CUSTOMER inbound since sequence-1 sent time opens/refreshes the rolling 24-hour free-text window; no outbound template, future, pre-initial or unverified record opens it. Exact `V+24h` is closed.
- Use the existing **effective configured follow-up due** (`sequence1.followUpDueAt`) and the one sequence-two slot for deliberate HUMAN templates after an expired or absent customer window. Test enabled/due 15-minute, 60-minute and 48-hour follow-ups; disabled/null/not-yet-due cases are denied. No `initialSentAt+24h` extra wait.
- Scheduled AUTOMATION no-response follow-up runs at the existing configured due only while unengaged; a customer reply suppresses automation even if that customer's service window subsequently expires. Expiry itself never creates a new scheduled job.
- Assert command acceptance and Background final permit make the same eligibility decision, with provider/credit never double-counted. No cross-platform implementation dependency and no second Conversation.

## Work Items

- [ ] Validate original Recoveries entry/detail basket/transcript responsive UX and 20 locales.
- [ ] Exercise secure WP proxy and connected hosted API reads/commands, negative auth/disconnect.
- [ ] Validate one-thread follow-up and receipt/credit invariants with provider and PostgreSQL evidence.

## Interfaces / Contracts

Woo WP-admin -> WordPress recovery detail REST -> existing Woo hosted recovery read endpoints enriched by API-002; API-003/004 for commands -> canonical Prisma/Background. No standalone inbox.

## Dependencies

- ARCH-040-WOOCOMMERCE-001
- ARCH-040-API-005
- ARCH-040-BACKGROUND-002
- ARCH-040-BACKGROUND-006
- ARCH-040-BACKGROUND-007
- ARCH-040-BACKGROUND-008

## Enables

None.

## Acceptance Criteria

- [ ] Woo recovery detail conveys moderation results safely and preserves its existing API and platform authentication boundaries.

- [ ] Woo Recoveries detail includes saved basket and real conversation, parity with Shopify without extra menu/navigation.
- [ ] Woo handover/window/follow-up/credit and idempotency match shared Background policy and no second Conversation.

## Validation

This terminal system-test task is separate from the developer-owned validation of the consolidated Woo implementation; results here do not gate implementation acceptance of WOOCOMMERCE-001.


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
