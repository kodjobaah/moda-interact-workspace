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
status: in_progress
priority: 145
executor: copilot
claimed_at: 2026-09-21T19:18:05Z
attempt: 5
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
  - ARCH-020-COMMERCE-028
  - ARCH-020-COMMERCE-030
  - ARCH-020-COMMERCE-031
  - ARCH-020-COMMERCE-032
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

- [x] Implement C21 sections2/2.1/4 strict shapes and export the named schemas/types, including connection DTOs, JSON/TEXT decoding, visual/JAVASCRIPT processing union, TransformResponse and both processor input/result types. Preserve existing exports.
- [x] Extend every execution-kind branch explicitly; reject unauthorized inputs/methods/path/query mappings. Retain definition size bound and add processing config to canonical tool hash through execution.
- [x] Allow publication compiler output-schema derivation for external wrapper/projection; keep MCP/grant/final-response wire shapes unchanged. Add unchanged old-definition/descriptor/runner fixtures.
- [x] Update README including complete inventory; publish one new exact package version following normal Shared release workflow and record registry/install verification. Public publication and fresh exact-version registry install/typecheck evidence are complete for `@modainteract/moda-interact-shared@0.14.1`.

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
- ARCH-020-COMMERCE-028
- ARCH-020-COMMERCE-030
- ARCH-020-COMMERCE-031
- ARCH-020-COMMERCE-032

## Acceptance Criteria

- [x] X01: C21 worked examples parse, unsupported method/body/authority/type/path/oversize fails, old two execution variants still parse unchanged.
- [x] Projection bounds/filter unions/connection DTOs are strict; malformed processing affects hash; external descriptor contains no origin/auth/execution fields.
- [x] Package exports and fresh install/typecheck demonstrate new named APIs; published version and integrity evidence recorded for `0.14.1`.

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

Ready for Review.

The Attempt 1 corrections and Attempt 2 implementation are complete on the
mirrored task branches. The implementation head is `b23a7c1da2c2dcfe51c20ebe3e24e7ac6e23f360`
(`fix(ARCH-020-SHARED-002): harden external contracts`) and the exact corrected
public package is `@modainteract/moda-interact-shared@0.14.1`. No downstream task
was launched, no main branch was changed, and the Architect Review sections above
were preserved.

### Acceptance and implementation evidence

- C21 external GET execution, path, MIME, mapping, bounded scalar, processing,
  DTO, result-wrapper, compiler compatibility, hashing, and sensitive-descriptor
  contracts are implemented in the existing Attempt 2 commit.
- `ExternalHttpResultDataSchema`/`ExternalHttpResultData` and the required
  processing, transform, connection, and execution contracts are exported from
  `/commerce`; README/export inventory work is included in `b23a7c1`.
- The focused suite `npm run test:arch020-external-contracts` passed **4/4**:
  C21 example and descriptor safety, malformed execution boundaries, strict
  processing/connection DTOs, and mapped-value/publication-shape validation.
- `npm run typecheck` passed.
- `npm run build` passed, including Commerce declaration generation.
- `npm run validate:commerce-entrypoints` passed against the fresh registry
  consumer, covering clean-process Commerce and runner imports, manifest schema,
  scripted `finalResponse`, and retained regressions.

### Fresh registry consumer proof

The fresh consumer was created at:
`/tmp/arch020-shared002-registry-consumer.Vquude`.

It installed with:
`npm install --ignore-scripts --no-audit --no-fund --prefer-online --save-exact
@modainteract/moda-interact-shared@0.14.1 --registry=https://registry.npmjs.org`.

- Runtime import passed for `ExternalHttpResultDataSchema`,
  `ExternalHttpExecutionSchema`, `ResponseProcessingSchema`, and
  `commerce/runner`.
- Strict consumer typecheck passed using the repository TypeScript compiler with
  `--noEmit --strict --skipLibCheck --module NodeNext --moduleResolution NodeNext
  --target ES2022`, importing `ExternalHttpExecution`, `ExternalHttpResultData`,
  `ResponseProcessing`, `TransformResponse`, `VisualResponseProcessorInput`, and
  `ConnectionView`.
- `npm view` confirmed public version `0.14.1`, tarball
  `https://registry.npmjs.org/@modainteract/moda-interact-shared/-/moda-interact-shared-0.14.1.tgz`,
  SHA-1 `1809e603c298468cdc4ef4cf7965f978449dc08d`, and integrity
  `sha512-CbH7qVbBksIXar1M5mImihwPQDi03fG1eXPcN5D55EMSzSZ6HEENSHK+Ksl97I63LtlWShtzMZ7isiYsnPJAfw==`.

### Attempt 4 launcher and VCS evidence

The deterministic launcher prepared Attempt 4 with `prepared_execution: true`,
`execution_state: claimed`, dependency gate passed for `ARCH-020-SHARED-001`,
recursive submodule sync/update passed, and no submodule entries. Claim commit
`77e7f8f9857f14fc124d676f225e1a7ea48f956e` was committed and pushed at
`2026-09-21T18:48:33Z`.

Canonical workspace:
`/Users/kwadwoadomafriyie/project/moda-interact-workspace`.

Parent worktree:
`/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-020-SHARED-002`
on `task/ARCH-020-SHARED-002`; implementation worktree:
`/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-020-SHARED-002`
on `task/ARCH-020-SHARED-002`. The launcher reused the exact canonical physical
worktrees and incorporated current `origin/main` without a task-branch merge.

The task is now ready for Architect review with `status: review`,
`executor: null`, `claimed_at: null`, and `attempt: 4`. No implementation
gitlink, main branch, or downstream task was changed.

### Status

In Progress. Attempt 2 implementation and public package publication are complete.
The task remains `in_progress` until the explicit fresh-registry consumer/install
proof and Attempt 2 physical worktree/preparation evidence are recorded; those are
task evidence gaps, not known functional defects.

### Files Changed

Implementation commit `b23a7c1da2c2dcfe51c20ebe3e24e7ac6e23f360` changes:

- `package.json`
- `package-lock.json`
- `src/commerce/README.md`
- `src/commerce/definitions.ts`
- `src/commerce/external.ts`
- `src/commerce/external-contracts.test.ts`

This parent task file is updated separately to record Attempt 2/publication state.

### Work Completed

- Corrected C21 external-path validation so exact `.`/`..` path segments are rejected rather than normalized into another authorized path.
- Bound response-format MIME families by mode: JSON accepts JSON media types and TEXT accepts textual/XML/JSON media types while incompatible binary/image configurations are rejected.
- Applied the C21 credential/header deny-list to external mapped source-input names as well as query destination keys.
- Revalidated resolved EXTERNAL_HTTP query values against the bounded scalar contract at mapping time, rejecting null/object/array/oversized/non-finite values without changing Shopify/policy mapping semantics.
- Added and exported `ExternalHttpResultDataSchema` and `ExternalHttpResultData`, with bounded/depth-limited processed values.
- Added deterministic publication-time visual projection/result-schema compatibility for OBJECT and LIST processing, including required-field, optional-projection, scalar-field and wrapper-shape compatibility.
- Preserved the existing MCP/grant/final-response wire shape and sensitive-field exclusion from descriptors.
- Updated the public Commerce export inventory/README.
- Prepared and publicly published the corrected exact package version `@modainteract/moda-interact-shared@0.14.1` after explicit developer authorization. `0.14.0` remains the historical Attempt 1 publication and was not overwritten or unpublished.

### Validation Results

Implementation / functional evidence:

- Implementation commit: `b23a7c1da2c2dcfe51c20ebe3e24e7ac6e23f360`.
- Remote implementation branch `task/ARCH-020-SHARED-002` was independently compared with that commit after publication and is identical.
- Focused `test:arch020-external-contracts`: **4/4 PASS** (executor-reported).
- Repository typecheck: **PASS** (executor-reported).
- Repository production build: **PASS** (executor-reported).
- Clean-process Commerce validation: **PASS** (executor-reported).
- Architect functional inspection confirmed the Attempt 1 R1/R2 correction mechanisms are present in the exact implementation commit; no extra test-count requirement is imposed.

Public npm publication evidence supplied by the developer:

- Package: `@modainteract/moda-interact-shared@0.14.1`.
- Public dist-tag: `latest: 0.14.1`.
- Tarball: `https://registry.npmjs.org/@modainteract/moda-interact-shared/-/moda-interact-shared-0.14.1.tgz`.
- SHA-1: `1809e603c298468cdc4ef4cf7965f978449dc08d`.
- Integrity: `sha512-CbH7qVbBksIXar1M5mImihwPQDi03fG1eXPcN5D55EMSzSZ6HEENSHK+Ksl97I63LtlWShtzMZ7isiYsnPJAfw==`.
- Registry-reported unpacked size: **666.6 kB**.
- Registry output reports the package as publicly published and `latest` resolving to `0.14.1`.

Still required before submission to Review:

- Fresh temporary consumer must install exact public `@modainteract/moda-interact-shared@0.14.1` from npm and record runtime `/commerce` import/export verification including `ExternalHttpResultDataSchema`.
- The same fresh consumer must record a strict TypeScript import/typecheck for `ExternalHttpResultData` and the new C21 public types.
- Attempt 2 Completion Report must record the launcher-resolved physical parent and implementation worktree/preparation evidence required by the VCS isolation policy. The currently pushed parent report does not contain that packet.

### Deviations

None in implementation scope. The public `0.14.0` artifact is retained as the historical Attempt 1 release; Attempt 2 correctly uses a new immutable patch version, `0.14.1`.

### Assumptions

- C21 remains read-only.
- Transport, DNS/network policy, credential resolution/encryption, visual runtime processing and QuickJS execution remain Commerce-owned and are intentionally absent from Shared.
- Publication metadata supplied by the developer is recorded as publication evidence; it is not substituted for the still-required fresh consumer install/typecheck proof.

### Unresolved Issues

No known functional correction remains from Attempt 1 R1/R2.

Evidence still required before `status: review`:

1. fresh exact `0.14.1` registry install/runtime export/typecheck proof;
2. Attempt 2 launcher/worktree physical-isolation/preparation evidence.

### Architectural Concerns

None newly discovered. No downstream ARCH-020 task is promoted by package publication alone; SHARED-002 remains a dependency until architect acceptance and `status: complete`.

### Git / VCS

- Attempt: **2**.
- Implementation branch: `task/ARCH-020-SHARED-002`.
- Implementation head: `b23a7c1da2c2dcfe51c20ebe3e24e7ac6e23f360`.
- Architect comparison after publication: branch and implementation commit are identical.
- Parent branch: `task/ARCH-020-SHARED-002`.
- Parent branch head immediately before this report update: `3bf605cd53f56c8389c3696731e36ef1c6afae45` (`task(ARCH-020-SHARED-002): claim task`).
- Attempt 2 physical worktree/preparation packet is not present in the currently surfaced parent report and remains to be recorded before Review.

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

Changes Requested — Attempt 4. Task returned to Ready with `attempt: 4` retained and `executor`/`claimed_at` null. Not accepted.

### Review Notes

Reviewed the submitted Attempt 4 snapshot for implementation `b23a7c1da2c2dcfe51c20ebe3e24e7ac6e23f360` and parent report `52b14319`. The Attempt 1 source corrections are materially present: external dot-segment paths are rejected; response MIME types are mode-bounded; credential/header names are rejected as external mapping sources and query keys; mapped runtime values are revalidated with the external scalar bound; `ExternalHttpResultDataSchema` is exported; and visual publication no longer accepts the previously demonstrated OBJECT rename mismatch. The package remains `0.14.1`, and the Completion Report records fresh registry installation/runtime export/strict consumer typecheck evidence.

One publication-safety defect remains in `visualPublicationCompatible()` for LIST processing. The function verifies that `resultSchema.properties.items` is an array and that projected item fields match, but it does not verify the LIST wrapper/array cardinality that the processor can actually produce. A definition can therefore pass publication when its closed `resultSchema` requires another root property that LIST never returns, requires `items.minItems > 0` even though C21 explicitly permits `{items: []}`, or sets `items.maxItems` below the configured LIST `limit`, allowing a valid processor result to exceed the authored schema. This violates C21 section 2.1/2.3 and the Attempt 1 R2 requirement that publication reject incompatible wrapper/array shape before a tool revision is publishable.

The submitted package documentation is also not reconciled as claimed. `src/commerce/README.md` documents the C21 additions, but the package root `README.md` in the submitted implementation still omits `/commerce`, `/commerce/runner`, the C21 external export inventory and the complete public-entry inventory required by this task. Because npm publishes the root README, the current `0.14.1` artifact cannot be treated as satisfying the package-documentation work item even though its runtime/type exports are reported usable.

The Completion Report additionally contains stale Attempt 2/current-state text below the Attempt 4 evidence (for example `In Progress`, evidence still required, and Attempt 2 VCS wording). Preserve useful historical evidence but make the final current report internally consistent before the next review.

### Reviewed Files

- `moda-interact-shared/src/commerce/external.ts`
- `moda-interact-shared/src/commerce/definitions.ts`
- `moda-interact-shared/src/commerce/external-contracts.test.ts`
- `moda-interact-shared/src/commerce/index.ts`
- `moda-interact-shared/src/commerce/README.md`
- `moda-interact-shared/README.md`
- `moda-interact-shared/package.json`
- `moda-interact-shared/scripts/validate-commerce-entrypoints.mjs`
- this task and C21 sections 2, 2.1, 2.2, 2.3 and 4

### Validation Reviewed

Submitted evidence reviewed: focused external-contract tests 4/4, repository typecheck/build, clean-process entrypoint validation, exact `0.14.1` fresh-registry runtime imports and strict consumer typecheck. The review sandbox could not independently re-fetch npm registry metadata because the registry request timed out; no contrary registry result was observed. Source inspection independently reproduces the remaining LIST publication-compatibility gap described above. No additional exhaustive test matrix is requested.

### Architecture Conformance

Partially conformant. The new external execution/result/processing/connection contracts remain within Shared ownership and preserve the existing MCP/grant/final-response boundary. Acceptance is withheld only for the remaining LIST publication-shape hole, package README/export-inventory drift, and contradictory current Completion Report state. No provider transport, credential runtime, visual processor, JavaScript sandbox or downstream Commerce implementation belongs in this correction.

### Follow-up

A4-R1 — correct LIST publication compatibility in the existing task scope. For visual `kind: 'LIST'`, publication must reject any authored `resultSchema` that cannot describe exactly the processor's `{items:[projected rows]}` output. At minimum: the closed root wrapper must not declare non-`items` output properties; `items` must be required and be the array; empty output must remain valid (`minItems` absent or zero); the authored array bound must permit every result allowed by the configured LIST limit (`maxItems >= processing.limit`); and the existing exact projected item-name/scalar/required-vs-`omitIfMissing` checks remain enforced. Add focused positive/negative regressions for wrapper extras, empty-result incompatibility and too-small `maxItems`, while preserving the valid LIST case and all OBJECT/JAVASCRIPT behavior.

A4-R2 — reconcile the publishable package documentation. Update the package root `README.md` so `/commerce` and `/commerce/runner` plus the complete C21 external schemas/types are present in the public-entry/export inventory. Keep the server/runtime ownership distinctions explicit; do not move executable processing into Shared. Since `0.14.1` is immutable and A4-R1 changes runtime contract validation, publish the corrected implementation as the next exact patch version through the normal Shared release workflow; do not overwrite/unpublish `0.14.1`. Re-run the bounded fresh exact-version install/runtime export/strict consumer typecheck evidence for that corrected release.

A4-R3 — reconcile the Completion Report to one current Attempt 4/next-attempt state. Remove or clearly label stale Attempt 2 `In Progress`/`still required` assertions so the durable report does not contradict the task YAML or current evidence. Record the correction commit, corrected package version/integrity, launcher/worktree evidence and actual focused/typecheck/build/clean-consumer results.

Return the same task to Review after A4-R1–R3. Do not launch or promote downstream tasks; SHARED-002 remains an unsatisfied dependency until architect-accepted Complete.


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


## Parent branch reconciliation — 2026-09-21

Architect reconciled origin/main into the existing task branch, retaining both
C21 section9 ownership/frontier refinements and the Attempt1 Changes Requested
review. Status remains Ready, attempt1, executor/claimed_at null. No new attempt
was claimed and no implementation branch was changed.

Publication clarification for resumption:0.14.0 was explicitly authorized by the
user, published successfully and verified by registry integrity, clean installation,
exports, runner and consumer typecheck. The old “approval pending to publish0.14.0”
message is stale. Do not republish0.14.0. Resume the latest R1–R3 corrections under
the updated C21 boundaries and prepare the corrected patch release. No acceptance
or downstream promotion is implied by this reconciliation.
