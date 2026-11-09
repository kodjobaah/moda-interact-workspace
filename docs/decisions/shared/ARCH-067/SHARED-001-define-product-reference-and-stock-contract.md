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
status: in_progress
priority: 20
executor: codex
claimed_at: 2026-11-09T05:02:52Z
attempt: 1
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


## Canonical stock output subset compatibility amendment — 2026-11-09
Actual accepted5.10baseline generatedget_product/searchproducts descriptors compile with depth7/8; currentdescriptors differ ONLY by optionalstock and fail because exact normative Zoddiscriminatedunion emits oneOf/stringconst. This is task-introduced usability gap, not excusedbaseline. Bounded same-owner touchpoints additionally include src/commerce/purpose-output.ts, purpose-output.test.ts and an exactgeneratedacceptedbaseline testfixture ifneeded. Preserve canonical generatedrepresentation; do not lossyconvertoneOf toanyOf or change exactStockSchema.
Support scalarconst (string,boolean,null,finite typednumber/safeinteger only; no object/arrayconst) and oneOf exactly-one-matchingbranch semantics. Preserve existinganyOf and reject mixedunionkeywords/unsupportedfields; preventconst/enum combinations bypassingconstraints. Keep ALL resource/securitylimits unchanged: depth8,256nodes,128properties,32KiBschema/result,4096implicitstring,128array,2..4unionbranches, code-ownedfixedpatterns/no callerregex/code. This is keywordcompatibility, not budgetincrease.
Requiredproof: realgeneratedget/search descriptorscompile and validatefullproducts withKNOWNzero/positive/safe-max PRODUCT/VARIANT, NOT_TRACKED/UNAVAILABLE and legacyomittedstock; malformedstock/extra fields reject. OverlappingoneOf matchesreject; malformed/mixedconst/unions and hostiledepth/node/property/byte/patternlimitsreject. Comparecurrentdescriptor to actualaccepted5.10generatedbaseline plus EXACToptionalstockdelta; retain historicalauditedfixture unchanged aslegacyvalidatorvectors, do not erase unrelateddelta or fabricatebaseline. Record exact baselineproofreceipt /private/tmp/arch067-shared001-purpose-baseline.log. Rerun affectedpurpose/stock/context/runner/model tests, typecheck/finalbuild/publicJS+declarations, and retain acceptedfinalartifact provenance; no release/consumer/source-main changes.
