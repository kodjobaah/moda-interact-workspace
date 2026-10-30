---
id: ARCH-052-SHARED-003
architecture_id: ARCH-052
title: Publish the accepted initial-outreach contracts (including product search)
task_kind: publication
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-052-SHARED-002
- ARCH-052-SHARED-005
- ARCH-052-SHARED-006
- ARCH-052-SHARED-008
enables:
- ARCH-052-ADMIN-001
- ARCH-052-ADMIN-002
- ARCH-052-BACKGROUND-005
- ARCH-052-BACKGROUND-007
- ARCH-052-BACKGROUND-010
- ARCH-052-COMMERCE-003
- ARCH-052-COMMERCE-006
- ARCH-052-COMMERCE-008
- ARCH-052-GATEWAY-001
- ARCH-052-MCP-001
- ARCH-052-MCP-002
- ARCH-052-MCP-003
- ARCH-052-SYSTEM-TEST-001
- ARCH-052-SYSTEM-TEST-002
- ARCH-052-WOOCOMMERCE-001
created: '2026-10-29'
updated: '2026-10-30'
---

# ARCH-052-SHARED-003: Publish the accepted initial-outreach contracts (including product search)

## Architecture

Architecture ID: `ARCH-052`. Parent: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`. Coordinator: `moda_architect`.

Portable canonical definition: **defined but not materialised**. No real Git worktree, commit, release or publication is asserted.

## Objective

Publish one architect-accepted version of the **four exact structural contract changes** defined in SHARED-002, SHARED-005, SHARED-006 and SHARED-008, without adding new implementation behaviour or rerunning implementation tests.

## Context

Shared owns reusable inter-service data shapes. Admin and Background consume template bindings, MCP and provider adapters consume targeted discount evidence, Background and MCP share the initial-outreach context, and MCP/Commerce consume the extended existing commerce-product schema. Their source implementation must have passed its own tests and architect review **before** this release task starts.

## Scope

- After the four prerequisite tasks have `status: complete` and `Architect Review: Accepted`, publish their accepted Shared package contents using the existing repository's authorised release process.
- Verify the exact released package exposes the unchanged `/commerce` entrypoint with `CommerceOutreachToolContextSchema`, `CommerceProductSaleEvidenceSchema`, existing product/discount tools plus the new `commerce_get_product` members; and new `/recovery-offer-proof` and `/recovery-template-bindings` entrypoints with the names listed below.
- Record the exact version, registry destination, publication command, registry evidence and changed release metadata. Keep implementation source unchanged.

## Out of Scope

- No new application schemas, runtimes, source edits, lint, typecheck, unit/integration tests, new agent code, tool publication, provider calls, database migration or consumer rollout in this publication task.
- Do not publish SHARED-001, SHARED-004 or SHARED-007; all remain superseded.

## Requirements

- The implementation tasks own schema tests, typechecks and builds. Do not perform those again as publication validation. `prepack` run by the package manager as part of an authorised publish is release mechanics, not a mandate to rerun tests.
- Retain the existing generic `CommerceToolResultSchema` and unchanged conversational tool semantics.
- New Zod code remains structural only, with all business authorisation/discount/product/CTA decisions in owning services. No bespoke HMAC or frozen-policy/sent-offer snapshot export.
- Run from the launcher-prepared dedicated mirrored publication task worktree. Never publish from another task worktree or commit implementation code as part of the release.

## Work Items

- [ ] Check `status: complete` and Accepted reviews for SHARED-002/005/006/008.
- [ ] Select approved package version and execute only the authorised release/publish procedure.
- [ ] Confirm that the exact expected version is visible at the registry and package exports resolve.
- [ ] Record release metadata-only diff and Completion Report evidence.

## Interfaces / Contracts

**Published package entrypoints and symbols:**

```typescript
// @modainteract/moda-interact-shared/recovery-template-bindings
RecoveryTemplateSemanticKeySchema;
RecoveryPromotionTargetSchema;
RecoveryTemplateHeaderMediaRoleSchema;
RecoveryTemplateTextBindingSchema;
RecoveryTemplateUrlButtonBindingSchema;
RecoveryTemplateFrozenBindingsSchema;

// @modainteract/moda-interact-shared/recovery-offer-proof
RecoveryDiscountTargetSchema;
RecoveryDiscountProofRequestSchema;
RecoveryEligibleDiscountProofSchema;
RecoveryNonEligibleDiscountProofSchema;
RecoveryDiscountProofResultSchema;

// @modainteract/moda-interact-shared/commerce
CommerceOutreachToolContextSchema;
CommerceProductSaleEvidenceSchema;
CommerceProductSchema;
CommerceToolInputs.commerce_search_products;
CommerceToolOutputs.commerce_search_products;
CommerceToolInputs.commerce_get_product;
CommerceToolOutputs.commerce_get_product;
CommerceToolResultSchema;
commerceToolResultSchema;
```

The dotted members above are runtime object members, not independent ESM named exports. The corresponding inferred TypeScript types must be included in package declaration output. Do not introduce an `OutreachToolResult` or `OutreachPromotionChoiceSchema` Shared export.

**The two new public export entries must be exactly:**

```json
{
  "./recovery-template-bindings": {
    "types": "./dist/recovery-template-bindings.d.ts",
    "import": "./dist/recovery-template-bindings.js"
  },
  "./recovery-offer-proof": {
    "types": "./dist/recovery-offer-proof.d.ts",
    "import": "./dist/recovery-offer-proof.js"
  }
}
```

This JSON fragment is an addition to the existing `package.json` `exports` object, not a replacement for the whole object. `/commerce` already exists and must remain unchanged as a package path.

## Dependencies

- `ARCH-052-SHARED-002` — Complete and architect-accepted.
- `ARCH-052-SHARED-005` — Complete and architect-accepted.
- `ARCH-052-SHARED-006` — Complete and architect-accepted.
- `ARCH-052-SHARED-008` — Complete and architect-accepted.

## Enables

- `ARCH-052-ADMIN-001`
- `ARCH-052-ADMIN-002`
- `ARCH-052-BACKGROUND-005`
- `ARCH-052-BACKGROUND-007`
- `ARCH-052-BACKGROUND-010`
- `ARCH-052-COMMERCE-003`
- `ARCH-052-COMMERCE-006`
- `ARCH-052-COMMERCE-008`
- `ARCH-052-GATEWAY-001`
- `ARCH-052-MCP-001`
- `ARCH-052-MCP-002`
- `ARCH-052-MCP-003`
- `ARCH-052-SYSTEM-TEST-001`
- `ARCH-052-SYSTEM-TEST-002`
- `ARCH-052-WOOCOMMERCE-001`

## Acceptance Criteria

- [ ] The package version contains precisely the four accepted Shared changes and retains all existing unrelated exports.
- [ ] All listed package paths and runtime symbols/types are present in the published version.
- [ ] Only authorised release metadata/lockfile updates occurred; no source code modifications or consumer integration.
- [ ] Registry visibility and actual version are recorded; publication failure or an implementation bug is returned to `moda_architect`.

## Validation

- [ ] Review accepted prerequisite report/commit evidence.
- [ ] Confirm the exact published package version is available from the intended registry and contains the specified export map.
- [ ] `git diff --check` and release-only file change inspection. Do **not** rerun unit tests, typecheck, lint or build as separate publication checks.

## Stop Condition

After publication evidence and Completion Report are recorded, set task to `review`, return to `moda_architect` and **STOP**. Do not implement the consumer tasks, merge branches or push `main`.

## Implementation Notes

Approved release metadata location: `moda-interact-shared/package.json`, and lockfile only when the repository's release mechanics legitimately change it. All schema and build-entrypoint edits belong to SHARED-002/005/006/008, not this publication task. The publisher must not choose a different runtime contract.

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
