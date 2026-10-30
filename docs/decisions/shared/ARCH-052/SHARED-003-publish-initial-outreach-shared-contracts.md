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
status: review
priority: 20
executor: codex
claimed_at: 2026-10-30T08:10:08Z
attempt: 1
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
updated: 2026-10-30
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

- [x] Check `status: complete` and Accepted reviews for SHARED-002/005/006/008.
- [x] Select approved package version and execute only the authorised release/publish procedure.
- [x] Confirm that the exact expected version is visible at the registry and package exports resolve.
- [x] Record release metadata-only diff and Completion Report evidence.

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

- [x] The package version contains precisely the four accepted Shared changes and retains all existing unrelated exports.
- [x] All listed package paths and runtime symbols/types are present in the published version.
- [x] Only authorised release metadata/lockfile updates occurred; no source code modifications or consumer integration.
- [x] Registry visibility and actual version are recorded; publication failure or an implementation bug is returned to `moda_architect`.

## Validation

- [x] Review accepted prerequisite report/commit evidence.
- [x] Confirm the exact published package version is available from the intended registry and contains the specified export map.
- [x] `git diff --check` and release-only file change inspection. Do **not** rerun unit tests, typecheck, lint or build as separate publication checks.

## Stop Condition

After publication evidence and Completion Report are recorded, set task to `review`, return to `moda_architect` and **STOP**. Do not implement the consumer tasks, merge branches or push `main`.

## Implementation Notes

Approved release metadata location: `moda-interact-shared/package.json`, and lockfile only when the repository's release mechanics legitimately change it. All schema and build-entrypoint edits belong to SHARED-002/005/006/008, not this publication task. The publisher must not choose a different runtime contract.

## Completion Report

### Status

Ready for Review — Attempt 1 published the four architect-accepted Shared contract changes as `@modainteract/moda-interact-shared@2.6.0`.

### Prepared Execution Evidence

- Canonical workspace root: /Users/kwadwoadomafriyie/project/moda-interact-workspace.
- Parent task worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-052-SHARED-003, branch `task/ARCH-052-SHARED-003`, start HEAD `7cd848144162ecd3e92a96f89dee0ac1b26727d7`.
- Implementation worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-052-SHARED-003, branch `task/ARCH-052-SHARED-003`, repository `moda-interact-shared`, start HEAD `8a13af84ed958a4c36f7b13700451ea259433a88`.
- Parent remote task branch fast-forward: not needed. Parent origin/main incorporated: yes.
- Implementation remote task branch fast-forward: not needed. Implementation origin/main incorporated: already current.
- Both worktrees were dedicated to this task. Shared workspace and implementation reference checkouts were not switched or used for task edits; no other task worktree was reused.
- Recursive implementation submodule sync and update-init passed; Shared has no submodule entries and status was ready.
- Attempt 1 claim was committed and pushed by the launcher as `ff9abff67d717a5a808f73ae7d00754aac2cdeeb`.

### Files Changed

- `package.json` — version 2.5.1 to 2.6.0.
- `package-lock.json` — root package version 2.5.1 to 2.6.0.

No source or consumer files changed. The release metadata commit `a44472a` is pushed to `origin/task/ARCH-052-SHARED-003`.

### Work Completed

- Confirmed SHARED-002, SHARED-005, SHARED-006 and SHARED-008 are `complete` with Accepted Architect Reviews.
- Applied the package's minor-version policy for additive public capabilities. Registry inspection confirmed 2.5.1 was the latest version and 2.6.0 was unused before publication.
- Published `@modainteract/moda-interact-shared@2.6.0` using `npm publish --access public` to https://registry.npmjs.org/.
- Published tarball: https://registry.npmjs.org/@modainteract/moda-interact-shared/-/moda-interact-shared-2.6.0.tgz.
- Registry integrity: `sha512-Q2k3kl8OI70BRFaSyRseJ6h3yGxFLTjgvq+jtd4QVfIsvDC1UMGds6kl3zjAdzt6SA7HavehoWD+4u8ru8lcAw==`; shasum `da39840e74538183b18f52ef201a2b6bf90a6cc6`.
- Inspected the downloaded registry tarball: version 2.6.0; unchanged `./commerce` export and exact `./recovery-template-bindings` / `./recovery-offer-proof` export maps; all required JavaScript and declaration files and symbols present, including product-search and exact-product members. No forbidden `OutreachToolResult` or `OutreachPromotionChoiceSchema` declarations.
- The first registry read returned 404 during npm's stated processing delay; a subsequent registry read confirmed version, tarball URL and integrity, and the downloaded tarball passed the artifact checks.

### Validation Results

- Passed: `git diff --check`.
- Passed: release-only file inspection; only `package.json` and `package-lock.json` changed, with package version fields updated and no dependency changes.
- Passed: npm registry metadata lookup and direct inspection of the published 2.6.0 tarball's version, export map, runtime artifacts, and declaration artifacts.
- Passed: npm `prepack` build as part of the authorized publish command; generated JS and declaration build succeeded.
- No unit tests, typecheck, lint, or separate build were run, as required by this publication task.
- `npm ci --prefer-offline` installed the exact lockfile dependencies for the prepack build. npm reported 3 audit findings (1 low, 2 high) and five install scripts awaiting approval; these did not prevent the build or publication and did not modify dependency manifests.

### Deviations

The fresh implementation worktree initially had no `node_modules`, so the first publish attempt stopped before upload when prepack could not find `tsup`. Installing the exact lockfile dependencies resolved this environment issue. The successful retry published the package; no source change or test rerun was needed.

### Assumptions

The additive export and structural contract changes warrant a minor release under the existing package policy; version 2.6.0 was selected after confirming no such version was published.

### Unresolved Issues

None. The package is visible at the intended registry and its published artifact has been verified.

### Architectural Concerns

None identified.


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
