---
id: ARCH-064-COMMERCE-001
architecture_id: ARCH-064
title: author superadmin initial outreach profile
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: developer
status: review
priority: 50
executor: codex
claimed_at: 2026-11-06T20:48:20Z
attempt: 2
depends_on: ["ARCH-064-DATABASE-001", "ARCH-064-SHARED-002", "ARCH-059-COMMERCE-001", "ARCH-064-SHARED-004"]
enables: ["ARCH-064-MCP-001", "ARCH-064-BACKGROUND-001", "ARCH-064-SYSTEM-TEST-001"]
created: 2026-11-06
updated: 2026-11-06
---
# Author superadmin initial outreach profile

## Architecture
ARCH-064; docs/architecture/ARCH-064-published-initial-outreach-profile.md. Coordinator moda_architect.

## Objective
Author superadmin initial outreach profile with immutable purpose selection, not global tool admission.

## Context
Background four-name Set, schema union and graph switches currently cap initial outreach independently of Studio publication. New profile references preserve existing capability ownership.

## Scope
moda-interact-commerce implementation and tests at verified touchpoints.

| Existing file | Exact surface | Required edit |
|---|---|---|
| moda-interact-commerce/src/studio/features/services.ts | feature read/mutation authorization | Hide/deny initial_outreach for ADMIN; SUPER_ADMIN only membership and behavior services with expected versions. |
| moda-interact-commerce/src/studio/features/persistence.ts | feature persistence | Implement draft reference joins, atomic version/audit/idempotency; no duplicate Tool/Capability. |
| moda-interact-commerce/src/studio/features/feature-configuration-screen.tsx | Feature editor | Show Initial Outreach behavior and Attach existing capability/reorder/remove controls. |
| moda-interact-commerce/src/commerce/publication/lifecycle.ts | CommerceLifecycle | Snapshot behavior/purpose joins with validated same-release members; immutable staged publish/activation. |
| moda-interact-commerce/src/commerce/bootstrap/system-commerce-tool-sync.ts | system setup | Seed first profile only with existing four references; preserve later edits. |


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
- [x] Hide/deny initial_outreach for ADMIN; SUPER_ADMIN only membership and behavior services with expected versions.
- [x] Implement draft reference joins, atomic version/audit/idempotency; no duplicate Tool/Capability.
- [x] Show Initial Outreach behavior and Attach existing capability/reorder/remove controls.
- [x] Snapshot behavior/purpose joins with validated same-release members; immutable staged publish/activation.
- [x] Seed first profile only with existing four references; preserve later edits.

## Interfaces / Contracts
Exact purpose profile/membership/behavior schemas and draft/release join models above; Shared publication prerequisite gates consumers. Initial Outreach is governance Feature, checkout_recovery remains admission, referenced owner-feature eligibility remains required.

## Dependencies
- ARCH-064-DATABASE-001
- ARCH-064-SHARED-002
- ARCH-059-COMMERCE-001

## Enables
- ARCH-064-MCP-001
- ARCH-064-BACKGROUND-001
- ARCH-064-SYSTEM-TEST-001

## Acceptance Criteria
- [x] SUPER_ADMIN fifth supported read tool addition/removal visible in published snapshot; ADMIN list/detail/direct-action denied.
- [x] Default seed repeats no changes, owns no cloned capabilities; unsupported/mutating tool/empty profile publication rejected.

## Validation
- [x] Run declared focused owner tests for each task assertion; add deterministic unit/integration fixtures for same-release/tenant/role/purpose/immutability constraints and the supported fifth-tool case.
- [x] Run declared typecheck/build appropriate to owner (Database schema/migration/constraint tests; Background build; System Test harness/syntax instead of app build). Record exact commands/results and no secrets in diagnostics.

## Stop Condition
Submit completed scoped report for authorized review and STOP. Explicit developer completion required. No enabled follow-on task auto-start; terminal System Test manually invoked after accepted dependencies.

## Implementation Notes
Execution ownership amendment (2026-11-06): developer explicitly requested `/moda-task ARCH-064-COMMERCE-001` implementation and authorized sync plus task claim/source/review publication. Delegate to moda_commerce via canonical preparation, preserving completion_mode developer and exact authoring/publication/seed scope. No live migration, consumer deployment, main merge or enabled execution.

Dependency reconciliation (2026-11-06): canonical routes confirm ARCH-064-DATABASE-001 and ARCH-059-COMMERCE-001 Complete; ARCH-064-SHARED-002 explicitly completed with verified published 5.4.0 purpose contract. All explicit dependencies satisfied; Ready at unchanged Attempt 0, unclaimed. No automatic execution.

No execution from definition. Use normal launcher-isolated/synchronized task worktrees when requested. Exact architecture choices above are binding; report demonstrated incompatibility instead of selecting new schema/identity/authorization design. Preserve historical task status and unrelated edits.

## Completion Report
### Status
Ready for Review — Attempt2 correction complete; explicit developer completion remains required.
### Files Changed
Attempt2 only: package.json/package-lock.json (published Shared5.5.0), src/commerce/publication/purpose-profile.ts, tests/initial-outreach-publication.test.ts. Prior validated authoring/UI/seed/lifecycle work retained unchanged.
### Work Completed
Adopted corrected published Shared5.5.0 and canonical compileCommercePurposeOutputSchema in the existing read-only admission/publication helper. Complete producer schemas retained without projection or local widening. Existing canonical profile schema now validates real default four descriptors. Real seed invokes production first-only seeding, feeds canonical IDs/order/behavior to lifecycle publication, validates full nonempty discount options/details and product search/get values through both canonical purpose compiler and unchanged CommerceToolOutputs. Actual supported compiled read-only GraphQL fifth is added/removed in subsequent immutable releases. Role, direct lifecycle, immutable old snapshot, empty/unsupported/mutating rejection and seed edit preservation remain enforced.
### Validation Results
- Published `@modainteract/moda-interact-shared@5.5.0` installed exact registry/integrity lock; only one dependency changed. Existing peer/audit warnings unchanged; no unrelated dependency work.
- `node node_modules/vitest/vitest.mjs run tests/initial-outreach-publication.test.ts tests/commerce-lifecycle.test.ts tests/publication-storage-release-delta.test.ts`: PASS 3 files/39 tests, zero skips/failures. Real seeded default profile + complete output values and fifth read add/remove included.
- `node node_modules/vitest/vitest.mjs run tests/initial-outreach-authoring.test.ts tests/feature-authoring.test.ts tests/feature-configuration-screen.test.tsx tests/initial-outreach-seed.test.ts tests/system-commerce-tool-sync.test.ts`: PASS 5 files/42 tests.
- `node node_modules/typescript/bin/tsc --noEmit -p tsconfig.build.json`: PASS exit0. Exact workspace bootstrap-resolved Node used, no alternate runtime selection. No production source changes after compiler pass.
- `git diff --check`: PASS.
### Correction Contract Disposition
- Published5.5.0 pin: implemented package+lock.
- Canonical output validator/compiler: implemented purpose-profile.ts; one Shared implementation, unchanged schema/results.
- Real default four seed/publication and complete values: implemented focused production descriptor/seed fixture, passes.
- Supported fifth, roles, immutable snapshot, empty/unsupported rejection: rechecked in39-test publication and42-test authoring/seed runs.
- Same branches/report and review return: implemented; no new claim or enabled task execution.
### Deviations
None. Known shipping descriptor remains outside canonical supported subset and is not misrepresented as supported; fifth acceptance uses actual compiler-validated read-only GraphQL. No arbitrary operation admission.
### Assumptions
No deployed rollout/activation implied. Canonical output compiler validates generic bounded structure; existing owning validators and owner-feature/tenant/permission controls remain authoritative.
### Unresolved Issues
None. Historical Shared5.4 default-output blocker resolved by accepted/published5.5.0; prior blocked record preserved below.
### Architectural Concerns
None newly introduced. No Shared source duplication, live migration/activation, main integration or downstream consumer implementation.
### Git / VCS — Attempt2
- Task branch unchanged: task/ARCH-064-COMMERCE-001.
- Canonical workspace /Users/kwadwoadomafriyie/project/moda-interact-workspace.
- Parent /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-064-COMMERCE-001; implementation /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-064-COMMERCE-001.
- Both exact task worktrees reused; no shared checkout mutation or another task worktree reuse.
- Launcher parent/implementation remote-task fast-forward not-needed; origin/main already-current. Recursive sync/update passed; database379d563f6b9ee070305e284615dddbc0b97afeb0 ready.
- Attempt2 claim80bc2ece9fb9a3f0a58c72074fa007f627094f31 committed/pushed by launcher; not repeated.
- Implementation correction bef213b (full hash in task history), pushed matching branch. Parent current report commit follows this edit and is pushed to same branch.
- No main merge, gitlink staging, live setup/migration/activation or follow-on execution.

### Historical Attempt1 Report
### Status
Blocked — scoped implementation published; default purpose output schemas incompatible with published Shared 5.4.0 profile subset.
### Files Changed
- package.json/package-lock.json: published Shared 5.4.0 pin.
- src/studio/features/{contracts,persistence,services,feature-configuration-screen}.ts(x); src/studio/server-actions.ts.
- src/commerce/integration/studio/services.ts: alternate feature list/detail visibility.
- src/commerce/publication/{ports,lifecycle,purpose-profile}.ts and integration/backend/publication-storage.ts.
- src/commerce/integration/backend.ts: server dev-auth environment/exact development identity guard.
- src/commerce/bootstrap/{system-commerce-tool-sync,system-product-release}.ts.
- Focused feature UI, purpose authoring/publication/seed, publication storage and system sync fixtures.
### Work Completed
Super Admin-only trusted feature list/detail/behavior/member services, persisted role checks, ordered canonical reference membership mutation with shared config CAS/advisory lock/audit/idempotency; ADMIN/forged client fields cannot grant role. Ordinary purpose-owned capability creation denied, existing canonical ownership retained in DTO and database. Attach choices/mutations reuse publication read validator. Initial Outreach uses existing behavior editor with attach/reorder/remove controls and conflict/unknown recovery, without duplicating capabilities.

Complete release snapshot loads/writes same-release purpose references and immutable exact revision IDs; lifecycle validates published Shared profile/read-only operations and rejects empty/foreign/unsupported profiles. Existing Super Admin publish/activate/rollback role path retained; production development impersonation guarded. Draft changes do not mutate old releases; setup cannot silently advance purpose-pinned revisions. First-only atomic seed reuses existing four canonical references and original trusted prompt, preserving later empty/edited profile.

Supported bounded Admin GraphQL fifth-read addition/removal tested. Real default policy schemas fail published DetailsSchema subset, so default profile publication stays fail-closed; no local schema widening/projection added. No live setup/migration/activation or consumer implementation performed.
### Validation Results
- Published package install and `npm run prisma:generate`: PASS. npm audit reported 35 existing dependency issues (18 moderate,16 high,1 critical); no broad remediation/lock churn.
- `vitest run tests/initial-outreach-authoring.test.ts tests/feature-authoring.test.ts tests/feature-configuration-screen.test.tsx tests/feature-configuration-page.test.tsx`: PASS 4 files/29 tests. Trusted ADMIN/bypass denial, forged fields, canonical attach/order/CAS/replay and ordinary/UI regressions.
- `vitest run tests/initial-outreach-seed.test.ts tests/system-commerce-tool-sync.test.ts`: PASS 2 files/18 tests. First-only/default order/no clones, edited empty profile preservation, missing refs atomic conflict, setup repoint guard and role checks.
- Publication/lifecycle/storage focused tests: PASS 3 files/38 tests, including bounded fifth GraphQL, removal, immutable pinned behavior/revision, ADMIN/forged lifecycle, empty/foreign/unsupported rejection.
- Production `tsc --noEmit -p tsconfig.build.json`: PASS after correcting owner DTO string narrowing. No UI routes/schema changes; local generated client used. Tests executed with exact workspace-bootstrap-resolved Node, no alternate runtime selection.
- `git diff --check`: PASS.
- Default operation output schema compatibility: FAIL (architectural Shared contract gap below), not treated as passing acceptance. Required snapshot/default acceptance and complete focused acceptance remain unchecked.
### Deviations
Task cannot finish default profile publication under current published Shared5.4.0 contract. Preserved valid prerequisite/UI/seed/lifecycle work rather than introduce incompatible local schema or silently change output. Exact fixture compiler is reused for genuinely supported bounded GraphQL fifth tool; no fake policy schema.
### Assumptions
Initial Outreach is governance only; existing checkout_recovery/owner-feature/plan admission unchanged. Runtime consumers independently owned; no rollout/deployed-state claim.
### Unresolved Issues
Published CommercePurposeProfileSchema uses DetailsSchemaSchema for outputSchema. Existing registered default policy descriptors are not accepted by that bounded subset: discounts.getOptions/getDetails root `/anyOf`; products.search `/properties/products/items/properties/url/format`, `unitPrice/pattern`, `categoryIds/maxItems=128`, `collectionIds/maxItems=128`, nested saleEvidence observedAt format/pattern; products.get equivalent under `/properties/product` plus nullable object. All four `DetailsSchemaSchema.safeParse` fail; profile reports capabilities[i].outputSchema -> bounded INVALID_DEFINITION. No existing canonical compatible projection found. Diagnostic local receipt /private/tmp/arch064-purpose-schemas.jsonl. Owning Shared correction/approved published contract or canonical bounded projection required before default publication acceptance.
### Architectural Concerns
Return contract gap to moda_architect; do not loosen validation, fabricate a compatible schema, change canonical tool outputs or implement downstream runtime workaround in Commerce.
### Git / VCS
Task branch: task/ARCH-064-COMMERCE-001
Physical worktree isolation:
- canonical workspace: /Users/kwadwoadomafriyie/project/moda-interact-workspace
- parent worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-064-COMMERCE-001
- implementation worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-064-COMMERCE-001
- shared/default checkout mutated or another task path reused: no
Start synchronization from prepared packet:
- parent and implementation task fast-forward: not-needed; origin/main already-current
- recursive submodule sync/update passed; database379d563f6b9ee070305e284615dddbc0b97afeb0; ready
- Attempt1 claim73976cbc085e9876d9d6cff533a551639b8a2e11 pushed
Implementation commit5f97611 (full hash in task history), published matching task branch. Parent report commit follows this edit; no gitlink staged, no main merges.

## Architect Review
### Review Status
Blocked — published Shared purpose output subset incompatible with default policy outputs.
### Review Notes
Inspected published partial implementation 5f976119901c271173e3c32152a11d00377f8449 and report 701cb23bfd0442570f057060977a9219dd9323f2. Valid authoring, server-side role checks, CAS/audit/idempotency, membership UI, seed and immutable snapshot work retained. Early owner DTO/read-only admission/replay authorization findings corrected. No Accepted outcome: default profile publication still fails correctly under Shared 5.4.0.
### Reviewed Files
Feature services/persistence/UI and legacy read paths; publication purpose helper/lifecycle/storage; first-only seed/system release preservation; focused tests and task report.
### Validation Reviewed
Feature/UI29, seed/sync18, publication/storage38 passed; production typecheck passed after DTO narrowing fix; diff checks passed. Supported bounded GraphQL fifth member tested. Actual default policy schemas deterministically fail DetailsSchemaSchema: discount root anyOf; product format/pattern/nullable object and maxItems128. Passing supported fixtures do not satisfy failing default acceptance.
### Architecture Conformance
Partial code respects single-owner and fail-closed boundaries; no local schema invention, default hardcoded restoration or downstream consumer workaround. Canonical worktree/publication evidence verified; no live migration/activation/main merge. Required complete acceptance remains unchecked.
### Follow-up
ARCH-064-SHARED-003 implements bounded canonical output compatibility; ARCH-064-SHARED-004 publishes accepted correction. Then reclaim same Commerce task/branches for corrected package pin and real default/fifth-tool acceptance. No source reimplementation merely to manufacture commits; preserve existing validated work. No automatic task execution.


## Purpose publication authority and underlying tool edits
Any release containing initial_outreach behavior/purpose members requires SUPER_ADMIN at publish AND activate/rollback, checked server-side in lifecycle services, not only Feature editor. Global ADMIN may retain existing rights to edit unrelated/shared tool drafts, but cannot publish/activate a new outreach snapshot or repoint its revisions through another Feature workflow. Existing immutable release references mean editing a draft never changes active outreach. Super Admin publication reviews selected exact revision IDs and behavior as one complete snapshot; ordinary release services cannot silently copy/advance outreach members to latest revisions. For a release that preserves outreach unchanged, activation still requires SUPER_ADMIN because the pointer controls this purpose. No bypass via setup command, generic release action, development role field or forged client role. Existing authenticated development bypass policy remains explicit and may not impersonate SUPER_ADMIN for production mutations. Add ADMIN direct lifecycle publish/activate/rollback tests plus underlying draft edit test proving active pinned profile unchanged. Keep existing audit reason/actor/operationId and immutable snapshot evidence; no new permission granted to arbitrary tools.

## Architect Dependency Unblocking — 2026-11-06
SHARED-004 Attempt1 explicitly developer-completed at5634042d8e52943adcf0dbac0ff929ddf62f4407, after verified public5.5.0 corrected compiler/profile/manifest/grant exports. External Shared contract blocker resolved. Return this same task to Ready with Attempt1 preserved and executor/claimed_at null; next canonical launcher claim increments exactly once. Preserve historical blocked review and partial source5f976119901c271173e3c32152a11d00377f8449.

### Next Attempt Correction Contract
- Pin published @modainteract/moda-interact-shared@5.5.0 in Commerce and lockfile.
- Replace local Details-only result-schema assumption with canonical validate/compileCommercePurposeOutputSchema export where required, retaining single Shared implementation and no lossy projection.
- Validate actual default four policy descriptors and complete output values through real publication/profile validation; default seed + publication must succeed, preserving canonical ownership/IDs and edits.
- Recheck supported fifth read addition/removal, empty/unsupported/mutating rejection, role/direct lifecycle guards and immutable old snapshot behavior, focused owner tests/typecheck.
- Record actual changed files/evidence on same branches and return review; no arbitrary schema widening, package republish, live activation/migration or downstream work.

Next invocation: `/moda-task ARCH-064-COMMERCE-001`. No implementation or new claim performed by this unblocking.
