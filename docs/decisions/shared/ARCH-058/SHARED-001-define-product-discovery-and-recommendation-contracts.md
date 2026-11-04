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
status: ready
priority: 20
executor: null
claimed_at: null
attempt: 0
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

- [ ] Confirm actual accepted source baseline and inspect each existing grant/descriptor consumer in this repository.
- [ ] Implement the exact structural schemas/dictionaries and export names.
- [ ] Implement deterministic built-in descriptor payloads/constants and branch-aware grant helpers.
- [ ] Support nullable detail scalars in the bounded subset and prove the published recommendation schema compiles.
- [ ] Update common runner descriptor registration and authorization without changing terminal error behavior.
- [ ] Add meaningful negative/positive contract and runner tests and update affected fixtures/export checks.
- [ ] Run validation, record exact evidence and return for architect review without publication.

## Interfaces / Contracts

Normative source: `docs/architecture/ARCH-058/contracts.md`. No local alternative types in consumers. The trusted conversation tool context is populated by Background and interpreted by MCP domain adapters; it is not a model input and does not alter generic transport authentication. In particular, `builtInTools` defaults to[] for manifests that do not project built-ins, while the new grant union remains strict. Package target 4.0.0 is deliberately a major release because its inferred output/grant types change; runtime runner 1.1.0 is required by new discovery releases.

`CommerceProductRecommendationSelectionSchema` validates only the two owned detail fields; existing response contracts can retain other owned fields. Service validation decides whether both selection fields are required for a recommendation turn. Do not make every Commerce response a product recommendation.

## Dependencies

None. The architecture freezes the public contract before parallel Database work.

## Enables

- ARCH-058-SHARED-002
- ARCH-058-SYSTEM-TEST-001

## Acceptance Criteria

- [ ] Every named export is present through the existing compiled public entrypoint, with correct inferred types.
- [ ] Category inputs/outputs, new search shape, optional lookup and flat recommendation fields exactly match the normative contract and bounds.
- [ ] Actual subset compilation handles nullable details and the new search schema without `oneOf`, with only the specified details depth 5 increase and unchanged input depth 3.
- [ ] A valid mixed published/built-in grant is retained and authorized; invalid/unknown/duplicate/hash-changed shapes fail closed.
- [ ] Authorization and terminal-error/referral tests demonstrate no tool-list bypass and no error erasure.
- [ ] Existing accepted product/discount/output consumers' normal success fixtures remain valid; intentional type changes are documented.
- [ ] No npm publication, database/provider change, package version bump or unrelated index edit occurred.

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

Not started. Defined but not materialised; no implementation validation has run.

### Files Changed

To be completed by the executor with actual implementation paths.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None recorded.

### Assumptions

Snapshot Shared package 3.1.0 and runner 1.0.0 are the observed baseline; confirm accepted main at materialisation.

### Unresolved Issues

None at definition time; reconcile changed baselines before changing the frozen interface.

### Physical Worktree and Synchronization Evidence

Not materialised. Record real canonical root, parent/implementation worktrees, branches, synchronized heads, submodule state, commits and pushes only when they exist.

## Architect Review

### Review Status

Not reviewed; task definition only.

### Review Notes

Await implementation and evidence. No acceptance is implied.
