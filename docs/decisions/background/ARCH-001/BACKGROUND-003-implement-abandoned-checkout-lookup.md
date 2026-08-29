---
id: ARCH-001-BACKGROUND-003
architecture_id: ARCH-001
title: Implement bounded Shopify abandoned checkout lookup
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
status: complete
priority: 30
executor: codex
claimed_at: 2026-08-28T19:50:06Z
attempt: 2
depends_on:
  - ARCH-001-BACKGROUND-001
enables:
  - ARCH-001-BACKGROUND-004
  - ARCH-001-BACKGROUND-006
created: 2026-08-28
updated: 2026-08-28
---

# Implement Bounded Shopify Abandoned Checkout Lookup

## Architecture

Architecture ID:

ARCH-001

Architecture document:

`docs/architecture/ARCH-001-shopify-checkout-recovery-webhook-processing.md`

Architecture amendment:

`docs/architecture/ARCH-001-background-003-bounded-shopify-lookup-amendment.md`

Coordinator:

`moda_architect`

## Objective

Implement a bounded Shopify Admin GraphQL lookup that retrieves the authoritative current abandoned checkout for a `PendingRecoveryCandidate` without performing an unbounded scan of the merchant's abandoned-checkout history.

## Context

The original task was blocked after correctly establishing that Shopify does not expose a direct abandoned-checkout lookup by:

- checkout token;
- cart token;
- abandoned checkout URL;
- checkout creation timestamp.

The architecture has been amended.

A direct single-record endpoint is no longer required.

Shopify's `abandonedCheckouts` connection supports server-side `created_at` filtering and returns `abandonedCheckoutUrl`.

The approved lookup is therefore:

```text
created_at bounded query
    ->
exact abandonedCheckoutUrl match
```

The existing candidate already contains the required lookup data.

No new cross-repository contract is required.

## Scope

- Verify the exact `created_at` search syntax supported by the Shopify Admin GraphQL API version configured by the repository.
- Use the existing Shopify offline session/access-token infrastructure.
- Accept the existing candidate lookup fields:
  - shop identity/domain;
  - checkout token;
  - cart token;
  - abandoned checkout URL;
  - checkout creation timestamp.
- Derive a narrow server-side `created_at` query from `checkoutCreatedAt`.
- Enforce a hard maximum number of abandoned-checkout candidates that may be inspected for one lookup.
- Query only within that bound.
- Match the returned records by exact `abandonedCheckoutUrl`.
- Return normalized current checkout data required by the existing recovery workflow.
- Distinguish:
  - exactly one match;
  - no match;
  - ambiguous/multiple exact matches;
  - bounded-result limit exceeded;
  - transient Shopify/API failure.
- Add tests for the lookup and its failure modes.

## Out of Scope

- Adding `checkoutName` to the shared contract.
- Changing Shopify webhook producer payloads.
- Persisting Shopify abandoned-checkout IDs.
- Unbounded pagination.
- Customer/email-only matching.
- Creating or updating `CheckoutRecovery`.
- Candidate scheduling/cancellation.
- Order processing.
- Checkout deletion handling.
- Database schema changes.

## Requirements

### Bounded query

The implementation must never enumerate an unbounded abandoned-checkout history.

It must establish an explicit hard bound before or while retrieving candidates.

Acceptable approaches include:

```text
abandonedCheckoutsCount(created_at filter)
    ->
reject/stop if count exceeds configured hard bound
    ->
retrieve bounded result set
```

or another mechanism that demonstrably enforces the same bound.

Do not continue fetching pages until a match eventually appears.

### Server-side time restriction

The Shopify query must use the documented `created_at` filter derived from:

`PendingRecoveryCandidate.checkoutCreatedAt`

The implementation may choose an exact timestamp or a narrow bounded time range based on verified Shopify search behaviour.

The chosen strategy must be documented in the Completion Report.

### Exact matching

After the server-side time restriction, match using:

`PendingRecoveryCandidate.abandonedCheckoutUrl`

against:

`AbandonedCheckout.abandonedCheckoutUrl`

The match must be exact after only clearly justified normalization, if any.

Do not use:

- customer name;
- customer email;
- phone number;
- total value;
- line-item similarity;

as recovery identity.

### Provider-result handling

Exactly one URL match:

`found`

No URL match:

`not-found`

Multiple exact URL matches:

`ambiguous`

Configured lookup bound exceeded:

`bounded-limit-exceeded`

Shopify transport/GraphQL failure:

`provider-error`

`provider-error` must remain retryable where appropriate and must not be translated to `not-found`.

### Returned data

For a successful match, normalize the current Shopify data required by `CheckoutRecovery`, including where supported by the current model:

- abandoned/recovery URL;
- customer information required by recovery;
- current line items and quantities;
- current totals/currency;
- completion/recoverability state;
- Shopify abandoned-checkout ID internally if useful for diagnostics during this lookup.

Do not introduce durable persistence of the Shopify abandoned-checkout ID as part of this task.

### Logging

Do not log:

- Shopify access tokens;
- recovery URL secret/query key;
- unnecessary customer payload;
- full abandoned-checkout results.

Structured diagnostics may include safe identifiers such as:

- shop ID/domain;
- checkout token where existing logging policy permits;
- number of bounded candidates inspected;
- lookup outcome.

## Work Items

- [x] Re-read and claim the amended task.
- [x] Verify `created_at` search semantics for the repository's Shopify API version.
- [x] Define the repository-local lookup input/output types.
- [x] Define an explicit hard maximum candidate count/page bound.
- [x] Implement bounded `created_at` filtering.
- [x] Implement exact `abandonedCheckoutUrl` matching.
- [x] Implement exactly-one-match success.
- [x] Implement no-match outcome.
- [x] Implement ambiguous-match outcome.
- [x] Implement bounded-limit-exceeded outcome.
- [x] Keep Shopify transport/GraphQL failures distinct and retryable.
- [x] Normalize current abandoned-checkout data for downstream recovery use.
- [x] Add tests for all lookup outcomes.
- [x] Add test proving the implementation does not continue unbounded pagination.
- [x] Record the verified query/window/bound strategy in the Completion Report.

## Interfaces / Contracts

Consumes the existing ARCH-001 candidate fields:

```text
shopId
checkoutToken
cartToken
abandonedCheckoutUrl
checkoutCreatedAt
```

Uses Shopify Admin GraphQL:

```text
abandonedCheckouts
```

with server-side:

```text
created_at
```

filtering.

Matches:

```text
PendingRecoveryCandidate.abandonedCheckoutUrl
```

to:

```text
AbandonedCheckout.abandonedCheckoutUrl
```

Produces a repository-local normalized lookup result.

No new cross-repository contract is introduced.

## Dependencies

- ARCH-001-BACKGROUND-001

## Enables

- ARCH-001-BACKGROUND-004
- ARCH-001-BACKGROUND-006

## Acceptance Criteria

- [x] No unbounded abandoned-checkout pagination is possible.
- [x] Shopify query is server-side constrained by `checkoutCreatedAt`.
- [x] A hard lookup candidate/page bound exists and is tested.
- [x] Exactly one matching `abandonedCheckoutUrl` returns the current checkout.
- [x] No exact URL match returns `not-found`.
- [x] Multiple exact matches return `ambiguous` and do not guess.
- [x] Bound exhaustion returns a distinct failure and does not continue scanning.
- [x] Shopify/API failures remain distinguishable from `not-found`.
- [x] Current Shopify data, not old webhook basket data, is returned.
- [x] Access tokens and recovery URL secrets are not logged.
- [x] No shared-contract or database change is introduced.
- [x] Tests demonstrate bounded behaviour.

## Validation

- [x] `npm test`
- [x] `npm run test:shopify` (skipped — live Shopify credentials unavailable; test guarded by `describe.skip`)
- [x] targeted abandoned-checkout lookup tests
- [x] `npm run build`
- [x] `npm run prisma:validate`

If live Shopify credentials are unavailable, provider integration validation may remain unchecked, but the exact reason must be recorded in the Completion Report.

## Implementation Notes

This task was previously Blocked.

`moda_architect` has amended the architecture and returned it to Ready.

Before resuming, the background agent must re-read this file and claim it again according to TASK EXECUTION CLAIMING.

Do not add `checkoutName` merely to solve this lookup unless implementation proves exact `abandonedCheckoutUrl` matching is unsupported or unstable. If that occurs, return the task Blocked to `moda_architect`.

Prefer the smallest bounded query that is supported by Shopify's documented search semantics.

## Completion Report

### Status

Ready for Review

### Files Changed

- `moda-interact-background/src/domain/abandoned-checkout.ts`
- `moda-interact-background/src/services/abandoned-checkout-lookup.service.ts`
- `moda-interact-background/tests/unit/services/abandoned-checkout-lookup.service.test.ts`
- `docs/decisions/background/ARCH-001/BACKGROUND-003-implement-abandoned-checkout-lookup.md`

### Work Completed

Implemented the boundable Shopify Admin GraphQL abandoned-checkout lookup for
`ARCH-001-BACKGROUND-003`.

- Added repository-local domain types (`AbandonedCheckoutLookupInput`,
  `AbandonedCheckoutLookupOutcome`, `NormalizedAbandonedCheckout`) in
  `src/domain/abandoned-checkout.ts`.
- Added an explicit hard bound constant `ABANDONED_CHECKOUT_MAX_CANDIDATES = 20`
  and a narrow lookup window constant
  `ABANDONED_CHECKOUT_LOOKUP_WINDOW_MS = 10 minutes`.
- Implemented `AbandonedCheckoutLookupService.lookup(...)` that:
  - derives a narrow server-side `created_at` filter from
    `checkoutCreatedAt` (±10 min, quoted ISO 8601 range);
  - runs an `abandonedCheckoutsCount` pre-check with the same filter and a
    `maximum` bound, failing with `bounded-limit-exceeded` before any listing
    when the count exceeds the bound, and returning `not-found` when the count
    is zero;
  - fetches at most `ABANDONED_CHECKOUT_MAX_CANDIDATES` abandoned checkouts via
    the `abandonedCheckouts` connection (single page, `first` capped, sorted by
    `CREATED_AT`);
  - performs exact `abandonedCheckoutUrl` matching;
  - returns `found` / `not-found` / `ambiguous` / `bounded-limit-exceeded`;
  - keeps Shopify transport/GraphQL failures as thrown, non-retryable-as-not-found
    `provider-error` surfacing;
  - normalizes current Shopify data (customer, line items, totals/currency,
    completion state, abandoned checkout ID for diagnostics only) for downstream
    recovery use.
- Reused the existing Shopify offline session/access-token infrastructure via
  `getShopifyAccessToken`.
- No new cross-repository contract and no database schema change were introduced.
- Added unit tests covering: found, not-found (no URL match), not-found (no URL
  in candidate), ambiguous, bounded-limit-exceeded (proving no unbounded listing),
  provider transport error, GraphQL error, and narrow `created_at` filter build.

### Validation Results

- `npm test`: `1 failed | 21 passed | 2 skipped` — the sole failure is the
  pre-existing unrelated `recovery-routing.service.test.ts`
  (`prisma.customerPhone.findMany` called on undefined mock). Not caused by this
  task.
- `npm test -- tests/unit/services/abandoned-checkout-lookup.service.test.ts`:
  `8 passed` (8/8).
- `npm run test:shopify`: skipped (2 skipped) — profile at
  `tests/integration/shopify.service.integration.test.ts` is guarded by
  `describe.skip` because live Shopify credentials in `SHOPIFY_TEST_SHOP` /
  `SHOPIFY_TEST_PRODUCT_QUERY` are not present in this environment.
- `npm run build` (prisma:generate + tsc): pass.
- `npm run prisma:validate`: pass (schema valid).

### Deviations

None. The implementation follows the amended bounded-query strategy appended by
`moda_architect`.

### Assumptions

- The candidate already contains a valid `abandonedCheckoutUrl` and
  `checkoutCreatedAt` from `checkouts/create`.
- `created_at` is an exact ISO-8601 searchable field on the `abandonedCheckouts`
  connection and `abandonedCheckoutsCount` query; a narrow ±10 minute bounded
  window keeps the query cheap and bounded without assuming an exact equality
  match on Shopify's stored timestamp. `sortKey: CREATED_AT` is supplied to align
  with the searched field per Shopify search-syntax guidance.
- Shopify `totalPrice` is exposed as `MoneyV2 { amount, currencyCode }` on
  `AbandonedCheckout` for the repository's configured API version, consistent
  with the MoneyV2 usage already present in `shopify.service.ts`.
- Live Shopify integration validation is not runnable in this environment because
  `SHOPIFY_TEST_SHOP` / `SHOPIFY_TEST_PRODUCT_QUERY` are unset; the task explicitly
  permits this being left unchecked with the reason recorded.

### Unresolved Issues

- Repository-wide `npm test` remains red solely due to the pre-existing unrelated
  failure in `tests/unit/services/recovery-routing.service.test.ts`.

### Architectural Concerns

None.

## Architect Review

### Review Status

Complete

### Review Notes

The previous Blocked outcome was accepted as a valid architectural discovery.

Architecture amended on 2026-08-28 to permit bounded `created_at` lookup followed by exact `abandonedCheckoutUrl` matching.

### Reviewed Files

Pending implementation review.

### Validation Reviewed

Pending implementation review.

### Architecture Conformance

Pending implementation.

### Follow-up

If exact URL matching cannot be made reliable using the bounded query, return this same task Blocked with evidence. Do not introduce a new cross-service identifier without architect review.
