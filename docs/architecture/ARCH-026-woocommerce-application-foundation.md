---
id: ARCH-026
title: WooCommerce application foundation
status: proposed
coordinator: moda_architect
created: 2026-10-01
updated: 2026-10-02
---

# ARCH-026: WooCommerce application foundation

## Status

Proposed.

This architecture is being defined iteratively. `ARCH-026-WOOCOMMERCE-001`,
`ARCH-026-WOOCOMMERCE-002`, `ARCH-026-DATABASE-001`, `ARCH-026-API-001`,
`ARCH-026-API-002`, `ARCH-026-WOOCOMMERCE-003` and `ARCH-026-WOOCOMMERCE-004`
are currently materialised. Later tasks must be added only after their precise runtime,
security and ownership boundaries have been discussed and inspected.

## Problem

Moda Interact currently has a Shopify-facing application but no WooCommerce-facing
application. WooCommerce extensions execute inside merchant-controlled WordPress
installations, so the Shopify Next.js deployment model cannot simply be reused.

The first requirement is to establish a genuine installable WordPress/WooCommerce
extension foundation before adding Moda-hosted API connectivity, commerce events,
recovery processing, products, discounts or billing.

## Goals

- Establish `moda-interact-woocommerce` as the repository for the installable Moda
  Interact WordPress/WooCommerce extension.
- Establish `moda_woocommerce` as the repository-owning logical agent.
- Use PHP for the WordPress/WooCommerce runtime and compiled React/JavaScript for a
  modern WooCommerce Admin merchant UI.
- Produce a reproducible, buildable, testable and installable plugin foundation.
- Keep the WooCommerce application boundary separate from Moda-hosted backend and
  asynchronous service ownership.
- Preserve a clean path for later secure HTTPS integration with Moda services.
- Establish the minimum durable Shop platform and Woo installation identity needed
  by the hosted API without refactoring existing Shopify/billing semantics.
- Establish `moda-interact-api` as the backend-only hosted synchronous API boundary
  that later Woo tasks can authenticate against without exposing Moda database or
  private-service credentials to merchant WordPress infrastructure.

## Non-Goals

The WOO-001/WOO-002 plugin-foundation stage does not implement:

- Moda-hosted merchant APIs or database reads/writes from the plugin;
- Woo store -> Moda Shop connection/handshake application code;
- cart/checkout/order event ingress;
- BullMQ or Background integration;
- recovery workflows;
- product/coupon integration;
- Merchant Knowledge or CommerceAgent integration;
- Woo Marketplace SaaS billing;
- recovery-credit purchases.

Those capabilities require later architecture discussion/tasks and must not be
smuggled into the foundation tasks.

## Current Architecture

`moda-interact-woocommerce` is now provisioned as the canonical workspace submodule,
with `moda_woocommerce` ownership and a `WOOCOMMERCE` launcher route. WOO-001 has
started execution but is currently blocked by an unresolved host-toolchain prerequisite;
no WooCommerce scaffold implementation has yet been committed.

`moda-interact/` remains the Shopify merchant-facing application. Existing shared
Background, Database, Commerce, Messaging, Admin, Shared and Gateway repositories
retain their current ownership.

## Proposed Architecture

The WooCommerce-facing application is an installable WordPress plugin:

```text
merchant WordPress installation

WordPress
    |
    +-- WooCommerce
            |
            +-- Moda Interact plugin
                    |
                    +-- PHP runtime
                    +-- compiled React/JavaScript Woo Admin UI
```

The plugin is not a separately hosted Next.js application and does not directly
connect to Moda PostgreSQL, Redis/BullMQ or private services.

Remote Moda integration uses a separate hosted service boundary:

```text
React UI
    -> local WordPress REST
    -> PHP plugin
    -> authenticated HTTPS
    -> moda-interact-gateway
    -> moda-interact-api
    -> PostgreSQL / architecture-owned services
```

`ARCH-026-API-001` establishes only the backend-only API runtime, canonical database
consumption and health/readiness behavior. `ARCH-026-API-002` then establishes the
Woo installation connection/authentication boundary: SSRF-safe site-control proof,
first connection/reconnect credential issuance, and reusable installation-principal
authentication. Merchant business APIs remain later tasks. `ARCH-026-DATABASE-001`
prepares the durable identity/credential state consumed by API-002.

## Repository Responsibilities

### `moda-interact-woocommerce` / `moda_woocommerce`

Owns the installable WordPress/WooCommerce extension, including PHP plugin runtime,
WooCommerce Admin integration, browser-to-plugin REST boundaries, Woo-supported
hooks/APIs and later Woo-specific provider edges when explicitly assigned.

It does not own Moda durable-state schema, Background workflows, Shared internal
contracts, Gateway infrastructure or private platform credentials.

### `moda-interact-database` / `moda_database`

Owns the additive ARCH-026 durable identity boundary: shared `commerce.Shop.platform`
plus one provider-owned `woocommerce.WooCommerceInstallation` record containing the
canonical Woo site URL, current one-way installation-credential digest/version and
revocation state. The dedicated `woocommerce` PostgreSQL schema owns Woo-specific
installation/authentication persistence; `commerce` remains the shared tenant domain.
It does not own the HTTP connection flow, raw secret generation, request
authentication or provider business workflows.

### `moda-interact-api` / `moda_api`

Owns the Moda-hosted synchronous HTTP boundary for external merchant applications.
API-001 establishes the server-only Node/TypeScript runtime, canonical database
submodule/Prisma consumption and liveness/readiness endpoints only. API-002 owns the
Woo installation site-control handshake, credential issuance/rotation and steady-state
installation principal. Later tasks may add bounded merchant queries/commands behind
that authenticated principal.

It does not own WordPress/Woo runtime code, database schema/migrations, asynchronous
Background workflows or Gateway deployment/routing.

## Data Model

ARCH-026 keeps `commerce.Shop` as the single Moda tenant. DATABASE-001 adds a
provider discriminator to that shared tenant and places Woo-specific connection state
under a dedicated `woocommerce` PostgreSQL schema:

```text
commerce.Shop
    platform = SHOPIFY | WOOCOMMERCE
    |
    `-- woocommerce.WooCommerceInstallation?
            id
            shopId                 UNIQUE -> Shop.id
            canonicalSiteUrl       UNIQUE
            status                 ACTIVE | REVOKED
            credentialDigest       SHA-256 digest only
            credentialVersion
            credentialIssuedAt
            revokedAt?
```

Existing Shop rows are migrated/defaulted to `SHOPIFY`; existing `domain` and
`shopifyShopId` fields remain intact. A Woo Shop must have `shopifyShopId = NULL`.
The installation row is deleted with its Shop but cannot be reassigned to another
Shop. No raw installation credential is persisted.

DATABASE-001 intentionally does not generalise `Customer`, billing, recovery or
other Shopify-specific historical fields.

## Contracts

WOO-001 and WOO-002 create no cross-service runtime contract. DATABASE-001 creates
a durable database contract only: `commerce.Shop.platform` plus
`woocommerce.WooCommerceInstallation`. API-001 creates only operational HTTP
contracts: `GET /health/live` and `GET /health/ready`.

API-002 owns the first PHP-consumable Woo installation API contract through
`openapi/woocommerce-installation-v1.yaml` and WOO-003 implements its WordPress/PHP consumer boundary:

```text
POST /v1/woocommerce/installations/connect
GET  /v1/woocommerce/installation
```

The unauthenticated connect route must first prove control of the canonical public
HTTPS Woo site through a bounded HMAC challenge callback before creating or rotating
installation state. Subsequent Woo API calls authenticate with installation ID plus
a presented raw credential whose SHA-256 digest matches the stored digest, then
resolve the authoritative `shopId`; site URL alone is never authentication.

WOO-003 additionally owns the local WordPress connection facade:

```text
GET  /wp-json/moda-interact/v1/connection
POST /wp-json/moda-interact/v1/connection
GET  /wp-json/moda-interact/v1/connection/challenge
```

Only the challenge route is public; the browser-facing GET/POST routes require a privileged
WooCommerce administrator and WordPress REST cookie/nonce authentication. Raw bootstrap
and long-lived installation credentials remain PHP/server-side and are never returned to
React.

WOO-001 establishes stable local plugin identities:

```text
Plugin name:   Moda Interact
Plugin slug:   moda-interact
Text domain:   moda-interact
PHP namespace: ModaInteract\WooCommerce
Woo Admin path: /moda-interact
```

## Consistency and Transactions

WOO-001/WOO-002 perform no Moda durable-state mutation. WOO-003 persists only merchant-side WordPress connection state after an API-002 verified connect/reconnect; it does not mutate Moda PostgreSQL directly. DATABASE-001 establishes
constraints so one Woo installation belongs to exactly one Shop, credential/revocation
state is internally consistent and an installation cannot be reassigned to another
tenant. API-002 performs site verification outside the database transaction, then
creates first-connection Shop/installation state atomically or rotates an existing
credential with credential-version compare-and-swap. Raw bootstrap/installation
secrets are never durable state.

## Ordering

Not applicable to WOO-001.

## Failure Handling

The plugin foundation must fail safely when its local development/runtime prerequisites
are not present and must not require Moda production secrets or remote services to render
the minimal Admin page. WOO-002 owns the local WordPress/WooCommerce/PHP compatibility
contract, delayed Woo initialisation, bounded administrator dependency feedback and
non-destructive activation/deactivation lifecycle.

API-001 separates liveness from readiness: process liveness does not depend on
PostgreSQL, while readiness returns 503 when the bounded database connectivity probe
fails. It must not run migrations or mutate business state as part of readiness.

WOO-003 must fail locally before connection when the store is not HTTPS, uses Plain permalinks or cannot expose the exact API-002 challenge REST route. Remote outage must not be interpreted as disconnection, and site URL mismatch must prevent silent credential reuse on a cloned/migrated WordPress database.

WOO-004 consumes only WOO-003's local browser-safe connection GET/POST routes. Its React shell must preserve the distinction between local connection state, remote availability and account/billing lifecycle; unknown/malformed responses fail closed rather than becoming connected/disconnected.

API-002 treats Woo site verification as an SSRF boundary: public HTTPS only, public/global
DNS answers only, pinned socket, original-host TLS verification, connected-peer checks,
no redirects, bounded deadline/body and exact HMAC proof. Connection/proof failure causes
zero durable mutation. Concurrent connects must converge without duplicate tenants or
silently invalidating a successfully returned credential.

## Scalability

No remote workload is introduced by WOO-001. The plugin foundation runs on each
merchant's WordPress installation. Later remote/event architecture must model the
Moda ingress and shared Background workload separately.

## Security

- No Moda database/Redis/private-service credentials in plugin source or browser
  assets.
- No direct PostgreSQL/Redis/BullMQ access from merchant WordPress infrastructure.
- No fake remote connection or merchant state presented as real.
- Executable UI assets are built and shipped with the plugin rather than requiring a
  merchant-side development server.
- Woo installation authentication stores only a one-way 32-byte credential digest;
  raw installation credentials must never be persisted in PostgreSQL or browser assets.
- API-002 issues the raw long-lived credential only after live site-control proof and
  returns it once to the PHP plugin; the browser never receives it.
- API-002 never trusts caller-supplied `shopId`/domain as tenant identity after connection;
  steady-state authorization resolves the Shop from the authenticated installation row.
- WOO-003 stores the raw installation credential only in non-autoloaded server-side WordPress state and never exposes it to browser JavaScript, localized data or logs.
- WOO-003 derives site identity and API authentication material server-side; browser requests cannot choose the remote tenant or API origin.
- WOO-004 browser code calls only the local WordPress REST connection facade and never receives the long-lived installation credential, bootstrap secret, Authorization header or credential digest.
- Installation status remains connection/authentication state only; onboarding and billing
  lifecycle are not encoded in `WooCommerceInstallationStatus`.

## Observability

WOO-001 introduces no new Moda-hosted telemetry requirement. API-001 must use the
canonical Shared structured logger for generic runtime logging and must not create
duplicate custom HTTP metrics/spans when standard/framework telemetry can provide the
signal. Hosted telemetry/export configuration remains deployment/Gateway work unless a
later bounded API task identifies a concrete service-owned gap.

## Rollout / Migration

This is a pre-production foundation with no existing WooCommerce Moda installation
state to migrate. No backwards-compatibility adapter is required.

The WooCommerce repository-provisioning checkpoint has been satisfied. WOO-001 must
complete and be architect-accepted before WOO-002 can execute. WOO-002 changes only
local plugin runtime/lifecycle behaviour and requires no deployment migration or
backwards-compatibility adapter.

DATABASE-001 is an additive pre-production migration that may execute independently.
It preserves existing `commerce.Shop` data, defaults/backfills all pre-existing Shop
rows to `SHOPIFY`, creates the dedicated `woocommerce` schema, and adds the cross-schema
one-to-one Woo installation relation; there is no existing Woo installation state to
migrate.

API-001 is independently provisionable and does not require DATABASE-001 because its
only database behavior is generic connectivity/readiness against the canonical schema.
It remains Pending until the `moda-interact-api` repository is provisioned and registered
as a workspace submodule. API-002 remains Pending until API-001 and DATABASE-001 are both
architect-accepted Complete; it must then pin the API repository's nested `database/`
gitlink to the accepted DATABASE-001 main commit before implementing the connection flow.

## Decisions / Tasks

| Task | Owner | Status | Depends On |
|---|---|---|---|
| ARCH-026-WOOCOMMERCE-001 | moda_woocommerce | Blocked | - |
| ARCH-026-WOOCOMMERCE-002 | moda_woocommerce | Pending | ARCH-026-WOOCOMMERCE-001 |
| ARCH-026-DATABASE-001 | moda_database | Ready | - |
| ARCH-026-API-001 | moda_api | Pending | - |
| ARCH-026-API-002 | moda_api | Pending | ARCH-026-API-001, ARCH-026-DATABASE-001 |
| ARCH-026-WOOCOMMERCE-003 | moda_woocommerce | Pending | ARCH-026-WOOCOMMERCE-002, ARCH-026-API-002 |
| ARCH-026-WOOCOMMERCE-004 | moda_woocommerce | Pending | ARCH-026-WOOCOMMERCE-003 |

DATABASE-001 may execute independently while the Woo plugin stream is blocked/pending.
API-001 also has no task dependency and is gated only by repository provisioning.
API-002 is separately gated on accepted API-001 + DATABASE-001 and establishes the
connection/authentication contract consumed by WOO-003. WOO-003 remains Pending until
both WOO-002 and API-002 are architect-accepted Complete; it implements the PHP-side
challenge callback, server-side credential storage, authenticated Moda API client and local
WordPress REST connection facade. WOO-004 then establishes the real Woo Admin React shell
and connection/setup experience over that accepted local facade without adding merchant
business screens. Later ARCH-026 tasks remain intentionally iterative and are not frozen by
these materialised tasks.

## Open Questions

- Exact first DB-backed merchant capability after the plugin foundation.
- Commerce-event and shared Background integration.
- Woo Marketplace billing architecture.

## Change History

- 2026-10-01: Initial iterative ARCH-026 foundation defined; WOO-001 materialised as
  the first bounded implementation task and `moda_woocommerce` ownership introduced.
- 2026-10-02: Repository provisioning completed and WOO-002 materialised to establish
  local plugin dependency, compatibility, initialisation and lifecycle behaviour after
  WOO-001 completes.
- 2026-10-02: DATABASE-001 materialised independently to persist explicit Shop platform
  identity plus the minimal one-to-one Woo installation credential/revocation state
  required by the future hosted API.
- 2026-10-02: DATABASE-001 schema ownership clarified: shared tenant/platform state remains
  in `commerce`; Woo-specific installation/authentication state is owned by the dedicated
  `woocommerce` PostgreSQL schema.

- 2026-10-02: API-001 materialised to establish `moda-interact-api` as the backend-only
  hosted synchronous API boundary with canonical database consumption and health/readiness
  behavior. Repository provisioning remains its only readiness gate.
- 2026-10-02: API-002 materialised to establish SSRF-safe Woo site-control proof,
  first-connect/reconnect credential issuance, and a reusable authenticated installation
  principal over the DATABASE-001 identity model.
- 2026-10-02: WOO-003 materialised as the PHP-side consumer of API-002, adding the public one-attempt site-control challenge callback, privileged local connection facade, server-side installation credential storage and authenticated Moda API client.
- 2026-10-02: WOO-004 materialised to replace the placeholder Admin page with the first production-shaped React shell and real connection/setup experience, consuming only the accepted WOO-003 browser-safe local REST boundary.
