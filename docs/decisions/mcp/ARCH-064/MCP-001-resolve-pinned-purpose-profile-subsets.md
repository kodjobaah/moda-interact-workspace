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
status: review
priority: 50
executor: null
claimed_at: null
attempt: 1
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
- [x] Resolve purpose subset after shop entitlement, return immutable profile/manifest.
- [x] Validate recognized trusted purpose, preserve private-ingress boundary.
- [x] List exactly eligible purpose members once.
- [x] Require pinned same-release purpose member at call and revalidate authorization.

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
- [x] Fifth implemented read tool can be listed/called only when published purpose member and entitled; missing/forged/stale purpose rejects before I/O.

## Validation
- [x] Run declared focused owner tests for each task assertion; add deterministic unit/integration fixtures for same-release/tenant/role/purpose/immutability constraints and the supported fifth-tool case.
- [x] Run declared typecheck/build appropriate to owner (Database schema/migration/constraint tests; Background build; System Test harness/syntax instead of app build). Record exact commands/results and no secrets in diagnostics.

## Stop Condition
Submit completed scoped report for authorized review and STOP. Explicit developer completion required. No enabled follow-on task auto-start; terminal System Test manually invoked after accepted dependencies.

## Implementation Notes
Execution ownership amendment (2026-11-06): developer explicitly requested `/moda-task ARCH-064-MCP-001` implementation and authorized sync plus task claim/source/review publication. Delegate to moda_mcp via canonical preparation, preserving completion_mode developer and private trusted purpose/authorization scope. No live deployment, main merge or downstream execution.

Dependency reconciliation (2026-11-06): canonical DATABASE001, SHARED002 and ARCH059-MCP001 Complete; Commerce001 Attempt2 explicitly completed after real-default/fifth-tool validation. Task Ready at unchanged Attempt0, unclaimed. Consume corrected published Shared5.5.0 canonical purpose compiler/profile semantics, not obsolete Details-only assumption. No automatic execution.

No execution from definition. Use normal launcher-isolated/synchronized task worktrees when requested. Exact architecture choices above are binding; report demonstrated incompatibility instead of selecting new schema/identity/authorization design. Preserve historical task status and unrelated edits.

## Completion Report
### Status
Ready for Review
### Files Changed
- package.json/package-lock.json: exact published Shared5.5.0.
- database gitlink: architect-approved accepted379d563f6b9ee070305e284615dddbc0b97afeb0 schema dependency.
- src/capabilities/{records,prisma-reader,resolve,manifest,purpose}.ts.
- src/mcp/{ports,authentication,service,snapshot,execution}.ts.
- src/runtime/{execution-registry,service-ports}.ts.
- tests/unit/capabilities/{purpose,prisma-reader}.test.ts; README.md trusted context contract.
### Work Completed
Trusted private header recognizes Shared INITIAL_RECOVERY_OUTREACH; model/tool arguments and opaque toolContext cannot select purpose. Discovery validates complete immutable same-release membership, governance identity and canonical output schemas before intersecting current shop/platform/owner-feature/plan/provider eligibility plus existing checkout_recovery admission. Purpose names use immutable revision Tool names, generic capability aliases remain unchanged. Canonical frozen profile is included only in purpose manifest, no generic behaviour leakage.

Purpose tools/call require caller's discovered releaseId in existing trusted header (Shared IdSchema); no new hash/signature or large schema header. Missing/stale pin denies before provider I/O. Execution registry re-reads permissions/release and compares exact profile/capability/tool/revision/descriptor identities; revocation/foreign/forged/missing/duplicate identities fail closed. Published Shared compiler validates policy data or canonical GraphQL mapped {values}; provider facts envelope stays separate unchanged. Existing generic discount-release guard does not restore removed discount profile members.

Prisma reader uses actual accepted CommerceReleaseFeature.purposeMembers relation (not nonexistent direct Release relation), flattened into read projection with generated Prisma.CommerceReleaseInclude typing. Generic entitlement query unchanged; purpose additionally reads checkout_recovery plan/preference metadata. Policy output schema metadata derives operation/version and existing canonical validators (custom revision names supported), lossless nullable/enum spelling only; no competing runtime validator or four-name admission ceiling.
### Validation Results
- Published dependency install5.5.0 PASS; audit18 existing issues(12 moderate,6 high), no unrelated fixes.
- Initial focused26/26 PASS, then final purpose9/9 PASS including real production GraphQL fifth adapter with typed mocked connection, separate HTTP discovery/call pin, cross-shop/revocation/active-release change denial, default four descriptors with custom names, malformed/oversized results, governance/owner/recovery gates and generic isolation.
- Declared npm run test:unit initial408/410 PASS; two failures were missing ignored pinned Admin schema artifact (ENOENT) in fresh worktree, no source failure. Installed exact local Commerce artifact through repository scripts/install-shopify-admin-schema.mjs, which verifies pinned SHA256; no schema download/version change/provider call.
- Final targeted command node --import tsx --test tests/unit/capabilities/purpose.test.ts tests/unit/capabilities/prisma-reader.test.ts tests/unit/execution/policy/product-search-composition.test.ts tests/unit/execution/policy/shipping-information-composition.test.ts: PASS46/46, including both prior artifact failures and new generated-query proof. Other408 prior unit successes preserved, no unrelated source changes.
- npm run typecheck: PASS (Prisma generation + TypeScript).
- npm run build: PASS (Prisma generation + production TypeScript).
- npm run lint: PASS zero warnings; git diff --check PASS.
- No long Docker/live validation launched; fixtures use mocked persistence/provider connection with real protocol/registry/GraphQL executor/Shared schemas, no live provider calls.
### Deviations
Architect-approved private context releaseId pin avoids full profile exceeding8KiB header; immutable release identifies exact snapshot, internal profile comparison retained. Startup databasebd2d090 lacked accepted purpose joins; intentionally pinned accepted379d563 in implementation only and regenerated client, no schema edits/live migration. Service-owned policy metadata normalization reuses existing Shared output validators and compiler; no schema fork. Generic context/discovery remains compatible.
### Assumptions
Private ingress authenticates caller before trusted header parsing; no public exposure/cutover changed. Active release change rejects stale pinned calls instead of silently adopting new profile; caller can cancel/re-resolve under owning Background orchestration.
### Unresolved Issues
None in scoped MCP implementation.
### Architectural Concerns
Reported separate upstream Commerce persistence query mismatch to moda_architect: accepted Commerce publication-storage.ts readState queries CommerceRelease.purposeMemberships, but accepted database379d563 exposes links through Feature snapshot.purposeMembers/Capability.purposeMemberships only. MCP uses correct nested relation with generated type proof; no Commerce edit performed. Architect will track owning correction (ARCH-064-COMMERCE-002). No inter-service deployment success claimed.
### Git / VCS
Task branch task/ARCH-064-MCP-001.
Physical isolation from launcher:
- canonical root /Users/kwadwoadomafriyie/project/moda-interact-workspace
- parent /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-064-MCP-001
- implementation /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-064-MCP-001
- parent/implementation branch task/ARCH-064-MCP-001
- shared/default checkout switched/mutated no; other task path reused no.
Start synchronization: parent/implementation remote task fast-forward not-needed; origin/main already-current. Recursive submodule sync/update passed; original recorded databasebd2d09066a8eb178a56f48fbbf88df637c411059 ready. Intentional accepted dependency pin379d563 recorded above, not startup drift.
Attempt1 claim4b97cd1f5dc79616d4fb96a52116950be135237f pushed.
Implementation4963baa915295a3deec2b470b73d7f61247d2f53 pushed/remote verified, clean. Parent task-only report commit follows this edit; architect coordination staged separately and not included. Parent implementation gitlink staged no. Main merges no; live migration/activation/cutover no; follow-on execution no.

## Architect Review
### Review Status
Accepted — explicit developer completion pending.
### Review Notes
Inspected actual4963baa915295a3deec2b470b73d7f61247d2f53 implementation/reportc66e0b09df40d9052b47e71fe9f9a410956fb908. Trusted private purpose is recognized by Shared schema; stateless purpose calls require existing Shared-validated pinned releaseId, preventing fresh active snapshot from accepting stale calls. Immutable same-release whole profile validates before entitlement intersection; ordinary owner-feature/plan/provider and checkout_recovery admission preserved. Governance Feature identity never grants tools. Purpose-facing names match immutable revision/profile while generic aliases unchanged. Calls re-read permissions/release and compare exact identities/profile before provider I/O. Canonical Shared5.5 output compiler validates mapped GraphQL values separately from transport facts; no name ceiling or local validator fork.
### Reviewed Files
Capability purpose/resolver/manifest/Prisma reader/records; authentication/service/snapshot/execution ports; runtime registry/service adapter; focused purpose protocol/query-shape tests and README; package/lock and accepted nested database pin.
### Validation Reviewed
Final46 targeted fixtures passed, including real production GraphQL fifth executor, separate HTTP list/call pin/missing/stale/cross-shop/revoked denial, actual four default custom-name descriptors and generated Prisma.CommerceReleaseInclude proof. Declared typecheck/build/lint/diff checks passed. Earlier full unit408/410 had two missing ignored schema-artifact ENOENT cases; exact pinned hash-verifying installer applied and both cases rerun/pass within final46. No live provider/database mutation. Read actual nested feature.purposeMembers projection against accepted generated schema.
### Architecture Conformance
Scoped MCP contract conforms. Dependency pin accepted database379d563 and Shared5.5; parent workspace gitlink untouched. Service policy metadata projection derives schemas, runtime validation remains canonical Shared. Canonical isolation/start synchronization/durable mirrored publication verified. No main/live migration/activation/downstream implementation.

Residual cross-repository issue: accepted Commerce publication-storage.ts:108 uses nonexistent direct release.purposeMemberships; actual DB exposes nested ReleaseFeature.purposeMembers. ARCH-064-COMMERCE-002 Ready correction defined, System Test explicitly depends on it. MCP owns/fixes only its own typed reader. Acceptance here does not claim integrated runtime/deployment complete.
### Follow-up
Explicit completion: `/moda_developer_update ARCH-064-MCP-001 complete`. Commerce002 remains Ready for separately authorized execution. Background/System Test remain gated until their required dependencies Complete; no automatic follow-on work.


## Purpose publication authority and underlying tool edits
Any release containing initial_outreach behavior/purpose members requires SUPER_ADMIN at publish AND activate/rollback, checked server-side in lifecycle services, not only Feature editor. Global ADMIN may retain existing rights to edit unrelated/shared tool drafts, but cannot publish/activate a new outreach snapshot or repoint its revisions through another Feature workflow. Existing immutable release references mean editing a draft never changes active outreach. Super Admin publication reviews selected exact revision IDs and behavior as one complete snapshot; ordinary release services cannot silently copy/advance outreach members to latest revisions. For a release that preserves outreach unchanged, activation still requires SUPER_ADMIN because the pointer controls this purpose. No bypass via setup command, generic release action, development role field or forged client role. Existing authenticated development bypass policy remains explicit and may not impersonate SUPER_ADMIN for production mutations. Add ADMIN direct lifecycle publish/activate/rollback tests plus underlying draft edit test proving active pinned profile unchanged. Keep existing audit reason/actor/operationId and immutable snapshot evidence; no new permission granted to arbitrary tools.
