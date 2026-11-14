---
id: ARCH-070-BACKGROUND-006
architecture_id: ARCH-070
title: Observe bounded final selection shape before runner validation
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 10
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-070-BACKGROUND-004
  - ARCH-070-BACKGROUND-005
enables: []
created: 2026-11-14
updated: 2026-11-14
---

# Observe bounded final selection shape before runner validation

## Architecture

ARCH-070; docs/architecture/ARCH-070-verified-recommendation-terminal-turn-recovery.md; moda_architect.

## Objective

Expose safe finalResponse selection-shape evidence at the application model bridge before semantic rejection, without changing model arguments or execution policy.

## Context

Genuine production Videographer question2026-11-14T08:20:54Z had2successful product searches, step3plain text, step4forced finalResponse and FINAL_PRODUCT_SELECTION_MISSING. Raw argument shape is absent from existing logs. Read-only source confirms bridge preserves args; pinned schema refines rather than strips; empty optional arrays normalize away; existing composition diagnostics run only after runner success. Missing selections could be omission or incomplete fields; no exact cause inferred without evidence. Root separately performs max2synthetic model probes under operational authority; this task performs no live calls.

## Scope

Existing Background src/commerce/host.ts model bridge response_postprocess seam and reusable application-owned structural diagnostic helper/direct tests. Reuse existing composition shape conventions/logger where compatible; no duplicate generic logger.

## Out of Scope

Shared changes/publication, schema/semantic validation changes, invented selections/IDs/version fields, added repair loops/provider search, model switching, prompt corrections based on guessed cause, database/migration/Gateway/layout changes, live model/Meta/provider/database operations or main merge.

## Requirements

- Normal launcher dedicated sibling parent/implementation worktrees and mirrored task branches. Preserve primary untracked/private data and unrelated staged ARCH069 task; do not print private traces or raw model arguments.
- Inspect actual existing model/bridge/composition diagnostics and shared-logging documentation. Framework/provider count/token telemetry cannot expose domain selection-shape omission before runner failure, so this is bounded domain semantic evidence, not duplicate HTTP telemetry.
- Emit shape-only semantic diagnostic immediately after model.invoke yields its step and BEFORE response postprocessing/rewrite/runner validation. Record only known allowlisted fields: exact-one-finalResponse boolean, capped call count, recognized answerKind enum/ABSENT/INVALID, details container type, known selection array ABSENT/ARRAY/INVALID and counts capped4, recommendation version ABSENT/V1/INVALID, recognized disposition/ABSENT/INVALID, shipping selection presence/container kind, optional known-key presence booleans and capped unknown-key count. Never enumerate arbitrary unknown key names or values.
- Correlate through existing turn/model-bridge identifiers and pinned response contract hash/revision only when independently available. Any forced/finalization indicator must come from trusted request metadata; do not infer model intention or add inaccessible context fields. Do not log prompts/prose, product IDs/URLs, checkout/customer info, credentials, raw payloads or arbitrary strings. Keep record bounded; malformed/nonobject/empty/large shapes safe.
- Preserve exact original step/call/arguments references and return semantics, including existing evidence-referral rewrite. Diagnostic failures/sink failure must not affect validation/delivery/model outcome. No argument normalization/coercion/autoselection beyond existing behavior; no weakened missing-selection guard.
- Prefer one app-owned allowlisted shape projection reused by existing successful composition diagnostic and new prevalidation seam if semantics match, without unrelated refactor. Never move business rules into Shared. Existing Shared generic logging API only; no new transport/env/debug secret toggle.
- Tests must distinguish empty details, empty arrays, valid details/options/recommendations, missing version, wrong types, shipping alternatives, unknown keys, multiple calls/plaintext, schema-invalid final, sensitive canaries and logger failures. Prove original object identity/content unchanged and existing terminal selection failure still occurs, with diagnostic preceding rejection; successful outputs unchanged.
- Commit/push exact source and parent report/PR/remotechecks, stop for review. Root owns actual merges/deployment/fresh genuine retry/protected synthetic probe. This task acceptance does NOT claim incident fixed or AI delivery verified; evidence determines a separately bounded application correction.

## Work Items

- [ ] Inspect actual logging gap and define bounded app-owned shape projection.
- [ ] Wire diagnostic before postprocess/runner rejection without modifying args/semantics.
- [ ] Test positive/negative/privacy/failure-isolation/terminal behavior.
- [ ] Push mirrored exact source/report/PR/check evidence and stop.

## Interfaces / Contracts

Existing model invoke step/call arguments, existing pinned finalResponse contract and structured logger identifiers. Shared package/runtime contract unchanged; application owns selection diagnostics. No new queue/data shape or environment variable.

## Dependencies

ARCH-070-BACKGROUND-004 and005 Complete; actual current Background3e46120 contains previous fixes/layout. No system-test prerequisite or new Shared release.

## Enables

Root evidence collection and bounded application-owned correction once actual failure shape is established. No implicit follow-on implementation.

## Acceptance Criteria

- [ ] Prevalidation shape record diagnoses absent/empty/partial known selections without sensitive payloads.
- [ ] Exact step/argument identity and all validation/retry/budget/referral/delivery semantics unchanged.
- [ ] Malformed values/logger failures cannot alter business behavior or leak arbitrary keys/values.
- [ ] Required tests/type/build/scopedlint/remotechecks and canonical isolation report ready; no liveops.

## Validation

- [ ] Focused shape helper/model bridge/composition/terminal failure and privacy/sink isolation tests.
- [ ] Relevant declared host/bridge tests and type/build/scopedlint; disclose exact untouched full-lint baseline, no unrelated cleanup.
- [ ] Diff/private-canary scan plus exact remote CI/check status and mirrored preparation/report evidence.

## Stop Condition

After required checks pass push both branches, set review, return Completion Report and STOP. Do not start a corrective adapter/prompt task, deploy or invoke a live model/provider.

## Implementation Notes

You are not alone; preserve others. Known existing composition shape projection is in host.ts after successful runner, unreachable on failure; reuse domain semantics rather than duplicating logger mechanics. Root holds private trace/contract, no need to commit or read customer payload for this structural test task.

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

Not run

### Deviations

None

### Assumptions

Root owns live evidence and source/main integration.

### Unresolved Issues

Exact production omission/partial-field cause not yet established.

### Architectural Concerns

Do not turn observability task into speculative model-selection or Shared business-policy change.

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

Incident remains unresolved until actual evidence, bounded correction and genuine production verification.
