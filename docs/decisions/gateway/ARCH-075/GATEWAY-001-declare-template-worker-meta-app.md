---
id: ARCH-075-GATEWAY-001
architecture_id: ARCH-075
title: Declare Meta app identity for template workers
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
claimed_at: 2026-11-13T09:07:05Z
attempt: 1
depends_on: []
enables:
  - ARCH-075-SYSTEM-TEST-001
created: 2026-11-13
updated: 2026-11-13
---

# Declare Meta app identity for template workers

## Architecture

ARCH-075; docs/architecture/ARCH-075-ordered-recovery-message-layout.md; coordinator moda_architect.

## Objective

Declare Meta app identity for template workers.

## Context

Actual staged registration encountered missing worker META_APP_ID before durable creation intent. BLOCKED rows cannot normally recover. Separately Admin confirmation accepts English SOURCE_SAVED while Background correctly requires REVIEWED; reviewing English only after provider approval is circular. These are concrete distinct owned gaps; preserve all accepted content/transport work.

## Scope

Relevant render.test.yaml/render.production.yaml messaging worker envVars and canonical render.yaml only if it declares the same service; matching deployment notes and structural checks.

## Out of Scope

Other repositories, Shared publication/schema, provider guard weakening, uncertain template-create retry, live provider/database/configuration writes, source merges, automatic activation or unrelated refactors.

## Requirements

Declare META_APP_ID with sync:false only on actual messaging worker services in both environments. No hardcoded app IDs/credential values, unrelated services, topology/scaling or env-group changes. Confirm actual upload adapter consumes the variable and startup worker matches declarations. Document setting the existing provider app identity through secure Render env mechanism; no new app/grants or credential rotation. Document preclaim failure recovery dependency instead of direct database repair. No live Render mutation in task.

Runtime inspection of accepted Background entrypoints/messaging.ts proves startProductionMetaTemplateDuePoller runs in messaging workers; merchant-communications owns translation execution, not this poller. The original task target was incorrect and is superseded by this evidence without resetting the claim. Root corrects live environment placement separately; no credentials or topology changes.

## Work Items

- [x] Confirm owning defect and implement only bounded capability.
- [x] Prove meaningful failure/race/compatibility behavior.
- [x] Complete checks, mirrored Completion Report and stop.

## Interfaces / Contracts

Existing Admin confirmed Meta registration and Background immutable provider lifecycle; Gateway owns runtime variable declaration. No new cross-service payload, setting, schema or Shared release. Runtime provider config remains server-owned and no secrets enter diagnostics.

## Dependencies

None

## Enables

ARCH-075-SYSTEM-TEST-001

## Acceptance Criteria

- [x] Assigned bounded gap corrected without weakening permission/provider identity or immutable source guards.
- [x] Negative/race/idempotency behavior and unchanged legacy domain semantics proven where applicable.
- [x] Canonical physical isolation/synchronization and exact checks documented; no live action by agent.

## Validation

- [x] Declared YAML/blueprint structural validation and focused service/env assertions: each relevant test/production worker exactly one META_APP_ID sync:false, no value/secrets/unrelated changes. Existing declared lint/checks as appropriate; report baseline unavailable tooling honestly, no app tests or deploy.
- [x] Diff/privacy hygiene and no unauthorized external mutation.

## Stop Condition

After required scope/checks, submit review and STOP. Do not execute live repair, register providers, deploy, merge or begin follow-on tasks.

## Implementation Notes

You are not alone; preserve others. Canonical launcher packet owns startup/claim. Root owns all final integration and live operations. Generic logging uses published shared logging if changed. Return actual dependency gaps rather than inventing alternate protocol or local generic primitives.

## Completion Report

### Status

Ready for Review. Implementation committed and pushed at `a8239ffd1277a25fdc53e978b03acec16ca47657` on `task/ARCH-075-GATEWAY-001`; parent report uses the same branch. No merges or live actions by this agent.

### Files Changed

- `render.test.yaml` and `render.production.yaml`: exactly one service-level `META_APP_ID` / `sync: false` on the actual messaging worker in each environment.
- `tests/validate-render-blueprints.sh`: exact declaration, ownership and group exclusion assertions.
- `tests/validate-render-blueprints-negative.sh`: ten missing/duplicate/value/non-owner/group fixtures across both environments.
- `docs/render-topology.md`: secure existing app identity setup, runtime ownership, preclaim recovery dependency and rollback notes.

### Work Completed

Implemented the coordinator amendment `808c6929d`: initial merchant-communications target was incorrect. Background `origin/main` inspected at `c5dad158175733849fb6f9ab6ff2e89841d195cf`: `src/entrypoints/messaging.ts` imports/starts `startProductionMetaTemplateDuePoller` (lines 10/25), and `src/services/meta-template-management/due-poller.ts` invokes `metaTemplateManagementService.processDueRegistrations`. The matching Blueprint command is `npm run start:messaging-worker`. Adapter `src/services/meta-template-management/meta-graph.adapter.ts` reads `META_APP_ID`, validates 1–32 numeric digits, and rejects missing/invalid values before IMAGE sample upload. No Background source edited. No `render.yaml` exists.

The latest Architect Review is Pending, so there are no Changes Requested items. Source diff self-review confirms only the two allowed service declarations, documentation and focused structural validation changed. No IDs, credentials, env groups, topology, scaling, provider guards, immutable source semantics or generic logging changed. Runtime race/idempotency behavior is unchanged and outside this declaration-only change.

### Validation Results

Passed (exit 0):

- `bash -n tests/validate-render-blueprints.sh tests/validate-render-blueprints-negative.sh`
- `bash tests/validate-render-blueprints.sh`: both canonical Blueprints pass YAML and existing topology/secret-wiring assertions.
- `NEGATIVE_CASE_FILTER=messaging_meta_app bash tests/validate-render-blueprints-negative.sh`: all 10 focused adversarial fixtures rejected.
- `git diff --check`; source diff/privacy review; implementation worktree clean after commit.

During test development the initial full negative run stopped on fixture expected-message mismatches for existing early duplicate/group guards. Expectations were corrected; all final scoped fixtures passed. Full unrelated negative suite not claimed. Repository has no `package.json`; no npm lint/check script invented. No app tests, Docker suites, deployments, provider requests or live Render mutation performed. Live validation remains coordinator/developer owned.

Physical isolation (launcher packet): canonical root `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-075-GATEWAY-001`; implementation `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-075-GATEWAY-001`; both branches `task/ARCH-075-GATEWAY-001`. Shared/default checkouts and other worktrees were not switched or modified. Both remote task branch fast-forwards were `not-needed`; both origin/main incorporations `already-current`. Recursive submodule sync/update passed; implementation has no submodule entries. Durable launcher claim `2f46fb1dc34b76d1f19b0983068af5a181c81083` retained without re-claiming.

### Deviations

The architect amended the target to messaging workers after concrete runtime evidence. Initial merchant-communications draft was corrected before publication; no declaration remains there.

### Assumptions

Operators supply the existing environment-appropriate provider app identity securely. Capacity and costs are unchanged; no capacity claim made.

### Unresolved Issues

Existing BLOCKED preclaim rows require the Background-owned lifecycle correction and validation; environment declaration alone does not recover them. No direct database repair attempted.

### Architectural Concerns

Original worker ownership mismatch was escalated and resolved through the coordinator amendment. No remaining scope conflict.

## Architect Review

### Review Status

Pending

### Review Notes

Pending implementation.

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

None
