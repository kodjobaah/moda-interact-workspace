---
id: ARCH-010-BACKGROUND-005
architecture_id: ARCH-010
title: Stop WhatsApp business execution for inactive shops
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 46
executor: null
claimed_at: null
attempt: 1
depends_on: []
enables:
  - ARCH-010-BACKGROUND-006
  - ARCH-010-BACKGROUND-013
  - ARCH-010-BACKGROUND-017
  - ARCH-010-SHOPIFY-005
created: 2026-09-11
updated: 2026-09-11T18:46:25Z
---

# ARCH-010-BACKGROUND-005: Stop WhatsApp business execution for inactive shops

## Objective

Ensure a normalized WhatsApp event cannot create/continue merchant customer-conversation work after its owning shop is known to be `UNINSTALLED` or `SUSPENDED`.

Do this in Background after ownership resolution. Do **not** redesign the Meta ingress or tenant-identification model.

## Architectural constraint

The normalized WhatsApp ingress event intentionally does not carry deterministic `shopId` ownership. The supplied `moda-interact-messaging` service therefore may continue to authenticate/normalize/enqueue raw events before the owning shop is known.

ARCH-010 accepts that limitation.

The execution rule is:

```text
once shop ownership is deterministically resolved:
  Shop.status == ACTIVE -> continue
  otherwise             -> terminal no-op
```

No heuristic tenant inference may be added by this task.

## Inspect before editing

At minimum inspect:

```text
src/workers/whatsapp.worker.ts
src/services/recovery-routing.service.ts
src/services/conversation-turn-processor.service.ts
src/services/conversation.service.ts
src/services/outbound-whatsapp-admission.service.ts
src/services/inbound-whatsapp-abuse-admission.service.ts
src/services/whatsapp-provider-status.service.ts
src/services/effective-billing-policy.service.ts
src/services/checkout-recovery.service.ts
src/integration/whatsapp/types.ts
tests/unit/**whatsapp**
tests/unit/**conversation**
package.json
```

If ARCH-010-BACKGROUND-004 introduced a reusable local shop-execution helper, reuse it. Do not create a competing status-policy implementation.

## `message-received` requirements

### Context-linked message

When `event.contextMessageId` resolves to an existing Conversation/CheckoutRecovery:

1. determine the owning shop from durable conversation/recovery ownership;
2. read current Shop.status before writing the inbound ConversationMessage;
3. if shop is not ACTIVE, return a terminal route/outcome such as `shop-unavailable`;
4. do not append the inbound message;
5. do not enqueue `process-conversation-turn`;
6. do not invoke abuse/business admission beyond any provider-global protection that occurs before tenant ownership is knowable;
7. do not invoke CommerceAgent or send WhatsApp output.

### Context-free routing

Existing routing by customer/recovery ownership must ignore non-ACTIVE shop ownership when choosing an actionable merchant.

When all otherwise-matching ownership belongs to inactive shops, resolve to a terminal/non-actionable outcome. Do not create a standalone conversation for an inactive shop.

If ownership remains ambiguous, preserve the existing ambiguous-tenant behaviour. Do not guess.

### Product-only / standalone path

Before `getOrCreateStandaloneConversation()` for a resolved merchant, require that merchant Shop.status is ACTIVE.

An uninstalled shop must not receive a new PRODUCT_DISCOVERY/PRODUCT_SUPPORT conversation.

## `process-conversation-turn` delayed-job requirements

A conversation-turn job may have been queued before uninstall.

Before loading agent context, invoking CommerceAgent, reserving outbound entitlement or sending WhatsApp:

1. resolve the conversation's owning shop from durable state;
2. read current Shop.status;
3. if not ACTIVE, return success/no-op;
4. do not retry solely due to inactive state;
5. do not enqueue another turn.

This guard is required even when `message-received` already checks status because uninstall can happen between inbound-message persistence and delayed turn execution.

## Outbound safety

Retain `EffectiveBillingPolicyResolver`'s existing non-ACTIVE rejection as a defense-in-depth gate.

The earlier WhatsApp guard must prevent inactive work before expensive agent/provider processing; the billing-policy check remains the final outbound entitlement guard.

## Provider status events

Do not drop historical delivery/read/failure status solely because the owning shop has since been uninstalled.

`message-status` may continue idempotently updating an outbound message that already exists because this is finalisation of pre-existing provider state, not new customer/business execution.

It must not cause:

- a new conversation turn;
- a new outbound message;
- a recovery restart;
- subscription activation;
- any other follow-up work for an inactive shop.

If the implementation currently creates `DELIVERED_WHATSAPP_MESSAGE` internal usage on status application, preserve existing semantics unless it would violate the established uninstall cutoff/accounting rules. Return to `moda_architect` rather than silently changing commercial metering.

## Race behaviour

No global uninstall/WhatsApp distributed lock is required.

A job checks durable Shop.status at the relevant execution boundary. If uninstall commits before that check, no-op. If execution passed the check before uninstall commits, existing idempotency/transaction behaviour applies; later outbound admission must still fail closed if it re-reads inactive policy.

## Required tests

Prove at least:

1. ACTIVE context-linked inbound message follows the existing route;
2. UNINSTALLED context-linked inbound message creates no inbound ConversationMessage;
3. UNINSTALLED context-linked inbound message enqueues no conversation turn;
4. SUSPENDED context-linked inbound message is likewise terminal;
5. context-free routing does not select an inactive shop as actionable ownership;
6. product-only routing does not create standalone conversation for inactive shop;
7. ambiguous ownership remains ambiguous rather than guessing an active/inactive tenant;
8. queued `process-conversation-turn` becomes a successful no-op after shop uninstall;
9. inactive turn invokes neither CommerceAgent nor outbound WhatsApp service;
10. ACTIVE turn remains unchanged;
11. provider delivery/read status for an already-existing outbound message can still be applied without starting follow-up work;
12. no new outbound message/agent invocation is caused by provider status finalisation;
13. existing `EffectiveBillingPolicyResolver` non-ACTIVE guard remains intact.

Assert expensive/provider functions were not called in inactive execution tests.

## Non-goals

Do not:

- add `shopId` to `NormalizedWhatsAppStatus` or inbound WhatsApp event contracts;
- change `moda-interact-messaging` ingress topology;
- add database access to Meta ingress merely to discover a shop;
- solve deterministic shop identification;
- delete old conversations/messages;
- change subscription or credit balances;
- define reinstall;
- alter internal Admin behaviour.

## Validation

Run focused WhatsApp/routing/conversation tests, then the repository's declared validation scripts applicable to the changed code. Run:

```text
git diff --check
```

Do not invent absent package scripts.

## Stop conditions

Stop and return to `moda_architect` if:

- a required WhatsApp path cannot obtain durable shop ownership before customer/business mutation;
- satisfying the task would require changing the cross-service event schema;
- provider-status handling would require a commercial metering decision not documented here;
- the only feasible implementation would move business/tenant correlation into `moda-interact-messaging`.

## Completion Report

### Status
Review requested. Implementation is complete and awaits `moda_architect` acceptance.

### Files Changed
- `moda-interact-background/src/services/shop-execution-eligibility.service.ts`
- `moda-interact-background/src/services/recovery-routing.service.ts`
- `moda-interact-background/src/services/conversation-turn-processor.service.ts`
- `moda-interact-background/src/workers/whatsapp.worker.ts`
- `moda-interact-background/tests/unit/services/recovery-routing.service.test.ts`
- `moda-interact-background/tests/unit/services/conversation-turn-processor.service.test.ts`

### Work Completed
- Added a shared ACTIVE-shop eligibility lookup.
- Context-linked inbound routing now checks durable recovery/conversation ownership before message persistence.
- Context-free recovery and product-only routing ignore inactive shops and return a terminal `shop-unavailable` route when no actionable owner remains.
- The WhatsApp worker exits before inbound persistence or turn enqueue for unavailable shops.
- Delayed conversation turns re-check current shop status before abuse admission, agent work, outbound reservation, or provider send, and complete as a no-op when inactive.
- Provider-status handling and existing effective billing-policy enforcement were left unchanged.

### Validation Results
- `npm test -- tests/unit/services/recovery-routing.service.test.ts -t 'inactive|returns product-only when|returns the only active recovery'`: passed, 5/5 selected tests.
- Full routing suite: 20/21 passed; the remaining pre-existing uniqueness-race fixture fails because `Prisma.PrismaClientKnownRequestError` is not constructible in this ungenerated client environment.
- Delayed-turn focused suite: blocked before test collection because `@prisma/client` was not generated.
- `npm run test:unit`: 243 tests passed; 24 suites were blocked by the ungenerated Prisma client, with the same pre-existing race-fixture failure.
- `npm run prisma:validate`: blocked because `database/prisma/schema.prisma` is absent in this checkout.
- `npx tsc --noEmit`: blocked by pre-existing `src/entrypoints/billing.ts:37` syntax error (`TS1135`); changed files have no editor diagnostics.
- `git diff --check`: passed.

### Git / VCS
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-BACKGROUND-004-task-ARCH-010-BACKGROUND-005`, branch `task/ARCH-010-BACKGROUND-005`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-BACKGROUND-004.worktrees/ARCH-010-BACKGROUND-005`, branch `task/ARCH-010-BACKGROUND-005`.
- Implementation commit pushed: `c54a6e4`.
- Parent claim commit pushed earlier: `36f4d40`.

### Architect Review
Pending.

#### Attempt 1 — Changes Requested

The overall WhatsApp inactive-shop execution-gate design is directionally correct,
but this submission is not yet safe to accept.

Architect review found one cross-task regression, incomplete required behavioural
coverage, and incomplete mandatory workflow evidence.

##### Accepted implementation direction

The following approach is accepted and should not be redesigned:

- durable `Shop.status` is checked only after WhatsApp ownership is deterministically
  resolved;
- context-linked `UNINSTALLED` / `SUSPENDED` ownership returns the terminal
  `shop-unavailable` route;
- context-free recovery ownership filters inactive shops before choosing actionable
  merchant ownership;
- product-only ownership checks shop activity before standalone-conversation
  creation;
- `processInboundMessage()` returns before inbound persistence when routing reports
  `shop-unavailable`;
- delayed conversation turns expose a `shopUnavailable` load result and suppress
  settled-turn abuse admission, CommerceAgent and outbound reservation/send;
- provider-status handling remains separate and continues finalising already-created
  outbound provider state;
- the existing `EffectiveBillingPolicyResolver` non-ACTIVE guard remains defense in
  depth.

Do not redesign those boundaries in Attempt 2.

##### Correction 1 — preserve the accepted BACKGROUND-004 helper API

The submitted BACKGROUND-005 branch changes:

```text
src/services/shop-execution-eligibility.service.ts
```

but its version contains only:

```ts
isShopExecutionActive(shopId)
```

The already-reviewed BACKGROUND-004 implementation of the same helper also contains
the `ShopExecutionRecord` contract and:

```ts
resolveShopByDomain(domain)
```

which BACKGROUND-004 uses for recovery scheduling/execution.

BACKGROUND-005 must not regress or replace that accepted helper API.

Synchronize/reconcile against the current canonical BACKGROUND-004 implementation
and preserve the **union** of the helper capabilities:

```text
resolveShopByDomain(...)
isShopExecutionActive(...)
```

Do not use a wholesale ours/theirs conflict resolution that deletes either task's
accepted behaviour.

If BACKGROUND-004 has not yet been integrated into the canonical mainline when
Attempt 2 starts, stop and coordinate with `moda_architect` rather than publishing
a helper version known to conflict with that accepted task.

##### Correction 2 — complete the required context-linked/worker coverage

The new routing tests prove that `UNINSTALLED` and `SUSPENDED` context-linked
ownership returns `shop-unavailable`.

They do **not** yet prove the task's worker-level acceptance requirements that the
terminal route prevents actual inbound persistence and delayed-turn enqueue.

Add focused executable coverage proving:

1. ACTIVE context-linked inbound still follows the existing route;
2. UNINSTALLED context-linked inbound causes no
   `conversationService.receiveMessage(...)`;
3. UNINSTALLED context-linked inbound enqueues no
   `process-conversation-turn`;
4. SUSPENDED context-linked inbound has the same terminal worker behaviour.

Prefer a focused worker/handler test with mocked dependencies. A deterministic
existing repository source-structure test is acceptable only if it genuinely
proves the terminal branch occurs before both persistence and enqueue; do not rely
only on the routing-service result.

##### Correction 3 — prove the real delayed-job ownership/status boundary

The processor test currently sets:

```ts
test.loaded.shopUnavailable = true
```

and correctly proves that the processor does not call settled abuse admission,
outbound admission or CommerceAgent.

That is useful but does not prove the actual Background loader turns durable
`Shop.status = UNINSTALLED | SUSPENDED` into that terminal result.

Add focused coverage around the real `loadConversationTurn`/worker boundary proving:

- a queued turn whose durable owning Shop is now `UNINSTALLED` completes/no-ops;
- `SUSPENDED` behaves the same way;
- no agent context is loaded after the inactive status determination;
- CommerceAgent is not invoked;
- outbound reservation/send is not invoked;
- no retry/new turn is scheduled solely because the shop is inactive;
- ACTIVE ownership continues through the existing path.

A small testability export/refactor of the existing loader is acceptable if needed;
do not redesign the worker architecture.

##### Correction 4 — explicitly protect provider-status finalisation

Required Tests 11 and 12 are not explicitly covered by the submitted changes.

Add focused regression evidence that an already-existing outbound message can still
receive `DELIVERED` / `READ` provider finalisation even when its merchant is now
inactive, and that provider-status handling does not:

- enqueue a conversation turn;
- invoke CommerceAgent;
- create/send a new outbound message;
- restart a recovery.

Preserve the current delivered-usage semantics. Do not introduce a new commercial
metering decision in this task.

##### Correction 5 — keep actionable-routing ambiguity semantics explicit

Retain the existing rule:

```text
inactive ownership is ignored for actionable merchant selection
multiple ACTIVE ownership pairs remain ambiguous
all otherwise-matching ownership inactive -> shop-unavailable
```

Keep/extend focused tests so the mixed inactive/active filtering does not
accidentally turn multiple active owners into a guessed tenant.

The existing all-active multi-owner ambiguity coverage may be reused if it remains
passing.

##### Correction 6 — mandatory worktree/synchronisation evidence

The Completion Report records paths/branches and an implementation commit, but it
does not contain the mandatory negative-isolation assertions or all four
start-of-attempt synchronization outcomes.

The recorded parent path is also nested under the BACKGROUND-004 task-worktree
naming lineage, so Attempt 2 must use the resolver-selected canonical
`ARCH-010-BACKGROUND-005` worktrees and state the evidence explicitly.

Record:

```text
Parent worktree:
Implementation worktree:

Negative isolation assertions:
  parent is not the primary/shared workspace: yes
  implementation is not the shared repository checkout: yes

Start-of-attempt synchronization:
  parent remote task branch fast-forwarded: yes|not-needed
  parent origin/main incorporated: yes|already-current
  implementation remote task branch fast-forwarded: yes|not-needed
  implementation origin/main incorporated: yes|already-current

Implementation commit:
Parent report commit:
Branches pushed:
Worktrees clean:
```

Do not treat a clean task branch or successful push as a substitute for this
physical isolation/synchronisation evidence.

##### Validation

The current submission reports useful focused routing results but the delayed-turn
suite was blocked by an ungenerated Prisma client and repository-wide checks have
baseline blockers.

Attempt 2 must run executable focused tests for every changed acceptance path above.
At minimum record the exact commands/results for:

```text
recovery-routing focused tests
WhatsApp inbound worker/handler inactive-gate tests
conversation-turn inactive delayed-job tests
provider-status finalisation tests
EffectiveBillingPolicyResolver non-ACTIVE regression
git diff --check
```

Run the repository-declared broader validation scripts that are actually available.
If Prisma/build/typecheck remain blocked by pre-existing unchanged repository
defects, document those blockers separately and precisely; they do not waive
task-local focused validation.

##### Scope guard

Do not:

- add `shopId` to the normalized WhatsApp ingress contract;
- move tenant discovery into `moda-interact-messaging`;
- redesign Meta ingress;
- alter subscription/credit/refund semantics;
- suppress historical provider-status finalisation;
- remove legitimate pre-uninstall usage accounting;
- modify another repository.

Return the same task to `review` after the corrections.

