---
id: ARCH-052-SHARED-005
architecture_id: ARCH-052
title: Define a typed provider discount-evidence payload for on-demand MCP calls
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

# ARCH-052-SHARED-005: Define a typed provider discount-evidence payload for on-demand MCP calls

## Architecture

Architecture ID: `ARCH-052`. Parent: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`. Coordinator: `moda_architect`.

Task materialised and claimed through the prepared launcher on 2026-10-29. The launcher created the dedicated mirrored task worktrees, verified both against their branch heads, initialized the implementation submodules, and pushed the Attempt 1 claim before implementation began.

## Objective

Create the **exact structural wire contract** for a targeted discount-evidence request and response exchanged by MCP and the provider-backed discount capability. The agent invokes this only when it needs evidence; it is **not** a mandatory catalogue-wide eligibility scan. No business rules are implemented in Zod.

## Context

The snapshot has `CommerceEvidenceSchema`, but that contract requires a conversational `turn`, `grantId` and `releaseId`; initial outreach has no inbound conversation turn. `src/recovery-offer-proof.ts` and this task's proposed exports do not yet exist. `CommerceToolResultSchema` already supplies the generic MCP success/error envelope; it is not replaced.

## Scope

- Create the exact browser-safe module and package subpath described under Interfaces / Contracts.
- Define only the identity, target, outcome and evidence **data shapes** shown below. Maintain exact naming and nullability.
- Add schema-only contract fixtures and type inference checks. Do not implement discount eligibility, savings computation, expiry comparisons, store-host checks or offer selection in Shared.
- Document consuming runtime responsibilities in the owning MCP/Commerce/WooCommerce tasks; do not implement them here.

## Out of Scope

- No bulk discount scan, provider HTTP call, database access, coupon creation/application, AI decision or new MCP result envelope.
- No pre-production migration, historical compatibility adapter, new table/column, private HMAC scheme or conversation-runner change.

## Requirements

- **Zod boundary:** types, required/nullable fields, literals, discriminants, lexical formats already provided by existing Shared primitives and unknown-key rejection only. Do not introduce `.refine()`, `.superRefine()`, `.transform()` or `.check()` for business rules.
- **MCP/provider boundary:** independently confirm the requested discount and target belong to the authenticated shop/recovery; decide eligibility, applicable code/method pairing, supported restrictions, savings, evidence freshness and whether evidence authorises a marketing claim. These checks are **not** part of `RecoveryDiscountProofResultSchema`.
- Existing conversation tool inputs and the generic `commerce.v1` success/error envelope remain unchanged.
- Follow the mirrored dedicated-worktree and start-of-attempt evidence rules in `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, and the prepared launcher packet. No unsafe logs, silent exception swallowing or competing logger; use Shared structured logging if runtime logging is introduced.

## Work Items

- [x] Create `moda-interact-shared/src/recovery-offer-proof.ts` with the exact source below.
- [x] Add `recovery-offer-proof` to `moda-interact-shared/tsup.config.ts` and `moda-interact-shared/package.json` exports with the exact entrypoint below.
- [x] Add `moda-interact-shared/src/recovery-offer-proof.test.ts` with the positive/negative schema cases below.
- [x] Attempt the repository's declared `typecheck`, `test` and `build` validations; document the unavailable `npm` entrypoint and sandbox limitations below.

## Interfaces / Contracts

**Create `moda-interact-shared/src/recovery-offer-proof.ts` exactly as follows:**

```typescript
import { z } from "zod";
import {
  IdSchema,
  HashSchema,
  DateSchema,
  CurrencySchema,
  MoneySchema,
} from "./commerce/primitives";

export const RecoveryDiscountTargetSchema = z.discriminatedUnion("kind", [
  z.strictObject({
    kind: z.literal("CHECKOUT"),
  }),
  z.strictObject({
    kind: z.literal("ALTERNATIVE_PRODUCT"),
    productId: IdSchema,
    variantId: IdSchema.nullable(),
  }),
]);
export type RecoveryDiscountTarget =
  z.infer<typeof RecoveryDiscountTargetSchema>;

const RecoveryProofIdentityShape = {
  schemaVersion: z.literal(1),
  shopId: IdSchema,
  checkoutRecoveryId: IdSchema,
  outreachAttemptId: IdSchema,
  catalogueDiscountId: IdSchema,
  providerDiscountId: IdSchema,
  checkoutFingerprint: HashSchema,
  target: RecoveryDiscountTargetSchema,
};

export const RecoveryDiscountProofRequestSchema = z.strictObject({
  ...RecoveryProofIdentityShape,
});
export type RecoveryDiscountProofRequest =
  z.infer<typeof RecoveryDiscountProofRequestSchema>;

export const RecoveryEligibleDiscountProofSchema = z.strictObject({
  ...RecoveryProofIdentityShape,
  checkedAt: DateSchema,
  outcome: z.literal("eligible"),
  method: z.enum(["CODE", "AUTOMATIC"]),
  code: z.string().nullable(),
  verifiedDescription: z.string(),
  currency: CurrencySchema.nullable(),
  savings: MoneySchema.nullable(),
  expiresAt: DateSchema,
  verifiedConditions: z.array(z.string()),
});

export const RecoveryNonEligibleDiscountProofSchema = z.strictObject({
  ...RecoveryProofIdentityShape,
  checkedAt: DateSchema,
  outcome: z.enum([
    "ineligible", "unsupported", "unavailable", "stale",
  ]),
  reasonCodes: z.array(z.string()),
});

export const RecoveryDiscountProofResultSchema = z.union([
  RecoveryEligibleDiscountProofSchema,
  RecoveryNonEligibleDiscountProofSchema,
]);
export type RecoveryDiscountProofResult =
  z.infer<typeof RecoveryDiscountProofResultSchema>;
```

**Package entrypoint additions (do not replace the existing export map):**

```typescript
// moda-interact-shared/tsup.config.ts — add to entry
"recovery-offer-proof": "src/recovery-offer-proof.ts",
```

```json
{
  "./recovery-offer-proof": {
    "types": "./dist/recovery-offer-proof.d.ts",
    "import": "./dist/recovery-offer-proof.js"
  }
}
```

`commerceToolResultSchema(RecoveryDiscountProofResultSchema)` remains the mechanism for checking an MCP `status: "OK"` result's `data`. Tool failures continue using the existing `CommerceToolResultSchema` `status: "ERROR"` branch.

**Illustrative, structurally valid request:**

```json
{
  "schemaVersion": 1,
  "shopId": "shop_123",
  "checkoutRecoveryId": "recovery_456",
  "outreachAttemptId": "attempt_789",
  "catalogueDiscountId": "discount_123",
  "providerDiscountId": "provider_123",
  "checkoutFingerprint": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "target": { "kind": "CHECKOUT" }
}
```

**Illustrative complete eligible result:**

```json
{
  "schemaVersion": 1,
  "shopId": "shop_123",
  "checkoutRecoveryId": "recovery_456",
  "outreachAttemptId": "attempt_789",
  "catalogueDiscountId": "discount_123",
  "providerDiscountId": "provider_123",
  "checkoutFingerprint": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "target": { "kind": "CHECKOUT" },
  "checkedAt": "2026-10-29T18:00:00.000Z",
  "outcome": "eligible",
  "method": "CODE",
  "code": "RUN20",
  "verifiedDescription": "20% off running shoes",
  "currency": "GBP",
  "savings": "20.00",
  "expiresAt": "2026-10-29T18:01:00.000Z",
  "verifiedConditions": ["PRODUCT_MATCH"]
}
```

**Illustrative complete non-eligible result:**

```json
{
  "schemaVersion": 1,
  "shopId": "shop_123",
  "checkoutRecoveryId": "recovery_456",
  "outreachAttemptId": "attempt_789",
  "catalogueDiscountId": "discount_123",
  "providerDiscountId": "provider_123",
  "checkoutFingerprint": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "target": {
    "kind": "ALTERNATIVE_PRODUCT",
    "productId": "product_123",
    "variantId": null
  },
  "checkedAt": "2026-10-29T18:00:00.000Z",
  "outcome": "unsupported",
  "reasonCodes": ["PROVIDER_RESTRICTION_UNKNOWN"]
}
```

**Business checks explicitly delegated to the owning runtime (not Zod):**

| Rule | Owning runtime |
|---|---|
| `shopId`, recovery, attempt and target represent the current authorised operation | MCP |
| Request/result IDs and fingerprint are equal; no cross-shop contamination | MCP/provider adapter |
| A `CODE` offer has a real redeemable code, an `AUTOMATIC` offer has no code | Provider-specific eligibility implementation |
| Dates describe an acceptable evidence lifetime; selected discount still current | MCP/Background send boundary |
| Savings reflect actual provider rules, not an AI guess | Provider-specific eligibility implementation |
| Claiming “eligible” is supported by known conditions; unsupported restrictions fail safely | Provider-specific eligibility implementation |

These rules **must not be reintroduced as Zod refinements**. In particular, a structurally valid `eligible` result with `method: "CODE", code: null` may pass the schema but **must not** be authorised for sending by the MCP/provider business layer.

## Dependencies

None.

## Enables

- `ARCH-052-SHARED-003`

## Acceptance Criteria

- [x] Both schemas and inferred TypeScript types exactly match the specified module; existing `CommerceEvidenceSchema` is untouched.
- [x] A full `CHECKOUT` and `ALTERNATIVE_PRODUCT` request and both result branches parse.
- [x] Missing IDs, unknown fields, invalid discriminants, missing alternative `productId`, malformed `checkoutFingerprint` and missing `checkedAt` fail structural parsing.
- [x] No business-rule `.refine`, `.superRefine`, `.transform` or `.check` is introduced; `CODE`/code consistency, date ordering and identity match are verified in the owning runtime rather than the Shared schema.
- [x] Generic MCP success/error envelope and conversation contracts remain unchanged.

## Validation

- [x] Attempt `npm run typecheck`, `npm test`, `npm run build` in Shared (see the recorded environment limitation and equivalent tool results below).
- [x] Structural fixtures using `safeParse` and `commerceToolResultSchema` cover the specified valid and invalid cases.
- [x] `git diff --check`; confirm browser-safe subpath export in generated package and no Node-only dependencies.

## Stop Condition

After Work Items, Acceptance Criteria and Validation have passed, fill the Completion Report, set `status: review`, return the mirrored task-branch evidence to `moda_architect`, and **STOP**. Do not start dependent tasks or mark your own task Complete.

## Implementation Notes

The source snippet is **normative for this review draft**: do not rename fields, invent proof statuses, add an additional result envelope, or move business policy into the schema. If a current source conflict prevents it, report the exact conflict for architect review instead of choosing a replacement contract.

## Completion Report

### Status

Review requested. Attempt 1 was claimed and pushed by the prepared launcher; implementation commit `aa4aaef` is pushed on `task/ARCH-052-SHARED-005`.

### Files Changed

`src/recovery-offer-proof.ts`, `src/recovery-offer-proof.test.ts`, `tsup.config.ts`, and `package.json` in `moda-interact-shared`.

### Work Completed

- Added the exact strict request and eligible/non-eligible proof schemas and inferred types, reusing the existing Shared primitives.
- Added the `recovery-offer-proof` tsup entry and package export without changing existing exports.
- Added runtime fixtures for both target kinds and result branches, the generic MCP success/error envelopes, missing IDs/timestamp, unknown keys, invalid target discriminant, missing alternative product ID, and malformed fingerprint.
- Kept business-rule checks outside Shared. No changes were made to `CommerceEvidenceSchema`, MCP envelopes, or conversation contracts.

### Prepared Launcher and Start-of-Attempt Synchronization Evidence

- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-052-SHARED-005`, branch `task/ARCH-052-SHARED-005`, start HEAD `71cf6915ff1a17911d10252e1aacd670c97f3bc5`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-052-SHARED-005`, repository `moda-interact-shared`, branch `task/ARCH-052-SHARED-005`, start HEAD `b4ebb52a2b5ae931b78983c1b1b800cf7e6b579e`.
- The prepared launcher synchronized both task branches with their origin state before execution; both were at the reported start HEADs, no fast-forward was needed, and the implementation worktree recursive submodule check reported `ready` (no recursive submodule entries).
- Attempt 1 claim commit `1880dc3897d4589718fa0d3c8560ef0d3aac8d32` was pushed before implementation. Implementation commit `aa4aaef` was pushed after validation. The task/report branch is now set to `review` and pushed separately.

### Validation Results

- The Shared checkout did not contain `node_modules`, and `npm` is not installed in the environment. The existing dependency installation from the canonical Shared checkout was used through a temporary validation copy under `/private/tmp/arch052-shared005-validation`; no validation-only files were added to the task worktree.
- Typecheck passed using the installed TypeScript compiler (`tsc --noEmit`).
- The focused proof contract tests passed: 3 tests, 0 failures, run with Node's test runner and the installed `tsx` loader.
- Build passed using the installed `tsup` executable. It generated `dist/recovery-offer-proof.js` and `dist/recovery-offer-proof.d.ts`; the package export targets both files, and the generated module has no Node-only imports.
- Full-suite attempt: the package's `tsx --test` launcher could not open its IPC socket (`listen EPERM`), so the equivalent Node test runner with the `tsx` loader was used. It reported 379 tests: 373 passed, 5 failed, and 1 skipped. All five failures were existing tests whose local HTTP server could not listen because the sandbox denied `127.0.0.1` (`listen EPERM`): “OTLP log export receives the same safe structured record” (`src/logging/node.test.ts`), “direct Loki transport receives sanitized structured JSON with bounded labels” (`src/logging/node/loki.test.ts`), “Prisma and BullMQ adapters emit joined traces and bounded metrics” (`src/observability/adapters.test.ts`), and “preload exports HTTP, fetch, metrics, correlated logs, and Loki” plus “invalid metric configuration does not abort trace initialization” (`src/observability/preload.test.ts`). The focused task tests passed separately.
- `git diff --check` passed. Build inspection confirmed browser-safe generated output and exact package subpath wiring.

### Deviations

The required npm scripts could not be invoked literally because npm is unavailable. Equivalent installed tools ran from a temporary copy. The full suite cannot pass in this sandbox because its network-listener tests are denied; this does not affect the focused contract tests.

### Assumptions

The existing Shared dependency installation is compatible with this checkout; the toolchain scripts completed typecheck and build against the copied task sources.

### Unresolved Issues

Full Shared-suite validation requires an environment that permits the existing localhost listener tests. No implementation failures were observed in the focused tests, typecheck, or build.

### Architectural Concerns

Report discovered cross-repository/credential/provider-proof issues to `moda_architect`.


## Architect Review

### Review Status

Accepted

### Review Notes

The task is correctly submitted in `review` at Attempt 1. The implementation branch `task/ARCH-052-SHARED-005` is clean at `aa4aaef` and contains only the four scoped source, fixture and export files. The schemas match the normative task contract: they reuse the existing `IdSchema`, `HashSchema`, `DateSchema`, `CurrencySchema` and `MoneySchema`; preserve the required identity and target fields; model eligible and non-eligible result branches; and keep target/identity matching, code/method consistency, evidence freshness, savings correctness and marketing authorization outside Zod. The generic `commerce.v1` envelope remains unchanged. No database, provider runtime, MCP execution or unrelated shared contract implementation was added.

The Completion Report provides the required dedicated parent and implementation worktree, branch synchronization, recursive submodule and claim evidence. The required focused proof tests, typecheck, build, generated package subpath inspection, browser-safety inspection and `git diff --check` passed. The full Shared test suite was attempted with the equivalent Node test runner because npm and the package launcher could not run in the sandbox; its five failures are identified local HTTP-listener tests blocked by sandbox `listen EPERM`, while the three task-specific tests passed. This task's Validation explicitly calls for the attempt and documentation of unavailable npm/sandbox limitations; the environment failures are recorded as unresolved limitations rather than passing results.

### Reviewed Files

- Attempt 1 Completion Report, launcher evidence, task Acceptance Criteria and Validation.
- Shared implementation branch `task/ARCH-052-SHARED-005` at `aa4aaef`, clean with a four-file diff from `origin/main`.
- `src/recovery-offer-proof.ts` and `src/recovery-offer-proof.test.ts`.
- `tsup.config.ts` and `package.json`.
- Existing `src/commerce/primitives.ts`, `src/commerce/schemas.ts`, and the ARCH-052 dependency plan.

### Validation Reviewed

Reviewed the recorded typecheck, focused tests (3 passed), build, public subpath/generated artifact inspection, browser-safety result, and `git diff --check`. Reviewed the full-suite attempt and its five identified sandbox listener failures. No tests were rerun for this review.

### Architecture Conformance

The implementation provides the single Shared-owned structural contract required for on-demand discount evidence and leaves tenant authorization, provider eligibility and business consistency to their owning runtimes. It conforms to the task, repository boundaries, and ARCH-052.

### Follow-up

Set this automatic-completion task to `complete`. Keep `ARCH-052-SHARED-003` `pending`; its other Shared implementation prerequisites have not reached `complete`. The five sandbox-blocked existing listener tests remain a validation-environment limitation and are not represented as passing.
