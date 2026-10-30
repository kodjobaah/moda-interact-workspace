---
id: ARCH-052-MCP-002
architecture_id: ARCH-052
title: Expose current shop discount catalogue to initial-outreach agent through MCP
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
- ARCH-052-SHARED-003
enables:
- ARCH-052-BACKGROUND-010
- ARCH-052-SYSTEM-TEST-001
- ARCH-052-SYSTEM-TEST-002
created: '2026-10-29'
updated: '2026-10-30'
---

# ARCH-052-MCP-002: Expose current shop discount catalogue to initial-outreach agent through MCP

## Architecture

Architecture ID: `ARCH-052`. Parent: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`. Coordinator: `moda_architect`. **Portable definition: not materialised.**

## Objective

Expose authorised discount options from the existing tenant-scoped PostgreSQL `ShopifyDiscount` catalogue through the generic `commerce_get_discount_options` MCP tool. **Do not build or call a separate provider-proof service, WooCommerce coupon-proof endpoint, or automatic eligibility-scanning workflow.** The dedicated Background agent determines basket/product relevance from returned stored discount conditions.

## Context

`ShopifyDiscount`, `providerSnapshot`, `providerStatus`, `unavailableAt`, dates and current merchant policy already exist. MCP has its own Prisma access; Background supplies checkout, merchant instructions and recovery context directly to the agent. The agent never queries PostgreSQL. ARCH-052 does **not** introduce Commerce private proof routes, WooCommerce native coupon-proof endpoints, or a pre-agent eligibility scan.

## Scope

- Retain the existing generic `CommerceToolResultSchema` and existing discount-options tool schema; do not create a feature-specific result envelope.
- Query existing shop-scoped discount catalogue and current merchant selection/provider-status fields via MCP Prisma.
- FIXED: return only currently merchant-selected records (`isAvailable=true`); AI_BEST_APPLICABLE: consider current catalogue independently of checkbox selection. NONE: do not expose a promotional offer set.
- Include condition information actually present in `providerSnapshot`; do not synthesise unsupported conditions or claims.
- Preserve existing 50-item/truncated contract, returning truncation faithfully. Do not invent pagination input or claim that 50 records exhaust the catalogue.
- Reuse existing shop authorization and tool permission gates; no recovery-attempt lookups and no direct hosted API/Commerce proof calls.
- Add focused structural and shop-isolation tests.

## Out of Scope

- Provider-specific proof endpoints and eligibility engines.
- Separate alternative-product evaluation orchestration.
- New Prisma tables/migrations, discount snapshot persistence, Commerce Studio discount-tool authoring.
- Changing the published generic MCP envelope or inventing cursor fields.

## Requirements

1. The tool reads shop-scoped current PostgreSQL discount records and does not call provider APIs or a private Commerce proof endpoint.
2. Merchant selection is `ShopifyDiscount.isAvailable`; provider status and availability are separate fields.
3. Return only source-backed condition data. The model chooses an offer, but cannot infer missing restrictions as true.
4. MCP enforces authenticated shop isolation and permissions; Background owns recovery lifecycle.
5. Preserve existing structural result schemas and truthful `truncated` reporting.
6. Log errors using the published Shared logger; do not silently swallow exceptions or include secrets or customer payloads.

## Work Items

- [ ] Implement shop-scoped discount catalogue retrieval with the existing Prisma model.
- [ ] Apply NONE/FIXED/AI selection semantics using current DB state.
- [ ] Return provider-snapshot facts without synthesising restrictions.
- [ ] Reuse existing `CommerceToolResultSchema` and tool access checks.
- [ ] Test FIXED vs AI, deleted/inactive discounts, shop isolation, no proof-service calls, truncation and failure logging.

## Interfaces / Contracts

Use existing `CommerceToolInputs.commerce_get_discount_options`, `CommerceToolOutputs.commerce_get_discount_options`, `CommerceOfferSchema` and `CommerceToolResultSchema` from the published Shared package. No new on-demand `RecoveryDiscountProof*` contract. Provider restriction detail may be returned only within already agreed contract fields; **do not invent additional wire fields**. If the existing contract cannot express material conditions, stop and return the concrete missing field to `moda_architect` for a separate contract decision.

## Dependencies

- `ARCH-052-MCP-001` — authorise the outreach purpose.
- `ARCH-052-SHARED-003` — publish the required generic Commerce/context contract extensions.

## Enables

- `ARCH-052-BACKGROUND-010`
- `ARCH-052-SYSTEM-TEST-001`
- `ARCH-052-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] Discount results are sourced from the authenticated shop’s PostgreSQL catalogue.
- [ ] FIXED uses current selected set; AI does not filter by merchant checkbox.
- [ ] No hosted private proof route, Woo proof endpoint or separate eligibility scan is called.
- [ ] Incomplete results are marked truncated; missing eligibility conditions are not fabricated.
- [ ] Tenant isolation, existing MCP authorisation and structured error logging remain enforced.

## Validation

- [ ] Run existing relevant MCP unit/integration tests for the discount tools.
- [ ] Exercise current selection modes, shop isolation and truncated-catalogue cases.
- [ ] Verify absence of calls to removed provider-proof dependencies.
- [ ] Run repository-declared typecheck/lint as applicable; record exact commands and outcomes in Completion Report.

## Stop Condition

After Work Items, Acceptance Criteria and Validation pass, complete the report, set `status: review`, return to `moda_architect`, and **STOP**. Do not start enabled tasks or merge/push main.

## Implementation Notes

Use the existing MCP database connection, discount models and feature/tool registry. The agent—not MCP—owns ranking and deciding which offer matches the checkout. MCP must return only facts established by its source data. Do not implement a new discount evaluator, provider-proof endpoint or a separate product recommendation engine.

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

Implementation must confirm package versions and the current task worktree baseline.

### Unresolved Issues

None established by implementation.

### Architectural Concerns

Escalate any unexpected provider API/auth/Shared/schema/contract gap to `moda_architect` without inventing a second implementation.

## Architect Review

### Review Status

Pending.

### Review Notes

Task definition only. No implementation accepted.

### Reviewed Files

Relevant October 29, 2026 code snapshot and task definition; no implementation source changes for this task reviewed.

### Validation Reviewed

None for implementation.

### Architecture Conformance

Pending implementation review.

### Follow-up

Materialise through the canonical launcher only after all dependency task YAMLs are Complete.
