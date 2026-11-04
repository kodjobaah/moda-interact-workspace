---
id: ARCH-058-SHARED-005
architecture_id: ARCH-058
title: Freeze discount built-in UTC timestamp validation and version the changed built-ins
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 37
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-058-SHARED-004
enables:
  - ARCH-058-SHARED-006
  - ARCH-058-DATABASE-002
  - ARCH-058-SYSTEM-TEST-001
created: 2026-11-04
updated: 2026-11-04
---

# ARCH-058-SHARED-005: Freeze discount built-in UTC timestamp validation and version the changed built-ins

## Architecture

Architecture ID: `ARCH-058`.

Parent: `docs/architecture/ARCH-058-commerce-agent-product-discovery.md`.

Diagnostic evidence: `docs/architecture/ARCH-058/shared-hash-reconciliation-evidence.json` records that Shared 4.0.0's `z.iso.datetime({offset:false})` acceptance differs when the same package resolves different Zod minor versions.

Coordinator: `moda_architect`.

## Objective

Make the timestamp fields exposed by the two discount built-ins use one explicit Moda-owned UTC syntax independent of Zod's `z.iso.datetime` implementation, without changing the existing general `DateSchema` used by other Commerce/recovery contracts. Bump both discount built-ins to `definitionVersion: "2.0.0"` because this correction changes their accepted output wire semantics. This makes `toolName + definitionVersion` a truthful contract identity after SHARED-003 removes hashes.

## Context

Removing built-in hashes solves the descriptor blocker but does not itself solve the validator-semantic drift exposed while reproducing that blocker. Shared 4.0.0's general `DateSchema` delegates to `z.iso.datetime({ offset: false })`; the same package accepted minute-only timestamps under one resolved Zod minor and rejected them under another. `DateSchema` is also reused by contracts outside the two discount built-ins, including recovery/evidence paths, so changing it globally here would create unrelated wire changes.

For ARCH-058, introduce one **internal discount-output timestamp validator in `src/commerce/schemas.ts`** and use it only for the timestamp fields that can occur in `commerce_get_discount_options` / `commerce_get_discount_details`: `CommerceOfferSchema.startsAt`, `CommerceOfferSchema.endsAt`, `CommerceDiscountConditionFactsSchema.observedAt`, and `CommerceDiscountConditionFactsSchema.unavailableAt`. Its canonical syntax is UTC only, seconds required, optional fractional seconds with one or more digits. The general exported `DateSchema` remains unchanged. Because these fields are part of the built-in output contract, this is a wire-contract semantic change; after hashes are removed, preserving `definitionVersion: "1.0.0"` would silently mutate that identity, so this task performs the coordinated breaking bump to `2.0.0`.

## Scope

Modify only the discount built-in schemas/version declarations and focused tests/documentation required to establish their exact final wire semantics:

- `src/commerce/schemas.ts` — add the internal discount-output timestamp validator and replace only the four discount timestamp fields named above;
- `src/commerce/definitions.ts`
- `src/commerce/built-in-tools.ts`
- `src/commerce/product-discovery-contracts.test.ts` or one new directly focused discount timestamp test file
- `src/commerce/runner/built-in-tools.test.ts` when needed for the canonical version assertions
- `scripts/validate-commerce-entrypoints.mjs` when its expected built-in version inventory requires updating
- `README.md`

## Out of Scope

- The general `src/commerce/primitives.ts:DateSchema` and every existing non-discount use of that schema, including product, evidence, recovery-offer-proof and external HTTP contracts.
- Changing Zod dependency versions or pinning application Zod dependencies.
- Converting timestamps, accepting local times, accepting numeric offsets or changing provider data upstream.
- Reintroducing built-in hashes or changing the three-field identity shape owned by SHARED-003.
- MCP context cleanup (SHARED-004) or publication (SHARED-006).

## Requirements

1. In `src/commerce/schemas.ts`, add one non-exported `CommerceDiscountDateTimeSchema` (or the exact repository-style equivalent name chosen in this task definition) implemented as a `z.string()` plus Shared-owned lexical/calendar validation. It must not call `z.iso.datetime`, and it must not replace or modify `primitives.ts:DateSchema`. Use this internal validator **only** for `CommerceOfferSchema.startsAt`, `CommerceOfferSchema.endsAt`, `CommerceDiscountConditionFactsSchema.observedAt`, and `CommerceDiscountConditionFactsSchema.unavailableAt`.
2. Accept exactly the following lexical forms, with a valid Gregorian calendar date/time:

   ```text
   YYYY-MM-DDTHH:mm:ssZ
   YYYY-MM-DDTHH:mm:ss.SZ
   YYYY-MM-DDTHH:mm:ss.SSZ
   YYYY-MM-DDTHH:mm:ss.SSSZ
   ... with any nonempty decimal fractional-second sequence
   ```

   where the fractional part, when present, contains one or more decimal digits; month/day/hour/minute/second ranges are valid and the calendar date actually exists.
3. Reject at minimum:
   - minute-only values such as `2026-11-04T10:00Z`;
   - numeric offsets such as `2026-11-04T10:00:00+00:00`;
   - lowercase `z`;
   - invalid calendar dates such as `2026-02-30T10:00:00Z`;
   - leap seconds (`:60`);
   - whitespace-prefixed/suffixed values.
4. Implement calendar validation with Shared-owned code after lexical matching. Do not rely on permissive `Date.parse` normalization alone. The implementation may use UTC `Date` field comparison after parsing numeric components, but it must compare every captured field back to the constructed UTC value.
5. `CommerceOfferSchema` and `CommerceDiscountConditionFactsSchema` use the internal discount timestamp validator only for the four fields above. `CommerceOfferSchema`'s existing start-before-end refinement remains unchanged. All other `DateSchema` consumers remain byte-for-byte untouched by this task.
6. Change the allowed/canonical `definitionVersion` for **both** `commerce_get_discount_options` and `commerce_get_discount_details` from exactly `1.0.0` to exactly `2.0.0` in `CommerceBuiltInToolGrantSchema`, `CommerceBuiltInToolDescriptorSchema` and `commerceDiscountBuiltInDescriptors`. Do not accept a union of `1.0.0 | 2.0.0` in the corrected source.
7. Preserve the two tool names, descriptions, input schemas and output schemas apart from the explicit `DateSchema` semantics above. No other field/meaning change is authorized.
8. Update focused tests so `2.0.0` is accepted and `1.0.0` is rejected by the corrected built-in grant/descriptor schemas. This is the deliberate pre-production breaking transition; DATABASE-002 upgrades persisted development grants in the same architecture before corrected consumers run.
9. No application dependency pin or package override is introduced.

## Work Items

- [x] Implement the exact internal discount UTC timestamp lexical/calendar validator in `src/commerce/schemas.ts` and wire only the four named discount fields to it.
- [x] Add positive and negative wire-contract fixtures covering the required cases.
- [x] Verify offer start/end behavior still uses the corrected primitive.
- [x] Bump both canonical discount built-ins and their strict grant/descriptor validators from `1.0.0` to `2.0.0`.
- [x] Replace focused `1.0.0` assertions with final `2.0.0` assertions and rejection of legacy `1.0.0`.
- [x] Document the exact Commerce timestamp syntax and `2.0.0` built-in contract identity in README.
- [x] Run required validation.

## Interfaces / Contracts

Corrected Shared contracts:

```text
Discount built-in timestamp fields: canonical UTC timestamp with seconds and an optional nonempty fractional-second component.
commerce_get_discount_options@2.0.0
commerce_get_discount_details@2.0.0
```

`definitionVersion` is the existing built-in wire-contract identity; no new version/hash field is introduced. The bump is mandatory because this task changes accepted output timestamp semantics. ARCH-058 is explicitly pre-production, so corrected Shared/Database/consumers move together and do not support the legacy `1.0.0` built-in identity after the transition.

## Dependencies

- `ARCH-058-SHARED-004`

## Enables

- `ARCH-058-SHARED-006`
- `ARCH-058-DATABASE-002`
- `ARCH-058-SYSTEM-TEST-001`

## Acceptance Criteria

- [x] `src/commerce/primitives.ts:DateSchema` and every non-discount use remain unchanged; the new internal discount timestamp validator does not call `z.iso.datetime`.
- [x] All required accepted timestamp examples parse.
- [x] Every required rejected example fails.
- [x] Invalid calendar dates are rejected by field comparison rather than normalized into another date.
- [x] `CommerceOfferSchema` still rejects a non-null `startsAt >= endsAt` pair.
- [x] Both canonical built-in descriptors/grants use exactly `definitionVersion: "2.0.0"`; the corrected schemas reject legacy `1.0.0`.
- [x] The names, descriptions, inputs and outputs apart from the explicit datetime semantics are unchanged.
- [x] No Zod/package dependency version changes are present.

## Validation

```bash
npm ci --no-audit --no-fund
npm run test:product-discovery-contracts
npm run typecheck
npm run build
npm run validate:commerce-entrypoints
git diff --check
```

Also record direct parse results through `CommerceOfferSchema` and `CommerceDiscountConditionFactsSchema` for these exact timestamp values (using otherwise-valid fixtures):

```text
PASS 2026-11-04T10:00:00Z
PASS 2026-11-04T10:00:00.1Z
PASS 2026-11-04T10:00:00.12Z
PASS 2026-11-04T10:00:00.123Z
PASS 2026-11-04T10:00:00.1234567890Z
FAIL 2026-11-04T10:00Z
FAIL 2026-11-04T10:00:00+00:00
FAIL 2026-02-30T10:00:00Z
FAIL 2026-11-04T10:00:60Z
```

## Stop Condition

After implementation and validation, set status to `review`, complete the report, return to `moda_architect` and STOP. Do not publish or modify consumer repositories.

## Implementation Notes

This task deliberately freezes the currently deployed-consumer-compatible seconds requirement **only for the two discount built-in output contracts** rather than changing Shared's general `DateSchema`. Since `definitionVersion` replaces the discarded hash as the durable built-in contract identity, the discount semantic change and the `2.0.0` bump are one atomic Shared correction and must be reviewed together.

## Completion Report

### Status

Ready for Review, Attempt 1, 2026-11-04. Implementation committed and pushed to `task/ARCH-058-SHARED-005` as `070975e6ea1a38fd5f01e8c7a001b15e1bd67d4c`. Required commands succeeded under their default configuration. One opt-in Commerce projector issue was separately reproduced on the unchanged starting source and is explicitly recorded below. No architect acceptance decision or publication is made by this report.

### Files Changed

- `src/commerce/schemas.ts`: one internal CommerceDiscountDateTimeSchema using an explicit ASCII UTC lexical pattern followed by numeric Gregorian/calendar and clock checks. Only the four authorized discount fields use it.
- `src/commerce/definitions.ts`, `src/commerce/built-in-tools.ts`: canonical/allowed version becomes exactly 2.0.0 for both built-ins; no legacy union.
- `src/commerce/product-discovery-contracts.test.ts`: full-schema and composed-output timestamp matrices, original-byte/nullability/ordering assertions, accepted 2.0.0 and rejected 1.0.0 grants/descriptors, unchanged canonical descriptions and input schemas.
- `src/commerce/runner/built-in-tools.test.ts`: legacy 1.0.0 and noncanonical 2.0.1 registration drift fail closed before execution.
- `scripts/validate-commerce-entrypoints.mjs`: clean-process canonical version inventory and legacy rejection assertions.
- `README.md`: exact discount syntax, scope, deliberate version transition and separate publication responsibility.

### Work Completed

All seven Work Items implemented. The internal validator requires a four-digit year, two-digit date/time components, uppercase T/Z, seconds and an optional nonempty decimal fraction. It rejects surrounding text/whitespace, including a trailing newline (absolute end-of-input lookahead), numeric offsets and leap seconds. Calendar validity uses month/day bounds and Gregorian divisibility-by-4/100/400 rules after lexical matching; no Date.parse or Zod ISO implementation is used for this validation. Fractional digits are neither parsed into a floating-point number nor normalized.

Existing offer start-before-end refinement remains unchanged. Nullability is preserved: startsAt, endsAt and unavailableAt allow null; observedAt does not. Both canonical descriptor and strict grant/descriptor schemas use exactly 2.0.0, preserving names, descriptions, inputs, strict field inventories and hash-free identities. No package version, dependency version, override, consumer repository or persisted grant is changed. Publication remains SHARED-006 and development-grant migration remains DATABASE-002.

### Validation Results

| Command/check | Result |
|---|---|
| `npm ci --no-audit --no-fund` | Passed with the existing lock |
| `npm run test:product-discovery-contracts` | 114 total: 113 passed, 0 failed, 1 existing opt-in Commerce projector test skipped because COMMERCE_CONTRACT_SOURCE_ROOT was unset |
| `npm run typecheck` | Passed |
| `npm run build` | Passed, including declarations |
| `npm run validate:commerce-entrypoints` | Passed; clean-process Commerce/runner imports, canonical 2.0.0 versions, legacy rejection and existing runner regressions |
| `npm exec -- tsx --test src/commerce/tool-contracts.test.ts src/commerce/contracts.test.ts src/commerce/external-contracts.test.ts` | 19 passed, 0 failed/skipped |
| `git diff --check` and staged equivalent | Passed |
| Read-only source preservation checks | Passed; details below |

#### Required direct parse matrix

Each value was checked through otherwise-valid full CommerceOfferSchema fixtures independently at startsAt and endsAt, and full CommerceDiscountConditionFactsSchema fixtures independently at observedAt and unavailableAt. Composed options/details outputs were also checked. All four direct-field results match this table:

| Timestamp | Expected and observed result |
|---|---|
| 2026-11-04T10:00:00Z | PASS |
| 2026-11-04T10:00:00.1Z | PASS |
| 2026-11-04T10:00:00.12Z | PASS |
| 2026-11-04T10:00:00.123Z | PASS |
| 2026-11-04T10:00:00.1234567890Z | PASS |
| 2026-11-04T10:00Z | FAIL |
| 2026-11-04T10:00:00+00:00 | FAIL |
| 2026-02-30T10:00:00Z | FAIL |
| 2026-11-04T10:00:60Z | FAIL |

Expanded fixtures contain 10 accepted and 26 rejected values. They include valid 2000/2024/2400 leap days, invalid 1900/2100 leap days, April 31, zero/out-of-range month/day, hour24/minute60, years0099/9999, lowercase T/Z, empty fractions, numeric exponent fractions, local/offset times, and trailing newline/text/whitespace. Original ten-digit fractional bytes survive parse. Equal and reversed non-null start/end pairs fail; increasing pairs pass.

#### Source and dependency preservation

Programmatically removed only the added validator block and restored its four field references in memory; the resulting schemas.ts equals the starting source byte-for-byte. Reversing only the version literals in definitions.ts and built-in-tools.ts also reproduces the starting files byte-for-byte. Thus no other field, description, input or existing DateSchema consumer was edited.

Unchanged SHA256 values:

```text
src/commerce/primitives.ts c0ef1212147df0bed4f993814a925eea38eed19f4c4d84956fc3e6964d5072eb
package.json b1ac53720c8b85d9c8a682a1dd1fefe594054b9443e1b416849bb0dedd10c544
package-lock.json 7626207660376204326d6555a96e89053158b14ed5769d2511c7cbb49d630908
```

Used workspace Node bootstrap: Node24.19.0, npm11.17.0. Locked Zod4.4.3, TypeScript5.9.3, tsx4.23.12, tsup8.5.1. Package metadata remains4.0.0; this is an unpublished source correction, not a claim that published4.0.0 contains2.0.0 built-ins.

### Physical Worktree and Launcher Evidence

```text
canonical workspace: /Users/kwadwoadomafriyie/project/moda-interact-workspace
parent task worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-058-SHARED-005
implementation task worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-058-SHARED-005
both branches: task/ARCH-058-SHARED-005
parent prepared head: c418c7d5d8d96ebf1f124e79995e799eb4a16aa6
implementation prepared head: 592aaf08fcccfd460a3349ca2e2fedd7aa48edfe
claim: 654a3dcadb88d745c3c21d2623844dfde952fc03
claim pushed: yes; Attempt1, codex, 2026-11-04T20:59:55Z
implementation end: 070975e6ea1a38fd5f01e8c7a001b15e1bd67d4c
parent/implementation remote task fast-forward: not-needed
parent/implementation origin/main incorporation: already-current
recursive submodule sync/update/init/verification: passed by launcher; no submodule entries
shared/default checkouts switched/mutated for implementation: no
another task worktree reused: no
```

No second claim/preparation, main merge/push, parent gitlink update, package publication, database operation or consumer implementation change occurred. Only task-owned scratch source archives were removed after diagnostic comparison.

### Deviations

No implementation-scope deviation. In addition to the required default command, explicitly enabled the existing opt-in Commerce projector test using a scratch archive of Commerce `df62ef096cdb6e98dc571b7c5cd7506974752468` (the parent task's recorded gitlink), with the existing Commerce dependency tree referenced read-only. No checkout was switched and no consumer package was installed/updated. Candidate run:113 passed,1 failed,0 skipped. The one failure is independently baseline-proven as described below; it is not counted as a pass.

### Assumptions

Launcher gate establishes SHARED-004 Complete. The coordinated pre-production2.0.0 transition and separate release/database/consumer sequencing remain architect-owned.

### Unresolved Issues

The existing opt-in `product-discovery-projection.test.ts` fails at line29 while validating the unchanged category-resolution input schema. Observed schema includes query:string(min1,max200) and limit:integer(default5,min1,max10); validateSubset rejects that generated input before the discount loop. The same test, Commerce source and dependency graph were rerun against untouched starting Shared source `592aaf08fcccfd460a3349ca2e2fedd7aa48edfe` in a separate scratch archive:0 passed,1 failed, with the identical schema/assertion. This proves the observed failure predates the timestamp/version changes. No matching baseline ID was found; no baseline ID was invented. It remains for architect/Commerce coordination, outside this task's permitted source changes. Required timestamp/version cases and default validation commands pass.

Diagnostic logs: `/tmp/shared005-focused.log`, `/tmp/shared005-focused-full.log`, `/tmp/shared005-baseline-projection.log`, `/tmp/shared005-regressions.log`, `/tmp/shared005-typecheck.log`, `/tmp/shared005-build.log`, `/tmp/shared005-entrypoints.log`. Both scratch archives were cleaned; durable baseline evidence and exact revisions are recorded above.

### Architectural Concerns

Return the pre-existing optional projection issue to the coordinator; do not weaken its test or modify Commerce here. Publication, persisted development grants and consumer adoption must remain coordinated through their own tasks. Downstream states and Architect Review/reconciliation text remain untouched.

## Architect Review

### Review Status

**Accepted — Attempt 1, 2026-11-04.** Implementation `070975e6ea1a38fd5f01e8c7a001b15e1bd67d4c` satisfies this bounded timestamp/version correction. No blocking findings identified. Task marked Complete under automatic completion mode; Attempt 1 preserved and executor/claim remain empty.

### Reviewed Source and Conformance

Reviewed the entire implementation diff: schemas, strict built-in definitions, canonical descriptors, focused contract/runner tests, entrypoint verifier and README. The internal lexical/calendar validator applies only to the four authorized discount fields, validates leap years and actual day/clock ranges without Date.parse normalization, requires seconds and uppercase UTC markers, and permits nonempty fractional digits. The general DateSchema, non-discount consumers and dependency metadata are unchanged. The existing offer ordering refinement is retained. Both canonical built-ins and strict descriptor/grant validators require exactly 2.0.0 and reject 1.0.0; names, descriptions and inputs remain unchanged. No hash identity is reintroduced.

### Independent Validation

Executed from the dedicated implementation worktree using Node 24.19.0:

- `npm run test:product-discovery-contracts`: **113 passed, 1 optional integration test skipped, 0 failed (114 total)**. The skipped Commerce projector case is not counted as passed. Tests exercise the required timestamp examples through the actual offer/facts schemas and discount outputs, Gregorian boundary cases, nullability, preserved wire bytes and ordering, and both version acceptance/rejection paths.
- `npm run typecheck`: passed.
- `npm run build`: passed, including declaration generation.
- `npm run validate:commerce-entrypoints`: passed with actual clean-process package imports.
- Implementation comparison whitespace check passed; no changes to general primitives, package metadata or lockfile.

Local review log: `/tmp/arch058-shared005-review.log` (not a committed artifact). Existing installed dependencies were used; npm ci and package publication were not rerun by this review.

### Separate Coordination Issue

The Completion Report records an explicitly enabled Commerce projection integration failure at the unchanged category-input schema, reproduced against the untouched starting Shared source with the same Commerce revision/dependency graph. This review inspected the report and test source; it did not independently rerun that opt-in comparison. It is not presented as passing validation or as a regression caused by this timestamp correction. Carry this known compatibility issue into Commerce/consumer validation; do not weaken its assertions or treat this acceptance as integrated publication proof.

### Isolation, Dependencies and Publication

Reviewed the prepared isolation/synchronization evidence. Parent `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-058-SHARED-005`; implementation `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-058-SHARED-005`; both use `task/ARCH-058-SHARED-005`.

All explicit prerequisites for SHARED-006 and DATABASE-002 are now Complete in the parent task definitions. Both are promoted to Ready at Attempt 0 with empty executor/claim. Neither is executed here. The breaking package release, persisted-grant migration and consumer adoption remain coordinated through their own tasks. SYSTEM-TEST-001 is not promoted; ARCH-058 is not marked implemented.

The developer explicitly authorized updating acceptance, committing and pushing on 2026-11-04. Only parent documentation is changed; no implementation source, schema, dependency, gitlink or main branch is modified.

## Architect Dependency Reconciliation (2026-11-04)

SHARED-004 Attempt 1 is architect-accepted and Complete at `2efd9cd`. The sole prerequisite is satisfied. Promoted to Ready with executor/claim empty and Attempt 0 preserved; no execution is started.

## Post-Acceptance Dependency Reconciliation (2026-11-04)

SHARED-005 is accepted and Complete at `070975e`. SHARED-006 and DATABASE-002 are Ready and unclaimed at Attempt 0; no follow-on task is started. Earlier pre-execution reconciliation remains historical.
