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
status: review
priority: 50
executor: null
claimed_at: null
attempt: 1
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
- [x] Extend existing setup plan/apply/verify with the two discount tools, canonical policy-operation revisions and FeatureCapabilities under product_search; display tools as Get Discount Options and Get Discount Details.
- [x] Provision enabled product_search plan mappings for every previously discount-eligible active plan including Free; verify active ALWAYS_ENABLED/systemRequired identity without overriding conflicting operator policy. Preserve checkout_recovery mappings and all merchant discount settings.
- [x] Use deterministic operation IDs and existing authoring/validation/audit/lifecycle services; publish complete immutable releases preserving unrelated members and stage without activation; activate only at the explicit strict-MCP cutover gate using optimistic concurrency.
- [x] Dry-run reports mapping/revision/release changes without writes; rerun converges and interrupted execution resumes; conflicting drafts fail without overwrite.
- [x] Verify each discount name appears once in published membership and preserve old-client compatibility during staged rollout; no provider reads during setup.

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
- [x] Extend existing setup plan/apply/verify with the two discount tools, canonical policy-operation revisions and FeatureCapabilities under product_search; display tools as Get Discount Options and Get Discount Details.
- [x] Provision enabled product_search plan mappings for every previously discount-eligible active plan including Free; verify active ALWAYS_ENABLED/systemRequired identity without overriding conflicting operator policy. Preserve checkout_recovery mappings and all merchant discount settings.
- [x] Use deterministic operation IDs and existing authoring/validation/audit/lifecycle services; publish complete immutable releases preserving unrelated members and stage without activation; activate only at the explicit strict-MCP cutover gate using optimistic concurrency.
- [x] Dry-run reports mapping/revision/release changes without writes; rerun converges and interrupted execution resumes; conflicting drafts fail without overwrite.
- [x] Verify each discount name appears once in published membership and preserve old-client compatibility during staged rollout; no provider reads during setup.
- [x] Existing authorization/provider evaluation and unrelated published members remain intact.

## Validation
- [x] Inspect package.json and run declared focused tests for every Work Item, plus declared typecheck/build when deployable TypeScript changes; record exact commands/results. Do not invent missing scripts.
- [x] Reports contain no secrets and demonstrate task scope only.

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

Ready for Developer Completion — Attempt 1. Passing developer self-review is recorded below; explicit developer completion remains pending.
### Files Changed
`package.json`, `package-lock.json`, `src/commerce/bootstrap/product-discovery-setup.cli.ts`, `src/commerce/bootstrap/product-discovery-setup.ts`, `src/commerce/bootstrap/system-commerce-tool-sync.cli.ts`, `src/commerce/bootstrap/system-commerce-tool-sync.ts`, `src/commerce/bootstrap/system-product-tools.ts`, `src/commerce/execution/policy-operation-authoring.ts`, `src/commerce/execution/renderer.ts`, `src/commerce/tool-definition/contracts.ts`, `tests/commerce-product-discovery-setup.test.ts`, `tests/persisted-policy-operation-tool-editor.test.tsx`, `tests/policy-operation-authoring-server-actions.test.ts`, `tests/policy-operation-registry.test.ts`, `tests/system-commerce-tool-sync.test.ts`.
### Work Completed
- Pinned the Commerce consumer to accepted `@modainteract/moda-interact-shared@5.1.0`. Registered `discounts.getDetails@1.0.0` using Shared validators and bounded rendering. Added Get Discount Options and Get Discount Details as canonical Product Search capabilities with input-only trusted-context bindings and immutable revision identities.
- Generalized setup planning/application to all six canonical Product Search tools. Setup reports and provisions enabled `product_search` mappings for every active plan, including Free, verifies the complete active-plan set, and preserves existing mappings such as `checkout_recovery`. Existing merchant discount settings and provider evaluation are not modified or invoked by setup.
- Reused deterministic operation IDs, authoring and lifecycle services. Default apply creates/verifies the complete immutable release as staged and leaves the active pointer unchanged. Explicit strict-MCP version, staged release ID, expected base release ID and expected pointer edit version are required for activation; lifecycle CAS and post-activation snapshot checks remain in force.
- Added read-only dry-run, plan mapping conflict, canonical identity/content conflict, idempotent rerun, interrupted draft/release retry, exact six-member and same-Feature unrelated-member preservation coverage. The P2 correction removes rejection of unrelated Product Search capabilities while retaining duplicate capability key and canonical identity checks.
- No provider reads, production activation, consumer deployment, database schema change, main merge or submodule gitlink update was performed.
### Validation Results
- `npm test -- tests/system-commerce-tool-sync.test.ts tests/commerce-product-discovery-setup.test.ts tests/persisted-policy-operation-tool-editor.test.tsx tests/policy-operation-registry.test.ts tests/policy-operation-authoring-server-actions.test.ts` — 5 files and 32 tests passed.
- `npm run typecheck` — passed.
- `npm run build` — passed; Next.js emitted the existing Nunjucks dynamic-dependency warning.
- `git diff --check` — passed.
- Commands ran against an isolated validation copy of the final task source under `/private/tmp/moda-commerce-arch059-001-validation`; the implementation worktree lacked the pretest `@shopify/dev-mcp` package required by `schema:sync`. The validation copy used the locked task dependency set and no production services.
### Git / VCS

Task branch: `task/ARCH-059-COMMERCE-001`.

Physical worktree isolation:
- Canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-059-COMMERCE-001`; branch `task/ARCH-059-COMMERCE-001`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-059-COMMERCE-001`; branch `task/ARCH-059-COMMERCE-001`.
- Shared workspace checkout switched/mutated for task work: no. Shared implementation checkout switched/mutated for task work: no. Another task worktree reused: no.

Synchronization and publication:
- Parent `origin/main` is incorporated by merge commit `687d1f097`; implementation baseline `7f50848` matched `origin/main` before the implementation commit.
- Implementation repository: `moda-interact-commerce`; commit `770d6ab` (`task(ARCH-059-COMMERCE-001): preserve unrelated Product Search capabilities`); pushed to `origin/task/ARCH-059-COMMERCE-001`.
- Parent task record: review submission commit `1ea7c8e99` pushed to `origin/task/ARCH-059-COMMERCE-001`; this VCS evidence update is also on that task branch. Submodule gitlink staged: no.
- Merged to implementation main: no. Merged to workspace main: no.
### Deviations
The implementation worktree's dependencies did not include `@shopify/dev-mcp`, so declared checks ran in an isolated validation copy rather than directly in the task worktree. The exact focused test/typecheck/build commands and results are recorded above.
### Assumptions
Shared 5.1.0 is the accepted ARCH-059-SHARED-002 publication; existing Commerce lifecycle persistence supports canonical capabilities.
### Unresolved Issues
Strict-MCP release activation and consumer rollout remain intentionally deferred until the strict MCP and Background consumer artifacts are accepted and the operational pause/drain and verification gates are completed. This is the task's required deployment gate, not an implementation blocker.
### Architectural Concerns
None identified. No activation or deployment was attempted.

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

## Developer Self-Review — Changes Requested, 5 November 2026

Reviewed the current uncommitted developer draft in the canonical implementation worktree, baseline HEAD `7f50848`. Returned to Ready, executor/claim null, Attempt 1 preserved; execution/completion ownership remains developer. No acceptance or downstream promotion. No implementation source is committed, reverted or otherwise changed by this review. Use the normal developer claim workflow for the next attempt; preserve the existing dirty task-owned implementation.

### Required Correction

**[P2] Setup rejects legitimate unrelated capabilities on Product Search.** `src/commerce/bootstrap/system-commerce-tool-sync.ts:149` fails IDENTITY_CONFLICT whenever any capability selected under product_search has a key outside the six canonical tool keys. The query deliberately loads all capabilities for that Feature, so an existing unrelated or future published capability causes plan/apply to abort. The task explicitly requires preservation of unrelated members and permits a total greater than six, with the canonical subset appearing exactly once. Preserve and validate unrelated same-Feature members instead of treating every noncanonical key as an identity conflict. Retain rejection of actual canonical-name/ID collisions and immutable revision drift.

The existing preservation case in `tests/system-commerce-tool-sync.test.ts` creates its unrelated capability under `feature-unrelated`; it does not exercise this failing same-product_search branch. Add a same-Feature unrelated capability/release fixture. Prove read-only plan, staged apply, repeat apply and interrupted retry retain that exact member/revision/feature snapshot and the old active pointer, while all six canonical members occur once and conflicting canonical names still fail closed. This finding is source-inspection evidence; no runtime reproduction is claimed.

### Validation and Submission Gaps

The developer draft contains 15 changed files, including Shared 5.1.0 adoption, details authoring/rendering and setup/staged cutover changes. Reviewed the current diff, task requirements and tests. The task Completion Report remains Not Started; required validation and final implementation publication are not yet recorded.

Attempted the declared focused test command via npm test with system-commerce-tool-sync, commerce-product-discovery-setup, persisted-policy-operation-tool-editor, policy-operation-authoring-server-actions and policy-operation-registry files. It failed before test execution because the pretest schema-sync prerequisite could not find `node_modules/@shopify/dev-mcp/package.json`. This is a missing worktree dependency, not a reproduced application/test assertion failure. Local log `/tmp/arch059-commerce001-review.log`. No tests/typecheck/build passes are claimed by this review. Working-tree whitespace check passed.

After correction, install the locked worktree prerequisites through the established workflow and run focused checks for every Work Item plus required typecheck/build. Complete the report with exact changes, stage-only/default-safe activation and optimistic-concurrency evidence, active-plan/Free provisioning without operator-policy overwrite, idempotence/interruption/conflict behavior, developer/agent assistance, physical worktree/synchronization and final task-branch commit/push evidence. Do not activate a real staged release, deploy or operate provider accounts merely to complete this source task. Consumer cutover remains gated on strict MCP acceptance.

### Ownership and Downstream

Parent `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-059-COMMERCE-001`; implementation `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-059-COMMERCE-001`, matching task branches. This review changes only parent task documentation. Developer source edits remain untouched. MCP, Background and terminal system validation stay Pending on this unaccepted prerequisite. No main merge, implementation gitlink update, deployment or new attempt occurs.

## Developer Self-Review — Passed, 5 November 2026

The required P2 correction is implemented and validated. The system sync now retains unrelated capabilities selected under the existing Product Search Feature while continuing to reject duplicate capability keys, canonical identity collisions and immutable revision drift. The same-Feature regression test verifies read-only planning, staged apply, repeat apply and interrupted retry preserve the unrelated member's exact revision and Feature snapshot, keep the previous active pointer, and include each of the six canonical Product Search tools exactly once. Existing conflicting canonical-name coverage still fails closed.

All Work Items and Acceptance Criteria are met by the scoped Commerce source changes. Focused tests, typecheck, build and whitespace validation passed as recorded in the Completion Report. Material assigned-agent assistance: `moda_commerce` implemented the canonical discount publication changes and the same-Feature preservation correction at the developer's explicit request. No real release was activated, no provider account was accessed, and no consumer was deployed.

Attempt 1 is preserved. This self-review passes the implementation to `review`; because `completion_mode: developer`, the developer's explicit completion decision remains pending. No downstream task is started or promoted here.
