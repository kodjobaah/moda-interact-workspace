---
id: ARCH-011-SYSTEM-TEST-001
architecture_id: ARCH-011
title: Validate prorated upgrades, concurrency and ARCH-010 regressions
task_kind: validation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: developer
completion_mode: manual
status: pending
priority: 90
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-011-DATABASE-001
- ARCH-011-SHARED-002
- ARCH-011-BACKGROUND-001
- ARCH-011-BACKGROUND-002
- ARCH-011-SHOPIFY-001
- ARCH-011-ADMIN-001
enables: []
created: 2026-09-13
updated: '2026-09-13'
---

# ARCH-011-SYSTEM-TEST-001: Validate prorated upgrades, concurrency and ARCH-010 regressions

## Execution gate

**Terminal/manual-gated. Do not auto-run when dependencies complete.**

The user explicitly invokes this task after ARCH-011 implementation integration/manual verification. No implementation/publication task may depend on it.

## Objective

Run one comprehensive integrated ARCH-011 validation covering merchant lifecycle, exact provider-cycle/effective-time behaviour, whole-period entitlement arithmetic, repeated upgrades, concurrency/idempotency, Admin audit/configuration and proof that ARCH-010 purchase/refund/capacity semantics remain unchanged.

Do not split lifecycle and concurrency into separate system-test tasks unless `moda_architect` creates a later amendment.

## Preconditions

Require all YAML dependencies architect-accepted Complete and deployed/testable in the target system-test environment. Record exact service/package/database versions/commits.

## A. Tier topology / direct-path scenarios

Validate active topology example:

```text
Free -> Starter -> Growth -> Scale
```

Required merchant behaviours:

```text
Free -> Starter immediate upgrade
Free -> Growth immediate direct upgrade
Free -> Scale immediate direct upgrade
Starter -> Scale immediate direct upgrade
Scale -> Starter lower-plan selection is next-cycle only
```

No test may require merchant traversal through adjacent tiers.

Invalid topology must fail closed in Shared/application and be rejected by database final-state enforcement.

## B. Free -> paid provider-cycle distinction

Test both provider-observable cases where environment/provider fixtures support them:

```text
Case 1: provider reports newly anchored currentBillingCycle
  => NEW_PROVIDER_CYCLE_FULL_ALLOWANCE
  => full opening paid allowance
  => no same-cycle target/delta

Case 2: provider preserves existing cycle and paid plan becomes current inside it
  => SAME_CYCLE_PRORATED
  => whole-period target entitlement
```

If live Shopify can expose only one case, fixture/integration coverage must prove the other deterministic branch; do not fabricate a claim about Shopify live behaviour.

## C. Usage-independent proration

Binding scenario:

```text
Starter allowance 100
Growth allowance 300
half-cycle provider-confirmed upgrade
target entitlement 200
alreadyGranted 100
additional grant 100
```

Repeat with different committed/reserved values. Additional grant must remain identical. Verify only granted quantity increases; committed/reserved/forfeited are preserved.

## D. Multiple upgrades in one provider cycle

Validate at minimum:

```text
Free -> Starter -> Growth -> Scale
```

with exact provider event times and one BillingPeriod. Prove chronological plan segments, whole-history target recalculation and no cumulative rounding drift.

Also validate a direct skip such as Free -> Scale produces only actual source/target segments.

## E. Unverified supersession

Validate:

```text
effective Starter
Growth REQUESTED, provider still Starter
merchant chooses Scale
=> Growth SUPERSEDED
=> new Starter -> Scale REQUESTED
```

Then validate race where provider already made Growth current before supersession request:

```text
=> supersession refused
=> reconcile/apply Growth first
=> later Scale upgrade may proceed
```

Lower target during unverified upgrade must be evaluated from still-effective plan and remain next-cycle downgrade.

## F. Downgrade rule

After an APPLIED same-cycle upgrade, lower tier must not become effective inside the current cycle. Verify no credit clawback. At next provider cycle boundary, accepted ARCH-010 downgrade/rollover opens the lower plan with full opening allowance.

## G. Provider effective-time proof

Verify same-cycle application uses exact matching provider lifecycle event `occurredAt`. Delayed worker observation must not shift segment boundary. Missing/mismatched event => NEEDS_ATTENTION and no grant.

## H. Idempotency/concurrency

Validate at minimum:

1. duplicate provider lifecycle event processed twice => one APPLIED transition/one grant;
2. two Background reconcilers race => one successful transition application;
3. conversation reservation races upgrade grant => Serializable/versioned-CAS retry preserves both valid outcomes without lost update;
4. two merchant upgrade requests race => database permits at most one unresolved transition;
5. stale Admin topology update races another topology write => invalid final topology rejected, no partial commit;
6. provider event replay after APPLIED does not create another segment.

## I. Top-up gate

While transition status is REQUESTED / PROVIDER_CONFIRMED / NEEDS_ATTENTION:

```text
new top-up purchase blocked server-side
existing top-up lots continue normal use/refund lifecycle
```

After APPLIED, top-up uses current provider tier/meter.

## J. ARCH-010 regression invariants

Prove ARCH-011 does not alter:

```text
RecoveryCreditPurchase lifecycle/provenance/refund valuation
purchased-credit FIFO allocation
promotional credit allocation
lifetime Free balance
existing admitted conversation reservations
freeze/unfreeze/cancellation/uninstall/reinstall semantics
capacity order
```

Capacity order remains:

```text
PAID: promotion -> included -> purchased FIFO -> lifetime Free -> block
FREE: promotion -> purchased FIFO -> lifetime Free -> block
```

## K. Admin validation/audit

Verify:

```text
canonical topology rendered correctly
direct skip described as valid upgrade
invalid topology rejected by DB even if application preflight is bypassed
economics guardrail remains independent and enforced
transition audit shows provider cycle/effective event/segments/target/granted/delta
usage shown separately from proration evidence
no provider secrets exposed
```

## Evidence / completion

Record exact commands, environment, commit/package versions, provider fixture/live identifiers, database rows relevant to each scenario, and screenshots/log excerpts where appropriate.

Any failure returns task to architect review with exact reproduction; do not patch implementation from the system-test task.

## Completion Report

### Status
Not started / manual-gated.

### Architect Review
Pending.
