# ARCH-058 follow-up: basket and destination shipping quotes

Status: separate design follow-up; **not an executable repository task**, not part of the ten-task first increment, and not an acceptance dependency. 4 November 2026.

Parent: [ARCH-058](../ARCH-058-commerce-agent-product-discovery.md). First-increment contract: [native shipping information](contracts.md#23-native-shipping-information).

## Intended outcome

When a customer asks for the cost or available delivery options for a specific purchase, obtain a provider-calculated estimate for that exact basket and destination. Report supported delivery estimates with their source and limitations. Keep the customer's existing basket unchanged unless a separately authorized action expressly requires a change.

The current first increment can read product attributes and written policy. It cannot derive a current quote from a category, weight, a shipping-class label or an arbitrary configured flat rate. A policy statement is not a current customer-specific price.

## Why implementation tasks are not yet ready

The inspected recovery context does not establish that a recovered Shopify checkout identifier is a Storefront Cart ID or that a server-side Woo request shares the customer's active cart session. The existing product connection is read-oriented. Live quotes may need explicit cart/session creation or destination updates, with different permissions and lifecycle ownership. These are concrete contract choices that must be frozen before implementation, rather than left to repository agents.

This document does not reserve a new architecture ID or authorize a cart mutation. No executable task with an invented dependency or blocked lifecycle state is created merely to hide these choices.

## Required decisions before task decomposition

1. **Quote context ownership.** Identify the existing authorized cart/session that can be read, or define an isolated quote context with an explicit lifecycle and no effect on the customer's saved/recovered basket. Decide which repository owns that context and whether any durable state is necessary. Use current inspected source; do not introduce a new table by default.
2. **Provider identity.** Specify exactly how Shopify Storefront Cart IDs and Woo cart sessions/tokens are obtained and bound to shop/conversation/customer. Never reinterpret checkoutRecoveryId, a recovery URL secret, an outreach attempt or a checkout token as a provider cart ID. Cart identifiers/secrets remain trusted adapter data, not arbitrary model arguments or log fields.
3. **Read versus mutation.** Classify each provider request. Reading options, creating a quote cart, adding/removing items, updating a destination and selecting an option are distinct actions. Define explicit tool/grant permissions and customer-intent boundaries; do not broaden current read-only grants implicitly. Background continues to use MCP, not direct provider HTTP.
4. **Purchase and destination contract.** Pin exact current product/variant IDs, quantities and purchase scope; establish currency/market context where required. Destination comes from explicit customer input or an authorized current source, with provenance. Ask only for necessary missing address fields. A place name in an unrelated weather question is never a destination.
5. **Complete provider result.** Preserve shipping packages/delivery groups and distinguish available versus selected options. Define how deferred carrier-calculated rates, asynchronous rates, partial options and unsupported extensions are represented. State tax inclusion and currencies explicitly where known; never add one package's cost and call it the complete order quote.
6. **Offers and totals.** Use the canonical permitted discount mechanism and exact quote context. A free-shipping code does not itself prove destination eligibility. Define whether an estimate includes offers/tax and when the provider can verify them, without implementing a second discount or shipping calculator.
7. **Absence, failure and freshness.** Separate no shipping needed, no eligible service, missing context, incomplete quote, optional operational unavailability and actual authorization/provider errors. Establish observation/version context and revalidation at the relevant customer action. A provider estimate must not become a guaranteed arrival date or an immutable price.
8. **Publication and deployment.** Freeze versioned Shared contracts first, then provider/runtime owners, authorization/provisioning consumers, host output and terminal system tests. Identify actual new scopes/grants or app configuration work. Reuse existing task/publication/logging mechanisms, not a speculative quote microservice.

## Provider evidence already available

- [Shopify Storefront Cart, 2026-07](https://shopify.dev/docs/api/storefront/2026-07/objects/Cart): delivery groups depend on address context; carrier rates are excluded by default and require withCarrierRates plus deferred-response support.
- [Shopify CartDeliveryGroup](https://shopify.dev/docs/api/storefront/2026-07/objects/CartDeliveryGroup) and [CartDeliveryOption](https://shopify.dev/docs/api/storefront/2026-07/objects/CartDeliveryOption): preserve group boundaries and estimated costs. The inspected option type has no dedicated guaranteed arrival-date field.
- [Shopify cart management](https://shopify.dev/docs/storefronts/headless/building-with-the-storefront-api/cart/manage): current cart identity and cart operations are separate from recovery identifiers.
- [Woo Store API Cart](https://developer.woocommerce.com/docs/apis/store-api/resources-endpoints/cart/): calculated shipping rates are returned per package for the current cart; cart-changing POST operations are distinct from GET.
- [Woo Cart Tokens](https://developer.woocommerce.com/docs/apis/store-api/cart-tokens): session identification is required to operate on the intended cart; a generic server call is not evidence of the customer's cart.
- [Woo delivery-time support](https://developer.woocommerce.com/2025/02/25/woocommerce-9-7-smarter-shipping-displays-and-faster-performance/): extensions may supply delivery_time; an empty value is unknown.

These are official API capabilities, not evidence that the current Moda integration has implemented them or obtained the required context/permissions. Recheck the actual pinned provider API and accepted source when this follow-up begins.

## Definition exit criteria

The follow-up is ready for repository task generation when the chosen cart/context and permission model is explicit, every operation has an owner, exact Shared input/result/failure contracts are frozen, and the implementation/publication dependency set is complete. The resulting integration tests must cover destination changes, exact variants/quantities, multiple packages, partial/deferred carrier rates, no service, unknown ETA, currencies/tax, supported promotions, stale/revoked context and zero unintended customer-cart mutation.

Until that point, first-increment output truthfully refers the customer to the published store policy/store when a current delivery price or date cannot be established. This does not block the product-discovery and basic-shipping tasks.
