---
id: ARCH-064-SHARED-001
architecture_id: ARCH-064
title: define published purpose profile contract
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: complete
priority: 50
executor: null
claimed_at: null
attempt: 1
depends_on: []
enables: ["ARCH-064-SHARED-002"]
created: 2026-11-06
updated: 2026-11-06
---
# Define published purpose profile contract

## Architecture
ARCH-064; docs/architecture/ARCH-064-published-initial-outreach-profile.md. Coordinator moda_architect.

## Objective
Define published purpose profile contract with immutable purpose selection, not global tool admission.

## Context
Background four-name Set, schema union and graph switches currently cap initial outreach independently of Studio publication. New profile references preserve existing capability ownership.

## Scope
moda-interact-shared implementation and tests at verified touchpoints.

| Existing file | Exact surface | Required edit |
|---|---|---|
| moda-interact-shared/src/commerce/definitions.ts | manifest/grant schemas | Add exact purpose/profile schema and optional backward-readable manifest field; new outreach requires present profile. |
| moda-interact-shared/src/commerce/runner/graph/nodes/resolve-available-tools.ts | available-tool resolution | Use profile subset schemas/identity, no static name ceiling for supported read tools. |


## Out of Scope
Duplicate Product Search capabilities/tools, merchant entitlement changes, arbitrary/mutating runtime installation from UI, discount evaluator redesign, unsafe all-tools admission, new ingress or auto execution.

## Requirements
## Decision and representation
Create Feature key `initial_outreach`, display name **Initial Outreach**, as the Super Admin-only Studio administration surface for trusted behavior and purpose membership. It is a governance/purpose Feature, not a new merchant purchase or an independent outreach entitlement. Existing `checkout_recovery` entitlement, consent/admission and moderation remain mandatory. Feature activation ALWAYS_ENABLED/systemRequired establishes system identity only; it does NOT grant capability access or replace existing member owner-feature/plan checks. Non-Super-Admin list/detail/actions hide/deny this Feature. No new plan mapping or merchant toggle is created.

CommerceCapability.featureId remains its existing single owning Feature. The four existing Product Search-owned capabilities/tools are NEVER cloned, reassigned or given alternate tool names. Reuse canonical Tool, Revision and Capability IDs. Add draft membership model `CommercePurposeCapability` in commerce schema with purposeFeatureId FK Feature, capabilityId FK CommerceCapability, position integer>=0, primary key [purposeFeatureId,capabilityId], unique [purposeFeatureId,position]. `CommerceFeatureConfiguration` already stores editable behaviorPrompt/editVersion for initial_outreach; reuse it and existing operation/audit machinery. Existing release feature snapshot `CommerceReleaseFeature` stores immutable initial_outreach behavior. Add `CommerceReleasePurposeCapability` with releaseId,purposeFeatureId,capabilityId,position, PK [releaseId,purposeFeatureId,capabilityId], unique [releaseId,purposeFeatureId,position]; composite FK [releaseId,purposeFeatureId] -> CommerceReleaseFeature and [releaseId,capabilityId] -> CommerceReleaseCapability. Thus a purpose member can only reference a member of SAME complete immutable release; revision identity derives that member, never a mutable draft lookup. Add explicit checks/indexes, Restrict relationships and existing immutable release guard coverage. No second copied definition/result schema on purpose rows.

Draft membership mutations require SUPER_ADMIN, reason, operationId, expected purpose feature editVersion and existing audit/idempotency; increment same feature config version atomically with membership/behavior updates. Feature's ordinary create-capability workflow must be replaced for Initial Outreach with **Attach existing capability**, reorder and remove controls. Do not accidentally create owned duplicate capabilities under it. Ordinary Feature authoring remains unchanged. Profile editor allows only already implemented read-only operations/revisions passing normal publication validation. Unsupported operation/new transport or result schema requires owning code/contracts first, not merely Studio config.

## Publication and defaults
Setup provisions initial_outreach Feature/config and draft references in this order ONLY on first seed: commerce_get_discount_options, commerce_get_discount_details, commerce_search_products, commerce_get_product. Keys are migration/seed defaults, not runtime allowlist, required ceiling or hidden reset-on-apply policy. Seed behavior from the existing initial-outreach trusted instructions, preserving host invariants below. Repeated setup preserves Super Admin membership/behavior edits, no automatic reattachment of removed keys. First seed requires referenced canonical capabilities exist; otherwise explicit conflict without partial activation. Default profile includes current behavior but future updates may remove/add supported read capabilities through Studio.

Complete release publishing snapshots initial_outreach behavior AND ordered purpose links referencing already selected release members, validated output/input schemas, read-only support and immutable revision IDs. New configuration does not affect running attempts until a new release is published/activated. Draft save is not a grant. An empty profile can be saved for editing but publication rejects empty initial_outreach profile with explicit PROFILE_EMPTY; no four-key count requirement. Removing a discount tool is allowed configuration: runtime follows existing no-verified-offer/unavailable safe behavior, no hidden automatic tool restoration. Rollback reactivates previous immutable release/purpose snapshot; never rewrite old releases. Missing purpose snapshot under new runtime fails closed, no hardcoded fallback. Old releases remain readable by old compatible runtime only during staged rollout.

## Exact trusted runtime contract
Shared exports `CommerceExecutionPurposeSchema` with value INITIAL_RECOVERY_OUTREACH and `CommercePurposeProfileSchema` under existing commerce entrypoint. Profile `{purpose:'INITIAL_RECOVERY_OUTREACH',featureId:string,releaseId:string,behaviourPrompt:string,capabilities:Array<{capabilityId:string,toolId:string,revisionId:string,name:string,position:number,inputSchema:InputSchemaSchema,outputSchema:DetailsSchemaSchema}>}`; frozen max profile 32 members, names unique, positions strictly increasing nonnegative, behavior <=32768 UTF-8 bytes, schema/result size governed existing subset limits. Full manifest/grant binding includes profile purpose, behavior and exact ordered capability identities within immutable release. Extend existing canonical manifest/grant validation rather than local signatures/hashes; no additional contractHash mechanism.

MCP recognizes trusted purpose from private context; untrusted user/model/tool text cannot set it. Purpose resolution first requires shop/platform/active release and ordinary owner-feature/plan/provider eligibility; then intersects same-release purpose references. Return only intersection to outreach, never entire shop MCP list. Include profile snapshot in trusted MCP manifest/projection, not arbitrary user args. List and call enforce same release/purpose/capability/revision; call-time revocation/current shop permission revalidation remains authoritative. Missing/wrong/duplicate profile, forged capability or purpose -> existing bounded denied/unavailable before provider I/O. Generic conversation snapshots do not automatically get Initial Outreach behavior or new tools. Existing MCP auth remains private ingress; no public endpoint expansion.

Background selector removes OUTREACH_MCP_TOOL_NAMES, ALLOWED_TOOLS, four-name union casts and name-indexed schema existence ceiling. `tools()` receives pinned validated profile and admits only its exact capabilities intersected by MCP; duplicate/unknown/mismatched identities reject. Validate mapped input and result against published bounded subset schemas. Use established Shared schema validators/compiler, never dynamic eval/unbounded JSON schema. Model schema/instructions derive selected profile; call budget stays 16, max steps8, deadline45s, result32KiB and messages128KiB, existing product search3/detail5 semantic counters remain for those known product operations. New supported read tool counts toward global16, not a new unlimited budget. SDK/model receives only current authorized tools.

Initial outreach graph cannot keep its default switch throwing for every non-four-name tool. Preserve typed semantic projection/eligibility for known discount/product observations. Add generic read-observation branch for any OTHER profile-admitted implemented read operation: bounded validated structured result to model, no new host discount/product evidence, no promotion/savings/URL authority from that result. Generic result may inform language/context only; it cannot unlock unsupported selection IDs or clear mandatory referral/invalid states. Existing final identifier-only offer choice, verified discount evaluator/combinations and same-turn/current-offer revalidation remain unchanged. Code-owned safety instructions (consent, no invented offers, final-response contract, deadline/budget) remain host-authoritative and cannot be overridden by editable behavior. Compose host invariants first, then trusted published behavior, then untrusted merchant/model content separated as data. Adding genuinely new evidence semantics or a new operation still needs code; adding an already supported read tool to profile does not.

## Deterministic acceptance and rollout
SUPER_ADMIN edits membership and behavior, publishes/activates release, then new attempts use new profile while an existing attempt remains pinned until completion/cancellation. ADMIN direct URL/server action and forged principal cannot read/write initial_outreach profile. Product Search IDs/ownership and conversation tool behavior unchanged. Add an already supported fifth read tool via Studio -> release -> MCP -> outreach: listed/called with bounded generic result, without changing Background name constants; remove it -> absent next release; stale/forged call denied. Default four-key seed idempotent and never resets edits. Unsupported/mutating tool publication rejected. Missing discount member produces safe no-offer behavior, not fabricated evidence. Cross-tenant membership/call/permission revocation and malformed oversized output fail closed.

Compatible staged rollout: Database additive migration, Shared accepted implementation then publication; Commerce UI/seed/staged complete release (do not activate against old consumer), MCP support, Background consumer after existing ARCH-059 Background adoption; operator pauses affected attempts and drains pinned legacy sessions via separately recorded operational procedure, activates complete profile release and resumes only after smoke verification. No procedure or deployment is claimed executed by these definitions. New runtime with missing profile fails closed. Previous runtime/release pairing is rollback unit; do not restore hardcoded fallback in new code. No schema destruction, queue deletion, new ingress/topology/secret requirement. No Gateway task identified. Reuse existing structured lifecycle diagnostics with release/purpose/capability IDs, no secrets or raw prompts/customer payloads. Terminal System Test after accepted dependencies and optional user exercise. No implementation auto-launch.

## Work Items
- [x] Add exact purpose/profile schema and optional backward-readable manifest field; new outreach requires present profile.
- [x] Use profile subset schemas/identity, no static name ceiling for supported read tools.

## Interfaces / Contracts
Exact purpose profile/membership/behavior schemas and draft/release join models above; Shared publication prerequisite gates consumers. Initial Outreach is governance Feature, checkout_recovery remains admission, referenced owner-feature eligibility remains required.

## Dependencies
None

## Enables
- ARCH-064-SHARED-002

## Acceptance Criteria
- [x] Profiles validate purpose, ordered same-release identities, safe input/output schemas and bounds; old conversation payloads remain compatible.

## Validation
- [x] Run declared focused owner tests for each task assertion; add deterministic unit/integration fixtures for same-release/tenant/role/purpose/immutability constraints and the supported fifth-tool case.
- [x] Run declared typecheck/build appropriate to owner (Database schema/migration/constraint tests; Background build; System Test harness/syntax instead of app build). Record exact commands/results and no secrets in diagnostics.

## Stop Condition
Submit completed scoped report for authorized review and STOP. Explicit developer completion required. No enabled follow-on task auto-start; terminal System Test manually invoked after accepted dependencies.

## Implementation Notes
No execution from definition. Use normal launcher-isolated/synchronized task worktrees when requested. Exact architecture choices above are binding; report demonstrated incompatibility instead of selecting new schema/identity/authorization design. Preserve historical task status and unrelated edits.

## Completion Report

### Status

Complete — Attempt 1 explicitly developer-completed on 2026-11-06.

### Files Changed
src/commerce/definitions.ts; src/commerce/schemas.ts; src/commerce/selection.ts; src/commerce/runner/types.ts; src/commerce/runner/preflight.ts; src/commerce/runner/tool-policy.ts; src/commerce/runner/tool-execution.ts; src/commerce/purpose-profile.test.ts.

### Work Completed
Exported execution-purpose/profile schemas and types: 1–32 members, unique names/capabilities, strictly increasing nonnegative positions, 32768 UTF-8 byte behavior limit, explicit PROFILE_EMPTY, bounded subset schemas and deeply frozen parsed snapshots. Optional purposeProfile preserves legacy manifest/grant parsing; canonical full-profile comparison binds purpose, behavior, ordered IDs and schemas. Manifest validates same-release capability/tool/revision/name/input identities.

Trusted runner executionPurpose requires matching outreach profile and fails closed when missing. Generic conversations remain unchanged. Preflight composes profile behavior after host invariants only for explicit trusted purpose. Existing graph resolver delegates to tool-policy; changed that actual policy rather than duplicating logic in the graph node. It intersects existing authorized registered tools with profile members, retains published position order, checks membership again at call time and validates successful output against profile subset schema. A fifth registered read-tool fixture executes without adding a tool-name ceiling; removal denies subsequent call.

### Validation Results
- `npm run typecheck`: passed.
- `npx tsx --test src/commerce/purpose-profile.test.ts src/commerce/selection.test.ts src/commerce/runner/runner.test.ts`: 63 passed.
- `npm run build`: ESM and declarations passed.
- `npm run validate:commerce-entrypoints`: passed.
- `git diff --check`: passed.
Tests cover profile bounds/order/deep immutability, malformed schemas/output, same-release identities, full behavior binding, fifth tool, member removal, grant-order independence, missing-profile denial and legacy compatibility. Tenant/role/database constraints belong to downstream owners; no cross-service integration or deployed execution is claimed here.

### Deviations / Assistance
Material moda_shared assistance implemented source/tests under explicit developer authorization; root retained lifecycle/publication. Launcher prepared/synchronized worktrees and set developer Attempt 1 before report-format validation failed; normalized report and published claim f7ddfa682 without another claim/increment. Supporting canonical schemas/selection and delegated runner policy/preflight/execution/types were necessary to bind/enforce the contract; no consumer repository edits.

### Boundaries / Unresolved Issues
Existing descriptors have no output-schema/read-only metadata: bounded output schema is canonically bound in profile/grant and runtime-validated; publication producers own authoritative compiled output and read-only eligibility. Membership never registers a tool or bypasses existing authorization. Generic budgets and existing 262144-byte result envelope remain unchanged; Background owns stricter outreach budgets. No extra hash mechanism, schema, dependency or package-version change. Package remains 5.3.0; SHARED-002 must publish the new contract before consumers pin it. No blocking scoped implementation issues.

### Git / VCS
Task branch: task/ARCH-064-SHARED-001.
Canonical workspace root: /Users/kwadwoadomafriyie/project/moda-interact-workspace.
Parent worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-064-SHARED-001.
Implementation worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-064-SHARED-001.
Both worktrees use task/ARCH-064-SHARED-001, prepared/synchronized by launcher before Attempt 1. Shared/default checkouts were not switched for task implementation; no other task worktree reused.
Implementation d478b057942da3185713eb348f48d5205b773539 pushed to origin/task/ARCH-064-SHARED-001.
Parent claim f7ddfa682 pushed; this report is committed/pushed on matching parent task branch, exact report commit available in Git history.
Submodule gitlink staged: no. Main merged/pushed: no. Package published: no.

## Developer Self-Review - Passed
Attempt 1 scoped Shared contract and enforcement pass focused tests, declared typecheck/build and entrypoint validation. Existing authorization and generic compatibility remain; rollout/publication stays gated on follow-on tasks. Explicit `/moda_developer_update ARCH-064-SHARED-001 complete` is pending.

## Architect Review
### Review Status
Pending
### Review Notes
Definition inspected against single-owner schema, role model and selector/graph code; no implementation reviewed.
### Reviewed Files
Verified touchpoints above.
### Validation Reviewed
Metadata/dependency/path checks only.
### Architecture Conformance
Single owning repository; shared contract publication separated; terminal integrated test.
### Follow-up
None


## Purpose publication authority and underlying tool edits
Any release containing initial_outreach behavior/purpose members requires SUPER_ADMIN at publish AND activate/rollback, checked server-side in lifecycle services, not only Feature editor. Global ADMIN may retain existing rights to edit unrelated/shared tool drafts, but cannot publish/activate a new outreach snapshot or repoint its revisions through another Feature workflow. Existing immutable release references mean editing a draft never changes active outreach. Super Admin publication reviews selected exact revision IDs and behavior as one complete snapshot; ordinary release services cannot silently copy/advance outreach members to latest revisions. For a release that preserves outreach unchanged, activation still requires SUPER_ADMIN because the pointer controls this purpose. No bypass via setup command, generic release action, development role field or forged client role. Existing authenticated development bypass policy remains explicit and may not impersonate SUPER_ADMIN for production mutations. Add ADMIN direct lifecycle publish/activate/rollback tests plus underlying draft edit test proving active pinned profile unchanged. Keep existing audit reason/actor/operationId and immutable snapshot evidence; no new permission granted to arbitrary tools.

## Developer Completion Decision
2026-11-06: Developer explicitly invoked `/moda_developer_update ARCH-064-SHARED-001 complete`. Accepted Attempt 1 unchanged; executor and claimed_at remain null. Passing self-review is durable in parent 180aced326f83a19a8b4dff1c616c346101b87e4. Implementation d478b057942da3185713eb348f48d5205b773539 matches origin/task/ARCH-064-SHARED-001; both canonical worktrees clean at verification. Required scoped work and validation satisfied. Neither main branch merged/pushed; package publication remains separate.

### Dependency-frontier reconciliation
ARCH-064-SHARED-002 has only SHARED-001 as explicit dependency and becomes Ready, unchanged Attempt 0, executor/claimed_at null. No claim or automatic execution. Commerce/MCP/Background remain gated by publication and their other dependencies; terminal System Test remains Pending/manual-gated.
