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
status: in_progress
priority: 10
executor: codex
claimed_at: 2026-10-29T22:12:51Z
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

Portable task definition: **defined but not materialised**. No developer branch/worktree, commit or push is asserted.

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

- [ ] Create `moda-interact-shared/src/recovery-template-bindings.ts` with the complete schema below.
- [ ] Register `recovery-template-bindings` in `tsup.config.ts` and `package.json` exports as shown below.
- [ ] Add `src/recovery-template-bindings.test.ts` covering the fixtures below and unchanged old keys.
- [ ] Run Shared declared validation and verify that the entrypoint is browser-safe.

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

- [ ] The exact module and package subpath exist; all current semantic variables and ShopBrand roles remain accepted.
- [ ] Both illustrative projections parse, and unknown variable names, unknown keys, wrong `promotionTarget` values and noninteger positions fail structural parsing.
- [ ] A structurally valid but semantically wrong pairing such as `promotionTarget: "ALTERNATIVE_PRODUCT"` with a `checkout.url` button is **not** rejected by Zod; Admin/Background business checks must reject it in their implementation tasks.
- [ ] No `checkout.url` URL validation is added; Shared preserves only the literal binding identifier.
- [ ] No `.refine()`, `.superRefine()`, `.transform()` or `.check()` is used for business rules.

## Validation

- [ ] `npm run typecheck`, `npm test`, `npm run build` in Shared, with actual command/result evidence.
- [ ] Positive/negative structural fixtures plus browser-safe entrypoint import check.
- [ ] `git diff --check`; confirm no cross-repository code edits or new persistence.

## Stop Condition

After Work Items, Acceptance Criteria and Validation pass, complete the report, set `status: review`, return the mirrored task-branch evidence to `moda_architect`, and **STOP**. Do not execute downstream tasks or self-accept.

## Implementation Notes

The schema source, JSON field names and package export above are the proposed normative contract for this review. No implementing agent may invent additional variables, business rules or bindings. Surface any conflict with existing immutable compilation as a concrete architect review issue instead.

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
