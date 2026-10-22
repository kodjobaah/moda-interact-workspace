---
id: ARCH-046-BACKGROUND-004
architecture_id: ARCH-046
title: Gate existing Woo recovery follow-ups by current customer consent
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: blocked
priority: 38
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-046-BACKGROUND-001
  - ARCH-046-BACKGROUND-002
  - ARCH-045-BACKGROUND-005
enables:
  - ARCH-046-SYSTEM-TEST-002
created: 2026-10-20
updated: 2026-10-22
---

# Gate existing Woo recovery follow-ups by current customer consent

## Architecture

Architecture ID: `ARCH-046`

Architecture document: `docs/architecture/ARCH-046-woocommerce-whatsapp-consent-gated-recovery.md`

Coordinator: `moda_architect`

**Lifecycle:** portable definition from 2026-10-20 snapshot; not materialised, claimed, committed, implemented or architect-accepted. Status means definition eligibility only.

**Execution gate:** This task is intentionally `blocked` pending a separately approved Woo recovery lifecycle/live checkout-state contract, and must **not** be claimed merely because its enumerated task dependencies become Complete.

## Objective

Once Woo recovery/follow-up execution is approved, reuse the shared Background current-consent policy and final outbound fence for **all Woo business-initiated proactive sends** (existing recovery follow-ups, post-window merchant templates and first-send reentries).

## Context

ARCH-035 provides capture only. The live Woo follow-up runtime is a separate prerequisite, so this task remains `blocked`. BACKGROUND-002 owns initial materialisation/pre-send admission; BACKGROUND-001 owns the exact-recipient, installation-aware current-state reader. This task owns the final pre-provider protection and billing/attempt compensation.

## Scope

- On approved Woo scheduled follow-up, merchant post-window recovery template and business-initiated first-send reentry paths, inject BACKGROUND-001's latest exact CustomerPhone decision/revision/no-contact snapshot and active installation check before billing/claim and the **final SQL send permit**.
- Reject revoked, unknown, wrong-number, same-shop ambiguous, customer STOP, merchant suppression, inactive installation or database unavailable **without provider dispatch**, committed credit or permanently consumed sequence-two attempt. Preserve existing compensation, unique follow-up slot and human/AI control semantics.
- Use a short DB fence to recheck the current exact recipient, consent revision, no-contact revision, installation status and existing attempt/entitlement guards. Do not invent Shopify HTTP preflights for Woo or add external/Redis calls under SQL locks.
- A legitimate customer-initiated in-window human reply retains its service-conversation classification, but the common final WhatsApp send permit **must deny it when an applicable `CUSTOMER_STOP` is active**. This rule applies to human/AI replies, delayed jobs and retries, not just marketing templates.
- Verify every Woo business-initiated abandoned-basket initial template, automated follow-up and merchant post-window recovery template is provider-approved in the **Marketing** category. An approved `checkout-recovery` purpose or catalogue `APPROVED` status alone does not prove provider category: confirm using trusted template metadata/approval before release, or report the owning contract gap; never send an unknown, Utility or Authentication template as basket-recovery marketing.
- Do not introduce a new recovery follow-up engine in this consent task, a new `WhatsAppRecipientReachability` consent schema or an evidence-triggered recovery poller.

## Out of Scope

- Woo checkout capture/engine construction, new recipient/session/customer tables, source epochs, erasure fence, consent-specific 72-hour window or marketing-template classification changes for ordinary service replies; STOP still blocks their delivery.

## Requirements

- [ ] Remain `blocked` until an approved Woo recovery **and** follow-up/send lifecycle exists.
- [ ] Both scheduled and merchant proactive follow-ups, plus initial reentries, fail closed on missing/withdrawn/unavailable local permission and installation invalidity.
- [ ] A cross-merchant standalone STOP written to this shop's CustomerPhone immediately suppresses Woo recovery marketing; a quoted STOP for another shop does not. Current consent and approved Marketing template are both required.
- [ ] A denial before dispatch does not spend recovery credit or sequence-two ownership; ordinary 24-hour service replies remain eligible only when no STOP blocks that shop/phone.

## Work Items

- [ ] After architecture unblocks the task, find the approved Woo proactive dispatch and initial reentry seams and inject BACKGROUND-001 policy.
- [ ] Implement current phone/installation revision recheck in the approved existing final outbound permit without network I/O under transaction locks.
- [ ] Test cross-path revoke/STOP, stale snapshot, installation disconnect and concurrent human/automation billing/attempt ownership.

## Interfaces / Contracts

Consumes ARCH-046-BACKGROUND-001, the approved ARCH-046-BACKGROUND-002 initial recovery contract, ARCH-045-BACKGROUND-005 CustomerPhone STOP, and existing shared Background outbound-fence/credit semantics. No separate Woo consent queue/schema, no Woo source-mode management and no additional recovery table.

## Dependencies

- `ARCH-046-BACKGROUND-001`
- `ARCH-046-BACKGROUND-002`
- `ARCH-045-BACKGROUND-005`

## Enables

- `ARCH-046-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] No Woo proactive template or first-send reentry reaches Meta after current consent withdrawal, local STOP/merchant suppression, recipient change, ambiguous identity, installation revocation or DB failure.
- [ ] Current consent, local no-contact and installation revision are checked at the final permit, without network I/O under SQL locks; credit/sequence-two compensation is preserved.
- [ ] Prior valid recovery history and legitimate in-window human replies remain usable; no consent-triggered recovery scheduler is added.
- [ ] Marketing-template category is demonstrated from provider-approved metadata (not inferred from `purpose` or status); wrong/unknown category produces zero Meta send, recovery credit or sequence-two claim.

## Validation

- [ ] **Only after live Woo recovery approval:** focused scheduled/manual proactive and first-reentry tests with current CustomerPhone revision, installation disconnect, recipient rotation, STOP, sequence-two claim race and compensated credit tests.
- [ ] Verify no network/Redis under SQL fence, no evidence poller, customer in-window HUMAN_TEXT regression and `git diff --check`.
- [ ] Template Marketing/Utility/unknown classification, cross-merchant standalone STOP, correct-merchant quoted STOP and no-template billing/attempt compensation tests.

## Stop Condition

After completing **only** the defined Work Items, Acceptance Criteria and required Validation, record launcher-resolved dedicated parent/implementation worktrees, their physical isolation and start-of-attempt synchronization evidence in the Completion Report. Change task to `review`, return control to `moda_architect`, and **STOP**. Do not start enabled tasks. A `blocked` task must remain blocked until the architect verifies and records the external missing recovery dependency and explicitly makes it Ready.

## Implementation Notes

This is a separate task because first outreach and scheduled/manual proactive follow-ups have distinct send/admission paths and failure modes.

Before any implementation, use `/moda-task` deterministic preparation against the **developer's actual** primary workspace, read the latest task/Architect Review, the parent architecture, relevant agent instructions, and the repository's real `package.json` scripts. Do not invent environment variables or claim a completed checkout/recovery source from the snapshot. Do not modify another repository, architecture-wide docs or `docs/decisions/**/_index.md` in a repository task. Use `@modainteract/moda-interact-shared/logging` for Node server diagnostics; PHP uses WordPress-specific safe diagnostics. Preserve official user/merchant i18n and tenant boundaries.

## Completion Report

### Status

Not Started — portable, not materialised.

### Files Changed

None — no runtime implementation in this documentation patch.

### Work Completed

None.

### Validation Results

Not run by a repository agent; no developer worktree/remote access is available from this snapshot.

### Deviations

None.

### Assumptions

Source is the supplied 2026-10-20 snapshot, not necessarily latest developer worktree. Versioned APIs/schema and future Woo recovery capability must be verified when eligible. Consent has no Moda-imposed waiting/expiry period. Recheck the current customer-phone permission and independently applicable checkout validity; do not invent a retention deadline.

### Unresolved Issues

External approved Woo recovery lifecycle/live checkout-state reader and independently accepted send/billing admission are currently missing; task remains Blocked.

### Architectural Concerns

None recorded beyond explicit context and gates.

## Architect Review

### Review Status

Pending — no implementation reviewed or accepted.

### Review Notes

None.

### Reviewed Files

None — portable definition only.

### Validation Reviewed

None.

### Architecture Conformance

Not assessed.

### Follow-up

None.
