---
id: ARCH-058-SHARED-003
architecture_id: ARCH-058
title: Remove hash-based identity from Commerce built-in tools
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 35
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-058-SHARED-002
enables:
  - ARCH-058-SHARED-004
  - ARCH-058-SHARED-006
  - ARCH-058-SYSTEM-TEST-001
created: 2026-11-04
updated: 2026-11-04
---

# ARCH-058-SHARED-003: Remove hash-based identity from Commerce built-in tools

## Architecture

Architecture ID: `ARCH-058`.

Parent: `docs/architecture/ARCH-058-commerce-agent-product-discovery.md`.

Normative correction: `docs/architecture/ARCH-058/shared-hash-reconciliation.md`, revision 10, and `docs/architecture/ARCH-058/contracts.md`, section 4.

Coordinator: `moda_architect`.

This task replaces the unexecuted revision-9 SHARED-003 Zod-pinning proposal. The previous task was defined but not materialised, claimed or implemented. Preserve the accepted SHARED-001 source history and SHARED-002 4.0.0 publication receipt as historical evidence; do not edit those completed task records.

## Objective

Make `toolName + definitionVersion` the complete durable identity for code-owned Commerce discount tools by removing `contractHash` and its runtime payload/hash mechanism from the Shared Commerce public contract, runner and focused tests. Preserve the two built-in tool names, their `definitionVersion: "1.0.0"`, their descriptions, bounded inputs, output schemas and runner version `1.1.0`.

## Context

MCP-002 correctly stopped when the Shared 4.0.0 descriptor constants did not hash to the payload produced by the installed consumer runtime. The mismatch proved that the hash is a second, dependency-sensitive identity mechanism layered on top of the immutable built-in name/version contract. ARCH-058 now removes that mechanism instead of pinning application Zod versions or replacing the recorded hashes.

The package remains at source metadata version `4.0.0` during this implementation task. SHARED-006 owns the coordinated breaking publication after SHARED-003, SHARED-004 and SHARED-005 are architect-accepted.

## Scope

Modify only the Shared Commerce contract/runtime files required to remove hash identity:

- `src/commerce/definitions.ts`
- `src/commerce/built-in-tools.ts`
- `src/commerce/schemas.ts`
- `src/commerce/selection.ts`
- `src/commerce/runner/tool-policy.ts`
- `src/commerce/product-discovery-contracts.test.ts`
- `src/commerce/runner/built-in-tools.test.ts`
- `scripts/validate-commerce-entrypoints.mjs`
- `README.md`

A directly related existing focused test may be changed only when it asserts the removed hash field/helper. Do not change unrelated Commerce contracts.

## Out of Scope

- Removing `CommerceConversationToolContextSchema` or its type; SHARED-004 owns that public-contract cleanup.
- Changing Commerce date/time syntax; SHARED-005 owns that correction.
- Changing package version or publishing; SHARED-006 owns release metadata/publication.
- Changing Zod versions, package overrides, peer dependencies or consumer dependencies.
- Editing Database functions/migrations; DATABASE-002 owns persisted-grant conversion.
- Editing MCP, Commerce or Background application source.
- Changing `responseContractHash`, `contentHash`, Shopify `schemaHash`, cryptographic hashes, source checksums or any hash unrelated to the two code-owned built-in descriptor/grant identities.

## Requirements

1. `CommerceBuiltInToolGrantSchema` must be a strict object with exactly:

   ```ts
   {
     kind: "BUILT_IN";
     toolName: "commerce_get_discount_options" | "commerce_get_discount_details";
     definitionVersion: "1.0.0";
   }
   ```

2. `CommerceBuiltInToolDescriptorSchema` must be a strict object with exactly the existing descriptor fields except `contractHash`:

   ```ts
   {
     kind: "BUILT_IN";
     name: "commerce_get_discount_options" | "commerce_get_discount_details";
     definitionVersion: "1.0.0";
     description: string;
     inputSchema: InputSchema;
   }
   ```

3. `commerceDiscountBuiltInDescriptors` must retain the current two tool names, descriptions, input schemas and literal `definitionVersion: "1.0.0"`. Remove the two checked-in hash constants.

4. Delete the public `commerceBuiltInToolContractPayload` helper. Do not replace it with another contract hash, fingerprint, generated-schema digest or serializer-derived identity.

5. `isTrustedCommerceBuiltInGrant` must return true only when `toolName` and `definitionVersion` match one of the canonical descriptor constants. `isTrustedCommerceBuiltInDescriptor` continues to validate the complete canonical descriptor object, now without a hash field.

6. `deduplicateTools` must emit built-in grants using only `kind`, `toolName` and `definitionVersion`. Published-tool grants remain unchanged.

7. `CommerceManifestSchema`, `manifestMatchesGrant`, `currentlyGrantedTools`, runner tool resolution and authorization must compare built-in identity by name/version and the canonical descriptor object. No path may accept an arbitrary built-in name or arbitrary version.

8. Because the schemas are strict, a legacy built-in object containing `contractHash` must fail the corrected public schemas. DATABASE-002 performs the durable row conversion before corrected consumers are deployed.

9. Keep `runnerVersion === "1.1.0"`. This task alone does not change the built-in input/output semantics, so its intermediate source keeps `definitionVersion === "1.0.0"`. Do not publish this intermediate source. SHARED-005 owns the later coordinated bump to `2.0.0` because SHARED-005 intentionally changes the accepted discount-output timestamp wire semantics.

10. Do not change `package.json` or `package-lock.json` dependency versions in this task. In particular, do not implement the superseded cross-application Zod pinning proposal.

## Work Items

- [ ] Remove `contractHash` from the built-in grant and descriptor schemas/types.
- [ ] Remove built-in hash constants and `commerceBuiltInToolContractPayload`.
- [ ] Update trusted-descriptor/grant helpers and manifest/grant projection/equality logic.
- [ ] Update runner built-in resolution to use canonical name/version identity without hashes.
- [ ] Replace hash-specific focused tests with strict name/version/extra-field tests.
- [ ] Update the clean-process Commerce entrypoint verifier and README contract inventory.
- [ ] Run the required validation and record exact results.

## Interfaces / Contracts

Contract owner: this task.

Public package: `@modainteract/moda-interact-shared/commerce`.

Canonical built-in identities after this task:

```text
commerce_get_discount_options@1.0.0
commerce_get_discount_details@1.0.0
```

`contractHash` and `commerceBuiltInToolContractPayload` are removed public API in the later SHARED-006 major release. Published Studio tools and their revision/content identities are not changed.

## Dependencies

- `ARCH-058-SHARED-002` — accepted historical 4.0.0 publication baseline.

## Enables

- `ARCH-058-SHARED-004`
- `ARCH-058-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Neither built-in descriptor nor built-in grant schemas/types contain `contractHash`.
- [ ] `commerceBuiltInToolContractPayload` is absent from source, generated declarations and the clean-process export check.
- [ ] Both canonical built-ins retain their existing names, descriptions, input schemas and definition version `1.0.0`.
- [ ] A corrected built-in grant with exactly three fields parses; the same object with `contractHash`, `toolId`, `capabilityKeys`, an unknown name or version `2.0.0` fails.
- [ ] A corrected manifest and retained grant match when the built-in name/version pair matches and fail when either name/version differs.
- [ ] Published-tool grant behavior and existing release/capability provenance behavior are unchanged.
- [ ] Runner built-in authorization resolves only the corrected canonical descriptor and does not use a hash.
- [ ] No Zod/package dependency change is present.
- [ ] Unrelated hash fields/helpers remain unchanged.

## Validation

From the Shared implementation worktree:

```bash
npm ci --no-audit --no-fund
npm run test:product-discovery-contracts
npm run typecheck
npm run build
npm run validate:commerce-entrypoints
npm pack --dry-run
git diff --check
```

Also run:

```bash
rg -n '\bcontractHash\b|commerceBuiltInToolContractPayload' \
  src/commerce/definitions.ts \
  src/commerce/built-in-tools.ts \
  src/commerce/schemas.ts \
  src/commerce/selection.ts \
  src/commerce/runner/tool-policy.ts
```

Expected result: no matches in these production contract/runtime files. Negative compatibility tests and the entrypoint verifier may mention the removed names as test strings; `npm run validate:commerce-entrypoints` must prove the built package does not export them. Do not broaden this grep to unrelated hash concepts such as `responseContractHash`.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report, return control to `moda_architect` and STOP. Do not begin SHARED-004, DATABASE-002, publication or consumer changes.

## Implementation Notes

This is a deliberate pre-production breaking contract correction. Do not add compatibility unions accepting both hashed and non-hashed built-in grants. The only supported identity field set is the three-field shape above. This task intentionally leaves the intermediate definition version at `1.0.0`; SHARED-005 must change both built-ins to `2.0.0` before publication because it changes their output timestamp semantics.

## Completion Report

### Status

Not Started

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

The accepted SHARED-002 4.0.0 receipt is historical evidence only; no corrected package has yet been published.

### Unresolved Issues

None beyond the declared dependent correction/publication tasks.

### Architectural Concerns

None.

## Architect Review

### Review Status

Pending

### Review Notes

Not reviewed.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Not assessed.

### Follow-up

None.
