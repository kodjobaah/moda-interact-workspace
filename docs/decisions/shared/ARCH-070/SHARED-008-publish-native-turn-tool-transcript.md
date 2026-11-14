---
id: ARCH-070-SHARED-008
architecture_id: ARCH-070
title: Publish accepted native turn tool protocol
task_kind: publication
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 10
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-070-SHARED-007
enables: []
created: 2026-11-14
updated: 2026-11-14
---

# Publish accepted native turn tool protocol

## Architecture

ARCH-070; docs/architecture/ARCH-070-verified-recommendation-terminal-turn-recovery.md; moda_architect.

## Objective

Publish accepted native turn tool protocol.

## Context

Fullcontext003 reproduced selectionomission; lastoutputfeedback004 negative; losslessschema005 negative; fullcurrentturncontexttrace006 negative despite nonemptytrace (4SDK/3tools,maxdata36045/fullrequest77737). None wiredproduction. Codesource gap: SDK dropsnativecallIDs, runner omitsassistantsteps and emits toolresults as HumanJSON; proper protocol mechanics now authorized, no businessrule change inferred.

## Scope

Release-only accepted007 source. Determine semver from actualpublicAPI compatibility; provisional6.1.0 if additive opt-in, do not assume. Prepare exact metadata/archive and compare accepted code members. No newimplementation/repeatedtestsbuildlint. Publication HELD until root relays new explicit user approval exact testedarchive/publiclatest AFTER concrete Backgroundconsumer/localpacked fullcontextdiagnostic. Existing6.0.1 approval doesnotapply. Verify actualregistrydownloadSHA/SRI/version/latest and oldversionimmutable.

## Out of Scope

Businessschema/selection/referral/layout/model/token/providerpolicy changes, fakeIDs/facts, new retries, liveagentcalls/mainmerges. No generalunboundedframework.

## Requirements

Release-only accepted007 source. Determine semver from actualpublicAPI compatibility; provisional6.1.0 if additive opt-in, do not assume. Prepare exact metadata/archive and compare accepted code members. No newimplementation/repeatedtestsbuildlint. Publication HELD until root relays new explicit user approval exact testedarchive/publiclatest AFTER concrete Backgroundconsumer/localpacked fullcontextdiagnostic. Existing6.0.1 approval doesnotapply. Verify actualregistrydownloadSHA/SRI/version/latest and oldversionimmutable.

## Work Items

- [ ] Implement owning bounded capability/release gate.
- [ ] Preserve exact identity/arguments/results/businessguards.
- [ ] Complete required checks/exactreport.

## Interfaces / Contracts

Contractowner ARCH-070-SHARED-007, published @modainteract/moda-interact-shared commerce/runner and Node model subpath; Background consumes canonicalpackage. PureJSONtranscript separate from business evidence. No persisteddatabase/wirequeue change.

## Dependencies

ARCH-070-SHARED-007

## Enables

Source007→release008→finalconsumer009; localpackedconsumerproof permitted beforepublicationapproval under architectReadyamendment.

## Acceptance Criteria

- [ ] Exactnativeassistant/toolpair semantics and unchangedbusinessguards verified whereowning.
- [ ] UnsafeIDs/orphans/overflow/retry/budget boundaries failclosed.
- [ ] Actualdiagnostic outcome/limits explicit; no productionfixclaim fromstubtests.
- [ ] Requiredchecks and exactimmutablehandoff complete.

## Validation

Release mechanics only: prerequisiteAccepted,metadataonly,intendedversion,exactarchive,explicitapproval,publishsuccess,independentregistryreceipt. No implementationvalidationreruns.

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
