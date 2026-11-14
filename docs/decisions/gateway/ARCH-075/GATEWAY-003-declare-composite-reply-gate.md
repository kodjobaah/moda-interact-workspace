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
status: complete
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
- [x] Run bounded Blueprint checks and publish report.

## Interfaces / Contracts

Accepted Background014 gate exact literaltrue and safe startupboolean; existing canonical Render IaC.

## Dependencies

SHARED010 Complete/Accepted/integrated at Sharedmainde3f9ee5d1aa24c4ac6c51b3f82b12269fddd300/parentmaineed3357296a61c2196af0e008fa89af6b1efbf7d. Root explicitly authorizes normal preparatory source/config/docs claim now against stable approved composite flag, in parallel with Background014 source. Final acceptance must verify actual Background014 flag/defaultOFF/startup proof; keep In Progress if that proof is pending. No live config/activation or fabricated deployed capability.

## Enables

Separately authorized root activation after source/readers/visual checks, not automatic.

## Acceptance Criteria

- [x] Exact declaration scoped service-level to two messagingworkers, no enabledvalue/secrets.
- [x] Existing topology/commands unchanged; reader-first and rollback documented.
- [x] Positive/negative Blueprint checks and clean mirrored evidence.

## Validation

- [x] Existing declared Blueprint syntax/negative gate validation and appropriate bounded regression checks.
- [x] Diff/privacy and no application/topology change.

## Stop Condition

Publish exact mirrored source/report, set review and return architect. No main merge, live mutation, enabled consumer or npm publication without release-specific authorization.

## Implementation Notes

Normal launcher dedicated sibling worktrees. You are not alone; preserve others and primary. Original approved mock is schematic only: small contained logo alongside shop details, divider, product beneath. Root owns operational/visual review and integration; no live sends.

## Completion Report

### Status

Ready for Review — final immutable Background source contract reconciled; Background CI/architect acceptance and live rollout remain separately gated.

### Files Changed

- `render.test.yaml`, `render.production.yaml`: add only messaging-worker service-level `RECOVERY_COMPOSITE_REPLY_ENABLED`, `sync: false`, no value.
- `tests/validate-render-blueprints.sh`: enforce the exact two environment-specific messaging-owner inputs.
- `tests/validate-render-blueprints-negative.sh`: reject missing, fixed false/true, sync-plus-value, duplicate, wrong-owner and group declarations in both environments.
- `docs/composite-reply-rollout.md`: separate gate, OFF/new readers/all-old-readers drain, root-authorized ON/readback/provider evidence and OFF rollback retaining compatible readers/frozen work.

### Work Completed

Source committed/pushed `a2157f2df59566bbdf1b597ab8a54c42c1e79ca8` on `task/ARCH-075-GATEWAY-003`. Draft source PR: https://github.com/kodjobaah/moda-interact-gateway/pull/18 . Existing branded-main declarations/docs and all service commands/topology remain unchanged. No live environment or provider operations, source/main merges, npm publication or new resources/cost.

Read-only final reconciliation used immutable Background commit `c7351ce5cbe2b34a7d54e02e5d1dc44affcc2ed6` (PR224; runtime implementation `52d` with only lock adoption changed in this final head). `src/services/recovery-multipart/composite.ts` exports `compositeReplyEnabled()` as `process.env.RECOVERY_COMPOSITE_REPLY_ENABLED === 'true'`; absent, false and all unrecognized strings therefore remain OFF. `src/workers/whatsapp.worker.ts` emits `recoveryCompositeReplyEnabled: compositeReplyEnabled()` on existing `whatsapp.worker.started`; the branded-main boolean and meaning remain unchanged. `docs/arch075-composite-replies.md` confirms reader-first semantics, exact startup field, messaging/legacy combined consumer audit and retained frozen plans on rollback.

Final Background package and lock declare Shared `6.0.0`, resolved from `https://registry.npmjs.org/@modainteract/moda-interact-shared/-/moda-interact-shared-6.0.0.tgz`. Coordinator supplied accepted/published Shared evidence: source `ade292`, accepted parent `a8b71f3d3dce0eeacaa6f797fef07ddb65f979e0`. No Blueprint flag/name/parser mismatch was found; Gateway implementation remains exactly `a2157f2df59566bbdf1b597ab8a54c42c1e79ca8`, with no additional source changes or new environment mechanism. The existing runbook's final-source proof requirement is satisfied by this report's immutable inspection; its activation prerequisites remain operational gates.

Background final CI/tests and architect source acceptance were still finishing at this report checkpoint; no pass or acceptance is claimed on their behalf. Root alone owns preprovisioning the composite setting false and subsequent operational decisions. No deployed startup, drain, enabled writer, media/provider proof or live rollout is claimed.

Actual messaging entrypoint creates WhatsApp worker/multipart repair; combined development `npm start` also creates WhatsApp worker. Runbook requires actual runtime inventory including extra combined/manual readers rather than assuming canonical inventory proves drain.

### Validation Results

Gateway has no package.json; inspected actual declared shell validators.

- `bash tests/validate-render-blueprints.sh`: passed, both canonical Blueprints.
- `NEGATIVE_CASE_FILTER=composite_gate bash tests/validate-render-blueprints-negative.sh`: passed, 14 focused fixtures, exit 0.
- `NEGATIVE_CASE_FILTER=branded_gate bash tests/validate-render-blueprints-negative.sh`: passed, eight existing gate regression fixtures, exit 0.
- `bash -n tests/validate-render-blueprints.sh tests/validate-render-blueprints-negative.sh`: passed.
- `git diff --check`: passed; diff contains only configuration, validators and docs, no secrets or application changes.

The unchanged Gateway source retains the recorded green bounded checks; no 96-fixture matrix or other unaffected suites were repeated during report-only reconciliation. `git diff --check` and clean implementation status were rechecked. Bounded checks satisfy this configuration scope; no broad Docker/system/provider suites repeated. Root owns live procedure in `docs/composite-reply-rollout.md`: expected success is complete compatible-reader/source inventory, OFF startup readback, all-old-reader termination with preserved work, separate authorization and ON/readback plus one-bubble provider/visual proof.

### Launcher Isolation Evidence

Prepared execution true, dependency gate passed (Shared010 complete), attempt 1 claim `e23e336f98658ab0cc8d23eb63fe954449a8bb1f` committed/pushed.
Canonical primary workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
Parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-075-GATEWAY-003` reused; implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-075-GATEWAY-003` created. Both branches `task/ARCH-075-GATEWAY-003`.
Both remote task fast-forward checks not-needed; both origin/main incorporations already-current. Recursive implementation submodule sync/update passed; entries empty. No shared/default checkout switched or mutated; no other task worktree reused; no parent gitlink staged.

### Deviations

None. Preparatory checkpoint is now reconciled against immutable actual-registry Background source. Architect Review Pending has no Changes Requested correction contract.

### Assumptions

Root owns final integration/release/live authorization. Existing branded-main value remains untouched; composite operator setting is independent per environment.

### Unresolved Issues

Final Background014 CI/test completion and architect acceptance remain external prerequisites for release/integration; immutable flag/default-OFF/startup source and Shared 6.0.0 adoption have been verified. Source PR remains draft under root release hold. Root-owned preprovisioning, actual deployed startup/drain checks and any later activation/provider proof are not performed or claimed by this task.

### Architectural Concerns

No source contract mismatch. Preserve the explicit Background acceptance/release and root operational gates. No infrastructure topology/cost/capacity changes.

## Architect Review

### Review Status

Accepted

### Review Notes

Accepted exact Gateway sourcea2157f2df59566bbdf1b597ab8a54c42c1e79ca8 (PR18), immutable report7a0201e1e and final parent reconciliationdaf015417 (actual main17eef incorporated). Actual Blueprint/validator/runbook diff inspected; source unchanged/clean. Launcher dedicated isolation/synchronization claime23e336f98658ab0cc8d23eb63fe954449a8bb1f reviewed.

Final immutable Backgroundc599f3dd4042a1cc72d764b5a45b25f4d32e5ca9 (runtime52d) is separately architect Accepted with both exactheadCI green; Shared6.0.0 actual published and registry adopted. Exact literaltrue/defaultOFF helper and existing worker-start boolean match declared input. Earlier report's pending external source gate is now satisfied; no source mismatch/no new mechanism needed.

### Reviewed Files

render.test.yaml/render.production.yaml messaging-only service inputs, positive/negative Blueprint validators, docs/composite-reply-rollout.md and actual final Background gate/startup/consumer topology evidence.

### Validation Reviewed

Both Blueprint validation PASS;14composite negative fixtures and8existing branded gate regressions PASS; shell syntax/diff checks PASS. Unchanged bounded validation retained, no unnecessary unaffected matrix rerun. No secrets/resources/cost/topology changes. Root externally preprovisioned persistedfalse on BOTH workers via SAVEONLY and verified values, no deployment/enable claimed by that operation.

### Architecture Conformance

Conforms: only independent sync:false flag on2messaging workers, no hardcodedvalue/group override, existing branded flag unchanged; actual runtime inventory/reader-first OFF/drain/separateON/rollback retaining compatible current readers required. Configuration acceptance does not prove deployed startup/drain or live one-bubble delivery. ARCH075 In Progress.

### Follow-up

Root merges source then actual parent gitlink and owns all live operations. Verify accepted worker source/startupfalse and every predecessor drain before enabling; controlled new template/reference/native cohort flow has no provider-name adoption bypass. Do not delete immutable audit/customer records. Unrelated closed workspacePR98 body incident is RESOLVED by root using official edit UI2INS/0DEL evidence, exactempty restoration and REST/UIreadback; no code affected/no further unrelated edits.
