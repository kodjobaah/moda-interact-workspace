---
id: ARCH-007-BACKGROUND-008
architecture_id: ARCH-007
title: Add independent billing worker for publication, subscription sync, reconciliation and uninstall drain
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
status: review
priority: 120
executor: copilot
claimed_at: 2026-09-08T19:10:31Z
attempt: 1
depends_on:
  - ARCH-007-BACKGROUND-005
  - ARCH-007-BACKGROUND-007
  - ARCH-007-BACKGROUND-009
  - ARCH-007-SHOPIFY-001
enables: 
  - ARCH-007-ADMIN-004
  - ARCH-007-GATEWAY-001
  - ARCH-007-SYSTEM-TEST-002
  - ARCH-007-SYSTEM-TEST-003
created: 2026-09-07
updated: 2026-09-08T20:19:00Z
---

# ARCH-007-BACKGROUND-008: Add independent billing worker for publication, subscription sync, reconciliation and uninstall drain

## Architecture

Canonical: `docs/architecture/ARCH-007-shopify-billing-usage-cost-control.md`

## Objective

Create the independently deployable billing worker runtime that continuously recovers durable billing work, reconciles Shopify subscription/usage state and prioritizes valid pre-uninstall events without coupling billing to recovery workers.

## Context

ARCH-007 cannot rely on callbacks or one-shot BullMQ jobs. Shopify plan changes can occur externally; Redis jobs can be lost; App Events pending rows must be recoverable from PostgreSQL.

## Scope

Background billing entrypoint/runtime/router/scheduler, Partner API subscription/usage reconciliation service and readiness integration following existing worker-process conventions.

## Out of Scope

- Render deployment declarations (GATEWAY-001).
- Merchant request projection implementation in moda-interact.
- Admin UI/actions.
- System tests.

## Requirements

- Add `src/entrypoints/billing.ts` (or repository-equivalent) using the same worker-process/observability/readiness conventions as existing background entrypoints; add package scripts `start:billing-worker` and `readiness:billing-worker` only if consistent with existing script pattern.
- Billing worker must run bounded recurring scans at minute-scale configuration, not sub-second busy loops.
- Publisher reconciliation: find due PENDING/RETRYABLE and stale IN_FLIGHT rows; stale IN_FLIGHT must return to retryable only under a bounded lease/attempt rule that preserves permanent idempotency identity.
- Recovery-credit purchase activation reconciliation: invoke the accepted BACKGROUND-009 durable activation/reconciliation path for reported pack-purchase UsageEvents so a Shopify-reported pack cannot remain indefinitely unactivated after a process crash. This worker wires/schedules the accepted service; it must not invent a second credit-grant implementation.
- Subscription reconciliation: query Shopify Partner ActiveSubscription for a bounded page of active shops, classify FlatRate/Tiered items identically to SHOPIFY-001 contract, and update local projection idempotently. Sharing source code across repos is not required; behavior/contract must match parent architecture.
- Partner API error != NO_CONTRACT. Preserve last known mapped plan subject to fail-closed staleness policy and record SYNC_ERROR; do not silently downgrade to Free.
- Reconciliation must discover pending updates and current-cycle transitions without subscription webhooks.
- Usage reconciliation: for current paid cycle compare Moda net REPORTED recovery-conversation quantity for the mapped meter with Shopify `items[].usage.quantity` for that TieredPrice item. Record discrepancy state/structured domain outcome for Admin; do not automatically create arbitrary financial corrections to force equality.
- Uninstall: prioritize pending/retryable events whose occurredAt <= stable Shop.uninstalledAt and stop any event with occurredAt after uninstall. After Shopify no longer accepts reporting window, mark NEEDS_ATTENTION rather than rewrite timestamp.
- Unknown Shopify plan handles remain UNMAPPED and become Admin-visible; next scan can map automatically after SUPER_ADMIN registers the plan.
- Worker readiness must verify process/config dependencies without calling provider on every readiness check. Telemetry uses existing shared logging/OTel conventions.

## Work Items

- [ ] Add billing worker entrypoint/scripts/readiness.
- [ ] Implement bounded subscription reconciliation using Partner API 2026-07 contract.
- [ ] Implement publisher stale-work recovery and periodic due scans.
- [ ] Wire bounded BACKGROUND-009 recovery-credit purchase activation reconciliation into the recurring billing worker scan.
- [ ] Implement Shopify-vs-Moda usage comparison/discrepancy persistence/visibility mechanism using accepted schema fields/audit/operational representation.
- [ ] Implement uninstall prioritization/cutoff.
- [ ] Add focused worker/reconciliation tests including external plan change, unmapped->mapped next scan, Partner failure, pending downgrade activation, stale IN_FLIGHT, discrepancy and uninstall deadline.

## Interfaces / Contracts

Worker deployable identity:

```text
service.name = moda-billing-worker
npm run start:billing-worker
npm run readiness:billing-worker
```

Use existing service.namespace/environment observability conventions.

## Dependencies

Explicit task dependencies are authoritative in YAML frontmatter. Do not begin unless every listed dependency is architect-accepted `complete` and any accepted Shared/database artifact required by this repository is available to consume.

## Enables

- ARCH-007-ADMIN-004
- ARCH-007-GATEWAY-001
- ARCH-007-SYSTEM-TEST-002
- ARCH-007-SYSTEM-TEST-003

## Acceptance Criteria

- [ ] Billing work survives Redis/job loss because PostgreSQL scans recover due state.
- [ ] A `RECOVERY_CREDIT_PACK_PURCHASE` whose billing UsageEvent is already REPORTED but whose purchase activation was interrupted is rediscovered and activated idempotently through BACKGROUND-009.
- [ ] External Shopify plan changes are reflected without requiring merchant callback.
- [ ] Partner failure cannot become no-contract/free.
- [ ] Unknown plan maps after Admin registration on later reconciliation with no deploy.
- [ ] Usage discrepancy is visible but not auto-fudged.
- [ ] Post-uninstall cutoff is enforced.
- [ ] Independent entrypoint/readiness/tests/validation pass.

## Validation

Inspect the repository `package.json` first. Run the focused tests required by this task plus the repository-declared typecheck/lint/build/Prisma validation that actually exists, and `git diff --check`. Do not invent missing npm scripts.

## Implementation Notes


Luna deterministic-execution guardrails:

- Treat this task file as the complete implementation contract. Do not infer additional product policy from old billing code.
- Inspect the named current implementation before editing, but if old code conflicts with ARCH-007, implement ARCH-007.
- Do not start an enabled/dependent task. Return only this task to `review` and STOP.
- Do not modify another repository except an explicitly permitted database submodule/package dependency pointer in this task.
- Do not add new billing raw SQL (`$queryRaw`, `$executeRaw`, `Prisma.sql`, raw driver SQL) to compensate for an unavailable Prisma delegate. Adopt/regenerate the accepted Prisma schema instead.
- Follow `docs/agent-vcs-ownership-policy.md` for all Git/VCS operations.
- Before returning this task to `review`, commit and push the assigned implementation `task/ARCH-007-BACKGROUND-008` branch and the mirrored parent-workspace `task/ARCH-007-BACKGROUND-008` branch; the parent commit is limited to the current task file plus explicitly task-owned evidence.
- Do not merge either task branch into `main`, push `main`, force-push, or stage the parent-workspace implementation submodule gitlink.


## Completion Report

### Status

Ready for architect review (Attempt 1)

### Files Changed

`moda-interact-background` implementation branch commit `7501979`.

- `src/entrypoints/billing.ts`
- `src/providers/shopify-partner-billing.provider.ts`
- `src/services/billing-reconciliation.service.ts`
- `src/services/shopify-usage-event-publisher.service.ts`
- `src/runtime/readiness.ts`
- `observability/billing.mjs`
- `package.json`
- focused runtime and reconciliation tests under `tests/unit/`

### Work Completed

Implemented an independent `moda-billing-worker` with readiness-first startup, shared observability/resource shutdown, and a 60-second bounded reconciliation interval.

The worker runs due/stale Shopify usage publication, BACKGROUND-009 recovery-credit activation reconciliation, bounded active-shop Partner ActiveSubscription reconciliation, current-cycle Moda-versus-Shopify usage comparison, and structured discrepancy logging without financial auto-correction.

Subscription projection preserves the existing mapped plan on Partner failure and records `SYNC_ERROR`; no-contract and unknown-plan states are distinguished, pending plan updates and billing periods are projected, and unknown handles remain `UNMAPPED` until a plan is mapped.

Usage publication now enforces the uninstall cutoff: pre-cutoff events can drain, while post-cutoff events are marked `NEEDS_ATTENTION` without timestamp rewriting.

### Validation Results

Passed:

- `npx vitest run tests/unit/services/billing-reconciliation.service.test.ts` (3 tests)
- focused runtime/publisher suite (26 tests)
- `npm run build`
- `npm run prisma:validate`
- `git diff --check`
- editor diagnostics for all changed TypeScript source files

`npm run test:unit` completed with 406 passing and 2 failing tests. The failures are existing `pending-recovery-candidate.service.test.ts` expectations unrelated to this task; no billing tests failed.

### Deviations

The accepted database schema has no dedicated billing-discrepancy table. Discrepancies are returned in the reconciliation result and emitted through the shared structured logger for operational/Admin consumption; no schema or database repository change was made.

### Assumptions

Partner credentials are supplied through `SHOPIFY_PARTNER_ORG_ID`, `SHOPIFY_PARTNER_ACCESS_TOKEN`, and `SHOPIFY_APP_ID`, matching SHOPIFY-001. Active-shop reconciliation is bounded to 200 rows per scan and defaults to 50.

### Unresolved Issues

The two unrelated pending-recovery candidate unit failures remain for architect/repository owner follow-up.

### Architectural Concerns

The discrepancy representation is operational structured output rather than durable database state because the accepted schema exposes no discrepancy model. Durable historical discrepancy querying would require a later schema/API task.

## Architect Review

### Review Status

Pending architect acceptance

### Review Notes

No architect acceptance decision has been made by this agent.

### Reviewed Files

Implementation branch commit `7501979` contains the files listed in the Completion Report.

### Validation Reviewed

Focused billing/runtime tests, build, Prisma validation, diff check, and source diagnostics passed. Full unit-suite result includes the two unrelated failures recorded above.

### Architecture Conformance

Pending architect acceptance

### Follow-up

None
