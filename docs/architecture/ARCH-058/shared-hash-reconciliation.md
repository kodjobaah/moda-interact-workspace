# ARCH-058 revision 9: Shared descriptor hash reconciliation

**Decision: preserve the Shared commerce work and correct the dependency graph.** Pin Shared and the three applications that compose its public schemas to exact **Zod 4.4.3**. Publish the accepted Shared packaging correction as immutable **4.0.1**. Keep the two discount descriptor hashes and `definitionVersion: "1.0.0"`, all public schemas/exports, runner **1.1.0** and the accepted Database grant guard unchanged.

This is a portable architectural reconciliation and complete task handoff. The new tasks are **defined but not materialised**. No corrected source has been implemented, accepted, published or installed by this review. The existing MCP-002 claim and draft are preserved; they resume after the new source/publication gates complete. The [machine-readable evidence](shared-hash-reconciliation-evidence.json) contains the exact artifact identities, diagnostic scripts, dependency graphs, canonical payloads and structural differences behind this decision.

## 1. Current source and task state

The current baseline is the supplied `moda-interact-workspace-ARCH-058-MCP-002.zip`, SHA-256 `49ec33bd730f6a1a54e96c8b29e0fcf170c48039b7c5d2c16a4b3e5dace70a9a`. Accepted Shared source/package metadata were also inspected in the earlier merged `moda-interact-workspace(20261104-125409).zip`; source paths and content hashes are labelled separately in the evidence file.

The newer uploaded MCP-002 report records its unfinished implementation as committed and pushed at `4bffa87ed4af0fb40513ad75d38df49c51746360`. That is newer than the user's quoted `a30d96ac` blocker report. The archive does not independently prove live remote ancestry; these commit identities are taken from its task evidence. No rollback to the earlier blocker state is appropriate.

| Item | Current state | Consequence |
| --- | --- | --- |
| MCP-001 | Complete, accepted Attempt 3, implementation `1dd5430b9d3108bf93bba86c1fb9233736f606d3` | Preserve importer, resolver, manifest and accepted evidence. |
| MCP-002 | `in_progress`, Attempt 1; executor `codex`; claimed at `2026-11-04T15:08:56Z` | Keep existing claim `f4250e2e68a71626b36c456e901077fec656fb96` and both dedicated worktrees. |
| MCP-002 WIP | Reported draft `4bffa87ed4af0fb40513ad75d38df49c51746360`, 40 source/test files | Preserve all source/test bytes; finish and validate the existing implementation after the dependency gate. |
| Database | Resolved accepted pin `ded8f14a60182f6b1443640f012caf0089b8a44c` | No migration, rollback, replacement schema or repeat pin repair. |
| Shared 4.0.0 | Historical accepted immutable artifact | Retain its receipt. Correct it through a new immutable publication. |

All existing task lifecycle fields and actual Completion/Architect Review evidence are preserved. The unexecuted MCP-003/Background report templates are updated only to name the corrected dependency pair. SHARED-002 receives only the reverse dependency edge to the new correction task. MCP-002 receives the explicit SHARED-004 dependency while remaining in progress; no claim/attempt reset is implied. SystemTest's exhaustive prerequisite set expands from nine to eleven; its ten deterministic scenarios and one optional quality scenario do not change.

## 2. Confirmed cause

The MCP check uses the correct exported helper:

```js
createHash("sha256")
  .update(commerceBuiltInToolContractPayload(descriptor))
  .digest("hex");
```

Shared's own source test uses the same calculation. The helper canonicalizes the descriptor name, version, description, input schema and a runtime-generated output schema from `z.toJSONSchema(CommerceToolOutputs[name], { io: "output", unrepresentable: "any" })`. Its hash constants are fixed, but its published `zod` dependency is `^4.0.0`.

Accepted Shared's source lock used **4.4.3**. MCP's actual lock declares direct **4.6.5** and has no nested Shared Zod copy. The permitted hoisted 4.6.5 therefore changes the output schema used by Shared's exported helper.

The independent diagnostic downloaded the exact 4.0.0 registry tarball, verified both SHA-256 and SHA-512 against the historical receipt, and used the same unchanged artifact in each dependency graph. Non-Zod dependencies were kept identical and checked against the accepted lock. The artifact SHA-256 is `57f7511ae9e52eebac5f532f0cd787c6a391361520f1fc0d09386312fb3d276e`; size is 287127 bytes. This establishes dependency-sensitive behavior rather than an altered Shared tarball.

| Descriptor | Recorded/accepted SHA-256 | Recomputed with Zod 4.6.5 |
| --- | --- | --- |
| `commerce_get_discount_options` | `a0a4a88c7920a25a31657a03761b6556419189aeab251261a58e2dfb83a3bdcb` | `6371003b0ade970987dabed9603d4efbfa8b653f801956252a86e5a3d7cca2b0` |
| `commerce_get_discount_details` | `776f6bc6ac1800c75744c2ffa7357f07a32be2b61309b1d71abf0493a2de316f` | `62c8d17c53d8a99add784e7c9d7a1226aaafb9b297592fee45c0c107ad508d38` |

Both 4.6.5 values reproduce the user's failure exactly. Both recomputations equal the original constants when Shared resolves 4.4.3. The options payload changes from 2278 to 2268 UTF-8 bytes; the details payload changes from 7193 to 7021 bytes.

`isTrustedCommerceBuiltInDescriptor(...) === true` is insufficient to dismiss the failure: that helper compares with the installed descriptor constants. It does not independently recompute their payload hashes. Keep the independent integrity assertion.

### The schema difference includes validation semantics

The structural diff identifies two changes:

- Datetime regexes on offer `startsAt`/`endsAt` and details `observedAt`/`unavailableAt` become stricter about seconds.
- Several nullable primitive schemas in details change from `anyOf` objects to a `type` array.

The actual exported `CommerceOfferSchema.shape.startsAt` was probed, not a locally recreated contract:

| Timestamp | Shared with Zod 4.4.3 | Shared with Zod 4.6.5 |
| --- | --- | --- |
| `2026-11-04T10:00Z` | Accepted | Rejected |
| `2026-11-04T10:00:00Z` | Accepted | Accepted |

This is not wholly cosmetic serialization. Keeping an old frozen JSON payload while allowing newer runtime validators would attest a timestamp contract the newer validator does not implement. The correction restores the accepted generator and validator together.

### Shared's Zod dependency is also a public type boundary

A private Shared 4.4.3 installation with an application still on 4.6.5 restores runtime hashes but fails real schema composition. Shared exports Zod schema types. MCP passes its merchant-knowledge enums to its own `z.array` and its taxonomy schema to its own `z.toJSONSchema`. These declarations encode `_zod.version.minor` literally.

The diagnostic compiled identical fixtures with TypeScript **5.9.3** and the relevant MCP strict options, including its existing `skipLibCheck`. Mixed versions produce **TS2345/TS2769**, because literal minor `4` does not satisfy minor `6`. The errors occur in consumer expressions; `skipLibCheck` cannot make those expressions compatible.

| Consumer Zod | Shared-resolved Zod | Both original hashes | Actual schema-composition typecheck |
| --- | --- | --- | --- |
| 4.4.3 | 4.4.3 | Pass | Pass |
| 4.6.5 | 4.6.5 | Fail, exact reported values | Pass |
| 4.6.5 | Nested 4.4.3 | Pass | Fail, TS2345/TS2769 |

Runtime array/object parsing, the real taxonomy input projection/normalization followed by `InputSchemaSchema.parse`, and `ZodError` recognition passed in the tested graphs. Runtime success does not replace the failed declaration check. The approved applications therefore use **aligned exact 4.4.3**. Legitimate private transitive copies that do not participate in Shared-schema composition are outside this alignment; do not impose a global npm override.

The source audit found relevant MCP SDK, LangChain and OpenAI dependency/peer ranges permit 4.4.3. This is a lock/metadata observation, not a substitute for the owners' final package installation, focused tests and actual application typecheck. Changing a consumer's own Zod version can also change its locally declared schemas, so those existing validations remain mandatory.

## 3. Selected correction and ownership

| Owner | Exact change | Preserved contract |
| --- | --- | --- |
| [SHARED-003](../../decisions/shared/ARCH-058/SHARED-003-pin-built-in-contract-schema-runtime.md) | Pin Shared runtime `zod` from `^4.0.0` to `4.4.3`; update lock root metadata; add one packed-consumer regression harness using the existing commerce entrypoint verifier | Source package version remains 4.0.0 during implementation; schema/descriptor/runner source unchanged |
| [SHARED-004](../../decisions/shared/ARCH-058/SHARED-004-publish-contract-hash-runtime-fix.md) | After source acceptance, change release metadata to 4.0.1, inspect/publish exact tarball, retrieve it and verify the same artifact through the accepted harness | Original 4.0.0 receipt; no consumer upgrades in the publication task |
| [MCP-002](../../decisions/mcp/ARCH-058/MCP-002-ground-merchant-products-and-discounts.md) | After accepted release, exact Shared 4.0.1 and direct Zod 4.4.3 in its existing package/lock; rerun unchanged hash assertions and actual composition/typechecks | Existing claim, draft, accepted Database and taxonomy work |
| [MCP-003](../../decisions/mcp/ARCH-058/MCP-003-read-merchant-shipping-information.md) | Inherit the accepted corrected MCP-002 graph | Shipping implementation decisions unchanged |
| [COMMERCE-001](../../decisions/commerce/ARCH-058/COMMERCE-001-provision-standard-product-discovery.md) | Exact Shared 4.0.1 and direct Zod 4.4.3 in its already owned upgrade | Capture/reuse original pre-upgrade legacy fixture; preserve actual projection/publication tests |
| [BACKGROUND-001](../../decisions/background/ARCH-058/BACKGROUND-001-ground-product-and-discount-recommendations.md) | Exact Shared 4.0.1 and direct Zod 4.4.3 in its already owned upgrade | Host/grant/control boundaries, prompts and existing validation |
| [SYSTEM-TEST-001](../../decisions/system-test/ARCH-058/SYSTEM-TEST-001-validate-standard-product-discovery.md) | Require both corrective tasks and verify the installed applications' receipt/resolved graph | No new application source, Shared/Zod dependency of its own, or scenario IDs |

Shared 4.0.1 is a backwards-compatible packaging repair restoring the accepted schema/identity, consistent with Shared README's patch-release policy. The exact registry version endpoint returned HTTP 404 during this read-only review. SHARED-004 must check availability again immediately before publication; a conflict returns to the architect rather than silently choosing a version. No 4.0.1 integrity, source acceptance or publication receipt exists at definition time.

Both discount names, descriptions, input/output schemas, `definitionVersion: "1.0.0"`, original hashes, runner 1.1.0 and public exports remain fixed. The previously noted unused `CommerceConversationToolContextSchema` cleanup stays separate. There is no Database change or grant rewrite in this repair.

## 4. Why broader alternatives are not selected

A wholesale revert would remove accepted grants, discovery/shipping/presentation schemas and runner behavior needed by the ongoing consumers. The evidence identifies a dependency defect, not grounds to discard those features.

Changing the two hashes to the values from today's consumer while retaining the same descriptor version would silently redefine an immutable identity and would still leave a floating generator. A proper new identity is a materially broader public contract change: Shared's grant/descriptor schemas and the accepted Database guard both require literal 1.0.0. It would need separate versioned-contract, Database and consumer reconciliation. None is necessary to restore the accepted payload.

Pinning only the consumer conceals the defective package metadata; pinning only Shared leaves a known public-type incompatibility. The selected correction fixes the package and explicitly aligns all three composing consumers. Freezing old JSON while leaving runtime schemas floating is rejected because the observed datetime change is semantic. Removing the independent assertion or trusting only the descriptor-equality helper would suppress a valid check.

## 5. Exact validation and release gates

SHARED-003 adds one artifact harness with the exact file/interface specified in its task. It reuses `scripts/validate-commerce-entrypoints.mjs` through its existing `COMMERCE_CONSUMER_DIRECTORY` input. Each fixture installs the actual packed package into an owned temporary directory; no source symlinks, linked build dependencies, global overrides or peer bypasses.

The aligned direct-4.4.3 fixture must pass version resolution, both hashes, existing commerce/runner checks, actual Shared-schema composition, strict declaration compilation and minute/second/invalid datetime controls. A second direct-4.6.5 fixture verifies Shared still resolves its own 4.4.3 and keeps the same runtime payload. That second fixture explicitly does not certify mixed-version schema composition or approve that configuration for the applications. The ordinary Shared focused source/type/build checks remain required. The implementation task does not publish.

SHARED-004 packages the exact accepted source plus release metadata, verifies the local tarball, publishes that same inspected tarball, retrieves exact 4.0.1, compares archive bytes/integrity and reruns the same harness against the retrieved bytes. Its immutable receipt records actual source/release commits, registry metadata, runner/Zod versions, per-fixture checks and verification times. Reusing source build dependencies through a symlink is not a clean consumer check. The earlier release verification missed this consumer dependency-resolution difference; this is the targeted gap the new release gate closes.

MCP-002 then updates the exact consumer pair through the commands in its amended definition. Both application-relative and Shared-relative resolution must be 4.4.3, and the installed Shared integrity must match SHARED-004. Existing focused tests and actual typecheck/integration-typecheck/lint/build run under the final lock. The 69/71 product group included two corrected-but-unrerun fixtures; the 72/73 generic group included the hash failure. Neither becomes a task pass solely because this diagnosis is complete. The integration scenario is unfinished, and the existing developer-owned Docker evidence remains required for acceptance.

Commerce and Background run their existing required projector/parser/runner checks and actual typechecks under their aligned graphs. SystemTest observes accepted applications and their artifact provenance. No owner bypasses a new failure by changing schemas, casting, weakening a compiler setting or substituting a mocked result.

## 6. Evidence limits and application protocol

Independent diagnostics ran on Node **24.22.1**; the uploaded failure report used **24.19.0**. The exact two hashes were reproduced despite that Node patch difference. The diagnostics used verified registry artifacts in isolated scratch trees. They did not execute the full Shared/MCP/Commerce/Background suites, launch Docker, publish a package, contact a merchant, mutate a database, deploy or send a customer response.

Apply the delivered revision 9 patch to the **current MCP-002 parent task worktree matching the supplied ZIP**, using `git apply --check --whitespace=error-all`, actual `git apply --whitespace=error-all`, and `git diff --check`. Commit only the changed documentation paths in the parent repository and push its existing `task/ARCH-058-MCP-002` branch. No implementation gitlink or source path belongs in that reconciliation commit. The developer integrates the definitions through the established parent workflow before starting SHARED-003 from the canonical workspace; do not use the MCP-002 task worktree as the base for a different task.

Run SHARED-003 through the normal launcher, return for acceptance, then run SHARED-004 through its publication workflow and return for acceptance. Only then resume MCP-002 under its existing claim/worktrees. Keep the remaining tasks pending on their declared prerequisites. This amendment is not implementation acceptance, final integration, deployment or permission to overwrite the immutable 4.0.0 artifact.
