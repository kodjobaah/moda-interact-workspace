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
  - ARCH-040-DATABASE-004

enables:
  - ARCH-040-SHOPIFY-002
created: 2026-10-14
updated: 2026-10-17
---

# ARCH-040-SHOPIFY-001 — Extend Shopify recovery-detail read data

## Architecture

Initiative: `ARCH-040`. Architecture document: `docs/architecture/ARCH-040-merchant-customer-conversations-human-handover.md`. Coordinator: `moda_architect`. **Portable definition only; defined but not materialised, no branch/commit/worktree.**

## Objective

Extend **only the existing Shopify Recovery Detail server-side read boundary** with saved checkout basket, existing conversation ownership/revision and platform human-messaging restriction projection. This read-only task must not implement Take Over, Resume AI or human-send actions; they belong to SHOPIFY-003. No new conversations inbox or route.

## Context

The verified Shopify app already routes `app/recoveries/:recoveryId` to `app/routes/app/recovery-detail/route.tsx`, with scoped readers in `app/services/recoveries/recovery-detail.server.ts`, paginated `/messages` and `/related` sections, and a read-only `RecoveryDetail.tsx`. `CheckoutRecovery` has `lineItems Json?`, `totalPrice Decimal?`, `currency String?`, and `checkoutUrl String?`; `readRecoveryDetail` currently does not project `lineItems`. The existing `Conversation` is reused and no separate hosted API is called by Shopify.

## Scope

- Extend recovery-detail shop-scoped reads: selected recovery summary, a **bounded sanitised basket snapshot**, the existing conversation ID/control mode and revision, 24-hour service-window advisory status, follow-up attempt summary, and existing paginated transcript.
- Keep the existing authenticated server-side recovery detail loader and its pagination; add only basket and control/restriction read projections. SHOPIFY-003 owns future control/send/status actions.
- Preserve existing recovery-list filters, back-navigation, embedded Shopify context, timezone/locale and message cursors.

## Out of Scope

- No write actions, merchant-send command insertion, follow-up claims, Background dispatch or provider calls in SHOPIFY-001. Those belong to SHOPIFY-003 and the common Background tasks.

- No `/app/conversations` route, new nav item, duplicate inbox, independent conversation store, additional checkout ingestion schema or live Shopify checkout fetch on every view.
- No provider dispatch or billing in loaders/actions; Background owns send/credit processing.
- No merchant staff account, permission matrix or new Shopify-to-Woo API bridge.
- No change to `_index.md` or unrelated architecture tasks.

## Requirements

- **Bounded read-only work:** return the existing recovery/conversation IDs, AI/HUMAN mode and revision, saved `CheckoutRecovery.lineItems` basket projection, recovery/sequence-2 status and permitted public suspension status. Avoid write-only DTO fields or assumptions that human sends are already available. Do not require DATABASE-002/003 or Background for this reader. Existing non-recovery Conversation types are outside ARCH-040.

### Read contract / source of truth

1. Each request authenticates using existing Shopify admin session and resolves the trusted shop server-side. Recovery ownership is checked via `CheckoutRecovery.shopId`; never authorise by client-provided shopId or nullable `Conversation.shopId` alone.
2. Extend **the existing recovery-detail loader DTO**, do not introduce a competing generic `ConversationInboxItem` endpoint. Keep existing message and related readers/pagination. Expose `conversation: { id, controlMode, controlRevision, lastInboundAt?, windowExpiresAt?, followUp: { used, initiatedBy? } } | null` and `basket: { items, currency, recoveryTotal, unavailableReason? }`. Keep field spelling compatible with the accepted database tasks and existing DTO conventions.
3. Read `CheckoutRecovery.lineItems` as a **snapshot**. Inspect the actual persisted checkout writer/JSON shape before mapping; validate the structure and project only supported fields such as name/title, variant, quantity, price amounts and safe thumbnail URL when genuinely available. Do not make assumptions about input keys or infer a unit/line price from an unreconciled total. Preserve decimal precision and currency; avoid checkout/cart tokens, personal details or unsafe URLs.
4. Empty/null/unsupported `lineItems` produces an explicit 'basket unavailable' or item-specific fallback, not fabricated products, placeholder prices or a hard failure of the rest of Recovery Detail. Distinguish snapshot total from currently live Shopify cart. Display totals only with defensible currency/amount evidence.
5. Allow a recovery with no conversation to display basket and recovery context without exposing takeover/send controls for a nonexistent conversation. Never create a conversation as a side-effect of reading the detail page.
6. Expose current `AI`/`HUMAN` state, revision, safe sender labels/receipts and advisory window status. Always re-evaluate eligibility in send admission rather than trusting stale client state.

### Platform restriction projection (read only)

- Read the shop's current DATABASE-004 human-messaging status; return only public ACTIVE/SUSPENDED availability, never private platform administrator notes.
- Recovery history, basket, mode and transcript remain readable while HUMAN messaging is suspended. SHOPIFY-003 will enforce suspension in server-side takeover/send transactions and allow Resume AI.
- Preserve Shopify shop-session authentication and tenant isolation for all reads, including nullable `Conversation.shopId` recovery records.

## Work Items

- [ ] Extend existing shop-authenticated recovery detail DTO with safe saved basket and control/restriction projections; retain paginated messages, milestones and related recovery data.
- [ ] Handle missing/malformed lineItems and null conversation without inventing products, prices, control mode or a new thread.
- [ ] Add loader/reader tests for nullable basket, variants, currency precision, cross-tenant records and suspended/readable state.

## Interfaces / Contracts

Consumer: existing Shopify `app/recoveries/:recoveryId` UI (SHOPIFY-002/003). Canonical read state: `CheckoutRecovery`, `Conversation`, `ConversationMessage`, existing `RecoveryOutreachAttempt` and shop-level human restriction in Prisma; `MerchantConversationSendCommand` is introduced and consumed by SHOPIFY-003, not this reader. Existing Shopify recovery-detail DTO and paginated message service are extended, **not replaced**. No Woo hosted API, `@modainteract/.../shared` conversation DTO, new shop authentication mechanism or direct Meta call.

## Dependencies

- ARCH-040-DATABASE-001
- ARCH-040-DATABASE-004

## Enables

- ARCH-040-SHOPIFY-002

## Acceptance Criteria

- [ ] Existing `/app/recoveries/:recoveryId` returns bounded saved basket, milestones and the same existing conversation ID; no extra inbox or thread is created.
- [ ] Missing/malformed basket data degrades safely; prices, quantities and currencies come only from persisted values.
- [ ] Shopify session and `CheckoutRecovery.shopId` prevent other-shop reads even with a nullable `Conversation.shopId`.
- [ ] HUMAN suspension still permits full recovery detail reads; no control mutation, command insert, provider send or credit operation is added by this task.

## Validation

- [ ] Existing recovery-detail reader/loader and shop-isolation tests plus saved-basket fixtures, no-conversation and ACTIVE/SUSPENDED read cases.
- [ ] Shopify route/reader typecheck, focused lint/build and `git diff --check`; record canonical task-worktree and dependency-sync evidence.

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
