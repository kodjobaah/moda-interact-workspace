# ARCH-010 SHARED-007 consumer sequencing correction

Date: 2026-09-12  
Coordinator: `moda_architect`

## Decision

SHARED-007 was correctly blocked on Attempt 1 because first-party Background and Shopify
consumers still depended on contracts it needed to remove.

Because ARCH-010 is pre-production, the resolution was to remove consumers first rather
than retain compatibility aliases.

## Corrected dependency order

```text
published Shared 0.10.0
        |
        +--> ARCH-010-BACKGROUND-020
        |
        +--> ARCH-010-SHOPIFY-024
                  |
                  v
         both Accepted Complete
                  |
                  v
         ARCH-010-SHARED-007 Attempt 2
                  |
                  v
         ARCH-010-SHARED-008 publish 0.11.0
                  |
                  v
         broader repository baseline-conformance + feature tasks
```

## Completed consumer cleanup

```text
ARCH-010-BACKGROUND-020   Complete
ARCH-010-SHOPIFY-024      Complete
```

Accepted cleanup established:

```text
Background local cancellation executor removed
Background retired cancellation-contract consumers = 0
Background BILLING_FREE_ALLOWANCE_EXHAUSTED consumers = 0
Background BILLING_PLAN_CHANGE_ACTION_REQUIRED consumers = 0
Shopify BILLING_FREE_ALLOWANCE_EXHAUSTED consumers = 0
Shopify BILLING_PLAN_CHANGE_ACTION_REQUIRED consumers = 0
```

## SHARED-007 accepted

```text
ARCH-010-SHARED-007
status: Complete
attempt: 2
```

Accepted result:

```text
retired cancellation mode/provider exports removed
retired local cancellation message codes removed
BILLING_FREE_ALLOWANCE_EXHAUSTED removed
BILLING_PLAN_CHANGE_ACTION_REQUIRED removed
no compatibility aliases/re-exports
retained reconciliation/capacity/refund/purchased-credit contracts unchanged
```

## SHARED-008 published

Manual developer publication of the already-accepted clean contract is complete:

```text
package:
  @modainteract/moda-interact-shared@0.11.0

npm latest:
  0.11.0

dist.shasum:
  fd096379901d4c454bf1cde575b48621c1c21b79

Shared main publication metadata commit:
  0526de05dbddef4fde2e20b12bd6b9e7cc2664c4
```

The published registry shasum exactly matches the pre-publication dry-run package
artifact.

Current Shared release gate:

```text
BACKGROUND-020  Complete
SHOPIFY-024     Complete
SHARED-007      Complete
SHARED-008      Complete
```

The clean Shared first-production contract is therefore publicly consumable.

## Downstream reconciliation rule

Do not promote downstream tasks from stale domain indexes or stale task snapshots.
Inspect each latest individual ARCH-010 task YAML and transition `pending -> ready`
only when **every** task in its `depends_on` list is Complete.

This coordination note does not itself change consumer task states.
