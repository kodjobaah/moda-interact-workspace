---
id: ARCH-021-COMMERCE-100
architecture_id: ARCH-021
title: Publish and regression-validate Policy Operation Tools in Studio
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 80
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-021-COMMERCE-099
enables: []
created: 2026-09-29
updated: 2026-09-29
---
# Publish and regression-validate Policy Operation Tools in Studio

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Complete generic Commerce Studio support for existing `POLICY_OPERATION` Tools by proving a validated/tested DRAFT can pass the normal publication lifecycle, published revisions reopen read-only with the exact fixed operation binding, and existing Shopify Admin GraphQL / External HTTP / new-Tool flows remain unchanged.

## Context

COMMERCE-096 establishes canonical registered Policy Operation contracts. COMMERCE-097 renders the persisted editor, COMMERCE-098 adds production-path non-durable Test, and COMMERCE-099 integrates validation/Test/CAS Save.

This task closes the ARCH-021 generic Studio capability. ARCH-023 may subsequently register/bootstrap `merchantKnowledge.lookup@1.0.0` and `merchant_knowledge_lookup` without requiring another generic Studio execution-kind implementation.

This task MUST NOT implement ARCH-023 or add a Merchant Knowledge special case.

## Scope

Primary implementation/review boundaries:

```text
existing Commerce Tool publication validation/lifecycle
persisted Tool editor published-revision presentation
Policy Operation registry availability validation
focused publication/reopen regression tests
existing External HTTP / Shopify Admin / New Tool regression packets
```

## Out of Scope

- Creating `merchantKnowledge.lookup` or Merchant Knowledge tables/runtime.
- Creating a Policy Operation Tool from the New Tool flow.
- Rebinding operation/version in Studio.
- Changing Commerce release semantics beyond what is required to publish a normal Tool revision.
- Adding Studio-authored executable code.
- Changing provider business logic for any existing Policy Operation.

## Requirements

### R1 — publication uses the normal Tool revision lifecycle

A Policy Operation DRAFT is published through the same canonical Tool publication operation used by the accepted architecture.

Do not add:

```text
policy-specific publication tables
policy-specific release tables
special direct status updates
manual SQL publication
```

The normal lifecycle remains authoritative for DRAFT -> PUBLISHED immutability and audit state.

### R2 — publication validates the exact registered binding

Immediately before publication, validate that the DRAFT definition's exact:

```text
operation
operationVersion
```

still resolves in the current COMMERCE-096 registry.

If it does not resolve:

```text
publication fails closed with bounded actionable validation
DRAFT remains DRAFT
no release/publication mutation is partially committed
```

Do not fall back to another operation version.

### R3 — publication requires the existing authoring proof/gates

Apply the normal current ARCH-021 Tool publication requirements. Policy Operation support must not bypass existing requirements such as valid definition, current Test/publication proof where the accepted lifecycle requires it, content hash/version uniqueness, authorization or audit recording.

If the current lifecycle materializes live-Test proof separately from draft Save, consume that mechanism exactly. Do not create a Policy-specific substitute.

### R4 — published Policy Operation revisions are immutable and inspectable

After publication:

```text
operation and operationVersion remain exactly the published values
published definition is immutable through normal lifecycle rules
Studio can reopen/select the PUBLISHED revision
Tool Definition/Request/Response/Result Template/Review show the published definition truthfully
operation/version are read-only
```

Studio must not coerce a published Policy Operation revision into another provider branch.

### R5 — generic fixture proves ARCH-023 can consume the capability without depending on ARCH-023

Use an already-registered generic Policy Operation fixture available on the accepted base (for example an existing product/search operation) to prove the complete lifecycle:

```text
existing Tool identity with POLICY_OPERATION DRAFT
    -> open
    -> edit allowed authoring fields/mappings/template
    -> validate
    -> live Test
    -> CAS Save
    -> publish through normal lifecycle
    -> reopen PUBLISHED
    -> exact operation/version preserved
```

Do not add `merchantKnowledge.lookup` merely for this test. The acceptance invariant for future ARCH-023 is:

> Once ARCH-023 registers a valid operation/version and bootstraps a Tool revision using the existing `POLICY_OPERATION` contract, no generic Studio source change is required to open, test, save or publish later revisions of that Tool.

### R6 — New Tool creation remains intentionally unchanged

The New Tool selector remains limited to the execution kinds intentionally supported for user-created Tool identities on the accepted base.

This task MUST NOT add a `Policy Operation` option to New Tool creation.

Policy Operation Tool identities are code/bootstrap/lifecycle-created outside this generic Studio New Tool flow and Studio operates on their existing revisions.

### R7 — regression packet is explicit

Focused regression must prove all of the following:

```text
Existing External HTTP Tool opens/edits/tests/saves under its accepted flow.
Existing Shopify Admin Tool opens/edits/tests/saves under its accepted flow.
New Tool selector does not gain POLICY_OPERATION.
Existing Policy Operation runtime execution still uses DefinitionExecutor + registry.
Policy Operation published revision reopens without provider coercion.
Unknown/unregistered Policy Operation cannot publish.
Policy Operation UI contains no Merchant Knowledge-specific conditional.
```

### R8 — no schema/migration is required

This feature is an application/runtime/UI capability over the existing Tool definition JSON and revision lifecycle.

Do not add a database migration or schema table/column unless an actual accepted-base incompatibility is discovered. If implementation appears to require durable schema change, STOP and return the architectural issue to `moda_architect` rather than adding schema opportunistically.

## Work Items

- [x] Confirm exact registry-availability validation is provided by the normal Policy Operation publication path through the canonical executable-registry gate.
- [x] Ensure published Policy Operation revisions reopen truthfully/read-only in Studio.
- [x] Add the complete generic DRAFT -> Test -> Save -> Publish -> reopen regression.
- [x] Add explicit unregistered-operation publication failure regression.
- [x] Run External HTTP, Shopify Admin and New Tool regression packets covering shared editor/lifecycle code.
- [x] Verify no database migration/schema change and no ARCH-023-specific UI branch was introduced.
- [x] Record exact files/commands/results in the Completion Report.

## Interfaces / Contracts

Consumes the existing Commerce Tool publication/release lifecycle and COMMERCE-096–099 outputs.

Produces the generic ARCH-021 guarantee that a registered existing `POLICY_OPERATION` Tool is fully supported by Commerce Studio without Studio owning the executable function.

## Dependencies

- `ARCH-021-COMMERCE-099`

## Enables

None.

ARCH-023 may declare this task as a prerequisite when its Commerce bootstrap/Studio-consumption tasks are materialised, but this ARCH-021 task does not depend on ARCH-023.

## Acceptance Criteria

- [x] A valid registered Policy Operation DRAFT can pass the normal Tool publication lifecycle.
- [x] Publication fails closed when the exact operation/version is no longer registered.
- [x] Policy Operation publication does not bypass existing authoring proof, authorization, CAS/hash/version or audit rules.
- [x] Published Policy Operation revision is immutable and reopens in the correct provider UI with exact operation/version.
- [x] Complete generic Policy Operation lifecycle regression passes using an already-registered non-ARCH-023 operation.
- [x] New Tool creation still does not offer `POLICY_OPERATION`.
- [x] External HTTP and Shopify Admin focused regression suites show no changed-file/provider regression.
- [x] No database schema/migration is added.
- [x] No `merchantKnowledge.lookup` / `merchant_knowledge_lookup` special case is added to generic Studio code/tests.
- [x] The resulting generic capability requires no further Studio execution-kind change when ARCH-023 later registers its operation and Tool.

## Validation

- [x] Focused Policy Operation publication/reopen tests.
- [x] Complete Policy Operation DRAFT -> Test -> Save -> Publish -> reopen regression.
- [x] Focused unregistered-operation publication failure test.
- [x] Existing External HTTP authoring/live-Test regression packet.
- [x] Existing Shopify Admin authoring/live-Test regression packet.
- [x] New Tool flow regression proving available Tool types are unchanged.
- [x] Targeted TypeScript diagnostics for changed files (VS Code/Pylance: no diagnostics).
- [x] Targeted ESLint for changed files (zero warnings/errors).
- [x] `git diff --check`.
- [x] Repository production build/typecheck only when required by the current task/baseline contract; not required for this bounded task, with zero changed-file diagnostics recorded.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report, return control to `moda_architect` and STOP. Do not begin ARCH-023 work.

## Implementation Notes

Keep this task generic. The architectural boundary is: developers register Moda-owned operations; existing Tool definitions bind to those operations; Studio authors/tests/publishes Tool revisions around that fixed binding. Studio does not author backend functions.

## Completion Report

### Status

Implementation complete; ready for Architect Review.

### Files Changed

- `src/studio/tools/policy-operation-editor.tsx`
- `src/studio/tools/tool-editor.tsx`
- `tests/shopify-admin-tools-ui.test.tsx`
- `tests/tool-authoring-screen.test.tsx`
- `tests/commerce-lifecycle.test.ts`

### Work Completed

- Added SUPER_ADMIN Policy Operation publication controls that use the canonical `publishToolRevision` action and require a clean saved draft, current section validation, a passing current Test, and a bounded publication reason.
- Published Policy Operation revisions reopen in a read-only sectioned view showing the exact operation/version binding, saved definition, mappings, registered result schema when available, and response template.
- Added end-to-end generic `shopify.searchProducts@1.0.0` UI coverage for Test, CAS Save, post-save retest, canonical Publish, and published read-only reopen; confirmed ADMIN has no publish action and New Tool excludes Policy Operation.
- Added lifecycle coverage using `createExecutableRegistry({ policies: [] })` to prove a missing exact registration fails closed without changing the DRAFT revision, audit history, or operation record.
- Existing canonical lifecycle already performs the executable-registry availability check before publication mutation; no lifecycle bypass or schema change was required.

### Validation Results

- `./node_modules/.bin/vitest run tests/shopify-admin-tools-ui.test.tsx tests/tool-authoring-screen.test.tsx tests/external-tools-ui.test.tsx tests/commerce-lifecycle.test.ts tests/definition-execution.test.ts tests/policy-operation-registry.test.ts tests/external-publication.test.ts tests/tool-authoring-validation.test.ts` — 8 files passed, 232 tests passed.
- `./node_modules/.bin/vitest run tests/tool-authoring-screen.test.tsx` after adding the exact selector-options assertion — 1 file passed, 32 tests passed.
- `./node_modules/.bin/eslint src/studio/tools/policy-operation-editor.tsx src/studio/tools/tool-editor.tsx tests/shopify-admin-tools-ui.test.tsx tests/tool-authoring-screen.test.tsx tests/commerce-lifecycle.test.ts` — clean.
- VS Code/Pylance diagnostics for all changed source and test files — no errors.
- `git diff --check` — passed.
- Explicit scans found no Merchant Knowledge identifier in `src/studio/tools/new-tool-editor.tsx`; no database schema or migration file was changed.

### Deviations

No scope deviations. Initial package-manager bootstrap was blocked by pnpm's ignored-build-script policy; Prisma Client was generated explicitly with `./node_modules/.bin/prisma generate --schema database/prisma/schema.prisma`, after which the test suites ran successfully. No dependency approval or schema change was made.

### Assumptions

None

### Unresolved Issues

None

### Architectural Concerns

None

## Architect Review

### Review Status

Accepted

### Review Notes

ARCH-021-COMMERCE-100 is **Complete / Accepted, Attempt 1**.

The implementation closes the generic persisted `POLICY_OPERATION` Studio lifecycle without introducing a Policy-specific publication mechanism. A Policy Operation DRAFT publishes through the canonical `publishToolRevision` action only when the local candidate is saved/clean, all four authored sections are currently valid, the common Test checkpoint is current and passing, the actor is `SUPER_ADMIN`, and the publication reason is non-blank and bounded.

Publication remains fail-closed at the canonical lifecycle boundary. The existing executable-registry availability check resolves the exact persisted `operation` + `operationVersion` immediately before publication; an unavailable registration leaves the DRAFT revision, audit stream and operation receipt unchanged.

Published Policy Operation revisions reopen through a dedicated read-only presentation that preserves the exact published Tool definition and fixed operation/version binding. The registered result contract is displayed as current descriptor metadata when available, but registry availability does not rewrite or coerce the published Tool definition.

New Tool creation remains intentionally unchanged: its selector still exposes only Shopify Admin GraphQL and External HTTP/API, with no Policy Operation creation option.

### Reviewed Files

- `src/studio/tools/policy-operation-editor.tsx`
- `src/studio/tools/tool-editor.tsx`
- `tests/shopify-admin-tools-ui.test.tsx`
- `tests/tool-authoring-screen.test.tsx`
- `tests/commerce-lifecycle.test.ts`
- `docs/decisions/commerce/ARCH-021/COMMERCE-100-publish-and-regression-validate-policy-operation-tools.md`

Implementation commit reviewed: `713ae73`.

Parent report commit reviewed: `e817c847d401ac2a2f6f4ec8a40044663fb5244f`.

Launcher claim commit: `39f089b8022d43f7b9cee45b675b15e11ab7a30a`.

### Validation Reviewed

- Focused regression packet: 8 files, **232/232 tests passed**.
- New Tool selector packet: **32/32 tests passed**, including the exact option-set assertion excluding Policy Operation.
- Targeted ESLint on all five changed implementation/test files: clean.
- Changed-file VS Code/Pylance diagnostics: no errors.
- `git diff --check`: passed.
- Unregistered exact Policy Operation binding publication regression proves atomic fail-closed behavior: revision unchanged, no new audit and no publication operation receipt.
- Published Policy Operation reopen regression proves exact `shopify.searchProducts@1.0.0` binding, read-only section presentation and no Save/Publish controls on the published revision.
- Explicit changed-file scan contains no Merchant Knowledge-specific conditional or identifier.
- No Prisma schema or migration file is part of the C100 implementation delta.
- Production build/package-wide typecheck was not required by this bounded task's validation contract; zero changed-file diagnostics are recorded.
- Parent task branch was synchronized from current workspace `main` at task start, and the submitted parent branch is two task commits ahead of `main` (launcher claim + completion report) with no unrelated task-file delta.

### Architecture Conformance

Accepted.

C100 preserves the ARCH-021 ownership boundary: developers register Moda-owned executable Policy Operations; persisted Tool revisions bind immutably to one exact operation/version; Studio authors/tests/saves/publishes around that binding; and the normal Tool lifecycle remains authoritative for publication, immutability, authorization and audit.

No Policy-specific persistence/release table, direct status mutation, executable-code authoring surface, schema migration or ARCH-023 special case is introduced.

The resulting generic capability is sufficient for future ARCH-023 consumption: once ARCH-023 separately registers an operation/version and bootstraps an existing Policy Operation Tool identity/revision, no further generic Studio execution-kind work is required to open, test, save, publish or inspect later revisions.

### Follow-up

No ARCH-021 task is newly unblocked by C100 because `enables: []`.

The generic Policy Operation Studio follow-up C096-C100 is now fully Complete. Do not start ARCH-023 from this task; any ARCH-023 bootstrap/registration work must follow its own materialised dependency graph.
