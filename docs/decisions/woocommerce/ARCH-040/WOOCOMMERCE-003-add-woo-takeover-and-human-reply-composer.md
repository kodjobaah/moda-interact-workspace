---
id: ARCH-040-WOOCOMMERCE-003
architecture_id: ARCH-040
title: Add takeover and replies within Woo Recovery Detail
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 40
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-040-WOOCOMMERCE-002
  - ARCH-040-BACKGROUND-003
  - ARCH-040-BACKGROUND-004
  - ARCH-040-BACKGROUND-005

enables:
  - ARCH-040-SYSTEM-TEST-003
created: 2026-10-14
updated: 2026-10-16
---

# ARCH-040-WOOCOMMERCE-003 — Add takeover and replies within Woo Recovery Detail

## Architecture

Initiative: `ARCH-040`. Architecture document: `docs/architecture/ARCH-040-merchant-customer-conversations-human-handover.md`. Coordinator: `moda_architect`. **Portable definition only; defined but not materialised, no branch/commit/worktree.**

## Objective

Add merchant Take Over / Resume AI, free-text replies during the open customer window, and one permitted recovery follow-up template on the **existing Woo Recovery Detail conversation panel** from WOOCOMMERCE-002.

## Context

Existing Woo navigation and the ARCH-035 recovery-detail shell remain the only entry point. WordPress REST proxies ARCH-040-API-003/004 commands, while Background owns actual Meta send. The checkout basket remains visible while merchants talk to customers.

## Scope

- Add revision-aware takeover/resume control, human composer and approved recovery-template selector to the existing Woo detail conversation component.
- Add actual command-status/receipt reconciliation, safe disabled/pending/failed states, WordPress native localisation and responsive layout.

## Out of Scope

- No new Conversations menu/route, new chat history, user accounts/roles, staff assignment, browser provider credentials, live chat service or AI suggestions.
- No second follow-up allowance or additional credit path; no `_index.md` changes.

## Required interaction ASCII

```text
+-------------------------------------------------------------+
| Recovery Detail / Customer         [HUMAN]  [Resume AI]     |
| Conversation transcript...                                 |
|-------------------------------------------------------------|
| 24-hour window OPEN:  [Write a reply...........]    [Send] |
+-------------------------------------------------------------+

If window CLOSED and sequence-2 still available:
+-------------------------------------------------------------+
| Free text is unavailable.                                 |
| [Approved recovery follow-up template  v] [Send Follow-up] |
| Notice: uses one recovery conversation credit.              |
+-------------------------------------------------------------+

If follow-up used: 'Window closed; follow-up already used.'
AI mode instead displays [Take Over] and no human composer.
```

## Requirements

1. Keep UI controls inside selected `Recoveries > Recovery Detail`; Take Over offered whenever valid conversation exists, regardless of 24-hour window. When control is `AI`, no human send permitted; `HUMAN` retains ownership until explicit Resume AI, even after new customer inbound.
2. Use existing WordPress authenticated REST facade, preserving `expectedControlRevision`, stable idempotency key and validated server errors; never call hosted API or Meta directly from JS.
3. Customer's latest inbound defines advisory window display. Only open-window free text; after closure only eligible approved sequence-2 template; if used/unavailable, composer disabled with an explanation.
4. During submit, disable duplicate button; show Accepted/Queued vs actual Sent/Delivered/Read/Failed status and safe retry/replay. Handle stale revision, mode conflicts, provider failure, disconnect and credential rotation without losing basket context.
5. No automatic AI mode change on inbound. Apply staff-free shop-level identity; standard WP `manage_woocommerce` capability and REST nonce only. Preserve 20 WordPress Admin locales with fallback and accessibility.
6. Reuse Woo recovery detail hooks/controller and split small control/composer modules; no monolithic `page.js`.

### Suspended merchant state — ASCII UI

```text
+---------------------------------------------------------------+
| Customer / Recovery       [HUMAN]          [Resume AI]        |
| Conversation history / Checkout basket remain visible        |
+---------------------------------------------------------------+
| HUMAN MESSAGING UNAVAILABLE                                   |
| This store's human replies are currently disabled by Moda.   |
| [Reply composer disabled]                                     |
+---------------------------------------------------------------+
```

No new WordPress role: use existing WP-admin capability/nonce and hosted restriction response. Disable Take Over, free-text and follow-up template submission while suspended; allow explicit Resume AI, readable transcript and checkout. Render typed safe errors for queued-command refusal and rate/content screening. Localise all new messages using existing 20-locale policy.


## Work Items

- [ ] Add takeover/resume stateful control on current Woo recovery detail.
- [ ] Add open-window human composer and closed-window approved template selector.
- [ ] Integrate command-status polling/receipts, idempotency, stale-state correction and disabled buttons.
- [ ] Add 20-locale, capability/nonce, disconnect/race, credit/follow-up and responsive tests.

- [ ] Render localised suspended state on existing Woo Recovery Detail, preserving basket/transcript and Resume AI.

## Interfaces / Contracts

WordPress REST facade (WOOCOMMERCE-001) to existing Woo-only hosted commands `POST /v1/merchant/conversations/{conversationId}/control`, `POST /v1/merchant/conversations/{conversationId}/messages`, and `GET /v1/merchant/conversations/{conversationId}/send-commands/{commandId}`. Read conversation ID and revision from the **recovery detail** DTO, not a new inbox list. Same durable Prisma/Background runtime as Shopify.

## Dependencies

- ARCH-040-WOOCOMMERCE-002
- ARCH-040-BACKGROUND-003
- ARCH-040-BACKGROUND-004
- ARCH-040-BACKGROUND-005

## Enables

- ARCH-040-SYSTEM-TEST-003

## Acceptance Criteria

- [ ] Woo merchant can interact with the existing conversation from Recoveries; basket remains visible and no new thread exists.
- [ ] One follow-up/credit across human/AI; closed-window text blocked, and new inbound does not auto-release HUMAN control.
- [ ] No fake delivery state, double clicks, duplicate sends or secret/tenant leaks; all 20 locales and narrow screen work.

- [ ] The Woo UI cannot send as HUMAN while suspended and does not present restriction state as a merchant preference.

## Validation

- [ ] Woo JS/controller and authenticated WordPress REST tests, LocalWP end-to-end with provider mock.
- [ ] All 20 admin-language strings, plugin build/ZIP checks, `git diff --check` and task worktree evidence.

## Implementation Notes

Keep basket and recovery timeline visible during sends. Reuse approved Woo admin navigation and ARCH-035 recovery-detail component structure.

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
