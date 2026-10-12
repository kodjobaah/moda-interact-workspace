---
id: ARCH-031-BACKGROUND-002
architecture_id: ARCH-031
title: Finalize Merchant Pricing translation publication
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 55
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-031-BACKGROUND-001
  - ARCH-031-DATABASE-002
  - ARCH-031-ADMIN-003
enables:
  - ARCH-031-SYSTEM-TEST-001
created: 2026-10-11
updated: 2026-10-11
---

# Finalize Merchant Pricing translation publication

## Architecture

Architecture ID: `ARCH-031`

Architecture document: `docs/architecture/ARCH-031-automatic-merchant-pricing-translations.md`

Coordinator: `moda_architect`

## Objective

Atomically publish a terminal Merchant Pricing translation run into its linked inactive draft, producing an exact 20-locale READY plan while leaving activation explicit.

## Context

Once Admin save became the durable draft boundary, automatic finalisation had to move out of the Admin request lifecycle. Background already owns translation reconciliation and is the correct owner of automatic publication after `READY_TO_APPLY`.

This task is recorded retrospectively during final reconciliation because the implementation exists in the 2026-10-11 snapshot but its durable task file was not materialised at implementation time.

## Scope

- reconcile linked TRANSLATING plans whose run becomes READY_TO_APPLY/FAILED/STALE;
- lock/revalidate run and draft in a serializable transaction;
- verify source schema, handle, hash/snapshot, current English source and exact translation item membership;
- atomically replace plan/highlight translations with the exact canonical set;
- transition plan to READY/inactive and run to APPLIED with provenance;
- record terminal failure/stale state without partial publication;
- emit bounded Shared-logger outcome events.

## Out of Scope

- Admin activation;
- provider translation execution already owned by BACKGROUND-001;
- database schema/migrations;
- system-test implementation.

## Requirements

Publication must be idempotent/fail closed, must not apply stale source, and must never leave a plan active as part of automatic finalisation.

## Work Items

- [x] Add publication reconciliation service and source/result validation helpers.
- [x] Add atomic persistence/write/failure helpers.
- [x] Wire publication reconciliation into Background runtime after translation state changes.
- [x] Add focused unit coverage.

## Interfaces / Contracts

Consumes `MerchantPricingPlanPublicationStatus`, `currentTranslationRunId`, and the ARCH-031 translation run/item tables. No new Shared runtime contract.

## Dependencies

- `ARCH-031-BACKGROUND-001`
- `ARCH-031-DATABASE-002`
- `ARCH-031-ADMIN-003`

## Enables

- `ARCH-031-SYSTEM-TEST-001`

## Acceptance Criteria

- [x] READY_TO_APPLY publication revalidates current source before writing translations.
- [x] Exact canonical translations are written atomically with plan READY and run APPLIED transitions.
- [x] Published plans remain inactive.
- [x] FAILED/STALE runs cannot partially publish translations.
- [x] Duplicate/stale publication attempts are safely skipped or fail closed.
- [x] Semantic logs contain identifiers/counts but no translation text/secrets.

## Validation

- [x] Focused publication service/source/result unit coverage accepted during implementation.
- [x] Background ARCH-031 runtime suite accepted during implementation.
- [x] `git diff --check` accepted during implementation.

## Stop Condition

Retrospectively satisfied; implementation is complete and architect-accepted.

## Implementation Notes

Key implementation is under `src/services/merchant-pricing-translation-publication.service.ts` and `src/services/merchant-pricing-translation/`.

## Completion Report

### Status

Ready for Review — retrospectively materialised from accepted integrated implementation.

### Files Changed

Merchant Pricing publication service/helpers, runtime wiring and focused tests.

### Work Completed

Automatic finalisation implemented as scoped.

### Validation Results

Developer-side focused Background validation was accepted during implementation. The extracted ZIP did not contain installed `vitest`, so the suite was not rerun during reconciliation.

### Deviations

Task record was materialised retrospectively during final reconciliation.

### Assumptions

None.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

Accepted

### Review Notes

The implementation correctly moves publication out of Admin, revalidates source/result identity at the final write boundary, atomically transitions run/plan state, and keeps the plan inactive for explicit administrator activation.

### Reviewed Files

`src/services/merchant-pricing-translation-publication.service.ts`; `src/services/merchant-pricing-translation/publication-*.ts`; runtime wiring and focused tests.

### Validation Reviewed

Source/test inspection plus accepted developer-side Background validation. Local rerun blocked only by missing installed dependencies in the ZIP.

### Architecture Conformance

Conforms.

### Follow-up

ARCH-031-SYSTEM-TEST-001 remains terminal validation.
