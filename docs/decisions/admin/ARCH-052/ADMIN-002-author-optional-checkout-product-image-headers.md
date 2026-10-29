---
id: ARCH-052-ADMIN-002
architecture_id: ARCH-052
title: Author optional checkout-product IMAGE headers and approved text fallbacks
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 35
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-052-SHARED-003
- ARCH-049-ADMIN-002
enables:
- ARCH-052-BACKGROUND-008
- ARCH-052-SYSTEM-TEST-001
- ARCH-052-SYSTEM-TEST-002
created: '2026-10-29'
updated: '2026-10-29'
---

# ARCH-052-ADMIN-002: Author optional checkout-product IMAGE headers and approved text fallbacks

## Architecture

Architecture ID: `ARCH-052`.

Architecture document: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`.

Coordinator: `moda_architect`. This is a **portable canonical definition — defined but not materialised**. No developer Git branch/worktree, commit or push is asserted.

## Objective

Enable immutable Admin-authored recovery templates with a frozen CHECKOUT_PRODUCT image header and paired approved text-only fallback.

## Context

ARCH-049 ADMIN002 already adds frozen ShopBrand media roles to Meta template authoring. A checkout product IMAGE role is distinct and optional; Meta approval applies to the exact header family.

Evidence and paths refer to the 29 October 2026 08:07 uploaded workspace snapshot; implementation must re-read current task/code before claiming.

## Scope

- Extend Admin headerMediaRole registry/AST compiler to accept Shared `CHECKOUT_PRODUCT` only for META_RECOVERY IMAGE headers and only when product media is an approved runtime input.
- Preserve existing `LOGO`/`SQUARE_LOGO`/`COVER_IMAGE` roles, immutable frozen projection digest and Meta approval per locale; do not rewrite a registered template.
- Show an illustrative checkout-product photo in preview with explicit sample/no-PHI notice; validate a separate approved TEXT/no-IMAGE fallback assignment for the same initial purpose and language.
- Ensure Admin publication cannot configure a product-image-only live template without a compatible fallback, unless the merchant knowingly accepts a typed no-send state.

## Out of Scope

- No actual Shopify/Woo photo download, R2 processing, Meta sample-media sourcing workaround or live send.

No out-of-repository modifications, new competing generic logger, uncapped provider operations, or implementation of Enables tasks.

## Requirements

- A saved Meta IMAGE header must never be silently converted to TEXT at send; fallback means a separately approved template identity.
- Admin compiler and Background use identical Shared role keys/digest fixtures.
- Review `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, and task preparation packet. Use dedicated mirrored task worktrees, correct start-of-attempt synchronization, and record both histories.
- Use `@modainteract/moda-interact-shared/logging` for new Node runtime logs. Unexpected exceptions must be logged with bounded, non-sensitive context and propagated to the owning retry/failure boundary; avoid silent catch. Plugin PHP must reuse its existing bounded operational logger.
- Do not send raw checkout URLs, bearer tokens, customer personal data or untrusted media source URLs to logs/telemetry.
- Provider mutation is prohibited except the customer-initiated Woo cart restoration explicitly owned by WOOCOMMERCE-002.

## Work Items

- [ ] Implement new header role UI/validation and preview.
- [ ] Add paired variant fallback publication/eligibility contract.
- [ ] Run immutable digest and Meta approval flow regression tests.

## Interfaces / Contracts

- Shared `CHECKOUT_PRODUCT` role and ARCH-049 `headerMediaRole` version-one frozen contract; existing ARCH-047 Admin publish/translation pipeline.

## Dependencies

- `ARCH-052-SHARED-003` — new ARCH-052 prerequisite (not yet materialised).
- `ARCH-049-ADMIN-002` — Complete in 29 October snapshot.

All dependencies must be `status: complete` in the authoritative individual task YAML immediately before launcher preparation; architect acceptance or Ready alone is insufficient. No non-system-test task depends on a system-test task.

## Enables

- `ARCH-052-BACKGROUND-008`
- `ARCH-052-SYSTEM-TEST-001`
- `ARCH-052-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] IMAGE header with product role compiles/reviews/publishes only through Admin.
- [ ] A missing READY product media selects an approved fallback or typed no-send; it never swaps media into an unrelated role.

## Validation

- [ ] Admin authoring/preview, frozen fingerprint and publication regression suites.
- [ ] Admin typecheck/tests/lint and `git diff --check`.

Use actual repository scripts rather than assuming uniform `npm` commands; record required integration harness/environment gaps without claiming unrun tests passed.

## Stop Condition

After all Work Items, Acceptance Criteria and required Validation pass, complete the report, set task `status: review`, hand the implementation branch and parent task report to `moda_architect` and **STOP**. Do not begin a dependent task, merge, push main, or edit architecture indexes as a repository agent.

## Implementation Notes

**Expected owning repository locations (verify paths in the execution worktree; create proposed paths only if appropriate):**

- `moda-interact-admin/src/lib/admin/whatsapp-templates/authoring/`
- `moda-interact-admin/src/lib/admin/whatsapp-templates/media/`
- `moda-interact-admin/src/lib/admin/whatsapp-templates/publishing/`
- `moda-interact-admin/tests/unit/`

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
