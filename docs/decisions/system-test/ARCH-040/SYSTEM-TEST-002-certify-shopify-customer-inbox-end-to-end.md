---
id: ARCH-040-SYSTEM-TEST-002
architecture_id: ARCH-040
title: Certify Shopify recovery-detail conversation and basket end-to-end
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
  - ARCH-040-SHOPIFY-001
  - ARCH-040-BACKGROUND-002
  - ARCH-040-BACKGROUND-006
  - ARCH-040-BACKGROUND-007
  - ARCH-040-SHOPIFY-004
  - ARCH-040-SHOPIFY-005
enables: []
created: 2026-10-14
updated: 2026-10-18
---

# ARCH-040-SYSTEM-TEST-002 — Certify Shopify recovery-detail conversation and basket end-to-end

## Architecture

Initiative: `ARCH-040`. Architecture document: `docs/architecture/ARCH-040-merchant-customer-conversations-human-handover.md`. Coordinator: `moda_architect`. **Portable definition only; defined but not materialised, no branch/commit/worktree.**

## Objective

Certify the **existing Shopify Recoveries -> Recovery Detail** human/AI conversation, persisted checkout basket and recovery context, without a new Conversations page.

## Context

Consolidated SHOPIFY-001 implements the current recovery-detail reader, page and human controls as one complete feature. Background and Prisma own the one-thread and follow-up invariants. The desktop/mobile ASCII layouts in consolidated SHOPIFY-001 are acceptance evidence. This Shopify certification is independently executable after consolidated Shopify-001 and the shared Background-002 prerequisite, regardless of Woo API, WooCommerce or shared-runtime SYSTEM-TEST-001 task status.

## Scope

- Browser E2E on the authenticated embedded Shopify recovery-detail route, including basket/related/milestones and existing transcript.
- Test mode control, open/closed customer window, human command lifecycle and one follow-up/credit race across AI/Human. Include unverified/pre-initial/future inbound records and exact 24-hour / no-reply merchant-template eligibility according to the approved ARCH-040 policy.

## Out of Scope

No new `/app/conversations` navigation/route, standalone inbox, staff assignment, provider secret or fake UI data. No `_index.md` changes.

## Requirements

### Shopify moderation acceptance scenario

Using the same existing Recovery Detail page and fake provider, show pending -> blocked/revise for flagged HUMAN command, persist and visually label flagged inbound while preventing AI execution, then demonstrate an allowed reply and normal provider status. Verify shop scoping, no extra credit and no new Conversations navigation. Do not depend on WooCommerce or its API.

- Verify consolidated SHOPIFY-001 delivers basket, transcript and authenticated human control/send actions together on that exact screen. No hosted Woo API/WordPress calls.

- Start from current `Recoveries` list, select an existing customer, and assert same `/app/recoveries/:id` renders accurate saved checkout items/quantities/variants/totals plus transcript, context and existing back-navigation.
- Test desktop two-column and mobile stacked basket/context layout against SHOPIFY-001 ASCII with snapshots/screenshots.
- Test no basket or invalid JSON fallback, no conversation, terminal recovery, pagination, mixed HUMAN/AGENT/AUTOMATION/CUSTOMER messages, safe links/receipts/audio placeholders.
- Exercise Take Over/Resume with revision conflicts and async provider race; open-window free text, closed-window approved template, follow-up used, duplicate clicks, sent/failed receipt and one credit.
- Verify cross-shop denied, one Conversation ID retained, no separate conversation UI/DB and no call to Woo-only hosted API.

### Shopify-only abuse-protection scenarios

- Exercise authenticated Shopify Recovery Detail with Admin-suspended shop: basket/transcript remain readable, Take Over and reply/template controls disable and server rejects forged requests, Resume AI is allowed. Verify accepted-before-suspended command is stopped by Background; safe typed error and recovery credit are correct.
- Verify independent Shopify actor never calls Woo hosted API and this certification does not depend on Woo tasks/system tests.


### Shopify producer boundary certification

Verify the Shopify action writes the canonical persisted command and does not enqueue a Shopify-specific BullMQ job or send WhatsApp directly. Exercise takeover, HUMAN message draft and idempotent submission in the existing recovery detail, then have the shared Background dispatcher process the command with the same status/credit semantics as a producer-neutral fixture. Assert `RECOVERY_HISTORY` is not treated as human-send entitlement, terminal recovery is read-only, and a provider permit admitted just before takeover is displayed honestly as not recallable. Preserve the task's existing ASCII screen/layout coverage and developer validation separation.


## Work Items

- [ ] Authenticate Shopify session and navigate existing Recoveries -> detail route; capture wide/narrow layout evidence.
- [ ] Validate real persisted basket projection, missing/unsupported items and transcript pagination/context.
- [ ] Validate control/send/race/window/follow-up/credit with provider mock and single Conversation identity.

## Interfaces / Contracts

Shopify app server loaders/actions backed by Prisma + Background command/Meta transport. Browser only uses existing Shopify authenticated routes; no separate conversations list or hosted Woo API.

## Dependencies

- ARCH-040-SHOPIFY-001
- ARCH-040-BACKGROUND-002


- ARCH-040-BACKGROUND-006
## Enables

None.

## Acceptance Criteria

- [ ] Shopify recovery detail visibly distinguishes moderation state from WhatsApp delivery, with blocked content never sent and no new inbox.

- [ ] Existing Recoveries UI, basket, transcript and context work on wide/narrow view without duplicate inbox.
- [ ] Human + AI share one thread and sequence-2 follow-up/credit with safe race behaviour.

## Validation

- [ ] Browser/system suite and screenshots of SHOPIFY-001 ASCII states.
- [ ] Disposable PostgreSQL/provider mock evidence, `git diff --check` and canonical worktree evidence.

## Implementation Notes

Manual UI verification can occur before system test execution; terminal system-test dependency direction remains intact.

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
