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
status: complete
priority: 20
executor: null
claimed_at: null
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
Status: Ready for Review — Attempt 1.
Implementation SHA: `cb7d002945482342a426daf6f7fdcc4cb17092c6`; committed and pushed to Commerce `task/ARCH-067-COMMERCE-001`.

### Implemented coverage
- Pin exact published Shared 5.11.0 and the handoff integrity; all stock normalization, reference schemas/recording, fact rendering, candidate rendering, composition and wrapper validation use public package exports. No local Shared source/schema fork.
- Shopify variant search, category search, exact variant and product reads request/parse tracking and inventory quantity. Exact variants map KNOWN/VARIANT, NOT_TRACKED or UNAVAILABLE; product-only identity remains product-only and never borrows a variant count. Woo product/variation allowlists include manage_stock and normalize product/variation/parent-managed/variable-parent semantics independently from availability. Negative counts normalize to zero using the public helper; malformed, fractional and unsafe counts stay unavailable.
- Successful verified detail/options/recommendation composition supplies ordered native pairs. Public candidate and wrapper renderers associate exact full/first/minimal fallback identities without parsing prose; only actual displayed pairs are recorded. Failed/cancelled/replayed/foreign-owner turns cannot replace context/history. Existing Redis/in-memory fencing persists successful context with the actual assistant body.
- Compatible readers accept old and additive v1 JSON; default-false, server-only literal-true write gate strips selectedOptions/presentation before persistence while retaining existing identity/freshness fields. Stock/prices never become persisted reference authority. No gate enabled or deployed by this task.
- Runner/OpenRouter context retains native selectedOptions and latest displayed order. Host instructions describe ordinal ambiguity and current-stock evidence without clothing/color-specific parsing.
- Existing Shared structured logger families carry bounded native identity/status/scope/reason and context/presentation counts with shop/conversation/run correlation; no quantity, provider body, credential or customer prose logging.
- Existing public-schema-derived policy authoring output projections automatically include optional stock from pinned CommerceToolOutputs. Equality tests prove exact schema projection; canonical draft definitions/input contracts and historical fixtures stay unchanged. No persisted database releases patched or sync/apply commands run.

### Actual changed paths
- `.env.example`
- `README.md`
- `package-lock.json`
- `package.json`
- `src/commerce/preview/presentation.ts`
- `src/commerce/preview/presented-pairs.ts`
- `src/commerce/preview/product-context.ts`
- `src/commerce/preview/product-discovery-instructions.ts`
- `src/commerce/preview/product-reads/registrations.ts`
- `src/commerce/preview/product-reads/shopify-core.ts`
- `src/commerce/preview/recommendation-presentation.ts`
- `src/commerce/preview/service.ts`
- `tests/arch067-model-context.test.ts`
- `tests/arch067-stock.test.ts`
- `tests/preview-redis-lua.test.ts`

### Agent-executed validation
- `npx vitest run tests/arch067-stock.test.ts tests/arch067-model-context.test.ts tests/local-product-query-contracts.test.ts tests/local-product-woocommerce.test.ts tests/local-product-search-diagnostics.test.ts tests/studio-tool-clients.test.ts tests/arch066-preview-presentation.test.ts tests/arch066-provider-facts.test.ts tests/preview-service.test.ts tests/preview-integration.test.ts tests/preview-redis-lua.test.ts tests/system-commerce-tool-sync.test.ts tests/system-product-response.test.ts`: PASS, 13 files / 129 tests, exit 0. Includes actual local Redis fencing/atomic additive JSON/replay, zero/positive/safe-max/negative/fractional/missing tracking cases, two composed-turn fresh-stock followups through local and mocked private MCP transport, wrapper BODY full/first/minimal pair preservation, exact public generated authoring schema, and real runner/OpenRouter request serialization (synthetic provider transport only).
- `npm run typecheck:build`: PASS, exit 0. Initial install omitted scripts and lacked generated Prisma client; ran `npx prisma generate --schema database/prisma/schema.prisma`, then production types passed. No schema/migration/pin edits.
- Scoped `npx eslint` over all changed TypeScript source and test paths: PASS, exit 0, no warnings.
- `git diff --check`: PASS, exit 0.
- Locked package integrity equals `sha512-VwVUszfUz0Bgs0alcnjJYK0m5bY7Jt9Nb/LuPRPgrWqk/JCFYqrWbzf7rnsXP2Z8EWlf4yfojbibnOQ4/9YyOg==`.

### Deployment / compatibility evidence
README and .env.example document reader-first Studio/Background deployment before MCP stock writer and default-false reference gate until both readers deploy with manual terminal system-test operational receipt. New local Studio reader/writer upgrade together. Legacy outputs with omitted stock remain readable; legacy stored context loads without rewriting. Task submission does not imply actual reader deployments, gate enablement or terminal system validation. No deployed environment/model/provider calls, main integration, remote sync/apply, inventory mutation, cleanup/reset/seed or WhatsApp send performed. Deterministic standalone MCP coverage uses an in-process mocked private transport, not a deployed endpoint.

### Prepared execution / physical isolation evidence
Canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-067-COMMERCE-001`; parent branch: `task/ARCH-067-COMMERCE-001`.
Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-067-COMMERCE-001`; implementation branch: `task/ARCH-067-COMMERCE-001`.
Shared workspace/implementation checkout switched or mutated for task work: no. Another task worktree reused: no.
Start-of-attempt parent remote task fast-forward: not-needed; parent origin/main incorporated: yes.
Implementation remote task fast-forward: not-needed; implementation origin/main: already-current.
Recursive submodule sync/update: passed; exact database commit `039778a4a472db7d09e6b077bb8c8d7c82a58129`, ready.
Durable Attempt 1 claim: `42e22d9d5f08c4131b36bd42a79988d397c69a89`, pushed by launcher. No duplicate preparation/claim.

### Architectural concerns / review disposition
No unresolved implementation contract conflict. No Changes Requested review preceded Attempt 1; exact publication handoff is satisfied. Required implementation and bounded local validation are complete; rollout/manual system-test gates remain intentionally unexecuted. Completion mode remains developer. Repository agent does not accept/complete its own task.

## Architect Review
Status: Accepted — Attempt1,2026-11-09.

### Review Notes
Independently inspected actual implementationcb7d002945482342a426daf6f7fdcc4cb17092c6 and report71d4be67c94654cb6804df1743039d0762175b69 against the binding architecture. Shopify search/category/exact variant projections preserve tracking/quantity, normalize counts via public Shared helper, and keep product-only identity from borrowing first-variant stock. Woo mapping explicitly distinguishes simple/variant, untracked, parent-managed and variable-parent unknown counts; availability remains independent. Shared5.11 schemas/renderers preserve known zero vs unknown and exact locale/wrapper limits. No local stock renderer/schema copied.

Exact presented pair order derives from verified identities and public full/first/minimal candidates, including prepared wrapper rendering, never prose parsing. Successful composition only records identities via public helper before existing owner-fenced atomic history/context finalization. Stock/prices are not persisted reference authority. Reader supports additive/legacy v1 JSON; server-only literaltrue gate defaults off and strips only additive reference fields. Model serialization carries selectedOptions/latest presentation. Provider/final-verification diagnostics use existing logger families and bounded identity/status/reason fields, no inventory quantity/secrets/prose. Generated authoring schema equality covers actual public stock projection without patching persisted releases.

### Reviewed Files
product-reads/shopify-core.ts and registrations.ts; presentation.ts/presented-pairs.ts; product-context.ts; service.ts; recommendation-presentation.ts; model-context/stock/Redis tests; package/lock and reader-first README/.env gate docs.

### Validation Reviewed
Independent bounded run npx vitest run tests/arch067-stock.test.ts tests/arch067-model-context.test.ts PASS2files20tests. Actual assertions cover count edge cases/unknowns, defaultoff/literaltrue persistence, full/first/minimal wrapper pair lists, local and mocked private MCP two-turn fresh stock, public output schema equality, real runner/OpenRouter request serialization. Inspected owner evidence129tests, production typecheck/scoped lint/diff PASS. No unnecessary healthy checks rerun.

### Architecture Conformance
Accepted. Prepared packet physical isolation, start synchronization, exact recursive database039778a4 and durable claim42e22d9d inspected; correct dedicated parent/implementation worktrees clean, exact remote heads verified after fetch. Exact Shared5.11.0/integrity matches accepted release handoff. No gate enable/deployment/provider mutation/standalone production record/main or gitlink integration; reader-first/manual rollout gate remains required. No blocking issue found in owned scope.

### Follow-up
Conditional developer completion authority exercised below; integrated terminal system tests and reader deployments remain separate manual gates.


## Architect exact publication handoff — 2026-11-09
SHARED002explicitlyCompleteAcceptedAttempt1; import ONLY exact @modainteract/moda-interact-shared5.11.0, integrity sha512-VwVUszfUz0Bgs0alcnjJYK0m5bY7Jt9Nb/LuPRPgrWqk/JCFYqrWbzf7rnsXP2Z8EWlf4yfojbibnOQ4/9YyOg==; archiveSHA25628db9055f58355fb9779b190beb0eccda356e20fd9a52cf0b753cd1564789309, release-source1ad0d7c47c0a9e1d3d12072b62e238aec1cc92fe/acceptedimplementation467cc1abf5afc467f73861f9830430524022bacd. No range/latestguess or sibling/internaldist import. Publicstock/reference/helper/types/canonicalpurposeoneOf+constcompiler verified.
No deployment occursbytaskclaim/Complete. Newreadersacceptlegacystock, oldstrictreadersrejectnewfield; upgradeBackground/Studio Sharedreaders beforedeployingMCPstockwriter, localStudio reader/writer upgrade together. Keep COMMERCE_PRODUCT_REFERENCE_V2_WRITE_ENABLED absent/falseuntilbothreadersdeployed, literaltrueonlyaftermanualoperationalgate interminalsystemreceipt. MCPsourcecanbeimplemented/acceptedbeforeBackgrounddependentcode; deploymentsequence remainsreader-first, no taskdependencycycle. No inventory/providerwrite, main/live/rollout/gateenablement authorized here.

Ready unchangedAttempt0/unclaimed; soleprerequisiteComplete. Canonicalprepareownsfutureclaim, no executionhere.

## Developer Completion Decision — 2026-11-09
Developer explicitly requested moda_architect review and, if passing, mark ARCH-067-COMMERCE-001 Complete and push review/completion decision. Independent review passed above. Implementationcb7d002/report71d4be67 verified clean and durably published at matching remote task refs; all owned mandatory criteria satisfied. Complete at unchanged Attempt1, executor/claimed_at null; execution_mode agent and completion_mode developer preserved. No source/gate/deployment/main/gitlink change made by this decision.

Dependency reconciliation: MCP001 currently Review (not Complete); BACKGROUND001 remains Pending on MCP001, SYSTEM-TEST001 remains Pending on BACKGROUND001/MCP001 despite COMMERCE001 now Complete. Manual system-test and reference-write rollout gates unchanged. No downstream task claimed or automatically executed.
