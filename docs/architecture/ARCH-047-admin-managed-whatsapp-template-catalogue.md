---
id: ARCH-047
title: Moda-authored multilingual WhatsApp templates and conversation wrappers
status: in_progress
coordinator: moda_architect
created: 2026-10-23
updated: 2026-10-26
---

# ARCH-047 — Moda-authored multilingual WhatsApp templates and conversation wrappers

## Status

**In Progress — task-state and contract reconciliation against the 26 October 2026, 14:48 uploaded snapshot.** Individual task YAML remains authoritative. Across 25 ARCH-047 task definitions: **19 `complete`, 2 `ready`, 2 `pending`, 2 `superseded`**. `BACKGROUND-007` is `ready`/Attempt 0 and **implementation remains paused pending review of this documentation reconciliation**; `BACKGROUND-009` is `ready`/Attempt 1 after `ARCH-040-DATABASE-007` completed; `WOOCOMMERCE-001` and `SYSTEM-TEST-001` remain `pending`. Completed task YAML is not, by itself, proof of integration into main. Do not rewrite developer completion/review histories to reflect a newer planning summary.

Only Moda Admin may author immutable templates. The former external Meta import/shop-copy workflow and its system-test contract are superseded. Do not assume the completed BG004 read-only offer module has a real checkout-specific provider evaluator; the default Shopify/Woo adapter returns `unavailable`.

## Problem

Moda needs a single controlled way to create recovery WhatsApp templates, translate them, submit each language to Meta, reconcile approval and publish to merchants, plus internally published wrappers around AI- and human-authored checkout conversations. The existing `whatsapp.WhatsAppTemplateVariant` is a shop-assigned operational row, not an English master, multilingual authoring record or provider-submission history. The historical sender relied on Meta metadata/category verification and a shop-scoped selector rather than compiled six-purpose payloads; BG001 and BG006 subsequently implemented preparation and automated integration, while merchant post-window BG007 remains outstanding.

A workflow-stage-only implementation split would scatter template preparation, offer logic and wrapper behaviour across recovery, human handover, AI and final admission services. This amendment defines **five owned Background feature modules** and **four narrow call-site integration tasks**, while preserving existing outbound business-admission authority.

## Goals

1. All Meta recovery templates and internal conversation wrappers are **created exclusively through Moda Admin**. Never import, register, adopt or publish templates authored outside Moda. Provider reads are permitted only to reconcile Moda-authored identities, statuses and drift.
2. Template content is immutable once saved; content corrections, including rejected versions, use **Clone as New** with a new identity. No Meta edit-existing-template API calls. Operational status, review progress and assignment state may change independently.
3. Author an English AST, persist it, durably request Background translation of the other 19 target languages, review immutable results, submit each Meta language, consume/reconcile Meta status events and **publish explicitly**. Internal wrappers skip Meta approval and instead use Admin-only activation.
4. Predefine the six recovery purposes: INITIAL/FOLLOW_UP × NO_OFFER/CODE_OFFER/AUTOMATIC_OFFER. The purpose determines typed variables. Resolve and independently validate offer eligibility *before* the prepared template is used; AI is only a read-only offer recommendation mechanism.
5. Keep template-selection/preparation and variable-binding behaviour in one Background module, distinct from offer resolution, Meta catalogue management, translation and conversation wrapping. Existing send flows delegate rather than replicate domain rules.
6. Preserve consent, authoritative STOP, recipient scope, WhatsApp service window, moderation, billing, retries, compensation, one permitted sequence-two follow-up and final send fencing. No new path may bypass them.
7. Support one/selected/all-current-eligible-shop publication with resumable **per-shop/per-language** targets and explicit replacement of overrides, using the existing shop-assignment table.

## Non-Goals

- No merchant-facing authoring or adoption of Meta-created templates; no in-place template edit, no Meta edit API and no provider-template creation on the ordinary send path.
- No AI commerce mutation: no cart additions/removals, quantity changes, coupon application, checkout edits or order placement. Customers edit their own baskets on Shopify/WooCommerce.
- No new cross-service generic logger, custom Batch runtime, bespoke AST parser or second moderation/send pipeline.
- No change to ARCH-045/046 consent and STOP authority, historical completed tasks or billing semantics.
- No repository-specific implementation or additional task files in this **module-planning** amendment.

## Current Architecture and Source Evidence

Inspected the uploaded 23 October workspace snapshots and the 24 October `ARCH-047-DATABASE-001` worktree/task amendment:

- **Historical pre-integration baseline:** `moda-interact-background/src/services/whatsapp-template-selector.service.ts` selected `WhatsAppTemplateVariant` by shop/WABA/purpose/language and exposed legacy metadata-verification behaviour. The new `recovery-template-preparation/` module was subsequently implemented and `BACKGROUND-001` is now Complete; do not interpret the historical baseline as an instruction to re-implement that module.
- **Historical integration targets:** `checkout-recovery/recovery-initiation.service.ts`, `checkout-recovery/recovery-outreach-follow-up-processor.service.ts`, `recovery-conversation/human-command-dispatcher.service.ts`, `recovery-conversation/outbound-send-fence.service.ts` and `outbound-whatsapp-admission/outbound-message-delivery.service.ts`. BG006 is now Complete; BG007 is Ready but unclaimed. Any remaining legacy references must be verified against current source during BG007 and System Test, not inferred from this earlier inventory.
- `src/services/translation-batch-runtime/` supplies reusable Batch provider submission, polling, correlation, result membership, retry/failure and repair mechanics. Domain-specific Merchant Pricing translation orchestration exists separately; it is **not** a drop-in WhatsApp translation service.
- `src/services/recovery-policy.service.ts` has `NONE`, `FIXED` and `AI_BEST_APPLICABLE` policy context, but currently does not provide the complete verified offer-outcome contract for six Meta template purposes.
- The existing outbound and recovery-conversation components own final send eligibility, moderation, STOP, credits and follow-up limits. ARCH-047 modules must remain downstream helpers, not competing admission authorities.
- The consolidated DB001 task is marked `complete` in the 26 October snapshot, with **11 new tables** and nullable `WhatsAppTemplateVariant.metaRegistrationId`; no business eligibility is enforced in PostgreSQL. Implementation acceptance and merge evidence are separate from task YAML.

Reinspect these paths at implementation start; this is snapshot evidence, not a claim about later Git commits.

## Proposed Architecture

### Authoring, translation and publication

```mermaid
flowchart TD
  A[Moda Admin English AST creation] --> B[(Immutable definition and English locale)]
  B --> C[Durable translation request]
  C --> D[Background Template Translation]
  D --> E[Admin 20-language review]
  E --> F{Template family}
  F -->|Meta recovery| G[Background Meta Template Management]
  G --> H[Meta review and template-status webhooks]
  H --> I[Admin approval and per-shop language publication]
  F -->|Conversation wrapper| J[Admin internal wrapper publication]
  I --> K[(Shop-assigned WhatsAppTemplateVariant)]
  J --> L[(Active wrapper pointer)]
```

Meta approves or rejects **each submitted language**. Neither approval nor successful submission silently assigns the template to shops. External template IDs not linked to Moda-authored definitions cannot enter the catalogue. A rejected or drifted template is not edited; a new definition must be authored and submitted. For a changing provider status, keep immutable submitted components and binding snapshots while recording current observations/events separately.

### Background module ownership (five modules)

| Module / proposed directory | Primary responsibility and owned data | Not owned |
|---|---|---|
| **A — Template Translation** `src/services/template-translation/` | Claim Admin-prepared keyed text segments from `TranslationRun.sourceSnapshot`, protect and restore placeholders, reuse `translation-batch-runtime`, correlate results and persist keyed translations in `TranslationItem.translatedAst`; never parse/rebuild Admin AST. | Meta creation/approval, shop publication, recovery sending, template selection. |
| **B — Meta Template Management** `src/services/meta-template-management/` | Submit Admin-compiled frozen `MetaRegistration.componentsSnapshot` via Meta **create** endpoint unchanged, reconcile uncertain outcomes, consume queued authenticated status observations, and maintain registration/event/drift history. | Webhook signature verification/ingress, Admin approvals, translations, recovery sending. |
| **C — Recovery Offer Resolution** `src/services/recovery-offers/` | Resolve NONE/FIXED/AI policy against current read-only provider/commerce evidence and return one verified `NO_OFFER`, `CODE_OFFER` or `AUTOMATIC_OFFER` decision. | Meta template selection, message wording, coupon application, cart/checkout mutation. |
| **D — Recovery Template Preparation** `src/services/recovery-template-preparation/` | Resolve the six-purpose slot, locally published and approved shop/WABA/language assignment, safe language fallback, frozen per-language parameter mapping and fully prepared Meta payload; expose a final-checkable assignment identity. | AI selection, Meta catalogue network calls, final outbound admission, sending/billing. |
| **E — Conversation Wrapper Rendering** `src/services/conversation-wrappers/` | Select published SHARED/AI/HUMAN wrapper, consume an **Admin-prepared runtime wrapper projection** (not authoring AST), resolve trusted checkout context, insert the original response exactly once and return composed content. | Generating AI response, human authorship, moderation policy, provider sending, checkout mutation. |

Module boundaries are behavioural, not arbitrary file count. A module may contain small coordinator, repository, provider adapter, mapper and pure helpers; it should expose one clearly typed facade to consumers. Keep BullMQ processors thin, inject external dependencies for testing, and avoid 300+ line catch-all files. **Admin alone owns the source AST, authoring validation, translation-segment extraction, translated-template reconstruction, Meta component/parameter-binding compilation and preparation of wrapper runtime projections.** Background consumes those **already prepared persisted values**, translates keyed text segments, resolves trusted runtime parameters and renders the prepared wrapper. BG001 must not parse, validate as an authoring AST or compile the template AST. The **only** new ARCH-047 Shared contract is the already implemented/published v2 Meta template-status queue event (`SHARED-001/002`); it contains no AST/compiler/renderer. Existing outbound admission remains the sole final-delivery control.

### Core interfaces and error behaviour

- `TemplateTranslationService.process(runId)` takes a durable run ID and reads Admin-prepared keyed text segments from `TranslationRun.sourceSnapshot`. It restores/validates protected tokens and saves `{schemaVersion,segments:[{key,text}]}` in the existing `TranslationItem.translatedAst` JSONB; Admin subsequently assembles complete locale payloads. Background cannot publish or modify source AST.
- `MetaTemplateManagementService.submit(registrationId)` sends the **already-persisted**, Admin-confirmed, frozen `componentsSnapshot`/`parameterBindingsSnapshot` for that registration without parsing or compiling authoring content, and reconciles unknown creates **before** retrying. `reconcile(event)` operates on trusted WABA/Meta identity and append-only event evidence; it never adopts outside templates or switches merchant assignments.
- `RecoveryOfferResolver.resolve(context)` returns `{kind:'NO_OFFER'}` or one server-verified code/automatic offer with bounded provenance; an AI recommendation is not itself eligibility proof. Inability to verify produces a no-offer outcome without advertising unsupported savings.
- `RecoveryTemplatePreparer.prepare({shopId, senderWabaId, stage, verifiedOffer, languageContext, checkoutContext})` returns a typed `PreparedRecoveryTemplate` (exact assigned variant/registration IDs, purpose, provider language/name and ordered component parameters) or a structured unavailable reason. It performs no provider metadata HTTP request and no outbound send. Final admission separately rechecks assignment/registration status and STOP/consent/send eligibility in its existing transaction/fence.
- `ConversationWrapperRenderer.render({conversationId, source:'AI'|'HUMAN', responseBody, languageContext})` returns a tagged rendered result with wrapper definition/version and source-message identity so callers can avoid double wrapping. Its checkout context is resolved read-only and tenant-scoped; a missing/stale URL is omitted, never guessed. It does **not** choose whether the message is permitted for WhatsApp delivery.

Background-local typed module ports remain local. The Admin-prepared source segment, translated segment, Meta component/binding and wrapper-runtime JSON shapes are versioned **persistence** agreements; Prisma/JSONB holds them but does not define or enforce the authoring semantics. Admin supplies/validates and persists those payloads. Background does not invent another AST schema or compiler; BG001 performs only necessary stored-payload integrity, binding resolution and send-eligibility checks. Existing Shared internationalisation/logging exports remain reusable. Separately, the completed `ARCH-047-SHARED-001` and published `SHARED-002` own **only** the v2 Messaging → BullMQ → BG003 template-status observation schema and occurrence identity; no new Shared authoring package, publication dependency or AST validation is required for BG001/BG007.

### Recovery and conversation integrations (four thin integrations)

- **Automated recovery:** Existing initial and scheduled follow-up orchestrators call C for a verified offer, then D for a prepared template and hand the result to the **existing** outbound admission/send path. The integration owns *when* to attempt outreach, not selecting discounts, interpreting AST or calling Meta catalogue APIs.
- **Merchant post-window follow-up:** Existing human recovery command dispatcher passes an eligible sequence-two request through C as necessary and D. It retains the single permitted follow-up, purchase/credit rules and service-window boundary; it must not create another outbound path.
- **AI in-window reply:** Existing AI conversation execution generates its response; E wraps it once; the **complete rendered output** goes through existing moderation and admission. AI prompt guardrails and the independent OpenAI Moderation API are separate mechanisms; neither is replaced by the wrapper.
- **Human in-window reply:** Merchant-authored text is wrapped by E, shown consistently in merchant preview, fully moderated and dispatched through existing admission. Merchant-authored human replies within the valid 24-hour window are not subject to the AI exchange cap, but still obey consent/STOP/moderation and existing delivery policy. Shopify and WooCommerce UI preview integration is owned by their own repositories, not Background.

Common final admission must check the exact assigned version again. To avoid conflicting changes to `outbound-message-delivery.service.ts`/send fence, **BACKGROUND-006 owns the common automated/final-fence adapter**; BACKGROUND-007 consumes that adapter and must not implement an independent final gate. AI/HUMAN wrapper integrations do not modify the generic outbound admission contract except through a separately reviewed narrowly scoped need.

### Flow and lifecycle invariants

1. Save immutable English AST; Admin starts a durable translation request after save. Progress flows `SAVED → TRANSLATION_QUEUED → TRANSLATING → READY_FOR_REVIEW`, with per-language failure/retry state.
2. Meta submission is a separate Admin-confirmed operation. Background uses only provider create/read for Moda-owned IDs, never Meta edit/update-template APIs; `message_template_status_update` is authenticated by Messaging and reconciled by B. Meta status is not merchant publication.
3. An approved 20-language definition may be published to one, selected or all **currently eligible** shops, with per-shop/per-language targets and explicit override impact confirmation. Old shop assignments remain active until Admin chooses replacement; publishing is idempotent/resumable and not automatic for future shops.
4. Template content and frozen binding metadata are not changed in place. Operational status/progress and provider observation fields may change; application services enforce immutability, approval, kind, audience, 20/20 completeness, sender WABA compatibility and shop assignment. PostgreSQL retains technical keys/FKs/indexes only.
5. Six recovery purposes are **INITIAL/FOLLOW_UP × NO_OFFER/CODE_OFFER/AUTOMATIC_OFFER**; the fixed and AI discount modes both feed the same verified-offer result. No unverified code/automatic discount promises. Follow-up must not contradict a now-invalid previous offer.
6. Only approved, enabled, correctly assigned and locally non-revoked Meta records may be prepared. No ordinary send calls provider template-list/category endpoints. Disabling/pausing a provider language can block future sends; later approval does **not** silently reactivate a disabled merchant assignment.
7. AI and human conversation content is related to the checkout, but the template module does not add a CheckoutRecovery row or guarantee checkout identity in the underlying current `Conversation` schema. Missing checkout context must fail safely or omit invalid fields. Enforcing conversation identity more broadly is a separate owning-architecture question.
8. No checkout/cart/discount mutation by CommerceAgent; human/customer basket changes happen on merchant storefronts. No wrapper can reopen the WhatsApp service window or create a second recovery follow-up.


### Meta template-status transport and fail-closed provider eligibility (25 October 2026 correction)

- **Producer/consumer boundary:** Existing signed Messaging webhook → existing `whatsapp-events` BullMQ job `meta-template-status-update` → Background BG003 → `WhatsAppTemplateMetaEvent` / `WhatsAppTemplateMetaRegistration`. Messaging has no PostgreSQL access; Background does not verify raw webhook signatures.
- **Canonical Shared-only transport:** `ARCH-047-SHARED-001` owns strict, nine-field `schemaVersion: 2` Meta template-status observation schema and occurrence-ID / BullMQ job-ID formatters; `ARCH-047-SHARED-002` publishes that package before BG003/MESSAGING-001 consume it. No Admin AST/translation/Meta compiler/wrapper renderer belongs in Shared. The prior v1 six-provider-field SHA hash was a **content fingerprint**, not an event occurrence identity, and is superseded before production.
- **Occurrence and replay:** Messaging creates a fresh UUID v4 for each authenticated template-status change; the same ID is preserved on BullMQ retry. Identical provider content delivered again receives a new occurrence ID, so a retained completed BullMQ job cannot suppress a later APPROVED after PAUSED. Background provider-state reconciliation is idempotent and cannot use receipt time as provider-event ordering.
- **Immediate safety fence:** A linked authenticated status observation is durably persisted with `processedAt = null`, and BG003 writes `providerStatus = UNKNOWN` plus due retry **in the same transaction, before Meta GET**. A GET timeout leaves UNKNOWN and the receipt unresolved; stale GET cannot erase a later observation. BG003 independently reconciles assigned/eligible registrations at most every 30 minutes, with bounded retries and rate limits.
- **Final outbound fence:** BG006 re-reads exact shop/variant/registration at the authoritative final-send boundary; require provider APPROVED, no drift/pending status and `lastReconciledAt` ≤60 minutes old. Otherwise refuse with no provider send or permanent charge. BG001 provides a prepared payload only; BG007 reuses the BG006 fence. Meta approval never restores Admin-disabled assignments or bypasses consent/STOP/moderation/billing.
- **Rollout:** The earlier v1 event is not a deployed contract. Should a v1 job be found in a live queue, stop and return compatibility sequencing to the architect; do not silently parse v1 or migrate it ad hoc.

## Repository Responsibilities

| Owner | Repository | Boundary |
|---|---|---|
| moda_database | `moda-interact-database/` | Consolidated `ARCH-047-DATABASE-001` exact 11-table contract, Prisma migration and technical integrity only. |
| moda_shared | `moda-interact-shared/` | `ARCH-047-SHARED-001` defines the **minimal Meta template-status event v2** used between Messaging and BG003; `SHARED-002` publishes it. Both are `complete`. No AST schema/compiler/translation/wrapper package is owned by Shared, and BG001/BG007 have no dependency on the v2 event publication. Existing shared localisation/logging exports remain reusable. |
| moda_admin | `moda-interact-admin/` | English AST authoring/validation, Clone as New, **keyed protected-text extraction**, translation request/reconstruction/review, Meta components and binding compilation, explicit provider submission, Meta approval dashboard and shop assignment; separately prepare/publish runtime wrappers. External-import ADMIN-001 and shop-to-shop-copy ADMIN-002 are marked `superseded` in their task files. |
| moda_background | `moda-interact-background/` | Five feature modules and four thin integration tasks below; never implement Admin approval or Messaging ingress. |
| moda_messaging | `moda-interact-messaging/` | Verify Meta webhook authenticity and publish a bounded `message_template_status_update` observation to existing BullMQ `whatsapp-events`; **no direct PostgreSQL writes**. |
| moda_app / moda_woocommerce | respective Shopify/Woo repositories | Human response preview and authenticated merchant interface; never duplicate wrapper rendering policy. |
| moda_system_test | `moda-interact-system-test/` | Validate end-to-end flows only after required implementation/publication tasks are Complete. |
| moda_gateway | `moda-interact-gateway/` | No additional Gateway implementation established yet; confirm existing Meta app callback and routing during Messaging handoff. Raise a bounded Gateway task only for a demonstrated missing route/configuration. |

## Data Model

The consolidated `ARCH-047-DATABASE-001` task is recorded `complete` in the latest snapshot (the earlier Attempt 7 document defined its persistence shape); do not create DATABASE-002–004. It has **11 new tables**, reuses `WhatsAppTemplateVariant` with nullable `metaRegistrationId` and existing `CommerceAuditEvent`, and deliberately has no distinct Release/ReleaseLocale. A `WhatsAppTemplateDefinition` is the content version; its locales, translation run/item/batch history, per-WABA Meta registration and event history, shop-language publication operations/targets and active wrapper pointers remain independently queryable. Admin writes keyed translation requests to `TranslationRun.sourceSnapshot`; Background stores language results (keyed segments) in `TranslationItem.translatedAst` **without creating a completed locale AST**; Admin writes final `localeAst` and precompiled `MetaRegistration.componentsSnapshot`/`parameterBindingsSnapshot` or a prepared wrapper projection into the appropriate existing JSONB records. `parameterBindingsSnapshot` freezes the Meta-facing positional mapping at submission. Meta drift observations do not overwrite the frozen snapshot.

This architecture does **not** instruct Database to enforce business rules via triggers, CHECK constraints, status-dependent unique keys or stored procedures. Application services own all authorization, lifecycle, eligibility, publication and version immutability policies. Preserve historic template rows without silently adopting externally authored ones: the new runtime refuses non-Moda-linked assignments when switched over.

## Contracts

**Admin-owned authoring contracts.** Admin is the only AST reader/compiler. It validates immutable source content on save, persists a versioned `TranslationRun.sourceSnapshot` containing keyed translatable text and an explicit protected-token map, and reconstructs each language after Background returns `{schemaVersion:1,segments:[{key,text}]}` in the existing `TranslationItem.translatedAst` JSONB. Protected variables such as `{{1}}` and `{{2}}` must be losslessly restored and checked by the translation module; no AST parser is required in Background. For Meta, Admin stores **fully compiled** `MetaRegistration.componentsSnapshot` and frozen `parameterBindingsSnapshot`, which BG003 submits without re-compiling. For internal wrappers, Admin stores an explicitly versioned **prepared runtime wrapper projection** in the applicable existing locale JSONB; BG005 interprets it without authoring-AST logic. Exact JSON transport examples belong in producer and consumer task fixtures, not a new Shared AST package.

**Messaging handoff.** Meta `message_template_status_update` is authenticated by Messaging → enqueued to existing BullMQ `whatsapp-events` → consumed/reconciled by Background → persisted in `MetaEvent`/`MetaRegistration`. The current worker supports inbound `message-received` and provider `message-status`; the new event is a **distinct** job and is not parsed as `NormalizedWhatsAppInboundMessage`. Reuse existing queue envelope and Meta's defined WABA fields where safe. The minimal canonical cross-repository queue event contract is owned by ARCH-047-SHARED-001/002; do not independently duplicate it in Messaging and Background. No Shared authoring AST package is needed.

**Runtime ports.** BG001 consumes stored compiled parameter maps and trusted customer/checkout values to produce a prepared Meta send. BG004 returns an internal verified offer decision. BG005 consumes the Admin-prepared wrapper projection. Their interfaces are Background-local; final consent/STOP, moderation, billing, service window and send fences remain owned by existing runtime.

### ShopBrand bindings and separate image-ingestion ownership (25 October 2026)

The Admin composer currently exposes `shopBrand.brandName`, `logoUrl`, `logoAltText`, `logoWidth`, `logoHeight`, `squareLogoUrl`, `squareLogoAltText`, and `coverImageUrl` as **text-token candidates**, plus trusted checkout-link buttons. Admin owns their typed prepared binding representation; BG001 resolves only the frozen referenced keys from the correct ShopBrand/shop and trusted checkout context, without parsing Admin AST. Image URL strings in body text are **not WhatsApp media headers**. ShopBrand originals are not acceptable runtime image media merely because a URL was stored. Width/height fields are display metadata, not provider resize instructions; absent values fail the relevant required binding without cross-shop fallback. BG006 and BG007 pass the prepared component arrays, button parameters and separately typed image header unchanged through the existing sender and final admission path.

The **separate ARCH-049 ShopBrand media-normalisation initiative** owns secure image ingress, resizing/encoding and R2 derivative/readiness contracts across Shopify and WooCommerce; its implementation state is governed by ARCH-049 task files. ARCH-047 does **not** author the asset processor, introduce media storage columns, fetch originals during sends or depend on a hypothetical READY asset. Until an approved prepared-media interface exists, real image-header sending fails closed; text-only templates work independently. BG003 uses a Meta-compatible approved sample for image-header template creation and never substitutes a merchant original URL as the sample. No new ARCH-047 Shared AST task is necessary merely for these bindings.

## Consistency and Transactions

PostgreSQL is durable state. Workers assume duplicate/out-of-order jobs. Business service operations use transactions/CAS and idempotency keys where required, not DB-owned template lifecycle constraints. No external Meta API, LLM or Redis operation inside a SQL transaction. Unknown Meta create outcomes require provider read/reconciliation before retry. Publication processes bounded targets with **shop-level all-selected-language atomicity or an explicit, reviewed partial policy**. Active shop slots are replaced only after operator confirmation. Frozen `parameterBindingsSnapshot` must correspond to exactly the submitted components; any mismatch makes runtime preparation fail closed. Only the existing final admission path can reserve/settle/compensate credits and commit sends.

## Ordering and Failure Handling

Per-definition translation/review, Meta provider events and per-shop publication use narrow concurrency identities. Provider status, drift, missing template, incomplete locale set or ambiguous shop-language slot is a structured failure, never an arbitrary fallback to an unverified template. If a verified offer is unavailable, C returns `NO_OFFER` instead of allowing invented discounts. Missing checkout URL is not fabricated. An admin's new release never silently replaces older eligible assignments. Duplicate response-wrapper application must be refused or idempotently recognised before sending.

## Scalability

Keep high-volume checkout-event filtering and ordinary send preparation bounded; expensive AI offer evaluation is invoked only for genuinely eligible `AI_BEST_APPLICABLE` outreach, not raw webhook events. Provider translation/Meta template creation run on separate low-throughput control-plane workloads with bounded retries; bulk publication uses paginated targets and does not lock all shops globally. Recovery selection uses indexed local database reads, not provider catalogue fetches. Reuse approved BullMQ/OTel infrastructure; any new queue routing or external API configuration must be justified by inspected capability gaps and assigned to its owner.

## Security

Meta credentials stay server-side. Meta webhooks are authenticated at Messaging ingress. Every lookup and prepared message is shop-, WABA-, conversation-/checkout- and recipient-scoped. Avoid logging sensitive AST samples, customer text, credentials or checkout URLs. Staff Admin operations require `SUPER_ADMIN` authorization. Do not treat an approved provider template as permission to contact a customer; consent, local authoritative STOP, service window, moderation and billing guards are independent. CommerceAgent can only retrieve read-only commerce information.

## Observability

Modules emit bounded business-outcome logs (run/definition IDs, WABA/template IDs where non-secret, status, attempt, cause), through the shared logger. Reuse existing OTel/framework request and BullMQ instrumentation; do not duplicate generic telemetry. Failed or delayed translation, unknown Meta create, stale webhook, provider drift, ambiguous template slot, offer verification refusal and wrapper-application errors must be traceable without customer contents. Provider/observability outages must not turn otherwise ineligible sends into eligible ones.

## Rollout / Migration

Classify production compatibility at implementation time. The 11-table Database migration is additive and preserves existing shop assignments and audit records. **The Shared v2 template-status contract implementation and publication are already Complete; there is no separate Shared AST publication gate.** Admin-owned compiled JSON and frozen binding metadata are the storage boundary consumed by completed BG001/BG003. Module implementation (BG001–005) and automated integration (BG006) are marked Complete; BG007 is a separate, still-Ready merchant follow-up integration and must reuse the BG001 preparer and BG006 late send fence without adding AST logic or a provider metadata GET. Explicitly publish approved shop assignments; legacy unlinked assignments are not silently treated as Moda-authored. Internal wrapper activation remains independent of Meta submission. System Test runs only after all required implementations and publication dependencies are Complete and the developer has performed any desired manual validation.


### ARCH-047 BG009 durable prepared-message dependency reconciled (2026-10-26)

Developer Attempt 1 identified a real moderation/delivery identity conflict: `MerchantConversationSendCommand.textBody` is immutable merchant intent, while moderation, final admission and provider paths used that raw body. A wrapper cannot be appended after moderation, and the accepted `textBody` cannot be rewritten.

`ARCH-040-DATABASE-007` is now Complete. It adds nullable, set-once `preparedTextBody`, `preparedWrapperEvidence` and `preparedAt` to the existing command and validates HUMAN_COMMAND/TEXT moderation against the SHA-256 of the frozen complete body. No new table, AST format, or DB-owned wrapper-eligibility policy was introduced. Both explicit BG009 dependencies (`ARCH-047-BACKGROUND-005` and `ARCH-040-DATABASE-007`) are Complete, so the same developer-owned BG009 task is **Ready** at its existing Attempt 1 count; its next claim is Attempt 2. Before Background source edits, the developer must merge DATABASE-007 into Database `main`, synchronize BG009's `database/` submodule to that merged commit, and regenerate/validate Prisma Client. Do not point the submodule at the unmerged Database task branch. Then BG009 wires freeze → whole-text moderation → exact durable `ConversationMessage.content` → provider text, with late wrapper/policy checks and no re-render on retries. The post-window BG007 template path remains unchanged and must be reconciled where it shares the dispatcher.

`ARCH-047-SYSTEM-TEST-001` must prove wrapper-only moderation refusal, lease/replay immutability, changed wrapper before permit, final STOP/window fences, no-wrapper passthrough and exact moderated/persisted/provider-text identity. Do not mark BG009 Complete based solely on the preparation-only module.

## Decisions / Tasks

### Current task inventory and execution state — 26 October 2026, 14:48 snapshot

| Task group | Task YAML status | Meaning for remaining work |
|---|---|---|
| `ARCH-047-DATABASE-001` | **Complete** | Consolidated 11-table schema; do not create DATABASE-002–004. |
| `ARCH-047-ADMIN-001/002` | **Superseded** | No external Meta imports or shop-to-shop copying. |
| `ARCH-047-ADMIN-003`–`008` | **Complete** | Admin-owned AST authoring, validation, translation request/reconstruction, compilation, Meta control and publication. |
| `ARCH-047-SHARED-001/002` | **Complete** | **Only** the Meta template-status event v2 transport contract and its published package; no Shared AST. |
| `ARCH-047-MESSAGING-001` | **Complete** | Signed webhook producer for the existing `whatsapp-events` queue. |
| `ARCH-047-BACKGROUND-001`–`006` and `008` | **Complete** | Five modules plus automated recovery and AI wrapper integrations. BG004 still defaults to No Offer where provider eligibility evidence is unavailable. |
| `ARCH-047-BACKGROUND-007` | **Ready**, Attempt 0 | **Paused for architectural documentation review**. Merchant post-window template integration remains to be implemented and validated; BG001, BG004 and BG006 are Complete. |
| `ARCH-047-BACKGROUND-009` | **Ready**, Attempt 1 | Human in-window wrapper integration awaits developer Attempt 2; `ARCH-040-DATABASE-007` is Complete. |
| `ARCH-047-SHOPIFY-001` / `ARCH-047-API-001` | **Complete** | Follow-up merchant-admission interface fixes; integration evidence belongs to their task records. |
| `ARCH-047-WOOCOMMERCE-001` | **Pending** | WooCommerce merchant follow-up UI; its API prerequisite is Complete, but task YAML has not been promoted. |
| `ARCH-047-SYSTEM-TEST-001` | **Pending** | Terminal end-to-end validation; blocked by incomplete implementation tasks. |

A **Complete** task is not automatically evidence of a merged implementation-main commit; use the owning task's acceptance/merge evidence. Do not overwrite historical Completion Reports or Architect Reviews when reconciling this current planning view.

### Module-first Background task boundaries and formal dependencies

| Task | Owned outcome | Task YAML status | Actual `depends_on` |
|---|---|---|---|
| `BACKGROUND-001` | Recovery Template Preparation: read compiled Meta components and bindings, resolve trusted parameters, return prepared payload; **no AST authoring or compilation** | Complete | `ARCH-047-DATABASE-001` |
| `BACKGROUND-002` | Keyed text-segment translation only; write `TranslationItem.translatedAst` results | Complete | `ARCH-047-DATABASE-001` |
| `BACKGROUND-003` | Submit frozen Meta components; consume v2 status events and reconcile provider drift | Complete | `ARCH-047-DATABASE-001`, `ARCH-047-SHARED-002` |
| `BACKGROUND-004` | Read-only verified offer resolution / safe No Offer | Complete | None |
| `BACKGROUND-005` | Render Admin-prepared conversation wrapper projection; no AST compiler | Complete | `ARCH-047-DATABASE-001` |
| `BACKGROUND-006` | Automated recovery integration, common late provider/send fence | Complete | `ARCH-047-BACKGROUND-001`, `ARCH-047-BACKGROUND-004` |
| `BACKGROUND-007` | Merchant post-window template integration using BG001 + BG006 existing ports | Ready, paused | `ARCH-047-BACKGROUND-001`, `ARCH-047-BACKGROUND-004`, `ARCH-047-BACKGROUND-006` |
| `BACKGROUND-008` | AI in-window wrapper integration | Complete | `ARCH-047-BACKGROUND-005` |
| `BACKGROUND-009` | Human in-window wrapper integration with frozen prepared content | Ready | `ARCH-047-BACKGROUND-005`, `ARCH-040-DATABASE-007` |

**BG007 handoff decision:** The parent architecture and BG001 now agree: `ADMIN-003/005` own the AST and persisted Meta compilation, `BACKGROUND-001` consumes compiled provider payload/bindings, and the only ARCH-047 Shared package is the already-published Meta status-event v2 used by Messaging/BG003. BG007 requires **no new Shared AST package, no AST parser/compiler, and no task dependency beyond its three recorded complete Background prerequisites**. After architect review of this documentation amendment, reconcile the stale “parent/BG001 unresolved” note in the BG007 task through that task's authorised workflow before its next claim. **Do not treat this documentation patch as a BG007 implementation or a status transition.**

### Execution dependency view

```mermaid
flowchart LR
  DB[DATABASE-001] --> B1[BG001 Template Preparation]
  DB --> B2[BG002 Translation]
  DB --> B3[BG003 Meta Management]
  DB --> B5[BG005 Wrapper Rendering]
  B4[BG004 Offer Resolution] --> B6[BG006 Automated Integration]
  B1 --> B6
  B1 --> B7[BG007 Post-window Integration]
  B4 --> B7
  B6 --> B7
  B5 --> B8[BG008 AI Integration]
  B5 --> B9[BG009 Human Integration]
  DB40[ARCH-040 DATABASE-007] --> B9
  B2 --> T[Integrated System Test]
  B3 --> T
  B6 --> T
  B7 --> T
  B8 --> T
  B9 --> T
```

The graph expresses necessary interfaces, not serial deployment of unrelated modules. `BACKGROUND-002`–`005` may proceed in parallel when prerequisites are met. `BACKGROUND-004` can be investigated without waiting for Meta template authoring. No implementation, Shared publication or Gateway task may depend on a system-test task.

## Remaining gates and repository ownership — 26 October 2026, 14:48 snapshot

The 06:28 review identified gaps before several implementation tasks were completed. They are not automatically still present after those tasks became Complete. Use owning task files and current source, not this older narrative, to establish the actual live behaviour.

| Concern | Current authoritative task state | Next verification / owner |
|---|---|---|
| **Checkout-specific positive discount eligibility** | `BACKGROUND-004` Complete, but its provider-read adapters previously returned unavailable and therefore safe `NO_OFFER` | Recovery-offer/provider-read owner must demonstrate verified per-checkout, per-customer eligibility for CODE/AUTOMATIC offers before claiming positive-offer coverage. No AI cart mutation. System Test must report this as an unresolved functional limitation until independently validated. |
| **Automated recovery legacy selector/category paths** | `BACKGROUND-006` Complete | Inspect BG006's merged source and accepted test evidence for removal of obsolete imports/category GET and the required late local provider-status fence; System Test independently verifies the final send path. Do not reassign completed BG006 work to BG007. |
| **Merchant post-window follow-up** | `BACKGROUND-007` **Ready and paused**; Shopify/API merchant admission tasks Complete | BG007 consumes BG001 prepared bindings + BG006 late fence, preserves one-follow-up/STOP/consent/moderation/billing, and removes legacy human-branch verifier/parameter trust only after a reference audit. No BG007 feature code is claimed by this reconciliation. |
| **WooCommerce merchant follow-up UI** | `ARCH-047-WOOCOMMERCE-001` Pending; `API-001` Complete | WooCommerce owner completes modular template picker and authenticated API proxy. Keep this implementation separate from BG007. |
| **AI vs human wrappers** | `BACKGROUND-008` Complete; `BACKGROUND-009` Ready, Attempt 1 with `ARCH-040-DATABASE-007` Complete | Verify AI wrapper path through accepted BG008 evidence; BG009 completes frozen prepared-message, full-text moderation and exact provider-content identity without changing post-window BG007 behaviour. |
| **Integrated certification** | `SYSTEM-TEST-001` Pending | Run only when all required implementation and publication tasks are Complete; certify immutable Admin authoring, 19 translations, provider status v2, six recovery purposes, offer evidence, human/AI wraps, consent/STOP/moderation and merchant parity. No external-import or in-place-edit scenarios. |

**Legacy code retirement:** Only the owning unfinished implementation may remove a now-orphaned production path, after confirming all callers migrated and adding regression evidence. Do not delete completed BG001/006 functionality or weaken consent, STOP, moderation, credit compensation or follow-up restrictions as part of documentation reconciliation.

**Task execution frontier:** The specific BG007 documentation blocker is resolved *as an architecture decision* in this document and BG001; BG007 still requires its own task-record clarification/authorised claim and focused validation. BG009 follows its existing developer worktree and ARCH-040 DB007 synchronisation instructions. ARCH-049 media readiness is separate; text-only sends are not blocked by unimplemented image-header readiness.

## Open Questions / Gates Before Integrated Acceptance

1. **Admin/Background persistence boundary is settled:** Admin owns AST and prepared payloads; BG001 and BG003 consume frozen compiled values. No new Shared AST work is required; Shared v2 event publication is Complete.
2. **Positive offers:** independently demonstrate provider-backed checkout eligibility or retain a documented fail-safe No Offer limitation; do not claim six-purpose positive-offer production readiness without evidence.
3. **Checkout association:** prove reliable shop-scoped checkout context for wrappers, including missing/stale URL behaviour; a wider conversation-identity migration is outside this task.
4. **Provider webhook and readiness:** verify Meta status observations reach the accepted Messaging → BullMQ → BG003 path and BG006's late revocation/freshness fence is effective.
5. **Final task state:** BG007 and BG009 Ready but unfinished; Woo merchant UI Pending; System Test Pending. No `_index.md` update until user explicitly closes the architecture session.

## Change History

- 2026-10-23 — Initial shop-scoped Admin Meta import/assignment design (now superseded).
- 2026-10-24 — User decisions: Moda Admin-only authoring, immutable new-version templates, English-first 20-language translation, Meta approval then explicit publication, six recovery purposes, checkout-related AI/human wrappers and strictly read-only CommerceAgent.
- 2026-10-24 — Consolidated DATABASE-001 11-table Attempt 7 schema considered the database contract; business lifecycle enforcement remains in services.
- 2026-10-24 — **Module-first Background plan adopted**: five feature modules and four thin integrations; Admin owns AST parsing, compilation and keyed translation preparation, Background consumes prepared data using existing Batch and outbound admission; BG002–BG009 portable task definitions prepared, not materialised.
- 2026-10-24 — **Admin module-first task definitions created**: six independent, DATABASE-001-only-dependent tasks; ADMIN-001/002 superseded, with no Admin AST/Meta compiler work delegated to Shared or Background.

- 2026-10-25 — Clarified Meta template-status v2 occurrence identity, Shared producer/consumer contract, atomic UNKNOWN provider observation fence and BG006 late-check freshness gate; no additional database table.

- 2026-10-26 — Reconciled current task YAML, identified checkout-specific verified-offer and merchant admission gaps, defined separately owned Shopify/API/Woo follow-ups, required removal of superseded runtime code after replacement, and rewrote SYSTEM-TEST-001 as terminal six-purpose/merchant safety certification.

- 2026-10-26 — **Post-completion documentation reconciliation:** authoritative 14:48 task-state inventory; Admin-only AST/compilation and saved-payload boundary made explicit for completed BG001; Shared-001/002 confirmed as completed v2 template-status queue contract only. BG007 retains its own Ready/unclaimed state and remains paused pending review of the task-level handoff note. No implementation code, completion/review history or `_index.md` changed.
