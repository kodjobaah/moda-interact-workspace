---
id: ARCH-040-SHOPIFY-003
architecture_id: ARCH-040
title: Add takeover and human replies within Shopify Recovery Detail
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 40
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-040-SHOPIFY-002
  - ARCH-040-BACKGROUND-003
  - ARCH-040-BACKGROUND-004
  - ARCH-040-BACKGROUND-005

enables:
  - ARCH-040-SYSTEM-TEST-002
created: 2026-10-14
updated: 2026-10-16
---

# ARCH-040-SHOPIFY-003 — Add takeover and human replies within Shopify Recovery Detail

## Architecture

Initiative: `ARCH-040`. Architecture document: `docs/architecture/ARCH-040-merchant-customer-conversations-human-handover.md`. Coordinator: `moda_architect`. **Portable definition only; defined but not materialised, no branch/commit/worktree.**

## Objective

Add merchant Take Over, Resume AI, human text replies and the one eligible approved follow-up template **inside the existing Shopify Recovery Detail conversation panel**, as laid out in SHOPIFY-002. No new customer conversations page.

## Context

SHOPIFY-002 builds the single read-only recovery detail conversation/basket screen; SHOPIFY-001 exposes authenticated Prisma-backed mode/send actions; Background guards outbound ownership and credit. This task makes the controls usable from the same selected recovery without affecting the basket or transcript.

## Scope

- Human/AI ownership button and status in conversation header.
- Text composer for HUMAN mode within customer-initiated 24-hour service window.
- Approved recovery follow-up selector/status for HUMAN mode after closure (sequence-2 available only).
- Persisted command state/receipts, reconciliation feedback and safe UI concurrency control.

## Out of Scope

- No `/app/conversations` route, independent inbox, multiple follow-ups, arbitrary post-window messages, staff assignment or provider calls from browser.
- No AI suggestion mode, attachments or additional recovery pricing model.
- No changes to checkout-basket data, underlying WhatsApp provider rules or `_index.md`.

## Required AI / HUMAN / closed-window ASCII states

```text
AI in control (any service-window state)       HUMAN + open window
+----------------------------------------+    +--------------------------------------+
| Conversation  [AI]         [Take Over] |    | Conversation [HUMAN] [Resume AI]   |
| Agent/customer transcript ...          |    | Agent/customer/human messages ...   |
|----------------------------------------|    |--------------------------------------|
| CommerceAgent is managing replies.     |    | [Type your reply ..............]    |
| Take over to reply.                    |    |                             [Send]  |
+----------------------------------------+    +--------------------------------------+

HUMAN + closed window + follow-up available   HUMAN + closed + already used
+----------------------------------------+    +--------------------------------------+
| Conversation [HUMAN]       [Resume AI]  |    | Conversation [HUMAN] [Resume AI]    |
| 24-hour customer window closed.        |    | Window closed. Follow-up used.     |
| [Approved recovery template       v]  |    | Await customer message to resume    |
| One remaining follow-up; 1 credit      |    | permitted free-form replying.       |
|                  [Send Follow-up]      |    | (no composer / no send button)       |
+----------------------------------------+    +--------------------------------------+
```

## Requirements

1. `AI` mode: show enabled Take Over control to authenticated merchant when underlying conversation exists; human composer remains absent/disabled. Click submits `expectedControlRevision`, disables while pending and waits for authoritative result. Takeover must work regardless of whether customer window is open, although sending remains subject to WhatsApp/recovery policy.
2. `HUMAN` mode: show Resume AI and optionally the supported composer. Resume invalidates stale unsent drafts/commands at revision change; perform no client-only ownership toggle, automatic release on customer reply or mode inference from message sender.
3. Open window based on latest verified **customer inbound**: allow bounded free text; display advisory expiry, but only server+Background permit send. On expiry or conflict during composition, preserve draft locally for revision but prevent illegal send and explain state.
4. Closed window: free-text composer disabled; if recovery sequence-2 is genuinely available, display only the approved recovery template and `1 recovery conversation credit` notice. After used/not eligible, display a clear no-send state. Do not allow merchant to choose arbitrary Meta template identifiers or send additional proactive follow-ups.
5. Use stable idempotency key for a submission attempt; disable double click and reconcile duplicate successful POST responses with the same command. Do not show `SENT` until actual Background/provider evidence; show Accepted/Queued, Sent, Delivered, Read, Failed/unknown as grounded by returned state.
6. Handle `409` stale mode, used follow-up, window expiry, provider failure, network errors and command retry safely; reload authoritative mode before repeating an action. Never treat acceptance as delivery. Keep basket/context visible during failures.
7. When a provider dispatch predated takeover, say the already-dispatched message cannot be recalled; don't promise stopping an already-sent WhatsApp request.
8. Localise text using existing merchant language tooling; accessible input focus, aria-live send state, keyboard submission/disabled safeguards and safe state restoration after refresh.

### Suspended merchant state — ASCII UI

```text
+---------------------------------------------------------------+
| Customer / Recovery       [HUMAN]           [Resume AI]       |
| Conversation history / Checkout basket remain visible        |
+---------------------------------------------------------------+
| HUMAN MESSAGING UNAVAILABLE                                   |
| This store's human replies are currently disabled by Moda.   |
| [Reply composer disabled]                                     |
+---------------------------------------------------------------+
```

Show this server-derived status when SUSPENDED. Disable Take Over, composer and follow-up selection without hiding messages/basket; permit Resume AI. Surface worker-blocked/abuse-screened command outcomes without showing internal admin notes. Refresh status after server rejection, not merely on page load. Do not auto-resume AI.


## Work Items

- [ ] Add conversation header Take Over/Resume with revision-aware loading/error handling.
- [ ] Add Human-open free-text composer and server-backed window/eligibility refresh.
- [ ] Add Human-closed approved follow-up template selector/used state and credit disclosure.
- [ ] Add idempotent send command state reconciliation, receipt presentation, safe retry/double click protection and stale-conflict recovery.
- [ ] Add focused component+integration tests for every wireframe state and concurrency/error case.

- [ ] Render suspended state and moderation command outcomes on existing Recovery Detail; prevent restricted double-submissions.

## Interfaces / Contracts

Use only authenticated SHOPIFY-001 server-side recovery controls and send-command/status reads. Background owns final Meta submission and billing; one `Conversation.id`, one `RecoveryOutreachAttempt` sequence 2 and existing recovery credit identity. UI does not bypass server policy.

## Dependencies

- ARCH-040-SHOPIFY-002
- ARCH-040-BACKGROUND-003
- ARCH-040-BACKGROUND-004
- ARCH-040-BACKGROUND-005

## Enables

- ARCH-040-SYSTEM-TEST-002

## Acceptance Criteria

- [ ] Merchant can Take Over and Resume AI from existing Recovery Detail at any time without changing thread ID.
- [ ] Text/approved-template composer reflects server window and follow-up eligibility; zero illegal sends after closure or credit reuse.
- [ ] No double submission, stale revision overwrite, optimistic fake sent status or basket/timeline disappearance.
- [ ] AI sends are suppressed after committed takeover per Background ownership fence (apart from irretrievable in-flight provider requests).

- [ ] A suspended shop can read the conversation/basket and Resume AI, but cannot Take Over or send HUMAN messages.

## Validation

- [ ] Shopify human controls/component tests and authenticated action tests.
- [ ] Manual desktop/mobile embedded Recovery Detail scenarios with open/closed window and follow-up used.
- [ ] Typecheck/lint/build, `git diff --check` and task-worktree evidence.

## Implementation Notes

Keep controls, reply composer, follow-up selector and command-status hook separate from `RecoveryDetail.tsx` container. Reuse existing transcripts and basket from SHOPIFY-002. Do not introduce a giant route component.

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
