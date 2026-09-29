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
status: in_progress
priority: 80
executor: copilot
claimed_at: 2026-09-29T21:14:56Z
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

- [ ] Integrate exact registry-availability validation into the normal Policy Operation publication path where not already provided by the canonical executable-registry gate.
- [ ] Ensure published Policy Operation revisions reopen truthfully/read-only in Studio.
- [ ] Add the complete generic DRAFT -> Test -> Save -> Publish -> reopen regression.
- [ ] Add explicit unregistered-operation publication failure regression.
- [ ] Run External HTTP, Shopify Admin and New Tool regression packets covering shared editor/lifecycle code.
- [ ] Verify no database migration/schema change and no ARCH-023-specific UI branch was introduced.
- [ ] Record exact files/commands/results in the Completion Report.

## Interfaces / Contracts

Consumes the existing Commerce Tool publication/release lifecycle and COMMERCE-096–099 outputs.

Produces the generic ARCH-021 guarantee that a registered existing `POLICY_OPERATION` Tool is fully supported by Commerce Studio without Studio owning the executable function.

## Dependencies

- `ARCH-021-COMMERCE-099`

## Enables

None.

ARCH-023 may declare this task as a prerequisite when its Commerce bootstrap/Studio-consumption tasks are materialised, but this ARCH-021 task does not depend on ARCH-023.

## Acceptance Criteria

- [ ] A valid registered Policy Operation DRAFT can pass the normal Tool publication lifecycle.
- [ ] Publication fails closed when the exact operation/version is no longer registered.
- [ ] Policy Operation publication does not bypass existing authoring proof, authorization, CAS/hash/version or audit rules.
- [ ] Published Policy Operation revision is immutable and reopens in the correct provider UI with exact operation/version.
- [ ] Complete generic Policy Operation lifecycle regression passes using an already-registered non-ARCH-023 operation.
- [ ] New Tool creation still does not offer `POLICY_OPERATION`.
- [ ] External HTTP and Shopify Admin focused regression suites show no changed-file/provider regression.
- [ ] No database schema/migration is added.
- [ ] No `merchantKnowledge.lookup` / `merchant_knowledge_lookup` special case is added to generic Studio code/tests.
- [ ] The resulting generic capability requires no further Studio execution-kind change when ARCH-023 later registers its operation and Tool.

## Validation

- [ ] Focused Policy Operation publication/reopen tests.
- [ ] Complete Policy Operation DRAFT -> Test -> Save -> Publish -> reopen regression.
- [ ] Focused unregistered-operation publication failure test.
- [ ] Existing External HTTP authoring/live-Test regression packet.
- [ ] Existing Shopify Admin authoring/live-Test regression packet.
- [ ] New Tool flow regression proving available Tool types are unchanged.
- [ ] Targeted TypeScript diagnostics for changed files.
- [ ] Targeted ESLint for changed files.
- [ ] `git diff --check`.
- [ ] Repository production build/typecheck only when required by the current task/baseline contract; classify pre-existing diagnostics explicitly and require zero changed-file diagnostics.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report, return control to `moda_architect` and STOP. Do not begin ARCH-023 work.

## Implementation Notes

Keep this task generic. The architectural boundary is: developers register Moda-owned operations; existing Tool definitions bind to those operations; Studio authors/tests/publishes Tool revisions around that fixed binding. Studio does not author backend functions.

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

None

### Deviations

None

### Assumptions

None

### Unresolved Issues

None

### Architectural Concerns

None

## Architect Review

### Review Status

Pending

### Review Notes

None

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

None
