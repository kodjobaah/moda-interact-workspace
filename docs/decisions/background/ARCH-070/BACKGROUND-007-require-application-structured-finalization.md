---
id: ARCH-070-BACKGROUND-007
architecture_id: ARCH-070
title: Require application structured finalization using pinned response fields
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
claimed_at: 2026-11-14T09:18:12Z
attempt: 1
depends_on:
  - ARCH-070-BACKGROUND-006
enables: []
created: 2026-11-14
updated: 2026-11-14
---

# Require application structured finalization using pinned response fields

## Architecture

ARCH-070; docs/architecture/ARCH-070-verified-recommendation-terminal-turn-recovery.md; moda_architect.

## Objective

Make recovery application finalization guidance consistently request the existing finalResponse envelope and supported pinned selection fields without altering model outputs or semantic admission.

## Context

Diagnostic BG006 is integrated at Background be077bf7bd6b5e7f5a91fad1ee84c75dc76e13fa and parent6191af7439674d3edec1fa78d9b986144a3b9790. Genuine09:08:47 turn succeeded: ordinary step3 plain text required existing repair, then forcedstep4 supplied one detail selection; one composite was delivered. Original08:20 forcedstep4 omission remains unexplained. This corrects observed routine raw-text completion friction, not a proven original failure cause. Root causal audit found Shared runner/model/response/selection files byte-unchanged between5.13.10 release44356b4 and6.0.0 ade292b; Background host/product-discovery unchanged across composite adoption. Layout changes did not change those selection sources.

## Scope

Background-owned trusted host instructions and a small pinned-schema-aware format guidance helper if needed; focused actual-host request/unchanged-semantic tests and documentation of evidence limits.

## Out of Scope

Shared edits/releases; model/provider/schema changes; fabricated IDs or automatic selections; argument mutation; new retries or higher budgets; layout/media changes; live operations or main merges.

## Requirements

- Recovery trusted instructions require customer-facing completion through existing finalResponse, including simple answers/clarifications. Ordinary tool access and current forced-repair mechanism remain unchanged; do not force finalResponse at initial request.
- Derive any concrete field guidance only from the verified pinned response contract. Explain exact observed product/variant identities for supported nonempty detail/option/recommendation fields; never invent enum values or canonical fields absent from a custom contract.
- Preserve referral, language, nonproduct and custom contract behavior. Nonproduct completion must not invent products/evidence. Pinned schema validation and existing terminal missing-selection guard remain authoritative.
- No logs containing prose, identifiers or private contract contents beyond already approved bounded diagnostics.
- Root performs a bounded synthetic unforced actual-production-model baseline versus explicit-guidance comparison, without customer input or WhatsApp sends. Record actual outcomes before claiming measured benefit. Unit guidance assertions alone do not prove model efficacy; original forced omission remains unknown.
- No infrastructure, database or observability capability changes are needed.

## Work Items

- [x] Add bounded application finalization guidance through existing trusted instruction assembly.
- [x] Add pinned-contract-aware field guidance where supported without copying validators.
- [x] Prove host/tool/semantic constraints unchanged through focused tests.
- [x] Record exact source, isolation and validation plus measured/unknown evidence distinction.

## Interfaces / Contracts

Consume published Shared6.0.0 runner/verified response contracts as-is. Background owns recovery format policy; Shared generic plain-text allowance remains unchanged. Existing finalResponse and selection schemas remain canonical.

## Dependencies

ARCH-070-BACKGROUND-006 Complete, accepted and integrated.

## Enables

None; root-owned deployment and genuine verification follow accepted integration.

## Acceptance Criteria

- [x] Actual host request includes specific recovery structured-finalization guidance while ordinary tools remain available.
- [x] Supported canonical selection fields receive accurate guidance; custom unsupported fields/enums are not invented.
- [x] Referral/nonproduct/language envelopes and model args remain unchanged by host processing.
- [x] Missing/invalid selections still fail closed with existing single repair and budgets.
- [x] Root comparison evidence is recorded honestly; no assertion of original forced-step failure cause.

## Validation

- [x] Inspect declared package scripts and run focused instruction/helper tests plus declared commerce-host suite.
- [x] Typecheck, production build, scoped lint and diff hygiene.
- [x] Exact-head configured remote CI passes; disclose known unchanged lint baseline with evidence.
- [x] Record root-owned bounded provider comparison outcome; no agent live calls.

## Stop Condition

After required work/checks, publish implementation and mirrored parent report, set review and STOP. Root owns all merges/live actions.

## Implementation Notes

Use normal moda-task launcher from primary root, dedicated sibling parent/implementation worktrees and preparation packet. You are not alone; preserve all other edits. Existing Background owner may inspect prior diagnostics but must use this task's worktrees. Prefer concise trusted instructions over a new adapter or policy framework. Root probe may run alongside implementation after exact proposed instruction is available; no efficacy claim ahead of result.

## Completion Report

### Status

Ready for Review. Source, exact checks and root-owned bounded comparison evidence complete.

### Files Changed

- `src/commerce/structured-finalization-instructions.ts`: Background-owned universal finalResponse completion guidance and pinned-schema-aware product detail/options/recommendation hints.
- `src/commerce/host.ts`: derives guidance from `verifyResponseContract` and inserts it into existing trusted host instructions; no model-call adapter or argument transformation.
- `tests/unit/commerce/structured-finalization-instructions.test.ts`: supported identity arrays, custom unsupported fields/types/capacity, incompatible version enum, actual positive recommendation hint, immutable contract content and nonproduct/referral constraints.
- `tests/integration/commerce/host-suites/instruction-composition.ts`: actual request contains helper output, remains initially unforced and retains ordinary tools; original finalResponse bytes and referral preserved.

### Work Completed

Implementation `c0292c5d60754b864967ec8ec1ced47236625a9e` pushed on `task/ARCH-070-BACKGROUND-007`, draft PR https://github.com/kodjobaah/moda-interact-background/pull/226. Every customer-facing completion is instructed to use the existing finalResponse, including simple answers, clarifications and referrals. Product detail/options hints require pinned array/object/string identity shape with nonzero capacity. Recommendation hints additionally require actual pinned version string enum support for1, beyond Shared's presence-only canonical contract predicate. No hints for unsupported custom fields/enums. Guidance is format policy, not a copied validator; Shared pinned validation remains authoritative. Initial tools/requiredToolName, response objects, referral/language handling, budgets and single repair remain unchanged. No Shared/publication/layout/provider/DB/logging changes.

### Validation Results

- Normal canonical prepared launcher: primary `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-070-BACKGROUND-007`; implementation `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-070-BACKGROUND-007`; matching mirrored task branches. Attempt1/codex claimed2026-11-14T09:18:12Z, parent claimdb6fe8e665099b36886fe7cc020e3824dd21be52 pushed; synchronized parentd7b1ba0d488208f1f2405a66be7a154c988e4a68/sourcebe077bf7bd6b5e7f5a91fad1ee84c75dc76e13fa. BG006 dependency complete, database submodule6f42b71112efe7ac63654d55f41cd74ca569b1ae ready. No primary/other-task edits.
- `npm ci`, `npm run build`: PASS.
- Focused `npx vitest run tests/unit/commerce/structured-finalization-instructions.test.ts tests/unit/commerce/final-selection-shape.test.ts tests/unit/commerce/model-bridge-diagnostics.test.ts`:31PASS/3files.
- Declared `npm run test:commerce-host`:127PASS, including existing language/referral/evidence/successful product and exact missing-selection terminal/refusal/repair/argument-identity paths plus the new actual request assembly test.
- `npx tsc --noEmit` and scoped ESLint on all4 changed files: PASS. Full `npm run lint` has exactly4 unchanged `@typescript-eslint/no-unused-vars` errors: candidate-index.store.ts:9 readRecoveryExecutionPolicy; recovery-offer-resolver.service.ts:23-25 MAX_CANDIDATES,VERIFICATION_TIMEOUT_MS,AI_TIMEOUT_MS. Both files are byte-identical at startingbe077bf, currentc0292c5 and prior3e46120 whose stdin baseline was proven in BG006; exact blobs8bff21b8514b4449dd326c1c1dac12a3ba4a8dbf /077bcbb76c018428bd5b64c0c82d2a1903b5c6e4. No new failure or unrelated cleanup; no full-lint-green claim. Exact-head CI [43580528735](https://github.com/kodjobaah/moda-interact-background/actions/runs/43580528735) and [43580502290](https://github.com/kodjobaah/moda-interact-background/actions/runs/43580502290): both SUCCESS. Relevant local logs retained privately in primary `local-backups/arch070-bg007-*`. Parent checkpointe85d08017 and draftPR https://github.com/kodjobaah/moda-interact-workspace/pull/1040 published; no gitlink staged.
- `git diff --check` PASS; bounded diff/private-content review found no customer payload/provider credentials/prose or logging changes. This task performs no model/provider/Meta/DB live calls and requires no migration/PG changes.
- Root-owned bounded actual-provider comparison: both unforced baseline and candidate returned exactly1 finalResponse, ANSWER, pinned-schema valid, productDetailSelections count1, recommendation count0; output tokens252baseline/265candidate. Same production DeepSeekV4Flash model, max800tokens/60s; candidate strings matched this actual built helper. Both succeeded, so NO measured efficacy gain or historical-failure reproduction is demonstrated. Important fidelity limit: probe appended candidate hints after response instructions, while the actual host places them before PRODUCT_DISCOVERY/response instructions via hostInstructions. This is a compatibility-only result, not a controlled proof of actual-host efficacy. Root's protected receipt is primary `local-backups/arch075-live-20261113/bg007-unforced-model-comparison.json`; root reports staged checksum failures occurred before any provider calls, then only the final verified pair ran. No WhatsApp sends. The repository agent made no live calls. Root relayed these actual outcomes after source/tests freeze.

### Deviations

No source-scope deviation. Root review caught presence-only recommendation predicate insufficiency before source freeze: added actual pinned types/enum support and negative custom-contract tests. No schema/validator weakening.

### Assumptions

Root owns bounded synthetic model comparison, integration, deployment and genuine production verification. This agent performs no live operations.

### Unresolved Issues

The original08:20 forced-step omission remains unexplained. The target is observed09:08 ordinary plaintext completion requiring existing repair; this does not attribute the original failure to layout/template changes or prove model reliability.

### Architectural Concerns

No Shared schema/package, retries/budgets, generated selections or new adapter. Final admission remains existing pinned contract and runner guard. Actual comparison and exact remote checks are recorded above; compatibility only, not an efficacy or production-delivery claim.

## Architect Review

### Review Status

Accepted

### Review Notes

Independently inspected exact implementation c0292c5d60754b864967ec8ec1ced47236625a9e and immutable parent report f1403192a528e757732cbb2f9bc8a7f75653e960. Accepted solely as application completion-format consistency: two observed product turns initially returned plaintext despite recovery requiring structured composition; the application now states its existing envelope requirement explicitly. This is a defensible instruction correction without claiming measured improvement. BOTH synthetic baseline and candidate already passed; no causal or efficacy inference is made, and differing probe hint order limits fidelity. Original forced-step omission remains unexplained. Architecture remains In Progress pending root integration/deployment/genuine evidence.

### Reviewed Files

All four changed files: host.ts, structured-finalization-instructions.ts, unit helper tests and actual host instruction-composition integration test. Verified pinned-contract verification occurs before guidance, shape/version gates avoid unsupported custom-field instructions, ordinary tools remain unforced and returned objects/referrals stay unchanged.

### Validation Reviewed

Canonical launcher packet/isolation/synchronization and recursive database evidence in report; focused31, host127, types/build/scoped lint, exact-head CI43580528735/43580502290 SUCCESS (root verified4385 tests/394 files). Four unrelated full-lint errors disclosed with unchanged blob identities; no broad repeats required. Root bounded two-call result compatibility-only: both valid detail1,252/265 tokens, no historical reproduction. No live operations by repository agent.

### Architecture Conformance

Conforms to bounded Background-owned application policy. Shared mechanics/contracts unchanged; no output transformation, fabricated identities, new retries, budget changes, schema relaxation, infrastructure or database change. No claim that historical intermittent failure is fixed. Automatic completion applies to this bounded instruction task only.

### Follow-up

Root owns source merge, actual parent gitlink integration, deployment/drain and genuine postchange trace. Preserve diagnostics and original unresolved omission explicitly; no extra model calls merely to seek a preferred comparative result.
