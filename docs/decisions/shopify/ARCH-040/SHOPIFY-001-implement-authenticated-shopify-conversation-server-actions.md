---
id: ARCH-040-SHOPIFY-001
architecture_id: ARCH-040
title: Extend Shopify recovery-detail server data and commands
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
  - ARCH-040-DATABASE-001
  - ARCH-040-DATABASE-002
  - ARCH-040-DATABASE-003
enables:
  - ARCH-040-SHOPIFY-002
  - ARCH-040-SHOPIFY-003
  - ARCH-040-SYSTEM-TEST-002
created: 2026-10-14
updated: 2026-10-15
---

# ARCH-040-SHOPIFY-001 — Extend Shopify recovery-detail server data and commands

## Architecture

Initiative: `ARCH-040`. Architecture document: `docs/architecture/ARCH-040-merchant-customer-conversations-human-handover.md`. Coordinator: `moda_architect`. **Portable definition only; defined but not materialised, no branch/commit/worktree.**

## Objective

Extend **the existing Shopify Recovery Detail server boundary** for checkout-basket and AI/HUMAN control data, and implement authenticated Take Over / Resume AI / human-send commands against canonical Prisma tables. Do not build a new conversations inbox or route.

## Context

The verified Shopify app already routes `app/recoveries/:recoveryId` to `app/routes/app/recovery-detail/route.tsx`, with scoped readers in `app/services/recoveries/recovery-detail.server.ts`, paginated `/messages` and `/related` sections, and a read-only `RecoveryDetail.tsx`. `CheckoutRecovery` has `lineItems Json?`, `totalPrice Decimal?`, `currency String?`, and `checkoutUrl String?`; `readRecoveryDetail` currently does not project `lineItems`. The existing `Conversation` is reused and no separate hosted API is called by Shopify.

## Scope

- Extend recovery-detail shop-scoped reads: selected recovery summary, a **bounded sanitised basket snapshot**, the existing conversation ID/control mode and revision, 24-hour service-window advisory status, follow-up attempt summary, and existing paginated transcript.
- Add small isolated session-authenticated server actions for takeover/resume, human message-command acceptance, and command-status reads from the Recovery Detail page. Keep read, control and send modules separate and tested.
- Preserve existing recovery-list filters, back-navigation, embedded Shopify context, timezone/locale and message cursors.

## Out of Scope

- No `/app/conversations` route, new nav item, duplicate inbox, independent conversation store, additional checkout ingestion schema or live Shopify checkout fetch on every view.
- No provider dispatch or billing in loaders/actions; Background owns send/credit processing.
- No merchant staff account, permission matrix or new Shopify-to-Woo API bridge.
- No change to `_index.md` or unrelated architecture tasks.

## Requirements

### Read contract / source of truth

1. Each request authenticates using existing Shopify admin session and resolves the trusted shop server-side. Recovery ownership is checked via `CheckoutRecovery.shopId`; never authorise by client-provided shopId or nullable `Conversation.shopId` alone.
2. Extend **the existing recovery-detail loader DTO**, do not introduce a competing generic `ConversationInboxItem` endpoint. Keep existing message and related readers/pagination. Expose `conversation: { id, controlMode, controlRevision, lastInboundAt?, windowExpiresAt?, followUp: { used, initiatedBy? } } | null` and `basket: { items, currency, recoveryTotal, unavailableReason? }`. Keep field spelling compatible with the accepted database tasks and existing DTO conventions.
3. Read `CheckoutRecovery.lineItems` as a **snapshot**. Inspect the actual persisted checkout writer/JSON shape before mapping; validate the structure and project only supported fields such as name/title, variant, quantity, price amounts and safe thumbnail URL when genuinely available. Do not make assumptions about input keys or infer a unit/line price from an unreconciled total. Preserve decimal precision and currency; avoid checkout/cart tokens, personal details or unsafe URLs.
4. Empty/null/unsupported `lineItems` produces an explicit 'basket unavailable' or item-specific fallback, not fabricated products, placeholder prices or a hard failure of the rest of Recovery Detail. Distinguish snapshot total from currently live Shopify cart. Display totals only with defensible currency/amount evidence.
5. Allow a recovery with no conversation to display basket and recovery context without exposing takeover/send controls for a nonexistent conversation. Never create a conversation as a side-effect of reading the detail page.
6. Expose current `AI`/`HUMAN` state, revision, safe sender labels/receipts and advisory window status. Always re-evaluate eligibility in send admission rather than trusting stale client state.

### Mutating boundary

7. Authenticated Take Over/Resume AI uses the existing `Conversation` controlRevision compare-and-set plus an audit event in one Prisma transaction. Do not dispatch or bill on mode change. Human takeover remains available at any time under the agreed eligibility rules.
8. Accept an immutable, shop-scoped `MerchantConversationSendCommand` only in `HUMAN` mode at the expected revision. Free-text only within the current customer-initiated 24-hour service window; after closure, use the one approved recovery sequence-2 template if still eligible. Retry/replay semantics and credit claim follow `DATABASE-002/003` and match Woo API behaviour.
9. Return accepted command ID/current status without claiming Meta send or receipt. Provide a bounded status read for the current recovery's command. All sends flow through Background.
10. Keep independent route/controller/service modules and existing error/i18n patterns; protect against rapid double clicks, spoofed Recovery IDs, absent conversations and stale revisions.

## Work Items

- [ ] Extend recovery detail reader/DTO for current control and **validated basket snapshot**; retain existing paginated transcript, milestones and related recoveries.
- [ ] Add session-authenticated takeover/resume server action with revision CAS/audit and safe failures.
- [ ] Add session-authenticated human send command admission/status with idempotency, template/follow-up claim and no provider send.
- [ ] Add model-shape, nullable basket, total/quantity/currency, shop isolation, replay/race and 24-hour-boundary tests.

## Interfaces / Contracts

Consumer: existing Shopify `app/recoveries/:recoveryId` UI (SHOPIFY-002/003). Canonical state: `CheckoutRecovery`, `Conversation`, `ConversationMessage`, `RecoveryOutreachAttempt`, `MerchantConversationSendCommand` in Prisma. Existing Shopify recovery-detail DTO and paginated message service are extended, **not replaced**. No Woo hosted API, `@modainteract/.../shared` conversation DTO, new shop authentication mechanism or direct Meta call.

## Dependencies

- ARCH-040-DATABASE-001
- ARCH-040-DATABASE-002
- ARCH-040-DATABASE-003

## Enables

- ARCH-040-SHOPIFY-002
- ARCH-040-SHOPIFY-003
- ARCH-040-SYSTEM-TEST-002

## Acceptance Criteria

- [ ] Existing `/app/recoveries/:recoveryId` reads a recovery's basket, milestones and **same existing conversation ID**; no new conversations route or separate inbox appears.
- [ ] A persisted, valid lineItems snapshot renders only grounded basket fields, and malformed/missing snapshots degrade gracefully.
- [ ] Authentication and tenant isolation hold for basket, messages, mode changes and send commands, even when `Conversation.shopId` is null.
- [ ] Takeover/resume/replay/race semantics and follow-up credit admission match Background and Woo; no provider send or bill happens in the Shopify request.

## Validation

- [ ] Existing recovery-detail reader/loader tests plus basket fixtures with variant, quantity, missing price/image, unknown shape, no conversation and foreign shop.
- [ ] Disposable PostgreSQL tests for revision CAS, idempotency, follow-up claim and command status.
- [ ] Existing Shopify component/route integration checks, lint/typecheck/build, `git diff --check` and canonical worktree evidence.

## Implementation Notes

Read the actual `recovery-snapshot-builder` and event writers before projecting JSON keys. Keep all customer/checkout links safe and avoid external Shopify round trips for a historical snapshot. No historical-data migration/backfill for this development-stage initiative.

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
