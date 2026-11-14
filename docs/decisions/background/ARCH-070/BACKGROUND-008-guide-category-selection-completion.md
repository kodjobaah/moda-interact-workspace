---
id: ARCH-070-BACKGROUND-008
architecture_id: ARCH-070
title: Correct application category selection completion guidance
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
claimed_at: 2026-11-14T16:47:23Z
attempt: 1
depends_on:
  - ARCH-070-BACKGROUND-007
enables: []
created: 2026-11-14
updated: 2026-11-14
---

# Correct application category selection completion guidance

## Architecture

ARCH-070; docs/architecture/ARCH-070-verified-recommendation-terminal-turn-recovery.md; moda_architect.

## Objective

Improve application category-answer structured selection conformance while preserving canonical admission and diagnosing provider-schema forwarding.

## Context

Genuine16:16 version27 category turn on deployed guidance: one remote productread, modelsteps3. Both initial16:16:36.935 and forcedrepair16:16:40.940 exactonefinalResponse ANSWER/detailsOBJECT with all selection/disposition/shipping fields absent (unknownkeys0), terminalFINAL_PRODUCT_SELECTION_MISSING. Contract8aca437730e539747f45f83a87e8b2aff4562e5c5e921846c53f88c026643788. Unlike prior rawunknown08:20, omission shape now proven. Layout code did not modify runner/model SDK; no causation inferred.

## Scope

Background application guidance/host integration/serialization audit and focused conformance regressions only.

## Out of Scope

Shared source/release, provider/model/budget changes, output argument rewriting, synthesized IDs/automatic selection, new retries, layout edits, main/live operations.

## Requirements

First audit exact app instruction composition and actual provider request serialization: nested finalResponse inputSchema allOf/product selection constraint, strict/tool choice/description forwarded unchanged. Existing runner already requires selection after product reads; do not assume missing schema or prompt rootcause. If actual fix requires Shared mechanism change, stop affected implementation and report concrete gap before new release/task; do not fork adapter or change siblings.

For app-owned correction, map category/catalogue availability/enumeration questions to supported pinned exact observed productDetailSelections where available even when no promotion/purchase recommendation is intended. Explain concrete pinned-compatible details object/identity shape without inventing current IDs, enums or unsupportedcustomfields; preserve discounts/required inspections for true recommendations. Reuse existing verified contract metadata, not copied validator. Existing referral/nonproduct/language/shipping semantics remain exact; no emptydetails bypass. Do not automatically select products or mutate model args, weaken validation, add retries, raise model/token budgets or alter model/provider. Preserve mandatory referrals and irrelevant-result/no-observedproduct behavior. No generic BG007 duplicate-only prompt accepted as diagnosis.

Add actual host request regression for category observations, schema/serialization preserving nested constraints, and final omission still terminalfailclosed after existing repair. Synthetic invalid arguments remain refused, exact returned step identity preserved. Root owns bounded actual configured-provider synthetic comparison using exact candidate instructions in ACTUAL host order (not appended elsewhere), no customer/private prose or WhatsApp sends. Record outcomes honestly: no measured improvement if both already pass, no claim historical failure reproduced without proof. Root alone merges/deploys/drains and asks genuine canary within allowance.

## Work Items

- [x] Audit app guidance and exact serialization forwarding before corrective implementation.
- [x] Implement precise supported category selection semantics if app seam is valid.
- [x] Prove canonical guards/tool access/args/referrals unchanged.
- [x] Record exact isolated source/checks and root model outcome limits.

## Interfaces / Contracts

Published Shared6.0.1 runner/product selection constraint/response schema unchanged; app owns category guidance. Canonical parser/validator authoritative.

## Dependencies

ARCH-070-BACKGROUND-007 Complete/integrated.

## Enables

Root integrated deployment and genuine category/product/media/footer proof.

## Acceptance Criteria

- [x] Actual provider request retains nested selection constraints/strict/toolchoice semantics; concrete gaps reported before scope expansion.
- [x] Category guidance uses only supported pinned fields/exact observed identities, no fabricated fields/automatic selection.
- [x] Missing/invalid/referral/custom/nonproduct cases retain canonical guards and existingrepair/budgets.
- [x] Root configured-provider proof accurately scoped; genuine incident not declared fixed from text assertions alone.

## Validation

- [x] Focused guidance/actualhost/schema serialization tests, declared commerce-host regression.
- [x] Types/build/scopedlint/diff/privacy/exact remoteCI; no unrelated broad local repeats.
- [x] Root bounded actualprovider candidate proof before efficacyclaim; no agent provider/live sends.

## Stop Condition

After work/checks publish exactsource and matching parent report, set review and STOP. Gap requiring Shared returns architect before implementation.

## Implementation Notes

Normal moda-task launcher dedicated siblings/claim. You are not alone; preserve otherwork. Parentbasecurrentmaincc78c608d includes018 integration, no previous taskworktreebase. Root actualcanary allowance constrained; no replay/reset/customerask byagent.

## Completion Report

### Status

Ready for Review. Both exact final-head CI runs passed; implementation and evidence await moda_architect review.

### Files Changed

- `src/commerce/structured-finalization-instructions.ts`
- `tests/unit/commerce/structured-finalization-instructions.test.ts`
- `tests/integration/commerce/host-suites/selection-semantics.ts`

### Work Completed

- Audited real application instruction order and published Shared6.0.1 runner selection constraint. Actual OpenRouter/LangChain HTTP loopback confirms nested `allOf`, dynamic nonempty selection constraint, strict mode, tool description, token limit and ordinary/forced tool choice arrive unchanged. No Shared serialization gap found.
- Added application-only category/catalogue/availability-to-detail-selection guidance, gated by the verified pinned supported identity array and required item shape. Gives bounded exact observed pair binding shape; does not infer recommendations/promotions, fabricate IDs, change language/shipping/referral semantics, or mutate returned arguments.
- Real host regression proves ordinary product read followed by a selected final response and existing independent final product verification. Real SDK double-empty case still reaches terminal `FINAL_PRODUCT_SELECTION_MISSING` after the existing repair, with original empty final argument contents retained.
- Source `dea6f14a8ec7feae4bd43a12260a37db8d2cef34`, draft Background PR231. No dependency, schema, provider, budget, retry, layout, database or live changes.

### Validation Results

- `npm ci`: PASS in canonical implementation worktree.
- `npm run build`: PASS, includes Prisma generation and both TypeScript projects.
- `npx vitest run tests/unit/commerce/structured-finalization-instructions.test.ts`: 11 PASS.
- Actual SDK serializer focused host test: 1 PASS (127 other tests skipped at that checkpoint).
- Final `npm run test:commerce-host`: 129 PASS, 25.66s; includes serializer and category regression.
- Scoped ESLint across all three changed files: PASS, no output. `git diff --check`: PASS.
- Known four unrelated full-lint errors remain outside scope; two affected file blobs exactly equal previously proven baseline `8bff21b8514b4449dd326c1c1dac12a3ba4a8dbf` and `077bcbb76c018428bd5b64c0c82d2a1903b5c6e4`. No matching durable baseline ID exists. No full-lint-green claim.
- Initial new host test failed from a nonexistent fixture receipt property; next run showed successful flow includes two provider reads (model-requested read plus existing independent verification). Corrected test-only assertion to actual receipt semantics; final complete host run green. Runtime guidance did not change for these corrections.
- Root actual configured-provider synthetic proof: both cases PASS on first ordinary finalResponse, pinned contract `8aca437730e539747f45f83a87e8b2aff4562e5c5e921846c53f88c026643788`, DeepSeek `deepseek-v4-flash`, unchanged 2048 token limit. Category question: schema-valid ANSWER, exactly three observed detail pairs, no recommendations, 282 output tokens. Catalogue list: same valid exact three details/no recommendations, 582 tokens. Probe SHA256 `d0a671223e5ce6930b2995cb7fabe0aa0b66dd38a38c915f258ff5bccfa63588`; protected receipt `local-backups/arch075-live-20261113/category-model-probe-20261114.json`. Synthetic DTO validated before model; candidate app guidance in actual host order plus pinned response/dynamic constraint; feature prompts omitted (`[]`), so bounded conformance, not full historical replay or comparative efficacy evidence. Root reports no shopper history, writes, sends or recovery allowance use. Initial harness module-resolution failure occurred before DB/model invocation.
- Exact final-head remote CI `43618834419` / `43618825837`: both SUCCESS, independently confirmed by root at 17:04:25Z.

### Deviations

No broad unrelated local suite or PostgreSQL tests: no persistence/schema change; task explicitly requires focused host/schema checks and remote CI.

### Assumptions

Normal launcher preparation packet supplies canonical paths, branch, claim/dependency and nested database evidence. Parent claim `2b36c9104b0670f3c8b534afb49ba162cf10c03a`; implementation base `8244752ba6dd987eb8873e216b2fec75011ad0f0`; database `6f42b71112efe7ac63654d55f41cd74ca569b1ae`. Both dedicated worktrees use `task/ARCH-070-BACKGROUND-008`; primary and other task changes untouched; no parent gitlink staged.

### Unresolved Issues

The historical model intent/adherence cause is unproven. Root owns synthetic configured-provider results, merges/deployment and genuine category canary; source tests alone do not establish the incident fixed.

### Architectural Concerns

None requiring Shared source/release. SDK forwarding is intact; the current correction is narrowly application-owned semantics.

## Architect Review

### Review Status

Accepted

### Review Notes

Independently inspected exactdea6f14a8ec7feae4bd43a12260a37db8d2cef34 and reportc9b4cbd797b01cc3d077c0f86d1ec6a2068f223c. Shape-gated category/catalogue factual guidance uses supported exact observed detail selections without discount/recommendation authority. Actual SDK HTTP loopback proves nested constraints/strict/description/token/toolchoice forwarded intact; no Shared adapter gap. Empty final arguments still fail after existing single repair. No findings.

### Reviewed Files

All three changed files: app guidance helper, helper tests, actual host category and SDK serialization regressions. Required field/max/canonicalcustom gates and returned argument identity preserved; no output transformation or automatic selection.

### Validation Reviewed

Canonical dedicated launcher/claim/sync/dependency/database evidence; helper11, host129 including actual serializer, build/types/scopedlint, both exactCI43618834419/43618825837success. Root two configured-model firstordinaryfinal conformance PASS: exact3detailpairs/ANSWER/no recommendations,282/582tokens at2048. Probe uses actualhostorder but featureprompts omitted; bounded conformance only, not historical replay/comparative efficacy or incidentreliability guarantee.

### Architecture Conformance

Conforms application-owned category format policy; Shared/model/token/retry/schema/guard unchanged. No invented identities or promotion authority, referral/nonproduct/custom behavior retained. Source task Complete; genuine integrated production verification remains root-owned, architecture InProgress.

### Follow-up

Root source merge/actualparentpin/deploydrain then combined BG019 verified-list fitting and genuine canary. Do not claim prior model intent/rootcause proven solely by conformance or prompt assertions.
