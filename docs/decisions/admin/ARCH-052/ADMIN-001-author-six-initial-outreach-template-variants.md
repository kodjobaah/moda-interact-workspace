---
id: ARCH-052-ADMIN-001
architecture_id: ARCH-052
title: Author and publish the six existing recovery purposes with basket copy
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
enables:
- ARCH-052-BACKGROUND-008
- ARCH-052-SYSTEM-TEST-001
- ARCH-052-SYSTEM-TEST-002
created: '2026-10-29'
updated: '2026-10-29'
---

# ARCH-052-ADMIN-001: Author and publish the six existing recovery purposes with basket copy

## Architecture

Architecture ID: `ARCH-052`.

Architecture document: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`.

Coordinator: `moda_architect`. This is a **portable canonical definition — defined but not materialised**. No developer Git branch/worktree, commit or push is asserted.

## Objective

Extend Admin-owned immutable WhatsApp template authoring to support the approved basket-summary variable and copy for no offer, code and automatic offer.

## Context

ARCH-047 already owns English AST authoring/translation/Meta submission/publication and six INITIAL/FOLLOW_UP × offer-purpose slots. Do not create a second merchant template editor.

Evidence and paths refer to the 29 October 2026 08:07 uploaded workspace snapshot; implementation must re-read current task/code before claiming.

## Scope

- Extend `src/lib/admin/whatsapp-templates/authoring/registry.ts`, `types.ts` and validation/compiler bindings to consume the Shared new checkout summary key.
- Provide Admin-authored starter copy for three INITIAL purposes while preserving six total slots and per-language independent approval. Include optional `shop.categoryName` in category-aware variants, with separately approved category-free variants.
- Require CODE_OFFER to have verified offer.code/description and AUTOMATIC_OFFER to have verified description but no invented coupon code; NO_OFFER must never include offer bindings.
- Keep exact immutable `parameterBindingsSnapshot`, registration digest and provider-approval lifecycle; no automatic publication from merely saving an AST.

## Out of Scope

- No new merchant template authoring, provider discount lookup, Admin media processing, changes to follow-up wording unless necessary for compatibility.

No out-of-repository modifications, new competing generic logger, uncapped provider operations, or implementation of Enables tasks.

## Requirements

- Meta template preview must be illustrative, but live variables must have proven Background resolver sources; no unbound placeholders.
- Translation tokens remain protected; require approval/publishing per shop/WABA/language.
- Review `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, and task preparation packet. Use dedicated mirrored task worktrees, correct start-of-attempt synchronization, and record both histories.
- Use `@modainteract/moda-interact-shared/logging` for new Node runtime logs. Unexpected exceptions must be logged with bounded, non-sensitive context and propagated to the owning retry/failure boundary; avoid silent catch. Plugin PHP must reuse its existing bounded operational logger.
- Do not send raw checkout URLs, bearer tokens, customer personal data or untrusted media source URLs to logs/telemetry.
- Provider mutation is prohibited except the customer-initiated Woo cart restoration explicitly owned by WOOCOMMERCE-002.

## Work Items

- [ ] Add basket summary to registry, AST and compiler validation.
- [ ] Create safe six-purpose/three INITIAL starter examples and variant eligibility rules.
- [ ] Test translation/fingerprint and Admin publication compatibility.

## Interfaces / Contracts

- Shared semantic key registry and existing ARCH-047 Admin AST, frozen positional binding and Meta registration contract.

## Dependencies

- `ARCH-052-SHARED-003` — new ARCH-052 prerequisite (not yet materialised).

All dependencies must be `status: complete` in the authoritative individual task YAML immediately before launcher preparation; architect acceptance or Ready alone is insufficient. No non-system-test task depends on a system-test task.

## Enables

- `ARCH-052-BACKGROUND-008`
- `ARCH-052-SYSTEM-TEST-001`
- `ARCH-052-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] All INITIAL NO/CODE/AUTOMATIC templates can be authored and previewed without changing ARCH-047 immutability.
- [ ] Invalid body/header bindings and missing locale/category are handled safely.

## Validation

- [ ] Admin authoring/compiler/publishing/translation unit tests and approved template snapshots.
- [ ] Admin typecheck/lint/tests and `git diff --check`.

Use actual repository scripts rather than assuming uniform `npm` commands; record required integration harness/environment gaps without claiming unrun tests passed.

## Stop Condition

After all Work Items, Acceptance Criteria and required Validation pass, complete the report, set task `status: review`, hand the implementation branch and parent task report to `moda_architect` and **STOP**. Do not begin a dependent task, merge, push main, or edit architecture indexes as a repository agent.

## Implementation Notes

**Expected owning repository locations (verify paths in the execution worktree; create proposed paths only if appropriate):**

- `moda-interact-admin/src/lib/admin/whatsapp-templates/authoring/registry.ts`
- `moda-interact-admin/src/lib/admin/whatsapp-templates/authoring/types.ts`
- `moda-interact-admin/src/lib/admin/whatsapp-templates/authoring/validation.ts`
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
