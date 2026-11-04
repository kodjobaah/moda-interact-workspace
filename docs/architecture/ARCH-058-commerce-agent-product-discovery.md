# ARCH-058: Standard CommerceAgent product discovery, grounded responses and shipping information

**Status:** task definitions for implementation; not implemented or deployed. 4 November 2026.

## Decision

Create ten repository-owned tasks to make product discovery and basic native shipping information standard CommerceAgent capabilities, with explicit grounded fallback responses. Use a global reference taxonomy in PostgreSQL/pgvector to interpret a product request, current merchant product reads to establish what the shop actually sells, and the canonical discount options/details flow to check promotions against the exact proposed purchase. Automatically create and publish the four standard product/shipping tools for every otherwise authorized store, including Free plans and new stores.

The required operator workflow is repeatable: migrate the database, import and activate the approved taxonomy generation, then publish the owned Commerce definitions/behavior/response fields. Admin's current Redis taxonomy implementation stays separate and intact.

Attempt 3 is prepared against the uploaded `moda-interact-workspace(20261104-035517).zip`, which already contains revision03's review and source-baseline evidence. It extends the eight unstarted Attempt 2 definitions and adds MCP-003 and SHOPIFY-001. The complete replacement patch applies to that exact uploaded baseline without an earlier task-definition patch; the separately validated update patch applies to that baseline plus the exact Attempt 2 patch. Both routes produce identical ARCH-058 documents. Neither patch recreates or edits the existing revision03 files. If task execution/lifecycle fields or these definitions have changed since Attempt 2, reconcile the actual current files instead of overwriting task history. ARCH-057 remains the separate Shopify application review. This is still task definition, not runtime implementation.

## Source and governing documents

- [Source-grounded review, revision03](reviews/commerce-agent-product-discovery-20261104-015544-r03/review.md), including its evidence table and explicit unverified deployment assumptions.
- [Source-baseline hashes](reviews/commerce-agent-product-discovery-20261104-015544-r03/source-baseline.json).
- [Frozen interfaces and execution behavior](ARCH-058/contracts.md), normative for the tasks below.
- [Task definition and materialisation](../task-definition-materialization.md), [developer task workflow](../developer-task-workflow.md), [worktree isolation](../agent-worktree-isolation-policy.md), [VCS ownership](../agent-vcs-ownership-policy.md) and [Shared logging](../observability/shared-logging.md).

Snapshot facts are not claims about the user's current running environment. Accepted source must be reconciled at materialisation, especially accepted ARCH-052 discount work and concurrent Background/Shopify work. Do not reopen accepted task statuses just because the source snapshot exposes a missing or stubbed path.

## Tasks and deliverables

| Task | Repository | Main deliverable | Prerequisites | Initial status |
| --- | --- | --- | --- | --- |
| [DATABASE-001](../decisions/database/ARCH-058/DATABASE-001-persist-reference-taxonomy-and-core-product-discovery.md) | `moda-interact-database` | Forward taxonomy/schema migration, required `product_search` policy and targeted existing/future plan mappings; grant JSON guard update | None | ready |
| [SHARED-001](../decisions/shared/ARCH-058/SHARED-001-define-product-discovery-and-recommendation-contracts.md) | `moda-interact-shared` | Category/search/browse/shipping schemas, built-in identities/grants, trusted conversation context, optional lookup outcome and typed answer presentation; runner integration | None | ready |
| [SHARED-002](../decisions/shared/ARCH-058/SHARED-002-publish-product-discovery-contracts.md) | `moda-interact-shared` | Publish the accepted exact Shared package and verify registry artifact | SHARED-001 | pending |
| [MCP-001](../decisions/mcp/ARCH-058/MCP-001-import-and-resolve-postgresql-taxonomy.md) | `moda-interact-mcp` | Approved source manifest, repeatable importer, PostgreSQL category resolution and always-enabled feature eligibility | DATABASE-001, SHARED-002 | pending |
| [MCP-002](../decisions/mcp/ARCH-058/MCP-002-ground-merchant-products-and-discounts.md) | `moda-interact-mcp` | Current-shop category/product/browse reads, visibility/pagination/currency correctness; canonical conversational discounts | MCP-001 | pending |
| [SHOPIFY-001](../decisions/shopify/ARCH-058/SHOPIFY-001-enable-shipping-policy-read-scope.md) | `moda-interact` | Add `read_legal_policies` to deployable app configurations, verify runtime SCOPES/actual grants and document rollout | None | ready |
| [MCP-003](../decisions/mcp/ARCH-058/MCP-003-read-merchant-shipping-information.md) | `moda-interact-mcp` | Fixed native shipping reads, paired offline scope preflight, normalized variant facts and bounded policy data | MCP-002, SHOPIFY-001 | pending |
| [COMMERCE-001](../decisions/commerce/ARCH-058/COMMERCE-001-provision-standard-product-discovery.md) | `moda-interact-commerce` | Automatic creation/versioning/publication of four standard tools and owned behavior/response fields; one environment setup command | MCP-002, MCP-003 | pending |
| [BACKGROUND-001](../decisions/background/ARCH-058/BACKGROUND-001-ground-product-and-discount-recommendations.md) | `moda-interact-background` | Trusted context, grounded recommendations and limitation responses, shipping presentation, final revalidation and localized host composition | MCP-002, MCP-003, COMMERCE-001 | pending |
| [SYSTEM-TEST-001](../decisions/system-test/ARCH-058/SYSTEM-TEST-001-validate-standard-product-discovery.md) | `moda-interact-system-test` | Integrated provision/restart/restore, all-store access, product/shipping/discount authorization, fallback composition and failure-evidence tests | All nine implementation/publication tasks | pending |

Shared implementation and Shared publication are deliberately separate because consumers must install a verified published package. Three MCP tasks separate corpus lifecycle/retrieval, merchant product/discount execution and the independently reviewable shipping reader with its distinct permission and absence semantics. The setup wrapper belongs to Commerce, which already owns system-tool publication; no additional parent-workspace, Gateway or Admin implementation task is needed.

All task definitions use attempt 0, null executor/claim and the normal ready/pending states. They are **defined but not materialised**. Creating these documents does not create implementation worktrees, branches, a release, a database migration, a seed/import script or a deployed feature.

## Execution order

Database, Shared contract implementation and Shopify permission setup can begin in parallel. Once Shared implementation is architect-accepted, publish the exact package. MCP taxonomy work begins after both the Database contract and Shared publication are complete. Then execute merchant product/discount/browse integration. Shipping reads follow MCP-002 and Shopify permission setup; Commerce provisions all four capabilities after shipping execution exists. Background composes the responses after publication, and system tests validate the complete implementation.

```mermaid
flowchart TD
  D["Database migration and policy"] --> M1["MCP taxonomy import and resolution"]
  S1["Shared implementation"] --> S2["Shared publication"]
  S2 --> M1
  M1 --> M2["MCP products, browse and discounts"]
  M2 --> M3["MCP shipping reads"]
  P["Shopify policy permission"] --> M3
  M3 --> C["Commerce provisioning"]
  C --> B["Background grounded responses"]
  M3 --> B
  B --> T["Integrated system tests"]
```

The system-test task formally depends on every preceding task even though the diagram shows the final chain for readability. Each task returns to the architect for acceptance before its dependent frontier is promoted. Do not merge, publish or deploy merely because a task definition is marked ready.

## Product and discount behavior

For a request such as “I want a hammer,” the agent can call `commerce_resolve_product_categories` with the customer's intent. MCP embeds that text with the pinned reference embedding configuration and returns a bounded ranked set of real taxonomy IDs and full paths from a complete PostgreSQL generation. Those candidates establish product meaning. They do not establish that the current shop carries hammers.

The agent then calls `commerce_search_products` for the authenticated shop, using useful text and, where supported, a verified native category filter. Exact product reads confirm relevant product/variant identity, availability, price and currency when known. A taxonomy match without merchant products produces no stock claim. An ambiguous request can lead to a clarification; a temporarily unavailable optional taxonomy lookup can lead to ordinary merchant text search. Hard authorization, stale-turn and malformed-result errors retain their existing terminal behavior.

Shopify's reference IDs are not WooCommerce shop category IDs. Shopify category filtering uses the provider's documented products path; Woo filtering uses a native shop category and verifies exact assigned membership after bounded provider reads. The first increment does not introduce descendant expansion, arbitrary SQL, a merchant product mirror or a cross-platform guessed ID map.

When recommending a product, read the current merchant discount policy and use the accepted `commerce_get_discount_options`/`commerce_get_discount_details` flow. `NONE` produces no promotional lookup or claim. `FIXED` respects the current permitted selection/override. `AI_BEST_APPLICABLE` reads the permitted canonical catalogue. The host checks conditions for each proposed product, real variant or null Woo simple-product variant, explicit quantity, current purchase scope and known currency. Do not treat the three suggested alternatives as one qualifying basket.

The model selects observed IDs; it does not author trusted prices or calculate promotions. The host rechecks selected products and conditions in finalization and composes the full recommendation from validated data in the current conversation language. Unknown, stale, incomplete, unauthorized or unsupported conditions produce no asserted saving. Current observed facts are not a provider redemption guarantee. Existing admission, takeover, language, moderation and delivery processing stay in control.

## Response behavior and shipping information

The agreed customer behavior is a truthful limitation followed by useful merchant information. An unrelated question such as weather receives a concise store-scope response plus at most one verified product and any currently permitted applicable promotion. With no supported promotion, show the product without asserting that the merchant has no discounts. With no verified product, show the verified store link. Product context comes from the customer's conversation, refreshed owned basket or explicit bounded catalogue browse; an unrelated place name never becomes a shipping destination. Do not call a suggestion similar, featured or a bestseller without the relevant evidence.

A shipping knowledge gap first uses the relevant authorized sources when available. Existing Merchant Knowledge remains optional and separately entitled. The new native reader can obtain Shopify's published shipping policy and basic provider product/variant attributes without requiring the merchant to upload a knowledge document. Woo's first increment reads product attributes; native general policy is explicitly unsupported, with existing approved Merchant Knowledge remaining available when granted. Do not guess WordPress page slugs or introduce an extra knowledge configuration UI.

Shipping metadata, written policy and basket/destination-specific quotes are different sources. This increment introduces no live quote, cart creation/update, zones-based price reconstruction or promised ETA. Unknown Woo measurement units and variant shipping requirements remain unknown. A similar product does not resolve an unknown delivery cost or time. Future quote work is captured in [the separate design follow-up](ARCH-058/shipping-quote-follow-up.md), which is not an executable repository task or an ARCH-058 acceptance dependency.

The response contract adds a bounded disposition within ordinary `ANSWER` details: STANDARD, OUT_OF_SCOPE_REDIRECT or SHIPPING_INFORMATION_UNVERIFIED. It leaves the terminal REFER_TO_STORE envelope intact. Background latches controlled composition when recommendation/product/discount work, product-bearing shipping reads or owned presentation fields are involved; omitted details cannot bypass the validator. The model selects observed identifiers. Background composes the fixed limitation, source link, validated product/offer and link using the current language and whole wrapped-message limit. Positive shipping-plus-product messages use only the typed shipping requirement and verified policy link; raw model policy summaries are not concatenated to a validated recommendation. Ordinary policy-only grounded answers retain the existing non-recommendation path. Contracts sections 2.3 and 5.1 are normative.

The four published tools are commerce_resolve_product_categories, commerce_search_products, commerce_get_product and commerce_get_shipping_information. Search gains an explicit browse flag with bounded visibility checks and mode-bound cursors. Get/search product outputs stay unchanged; shipping has its own typed output and fixed operation. Commerce publishes the corresponding nonempty owned response instructions and verifies all four tools in receipts and repeat runs.

Shopify's read_legal_policies permission is declared by its owning application task. MCP reads actual persisted offline scope with the corresponding token and checks before requesting policy data. Missing policy scope is an expected tool-data result; an attempted query's authentication/provider failure is an error. Declaring or publishing the feature never creates a merchant's permission. Product reads keep their existing read_products access. Existing Session.scope is sufficient; shipping adds no database migration or policy mirror.

## Durable taxonomy and operational setup

The new reference corpus is global per environment/source/language and lives in separate PostgreSQL tables with complete immutable generations, versioned source/checksum and embedding tuple. A validated candidate is prepared outside the final transaction. A per-corpus lock and embedding-configuration row lock protect atomic activation. Failed imports leave the old generation usable; exact reruns are no-ops; conflicting concurrent generations cannot overwrite one another silently. A runtime query pins one complete generation through embedding and retrieval. PostgreSQL restart and restore are integrated acceptance cases.

MCP reads the existing `REFERENCE_TAXONOMY` embedding configuration using the correct purpose/AAD. It does not update that shared configuration or operate Admin's Redis taxonomy index. The uploaded archive includes a pinned source manifest, not the corpus bytes or a verified checksum/count. Obtaining and validating those real bytes is an explicit MCP-001 work item; task definitions must not invent taxonomy IDs or counts.

The concrete implementation paths are:

| Deliverable | Task |
| --- | --- |
| `moda-interact-database/prisma/migrations/20261104120000_reference_taxonomy_and_core_product_discovery/migration.sql` | DATABASE-001 |
| Targeted canonical seed-policy alignment, without running the destructive broad seed against an existing environment | DATABASE-001 |
| `moda-interact-mcp/src/data/reference-taxonomy-manifest.json` | MCP-001 |
| `moda-interact-mcp/scripts/sync-reference-taxonomy.mjs` and `npm run taxonomy:sync` | MCP-001 |
| Extended `moda-interact-commerce/scripts/sync-system-commerce-tools.mjs` and existing `npm run commerce:sync-tools` | COMMERCE-001 |
| `moda-interact-commerce/scripts/setup-commerce-product-discovery.mjs` and `npm run commerce:setup-discovery` | COMMERCE-001 |

After these tasks are implemented and compatible runtime versions are available, an operator runs the following from the accepted Commerce checkout, supplying the actual workspace root:

```bash
npm run commerce:setup-discovery -- \
  --workspace-root="$MODA_WORKSPACE_ROOT" \
  --environment=test \
  --dry-run

npm run commerce:setup-discovery -- \
  --workspace-root="$MODA_WORKSPACE_ROOT" \
  --environment=test \
  --apply
```

These are future implementation commands; the scripts do not exist merely because this task bundle is applied. The wrapper validates the selected repository identities/environment, then invokes the Database migration path, MCP importer and Commerce publisher in order. An optional staged source file must match the approved manifest bytes. Production retains the existing explicit confirmation flag. Dry-run does not mutate state, publish, create audit entries or call the paid embedding API.

The wrapper emits a stage receipt, stops on failure, reports the completed stages, and can be rerun safely. Publication preserves unrelated release pins, feature prompts and response fields, uses ownership/content checks and a pointer compare-and-swap, and reports all four standard tools. It does not silently migrate retained conversation grants. Use fresh pre-production test conversations or an explicitly reviewed transition after a compatible rollout.

## Important boundaries

The approved design uses the existing feature, selection, system publication, discount facts, logger and host mechanisms. It adds only the contracts and adapters needed to connect them. The database migration must account for the current JSON shape guard and release-membership insert trigger when introducing built-in grant entries; merely changing the TypeScript type would fail at persistence.

Original provider/SDK errors, messages and safe response details must survive through Shared structured logs with current redaction. Missing credentials, a provider error, invalid generated embeddings and a stale grant must be diagnosable without leaking secrets or customer data. Tests distinguish permitted optional lookup degradation from hard failures; a blanket empty-success catch is not acceptable.

No changes are planned to Admin taxonomy readers/scripts/UI/indexes, Redis availability for Admin, the existing discount policy model, cart/coupon mutations, prior migration files, accepted ARCH-052 histories, unrelated ARCH-053/055/056/057 work, or any `docs/decisions/**/_index.md`. New runtime files and log events use semantic names rather than architecture numbers.

## Acceptance and evidence

Individual tasks specify their repository tests and exact completion-report requirements. The integrated suite must demonstrate a clean and upgraded PostgreSQL17/pgvector setup, repeat execution, failed-stage recovery, restart/restore, atomic generation/configuration behavior, all-store capability availability, tenant/provider/category/cursor correctness, current policy and exact-purchase discount checks, full controlled-response grounding, shipping policy/variant/permission semantics, unsupported-question fallback, supported-language composition, whole-wrapper bounds and redacted original-error evidence. Tests exercise real adapters and schema guards with deterministic fixtures; they do not send customer messages.

An optional real-model evaluation separately measures semantic retrieval and clarification/relevance across the supported languages under a named model/corpus/budget. A scripted model or fixture transport cannot certify real-model semantic quality. Missing optional evaluation is explicitly NOT_RUN/BLOCKED, never reported as passed.

For this task-definition deliverable, validation consists of canonical task metadata/routes, complete dependency graph, matching enables, source-relative links, untouched original files/indexes, strict `git apply --check --whitespace=error-all`, applied `git diff --check`, and reverse-apply verification. No runtime, importer, migration or provider test is claimed until the corresponding implementation task executes.

## Attempt 3 definition review

Reviewed design changes: the existing hard-referral path discards product details; search previously required a query/category; product outputs omit shipping facts; Shopify policy permission is absent from deployable app scopes; MCP's session reader currently projects token without scope; and Woo product projections omit shipping fields/measurement units. The tasks now assign each gap to an existing repository owner with explicit producer/consumer contracts. Scope checks reuse existing offline Session storage and generic authenticated scope persistence. No additional Database, Admin, API, Gateway or Messaging task is needed for the defined first increment. Concurrent ARCH-057 scope/session changes must be reconciled at materialisation, without reopening or duplicating their implementation.

Primary provider references: [Shopify Admin ShopPolicy](https://shopify.dev/docs/api/admin-graphql/2026-07/objects/ShopPolicy), [InventoryItem](https://shopify.dev/docs/api/admin-graphql/2026-07/objects/InventoryItem), [Woo products](https://developer.woocommerce.com/docs/apis/rest-api/v3/products/) and [Woo variations](https://developer.woocommerce.com/docs/apis/rest-api/v3/product-variations/). Native policy absence is not a shipping quote. This review is static against the uploaded source, not proof of installed permissions, provider execution or deployed behavior.
