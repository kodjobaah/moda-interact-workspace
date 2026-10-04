---
id: ARCH-027-WOOCOMMERCE-003
architecture_id: ARCH-027
title: Add WooCommerce purchase history, refund request and reactivation UI
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 85
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-027-WOOCOMMERCE-002
  - ARCH-027-API-006
enables: []
created: 2026-10-03
updated: 2026-10-03
---

# Add WooCommerce purchase history, refund request and reactivation UI

## Architecture

Architecture ID:

`ARCH-027`

Architecture document:

`docs/architecture/ARCH-027-woocommerce-marketplace-billing-adapter.md`

Coordinator:

`moda_architect`

## Objective

Complete the merchant-facing purchased-credit management portion of the Woo Billing experience.

This task adds a real:

```text
Purchased credits
```

view inside the accepted ARCH-027 Billing surface and reproduces the existing Shopify product behavior for:

```text
purchase history
status filters
pagination
single/batch refund selection
refund request confirmation
independent per-purchase outcomes
refund-in-progress presentation
pre-provider reactivation
completed refund history
```

The browser boundary remains:

```text
WooCommerce Admin React
        |
        | WordPress REST cookie + nonce
        v
local Moda plugin REST
        |
        | PHP ModaApiClient
        | stored installation credential
        v
ARCH-027-API-006
```

The plugin/browser MUST NOT:

- call the hosted Moda API directly;
- call Woo provider billing APIs;
- calculate refundable quantities;
- calculate refund money;
- expose Woo provider contract/transaction IDs;
- create/complete refunds locally;
- bypass BACKGROUND-005.

The merchant HTTP request creates only the local refund hold defined by API-006.

Provider refund preparation/settlement remains asynchronous in BACKGROUND-005.

## Context

WOOCOMMERCE-001 establishes the accepted Billing surface, PHP credential boundary, strict remote-response handling and connection-generation/stale-response protections.

WOOCOMMERCE-002 adds predefined top-up purchasing and the purchased-capacity summary.

API-006 now provides the exact backend surface:

```text
GET  /v1/billing/recovery-credit-purchases
POST /v1/billing/recovery-credit-refunds
POST /v1/billing/recovery-credit-refunds/reactivate
```

The existing Shopify purchase manager in the supplied workspace is the UX reference:

```text
filters:
    ACTIVE
    WITHDRAWN
    COMPLETED
    REFUNDED
    ALL

page sizes:
    5
    10
    20

default:
    ACTIVE
    page 1
    pageSize 5

batch maximum:
    20 purchases
```

The Shopify UI also demonstrates the accepted merchant interaction model:

- select eligible purchases on the current page;
- select-all affects the current visible eligible page only;
- confirm refund in an accessible dialog;
- submit the selected purchase IDs as one bounded merchant action;
- show independent result messages;
- refresh authoritative state after mutation;
- allow reactivation only while provider action has not begun.

### Woo-specific provider difference

Do not copy Shopify's current-meter-context presentation rule into Woo.

API-006 deliberately makes Woo refund eligibility purchase-local:

```text
unused/unreserved credits
+
valid purchase provider evidence
```

A historical Woo purchase may remain refundable after the merchant changes plan or billing period.

The UI MUST render the API's `refundEligible`, `refundUnavailableReason`, `reactivationAvailable` and `providerActionStarted` fields rather than rebuilding those rules in React.

## Scope

Modify only `moda-interact-woocommerce` PHP/React/tests required for:

1. local purchase-history proxy;
2. local refund-request proxy;
3. local refund-reactivation proxy;
4. Purchased credits view inside the existing Billing surface;
5. filters/pagination;
6. current-page single/batch selection;
7. refund confirmation/outcome UX;
8. refund status presentation;
9. pre-provider reactivation UX.

Expected implementation areas conceptually:

```text
includes/
  Api/
    ModaApiClient.php
  Rest/
    BillingController.php

src/
  billing/
    billing-page.tsx
    purchased-credits-view.tsx
    purchase-history-client.ts
    purchase-card.tsx
    purchase-filter-tabs.tsx
    purchase-pagination.tsx
    refund-confirmation-dialog.tsx
    refund-results.tsx
    use-purchase-history.ts
    use-refund-request.ts
    use-refund-reactivation.ts

tests/
  ... PHP client/REST + React state/presentation tests
```

Use the actual accepted WOO-001/WOO-002 component/controller structure where names differ.

## Out of Scope

- Provider refund initiation.
- Woo vendor-dashboard actions.
- Provider refund completion.
- Admin NEEDS_ATTENTION/unmatched-refund support UI.
- Subscription refund UI.
- Top-up quantity changes.
- Purchase-provider evidence inspection UI.
- Direct Woo API calls.
- Direct browser-to-hosted-Moda calls.
- New WordPress top-level page/menu.
- New frontend router/state-management/data-fetching framework.
- Database/API schema changes other than the companion API-006 response clarification in this definition patch.
- Gateway/infrastructure changes.
- Updating `docs/architecture/_index.md`.

## Requirements

### R1 — Add one real Purchased credits view inside Billing

Extend the existing WOOCOMMERCE-001 Billing surface with an internal:

```text
Purchased credits
```

view.

It is not a new WordPress page or top-level Woo Admin navigation destination.

The Billing surface may now switch among its accepted internal views:

```text
Summary
Plans
Purchased credits
```

using the existing Billing view-switching mechanism.

Do not introduce another router framework.

### R2 — Add the real Manage purchased credits entry point

Because the destination now exists, add a real merchant action from the purchased-capacity/top-up area:

```text
Manage purchased credits
```

It opens the internal Purchased credits view.

Do not show this action while the plugin connection is not:

```text
CONNECTED
```

The view remains available for:

```text
ACTIVE
FROZEN
BILLING_ATTENTION
```

billing experience states when the authenticated local API permits it.

Do not couple purchase/refund management to `surfaces.managePlansAllowed`.

### R3 — Exact local history route

Expose/extend exactly:

```text
GET /wp-json/moda-interact/v1/billing/recovery-credit-purchases
```

This is the same path whose POST method is already owned by WOOCOMMERCE-002 for top-up initiation.

GET requires:

```text
manage_woocommerce
valid WordPress REST cookie/nonce
CONNECTED installation
```

Accepted local query parameters are exactly:

```text
filter
page
pageSize
```

Reject unknown query parameters.

### R4 — Exact history remote mapping

PHP forwards only:

```text
GET /v1/billing/recovery-credit-purchases
    ?filter=<...>
    &page=<...>
    &pageSize=<...>
```

through the accepted server-side installation-authenticated Moda client.

Do not add:

```text
shopId
domain
provider contract
current plan
billing period
```

parameters.

### R5 — Exact filters and pagination

The React view exposes exactly:

```text
ACTIVE
WITHDRAWN
COMPLETED
REFUNDED
ALL
```

Default:

```text
ACTIVE
```

Page sizes exactly:

```text
5
10
20
```

Default:

```text
5
```

Changing filter or page size resets:

```text
page = 1
selected purchase IDs = []
```

Changing page also clears selections that are no longer visible/eligible.

Selection never spans hidden pages.

### R6 — Strict history response validation

Consume API-006's versioned history response:

```text
schemaVersion = 1
page
pageSize
total
purchases
```

Require:

- page/pageSize/total are bounded safe integers;
- `purchases` is an array bounded by `pageSize`;
- every purchase item conforms to API-006's merchant-safe contract;
- timestamps/money/refund summaries are bounded/nullable exactly as documented;
- no unknown schema version is accepted.

Do not forward arbitrary hosted JSON to React.

### R7 — Merchant purchase card contract

Each purchase card may render only API-006 merchant-safe fields:

```text
bundleLabel
planName
status

createdAt
activatedAt

creditsGranted
currentAmount
reservedAmount
availableAmount
heldForRefundAmount

originalProviderPurchase

latestRefund
completedRefund

refundEligible
refundUnavailableReason

reactivationAvailable
providerActionStarted
```

Fallback label when:

```text
bundleLabel = null
```

is merchant-readable:

```text
Purchased credits
```

Do not reconstruct a label from opaque IDs.

### R8 — Purchase statuses

Render these purchase states:

```text
REQUESTED
ACTIVE
WITHDRAWN
COMPLETED
REFUNDED
```

Merchant text:

```text
REQUESTED  -> Awaiting confirmation
ACTIVE     -> Active
WITHDRAWN  -> Refund in progress
COMPLETED  -> Used
REFUNDED   -> Refunded
```

`REQUESTED` may appear only through the `ALL` filter and is never refund-selectable.

Do not expose provider/operation IDs.

### R9 — Purchase metrics

Render:

```text
purchase date
original credits
current credits
reserved credits
available credits
original provider purchase amount
```

For WITHDRAWN also render:

```text
heldForRefundAmount
```

Money formatting uses the exact API value/currency and locale-aware browser formatting.

Do not derive provider amount from top-up catalogue price.

### R10 — Refund eligibility is API-authoritative

A purchase may be selected/requested only when:

```text
status = ACTIVE
refundEligible = true
availableAmount > 0
```

Do not rebuild eligibility from:

```text
current plan
current BillingPeriod
current Subscription status
provider contract
browser-known top-up offer
```

The API owns those decisions.

### R11 — Refund-unavailable reason mapping is bounded

For an ACTIVE non-eligible purchase map exactly:

```text
NO_AVAILABLE_CREDITS
    -> "There are no unused credits available to refund."

PROVIDER_EVIDENCE_UNAVAILABLE
    -> "This purchase is not currently available for provider refund."

REFUND_IN_PROGRESS
    -> "A refund is already in progress for this purchase."
```

Unknown values use a generic merchant-safe:

```text
Refund is not currently available.
```

Do not show raw backend reason codes.

For non-ACTIVE states the status itself is the explanation.

### R12 — Select-all is current-page only

Show a selection checkbox only for currently visible R10-eligible purchases.

`Select all` selects/deselects only those eligible purchases on the current page.

Because maximum page size is 20, the visible selection cannot exceed API-006's 20-purchase batch limit.

Do not implement cross-page retained selection.

### R13 — Refund confirmation dialog explains hold semantics

Before submitting selected purchases, show an accessible modal/dialog.

It must explain in merchant-readable language:

- only unused/unreserved purchased credits are placed on refund hold immediately;
- conversations/reservations already in progress are not interrupted;
- as those reservations settle/release, the final refundable credit quantity may change;
- the monetary refund is handled by Woo/provider workflow, not calculated by Moda;
- provider refund processing happens asynchronously after the local allowance hold;
- while the hold is active, those held credits cannot start new recoveries;
- reactivation is available only before provider processing begins.

Do not ask the merchant to enter:

```text
refund credit quantity
money amount
currency
provider transaction
```

### R14 — Exact local batch refund route

Expose exactly:

```text
POST /wp-json/moda-interact/v1/billing/recovery-credit-refunds
```

Require:

```text
manage_woocommerce
valid WordPress nonce/cookie
CONNECTED installation
```

Request JSON exactly:

```json
{
  "purchaseIds": ["...", "..."],
  "actionId": "<uuid-v4>"
}
```

Reject unknown fields.

### R15 — Refund `actionId` uses the accepted idempotency helper

Reuse WOOCOMMERCE-001/WOO-002's exact UUID-v4 `actionId` generator/validator.

One explicit batch confirmation creates one action ID.

PHP maps:

```text
actionId -> hosted Idempotency-Key
```

unchanged.

Remote body contains only:

```json
{
  "purchaseIds": ["...", "..."]
}
```

Do not persist the action ID.

An automatic local HTTP retry of the same explicit attempt reuses it.

A deliberate later refund request creates a new action ID.

### R16 — Exact remote refund mapping

Map local POST to:

```text
POST /v1/billing/recovery-credit-refunds
Idempotency-Key: actionId
```

with only:

```text
purchaseIds
```

PHP MUST NOT supply:

```text
quantity
refund amount
currency
shopId
billingPeriodId
providerReference
```

### R17 — Strict batch refund response

Accept only:

```json
{
  "schemaVersion": 1,
  "outcomes": [
    {
      "purchaseId": "...",
      "code": "...",
      "currentAmount": 10,
      "reservedAmount": 2,
      "availableAmount": 8
    }
  ]
}
```

Allowed outcome codes exactly:

```text
REQUESTED
REFUND_NOT_AVAILABLE
NOT_ACTIVE
ALREADY_WITHDRAWN
ALREADY_REFUNDED
COMPLETED
NOT_FOUND
REFUND_STATE_CONFLICT
```

Reject duplicate/unknown outcome purchase IDs or unknown codes as invalid remote response.

Do not forward arbitrary remote data.

### R18 — Refund outcome presentation

After one refund response:

1. clear current selection;
2. show one merchant-readable result per returned purchase;
3. refresh current purchase-history page;
4. refresh the existing Billing summary/capacity state.

Map outcomes:

```text
REQUESTED
    -> "Refund requested."

REFUND_NOT_AVAILABLE
    -> "Refund is not currently available."

NOT_ACTIVE
    -> "This purchase is no longer active."

ALREADY_WITHDRAWN
    -> "A refund is already in progress."

ALREADY_REFUNDED
    -> "This purchase has already been refunded."

COMPLETED
    -> "This purchase has no remaining credits."

NOT_FOUND
    -> "This purchase is no longer available."

REFUND_STATE_CONFLICT
    -> "Refund state changed. The latest purchase state has been refreshed."
```

Do not automatically resubmit failed outcomes.

### R19 — Refund request is single-flight

While one refund batch is in flight:

```text
selection controls disabled
refund buttons disabled
pagination/filter mutation disabled
reactivation disabled
```

This prevents UI races against the authoritative post-mutation refresh.

A batch outcome remains independently authoritative per purchase.

### R20 — Refund-status presentation uses known statuses only

Map `latestRefund.status`:

```text
REQUESTED
    -> "Refund requested. Waiting for in-progress reservations to settle."

PROVIDER_ACTION_REQUIRED
    -> "Credits are on hold. Complete the monetary refund through Woo's supported refund workflow."

NEEDS_ATTENTION
    -> "Refund needs review."

COMPLETED
    -> "Refund completed."

CANCELLED
    -> "Refund cancelled."

REJECTED
    -> "Refund could not be completed."
```

Do not expose raw refund status/reason codes to merchants.

### R21 — Known refund reasons may refine copy but are never printed raw

For a known `latestRefund.reason`:

```text
MERCHANT_REACTIVATED
    -> "Refund cancelled and credits reactivated."

NO_CREDITS_REMAINING
    -> "Refund cancelled because no refundable credits remained."

WOO_PROVIDER_REFUND_AMOUNT_MISMATCH
    -> "Refund needs review because provider settlement did not match the expected amount."
```

Other/unknown reasons use the status-level copy.

Never render the literal backend reason string.

### R22 — Completed refund presentation

For REFUNDED purchase:

```text
completedRefund.finalCreditQuantity
completedRefund.completedAt
```

may be displayed.

Provider money may be shown only as provider-reported audit history when the API exposes it. Do not calculate or label a Moda expected refund amount. Do not display provider transaction/reference IDs.

### R23 — Exact local reactivation route

Expose exactly:

```text
POST /wp-json/moda-interact/v1/billing/recovery-credit-refunds/reactivate
```

Require the same local WordPress permission/authentication boundary.

Request JSON exactly:

```json
{
  "purchaseId": "..."
}
```

No `actionId` is required because API-006 defines reactivation as state-idempotent.

Reject unknown fields.

### R24 — Exact remote reactivation mapping

Map to:

```text
POST /v1/billing/recovery-credit-refunds/reactivate
```

with exactly:

```json
{
  "purchaseId": "..."
}
```

No provider/refund quantity/money fields.

### R25 — Reactivation button is API-authoritative

Show:

```text
Reactivate credits
```

only when:

```text
purchase.status = WITHDRAWN
purchase.reactivationAvailable = true
```

Do not infer this from `latestRefund.status` alone.

When:

```text
providerActionStarted = true
```

show merchant-readable:

```text
Provider refund processing has started. These credits can no longer be reactivated here.
```

and no reactivation button.

### R26 — Accessible reactivation confirmation

Before reactivation show a confirmation dialog explaining:

```text
This cancels the local refund request only if provider refund processing has not started.
Available purchased credits will become usable again; in-progress reservations remain unchanged.
```

No provider details are shown.

### R27 — Strict reactivation response

Accept only:

```json
{
  "schemaVersion": 1,
  "purchaseId": "...",
  "code": "REACTIVATED" | "COMPLETED_NO_CREDITS",
  "currentAmount": 0,
  "reservedAmount": 0
}
```

`currentAmount`/`reservedAmount` are bounded non-negative safe integers.

For:

```text
REACTIVATED
```

show:

```text
Credits reactivated.
```

For:

```text
COMPLETED_NO_CREDITS
```

show:

```text
Refund request cancelled. No purchased credits remained to reactivate.
```

Then refresh purchase history and Billing capacity.

### R28 — Reactivation-not-available behavior

When hosted API reports:

```text
REACTIVATION_NOT_AVAILABLE
```

do not retry automatically.

Refresh purchase history once and show:

```text
This refund can no longer be reactivated.
```

The refreshed:

```text
reactivationAvailable
providerActionStarted
latestRefund
```

are authoritative.

### R29 — Provider action / NEEDS_ATTENTION cannot be cancelled by the browser

No UI control may attempt to reactivate/cancel:

```text
PROVIDER_ACTION_REQUIRED
NEEDS_ATTENTION
```

refunds.

The merchant sees status/support-oriented copy only.

Admin/support recovery remains a later task.

### R30 — History is refreshed independently from Billing read

The purchase-history endpoint is its own paginated read.

Do not attempt to synthesize the history from:

```text
topUps.latestPurchase
topUps.unresolvedPurchases
capacity.purchased
```

those remain summary data only.

After mutations:

```text
refresh purchase history
+
refresh Billing summary
```

because refund holds/reactivation change purchased available/refunding capacity.

### R31 — Connection changes clear purchase state

If ARCH-026 connection state leaves:

```text
CONNECTED
```

while the Purchased credits view is loaded:

- abort/ignore outstanding history/refund/reactivation responses;
- clear selection/outcomes/dialog state;
- clear merchant purchase-history data;
- return to accepted connection/setup presentation.

Do not leave purchase/refund data visible after connection invalidation.

### R32 — Stale response protection

Use the accepted WOO-001/WOO-002 connection generation/request sequencing.

A late response MUST NOT:

- repopulate history after disconnect;
- overwrite a newer page/filter response;
- show stale refund outcomes after a newer mutation/refresh;
- re-enable reactivation from an older purchase model.

### R33 — No browser persistence

Do not persist:

```text
purchase history
selected IDs
refund outcomes
actionId
refund state
provider amounts
```

in:

```text
localStorage
sessionStorage
WordPress options
cookies
```

The view always reloads from authenticated local REST.

### R34 — Localization/accessibility

All visible strings use:

```text
@wordpress/i18n
text domain: moda-interact
```

Requirements include:

- filter controls expose selected state;
- checkbox selection has meaningful accessible labels;
- result updates use an appropriate live region;
- dialogs are keyboard/focus accessible;
- busy state is announced and disables conflicting actions;
- status meaning is conveyed with text, not color alone;
- date/number/money formatting is locale-aware.

### R35 — No provider or internal identifiers in the browser model

PHP/React MUST NOT expose:

```text
Woo provider contract ID
Woo transaction ID
providerPriceSnapshot
providerReference
Shopify event/plan handles
refund requestKey
admin/support internal IDs
```

Only API-006's merchant-safe fields may cross the local browser boundary.

## Work Items

- [ ] Add Purchased credits as a real internal Billing view.
- [ ] Add the real Manage purchased credits entry point.
- [ ] Extend the existing local recovery-credit-purchases path with GET history proxy semantics.
- [ ] Add strict PHP query validation/filter/page/pageSize forwarding.
- [ ] Add strict history schema/item validation.
- [ ] Add ACTIVE/WITHDRAWN/COMPLETED/REFUNDED/ALL filter tabs.
- [ ] Add exact 5/10/20 page-size and bounded pagination.
- [ ] Render merchant-safe purchase cards/metrics/status/refund summaries.
- [ ] Add current-page-only eligible selection/select-all.
- [ ] Add accessible refund confirmation dialog with hold/reservation semantics.
- [ ] Add exact local batch refund route.
- [ ] Reuse actionId -> Idempotency-Key helper.
- [ ] Add exact independent outcome presentation and post-request history+Billing refresh.
- [ ] Add bounded refund status/reason presentation.
- [ ] Add exact local reactivation proxy route.
- [ ] Show Reactivate credits only from API `reactivationAvailable`.
- [ ] Add accessible reactivation confirmation.
- [ ] Add strict reactivation response handling and refresh.
- [ ] Block provider-action/NEEDS_ATTENTION reactivation.
- [ ] Add single-flight/stale-response/connection-generation protections.
- [ ] Prove no browser persistence/provider/internal identifier leakage.
- [ ] Add focused PHP/React tests.

## Interfaces / Contracts

### Local purchase history

```text
GET /wp-json/moda-interact/v1/billing/recovery-credit-purchases
  ?filter=ACTIVE|WITHDRAWN|COMPLETED|REFUNDED|ALL
  &page=1
  &pageSize=5|10|20
```

Hosted owner:

`ARCH-027-API-006`

### Local refund request

```text
POST /wp-json/moda-interact/v1/billing/recovery-credit-refunds

{
  "purchaseIds": ["..."],
  "actionId": "<uuid-v4>"
}
```

Maps to hosted API-006 with:

```text
Idempotency-Key = actionId
```

and no actionId in hosted JSON.

### Local reactivation

```text
POST /wp-json/moda-interact/v1/billing/recovery-credit-refunds/reactivate

{
  "purchaseId": "..."
}
```

### Background handoff

The plugin performs no direct Background call.

The durable API-006 refund row:

```text
provider = WOOCOMMERCE
status = REQUESTED
```

is consumed asynchronously by BACKGROUND-005.

## Dependencies

- `ARCH-027-WOOCOMMERCE-002`
- `ARCH-027-API-006`

Both must be architect-accepted Complete before WOOCOMMERCE-003 becomes Ready.

WOOCOMMERCE-002 supplies the accepted complete Billing/top-up surface and shared PHP/React billing state patterns.

API-006 supplies the exact history/refund/reactivation hosted contracts.

## Enables

None yet.

Follow-on architecture areas include:

- Admin Woo PROVIDER_ACTION_REQUIRED / NEEDS_ATTENTION / unmatched-refund support;
- Gateway/deployment wiring;
- end-to-end Woo billing system/sandbox validation.

## Acceptance Criteria

- [ ] Purchased credits is a real internal view in the existing Billing surface.
- [ ] No new WordPress top-level page/router framework is introduced.
- [ ] Manage purchased credits links to the real implemented destination.
- [ ] Purchase/refund management is available while connected even when recurring billing is FROZEN/BILLING_ATTENTION.
- [ ] GET purchase history uses only local privileged REST -> PHP -> hosted API.
- [ ] Exact filters/default/page sizes/pagination are implemented.
- [ ] Selection is current-page-only and never exceeds the 20-item API batch bound.
- [ ] History response is strict schemaVersion 1 and merchant-safe.
- [ ] REQUESTED appears only in ALL and is never refund-selectable.
- [ ] React renders no provider/internal identifiers.
- [ ] Refund eligibility/unavailability/reaction availability come from API fields rather than recreated provider rules.
- [ ] Refund confirmation asks for no quantity/money/provider input and states that Woo/provider owns monetary settlement while Moda holds allowance.
- [ ] Batch refund sends only purchaseIds + actionId locally; PHP maps actionId only to Idempotency-Key.
- [ ] Independent API outcomes are rendered independently and are not auto-retried.
- [ ] Successful/partial batch result refreshes both purchase history and Billing capacity state.
- [ ] Refund REQUESTED/PROVIDER_ACTION_REQUIRED/NEEDS_ATTENTION/COMPLETED/CANCELLED/REJECTED are rendered with bounded merchant-safe text.
- [ ] Raw backend reason codes are never printed.
- [ ] Reactivation button is controlled only by API `reactivationAvailable`.
- [ ] `providerActionStarted` blocks reactivation and shows provider-processing copy.
- [ ] Reactivation request contains only purchaseId.
- [ ] REACTIVATED and COMPLETED_NO_CREDITS responses are strictly validated and reflected after refresh.
- [ ] REACTIVATION_NOT_AVAILABLE causes one refresh and no automatic retry.
- [ ] Provider-action/NEEDS_ATTENTION refunds have no browser cancellation/reactivation action.
- [ ] Disconnect clears purchase/refund data and stale requests cannot restore it.
- [ ] Purchase/refund state/action IDs are not persisted in browser/WordPress storage.
- [ ] All strings/actions/statuses meet WordPress i18n/accessibility requirements.
- [ ] `docs/architecture/_index.md` is unchanged.

## Validation

Inspect accepted `moda-interact-woocommerce` scripts/repository instructions before selecting exact commands.

Required validation categories:

- [ ] repository-required Woo bootstrap/preparation;
- [ ] JavaScript unit tests;
- [ ] PHP unit tests;
- [ ] changed-file JS lint;
- [ ] CSS lint when styles change;
- [ ] PHP lint/code standards;
- [ ] production build;
- [ ] plugin ZIP/safety validation when repository policy requires it;
- [ ] local history REST permission/nonce/query validation tests;
- [ ] PHP history remote mapping and strict schema/item validation tests;
- [ ] ACTIVE/WITHDRAWN/COMPLETED/REFUNDED/ALL filter tests;
- [ ] exact 5/10/20 pagination/page-clamp tests;
- [ ] current-page-only selection/select-all test;
- [ ] REQUESTED-in-ALL/non-selectable test;
- [ ] refundUnavailableReason merchant-copy mapping tests;
- [ ] refund dialog no quantity/money inputs test;
- [ ] local refund REST permission/nonce/body test;
- [ ] actionId -> hosted Idempotency-Key/body redaction test;
- [ ] independent batch outcome rendering test for every API-006 code;
- [ ] mutation refreshes history + Billing capacity test;
- [ ] latestRefund status/reason bounded-copy tests;
- [ ] completed-refund quantity/date/money presentation test;
- [ ] local reactivation REST permission/nonce/body test;
- [ ] `reactivationAvailable=true` button test;
- [ ] `providerActionStarted=true` blocked-copy test;
- [ ] REACTIVATED response/refresh test;
- [ ] COMPLETED_NO_CREDITS response/refresh test;
- [ ] REACTIVATION_NOT_AVAILABLE refresh/no-retry test;
- [ ] refund request/reactivation single-flight tests;
- [ ] stale page/filter/history response test;
- [ ] disconnect clears/blocks stale purchase data test;
- [ ] no browser persistence test;
- [ ] no direct hosted API/provider/network call from browser test;
- [ ] no provider/internal identifier leakage test;
- [ ] WordPress i18n/accessibility/focus/live-region tests;
- [ ] current/minimum supported WordPress/WooCommerce browser/DOM smoke when required by repository policy;
- [ ] `git diff --check`;
- [ ] dedicated parent/implementation worktree, start-of-attempt synchronization and pushed task-branch evidence.

## Stop Condition

After Work Items, Acceptance Criteria and required Validation complete:

```text
finish Completion Report
    -> status: review
    -> return to moda_architect
    -> STOP
```

Do not begin Admin refund support, Gateway or system-test work.

## Implementation Notes

Match the Shopify product behavior, not its provider implementation.

The correct boundary is:

```text
React
    -> display API-computed eligibility/state
    -> submit selected purchase IDs

PHP
    -> authenticated API proxy

API-006
    -> create/cancel local refund hold

BACKGROUND-005
    -> prepare provider economics
    -> reconcile provider refund evidence
```

Do not move refund arithmetic or provider state interpretation into the plugin.

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

- WOOCOMMERCE-002 is accepted and supplies the complete Billing/top-up shell.
- API-006 is accepted with the companion versioned-history/reactivation response clarification in this patch.
- BACKGROUND-005 remains the only Woo refund preparation/settlement owner.
- Admin/provider-attention recovery remains a later task.

### Unresolved Issues

None within the merchant purchase-history/refund/reactivation UI boundary.

### Architectural Concerns

None.

## Architect Review

### Review Status

Pending

### Review Notes

Pending implementation.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending.

### Follow-up

Pending.
