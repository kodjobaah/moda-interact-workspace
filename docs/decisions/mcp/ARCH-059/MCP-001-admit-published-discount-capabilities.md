---
id: ARCH-059-MCP-001
architecture_id: ARCH-059
title: Admit published discount capabilities
task_kind: implementation
domain: mcp
repository: moda-interact-mcp
assigned_agent: moda_mcp
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: complete
priority: 50
executor: null
claimed_at: null
attempt: 1
depends_on: ["ARCH-059-SHARED-002", "ARCH-059-COMMERCE-001", "ARCH-058-MCP-003"]
enables: ["ARCH-059-BACKGROUND-001", "ARCH-059-SYSTEM-TEST-001"]
created: 2026-11-05
updated: 2026-11-05
---
# Admit published discount capabilities

## Architecture
ARCH-059; docs/architecture/ARCH-059-unified-discount-capability-registration.md. Coordinator: moda_architect.

## Objective
Admit published discount capabilities through canonical setup, immutable release and MCP authorization.

## Context
MCP currently appends global discount tools outside published membership. Follow parent architecture identity, parity and compatible migration decisions.

## Scope
Only moda-interact-mcp source/tests/documentation required by Work Items.

## Out of Scope
Other repositories, new Feature identities, provider evaluator redesign, schema changes, main merges and automatic execution.

## Requirements
Feature product_search (Product Search) owns both canonical discount tools exactly once. INITIAL_RECOVERY_OUTREACH remains purpose with checkout_recovery host admission. Preserve active-plan permission parity including Free through explicit provisioning verification; preserve merchant settings and provider evaluation. Fail closed on missing release or stale identity. No global fallback, duplicate descriptors, contract hashes or locally copied Shared contracts. Follow recorded rollout order.

## Work Items
- [x] Resolve discount list/call exclusively from active published capability/revision membership; remove unconditional projectShopDiscountTools append in migrated runtime.
- [x] Dispatch canonical policy operations through existing discount authorization/catalogue/details evaluator; retain NONE/FIXED/AI_BEST_APPLICABLE, override expiry, current permission, tenant, provider and platform checks.
- [x] Reject missing/inactive/mismatched releases, duplicates, stale capability revisions and legacy built-in-only grants before provider I/O, without synthesized fallback.
- [x] Prove pre/post eligibility and result parity for Shopify/WooCommerce, active Free/paid plans, revoked permission and cross-tenant IDs.

## Interfaces / Contracts
Published @modainteract/moda-interact-shared/commerce input/output, release/capability/revision/grant validators; versioned extensions owned by ARCH-059-SHARED-001, registry availability by ARCH-059-SHARED-002. Producers/consumers and storage trust boundary are normative in parent architecture.

## Dependencies
- ARCH-059-SHARED-002
- ARCH-059-COMMERCE-001
- ARCH-058-MCP-003

## Enables
- ARCH-059-BACKGROUND-001
- ARCH-059-SYSTEM-TEST-001

## Acceptance Criteria
- [x] Resolve discount list/call exclusively from active published capability/revision membership; remove unconditional projectShopDiscountTools append in migrated runtime.
- [x] Dispatch canonical policy operations through existing discount authorization/catalogue/details evaluator; retain NONE/FIXED/AI_BEST_APPLICABLE, override expiry, current permission, tenant, provider and platform checks.
- [x] Reject missing/inactive/mismatched releases, duplicates, stale capability revisions and legacy built-in-only grants before provider I/O, without synthesized fallback.
- [x] Prove pre/post eligibility and result parity for Shopify/WooCommerce, active Free/paid plans, revoked permission and cross-tenant IDs.
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
| `moda-interact-mcp/src/capabilities/resolve.ts` | resolveShopCapabilities; publishedDescriptor | Resolve published members, reject duplicates and stop global discount append. |
| `moda-interact-mcp/src/execution/discount-tools.ts` | projectShopDiscountTools; resolveDiscountAuthorizationPolicy | Remove use of global projection from new runtime; preserve permission resolver logic. |
| `moda-interact-mcp/src/execution/discount-catalogue.ts` | createPrismaDiscountCatalogueReader; DiscountSystemToolCall | Adapt canonical published calls to existing read evaluator with trusted context/deadline/signal; retain provider and merchant checks. |
| `moda-interact-mcp/src/mcp/execution.ts` | executePublishedTool; executeDiscountTool | Integrate published discounts using existing catalogue evaluator after capability checks; do not dispatch by tool name alone. |
| `moda-interact-mcp/src/mcp/registration.ts` | registerCapabilityServer | Register each canonical name once from published snapshot, no concatenated global duplicates. |
| `moda-interact-mcp/src/mcp/service.ts` | createMcpService | Ensure list/call admission share snapshot identity and new grant validation. |
| `moda-interact-mcp/tests/unit/execution/discount-catalogue.test.ts` | catalogue tests | Retain evaluator fixtures and add published adapter parity vectors. |

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

Complete — explicit developer completion on 5 November 2026 after durable passing Attempt 1 review `7cbf62320`. Implementation `519e905` is committed/pushed. Executor/claimed_at remain null; Attempt 1 and developer execution/completion modes are preserved.

### Files Changed

Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-059-MCP-001`, branch `task/ARCH-059-MCP-001`.

- `package.json`, `package-lock.json`: pin accepted published Shared 5.1.0.
- `src/capabilities/{records,resolve}.ts`: Feature identity projection; remove global discount append.
- `src/execution/policy/discount-executor.ts`: Shared-validated published operation adapter, canonical member guard and restricted response rendering.
- `src/execution/discount-tools.ts`: label legacy projection as historical parity support; permission resolver unchanged.
- `src/mcp/{execution,ports,registration,service,snapshot}.ts`: remove direct built-in execution/registration, reject legacy identities and verify exact published manifest/grant selection.
- `src/runtime/{execution-registry,service-ports}.ts`: registry dispatch, fresh canonical membership checks and descriptor drift refusal.
- `tests/fixtures/discount-published.ts`; `tests/unit/runtime/published-discounts.test.ts`: Shared-derived v3 fixtures and admission/entitlement/protocol coverage.
- `tests/unit/execution/discount-catalogue.test.ts`; `tests/unit/capabilities/manifest.test.ts`; `tests/unit/mcp/{execution-policy,service}.test.ts`; `tests/unit/runtime/service-ports.test.ts`: evaluator parity and migrated execution expectations.
- `README.md`: strict membership behavior and coordinated rollout/rollback gate.

Implementation published as `519e905` on `origin/task/ARCH-059-MCP-001`. The preparation claim is recorded at `d56c9e12d`; this reconciliation publishes the parent report/review separately on the mirrored task branch. Executor/claim cleared, Attempt 1 preserved.

### Work Completed

- Discovery and invocation now use published capability/revision membership; no global projection or direct discount port remains in the migrated execution path.
- Production composition checks both canonical discount members, immutable definition version 3.0.0, Shared operation/version/name mapping, Product Search ownership and persisted revision identity on discovery and again on execution. Missing/malformed old release membership returns explicit UNAVAILABLE during the controlled cutover window.
- Existing evaluator handles trusted host shop/context, deadlines and cancellation. NONE/FIXED/AI_BEST_APPLICABLE, override expiry, current permission, tenant filtering and provider/platform facts remain unchanged; no evaluator redesign or copied discount input/output contract.
- Legacy built-in descriptors/grants, duplicate canonical persisted names, stale releases/revisions/descriptors and forged input shop IDs fail closed before evaluator/provider access.
- List/resource/call identity consistency, six canonical members plus unrelated members, Free/paid ACTIVE/TRIALING entitlement parity, revoked mappings/Feature/plan/capability and Shopify/WooCommerce support covered.
- Thirty-six platform/plan/mode/override vectors compare published calls against the same existing evaluator at a fixed time, including details, cross-tenant IDs, current permission changes and unavailable selected discounts. Structured facts/error semantics match; published templates intentionally supply rendered text.

### Validation Results

All commands ran in the isolated MCP task worktree with Node 24.19.0 / npm 11.17.0.

- `npm install --save-exact @modainteract/moda-interact-shared@5.1.0 --include=dev` — passed; exact accepted published dependency installed.
- `npm run schema:install:shopify -- /Users/kwadwoadomafriyie/project/moda-interact-workspace/moda-interact-commerce/lib/discovery/artifacts/admin-2026-07.json` — passed. Documented test prerequisite installed into ignored `artifacts/`; installer verified its pinned SHA-256. No schema source changed.
- `npm run test:unit` — final run passed: 347 tests, 347 passed, zero failures/skips/cancellations.
- `npm run typecheck` — passed, including declared Prisma generation.
- `npm run build` — passed, including declared Prisma generation.
- `npm run lint` — passed, zero errors/warnings.
- `git -c core.fsmonitor=false diff --check` — passed, including the published review report. Completion/frontier documentation is checked again before publication.

An earlier full run found an obsolete built-in grant-count expectation and two missing local schema-artifact prerequisites; corrected/installed, then reran the complete declared suite successfully. Earlier lint unused-variable finding was corrected before the final successful lint run.

No Docker/integration suite, live provider call, deployment, release activation or operational pause/drain was run. Canonical setup apply/dry-run/retry lifecycle behavior belongs to accepted prerequisite COMMERCE-001; this task tests MCP consumption of the complete staged subset rather than claiming to rerun those Commerce lifecycle tests.

### Deviations

No architecture or billing/permission-policy changes. Historical `projectShopDiscountTools` remains only for pre-migration parity fixtures; runtime discovery does not call it. Optional adapter-less test compositions retain unrelated published-tool behavior; production Prisma composition always supplies the discount evaluator and strict member guard.

### Assumptions

Accepted Commerce setup provisions Product Search mappings explicitly for eligible Free and paid plans and stages the complete release. An operator performs the coordinated cutover; implementation readiness does not authorize activation.

### Unresolved Issues

No required implementation/check failures remain. Developer completion is recorded below. Background is dependency-ready; System Test remains pending Background completion and manual execution. No downstream execution was started.

### Architectural Concerns

Preserve the staged-release gate: retain the old pointer until affected consumers are paused/drained and strict MCP is deployed; activate only after explicit operator confirmation. Verify unique discount names, mappings and read-only calls before resuming Background. Roll back old MCP/Background and the previous compatible pointer together. No deployment or pointer/queue/credit/delivery changes were made.

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

SHARED-002 Attempt 1 passed review and is explicitly developer-completed. Exact published Shared version is 5.1.0, release metadata `3096ca2`, accepted source `50891ef`. This task remains Pending on its other explicit prerequisites; attempt/claim/dependency list unchanged. Readiness does not authorize automatic execution, consumer deployment or cutover; the staged-release rollout gate remains binding.

## Architect Dependency Reconciliation — 5 November 2026

COMMERCE-001 Attempt 1 passed developer self-review and is explicitly developer-completed at implementation `770d6ab`. All explicit prerequisites are Complete; promoted to Ready, Attempt 0 preserved, executor/claim null. No automatic execution or cutover is authorized. Staged-release activation remains gated on accepted strict MCP and the explicit operator rollout confirmation; preserve the previous compatible release pointer until that gate.


## Developer Self-Review Passed / Accepted — Attempt 1 (2026-11-05)

**Review passed; no actionable findings.** Reconciled the actual task-owned source/test/doc changes and report under `/moda_developer_update`. Preserved `execution_mode: developer` and `completion_mode: developer`. Status Review, executor/claimed_at null, Attempt 1 unchanged; explicit developer completion is pending.

Reviewed published membership resolution, fresh execution-registry identity checks, canonical Shared-derived discount policy operation dispatch, snapshot/grant registration consistency, production strict-member wiring and evaluator reuse/parity. Runtime discovery no longer appends global built-ins. Legacy grant identities, duplicate/stale membership and descriptor drift fail closed; permissions and merchant/provider evaluator remain unchanged. The tests cover entitlement parity and task-owned admission, not coordinated deployment or live activation.

Independently ran declared `npm run test:unit`: **347 passed, 0 failed/skipped/cancelled**, exit 0. Local evidence `/tmp/arch059-mcp-review.log`. Independently checked final whitespace. Typecheck/build/lint remain implementer-reported passing checks; they were not independently rerun here. No Docker/integration or live provider run is claimed or required as substituted evidence for this bounded unit review; terminal cross-repository proof remains separately owned.

### Publication, isolation and assistance

- Canonical workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-059-MCP-001`; implementation `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-059-MCP-001`. Both matching task branches remain dedicated; no shared checkout was switched or modified by this reconciliation.
- Reviewed implementation changes started from `45138e6`. Published all 21 task-owned files (including the previously untracked adapter/fixtures/test) as implementation commit `519e905` to `origin/task/ARCH-059-MCP-001`; no unrelated files were staged. Original authorized Codex implementation assistance is retained as material developer assistance, without changing execution ownership.
- Parent task claim `d56c9e12de10d7a369ebf64f9d1aec36e5a874ae` was the pushed parent baseline. This review incorporates the previously uncommitted report and publishes this task file only; no parent gitlink, index or main branch is changed.
- No startup synchronization or claim was repeated by this review. Existing prepared developer claim is reconciled rather than incremented. No package publication, deployment, release activation or operational pause/drain occurred.

The staged-release cutover gate remains mandatory: strict MCP and compatible host artifacts, owned maintenance/drain, explicit operator activation and paired rollback. Downstream Background/System Test tasks are not promoted because this task is not Complete. The developer may make the explicit completion decision after this durable passing review.


## Developer Completion Decision — Attempt 1 (2026-11-05)

The developer explicitly invoked `/moda_developer_update ARCH-059-MCP-001 complete`. The current attempt has durable Developer Self-Review Passed / Accepted at parent `7cbf623201a6187fc6edd1e5a4ceb5e9503fca57`; all required Work Items, Acceptance Criteria and Validation are checked. Implementation `519e905aa21e8ee30acc476cec23601664070eb0` and that parent review were verified against their remote `task/ARCH-059-MCP-001` branch tips before this decision. Both dedicated worktrees were clean. No implementation changes or repeated tests were needed for this documentation-only transition.

Set status Complete; preserve Attempt 1, execution_mode/completion_mode developer, executor null and claimed_at null. This decision does not replace the historical review or claim independent architect review acceptance. Publish this task decision and the authorized dependency-frontier records on the matching parent task branch. No main merge/push or submodule gitlink change.

### Dependency frontier

ARCH-059-BACKGROUND-001: Pending -> Ready, Attempt 0 preserved, unclaimed. Its explicit prerequisites ARCH-059-SHARED-002, ARCH-059-COMMERCE-001, ARCH-059-MCP-001 and ARCH-058-BACKGROUND-001 are all Complete in the authoritative task records. ARCH-059-SYSTEM-TEST-001 remains Pending because ARCH-059-BACKGROUND-001 is not Complete; its manual execution gate remains binding. No downstream work or deployment is started. The staged-release activation, pause/drain and paired rollback gates remain unchanged.
