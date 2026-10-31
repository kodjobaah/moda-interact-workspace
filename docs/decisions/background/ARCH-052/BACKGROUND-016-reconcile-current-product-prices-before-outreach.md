---
id: ARCH-052-BACKGROUND-016
architecture_id: ARCH-052
title: Reconcile observed checkout prices with current exact-product catalogue facts
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 52
executor: copilot
claimed_at: 2026-10-31T09:43:51Z
attempt: 1
depends_on:
- ARCH-052-MCP-003
- ARCH-052-COMMERCE-007
- ARCH-052-BACKGROUND-005
enables:
- ARCH-052-BACKGROUND-010
- ARCH-052-BACKGROUND-008
- ARCH-052-SYSTEM-TEST-001
- ARCH-052-SYSTEM-TEST-002
created: 2026-10-31
updated: 2026-10-31
---

# ARCH-052-BACKGROUND-016: Reconcile current product-price observations before outreach

## Architecture

Architecture ID: `ARCH-052`.

Architecture document: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`.

Coordinator: `moda_architect`. This is a **portable canonical definition — defined but not materialised**. No local developer worktree/branch, push or commit has been created by this definition.

## Objective

Provide one **Background-owned, source-backed, deterministic, read-only price-reconciliation operation** for an eligible initial recovery attempt. Compare the saved checkout **unit** prices against fresh exact product/variant catalogue observations without claiming catalogue prices are necessarily customer-payable checkout prices. Supply a typed, immutable, attempt-scoped line report consumed by BACKGROUND-010/008. Do not send WhatsApp, mutate checkout prices or introduce a new provider API.

## Context

- `CheckoutRecovery.lineItems` is JSON, currently serialised by `src/services/checkout-recovery/recovery-mappers.ts` as `{productId, variantId, title, variantTitle, sku, quantity, price}`. `price` from Shopify abandoned checkout uses `originalUnitPriceSet.presentmentMoney.amount`, **not** guaranteed current customer-payable or pre-discount merchandise total. `CheckoutRecovery.currency` is the saved checkout currency; `totalPrice` can include tax/shipping and is **not** a valid merchandise subtotal substitute. Woo line-price semantics must be checked against its source projection, not guessed.
- Published Shared `CommerceToolOutputs.commerce_get_product` provides `productId`, nullable `variantId`, nullable `unitPrice`, nullable `currency`, and `observedAt`, returned by the authenticated current-shop direct-provider MCP reader (ARCH-052-MCP-003 / COMMERCE-007). It **does not** provide a checkout/customer/market-specific payable-price quote or an equivalence proof between shop catalogue and checkout pricing contexts.
- For Shopify the current exact-variant GraphQL reader observes the shop-currency catalogue price; the saved checkout may use presentment/market pricing. Woo pricing may depend on plugins/customer/session. Equality of currency alone does **not** prove matching pricing context.
- This is price safety only. ARCH-052-BACKGROUND-010 owns discount targeting/combination and selection; BACKGROUND-008 owns final admission/Meta send; BACKGROUND-007 owns independent optional R2 product images. ARCH-053 owns Woo checkout restoration.

## Scope

1. Create a bounded pure comparison and a Background application service using current `CommerceMcpClient`, the published exact `commerce_get_product` tool and existing trusted recovery/attempt repository records. Background does not call Shopify/Woo APIs or hosted Moda API directly.
2. Evaluate every saved checkout line **required for a monetary offer or basket minimum/maximum** (up to 100 lines). If any effective whole-basket threshold is involved, **every line in the saved basket is required**; single-line checks may use a source-identified subset but still return one ordered status for each saved line. Use exact current-shop product and variant identity. If one required line cannot be verified, return an explicit incomplete result; never silently skip it or treat it as price-unchanged.
3. Expose only Background-local typed result; do not change Shared Zod, MCP endpoints, database schema, queues or the persisted `CheckoutRecovery.lineItems` format.
4. Supply injected clock, cancellation and bounded read budget for deterministic tests; preserve originating MCP/SDK/provider errors through Shared logging.

## Out of Scope

No customer-price quotation API, no checkout refresh, cart repricing, Woo restore implementation, currency FX conversion, discounts calculation, stock reservation, AI agent change, Meta send, source image download/R2 upload or new database table. Do not add direct external network access to Background. Do not revise other accepted tasks or any `docs/decisions/**/_index.md`.

## Requirements

### A. Exact implementation files and API

Create only the following new Background-owned modules (existing wiring belongs to consuming tasks):

- `src/services/recovery-pricing/checkout-price-reconciliation.types.ts` — types shown below.
- `src/services/recovery-pricing/price-comparison.ts` — pure `fingerprintRecoveryPricingBasket()`, `compareObservedLinePrices()` and `deriveCheckoutPriceReconciliation()`.
- `src/services/recovery-pricing/checkout-price-reconciliation.service.ts` — `CheckoutPriceReconciliationService.reconcile(input)`; injected trusted recovery/attempt reader, MCP exact product reader, clock and abort signal. Production adapter may use existing Background database access **only before** MCP calls and must not hold a database transaction open while making MCP calls.
- `tests/unit/services/recovery-pricing/price-comparison.test.ts` and `checkout-price-reconciliation.service.test.ts` — isolated fake DB/MCP/clock/cancellation tests. Integration checks in the consuming BG010/008 tasks.

Use these exact exported Background-local declarations in the new `*.types.ts` (do not reimplement the published `CommerceProductSchema`):

```typescript
export type LinePriceObservation = Readonly<{
  lineKey: string;                         // 'line-' + 1-based zero-padded four-digit saved index
  productId: string | null;
  variantId: string | null;
  quantity: number | null;
  checkoutUnitPrice: string | null;
  checkoutCurrency: string | null;
  catalogueUnitPrice: string | null;
  catalogueCurrency: string | null;
  catalogueObservedAt: string | null;     // source value, not inferred timestamp
  catalogueComparison: "EQUAL" | "DIFFERENT" | "INCOMPARABLE";
  checkoutPriceChange: "CONFIRMED_UNCHANGED" | "CONFIRMED_CHANGED" | "UNVERIFIABLE";
  reasonCodes: readonly string[];
}>;

export type CheckoutPriceReconciliation = Readonly<{
  shopId: string;
  checkoutRecoveryId: string;
  outreachAttemptId: string;
  generation: number;
  basketFingerprint: string;
  evaluatedAt: string;                   // injected UTC observation, ISO 8601
  lines: readonly LinePriceObservation[]; // one per saved line when 1..100; [] for invalid/overflow basket
  reasonCodes: readonly string[];            // whole-report reason, e.g. BASKET_TOO_LARGE
  currentMerchandiseSubtotal: Readonly<{ amountDecimal: string; currency: string }> | null;
  completeness: "COMPLETE" | "PARTIAL";
}>;

export type PriceReconciliationInput = Readonly<{
  shopId: string;
  checkoutRecoveryId: string;
  outreachAttemptId: string;
  expectedGeneration: number;
  expectedBasketFingerprint: string;
  signal: AbortSignal;
}>;
```

`reconcile(input): Promise<CheckoutPriceReconciliation>` reads trusted state, verifies `shopId`, recovery/attempt relation, generation, `lineItems` and fingerprint **before and after** source fetch, and produces the typed result. A stale/mismatched attempt must **fail closed** with an existing owning retry/invalid-attempt outcome, not return a fabricated comparable report. Any new local helper types/reason-code enum must live under this folder, not in Shared.

**Canonical basket fingerprint, owned once by BG016:** `fingerprintRecoveryPricingBasket(input)` is a pure SHA-256 of UTF-8 bytes of the prefix `ARCH052_PRICE_BASKET_V1\0` followed by `JSON.stringify` of **one ordered object** with properties in this exact order: `shopId`, `checkoutRecoveryId`, `generation`, `currency`, `lineItems`. Each item is a canonical ordered object with properties `productId`, `variantId`, `title`, `variantTitle`, `sku`, `quantity`, `price`, mapping missing nullable values to `null` and requiring supported primitive types (no coercion). Use the original persisted `CheckoutRecovery.lineItems` order. Output a lowercase 64-character SHA-256 hex string; never include checkout URL, phone or customer PII. No DB fingerprint field exists in this snapshot. BG010 and BG008 **must import this one helper** when constructing/verifying their Background-local basket fingerprint, rather than maintaining incompatible JSON/hash algorithms. Re-read the persisted recovery to recompute the same hash after external reads and immediately before send. Reject an unexpected caller-supplied fingerprint or changed generation; do not silently update the report to a different checkout.

### B. Trusted line and exact provider-read rules

1. Consume the persisted array order, cap at **100** entries. For **1..100 valid lines**, return exactly one line result per saved line in that order. For a non-array, empty or larger-than-100 basket, return `completeness:PARTIAL`, `lines:[]`, `currentMerchandiseSubtotal:null` and whole-report `reasonCodes:["BASKET_INVALID"]` or `["BASKET_TOO_LARGE"]`; do not issue product reads or treat it as a verified basket. Produce `lineKey = "line-" + String(index + 1).padStart(4,"0")` for every allowed saved line. Identity of a key is scoped by `checkoutRecoveryId`, `generation` and `basketFingerprint`; it is not a provider/cart line ID or stable across checkout changes.
2. A required line needs a nonempty source `productId`, a positive safe integer `quantity`, a parseable decimal saved **unit** price and currency. For Shopify, require exact variant ID to establish a variant-level price; when absent, classify the line `INCOMPARABLE` instead of equating a random first variant. Woo simple products may use `variantId:null`, provided the exact Woo product response also has `variantId:null`. Do not use product title/SKU/category or fuzzy search to match a line.
3. Call `commerce_get_product` with the exact provider IDs under the authenticated current shop and `purpose:INITIAL_RECOVERY_OUTREACH`. Verify the response through the **published** `CommerceToolOutputs.commerce_get_product`, and require exact `productId` and `variantId` match, actual current `unitPrice`, `currency` and valid `observedAt`. A null product, provider failure, identity mismatch, unavailable price, malformed timestamp or missing currency makes that line `INCOMPARABLE`. Never fall back to an alternative product/variant, untrusted model data or a previous attempt's response.
4. Deduplicate identical `(productId,variantId)` reads **within this one invocation**, retaining distinct line/quantity entries. Preserve saved checkout array order in the report. Bound to at most 100 unique reads, **4 in-flight requests**, and **20,000 ms elapsed** from injected start; propagate `signal` and abort/cancel on deadline. A budget-exceeded/unavailable read marks every affected required line `INCOMPARABLE` / `PARTIAL` with a bounded original-error diagnostic. No unbounded fanout/retry, no external operation inside a DB transaction.
5. A retry or new send preparation repeats the trusted source read (no five-minute TTL, no persisted verification certificate). An R2 image prepared earlier does not substitute for price evidence.

### C. Exact comparison, monetary and context rules

1. Validate decimal strings without exponent/scientific notation, negative values, leading/trailing whitespace or extra fractional digits. Resolve ISO-4217 currency exponent deterministically from the current Node runtime's `Intl.NumberFormat("en", {style:"currency", currency}).resolvedOptions().maximumFractionDigits` after validating `^[A-Z]{3}$`, and fail closed on invalid/unsupported code or ambiguous precision; assert explicit GBP/USD=2, JPY=0 and KWD=3 vectors in tests. Convert to integer minor units with `BigInt`/exact decimal string operations. **Never use floating point, FX conversion, `totalPrice`, inferred VAT, guessed customer market or hidden rounding.** Currency mismatch, unknown exponent, negative/invalid money or unsupported price semantics => `INCOMPARABLE`.
2. If the saved and current catalogue unit prices are valid and currency-identical, return `catalogueComparison:EQUAL` or `DIFFERENT` by exact integer comparison; otherwise return `INCOMPARABLE`. A `DIFFERENT` outcome establishes an **observed catalogue-versus-snapshot difference**, not that the customer's payable price changed. A price decrease and increase use the same factual comparison without guessing direction from untrusted strings.
3. `checkoutPriceChange` may be `CONFIRMED_CHANGED`/`CONFIRMED_UNCHANGED` **only** when both observations come from provably equivalent customer/market/session, tax, price-list and unit-price bases. A unit-price source that includes one-off coupons or tax-inclusive presentation is not equivalent to a base merchandise unit price without source-backed normalization. The present `CommerceProduct` tool supplies **no such equivalence evidence**. With current wire facts, set `checkoutPriceChange:UNVERIFIABLE` even if the numerical comparison is `EQUAL` or `DIFFERENT`; do not let a caller or model set a trusted equivalence flag. If an authoritative equivalent-context price source is genuinely required, return that cross-service contract gap to moda_architect, not invent a local proof.
4. Set `currentMerchandiseSubtotal` only when **every required line** has comparable **confirmed checkout-context** pre-discount merchandise unit-price evidence, known currency and quantity. Compute exact sum of line `unitPrice * quantity`, not tax/shipping/discounted total. With present catalogue-only MCP source the subtotal will normally be `null`; **do not substitute** a historical checkout total or sum of unmatched catalogue prices as the current checkout subtotal. `completeness:COMPLETE` means every required line has a conclusive, equivalent-context verdict; otherwise `PARTIAL`.
5. Reason codes must distinguish at least `MISSING_LINE_IDENTITY`, `MISSING_VARIANT_ID`, `SNAPSHOT_UNIT_PRICE_UNKNOWN`, `CATALOGUE_PRICE_UNAVAILABLE`, `PROVIDER_IDENTITY_MISMATCH`, `CURRENCY_MISMATCH`, `PRICE_CONTEXT_UNVERIFIED`, `CATALOGUE_PRICE_DIFFERENCE`, `SOURCE_OBSERVATION_INVALID`, `BUDGET_EXHAUSTED`. Reason codes supplement, never replace, original source diagnostics in logs. No guessed `price changed` statement in AI prompts or customer-visible messages.

### D. Failure, logs and ownership

- Expected non-comparability is typed `PARTIAL` with original stage/source error logged. Unexpected DB, SDK or transport exceptions preserve the originating `Error`/cause and must propagate to the existing owning failure/retry boundary. Use only `@modainteract/moda-interact-shared/logging`; record shop/recovery/attempt, generation, line key, provider operation, affected count, duration, reason code and source error name/message/status/metadata **after bounded sensitive-value redaction**. Do not log customer PII, checkout URLs, raw provider payloads, product descriptions, coupon codes, model prompts or credentials. A generic reason must never replace the provider's actual message.
- Never send a message, approve a discount or mutate checkout/persisted price state from this task. A typed `PARTIAL` result is consumed downstream as price uncertainty; it is not permission for a monetary claim.

## Work Items

- [x] Create the three named modules and the exact Background-local public interfaces; validate published Shared product output rather than a local imitation.
- [x] Implement the canonical source-bound `fingerprintRecoveryPricingBasket()` and use it before and after source reads; the helper is available for BG010/BG008, whose imports remain in their task scope. Verify same-shop recovery/attempt/generation without a network-held transaction.
- [x] Implement 100-line parsing, exact identity/variant reads, within-invocation deduplication, four concurrent reads, a 20-second budget and cancellation.
- [x] Implement pure exact-decimal comparison and catalogue-only vs verified-checkout-context separation, with a null subtotal when checkout context is unverified.
- [x] Add fakes/tests for Shopify and Woo line shapes, missing facts, source errors, fresh retry reads and cross-shop isolation; pass originating SDK errors to Shared structured logging.
- [x] Run declared focused tests, lint, build and whitespace validation; record launcher/worktree evidence in the Completion Report.

## Interfaces / Contracts

Source wire contract: existing published `@modainteract/moda-interact-shared/commerce` `CommerceToolOutputs.commerce_get_product`. Background `CheckoutRecovery` + `RecoveryOutreachAttempt` (persisted shop/generation/lineItems/fingerprint scope). The new local types above are not new Zod wire contracts or persisted models. BG010 consumes `CheckoutPriceReconciliation` before threshold eligibility; BG008 re-invokes reconciliation in the final send-preparation path; BG007 independently resolves optional R2 image.

Example when a saved GBP 80.00 item has a same-ID, currently observed GBP 90.00 catalogue price but equivalent checkout context is **not** proven (this is the expected present MCP behaviour):

```json
{
  "lineKey": "line-0001",
  "productId": "product-1",
  "variantId": "variant-2",
  "quantity": 1,
  "checkoutUnitPrice": "80.00",
  "checkoutCurrency": "GBP",
  "catalogueUnitPrice": "90.00",
  "catalogueCurrency": "GBP",
  "catalogueObservedAt": "2026-10-31T09:00:00.000Z",
  "catalogueComparison": "DIFFERENT",
  "checkoutPriceChange": "UNVERIFIABLE",
  "reasonCodes": ["CATALOGUE_PRICE_DIFFERENCE", "PRICE_CONTEXT_UNVERIFIED"]
}
```

## Dependencies

- `ARCH-052-MCP-003` — accepted current-shop direct Shopify/WooCommerce exact-product reader.
- `ARCH-052-COMMERCE-007` — published code-defined product tools in TEST.
- `ARCH-052-BACKGROUND-005` — accepted recovery basket presentation and merchant context.

## Enables

- `ARCH-052-BACKGROUND-010`
- `ARCH-052-BACKGROUND-008`
- `ARCH-052-SYSTEM-TEST-001`
- `ARCH-052-SYSTEM-TEST-002`

## Acceptance Criteria

- [x] Every allowed 1..100-line basket has exactly one ordered result per saved line with exact same-shop identity; invalid/101-line baskets return `PARTIAL`, `lines:[]`, the exact whole-report reason code and zero product reads, never COMPLETE.
- [x] 80.00 checkout / 90.00 catalogue GBP yields `DIFFERENT` plus `UNVERIFIABLE`, not a confirmed customer price increase; same 80.00/80.00 yields `EQUAL` plus `UNVERIFIABLE` without verified equivalence. Currency mismatch never becomes an equal-price decision.
- [x] Four concurrent / 100 unique reads / 20-second limits, injected timer and abort are covered by isolated fakes; retries make fresh observations. No database adapter or transaction is introduced around network calls.
- [x] Shopify missing variant and Woo nullable simple-product variant are handled differently; wrong product/variant/shop, null price, stale generation, invalid observation, negative money, ambiguous currency and unknown ISO exponent fail closed; GBP/USD, JPY and KWD exact-decimal tests pass.
- [x] The report never computes a trusted current subtotal from old totals or unverified catalogue prices; SDK errors are passed as `error` to the Shared logger and tool-result failures retain their source code.
- [x] No checkout writes, additional Meta sends/credits, external Shopify/Woo API calls from Background, Shared/MCP schema changes or image R2 side effects were introduced.

## Validation

- [x] `npx vitest run tests/unit/services/recovery-pricing/price-comparison.test.ts tests/unit/services/recovery-pricing/checkout-price-reconciliation.service.test.ts` — 2 files passed, 17 tests passed.
- [x] `npx eslint src/services/recovery-pricing` — passed; `npm run build` — passed (Prisma client generation and TypeScript compilation).
- [x] `git diff --check` — passed for task changes; adjacent checkout projection/snapshot regression tests passed (2 files, 17 tests). No directly relevant MCP exact-product unit test exists in this repository.
- [ ] Authenticated current-shop MCP integration fixture and cross-task BG010/BG008 fingerprint integration were unavailable in this attempt; no live provider behavior was simulated. Unit fakes cover the bounded reads, source outcomes and canonical fingerprint locally.

## Stop Condition

After the Work Items, Acceptance Criteria and Validation are complete, record real command results and physical task worktree/synchronization evidence, set this task to `review`, return its Completion Report to `moda_architect` and **STOP**. Do not implement BG010/BG008/BG007 or edit `_index.md`.

## Implementation Notes

- Follow `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, `docs/observability/shared-logging.md`, the launcher preparation packet, and existing Background test conventions.
- This task adds **no new provider proof contract**. If the final architecture requires an authoritative live checkout price quote, the current `CommerceProduct` wire does not support it; record the exact gap and stop rather than claiming a source-equivalent quote.
- Keep all new implementation source inside `moda-interact-background/`, with only this task file as the coordination exception; do not modify accepted Shared/MCP/source projects.

## Completion Report

### Status

Implementation complete; returned to `review` for Architect review. No Architect acceptance decision has been made.

### Files Changed

- `moda-interact-background/src/services/recovery-pricing/checkout-price-reconciliation.types.ts`
- `moda-interact-background/src/services/recovery-pricing/price-comparison.ts`
- `moda-interact-background/src/services/recovery-pricing/checkout-price-reconciliation.service.ts`
- `moda-interact-background/tests/unit/services/recovery-pricing/price-comparison.test.ts`
- `moda-interact-background/tests/unit/services/recovery-pricing/checkout-price-reconciliation.service.test.ts`

### Work Completed

- Added the exact Background-local report/input types and injected trusted-state/product-reader ports; parsed exact product results through the pinned Shared `CommerceToolOutputs.commerce_get_product` contract.
- Implemented the canonical SHA-256 basket fingerprint, exact BigInt decimal comparisons, explicit catalogue-only comparison semantics, and immutable partial report with `UNVERIFIABLE` checkout-price change and null current subtotal.
- Implemented trusted same-shop/recovery/attempt/generation/fingerprint checks before and after reads, ordered line results, Shopify/Woo variant rules, exact identity validation, invocation deduplication, four-way bounded concurrency, 20-second deadline and abort propagation.
- Added focused unit tests for currency precision, invalid values, basket fingerprinting, line ordering, identity isolation, provider errors, retries, concurrency, deadline and cancellation.

### Validation Results

- `npx vitest run tests/unit/services/recovery-pricing/price-comparison.test.ts tests/unit/services/recovery-pricing/checkout-price-reconciliation.service.test.ts`: 2 files passed, 17 tests passed.
- `npx eslint src/services/recovery-pricing`: passed.
- `npm run build`: passed; Prisma client generated and TypeScript compilation completed.
- Existing `tests/unit/services/abandoned-checkout-lookup.service.test.ts` and `tests/unit/services/checkout-recovery/recovery-snapshot-builder.service.test.ts`: 2 files passed, 17 tests passed.
- `git diff --check`: passed for the implementation and task changes.
- Implementation commits: `39af26b` and `38cf8a7`, pushed to `origin/task/ARCH-052-BACKGROUND-016`.
- Launcher-resolved worktrees: parent `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-052-BACKGROUND-016`; implementation `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-052-BACKGROUND-016`. Both use branch `task/ARCH-052-BACKGROUND-016`.

### Deviations

- Authenticated current-shop MCP integration was not run because no live TEST credential fixture was available. Existing Background MCP exact-product unit coverage was not present; injected service fakes were used without simulating a live provider.
- No production reader adapter or consuming-task wiring was added; BG010/BG008 own production composition and adoption of the exported canonical fingerprint helper.

### Assumptions

The consuming tasks will use the typed report without converting unknown into a positive price or discount claim, and will import the canonical fingerprint helper rather than reimplementing it.

### Unresolved Issues

The current MCP product contract cannot establish equivalent checkout/customer-market pricing context; catalogue comparisons are informational, not authoritative payable-price changes. An authenticated current-shop integration fixture and BG010/BG008 adoption remain unverified in this task attempt.

### Architectural Concerns

Any requirement for authoritative repricing must be assigned to a separately owned checkout-price source, not invented by this service.

## Architect Review

### Review Status

Pending.

### Review Notes

Planning task, no implementation reviewed.

### Reviewed Files

Inspected 31 October 2026 09:06 snapshot of current `CheckoutRecovery` storage, Background recovery mappings and published MCP product response.

### Validation Reviewed

None for implementation.

### Architecture Conformance

To be determined after implementation review.

### Follow-up

The architect may promote dependants only after BG016 is accepted Complete.
