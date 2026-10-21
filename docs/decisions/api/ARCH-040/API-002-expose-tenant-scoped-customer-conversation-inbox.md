---
id: ARCH-040-API-002
architecture_id: ARCH-040
title: Enrich Woo recovery detail with basket and conversation control
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: review
priority: 40
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-040-DATABASE-001
  - ARCH-035-API-013
  - ARCH-040-DATABASE-005
enables:
  - ARCH-040-WOOCOMMERCE-001
created: 2026-10-14
updated: 2026-10-21
---

# ARCH-040-API-002 — Enrich Woo recovery detail with basket and conversation control

## Architecture

Initiative: `ARCH-040`. Architecture document: `docs/architecture/ARCH-040-merchant-customer-conversations-human-handover.md`. Coordinator: `moda_architect`. Materialised on the canonical parent and implementation worktrees for `task/ARCH-040-API-002`; developer execution is claimed for Attempt 1.

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

### Moderation read projection (DATABASE-005)

Extend the existing shop-scoped Recovery Detail read to project each message's `moderationStatus` (`PENDING`, `ALLOW`, `BLOCK`, `REVIEW_REQUIRED`, `RETRYABLE_ERROR`) and a stable safe `moderationReasonCode` from the most recent applicable assessment. For HUMAN commands expose these fields through existing command-status reads. Preserve `senderType` and the canonical transcript; do not delete flagged CUSTOMER messages or expose vendor scores, raw moderation categories, model request IDs or internal admin notes. Resolve shop through the authenticated Woo installation and `CheckoutRecovery.shopId`. Do not create another conversation or new inbox route.

- This is a **read-only** DTO extension. It does not depend on or implement API-003/004 or the merchant command/outbox schema. Keep the current ARCH-035 recovery-detail routes and message pagination unchanged. No generic Conversation listing routes.

1. Authenticate each recovery-detail call with existing `WooInstallationAuthenticator` and validate active installation, shop ownership and customer/conversation association in the same trusted read boundary. Recovery ownership via `CheckoutRecovery.shopId`, even with null `Conversation.shopId`; foreign and missing recovery return non-enumerating 404.
2. Project only safely validated lineItems snapshot fields and accurate decimal/currency amounts (strings; no float rounding). Bound number of rows, string/image lengths and serialized size; no unsafe URLs or raw payloads.
3. `conversation.id` remains the existing ID; no row created by GET. Include control revision/mode and advisory customer service-window metadata; no guarantee that subsequent POST will be allowed based solely on GET.
4. Preserve ARCH-035's `schemaVersion`, current recovery summary, pagination, errors and no-store/nosniff headers; no duplicate message reader or invented cursor protocol.
5. Handle null/no-conversation and empty basket distinctly, and deliver current recovery snapshot even if lineItems is invalid. No PII beyond existing authorized recovery detail output.

### Human-messaging restriction projection (DATABASE-001)

- When DATABASE-001 is available, include only `humanMessagingAllowed`/`humanMessagingStatus` in the existing Woo recovery-detail response. Default ACTIVE for a shop without a restriction row; do not expose private admin reason/audit notes.
- Rendering a suspended conversation or saved basket remains available. The response is presentation metadata, not a replacement for command authorization. Do not introduce a generic conversations inbox or a Shopify API endpoint.


### Configured follow-up read-side consistency

The original `lastInboundAt`/`windowExpiresAt` projection must use the newest provider-verified CUSTOMER/INBOUND row since initial sequence-1 `sentAt`, bounded by current time. If exposing a `followUp.eligible` or equivalent advisory flag, it must respect the recovery's effective persisted sequence-1 `followUpDueAt` (non-null and due), a closed verified customer window, and an available sequence-2 attempt—not a fixed delay from initial outreach. Keep this presentation-only: API-005 separately owns corrective POST admission and Background-008 final provider permit. API-002 remains independently executable once its own ARCH-035 and database prerequisites are satisfied; it **does not depend** on API-005 or Shopify.

### Read projection clarifications

The saved basket is only the `CheckoutRecovery.lineItems` snapshot; map fields actually stored by the Woo recovery writer and label `totalPrice` as the recorded recovery total, never imply live checkout prices or fabricate missing images/discounted line totals. Return the authoritative `controlRevision`, HUMAN restriction status (without admin notes), and *advisory* service-window expiry calculated from latest verified customer inbound; do not use `lastMessageAt` or an outbound template to open a window. Reading recovery details does not grant human-send eligibility; API-004 remains the authoritative command admission owner.


## Work Items

- [x] Inspect stored lineItems shape and add sanitised basket projection to Woo recovery detail DTO.
- [x] Add original conversation ID/mode/revision/advisory window/follow-up read projection.
- [x] Reuse ARCH-035 detail route, update its OpenAPI response and tests without adding `/conversations` read routes.
- [x] Add owned/foreign/no conversation, null/malformed basket, multi-item/quantity/variant, precision, mixed sender and service-window boundary tests.

## Interfaces / Contracts

`moda-interact-api` owns the extension of `ARCH-035-API-013` existing recovery detail **HTTP DTO**, not database schema. Woo PHP passes through existing authenticated recovery-detail route via WOOCOMMERCE-001; The combined WooCommerce-001 task uses it in the existing React Recovery Detail screen. Control/send paths remain API-003/004 on `conversationId`. No Shopify hosted API consumer.

## Dependencies

- ARCH-040-DATABASE-001
- ARCH-035-API-013


- ARCH-040-DATABASE-005
## Enables

- ARCH-040-WOOCOMMERCE-001

## Acceptance Criteria

- [x] The existing Woo recovery-detail read safely shows pending/blocked/review moderation state for the authenticated shop without leaking private scores or hiding the original transcript.

- [x] No new generic `/v1/merchant/conversations` GET list/detail/messages API; existing Woo Recovery Detail response contains checkout basket, original conversation ID/control mode/revision and same paginated history links.
- [x] Valid snapshot/quantity/variant/amount fields render accurately; malformed/missing entries degrade without fabricating prices or breaking recovery detail.
- [x] Existing Woo installation auth, tenant isolation and existing recovery-detail pagination/header/error contract remain intact.

## Validation

- [x] Hosted API contract/OpenAPI and detail/messages/related regression tests: focused unit suite passed **30/30** after dependency setup.
- [x] Disposable PostgreSQL owned/foreign/nullable shopId and basket/window/moderation tests: **3/3** suites passed after correcting the test fixture's `controlChangedAt`; 58 migrations applied and Prisma Client generated.
- [x] Typecheck, lint and build passed in the supplied validation log; `git diff --check` passed. The dedicated implementation worktree and remote `task/ARCH-040-API-002` commit are recorded below; the review authority can independently inspect launcher/synchronisation evidence.

## Implementation Notes

This extends the pending developer-owned `ARCH-035-API-013` boundary only **after that prerequisite is Complete**. Do not silently implement or modify its pending task/claim. No fresh API inbox is needed because the merchant navigates through Recoveries.

## Stop Condition

After only this task's Work Items, Acceptance Criteria and Validation are complete, set status `review`, record Completion Report and return to moda_architect. STOP.

## Execution Ownership Amendment

The developer invoked `/moda_developer_create ARCH-040-API-002` to take over this ready agent-owned task. The assigned domain owner remains `moda_api`.

- Previous execution mode: `agent`
- Previous completion mode: `automatic`
- New execution mode: `developer`
- New completion mode: `developer`
- Amendment date: 2026-10-21
- Attempt claimed: 1

## Completion Report

### Status
Ready for Review — developer Attempt 1 implemented and published on `task/ARCH-040-API-002` on 2026-10-21. Formal review and explicit developer completion remain pending.

### Files Changed

API implementation and contract:

- `openapi/merchant-conversation-human-send-v1.yaml`
- `openapi/merchant-recovery-detail-v1.yaml`
- `scripts/test-arch040-woo-human-send-postgres.mjs`
- `src/merchant/conversations/messages/contract.ts`
- `src/merchant/conversations/messages/status.service.ts`
- `src/merchant/conversations/moderation/read-projection.ts`
- `src/merchant/recoveries/detail/basket.ts`
- `src/merchant/recoveries/detail/contracts.ts`
- `src/merchant/recoveries/detail/conversation-projection.ts`
- `src/merchant/recoveries/detail/moderation.ts`
- `src/merchant/recoveries/detail/pages.ts`
- `src/merchant/recoveries/detail/read.service.ts`
- `src/merchant/recoveries/detail/validate-response.ts`

Focused verification:

- `tests/integration/merchant/recoveries/detail/enriched-detail.postgres.test.ts`
- `tests/unit/merchant/conversations/messages/contract.test.ts`
- `tests/unit/merchant/conversations/messages/openapi-contract.test.ts`
- `tests/unit/merchant/conversations/messages/routes.test.ts`
- `tests/unit/merchant/recoveries/detail/basket.test.ts`
- `tests/unit/merchant/recoveries/detail/conversation-projection.test.ts`
- `tests/unit/merchant/recoveries/detail/moderation.test.ts`
- `tests/unit/merchant/recoveries/detail/openapi-contract.test.ts`
- `tests/unit/merchant/recoveries/detail/pages.test.ts`
- `tests/unit/merchant/recoveries/detail/read.service.test.ts`
- `tests/unit/merchant/recoveries/detail/routes.test.ts`

This is the changed-file set in published implementation commit `81e7b1a85cbbc387c49b1409e59eb96a3b0f881a`.

### Work Completed

- Enriched the existing Woo-authenticated Recovery Detail DTO with bounded, sanitised saved basket items, exact decimal price strings, recorded recovery total and explicit unavailable values for absent fields. Did not invent line totals, images or live checkout pricing.
- Exposed the original conversation ID, AI/HUMAN control mode and revision, current HUMAN messaging restriction, sequence-two follow-up state, and advisory verified-inbound customer window.
- Added a safe current moderation projection for existing transcript pages and HUMAN command status without publishing private moderation details or changing message/related cursors.
- Reused the existing recovery detail, `/messages`, `/related` and command-status routes. No generic inbox route, additional database writes, migrations, billing or provider integrations were introduced.
- Added OpenAPI, unit, route and disposable PostgreSQL regression coverage, including shop ownership with nullable direct conversation shop ID, malformed basket data, moderation and customer-window boundaries.

### Validation Results

- Focused unit command: `node --import tsx --test tests/unit/merchant/recoveries/detail/*.test.ts tests/unit/merchant/conversations/messages/*.test.ts` — **30 passed, 0 failed**, after dependency setup.
- `npm run test:arch040-human-send:postgres` — **3 passed, 0 failed** on the final run (API-002 detail plus API-004 and API-005 admission suites). The disposable database applied **58 migrations** and generated Prisma Client **6.19.3**.
- Earlier API-002 PostgreSQL attempt failed the `Conversation_control_revision_check` during fixture creation. Corrected the test-only fixture by supplying `controlChangedAt` for `controlRevision: 7`; the next PostgreSQL run passed all three suites.
- `npm run typecheck`, `npm run lint`, and `npm run build` — passed in the supplied earlier validation log. These checks were not rerun after the one-line PostgreSQL fixture correction; the corrected PostgreSQL suite passed afterward.
- `git diff --check` — passed; final local `git status --short` and `git diff --submodule=short -- database` produced no output.
- The API task branch `task/ARCH-040-API-002` is published at **`81e7b1a85cbbc387c49b1409e59eb96a3b0f881a`** (`feat(api)`); its committed database gitlink is **`807af3393f992c8a19bc9ef278d7e7e05f41799d`**, matching the schema used during the successful database validation.
- The developer's terminal evidence shows the dedicated API task worktree. The canonical parent task worktree is recorded in task materialisation; launcher-resolved synchronisation evidence was not independently rerun in this review-preparation session.

### Deviations

None outside the agreed read-side scope. `lineTotal` and `imageUrl` remain null where the saved checkout writer does not persist them.

### Assumptions

- Recovery basket data is a historical persisted snapshot, not live WooCommerce data; decimal values are returned as strings.
- `windowExpiresAt` is presentation-only, not permission to send. Command admission remains authoritative elsewhere.

### Unresolved Issues

No known API-002 implementation defect remains based on the supplied tests. Architect review and explicit developer completion are still outstanding.

### Architectural Concerns

- No new generic conversation inbox, schema or cross-service contract was introduced.
- Task worktree and published commit evidence are supplied for review; the reviewing authority should verify launcher-resolved physical-isolation/synchronisation evidence against the canonical workflow record.

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
