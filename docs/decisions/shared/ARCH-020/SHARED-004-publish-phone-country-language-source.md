---
id: ARCH-020-SHARED-004
architecture_id: ARCH-020
title: Add and publish phone-country language provenance
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 25
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-020-SHARED-001
enables:
  - ARCH-020-BACKGROUND-001
  - ARCH-020-COMMERCE-012
  - ARCH-020-SYSTEM-TEST-001
created: 2026-09-20
updated: 2026-09-20
---

# Add and publish phone-country language provenance

## Architecture

ARCH-020. Read [implementation contracts C6.2/C6.3](../../../architecture/ARCH-020-implementation-contracts.md) and BACKGROUND-001 A1/A2. Coordinator: moda_architect.

## Objective

Provide truthful phone-country language provenance for the expanded recovery path.

## Context

New user scope, not a defect in previously accepted work. Preserve accepted ARCH-020-SHARED-001 history. This narrowly scoped task may run independently of the other new provenance task; Background emission waits for both.

## Scope

moda-interact-shared implementation, focused tests and required artifact delivery only.

## Out of Scope

Other repository code, phone-country mapping policy, new customer-preference settings, transcription/provider changes, production rollout, automatic downstream execution and destructive migration.

## Requirements

Use exact wire phone-country / persisted PHONE_COUNTRY spelling in the owning layer. Do not masquerade as detected, shopify, merchant-default or customer-explicit. Unknown values remain rejected. Preserve old reader compatibility until consumers are updated; additive schema acceptance does not authorize premature emission.

## Work Items

Extend the existing LanguageSourceSchema/type with exactly phone-country. Carry that value through existing internationalization context and Commerce runner input validation without treating it as customer-explicit or detected speech. Preserve all existing values, strict schemas, grounding and response contracts. Do not add a second enum/validator, phone parsing, country mapping or Prisma dependencies.

Update every affected exhaustive internal source mapping/fixture. Publish one new compatible package version through the existing release mechanism; do not overwrite 0.13.1. Record source SHA, registry version, tarball integrity and exports. No independent publication task is needed.

## Interfaces / Contracts

Wire: phone-country. Prisma/PostgreSQL: PHONE_COUNTRY. Background owns the two-way mapping and C6.2 initial selection; its task must consume both accepted artifacts. Gateway configuration has no reverse dependency on these tasks.

## Dependencies

- ARCH-020-SHARED-001

Accepted Complete in canonical records. Use its actual integrated/published source. Normal launcher must verify physical worktree and source availability before claim.

## Enables

- ARCH-020-BACKGROUND-001
- ARCH-020-COMMERCE-012
- ARCH-020-SYSTEM-TEST-001

## Acceptance Criteria

- [ ] Exact new value is supported with unchanged legacy meanings and strict rejection of unknown values.
- [ ] Required tests and artifact delivery below are evidenced with commands, versions/SHAs and actual results.
- [ ] No other repository changed and no new phone-country value emitted by this task.

## Validation

Test phone-country acceptance in internationalization and Commerce runner context, all legacy sources, rejection of unknown spellings, and continued precedence of substantive detected language over a phone-derived initial hint. Validate affected tests/typecheck/build using declared scripts. Install the exact published version in a clean temporary consumer and import internationalization, commerce and commerce/runner; validate a phone-country context with no provider/database credentials. Packing alone is insufficient.

## Stop Condition

Publish task-owned implementation/report branches and submit for architect acceptance. Do not self-complete or start Background/system tests. Keep pending developer-owned validation explicit.

## Implementation Notes

Use normal moda-task preparation and dedicated mirrored worktrees, repository-local instructions and workspace VCS/validation policies. Definition is published on main under the user's established authoring exception; this does not authorize implementation on main. Readiness is not an execution claim.

## Completion Report

Not Started. No implementation or tests claimed. Record exact source/artifact availability before acceptance.

## Architect Review

Ready for execution: prerequisite accepted; this is a new scope addition. No attempt claimed. Background remains in Review until both new tasks are accepted and their artifacts are available.
