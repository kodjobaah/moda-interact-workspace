---
id: ARCH-027-WOOCOMMERCE-001
architecture_id: ARCH-027
title: Add the Woo merchant billing hub and recurring plan management
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 75
executor: copilot
claimed_at: 2026-10-09T08:58:16Z
attempt: 1
depends_on:
  - ARCH-026-WOOCOMMERCE-005
  - ARCH-027-API-002
  - ARCH-027-API-003
enables:
  - ARCH-027-WOOCOMMERCE-002
created: 2026-10-03
updated: 2026-10-09
---

# Add the Woo merchant billing hub and recurring plan management

## Architecture

Architecture ID:

`ARCH-027`

Architecture document:

`docs/architecture/ARCH-027-woocommerce-marketplace-billing-adapter.md`

Coordinator:

`moda_architect`

## Objective

Extend the accepted ARCH-026 WooCommerce Admin application with the first real merchant billing surface.

This task owns:

```text
Billing navigation/content surface
current plan/status
recovery-capacity summary
selectable plan catalogue
Free -> paid subscription checkout
paid -> paid plan switch checkout
paid Woo cancellation -> scheduled prepaid term end
actual prepaid term end -> verified return to Free
later paid purchase after term end -> ordinary Free -> paid flow
Woo confirmation redirect
Woo return/status refresh
pending plan/cancellation presentation
```

The browser architecture remains exactly:

```text
WooCommerce Admin React
        |
        | WordPress REST cookie + nonce
        v
local Moda plugin REST route
        |
        | PHP ModaApiClient
        | stored installation credential
        v
hosted moda-interact-api
        |
        v
durable Moda billing state / Woo command initiation
```

Browser JavaScript MUST NOT call `moda-interact-api` directly.

The WordPress plugin MUST NOT contain:

```text
Woo vendor API key
Woo vendor API secret
Moda installation bearer credential in JavaScript
authoritative billing calculations
provider contract IDs
```

This task deliberately does **not** implement:

- top-up purchasing; owned by later `ARCH-027-WOOCOMMERCE-002`;
- purchase history/refund UI; owned by later `ARCH-027-WOOCOMMERCE-003`.

It may display purchased/top-up capacity already returned by API-002, but it must not expose non-functional Buy/Refund controls before those tasks exist.

## Context

ARCH-026 established the plugin application boundary:

- WOO-003 owns the server-side installation credential and authenticated Moda HTTP client;
- WOO-004 owns the Woo Admin React shell and connection lifecycle;
- WOO-005 owns the first authenticated merchant Overview and proves the browser -> local WordPress REST -> PHP Moda client -> hosted API pattern;
- React never receives the remote installation credential;
- local REST routes require `manage_woocommerce` and normal WordPress REST cookie/nonce authorization;
- merchant business data is not persisted in `localStorage` / `sessionStorage`.

ARCH-027 now provides:

### API-002 — read model

```text
GET /v1/billing
GET /v1/billing/plans
```

including:

```text
experienceState
surface availability
currentPlan
pendingPlan
pendingCancellation
capacity
predefined top-up presentation
selectable plan catalogue
```

### API-003 — recurring commands

```text
POST   /v1/billing/subscription
POST   /v1/billing/subscription/switch
DELETE /v1/billing/subscription
```

Create/switch return a validated Woo `confirmationUrl`.

Cancellation is provider-command acceptance only; paid access continues until verified lifecycle evidence reaches prepaid-term end.

### Shopify UX reference

The current Shopify application already presents:

- billing hero/current plan;
- capacity balances;
- current/pending plan;
- scheduled cancellation;
- plan-management actions;
- provider confirmation as a separate provider-controlled step.

Woo must reproduce those product semantics without reproducing Shopify hosted-pricing mechanics.

## Scope

Modify only `moda-interact-woocommerce` PHP/React/tests/documentation required for:

1. local PHP proxy routes for API-002/API-003;
2. a real Billing surface in the existing Woo Admin shell;
3. current/pending/cancellation/capacity presentation;
4. plan catalogue selection;
5. recurring create/switch/cancel commands;
6. redirect/return UX.

Expected implementation areas conceptually:

```text
includes/
  Api/
    ModaApiClient.php          # extend accepted WOO-003 client
  Rest/
    BillingController.php

src/
  billing/
    billing-client.ts
    billing-state.ts
    billing-page.tsx
    billing-summary.tsx
    plan-list.tsx
    plan-card.tsx
    pending-billing-notice.tsx
    use-billing.ts
    use-plans.ts
    use-recurring-command.ts

  app/navigation or existing shell composition files

tests/
  ... PHP REST/client + React/controller/presentation tests
```

Exact filenames must follow the accepted ARCH-026 implementation rather than creating duplicate framework layers.

## Out of Scope

- Direct browser calls to the hosted Moda API.
- Woo vendor credentials in WordPress/PHP/browser.
- Top-up purchase command/UI.
- Purchase-history/refund/reactivation UI.
- Merchant refund hold creation.
- Usage-history implementation.
- Admin support tooling.
- Webhook processing.
- Background reconciliation.
- Provider price/tax calculation.
- A second frontend router/state-management/data-fetching framework.
- New WordPress top-level menu/page.
- Prisma/database changes.
- Gateway/Render changes.
- Updating `docs/architecture/_index.md`.

## Requirements

### R1 — Billing is a real second merchant surface inside the existing shell

Add one navigable merchant surface:

```text
Billing
```

inside the existing ARCH-026 `/moda-interact` WooCommerce Admin application.

Do not register another WordPress top-level page.

The existing:

```text
Overview
```

remains intact.

Do not add placeholder navigation for Top-ups, Purchase History, Refunds, Usage or Support unless a real accepted backend/UI task owns the destination.

The Billing surface may contain internal view switching for:

```text
Summary
Plans
```

without introducing a new router framework.

### R2 — Connection state gates billing data

Load/render hosted billing data only while WOO-004 connection state is:

```text
CONNECTED
```

When connection leaves CONNECTED:

- abort/ignore stale billing/plans responses;
- clear/hide merchant billing state;
- return to the accepted connection/setup presentation.

Do not infer connection from billing API success/failure.

### R3 — Exact local read routes

Expose exactly:

```text
GET /wp-json/moda-interact/v1/billing
GET /wp-json/moda-interact/v1/billing/plans
```

Both require:

```text
manage_woocommerce
valid WordPress REST cookie/nonce authentication
accepted WOO-003 local connection state
```

PHP calls:

```text
GET /v1/billing
GET /v1/billing/plans
```

through the accepted server-side Moda API client.

The browser never sends or receives the installation bearer credential.

### R4 — Presentation locale for plan catalogue

For the local plans route, PHP derives presentation locale from the current WordPress administrator UI locale.

Normalize WordPress locale syntax only for this presentation request, e.g.:

```text
en_GB -> en-GB
```

and pass it as:

```text
GET /v1/billing/plans?locale=<BCP-47>
```

when valid.

Do not persist that locale as Shop/store international context.

Do not use store locale to change the WordPress Admin UI language.

If locale normalization fails, omit the optional locale and allow API-002 fallback behavior.

### R5 — PHP strictly validates hosted read responses

Consume API-002's versioned contract.

Require:

```text
schemaVersion = 1
```

and strict bounded response validation.

Do not forward arbitrary remote JSON to React.

Unknown schema versions/malformed/oversized/non-JSON responses become bounded local errors.

Use the same remote error/redaction conventions established by WOO-003/WOO-005.

### R6 — Exact local recurring command routes

Expose exactly these browser-facing local routes:

```text
POST /wp-json/moda-interact/v1/billing/subscription
POST /wp-json/moda-interact/v1/billing/subscription/switch
POST /wp-json/moda-interact/v1/billing/subscription/cancel
```

Each requires:

```text
manage_woocommerce
valid WordPress REST nonce/cookie
CONNECTED installation
```

The local cancel route deliberately uses POST even though PHP calls the hosted:

```text
DELETE /v1/billing/subscription
```

This avoids browser/body ambiguity while keeping the hosted API contract unchanged.

### R7 — Browser action ID is idempotency only, never authority

Create/switch local request:

```json
{
  "merchantPricingPlanId": "...",
  "actionId": "..."
}
```

Cancel local request:

```json
{
  "actionId": "..."
}
```

`actionId` is a browser-generated UUID v4 created with a cryptographically secure browser primitive such as:

```text
crypto.randomUUID()
```

Require canonical lower/upper hexadecimal UUID-v4 syntax.

PHP maps:

```text
actionId -> hosted Idempotency-Key header
```

unchanged.

PHP never includes `actionId` in the hosted JSON body.

`actionId` is not tenant identity and grants no authority.

React keeps one action ID in memory for the lifetime of one explicit command attempt so local HTTP retries reuse the same idempotency key.

A deliberate new merchant attempt generates a new action ID.

Do not persist action IDs in browser storage.

### R8 — Create/switch remote mapping is exact

Local create:

```text
POST /wp-json/moda-interact/v1/billing/subscription
```

maps to:

```text
POST /v1/billing/subscription
Idempotency-Key: actionId

{
  "merchantPricingPlanId": "..."
}
```

Local switch maps identically to:

```text
POST /v1/billing/subscription/switch
```

The PHP layer MUST NOT supply:

```text
shopId
price
currency
billing period
provider contract ID
return URL
```

### R9 — Cancel remote mapping is exact

Local:

```text
POST /wp-json/moda-interact/v1/billing/subscription/cancel
{
  "actionId": "..."
}
```

maps to:

```text
DELETE /v1/billing/subscription
Idempotency-Key: actionId
```

with:

```text
no hosted request body
no query parameters
```

### R10 — Hosted command response is reduced to a browser-safe model

For create/switch, local PHP may return only:

```json
{
  "schemaVersion": 1,
  "operationId": "...",
  "state": "AWAITING_CONFIRMATION",
  "confirmationUrl": "https://..."
}
```

For cancel:

```json
{
  "schemaVersion": 1,
  "operationId": "...",
  "state": "CONFIRMED",
  "confirmationUrl": null
}
```

Do not return:

```text
providerContractId
requestKey
requestFingerprint
raw provider response
Woo credentials
```

### R11 — Defense-in-depth confirmation URL validation

Before returning create/switch success to React, PHP must validate:

```text
scheme = https
host exactly one of:
    woocommerce.com
    sandbox.woocommerce.com

username = empty
password = empty
```

Reject malformed/other-host URLs as:

```text
remote_response_invalid
```

Do not redirect to arbitrary URLs supplied by a remote error body.

React should validate the same bounded URL shape before navigation.

### R12 — Create/switch navigates the top-level browser to Woo

After a validated create/switch success, navigate with the browser top-level location to:

```text
confirmationUrl
```

Do not:

- render Woo checkout in an iframe;
- open a hidden popup;
- mark the plan changed locally;
- mutate WordPress options as billing truth.

The Woo confirmation page is provider-controlled.

### R13 — Woo return is a refresh signal, not entitlement proof

API-003 returns Woo to:

```text
/wp-admin/admin.php
?page=wc-admin
&path=/moda-interact
&moda_billing_return=1
&operation=<opaque operation id>
```

When that marker is present:

1. select/open the Billing surface;
2. perform a fresh local `GET /billing`;
3. present returned durable current/pending state.

The browser return MUST NOT:

```text
activate the paid plan
change current plan
clear pending state
write billing state to WordPress
```

The `operation` parameter is diagnostic/refresh context only.

Do not send it as tenant or billing authority.

### R14 — No unbounded webhook polling in the browser

After Woo return, perform one authoritative refresh.

If the durable read still shows pending state, present:

```text
Confirmation is still being processed.
```

with an explicit:

```text
Refresh
```

action.

Do not implement indefinite polling or a background retry loop.

A bounded single-flight manual refresh is sufficient because provider webhook reconciliation owns correctness.

### R15 — Current plan summary mirrors the Shopify product concepts

Render API-002:

```text
currentPlan.displayName
currentPlan.planKind
currentPlan.recurringAmountMinor
currentPlan.currency
currentPlan.billingPeriod
currentPlan.currentPeriodEnd
currentPlan.cancelAtPeriodEnd
```

For Free, a null:

```text
currentPeriodEnd
provider subscription
```

is normal.

For Woo, verified `canceled` **does** remain as a scheduled paid state until prepaid entitlement ends. The UI may show `pendingCancellation` only during the command-to-webhook reconciliation window; once BACKGROUND-002 verifies `canceled`, authoritative billing state remains the paid plan with:

```text
cancelAtPeriodEnd = true
cancellationEffectiveAt = provider end date
```

Render `currentPeriodEnd` only as the next Moda included-allowance reset. Render `cancellationEffectiveAt` separately as the date the paid subscription ends. Do not label either as Woo `next_payment_date`.

### R16 — Capacity summary uses API-002 only

Render the available categories returned by the hosted read:

```text
paidIncluded
freeLifetime
promotional
purchased
```

Do not recalculate capacity from raw database/business rules in PHP or React.

For purchased capacity use:

```text
capacity.purchased.available
```

as the merchant-usable amount.

Do not implement top-up purchasing in this task.

### R17 — Pending recurring presentation is durable

Render:

```text
pendingPlan
```

when API-002 returns it.

Present state deliberately:

```text
INITIATING
AWAITING_CONFIRMATION
OUTCOME_UNKNOWN
```

`OUTCOME_UNKNOWN` must be explained as requiring reconciliation/support rather than offering an automatic provider retry.

Also render API-002:

```text
pendingCancellation
```

when non-null.

Possible states:

```text
INITIATING
AWAITING_CONFIRMATION
OUTCOME_UNKNOWN
CONFIRMED
```

`CONFIRMED` means Woo accepted the cancellation command but the durable Subscription projection has not yet recorded scheduled cancellation.

Do not infer pending cancellation from browser memory alone.

### R18 — Plan catalogue uses opaque Moda plan IDs

Load:

```text
GET /billing/plans
```

only when the Billing surface needs plan-management content and API-002:

```text
surfaces.managePlansAllowed = true
```

Render:

```text
displayName
localizedDescription
includedRecoveryCredits
recurringAmountMinor
currency
billingPeriod
featured
highlights
```

Selection authority is only:

```text
merchantPricingPlanId
```

Never expose or consume:

```text
shopifyPlanHandle
Woo provider contract ID
```

in React.

### R19 — Exact plan action matrix

Use authoritative billing state + selected plan.

#### Free -> paid

POST local `/billing/subscription`, then Woo confirmation.

This is the only subscription-create UI path. It applies both to a merchant who has always been Free and to a merchant whose earlier Woo paid contract was verified canceled and therefore already returned to Free.

The UI does not decide whether prior paid usage carries forward; BACKGROUND-002 decides that from durable former-period state after verified activation.

#### ACTIVE paid -> different paid

POST local `/billing/subscription/switch`, then Woo confirmation.

#### ACTIVE or payment-paused FROZEN paid -> cancel

Explicit confirmation, then local cancel.

After Woo accepts the DELETE, keep showing pending cancellation until BACKGROUND-002 receives verified `canceled` lifecycle evidence.

After verified cancellation the next billing read still shows the current paid plan with a scheduled end:

```text
currentPlan = current paid plan
cancelAtPeriodEnd = true
cancellationEffectiveAt = provider end date
```

Paid included allowance remains current until the prepaid term actually ends. Purchased/lifetime-Free capacity remains visible/owned throughout. At actual term end the next authoritative read becomes normal Free.

#### FROZEN

FROZEN means provider payment-pause/recovery, not successful cancellation. Do not offer plan switch/create while FROZEN; allow cancel only when API-002 says `cancelSubscriptionAllowed=true`.

#### Current plan

ACTIVE paid current plan is no-op. Free merchants may select any eligible paid plan through the normal Free -> paid path.

### R20 — Plan actions fail closed while a recurring transition is pending

Disable conflicting recurring actions while a command/pending operation is authoritative. Do not use `experienceState != ACTIVE` as a blanket block. Use API-002 `managePlansAllowed` and `cancelSubscriptionAllowed`.

There is no `resubscribeAllowed` surface state. While cancellation is scheduled the merchant remains on the paid plan and recurring plan create/switch is disabled. After prepaid term end the merchant is ordinary Free and may use the normal Free -> paid flow.

Do not rely only on button disabling for correctness; hosted API remains authoritative.

### R21 — FROZEN/BILLING_ATTENTION presentation

For:

```text
experienceState = FROZEN
```

present current plan/capacity as available from API-002 but disable plan-management commands and new top-up purchasing.

Use merchant-readable text that recurring billing recovery is required.

Also explain:

```text
paid included credits -> temporarily unavailable
already-owned purchased top-up credits -> remain usable
remaining lifetime-Free credits -> remain usable
promotional credits -> existing promotion eligibility
```

Do not tell the merchant that all recovery capacity is frozen.

For:

```text
BILLING_ATTENTION
NO_CONTRACT
```

present the bounded API state and disable unsupported commands.

Do not fabricate a repair/reconnect billing action.

Connection/authentication issues remain the ARCH-026 connection experience.

### R22 — Cancellation command does not immediately display Free

After local cancellation returns:

```text
state = CONFIRMED
```

do not change `currentPlan` locally.

Set a transient success notice:

```text
Cancellation request accepted.
```

then refresh `GET /billing`.

Durable UI truth is `pendingCancellation` until verified provider cancellation is reconciled. After that refresh `pendingCancellation` clears and the current paid plan shows `cancelAtPeriodEnd=true` plus `cancellationEffectiveAt`.

The UI does not offer replacement recurring plan creation/switch while cancellation is scheduled. After actual prepaid term end the current plan becomes Free; any later paid selection uses the ordinary Free -> paid flow.

### R23 — Strict single-flight/stale-response behavior

Billing reads, plan reads and commands must be race-safe.

Requirements:

- no overlapping command submissions;
- a late Billing GET cannot overwrite a newer post-command refresh;
- a late Plans GET cannot overwrite state after connection leaves CONNECTED;
- a late Billing result cannot re-show merchant billing state after disconnect;
- command buttons remain disabled until command success/failure is authoritative;
- browser navigation to Woo occurs only for the currently authoritative command response.

Reuse WOO-004/WOO-005 request-generation/abort/stale-response patterns rather than introducing another state library.

### R24 — Local error mapping is bounded

PHP must not relay arbitrary hosted/provider error bodies.

React receives bounded local codes sufficient for presentation, including categories such as:

```text
remote_authentication_failed
remote_unavailable
billing_not_initialized
billing_operation_conflict
billing_operation_in_progress
billing_provider_outcome_unknown
billing_operation_failed
invalid_plan_selection
remote_response_invalid
```

Map exact accepted hosted error codes where useful but keep arbitrary remote details server-side.

A hosted installation-auth failure must feed the existing connection-attention/reconnect path rather than pretending to be a billing-plan problem.

### R25 — No browser persistence of billing business state

Do not copy billing/plans/command responses to:

```text
localStorage
sessionStorage
WordPress options
cookies
```

React state is in-memory and reloaded from the authenticated local PHP route.

The server-side WOO-003 installation credential remains the only persistent plugin credential.

### R26 — Internationalization/accessibility

All plugin-visible strings use:

```text
@wordpress/i18n
text domain: moda-interact
```

Do not invent a Moda Woo locale allowlist.

Currency/date/number formatting must use locale-aware platform/browser primitives.

Plan/cancellation/pending status must not be communicated by color/icon alone.

Busy buttons expose disabled/busy state to assistive technology.

Confirmation dialog must be keyboard/focus accessible.

### R27 — No top-up or refund placeholder controls

This task may display:

```text
purchased-credit balance
```

because it is part of the billing summary.

It MUST NOT display clickable:

```text
Buy credits
Manage purchases
Refund
Reactivate
```

controls until their owning Woo UI tasks are accepted.

Do not create disabled "coming soon" actions.

## Work Items

- [ ] Extend the accepted PHP Moda API client with API-002 billing/plans reads and API-003 recurring commands.
- [ ] Add the two exact privileged local read routes.
- [ ] Add the three exact privileged local recurring command routes.
- [ ] Add strict PHP validation/redaction for API-002/API-003 responses.
- [ ] Add actionId -> hosted Idempotency-Key mapping.
- [ ] Add HTTPS/exact Woo-host confirmation URL validation.
- [ ] Add typed React billing/plans/command clients and discriminated state.
- [ ] Add Billing as a real second merchant surface inside the existing Woo Admin shell.
- [ ] Gate all billing work on CONNECTED.
- [ ] Render current plan, scheduled cancellation, capacity and pending-state summary.
- [ ] Render selectable API-002 plan catalogue with opaque Moda IDs only.
- [ ] Implement exact Free->paid / paid->paid / paid->Free action matrix.
- [ ] Add accessible cancellation confirmation.
- [ ] Redirect validated create/switch success to Woo at top-level.
- [ ] Detect Woo return marker, open Billing and refresh durable state once.
- [ ] Present durable pending confirmation/cancellation with explicit manual Refresh and no unbounded polling.
- [ ] Add single-flight/stale-response protections.
- [ ] Use WordPress i18n and accessible busy/status semantics.
- [ ] Prove no provider credentials, provider contract IDs or Shopify handles reach React.
- [ ] Add focused PHP REST/client + React/controller/presentation tests.

## Interfaces / Contracts

### Hosted reads

Owner:

`ARCH-027-API-002`

```text
GET /v1/billing
GET /v1/billing/plans?locale=<optional>
```

### Hosted recurring commands

Owner:

`ARCH-027-API-003`

```text
POST /v1/billing/subscription
POST /v1/billing/subscription/switch
DELETE /v1/billing/subscription
```

### Local browser reads

Owner:

`ARCH-027-WOOCOMMERCE-001`

```text
GET /wp-json/moda-interact/v1/billing
GET /wp-json/moda-interact/v1/billing/plans
```

### Local browser recurring commands

```text
POST /wp-json/moda-interact/v1/billing/subscription
POST /wp-json/moda-interact/v1/billing/subscription/switch
POST /wp-json/moda-interact/v1/billing/subscription/cancel
```

Local command `actionId` is translated by PHP to the hosted `Idempotency-Key`.

### Woo return

Provider/server-derived by API-003:

```text
/wp-admin/admin.php
?page=wc-admin
&path=/moda-interact
&moda_billing_return=1
&operation=<opaque id>
```

It is a UX refresh signal only.

## Dependencies

- `ARCH-026-WOOCOMMERCE-005`
- `ARCH-027-API-002`
- `ARCH-027-API-003`

All must be architect-accepted Complete before this task becomes Ready.

The ARCH-026 dependency supplies the accepted Admin shell/local REST/PHP credential boundary.

API-002 supplies merchant billing presentation.

API-003 supplies recurring provider commands and server-derived Woo confirmation URLs.

## Enables

- `ARCH-027-WOOCOMMERCE-002`

The next Woo task will add predefined top-up purchasing to this accepted Billing surface.

## Acceptance Criteria

- [ ] Billing is a real second merchant surface inside the existing `/moda-interact` Woo Admin shell.
- [ ] No new WordPress top-level page/router framework exists.
- [ ] Billing loads only while connection state is CONNECTED.
- [ ] Browser calls only local WordPress REST, never hosted Moda directly.
- [ ] PHP remote calls use only the stored installation credential for tenant authentication.
- [ ] Two exact local billing read routes exist with manage_woocommerce + nonce authorization.
- [ ] Three exact local recurring command routes exist with manage_woocommerce + nonce authorization.
- [ ] WordPress admin locale is presentation-only and is not persisted as store context.
- [ ] Hosted API responses are strictly schema-validated and arbitrary remote bodies are not relayed.
- [ ] Browser-generated UUID-v4 actionId maps only to hosted Idempotency-Key.
- [ ] Create/switch local routes accept only plan ID + actionId; cancel accepts only actionId.
- [ ] No browser input controls Shop, price, currency, period, provider contract or return URL.
- [ ] Confirmation URLs are HTTPS and host-limited to woocommerce.com / sandbox.woocommerce.com before browser navigation.
- [ ] Create/switch navigate the top-level browser to Woo and do not mutate local plan state.
- [ ] Woo return selects Billing and performs one durable-state refresh only.
- [ ] Browser return/operation query never activates or changes billing state.
- [ ] Current plan/capacity presentation comes only from API-002.
- [ ] Free is presented as a normal current plan with no recurring Woo contract required.
- [ ] Pending plan and pending cancellation states are presented durably.
- [ ] OUTCOME_UNKNOWN does not expose automatic retry.
- [ ] Free->paid uses create; ACTIVE paid->paid uses switch; verified Woo cancellation keeps the current paid plan visible with a scheduled end; actual prepaid term end returns the UI to Free, after which any later paid purchase uses the ordinary Free->paid create path.
- [ ] Scheduled cancellation shows a distinct `cancellationEffectiveAt`; `currentPeriodEnd` remains the Moda allowance-reset boundary.
- [ ] Current-plan selection is disabled/no-op.
- [ ] Any pending recurring transition/scheduled cancellation disables conflicting plan commands.
- [ ] Cancel success does not immediately display Free.
- [ ] FROZEN/BILLING_ATTENTION disable unsupported plan commands without inventing repair logic.
- [ ] Command/read state is single-flight and stale responses cannot overwrite newer connection/command state.
- [ ] Billing business data/action IDs are not persisted in browser storage/WordPress options.
- [ ] All strings are localized through WordPress i18n and actionable/status UI is accessible.
- [ ] No top-up/refund/purchase-history placeholder control is introduced.
- [ ] No Woo vendor credential/provider contract ID/Shopify handle reaches React.
- [ ] `docs/architecture/_index.md` is unchanged.

## Validation

Inspect the accepted `moda-interact-woocommerce/package.json`, Composer scripts and ARCH-026 validation instructions before choosing exact commands.

Required validation categories:

- [ ] required Woo repository/bootstrap preparation from accepted ARCH-026 instructions;
- [ ] JavaScript unit tests;
- [ ] PHP unit tests;
- [ ] changed-file JS lint;
- [ ] CSS lint when styles change;
- [ ] PHP lint/code standards;
- [ ] production build;
- [ ] plugin ZIP build/safety validation when required by repository policy;
- [ ] local billing GET PHP-client fixture test;
- [ ] local plans GET locale/header/strict-response tests;
- [ ] local create/switch/cancel PHP remote-mapping tests;
- [ ] test proving PHP sends installation auth but no caller-selected shopId/domain;
- [ ] actionId UUID validation + Idempotency-Key forwarding tests;
- [ ] confirmation URL allowed-host/rejected-host tests;
- [ ] WordPress REST permission/nonce tests for all five local routes;
- [ ] React connection-gating test;
- [ ] current Free/paid plan summary tests;
- [ ] capacity presentation tests;
- [ ] scheduled cancellation presentation test;
- [ ] pending plan state tests;
- [ ] pending cancellation INITIATING/OUTCOME_UNKNOWN/CONFIRMED presentation tests;
- [ ] plan catalogue Free/paid/current/featured rendering tests;
- [ ] exact Free->paid create mapping test;
- [ ] exact paid->paid switch mapping test;
- [ ] paid->Free confirmation/cancel mapping test;
- [ ] single-flight command test;
- [ ] stale Billing/Plans GET tests;
- [ ] Woo confirmation redirect top-level navigation test;
- [ ] Woo return marker selects Billing + one refresh and never activates state test;
- [ ] no unbounded polling test;
- [ ] FROZEN/BILLING_ATTENTION command-disabled tests;
- [ ] no browser persistence test;
- [ ] no direct hosted API/browser Authorization test;
- [ ] no top-up/refund placeholder controls test;
- [ ] current + minimum supported WordPress/WooCommerce browser/DOM smoke if required by accepted ARCH-026 repository policy;
- [ ] `git diff --check`;
- [ ] dedicated parent/implementation worktree, start-of-attempt synchronization and pushed task-branch evidence.

## Stop Condition

After all Work Items, Acceptance Criteria and required Validation are complete:

```text
finish Completion Report
    -> status: review
    -> return to moda_architect
    -> STOP
```

Do not begin top-up, purchase-history/refund, Admin support or Gateway work.

## Implementation Notes

Keep the task smaller than a full Shopify application clone.

The first Woo Billing surface should provide:

```text
current commercial state
capacity summary
plan management
provider checkout/return UX
```

and nothing that lacks a real accepted backend.

Reuse the WOO-004/WOO-005 shell and request-state patterns. Do not introduce a second frontend application architecture.

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

- ARCH-026-WOOCOMMERCE-005 provides the accepted Overview/shell/local REST/client structure.
- API-002 includes the companion `pendingCancellation` presentation correction included with this task definition.
- API-003 create/switch confirmation URLs remain provider/server-derived and validated.
- Top-up and purchase/refund UI are intentionally separate tasks to keep the Woo implementation reviewable.

### Unresolved Issues

None within the recurring billing UI boundary.

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
