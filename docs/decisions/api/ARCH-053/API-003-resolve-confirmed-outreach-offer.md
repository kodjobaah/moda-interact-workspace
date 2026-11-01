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
status: complete
priority: 50
executor: null
claimed_at: null
attempt: 2
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

- [x] Reuse the exact API-002 authorize/resolve operation under one v1 resolver endpoint; preserve all existing API-002 tests.
- [x] Implement strict initial-confirmed outbound attempt/message receipt read; map to the exact Shared v1 union, with no text parsing or mutable discount lookup.
- [x] Fail closed on absent/unverifiable offer evidence, with distinct provider-unknown vs DB-outage semantics and bounded logs.
- [x] Add Postgres/route tests for tenant, generation, receipt and error cases; verify single-v1 strict contract validation.

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

- [x] The single v1 resolver remains strictly validated and now enriches mandatory `outreachOffer`; no v2 schema or route is introduced.
- [x] Correct confirmed checkout code is returned **only** when outbound status, provider ID, attempt linkage, shop, recovery/generation and explicit target all match.
- [x] Alternative-product offer and AUTOMATIC offer never leak a checkout code to be applied; NONE never removes existing original coupons.
- [x] No sent evidence / unverified content / DB failure are distinct, covered by tests and diagnostic events without coupon codes.
- [x] Cross-tenant and terminal/superseded recovery never exposes offer or basket; API remains read-only.
- [x] No new offer storage, discovery, outbound or API credential exposure.

## Validation

- [x] Targeted API route/offer parser tests and `npm run typecheck` (actual package scripts)
- [x] Postgres-backed relation/tenant test with duplicate, failed, unconfirmed, current vs old generation receipts
- [x] `npm run build` and `git diff --check`

## Stop Condition

When all defined Work Items, Acceptance Criteria and Validation are satisfied, update only this task's authorized metadata and Completion Report, set `status: review`, return to `moda_architect` and **STOP**. Do not begin Enabled tasks, self-accept, create new tasks, modify a sibling repository or merge/push main.

## Implementation Notes

The resolver should share one authorization implementation with v1: do not fork the security checks for v1. The admitted customer sees current Woo checkout totals, not a guaranteed discount from the initial WhatsApp message. Missing positive `promotionTarget` is a blocked proof, never `CHECKOUT` by default.

## Completion Report

### Status

Ready for Review — the Architect Review correction is implemented and required focused validation passed. This is Attempt 2; no Architect acceptance is claimed.

### Files Changed

Implementation repository (`/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-053-API-003`, branch `task/ARCH-053-API-003`): cumulative task files are `src/composition/woocommerce.ts`; `src/woocommerce/recovery-restore/contract.ts`, `service.ts`, `offer-receipt.ts`, and `offer-resolver.ts`; `tests/integration/woocommerce/recovery-restore/service.postgres.test.ts`; and the `routes.test.ts`, `service.test.ts`, `offer-receipt.test.ts`, and `offer-resolver.test.ts` unit tests under `tests/unit/woocommerce/recovery-restore/`. Attempt 2 changed only `src/woocommerce/recovery-restore/offer-receipt.ts` and `tests/unit/woocommerce/recovery-restore/offer-receipt.test.ts`.

### Work Completed

Attempt 2 addresses the Architect Review finding. The BG004 writer in `moda-interact-background/src/services/recovery-template-integration/automated-recovery-template.service.ts` persists `ALTERNATIVE_PRODUCT_PROMOTION` with explicit `promotionTarget: "ALTERNATIVE_PRODUCT"`, `offerId`, `providerDiscountId`, `method`, `productId`, `variantId`, and `productTitle`; CODE additionally has `code`, while AUTOMATIC has no `code` field. The API parser now requires that exact key set and method-specific shape, validates the explicit target and nonblank evidence fields, and projects either method to Shared `{ kind: "ALTERNATIVE_PRODUCT" }` without returning the coupon code. Generic CODE/AUTOMATIC alternative-target promises and `CHECKOUT_DISCOUNT` tagged as alternative-product are now `NONE/UNVERIFIABLE`; malformed or ambiguous alternative receipts fail closed. Tests cover both production shapes, code non-leakage, malformed method fields, and the contradictory checkout-group regression.

The original API-003 implementation remains intact: it uses the published Shared schemas, reads only the confirmed sequence-one attempt/message relation scoped to the authorized shop/recovery/generation/conversation, reuses API-002 authorization and rechecks eligibility after the evidence read. No route, schema, Shared, Background, Woo/plugin, queue, provider-call, or write behavior was changed.

### Validation Results

Launcher Attempt 2 evidence: task claim commit `70670476eee0de394cf9e75d7b1c7c06d4c851f3`; parent task worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-053-API-003` synchronized at architect report commit `980884c8316b65f657c3f0e99299c44ab1717f68`; implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-053-API-003` started at `98d85c947bcb5670eaaa9367a186d282d201d3e1`; database submodule `7c377282aa5819b3008b7d7f3018f44f4161523e`. Launcher dependency gate passed for `ARCH-052-SHARED-012`, `ARCH-053-API-002`, `ARCH-053-SHARED-002`, and `ARCH-053-BACKGROUND-004`.

- `npx tsx --test tests/unit/woocommerce/recovery-restore/offer-receipt.test.ts`: passed, 5 tests.
- `npx tsx --test tests/unit/woocommerce/recovery-restore/*.test.ts`: passed, 21 tests across parser, resolver, service, and route.
- `npm run test:arch053-recovery-restore:postgres`: passed, 1 PostgreSQL-backed relation/generation test.
- `npm run typecheck`: passed.
- `npm run build`: passed.
- `npm exec -- eslint src/woocommerce/recovery-restore src/composition/woocommerce.ts tests/unit/woocommerce/recovery-restore tests/integration/woocommerce/recovery-restore --max-warnings=0`: passed.
- `git diff --check`: passed.
- Full `npm test` and repository-wide `npm run lint` were not rerun in Attempt 2. The prior report records 9 unrelated full-suite failures and the unrelated `no-empty` finding at `src/merchant/support/routes.ts:75`; this correction did not touch those paths.

Implementation commit: `a755724bba304dcc2b9c7f1bf390aa121b3c6558` (`fix(api): parse alternative-product recovery receipts`), pushed to `origin/task/ARCH-053-API-003`.

### Deviations

None to implementation scope. Full-suite and repository-wide lint findings were not rerun and remain outside the task-owned files.

### Assumptions

The prepared Shared package version `3.1.0` contains the required published v1 request/response and checkout-offer set schemas; the canonical database schema contains the required recovery, conversation, attempt and outbound-message relations. No cross-repository contract or schema work was required.

### Unresolved Issues

No task-scope implementation issue remains. The previously reported unrelated full-suite failures and full-lint finding remain for their respective owners; see Validation Results.

### Architectural Concerns

Escalate contract or ownership gaps instead of inventing a new transport or persistence location.

## Architect Review

### Review Status

Accepted

### Review Notes

Attempt 2 resolves the finding: `ALTERNATIVE_PRODUCT_PROMOTION` now accepts the exact production CODE and AUTOMATIC receipt shapes, requires the explicit `ALTERNATIVE_PRODUCT` target and method-specific fields, and projects to `ALTERNATIVE_PRODUCT` without exposing a code. Malformed or contradictory receipts, including `CHECKOUT_DISCOUNT` tagged as alternative-product, return `NONE/UNVERIFIABLE`. The regression tests exercise both writer shapes and the contradiction case. The production writer was inspected and matches the parser's required field sets.

### Reviewed Files

- `src/woocommerce/recovery-restore/offer-receipt.ts`
- `src/woocommerce/recovery-restore/offer-resolver.ts`
- `src/woocommerce/recovery-restore/service.ts`
- `src/woocommerce/recovery-restore/routes.ts`
- `src/composition/woocommerce.ts`
- `tests/unit/woocommerce/recovery-restore/offer-receipt.test.ts`
- `tests/unit/woocommerce/recovery-restore/offer-resolver.test.ts`
- `tests/unit/woocommerce/recovery-restore/service.test.ts`
- `tests/integration/woocommerce/recovery-restore/service.postgres.test.ts`

### Validation Reviewed

Reviewed Attempt 2's 21 focused restore tests, PostgreSQL-backed relation test, typecheck, build, focused lint, and diff check. The full test run and repository-wide lint were not rerun; the report preserves the previously identified unrelated failures and lint finding. No tests were rerun during this review.

### Architecture Conformance

Accepted. The correction now parses the confirmed alternative-product receipt variant emitted by BACKGROUND-004. The authenticated v1 resolver, generation recheck, checkout group handling, and fail-closed behavior conform based on the inspected code and submitted validation report.

### Follow-up

The Attempt 1 follow-up is resolved by the submitted Attempt 2 correction. The historical follow-up requested retaining Attempt 1, but the deterministic launcher claimed and recorded Attempt 2; acceptance preserves that recorded attempt number. `ARCH-053-WOOCOMMERCE-007` is now Ready because its other dependencies are Complete.
