# ARCH-010 Implementation Handoff

Date: 2026-09-12
Coordinator: `moda_architect`

## Current architecture state

ARCH-010 is **Agreed / In Progress** and is now explicitly the **first-production baseline** for Moda Interact billing, merchant lifecycle and recovery capacity.

Read in this order before implementing any ARCH-010 task:

1. [`ARCH-010-first-production-baseline.md`](ARCH-010-first-production-baseline.md)
2. [`ARCH-010-merchant-lifecycle-state-transitions.md`](ARCH-010-merchant-lifecycle-state-transitions.md)
3. [`ARCH-010-promotional-campaigns.md`](ARCH-010-promotional-campaigns.md)
4. [`ARCH-010-supersession-map.md`](ARCH-010-supersession-map.md)
5. the exact assigned `docs/decisions/<domain>/ARCH-010/<TASK>.md`

The exact task file remains the implementation handoff. Do not implement from this summary alone.

## First-production baseline rule

Rollout classification:

```text
PRE-PRODUCTION / BREAKING ROLLOUT
```

There is no production billing state requiring compatibility with the intermediate development schema/contracts.

Therefore:

```text
ARCH-010-DATABASE-013
  = one canonical empty-database first-production schema/migration baseline

future ARCH-011+
  = ordinary forward migrations from that accepted baseline
```

Do not preserve development-only aliases, backfills, dual reads or transitional state machines merely because a completed development task once introduced them.

## Immutable accepted history

For this consolidation, completed ARCH-010 task files are immutable accepted evidence.

```text
Complete task
  -> do not reopen
  -> do not rewrite Completion Report / Architect Review
  -> if accepted implementation no longer matches final baseline,
     use later correction/conformance work
```

The supplied workspace contains **23 Complete tasks**, and their task files remain unchanged by this baseline overlay.

`ARCH-010-SHOPIFY-002` remains `review` exactly as supplied. Do not amend its Attempt-8 task evidence to retrofit the new baseline. After it is architect-accepted Complete, `ARCH-010-SHOPIFY-023` performs the clean-baseline conformance work.

For immutable Complete/Review task files, their historical `enables:` list is an accepted snapshot and is not rewritten when later correction tasks are added. **Current task `depends_on:` metadata is the eligibility authority**, with domain indexes and this handoff providing the current reverse planning view.

## Database baseline

### Historical development tasks

`ARCH-010-DATABASE-001` through `ARCH-010-DATABASE-011` remain Complete implementation/review history.

They are **not** the production migration chain.

### Superseded task

`ARCH-010-DATABASE-012` is `superseded` and must not be implemented independently. Its valid upgrade-economics schema target is folded into DATABASE-013.

### Canonical database task

`ARCH-010-DATABASE-013` is Complete and owns:

- final Prisma schema;
- one empty-database first-production baseline migration;
- final seed/validators/ERD;
- removal of development migration directories;
- clean lifetime-Free entitlement model;
- clean human refund model;
- removal of local cancellation schema;
- campaign-only exact promotional grant lots;
- upgrade-economics policy/edges/snapshots.

Key removed first-production concepts include:

```text
BillingPlan.freeLifetimeConversationAllowance
BillingAllowanceAdjustment
FREE_RECOVERY_LIFETIME
ShopEntitlementCounter(PROMOTIONAL_RECOVERY_CREDITS)
MIGRATION_RECONCILED
SubscriptionCancellationRequest / mode / status
RecoveryCreditPurchaseStatus.REFUNDED
negative-App-Event refund correction state
campaign-less/direct promotional grant compatibility
BILLING_FREE_ALLOWANCE_EXHAUSTED historical-row compatibility
```

Canonical lifetime entitlement:

```text
LIFETIME_FREE_RECOVERY_CREDITS
```

## Shared baseline

`ARCH-010-SHARED-007` is Ready and removes superseded pre-production billing compatibility contracts, including the local-cancellation exports and the Free-only `BILLING_FREE_ALLOWANCE_EXHAUSTED` message code.

`ARCH-010-SHARED-008` is Pending behind SHARED-007 and publishes the clean package as:

```text
@modainteract/moda-interact-shared@0.11.0
```

Do not republish SHARED-001/003/005 individually. Their retained contracts are already part of the accepted 0.10.0 development release; SHARED-008 is the one new publication required because SHARED-007 changes package contents.

## Runtime baseline-conformance bridge

Two new correction tasks protect completed/in-flight implementation history while moving consumers to the clean baseline:

```text
ARCH-010-ADMIN-010
  DATABASE-013 + SHARED-008 + accepted ADMIN-001
  -> remove Admin compatibility reads/types/actions

ARCH-010-SHOPIFY-023
  DATABASE-013 + SHARED-008 + accepted SHOPIFY-002
  -> remove Shopify billing compatibility reads/raw SQL/types
```

These tasks do not implement downstream product features. They only make the current repositories clean consumers of the first-production baseline.

Still-open Background tasks were amended directly rather than duplicated. In particular:

- BACKGROUND-011 has **no** signed Free-adjustment compatibility;
- BACKGROUND-012 removes any remaining local cancellation executor/mutation path while implementing provider reconciliation;
- BACKGROUND-014 removes any remaining automatic negative-App-Event refund/correction path;
- BACKGROUND-019 uses only exact selected campaign grant lots and no aggregate promotional counter.

## Canonical recovery-capacity order

```text
FREE
  selected usable campaign PromotionalCreditGrant
  -> PURCHASED_RECOVERY_CREDITS
  -> LIFETIME_FREE_RECOVERY_CREDITS
  -> BLOCK NEW RECOVERY ADMISSION

PAID
  selected usable campaign PromotionalCreditGrant
  -> current BillingPeriod INCLUDED_RECOVERY_CREDITS
  -> PURCHASED_RECOVERY_CREDITS
  -> LIFETIME_FREE_RECOVERY_CREDITS
  -> BLOCK NEW RECOVERY ADMISSION
```

There is no automatic Paid overage.

## Current task frontier

The Ready ARCH-010 implementation tasks after baseline consolidation are:

| Task | Owner | Why Ready |
|---|---|---|
| `ARCH-010-SHARED-007` | `moda_shared` | SHARED-006 is Complete |
| `ARCH-010-ADMIN-007` | `moda_admin` | independent pure upgrade-economics evaluator |
| `ARCH-010-BACKGROUND-015` | `moda_background` | dependency-free provider snapshot; no architecture hold |

Current in-review work:

| Task | State | Rule |
|---|---|---|
| `ARCH-010-SHOPIFY-002` | Review, Attempt 8 | architect review it as submitted; do not retrofit baseline cleanup into that attempt |

Everything else remains Pending behind the appropriate baseline/conformance or existing feature dependency.

## Expected near-term unlock order

```text
DATABASE-013 Complete
        │
        ├── enables database-dependent open work
        ├── contributes to ADMIN-010
        └── contributes to SHOPIFY-023

SHARED-007 Complete
        ↓
SHARED-008 publish 0.11.0
        │
        ├── contributes to ADMIN-010
        ├── contributes to SHOPIFY-023
        └── unblocks Shared-consuming Background/Shopify work

SHOPIFY-002 Accepted Complete
        + DATABASE-013 Complete
        + SHARED-008 Complete
        ↓
SHOPIFY-023

ADMIN-001 already Complete
        + DATABASE-013 Complete
        + SHARED-008 Complete
        ↓
ADMIN-010
```

DATABASE-013 and SHARED-007 can execute in parallel. ADMIN-007 and BACKGROUND-015 can also execute independently.

## Current task counts

From individual task YAML after this consolidation:

```text
all ARCH-010 tasks: 79
complete:           24
review:              1
ready:               3
pending:            49
superseded:          2
```

Domain totals:

```text
Shopify       23
Background    19
Database      13
Admin         10
Shared         8
System Test    5
Gateway        1
```

## System-test rule

All ARCH-010 system-test tasks remain terminal/manual-gated.

No implementation, publication, infrastructure or observability task depends on a system-test task.

After implementation is complete, the developer may manually verify the integrated product before explicitly invoking the expensive system-test tasks. Do not auto-start them merely because dependencies become Complete.

## Task materialisation

This overlay was authored outside the developer's canonical Git/worktree environment. New tasks are therefore **defined but not materialised** under the architect task-materialisation policy.

After applying the overlay to the real workspace, use the normal task materialisation/launcher path for an eligible Ready task. Do not claim that this external architecture session created/pushed task branches or worktrees.

## Stop rule for implementation agents

If DATABASE-013/SHARED-008 removes a symbol that an open task still requires in a way not covered by its amended definition:

1. stop that task;
2. record the exact schema/contract gap;
3. return to `moda_architect`;
4. do **not** recreate the removed compatibility concept locally.

The goal is one first-production model, not a clean database wrapped by service-local legacy adapters.

## Sequencing correction — SHARED-007 live-consumer block (2026-09-12)

This section supersedes the earlier handoff statements that describe SHARED-007 as
immediately Ready and place consumer cleanup after SHARED-008.

SHARED-007 Attempt 1 correctly stopped because live first-party consumers still import
contracts that the task must delete. The corrected pre-production breaking-release
sequence is:

```text
Shared 0.10.0 already published
        |
        +--> BACKGROUND-020  remove Background cancellation/free-exhaustion consumers
        |
        +--> SHOPIFY-024     remove Shopify Free-only exhaustion consumer
                  |
                  v
          architect acceptance of both
                  |
                  v
          SHARED-007 blocked -> ready
                  |
                  v
          SHARED-007 Attempt 2
                  |
                  v
          SHARED-008 publish 0.11.0
                  |
                  v
          ADMIN-010 / SHOPIFY-023 and remaining Shared-consuming work
```

The cleanup tasks are intentionally narrow:

- `BACKGROUND-020` does not implement BACKGROUND-009 or BACKGROUND-012;
- `SHOPIFY-024` does not implement SHOPIFY-008 or SHOPIFY-023;
- `SHARED-007` still owns deletion of the public names;
- `SHARED-008` still owns the only 0.11.0 publication.

`BILLING_PLAN_CHANGE_ACTION_REQUIRED` had no active first-party consumer in the
SHARED-007 blocked-run inspection and remains scheduled for deletion by SHARED-007.

Individual task YAML remains authoritative for execution state. Domain indexes should
be regenerated/reconciled from current task YAML after these portable task definitions
are applied to the latest workspace, rather than copying stale status rows from the
SHARED-007 Attempt-1 worktree snapshot.

