# ARCH-058: Product discovery and recommendation contracts

Status: proposed implementation contract; task definitions only, 4 November 2026.

Parent: [ARCH-058 architecture](../ARCH-058-commerce-agent-product-discovery.md). This file is normative for the eight ARCH-058 tasks. The source-grounded revision 03 review remains supporting evidence; this contract resolves its open implementation choices. No runtime implementation, package publication, import, or deployment has been performed by creating this document.

## 1. Ownership and compatibility

Use the existing `@modainteract/moda-interact-shared/commerce` and `/commerce/runner` entrypoints. SHARED-001 owns structural schemas, exported descriptor constants, equality helpers and the runner changes required by the new built-in descriptor branch. SHARED-002 publishes that accepted implementation separately. MCP owns database/provider reads and authorization. Commerce owns authored system definitions, immutable release publication and the operator wrapper. Background owns purchase applicability and the final customer-facing composition. Database owns forward schema/policy migration. Admin implementation is outside the change.

Package target is **4.0.0**, conditional on the actual accepted source and registry baseline remaining **3.1.0**. Runtime runner target is **1.1.0**; new product-discovery releases require `>=1.1.0 <2.0.0`. Existing `commerce.v1` result envelopes remain. This is a coordinated pre-production update: deploy compatible consumers before activation and use fresh test conversations/grants. If either version is already occupied or the baseline has changed, reconcile the actual version with the architect before publishing; never overwrite an immutable package or guess another version. The task dependency is the recorded exact published version, not an unverified local checkout.

New transport validation is structural: strict keys, types, lengths, enumerations and size bounds. Cross-field policy belongs in service functions, not new Zod refinements/transforms. Existing schema refinements unrelated to this work are not to be removed. Retain the existing result byte limits, deadlines and terminal error/referral rules.

## 2. Standard product tools

All three tools belong to the existing `product_search` feature, which becomes active, `ALWAYS_ENABLED` and `systemRequired`. They are available to each otherwise authorized CommerceAgent store with an active eligible plan mapping, including Free plans and future stores. This does not bypass tenant, connection, plan status, turn, release or grant checks. No merchant preference is required. No new feature or manually authored Studio definition is needed.

| Name | Definition version | Execution operation | Operation version |
| --- | --- | --- | --- |
| `commerce_resolve_product_categories` | `1.0.0` | `taxonomy.resolveCategories` | `1.0.0` |
| `commerce_search_products` | `2.0.0` | `products.search` | `1.0.0` |
| `commerce_get_product` | retain existing `1.0.0` | `products.get` | retain existing `1.0.0` |

Published descriptors must pass the **actual** existing bounded subset validator after projection. Zod JSON Schema literals/enums are not automatically valid subsets: normalize string `const` to a single-item `enum`, and give fixed string literals/enums an explicit finite `maxLength` (the longest allowed value is sufficient), while preserving required keys, nullability and all declared bounds. Keep existing `$schema`/default stripping and supported nullable normalization. Either construct the exact bounded owned subset or narrowly extend the existing authoring projector; do not admit arbitrary `const`/`oneOf` keywords or create another general schema engine. Tests must start from the actual Shared schemas and the actual Commerce projection/publication route, including `category.system`, recommendation version/scope/promotion kind and nullable IDs.

The get-product definition remains unchanged if its existing schema/description/template are byte-identical. If implementation requires changing that immutable content, explicitly reconcile a new definition version before publication. A definition and an execution operation have independent version identities. Register the resolver in the same trusted system policy operation path as the existing product reads; adding it only to an authoring schema is insufficient.

### 2.1 Category resolution

Add `CommerceCategoryCandidateSchema`, `CommerceCategoryResolutionSchema` and inferred types, and matching dictionary entries in `CommerceToolInputs`/`CommerceToolOutputs`.

Input is exactly `{query: string(1..200), limit?: integer(1..10)}`; parsed default limit is 5. Trusted request context supplies environment and tenant. The client cannot supply a database name, vector, embedding model, source URL, SQL or shop ID.

Successful output is one of:

```typescript
type CategoryResolution = {
  outcome: "CANDIDATES" | "NO_CANDIDATES";
  generationId: string; // 1..128
  source: "SHOPIFY_STANDARD_PRODUCT_TAXONOMY";
  taxonomyVersion: string; // 1..64
  languageTag: string; // 1..35; corpus language, not promised query language
  candidates: Array<{
    categoryId: string; // original provider ID, 1..128
    name: string; // 1..512
    fullName: string; // full path, 1..4096
    parentId: string | null; // 1..128 when present
    level: number; // integer 0..32
    ancestorIds: string[]; // max 32, original IDs
    distance: number; // finite cosine distance, 0..2, lower is nearer
  }>; // max 10, and no more than requested limit
} | {
  outcome: "UNAVAILABLE";
  reasonCode: "NOT_READY" | "TEMPORARY_UNAVAILABLE";
};
```

Service invariants: `CANDIDATES` has at least one item; `NO_CANDIDATES` has none; every item belongs to the pinned complete generation; results sort by distance then category ID. Distance is a ranking value, not a probability or a claim of stock. Do not invent a universal confidence cutoff. A broad or ambiguous request may justify a clarification. The corpus stores reference meaning, never merchant inventory.

`NOT_READY` is limited to an absent active complete corpus or unavailable required embedding configuration. `TEMPORARY_UNAVAILABLE` is limited to classified operational database/embedding timeouts or transient unavailability after the request is authorized. These are `status: "OK"` result data; the host may continue with merchant text search. Wrong credentials, tenant denial, stale turn/grant, malformed vectors, an invalid model/configuration tuple, invalid SQL, unexpected exceptions and malformed output remain typed outer errors under the existing runner semantics. Preserve and log original errors using Shared logging.

### 2.2 Merchant product search

Extend only the search input. Preserve existing maximum-price, available-only, limit and cursor contracts/defaults. `query` becomes optional/nullable with parsed default `null`; a non-null query remains 1..200 characters. Add optional `category`:

```typescript
{
  system: "SHOPIFY_STANDARD_PRODUCT_TAXONOMY" | "WOOCOMMERCE_PRODUCT_CATEGORY";
  id: string; // 1..128
  taxonomyVersion: string | null; // 1..64 when non-null
}
```

Use this flat object because the existing published JSON Schema subset does not support `oneOf`. Service policy rejects a request with neither query nor category, a category incompatible with the authorized connection, invalid native IDs, a missing/mismatched Shopify taxonomy version, or a non-null Woo taxonomy version. Shopify IDs must be canonical taxonomy GIDs validated against the active pinned reference version before deriving the provider's short filter token. Woo IDs must be positive decimal strings and are scoped to the current shop. Never treat Shopify IDs, labels, product types or broad `Shop.activeCategoryId` as Woo native category IDs.

The first increment requests **exact assigned category membership**. There is no descendant flag or automatic parent expansion. For Shopify, use the documented pinned Admin API `products` category filter and verify `Product.category.id`; do not assume the variants search supports that filter. For Woo, the REST category query can include children, so exact membership requires a bounded check against returned `categories[].id`. Preserve true provider variant IDs, including null for a Woo simple product. Variant pagination within category-filtered Shopify products cannot silently drop later variants.

The existing opaque cursor must bind the authorized shop/connection, provider branch, normalized query/category/version, price/availability filters and both product and variant progress where needed. A filter or shop change invalidates it. Bounded scanning can return an empty page with a continuation cursor. `truncated` and exhaustion must be truthful. Fetching a small top-k taxonomy result or product page does not justify an unbounded underlying scan.

Search and exact product reads retain their existing output shapes. Add trustworthy currency/context only through existing declared product/context fields. Unknown currency stays unknown; shop base currency is not proof of a customer-market price. Product identity, price, availability, URL and discounts must come from the current shop's actual reads, not from the taxonomy. No product mirror is added.

## 3. Canonical discounts and optional lookup degradation

Retain `commerce_get_discount_options` and `commerce_get_discount_details`, their existing inputs, normal success objects, canonical `CommerceOfferSchema` and `CommerceDiscountDetailsSchema` from ARCH-052. Do not add a second discount engine or substitute `commerce_evaluate_discount`.

Extend each output dictionary member with this alternative strict object:

```typescript
{ outcome: "UNAVAILABLE", reasonCode: "TEMPORARY_UNAVAILABLE" }
```

Export `CommerceOptionalLookupUnavailableSchema` and its inferred type. This object is structurally disjoint from the existing normal success objects, which have `offers` or `details` and no `outcome`. It appears inside the existing `status: "OK"` envelope only for a classified temporary failure of an optional conversational discount read. It has no fabricated offers, mode, cursor or condition facts. Existing normal success objects remain canonical and need no compatibility adapter. The initial-outreach producer retains its current hard-failure behavior; any compile-time narrowing needed in a shared consumer must explicitly handle the new branch conservatively.

Keep authorization, stale turn/grant, malformed arguments/provider facts and unexpected exceptions as outer errors. An outer `ERROR` still requires the runner's normal referral; a later successful lookup cannot clear that state. Do not convert every error into an empty successful list.

Current merchant policy is checked for every discovery/detail call and again before a claim. `NONE` means no discount lookup or promotional claim. `FIXED` uses the current permitted selection/override. `AI_BEST_APPLICABLE` considers the canonical permitted catalogue independently of the merchant-selection checkbox. Unknown or incomplete condition facts are not a supported promotion. `details: null` means no details for that currently permitted ID; it does not prove a saving.

## 4. Built-in tool identity and retained grants

Discount tools remain code-defined built-ins; the three product tools remain published system capabilities. Do not fabricate database tool/revision/capability identities for built-ins, grant everything returned by `tools/list`, or publish duplicate discount definitions in Studio.

Add `CommerceBuiltInToolDescriptorSchema` and inferred type:

```typescript
{
  kind: "BUILT_IN";
  name: "commerce_get_discount_options" | "commerce_get_discount_details";
  definitionVersion: "1.0.0";
  contractHash: string; // lowercase SHA256
  description: string; // 1..4096
  inputSchema: SubsetSchema;
}
```

Export the two canonical `commerceDiscountBuiltInDescriptors` from Shared. Use these exact descriptions:

- `commerce_get_discount_options`: `Read the current shop's permitted discount options.`
- `commerce_get_discount_details`: `Read details for a permitted discount in the current shop.`

Compute `contractHash` from existing canonical JSON over `{name, definitionVersion, description, inputSchema, outputSchema}`. Use the bounded input subset and canonical generated JSON schema for the exact Shared output member. Hashing occurs in the existing trusted Node adapter/publication path; the portable contract does not introduce a Node-only import into browser entrypoints. Export `commerceBuiltInToolContractPayload` as a pure canonical-payload helper and accept an injected digest where necessary. Exported descriptor hashes are generated from that canonical payload as reviewed constants, verified by Node tests against the actual schemas; no caller-controlled hash or runtime Node import is required to read the portable constants. Verify the exported descriptors and compiled schemas agree; a hash asserted by MCP alone is not authority.

`CommerceManifestSchema` gains `builtInTools`, an array of these descriptors, max 2 and default `[]` for producers that do not project built-ins. Extend the existing `grantedTools` array union with `CommerceBuiltInToolGrantSchema`:

```typescript
{
  kind: "BUILT_IN";
  toolName: "commerce_get_discount_options" | "commerce_get_discount_details";
  definitionVersion: "1.0.0";
  contractHash: string;
}
```

The existing published grant shape remains unchanged. Existing PostgreSQL JSON storage retains both branches; no grant table column is needed. DATABASE-001 must nevertheless update the existing database JSON-shape guard and insert trigger in a new forward migration: they currently allow only published grants and compare the whole array with the published release union. Partition that comparison, preserve all published-release and row-identity invariants, and restrict the built-in branch to the exact allowlisted structural shape below. Runtime Shared/MCP/Background independently authenticate its exact canonical hash and current permission; a structurally valid database row alone does not grant a tool. Published grants still equal the selected published-capability union with their sorted provenance keys. Built-in grants equal the descriptor set by name/version/hash. The combined list has at most32 entries with unique names; duplicate, collision, missing and unexpected branches are invalid. Structural parsing and separate service validation together enforce this without adding business refinements to the new leaf schemas.

Update manifest/grant equality, deduplication, runner tool descriptors, preflight/registration/authorization, MCP projection/execution, Background persistence/list checking, and the existing Commerce preview adapter as required. Every switch must deliberately distinguish the branches. The model only sees the usual MCP `{name, description, inputSchema}` listing; the host matches it exactly to an authorized pinned descriptor before execution.

### 4.1 Trusted conversation adapter context

Add `CommerceConversationToolContextSchema` and `CommerceConversationToolContext`:

```typescript
{
  purpose: "CONVERSATION";
  conversationId: string; // existing ID bound
  inboundVersion: number; // positive integer
  grantId: string | null; // existing ID bound; null only for initial resolution
}
```

Background's existing `encodeCommerceContext` validates its normal turn assertion, then attaches this bounded object under the existing opaque `toolContext` header field. Use null grant ID during initial manifest resolution and the real retained ID thereafter. Do not encode a fake outreach attempt or permit model arguments to set the context. Existing initial-outreach context remains unchanged.

Generic MCP transport authentication remains opaque and continues to rely on private ingress. Its domain capability/discount adapter validates this context, checks conversation ownership and current inbound version/processing lease, and, when a grant ID is present, reads `commerceConversationGrant` to verify shop, conversation, expiry, runner and release identity before using its retained built-in set. Source that set from the database, not caller-supplied descriptors/hashes. A malformed context or mismatch is a hard error. An absent context represents the existing generic shop caller; it does not enable conversational discount built-ins or optional conversation degradation. No new grant schema column or generic authentication protocol is introduced.

Conversation resolution grants only allowlisted discount built-ins when current policy permits them. Later calls re-check current policy, store and connection. Re-project a retained grant's descriptor set for equality without widening it; current policy can remove a tool from availability or deny its execution without silently editing the retained grant. A conversation first granted under `NONE` does not gain discount permission merely because a later turn sees a policy change; establish a fresh conversation under the documented pre-production transition. Code-contract drift, unknown built-ins, hash changes and stale grants fail closed. Outreach's current separate context remains supported and never receives a fabricated conversation grant.

## 5. Recommendation selection and host composition

Export `CommerceProductRecommendationSelectionSchema` and its inferred type. Add these optional owned fields to the release response contract's existing `detailsSchema`:

```typescript
{
  productRecommendationVersion: "1";
  productRecommendations: Array<{
    scope: "PRODUCT_ONLY" | "ADD_TO_BASKET" | "REPLACE_BASKET_LINE";
    basketLineId: string | null; // 1..128 when present
    productId: string; // 1..128
    variantId: string | null; // 1..128 when present
    quantity: number; // integer 1..99
    promotionKind: "NONE" | "NATIVE_SALE" | "DISCOUNT";
    offerIds: string[]; // max 3, each1..128
  }>; // min1,max 3; each is an independent alternative
}
```

The exported schema represents the owned selection fields, not unrelated release details. Service validation requires both fields together and validates each relation: `PRODUCT_ONLY`/`ADD_TO_BASKET` have null `basketLineId`; `REPLACE_BASKET_LINE` identifies one observed current basket line. `NONE`/`NATIVE_SALE` have no discount offer IDs; `DISCOUNT` has one to three observed IDs. Each alternative is evaluated as its own proposed purchase, never combined with the other alternatives. An explicit proposed quantity is required. A product-only one-unit example is permitted when clearly presented as hypothetical; it is not a claim about the customer's actual basket or quantity. An unknown basket or quantity cannot be guessed to satisfy a threshold.

This flat structure requires details nesting depth 5 because the existing validator counts the root as1 and each `offerIds` string as5. Increase only the details maximum from 4 to 5; keep input depth 3 and all existing property, array and result-size bounds. Permit the same bounded nullable scalar syntax already used by input schemas in the details subset. This one-level extension avoids a separate cross-referenced offer-selection array. Do not add general `oneOf`, increase any other bound, or replace unrelated response fields. Never include model-supplied prices, currencies, calculated savings, promotional prose or invented `evidenceIds` in this selection.

The host records trusted tool observations for the current turn, keyed by authorized descriptor/revision or built-in hash, arguments and current shop. Validate selected product/variant/offer IDs against those observations. Missing selections or free-text-only promotion must not bypass this path. When the turn is producing a product recommendation, the full customer-facing recommendation is composed by trusted host code from validated product data and permitted facts, including a no-promotion product branch. Do not concatenate unvalidated model monetary claims to a validated card.

Re-read selected exact products and canonical discount facts in the existing host finalization phase with reserved call/deadline budget, current policy and current-turn checks before/after awaits. Reject changes to identity, price currency, availability, applicability or authorization. For `NONE`, use only a grounded product description/current price if known. For `NATIVE_SALE`, require provider-native sale evidence and permitting policy. For `DISCOUNT`, check exact proposed purchase, condition completeness, status, dates, targeting/exclusions, quantities, currency-aware subtotal thresholds, sale/customer/usage restrictions and supported reciprocal combination policy. Unsupported eligibility is not advertised as applicable. Do not manufacture an outreach attempt ID or legacy CommerceEvidence record; reuse pure validation arithmetic/policy through a conversation adapter.

A supported offer is a claim about observed current facts, not guaranteed redemption or a provider-atomic cart price. Do not calculate a guaranteed multi-discount total unless the existing canonical rules establish it. After current host finalization, the existing processor language/wrapper/moderation/send stages remain in control; no new last-moment processor hook or worker rewrite is included. Preserve admission, takeover, stale-turn and delivery behavior. Use the current conversation language and Shared localization/formatting; all new fixed customer-facing strings require the existing 20 supported locales.

## 6. Taxonomy storage and import lifecycle

DATABASE-001 is authoritative for exact Prisma fields, SQL names, checks, indexes and foreign keys. Use `commerce.ReferenceTaxonomyGeneration` and `commerce.ReferenceTaxonomyCategory`, with `Unsupported("vector")`, dimension checks and complete-generation activation. Corpus identity is environment/source/language. A generation pins source bytes/version/checksum, embedding provider/model/dimensions/indexVersion, deterministic embedding-text version and import fingerprint. No taxonomy rows contain merchant inventory.

MCP owns `src/data/reference-taxonomy-manifest.json` and a local parser for the approved pinned Shopify `2026-08` English distribution. Obtain and review the real source SHA256 and actual count at implementation; neither is present in the uploaded corpus manifest. Never insert guessed IDs/checksums/counts. Validate every imported record against the public category wire bounds as well as database constraints before activation; do not silently truncate IDs, hierarchy paths or labels to make output validation pass. Optional `--source` reads local bytes only if they match that trusted manifest. The runtime CLI has no arbitrary `--manifest` or source-URL override. Tests may inject a known fixture manifest/transport into the same parser/service through a test harness, guarded as test-only, without a production validation bypass.

### 6.1 Embedding text and import identity

Freeze `embeddingTextVersion` to `"1"`. For each validated source category, embed exactly `Category: ${name}\nPath: ${fullName}` in UTF-8 with a single literal newline between the two lines and no trailing newline. Use parsed source labels/full paths unchanged after the source parser's documented boundary-whitespace handling; do not generate synonyms, append merchant facts or silently translate labels. Query embedding uses the validated query trimmed at its outer boundary, with no prompt/instruction suffix. Reject a whitespace-only query in the service before an embedding call.

Compute `importFingerprint` as lowercase SHA256 of existing canonical JSON for exactly `{environment, source, taxonomyVersion, languageTag, sourceSha256, embeddingProvider, embeddingModel, embeddingDimensions, embeddingIndexVersion, embeddingTextVersion}`. Use the validated uppercase database environment enum and the exact stored source/configuration scalar values; `sourceSha256` is the checksum of the approved distribution bytes, including compression if the manifest pins a compressed asset. Credentials, editVersion, source download mirror, generated row IDs and timestamps do not participate. Credential rotation alone does not invalidate vectors; a changed embedding tuple or text version does. Record the embedding tuple as stored provenance, not a caller-controlled override.

Read the existing environment `REFERENCE_TAXONOMY` embedding configuration and credential envelope using the correct purpose in the database lookup and AAD. Do not modify it, substitute the merchant-knowledge purpose, rotate keys, or rebuild Admin's Redis index. The same configuration may be read-only shared with Admin. If required credentials/configuration are absent, report the unmet prerequisite.

Prepare bounded source parsing and embeddings outside the database transaction. In the bounded final activation transaction, take a corpus advisory lock, compare the active baseline, lock the selected embedding-configuration row `FOR SHARE` through commit, verify the tuple, insert a complete parent-first generation, validate count/hierarchy/vector dimensions and smoke retrieval, then deactivate the old generation and activate the candidate atomically. Exact concurrent fingerprint winners become no-ops; different winners are conflicts requiring explicit rerun/review. An obsolete candidate must not silently replace a newer generation. Persist only complete generations; retain old generations in the first increment. No implicit rollback or garbage collection.

Pin one complete generation through query embedding and SQL retrieval. Use parameterized SQL scoped to it before cosine ranking, return only bounded top-k data and enforce a statement deadline. Initially use exact cosine search; a small returned limit does not bound scanned work. Measure actual corpus size/latency before choosing an ANN index. Reconfiguration and restart/restore tests must prove a mixed-model or partial generation cannot be served. Conversation taxonomy has no Redis read/write/fallback dependency; Admin retains its own Redis implementation unchanged.

## 7. Repeatable operator commands and receipts

Runtime implementation deliverables are:

| Owner | Path/command | Purpose |
| --- | --- | --- |
| Database | new forward migration; `npm run migrate:deploy` | Create schema and targeted always-enabled feature/plan policy |
| MCP | `scripts/sync-reference-taxonomy.mjs`; `npm run taxonomy:sync` | Validate, embed, import and activate/no-op a pinned corpus |
| Commerce | extend `scripts/sync-system-commerce-tools.mjs`; `npm run commerce:sync-tools` | Create/version/publish the three owned definitions, behavior and response fields |
| Commerce | `scripts/setup-commerce-product-discovery.mjs`; `npm run commerce:setup-discovery` | Thin environment orchestration of the three stages |

The setup wrapper is **Commerce-owned**. This refines revision03's proposed parent-wrapper location so every implementation file has an existing launcher repository owner. It launches documented child commands; it does not import sibling application internals or modify sibling source.

Taxonomy sync requires `--environment=<local|test|development|staging|production>` and exactly one of `--dry-run`/`--apply`; optional `--source=<verified-local-file>`; production apply requires the existing `--confirm-production` convention. Wrapper adds required `--workspace-root=<canonical-operator-checkout>` and forwards applicable flags explicitly. Validate repository/package identities and environment agreement; do not infer a developer path or silently redirect to a sibling checkout. Preserve existing credential keyring, database and Commerce actor prerequisites. The operator root must deliberately contain the accepted Database, MCP and Commerce revisions recorded in task reports.

Stage order: **preflight → migration → taxonomy → publication**. Preflight verifies identities, environment, command/runtime/package compatibility, database/pgvector support, configuration/credential access, approved source bytes, current publication ownership and actor. A dry-run may make read-only local/database/source reads but must not apply migrations, call a paid embedding API, change grants, create audit entries or publish. On an empty target, report planned post-migration checks explicitly rather than requiring nonexistent new tables before migration. No broad `prisma/seed.mjs`: it rewrites unrelated plan mappings.

Commands emit a bounded JSON receipt with:

```typescript
{
  schemaVersion: "1";
  environment: string;
  mode: "DRY_RUN" | "APPLY";
  stages: Array<{
    stage: "preflight" | "migration" | "taxonomy" | "publication";
    status: "PLANNED" | "APPLIED" | "UNCHANGED" | "FAILED" | "NOT_RUN";
    code: string;
  }>;
  taxonomy: null | {
    sourceSha256: string;
    importFingerprint: string;
    generationId: string | null;
    categoryCount: number | null;
  };
  publication: null | {
    previousReleaseId: string | null;
    releaseId: string | null;
    actions: Array<{
      name: string; // every one of the three standard product tools
      action: string; // reuse existing synchronizer action values
      revisionId: string | null;
      definitionHash: string;
    }>;
  };
}
```

Subcommands report their owned stage(s); the wrapper assembles the ordered full receipt. Exit nonzero on failure, retain earlier successful stages and mark later stages `NOT_RUN`. Rerunning after a failure completes the remaining work without duplicate active generations, owned tools, capabilities or releases. The receipt must not contain API keys, source corpus text, vectors, credentials, customer data or database connection strings. Operator readiness is not inferred merely from exit0: verify all three tools, the active compatible release and a complete corpus.

## 8. Failure evidence and validation boundary

Use the existing Shared structured logger. Retain the original thrown provider/SDK error object, original message and safe provider response/status/request ID as allowed by current redaction rules, attached to semantic stage/reason/tenant correlation. Redact tokens, headers, connection strings, personal data and sensitive bodies; do not replace the original exception with only a generic log. No customer-visible stack traces or secrets. New runtime modules, script names and event names use semantic product/taxonomy terminology, not architecture IDs.

Each implementation task validates its owned boundary. SYSTEM-TEST-001 exercises the actual adapters, PostgreSQL17/pgvector, operator wrapper and public Commerce/MCP/Background composition with deterministic fixtures, without customer sends. Exact provider category semantics and the pinned Shopify query guard require real adapter composition tests. Optional real-model quality evaluation is separate, with explicit model/corpus/version/budget and NOT_RUN/BLOCKED reporting if unavailable. Scripted runner fixtures cannot certify multilingual semantic retrieval quality.

The task bundle changes documentation only. Migration files, importer/setup scripts, provider/runtime changes and their tests are outputs of the tasks above, not completed work hidden in this patch.
