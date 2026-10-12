---
id: ARCH-027-API-006
architecture_id: ARCH-027
title: Expose WooCommerce purchase history and refund navigation
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 65
executor: null
claimed_at: null
attempt: 2
depends_on:
  - ARCH-027-BACKGROUND-005
enables:
  - ARCH-027-WOOCOMMERCE-003
created: 2026-10-03
updated: 2026-10-11
---

# Expose WooCommerce purchase history and refund navigation

## Architecture

Architecture ID: `ARCH-027`

Architecture document: `docs/architecture/ARCH-027-woocommerce-marketplace-billing-adapter.md`

Coordinator: `moda_architect`

## Objective

Expose the merchant-safe Woo purchased-credit history needed by the Woo Billing UI and provide the **external WooCommerce.com refund-request navigation**.

This task is read-only for refunds.

It MUST NOT create a `RecoveryCreditRefund`, withdraw a purchase, hold credits, call Woo, or reactivate/cancel a refund.

Woo's v1 refund initiation is:

```text
Moda purchase history
    -> link to https://woocommerce.com/my-account/orders/
    -> merchant submits real refund request on WooCommerce.com
    -> Moda/vendor receives it in Woo Pending Refunds
    -> ADMIN-001 prepares the local allowance hold
```

## Scope

Add exactly:

```text
GET /v1/billing/recovery-credit-purchases
```

using the accepted Woo installation authentication boundary.

The response owns:

- ACTIVE/WITHDRAWN/COMPLETED/REFUNDED history;
- exact 5/10/20 page sizes and bounded pagination;
- provider-safe purchase/refund summaries;
- purchase-local refund eligibility presentation;
- the WooCommerce Orders refund-navigation URL;
- one-attempt history (`refundAttemptedAt`).

## Out of Scope

- `POST /v1/billing/recovery-credit-refunds` for Woo merchants.
- Any refund-reactivation endpoint.
- Batch refund commands.
- Monetary refund calculation.
- Creating the Woo provider refund request.
- Admin vendor approval/rejection.
- Provider webhook reconciliation.
- Shopify merchant refund routes.
- `docs/architecture/_index.md`.

## Requirements

### R1 — Exact endpoint/query contract

Accept only:

```text
GET /v1/billing/recovery-credit-purchases
  ?filter=ACTIVE|WITHDRAWN|COMPLETED|REFUNDED|ALL
  &page=<positive integer>
  &pageSize=5|10|20
```

Defaults:

```text
filter=ACTIVE
page=1
pageSize=5
```

Reject unknown query parameters.

### R2 — Authentication / tenant isolation

Authenticate with the accepted ARCH-026 Woo installation authenticator and derive `shopId` only from that principal.

Query only:

```text
purchase.shopId = principal.shopId
purchase.provider = WOOCOMMERCE
```

### R3 — Strict versioned response

Return `schemaVersion=1`, bounded pagination metadata and merchant-safe purchase rows.

Do not expose provider contract/transaction IDs, request keys, raw price snapshots, Shopify handles or internal billing-period IDs.

### R4 — Merchant-safe purchase row

Each row may expose:

```text
id
status
createdAt
activatedAt
bundleLabel | null
planName
creditsGranted
currentAmount
reservedAmount
availableAmount
heldForRefundAmount
refundEligible
refundUnavailableReason
refundAttempted
latestRefund | null
completedRefund | null
originalProviderPurchase amount/currency | null
```

`refundAttempted = purchase.refundAttemptedAt != null`.

### R5 — Woo refund request navigation is provider-owned

Return one bounded top-level contract:

```json
{
  "method": "WOOCOMMERCE_ORDERS",
  "url": "https://woocommerce.com/my-account/orders/"
}
```

The URL is navigation only. API-006 performs no mutation when the merchant follows it.

### R6 — Refund eligibility is local purchase guidance only

A Woo purchase may be presented as eligible to request a provider refund only when:

```text
status = ACTIVE
availableAmount > 0
valid Woo acquisition/provider evidence exists
refundAttemptedAt = NULL
```

Refund eligibility does not require the acquisition BillingPeriod/current recurring subscription to remain current.

If a prior refund attempt exists, return:

```text
refundEligible = false
refundUnavailableReason = REFUND_ALREADY_ATTEMPTED
```

even when the prior refund was REJECTED/CANCELLED and allowance was restored.

Other bounded reasons include:

```text
NO_AVAILABLE_CREDITS
PROVIDER_EVIDENCE_UNAVAILABLE
REFUND_IN_PROGRESS
```

### R7 — Requesting a refund is not a Moda API mutation

There is no Woo merchant refund POST in this task.

The merchant is told to submit the provider request in WooCommerce.com Orders. A local hold begins only after the vendor/operator verifies the real Pending Refund and ADMIN-001 prepares it.

### R8 — No merchant reactivation

Do not expose:

```text
reactivationAvailable
providerActionStarted as a merchant action gate
POST .../reactivate
```

The merchant cannot undo a refund attempt in Moda.

A vendor rejection may later restore held allowance through ADMIN-001, while the purchase remains permanently ineligible for another refund attempt.

### R9 — Refund summaries are status/history only

Return bounded refund status/reason/final credit quantity/provider-reported money when appropriate, but never calculate a Moda expected monetary refund.

### R10 — Pagination/order

Order by:

```text
createdAt DESC, id DESC
```

Clamp an over-high requested page to the last available page; empty result uses page 1.

## Work Items

- [ ] Add authenticated provider-scoped history query.
- [ ] Add strict filters/pagination/versioned response validation.
- [ ] Add merchant-safe refund history/status projection.
- [ ] Add `refundAttempted` / `REFUND_ALREADY_ATTEMPTED` semantics.
- [ ] Add WooCommerce Orders navigation contract.
- [ ] Remove/avoid Woo merchant refund and reactivation mutations.
- [ ] Update OpenAPI.
- [ ] Add focused tenant/provider/history/refund-navigation tests.

## Dependencies

- `ARCH-027-BACKGROUND-005`

BACKGROUND-005 fixes the authoritative Woo refund statuses and provider-refund completion semantics consumed by the history projection.

## Enables

- `ARCH-027-WOOCOMMERCE-003`

## Acceptance Criteria

- [ ] Exactly one GET purchase-history endpoint is owned by API-006.
- [ ] Woo merchant refund initiation performs no Moda mutation.
- [ ] Response contains the WooCommerce Orders URL.
- [ ] History is shop+WOOCOMMERCE scoped.
- [ ] A previous refund attempt permanently disables another refund request for the purchase.
- [ ] Rejected refund history may coexist with restored ACTIVE allowance but remains `refundEligible=false`.
- [ ] No merchant reactivation endpoint/field exists.
- [ ] Historical Woo purchase can remain refund-eligible after recurring plan/period changes when it has no prior attempt.
- [ ] No internal/provider/Shopify identifiers leak.
- [ ] `docs/architecture/_index.md` is unchanged.

## Validation

Required categories:

- [ ] OpenAPI validation;
- [ ] authentication/tenant isolation;
- [ ] filter/page-size/page-clamp tests;
- [ ] provider=WOOCOMMERCE exclusion/inclusion tests;
- [ ] refundAttempted/REFUND_ALREADY_ATTEMPTED tests;
- [ ] Orders URL response test;
- [ ] proof no refund/reactivation mutation routes were added;
- [ ] typecheck/build/lint/test according to repository scripts;
- [ ] `git diff --check`.

## Stop Condition

Complete the report, set `review`, return to `moda_architect`, STOP.

## Completion Report

### Status

Completed and **architect-accepted on 2026-10-11** as API-006 Attempt 2.
The developer applied the bounded API-006 implementation patch (Attempt 1)
and the two incremental Attempt 2 corrections. This closes the authenticated,
read-only purchase-history API implementation, **not** WooCommerce.com provider
transaction/refund certification. No task launcher claim, implementation commit
or push is asserted for this manual patch workflow.

### Files Changed

Developer-applied `moda-interact-api` implementation and test changes:

- `src/index.ts` and `src/woocommerce/installation/routes.ts` — integrate the
  new Woo purchase-history GET handler with the existing installation boundary;
- `src/billing/purchase-history/contract.ts`, `schema.ts`, `projection.ts`,
  `service.ts` and `routes.ts` — exact versioned response, provider-scoped
  history projection, read-only transaction and strict HTTP query handling;
- `src/billing/purchase-history/service.test.ts`, `routes.test.ts`,
  `schema.test.ts` and `openapi-contract.test.ts` — focused contract and
  behavioural proof;
- `openapi/woocommerce-billing-purchase-history-v1.yaml` — GET-only history
  contract and external Orders navigation;
- `src/woocommerce/rest-read/authorization.test.ts` — unrelated pre-existing
  unused-variable lint correction, delivered as a **separate** incremental
  Attempt 2 test-only patch.

**This architect acceptance patch changes only this parent task record.** It
does not alter API runtime source, tests, `_index.md` or architecture indexes.

### Work Completed

- Added only `GET /v1/billing/recovery-credit-purchases`, authenticated with
  the established Woo installation principal and constrained to its Shop and
  `provider=WOOCOMMERCE` purchases. No browser-supplied tenant or provider can
  expand that scope.
- Added strict `ACTIVE|WITHDRAWN|COMPLETED|REFUNDED|ALL` filters, bounded
  5/10/20 page sizes, deterministic newest-first order, last-page clamping and
  repeatable-read count/page consistency.
- Projects merchant-safe purchase and refund summaries without exposing raw
  provider charge IDs, internal billing-period IDs or Shopify identifiers.
- Derives refund eligibility from existing verified purchase evidence and
  durable `refundAttemptedAt`; a prior attempt permanently prevents a second
  merchant link even after a rejected refund restores spendable credits.
- Returns the fixed provider-owned navigation contract for
  `https://woocommerce.com/my-account/orders/`.
- Does **not** add Woo refund initiation, allowance withdrawal/hold,
  reactivation, cancellation, payment/refund amount calculation or settlement
  mutation endpoints. Financial and credit decisions remain with their
  respective Woo vendor/Admin/Background owners.
- Corrected TypeScript literal inference (`schemaVersion: 1`) via the
  `satisfies PurchaseHistoryResponse` type assertion and addressed one
  unrelated pre-existing REST-read test lint error in separately bounded
  Attempt 2 corrections. Neither correction changes runtime behaviour.

### Validation Results

- **Developer-reported PASS:** `npm run typecheck`, `npm run lint`, and
  `npm test` on the completed API-006 Attempt 2 implementation, after applying
  both incremental corrections. The developer explicitly confirmed all green.
  Raw final command output was not independently captured by the architect.
- Earlier architect-side isolated focused behavioural checks for API-006
  passed **9/9**, covering purchase-history projection, pagination,
  authentication, strict input handling and Orders link behavior. Those are
  isolated checks, not a substitute for the developer's complete repository
  suite or real provider certification.
- The developer's local typecheck initially identified the widened
  `schemaVersion` type; the corrected `satisfies` return passed subsequent
  reported validation. The unrelated REST-read unused-variable lint error was
  also separately corrected and reported green.
- The implementation/repair patches were checked against their stated upload
  baselines with `git apply --check --whitespace=error-all`, actual
  `git apply`, `git diff --check` and patch ZIP integrity. This task-record
  overlay is verified independently against the exact uploaded 2026-10-11
  17:07 workspace snapshot.
- The OpenAPI contract and focused contract tests are present in the
  implementation. No independent real WooCommerce.com refund request,
  vendor decision, payment settlement, webhook or non-empty purchased-history
  integration test is claimed here. A standalone `npm run build` result for
  API-006 was not separately supplied.

### Deviations

Implementation was completed with developer-applied, architect-supplied
incremental patches rather than the original dedicated agent/task-worktree
workflow. The Attempt 2 REST-read lint cleanup touches an unrelated test;
that change was provided separately and does not modify purchase-history
runtime logic. No implementation commit or agent Completion Report is inferred.

### Assumptions

- The user's all-green confirmation refers to both Attempt 2 corrections
  applied to the API implementation, not only to the initial Attempt 1 patch.
- `ARCH-027-BACKGROUND-005` is Complete at Attempt 3 in the latest uploaded
  parent workspace task record; its accepted provider-refund semantics remain
  the source of durable purchase/refund state.
- `ARCH-027-WOOCOMMERCE-003` consumes this versioned history contract, with
  its own separate plugin implementation and acceptance record.

### Unresolved Issues

1. WooCommerce.com Marketplace SaaS Billing sandbox key/secret have not been
   issued. Real provider charge creation, confirmation, vendor refund
   requests/decisions and signed settlement evidence remain untested release
   gates, not part of this read-only API endpoint's acceptance.
2. The LocalWP HTTP site is not suitable for the API's HTTPS-only provider
   return-URL builder. A valid HTTPS confirmation origin is required for
   provider system certification.
3. `ARCH-027-ADMIN-001` vendor-side refund handling and full ARCH-027
   provider/payment/refund integration certification remain separate work.
   No provider money/Moda credit settlement is inferred from this API read.
4. The parent task/workspace metadata reconciliation and architecture
   `_index.md` updates remain deferred until the user explicitly closes the
   broader architecture session.

### Architectural Concerns

No scope deviation in API-006's accepted GET-only contract. WooCommerce.com
owns merchant refund initiation and money, while Moda reads and reflects
verified provider/purchase evidence and separately owns recovery allowance.
Preserve one-attempt eligibility and fail-closed provider/tenant isolation.

## Architect Review

### Review Status

Accepted — **ARCH-027-API-006 Attempt 2**, implementation boundary only.
External WooCommerce.com billing/refund certification remains outstanding.

### Review Notes

Accepted the developer-applied purchase-history API, its strict read-only
contract and the bounded Attempt 2 typecheck/test-lint corrections. The
predecessor `ARCH-027-BACKGROUND-005` is recorded Complete, the dependent
WooCommerce history UI has been implemented and separately reviewed, and the
developer reports full local API validation green. This is not provider
payment/refund operational signoff.

### Reviewed Files

Uploaded 2026-10-11 API source snapshot: `src/billing/purchase-history/`
contract, projection, schema, service, route and focused test modules;
`src/index.ts`; `src/woocommerce/installation/routes.ts`;
`openapi/woocommerce-billing-purchase-history-v1.yaml`; and the two incremental
Attempt 2 correction patches.

### Validation Reviewed

Developer confirmation of green `npm run typecheck`, `npm run lint`,
`npm test`; prior 9/9 isolated API-006 checks and bounded patch/ZIP validation.
No live WooCommerce.com transaction, monetary refund, signed provider receipt
or end-to-end reconciliation was independently executed.

### Architecture Conformance

Conforms to ARCH-027 API-006: tenant/provider-scoped authenticated GET,
server-authoritative purchase/refund evidence, exact Orders navigation,
previous-refund-attempt suppression and no merchant financial/refund mutation.

### Follow-up

- Proceed with `ARCH-027-WOOCOMMERCE-003` task-record reconciliation if its
  separate acceptance patch has not yet been applied, and continue
  `ARCH-027-ADMIN-001` as its own owner of Woo vendor refund support.
- Obtain WooCommerce.com SaaS sandbox credentials and HTTPS return handling;
  certify purchase, vendor refund, provider webhooks and allowance settlement
  in the ARCH-027 integration/system tests before release.
- Do not change any `docs/decisions/**/_index.md` or architecture index until
  the user explicitly authorizes the final architecture reconciliation.
