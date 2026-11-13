---
id: ARCH-075-BACKGROUND-009
architecture_id: ARCH-075
title: Wire production human common-root preparation
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 5
executor: codex
claimed_at: 2026-11-13T19:49:35Z
attempt: 1
depends_on:
  - ARCH-075-BACKGROUND-002
enables: []
created: 2026-11-13
updated: 2026-11-13
---

# Wire production human common-root preparation

## Architecture

ARCH075; docs/architecture/ARCH-075-ordered-recovery-message-layout.md; coordinator moda_architect.

## Objective

Make the default production human-command adapter freeze an eligible common-layout root before ordered delivery.

## Context

Root actual production common activation revision1 succeeded, approved NoOffer assignments switched. Genuine human command failed multipart_root_not_prepared despite preparedAt and HUMAN revision7, with no outbound root/parts/provider send. Root read-only source inspection found human-command-dispatcher.service.ts defaultDependencies injects multipart.continue without freeze; dispatch prefers that injected adapter and creates an absent root only when engine.freeze exists. Injected complete engines in tests hide the production wiring gap. Earlier human-inactive cancellations were test timing and must not be conflated with this failure. Root will supply protected exact evidence directly; do not repeat live investigation or mutate live state.

## Scope

Background default human dispatcher multipart adapter wiring and directly related meaningful default-runtime and disposable PostgreSQL regressions. Minimal freeze delegation using the existing canonical delivery engine; preserve frozen ordered root/media/footer contracts.

## Out of Scope

Shared/DB/Admin contracts or releases; new engine/framework; live commands/settings/DB writes/provider sends; weakening guards or fabricating roots/parts; replays of cancelled commands; sender pooling; unrelated AI/recovery redesign.

## Requirements

- Default production wiring must expose the existing delivery engine freeze capability as well as continuation, so an eligible prepared human common command can atomically freeze exactly one root then continue its ordered parts. Reuse existing APIs, never duplicate preparation or insert arbitrary rows as workaround.
- Regression must exercise DEFAULT production dependency/adapter construction, not only inject a full engine. Demonstrate current failure before correction, then successful absent-root freeze delegation and correct continuation under real PG ownership/constraint behavior.
- Preserve command lease/CAS/control revision/mode, trusted shop/conversation/checkout common identity, moderation, root admission/dispatch permit, immutable prepared evidence, exact logo/details/body/product/footer ordering and idempotent replay. A root missing because a guard fails must remain fail closed; no provider call before valid root.
- Keep absent/noteligible/unknown/terminal distinctions and bounded retry semantics. Replayed or concurrently claimed commands must not create a second root/part or duplicate provider send. Human-inactive, stale revision, moderation refusal and tampered prepared/common evidence remain negative tests.
- No new durable schema or cross-service contract is expected. Report any concrete dependency gap before widening scope. No generic logger/telemetry duplication; if changed semantic diagnostics are necessary reuse Shared logging.
- Root owns final source/parent merges, deployment verification, and genuinely new human/AI live messages after rollout. Local tests are not proof of live delivery; preserve active root/media/footer controls.

## Work Items

- [ ] Confirm root's narrow default-wiring gap and capture failing default-runtime regression.
- [ ] Delegate existing freeze capability without bypassing lifecycle/dispatch guards.
- [ ] Prove PG first-freeze/continuation/replay and relevant negative behavior; run required checks.
- [ ] Publish exact source and mirrored report with launcher/source/evidence provenance, then return review.

## Interfaces / Contracts

Existing Background human command/default adapter and canonical multipart engine; published Shared ordered layout contracts unchanged. Existing Database root/part/dispatch constraints remain authoritative.

## Dependencies

ARCH-075-BACKGROUND-002 architect-accepted Complete.

## Enables

Root-owned deployment and genuine new human common-layout live test, followed by AI mode proof. No automatic follow-on task.

## Acceptance Criteria

- [ ] Default production wiring can prepare an eligible absent root and continue using existing engine; failing regression becomes green.
- [ ] Real PG tests prove exact one root/part lineage and immutable ordering, no duplicate provider send on replay/concurrency.
- [ ] Human/control/moderation/common evidence/lease/dispatch negatives remain enforced.
- [ ] Relevant tests/build/scoped lint/diff/privacy and physical worktree preparation evidence pass; no live mutations.

## Validation

- [ ] Focused default-runtime RED/GREEN plus existing human/multipart/control/dispatch regression suites.
- [ ] Disposable PostgreSQL human/common-root first-freeze, continuation, replay/concurrency and negative guard tests; no hosted DB fallback.
- [ ] Relevant declared full tests, production build/typecheck, lint with exact existing baseline disposition if untouched errors persist; do not suppress new failures or broaden unrelated cleanup.
- [ ] Exact source diff/privacy, matching branch publication, normal launcher isolation/synchronization/recursive evidence and exact-head remote checks before root merge.

## Stop Condition

Set review and return exact source/report after required checks. Do not self-accept, merge, deploy, run live commands or start follow-on work.

## Implementation Notes

Use normal launcher-prepared dedicated parent/implementation task worktrees. You are not alone; preserve others/current main/primary originals. Root's code evidence is a starting point, not permission to bypass a lifecycle gate. Read shared logging convention only if changing runtime structured logging. No source changes outside owning Background scope.

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

Not run

### Deviations

None

### Assumptions

Root owns private live evidence and operational rollout; no live test by owner.

### Unresolved Issues

Live human and AI delivery proof remains required after source deployment.

### Architectural Concerns

Return genuine cross-owner gaps before expansion.

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

ARCH075 remains In Progress pending real approval/activation/delivery acceptance.
