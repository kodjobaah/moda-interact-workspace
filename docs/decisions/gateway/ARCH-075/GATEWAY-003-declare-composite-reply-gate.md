---
id: ARCH-075-GATEWAY-003
architecture_id: ARCH-075
title: Declare default-off composite reply deployment gate
task_kind: implementation
domain: gateway
repository: moda-interact-gateway
assigned_agent: moda_gateway
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 10
executor: codex
claimed_at: 2026-11-14T00:14:56Z
attempt: 1
depends_on:
  - ARCH-075-SHARED-010
enables: []
created: 2026-11-13
updated: 2026-11-14
---

# Declare default-off composite reply deployment gate

## Architecture

ARCH-075; docs/architecture/ARCH-075-ordered-recovery-message-layout.md; moda_architect.

## Objective

Codify the new defaultOFF composite writer gate and safe reader-first activation procedure without changing deployment topology.

## Context

Single-bubble composite uses distinct RECOVERY_COMPOSITE_REPLY_ENABLED so current branded-main gate stays unchanged. Source branch implementation is separately tested; no live activation requested by task author.

## Scope

Canonical test/production Render Blueprint messagingworker service-level env declaration sync:false, existing bounded Blueprint negative validation and deployment documentation.

## Out of Scope

Application implementation, secrets/hardcodedtrue, other workers/services topology/cost/scaling, live Render changes/sends, npm publication.

## Requirements

- Declare exact composite gate service-level sync:false for messagingworker in test/production only. Do not hardcode enable or groupinheritance; absent/invalid/false remains OFF under Background.
- Document deployed reader-first with compositeOFF: verify actual runtime inventory, every old reader drained, safe startup boolean proof, then root separately authorizes ON and actual one-bubble media/caption. Rollback writerOFF preservingnewreader/frozenplans; noqueueclear/reset.
- Existing branded-main flag unaffected. No secret values, new services or cost. Preserve current Blueprint validations and existing rollout docs.

### Preparatory execution gate

Root requests all authorized source be concrete/tested/pushed before final public release approval. This Ready task may implement/test/push the narrow sync:false declarations and rollout docs now. Return sourcePR/checkpoint while In Progress if Background014 actual flag proof is still pending. Do not claim completed runtime rollout or set live values. Current branded-main flag stays untouched; new composite flag exactliteraltrue defaultOFF must match Background final source before final acceptance.

## Work Items

- [x] Add narrow declarations/negative validation.
- [x] Document exact OFF→readerdrain→authorizedON and rollback.
- [ ] Run bounded Blueprint checks and publish report.

## Interfaces / Contracts

Accepted Background014 gate exact literaltrue and safe startupboolean; existing canonical Render IaC.

## Dependencies

SHARED010 Complete/Accepted/integrated at Sharedmainde3f9ee5d1aa24c4ac6c51b3f82b12269fddd300/parentmaineed3357296a61c2196af0e008fa89af6b1efbf7d. Root explicitly authorizes normal preparatory source/config/docs claim now against stable approved composite flag, in parallel with Background014 source. Final acceptance must verify actual Background014 flag/defaultOFF/startup proof; keep In Progress if that proof is pending. No live config/activation or fabricated deployed capability.

## Enables

Separately authorized root activation after source/readers/visual checks, not automatic.

## Acceptance Criteria

- [ ] Exact declaration scoped service-level to two messagingworkers, no enabledvalue/secrets.
- [ ] Existing topology/commands unchanged; reader-first and rollback documented.
- [ ] Positive/negative Blueprint checks and clean mirrored evidence.

## Validation

- [x] Existing declared Blueprint syntax/negative gate validation and appropriate bounded regression checks.
- [x] Diff/privacy and no application/topology change.

## Stop Condition

Publish exact mirrored source/report, set review and return architect. No main merge, live mutation, enabled consumer or npm publication without release-specific authorization.

## Implementation Notes

Normal launcher dedicated sibling worktrees. You are not alone; preserve others and primary. Original approved mock is schematic only: small contained logo alongside shop details, divider, product beneath. Root owns operational/visual review and integration; no live sends.

## Completion Report

### Status

Preparatory checkpoint — In Progress; final Background014 source proof pending.

### Files Changed

- `render.test.yaml`, `render.production.yaml`: add only messaging-worker service-level `RECOVERY_COMPOSITE_REPLY_ENABLED`, `sync: false`, no value.
- `tests/validate-render-blueprints.sh`: enforce the exact two environment-specific messaging-owner inputs.
- `tests/validate-render-blueprints-negative.sh`: reject missing, fixed false/true, sync-plus-value, duplicate, wrong-owner and group declarations in both environments.
- `docs/composite-reply-rollout.md`: separate gate, OFF/new readers/all-old-readers drain, root-authorized ON/readback/provider evidence and OFF rollback retaining compatible readers/frozen work.

### Work Completed

Source committed/pushed `a2157f2df59566bbdf1b597ab8a54c42c1e79ca8` on `task/ARCH-075-GATEWAY-003`. Draft source PR: https://github.com/kodjobaah/moda-interact-gateway/pull/18 . Existing branded-main declarations/docs and all service commands/topology remain unchanged. No live environment or provider operations, source/main merges, npm publication or new resources/cost.

Read-only inspection of canonical Background014 implementation worktree finds draft `composite.ts` exact-string `RECOVERY_COMPOSITE_REPLY_ENABLED === 'true'` helper and `whatsapp.worker.started` boolean `recoveryCompositeReplyEnabled`. Those files remain uncommitted drafting evidence; package inspection still reports Shared 5.13.10. Final frozen source, consumer version and focused parser/startup validation evidence must be supplied/verified before this task enters review. No deployed runtime proof is claimed.

Actual messaging entrypoint creates WhatsApp worker/multipart repair; combined development `npm start` also creates WhatsApp worker. Runbook requires actual runtime inventory including extra combined/manual readers rather than assuming canonical inventory proves drain.

### Validation Results

Gateway has no package.json; inspected actual declared shell validators.

- `bash tests/validate-render-blueprints.sh`: passed, both canonical Blueprints.
- `NEGATIVE_CASE_FILTER=composite_gate bash tests/validate-render-blueprints-negative.sh`: passed, 14 focused fixtures, exit 0.
- `NEGATIVE_CASE_FILTER=branded_gate bash tests/validate-render-blueprints-negative.sh`: passed, eight existing gate regression fixtures, exit 0.
- `bash -n tests/validate-render-blueprints.sh tests/validate-render-blueprints-negative.sh`: passed.
- `git diff --check`: passed; diff contains only configuration, validators and docs, no secrets or application changes.

Bounded checks satisfy preparatory scope; no broad Docker/system/provider suites repeated. Root owns live procedure in `docs/composite-reply-rollout.md`: expected success is complete compatible-reader/source inventory, OFF startup readback, all-old-reader termination with preserved work, separate authorization and ON/readback plus one-bubble provider/visual proof.

### Launcher Isolation Evidence

Prepared execution true, dependency gate passed (Shared010 complete), attempt 1 claim `e23e336f98658ab0cc8d23eb63fe954449a8bb1f` committed/pushed.
Canonical primary workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
Parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-075-GATEWAY-003` reused; implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-075-GATEWAY-003` created. Both branches `task/ARCH-075-GATEWAY-003`.
Both remote task fast-forward checks not-needed; both origin/main incorporations already-current. Recursive implementation submodule sync/update passed; entries empty. No shared/default checkout switched or mutated; no other task worktree reused; no parent gitlink staged.

### Deviations

None. Preparatory execution explicitly permits source checkpoint before final Background proof. Architect Review Pending has no Changes Requested correction contract.

### Assumptions

Root owns final integration/release/live authorization. Existing branded-main value remains untouched; composite operator setting is independent per environment.

### Unresolved Issues

Final Background014 gate/default-OFF/startup proof and accepted consumer version pending. Keep task In Progress and source PR draft until verified; no runtime activation or final acceptance claimed.

### Architectural Concerns

None beyond the explicit prerequisite hold. No infrastructure topology/cost/capacity changes.

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

No architectural/live completion claim.
