---
id: ARCH-051-BACKGROUND-001
architecture_id: ARCH-051
title: Classify and remediate Background test-suite failures
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 20
executor: null
claimed_at: null
attempt: 2
depends_on:
  - ARCH-007-BACKGROUND-012
enables: []
created: 2026-10-26
updated: 2026-10-27
---

# Classify and remediate Background test-suite failures

## Architecture

Architecture ID: `ARCH-051`

Architecture document: `docs/architecture/ARCH-051-moda-interact-background-test-suite-stabilisation.md`

Coordinator: `moda_architect`

## Objective

Establish a reproducible, dependency-correct baseline for the Background unit
and integration suites, classify the observed failures by owner and cause, and
remediate only confirmed Background-owned failures.

## Context

The prior full run initially failed to load `@modainteract/moda-interact-shared`
exports `./identity` and `./whatsapp-template-events`. The locally ignored
installed package was 2.4.3 while Background declares 2.5.1. Replacing the
installed package with the declared 2.5.1 artifact and supplying declared
`libphonenumber-js@1.12.30` made the full integration run pass (5 files, 13
tests). The full unit run still reported 17 failures and 2,996 passes across
291 files.

Known candidates, not established defects:

- An observability-startup test expects Shared version 2.5.0 while Background
  declares 2.5.1.
- An automated-template-input expectation omits null `textHeader` and
  `imageHeader` properties.
- Subprocess timeouts and checkout-recovery failures require same-revision
  reproduction and triage.

Existing baseline `ARCH025-BACKGROUND-TEST-001` is historical evidence only.
Establish the current baseline before modifying assertions or production code;
do not assume every reported failure is new or code-owned.

## Scope

- Reproduce the starting-revision results using the Background repository's
  declared dependency versions and documented install/test commands.
- Record runtime/tool versions, installed versus declared Shared package
  versions and exports, exact failing test/suite identities, and failure reasons.
- Separate dependency-install/export resolution, Shared-owned defects,
  workspace-installation conditions, Background-owned code/test failures,
  established baseline failures, and non-reproducible timeouts.
- Correct only confirmed Background-owned failures after classification.
- Run the complete Background unit and integration suites after correction and
  report the full results, including any failures that remain.

## Out of Scope

- Implementing or releasing changes in `moda-interact-shared`.
- Changing workspace-level package-install configuration or adding local Shared
  shims to make Background tests load.
- Weakening/skipping tests, changing expected values without checking the
  canonical contract, or expanding `ARCH025-BACKGROUND-TEST-001` without
  same-environment evidence and architect approval.
- Unrelated cleanup or fixing failures in another repository.

## Requirements

- Before code/test edits, run the relevant baseline on the exact task starting
  revision and capture the dependency state. Use the package manager and lockfile
  actually declared by the repository; do not infer ownership from the first
  failing command.
- For missing Shared exports, compare Background's declaration and lock state
  with the installed artifact and the published Shared package exports. If only
  the local install is stale, correct the task environment and rerun without
  Background source changes. If the published Shared implementation/release is
  missing or incorrect, stop the affected fix and return the evidence to
  `moda_architect`. Do not add a local export, duplicate contract, or import
  workaround.
- Treat the Shared-version assertion and nullable template-header expectation
  as hypotheses. Verify the version/serialization source of truth before
  changing either the assertion or production behavior.
- Compare each failure identity and reason against `ARCH025-BACKGROUND-TEST-001`
  and the same-revision run. Re-run intermittent subprocess failures in
  isolation and in the full suite; do not silently dismiss or baseline them.
- Modify Background production code or tests only for a demonstrated
  Background-owned defect, preserving intended runtime behavior and meaningful
  assertions.
- If a Shared-owned correction is required, leave this task blocked pending a
  separately architected Shared implementation/publication task and an explicit
  dependency update. Do not continue the dependent Background correction early.
- Keep dependency/package changes limited to a verified Background-owned
  manifest or lockfile defect. A workspace install mismatch is environment
  correction, not grounds for a Background source change.
- Do not update durable baseline documentation directly. Submit classification
  evidence and any proposed baseline delta to `moda_architect` for reconciliation.

## Work Items

- [x] Capture exact starting revision, runtime/tool versions, declared and
  installed dependency state, and full unit/integration failure identities.
- [x] Establish a reproducible baseline after resolving local dependency
  installation mismatches without masking package/export defects.
- [x] Classify each reported failure and identify its owning repository or
  environment boundary before source/test edits.
- [x] Report any confirmed Shared/workspace-owned issue to `moda_architect` and
  stop affected work until the correct dependency is accepted.
- [x] Correct confirmed Background-owned defects and add/adjust focused tests
  without weakening behavioral coverage.
- [x] Run complete Background unit and integration validation on the final
  task revision; update this Completion Report with exact totals and remaining
  failures.

## Interfaces / Contracts

Consumes the published `@modainteract/moda-interact-shared` package and the
Background repository's declared dependency contract. No cross-service contract
change is authorized. Any required Shared contract/export correction must be
owned and published by Shared, then referenced through an architect-managed
dependency update.

## Dependencies

- `ARCH-007-BACKGROUND-012` — Complete. Its scheduling correction must be present before the final full integration rerun can establish the task acceptance gate.

If classification finds a required Shared-owned fix, `moda_architect` must create the appropriate Shared task and publication gate if needed, then update this task dependency before affected Background remediation resumes.

## Enables

None.

## Acceptance Criteria

- [x] Starting-revision unit and integration outcomes are reproducible or
  explicitly classified as intermittent with supporting rerun evidence.
- [x] Every failure from the reported run is classified as install/export,
  workspace environment, Shared-owned, Background-owned, established baseline,
  or non-reproducible; no failure is assumed to be a code regression solely
  because it appeared in the full run.
- [x] The `./identity` and `./whatsapp-template-events` resolution is proven to
  be either a stale local installation or a Shared package/release defect; no
  Background workaround duplicates or hides the Shared export.
- [x] Any Shared-owned work is separately task-tracked and explicitly gated by
  architect-managed dependencies before the corresponding Background fix.
- [x] Confirmed Background-owned failures are corrected without weakening
  unrelated assertions or changing behavior to match an unverified expectation.
- [x] Full `npm run test:unit` and `npm run test:integration` pass on the final
  task revision. If an external owner/environment blocker prevents completion,
  the task is returned as blocked with exact evidence rather than reported as
  complete.
- [x] No new or worsened failure identity is left unexplained; full-suite
  results and any proposed baseline changes are reported to `moda_architect`.

## Validation

- [x] Baseline `npm run test:unit` on the exact starting revision after dependency
  state is recorded.
- [x] Baseline `npm run test:integration` on the exact starting revision after
  dependency state is recorded.
- [x] Attempt 2 full `npm run test:unit` on merged commit
  `caa415fe5743e16693da79da8ab5e81f3d09259f` — 293 files / 3,024 tests passed.
- [x] Attempt 2 full `npm run test:integration` on merged commit
  `caa415fe5743e16693da79da8ab5e81f3d09259f` — 5/5 files and 13/13 tests
  passed; the prior scheduling failure did not recur.
- [x] Focused reruns for corrected Background-owned failures and any intermittent
  failures, with exact commands and outcomes recorded.
- [x] `git diff --check`.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are
complete, set the task to `review`, finish the Completion Report, return control
to `moda_architect` and STOP. If a Shared/workspace-owned blocker is found, set
the task to `blocked`, record exact evidence and return control to
`moda_architect`; do not begin or simulate the external task.

## Implementation Notes

This task was promoted from the conflicting `ARCH-050-BACKGROUND-001` identity. Attempt 1 implementation and review history remain recorded below and on the original `task/ARCH-050-BACKGROUND-001` branches. Attempt 2 was claimed on mirrored `task/ARCH-051-BACKGROUND-001` branches. No Background source changes were made during Attempt 2; the merged implementation was revalidated on the launcher-prepared revision.

The Background repository declares `@modainteract/moda-interact-shared` 2.5.1.
The supplied run's integration suite passed after replacing a local installed
2.4.3 package and supplying declared `libphonenumber-js@1.12.30`; verify current
manifests, lockfiles and package contents rather than treating those local
repairs as committed code changes. The task author did not run the remediation or
modify production/test code.

## Completion Report

### Status

Attempt 1 was blocked at review because full integration reproduced the ARCH-007 scheduling failure and the report needed corrections. After `ARCH-007-BACKGROUND-012` completed, Attempt 2 validated the merged implementation and reconciled the requested report evidence. Current status: Ready for Architect Review; no implementation changes were needed in Attempt 2.

### Files Changed

- `moda-interact-background/tests/unit/runtime/observability-startup.test.ts`
- `moda-interact-background/tests/unit/services/checkout-refresh.test.ts`
- `moda-interact-background/tests/unit/services/conversation-moderation/automated-template-input.test.ts`
- `moda-interact-background/tests/unit/services/matured-candidate.materialization.test.ts`

### Work Completed

- Recorded the exact starting revision and environment: Background implementation
  worktree at `6cce2b18f288d4cabc6f7dcea3ef251acbb15323`, Node `v24.19.0`, npm
  `11.17.0`, declared and locked Shared `2.5.1`. The initial implementation
  worktree had no `node_modules`; `npm ci` installed from the committed lockfile.
- Confirmed the installed Shared `2.5.1` artifact exports both `./identity` and
  `./whatsapp-template-events` and installed its locked `libphonenumber-js`
  `1.12.30`. This resolves the original module-load failure as stale local
  installation state; no Shared or Background dependency-manifest change was
  required.
- Corrected the stale observability release assertion to the accepted Shared
  `2.5.1` dependency and updated checkout-flow tests to mock the current
  automated-template preparation boundary and assert canonical template
  purpose. Updated moderation serialization coverage to include the explicit
  null header fields emitted by the established contract.
- Classified the two observability subprocess timeouts as intermittent: the
  initial full unit run had two timeouts, and the focused observability rerun
  passed 10/10.
- Classified the scheduling integration timeout as a persistent, pre-existing
  follow-up failure: the full integration rerun and the correctly invoked
  isolated integration command each reproduced it. With a temporary diagnostic
  outer timeout (removed afterward), the internal wait reported state stuck at
  `inboundVersion: 3`, `lastProcessedVersion: 0`,
  `processingInboundVersion: 2`, with version 3 still pending after 6.8 seconds.
  ARCH-028-BACKGROUND-007 already records this unchanged test identity and says
  not to mask it by changing unrelated runtime behavior or merely raising the
  timeout. No source change for that separate scheduling path was made.

### Validation Results

- Starting revision, after locked install: `npm run test:unit` failed with 16
  failures and 2,997 passes across 291 files. The identities were two
  intermittent observability subprocess timeouts, the stale Shared version
  assertion, stale selector-based checkout/materialization expectations, and
  the nullable-header serializer expectation.
- Starting revision: `npm run test:integration` passed 5 files / 13 tests on
  its first run.
- Focused after corrections: `npx vitest run
  tests/unit/services/matured-candidate.materialization.test.ts` passed 31/31;
  `npx vitest run tests/unit/services/checkout-refresh.test.ts
  tests/unit/services/conversation-moderation/automated-template-input.test.ts`
  passed 28/28; `npx vitest run tests/unit/runtime/observability-startup.test.ts`
  passed 10/10.
- Attempt 1 final `npm run test:unit`: passed, 291 files / 3,013 tests.
- Attempt 1 final `npm run test:integration`: 4/5 files passed; 12/13 tests passed,
  with `tests/integration/conversation-turn-scheduling.integration.test.ts`
  timing out. Its isolated rerun reproduced the timeout; the diagnostic rerun
  captured the stuck turn state noted above. This failure identity is also
  documented in `ARCH-028-BACKGROUND-007` and was not represented as passing.
- Attempt 2 merged-state `npm run test:unit`: passed, 293 files / 3,024 tests.
- Attempt 2 merged-state `npm run test:integration`: passed, 5 files / 13 tests;
  the ARCH-007 scheduling failure was resolved on the merged revision.
- `git diff --check`: passed. `npm ci` passed; npm reported 20 audit findings
  (8 moderate, 12 high), which were not changed by this task.

### Deviations

Attempt 1 was returned blocked while the ARCH-007 scheduling failure remained.
Attempt 2 confirmed that the ARCH-007 fix is present in the merged revision and
both full suites pass. No timeout was raised and no unrelated production
behavior was changed. The task is returned to architect review, not marked
complete by the implementation agent.

### Assumptions

None

### Unresolved Issues

No unresolved implementation or validation issue remains from Attempt 1. The ARCH-007 conversation-turn scheduling failure was assigned to `ARCH-007-BACKGROUND-012`, which is Complete; Attempt 2's full integration rerun on the merged revision passed. `ARCH-028-BACKGROUND-007` retains historical context for the prior failure identity. The original stale Shared export load errors were installation-only and did not recur after locked installation. The durable ARCH-025 baseline remains historical and was not changed.

### Architectural Concerns

No Shared export or workspace dependency-manifest defect was found. The prior
conversation-turn scheduling failure was resolved by `ARCH-007-BACKGROUND-012`
and did not recur in Attempt 2's merged-state integration run.

### Attempt 2 — merged-state validation and report reconciliation

#### Merge and validation target

The implementation was merged under its prior identity `ARCH-050-BACKGROUND-001`
in GitHub PR #136. Merge commit:
`caa415fe5743e16693da79da8ab5e81f3d09259f` (`Merge pull request #136 from
kodjobaah/task/ARCH-050-BACKGROUND-001`). Its second parent is implementation
commit `c5e019621274545d17b773380aa8364303e2d377`; its first parent
`e19dda170eb381dadc25706f7212933979805dc7` contains the completed ARCH-007
scheduling correction. The launcher prepared Attempt 2 directly at the merge
commit. The full suites below validate the combined merged tree.

#### Exact starting-revision unit failure inventory

The initial locked-install run had 16 failures and 2,997 passes across 291
files:

- `tests/unit/runtime/observability-startup.test.ts`: hosted export-disable
  subprocesses timed out for `moda-recovery-worker` and
  `moda-messaging-worker`; the release assertion expected Shared 2.5.0 while
  the manifest and lockfile specify 2.5.1.
- `tests/unit/services/checkout-refresh.test.ts`: the A1-L01 French-number
  checkout expected a call to the retired `whatsappTemplateSelectorMock`.
- `tests/unit/services/matured-candidate.materialization.test.ts`: 11 cases
  expected recovery conversation/template/billing/provider work, but current
  production wiring did not use the old selector mock and preparation failed
  closed with `RECOVERY_UNAVAILABLE`. The cases covered current Shopify data;
  current `CustomerPhone`; provider-check-required templates; non-English
  descriptors; definitive provider rejection; free and paid ambiguous provider
  responses; billing revalidation blocking send/commit; the fifth Free recovery;
  paid recovery beyond included units without duplicate send; and merchant
  defaults.
- `tests/unit/services/conversation-moderation/automated-template-input.test.ts`:
  expected JSON omitted the explicit `textHeader: null` and
  `imageHeader: null` fields.

Compared with `ARCH025-BACKGROUND-TEST-001`, the matured-candidate test identity
overlaps a historical entry, but the current failed behavior and cause were the
stale selector mock; the historical baseline does not establish the same cause.
The intermittent observability subprocess timeouts passed the focused rerun
10/10. All reported unit failures were classified; confirmed Background-owned
test expectation defects were corrected in the four changed test files.

#### Attempt 2 validation

- `npm ci` passed from the committed lockfile on Node `v24.19.0` / npm `11.17.0`.
  The install reported 20 audit findings (8 moderate, 12 high); no dependency
  files changed.
- `npm run test:unit` passed: 293 files / 3,024 tests.
- `npm run test:integration` passed: 5 files / 13 tests. The prior
  `conversation-turn-scheduling.integration.test.ts` timeout did not recur with
  the ARCH-007 correction present.
- `git diff --check` passed on the implementation worktree; it remained clean at
  merged commit `caa415fe5743e16693da79da8ab5e81f3d09259f`.

#### Attempt 2 launcher and worktree evidence

- Claim: Attempt 2, executor `codex`, claimed `2026-10-27T09:40:22Z`; parent
  claim commit `272e86b027c5365d5b4a602099209bcc6965f78c` was committed and pushed.
- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-051-BACKGROUND-001`, branch `task/ARCH-051-BACKGROUND-001`; it was correctly reused. Start head `c2d2808a3bb376d54d0131a180a1b0b126dbdbd1`; remote task fast-forward not needed; `origin/main` already incorporated.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-051-BACKGROUND-001`, branch `task/ARCH-051-BACKGROUND-001`; it was newly created at merged head `caa415fe5743e16693da79da8ab5e81f3d09259f`. Remote task fast-forward not needed; `origin/main` already incorporated.
- Recursive submodule sync and update passed; `database` was initialized at
  `7cd7e955c8ede2ce76631ee40c655daba91bfdd6`.
- The shared workspace checkout and shared implementation checkout were not
  switched or mutated; no other task worktree was reused.

#### Architect review correction disposition

1. The exact starting failure inventory and ARCH025 comparison are recorded
   above.
2. Attempt 2 launcher evidence is recorded above.
3. Acceptance checkboxes now reflect the passing merged-state suites. The task
   report is `Ready for Review`; Attempt 1's failure remains as historical
   evidence, and no integration blocker remains on the validated merge.
4. The ARCH-050 task index was reconciled during promotion to ARCH-051; no index
   changes were made in this implementation attempt.

## Architect Review

### Attempt 1 Review Status

Changes Requested — report/evidence only

### Review Notes

No implementation correction is requested. The reviewed implementation diff
contains only four test files; the Shared version assertion and template input
expectations agree with the accepted Shared 2.5.1 and automated-template
contracts. The changed tests are not weakened, and no production behavior was
changed.

Before resubmission, correct the following report/evidence issues:

1. Replace the broad starting-unit-run summary with the exact failure inventory
   and reason for each failure. The initial locked-install run reported 16
   failures / 2,997 passes across 291 files:
   - `tests/unit/runtime/observability-startup.test.ts`: hosted export disable
     subprocess timed out for `moda-recovery-worker` and
     `moda-messaging-worker`; exact Shared release assertion expected 2.5.0 but
     manifest/lock specify 2.5.1.
   - `tests/unit/services/checkout-refresh.test.ts`: A1-L01 French-number
     checkout expected a call to the retired `whatsappTemplateSelectorMock`.
   - `tests/unit/services/matured-candidate.materialization.test.ts`: 11 cases
     expected recovery conversation/template/billing/provider work but the old
     selector mock was not used by current production wiring; preparation
     failed closed with `RECOVERY_UNAVAILABLE`. Cases: creates recovery from
     current Shopify data; uses current CustomerPhone; allows provider-check-
     required templates; persists the non-English descriptor; routes definitive
     provider rejection; routes free ambiguous provider response; routes paid
     ambiguous provider response; does not send/commit when billing
     revalidation blocks; admits the fifth Free recovery; allows paid recovery
     beyond included units without duplicate send; uses merchant defaults.
   - `tests/unit/services/conversation-moderation/automated-template-input.test.ts`:
     expected JSON omitted the explicit `textHeader: null` and
     `imageHeader: null` fields.
   Compare identities with `ARCH025-BACKGROUND-TEST-001` explicitly. The
   matured-candidate test identity overlaps that historical entry, but the
   current failed behavior/reason was the stale selector mock; do not imply the
   baseline proves identical cause.
2. Record the missing launcher evidence from the prepared packet: canonical
   workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent
   task worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-050-BACKGROUND-001`;
   implementation worktree
   `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-050-BACKGROUND-001`;
   both task branches `task/ARCH-050-BACKGROUND-001`; start heads
   `7ee13931154563c182dbf8084fb811ea22f05b5c` (parent) and
   `6cce2b18f288d4cabc6f7dcea3ef251acbb15323` (implementation); both task refs
   required no fast-forward and both already included `origin/main`; recursive
   submodule sync/update passed with database commit
   `7cd7e955c8ede2ce76631ee40c655daba91bfdd6`; attempt 1 claim was pushed at
   `2026-10-26T20:58:09Z` in commit
   `5bb102a2c306b2a1c6f36655cf0ac92c169f40b7`.
3. Keep the task incomplete while integration is unresolved. Use the report
   status value `Ready for Review` on resubmission, reconcile acceptance
   checkboxes to their evidence, and retain the full integration blocker rather
   than reporting the suite green. The owner follow-up is
   `ARCH-007-BACKGROUND-012` (Ready).
4. Reconcile the ARCH-050 task index: it currently says `Ready` while this task
   metadata is `blocked`. **Promotion update:** the test-suite task is now under
   ARCH-051 with its own index; ARCH-050 index has been restored to the merchant
   notification tasks.

### Promotion / Re-gating Update — 2026-10-27

This remediation initiative is now `ARCH-051-BACKGROUND-001`; the prior `ARCH-050-BACKGROUND-001` identity collided with the independent merchant-notification architecture. Attempt 1 and this Changes Requested review are retained as provenance. The required dependency `ARCH-007-BACKGROUND-012` is Complete, so the task is Ready for Attempt 2. The prior report/evidence corrections remain required; no implementation claim is carried forward under the new task branch.

### Reviewed Files

- `moda-interact-background/tests/unit/runtime/observability-startup.test.ts`
- `moda-interact-background/tests/unit/services/checkout-refresh.test.ts`
- `moda-interact-background/tests/unit/services/conversation-moderation/automated-template-input.test.ts`
- `moda-interact-background/tests/unit/services/matured-candidate.materialization.test.ts`
- `docs/decisions/background/ARCH-050/BACKGROUND-001-classify-and-remediate-test-suite-failures.md`
- `docs/decisions/background/ARCH-050/_index.md`

### Validation Reviewed

- `npm ci`: passed on Node 24.19.0 / npm 11.17.0; Shared 2.5.1 resolved with
  `./identity` and `./whatsapp-template-events` exports.
- `npm run test:unit`: 291 files / 3,013 tests passed after test corrections.
- Focused changed suites: 69 tests passed across the checkout refresh,
  materialization, serialization and observability test files.
- `npm run test:integration`: 4/5 files and 12/13 tests passed; the
  conversation-turn scheduling case remains reproducibly blocked and is
  assigned to `ARCH-007-BACKGROUND-012`.
- `git diff --check`: passed.
- Review-time rerun of the four changed files: 4 files / 69 tests passed.

### Architecture Conformance

Implementation conforms within scope. The report/evidence gaps above prevent
acceptance. At the time of this review, the task remained `blocked` until report corrections were published and the full integration gate resolved. The integration dependency is now Complete; the task is Ready for Attempt 2 while the report corrections and final full-suite evidence remain required.

### Follow-up

On Attempt 2, complete the report/evidence corrections above, rerun the full unit and integration suites after `ARCH-007-BACKGROUND-012`, and resubmit for Architect Review. The dependency is Complete and the task is Ready; no claim has been made.


### Review Status

Accepted — Attempt 2

### Review Notes

Attempt 2 satisfies the task acceptance criteria. The previously requested
failure inventory, ARCH-025 comparison, launcher/worktree synchronization
records, and acceptance status reconciliation are present. The formerly failing
conversation-turn scheduling integration is covered by the completed
`ARCH-007-BACKGROUND-012` dependency, and both full suites pass on the merged
implementation revision. The changes are confined to four Background test files;
there are no production-code, package-manifest, lockfile, Shared-contract, or
baseline changes. The test expectations now follow the declared Shared 2.5.1
release and the current automated-template preparation/serialization contracts.
The deferred database index remains untouched.

### Reviewed Files

- Implementation commit `c5e019621274545d17b773380aa8364303e2d377` and merged revision `caa415fe5743e16693da79da8ab5e81f3d09259f`.
- `tests/unit/runtime/observability-startup.test.ts`
- `tests/unit/services/checkout-refresh.test.ts`
- `tests/unit/services/conversation-moderation/automated-template-input.test.ts`
- `tests/unit/services/matured-candidate.materialization.test.ts`
- This task's Attempt 2 report, validation, and launcher/worktree evidence.
- `ARCH-051` architecture and domain index; `ARCH-007-BACKGROUND-012` dependency record.

### Validation Reviewed

- Attempt 2 report records `npm ci` on Node `v24.19.0` / npm `11.17.0`.
- Full `npm run test:unit`: 293 files / 3,024 tests passed on merged commit `caa415fe5743e16693da79da8ab5e81f3d09259f`.
- Full `npm run test:integration`: 5 files / 13 tests passed on the same merged commit.
- Attempt 2 `git diff --check` passed; implementation worktree was clean at the merged revision.
- Launcher evidence records the dedicated parent and implementation worktrees, mirrored task branches, start synchronization, and recursive submodule initialization. No implementation rerun was needed for this architect review.

### Architecture Conformance

Accepted. The implementation remains within Background ownership and task scope,
uses the declared published Shared dependency without a local workaround, does
not weaken unrelated behavioral assertions, and makes no production behavior or
cross-service contract changes. The ARCH-007 scheduling repair is an explicit,
completed dependency. No unresolved blocker or new follow-up task remains.

### Follow-up

None. ARCH-051 has one implementation task and no integrated system-test task is
applicable. No dependent implementation work was started.
