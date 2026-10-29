---
id: ARCH-052-DATABASE-002
architecture_id: ARCH-052
title: Persist one bounded checkout-product media selection
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 10
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables:
- ARCH-052-BACKGROUND-007
- ARCH-052-SYSTEM-TEST-001
- ARCH-052-SYSTEM-TEST-002
created: '2026-10-29'
updated: '2026-10-29'
---

# ARCH-052-DATABASE-002: Persist one bounded checkout-product media selection

## Architecture

Architecture ID: `ARCH-052`.

Architecture document: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`.

Coordinator: `moda_architect`. This is a **portable canonical definition — defined but not materialised**. No developer Git branch/worktree, commit or push is asserted.

## Objective

Provide durable, tenant-scoped READY product-image metadata for optional WhatsApp initial-outreach image headers.

## Context

CheckoutRecovery.lineItems does not contain product images. ARCH-049 ShopBrand media stores merchant branding, not recovery-item product pictures. Do not overload ShopBrand with checkout-specific assets.

Evidence and paths refer to the 29 October 2026 08:07 uploaded workspace snapshot; implementation must re-read current task/code before claiming.

## Scope

- Add `CheckoutRecoveryProductMedia` with unique `checkoutRecoveryId`, `shopId`, source product/variant identity, source fingerprint, source observed timestamp, lifecycle (`PENDING`, `READY`, `UNAVAILABLE`), READY R2 object key/sha256/MIME/dimensions/bytes, failure-reason code and expiry/cleanup timestamp.
- Use same-shop referential integrity to CheckoutRecovery, enforce one current asset per recovery, bounded indexed lifecycle/expiry reads and transaction-safe generation transitions.
- Create additive Prisma migration and real PostgreSQL tests for stale generations, shop mismatch, READY constraints and cleanup; keep raw merchant image URLs and customer tokens out of publicly readable columns.

## Out of Scope

- No image fetching/processing, WordPress/Shopify product API calls, ShopBrand schema mutation or WhatsApp header compilation.

No out-of-repository modifications, new competing generic logger, uncapped provider operations, or implementation of Enables tasks.

## Requirements

- READY is never inferred from an arbitrary provider image URL; require verified R2 derivative metadata and matching recovery/source generation.
- Expiry/retention policy must ensure product media does not outlive relevant recovery and consent lifecycle; no broad customer-media archive.
- Review `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, and task preparation packet. Use dedicated mirrored task worktrees, correct start-of-attempt synchronization, and record both histories.
- Use `@modainteract/moda-interact-shared/logging` for new Node runtime logs. Unexpected exceptions must be logged with bounded, non-sensitive context and propagated to the owning retry/failure boundary; avoid silent catch. Plugin PHP must reuse its existing bounded operational logger.
- Do not send raw checkout URLs, bearer tokens, customer personal data or untrusted media source URLs to logs/telemetry.
- Provider mutation is prohibited except the customer-initiated Woo cart restoration explicitly owned by WOOCOMMERCE-002.

## Work Items

- [ ] Define shop/recovery-referenced asset lifecycle and SQL constraints.
- [ ] Add migrations and index/cleanup rules.
- [ ] Exercise real transaction and cross-tenant race fixtures.

## Interfaces / Contracts

- `CheckoutRecoveryProductMedia` indexed by `(shopId, checkoutRecoveryId)`; source generation and digest used to reject stale race completions.
- One ready image is optional; no missing-media row may block a text-only recovery.

## Dependencies

None.

All dependencies must be `status: complete` in the authoritative individual task YAML immediately before launcher preparation; architect acceptance or Ready alone is insufficient. No non-system-test task depends on a system-test task.

## Enables

- `ARCH-052-BACKGROUND-007`
- `ARCH-052-SYSTEM-TEST-001`
- `ARCH-052-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] No cross-tenant media association or stale worker overwrite is possible.
- [ ] Only one usable READY media pointer per recovery, with no untrusted source URL as sendable asset.
- [ ] Existing CheckoutRecovery/outreach constraints and ShopBrand pipeline are unchanged.

## Validation

- [ ] Prisma validate/migration and real PostgreSQL media lifecycle tests.
- [ ] Database integration tests for duplicate, stale generation, tenant mismatch and cleanup.
- [ ] `git diff --check`.

Use actual repository scripts rather than assuming uniform `npm` commands; record required integration harness/environment gaps without claiming unrun tests passed.

## Stop Condition

After all Work Items, Acceptance Criteria and required Validation pass, complete the report, set task `status: review`, hand the implementation branch and parent task report to `moda_architect` and **STOP**. Do not begin a dependent task, merge, push main, or edit architecture indexes as a repository agent.

## Implementation Notes

**Expected owning repository locations (verify paths in the execution worktree; create proposed paths only if appropriate):**

- `moda-interact-database/prisma/schema.prisma`
- `moda-interact-database/prisma/migrations/<arch052_media_migration>/migration.sql`

Source ownership is restricted to the assigned repository plus this task file. `moda_architect` owns architectural/dependency/index reconciliation. The implementing agent should stop for an architectural connector/schema gap rather than inventing a cross-repository workaround.

## Completion Report

### Status

Not Started — portable definition, no task claim.

### Files Changed

None yet.

### Work Completed

None yet.

### Validation Results

Not run.

### Deviations

None reported.

### Assumptions

Execution will verify its current workspace, source state, dependency versions and test harness.

### Unresolved Issues

None established by implementation.

### Architectural Concerns

Report discovered cross-repository/credential/provider-proof issues to `moda_architect`.


## Architect Review

### Review Status

Pending.

### Review Notes

Planning only; no source implementation accepted.

### Reviewed Files

The task definition was authored from the 29 October 2026 snapshot; a code implementation has not been reviewed.

### Validation Reviewed

None for implementation.

### Architecture Conformance

To be determined after implementation review.

### Follow-up

Materialise with the canonical task launcher after the planning patch is integrated and dependencies become Complete.
