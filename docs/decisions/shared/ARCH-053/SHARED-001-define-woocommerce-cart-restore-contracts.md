---
id: ARCH-053-SHARED-001
architecture_id: ARCH-053
title: Define canonical Woo restoration wire schemas
task_kind: implementation
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
depends_on: []
enables:
- ARCH-053-SHARED-002
created: 2026-10-29
updated: 2026-10-30
---

# ARCH-053-SHARED-001 — Define canonical Woo restoration wire schemas

## Architecture

Architecture ID: `ARCH-053`. Document: `docs/architecture/ARCH-053-woocommerce-checkout-recovery-links-and-cart-restoration.md`. Coordinator: `moda_architect`. **Portable canonical task: defined but not materialised**; no Git branch, worktree, commit, push, review or producer deployment claimed.

## Objective

Define canonical Woo restoration wire schemas. One bounded outcome in `moda-interact-shared` owned by `moda_shared`.

## Context

The inspected source snapshot is dated 2026-10-30. ARCH-052 owns dynamic discount discovery and must not be used for these checkout-URL changes. An ARCH-048 next-generation dependency exists only as a separate *portable* proposal until accepted/materialised. This task is **Ready** from the snapshot/dependency inventory, subject to fresh launcher re-gating.

## Scope

Implement only these **Shared repository** paths; the API, Background and WooCommerce consumers have separate tasks:

- `moda-interact-shared/src/woocommerce/contracts.ts` — new strict, browser-safe Zod definitions and inferred TypeScript types. Implement the **exact declarations in Interfaces / Contracts**; no alternate model or additional fields.
- `moda-interact-shared/src/woocommerce/index.ts` — re-export the schemas, constants and inferred types from `./contracts.js` (or the existing package-consistent TypeScript resolution convention).
- `moda-interact-shared/src/woocommerce/contracts.test.ts` — deterministic positive/negative structural contract tests and fixture round trips.
- `moda-interact-shared/src/woocommerce/__fixtures__/woo-restore-v1.json` — exact canonical JSON example bundle specified below, also used for PHP serialization parity. Publish this JSON fixture through the explicit package subpath below so cross-repository consumers can compare to the same source.
- `moda-interact-shared/tsup.config.ts` — add ONLY entry `"woocommerce/index": "src/woocommerce/index.ts"`, preserving existing entries and browser-safe runtime dependencies.
- `moda-interact-shared/package.json` — add the `"./woocommerce"` `types`/`import` export and `"./woocommerce/fixtures"` JSON asset export, and include the fixture path under `files`; do not change package version (publication is SHARED-002).

The Shared **snapshot contract** is the standalone `checkout.restoration` value. A canonical Woo v1 HTTP checkout has `checkout: {currency, total, items?, contact?, restoration?}` but the existing checkout identity and normalized phone-proof rules remain API-owned. Do not redefine those existing fields in Shared.

No new source paths or tests outside the list without architect approval. The only parent-workspace file an executing agent may update is this task's authorised metadata/Completion Report.

## Out of Scope

No Woo plugin/API/Background implementation; no package publication in this task; no ARCH-052 discount selection contracts.

No execution of Enabled tasks, unrelated cross-repository implementation, extra database objects or new generic logger.

## Requirements

- All declared schemas use `z.strictObject` and reject unknown keys. The one `kind` discriminator must provide **two mutually exclusive variants**: supported requires `lines` and forbids `reason`; unsupported requires `reason` and forbids `lines`.
- A **supported** snapshot is a complete, validated restoration record with `lines` (1..50) and the **complete known original** `appliedCouponCodes` (0..10). An empty coupon array in a supported snapshot means Woo verified no coupon was applied; it must never mean "field missing" or "coupon enumeration failed".
- An **unsupported** snapshot has a required `reason`, a structurally bounded `appliedCouponCodes` array and **no `lines` key**. Its coupon list is not evidence that restoration is possible or that coupon enumeration succeeded: `reason: 'COUPONS_UNAVAILABLE'` makes even `[]` non-authoritative. No link is issued for an unsupported snapshot. An *absent `checkout.restoration` field* means legacy/unknown, never "coupon free".
- Every supported line has a Woo positive decimal product ID **encoded as a string**, optional positive decimal variation ID string, quantity integer 1..100000 and optional Woo variation-attribute map (`Record<string,string>`, at most ten entries, bounded keys/values). No display fields (`title`, `sku`, `unitPrice`, `total`) or customer fields belong inside the restoration line.
- Coupon strings are preserved in their original Woo-applied order/content; Shared never upper/lower-cases, sorts, deduplicates, verifies, replaces or issues coupons. Runtime coupon validity, usage/expiry/stacking and current totals remain WooCommerce-owned.
- The resolver request has exactly `schemaVersion`, `recoveryId`, `token`; the positive resolver response has exactly `schemaVersion`, `status:'eligible'`, `recoveryId`, `checkoutKey`, `snapshot:<supported snapshot>`, `outreachOffer:<verified offer>`. The resolver **never** returns an unsupported snapshot, customer identity or shop credentials. Denials are API-owned HTTP statuses/body, not a second successful response union.
- Shared is **wire-shape validation only**. It may enforce lengths, types, key count, allowed characters, strictness and version literals, but MUST NOT use schema refinements for provider product ownership, Woo stock/variant eligibility, current coupon validity, merchant host checking, replay/freshness, consent/STOP, recovery generation state or token authentication. The lone attribute count check is a structural cardinality limit (not a business-rule check).
- The v1 checkout restoration extension is optional on the containing checkout. Do not define a competing complete HTTP event schema or locally reimplement `WooCheckoutContact` or phone canonicalisation. API-001 owns the **single** `woo.activity.v1` HTTP input with normalized phone proof and its projection into the existing `woo.activity.v1` BullMQ job; Background-001 validates the additive queue field. No HTTP v2/v3 versions or compatibility wrappers.
- Reject unsafe input shape and unexpected keys, do not silently trim/normalise incomplete baskets; do not include any PII, raw recovery URL or WordPress session token in the snapshot. Round-trip JSON fixtures must remain stable across Node/Woo PHP consumers.

### Mandatory workflow/security invariants

- Inspect `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, `docs/developer-task-workflow.md`, `docs/task-definition-materialization.md` and launcher preparation evidence. Use dedicated, synchronized parent and implementation task worktrees; never infer branch creation/push from this portable definition.
- Read ARCH-053 and this task before claiming Ready, and stop on a missing Shared dependency or ownership gap. This task must not change ARCH-052 dynamic discount discovery or overwrite existing identity/commerce contracts.
- Do not swallow unexpected errors. Node services use the existing Shared logger; tests for this pure schema should not log secrets, coupon codes, customer details or complete URLs. PHP diagnostics are owned by WooCommerce. Unexpected runtime/authentication/provider failures must not be converted into valid schema results.
- No direct WordPress plugin, API, Background, Prisma, Redis, package publication, new URL signer or production WhatsApp sending implementation. Do not relax consent/STOP/order/final-send guards or introduce cross-generation outreach caps/cooldowns.

## Work Items

- [ ] Create `src/woocommerce/contracts.ts` with the exact version constants, literal unions, line schema, supported/unsupported snapshot schemas, outreach-offer union, extension schema and single v1 resolver schemas/types below.
- [ ] Export precisely those schemas/types from `src/woocommerce/index.ts` and publish the browser-safe `./woocommerce` subpath through `tsup.config.ts` and `package.json`.
- [ ] Create the exact JSON fixture structure described below in `src/woocommerce/__fixtures__/woo-restore-v1.json`; expose it under `./woocommerce/fixtures` without embedding customer data or bearer secrets from a real installation.
- [ ] Add passing structural parsing tests for the supported/unsupported snapshots, v1 checkout restoration extension, resolver v1 request/response, all four outreach-offer variants, and deterministic JSON round trip.
- [ ] Add rejecting tests for missing/extra fields, forbidden `lines`/`reason` cross-variant fields, invalid IDs and quantities, overlong/too-many attributes/coupons, missing coupon list, bad token, invalid outreach-offer variants and any v2 resolver schemaVersion.
- [ ] Validate package `build`, `typecheck`, focused Shared unit tests, built ESM `./woocommerce` export from the package and JSON fixture package inclusion; report exact commands in Completion Report.

## Interfaces / Contracts

**Owner:** `moda_shared`. **Published import:** `@modainteract/moda-interact-shared/woocommerce` (implementation in SHARED-001; publication in SHARED-002). **PHP:** reads the fixture/wire specification, not a TypeScript import.

### 1. Exact TypeScript/Zod source to implement

Create `src/woocommerce/contracts.ts` with the following definitions. Do not substitute abstract placeholders such as `lines: [...1..50]`, `items: unknown[]` or `coupons: any[]`.

```typescript
import { z } from "zod";

export const WOO_CART_RESTORE_SNAPSHOT_VERSION = "woo.cart-restore.v1" as const;
export const WOO_RESTORE_RESOLVE_VERSION = "woo.restore.resolve.v1" as const;

// Wire IDs are strings because WordPress/PHP may emit integer IDs larger
// than JavaScript's safe-integer range. WooCommerce validates their meaning.
const WooPositiveDecimalIdSchema = z.string()
  .min(1).max(20).regex(/^[1-9][0-9]*$/);
const WooOpaqueRecoveryIdSchema = z.string()
  .min(1).max(128).regex(/^[A-Za-z0-9][A-Za-z0-9._:~-]{0,127}$/);
const WooNoControlTextSchema = (max: number) => z.string()
  .min(1).max(max).regex(/^[^\p{Cc}]+$/u);

// z.record has no .max() for property count. This single refinement enforces
// only the documented structural <=10 property bound; NO business policy.
const WooRestoreAttributesV1Schema = z.record(
  WooNoControlTextSchema(80), WooNoControlTextSchema(200),
).superRefine((value, ctx) => {
  if (Object.keys(value).length > 10) {
    ctx.addIssue({code: "custom", message: "Too many attributes"});
  }
});

const WooAppliedCouponCodesV1Schema = z.array(WooNoControlTextSchema(128)).max(10);

export const WooCartRestoreLineV1Schema = z.strictObject({
  productId: WooPositiveDecimalIdSchema,
  variationId: WooPositiveDecimalIdSchema.optional(),
  quantity: z.number().int().min(1).max(100_000),
  attributes: WooRestoreAttributesV1Schema.optional(),
});
export type WooCartRestoreLineV1 = z.infer<typeof WooCartRestoreLineV1Schema>;

export const WooCartRestoreUnsupportedReasonV1Schema = z.enum([
  "ITEMS_UNAVAILABLE",
  "UNSUPPORTED_PRODUCT_TYPE",
  "CUSTOM_CART_ITEM_DATA",
  "INVALID_VARIATION",
  "COUPONS_UNAVAILABLE",
  "LIMIT_EXCEEDED",
]);
export type WooCartRestoreUnsupportedReasonV1 =
  z.infer<typeof WooCartRestoreUnsupportedReasonV1Schema>;

export const WooCartRestoreSupportedSnapshotV1Schema = z.strictObject({
  schemaVersion: z.literal(WOO_CART_RESTORE_SNAPSHOT_VERSION),
  kind: z.literal("supported"),
  appliedCouponCodes: WooAppliedCouponCodesV1Schema,
  lines: z.array(WooCartRestoreLineV1Schema).min(1).max(50),
});
export type WooCartRestoreSupportedSnapshotV1 =
  z.infer<typeof WooCartRestoreSupportedSnapshotV1Schema>;

export const WooCartRestoreUnsupportedSnapshotV1Schema = z.strictObject({
  schemaVersion: z.literal(WOO_CART_RESTORE_SNAPSHOT_VERSION),
  kind: z.literal("unsupported"),
  reason: WooCartRestoreUnsupportedReasonV1Schema,
  appliedCouponCodes: WooAppliedCouponCodesV1Schema,
});
export type WooCartRestoreUnsupportedSnapshotV1 =
  z.infer<typeof WooCartRestoreUnsupportedSnapshotV1Schema>;

export const WooCartRestoreSnapshotV1Schema = z.discriminatedUnion("kind", [
  WooCartRestoreSupportedSnapshotV1Schema,
  WooCartRestoreUnsupportedSnapshotV1Schema,
]);
export type WooCartRestoreSnapshotV1 =
  z.infer<typeof WooCartRestoreSnapshotV1Schema>;

// This is an EXTENSION for API-001's canonical v1 checkout object, not a
// competing checkout-event/identity/phone/contact schema.
export const WooCheckoutRestoreExtensionV1Schema = z.strictObject({
  restoration: WooCartRestoreSnapshotV1Schema.optional(),
});
export type WooCheckoutRestoreExtensionV1 =
  z.infer<typeof WooCheckoutRestoreExtensionV1Schema>;

export const WooRestoreResolveRequestV1Schema = z.strictObject({
  schemaVersion: z.literal(WOO_RESTORE_RESOLVE_VERSION),
  recoveryId: WooOpaqueRecoveryIdSchema,
  token: z.string().length(43).regex(/^[A-Za-z0-9_-]{43}$/),
});
export type WooRestoreResolveRequestV1 =
  z.infer<typeof WooRestoreResolveRequestV1Schema>;

// The original customer's applied coupons remain in snapshot.appliedCouponCodes.
// This is ONLY the verified offer previously sent in initial outreach; its
// eligibility and provenance are enforced by API-003, not by Zod.
export const WooRestoreOutreachOfferV1Schema = z.discriminatedUnion("kind", [
  z.strictObject({
    kind: z.literal("NONE"),
    reason: z.enum(["NO_CONFIRMED_OFFER", "UNVERIFIABLE"]),
  }),
  z.strictObject({
    kind: z.literal("CHECKOUT_CODE"),
    code: WooNoControlTextSchema(128),
    providerDiscountId: WooNoControlTextSchema(191),
  }),
  z.strictObject({
    kind: z.literal("CHECKOUT_AUTOMATIC"),
    providerDiscountId: WooNoControlTextSchema(191),
  }),
  z.strictObject({kind: z.literal("ALTERNATIVE_PRODUCT")}),
]);
export type WooRestoreOutreachOfferV1 =
  z.infer<typeof WooRestoreOutreachOfferV1Schema>;

export const WooRestoreResolveResponseV1Schema = z.strictObject({
  schemaVersion: z.literal(WOO_RESTORE_RESOLVE_VERSION),
  status: z.literal("eligible"),
  recoveryId: WooOpaqueRecoveryIdSchema,
  checkoutKey: WooOpaqueRecoveryIdSchema,
  snapshot: WooCartRestoreSupportedSnapshotV1Schema,
  outreachOffer: WooRestoreOutreachOfferV1Schema,
});
export type WooRestoreResolveResponseV1 =
  z.infer<typeof WooRestoreResolveResponseV1Schema>;
```

**No resolver v2:** `woo.restore.resolve.v1` is the first and only restoration resolver protocol. `outreachOffer` is **mandatory** on every eligible response: use `{kind:"NONE", reason:"NO_CONFIRMED_OFFER"}` when no confirmed initial offer exists. It must NOT be inferred from `snapshot.appliedCouponCodes`. The schema must reject `woo.restore.resolve.v2` and unknown/extra keys. No fallback/dual-version adapter is authorized.

**Structural versus semantic checks:** 20-digit positive decimal strings are a bounded **wire representation**, not approval that a Woo product/variation exists, fits a platform integer or belongs to the current shop. The 43-character token matcher enforces only length/alphabet: API-002 owns canonical 32-byte base64url decoding, constant-time token comparison and authorization. A JSON parser can already collapse duplicate object keys, so Shared's parsed-value schema **cannot prove there were no duplicate raw JSON attribute names**. WooCommerce-001 must prevent duplicate/ambiguous variation keys at source; no Shared task may falsely claim that Zod detects raw JSON duplicate properties. Coupon eligibility, price, stock, restoration safety, duplicate business line identity and coupon uniqueness are checked in their owning Woo/API/Background services, not here.

### 2. Exact published exports

Create `src/woocommerce/index.ts` exporting the two version constants, `WooRestoreOutreachOfferV1Schema`/`WooRestoreOutreachOfferV1`, all other `Woo*V1Schema`/`Woo*V1`, and `WooCheckoutRestoreExtensionV1Schema`/`WooCheckoutRestoreExtensionV1` declarations above. Do not re-export Node cryptography or service-specific APIs.

Add only these `package.json` exports (maintaining existing exports unchanged):

```json
{
  "./woocommerce": {
    "types": "./dist/woocommerce/index.d.ts",
    "import": "./dist/woocommerce/index.js"
  },
  "./woocommerce/fixtures": "./src/woocommerce/__fixtures__/woo-restore-v1.json"
}
```

`package.json.files` must additionally include `src/woocommerce/__fixtures__/woo-restore-v1.json`. In `tsup.config.ts` add `"woocommerce/index": "src/woocommerce/index.ts"` to the existing `entry` map. SHARED-001 **does not bump the version or publish**; that belongs to SHARED-002.

### 3. Exact JSON fixture (`woo-restore-v1.json`)

The canonical fixture is **one JSON object** with exactly these five named properties; values must be present (do not substitute partial examples):

```json
{
  "supportedSnapshot": {
    "schemaVersion": "woo.cart-restore.v1",
    "kind": "supported",
    "appliedCouponCodes": ["save10", "freeship"],
    "lines": [
      {"productId": "101", "quantity": 2},
      {
        "productId": "202",
        "variationId": "207",
        "quantity": 1,
        "attributes": {
          "attribute_pa_color": "navy",
          "attribute_pa_size": "m"
        }
      }
    ]
  },
  "unsupportedSnapshot": {
    "schemaVersion": "woo.cart-restore.v1",
    "kind": "unsupported",
    "reason": "CUSTOM_CART_ITEM_DATA",
    "appliedCouponCodes": ["save10"]
  },
  "resolveRequest": {
    "schemaVersion": "woo.restore.resolve.v1",
    "recoveryId": "recovery_456",
    "token": "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
  },
  "eligibleResolveResponse": {
    "schemaVersion": "woo.restore.resolve.v1",
    "status": "eligible",
    "recoveryId": "recovery_456",
    "checkoutKey": "woo-example-checkout",
    "snapshot": {
      "schemaVersion": "woo.cart-restore.v1",
      "kind": "supported",
      "appliedCouponCodes": ["save10", "freeship"],
      "lines": [
        {"productId": "101", "quantity": 2},
        {
          "productId": "202", "variationId": "207", "quantity": 1,
           "attributes": {"attribute_pa_color": "navy", "attribute_pa_size": "m"}}
      ]
    },
    "outreachOffer": {
      "kind": "CHECKOUT_CODE", "code": "EXTRA15",
      "providerDiscountId": "woo-discount-915"
    }
  },
  "outreachOfferExamples": {
    "none": {"kind": "NONE", "reason": "NO_CONFIRMED_OFFER"},
    "unverifiable": {"kind": "NONE", "reason": "UNVERIFIABLE"},
    "checkoutCode": {
      "kind": "CHECKOUT_CODE", "code": "EXTRA15",
      "providerDiscountId": "woo-discount-915"
    },
    "checkoutAutomatic": {
      "kind": "CHECKOUT_AUTOMATIC", "providerDiscountId": "woo-discount-916"
    },
    "alternativeProduct": {"kind": "ALTERNATIVE_PRODUCT"}
  }
}
```

The token in the test fixture is a **synthetic shape example**, never a usable credential. The fixture is not an authorization test vector. The actual API's token comparison must be tested separately in API-002.

### 4. Location within the canonical HTTP v1 checkout event

This is an **example of API-001's canonical v1 HTTP envelope**, not a second Shared schema. It shows exactly where the restoration data goes. The usual `currency`, `total`, `items` and optional `contact` stay in the existing API-owned checkout shape.

```json
{
  "schemaVersion": "woo.activity.v1",
  "eventId": "woo-0123456789abcdef0123456789abcdef",
  "eventType": "CHECKOUT_UPDATED",
  "checkoutKey": "woo-example-checkout",
  "occurredAt": "2026-10-30T06:00:00.000Z",
  "checkout": {
    "currency": "GBP",
    "total": "80.00",
    "items": [
      {"quantity": 2, "productId": "101", "title": "T-shirt"},
      {"quantity": 1, "productId": "202", "variationId": "207", "title": "Jacket"}
    ],
    "restoration": {
      "schemaVersion": "woo.cart-restore.v1",
      "kind": "supported",
      "appliedCouponCodes": ["save10"],
      "lines": [
        {"productId": "101", "quantity": 2},
        {"productId": "202", "variationId": "207", "quantity": 1,
         "attributes": {"attribute_pa_color": "navy"}}
      ]
    }
  }
}
```

API-001 accepts HTTP v1, validates `checkout.restoration` with the published `WooCartRestoreSnapshotV1Schema`, and emits the current v1 checkout queue envelope with the **same optional restoration**. Background-001 adopts the same published schema. Neither consumer may copy/paste a competing restore validator into a local repository. The agreed pre-production target accepts one canonical HTTP v1 event contract; an absent restoration field remains unknown/unrestorable rather than a fabricated empty coupon list.

### 5. Owner-specific responsibilities

| Responsibility | Owning task |
|---|---|
| Schemas, exact v1 outreach-offer union, structural bounds, package entrypoints and canonical fixture | `ARCH-053-SHARED-001` |
| Version bump and package publication | `ARCH-053-SHARED-002` |
| PHP restorable lines, applied coupons, unsupported reason selection | `ARCH-053-WOOCOMMERCE-001`, coupon-only changes `WOOCOMMERCE-004` |
| HTTP v1 envelope validation, phone normalization, authenticated ingress, v1 queue projection | `ARCH-053-API-001` |
| Strict v1 queue validation and candidate retention | `ARCH-053-BACKGROUND-001` |
| Durable snapshot and recovery admission | `ARCH-053-DATABASE-001`, `ARCH-053-BACKGROUND-002` |
| Recovery generation URL/token issuance and freshness/order/consent gating | `ARCH-053-BACKGROUND-003`, `ARCH-053-API-002` |
| Confirmed initial outreach receipt target and v1 offer projection | `ARCH-053-BACKGROUND-004`, `ARCH-053-API-003` |
| Applying confirmed recommended checkout code and conflict notices | `ARCH-053-WOOCOMMERCE-007`, `ARCH-053-WOOCOMMERCE-008` |
| Current product/variation/cart and coupon eligibility at restore time | `ARCH-053-WOOCOMMERCE-002`, `WOOCOMMERCE-005`, `WOOCOMMERCE-006` |

Do **not** implement any of the consumer responsibilities inside Shared. These contracts carry a confirmed prior offer **as data**; they perform no dynamic discount discovery or issuance.

## Dependencies

None — independently executable after materialisation / launcher gate.

## Enables

- `ARCH-053-SHARED-002`

## Acceptance Criteria

- [ ] The exact declarations and inferred TS types above compile in `src/woocommerce/contracts.ts`; importing `@modainteract/moda-interact-shared/woocommerce` after build provides all named exports without pulling in `node:crypto`, Prisma, BullMQ, WordPress or a service-local logger.
- [ ] Supported snapshot: `schemaVersion`, `kind`, full `appliedCouponCodes` and 1..50 complete `lines` are mandatory. A plain simple line and a variation line with `attributes` parse; no display price, PII or extra fields are accepted in restore lines.
- [ ] Unsupported snapshot: exact enumerated `reason` and bounded coupon array are mandatory; `lines` is forbidden. Supported snapshot with `reason` and unsupported snapshot with `lines` both fail.
- [ ] Empty `appliedCouponCodes` on **supported** proves Woo reported none; a missing coupon list never silently defaults to `[]`. `kind:'unsupported'` with `reason:'COUPONS_UNAVAILABLE'` never becomes restorable even when its bounded array is empty.
- [ ] Resolver request accepts only schemaVersion, opaque recoveryId and 43-character base64url token; positive response accepts only eligible status, same required IDs, `snapshot.kind:'supported'` and a **required** strictly typed `outreachOffer`. Denial/invalid token/expired-generation logic remains API-owned, not fabricated in Shared.
- [ ] Checkout extension with no `restoration` parses without creating a snapshot, and a v1 extension containing the supported/unsupported snapshot parses unchanged.
- [ ] Golden fixture has all five exact keys and round trips with the appropriate canonical Shared schemas, including `outreachOfferExamples` for NONE, CHECKOUT_CODE, CHECKOUT_AUTOMATIC and ALTERNATIVE_PRODUCT.
- [ ] Boundary rejection tests cover missing coupon list, >10 coupons, empty/over-50 lines, invalid product/variation IDs, zero/fractional/overlarge quantity, >10 attribute entries, control/overlong characters, wrong enum/version/token, missing outreachOffer, extra/PII fields, automatic offer with code, alternative-product with code, incomplete CHECKOUT_CODE, invalid provider ID, and v2 resolver requests.
- [ ] No Zod coupon eligibility/stacking/expiry policy, WordPress runtime imports, duplicated API identity/contact schemas, v2 resolver, package publishing, new discount discovery or changes to ARCH-052.

## Validation

- [ ] In `moda-interact-shared`, run exact declared scripts `npm run typecheck`, `npm test`, `npm run build` (per inspected `package.json`); use the task's canonical Node bootstrap policy when required.
- [ ] Run `src/woocommerce/contracts.test.ts` with the repository's installed test runner, covering all passing/failing examples above; report exact command/result.
- [ ] After build, ESM import smoke check of the compiled `./dist/woocommerce/index.js` exports and `.d.ts` existence. Verify a packed artifact contains `src/woocommerce/__fixtures__/woo-restore-v1.json` and package `./woocommerce/fixtures` export (do NOT publish).
- [ ] Verify no unrelated bundle/entrypoint has gained Node-only modules or unwanted re-exports; `git diff --check` and only the allowed Shared files + task Completion Report are modified.
- [ ] If the dependency tree cannot support exact structural validation, do not invent a competing rule or omit a required check: report the limitation to the architect and stop.

## Stop Condition

When Work Items, Acceptance Criteria and required Validation are complete, update ONLY this task's authorised execution metadata, checklists and Completion Report, set `status: review` and return to `moda_architect`; **STOP**. Do not begin Enables, merge task branches, push `main` or change Architect Review yourself.

## Implementation Notes

**Source boundaries are exact.** `moda-interact-shared` currently has `tsup.config.ts` mapping subpaths to `dist/<subpath>/index.js` and `package.json` `exports` for browser-safe paths. Add WooCommerce as a **new subpath**, not to the root `src/index.ts` (avoids needless imports/changes). Do not create an alternative local Zod schema inside API or Background.

The only structural `.superRefine` permitted in the provided declarations is the `Record` **attribute entry count** bound; do not interpret that as permission to implement WooCommerce business rules in Shared. Zod string `.max()` limits are character counts, not necessarily byte counts: existing API's 65,536-byte HTTP payload cap remains API-001's responsibility.

Do not add `shipping`, `tax`, `checkoutUrl`, `shopId`, `generation`, `couponDiscount`, `regularPrice`, `customer`, `sessionId`, `cartItemKey`, discount-proof fields or token to a restore line/snapshot. The separate `outreachOffer` has no customer identity, vendor coupon validity decision, or external offer-discovery controls. The WooCommerce original applied-coupon list is not ARCH-052's prospective dynamic discount discovery result. `outreachOffer` is distinct, populated later from confirmed message evidence by API-003; Shared does NOT authorize or discover offers. The offer union is mandatory even before a WhatsApp message has been sent (`NONE`).

The source package `package.json` currently has `version: 2.5.1` and no `./woocommerce` entry; SHARED-001 adds entrypoints **without versioning or publishing**. The fixtures use synthetic test data only, not actual customer or provider values.

## Completion Report

### Status

Not Started

### Files Changed

None — portable task definition only.

### Work Completed

Not Started.

### Validation Results

Not Run — no implementation claimed.

### Deviations

None.

### Assumptions

Design reconciled against uploaded 2026-10-30 07:59 source snapshot; re-check source and prior task acceptance before implementation.

### Unresolved Issues

None asserted as executed; dependencies must be materialised/accepted.

### Architectural Concerns

Return any cross-service schema/provider/transaction concern to `moda_architect` before improvising.

## Architect Review

### Review Status

Pending

### Review Notes

Not Reviewed — task not executed.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

To be assessed after implementation.

### Follow-up

None.
