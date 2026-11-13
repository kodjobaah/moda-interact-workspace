---
id: ARCH-075-GATEWAY-002
architecture_id: ARCH-075
title: Declare reader-first branded reply rollout gate
task_kind: implementation
domain: gateway
repository: moda-interact-gateway
assigned_agent: moda_gateway
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 5
executor: codex
claimed_at: 2026-11-13T20:50:32Z
attempt: 1
depends_on:
  - ARCH-075-BACKGROUND-010
enables: []
created: 2026-11-13
updated: 2026-11-13
---

# Declare reader-first branded reply rollout gate

## Architecture

ARCH075; docs/architecture/ARCH-075-ordered-recovery-message-layout.md; coordinator moda_architect.

## Objective

Codify the reader-first/new-writer-off deployment gate for consolidated branded replies.

## Context

Root verified BG010 source PR221 merged `1b71a7d3582f6f946939ac669a9308f1a0c66b01`, accepted parent PR1026 `ffa37c3f3697c038208d20f4054afc2918042141`. Dependency Complete and integrated. Runtime gate exacttrue/defaultOFF and safe startup boolean are implemented; root currently observes PhaseA OFF and retains operational enable authority.

Commonlayoutalreadyactive; BG010 must not emit newHEADER-only during overlap with oldShared5.13.9 readers. Background implements RECOVERY_BRANDED_MAIN_REPLY_ENABLED defaultoff. Canonical deployment declaration and operator-controlled PhaseA/B sequence must reflect this explicitly.

## Scope

Gateway Render test/production Blueprint declarations and bounded rollout/drift documentation/tests only.

## Out of Scope

Background implementation, environment/live mutation, provider sends, new services/secrets/paidresources, lost-event platformpauses, source/main merges.

## Requirements

- Inspect actual BG010 implementation/env parsing and all producer messaging workers before declaring. Declare RECOVERY_BRANDED_MAIN_REPLY_ENABLED consistently in test/prod canonical Blueprints for relevant workers. Operator-owned activation sync:false or existing approved mechanism must not let Blueprint hardcodedfalse overwrite deliberatePhaseBtrue; document actual unsupported setting owner if required.
- Initial absent/false PhaseA deploys compatible readers with legacywriter. Root verifies ALL oldworkers stopped/drained and allrelevantqueues/frozenjobs preserved, then enablestrue PhaseB; overlapsafe because allreadersnew. Never pause ingress or discard jobs.
- Document exact rootreadback/rollback/driftchecks and environmentisolation. RollbackturnwriterOFF whilekeepingnewreader for alreadyfrozenHEADERplans; do not rollback to oldreader with newjobs.
- No secret value added; no business implementation or liveactions.

## Work Items

- [x] Inspect acceptedBG010 env/entrypoint and canonicalBlueprint topology.
- [x] Declare operator gate and exactreader-first/drain/enable/rollback checks.
- [x] Validate actualdeclaredBlueprint/configtests and publishsource/report.

## Interfaces / Contracts

Background-owned RECOVERY_BRANDED_MAIN_REPLY_ENABLED gate; Gatewayowns Render IaC. No crossservicewire/schema change.

## Dependencies

ARCH-075-BACKGROUND-010 accepted Complete before execution.

## Enables

Root executes PhaseA/B only after accepted topology/source, no implicitoperation.

## Acceptance Criteria

- [x] Test/prod relevant worker gate declarations matchactualruntime and preserveoperatorenable.
- [x] Drain/preservejobs/PhaseB/rollback/drift sequence explicit withoutlostevents.
- [x] Focused declared configuration checks/privacy and preparedisolationevidence pass, no live mutation.

## Validation

- [x] Existing relevant Blueprint/YAML/config tests and documented envname/default/worker parity; inspectactualpackagescripts.
- [x] Diff/secret/privacy and normaldedicatedworktreepublicationevidence. Noapplication/provider tests repeated.

## Stop Condition

Publish exactsource/report, setreview, returnarchitectandstop; no main/livechanges.

## Implementation Notes

Normal launcher dedicatedmirroredworktrees, youarenotalonepreservecurrentmain/others. ReturngenuineBGgate mismatch before widening.

## Completion Report

### Status

Ready for Review

### Files Changed

- `render.test.yaml`, `render.production.yaml`: messaging-only operator-owned `RECOVERY_BRANDED_MAIN_REPLY_ENABLED` with `sync: false` and no fixed value.
- `docs/branded-reply-rollout.md`: actual entrypoint/topology evidence, Phase A/B, all-instance drain and readback, preserved jobs, rollback and drift checks.
- `tests/validate-render-blueprints.sh`, `tests/validate-render-blueprints-negative.sh`: enforce exact messaging-only external declaration and reject missing/fixed/duplicate/non-owner settings in both environments.

### Work Completed

Inspected Background accepted `1b71a7d3582f6f946939ac669a9308f1a0c66b01`: package/lock use Shared 5.13.10; composition enables only exact string `true`; WhatsApp startup emits safe `recoveryBrandedMainReplyEnabled` boolean. `start:messaging-worker` starts WhatsApp and multipart repair. Other declared worker entrypoints do not create WhatsApp/multipart workers. `npm start` combined development entrypoint also creates WhatsApp, so runbook requires actual legacy/manual/combined inventory rather than assuming canonical topology proves drain.

Root controls actual live inventory, old-instance termination verification and activation independently for test/production. No live mutation, application edits, service additions, paid capacity changes or routing changes were performed. Reader-first rollout retains queues and frozen plans; writer rollback retains compatible readers.

Implementation commit: `4c05b55`; source PR: https://github.com/kodjobaah/moda-interact-gateway/pull/17 . Both source and parent use `task/ARCH-075-GATEWAY-002`; no main merge or submodule pointer staging.

### Validation Results

- Gateway has no package.json; inspected actual `tests/validate-render-blueprints*.sh` validation entrypoints instead.
- `bash tests/validate-render-blueprints.sh`: passed, both canonical files parsed and configuration checks passed.
- `bash tests/validate-render-blueprints-negative.sh`: passed, exit 0; all eight added gate cases passed, full existing Blueprint negative matrix passed, nested ARCH-043 platform configuration negative validation passed (96 fixtures).
- `bash -n tests/validate-render-blueprints.sh tests/validate-render-blueprints-negative.sh`: passed.
- `git diff --check`: passed. Reviewed diff contains only nonsecret declarations, documentation and validators.
- No Docker/application/provider suites required for this configuration-only change. No live validation claimed. Root-owned live procedure: execute the environment-specific Phase A/B and rollback/readback checks in `docs/branded-reply-rollout.md`; expected result is compatible-reader source/instance evidence, no old readers, preserved jobs and startup booleans matching the intended phase.

### Physical Worktree and Launcher Evidence

Prepared execution true; dependency gate passed (BG010 complete); claim attempt 1 committed/pushed `ece41eb266dcf2201ded218faac8bb5e2d289804`.
Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-075-GATEWAY-002` (reused).
Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-075-GATEWAY-002` (created).
Both branches: `task/ARCH-075-GATEWAY-002`. Parent and implementation remote task fast-forward: not-needed; origin/main incorporation: already-current.
Recursive implementation submodule sync/update passed; entries empty. Shared/default checkouts not switched/mutated; another task worktree not reused. Startup discovery/claim was not repeated.

### Deviations

None. Existing Architect Review is Pending, so no Changes Requested correction contract applies.

### Assumptions

Root controls live activation. Operator-owned nonsecret values remain independently configured per environment; an approved Phase B true must not be reset by Blueprint synchronization.

### Unresolved Issues

Live Phase A/B/drain evidence and operator readback remain root-owned; repository validation is not deployment evidence.

### Architectural Concerns

None. No new resources/cost/capacity claims; existing infrastructure sizing unchanged.

## Architect Review

### Review Status

Pending

### Review Notes

None

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

No live rollout or architecture completion claim.
