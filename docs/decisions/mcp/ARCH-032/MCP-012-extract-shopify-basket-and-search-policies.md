---
id: ARCH-032-MCP-012
architecture_id: ARCH-032
title: Extract Commerce Shopify basket and bounded product-search policy operations
task_kind: implementation
domain: mcp
repository: moda-interact-mcp
assigned_agent: moda_mcp
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: pending
priority: 12
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-032-MCP-011
enables:
  - ARCH-032-MCP-013
created: 2026-10-11
updated: 2026-10-11
---

# Shopify basket and product-search policy extraction

## Objective

Extract the first two remaining built-in Commerce policy operations into MCP:
`recovery.getBasket@1.0.0` and `shopify.searchProducts@1.0.0`. Preserve
published-revision authorization, deterministic recovery reads, bounded
Shopify reads and signed continuation cursors. Follow with discounts and
recommendation operations in subsequent bounded tasks.

## Read first

- `moda-interact-commerce/src/commerce/products/index.ts`
- `moda-interact-mcp/src/execution/policy/execute.ts`
- `moda-interact-mcp/src/connections/ports.ts`
- `moda-interact-mcp/src/runtime/{prisma,service-ports}.ts`
- `moda-interact-mcp/tests/integration/prisma.integration.test.ts`

## Scope

- Extract Commerce basket normalization and signed product-search cursors.
- Restrict search to the fixed pinned Shopify Admin GraphQL operation.
- Resolve identity, published definition, grant, feature and entitlements on
  every call and reject cross-tenant/revoked/unsupported calls.
- Use persisted recovery ownership and the existing authenticated Shopify
  StoreConnection; credentials must not be created or managed in policy code.
- Reuse `COMMERCE_CURSOR_SECRET`; missing/short secrets disable search only.
- Charge provider requests once in StoreConnection, not in the policy adapter.
- Preserve the existing Commerce, Background, API, Gateway and HTTP activation.
- Keep discounts, product recommendations, external HTTP and WooCommerce
  product REST policies out of this task; those remain unavailable.
- Keep all tests under `tests/`, including disposable PostgreSQL fixtures.

## Acceptance Criteria

- Published basket and Shopify search operations are discoverable only for
  eligible Shopify shops, and execute only the exact pinned revision.
- Basket owner, deadline, feature revocation and product-query mapping are
  checked before provider or persisted checkout access.
- Shopify search cannot accept arbitrary API URLs, credentials or GraphQL
  documents from a published tool or from model-supplied arguments.
- HMAC cursors are bound to the store and query, cannot be forged, expire,
  and preserve Commerce's limits and response normalization.
- Other policy operation types remain undiscoverable until explicitly enabled.
- Local unit, typecheck, lint, build and disposable migrated PostgreSQL tests
  pass; no live provider calls or service activation.
- No `docs/decisions/**/_index.md` change.

## Validation

- [ ] `git apply --check --whitespace=error-all` on MCP-011 Attempt-1 baseline.
- [ ] `git apply --whitespace=error-all` and `git diff --check`.
- [ ] `npm run typecheck && npm run lint && npm test && npm run build`.
- [ ] `npm run typecheck:integration && npm run test:integration:docker`.
- [ ] Confirm the existing Commerce and live MCP HTTP routes are unchanged.

## Completion Report

### Status

Not started. Developer-owned patch delivery awaiting local validation and
architect review. No architect acceptance decision is implied.

## Architect-requested execution-model correction (Attempt 2)

The canonical invocation contract for the standalone MCP runtime is now:

- A feature can own many capabilities; each capability references exactly one
  published tool. Different features/capabilities may reference that same tool.
- For an authorized execute context, `tools/list` returns **one item for each
  entitled, selected and runnable capability**, never one item per tool ID.
  Callable identity is the globally unique `CommerceCapability.key` (invalid MCP
  invocation keys fail closed),
  while the input schema derives from the pinned associated tool revision.
- `tools/call` resolves the exact selected capability ID/key first, verifies
  its published tool revision and authorization again, then invokes a generic
  registered execution adapter. No cross-capability authorization borrowing.
- The Shared manifest/grant format remains unchanged; its grouped grantedTools
  preserve capability provenance through `capabilityKeys`.
- Two capabilities sharing a tool must be independently listable, callable and
  revocable. A feature entitlement change must not disable a sibling capability.
- Runtime executor support is filtered per capability, not only by tool ID.
- Respect `CommerceCapability.shopPlatform` independently for every capability:
  `null` means platform-generic; otherwise it must match the trusted, persisted
  `Shop.platform`. Filter both discovery and invocation, even for capabilities
  sharing the same tool and grant. No model-supplied platform override.
- Add unit tests and disposable migrated PostgreSQL tests for those invariants.
- Existing Background/Shared runner tool-name assumptions require a separately
  coordinated compatibility task and end-to-end tests before any live routing.
  This attempt does not change their code, Commerce or the live MCP endpoint.

Attempt 2 is incremental over the MCP-012 Attempt-1 implementation patch.
The developer owns validation and publication; do not infer architect acceptance
from the filename or from green local checks.
