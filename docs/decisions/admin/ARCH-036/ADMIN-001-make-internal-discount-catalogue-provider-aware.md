---
id: ARCH-036-ADMIN-001
architecture_id: ARCH-036
title: Show provider-aware discount provenance in Moda Admin
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: pending
priority: 60
executor: null
claimed_at: null
attempt: 0
depends_on: ["ARCH-036-DATABASE-001", "ARCH-036-BACKGROUND-001", "ARCH-036-API-001"]
enables: ["ARCH-036-SYSTEM-TEST-001"]
created: 2026-10-12
updated: 2026-10-12
---

# ARCH-036-ADMIN-001 — Show provider-aware discount provenance in Moda Admin

## Architecture

- Architecture ID: `ARCH-036`.
- Parent: `docs/architecture/ARCH-036-shared-commerce-discount-catalogue.md`.
- Coordinator: `moda_architect`.
- Portable canonical task definition; **defined but not materialised**. No Git branch, worktree, commit or push has been made.

## Objective

Ensure the internal Admin recovery-policy view shows Woo coupon catalogue state instead of Shopify-only discount controls.

## Context

The user showed a Woo shop on Moda Admin whose Recovery Settings still contained `Shopify discount catalogue` and `Sync now`. Those controls are provider-specific and should not be offered for Woo stores.

## Scope

In the internal Admin UI, show neutral catalogue status, provider, generation/freshness, coupon availability and effective selected mode. Preserve Shopify sync action only for Shopify shops; Woo uses plugin-push sync and exposes read-only freshness/reconnect guidance. Reuse existing Admin components and Shop.platform.

## Out of Scope

- No new PostgreSQL discount/coupon catalogue, selection, sync staging or join **tables**; reuse existing physical `ShopifyDiscountCatalogue`, `ShopifyDiscount`, policy and attempt records.
- No other repository's implementation, incidental feature work, migration-history rewrite, or `_index.md` modification.
- No new unsupported coupon promises, billing changes or checkout mutation.
- No implementation of tasks listed under Enables; return to the architect at the defined stop point.

## Requirements

Do not let the Admin UI invoke Shopify GraphQL sync for a Woo merchant. Admin override data and selected coupon set must use existing authorized policy override; sensitive raw provider snapshots and secrets remain hidden. Show correct stale/revoked/failure badges and no fabricated current state.

## Work Items

- [ ] Branch existing discount provenance UI by provider using shared catalogue read.
- [ ] Hide/disable Shopify-only actions on Woo shops and show Woo sync freshness.
- [ ] Test Shopify and Woo tabs, admin authorization and empty/stale states.

## Interfaces / Contracts

Existing Admin merchant recovery policy tab and mapped catalogue DB rows; `Shop.platform`; no new admin telemetry or REST write mechanism.

## Dependencies

- `ARCH-036-DATABASE-001`
- `ARCH-036-BACKGROUND-001`
- `ARCH-036-API-001`

## Enables

- `ARCH-036-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Woo merchant page never calls Shopify sync and does not claim Shopify coupon compatibility.
- [ ] Shopify merchant page remains unchanged in behaviour.
- [ ] Admin effective/merchant provenance correctly distinguishes overrides and provider.
- [ ] Tenant/auth restrictions and no secrets in markup.

## Validation

- [ ] Admin recovery-policy UI tests and provider branching assertions
- [ ] Declared Admin lint/typecheck/build and `git diff --check`

## Implementation Notes

Do not change the Shopify sync worker or Woo plugin from Admin.

For developer execution, use the canonical `/moda_developer_create ARCH-036-ADMIN-001` preparation/worktree process once the task is materialised and Ready. For agent execution use `/moda-task ARCH-036-ADMIN-001`. Do not implement from a shared checkout merely because the patch can be applied there. Validate using the repository's **actual** `package.json`/tooling and record launcher-resolved physical parent and implementation worktrees, start-of-attempt sync/submodules, branch/commit and test evidence. Never accept an unverified claim of test success.

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

The implementation executor will verify local checkout, dependencies and available toolchain at claim time.

### Unresolved Issues

None recorded by an implementation executor.

### Architectural Concerns

Report schema, cross-service or provider-proof deviations to `moda_architect` instead of silently expanding scope.

## Architect Review

### Review Status

Pending.

### Review Notes

Portable definition only, not implementation acceptance.

### Reviewed Files

Current 12 October 2026 source snapshot used to define ownership; implementation not yet reviewed.

### Validation Reviewed

None from this task.

### Architecture Conformance

To be determined after implementation inspection.

### Follow-up

Await canonical materialisation, execution and review.
