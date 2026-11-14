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
status: complete
priority: 10
executor: codex
claimed_at: 2026-11-14T08:41:55Z
attempt: 1
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

- [x] Inspect actual logging gap and define bounded app-owned shape projection.
- [x] Wire diagnostic before postprocess/runner rejection without modifying args/semantics.
- [x] Test positive/negative/privacy/failure-isolation/terminal behavior.
- [x] Push mirrored exact source/report/PR/check evidence and stop.

## Interfaces / Contracts

Existing model invoke step/call arguments, existing pinned finalResponse contract and structured logger identifiers. Shared package/runtime contract unchanged; application owns selection diagnostics. No new queue/data shape or environment variable.

## Dependencies

ARCH-070-BACKGROUND-004 and005 Complete; actual current Background3e46120 contains previous fixes/layout. No system-test prerequisite or new Shared release.

## Enables

Root evidence collection and bounded application-owned correction once actual failure shape is established. No implicit follow-on implementation.

## Acceptance Criteria

- [x] Prevalidation shape record diagnoses absent/empty/partial known selections without sensitive payloads.
- [x] Exact step/argument identity and all validation/retry/budget/referral/delivery semantics unchanged.
- [x] Malformed values/logger failures cannot alter business behavior or leak arbitrary keys/values.
- [x] Required tests/type/build/scopedlint/remotechecks and canonical isolation report ready; no liveops.

## Validation

- [x] Focused shape helper/model bridge/composition/terminal failure and privacy/sink isolation tests.
- [x] Relevant declared host/bridge tests and type/build/scopedlint; disclose exact untouched full-lint baseline, no unrelated cleanup.
- [x] Diff/private-canary scan plus exact remote CI/check status and mirrored preparation/report evidence.

## Stop Condition

After required checks pass push both branches, set review, return Completion Report and STOP. Do not start a corrective adapter/prompt task, deploy or invoke a live model/provider.

## Implementation Notes

You are not alone; preserve others. Known existing composition shape projection is in host.ts after successful runner, unreachable on failure; reuse domain semantics rather than duplicating logger mechanics. Root holds private trace/contract, no need to commit or read customer payload for this structural test task.

## Completion Report

### Status

Ready for Review. Implementation, local validation and both exact remote checks complete.

### Files Changed

- `src/commerce/final-selection-shape.ts`: one Background-owned bounded allowlist projection and best-effort Shared-logger adapter.
- `src/commerce/host.ts`: observes original model step immediately after invoke, before postprocessing/rewrite/runner validation; successful composition uses the same shape projection.
- `tests/unit/commerce/final-selection-shape.test.ts`: malformed containers, capped arrays/unknown-key counts, fixed enum states, shipping containers, sensitive canaries, trusted forced flag/hash, exact argument identity and throwing getters/sink isolation.
- `tests/integration/commerce/host-suites/selection-semantics.ts`: actual host omission remains `FINAL_PRODUCT_SELECTION_MISSING`/nonretryable `INVALID_FINAL`, with diagnostic preceding terminal event and exact original final step/call/argument references and content preserved; exhausted correction remains three invocations with one product read.

### Work Completed

Source `58783dd643ff75e2ce8e6618277a606fc4b10eee` pushed to mirrored implementation branch `task/ARCH-070-BACKGROUND-006`; draft PR https://github.com/kodjobaah/moda-interact-background/pull/225. New event `commerce.host.model_bridge.final_selection_shape` emits only existing trusted turn identifiers, request-derived `forcedFinalResponse`, independently pinned lowercase64hex contract hash, fixed shape states and capped counts. No arbitrary argument keys/values/prose/URLs/product identifiers emitted. No normalization, selection fabrication, schema, retry, prompt, budget, provider or delivery changes. No new generic logger/transport/flag. Existing standard telemetry cannot expose this prevalidation domain shape; Shared logging handles generic emission.

### Validation Results

- Canonical normal launcher packet: primary `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-070-BACKGROUND-006`; implementation `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-070-BACKGROUND-006`. Attempt1/codex claimed2026-11-14T08:41:55Z, pushed parent claim32bcfe9325d68d53c997ce02897ddb14f94221d6. Parent synchronized6567d99f65c664f746d25501d22083ccb64e4929, source baseline3e46120ba79c26389df92fb25504a0a2e652a68b, explicit dependencies complete, database submodule6f42b71112efe7ac63654d55f41cd74ca569b1ae ready. No primary/other worktree modifications.
- Normal `npm ci`: PASS. `npx vitest run tests/unit/commerce/final-selection-shape.test.ts tests/unit/commerce/model-bridge-diagnostics.test.ts tests/unit/commerce/host-diagnostics.test.ts`:26PASS/3files. First helper attempt had3 test-table array-expansion fixture failures; corrected fixture only and exact focused rerun green. No failure waived.
- Declared `npm run test:commerce-host`:126PASS, including successful existing composition/referral/evidence paths and new precise terminal omission/order/identity assertion.
- `npx tsc --noEmit`, `npm run build` and scoped eslint on all4 changed files: PASS. No DB/provider/model/Meta calls or schema/migration checks required by this diagnostic-only scope.
- Full `npm run lint`: exactly4 existing `@typescript-eslint/no-unused-vars` errors in unchanged `candidate-index.store.ts:9` (readRecoveryExecutionPolicy) and `recovery-offer-resolver.service.ts:23-25` (MAX_CANDIDATES,VERIFICATION_TIMEOUT_MS,AI_TIMEOUT_MS). Both files byte-unchanged from exact starting3e46120. Baseline stdin proof recorded separately; no matching durable baseline ID found, no unrelated cleanup/full-lint-green claim.
- `git diff --check`: PASS. Diff/privacy review: production change contains no raw payload/model strings, secrets, customer data, URLs or arbitrary unknown-key values. Synthetic sensitive canaries remain only in tests and are asserted absent from diagnostic records.
- Exact head remote runs [43577944714](https://github.com/kodjobaah/moda-interact-background/actions/runs/43577944714) and [43577902536](https://github.com/kodjobaah/moda-interact-background/actions/runs/43577902536): both SUCCESS. Completed remote unit receipt:393files/4376tests PASS (not the historical4386 suite count). Mirrored parent evidence checkpoint6c34ed70f pushed before final review-status commit. Logs retained privately under primary `local-backups/arch070-bg006-*` (npm-ci, focused initial/final, host, types, scoped lint, build initial/final, full/baseline lint). No broad4386local rerun: focused and declared host suites are the task-relevant validation; remote workflow covers its declared scope.

### Deviations

No runtime-scope deviation. Initial fixture correction disclosed above. Full lint remains the exact untouched4-error baseline.

### Assumptions

Root owns live evidence, main integration/deployment and separately authorized synthetic probes. This agent performed none.

### Unresolved Issues

The exact historical production omission/partial-field cause remains unproven. This change supplies evidence before rejection; it is not an incident correction or production AI-delivery verification.

### Architectural Concerns

No Shared/queue/DB contract change, package publication or live operation. Any behavioral correction follows actual evidence in a separately bounded task.

## Architect Review

### Review Status

Accepted

### Review Notes

Accepted exact implementation58783dd643ff75e2ce8e6618277a606fc4b10eee (PR225) and immutable parent report378b9a4f1. Actual all4-file diff independently inspected; source clean and parent actual origin/main already current. Canonical launcher dedicated worktree/sync/recursive submodule evidence reviewed. No findings.

New event is application semantic evidence before runner rejection, not duplicate generic transport telemetry. Allowlisted fixed enums/cappedcounts, trusted forced-tool boolean and lowercase64hex pinned contract hash only; no rawkeys/prose/product/customer/URL data. Shared logger reused, helper catches diagnostic/getter/sink failures. Original returned step/call/args identity/content and existing rewrite/validation/repair/budget behavior preserved. Composition reuses same projection; no competing generic logging or Shared business-rule change.

### Reviewed Files

final-selection-shape.ts; actual host bridge/pre-postprocess and successful composition seam; helper privacy/reference/failure vectors; actual host-suites terminal omission/partialrecommendation tests and final report.

### Validation Reviewed

Focused26/declaredhost126/type/build/scopedlint/diff PASS. Actual host omission emits shape before nonretryable FINAL_PRODUCT_SELECTION_MISSING, exact original identity/content preserved, one product read/three model calls unchanged. Both exacthead remote43577944714 and43577902536 SUCCESS,393files4376testsPASS. Full lint4unchanged baseline errors exact starting-source/stdin proof disclosed; no unrelated cleanup/greenclaim or unnecessary broad local repeat.

### Architecture Conformance

Conforms to bounded Background-owned diagnostics, Shared structural/application policy boundary and privacy/failure isolation. No schema/queue/package/prompt/provider/layout/live change. Complete applies this diagnostic capability ONLY; production omission cause and correction remain unresolved, ARCH070 remains In Progress.

### Follow-up

Root merges source then actual parent gitlink, verifies deployed source/startup/drain before fresh genuine customer retry. Root synthetic equivalent probe only proved provider can return selection, not historical reproduction. Use actual shape to define any separately bounded application correction; do not fabricate selections, weaken guard or claim incident fixed from this acceptance.

## Developer Integration

Root merged sourcePR225 exact reviewed58783dd643ff75e2ce8e6618277a606fc4b10eee into actual Backgroundmainbe077bf7bd6b5e7f5a91fad1ee84c75dc76e13fa at2026-11-14T08:58:22Z. Architect independently fetched actual main and verified reviewedsource ancestor and complete tree equality. At root's explicit request, this feature branch pins only moda-interact-background to actualmergedbe077 and records integration; parent origin/main already current. No primary/unrelated staged work touched, no parentmain merge or live operation. Root owns final PR1039 merge and diagnostic rollout/drain/freshgenuine evidence; no incident-fixed claim.
