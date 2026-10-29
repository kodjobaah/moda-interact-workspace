---
id: ARCH-052-BACKGROUND-007
architecture_id: ARCH-052
title: Normalize and cache optional checkout-product IMAGE header
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 45
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-052-DATABASE-002
- ARCH-052-SHARED-003
- ARCH-052-COMMERCE-002
- ARCH-049-BACKGROUND-001
- ARCH-049-BACKGROUND-002
- ARCH-049-BACKGROUND-004
enables:
- ARCH-052-BACKGROUND-008
created: '2026-10-29'
updated: '2026-10-29'
---

# ARCH-052-BACKGROUND-007: Normalize and cache optional checkout-product IMAGE header

## Architecture

Architecture ID: `ARCH-052`.

Architecture document: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`.

Coordinator: `moda_architect`. This is a **portable canonical definition — defined but not materialised**. No developer Git branch/worktree, commit or push is asserted.

## Objective

Select and safely convert at most one actual checkout-product image into a durable READY R2 derivative consumed by the frozen Meta IMAGE header.

## Context

ARCH-049 has safe image fetch/transform/R2 primitives for ShopBrand; that state is brand-specific. A checkout product image must use the exact checkout product/variant ID and its own durable lifecycle.

Evidence and paths refer to the 29 October 2026 08:07 uploaded workspace snapshot; implementation must re-read current task/code before claiming.

## Scope

- Add focused recovery-product-media processor/repository using DB002; select first present purchasable line with an exact product/variant image, bounded to a few provider reads, and store one source-generation association.
- For Shopify, consume COMMERCE002 image-source port. For Woo, reuse existing authenticated Woo read grant and WC REST exact product/variation image source (do not invent plugin-side duplication).
- Reuse inspected ARCH-049 secure fetch/redirect/DNS/peer safety, image transform, MIME/dimension/size validation and Cloudflare R2 writer mechanisms, extracting only genuinely shared mechanics instead of copying a brand-only service.
- Resolve READY HTTPS derivative with exact shop/recovery/source/version and approved R2 host; no external network fetch, resize or upload in final send transaction or immediately inside the provider call.
- On missing, unsafe, expired, stale or unavailable image, return typed absent; allow a separately approved text/ShopBrand-header template fallback. Never block essential no-discount text outreach solely for an optional product photo.

## Out of Scope

- No editing existing ARCH-049 brand role semantics, merchant AST compiler, real-time per-send arbitrary image fetch or unbounded media retention.

No out-of-repository modifications, new competing generic logger, uncapped provider operations, or implementation of Enables tasks.

## Requirements

- Per-recovery media generation fencing, idempotent retry/cleanup and bounded worker concurrency/cost.
- Retain customer consent/STOP gates even when media was prepared early; no image may cause an unauthorised send.
- Review `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, and task preparation packet. Use dedicated mirrored task worktrees, correct start-of-attempt synchronization, and record both histories.
- Use `@modainteract/moda-interact-shared/logging` for new Node runtime logs. Unexpected exceptions must be logged with bounded, non-sensitive context and propagated to the owning retry/failure boundary; avoid silent catch. Plugin PHP must reuse its existing bounded operational logger.
- Do not send raw checkout URLs, bearer tokens, customer personal data or untrusted media source URLs to logs/telemetry.
- Provider mutation is prohibited except the customer-initiated Woo cart restoration explicitly owned by WOOCOMMERCE-002.

## Work Items

- [ ] Implement exact-item source readers and media lifecycle processor.
- [ ] Reuse safe R2 mechanisms and export READY image resolver for template preparer.
- [ ] Test media races, origin attacks, absent image and approved-header fallback.

## Interfaces / Contracts

- DB002 `CheckoutRecoveryProductMedia`; Shared IMAGE header role `CHECKOUT_PRODUCT`; existing ARCH-049 verified R2 media primitives, new Background resolver adapter.

## Dependencies

- `ARCH-052-DATABASE-002` — new ARCH-052 prerequisite (not yet materialised).
- `ARCH-052-SHARED-003` — new ARCH-052 prerequisite (not yet materialised).
- `ARCH-052-COMMERCE-002` — new ARCH-052 prerequisite (not yet materialised).
- `ARCH-049-BACKGROUND-001` — Complete in 29 October snapshot.
- `ARCH-049-BACKGROUND-002` — Complete in 29 October snapshot.
- `ARCH-049-BACKGROUND-004` — not Complete in 29 October snapshot.

All dependencies must be `status: complete` in the authoritative individual task YAML immediately before launcher preparation; architect acceptance or Ready alone is insufficient. No non-system-test task depends on a system-test task.

## Enables

- `ARCH-052-BACKGROUND-008`

## Acceptance Criteria

- [ ] No cross-tenant or stale product image; no Meta IMAGE header uses a raw Shopify/Woo source URL.
- [ ] Missing picture falls back to approved text/header path rather than preventing NO_OFFER outreach.
- [ ] No network I/O inside final DB permit transaction.

## Validation

- [ ] Focused Background media processing tests with R2/provider simulators.
- [ ] PostgreSQL race/retention tests, final-template IMAGE parameter and text regression tests.
- [ ] Background build/lint and `git diff --check`.

Use actual repository scripts rather than assuming uniform `npm` commands; record required integration harness/environment gaps without claiming unrun tests passed.

## Stop Condition

After all Work Items, Acceptance Criteria and required Validation pass, complete the report, set task `status: review`, hand the implementation branch and parent task report to `moda_architect` and **STOP**. Do not begin a dependent task, merge, push main, or edit architecture indexes as a repository agent.

## Implementation Notes

**Expected owning repository locations (verify paths in the execution worktree; create proposed paths only if appropriate):**

- `moda-interact-background/src/services/shop-brand-media/ (reuse primitives only)`
- `moda-interact-background/src/services/recovery-product-media/ (new)`
- `moda-interact-background/src/services/recovery-template-preparation/`
- `moda-interact-background/tests/integration/`

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
