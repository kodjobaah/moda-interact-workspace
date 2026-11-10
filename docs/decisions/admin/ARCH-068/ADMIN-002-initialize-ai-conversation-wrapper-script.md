---
id: ARCH-068-ADMIN-002
architecture_id: ARCH-068
title: Initialize AI conversation wrapper safely
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
depends_on: ['ARCH-068-ADMIN-001', 'ARCH-068-COMMERCE-001', 'ARCH-068-BACKGROUND-001']
enables: ["ARCH-068-SYSTEM-TEST-001"]
created: 2026-11-09
updated: 2026-11-10
---
# Initialize AI conversation wrapper safely

## Architecture and objective
Implement the owned portion of [binding ARCH-068](../../../architecture/ARCH-068-optional-conversation-product-image.md). The entire contract is normative, including exact schemas, transport/failure rules, initialization, rollout and acceptance matrix. Read it before execution.

## Context and scope
ADMIN-002 adds `scripts/initialize-conversation-wrapper.mjs`, server core `src/lib/admin/whatsapp-templates/wrappers/initialize.ts`, package command `whatsapp:initialize-conversation-wrapper`, README and disposable DB tests. Exact CLI: `--environment=test|production --actor-admin-id=<id> --dry-run|--apply --reason=<10..500 chars>`; default dry-run, mutually exclusive modes, unknown args fail. Resolve trusted deployment environment using existing Admin runtime configuration and require exact match with requested environment; production is supported but never executed by implementation/tests. Actor must already exist and have SUPER_ADMIN role; never synthesize/elevate actor.

Exact source: schemaVersion1/family MODA_CONVERSATION_WRAPPER/sourceLanguageTag en/audience AI/header[]/body[{type:'slot',name:'response.body'}]/footer[]/conditionals[]/productImage{variable:'response.productImage',placement:'BEFORE_BODY',optional:true}. Use canonical compiler and hash helpers. Stable submission UUID is `e14e7967-05bb-4a5c-bacf-0663b42b37d5`, derive definitionIdForSubmit(actorId,uuid). Same actor repeat verifies byte-identical immutable source/prepared; mismatch fails, never edits existing definition. Existing occupied AI slot: identical canonical desired prepared/binding and eligible definition -> UNCHANGED even if different author ID; any other active definition -> SLOT_OCCUPIED, no writes, no overwrite/force flag. Empty slot -> create/save immutable definition and locales and activate atomically in one SERIALIZABLE transaction; concurrent empty-slot initialization loses cleanly with conflict, no orphan partial template.

All20 existing REVIEW_LANGUAGES locales use precisely the slot-only AST, identical binding, no prose. English SOURCE_SAVED; other languages REVIEWED with supplied superadmin actor, common transaction timestamp, providerLanguageCode null. This is operator approval of language-invariant structural content, not fabricated translation review. Reuse existing eligibility and activation/audit semantics via extracted transaction-internal service functions, not nested transactions or direct unchecked pointer SQL. Audit metadata identifies script/version/structural-only locales/source+content hashes/previous slot; reason provided by operator. Never create a Meta registration/submission job. Dry-run writes nothing and reports planned definition ID/hash/locale count/current pointer; apply returns CREATED_AND_ACTIVATED or UNCHANGED; failures typed INVALID_ARGUMENT/ENVIRONMENT_MISMATCH/ACTOR_DENIED/IMMUTABLE_CONFLICT/SLOT_OCCUPIED/CONCURRENT_STATE_CHANGE. Output no secrets/customer data. No automatic execution against test/production in task.

## Interfaces and contracts
The named exported schemas/APIs and exact JSON shapes in the binding contract are authoritative. Existing v1 template hashes/legacy records remain compatible. No clothing-specific fields/model image URL or Meta recovery contract extension.

## Work Items
- [x] Verify dependencies and current owned source against binding touch points.
- [x] Implement every requirement in the owned scope and binding contract.
- [x] Add deterministic success/failure/compatibility tests specified above.
- [x] Run declared repository validation and record exact evidence.
- [x] Publish implementation and parent report on mirrored task branches for review.

## Dependencies
ARCH-068-ADMIN-001, ARCH-068-COMMERCE-001, ARCH-068-BACKGROUND-001

## Acceptance criteria
All owned scope above is complete, exact contract tests pass and no TODO/placeholder or unresolved cross-service choice remains. For tasks consuming Shared, prove the dependency using the exact published artifact; no sibling source imports/copied mechanics. Record actual changed paths and checks. Preserve existing grounded text, product identity, moderation/send fences, initial/proactive Meta flows.

## Out of Scope
No redesign of aspects 1 and 3, Meta submission/WABA validation, inventory write, unrelated cleanup, budget increase, production mutation or automatic live initializer.

## Agent execution and review
Execution is owned by the assigned agent, not a human developer. Use /moda-task with canonical isolated parent/implementation worktrees and mirrored task branches. Do not claim on authoring. Implement only this repository portion; use published Shared APIs. If an actual source conflict contradicts the exact binding contract, report it to the architect with path/symbol/evidence; do not invent a replacement architecture or leave a placeholder. No main merge/push, production mutation, real send or live initializer execution is part of this task.

## Completion Report

Complete — independently Accepted Attempt 1, 2026-11-10. User-authorized automatic completion applied; attempt unchanged, executor/claimed_at null. Original implementation submission/evidence follows; current acceptance and completion decision are recorded in Architect Review.

### Implementation

Admin source `40fc5b67e6a814020668a6d4ae25eaa7c0d5f17a`, committed/pushed and clean on `task/ARCH-068-ADMIN-002`, implements:

- Exact CLI `--environment=test|production --actor-admin-id=<id> --dry-run|--apply --reason=<10..500 chars>`, default dry-run, strict required/unique/known flags and mutually exclusive modes. Output is bounded JSON with no argument echo, credentials, customer data, database error text or stack traces.
- Trusted environment selection reuses `resolveDeploymentEnvironmentName`; requested environment must match exactly before a transaction. The script never assigns the runtime environment from its requested flag. Actor is read from the database and must already be active/SUPER_ADMIN; no provisioning, elevation or development-actor helper is called.
- Exact canonical source has empty header/footer/conditionals, only response.body, AI audience and the Shared optional BEFORE_BODY binding. Existing compiler, canonical hash and definitionIdForSubmit helpers produce records/identity using the specified stable submission UUID. No prose, header logo, product facts, model call, translation or Meta job is introduced.
- Dry-run reads actor/immutable candidate/current AI slot in SERIALIZABLE and returns planned definition/hash/locale-count/current-pointer information without writes. Apply uses one SERIALIZABLE transaction for definition, English source, the remaining canonical REVIEW_LANGUAGES locales, eligibility, pointer CAS, first-publication marker and audits.
- Same-actor records must match immutable source/prepared bytes and eligibility; conflicting records fail IMMUTABLE_CONFLICT without repair. Any eligible occupied slot with the identical canonical prepared record returns UNCHANGED, including another actor's definition. Other occupied/incomplete slots fail SLOT_OCCUPIED. Empty-slot races permit one winner; the loser fails CONCURRENT_STATE_CHANGE with no orphan definition/locales/audit and no automatic retry.
- All current20 languages come from REVIEW_LANGUAGES. English is SOURCE_SAVED; other locales are REVIEWED by the explicit operator with a shared database transaction timestamp, identical source/prepared records and null provider language codes. Audit metadata identifies script/version/environment, structural operator approval, canonical locales, source/content hashes and previous slot; the operator's supplied reason is preserved.
- Existing authoring and activation were extracted into transaction-local helpers, with ordinary services delegating to them. Initializer uses those helpers directly inside its one transaction, retaining compiler/eligibility/CAS/audit semantics without nested transactions or unchecked pointer SQL. Only a fixed transaction_timestamp read uses SQL; pointer updates retain the existing repository.
- README places the required deployed Commerce/Background versions and successful binding fixture evidence immediately before apply. It explains that local completion does not prove deployed compatibility, and the script reads no deployment API. No startup/deployment hook runs initialization automatically.

The CLI uses existing esbuild to load local Admin TypeScript as native ESM, keeping installed npm dependencies external via their public export resolution and preserving the existing Admin source alias. This avoids a package-wide module-mode or global import-condition change; the temporary local-code artifact is removed on exit. The real CLI is validated against disposable PostgreSQL, not merely through an injected service port.

### Changed files (implementation-repository relative)

- README.md
- package.json
- scripts/initialize-conversation-wrapper.mjs
- scripts/test-arch068-admin-initializer-postgres.mjs
- src/lib/admin/whatsapp-templates/authoring/repository.ts
- src/lib/admin/whatsapp-templates/wrappers/initialize.ts
- src/lib/admin/whatsapp-templates/wrappers/repository.ts
- src/lib/admin/whatsapp-templates/wrappers/service.ts
- tests/unit/arch068-conversation-wrapper-initializer.test.ts
- tests/integration/arch068-conversation-wrapper-initializer.postgres.test.ts

### Validation

- `npm run test:arch068-admin-initializer:unit`: **7 passed, 0 failed/skipped**. Strict/default CLI, exact structural AST/UUID/current language coverage, invalid/environment gate before database access, read-only dry-run and deterministic plan, existing active SUPER_ADMIN requirement, redacted errors and real native CLI module/environment gate.
- `npm run test:arch068-admin-initializer:postgres`: **11 passed, 0 failed/skipped** in a newly created loopback-only pgvector/PostgreSQL17 Docker fixture with the recorded repository migrations. Validates read-only dry-run via complete before/after snapshots; exact20-locale apply/common review timestamp/audits; same/different actor idempotency; immutable conflicts; occupied different and incomplete records; actor denial; activation of an existing immutable definition without locale rewrites; creation and activation audit failure rollback; forced concurrent empty-slot race with no orphan losing rows/audit; and the actual CLI default/apply/repeat/environment behavior. No Meta registration or translation run is created. The harness removed its container; final matching-container inventory was empty. No external/deployed database is accepted.
- Existing native ESM authoring/wrapper regression runner against arch047-template-authoring-service, arch047-template-wrappers, arch047-template-wrappers-service, and both accepted arch068-conversation-product-image test files: **29 passed, 0 failed/skipped**. Ordinary save/clone/replay/rollback, activation/CAS/audit and accepted binding/translation/preview behavior remain intact after helper extraction.
- `npx tsc --noEmit`: passed, final diagnostics empty.
- Changed-source/helper/CLI/harness `npm run lint -- <six owned paths>`: passed, including final native-loader changes. Full-repository lint was not claimed clean or redundantly rerun; accepted ADMIN001 already records its unchanged media-hook/database-config baseline findings. No such file was edited here.
- `npm run build`: passed, including existing Prisma generation, optimized Next webpack build, TypeScript checks and route generation. Existing BullMQ expression/optional Valkey module warnings remain nonfatal; package versions and those paths are unchanged.
- Published dependency integrity, accepted source containment, unchanged package-lock/database gitlink and git diff/staged checks passed. Workspace Node24.19.0/npm11.17.0 were selected through the canonical bootstrap.

Initial real-CLI validation exposed the repository's CommonJS/global import-condition incompatibility with a Shared transitive module; the native ESM loader above and real-CLI regression resolve it. All final initializer checks pass. Production spelling is parsed as supported, but no initializer core/apply was executed against production; test-mode CLI calls occurred only in the guarded disposable fixture.

Evidence retained under /tmp: arch068-admin002-unit-final.log, arch068-admin002-postgres-final.log, arch068-admin002-regressions.log, arch068-admin002-types-final.log, arch068-admin002-changed-lint-final.log and arch068-admin002-build.log.

### Dependency and ownership evidence

Launcher verified ADMIN001, COMMERCE001 and BACKGROUND001 Complete. Prepared Admin baseline `5b85311a51d4c7e81b124059f1348fe550b95e1f` contains accepted ADMIN001 source `31e24c04d532e364e4c4e4bf6eb959e51ec01c07` (Git ancestry verified), so its compiler/hash/binding/eligibility implementation is reused directly.

Installed Shared remains exactly `@modainteract/moda-interact-shared@5.12.0`; unchanged lockfile SRI `sha512-RD3pGDVZHK8sRwbi91SpdouRDVkyf+4rhdB4eczaG48avsnEOQRhRccqzX2YI9KhXa1jXE4S2LHfz7D9DR5PEw==` was asserted. Binding imports use public `/commerce/presentation`; no sibling-source import, copied compiler/schema or Node media implementation is introduced. No dependency/version/lock change or package publication is part of this task.

### Git / VCS and physical isolation

Both repositories use `task/ARCH-068-ADMIN-002`.

- Canonical workspace root: /Users/kwadwoadomafriyie/project/moda-interact-workspace.
- Parent worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-068-ADMIN-002, reused; remote task fast-forwarded yes; origin/main incorporated yes; preclaim head1b562301199386e9cf6f2a72fef84d9a3cc2d552.
- Implementation worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-068-ADMIN-002, created at5b85311a51d4c7e81b124059f1348fe550b95e1f; remote task fast-forward not-needed; origin/main already-current.
- Launcher recursive submodule sync/update passed; ready; database initialized at recorded5329d5390d346042895219663f3a040ea54ae168. Schema/migrations/gitlink unchanged.
- Durable parent claim849440f475e256c39480b47082c958e8046e7f62, pushed; Attempt1/codex at2026-11-10T01:15:13Z. No duplicate claim or attempt increment.
- Shared/default workspace and implementation checkout switched/mutated for task execution: no. Another task worktree reused: no.
- Implementation HEAD and origin/task/ARCH-068-ADMIN-002 match40fc5b67e6a814020668a6d4ae25eaa7c0d5f17a, clean. This task-only parent report is committed/pushed on its matching branch; final report commit is provided in the execution response. No submodule pointer staged, other task/index/architecture edit, main merge/push or force-push.

### Handoff

No unresolved required work, failed final initializer validation or cross-service choice remains. No subagent assistance was used. Implementation/testing did not run an initializer against a deployed test/production environment, change any live AI pointer, send a message, mutate provider/R2 infrastructure or deploy a migration. Operator apply still requires deployed-consumer readiness as documented. SYSTEM-TEST readiness is unchanged pending independent architect review/completion/reconciliation. This is a Review submission, not architect acceptance or self-completion.

## Architect Review

### Review Status
Accepted — Attempt 1, 2026-11-10.

### Review Notes
Independent moda_architect review of source `40fc5b67e6a814020668a6d4ae25eaa7c0d5f17a` against prepared baseline `5b85311a51d4c7e81b124059f1348fe550b95e1f` and parent submission `3d492cde3e408b6e6e4c6a3376f529063657ae7c`. No required correction remains.

Strict CLI/default dry-run, requested-versus-trusted environment equality and database-backed existing active SUPER_ADMIN checks conform. Exact source/UUID, compiler/hash reuse and public Shared5.12.0 schema are retained. Own immutable identity mismatch refuses; an eligible identical occupied slot is read-only UNCHANGED across operators; other occupied/incomplete records refuse. Empty initialization composes existing transaction-local save/activation helpers in one SERIALIZABLE transaction, preserving eligibility, versioned CAS, immutable records and audit rollback. Canonical REVIEW_LANGUAGES locale creation uses truthful operator approval and common database transaction time. No nested transaction, unchecked pointer SQL, actor provisioning, Meta job, model/media/provider I/O or automatic deployed apply exists.

Native ESM CLI loading bundles only local Admin source; installed npm public exports and the existing source alias resolve normally. Temporary artifacts are removed. README records deployed consumer versions/fixture evidence before apply; completion does not prove deployment readiness or authorize live initialization. The bounded unknown-transaction failure code avoids exposing uncertain outcomes or database text and performs no retry.

### Reviewed Files
CLI and core initializer; authoring repository; wrapper repository/service/eligibility; package commands and README; unit/integration tests and disposable PostgreSQL harness. Source changes are confined to the ten reported Admin files. Published Shared5.12.0 dependency/lock and database gitlink are unchanged.

### Validation Reviewed
Independently reran `npm run test:arch068-admin-initializer:unit` (**7/7 passed**), `npm run test:arch068-admin-initializer:postgres` (**11/11 passed**, actual CLI, audit rollback, forced race/no orphan state) and `npx tsc --noEmit` (**passed**, empty diagnostics). Disposable container cleanup confirmed. Reviewed submitted29-pass ordinary authoring/wrapper/binding regressions, changed-file lint and successful production build evidence. Existing nonfatal BullMQ build warnings and prior accepted full-lint baseline are accurately separated from task checks. No deployed test/production initialization was run. Review logs: `/tmp/arch068-admin002-architect-{unit,postgres,types}.log`.

### Architecture Conformance
Conforms to the task/binding architecture, repository ownership, shared schema, transaction/failure, idempotency, privacy and rollout boundaries. Canonical parent/implementation worktree registrations, clean task branches, prepared claim/synchronization/submodule evidence and exact remote source publication were verified. No implementation code or branch, schema/gitlink or main changed during review.

### Completion Decision and Follow-up
The user explicitly authorized acceptance, completion, parent publication and downstream reconciliation if review passes. Accepted Attempt1 satisfies completion_mode automatic: Complete, executor/claimed_at null, attempt unchanged. No duplicate claim or implementation correction is needed. All three explicit SYSTEM-TEST001 prerequisites are Complete; promote that task Pending→Ready at Attempt0, unclaimed, retaining explicit developer/manual launch and separate real-infrastructure/send authorization. Architecture stays In Progress until integrated system acceptance. No system execution, deployment or activation is authorized by readiness.

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

## Accepted prerequisites and readiness handoff — 2026-11-10
Ready at unchanged Attempt0, executor/claimed_at null. All explicit prerequisites are Complete / independently Accepted Attempt1:

- ADMIN001 source `31e24c04d532e364e4c4e4bf6eb959e51ec01c07`, durable completion `9be7c236d8d4798be6796b115d4b72011070589f`.
- COMMERCE001 source `ee42e4e4894361138ea13aad4ce5e7213461d47e`, durable completion `69acccb6011e5f8c71da79f362127b77ac94da63`.
- BACKGROUND001 source `383efdce24fb60888ff91bc260ff13b4b524b7dd`, durable completion `7af4b2852d8e917b3974530988c5ef9c6a499d6c`.

Use the accepted Admin compiler/hash/eligibility source and published Shared exactly `5.12.0`, SRI `sha512-RD3pGDVZHK8sRwbi91SpdouRDVkyf+4rhdB4eczaG48avsnEOQRhRccqzX2YI9KhXa1jXE4S2LHfz7D9DR5PEw==`. Completion does not imply main integration: verify accepted Admin source containment when preparing implementation; no sibling imports or duplicated compiler are permitted. The public browser contract remains separate from Node media preparation.

This handoff creates no implementation worktree or claim and does not run the initializer. Deployed Commerce/Background compatibility and fixture evidence remain required operator prerequisites before any apply/activation. SYSTEM-TEST001 remains Pending/manual-gated until this initializer task is Complete.
