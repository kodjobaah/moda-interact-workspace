---
id: ARCH-066-COMMERCE-003
architecture_id: ARCH-066
title: Remove template and sender validation from Studio outreach preview
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: developer
status: in_progress
priority: 20
executor: codex
claimed_at: 2026-11-09T02:29:13Z
attempt: 1
depends_on: ["ARCH-066-SHARED-016"]
enables: []
created: 2026-11-09
updated: 2026-11-09
---
# Remove template and sender validation from Studio outreach preview

## Objective
Remove template/WABA validation from Studio initial-outreach preview. Use the existing selected template content/bindings directly with Shared's preview-only renderer. This separate correction owns removal of the SENDER_UNAVAILABLE stub and template/sender prerequisites; COMMERCE002 retains all remaining unfinished host/evaluator/lifecycle work. Never mark002 Complete merely because this correction passes.

## Exact touch points
`package.json`/lock: exact016 artifact/integrity. `lib/preview/initial-outreach-runtime.ts`: remove unconditional sender-unavailable refusal; no sender-identity read/decryption. `src/commerce/preview/initial-outreach/{contracts,presentation,service,ports}.ts`: renderer dependency uses renderStudioInitialOutreachPreview; add NEW `template-reader.ts` for existing template content. `lib/preview/initial-outreach-http.ts` and existing collection/status/cancel routes: preserve selected-shop authorization and request schema. `src/studio/test-conversations/initial-outreach-preview-panel.tsx`: show source template/locale and final text; label “Template validation not evaluated. No message sent.” Existing initial-outreach service/UI fixtures and NEW `tests/arch066-initial-outreach-template-reader.test.ts`. Resolve actual existing configuration reader symbol by inspection and record path; no parallel configuration store. No Admin/Background/Shared source edits.

## Source selection and data mapping
Use existing selected-shop assigned initial template and existing locale-resolution precedence already implemented by Background's configuration reader, read-only; document actual reader/query path before editing. Filter for selected shop and evaluated initial purpose (no offer/code/automatic). Do not filter on Meta approval/status, registration submission state, enabled registration, configured sender/WABA, drift/category/hash/fingerprint. Use configured template assignment and stored locale component/binding snapshot; missing stored content returns typed configuration TEMPLATE_UNAVAILABLE, never fabricate components. Preserve established locale precedence; ties at the same precedence refuse AMBIGUOUS_TEMPLATE rather than choose an arbitrary row. Do not infer sender from assignment. Map existing definition/locale IDs, languageTag, componentsSnapshot and parameterBindingsSnapshot into Shared StudioOutreachTemplateSchema. No extra Meta lookup/revalidation/register/send. Current shop authorization and approved ready media access remain host data boundaries; these are not template approval checks.

## Runtime correction boundary
Delete imports/calls/readers for messaging.sender, messaging.senderIdentity, sender projection version checks and production selectRecoveryAssignment/renderInitialOutreachPreview from this preview path. Wire presentation to public renderStudioInitialOutreachPreview with actual stored template/facts, existing saved-brand data and ready media. No dummy WABA, approved status, hash or registration creation. Use production-independent template result type and NOT_EVALUATED marker. Keep same-origin/SUPER_ADMIN/tenant/checkout checks, live product evaluator, cancellation/budget/storage checks and no-side-effect rules. Missing template/content/variables yields precise refusal, not generic sender-unavailable. If genuine evaluator host integration is still unavailable, expose that specific configuration failure and retain002 incomplete; injected simulation never becomes default live service.

## Required tests/review
Prove preview with stored template works without messaging.sender/projection and with mocked non-approved/stale-hash metadata: metadata must not enter renderer input or gate result. Assert zero sender-secret, sender-projection, Meta/registration/send accesses. Missing components and unresolved placeholders refuse precisely; cross-shop selection remains rejected before I/O. Compare parameters/full body to016 and Background's identical valid-content golden; preserve both-platform checkout live reads and no mutation spies. Run existing `tests/arch066-initial-outreach-preview.test.ts`, `tests/arch066-initial-outreach-store.test.ts`, `tests/arch066-initial-outreach-ui.test.tsx` plus new reader tests via Vitest, production typecheck and changed-file ESLint. Report actual remaining002 gaps explicitly.

## Coordination handoff
At review, architect removes SHARED014 and ADMIN001 sender prerequisites from COMMERCE002 and records this correction's accepted source/artifact;013/014/Admin001 are unnecessary for Studio and their historical reports are preserved. Do not execute those tasks or claim they are completed. Existing Background production renderer/send validation stays unchanged. This task does not depend on blocked002 (avoids cycle); reuse its published partial source via normal main/task integration only, record exact baseline and preserve its work. Keep task Pending until016 Complete and partial002 source available on canonical implementation baseline; no cherry-pick selected unreviewed files silently.

## Execution and completion boundary
Definition only. Preserve unrelated work; you are not alone in the codebase. Use canonical launcher task worktrees and mirrored task branches. Record exact source, commands/results and package integrity; submit for review, stop and retain developer completion authority. No main merge/push, deployment, real customer send, Meta call, database mutation in a hosted environment or follow-on task execution is authorized. No acceptance from tests against injected simulation alone.

## Completion Report
Not started. No implementation or validation performed.

## Code-level amendment — 2026-11-09

### 1. Exact removals from the existing partial implementation

Remove this entire unused port from `src/commerce/preview/initial-outreach/ports.ts`:
```typescript
export interface InitialOutreachSenderIdentityPort {
  read(environment:string):Promise<{businessAccountId:string;sourceVersion:number}|null>;
}
```
Remove OutreachConfigurationError (whose reasonCode is SENDER_UNAVAILABLE) and the unconditional `throw new OutreachConfigurationError()` from `lib/preview/initial-outreach-runtime.ts`. Do not replace them with dummy sending credentials or a stub that claims live readiness. COMMERCE002 still owns construction of the real host factory; after this correction its factory has no sender prerequisite. If that factory is not implemented, report the outstanding002 work explicitly and do not accept a success-returning simulation as completion. Keep test injection confined to tests.

Remove any preview-only reads/imports for messaging.sender/messaging.senderIdentity, source-version checks, selectRecoveryAssignment and production renderInitialOutreachPreview. Do not edit Background callers or remove production Shared exports.

### 2. Replace the presentation adapter exactly

Replace `src/commerce/preview/initial-outreach/presentation.ts` with:
```typescript
import {
  renderStudioInitialOutreachPreview,
  type InitialOutreachEvaluationResult,
  type StudioInitialOutreachRenderInput,
} from '@modainteract/moda-interact-shared/commerce/outreach';
export function renderFrozenOutreach(
  evaluation: Extract<InitialOutreachEvaluationResult,{kind:'ready'}>,
  frozen: Omit<StudioInitialOutreachRenderInput,'schemaVersion'|'evaluation'>,
) {
  return renderStudioInitialOutreachPreview({schemaVersion:1,evaluation,...frozen});
}
```
In ports.ts replace imported InitialOutreachRenderInput with StudioInitialOutreachRenderInput and change `presentation: Omit<InitialOutreachRenderInput,'schemaVersion'|'evaluation'>` accordingly. In contracts.ts replace InitialOutreachRenderResultSchema import/use with StudioInitialOutreachRenderResultSchema. Preserve 64KiB result cap, existing ready/refused envelope, run ownership and productionChecks NOT_EVALUATED.

### 3. Exact stored content query and mapping

NEW template-reader.ts reads the existing assigned variant relation, not Meta and not localeAst compilation. The host supplies shopId plus evaluated purpose and ordered languageTags from its existing resolved language context. Preserve order; deduplicate tags without sorting. For each tag run:
```typescript
const rows = await db.whatsAppTemplateVariant.findMany({
  where: {shopId, purpose, languageTag},
  orderBy: {id:'asc'},
  take: 2,
  select: {
    id:true,
    metaRegistration: {
      select: {
        componentsSnapshot:true,
        parameterBindingsSnapshot:true,
        locale: {select:{id:true, languageTag:true}},
      },
    },
  },
});
```
No predicate/select of providerAccountId, approval/status, enabled, drift/hash/category or current sender is added. Stop on first nonempty language tier: >1 rows => AMBIGUOUS_TEMPLATE; one row without registration/content => TEMPLATE_UNAVAILABLE (the relation supplies existing content, not proof of approval). No rows across all tiers => TEMPLATE_UNAVAILABLE. Do not fall through a conflicting/missing-content tier to another language. Map exactly:
```typescript
const template = StudioOutreachTemplateSchema.parse({
  templateId: row.id,
  localeId: row.metaRegistration.locale.id,
  languageTag: row.metaRegistration.locale.languageTag,
  components: row.metaRegistration.componentsSnapshot,
  bindings: row.metaRegistration.parameterBindingsSnapshot,
});
```
Catch schema failure as TEMPLATE_CONTENT_UNRENDERABLE; never invent/repair or rehash content. Expose local reader error with fixed reasonCode and map to CONFIGURATION refusal through the existing HTTP/service error path; no raw DB/template body logs. Shop authorization occurs before reader call. This query deliberately does not check Meta approval; it only locates stored content for rendering.

### 4. When content is selected

Evaluation determines no-offer/code/automatic purpose, so do not guess from policy before evaluation. Freeze read-only template candidates for all three purposes using the query above during host.freeze; this is a bounded map of at most three successful templates plus typed per-purpose absence/ambiguity. Freeze same languageTags, brand/media/variables and source IDs with the run. After ready evaluation use existing public selectSendableOutreachOffer, then the public Shared purposeFor('INITIAL', sendable.presentation) helper (no local mapping); no provider call or template reread at render time. Add a local `FrozenInitialPresentation` strict interface `{templates: Record<InitialPurpose, StudioOutreachTemplate|null>, templateErrors: Partial<Record<InitialPurpose, 'TEMPLATE_UNAVAILABLE'|'AMBIGUOUS_TEMPLATE'|'TEMPLATE_CONTENT_UNRENDERABLE'>>, variables, headerMedia, preparedBrand?, preparedBrandMedia?}` where variables/media types are indexed from StudioInitialOutreachRenderInput. Pass only selected template and these variables/assets to renderFrozenOutreach. Missing selected purpose returns its fixed refusal, no arbitrary template fallback. Hash frozen map for run replay identity only; do not compare it to any saved registration hash. Update service.ts/ports.ts and fixture hosts together. Partial host dependencies still belong to002; no new sender tasks.

### 5. UI and tests

Replace accesses to rendering.templateProvenance (not present in Studio result) with rendering.templateId/localeId. Display exact ready text/parameters/header plus “Template validation not evaluated. No message sent.” Do not display an approval/readiness badge. Keep mode LIVE_READ_ONLY/SIMULATION and productionChecks labels.

Reader fixture verifies exact query predicate/select, locale priority and ambiguity; a supplied declined/disabled/stale-hash registration renders because none of those fields is selected or evaluated. Spies throw on sender/Meta access and must never fire. Missing content/placeholder is shown as render/configuration failure. Rerun all tests specified above and add result-schema/UI assertions for the new result type. No implementation can be accepted merely by deleting the sender stub; the selected stored-content→Shared renderer path must actually execute in service tests.


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


## Architect readiness handoff — 2026-11-09
SHARED016 explicitly CompleteAcceptedAttempt1; exact public artifact5.10.0 integrity sha512-cdXKp0YLPg/yFN5acZNpdZbDfzFqY1MV45rFHh1+Q1e8Wf3VFuR1Ylgr8icorCj9h8pE3CTFTheUuxCEMKCfFw==; downloadedSHA256711fe20dfe54f6516e67eab0f6616e7799d4f9d567c93d90819e4eb974f4ac2d. Adopt exact version/integrity, never range/latest/sibling source. Ready unchangedAttempt0/unclaimed; canonical prepare owns future claim. Existing latest code-level/reuse amendments control. COMMERCE002 remains BlockedAttempt1 with unfinished real-host/lifecycle requirements; correction does not imply full preview completion. Withdrawn sender013/014/Admin001 remain withdrawn; production validation unchanged.


## Architect explicit source-composition amendment — 2026-11-09
Prepared canonical implementation baseline64cdb570940c72097bb3eb9097e159afc1472643 does not contain the published partial002source078f67a2187ba4701e2fbbf49fa2185837ae9bf7. Developer explicitly authorizes continuing this correction and preserving that published implementation. Repository owner may carry the ENTIRE exact078f67commit onto this isolated003task branch by normal non-forced cherry-pick, recording resulting commit and original provenance; do not cherry-pick selected unreviewed files silently, rewrite history, merge/push main or label002Accepted. This bounded integration satisfies availability for003source work and supersedes the earlier wait-for-canonical-baseline clause only for this exact published commit. Required003checks run on the actual composed task tree. No unfinished002real-host/lifecycle scope is transferred: if factory absent, explicit precise host-unavailable remains, never default simulation/live success. Stored-template→actual installed Shared renderer path must execute in003service tests; all other current acceptance/reuse and production safety requirements remain.
