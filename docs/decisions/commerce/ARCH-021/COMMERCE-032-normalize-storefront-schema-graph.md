---
id: ARCH-021-COMMERCE-032
architecture_id: ARCH-021
title: Normalize the pinned Storefront schema graph
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 20
executor: null
claimed_at: null
attempt: 2
depends_on:
  - ARCH-021-COMMERCE-029
enables:
  - ARCH-021-COMMERCE-033
created: 2026-09-24
updated: 2026-09-24
---

# Normalize the pinned Storefront schema graph

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Make the real pinned Shopify Storefront `2026-07` introspection artifact the single source of truth for Studio schema discovery by exposing one truthful typed graph contract with no synthetic field paths or hand-authored field catalogue.

## Context

Manual checkpoint validation exposed a production contract mismatch in the existing Shopify schema builder.

The repository already contains the real pinned Storefront introspection artifact:

```text
lib/discovery/artifacts/storefront-2026-07.json
lib/discovery/artifacts/storefront-2026-07.provenance.json
```

The provenance currently identifies:

```text
apiVersion:        2026-07
sourcePackage:     @shopify/dev-mcp@1.15.4
sourcePackagePath: dist/data/storefront-graphql_2026-07.json.gz
artifactSha256:    54b992d0bc6ceffd030f9d4de69be944159cc9686e1e030d97b8293a5fe059bc
queryType:         QueryRoot
```

The committed artifact is a real GraphQL introspection response and currently contains hundreds of actual Shopify types. It is already consumed by the Storefront compiler.

The bug is that `lib/discovery/schema.ts` flattens the real schema into a DTO that does **not** contain `path`, while `src/studio/contracts.ts` independently declares `DiscoveryField.path` as required. `src/commerce/integration/studio/services.ts` then hides that mismatch with `as SchemaPage`, and the UI uses `field.path` as its React/checkbox identity. At runtime every `path` is therefore `undefined`, so clicking one checkbox can make every checkbox appear selected.

There is also an obsolete hand-authored subset:

```text
lib/discovery/storefront-2026-07.json
```

which is not used by the real discovery/compiler path and must not become a second schema source.

This task fixes only the schema-source/contract layer. It does not implement recursive UI navigation or GraphQL generation.

## Scope

Primary files:

```text
lib/discovery/artifacts/storefront-2026-07.json
lib/discovery/artifacts/storefront-2026-07.provenance.json
lib/discovery/storefront-artifact.ts             # new canonical artifact/provenance accessor
lib/discovery/schema.ts
lib/discovery/compiler.ts                        # consume shared artifact metadata/policy only
lib/discovery/storefront-2026-07.json             # remove obsolete hand-authored subset
src/studio/contracts.ts
src/commerce/integration/studio/services.ts
components/studio-workspace.tsx                   # remove unsafe SchemaPage cast only
scripts/check-storefront-schema-artifact.mjs      # new deterministic artifact inspection/check
package.json
tests/storefront-schema-graph.test.ts             # new
tests/discovery.test.ts
tests/discovery-route.test.ts
```

Additional directly affected files may be changed only when required to compile the contract change.

## Out of Scope

- Recursive schema-navigation UI.
- Checkbox/tree state implementation.
- GraphQL document generation.
- Tool argument-binding UI.
- Live Shopify requests from the Studio browser.
- Store-specific schema introspection.
- Shopify Admin GraphQL / Phase-3 authoring.
- Database migrations.
- Shared-package changes.
- Background/Gateway changes.
- Provider/model calls.
- Any new hand-authored field allowlist/catalogue.

## Requirements

### R1 — one real schema source of truth

The canonical Storefront schema source is exactly:

```text
lib/discovery/artifacts/storefront-2026-07.json
```

with provenance:

```text
lib/discovery/artifacts/storefront-2026-07.provenance.json
```

Normal Studio schema browsing MUST NOT call Shopify or Shopify Dev MCP on every field expansion. The builder is dynamic because it consumes the complete real pinned introspection artifact, not because it performs a live network request for each UI interaction.

The obsolete hand-authored file:

```text
lib/discovery/storefront-2026-07.json
```

must be deleted. No replacement hand-authored field list may be introduced.

### R2 — deterministic artifact verification

Create:

```text
scripts/check-storefront-schema-artifact.mjs
```

and package script:

```json
"check:storefront-schema-artifact": "node scripts/check-storefront-schema-artifact.mjs"
```

The script MUST:

1. read the committed introspection artifact and provenance;
2. require `apiVersion === "2026-07"`;
3. require `sourcePackage === "@shopify/dev-mcp@1.15.4"`;
4. require a GraphQL introspection object at `data.__schema`;
5. read the query-root name from `data.__schema.queryType.name` instead of hard-coding it;
6. recompute SHA-256 over the exact committed artifact bytes and require it equals provenance `artifactSha256`;
7. print deterministic bounded summary lines containing:
   - API version;
   - artifact SHA-256;
   - query-root name;
   - total type count;
   - query-root field count;
8. exit non-zero on any mismatch.

Do not print the complete 1.7MB artifact.

The task Completion Report MUST record the actual summary values produced by this script.

### R3 — canonical serializable GraphQL type reference

Define one serializable type-reference contract owned by Commerce discovery.

Use this exact semantic model:

```text
NON_NULL -> child type reference
LIST     -> child type reference
NAMED    -> name + GraphQL named-kind
```

The public TypeScript representation may use discriminated unions or the equivalent recursive object, but it MUST preserve the wrapper structure rather than reducing a field type to a display string.

The named kind must be bounded to the GraphQL introspection kinds used by the artifact, including at least:

```text
SCALAR
OBJECT
ENUM
INTERFACE
UNION
INPUT_OBJECT
```

Provide pure helpers for:

```text
display type text
unwrap named type
is nullable
is list
is expandable output type
```

Those helpers must derive their answer from the type-reference contract.

### R4 — truthful discovery field contract

A discovered field MUST NOT contain a server-supplied `path`.

The normalized discovered field contract must contain at least:

```text
name
description
typeRef
namedTypeName
namedTypeKind
nullable
list
expandable
selectable
restrictionReason
arguments
deprecated
deprecationReason
```

Each argument must contain at least:

```text
name
description
typeRef
required
defaultValue
```

The values are derived from the real pinned introspection artifact.

No UI-oriented synthetic ancestry/path belongs in the server field DTO.

### R5 — truthful schema-page contract

`browseSchema()` must return one canonical serializable response containing at least:

```text
apiVersion
schemaHash
rootTypeName
parentTypeName
parentTypeKind
fields
nextCursor
```

`rootTypeName` is read from the introspection artifact.

`parentTypeName` is the actual type being browsed.

The default parent is the artifact's real `queryType.name`, not a duplicated string constant.

Searching/pagination remain bounded and deterministic.

### R6 — discovery policy must agree with the accepted compiler policy

The browse result must not present a field as selectable when the accepted Storefront compiler will always reject it for the same context.

At minimum, root-level restrictions already enforced by the compiler and Storefront token requirements must produce:

```text
selectable: false
restrictionReason: <bounded safe explanation>
```

Do not create a second independently maintained restriction matrix.

Factor/reuse one Commerce-owned policy helper where necessary so schema browsing and compiler enforcement cannot silently diverge.

This task must preserve the current accepted compiler semantics; it must not broaden Storefront access.

### R7 — remove contract casts/duplication

After this task:

```text
src/studio/contracts.ts
```

must consume/alias the canonical discovery types using type-only imports rather than re-declaring a richer incompatible `DiscoveryField`.

Remove unsafe contract assertions such as:

```text
as SchemaPage
```

from the production discovery adapter and Studio composition where the underlying value is the discovery response.

TypeScript must prove the contract.

### R8 — actual pinned-schema evidence

Focused tests must use the real committed introspection artifact and prove at least:

```text
query root comes from artifact.data.__schema.queryType.name
QueryRoot contains product
product resolves to named output type Product
Product contains title
Product contains priceRange
ProductPriceRange contains minVariantPrice
MoneyV2 contains amount
customer/root token restriction is represented as not selectable
field DTOs contain no `path`
schemaHash equals provenance artifactSha256
```

Tests must not recreate those fields in a richer hand-written fixture.

### R9 — no normal runtime network dependency

`browseSchema()` remains local/committed-artifact backed.

Do not add a Shopify token requirement, Storefront endpoint, HTTP fetch, Shopify Admin API call or Dev MCP subprocess to normal Studio schema browsing.

The existing developer-documentation upstream remains separate.

## Work Items

- [x] Add canonical Storefront artifact/provenance accessor.
- [x] Add deterministic committed-artifact checker.
- [x] Add recursive serializable type-reference helpers.
- [x] Replace flat/incompatible schema DTO with truthful normalized contract.
- [x] Align browse selectability with accepted compiler restrictions.
- [x] Remove `DiscoveryField.path` from the server contract.
- [x] Remove production `as SchemaPage` assertions at the discovery boundary.
- [x] Remove the unused hand-authored `lib/discovery/storefront-2026-07.json`.
- [x] Add real-artifact focused regressions.
- [x] Add package validation script.

## Interfaces / Contracts

Produces the canonical Commerce-owned Storefront schema-discovery contract consumed by:

```text
ARCH-021-COMMERCE-033
ARCH-021-COMMERCE-034
```

The schema artifact is not a Shared-package cross-service contract.

No database or Background contract changes are produced.

## Dependencies

- ARCH-021-COMMERCE-029

## Enables

- ARCH-021-COMMERCE-033

## Acceptance Criteria

- [x] The full pinned Storefront introspection artifact is the only field/type source.
- [x] Artifact provenance and SHA-256 are checked deterministically.
- [x] Discovery type wrappers/arguments are preserved structurally.
- [x] Discovery fields no longer contain synthetic `path`.
- [x] `src/studio/contracts.ts` no longer invents a richer schema-field shape.
- [x] No production `as SchemaPage` hides a contract mismatch.
- [x] Root/nested fields come from the real artifact.
- [x] Browse restrictions cannot advertise an always-rejected root as selectable.
- [x] Normal schema browsing performs no provider/network I/O.
- [x] Existing Storefront compiler behavior remains unchanged except for sharing canonical artifact/policy metadata.

### Validation

- [x] `npm run check:storefront-schema-artifact`
- [x] `npx vitest run tests/storefront-schema-graph.test.ts tests/discovery.test.ts tests/discovery-route.test.ts --reporter=verbose`
- [x] targeted ESLint for every changed source/test/script file
- [x] `npm run typecheck` (record only unchanged documented unrelated baseline diagnostics; zero task-owned diagnostics required)
- [x] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report, return to `moda_architect` and STOP.

Do not start COMMERCE-033.

## Implementation Notes

Do not load the complete schema artifact into a Client Component solely to make the UI dynamic. The server discovery action may return bounded type pages derived from the complete local graph.

The artifact is already the real pinned introspection response. Dynamic means the UI follows that graph; it does not mean introducing live remote introspection on every click.

Do not solve the checkbox bug with:

```text
path ?? name
path: field.name
```

or another synthetic server path. Ancestry belongs to client selection state in COMMERCE-033.

## Completion Report

### Status

Ready for Review

### Files Changed

- Attempt 2 correction files:
   - `lib/discovery/storefront-2026-07.json` (deleted)
   - `scripts/check-storefront-schema-artifact.mjs`
   - `tests/storefront-schema-graph.test.ts`
- `components/studio-workspace.tsx`
- `lib/discovery/compiler.ts`
- `lib/discovery/schema.ts`
- `lib/discovery/storefront-artifact.ts`
- `package.json`
- `scripts/check-storefront-schema-artifact.mjs`
- `src/commerce/integration/studio/services.ts`
- `src/studio/contracts.ts`
- `src/studio/testing/in-memory-studio-services.ts`
- `tests/storefront-schema-graph.test.ts`

### Work Completed

- Added the canonical accessor for the committed `storefront-2026-07` introspection artifact and provenance, including recursive serializable GraphQL type references and pure wrapper helpers.
- Reworked discovery browsing to normalize the complete real artifact graph, preserve argument/type wrappers, expose root and parent type metadata, and omit server-supplied paths.
- Shared the compiler and discovery Storefront restriction helper; customer/token-required roots are non-selectable with bounded reasons.
- Removed production discovery `as SchemaPage` assertions and updated the in-memory Studio fixture to the canonical contract.
- Removed the obsolete hand-authored `lib/discovery/storefront-2026-07.json` source and added deterministic artifact verification plus real-artifact graph regressions.

Attempt 2 correction checklist:

- [x] `git ls-files --error-unmatch lib/discovery/storefront-2026-07.json` classified the path as `tracked legacy file`.
- [x] Deleted the tracked legacy source; `test ! -e lib/discovery/storefront-2026-07.json` passed in the implementation worktree.
- [x] Checker now fails with the required message if the obsolete path is reintroduced.
- [x] Focused regression creates the forbidden path in a controlled test, verifies checker failure, and removes the temporary file.
- [x] Preserved accepted artifact graph, provenance/hash, recursive references, truthful DTOs, shared restriction policy, no production `as SchemaPage`, and local/no-network browsing behavior.

Correction mapping:
- Attempt 1 accepted source/provenance and contract work: `lib/discovery/storefront-artifact.ts`, `lib/discovery/artifacts/storefront-2026-07.*`, `lib/discovery/schema.ts`, `lib/discovery/compiler.ts`, `src/studio/contracts.ts`, `src/commerce/integration/studio/services.ts`, `components/studio-workspace.tsx`, `src/studio/testing/in-memory-studio-services.ts`, `package.json`.
- Attempt 2 legacy-source correction: deleted `lib/discovery/storefront-2026-07.json`; guarded exact path in `scripts/check-storefront-schema-artifact.mjs`; added invariant regression in `tests/storefront-schema-graph.test.ts`.

### Validation Results

- Artifact checker: `npm run check:storefront-schema-artifact` passed. Summary: `apiVersion: 2026-07`; `artifactSha256: 54b992d0bc6ceffd030f9d4de69be944159cc9686e1e030d97b8293a5fe059bc`; `queryRoot: QueryRoot`; `typeCount: 392`; `queryRootFieldCount: 33`.
- Focused tests: `npx vitest run tests/storefront-schema-graph.test.ts tests/discovery.test.ts tests/discovery-route.test.ts --reporter=verbose` passed, 3 files and 29 tests.
- Targeted ESLint: all changed source, fixture, script, and focused test files passed.
- Legacy absence: `test ! -e lib/discovery/storefront-2026-07.json` passed.
- `git diff --check` passed.
- Typecheck: `npm run typecheck` remains non-zero on unchanged repository baseline diagnostics (`TYPECHECK-001`), including Prisma/generated-client and unrelated service/test typing errors. Zero diagnostics were reported in Attempt 2 checker/test/deleted-file paths. The only task-adjacent diagnostics remain the documented pre-existing `src/commerce/integration/studio/services.ts` diagnostics at lines 72 and 85; no Attempt 2 change touched that file.
- Initial dependency setup also reported `ERR_PNPM_IGNORED_BUILDS` for unapproved package build scripts; direct checker/tests/lint ran successfully after setup and no generated dependency files were retained.

### Deviations

The Architect Review identified the obsolete subset as tracked. It was deleted in Attempt 2 and the checker now prevents reintroduction. No replacement field catalogue was added.

### Assumptions

- The committed artifact bytes and provenance remain the accepted pinned Shopify Storefront `2026-07` source.
- The existing repository-wide typecheck baseline remains architect-owned and outside this bounded schema contract task.

### Unresolved Issues

Repository-wide typecheck remains blocked by unchanged `TYPECHECK-001` baseline diagnostics; this task introduces no diagnostics in its changed schema/discovery contract paths.

### Publication Evidence

- Prepared packet evidence: parent sync head `8aff42630a6c5aad4d2c60efebee63f2f5d6ce2d`; implementation head at start `641f764c0fe74eaa85b446b9a390234f4eb85dee`; claim commit `e1b1466c30b71d09b473beeab6b36a744aff4dfc`; dependency `ARCH-021-COMMERCE-029` complete; database submodule `0a8d3b9feade69690b6c1e33aeda051ea588bd45`.
- Canonical worktrees: parent `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-032`; implementation `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-032`.
- Implementation branch: `task/ARCH-021-COMMERCE-032`; implementation commit: `76358c6` (`fix(commerce): enforce pinned storefront schema source`), pushed to `origin/task/ARCH-021-COMMERCE-032`.
- Parent report publication commit: `146e6123`, pushed to `origin/task/ARCH-021-COMMERCE-032`.
- No secrets or `token.txt` were accessed or changed. `ARCH-021-COMMERCE-033` was not started.

### Architectural Concerns

None.

## Architect Review

### Review Status

Changes Requested

### Review Notes

Attempt 1 is architecturally correct in its primary implementation:

- `lib/discovery/artifacts/storefront-2026-07.json` is consumed as the real pinned Storefront `2026-07` introspection source;
- provenance/hash/query-root metadata are centralized through `storefront-artifact.ts`;
- recursive `NON_NULL` / `LIST` / named type references are preserved;
- discovery fields expose truthful schema metadata and no longer expose a synthetic server `path`;
- `src/studio/contracts.ts` aliases the canonical discovery contract instead of independently declaring a richer field shape;
- the production `as SchemaPage` assertion was removed;
- discovery and the Storefront compiler share the same root/token restriction helper;
- normal `browseSchema()` remains local to the committed artifact and introduces no provider/network dependency;
- the submitted focused tests cover the real artifact graph and report 28 passing tests.

Architect independently ran:

```text
node scripts/check-storefront-schema-artifact.mjs
```

against the supplied review snapshot and confirmed:

```text
apiVersion: 2026-07
artifactSha256: 54b992d0bc6ceffd030f9d4de69be944159cc9686e1e030d97b8293a5fe059bc
queryRoot: QueryRoot
typeCount: 392
queryRootFieldCount: 33
```

There is one implementation blocker.

#### R1 is not actually satisfied: the obsolete hand-authored schema file is still present

The supplied Attempt 1 review snapshot physically contains:

```text
moda-interact-commerce/lib/discovery/storefront-2026-07.json
```

The file is 1,303 bytes and contains the old hand-authored subset, including entries such as:

```text
availableForSale
description
handle
onlineStoreUrl
product
productType
shop
title
vendor
```

This contradicts both:

```text
R1 — the obsolete hand-authored file must be deleted
```

and the Completion Report statement:

```text
"The obsolete hand-authored subset ... was absent after cleanup and is verified absent."
```

The current artifact checker also still exits successfully while that obsolete file exists, so it does not enforce the single-source-of-truth invariant.

Whether that legacy file is currently tracked, untracked, or residual local workspace state does not change the architectural requirement: the task worktree used for review must not contain a second Storefront schema source.

### Attempt 2 deterministic correction

Reclaim the same task as Attempt 2.

Do **not** redesign the normalized graph, compiler policy, Studio schema DTO, or future recursive browser. The only implementation correction is legacy-source removal plus durable validation of that invariant.

1. At Attempt 2 start, inspect:

   ```bash
   git ls-files --error-unmatch lib/discovery/storefront-2026-07.json
   ```

   Record one of these exact outcomes in the Completion Report:

   ```text
   tracked legacy file
   ```

   or:

   ```text
   untracked/local legacy residue
   ```

   Do not guess.

2. Ensure this path does not exist in the implementation worktree:

   ```text
   lib/discovery/storefront-2026-07.json
   ```

   If tracked, delete it and commit the deletion.

   If untracked/local residue, remove it from the worktree and record that no Git deletion was possible because it was not tracked.

3. Strengthen:

   ```text
   scripts/check-storefront-schema-artifact.mjs
   ```

   so the checker fails non-zero if the obsolete path exists.

   Use the repository root already resolved by the script. The checker must test the exact path:

   ```text
   lib/discovery/storefront-2026-07.json
   ```

   Required failure message:

   ```text
   storefront-schema-artifact: obsolete hand-authored schema source still exists: lib/discovery/storefront-2026-07.json
   ```

   Do not add the obsolete file to `.gitignore`.

4. Add a focused regression for the checker invariant. The test may either:

   - invoke the checker in a controlled temporary fixture; or
   - factor a small pure checker helper used by both the script and test.

   It must prove that presence of the obsolete path causes failure.

   Do not create a second schema fixture that becomes another production source.

5. Preserve all accepted Attempt 1 behavior:

   ```text
   real artifact graph
   provenance/hash verification
   query root from introspection
   recursive type references
   no DiscoveryField.path
   no production as SchemaPage
   shared compiler/discovery restriction helper
   no runtime provider/network schema request
   ```

6. Re-run:

   ```bash
   npm run check:storefront-schema-artifact

   npx vitest run \
     tests/storefront-schema-graph.test.ts \
     tests/discovery.test.ts \
     tests/discovery-route.test.ts \
     --reporter=verbose
   ```

   Include any new checker-specific test file in the same focused packet.

7. Run targeted ESLint for every Attempt 2 changed source/test/script file.

8. Run:

   ```bash
   npm run typecheck
   ```

   The already-documented unrelated baseline may remain non-zero, but the Completion Report must record the exact current baseline classes and confirm zero new diagnostics in Attempt 2-owned files.

9. Run:

   ```bash
   test ! -e lib/discovery/storefront-2026-07.json
   git diff --check
   ```

   Both must pass.

10. Reconcile the task `## Validation` checklist. Attempt 1 returned with every Validation checkbox unchecked despite recording the commands as executed. On Attempt 2, mark each validation item `[x]` when its required evidence is satisfied, including typecheck when only the explicitly allowed unchanged unrelated baseline remains.

11. Reconcile the Completion Report so it no longer states that the obsolete file was absent unless the final worktree actually proves:

   ```bash
   test ! -e lib/discovery/storefront-2026-07.json
   ```

12. Record normal Attempt 2 launcher/worktree/synchronization/submodule evidence, implementation commit, parent report commit, and final clean/upstream branch state.

13. Return:

   ```yaml
   status: review
   executor: null
   claimed_at: null
   attempt: 2
   ```

   and STOP.

Do not start `ARCH-021-COMMERCE-033`.

### Reviewed Files

- `lib/discovery/artifacts/storefront-2026-07.json`
- `lib/discovery/artifacts/storefront-2026-07.provenance.json`
- `lib/discovery/storefront-2026-07.json`
- `lib/discovery/storefront-artifact.ts`
- `lib/discovery/schema.ts`
- `lib/discovery/compiler.ts`
- `src/studio/contracts.ts`
- `src/commerce/integration/studio/services.ts`
- `components/studio-workspace.tsx`
- `src/studio/testing/in-memory-studio-services.ts`
- `scripts/check-storefront-schema-artifact.mjs`
- `tests/storefront-schema-graph.test.ts`
- `tests/discovery.test.ts`
- `tests/discovery-route.test.ts`
- `package.json`
- task Completion Report

### Validation Reviewed

Architect independently verified the artifact checker against the supplied snapshot:

```text
apiVersion: 2026-07
artifactSha256: 54b992d0bc6ceffd030f9d4de69be944159cc9686e1e030d97b8293a5fe059bc
queryRoot: QueryRoot
typeCount: 392
queryRootFieldCount: 33
```

Submitted evidence records:

```text
focused tests: 3 files / 28 passed
targeted ESLint: PASS
git diff --check: PASS
```

The supplied archive has no `node_modules`, so the architect did not independently rerun Vitest/ESLint/typecheck.

### Architecture Conformance

Partial.

The normalized Storefront graph and Studio contract are conformant. The remaining non-conformance is the physical presence of the obsolete hand-authored Storefront schema source and the lack of a checker guard preventing its reintroduction.

### Follow-up

Attempt 2 is removal/validation-only. No schema-browser or query-builder work is authorized in this correction.

`ARCH-021-COMMERCE-033` remains Pending until COMMERCE-032 is architect-accepted Complete.
