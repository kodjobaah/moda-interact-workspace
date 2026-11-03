---
id: ARCH-052-COMMERCE-005
architecture_id: ARCH-052
title: Publish approved version-2 discount MCP capabilities in TEST
task_kind: publication
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: superseded
priority: 45
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables: []
created: 2026-10-29
updated: 2026-10-29
---

# ARCH-052-COMMERCE-005: Publish approved version-2 discount MCP capabilities in TEST

## Architecture

Architecture ID: `ARCH-052`.

Architecture document: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`.

Coordinator: `moda_architect`. **Portable definition, not materialised**; no local branch, commit, worktree or remote action has been created. Developer execution and explicit completion are required for the privileged release action.

## Objective

**Superseded without implementation.** No Commerce Studio publication is required for the built-in discount tools. COMMERCE-006/007 cover only automatic publication of product search and exact-product tools.

## Context

`moda-interact-commerce/src/commerce/publication/lifecycle.ts` provides the existing privileged `publishToolRevision`, `createRelease`/`createSuccessorRelease`, `activateRelease` and release pointer controls. `publishToolRevision` validates `registry.isAvailable(definition)`, which requires the MCP executor to be registered and reviewed before this task. COMMERCE-004 owns authoring implementation and MCP-002 owns executable handler implementation; this task is **publication only**.

## Scope

No implementation. Do not claim, materialise, modify repository code or attempt publication under this task.

## Out of Scope

- No new source behaviour, schema, migration, tests, refactors, build, typecheck, lint, general release tooling, new tooling/credentials or activation in PRODUCTION.

## Requirements

The replacement tasks and parent architecture are authoritative. Historical wording in this superseded task is retained solely for audit; it must not govern an implementation.

## Work Items

- [x] Marked superseded in the architecture plan. No code executed.

## Interfaces / Contracts

None — see replacement tasks.

## Dependencies

None — task is superseded.

## Enables

None — task is superseded.

## Acceptance Criteria

- [x] Superseded without implementation. The replacement tasks are explicitly identified.

## Validation

Not applicable; no implementation permitted.

## Stop Condition

After publication-only Work Items and checks, fill the Completion Report, set task to `review`, submit for architectural acceptance, and **STOP**. `completion_mode: developer` requires the developer to explicitly mark Complete via `/moda_developer_update ARCH-052-COMMERCE-005 complete` after Accepted review; no downstream task becomes Ready before actual Complete.

## Implementation Notes

No implementation. Replacement: No Commerce Studio publication is required for the built-in discount tools. COMMERCE-006/007 cover only automatic publication of product search and exact-product tools.

## Completion Report

### Status

Not Started. Developer release gate.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

The TEST environment has an authorised `SUPER_ADMIN` and its current immutable release metadata can be read through approved operations.

### Unresolved Issues

None reported.

### Architectural Concerns

Report conflicts or missing registry support to `moda_architect`; do not bypass publication gates.

## Architect Review

### Review Status

Pending.

### Review Notes

Publication-only task definition; no release performed.

### Reviewed Files

Source-level publication lifecycle API and current task definition only.

### Validation Reviewed

None for publication.

### Architecture Conformance

Pending publication and explicit developer completion.

### Follow-up

After accepted publication, the developer must explicitly mark Complete before Background-010 is eligible.
