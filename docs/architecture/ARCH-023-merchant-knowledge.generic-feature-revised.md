---
id: ARCH-023
title: Merchant knowledge, store profiles and localized CommerceAgent instructions
status: proposed
coordinator: moda_architect
created: 2026-09-28
updated: 2026-09-28
---

# ARCH-023: Merchant knowledge, store profiles and localized CommerceAgent instructions

## Status

Proposed for review. This Patch 1 document defines the architecture and exact target
contracts only. It does not create implementation task files, task branches, claims,
worktrees or repository changes outside `docs/architecture/`.

ARCH-023 extends the existing dynamic Feature/BillingPlan model, ARCH-005 language
foundation and ARCH-021 CommerceAgent configuration/capability foundation. Where this
document conflicts with ARCH-021 prompt-composition semantics, the narrower ARCH-023
decisions below are authoritative for the target state described here.

## Problem

Moda merchants can currently enable plan-backed features and configure recovery
behaviour, while Commerce capabilities determine which tools the CommerceAgent may
execute. The platform does not yet provide a durable, plan-limited way for a merchant
to supply factual information from public company/help/policy/product pages for use by
the agent.

The missing capability must solve several separate concerns without conflating them:

1. **Commercial entitlement** — a pricing plan must limit how much Merchant Knowledge a
   shop may configure.
2. **Merchant configuration** — the merchant needs to create logical knowledge entries,
   attach public URLs and trigger refreshes from the existing Shopify application UI.
3. **Asynchronous ingestion** — page fetching, SSRF protection, extraction, content
   limiting, chunking and embedding must not occur in the browser or request lifecycle.
4. **Semantic retrieval** — the CommerceAgent needs bounded, tenant-scoped retrieval of
   relevant passages during a conversation.
5. **Instruction safety** — merchant/customer/web/tool content is untrusted data and
   must never expand tool authority or override higher-trust instructions.
6. **Store identity** — merchants select a store category which seeds a default Shop
   Instruction prompt from an Admin-managed template library.
7. **Internationalisation** — store configuration language and customer conversation
   language are independent. Shop configuration/knowledge selection uses the shop
   language; the final reply uses the customer conversation language.
8. **Prompt ownership** — platform/shop behavioural instructions belong in the Admin
   application; capability-local operational instructions and tool contracts belong in
   Commerce Studio.

## Goals

- Add `merchant_knowledge` as an ordinary Feature using the existing `ALWAYS_ENABLED` activation mode. Application/domain plan policy includes it by default on every merchant pricing plan; the database schema does not make this Feature structurally special or required.
- Represent plan limits as generic plan-feature configuration rather than hard-coded
  Free/Starter checks.
- Limit Merchant Knowledge by **logical knowledge entries**, not physical URLs.
- Allow one logical entry to have one source per supported Moda language.
- Use deterministic language-neutral **content units**, not word counts.
- Store extracted source text durably in PostgreSQL.
- Store semantic chunk embeddings in PostgreSQL using pgvector.
- Keep Redis/BullMQ as queue/reconciliation infrastructure; do not make Redis the
  Merchant Knowledge source of truth or vector index in v1.
- Process Merchant Knowledge asynchronously in `moda-interact-background` and write the
  resulting durable state directly to PostgreSQL.
- Create exactly one global, FEATURE-bound `merchant_knowledge` Commerce capability.
- Give that capability one MCP-visible tool named `merchant_knowledge_lookup`, backed by the Commerce-internal policy operation `merchantKnowledge.lookup`.
- Ensure merchant configuration creates **knowledge data**, never new Commerce
  capabilities/releases.
- Add initial Store Category selection to the **existing Shopify onboarding page**.
- Preserve the existing `/app/billing/select` -> Shopify Managed Pricing navigation.
- Persist the selected category before leaving Moda, but do not activate it until the
  durable subscription projection is `ACTIVE` or `TRIALING`.
- Add later Store Profile and Merchant Knowledge management as sections on the
  **existing Recovery Settings page**.
- Make each Store Category have exactly one explicit default prompt template.
- Translate each current template edit into all 20 supported Moda languages before the
  template can be selected for new shops.
- Resolve the template/knowledge language from `ShopSettings.defaultLanguageTag`, with
  English fallback.
- Keep customer conversation language independent and use it only for the generated
  customer response.
- Make Platform Instructions and Shop Instructions additive.
- Keep the immutable security/protocol kernel code-owned and non-editable.
- Use the existing reconciliation pattern to recover durable PENDING knowledge work
  when queue publication or worker execution is interrupted.
- Allow any public HTTPS URL that passes the ingestion security policy; do not require
  the URL to share the Shopify storefront domain.
- Make refresh merchant-initiated in v1; do not introduce automatic crawling.

## Non-Goals

ARCH-023 does not introduce:

- a new public or private Commerce ingestion HTTP endpoint;
- one Commerce capability per merchant URL or per knowledge entry;
- a Redis vector index;
- a new database or object-storage service;
- a headless browser/JavaScript-rendering crawler;
- arbitrary merchant-authored prompt instructions attached to URLs;
- automatic scheduled webpage refreshes;
- customer-language selection of Shop Instructions or knowledge sources;
- per-shop embedding-model selection;
- an Admin UI for selecting embedding models;
- a generic capability-dependency graph;
- automatic execution of business actions merely because merchant knowledge says an
  action should occur;
- background jobs whose purpose is to create merchant-specific Commerce capabilities;
- a second Shopify onboarding wizard or a separate Merchant Knowledge settings page.
- a merchant-facing enable/disable toggle for the baseline Merchant Knowledge feature.

## Current Architecture

### Existing merchant feature/billing model

The current database already provides:

- `Feature` with `FeatureActivationMode` and `systemRequired`;
- `MerchantPricingPlanFeature` for pricing-catalogue feature membership;
- `BillingPlanFeature` for materialised runtime plan-feature membership;
- `ShopFeaturePreference` for merchant opt-in state on optional features; ARCH-023 does not use `ShopFeaturePreference` to enable or disable `merchant_knowledge`;
- `Subscription.status` using `SubscriptionProjectionStatus` including `ACTIVE` and
  `TRIALING`.

`BillingPlanFeature` and `MerchantPricingPlanFeature` do not currently carry generic
feature-specific configuration.

### Existing Shopify language and UI surfaces

`ShopSettings.defaultLanguageTag` already stores the merchant/shop language context.
The Shopify application already supports 20 merchant UI locales:

```text
zh-Hans, zh-Hant, cs, da, nl, en, fi, fr, de, it,
ja, ko, nb, pl, pt-BR, pt-PT, es, sv, th, tr
```

The existing onboarding component is:

```text
moda-interact/app/components/onboarding/Onboarding.jsx
```

and its current plan CTAs navigate to:

```text
/app/billing/select
```

which redirects to Shopify Managed Pricing.

The existing merchant configuration surface is the Recovery Settings route/view and
already renders `FeaturePreferences` followed by recovery configuration. ARCH-023 adds
Store Profile and Merchant Knowledge sections to this page; it does not create new
merchant navigation.

### Existing Commerce configuration

The current Commerce database already contains:

- `CommercePromptTemplateCategory`;
- `CommercePromptTemplate` with mutable current `promptText` and `editVersion`;
- `CommerceAgentPrompt` scoped `PLATFORM` or `SHOP`;
- immutable `CommerceAgentPromptRevision` records;
- `CommerceAgentConfiguration` with platform/shop active prompt pointers;
- `CommerceCapability`, `CommerceCapabilityRevision`, releases and grants;
- FEATURE-bound capability selection through feature facts.

ARCH-021 simplification intentionally removed a separate prompt-template revision table.
ARCH-023 preserves that simplification: template history needed for localized selection
is represented by immutable translation snapshots keyed by template `editVersion`, not
by reintroducing `CommercePromptTemplateRevision`.

### Existing asynchronous infrastructure

Moda already uses BullMQ and reconciliation patterns for durable work that is persisted
before queue publication. ARCH-023 reuses that pattern. PostgreSQL remains the durable
source of truth and BullMQ delivery is treated as at-least-once/retryable rather than
exactly-once.

### pgvector availability

The development PostgreSQL instance has been verified to load the `vector` extension
and execute vector-distance queries successfully. ARCH-023 therefore targets pgvector
for Merchant Knowledge semantic retrieval.

## Core Architectural Decisions

### D1 — Feature, Capability and Knowledge are different concepts

```text
FEATURE
    commercial entitlement / generic plan feature
        |
        v
CAPABILITY
    agent behaviour + executable tool authority
        |
        v
KNOWLEDGE
    shop-scoped factual reference material
```

The platform creates one ordinary Feature using the existing generic Feature model:

```text
key:            merchant_knowledge
displayName:    Merchant Knowledge
active:         true
activationMode: ALWAYS_ENABLED
systemRequired: false
```

`merchant_knowledge` is **not** a database-required Feature. The database schema, migrations and constraints MUST NOT contain a `merchant_knowledge`-specific rule requiring a pricing plan or billing plan to contain it.

Application/domain plan policy is responsible for the product rule that every merchant pricing plan includes `merchant_knowledge` by default. The supported pricing-plan create/update workflow must add or retain one enabled `MerchantPricingPlanFeature` mapping for this Feature before the plan can be made available. This is code-level validation keyed by the stable Feature key, not a database invariant.

`BillingPlan` materialisation remains generic: it copies the already-approved `MerchantPricingPlanFeature` rows and their configuration without a `merchant_knowledge`-specific branch. Because the Feature uses the existing `ALWAYS_ENABLED` activation mode, the normal generic feature resolver does not require a `ShopFeaturePreference` row for it. `systemRequired` remains `false`.

Commerce Studio creates one global FEATURE-bound capability with key:

```text
merchant_knowledge
```

and that capability exposes exactly one MCP-visible tool:

```text
merchant_knowledge_lookup
```

The tool is backed internally by the Commerce policy operation:

```text
merchantKnowledge.lookup
```

`merchant_knowledge_lookup` is the ToolDefinition/MCP name. `merchantKnowledge.lookup` is
an internal Commerce execution identifier and is never emitted by MCP `tools/list`.

Merchant actions create/update/delete knowledge rows only. They do not create or
publish Commerce capabilities, capability revisions or releases.

A merchant whose plan contains the Feature but has no configured knowledge entries still has
the capability available; the lookup returns no matches. Providing the first knowledge entry
requires no separate feature-toggle transition.

Knowledge may inform an otherwise-authorised capability. Knowledge must never:

- enable a Feature;
- select a Capability;
- add a tool;
- expand a conversation grant;
- authorise an action;
- change tenant identity;
- override platform/shop/capability instructions.

### D2 — plan limits apply to logical knowledge entries

A plan does not count physical URLs. It limits logical entries such as:

```text
Customer Support
Returns & Refunds
Shipping & Delivery
About the Company
```

One entry may have localized source variants, for example:

```text
Customer Support
    fr -> https://example.fr/aide
    en -> https://example.com/help
```

Both localized URLs consume one logical-entry slot. Product policy makes Merchant Knowledge
available on every plan by ensuring the ordinary Feature mapping is included during plan
authoring. Plan configuration changes the allowance, not the Feature model itself.

The Merchant Knowledge feature configuration is exactly:

```json
{
  "schemaVersion": 1,
  "maxKnowledgeEntries": 5,
  "maxContentUnitsPerLocaleSource": 1500
}
```

The values are plan data, not application constants. `1500` content units is the
initial recommended per-locale-source allowance; individual plans may configure a
different positive value.

### D3 — content units are deterministic and language-neutral

One content unit is four normalized Unicode code points:

```text
contentUnits = ceil(normalizedCodePointCount / 4)
```

The canonical normalization algorithm is:

1. normalize Unicode using NFC;
2. convert CRLF and CR line endings to LF;
3. replace Unicode White_Space characters other than LF with U+0020 SPACE;
4. collapse consecutive U+0020 SPACE characters to one SPACE;
5. remove SPACE immediately before or after LF;
6. collapse three or more consecutive LF characters to exactly two LF characters;
7. trim leading/trailing SPACE and LF;
8. count Unicode code points using code-point iteration, not UTF-16 code units.

If normalized content exceeds the configured allowance, Background truncates it to:

```text
maxContentUnitsPerLocaleSource * 4
```

Unicode code points before chunking and records `truncated = true`. It does not fail
an otherwise-valid page solely because it is longer than the plan allowance.

### D4 — store language and customer language are independent

`ShopSettings.defaultLanguageTag` controls:

- which localized category template is used to seed Shop Instructions;
- which Merchant Knowledge source locale is preferred at runtime.

The current customer's resolved conversation language controls only the generated
customer-facing response.

Example:

```text
shop default language = fr
Shop Instructions      = French localized template text
Merchant Knowledge     = French source text
customer language      = English
customer reply         = English
```

Changing customer language must not change feature entitlement, tool authority,
knowledge source selection, Shop Instructions or security semantics.

### D5 — supported configuration locales are the existing 20 Moda locales

ARCH-023 uses exactly this ordered set:

```text
zh-Hans, zh-Hant, cs, da, nl, en, fi, fr, de, it,
ja, ko, nb, pl, pt-BR, pt-PT, es, sv, th, tr
```

A shared locale resolver maps `ShopSettings.defaultLanguageTag` to one of those values:

1. canonicalize the BCP-47 tag;
2. use an exact supported tag when present;
3. otherwise use the unique supported tag with the same primary language;
4. Portuguese uses region-specific `pt-BR`/`pt-PT`; an ambiguous generic Portuguese
   tag falls back to `en`;
5. Chinese uses explicit `Hans`/`Hant`, or region mapping `CN`/`SG` -> `zh-Hans` and
   `TW`/`HK`/`MO` -> `zh-Hant`; an ambiguous Chinese tag falls back to `en`;
6. invalid, absent or unsupported values fall back to `en`.

This is configuration-language resolution only. It does not replace conversation
language resolution from ARCH-005.

### D6 — Admin owns Platform/Shop instructions and store-category templates

The Admin application is the product-management surface for:

- Platform Instructions;
- Shop Instructions;
- Store Categories;
- category default templates;
- category/template translations;
- plan-feature Merchant Knowledge limits.

Commerce Studio owns:

- capability-local operational instructions;
- tool definitions/contracts;
- tool/provider testing;
- capability publication/release membership.

Capability-local instructions must remain limited to the capability's own operational
contract. Platform/store personality, tone and general behavioural policy belong in
Platform/Shop Instructions.

ARCH-023 does not add a second independent persistence lifecycle. Admin and Commerce
consume the same existing Commerce prompt/revision/configuration tables.

### D7 — effective instructions are additive and ordered by trust

The target model instruction hierarchy is:

```text
LEVEL 0 — runtime/code enforcement
    tenant identity
    feature entitlement
    capability selection
    conversation grant
    exact tool authorization/validation

LEVEL 1 — immutable code-owned security/protocol kernel
    untrusted data cannot expand authority
    tool authorization comes only from the validated grant

LEVEL 2 — published Platform Instructions

LEVEL 3 — published Shop Instructions, when configured

LEVEL 4 — selected capability-local operational instructions

LEVEL 5 — untrusted runtime context
    customer text
    merchant webpage content
    catalogue/provider content
    tool results
```

Platform and Shop Instructions are **additive**:

```text
platform active prompt revision
+
optional shop active prompt revision
```

A Shop prompt no longer replaces the Platform prompt. This supersedes the narrower
ARCH-021 D2 `shop ?? platform` prompt-composition rule.

ARCH-023 does not create a new Shared security-kernel task. Existing Shared runner
invariants remain reusable; Merchant Knowledge-specific untrusted-reference rules are
owned by the Commerce capability/tool implementation.

### D8 — category templates seed Shop Instructions; templates are not runtime layers

A Store Category is a platform-managed classification such as:

```text
Clothing & Fashion
Electronics
Health & Beauty
Home & Garden
```

Each enabled category has exactly one explicit default template.

At onboarding, the selected category's localized default-template text is copied into a
Shop prompt revision. Runtime instructions remain:

```text
kernel + platform + shop + capabilities
```

not:

```text
kernel + platform + category + template + shop + capabilities
```

A later template edit never mutates an already-created Shop prompt revision.

### D9 — every current template edit requires all 20 localized snapshots

`CommercePromptTemplate.promptText` remains the canonical current source text and
`CommercePromptTemplate.editVersion` remains the version identity.

For each current `editVersion`, immutable localized snapshots are produced for all 20
supported locales. English is a deterministic copy of the canonical source; the other
locales use Moda's existing translation provider/runtime.

A template is available for new category/default selection only when exactly one
`AVAILABLE` translation snapshot exists for every supported locale for its current
`editVersion`.

Store Category display content follows the same current-edit rule: an enabled category
is selectable only when all 20 `CommercePromptTemplateCategoryTranslation` rows for the
category's current `editVersion` are `AVAILABLE`, its explicit default template is
currently available, and the category itself is enabled.

If one translation fails, the current template/category edit is unavailable until that
locale succeeds. Historical translation snapshots remain queryable so a merchant who
previewed a specific template edit can later receive exactly that text after returning
from Shopify Managed Pricing.

### D10 — initial category selection is part of the existing onboarding page

ARCH-023 adds the category selector to:

```text
moda-interact/app/components/onboarding/Onboarding.jsx
```

It does not add another onboarding route.

When no pending selection exists, Shopify product taxonomy signals are mapped to an
enabled Moda Store Category and the deterministic best match is pre-selected. The
merchant can change the selection before continuing.

All existing plan CTAs continue to lead to `/app/billing/select`, but the onboarding
submission must first persist the pending Store Category and exact localized template
snapshot the merchant previewed.

If the merchant leaves Shopify Managed Pricing without choosing a plan, that pending
selection remains inactive and is restored when onboarding is resumed.

### D11 — Shopify subscription projection is the category activation boundary

Pending Store Category state becomes active only when the durable `Subscription`
projection for the shop has:

```text
status IN (ACTIVE, TRIALING)
```

`ShopSettings.onboardingCompleted` is not an activation authority.

Initial activation performs one transaction that:

1. verifies the pending category and pinned translation snapshot still exist;
2. verifies the subscription projection is `ACTIVE` or `TRIALING`;
3. resolves/creates the shop's `CommerceAgentPrompt` lineage with scope `SHOP`;
4. creates a new immutable `CommerceAgentPromptRevision` whose `promptText` is the
   pinned localized template snapshot;
5. records template provenance;
6. publishes that initial revision immediately;
7. sets the shop `CommerceAgentConfiguration.activePromptRevisionId` to that revision
   and increments its prompt CAS version;
8. moves `pendingCategoryId` to `activeCategoryId`;
9. clears the pending selection fields.

The normal billing callback may perform the happy path, but existing billing
reconciliation must perform the same idempotent activation if the callback/redirect is
missed.

### D12 — later category changes never overwrite active Shop Instructions silently

After onboarding, Store Category is managed from the Store Profile section on the
existing Recovery Settings page.

A later category change:

1. writes new pending category/template-selection state;
2. creates a DRAFT Shop prompt revision copied from the pinned localized default
   template snapshot;
3. leaves the current active category and current published Shop prompt unchanged;
4. exposes the draft to Admin for review/edit/publication;
5. promotes `pendingCategoryId` to `activeCategoryId` only when that exact draft (or an
   Admin-edited descendant representing the same pending category change) is published;
6. clears pending category state after publication.

### D13 — Merchant Knowledge UI lives on the existing Recovery Settings page

The existing Recovery Settings page gains two sections:

```text
Conversation features
    existing FeaturePreferences remain unchanged
    Merchant Knowledge is not rendered as an editable FeaturePreferences checkbox

Store Profile
    active Store Category
    default assistant/template provenance
    change-category action

Merchant Knowledge
    plan allowance
    ordered logical entries
    localized URLs
    status
    content-unit usage
    last refreshed timestamp
    Refresh / Edit / Delete actions

Existing recovery-specific settings
```

No separate Merchant Knowledge settings navigation is introduced in v1.

### D14 — ingestion is Background-owned and writes PostgreSQL directly

The ingestion path is:

```text
Shopify application
    persist Entry/Source/Revision(PENDING)
        |
        v
BullMQ merchant-knowledge job
        |
        v
moda-interact-background worker
    validate current generation + entitlement
    fetch public URL safely
    extract/normalize/truncate
    chunk
    create embeddings
    persist chunks/pgvector
    promote revision ACTIVE
```

There is no Background -> Commerce ingestion HTTP call.

Background already has access to the shared PostgreSQL database and is the owner of
asynchronous business workflows. A network hop to Commerce would add failure and
authentication boundaries without adding authority or persistence ownership.

### D15 — refresh and URL replacement are revisioned

Each localized source has a monotonically increasing `currentGeneration`.

Creating a source, changing its URL or pressing Refresh creates a new PENDING revision
with that generation. The existing ACTIVE revision remains active while the new
revision is PENDING/PROCESSING.

On success, one database transaction:

1. changes the old ACTIVE revision to `SUPERSEDED`;
2. changes the new revision to `ACTIVE`;
3. deletes semantic chunks belonging to the superseded revision;
4. leaves the superseded revision's normalized content/metadata for audit/history.

On failure, the new revision becomes `FAILED`; the previous ACTIVE revision and chunks
remain unchanged.

A worker must not promote a revision if its `generation` is no longer equal to its
source's `currentGeneration`.

### D16 — public HTTPS sources are allowed subject to SSRF policy

A knowledge source may live on the Shopify storefront, a corporate domain or a third-
party public help/documentation host.

The fetcher must enforce all of the following:

- scheme exactly `https:`;
- no URL userinfo credentials;
- maximum URL length 2048 characters;
- at most 5 redirects;
- validate the initial destination and every redirect destination;
- reject loopback, private, link-local, multicast, unspecified and reserved IPv4/IPv6
  destinations;
- reject cloud metadata/link-local targets including `169.254.169.254`;
- reject a hostname if any resolved address is non-public;
- prevent DNS-rebinding bypass by binding the validated resolution to the outbound
  connection or validating the actual connected peer address;
- do not send merchant/browser cookies or credentials;
- overall fetch timeout 10 seconds;
- maximum decompressed response body 1 MiB;
- accept only `text/html` and `text/plain` media types;
- do not execute page JavaScript;
- do not follow `<iframe>`, `<script>`, CSS, image or other subresource URLs.

HTML extraction removes scripts, styles and markup while preserving human-visible text
order. The result then passes through D3 normalization.

### D17 — chunking and embedding are deterministic platform configuration

After D3 truncation, Background splits normalized content into deterministic overlapping
code-point windows:

```text
target chunk size: 1200 code points
overlap:           200 code points
```

The final chunk may be shorter. Empty chunks are not stored. Chunk `ordinal` starts at
0 and increments by one.

The whole platform uses one multilingual embedding model configured through server-side
environment variables:

```text
EMBEDDING_PROVIDER
EMBEDDING_MODEL
EMBEDDING_DIMENSIONS
EMBEDDING_INDEX_VERSION
EMBEDDING_API_KEY
```

`EMBEDDING_MODEL` must support all 20 Moda languages. Background embeds document chunks;
Commerce embeds lookup queries. Both must use identical provider/model/dimensions/index
version.

The embedding model is not database-configurable and has no Admin UI in ARCH-023.

### D18 — PostgreSQL/pgvector is the vector store

PostgreSQL remains authoritative for entries, sources, revisions, normalized content,
chunks and embeddings.

V1 does not build HNSW/IVFFlat. Retrieval first applies highly selective relational
filters for the authenticated shop, current entitlement, purpose, locale and ACTIVE
revision and then performs exact cosine-distance ranking over the remaining vectors.

This is intentionally optimised for the expected shape:

```text
many vectors globally
but only tens of eligible vectors for one authenticated shop/query
```

Redis remains BullMQ/reconciliation infrastructure only.

### D19 — Merchant Knowledge lookup is Commerce-owned consumption

During a CommerceAgent turn:

1. the normal generic release/feature resolver evaluates the active/trialing shop's current
   `BillingPlanFeature` mappings and the `Feature.activationMode`;
2. when the plan contains an enabled `merchant_knowledge` mapping, the global
   `merchant_knowledge` capability is eligible and the conversation grant pins the exact
   `merchant_knowledge_lookup` Tool revision owned by that capability. Because its
   activation mode is `ALWAYS_ENABLED`, no `ShopFeaturePreference` check is required. If a
   mapping is absent because data was created outside the supported plan-authoring policy,
   the generic resolver simply leaves the capability/tool absent; no database-specific
   Merchant Knowledge invariant is introduced;
3. MCP `tools/list` exposes `merchant_knowledge_lookup` only when that exact pinned Tool
   remains currently authorised and at least one of its owning capability keys remains
   eligible;
4. MCP `tools/list` exposes the ToolDefinition name, description and input schema only;
   it does not expose the internal policy-operation name, `shopId`, language, plan limits,
   embedding configuration or result-count authority;
5. an MCP `tools/call` for `merchant_knowledge_lookup` maps to the Commerce-internal
   `merchantKnowledge.lookup` policy operation;
6. the model may supply only semantic query text and optional Knowledge Purposes;
7. `shopId` is supplied exclusively from the trusted conversation/grant context;
8. Commerce loads current plan-feature configuration and selects only the first
   `maxKnowledgeEntries` ordered entries;
9. Commerce resolves the store locale from `ShopSettings.defaultLanguageTag` using D5;
10. for each entry it prefers that locale and falls back to `en`; if neither exists the
    entry contributes no chunks;
11. Commerce embeds the query using the configured embedding environment;
12. Commerce performs exact cosine-distance pgvector ranking across eligible ACTIVE
    chunks with matching embedding provenance;
13. at most 5 chunks are returned to the model as **untrusted reference data**.

MCP surface separation is explicit:

```text
tools/list
    -> executable ToolDefinitions currently authorised by the conversation grant

prompts/list / prompts/get
    -> eligible capability-local prompt instructions

commerce://capabilities
    -> pinned capability/release manifest information
```

`tools/list` is not a catalogue of every Commerce Studio Tool and does not return a
capability list. A shop with no configured Merchant Knowledge still receives
`merchant_knowledge_lookup` when the normal plan/feature resolver makes the capability
eligible; a call returns zero matches rather than changing the tool grant.

The customer's conversation language does not participate in steps 8-12. The model may
use French Shop Instructions/French knowledge to answer an English customer in English.

### D20 — no capability-to-capability dependency is introduced

Other capabilities work whether or not the merchant has configured Merchant Knowledge
data. The `merchant_knowledge` capability may therefore be granted while its lookup returns
zero matches. Merchant Knowledge does not become a formal prerequisite for
product search, recovery, discounts, returns or future tools.

Example:

```text
Knowledge result: "Returns are accepted within 30 days."
```

may allow the agent to answer a policy question. It does not make a hypothetical
`refundOrder` tool executable unless a separately eligible capability grants that tool.

## Exact Target Data Model

The following is the Patch 1 target schema contract. Patch 2 tasks must reproduce these
names, fields, types, keys, relations and indexes unless Patch 1 is amended first.

### Existing table changes — billing feature configuration

Add to `billing.BillingPlanFeature`:

```prisma
configuration Json @default("{}") @db.JsonB
```

Add to `billing.MerchantPricingPlanFeature`:

```prisma
configuration Json @default("{}") @db.JsonB
```

The two `configuration` columns are **generic plan-feature configuration**, not
Merchant Knowledge-specific database fields. The database stores JSON and MUST NOT inspect
its shape based on a Feature key. No Merchant Knowledge-specific entitlement table, check
constraint, trigger or required-feature constraint is introduced.

For Feature key `merchant_knowledge`, application/domain code validates the JSON with
`MerchantKnowledgeFeatureConfigurationV1` defined under Contracts before the pricing plan
can be made available. The plan-authoring domain policy also adds or retains the ordinary
`MerchantPricingPlanFeature` mapping for `merchant_knowledge` by default on every plan.
This default-inclusion rule is enforced in code, not in the database schema.

`BillingPlan` materialisation copies the generic plan-feature mappings and their
`configuration` JSON without semantic transformation and without a
`merchant_knowledge`-specific materialisation branch. ARCH-023 is pre-production and there
are no existing plans requiring compatibility backfill.

No Merchant Knowledge limit is read from plan display names or hard-coded plan kinds.

### Existing table changes — Store Category default template

Extend `commerce.CommercePromptTemplateCategory` with:

```prisma
defaultTemplateId String? @unique @db.Text
```

and a named relation to `CommercePromptTemplate`.

Database/application validation must enforce:

- an enabled category must have non-null `defaultTemplateId` before it is selectable;
- `defaultTemplateId` must reference a template whose `categoryId` equals this category;
- the referenced template must be enabled and currently available under the 20/20 rule
  before the category is offered for new merchant selection.

### Required existing-model relation fields

The Prisma implementation must add the corresponding reverse relation fields with the
following names so every relation in this document is deterministic:

```text
Shop.commerceShopProfile
Shop.merchantKnowledgeEntries

CommercePromptTemplateCategory.defaultTemplate
CommercePromptTemplateCategory.translations
CommercePromptTemplateCategory.taxonomyMappings
CommercePromptTemplateCategory.activeShopProfiles
CommercePromptTemplateCategory.pendingShopProfiles

CommercePromptTemplate.defaultForCategory
CommercePromptTemplate.translations

CommerceAgentPromptRevision.sourceTemplateTranslation
CommerceAgentPromptRevision.pendingForShopProfiles

CommercePromptTemplateTranslation.pendingForShopProfiles
```

The `defaultTemplate`/`defaultForCategory` relation name is:

```text
CommercePromptTemplateCategoryDefault
```

The active/pending profile-category relation names are exactly:

```text
CommerceShopProfileActiveCategory
CommerceShopProfilePendingCategory
```

### New enum — localized translation status

```prisma
enum CommerceLocalizedContentStatus {
  PENDING
  PROCESSING
  AVAILABLE
  FAILED

  @@schema("commerce")
}
```

### New table — `CommercePromptTemplateCategoryTranslation`

```prisma
model CommercePromptTemplateCategoryTranslation {
  id                String                         @id @default(cuid()) @db.Text
  categoryId        String                         @db.Text
  locale            String                         @db.VarChar(16)
  sourceEditVersion Int
  displayName       String                         @db.VarChar(255)
  description       String                         @default("") @db.Text
  status            CommerceLocalizedContentStatus @default(PENDING)
  failureCode       String?                        @db.VarChar(128)
  createdAt         DateTime                       @default(now()) @db.Timestamptz(3)
  updatedAt         DateTime                       @default(now()) @updatedAt @db.Timestamptz(3)

  category CommercePromptTemplateCategory @relation(fields: [categoryId], references: [id], onDelete: Cascade, onUpdate: Restrict)

  @@unique([categoryId, locale, sourceEditVersion])
  @@index([categoryId, sourceEditVersion, status])
  @@schema("commerce")
}
```

`locale` must be one of the 20 D5 values. Historical edit-version rows are immutable
once `AVAILABLE`; failed/pending rows for the same key may be retried/replaced according
to the translation workflow.

### New table — `CommercePromptTemplateTranslation`

```prisma
model CommercePromptTemplateTranslation {
  id                String                         @id @default(cuid()) @db.Text
  templateId        String                         @db.Text
  locale            String                         @db.VarChar(16)
  sourceEditVersion Int
  displayName       String                         @db.VarChar(255)
  description       String                         @default("") @db.Text
  promptText        String                         @db.Text
  status            CommerceLocalizedContentStatus @default(PENDING)
  contentHash       String?                        @db.VarChar(64)
  failureCode       String?                        @db.VarChar(128)
  createdAt         DateTime                       @default(now()) @db.Timestamptz(3)
  updatedAt         DateTime                       @default(now()) @updatedAt @db.Timestamptz(3)
  completedAt       DateTime?                      @db.Timestamptz(3)

  template CommercePromptTemplate @relation(fields: [templateId], references: [id], onDelete: Cascade, onUpdate: Restrict)

  @@unique([templateId, locale, sourceEditVersion])
  @@index([templateId, sourceEditVersion, status])
  @@schema("commerce")
}
```

For locale `en`, `displayName`, `description` and `promptText` are copied directly from
the canonical template edit and marked `AVAILABLE` without an external translation
call. For all other locales, translated fields are provider output.

`contentHash` is lowercase SHA-256 of the exact persisted UTF-8 `promptText` and is
required when `status=AVAILABLE`.

A template is **currently available** iff:

- `CommercePromptTemplate.enabled = true`; and
- for `sourceEditVersion = CommercePromptTemplate.editVersion`, there are exactly 20
  translation rows, exactly one per D5 locale; and
- every row has `status = AVAILABLE`.

### Existing table change — prompt provenance

Extend `commerce.CommerceAgentPromptRevision` with:

```prisma
sourceTemplateTranslationId String? @db.Text
```

and a nullable FK to `CommercePromptTemplateTranslation.id` using
`ON DELETE RESTRICT ON UPDATE RESTRICT`.

When a Shop prompt is seeded from a localized category template:

- existing `sourceTemplateId` stores the template id; and
- `sourceTemplateTranslationId` stores the exact immutable localized snapshot used.

### New table — Shopify taxonomy to Store Category mapping

```prisma
model CommerceStoreCategoryTaxonomyMapping {
  id                        String                         @id @default(cuid()) @db.Text
  categoryId                String                         @db.Text
  shopifyTaxonomyCategoryId String                         @unique @db.VarChar(255)
  weight                    Int                            @default(1)
  createdAt                 DateTime                       @default(now()) @db.Timestamptz(3)
  updatedAt                 DateTime                       @default(now()) @updatedAt @db.Timestamptz(3)

  category CommercePromptTemplateCategory @relation(fields: [categoryId], references: [id], onDelete: Cascade, onUpdate: Restrict)

  @@index([categoryId])
  @@schema("commerce")
}
```

`weight` must be a positive integer. Onboarding suggestion scores the merchant's
Shopify product taxonomy categories by summing mapping weights. Highest score wins;
ties are resolved by category `displayOrder ASC`, then category `id ASC`. If no mapping
matches, the first enabled/selectable category by the same ordering is pre-selected.
The merchant may always change the pre-selection.

### New table — `CommerceShopProfile`

```prisma
model CommerceShopProfile {
  id                           String    @id @default(cuid()) @db.Text
  shopId                       String    @unique @db.Text
  activeCategoryId             String?   @db.Text
  activeCategoryActivatedAt    DateTime? @db.Timestamptz(3)
  pendingCategoryId            String?   @db.Text
  pendingTemplateTranslationId String?   @db.Text
  pendingPromptRevisionId      String?   @db.Text
  pendingSelectionGeneration   Int       @default(0)
  pendingSelectedAt            DateTime? @db.Timestamptz(3)
  createdAt                    DateTime  @default(now()) @db.Timestamptz(3)
  updatedAt                    DateTime  @default(now()) @updatedAt @db.Timestamptz(3)

  shop                       Shop                                @relation(fields: [shopId], references: [id], onDelete: Cascade, onUpdate: Restrict)
  activeCategory             CommercePromptTemplateCategory?     @relation("CommerceShopProfileActiveCategory", fields: [activeCategoryId], references: [id], onDelete: Restrict, onUpdate: Restrict)
  pendingCategory            CommercePromptTemplateCategory?     @relation("CommerceShopProfilePendingCategory", fields: [pendingCategoryId], references: [id], onDelete: Restrict, onUpdate: Restrict)
  pendingTemplateTranslation CommercePromptTemplateTranslation?  @relation(fields: [pendingTemplateTranslationId], references: [id], onDelete: Restrict, onUpdate: Restrict)
  pendingPromptRevision      CommerceAgentPromptRevision?        @relation(fields: [pendingPromptRevisionId], references: [id], onDelete: Restrict, onUpdate: Restrict)

  @@index([activeCategoryId])
  @@index([pendingCategoryId])
  @@index([pendingTemplateTranslationId])
  @@index([pendingPromptRevisionId])
  @@schema("commerce")
}
```

Invariant checks must enforce:

- `pendingSelectionGeneration >= 0`;
- pending category/template fields are either all null (no pending selection) or refer
  to the same category through template -> category;
- `pendingPromptRevisionId`, when present, belongs to the same shop's SHOP prompt
  lineage;
- `activeCategoryActivatedAt` is non-null iff `activeCategoryId` is non-null.

### New enum — Merchant Knowledge purpose

```prisma
enum MerchantKnowledgePurpose {
  COMPANY_INFORMATION
  CUSTOMER_SUPPORT
  POLICIES
  FAQ
  PRODUCT_INFORMATION
  SHIPPING_AND_DELIVERY

  @@schema("commerce")
}
```

### New enum — Merchant Knowledge revision reason

```prisma
enum MerchantKnowledgeRevisionReason {
  CREATE
  URL_CHANGE
  REFRESH

  @@schema("commerce")
}
```

### New enum — Merchant Knowledge revision status

```prisma
enum MerchantKnowledgeRevisionStatus {
  PENDING
  PROCESSING
  ACTIVE
  FAILED
  SUPERSEDED

  @@schema("commerce")
}
```

### New table — `MerchantKnowledgeEntry`

```prisma
model MerchantKnowledgeEntry {
  id        String                   @id @default(cuid()) @db.Text
  shopId    String                   @db.Text
  name      String                   @db.VarChar(160)
  purpose   MerchantKnowledgePurpose
  position  Int
  createdAt DateTime                 @default(now()) @db.Timestamptz(3)
  updatedAt DateTime                 @default(now()) @updatedAt @db.Timestamptz(3)

  shop    Shop                      @relation(fields: [shopId], references: [id], onDelete: Cascade, onUpdate: Restrict)
  sources MerchantKnowledgeSource[]

  @@unique([shopId, position])
  @@index([shopId, purpose, position])
  @@schema("commerce")
}
```

`position` is zero-based and non-negative. Runtime entitlement selects entries by
`position ASC, id ASC` and takes the first `maxKnowledgeEntries`.

### New table — `MerchantKnowledgeSource`

```prisma
model MerchantKnowledgeSource {
  id                String   @id @default(cuid()) @db.Text
  entryId           String   @db.Text
  languageTag       String   @db.VarChar(16)
  currentGeneration Int      @default(0)
  createdAt         DateTime @default(now()) @db.Timestamptz(3)
  updatedAt         DateTime @default(now()) @updatedAt @db.Timestamptz(3)

  entry     MerchantKnowledgeEntry            @relation(fields: [entryId], references: [id], onDelete: Cascade, onUpdate: Restrict)
  revisions MerchantKnowledgeSourceRevision[]

  @@unique([entryId, languageTag])
  @@index([languageTag])
  @@schema("commerce")
}
```

`languageTag` must be exactly one D5 supported locale. `currentGeneration` is
non-negative and increments by exactly one whenever CREATE/URL_CHANGE/REFRESH creates a
new revision for this source.

### New table — `MerchantKnowledgeSourceRevision`

```prisma
model MerchantKnowledgeSourceRevision {
  id                  String                          @id @default(cuid()) @db.Text
  sourceId            String                          @db.Text
  generation          Int
  reason              MerchantKnowledgeRevisionReason
  requestedUrl        String                          @db.VarChar(2048)
  resolvedUrl         String?                         @db.VarChar(2048)
  status              MerchantKnowledgeRevisionStatus @default(PENDING)
  contentType         String?                         @db.VarChar(128)
  httpStatus          Int?
  normalizedContent   String?                         @db.Text
  contentUnits        Int?
  contentHash         String?                         @db.VarChar(64)
  truncated           Boolean                         @default(false)
  failureCode         String?                         @db.VarChar(128)
  requestedAt         DateTime                        @default(now()) @db.Timestamptz(3)
  processingStartedAt DateTime?                       @db.Timestamptz(3)
  fetchedAt           DateTime?                       @db.Timestamptz(3)
  completedAt         DateTime?                       @db.Timestamptz(3)
  createdAt           DateTime                        @default(now()) @db.Timestamptz(3)
  updatedAt           DateTime                        @default(now()) @updatedAt @db.Timestamptz(3)

  source MerchantKnowledgeSource  @relation(fields: [sourceId], references: [id], onDelete: Cascade, onUpdate: Restrict)
  chunks MerchantKnowledgeChunk[]

  @@unique([sourceId, generation])
  @@index([sourceId, status, generation])
  @@index([status, requestedAt])
  @@schema("commerce")
}
```

The migration must add a PostgreSQL partial unique index enforcing at most one ACTIVE
revision per source:

```sql
CREATE UNIQUE INDEX "MerchantKnowledgeSourceRevision_one_active_per_source"
ON "commerce"."MerchantKnowledgeSourceRevision" ("sourceId")
WHERE "status" = 'ACTIVE';
```

`contentUnits` and `contentHash` are required for ACTIVE/SUPERSEDED revisions.
`contentHash` is lowercase SHA-256 of exact UTF-8 normalized/truncated content.

### New table — `MerchantKnowledgeChunk`

Prisma target:

```prisma
model MerchantKnowledgeChunk {
  id                    String   @id @default(cuid()) @db.Text
  revisionId            String   @db.Text
  ordinal               Int
  content               String   @db.Text
  contentUnits          Int
  contentHash           String   @db.VarChar(64)
  embedding             Unsupported("vector")
  embeddingProvider     String   @db.VarChar(64)
  embeddingModel        String   @db.VarChar(255)
  embeddingDimensions   Int
  embeddingIndexVersion String   @db.VarChar(64)
  createdAt             DateTime @default(now()) @db.Timestamptz(3)

  revision MerchantKnowledgeSourceRevision @relation(fields: [revisionId], references: [id], onDelete: Cascade, onUpdate: Restrict)

  @@unique([revisionId, ordinal])
  @@index([revisionId, ordinal])
  @@index([embeddingIndexVersion, embeddingDimensions])
  @@schema("commerce")
}
```

The migration must execute:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

and add checks equivalent to:

```text
ordinal >= 0
contentUnits > 0
embeddingDimensions > 0
vector_dims(embedding) = embeddingDimensions
contentHash matches ^[0-9a-f]{64}$
```

No pgvector ANN index is created in v1.

## Contracts

Only contracts used by more than one application repository belong in
`@modainteract/moda-interact-shared` for ARCH-023. Commerce-only trust/kernel/tool
implementation does not receive a Shared task merely because it is security-related.

### C1 — supported configuration locales

Owner: `moda-interact-shared`

Export target: `@modainteract/moda-interact-shared/internationalization`

```ts
export const MODA_SUPPORTED_LANGUAGE_TAGS = [
  "zh-Hans", "zh-Hant", "cs", "da", "nl", "en", "fi", "fr", "de", "it",
  "ja", "ko", "nb", "pl", "pt-BR", "pt-PT", "es", "sv", "th", "tr",
] as const;
```

Shared also owns `resolveModaConfigurationLocale(input: string | null | undefined)`
with the exact D5 algorithm because Shopify, Admin, Background and Commerce must make
the same choice.

### C2 — Merchant Knowledge feature configuration

Owner: `moda-interact-shared`

Consumers: `moda-interact-admin`, `moda-interact`, `moda-interact-background`,
`moda-interact-commerce`.

```ts
export const MERCHANT_KNOWLEDGE_FEATURE_CONFIGURATION_SCHEMA_VERSION = 1 as const;

export const MerchantKnowledgeFeatureConfigurationSchema = z.object({
  schemaVersion: z.literal(1),
  maxKnowledgeEntries: z.number().int().min(1).max(100),
  maxContentUnitsPerLocaleSource: z.number().int().min(1).max(25000),
}).strict();
```

No downstream consumer may redefine this shape locally.

### C3 — Merchant Knowledge purpose

Owner: `moda-interact-shared`

Consumers: Shopify, Background, Commerce.

```ts
export const MERCHANT_KNOWLEDGE_PURPOSES = [
  "COMPANY_INFORMATION",
  "CUSTOMER_SUPPORT",
  "POLICIES",
  "FAQ",
  "PRODUCT_INFORMATION",
  "SHIPPING_AND_DELIVERY",
] as const;
```

The Shared Zod enum and TypeScript type must exactly match the database enum names.

### C4 — Merchant Knowledge processing queue

Owner: `moda-interact-shared`

Producer: `moda-interact`

Consumer: `moda-interact-background`

```ts
export const MERCHANT_KNOWLEDGE_QUEUE_NAME = "merchant-knowledge" as const;
export const MERCHANT_KNOWLEDGE_PROCESS_JOB_NAME = "process-source-revision" as const;
export const MERCHANT_KNOWLEDGE_PROCESS_SCHEMA_VERSION = 1 as const;

export const MerchantKnowledgeProcessSourceRevisionJobSchema = z.object({
  schemaVersion: z.literal(1),
  shopId: z.string().trim().min(1).max(128),
  sourceRevisionId: z.string().trim().min(1).max(128),
  generation: z.number().int().positive(),
  requestedAt: z.iso.datetime({ offset: true }),
}).strict();
```

The deterministic BullMQ job id is:

```text
merchant-knowledge-process-
+ sha256(shopId + U+001F + sourceRevisionId + U+001F + generation)
```

encoded as lowercase hexadecimal after the prefix.

There is no Shared `create-capability` Merchant Knowledge job. Capability creation and
publication remain Commerce Studio operations.

Background-only reconciliation jobs/contracts remain Background-owned unless a later
producer in another repository is introduced.

### C5 — configuration translation queue

Template/category authoring occurs in Admin while translation provider execution occurs
in Background, so this boundary is Shared.

Owner: `moda-interact-shared`

Producer: `moda-interact-admin`

Consumer: `moda-interact-background`

```ts
export const COMMERCE_CONFIGURATION_QUEUE_NAME = "commerce-configuration" as const;
export const COMMERCE_PROMPT_TEMPLATE_TRANSLATION_JOB_NAME = "translate-prompt-template" as const;
export const COMMERCE_CATEGORY_TRANSLATION_JOB_NAME = "translate-prompt-template-category" as const;
export const COMMERCE_CONFIGURATION_TRANSLATION_SCHEMA_VERSION = 1 as const;
```

Template payload:

```ts
z.object({
  schemaVersion: z.literal(1),
  templateId: z.string().trim().min(1).max(128),
  sourceEditVersion: z.number().int().positive(),
  requestedByAdminId: z.string().trim().min(1).max(128),
  requestedAt: z.iso.datetime({ offset: true }),
}).strict()
```

Category payload:

```ts
z.object({
  schemaVersion: z.literal(1),
  categoryId: z.string().trim().min(1).max(128),
  sourceEditVersion: z.number().int().positive(),
  requestedByAdminId: z.string().trim().min(1).max(128),
  requestedAt: z.iso.datetime({ offset: true }),
}).strict()
```

Job ids use the same SHA-256/U+001F convention with prefixes:

```text
commerce-template-translation-
commerce-category-translation-
```

and inputs `(id, sourceEditVersion)`.

Background may reuse the existing translation provider/batching primitives internally,
but the Admin/Background runtime boundary is this contract rather than support-message-
specific translation payloads.

### C6 — `merchant_knowledge_lookup` MCP tool / `merchantKnowledge.lookup` policy contract

This contract is Commerce-owned, not Shared, because it does not cross an application
boundary.

The exact MCP-visible Tool name is:

```text
merchant_knowledge_lookup
```

The exact internal Commerce policy-operation identifier is:

```text
merchantKnowledge.lookup
```

The published ToolDefinition must use `name = "merchant_knowledge_lookup"`. Its
`POLICY_OPERATION` execution must use `operation = "merchantKnowledge.lookup"` and
`operationVersion = "1.0.0"`. The existing Commerce Tool name rules therefore apply to
the MCP-visible underscore-delimited name, while the dotted name remains an internal
policy-operation identifier.

Agent input:

```ts
{
  query: string;              // trimmed, 1..1000 Unicode code points
  purposes?: MerchantKnowledgePurpose[]; // unique, max 6
}
```

The exact MCP input schema is:

```json
{
  "type": "object",
  "properties": {
    "query": {
      "type": "string",
      "minLength": 1,
      "maxLength": 1000
    },
    "purposes": {
      "type": "array",
      "uniqueItems": true,
      "maxItems": 6,
      "items": {
        "type": "string",
        "enum": [
          "COMPANY_INFORMATION",
          "CUSTOMER_SUPPORT",
          "POLICIES",
          "FAQ",
          "PRODUCT_INFORMATION",
          "SHIPPING_AND_DELIVERY"
        ]
      }
    }
  },
  "required": ["query"],
  "additionalProperties": false
}
```

The policy-operation argument mapping is exactly:

```text
query    <- agent input query
purposes <- agent input purposes, omitted when absent
```

The model cannot supply `shopId`, language, plan limits, embedding model/version or
result count.

Trusted runtime inputs are:

```text
shopId                 <- conversation grant/context
current BillingPlan    <- subscription projection
feature configuration  <- BillingPlanFeature.configuration
shop language          <- ShopSettings.defaultLanguageTag
embedding provenance   <- server environment
```

Maximum tool result: 5 chunks.

Each returned match has exactly:

```ts
{
  entryId: string;
  sourceRevisionId: string;
  purpose: MerchantKnowledgePurpose;
  languageTag: ModaSupportedLanguageTag;
  sourceUrl: string;
  chunkOrdinal: number;
  content: string;
}
```

Vector distance is used for ranking but is not exposed as authority or permission and
need not be returned to the model.

## Request / Event Flows

### Flow A — first onboarding category selection

```text
Existing Onboarding page
    |
    +--> load pending CommerceShopProfile selection if present
    |        else compute Shopify-taxonomy suggestion
    |
    +--> pre-select category; merchant may change it
    |
    +--> resolve category.defaultTemplate
    |
    +--> resolve shop configuration locale from ShopSettings.defaultLanguageTag
    |
    +--> display exact AVAILABLE CommercePromptTemplateTranslation snapshot
    |
    +--> merchant clicks existing plan CTA
              |
              v
        persist pendingCategoryId + pendingTemplateTranslationId
        increment pendingSelectionGeneration
              |
              v
        existing /app/billing/select
              |
              v
        Shopify Managed Pricing
```

No category/prompt becomes active at this point.

### Flow B — initial plan activation

```text
Shopify plan selection
    |
    v
normal subscription sync/reconciliation
    |
    v
Subscription.status = ACTIVE or TRIALING
    |
    v
idempotent pending CommerceShopProfile activation transaction
    |
    +--> create/publish initial SHOP prompt revision from pinned translation
    +--> set SHOP CommerceAgentConfiguration.activePromptRevisionId
    +--> set activeCategoryId
    +--> clear pending fields
```

### Flow C — later category change

```text
Recovery Settings -> Store Profile
    |
    v
merchant selects new category
    |
    v
persist pending category + pinned localized template snapshot
    |
    v
create DRAFT Shop prompt revision
    |
    v
current active category/prompt continue unchanged
    |
    v
Admin reviews/edits/publishes pending Shop Instructions
    |
    v
promote pending category to active
```

### Flow D — create or refresh Merchant Knowledge

```text
Recovery Settings -> Merchant Knowledge
    |
    v
validate feature entitlement + logical-entry limit
    |
    v
transaction:
  increment source.currentGeneration
  insert PENDING source revision
    |
    v
best-effort BullMQ process-source-revision enqueue
    |
    +--> success: normal Background processing
    |
    +--> failure: durable PENDING state remains
                  and reconciliation re-enqueues later
```

### Flow E — Background source processing

```text
process-source-revision job
    |
    v
runtime-validate Shared payload
    |
    v
load source/revision/entry/shop/plan entitlement
    |
    +--> stale generation -> skip without mutation
    +--> no longer entitled -> fail/leave active predecessor intact
    |
    v
claim PENDING -> PROCESSING
    |
    v
secure public HTTPS fetch
    |
    v
extract + D3 normalize/truncate
    |
    v
D17 chunk
    |
    v
embed each chunk with platform embedding configuration
    |
    v
transaction:
  persist normalized revision metadata/content
  persist chunks/vectors/provenance
  re-check generation
  predecessor ACTIVE -> SUPERSEDED
  new revision -> ACTIVE
  delete predecessor chunks
```

### Flow F — conversation lookup

```text
conversation grant
    |
    v
normal capability selection
    |
    +--> merchant_knowledge mapping absent/disabled -> generic resolver leaves tool absent
    |
    +--> merchant_knowledge mapping present/enabled (normal application-created plan)
              |
              v
        merchant_knowledge_lookup granted
              |
              v
        agent submits query + optional purposes
              |
              v
        Commerce injects trusted shopId
              |
              v
        resolve current feature config + first N ordered entries
              |
              v
        resolve shop configuration locale; per entry locale -> en fallback
              |
              v
        embed query using current embedding provenance
              |
              v
        exact pgvector cosine ranking over eligible ACTIVE chunks
              |
              v
        <=5 untrusted reference chunks returned
              |
              v
        model answers using current customer conversation language
```

## Consistency and Transactions

### Knowledge configuration transaction

Creating/changing/refreshing a localized source must atomically:

1. lock/load the source row;
2. increment `currentGeneration` by one;
3. insert exactly one PENDING revision with the same generation;
4. commit before BullMQ publication.

Queue publication is outside the transaction. Reconciliation recovers committed
PENDING work that did not reach BullMQ.

### Knowledge processing promotion transaction

A worker may promote only when:

```text
revision.generation == source.currentGeneration
```

The final transaction re-checks this condition after embeddings are prepared. If it is
false, the new result is stale and must not replace the current ACTIVE revision.

### Prompt/category onboarding activation transaction

Initial category activation and initial Shop prompt publication are one logical database
transaction so the active category and active Shop Instructions cannot diverge.

### At-least-once processing

BullMQ jobs may be duplicated or retried. Job handlers must be idempotent by durable
revision/template edit identity. No design assumes exactly-once delivery.

## Ordering

- Merchant Knowledge entries are ordered by `(position ASC, id ASC)`.
- Source generations are strictly increasing per `(entry, languageTag)` source.
- Only the latest source generation may become ACTIVE.
- Category suggestion ties are resolved by `(displayOrder ASC, category.id ASC)`.
- Conversation messages retain the existing conversation-ordering architecture; ARCH-023
  does not introduce global serialization.

## Failure Handling

### URL fetch/extraction failure

The new revision becomes `FAILED` with bounded `failureCode`. Any prior ACTIVE revision
remains active and queryable.

### Embedding-provider failure

The new revision becomes/retries according to Background retry policy. It must not be
promoted without all chunks having embeddings matching the current configured
provenance.

### Embedding model/version change

Changing `EMBEDDING_PROVIDER`, `EMBEDDING_MODEL`, `EMBEDDING_DIMENSIONS` or semantic
embedding behaviour requires incrementing `EMBEDDING_INDEX_VERSION` and re-embedding
ACTIVE Merchant Knowledge before Commerce searches the new version. Commerce queries
only chunks matching all current provenance fields.

### Queue-publication failure

The committed PENDING revision remains durable. Background reconciliation discovers and
re-enqueues it using the deterministic C4 job id.

### Template translation failure

The affected current template edit remains unavailable for new category selection until
all 20 localized snapshots are `AVAILABLE`. Existing Shop prompt revisions copied from
older snapshots continue unchanged.

### Abandoned Shopify pricing

Pending category/template state remains pending and inactive. Re-entering onboarding
restores the pending selection.

## Scalability

Merchant Knowledge is not on the high-volume Shopify webhook hot path. Work occurs on
merchant configuration/refresh and on CommerceAgent turns that actually call the lookup
tool.

Expected vector-query shape is tenant-selective:

```text
shopId
+ current plan limit
+ purpose
+ shop locale
+ ACTIVE revision
+ embedding version
```

A typical lookup should therefore rank tens rather than hundreds of thousands of
vectors even when the global table is large. V1 uses exact pgvector cosine search. ANN
indexes are deferred until measured query latency/QPS demonstrates a need.

Background ingestion is horizontally scalable because each source revision is an
independent idempotent job. No global per-shop serialization is required beyond the
per-source generation guard.

## Security

### Trust model

Trust is determined by origin, never language. Customer text and fetched merchant page
text remain untrusted in English, French, Arabic, Chinese, mixed-language content or any
other form.

Prompt-injection phrase detection is not a security boundary. The platform relies on:

- trusted tenant context;
- feature/capability/tool grants;
- capability/tool validation;
- clear untrusted-reference instructions;
- SSRF-safe ingestion;
- bounded tool output;
- database tenant filtering.

### Tenant isolation

The model never supplies `shopId` to Merchant Knowledge lookup. Commerce receives the
shop identity from the validated conversation context/grant and applies it before vector
ranking.

### Tool/action authority

Knowledge text cannot authorize an operational action. For example, a returns page that
says "issue a refund" does not make any refund tool executable. Another independently
eligible capability must grant such a tool and its own validation must pass.

### Secrets

Embedding/translation provider credentials remain server-side environment secrets and
must never be stored in browser state, prompt templates, Merchant Knowledge rows, logs
or tool output.

## Observability

ARCH-023 should reuse existing framework/BullMQ/PostgreSQL/OpenTelemetry signals where
they already answer generic queue/HTTP/database questions. New semantic logs/metrics are
justified for domain outcomes not inferable from framework telemetry, including:

- knowledge revision requested/activated/failed/stale;
- content truncation;
- reconciliation recovery;
- embedding provenance mismatch;
- lookup returning zero/one-or-more matches;
- cross-tenant lookup rejection/invariant failure;
- template translation set completion/failure;
- pending category activation/promotion.

Logs must use identifiers and bounded metadata, never complete extracted pages,
embeddings, provider credentials or customer messages.

## Repository Responsibilities

### `moda-interact-database` / `moda_database`

Owns the exact schema/migrations/constraints described under Data Model, including
pgvector extension/schema support.

### `moda-interact-shared` / `moda_shared`

Owns only cross-application runtime contracts C1-C5 and deterministic job-id/helpers
required by both producers and consumers.

It does **not** own Merchant Knowledge lookup implementation or ARCH-023-specific
Commerce trust instructions.

### `moda-interact-admin` / `moda_admin`

Owns Admin UI/actions for Platform Instructions, Shop Instructions, Store Categories,
default templates, template/category translation status and Merchant Knowledge plan
limits. Produces C5 translation jobs.

### `moda-interact` / `moda_app`

Owns the merchant-facing onboarding category section, Recovery Settings Store Profile
and Merchant Knowledge sections, merchant CRUD/refresh actions, plan-limit checks and C4
processing-job publication. Merchant Knowledge has no merchant enable/disable preference.

### `moda-interact-background` / `moda_background`

Owns C4 consumption, reconciliation, URL fetching/security, extraction, normalization,
content-unit enforcement, deterministic chunking, document embeddings, vector writes and
revision state transitions. It also consumes C5 and reuses the existing translation
provider/runtime for category/template localization.

The target worker modules/entrypoints are fixed as:

```text
src/workers/merchant-knowledge.worker.ts
src/entrypoints/merchant-knowledge.ts
    queue: merchant-knowledge
    job:   process-source-revision

src/workers/commerce-configuration.worker.ts
src/entrypoints/commerce-configuration.ts
    queue: commerce-configuration
    jobs:  translate-prompt-template
           translate-prompt-template-category
```

`merchant-knowledge.worker.ts` is the only ARCH-023 worker that processes merchant
knowledge source revisions. It does not create Commerce capabilities.

There is no Background worker whose purpose is to add Commerce capabilities. The one
`merchant_knowledge` capability is authored/published through Commerce Studio before
merchant knowledge can be used.

### `moda-interact-commerce` / `moda_commerce`

Owns creation/publication of the one global `merchant_knowledge` capability with the
MCP-visible `merchant_knowledge_lookup` Tool backed by the internal
`merchantKnowledge.lookup` policy operation, additive platform/shop/capability instruction
composition, query embedding and exact pgvector retrieval.

### `moda-interact-gateway` / `moda_gateway`

Only required if deployment topology must add a dedicated Background worker process or
wire embedding environment/secrets to deployables that do not already receive them. No
new public/private HTTP service is required by the architecture itself.

### `moda-interact-system-test` / `moda_system_test`

Owns final integrated validation after all implementation/infrastructure dependencies
are Complete and after developer manual validation.

## Infrastructure Assessment

No new database, Redis cluster or web service is required.

Potential infrastructure work is limited to:

- ensure the deployed PostgreSQL database has pgvector available/enabled;
- ensure the Background process performing ingestion and Commerce runtime performing
  lookup receive the same embedding provider/model/dimensions/index-version settings;
- ensure both receive the appropriate server-only embedding credential;
- create a dedicated Merchant Knowledge worker deployment only if the current Background
  worker topology does not provide an appropriate independently scalable entrypoint.

The exact Gateway requirement is deferred until Patch 5 inspection of current deployed
worker/environment wiring. No Gateway task is created in Patch 1.

## Rollout / Migration

Rollout classification: **pre-production/breaking for the new Merchant Knowledge data
model**, while existing billing/prompt tables contain development state that must be
preserved by additive migrations.

Required order will be finalized after task review, but architectural dependency order
is:

```text
database schema + shared cross-app contracts
        |
        +--> Admin configuration authoring/translation
        +--> Shopify onboarding/settings producers
        +--> Background ingestion/translation consumers
        +--> Commerce lookup/capability runtime
        |
        v
infrastructure wiring if required
        |
        v
developer manual validation
        |
        v
terminal system tests
```

Existing Shop/Subscription/Prompt/Capability data must not be destroyed.

## Decisions / Tasks

No implementation tasks are created by Patch 1.

After this architecture is reviewed and amended/Agreed, Patch 2 will define only the
Database and Shared tasks against the exact Data Model and Contracts above. Later
patches will separately define Admin/Shopify, Background/Commerce and final
infrastructure/system-test work.

## Open Questions

None are required to review Patch 1's target behaviour. Implementation details may be
amended during Patch 1 review before task files are created.

## Change History

### 2026-09-28 — Patch 1 proposed architecture

- Created ARCH-023 as a separate initiative from ARCH-021/ARCH-022.
- Chose PostgreSQL + pgvector rather than Redis vectors for v1.
- Chose logical knowledge-entry limits and deterministic content units.
- Made Background the ingestion owner with direct PostgreSQL writes.
- Kept a single global Merchant Knowledge Commerce capability.
- Kept `merchant_knowledge` as an ordinary Feature (`ALWAYS_ENABLED`,
  `systemRequired=false`); application/domain plan policy includes it by default on every
  merchant pricing plan, with no database-level required-feature invariant.
- Defined `merchant_knowledge_lookup` as the MCP-visible Tool name and
  `merchantKnowledge.lookup` as its Commerce-internal policy operation.
- Defined MCP `tools/list` as the current conversation-grant tool surface, separate from
  capability prompts and `commerce://capabilities`.
- Added Store Category/default-template onboarding on the existing onboarding page.
- Added Store Profile and Merchant Knowledge to the existing Recovery Settings page.
- Made Platform + Shop Instructions additive and Admin-managed.
- Kept capability-local tool instructions Commerce-owned.
- Defined shop-language/template/knowledge resolution independently from customer reply
  language.
- Defined exact target tables, keys, indexes and cross-application contracts for review
  before implementation-task creation.
