---
id: ARCH-031-ADMIN-001
architecture_id: ARCH-031
title: Configure the default automatic translation model
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-031-DATABASE-001
enables:
  - ARCH-031-ADMIN-003
created: 2026-10-10
updated: 2026-10-10
---

# Configure the default automatic translation model

## Architecture

Architecture ID: `ARCH-031`.

Architecture document: `docs/architecture/ARCH-031-automatic-merchant-pricing-translations.md`.

Coordinator: `moda_architect`.

## Objective

Extend the existing System Controls / Translations surface so a `SUPER_ADMIN` can designate exactly one enabled translation model as the automatic platform default used by Merchant Pricing translation.

## Context

The current Admin translation configuration surface manages one encrypted OpenAI credential per environment/provider and multiple enabled/disabled model profiles. Store Category translation currently lets the administrator choose one of those models per request.

ARCH-031 adds a central automatic-default model. Merchant Pricing authors must not choose a model each time they create a plan.

## Scope

Only `moda-interact-admin` translation-configuration read/action/UI code and focused tests.

Likely surface:

```text
src/lib/admin/translation-configuration.ts
src/app/actions/translation-configuration.ts
src/components/admin/translation-configuration/translation-configurations-panel.tsx
src/components/admin/translation-configuration/translation-model-configurations.tsx
src/components/admin/translation-configuration/translation-model-configuration-form.tsx
focused unit/security tests
```

Advance the nested database dependency/gitlink only through the normal repository task workflow once DATABASE-001 is accepted; do not edit Prisma schema/migrations from Admin.

## Out of Scope

- Merchant Pricing builder changes;
- Merchant Pricing translation run creation/status;
- Background translation execution;
- changing Store Category request UI to use the default;
- new provider credentials/providers;
- deleting translation model configurations;
- any `_index.md` update.

## Requirements

1. Read and expose the new automatic-default field in the existing translation model view.
2. Display a clear `Automatic default` badge/state for the current default model.
3. Add an explicit `Set as automatic default` mutation for enabled models only.
4. The mutation must:
   - require existing `requirePlatformAdminMutation` authorization;
   - require `SUPER_ADMIN`;
   - validate model id and expected `editVersion`/current row state using existing CAS conventions;
   - execute atomically so the selected model becomes default and any previous default in the same environment/provider is cleared;
   - increment/edit audit versions consistently with current translation configuration actions;
   - write a bounded Commerce/Admin audit event using an appropriate existing/new audit action owned by the accepted database schema. If DATABASE-001 does not add an audit enum value, use an existing generic configuration audit mechanism only when semantically correct; do not silently skip audit.
5. Do not allow a disabled model to become default.
6. Existing enable/disable action must fail closed if asked to disable the current automatic default. Required UX meaning:

   ```text
   Choose another automatic-default translation model before disabling this model.
   ```

7. Creating a model does not silently make it default. The default designation is explicit and auditable.
8. If no default exists, show a clear configuration warning that automatic workflows such as Merchant Pricing translation are unavailable; do not guess the first enabled model.
9. Update current Store-Category-only explanatory copy so the page accurately describes platform translation model profiles while preserving Store Category behaviour.
10. Preserve double-submit guards and refresh/stale-write behaviour already present in translation configuration forms.

## Work Items

- [ ] Consume accepted DATABASE-001 schema.
- [ ] Extend translation configuration read model with default state.
- [ ] Add validated audited `set automatic default` server action/service path.
- [ ] Harden disable action against disabling the current default.
- [ ] Update Translation System Controls presentation and explanatory copy.
- [ ] Add focused tests for default selection, replacement, stale edit version, disabled-model rejection and default-disable rejection.
- [ ] Run repository-focused validation and record results.

## Interfaces / Contracts

Consumes:

- `CommerceTranslationModelConfiguration.automaticDefault` or the exact accepted DATABASE-001 equivalent;
- existing `CommerceTranslationProviderCredential`;
- existing platform-admin authentication/audit conventions.

Produces no cross-repository runtime contract. `ARCH-031-ADMIN-002` later resolves this database-backed default server-side.

## Dependencies

- `ARCH-031-DATABASE-001`.

## Enables

- `ARCH-031-ADMIN-003`.

## Acceptance Criteria

- [ ] System Controls visibly identifies the automatic default.
- [ ] `SUPER_ADMIN` can set a different enabled model as default in one operation.
- [ ] Replacing the default leaves exactly one default in that environment/provider.
- [ ] A stale edit/version cannot silently replace the default.
- [ ] Disabled models cannot be selected as default.
- [ ] The current default cannot be disabled until another default is chosen.
- [ ] No default state is inferred client-side from array order.
- [ ] No provider credential/model ID is exposed beyond existing safe configuration fields.
- [ ] Existing Store Category selectable-model workflow still functions.

## Validation

- [ ] focused unit tests for translation configuration read/validation helpers.
- [ ] focused security/server-action tests for SUPER_ADMIN/CAS/audit behaviour.
- [ ] `npm run lint` for changed files or repository-declared equivalent.
- [ ] `npm run build` if required by repository task conventions.
- [ ] `git diff --check`.

Do not claim provider connectivity; this task configures model selection only.

## Stop Condition

After Work Items, Acceptance Criteria and required Validation are complete, set status to `review`, return the Completion Report to `moda_architect` and STOP. Do not begin Merchant Pricing translation implementation.

## Implementation Notes

Keep the page modular. Extend the existing translation configuration components rather than introducing another System Controls page or duplicating credential/model state. The automatic default is a platform configuration property, not a Merchant Pricing form field.

## Completion Report

### Status

Not Started

### Files Changed

None.

### Work Completed

None.

### Validation Results

None.

### Deviations

None.

### Assumptions

None.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

Pending

### Review Notes

None.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending implementation review.

### Follow-up

None.
