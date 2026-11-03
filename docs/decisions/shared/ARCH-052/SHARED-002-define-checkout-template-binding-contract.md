---
id: ARCH-052-SHARED-002
architecture_id: ARCH-052
title: Define checkout and alternative-promotion WhatsApp bindings
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 10
executor: null
claimed_at: null
attempt: 1
depends_on: []
enables:
- ARCH-052-SHARED-003
created: '2026-10-29'
updated: 2026-10-29
---

# ARCH-052-SHARED-002: Define checkout and alternative-promotion WhatsApp bindings

## Architecture

Architecture ID: `ARCH-052`. Parent: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`. Coordinator: `moda_architect`.

Task definition: **materialised and executed** through the canonical launcher-resolved parent and Shared worktrees. The Completion Report records the prepared packet evidence.

## Objective

Create **one concrete, browser-safe structural contract** for the semantic variables and immutable WhatsApp template binding projections exchanged between Admin and Background. Business decisions about whether a binding is permitted in a particular template belong to Admin/Background, not Zod.

## Context

Current Admin source (`src/lib/admin/whatsapp-templates/authoring/types.ts`) and Background source (`src/services/recovery-template-preparation/recovery-template-brand.ts` and `recovery-template-bindings.ts`) each enumerate the existing binding keys. They already recognise `shop.categoryName` and the ShopBrand roles. `@modainteract/moda-interact-shared/recovery-template-bindings` does not yet exist. ARCH-052 introduces checkout-item summaries and independently approved alternative-product promotions without inventing freeform model-written WhatsApp text.

## Scope

- Implement the module and public package entrypoint below. The code is the proposed canonical **shape**; Admin and Background must consume the published export in their own repository tasks.
- Preserve all existing semantic variable names and media roles, add the exact new keys below, and define the compiled URL-button binding representation.
- Carry a `promotionTarget` discriminator in the existing authoring/compiled JSON projection without adding a Prisma column or changing Meta purpose enums.
- Do **not** add checkout-URL validation. `checkout.url` continues to receive the upstream `CheckoutRecovery.checkoutUrl` unchanged. This Shared schema does not inspect URL protocols, hosts, prefixes, expiry, destination ownership or reachability.

## Out of Scope

- No Admin compiler, Meta template registration, Background binding resolver, send logic, Meta media processing or URL handling implementation in Shared.
- No database/media table, dynamic footer, unapproved template generation, frozen merchant policy or new business-rule Zod refinements.

## Requirements

- **Zod boundary:** syntax of the binding object, recognised key strings, position type, optional/nullable fields and unknown-key rejection only. No conditions such as “an alternative promotion must have a product URL” or “a CODE offer must have a code” are imposed by Zod.
- **Admin/Background business boundary:** eligible variables by template purpose, checkout versus alternative product wording, role/target compatibility, number and order of Meta parameters, approved button semantics, absence handling, compile/hash checks and approved template selection belong to their owning services.
- Keep the existing authoring AST and provider-approved projection immutable after publication. ARCH-052 does not make arbitrary model text a template variable.
- Follow the repository's dedicated mirrored worktree/start-of-attempt policy. Use Shared structured logging for any runtime logs; never log checkout URLs, customer personal data or provider secrets.

## Work Items

- [x] Create `moda-interact-shared/src/recovery-template-bindings.ts` with the complete schema below.
- [x] Register `recovery-template-bindings` in `tsup.config.ts` and `package.json` exports as shown below.
- [x] Add `src/recovery-template-bindings.test.ts` covering the fixtures below and unchanged old keys.
- [x] Run Shared declared validation and verify that the entrypoint is browser-safe.

## Interfaces / Contracts

**Create `moda-interact-shared/src/recovery-template-bindings.ts` exactly as follows:**

```typescript
import { z } from "zod";

export const RecoveryTemplateSemanticKeySchema = z.enum([
  "customer.firstName",
  "shop.name",
  "shop.categoryName",
  "checkout.url",
  "checkout.itemsSummary",
  "offer.code",
  "offer.description",
  "promotion.productName",
  "promotion.productUrl",
  "promotion.offerDescription",
  "promotion.code",
  "shopBrand.brandName",
  "shopBrand.logoUrl",
  "shopBrand.logoAltText",
  "shopBrand.logoWidth",
  "shopBrand.logoHeight",
  "shopBrand.squareLogoUrl",
  "shopBrand.squareLogoAltText",
  "shopBrand.coverImageUrl",
]);
export type RecoveryTemplateSemanticKey =
  z.infer<typeof RecoveryTemplateSemanticKeySchema>;

export const RecoveryPromotionTargetSchema = z.enum([
  "CHECKOUT",
  "ALTERNATIVE_PRODUCT",
]);
export type RecoveryPromotionTarget =
  z.infer<typeof RecoveryPromotionTargetSchema>;

export const RecoveryTemplateHeaderMediaRoleSchema = z.enum([
  "LOGO",
  "SQUARE_LOGO",
  "COVER_IMAGE",
  "CHECKOUT_PRODUCT",
]);
export type RecoveryTemplateHeaderMediaRole =
  z.infer<typeof RecoveryTemplateHeaderMediaRoleSchema>;

export const RecoveryTemplateTextBindingSchema = z.strictObject({
  position: z.number().int(),
  variable: RecoveryTemplateSemanticKeySchema,
});
export type RecoveryTemplateTextBinding =
  z.infer<typeof RecoveryTemplateTextBindingSchema>;

export const RecoveryTemplateUrlButtonBindingSchema = z.strictObject({
  index: z.number().int(),
  subType: z.literal("url"),
  variable: z.enum([
    "checkout.url",
    "promotion.productUrl",
  ]),
});
export type RecoveryTemplateUrlButtonBinding =
  z.infer<typeof RecoveryTemplateUrlButtonBindingSchema>;

export const RecoveryTemplateFrozenBindingsSchema = z.strictObject({
  schemaVersion: z.literal(1).optional(),
  promotionTarget: RecoveryPromotionTargetSchema.optional(),
  headerMediaRole: RecoveryTemplateHeaderMediaRoleSchema.optional(),
  header: z.array(RecoveryTemplateTextBindingSchema).optional(),
  body: z.array(RecoveryTemplateTextBindingSchema),
  buttons: z.array(RecoveryTemplateUrlButtonBindingSchema),
});
export type RecoveryTemplateFrozenBindings =
  z.infer<typeof RecoveryTemplateFrozenBindingsSchema>;
```

`promotionTarget` is **optional at the transport level** so existing Meta recovery projections (with no such field) remain parseable; Admin must require and freeze it for **new ARCH-052 alternative-product template variants**. This is a template *policy*, enforced outside Zod. `headerMediaRole` is likewise optional because TEXT headers have no image. This task does not change stored authoring-data migration or the meaning of the existing ShopBrand roles.

**Package entrypoint additions:**

```typescript
// moda-interact-shared/tsup.config.ts — add to entry
"recovery-template-bindings": "src/recovery-template-bindings.ts",
```

```json
{
  "./recovery-template-bindings": {
    "types": "./dist/recovery-template-bindings.d.ts",
    "import": "./dist/recovery-template-bindings.js"
  }
}
```

**Illustrative structurally valid checkout projection:**

```json
{
  "schemaVersion": 1,
  "promotionTarget": "CHECKOUT",
  "body": [
    {"position": 1, "variable": "customer.firstName"},
    {"position": 2, "variable": "checkout.itemsSummary"},
    {"position": 3, "variable": "offer.description"}
  ],
  "buttons": [{"index": 0, "subType": "url", "variable": "checkout.url"}]
}
```

**Illustrative structurally valid alternative-product projection:**

```json
{
  "schemaVersion": 1,
  "promotionTarget": "ALTERNATIVE_PRODUCT",
  "body": [
    {"position": 1, "variable": "promotion.productName"},
    {"position": 2, "variable": "promotion.offerDescription"}
  ],
  "buttons": [{"index": 0, "subType": "url", "variable": "promotion.productUrl"}]
}
```

This is a **structural example only**; image headers are optional, and Admin/Background determine the permissible media role for each approved variant. The Shared schema does not confer approval.

**Business checks explicitly delegated to service owners (not Zod):**

| Rule | Owner |
|---|---|
| Allowed variables for `NO_OFFER`, `CODE_OFFER`, `AUTOMATIC_OFFER` and the configured promotion target | Admin compiler and Background resolver |
| Header role allowed for the intended product/media, image readiness and Meta approval | Admin + Background |
| No alternative-product claim unless the selected product/offer is backed by MCP results | Background |
| Product promotion URL belongs to the merchant and is safe to advertise | MCP product provider / Background promotion preparation |
| Checkout URL used unchanged; no new ARCH-052 format/host/prefix/reachability check | Background |
| Button positions, Meta parameter counts, immutable template/hash matching | Admin compiler + Background template send |

## Dependencies

None.

## Enables

- `ARCH-052-SHARED-003`

## Acceptance Criteria

- [x] The exact module and package subpath exist; all current semantic variables and ShopBrand roles remain accepted.
- [x] Both illustrative projections parse, and unknown variable names, unknown keys, wrong `promotionTarget` values and noninteger positions fail structural parsing.
- [x] A structurally valid but semantically wrong pairing such as `promotionTarget: "ALTERNATIVE_PRODUCT"` with a `checkout.url` button is **not** rejected by Zod; Admin/Background business checks must reject it in their implementation tasks.
- [x] No `checkout.url` URL validation is added; Shared preserves only the literal binding identifier.
- [x] No `.refine()`, `.superRefine()`, `.transform()` or `.check()` is used for business rules.

## Validation

- [x] `npm run typecheck`, `npm test`, `npm run build` in Shared, with actual command/result evidence.
- [x] Positive/negative structural fixtures plus browser-safe entrypoint import check.
- [x] `git diff --check`; confirm no cross-repository code edits or new persistence.

## Stop Condition

After Work Items, Acceptance Criteria and Validation pass, complete the report, set `status: review`, return the mirrored task-branch evidence to `moda_architect`, and **STOP**. Do not execute downstream tasks or self-accept.

## Implementation Notes

The schema source, JSON field names and package export above are the proposed normative contract for this review. No implementing agent may invent additional variables, business rules or bindings. Surface any conflict with existing immutable compilation as a concrete architect review issue instead.

## Completion Report

### Status

Ready for Review — Attempt 1 implemented the structural binding contract and passed all declared validation.

### Prepared Execution Evidence

- Canonical workspace root: /Users/kwadwoadomafriyie/project/moda-interact-workspace.
- Task definition was materialized.
- Parent task worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-052-SHARED-002, branch task/ARCH-052-SHARED-002; created for this attempt.
- Implementation worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-052-SHARED-002, branch task/ARCH-052-SHARED-002; created for this attempt.
- Shared workspace checkout switched or mutated for task work: no. Shared implementation checkout switched or mutated for task work: no. Another task worktree reused: no.
- Parent task branch fast-forward from origin: not needed. Parent origin/main incorporated: already current. Parent start head: 71cf6915ff1a17911d10252e1aacd670c97f3bc5.
- Implementation task branch fast-forward from origin: not needed. Implementation origin/main incorporated: already current. Implementation start head: b4ebb52a2b5ae931b78983c1b1b800cf7e6b579e.
- Recursive submodule sync and update-init both passed; the Shared repository has no submodule entries.
- Attempt 1 claim was committed and pushed by the launcher as 612260e0141f6458d3f733aa25647b8ae98a24a9.
- Implementation repository commit: 2e86537 (task(ARCH-052-SHARED-002): add recovery template binding contract), pushed to origin/task/ARCH-052-SHARED-002.

### Files Changed

- moda-interact-shared/src/recovery-template-bindings.ts
- moda-interact-shared/src/recovery-template-bindings.test.ts
- moda-interact-shared/tsup.config.ts
- moda-interact-shared/package.json

### Work Completed

- Added the exact task-defined strict Zod schemas and inferred TypeScript types for semantic keys, promotion target, header media roles, text bindings, URL-button bindings, and frozen binding projections.
- Preserved all prior semantic keys and ShopBrand roles and added the specified checkout-item and alternative-promotion keys.
- Added tests for both illustrative projections, legacy projections with optional fields omitted, unknown keys and variables, invalid targets, noninteger positions and button indexes, and a structurally valid target/button mismatch.
- Kept Zod limited to structure. It performs no target compatibility, offer semantics, media approval, parameter ordering, checkout URL inspection, or other business-rule checks. Admin and Background remain the intended consumer repositories for their own policy enforcement.
- Registered the dedicated package subpath in tsup and package exports. No root API, persistence, or consumer repository changes were made.

### Validation Results

- Passed: npm run typecheck.
- Passed: npm test — 381 tests, 380 passed, 1 skipped, 0 failed.
- Passed: npm run build, including the new dist/recovery-template-bindings.js and declaration output.
- Passed: imported the built public subpath @modainteract/moda-interact-shared/recovery-template-bindings and parsed an exported semantic key.
- Passed: bundled dist/recovery-template-bindings.js with esbuild using platform=browser, confirming the built entrypoint resolves for browser use.
- Passed: git diff --check.

### Deviations

The initial typecheck could not find tsc because the newly created worktree had no node_modules. The exact package-lock dependencies were installed from the local npm cache with npm ci --offline; typecheck, tests, and build then passed. No dependency manifest or lockfile change resulted.

### Assumptions

Admin and Background will consume the published Shared subpath in their separately assigned implementation tasks. Optional promotionTarget and headerMediaRole preserve existing projection compatibility as specified.

### Unresolved Issues

None.

### Architectural Concerns

None.


## Architect Review

### Review Status

Accepted

### Review Notes

The implementation branch `task/ARCH-052-SHARED-002` is clean at `2e86537` and contains only the task's four scoped files. The exported Zod schemas match the task's semantic-key list, promotion target, header media roles, text and URL-button bindings, optional compatibility fields, and strict frozen-binding shape. Unknown keys are rejected structurally, while target/button compatibility and checkout URL content remain outside Zod as required. The tests cover both illustrative projections, existing projections without optional fields, legacy semantic keys/media roles, malformed structures, and the deliberate structurally valid business mismatch. The package subpath is registered in tsup and `package.json`; the runtime entrypoint imports Zod only and is browser-safe. No persistence or consumer-service implementation was added.

The Completion Report records launcher-resolved dedicated parent and implementation worktrees, synchronized task branches and `origin/main`, recursive submodule preparation, and no shared checkout or worktree reuse. Required typecheck, test (380 passed, 1 skipped), build, public-subpath import, browser-platform bundle, and `git diff --check` all passed. The temporary offline dependency installation made no manifest or lockfile changes.

#### Reviewed Files

- Attempt 1 Completion Report and task Acceptance Criteria/Validation.
- Shared implementation branch `task/ARCH-052-SHARED-002` at `2e86537`, clean with a four-file diff from `origin/main`.
- `src/recovery-template-bindings.ts`.
- `src/recovery-template-bindings.test.ts`.
- `tsup.config.ts` and `package.json`.
- ARCH-052 execution plan and Shared task index, including SHARED-003's publication dependencies.

#### Validation Reviewed

Reviewed the recorded `npm run typecheck`, `npm test` (380 passed, 1 skipped, 0 failed), `npm run build`, public package-subpath import and parse, browser-platform bundle, and `git diff --check`. No tests were rerun for this review.

#### Architecture Conformance

The schema provides a single Shared-owned, browser-safe structural contract and does not duplicate service policy or impose checkout URL validation. Admin and Background remain responsible for business checks. The task conforms to ARCH-052, Shared ownership, compatibility requirements, and its bounded scope.

#### Follow-up

Set this automatic-completion task to `complete`. `ARCH-052-SHARED-003` remains `pending` because its other implementation prerequisites, SHARED-005, SHARED-006, and SHARED-008, are still Ready rather than Complete. No consumer or publication task is promoted by this acceptance.
