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
status: ready
priority: 37
executor: null
claimed_at: null
attempt: 0
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

- [ ] Implement the exact internal discount UTC timestamp lexical/calendar validator in `src/commerce/schemas.ts` and wire only the four named discount fields to it.
- [ ] Add positive and negative wire-contract fixtures covering the required cases.
- [ ] Verify offer start/end behavior still uses the corrected primitive.
- [ ] Bump both canonical discount built-ins and their strict grant/descriptor validators from `1.0.0` to `2.0.0`.
- [ ] Replace focused `1.0.0` assertions with final `2.0.0` assertions and rejection of legacy `1.0.0`.
- [ ] Document the exact Commerce timestamp syntax and `2.0.0` built-in contract identity in README.
- [ ] Run required validation.

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

- [ ] `src/commerce/primitives.ts:DateSchema` and every non-discount use remain unchanged; the new internal discount timestamp validator does not call `z.iso.datetime`.
- [ ] All required accepted timestamp examples parse.
- [ ] Every required rejected example fails.
- [ ] Invalid calendar dates are rejected by field comparison rather than normalized into another date.
- [ ] `CommerceOfferSchema` still rejects a non-null `startsAt >= endsAt` pair.
- [ ] Both canonical built-in descriptors/grants use exactly `definitionVersion: "2.0.0"`; the corrected schemas reject legacy `1.0.0`.
- [ ] The names, descriptions, inputs and outputs apart from the explicit datetime semantics are unchanged.
- [ ] No Zod/package dependency version changes are present.

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

Not Started

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

All ARCH-058 consumers are still pre-production and can move together to the corrected major package.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

Pending

### Review Notes

Not reviewed.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Not assessed.

### Follow-up

None.

## Architect Dependency Reconciliation (2026-11-04)

SHARED-004 Attempt 1 is architect-accepted and Complete at `2efd9cd`. The sole prerequisite is satisfied. Promoted to Ready with executor/claim empty and Attempt 0 preserved; no execution is started.
