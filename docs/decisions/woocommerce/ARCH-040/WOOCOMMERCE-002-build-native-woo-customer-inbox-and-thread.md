---
id: ARCH-040-WOOCOMMERCE-002
architecture_id: ARCH-040
title: Extend Woo Recovery Detail with basket and conversation
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
  - ARCH-040-WOOCOMMERCE-001
  - ARCH-035-WOOCOMMERCE-013
enables:
  - ARCH-040-WOOCOMMERCE-003
created: 2026-10-14
updated: 2026-10-15
---

# ARCH-040-WOOCOMMERCE-002 — Extend Woo Recovery Detail with basket and conversation

## Architecture

Initiative: `ARCH-040`. Architecture document: `docs/architecture/ARCH-040-merchant-customer-conversations-human-handover.md`. Coordinator: `moda_architect`. **Portable definition only; defined but not materialised, no branch/commit/worktree.**

## Objective

Extend the **existing WooCommerce Recoveries > Recovery Detail screen** to show the saved checkout basket beside the existing WhatsApp conversation and recovery context, mirroring Shopify SHOPIFY-002. Do not introduce a separate customer conversations inbox.

## Context

The inspected Woo plugin already has a modular recovery-detail shell under `src/recoveries/detail/`, including `context/checkout-context-panel.js`, a conversation presenter/controller and ARCH-035 staged read-only detail integration. `ARCH-035-WOOCOMMERCE-013` remains a prerequisite. ARCH-040-API-002 enriches the existing Woo recovery detail response (not a new generic conversations list), and WOOCOMMERCE-001 proxies that response via existing trusted WordPress REST.

## Scope

- Extend existing recovery detail client/controller/presentation and checkout-context panel for saved basket and read-only AI/HUMAN state, while retaining conversation transcript, related recoveries and milestones.
- Preserve both intentional WordPress nav registrations: entry via `WooCommerce > Moda Interact`, then active Moda Interact menus with `Recoveries` route. Do not add Conversations to the menu.
- Responsive and accessible basket + transcript layout with WP-native 20-locale admin translations.

## Out of Scope

- No new Woo inbox/menu, parallel chat history, separate account or staff permission, direct DB connection or new hosted API list route.
- No UI takeover or composer wiring until WOOCOMMERCE-003.
- No Woo live-cart refresh as the source for historical snapshots, guessed product price, or new `_index.md`.

## Required desktop and narrow-screen ASCII wireframes

```text
WooCommerce > Moda Interact > Recoveries > Sarah Jones
+------------------------------------------+----------------------------------+
| CUSTOMER CONVERSATION                    | CHECKOUT BASKET                  |
| [AI / HUMAN] (read only in this task)    | Saved checkout snapshot         |
|------------------------------------------| Product A / Variant / Qty 2      |
| Agent: Can I help with this checkout?    | Price (only if persisted)       |
| Customer: Please check delivery.         | Product B / Qty 1               |
| Merchant: Yes, let me check.             |                                  |
| [Previous] [Latest] [Refresh]            | Saved recovery total             |
|                                          +----------------------------------+
| Read-only; composer arrives in 003       | Recovery milestones/related      |
+------------------------------------------+----------------------------------+

NARROW SCREEN
+--------------------------------------+
| < Recoveries / Sarah Jones            |
| [Checkout basket v]                  |
| [Recovery context v]                 |
| Conversation    [AI / HUMAN]         |
| Agent / Customer / Human messages    |
| [Previous] [Latest] [Refresh]        |
+--------------------------------------+
```

Sample names/items are illustration, never fixtures in production.

## Requirements

1. Reuse existing `src/recoveries/detail/` modular components/controller/hooks and the ARCH-035 recovery detail route; no new page.js monolith or duplicate detail state store.
2. Consume basket snapshot **only** from existing recovery detail DTO enhanced by API-002 and WordPress REST facade, with safe item title/variant/quantity and optional real image/price. Label it as a snapshot; fall back gracefully on missing/malformed `lineItems`. Never imply live Woo product pricing.
3. Conversation is the primary larger column; basket above milestones/related on the right. Small screens collapse/stack basket and context above transcript; preserve message pagination and existing navigation/back behaviour.
4. Show CUSTOMER/AGENT/AUTOMATION/HUMAN, safe text/transcription/delivery receipts with one conversation ID for initial and follow-up. Show read-only control-mode label; action controls are introduced only by WOOCOMMERCE-003.
5. Preserve plugin disconnect and retry states, WordPress capability/nonce and credential boundary; twenty supported merchant-admin UI locales, WordPress native i18n and site fallback remain mandatory. Keep merchant UI language separate from store/conversation language.
6. No invented unread count or auto-scroll replacing the selected transcript. Focused refresh should not wipe basket or switch recoveries.

## Work Items

- [ ] Extend approved Woo recovery-detail DTO consumption and modular checkout basket component.
- [ ] Integrate mode label and mixed-author conversation with current recovery screen.
- [ ] Implement wide/narrow layout per ASCII without new menu or inbox.
- [ ] Add JS/PHP/read-facade fixtures and accessibility/i18n regression coverage.

## Interfaces / Contracts

Woo UI -> authenticated WordPress REST recovery detail -> existing Woo installation-authenticated `GET /v1/merchant/recoveries/:recoveryId` (augmented in API-002), and existing paginated `/messages`/`related`. No `/v1/merchant/conversations` inbox GET. Provider send and billing owned by Background; no browser secrets.

## Dependencies

- ARCH-040-WOOCOMMERCE-001
- ARCH-035-WOOCOMMERCE-013

## Enables

- ARCH-040-WOOCOMMERCE-003

## Acceptance Criteria

- [ ] Merchant selects recovery using existing Woo Recoveries and sees checkout basket, one conversation history and recovery context on its existing detail page.
- [ ] No new customer conversations navigation, new thread, fabricated price or duplicate Woo transcript.
- [ ] Empty/partial basket, no conversation, invalid/disconnected state, pagination and locale cases work.

## Validation

- [ ] Focused Woo component/controller/API-client and WordPress REST tests, desktop/mobile accessibility screenshots.
- [ ] All twenty locale strings verified; plugin JS/CSS/PHP build/lint and ZIP clean install checks.
- [ ] `git diff --check`, correct launcher worktree evidence.

## Implementation Notes

Extend `context/checkout-context-panel.js` instead of creating a new top-level app. Keep invoice/order details distinct from the saved checkout snapshot.

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
