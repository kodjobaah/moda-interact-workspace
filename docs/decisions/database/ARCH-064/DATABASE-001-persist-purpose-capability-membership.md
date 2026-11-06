---
id: ARCH-064-DATABASE-001
architecture_id: ARCH-064
title: persist purpose capability membership
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: developer
status: review
priority: 50
executor: null
claimed_at: null
attempt: 1
depends_on: []
enables: ["ARCH-064-COMMERCE-001", "ARCH-064-MCP-001", "ARCH-064-SYSTEM-TEST-001"]
created: 2026-11-06
updated: 2026-11-06
---
# Persist purpose capability membership

## Architecture
ARCH-064; docs/architecture/ARCH-064-published-initial-outreach-profile.md. Coordinator moda_architect.

## Objective
Persist purpose capability membership with immutable purpose selection, not global tool admission.

## Context
Background four-name Set, schema union and graph switches currently cap initial outreach independently of Studio publication. New profile references preserve existing capability ownership.

## Scope
moda-interact-database implementation and tests at verified touchpoints.

| Existing file | Exact surface | Required edit |
|---|---|---|
| moda-interact-database/prisma/schema.prisma | Feature/CommerceFeatureConfiguration/CommerceReleaseFeature and release members | Add exact two purpose membership joins and relations/checks/indexes; preserve existing ownership/immutability. |


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
- [x] Add exact two purpose membership joins and relations/checks/indexes; preserve existing ownership/immutability.

## Interfaces / Contracts
Exact purpose profile/membership/behavior schemas and draft/release join models above; Shared publication prerequisite gates consumers. Initial Outreach is governance Feature, checkout_recovery remains admission, referenced owner-feature eligibility remains required.

## Dependencies
None

## Enables
- ARCH-064-COMMERCE-001
- ARCH-064-MCP-001
- ARCH-064-SYSTEM-TEST-001

## Acceptance Criteria
- [x] Migration accepts same-release member references and rejects cross-release/missing member, duplicate position and delete/rewrite immutable release purposes.

## Validation
- [x] Run declared focused owner tests for each task assertion; add deterministic unit/integration fixtures for same-release/tenant/role/purpose/immutability constraints and the supported fifth-tool case.
- [x] Run declared typecheck/build appropriate to owner (Database schema/migration/constraint tests; Background build; System Test harness/syntax instead of app build). Record exact commands/results and no secrets in diagnostics.

## Stop Condition
Submit completed scoped report for authorized review and STOP. Explicit developer completion required. No enabled follow-on task auto-start; terminal System Test manually invoked after accepted dependencies.

## Implementation Notes
Execution ownership amendment (2026-11-06): developer explicitly requested agent implementation through `/moda-task ARCH-064-DATABASE-001` and authorized synchronization plus task claim, implementation and review publication. Delegate to moda_database through canonical preparation, retaining completion_mode developer and exact additive schema/migration scope. No live database migration or downstream runtime implementation authorized by this amendment.

No execution from definition. Use normal launcher-isolated/synchronized task worktrees when requested. Exact architecture choices above are binding; report demonstrated incompatibility instead of selecting new schema/identity/authorization design. Preserve historical task status and unrelated edits.

## Completion Report
### Status
Ready for Review
### Files Changed
- prisma/schema.prisma: two exact purpose membership joins and four inverse relations.
- prisma/migrations/20261106192000_arch064_purpose_capability_membership/migration.sql: additive tables, keys/checks/indexes/Restrict FKs and existing immutable trigger.
- scripts/test-arch064-purpose-membership-postgres.mjs and package.json: focused disposable fixture command.
- docs/generated/prisma-erd.puml: task-specific generated entities/relations.
### Work Completed
Draft membership references canonical Feature/Capability without changing ownership. Release membership references exact same-release Feature snapshot and Capability member through composite FKs, deriving revision identity from existing member. Unique ordered positions and nonnegative checks apply to both joins. Release update/delete uses existing commerce.arch020_immutable guard; draft remains editable. Reverse capability index supports reference lookup/deletion integrity; release/capability index supports member FK and reverse lookup. Existing PK/unique prefixes support ordered purpose reads. No seed, entitlement, permission/runtime or live migration changed.
### Validation Results
- `npm ci --ignore-scripts`: PASS locked install; audit reported 9 existing dependency issues (4 moderate,5 high), no dependency changes/remediation.
- `npm run prisma:validate`: PASS; repeated final validation after whitespace-only minimization PASS.
- `prisma migrate diff --from-schema-datamodel <accepted-before-schema> --to-schema-datamodel prisma/schema.prisma --script`: PASS generated DDL comparison. SQL names aligned exactly to Prisma 63-byte bounded FK and explicitly mapped unique index; SQL adds required CHECK/trigger beyond Prisma representation.
- `npm run test:arch064-purpose-membership:postgres` (final direct invocation using exact bootstrap-resolved Node): PASS fresh complete migration history on disposable pgvector/pgvector:pg17 plus focused actual migration over minimal accepted parent-key fixture. Valid same-release members/draft edits accepted; 14 deterministic invalid cross/missing-release/feature/capability/position/rewrite/delete operations rejected; canonical owner preserved. Container removed. Initial plain postgres image lacked vector extension; corrected to repository-standard pgvector image. Readiness socket messages transient; historical migration identifier notices only, no new truncation notice.
- `npm run prisma:generate`: PASS Prisma Client 6.19.3.
- `npm run erd:puml`: PASS; retained only two generator-produced entity blocks and their relationships, avoiding unrelated stale-ERD catch-up.
- `git diff --check`: PASS.
### Deviations
Authored additive SQL from Prisma-generated schema diff and validated complete chain on disposable PostgreSQL rather than running migrate dev against the user's standard local database; no shared/live database touched. Focused integrity fixture uses minimal accepted parent-key tables and an equivalent immutable trigger function; full-chain proof applies actual accepted guard history. Tenant/role/fifth-tool runtime assertions belong to consumer/system tasks, not these global join constraints. ERD update scoped to generated task additions, avoiding unrelated 800-line catch-up. No semantic schema formatter churn retained.
### Assumptions
Purpose membership is global Studio governance; tenant/role authorization and optimistic feature configuration/audit updates remain owning Commerce service responsibilities. Missing profile publication rejection and release orchestration remain consumers' responsibility.
### Unresolved Issues
None.
### Architectural Concerns
No new cross-repository requirement; additive migration must precede consumers. No rollback destruction/backfill or data rewrite required.
### Git / VCS
Task branch: task/ARCH-064-DATABASE-001
Physical isolation:
- canonical workspace: /Users/kwadwoadomafriyie/project/moda-interact-workspace
- parent: /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-064-DATABASE-001
- implementation: /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-064-DATABASE-001
- parent/implementation branch: task/ARCH-064-DATABASE-001
- shared/default checkout mutated/switched: no; other task worktree reused: no
Start synchronization (prepared launcher): both remote task fast-forwards not-needed; both origin/main already-current; recursive submodule sync/update passed, no submodules.
Claim Attempt1 e24ef28dd49b95808ac5ce186dc7ce4b051095a6 pushed.
Implementation: b161a0fa251031737fdc05f4ddbfcb265742af71 pushed and exact remote verified.
Parent report commit follows this edit, matching task branch; submodule gitlink staged no. Main merges none.

## Architect Review
### Review Status
Accepted — explicit developer completion pending.
### Review Notes
2026-11-06 moda_architect inspected actual schema, migration and fixture at b161a0fa251031737fdc05f4ddbfcb265742af71 plus report 7455d6b9ab2286a144dd5a8bba85a90c60b59c2b. Two joins implement exact draft/release purpose membership without capability ownership duplication. Same-release composite FKs bind immutable Feature and Capability snapshots, positions are nonnegative/unique, Restrict relationships preserve references, existing immutable row guard blocks release-purpose rewrite/delete. No copied schemas/revisions or merchant entitlement introduced. Generated DDL identifier mismatch found during implementation was corrected and validated; no outstanding correction.
### Reviewed Files
- prisma/schema.prisma
- prisma/migrations/20261106192000_arch064_purpose_capability_membership/migration.sql
- scripts/test-arch064-purpose-membership-postgres.mjs
- package.json, scoped generated prisma-erd.puml, task Completion Report.
### Validation Reviewed
Prisma validate/client generation and generated DDL comparison passed; SQL identifiers match Prisma bounded names and mapped unique index. Disposable pgvector PostgreSQL17 applied complete migration history successfully. Focused actual new migration validates valid same-release membership, editable drafts/owner preservation and 14 rejected FK/position/immutable/delete mutations. Focused parent-key fixture uses equivalent immutable function; actual accepted guard is applied by full-chain proof. No claims of tenant/role/fifth-tool runtime validation at database boundary. Scoped generated ERD/diff checks passed.
### Architecture Conformance
Conforms to ARCH-064 additive database contract and single-owner boundary. SQL CHECK/trigger supplement Prisma representation. Migration authoring via generated diff plus disposable full-chain proof is acceptable and avoids unauthorized live migration. Canonical dedicated worktrees/synchronization/durable claim evidence verified. No live migration, main merge, gitlink, seed, runtime or permission changes.
### Follow-up
Task remains review at Attempt 1 with completion_mode developer. Explicit completion: `/moda_developer_update ARCH-064-DATABASE-001 complete`. Additive migration must precede consumers during rollout; no dependent task promotion before actual completion, no automatic follow-on execution.


## Purpose publication authority and underlying tool edits
Any release containing initial_outreach behavior/purpose members requires SUPER_ADMIN at publish AND activate/rollback, checked server-side in lifecycle services, not only Feature editor. Global ADMIN may retain existing rights to edit unrelated/shared tool drafts, but cannot publish/activate a new outreach snapshot or repoint its revisions through another Feature workflow. Existing immutable release references mean editing a draft never changes active outreach. Super Admin publication reviews selected exact revision IDs and behavior as one complete snapshot; ordinary release services cannot silently copy/advance outreach members to latest revisions. For a release that preserves outreach unchanged, activation still requires SUPER_ADMIN because the pointer controls this purpose. No bypass via setup command, generic release action, development role field or forged client role. Existing authenticated development bypass policy remains explicit and may not impersonate SUPER_ADMIN for production mutations. Add ADMIN direct lifecycle publish/activate/rollback tests plus underlying draft edit test proving active pinned profile unchanged. Keep existing audit reason/actor/operationId and immutable snapshot evidence; no new permission granted to arbitrary tools.
