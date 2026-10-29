---
id: ARCH-052-MCP-004
architecture_id: ARCH-052
title: Verify alternate product promotions using existing MCP provider proof
task_kind: implementation
domain: mcp
repository: moda-interact-mcp
assigned_agent: moda_mcp
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 45
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-052-MCP-001
- ARCH-052-MCP-002
- ARCH-052-MCP-003
- ARCH-052-COMMERCE-008
- ARCH-052-WOOCOMMERCE-001
enables:
- ARCH-052-BACKGROUND-010
- ARCH-052-SYSTEM-TEST-001
- ARCH-052-SYSTEM-TEST-002
created: '2026-10-29'
updated: '2026-10-29'
---

# ARCH-052-MCP-004: Verify alternate product promotions using existing MCP provider proof

## Architecture

Architecture ID: `ARCH-052`. Architecture document: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`. Coordinator: `moda_architect`. **Defined but not materialised**; no Git branch or worktree created.

## Objective

Make alternative-product discount evidence a trusted, read-only MCP operation reusing the same discount proof tool as checkout offers.

## Context

After checkout discount matching fails, the InitialOutreachOfferAgent should search for other merchant promotions; a coupon code applying to a different product is not evidence that the abandoned checkout is discounted.

## Scope

- Extend the MCP-002 built-in `commerce_evaluate_discount` handler to accept Shared-006 `target.kind="ALTERNATIVE_PRODUCT"` with exact product/variant identity from an MCP-003 `commerce_get_product` result; perform target-product shop ownership and availability check before provider proof.
- Shopify calls COMMERCE-003 current authenticated proof route (COMMERCE-008 target verification); Woo calls the existing direct Woo REST credential transport from MCP-003 to the WooCommerce-001 native GET coupon-proof endpoint using dedicated product-id header(s). **No MCP->API proxy**, no plugin cart mutation.
- Verify code/coupon or automatic promotion using the original customer’s current restrictions; if insufficient evidence, return `unavailable`/`unsupported` and do not advertise. For native sale-price promotions, only surface when provider confirms regularPrice > current price and current product availability, with no fabricated coupon code; merchant FIXED may not promote an unrelated general sale that was never selected unless separately permitted by its selected discount.
- The system returns Shared-008 `VerifiedAlternativeProductPromotionSchema` carrying a trusted product permalink and separate promo target; never claim it reduces the abandoned checkout. Set proof expiry <= provider contract limit and recheck at preparation if stale.
- Coverage tests: no checkout match but one related promoted SKU, only unrelated valid promo, product now unavailable, old price changed, wrong shop, customer not eligible, no selected promotions in FIXED, AI includes unselected catalogue promo, failure/partial scan, unavailable proof and read-only Woo callback.

## Out of Scope

No additional database table/column/migration, migration backfill, alternate provider proxy, customer-facing product database/cache, secret-bearing logs, unrelated architecture or other repository implementation.

## Requirements

- Only assigned repository code and this task report may be changed. Do not implement Enabled tasks.
- Follow `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, the exact launcher packet and dedicated mirrored parent/implementation worktrees. Re-read the authoritative task before claiming.
- Use `@modainteract/moda-interact-shared/logging` for new Node structured logs; record unexpected exceptions with bounded reason codes and propagate to the owning error/retry boundary. Never log credentials, complete URLs, coupon codes, raw provider payloads or customer personal data.
- Authenticate every shop/grant/call with its trusted identity, enforce provider deadlines, bounded pagination, strict response projection, customer/tenant separation and read-only provider behavior.
- This is a **pre-production breaking design**. Do not add legacy adapters/backfills or change conversation CommerceAgent lifecycle.

## Work Items

- [ ] Implement exactly the scoped files and runtime behavior.
- [ ] Add deterministic unit and negative/security tests.
- [ ] Run the required validation; record all commands and evidence in Completion Report.

## Interfaces / Contracts

Built-in MCP `commerce_evaluate_discount` target `ALTERNATIVE_PRODUCT` (SHARED-006); Shared-005 alternative-product provider evidence (inside existing generic MCP result envelope); WooCommerce-001 native proof and COMMERCE-008 Shopify proof; no new published tool or Commerce Studio authoring.

## Dependencies

- `ARCH-052-MCP-001` — must be Complete and architect-accepted before this task starts.
- `ARCH-052-MCP-002` — must be Complete and architect-accepted before this task starts.
- `ARCH-052-MCP-003` — must be Complete and architect-accepted before this task starts.
- `ARCH-052-COMMERCE-008` — must be Complete and architect-accepted before this task starts.
- `ARCH-052-WOOCOMMERCE-001` — must be Complete and architect-accepted before this task starts.

Dependencies are authoritative in YAML; system tests are terminal validation and must never block implementation.

## Enables

- `ARCH-052-BACKGROUND-010`
- `ARCH-052-SYSTEM-TEST-001`
- `ARCH-052-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] Alternative product promo is a real, currently redeemable provider-backed offer, not an LLM assertion.
- [ ] FIXED never searches unselected merchant codes; AI may inspect provider-current catalogue under bounded budgets.
- [ ] Customer message distinguishes separate offer from existing checkout discount.
- [ ] No MCP-to-API call, cart mutation or credential leak.

## Validation

- [ ] MCP alternative proof unit tests with mocked provider reads.
- [ ] Integration tests for Shopify/Woo, eligibility and expired proofs.
- [ ] MCP typecheck/lint/build, `git diff --check`.

Use the scripts actually declared by the repository's package/tooling. Record unrun checks as unverified; include `git diff --check`.

## Stop Condition

Once Work Items, acceptance criteria and validation are met, set task status to `review`, complete its report, return to `moda_architect` and **STOP**. Do not mark it Complete, publish another task, merge branches or push `main`.

## Implementation Notes

Expected workspace-relative owned source paths (confirm paths exist in checked-out worktree before editing):

- `moda-interact-mcp/src/execution/policy/discount-tool-executor.ts` (from MCP-002)
- `moda-interact-mcp/src/execution/policy/alternative-product-proof.ts` (new)
- `moda-interact-mcp/src/connections/woocommerce/provider.ts`
- `moda-interact-mcp/src/runtime/service-ports.ts`
- `moda-interact-mcp/tests/unit/execution/policy/`

## Completion Report

### Status

Not Started — portable definition; no task claim.

### Files Changed

None yet.

### Work Completed

None yet.

### Validation Results

Not run.

### Deviations

None reported.

### Assumptions

Confirm execution baseline in dedicated task worktree.

### Unresolved Issues

None established.

### Architectural Concerns

Return material contract/security/proof gaps to `moda_architect` without inventing a workaround.

## Architect Review

### Review Status

Pending.

### Review Notes

Definition only; no implementation accepted.

### Reviewed Files

Task definition and uploaded 29 October 2026 snapshot only.

### Validation Reviewed

No implementation tests yet.

### Architecture Conformance

Pending implementation review.

### Follow-up

Materialise through canonical task launcher only after dependencies are Complete.
