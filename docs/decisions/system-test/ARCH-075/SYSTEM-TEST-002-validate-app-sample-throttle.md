---
id: ARCH-075-SYSTEM-TEST-002
architecture_id: ARCH-075
title: Validate durable sample throttle across replicas
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 5
executor: codex
claimed_at: 2026-11-13T12:34:39Z
attempt: 1
depends_on:
  - ARCH-075-ADMIN-006
  - ARCH-075-DATABASE-002
  - ARCH-075-BACKGROUND-007
  - ARCH-075-SYSTEM-TEST-001
enables: []
created: 2026-11-13
updated: 2026-11-13
---

# Validate durable sample throttle across replicas

## Architecture

ARCH-075; docs/architecture/ARCH-075-ordered-recovery-message-layout.md; coordinator moda_architect.

## Objective

Validate durable sample throttle across replicas.

## Context

Actual Meta sample_session HTTP403/code4 app request limit was classified as permanent blocked. One upload perlocale plus60second local polling and replica overlap can amplify calls; changing classification alone does not give durable cooldown. Existing scheduler leases/config/audit rows are not proper app-scoped lifecycle state. Generic historical rejection events do not carry code4 evidence.

## Scope

Terminal independent disposable PostgreSQL/worker/provider-simulator validation of the accepted new app throttle capability only. Preserve SystemTest001 accepted proof/history.

## Out of Scope

Other repositories except explicit accepted submodule adoption, provider credentials/grants, live sends/repair/deployment, Shared publication, blind create retry, unsupported caching, generic refactors or implementation-source merges.

## Requirements

Also reconcile accepted Admin006 repeated-retry audit proof using actual domain fixtures where appropriate; preserve original SystemTest001 acceptance and do not duplicate unrelated full delivery validation.

Exercise actual accepted sample/provider/submit path and dedicated durable app state across two independent workers/processes: one evidenced code4 produces persistent backoff, stops remaining same-app uploads across cycle/restart/replica and leaves template creation unclaimed; current auth403 remains nonretryable; other app/environment cannot inherit authority. Verify exact operator-evidenced recovery refuses ambiguous/intent-bearing historical blocks and cannot bypass cooldown. Reuse source/image provenance strategy only with explicit accepted-source manifests and Linux runtime Prisma generation for the new model; no host native clients copied. No production build-parity/live/fleet/provider approval claim. No implementation task depends on this terminal task; execute only after accepted prerequisites and root manual checkpoint.

## Work Items

- [x] Implement only the owning bounded outcome and final contract.
- [x] Prove meaningful failure/concurrency/compatibility behavior.
- [x] Complete mirrored report/checks, return review and stop.

## Interfaces / Contracts

Database002 owns durable Prisma/SQL state. Background007 consumes exact accepted schema and owns provider policy/leases/recovery; no new Shared contract. SystemTest002 is terminal validation. Root owns migration/deployment/operational evidence; no network inside transaction.

## Dependencies

ARCH-075-ADMIN-006, ARCH-075-DATABASE-002, ARCH-075-BACKGROUND-007, ARCH-075-SYSTEM-TEST-001

## Enables

None

## Acceptance Criteria

- [x] Assigned bounded capability/invariants and explicit negative behavior satisfied.
- [x] Existing provider-intent, tenant/environment, immutable source and legacy lifecycle guards remain intact.
- [x] Canonical matching physical isolation/sync and exact validation evidence reported; no live mutation.

## Validation

- [x] Deterministic real PostgreSQL/replica/provider fault scenarios, exact source/migration/image identities and bounded captured telemetry/privacy; relevant harness/static checks. No broad rerun of unchanged ordered-layout scenarios or real API requests.
- [x] Diff/privacy hygiene; no secrets/private production identifiers or unsupported capability claim.

## Stop Condition

When scope/checks complete, submit Completion Report/status review and STOP. No enabled task, source merge, hosted migration or live recovery/provider action.

## Implementation Notes

Accepted source identities: Background `ce9d6e1017f553d307f21899c20f713d514189fd`; Database `6f42b71112efe7ac63654d55f41cd74ca569b1ae`; Admin `e0699c99e82f12fd8c2a778f38a0a44cebb8a2cf`; accepted SystemTest001 merge `05676a22d111081f3889a0fddcb16820077e3ec6`. New migration `20261113111320_arch075_meta_app_operation_state` SHA256 `413aa05032522ee291cb406325bccbc8dd3c92cf42046ed9841000d5832b856c`. Use exact accepted source provenance in independent disposable fixtures; do not mutate owning repositories. Root explicitly passed the developer manual checkpoint for this terminal task. Preserve prior accepted integrated proof and its documented correctness-image build limitation.

You are not alone; preserve other work. Canonical launcher packet owns start/claim. Root owns all final merges, test/prod migration, worker rollout/drain and protected live evidence. New domain logs reuse published Shared logging; do not duplicate generic telemetry. Return genuine contract gaps before widening scope.

## Completion Report

### Status

Ready for Review. Independent local proof only; no live repair/fleet/provider
approval claim. Implementation `0ea7b4c6c997feb32f9c433d3e0a8073601fb71b`
is committed and pushed on `task/ARCH-075-SYSTEM-TEST-002`.

### Files Changed

- Capability scripts `validate:meta:sample-throttle` and
  `build:meta:sample-throttle-image` plus package script declarations.
- `src/harness/meta-sample-throttle/`: exact source/image audit, disposable
  session, actual Admin confirmation/retry bundle, two-process sample adapter/
  due-service fixtures, local HTTP simulator and strict operator history cases.
- `test/harness/meta-sample-throttle-image.test.js`: bounded output allowlist,
  removal/new CLI runtime/foreign output refusal.
- `docs/validation/meta-sample-throttle*.md`: exact results, identities, hashes,
  commands and process/build limitations. No accepted SystemTest001 file changed.
- Only this parent task report/lifecycle is independently staged; no gitlink,
  index, architecture, policy, other task or rollup staged.

### Work Completed

Prepared claim `a48ed6ecffb4472bcca7813dca9e7604b74a0c68`, attempt 1, executor
codex reused without reprepare/reset. Canonical workspace
`/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent
`/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-075-SYSTEM-TEST-002`;
implementation
`/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-075-SYSTEM-TEST-002`.
Both dedicated branches `task/ARCH-075-SYSTEM-TEST-002`; no shared/default or
another task checkout switched/mutated. Packet parent head dcbfb91e5 and
implementation head 05676a22d already incorporated origin/main; remote task branch
fast-forward not needed. Recursive implementation sync/update passed, no
submodules. Launcher dependency gate/manual checkpoint passed; existing Architect
Review was Pending, with no Changes Requested correction checklist.

Exact accepted source: Background `ce9d6e1017f553d307f21899c20f713d514189fd`,
Database `6f42b71112efe7ac63654d55f41cd74ca569b1ae`, Admin
`e0699c99e82f12fd8c2a778f38a0a44cebb8a2cf`; SystemTest001 baseline
`05676a22d111081f3889a0fddcb16820077e3ec6` preserved.

### Validation Results

Final real disposable PostgreSQL/local HTTP/independent Node22 process proof:
**8 integration scenarios passed**, 2026-11-13T12:58:20.752Z–13:00:32.027Z.
There were 18 container invocations: sixteen domain worker invocations and two
migration/inventory invocations; these are not eighteen distinct replicas or
Node unit test cases.

- Hold first actual sample-session request while another process races; exactly
  one app 111 HTTP403/numeric code4 persists a roughly 900-second cooldown. Overlap
  and two fresh-process cycles make no further same-app HTTP request. Fifteen
  registrations defer durably; all remain unclaimed before the explicit
  different-app positive case.
- Current auth403/code190 blocks permanently; repeat makes no HTTP request and
  app 222 throttle count stays 0. App 333 independently succeeds through actual
  session/upload/find/create; exactly one CREATE_INTENT/POST_INTENT/CREATE_RESULT
  belongs to that positive case. Six total simulator HTTP calls, no live calls.
- Separate processes fence expired lease generations; foreign app/environment
  identities cannot inherit authority. Distinct apps with expired histories
  exercise 900/1800/3600/7200/14400/21600/21600-second policy intervals and durable
  increments, with real SQL cooldown-regression rejection asserted.
- Exact synthetic historical cohort/numeric code4 attestation required; string
  code4 and foreign IDs refuse, intent-bearing history refuses, dry run leaves
  rows untouched, wrong digest/environment/app refuses. Apply/replay writes one
  operator audit, preserves frozen snapshots and never shortens cooldown. Even
  a deliberately stale registration retry date cannot bypass app cooldown.
- Foreign WABA refuses before sample/intent. Captured telemetry 39,985 bytes passes
  four injected token/URL/email/phone absence checks. One throttle and four
  deferral events persisted. All owned containers cleaned.
- Actual Admin006 services: two nonempty retries have distinct audit IDs; two
  concurrent repeats and an empty repeat are no-ops, completed item is unchanged,
  and audit-FK failure rolls back retry writes. No translation provider called.
- All **78 migrations** finish and match owning checksums. New migration
  `20261113111320_arch075_meta_app_operation_state` SHA256
  `413aa05032522ee291cb406325bccbc8dd3c92cf42046ed9841000d5832b856c`.

Focused harness tests **13 passed, zero failed, one existing opt-in generic
Docker smoke test skipped**; actual new PostgreSQL integration above ran.
Final lint passes syntax for 290 JS files and source/test structural limits; catalogue
and diff/privacy checks pass. Counts distinguish unit tests, integration
assertions, process invocations and HTTP calls.

Image provenance: final immutable
`sha256:bd00e5524f05597030995b95ba8328a4c6aea054b6c7a8e5be7cb49fcae2957b`
over accepted keyed base
`sha256:dd73ff316ac7eb7b6c335291163a27e673968b94392784c2afbbb50fe75fd319`.
Exactly 16 named compiler outputs differ/new; other 1,120 runtime outputs match.
Locked TS6.0.2 declared ES2022/NodeNext under host24.19; actual Linux Node22.23.5,
Prisma6.19.3, new model present, NODE_OPTIONS absent. Exact accepted Prisma source
copied and client generated inside Linux; no host clients/native dependencies
copied. Inherited Linux dependency layers and runtime ENV/CMD/entrypoint retained,
with declared generated-client change. Whole package/lock/tsconfig hashes pinned.

Full source/module old-new/Dockerfile/schema/map hashes and limits:
`docs/validation/meta-sample-throttle-evidence.md`; private local
`/tmp/moda-throttle-image.json`, `/tmp/moda-throttle-run-final.log`,
`.validation/meta-sample-throttle/results.json`, captured telemetry.log.

### Deviations

Image audit stopped on the additional corresponding contracts CLI source map.
Architect explicitly approved that single map only: source resolves solely to
accepted contracts.ts type-only change, both maps omit sourcesContent, old/new
hashes recorded and corresponding CLI JS stays byte-identical. No other CLI
runtime/output expansion accepted.

Preliminary fixture tried to shorten active cooldown and correctly hit
META_APP_OPERATION_COOLDOWN_REGRESSION. Final fixture seeds expired prior
histories in distinct synthetic apps and asserts regression refusal; no database
trigger/application guard was relaxed. Controlled disposable lease/retry-date
fixtures establish fencing; they are not live operational permission.

### Assumptions

No provider reset guarantee; computed durations are bounded internal policy.
Historical attestation/worker references are synthetic and cannot authorize live
repair. Actual process boundary is accepted due/submit/sample/operator services
in independent processes with a packaged validated sample replacing R2, not the
full messaging entrypoint/Redis queues or a deployed fleet.

### Unresolved Issues

No owning-source implementation defect remains in this bounded validation.
No broad unchanged ordered-layout rerun or prior proof relabeling. Root owns
all final merges, hosted migration/deployment/drain and genuine live evidence.

### Architectural Concerns

Source-derived runtime correctness only; no production image/build-parity,
provider quality/approval, live recovery/activation/delivery claim. Test image
must never be promoted. No live credentials/settings/counters/sends/replays or
main merge performed.

## Architect Review

### Review Status

Pending

### Review Notes

Pending implementation.

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

None
