---
id: ARCH-036-SHARED-001
architecture_id: ARCH-036
title: "Define versioned Woo coupon read-page contract"
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: ready
priority: 10
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables: ["ARCH-036-SHARED-003"]
created: 2026-10-12
updated: 2026-10-12
---
# ARCH-036-SHARED-001 — Define versioned Woo coupon read-page contract

## Architecture

- Architecture: `ARCH-036` — `docs/architecture/ARCH-036-shared-commerce-discount-catalogue.md`.
- Coordinator: `moda_architect`; owner: `moda_shared` / `moda-interact-shared`.
- **Defined but not materialised.** No task branch, dedicated worktree, implementation commit or push has been created.

## Objective

Define the **small cross-service read-page contract** between API-owned WooCommerce REST access and the Background catalogue synchroniser, without database changes.

## Context

API-001 provides bounded Woo `wc/v3/coupons` pages through the approved Woo read grant; BACKGROUND-001 must validate their shape. These two separately deployed services consume a published runtime contract. This task does not define selection storage or create any new provider identity columns.

## Scope

Define `woo.coupons.read-page.v1` request/result schema with authenticated Shop correlation (not credentials), bounded pagination metadata, immutable Woo numeric ID, mutable coupon code, type/amount/expiry/status/restriction summary, and typed errors. `providerStatus` normalisation is Background-owned; `isAvailable` is **not** a provider field and MUST NOT be present as a provider-derived availability indicator.

## Out of Scope

No WordPress PHP upload payload, sync start/page/complete token, Shopify event contract changes, new discount table, credential grant, HTTP routing, provider SDK or implementation in API/Background.

## Requirements

- Coupon pagination is bounded; provider offsets/totals must not be fabricated, and incomplete/unstable enumeration is a failure, not an empty catalogue.
- Woo provider coupon IDs are positive stable integers; adapter key `woo:coupon:<id>` is computed by Background into existing `shopifyDiscountNodeId`.
- Types/rules cannot claim checkout-level eligibility from catalogue listing alone. Do not expose Woo API credentials, customer email allowlists or unbounded provider payloads.
- Do not modify existing Shopify event/recovery-policy schema exports.

## Work Items

- [ ] Define runtime-validatable read-page request, response and error schema.
- [ ] Include bounded amount/expiry/restriction metadata and pagination-total test vectors.
- [ ] Test empty, changing pages, revoked read grant, malformed identities and privacy.
- [ ] Document API producer and Background consumer with exact version and publication dependency.

## Interfaces / Contracts

Published `@modainteract/moda-interact-shared` coupon read-page schema consumed by API-001 and BACKGROUND-001; WP plugin does not publish/consume this private port.

## Dependencies

None.

## Enables

- `ARCH-036-SHARED-003`

## Acceptance Criteria

- [ ] Both API and Background validate the same schema without divergent local copies.
- [ ] No selection flags, fake provider availability or database migration included.
- [ ] Invalid/incomplete pagination fails closed.

## Validation

- [ ] Shared focused contract validators and negative cases.
- [ ] Declared package lint, typecheck and build.
- [ ] `git diff --check`.

## Stop Condition

After bounded work, acceptance checks and required validation: document the Completion Report, set the task to `review` and STOP. Do not begin dependent tasks. For `superseded` tasks, do not execute or claim.

## Implementation Notes

Use a bounded API-owned private read adapter. Background controls catalogue `syncGeneration` and `activeSyncToken`; they do not belong in the provider page schema.

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
