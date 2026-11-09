---
id: ARCH-067-BACKGROUND-001
architecture_id: ARCH-067
title: Use remembered identities and current stock in Background
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: developer
status: pending
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on: ["ARCH-067-SHARED-002", "ARCH-067-MCP-001"]
created: 2026-11-09
updated: 2026-11-09
---
# Use remembered identities and current stock in Background

## Objective and binding specification
Implement the owned portion of [ARCH-067](../../../architecture/ARCH-067-product-reference-and-current-stock-parity.md). Every schema, mapping, persistence, rendering, diagnostic and compatibility rule there is normative. No merchandise-specific behavior. Dependencies must be complete before execution.

## Exact work and touch points
Own package.json/lock; src/commerce/host.ts model context, verified get_product observations and completion path; product-context-repository.ts validation/serialization/CAS; presentation.ts and recommendation presentation call sites; existing conversation application/replay transaction identified by productContextUpdate. No Prisma schema/table migration. Store extended v1 complete JSON object in existing references JsonB with existing revision/sourceInboundVersion fences. Use Shared recordCommerceProductPresentation with ordered pairs from actual verified rendered result; persist with final reply atomically, not on failed composition. Preserve retry/replay idempotence: replay stored body/context rather than re-read and change the count. Fresh MCP facts carry quantity into Shared verifier/composer, never extract it from history/model text. Initial outreach remains checkout-led with existing rendering and send fences; no new workflow. Test subsequent message 'first one' and variant-label follow-up, stale reference refresh, cross-shop rejection, CAS conflict, unavailable tracking and known0, failed turn leaves context unchanged, replay and final WhatsApp body parity. Run scoped host/repository/presentation tests, typecheck/lint. Record deployment reader gate before emitting new context fields.

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

StillPendingunchangedAttempt0/unclaimed: MCP001notComplete. Publicationavailability alone doesnotclearMCPdependency.
