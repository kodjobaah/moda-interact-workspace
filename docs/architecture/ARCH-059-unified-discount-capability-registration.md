---
id: ARCH-059
title: Unified discount capability registration
status: agreed
coordinator: moda_architect
created: 2026-11-05
updated: 2026-11-05
---
# ARCH-059: Unified discount capability registration

## Status
Agreed design; portable definitions only. No implementation claimed. Remote publication requires approval after automatic review rejected the external destination.

## Current architecture and problem
Inspected MCP src/capabilities/resolve.ts resolves published capabilities then appends projectShopDiscountTools; execution/discount-tools.ts grants these descriptors to ACTIVE/TRIALING subscriptions with active plans independently of published membership. Shared src/commerce/built-in-tools.ts owns two version 2.0.0 descriptors. Commerce src/commerce/bootstrap/system-product-tools.ts publishes four product/shipping tools under product_search. Background src/services/recovery-offers/recovery-outreach-mcp-selector.service.ts lists the discount tools plus commerce_search_products and commerce_get_product under INITIAL_RECOVERY_OUTREACH. Its existing eligibility/combinations modules own offer decisions. Registration currently has two paths.

## Decision and exact identity
Feature key product_search, display name Product Search, owns reusable discount capabilities. Preserve ALWAYS_ENABLED/systemRequired policy. Capability/tool keys remain commerce_get_discount_options and commerce_get_discount_details, display names Get Discount Options and Get Discount Details. Initial outreach is runtime purpose INITIAL_RECOVERY_OUTREACH, not a new Feature, duplicate capability or duplicate registration. Existing checkout_recovery remains an additional host admission/entitlement gate for outreach. Both conversation and outreach use the same tools and evaluator.

Before global projection removal, setup provisions and verifies enabled product_search mappings for every active plan previously eligible for discounts, including Free. Feature conflicts fail visibly; no silent policy overwrite or narrowing of existing active-plan access. Merchant discount modes/settings/permissions remain unchanged. Test old/new eligibility on identical fixtures. Publication never grants permission by itself.

## Flow and contracts
Setup plan -> validated drafts/revisions -> FeatureCapabilities -> complete immutable release -> environment activation -> MCP shop snapshot/list -> pinned capability call -> existing policy evaluator -> Background offer validation. Each name appears once. Shared owns the versioned contracts/validators exported by @modainteract/moda-interact-shared/commerce; Commerce produces persisted releases; MCP consumes releases and produces trusted projections; Background consumes projections. Reuse existing capability/revision/grant structure and tool input/output schemas; no new contractHash or local competing schema. Trusted storage supplies authority, not model arguments or merchant prose.

## Data, consistency and failures
Existing Feature, plan mapping, draft/revision, capability, release and activation records suffice; no schema migration identified. Commerce uses canonical authoring/lifecycle/audit APIs, deterministic operation IDs and optimistic versions. Retry safely after partial failure. Never overwrite conflicting operator drafts, mutate immutable releases or rewrite historical grants. No provider calls in setup/transactions. Missing/inactive release/member/Feature/tool, duplicate name, wrong revision, stale identity or legacy built-in-only permission fails closed before provider I/O. Preserve NONE/FIXED/AI_BEST_APPLICABLE, override expiry, provider/tenant isolation, bounded model budgets and current offer revalidation. Unknown facts establish no saving. Return discovered schema gaps to architect for Database-owned work.

## Rollout and migration
PRODUCTION / COMPATIBLE ROLLOUT. Existing consumers and persisted state may exist.

### Deployment gate: prevent duplicate old/new registration
Commerce task completion means code and a tested STAGED immutable release are ready; it MUST NOT activate the new discount-member release against an old MCP binary. Old MCP appends global discount names, so activation there would duplicate registration. This is a hard staging gate, not a dependency cycle: Commerce implementation can be accepted while activation is deferred to coordinated rollout after MCP implementation acceptance.

1. Publish Shared package and deploy Commerce support. Plan/provision mappings, create and validate the complete staged release while the OLD active pointer remains unchanged. Record staged release ID, previous pointer/version and ready-to-activate member list. Do not activate from ordinary setup apply until the operator supplies explicit cutover confirmation; add a stage-only/default-safe activation gate to the setup workflow and test its argument handling. No new Render environment variable is required.
2. Build and validate strict MCP and Background consumer artifacts before cutover. Pause affected initial-outreach/conversation discount attempts through the existing operational pause/drain procedure; wait for old sessions/grants to finish and record zero active affected sessions. Do not delete queued work or change credit/delivery state.
3. Deploy strict MCP first, keeping the old release active temporarily. Missing canonical members produce explicit UNAVAILABLE, never legacy fallback. This bounded discount unavailability is intentional within the controlled maintenance window. Other services must not treat it as an absence of discounts.
4. Operator confirms strict MCP version and staged release ID, then explicitly activates that complete release through Commerce lifecycle concurrency checks. Verify each discount name appears exactly once, mapping parity and read-only authorized calls before deploying/resuming the new Background consumer.
5. Resume paused consumers only after list/call/host checks pass. If verification fails, remain paused and restore OLD MCP/Background artifacts together with the previous compatible release pointer; do not run old MCP against the new discount-member release. Record version/pointer pairing and rollback evidence. No task executes this deployment simply because definitions exist.

MCP must reject duplicate persisted names before server registration. No name-based deduplication is permission evidence. Missing membership cannot fall back to projectShopDiscountTools in strict runtime. Historical built-in grants remain historical and are rejected by the new path; do not rewrite them into capabilities.

## Repository responsibilities and scope
Shared owns contracts and a separate publication gate. Commerce owns setup/publication. MCP owns release admission and existing provider evaluator reuse. Background owns trusted context, pinning and outreach host checks. System Test owns terminal integrated verification after all implementation gates. No Database task absent an actual schema gap. No Gateway task: no Render topology/network/secret changes. No outreach agent redesign or discount evaluation changes.

## Observability
Reuse existing structured lifecycle/setup/MCP diagnostics; include bounded release/revision/capability IDs and failure reasons without tokens/customer payloads. No duplicate generic metrics or logger. Telemetry failures cannot affect correctness.

## Task graph
| Task | Owner | Status | Dependencies |
|---|---|---|---|
| ARCH-059-SHARED-001 | moda_shared | Ready | - |
| ARCH-059-SHARED-002 | moda_shared | Pending | ARCH-059-SHARED-001 |
| ARCH-059-COMMERCE-001 | moda_commerce | Pending | ARCH-059-SHARED-002, ARCH-058-COMMERCE-001 |
| ARCH-059-MCP-001 | moda_mcp | Complete | ARCH-059-SHARED-002, ARCH-059-COMMERCE-001, ARCH-058-MCP-003 |
| ARCH-059-BACKGROUND-001 | moda_background | Ready | ARCH-059-SHARED-002, ARCH-059-COMMERCE-001, ARCH-059-MCP-001, ARCH-058-BACKGROUND-001 |
| ARCH-059-SYSTEM-TEST-001 | moda_system_test | Pending | ARCH-059-SHARED-002, ARCH-059-COMMERCE-001, ARCH-059-MCP-001, ARCH-059-BACKGROUND-001 |

## Open Questions
None blocking definition. Publication selects the exact available approved version and records it before consumer pins.

## Handoff
Developer execution and explicit developer completion. No claims or implementation worktrees created. Materialise each canonical task via /moda_developer_create with its definition when ready; respect dependencies. System Test remains terminal and manually invoked.

## Concrete capability authoring boundary

### Canonical operation mapping
| Tool key / display name | Policy operation | Version | Input/output contract |
|---|---|---|---|
| commerce_get_discount_options / Get Discount Options | discounts.getOptions | 1.0.0 | CommerceToolInputs/Outputs.commerce_get_discount_options |
| commerce_get_discount_details / Get Discount Details | discounts.getDetails | 1.0.0 | CommerceToolInputs/Outputs.commerce_get_discount_details |

`discounts.getDetails` is a NEW operation ID required by this architecture. `discounts.evaluate` is an existing basket-evaluation operation with a different contract and MUST NOT substitute for details. Existing getOptions schema/operation is reused; the MCP published-capability adapter still requires implementation. Existing discount catalogue/provider evaluation is reused, not reimplemented. Both operations bind trusted shop/context from the host, never an input shopId. Add new details ID to Shared validation before Commerce/MCP consume it. Definition version is an immutable published tool revision version, separate from operationVersion; select the new revision identity through existing version rules, do not overwrite 2.0.0 built-in identity in place.

### Configuration versus new runtime capability
Once an operation/version is implemented, an authorized staff user may configure a draft via the existing Policy Operation editor, validate/test it, attach it to an existing Feature capability, publish a complete release and activate that release. Setup automates those same lifecycle APIs for these six canonical tools. UI draft save, Feature attachment or publication alone never grants an MCP call or modifies Background purpose admission. New operations/versions or new provider I/O require Shared contract, Commerce authoring registry and MCP runtime implementation/review before UI selection becomes executable; the UI cannot install arbitrary server code. Future capabilities reuse this lifecycle but are not implemented by ARCH-059. Initial outreach has a host-owned four-name allowlist: commerce_get_discount_options, commerce_get_discount_details, commerce_search_products, commerce_get_product. Adding a future published tool does NOT add it to outreach automatically.

## Contract producer/consumer table
| Contract | Owner/producer | Consumers | Runtime validator |
|---|---|---|---|
| Policy operation IDs and tool arguments/results | Shared published commerce export | Commerce authoring, MCP dispatch, Background results | Existing policy execution schema and CommerceToolInputs/Outputs; new details ID accepted explicitly |
| Immutable release/capability/revision membership | Commerce lifecycle/storage | MCP snapshot and published execution | Existing published descriptor/revision checks and Feature/plan selection |
| Trusted manifest/grant identity | MCP snapshot then Background grant persistence | Background and MCP calls | validateRelease, manifestMatchesGrant and MCP published admission |
| Outreach purpose/allowlist | Background host | MCP context and selector | Trusted context and explicit OUTREACH_MCP_TOOL_NAMES; no model-granted authority |


## Dependency frontier reconciliation — 5 November 2026

ARCH-059-MCP-001 is Complete by explicit developer decision following durable passing Attempt 1 review `7cbf62320` and published implementation `519e905`. ARCH-059-BACKGROUND-001 is Ready (all four explicit prerequisites Complete), still unclaimed Attempt 0. ARCH-059-SYSTEM-TEST-001 remains Pending Background completion and manual-gated. This reconciliation authorizes no downstream execution, deployment or release activation; preserve the coordinated staged-release cutover and paired rollback procedure.
