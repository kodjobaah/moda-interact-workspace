# ARCH-058: Standard CommerceAgent product discovery, grounded responses and shipping information

**Status:** implementation in progress; revision 10 replaces the unexecuted Zod-pinning/hash-reconciliation plan with explicit no-hash contract corrections. MCP-001 is Complete at accepted Attempt 3. MCP-002 Attempt 1 is preserved but architecturally blocked until DATABASE-002 and SHARED-006 are Complete. The architecture is not complete.

## Current decision and patch scope

Preserve the accepted taxonomy, Database and useful Shared product/shipping/recommendation contracts. Remove the redundant built-in `contractHash` mechanism, remove the unused conversation-specific MCP context export, freeze the discount built-in timestamp wire syntax in Shared-owned code, forward-migrate persisted built-in grant JSON and publish the combined breaking Shared correction as approved target 5.0.0. Do **not** pin MCP, Commerce or Background to Zod 4.4.3 for ARCH-058. [Revision-10 reconciliation](ARCH-058/shared-hash-reconciliation.md) is the binding decision.

This revision uses `moda-interact-workspace(20261104-165221).zip` as the application/documentation baseline. It preserves all accepted task Completion/Architect Review history and all application source. The previously defined SHARED-003/004 revision-9 tasks were not materialised; their definitions are replaced before execution. New DATABASE-002, SHARED-005 and SHARED-006 definitions are portable and not materialised by this patch. Decision indexes remain untouched.

## Objective

Fifteen repository-owned tasks deliver standard product discovery, native shipping information and grounded response behavior, including the five corrective contract/migration/publication gates introduced by revision 10. The global reference taxonomy remains in PostgreSQL/pgvector; merchant product reads establish actual assortment; canonical discount options/details establish promotion facts for the proposed purchase. Commerce creates and publishes the four standard product/shipping tools for every otherwise authorized store, including Free plans and new stores. Admin's existing taxonomy implementation stays separate.

## Normative documents

- [Contracts](ARCH-058/contracts.md): wire shapes, responsibility boundaries, instruction ownership and corrected built-in identity.
- [Implementation handoff](ARCH-058/implementation-handoff.md): accepted source, current frontier and continuation requirements.
- [Execution baseline](ARCH-058/execution-baseline.json): historical publication receipt and current correction state.
- [Shared hash reconciliation](ARCH-058/shared-hash-reconciliation.md): reproduced failure and revision-10 no-hash decision; revision 9 remedy is superseded.
- [Original source-grounded review](reviews/commerce-agent-product-discovery-20261104-015544-r03/review.md): historical supporting evidence.

## Task graph and current frontier

| Task | Repository | Concrete responsibility | Prerequisites | Current state |
| --- | --- | --- | --- | --- |
| [DATABASE-001](../decisions/database/ARCH-058/DATABASE-001-persist-reference-taxonomy-and-core-product-discovery.md) | `moda-interact-database` | Accepted taxonomy schema, policy and original grant guard | - | Complete; historical baseline |
| [SHARED-001](../decisions/shared/ARCH-058/SHARED-001-define-product-discovery-and-recommendation-contracts.md) | `moda-interact-shared` | Accepted product/shipping/recommendation contracts and runner | - | Complete; historical baseline |
| [SHARED-002](../decisions/shared/ARCH-058/SHARED-002-publish-product-discovery-contracts.md) | `moda-interact-shared` | Historical immutable 4.0.0 publication | SHARED-001 | Complete; receipt preserved |
| [SHARED-003](../decisions/shared/ARCH-058/SHARED-003-remove-built-in-contract-hashes.md) | `moda-interact-shared` | Remove hash-based built-in identity | SHARED-002 | Complete; accepted Attempt 2 |
| [SHARED-004](../decisions/shared/ARCH-058/SHARED-004-remove-obsolete-conversation-tool-context.md) | `moda-interact-shared` | Remove obsolete MCP conversation-context export | SHARED-003 | Complete; accepted |
| [SHARED-005](../decisions/shared/ARCH-058/SHARED-005-freeze-commerce-datetime-wire-syntax.md) | `moda-interact-shared` | Freeze explicit discount built-in UTC timestamp syntax and bump both discount built-ins to 2.0.0 | SHARED-004 | Complete; accepted |
| [SHARED-006](../decisions/shared/ARCH-058/SHARED-006-publish-corrected-commerce-contracts.md) | `moda-interact-shared` | Publish/verify combined corrected package, target 5.0.0 | SHARED-003, SHARED-004, SHARED-005 | Complete; accepted |
| [DATABASE-002](../decisions/database/ARCH-058/DATABASE-002-remove-built-in-contract-hash-storage.md) | `moda-interact-database` | Forward-convert persisted built-in grants from hashed 1.0.0 to no-hash 2.0.0 identity | DATABASE-001, SHARED-005 | Complete; accepted |
| [MCP-001](../decisions/mcp/ARCH-058/MCP-001-import-and-resolve-postgresql-taxonomy.md) | `moda-interact-mcp` | Accepted importer, resolver and required-feature selection | DATABASE-001, SHARED-002 | Complete, Attempt 3 |
| [MCP-002](../decisions/mcp/ARCH-058/MCP-002-ground-merchant-products-and-discounts.md) | `moda-interact-mcp` | Preserve WIP; consume corrected Shared/Database and finish product/discount work | MCP-001, DATABASE-002, SHARED-006 | Complete; accepted |
| [SHOPIFY-001](../decisions/shopify/ARCH-058/SHOPIFY-001-enable-shipping-policy-read-scope.md) | `moda-interact` | Accepted native policy permission declaration | - | Complete |
| [MCP-003](../decisions/mcp/ARCH-058/MCP-003-read-merchant-shipping-information.md) | `moda-interact-mcp` | Native shipping reader | MCP-002, SHOPIFY-001 | Complete; accepted |
| [COMMERCE-001](../decisions/commerce/ARCH-058/COMMERCE-001-provision-standard-product-discovery.md) | `moda-interact-commerce` | Consume Shared 5.0.0; publish standard tools/instructions | MCP-002, MCP-003, SHARED-006 | Complete; accepted Attempt 3 |
| [BACKGROUND-001](../decisions/background/ARCH-058/BACKGROUND-001-ground-product-and-discount-recommendations.md) | `moda-interact-background` | Consume Shared 5.0.0; implement grounded host composition | MCP-002, MCP-003, COMMERCE-001, SHARED-006 | Ready; unclaimed, Attempt 0 |
| [SYSTEM-TEST-001](../decisions/system-test/ARCH-058/SYSTEM-TEST-001-validate-standard-product-discovery.md) | `moda-interact-system-test` | Verify corrected contracts, migration and integrated customer behavior | All required implementation/publication tasks | Pending |

Execution frontier: DATABASE, Shared, Shopify, MCP and Commerce prerequisites are Complete. BACKGROUND-001 is Ready/unclaimed after Commerce Attempt 3 acceptance; it must use normal launcher preparation when invoked. SYSTEM-TEST-001 remains Pending on Background acceptance and is a terminal, separately invoked validation task. Historical frontier snapshots below remain evidence, not current execution authority.

The prior revisions' product, shipping, instruction, grant and error-handling decisions below remain in force except where revision 10 explicitly replaces hash/Zod/context/package statements.

## Product and discount behavior

For a request such as “I want a hammer,” the agent can call `commerce_resolve_product_categories` with the customer's intent. MCP embeds that text with the pinned reference embedding configuration and returns a bounded ranked set of real taxonomy IDs and full paths from a complete PostgreSQL generation. Those candidates establish product meaning. They do not establish that the current shop carries hammers.

The agent then calls `commerce_search_products` for the authenticated shop, using useful text and, where supported, a verified native category filter. Exact product reads confirm relevant product/variant identity, availability, price and currency when known. A taxonomy match without merchant products produces no stock claim. An ambiguous request can lead to a clarification; a temporarily unavailable optional taxonomy lookup can lead to ordinary merchant text search. MCP retains hard shop/data authorization and malformed-result errors. Background owns stale-turn/lease/control failures and its terminal response behavior.

The model receives trusted `commerceProvider` (SHOPIFY or WOOCOMMERCE) from the already-read current `Shop.platform`. Shopify's reference IDs are not WooCommerce shop category IDs. Shopify category filtering uses the provider's documented products path; Woo begins with real product text unless a current-shop native ID has already been observed; its filter uses `WOOCOMMERCE_PRODUCT_CATEGORY` with null taxonomyVersion and verifies exact assigned membership after bounded provider reads. An absent/invalid provider context uses direct text search, never inferred routing from domain, customer text or an ID. The first increment does not introduce descendant expansion, arbitrary SQL, a merchant product mirror or a cross-platform guessed ID map.

When recommending a product, Background reads the current merchant discount policy and controls use of the accepted `commerce_get_discount_options`/`commerce_get_discount_details` flow. `NONE` produces no promotional lookup or claim. `FIXED` respects the current permitted selection/override. `AI_BEST_APPLICABLE` reads the permitted canonical catalogue. The host checks conditions for each proposed product, real variant or null Woo simple-product variant, explicit quantity, current purchase scope and known currency. Do not treat the three suggested alternatives as one qualifying basket.

Every product search mode and exact refresh applies private publication qualification before public mapping: Shopify ACTIVE plus a safe storefront URL; Woo published parent/selected variation with the mode-specific permitted catalog visibility. Woo availability combines the selected source's purchasable/stock facts; stock alone does not prove buyability. Known ineligibility skips/nulls, malformed required qualifiers remain hard errors, and availableOnly:false cannot bypass publication. The public product schema stays unchanged.

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

MCP reads the existing `REFERENCE_TAXONOMY` embedding configuration using the correct purpose/AAD. It does not update that configuration or operate Admin's Redis index. The archived Admin manifest/pipeline and the user-reported MCP-001 source check are recorded separately in the handoff. Remaining tasks reuse MCP-001's accepted manifest/CLI/verified asset and never open a second release-selection/importer task. A supplied local file must match the accepted distribution-byte checksum; compressed and derived files are not interchangeable.

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

The MCP taxonomy CLI is present in the submitted worktree; its acceptance remains pending. The Commerce setup/publication changes are future implementation work. The wrapper validates selected repository identities/environment, then invokes Database migration, the accepted MCP importer and Commerce publication in order. A schema-empty target defers database-dependent configuration/actor checks until after migration; missing prerequisites produce explicit partial-failure receipts and a rerun resumes after existing configuration workflows supply them. An optional staged source file must match the approved manifest bytes. Production retains the explicit confirmation flag. Dry-run does not mutate state, publish, create audit entries or call the paid embedding API.

After validated receipt-context initialization, the owning CLI emits exactly one stage receipt, stops on failure, reports completed stages and can be rerun safely. Invalid invocation or earlier initialization/bundling/import failure has nonzero exit, safe original stderr diagnostics and no receipt; outer wrappers never fabricate or duplicate one. The setup parent rejects missing/multiple/malformed/exit-inconsistent child receipts. Publication preserves unrelated release pins, feature prompts and response fields, uses ownership/content checks and a pointer compare-and-swap, and reports all four standard tools. It does not silently migrate retained conversation grants. Use fresh pre-production test conversations or an explicitly reviewed transition after a compatible rollout.

## Important boundaries

The approved design uses the existing feature, selection, system publication, discount facts, logger and host mechanisms. It adds only the contracts and adapters needed to connect them. The database migration must account for the current JSON shape guard and release-membership insert trigger when introducing built-in grant entries; merely changing the TypeScript type would fail at persistence.

Original provider/SDK errors, messages and safe response details must survive through Shared structured logs with current redaction. Missing credentials, a provider error, invalid generated embeddings and a stale grant must be diagnosable without leaking secrets or customer data. Tests distinguish permitted optional lookup degradation from hard failures; a blanket empty-success catch is not acceptable.

No changes are planned to Admin taxonomy readers/scripts/UI/indexes, Redis availability for Admin, the existing discount policy model, cart/coupon mutations, prior migration files, accepted ARCH-052 histories, unrelated ARCH-053/055/056/057 work, or any `docs/decisions/**/_index.md`. New runtime files and log events use semantic names rather than architecture numbers.

## Acceptance and evidence

Individual tasks specify their repository tests and exact completion-report requirements. The integrated suite must demonstrate a clean and upgraded PostgreSQL17/pgvector setup, repeat execution, failed-stage recovery, restart/restore, atomic generation/configuration behavior, all-store capability availability, tenant/provider/category/cursor correctness, current policy and exact-purchase discount checks, full controlled-response grounding, shipping policy/variant/permission semantics, unsupported-question fallback, supported-language composition, whole-wrapper bounds and redacted original-error evidence. Tests exercise real adapters and schema guards with deterministic fixtures; they do not send customer messages.

An optional real-model evaluation separately measures semantic retrieval and clarification/relevance across the supported languages under a named model/corpus/budget. A scripted model or fixture transport cannot certify real-model semantic quality. Missing optional evaluation is explicitly NOT_RUN/BLOCKED, never reported as passed.

For Attempt 6, validation checks all ten task routes/metadata/dependencies, local links, the exact ten-document patch scope, unchanged completed records and MCP-001 report/review bytes, unchanged indexes and application files, strict `git apply --check --whitespace=error-all`, actual application, `git diff --check`, reverse checks and actual byte-restoring reverse application against a fresh extraction of the current MCP-001 upload. Earlier 094947 evidence is retained with an explicit source label. Runtime tests reported by the implementer are not rerun or claimed as newly executed by this documentation review.

## Attempt 3 definition review

Reviewed design changes: the existing hard-referral path discards product details; search previously required a query/category; product outputs omit shipping facts; Shopify policy permission is absent from deployable app scopes; MCP's session reader currently projects token without scope; and Woo product projections omit shipping fields/measurement units. The tasks now assign each gap to an existing repository owner with explicit producer/consumer contracts. Scope checks reuse existing offline Session storage and generic authenticated scope persistence. No additional Database, Admin, API, Gateway or Messaging task is needed for the defined first increment. Concurrent ARCH-057 scope/session changes must be reconciled at materialisation, without reopening or duplicating their implementation.

Primary provider references: [Shopify Admin ShopPolicy](https://shopify.dev/docs/api/admin-graphql/2026-07/objects/ShopPolicy), [InventoryItem](https://shopify.dev/docs/api/admin-graphql/2026-07/objects/InventoryItem), [Woo products](https://developer.woocommerce.com/docs/apis/rest-api/v3/products/) and [Woo variations](https://developer.woocommerce.com/docs/apis/rest-api/v3/product-variations/). Native policy absence is not a shipping quote. This review is static against the uploaded source, not proof of installed permissions, provider execution or deployed behavior.

## Attempt 4 remaining-task review

The review corrected concrete implementation gaps: stale release selection; missing accepted discount source integration; category/browse pagination and private Woo allowlists; a conversation-context ownership proposal subsequently withdrawn in Attempt 5; paired shipping permission reads; publication changes to owned response instructions; fresh-schema setup prerequisites and stdout receipts; actual Background prompt/policy/basket projections; one shared finalization budget; host test discovery; and SystemTest fixtures that would overwrite the real published release. Each is assigned to one of the five existing pending owners with exact touchpoints, outcomes and commands in its task. No additional Database, Shared, Admin or taxonomy redesign is introduced.

Natural-language intent and relevance remain model behavior. Trusted feature instructions direct bounded discovery and discount checks; the host validates selections, source facts, current policy and output. Missing or invalid selections produce the verified store-link fallback. Scripted integration fixtures demonstrate this control flow and the deterministic host guarantees, not real-model semantic quality or live merchant deployment.

## Attempt 5 MCP responsibility correction

MCP is the generic tool provider and executor. The earlier proposal for an MCP conversation context, conversation/grant database reads, lease/control validation and retained-grant-specific listing is withdrawn. Background owns those workflow checks. MCP enforces current shop/plan/connection/data access, validates tool inputs, performs the selected reads and returns facts. The existing discount result's configured shop mode and permitted catalogue remain legitimate tool data; MCP does not choose how a customer conversation uses them.

The standard Background client sends only `{shopId}` after local assertion validation. MCP advertises stable canonical discount descriptors for an otherwise authorized shop. Background persists the full validated descriptor set for new conversation grants and uses current policy to expose/execute tools, with existing exact manifest equality and current-turn checks. Generic optional data unavailability has one provider meaning; caller-specific continuation belongs in Background. No new Shared release, Database migration or change to active MCP-001 is introduced. Contracts section 4.1 and the implementation handoff define this boundary; the pending tasks name its exact files and tests.

## Attempt 6 current-worktree reconciliation

The uploaded MCP-001 task is review/Attempt 2 and its taxonomy implementation uses only generic shop/published-definition/RPC checks. `WorkContext` carries AbortSignal, deadline and provider-request budget; it contains no conversation identity or retained grant. The clarified task removes ambiguous grant/stale-invocation wording without restarting valid importer work. Its submitted integration report records 25 passes and one opt-in live skip; this amendment preserves that report and does not independently accept it.

MCP-002's former section “One domain authorization read for conversation discounts” and its dependent reader/module/test requirements are withdrawn. Generic shop descriptors and catalogue execution replace them; Background alone owns workflow permission and retained state. The actual current catalogue factory, execution port and query boundaries now anchor those changes. The current MCP CLI also anchors the Commerce child receipt: one stdout receipt, one taxonomy stage, and a null import fingerprint only for pending-migration dry-run planning.

SHARED-004 removes the previously published unused `CommerceConversationToolContextSchema` and type. The corrected design still preserves Background/runner conversation contracts and the separately accepted outreach tool context. No conversation-specific replacement is added to MCP.

## Architect Acceptance Reconciliation (2026-11-04)

MCP-001 Attempt 3 is accepted and Complete at `1dd5430b9d3108bf93bba86c1fb9233736f606d3`; its task contains the authoritative review and validation limits. Earlier review/Attempt 2 snapshots above are historical. MCP-002 subsequently entered Attempt 1 and preserved its WIP source; revision 10 blocks continuation on DATABASE-002 and SHARED-006. SYSTEM-TEST-001 remains pending on the remaining implementations; the architecture is not yet Implemented. No persistent import, deployment or publication is certified by task acceptance.

## Shared Hash Removal Acceptance (2026-11-04)

SHARED-003 Attempt 2 is architect-accepted and Complete at `59ea61f34197d64180e46680ac6d552b5e989a36`. Its provenance correction closes the prior documentation finding; implementation and prior independent validation are unchanged. Earlier unmaterialised/ready references are historical. SHARED-004 is now ready and unclaimed. SHARED-006 remains pending on SHARED-004/005; the intermediate source must not be published. Remaining architecture and system-test gates are unchanged.


## Commerce prerequisite reconciliation — 5 November 2026

COMMERCE-001 Attempt 1 preserved its unfinished draft at `0914178` and stopped at a historical Database task-commit ancestry check. The complete tree of `ded8f14a` equals accepted squash merge `395675f`; the accepted Database pin `bd2d090` descends from that merged commit and retains DATABASE-002. Revision 11 uses the merged ancestor, preserves the immutable original Shared 2.7.2 tool fixture, and returns Commerce Ready/unclaimed with Attempt 1 retained. This is prerequisite reconciliation, not implementation acceptance. Background owns downstream model-request instruction/context fixtures; Commerce owns publisher/Shared-parser proof. No reverse dependency, source edit, deployment or downstream execution is authorized by the reconciliation.


## Commerce acceptance and Background frontier — 5 November 2026

COMMERCE-001 Attempt 3 is accepted and Complete at `58f5418`, with the process-group timeout/overflow correction, independent 7-test setup regression proof, reviewed 149-test fast-check submission, passing developer-authorized build and migrated PostgreSQL proof (1/1, exit 0, zero owned-container leftovers). The immutable legacy fixture, accepted Database pin and Shared 5.0.0 remain preserved. BACKGROUND-001 is Ready/unclaimed, Attempt 0, because every explicit prerequisite is Complete. SYSTEM-TEST-001 remains Pending until Background is accepted. No downstream execution, merge, deployment or architecture-wide completion is implied.

## Cursor removal amendment — 2026-11-05 (ARCH-058-COMMERCE-002)

Developer decision: remove Moda cryptographic cursor validation, query/policy binding, expiry enforcement and COMMERCE_CURSOR_SECRET dependency. Preserve bounded position parsing, provider cursors, authenticated current-shop authorization, current policy, query parameterization and limits. This overrides earlier signed/encrypted cursor requirements, including MCP-002. No credential-encryption change. Internal pre-production legacy cursors restart from null; no signature/decryption compatibility path. Both repository tasks are independently Ready: ARCH-058-MCP-004 (private MCP search/catalogue) and ARCH-058-COMMERCE-002 (local preview). Only this branch materialises ARCH-058-COMMERCE-002; integrate both definitions before cross-repository rollout. No infrastructure task is required: inspected Gateway Blueprints contain no cursor-secret declaration. Repository docs/config cleanup belongs to each task. No new telemetry mechanism is needed; retain existing safe diagnostics. Required terminal product-discovery certification remains manual-gated.
