---
id: ARCH-064-MCP-001
architecture_id: ARCH-064
title: resolve pinned purpose profile subsets
task_kind: implementation
domain: mcp
repository: moda-interact-mcp
assigned_agent: moda_mcp
coordinator: moda_architect
execution_mode: agent
completion_mode: developer
status: ready
priority: 50
executor: null
claimed_at: null
attempt: 0
depends_on: ["ARCH-064-DATABASE-001", "ARCH-064-SHARED-002", "ARCH-064-COMMERCE-001", "ARCH-059-MCP-001"]
enables: ["ARCH-064-BACKGROUND-001", "ARCH-064-SYSTEM-TEST-001"]
created: 2026-11-06
updated: 2026-11-06
---
# Resolve pinned purpose profile subsets

## Architecture
ARCH-064; docs/architecture/ARCH-064-published-initial-outreach-profile.md. Coordinator moda_architect.

## Objective
Resolve pinned purpose profile subsets with immutable purpose selection, not global tool admission.

## Context
Background four-name Set, schema union and graph switches currently cap initial outreach independently of Studio publication. New profile references preserve existing capability ownership.

## Scope
moda-interact-mcp implementation and tests at verified touchpoints.

| Existing file | Exact surface | Required edit |
|---|---|---|
| moda-interact-mcp/src/capabilities/resolve.ts | resolveShopCapabilities | Resolve purpose subset after shop entitlement, return immutable profile/manifest. |
| moda-interact-mcp/src/mcp/authentication.ts | parseMcpRequestContext | Validate recognized trusted purpose, preserve private-ingress boundary. |
| moda-interact-mcp/src/mcp/registration.ts | registerCapabilityServer | List exactly eligible purpose members once. |
| moda-interact-mcp/src/mcp/execution.ts | executePublishedTool | Require pinned same-release purpose member at call and revalidate authorization. |


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
- [ ] Resolve purpose subset after shop entitlement, return immutable profile/manifest.
- [ ] Validate recognized trusted purpose, preserve private-ingress boundary.
- [ ] List exactly eligible purpose members once.
- [ ] Require pinned same-release purpose member at call and revalidate authorization.

## Interfaces / Contracts
Exact purpose profile/membership/behavior schemas and draft/release join models above; Shared publication prerequisite gates consumers. Initial Outreach is governance Feature, checkout_recovery remains admission, referenced owner-feature eligibility remains required.

## Dependencies
- ARCH-064-DATABASE-001
- ARCH-064-SHARED-002
- ARCH-064-COMMERCE-001
- ARCH-059-MCP-001

## Enables
- ARCH-064-BACKGROUND-001
- ARCH-064-SYSTEM-TEST-001

## Acceptance Criteria
- [ ] Fifth implemented read tool can be listed/called only when published purpose member and entitled; missing/forged/stale purpose rejects before I/O.

## Validation
- [ ] Run declared focused owner tests for each task assertion; add deterministic unit/integration fixtures for same-release/tenant/role/purpose/immutability constraints and the supported fifth-tool case.
- [ ] Run declared typecheck/build appropriate to owner (Database schema/migration/constraint tests; Background build; System Test harness/syntax instead of app build). Record exact commands/results and no secrets in diagnostics.

## Stop Condition
Submit completed scoped report for authorized review and STOP. Explicit developer completion required. No enabled follow-on task auto-start; terminal System Test manually invoked after accepted dependencies.

## Implementation Notes
Execution ownership amendment (2026-11-06): developer explicitly requested `/moda-task ARCH-064-MCP-001` implementation and authorized sync plus task claim/source/review publication. Delegate to moda_mcp via canonical preparation, preserving completion_mode developer and private trusted purpose/authorization scope. No live deployment, main merge or downstream execution.

Dependency reconciliation (2026-11-06): canonical DATABASE001, SHARED002 and ARCH059-MCP001 Complete; Commerce001 Attempt2 explicitly completed after real-default/fifth-tool validation. Task Ready at unchanged Attempt0, unclaimed. Consume corrected published Shared5.5.0 canonical purpose compiler/profile semantics, not obsolete Details-only assumption. No automatic execution.

No execution from definition. Use normal launcher-isolated/synchronized task worktrees when requested. Exact architecture choices above are binding; report demonstrated incompatibility instead of selecting new schema/identity/authorization design. Preserve historical task status and unrelated edits.

## Completion Report
### Status
Not Started
### Files Changed
None
### Work Completed
None
### Validation Results
Definition only.
### Deviations
None
### Assumptions
Existing publication and supported read operation registry remain canonical.
### Unresolved Issues
None blocking definition.
### Architectural Concerns
Do not widen permissions or generic result evidence authority.

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
