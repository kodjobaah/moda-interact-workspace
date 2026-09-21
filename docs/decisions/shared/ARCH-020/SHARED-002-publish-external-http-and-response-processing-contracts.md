---
id: ARCH-020-SHARED-002
architecture_id: ARCH-020
title: Publish external HTTP and response-processing contracts
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 145
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-020-SHARED-001
enables:
  - ARCH-020-COMMERCE-023
  - ARCH-020-COMMERCE-021
  - ARCH-020-COMMERCE-025
  - ARCH-020-COMMERCE-012
  - ARCH-020-COMMERCE-022
  - ARCH-020-COMMERCE-020
  - ARCH-020-COMMERCE-026
  - ARCH-020-COMMERCE-027
created: 2026-09-21
updated: 2026-09-21
---

# Publish external HTTP and response-processing contracts

## Architecture

ARCH-020. Binding specification: [C21 external API tools](../../../architecture/ARCH-020-external-api-tools.md).
Read C21 in full and existing [contracts](../../../architecture/ARCH-020-implementation-contracts.md)
C7/C14/C20 where extended. C21 resolves this task's exact fields, interfaces,
limits, errors, ownership and acceptance IDs. No model-selected replacement design.

## Objective

Own /commerce exported contracts, discriminated execution validation, argument mapping/hash/compiler contracts, DTOs and package documentation/publication. No provider transport, encryption or response-processing implementation.

## Context

The user approved read-only non-Shopify APIs, visual response filtering and sandboxed response code. Existing
Shopify/policy execution and Background MCP protocol remain supported. Future
external tool definitions require publication, not another Background handler.
This is new scope, not a correction to an accepted task.

## Scope

Own /commerce exported contracts, discriminated execution validation, argument mapping/hash/compiler contracts, DTOs and package documentation/publication. No provider transport, encryption or response-processing implementation.

## Out of Scope

Writes, OAuth, unsandboxed code, customer-specific lookups, live credentials or
WhatsApp sends, pricing/merchant feature overrides, automatic API discovery,
external-result caching and other owners' implementation files. No live deployment.

## Requirements

Use C21 named interfaces and bounded examples. All dependencies must be accepted
Complete before claim. Readiness is not execution. Component tasks may prove their
ports with fixtures; only024 and SYSTEM-TEST-002 claim real assembled flow.
Protect every UI command against double clicks, preserve same-operation retries,
and never expose secrets or raw external response data in errors/logs.

## Work Items

- [ ] Implement C21 sections2/2.1/4 strict shapes and export the named schemas/types, including connection DTOs, JSON/TEXT decoding, visual/JAVASCRIPT processing union, TransformResponse and both processor input/result types. Preserve existing exports.
- [ ] Extend every execution-kind branch explicitly; reject unauthorized inputs/methods/path/query mappings. Retain definition size bound and add processing config to canonical tool hash through execution.
- [ ] Allow publication compiler output-schema derivation for external wrapper/projection; keep MCP/grant/final-response wire shapes unchanged. Add unchanged old-definition/descriptor/runner fixtures.
- [ ] Update README including complete inventory; publish one new exact package version following normal Shared release workflow and record registry/install verification. Do not mark Complete on local build alone.

## Interfaces / Contracts

C21 is the shared contract between these tasks. Own only the paths identified
above. Record exact accepted dependency SHA/package version and source exports
in the Completion Report. No catch-all shared integration barrel. Return genuine
contract contradictions with a source reproduction; do not weaken validation.

## Dependencies

- ARCH-020-SHARED-001

## Enables

- ARCH-020-COMMERCE-023
- ARCH-020-COMMERCE-021
- ARCH-020-COMMERCE-025
- ARCH-020-COMMERCE-012
- ARCH-020-COMMERCE-022
- ARCH-020-COMMERCE-020
- ARCH-020-COMMERCE-026
- ARCH-020-COMMERCE-027

## Acceptance Criteria

- [ ] X01: C21 worked examples parse, unsupported method/body/authority/type/path/oversize fails, old two execution variants still parse unchanged.
- [ ] Projection bounds/filter unions/connection DTOs are strict; malformed processing affects hash; external descriptor contains no origin/auth/execution fields.
- [ ] Package exports and fresh install/typecheck demonstrate new named APIs; published version and integrity evidence recorded.

## Validation

Provide `test:arch020-external-contracts` in the owning repository and document its exact scope.
Run focused changed-boundary tests, then existing repository typecheck/build
and lint where defined. Inspect package scripts first; do not invent a claim that
an absent script passed. Use C21 controlled transports and isolated stores.
Follow current developer-owned live/container validation policy; clearly separate
actual agent results from required unrun developer checks. No arbitrary screenshot
quota or repeated full-suite runs without new changes/failures.

## Stop Condition

Submit implementation and parent report through normal mirrored task branches,
then stop at Review for moda_architect. Never self-accept, launch downstream tasks,
merge main, publish service deployments or update workspace service gitlinks.
Shared's package publication is required only for SHARED-002 as explicitly scoped.
SYSTEM-TEST-002 requires explicit developer invocation even when Ready.

## Implementation Notes

Use /moda-task launcher-resolved dedicated worktrees and preparation packet.
Task authoring on main is the user's documentation exception, not permission for
implementation on main. Preserve unrelated work and existing task claims.

## Completion Report

### Status

Not Started.

### Files Changed

None; task definition only.

### Work Completed

None.

### Validation Results

No implementation validation performed.

### Deviations

Definition authored on main under the user's existing instruction.

### Assumptions

C21 read-only scope; visual rules and generic JavaScript only inside the specified sandbox.

### Unresolved Issues

No implementation reported. Explicit dependencies gate execution.

### Architectural Concerns

Return contradictory accepted source facts to moda_architect before weakening contracts.

### Git / VCS

Expected mirrored branch: task/ARCH-020-SHARED-002. Attempt0; no implementation worktree or
commit claimed. At submission record physical isolation, dependency versions,
recursive database submodule evidence where applicable, commits and pushes.

## Architect Review

### Attempt 1 — Changes Requested (2026-09-21)

Reviewer: moda_architect. **Changes Requested; Ready, Attempt 1 retained; executor/claimed_at null. Not accepted.** The user requested review after public publication. Reviewed implementation `dfc9abf5134b33906cb825fce5c70043fb37a427`, current parent publication-evidence commit `6b18ffb7c1d4469ce4b56f9e20c8ca2e0cd24e27`, C21 and the task acceptance criteria. Both mirrored task heads match remote and both worktrees were clean before this overlay.

Publication of0.14.0 succeeded with explicit user authorization; registry integrity, clean installation, export-presence smoke, runner smoke and consumer type imports passed as recorded below. Those checks establish package delivery, not full C21 conformance. No unpublish, replacement of0.14.0, dist-tag change or implementation edit was performed.

Independent `npm run test:arch020-external-contracts`: **3/3 passed**. `/tmp/shared002-review.mjs`, copied into the fresh registry consumer as review.mjs, executes seven additional assertions against actual published0.14.0: **7 failed**, detailed below. Each definition mutation starts from a parsed valid external definition. Full163+one skipped/typecheck/build remain developer-submitted evidence; not rerun redundantly. No live provider was contacted. Existing publication evidence remains valid and preserved.

#### R1 — P1 — Enforce C21 path, MIME and mapped scalar boundaries

Files: `src/commerce/external.ts`, `src/commerce/definitions.ts`, `src/commerce/external-contracts.test.ts`.

1. `ExternalPathSchema` currently accepts `/catalogue/../admin` and dot segments generally. Add `value.split('/').every(segment => segment !== '.' && segment !== '..')` to the existing refinement. Preserve `/`, trailing slash and ordinary dots inside names; reject exact dot segments at all positions. Do not normalize them into a different authorized path.
2. `ExternalResponseFormatSchema` currently accepts JSON+image/png and TEXT+application/octet-stream. Keep existing lowercase/exact/no-wildcard/unique bounds, then refine by mode: JSON allows application/json or a concrete application subtype ending +json; TEXT allows a concrete text subtype, application/xml or a concrete application subtype ending +xml, plus the JSON set. Test accepted application/problem+json, text/html and application/atom+xml, and rejected image/png/octet-stream in their forbidden modes. Preserve0-parameter configuration; sample contentType may include charset per C21.2.3.
3. External query *keys* reject credential names, but mapped input names do not: query `{q:{input:'password'}}` with a declared string password input currently parses. Apply C21's case-insensitive credential/header list to external mapping source names as well as destination keys: authorization,cookie,set-cookie,host,x-api-key,api_key,apikey,access_token,token,secret,password. Keep existing authority exclusions and old execution contracts. No new endpoint/credential authority may arrive through renamed query keys.
4. `mapToolArguments` currently returns a2049-byte mapped string when inputSchema permits it; nullable scalar input can also map to null although external query values allow only string/finite number/boolean. After resolving each EXTERNAL_HTTP mapping, validate its actual value with the same bounded scalar contract used for literals (string<=2048 UTF-8 bytes, finite number, boolean; no null/array/object). Do not change Shopify/policy mapping semantics. Optional missing is omitted only with omitIfMissing:true; explicit null is not missing. Assert zero returned invalid mapping for oversized multibyte text/null and preserve valid0/false/empty string where allowed by input schema.

Acceptance includes positive controls plus each independent rejected path/format/key/source/value case. These are Shared contract checks; DNS, socket, credentials and live transport remain Commerce-owned.

#### R2 — P1 — Export the required external result contract and validate visual publication shape

Files: `src/commerce/external.ts` or `definitions.ts` as appropriate, `/commerce` exports, compiler/publication fixtures and README export inventory.

C21.2 explicitly requires `ExternalHttpResultDataSchema` and `ExternalHttpResultData`; both are absent from source and published export. Implement/export the strict data-only wrapper `{source:'EXTERNAL_HTTP',connectionRevisionId:IdSchema,observedAt:<existing timestamp schema>,values:<closed JSON object>}`. Preserve commerce.v1 outer result and enforce C21 processed-values48KiB/depth20 limits using existing bounded JSON validation. No transport, execution secret or new MCP protocol belongs in Shared. Add runtime and clean-consumer type checks for both required names; the prior export smoke omitted them and therefore did not establish the complete inventory.

`validateDefinitionForPublication` unconditionally accepts external mapped compilation via `validateMappedArguments:()=>true` and derives only resultSchema. It accepts OBJECT fields `{other:{path:'title'}}` while resultSchema requires `title`, with a template using `result.values.title`. No possible output of that projection satisfies the required shape. C21.2.1/2.3 requires publication rejection for incompatible projection names/array shape/types.

Perform deterministic static visual-shape compatibility before publication: OBJECT compares projected names with the closed resultSchema object; LIST compares with the closed object schema under values.items (the authored resultSchema's items property). Reject missing required names, impossible declared array/object projection values (visual projections are scalar), incompatible wrapper shape and undeclared output names. Account for omitIfMissing:true so a required output is not guaranteed by an optional projection. JAVASCRIPT uses its own runtime/sample validation owner; do not implement026 here. Keep the compiler extension boundary explicit rather than claiming a no-op validates projection compatibility. Include valid OBJECT and LIST publication plus one independent negative for each relevant incompatibility. Use resultSchema for derived template paths and preserve old Shopify/policy compiler behavior.

#### R3 — P2 — Finish acceptance evidence and prepare a corrected exact release

The task Completion Report still says Not Started/None and retains definition-only claims despite the implementation and publication appendix. Replace those placeholders with the actual implementation/validation/isolation/dependency/publication evidence, preserving the historical publication receipt and this review. The user asked for review before the owner completed submission; do not treat the old active claim or placeholders as acceptance.

Add focused assertions for processing changes affecting canonical tool hash, definition bounds, strict DTO/processing extra-field rejection, required result exports, and unchanged old execution definitions/descriptors/runner. Use existing tests where they already cover a case and name the exact case/command; no arbitrary test-count requirement. README must enumerate all new public schemas/types and distinguish contracts from runtime processing implementation. Report known C21 contradictions explicitly rather than weakening contracts.

0.14.0 is already immutable on npm. Prepare corrections as the next exact patch version through the normal Shared release workflow; do not republish/overwrite/unpublish0.14.0 or silently mark it architect-accepted. The user's prior explicit publication authorization named0.14.0; any new public release must follow its applicable release authorization. Complete and make the patch reviewable before requesting that final publication authorization if needed. No authorization question is being asked by this review overlay.

Run focused contract checks and repository-required typecheck/build, then clean packed/registry consumer verification for the corrected release, including the missing result schema/type. Return to Review with complete report and clear claims after publishing the authorized corrected version. No downstream prerequisite is satisfied by0.14.0's availability alone. No downstream tasks launched, main integration or gitlink change.

### Review Status

Pending.

### Review Notes

Definition only; no implementation acceptance.

### Reviewed Files

Not applicable.

### Validation Reviewed

Not applicable.

### Architecture Conformance

Awaiting implementation.

### Follow-up

Reconcile readiness/indexes after prerequisite acceptance; no automatic launch.


## User-authorized npm publication — 2026-09-21

The user explicitly authorized public publication of
`@modainteract/moda-interact-shared@0.14.0` after the earlier automatic approval
review rejection. Publication was executed from the prepared implementation at
`dfc9abf5134b33906cb825fce5c70043fb37a427`, matching its remote task branch.
No implementation source, version, main branch or gitlink was changed.

The release archive was rebuilt by the normal `npm pack`/prepack workflow and
contains75 entries: dist artifacts, README.md and package.json. Published the exact
archive with `npm publish /tmp/modainteract-moda-interact-shared-0.14.0.tgz --access public --registry=https://registry.npmjs.org`.
The command exited0 and reported `+ @modainteract/moda-interact-shared@0.14.0`,
public access, tag latest, and “Your package is being processed and may take a few
minutes to become available.” Do not republish this version solely because the
public lookup has not propagated.

Archive SHA-1: `f83a226ff80f3900048a63246e839624f588ca0b`.
Archive integrity: `sha512-6xC/cLnyWyeOpMHjTTH4mpWOJGnHx8K64Ldx7E2UYhhWxQp5aFf2GLhdvt9ZR6udmrZbf6zb6BcmvdFE6W+klw==`.

Registry availability and clean-install verification **passed** after npm processing
completed. Initial404/ETARGET responses were temporary; no republish occurred.
Independent `npm view` confirmed version0.14.0, dist.integrity and dist.shasum
exactly match the archive above. The user also confirmed latest=0.14.0.

A fresh temporary consumer installed the exact registry package using
`npm install --ignore-scripts --no-audit --no-fund --prefer-online --save-exact @modainteract/moda-interact-shared@0.14.0 --registry=https://registry.npmjs.org`.
The consumer had no previous package installation or workspace link.

- New /commerce external query/path/format, projection/filter/processing,
  TransformResponse/sample and connection DTO/schema exports: PASS. Valid JSON
  format accepted and unsupported XML format rejected.
- Existing `scripts/validate-commerce-entrypoints.mjs`, with
  COMMERCE_CONSUMER_DIRECTORY set to the fresh consumer: PASS for Commerce and
  runner imports, manifest schema, scripted finalResponse and retained regressions.
- Consumer .mts imports of new public contract types, checked with the repository
  TypeScript compiler using `--noEmit --strict --skipLibCheck --module NodeNext
  --moduleResolution NodeNext --target ES2022`: PASS. This validates consumer
  imports/types; skipLibCheck excludes dependency declaration internals.

Verification artifacts reside in the temporary consumer recorded by
`/tmp/arch020-shared002-consumer-path`; registry metadata is in
`/tmp/arch020-shared002-registry.json`. No provider, database or live service calls
were part of these package checks.

This entry records publication execution only; it is not architect acceptance or
a claim that SHARED-002 is Complete. Existing execution claim/status is preserved
for the owning task to finish its report and submission. No downstream launch.
