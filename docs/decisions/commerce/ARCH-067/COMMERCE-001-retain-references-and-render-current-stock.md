---
id: ARCH-067-COMMERCE-001
architecture_id: ARCH-067
title: Test fresh stock and follow-up references in Studio
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: developer
status: in_progress
priority: 20
executor: codex
claimed_at: 2026-11-09T07:04:37Z
attempt: 1
depends_on: ["ARCH-067-SHARED-002"]
created: 2026-11-09
updated: 2026-11-09
---
# Test fresh stock and follow-up references in Studio

## Objective and binding specification
Implement the owned portion of [ARCH-067](../../../architecture/ARCH-067-product-reference-and-current-stock-parity.md). Every schema, mapping, persistence, rendering, diagnostic and compatibility rule there is normative. No merchandise-specific behavior. Dependencies must be complete before execution.

## Exact work and touch points
Own package.json/lock; src/commerce/preview/product-reads/shopify-core.ts all query/parser/normalizer paths; product-reads/registrations.ts Woo fields; preview/product-context.ts; service.ts successful completeRun path; presentation.ts/recommendation-presentation.ts; existing preview state-store conversation serialization and its tests; system-tool bootstrap/output-schema definitions located by CommerceProductSchema/commerce_get_product/commerce_search_products symbols. Apply exact provider mappings and Shared public APIs, no host copy of stock renderer/reference schema. Keep local and standalone MCP execution selectable. Preserve IDs/options and record the verified displayed pair order only after compose success, atomically with assistant body. Pass presentation to model context. Fresh PRODUCT_DETAILS verification yields stock body via Shared, including unavailable counts without falsely saying no stock. Add reader compatibility before emission per rollout gate. Target service/state-store/presentation/provider tests and production typecheck/lint; test a two-turn stock question in both execution modes. Do not register templates, send messages, fabricate checkout rows or bypass wrapper limits.

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
