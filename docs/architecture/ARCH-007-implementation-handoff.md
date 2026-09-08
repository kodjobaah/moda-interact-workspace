# ARCH-007 implementation handoff

> Reconciled: 2026-09-08  
> Coordinator: `moda_architect`  
> Canonical architecture: [`ARCH-007-shopify-billing-usage-cost-control.md`](ARCH-007-shopify-billing-usage-cost-control.md)

This page is the compact pickup document for a new architect. It does not replace task YAML or the canonical architecture.

## Read order

1. [`ARCH-007-shopify-billing-usage-cost-control.md`](ARCH-007-shopify-billing-usage-cost-control.md) — architecture/invariants/task graph.
2. [`../product/pricing-and-billing-model.md`](../product/pricing-and-billing-model.md) — readable product/commercial model and implementation mapping.
3. `docs/decisions/<domain>/ARCH-007/_index.md` — domain frontier.
4. The exact task file being executed — authoritative status/dependencies/correction contract.
5. For the cross-architecture UI dependency, read `docs/decisions/shopify/ARCH-005/SHOPIFY-004-complete-merchant-ui-internationalisation.md` and its key manifest.

Do not derive current state from root-level `*-overlay.zip`, `*.patch` or old amendment transport files. They are historical delivery artifacts. Current files under `docs/architecture/` and `docs/decisions/` are authoritative.

## Product model in one screen

```text
Merchant commercial unit
  RECOVERY_CONVERSATION

Free
  $0
  5 lifetime base allowance
  + signed per-shop Admin adjustments
  -> purchased recovery credits
  -> block when neither source has capacity

Starter
  $35/month
  200 included/month
  -> purchased recovery credits
  -> $0.05 normal overage

Growth
  $75/month
  500 included/month
  -> purchased recovery credits
  -> $0.04 normal overage

Scale
  $149/month
  1,200 included/month
  -> purchased recovery credits
  -> $0.03 normal overage
```

Every plan may buy recovery-credit packs repeatedly. Purchased credits do not reset monthly. Exact pack quantity/monetary rates remain product configuration; monetary rates live in Shopify App Pricing. Paid/higher tiers are intended to receive cheaper pack rates.

### Free testing/support override

Do not mutate the Free plan or add environment/test-shop branches.

```text
base Free allowance = 5
effective allowance = 5 + SUM(BillingAllowanceAdjustment.quantity)
```

Example test shop:

```text
+95 signed adjustment -> effective allowance 100
```

A lower adjustment never rewrites historical usage; remaining capacity bottoms at zero. ADMIN-002 is the UI/audit owner for this mechanism; DATABASE-003 persistence is already Complete.

## WhatsApp/AI cost model

Raw inbound WhatsApp message != logical customer turn != merchant recovery charge. Authentication also does not imply unlimited AI entitlement.

```text
raw inbound fragments
  -> raw sender/global abuse admission
  -> if allowed: resolve + deduplicate + persist
  -> stable durable conversation
  -> 3s quiet / 10s max settle
  -> settled-turn sender/conversation/shop/global abuse admission
  -> reserve per-conversation OUTBOUND_AUTOMATED_MESSAGE capacity
  -> only then invoke CommerceAgent
  -> one reply
```

The per-conversation hard cap reserves one deterministic non-LLM terminal response. Once normal capacity is exhausted, do not invoke CommerceAgent. Customer inbound messages do not themselves consume the outbound metric.

Standalone product/support conversation scopes use a 24-hour inactivity lifecycle so the safety budget cannot be reset by creating a new conversation every turn.

## Current execution frontier

### Ready

- `ARCH-007-SHOPIFY-003` — **Ready, Changes Requested**, `attempt: 1`; next claim Attempt 2. The uninstall implementation is sound; restore only the accepted Shared 0.7.4 dependency baseline and revalidate.
- `ARCH-007-ADMIN-001` — Ready, Attempt 1.
- `ARCH-007-BACKGROUND-005` — Ready, Attempt 1.
- `ARCH-007-BACKGROUND-009` — Ready, Attempt 1.
- `ARCH-007-BACKGROUND-010` — Ready, Attempt 1.
- Cross-architecture `ARCH-005-SHOPIFY-004` — Ready, Attempt 1.

### Accepted Complete

- DATABASE-001/002/003/004/005/006
- SHARED-001/002/003/004/005/006
- SHOPIFY-001/002
- MESSAGING-001 Attempt 3
- BACKGROUND-001/002/003/004/006/007

### Dependency-gated

- `BACKGROUND-011` remains Pending behind BACKGROUND-010.
- `ADMIN-002` remains Pending behind ADMIN-001.
- `ADMIN-005` remains Pending behind ADMIN-001 (DATABASE-005 and SHARED-006 are Complete).
- `SHOPIFY-004` remains Pending behind ADMIN-005.
- `BACKGROUND-008` remains Pending behind BACKGROUND-005 and BACKGROUND-009.
- `GATEWAY-001` remains Pending behind BACKGROUND-008.
- ARCH-007 SYSTEM-TEST-001..005 remain Pending/manual-gated.

Current accepted/published Shared package:

```text
@modainteract/moda-interact-shared@0.8.0
```

## Dependency chains

### Core outbound/provider lifecycle

```text
BACKGROUND-004 Complete
MESSAGING-001 Complete
SHARED-004 Complete
  -> BACKGROUND-005 Ready
```

### Recovery-credit packs

```text
DATABASE-005 Complete
  -> SHARED-005 Complete
      -> SHARED-006 Complete / published 0.8.0
          -> BACKGROUND-009 Ready
          -> ADMIN-005 (still waits on ADMIN-001)
              -> SHOPIFY-004

BACKGROUND-005 + BACKGROUND-007 + BACKGROUND-009 + SHOPIFY-001
  -> BACKGROUND-008 billing worker/reconciliation
```

The generic BACKGROUND-007 publisher is Complete and remains metric-agnostic. Pack-purchase UsageEvents use that same persisted event-handle/idempotent App Events path.

### Fragmented inbound turns and abuse admission

```text
DATABASE-006 Complete
BACKGROUND-004 Complete
  -> BACKGROUND-010 Ready
      -> BACKGROUND-011 Pending
      -> SYSTEM-TEST-005 terminal/manual-gated after BACKGROUND-011
```

BACKGROUND-011 must integrate against the accepted post-BACKGROUND-010 worker flow.

### Admin path

```text
ADMIN-001
  -> ADMIN-002 (platform/shop safety + signed Free allowance adjustments)
  -> ADMIN-005 (after DATABASE-005 + SHARED-006; top-up pack plan mapping)

ADMIN-002 + BACKGROUND-007 + SHOPIFY-001
  -> ADMIN-003
```

## ARCH-005 cross-architecture internationalisation gate

`ARCH-005-SHOPIFY-004` is now Ready because `ARCH-005-SHOPIFY-002`, `ARCH-006-SHOPIFY-003`, and `ARCH-007-SHOPIFY-002` are all architect-accepted Complete.

The exact key/copy contract is:

`docs/decisions/shopify/ARCH-005/SHOPIFY-004-i18n-key-manifest.md`

Luna must translate every manifest value naturally into all 20 declared locale languages, preserve ICU placeholders exactly and preserve only the listed brand/technical tokens. ARCH-007-SHOPIFY-002 is Complete, so the previous overlap gate is satisfied. Claim ARCH-005-SHOPIFY-004 only once and follow its 32-key manifest exactly.

## System-test rule

ARCH-007 SYSTEM-TEST-001..005 and ARCH-005 system tests are terminal/manual-gated. SYSTEM-TEST-005 now covers inbound abuse admission as well as turn coalescing. Once all explicit YAML dependencies are Complete they may be promoted to `ready`, but `ready` is dependency-readiness only: they must remain dormant until the developer explicitly invokes expensive integrated validation.

No implementation, publication or infrastructure task may depend on a system-test task.


## Historical overlay artifacts

Root-level `ARCH-007-*.zip` / `.patch` files are historical transport artifacts used to apply earlier coordination changes. They are **not** current sources of truth. A new architect must read canonical architecture, task YAML, domain indexes and this handoff instead of inferring state from an old overlay filename.

## Git/publication rule

Repository agents implement/validate, commit and push both mirrored `task/<TASK_ID>` branches, return the task to `review`, and STOP. `moda_architect` accepts or returns Changes Requested. Repository agents must not merge/push `main` or stage an unmerged implementation submodule gitlink; developer/user owns final merges, `main` publication and final workspace submodule-pointer integration.

## Architect review hygiene

When accepting a task:
- set `status: complete`;
- clear `executor` and `claimed_at`;
- preserve `attempt`;
- write final `Architect Review: Accepted` evidence;
- update the domain `_index.md` and canonical ARCH-007 frontier/dependencies;
- only promote downstream implementation tasks when **all** YAML dependencies are Complete;
- promote a terminal/manual-gated system-test task to `ready` when all of its explicit YAML dependencies are Complete, but never auto-claim/auto-run it; execution requires explicit developer invocation.

When requesting changes:
- return the **same** task to `ready` unless a true external dependency makes it `blocked`;
- clear `executor`/`claimed_at`;
- preserve attempt so next claim increments it;
- put the exact bounded correction contract in the latest `## Architect Review`.
