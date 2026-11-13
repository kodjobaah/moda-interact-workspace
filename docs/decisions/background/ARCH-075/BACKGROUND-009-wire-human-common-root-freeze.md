---
id: ARCH-075-BACKGROUND-009
architecture_id: ARCH-075
title: Wire production human common-root preparation
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 5
executor: codex
claimed_at: 2026-11-13T19:49:35Z
attempt: 1
depends_on:
  - ARCH-075-BACKGROUND-002
enables: []
created: 2026-11-13
updated: 2026-11-13
---

# Wire production human common-root preparation

## Architecture

ARCH075; docs/architecture/ARCH-075-ordered-recovery-message-layout.md; coordinator moda_architect.

## Objective

Make the default production human-command adapter freeze an eligible common-layout root before ordered delivery.

## Context

Root actual production common activation revision1 succeeded, approved NoOffer assignments switched. Genuine human command failed multipart_root_not_prepared despite preparedAt and HUMAN revision7, with no outbound root/parts/provider send. Root read-only source inspection found human-command-dispatcher.service.ts defaultDependencies injects multipart.continue without freeze; dispatch prefers that injected adapter and creates an absent root only when engine.freeze exists. Injected complete engines in tests hide the production wiring gap. Earlier human-inactive cancellations were test timing and must not be conflated with this failure. Root will supply protected exact evidence directly; do not repeat live investigation or mutate live state.

## Scope

Background default human dispatcher multipart adapter wiring and directly related meaningful default-runtime and disposable PostgreSQL regressions. Minimal freeze delegation using the existing canonical delivery engine; preserve frozen ordered root/media/footer contracts.

## Out of Scope

Shared/DB/Admin contracts or releases; new engine/framework; live commands/settings/DB writes/provider sends; weakening guards or fabricating roots/parts; replays of cancelled commands; sender pooling; unrelated AI/recovery redesign.

## Requirements

- Default production wiring must expose the existing delivery engine freeze capability as well as continuation, so an eligible prepared human common command can atomically freeze exactly one root then continue its ordered parts. Reuse existing APIs, never duplicate preparation or insert arbitrary rows as workaround.
- Regression must exercise DEFAULT production dependency/adapter construction, not only inject a full engine. Demonstrate current failure before correction, then successful absent-root freeze delegation and correct continuation under real PG ownership/constraint behavior.
- Preserve command lease/CAS/control revision/mode, trusted shop/conversation/checkout common identity, moderation, root admission/dispatch permit, immutable prepared evidence, exact logo/details/body/product/footer ordering and idempotent replay. A root missing because a guard fails must remain fail closed; no provider call before valid root.
- Keep absent/noteligible/unknown/terminal distinctions and bounded retry semantics. Replayed or concurrently claimed commands must not create a second root/part or duplicate provider send. Human-inactive, stale revision, moderation refusal and tampered prepared/common evidence remain negative tests.
- No new durable schema or cross-service contract is expected. Report any concrete dependency gap before widening scope. No generic logger/telemetry duplication; if changed semantic diagnostics are necessary reuse Shared logging.
- Root owns final source/parent merges, deployment verification, and genuinely new human/AI live messages after rollout. Local tests are not proof of live delivery; preserve active root/media/footer controls.

## Work Items

- [x] Confirm root's narrow default-wiring gap and capture failing default-runtime regression.
- [x] Delegate existing freeze capability without bypassing lifecycle/dispatch guards.
- [x] Prove PG first-freeze/continuation/replay and relevant negative behavior; run required checks.
- [x] Publish exact source and mirrored report with launcher/source/evidence provenance, then return review.

## Interfaces / Contracts

Existing Background human command/default adapter and canonical multipart engine; published Shared ordered layout contracts unchanged. Existing Database root/part/dispatch constraints remain authoritative.

## Dependencies

ARCH-075-BACKGROUND-002 architect-accepted Complete.

## Enables

Root-owned deployment and genuine new human common-layout live test, followed by AI mode proof. No automatic follow-on task.

## Acceptance Criteria

- [x] Default production wiring can prepare an eligible absent root and continue using existing engine; failing regression becomes green.
- [x] Real PG tests prove exact one root/part lineage and immutable ordering, no duplicate provider send on replay/concurrency.
- [x] Human/control/moderation/common evidence/lease/dispatch negatives remain enforced.
- [x] Relevant tests/build/scoped lint/diff/privacy and physical worktree preparation evidence pass; no live mutations.

## Validation

- [x] Focused default-runtime RED/GREEN plus existing human/multipart/control/dispatch regression suites.
- [x] Disposable PostgreSQL human/common-root first-freeze, continuation, replay/concurrency and negative guard tests; no hosted DB fallback.
- [x] Relevant declared full tests, production build/typecheck, lint with exact existing baseline disposition if untouched errors persist; no suppressed new failures or unrelated cleanup.
- [x] Exact source diff/privacy, matching branch publication, normal launcher isolation/synchronization/recursive evidence. Exact-head remote checks pending as root merge gate.

## Stop Condition

Set review and return exact source/report after required checks. Do not self-accept, merge, deploy, run live commands or start follow-on work.

## Implementation Notes

Use normal launcher-prepared dedicated parent/implementation task worktrees. You are not alone; preserve others/current main/primary originals. Root's code evidence is a starting point, not permission to bypass a lifecycle gate. Read shared logging convention only if changing runtime structured logging. No source changes outside owning Background scope.

## Completion Report

### Status

Ready for Review

### Files Changed

- `src/services/recovery-conversation/human-command-dispatcher.service.ts`
- `tests/unit/services/recovery-conversation/human-default-multipart-runtime.test.ts`
- `tests/integration/arch075-common-layout.integration.test.ts`
- This task file only in the parent repository.

### Work Completed

- Implementation `0f7e4d4f8c293d4413bb1f0dc3df30fe66ae622d` committed/pushed to `origin/task/ARCH-075-BACKGROUND-009`; draft implementation PR requested. Remote exact-head checks remain root's merge gate.
- Confirmed the actual production factory returned `multipart.continue` without `freeze`. RED default-factory test failed because `freeze` was undefined; GREEN delegates the existing canonical singleton's freeze and continue with unchanged input identities.
- Production change is only the missing lazy freeze delegation beside continuation. No command/lease/control/moderation/source/media/consent/permit/claim/part/usage code changed; no Shared, schema, provider or logging changes.
- Real PostgreSQL regression constructs `createHumanDispatcherDependencies().multipart` and uses the actual canonical runtime singleton, not an injected full engine. Shared's standard runner supplies disposable PostgreSQL/Redis; the existing local WhatsApp emulator supplies actual loopback HTTP and test sender configuration; local moderation model results are durably persisted. A bounded in-memory queue fixture records continuation scheduling; the test explicitly drives delivery status/continuation rather than claiming full worker-fleet coverage.
- Two real PostgreSQL command claim replicas yield one winner. First default-runtime dispatch freezes exactly one deterministic root with ordered HEADER/ANSWER, sends only the header, and waits for DELIVERED before the answer. Concurrent stale command replay/continuation produces no extra send. Root content and part IDs/payloads/digests/source identities remain immutable; each actual HTTP message ends with the exact checkout footer; HUMAN usage remains outside automated usage.
- Six actual default-runtime guard scenarios preserve human-inactive, stale revision, naturally expired five-second SQL lease, controlled moderation BLOCK, tampered prepared plan and stale common source refusal. No provider HTTP occurs for any; stale-common prepared parts are cancelled without a dispatch permit. The tampered input is supplied only by a negative test, never persisted as a workaround.
- Existing common test fixture now includes a legitimate synthetic shop-owned Shopify customer identity and explicitly verifies actual stored-consent preflight ALLOWED. Previous tests used an injected consent reader; canonical runtime correctly refused that incomplete old fixture, so the fixture was repaired without bypassing the consent policy.

### Physical isolation / preparation

- Canonical primary workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-075-BACKGROUND-009`; implementation `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-075-BACKGROUND-009`; both branch `task/ARCH-075-BACKGROUND-009`.
- Deterministic launcher reused the correct parent and created the correct implementation worktree. Parent remote task fast-forward not-needed and origin/main already-current; implementation remote task fast-forward not-needed and origin/main already-current at `8add92e4633fa8c74a819f8fa3dab6e493442028`.
- Recursive database submodule sync/update ready at recorded `6f42b71112efe7ac63654d55f41cd74ca569b1ae`; no remote submodule update.
- Attempt1/executor codex claim committed/pushed `937e31d23f5293831b22d44af995a2b4a827547a`, `2026-11-13T19:49:35Z`.
- No shared/default checkout switched or modified for implementation; no other task worktree reused; no parent gitlink/index/architecture/policy changes. No live DB/provider/settings actions by this task.

### Validation Results

- RED actual default production factory regression:1 failed as expected (`freeze` undefined); no injected complete engine masked the failure.
- Focused unit suites `tests/unit/services/recovery-conversation` and `tests/unit/services/recovery-multipart`:18 files /169 tests PASS.
- Actual disposable PostgreSQL/Redis integration runner across common layout, multipart delivery and human dispatcher:3 files /69 tests PASS, zero skips,97.90s. Includes seven new default-runtime scenarios and existing unknown/replay/partial/control/dispatch coverage. No hosted database fallback.
- Full local test suite:391 files passed,1 skipped;4,295 tests passed,10 existing configured skips;261.94s. Integration files are separately run by the actual PG runner above, not counted as executed in the default unit suite.
- Production `npm run build` PASS: Prisma6.19.3 generation, primary TypeScript compiler, provisioning TypeScript compiler and packaged sample asset. Source remained unchanged after this build.
- Final scoped ESLint across all three owned TypeScript files PASS; `git diff --check` PASS.
- Full `eslint .` FAILED with the same four pre-existing `@typescript-eslint/no-unused-vars` errors in untouched `candidate-index.store.ts` (`readRecoveryExecutionPolicy`) and `recovery-offer-resolver.service.ts` (`MAX_CANDIDATES`, `VERIFICATION_TIMEOUT_MS`, `AI_TIMEOUT_MS`). Exact baseline `8add92e4` file contents piped through ESLint reproduce the same1+3 findings; working-file diff against that baseline is empty. No full-lint-green claim; no unrelated source cleanup.
- Initial PG fixture attempts correctly exposed active-lease mutation refusal and incomplete Shopify identity; replaced them with legal five-second lease expiry and real linked identity. A duplicate same-lease moderation race was replaced with actual concurrent SQL claim winners followed by concurrent replay; no application guard was weakened.
- Protected root-owned evidence logs `local-backups/arch075-live-20261113/bg009-{red,focused,postgres-final,full-tests,build,targeted-lint-final,full-lint,baseline-lint-candidate,baseline-lint-offer}.log`. No production payload/credential/recipient data committed.

### Deviations

Full lint remains limited by the four verified unchanged unrelated baseline findings. Exact-head hosted CI is pending at report publication; root must verify before merge. No extra migration or Shared publication was required.

### Assumptions

Root owns private live evidence and operational rollout; no live test by owner. Local default runtime/real PG/loopback provider verification is not a claim of deployed production delivery.

### Unresolved Issues

Live human and AI delivery proof remains required after source deployment.

### Architectural Concerns

Return genuine cross-owner gaps before expansion.

## Architect Review

### Review Status

Accepted

### Review Notes

Independent exact-source review `0f7e4d4f8c293d4413bb1f0dc3df30fe66ae622d` and mirrored report `87e2564f560b81e9f470129443a09ee6c6cc987d`: only production change delegates freeze to the same existing canonical runtime as continue. Real default dependency factory is exercised; no injection-only blind spot. No findings.

### Reviewed Files

All three production/unit/PG files. Reviewed default adapter, actual singleton runtime/SQL claim paths, corrected legitimate consent fixture and six fail-closed guards; launcher dedicated physical isolation/synchronization/recursive submodule evidence.

### Validation Reviewed

DefaultfactoryRED then focused169/full4295 passed; real disposablePG/Redis/loopbackMeta three suites69tests/zero skips passed including concurrentSQLclaim/replay/DELIVEREDordering/footer and six negatives. Build and scopedlint passed. Four unrelated full-lint findings reproduced at exact unchanged baseline1+3; no full-lintgreen claim. Root must verify exact remoteCI before merge; no redundant rerun.

### Architecture Conformance

Minimal Background wiring only; existing root/part/lease/control/moderation/common receipt/dispatch/billing guards remain. No schema/Shared/newengine/live mutation. Preparation creates one canonical root and continuation uses existing ordering/idempotency; failed guards never send.

### Follow-up

Root verifies CI then merges source/parent, deploys and checks genuine new human delivery. BG010 remains separately gated on accepted publication and reader-first writer gate. Source acceptance is not live human proof or ARCH075 completion.
