---
id: ARCH-053-API-003
architecture_id: ARCH-053
title: Resolve confirmed initial outreach offer in Woo restore response v1
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 50
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-052-SHARED-012
- ARCH-053-API-002
- ARCH-053-SHARED-002
- ARCH-053-BACKGROUND-004
enables:
- ARCH-053-WOOCOMMERCE-007
created: 2026-10-30
updated: 2026-11-01
---

# ARCH-053-API-003 — Resolve confirmed initial outreach offer in Woo restore response v1

## Architecture

`ARCH-053` — `docs/architecture/ARCH-053-woocommerce-checkout-recovery-links-and-cart-restoration.md`, coordinated by `moda_architect`. Defined but **not materialised**; no branch, worktree, commit, push or acceptance is claimed.

## Objective

Extend the existing **installation-authenticated, read-only** WooCommerce recovery-link resolver to return a verified, *confirmed outbound* checkout offer in a canonical v1 response. v1 is not implemented yet, so return the full offer-aware v1 response from its first implementation; do not introduce a compatibility version.

## Context

API-002 owns authorization and `POST /v1/woocommerce/recovery-restore/resolve` v1. SHARED-001 owns the required v1 outreach-offer union, and BACKGROUND-004 ensures the confirmed initial `ConversationMessage.content.recoveryPromise` includes `promotionTarget`. There is no separate offers table or need to call the dynamic-discovery agent during restoration. The codebase's `RecoveryOutreachAttempt` has unique `(checkoutRecoveryId, sequence)` and an `outboundMessageId` relation to `ConversationMessage`.

## Scope

Modify only these `moda-interact-api` paths, and related focused tests within `tests/unit/` / the existing integration-test location:

- **Create** `src/woocommerce/recovery-restore/offer-receipt.ts` — parse only a confirmed initial automated template receipt; return a typed internal result with no untrusted interpretations.
- **Create** `src/woocommerce/recovery-restore/offer-resolver.ts` — read existing Prisma attempt/message relations scoped to the already authorized shop and recovery and project into `WooRestoreOutreachOfferV1`.
- **Update** `src/woocommerce/recovery-restore/contract.ts` — import v1 schemas from the *published* `@modainteract/moda-interact-shared/woocommerce` export. Use the single published v1 resolver type.
- **Update** `src/woocommerce/recovery-restore/service.ts` — reuse all API-002 eligibility checks for v1; after authorization, load offer evidence and recheck eligible recovery identity/generation before returning the final v1 response.
- **Update** `src/woocommerce/recovery-restore/routes.ts` — same POST route and installation authenticator; one strict v1 body parser and existing 4 KiB request cap, no version switch or second endpoint.
- **Update** `src/composition/woocommerce.ts` only if required for dependency injection of offer reader; no new route prefix/Gateway rule.
- Add `tests/unit/woocommerce/recovery-restore/*` or existing equivalent dedicated tests and a Postgres-backed identity test.

## Out of Scope

No discount discovery, AI/CommerceAgent call, Woo provider API call, coupon creation/claim, WhatsApp send, mutable merchant setting lookup, external URL fetch, cart mutation, database schema change, new Redis enqueue or alternate visitor authentication path.

## Requirements

### Multi-discount v1 offer resolution — normative 30 October 2026

For a confirmed `promotionTarget:CHECKOUT` initial receipt with 2..3 source-grounded entries, import the published `InitialOutreachCheckoutOfferSetSchema` and `WooRestoreOutreachOfferV1Schema`, verify whole ordered group (not just its first code), match every trusted provider discount ID and emit `outreachOffer:{kind:"CHECKOUT_OFFERS",offers:[...]}` inside the **same** `woo.restore.resolve.v1` success payload. Preserve existing singleton branches. Malformed/incomplete/duplicate/unsupported group cannot be projected as a verified subset from the API: emit `NONE/UNVERIFIABLE` while keeping the originally restored basket eligible. Database/read outage remains 503. Never extract codes from message prose, coupon URL, current merchant selection or unsigned model text. Keep API read-only and no extra v2 route.


1. **Authenticate first:** `WooInstallationAuthenticator` supplies `shopId`. Do not accept shopId, checkoutKey, providerDiscountId, coupon code, message ID or recipient from request body. The plugin sends the same recoveryId/token pair defined in API-002. Exactly one request version `woo.restore.resolve.v1` is allowed; return its mandatory `outreachOffer` field, derived only from confirmed evidence. Reject `woo.restore.resolve.v2` and all unknown versions with 400; no compatibility adapter.
2. **Authorize recovery exactly as API-002:** installed active merchant, latest generation, eligible status, not terminal/completed/order-suppressed, 7-day freshness, stored HTTPS host/path and 32-byte token. Neither `outreachOffer` nor message evidence may override a denial. Uniform `404 {"error":"restore_unavailable"}` for authorization denial; `Cache-Control: no-store`, never reflect supplied token.
3. **Read the initial confirmed attempt only:** `where: {checkoutRecoveryId: authorizedRecovery.id, sequence: 1}`; verify `sentAt != null` and `outboundMessageId != null`, then matching `ConversationMessage` by ID with `direction: 'OUTBOUND'`, `senderType: 'AUTOMATION'`, `status in ('SENT','DELIVERED','READ')`, `providerMessageId != null`, `conversationId == recovery.conversation.id`, and immutable `content.contract === 'moda.whatsapp.automated-template-parameters.v1'`. Check the chain under authenticated shop; never search messages solely by coupon/provider ID, phone or text.
4. **Parse the explicit promise:** `NO_OFFER` → `{kind:'NONE',reason:'NO_CONFIRMED_OFFER'}`; positive CODE_OFFER + target CHECKOUT + valid bounded code/id → `{kind:'CHECKOUT_CODE',code,providerDiscountId}`; AUTOMATIC_OFFER + target CHECKOUT → `{kind:'CHECKOUT_AUTOMATIC',providerDiscountId}`; any positive `promotionTarget:'ALTERNATIVE_PRODUCT'` → `{kind:'ALTERNATIVE_PRODUCT'}` with **no code**; absent attempt → `NONE/NO_CONFIRMED_OFFER`. If a claimed/confirmed message exists but its content is corrupt, untagged, mismatched or ambiguous → `NONE/UNVERIFIABLE` plus bounded warning (never infer target). Exactly one result.
5. **Dependency outage is not `NONE`:** Prisma read/timeouts/unexpected errors log via Shared logger and fail with 503; never quietly drop offer when the resolver cannot determine eligibility. In contrast, malformed or unverified evidence does not permit a coupon but must **not** discard an otherwise valid original basket.
6. **No stale checkout:** generation/status/order check must be repeated when moving from authorized response to completing the v1 projection; an asynchronous return after authorization cannot be claimed atomic across WordPress and hosted Postgres. No API writes, queues, additional client credentials or arbitrary network calls.
7. **Never trust the offered price:** neither provider ID nor code is proof of current coupon applicability. The API reports **what the shop sent**, not the discount the customer will actually receive; Woo applies current native rules on customer-confirmed POST.

### Repository / execution safeguards

- Read `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, the launcher preparation packet and the parent ARCH-053 architecture before claiming. Work from dedicated, synchronized mirrored task worktrees; record both physical paths, initial SHAs and validation in the Completion Report. A snapshot does not establish the developer's current branch/status.
- Only change the **permitted owning-repository files** in Scope and this task's own authorised task metadata/Completion Report. No `_index.md`, no unrelated code, no other agent's task, no production WhatsApp activation, no merge/push to `main`.
- Node services use `@modainteract/moda-interact-shared/logging`. Log bounded identifiers and event codes, not raw URLs, bearer tokens, coupon codes, full customer data, original message text or unbounded provider bodies. Log and propagate unexpected dependency errors to the owner; never silently swallow them. PHP uses existing plugin-safe diagnostics, not a new generic logger.
- Keep checkout restoration read-only in the hosted API and cart-local in WooCommerce. Never have PHP query Moda PostgreSQL/Redis or an API handler change a visitor cart. Never create a new discount, extend an expired coupon, use ARCH-052 discovery code, bypass merchant consent/STOP/order/final provider gates or impose a cross-generation outreach cap.
- When the specified receipt/provider contract is absent, conflicting or untestable, **stop and return the gap to moda_architect**; do not invent an approximation, copy a Shared schema locally or broaden the task to another repo. System-test tasks are terminal and may not gate implementation tasks.


## Work Items

- [ ] Reuse the exact API-002 authorize/resolve operation under one v1 resolver endpoint; preserve all existing API-002 tests.
- [ ] Implement strict initial-confirmed outbound attempt/message receipt read; map to the exact Shared v1 union, with no text parsing or mutable discount lookup.
- [ ] Fail closed on absent/unverifiable offer evidence, with distinct provider-unknown vs DB-outage semantics and bounded logs.
- [ ] Add Postgres/route tests for tenant, generation, receipt and error cases; verify single-v1 strict contract validation.

## Interfaces / Contracts

**HTTP API (single canonical v1 request and response):**

```http
POST /v1/woocommerce/recovery-restore/resolve
Authorization: Bearer <installation-api-credential>
Content-Type: application/json
Cache-Control: no-store

{"schemaVersion":"woo.restore.resolve.v1",
 "recoveryId":"recovery_456",
 "token":"AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"}
```

The token is illustrative and never loggable. The v1 request is the **only** accepted resolver request; no v2 endpoint, dual-branch parser or historic compatibility promise exists.

**V1 successful response — full example (products and original vs recommended coupons separated):**

```json
{
  "schemaVersion": "woo.restore.resolve.v1",
  "status": "eligible",
  "recoveryId": "recovery_456",
  "checkoutKey": "woo-example-checkout",
  "snapshot": {
    "schemaVersion": "woo.cart-restore.v1",
    "kind": "supported",
    "appliedCouponCodes": ["SAVE10"],
    "lines": [
      {"productId": "101", "quantity": 2},
      {"productId": "202", "variationId": "207", "quantity": 1,
        "attributes": {"attribute_pa_color": "navy"}}
    ]
  },
  "outreachOffer": {
    "kind": "CHECKOUT_CODE",
    "code": "EXTRA15",
    "providerDiscountId": "woo-discount-915"
  }
}
```

**Internal implementation interface (keep code in API repo; no parallel Shared domain rules):**

```typescript
import type { WooRestoreOutreachOfferV1 } from
  '@modainteract/moda-interact-shared/woocommerce';

interface ConfirmedWooSentOfferReader {
  read(input: {
    shopId: string;
    recoveryId: string;
    conversationId: string | null;
  }): Promise<WooRestoreOutreachOfferV1>;
}
```

The reader is called **only after** successful API-002 authorization. Source query must be grounded in `RecoveryOutreachAttempt` and `ConversationMessage`, not synthesized from the abandoned basket's `appliedCouponCodes`, `offerSnapshot` or current merchant setting. Strict parser for receipt JSON lives in this API repo because it is a *local durable database/Meta evidence format*, distinct from the Shared wire response. No new HTTP exposed route.

**Denial/error table:**

| Condition | V1 outcome |
|---|---|
| Wrong shop / wrong token / superseded generation / order terminal / unsupported basket | `404 restore_unavailable`, no basket or offer |
| Valid recovery, no confirmed initial message | 200 with `outreachOffer: {kind:'NONE',reason:'NO_CONFIRMED_OFFER'}` |
| Confirmed checkout CODE_OFFER, explicit target | 200 `CHECKOUT_CODE` |
| Confirmed checkout AUTOMATIC_OFFER, explicit target | 200 `CHECKOUT_AUTOMATIC` |
| Confirmed alternative-product promotion | 200 `ALTERNATIVE_PRODUCT`; no code |
| Confirmed receipt corrupt / missing explicit target | 200 `{kind:'NONE',reason:'UNVERIFIABLE'}` + bounded warning |
| DB unavailable, pool timeout, unexpected read error | `503` (not 200 NONE) |
| Invalid body/version/extra request fields | `400` |

## Dependencies

- `ARCH-053-API-002` — accepted authenticated v1 recovery resolver.
- `ARCH-053-SHARED-002` — published and architect-accepted Shared v1 wire contracts.
- `ARCH-053-BACKGROUND-004` — confirmed initial sent receipt has explicit checkout/alternative target (or the completed BG004 evidence-only review proves the existing target).

## Enables

- `ARCH-053-WOOCOMMERCE-007` — authenticated Woo v1 client and safe coupon application.

## Acceptance Criteria

- [ ] The single v1 resolver remains strictly validated and now enriches mandatory `outreachOffer`; no v2 schema or route is introduced.
- [ ] Correct confirmed checkout code is returned **only** when outbound status, provider ID, attempt linkage, shop, recovery/generation and explicit target all match.
- [ ] Alternative-product offer and AUTOMATIC offer never leak a checkout code to be applied; NONE never removes existing original coupons.
- [ ] No sent evidence / unverified content / DB failure are distinct, covered by tests and diagnostic events without coupon codes.
- [ ] Cross-tenant and terminal/superseded recovery never exposes offer or basket; API remains read-only.
- [ ] No new offer storage, discovery, outbound or API credential exposure.

## Validation

- [ ] `npm test` targeted API route/offer parser tests and `npm run typecheck` (actual package scripts)
- [ ] Postgres-backed relation/tenant test with duplicate, failed, unconfirmed, current vs old generation receipts
- [ ] `npm run build` if changed source is in production compilation; `git diff --check`

## Stop Condition

When all defined Work Items, Acceptance Criteria and Validation are satisfied, update only this task's authorized metadata and Completion Report, set `status: review`, return to `moda_architect` and **STOP**. Do not begin Enabled tasks, self-accept, create new tasks, modify a sibling repository or merge/push main.

## Implementation Notes

The resolver should share one authorization implementation with v1: do not fork the security checks for v1. The admitted customer sees current Woo checkout totals, not a guaranteed discount from the initial WhatsApp message. Missing positive `promotionTarget` is a blocked proof, never `CHECKOUT` by default.

## Completion Report

### Status

Not Started — portable task definition, not claimed.

### Files Changed

None.

### Work Completed

Not Started.

### Validation Results

Not run. Report exact commands, results and any environment blockers after execution.

### Deviations

None.

### Assumptions

Defined from the 2026-10-30 uploaded snapshot. Re-read current task and repository HEAD after launcher preparation.

### Unresolved Issues

None claimed resolved. See explicit dependency/receipt gates above.

### Architectural Concerns

Escalate contract or ownership gaps instead of inventing a new transport or persistence location.

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

To be assessed after implementation.

### Follow-up

None.
