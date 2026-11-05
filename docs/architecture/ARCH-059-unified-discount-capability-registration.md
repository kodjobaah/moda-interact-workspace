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
Setup plan -> validated drafts/revisions -> FeatureCapabilities -> complete immutable release -> environment activation -> MCP shop snapshot/list -> capability request -> MCP current published revision admission -> existing policy evaluator -> Background offer validation. Each name appears once. Shared owns the versioned contracts/validators exported by @modainteract/moda-interact-shared/commerce; Commerce produces persisted releases; MCP consumes releases and produces trusted projections; Background consumes projections. Reuse existing capability/revision/grant structure and tool input/output schemas; no new contractHash or local competing schema. Trusted storage supplies authority, not model arguments or merchant prose.

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
Shared owns contracts and a separate publication gate. Commerce owns setup/publication. MCP owns release admission and existing provider evaluator reuse. Background owns trusted context, permitted capability requests and outreach host checks; MCP owns current published revision selection and fresh execution admission. System Test owns terminal integrated verification after all implementation gates. No Database task absent an actual schema gap. No Gateway task: no Render topology/network/secret changes. No outreach agent redesign or discount evaluation changes.

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
Once an operation/version is implemented, an authorized staff user may configure a draft via the existing Policy Operation editor, validate/test it, attach it to an existing Feature capability, publish a complete release and activate that release. Setup automates those same lifecycle APIs for these six canonical tools. UI draft save, Feature attachment or publication alone never grants an MCP call or modifies Background purpose admission. New operations/versions or new provider I/O require Shared contract, Commerce authoring registry and MCP runtime implementation/review before UI selection becomes executable; the UI cannot install arbitrary server code. Future capabilities reuse this lifecycle but are not implemented by ARCH-059. Background requests the authorized capability and exposes its MCP-resolved published tools to the agent. No Background-owned tool-name allowlist determines membership. A newly published supported tool in that authorized capability is available without a Background tool-list edit; unrelated capabilities remain excluded by capability authorization.

## Contract producer/consumer table
| Contract | Owner/producer | Consumers | Runtime validator |
|---|---|---|---|
| Policy operation IDs and tool arguments/results | Shared published commerce export | Commerce authoring, MCP dispatch, Background results | Existing policy execution schema and CommerceToolInputs/Outputs; new details ID accepted explicitly |
| Immutable release/capability/revision membership | Commerce lifecycle/storage | MCP snapshot and published execution | Existing published descriptor/revision checks and Feature/plan selection |
| Trusted manifest/grant identity | MCP snapshot then Background grant persistence | Background and MCP calls | validateRelease, manifestMatchesGrant and MCP published admission |
| Outreach purpose/capability | Background host and MCP authorization | MCP-resolved capability tool discovery and agent selection | Trusted context and current capability authorization; no host tool-name allowlist or model-granted authority |


## Dependency frontier reconciliation — 5 November 2026

ARCH-059-MCP-001 is Complete by explicit developer decision following durable passing Attempt 1 review `7cbf62320` and published implementation `519e905`. ARCH-059-BACKGROUND-001 is Ready (all four explicit prerequisites Complete), still unclaimed Attempt 0. ARCH-059-SYSTEM-TEST-001 remains Pending Background completion and manual-gated. This reconciliation authorizes no downstream execution, deployment or release activation; preserve the coordinated staged-release cutover and paired rollback procedure.


## Controlling revision-ownership decision — 5 November 2026

MCP selects and authorizes the current published revision per request. Background does not enforce an attempt-pinned remote revision. Compatible activation between discovery and execution is permitted; current tenant/membership/permission and request-local consistency remain enforced by MCP before dispatch. Background retains purpose, authorized capability requests, conversation state, policy, budgets and validated-result responsibilities. Historical revision-bearing grants remain historical and are not rewritten; revision metadata does not transfer remote revision authority to Background.

The proposed expected-call SHARED-003/004 and MCP-002 prerequisite sequence is withdrawn for BACKGROUND-001. Do not materialise or execute those proposals on this basis. Its amended task specifies the required current-admission/compatible-activation proof. Earlier expected-call review conclusions are historical and superseded; no implementation acceptance or lifecycle promotion is implied by this definition change.


## Controlling capability-discovery decision — 5 November 2026

The developer explicitly removes Background's hardcoded tool-name allowlist. Background requests an authorized capability with trusted shop/purpose context. MCP resolves the current published members and exposes their supported descriptors; the agent selects tools from that set. Background must not duplicate capability membership in OUTREACH_MCP_TOOL_NAMES, four-name filters or another static per-tool admission list. A newly published supported member of the requested authorized capability is discoverable without changing Background code; a tool in an unrelated or unauthorized capability is not admitted.

MCP retains current tenant, capability membership, entitlement, operation support and revision authorization on each invocation. Background retains conversation/lease/takeover, current merchant policy, bounded aggregate remote-call/token/time budgets and delivery/credit controls. Model text cannot request broader authority. Existing result validation and offer-safety rules remain mandatory for facts used in customer messages; dynamic discovery does not authorize unknown server code, arbitrary provider requests or bypassing contract validation. Reconcile tool-specific discovery/routing assumptions and name-based search/detail admission counters with capability-driven selection while preserving explicit aggregate resource bounds and finalization safety; do not replace the removed list with another hardcoded membership gate.

Required regression proof: expose a supported additional tool published inside the requested capability without editing Background's tool list; let the agent select and invoke it through MCP. Reject a tool from an unrelated/unentitled capability, invented model tool names, revoked permissions and missing membership before unauthorized execution. Preserve trusted purpose, current conversation state, deadlines, aggregate budgets and validated-output boundaries. No new operation implementation is authorized merely by publication.

Earlier four-tool allowlist requirements, review instructions and implementation-report statements are historical and superseded by this decision. Existing source still requires implementation reconciliation; this definition amendment neither removes runtime code itself nor certifies a passing review. Task Ready, developer-owned, Attempt 1 preserved; no automatic claim, completion, package publication, rollout or downstream promotion.


## Initial outreach extensibility acceptance — 5 November 2026

ARCH-059-BACKGROUND-001 explicitly owns removing every hardcoded tool-membership gate from initial outreach and conversation discovery/model projection/dispatch, including selector constants, fixed unions/filters, graph switches or named-first-call requirements that block an added capability member. Agent selection uses MCP-provided tools for the requested authorized capability. New supported members must work without a Background tool-name code edit; unrelated capabilities remain unauthorized. Retained tool-specific offer-fact interpreters may protect customer claims but cannot become admission gates. Aggregate budgets, state/control checks and deterministic offer/delivery safety remain required. The task's integrated regression must exercise an added non-original tool through the actual initial-outreach model/selector/client path. This is in-scope implementation work for the existing task, not a deferred cleanup or automatic implementation acceptance.


## Background Completion / Terminal Frontier — 5 November 2026

The developer explicitly completed BACKGROUND-001 Attempt 2 after passing review `4758c6e9f`, source `772f9e8`. SHARED-001/002, COMMERCE-001 and MCP-001 are also Complete. SYSTEM-TEST-001 is now dependency-ready/unclaimed at Attempt 0; its developer execution/completion and manual environment/cutover gates remain mandatory. No terminal proof, rollout, release activation or complete-architecture acceptance is implied by implementation completion.
