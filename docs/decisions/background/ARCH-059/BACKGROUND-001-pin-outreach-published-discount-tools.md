---
id: ARCH-059-BACKGROUND-001
architecture_id: ARCH-059
title: Pin outreach published discount tools
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: ready
priority: 50
executor: null
claimed_at: null
attempt: 1
depends_on: ["ARCH-059-SHARED-002", "ARCH-059-COMMERCE-001", "ARCH-059-MCP-001", "ARCH-058-BACKGROUND-001"]
enables: ["ARCH-059-SYSTEM-TEST-001"]
created: 2026-11-05
updated: 2026-11-05
---
# Pin outreach published discount tools

## Architecture
ARCH-059; docs/architecture/ARCH-059-unified-discount-capability-registration.md. Coordinator: moda_architect.

## Objective
Pin outreach published discount tools through canonical setup, immutable release and MCP authorization.

## Context
MCP currently appends global discount tools outside published membership. Follow parent architecture identity, parity and compatible migration decisions.

## Scope
Only moda-interact-background source/tests/documentation required by Work Items.

## Out of Scope
Other repositories, new Feature identities, provider evaluator redesign, schema changes, main merges and automatic execution.

## Requirements
Feature product_search (Product Search) owns both canonical discount tools exactly once. INITIAL_RECOVERY_OUTREACH remains purpose with checkout_recovery host admission. Preserve active-plan permission parity including Free through explicit provisioning verification; preserve merchant settings and provider evaluation. Fail closed on missing release or stale identity. No global fallback, duplicate descriptors, contract hashes or locally copied Shared contracts. Follow recorded rollout order.

## Work Items
- [ ] Consume canonical published MCP identities in outreach and conversation; replace the existing code-owned built-in descriptor/grant path with published capability/revision identities. Preserve existing authorization checks and historical grants; do not delete or reinterpret historical records.
- [ ] Keep INITIAL_RECOVERY_OUTREACH as trusted runtime purpose and require existing checkout_recovery admission before selector creation; preserve four-tool outreach allowlist, budgets and deadline.
- [ ] Pin release/capability/revision within attempt; missing/stale/mismatched tools follow existing unavailable/no-verified-offer behavior, never permissive fallback. Require the versioned Shared expected-call identity and positive MCP enforcement support described in the definition amendment; host pre/post checks alone do not satisfy this item.
- [ ] Preserve initial outreach eligibility/combinations, current-offer revalidation, identifier-only selection, moderation, takeover, credit and delivery behavior.
- [ ] Add parity tests for conversation/outreach tool identity, duplicate names, denied purpose, missing release, revoked permission and existing eligibility fixtures.

## Interfaces / Contracts
Published @modainteract/moda-interact-shared/commerce input/output, release/capability/revision/grant validators; versioned extensions owned by ARCH-059-SHARED-001, registry availability by ARCH-059-SHARED-002. Producers/consumers and storage trust boundary are normative in parent architecture.

### Architect-confirmed expected-call prerequisite (definition amendment)

The implementation exposed a cross-request pinning gap in accepted MCP-001. A host manifest read followed by a call is not an atomic expected-release assertion. Preserve the original before-provider-I/O requirement; pre/post host checks and pause/drain do not replace it.

Before this task can return for review:

- Complete the architect-defined sequence ARCH-059-SHARED-003 (validated trusted expected published-call identity), ARCH-059-SHARED-004 (exact package publication) and ARCH-059-MCP-002 (server enforcement and positive support advertisement).
- Consume that exact published Shared contract. Send the attempt-pinned release/capability/key/tool/revision/name in trusted client context; model arguments cannot supply or override it. Reject missing enforcement support because older MCP ignores unknown context fields.
- Prove unchanged identity success, malformed/foreign identity rejection, and release activation both before the MCP request snapshot and before its fresh registry check. Both race cases must reject before dispatch/provider I/O, with zero provider calls.
- Preserve historical grants and the existing four-name outreach purpose allowlist, current policy checks, budgets, deadlines, credit and delivery semantics.

These three prerequisites are portable architect definitions, not yet materialised/claimed/complete tasks. Their exact contract and resumption sequence are recorded in this definition and its report. The formal dependency list must be reconciled by the architect when they are materialised; no missing prerequisite is treated as satisfied. Preserve this active developer Attempt 1 rather than silently reclaiming it.

## Dependencies
- ARCH-059-SHARED-002
- ARCH-059-COMMERCE-001
- ARCH-059-MCP-001
- ARCH-058-BACKGROUND-001

## Enables
- ARCH-059-SYSTEM-TEST-001

## Acceptance Criteria
- [ ] Consume canonical published MCP identities in outreach and conversation; replace the existing code-owned built-in descriptor/grant path with published capability/revision identities. Preserve existing authorization checks and historical grants; do not delete or reinterpret historical records.
- [ ] Keep INITIAL_RECOVERY_OUTREACH as trusted runtime purpose and require existing checkout_recovery admission before selector creation; preserve four-tool outreach allowlist, budgets and deadline.
- [ ] Pin release/capability/revision within attempt; missing/stale/mismatched tools follow existing unavailable/no-verified-offer behavior, never permissive fallback. Require the versioned Shared expected-call identity and positive MCP enforcement support described in the definition amendment; host pre/post checks alone do not satisfy this item.
- [ ] Preserve initial outreach eligibility/combinations, current-offer revalidation, identifier-only selection, moderation, takeover, credit and delivery behavior.
- [ ] Add parity tests for conversation/outreach tool identity, duplicate names, denied purpose, missing release, revoked permission and existing eligibility fixtures.
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
| `moda-interact-background/src/services/recovery-offers/recovery-outreach-mcp-selector.service.ts` | OUTREACH_MCP_TOOL_NAMES; RecoveryOutreachMcpSelectorService | Preserve explicit four-name allowlist and list-before-call; consume canonical identity without auto-admitting other published tools. |
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

In Progress — developer-owned Attempt 1; authorized Codex implementation assistance completed the Background-local changes and validation below. NOT ready for review/completion: the before-provider-I/O pinning criterion has an architect-confirmed Shared/MCP prerequisite gap. Executor, claim, attempt and execution/completion modes are unchanged. No downstream task started.

### Files Changed

Canonical implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-059-BACKGROUND-001`, branch `task/ARCH-059-BACKGROUND-001` (21 committed task-owned files):

- `package.json`, `package-lock.json`: accepted published Shared 5.1.0.
- `src/commerce/published-tools.ts` (new): Shared manifest/grant validation, published-only admission and capability-key list checks; valid underlying tool reuse remains supported.
- `src/commerce/{grants,mcp-client,host}.ts`: published member/revision persistence validation, historical built-in refusal without rewriting records, attempt manifest pinning, pre/post result validation, capability-key routing and preserved current-offer policy refresh.
- `src/services/recovery-offers/{recovery-outreach-mcp-selector,initial-outreach-offer-selection,current-outreach-offer-revalidation}.service.ts`, `src/agents/initial-outreach-offer.agent.ts`, `src/services/recovery-product-media/recovery-product-image-resolver.ts`: async production factory admission through existing checkout_recovery entitlement before selector/client creation; pinned outreach discovery and calls.
- `tests/fixtures/commerce/published-discounts.ts` (new), `tests/unit/commerce/published-{tools,client,grants}.test.ts` (new), `tests/unit/services/recovery-offers/recovery-outreach-mcp-selector.service.test.ts`: Shared-derived fixtures, persisted identities, stale/missing/duplicate/legacy/purpose failures and admission tests.
- `tests/integration/commerce/host.fixture.ts`, `tests/integration/commerce/host-suites/{authority,grants,recommendations}.ts`: real local SDK fixture now advertises capability keys and uses published discount grants; expectations preserve unrelated underlying tool reuse and recommendation facts.
- `README.md`: migration behavior, outstanding prerequisite and operator rollout gate.

Implementation publication is explicitly authorized by the developer and recorded in Git / VCS below. The durable developer claim was pushed at `86b511c13`. Shared/default implementation and parent checkouts were not switched for execution; no gitlink or main update.

### Git / VCS

- Task branch in both repositories: `task/ARCH-059-BACKGROUND-001`.
- Canonical primary workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Dedicated parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-059-BACKGROUND-001`; dedicated implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-059-BACKGROUND-001`.
- Preparation synchronization/dependency/submodule steps completed before the report-format claim repair; no claim increment or startup synchronization was repeated for publication.
- Implementation baseline `efbbe0f`; implementation commit `0995635` published successfully to `origin/task/ARCH-059-BACKGROUND-001` on 5 November 2026, explicitly authorized by the developer. All 21 source/test/doc/dependency files are committed; staged scope and whitespace were checked.
- Parent durable claim `86b511c13`; this definition/report publication commit stages only this task file and is pushed to matching `origin/task/ARCH-059-BACKGROUND-001`. Its resulting SHA is reported to the developer after successful publication.
- Submodule gitlink staged: no. Shared checkouts switched/mutated for implementation: no. Another task worktree reused: no. Main merges/pushes, deployment and activation: none.

### Work Completed

- Removed conversation built-in descriptor/grant admission; new persistence requires a Shared-valid published projection and exact stored capability/tool/revision/definition metadata. Historical rows remain untouched and fail closed on the new path.
- Conversation and outreach share canonical published identities. Tools/list is checked against capability keys/input schemas; underlying model tool names route to an admitted published capability key. Legitimate capability description overrides and same-revision tool reuse remain valid.
- Outreach retains trusted INITIAL_RECOVERY_OUTREACH purpose, the explicit four-name allowlist, list-before-call, Shared input/output validation and existing call/search/detail budgets. The existing graph, deadline, eligibility/combinations algorithms and identifier-only model selection remain unchanged.
- Every production selector factory, including price reconciliation, current offer revalidation and product media, uses the existing checkout_recovery Feature admission before construction. No new Feature or billing rule/credit mutation introduced.
- Manifest/release/revision drift and revoked selections are checked before calls, and post-call drift discards a raced result. These are HOST checks only and are explicitly insufficient for the remaining server-enforced race gate below.
- Existing offer policy refresh, revalidation, moderation, human takeover, credit and delivery behavior remain unchanged. Task-focused existing behavior suites pass.

### Validation Results

Node 24.19.0 / npm 11.17.0 through canonical bootstrap; commands run in the isolated implementation worktree unless noted.

- `npm install --save-exact @modainteract/moda-interact-shared@5.1.0 --include=dev` — passed.
- `npm test -- tests/unit/commerce/published-tools.test.ts tests/unit/commerce/published-client.test.ts tests/unit/commerce/published-grants.test.ts tests/unit/services/recovery-offers/recovery-outreach-mcp-selector.service.test.ts tests/unit/services/recovery-offers/initial-outreach-offer-selection.service.test.ts tests/unit/services/recovery-offers/initial-outreach-agent-context.service.test.ts tests/unit/services/recovery-product-media/recovery-product-image-resolver.test.ts tests/unit/services/effective-billing-policy.service.test.ts` — 8 files / 64 tests passed. Evidence `/tmp/arch059-bg-focused-final.log`.
- `npm run test:commerce-recommendations` — 20 files / 197 tests passed, including eligibility, combinations, agent/graph, current offer revalidation, context/recommendation and template behaviors. Evidence `/tmp/arch059-bg-recommendations.log`.
- `npm run test:commerce-host` — 70 tests passed using local mocked HTTP/SDK/model fixtures, no live provider or production service. Evidence `/tmp/arch059-bg-host-last.log`. Earlier migrated fixture assertions were corrected, not waived.
- `npm run build` — passed, including declared Prisma generation and TypeScript compilation. No separate typecheck script exists; none invented. Evidence `/tmp/arch059-bg-build-last.log`.
- `npm run lint` — passed with no diagnostics. Evidence `/tmp/arch059-bg-lint-last.log`.
- `git -c core.fsmonitor=false diff --check` — passed; report also checked after writing.

Exploratory broad run: `npm run test:unit -- tests/unit/services/recovery-offers/recovery-outreach-mcp-selector.service.test.ts` runs the full tests/unit directory because the script already supplies that directory. It reported 3741 passed / 40 failed across 356 files: five new fixture constraint failures were subsequently fixed and the affected focused tests passed; 35 failures were outside task files. Evidence `/tmp/arch059-bg-unit-first.log`.

Controlled baseline comparison: extracted pre-task HEAD `efbbe0f` read-only into `/tmp/arch059-bg-pre-task`, reused identical installed dependencies, and ran `npm test -- <the 12 unchanged failing test file paths>` via subprocess (exact list `/tmp/arch059-bg-pre-task-files.json`). Baseline also reported 35 failed / 165 passed. Thirty-four broad-run failure identifiers matched; the remaining identity on each side was a different 5-second observability child-process timeout. Isolated `npm test -- tests/unit/runtime/observability-startup.test.ts` reruns on current and baseline both had 9 passed / 1 failed, only the inherited test hardcoding Shared 3.0.0 (pre-task package already pinned 5.0.0). No child-process timeout reproduced in isolation. Evidence `/tmp/arch059-bg-baseline.log`, `/tmp/arch059-bg-runtime-{current,baseline}.log`. Full suite is NOT claimed green. Historical ARCH025-BACKGROUND-TEST-001 does not describe this full current failure set; it was not used to waive new failures.

No Docker/PostgreSQL/Redis integration, live external provider, deployment, queue operation, release activation or grant migration was performed. Canonical setup provisioning/apply/retry behavior remains prerequisite Commerce evidence; this task does not claim to rerun it.

### Deviations

A narrow correction to task report blank-line formatting was necessary after the launcher wrote Attempt 1 but before it could publish the claim. The existing claim was completed and pushed once; no second attempt/claim was created. Preparation had already synchronized worktrees/submodules and passed dependency gates before the report-format stop.

The requested implementation cannot satisfy the complete pinning gate using Background changes alone. No contract was invented locally and no other implementation repository was edited. No acceptance criterion was weakened.

### Assumptions

Accepted Commerce provisions the explicit product_search mappings for active Free/paid plans and stages the complete release. Existing effective billing Feature selection remains authoritative for checkout_recovery; MCP remains authoritative for current published tool entitlement/provider access.

### Unresolved Issues

REQUIRED BEFORE REVIEW: trusted expected-call identity and positive enforcement support must be published by Shared, enforced by MCP and then consumed by this client. Current pre/post host checks cannot prove rejection before provider I/O if release activation races the request. Architect assessment and portable prerequisite handoff are recorded below. Current task remains developer In Progress; no review, completion or downstream promotion.

### Architectural Concerns

Architect assistance confirmed the concrete race against accepted MCP `519e905`: it selects the current release for tools/call and its registry compares against that request's snapshot, not Background's pinned attempt. Activation after the last Background manifest read but before MCP snapshot resolution can execute the new revision. Background may discard the result afterward, but this does not meet the normative before-provider-I/O requirement. Pause/drain is rollout mitigation, not enforcement evidence.

Portable architect definitions (defined, NOT materialised, not claimed/executed) are available at:

- `/tmp/arch059-background-prerequisites/SHARED-003-define-expected-published-call-identity.md`
- `/tmp/arch059-background-prerequisites/SHARED-004-publish-expected-published-call-identity.md`
- `/tmp/arch059-background-prerequisites/MCP-002-enforce-host-expected-published-call-identity.md`
- `/tmp/arch059-background-prerequisites/HANDOFF.md`

Sequence: accepted/completed SHARED-003 -> published/accepted/completed SHARED-004 -> accepted/completed MCP-002 -> architect reconciles current Background prerequisites and resumes THIS developer attempt. The new contract must carry the pinned release/capability/key/tool/revision/name through trusted context, with positive support advertisement because old MCP ignores extra context keys. Model arguments never supply that authority. Required resumption tests cover unchanged identity success, malformed/foreign identity, and both activation race windows with zero provider calls. Existing lifecycle/dependencies and architect review section were not edited by this assistance pass.

Retain controlled staged activation, pause/drain, unique-name/plan-parity verification and paired MCP/Background/pointer rollback. No deployment or activation is authorized by portable definitions or local source readiness.

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
