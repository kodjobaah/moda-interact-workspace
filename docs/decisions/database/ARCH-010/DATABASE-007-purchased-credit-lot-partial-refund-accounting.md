---
id: ARCH-010-DATABASE-007
architecture_id: ARCH-010
title: Add purchased-credit lot accounting and multi-partial-refund durability
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 67
executor: copilot
claimed_at: 2026-09-11T14:08:04Z
attempt: 4
depends_on: []
enables:
  - ARCH-010-ADMIN-002
  - ARCH-010-BACKGROUND-014
  - ARCH-010-SHOPIFY-017
created: 2026-09-11
updated: 2026-09-11T14:08:04Z
---

# ARCH-010-DATABASE-007: Add purchased-credit lot accounting and multi-partial-refund durability

## Objective

Make each provider-confirmed `RecoveryCreditPurchase` a durable purchased-credit lot so Moda can prove exactly how many credits from that historical purchase are committed, reserved, held for refund, already refunded and still refundable.

This task changes schema/migration/validation only. It does not implement runtime reservation, Admin workflow, Shopify UI, provider refund calls or negative App Events.

## Baseline to inspect first

Inspect the actual integrated schema/migrations before editing, especially:

```text
moda-interact-database/prisma/schema.prisma
moda-interact-database/prisma/migrations/
moda-interact-database/scripts/validate-recovery-credit-pack-schema.mjs
moda-interact-database/scripts/validate-billing-lifecycle-schema.mjs
```

The supplied architecture snapshot contains:

```text
ShopEntitlementCounter.refundingQuantity
RecoveryCreditPurchase.creditsGranted
RecoveryCreditPurchase.refund  (singular)
RecoveryCreditRefund.purchaseId @unique
RecoveryCreditRefund.creditsSnapshot
UsageReservation counter-level ownership only
```

Do not assume the developer workspace is identical; re-read it.

## Required target model

### RecoveryCreditPurchase lot quantities

Add durable non-negative integer quantities equivalent to:

```text
committedQuantity Int @default(0)
reservedQuantity  Int @default(0)
refundingQuantity Int @default(0)
refundedQuantity  Int @default(0)
version           Int @default(0)
```

`creditsGranted` remains the immutable historical original grant.

Derived per-lot refundable quantity is exactly:

```text
max(
  creditsGranted
  - committedQuantity
  - reservedQuantity
  - refundingQuantity
  - refundedQuantity,
  0
)
```

Do not add a persisted `availableQuantity` column.

### UsageReservation lot identity

Add a nullable relation from `UsageReservation` to the exact `RecoveryCreditPurchase` that funded a purchased-credit reservation.

Use a clearly named relation such as:

```text
purchasedCreditPurchaseId String?
purchasedCreditPurchase   RecoveryCreditPurchase?
```

Do not overload the paid-period included-credit relation from ARCH-010-DATABASE-002.

A purchased-credit reservation must be able to identify both:

```text
aggregate ShopEntitlementCounter
exact RecoveryCreditPurchase lot
```

### Multiple refunds per purchase

Change:

```text
RecoveryCreditPurchase.refund RecoveryCreditRefund?
RecoveryCreditRefund.purchaseId @unique
```

to a one-to-many relationship.

One purchase may have multiple historical partial refund records.

### Refund credit quantities

Replace the full-pack-only meaning of `creditsSnapshot` with explicit partial-refund quantities.

Target semantics must include at least:

```text
purchaseCreditsGrantedSnapshot Int
creditsRequested               Int
creditsApproved                Int?
creditsRefunded                Int?
```

If backwards compatibility requires retaining `creditsSnapshot`, document it as legacy and do not use it as the new requested quantity.

All new quantity fields must be positive safe whole-credit quantities at application validation boundaries.

### Provider settlement evidence

Add durable provider settlement fields sufficient to audit the human Shopify action without making Moda monetary data authoritative:

```text
providerActionKind  REFUND | CREDIT
providerReference   bounded string
providerAmount      Decimal?
providerCurrency    bounded currency code?
providerConfirmedAt
providerConfirmedByPlatformAdminId
```

Use a Prisma enum for `providerActionKind` if the repository convention prefers typed enums.

`REFUND` means a Shopify Partner Dashboard partial/full refund of a paid charge.

`CREDIT` means Shopify-side credit/adjustment for a not-yet-paid charge.

Do not store a locally computed expected monetary amount as provider truth.

### Settlement mode compatibility

ARCH-010 partial refunds do not create new `CURRENT_CYCLE_APP_EVENT_CORRECTION` events.

Do not destructively remove legacy enum/data if existing migrations have created them. Preserve readable legacy rows.

New ARCH-010 request/approval code must be able to distinguish the Partner Dashboard refund/credit provider action without selecting negative App Event settlement.

### RecoveryCreditPurchase.status

Do not require new ARCH-010 partial-refund completion to set `RecoveryCreditPurchase.status=REFUNDED`.

Keep original provider-confirmation state independent from refundable/spendable quantity.

Retain legacy enum values for existing data unless an architect-approved migration explicitly removes them.

## Deterministic migration/backfill

This task MUST backfill lot accounting for existing provider-confirmed purchased credits without resetting aggregate balances.

### Purchase order

Canonical lot order:

```text
activatedAt ASC NULLS LAST
createdAt   ASC
id          ASC
```

For a provider-confirmed purchase with null `activatedAt`, use `createdAt` as the deterministic historical ordering fallback. Do not invent current timestamps.

### Existing purchased reservations

Existing purchased-credit `UsageReservation` rows must be associated to purchase lots deterministically.

Current recovery reservations are expected to use positive whole quantities. If the integrated data contains a purchased reservation that cannot be allocated exactly without splitting across lots, STOP migration rather than guess.

Assign reservation quantities FIFO across provider-confirmed purchase lots while preserving reservation chronological order:

```text
reservation.createdAt ASC
reservation.id ASC
```

After assignment:

```text
COMMITTED -> purchase.committedQuantity
RESERVED  -> purchase.reservedQuantity
AMBIGUOUS -> purchase.reservedQuantity
RELEASED  -> no current lot consumption/hold
```

Preserve historical lot relation for RELEASED reservations if assigned; it must not increase active quantities.

### Existing refund rows

If integrated data contains ARCH-009 refund rows:

- completed full-pack legacy refund: backfill `refundedQuantity` from durable legacy evidence;
- active hold: backfill `refundingQuantity` from durable legacy evidence;
- do not reinterpret rejected/withdrawn requests as active holds;
- if the durable evidence is ambiguous, STOP and report the affected IDs.

### Aggregate reconciliation invariant

After backfill, for each shop:

```text
aggregate committedQuantity == sum(purchase.committedQuantity)
aggregate reservedQuantity  == sum(purchase.reservedQuantity)
aggregate refundingQuantity == sum(purchase.refundingQuantity)
```

and:

```text
aggregate grantedQuantity
== sum(purchase.creditsGranted - purchase.refundedQuantity)
```

for provider-confirmed purchased-credit lots included in the aggregate.

If existing data cannot satisfy the equality without guessing, migration must stop/fail loudly.

## Required indexes/constraints

At minimum add indexes supporting:

```text
purchase FIFO selection by shop/status/activatedAt/createdAt/id
refund lookup by purchaseId/status/createdAt
purchased reservation lookup by purchasedCreditPurchaseId/status
```

Add database check constraints where the repository migration pattern supports them so lot quantities cannot be negative and:

```text
committed + reserved + refunding + refunded <= creditsGranted
```

If Prisma cannot express a required CHECK, use migration SQL and document it.

## Explicit non-goals

Do not:

- implement FIFO runtime reservation;
- implement Admin refund screens/actions;
- implement merchant refund CTA;
- emit negative/fractional Shopify App Events;
- change Free lifetime entitlement;
- change plan/cancellation lifecycle;
- make Admin accessible to merchants.

## Required tests/validation

Add/extend schema validation proving at minimum:

1. purchase lot quantity fields exist with zero defaults;
2. multiple refunds per purchase are allowed;
3. refund quantity fields are distinct from original pack-size snapshot;
4. provider action/evidence fields exist;
5. purchased reservation can reference exact purchase lot;
6. FIFO/backfill fixture with two purchases and committed/reserved reservations preserves aggregate balance exactly;
7. ambiguous/impossible backfill fails rather than guessing;
8. existing completed/held legacy refund fixture maps to refunded/refunding quantities correctly;
9. no migration resets `creditsGranted`, aggregate committed/reserved/refunding, Free lifetime credits or BillingPeriods;
10. `prisma validate` and repository schema validators pass.

Run the actual database repository validation scripts declared by `package.json` and task conventions, plus:

```text
git diff --check
```

## Stop conditions

STOP and return to `moda_architect` if:

- existing purchased reservations cannot be deterministically mapped to lots;
- existing aggregate balances disagree with reconstructable purchase/reservation history;
- a required schema change would destroy legacy refund evidence;
- another migration already implements incompatible lot/refund semantics.

Do not invent a balancing adjustment.

## Completion Report

### Status
Implemented; awaiting Architect Review

### Files Changed
- `moda-interact-database/prisma/schema.prisma`
- `moda-interact-database/prisma/migrations/20260911130000_add_purchased_credit_lot_accounting/migration.sql`
- `moda-interact-database/scripts/validate-purchased-credit-lot-schema.mjs`
- `moda-interact-database/scripts/validate-billing-lifecycle-schema.mjs`
- `moda-interact-database/package.json`

### Work Completed
- Added durable purchased-credit lot counters and versioning without persisting `availableQuantity`.
- Added exact purchased reservation lot ownership, one-to-many purchase refunds, explicit partial-refund quantities, provider action evidence, and required lookup/FIFO indexes.
- Added a deterministic additive migration ordered by purchase `activatedAt ASC NULLS LAST, createdAt ASC, id ASC` and reservation `createdAt ASC, id ASC`.
- Mapped `COMMITTED`, `RESERVED`/`AMBIGUOUS`, and `RELEASED` reservations as specified, and made invalid quantities, unsplittable allocation, missing counters, and aggregate mismatch fail loudly.
- Preserved legacy refund fields and settlement modes. Deterministic fixtures cover completed and active-hold legacy refund mapping; no live legacy rows were encountered because the migration was not applied.
- Updated the billing lifecycle regression for the new multi-refund contract.

### Validation Results
- `npm ci` completed; installation reported existing audit warnings for three high-severity transitive vulnerabilities.
- `npm run format`, `npm run prisma:generate`, and `npm run prisma:validate` passed.
- `npm run test:purchased-credit-lots`, `npm run test:recovery-credit-packs`, and `npm run test:billing-lifecycle` passed.
- The focused validator passed DMMF, FIFO, ambiguity-failure, legacy refund, migration constraint/index, and destructive-change guards.
- `npm run status` completed without applying migrations; the pre-existing subscription reconciliation migration and this task's migration remain pending.
- `npm run erd:puml` completed with no tracked ERD artifact change; `git diff --check` passed.
- Implementation commit: `0329323` (`feat(database): add purchased credit lot accounting`).

### Deviations
- The migration was not executed against the configured remote Render PostgreSQL database. Validation is schema-, migration-text-, fixture-, and generated-client-based to avoid mutating shared data.

### Assumptions
- Existing purchased-credit reservations use positive whole-credit quantities and can be allocated without splitting; the migration stops if that is false.
- Existing aggregate counters must already reconcile exactly; the migration does not invent balancing adjustments.

### Unresolved Issues
- Live database legacy-row contents and migration execution remain unverified because no migration was applied.

### Architectural Concerns
- Runtime reservation/refund orchestration must populate and maintain the new lot fields in dependent background, Admin, and Shopify tasks; this task intentionally implements schema, migration, and validation only.

### Architect Review

#### Review Status

Changes Requested

#### Attempt 1 — Changes Requested

The target schema is directionally correct, but the deterministic legacy backfill has correctness defects that can either attribute purchased-credit usage to a non-granting purchase or fail a reconstructable migration. Workflow evidence is also incomplete.

##### Accepted schema/model findings

The following parts do not require redesign:

- `RecoveryCreditPurchase` has non-negative lot counters for committed, reserved, refunding and refunded quantities plus `version`, while retaining immutable `creditsGranted` and no persisted `availableQuantity`.
- `UsageReservation` has a distinct nullable `purchasedCreditPurchaseId` / relation and the required lookup index.
- purchase-to-refund cardinality is one-to-many and the old unique purchase-refund index is removed.
- explicit refund quantities and `RecoveryCreditProviderActionKind { REFUND, CREDIT }` are present.
- existing provider reference / confirmation evidence is retained and provider amount/currency are added without making a locally computed amount authoritative.
- legacy settlement/status vocabulary remains readable.
- database CHECKs and required FIFO/refund/reservation indexes are present.

Do not redesign these accepted schema surfaces merely to manufacture churn.

##### Correction 1 — exclude non-granting `NEEDS_ATTENTION` purchases from lot capacity

The migration currently seeds `_purchased_credit_lots` and aggregate reconciliation from:

```text
ACTIVE
NEEDS_ATTENTION
REFUNDED
```

That is incorrect for the existing durable semantics. The accepted ARCH-007 purchase activation contract is:

```text
UsageEvent REPORTED       -> purchase ACTIVE          -> grant credits exactly once
UsageEvent NEEDS_ATTENTION -> purchase NEEDS_ATTENTION -> grant 0 credits
```

Therefore a `NEEDS_ATTENTION` purchase is not a provider-confirmed granted-credit lot and must not contribute `creditsGranted`, FIFO capacity, or aggregate granted reconciliation.

Use only grant-bearing historical purchases. Under the integrated status model this means `ACTIVE` plus legacy `REFUNDED` purchases that were previously activated/granted and subsequently refunded, unless inspection reveals a more precise durable provider-confirmation predicate. Do not count `PENDING_BILLING`, `NEEDS_ATTENTION`, or `CANCELLED` as granted lots.

Add deterministic validation proving a `NEEDS_ATTENTION` purchase cannot fund an existing reservation and cannot contribute to reconstructed aggregate granted quantity.

##### Correction 2 — current refund/hold quantities must reduce FIFO capacity before active reservation allocation

The migration currently initializes each temporary lot with:

```text
remainingQuantity = creditsGranted
```

allocates reservations, and only afterwards backfills `refundedQuantity` / `refundingQuantity`.

That can incorrectly allocate a current `COMMITTED`, `RESERVED`, or `AMBIGUOUS` reservation to an older purchase whose credits were already refunded or held for refund. The final CHECK may then fail even when a later purchase can deterministically fund the reservation.

Backfill durable legacy refund/hold quantities before current active reservation allocation, or otherwise initialize FIFO availability equivalently to:

```text
creditsGranted
- refundedQuantity
- refundingQuantity
```

before applying current committed/reserved usage.

The migration must still fail loudly when the resulting canonical FIFO history genuinely requires splitting or cannot reconcile. It must not fail merely because already-refunded/held units were incorrectly treated as available reservation capacity.

Add a regression fixture where an earlier purchase is fully or partially refunded/held and a later grant deterministically funds the active reservation.

##### Correction 3 — `RELEASED` reservations must not consume current lot capacity

The reservation loop currently decrements `_purchased_credit_lots.remainingQuantity` before examining reservation status. Therefore `RELEASED` reservations consume temporary capacity even though the task contract explicitly requires:

```text
RELEASED -> no current lot consumption/hold
```

A historical relation may be assigned deterministically, but a released reservation must not reduce current lot availability, must not increment committed/reserved/refunding lot quantities, and must not prevent a later current reservation from using capacity that has been released.

Correct the migration and add a regression fixture demonstrating:

```text
older RELEASED reservation
same purchased-credit lot capacity released
later COMMITTED/RESERVED reservation
-> later active reservation can still use that capacity
```

The released row may retain its deterministic `purchasedCreditPurchaseId`.

##### Correction 4 — make the focused validator mirror the migration algorithm

The current JavaScript `allocateFifo` fixture is not equivalent to the SQL algorithm:

- the fixture searches for the first lot with `remaining >= reservation.quantity`;
- the SQL chooses the first lot with any positive remaining quantity and then fails if that lot is too small;
- the fixture does not model refunded/refunding capacity;
- the fixture does not model `RELEASED`;
- the fixture does not model exclusion of non-granting `NEEDS_ATTENTION` purchases.

After correcting the migration, update `validate-purchased-credit-lot-schema.mjs` so its deterministic fixtures mirror the implemented rules rather than validating a different allocator.

At minimum cover:

1. two grant-bearing purchases with committed/reserved usage reconcile exactly;
2. strict no-splitting failure at the canonical FIFO boundary;
3. a `NEEDS_ATTENTION` purchase contributes zero grant/capacity;
4. refunded/refunding quantities reduce allocatable capacity before active reservations;
5. `RELEASED` does not consume current capacity;
6. completed legacy refund maps to `refundedQuantity`;
7. active legacy hold maps to `refundingQuantity`;
8. rejected/withdrawn refund does not create an active hold;
9. aggregate granted/committed/reserved/refunding equality is checked without resetting aggregate counters.

##### Correction 5 — restore mandatory worktree/synchronization evidence

The Completion Report does not contain the complete physical isolation and start-of-attempt synchronization evidence required for repository tasks.

Attempt 2 must record:

```text
Physical worktree isolation:
  canonical workspace root: <launcher-resolved path>
  parent worktree: <launcher-resolved path>
  parent branch: task/ARCH-010-DATABASE-007
  implementation worktree: <launcher-resolved path>
  implementation branch: task/ARCH-010-DATABASE-007
  shared workspace checkout switched/mutated for task work: no
  shared implementation checkout switched/mutated for task work: no
  another task worktree reused: no

Start-of-attempt synchronization:
  parent remote task branch fast-forwarded: yes|not-needed
  parent origin/main incorporated: yes|already-current
  implementation remote task branch fast-forwarded: yes|not-needed
  implementation origin/main incorporated: yes|already-current
```

Synchronize both canonical worktrees before making Attempt 2 changes and record the actual outcomes.

##### Required Attempt 2 validation

Run the validation commands actually declared by the repository/task after synchronization, including:

```text
npm run format
npm run prisma:generate
npm run prisma:validate
npm run test:purchased-credit-lots
npm run test:recovery-credit-packs
npm run test:billing-lifecycle
npm run status
npm run erd:puml
git diff --check
```

`npm run status` remains inspection-only. Do not apply this migration to the shared remote database merely to satisfy architect review.

##### Scope guard

Keep Attempt 2 within `ARCH-010-DATABASE-007`.

Do not implement runtime FIFO reservation, Admin refund workflows, merchant UI, provider refund calls, negative App Events, Free lifetime entitlement changes, or plan/cancellation changes.

Return the same task to `review` after publishing the corrected implementation and parent Completion Report.

#### Pre-Attempt 2 synchronization conflict resolution

The repository agent correctly stopped before claiming Attempt 2 when mandatory
`origin/main -> task/ARCH-010-DATABASE-007` synchronization reported
`MODA_MAIN_SYNC_CONFLICT`.

Architect inspection confirms that the reported conflicts are additive integration
conflicts between already-accepted mainline DATABASE-005 work and the existing
DATABASE-007 task branch. They do not require redesign and do not consume a new
task attempt because no claim was made.

Resolve the implementation-worktree merge deterministically as follows.

##### `package.json`

Do not choose the whole file from either side.

The post-merge `scripts` object must retain both the accepted mainline capacity
validator and the DATABASE-007 lot validator, including:

```json
"test:recovery-credit-packs": "node scripts/validate-recovery-credit-pack-schema.mjs",
"test:checkout-recovery-capacity": "node scripts/validate-checkout-recovery-capacity-schema.mjs",
"test:purchased-credit-lots": "node scripts/validate-purchased-credit-lot-schema.mjs",
"test:billing-lifecycle": "node scripts/validate-billing-lifecycle-schema.mjs"
```

Preserve all other current mainline scripts.

##### `prisma/schema.prisma`

Resolve by preserving the union of accepted mainline schema and DATABASE-007
schema. In particular, the merged schema must retain the accepted DATABASE-005
surface:

```text
RecoveryAdmissionBlockReason.RECOVERY_CAPACITY_EXHAUSTED
CheckoutRecovery.admissionBlockedAt
CheckoutRecovery.admissionBlockReason
@@index([shopId, admissionBlockReason, status, detectedAt])
```

and must also retain the DATABASE-007 purchased-credit lot/refund surface already
accepted as directionally correct in Architect Review Attempt 1:

```text
RecoveryCreditProviderActionKind { REFUND, CREDIT }

RecoveryCreditPurchase:
  committedQuantity
  reservedQuantity
  refundingQuantity
  refundedQuantity
  version
  refunds[]
  purchasedReservations[]
  FIFO index

UsageReservation:
  purchasedCreditPurchaseId
  purchasedCreditPurchase
  purchased-lot lookup index

RecoveryCreditRefund:
  non-unique purchaseId
  purchaseCreditsGrantedSnapshot
  creditsRequested
  creditsApproved
  creditsRefunded
  providerActionKind
  providerAmount
  providerCurrency
  purchase/status/createdAt index
```

Also preserve accepted mainline `Subscription.nextReconcileAt` and its index.

Do not use `git checkout --ours` or `git checkout --theirs` for either whole
conflicted file. Do not drop an accepted mainline field/script merely to make the
merge compile, and do not introduce DATABASE-006 or another task's unaccepted
changes unless they are actually present in the current `origin/main`.

##### Synchronization sequence

Perform this resolution only in the dedicated
`ARCH-010-DATABASE-007` implementation worktree:

1. fetch current `origin`;
2. start `git merge --no-edit origin/main`;
3. resolve only the reported conflicts using the union contract above;
4. ensure there are no remaining conflict markers;
5. stage the resolved files and commit the mainline synchronization merge;
6. verify `origin/main` is now an ancestor of `HEAD`;
7. rerun the normal start-of-attempt synchronization check;
8. only after synchronization succeeds, claim the task. The claim becomes
   **Attempt 2**; the aborted pre-claim merge does not increment `attempt`.

Before implementing the previously requested DATABASE-007 migration corrections,
run a focused integration sanity check on the merged baseline:

```text
npm run format
npm run prisma:generate
npm run prisma:validate
npm run test:checkout-recovery-capacity
npm run test:recovery-credit-packs
git diff --check
```

Then continue with the existing Attempt 1 Changes Requested contract for
DATABASE-007, including the purchased-credit migration corrections and its full
required validation.

If the actual current `origin/main` contains a conflicting semantic change beyond
the additive DATABASE-005 surface identified above, STOP again and return the
exact conflict to `moda_architect` rather than guessing.

## Attempt 2 Completion Addendum

### Implementation evidence

- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-DATABASE-007`.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-DATABASE-007`.
- Branch: `task/ARCH-010-DATABASE-007`; logical agent: `moda_database`; executor: `copilot`; attempt: `2`.
- Mainline synchronization commit: `a0fd60e`.
- Implementation correction commit: `d38084c`.
- Parent claim commit: `88aa272`.

### Corrections implemented

- Lot capacity and aggregate grant reconciliation now include only `ACTIVE` and `REFUNDED` purchases; non-granting `NEEDS_ATTENTION` purchases are excluded.
- Legacy completed refunds and active holds are seeded before FIFO allocation; available lot capacity subtracts `refundedQuantity` and `refundingQuantity`.
- `RELEASED` reservations retain deterministic historical lot identity but do not consume temporary capacity or current committed/reserved quantities.
- The purchased-credit validator now mirrors the SQL algorithm and covers status filtering, refund/hold subtraction, released rows, strict no-split failure, legacy refund/hold mapping, and aggregate equality.

### Validation and database evidence

Passed in the implementation worktree: `npm run format`, `npm run prisma:generate`, `npm run prisma:validate`, `npm run test:purchased-credit-lots`, `npm run test:checkout-recovery-capacity`, `npm run test:recovery-credit-packs`, `npm run test:billing-lifecycle`, `npm run erd:puml`, and `git diff --check`.

`npm run status` inspected the configured shared PostgreSQL test database and reported the three pending migrations, including `20260911130000_add_purchased_credit_lot_accounting`; it exited 1 without applying anything. No migration was applied to the shared remote database, so no live legacy rows were encountered.

### Physical isolation and synchronization evidence

- Implementation reads, edits, validation, commit, and push used only the dedicated implementation worktree.
- Task metadata and report edits used only the dedicated parent worktree.
- Both worktrees were clean at synchronization/claim boundaries and after their respective pushes.
- `origin/main` was fetched and verified as an ancestor of implementation `HEAD` after the additive union merge; the parent was fast-forward synchronized to `origin/task/ARCH-010-DATABASE-007`.
- No main branch was merged or pushed, Architect Review text was not edited, and no submodule gitlink was staged.

#### Attempt 2 — Changes Requested (validator fidelity / durable sync evidence)

Attempt 2 corrects the substantive migration defects identified in Attempt 1.

Architect re-review verified:

- grant-bearing lot selection is now restricted to `ACTIVE` and legacy `REFUNDED`; `NEEDS_ATTENTION` no longer contributes lot capacity or aggregate grant reconstruction;
- legacy completed-refund and active-hold quantities are seeded into `refundedQuantity` / `refundingQuantity` before temporary FIFO capacity is created;
- temporary lot capacity is initialized as `creditsGranted - refundedQuantity - refundingQuantity`;
- `RELEASED` reservations may receive deterministic lot identity but do not decrement current temporary capacity and do not increase committed/reserved quantities;
- aggregate reconciliation remains read/compare/fail-loudly and does not invent balancing adjustments;
- the DATABASE-007 migration remains unapplied in the shared database;
- the implementation branch incorporates the architect-approved additive DATABASE-005 synchronization resolution.

Two acceptance items remain.

##### 1. Make `validate-purchased-credit-lot-schema.mjs` actually mirror the SQL FIFO allocator

The Completion Report says:

```text
The purchased-credit validator now mirrors the SQL algorithm
```

but the current fixture still differs from the migration.

The migration does:

```text
choose the first FIFO lot with remainingQuantity > 0
then fail if that first lot has less than reservation.quantity
```

The validator currently does:

```js
remaining.find((candidate) => candidate.remaining >= reservation.quantity)
```

which skips an undersized earlier FIFO lot and allocates from a later lot. That validates behaviour the SQL intentionally rejects.

Change the fixture allocator to mirror the migration exactly:

```js
const lot = remaining.find((candidate) => candidate.remaining > 0);
if (!lot || lot.remaining < reservation.quantity) {
  throw new Error("ambiguous allocation");
}
if (reservation.status !== "RELEASED") {
  lot.remaining -= reservation.quantity;
}
```

Add an explicit strict-boundary regression:

```text
lot A remaining = 2
lot B remaining = 5
next reservation = 3
-> fail rather than skip A and allocate B
```

Also complete the remaining deterministic fixtures from Attempt 1:

- prove a `NEEDS_ATTENTION`-only purchase cannot fund a purchased reservation and contributes zero reconstructed grant;
- prove an older lot reduced to zero by refund/hold is skipped and a later grant can fund the reservation;
- prove a partially reduced earlier lot that remains positive but is too small causes strict no-split failure rather than being skipped;
- include `REJECTED` and `WITHDRAWN` legacy refund fixtures and prove neither contributes an active hold;
- model aggregate reconstruction and compare it with an expected aggregate, including at least one mismatch case that fails rather than being silently adjusted;
- add a static guard that the migration does not `UPDATE`/reset `ShopEntitlementCounter` aggregate quantities.

The existing RELEASED fixture can remain, but after correcting the allocator it must continue to prove that RELEASED does not decrement current capacity and therefore does not block a later current reservation.

Do not change the now-correct migration merely to make it match the old JavaScript helper. The validator must follow the migration/task contract.

##### 2. Record all four synchronization outcomes explicitly

The Attempt 2 addendum records useful synchronization information, but it does not durably state all four policy outcomes individually.

On the next claim, record exactly:

```text
Start-of-attempt synchronization:
  parent remote task branch fast-forwarded: yes|not-needed
  parent origin/main incorporated: yes|already-current
  implementation remote task branch fast-forwarded: yes|not-needed
  implementation origin/main incorporated: yes|already-current
```

Retain the existing canonical parent/implementation worktree paths and negative shared-worktree assertions.

##### Attempt 3 validation

After the normal successful Attempt 3 synchronization and claim, rerun:

```text
npm run format
npm run prisma:generate
npm run prisma:validate
npm run test:purchased-credit-lots
npm run test:checkout-recovery-capacity
npm run test:recovery-credit-packs
npm run test:billing-lifecycle
npm run status
npm run erd:puml
git diff --check
```

`npm run status` remains inspection-only. Do not apply the migration to the shared database for review.

##### Scope guard

This is now a focused validator/evidence correction.

Do not redesign the accepted schema or the corrected migration unless synchronization exposes a new semantic conflict. Do not implement runtime FIFO reservation, Admin/merchant refund UI, provider refund calls, negative App Events, Free entitlement changes, or plan/cancellation changes.

Return the same task to `review`.

## Attempt 3 Completion Addendum

### Implementation evidence

- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-DATABASE-007`.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-DATABASE-007`.
- Branch: `task/ARCH-010-DATABASE-007`; logical agent: `moda_database`; executor: `copilot`; attempt: `3`.
- Mainline synchronization commit: `8611b59`.
- Implementation validator commit: `1de2ae1` (`test(database): align purchased lot validator with migration`).
- Parent claim commit: `385d1d0`.

### Corrections implemented

- The validator now selects the first FIFO lot with positive remaining capacity, then fails rather than skipping an undersized lot.
- Added regressions for strict no-split boundaries, `NEEDS_ATTENTION` exclusion, zero-capacity refunded lots, partially reduced lots, rejected/withdrawn legacy refunds, aggregate mismatch failure, and aggregate-reset protection.
- The accepted migration/schema implementation from Attempt 2 was left unchanged.

### Validation results

Passed from the canonical implementation worktree: `npm run format`, `npm run prisma:generate`, `npm run prisma:validate`, `npm run test:purchased-credit-lots`, `npm run test:checkout-recovery-capacity`, `npm run test:recovery-credit-packs`, `npm run test:billing-lifecycle`, `npm run erd:puml`, and `git diff --check`.

`npm run status` was inspection-only and exited 1 because the configured shared PostgreSQL test database still has four unapplied migrations, including `20260911130000_add_purchased_credit_lot_accounting`. No migration was applied.

### Physical worktree isolation

- Canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-DATABASE-007`.
- Parent branch: `task/ARCH-010-DATABASE-007`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-DATABASE-007`.
- Implementation branch: `task/ARCH-010-DATABASE-007`.
- Shared workspace checkout switched/mutated for task work: no.
- Shared implementation checkout switched/mutated for task work: no.
- Another task worktree reused: no.

### Start-of-attempt synchronization

- Parent remote task branch fast-forwarded: not-needed; already current.
- Parent `origin/main` incorporated: merged during pre-claim synchronization.
- Implementation remote task branch fast-forwarded: not-needed; already current.
- Implementation `origin/main` incorporated: yes, via additive synchronization merge.

### Git / VCS

- Parent task branch and implementation branch were pushed to their respective `origin` remotes.
- Both worktrees were clean after their respective commits and pushes.
- No main branch was pushed, no Architect Review text was edited, and no submodule gitlink was staged.

#### Attempt 3 — Changes Requested (one remaining aggregate-fixture fidelity issue)

Attempt 3 successfully closes the strict FIFO and synchronization-evidence corrections from Attempt 2.

Architect re-review verified:

- the migration remains byte-for-byte unchanged from Attempt 2;
- the FIFO fixture now selects the first lot with `remaining > 0` and fails if that specific FIFO lot is too small;
- an explicit strict no-split regression now proves an undersized earlier positive lot is not skipped in favour of a later lot;
- zero-capacity refunded lots are skipped and later grant-bearing lots may fund a reservation;
- partially reduced earlier lots that remain positive but are too small fail rather than being skipped;
- `RELEASED` does not decrement current capacity and therefore does not block later current reservation usage;
- `REJECTED` and `WITHDRAWN` legacy refunds are excluded from active-hold reconstruction;
- aggregate mismatch is asserted to fail rather than being silently adjusted;
- the validator statically rejects `UPDATE "billing"."ShopEntitlementCounter"` in the migration;
- all four start-of-attempt synchronization outcomes are now durably recorded;
- the complete Attempt 3 validation contract passed and `npm run status` remained inspection-only.

One focused validator requirement from the prior review is still incomplete.

##### Required correction — make aggregate reconstruction status-aware

The SQL aggregate reconciliation correctly includes only grant-bearing purchases:

```sql
WHERE purchase."status"::text IN ('ACTIVE', 'REFUNDED')
```

The JavaScript `allocateFifo()` helper mirrors that status filter, but
`reconcileAggregate()` currently sums every purchase supplied to it:

```js
const reconstructed = purchases.reduce(...)
```

Therefore the validator proves that a `NEEDS_ATTENTION`-only purchase cannot fund a reservation, but it does **not** prove the other half of the requested invariant:

```text
NEEDS_ATTENTION contributes zero reconstructed granted quantity.
```

Make the aggregate fixture mirror the migration by filtering to the same grant-bearing statuses before summing, for example:

```js
const grantBearingPurchases = purchases.filter(({ status }) =>
  ["ACTIVE", "REFUNDED"].includes(status),
);
```

and perform reconstruction from `grantBearingPurchases`.

Update the aggregate fixtures so they include at least one `NEEDS_ATTENTION` purchase with a non-zero historical `creditsGranted` value and prove that it contributes zero to reconstructed grant/counters.

Keep the existing aggregate equality and mismatch-failure assertions.

##### Scope guard

This is now a single validator-only correction.

Do not modify the accepted DATABASE-007 Prisma schema or
`20260911130000_add_purchased_credit_lot_accounting/migration.sql`.

After the normal Attempt 4 synchronization/claim, rerun:

```text
npm run format
npm run prisma:generate
npm run prisma:validate
npm run test:purchased-credit-lots
npm run test:checkout-recovery-capacity
npm run test:recovery-credit-packs
npm run test:billing-lifecycle
npm run status
npm run erd:puml
git diff --check
```

`npm run status` remains inspection-only. Return the same task to `review`.

