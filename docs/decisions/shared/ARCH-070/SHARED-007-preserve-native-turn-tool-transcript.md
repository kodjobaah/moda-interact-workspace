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
status: in_progress
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

- [ ] Implement owning bounded capability/release gate.
- [ ] Preserve exact identity/arguments/results/businessguards.
- [ ] Complete required checks/exactreport.

## Interfaces / Contracts

Contractowner ARCH-070-SHARED-007, published @modainteract/moda-interact-shared commerce/runner and Node model subpath; Background consumes canonicalpackage. PureJSONtranscript separate from business evidence. No persisteddatabase/wirequeue change.

## Dependencies

None; existing runner available.

## Enables

Source007→release008→finalconsumer009; localpackedconsumerproof permitted beforepublicationapproval under architectReadyamendment.

## Acceptance Criteria

- [ ] Exactnativeassistant/toolpair semantics and unchangedbusinessguards verified whereowning.
- [ ] UnsafeIDs/orphans/overflow/retry/budget boundaries failclosed.
- [ ] Actualdiagnostic outcome/limits explicit; no productionfixclaim fromstubtests.
- [ ] Requiredchecks and exactimmutablehandoff complete.

## Validation

Focused actualSDKroles/IDs/order+runner batch/cache/denial/invalid/retry/budgetskip/finalrepair/plaintext/cancel/deadline/modelremoteceilings/overflow tests, types/build/installedNode/browserpureboundary/diffprivacy. Exact tested localpack to consumer/root beforepublication. No provider calls byagent.

## Stop Condition

After definedchecks publishmatching source+parentreport, review and STOP. Publicationheldgate remainsInProgress, no inferredapproval. Return architecturegaps ratherthanexpand.

## Implementation Notes

Normal moda-task canonical siblingworktree/claim; notalonepreserveothers. Rootownslive/publicapproval/mainmerge. Inspectrole/policies/declaredscripts. Shopifyingress hotpath unaffected; perconversation ephemeralbounded transcript no globalcache/state. No newgenericlogs/rawcontent; framework/sharedloggingonly.

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

Pending

### Deviations

None

### Assumptions

None

### Unresolved Issues

Providerconformance notguaranteed beforeactualnativeproof.

### Architectural Concerns

None

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
