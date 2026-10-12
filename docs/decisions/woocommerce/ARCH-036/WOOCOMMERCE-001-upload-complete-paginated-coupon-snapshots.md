---
id: ARCH-036-WOOCOMMERCE-001
architecture_id: ARCH-036
title: "Superseded — Woo coupon snapshot uploader not required"
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: superseded
priority: 40
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables: []
created: 2026-10-12
updated: 2026-10-12
---
# ARCH-036-WOOCOMMERCE-001 — Superseded — Woo coupon snapshot uploader not required

## Architecture

- Architecture: `ARCH-036` — `docs/architecture/ARCH-036-shared-commerce-discount-catalogue.md`.
- Coordinator: `moda_architect`; owner: `moda_woocommerce` / `moda-interact-woocommerce`.
- **Defined but not materialised.** No task branch, dedicated worktree, implementation commit or push has been created.

## Objective

Archive the previously defined WooCommerce plugin-driven coupon synchronisation work; it must not be executed.

## Context


ARCH-036 now uses direct Background reads of WooCommerce REST coupons with its authorised, encrypted Woo read grant. No coupon upload flow, Action Scheduler sync job, WordPress coupon hook producer or API proxy is required.

## Scope

Documentation-only supersession. Preserve the already implemented ARCH-035 native Woo coupon-preview REST route as a read-only merchant UI feature.

## Out of Scope

No plugin snapshot push, Action Scheduler sync, coupon lifecycle hook, inbound batch API, background job or new local storage.

## Requirements


Do not claim or implement. `ARCH-036-BACKGROUND-001` owns periodic bounded coupon fetching and catalogue reconciliation. `ARCH-036-BACKGROUND-003` owns live read/eligibility at send time. The Woo plugin retains the normal merchant-facing UI and its existing read access / connection flows.

## Work Items

- [x] Supersede the old plugin push workstream.
- [x] Remove all downstream task dependencies on this superseded task.

## Interfaces / Contracts


None — superseded. No plugin push event or payload contract.

## Dependencies

None.

## Enables

None.

## Acceptance Criteria

- [x] No new WordPress coupon synchronisation mechanism is required.
- [x] Background and API boundaries own provider fetches.

## Validation

Documentation/dependency check only.

## Stop Condition

After bounded work, acceptance checks and required validation: document the Completion Report, set the task to `review` and STOP. Do not begin dependent tasks. For `superseded` tasks, do not execute or claim.

## Implementation Notes

Historical task file retained solely to explain supersession.

For developer execution, materialise/prepare the canonical `task/<TASK_ID>` parent and implementation worktrees through `/moda_developer_create`; for agent execution use `/moda-task`. Record launcher-resolved paths, start-of-attempt sync, recursive submodule evidence, branch/commit and actual test results. Do not edit shared/default checkouts or domain `_index.md` files.

## Completion Report

### Status

Not Started.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run; task not claimed.

### Deviations

None.

### Assumptions

The executor will verify checkout, actual dependencies, task worktrees and available toolchain at claim time.

### Unresolved Issues

None recorded.

### Architectural Concerns

Stop and return cross-repository, credential, provider compatibility or schema deviations to `moda_architect`.

## Architect Review

### Review Status

Pending.

### Review Notes

Portable revised definition; no implementation submitted or accepted.

### Reviewed Files

Source snapshot and task contract only. No execution files reviewed.

### Validation Reviewed

No implementation tests have run as part of this definition.

### Architecture Conformance

To be determined after implementation review.

### Follow-up

Await real task materialisation, execution, Completion Report and Architect review.
