---
id: ARCH-008
title: Shopify App Pricing conformance and Admin billing progressive disclosure
status: Agreed
coordinator: moda_architect
created: 2026-09-09
updated: 2026-09-09
---

# ARCH-008: Shopify App Pricing conformance and Admin billing progressive disclosure

## Status

Agreed.

This is a **pre-production correction architecture**. ARCH-008 preserves the ARCH-007 commercial model and corrects both the asynchronous Shopify App Events boundary and the Admin presentation of billing state.

## Decision

Moda Interact will use **Shopify App Pricing** (formerly Managed Pricing), not Manual Pricing.

The current product model is representable with Shopify App Pricing:

- one Free plan;
- Starter / Growth / Scale monthly plans;
- recurring + usage pricing;
- included usage allowances;
- usage App Events;
- recovery-credit packs represented as repeatable usage units on a dedicated Shopify App Pricing meter.

Moda must continue to avoid introducing a second/legacy billing architecture through `appSubscriptionCreate`, `appPurchaseOneTimeCreate`, `billing.request`, Billing API charge webhooks or `charge_id`-based state.

### Manual Pricing reconsideration trigger

Revisit Manual Pricing only if a future product requirement cannot be represented by Shopify App Pricing and the benefit justifies a legacy Billing API integration. A true requirement for a synchronous, merchant-approved, individually callback-confirmed one-time purchase would be such a trigger. That is not the ARCH-008 product decision.

## Shopify references

- Shopify App Pricing: https://shopify.dev/docs/apps/launch/billing/shopify-app-pricing
- Billing pricing-method selection: https://shopify.dev/docs/apps/launch/billing
- Manual Pricing: https://shopify.dev/docs/apps/launch/billing/manual-pricing
- Combined recurring + usage: https://shopify.dev/docs/apps/launch/billing/shopify-app-pricing/subscription-billing/combined-subscription-and-usage
- Migration to Shopify App Pricing: https://shopify.dev/docs/apps/launch/billing/shopify-app-pricing/migrating-to-shopify-app-pricing
- App Events API: https://shopify.dev/docs/api/app-events/2026-07
- Build a Billing Event: https://shopify.dev/docs/apps/launch/billing/shopify-app-pricing/subscription-billing/build-billing-event
- Partner Active Subscription: https://shopify.dev/docs/api/partner/latest/active-subscription

## Problem

ARCH-007 selected the correct billing architecture but two correction areas remain.

### 1. App Events receipt is not billing confirmation

A successful App Events request means Shopify received the event. Billing validation is asynchronous. Moda currently has a path in which transport success can cause a recovery-credit purchase to become ACTIVE. That is too strong.

Shopify provides current-cycle usage quantity through Partner `activeSubscription`, but that quantity is aggregate. Shopify does not expose the App Events idempotency key as a per-event billing-confirmation callback/API. Moda must therefore reconcile aggregate provider quantity without fabricating individual provider confirmation.

### 2. Admin billing surfaces expose implementation detail before business state

The supplied Admin implementation renders the global Billing catalogue, operational App Event ledger, plan forms and platform controls on one long surface. Tenant Directory -> Billing similarly renders subscription, usage internals, policy override, Shopify reconciliation and the full App Event ledger simultaneously.

A new platform operator should be able to answer simple questions first:

- What plan is active?
- Is billing healthy?
- How much allowance remains?
- Is a pack still awaiting Shopify confirmation?
- Is there an issue that needs attention?

Low-level event handles, provider response summaries, retry attempts and policy internals remain necessary for support/debugging but should be revealed on demand.

## Goals

1. Preserve Shopify App Pricing as the sole commercial billing architecture.
2. Define App Events `202` / local `REPORTED` as **submitted to Shopify**, not individual billing validation success.
3. Treat App Events `409` as retryable using the same permanent idempotency key.
4. Prevent recovery-credit capacity from being granted from transport acknowledgement alone.
5. Reconcile recovery-credit packs against current-cycle provider pack-meter quantity from Partner `activeSubscription`.
6. Match provider-confirmed aggregate units deterministically and exactly once; fail closed when partial matching is ambiguous.
7. Keep normal recovery and customer messaging independent of provider reconciliation latency.
8. Make Admin wording faithfully reflect asynchronous Shopify semantics.
9. Replace Admin billing information overload with tabbed progressive disclosure.
10. Use right-side drawers for low-frequency detail/edit/diagnostic interactions.
11. Preserve existing authorization, server-side data access, i18n, pagination, billing calculations and mutation semantics.
12. Make implementation tasks deterministic enough that a GPT-5.6 Luna repository agent should not need to invent architecture during execution.

## Non-Goals

- Migrating to Manual Pricing.
- Rebuilding Shopify's hosted pricing page.
- Introducing `appPurchaseOneTimeCreate` for recovery packs.
- Adding a new database model at the design baseline.
- Adding a second billing provider client in Admin.
- Scraping the Shopify Dev Dashboard.
- Inventing an unsupported App Events failure webhook.
- Treating Partner aggregate usage as if it identifies a specific App Event.
- Redesigning billing calculations, plan economics or entitlement formulas.
- Redesigning Tenant Administration or Recovery Logs outside the Billing sub-surface.
- Introducing a new UI framework or drawer/navigation state library.

## Current Architecture

### Background billing boundary

The inspected background snapshot contains:

- `src/providers/shopify-app-events.provider.ts` posting to App Events and classifying HTTP/provider failures;
- `src/services/shopify-usage-event-publisher.service.ts` marking successful submissions `REPORTED` and invoking recovery-credit activation;
- `src/services/recovery-credit-purchase.service.ts` granting purchased credits when the linked UsageEvent is `REPORTED`;
- durable `UsageEvent`, `RecoveryCreditPurchase`, billing-period and entitlement-counter state.

Accepted ARCH-007 work also defines Partner Active Subscription reconciliation. Because the supplied snapshot may lag the integrated workspace, ARCH-008 tasks must verify the accepted reconciliation capability after synchronising the real task worktree instead of reimplementing it from the snapshot.

### Admin billing boundary

The inspected Admin snapshot currently has:

- `src/app/(protected)/billing/page.tsx` loading plans, policy, overview and ledger together;
- `src/components/admin/billing-plan-catalog.tsx` rendering registration plus every plan as an expanded form;
- `src/components/admin/billing-overview.tsx` rendering global metric cards and a wide App Event ledger;
- `src/components/admin/tenant-billing.tsx` rendering all tenant billing sections and a wide ledger in one stack;
- `src/lib/admin/billing.ts` owning protected server-side billing read models;
- `src/lib/admin/query.ts` providing query-param update helpers;
- an existing right-side `RecoveryDrawer` pattern using URL query parameters and `<Link>` navigation.

ARCH-008 reuses these existing boundaries instead of creating a second Admin billing application.

## Proposed Architecture

### App Events state meaning

Keep the current database enum.

```text
PENDING -> IN_FLIGHT -> REPORTED
```

ARCH-008 semantic contract:

```text
REPORTED = submitted/received by Shopify App Events with the durable idempotency identity.
REPORTED != Shopify individually confirmed the event as billable.
```

`reportedAt` remains the durable field name for compatibility but is presented as **Submitted at**.

### Recovery-credit pack confirmation

```text
RecoveryCreditPurchase PENDING_BILLING
        |
        v
linked +1 pack UsageEvent PENDING
        |
        v
App Events request
        |
        +-- synchronous/retryable failure --> existing retry/attention lifecycle
        |
        +-- 202 --> UsageEvent REPORTED (submitted only)
                      |
                      v
            purchase remains PENDING_BILLING
                      |
                      v
Partner activeSubscription current-cycle pack-meter usage.quantity
                      |
                      v
provider confirmed aggregate units - already activated current-cycle units
                      |
                      v
safe deterministic local matching
                      |
                      +-- safe --> activate exactly confirmed eligible purchases once
                      |
                      +-- ambiguous/inconsistent --> grant nothing ambiguous; surface attention
```

The provider quantity is an accounting aggregate, not proof that a named idempotency key passed billing validation.

### Global Admin Billing information architecture

Route remains the existing protected `/billing` page. Internal view selection is URL-backed:

```text
?view=overview|plans|packs|events|controls
```

Default: `overview`.

Required tabs:

1. **Overview** — compact business/health summary only.
2. **Plans** — compact catalogue; register/edit actions in right-side drawers.
3. **Recovery packs** — bounded purchase list; details in a drawer.
4. **App Events** — compact operational ledger; provider diagnostics in a drawer.
5. **Controls** — existing platform billing policy controls only.

Do not load all tab-specific datasets for every request merely to keep hidden sections mounted. Server code should load the selected tab's required data plus any selected drawer detail.

### Tenant Directory -> Billing information architecture

Keep the current top-level tenant navigation:

```text
Administration | Recovery Logs | Billing
```

Inside Billing use URL-backed subviews:

```text
?billingView=overview|usage|shopify|activity
```

Default: `overview`.

Required sub-tabs:

1. **Overview** — current plan, status, period, remaining usage, pending change, billing health/override warning.
2. **Usage** — entitlement counters and advanced limits.
3. **Shopify** — observed/pending provider plan, sync state and reconciliation/discrepancy information.
4. **Activity** — recovery-pack activity + compact App Event ledger; detail drawers on demand.

An absent billing-policy override must not consume a large card. Display `Default policy` as a concise line. Active overrides receive a visible warning; historical/advanced override details belong behind progressive disclosure.

### Drawer contract

Use the Admin's existing server/query-param drawer interaction pattern:

- `<Link>` changes a query parameter;
- an overlay and right-side `<aside>` render server-side;
- close removes only the drawer-selection parameter;
- browser back/forward and copied deep links preserve state;
- no new client-state library is introduced.

Global Billing creates reusable drawer shell/detail components in `ARCH-008-ADMIN-002`. Tenant Billing reuses them in `ARCH-008-ADMIN-003`, which is why the UI tasks are serialised.

## Data Model

No schema change is authorised at the design baseline.

Existing durable concepts remain authoritative:

- `UsageEvent`
- `RecoveryCreditPurchase`
- `BillingPeriod`
- plan/policy state
- entitlement counters

If exact current-cycle pack-meter matching cannot be implemented from the accepted integrated state without adding a durable identity/constraint, `ARCH-008-BACKGROUND-002` must stop and return the concrete schema/producer gap to `moda_architect`. Background may not silently edit the database repository.

## Contracts

No new cross-repository shared package contract is planned.

Important semantic contracts:

### App Events submission

Owner: `moda_background`

```text
HTTP 202 -> local REPORTED = submitted/received
HTTP 409 -> retryable, same permanent idempotency key
```

### Provider pack-meter reconciliation

Owner: `moda_background`

Input: Partner Active Subscription current billing cycle + exact configured pack meter + provider `usage.quantity`.

Output: bounded local purchase activation/attention result. No per-event provider confirmation is claimed.

### Admin read/presentation

Owner: `moda_admin`

Admin consumes durable billing state; it must not perform Shopify billing writes or create independent billing truth.

## Consistency and Transactions

- Permanent App Events idempotency identity is preserved across retries.
- Recovery-credit activation remains exactly-once at the durable counter/purchase transaction boundary.
- `REPORTED` alone is insufficient for pack activation.
- Reconciliation is replay-safe.
- Provider aggregate under-count does not revoke already-active credits automatically.
- Provider aggregate over-count is surfaced; Moda does not fabricate local purchases.
- Ambiguous partial pack matching grants no ambiguous credits.

## Failure Handling

- 409/429/transient/server/transport App Events failures remain retryable according to the existing bounded retry policy.
- Synchronous non-retryable provider/configuration failures use existing attention state.
- Asynchronous App Events validation failures cannot be assigned an invented exact provider error code because Shopify does not expose such a callback/API.
- Persistent local/provider mismatch is operationally visible.
- Admin does not turn provider diagnostics into browser secrets.

## Security

- Existing platform-admin authorization stays server-side.
- Tenant Billing detail reads remain scoped to the selected tenant.
- Do not expose Shopify access tokens, App Events client secrets, Partner credentials or authorization headers.
- Drawers may show existing safe identifiers/response summaries but not raw secret-bearing provider payloads.

## Observability

No new telemetry mechanism is required by this architecture. Existing durable diagnostics and Admin operational presentation are sufficient at the design baseline. Do not introduce custom metrics merely to drive the redesigned UI.

## Infrastructure Assessment

No Render/gateway/topology/environment change is required. No `moda_gateway` task is created.

## Rollout / Migration

Classification: **pre-production correction**.

Expected order:

1. correct App Events submission/retry semantics;
2. correct pack provider-confirmation lifecycle;
3. add shared Admin billing read/presentation primitives;
4. simplify global Admin Billing;
5. simplify Tenant Billing inspection;
6. developer manual validation;
7. terminal system-test validation.

No database migration is planned. If a schema gap is proven, stop and re-plan before implementation continues.

## Decisions / Tasks

| Task | Repository | Purpose |
|---|---|---|
| `ARCH-008-BACKGROUND-001` | moda-interact-background | Correct App Events receipt/409 retry semantics without changing entitlement confirmation yet. |
| `ARCH-008-BACKGROUND-002` | moda-interact-background | Remove pack activation from 202 and reconcile provider-confirmed aggregate pack units. |
| `ARCH-008-ADMIN-001` | moda-interact-admin | Establish accurate asynchronous billing labels plus bounded safe read primitives used by redesigned surfaces. |
| `ARCH-008-ADMIN-002` | moda-interact-admin | Replace global Billing information overload with five URL-backed tabs and detail drawers. |
| `ARCH-008-ADMIN-003` | moda-interact-admin | Replace Tenant Directory Billing information overload with four URL-backed sub-tabs and reused drawers. |
| `ARCH-008-SYSTEM-TEST-001` | moda-interact-system-test | Terminal/manual-gated integrated validation of App Pricing semantics and Admin progressive disclosure. |

## Dependency Graph

```text
BACKGROUND-001
    |
    v
BACKGROUND-002
    |
    v
ADMIN-001
    |
    v
ADMIN-002
    |
    v
ADMIN-003
    |
    v
SYSTEM-TEST-001
```

System test is terminal. No implementation task depends on it.

## Luna deterministic-execution rule

Every ARCH-008 task is an implementation specification, not an invitation to redesign.

An implementation agent must:

1. follow the explicit architecture and file/behavior boundaries;
2. reuse named existing capabilities when present;
3. not broaden scope to adjacent cleanup;
4. not invent a database/provider/shared contract when the task says to stop;
5. run the exact task validation after inspecting `package.json` to confirm scripts still exist;
6. return to `review` and stop after the assigned task.

If synchronised source materially differs from the inspected baseline such that an explicit instruction is impossible or unsafe, stop with the exact conflicting file/capability and return to `moda_architect`.
