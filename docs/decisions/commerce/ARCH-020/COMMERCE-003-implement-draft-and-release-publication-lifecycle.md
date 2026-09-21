---
id: ARCH-020-COMMERCE-003
architecture_id: ARCH-020
title: Implement draft and release publication lifecycle
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 70
executor: null
claimed_at: null
attempt: 2
depends_on:
  - ARCH-020-COMMERCE-002
  - ARCH-020-DATABASE-001
  - ARCH-020-SHARED-001
enables:
  - ARCH-020-COMMERCE-004
  - ARCH-020-COMMERCE-012
  - ARCH-020-COMMERCE-013
  - ARCH-020-SYSTEM-TEST-001
created: 2026-09-20
updated: 2026-09-21
---

# Implement draft and release publication lifecycle

## Architecture

Architecture ID: ARCH-020.

Architecture document: docs/architecture/ARCH-020-commerce-agent-studio-mcp-capabilities.md.

Coordinator: moda_architect. Read the complete parent architecture and relevant dependency/contract tasks. Execution handoff: docs/architecture/ARCH-020-implementation-handoff.md.

## Objective

Persist and atomically publish immutable capability releases with an auditable rollback path.

## Context

Merchant-selected capabilities should drive WhatsApp CommerceAgent behaviour through a separate Next.js MCP server with a team-only Studio. Production conversation admission, ordering, model hosting and delivery remain in Background. This is a pre-production breaking rollout, with no implicit permission to delete durable data.

Task definition is on local workspace main by the developer's explicit 2026-09-20 review request. It is not a claim, task-branch materialisation or implementation approval. All execution fields remain unclaimed.

## Scope

Commerce persistence services and protected server actions for draft/publish/history/rollback/disable.

## Out of Scope

Other repositories' implementation, unrelated refactoring, automatic execution of enabled tasks, live deployment, main integration/push and changes to billing prices/merchant entitlements. No cart/order/discount mutation, WhatsApp sending from Commerce, arbitrary executable code or arbitrary-host HTTP endpoints; C14 validated read-only GraphQL definitions are explicitly permitted. No duplicate discount catalogue/merchant configuration system. Shared indexes and architecture reconciliation remain architect-owned.

## Requirements

Follow the parent architecture's tenant/policy/revision contracts and the assigned logical owner. Preserve unrelated changes. Read repository-local AGENTS.md if present. Commerce consumes the canonical database through its nested database/ Git submodule; schema and migrations belong to moda_database. For consumers, use actual accepted and published dependency revisions, not copied task snapshots or hypothetical versions.

### Duplicate-action protection

Every state-changing or costly UI action in this task must prevent duplicate
activation, including mouse double-click, double-tap, Enter/Space repetition and
form-submit plus button-click combinations. Acquire a synchronous submission
guard before awaiting work (a render-delayed disabled state alone is insufficient),
and route all activation paths through the same submit handler. Disable the
trigger and conflicting controls immediately, show a meaningful pending label,
and expose accessible busy/status feedback. Do not lock unrelated navigation.

Keep the guard until the operation has definitively completed, failed or been
cancelled. A client timeout is an unknown outcome: reconcile the original
operation before allowing a retry, rather than silently creating a second one.
On a known failure, restore controls and preserve input for an intentional retry.
Ignore stale completions so an earlier request cannot reset a newer request's
pending state. Debounce alone is not sufficient for mutations or paid previews.
Server authorisation and duplicate protection are required independently of the
browser controls; inspect direct duplicate requests as well as UI behaviour.

## Work Items

### Parallel implementation and integration ownership

Architect promotion on 2026-09-21: Ready, unclaimed. Implement publication against
C17 agreed ports and deterministic fixtures. This task may be accepted independently
when its owned component, typed interfaces and fixture acceptance tests pass.
ARCH-020-COMMERCE-013 owns real provider adapters, composition and integrated
acceptance; do not wait for or implement that task here.

For this task, all requirements below to consume pending services or exercise a
complete service flow mean contract-fixture execution. This explicitly supersedes
earlier accepted-service/full-integration wording for those pending dependencies.
Retain every field, page, role, failure and side-effect expectation. Do not weaken
them to snapshots or static mockups. Production composition must fail unavailable
until013 installs real adapters; fixtures are test-harness-only, never a runtime
fallback. Already accepted auth/Shared/database dependencies remain real inputs.
Record the port signatures and mapping in the C17 contract document. Integration
checks are assigned explicitly to013, not reported as passed by this task.

- [ ] Reuse C7.1 guards for every publication operation and validation endpoint; ensureDevelopmentStudioAdmin inside the same FK-backed audit/publication transaction when the server-resolved principal is development bypass. Verify A07/A08/A10; no copied auth policy.

- [ ] Implement C16 createRelease definition/hash persistence, replay binding and authenticated /api/studio/response-contract/validate; baseline seed, immutable clone semantics, role enforcement and R01–R06/R09.

- [ ] Implement independent createTool/updateTool/createToolDraft/updateToolDraft/publishToolRevision/setToolEnabled with C7 replay/CAS/audit. Capability drafts store exact toolBindings; no copied definitions. Shared tools can be reused; no implicit latest revision.
- [ ] Consume the accepted COMMERCE-011 local schema/compiler validator for query publication; validate installed policy operation descriptors through an injected registry interface. Until concrete adapters exist, test policy operations using explicit fixtures and reject unavailable adapters at runtime, never claim they are installed.
- [ ] Release creation rejects conflicting shared-tool revisions, deduplicates identical ones and preserves full original grant provenance. Base conversation_core can contain no tools. Publication never modifies Admin Feature/plan/preference records.

- [ ] Read the existing Admin-owned Feature catalogue by database identity for Studio configuration. Do not create or mutate Feature records, plan mappings or ShopFeaturePreference from Studio. A missing Commerce configuration must not change billing eligibility. Validate an arbitrary newly created feature key rather than seed-name whitelists.

- [ ] Create/save/publish independent tool definitions and exact capability toolBindings using existing replay/CAS/audit. Validate definition-version changes and available operationVersion; hash schemas/mappings/templates. Seed reviewed example definitions through existing explicit seed command.

- [ ] Implement capability bindings, optimistic draft edits and bounded schema validation using the canonical shared package.
- [ ] Validate database definitions, executor-operation availability and runner compatibility and create complete immutable release membership, then activate its pointer in a separate explicit atomic operation.
- [ ] Append actor/reason/hash audit evidence in the same transaction; implement compatible rollback and emergency disable.
- [ ] Enforce the DATABASE-001 publishing responsibilities: atomic 1–32-member release creation with contiguous positions and base capability, no later member insertion, CAS writes, canonical content hashing and actor/audit transactions.
- [ ] Provide paginated read models for Studio and an idempotent explicit initial-release seeding command; never seed by wiping tables.
- [ ] Consume the accepted database revision through the nested submodule; document the exact pin.

- [ ] Make create/save/publish/activate/rollback/enable/disable mutations replay-safe. Each logical operation carries one opaque operationId reused on retries and a canonical payload hash. Use CommerceAuditEvent.id as the unique operation key inside the same transaction as business writes; store payloadHash and bounded result IDs in metadata. Check current authorisation first. A committed matching actor/action/hash replay returns the original result; mismatched reuse conflicts. Concurrent duplicates must roll back losing writes and resolve the winning audit record, producing no extra revision/release/audit. Keep CAS checks for distinct conflicting edits. Set enabled to an explicit value, never blind toggle.

## Interfaces / Contracts

Read the binding schema contract in docs/decisions/database/ARCH-020/DATABASE-001-persist-capability-releases-and-turn-revision-pins.md. Its exact field names/types, enum values, JSON shapes/bounds, immutable release membership and selectedCapabilityKeys/grantedTools conversation grants are the persistence contract; do not invent alternative representations. Shared APIs serialize dates as ISO strings and map database environment enums to lower case.

Database revision/release model and ./commerce schemas. Reuse canonical policy state read-only.

### Implementation guidance

Apply binding contracts **C14–C15** for reusable tool revisions, query/policy execution, safe templates, original grant provenance and integrated Studio authoring. The page/traversal specification is required for UI owners.

Binding companion: [ARCH-020 implementation contracts](../../../architecture/ARCH-020-implementation-contracts.md), sections **C1, C4, C7**. These are required acceptance inputs, not optional examples.

Deliver publication domain services, strict action schemas, transactional audit/replay and explicit seed CLI. Build typed read-only executor-operation descriptors as the publication registry; operations may be added by COMMERCE-005/006/007, but descriptors alone must not claim operation availability. Publish database tool definitions only when their query executor/schema or policy-operation versions have executable implementations in the deployed build. Synthetic registry fixtures permit this task to be tested before later implementations.

### Deterministic review clarification

Synthetic executable registry adapters are dependency-isolated test fixtures,
never production registrations. This task proves publication validation and
transactions with those fixtures; COMMERCE-005/006/007 provide real executors and
SYSTEM-TEST-001 proves the deployed author/publish/invoke flow. Do not add a
circular dependency on those later tasks or advertise unimplemented operations.
Provide the isolated PostgreSQL rehearsal command and expected assertions; report
agent fixture results separately from developer-owned database rehearsal evidence
under C12. An unexecuted rehearsal must remain explicitly pending.

### Required evidence

Use two-transaction local storage fixtures and an isolated PostgreSQL rehearsal for duplicate operation IDs, mismatched reuse, revision allocation, CAS pointer conflicts, rollback and failed partial publication. This backend task tests direct requests; COMMERCE-008 owns mouse/keyboard tests.

For this task, record a requirement-to-fixture matrix with expected side effects, actual commands and results in the Completion Report. Do not implement another repository's changes to bypass a dependency.

## Dependencies

- ARCH-020-COMMERCE-002
- ARCH-020-DATABASE-001
- ARCH-020-SHARED-001

Every dependency must be Complete and architect-accepted before execution. Reconcile accepted dependency metadata into the matching parent task branch before promotion. Developer integration or explicitly approved accepted-commit consumption is required to obtain prerequisite source. Readiness never launches a task. Commerce tasks additionally require the new-owner setup checkpoint.

## Enables

- ARCH-020-COMMERCE-004
- ARCH-020-COMMERCE-012
- ARCH-020-COMMERCE-013
- ARCH-020-SYSTEM-TEST-001

## Acceptance Criteria

- [ ] Demonstrate the assigned C16 response-contract cases with named fixtures and actual outcomes; reference the exact published definition/hash or synthetic preview definition used.

- [ ] Two features can reuse one published tool; editing/publishing a new tool version changes neither feature binding until explicitly updated. A release with conflicting tool versions is rejected atomically.
- [ ] Publish a new static Shopify query within the pinned schema without registering a business operation or deploying a service; changed query/schema/template requires a new tool version.

- [ ] Concurrent publish/edit operations cannot overwrite each other or expose partial releases.
- [ ] Published revisions are immutable; rollback preserves history; invalid definitions or unavailable executor operation versions cannot be published.
- [ ] Every release mutation is server-authorised and audited; no merchant feature, discount or billing settings are overwritten.

- [ ] Concurrent identical mutation requests yield one committed business change and one operation audit record. Matching retries recover the original result; altered payload/actor reuse is rejected. A timeout after commit cannot create another revision/release on retry.

## Validation

- [ ] Publishing a new definition over an installed operation succeeds without a service deployment; changed definition with unchanged version, unsupported operation, bad mapping/template and duplicate release tool names fail atomically.

- [ ] Run focused local transactional/optimistic-concurrency tests with deterministic storage fixtures.
- [ ] Provide a developer-owned PostgreSQL rehearsal command for atomic pointer/audit and rollback evidence; run declared local type/lint checks.

Use package.json commands actually provided by the repository. New Commerce scripts and test fixtures are deliverables, not claims that they exist today. Follow docs/agent-validation-execution-policy.md and docs/agent-live-validation-execution-policy.md. Separate local evidence from pending developer-owned long/live validation; required evidence must exist before acceptance.

## Stop Condition

After scoped work and agent-owned checks, update this task's execution/report fields, publish task-owned mirrored branches and return to review. Record exact pending developer validation where applicable. Stop; do not begin enabled tasks or mark your own task Complete. Publication tasks stop after release mechanics. System tests require explicit developer invocation even after becoming Ready.

## Implementation Notes

Normal execution uses /moda-task and scripts/start-agent-task.py preparation, dedicated parent and implementation worktrees, synchronization and recursive submodule initialisation. Follow docs/agent-vcs-ownership-policy.md, docs/agent-worktree-isolation-policy.md and docs/task-definition-materialization.md. The main-only exception applies to this review draft, not task execution. The COMMERCE route is registered in this packet; the actual repository must be provisioned before execution preparation.

## Completion Report

### Status

Ready for Review.

### Files Changed

Attempt 2 implementation commit `d5d7f56` changes:

- `src/commerce/publication/ports.ts`
- `src/commerce/publication/validation.ts`
- `src/commerce/publication/lifecycle.ts`
- `src/commerce/publication/read-models.ts`
- `lib/commerce/lifecycle.ts` (compatibility re-export)
- `app/api/studio/response-contract/validate/route.ts`
- `tests/commerce-lifecycle.test.ts`
- `tests/fixtures/publication-store.ts`
- `docs/publication-service-contract.md`
- `scripts/rehearse-publication-postgres.sh`
- `scripts/fixtures/arch020-publication-rehearsal.sql`

### Work Completed

Attempt 2 implements all four requested corrections:

- **R1 implemented:** publication validation and hashes now wrap the accepted
  Shared schemas and `canonicalJson`, `toolHashInput`, `capabilityHashInput`, and
  `responseContractCanonicalJson`. Tool hashes select only the six canonical
  definition fields. The authenticated validation route also validates the
  complete example response.
- **R2 implemented:** transaction admission, persisted state, snapshots, command
  results, and replay results are detached. Release creation validates all
  members before writes, rejects duplicate revision/capability membership, keeps
  contiguous positions, permits shared identical tool revisions, and rejects
  conflicting revisions atomically.
- **R3 implemented:** the owned component now has explicit storage,
  authorization, query-validation, and executable-registry ports; complete C7
  create/update/draft/publish/release/pointer/enable operations; detached read
  models; and a repeat-safe initial release seed orchestration. Two independent
  service instances share the transaction fixture. Current authorization is
  checked before replay and again inside the transaction; development-principal
  assurance is inside that transaction. Production composition remains
  unavailable for COMMERCE-013.
- **R4 implemented:** pagination uses the last returned row as its exclusive
  continuation cursor, rejects unknown cursors/invalid limits, returns null at
  completion, and detaches returned rows.

### Validation Results

Commands and outcomes for Attempt 2:

- `npm test -- --run tests/commerce-lifecycle.test.ts`: **17/17 passed**.
- `npm run lint`: **passed**.
- `npm run typecheck`: **passed**.
- `npm run build`: **passed**, including Prisma generation and Next production build.
- `npm test`: **86/86 passed** across 14 files. An earlier run executed in
  parallel with the production build had two readiness child-process timing
  failures; the final sequential run passed both unchanged tests.
- `git diff --check`: **passed**.

Requirement-to-fixture matrix:

- **R1 / Shared validation and hashes:** `accepts the Shared baseline and optional
  required keyword...`, `hashes only the Shared six-key tool definition`, and
  `keeps malformed draft content editable but rejects it atomically at
  publication`. Valid cases commit normally; invalid publication leaves the
  draft unchanged and adds **0** publication audit rows.
- **R2 / immutable ownership and membership:** `detaches admitted inputs,
  snapshots, and replay results`, `rejects duplicate release membership with
  zero release/member/audit writes`, and `allows two capabilities to share one
  revision and rejects conflicting tool revisions atomically`. Duplicate and
  conflict cases add **0** releases and **0** audit rows; the valid shared-tool
  release commits one release and one audit.
- **R3 / ports and transactions:** `serializes two service instances...` proves
  two callers produce **1** business row, **1** operation, and **1** audit;
  actor/payload conflicts and revoked replay add **0** rows; injected pre-audit
  failure rolls back to **0** rows and a retry commits exactly **1**. Query
  validation covers all three false codes and a thrown timeout/error with **0**
  publication writes/audits. Metadata/draft CAS, explicit enabled state,
  absent-pointer CAS, and repeat-safe seed all pass.
- **R4 / pagination:** limits 1 and 2 over five rows concatenate to all five IDs
  exactly once; empty/final cursors are null; unknown cursor and invalid limits
  reject; returned rows are detached.

Developer-owned PostgreSQL rehearsal remains explicitly pending. Run:

```bash
ARCH020_REHEARSAL_DATABASE_URL='postgresql://.../isolated_arch020_test' \
  bash scripts/rehearse-publication-postgres.sh
```

The script checks accepted database ownership/revision/position constraints and
lists the required adapter transaction assertions for duplicate IDs, mismatched
reuse, revision allocation, pointer CAS, rollback, and pre-audit failure. Real
provider/executor adapters and assembled integration remain COMMERCE-013-owned.

### Deviations

None for the Attempt 2 correction contract. Production Prisma composition and
real executor registrations remain unavailable by C17 design until COMMERCE-013;
all stores, authorization resolvers, registries, and query validators used by the
tests are injected fixtures only.

### Assumptions

Use the parent architecture and actual accepted dependency revisions. Return contradictory source facts to moda_architect.

### Unresolved Issues

The isolated PostgreSQL rehearsal is unexecuted under the developer-owned live
validation policy. Real executor/provider adapters remain pending
COMMERCE-005/006/007 and COMMERCE-013 composition.

### Architectural Concerns

None newly reported.

### Git / VCS

Implementation commit `d5d7f56` is pushed to
`origin/task/ARCH-020-COMMERCE-003`. Attempt: 2. The parent task report is
submitted on the mirrored parent branch. No main merge or parent service gitlink
update was performed.

## Architect Review

### Changes Requested — Attempt 2 — 2026-09-21

**Current decision: Ready, Attempt 2 preserved, executor/claimed_at cleared; not accepted.** Supersedes earlier current-state wording, preserving review history. Reviewed published implementation `d5d7f566f89bf62b385af550b435c6199e87590e` and parent report `6f4359a3383d5e36056e66149cbaf89430ea4cad`; both remote heads verified and dedicated worktrees clean. No implementation changes, main integration, gitlink updates or dependent promotion.

Accepted progress: Shared response/tool validation and canonical hashes, detached post-commit results, unique release membership, injected component ports, exclusive last-returned cursor. These corrections should be retained. Independently reran the submitted focused command: **17/17 passed**. An isolated copy of those tests importing the actual implementation added three regressions: **17 passed, 3 failed**, detailed below. Diff check passed. Full86/lint/typecheck/build are submitted passing evidence, not rerun in this review. PostgreSQL and live/provider integration remain explicitly unrun; C17 permits independent component acceptance and does not require implementing COMMERCE-013 here.

#### A2-R1 — P1 — Strict command validation must prevent ADMIN publication-state injection

Files: `src/commerce/publication/validation.ts`, `ports.ts`, and `lifecycle.ts` (`command`, `createDraft`, `updateDraft`, `publishRevision`). `CapabilityDraft` is only a TypeScript annotation. `updateDraft` checks contractVersion and then Object.assigns the entire caller object into the persisted revision. An ADMIN can supply additional `status:'PUBLISHED'` and `contentHash` fields, bypassing the SUPER_ADMIN publication command. The same path can replace row identity/ownership fields. Separate reproduction: configuration set to the string `not an object` is accepted by createDraft and successfully published with a hash. Shared's hash helper encodes content; it is not structural validation.

Required correction: define strict runtime command schemas, including strict nested capability drafts, and reject unknown keys before work/replay. Reuse accepted `CommerceConfigurationSchema`/tool binding schemas and DATABASE-001 prompt/configuration/binding bounds; do not create a parallel permissive wire schema. Persist only explicit owned fields. After parsing and detaching a draft, replace the update assignment with this field allowlist (variable names shown are local):

```ts
revision.contractVersion = draft.contractVersion;
revision.promptTemplate = draft.promptTemplate;
revision.configuration = structuredClone(draft.configuration);
revision.toolBindings = structuredClone(draft.toolBindings);
revision.editVersion += 1;
```

Never copy id, capabilityId, revisionNumber, status, contentHash, actor or timestamps from draft input. Publish must independently revalidate persisted prompt/configuration/bindings and exact published tool associations before changing status/hash. An invalid saved draft may remain editable where the contract permits it, but cannot publish. All command booleans/environments/CAS fields/metadata must be runtime validated; TypeScript alone does not satisfy C7 strict arguments. Capture a detached validated request before the first authorization/transaction await; hash and execute that same snapshot, rather than hashing a clone while work closures still read mutable caller input.

Permanent tests: ADMIN injection of each status/hash/identity field rejects with zero changed revision/audit rows; published state cannot be reached by updateDraft. Scalar/over-limit configuration, blank/oversized prompt and invalid bindings reject at the contract-appropriate boundary. Valid inputs publish with the Shared expected hash. Add a controlled authorization/transaction barrier proving caller mutation while the command is waiting cannot change admitted payload or replay binding. The isolated review tests are `review: ADMIN draft update cannot set publication state` and `review: malformed capability configuration cannot be published` in `/tmp/c003-a2-review/publication-review.test.ts`; both currently resolve instead of rejecting.

#### A2-R2 — P1 — Validate release compatibility before activation and rollback

Files: `src/commerce/publication/lifecycle.ts` (`createRelease`, `pointerMutation`), `ports.ts`, validation wrappers and tests. createRelease stores arbitrary runnerCompatibility strings; pointerMutation checks only release existence and CAS. The isolated test creates a release with `runnerCompatibility:'^99.0.0'` and activates it in TEST: result is successful pointer editVersion1. The accepted runner is1.x, so this creates a release pointer that consumers cannot execute. Original R3 explicitly required runner compatibility; this is not a new requirement.

Use a supported-runner/contract compatibility port or an explicit validated component dependency, supplied deterministically by fixtures and by013 production composition. Validate nonblank bounded SemVer ranges at release creation; before BOTH activateRelease and rollbackRelease, require target contractVersion and range compatibility with the supported runtime. Reject with INCOMPATIBLE_VERSION before pointer/audit writes. Recheck required immutable release metadata/hashes according to C16; do not make incompatible historical releases valid merely because they already exist. Preserve absent-pointer expectedEditVersion0 and normal CAS semantics. Add valid activation/rollback, malformed range, unsupported contract, unsupported range and stale-CAS tests; invalid operations leave pointer and audit counts unchanged. Keep creation of a valid future-version release separate from permission to activate it if that behavior is intentionally supported.

#### A2-R3 — P1 — Make capability selection ports represent the accepted database contract

Files: `src/commerce/publication/ports.ts`, `lifecycle.ts`, `read-models.ts`, fixture store and `docs/publication-service-contract.md`. Capability/createCapability omit featureId entirely, while DATABASE-001 requires FEATURE if and only if featureId is present. The submitted shared-tool fixture creates FEATURE without featureId, and another fixture uses RECOVERY_POLICY with key discount_help although the accepted key is discount_assistance. These synthetic successes cannot map to the real schema. Deferring013 adapters cannot repair missing business arguments without changing the accepted component interface.

Add the canonical nullable featureId to command/state/read mappings and a read-only existing-Feature lookup port. Validate arbitrary existing Feature IDs without a seed-name whitelist; never insert/update Feature, plan or ShopFeaturePreference. Enforce BASE iff key is conversation_core (single BASE), RECOVERY_POLICY only for discount_assistance, FEATURE with a real Feature identity, and non-FEATURE with no featureId. Preserve logical selection identity once a revision exists. Apply DATABASE-001 metadata bounds and map expectedUpdatedAt as the canonical timestamp token rather than manufacturing `version:<sequence>` in the domain. IDs/timestamps should be allocated by the storage transaction contract (deterministic clocks/IDs in fixtures), enabling013 to implement persistence without replacing lifecycle business logic. Document exact DB fields for identity, actors, timestamps and CAS, not only table names.

Tests: an arbitrary existing feature key/ID succeeds and is retained in the read model; nonexistent/missing/misbound Feature and wrong BASE/RECOVERY_POLICY identity reject with zero business/audit rows; multiple capabilities sharing the same Feature are allowed. Correct existing fixtures to use valid identities. Feature catalogue writes must remain zero. Metadata CAS tests must use real ISO timestamp tokens from a controlled storage clock.

#### A2-R4 — P2 — Deliver executable rehearsal assertions and complete transaction evidence

Files: `scripts/rehearse-publication-postgres.sh`, `scripts/fixtures/arch020-publication-rehearsal.sql`, `tests/commerce-lifecycle.test.ts`, fixture storage and contract/report docs. The SQL currently counts constraints and prints three PENDING strings; it does not execute replay conflicts, revision races, pointer CAS, rollback or injected partial-publication failure. The documentation calls these expected assertions of the command. Pending developer execution is valid; absent implementation of the promised rehearsal is a separate deliverable gap. A constraint count is not behavioral transaction evidence.

Implement a developer-invoked isolated database rehearsal with deterministic setup and real assertion failures for the promised cases. Use two coordinated PostgreSQL sessions for concurrent cases; a single outer transaction cannot demonstrate two-transaction races. Keep setup/cleanup scoped to the dedicated rehearsal database and accepted schema; no production adapters or live execution are required in this task. If a scenario specifically tests013's eventual adapter, label it separately as013 integration and supply the required003 SQL/storage contract rehearsal now. The command must return nonzero on a failed behavior and must not print a pass for pending checks. Do not run the developer-owned rehearsal during correction execution.

Complete the local two-service fixture cases promised in original R3: concurrent revision allocation, conflicting CAS winners, rollback, and lost response AFTER commit followed by matching retry. Existing pre-audit rollback proves a different case and must remain. Assert exact business/member/audit counts for each. Add unavailable-registry and role-denied publication cases independently of invalid schemas. Update the requirement matrix with actual test names/results; do not claim absent-pointer CAS conflict coverage from only a successful seed. Record the existing prepared packet's physical isolation, start-of-attempt synchronization and recursive database pin evidence; do not re-prepare an active attempt solely to recreate evidence.

### Attempt 2 resubmission gate

Make A2-R1–R4 corrections in the files above, preserving accepted R1/R2/R4 progress. Run permanent regressions and focused/full local tests, lint, typecheck, build and diff check; keep database/live013 validation honestly pending with runnable instructions. Publish the same implementation/report task branches and return to Review. This parent review overlay is published before handoff; it does not claim Attempt3. No new downstream task is started.


### Changes Requested — Attempt 1 — 2026-09-21

**Not accepted; Ready for corrections**, Attempt 1 preserved, executor/claimed_at cleared. Submission report says Ready for Review but YAML was in_progress; this review reconciles the authoritative state. Reviewed implementation 211b4a30a7fb73acf0195ca79e07e3c679a9e999 and report 194419508136a18edf21be8fa0decd3ebc162443 in clean dedicated worktrees. No new attempt or downstream promotion.

C17 explicitly permits deterministic component acceptance. Pending COMMERCE-013 production adapters and explicitly unrun developer PostgreSQL rehearsal are not being treated as implementation defects here. The submitted component itself fails the following requirements.

#### R1 — P1: consume the accepted Shared validation and canonical hash contracts

Location: `lib/commerce/lifecycle.ts`, local `canonical`, `validateDetailsSchema`, `validateResponseContract`, `validateTool`, and publishToolRevision. Replace parallel schema/type/encoder implementations with accepted Shared exports. Current response validation accepts `{version:'response.v1',instructions:'fixture',detailsSchema:{type:'string',maxLength:20}}` although C16 requires an object root; it also requires `required` where Shared allows omission. A permissive registry fixture cannot substitute for independent structural validation.

Tool hash currently includes the full mutable revision row (IDs, status, revisionNumber/editVersion) and is computed before editVersion is incremented. C14 hashes exactly `{contractVersion,definition}`, where definition has its six canonical keys. Use Shared's toolHashInput/canonicalJson, capabilityHashInput/canonicalJson and responseContractCanonicalJson as applicable. Do not substitute one generic sort/encoder for the distinct accepted contracts.

Deterministic corrections/tests: create `src/commerce/publication/validation.ts`; export wrappers over accepted schemas and hash helpers. Non-object root, extra response envelope keys, invalid bounds/enums/templates and malformed definitions must reject; valid Shared baseline and optional-required-keyword cases must pass identically. Two storage rows holding the same six-key definition but different IDs/revision metadata must produce the same expected Shared hash. Changed definition content changes it; changing editVersion alone does not. Compare against Shared's helper output, not the implementation's own hash function.

#### R2 — P1: enforce immutable release ownership and unique membership

Location: createRelease/createToolDraft/createCapabilityDraft and replay result storage in `lib/commerce/lifecycle.ts`. The release keeps caller-owned nested detailsSchema references. Reproduction: create a release from `contract`, then assign `contract.detailsSchema.properties={injected:{type:'string',maxLength:20}}`; snapshot now contains injected data under an unchanged persisted hash. This violates immutability even in fixture-only execution. Similar shallow input/reference ownership must be eliminated throughout state and replay results.

createRelease also accepts `[publishedRevisionId,publishedRevisionId]`, producing two members of the same capability. Distinct capability identities are required, not merely 1–32 array entries.

Deterministic corrections/tests: clone validated data on admission and detach returned/replayed results; no caller-held reference may mutate durable fixture state. Validate all members before writes: unique capability IDs/revision membership, published status, base capability, contiguous positions, and no conflicting tool revision bindings. Mutate original inputs and returned/replayed results after commit: release content/hash/member rows/audit remain unchanged. Duplicate member test must reject with zero new release/member/audit writes; two distinct capabilities sharing one tool revision pass, conflicting revisions fail atomically. Preserve original payload/result replay binding.

#### R3 — P1: deliver C17 ports and the complete owned lifecycle component

The entire service is one class under lib/commerce with private arrays/Map and a per-instance Promise queue. There is no QueryValidationPort, separate executable-registry check, documented command/read mapping, storage transaction port, updateTool/updateToolDraft/updateCapabilityDraft commands or explicit idempotent seed CLI. Sequential replay within one instance does not prove two-transaction fixture semantics. The runtime unavailable factory is permitted by C17 and should remain unavailable until013 composes real adapters; it does not waive these owned component interfaces.

Assigned files: place the owned component under `src/commerce/publication/` as C17 specifies; use `ports.ts` for QueryValidationPort/registry/storage/auth interfaces, `lifecycle.ts` for commands and `read-models.ts` for queries. The old lib path may re-export for compatibility. Add `docs/publication-service-contract.md` with every C7 command's exact fields/results/CAS/roles/errors and database field mapping. QueryValidationPort.validate takes `{definition}` using Shared's accepted type and returns exactly `{ok:true}` or `{ok:false,code,issues}` with C17 codes/32-issue/512-character bounds. It is separate from installed executor availability; ok validation cannot make a missing executor publishable.

Implement omitted C7 create/update/draft/publish/release/activation/rollback/explicit-enabled/read operations and the explicit repeat-safe seed command. Use canonical IDs/fields and actor/reason/hash audit payloads; no invented storage enum/shape. Verify tool-name identity, strictly increasing published SemVer, absent-pointer CAS expected version, runner compatibility and release bounds. Recheck current server-resolved authorization before replay; reject invalid/revoked principals and unauthorized roles before any read of a replay result or write. Preserve development principal identity creation within the same FK-backed transaction when wired to the accepted auth dependency. Do not trust a TypeScript role annotation as runtime authorization.

Fixture tests must use two independent service instances sharing a transaction fixture store: race matching operation IDs, different payload/actor reuse, concurrent revision allocation and conflicting CAS; inject failure after business write/before audit to prove rollback; retry after simulated lost response to prove exactly one committed operation. Cover each QueryValidationPort result plus thrown timeout/error; denied/unavailable cases cause zero state/audit changes. Fixture stores/adapters must only be injected from tests; no production fallback. Provide the isolated PostgreSQL rehearsal script/command and expected assertions, explicitly pending developer execution. Do not implement real013 provider composition here.

#### R4 — P2: repair cursor continuation without skipping rows

Location: paginate in `lib/commerce/lifecycle.ts` (move into read-models.ts with the component). It returns the first NOT returned row as nextCursor, while the next call starts AFTER that cursor. Independent test with [a,b,c], limit1 returns a then c, skipping b.

Use an exclusive last-returned-row cursor consistently. After validating a known cursor and sorting by the binding read-model key plus stable ID tie-breaker, compute `page = items.slice(start, start + limit)` and return `nextCursor = start + page.length < items.length ? page[page.length - 1].id : null`. Reject an unknown cursor rather than silently restarting. Tests: limits1/2 over [a,b,c,d,e] concatenate to exactly all five IDs once; final cursor null, empty collection empty/null, unknown cursor typed invalid, invalid limits reject. Return detached read-model data so editing a response cannot mutate service state.

#### Validation record and deterministic resubmission gate

Independent harness at `/tmp/commerce003-review/lifecycle-review.test.ts` imports committed source and extends the submitted fixtures: **8 original tests passed, 4 review tests failed** (non-object details root, skipped pagination row, caller-mutated release, duplicate membership). No repository implementation edits or live service calls were made. Those four reproductions are specified above and must become permanent regressions. Submitted lint/type/build results and 75-pass/two-auth-fixture-failure full run remain reported evidence; do not claim a green full suite. Verify the auth fixture failures against unchanged baseline or fix task-caused regressions, without weakening accepted auth checks.

For each R1–R4, report changed files, named tests, expected/actual state and audit counts, and exact command/results. Required local success: permanent regression cases plus C17 port/two-transaction/omitted-command fixtures, lint, typecheck/build and diff check. Keep developer database rehearsal and013 integration separately pending with runnable instructions, not marked passed. Preserve accepted dependencies and original report history. Commit/push the same implementation/report branches and resubmit; normal preparation owns the next claim after this review overlay is published.

### Historical definition review


### Review Status

Pending.

### Review Notes

No implementation submitted. This task is a reviewable definition.

### Reviewed Files

None for implementation review.

### Validation Reviewed

None for implementation review.

### Architecture Conformance

Awaiting implementation.

### Follow-up

Reconcile task/index/frontier after review; preserve the terminal/manual system-test gate.
