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
status: pending
priority: 20
executor: null
claimed_at: null
attempt: 0
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
