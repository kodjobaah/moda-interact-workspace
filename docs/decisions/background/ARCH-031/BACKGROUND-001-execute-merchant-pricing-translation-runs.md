---
id: ARCH-031-BACKGROUND-001
architecture_id: ARCH-031
title: Execute Merchant Pricing translation runs
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 50
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-031-DATABASE-001
enables:
  - ARCH-031-ADMIN-003
created: 2026-10-10
updated: 2026-10-10
---

# Execute Merchant Pricing translation runs

## Architecture

Architecture ID: `ARCH-031`.

Architecture document: `docs/architecture/ARCH-031-automatic-merchant-pricing-translations.md`.

Coordinator: `moda_architect`.

## Objective

Execute durable Merchant Pricing translation runs through the existing merchant-communications translation runtime, reusing the established provider/Batch safety mechanics and producing only validated `READY_TO_APPLY` runs for Admin consumption.

## Context

The inspected snapshot already runs translation work through `moda-merchant-communications-worker` using the `TRANSLATION_RECONCILIATION` lease, the existing `merchant-communications` BullMQ queue, `createOpenAITranslationProvider`, and reusable helpers under `src/services/translation-batch-runtime/`.

Store Category translation demonstrates the durable run/item/batch pattern, but its database rows and domain services are category-specific. ARCH-031 adds dedicated Merchant Pricing translation state in DATABASE-001 and requires Background to execute it without creating another queue, scheduler, provider abstraction or deployable worker.

## Scope

Within `moda-interact-background` only:

- Merchant Pricing translation job schemas and deterministic job identifiers owned locally by Background;
- reconciliation of durable Merchant Pricing `PENDING` / `PROCESSING` runs and retry-due items;
- Batch assembly against the accepted DATABASE-001 tables;
- provider Batch submit / poll / results services;
- translation-output validation and bounded retry/failure transitions;
- run-state advancement to `READY_TO_APPLY` or `FAILED`;
- integration into the existing `TRANSLATION_RECONCILIATION` leased scheduler;
- dispatch through the existing `merchant-communications` queue/worker;
- focused unit/integration tests and bounded shared structured logging.

Prefer small domain-specific services parallel to the existing Store Category services while extracting/reusing only already-generic `translation-batch-runtime` mechanics. Do not create a new catch-all translation service.

## Out of Scope

- Admin request/status/final apply behaviour;
- `MerchantPricingPlan` creation or mutation;
- database schema/migration changes;
- Store Category translation publication behaviour;
- Promotion translation;
- a new Shared package contract;
- a new BullMQ queue, Redis instance, lease name, scheduler, worker entrypoint or Render/Gateway service;
- translation-model configuration UI;
- cleanup/retention of old terminal Merchant Pricing translation runs;
- any `_index.md` update.

## Requirements

### R1 — existing execution boundary

Use the existing deployment/runtime boundary:

```text
moda-merchant-communications-worker
        |
TRANSLATION_RECONCILIATION leased scheduler
        |
merchant-communications queue
        |
Merchant Pricing translation jobs
```

Extend the scheduler's reconciliation fan-out so Merchant Pricing reconciliation is isolated with the existing domains: a failure in one translation domain must not prevent the other domain reconcilers from being attempted during that lease iteration. Preserve the current `Promise.allSettled`/aggregate-failure style or an equivalent isolation contract.

Do not add another recurring lease solely for Merchant Pricing translation.

### R2 — local deterministic job contract

Background owns local runtime-safe schemas for Merchant Pricing Batch jobs equivalent in responsibility to the current Store Category jobs:

```text
merchant-pricing-translation-batch-submit
merchant-pricing-translation-batch-poll
merchant-pricing-translation-batch-results
```

Every payload is strict, versioned and contains only the durable Batch id plus the poll sequence where required. Job ids are deterministic from Batch identity/poll sequence so reconciliation may safely repair Redis work after loss/restart.

This is an internal Background queue contract; do not create a Shared publication task unless implementation proves another repository must produce/consume these BullMQ jobs directly.

### R3 — durable reconciliation

The reconciler treats PostgreSQL as source of truth and must be restart-safe/idempotent.

At minimum it must:

1. page eligible Merchant Pricing runs/items/batches using DATABASE-001 indexes;
2. move a new run from `PENDING` to `PROCESSING` only through a concurrency-safe transition;
3. assemble provider batches from retry-due `PENDING` items using existing runtime Batch-size controls;
4. ensure deterministic submit/poll/results jobs exist for durable work;
5. recover `SUBMISSION_UNKNOWN`/provider-correlation states using the existing generic provider-correlation helper;
6. advance a run only from the durable item state, never from queue presence;
7. mark the run `READY_TO_APPLY` only when every required item is `AVAILABLE` and no required item remains pending/failed;
8. mark a terminally unrecoverable run `FAILED` with a bounded failure code.

A Redis/BullMQ loss must be repairable by a later reconciliation pass.

### R4 — reuse the existing provider runtime

Reuse the existing generic mechanisms under `src/services/translation-batch-runtime/` and the existing provider/credential boundary, including where applicable:

- provider submission and submission-unknown handling;
- provider Batch correlation;
- provider polling;
- provider result download/application mechanics;
- exact result-membership validation;
- item retry disposition;
- bounded failure policy;
- queue-job repair;
- encrypted credential resolution;
- Background runtime Batch size / polling / retry controls.

Do not duplicate those mechanisms in Merchant Pricing-specific code merely because Store Category has its own orchestration services.

### R5 — request assembly

Only `PENDING` non-English Merchant Pricing items are submitted. `AVAILABLE` English or retained-existing translations are never sent to the provider.

Provider requests use the run's snapshotted provider/model identity and each item's exact source/target language values. Do not replace a run's snapshotted model with whatever model is currently the automatic default.

No provider call occurs inside a PostgreSQL transaction.

### R6 — result validation before availability

Trim provider output and validate the translated value before an item becomes `AVAILABLE`.

Required content constraints mirror the existing Merchant Pricing canonical parser:

```text
plan description       non-empty, <= 2000 characters
highlight title        non-empty, <= 120 characters
highlight description  non-empty, <= 500 characters
```

Also require exact provider custom-id/result membership through the existing Batch result-membership protection.

Invalid/missing/duplicate provider results follow bounded item retry disposition. They must never be silently accepted, replaced by English, or cause a partial final Merchant Pricing plan to be written.

### R7 — run-state correctness

Run state is derived from durable item state under concurrency-safe database updates.

- `READY_TO_APPLY` means every exact required run item is `AVAILABLE`.
- `FAILED` means required work has terminally failed according to existing retry policy.
- `STALE` / `APPLIED` runs receive no new provider work.
- repeated workers/reconciliation passes are idempotent.
- results arriving after a run becomes terminal are ignored/fail closed rather than reopening it.

Background does **not** mark a run `APPLIED`; only the Admin final plan transaction in ADMIN-003 owns that transition.

### R8 — provider failure isolation

Expected provider/network failures use the existing bounded retry/backoff semantics. A provider outage must not crash the merchant-communications worker process or corrupt unrelated merchant-message/Store-Category translation work.

Preserve submission-ambiguity handling: never blindly resubmit an unknown submission when the existing provider-correlation mechanism can establish whether a Batch already exists.

### R9 — observability

Use `@modainteract/moda-interact-shared/logging` for new/changed generic application logs. Do not add a competing logger or new custom metrics duplicating existing BullMQ/OpenTelemetry signals.

Emit bounded domain events such as:

```text
background.merchant_pricing_translation.run_started
background.merchant_pricing_translation.batch_assembled
background.merchant_pricing_translation.batch_completed
background.merchant_pricing_translation.run_ready
background.merchant_pricing_translation.run_failed
```

Allowed metadata is limited to bounded identifiers, provider/model configuration identity, statuses, attempt/count information and failure codes. Do not log source text, translated text, provider file bodies, credentials/tokens or raw provider errors containing request payloads.

## Work Items

- [ ] Consume the accepted DATABASE-001 schema/gitlink.
- [ ] Add focused Merchant Pricing translation domain job schemas and deterministic job ids.
- [ ] Add run-state/reconciliation logic against durable Merchant Pricing translation state.
- [ ] Add Batch assembly using existing runtime Batch-size controls.
- [ ] Add submit/poll/results orchestration that reuses `translation-batch-runtime` provider helpers.
- [ ] Validate translated values against Merchant Pricing field limits before `AVAILABLE`.
- [ ] Integrate Merchant Pricing reconciliation into the existing leased translation scheduler.
- [ ] Register the three Merchant Pricing Batch job types in the existing merchant-communications worker.
- [ ] Add bounded shared structured logging.
- [ ] Add focused tests for idempotency, Redis repair, submission ambiguity, retries, invalid results, exact run-ready semantics and terminal-state protection.
- [ ] Run repository-required focused validation and record results.

## Interfaces / Contracts

Consumes database state owned by:

- `ARCH-031-DATABASE-001`.

Consumes existing internal/shared runtime capabilities:

```text
@modainteract/moda-interact-shared/logging
@modainteract/moda-interact-shared/observability/bullmq
src/providers/translation.provider.ts
src/services/translation-batch-runtime/*
```

Produces durable run/item state consumed by:

- `ARCH-031-ADMIN-003` through Admin's DATABASE-001-backed service boundary.

No new cross-repository queue schema is introduced.

## Dependencies

- `ARCH-031-DATABASE-001`.

## Enables

- `ARCH-031-ADMIN-003`.

## Acceptance Criteria

- [ ] Merchant Pricing translation executes on the existing merchant-communications worker/queue and existing translation-reconciliation lease.
- [ ] No new provider abstraction, queue, scheduler, worker deployment or Gateway configuration is introduced.
- [ ] Only pending non-English items are submitted; English/retained available items are not translated again.
- [ ] Provider/model identity used for execution is the run snapshot, not the current default at execution time.
- [ ] Reconciliation is idempotent and can restore missing deterministic queue jobs from PostgreSQL state.
- [ ] `SUBMISSION_UNKNOWN` uses existing provider-correlation safety rather than blind duplicate submission.
- [ ] Missing/duplicate/malformed provider results cannot become `AVAILABLE`.
- [ ] Over-limit/blank translations follow bounded retry/failure policy and cannot reach `READY_TO_APPLY`.
- [ ] A run reaches `READY_TO_APPLY` only when every required item is available.
- [ ] Background never creates/mutates a final `MerchantPricingPlan` and never marks a run `APPLIED`.
- [ ] Store Category and ordinary merchant-message translation behaviour remains regression-covered.
- [ ] New logs contain no source/translated text or provider secrets.

## Validation

- [ ] focused unit tests for Merchant Pricing job schemas/job ids.
- [ ] focused unit tests for run-state and Batch assembly.
- [ ] focused unit tests for provider submit/poll/results retry/correlation/result validation.
- [ ] focused reconciliation test proving lost queue jobs are repaired from durable state.
- [ ] regression tests for Store Category translation runtime and generic `translation-batch-runtime` helpers touched by this task.
- [ ] repository integration test where available for PostgreSQL-backed concurrency/idempotency paths.
- [ ] `npm run build`.
- [ ] focused `npm run test:unit -- <files>` / repository-declared Vitest commands for changed scope.
- [ ] `git diff --check`.

## Stop Condition

After Work Items, Acceptance Criteria and required Validation are complete, set status to `review`, return the Completion Report to `moda_architect` and STOP. Do not begin Admin builder integration.

## Implementation Notes

Keep domain-specific SQL and lifecycle semantics in focused Merchant Pricing services. Reuse generic provider mechanics but do not force Store Category and Merchant Pricing into a speculative shared polymorphic service/table abstraction.

The existing merchant-communications entrypoint currently also calls Store Category publication reconciliation. Merchant Pricing has no analogous Background publication stage: readiness ends at `READY_TO_APPLY`; Admin owns atomic application when the administrator submits the final pricing plan.

## Completion Report

### Status

Not Started

### Files Changed

None.

### Work Completed

None.

### Validation Results

None.

### Deviations

None.

### Assumptions

None.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

Pending

### Review Notes

None.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending implementation review.

### Follow-up

None.
