---
id: ARCH-056-SYSTEM-TEST-002
architecture_id: ARCH-056
title: Replace architecture-based test names
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
- ARCH-056-SYSTEM-TEST-001
enables: []
created: '2026-11-04'
updated: '2026-11-04'
---

# ARCH-056-SYSTEM-TEST-002: Replace architecture-based test names

## Architecture

Architecture: `ARCH-056`. Parent: `docs/architecture/ARCH-056-background-persistence-and-recovery-progress.md`. Coordinator: `moda_architect`. Definition revision: 3. **Defined but not materialised.** This final task is pending and unclaimed at attempt 0; it starts only after `ARCH-056-SYSTEM-TEST-001` is Complete and architect-accepted.

## Objective

Give permanent System-Test executables, scenarios and helpers capability names while preserving their behavior, coverage, governance traceability and accepted failure diagnostics. Make the existing naming convention enforceable through the repository's current catalogue and structure checks.

## Context

The user permits architecture identifiers in task/document names and requires tests/code to describe the capability they exercise. The new ARCH-056 producer definitions already use semantic names. This task handles the remaining legacy System-Test naming and verifies the complete accepted Background-persistence proof after those changes.

The existing workspace `docs/validation-command-naming.md`, `docs/validation-migrations/render-test-validator-naming.md` and System-Test consolidated plan distinguish reusable executable names from architecture provenance. Earlier Render naming work left two exit-64 deprecation tombstones. Their behavior remains intact under semantic filenames. Existing `ARCH002_TEST_*` input names remain an explicit compatibility contract.

This is a single-repository outcome. Existing API/Background architecture-coded filenames, Database migrations/functions, Shared exports and production idempotency/provider identities are not transferred to System-Test ownership. The blocked uncertain-outcome billing policy remains blocked; renaming existing 131026 scenarios does not certify the unfinished terminal ARCH-028 task.

## Scope

One owning repository: `moda-interact-system-test`; all implementation paths below are relative to it. The canonical parent `docs/architecture/ARCH-056/test-naming-map.json` supplies the exact legacy file/symbol/scenario/literal mapping and protected values. Its legacy System-Test section is the bounded transformation contract; do not run a global ARCH replacement. No production application repository, nested Database or parent coordination surface may be edited.

### Exact source/script moves

| Existing path | New path |
|---|---|
| `src/harness/recovery/arch028-credit-source-checkout-diagnostics.js` | `src/harness/recovery/credit-source-checkout-diagnostics.js` |
| `src/harness/recovery/arch028-credit-source-diagnostics.js` | `src/harness/recovery/credit-source-diagnostics.js` |
| `src/harness/recovery/arch028-credit-source-fixtures.js` | `src/harness/recovery/credit-source-fixtures.js` |
| `src/harness/recovery/arch028-credit-source-ingress-diagnostics.js` | `src/harness/recovery/credit-source-ingress-diagnostics.js` |
| `src/harness/recovery/arch028-credit-source-initial-diagnostics.js` | `src/harness/recovery/credit-source-initial-diagnostics.js` |
| `src/harness/recovery/arch028-credit-source-observation.js` | `src/harness/recovery/credit-source-observation.js` |
| `src/harness/recovery/arch028-credit-source-receipt-diagnostics.js` | `src/harness/recovery/credit-source-receipt-diagnostics.js` |
| `src/harness/recovery/arch028-credit-source-scenario.js` | `src/harness/recovery/credit-source-scenario.js` |
| `src/harness/recovery/arch028-purchased-source-fixture.js` | `src/harness/recovery/purchased-source-fixture.js` |
| `scripts/run-arch002-observability.js` | `scripts/run-integrated-observability.js` |
| `scripts/run-arch002-production-readiness.js` | `scripts/run-production-readiness.js` |
| `scripts/run-arch002-render-test-topology.js` | `scripts/deprecated-render-test-topology.js` |
| `scripts/run-arch028-compensation-smoke.js` | `scripts/run-terminal-recipient-compensation-smoke.js` |
| `scripts/system-test-006-developer-validation.sh` | `scripts/deprecated-render-test-validation.sh` |

### Exact test moves

| Existing path | New path |
|---|---|
| `test/harness/arch028-compensation-smoke.test.js` | `test/harness/terminal-recipient-compensation-smoke.test.js` |
| `test/harness/arch028-credit-source-checkout-diagnostics.test.js` | `test/harness/credit-source-checkout-diagnostics.test.js` |
| `test/harness/arch028-credit-source-ingress-diagnostics.test.js` | `test/harness/credit-source-ingress-diagnostics.test.js` |
| `test/harness/arch028-credit-source-receipt-diagnostics.test.js` | `test/harness/credit-source-receipt-diagnostics.test.js` |
| `test/harness/arch028-credit-sources.test.js` | `test/harness/credit-sources.test.js` |
| `test/harness/arch028-follow-up-diagnostics.test.js` | `test/harness/follow-up-diagnostics.test.js` |
| `test/harness/arch028-initial-outreach-diagnostics.test.js` | `test/harness/initial-outreach-diagnostics.test.js` |
| `test/harness/arch028-purchased-source-fixture.test.js` | `test/harness/purchased-source-fixture.test.js` |
| `test/harness/arch028-terminal-recipient-merchant-ui.test.js` | `test/harness/terminal-recipient-merchant-ui.test.js` |
| `test/harness/arch028-terminal-recipient-observation.test.js` | `test/harness/terminal-recipient-observation.test.js` |

All 24 paths are moves with corresponding import/reference updates. Content changes in the moved files are limited to the mapped local identifiers, test-owned names, diagnostic/progress labels, imports and required naming regression assertions. Do not delete cases or retain permanent executable aliases under the old paths.

### Existing reference consumers and guard owners

Modify only:

- `README.md`
- `catalogue/historical-system-test-map.json`
- `catalogue/scenarios.json`
- `docs/ARCH-028-COMPENSATION-SMOKE.md`
- `docs/ARCH-028-CREDIT-SOURCE-COMPENSATION.md`
- `docs/SHOPIFY-COVERAGE-MATRIX.md`
- `package.json`
- `scripts/run-credit-source-compensation.js`
- `scripts/validate-render-deployment.js`
- `scripts/validate-source-structure.js`
- `src/harness/messaging/terminal-recipient-merchant-ui.js`
- `src/harness/recovery/constants.js`
- `src/harness/recovery/index.js`
- `src/merchant-scenario.js`
- `src/render-test-topology.js`
- `src/scenario-catalogue.js`

The first six documentation/catalogue paths and `package.json` receive active reference/mapping updates. `src/scenario-catalogue.js` and `scripts/validate-source-structure.js` own the bounded naming guards. Remaining runtime/script consumers receive only the exact map's name/reference/label changes. In particular, `src/merchant-scenario.js` changes its listed synthetic display/fixture labels only; keep its apply/restore operations, provider calls, advisory lock and all mutation logic unchanged. `src/render-test-topology.js` and `scripts/validate-render-deployment.js` change mapped descriptive text only; preserve live input keys, hosts, authentication, request behavior and exit semantics.

Extend these existing tests:

- `test/harness/approved-template-fixtures.test.js`
- `test/harness/language-provider-runtime-setup.test.js`
- `test/harness/language-recovery-provider-setup.test.js`
- `test/harness/language-recovery-runtime-wiring.test.js`
- `test/harness/platform-configuration-fixture.test.js`
- `test/harness/recovery-executors.test.js`
- `test/harness/selection.test.js`
- `test/harness/source-structure.test.js`
- `test/scenario-catalogue.test.js`
- `test/render-test-topology.test.js`

The moved tests own their import/symbol/fixture-label adjustments. The additional `test/render-test-topology.test.js` owns deterministic subprocess assertions for both renamed tombstones, preserving stderr and exit 64 without invoking the advised live commands. No new test framework or production module is required.

Create only `docs/TEST-NAMING.md`, containing the current exact mapping, allowed compatibility/provenance values, active commands, evidence limits and open-owner handoff. Existing archived logs, evidence files and Complete review records remain unchanged. Current operator docs may retain architecture-based filenames because they are documents.

### Read-only dependencies

- `src/harness/selection.js`
- `scripts/run-system-tests.js`
- `src/harness/background-persistence/contracts.js`
- `src/harness/background-persistence/executors.js`
- `src/harness/background-persistence/runtime.js`
- `src/harness/background-persistence/evidence.js`
- `src/harness/background-production-image.js`
- `src/harness/recovery/runtime.js`
- `src/harness/messaging/provider-status-observation.js`
- `src/harness/messaging/terminal-recipient-observation.js`
- `src/harness/language/model-fixture.js`
- `src/harness/billing-executors.js`
- `src/observability-validation.js`
- `src/render-blueprint-validation.js`
- `scripts/validate-render-test.sh`
- `scripts/developer-validation.sh`
- `test/observability-validation.test.js`
- `test/render-blueprint-validation.test.js`
- `test/merchant-scenario.test.js`
- `test/harness/language-model-fixture.test.js`
- `test/harness/billing-executors.test.js`
- `test/harness/background-persistence-contracts.test.js`
- `test/harness/background-persistence-registration.test.js`
- `test/harness/background-persistence-provenance.test.js`
- `test/harness/background-persistence-fault-controls.test.js`
- `test/harness/background-persistence-results.test.js`
- `docs/BACKGROUND-PERSISTENCE-VALIDATION.md`

The Background-persistence modules/tests/document above are produced by the accepted predecessor, not present-time source assumptions. The workspace naming policies, parent architecture/maps, normal task/worktree policies and the two known unfinished task files named below are read-only coordination dependencies.

## Out of Scope

No application implementation or test rename; no schema/migration, Shared publication, provider protocol change, credit/permit/settlement policy change, cancellation/crash-recovery expansion, environment-input migration, new runner, generic parser/framework, new live validator, production-readiness correction or parent task lifecycle mutation. Do not rewrite historical reports to pretend they used the new names. Do not invoke deployed validators or seek live credentials for this naming task.

`ARCH-002-SYSTEM-TEST-010` retains the unrelated HAProxy/readiness correction. `ARCH-028-SYSTEM-TEST-001` retains its terminal/manual gate and 131026 scope. Existing ready status is not acceptance and is not, by itself, a new prerequisite on their unfinished behavior.

## Requirements

### Owned preflight and architect handoff

1. Accept the launcher-prepared System-Test and parent task worktrees. Recheck the predecessor's accepted status/revisions, current rename-source paths, collision-free destinations and actual branch/claim state. Capture the accepted catalogue, historical map, executor inventory, focused test results and relevant file identities before mutation.
2. An `in_progress` or `review` task with an overlapping writer is a concrete preflight blocker. Return the exact task/file conflict for architect sequencing before a naming mutation; do not silently merge around it or transfer ownership. A `ready` task alone does not add a dependency. Any approved intervening baseline change must be explicitly reconciled into the mapping before proceeding.
3. The Completion Report must provide the exact old/new executable-reference handoff for these known unfinished owners. Architect reconciliation of their current scope/command guidance is required **before accepting this cleanup**. The executor must not edit those task files, change their lifecycle or rewrite Complete historical reviews:

| Read-only parent task | Snapshot evidence and required handoff |
|---|---|
| `docs/decisions/system-test/ARCH-002/SYSTEM-TEST-010-reconcile-production-readiness-validator-with-haproxy.md` | Ready/attempt 0 at lines 9–13; capability objective at 25–27; stale `test/render-blueprint-validation.test.js` evidence at 37–46; bounded HAProxy scope at 50–54. Handoff `run-arch002-production-readiness.js` / `validate:arch002-production-readiness` to the semantic entrypoint/command and their unchanged core-test relationship. The task does not contain a literal old executable command; do not invent one. |
| `docs/decisions/system-test/ARCH-028/SYSTEM-TEST-001-validate-whatsapp-delivery-compensation-and-suppression.md` | Ready/attempt 0 at lines 12–16; unstarted/manual-gated note at 27; 131026 and uncertainty boundary at 45–47; future fixture work at 86–96; validation at 126–128. Handoff the three scenario IDs, moved credit-source helpers/importers and smoke entrypoint. Preserve its unchanged terminal scope, status and provenance warnings. |

The line locations identify the reviewed snapshot; use the actual current file at execution. The architect owns any required current reference amendments. Unchanged historical completion text is evidence, not a stale import to repair.

### Exact capability mapping

Apply the 11 local symbol changes together with their imports/exports and callers:

| Existing name | Capability name |
|---|---|
| `seedArch028CreditSource` | `seedCreditSource` |
| `seedArch028PurchasedSource` | `seedPurchasedSource` |
| `readArch028CreditSourceState` | `readCreditSourceState` |
| `assertArch028InitialCredit` | `assertInitialCredit` |
| `assertArch028CompensatedCredit` | `assertCompensatedCredit` |
| `assertArch028CreditReplay` | `assertCreditReplay` |
| `waitForArch028CreditState` | `waitForCreditState` |
| `failedArch028InitialCreditChecks` | `failedInitialCreditChecks` |
| `reportArch028CreditSourceFailure` | `reportCreditSourceFailure` |
| `runArch028CreditSourceScenario` | `runCreditSourceScenario` |
| `registerArch028CreditSourceScenarios` | `registerCreditSourceScenarios` |

Apply only the 56 file-scoped synthetic fixture/label/progress replacements recorded in the canonical naming map. They do not authorize changes to production keys or historical evidence. Preserve all mapped assertions, source-specific semantics, cleanup, timeouts and retry behavior. If another executable consumer is discovered outside the allowlist, return its exact path for an architect scope amendment before editing.

Rename exactly these permanent scenario IDs and their registration/selection/reference consumers:

| Existing name | Capability name |
|---|---|
| `RECOVERY-ARCH028-PAID-001` | `RECOVERY-PAID-CREDIT-COMPENSATION-001` |
| `RECOVERY-ARCH028-PROMO-001` | `RECOVERY-PROMOTIONAL-CREDIT-COMPENSATION-001` |
| `RECOVERY-ARCH028-PURCHASED-001` | `RECOVERY-PURCHASED-CREDIT-COMPENSATION-001` |

Each remains its original implemented, automated, local-provider **L3 / BLACK_BOX** scenario with unchanged `requiredEvidenceClass`, providers, release gates, fixtures, actions and assertions. Preserve the existing paid/promotional/purchased distinctions and 131026-only claims. The new identifiers are a bijection, not additional scenarios or an opportunity to retire existing rows.

### Reusable commands and deprecation behavior

| Old npm key | New npm key | Exact new command |
|---|---|---|
| `validate:arch002-observability` | `validate:integrated-observability` | `node scripts/run-integrated-observability.js` |
| `validate:arch002-production-readiness` | `validate:production-readiness` | `node scripts/run-production-readiness.js` |

Remove the two old npm keys; add only these two semantic replacements. The existing runner remains authoritative. The semantic Background-persistence commands were supplied by System-Test-001 and are reused unchanged.

The renamed JavaScript tombstone preserves its exact stderr advice: `Deprecated: use ` followed by the existing `npm run validate:render:test` / `scripts/validate-render-deployment.js --environment test` message, and exit 64. The renamed shell tombstone preserves its exact three stderr lines and exit 64, including `./scripts/developer-validation.sh ARCH-002-SYSTEM-TEST-006 -- ./scripts/validate-render-test.sh`. The embedded task ID is valid governance provenance. Snapshot exact bytes in the owned local subprocess test; neither tombstone may execute the suggested command. Preserve their file mode. Do not run live Render validation.

### Enforce names through existing validators

Extend `src/scenario-catalogue.js` to reject architecture-coded permanent `id`, `name` and `title` values and repository-owned `implementation` paths. Keep the existing scenario grammar, domain prefix, required fields, evidence/layer rules and traceability checks. An invalid architecture token must fail even when it matches the broad current scenario-ID grammar.

Extend `scripts/validate-source-structure.js` with a bounded `capabilityNamingViolations` helper invoked by its existing validation entry. Check executable path segments under `src`, `test` and `scripts` for `.js`, `.mjs`, `.cjs`, `.sh`, `.ts`, `.tsx`, `.json`, `.yaml`, `.yml` and `.sql`, plus actual suite keys and npm script keys. Include fixture/configuration filenames, exclude Markdown documents and historical evidence directories, and do not scan JSON/YAML/SQL contents indiscriminately. Reject case-insensitive `ARCH` plus an optional hyphen/underscore and three digits, and task-specific `SYSTEM-TEST-NNN` executable names. Check names rather than all source text. A Markdown document under `scripts/`, a task ID in `sourceRequirements`, a negative guard fixture and an exact protected wire literal are not executable naming violations.

Keep line-budget enforcement restricted to its existing `src/harness` and `test/harness` roots: 300 lines per module/test, 120 per domain index. Do not expand those size limits to existing unrelated large sources merely because the name scanner walks broader roots. No new parser dependency, general AST scanner, runner or validator framework is authorized. The existing `lint` / `validate:structure` and `validate:catalogue` scripts must execute the guard; no optional-only check.

Guard tests must reject an architecture-named file, directory, scenario ID/name/title, suite or npm key; reject the task-coded tombstone filename; accept semantic names and preserved valid governance metadata. Test that adding valid provenance does not change suite membership, and that removing/duplicating a required scenario or executor still fails. Preserve original line-limit boundary tests.

### Preserve provenance and reconcile coverage exactly

Architecture IDs remain valid in `sourceRequirements`, historical `sourceTask` / `sourceFile`, task/worktree routes, evidence metadata and historical notes. Add this task's source requirement to exactly the three renamed legacy scenarios and the nine accepted Background-persistence scenarios. Preserve every existing source-requirement member. Add exactly one symmetric historical-map row with `sourceTask: "ARCH-056-SYSTEM-TEST-002"`, canonical source file `docs/decisions/system-test/ARCH-056/SYSTEM-TEST-002-replace-architecture-based-test-names.md`, definition-baseline `historicalStatus: "pending"` and exactly those twelve permanent scenario IDs. Do not claim this cleanup or another task is Complete before architect acceptance.

No catalogue scenario or executor is added or removed by this task. The capability suite selects the predecessor's explicit `BACKGROUND_PERSISTENCE_SCENARIO_IDS`; it does not select by provenance, implementation status or available executors. Keep the original source requirement and symmetric traceability validation without freezing an exclusive provenance singleton. The final task's additional provenance must not make the nine-scenario suite select twelve rows.

The inspected baseline contains 172 scenarios (69 implemented / 103 planned), with implemented evidence classes 23 CONTRACT / 22 INTEGRATION / 24 BLACK_BOX, and 50 historical mappings. System-Test-001 adds nine implemented scenarios and one historical mapping. With no approved intervening changes, this task therefore preserves 181 scenarios (78 implemented / 103 planned), with 24 CONTRACT / 26 INTEGRATION / 28 BLACK_BOX, and its single new provenance row brings the historical mapping count to 52. Reconcile the existing stale test expectations of 163/54/109 and 9 BLACK_BOX to the **actual accepted predecessor**; never make tests green by deleting membership checks or replacing exact comparison with a loose minimum. Capture before/after membership and metadata under the three-ID bijection, including the allowed provenance addition. If approved intervening work changes totals, identify the exact accepted change and expected membership rather than hardcoding these illustrative totals over it.

### Protected identities and scope limits

Preserve exactly:

- The existing `ARCH002_TEST_*` input variable names and secure bootstrap contract.
- Canonical seeded `arch024-platform-model-availability`, its default references and source-owned fixtures.
- Application `ARCH028_RECOVERY_DELIVERY_FAILED`, `arch028-undelivered:<reservationId>` and `arch028-recovery-delivery-failed:v1:<64hex>` identities and corresponding assertions.
- Database-owned `scripts/validate-arch017-ai-conversations-required.mjs` references; do not add a System-Test alias or rename the external executable.
- The `arch017:<shopId>` advisory lock used by the manual merchant apply/restore pair.
- Truthful `ARCH-028 remains OPEN` / `ARCH-028-SYSTEM-TEST-001 is NOT CERTIFIED` governance warnings and task-route format fixtures.
- All archived run logs, reports, result IDs and acceptance history, including their original names.

These are precise compatibility/provenance values, not permission to exempt an entire architecture prefix or directory from naming checks. Tests continue to exercise real application identities. Do not rewrite an assertion to match an invented replacement protocol.

## Work Items

- [ ] Verify accepted predecessor, collision-free move destinations, exact baseline membership and active-writer preflight; record the two known open-owner handoff requirements.
- [ ] Perform all 24 moves and the exact symbol/scenario/literal/command mapping; update the declared importers and active documentation without changing behavior.
- [ ] Add the bounded naming checks to the existing catalogue and structure validators, with positive/negative cases in their existing tests and unchanged line-limit coverage.
- [ ] Add exact local subprocess assertions for both semantic deprecation tombstones; preserve stderr, exit 64, file mode and their governance advice.
- [ ] Add the twelve-scenario cleanup provenance mapping, reconcile exact accepted catalogue expectations and regenerate the coverage matrix using its existing generator.
- [ ] Record the mapping, compatibility exceptions and current commands in `docs/TEST-NAMING.md`; prepare the exact open-task executable-reference handoff for architect reconciliation.
- [ ] Run the focused/renamed tests, three renamed credit-source scenarios and the entire accepted Background-persistence suite, preserving all 30 cases and 39 mandatory logging assertions.
- [ ] Report actual revisions, commands, outcomes, coverage parity, preserved known baseline failures and unresolved issues; return for architect review.

## Interfaces / Contracts

The new local `capabilityNamingViolations` helper returns bounded structured naming violations and is invoked by the existing structure validator. Reuse its existing root/filesystem test seams and keep the prior line-limit API/return behavior compatible. Export the helper only from that existing module for its owned tests; no application/public API is created.

The exact moved paths, 11 local helper exports, three permanent scenario IDs and two npm aliases above are the changed test interfaces. Update every declared consumer in the same task. No compatibility alias with an architecture-based executable name remains. The 56 literal updates are limited to test-owned synthetic names/labels and cannot alter production or cross-version identities.

The unchanged successor-facing suite contract is:

| Semantic scenario | Class / layer | Required cases |
|---|---|---|
| `REPOSITORY-BACKGROUND-DEPENDENCY-001` | CONTRACT / L1 | D1, D2 |
| `MESSAGING-INBOUND-PERSISTENCE-001` | INTEGRATION / L2 | I1, I2, I3 |
| `RECOVERY-CANDIDATE-PROGRESS-001` | BLACK_BOX / L3 | C1, C2, C3 |
| `RECOVERY-INITIAL-ADMISSION-001` | INTEGRATION / L2 | A1, A2, A3, A4 |
| `RECOVERY-INITIAL-UNCERTAINTY-001` | BLACK_BOX / L3 | U1, U2, U3 |
| `BILLING-INITIAL-OUTREACH-SETTLEMENT-001` | INTEGRATION / L2 | B1, B2, B3, B4, B5, B6 |
| `RECOVERY-INITIAL-FINALIZATION-001` | BLACK_BOX / L3 | F1, F2, F3, F4 |
| `RECOVERY-WOO-INITIAL-GATE-001` | INTEGRATION / L2 | W1, W2 |
| `RECOVERY-FAILED-CANDIDATE-REPAIR-001` | BLACK_BOX / L3 | R1, R2, R3 |

Exactly nine scenarios, 30 case IDs, and the accepted contract's 39 mandatory logging assertions across 16 cases remain required. Preserve actual installed Shared provenance, source-message/component/privacy checks, truthfully held outcomes and the existing non-PASS treatment of missing, blocked, failed, not-run or incomplete cases. This task does not change the evidence classes or application contracts underlying those checks.

## Dependencies

- `ARCH-056-SYSTEM-TEST-001` — must be Complete and architect-accepted; supplies semantic suite/module names, frozen case/logging contracts and accepted executed-source evidence for the five implementation tasks.

This direct dependency is sufficient for the new graph. Prior completed Render/observability/readiness naming-policy baselines are read-only context. Existing ready tasks are subject to the concrete active-writer and architect reference-handoff rule above, not added as unrelated behavioral dependencies. Do not run before the real launcher verifies eligibility.

## Enables

None. This is the final naming rectification and regression verification task for this definition package. It does not enable production rollout or complete other tasks.

## Acceptance Criteria

- [ ] All 24 old executable paths have exactly their declared semantic successors; every moved test/scenario/registration remains present and no old active executable alias survives.
- [ ] All 11 local symbol changes, three scenario-ID changes, 56 scoped literal changes and two npm-key changes are applied with their declared consumers; no application/schema/provider/policy/environment-input behavior changes.
- [ ] Existing validators reject architecture/task-coded permanent naming surfaces and accept valid governance/protocol exceptions; the guard runs through ordinary quality commands and preserves line limits and traceability checks.
- [ ] Both tombstones emit byte-identical stderr and exit 64 from their new paths without invoking any advised live command.
- [ ] Before/after catalogue and executor membership are equivalent under the three-ID map; source metadata gains only the declared symmetric final-task provenance, and existing statuses/evidence classes/gates remain intact. Stale test totals are reconciled to an identified accepted baseline with exact membership assertions retained.
- [ ] Focused naming/catalogue tests, all renamed harness tests and the three renamed credit-source scenarios pass at their original evidence classes. No test is silently skipped, retired or weakened to satisfy the naming guard.
- [ ] The semantic Background-persistence suite passes again with exactly nine scenarios, all 30 cases and all 39 mandatory logging assertions, real emitted records and required cleanup/provenance evidence. A narrowed plan, wrong SHA/package, missing log, BLOCKED or NOT_RUN result is not acceptance.
- [ ] Protected production/seed/advisory-lock values, live-input keys, archived evidence and unfinished terminal warnings remain unchanged.
- [ ] No conflicting active writer remains; the exact two open-owner old/new reference mappings are handed off and reconciled by the architect before cleanup acceptance. The executor has not edited other task lifecycles or Complete review history.
- [ ] `docs/TEST-NAMING.md` and current operator references agree with the actual command/path mapping; the Completion Report distinguishes System-Test naming completion from deferred application names and production-readiness certification.

## Validation

Use the launcher-resolved implementation worktree, existing workspace Node bootstrap and locked dependencies. The two semantic validation aliases are deliverables; they are not commands to execute during this task. No live secrets or remote deployed probe is required.

Before mutation, capture exact accepted catalogue/map/executor membership and focused baseline results for modified existing validator/core tests. After mutation run those same focused tests plus the renamed modules. Any edited readiness/core test must be executed before and after; if it encounters the already reported missing-NGINX defect, record the exact matching failure and its `ARCH-002-SYSTEM-TEST-010` owner. Only a proven unchanged baseline failure may be preserved. A new import/path/selection failure blocks cleanup. Do not edit HAProxy/readiness behavior or omit a modified failing test. Broad `npm test` is not a substitute for the selected checks.

Run these exact commands after the moves:

```sh
npm run validate:catalogue -- --write
npm run validate:catalogue
node --test test/scenario-catalogue.test.js test/render-test-topology.test.js test/observability-validation.test.js test/merchant-scenario.test.js
npm run typecheck
npm run lint
npm run test:harness
npm run system:background-persistence:plan -- --json
npm run system:background-persistence -- --json
MODA_SYSTEM_TEST_BACKGROUND_REF="${MODA_SYSTEM_TEST_BACKGROUND_REF:?set the accepted full Background SHA}" MODA_BACKGROUND_IMAGE= node scripts/run-credit-source-compensation.js --workspace-root "$MODA_WORKSPACE_ROOT"
git diff --check
```

For the credit-source command, set the existing `MODA_SYSTEM_TEST_BACKGROUND_REF` to the verified full accepted Background SHA from the predecessor's provenance before invocation; reject a branch name/short hash. The command clears the optional prebuilt-image override. Record and compare the returned image/source revision and consumed dependencies. The semantic Background-persistence runtime retains its accepted exact-SHA verification. Floating remote `main`, a mismatched prebuilt image or source-only provenance cannot establish the required runtime result. Use the launcher-supplied `MODA_WORKSPACE_ROOT`; do not guess another checkout.

The credit-source runner must still execute exactly the three renamed paid/promotional/purchased cases in separate disposable runs, stop on failure and retain its truthful unfinished-ARCH-028 warning. This proves name/reference preservation of those cases; it does not accept the entire terminal task. All actual runtime setup, stdout/stderr evidence, provider emulation and cleanup remain the existing implementations.

Regenerate the matrix with `--write`, then validate it without write. Confirm the ordinary `test:harness` glob executes the ten moved tests and all five semantic Background-persistence test modules. Naming guard tests require real temporary path/catalogue/script/suite fixtures; runtime proof uses actual accepted services and the existing emulators, not rewritten business models. Do not weaken the predecessor's concurrency barriers, logging checks, safe capture/redaction, source provenance or non-PASS rules.

## Implementation Notes

Use the parent architecture's normal isolation, mirrored task/report publication, original-error/logging and architect-review rules. No Git/worktree/commit/runtime result is claimed by this definition. Do not add a framework or general AST scanner. Preserve the existing source-structure limits without opportunistic refactoring of unrelated large modules. If a required path or accepted interface differs from this contract, return the exact discrepancy before expanding ownership.

### Stop Condition

Complete the scoped mapping, required validation and Completion Report; set only this task to `review`, hand the exact open-owner reference mapping and evidence to `moda_architect`, and stop. Architect reference reconciliation and acceptance remain required. Do not merge, deploy, start another task or self-complete the work.

## Completion Report

This section belongs to the implementing repository agent. No implementation is recorded by this definition.

### Status

Not Started

### Files Changed

Pending implementation.

### Work Completed

Pending implementation.

### Validation Results

Not run. Record exact commands, exit results, failures, warnings, source/build/schema provenance, scenario evidence and cleanup; do not copy planned checks as completed results.

### Deviations

None at definition time. Record actual deviations and their architect disposition before review.

### Assumptions

The reviewed snapshot and accepted prerequisite contracts are the definition baseline. Recheck the real current checkout and task state at launch.

### Unresolved Issues

Pending implementation evidence. Preserve the task's explicit held/deferred and blocked-policy boundaries.

### Architectural Concerns

Return changes to ownership, contracts, schema, transaction boundaries, durable-state semantics, queue behavior, security or another repository to moda_architect before expanding scope.

## Architect Review

This section belongs only to moda_architect. Definition authoring is not implementation acceptance.

### Review Status

Pending

### Review Notes

Awaiting an implementation submission and its evidence.

### Reviewed Files

No implementation submitted.

### Validation Reviewed

No implementation validation submitted.

### Architecture Conformance

Pending review against the parent architecture, task allowlist, interface contracts, repository boundaries and failure requirements.

### Follow-up

Pending implementation review; no enabled task may be started by this task's executor.
