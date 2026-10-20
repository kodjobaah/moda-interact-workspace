---
id: ARCH-040-API-005
architecture_id: ARCH-040
title: Align Woo merchant follow-up admission to configured recovery policy
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: in_progress
priority: 30
executor: developer
claimed_at: 2026-10-20T22:43:04Z
attempt: 1
depends_on:
  - ARCH-040-API-004
enables:
  - ARCH-040-WOOCOMMERCE-001
  - ARCH-040-SYSTEM-TEST-003
created: 2026-10-20
updated: 2026-10-20
---

# ARCH-040-API-005 — Woo configured follow-up eligibility correction

## Architecture

ARCH-040 parent: `docs/architecture/ARCH-040-merchant-customer-conversations-human-handover.md`. Owner `moda_api` / `moda-interact-api`. Portable task definition only; no branch/worktree/commit is claimed.

## Objective

Remove the independent hardcoded 24-hour delay from the accepted WooCommerce HUMAN follow-up template admission. Use **verified inbound only for the rolling free-text service window** and the **existing effective recovery follow-up setting and persisted due time** for post-window merchant template eligibility.

## Current source and defect

- `src/merchant/conversations/messages/eligibility.ts`: `latestVerifiedCustomerInbound()` and `windowOpen()` correctly define the verified 24-hour window. Retain these semantics. `merchantFollowUpWindowClosed(initialSentAt,inbound,now)` currently applies `now >= max(initialSentAt,inbound)+24h` even with no reply; this incorrectly introduces a fixed wait irrespective of Recovery Settings.
- `src/merchant/conversations/messages/admission.service.ts`: `MerchantConversationMessageAdmissionService.admit()` uses that helper for `RECOVERY_FOLLOW_UP_TEMPLATE` and atomically claims the one existing sequence-2 attempt.
- Prisma already includes `RecoveryOutreachAttempt.followUpDueAt` on sequence 1; the effective recovery policy is reflected in its persisted due time. Existing ShopSettings/ShopRecoveryPolicyOverride are the inputs to policy resolution, not a new independent timer.
- API-004 is Complete. **Do not reopen or rewrite that task file**. Implement this correction only in API-005.

## Scope

1. Keep the current Woo installation credentials, current shop/recovery isolation, idempotent replay before eligibility, HUMAN mode/revision, recipient/approved-template, suspension, entitlement and sequence-two lock/claim rules.
2. Continue selecting newest **provider-verified** CUSTOMER/INBOUND row between sequence-1 `sentAt` and one captured server `now`, ordered `(createdAt DESC,id DESC)`. No outbound, pre-initial, future or unverified row can open a window.
3. `HUMAN_TEXT`: allow only while the latest verified CUSTOMER inbound's `[at,at+24h)` window is open. At exact expiry deny.
4. `RECOVERY_FOLLOW_UP_TEMPLATE`: allow only when the window is **closed** (including no customer reply), the initial attempt was sent, the existing **configured** follow-up is enabled/scheduled/due as evidenced by `sequence1.followUpDueAt != null && followUpDueAt <= now`, and sequence 2 is unclaimed and otherwise eligible. **Remove `initialSentAt+24h` or `lastInboundAt+24h` as independent follow-up delay gates.** The latter is only a window-closed boundary.
5. If follow-up is disabled, absent or not yet due, deny with existing stable typed failure (`follow_up_unavailable` or an established equivalent); do not schedule a new job or compute a default due time. Respect frozen effective recovery-policy evidence rather than an ad hoc live setting read.
6. Preserve scheduled AUTOMATION no-response timing and engagement suppression, billing and command acceptance. Do not modify Shopify, Background or WP plugin in this task.
7. Add focused unit and PostgreSQL tests for verified/unverified and exact 24h boundaries, absent initial, absent/future due, enabled short and long configured delays, previously engaged customer, one sequence-two winner, idempotent replay and tenant isolation.

## Out of Scope

No new follow-up queue, schema, template catalogue, sender, credit or separate conversation. No recovery settings UI changes; no cross-repository implementation; no `_index.md` updates.

## Decision table

`S` = initial sent, `D` = effective persisted due (null if disabled/unscheduled), `V` = verified inbound.

| Scenario | HUMAN_TEXT | HUMAN template |
|---|---|---|
| `V` is within latest 24 hours | Eligible | Denied: window open |
| `V` expired, `D <= now` | Denied | Eligible if sequence 2 free |
| `V` expired, `D > now` or null | Denied | Denied |
| No `V`, `D <= now` | Denied | Eligible even if `now < S+24h` |
| No `V`, `D > now` or null | Denied | Denied |
| Missing unsent `S` or terminal recovery | Denied | Denied |

The existing approved Meta template requirement and all other policy gates apply to every eligible template row. A customer reply **does not schedule** a new follow-up; scheduled no-response jobs remain suppressed after engagement.

## Work Items

- [ ] Inspect actual Woo API-004 accepted source and sequence-1 due producer before editing.
- [ ] Replace the obsolete post-initial fixed waiting condition with a recovery-specific, persisted-due + closed-window predicate.
- [ ] Keep all current transaction locks and idempotency ordering; preserve the validated CUSTOMER inbound reader.
- [ ] Update contract/error tests for the decision table and prove one sequence-two claim.
- [ ] Report any missing effective due-time producer as a real dependency gap; do not invent a fallback delay.

## Interfaces / Contracts

Existing `POST /v1/merchant/conversations/{conversationId}/messages`; existing `HumanSendInput`, `SendHttpError`, `RecoveryOutreachAttempt` and Woo principal. No new HTTP route or Shared contract. API-002 owns the independent read projection; WooCommerce-001 consumes the already-authenticated API boundary.

## Dependencies

- ARCH-040-API-004 (Complete in supplied snapshot).

## Enables

- ARCH-040-WOOCOMMERCE-001.
- ARCH-040-SYSTEM-TEST-003.

## Acceptance Criteria

- [ ] Woo free text is eligible only from verified inbound within the latest rolling 24-hour customer window.
- [ ] Human follow-up template is limited by closed customer window and the existing **configured due time**; there is no mandatory fixed delay from initial recovery outreach.
- [ ] Disabled/missing/not-due configured follow-up cannot reserve sequence two, produce a command or consume credit.
- [ ] Existing Woo installation/tenant, ownership, approved template, idempotency, moderation and single-follow-up guarantees remain unchanged.
- [ ] No Shopify/Background files or new infrastructure are modified.

## Validation

- [ ] Focused API unit/contract and disposable PostgreSQL tests, typecheck/build, `git diff --check`; record actual results. Subsequent developer integration validation remains separate from the functional task acceptance contract.

## Implementation Notes

Do not repurpose `latestVerifiedCustomerInbound` as a follow-up timer. `followUpDueAt` is the recovery snapshot; validate how it is written by the existing recovery scheduling flow. Keep one captured `now` per admission transaction; provider sending and billing remain Background-owned.

## Stop Condition

After scoped implementation and functional acceptance criteria are complete, record the Completion Report, set status `review`, return to moda_architect and STOP.

## Completion Report

### Status

Not Started.

### Files Changed

None.

## Execution Ownership Amendment

Developer execution was explicitly requested for this task. The task remains
assigned to `moda_api`; execution ownership is changed from the automatic agent
path to the developer path for this attempt.

- Previous execution mode: `agent`
- Previous completion mode: `automatic`
- New execution mode: `developer`
- New completion mode: `developer`
- Amendment date: 2026-10-20

### Work Completed
None.

### Validation Results
Not run.

### Deviations
None.

### Assumptions
Effective follow-up due is persisted on initial `RecoveryOutreachAttempt`; actual producer must be verified before coding.

### Unresolved Issues
None about the agreed policy; report missing persisted evidence if found.

### Architectural Concerns
No other repository may be edited through this task.

## Architect Review

### Review Status
Pending.

### Review Notes
Defined; not implemented.

### Reviewed Files
Woo API eligibility/admission from 2026-10-20 snapshot.

### Validation Reviewed
Static source only.

### Architecture Conformance
Pending implementation.

### Follow-up
None.
