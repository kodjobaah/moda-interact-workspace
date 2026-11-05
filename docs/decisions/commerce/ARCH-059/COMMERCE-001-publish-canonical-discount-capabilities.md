---
id: ARCH-059-COMMERCE-001
architecture_id: ARCH-059
title: Publish canonical discount capabilities
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: ready
priority: 50
executor: null
claimed_at: null
attempt: 0
depends_on: ["ARCH-059-SHARED-002", "ARCH-058-COMMERCE-001"]
enables: ["ARCH-059-MCP-001", "ARCH-059-BACKGROUND-001", "ARCH-059-SYSTEM-TEST-001"]
created: 2026-11-05
updated: 2026-11-05
---
# Publish canonical discount capabilities

## Architecture
ARCH-059; docs/architecture/ARCH-059-unified-discount-capability-registration.md. Coordinator: moda_architect.

## Objective
Publish canonical discount capabilities through canonical setup, immutable release and MCP authorization.

## Context
MCP currently appends global discount tools outside published membership. Follow parent architecture identity, parity and compatible migration decisions.

## Scope
Only moda-interact-commerce source/tests/documentation required by Work Items.

## Out of Scope
Other repositories, new Feature identities, provider evaluator redesign, schema changes, main merges and automatic execution.

## Requirements
Feature product_search (Product Search) owns both canonical discount tools exactly once. INITIAL_RECOVERY_OUTREACH remains purpose with checkout_recovery host admission. Preserve active-plan permission parity including Free through explicit provisioning verification; preserve merchant settings and provider evaluation. Fail closed on missing release or stale identity. No global fallback, duplicate descriptors, contract hashes or locally copied Shared contracts. Follow recorded rollout order.

## Work Items
- [ ] Extend existing setup plan/apply/verify with the two discount tools, canonical policy-operation revisions and FeatureCapabilities under product_search; display tools as Get Discount Options and Get Discount Details.
- [ ] Provision enabled product_search plan mappings for every previously discount-eligible active plan including Free; verify active ALWAYS_ENABLED/systemRequired identity without overriding conflicting operator policy. Preserve checkout_recovery mappings and all merchant discount settings.
- [ ] Use deterministic operation IDs and existing authoring/validation/audit/lifecycle services; publish complete immutable releases preserving unrelated members and stage without activation; activate only at the explicit strict-MCP cutover gate using optimistic concurrency.
- [ ] Dry-run reports mapping/revision/release changes without writes; rerun converges and interrupted execution resumes; conflicting drafts fail without overwrite.
- [ ] Verify each discount name appears once in published membership and preserve old-client compatibility during staged rollout; no provider reads during setup.

## Interfaces / Contracts
Published @modainteract/moda-interact-shared/commerce input/output, release/capability/revision/grant validators; versioned extensions owned by ARCH-059-SHARED-001, registry availability by ARCH-059-SHARED-002. Producers/consumers and storage trust boundary are normative in parent architecture.

## Dependencies
- ARCH-059-SHARED-002
- ARCH-058-COMMERCE-001

## Enables
- ARCH-059-MCP-001
- ARCH-059-BACKGROUND-001
- ARCH-059-SYSTEM-TEST-001

## Acceptance Criteria
- [ ] Extend existing setup plan/apply/verify with the two discount tools, canonical policy-operation revisions and FeatureCapabilities under product_search; display tools as Get Discount Options and Get Discount Details.
- [ ] Provision enabled product_search plan mappings for every previously discount-eligible active plan including Free; verify active ALWAYS_ENABLED/systemRequired identity without overriding conflicting operator policy. Preserve checkout_recovery mappings and all merchant discount settings.
- [ ] Use deterministic operation IDs and existing authoring/validation/audit/lifecycle services; publish complete immutable releases preserving unrelated members and stage without activation; activate only at the explicit strict-MCP cutover gate using optimistic concurrency.
- [ ] Dry-run reports mapping/revision/release changes without writes; rerun converges and interrupted execution resumes; conflicting drafts fail without overwrite.
- [ ] Verify each discount name appears once in published membership and preserve old-client compatibility during staged rollout; no provider reads during setup.
- [ ] Existing authorization/provider evaluation and unrelated published members remain intact.

## Validation
- [ ] Inspect package.json and run declared focused tests for every Work Item, plus declared typecheck/build when deployable TypeScript changes; record exact commands/results. Do not invent missing scripts.
- [ ] Reports contain no secrets and demonstrate task scope only.

## Stop Condition
After Work Items, Acceptance Criteria and Validation complete, submit Completion Report for review and STOP. Explicit developer completion via /moda_developer_update is required. Do not start enabled work. System Test is manually invoked after prerequisites complete.


### Canonical operation mapping
| Tool key / display name | Policy operation | Version | Input/output contract |
|---|---|---|---|
| commerce_get_discount_options / Get Discount Options | discounts.getOptions | 1.0.0 | CommerceToolInputs/Outputs.commerce_get_discount_options |
| commerce_get_discount_details / Get Discount Details | discounts.getDetails | 1.0.0 | CommerceToolInputs/Outputs.commerce_get_discount_details |

`discounts.getDetails` is a NEW operation ID required by this architecture. `discounts.evaluate` is an existing basket-evaluation operation with a different contract and MUST NOT substitute for details. Existing getOptions schema/operation is reused; the MCP published-capability adapter still requires implementation. Existing discount catalogue/provider evaluation is reused, not reimplemented. Both operations bind trusted shop/context from the host, never an input shopId. Add new details ID to Shared validation before Commerce/MCP consume it. Definition version is an immutable published tool revision version, separate from operationVersion; select the new revision identity through existing version rules, do not overwrite 2.0.0 built-in identity in place.

### Configuration versus new runtime capability
Once an operation/version is implemented, an authorized staff user may configure a draft via the existing Policy Operation editor, validate/test it, attach it to an existing Feature capability, publish a complete release and activate that release. Setup automates those same lifecycle APIs for these six canonical tools. UI draft save, Feature attachment or publication alone never grants an MCP call or modifies Background purpose admission. New operations/versions or new provider I/O require Shared contract, Commerce authoring registry and MCP runtime implementation/review before UI selection becomes executable; the UI cannot install arbitrary server code. Future capabilities reuse this lifecycle but are not implemented by ARCH-059. Initial outreach has a host-owned four-name allowlist: commerce_get_discount_options, commerce_get_discount_details, commerce_search_products, commerce_get_product. Adding a future published tool does NOT add it to outreach automatically.

### Verified implementation touchpoints
Paths below exist at definition time; changes are task requirements, not completed work.

| File | Existing symbol/surface | Required change |
|---|---|---|
| `moda-interact-commerce/src/commerce/execution/policy-operation-authoring.ts` | POLICY_OPERATION_CONTRACTS; getPolicyOperationAuthoringDescriptor | Register discounts.getDetails/1.0.0 with details validators; verify options registration unchanged. |
| `moda-interact-commerce/src/commerce/execution/renderer.ts` | operation-specific result bounds switch | Add bounded details result handling consistent with existing operation response validation; no provider evaluation change. |
| `moda-interact-commerce/src/studio/tools/policy-operation-editor.tsx` | existing Policy Operation editor | Expose only registered operation/version choices; verify details schemas and argument mapping controls. |
| `moda-interact-commerce/src/studio/tools/policy-operation-authoring-server-actions.ts` | getPolicyOperationAuthoringDescriptorAction | Authorize descriptor reads; reject unsupported operation/version; never grant runtime authority. |
| `moda-interact-commerce/src/studio/tools/authoring/persisted-policy-operation-tool-editor.tsx` | persisted policy operation editor | Verify save/reload/validate workflow for options/details through existing APIs. |
| `moda-interact-commerce/src/studio/features/add-capability/add-capability-screen.tsx` | existing add capability screen | Verify canonical tool selection under Product Search without duplicating a Feature or granting outreach access. |
| `moda-interact-commerce/src/commerce/bootstrap/system-product-tools.ts` | SYSTEM_COMMERCE_PRODUCT_TOOLS; SYSTEM_PRODUCT_TOOL_DRAFTS | Add two canonical definitions with input-only bindings: options limit/cursor optional; details offerId required. |
| `moda-interact-commerce/src/commerce/bootstrap/system-commerce-tool-sync.ts` | loadSystemProductIdentity; planSystemCommerceToolSync; applySystemCommerceToolSync | Generalize sync to six canonical members; preserve unrelated members; map all previously eligible plans; stage without premature activation. |
| `moda-interact-commerce/src/commerce/bootstrap/product-discovery-setup.ts` | parseSetupArguments; SetupReceipt | Represent explicit stage-only and operator-confirmed cutover modes and bounded receipt gate evidence. |
| `moda-interact-commerce/src/commerce/publication/lifecycle.ts` | CommerceLifecycle | Use existing publish/activate lifecycle validation and optimistic concurrency; do not bypass immutability. |
| `moda-interact-commerce/tests/system-commerce-tool-sync.test.ts` | sync test suite | Add exact six-member, idempotence, conflict and staging assertions. |
| `moda-interact-commerce/tests/persisted-policy-operation-tool-editor.test.tsx` | editor tests | Verify registered details operation authoring and unsupported operation refusal. |

### Deterministic acceptance matrix
| Fixture/trigger | Required result |
|---|---|
| Clean active-plan canonical setup | Exactly six product_search capabilities: four existing product/shipping plus two discounts; each tool key once |
| Existing unrelated capability/release member | Preserved; total may exceed six, canonical subset remains exactly six |
| Repeat apply / dry-run / interrupted retry | No duplicate tool/revision/member; dry-run zero writes; retry converges |
| Free and paid ACTIVE/TRIALING on active plans | Same prior discount eligibility after explicit product_search mapping provisioning |
| Inactive plan/shop/Feature, revoked mapping or permission | No unauthorized call; preserve existing policy denial semantics |
| NONE / FIXED / AI_BEST_APPLICABLE; expired override | Same evaluator facts/results as baseline for same tenant/time/provider |
| Missing member, wrong revision, duplicate name or forged tenant | Fail closed before provider I/O; bounded diagnostic, no global fallback |
| Extra future published capability | Available only via normal entitlement; excluded from initial-outreach four-name allowlist |
| UI save without published active membership | No MCP tool/grant created by save alone |
| Old MCP + staged canonical release | Old pointer remains active; new release not activated until strict MCP cutover |

### Deployment gate: prevent duplicate old/new registration
Commerce task completion means code and a tested STAGED immutable release are ready; it MUST NOT activate the new discount-member release against an old MCP binary. Old MCP appends global discount names, so activation there would duplicate registration. This is a hard staging gate, not a dependency cycle: Commerce implementation can be accepted while activation is deferred to coordinated rollout after MCP implementation acceptance.

1. Publish Shared package and deploy Commerce support. Plan/provision mappings, create and validate the complete staged release while the OLD active pointer remains unchanged. Record staged release ID, previous pointer/version and ready-to-activate member list. Do not activate from ordinary setup apply until the operator supplies explicit cutover confirmation; add a stage-only/default-safe activation gate to the setup workflow and test its argument handling. No new Render environment variable is required.
2. Build and validate strict MCP and Background consumer artifacts before cutover. Pause affected initial-outreach/conversation discount attempts through the existing operational pause/drain procedure; wait for old sessions/grants to finish and record zero active affected sessions. Do not delete queued work or change credit/delivery state.
3. Deploy strict MCP first, keeping the old release active temporarily. Missing canonical members produce explicit UNAVAILABLE, never legacy fallback. This bounded discount unavailability is intentional within the controlled maintenance window. Other services must not treat it as an absence of discounts.
4. Operator confirms strict MCP version and staged release ID, then explicitly activates that complete release through Commerce lifecycle concurrency checks. Verify each discount name appears exactly once, mapping parity and read-only authorized calls before deploying/resuming the new Background consumer.
5. Resume paused consumers only after list/call/host checks pass. If verification fails, remain paused and restore OLD MCP/Background artifacts together with the previous compatible release pointer; do not run old MCP against the new discount-member release. Record version/pointer pairing and rollback evidence. No task executes this deployment simply because definitions exist.

MCP must reject duplicate persisted names before server registration. No name-based deduplication is permission evidence. Missing membership cannot fall back to projectShopDiscountTools in strict runtime. Historical built-in grants remain historical and are rejected by the new path; do not rewrite them into capabilities.

## Implementation Notes
Use launcher-resolved isolated matching task worktrees/branches and record synchronization evidence. No execution started by this definition. Reuse existing policy/lifecycle services. Return missing schema/contract capability or permission-parity conflicts to architect.

## Completion Report
### Status
Not Started
### Files Changed
None
### Work Completed
None
### Validation Results
Not run; definition only.
### Deviations
None
### Assumptions
Existing lifecycle persistence supports canonical capabilities.
### Unresolved Issues
None identified during definition.
### Architectural Concerns
Return newly discovered cross-service or policy gaps before proceeding.

## Architect Review
### Review Status
Pending
### Review Notes
Definition only.
### Reviewed Files
None
### Validation Reviewed
None
### Architecture Conformance
Pending implementation.
### Follow-up
None

## Architect Dependency Reconciliation — 5 November 2026

SHARED-002 Attempt 1 passed review and is explicitly developer-completed. Exact published Shared version is 5.1.0, release metadata `3096ca2`, accepted source `50891ef`. All explicit prerequisites are Complete (including ARCH-058-COMMERCE-001); promoted to Ready, unclaimed, Attempt 0 preserved. Readiness does not authorize automatic execution, consumer deployment or cutover; the staged-release rollout gate remains binding.
