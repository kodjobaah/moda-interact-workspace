---
id: ARCH-070-SHARED-007
architecture_id: ARCH-070
title: Preserve ordered native current-turn tool protocol
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 10
executor: codex
claimed_at: 2026-11-14T19:02:15Z
attempt: 1
depends_on: []
enables: []
created: 2026-11-14
updated: 2026-11-14
---

# Preserve ordered native current-turn tool protocol

## Architecture

ARCH-070; docs/architecture/ARCH-070-verified-recommendation-terminal-turn-recovery.md; moda_architect.

## Objective

Preserve ordered native current-turn tool protocol.

## Context

Fullcontext003 reproduced selectionomission; lastoutputfeedback004 negative; losslessschema005 negative; fullcurrentturncontexttrace006 negative despite nonemptytrace (4SDK/3tools,maxdata36045/fullrequest77737). None wiredproduction. Codesource gap: SDK dropsnativecallIDs, runner omitsassistantsteps and emits toolresults as HumanJSON; proper protocol mechanics now authorized, no businessrule change inferred.

## Scope

Implement reusable PURE JSON current-turn transport transcript distinct from runtimeMessages observation/evidence. ModelCall may expose optional native id, SDK must preserve actual bounded provider-issued ID; nativepath refuses missing/malformed/duplicate IDs BEFORE tool I/O (no name/index-derived IDs for providercalls). Explicit native mode may scope requirements for currentcustom/offlineinvokers, but productionconsumer must opt into strictnative path. Do not retain opaque AIMessage/reasoning/provider metadata. Propose exact API/checkpoint promptly, no businessschema/default/layout change.

Transcript assistant{text?,calls[{id,name,arguments}]} and tool{callId,name,payload} ordered records, payload tagged existing validated commerce-result OR bounded runner-feedback(reasonCode/issuePaths). Native SDK maps AIMessage.tool_calls+ToolMessage.tool_call_id preserving exact arguments/text/results; no duplicate HumanJSON runtimeMessages when transcriptpresent. Existinghistory/context/latestcustomer order retained, currentturn trace follows currentobjective. Observation/evidence reducers still consume original canonical runtimeMessages independently.

Append actualassistantstep before routing, exactly one matching terminal toolresult per declaredcall before next model request. Cover denial/INVALID_INPUT/cache(newrequestID)/retry(one terminalresult)/budget-reserved unexecuted remainder/finalResponse validation or missingselectionrepair. Feedback is mechanical not successful commercefacts, never evidence; no extra remote/model retries. Plaintext invalidcompletion stays actualassistanttext. Preserve every businessselection/referral/shipping/currentturnverification/authorization/tenant and deadline/budget/cancellation guard unchanged. Bound tracebytes with failclosed explicitoverflow, no truncation/orphans. Keep Node/LangChain classes only modelNode adapter, purebrowser exports safe.

Test native actualSDKserialization first, runneredges then exactlocalpackedconsumer diagnostic on same reconstructedcontext/seed/read-only bounds. Root alone actualprovider/MCP and privatecaptures. No productiondeployment/publication until acceptedexactarchive/newexplicitapproval+consumerproof.

## Out of Scope

Businessschema/selection/referral/layout/model/token/providerpolicy changes, fakeIDs/facts, new retries, liveagentcalls/mainmerges. No generalunboundedframework.

## Requirements

Implement reusable PURE JSON current-turn transport transcript distinct from runtimeMessages observation/evidence. ModelCall may expose optional native id, SDK must preserve actual bounded provider-issued ID; nativepath refuses missing/malformed/duplicate IDs BEFORE tool I/O (no name/index-derived IDs for providercalls). Explicit native mode may scope requirements for currentcustom/offlineinvokers, but productionconsumer must opt into strictnative path. Do not retain opaque AIMessage/reasoning/provider metadata. Propose exact API/checkpoint promptly, no businessschema/default/layout change.

Transcript assistant{text?,calls[{id,name,arguments}]} and tool{callId,name,payload} ordered records, payload tagged existing validated commerce-result OR bounded runner-feedback(reasonCode/issuePaths). Native SDK maps AIMessage.tool_calls+ToolMessage.tool_call_id preserving exact arguments/text/results; no duplicate HumanJSON runtimeMessages when transcriptpresent. Existinghistory/context/latestcustomer order retained, currentturn trace follows currentobjective. Observation/evidence reducers still consume original canonical runtimeMessages independently.

Append actualassistantstep before routing, exactly one matching terminal toolresult per declaredcall before next model request. Cover denial/INVALID_INPUT/cache(newrequestID)/retry(one terminalresult)/budget-reserved unexecuted remainder/finalResponse validation or missingselectionrepair. Feedback is mechanical not successful commercefacts, never evidence; no extra remote/model retries. Plaintext invalidcompletion stays actualassistanttext. Preserve every businessselection/referral/shipping/currentturnverification/authorization/tenant and deadline/budget/cancellation guard unchanged. Bound tracebytes with failclosed explicitoverflow, no truncation/orphans. Keep Node/LangChain classes only modelNode adapter, purebrowser exports safe.

Test native actualSDKserialization first, runneredges then exactlocalpackedconsumer diagnostic on same reconstructedcontext/seed/read-only bounds. Root alone actualprovider/MCP and privatecaptures. No productiondeployment/publication until acceptedexactarchive/newexplicitapproval+consumerproof.

## Work Items

- [x] Implement owning bounded native protocol; publication remains separate.
- [x] Preserve actual IDs/arguments/results and existing business guards.
- [x] Complete required checks/exactreport.

## Interfaces / Contracts

Contractowner ARCH-070-SHARED-007, published @modainteract/moda-interact-shared commerce/runner and Node model subpath; Background consumes canonicalpackage. PureJSONtranscript separate from business evidence. No persisteddatabase/wirequeue change.

## Dependencies

None; existing runner available.

## Enables

Source007→release008→finalconsumer009; localpackedconsumerproof permitted beforepublicationapproval under architectReadyamendment.

## Acceptance Criteria

- [x] Exactnativeassistant/toolpair semantics and unchangedbusinessguards verified whereowning.
- [x] UnsafeIDs/orphans/overflow/retry/budget boundaries failclosed.
- [x] Actualdiagnostic outcome/limits explicit; no productionfixclaim fromstubtests.
- [x] Requiredchecks and exactimmutablehandoff complete.

## Validation

Focused actualSDKroles/IDs/order+runner batch/cache/denial/invalid/retry/budgetskip/finalrepair/plaintext/cancel/deadline/modelremoteceilings/overflow tests, types/build/installedNode/browserpureboundary/diffprivacy. Exact tested localpack to consumer/root beforepublication. No provider calls byagent.

## Stop Condition

After definedchecks publishmatching source+parentreport, review and STOP. Publicationheldgate remainsInProgress, no inferredapproval. Return architecturegaps ratherthanexpand.

## Implementation Notes

Normal moda-task canonical siblingworktree/claim; notalonepreserveothers. Rootownslive/publicapproval/mainmerge. Inspectrole/policies/declaredscripts. Shopifyingress hotpath unaffected; perconversation ephemeralbounded transcript no globalcache/state. No newgenericlogs/rawcontent; framework/sharedloggingonly.

## Completion Report

### Status

Ready for independent source review with a NEGATIVE actual diagnostic. Local implementation checks passed and root observed correct native frames, but the model still failed required product selection. Source remains a mechanics candidate, not an accepted incident correction. Publication/deployment/public conformance or fix claims are held by root.

### Files Changed

Current source `fea4f4f2486b53004976bdd00493c99e804ad124`, PR https://github.com/kodjobaah/moda-interact-shared/pull/93; initial source checkpoint `f6359576854d12089acb687ab606143f3d47275b` superseded by the approved plaintext-feedback correction.

- `runner/tool-transcript.ts`: JSON-only types, opaque ID and complete pairing validation, canonical observation binding, bounded copied/frozen snapshots, finite mechanical feedback and native data-only formatting. New focused pure protocol tests.
- `runner/types.ts`, `runner/index.ts`, `runner/preflight.ts`: additive explicit native opt-in/types/exports and unsupported-selector refusal.
- Graph state/model/tool/final-validation nodes and `tool-execution.ts`: independent per-turn transport transcript; exact assistant/result/feedback sequence while retaining existing semantic observations, evidence, business decisions and budgets.
- `model/openrouter-model-client.internal.ts`: preserve actual provider IDs, strict native protocol/observation checks and framework-native AIMessage/ToolMessage/SystemMessage serialization; no duplicate HumanJSON results. New actual pinned-SDK offline HTTP serialization tests.
- Existing diagnostics/reason explanations: three finite protocol failure codes, no raw IDs/content or competing logging.
- `runner/runner.test.ts`: native batch/cache/denial/input/retry/reservation/repair/plaintext/cancel/deadline/budget regressions alongside unchanged business tests.
- README and `scripts/validate-native-tool-transcript.mjs`: documented opt-in and exact installed ESM/types/browser/native SDK proof. Task-owned tested-package/bundle receipt beside this task. No dependency/version/consumer code changes.

### Work Completed

- Stable API: `RunCommerceTurnInput.toolProtocol?: "native"`; the runner then always supplies `ModelRequest.toolTranscript`, including `[]` initially. Presence makes SDK transport strict; malformed/undefined native transcript never silently falls back. Unsupported opt-in strings fail before model work. Existing custom/offline invokers can omit the option; production adoption must explicitly opt in through BG009.
- `ModelCall.id?:string` preserves actual provider-issued values. Native mode requires nonblank bounded IDs without controls, max256 characters, unique across the whole current-turn transcript. IDs are never trimmed, generated or derived from names/indexes. Missing/malformed/duplicate native SDK IDs and invalid_tool_calls fail before tools execute.
- Exported pure `CurrentTurnTransportMessage`: assistant `{role,text?,calls:[{id,name,arguments}]}`; tool `{role,callId,name,payload}`; distinct plaintext-repair `CurrentTurnRunnerFeedback` `{role:"runner-feedback",reasonCode,issuePaths?}`. Commerce payloads carry existing validated results. Tool mechanical feedback has finite reservation/final-validation/acceptance codes; plaintext event permits only FINAL_SCHEMA_INVALID or FINAL_PRODUCT_SELECTION_MISSING and only immediately after actual assistant text with no calls. No callId/fake tool call is created.
- Root/architect identified terminal-assistant prefill risk in plaintext repair. Added an offline failing SDK ordering regression first, then the authorized feedback event: exact original assistant text followed by a fixed host-authored SystemMessage. No model/customer/tool content is promoted into that system message. Issue paths must exactly match existing safeRunnerDiagnostic allowlisting (max5, max80 characters, known dot-separated schema parts); raw/unknown/duplicate paths reject. The same initial correction instructions and single repair budget remain unchanged.
- Assistant steps append before routing. Every declared call is paired before another model request, including denials, invalid input, cache using the new requesting ID, one terminal result after existing retry attempts, budget-reserved unexecuted batch remainder and finalResponse-call repair. Fatal cancellation/deadline/budget failures stop further I/O rather than transmitting incomplete pairs. Plaintext repair feedback never becomes commerce evidence.
- Native adapter creates only framework AIMessage.tool_calls, ToolMessage.tool_call_id and fixed SystemMessage feedback. Historical user/assistant dialogue, trusted context and separate latest customer objective keep their existing order; current-turn transcript follows. Current customer wording occurs exactly once per request, never synthesized from history. Original tool-result data-only prefix and canonical `{tool,result}` bytes remain; no duplicate Human tool JSON is sent.
- `runtimeMessages`/request.messages remain the original observation/evidence representation. Ordered commerce-result trace payloads must exactly match those semantic messages; empty/mismatched trace cannot discard or replace evidence. Feedback events are excluded from semantic observations. All product/shipping selection, referral, authorization, tenant, evidence and final-response business guards remain unchanged.
- Technical bound: 1MiB canonical transcript, max4096 records,32 calls/assistant step, bounded JSON nesting/node traversal and pre-serialization lower-bound checks. Overflow is explicit with no truncation/orphan repair. Snapshots copy/freeze data; no opaque SDK objects, provider reasoning/metadata, durable state, shared cache or extra model/provider retries.

### Validation Results

- Canonical isolated dependency install `npm ci --ignore-scripts --no-audit --no-fund`: PASS, no lock/dependency changes.
- Actual pinned ChatOpenRouter offline HTTP-intercept serialization tests: PASS, including native assistant/tool IDs/roles, unchanged chronology/latest objective, no human duplication, strict missing/duplicate/orphan refusal, observation binding, exact plaintext→fixed System feedback and forced final tool choice. No external API calls.
- Updated focused runner/protocol/selection/diagnostic set: PASS135/135. `npm run typecheck`: PASS. `npm run build`: ESM/DTS PASS. Full `npm test`: PASS818,3 configured skips (821 total), no failures. The earlier superseded no-plaintext-event candidate had a separate816-pass baseline; final counts above are for current source.
- Exact immutable local candidate `/tmp/ARCH-070-SHARED-007/native-provisional-800059e55690.tgz`, unchanged metadata6.0.1 for unpublished local testing:975475 bytes, unpacked3369956 bytes,163 files; SHA256 `800059e55690d6c27e8233fad8a6d6dd5ee9a09f5d4f9a6fcbe553c1d6fa31a0`; npm SHA1 `fbfab19b30ec29d56451be639002b76d61f6d16c`; SRI `sha512-TukApaBsw1nBHyJjxdcnd6zy2gWgNYySn/Km+b/uXlV2Fajsf10azUpZCQUDAXGtcIVc9U2XZ4pamPL6kpY02w==`. Member-manifest SHA256 `c22ab8f44766c5a5dcfde33430a7275437fbe105714b3331b8d2b9d0c345f555`.
- `node scripts/validate-native-tool-transcript.mjs <exact candidate>`: PASS installed native SDK serialization/actual IDs/chronology/semantic binding/plaintext system feedback, installed TypeScript API and browser-pure model bundle/VM boundary. No LangChain/Node/Sharp/AWS/Prisma/logging/observability import enters the pure model entrypoint. SDK classes remain in Node adapter.
- Root requested a small diagnostic bundle from the exact unpacked archive. Supplied `/tmp/ARCH-070-SHARED-007/diagnostic-800059e55690/native-candidate-800059e55690.node22.mjs`:140062 bytes, SHA256 `61b7a246a8e5297b6d9e5869cdb3acbe0526124a40e3c7fb4f261ac8c3f0b8e6`; gzip41599 bytes, SHA256 `a7c51a51863e26db5e440630482e4f823ef1db2a661a3e0ebe3489efcaa4d133`. Node22 target, packages external; only runCommerceTurn/OpenRouterModelClient exports, no renderer assets/maps/declarations. Public-code-only archive provenance/metafile/receipt accompany it. Root must inject candidate runner AND candidate SDK through deployed createProductionCommerceModelInvoker.createClient; old runner cannot construct new trace. No provider calls by this agent.
- Candidate8be07c and its bundle are explicitly superseded; root confirmed it would not execute them. All current hashes above refer to the plaintext-feedback-corrected source. No build/version/publication change after current artifact creation.
- Privacy/member scan: no actual shop/customer assets/header files/backups/.env/.npmrc; no provider credentials in fixtures/artifact/report. `git diff --check`: PASS. No declared lint script exists; no invented lint/doctor/bootstrap tooling added.
- Prepared isolation: canonical primary `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent `moda-interact-workspace-task-ARCH-070-SHARED-007` reused; implementation `moda-interact-workspace.worktrees/ARCH-070-SHARED-007` created; both mirrored `task/ARCH-070-SHARED-007`. Parent initial `af161684fa7fcf937a34db0d76b0d3318882f114`, implementation initial `4c736db2422a2001d0f3634403734f85a75626c0`. Remote task fast-forward not-needed/origin-main already-current both; recursive sync/update passed/ready/no submodule entries. Durable claim `49bad6cd3bb5c02a4fd9c56c29c5a4861b671233`, codex/attempt1 at2026-11-14T19:02:15Z. No shared checkout/main/gitlink/other-task edits.

### Actual root diagnostic outcome

Root relayed natural native trial007 as NEGATIVE: 7 actual SDK calls,5 tool calls,10 observed pairs; native frames were all valid (first transcript empty, actual issued IDs and correlated pairs thereafter). The final output was ANSWER / STANDARD with zero selections, rejected by the unchanged FINAL_PRODUCT_SELECTION_MISSING guard. No synthetic seed/native ID was used. Root reports no outbound or database host writes. Archive800059 and bundle61b7 provenance matched; final output SHA256 `e20baafb3dc0b5bc3983ec65c99eb7cc66199c546aeecd9cfe33d4eb7b986db8`.

This is evidence that native protocol framing was delivered on this bounded trial; it did not cure the incident or establish product-selection/provider conformance. All raw captures remain private/root-owned and are not committed. Root explicitly stopped publication/deployment/fix claims and further optional code/probes/prompt/business-rule changes pending architectural disposition. No new calls or source edits were performed after that result. The exact source/archive/bundle remain unchanged.

### Deviations

Root/architect explicitly authorized the bounded third transcript event for actual plaintext validation repair after observing that exact assistant-last replay can be interpreted as prefill by some providers. It adds truthful mechanical feedback only, without business rule, retry, fake ID or fake customer content. No compatibility fallback is added to the native path. TypeScript helper narrowing/update annotations were corrected before final green checks; no unresolved baseline failure.

### Assumptions

Root alone performs actual provider/MCP diagnostic and private captures. First trial uses natural actual SDK output and actual IDs; any controlled first discovery requires separate root-authorized diagnostic labeling, not a general production forced-search API. BG009 owns production explicit native opt-in. Accepted source then separate008 release requires exact tested archive and NEW explicit public approval; no publication in this task.

### Unresolved Issues

Actual trial remains selection-invalid despite valid native frames and nonempty observations. Incident correction is unresolved; root/architect are evaluating actual schema/provider behavior versus application category grounding. No implementation/check failure is concealed, and no business validator was weakened. Publication/deployment remains held; no further code/probe change is inferred.

### Architectural Concerns

Native transport correctness must not weaken business validators to obtain an answer. The genuine unseeded trial produced continued selection rejection; therefore no provider-conformance, incident-fix or publication decision follows from this source review. No fabricated seed/native ID, semantic evidence promotion, raw reasoning replay or new retry is authorized.

## Architect Review

### Review Status

Pending

### Review Notes

Pending actualimplementation

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

Root actualintegratedverification

## Plaintext validation-repair transport clarification

Architect authorizes bounded third transcript row role runner-feedback ONLY when actualplainassistant output triggers existingvalidationrepair. It has no callId, finite existingvalidator reasonCode and bounded issuePaths only. NodeSDK maps it to FIXED SystemMessage validatorstatus after exactactualassistanttext before forcedfinal; neverpromote model/tool/customer/rawpayload content tosystem, no fakeassistanttoolcall/ID/prefill. Existinginitialinstructions/singlerepair/budgets/businessguards unchanged. Exact offlineSDK order/negative injection tests required. Rootactualendpointconformance still required.
