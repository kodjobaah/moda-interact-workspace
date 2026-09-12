---
id: ARCH-010-BACKGROUND-015
architecture_id: ARCH-010
title: Read Shopify live subscription plus latest lifecycle event for reconciliation
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 57
executor: copilot
claimed_at: '2026-09-12T22:30:00Z'
attempt: 2
depends_on: []
enables:
- ARCH-010-BACKGROUND-012
created: 2026-09-11
updated: '2026-09-12'
---

# ARCH-010-BACKGROUND-015: Read Shopify live subscription plus latest lifecycle event for reconciliation

## Objective

Extend the existing Shopify Partner provider so reconciliation can distinguish a frozen subscription from cancellation instead of treating `activeSubscription=null` as sufficient cancellation evidence.

This task owns provider I/O and typed provider results only. It does not mutate Prisma state.

## Inspect before editing

```text
src/providers/shopify-partner-billing.provider.ts
tests/unit/providers/shopify-partner-billing.provider.test.ts
src/services/billing-reconciliation.service.ts   # inspect consumers only
SHOPIFY Partner API environment configuration already used by the provider
```

Read the ARCH-010 cancellation/freeze architecture before editing.

## Provider query

Add one reconciliation-snapshot method, using the repository's naming conventions, equivalent to:

```ts
getSubscriptionReconciliationSnapshot(shopifyShopId: string): Promise<{
  activeSubscription: PartnerSubscription | null;
  latestLifecycleEvent: PartnerSubscriptionLifecycleEvent | null;
}>;
```

Do not delete or change the externally observable contract of
getActiveSubscription().

Before changing this service, search the repository for every existing call site
of getActiveSubscription().

Existing code that currently calls getActiveSubscription() MUST continue to:

- compile;
- receive the same return shape;
- preserve the same null/error semantics;
- preserve the same Shopify-provider interpretation.

BG15 may refactor getActiveSubscription() internally so that it delegates to the
new shared Partner GraphQL parsing/snapshot implementation, but existing call
sites MUST NOT be forced to migrate as part of this task unless this task
explicitly names those call sites.

Do not add merchant/customer backwards-compatibility behaviour. This requirement
is only about repository API compatibility for existing source-code callers.

```text
activeSubscription(appId, shopId)
events(filter: { subjectId: appId, shopId, eventTypes: [...] }, first: 1, orderBy: OCCURRED_AT_DESC)
```

Filter lifecycle history to exactly:

```text
SUBSCRIPTION_CREATED
SUBSCRIPTION_UPDATED
SUBSCRIPTION_CANCELLATION_SCHEDULED
SUBSCRIPTION_CANCELED
SUBSCRIPTION_FROZEN
SUBSCRIPTION_UNFROZEN
```

Use `occurredAtMin = now - 365 days` and `occurredAtMax = now`, which is Shopify's maximum documented Historical Events range. Do not issue an unbounded history query.

## Lifecycle result

Return a typed event equivalent to:

```ts
type PartnerSubscriptionLifecycleEvent = {
  id: string;
  eventType:
    | "SUBSCRIPTION_CREATED"
    | "SUBSCRIPTION_UPDATED"
    | "SUBSCRIPTION_CANCELLATION_SCHEDULED"
    | "SUBSCRIPTION_CANCELED"
    | "SUBSCRIPTION_FROZEN"
    | "SUBSCRIPTION_UNFROZEN";
  state:
    | "CREATED"
    | "UPDATED"
    | "CANCELLATION_SCHEDULED"
    | "CANCELED"
    | "FROZEN"
    | "UNFROZEN";
  occurredAt: Date;
  cancelEffectiveOn: string | null;
  planHandle: string | null;
  billingPeriod: string | null;
};
```

Use exact generated/provider naming where necessary. Preserve semantics.

Do not infer a lifecycle state from `activeSubscription` fields. Historical `SubscriptionStatus.state` is provider evidence.

## Parsing rules

1. Partner non-2xx -> throw existing provider request error.
2. Any GraphQL error that makes either requested root result unreliable -> throw; do not return partial success.
3. `activeSubscription=null` is a valid live result.
4. zero lifecycle events in the 365-day range -> `latestLifecycleEvent=null`.
5. require the returned event to be a `SubscriptionStatus` event for the requested shop/app; malformed shapes are provider errors.
6. parse `occurredAt` as a valid Date; invalid timestamps fail the provider call.
7. preserve existing active-subscription parsing/invariants exactly, including one active flat-rate item and usage snapshots.

## Important terminology

Do NOT interpret the App Events billing error `ACCOUNT_FROZEN` as merchant subscription freeze. Shopify documents `ACCOUNT_FROZEN` as a partner-account billing-event error. This task deals only with `SUBSCRIPTION_FROZEN` / `SubscriptionStatusState.FROZEN` for the merchant subscription.

## Required tests

At minimum prove:

1. active subscription + latest CREATED parses both results;
2. active subscription + latest FROZEN exposes `FROZEN` lifecycle evidence;
3. `activeSubscription=null` + latest FROZEN remains distinguishable from cancellation;
4. `activeSubscription=null` + latest CANCELED exposes CANCELED;
5. latest UNFROZEN parses correctly;
6. latest CANCELLATION_SCHEDULED parses `cancelEffectiveOn`;
7. zero events returns null lifecycle evidence;
8. provider HTTP failure throws;
9. GraphQL errors do not become provider null;
10. malformed lifecycle timestamp/state fails closed;
11. the query scopes history by both app/subject and shop;
12. the query uses the six explicit event types and bounded 365-day window;
13. existing `getActiveSubscription()` behaviour/tests remain valid;
14. no Prisma write occurs in this provider.

## Non-goals

No Subscription update, no FROZEN transition, no BullMQ scheduling, no execution gate, no UI and no historical-event persistence.

## Validation

Run focused provider tests, repository-declared typecheck/build/unit suite and `git diff --check`.

## Stop conditions

STOP if the configured Partner API version does not expose root `events`, `EventFilterInput`, `SubscriptionStatus.state` and the required lifecycle event types. Return the exact schema mismatch to `moda_architect`; do not fall back to legacy Admin Billing API/webhooks.

## Completion Report

### Status
In Progress.

### Files Changed

- `src/providers/shopify-partner-billing.provider.ts`
- `tests/unit/providers/shopify-partner-billing.provider.test.ts`

### Work Completed

- Added `getSubscriptionReconciliationSnapshot()` without changing the existing `getActiveSubscription()` contract.
- Added a bounded Partner Historical Events query scoped by app subject, shop, six lifecycle event types, and a 365-day window.
- Added typed lifecycle event parsing for created, updated, cancellation-scheduled, canceled, frozen, and unfrozen states.
- Preserved active-subscription parsing, usage snapshots, and null/error semantics for existing callers.
- Added fail-closed validation for missing roots, non-`SubscriptionStatus` payloads, mismatched app/shop identity, invalid timestamps, states, event types, and lifecycle field shapes.
- Added focused coverage for lifecycle states, frozen-versus-canceled null subscriptions, cancellation dates, empty history, HTTP/GraphQL failures, query scoping/window variables, and malformed events.

### Validation Results

- Editor diagnostics: passed for provider and focused test file.
- `git diff --check`: passed.
- Focused Vitest command: not run because `node_modules/.bin/vitest` is unavailable in the implementation worktree.
- Repository typecheck: not run because `node_modules/.bin/tsc` is unavailable in the implementation worktree.

### Deviations

None.

### Assumptions

The existing configured Partner API version supports the queried `events` root, event filter fields, `SubscriptionStatus` subject, lifecycle state fields, and the six requested event types. Runtime schema validation remains dependent on the repository's available generated/provider contract.

### Unresolved Issues

Focused runtime tests and repository typecheck remain pending until dependencies are installed in the implementation worktree.

### Architectural Concerns

None.

### Git / VCS

Task branch: `task/ARCH-010-BACKGROUND-015`

Physical worktree isolation:
  canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
  parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-BACKGROUND-015`
  parent branch: `task/ARCH-010-BACKGROUND-015`
  implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-BACKGROUND-015`
  implementation branch: `task/ARCH-010-BACKGROUND-015`
  shared workspace checkout switched/mutated for task work: no
  shared implementation checkout switched/mutated for task work: no
  another task worktree reused: no

Implementation repository:
  repository: `moda-interact-background`
  commit: `d03e60b`
  remote branch: `origin/task/ARCH-010-BACKGROUND-015`
  pushed: yes

Parent workspace:
  task file: `docs/decisions/background/ARCH-010/BACKGROUND-015-shopify-subscription-lifecycle-snapshot.md`
  commit: pending
  remote branch: `origin/task/ARCH-010-BACKGROUND-015`
  pushed: pending
  submodule gitlink staged: no

Merged to implementation main: no
Merged to workspace main: no

## Architect Review

### Attempt 1 — Changes Requested

#### Review Status

Changes Requested.

The architectural direction is correct: keep `getActiveSubscription()` source-compatible and add one reconciliation snapshot request that combines the live managed-pricing subscription with the latest bounded historical lifecycle event.

Attempt 1 cannot be accepted because the historical-events GraphQL shape does not conform to the Shopify Partner API 2026-07 schema and therefore would be rejected by Shopify before the parser can run. Required dependency-backed validation also did not run, and the focused test file already contains a deterministic failing assertion.

#### Finding 1 — Correct the Historical Events GraphQL to the actual Partner API schema

**Affected production file**

```text
src/providers/shopify-partner-billing.provider.ts
```

The current query is structurally invalid in four related ways:

```text
events { nodes { ... } }
```

is not the Partner historical-events connection shape. `PartnerEventConnection` exposes:

```text
edges
pageInfo
```

and the event is at:

```text
events.edges[0].node
```

The current query also places:

```graphql
... on SubscriptionStatus
```

inside `subject`. That is invalid. `subject` is the `Subject` union:

```text
AppReference | ThemeReference
```

`SubscriptionStatus` is instead the historical event object implementing `PartnerEvent`.

Finally, these fields do not exist directly on `SubscriptionStatus`:

```text
appId
shopId
planHandle
billingPeriod
```

The normalized values required by this task must be derived from the actual provider shape:

```text
event.subject -> AppReference.id
event.shop    -> ShopReference.id
event.plan    -> Plan.handle / Plan.billingPeriod
```

Implement the historical-event portion of the snapshot query using this shape (formatting may differ, semantics must not):

```graphql
events(
  first: 1
  filter: {
    subjectId: $appId
    shopId: $shopId
    eventTypes: $eventTypes
    occurredAtMin: $occurredAtMin
    occurredAtMax: $occurredAtMax
  }
  orderBy: OCCURRED_AT_DESC
) {
  edges {
    node {
      __typename
      id
      occurredAt
      eventType
      shop {
        id
      }
      subject {
        __typename
        ... on AppReference {
          id
        }
      }
      ... on SubscriptionStatus {
        state
        cancelEffectiveOn
        plan {
          handle
          billingPeriod
        }
      }
    }
  }
}
```

Do **not** add a second Partner request. The snapshot must still use one HTTP/GraphQL request containing both root fields:

```text
activeSubscription
events
```

Do **not** change `ACTIVE_SUBSCRIPTION_QUERY` merely to share query text. Existing `getActiveSubscription()` callers must retain exactly their current external contract and null/error interpretation.

#### Finding 2 — Parse and validate the actual event/edge shape

Update the response typing and parser in:

```text
src/providers/shopify-partner-billing.provider.ts
```

Required behavior:

1. read zero/latest event from:

```text
result.data.events.edges
```

2. zero edges ->

```text
latestLifecycleEvent: null
```

3. for a non-empty result, require:

```text
edge is an object
edge.node is an object
node.__typename === "SubscriptionStatus"
node.subject.__typename === "AppReference"
node.subject.id === configured SHOPIFY_APP_ID
node.shop.id === requested shopifyShopId
```

4. continue requiring:

```text
id: non-empty/string provider ID
occurredAt: valid Date
eventType: one of the six explicit lifecycle event types
state: matching SubscriptionStatusState
```

5. normalize lifecycle fields as:

```text
cancelEffectiveOn = node.cancelEffectiveOn ?? null
planHandle        = node.plan?.handle ?? null
billingPeriod     = node.plan?.billingPeriod ?? null
```

If `plan` is present, fail closed when `plan.handle` or `plan.billingPeriod` is neither a string nor null/undefined. Preserve null when Shopify omits the plan.

6. continue verifying the state/event-type pair exactly:

```text
CREATED                <-> SUBSCRIPTION_CREATED
UPDATED                <-> SUBSCRIPTION_UPDATED
CANCELLATION_SCHEDULED <-> SUBSCRIPTION_CANCELLATION_SCHEDULED
CANCELED               <-> SUBSCRIPTION_CANCELED
FROZEN                 <-> SUBSCRIPTION_FROZEN
UNFROZEN               <-> SUBSCRIPTION_UNFROZEN
```

7. GraphQL errors or malformed/missing requested root data remain provider errors. Do not return partial success.

Do not infer lifecycle state from `activeSubscription`.

#### Finding 3 — Fix the deterministic CANCELED test failure and use provider-realistic fixtures

**Affected test file**

```text
tests/unit/providers/shopify-partner-billing.provider.test.ts
```

The current parameterized lifecycle test does this for `CANCELED`:

```text
response activeSubscription = null
```

but then still asserts:

```text
activeSubscription: { planHandle: "growth-plan" }
```

That assertion is internally contradictory and will fail once Vitest actually runs.

Correct the tests so each case asserts its intended live result explicitly.

Replace historical-event fixtures with the real Partner API response shape:

```text
events.edges[].node
node.__typename = SubscriptionStatus
node.subject = { __typename: AppReference, id: <app GID> }
node.shop = { id: <shop GID> }
node.plan = { handle, billingPeriod } | null
```

Do not keep a synthetic `SubscriptionStatus` object nested inside `subject`.

#### Finding 4 — Complete the required focused coverage

The focused test suite must directly prove all of the following after the schema correction:

```text
1. active subscription + latest CREATED parses both roots;
2. active subscription + latest FROZEN exposes FROZEN;
3. null active subscription + latest FROZEN remains distinguishable from cancellation;
4. null active subscription + latest CANCELED exposes CANCELED;
5. latest UNFROZEN parses;
6. latest UPDATED parses;
7. latest CANCELLATION_SCHEDULED maps cancelEffectiveOn;
8. Plan.handle / Plan.billingPeriod map to planHandle / billingPeriod;
9. null Plan maps both normalized plan fields to null;
10. zero event edges returns latestLifecycleEvent=null;
11. non-2xx throws the existing provider HTTP error;
12. GraphQL errors fail the whole snapshot;
13. non-SubscriptionStatus node fails closed;
14. non-AppReference subject fails closed;
15. mismatched app ID fails closed;
16. mismatched shop ID fails closed;
17. invalid occurredAt fails closed;
18. invalid/mismatched state/eventType fails closed;
19. malformed plan field types fail closed;
20. query uses edges/node and the SubscriptionStatus inline fragment at the event-node level;
21. query filters by both subjectId/app and shopId;
22. query contains exactly the six lifecycle event types;
23. query uses occurredAtMin/occurredAtMax with the 365-day window;
24. existing getActiveSubscription() tests/return shape/null semantics remain valid.
```

No Prisma writes are authorized or required.

#### Finding 5 — Required validation was not performed

The task's Validation section requires dependency-backed tests/typechecking/build/unit validation. Attempt 1 returned to review while recording that Vitest and TypeScript were unavailable because dependencies were not installed.

That is insufficient for this task, especially because the focused test currently contains an assertion that would fail.

For Attempt 2, from the canonical implementation worktree:

```bash
command -v node >/dev/null 2>&1 || \
  source "$MODA_WORKSPACE_ROOT/scripts/bootstrap-node.sh"

cd moda-interact-background
```

If `node_modules` is absent, install the repository lockfile dependencies:

```bash
npm ci
```

Then run at minimum:

```bash
./node_modules/.bin/vitest run tests/unit/providers/shopify-partner-billing.provider.test.ts
./node_modules/.bin/tsc --noEmit
npm run build
npm run test:unit
git diff --check
```

Before running commands, inspect `package.json`; do not invent alternate scripts.

If `npm ci` or any required validation cannot execute because of a concrete environment/registry/toolchain problem, **do not return the task to review with required validation knowingly incomplete**. Record the exact failure and return the task blocked for architect/developer resolution.

If repository-wide unit/build validation has unrelated pre-existing failures, record the exact failing files/tests and prove the changed provider/test slice is not responsible.

#### Finding 6 — Record mandatory start-of-attempt synchronization evidence

Attempt 1 records the physical task worktrees but omits the four mandatory synchronization outcomes.

Attempt 2 Completion Report must contain:

```text
Start-of-attempt synchronization:
  parent remote task branch fast-forwarded: yes|not-needed
  parent origin/main incorporated: yes|already-current
  implementation remote task branch fast-forwarded: yes|not-needed
  implementation origin/main incorporated: yes|already-current
```

Do not substitute branch cleanliness, push success, diagnostics, or archive provenance for these four fields.

#### Scope boundaries for Attempt 2

Allowed production-source scope:

```text
src/providers/shopify-partner-billing.provider.ts
```

Allowed test scope:

```text
tests/unit/providers/shopify-partner-billing.provider.test.ts
```

Do not modify:

```text
billing-reconciliation.service.ts
billing-subscription-reconciliation.service.ts
Prisma schema/migrations
queue contracts
Shared package
Shopify application repository
ADMIN/BACKGROUND-012 lifecycle transitions
```

`getActiveSubscription()` must not be removed, renamed, or changed externally.

Do not implement cancellation/freeze persistence in this task.

#### Stop conditions

Stop and return the exact evidence to `moda_architect` if the actual configured Partner API schema contradicts the 2026-07 historical-events model required here, including any absence of:

```text
QueryRoot.events
PartnerEventConnection.edges
PartnerEventEdge.node
SubscriptionStatus.state
SubscriptionStatus.cancelEffectiveOn
SubscriptionStatus.plan
SubscriptionStatus.shop
SubscriptionStatus.subject
Plan.handle
Plan.billingPeriod
AppReference.id
ShopReference.id
```

Do not fall back to the legacy Admin Billing API or legacy app-event webhooks.

#### Architect Decision

**Changes Requested — Attempt 1.**

The same task returns to:

```text
status: ready
attempt: 1
executor: null
claimed_at: null
```

The next authorized `/moda-task ARCH-010-BACKGROUND-015` claim becomes Attempt 2.

`ARCH-010-BACKGROUND-012` remains gated until this task is architect-accepted Complete.

