---
id: ARCH-058-SHARED-003
architecture_id: ARCH-058
title: Stabilize the accepted built-in contract runtime and verify packed consumers
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 35
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-058-SHARED-002
enables:
  - ARCH-058-SHARED-004
  - ARCH-058-SYSTEM-TEST-001
created: 2026-11-04
updated: 2026-11-04
---

# ARCH-058-SHARED-003: Stabilize the accepted built-in contract runtime and verify packed consumers

## Architecture

`docs/architecture/ARCH-058-commerce-agent-product-discovery.md`, `docs/architecture/ARCH-058/contracts.md` and the Shared hash reconciliation in `docs/architecture/ARCH-058/implementation-handoff.md`. Coordinator: `moda_architect`.

**Definition state:** defined but not materialised. This portable definition creates no branch, worktree, claim or implementation. Use `/moda-task ARCH-058-SHARED-003` after the definition is available to the normal launcher.

## Objective

Make Shared's accepted built-in payloads and validators use exactly Zod **4.4.3** independently of a consumer's dependency resolution, preserving the two existing built-in identities and all public source contracts. Add one reproducible packed-artifact check that proves the supported aligned consumer graph and the package's runtime isolation from a different direct consumer Zod. SHARED-004 separately owns the immutable **4.0.1** publication after architect acceptance.

## Context and selected decision

SHARED-002 is Complete. Its accepted source is `0b5567c3e01748de1d5d8c7d3be0d84a55dfb139`; its release metadata commit is `2489824bb879caa8c463fd857728078642dd1fd9`. The published `@modainteract/moda-interact-shared@4.0.0` artifact matches that task's immutable receipt. Its package declares Zod `^4.0.0`, while its accepted lock and validation used **4.4.3**. MCP-002 resolves the same published package against its direct **4.6.5** dependency.

The architect reproduced both reported hash failures from the actual registry artifact. Zod 4.4.3 reproduces the recorded hashes below; Zod 4.6.5 produces `6371003b0ade970987dabed9603d4efbfa8b653f801956252a86e5a3d7cca2b0` for options and `62c8d17c53d8a99add784e7c9d7a1226aaafb9b297592fee45c0c107ad508d38` for details. The generated datetime patterns differ, and details also differs in nullable primitive representation. This includes a real validator difference: the accepted 4.4.3 datetime parser permits a UTC minute timestamp that 4.6.5 rejects.

Pinning Shared alone also creates an unsupported TypeScript composition graph when a consumer still imports Zod 4.6.5. The architect reproduced TS2345/TS2769 at the existing schema-composition boundaries; aligned 4.4.3 and aligned 4.6.5 graphs compile. The selected repair preserves the accepted **4.4.3** contract semantics. MCP-002, COMMERCE-001 and BACKGROUND-001 own their coordinated exact 4.4.3 consumer pins. Those consumer pins also change the runtime used by their own direct Zod parsers; their existing focused parsing regressions and typecheck gates must run after alignment. This task does not certify those application changes. No new built-in hashes or definition versions are authorized.

| Identity | Required unchanged value |
| --- | --- |
| `commerce_get_discount_options` definition | `1.0.0` |
| Options contract SHA-256 | `a0a4a88c7920a25a31657a03761b6556419189aeab251261a58e2dfb83a3bdcb` |
| `commerce_get_discount_details` definition | `1.0.0` |
| Details contract SHA-256 | `776f6bc6ac1800c75744c2ffa7357f07a32be2b61309b1d71abf0493a2de316f` |
| Runtime runner | `1.1.0` |
| Shared package during this implementation task | `4.0.0` |
| Shared-owned Zod dependency after this task | Exact `4.4.3` |
| Subsequent approved publication target | `4.0.1`, owned by SHARED-004 |

## Scope and exact edit map

Only the Shared implementation checkout and this task's report are writable by this task.

| Path in `moda-interact-shared` | Required change |
| --- | --- |
| `package.json` | Change only `dependencies.zod` from `^4.0.0` to exact `4.4.3`; add `validate:commerce-consumer-artifact` with value `node scripts/validate-commerce-consumer-artifact.mjs`. Keep package version `4.0.0`, existing exports, scripts and other dependency declarations. |
| `package-lock.json` | Set the root package's Zod dependency to exact `4.4.3`. Preserve the already accepted `node_modules/zod` 4.4.3 record, including integrity `sha512-ytENFjIJFl2UwYglde2jchW2Hwm4GJFLDiSXWdTrJQBIN9Fcyp7n4DhxJEiWNAJMV1/BqWfW/kkg71UDcHJyTQ==`. Preserve package versions and every unrelated dependency record. |
| `scripts/validate-commerce-consumer-artifact.mjs` | Add the bounded, temporary packed-consumer check specified below. Reuse the existing commerce entrypoint verifier. |
| `README.md` | Amend the product-discovery/built-in contract section to identify exact Shared and composing-consumer Zod 4.4.3, the new validation command, and the separate publication task. Preserve the historical 4.0.0 release explanation and existing public export inventory. |

`src/**`, `tsup.config.*`, `tsconfig*.json` and the existing validation helpers remain unchanged. The dependency declaration and regression harness are the implementation. Generated tarballs, fixture installs and compiler files stay in task-owned temporary directories and are not committed.

## Requirements

### 1. Accepted baseline and narrow dependency update

Use the launcher's isolated Shared implementation worktree and its preparation evidence. Verify the prepared source contains the accepted SHARED-002 source/release metadata, package version 4.0.0 and the two identities above. An accepted later descendant is permitted only when it preserves these named surfaces; report a real conflicting change for architect reconciliation. Keep completed SHARED-001/002 records and their receipts intact.

Update the dependency with the repository's installed npm and inspect the structured package/lock diff. The existing lock already contains 4.4.3; no broad dependency refresh is needed. A lock writer that changes unrelated records must not have those unrelated changes committed. Use the existing Node bootstrap prerequisite before Node/npm commands:

```bash
command -v node >/dev/null 2>&1 || source "$MODA_WORKSPACE_ROOT/scripts/bootstrap-node.sh"
npm install --package-lock-only --ignore-scripts --save-exact zod@4.4.3
npm ci --ignore-scripts --no-audit --no-fund
```

Preserve `commerceBuiltInToolContractPayload` and its actual-schema canonicalization. Do not replace it with frozen JSON, normalize away schema differences, copy a consumer-local descriptor, overwrite literal hashes, alter a validator, change a trust check or introduce npm overrides/aliases/peer-dependency workarounds.

### 2. One reusable packed-artifact harness

Add exactly this CLI interface:

```text
npm run validate:commerce-consumer-artifact -- --tarball <absolute-existing-tgz-path> --expected-version <exact-package-version>
```

The script accepts exactly one value for each required flag and rejects unknown, duplicate, missing or empty flags. It requires an absolute regular tarball file and a plain exact semantic version. It reads the installed package metadata after installation and requires package name `@modainteract/moda-interact-shared`, the supplied exact version and `dependencies.zod === "4.4.3"`. It never publishes, changes repository package files or resolves `latest`.

Create two independent task-owned temporary npm projects with `type: "module"`. Each installs the supplied tarball as its only Shared package source. Declare direct Zod exactly as follows:

| Fixture | Direct Zod | Purpose |
| --- | --- | --- |
| `aligned` | `4.4.3` | Prove the supported public-schema composition used by MCP, Commerce and Background. |
| `foreign-runtime` | `4.6.5` | Prove Shared's own runtime hashes and validators stay on 4.4.3 even when another package version is present at the consumer root. This is not a supported cross-version TypeScript composition graph. |

Use the existing npm registry/authentication configuration, `--ignore-scripts --no-audit --no-fund`, explicit `cwd` and argument arrays with `shell: false`. Installation may fetch the exact fixture packages and the packed package's declared dependencies. Do not create source dependency symlinks, use repository `node_modules` to satisfy the artifact's runtime imports, inherit a provider/database configuration into runtime checks, or print registry credentials. Clean up both owned temporary trees in `finally`, including on failed installation or assertion. Preserve exit status/nonzero failures and print a bounded success/failure result per fixture.

Resolve dependency identity using `createRequire` anchored separately at the fixture package and at Shared's actual resolved public entrypoint. Read the Zod package metadata reached by each resolver; do not assume a fixed nested filesystem path. Require direct fixture Zod to equal its table value and Shared-resolved Zod to equal **4.4.3** in both fixtures. Record those identities, installed Shared version and both recomputed hashes in the result. The two fixtures must produce the original identical canonical payload strings and hashes.

Invoke the unchanged `scripts/validate-commerce-entrypoints.mjs` using the current Node executable and `COMMERCE_CONSUMER_DIRECTORY` set to each fixture directory. That helper already verifies the actual package's public contracts, both SHA-256 hashes, canonical descriptor schemas and runner 1.1.0 through fresh-process imports. Reuse it instead of copying those assertions into another validator. Its success is necessary in both fixtures.

### 3. Supported aligned composition and timestamp controls

Only the `aligned` fixture performs the consumer composition check. Install exact test-only `typescript@5.9.3` and `@types/node@24.19.1` in that temporary fixture, matching the current MCP consumer compiler/type baseline; do not add them to Shared's production dependencies or change Shared's existing compiler settings.

Write a temporary `.mts` consumer that imports its own `z` from `zod` and imports public Shared schemas through package exports. It must compile without casts, `any`, `@ts-ignore`, `@ts-expect-error` or changes to the fixed consumer compiler options below. Include these concrete existing boundary shapes:

- Define `z.input<typeof CommerceToolInputs.commerce_search_products>` and `z.output<typeof CommerceToolInputs.commerce_search_products>` and parse an empty raw input to the normalized output.
- Compose `z.object({offer: CommerceOfferSchema})` and parse an ordinary valid offer.
- Compose `z.array(MerchantKnowledgePurposeKeySchema).max(7).optional()` and `z.strictObject({purpose: MerchantKnowledgePurposeKeySchema, dataFormat: MerchantKnowledgeDataFormatKeySchema, languageTag: ModaSupportedLanguageTagSchema})` using the public `/merchant-knowledge` and `/internationalization` exports.
- Call the consumer's `z.toJSONSchema(CommerceToolInputs.commerce_resolve_product_categories, {io: "input"})` and its `z.toJSONSchema(CommerceToolOutputs.commerce_get_discount_options, {io: "output", unrepresentable: "any"})`.
- Compose `CommerceProductRecommendationSelectionSchema.extend({...CommerceAnswerPresentationSelectionSchema.shape, unrelated: z.string().max(20).optional()})` and parse `{}` and an ordinary `STANDARD` presentation with null shipping IDs.

Compile that fixture with the relevant existing MCP settings: `target: ES2022`, `module: NodeNext`, `moduleResolution: NodeNext`, `strict: true`, `noUncheckedIndexedAccess: true`, `exactOptionalPropertyTypes: true`, `esModuleInterop: true`, `skipLibCheck: true`, and `types: ["node"]`. The existing `skipLibCheck` setting does not suppress the real consumer-expression TS2345/TS2769 errors reproduced in this review; preserve it rather than creating an unrelated third-party declaration audit. Do not weaken any of these fixed options or suppress expression diagnostics. Emit only into its owned temporary directory, execute the emitted module, and require the search defaults `{query:null,browse:false,availableOnly:true,limit:10,cursor:null}` and successful ordinary composed-schema parses. Use fixture-local installed compiler files, not a global/npx-downloaded compiler. No mixed-version compilation success is asserted for `foreign-runtime`; the architect already established that composition is unsupported.

Both fixtures must exercise the actual packed Shared `DateSchema` and discount-options output with the following controls:

| Timestamp | Shared 4.4.3 result in both fixtures | Native fixture Zod 4.4.3 | Native fixture Zod 4.6.5 |
| --- | --- | --- | --- |
| `2026-11-04T12:00Z` | Accepted | Accepted | Rejected |
| `2026-11-04T12:00:00Z` | Accepted | Accepted | Accepted |
| `not-a-date` | Rejected | Rejected | Rejected |

For the native control use `z.iso.datetime({offset:false})`. For the real discount-output control parse `{mode:"AI_BEST_APPLICABLE", offers:[{offerId:"fixture-offer",title:"Fixture",method:"AUTOMATIC",code:null,startsAt:<timestamp>,endsAt:null,support:"SUPPORTED",reasonCodes:[]}],truncated:false}` with the packed `CommerceToolOutputs.commerce_get_discount_options`. This verifies preserved wire validation, not just JSON-schema serialization. Treat a different result as a blocking regression; do not alter the expected values to make a different dependency graph pass.

## Interfaces / Contracts

Existing `/commerce`, `/commerce/runner`, `/merchant-knowledge` and `/internationalization` exports and all public inferred types remain unchanged. This implementation retains package version 4.0.0 and prepares a compatible dependency correction; the separate publication task owns 4.0.1. Public-schema composition is supported with the coordinated exact 4.4.3 consumer pin. A foreign runtime fixture proves isolation of Shared's own behavior, not compatibility of foreign Zod schema composition.

## Dependencies

- `ARCH-058-SHARED-002`: accepted 4.0.0 source, release metadata and immutable artifact receipt.

## Enables

- `ARCH-058-SHARED-004`: publication of the architect-accepted dependency correction.
- `ARCH-058-SYSTEM-TEST-001`: provenance for the corrected contract graph, consumed after publication and application upgrades.

## Work Items

- [ ] Verify the accepted baseline and unchanged descriptor/schema/runner identities.
- [ ] Apply only the exact Zod declaration/lock correction and named validation-script addition.
- [ ] Implement the two-fixture artifact harness, reusing the existing entrypoint verifier.
- [ ] Verify the aligned strict TypeScript/runtime composition and both fixtures' timestamp/hash controls.
- [ ] Update the existing README section and record focused source/artifact validation.
- [ ] Submit the source and report for architect review without publication or consumer changes.

## Acceptance Criteria

- [ ] Shared resolves exact Zod 4.4.3 from its own published package metadata; the accepted locked Zod artifact and unrelated dependencies are preserved.
- [ ] Both existing descriptor hashes, definition versions, canonical payloads, public source schemas and runner 1.1.0 remain unchanged.
- [ ] Both packed-consumer fixtures pass the existing commerce entrypoint verifier and Shared timestamp controls; their resolver identities and hashes are recorded.
- [ ] The aligned graph compiles and executes the named real consumer composition shapes under strict checks. The foreign-runtime result makes no mixed-version type-compatibility claim.
- [ ] Only the four implementation paths in the edit map and this report change; package version remains 4.0.0.
- [ ] Required checks below pass or an exact blocking failure is reported. No registry publication, application upgrade, deployment or task-index edit occurs.

## Validation

After the dependency preparation above, run the existing focused source checks and one actual pack. The package's existing `prepack` performs the required build; an additional stand-alone build is unnecessary when that lifecycle succeeds.

```bash
npm run typecheck
npm run test:product-discovery-contracts
shared_hash_artifact_dir="$(mktemp -d "${TMPDIR:-/tmp}/moda-shared-contract-hash.XXXXXX")"
npm pack --json --pack-destination "$shared_hash_artifact_dir"
npm run validate:commerce-consumer-artifact -- --tarball "$shared_hash_artifact_dir/modainteract-moda-interact-shared-4.0.0.tgz" --expected-version 4.0.0
git diff --check
```

Record the actual package/lock diff, Node/npm/compiler versions, test counts and any existing optional Commerce-source integration skip truthfully. This dependency repair does not require provisioning or rerunning that separate integration, a full repository suite, Docker, PostgreSQL, provider traffic or a model. Inspect the tarball's metadata and required export targets. Record its SHA-256 and fixture results; it is a review artifact, not a published replacement for 4.0.0. A failed known source/artifact check remains blocking and must not be relabelled as an optional skip.

## Out of Scope

No application runtime source edits, replacement canonicalizer, frozen-schema workaround, changed hashes/definition versions, timestamp-schema redesign, new package subpath, runner change, obsolete conversation-context export cleanup, Database change, consumer pin, npm publication, persistent import, Commerce publication, Admin change, index edit or customer send. MCP-002's current attempt/claim and WIP are preserved. This task neither resumes nor completes MCP-002.

## Stop Condition

Stop for architect reconciliation if the accepted baseline, dependency identity, original hashes, timestamp controls or aligned public-schema composition cannot be preserved with the specified changes. Do not choose another Zod/package/descriptor version or expand runtime scope. After successful implementation and focused validation, complete this report, set this task to `review`, and return to the architect. SHARED-004 remains gated until this task is architect-accepted and Complete.

## Completion Report

### Status

Not started. Defined but not materialised; no implementation or execution claim.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run by this implementation task. Record actual commands, source and packed-artifact results, dependency identities, immutable artifact checksum, optional skips and owned temporary cleanup here.

### Deviations

None.

### Unresolved Issues

None beyond the explicit implementation and acceptance gates above.

## Architect Review

### Review Status

Pending.

### Review Notes

No implementation acceptance is granted by this portable definition.
