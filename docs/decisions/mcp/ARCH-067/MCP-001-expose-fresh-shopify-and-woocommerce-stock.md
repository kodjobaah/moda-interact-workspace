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
status: review
priority: 20
executor: codex
claimed_at: 2026-11-09T07:05:23Z
attempt: 1
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

### Status

Ready for Review — Attempt 1. Implementation and validation evidence are published on mirrored task/ARCH-067-MCP-001 branches. Execution remains agent/codex; completion_mode developer retained. Architect acceptance and explicit completion have not occurred.

### Implementation / source

Implementation `9b5fa5680905930e65c89a0a6bf3e7b3546ef633` is committed/pushed and equals local HEAD/origin task ref; implementation worktree is clean. Exact Shared5.11.0 is imported through published public exports and locked to `sha512-VwVUszfUz0Bgs0alcnjJYK0m5bY7Jt9Nb/LuPRPgrWqk/JCFYqrWbzf7rnsXP2Z8EWlf4yfojbibnOQ4/9YyOg==`, matching the architect's accepted release handoff. No sibling source/internal-dist import or duplicated generic stock-quantity validator was added.

Actual changed paths (seven):

- `package.json`: exact Shared5.6.0 ->5.11.0 dependency; private MCP package/version unchanged.
- `package-lock.json`: exact5.11.0 archive/integrity plus its required parse5/entities transitive dependencies; no unrelated dependency refresh.
- `src/execution/policy/shopify-core.ts`: inventory selections/parsers/normalizers for SEARCH_DOCUMENT, CATEGORY_SEARCH_DOCUMENT, GET_PRODUCT_DOCUMENT and GET_VARIANT_DOCUMENT; Woo tracking/scope mapping; bounded stock observations.
- `src/execution/policy/shopify-core-executor.ts`: stock status/quantity/scope in existing search/get template-output projections and typed info logger propagation. Canonical wire output still validates against the public Shared schema and retains original discriminated stock objects.
- `src/connections/woocommerce/direct-product-reader.ts`: manage_stock alongside stock_quantity in product/list/get and variation/list/get read allowlists, leaving SHIPPING projections untouched.
- `tests/unit/execution/policy/product-stock.test.ts`: deterministic provider matrix, all four Shopify query paths, both Woo search/get identity scopes, ambiguity/parent/tenant failures, exact built public stock-schema equality, serialized published get/search envelopes and bounded diagnostic assertions.
- `tests/unit/connections/woocommerce/direct-product-reader.test.ts`: intentional allowlist goldens updated; four read-operation fixtures assert tracking/count requests without weakening credential/grant/redirect checks.

### Requirement disposition

- **Implemented:** every Shopify variant path requests inventoryQuantity/inventoryItem.tracked. Explicit false maps NOT_TRACKED; explicit true and Shared-normalized safe integer maps KNOWN/VARIANT. Missing/malformed tracking/count maps UNAVAILABLE, decimal/unsafe quantities are not rounded and negative integers normalize to zero through the imported Shared helper. Existing availability stays independent.
- **Implemented:** product-only Shopify requests first:1 plus pageInfo.hasNextPage, preserving the original request/item budgets. A sole returned variant with hasNextPage false can supply exact VARIANT stock; multiple, missing or unproven variant membership yields UNAVAILABLE/VARIANT_REQUIRED. No first variant is presented as a product total. Exact get variant-parent checks remain unchanged and regression-tested.
- **Implemented:** Woo boolean true + valid count maps KNOWN/PRODUCT for simple products and KNOWN/VARIANT for variations; false maps NOT_TRACKED. Variable parents and parent-managed variations emit UNAVAILABLE without sums/borrowed totals. Non-simple unknown product types cannot fabricate product-wide known counts. Product/variation allowlists retain the raw provider tracking value, including 'parent', for this mapping. A variable-parent exact read returns its native parent product with unavailable stock rather than silently inventing a variant quantity.
- **Implemented:** new product adapters always emit stock; legacy omitted stock remains accepted by the public Shared schema. Both canonical get/search schemas are checked against built public CommerceProductStockSchema. Published executor results survive JSON wire serialization and canonical result/output parsing for KNOWN zero, NOT_TRACKED and UNAVAILABLE without stripping stock or adding quantity/scope to non-KNOWN variants. This proves the MCP response consumed by an upgraded Background reader retains stock; it does not claim that old strict Background readers accept it.
- **Implemented:** existing Shared logger is reused under mcp.product.lookup event family. Authorized normalized observations include shop/request/recovery correlation where present, native product/variant IDs, stock status/scope and closed reason enum. No raw provider text, tokens, customer text or quantity is logged. Persisted context reference/presentation counts are unavailable at the MCP provider boundary and are represented truthfully as null, not guessed zero; actual host final-verification counts remain Background/Commerce responsibilities under the architecture ownership clarification. Tests assert reasons, absence of raw quantity/canary text and no observations for rejected parent/tenant reads.
- **Preserved:** existing API2026-07 resolver, offline credentials, provider authorization/scope enforcement, parent/tenant fences, checkout ownership, read-only operation guard, revocation, retry behavior, cancellation, provider budgets and output bounds. No permission, schema-compiler resource cap, model budget, scope configuration, storefront API, inventory write or live provider request was added.

### Agent-executed validation

Canonical workspace Node24.19.0/npm11.17.0 bootstrap used. Exact Shared5.11.0 lock integrity verified after installation.

- `npm run schema:install:shopify -- /Users/kwadwoadomafriyie/project/moda-interact-workspace/moda-interact-commerce/lib/discovery/artifacts/admin-2026-07.json`: passed the existing installer hash check `2b507dc1f74c6157e0eb98500db0f3c3e238d69eaf0d98fd7657ac7ed3f6900b`. Installs the ignored local validation artifact only; no generated schema/version rewrite or source fixture fabrication. This resolved the new task worktree's initially missing artifact in the fixed-document schema test.
- Focused provider/core/options/composition/connection tests passed102/102 before the final diagnostic-canary test; final full suite includes that case and all owned fixtures.
- `npm run test:unit`: **474 passed, 0 failed, 0 skipped**, about40s. Includes tenant/revocation/provider failure, checkout ownership, protocol/execution, readiness/shutdown, product composition and prior regression tests. No Docker/database/live suite or infrastructure orchestration was launched.
- `npm run typecheck`: passed, including Prisma6.19.3 generation from the pinned database submodule.
- `npm run lint`: passed with max-warnings0.
- `npm run build`: Prisma generation and production TypeScript build passed.
- `git diff --check` and staged diff check: passed.
- All four current fixed Shopify documents validate against the installed pinned introspection and unchanged read-only/depth/field guard in unit fixtures. Shopify toolkit Admin validator also independently accepted all four for2026-07. Its warnings identify the existing deprecated Product.featuredImage selection and required read_products/read_inventory scopes; these were not changed or bypassed. Initial toolkit invocation used an unsupported topic flag; corrected invocation passed all four. No live merchant execution was used.
- Documentation checked: [ProductVariant2026-07](https://shopify.dev/docs/api/admin-graphql/2026-07/objects/ProductVariant) and pinned toolkit documentation for inventoryItem/tracked. Shopify skill instrumentation disabled for these local checks.

### Physical worktrees / synchronization / publication

Canonical workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; reused parent `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-067-MCP-001`; created implementation `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-067-MCP-001`. Both use task/ARCH-067-MCP-001. No shared checkout switched/mutated for implementation and no other task worktree reused. Launcher verified sole dependency ARCH-067-SHARED-002 Complete, synchronized both task branches (remote fast-forwards not needed, origin/main incorporated in parent and already current in implementation), initialized recursive submodules, and durably claimed Attempt1 as codex at2026-11-09T07:05:23Z in parent `00aff857f4069c57bf0ab027af4d911a7dda4e00`. Preclaim parent462a92ad103fb50345d30ec36c1ee5dc6b2744bd, implementation baseline4d44a85c2aecd733c3fea1dc6ec8660d6e7ffb5b. Database submodule initialized at379d563f6b9ee070305e284615dddbc0b97afeb0; no gitlink/schema change.

The complete Architect Review was read before source inspection: outcome Not reviewed, with the exact5.11.0 publication/reader-first handoff below. No Changes Requested correction list existed; no review requirement was waived. No subagent assistance. Implementation push succeeded; this corresponding parent report is pushed for architect review. Private MCP runtime has no npm release in this task; it consumes the already published Shared artifact. No main merge/push, package republication, database migration/reset/seed, deployment, real customer message or operational gate enablement.

### Deployment / compatibility handoff

Reader-first sequencing remains mandatory: deploy Background and Studio readers supporting Shared5.11.0 stock before deploying the MCP stock writer; local Studio reader/writer upgrade together. Keep COMMERCE_PRODUCT_REFERENCE_V2_WRITE_ENABLED absent/false until both reference readers are deployed, then enable only literaltrue under the manual terminal system receipt. This MCP source task does not introduce a stock flag or enable either host gate. Old strict readers reject additive stock, so source review/publication is not rollout approval. Background-dependent implementation and terminal/manual system evidence remain separately owned follow-ons; no deployment or end-to-end live parity is claimed here.

## Architect Review
Status: Not reviewed.


## Architect exact publication handoff — 2026-11-09
SHARED002explicitlyCompleteAcceptedAttempt1; import ONLY exact @modainteract/moda-interact-shared5.11.0, integrity sha512-VwVUszfUz0Bgs0alcnjJYK0m5bY7Jt9Nb/LuPRPgrWqk/JCFYqrWbzf7rnsXP2Z8EWlf4yfojbibnOQ4/9YyOg==; archiveSHA25628db9055f58355fb9779b190beb0eccda356e20fd9a52cf0b753cd1564789309, release-source1ad0d7c47c0a9e1d3d12072b62e238aec1cc92fe/acceptedimplementation467cc1abf5afc467f73861f9830430524022bacd. No range/latestguess or sibling/internaldist import. Publicstock/reference/helper/types/canonicalpurposeoneOf+constcompiler verified.
No deployment occursbytaskclaim/Complete. Newreadersacceptlegacystock, oldstrictreadersrejectnewfield; upgradeBackground/Studio Sharedreaders beforedeployingMCPstockwriter, localStudio reader/writer upgrade together. Keep COMMERCE_PRODUCT_REFERENCE_V2_WRITE_ENABLED absent/falseuntilbothreadersdeployed, literaltrueonlyaftermanualoperationalgate interminalsystemreceipt. MCPsourcecanbeimplemented/acceptedbeforeBackgrounddependentcode; deploymentsequence remainsreader-first, no taskdependencycycle. No inventory/providerwrite, main/live/rollout/gateenablement authorized here.

Ready unchangedAttempt0/unclaimed; soleprerequisiteComplete. Canonicalprepareownsfutureclaim, no executionhere.
