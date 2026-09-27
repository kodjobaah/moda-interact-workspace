---
id: ARCH-023
title: Merchant knowledge and store-aware Commerce Agent configuration
status: proposed
coordinator: moda_architect
created: 2026-09-27
updated: 2026-09-27
---

# ARCH-023: Merchant knowledge and store-aware Commerce Agent configuration

## Status

Proposed.

This architecture is defined from the 2026-09-27 workspace snapshot and the design decisions agreed in the architecture session. The definitions in this patch are portable coordination artifacts only; they are not materialised task branches/worktrees in the developer's canonical workspace.

## Problem

Moda already has:

- dynamic billing `Feature` records and plan-feature materialisation;
- merchant feature preferences;
- published Commerce capabilities bound to features;
- platform/shop Commerce prompt records and revisions;
- data-driven `CommercePromptTemplateCategory` / `CommercePromptTemplate` records;
- internationalisation with canonical BCP-47 tags and 20 supported merchant locales;
- asynchronous Background reconciliation;
- PostgreSQL, BullMQ/Redis and an existing Commerce Agent runtime.

The current system does not yet provide one coherent way for a merchant to:

1. classify the type of store they operate;
2. receive a sensible, localised default Shop Instruction prompt for that store category;
3. keep platform instructions and store-specific instructions additive rather than replacement-based;
4. configure public web pages as factual store knowledge;
5. limit that knowledge according to the merchant's plan;
6. process those pages asynchronously and safely;
7. retrieve only the current shop's relevant knowledge during a Commerce Agent conversation; and
8. preserve security semantics independently of the language used by customers, prompts or retrieved content.

The existing Commerce prompt resolver currently resolves the shop prompt as an override of the platform prompt. The target architecture requires both to be applied.

Merchant Knowledge must also compose with other Commerce capabilities. It must provide factual context without becoming an authority mechanism. Web page content must never create a feature, capability, tool grant or permission merely because the page contains instructions addressed to an AI agent.

## Goals

ARCH-023 will:

1. introduce a normal merchant-opt-in `merchant_knowledge` Feature that can be mapped to any pricing plan;
2. store per-plan Merchant Knowledge limits as plan-feature configuration rather than hard-coded Free/Starter rules;
3. count logical Knowledge Entries rather than physical URLs for commercial limits;
4. permit locale variants under one logical Knowledge Entry without consuming additional entry slots;
5. define a deterministic language-neutral content-unit metric;
6. store processed merchant knowledge durably in PostgreSQL and store vector embeddings with pgvector;
7. use exact pgvector similarity after narrow trusted relational filtering rather than Redis vector search in v1;
8. keep PostgreSQL authoritative and Redis limited to queue/reconciliation duties for this feature;
9. add store-category selection to the pre-managed-pricing onboarding path;
10. preselect a category from Shopify product-taxonomy evidence while allowing the merchant to change it;
11. persist that onboarding choice before leaving Moda but keep it pending until Shopify plan activation is durably projected as `ACTIVE` or `TRIALING`;
12. seed the initial Shop Instructions from the exact localised default template the merchant previewed;
13. preserve later category changes as pending Shop Instruction drafts until an Admin explicitly publishes them;
14. move Platform Instructions and Shop Instructions authoring to the Admin application;
15. keep capability prompts and external-tool behaviour in Commerce Studio;
16. translate Admin-authored categories/templates/platform/shop prompts into all 20 supported locales through the existing translation provider/runtime;
17. require all 20 translations for the current source version before a template or Admin-owned prompt revision can become available/published;
18. use `ShopSettings.defaultLanguageTag` (with English fallback) to select store instructions and Merchant Knowledge sources;
19. keep customer conversation language independent, controlling only the response language;
20. add one feature-bound Commerce capability, `merchant_knowledge`, with one shop-scoped lookup tool/policy operation;
21. allow every otherwise-authorised capability in the same turn to benefit from Merchant Knowledge without Merchant Knowledge granting those capabilities;
22. permit merchant-initiated refresh of configured knowledge pages; and
23. preserve active knowledge while a replacement/refresh revision is processing or fails.

## Non-Goals

ARCH-023 does not:

- add a capability per merchant URL;
- republish a Commerce release when a merchant changes a URL;
- make merchant web pages authoritative agent instructions;
- allow merchant-authored arbitrary prompt instructions on each knowledge source in v1;
- automatically crawl or periodically refresh merchant pages;
- render JavaScript-heavy sites in a headless browser;
- introduce a new public/private Commerce ingestion endpoint;
- use Redis as the Merchant Knowledge vector database in v1;
- introduce capability-to-capability dependency semantics;
- translate capability prompts managed in Commerce Studio;
- vary authorisation, tenant identity or tool grants by language;
- implement the rare onboarding concurrency edge cases discussed during design (for example, two simultaneous category-selection tabs); or
- redesign the existing Shopify billing lifecycle.

## Current Architecture

### Feature and plan model

The current database has:

```text
billing.Feature
billing.MerchantPricingPlanFeature
billing.BillingPlanFeature
billing.ShopFeaturePreference
```

`MerchantPricingPlanFeature` and `BillingPlanFeature` currently express membership/enabled state but do not carry generic per-feature configuration. ARCH-023 extends both so Merchant Knowledge limits can be materialised with the plan.

### Commerce capability model

`commerce.CommerceCapability` already supports:

```text
selectionBinding = FEATURE
featureId = <billing.Feature.id>
```

The Commerce runtime resolves active plan features and merchant preferences before selecting FEATURE-bound capabilities for a new grant. This is the correct integration point for Merchant Knowledge.

### Prompt model

The current schema already contains:

```text
CommercePromptTemplateCategory
CommercePromptTemplate
CommerceAgentPrompt
CommerceAgentPromptRevision
CommerceAgentConfiguration
```

`CommerceAgentPrompt` already distinguishes `PLATFORM` and `SHOP` scopes. The current effective configuration resolver, however, treats an active Shop prompt as a replacement for the Platform prompt. ARCH-023 changes prompt resolution only; model-selection override semantics remain unchanged.

### Language model

`ShopSettings.defaultLanguageTag` already exists. Shared internationalisation already canonicalises BCP-47 language tags. Existing merchant catalogue migrations define the supported merchant-language set:

```text
cs, da, de, en, es, fi, fr, it, ja, ko,
nb, nl, pl, pt-BR, pt-PT, sv, th, tr, zh-Hans, zh-Hant
```

ARCH-023 reuses this exact supported-locale set for dynamic store-category/template/platform/shop prompt translations and Merchant Knowledge source variants.

### Translation

Background already has an approved OpenAI-backed translation provider and reconciliation logic. ARCH-023 reuses that provider/runtime and does not introduce a second translation provider.

### Billing onboarding

`/app/billing/select` currently authenticates the merchant and redirects directly to Shopify Managed Pricing. ARCH-023 inserts a Moda-owned store-category gate immediately before this redirect.

The existing billing callback and Background reconciliation project Shopify subscription state into `SubscriptionProjectionStatus`. ARCH-023 uses only durable `ACTIVE` / `TRIALING` projection state as the category-activation boundary; `ShopSettings.onboardingCompleted` remains a commercial milestone and is not sufficient authority.

### PostgreSQL vector support

The developer verified that the target PostgreSQL installation supports pgvector. ARCH-023 nevertheless adds `CREATE EXTENSION IF NOT EXISTS vector` to the canonical database migration so deployment does not rely on undocumented manual extension state.

## Proposed Architecture

### Trust and instruction hierarchy

The runtime trust model is:

```text
LEVEL 0 — CODE/RUNTIME ENFORCEMENT
  tenant identity
  subscription / feature entitlement
  capability selection
  tool grant
  tool input validation

LEVEL 1 — IMMUTABLE SECURITY KERNEL
  code-owned Commerce runner instructions
  untrusted-data semantics
  permission non-expansion

LEVEL 2 — PLATFORM INSTRUCTIONS
  Admin-authored, published, localised

LEVEL 3 — SHOP INSTRUCTIONS
  Admin-authored, shop-scoped, published, localised

LEVEL 4 — CAPABILITY INSTRUCTIONS
  Commerce Studio-owned capability-local behaviour

LEVEL 5 — UNTRUSTED CONTEXT
  customer messages
  merchant knowledge pages
  catalogue/provider text
  tool results
```

The immutable security kernel is never translated into separately maintained policy variants. Its semantics are code-owned and enforced by runtime checks. Platform and Shop Instructions are localised configuration, but no translation can change runtime authorisation.

### Platform + Shop prompt composition

Model selection remains:

```text
shop model override ?? platform model
```

Prompt resolution becomes:

```text
immutable kernel
+ platform prompt translation selected for shop language
+ optional shop prompt translation selected for shop language
+ selected capability prompts
```

It is never:

```text
shopPrompt ?? platformPrompt
```

### Store categories

`CommercePromptTemplateCategory` is the stable data-driven Store Category catalogue, for example:

```text
clothing-fashion
consumer-electronics
health-beauty
home-garden
general-retail
```

Each enabled category must have:

- one explicit default template;
- localised category display content;
- zero or more Shopify taxonomy mappings; and
- one platform-wide fallback category must be designated for shops whose Shopify product taxonomy yields no configured match.

Shopify taxonomy mappings are configuration, not hard-coded category names in the Shopify application.

### Store category suggestion

Before the first redirect to Shopify Managed Pricing, Moda reads bounded Shopify shop/category evidence, principally the standardised product-category identifiers available for the shop.

Suggestion is deterministic:

1. map observed Shopify taxonomy identifiers through Admin-configured Store Category mappings;
2. select the category with the highest number of mapped observations;
3. break ties by category display order then stable id; and
4. use the designated fallback category when no mapping is found.

The result is preselected. The merchant can change it before continuing.

### Pending Commerce shop profile

A new `CommerceShopProfile` stores Commerce-specific merchant classification rather than placing Commerce category state in `ShopSettings`.

Conceptually:

```text
CommerceShopProfile
  shopId

  activeStoreCategoryId

  pendingStoreCategoryId
  pendingTemplateId
  pendingTemplateEditVersion
  pendingLanguageTag
  pendingPromptRevisionId
  pendingSelectedAt
```

The exact template edit version and language previewed by the merchant are pinned before the Shopify redirect. Historical template translations for that edit version remain available, so a later Admin edit does not silently change the prompt the merchant confirmed.

A category/template later becoming disabled is not an onboarding invalidation rule in v1; the already-pinned available snapshot may still complete the pending onboarding attempt.

### Onboarding activation

The merchant flow is:

```text
click Select plan
  -> Moda category gate
  -> Shopify-derived category preselected
  -> merchant confirms/changes category
  -> show exact localised default-prompt preview
  -> persist pending CommerceShopProfile selection
  -> redirect to Shopify Managed Pricing
```

If the merchant leaves Shopify without activating a plan, pending state remains but nothing becomes active.

When billing callback/reconciliation later projects the subscription as `ACTIVE` or `TRIALING`, Background reconciliation:

1. verifies the pending pinned template edit-version bundle remains present;
2. creates the initial Shop prompt lineage/revision when none exists;
3. copies the exact 20-language translation bundle from the pinned template edit version;
4. publishes/activates that Shop prompt;
5. promotes `pendingStoreCategoryId` to `activeStoreCategoryId`; and
6. clears pending onboarding fields.

This operation is idempotent and recoverable through the existing reconciliation approach.

### Later category changes

After onboarding, the merchant may select another Store Category.

A later change:

1. stores a new pending category/template/language snapshot;
2. creates a new Shop Instructions DRAFT from the pinned default-template translation bundle;
3. keeps the existing published Shop Instructions and active category unchanged; and
4. exposes the draft/pending category in Admin.

When an authorised Admin publishes/activates that draft, the same transaction promotes the pending category to active.

### Admin-owned prompt authoring

The Admin application becomes the only product authoring surface for:

- Platform Instructions;
- Shop Instructions;
- Store Categories;
- Store Category Shopify taxonomy mappings;
- default category templates; and
- localised prompt/template translation lifecycle.

Commerce Studio stops offering Platform/Shop prompt authoring after the Admin surface is available.

Capability prompts remain Commerce Studio-owned because they describe executable capability/tool behaviour.

### Localised prompt lifecycle

For Admin-authored templates and Platform/Shop prompt revisions:

1. one source-language text/version is authored;
2. a translation job is queued to Background using the existing approved translation provider;
3. immutable translations are stored for all 20 supported locales, keyed to the exact source edit version/revision;
4. all 20 current-version translations must be `AVAILABLE` before a template can be merchant-selectable or a Platform/Shop prompt revision can be published/activated; and
5. editing the source increments the source edit version and makes earlier translations stale for the new version without deleting their historical snapshot.

For prompt templates, translation history is keyed by `(templateId, sourceEditVersion, locale)` so onboarding can pin an exact edit version without reintroducing a separate template-revision entity.

For `CommerceAgentPromptRevision`, translation history is keyed by `(promptRevisionId, sourceEditVersion, locale)` while the published revision remains immutable.

### Shop-language selection

Store configuration language is resolved from:

```text
ShopSettings.defaultLanguageTag
  -> canonical supported Moda locale / primary-language match
  -> English fallback
```

This selects:

- Platform Instructions translation;
- Shop Instructions translation;
- category/default-template preview; and
- Merchant Knowledge locale source.

Customer conversation language is resolved independently by the existing conversation language path and controls only generated reply presentation.

Example:

```text
shop default language: fr
Platform Instructions used: fr
Shop Instructions used: fr
Merchant Knowledge used: fr
customer language: en
agent reply: en
```

### Merchant Knowledge feature entitlement

Merchant Knowledge is a normal merchant-opt-in feature:

```text
Feature.key = merchant_knowledge
Feature.activationMode = MERCHANT_OPT_IN
```

No plan name is hard-coded in application logic.

`MerchantPricingPlanFeature.configuration` is materialised exactly into `BillingPlanFeature.configuration`.

For `merchant_knowledge`, configuration schema v1 is:

```json
{
  "schemaVersion": 1,
  "maxKnowledgeEntries": 5,
  "maxContentUnitsPerLocaleSource": 1500
}
```

Values are plan data. The numbers above are examples, not architecture-defined Free/Starter constants.

Missing or invalid Merchant Knowledge configuration fails closed for the feature.

### Content-unit metric

ARCH-023 defines one deterministic provider-independent content unit:

```text
normalise extracted text to Unicode NFC
normalise whitespace
count Unicode code points (not UTF-16 code units)
contentUnits = ceil(codePointCount / 4)
```

The initial recommended source allowance is `1500` content units, approximately 6000 normalised Unicode code points. Plans may configure another value within validated platform bounds.

This metric is used for entitlement/storage limits and is not tied to an LLM tokenizer.

### Logical Knowledge Entries

Commercial limits count logical entries, not URL rows.

Example:

```text
Knowledge Entry: Customer Support
purpose = CUSTOMER_SUPPORT
position = 1

  fr -> https://merchant.example/aide
  en -> https://merchant.example/help
```

This consumes one Knowledge Entry slot.

Each entry has:

- a merchant-facing name;
- one allow-listed Knowledge Purpose;
- deterministic position/priority; and
- up to one source per supported Moda locale.

Knowledge Purpose v1 values are:

```text
COMPANY_INFORMATION
CUSTOMER_SUPPORT
POLICIES
FAQ
PRODUCT_INFORMATION
SHIPPING_AND_DELIVERY
```

Purposes are trusted platform metadata. They narrow retrieval; they do not grant tools or actions.

### Knowledge source revisions

Each `(entry, locale)` source uses immutable/revisioned processing:

```text
MerchantKnowledgeEntry
  -> MerchantKnowledgeSource
      -> MerchantKnowledgeSourceRevision
          -> MerchantKnowledgeChunk[]
```

Source revision states:

```text
PENDING
PROCESSING
ACTIVE
FAILED
```

The source points to one active revision.

When URL/refresh processing starts, the prior active revision remains active. Only after extraction, content-limit processing, embedding and chunk persistence all succeed is the new revision promoted atomically. Failure leaves the old revision active.

Entitlement availability is derived separately from ingestion status. A plan downgrade does not rewrite an `ACTIVE` revision to a synthetic suspended state.

### Plan downgrade

The effective merchant entitlement selects the first `maxKnowledgeEntries` entries by deterministic `position`.

Entries beyond the current limit remain durably stored but are not returned by `merchantKnowledge.lookup`. Re-upgrade can make them eligible again without refetching.

### Merchant-initiated refresh

There is no scheduled refresh in v1.

The merchant can select **Refresh**, which creates a new pending source revision and queues processing. The existing active revision remains in use until refresh succeeds.

### Public URL ingestion

Any public HTTPS URL may be configured; it does not need to share the Shopify storefront domain.

Background owns ingestion. There is no Background -> Commerce ingestion HTTP call.

The Background processing boundary is:

```text
load pending source revision
  -> validate current shop / entry state
  -> SSRF-safe public HTTPS resolution
  -> bounded fetch and redirect validation
  -> accept text/html or text/plain
  -> strip HTML / remove executable markup
  -> normalise text
  -> enforce content-unit cap (truncate safely and mark truncated)
  -> deterministic chunking
  -> generate multilingual embeddings
  -> persist chunks/vectors
  -> promote revision ACTIVE
```

Security requirements include:

- reject loopback, private, link-local, metadata and other non-public IPv4/IPv6 destinations;
- revalidate every redirect and resolved address;
- bounded redirects, connect/read deadline and response bytes;
- no browser/JavaScript execution;
- no credentials/cookies from Moda or Shopify sent to the source;
- no logging of extracted page content; and
- only `text/html` and `text/plain` in v1.

### Chunking and embeddings

Recommended v1 chunking is:

```text
target chunk size: 300 content units
chunk overlap: 50 content units
```

A source capped at 1500 content units therefore normally produces about 6 chunks.

Background and Commerce use one platform-wide multilingual embedding model/provider selected only through deployment environment configuration. The model must support semantic similarity across all 20 supported Moda languages.

The canonical deployment contract is:

```text
EMBEDDING_PROVIDER
EMBEDDING_MODEL
EMBEDDING_DIMENSIONS
EMBEDDING_INDEX_VERSION
EMBEDDING_API_KEY   # server-side secret
```

No embedding-model catalogue or Admin selector is introduced. Stored revision metadata records provider/model/dimensions/index version. A model/index-version change requires reprocessing/reindexing active knowledge before Commerce begins querying with the new vector space; runtime lookup fails closed on provenance mismatch.

### PostgreSQL + pgvector

PostgreSQL is the durable source of truth for:

- source text;
- revision lifecycle;
- chunks;
- vector embeddings; and
- embedding provenance.

`MerchantKnowledgeChunk.embedding` uses pgvector. Prisma may model the vector as an unsupported native type while Background/Commerce use parameterised raw SQL for vector writes/distance queries.

ARCH-023 does not create a global ANN vector index initially.

Runtime queries first restrict by trusted relational scope to a small candidate set, then perform exact cosine/vector distance ordering over that set.

This is deliberate because a typical shop has tens of eligible chunks even if the platform has hundreds of thousands globally.

### Merchant Knowledge capability

The platform authors one global Commerce capability:

```text
key: merchant_knowledge
selectionBinding: FEATURE
featureId: Feature(merchant_knowledge)
```

The capability binds one platform-owned lookup tool/policy operation:

```text
merchantKnowledge.lookup
```

The agent-facing input contains only bounded semantic search intent, conceptually:

```json
{
  "query": "customer support telephone number",
  "purposes": ["CUSTOMER_SUPPORT"]
}
```

There is no `shopId` input.

The authorised Commerce context supplies the shop identity.

### Runtime lookup

At execution time `merchantKnowledge.lookup`:

1. receives the authenticated/authorised shop context from Commerce;
2. re-reads current Merchant Knowledge feature entitlement/configuration;
3. fails closed if the feature is not currently entitled/enabled/configured;
4. takes the first N logical entries by position where `N = maxKnowledgeEntries`;
5. narrows to requested allow-listed purposes when supplied;
6. resolves the source locale from `ShopSettings.defaultLanguageTag`, falling back to English when the shop locale/source is unavailable;
7. generates a query embedding with the configured multilingual embedding model;
8. exact-searches only active chunks belonging to eligible same-shop entries/source revisions;
9. returns a bounded top result set with source/purpose metadata; and
10. marks the returned material as untrusted reference data in the tool-result contract.

### Cross-capability composition

Merchant Knowledge does not create dependencies from Product/Recovery/Returns/etc. onto Merchant Knowledge.

If the current Commerce grant contains both:

```text
product_recommendations
merchant_knowledge
```

then the model can use both tool sets during the same turn.

If it contains only Merchant Knowledge, retrieved content can support an informational answer but cannot create an operational tool.

Invariant:

```text
Knowledge can inform a capability.
Knowledge can never enable or authorise a capability.
```

### Prompt-injection handling

Prompt-injection detection is not a security boundary.

The same untrusted classification applies whether retrieved content is English, French, Arabic, mixed-language, Unicode-obfuscated or claims to be a system message.

Merchant knowledge may never:

- alter tenant identity;
- change feature eligibility;
- add a capability;
- add a tool;
- expand a tool grant;
- grant permission for an action;
- override immutable/platform/shop/capability instructions; or
- modify durable business state except through an independently authorised tool that passes its own validation.

## Request / Event Flows

### First onboarding category flow

```text
Merchant -> Shopify app: choose plan
Shopify app -> Shopify Admin API: read bounded taxonomy evidence
Shopify app -> PostgreSQL: read enabled category mappings/default templates
Shopify app: preselect suggested/fallback category
Merchant -> Shopify app: confirm/change category
Shopify app -> PostgreSQL: persist pending category + exact template edit version + shop language
Shopify app -> Shopify Managed Pricing: redirect

[merchant may abandon here; pending state remains]

Shopify -> Moda billing callback/reconciliation: plan activated
Billing -> PostgreSQL: Subscription ACTIVE/TRIALING
Background profile reconciler -> PostgreSQL: create/publish initial Shop Instructions from pinned 20-locale template bundle
Background profile reconciler -> PostgreSQL: promote pending category to active
```

### Later category-change flow

```text
Merchant -> Shopify app: choose new category
Shopify app -> PostgreSQL: persist pending category/template snapshot
Background profile reconciler -> PostgreSQL: create Shop Instructions DRAFT from pinned template bundle
Admin -> Admin app: review/edit translated Shop Instructions
Admin -> PostgreSQL: publish/activate prompt + promote pending category atomically
```

### Merchant Knowledge ingestion flow

```text
Merchant -> Shopify app: create/update/refresh source
Shopify app -> PostgreSQL: persist entry/source + PENDING revision
Shopify app -> BullMQ: best-effort processing job
Background reconciliation -> PostgreSQL/BullMQ: repair missing/stale jobs
Background worker -> public HTTPS source: bounded safe fetch
Background worker -> embedding provider: chunk embeddings
Background worker -> PostgreSQL: content + chunks + vectors; promote revision ACTIVE
```

### Conversation lookup flow

```text
Conversation -> Commerce grant resolution
  -> feature/capability eligibility
  -> merchant_knowledge tool present only when capability is selected

LLM -> merchantKnowledge.lookup(query, purposes?)
Commerce -> PostgreSQL: current entitlement + shop default language + eligible entries
Commerce -> embedding provider: query embedding
Commerce -> PostgreSQL/pgvector: exact similarity over same-shop active candidate chunks
Commerce -> LLM: bounded untrusted reference result
LLM -> customer: answer in resolved customer conversation language
```

## Repository Responsibilities

### moda-interact-database / moda_database

Owns:

- generic plan-feature configuration columns/constraints;
- Store Category default/fallback/taxonomy mapping tables;
- category/template translation history;
- Platform/Shop prompt revision translation history;
- CommerceShopProfile;
- Merchant Knowledge entry/source/revision/chunk tables;
- pgvector extension/migration/indexes/constraints; and
- deletion/tenant-integrity constraints.

### moda-interact-shared / moda_shared

Owns:

- versioned Merchant Knowledge feature configuration schema;
- Knowledge Purpose enum/schema;
- content-unit normalisation/count helper;
- Commerce configuration queue schemas/job names/id helpers;
- supported-locale reuse contracts;
- runner instruction composition contract; and
- immutable kernel rules required for untrusted Merchant Knowledge.

### moda-interact-admin / moda_admin

Owns:

- Store Category/default-template/taxonomy mapping management;
- category/template translation dispatch/status/retry UI;
- Platform Instructions authoring/publication;
- Shop Instructions authoring/publication;
- pending category-change review/publish;
- Merchant Knowledge per-plan entitlement configuration; and
- Admin authorisation/audit presentation.

### moda-interact / moda_app

Owns:

- onboarding category suggestion/confirmation gate;
- pending category persistence before Shopify Managed Pricing;
- later merchant category selection;
- Merchant Knowledge merchant configuration UI;
- knowledge entry/source CRUD;
- merchant refresh action;
- best-effort processing job publication; and
- tenant-scoped status/entitlement presentation.

### moda-interact-background / moda_background

Owns:

- Admin configuration translation workers/reconciliation;
- pending CommerceShopProfile/subscription reconciliation;
- initial Shop Instructions bootstrap;
- later-category draft bootstrap;
- Merchant Knowledge public URL fetch/extraction/content-unit enforcement;
- embedding generation/chunk writes;
- revision promotion/failure handling; and
- knowledge processing queue reconciliation.

### moda-interact-commerce / moda_commerce

Owns:

- additive Platform + Shop instruction resolution;
- shop-language prompt translation selection;
- capability-local prompts/tool authoring in Studio;
- `merchantKnowledge.lookup` policy/tool execution;
- current entitlement revalidation at lookup;
- multilingual query embedding and exact pgvector lookup; and
- removal of duplicate Platform/Shop authoring UI from Studio after Admin replacement.

### moda-interact-gateway / moda_gateway

Owns only deployment configuration required to expose the architecture-approved embedding configuration/secret to Background and Commerce. No new service, route or private-link endpoint is required.

### moda-interact-system-test / moda_system_test

Owns terminal integrated validation after implementation is accepted and after developer manual validation.

## Data Model

### Plan-feature configuration

Add generic JSON configuration to both catalogue and materialised feature mapping:

```text
MerchantPricingPlanFeature.configuration JSONB
BillingPlanFeature.configuration JSONB
```

For `merchant_knowledge`, Shared owns runtime validation of `MerchantKnowledgeFeatureConfigurationV1`.

### Store categories and templates

Conceptual additions:

```text
CommercePromptTemplateCategory
  defaultTemplateId?
  isFallback
  translationReadyVersion?

CommercePromptTemplateCategoryTranslation
  categoryId
  sourceEditVersion
  locale
  displayName
  description
  status
  errorCode?

CommercePromptTemplateCategoryShopifyTaxonomy
  categoryId
  taxonomyCategoryId

CommercePromptTemplate
  sourceLanguageTag
  translationReadyVersion?

CommercePromptTemplateTranslation
  templateId
  sourceEditVersion
  locale
  displayName
  description
  promptText
  status
  errorCode?

CommerceAgentPromptRevision
  sourceLanguageTag
  sourceTemplateEditVersion?

CommerceAgentPromptRevisionTranslation
  promptRevisionId
  sourceEditVersion
  locale
  promptText
  status
  errorCode?
```

Historical translation rows are retained by source edit version.

### Commerce shop profile

```text
CommerceShopProfile
  id
  shopId UNIQUE
  activeStoreCategoryId?
  pendingStoreCategoryId?
  pendingTemplateId?
  pendingTemplateEditVersion?
  pendingLanguageTag?
  pendingPromptRevisionId?
  pendingSelectedAt?
  createdAt
  updatedAt
```

Profile deletion follows Shop deletion.

### Merchant Knowledge

```text
MerchantKnowledgeEntry
  id
  shopId
  name
  purpose
  position
  createdAt
  updatedAt

MerchantKnowledgeSource
  id
  entryId
  languageTag
  activeRevisionId?
  createdAt
  updatedAt

MerchantKnowledgeSourceRevision
  id
  sourceId
  revisionNumber
  status
  requestedUrl
  resolvedUrl?
  contentType?
  extractedContent?
  contentUnits?
  truncated
  contentHash?
  embeddingProvider?
  embeddingModel?
  embeddingDimensions?
  embeddingIndexVersion?
  failureCode?
  fetchedAt?
  createdAt
  updatedAt

MerchantKnowledgeChunk
  id
  revisionId
  ordinal
  content
  contentUnits
  embedding vector
```

Required uniqueness/indexing includes:

```text
Entry: (shopId, position) unique
Source: (entryId, languageTag) unique
Revision: (sourceId, revisionNumber) unique
Chunk: (revisionId, ordinal) unique
```

All entry/source/revision/chunk rows cascade from Shop ownership through the knowledge hierarchy.

No HNSW/IVFFlat index is required in v1; exact distance is intentionally evaluated after highly selective relational filters.

## Contracts

### Shared package

Implementation owners:

- `ARCH-023-SHARED-001` — Store Category/configuration translation and shop-profile reconciliation contracts;
- `ARCH-023-SHARED-002` — Merchant Knowledge purpose/configuration/content-unit/process/reconcile contracts;
- `ARCH-023-SHARED-003` — immutable runner trust/instruction composition contract.

Publication gate:

`ARCH-023-SHARED-004`

Package:

`@modainteract/moda-interact-shared`

Published exports include architecture-equivalent forms of:

```text
CommerceConfigurationTranslationJobSchema
CommerceShopProfileReconcileJobSchema
resolveSupportedShopLanguage(...)
MerchantKnowledgePurposeSchema
MerchantKnowledgeFeatureConfigurationV1Schema
MerchantKnowledgeProcessJobSchema
MerchantKnowledgeReconcileJobSchema
countMerchantKnowledgeContentUnits(...)
createMerchantKnowledgeProcessJobId(...)
```

Producer/consumer mapping:

```text
Shopify -> Background
  MerchantKnowledgeProcessJob

Admin -> Background
  CommerceConfigurationTranslationJob

Shopify/billing reconciliation -> Background
  CommerceShopProfileReconcileJob
```

All queue payloads are versioned and runtime validated.

### Runner instruction contract

Owner:

`ARCH-023-SHARED-003`

The runner keeps immutable platform security instructions first and accepts Platform/Shop instruction fragments as trusted host-owned instruction inputs ahead of capability prompts. Untrusted knowledge remains tool/context data, never runner instructions.

### `merchantKnowledge.lookup`

Owner:

`ARCH-023-COMMERCE-002`

Agent-visible input is bounded and contains no tenant identifier. Shop identity, entitlement and language are trusted runtime context.

## Consistency and Transactions

### Plan materialisation

Admin catalogue mutation must copy MerchantPricingPlanFeature configuration into BillingPlanFeature configuration using the existing ARCH-017 materialisation transaction rules.

### Pending category selection

Persisting the pending category/template snapshot is a normal PostgreSQL transaction before external Shopify navigation. It is not activated in that transaction.

### Initial profile activation

Background profile reconciliation creates/activates the initial Shop prompt and promotes pending->active category within one database transaction after verifying an `ACTIVE`/`TRIALING` subscription projection.

### Later category publication

Admin publication of the pending category-generated Shop prompt and promotion of pending->active category occur in one transaction.

### Knowledge ingestion

The requested source revision is committed before queue publication. Queue publication is best effort. Background reconciliation repairs missing/stale work using the existing Moda reconciliation pattern; no new transactional outbox is introduced.

Revision content/chunks/vector writes and active-revision promotion must be atomic enough that lookup never observes a revision as active before its chunks are complete.

### Duplicate jobs

All Background jobs are idempotent by durable target identity. Reprocessing an already terminal/current revision is a no-op or deterministic reconciliation, not duplicate durable content.

## Ordering

No global ordering is required.

Knowledge processing is ordered only by source revision identity/current active promotion. A later source revision must not be overwritten by a stale earlier job.

Store profile processing is scoped by shop profile. V1 does not attempt to solve simultaneous multi-tab category editing beyond normal last-committed pending selection plus idempotent reconciliation.

## Failure Handling

### Translation

- provider failures retain draft/unavailable state;
- incomplete translation sets remain unavailable;
- retries use existing translation-provider/reconciliation behaviour;
- old edit-version translations remain historical but cannot satisfy a newer source version.

### Category onboarding

- leaving Shopify without selecting a plan leaves only pending profile state;
- missed/failed billing callback is repaired by existing subscription reconciliation;
- profile activation is retried until the active subscription projection and pending profile can be reconciled;
- `onboardingCompleted` alone never activates the category.

### Knowledge fetch

- DNS/SSRF failure -> revision `FAILED`;
- unsupported content type -> `FAILED`;
- timeout/oversize -> `FAILED`;
- embedding/provider failure -> `FAILED` or retryable according to provider classification;
- prior active revision remains active on replacement failure.

### Lookup

Lookup fails closed when:

- current feature entitlement is missing/invalid;
- no supported shop language can be resolved beyond English fallback;
- embedding configuration does not match stored active revision metadata; or
- pgvector/database access fails.

Failure does not expand tool authority or cause another capability to execute.

## Scalability

Merchant Knowledge is not on the raw Shopify webhook hot path.

### Ingestion workload

Ingestion volume is merchant-configuration driven and low relative to the platform's event-ingress workload. Work is asynchronous and horizontally scalable through Background workers.

### Vector workload

A reasonable planning shape is:

```text
~300 content units/chunk
~6 chunks for a full 1500-unit locale source
```

At 3 logical entries and ~1.5 locale variants per active merchant:

```text
~27 chunks / merchant
100,000 chunks ~= 3,700 merchants at full planning utilisation
```

Actual utilisation is expected to vary and must be measured rather than assumed.

Even with hundreds of thousands of total chunks, one lookup first restricts by one shop, current plan entry count, purpose and active locale source. The candidate vector set is therefore typically tens of rows. Exact pgvector search is preferred until measured query rate/candidate size proves it insufficient.

### Database

Required capacity considerations:

- embedding storage size;
- Background write throughput during merchant refresh bursts;
- exact vector distance CPU after selective filters;
- index selectivity by shop/entry/source; and
- connection-pool impact from embedding/query workflows.

Redis vector indexing is explicitly deferred and may be introduced later as a rebuildable derived index if measured PostgreSQL latency/QPS requires it.

## Security

### Tenant isolation

`shopId` is never accepted from the LLM as a lookup argument. Commerce supplies the authenticated shop context.

Every lookup query constrains data by trusted same-shop ownership before vector ranking.

### SSRF

Background's source fetcher is a security boundary and must validate the original URL, DNS results and every redirect target before network access.

### Prompt injection

Trust follows origin, not language or apparent role labels inside text. Merchant page content is untrusted reference data even when it says `SYSTEM`, `developer`, `ignore previous instructions`, or equivalent text in another language.

### Tool authority

Tool execution remains determined only by the validated Commerce grant plus tool-specific validation. Merchant knowledge cannot grant or widen a tool.

### Secrets

Embedding/translation/provider credentials remain server-side. No source page receives Shopify, Meta, database, Redis or LLM credentials.

### Logs

Logs must not contain extracted page bodies, embeddings, access tokens or provider credentials. Prefer `shopId`, entry/source/revision ids, purpose, locale, bounded failure code and timing metadata.

## Observability

ARCH-023 reuses existing framework/OpenTelemetry/Prisma/BullMQ telemetry rather than duplicating generic request/queue metrics.

New domain-semantic structured logs are required at owning boundaries:

- pending profile selection/activation outcome;
- configuration translation target/version outcome;
- knowledge revision processing outcome;
- refresh/reconcile decision;
- lookup outcome count / bounded failure classification.

All generic logging uses:

`@modainteract/moda-interact-shared/logging`

No new standalone metrics are required for v1 unless implementation inspection shows a concrete gap not supplied by existing framework/BullMQ/HTTP instrumentation.

## Infrastructure Assessment

No new deployable service, route, database or Redis instance is required.

A bounded Gateway task is required because the existing Render Blueprint is the infrastructure source of truth, ARCH-023 adds a dedicated Merchant Knowledge Background worker entrypoint, and both that worker and Commerce need the same platform-wide `EMBEDDING_PROVIDER`, `EMBEDDING_MODEL`, `EMBEDDING_DIMENSIONS`, and `EMBEDDING_INDEX_VERSION`. `EMBEDDING_API_KEY` remains a server-side secret placeholder.

No embedding configuration is stored in PostgreSQL and no new public/private Commerce ingestion route or service is introduced.

## Rollout / Migration

Classification:

**PRE-PRODUCTION / BREAKING ROLLOUT for ARCH-023-only functionality**, while preserving existing ARCH-021 prompt data and existing billing behaviour.

Safe order:

1. DATABASE-001 feature configuration schema;
2. DATABASE-002 store-category/profile/localised prompt schema;
3. DATABASE-003 Merchant Knowledge + pgvector schema;
4. SHARED-001/002/003 implementations followed by SHARED-004 publication;
5. Admin/Shopify/Background/Commerce implementation tasks according to dependencies;
6. Gateway environment wiring;
7. operator creates/enables `merchant_knowledge` Feature and assigns validated per-plan configuration through Admin;
8. operator authors/publishes one FEATURE-bound `merchant_knowledge` Commerce capability/tool through the normal Commerce Studio lifecycle;
9. developer manually validates the integrated feature;
10. terminal ARCH-023 system-test tasks run;
11. architect performs final verification.

Existing Platform/Shop prompt rows are preserved. Commerce Studio Platform/Shop authoring UI is removed only after Admin authoring is available.

A future embedding-model change requires an explicit reprocessing/migration plan; do not silently mix active chunk embeddings from incompatible vector spaces.

## Decisions / Tasks

| Task | Owner | Status | Depends On |
|---|---|---|---|
| ARCH-023-DATABASE-001 | moda_database | Ready | - |
| ARCH-023-DATABASE-002 | moda_database | Ready | - |
| ARCH-023-DATABASE-003 | moda_database | Ready | - |
| ARCH-023-SHARED-001 | moda_shared | Ready | - |
| ARCH-023-SHARED-002 | moda_shared | Ready | - |
| ARCH-023-SHARED-003 | moda_shared | Ready | - |
| ARCH-023-SHARED-004 | moda_shared | Pending | SHARED-001, SHARED-002, SHARED-003 |
| ARCH-023-ADMIN-001 | moda_admin | Pending | DATABASE-002, SHARED-004 |
| ARCH-023-ADMIN-002 | moda_admin | Pending | ADMIN-001, DATABASE-002, SHARED-004 |
| ARCH-023-ADMIN-003 | moda_admin | Pending | DATABASE-002, SHARED-004 |
| ARCH-023-ADMIN-004 | moda_admin | Pending | DATABASE-001, SHARED-004 |
| ARCH-023-SHOPIFY-001 | moda_app | Pending | DATABASE-002, SHARED-004 |
| ARCH-023-SHOPIFY-002 | moda_app | Pending | SHOPIFY-001, DATABASE-002, SHARED-004 |
| ARCH-023-SHOPIFY-003 | moda_app | Pending | DATABASE-001, DATABASE-003, SHARED-004 |
| ARCH-023-SHOPIFY-004 | moda_app | Pending | SHOPIFY-003 |
| ARCH-023-BACKGROUND-001 | moda_background | Pending | DATABASE-002, SHARED-004 |
| ARCH-023-BACKGROUND-002 | moda_background | Pending | DATABASE-002, SHARED-004 |
| ARCH-023-BACKGROUND-003 | moda_background | Pending | DATABASE-001, DATABASE-003, SHARED-004 |
| ARCH-023-BACKGROUND-004 | moda_background | Pending | BACKGROUND-003, SHARED-004 |
| ARCH-023-COMMERCE-001 | moda_commerce | Pending | DATABASE-002, SHARED-004 |
| ARCH-023-COMMERCE-002 | moda_commerce | Pending | DATABASE-001, DATABASE-003, SHARED-004 |
| ARCH-023-COMMERCE-003 | moda_commerce | Pending | ADMIN-003, COMMERCE-001 |
| ARCH-023-GATEWAY-001 | moda_gateway | Pending | BACKGROUND-003, BACKGROUND-004, COMMERCE-002 |
| ARCH-023-SYSTEM-TEST-001 | moda_system_test | Pending | DATABASE-002, SHARED-004, ADMIN-001/002/003, SHOPIFY-001/002, BACKGROUND-001/002, COMMERCE-001/003 |
| ARCH-023-SYSTEM-TEST-002 | moda_system_test | Pending | DATABASE-001/003, SHARED-004, ADMIN-004, SHOPIFY-003/004, BACKGROUND-003/004, COMMERCE-001/002, GATEWAY-001 |

Ready initial frontier: DATABASE-001/002/003 and SHARED-001/002/003. These definitions are portable and are not materialised/claimed by this review patch.

System-test tasks are terminal. No implementation/publication/infrastructure task depends on a system-test task.

## Open Questions

None blocking task definition.

The following are intentionally implementation-tuned rather than architecture blockers:

- exact network timeout/byte bounds for public-page fetching, provided they remain bounded and tested;
- exact deployment values for the single multilingual `EMBEDDING_*` model/provider configuration, provided Background and Commerce receive the same vector-space identity and stored provenance matches; and
- exact similarity-result count/threshold tuning, provided results remain bounded and tenant/entitlement filters occur before semantic ranking.

## Change History

### 2026-09-27

- Created ARCH-023 from the Merchant Knowledge architecture session.
- Chose PostgreSQL + pgvector over Redis vector search for v1 because per-shop candidate sets are small and PostgreSQL is already the durable source of truth.
- Removed the previously considered Background -> private Commerce ingestion endpoint; Background writes processed knowledge directly to PostgreSQL and Commerce only reads it at runtime.
- Locked logical Knowledge Entry limits, language-neutral content units, shop-language configuration selection, customer-language-independent responses, all-20 translation gating, merchant-initiated refresh and pending category activation after durable Shopify subscription projection.
- Kept one platform-wide embedding model in deployment environment configuration rather than adding a database model catalogue; persisted vector provenance/index version remains mandatory.
