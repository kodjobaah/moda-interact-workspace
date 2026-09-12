# ARCH-010 Final Consolidation / Architect Review

Date: 2026-09-11  
Coordinator: `moda_architect`

## Overall decision

**ARCH-010 architecture is Agreed and implementation-ready. It is not yet Implemented.**

The twelve behavioural iterations plus the Iteration 11B Shopify-event gate have been consolidated into one final merchant lifecycle model. The final pass found no missing merchant lifecycle state requiring another feature iteration.

Implementation completion still requires:

1. every required repository task to be implemented and architect-accepted;
2. developer manual verification of the integrated behaviour;
3. explicit execution and acceptance of the four terminal/manual-gated ARCH-010 system-test tasks.

## What was reviewed

The consolidation pass reviewed:

- the canonical ARCH-010 architecture document;
- all ARCH-010 task files in Admin, Background, Database, Gateway, Shared and Shopify;
- the current source tree used when those tasks were authored;
- task frontmatter status/dependencies/enables;
- current agent/task workflow requirements from `.codex/agents/moda_architect.toml`;
- current Shopify App Pricing documentation for subscription state, historical events, usage/App Events, usage-only plans and provider refund/credit behaviour.

## Final architectural invariants

### Subscription authority

- Shopify App Pricing is commercial subscription authority.
- Local `BillingPlan` rows are Moda mapping/entitlement configuration, not the live Shopify plan catalogue.
- `Subscription` is the durable local current/pending projection.
- Partner `activeSubscription` plus Historical Events provide current/pending/provider-lifecycle evidence.
- `activeSubscription = null` alone does not prove cancellation for an established merchant.

### Lifetime Free entitlement

- Every shop receives the shop-lifetime Free grant exactly once at first verified subscription activation, whether the first plan is Free or Paid.
- The current default is 5 recoveries, snapshotted from platform policy.
- Plan change, renewal, uninstall, reinstall, cancellation or freeze never resets/regrants it.

### Final capacity order

```text
Paid
  monthly included
  -> promotional
  -> purchased
  -> lifetime Free
  -> BLOCK NEW RECOVERY ADMISSION

Free
  promotional
  -> purchased
  -> lifetime Free
  -> BLOCK NEW RECOVERY ADMISSION
```

No automatic paid overage exists.

Here `BLOCK NEW RECOVERY ADMISSION` means capacity exhaustion prevents a new recovery from being admitted; it does not terminate already-admitted conversations or remove dashboard/history/billing/support access.

### Credit ownership

- Paid included credits are BillingPeriod-scoped and do not roll over.
- **Superseded by the 2026-09-12 promo amendment:** new promotional capacity comes from expiring merchant-selected GLOBAL/PLAN/SHOP campaigns; campaign/grant history remains durable and non-refundable.
- Purchased top-up credits are shop-lifetime, survive plan/lifecycle changes and are refundable only while unused/unheld according to purchase-lot accounting.
- Promotional capacity is consumed before purchased capacity so merchant-funded refundable credits are preserved longer.

### Free App Pricing billing cycle

A Free Shopify App Pricing contract may still have a provider BillingPeriod because it carries the recovery-credit-pack usage meter.

That provider BillingPeriod is App Event/commercial scope only. It never replenishes the lifetime Free recovery grant.

### Lifecycle execution gates

The architecture distinguishes:

```text
capacity exhaustion
NO_CONTRACT
UNINSTALLED/inactive Shop
FROZEN subscription
provider-period DRAINING/reconciling
```

These states are not aliases.

- Capacity exhaustion blocks new recovery initiation only; existing admitted conversations continue.
- `NO_CONTRACT`, inactive/uninstalled and `FROZEN` block new shop business execution while preserving owned historical balances.
- Frozen checkout/cart queued events terminate early; `order.completed` may perform only terminal safety bookkeeping on already-existing recovery state.

### Billing actions

- Plan changes use Shopify-hosted App Pricing plus Partner current/pending state.
- Moda does not use `appSubscriptionCreate` for ARCH-010 plan changes.
- Moda does not call `appSubscriptionCancel`; Shopify cancellation state is observed/reconciled.
- Recovery-credit top-ups use Shopify App Pricing usage meter + App Event, not `appPurchaseOneTimeCreate`.
- Partial purchased-credit refunds are human-settled against Shopify provider billing evidence; ARCH-010 does not automate negative App Events as the refund mechanism.

## Provider documentation verification

The final pass re-verified the provider assumptions against Shopify developer documentation current on 2026-09-11:

- Shopify App Pricing / Active Subscription / Historical Events:  
  `https://shopify.dev/docs/apps/launch/billing/shopify-app-pricing`
- App Pricing migration, including repeated one-time charges represented by App Events:  
  `https://shopify.dev/docs/apps/launch/billing/shopify-app-pricing/migrating-to-shopify-app-pricing`
- Usage-based and usage-only plan behaviour:  
  `https://shopify.dev/docs/apps/launch/billing/shopify-app-pricing/subscription-billing/setup-usage-charges`
- App charge refunds/credits:  
  `https://shopify.dev/docs/apps/launch/billing/billing-adjustments/refund-app-charges`

No provider fact discovered during this verification requires a new ARCH-010 implementation iteration.

## Consolidation findings corrected

### 1. Historical iteration layering

Earlier task files sometimes contained an original rule followed by an Iteration 11/12 amendment. Examples included pre-promotional fallback wording.

The final task contracts now state the final integrated rule directly. Implementation agents should not need to infer which historical paragraph wins.

### 2. Task reverse-dependency drift

After twelve iterations, several `enables:` lists no longer matched actual `depends_on` references.

The final pass regenerated `enables` from the dependency graph. `depends_on` remains the eligibility authority; `enables` is now a consistent reverse index.

### 3. Shared index omission

`ARCH-010-SHARED-003/004` existed but were missing from the Shared `_index.md` table. The final index includes all six Shared tasks.

### 4. Workflow completion sections

Some later overlay-created tasks lacked a formal `Completion Report` section even though the execution template requires agents to update it when claiming/submitting a task.

Every active implementation/publication ARCH-010 task now contains a Completion Report. Missing explicit Stop/Non-goal/Validation sections on bounded tasks were also normalized.

### 5. Architecture status

The canonical architecture still said `proposed` and described only early iterations as defined. It is now `agreed` and records the complete behavioural scope.

### 6. Subscription-history wording

An early invariant promised a later append-only local subscription-history model, but ARCH-010 ultimately did not need one. The final architecture now states the real model explicitly:

- local current/pending `Subscription` projection;
- local exact BillingPeriod history;
- latest provider lifecycle evidence for reconciliation;
- Shopify Historical Events as provider-authoritative full lifecycle history.

No duplicate local provider-history table is required by ARCH-010.

### 7. Terminal system validation was missing

Four manual-gated system-test tasks now define final integrated validation without blocking implementation:

- `ARCH-010-SYSTEM-TEST-001` — core subscription/capacity/App Pricing lifecycle;
- `ARCH-010-SYSTEM-TEST-002` — uninstall/reinstall/cancellation/freeze execution gates;
- `ARCH-010-SYSTEM-TEST-003` — partial purchased refunds + promotional operations;
- `ARCH-010-SYSTEM-TEST-004` — final cross-scenario acceptance matrix.

## Task graph audit

Final counts:

```text
all ARCH-010 task files:         64
active tasks:                    63
superseded tasks:                 1
ready implementation tasks:     14
pending implementation tasks:   45
pending manual system tests:      4
```

Domain totals:

```text
Shopify       20   (1 superseded)
Background    19
Database       9
Shared         6
Admin          5
Gateway        1
System Test    4
```

Graph checks:

```text
missing ARCH-010 dependency references: 0
internal dependency cycles:              0
non-system task -> system-test deps:     0
enables/reverse-dependency mismatches:   0
```

## Task-size review

Some tasks are intentionally detailed because they protect concurrency/provider-boundary state, especially:

- DATABASE-004 / DATABASE-007;
- BACKGROUND-006 / 007 / 009 / 010 / 012 / 016;
- SHOPIFY-012.

They remain acceptable as bounded tasks because each has one repository, one primary capability, explicit dependencies, deterministic state transitions, focused acceptance criteria and stop conditions. The previously over-broad billing-options UI work is already split across SHOPIFY-009 through SHOPIFY-015 rather than being recombined.

If implementation reveals a task actually requires a second independent mechanism, the agent must stop and return that scope to `moda_architect` rather than widening the task.

## Deliberate future scope

The following are not unresolved ARCH-010 defects:

- automatic campaign marketing delivery or coupon-code mechanics;
- continuous automatic enrolment of future merchants into an active campaign;
- self-service merchant provider refund settlement;
- automatic negative-App-Event top-up refunds;
- subscription-fee refund ownership by Moda;
- automatic paid overage;
- local duplicate append-only Shopify subscription history;
- deterministic shop identity redesign;
- mid-cycle plan-entitlement segmentation/proration if unexpected immediate Shopify plan changes become normal provider behaviour.

## Architect conclusion

**ARCH-010 is approved for implementation.**

Use the individual task files and `ARCH-010-implementation-handoff.md` as the execution frontier. Do not start terminal system tests until their dependencies are complete, architect-accepted and the developer explicitly invokes them.
