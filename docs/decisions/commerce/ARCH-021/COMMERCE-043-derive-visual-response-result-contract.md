---
id: ARCH-021-COMMERCE-043
architecture_id: ARCH-021
title: Derive the Visual response result contract from projection authoring
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 60
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-021-COMMERCE-016
  - ARCH-021-COMMERCE-021
  - ARCH-021-COMMERCE-039
enables:
  - ARCH-021-COMMERCE-044
created: 2026-09-26
updated: 2026-09-26
---

# Derive the Visual response result contract from projection authoring

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Remove duplicate Visual-response authoring by giving each projected output field an explicit bounded result type in Studio authoring and deterministically deriving the canonical `resultSchema` from the Visual projection instead of requiring an administrator to separately maintain `Response shape JSON`.

## Context

Manual review of the completed local-only Tool flow found that Visual response authoring currently asks the administrator to describe the same result twice:

```text
Visual processing
  output field -> source path -> omit if missing

Response shape JSON
  output field -> JSON-schema type -> required/optional
```

The two representations can disagree, which is why publication validation currently needs `visualPublicationCompatible(...)` to reject mismatches.

For Visual OBJECT/LIST processing the Studio already owns enough authoring intent to make the result contract deterministic once the projected field's expected scalar type is explicit. The persisted runtime processing contract itself does not need a cross-repository change: projection paths and `omitIfMissing` remain in `responseProcessing`, while the generated bounded output contract remains in the existing Commerce-owned `resultSchema` field.

This task establishes the deterministic derivation capability and focused authoring contract. COMMERCE-044 owns Response-only authoritative validation. COMMERCE-045 owns the final Response-tab presentation and mode UX.

## Scope

Primary files:

```text
src/commerce/tool-authoring/                         # bounded Visual result-schema derivation helper/location
src/commerce/tool-definition/publication.ts          # consume/reconcile canonical compatibility where appropriate
src/studio/external-http/response-tab.tsx             # only minimal authoring integration needed to prove the derived contract

tests/external-tool-authoring-validation.test.ts
 tests/arch021-commerce-tool-contract.test.ts         # when the existing packet owns result-schema contract coverage
 tests/external-tools-ui.test.tsx                     # focused Visual result-contract coverage only
```

Use repository-conventional filenames if the helper belongs in an existing module rather than creating a new module solely for naming symmetry.

## Out of Scope

- Changing `VisualResponseProcessingSchema` in `@modainteract/moda-interact-shared`.
- Publishing a new Shared package version.
- Adding a persisted `type` field to Visual response-processing mappings.
- Direct-mode or JavaScript-mode sample-based result-schema inference; that requires observed processed output and belongs to later Test-tab review.
- Response-specific Server Action validation; COMMERCE-044 owns that boundary.
- Full Response-tab layout, JavaScript panel wiring, Source-path presentation or mode-draft preservation; COMMERCE-045 owns those changes.
- Live provider I/O.
- Phase 2 tab gating.
- Database schema changes.

## Requirements

### R1 — one authored Visual field contract

For Visual `OBJECT` and `LIST` authoring, treat each projected output field as one authoring concept containing:

```text
output name
source path
result scalar type
omit if missing
```

Supported result scalar types are the bounded result-schema scalar types already compatible with Visual processing:

```text
string
integer
number
boolean
```

`omit if missing` remains the existing runtime processing semantic. For result-contract derivation:

```text
omit if missing = true
    -> field is optional in the derived schema

omit if missing absent/false
    -> field is required in the derived schema
```

Do not create a second independently persisted `required` flag.

### R2 — no Shared/runtime processing contract expansion

The new result-type choice is Studio/Commerce authoring information used to maintain the existing `resultSchema`.

Do NOT change the shared Visual response-processing runtime shape:

```text
fields[name].path
fields[name].omitIfMissing
```

The persisted canonical Tool definition continues to contain:

```text
responseProcessing
resultSchema
```

but Studio authors those as one coherent Visual contract rather than two independent JSON documents.

### R3 — deterministic OBJECT result schema

For Visual `OBJECT`, derive the complete `resultSchema` deterministically from the projected fields.

The generated schema MUST be:

```text
type: object
properties: exactly the projected output names
required: exactly fields without omitIfMissing
additionalProperties: false
```

Type mapping:

```text
string  -> { type: "string", maxLength: 4096 }
integer -> { type: "integer" }
number  -> { type: "number" }
boolean -> { type: "boolean" }
```

Use the exact bounded subset accepted by `DetailsSchemaSchema`; do not generate unsupported JSON Schema keywords.

### R4 — deterministic LIST result schema

For Visual `LIST`, derive the canonical result contract matching the actual Visual processor output:

```text
{
  items: [ projected row, ... ]
}
```

The generated schema MUST therefore represent:

```text
root object
  required property: items
  items property: array
    maxItems: current Visual limit
    item: object whose properties/required fields derive from the Visual field contract
root additionalProperties: false
row additionalProperties: false
```

Do not invent a different list envelope from the one returned by the accepted response processor.

### R5 — one derivation helper

Implement one deterministic Commerce-owned helper used by authoring code/tests to derive the Visual `resultSchema`.

Do not hand-build subtly different schema objects in separate UI handlers.

The helper must reject or deterministically report:

- no projected fields;
- unsafe/duplicate output names;
- unsupported result types;
- impossible/non-bounded generated schema;
- LIST limits outside the accepted runtime bounds.

Existing `responseProcessing` schema validation remains authoritative for path/filter/sort correctness.

### R6 — reconstruct editable field types from an existing compatible draft

Persisted Visual drafts already contain both `responseProcessing` and `resultSchema`.

Provide a deterministic way for Studio authoring to recover the authored scalar type for each projected field from a compatible persisted `resultSchema` so existing drafts can be edited without a new persisted metadata field.

Do not silently guess a type when an existing schema is incompatible with the projection. Return an explicit authoring incompatibility for later UI presentation instead.

### R7 — derived schema replaces independently editable Visual shape JSON

Once the Visual authoring contract is valid, the Visual mode's `resultSchema` is generated from that contract.

The user must not be required to independently edit raw `Response shape JSON` in Visual mode merely to repeat the field/type/required information already captured by the projection controls.

COMMERCE-045 will own the final presentation (for example a read-only `View derived schema` disclosure). This task must provide the data/helper needed for that presentation.

### R8 — preserve Direct and JavaScript contracts

Do not change Direct or JavaScript `resultSchema` semantics in this task.

Those modes cannot be deterministically derived from configuration alone:

```text
Direct
  source path identifies where data comes from but not all output types

JavaScript
  arbitrary transform(response) determines the output shape
```

They retain an explicit canonical `resultSchema` until later Test-tab work decides how sample-derived schema generation should operate.

## Work Items

- [ ] Define the bounded Visual projected-field result-type authoring model without changing Shared runtime contracts.
- [ ] Add one deterministic OBJECT result-schema derivation helper.
- [ ] Add deterministic LIST result-schema derivation matching `{ items: [...] }` runtime output.
- [ ] Map `omitIfMissing` to derived required/optional schema semantics.
- [ ] Add deterministic reconstruction of Visual field types from compatible persisted result schemas.
- [ ] Reject incompatible legacy/malformed Visual projection/schema pairs rather than silently guessing.
- [ ] Add focused contract/authoring regressions for OBJECT and LIST derivation.
- [ ] Preserve Direct/JavaScript result-schema semantics unchanged.

## Interfaces / Contracts

Consumes:

```text
ARCH-021-COMMERCE-016
Commerce-owned Tool definition and bounded result schema

ARCH-021-COMMERCE-021
accepted Visual OBJECT/LIST response authoring semantics

ARCH-021-COMMERCE-039
local-only new-Tool authoring invariant
```

Produces a Commerce-owned deterministic Visual result-schema authoring helper consumed by COMMERCE-044/045.

No cross-repository runtime contract or Shared package change is introduced.

## Dependencies

- ARCH-021-COMMERCE-016
- ARCH-021-COMMERCE-021
- ARCH-021-COMMERCE-039

## Enables

- ARCH-021-COMMERCE-044

## Acceptance Criteria

- [ ] Visual OBJECT projected fields have an explicit authoring result type drawn from string/integer/number/boolean.
- [ ] Visual LIST projected fields use the same bounded type model.
- [ ] `omitIfMissing` is the single source for required/optional semantics.
- [ ] OBJECT `resultSchema` is generated deterministically from the Visual field contract.
- [ ] LIST `resultSchema` is generated deterministically and matches the accepted `{ items: [...] }` runtime result envelope.
- [ ] Generated string schemas include the bounded `maxLength` required by the canonical schema subset.
- [ ] Existing compatible persisted Visual definitions can reconstruct their field types deterministically.
- [ ] Incompatible projection/schema pairs are reported rather than silently coerced.
- [ ] Direct and JavaScript result-schema behaviour is unchanged.
- [ ] `@modainteract/moda-interact-shared` and Prisma schemas are unchanged.
- [ ] No live provider call, persistence change or tab gating is introduced.

## Validation

- [ ] focused Visual result-schema derivation unit tests
- [ ] focused OBJECT/LIST publication-compatibility regressions
- [ ] focused External HTTP authoring/UI regression required to prove round-trip reconstruction
- [ ] existing common Tool-authoring packet required by repository scripts
- [ ] targeted TypeScript diagnostics or repository typecheck with baseline reconciliation
- [ ] targeted ESLint for changed files
- [ ] `git diff --check`

## Stop Condition

After deterministic Visual result-contract derivation, persisted-draft reconstruction and required regressions are complete, set the task to `review`, complete the Completion Report and STOP. Do not add Response-only Server Actions, rework the complete Response-tab layout, wire live provider testing or start COMMERCE-044.

## Implementation Notes

The runtime Visual processor already emits scalar projected values and LIST results as `{ items: rows }`. Keep the generated schema aligned to those accepted runtime semantics.

This task removes duplicated *authoring*, not the durable `resultSchema` field. The canonical definition still persists `resultSchema` because downstream validation/templates require a durable output contract.

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
