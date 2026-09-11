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
attempt: 0
depends_on: []
enables:
  - ARCH-010-BACKGROUND-006
  - ARCH-010-BACKGROUND-013
  - ARCH-010-BACKGROUND-017
  - ARCH-010-SHOPIFY-005
created: 2026-09-11
updated: 2026-09-11
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
Not started.

### Files Changed
Populate during implementation.

### Work Completed
Populate during implementation.

### Validation Results
Populate during implementation.

### Git / VCS
Populate canonical isolated worktree/branch/commit/push evidence.

### Architect Review
Pending.
