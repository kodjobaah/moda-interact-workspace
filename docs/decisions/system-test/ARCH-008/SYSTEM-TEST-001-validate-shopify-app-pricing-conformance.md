---
id: ARCH-008-SYSTEM-TEST-001
architecture_id: ARCH-008
title: Validate Shopify App Pricing and Admin billing progressive disclosure
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 100
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-008-BACKGROUND-001
  - ARCH-008-BACKGROUND-002
  - ARCH-008-ADMIN-001
  - ARCH-008-ADMIN-002
  - ARCH-008-ADMIN-003
  - ARCH-007-SHOPIFY-004
enables: []
created: 2026-09-09
updated: 2026-09-09
---

# ARCH-008-SYSTEM-TEST-001: Validate Shopify App Pricing and Admin billing progressive disclosure

## Architecture

Canonical: `docs/architecture/ARCH-008-shopify-app-pricing-conformance.md`

## Objective

Prove in an approved Shopify development/test environment that Moda uses Shopify App Pricing correctly, grants recovery-credit packs only from provider-confirmed aggregate meter usage, and exposes the resulting lifecycle through understandable progressive-disclosure Admin billing surfaces.

## Terminal/manual-gated invariant

This is a **terminal architecture validation task**.

Do not execute merely because it becomes Ready. The developer/user may first manually exercise the integrated implementation and must explicitly invoke this task.

No implementation/publication/infrastructure task may depend on this task.

## Required preflight

1. Every YAML dependency is Complete and architect-accepted.
2. Developer explicitly invokes the task after manual validation.
3. Use only approved development/test Shopify app/store/plan/meter configuration.
4. Capture no secret values in evidence.
5. If application behavior fails, record reproducible evidence and return to `moda_architect`; do not fix application repositories from system-test.

## Scenario A — Shopify App Pricing subscription authority

Validate at least:

- one mapped Free plan;
- one mapped paid recurring + usage plan.

Prove:

1. merchant plan selection uses Shopify-hosted pricing flow;
2. callback/redirect plan handle is re-verified through authoritative provider subscription projection;
3. Partner `activeSubscription` identifies active plan and usage items;
4. no Manual Pricing/Billing API charge-creation path is required.

## Scenario B — App Events 202 semantics and 409 contract

For a billable usage event:

1. durable local UsageEvent exists;
2. App Events receives it;
3. local state becomes `REPORTED`;
4. Admin displays `Submitted to Shopify`, not Confirmed/Billed;
5. provider quantity catches up later;
6. replay with same durable identity does not duplicate provider usage.

For 409:

- if a safe deterministic live 409 can be produced, prove the same idempotency key is retried;
- otherwise use accepted repository provider-contract test evidence and explicitly record that live 409 generation is non-deterministic. Do not force an unsafe race.

## Scenario C — Recovery-credit pack confirmation

For a pack-enabled plan:

1. request one pack;
2. exactly one RecoveryCreditPurchase + one +1 pack UsageEvent exist;
3. immediately after App Events receipt:
   - UsageEvent is `REPORTED` / Submitted to Shopify;
   - purchase remains `PENDING_BILLING` / Awaiting Shopify confirmation;
   - purchased-credit entitlement has not increased;
4. after Partner pack-meter usage quantity increases by one:
   - exactly one purchase becomes ACTIVE;
   - credits are granted exactly once;
5. repeat reconciliation and prove no second grant.

Repeat with two equivalent pack requests and provider quantity increase of two.

## Scenario D — Received but not provider-confirmed pack event

Use a safe test-only scenario that can be received by App Events without increasing the intended pack meter quantity.

Prove:

- receipt can occur;
- intended provider quantity does not increase;
- pack remains unactivated;
- Admin does not invent an exact async provider failure reason;
- Dev Dashboard App Billing Event logs are the manual source for exact validation details when required.

Do not modify production meter configuration.

## Scenario E — aggregate ambiguity

Using deterministic fixtures where live provider generation would be unsafe/impossible:

- create pending eligible purchases with different `creditsGranted`/pack snapshots;
- supply provider aggregate confirmation for only a subset;
- prove ambiguous subset grants no arbitrary credits and surfaces attention/discrepancy.

## Scenario F — normal recovery independence

Prove a normal paid recovery can complete while Partner reconciliation is delayed/unavailable. Later mismatch may be visible but must not roll back completed recovery or fabricate financial correction.

## Scenario G — global Admin Billing progressive disclosure

Validate protected `/billing` as a platform admin.

### Default Overview

- default URL/view renders Overview;
- visible primary content is compact business summary;
- no expanded plan forms;
- no full App Event ledger;
- no platform policy control form.

### Plans

- Plans tab deep link works;
- catalogue is compact;
- Register opens right-side drawer;
- Edit one plan opens right-side drawer;
- drawer close + browser back preserve sensible URL state;
- existing plan mutation safety remains functional in approved dev/test data.

### Recovery packs

- compact pack list is paginated;
- pending pack reads `Awaiting Shopify confirmation`;
- active pack reads `Active`;
- detail drawer exposes safe linked event diagnostics and no secrets.

### App Events

- compact table contains only primary columns;
- `REPORTED` reads `Submitted to Shopify`;
- detail drawer exposes attempts/provider summary/handle/submitted time;
- filter/pagination/deep-link behavior works.

### Controls

- existing platform billing controls are isolated to Controls tab;
- no regression to authorization/audit behavior.

## Scenario H — Tenant Directory Billing progressive disclosure

For one selected tenant:

1. keep `Administration | Recovery Logs | Billing` top-level navigation;
2. Billing defaults to Overview;
3. exactly four internal sub-tabs work: Overview, Usage, Shopify, Activity;
4. Overview does not show the App Event ledger;
5. no active override is shown concisely as `Default policy`, not a large empty override panel;
6. Usage groups entitlement values and advanced limits disclosure;
7. Shopify isolates provider sync/reconciliation information and uses concise unavailable state when no snapshot exists;
8. Activity shows compact pack + App Event lists;
9. event/pack drawers remain scoped to selected tenant;
10. attempt to deep-link a different tenant's event/purchase under the current tenant must return not found/denied rather than leak data.

## Scenario I — usability smoke check for a new operator

Without relying on hidden implementation knowledge, verify the default global and tenant Billing views make these questions answerable without opening raw event diagnostics:

- What plan is active?
- Is billing healthy/needs attention?
- Is a recovery pack pending or active?
- Where do I inspect App Event history if needed?

Record screenshots/evidence only if they contain no secret/customer-sensitive data beyond approved test fixtures.

## Acceptance Criteria

- [ ] Shopify App Pricing remains the plan/usage architecture; no Manual Pricing migration is required.
- [ ] `202` is evidenced as receipt/submission, not individual billing confirmation.
- [ ] App Events identity is idempotent under replay and 409 contract is covered.
- [ ] Pack credits remain ungranted until provider aggregate meter confirms units.
- [ ] Provider-confirmed units activate exactly the safe number of purchases once.
- [ ] Ambiguous partial matching fails closed.
- [ ] Normal recovery is independent of reconciliation latency/failure.
- [ ] Global Billing uses five progressive-disclosure views and drawers.
- [ ] Tenant Billing uses four progressive-disclosure views and drawers.
- [ ] `REPORTED` is displayed `Submitted to Shopify` and `reportedAt` as `Submitted at`.
- [ ] Detail drawers expose no secrets and tenant detail is tenant-scoped.
- [ ] Browser/deep-link navigation works without client-state-only assumptions.

## Validation / evidence

Run only the architecture-level system tests and browser flows required by this task against approved test configuration. Record:

- environment identity;
- test shop/app identifiers in non-secret form;
- plan/meter handles in non-secret form;
- provider quantity before/after where relevant;
- local durable states before/after;
- browser route/query states for tabs/drawers;
- screenshots only when safe;
- exact pass/fail result for every scenario.

Do not modify production application code. Return failures to `moda_architect`.

## Stop / return rule

After validation, complete Completion Report, set task `review`, return to `moda_architect`, and STOP.

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

None

### Deviations

None

### Assumptions

None

### Unresolved Issues

None

### Architectural Concerns

None

## Architect Review

### Review Status

Pending

### Review Notes

None

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

None
