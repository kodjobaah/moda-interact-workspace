---
id: ARCH-031-SYSTEM-TEST-001
architecture_id: ARCH-031
title: Validate automatic Merchant Pricing translations
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 90
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-031-DATABASE-001
  - ARCH-031-ADMIN-001
  - ARCH-031-ADMIN-002
  - ARCH-031-BACKGROUND-001
  - ARCH-031-ADMIN-003
enables: []
created: 2026-10-10
updated: 2026-10-10
---

# Validate automatic Merchant Pricing translations

## Architecture

Architecture ID: `ARCH-031`.

Architecture document: `docs/architecture/ARCH-031-automatic-merchant-pricing-translations.md`.

Coordinator: `moda_architect`.

## Objective

Provide terminal black-box/integration evidence that a platform administrator can author Merchant Pricing content in English only, Moda automatically obtains complete valid translations through the configured Background runtime, and the final plan is published atomically only from matching ready translation work.

## Context

ARCH-031 replaces the ARCH-014 Merchant Pricing workbook authoring dependency. Repository-level tests prove individual schema/Admin/Background behavior; this task validates the integrated architecture after every implementation dependency is Complete and architect-accepted.

The existing system-test repository is the architecture-level validation boundary. Tests should reuse its disposable PostgreSQL/Redis orchestration and evidence conventions and remain modular: scenario registry, fixtures, executors, assertions and process orchestration must stay separated rather than growing a large catch-all file.

The current ARCH-014 system-test task contains historical XLSX-specific expectations. Those expectations are superseded for the normal Merchant Pricing builder after ARCH-031 integration and must not be run as contradictory release evidence without architect reconciliation.

## Scope

Within `moda-interact-system-test` only:

- add architecture-level scenarios/evidence for automatic Merchant Pricing translation;
- configure deterministic test translation-provider behavior or an architecture-approved provider emulator/stub at the existing provider boundary;
- exercise Admin + PostgreSQL + Redis/BullMQ + Background integration where the harness supports it;
- prove exact translation completeness and final-plan atomicity from externally observable/database evidence;
- cover stale source, retry/failure and duplicate/concurrency safety;
- record evidence using existing system-test output conventions.

## Out of Scope

- changing production Admin/Background/Database implementation;
- calling paid/live OpenAI by default in deterministic local/system tests;
- changing the supported language set;
- testing Promotion workbook translation;
- changing Store Category translation semantics;
- modifying ARCH-014 task documents or any `_index.md` as part of this implementation task;
- making any implementation task depend on this system-test task.

## Requirements

### R1 — terminal dependency gate

Do not execute until every declared implementation dependency is `complete` and architect-accepted.

This task is terminal validation. It must not be introduced as a prerequisite for Admin/Background/Database implementation.

### R2 — deterministic provider test boundary

System tests MUST NOT depend on nondeterministic/paid live OpenAI availability for normal certification.

Use the existing provider abstraction/harness patterns to supply deterministic Batch lifecycle/results while preserving the real application boundaries being validated:

```text
Admin request
  -> PostgreSQL durable run/items
  -> Background reconciliation
  -> BullMQ merchant-communications jobs
  -> translation provider boundary (deterministic test implementation/emulation)
  -> durable results
  -> Admin final application
```

If the current provider abstraction cannot be substituted without production changes, stop and report the concrete testability gap to `moda_architect` rather than embedding production bypasses in system tests.

### R3 — fresh automatic create scenario

Prove end-to-end for a new Merchant Pricing plan:

1. an enabled automatic-default translation model/credential exists;
2. Admin supplies English description/highlights only;
3. no XLSX translation input is supplied;
4. entering/using Step 7 creates/reuses durable translation work;
5. Background submits only 19 non-English translations per changed source field;
6. run reaches `READY_TO_APPLY` with exact required item completeness;
7. final Admin create succeeds;
8. resulting `MerchantPricingPlan` has exactly the canonical 20 plan translations and exactly 20 translations for every highlight;
9. run is atomically `APPLIED` and points/snapshots provenance as designed.

### R4 — edit retention and reorder scenario

For an existing complete plan:

- changing a single English source field retains every unchanged field translation and translates only that changed field's 19 non-English targets;
- reordering highlights without changing source text/contentKey does not request translation and preserves translations;
- changing only pricing/economics/features does not request translation.

Evidence must distinguish provider requests/items sufficiently to prove unnecessary translation did not occur.

### R5 — stale-source scenario

Start translation for source A, then change a translatable English field to source B before final application.

Prove:

- source-A completion cannot be applied to source B;
- final plan write with stale run is rejected without partial catalogue change;
- a current source-B run may subsequently complete and apply successfully.

Client-side invalidation alone is insufficient evidence; exercise the server correctness boundary.

### R6 — failure/retry scenario

Inject a retryable provider/item failure and then success.

Prove:

- bounded retry behavior occurs through the existing runtime;
- no partial Merchant Pricing plan appears during translation;
- terminal `FAILED` is surfaced if retry budget is exhausted;
- Admin can request/retry current source after terminal failure;
- successful retry may reach ready/apply.

Also cover one invalid provider output (blank/over-limit or exact-result-membership violation) and prove it is never persisted as an available final translation.

### R7 — configuration failure scenario

With no valid automatic-default translation model or credential:

- Admin returns bounded configuration-required state;
- no provider/queue work is created;
- no partial plan is created;
- no manual-XLSX fallback appears in the normal builder flow.

### R8 — duplicate/concurrency scenario

Prove:

- repeated identical automatic requests reuse/prevent duplicate active handle+source work;
- Redis job loss or omission is repairable by Background reconciliation from PostgreSQL state where the harness can safely remove/recreate queue work;
- two final submissions cannot both consume the same `READY_TO_APPLY` run;
- final database state contains one coherent plan application and one terminal run application outcome.

### R9 — language-set evidence

Validate the final persisted translations use exactly the canonical 20 language tags, with no missing/extra locale and no English fallback masquerading as a generated translation for non-English locales.

Do not assert translation quality semantically beyond deterministic fixture expected output; this task validates workflow/integrity, not linguistic benchmarking.

### R10 — evidence quality

Record enough evidence to diagnose a failure without exposing secrets or full customer/provider payloads. Include architecture/scenario ids, run id, statuses/counts and relevant durable identifiers.

Keep scenario implementation modular and within current system-test source-structure rules.

## Work Items

- [ ] Confirm all implementation dependencies are Complete and architect-accepted before claim/execution.
- [ ] Inspect current billing/system-test harness and choose the smallest correct domain/suite placement.
- [ ] Add deterministic translation-provider Batch fixture/emulation at the approved boundary.
- [ ] Add fresh-create automatic translation scenario.
- [ ] Add partial-edit/reorder/no-translatable-change scenario(s).
- [ ] Add stale-source rejection/current-source success scenario.
- [ ] Add retry/terminal-failure/invalid-output scenario(s).
- [ ] Add missing-default/credential configuration-failure scenario.
- [ ] Add duplicate request / queue repair / double-consume concurrency evidence where supported by the harness.
- [ ] Assert exact 20-locale persisted plan/highlight state.
- [ ] Keep executors, fixtures, assertions and orchestration split by responsibility.
- [ ] Run catalogue/source-structure/harness validations and selected system scenarios.
- [ ] Record evidence paths/run ids in the Completion Report.

## Interfaces / Contracts

Validates the integrated result of:

- `ARCH-031-DATABASE-001`;
- `ARCH-031-ADMIN-001`;
- `ARCH-031-ADMIN-002`;
- `ARCH-031-BACKGROUND-001`;
- `ARCH-031-ADMIN-003`.

Consumes existing system-test orchestration and environment contracts. It does not define a new production cross-service contract.

## Dependencies

- `ARCH-031-DATABASE-001`.
- `ARCH-031-ADMIN-001`.
- `ARCH-031-ADMIN-002`.
- `ARCH-031-BACKGROUND-001`.
- `ARCH-031-ADMIN-003`.

## Enables

None.

## Acceptance Criteria

- [ ] A new Merchant Pricing plan can be fully created from English content without manual translation/XLSX input.
- [ ] Automatic translation executes through the real durable Admin -> Background -> provider-boundary workflow.
- [ ] Exactly 20 plan locales and 20 locales per highlight are persisted before the plan becomes usable.
- [ ] No incomplete Merchant Pricing plan exists while translation is pending/failed.
- [ ] Partial English edits translate only changed/new source fields; unchanged translations are retained.
- [ ] Highlight reorder and non-translatable edits do not trigger unnecessary provider work.
- [ ] A stale run cannot be applied after English source changes.
- [ ] Retryable failures recover within policy; terminal/invalid results never become final translations.
- [ ] Missing automatic-default configuration fails closed without provider work/manual-XLSX fallback.
- [ ] Duplicate requests do not create duplicate active work and a ready run cannot be consumed twice.
- [ ] Queue-work loss is recoverable from durable state where exercised by the harness.
- [ ] Normal Merchant Pricing UI/process no longer depends on workbook upload/download.
- [ ] Evidence contains no provider credentials/secrets or unnecessary translation payloads.

## Validation

- [ ] `npm run lint`.
- [ ] `npm run validate:structure`.
- [ ] `npm run validate:catalogue`.
- [ ] focused harness unit tests for any new executor/emulator/fixture modules.
- [ ] selected ARCH-031 scenario plan/list command succeeds.
- [ ] selected ARCH-031 system scenarios execute with PASS evidence in the intended disposable-local/test environment.
- [ ] `git diff --check`.

## Stop Condition

After Work Items, Acceptance Criteria and required Validation are complete, set status to `review`, return the Completion Report/evidence to `moda_architect` and STOP. Do not mark the parent architecture Implemented; final architectural verification remains with `moda_architect`.

## Implementation Notes

Prefer extending the existing billing domain when its harness already owns Merchant Pricing/Admin catalogue scenarios; create a new domain only if the current catalogue structure genuinely requires it.

Do not create 300+ line catch-all system-test files. Split deterministic provider fixtures, database assertions, executor/process orchestration and scenario registration into focused modules according to the repository's existing structure rules.

The test translation provider should produce deterministic target-language-tagged fixture values that satisfy the same field limits as production validation and allow exact assertions without evaluating linguistic quality.

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
