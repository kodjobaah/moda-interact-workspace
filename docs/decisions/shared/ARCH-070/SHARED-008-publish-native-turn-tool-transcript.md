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

- [ ] Verify accepted007 exact source c1c1d2b8d00276dd88bf974997db2c8855fa9aa4 and root018 disposition before normal preparation.
- [ ] Apply additive version6.1.0 to package metadata/lock only and prepare one immutable archive from accepted built output, without rebuilding accepted implementation.
- [ ] Compare every nonmetadata member with accepted79003cd3 archive; record exact archive SHA256/size/member count/SHA1/SRI for user review.
- [ ] Hold publication until root relays new explicit user approval for that exact archive/public latest.
- [ ] Publish the approved exact archive without repack/rebuild; independently verify registry version/latest/download bytes/SRI and unchanged public6.0.1.
- [ ] Return immutable publication receipt/report and STOP; consumers remain separate.

## Interfaces / Contracts

Contractowner ARCH-070-SHARED-007, published @modainteract/moda-interact-shared commerce/runner and Node model subpath; Background consumes canonicalpackage. PureJSONtranscript separate from business evidence. No persisteddatabase/wirequeue change.

## Dependencies

ARCH-070-SHARED-007

## Enables

Source007→release008→finalconsumer009; localpackedconsumerproof permitted beforepublicationapproval under architectReadyamendment.

## Acceptance Criteria

- [ ] Source007 is architect-accepted and root application evidence disposition permits preparation.
- [ ] Version6.1.0 metadata-only release preserves every accepted nonmetadata member exactly.
- [ ] New explicit exact-artifact publication approval is recorded before publish.
- [ ] Actual public registry receipt proves exact approved archive/version/latest;6.0.1 unchanged.
- [ ] No implementation validation reruns or consumer integration inside this release task.

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

## Prepared release plan checkpoint

Architect reviewed accepted c1c1d2b and superseding79003cd3 archive; additive native opt-in, optional terminal port and compatible omission support6.1.0. Whole-batch fields extend only newly unpublished APIs. Root018 natural application outcome remains pending: task stays Pending, no claim/publication authorization inferred. Root must make accepted source/report available to normal launcher dependency resolution before execution. Metadata branch may change package.json/package-lock.json only; no rebuild, source test or lint repetition. Consumer Background and Commerce adoption/deployments precede global saved routing nesting; old consumers cannot remain. Exact archive is reviewable before any public approval question. No publication until root's explicit relay.
