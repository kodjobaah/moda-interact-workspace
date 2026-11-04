---
id: ARCH-058-SHARED-001
architecture_id: ARCH-058
title: Define product discovery, built-in grants and recommendation contracts
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 20
executor: codex
claimed_at: 2026-11-04T05:03:01Z
attempt: 1
depends_on: []
enables:
  - ARCH-058-SHARED-002
  - ARCH-058-SYSTEM-TEST-001
created: 2026-11-04
updated: 2026-11-04
---

# ARCH-058-SHARED-001: Define product discovery, built-in grants and recommendation contracts

## Architecture

`docs/architecture/ARCH-058-commerce-agent-product-discovery.md`; normative interfaces: `docs/architecture/ARCH-058/contracts.md`, sections 1–5. Coordinator: `moda_architect`.

**Defined but not materialised.** No task branch, worktree, claim, commit, push or implementation exists by virtue of this definition. Materialise with `/moda-task ARCH-058-SHARED-001` under the existing workspace workflow. The empty dependency frontier makes this task ready; the frozen architecture contract, rather than a sibling checkout, is the implementation input.

## Objective

Give MCP, Commerce and Background one published contract for category resolution, category-aware merchant reads, optional lookup unavailability, explicitly authorized discount built-ins and identifier-only recommendation selection. Update the common runner to enforce those identities without weakening terminal errors or release grants.

## Context

In the snapshot, Shared 3.1.0 defines product search without category filters. Every granted tool and runner descriptor assumes a database-published tool/revision/capability. Built-in discount tools have an accepted options/details contract, but the conversational host cannot safely admit them through the published-only identity shape. The existing input/details JSON Schema subset also rejects union keywords and nullable details fields. These are concrete cross-repository blockers; they are addressed together before consumer implementation and separately from package publication.

Read `src/commerce/definitions.ts`, `schemas.ts`, `selection.ts`, `subset.ts`, `response.ts`, `runner/types.ts`, `runner/preflight.ts`, `runner/tools.ts` (or the actual current equivalent), `runner/version.ts` and current export declarations. Reconcile the accepted main baseline at task start. Accepted ARCH-052, ARCH-053 and ARCH-056 task histories remain intact.

## Scope

Paths below are relative to `moda-interact-shared`.

- Extend the existing `src/commerce/schemas.ts` dictionaries and named schema exports, `definitions.ts` descriptor/grant types, `selection.ts` equality/deduplication/availability and current manifest/grant validation code.
- Update `src/commerce/subset.ts` and its compiler only for bounded nullable scalar fields in details and the justified details depth 4-to 5 increase; keep input depth 3, all property/array/byte bounds and the rest of the existing JSON Schema subset. No general union support.
- Adapt `src/commerce/runner/**` only where its tool/descriptor registration, grant authorization, diagnostics or version assumes a published tool ID. Preserve execution budgets, cancellation, stale-turn handling, retry ceilings, tool result validation and referral state.
- Add a semantic `src/commerce/built-in-tools.ts` for code-owned descriptor constants and pure canonical-payload helper if needed; re-export it through the existing commerce entrypoint. Keep browser entrypoints free of Node crypto imports.
- Add focused contract/runner fixtures and tests; update affected existing fixtures to cover the deliberate new union. Update README export inventory and the existing commerce entrypoint verification script. Add one focused package test command if helpful, named `test:product-discovery-contracts`.
- Change the runtime runner version to 1.1.0 and eliminate any touched hard-coded observability version value in favor of the actual existing version export. Do not change npm package metadata; SHARED-002 owns the4.0.0 release gate.

## Out of Scope

No provider API/SDK calls, SQL, database migration, embedding/importer, discount eligibility engine, product ranking policy, host response composition, Commerce publication or consumer dependency upgrades. No new package subpath, customer-facing strings, Admin changes or index edits. Do not run `npm publish` here.

## Requirements

Implement exactly the contracts in sections 2–5, including the following public names:

- `CommerceCategoryCandidateSchema`, `CommerceCategoryCandidate`, `CommerceCategoryResolutionSchema`, `CommerceCategoryResolution`.
- `CommerceOptionalLookupUnavailableSchema`, `CommerceOptionalLookupUnavailable`.
- `CommerceBuiltInToolDescriptorSchema`, `CommerceBuiltInToolDescriptor`, `CommerceBuiltInToolGrantSchema`, `CommerceBuiltInToolGrant`.
- `commerceDiscountBuiltInDescriptors`, `commerceBuiltInToolContractPayload`.
- `CommerceConversationToolContextSchema`, `CommerceConversationToolContext`; keep the accepted outreach context unchanged.
- `CommerceProductRecommendationSelectionSchema`, `CommerceProductRecommendationSelection`.
- Updated existing `CommerceToolInputs`, `CommerceToolOutputs`, manifest/grant/descriptor inferred types and runner types through their existing entrypoints.

Preserve normal ARCH-052 discount success objects exactly. Add only the explicit unavailable branch; it is not an empty success, a new result envelope or a change to initial-outreach failure policy. Newly authored leaf schemas use strict structural constraints only. Applicability, cross-field request validity, recommendation scope, combination legality, expiry, current permission and amount calculations remain service policy.

The category input is the flat bounded object in the contract, not a Zod discriminated union that becomes unsupported `oneOf` in a published tool. Recommendation fields are flat; allow details depth 5 because the current validator counts the root as1 and a recommendation offer ID string as5. This one-level extension keeps offer IDs with their recommendation, without an additional cross-referenced selection structure. Input depth remains3. Preserve unrelated details fields and the existing 16KiB details limit. Nullable detail scalars must compile and validate through the actual subset path; merely adding a TypeScript type is insufficient. As contracts section 2 requires, string literals project to bounded single-item enums and fixed enums have explicit finite maxLength. The validator continues rejecting arbitrary const/oneOf keywords. Test the actual generated/projection schema, not a hand-built substitute that hides generator differences; Commerce owns its existing authoring projector.

Published and built-in grants form an explicit union. A built-in has no `toolId`, `toolRevisionId` or `capabilityKeys`. Keep published equality/provenance intact and include the allowed built-in set in retained-grant equality. Reject ambiguous/extra-key shapes, duplicate names, name collisions with published tools, changed contract hashes, unexpected names, extra permissions and overflow. The existing combined max 32 applies. A preflight parser success is not current authorization: the runner must still invoke the host's authorization checks before and after the relevant awaits.

Use deterministic canonical payloads and checked-in generated hash constants for the two descriptors, with tests recomputing from actual name/version/description/input/output schemas. Use the existing canonical JSON representation. No trusted descriptor may accept a hash supplied by a model, caller or arbitrary MCP registry. Keep the hash helper portable and reuse an injected digest/Node verification path where appropriate.

An optional operational `OK`/`UNAVAILABLE` branch allows a consumer to continue without a promotion or taxonomy candidate. An actual outer `ERROR` still sets the existing required referral and cannot be erased by a later success. Do not reinterpret denial, malformed output, stale grants or unexpected bugs as optional lookup outcomes.

The database has existing JSON guard/insert equality constraints on grants. DATABASE-001 owns their forward migration for this union; do not assume an unconstrained JSON column means no database work. Shared does not import Prisma or sibling source to model it.

## Work Items

- [x] Confirm actual accepted source baseline and inspect each existing grant/descriptor consumer in this repository.
- [x] Implement the exact structural schemas/dictionaries and export names.
- [x] Implement deterministic built-in descriptor payloads/constants and branch-aware grant helpers.
- [x] Support nullable detail scalars in the bounded subset and prove the published recommendation schema compiles.
- [x] Update common runner descriptor registration and authorization without changing terminal error behavior.
- [x] Add meaningful negative/positive contract and runner tests and update affected fixtures/export checks.
- [x] Run validation, record exact evidence and return for architect review without publication.

## Interfaces / Contracts

Normative source: `docs/architecture/ARCH-058/contracts.md`. No local alternative types in consumers. The trusted conversation tool context is populated by Background and interpreted by MCP domain adapters; it is not a model input and does not alter generic transport authentication. In particular, `builtInTools` defaults to[] for manifests that do not project built-ins, while the new grant union remains strict. Package target 4.0.0 is deliberately a major release because its inferred output/grant types change; runtime runner 1.1.0 is required by new discovery releases.

`CommerceProductRecommendationSelectionSchema` validates only the two owned detail fields; existing response contracts can retain other owned fields. Service validation decides whether both selection fields are required for a recommendation turn. Do not make every Commerce response a product recommendation.

## Dependencies

None. The architecture freezes the public contract before parallel Database work.

## Enables

- ARCH-058-SHARED-002
- ARCH-058-SYSTEM-TEST-001

## Acceptance Criteria

- [x] Every named export is present through the existing compiled public entrypoint, with correct inferred types.
- [x] Category inputs/outputs, new search shape, optional lookup and flat recommendation fields exactly match the normative contract and bounds.
- [x] Actual subset compilation handles nullable details and the new search schema without `oneOf`, with only the specified details depth 5 increase and unchanged input depth 3.
- [x] A valid mixed published/built-in grant is retained and authorized; invalid/unknown/duplicate/hash-changed shapes fail closed.
- [x] Authorization and terminal-error/referral tests demonstrate no tool-list bypass and no error erasure.
- [x] Existing accepted product/discount/output consumers' normal success fixtures remain valid; intentional type changes are documented.
- [x] No npm publication, database/provider change, package version bump or unrelated index edit occurred.

## Validation

Use the existing Node bootstrap prerequisite from the workspace instructions before any Node/npm command. Run in the isolated Shared implementation worktree.

1. Focused contract tests: valid/invalid category structures, query-null defaults, exact bounds, no business refinements, old discount normal successes and the explicit unavailable branch.
2. Subset tests: actual published category input and recommendation details compile; null Woo variant/basket-line values pass; unbounded/extra-key/unsupported schema variants and depth 6 details fail; input depth 4 remains rejected.
3. Runner tests: mixed grant success; altered hash/name/version/input schema, collision, missing descriptor, extra listed tool, wrong shop/turn and revoked current authorization fail. `OK` unavailable does not manufacture referral, while outer errors remain terminal through later successful calls. Check allowed tools are capped and the original cancel/deadline budgets remain effective.
4. `npm run typecheck`, `npm test`, `npm run build`, `npm run validate:commerce-entrypoints`. The latter exists in the snapshot; update it narrowly to include new exports. If an accepted baseline changes scripts, record the actual equivalent rather than inventing a command.
5. `npm pack --dry-run` to verify intended compiled JavaScript/declarations are included; no registry write. `git diff --check`.

Do not repeat broad tests solely to accumulate evidence after the concrete risks above are resolved. Record command/status and any blocked test honestly.

## Stop Condition

Set status to review and provide the completion report and actual task-branch/worktree evidence through the established workflow. Return to the architect and stop. SHARED-002 starts only after this task is complete and architect-accepted.

## Implementation Notes

Use semantic module/test/event names. Retain existing Shared logger/diagnostic structures and original caught errors; do not introduce a generic logger or silently swallow provider-shaped fixtures. Other repositories consume a released package after SHARED-002, never a relative import or unrecorded local link.

## Completion Report

### Status

Ready for Review — Attempt 1, codex, 2026-11-04. Implementation committed and pushed as `602417366ecab046757f3f84dbc7923e816b009b` on `task/ARCH-058-SHARED-001`. No package publication, merge to main or architect acceptance is asserted.

### Files Changed

```text
README.md
package.json
scripts/validate-commerce-entrypoints.mjs
src/commerce/README.md
src/commerce/built-in-tools.ts
src/commerce/definitions.ts
src/commerce/fixtures.ts
src/commerce/index.ts
src/commerce/product-discovery-contracts.test.ts
src/commerce/product-discovery-projection.test.ts
src/commerce/response-contracts.test.ts
src/commerce/runner/built-in-tools.test.ts
src/commerce/runner/observability.ts
src/commerce/runner/preflight.ts
src/commerce/runner/runner.test.ts
src/commerce/runner/tool-execution.ts
src/commerce/runner/tool-policy.ts
src/commerce/runner/version.ts
src/commerce/schemas.ts
src/commerce/selection.test.ts
src/commerce/selection.ts
src/commerce/subset.ts
```

### Work Completed

- Added every named schema/type export for category candidates/resolution, optional lookup unavailability, trusted conversation tool context, built-in identities and identifier-only recommendation selections through the existing commerce entrypoint.
- Extended the input/output dictionaries with category resolution and flat category-aware search. Query defaults to null; existing price, availability, limit and cursor behavior remains. Get-product validators and normal discount success shapes remain unchanged. Only the explicit unavailable alternative was added to discount outputs.
- New recommendation/category fields enforce structural bounds only. Candidate ordering, outcome/count relations, provider category validity, recommendation/offer relationships and applicability remain service policy. Recommendation fields are optional owned details fields; ordinary Commerce responses remain valid.
- Added immutable canonical discount descriptor constants with the exact required descriptions. Their generated hashes cover canonical JSON of name/version/description/input schema and the actual generated Shared output schema. The portable payload helper uses no Node crypto; Node tests independently recompute both hashes from actual schema members.
- Published grants retain their existing identity/provenance shape. Built-ins use only their distinct kind/name/version/hash branch, with no fabricated tool/revision/capability IDs. Strict parsers reject extra/ambiguous shapes; manifest validation binds exact canonical descriptors and the complete published-plus-built-in union, with unique names and a combined maximum of 32.
- Equality/deduplication/availability deliberately distinguish branches. Availability requires an explicit currently permitted canonical built-in set; the default cannot add built-in permission. Published provenance and release/capability equality remain intact.
- Common runner registration, advertisement and execution now handle both descriptor branches. Extra/duplicate/overflow registrations fail closed; built-in adapters must be present and exact. Current host authorization is checked during advertisement, before execution and after awaited execution. Descriptor drift across model/authorization awaits fails closed. Code-owned built-in outputs are validated against their actual dictionary schema.
- Optional `status: OK` unavailable data does not manufacture a referral. Hard outer errors retain required referral through later success; stale turns remain terminal even alongside revocation. Existing call/token/deadline/cancellation ceilings and two-attempt retry limit remain.
- Details subset depth is now five and bounded nullable detail scalars compile through the actual subset path. Input depth stays three; scalar/property/array/schema-size/result-size limits and arbitrary const/oneOf rejection remain.
- Runner version is 1.1.0 and observability reads its existing version export. Added the trusted taxonomy/products policy-operation metadata; actual provider executors remain MCP-owned.
- Updated documentation, existing affected fixtures and clean-process export verification. Package version remains 3.1.0, with unchanged name, dependency versions, lockfile and subpaths. The separate release task owns the coordinated 4.0.0 gate.

### Validation Results

| Command / gate | Result |
|---|---|
| `npm run test:product-discovery-contracts` | 17 passed, zero failures/skips |
| `npm run typecheck` | passed |
| `npm test` | 424 passed, zero failures, one existing optional live-Redis test skipped |
| `npm run build` | passed, JavaScript and declarations generated |
| `npm run validate:commerce-entrypoints` | passed in clean subprocess without provider/database credentials |
| `npm pack --dry-run` | passed; 131 intended files; commerce and runner JavaScript/declarations included |
| Browser-platform bundle of `src/commerce/index.ts` | passed, 159 source/dependency inputs; no Node-only import requirement |
| `git diff --check` and staged diff check | passed |

The focused tests are a subset of the full suite, not an additional distinct total. The single full-suite skip is the existing native BullMQ trace-context test gated by `TEST_REDIS_URL`; no required discovery/built-in/subset case was skipped. No Redis or PostgreSQL integration is required by this contract-only task.

Commands ran in the isolated implementation worktree after the workspace Node bootstrap. For both focused and full tests, the explicit test-only prerequisite was:

```sh
export COMMERCE_CONTRACT_SOURCE_ROOT="$MODA_WORKSPACE_ROOT/moda-interact-commerce"
npm run test:product-discovery-contracts
npm test
```

The actual existing Commerce `createPolicyOperationAuthoringDescriptor` receives candidate Shared validators as function arguments. Tests execute its real Zod JSON Schema generation/default stripping/nullable normalization, its real `policySchemaFromJson` renderer projection and its actual publication validation with the current Nunjucks template format. Compiler/execution transport is a controlled port; this does not claim an MCP executor is already deployed. No local link, consumer package upgrade, copied projector or hand-built replacement publication schema was introduced.

The actual generated category/search input schemas pass bounded input validation/publication. The generated selection details compile at depth five with null variant/basket-line values and finite bounded enums, including the single-value version enum. Depth six, input depth four, unbounded fields, unknown keys, unsupported nullable object/array types and const/oneOf variants fail. Existing runtime details-byte overflow coverage still passes at the unchanged 16KiB limit.

The direct contract fixtures exercise exact ID/string/array/quantity/distance bounds, query-null defaults, preserved discount normal successes and strict unavailable alternatives. Deliberately inconsistent business relationships remain structurally valid for the service to decide. Mixed grants, canonical hashes, unknown names, changed hashes/versions/schemas, duplicate/colliding names, extra permissions and combined overflow fail closed.

Runner fixtures cover mixed success, optional unavailable continuation, persistent hard-error referral, malformed outputs, original thrown tool failures, wrong shop/conversation/turn, current revocation before/after execution, adapter/descriptor drift, missing built-in adapter, extra registrations, stale-turn precedence, cancellation, deadlines and call ceilings. Existing prompt-injection/OpenRouter fixtures now separately assert that an ungranted registered adapter fails preflight before continuing their unchanged hostile-runtime-data/referral scenario.

#### Generated built-in hashes

| Built-in | Canonical SHA256 |
|---|---|
| `commerce_get_discount_options` | `a0a4a88c7920a25a31657a03761b6556419189aeab251261a58e2dfb83a3bdcb` |
| `commerce_get_discount_details` | `776f6bc6ac1800c75744c2ffa7357f07a32be2b61309b1d71abf0493a2de316f` |

Both focused tests and the compiled public entrypoint verifier recompute these hashes using Node SHA256 over the exported pure canonical payload. Descriptor input schemas equal the actual Commerce projection of the Shared input members; output schemas equal actual `z.toJSONSchema` output for the corresponding Shared output member.

#### Source/build provenance

- Implementation start: `5bc7711d94201dbc0538373a35c943da780ae125`; end/pushed: `602417366ecab046757f3f84dbc7923e816b009b`.
- Source package baseline and final metadata: `@modainteract/moda-interact-shared@3.1.0`. Runtime runner: 1.0.0 → 1.1.0.
- Node: 24.19.0 through the workspace bootstrap; locked Zod: 4.4.3.
- Actual Commerce projector/publication source checkout: `/Users/kwadwoadomafriyie/project/moda-interact-workspace/moda-interact-commerce`, HEAD `1b30ed9cf03ac85d04eb9e1502ae5463817c17f2`; the three consumed source files were clean and unmodified. Its installed Shared dependency remains unchanged; candidate validators are only test function arguments.
- Generated build output is ignored and not committed; package dry-run writes no registry state and no package version was changed.

| Shared source/artifact | SHA256 |
|---|---|
| `src/commerce/built-in-tools.ts` | `fc77616161ec2aacc0c41446f6d77e76801ea12b3e0682119d6692653ba8e5d9` |
| `dist/commerce/index.js` | `230d114af36cca05723e13df0e6b1e7e78e87404a095c27c4e4ed6d0123e98b9` |
| `dist/commerce/index.d.ts` | `65b8734feb5fd5e5dd895fd0a21d495d591b1120e82fdf310850400fbef23ac2` |
| `dist/commerce/runner/index.js` | `a9c86c4e9c6aac14bbfaa25356ff56c63ae0f464addf73fc7e55dee479140c9d` |
| `dist/commerce/runner/index.d.ts` | `6098db4aad5155b8161f18f74502f86cd0f70749a473b1866421b9ebaa55d08b` |

| Actual Commerce test prerequisite | SHA256 |
|---|---|
| `src/commerce/execution/policy-operation-authoring.ts` | `306105bcc30b4fd4cf6c03d9b5bf17363285088390315363878333054585d608` |
| `src/commerce/execution/policy-result-schema.ts` | `103195938924b2c5c0b01ddf05c0e6bc660a800b8455ba84f4303a93f571ae74` |
| `src/commerce/tool-definition/publication.ts` | `a056e6b5869a35b7ca6bf78380d2caab5cde635d56fbd5697ae89efff993edaa` |

Complete local command logs: `/tmp/shared058-{focused,typecheck,tests,build,entrypoints,pack,browser}.log`. Source was committed unchanged after these checks.

### Deviations

The first actual-publication fixture used the historical text template shape and raw generated result schema. It was corrected to use the existing Commerce Nunjucks format and actual renderer projection; no consumer implementation was modified or validator weakened. Existing nullable-string rejection and extra-registry fixtures were adapted to the intentional contract changes, retaining unsupported-union and hostile-data coverage. Initial failures were resolved before the passing required runs above.

### Assumptions

Service owners implement current tenant/turn/grant/expiry/permission, category/purchase applicability and grounded recommendation composition. A structurally valid contract is not authorization. DATABASE-001 must update its existing JSON grant guards in a forward migration before consumers persist the new union; this task makes no persistence-readiness claim.

The optional actual-Commerce source prerequisite is explicit and portable; absent that checkout, the test reports a skip. It was present and executed for this submission. Real-model retrieval quality, provider category semantics and corpus/database behavior are not assessed here.

### Unresolved Issues

None in this bounded Shared implementation. Architect review and the separate publication/consumer tasks remain pending. SHARED-002 was not started or promoted.

### Physical Worktree and Synchronization Evidence

```text
canonical primary workspace: /Users/kwadwoadomafriyie/project/moda-interact-workspace
parent task worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-058-SHARED-001
implementation worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-058-SHARED-001
both task branches: task/ARCH-058-SHARED-001
parent synchronized head before claim: 416e292bce611ddad3bdced2daa33f57e038bc0e
implementation synchronized head before claim: 5bc7711d94201dbc0538373a35c943da780ae125
parent remote task branch fast-forward: not-needed
parent origin/main incorporated: already-current
implementation remote task branch fast-forward: not-needed
implementation origin/main incorporated: already-current
final parent synchronization/re-gate: already-current; dependency gate passed
Attempt 1 claim commit: a1f015f4a5b22bbdbddca5d73070591f3afde1dd
claim committed and pushed: yes
claimed_at: 2026-11-04T05:03:01Z
parent and implementation worktrees newly created: yes
recursive submodule sync/update: passed
recursive implementation submodule entries: none
shared workspace/source checkout switched or mutated for task implementation: no
another task worktree reused: no
implementation parent gitlink staged or changed: no
main merged/updated/pushed: no
npm publication: no
```

## Architect Review

### Review Status

Not reviewed; task definition only.

### Review Notes

Await implementation and evidence. No acceptance is implied.
