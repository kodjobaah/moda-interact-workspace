---
id: ARCH-067-MCP-001
architecture_id: ARCH-067
title: Expose current stock through production MCP
task_kind: implementation
domain: mcp
repository: moda-interact-mcp
assigned_agent: moda_mcp
coordinator: moda_architect
execution_mode: agent
completion_mode: developer
status: ready
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on: ["ARCH-067-SHARED-002"]
created: 2026-11-09
updated: 2026-11-09
---
# Expose current stock through production MCP

## Objective and binding specification
Implement the owned portion of [ARCH-067](../../../architecture/ARCH-067-product-reference-and-current-stock-parity.md). Every schema, mapping, persistence, rendering, diagnostic and compatibility rule there is normative. No merchandise-specific behavior. Dependencies must be complete before execution.

## Exact work and touch points
Own package.json/lock; src/execution/policy/shopify-core.ts (all SEARCH_DOCUMENT, CATEGORY_SEARCH_DOCUMENT, GET_PRODUCT_DOCUMENT, GET_VARIANT_DOCUMENT queries/parsers/normalizers); src/execution/policy/shopify-core-executor.ts output projections; src/connections/woocommerce/direct-product-reader.ts allowlists; related provider fixtures and schema tests. Apply exact provider mappings in the architecture document. Inventory scope and variant membership cannot be weakened. Search and get schemas both admit Shared stock. Use the existing Shopify API version/credential resolver and Woo connection, no new scope/configuration/storefront API. If provider does not return a field, emit UNAVAILABLE, not an invented count. Verify provider integration fixtures for both platforms and all four Shopify query paths. Run repository type checking, lint and scoped executor/connection tests. Prove Background's MCP tool result retains stock without response projection stripping. Add required bounded diagnostics.

## Acceptance criteria
All owned requirements above and architecture contract are implemented and verified. List every actual changed path and test result. Shared behavior must be imported through published public exports; no copied cross-repository source. Unknown inventory remains distinct from zero. Existing authorization, checkout ownership, WhatsApp composition and replay rules pass regression checks. No unresolved design choices may be silently substituted; report a concrete contract conflict before implementing an alternative.

## Non-goals
No inventory mutation, new database table, token-refresh redesign, new template approval/WABA validation, category sequencing redesign or budget increase.

## Completion Report
Status: Not started.
Implementation SHA: Pending.
Validation: Pending.
Deployment/compatibility evidence: Pending.

## Architect Review
Status: Not reviewed.


## Architect exact publication handoff — 2026-11-09
SHARED002explicitlyCompleteAcceptedAttempt1; import ONLY exact @modainteract/moda-interact-shared5.11.0, integrity sha512-VwVUszfUz0Bgs0alcnjJYK0m5bY7Jt9Nb/LuPRPgrWqk/JCFYqrWbzf7rnsXP2Z8EWlf4yfojbibnOQ4/9YyOg==; archiveSHA25628db9055f58355fb9779b190beb0eccda356e20fd9a52cf0b753cd1564789309, release-source1ad0d7c47c0a9e1d3d12072b62e238aec1cc92fe/acceptedimplementation467cc1abf5afc467f73861f9830430524022bacd. No range/latestguess or sibling/internaldist import. Publicstock/reference/helper/types/canonicalpurposeoneOf+constcompiler verified.
No deployment occursbytaskclaim/Complete. Newreadersacceptlegacystock, oldstrictreadersrejectnewfield; upgradeBackground/Studio Sharedreaders beforedeployingMCPstockwriter, localStudio reader/writer upgrade together. Keep COMMERCE_PRODUCT_REFERENCE_V2_WRITE_ENABLED absent/falseuntilbothreadersdeployed, literaltrueonlyaftermanualoperationalgate interminalsystemreceipt. MCPsourcecanbeimplemented/acceptedbeforeBackgrounddependentcode; deploymentsequence remainsreader-first, no taskdependencycycle. No inventory/providerwrite, main/live/rollout/gateenablement authorized here.

Ready unchangedAttempt0/unclaimed; soleprerequisiteComplete. Canonicalprepareownsfutureclaim, no executionhere.
