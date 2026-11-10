---
id: ARCH-068-ADMIN-001
architecture_id: ARCH-068
title: Author and preview optional AI wrapper media
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 30
executor: null
claimed_at: null
attempt: 1
depends_on: ['ARCH-068-SHARED-003']
enables: ["ARCH-068-ADMIN-002"]
created: 2026-11-09
updated: 2026-11-10
---
# Author and preview optional AI wrapper media

## Architecture and objective
Implement the owned portion of [binding ARCH-068](../../../architecture/ARCH-068-optional-conversation-product-image.md). The entire contract is normative, including exact schemas, transport/failure rules, initialization, rollout and acceptance matrix. Read it before execution.

## Context and scope
ADMIN-001 consumes Shared publication. Touch authoring/{types,validation,compiler,preview}.ts, compilation/{wrapper-compiler,reconstruction,contracts}.ts, wrappers/{eligibility,preview,service}.ts, translation source snapshot/protected binding checks, DTO/server actions/routes that carry draft/prepared/preview, components under authoring (template-content-editor, wrapper-structure-editor, template-read-only-preview, template-editor-steps) and wrappers/wrapper-before-after-preview/compilation/conversation-wrapper-review-preview. Add a wrapper-only toggle default false with explanatory “One verified product image above the response; omitted when unavailable” and an illustrative preview. Uses exact shared schema. Binding preserved in compile/clone/translation/review, included source/prepared hashes; locale eligibility requires binding equality across all locales. Meta AST rejects this key; HUMAN/SHARED wrapper editor rejects it for this phase; supported audience AI only, checked server-side. Existing text URL fields remain text. Do not fetch live merchant images in Admin preview or read R2 secrets there.

The initializer script is owned by ADMIN-002; do not implement or run it in this task.

## Interfaces and contracts
The named exported schemas/APIs and exact JSON shapes in the binding contract are authoritative. Existing v1 template hashes/legacy records remain compatible. No clothing-specific fields/model image URL or Meta recovery contract extension.

## Work Items
- [x] Verify dependencies and current owned source against binding touch points.
- [x] Implement every requirement in the owned scope and binding contract.
- [x] Add deterministic success/failure/compatibility tests specified above.
- [x] Run declared repository validation and record exact evidence.
- [x] Publish implementation and parent report on mirrored task branches for review.

## Dependencies
ARCH-068-SHARED-003

## Acceptance criteria
All owned scope above is complete, exact contract tests pass and no TODO/placeholder or unresolved cross-service choice remains. For tasks consuming Shared, prove the dependency using the exact published artifact; no sibling source imports/copied mechanics. Record actual changed paths and checks. Preserve existing grounded text, product identity, moderation/send fences, initial/proactive Meta flows.

## Out of Scope
No redesign of aspects 1 and 3, Meta submission/WABA validation, inventory write, unrelated cleanup, budget increase, production mutation or automatic live initializer.

## Agent execution and review
Execution is owned by the assigned agent, not a human developer. Use /moda-task with canonical isolated parent/implementation worktrees and mirrored task branches. Do not claim on authoring. Implement only this repository portion; use published Shared APIs. If an actual source conflict contradicts the exact binding contract, report it to the architect with path/symbol/evidence; do not invent a replacement architecture or leave a placeholder. No main merge/push, production mutation, real send or live initializer execution is part of this task.

## Completion Report

Ready for Review — Attempt 1, 2026-11-10. Implementation and validation are complete; independent architect acceptance is pending. Existing regression/lint findings are recorded explicitly below.

### Implementation and published dependency

Admin implementation `31e24c04d532e364e4c4e4bf6eb959e51ec01c07` is committed/pushed and clean on `task/ARCH-068-ADMIN-001`, based on prepared source `b57869d14d389e7bd2e80220a29b64562270069d`.

Pinned the exact public `@modainteract/moda-interact-shared@5.12.0` artifact. package-lock records registry tarball https://registry.npmjs.org/@modainteract/moda-interact-shared/-/moda-interact-shared-5.12.0.tgz and accepted SRI `sha512-RD3pGDVZHK8sRwbi91SpdouRDVkyf+4rhdB4eczaG48avsnEOQRhRccqzX2YI9KhXa1jXE4S2LHfz7D9DR5PEw==`. The published schema/type/reader is imported through `/commerce/presentation`; no copied schema, sibling-source import or Node media import is used. Lock comparison shows Shared3.0.0→5.12.0 is the only existing package version change, 27 new transitive entries, no removals. No new package was published by this task.

- AI wrappers expose a default-off Optional product image checkbox. It emits the exact shared binding and removes the property when off or when switching to HUMAN/SHARED. Server AST validation uses the public strict schema and rejects non-AI audiences, Meta AST fields, null/undefined/duplicate/nonoptional/inline/URL bindings and image tokens masquerading as text variables.
- Binding is preserved in source, compiled prepared data, clone and preview DTOs and their existing canonical hashes. Omission retains legacy source/prepared shapes and hashes. The public prepared-wrapper reader accepts the generated projection and digest.
- Translation sends only existing text segments. Binding remains in immutable English and is protected by its source hash, copied during reconstruction and compared across all reviewed locales. The strict Background translation transport was inspected read-only; no new transport member or worker change is required. Opted-in snapshot preparation also checks compiled binding/content equality; legacy records retain their prior acceptance.
- Real source extraction emits .text/occurrence keys whereas review previously consumed component keys only. The owned compilation adapter now verifies/restores the actual extractor format (including wrapper body regions around the protected response slot), while retaining historical component-key records. Initial Meta Reply instructions and existing text/URL bindings remain protected; no Meta authoring/send behavior is changed.
- Authoring, locale review and before/after activation previews show the same local SVG illustration above the complete wrapped response. No merchant image, product, credential, R2 or provider is loaded. UI explains omission and full-text fallback. README records deployed-consumer readiness before activation and the separate ADMIN002 initializer boundary.

### Owned touch-point trace

`compileWrapperLocale` delegates to the enhanced `compileTemplateAst`; `reconstructAndCompile` delegates to the enhanced snapshot verification/restoration and compiler. `CompilationCandidate`, review DTOs, wrapper preview definitions and server actions already carry the enhanced authoring/prepared/preview types without narrowing or rebuilding their properties. `saveEnglishTemplate`/its existing transaction persist the complete record, while wrapper activation service calls the enhanced locale eligibility check. `TemplateContentEditor` delegates to `WrapperStructureEditor`; editor step navigation retains parent-owned draft state. These existing forwarding points were traced and tested without unnecessary edits. Clone remains structuredClone of the complete AST.

### Changed files (implementation-repository relative)

- README.md
- package.json
- package-lock.json
- scripts/test-arch068-admin-authoring.mjs
- src/lib/admin/whatsapp-templates/authoring/types.ts
- src/lib/admin/whatsapp-templates/authoring/validation.ts
- src/lib/admin/whatsapp-templates/authoring/compiler.ts
- src/lib/admin/whatsapp-templates/authoring/draft-operations.ts
- src/lib/admin/whatsapp-templates/authoring/preview.ts
- src/lib/admin/whatsapp-templates/compilation/segments.ts
- src/lib/admin/whatsapp-templates/compilation/restoration.ts
- src/lib/admin/whatsapp-templates/translations/source-snapshot.ts
- src/lib/admin/whatsapp-templates/wrappers/eligibility.ts
- src/lib/admin/whatsapp-templates/wrappers/preview.ts
- src/components/admin/whatsapp-templates/authoring/conversation-product-image-example.tsx
- src/components/admin/whatsapp-templates/authoring/wrapper-structure-editor.tsx
- src/components/admin/whatsapp-templates/authoring/template-family-purpose-selector.tsx
- src/components/admin/whatsapp-templates/authoring/template-read-only-preview.tsx
- src/components/admin/whatsapp-templates/authoring/template-review-summary.tsx
- src/components/admin/whatsapp-templates/compilation/conversation-wrapper-review-preview.tsx
- src/components/admin/whatsapp-templates/wrappers/wrapper-before-after-preview.tsx
- tests/unit/arch068-conversation-product-image.test.ts
- tests/unit/arch068-conversation-product-image-components.test.tsx

### Validation and limits

- `npm run test:arch068-admin-authoring`: **14 passed, 0 failed/skipped**. Covers default/toggled-off compatibility, strict AI-only schema, public reader/hash interoperability, clone/previews/audience switching, real and historical translation formats, all20 current canonical locales, binding/marker tampering and stale source hashes, immutable locale binding equality even with recomputed hashes, forged server requests, atomic persistence/audit, legacy Meta snapshot compatibility and all three preview surfaces.
- Native ESM runner against 12 existing authoring, translation, compilation, wrapper service/component and media-compiler test files: **89 passed, 1 inherited failure, 0 skipped (90 tests)**. The failure is unchanged `arch049-admin-media-compiler.test.ts` “each IMAGE header role compiles…”: its expected two body bindings omit the already-existing initial `checkout.itemsSummary`, while baseline produces three. A separate temporary bundle loaded original src/tests directly via `git show b57869d...` and reproduced exactly this same 1-failure/4-pass media result. No expectation was loosened or unrelated source changed. Initial Reply/Meta/protected-marker and wrapper regressions pass. The earlier native ESM Next/link resolution issue was fixed in the task test runner; it is not a remaining failure.
- `npx tsc --noEmit`: passed (empty diagnostics). Final production `npm run build`: **passed**, including existing Prisma generation, optimized webpack build, Next TypeScript checks and route generation. Known BullMQ expression/optional Valkey module build warnings remain nonfatal; BullMQ version and source are unchanged.
- Changed-file `npm run lint -- <changed source/helper paths>`: passed. Final delta checks for snapshot verification also passed. Full `npm run lint` reports **1 inherited error/3 warnings**: unchanged `media/use-shop-brand-media-role.ts` react-hooks/set-state-in-effect and two hook warnings, plus unchanged database/eslint.config.mjs default-export warning. The hook is byte-identical to the prepared baseline and no source/helper changed-file diagnostic remains. No matching durable baseline ID was found; this task records the concrete observation without editing unrelated hook/Database work.
- Browser esbuild graph of the actual authoring validator and wrapper editor: passed; excludes Node builtins, AWS SDK, sharp, Prisma, logging and observability. Published lock SRI equality, dependency-diff audit and git diff/staged checks passed.
- All commands ran in the canonical implementation worktree with workspace-bootstrap Node24.19.0/npm11.17.0. The task ESM runner leaves npm packages external and bundles only repository-local tests; no source alias to Shared is used. Native Next test imports resolve to their installed files. No local DB query/mutation or provider/network media call was required; Prisma generation changes only installed/generated client artifacts.

Temporary validation evidence: /tmp/arch068-admin001-focused-final.log, /tmp/arch068-admin001-regressions-final.log, /tmp/arch068-admin001-extra-checks.log, /tmp/arch068-admin001-types-final.log, /tmp/arch068-admin001-changed-lint.log, /tmp/arch068-admin001-final-delta-lint.log, /tmp/arch068-admin001-lint.log and /tmp/arch068-admin001-build-final.log. The immutable-baseline and browser probes are temporary validation artifacts, not production code.

### Git / VCS and physical isolation

Both repositories use `task/ARCH-068-ADMIN-001`.

- Canonical workspace: /Users/kwadwoadomafriyie/project/moda-interact-workspace.
- Parent worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-068-ADMIN-001, reused; parent remote task fast-forward not-needed; origin/main incorporated yes, preclaim head2e175c89e5cfd47c12f1e3412aceeb16973fb5c9.
- Implementation worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-068-ADMIN-001, created at b57869d14d389e7bd2e80220a29b64562270069d; remote task fast-forward not-needed; origin/main already-current.
- Launcher recursive implementation submodule sync/update passed; ready; database initialized at recorded5329d5390d346042895219663f3a040ea54ae168. No gitlink changed.
- Durable parent claim55de683403f8fe191f5e3c73b20d14869613cf7b, pushed; Attempt1, executor codex, claimed2026-11-10T00:02:31Z. No repeated claim or attempt increment.
- Shared/default workspace and implementation checkouts switched/mutated for task execution: no. Another task worktree reused: no.
- Implementation HEAD and origin/task/ARCH-068-ADMIN-001 match31e24c04d532e364e4c4e4bf6eb959e51ec01c07 and are clean. This parent task-only report is committed/pushed on its matching branch; final report commit is provided in the execution response. No submodule pointer staged, other task/index/architecture changed, main merge/push or force-push.

### Handoff and unresolved issues

No unresolved owned-scope decision or task-introduced failure remains. Inherited full-lint and stale media-fixture failures are described above for architect assessment. No subagent assistance was used. ADMIN002 initializer, consumer implementations, activation, deployment, migration and live operations remain outside this task. Existing permissions, atomic save/audit and activation services remain in place; no initializer or actual activation was executed. Downstream readiness is unchanged pending independent architect review. This submission is Review, not architect acceptance or self-completion.

## Architect Review
### Review Status
Accepted — Attempt1, 2026-11-10. Automatic completion applied; executor/claimed_at remain null.

### Review Notes
Independently inspected source `31e24c04d532e364e4c4e4bf6eb959e51ec01c07` and published report `111326fa26fba9d96f6e7410871db0c1b339d839`, current clean mirrored task histories and task acceptance. The server uses the exact public Shared strict binding schema, permits it only for AI wrappers and rejects Meta/HUMAN/SHARED injection. Compilation/source hashes preserve binding while omission preserves legacy shapes. Translation transport contains text only; immutable source verification and all-locale eligibility protect the structural binding, including recomputed locale hashes. Real extractor restoration preserves response slots and existing Meta instructions. UI switching removes non-AI bindings; authoring/review/activation previews use a local SVG above the full response with no merchant fetch or secret.

### Reviewed Files
Authoring types/validation/compiler/draft operations/preview; translation source snapshot and compilation segments/restoration; wrapper eligibility/preview; editor audience/toggle and all three preview surfaces; task runner and focused fixtures; package/lock and README deployment guidance. Existing save/audit and activation forwarding paths were traced, not replaced.

### Validation Reviewed
Independent `npm run test:arch068-admin-authoring` rerun:14 passed,0 failed/skipped. Reviewed recorded89 passing regression tests and one inherited media-compiler expectation failure, typecheck and final production build pass, changed-file lint/browser isolation and exact registry SRI checks. Source diff check passes. The inherited media fixture expects two bindings where prepared baseline already emits checkout.itemsSummary as a third; source/test are unchanged. The full-lint hook error/three warnings are outside changed paths; independently hashed the failing hook against prepared baseline with identical SHA256bac1e2245dd4fc8b082ce57c33a1e92196f6562a6b3f5596f12b2ffe050d2f8c. No introduced failure or required owned work is waived; no baseline ID is invented. Initial review rerun sandbox cache restriction was resolved by proper escalation and the complete focused rerun passed.

### Architecture Conformance
Conforms to ARCH-068 Admin authoring scope, public Shared5.12.0 browser contract and immutable locale/protected-binding rules. Prepared dedicated parent/implementation topology, synchronization, recursive exact database gitlink and claim evidence above verified. No shared checkout reuse, source ownership crossover, initializer implementation, live image/R2 read, activation or main merge occurred.

### Follow-up
No same-task correction remains. Background001 is Complete at Accepted Attempt1; Commerce001 retains its published review Attempt1 and is not accepted by this review. Admin002 remains Pending until Commerce001 is Complete; SystemTest001 remains terminal/manual-gated. Deployment compatibility must be checked before activation; this acceptance performs no deployment, activation or follow-on execution.

## Coherence amendment — exact handoff and precedence

This section resolves terminology in earlier sections; it does not authorize another implementation. The original Background product transformer is the only product preset. Its output is strictly less than 5MiB, uses contain/white padding (not crop), and retains its quality ladder. Host configuration readers and credential loading stay in their host repositories. Only the generic media operations move to Shared.

Shared SHARED-001 also exports these exact strict provenance schemas, reusing the validators already defined above:
```ts
export const ConversationProductPairSchema = z.strictObject({
  productId: NativeProductId, variantId: NativeVariantId,
});
export const ConversationVerifiedProductsSchema = z.strictObject({
  shopId: BoundId,
  platform: z.enum(['SHOPIFY', 'WOOCOMMERCE']),
  products: z.array(CommerceProductSchema).max(3),
});
export const ConversationProductImageSourceSchema = z.strictObject({
  kind: z.literal('SOURCE'), shopId: BoundId,
  platform: z.enum(['SHOPIFY', 'WOOCOMMERCE']),
  productId: NativeProductId, variantId: NativeVariantId, sourceUrl: HttpsUrl,
});
```
Selector input is exactly `{shopId, platform, displayedPairs, verifiedProducts}`; displayedPairs is an array of ConversationProductPairSchema with maximum 3 and uniqueness by canonical productId/variantId tuple. Verified product array pairs must also be unique. Schema/provenance mismatch throws an Error with code PRODUCT_IMAGE_IDENTITY_INVALID; missing exact first pair returns PRODUCT_NOT_VERIFIED. No new native-ID format validation is introduced. This result is internal and is never accepted from a browser or model as proof of authorization. Shared task tests must cover WooCommerce simple products (`variantId:null`) and both platforms' native variant IDs.

Plan construction first validates the body and binding. Omitted binding produces TEXT/BINDING_DISABLED. A present invalid binding throws PREPARED_INVALID; it cannot silently become text. With a valid binding, precedence is NO_PRESENTED_PRODUCT, CAPTION_TOO_LONG, IMAGE_UNAVAILABLE, IMAGE_IDENTITY_MISMATCH, then IMAGE success. Host source/preparation omissions are logged with their original reason; buildConversationDeliveryPlan's IMAGE_UNAVAILABLE is the delivery-level summary. IMAGE_IDENTITY_MISMATCH logs at error severity and never dispatches that URL. Source absence or optional preparation failure still allows valid text. Hosts skip media configuration/network work when the first two applicable omission conditions already determine TEXT.

Schema files do not implement final send authorization. Background requires persisted plan.image.shopId to equal the locked message's conversation shop, and its exact pair to equal the verified selected first pair in the matching receipt. Persisted JSON alone is not a receipt. Null is legacy only: a newly prepared aspect-2 reply always persists TEXT or IMAGE. Legacy text retry remains legacy; it cannot be upgraded to IMAGE. No later retry rewrites a previously admitted plan.

SHARED-001 owns changes to Shared source only. SHARED-002 can read Background source as extraction input but writes only Shared. BACKGROUND-001 owns replacement of Background implementation bodies and updates every compatibility caller/mock. ADMIN-001 owns authoring only; ADMIN-002 owns script/extracted transaction helpers. DATABASE-001 owns schema/migration/generation validation only; it does not implement Shared validation or Background admission. Each task's acceptance applies only to its repository and explicitly owned interfaces; the whole acceptance matrix is integrated by SYSTEM-TEST-001.

SYSTEM-TEST-001 creates `src/harness/conversation-product-image/{fixtures.js,scenario.js,assertions.js}` and `test/conversation-product-image.test.js`; wires the existing package.json test command using the repository's existing test runner and documents launch in README.md. Reuse `src/whatsapp-emulator.js`, `src/harness/aimock/runtime.js`, `src/harness/environment.js` for transport/model/environment control; extend them only where IMAGE payload capture is missing. Fixtures use the same compiled wrapper, product bytes, public origin and scripted envelope for both hosts; assert complete plan equality, media omission, one provider call, body preservation and legacy behavior. Add the mandatory failure/race cases above. Tests use disposable local infrastructure/provider emulator; launching real infrastructure or sending real WhatsApp messages requires separate explicit user authorization. Do not mark blocked merely because optional live infrastructure was not authorized when local acceptance can run.

Script `--apply` is opt-in and a separate operator action. Implementation completion does not activate a wrapper. Existing occupied slots are never replaced. Source contains no header logo or fixed product facts: only response.body and the optional structured binding. Existing all-language eligibility rules remain authoritative; obtain REVIEW_LANGUAGES from its existing export, not a copied locale list or hardcoded loop count. Tests assert the current count and exact coverage from that export.

## Accepted publication handoff — 2026-11-09
SHARED003 is Complete / independently Accepted Attempt1. Install exactly `@modainteract/moda-interact-shared@5.12.0`, registry https://registry.npmjs.org/, SRI `sha512-RD3pGDVZHK8sRwbi91SpdouRDVkyf+4rhdB4eczaG48avsnEOQRhRccqzX2YI9KhXa1jXE4S2LHfz7D9DR5PEw==`, tarball SHA256 `e4416c765079a6c8c8ca04894e87e3822c3af0acf19428a5d3f542effe697393`. Release source `12d0b85aaeefba4dfc46bb12637004f19d462b19` includes both accepted Shared capabilities. Use browser-safe `/commerce/presentation` for contracts and Node-only `/commerce/presentation/node` for media preparation; no sibling source import or copied generic mechanics. Ready at unchanged Attempt0, executor/claimed_at null; no claim or implementation begins here.
