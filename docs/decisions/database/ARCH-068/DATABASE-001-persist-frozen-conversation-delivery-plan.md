---
id: ARCH-068-DATABASE-001
architecture_id: ARCH-068
title: Add nullable frozen outbound delivery plan
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 30
executor: null
claimed_at: null
attempt: 1
depends_on: []
enables: ["ARCH-068-BACKGROUND-001"]
created: 2026-11-09
updated: 2026-11-09
---
# Add nullable frozen outbound delivery plan

## Architecture and objective
Implement the owned portion of [binding ARCH-068](../../../architecture/ARCH-068-optional-conversation-product-image.md). The entire contract is normative, including exact schemas, transport/failure rules, initialization, rollout and acceptance matrix. Read it before execution.

## Context and scope
Exact addition to `ConversationMessage` in prisma/schema.prisma:
```prisma
  // Frozen aspect-2 delivery plan; null for legacy/other message paths.
  outboundPresentation Json? @db.JsonB
```
Migration SQL is only:
```sql
ALTER TABLE "whatsapp"."ConversationMessage"
ADD COLUMN "outboundPresentation" JSONB;
```
No default/backfill/index/new table/enum change. Application validates ConversationDeliveryPlanSchema and additionally matches plan.body to content. Image plans use existing contentType TEXT and ordinary caption content for current history/moderation compatibility; actual provider media classification is in outboundPresentation, not reused inbound AUDIO/transcription fields. Do not populate providerMediaId with an R2 URL. Existing providerMessageId remains the one provider receipt. No credentials, recipient, source URL or model prose beyond existing body in this JSON. Migration deploys before Background references this field. Null means existing legacy send behavior; plan never inferred from text.

## Interfaces and contracts
The named exported schemas/APIs and exact JSON shapes in the binding contract are authoritative. Existing v1 template hashes/legacy records remain compatible. No clothing-specific fields/model image URL or Meta recovery contract extension.

## Work Items
- [x] Verify dependencies and current owned source against binding touch points.
- [x] Implement every requirement in the owned scope and binding contract.
- [x] Add deterministic success/failure/compatibility tests specified above.
- [x] Run declared repository validation and record exact evidence.
- [x] Publish implementation and parent report on mirrored task branches for review.

## Dependencies
None; launcher dependency gate passed for Attempt 1. Claim `de8ce01f6fc41c79bc356ba3d2e48cf4895d599e` was pushed before implementation.

## Acceptance criteria
All owned scope above is complete, exact contract tests pass and no TODO/placeholder or unresolved cross-service choice remains. For tasks consuming Shared, prove the dependency using the exact published artifact; no sibling source imports/copied mechanics. Record actual changed paths and checks. Preserve existing grounded text, product identity, moderation/send fences, initial/proactive Meta flows.

## Out of Scope
No redesign of aspects 1 and 3, Meta submission/WABA validation, inventory write, unrelated cleanup, budget increase, production mutation or automatic live initializer.

## Agent execution and review
Execution is owned by the assigned agent, not a human developer. Use /moda-task with canonical isolated parent/implementation worktrees and mirrored task branches. Do not claim on authoring. Implement only this repository portion; use published Shared APIs. If an actual source conflict contradicts the exact binding contract, report it to the architect with path/symbol/evidence; do not invent a replacement architecture or leave a placeholder. No main merge/push, production mutation, real send or live initializer execution is part of this task.

## Completion Report

Status: Ready for Review — Attempt 1, 2026-11-09.

Implementation committed and pushed on Database `task/ARCH-068-DATABASE-001`:
`75669477b9048104758e8f1e897abecef13bf059`.

### Implemented owned scope

- `prisma/schema.prisma`: exact optional `ConversationMessage.outboundPresentation Json? @db.JsonB` and requested comment. Existing fields, enums and relations unchanged.
- `prisma/migrations/20261109210000_arch068_conversation_delivery_plan/migration.sql`: exact one-statement nullable JSONB addition, with no default/backfill/index/table/enum change.
- `scripts/validate-arch068-conversation-delivery-plan.mjs` and `package.json`: exact DDL/schema contract validator and declared task commands.
- `scripts/test-arch068-conversation-delivery-plan-postgres.mjs`: invocation-owned disposable local PostgreSQL fresh/upgrade tests, historical row preservation, optional old-writer compatibility, TEXT/IMAGE JSON roundtrips, unchanged TEXT/content/provider receipt/media behavior, and finally cleanup.
- `docs/generated/prisma-erd.puml` and `docs/generated/erd.png`: nullable field added to message entity and diagram rendered. The full existing generator was exercised; it exposed broad unrelated pre-existing diagram drift. That drift was excluded; the committed PlantUML source changes only this field and its PNG is rerendered with the installed tool.
- `docs/arch068-conversation-delivery-plan.md`: rollout ordering, rollback/data retention, query/index rationale, local test commands, and application-validation/send-authorization ownership.

### Validation evidence

All final checks passed:

- Locked `npm ci --ignore-scripts`; workspace bootstrap selected Node 24.19.0, npm 11.17.0, Prisma/client 6.19.3.
- On an invocation-labelled disposable `pgvector/pgvector:pg17` database bound exclusively to loopback: `npx prisma migrate deploy --schema prisma/schema.prisma` applied 75 historical migrations; `npx prisma migrate dev --schema prisma/schema.prisma --name arch068_conversation_delivery_plan --create-only --skip-generate` authored the new migration. Normalized its timestamp/name and removed the generated SQL comment to match the exact binding DDL. No developer/deployed database used.
- `npm run prisma:validate`: PASS.
- `npm run prisma:generate`: PASS. Generated client DMMF assertion additionally verified field type Json, isRequired false, hasDefaultValue false.
- `npm run erd`: PASS, followed by task-only diagram scope reconciliation and successful `plantuml -tpng docs/generated/prisma-erd.puml` rerender.
- `npm run test:arch068-conversation-delivery-plan`: PASS exact schema/DDL and legacy field compatibility.
- `npm run test:arch068-conversation-delivery-plan:postgres`: PASS both fresh and upgrade scenarios (76 migrations each), including original populated message preservation excluding only the new NULL field; no default; old-writer omission; complete TEXT/IMAGE JSON equality; existing receipt and media semantics. Final fixture uses the specified content-addressed object-key/URL shape. Invocation-owned container removed in finally; authoring container also removed by EXIT trap.
- `npm run lint`: PASS zero warnings/errors. One new regex-style lint error was corrected before the final passing run.
- `git diff --check`: PASS.

### Compatibility, rollout and limits

Database-only contract is complete. The migration must deploy before Background code references the new field; consumers regenerate their clients from the accepted schema. NULL remains legacy, with no inference/backfill. Existing TEXT classification/providerMessageId/providerMediaId semantics are preserved. JSON schema validation, body equality, tenant/product receipt verification, admission immutability and media dispatch remain Shared/Background responsibilities; this task deliberately adds no SQL schema/provenance validation or send logic. No extra index is justified: existing locked message ID access loads the column without an additional query. No row-rewriting backfill or high-volume hot-path index added. Normal ALTER TABLE locking remains an operator deployment consideration. Retain the column and frozen data during application rollback.

No package is consumed from Shared by this schema-only task. No provider calls, production mutation, initializer, wrapper activation, real send, main merge or parent implementation gitlink update performed. No unresolved owned acceptance item or new cross-repository choice remains. Architect acceptance is pending.

### Launcher preparation evidence

```text
Physical worktree isolation:
  canonical workspace root: /Users/kwadwoadomafriyie/project/moda-interact-workspace
  parent worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-068-DATABASE-001
  parent branch: task/ARCH-068-DATABASE-001
  implementation worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-068-DATABASE-001
  implementation branch: task/ARCH-068-DATABASE-001
  shared workspace checkout switched/mutated for task work: no
  shared implementation checkout switched/mutated for task work: no
  another task worktree reused: no

Start-of-attempt synchronization:
  parent remote task branch fast-forwarded: not-needed
  parent origin/main incorporated: already-current
  implementation remote task branch fast-forwarded: not-needed
  implementation origin/main incorporated: already-current

Recursive implementation submodules:
  git submodule sync --recursive: passed
  git submodule update --init --recursive: passed
  recursive status: ready (no entries)
  dependency gate: passed (none)
  claim commit pushed: de8ce01f6fc41c79bc356ba3d2e48cf4895d599e
```

## Architect Review
Status: Accepted — Attempt1,2026-11-09.

### Independent implementation review
Inspected actual75669477b9048104758e8f1e897abecef13bf059 diff, not solely Completion Report. Schema adds exactly optional ConversationMessage.outboundPresentation Json? @db.JsonB with binding comment. Migration contains only the two-line ALTER TABLE/ADD COLUMN JSONB statement; no default, backfill, index, table, enum, relationship or existing message field change. ERD PlantUML source changes only the new field, rendered PNG accompanies it; unrelated generator drift excluded. Rollout document correctly requires migration before Background/client regeneration, retains column/frozen data on app rollback, and leaves plan validation/body equality/tenant receipt/admission/send semantics with Shared/Background.

### Validation reviewed
Independently ran npm run test:arch068-conversation-delivery-plan PASS exact schema/DDL. Independently ran npm run test:arch068-conversation-delivery-plan:postgres PASS fresh and populated upgrade, old row equality except new NULL column, nullable JSONB/no-default catalog check, omitted old-writer field, full TEXT/IMAGE JSON equality and unchanged TEXT/provider receipt/media fields. Inspected harness: random invocation-owned network-none local pgvector17 only, no inherited/deployed DATABASE_URL, historical migrations applied, cleanup finally removed owned container. Inspected declared scripts and owner passing Prisma validate/generate+DMMF, lint, ERD render and diff evidence; no redundant healthy checks needed. Database intentionally does not validate application JSON semantics.

### Conformance and isolation
Accepted database-only scope, no unresolved owned criterion or contract choice. Prepared packet dedicated parent/implementation worktree identity, start synchronization, ready recursive submodules/dependency gate and durable claimde8ce01f inspected. Both worktrees clean; freshly fetched remote task refs equal implementation75669477 and parent report26b56637. No shared/default source edits, main/gitlink integration, deployed migration, seed/reset, inventory/provider call, wrapper activation or actual send during review. Operator ALTER TABLE lock/deploy ordering remains documented, not silently performed.

### Completion and follow-up
completion_mode automatic allows Accepted→Complete. Developer also explicitly authorized conditional completion after passing review; decision recorded below. Background001 remains Pending on SHARED003 publication; no readiness until every prerequisite Complete. System validation remains terminal/manual-gated.

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

## Completion Decision — 2026-11-09
Independent moda_architect review passed; developer explicitly requested Complete if passing. Marked Complete at unchanged Attempt1, executor/claimed_at null, execution_mode agent/completion_mode automatic unchanged. Reviewed implementation75669477 and report26b56637 are durably published; no mandatory owned work remains. No source, deployment, main or gitlink mutation by this decision.

Authoritative downstream reconciliation: ARCH-068-SHARED-003 Pending; ARCH-068-BACKGROUND-001 stays Pending on SHARED003 despite Database prerequisite now satisfied. ARCH-068-SYSTEM-TEST-001 remains Pending on unfinished consumer dependencies with manual gate intact. No downstream task promoted, claimed or started.
