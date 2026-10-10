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
status: complete
priority: 75
executor: null
claimed_at: null
attempt: 2
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

- [x] Extend the accepted PHP Moda API client with API-002 billing/plans reads and API-003 recurring commands.
- [x] Add the two exact privileged local read routes.
- [x] Add the three exact privileged local recurring command routes.
- [x] Add strict PHP validation/redaction for API-002/API-003 responses.
- [x] Add actionId -> hosted Idempotency-Key mapping.
- [x] Add HTTPS/exact Woo-host confirmation URL validation.
- [x] Add typed React billing/plans/command clients and discriminated state.
- [x] Add Billing as a real second merchant surface inside the existing Woo Admin shell.
- [x] Gate all billing work on CONNECTED.
- [x] Render current plan, scheduled cancellation, capacity and pending-state summary.
- [x] Render selectable API-002 plan catalogue with opaque Moda IDs only.
- [x] Implement exact Free->paid / paid->paid / paid->Free action matrix.
- [x] Add accessible cancellation confirmation.
- [x] Redirect validated create/switch success to Woo at top-level.
- [x] Detect Woo return marker, open Billing and refresh durable state once.
- [x] Present durable pending confirmation/cancellation with explicit manual Refresh and no unbounded polling.
- [x] Add single-flight/stale-response protections.
- [x] Use WordPress i18n and accessible busy/status semantics.
- [x] Prove no provider credentials, provider contract IDs or Shopify handles reach React.
- [x] Add focused PHP REST/client + React/controller/presentation tests.

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

- [x] Billing is a real second merchant surface inside the existing `/moda-interact` WooCommerce Admin shell.
- [x] No new WordPress top-level page/router framework exists.
- [x] Billing loads only while connection state is CONNECTED.
- [x] Browser calls only local WordPress REST, never hosted Moda directly.
- [x] PHP remote calls use only the stored installation credential for tenant authentication.
- [x] Two exact local billing read routes exist with manage_woocommerce + nonce authorization.
- [x] Three exact local recurring command routes exist with manage_woocommerce + nonce authorization.
- [x] WordPress admin locale is presentation-only and is not persisted as store context.
- [x] Hosted API responses are strictly schema-validated and arbitrary remote bodies are not relayed.
- [x] Browser-generated UUID-v4 actionId maps only to hosted Idempotency-Key.
- [x] Create/switch local routes accept only plan ID + actionId; cancel accepts only actionId.
- [x] No browser input controls Shop, price, currency, period, provider contract or return URL.
- [x] Confirmation URLs are HTTPS and host-limited to woocommerce.com / sandbox.woocommerce.com before browser navigation.
- [x] Create/switch navigate the top-level browser to Woo and do not mutate local plan state.
- [x] Woo return selects Billing and performs one durable-state refresh only.
- [x] Browser return/operation query never activates or changes billing state.
- [x] Current plan/capacity presentation comes only from API-002.
- [x] Free is presented as a normal current plan with no recurring Woo contract required.
- [x] Pending plan and pending cancellation states are presented durably.
- [x] OUTCOME_UNKNOWN does not expose automatic retry.
- [x] Free->paid uses create; ACTIVE paid->paid uses switch; verified Woo cancellation keeps the current paid plan visible with a scheduled end; actual prepaid term end returns the UI to Free, after which any later paid purchase uses the ordinary Free->paid create path.
- [x] Scheduled cancellation shows a distinct `cancellationEffectiveAt`; `currentPeriodEnd` remains the Moda allowance-reset boundary.
- [x] Current-plan selection is disabled/no-op.
- [x] Any pending recurring transition/scheduled cancellation disables conflicting plan commands.
- [x] Cancel success does not immediately display Free.
- [x] FROZEN/BILLING_ATTENTION disable unsupported plan commands without inventing repair logic.
- [x] Command/read state is single-flight and stale responses cannot overwrite newer connection/command state.
- [x] Billing business data/action IDs are not persisted in browser storage/WordPress options.
- [x] All strings are localized through WordPress i18n and actionable/status UI is accessible.
- [x] No top-up/refund/purchase-history placeholder control is introduced.
- [x] No Woo vendor credential/provider contract ID/Shopify handle reaches React.
- [x] `docs/architecture/_index.md` is unchanged.

## Validation

Inspect the accepted `moda-interact-woocommerce/package.json`, Composer scripts and ARCH-026 validation instructions before choosing exact commands.

Required validation categories:

- [x] required Woo repository/bootstrap preparation from accepted ARCH-026 instructions;
- [x] JavaScript unit tests;
- [x] PHP unit tests;
- [x] changed-file JS lint;
- [x] CSS lint when styles change;
- [x] PHP lint/code standards;
- [x] production build;
- [x] plugin ZIP build/safety validation when required by repository policy;
- [x] local billing GET PHP-client fixture test;
- [x] local plans GET locale/header/strict-response tests;
- [x] local create/switch/cancel PHP remote-mapping tests;
- [x] test proving PHP sends installation auth but no caller-selected shopId/domain;
- [x] actionId UUID validation + Idempotency-Key forwarding tests;
- [x] confirmation URL allowed-host/rejected-host tests;
- [x] live WordPress REST cookie/nonce smoke for all five local routes (developer-owned integration run below);
- [x] React connection-gating test;
- [x] current Free/paid plan summary tests;
- [x] capacity presentation tests;
- [x] scheduled cancellation presentation test;
- [x] pending plan state tests;
- [x] pending cancellation INITIATING/OUTCOME_UNKNOWN/CONFIRMED presentation tests;
- [x] plan catalogue Free/paid/current/featured rendering tests;
- [x] exact Free->paid create mapping test;
- [x] exact paid->paid switch mapping test;
- [x] paid->Free confirmation/cancel mapping test;
- [x] single-flight command test;
- [x] stale Billing/Plans GET tests;
- [x] Woo confirmation redirect top-level navigation test;
- [x] Woo return marker selects Billing + one refresh and never activates state test;
- [x] no unbounded polling test;
- [x] FROZEN/BILLING_ATTENTION command-disabled tests;
- [x] no browser persistence test;
- [x] no direct hosted API/browser Authorization test;
- [x] no top-up/refund placeholder controls test;
- [x] current WordPress 7.1.2 / WooCommerce 11.1.2 / PHP 8.1 package fresh-install, accepted-baseline upgrade, deactivate/reactivate lifecycle smoke (developer-owned integration run below); minimum-version compatibility is inherited from accepted ARCH-026 prerequisites and was not independently rerun for this task;
- [x] `git diff --check`;
- [x] dedicated parent/implementation worktree, start-of-attempt synchronization and pushed task-branch evidence.

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

Complete and architect-accepted on Attempt 2, after developer-owned WordPress REST integration and package-lifecycle validation passed.

### Files Changed

Implementation worktree (`moda-interact-woocommerce`):

- `composer.json`
- `includes/Api/BillingResponseValidator.php`
- `includes/Api/ModaApiClient.php`
- `includes/Rest/BillingController.php`
- `includes/Runtime.php`
- `src/billing-client.js`
- `src/billing-controller.js`
- `src/billing-screen.js`
- `src/index.scss`
- `src/page.js`
- `tests/BillingApiClientTest.php`
- `tests/BillingControllerTest.php`
- `tests/integration/run-wordpress.mjs`
- `tests/bootstrap.php`
- `tests/js/billing-client.test.js`
- `tests/js/billing-controller.test.js`
- `tests/js/billing-screen.test.js`
- `tests/js/page.test.js`

### Work Completed

- Added strict API-002/API-003 server validation and five privileged local billing routes. Hosted requests use the saved installation credential; action IDs are forwarded only as idempotency headers, and confirmation URLs are restricted to the two approved HTTPS Woo hosts.
- Added an Overview/Billing tab within the existing Woo Admin application, with connected-state gating, plans-on-demand, single-flight/stale-response protection, create/switch/cancel flows, Woo top-level confirmation navigation, and one authoritative refresh on return/cancellation.
- Added localized current-plan, allowance reset, cancellation end, capacity, catalogue, pending-state and accessible cancellation-confirmation presentation. No business state is persisted in browser storage and no future top-up/refund controls were added.
- Added PHP and JavaScript client/controller/presentation/shell regression coverage.
- Extended the Docker-backed WordPress REST integration runner to test unauthenticated and invalid-nonce rejection on all five billing routes, plus authenticated API-002 reads and API-003 create/switch/cancel mappings through its HTTPS fixture.

### Validation Results

- `source "$MODA_WORKSPACE_ROOT/scripts/bootstrap-woocommerce.sh"`: passed during task setup; Node/npm, PHP, Composer and Docker prerequisites were verified.
- `npm run test:js`: passed, 9 files / 70 tests.
- `npm run lint:js`: passed (tool emitted the repository's existing legacy ESLint configuration warning).
- `npm run lint:css`: passed.
- `composer lint`: passed, including the new validator/controller and billing PHP tests.
- `composer test`: passed, 44 tests / 251 assertions. The first parallel full-suite run briefly raced with asset regeneration; the isolated rerun and post-package rerun passed.
- `npm run build`: passed; repeated successfully as part of package verification.
- `npm run package:production`: passed. Archive audit verified 35 entries under the single `moda-interact/` root, required runtime files, no prohibited development/secrets/source maps, and no hosted API origin or credentials in browser runtime. SHA-256: `15c3aeda292a1a9fe7598b75a1de7243876f74a3d82c0f3b5baf114daed3060a`.
- `npm run install:php && composer lint && composer test`: passed after packaging restored development Composer dependencies.
- `node --check tests/integration/run-wordpress.mjs`, `npm run lint:js`, and `npm run test:js`: passed after extending the WordPress integration runner; the full JS suite remains 70/70.
- `git diff --check`: passed.

Developer validation subsequently completed (Docker-backed WordPress integration and packaged lifecycle; not launched by the repository agent):

```sh
npm run test:integration:wordpress
npm run test:integration:package-lifecycle
```

Observed: both required integration commands completed with exit code 0. The package lifecycle exercised the WordPress 7.1.2 / WooCommerce 11.1.2 / PHP 8.1 candidate and an accepted WOO-005 upgrade baseline. These runs do not constitute a separate new cross-version minimum WordPress/WooCommerce UI proof; that broader compatibility work remains with the accepted ARCH-026 baseline and later integrated validation.

### Deviations

- Agent execution deferred the Docker-backed WordPress integration and package-lifecycle tests under `docs/agent-validation-execution-policy.md`; the developer subsequently ran both commands successfully, as recorded in the final validation evidence below.

### Assumptions

- ARCH-026-WOOCOMMERCE-005 provides the accepted Overview/shell/local REST/client structure.
- API-002 includes the companion `pendingCancellation` presentation correction included with this task definition.
- API-003 create/switch confirmation URLs remain provider/server-derived and validated.
- Top-up and purchase/refund UI are intentionally separate tasks to keep the Woo implementation reviewable.

### Unresolved Issues

- No unresolved WOO-001 validation gate remains. Real Woo provider sandbox certification is an external downstream gate, not a claim made by the WordPress fixture results.

### Architectural Concerns

None identified. Browser billing data remains ephemeral; PHP retains hosted API credentials and validates all remote responses before returning bounded data.

### Physical Worktree Isolation and Synchronization

- Canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-027-WOOCOMMERCE-001`, branch `task/ARCH-027-WOOCOMMERCE-001`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-027-WOOCOMMERCE-001`, branch `task/ARCH-027-WOOCOMMERCE-001`.
- Shared workspace checkout switched/mutated for implementation: no. Shared implementation checkout switched/mutated: no. Another task worktree reused: no.
- Prepared launcher completed task-branch synchronization, dependency gate, and recursive submodule synchronization/update before claim. The implementation branch began up to date with `origin/main`; exact start-of-attempt commit IDs remain in the launcher preparation evidence.
- `git submodule sync --recursive` and `git submodule update --init --recursive`: passed during prepared launcher execution; no submodule gitlink change is part of this task.
- Implementation commits `096afd8` (`Add WooCommerce merchant billing hub`) and `39c7623` (`Add live WordPress billing route coverage`) are pushed to `origin/task/ARCH-027-WOOCOMMERCE-001`.
- Parent task/report commit `d12a2cee` (`Record WordPress billing smoke coverage`) is pushed to `origin/task/ARCH-027-WOOCOMMERCE-001`; this final synchronization note is published in the following report commit.

### Attempt 2 Rework (2026-10-09)

- **A1-R1 addressed:** Added a shared `Intl.NumberFormat(locale)` presentation helper and used it for the four capacity quantities and plan included credits. The helper leaves data and API quantities untouched and uses the browser locale when no explicit locale is supplied. Display regressions cover values above 1,000 in `en-US` and `de-DE`, comparing against each locale's `Intl.NumberFormat` output rather than hard-coded separators.
- **A1-R2 addressed:** The cancellation dialog now allows normal Tab and Shift+Tab movement between controls and intercepts only at the first/last focusable control to wrap focus. Initial focus remains on Keep; Escape closes the dialog; dismissal restores focus through the originating Cancel ref; only the explicit confirmation action invokes cancellation. The keyboard regression exercises the dialog's rendered key handler in both directions from both controls, Escape, focus restoration, and Keep-versus-Confirm behavior.
- Focused Billing screen tests: `npm run test:js -- tests/js/billing-screen.test.js` passed, 14/14 tests.
- Full JavaScript suite: `npm run test:js` passed, 9 files / 74 tests.
- `npm run lint:js`: passed; ESLint emitted the repository's existing legacy configuration warning.
- `npm run build`: passed.
- Editor diagnostics for both changed files: no errors. `git diff --check`: passed.
- Implementation commit `58dd7a7` (`task(ARCH-027-WOOCOMMERCE-001): address architect review`) is pushed to `origin/task/ARCH-027-WOOCOMMERCE-001`.
- **A1-R3 at the time of agent resubmission:** Neither Docker-backed integration command had been run by the agent. Both were subsequently executed by the developer and passed; see the final validation evidence below.
- Attempt 2 is submitted with `status: review`, `executor: null`, and `claimed_at: null`. The implementation task worktree is `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-027-WOOCOMMERCE-001`; the parent task worktree is `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-027-WOOCOMMERCE-001`; both use `task/ARCH-027-WOOCOMMERCE-001`. Start-of-attempt task-branch fast-forwards were not needed and both `origin/main` refs were already current. Prepared launcher dependencies and recursive submodule synchronization passed; no shared checkout or implementation gitlink was changed.


### Attempt 2 — Final Developer Integration Evidence (2026-10-09)

- `npm run package:production`: developer regenerated the corrected plugin before the package lifecycle run. The later tested candidate reports plugin `0.1.0` and SHA-256 `65be4dc39432b72d5e0d030d08026e01dc6690cac3985780648275ee80ab4337`; this supersedes the earlier interim rebuilt hash and the old Attempt 1 archive.
- `npm run test:integration:wordpress`: **PASS, exit code 0**, reported from the developer's dedicated WOO-001 implementation worktree. Integration harness corrections addressed the previous HTTP socket closure, WordPress `en_GB` fixture locale and four-field bootstrap international-context readback. These were fixture/HTTP-harness corrections; the production billing UI and PHP contracts were not changed by them.
- `npm run test:integration:package-lifecycle`: **PASS, exit code 0**, reported after fixing the integration harness's fixed host-port collision. Tested WordPress `7.1.2`, WooCommerce `11.1.2`, PHP `8.1`; candidate version `0.1.0`, SHA-256 `65be4dc39432b72d5e0d030d08026e01dc6690cac3985780648275ee80ab4337`; WOO-005 accepted-baseline commit `98273e4ebdfa9a78146cb897fb905ef97a6814e7`.
- The latest published implementation task-branch head inspected by the architect is `f7e8d0ea0d515b826d06b090f9a9206af6122b5f`, which contains the test-harness corrections. The parent completion-report branch previously submitted at `bbb7547205b0d2f4142f635fe0a0c7b2ff448e99`; the final developer evidence is durably recorded in this acceptance amendment.
- Both commands and exit codes are supplied directly by the developer. The architect did not independently execute Docker or inspect the exact final ZIP bytes. The WOO-001 package lifecycle used current WordPress/WooCommerce versions; the earlier ARCH-026 baseline covers packaging compatibility, not an additional new cross-version WOO-001 UI run.

## Architect Review

### Review Status

Accepted — Attempt 2 (2026-10-09). A1-R1 and A1-R2 are source-reviewed and corrected; the developer completed A1-R3 with both required integration commands passing (exit code 0). Task is `complete`.

Historical review status: Changes Requested — Attempt 1 (2026-10-09).

### Review Notes

#### Attempt 2 — final architect acceptance (2026-10-09)

- **A1-R1 Accepted:** Locale-aware capacity and plan quantities are formatted with `Intl.NumberFormat` without changing hosted or persisted numeric contracts. Focused JavaScript display tests passed 14/14; full JavaScript suite passed 74/74 (developer-reported).
- **A1-R2 Accepted:** Cancel confirmation dialog preserves initial Keep focus; Tab and Shift+Tab wrap only at the appropriate edges, Escape dismisses, and focus returns to the originating Cancel control. Cancellation occurs only through explicit confirmation.
- **A1-R3 Accepted:** Developer supplied `npm run test:integration:wordpress` PASS/exit 0 and `npm run test:integration:package-lifecycle` PASS/exit 0 on the corrected WOO-001 worktree. The final package-lifecycle test reports WordPress 7.1.2 / WooCommerce 11.1.2 / PHP 8.1, plugin 0.1.0 and the candidate SHA-256 recorded above. Initial connection, locale and bootstrap test-fixture defects and a package-runner port conflict were corrected and the full commands rerun successfully; no production source rewrite was needed.
- **Published source provenance:** The task-branch implementation head `f7e8d0ea0d515b826d06b090f9a9206af6122b5f` includes the final test-harness corrections, following the previously reviewed billing-screen correction `58dd7a7`. The submitted parent completion-report head is `bbb75472`; the architect acceptance patch records the final developer evidence without making any new implementation commits or merges. Local worktree cleanliness after the final commands has not been independently verified here.
- **Scope and gates:** This accepts the bounded WOO-001 Billing hub, not Woo provider sandbox certification. No schema, Shared package, billing provider-state semantics or `_index.md` changes are part of this acceptance. The latest package SHA is developer-reported, not independently hashed by the architect.
- **Dependency frontier:** API-004 was previously architect-accepted and is `complete` on the canonical parent `main`; marking WOO-001 `complete` satisfies WOO-002's second dependency. Promote WOO-002 to `ready`, subject to the developer reconciling the WOO-001 task branch's stale API-004 task-file copy with canonical main during integration. The receiving task must re-gate dependencies under the normal launcher.

#### Attempt 2 — preliminary architect review (historical, prior to developer validation)

- **A1-R1 — Source correction verified:** `src/billing-screen.js` uses `Intl.NumberFormat(locale)` for the four capacity quantities and plan included credits. No contract quantities are altered. `tests/js/billing-screen.test.js` tests `en-US` and `de-DE` with amounts exceeding 1,000 and compares results using locale-aware `Intl` output.
- **A1-R2 — Source correction verified:** The dialog's Tab handler permits normal movement between controls, wraps Shift+Tab at the first and Tab at the last, and closes on Escape. The source retains initial Keep focus, dismissal focus restoration through the cancel trigger, and explicit-confirmation-only cancellation. The tests exercise the handler and restoration helper. Actual browser focus remains covered by the pending developer integration gate.
- **Submitted validation:** focused JavaScript 14/14, full JavaScript 74/74, lint, build and `git diff --check` are reported passed; the architect inspected source and tests but did not independently rerun the repository's complete test suite.
- **Branch and snapshot provenance:** implementation commit `58dd7a7` and parent report commit `bbb75472` were inspected on their respective published task branches. The submitted source, test and task report Git blob IDs match those remote branches. Submitted task metadata is `status: review`, `attempt: 2`, `executor: null`, `claimed_at: null`.
- **A1-R3 — Required developer evidence outstanding:** both `npm run test:integration:wordpress` and `npm run test:integration:package-lifecycle` remain unchecked. Preserve `status: review` and do not mark the task Complete, accept it, or promote WOO-002 until their exact exit statuses and results are recorded and reviewed.
- **Important package sequencing:** the snapshot's `moda-interact-woocommerce/moda-interact.zip` is the older 35-entry artifact (SHA-256 `15c3aeda292a1a9fe7598b75a1de7243876f74a3d82c0f3b5baf114daed3060a`). Its bundled JS lacks the Attempt 2 focus handler and quantity formatter. `tests/integration/run-package-lifecycle.mjs` reads this existing ZIP rather than building the candidate. Therefore, run `npm run package:production` **first** on the corrected implementation branch; record the newly generated SHA-256, and only then execute both developer-owned integration commands. A lifecycle PASS against the old ZIP does not satisfy A1-R3.
- **Review disposition:** no further source changes requested for A1-R1/A1-R2. The remaining step is developer-owned validation and a final architect review of that evidence. On failure, report the failing command and its output rather than claiming the gate passed.

#### Attempt 1 — original architect review (historical)

- **A1-R1 — Localized quantities (source and tests required):** `moda-interact-woocommerce/src/billing-screen.js` formats currency and dates through `Intl`, but renders `capacity.paidIncluded.remaining`, `capacity.freeLifetime.remaining`, `capacity.promotional.remaining`, `capacity.purchased.available` and `plan.includedRecoveryCredits` using `String(...)`. Requirement R26 mandates locale-aware formatting for displayed numbers. Replace those presentation-only conversions with a shared `Intl.NumberFormat` helper using the administrator/browser locale. Do not alter persisted quantities, API contract fields or arithmetic. Add a focused display regression with values >= 1,000 showing grouping under at least two locales, without brittle assumptions about non-breaking-space separators.
- **A1-R2 — Keyboard modal focus cycle (source and tests required):** `src/billing-screen.js` cancellation `alertdialog` prevents every forward Tab and focuses the Confirm button, trapping forward navigation there. Shift+Tab likewise always focuses Keep. Implement correct focus movement/loop at the first/last focusable controls while retaining initial focus on Keep, Escape to dismiss, and restoration to the originating Cancel button on dismissal. Add a keyboard regression that exercises forward and reverse Tab from both controls, Escape and focus restoration; verify that cancellation still requires explicit confirmation.
- **A1-R3 — Required developer validation (evidence gate; not an agent-execution command):** The task's Validation section leaves `npm run test:integration:wordpress` and `npm run test:integration:package-lifecycle` unchecked. Under `docs/agent-validation-execution-policy.md`, an agent may correctly submit at `review` while these longer developer-owned commands remain pending. They must be run by the developer after the A1-R1/A1-R2 corrections, with actual command, exit status, and pass/failure summary recorded before architect acceptance. If either fails, report evidence rather than marking it passed or blindly retrying.
- Current implementation otherwise follows the bounded PHP server credential and WordPress REST permission boundary, translates browser action IDs into hosted Idempotency-Key, validates Woo confirmation hosts, and respects durable cancellation/return semantics. The 35-entry production ZIP's SHA-256 matches the submitted report. Both dependent hosted API tasks are `complete` in the submitted snapshot.
- The submitted task reached `review` while `executor: copilot` and `claimed_at` were still set. This review clears the stale execution claim so the same task may be reclaimed for Attempt 2; it preserves `attempt: 1` and the entire original Completion Report.

### Reviewed Files

- `moda-interact-woocommerce/includes/Rest/BillingController.php`
- `moda-interact-woocommerce/includes/Api/ModaApiClient.php`
- `moda-interact-woocommerce/includes/Api/BillingResponseValidator.php`
- `moda-interact-woocommerce/src/billing-client.js`
- `moda-interact-woocommerce/src/billing-controller.js`
- `moda-interact-woocommerce/src/billing-screen.js`
- `moda-interact-woocommerce/src/page.js`
- `moda-interact-woocommerce/tests/js/billing-screen.test.js`
- `moda-interact-woocommerce/tests/integration/run-wordpress.mjs`
- `moda-interact-woocommerce/moda-interact.zip`
- Canonical task, ARCH-027 parent architecture, API-002 and API-003 dependency task documents, Completion Report.

### Validation Reviewed

- Independently checked PHP syntax for the affected API/REST files and tests, plus JavaScript syntax for billing files and WordPress test runner: passed.
- Independently checked the submitted 35-entry plugin ZIP integrity, top-level `moda-interact/` root and SHA-256 `15c3aeda292a1a9fe7598b75a1de7243876f74a3d82c0f3b5baf114daed3060a`: passed.
- Reported agent execution: 70 JavaScript tests; 44 PHP tests / 251 assertions; JS/CSS/PHP lint; production build and package audit — submitted as passing evidence, not independently rerun.
- Developer-owned WordPress REST integration: **PASS (exit 0)**. Developer-owned packaged fresh-install/upgrade/deactivate/reactivate lifecycle: **PASS (exit 0)** on WordPress 7.1.2 / WooCommerce 11.1.2 / PHP 8.1, candidate 0.1.0 SHA-256 `65be4dc39432b72d5e0d030d08026e01dc6690cac3985780648275ee80ab4337`. The architect reviewed the developer-provided output; did not rerun Docker.
- Implementation commits `096afd8` and `39c7623`, parent task status/provenance and corresponding GitHub branches inspected.

### Architecture Conformance

- PHP installation-authentication/tenant isolation, hosted API mapping, Woo URL restrictions, no-browser-storage and provider-command semantics appear conformant in inspected source.
- R26 quantity internationalization and cancellation-dialog keyboard accessibility were corrected in Attempt 2 and covered by focused tests. Required WordPress REST and candidate package-lifecycle runs now pass. No durable billing-state change is authorized by these presentation/test-harness corrections.
- No new cross-repository schema, Shared contract, provider logic, or Gateway work is authorized as part of these corrections.

### Follow-up

- Attempt 1 Changes Requested disposition and the earlier Attempt 2 preliminary review are retained above as history; all A1-R1/R2/R3 correction gates are now satisfied.
- Mark `ARCH-027-WOOCOMMERCE-001` complete, retaining Attempt 2 and cleared claim fields. Promote `ARCH-027-WOOCOMMERCE-002` to ready based on WOO-001 acceptance and the previously accepted API-004 prerequisite on canonical main; normal task-launch preparation must re-check the fully reconciled dependency state.
- Keep ARCH-027 Proposed until remaining implementations and terminal system tests finish. No `docs/decisions/**/_index.md` modifications.
