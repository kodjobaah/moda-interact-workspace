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
enables:
  - ARCH-046-SYSTEM-TEST-002
created: 2026-10-20
updated: 2026-10-21
---

# Gate existing Woo recovery follow-ups by current customer consent

## Architecture

Architecture ID: `ARCH-046`

Architecture document: `docs/architecture/ARCH-046-woocommerce-whatsapp-consent-gated-recovery.md`

Coordinator: `moda_architect`

**Lifecycle:** portable definition from 2026-10-20 snapshot; not materialised, claimed, committed, implemented or architect-accepted. Status means definition eligibility only.

**Execution gate:** This task is intentionally `blocked` pending a separately approved Woo recovery lifecycle/live checkout-state contract, and must **not** be claimed merely because its enumerated task dependencies become Complete.

## Objective

Gate any **existing, previously authorised** Woo recovery's future proactive follow-up on the latest customer-phone consent and merchant source, without burning credit or attempt slots on denial.

## Context

The separate Woo recovery/follow-up engine does not exist in ARCH-035 capture-only. Initial no-consent checkouts now have **no CheckoutRecovery row**; this task applies only to an otherwise real prior authorised recovery. Status remains BLOCKED.

## Scope

- For any separately approved Woo existing-recovery scheduled or merchant post-window proactive WhatsApp template, use BACKGROUND-001 current CustomerPhone decision plus current WooInstallation source/epoch and exact immutable recipient before claim/billing and provider dispatch.
- Reject revoked/unknown/wrong phone, source switch and DB outage without sending or consuming a recovery credit/sequence-two slot; preserve existing compensation and control ownership rules.
- No polling immutable evidence and no consent-change background trigger. Normal in-window customer replies remain governed by existing Meta/human rules.

## Out of Scope

- No new follow-up engine, broad Shopify changes, consent 72-hour timer or new recovery waiting status.

## Requirements

- **Execution gate:** approved Woo recovery **and** proactive follow-up lifecycle must be architect-accepted first.
- No proactive send on revoked/unknown/unavailable current permission or changed source/phone; preserve valid 24h replies under applicable rules.

## Work Items

- [ ] Identify owner-approved Woo proactive send paths and wire injected Background-001 consent policy.
- [ ] Test revocation, source switch, changed recipient, concurrent human/automation slot ownership and compensation.

## Interfaces / Contracts

Consumes ARCH-046-BACKGROUND-001 current CustomerPhone/WooInstallation consent, BACKGROUND-002 approved recovery engine and existing proactive follow-up/credit contracts. No ARCH-046-BACKGROUND-003 or evidence worklist.

## Dependencies

- `ARCH-046-BACKGROUND-001`
- `ARCH-046-BACKGROUND-002`

## Enables

- `ARCH-046-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] Proactive templates fail closed after withdrawal or source invalidation without credit/sequence-two loss.
- [ ] Previously sent recovery history remains unchanged and in-window replies are not incorrectly blocked.

## Validation

- [ ] Focused approved Woo follow-up and billing/Meta race tests; repository-declared build and `git diff --check`.

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
