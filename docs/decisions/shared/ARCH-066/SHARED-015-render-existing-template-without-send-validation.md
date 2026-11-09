---
id: ARCH-066-SHARED-015
architecture_id: ARCH-066
title: Render existing outreach template for Studio without send validation
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: developer
status: in_progress
priority: 20
executor: codex
claimed_at: 2026-11-09T01:35:53Z
attempt: 1
depends_on: ["ARCH-066-SHARED-012"]
enables: ["ARCH-066-SHARED-016"]
created: 2026-11-09
updated: 2026-11-09
---
# Render existing outreach template for Studio without send validation

## Objective and controlling scope
User explicitly requires Studio to use the existing template without template/WABA validation. Add a preview-only public renderer which substitutes existing component bindings without checking Meta approval, configured sender, WABA, registration lifecycle, drift, category, content hash or binding fingerprint. Existing production renderInitialOutreachPreview and Background send behaviour remain unchanged. No sender identity projection dependency (013/014/Admin001).

## Exact owned touch points
`src/commerce/outreach/template-contracts.ts`: export StudioOutreachTemplateSchema, StudioInitialOutreachRenderInputSchema and StudioInitialOutreachRenderResultSchema and inferred types. `render.ts`: add renderStudioInitialOutreachPreview and extract common substitution into NEW `component-render.ts`. `bindings.ts`: extract parameter construction without copying it; existing prepareFrozenComponents retains ALL current production checks before invoking common construction. `variables.ts`: allow both renderer inputs through a private structural type containing evaluation/variables/headerMedia/preparedBrand/preparedBrandMedia only; no public production type widening. `index.ts`: additive public exports. NEW `studio-render.test.ts`; existing render.test.ts/contracts.test.ts/test-fixtures.ts; README.md; scripts/validate-commerce-outreach.mjs. No source imports from Background/Commerce. No changes to assignment selection or production validation.

## Exact Zod contract
Reuse existing ComponentSchema, FrozenBindingsSchema, InitialOutreachRenderInputSchema, PreparedComponentSchema, ReadyMediaSchema and RenderReasonSchema; export existing component/binding schemas from public outreach index as required for typed consumer mapping. Do not copy their definitions.
```typescript
export const StudioOutreachTemplateSchema = z.strictObject({
  templateId: hostId,
  localeId: hostId,
  languageTag: z.string().min(1).max(512),
  components: z.array(ComponentSchema).min(1).max(4),
  bindings: FrozenBindingsSchema,
});
export const StudioInitialOutreachRenderInputSchema =
  InitialOutreachRenderInputSchema.omit({preparedProjection:true}).extend({
    template: StudioOutreachTemplateSchema,
  });
export const StudioInitialOutreachRenderResultSchema = z.discriminatedUnion('kind',[
  z.strictObject({kind:z.literal('ready'), renderedText:z.string().max(8192),
    parameters:z.array(PreparedComponentSchema).max(4), headerPreview:ReadyMediaSchema.nullable(),
    templateId:hostId, localeId:hostId, templateValidation:z.literal('NOT_EVALUATED')}),
  z.strictObject({kind:z.literal('refused'), reasonCode:RenderReasonSchema}),
]);
```
The input has no registration, provider status, WABA, sender, hash or fallback projection. Structural parsing and missing placeholder/value handling are necessary to render; they do not validate approval/send readiness. safeParse failure returns INVALID_REQUEST; unresolved bindings use existing typed reasons. No automatic template substitution, registration lookup, rehash, approval check or text fallback selection. Missing IMAGE data returns MEDIA_NOT_READY; host may select an existing TEXT template explicitly on a later request, never pretend image was rendered.

## Deterministic algorithm
Parse input; preserve existing same-shop brand/media checks; resolve variables using existing PreparedVariableResolver semantics; construct provider parameters in existing frozen order and substitute HEADER/BODY/FOOTER using shared common construction. Enforce existing component/parameter limits and BODY4096/fulltext8192 limits. Missing/unmatched placeholders refuse BINDINGS_INVALID; missing required values use existing reasons. Common function receives components/bindings/resolver only, never registration/category/hash. The production wrapper performs its existing registration/hash/category validation first and calls that same function. Preview calls it directly. Do not invent a registration or dummy WABA/hash to pass production validation. No database/network/model work in renderer. Returned IDs identify input source only, not send approval.

## Acceptance and exact checks
Positive preview fixture renders existing components with no Meta/sender metadata and exact same parameters/body as production when both receive equivalent valid template/facts; production invalid approval/hash/category fixtures still refuse. Preview input cannot accept extra approval/WABA fields. Assert binding/value errors,4096/4097 body boundaries, ready image/text, same-shop media/brand rules and old production golden bytes unchanged. Shared renderer performs zero selection/provider calls. Run `npx tsx --test src/commerce/outreach/*.test.ts`, `npm run typecheck`, `npm run build`, `npm run validate:commerce-outreach`; public build runtime/declaration smoke must include new exports. Retain accepted 5.9.0 changes; no package publish/version edit in015.

## Execution and completion boundary
Definition only. Preserve unrelated work; you are not alone in the codebase. Use canonical launcher task worktrees and mirrored task branches. Record exact source, commands/results and package integrity; submit for review, stop and retain developer completion authority. No main merge/push, deployment, real customer send, Meta call, database mutation in a hosted environment or follow-on task execution is authorized. No acceptance from tests against injected simulation alone.

## Completion Report
Not started. No implementation or validation performed.

## Code-level amendment — 2026-11-09

This amendment is normative. Code below defines required signatures and replacements; relocation of unchanged parameter/substitution bodies is specified by exact existing symbols rather than a second implementation. Do not add production validation to the Studio path.

### 1. Split parameter construction from production validation

In `bindings.ts`, export this function (keep it in this file so it can reuse private strictComponents/parseFrozenBindings/textMatchesFrozenBindings):
```typescript
export function prepareStoredComponents(input: {
  components: unknown;
  bindings: unknown;
  variables: PreparedVariableResolver;
}): { components: readonly PreparedMetaComponent[] } {
  const approved = strictComponents(input.components);
  const frozen = parseFrozenBindings(input.bindings);
  const variables = input.variables;
  // Move the existing block starting `const result: PreparedMetaComponent[] = []`
  // through the matchedBody/matchedHeader/matchedButtons check here unchanged.
  // Finish with `return { components: result };`.
}
```
The existing production `prepareFrozenComponents` retains every statement from `const { registration, variables } = input` through category/hash validation. Replace only its parameter-construction block with:
```typescript
return {
  ...prepareStoredComponents({
    components: approved,
    bindings: frozen,
    variables,
  }),
  bindingFingerprint: fingerprint,
};
```
Do not move adminFrozenDigest, category, submittedContentHash, locale.contentHash or registration validation into prepareStoredComponents. Do not export prepareStoredComponents publicly: it is an internal renderer helper. Existing structural placeholder checks merely ensure the stored content can be substituted; they must never query approval or decide whether a template can be sent.

### 2. Share text substitution without copying production rendering

NEW `component-render.ts` exports:
```typescript
import type { z } from 'zod';
import type { ComponentSchema, PreparedComponentSchema } from './template-contracts.js';
import { BindingUnavailable } from './variables.js';
type Component = z.infer<typeof ComponentSchema>;
type ParameterComponent = z.infer<typeof PreparedComponentSchema>;
export function renderStoredComponentText(
  components: readonly Component[],
  parameters: readonly ParameterComponent[],
): string {
  function substitute(text: string, type: 'header'|'body'): string {
    const values = parameters.find(p => p.type === type)?.parameters ?? [];
    return text.replace(/\{\{([1-9][0-9]*)\}\}/g, (_, position: string) => {
      const value = values[Number(position)-1];
      if (!value || value.type !== 'text') throw new BindingUnavailable('BINDINGS_INVALID');
      return value.text;
    });
  }
  const body = components.find(c => c.type === 'BODY');
  if (!body || body.type !== 'BODY') throw new BindingUnavailable('BINDINGS_INVALID');
  if (substitute(body.text, 'body').length > 4096)
    throw new BindingUnavailable('MESSAGE_TOO_LARGE');
  const text = components.flatMap(c => {
    if (c.type === 'BODY') return [substitute(c.text, 'body')];
    if (c.type === 'FOOTER') return [c.text];
    if (c.type === 'HEADER' && c.format === 'TEXT') return [substitute(c.text, 'header')];
    return [];
  }).join('\n');
  if (text.length > 8192) throw new BindingUnavailable('MESSAGE_TOO_LARGE');
  return text;
}
```
Add MESSAGE_TOO_LARGE to internal TemplateUnavailableReason (it already exists in RenderReasonSchema) so BindingUnavailable is typed; retain all old reason members. Replace production render.ts's existing BODY/header/footer text-substitution block with a call to renderStoredComponentText(registration.componentsSnapshot, prepared.components). Existing production selection/provenance/result parsing remain unchanged. Existing golden bytes must remain identical.

### 3. Add the Studio renderer

In variables.ts change only the constructor input type to this internal type, allowing the new input without preparedProjection:
```typescript
type VariableInput = Pick<InitialOutreachRenderInput,
  'evaluation'|'variables'|'headerMedia'|'preparedBrand'|'preparedBrandMedia'>;
// constructor(private input: VariableInput, private languageTag: string,
//             private sendable: SendableOutreachOffer) {}
```
Extract the existing preparedBrand tenant and preparedBrandMedia role/URL checks from render.ts into private `validatePreparedAssets(input: VariableInput): RenderReason|null` and invoke it in BOTH entrypoints after parsing; same branch order/reasons. Do not add template metadata to this helper.

Add these imports to render.ts from existing modules: Studio schemas/types from template-contracts; prepareStoredComponents from bindings; renderStoredComponentText from component-render. Add:
```typescript
export function renderStudioInitialOutreachPreview(
  raw: StudioInitialOutreachRenderInput,
): StudioInitialOutreachRenderResult {
  const parsed = StudioInitialOutreachRenderInputSchema.safeParse(raw);
  if (!parsed.success) return {kind:'refused', reasonCode:'INVALID_REQUEST'};
  const input = parsed.data;
  const assetError = validatePreparedAssets(input);
  if (assetError) return {kind:'refused', reasonCode:assetError};
  try {
    const sendable = selectSendableOutreachOffer(input.evaluation.offerDecision);
    const prepared = prepareStoredComponents({
      components: input.template.components,
      bindings: input.template.bindings,
      variables: new PreparedVariableResolver(input, input.template.languageTag, sendable),
    });
    const image = input.template.components.some(c => c.type==='HEADER' && c.format==='IMAGE');
    return StudioInitialOutreachRenderResultSchema.parse({
      kind:'ready',
      renderedText:renderStoredComponentText(input.template.components, prepared.components),
      parameters:prepared.components,
      headerPreview:image ? input.headerMedia : null,
      templateId:input.template.templateId,
      localeId:input.template.localeId,
      templateValidation:'NOT_EVALUATED',
    });
  } catch (error) {
    return {kind:'refused', reasonCode:error instanceof BindingUnavailable
      ? error.reason : 'BINDINGS_INVALID'};
  }
}
```
No call to selectRecoveryAssignment or prepareFrozenComponents occurs in this function. No mocked/fabricated registration is allowed. Keep their production callers intact. All required schemas are the exact code in the preceding contract section, not a second shape. Public index exports the three Studio schemas, three inferred types, ComponentSchema/FrozenBindingsSchema and renderStudioInitialOutreachPreview. New component-render.ts remains internal; add it and template-types.ts to owned touch points. Earlier instruction to move parameter construction into component-render.ts is superseded: bindings.ts owns parameter construction, component-render.ts owns only text substitution.

### Review evidence
Provide a path/symbol checklist showing production checks still in prepareFrozenComponents/selectRecoveryAssignment, and their absence in Studio. Tests must spy on selection and prove it is not called by Studio; compare exact production/previews parameters and text for identical valid stored content. A failing production metadata test must remain failing closed, while Studio input has no corresponding metadata fields. The above is task-definition code, not claimed implemented source.


## Mandatory shared-component ownership and reuse — 2026-11-09

This section controls earlier ambiguous wording. Shared means implementation in the published `@modainteract/moda-interact-shared` package, consumed through its public entrypoints. A helper placed only in Commerce or duplicated between services does not meet this requirement.

| Responsibility | Sole implementation owner | Consumers |
|---|---|---|
| Preview template/input/result Zod schemas and inferred types | Shared outreach/template-contracts.ts, public outreach exports | Commerce; Shared tests |
| Placeholder-to-parameter construction | Shared outreach/bindings.ts prepareStoredComponents | Both Shared production and Studio renderer entrypoints |
| Header/body/footer text substitution and length handling | Shared outreach/component-render.ts renderStoredComponentText | Both Shared renderer entrypoints |
| Variable/brand/media resolution | Existing Shared PreparedVariableResolver | Both Shared renderer entrypoints |
| Offer presentation classification and INITIAL purpose mapping | Existing Shared selectSendableOutreachOffer and purposeFor | Both Shared renderer paths; Commerce host selecting frozen content |
| Production registration/approval/hash/sender validation | Existing Shared production entrypoint and Background sending pipeline | Production only; never Studio renderer |
| Database query, selected-shop authorisation, credentials, preview lifecycle/storage and UI | Commerce | Studio only; these are host adapters, not Shared business logic |

### Exact public API addition in SHARED-015

Add to `src/commerce/outreach/index.ts`:
```typescript
export { selectSendableOutreachOffer } from './sendable-offer.js';
export type { SendableOutreachOffer } from './sendable-offer.js';
export { purposeFor } from './selection.js';
```
These export the existing implementations; do not create wrappers, a second classifier or a copied purpose switch. Preserve the exact existing function signatures and inferred return type. Verify SendableOutreachOffer is the existing exported type; if declaration emission requires an existing referenced type, expose that type additively without changing its shape.

COMMERCE-003 imports those helpers from the public outreach entrypoint and uses:
```typescript
const sendable = selectSendableOutreachOffer(evaluation.offerDecision);
const purpose = purposeFor('INITIAL', sendable.presentation);
```
It must not implement its own no-offer/code/automatic mapping. Shared owns reusable semantic decisions; Commerce freezes/selects existing database content using the resolved purpose. The Commerce presentation adapter delegates once and contains no substitution, brand resolution, template approval, hash validation or message-length algorithm.

### Required proof before acceptance

1. Inspect real call sites: production prepareFrozenComponents and renderInitialOutreachPreview delegate to the same Shared prepareStoredComponents/renderStoredComponentText used by renderStudioInitialOutreachPreview. No parallel replacement bodies remain.
2. Shared tests exercise both entrypoints using identical content/variables and assert exact parameters/full text. Production validation still refuses invalid production metadata; Studio does not consume that metadata.
3. Commerce tests invoke the actual installed published renderer and purpose helpers; do not mock them in the parity acceptance test. Mock only host I/O, clocks and external provider/model boundaries. Assert no service-local rendering/classification algorithm or cross-repository source/internal-dist import.
4. SHARED-016 installed-artifact JS/declaration smoke includes the new purpose/classification exports as well as the Studio schemas/renderer. Record the exact accepted package version/integrity in Commerce's report.
5. Review removes replaced duplicate code and verifies old production golden bytes remain unchanged. Merely naming a file “shared” or passing tests against copied helper code is insufficient.

No new standalone service, database table, sender projection or UI component in Shared is introduced. Existing Background consumers use the same common code through their existing production renderer; no Background package change is part of these tasks.


## Architect eligibility reconciliation — 2026-11-09
Sole explicit prerequisite SHARED012 is CompleteAcceptedAttempt1, canonical remote4b5ff8d7f1b45516357152baa49f0a81d710ad69. Pending was stale eligibility; promoted Ready unchangedAttempt0/unclaimed. Exact latest normative code/reuse amendments govern execution. No sender projection chain dependency is introduced. Developer explicitly invoked015 implementation/sync/claim/source/report publication; canonical prepare alone owns the next claim.
