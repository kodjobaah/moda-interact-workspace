---
id: ARCH-040-SHOPIFY-002
architecture_id: ARCH-040
title: Extend Shopify Recovery Detail with basket and conversation
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: superseded
priority: 40
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables: []
created: 2026-10-14
updated: 2026-10-17
---

# ARCH-040-SHOPIFY-002 — Extend Shopify Recovery Detail with basket and conversation

## Architecture

Initiative: `ARCH-040`. Architecture document: `docs/architecture/ARCH-040-merchant-customer-conversations-human-handover.md`. Coordinator: `moda_architect`. **Portable definition only; defined but not materialised, no branch/commit/worktree.**

## Supersession decision — 17 October 2026

**SUPERSEDED. DO NOT EXECUTE.** All server, layout, basket, interaction, desktop/narrow ASCII, follow-up and suspension requirements are consolidated into active `ARCH-040-SHOPIFY-001`. The remaining contents below are historical specifications, not additional implementation or acceptance requirements. No separate read-only UI or interactive phase is required.

## Objective

Extend **the existing Shopify Recovery Detail page** into the human-and-AI conversation workspace, with the checkout basket visible alongside the **existing** transcript. Keep `Recoveries -> select recovery` navigation and URL; do not create a separate Conversations inbox.

## Context

`app/routes.ts` already declares `app/recoveries/:recoveryId`, whose `RecoveryDetail.tsx` shows customer header, value/status, paginated read-only WhatsApp transcript, milestones and related recoveries. The original task wrongly requested a new inbox/list/search interface. SHOPIFY-001 extends the existing recovery-detail data with the persisted basket snapshot and control state. SHOPIFY-003 later adds the interactive controls to this page.

## Scope

- Extend current `RecoveryDetail.tsx` and its modular children: main **conversation** column, right **checkout basket** followed by recovery context/timeline, and responsive stacked layout.
- Preserve existing back-to-Recoveries link (filters, scroll restoration and Shopify embed context), message pagination/refresh, author/receipt labels, safe HTTP linkification, audio transcription and related recoveries.
- Add read-only UI for basket and AI/HUMAN status; do not enable live human sending until SHOPIFY-003.

## Out of Scope

- No `/app/conversations` or extra `Conversations` nav, independent search/filter inbox, duplicated transcript or separate chat datastore.
- No fabricated unread counts, product images, discounts, taxes, shipping, price breakdowns or checkout URL when not in persisted data.
- No takeover/send action in this task (SHOPIFY-003 owns interactions).
- No changes to `docs/decisions/**/_index.md`.

## Required desktop ASCII wireframe (canonical layout)

```text
+-------------------------------------------------------------------------------+
| < Back to Recoveries                                                         |
| Customer: Sarah Jones          Recovery: ENGAGED        Saved value: GBP 124.99 |
+----------------------------------------------+--------------------------------+
| CUSTOMER CONVERSATION                        | CHECKOUT BASKET                |
| AI in control                [Take Over]*     | Basket snapshot (at recovery) |
| Window: open until <customer inbound +24h>    |                                |
|----------------------------------------------| Product A  Blue / Large        |
| CommerceAgent                        10:20    | Qty 2             GBP 59.98   |
|  [Can I help you with your checkout?]         | Product B  Black               |
|                                              | Qty 1             GBP 65.01   |
| Customer                             10:25    |--------------------------------|
|  [Can you help with delivery?]                | Saved recovery total GBP124.99|
|                                              +--------------------------------+
| Merchant                             10:28    | RECOVERY CONTEXT               |
|                        [Yes, let me check.]   | Status / milestones            |
|                                              | Initial / follow-up state      |
| [Previous] [Latest] [Next] [Refresh]          | Related recoveries             |
|----------------------------------------------|                                |
| Read-only transcript (composer in 003)        |                                |
+----------------------------------------------+--------------------------------+
* Take Over is a visual placeholder in SHOPIFY-002; wired in SHOPIFY-003.
```

Example names/items/totals are illustrative only: **never hardcode sample customer or product data**.

## Required narrow-screen ASCII wireframe

```text
+--------------------------------------+
| < Recoveries       Sarah Jones       |
| Recovery: ENGAGED     GBP 124.99     |
|--------------------------------------|
| [Checkout basket v]                  |
|  Product A  Qty 2 ...                 |
|  Saved recovery total ...            |
|--------------------------------------|
| [Recovery context v]                 |
|--------------------------------------|
| Conversation       [AI / HUMAN]      |
| [Take Over]*                         |
|                                      |
| CommerceAgent: Can I help?           |
| Customer: Can you help?              |
| Merchant: Yes, of course.            |
|                                      |
| [Previous] [Latest] [Refresh]        |
| Read-only until SHOPIFY-003          |
+--------------------------------------+
```

## Requirements

1. **Reuse the current route and message component**; split basket display, conversation header/transcript, and recovery context into modular components/hooks instead of growing a 400+ line `RecoveryDetail.tsx` further. Respect existing merchant UI localization and CSS naming conventions.
2. Conversation is primary: at normal desktop widths it takes the larger column; right column shows checkout basket at the top, and milestones/related recoveries below. If either data set is missing, the other areas remain usable.
3. Render `CheckoutRecovery.lineItems` via SHOPIFY-001's sanitised DTO: title, variant, quantity, persisted unit/line amount, safe image only when present; formatted currency and clearly labelled **snapshot** total. Handle empty, malformed or missing item fields independently. Never substitute current Shopify product price.
4. Retain existing sender attribution CUSTOMER/AGENT/AUTOMATION/HUMAN, safe linkification, transcription and actual provider delivery statuses; initial outreach and follow-up stay in one message history. No secondary transcript hidden elsewhere.
5. Display `AI` or `HUMAN` control state and recovery/follow-up status as read-only labels. This task may reserve space for control/composer, but sends/mode actions remain inert/absent until SHOPIFY-003; no fake clickable buttons.
6. On narrow screens stack/collapse the basket and recovery context **above** the conversation; preserve accessible transcript and touch-friendly pagination. The future composer must remain reachable without forcing horizontal scrolling.
7. Keep message pagination explicit; loading, no conversation, missing basket, malformed basket, empty history, errored section and terminal recovery states get distinct honest copy. Do not introduce a fabricated unread counter or auto-scroll while merchant reads history.
8. Preserve back link's recovery filters and Shopify embedded navigation. Refresh only the relevant sections, discard stale responses on recovery changes, avoid list reordering and unwanted auto-refresh interruption.

## Work Items

- [ ] Extract/reuse presentational pieces from the existing Recovery Detail page; keep existing transcript renderer and pagination functionality.
- [ ] Add checkout basket and currency/quantity rendering with accessible empty/partial states.
- [ ] Add AI/HUMAN and follow-up read-only indicators in conversation header; preserve milestones/related.
- [ ] Implement desktop/touch/narrow-screen layout matching ASCII and localization.
- [ ] Add component tests for real/missing/malformed basket, sender types, navigation, responsive states and section retry/pagination.

## Interfaces / Contracts

Consume **SHOPIFY-001's extended recovery-detail loader**, existing recovery messages/related fetchers, and canonical Prisma-backed data on the server. Do not call `moda-interact-api` or expose browser DB credentials. Subsequent SHOPIFY-003 attaches interactive ownership/reply components to the same screen.

## Dependencies

None. Historical prerequisites no longer apply.

## Enables

None. This task no longer enables another task.

## Acceptance Criteria

- [ ] No new Conversations navigation, inbox route or duplicate transcript. `Recoveries -> customer` opens the upgraded existing Recovery Detail.
- [ ] Desktop and mobile conform to embedded ASCII layout: conversation + basket + recovery context, with safe fallbacks.
- [ ] Transcript pagination, safe links, audio, receipts, related recoveries and recovery list back-navigation are not regressed.
- [ ] Message history is truly read-only during SHOPIFY-002 and shows real AI/HUMAN state; no simulated send success.

## Validation

- [ ] Focused RecoveryDetail component/responsive/accessibility/i18n tests.
- [ ] Screenshots/manual checks at wide and narrow embedded Shopify Admin widths against the wireframes.
- [ ] Recovery detail pagination/navigation regression tests, build/lint/typecheck and `git diff --check` with isolated task worktree evidence.

## Implementation Notes

This is a **modification of existing Recoveries UX**, not a new application section. Do not block on Woo API. Present only basket facts supported by the persisted JSON and avoid mutating historical recovery snapshots.

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
