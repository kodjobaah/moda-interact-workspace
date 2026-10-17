---
id: ARCH-040-API-002
architecture_id: ARCH-040
title: Enrich Woo recovery detail with basket and conversation control
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
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
  - ARCH-035-API-013
enables:
  - ARCH-040-WOOCOMMERCE-001
created: 2026-10-14
updated: 2026-10-17
---

# ARCH-040-API-002 — Enrich Woo recovery detail with basket and conversation control

## Architecture

Initiative: `ARCH-040`. Architecture document: `docs/architecture/ARCH-040-merchant-customer-conversations-human-handover.md`. Coordinator: `moda_architect`. **Portable definition only; defined but not materialised, no branch/commit/worktree.**

## Objective

Extend **the existing WooCommerce Recovery Detail read API** with the checkout basket snapshot and AI/HUMAN conversation-control state. Reuse ARCH-035-API-013's recovery detail, messages and related endpoints; do **not** build another conversations inbox API.

## Context

`ARCH-035-API-013` defines authenticated `GET /v1/merchant/recoveries/:recoveryId`, `/messages` and `/related`, including their recovery-scoped cursors and Woo installation identity. The original ARCH-040-API-002 requested generic `/v1/merchant/conversations` list/detail/messages endpoints, which would duplicate the Recoveries experience and its transcript. Current `CheckoutRecovery.lineItems Json?`, `totalPrice`, `currency` provide saved basket state; conversation control comes from ARCH-040-DATABASE-001.

## Scope

- Enrich the **same** `GET /v1/merchant/recoveries/:recoveryId` output with bounded `basket` and `conversation` details needed by the Woo UI.
- Preserve ARCH-035's existing `/messages` and `/related` pagination, response headers/authentication and unrelated recovery fields. Extend detail OpenAPI and tests.
- Use existing Woo installation authenticator and tenant-safe recovery/read transaction; do not expose a new generic inbox list.

## Out of Scope

- No `/v1/merchant/conversations` **GET inbox/detail/message read endpoints** for ARCH-040. (Control/send/status command endpoints from API-003/004 remain scoped by conversation ID.)
- No new Shopify authentication, staff identity/permission table, extra conversation or separate credit counter.
- No live Woo cart lookup/price recalculation, WhatsApp provider call or Woo plugin UI work.
- No `_index.md` updates or historical migrations.

## Existing route and enriched detail contract

`GET /v1/merchant/recoveries/:recoveryId` (Woo installation authentication as ARCH-035) continues returning `schemaVersion: 1`, `timeZone`, `id`, recovery status, value and milestones, customer and `hasConversation`, plus:

```text
conversation: null | {
  id: string,
  controlMode: 'AI' | 'HUMAN',
  controlRevision: integer,
  lastInboundAt: ISO8601|null,
  windowExpiresAt: ISO8601|null,  // advisory, not send authorisation
  followUp: { sequence2Used: boolean, initiatedBy: 'HUMAN'|'AGENT'|'AUTOMATION'|null }
}
basket: {
  items: Array<{
    title: string|null, variantTitle: string|null,
    quantity: integer|null,
    unitPrice: {amount:string,currency:string}|null,
    lineTotal: {amount:string,currency:string}|null,
    imageUrl: string|null
  }>,
  recoveryTotal: {amount:string|null,currency:string|null},
  unavailableReason: string|null
}
```

Field naming can use established ARCH-035 DTO conventions **only if documented and consumed consistently**; do not invent values. `basket` is the saved checkout snapshot, not current inventory/order state. Source fields: `CheckoutRecovery.lineItems`, `totalPrice`, `currency`; inspect the real persisted lineItem JSON writer before mapping. Unknown/malformed entries are safely omitted or represented as unavailable without corrupting the rest of the recovery detail. Never infer item price by dividing the recovery total. Return only validated safe optional image URLs, not arbitrary HTML or raw checkout tokens.

Existing routes **unchanged in purpose/semantics**:

- `GET /v1/merchant/recoveries/:recoveryId/messages?cursor=...&window=latest|first` — paginated original ConversationMessage, with sender type and delivery receipts.
- `GET /v1/merchant/recoveries/:recoveryId/related?cursor=...` — paginated related recoveries.

`POST /v1/merchant/conversations/:conversationId/control`, `POST .../messages`, `GET .../send-commands/:commandId` remain API-003/004 write/status operations and can receive conversation ID from the enriched recovery detail.

## Requirements

- This is a **read-only** DTO extension. It does not depend on or implement API-003/004 or the merchant command/outbox schema. Keep the current ARCH-035 recovery-detail routes and message pagination unchanged. No generic Conversation listing routes.

1. Authenticate each recovery-detail call with existing `WooInstallationAuthenticator` and validate active installation, shop ownership and customer/conversation association in the same trusted read boundary. Recovery ownership via `CheckoutRecovery.shopId`, even with null `Conversation.shopId`; foreign and missing recovery return non-enumerating 404.
2. Project only safely validated lineItems snapshot fields and accurate decimal/currency amounts (strings; no float rounding). Bound number of rows, string/image lengths and serialized size; no unsafe URLs or raw payloads.
3. `conversation.id` remains the existing ID; no row created by GET. Include control revision/mode and advisory customer service-window metadata; no guarantee that subsequent POST will be allowed based solely on GET.
4. Preserve ARCH-035's `schemaVersion`, current recovery summary, pagination, errors and no-store/nosniff headers; no duplicate message reader or invented cursor protocol.
5. Handle null/no-conversation and empty basket distinctly, and deliver current recovery snapshot even if lineItems is invalid. No PII beyond existing authorized recovery detail output.

### Human-messaging restriction projection (DATABASE-001)

- When DATABASE-001 is available, include only `humanMessagingAllowed`/`humanMessagingStatus` in the existing Woo recovery-detail response. Default ACTIVE for a shop without a restriction row; do not expose private admin reason/audit notes.
- Rendering a suspended conversation or saved basket remains available. The response is presentation metadata, not a replacement for command authorization. Do not introduce a generic conversations inbox or a Shopify API endpoint.


### Read projection clarifications

The saved basket is only the `CheckoutRecovery.lineItems` snapshot; map fields actually stored by the Woo recovery writer and label `totalPrice` as the recorded recovery total, never imply live checkout prices or fabricate missing images/discounted line totals. Return the authoritative `controlRevision`, HUMAN restriction status (without admin notes), and *advisory* service-window expiry calculated from latest verified customer inbound; do not use `lastMessageAt` or an outbound template to open a window. Reading recovery details does not grant human-send eligibility; API-004 remains the authoritative command admission owner.


## Work Items

- [ ] Inspect stored lineItems shape and add sanitised basket projection to Woo recovery detail DTO.
- [ ] Add original conversation ID/mode/revision/advisory window/follow-up read projection.
- [ ] Reuse ARCH-035 detail route, update its OpenAPI response and tests without adding `/conversations` read routes.
- [ ] Add owned/foreign/no conversation, null/malformed basket, multi-item/quantity/variant, precision, mixed sender and service-window boundary tests.

## Interfaces / Contracts

`moda-interact-api` owns the extension of `ARCH-035-API-013` existing recovery detail **HTTP DTO**, not database schema. Woo PHP passes through existing authenticated recovery-detail route via WOOCOMMERCE-001; The combined WooCommerce-001 task uses it in the existing React Recovery Detail screen. Control/send paths remain API-003/004 on `conversationId`. No Shopify hosted API consumer.

## Dependencies

- ARCH-040-DATABASE-001
- ARCH-035-API-013

## Enables

- ARCH-040-WOOCOMMERCE-001

## Acceptance Criteria

- [ ] No new generic `/v1/merchant/conversations` GET list/detail/messages API; existing Woo Recovery Detail response contains checkout basket, original conversation ID/control mode/revision and same paginated history links.
- [ ] Valid snapshot/quantity/variant/amount fields render accurately; malformed/missing entries degrade without fabricating prices or breaking recovery detail.
- [ ] Existing Woo installation auth, tenant isolation and existing recovery-detail pagination/header/error contract remain intact.

## Validation

- [ ] Hosted API contract/OpenAPI tests of enriched `GET /recoveries/:id` and original `/messages`/`related` regressions.
- [ ] Disposable PostgreSQL owned/foreign/nullable shopId and precision/malformed basket/window test fixtures; stable page cursor checks.
- [ ] Typecheck/build/lint, `git diff --check` and isolated task worktree evidence.

## Implementation Notes

This extends the pending developer-owned `ARCH-035-API-013` boundary only **after that prerequisite is Complete**. Do not silently implement or modify its pending task/claim. No fresh API inbox is needed because the merchant navigates through Recoveries.

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
