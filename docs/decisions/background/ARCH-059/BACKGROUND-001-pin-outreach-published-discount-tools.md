---
id: ARCH-059-BACKGROUND-001
architecture_id: ARCH-059
title: Consume MCP-authorized published discount capabilities
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: review
priority: 50
executor: null
claimed_at: null
attempt: 2
depends_on: ["ARCH-059-SHARED-002", "ARCH-059-COMMERCE-001", "ARCH-059-MCP-001", "ARCH-058-BACKGROUND-001"]
enables: ["ARCH-059-SYSTEM-TEST-001"]
created: 2026-11-05
updated: 2026-11-05
---
# Consume MCP-authorized published discount capabilities

## Architecture
ARCH-059; docs/architecture/ARCH-059-unified-discount-capability-registration.md. Coordinator: moda_architect.

## Objective
Consume published discount capabilities while MCP owns current release/revision selection and execution authorization for each request.

## Context
MCP currently appends global discount tools outside published membership. Follow parent architecture identity, parity and compatible migration decisions.

## Scope
Only moda-interact-background source/tests/documentation required by Work Items.

## Out of Scope
Other repositories, new Feature identities, provider evaluator redesign, schema changes, main merges and automatic execution.

## Requirements
Feature product_search (Product Search) owns both canonical discount tools exactly once. INITIAL_RECOVERY_OUTREACH remains purpose with checkout_recovery host admission. Preserve active-plan permission parity including Free through explicit provisioning verification; preserve merchant settings and provider evaluation. Fail closed on missing release or stale identity. No global fallback, duplicate descriptors, contract hashes or locally copied Shared contracts. Follow recorded rollout order.

## Work Items
- [x] Consume canonical published MCP identities in outreach and conversation; replace the existing code-owned built-in descriptor/grant path with published capability/revision identities. Preserve existing authorization checks and historical grants; do not delete or reinterpret historical records.
- [x] Keep INITIAL_RECOVERY_OUTREACH as trusted runtime purpose and require existing checkout_recovery admission before selector creation; derive tool membership from the authorized published capability, remove the hardcoded tool-name allowlist, and retain bounded execution budgets and deadline.
- [x] Request permitted capabilities through MCP; MCP resolves and validates the current published release/revision for each request before dispatch. Background must not require an attempt-pinned expected revision or reject an otherwise authorized call solely because activation changed the revision between requests. Missing or denied capabilities retain the existing explicit failure behavior; no permissive fallback.
- [x] Preserve initial outreach eligibility/combinations, current-offer revalidation, identifier-only selection, moderation, takeover, credit and delivery behavior.
- [x] Add parity tests for conversation/outreach tool identity, duplicate names, denied purpose, missing release, revoked permission and existing eligibility fixtures.

## Interfaces / Contracts
Published @modainteract/moda-interact-shared/commerce input/output, release/capability/revision/grant validators; versioned extensions owned by ARCH-059-SHARED-001, registry availability by ARCH-059-SHARED-002. Producers/consumers and storage trust boundary are normative in parent architecture.

### Controlling developer-as-architect decision — MCP-owned revision selection (2026-11-05)

MCP owns selecting the correct current published revision for each request. Background requests an allowed capability with trusted shop/purpose context; it does not select a server revision or require MCP to execute an attempt-pinned revision. A legitimate activation between discovery and execution may cause MCP to execute the newly current authorized revision. That change alone is not a stale-attempt violation.

MCP must continue validating current tenant, active release membership, capability/revision consistency, Feature/plan permissions and supported operation/input contracts before provider dispatch, including its existing fresh registry admission checks. Request-local snapshot-to-dispatch consistency remains MCP's responsibility. This does not authorize dispatch by an untrusted name alone, missing membership fallback, revoked permissions or an unsupported contract.

Background retains trusted INITIAL_RECOVERY_OUTREACH purpose, checkout_recovery admission, authorized capability selection, bounded dynamic tool discovery, current merchant policy, turn/lease/takeover checks, result validation, budgets, deadlines and delivery/credit behavior. Discovery metadata and persisted historical grants may retain revision IDs for audit/compatibility; they do not make Background the authority selecting or enforcing a remote revision. Do not rewrite historical grants. Contract/permission incompatibility must still fail closed; revision equality across separate MCP requests is not required by this task.

The earlier proposed SHARED-003, SHARED-004 and MCP-002 expected-call sequence is **withdrawn for this task**. No expected-revision context field, positive expected-call support advertisement, additional Shared publication or zero-provider-call test for activation alone is required. The portable files in `/tmp/arch059-background-prerequisites/` are superseded proposals, not prerequisites to materialise or execute under this definition.

Required deterministic proof: Background supplies trusted shop/purpose and only permitted capability arguments; MCP owns current revision selection; a compatible activation between requests is not rejected solely for revision drift; current membership/permission/tenant and incompatible input/output failures still deny safely; existing conversation-state and outreach budgets remain enforced. Use the existing accepted MCP/Shared contracts rather than inventing a new expected-call transport.

This decision changes the task contract, not its completion status. Existing implementation contains host manifest-pinning checks and must be reconciled against this boundary in a subsequent implementation/review cycle. No passing review, completion or runtime change is asserted here.

## Dependencies
- ARCH-059-SHARED-002
- ARCH-059-COMMERCE-001
- ARCH-059-MCP-001
- ARCH-058-BACKGROUND-001

## Enables
- ARCH-059-SYSTEM-TEST-001

## Acceptance Criteria
- [x] Consume canonical published MCP identities in outreach and conversation; replace the existing code-owned built-in descriptor/grant path with published capability/revision identities. Preserve existing authorization checks and historical grants; do not delete or reinterpret historical records.
- [x] Keep INITIAL_RECOVERY_OUTREACH as trusted runtime purpose and require existing checkout_recovery admission before selector creation; derive tool membership from the authorized published capability, remove the hardcoded tool-name allowlist, and retain bounded execution budgets and deadline.
- [x] Request permitted capabilities through MCP; MCP resolves and validates the current published release/revision for each request before dispatch. Background must not require an attempt-pinned expected revision or reject an otherwise authorized call solely because activation changed the revision between requests. Missing or denied capabilities retain the existing explicit failure behavior; no permissive fallback.
- [x] Preserve initial outreach eligibility/combinations, current-offer revalidation, identifier-only selection, moderation, takeover, credit and delivery behavior.
- [x] Add parity tests for conversation/outreach tool identity, duplicate names, denied purpose, missing release, revoked permission and existing eligibility fixtures.
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
Once an operation/version is implemented, an authorized staff user may configure a draft via the existing Policy Operation editor, validate/test it, attach it to an existing Feature capability, publish a complete release and activate that release. Setup automates those same lifecycle APIs for these six canonical tools. UI draft save, Feature attachment or publication alone never grants an MCP call or modifies Background purpose admission. New operations/versions or new provider I/O require Shared contract, Commerce authoring registry and MCP runtime implementation/review before UI selection becomes executable; the UI cannot install arbitrary server code. Future capabilities reuse this lifecycle but are not implemented by ARCH-059. Background requests the authorized capability and exposes its MCP-resolved published tools to the agent. No Background-owned tool-name allowlist determines membership. A newly published supported tool in that authorized capability is available without a Background tool-list edit; unrelated capabilities remain excluded by capability authorization.

### Verified implementation touchpoints
Paths below exist at definition time; changes are task requirements, not completed work.

| File | Existing symbol/surface | Required change |
|---|---|---|
| `moda-interact-background/src/services/recovery-offers/recovery-outreach-mcp-selector.service.ts` | OUTREACH_MCP_TOOL_NAMES; RecoveryOutreachMcpSelectorService | Remove OUTREACH_MCP_TOOL_NAMES membership filtering; discover the requested authorized capability's published tools and let the agent select among them. Preserve list-before-call, current authorization and unrelated-capability isolation. |
| `moda-interact-background/src/commerce/mcp-client.ts` | CommerceMcpClient; CommerceOutreachMcpIdentity; encodeCommerceContext | Carry trusted purpose and canonical release/capability identities through client transport, never model inputs. |
| `moda-interact-background/src/commerce/grants.ts` | validateRelease; persistGrant; manifestMatchesGrant | Persist and validate canonical published identity; no synthesis from built-in descriptor trust. |
| `moda-interact-background/src/agents/initial-outreach-offer.graph.ts` | initial outreach graph module | Preserve first-call/options sequencing, validated result projection and budgets. |
| `moda-interact-background/src/agents/initial-outreach-offer.eligibility.ts` | evaluateCheckoutDiscount | Regression protection only: same authorized facts yield same eligibility. |
| `moda-interact-background/tests/unit/services/recovery-offers/recovery-outreach-mcp-selector.service.test.ts` | selector tests | Test exact list, new unrelated published tool excluded, stale identity and missing members. |

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
| Extra future published capability | Available only through authorized capability selection; unrelated capabilities remain excluded. New supported tools within the requested capability require no host name-list change |
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

In Progress — developer-owned Attempt 2. Authorized implementation assistance completed the amended Background scope and required focused validation. Ready for `/moda_developer_update ARCH-059-BACKGROUND-001` reconciliation/review; no self-review acceptance or completion decision is claimed. Status, developer executor, claim and Attempt 2 remain unchanged. No downstream execution or promotion.

The controlling MCP-owned revision-selection and dynamic-discovery decisions supersede Attempt 1's expected-call blocker and four-tool requirements. SHARED-003/004 and MCP-002 remain withdrawn proposals, not prerequisites for this task. No expected-revision field or positive enforcement advertisement was added.

### Files Changed

Implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-059-BACKGROUND-001`, branch `task/ARCH-059-BACKGROUND-001`; 17 task-owned changed/new files relative to published `099563513207fcc1e67feedcee3d9ed10baaa45c`:

- `src/services/recovery-offers/recovery-outreach-mcp-selector.service.ts`: current published Feature-scope projection; dynamic descriptors and generic Shared input/result validation; no named membership set or quota; existing checkout_recovery factory admission retained.
- `src/agents/initial-outreach-offer.graph.ts`: dynamic per-model-step discovery, generic result flow, agent-selected call order; remove forced first/options and injected final product read; retain deterministic fact interpretation and aggregate limits.
- `src/agents/initial-outreach-offer.instructions.ts`: agent chooses from supplied capability descriptors without a mandatory first tool.
- `src/commerce/{mcp-client,published-tools,grants,host}.ts`: remove attempt revision equality; MCP owns current selection, current input checks and capability-key routing remain. Conversation execution derives its retained Feature scope from historical release membership and projects current MCP members within that scope. Historical database grant rows are never rewritten.
- `tests/fixtures/commerce/outreach-context.ts` (new); `tests/integration/commerce/host-suites/dynamic-outreach.ts` (new): actual initial agent/graph/selector/client loopback extension, isolation, activation and limits proof.
- `tests/integration/commerce/{host.fixture,host.test}.ts`; `tests/integration/commerce/host-suites/grants.ts`: trusted outreach context harness; compatible activation and retained grant-history/scope expectations.
- `tests/unit/agents/initial-outreach-offer.graph.test.ts`; `tests/unit/commerce/{published-client,published-tools}.test.ts`; `tests/unit/services/recovery-offers/recovery-outreach-mcp-selector.service.test.ts`: remove obsolete first-call, injected-read, static-membership and stale-revision assumptions while preserving fact-safety cases.
- `README.md`: current responsibility boundary, generic execution, scope and retained aggregate controls; obsolete prerequisite/allowlist text removed.

### Work Completed — correction and gate inventory

1. **MCP-owned revision selection implemented.** Removed pinnedManifest and pre/post revision equality refusal, manifestMatchesGrant-based remote revision veto and selector attempt comparison. Compatible activation is accepted by unit and real loopback paths. Current membership, current input schema, Shared result-envelope validation and persisted current release/member consistency checks remain. No unknown contract/permission fallback.
2. **Selector membership gates removed.** Removed OUTREACH_MCP_TOOL_NAMES, ALLOWED_TOOLS, OutreachMcpToolName, required options/details presence, per-tool Shared input/output registry membership and named search/detail quotas. Trusted product_search Feature ID plus the current MCP-authorized published projection determines membership. The full shop projection is validated internally; only the selected Feature's descriptors are exposed to the outreach model. Identically named tools belonging only to another Feature are excluded.
3. **Graph/model/dispatch gates removed.** Removed options-first final/dispatch checks, name-specific product stage restrictions, named search/detail counters, name-based pre-call source prerequisites, exhaustive default rejection and automatic insertion of commerce_get_product after a final choice. Discovery refreshes each model step; calls must belong to that advertised set and current selector membership. An additional supported member uses its published input schema and Shared CommerceToolResult envelope without a new Background handler or schema-switch entry.
4. **Safe result handling retained.** Generic outputs are bounded and delivered to the next model step as untrusted data. Known options/details/product interpreters remain solely to redact/project known facts and populate deterministic offer/product evidence. They do not gate advertising, selection or execution of other supported members. Positive customer-facing discounts/promotions still require source-bound known facts and existing eligibility/combinations/finalization. Missing exact product evidence no longer injects a host-selected call and cannot establish a promotion.
5. **Authority and budgets retained.** checkout_recovery admission precedes every production selector factory. Trusted shop/purpose, current merchant policy and conversation lease/control/takeover checks remain. Historical grants are retained as audit/scope records; per-turn current published runner projections do not write or widen their stored Feature scope. Current MCP membership remains required. Aggregate 16 remote calls, 8 model steps, at most 512 output tokens per step, 45-second graph deadline, 32 KiB projected result and 128 KiB message history remain. Generic duplicate-call protection remains; no replacement per-tool admission list.
6. **Required integrated extension regression implemented.** The existing loopback MCP/model harness runs the actual initial-outreach agent, graph, selector and client. A published_store_guidance member absent from the original four is advertised, selected FIRST by the agent, reaches the MCP tools/call boundary and returns a bounded result to the next actual model request. No special production handler/list entry exists for it. A valid NO_VERIFIED_OFFER final outcome leaves grant/transaction/credit/delivery writes untouched. Removal, revocation, unrelated-only membership and invented names all deny without a tool call. Compatible activation succeeds; aggregate call/deadline, cancellation and result-size limits stop the dynamic path.
7. **Historical review disposition.** Attempt 1 review items 1–3 (expected-call contract, publication, support advertisement and activation-alone zero-provider tests) are superseded by the controlling definition decision, not left blocked or falsely reported implemented. Its fourth item's static four-tool requirement is superseded by the mandatory dynamic scope; current merchant policy, admission, finalization and aggregate safety controls are retained and revalidated. No withdrawn prerequisite task was materialised or executed.

### Validation Results

Declared commands ran in the dedicated implementation worktree using Node 24.19.0 / npm 11.17.0, recovered only through the canonical workspace bootstrap. Shared remains the accepted published 5.1.0; no dependency upgrade or new Shared contract in this attempt.

- `npm test -- tests/unit/commerce/published-tools.test.ts tests/unit/commerce/published-client.test.ts tests/unit/commerce/published-grants.test.ts tests/unit/services/recovery-offers/recovery-outreach-mcp-selector.service.test.ts tests/unit/services/recovery-offers/initial-outreach-offer-selection.service.test.ts tests/unit/services/recovery-offers/initial-outreach-agent-context.service.test.ts tests/unit/services/recovery-product-media/recovery-product-image-resolver.test.ts tests/unit/services/effective-billing-policy.service.test.ts` — **8 files / 65 tests passed**, exit 0. `/tmp/arch059-bg2-focused-final.log`.
- `npm run test:commerce-recommendations` — **20 files / 197 tests passed**, exit 0. Includes actual graph/agent, eligibility/combinations, recommendation facts, revalidation and automated recovery template/finalization regressions. `/tmp/arch059-bg2-recommendations.log`.
- `npm run test:commerce-host` — **81 tests passed**, exit 0, including 11 actual loopback dynamic/scope/activation/resource scenarios alongside existing conversation host authorization, diagnostics, state, lifecycle and finalization tests. `/tmp/arch059-bg2-host-final.log`.
- `npm run build` — passed, including declared Prisma generation and TypeScript compilation. No separate typecheck script exists. `/tmp/arch059-bg2-build-final.log`.
- `npm run lint` — passed, no diagnostics. `/tmp/arch059-bg2-lint-final.log`.
- `git -c core.fsmonitor=false diff --check` — passed in implementation and after report update.
- Source inventory for removed fixed-name gates returned no matches for OUTREACH_MCP_TOOL_NAMES, ALLOWED_TOOLS, OutreachMcpToolName, FIRST_TOOL_CALL_MUST, MAX_PRODUCT_SEARCHES/MAX_PRODUCT_DETAIL_READS, pinnedManifest, OUTREACH_TOOL_NOT_ALLOWED or obsolete named stage/read admission reasons on the affected agent/commerce/selector paths.

Total focused proof: **343 passing tests** across these distinct suites. The full unit suite was not rerun in Attempt 2 and is not claimed green. Attempt 1's published report at parent `4b27ce2a9` retains the exploratory full-suite failure evidence and controlled pre-task comparison: 35 failures outside task files reproduced on the pre-task source, with child-process timing variability isolated separately. That historical broad result is not substituted for this attempt's focused tests and does not describe a newly run full suite.

No Docker/PostgreSQL/Redis integration, live provider, actual model API, deployment, release activation, customer send or stored grant/credit migration was run. Loopback fixtures simulate authorized supported published operations; no new operation implementation was added. Setup/provisioning/retry behavior remains accepted Commerce prerequisite evidence.

### Git / VCS

- Canonical primary workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Dedicated parent `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-059-BACKGROUND-001`; dedicated implementation `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-059-BACKGROUND-001`; both branch `task/ARCH-059-BACKGROUND-001`. No shared checkout switch or another task worktree reuse.
- Launcher preparation: both remote task branches not-needed for fast-forward, origin/main already-current; explicit dependency gate passed. Recursive submodule sync/update passed; database at recorded `bd2d09066a8eb178a56f48fbbf88df637c411059`.
- Developer Attempt 2 claim `8ba1fd0ab7950caf3d52d3e2e1b7113c402fd208` pushed, claimed_at 2026-11-05T23:14:01Z. No repeated claim/preparation.
- Published implementation baseline `099563513207fcc1e67feedcee3d9ed10baaa45c`. At the developer's explicit request to commit/push, Attempt 2 implementation was committed as `772f9e8` (17 task-owned files) and pushed successfully to implementation `origin/task/ARCH-059-BACKGROUND-001`. This task-only report update is committed/pushed to the matching parent task branch; its resulting SHA is reported after publication. No lifecycle or acceptance transition is implied.
- No submodule gitlink staged; no main merge/push, withdrawn prerequisite materialisation, dependency promotion, deployment or activation.

### Deviations / Assumptions

None from the controlling amended scope. The fixed product_search Feature key is the trusted host-owned capability group, not a tool-name membership list; current MCP authorization supplies its members. Conversation Feature scope is read from historical grant/release membership and kept separate from current remote revision selection. Shared schemas validate published inputs/envelopes; generic results alone cannot supply new deterministic offer authority.

### Unresolved Issues / Architectural Concerns

No implementation or required focused-check failure remains. Developer reconciliation/review and explicit completion remain separate workflow actions. The earlier expected-call gap and portable prerequisites are withdrawn by the task's controlling decision and must not block this attempt. Operator rollout/activation gates remain unchanged; implementation readiness does not execute them.

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

COMMERCE-001 Attempt 1 passed developer self-review and is explicitly developer-completed at implementation `770d6ab`. Remains Pending on remaining explicit prerequisites; attempt/claim/dependency list unchanged. No automatic execution or cutover is authorized. Staged-release activation remains gated on accepted strict MCP and the explicit operator rollout confirmation; preserve the previous compatible release pointer until that gate.


## Architect Dependency Reconciliation — 5 November 2026

Developer-completed ARCH-059-MCP-001 after durable accepted Attempt 1 review `7cbf62320` and published implementation `519e905`. All explicit prerequisites are Complete (ARCH-059-SHARED-002, ARCH-059-COMMERCE-001, ARCH-059-MCP-001, ARCH-058-BACKGROUND-001). Promoted Pending -> Ready; Attempt 0, executor null and claimed_at null preserved. No claim/execution is authorized by reconciliation alone. Retain staged-release cutover, pause/drain and operator activation gates.


## Developer-authorized definition and publication update — 5 November 2026

The developer requested: “can you update the task definition commit and push”. The definition now explicitly records the architect-confirmed expected-call prerequisite, positive enforcement support and zero-provider race tests. Original acceptance requirements are preserved, not waived. The original formal dependencies remain unchanged until the portable prerequisite definitions are materialised and reconciled through the architect workflow. No lifecycle/claim/attempt or architect review decision was changed.

Both matching task branches are published for preservation/review of the current implementation state. Publication does not establish task completion or readiness for deployment; the cross-repository prerequisite remains required. No main branch or submodule gitlink is staged or updated.


## Developer Self-Review - Changes Requested — Attempt 1 (2026-11-05)

### Decision

**Review fails: required expected-call enforcement is not implemented.** Reconciled the actual published implementation `099563513207fcc1e67feedcee3d9ed10baaa45c`, report, controlling prerequisite amendment and portable handoff using `/moda_developer_update`. Return to Ready with executor/claimed_at null and Attempt 1 unchanged, as required by the invoked developer review workflow. Execution/completion modes remain developer/developer. No completion, new claim or next attempt is created here. Historical instructions to preserve the active attempt describe the earlier assistance pause; this explicit review now clears the claim while preserving its source and history.

### Required corrections and ordering

1. Materialise, implement, review and complete the architect-defined SHARED-003, SHARED-004 and MCP-002 prerequisite sequence through its normal authorized workflows. The portable handoff is not implementation or dependency acceptance. This review creates no new tasks and does not fabricate formal dependency edges to nonexistent materialised records. Architect reconciliation of the durable dependencies is required before continuation, as specified by the controlling amendment; Ready here is the changes-requested workflow disposition, not permission to bypass that gate.
2. Consume the exact accepted published Shared contract and send the pinned release/capability/key/tool/revision/name through trusted client context for both conversation and outreach. Require positive MCP enforcement support; older servers ignoring extra context keys must fail closed. Model arguments must never supply or replace the identity.
3. Add deterministic cross-boundary tests for unchanged identity success, malformed/foreign identity denial and release activation in both windows: before MCP request snapshot and before fresh registry validation. Both race cases must reject before dispatch/provider I/O with zero provider calls. Host pre/post manifest reads and operational pause/drain do not substitute for enforcement.
4. Preserve published grant history, checkout_recovery admission, four-tool outreach allowlist, current policy/permission, budgets, deadlines, eligibility/combinations and delivery/credit behavior. Rerun relevant declared checks and update the report before resubmitting. Preserve the published partial implementation rather than resetting it.

### Review evidence and limits

Inspected `src/commerce/mcp-client.ts` manifest/list/call changes: it pins and rereads the manifest but sends only capability name and model arguments in tools/call; it does not attach the required expected tuple or check positive enforcement support. Inspected outreach selector list/admission and the documented prerequisite handoff at `/tmp/arch059-background-prerequisites/HANDOFF.md`. The canonical task tree contains no materialised SHARED-003/004 or MCP-002 definitions at this review. Thus the submission's own unmet before-provider-I/O criterion remains concrete, not merely missing prose.

Implementation HEAD equals its remote task ref at `099563513207fcc1e67feedcee3d9ed10baaa45c`; canonical implementation and parent worktrees were clean before this task update. The source whitespace check passed. Dedicated paths, matching task branches, preparation/claim repair, publication and material authorized Codex assistance are recorded in the Completion Report and remain preserved.

Reviewed the reported 64 focused tests, 197 recommendation tests, 70 host tests, build/lint and controlled broad-suite baseline comparison. **No tests, build, lint, Docker or live provider validation were rerun by this review.** Reported full-suite failures remain disclosed and are not relabelled as a passing suite. Existing green tests cannot satisfy the missing expected-call/race cases. No implementation change, integration merge, dependency publication, cutover, release activation, grant migration or customer send is made by this reconciliation.

### Downstream

ARCH-059-SYSTEM-TEST-001 remains gated on Background completion and terminal manual execution requirements. No downstream task is promoted. Explicit developer completion is unavailable until required work and a later passing review are durable.


## Definition Decision Superseding Expected-Call Blocker — 2026-11-05

The developer explicitly directed MCP-owned revision selection and requested this definition update. The earlier Developer Self-Review Changes Requested record remains historical, but its expected-call prerequisites and activation-alone zero-provider-call criterion are superseded by the controlling decision above. They must not be used to block this task or spawn additional work. The task remains Ready, developer/developer, claim null, Attempt 1 unchanged. Reconcile the existing host manifest/grant checks and tests with the amended responsibility boundary before a new passing review; do not simply relabel the prior implementation accepted. Formal dependency IDs are unchanged. No downstream promotion, claim, code change, package publication, deployment or activation occurs.


## Controlling capability-discovery decision — 5 November 2026

The developer explicitly removes Background's hardcoded tool-name allowlist. Background requests an authorized capability with trusted shop/purpose context. MCP resolves the current published members and exposes their supported descriptors; the agent selects tools from that set. Background must not duplicate capability membership in OUTREACH_MCP_TOOL_NAMES, four-name filters or another static per-tool admission list. A newly published supported member of the requested authorized capability is discoverable without changing Background code; a tool in an unrelated or unauthorized capability is not admitted.

MCP retains current tenant, capability membership, entitlement, operation support and revision authorization on each invocation. Background retains conversation/lease/takeover, current merchant policy, bounded aggregate remote-call/token/time budgets and delivery/credit controls. Model text cannot request broader authority. Existing result validation and offer-safety rules remain mandatory for facts used in customer messages; dynamic discovery does not authorize unknown server code, arbitrary provider requests or bypassing contract validation. Reconcile tool-specific discovery/routing assumptions and name-based search/detail admission counters with capability-driven selection while preserving explicit aggregate resource bounds and finalization safety; do not replace the removed list with another hardcoded membership gate.

Required regression proof: expose a supported additional tool published inside the requested capability without editing Background's tool list; let the agent select and invoke it through MCP. Reject a tool from an unrelated/unentitled capability, invented model tool names, revoked permissions and missing membership before unauthorized execution. Preserve trusted purpose, current conversation state, deadlines, aggregate budgets and validated-output boundaries. No new operation implementation is authorized merely by publication.

Earlier four-tool allowlist requirements, review instructions and implementation-report statements are historical and superseded by this decision. Existing source still requires implementation reconciliation; this definition amendment neither removes runtime code itself nor certifies a passing review. Task Ready, developer-owned, Attempt 1 preserved; no automatic claim, completion, package publication, rollout or downstream promotion.


## Mandatory implementation scope — remove fixed tool-membership gates (2026-11-05)

This work belongs to **this task**, not a future cleanup. The developer explicitly requires initial outreach to be extensible by publishing supported tools into its authorized capability without Background source changes. A definition-only removal or deletion of one constant is not sufficient for acceptance.

### Source inventory and authorized changes

Audit the complete initial-outreach and conversation discovery → model tool projection → selection → argument validation → dispatch → result-consumption path. Remove every fixed tool-name array/set, literal-name union, filter, exhaustive switch/default rejection or name-based prerequisite that functions as a membership/admission gate. This includes `OUTREACH_MCP_TOOL_NAMES`, `ALLOWED_TOOLS`, `OutreachMcpToolName`, required named tools, model-call filtering, fixed first-tool requirements and fixed tool-specific admission counters in `recovery-outreach-mcp-selector.service.ts` and `initial-outreach-offer.graph.ts`. Inspect equivalent client/host/published-tools paths; do not relocate the same list or replace it with a four-entry registry/schema union.

Extend this task's editable Background scope to the graph, agent/types/model-tool projection and their tests as needed for dynamic capability execution. Earlier directions to leave the graph unchanged, preserve options-first dispatch or preserve fixed search/detail invocation quotas are superseded where they impose hardcoded membership or tool selection. Retain explicit aggregate remote-call/token/output/time limits and current cancellation/lease/control checks. The agent chooses the next tool from the current MCP-provided capability descriptors; Background must not force an injected named-tool call as a substitute for that choice.

Tool-specific **fact interpretation** may remain only where needed to validate an existing offer/product fact used in a controlled customer response. Such interpretation must not prevent an additional supported capability member from being advertised, selected, called or returning a bounded validated result to the agent. New tool outputs do not automatically establish eligibility, savings or delivery authority; existing deterministic final-result and offer-safety validation remains mandatory. Use MCP/published schemas and supported generic result handling for dynamic execution; do not require a new Background schema switch entry for each tool merely to run it. If current contracts cannot safely support that generic path, report the exact missing interface for architect reconciliation before widening another repository.

### Additional Work Items / Acceptance Criteria

- [x] Inventory and remove all Background hardcoded tool-membership/admission gates on the affected conversation and initial-outreach paths, including graph/model projection/dispatch gates rather than only selector constants. Record each removed gate and any retained name-specific fact interpreter with its non-admission purpose.
- [x] The requested authorized capability's supported published descriptors determine the agent-visible tool set. The agent can select an additional supported member absent from the original four names; no Background source/config allowlist edit is needed.
- [x] Adding, replacing or removing a supported tool within that capability is reflected through MCP discovery/current authorization. Unrelated or unauthorized capabilities and model-invented tools remain denied; no global tools/list exposure or grant widening.
- [x] Preserve trusted shop/purpose, checkout_recovery admission, current merchant offer policy, conversation state, takeover/moderation, aggregate budgets/deadlines and credit/delivery behavior. Preserve deterministic validation of any customer-facing offer facts.
- [x] Remove obsolete fixed-name test assumptions. Do not manufacture extension support with a mock that bypasses the actual graph/model projection or dispatch gate.

### Required integrated extension regression

Use the existing loopback MCP/model harness and the actual initial-outreach agent/selector/client path. Provide an extra supported tool descriptor inside the authorized capability, with a name not present in the original four. Capture the actual model request showing that descriptor; script the agent to choose it; assert the invocation reaches the MCP boundary and its bounded result reaches the next model step. Do not add a special production handler/list entry for the fixture name. Assert a complete valid final outcome using the existing finalization rules and unchanged delivery/credit boundary. Repeat with that member removed/revoked and with an identically named tool only in an unrelated capability: both must remain unavailable/denied. Prove aggregate call/deadline limits and conversation cancellation still stop the dynamic path.

Run the declared focused agent/graph, selector/client, conversation-host and offer/finalization regressions plus build/lint. Report actual commands/results and any unchanged baseline failures separately. No live provider run or new operation implementation is introduced by this acceptance test.

This amendment is authoritative over historical hardcoded-tool requirements and prior source reports. Task remains Ready, developer/developer, Attempt 1 preserved with no active claim. Runtime allowlist removal is still implementation work; no passing review/completion or automatic execution is asserted by this definition commit.


## Developer-authorized Attempt 2 publication — 5 November 2026

The developer explicitly requested commit and push after the amended implementation and its 343 passing focused tests, build and lint. Published implementation `772f9e8` and this current task/report record on matching `task/ARCH-059-BACKGROUND-001` branches. Staged only the 17 task-owned implementation files and this task document; whitespace checks passed. No implementation change or repeated validation was required for publication. At that publication point status remained In Progress, executor developer, Attempt 2; the later Developer Self-Review record governs current review status. No main merge/push, gitlink change, deployment, activation or downstream promotion.


## Developer Self-Review Passed / Accepted — Attempt 2 (2026-11-05)

**Review passed under the controlling MCP-owned revision and dynamic capability-discovery amendments. No actionable findings.** Reconciled implementation `772f9e88d65b32c26bb64d03ca996b4757c9873c`, published report and the actual 17-file correction. Status Review, executor/claimed_at null, Attempt 2 unchanged. Execution/completion remain developer/developer; explicit `/moda_developer_update ARCH-059-BACKGROUND-001 complete` is still required. Earlier expected-call prerequisites and fixed-name review requirements are superseded, not outstanding blockers.

### Source and acceptance reconciliation

The selector derives tool membership from the authorized product_search Feature projection and current MCP descriptors. Fixed four-name sets/unions, forced first-tool calls, name-specific admission quotas and default unknown-tool rejection were removed from the agent/selector path. Generic supported results reach the next model step without a fixture-specific production dispatch entry. Retained name-specific interpretation protects existing offer/product facts rather than controlling whether an added supported member can execute.

The client no longer pins a manifest/revision across requests. MCP selects the current revision; current membership/input validation and trusted shop/purpose remain enforced. Conversation scope derives from the historical grant's authorized Feature membership without rewriting stored grants or admitting unrelated Features. Current offer policy, aggregate budgets/deadlines, cancellation, conversation controls and deterministic offer/result validation remain in force.

Inspected the actual loopback extension regression: the new member appears in the model request, is chosen first, crosses the selector/client/MCP boundary and returns bounded data to the next model step before a valid NO_VERIFIED_OFFER final outcome. Removed/revoked/unrelated/invented cases reject without a tool request. Additional cases cover compatible activation, unchanged historical grant scope, aggregate call/deadline limits, cancellation, oversized results and absence of injected named-tool discovery.

### Validation

- Independently reran the isolated loopback host suite using the declared `vitest.commerce-host.config.ts`: **81 tests passed**, exit 0. Local evidence `/tmp/arch059-bg-attempt2-review-host.log`.
- Independently reran the eight-file focused published-tools/client/grants, selector, offer selection/context, product-media and billing-policy set listed in the report: **65 tests passed**, exit 0. Local evidence `/tmp/arch059-bg-attempt2-review-unit.log`.
- Independently checked `git diff --check 0995635 HEAD`: passed, and source HEAD equals its remote task ref.
- Reviewed submitted 197 recommendation tests, build/lint and the disclosed broad-suite baseline comparison; these checks were not independently repeated. No complete full-unit-suite pass is claimed. No Docker, live provider/model, deployment or activation was performed by this review.

### Publication and ownership

Implementation `772f9e8` is already committed/pushed. The canonical implementation worktree is clean; the parent task worktree was clean before this update. Matching dedicated task paths/branches, Attempt 2 claim `8ba1fd0ab`, preparation/synchronization, unchanged Database pin and authorized Codex assistance are recorded in the Completion Report. Assistance and publication do not transfer developer completion authority. Only this parent task record is committed/pushed by the reconciliation; no implementation or gitlink change and no main merge.

### Follow-up

Explicit developer completion remains pending. SYSTEM-TEST-001 is not promoted while Background remains Review; terminal execution and staged-release rollout remain separately gated. This passing review certifies the amended task scope and deterministic local evidence, not live provider behavior or deployment.
