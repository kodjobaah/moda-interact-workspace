---
id: ARCH-001
title: Shopify checkout recovery webhook processing
status: agreed
coordinator: moda_architect
created: 2026-08-28
updated: 2026-08-28
---

# ARCH-001 Amendment: Bounded Shopify Abandoned-Checkout Lookup

## Status

**Agreed**

This amendment resolves the architectural block discovered while implementing:

`ARCH-001-BACKGROUND-003`

The remainder of ARCH-001 is unchanged.

## Discovery

Shopify does not provide a direct Admin API lookup of an abandoned checkout using:

- `checkoutToken`;
- `cartToken`;
- `abandonedCheckoutUrl`;
- `checkoutCreatedAt`.

The public Admin GraphQL API exposes abandoned checkouts through the paginated:

`abandonedCheckouts`

connection.

However, ARCH-001 does not prohibit bounded listing. It prohibits an unbounded scan of a merchant's abandoned-checkout history.

Shopify supports server-side filtering of `abandonedCheckouts` by `created_at`.

The returned `AbandonedCheckout` includes:

- `abandonedCheckoutUrl`;
- `createdAt`;
- the current checkout/customer/line-item/pricing data required by recovery.

The existing `PendingRecoveryCandidate` already contains:

```text
shopId
checkoutToken
cartToken
abandonedCheckoutUrl
checkoutCreatedAt
```

No additional shared-contract identifier is required for this lookup.

## Revised Lookup Decision

When a pending candidate matures, `moda-interact-background` must perform a bounded lookup.

```text
PendingRecoveryCandidate
        |
        v
checkoutCreatedAt
        |
        v
build narrow Shopify created_at filter
        |
        v
bounded abandonedCheckouts query
        |
        v
exact match on abandonedCheckoutUrl
        |
    +---+---+
    |       |
   one     zero / multiple /
  match    bound exceeded
    |       |
    v       v
 return    safe non-success
 checkout  outcome
```

## Bounding Rule

The lookup must never page through an unbounded abandoned-checkout history.

The implementation must:

1. derive the Shopify `created_at` filter from `checkoutCreatedAt`;
2. enforce a hard maximum number of candidate records that may be inspected;
3. stop/fail safely when that bound would be exceeded;
4. perform an exact match using `abandonedCheckoutUrl`;
5. never fall back to customer/email/name-only heuristics.

The repository implementation may use either:

- an `abandonedCheckoutsCount` pre-check followed by the bounded query; or
- another demonstrably bounded mechanism supported by the configured Shopify API version.

The exact page size/time-window mechanics are repository implementation details, provided they satisfy the hard bound and exact URL matching requirements.

## Match Outcomes

### Exactly one URL match

Return the current Shopify abandoned checkout.

This result may then be used by ARCH-001-BACKGROUND-004 to populate `CheckoutRecovery`.

### No URL match

Return a non-success lookup outcome.

Do not create recovery from the old webhook snapshot.

### Multiple exact URL matches

Treat as an invalid/ambiguous provider result.

Do not guess.

### Candidate bound exceeded

Treat as a bounded-lookup failure.

Do not continue paging.

Do not perform an unbounded scan.

### Shopify/API failure

Treat as a transient provider failure where appropriate.

Do not convert provider failure into "checkout not recoverable".

## Why No New Contract Task Is Required

`abandonedCheckoutUrl` is already part of the approved `PendingRecoveryCandidate`.

`checkoutCreatedAt` is already part of the approved `PendingRecoveryCandidate`.

Therefore the discovered API limitation does not require:

- a new shared contract version;
- a new Shopify webhook field;
- a new database field;
- a new cross-repository task.

The architectural correction remains within the original objective of `ARCH-001-BACKGROUND-003`.

## Task State Change

`ARCH-001-BACKGROUND-003` may transition:

```text
blocked -> ready
```

after its task definition is updated to this bounded lookup strategy.

The background agent must claim it again before resuming implementation.

## Change History

### 2026-08-28

`ARCH-001-BACKGROUND-003` was blocked after confirming there is no direct Shopify abandoned-checkout lookup by checkout/cart token or recovery URL.

Architecture amended to use:

```text
bounded created_at-filtered abandonedCheckouts query
    +
exact abandonedCheckoutUrl match
```

No new cross-service contract was introduced.
