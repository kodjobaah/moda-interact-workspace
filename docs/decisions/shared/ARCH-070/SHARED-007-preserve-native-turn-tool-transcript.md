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
status: ready
priority: 10
executor: null
claimed_at: null
attempt: 3
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

### Attempt 3 — optional transport parameter correction

Ready for Review. All bounded attempt3 source checks passed. Source `667a658915f4071835a966c345e5fe76feda0829`, existing PR https://github.com/kodjobaah/moda-interact-shared/pull/93. Production correction is the deletion of unconditional `parallel_tool_calls: false` in `model/openrouter-model-client.internal.ts`; no replacement provider capability policy or synthetic sequential semantics. Actual SDK HTTP regressions and old configuration expectation updated; installed proof checks omission too.

Latest Changes Requested items:

- Implemented: default HTTP request omits the optional parameter. Actual SDK assertions preserve exact schemas/strict, auto/named/required tool choice and `max_tokens`.
- Implemented: native batches, remote/model ceilings, budget-reserved unexecuted pairing, retry, actual IDs and result pairing remain unchanged and pass affected tests.
- Implemented: terminal projection, required referral, invalid decisions, cancellation/deadline and canonical guards remain unchanged and pass affected tests.
- Implemented: types/build and focused affected model/runner checks PASS (208 tests). No unrelated full-suite repeat, as directed by latest correction.
- Implemented: exact installed Node SDK HTTP omission/native pairing/current-objective/semantic binding/plaintext repair/types and pure-browser checks PASS. Archive-derived Node22 bundle produced; no actual provider call by this agent. Root trial015 restored HTTP with omission but still had empty selections; this source correction is compatibility-only, not an incident fix.

Exact superseding unpublished archive `/tmp/ARCH-070-SHARED-007/transport-omission-890d060d52d4.tgz`, metadata6.0.1, 982847 bytes/163 members, SHA256 `890d060d52d4a840eecd4393527b895b1874a97770248a8eec1e34ff3ba0e1fd`. Prior c09ea artifact/report retained historically and superseded for current diagnostic source. Public6.0.1 unchanged, no release/merge/live operation authorized or performed.

Launcher evidence: attempt3 codex claim `70ba11c5cd6e7998ec6fd4ed7eeda697f2666bdd`, canonical primary workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-070-SHARED-007`, implementation `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-070-SHARED-007`, both `task/ARCH-070-SHARED-007`, reused canonical worktrees. Both remote task FF not needed and origin/main already current; recursive implementation sync/update passed with no entries. Initial parent3579bd9eb/implementationec7658b. No shared checkout switched, other task reused or parent submodule gitlink staged.

Installed receipt bound to exact archive890d060d52d4: all Node/type/browser checks PASS. Node22 external-package diagnostic bundle exports only `runCommerceTurn` and `OpenRouterModelClient`, no assets/maps/declarations. `/tmp/ARCH-070-SHARED-007/diagnostic-890d060d52d4/native-candidate-890d060d52d4.node22.mjs`, 145635 bytes, SHA256 `b1acf14a669e1551e985e01c1844789d0d96e1e5ae1346a8c633b4f63e5ccd7d`; gzip 43114 bytes, SHA256 `5df6c336462d0a7bafc4973c2c34779d8aa425eb945ae9b0ef02a40b69a0b010`. Root and Background received exact identities. Eventual additive release recommendation remains6.1.0, requiring separate exact metadata/archive review and new explicit public approval. No version change performed inside implementation.

### Historical attempt 2 report

### Status

Ready for independent review of attempt 2 source mechanics; all declared local checks passed. Root actual-provider candidate diagnostic pending. No publication, deployment or incident-fix claim. Source pushed on the same mirrored task branch; previous negative native-only diagnostic remains evidence below.

### Files Changed

Source checkpoint `ec7658b`, existing PR https://github.com/kodjobaah/moda-interact-shared/pull/93. New `runner/terminal-decision.ts` provides the optional synchronous generic terminal port and bounded immutable callback snapshots. Runner types/preflight/graph/final-validation route only the existing forced-final phase through separately projected canonical decisions. Native SDK supports generic `requireToolCall` with mutually exclusive named choice. Diagnostics add finite safe failure reasons. Focused tests and installed-package proof cover the exported seam.

### Architect correction checklist

- Implemented: raw provider ModelStep/call ID/name/arguments remain unchanged in the native journal; projected canonical decision never becomes transport arguments. Focused raw-journal and actual SDK tests.
- Implemented: optional synchronous `TerminalDecisionPort` with finite declared `terminalTools`, selected subset, and separate `project` result bound to the exact framework-issued binding reference (turn/inbound/model-step/raw-call SHA256/pinned response contract). No app branch mapping in Shared.
- Implemented: only existing forced-final phase advertises selected alternatives, accepts exactly one actual selected call, and executes no ordinary tools. SDK `requireToolCall` becomes `tool_choice: required`; named choice conflict rejected.
- Implemented: selector/projector callbacks receive deep frozen copied JSON snapshots. Async, throw, unknown/duplicate/reserved names, stale/foreign bindings, mutation, oversized decisions and invalid canonical results fail terminally without extra calls. Cancellation/deadline checked around callbacks.
- Implemented: all canonical validators and model/remote budgets retained. Projection is checked by existing schema, evidence, language, referral, selection and grounding mechanics; no follow-on repair after failed projection.
- Pending root-only evidence: actual natural no-seed candidate runner+SDK+application adapter probe; source cannot claim incident correction before its result.

### Validation Results

- Typecheck PASS; focused terminal-port/native SDK 14 PASS.
- tsup ESM and DTS build PASS.
- Exact installed-package Node SDK, actual IDs, chronology, semantic observation binding, plaintext feedback, generic required alternative tools, exported types and pure browser boundary PASS.
- Final full suite PASS: 828 passed, 3 existing configured skips, 831 total; zero failures. Initial test-only referral fixture mistakes were corrected (callerSignal, canonical negative fixture and curried graph invocation); no production-byte change followed archive creation.
- `git diff --check` PASS.

### Exact unpublished provisional artifact

`/tmp/ARCH-070-SHARED-007/terminal-provisional-c09ea94f6907.tgz`, metadata version 6.0.1 (unpublished), 982879 bytes/163 members. SHA256 `c09ea94f6907a46748221c50c0528cd58743cc15f1fd0eb7d79067fcdfdda549`. Shared with Background and root for local installed consumer testing only. Existing public 6.0.1 remains unchanged.

### Diagnostic bundle from exact installed archive

Node22 external-package ESM exports only `runCommerceTurn` and `OpenRouterModelClient`; no renderer assets/maps/declarations. `/tmp/ARCH-070-SHARED-007/diagnostic-c09ea94f6907/native-candidate-c09ea94f6907.node22.mjs`, 145658 bytes, SHA256 `6faf9ab8eb287cd783b7de1240fd1a6fa4a50c778cd699cbc6b7c573c52c1558`. Gzip 43120 bytes, SHA256 `e61f89cb75a2a574058a172fd6d06e105481d1c2a093ea0f928dbe8e2fff46ff`. Root received exact provenance and will combine with application adapter only after consumer checks. No actual provider calls made by this agent.

### Prior actual diagnostic outcome

Native-only candidate `800059e55690d6c27e8233fad8a6d6dd5ee9a09f5d4f9a6fcbe553c1d6fa31a0` root diagnostic was NEGATIVE: 7 SDK calls/5 tools/10 observed pairs, valid actual native IDs and pairing, final ANSWER STANDARD with no product selection, `FINAL_PRODUCT_SELECTION_MISSING`. Final-output SHA256 `e20baafb3dc0b5bc3983ec65c99eb7cc66199c546aeecd9cfe33d4eb7b986db8`. Native mechanics conformance did not fix the incident. No raw private captures committed.

### Assumptions and unresolved issues

Background owns terminal schema/mode filtering/projection and business grounding; root owns actual provider diagnostics and public archive authorization; architect owns acceptance. No publication/deployment/main merge performed. Attempt 2 generic port requires both candidate runner and SDK in the root probe. Parent and implementation histories remain separate; no parent gitlink staged.

## Historical Architect Review — source checkpoint

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

## Architect Review

### Review Status

Accepted

### Review Notes

Root authorizes extending held007 with minimal GENERIC terminal-decision seam after native007 negative and isolatedflat008 positive. Preserve all prior nativeprotocol code/checks; providerconformance correct but incidentunfixed. Normal reprepare attempt2 required, priorattempt1 preserved/claimcleared. No businessmapping inShared.

### Reviewed Files

Existing rawpendingStep/nativejournal/validateFinalResponse coupling and appadapter feasibility audit.

### Validation Reviewed

Native0077SDK/5tools/10observedpairs stillmissingselection. Flatassay0081SDK/0MCP3exactpairs valid onlyisolatedcapability. No productionfixclaim.

### Architecture Conformance

Implement synchronous optional host terminal-decision port ONLY on existing runner-required finalization. Exact rawModelStep/callID/name/arguments/nativejournal remain unchanged; canonicaldecision separate and bound to same turn/inbound/modelstep/rawcall digest/pinnedresponse hash by framework, not usermetadata. Soleactualcall required, unknown/multiple/textonly/foreign/stale results refuse. App port owns provider-facing flatschema and projection, Shared owns mechanics/terminalcontrol. Validate canonicaldecision through UNCHANGED canonicalschema/selectionconflict/grounding/mandatoryreferral/shipping/evidence/authorization checks. ANY projection or decisionvalidation failure TERMINAL, no repair/reinvoke after port, no extra model/tool/outputtoken budget. Validdecision still subjectcurrenthostverification/sendfences. Cancellation/deadline checks retained before/after synchronousprojection. No argumentrewrite masqueradingasproviderissued.

Add minimal generic SDK require-one-tool choice support if necessary for finite alternative completiontools (tool_choice required), mutuallyexclusivewith namedchoice, names/actualIDs exact, no businessbranchselection inShared. Nativeexisting canonicalrunner path unchanged when portabsent; no silentfallback once portchosen. Puretransportrequest/result API checkpoint must reach BG010owner beforecodingconsumer.

Tests: rawcanonicalimmutability/binding, ordinarycallportnotinvoked, allinvalidterminal/no secondcall, mandatoryreferralwins, exactcounters/cancel/foreignidentity/overbudget, actualSDKrequiredtoolchoice. Existingnativebatch/cache/repair/role/ID and fullguardregressions continue. Exactnewlocalpack then root ONE naturalfullcontext native+terminalprobe before sourceacceptance/publicreleaseapproval. No businessschema/layout/model/providerpolicychange. Allreleased6.0.1immutable; eventualversionrecommendation explicit, no publicationauthorization.

### Follow-up

Background ARCH-070-BACKGROUND-010 owns finite simpleflat completiontools/pinnedcanonicalprojection, no autogeneratedIDs/businessbypass. Separate008publication includes finalaccepted007 only after exactarchive+consumerproof+NEWuserapproval. No mergers/liveagentcalls.

## Terminal tool subset selection precision

Root/architect authorize OPTIONAL synchronous pure selectTools(readonly currentobservations/requiredReferral/frameworkcontext) returning a boundedunique nonempty subset of declared terminalToolNAMES. Shared only validates declaration/subset/immutability/binding, NO businessfilter. Selectedset bound to existingforcedinvocation; soleactualcall must be selected. Throws/async/unknownnames/duplicates/emptysubset terminal/noextraSDKcall. Background owns semanticavailability so knowninvalidnonproduct/shipping escapes aren't advertised merelytofailcanonicalguard. Samecheckedcopy/deepfreeze beforeandafter callback; rawprovidertransport unchanged.

### Latest correction contract: DeepSeek transport capability (2026-11-14)

Changes Requested. Preserve attempt2 and its report; normal launcher claim increments the next attempt. Trial015 changed only omission of unconditional `parallel_tool_calls:false` from exact012 and restored HTTP success through DeepInfra; raw empty arguments remained and terminal decision correctly failed. This proves a separate compatibility defect, not an incident selection fix.

Remove unconditional emission of the optional parallel-tool-call parameter. Omit it by default rather than claiming provider capability; do not synthesize sequential-provider semantics. Preserve native actual calls, batch budget/accounting, authorization, tool choice, strict schemas, model/token/deadline/cancellation and canonical business guards. No business/model/provider routing preference change in Shared. Explicit future caller opt-in is unnecessary unless existing public API already requires it; no opportunistic capability registry.

Required source tests: actual SDK HTTP body omits the key by default while exact schemas/strict/named-or-required choice/max_tokens remain unchanged; multi-call batches still respect existing remote/model budgets and result pairing; native terminal/referral/invalid-decision guards remain intact. Run affected focused checks, types/build/installed package proofs appropriate to the changed source; no unrelated broad repeats. Supply exact superseding archive/bundle identity to BG010/root. Publication remains separate and unapproved; actual full-context proof is still required before incident acceptance. Return Review and STOP.

### Final independent source acceptance — attempt 3

Accepted exact implementation `667a658915f4071835a966c345e5fe76feda0829` and report `ca07361b4`. Canonical mirrored parent/implementation worktrees, normal launcher claim70ba11c5, synchronization and recursive submodule evidence reviewed. Earlier generic native transcript/terminal-port code review retained; latest production delta removes only unconditional parallel_tool_calls:false. Actual SDK wire regressions preserve schemas/strict/auto/named/required choices/max_tokens; affected208/type/build/installed SDK/types/browser proofs pass. Root015 independently shows routing reaches DeepInfra with omission, while empty selection remains correctly rejected.

This acceptance covers reusable native protocol, immutable raw/canonical separation, terminal controls and optional transport compatibility, not application selection efficacy. Root explicitly requests source acceptance now while BG010 actual proof remains held. That application/release gate supersedes earlier wording coupling this generic task completion to incident success. No budgets, referral/grounding/business policy or privacy preference was relaxed. No source finding remains. Additive6.1.0 is the release recommendation; published6.0.1 unchanged. Separate Shared008 publication may prepare only after root's required016 application evidence disposition and requires a new explicit exact-archive public approval. No source/main merge, publication or live operation is performed by this review.

### Latest Architect Review — whole-batch terminal equivalence correction

Review Status: Changes Requested. Root explicitly reopens Complete007 after016; preserve accepted attempt3 history and number, clear claim, next normal launcher claim is attempt4. Earlier accepted source667a658 remains historical only; publication008 remains held.

Actual016 returned three recovery_complete_details calls with distinct actual provider IDs and exactly identical raw argument SHA a7d6f34b8119c94048467a9f39dda7ffa6e8a077382637c042e547ac125f3c22. Each selects two currently observed pairs. The framework correctly rejected its former sole-call contract; do not take an arbitrary first result or rewrite raw provider output.

Authorize one bounded generic correction: only the existing PURE terminal-decision phase may coalesce a batch into one equivalence class when EVERY call is a currently advertised terminal tool, every actual ID is present/unique, all names identical and all parsed arguments canonical-JSON identical. Any ordinary/foreign/unadvertised/differently named/differently valued/invalid-ID call invalidates the ENTIRE batch. Existing bounded call count/transcript limits remain. No ordinary tool execution, synthetic call/ID, new provider request, retry, token/counter reset or business validation change.

Bind the projected decision to the WHOLE original batch: ordered actual IDs plus canonical full raw-step/calls digest, same turn/inbound/modelstep/responsecontract. Preserve existing per-call identity as a representative ONLY after proving equivalence, explicitly recording that it is one actual member of the bound class, not a manufactured provider call. Expose sufficient immutable batch binding/input for the application callback to echo the exact framework binding reference; never present modified canonical args as provider-issued. Deep-copy/freeze all snapshots and validate binding before and after callback. Keep raw ModelStep and native journal byte/value-identical. Apply project ONCE; charge the original model output and step ONCE. Every canonical grounding/referral/shipping/evidence check remains authoritative; any projection or canonical failure terminal with no repair/reinvoke. Existing single-call behavior remains valid.

Required regressions: actual captured STRUCTURAL equivalent3-call batch with generic synthetic IDs/pairs projects once; all IDs/order/fullbatchdigest bound and immutable; raw unchanged; duplicate/missing IDs, one differing argument/name, one ordinary/unadvertised call, mutation/foreign binding all reject with zero project/tool work; invalid projected value still terminal; native transcript and budgets unchanged. Exact local offline replay of private016 by root must pass unchanged canonical result and exact observed membership before any further bounded natural proof. Public fixtures must not contain merchant data. Run affected focused/types/build/installed SDK/type/browser checks, no unrelated broad repeats. Deliver new exact archive/bundle and review report; STOP. No publication/main/live operation.
