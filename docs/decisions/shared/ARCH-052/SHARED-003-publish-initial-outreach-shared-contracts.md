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
status: complete
priority: 20
executor: null
claimed_at: null
attempt: 1
depends_on:
- ARCH-052-SHARED-002
- ARCH-052-SHARED-006
- ARCH-052-SHARED-008
enables:
- ARCH-052-ADMIN-001
- ARCH-052-ADMIN-002
- ARCH-052-BACKGROUND-005
- ARCH-052-BACKGROUND-007
- ARCH-052-BACKGROUND-010
- ARCH-052-COMMERCE-006
- ARCH-052-GATEWAY-001
- ARCH-052-MCP-001
- ARCH-052-MCP-002
- ARCH-052-MCP-003
- ARCH-052-SYSTEM-TEST-001
- ARCH-052-SYSTEM-TEST-002
created: '2026-10-29'
updated: 2026-10-30
---

# ARCH-052-SHARED-003: Publish the accepted initial-outreach contracts (including product search)

## Architecture

Architecture ID: `ARCH-052`. Parent: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`. Coordinator: `moda_architect`.

Materialised through the canonical task launcher. The release metadata commit and package publication are recorded in the Completion Report.

## Objective

Publish one architect-accepted version of the **three required structural contract changes** defined in SHARED-002, SHARED-006 and SHARED-008, without adding new implementation behaviour or rerunning implementation tests.

## Context

Shared owns reusable inter-service data shapes. Admin and Background consume template bindings, Background and MCP share the purpose-only initial-outreach context, and MCP/Commerce consume the extended commerce-product schema. SHARED-005 was separately **completed and architect-accepted** in an earlier implementation attempt. Its accepted task and review record remain intact, but the later ARCH-052 architecture no longer requires the proof-contract functionality. Do not add its proof entrypoint to this release. The SHARED-002/006/008 implementation tasks have already passed their own tests and architect review.

## Scope

- After the three prerequisite tasks have `status: complete` and `Architect Review: Accepted`, publish their accepted Shared package contents using the existing repository's authorised release process.
- Verify the exact released package exposes the unchanged `/commerce` entrypoint with `CommerceOutreachToolContextSchema`, `CommerceProductSaleEvidenceSchema`, existing product/discount tools plus the new `commerce_get_product` members; and the new `/recovery-template-bindings` entrypoint with the names listed below.
- Record the exact version, registry destination, publication command, registry evidence and changed release metadata. Keep implementation source unchanged.

## Out of Scope

- No new application schemas, runtimes, source edits, lint, typecheck, unit/integration tests, new agent code, tool publication, provider calls, database migration or consumer rollout in this publication task.
- Do not include the SHARED-005 proof-contract entrypoint as part of this ARCH-052 release. Its accepted historical task remains Complete and is **not a publication prerequisite**. SHARED-001, SHARED-004 and SHARED-007 are superseded.
- If the current Shared package source already includes a proof export that cannot be excluded without source changes, stop and return that integration issue to `moda_architect`. A publication task must not modify accepted implementation source.

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

**The retained new public export entry must be exactly:**

```json
{
  "./recovery-template-bindings": {
    "types": "./dist/recovery-template-bindings.d.ts",
    "import": "./dist/recovery-template-bindings.js"
  }
}
```

This JSON fragment is an addition to the existing `package.json` `exports` object, not a replacement for the whole object. `/commerce` already exists and must remain unchanged as a package path.

## Dependencies

- `ARCH-052-SHARED-002` — Complete and architect-accepted.
- `ARCH-052-SHARED-006` — Complete and architect-accepted.
- `ARCH-052-SHARED-008` — Complete and architect-accepted.

## Enables

- `ARCH-052-ADMIN-001`
- `ARCH-052-ADMIN-002`
- `ARCH-052-BACKGROUND-005`
- `ARCH-052-BACKGROUND-007`
- `ARCH-052-BACKGROUND-010`
- `ARCH-052-COMMERCE-006`
- `ARCH-052-GATEWAY-001`
- `ARCH-052-MCP-001`
- `ARCH-052-MCP-002`
- `ARCH-052-MCP-003`
- `ARCH-052-SYSTEM-TEST-001`
- `ARCH-052-SYSTEM-TEST-002`

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

Approved release metadata location: `moda-interact-shared/package.json`, and lockfile only when the repository's release mechanics legitimately change it. All schema and build-entrypoint edits belong to SHARED-002/006/008, not this publication task. The publisher must not choose a different runtime contract.

## Completion Report

### Status

Complete — Attempt 1 published the four architect-accepted Shared contract changes as `@modainteract/moda-interact-shared@2.6.0`; architect review accepted the release evidence and metadata-only change.

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

None identified. The report records publication and registry artifact inspection; this review environment could not independently reach GitHub or npm because external DNS resolution was unavailable.


## Architect Review

### Review Status

Accepted — Attempt 1. Package `@modainteract/moda-interact-shared@2.6.0` was published and the reported tarball/export inspection satisfies the publication criteria. Only version metadata and lockfile version fields changed. Task Complete; no source implementation, consumer rollout, or merge to `main` is implied.

### Review Notes

The implementation diff contains only `package.json` and `package-lock.json` version changes from 2.5.1 to 2.6.0; dependency versions and source files are unchanged. The Completion Report records the publish command, public registry destination, tarball URL and integrity, exact exports/runtime/declaration checks, and `prepack` result. The four prerequisite tasks are marked Complete in the authoritative task records. The task's stale portable/unmaterialised narrative has been corrected. A direct external re-query was unavailable in this review environment, so registry evidence is accepted from the recorded publication output and tarball inspection.

### Reviewed Files

- `moda-interact-shared/package.json`
- `moda-interact-shared/package-lock.json`
- Published `@modainteract/moda-interact-shared@2.6.0` tarball evidence recorded in the Completion Report

### Validation Reviewed

Reviewed the reported `git diff --check`, release-only file inspection, registry metadata lookup, tarball export/runtime/declaration inspection, and package `prepack` result. Publication-task instructions prohibit rerunning implementation tests, typecheck, lint, or a separate build. Direct network verification was unavailable from this review environment.

### Architecture Conformance

The release metadata-only change preserves existing exports and exposes the four accepted Shared contract changes in the reported published artifact. The publication remains isolated from consumer rollout and source implementation, as required.

### Follow-up

Dependency frontier reconciled: ADMIN-001, ADMIN-002, BACKGROUND-005, COMMERCE-006, MCP-001, and WOOCOMMERCE-001 are Ready. Other enabled tasks remain gated by their incomplete dependencies. No merge to `main` was performed.
