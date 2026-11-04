# ARCH-058: Product discovery and recommendation contracts

Status: accepted Shared/Database contracts with pending consumer implementation; Attempt 7 explicit CommerceAgent instruction and discount-inspection amendment, 4 November 2026.

Parent: [ARCH-058 architecture](../ARCH-058-commerce-agent-product-discovery.md). This file is normative for the ten ARCH-058 tasks. The [remaining implementation handoff](implementation-handoff.md) and [execution baseline](execution-baseline.json) bind the current accepted dependencies and source integration deltas. Revision 03 remains historical supporting evidence. This amendment changes documentation only; it preserves accepted implementation/publication records and MCP-001 lifecycle/report history while clarifying its current definition.

## 1. Ownership and compatibility

Use the existing `@modainteract/moda-interact-shared/commerce` and `/commerce/runner` entrypoints. SHARED-001 owns structural schemas, exported descriptor constants, equality helpers and the runner changes required by the new built-in descriptor branch. SHARED-002 publishes that accepted implementation separately. MCP owns shop-scoped tool discovery/execution, tool-input validation, provider/database reads and current shop/connection/plan/data access. Background owns conversations, inbound versions, processing leases, human control, retained conversation grants, the decision to use discount tools, purchase applicability and final customer-facing composition. Commerce owns authored system definitions, immutable release publication and the operator wrapper. Database owns forward schema/policy migration. Admin implementation is outside the change.

The accepted published package is **@modainteract/moda-interact-shared@4.0.0**, with runner **1.1.0** and the immutable receipt recorded in SHARED-002 / `execution-baseline.json`. Every remaining consumer installs that exact artifact; there is no open version-selection or publication decision. New product-discovery releases require `>=1.1.0 <2.0.0`; existing `commerce.v1` result envelopes remain. This is a coordinated pre-production update: deploy compatible consumers before activation and use fresh test conversations/grants. Backwards compatibility with pre-production retained grants is not required; do not add a legacy translation layer or mutate those grants. A package/integrity mismatch is a prerequisite failure, not permission to republish or choose another version. Installed consumer compatibility checks, including Commerce backend/CLI/preview, must use the accepted runner version.

New transport validation is structural: strict keys, types, lengths, enumerations and size bounds. Cross-field policy belongs in service functions, not new Zod refinements/transforms. Existing schema refinements unrelated to this work are not to be removed. Retain the existing result byte limits, deadlines and terminal error/referral rules.

### 1.1 Where CommerceAgent instructions live

The shopper-facing behavior is specified verbatim in [COMMERCE-001 section 3](../../decisions/commerce/ARCH-058/COMMERCE-001-provision-standard-product-discovery.md). That pending task creates `moda-interact-commerce/src/commerce/bootstrap/system-product-response.ts`, exporting `SYSTEM_PRODUCT_BEHAVIOUR` and `SYSTEM_PRODUCT_RESPONSE_INSTRUCTIONS`. These are application instructions, not the architect/developer TOML role. The MCP-001 archive contains neither a completed Commerce implementation nor a deployed replacement prompt; absence of that new file there is expected.

| Assembly position | Instruction owner and source | Publication or loading contract |
| --- | --- | --- |
| 1 | Shared `PLATFORM_INSTRUCTIONS` in `src/commerce/runner/instructions.ts` | Existing accepted runner kernel. Preserve its data-authority, grant and mandatory-referral rules. |
| 2 | Background `RECOVERY_INSTRUCTIONS` in `src/commerce/recovery-instructions.ts` | Existing host instructions, with the exact third-string replacement specified by BACKGROUND-001 section 3. Recovery state and historical checkout facts remain host-owned. |
| 3 | Published Platform business prompt | BACKGROUND-001 section 1 reads the single active PLATFORM configuration and its PUBLISHED revision once per turn. |
| 4 | Optional published current-Shop business prompt | The same bounded lookup loads the current shop's PUBLISHED revision, when configured; another shop's row is rejected. |
| 5 | Commerce `SYSTEM_PRODUCT_RESPONSE_INSTRUCTIONS` | The owned immutable release response contract supplies the structured selection/finalResponse instructions. |
| 6 | Commerce `SYSTEM_PRODUCT_BEHAVIOUR` | The owned `product_search.behaviourPrompt` is frozen into the published release, then loaded through its pinned manifest. Other granted feature prompts retain their existing manifest order. |

Background passes recovery instructions, Platform text and optional Shop text as `hostInstructions`. Shared's existing `composeTrustedInstructions` then assembles kernel, host instructions, response instructions and feature prompts in that order. This is the actual model-request assembly order, not a permission hierarchy created by string position. Host tool admission, current-policy checks, observation validation and final composition enforce authority. MCP provides tool contracts and results; it neither stores nor selects conversation instructions.

The existing Background third recovery string says `Missing evidence requires REFER_TO_STORE.` BACKGROUND-001 must replace that entire string with its exact scoped literal, allowing expected out-of-scope/missing-information dispositions while preserving requiredReferral, denial and terminal-error behavior. Appending a contradictory prompt is not sufficient. Do not copy the full Commerce behavior into Background; Commerce owns the reusable shopping/routing text and Background owns recovery context, policy and enforcement. Tests capture the actual model invocation and verify all six sources, the published bytes and the absence of the obsolete blanket sentence.

## 2. Standard product and shipping tools

All four tools belong to the existing `product_search` feature, which becomes active, `ALWAYS_ENABLED` and `systemRequired`. They are available to each otherwise authorized CommerceAgent store with an active eligible plan mapping, including Free plans and future stores. MCP retains tenant, connection, plan status and published-tool checks. Background retains turn, lease and conversation-grant checks. No merchant preference is required. No new feature or manually authored Studio definition is needed.

| Name | Definition version | Execution operation | Operation version |
| --- | --- | --- | --- |
| `commerce_resolve_product_categories` | `1.0.0` | `taxonomy.resolveCategories` | `1.0.0` |
| `commerce_search_products` | `2.0.0` | `products.search` | `1.0.0` |
| `commerce_get_product` | retain existing `1.0.0` | `products.get` | retain existing `1.0.0` |
| `commerce_get_shipping_information` | `1.0.0` | `shipping.getInformation` | `1.0.0` |

Published descriptors must pass the **actual** existing bounded subset validator after projection. Shared 4.0.0 supplies bounded enum metadata in its accepted schemas. Commerce consumes those schemas through its existing authoring projector and applies the exact narrow projector changes listed in COMMERCE-001. Preserve `$schema`/default stripping, required keys, nullability and finite literal/enum bounds. Do not write alternative local wire schemas, admit arbitrary `const`/`oneOf` keywords or create another general schema engine. Tests start from actual Shared schemas and the actual Commerce projection/publication route, including `category.system`, recommendation version/scope/promotion kind and nullable IDs.

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

`NOT_READY` is limited to an absent active complete corpus or unavailable required embedding configuration. `TEMPORARY_UNAVAILABLE` is limited to classified operational database/embedding timeouts or transient unavailability after the request is authorized. These are `status: "OK"` result data; the host may continue with merchant text search. Wrong credentials, tenant denial, malformed vectors, an invalid model/configuration tuple, invalid SQL, unexpected exceptions and malformed output remain typed MCP errors. Background independently rejects stale turns, leases and conversation grants before invoking or using the result. Preserve and log original errors using Shared logging.

### 2.2 Merchant product search

Extend only the search input. Preserve existing maximum-price, available-only, limit and cursor contracts/defaults. Add `browse?: boolean`, parsed default `false`. `query` becomes optional/nullable with parsed default `null`; a non-null query remains 1..200 characters. Add optional `category`:

```typescript
{
  system: "SHOPIFY_STANDARD_PRODUCT_TAXONOMY" | "WOOCOMMERCE_PRODUCT_CATEGORY";
  id: string; // 1..128
  taxonomyVersion: string | null; // 1..64 when non-null
}
```

Use this flat object because the existing published JSON Schema subset does not support `oneOf`. Service policy rejects a normal (`browse: false`) request with neither query nor category, a category incompatible with the authorized connection, invalid native IDs, a missing/mismatched Shopify taxonomy version, or a non-null Woo taxonomy version. Shopify IDs must be canonical taxonomy GIDs validated against the active pinned reference version before deriving the provider's short filter token. Woo IDs must be positive decimal strings and are scoped to the current shop. Never treat Shopify IDs, labels, product types or broad `Shop.activeCategoryId` as Woo native category IDs.

The first increment requests **exact assigned category membership**. There is no descendant flag or automatic parent expansion. For Shopify, use the documented pinned Admin API `products` category filter and verify `Product.category.id`; do not assume the variants search supports that filter. For Woo, the REST category query can include children, so exact membership requires a bounded check against returned `categories[].id`. Preserve true provider variant IDs, including null for a Woo simple product. Variant pagination within category-filtered Shopify products cannot silently drop later variants.

The existing opaque cursor must bind the authorized shop/connection, provider branch, normalized browse/query/category/version, publication-visibility rules, price/availability filters and both product and variant progress where needed. A filter or shop change invalidates it. Bounded scanning can return an empty page with a continuation cursor. `truncated` and exhaustion must be truthful. Fetching a small top-k taxonomy result or product page does not justify an unbounded underlying scan.

For `browse: true`, require query null/omitted and category absent; reject combinations before provider I/O. This is an explicit bounded catalogue operation, never a fabricated wildcard/text intent. Preserve caller price/availability filters and their existing defaults; Background fallback requests set `availableOnly: true` and only recommend an observed `available === true` product with a verified non-null URL. In browse mode Shopify requires verified parent status `ACTIVE` and an actual non-null safe storefront URL; Woo requires parent `status: publish` and `catalog_visibility: visible|catalog`, plus `status: publish` for returned variations. Do not include drafts, private/hidden products, search-only Woo listings, or unpublished variants merely because inventory is positive. The provider queries/projections and post-read checks must establish these facts, without changing the public product schema. Keep the existing bounded page/request ceilings; empty output with a continuation cursor is not an exhausted catalogue. No bestseller/featured label without actual evidence. Bind `browse` and fixed visibility rules into the opaque cursor and reject cross-mode replay. Ordinary text/category search keeps its existing semantics.

Search and exact product reads retain their existing output shapes. Add trustworthy currency/context only through existing declared product/context fields. Unknown currency stays unknown; shop base currency is not proof of a customer-market price. Product identity, price, availability, URL and discounts must come from the current shop's actual reads, not from the taxonomy. No product mirror is added.

### 2.3 Native shipping information

Add/export `CommerceShippingInformationInputSchema`, `CommerceShippingInformationInput`, `CommerceShippingInformationSchema` and `CommerceShippingInformation`; add the exact dictionary members and the `shipping.getInformation` policy operation. The fourth tool is published, granted and retained like other `product_search` tools, not a discount built-in. Missing optional policy permission must not remove the tool from an otherwise valid immutable grant or disable product discovery.

Input is the strict object `{productId?: string | null, variantId?: string | null}` with each non-null ID bounded 1..128; both parsed defaults are null. Service validation requires productId when variantId is non-null, validates provider-native identifiers and current-shop ownership before reads, and rejects extra query/URL/destination/cart/shop/scope arguments. No IDs requests the native merchant policy only. No caller-supplied scope, token, provider URL or provider query is permitted.

Successful output is one strict object; all shown fields are required and nullable values are explicit:

```typescript
{
  provider: "SHOPIFY" | "WOOCOMMERCE";
  observedAt: string; // existing ISO timestamp bound
  product: {
    status: "NOT_REQUESTED" | "VARIANT_REQUIRED" | "AVAILABLE";
    productId: string | null; // 1..128
    variantId: string | null; // 1..128
    requiresShipping: boolean | null;
    virtual: boolean | null;
    weight: null | {
      value: number; // finite, >= 0
      unit: "GRAMS" | "KILOGRAMS" | "OUNCES" | "POUNDS" | null;
    };
    dimensions: null | {
      length: number | null; // each finite, >= 0 when present
      width: number | null;
      height: number | null;
      unit: string | null; // 1..16; null throughout this first increment
    };
    shippingClassId: string | null; // 1..128
    shippingClassSlug: string | null; // 1..512
  };
  policy: {
    status: "AVAILABLE" | "NOT_CONFIGURED" | "SCOPE_NOT_GRANTED" | "UNSUPPORTED";
    trust: "UNTRUSTED_REFERENCE";
    title: string | null; // 1..512
    bodyStatus: "AVAILABLE" | "EMPTY" | "TOO_LARGE" | "NOT_AVAILABLE";
    bodyHtml: string | null; // 1..8000 characters AND <= 16384 UTF-8 bytes
    url: string | null; // HTTPS, 1..2048, verified current-shop policy URL
    updatedAt: string | null; // source timestamp, never invented
  };
}
```

Leaf schemas enforce structural bounds; adapter/service code enforces cross-field relationships and the UTF-8 budget. This result is still inside the existing `commerce.v1` outer envelope and byte/deadline limits. `UNTRUSTED_REFERENCE` means the policy may supply facts but cannot issue instructions, create intent, expand permissions, or authorize a promotion/cart change. Policy HTML is data; do not execute it, follow embedded links, fetch the policy URL, or append raw HTML to a customer message.

**Product status rules.** No requested product yields `NOT_REQUESTED` with null IDs/facts. `VARIANT_REQUIRED` follows a successful current-shop product read when variant-level facts are required; return its actual productId, null variantId and null facts. For Shopify productId alone, verify product existence and return this status; never select the first variant. For a standard Woo variable parent without a selected variation, use the same status. `AVAILABLE` identifies the exact observed simple product or requested native variant and exposes only fields actually provided. A missing product/variant, invalid native ID, mismatch or malformed provider result retains typed outer-error semantics; do not echo an unverified ID as an existing product. For this shipping operation only, support Woo type simple and standard type variable with an explicitly selected variation when needed. Reject other/custom/grouped/external types with the existing appropriate typed outer error; this is a new narrow shipping rule, not an assertion that get/search already has a type allowlist. A supplied variation for a simple product is an identity error. Preserve get/search behavior outside its separately defined browse changes.

**Shopify mapping.** Use fixed named Admin 2026-07 read queries through the real connection resolver/provider/query guard. Variant reads select `productVariant(id) { id product { id } inventoryItem { requiresShipping measurement { weight { value unit } } } }`; both selected IDs must match. Existing `read_products` is sufficient for these fields. `virtual`, dimensions and shipping class fields are null. A product-only existence query is separately bounded. The policy query selects `shop { primaryDomain { url } shopPolicies { type title body url updatedAt } }`; project only `SHIPPING_POLICY`. `shop.shippingPolicy` is a Storefront field and must not be substituted into Admin.

Read accessToken and nullable scope together from the same existing validated offline `shopify.Session` row; no schema migration is needed. Keep tokens/scopes private. Before the policy query, the credential-owning provider checks the exact trusted `read_legal_policies` requirement. Missing/null/blank persisted permission maps only in this shipping adapter to `SCOPE_NOT_GRANTED` with zero policy HTTP calls; product reads may still succeed. A missing/invalid session, tenant/native-provider permission failure, or 401/403/GraphQL error after an attempted authorized query remains an actual outer error with original diagnostics. Conversation turn/grant checks remain in Background. Do not classify all `UNAVAILABLE` failures as missing permission. Preserve query/depth/pagination/field/request/response bounds and private resolver key allowlists when adding this narrowly typed preflight requirement.

**Policy mapping.** A successful authorized query with no shipping policy yields `NOT_CONFIGURED`, null payload and `bodyStatus: NOT_AVAILABLE`. A returned policy yields `AVAILABLE` with its verified URL/title/timestamp; a blank body becomes `bodyStatus: EMPTY`, bodyHtml null. A nonblank body within both limits is `AVAILABLE` bodyStatus and retains its exact HTML bytes. A selected body exceeding either limit becomes `TOO_LARGE` with bodyHtml null and the valid URL/title/timestamp retained; never silently truncate a policy and imply it is complete. A whole provider response exceeding its existing transport bound remains a typed read error, not missing policy. A successful non-AVAILABLE policy status has all nullable payload fields null and bodyStatus NOT_AVAILABLE. A malformed/unsafe provider policy URL is handled by current provider-result validation, not replaced by a guessed slug. Verify against the authenticated shop and returned primary domain, preserving the existing HTTPS/host rules.

**Woo mapping.** Reuse the active verified tenant-bound REST read grant and existing product/variation operations; add explicit requested/projection fields for `virtual`, `shipping_required` (product endpoint only), `weight`, `dimensions`, `shipping_class`, `shipping_class_id` and required identity/type fields. Existing REST product reads do not supply measurement units: return unit null, never assume kg/cm, and do not add settings GETs or request write permission. Normalize missing/null/empty-string measurements to null, parse supplied nonnegative decimal values to finite numbers, and reject malformed values, including whitespace-only numeric strings. Return dimensions null if all three values are null; zero remains a known value. Product endpoint `shipping_required` is authoritative when returned. The variation endpoint does not return it and Woo's effective requirement is filterable: return requiresShipping null for a variation even when virtual is false; preserve its explicit virtual flag separately. Use endpoint-returned effective variation measurements/class, without a second guessed parent inheritance layer. Woo shipping_class_id 0/null/absent maps to null; a valid positive native integer maps to its decimal string, and malformed/negative IDs are errors. Empty/null/absent class slug maps to null; preserve observed fields without inventing a class name or description. Native policy is `UNSUPPORTED` with null payload; do not guess WordPress policy slugs or introduce a crawler/new page configuration in this increment.

Existing `merchant_knowledge_lookup` with purpose `SHIPPING_AND_DELIVERY` remains a separately authorized/entitled source. Product-search being standard does not grant Merchant Knowledge or enable a disabled preference. A no-match knowledge result is ordinary absence; the nearest chunk is not proof that the requested cost/destination/time is covered. Contradictory or insufficient policy evidence cannot support an exact delivery claim. No shipping configuration scan, shipping-zone rate calculator, Storefront/Store API cart session, cart mutation, quote or promised ETA is introduced here.

MCP-003 owns this adapter and native mappings; SHOPIFY-001 owns the declared-scope/runtime-scope rollout. A declared scope is not a granted permission. Live rates remain current provider facts, never taxonomy-vector facts. Provider references and exact source touchpoints are recorded in MCP-003 and SHOPIFY-001.

## 3. Canonical discount data and caller-owned failure handling

Retain `commerce_get_discount_options` and `commerce_get_discount_details`, their existing inputs, normal success objects, canonical `CommerceOfferSchema` and `CommerceDiscountDetailsSchema` from ARCH-052. The accepted Shared 4.0.0 options result includes the configured shop `mode`; keep that truthful field and the existing permitted-catalogue/FIXED-selection semantics. Reading those shop settings is part of executing that existing data contract. It does not give MCP conversation state or authority to choose a conversational recommendation. Do not invent a constant mode, remove a field under the same contract hash, or introduce a second discount engine.

MCP's canonical catalogue executor reads current shop configuration/override/selected IDs at the actual call boundary. It returns the same shop data for the same authenticated shop, inputs and data state regardless of conversation, purpose, inbound version or retained grant. For `NONE` with initial cursor null, options is the canonical successful empty result `{mode:"NONE", offers:[], cursor:null, truncated:false}`. Details under NONE or outside the current permitted FIXED set remains DENIED; a permitted ID without current details returns `{details:null}`. Existing invalid/expired/cross-mode cursor rejection still applies before the empty NONE result. The existing AI_BEST_APPLICABLE catalogue semantics remain unchanged. Capability discovery does not need these configuration reads merely to advertise the two tools.

The accepted output union also includes this strict alternative:

```typescript
{ outcome: "UNAVAILABLE", reasonCode: "TEMPORARY_UNAVAILABLE" }
```

This `CommerceOptionalLookupUnavailableSchema` branch is inside `status:"OK"` only for the exact classified transient catalogue-data read failures in MCP-002, after ordinary shop/data authorization succeeds. It has no fabricated offers, mode, cursor or condition facts. MCP returns it consistently to every caller; it never decides whether the request belongs to a conversation or initial outreach. Shop/configuration authorization failures, malformed arguments/data, missing schema, unexpected exceptions, and request cancellation/deadline remain actual errors. An outer `ERROR` retains the runner's existing terminal behavior.

The caller decides what the unavailable data permits. Background's conversational host can omit a promotion and continue with independently verified product facts. Its initial-outreach adapter explicitly rejects the unavailable branch under its existing conservative failure path. This distinction is implemented in Background, not by a purpose switch in MCP. Original source diagnostics remain logged at the owning reader boundary.

Background resolves the current merchant recommendation policy before exposing/running discount tools, checks it around discount reads and before final claims, and enforces the exact proposed-purchase conditions. `NONE` makes no conversational discount RPC or promotional claim. FIXED uses the current permitted selection/override; AI_BEST_APPLICABLE uses observed permitted catalogue facts. A tool result's configured mode does not override the host's current policy. Unknown or incomplete condition facts do not support a promotion. `details:null` never proves a saving.

## 4. Built-in tool identity and retained grants

Discount tools remain code-defined built-ins; the four product/shipping tools remain published system capabilities. Do not fabricate database tool/revision/capability identities for built-ins, grant everything returned by `tools/list`, or publish duplicate discount definitions in Studio.

The accepted Shared release supplies `CommerceBuiltInToolDescriptorSchema` and its inferred type:

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

Consume the two accepted `commerceDiscountBuiltInDescriptors` from Shared with these exact descriptions:

- `commerce_get_discount_options`: `Read the current shop's permitted discount options.`
- `commerce_get_discount_details`: `Read details for a permitted discount in the current shop.`

Compute `contractHash` from existing canonical JSON over `{name, definitionVersion, description, inputSchema, outputSchema}`. Use the bounded input subset and canonical generated JSON schema for the exact Shared output member. Hashing occurs in the existing trusted Node adapter/publication path; the portable contract does not introduce a Node-only import into browser entrypoints. Export `commerceBuiltInToolContractPayload` as a pure canonical-payload helper and accept an injected digest where necessary. Exported descriptor hashes are generated from that canonical payload as reviewed constants, verified by Node tests against the actual schemas; no caller-controlled hash or runtime Node import is required to read the portable constants. Verify the exported descriptors and compiled schemas agree; a hash asserted by MCP alone is not authority.

`CommerceManifestSchema` already includes `builtInTools`, an array of these descriptors, max 2 and default `[]` for producers that do not project built-ins. Its `grantedTools` union already accepts `CommerceBuiltInToolGrantSchema`:

```typescript
{
  kind: "BUILT_IN";
  toolName: "commerce_get_discount_options" | "commerce_get_discount_details";
  definitionVersion: "1.0.0";
  contractHash: string;
}
```

The existing published grant shape remains unchanged. Existing PostgreSQL JSON storage retains both branches; no grant table column is needed. The accepted DATABASE-001 forward migration already updated the database JSON-shape guard and insert trigger to admit the allowlisted built-in branch while preserving published-release and row-identity invariants. Consume it unchanged. MCP validates only the canonical descriptor identity in its shop capability projection; it never loads a persisted conversation grant. Background validates/persists that grant and enforces current workflow permission. A structurally valid database row alone is not permission for the model to invoke a tool. Published grants still equal the selected published-capability union with their sorted provenance keys. Built-in grants equal the descriptor set by name/version/hash. The combined list has at most32 entries with unique names; duplicate, collision, missing and unexpected branches are invalid. Structural parsing and separate service validation together enforce this without adding business refinements to the new leaf schemas.

Update manifest/grant equality, deduplication, runner tool descriptors, preflight/registration/authorization, MCP projection/execution, Background persistence/list checking, and the existing Commerce preview adapter as required. Every switch must deliberately distinguish the branches. The model only sees the usual MCP `{name, description, inputSchema}` listing; the host matches it exactly to an authorized pinned descriptor before execution.

### 4.1 Provider metadata and host workflow are separate

The conversational Background client validates its existing `CommerceAssertionSchema` locally, then serializes exactly `{shopId}` into the existing `X-Moda-Commerce-Context` header. The private ingress remains the authentication boundary and MCP supplies the environment from server configuration. Model arguments cannot set the tenant. Background sends no conversation ID, recovery ID, grant ID, inbound version, lease, control state or discount-policy override to these standard tools. Existing opaque context forwarding for unrelated already accepted execution adapters remains unchanged; this work adds no CONVERSATION interpretation anywhere in MCP.

`parseMcpRequestContext`, `resolveShopCapabilities` and the production capability reader retain their generic shop responsibilities. MCP-002 removes discount-policy reads from capability listing and supplies the two exact canonical built-in descriptors for an active supported shop with an ACTIVE/TRIALING subscription and active plan, independently of the configured recovery-offer mode. It reads no Conversation, ConversationMessage, ConversationControlEvent or CommerceConversationGrant row. There is no `conversation-discount-context.ts` module, domain conversation adapter, conversation grant cache, lease check or human-control check in MCP. Published product/knowledge eligibility retains its actual feature/plan/connection rules, including MCP-001's required-feature selection.

The MCP manifest's `grantedTools` field describes the shop-eligible tool projection required by the existing wire contract; MCP does not create or retain a conversation grant. Construct this projection with the accepted Shared helpers and canonical built-in identities. `tools/list` and the generic manifest must agree exactly. Discount configuration is read by its actual executor, not to personalize tool discovery for a caller's workflow.

Background alone calls `readGrant`, `persistGrant` and `validateRelease`. New conversation grants retain the full validated manifest, including both canonical discount built-ins even under NONE. They express the stable available identities; current business policy independently controls use. Register those exact identities with the runner, validate the full remote list first, then hide/deny discount execution locally for NONE or an empty FIXED selection. NONE-to-AI may enable use of an already retained identity without changing the grant; AI-to-NONE hides/denies it without deleting the identity. Retain the existing exact `manifestMatchesGrant` check, including release and selected-capability equality; do not create a narrowed substitute grant, silently widen an old grant, or relax Shared equality. A pre-production grant missing the required canonical pair or using an old hash requires the already documented fresh-conversation transition.

Current conversation ownership, inbound version, processing lease, human control and policy checks happen in Background at its named existing fences. MCP may successfully answer the same generic shop request when a separate conversation is stale or under HUMAN control; Background must prevent that workflow from making/using the call. Tool availability/data access and permission to continue a customer conversation are separate checks with separate owners.

Shared 4.0.0 also contains `CommerceConversationToolContextSchema` from the earlier accepted contract implementation. This correction does not use that export, transmit it, or authorize MCP to interpret it. The current runtime correction remains compatible with 4.0.0. Removing the obsolete public export requires a separate Shared source correction, acceptance, new immutable release under its public-API version policy and coordinated consumer pins. That cleanup is not implemented or silently made a prerequisite by this focused task-definition amendment.

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

Discovery occurs inside the existing bounded runner/tool loop under trusted published instructions; host finalization does not launch a second search/browse loop. The host records trusted tool observations for the current turn, keyed by authorized descriptor/revision or built-in hash, arguments and current shop. Validate selected product/variant/offer IDs against those observations. Missing selections or free-text-only promotion must not bypass this path. When the turn is producing a product recommendation, the full customer-facing recommendation is composed by trusted host code from validated product data and permitted facts, including a no-promotion product branch. Do not concatenate unvalidated model monetary claims to a validated card.

Re-read selected exact products and canonical discount facts in the existing host finalization phase with current policy and current-turn checks before/after awaits. BACKGROUND-001 fixes one total of ten charged MCP tool calls, with Shared runner budget six and at least four reserved for finalization; unused runner capacity also remains available within that total. Preserve Shared's existing admission rule `discoveryAttempts + selectedLegacyEvidenceCount <= 6`: five discovery attempts plus one evidence ID can proceed; six plus one is `EVIDENCE_RESERVATION_EXCEEDED`. Actual legacy replay is charged once, together with canonical product/offer and selected shipping refreshes, within the original total ten. Determine the ordered refresh plan before calling; reduce whole alternatives or unsupported offer claims to fit the remaining budget, never create a second budget or refresh loop. Preserve the existing overall deadline. Reject changes to identity, price currency, availability, applicability or authorization. For `NONE`, use only a grounded product description/current price if known. For `NATIVE_SALE`, require provider-native sale evidence and permitting policy. For `DISCOUNT`, check exact proposed purchase, condition completeness, status, dates, targeting/exclusions, quantities, currency-aware subtotal thresholds, sale/customer/usage restrictions and supported reciprocal combination policy. In the conversation adapter, Shopify's bounded collection list of 20 entries has unknown completeness and becomes null for collection-dependent eligibility; fewer than 20 retains its observed complete list. Missing native-sale evidence is unknown sale status, never known false. Unsupported eligibility is not advertised as applicable. Do not manufacture an outreach attempt ID or legacy CommerceEvidence record; reuse pure validation arithmetic/policy through a conversation adapter.

A supported offer is a claim about observed current facts, not guaranteed redemption or a provider-atomic cart price. Do not calculate a guaranteed multi-discount total unless the existing canonical rules establish it. After current host finalization, the existing processor language/wrapper/moderation/send stages remain in control; no new last-moment processor hook or worker rewrite is included. Preserve admission, takeover, stale-turn and delivery behavior. Use the current conversation language and Shared localization/formatting; all new fixed customer-facing strings require the existing 20 supported locales.

### 5.1 Expected limitations and answer presentation

Add/export `CommerceResponseDispositionSchema` / `CommerceResponseDisposition` and `CommerceAnswerPresentationSelectionSchema` / `CommerceAnswerPresentationSelection` through the existing commerce entrypoint. The latter owns only these optional response-detail fields, independently of the existing recommendation selection fields:

```typescript
{
  responseDisposition?: "STANDARD" | "OUT_OF_SCOPE_REDIRECT" | "SHIPPING_INFORMATION_UNVERIFIED";
  shippingInformationSelection?: {
    productId: string | null; // 1..128
    variantId: string | null; // 1..128; needs productId in service policy
  };
}
```

No arbitrary text, amounts, URLs, scope claims or observation IDs are supplied by this selection. Both IDs null reference the current-shop policy-only observation. Non-null IDs must match the exact current-turn shipping-tool observation; choose the latest observation of the same arguments and revalidate any used facts before final composition. Shipping selection requires an explicit disposition; omission of both presentation fields is permitted for ordinary existing non-recommendation responses. A policy-only null/null shipping observation may use that ordinary path; a product-bearing shipping observation latches controlled composition even when the model omits shippingInformationSelection. The maximum details depth remains 5. `STANDARD` is the normal host-composed branch when structured recommendations/shipping presentation are present; it is not a bypass for arbitrary replyText.

Expected limitations use `answerKind: ANSWER`, null referralReason and the typed disposition. Keep the hard `REFER_TO_STORE` envelope unchanged, including empty details/evidence, published-details referral handling, requiredReferral enforcement and fixed hard-referral rendering. Update the runner's blanket unknown/ungranted-fact instruction narrowly: absence of support for one fact permits a truthful limitation plus independently authorized help; it never permits asserting that unsupported fact or clearing a tool-imposed terminal error. The model's disposition creates no tool or delivery authority. Ordinary no-tool greetings/clarifications remain valid.

The trusted host latches controlled composition whenever the run uses product/discount observations or a product-bearing shipping observation (a non-null productId request), the trusted workflow requires a recommendation, or a soft disposition/owned recommendation or shipping selection is present. A model cannot escape that latch by omitting details, returning empty selections or switching to plain text. Within that branch Background discards raw replyText for customer composition. Invalid/missing selections produce the localized verified-store fallback under the current failure semantics, never unvalidated promotional prose. Do not claim a semantic guarantee for unrelated legacy ordinary-text turns. Policy-only grounded answers may use the existing ordinary answer path only when no recommendation/controlled-presentation branch is active.

For `OUT_OF_SCOPE_REDIRECT`, compose a brief localized store-scope sentence and at most one verified available current-shop product with any currently permitted/applicable offer. Do not invoke weather/general-web tools or send the off-topic text to taxonomy as supposed product intent. Choose from current customer product/category context, then refreshed owned-basket context, then explicit bounded browse. Merchant-selected/featured metadata can be used only if an actual authorized source provides it; no new feature-management store is added. No context means a store suggestion, not a claim of similarity or bestseller status. If bounded search yields no usable item, provide the verified store URL without claiming the entire catalogue is empty. Do not repeatedly append the same unrelated suggestion to every follow-up; honor explicit customer rejection of product suggestions using the existing conversation context.

For `SHIPPING_INFORMATION_UNVERIFIED`, state that the particular delivery detail cannot be confirmed, give a verified policy/store reference, then optionally one separately validated related product/offer. Attempt the relevant granted native/knowledge read before claiming no information when the configured budget permits; an unavailable grant is not permission to call that tool. Record the expected absence/insufficiency or missing capability, without conflating it with a terminal failure. Missing/irrelevant knowledge, native policy absence, absent policy scope, empty/oversized policy body or no supported exact quote can justify the limited statement. A product alternative does not establish its delivery charge/speed/destination eligibility. Location words in an unrelated question do not become a shipping destination.

For positive shipping facts combined with a recommendation, use `STANDARD` plus a shipping selection. Host composition may include the exact observed requiresShipping fact, a verified merchant-policy link, and the separately validated product/offer. Product and policy availability are independent: missing/unsupported policy does not erase a known current product requirement; it only removes the unavailable policy reference. An AVAILABLE policy with EMPTY or TOO_LARGE body may still supply its verified URL. Never merge raw model policy summaries, HTML, measurements with unknown units, or inferred shipping costs/times into that body. A destination-specific interpretation that the fixed facts cannot support uses SHIPPING_INFORMATION_UNVERIFIED and any available policy link. This increment deliberately avoids a new semantic prose-verification engine. Ordinary policy-only answers can summarize the bounded relevant reference using the existing grounded-answer instructions, without presenting a quote as current checkout truth.

Every controlled body follows: supported fixed answer or narrow limitation, verified policy/store reference where relevant, verified product, permitted promotion if applicable, verified product link. Preserve current NONE/FIXED/AI_BEST_APPLICABLE policy. NONE never triggers promotional reads/claims. An empty or incomplete optional discount result means no supported promotion for this recommendation, not that the merchant has no discounts. Missing product evidence results in store-link fallback. A free-shipping promotion cannot supply a destination/quantity/eligibility fact absent from canonical validation.

Background owns a typed catalogue of trusted fixed strings for the existing 20 supported locales and uses the same effective-language evaluation as the processor; do not render the body in the old language and wrap it in a newly persisted language. Reserve and account for finalization calls/time up front, including a selected shipping refresh; perform current-turn/takeover checks around awaits. Never call provider APIs directly from Background. For controlled responses, Background constructs a private optional `hostComposedReplyCandidates` array on its internal CommerceAgentResult: 1..3 complete strings, each 1..4096, first equal to replyText. Order is full supported recommendation, one product, then a minimal disposition plus verified store reference; omit duplicates and raw bodies that already exceed the existing limit. This is not a Shared/model/MCP field. The same existing processor composition call passes these candidates to the existing wrapper service, which loads actual context/slot/locale once and uses unchanged renderPreparedWrapper to select the first fitting candidate. Advance only on OUTPUT_TOO_LONG; retain every other refusal. No wrapper means exact first-body passthrough. Existing replay/application-key rules use the selected candidate's digest/body, and a previous selected response must still match a current candidate exactly or return REPLAY_MISMATCH. Never truncate a URL or qualification. If no candidate fits, preserve the existing typed wrapper/admission failure. Authorize only this narrow existing processor/wrapper seam, not a new send stage, worker rewrite, host-side wrapper prefetch, duplicate configuration read or provider recheck in the processor.

Commerce owns explicit nonempty published response instructions for these fields and the existing recommendations. Replace any inherited instruction requiring empty details for these controlled branches. Preserve ordinary non-recommendation behavior and unrelated response fields. Studio feature previews must consume the matching published/owned response instructions instead of silently pinning EMPTY_RESPONSE_CONTRACT when exercising this capability; label raw runner previews as such unless they actually use Background's final composer/wrapper. Do not claim full customer-preview parity from raw model replyText.

### 5.2 Required permitted discount inspection before a recommendation

The source-owned Commerce behavior explicitly requires discount discovery before finalizing a product recommendation whenever the current Background policy is FIXED with a nonempty authorized-ID list or AI_BEST_APPLICABLE. The model calls the canonical discount-options tool inside the existing runner loop and, when a permitted candidate exists, the canonical details tool for at least one such candidate. This is a bounded inspection, not a claim to exhaust the catalogue or identify the global best offer. Existing selected-offer eligibility and final revalidation still decide whether any promotion may be shown. NONE and FIXED with no authorized ID make zero discount calls and permit a verified product-only recommendation with its current price, but no discount or native-sale promotional claim.

BACKGROUND-001 implements the pure `evaluateRecommendationDiscountInspection(observations, policy)` helper in the already planned `recommendations/observations.ts`. Its only outcomes are `NOT_REQUIRED`, `SATISFIED`, `MISSING_OPTIONS` and `MISSING_DETAILS`. It uses the host's existing accepted current-turn observations under the same authorized descriptor and unchanged policy fences; no prior-turn, wrong-tool, wrong-shop, mismatched-mode or rejected observation counts. Use the latest accepted observation for each canonical argument key, as the existing ledger requires.

For a mode requiring inspection, no retained canonical options outcome means MISSING_OPTIONS. A normal mode-matching options result or the canonical typed optional UNAVAILABLE result counts as a completed options call. Form the union of permitted offer IDs from **all retained normal options observations**; FIXED intersects that union with the host's authorized IDs, while AI_BEST_APPLICABLE uses the returned IDs. A later empty result or UNAVAILABLE under different arguments cannot erase a previously retained nonempty page. If the union is empty, inspection is SATISFIED and a grounded product-only recommendation is permitted. If nonempty, require at least one retained matching details outcome for a union member: actual details, explicit `details: null`, or the canonical typed optional UNAVAILABLE result. Such an outcome completes bounded inspection; it does not prove offer eligibility. Otherwise the outcome is MISSING_DETAILS. A later observation with the same canonical argument key replaces the earlier one normally; this rule does not preserve stale success.

Apply this acceptance gate only when an otherwise accepted ANSWER would retain product recommendation proposals, before selecting fallback products or planning their final refreshes. NOT_REQUIRED and SATISFIED continue through the existing validation/composition path. MISSING_OPTIONS and MISSING_DETAILS discard every product recommendation proposal. Continue the existing controlled composition with no product proposal: a weather redirect becomes the minimal disposition plus verified store reference; independently valid shipping facts/reference retain their existing authorized refresh and composition path. An ordinary or shipping-only answer with no product recommendation does not require discount discovery and cannot be redirected solely because this helper returns a missing-inspection outcome. No extra model call, host-side discovery, second loop or larger call budget is allowed. A hard error, requiredReferral, stale turn, takeover or policy change retains its existing hard handling and cannot be softened by this helper. Never say that no discounts exist, or that a lookup failed, merely because the model skipped the required call. The helper adds no Shared/MCP schema or database read.

## 6. Taxonomy storage and import lifecycle

DATABASE-001 is authoritative for exact Prisma fields, SQL names, checks, indexes and foreign keys. Use `commerce.ReferenceTaxonomyGeneration` and `commerce.ReferenceTaxonomyCategory`, with `Unsupported("vector")`, dimension checks and complete-generation activation. Corpus identity is environment/source/language. A generation pins source bytes/version/checksum, embedding provider/model/dimensions/indexVersion, deterministic embedding-text version and import fingerprint. No taxonomy rows contain merchant inventory.

MCP-001 owns `src/data/reference-taxonomy-manifest.json` and the parser for the pinned Shopify `2026-08` English distribution. The current submitted worktree contains that manifest, importer and CLI; the manifest records distribution SHA256 `afc8f21242527a209622302bd99e29efe8cc2521ae949104c2c0dc3f931e461a`, 14,606 categories and 183,429 compressed bytes. The full source distribution is not included in this archive; these are observed manifest/report values, not a new download verification. After MCP-001 acceptance, remaining tasks reuse that source identity and receipt without choosing another release/format or repeating completed preparation. Admin remains separate. Every imported record obeys the public wire and Database bounds without truncation. Optional `--source` accepts only bytes matching that MCP manifest; production exposes no `--manifest` or source-URL override. Existing parser/service/main factory seams are test-only and remain in MCP-owned focused tests. Full operator CLI tests use the accepted staged source bytes and deterministic provider transport without replacing the production manifest or injecting an undocumented environment hook.

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
| Commerce | extend `scripts/sync-system-commerce-tools.mjs`; `npm run commerce:sync-tools` | Create/version/publish the four owned definitions, behavior and response fields |
| Commerce | `scripts/setup-commerce-product-discovery.mjs`; `npm run commerce:setup-discovery` | Thin environment orchestration of the three stages |

The setup wrapper is **Commerce-owned**. This refines revision03's proposed parent-wrapper location so every implementation file has an existing launcher repository owner. It launches documented child commands; it does not import sibling application internals or modify sibling source.

Taxonomy sync requires `--environment=<local|test|development|staging|production>` and exactly one of `--dry-run`/`--apply`; optional `--source=<verified-local-file>`; production apply requires the existing `--confirm-production` convention. Wrapper adds required `--workspace-root=<canonical-operator-checkout>` and forwards applicable flags explicitly. Validate repository/package identities and environment agreement; do not infer a developer path or silently redirect to a sibling checkout. Preserve existing credential keyring, database and Commerce actor prerequisites. The operator root must deliberately contain the accepted Database, MCP and Commerce revisions recorded in task reports.

Stage order: **preflight → migration → taxonomy → publication**, using the exact child argv/cwd and receipt mapping in COMMERCE-001. Preflight checks repository identities, environment, installed artifacts, source identity and available database state. On an already configured schema it also checks configuration/actor and ownership before writes. On a genuinely schema-empty target those database-dependent checks are explicitly deferred until after migration. A dry-run reports the deferred conditions and makes zero migration/embedding/grant/audit/publication writes. Apply may therefore complete migration and then return taxonomy `FAILED` / `TAXONOMY_CONFIGURATION_UNAVAILABLE`, publication `NOT_RUN` / `PREREQUISITE_FAILED`, exit 1. Missing required publisher actor uses `ACTOR_UNAVAILABLE` when that check becomes possible. Provision actor/configuration through the existing Admin workflows named in COMMERCE-001, then rerun; never silently create them or call a partial setup successful. No broad `prisma/seed.mjs` against an existing environment. The wrapper forwards verified `--source` unchanged and does not parse/download/choose taxonomy independently of MCP-001.

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
    importFingerprint: string | null;
    generationId: string | null;
    categoryCount: number | null;
  };
  publication: null | {
    previousReleaseId: string | null;
    releaseId: string | null;
    actions: Array<{
      name: string; // every one of the four standard product/shipping tools
      action: string; // reuse existing synchronizer action values
      revisionId: string | null;
      definitionHash: string;
    }>;
  };
}
```

Subcommands report their owned stages and the wrapper assembles the ordered full receipt. The submitted MCP CLI writes exactly one receipt object as one stdout line, with exactly one taxonomy stage and publication null; its logger writes diagnostics to stderr. `DRY_RUN` / `PLANNED` / `TAXONOMY_PENDING_MIGRATION` has verified sourceSha256/categoryCount but null importFingerprint and generationId because database configuration is unavailable before migration. Other non-null taxonomy payloads require a non-null import fingerprint. A failed taxonomy operation returns taxonomy null; argument/runtime construction failures may exit nonzero before any receipt, and the wrapper must handle that failure explicitly. COMMERCE-001 defines exact child validation and failure mapping. Commerce direct Node CLIs also emit one bounded stdout receipt and logger diagnostics on stderr. Do not scan stderr or embedded log text for a successful receipt. Exit nonzero on failure, retain earlier successful stages and mark later stages NOT_RUN. Reruns avoid duplicate active generations, tools, capabilities or releases. Receipts contain no API keys, source text, vectors, credentials, customer data or database connection strings. Readiness requires all four tools, a compatible active release and complete corpus; exit 0 alone is insufficient.

### 7.1 Exact submitted MCP taxonomy child receipt

The child has exactly one taxonomy stage and `publication: null`. Its `sourceSha256` and non-null category count must match the accepted production manifest for a full CLI import. The wrapper carries observed values; it does not fabricate fingerprints or generation IDs.

| Child mode/status/code | Taxonomy payload and exit | Wrapper treatment |
| --- | --- | --- |
| DRY_RUN / PLANNED / TAXONOMY_PENDING_MIGRATION | Verified source/count; importFingerprint null; generationId null; exit 0 | Preserve pending-migration planning and defer database-dependent prerequisites. |
| DRY_RUN / PLANNED / TAXONOMY_PREPARE_GENERATION | Non-null fingerprint; generationId current active ID or null; exit 0 | Preserve planned taxonomy work. |
| Either mode / UNCHANGED / TAXONOMY_IDENTICAL_ACTIVE | Non-null fingerprint and generationId; exit 0 | Preserve unchanged result. |
| APPLY / APPLIED / TAXONOMY_ACTIVATED | Non-null fingerprint and generationId; exit 0 | Preserve applied result. |
| Either mode / FAILED / actual source reason | taxonomy null; nonzero exit | Preserve source failure and earlier stages; later stages NOT_RUN. Map the exact child TAXONOMY_CONFIGURATION_MISSING reason to the established wrapper TAXONOMY_CONFIGURATION_UNAVAILABLE code, retaining the original source reason in diagnostics. |
| Early argument/runtime-construction failure | No receipt; nonzero exit | Fail explicitly under the child-error handling in COMMERCE-001; do not infer successful planning from stderr text or invent a receipt. |

## 8. Failure evidence and validation boundary

Use the existing Shared structured logger. Retain the original thrown provider/SDK error object, original message and safe provider response/status/request ID as allowed by current redaction rules, attached to semantic stage/reason/tenant correlation. Redact tokens, headers, connection strings, personal data and sensitive bodies; do not replace the original exception with only a generic log. No customer-visible stack traces or secrets. New runtime modules, script names and event names use semantic product/taxonomy terminology, not architecture IDs.

Each implementation task validates its owned boundary with the exact commands and executor stated in that task and `docs/agent-validation-execution-policy.md`. SYSTEM-TEST-001 exercises actual adapters, PostgreSQL17/pgvector, operator wrapper and public Commerce/MCP/Background composition with deterministic transport fixtures, without customer sends. It does not seed replacement tools/releases/response contracts or assume an unimplemented importer fixture API. Existing/future store access is exercised on provisioned Free/paid plans; fixture SQL is not claimed as an Admin plan-authoring end-to-end test. Exact provider semantics and the pinned Shopify query guard require composed adapter tests. Optional real-model quality evaluation is separate with a named model/corpus/version/budget and NOT_RUN/BLOCKED if absent. Scripted runner fixtures cannot certify multilingual semantic retrieval quality.

This definition amendment changes documentation only. Accepted Database/Shared/Shopify work is recorded in the execution baseline. Remaining importer/provider/setup/host implementation and runtime test evidence are produced by their assigned tasks; this patch does not claim to have executed them.
