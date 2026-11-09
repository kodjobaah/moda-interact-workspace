---
id: ARCH-067-SHARED-001
architecture_id: ARCH-067
title: Define shared references, stock facts and WhatsApp composition
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: developer
status: ready
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on: []
created: 2026-11-09
updated: 2026-11-09
---
# Define shared references, stock facts and WhatsApp composition

## Objective and binding specification
Implement the owned portion of [ARCH-067](../../../architecture/ARCH-067-product-reference-and-current-stock-parity.md). Every schema, mapping, persistence, rendering, diagnostic and compatibility rule there is normative. No merchandise-specific behavior. Dependencies must be complete before execution.

## Exact work and touch points
Owned touch points: src/commerce/schemas.ts; product-context.ts and tests; instructions.ts; runner/graph/nodes/invoke-model.ts; runner/index.ts; runner/preflight.ts; model/openrouter-model-client.internal.ts serialization tests; presentation/facts.ts, fact-messages.ts, schemas.ts, compose.ts, render.ts, index.ts; commerce public index.ts and public import validation scripts. Implement every Shared contract in the architecture document; extend exported types and generated tool output JSON schemas through existing generation. Do not create parallel inventory facts/renderers in hosts. Test built public runtime and declarations, not only source imports. Tests: legacy context/product fixtures; selected options arbitrary names (height, finish, volume as well as color); presentation ordered [20,3] survives recency sorting [3,20]; ambiguous labels require clarification; all stock states and0; invalid/negative/unsafe count normalization semantics; context size/TTL/ownership; no stale count authority; exact WhatsApp body and locale/length boundaries. Run npm run typecheck, npm run build and targeted product-context/presentation/runner/model tests using repository scripts. Record accepted source/build archive provenance for publication.

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
