---
id: ARCH-059
title: Unified discount capability registration
status: agreed
coordinator: moda_architect
created: 2026-11-05
updated: 2026-11-05
---
# ARCH-059: Unified discount capability registration

## Status
Agreed design; portable definitions only. No implementation claimed. Remote publication requires approval after automatic review rejected the external destination.

## Current architecture and problem
Inspected MCP src/capabilities/resolve.ts resolves published capabilities then appends projectShopDiscountTools; execution/discount-tools.ts grants these descriptors to ACTIVE/TRIALING subscriptions with active plans independently of published membership. Shared src/commerce/built-in-tools.ts owns two version 2.0.0 descriptors. Commerce src/commerce/bootstrap/system-product-tools.ts publishes four product/shipping tools under product_search. Background src/services/recovery-offers/recovery-outreach-mcp-selector.service.ts lists the discount tools plus commerce_search_products and commerce_get_product under INITIAL_RECOVERY_OUTREACH. Its existing eligibility/combinations modules own offer decisions. Registration currently has two paths.

## Decision and exact identity
Feature key product_search, display name Product Search, owns reusable discount capabilities. Preserve ALWAYS_ENABLED/systemRequired policy. Capability/tool keys remain commerce_get_discount_options and commerce_get_discount_details, display names Get Discount Options and Get Discount Details. Initial outreach is runtime purpose INITIAL_RECOVERY_OUTREACH, not a new Feature, duplicate capability or duplicate registration. Existing checkout_recovery remains an additional host admission/entitlement gate for outreach. Both conversation and outreach use the same tools and evaluator.

Before global projection removal, setup provisions and verifies enabled product_search mappings for every active plan previously eligible for discounts, including Free. Feature conflicts fail visibly; no silent policy overwrite or narrowing of existing active-plan access. Merchant discount modes/settings/permissions remain unchanged. Test old/new eligibility on identical fixtures. Publication never grants permission by itself.

## Flow and contracts
Setup plan -> validated drafts/revisions -> FeatureCapabilities -> complete immutable release -> environment activation -> MCP shop snapshot/list -> pinned capability call -> existing policy evaluator -> Background offer validation. Each name appears once. Shared owns the versioned contracts/validators exported by @modainteract/moda-interact-shared/commerce; Commerce produces persisted releases; MCP consumes releases and produces trusted projections; Background consumes projections. Reuse existing capability/revision/grant structure and tool input/output schemas; no new contractHash or local competing schema. Trusted storage supplies authority, not model arguments or merchant prose.

## Data, consistency and failures
Existing Feature, plan mapping, draft/revision, capability, release and activation records suffice; no schema migration identified. Commerce uses canonical authoring/lifecycle/audit APIs, deterministic operation IDs and optimistic versions. Retry safely after partial failure. Never overwrite conflicting operator drafts, mutate immutable releases or rewrite historical grants. No provider calls in setup/transactions. Missing/inactive release/member/Feature/tool, duplicate name, wrong revision, stale identity or legacy built-in-only permission fails closed before provider I/O. Preserve NONE/FIXED/AI_BEST_APPLICABLE, override expiry, provider/tenant isolation, bounded model budgets and current offer revalidation. Unknown facts establish no saving. Return discovered schema gaps to architect for Database-owned work.

## Rollout and migration
PRODUCTION / COMPATIBLE ROLLOUT: existing deployed consumers and state may exist. Accept Shared contracts then publish package; deploy Commerce provisioning; dry-run/provision all previously eligible plan mappings and activate complete canonical releases while retaining old-client compatibility. Verify publication and plan parity before deploying MCP release-only admission, then Background consumption. Pause/drain affected in-flight sessions before rejecting old grant-only requests; never reinterpret old grants as new authority. No queue deletion or historical release rewrite. Record actual readiness/draining evidence in owner task reports. Roll back paired application versions and known compatible release pointer, retaining canonical releases. New runtime never silently restores global fallback.

## Repository responsibilities and scope
Shared owns contracts and a separate publication gate. Commerce owns setup/publication. MCP owns release admission and existing provider evaluator reuse. Background owns trusted context, pinning and outreach host checks. System Test owns terminal integrated verification after all implementation gates. No Database task absent an actual schema gap. No Gateway task: no Render topology/network/secret changes. No outreach agent redesign or discount evaluation changes.

## Observability
Reuse existing structured lifecycle/setup/MCP diagnostics; include bounded release/revision/capability IDs and failure reasons without tokens/customer payloads. No duplicate generic metrics or logger. Telemetry failures cannot affect correctness.

## Task graph
| Task | Owner | Status | Dependencies |
|---|---|---|---|
| ARCH-059-SHARED-001 | moda_shared | Ready | - |
| ARCH-059-SHARED-002 | moda_shared | Pending | ARCH-059-SHARED-001 |
| ARCH-059-COMMERCE-001 | moda_commerce | Pending | ARCH-059-SHARED-002, ARCH-058-COMMERCE-001 |
| ARCH-059-MCP-001 | moda_mcp | Pending | ARCH-059-SHARED-002, ARCH-059-COMMERCE-001, ARCH-058-MCP-003 |
| ARCH-059-BACKGROUND-001 | moda_background | Pending | ARCH-059-SHARED-002, ARCH-059-COMMERCE-001, ARCH-059-MCP-001, ARCH-058-BACKGROUND-001 |
| ARCH-059-SYSTEM-TEST-001 | moda_system_test | Pending | ARCH-059-SHARED-002, ARCH-059-COMMERCE-001, ARCH-059-MCP-001, ARCH-059-BACKGROUND-001 |

## Open Questions
None blocking definition. Publication selects the exact available approved version and records it before consumer pins.

## Handoff
Developer execution and explicit developer completion. No claims or implementation worktrees created. Materialise each canonical task via /moda_developer_create with its definition when ready; respect dependencies. System Test remains terminal and manually invoked.
