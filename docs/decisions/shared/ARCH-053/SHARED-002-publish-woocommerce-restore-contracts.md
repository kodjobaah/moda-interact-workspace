---
id: ARCH-053-SHARED-002
architecture_id: ARCH-053
title: Publish accepted Woo restoration contracts
task_kind: publication
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 25
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-053-SHARED-001
- ARCH-053-SHARED-003
- ARCH-053-SHARED-003
enables:
- ARCH-053-API-001
- ARCH-053-API-002
- ARCH-053-BACKGROUND-001
- ARCH-053-API-003
- ARCH-053-API-003
created: 2026-10-29
updated: 2026-10-30
---

# ARCH-053-SHARED-002 — Publish accepted Woo restoration contracts

## Architecture

Architecture ID: `ARCH-053`. Document: `docs/architecture/ARCH-053-woocommerce-checkout-recovery-links-and-cart-restoration.md`. Coordinator: `moda_architect`. **Portable canonical task: defined but not materialised**; no Git branch, worktree, commit, push, review or producer deployment claimed.

## Objective

Publish accepted Woo restoration contracts. One bounded outcome in `moda-interact-shared` owned by `moda_shared`.

## Context

The uploaded workspace snapshot is dated 2026-10-29. ARCH-052 owns dynamic discount discovery and must not be used for these checkout-URL changes. An ARCH-048 next-generation dependency exists only as a separate *portable* proposal until accepted/materialised. This task is **Pending** from the snapshot/dependency inventory, subject to fresh launcher re-gating.

## Scope

- Version and publish ONLY the accepted Shared package implementing **both** `ARCH-053-SHARED-001` and `ARCH-053-SHARED-003` to the already approved registry; record exact version, tag and registry evidence.
- Limit changed files to authorised release metadata and lockfile updates mechanically required by publication.

## Out of Scope

No new source changes, revalidation tests or API/Background integration.

No execution of Enabled tasks, unrelated cross-repository implementation, extra database objects or new generic logger.

## Requirements

- Verify **SHARED-001 and SHARED-003** are each architect-accepted Complete and published artifact contains the exact `@modainteract/moda-interact-shared/woocommerce` **v1 and v2** exports, plus both published JSON fixture subpaths; leave downstream consumption to separately assigned owners.
- Publication-only work: do not rerun tests, lint, build or alter runtime implementation already validated in SHARED-001. If publishing reveals a code defect, stop and return it to architect.

### Mandatory workflow/security invariants

- Inspect `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, `docs/developer-task-workflow.md`, `docs/task-definition-materialization.md` and the launcher preparation evidence. Use the **dedicated, synchronized parent and implementation task worktrees**; do not operate from a shared checkout or claim a branch was pushed without evidence. Implement only the owning repository and assigned task metadata. No unrelated refactors, migrations, agent handoffs or remote pushes to `main`.
- Read the ARCH-053 parent architecture and all dependency tasks before claiming Ready. Any missing contract or incorrect owner is a blocking architect question; do not invent a local parallel schema or silently change another agent's task. System-test tasks must remain terminal.
- Never swallow unexpected errors: Node uses `@modainteract/moda-interact-shared/logging`; PHP uses the existing safe plugin diagnostics (not a competing generic Node logger). Report bounded event codes, ids and outcomes, propagate retryable failures to their owning boundary, omit tokens, full URLs, coupon codes and customer personal data from logs.
- The plugin cannot access PostgreSQL/Redis. The API cannot mutate merchant WordPress cart sessions. Background cannot directly call an unverified merchant endpoint to mint URLs. Do not enable Woo production WhatsApp sending, relax final consent/STOP/order gates, or add cross-generation outreach caps/cooldowns.

## Work Items

- [ ] Apply approved package version and publish using existing release workflow.
- [ ] Verify the exact published version exposes **both v1 and v2** types/schemas and fixture paths; record registry evidence.

## Interfaces / Contracts

Entrypoint `@modainteract/moda-interact-shared/woocommerce` with **all** schemas/types accepted in SHARED-001 and SHARED-003: `WooCartRestoreSnapshotV1Schema`, `WooRestoreResolveRequestV1Schema`, `WooRestoreResolveResponseV1Schema`, `WooRestoreOutreachOfferV1Schema`, `WooRestoreResolveOfferRequestV2Schema`, `WooRestoreResolveOfferResponseV2Schema`, and their inferred types. Publish both fixture subpaths `./woocommerce/fixtures` and `./woocommerce/outreach-offer-fixtures`. API and Background pin the published version; no sibling-source import.

## Dependencies

- `ARCH-053-SHARED-001` — accepted base schemas.
- `ARCH-053-SHARED-003` — accepted v2 offer-aware resolver schemas.

## Enables

- `ARCH-053-BACKGROUND-001`
- `ARCH-053-API-001`
- `ARCH-053-API-002`
- `ARCH-053-API-003`
- `ARCH-053-API-003`

## Acceptance Criteria

- [ ] Apply approved package version and publish using existing release workflow.
- [ ] Verify the exact published version exposes **both v1 and v2** types/schemas and fixture paths; record registry evidence.
- [ ] No regression in tenant isolation, historical generation preservation, valid shopper cart or consent/STOP/terminal order guards.
- [ ] No change outside assigned domain repository code plus owned task Completion Report; no ARCH-052 work.

## Validation

- [ ] Both SHARED-001 and SHARED-003 accepted status and intended version recorded
- [ ] Registry visibility and unchanged release-specific code check; `git diff --check`

## Stop Condition

When Work Items, Acceptance Criteria and required Validation are complete, update ONLY this task's authorised execution metadata, checklists and Completion Report, set `status: review` and return to `moda_architect`; **STOP**. Do not begin Enables, merge task branches, push `main` or change Architect Review yourself.

## Implementation Notes

This is a `task_kind: publication` gate for **both** accepted Shared implementations. It must not rerun their tests, lint, typecheck or build. Consumers may only pin/import a registry-visible package version containing both v1 and v2 and both JSON fixtures. If a missing export needs code changes, STOP and return to architect; do not fix source in this publication task. Architect reviews publication evidence only. No consumer is permitted to use unpublished sibling code.

## Completion Report

### Status

Not Started

### Files Changed

None — portable task definition only.

### Work Completed

Not Started.

### Validation Results

Not Run — no implementation claimed.

### Deviations

None.

### Assumptions

Design based on uploaded 2026-10-29 source snapshot; re-check source and prior task acceptance before implementation.

### Unresolved Issues

None asserted as executed; dependencies must be materialised/accepted.

### Architectural Concerns

Return any cross-service schema/provider/transaction concern to `moda_architect` before improvising.

## Architect Review

### Review Status

Pending

### Review Notes

Not Reviewed — task not executed.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

To be assessed after implementation.

### Follow-up

None.
