---
id: ARCH-052-BACKGROUND-013
architecture_id: ARCH-052
title: Capture Shopify discount classes and own combination tags
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 32
executor: copilot
claimed_at: 2026-10-31T04:53:29Z
attempt: 1
depends_on:
- ARCH-052-BACKGROUND-011
enables:
- ARCH-052-MCP-002
- ARCH-052-SYSTEM-TEST-001
created: 2026-10-30
updated: 2026-10-31
---

# ARCH-052-BACKGROUND-013 — Capture Shopify discount classes and own combination tags

## Architecture

Architecture: `ARCH-052`. Parent: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`. Architect coordination task; **portable definition, not materialised**. No branch or runtime implementation has been created by this artifact.

## Objective

Complete Shopify Basic discount combination snapshots by persisting each discount's own tags and provider discount classes, separately from already-captured `combinesWith` allowances.

## Context

BACKGROUND-011 was accepted after Attempt 4 and is now Ready for Attempt 5 to add actionable, bounded error diagnostics. It already captures Basic `combinesWith` booleans, allowed and own same-line tags, discount classes and trusted Plus entitlement. This task covers the newly identified source-backed `minimumRequirement` threshold facts and their currency; do not start it until BACKGROUND-011 is accepted again.

## Scope

- In `moda-interact-background/src/providers/shopify-discount.provider.ts`, extend BOTH existing `DiscountAutomaticBasic` and `DiscountCodeBasic` GraphQL selections with `tags` and `discountClasses`; obtain authenticated `shop.plan.shopifyPlus` once per provider sync (not once per coupon or send) and preserve the existing bounded snapshot format and operation/error handling.
- Normalize own `tags`, provider `discountClasses` and an observed shop-level `shopifyPlus` in the snapshot without overwriting `combinesWith.productDiscountsWithTagsOnSameCartLine` (allowed tags). Preserve strict boundedness, source provenance and truncation status.
- In the SAME two Basic selections, capture `minimumRequirement` using typed GraphQL fragments: `... on DiscountMinimumSubtotal { greaterThanOrEqualToSubtotal { amount currencyCode } }` and `... on DiscountMinimumQuantity { greaterThanOrEqualToQuantity }`. Preserve source `MoneyV2.currencyCode` alongside the exact decimal amount; do not convert to floats or infer currency from merchant locale. This is source capture only, not eligibility evaluation.
- Add focused GraphQL fixture tests for mutual/nonmutual tags, empty vs unknown, truncation, mixed discount classes, observed/missing subtotal currency, quantity thresholds, unsupported discount types and provider failures.

## Out of Scope

- No changes to currently claimed `ARCH-052-SHOPIFY-001` merchant UI, `ARCH-052-MCP-005` Woo reader, `ARCH-049-BACKGROUND-003` brand sync, accepted SHARED-009/010, Woo coupon plugin or new database schema.

## Requirements

- Treat absent/malformed/overflow provider tags/classes as unknown/incomplete. Do not truncate then label `COMPLETE`.
- Source `tags` are the discount's own tags; allowed same-line tags remain inside `combinesWith`. Shopify Plus plan entitlement is obtained from the separately authenticated shop plan source; if unavailable it must be `null`, never inferred from title or tags.
- Keep the existing providerSnapshot same-table strategy. No external network operations in a DB transaction or extra provider calls per checkout.
- For `minimumRequirement` use only Shopify 2026-07 union fragment fields. Missing/malformed `MoneyV2` amount or `currencyCode` stays source-incomplete; do not claim a provable minimum/maximum. Persist the source amount and ISO currency together, preserving whether a quantity or subtotal threshold was observed. No automatic exchange-rate conversion or assumption that discount-value currency is subtotal currency.

### Source completeness and projection correctness (required)

- The Attempt 2 `normalizeConditionFacts()` source initialises `let completeness = false` and never makes it true. Replace that constant-false result with an **evidence-derived** decision: incomplete/unknown values, target truncation, unsupported type, unverified user/market constraints and source-partial combination policy remain `PARTIAL/UNKNOWN`; **only fully observed, representable and non-ambiguous facts can be `COMPLETE`** after the consumer projects SHARED-011. Keep the existing `COMBINATION_POLICY_NOT_REPRESENTED_IN_SHARED_FACTS` source reason as historical provider-snapshot provenance until MCP-002 successfully projects the policy; do not delete a reason merely to force COMPLETE.
- On arrays from provider connections, preserve `hasNextPage=true` as a loss-of-completeness reason; cap and mark incomplete rather than silently slicing and then claiming full coverage. For source tags, do not compare truncated or malformed strings; retain `null` (not a shortened supposedly authoritative tag list). Use source values without case-folding or inferring emptiness.
- `shopifyPlus` is a shop-scoped synchronised observation, not a per-offer fact discovered by the AI. Capture status once per sync and tie it to the same shop whose discounts are being fetched. A failed shop-plan read cannot create a false Plus entitlement; record `null` and the existing bounded operational failure semantics.
- Do not add a Background-013 basket eligibility helper or a direct provider call during outbound message preparation; BACKGROUND-010 will evaluate source-backed line matches from MCP-002.

### Shopify API error provenance (mandatory 31 October 2026)

The existing `src/providers/shopify-discount.provider.ts` is the Shopify
GraphQL fetch/normalisation boundary. For failed discount or shop-plan reads,
record the **actual** Shopify HTTP or GraphQL `errors[].message` and
source `extensions.code` (if present), original request ID, HTTP status and
safe path/operation; preserve SDK/network exception name/message/cause when
there is no HTTP/GraphQL error. GraphQL `errors` with HTTP 200 are failures,
not successful empty discounts. Log source error text verbatim except marked
PII/secret redaction and length truncation; internal `reasonCode`/sync state
are separate. Do not log GraphQL queries containing credentials, source
product data, request/response bodies, tokens or customer/discount codes.
Keep existing sync generation/idempotency/failure semantics; an error must not
mark source facts COMPLETE or silently overwrite the last trusted snapshot.
Use only the Shared logger and the provider-origin policy; do not build a
competing generic logger or create new external reads.

## Work Items

- [x] Add own tags/classes, shop-plan evidence and typed `minimumRequirement` (subtotal amount + currency or quantity) to both Basic GraphQL selections and normalize independently.
- [x] Ensure no regression to previously persisted `combinesWith` policy.
- [x] Test valid, malformed and ambiguous provider facts; record validation evidence.

- [x] Fix the constant-false completeness computation without losing any source uncertainty reason, and test a genuinely complete Basic fixture versus unsupported/partial/truncated fixtures.
- [x] Preserve original Shopify GraphQL/HTTP errors and SDK transport exceptions at the existing provider fetch boundary, with source provenance, separate internal reason and redaction/truncation markers.

## Interfaces / Contracts

Shopify Admin GraphQL 2026-07: `shop { plan { shopifyPlus } }` (one bounded shop-level observation per sync), `DiscountAutomaticBasic.tags`, `DiscountAutomaticBasic.discountClasses`, `DiscountCodeBasic.tags`, `DiscountCodeBasic.discountClasses` and `DiscountCombinesWith.productDiscountsWithTagsOnSameCartLine`. The resulting snapshot stores `tags: string[]|null`, `discountClasses: Array<"ORDER"|"PRODUCT"|"SHIPPING">|null`, `shopifyPlus: boolean|null`, and the existing typed `combinesWith` object. The same Basic query also retains `minimumRequirement` as source money (`amount: string`, `currencyCode: string`) or source quantity (`greaterThanOrEqualToQuantity: number`), with `null`/incompleteness for unobserved or unrecognised union cases; MCP-002 projects the monetary currency only through published SHARED-013/014. MCP-002 subsequently projects these into Shared facts. It is not an eligibility verdict.

## Dependencies

- ARCH-052-BACKGROUND-011

## Enables

- ARCH-052-MCP-002
- ARCH-052-SYSTEM-TEST-001

## Acceptance Criteria

- [x] Own vs allowed tags are not confused, and an unknown or oversized array remains non-authoritative.

- [x] Complete source fixtures may report COMPLETE only when all relevant conditions and combination inputs were observed; incomplete cases retain precise, non-empty reasons instead of permanent false or fabricated true.
- [x] Both Basic selectors preserve existing discount data, seller selections and source-backed conditions without modifying provider availability/merchant flags. Subtotal threshold facts preserve the original `MoneyV2.amount/currencyCode` pair, and quantity thresholds cannot be mistaken for a zero subtotal.
- [x] No checkout mutation or additional provider lookup on the hot path.

- [x] Mock HTTP-200 GraphQL `errors`, HTTP 4xx/5xx provider error and SDK transport exception; assert actual Shopify message/code survives logging, secrets/codes do not leak and catalogue completeness/idempotency remains correct.

## Validation

- [x] Focused Shopify provider query/normalization tests, including a positive GBP threshold amount/currency, unknown currency, source quantity threshold and unsupported minimum requirement.
- [x] Background declared lint/build and `git diff --check`.

## Stop Condition

After the specified work, validation and acceptance criteria pass, update this task's Work Items and Completion Report, set status to `review`, hand back the implementation branch and evidence, and STOP. Do not self-accept, implement enabled tasks, modify other task/index files or push main.

## Implementation Notes

Use the launcher-resolved dedicated mirrored parent/implementation worktrees and shared structured logger. All unexpected errors must be logged with bounded identifiers and propagated to the owning failure/retry boundary. Never log coupon codes, customer information, bearer tokens or raw checkout URLs. Use relative workspace edit paths; do not touch `_index.md`.

## Completion Report

### Status

Ready for Review.

### Files Changed

Changed implementation files: `moda-interact-background/src/providers/shopify-discount.provider.ts`, `moda-interact-background/tests/unit/providers/shopify-discount.provider.test.ts`, and `moda-interact-background/tests/unit/services/shopify-discount-catalogue.service.test.ts`.

### Work Completed

Both Shopify Basic GraphQL selections preserve own `tags`, `discountClasses`, `combinesWith`, and typed subtotal/quantity `minimumRequirement` facts. The Plus-plan observation is requested on the first page only and reused for subsequent pages. Tags/classes are all-or-null, preserving exact valid values and observed empty arrays while malformed, missing, oversized, or truncated inputs remain null with explicit reasons. Threshold amount and currency remain paired without inference or numeric conversion. Completeness is reason-derived; unsupported/restricted/truncated conditions retain precise reasons, and `COMBINATION_POLICY_NOT_REPRESENTED_IN_SHARED_FACTS` remains until MCP-002 projects the combination policy. Provider diagnostics preserve GraphQL messages/codes, HTTP status, request ID, operation and safe versioned path, plus bounded SDK exception diagnostics; error text is redacted before the existing Shared logger. Existing sync retry and snapshot behavior remains unchanged; no checkout lookup, schema, availability flags, merchant selection, dependency manifests, Shared/MCP code, or other repository was changed. Implementation commit `8e0fe0cf8028671823808fae827f7e750a047d99` is pushed to `origin/task/ARCH-052-BACKGROUND-013`.

### Validation Results

`npm test -- tests/unit/providers/shopify-discount.provider.test.ts tests/unit/services/shopify-discount-catalogue.service.test.ts tests/unit/workers/shopify-discount-sync.worker.test.ts` — 3 files, 42 tests passed. `npm run lint` passed. `npm run build` passed, including Prisma Client generation and TypeScript compilation. `git diff --check` passed. `npm ci` was required because the implementation worktree lacked `node_modules`; npm reported 40 advisories (27 moderate, 13 high). No dependency remediation was performed because it is outside task scope.

### Deviations

No implementation-scope deviations. Basic facts retain the required combination projection reason until MCP-002 projects the corresponding fields, preserving source provenance.

### Assumptions

No production compatibility change was required. The existing Shared logger API is used; dependency declarations remain unchanged because this task owns provider source capture, not consumer projection.

### Unresolved Issues

None blocking this task. MCP-002 must remove the preserved combination-only reason only after all corresponding facts are genuinely projected.

### Architectural Concerns

No cross-repository or database changes were needed. Architect Review remains unchanged.

## Architect Review

### Review Status

Pending.

### Review Notes

New multi-discount feature task; no implementation reviewed.

### Reviewed Files

None.

### Validation Reviewed

No implementation validation yet.

### Architecture Conformance

Pending implementation and review.

### Follow-up

None.
