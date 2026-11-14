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
status: in_progress
priority: 10
executor: codex
claimed_at: 2026-11-14T17:36:21Z
attempt: 2
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

## Historical Architect Review — accepted attempt1

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

## Developer Integration

Root sourcePR231 merged17:06:56Z actualBackgroundmain2bfc7074a7cd2808f65994d301d52649948cf8d5. Independently fetched exactorigin/main/treeequal revieweddea6f14. Parent currentmain already current, actual merged gitlink recorded. Root alone parentmerge/deploy/genuineverification; BG019 must sync this acceptedmain before finalchecks.

## Reopened attempt2 — full-context conformance diagnosis

User/root explicitly reopens after genuinev28 on2352 deployedsource failed. Category/searchOK, INVALID_INPUT nextsearch, newsearchOK, plaintext then forcedfinalANSWER/detailsSTANDARD with allselectionarrays absent. Earlier bounded[]feature syntheticprobe did not reproduce fullhistory. Prior accepted attempt/source/checks remain valid historical evidence, not proof currentincidentresolved. BG019 independentvalid.

Current scope ONLY isolated protected conformance harness and diagnosis; NO furtherpromptchange, schema/Sharedmechanicalfix without evidence/disposition. Use actualpublishedmanifest full ordered featureBehaviours/responseinstructions+apphostguidance, exactsupportedmodelconfig/SDK, boundedexistinghistory/context/currentinput/toolresultsequence and currentselectionconstraint. Do not reconstruct missing historicalrawrequests as exact; label source-derived reconstruction vs capturedexactbytes. Root supplies protected input and executes actualprovider/read-onlyMCP only; repositoryagent writes harness+syntheticguardtests, no livecalls/secrets.

Harness must bypass productionhostexecution/DBwrites/inbound/usage/quota/outbound/Meta. Use actualSharedrunner with isolateddependencies; default offline capturedtoolresults, optional root-only explicitly allowlisted read-onlyMCP under existinggrant and boundedtool/model/deadline/token limits. No discountcreate/apply/cart/order mutations or networkunknown tools. Never invoke productionconversation processor/send/finalpermit. All exactrequests/toolresults/outputs private0600 file under operator-provided protecteddirectory, no stdout rawhistory/prompts/IDs/URLs/credentials/genericlogs. Public output aggregate shapes/reasoncodes/digests only. No hosted diagnostic deployment.

Root bounded actualrun must preserve full instructionorder/features/history and independent canonicalfinalvalidation. Capture model requests and outputs privately sufficient to distinguish prompt conflict vs ignored nestedschema; no repeatedcalls merely chasingpreferredresult. On finding, return concrete minimalmechanical/appownership recommendation with actualproof and tests; do not implement guessedcorrectiveprompt/Sharedrelease within this rework.

### Attempt2 Work Items / Validation

- [ ] Implement isolated safe input/output/callallowlist/budget harness using actualrunner/SDK.
- [ ] Synthetic tests prove no unsafe tools/writes/sends/rawstdout and exactfullcontextorder forwarded, originalreturnedargs unchanged.
- [ ] Types/scopedlint/relevantbuild and diffprivacy pass; exactheadCI whereconfigured.
- [ ] Root actualfullcontextdiagnostic result recorded privately with honest reconstructionlimits.
- [ ] Return diagnosis+minimalowningcorrection contract to architect; incident remains InProgress.

## Attempt2 Completion Report

### Status

Implementation and local validation complete; awaiting root full-context diagnostic result and exact-head remote CI before review submission.

### Changes Requested correction checklist

- Implemented: isolated published-runner harness with complete supplied manifest/app instructions/context/history/current input, default offline captured model/tool receipts, no production host/database/processor/persistence/delivery imports (`src/commerce/diagnostics/context-probe.ts`).
- Implemented: explicit operator gate for root-only injected configured model/read-only MCP, fixed 12/6/60000/2048 limits, safe read-tool allowlist, exact pinned grant/descriptor/version matching and exact captured argument replay.
- Implemented: original request/output capture in fresh 0700 directory and exclusive 0600 artifacts, original model arguments unchanged, only safe shape/count/digest result exposed. Existing shared logger with private sink; no competing generic logger or public raw output.
- Implemented: deployed evidence extractor callback passed unchanged to runner tools. Search/get/category/shipping do not normally produce discount evidence; retain the callback anyway. Host post-model ineligible-evidence rewrite and delivery revalidation are explicitly outside this isolated runner; no delivery equivalence claimed.
- Implemented: synthetic guards for full context and ordered feature forwarding/private permissions/no stdout, default no model/network, explicit operator gating, unsafe descriptors/wrong tenant, unsafe model-requested create operation never dispatched, fixed budgets, exact read replay/refusal and original invalid model output preserved/canonical refusal.
- Pending root evidence: actual configured model/MCP execution and causal/owning-correction disposition. No further prompt, schema, Shared release or production behavior changes were implemented.

### Source and validation

- Source `5bbbca7a99f15c14f8a4be607549ab922d74ee3d`, draft Background PR233. Owned files: harness, `tests/unit/commerce/context-probe.test.ts`, `docs/diagnostics/commerce-context-probe.md`.
- Final focused guard suite: 7 PASS, 2.15s. Repository build passed initial harness; final evidence-callback delta passed `tsc --noEmit`, scoped ESLint and exact Node22 operator bundle build; diff check PASS. No unchanged broad local suite repeated.
- Initial synthetic fixture used invalid language source `shop`; corrected to published `shopify`. Extractor fixture initially lacked canonical get-product payload and correctly failed before extraction; corrected to `{product:null}`, preserving all canonical validation. These were fixture corrections, not source guard weakening.
- Exact Node22-compatible operator bundle `/tmp/arch070-context-probe.mjs` SHA256 `eaa5037c0a7e89bc479f31e58982c79f6b6e46a849f82a5e437c7053febc2cee`; published Shared dependency remains external. This is a local diagnostic artifact, not a hosted deployment or package release.
- Exact source CI `43623474142` and `43623467171`: both SUCCESS at exact source `5bbbca7a99f15c14f8a4be607549ab922d74ee3d`.

### Isolation and limitations

Normal attempt2 claim `1dfb8257de7f8f4fabb522cd0c23540c675b054e`; canonical mirrored task branches/worktrees reused and main synchronized by launcher. No primary/other task files or parent gitlink staged. No provider or live MCP calls made by repository agent.

Root snapshot uses actual moderation-aware production history/context readers and ordered pinned manifest, explicitly CURRENT_RECONSTRUCTION because the original processing boundary/request bytes were not retained. Exact ModelRequest and ModelStep artifacts are protected; they are not raw provider HTTP/reasoning captures. Injected operator adapters must retain production authorization and redirect their own transport output privately. Diagnostic success alone cannot prove the genuine incident fixed.


## Architect Review

### Review Status

Changes Requested

### Review Notes

PriorAccepted0ecba05d5 retained above as historical boundedguidance acceptance. Genuinev28 disproves sufficiency forfullcontext. Reopen SAMEtask statusReady, executor/claimed cleared, acceptedattempt1 preserved; launcher increments exactlyonce. Execute this diagnosiscontract before any additionalbusinesssourcefix. No needcodechurn to reinterpret earliervalidtests.

### Reviewed Files

Newprivatepastedlogs root-supplied; existingfullcontextinstructionassembly and modelbridge audit.

### Validation Reviewed

Earlierprobe excludedfeatures/history; newactualfailure arraysabsent bothfinals. No furthercausalclaim justified.

### Architecture Conformance

Currentevidence requires diagnosis first; Sharedmechanicalgap only if reproduced/confirmed, no releaseinferred.

### Follow-up

Root executes privateboundedactualrun; architect determines correctionowner/task from actualevidence. Do not markincidentfixed from harnessstub or newprompt assertions.

### Authorized bounded diagnostic phase002

Probe001 used current reconstruction and returned only category resolver outcomes, no current product observations; runnerok/plaintext was not selection conformance or delivery proof. Root may execute one further bounded diagnostic with explicit artificial initial read-only product DISCOVERY browse {browse:true,query:null,availableOnly:true,limit:5,cursor:null}, actual authorized fresh MCP result then actualproduction SDK/fullcontext. It chooses no product IDs/selections. Same12/6/60s/2048 budgets/private0600 capture/no productionwrites/sends. Label seeded discovery vs historical replay. Capture whether productcondition/repair occurs and exact private prioroutput/request. No app/Sharedrepairfeedback implementation inferred. Candidate invocation-local previous-output feedback must remain lowertrust data, never trustedinstruction/toolresult spoofing, and requires concrete evidence/disposition before source change.

### Authorized phase003 feedback counterfactual — diagnostic only

Corrected seeded-discovery probe003 reproduced FINAL_PRODUCT_SELECTION_MISSING with actual product observations (4actualSDKcalls+1seed/6readMCP), forcedANSWER omitted allselectionfields. Prior002 text:null setup rejected before SDK/MCP, retained separately. No historical replay claim. Root may run ONEactualSDK counterfactual using SAME captured forcedrequest5 plus immediateprior rawModelStep4, zeroMCP, unchanged2048/tools/schema/order/objective.

Agent may implement pure app helper+guardtests/bundle for this diagnostic, NOT productionhostwiring. Only requiredToolName finalResponse permits bounded exact priorcalls/text as explicitly UNTRUSTED DATA in reserved contextkey; preserve originalcontext fields, refuse keycollision/nonobject/unsupportedinput and omitwhole if bytes exceed boundedfeedback or remaining canonicalcontext/history/currentmessages131072. No truncation, reasoning/providertransportmetadata, trustedinstruction elevation, fake toolresult, argsmutation, generatedIDs or newretry. Root private0600 execution+capture; productionwiring requires separate explicit disposition after actualcounterfactual outcome.
