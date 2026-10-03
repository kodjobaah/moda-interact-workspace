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
`ARCH-026-API-002`, `ARCH-026-API-003`, `ARCH-026-WOOCOMMERCE-003`,
`ARCH-026-WOOCOMMERCE-004`, `ARCH-026-WOOCOMMERCE-005`, `ARCH-026-DATABASE-002`,
`ARCH-026-SHOPIFY-001`, `ARCH-026-SHOPIFY-002`, `ARCH-026-BACKGROUND-001`,
`ARCH-026-BACKGROUND-002`, `ARCH-026-ADMIN-001`, `ARCH-026-ADMIN-002` and
`ARCH-026-GATEWAY-001` and `ARCH-026-WOOCOMMERCE-006` are currently materialised. Later tasks must be added only after
their precise runtime, security and ownership boundaries have been discussed and inspected.

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
  by the hosted API.
- Treat internationalization as a first-class Woo architecture invariant: accept and preserve
  WordPress/WooCommerce locale identity without a Moda-specific Woo locale allowlist,
  distinguish administrator UI locale from merchant/store international context, and
  move durable store language/time-zone/country defaults to provider-neutral Shop state.
- Move the one-time merchant onboarding milestone toward provider-neutral `commerce.Shop`
  ownership while retaining the existing Shopify field temporarily during bounded consumer
  migration tasks.
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
with `moda_woocommerce` ownership and a `WOOCOMMERCE` launcher route. WOO-001 is
architect-accepted Complete after Attempt 4; its installable PHP + React foundation and
pinned local runtime were accepted without introducing Moda backend coupling. WOO-002 is
architect-accepted Complete at Attempt 1; API-002 is now architect-accepted Complete at Attempt 2 and WOO-003 is Ready.

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
Woo installation connection/authentication boundary: production-safe site-control proof,
first connection/reconnect credential issuance, and reusable installation-principal
authentication. Merchant business APIs remain later tasks. `ARCH-026-DATABASE-001`
prepares the durable identity/credential state consumed by API-002.

ARCH-026 also defines a separate explicit local-development connection mode so normal
development does not require paid/public WordPress hosting:

```text
local WordPress/WooCommerce
    -> local PHP plugin
    -> local moda-interact-api
    -> development PostgreSQL

API callback:
local moda-interact-api
    -> local WordPress REST challenge route
```

The local-development mode changes only network reachability/TLS rules for explicitly local
targets. The HMAC site-control proof, secret handling, credential issuance/rotation, tenant
resolution, request limits, CAS/concurrency and browser-isolation rules remain identical.
Production remains strict public HTTPS and the development mode must fail closed when
configured in a production API runtime.

## Repository Responsibilities

### `moda-interact-woocommerce` / `moda_woocommerce`

Owns the installable WordPress/WooCommerce extension, including PHP plugin runtime,
WooCommerce Admin integration, browser-to-plugin REST boundaries, Woo-supported
hooks/APIs and later Woo-specific provider edges when explicitly assigned.

It does not own Moda durable-state schema, Background workflows, Shared internal
contracts, Gateway infrastructure or private platform credentials.

### `moda-interact-database` / `moda_database`

Owns the additive ARCH-026 durable identity/lifecycle boundary: shared
`commerce.Shop.platform`, shared `commerce.Shop.onboardingCompleted`, plus one provider-owned `woocommerce.WooCommerceInstallation` record containing the
canonical Woo site URL, current one-way installation-credential digest/version and
revocation state. The dedicated `woocommerce` PostgreSQL schema owns Woo-specific
installation/authentication persistence; `commerce` remains the shared tenant domain.
DATABASE-002 additionally owns provider-neutral `commerce.Shop` international context:
provider-native `storeLocale`, normalized `defaultLanguageTag`, `defaultTimeZone` and
`defaultCountryCode`, while retaining the existing Shopify compatibility fields during
bounded consumer migrations. It deliberately defines no locale enum/allowlist.

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
provider discriminator and provider-neutral one-time onboarding milestone to that shared
tenant, and places Woo-specific connection state
under a dedicated `woocommerce` PostgreSQL schema:

```text
commerce.Shop
    platform = SHOPIFY | WOOCOMMERCE
    onboardingCompleted = false | true
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

DATABASE-001 intentionally does not generalise `Customer`, billing, recovery or other
Shopify-specific historical fields. It retains `shopify.ShopSettings.onboardingCompleted`
for transitional compatibility; SHOPIFY-001 and BACKGROUND-001 make the shared Shop field
authoritative for their runtime lifecycle decisions while mirroring successful completion
to the legacy field. ADMIN-001 then consumes the shared field for cross-platform tenant
presentation. No task in this group removes the legacy field.

DATABASE-002 adds shared merchant/store international context:

```text
commerce.Shop
    storeLocale?          provider-native platform locale
    defaultLanguageTag?   normalized Moda/BCP-47 language tag when available
    defaultTimeZone?      IANA time zone
    defaultCountryCode?   ISO-3166 alpha-2 country code
```

The existing `shopify.ShopSettings.defaultLanguageTag/defaultTimeZone/defaultCountryCode`
fields remain present temporarily. Existing Shopify normalized values are backfilled to the
shared Shop fields, but historical `storeLocale` remains null because the provider-native
locale was not stored separately. SHOPIFY-002 becomes the provider writer/mirror for current
Shopify tenants; BACKGROUND-002 and ADMIN-002 migrate cross-platform readers.

## Internationalization

Internationalization is a first-class ARCH-026 requirement rather than a later UI cleanup.

The Woo integration MUST NOT maintain a fixed Moda-specific allowlist of Woo/WordPress
locales. Provider-native locale identifiers accepted by the WordPress/Woo integration are
preserved as bounded strings; translation coverage is a separate concern. A merchant/admin
locale does not become invalid merely because Moda has not yet published translated strings
for it.

ARCH-026 distinguishes:

```text
current administrator UI locale
    -> WordPress/Woo request/user locale
    -> drives PHP/React translation only

merchant/store locale
    -> provider-native store locale
    -> durable shared Shop international context
```

Those values may differ. The Woo Admin React/PHP UI uses WordPress internationalization
facilities and the canonical `moda-interact` text domain; it must not persist the current
administrator locale as the store default.

Backend business context uses provider-neutral Shop fields. `storeLocale` preserves the
provider-native identifier (for Woo this may use WordPress forms such as `pt_BR`), while
`defaultLanguageTag` is a separately normalized language tag such as `pt-BR` when a safe
conversion/selection has been established. The architecture must not implement this as a
blind underscore-to-hyphen replacement or a closed enum.

Missing translation coverage uses normal fallback behavior; it must not rewrite or reject
the persisted provider locale. Time zone and country are likewise shared store context, not
Shopify-only settings.

## Contracts

WOO-001 and WOO-002 create no cross-service runtime contract. DATABASE-001 creates
a durable database contract: `commerce.Shop.platform`,
`commerce.Shop.onboardingCompleted` and `woocommerce.WooCommerceInstallation`. API-001 creates only operational HTTP
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

API-003's merchant bootstrap contract additionally exposes provider-neutral Shop international
context from DATABASE-002 and never falls back to Shopify settings. Provider-native locale
and normalized language tag remain separate nullable response fields.

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

WOO-003 must fail locally before connection when the store violates the selected API-002 connection mode, uses Plain permalinks or cannot expose the exact challenge REST route. Production requires public HTTPS. Explicit local-development mode may use a local HTTP WordPress identity and local API origin without requiring public hosting. Remote outage must not be interpreted as disconnection, and site URL mismatch must prevent silent credential reuse on a cloned/migrated WordPress database.

WOO-004 consumes only WOO-003's local browser-safe connection GET/POST routes. Its React shell must preserve the distinction between local connection state, remote availability and account/billing lifecycle; unknown/malformed responses fail closed rather than becoming connected/disconnected.

API-002 treats Woo site verification as an SSRF boundary. Production mode remains public
HTTPS only with public/global DNS answers, pinned socket, original-host TLS verification,
connected-peer checks, no redirects, bounded deadline/body and exact HMAC proof. An
explicit local-development mode may additionally verify loopback/private/`.local` identities
(and local HTTP) while retaining address pinning, peer checks, no redirects, bounds and the
exact HMAC proof; it cannot start under the production runtime. Connection/proof failure
causes zero durable mutation. Concurrent connects must converge without duplicate tenants
or silently invalidating a successfully returned credential.

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
- Local-development network relaxation is explicit server-side configuration only, is disabled by default, cannot run in the production API runtime and does not bypass HMAC proof, credential protection, tenant resolution or request bounds.
- Installation status remains connection/authentication state only; onboarding and billing
  lifecycle are not encoded in `WooCommerceInstallationStatus`.

## Observability

WOO-001 introduces no new Moda-hosted telemetry requirement. API-001 must use the
canonical Shared structured logger for generic runtime logging and must not create
duplicate custom HTTP metrics/spans when standard/framework telemetry can provide the
signal. GATEWAY-001 deploys the private API service with the existing environment-specific
general/observability configuration and routes it only through the public Gateway. It must
not invent duplicate application HTTP telemetry or make telemetry transport a correctness
dependency. Later bounded API tasks may add service-owned telemetry only for concrete
Moda-specific semantic gaps.

## Rollout / Migration

This is a pre-production foundation with no existing WooCommerce Moda installation
state to migrate. No backwards-compatibility adapter is required.

Normal development may use a developer-owned local WordPress/WooCommerce fixture rather
than a paid/public WordPress host. The currently demonstrated Local fixture uses WordPress
7.1.2, WooCommerce 11.1.2, PHP 8.2.29 and non-Plain permalinks at a `.local` HTTP origin.
This is development evidence only; it does not replace the deterministic WOO-002 compatibility
matrices or terminal production/public-mode validation.

The WooCommerce repository-provisioning checkpoint has been satisfied. WOO-001 must
complete and be architect-accepted before WOO-002 can execute. WOO-002 changes only
local plugin runtime/lifecycle behaviour and requires no deployment migration or
backwards-compatibility adapter.

DATABASE-001 and DATABASE-002 are architect-accepted Complete at Attempt 1. DATABASE-002
followed DATABASE-001 to avoid concurrent Shop-schema migrations, backfills the shared
normalized international-context fields from retained Shopify settings and leaves provider-native
`storeLocale` null for historical rows until a provider writer establishes it.
It preserves existing `commerce.Shop` data, defaults/backfills all pre-existing Shop rows
to `SHOPIFY`, backfills `commerce.Shop.onboardingCompleted` from the existing Shopify
settings milestone, retains `shopify.ShopSettings.onboardingCompleted`, creates the
dedicated `woocommerce` schema, and adds the cross-schema one-to-one Woo installation
relation; there is no existing Woo installation state to migrate.

SHOPIFY-001 is architect-accepted Complete at Attempt 1. It makes the shared Shop
onboarding milestone authoritative for Shopify application lifecycle reads and mirrors a
successful completion to the retained legacy Shopify field in one bounded transaction.
BACKGROUND-001 remains Ready as the corresponding Background consumer migration. ADMIN-001
still waits for BACKGROUND-001 before using the shared field as its cross-platform tenant
presentation source. With DATABASE-002 already accepted, SHOPIFY-002 is now Ready as the
next serialized `moda-interact` ARCH-026 migration.

API-001 is independently provisionable and does not require DATABASE-001 because its
only database behavior is generic connectivity/readiness against the canonical schema.
The `moda-interact-api` repository/submodule provisioning gate is satisfied. API-001
Attempt 2 and API-002 Attempt 2 are Accepted and Complete. Accepted API-002 implementation
`ba2650b36b599d7965ca5fe12ac0131179a2bcfa` pins merged DATABASE-001 main
`201e0a7044e7ab20d21538487816163ade2233b0` and now owns the authoritative Woo
site-control, credential rotation, steady-state installation authentication and OpenAPI v1
contract. WOO-003 and API-003 each have all declared dependencies satisfied and are Ready.

GATEWAY-001 is Ready because its sole dependency API-001 is architect-accepted Complete.
It may add `moda-interact-api` as a private Render service in both environments and route
the exact public hosts `api-test.modainteract.com` / `api.modainteract.com` through the
existing public Gateway. The API service receives only the environment's general
configuration, `NODE_ENV=production` and PostgreSQL `DATABASE_URL` at this stage; no
Redis/provider credentials or database-migration command are introduced.

WOO-006 remains Pending until WOO-005 and GATEWAY-001 are architect-accepted Complete. It
then freezes the canonical server-side production API default, hardens the self-contained
`moda-interact.zip` distribution artifact, corrects release/i18n/readme packaging metadata
and proves clean install plus in-place upgrade/deactivate/reactivate preservation of the
accepted WOO-003 local connection state. Marketplace submission and billing remain outside
ARCH-026 WOO-006.

## Decisions / Tasks

| Task | Owner | Status | Depends On |
|---|---|---|---|
| ARCH-026-WOOCOMMERCE-001 | moda_woocommerce | Complete | - |
| ARCH-026-WOOCOMMERCE-002 | moda_woocommerce | Complete | ARCH-026-WOOCOMMERCE-001 |
| ARCH-026-DATABASE-001 | moda_database | Complete | - |
| ARCH-026-DATABASE-002 | moda_database | Complete | ARCH-026-DATABASE-001 |
| ARCH-026-API-001 | moda_api | Complete | - |
| ARCH-026-API-002 | moda_api | Complete | ARCH-026-API-001, ARCH-026-DATABASE-001 |
| ARCH-026-API-003 | moda_api | Ready | ARCH-026-API-002, ARCH-026-DATABASE-002 |
| ARCH-026-WOOCOMMERCE-003 | moda_woocommerce | Ready | ARCH-026-WOOCOMMERCE-002, ARCH-026-API-002 |
| ARCH-026-WOOCOMMERCE-004 | moda_woocommerce | Pending | ARCH-026-WOOCOMMERCE-003 |
| ARCH-026-WOOCOMMERCE-005 | moda_woocommerce | Pending | ARCH-026-WOOCOMMERCE-004, ARCH-026-API-003 |
| ARCH-026-WOOCOMMERCE-006 | moda_woocommerce | Pending | ARCH-026-WOOCOMMERCE-005, ARCH-026-GATEWAY-001 |
| ARCH-026-SHOPIFY-001 | moda_app | Complete | ARCH-026-DATABASE-001 |
| ARCH-026-SHOPIFY-002 | moda_app | Ready | ARCH-026-DATABASE-002, ARCH-026-SHOPIFY-001 |
| ARCH-026-BACKGROUND-001 | moda_background | Ready | ARCH-026-DATABASE-001 |
| ARCH-026-BACKGROUND-002 | moda_background | Pending | ARCH-026-DATABASE-002, ARCH-026-SHOPIFY-002, ARCH-026-BACKGROUND-001 |
| ARCH-026-ADMIN-001 | moda_admin | Pending | ARCH-026-SHOPIFY-001, ARCH-026-BACKGROUND-001 |
| ARCH-026-ADMIN-002 | moda_admin | Pending | ARCH-026-DATABASE-002, ARCH-026-SHOPIFY-002, ARCH-026-ADMIN-001 |
| ARCH-026-GATEWAY-001 | moda_gateway | Ready | ARCH-026-API-001 |

WOO-001 Attempt 4 and WOO-002 Attempt 1 are Accepted and Complete. WOO-002 establishes the frozen WordPress/WooCommerce/PHP compatibility window, native plugin requirement metadata, bounded missing/unsupported-Woo runtime guard, delayed idempotent `woocommerce_init` initialisation and non-destructive local activation/deactivation lifecycle while preserving the WOO-001 Admin foundation.

DATABASE-001 and DATABASE-002 are Accepted and Complete at Attempt 1; the ARCH-026 database stream is complete. SHOPIFY-001 and BACKGROUND-001 remain Ready from DATABASE-001 acceptance. API-001 and API-002 are Accepted and Complete at Attempt 2. API-002 acceptance satisfies the remaining dependencies of both API-003 and WOO-003, so API-003 and WOO-003 are Ready. SHOPIFY-002 remains Ready after SHOPIFY-001 + DATABASE-002 acceptance. GATEWAY-001 remains Ready because accepted API-001 was its sole dependency. WOO-004 remains Pending until WOO-003 is architect-accepted Complete; WOO-005 then requires accepted WOO-004 + API-003. Later ARCH-026 tasks remain intentionally iterative and are not frozen here.

## Open Questions

- Exact Woo provider-owned synchronization command for store locale/time-zone/country into shared Shop context.
- When to remove the retained `shopify.ShopSettings.onboardingCompleted` compatibility field after all runtime/test consumers have migrated.
- Commerce-event and shared Background integration.
- Woo Marketplace billing architecture.

## Change History

- 2026-10-03: API-002 Accepted / Complete at Attempt 2. Correction commit `ba2650b36b599d7965ca5fe12ac0131179a2bcfa` closes all four Attempt-1 review findings: public/global targets under local-development retain HTTPS/default-port policy; authenticated probe failures distinguish expected `401 unauthorized` from unexpected `500 internal_error` with exact OpenAPI status/error mappings; SUSPENDED/incompatible reconnect state is checked only after live site-control proof while preserving observed-version CAS; and the Completion Report records the full launcher/worktree/synchronization/recursive-submodule packet. Focused corrections pass 20/20, `npm test` reports 40 passed with five PostgreSQL-only tests skipped by design, and the separate disposable PostgreSQL suite passes 5/5 including concurrent create/reconnect and suspended-Shop rejection. Typecheck, lint, build and diff checks pass. DATABASE-001 remains pinned at `201e0a7044e7ab20d21538487816163ade2233b0`. API-003 and WOO-003 are promoted Ready.
- 2026-10-03: API-002 Attempt 1 returned Ready / Changes Requested. Implementation `940cb4115fc3eef4df9d4e34416b7f1293ba6271` correctly pins merged DATABASE-001 main `201e0a7044e7ab20d21538487816163ade2233b0` and establishes the intended bounded connect/HMAC/pinned-transport/digest-auth/CAS/OpenAPI structure, with 38 non-DB tests plus a separate 5/5 disposable PostgreSQL race suite. Acceptance is blocked by four bounded corrections: (1) public/global targets encountered under local-development must still reject non-default HTTPS ports; (2) unexpected authenticated-probe infrastructure failures must return bounded internal error rather than 401 so WOO-003 can distinguish outage from credential rejection, with exact OpenAPI error mapping; (3) SUSPENDED/incompatible reconnect state must not produce a state-dependent conflict before site-control proof; and (4) the Completion Report must record the full prepared launcher/worktree/synchronization/recursive-submodule packet. WOO-003 and API-003 remain Pending.
- 2026-10-03: SHOPIFY-001 Accepted / Complete at Attempt 1. Implementation `93f36cbecc396ee4c5f3c6d7f70b2a425733c5f0` makes `commerce.Shop.onboardingCompleted` authoritative across Shopify application lifecycle reads, removes legacy onboarding authority from merchant routes/access/discount eligibility and atomically mirrors successful completion to the retained ShopSettings flag with invariant-enforced rollback. Prisma generation, typecheck, focused lifecycle coverage (114 passed / 6 PostgreSQL-prerequisite skips), production build, static source audit and diff checks pass. The two targeted lint diagnostics are unchanged from pre-task base `e59451da815de5c3b60c669e04175811977b2755`. SHOPIFY-002 is promoted Ready; ADMIN-001 remains Pending on BACKGROUND-001.
- 2026-10-03: DATABASE-002 Accepted / Complete at Attempt 1. Implementation `10bcc01fbfca0e4ac90262222c7975b1c9115d3d` adds nullable bounded provider-neutral Shop `storeLocale` / language / time-zone / country context, backfills only the three retained Shopify normalized values and deliberately leaves historical `storeLocale` null. The review correction pins the uppercase ASCII country-code check to PostgreSQL `C` collation; static validation and fresh/upgrade `pgvector/pgvector:pg17` rehearsals verify the installed constraint and reject lowercase, short and non-ASCII values. Legacy Shopify context fields remain unchanged and no locale allowlist/translation-catalogue constraint is introduced. API-003 and SHOPIFY-002 each have their DATABASE-002 dependency satisfied but remain Pending on API-002 and SHOPIFY-001 respectively; the database stream is complete.
- 2026-10-03: DATABASE-001 Accepted / Complete at Attempt 1. Implementation `16e52b47d668e1dad70246be38dcdf7e3dbcdc2f` adds provider-neutral `commerce.Shop.platform` / `onboardingCompleted`, backfills the shared onboarding milestone from retained Shopify settings, and adds one digest-only `woocommerce.WooCommerceInstallation` identity with deterministic FK/unique/check/update-guard integrity. Prisma format/validation/generation, focused static checks, ERD generation and isolated fresh/upgrade `pgvector/pgvector:pg17` rehearsals pass. The unchanged ARCH-023 whole-schema validator still false-positives on existing `MERCHANT_KNOWLEDGE_*` runtime-lease enum values and is not an ARCH-026 regression. DATABASE-002, API-002, SHOPIFY-001 and BACKGROUND-001 are promoted Ready.
- 2026-10-01: Initial iterative ARCH-026 foundation defined; WOO-001 materialised as
  the first bounded implementation task and `moda_woocommerce` ownership introduced.
- 2026-10-02: WOO-001 Attempt 3 implementation/runtime behavior found architecture-conformant; task returned to Ready with Changes Requested for bounded VCS/evidence correction before acceptance.
- 2026-10-02: WOO-001 Attempt 4 accepted after completing the bounded VCS/evidence correction contract; WOO-001 marked Complete and WOO-002 promoted to Ready.
- 2026-10-02: WOO-002 Attempt 1 accepted after validating the frozen WordPress/WooCommerce/PHP matrices, native requirement metadata, bounded runtime gating, delayed single-run Woo initialisation and non-destructive local lifecycle; WOO-003 remains Pending on API-002.
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
- 2026-10-02: API-001 Attempt 1 implementation found architecture-conformant; task returned to Ready for a bounded launcher/worktree/VCS evidence-only correction before acceptance.
- 2026-10-02: API-001 Attempt 2 accepted after the evidence-only correction recorded canonical worktree isolation, synchronization, recursive-submodule provisioning and durable publication state; API-001 marked Complete and GATEWAY-001 promoted to Ready while API-002 remains Pending on DATABASE-001.
- 2026-10-02: API-002 materialised to establish SSRF-safe Woo site-control proof,
  first-connect/reconnect credential issuance, and a reusable authenticated installation
  principal over the DATABASE-001 identity model.
- 2026-10-02: WOO-003 materialised as the PHP-side consumer of API-002, adding the public one-attempt site-control challenge callback, privileged local connection facade, server-side installation credential storage and authenticated Moda API client.
- 2026-10-02: WOO-004 materialised to replace the placeholder Admin page with the first production-shaped React shell and real connection/setup experience, consuming only the accepted WOO-003 browser-safe local REST boundary.
- 2026-10-02: WOO-005 materialised as the first real authenticated merchant-data surface, consuming accepted WOO-004 + API-003 to render read-only shared onboarding, Store Category projection and provider-neutral international context inside WooCommerce Admin.
- 2026-10-02: GATEWAY-001 materialised to deploy `moda-interact-api` as a private Render service in test/production and route the exact API hostnames through the existing public Gateway without transferring authentication, database-migration or business-logic ownership to Gateway.
- 2026-10-02: WOO-006 materialised as the terminal Woo implementation packaging task for ARCH-026 foundation work, freezing the canonical production API default, self-contained release ZIP, internationalization/readme assets and clean install/upgrade/deactivate lifecycle without adding Marketplace billing or submission behavior.

- 2026-10-02: Provider-neutral onboarding migration materialised without removing the
  legacy Shopify field: DATABASE-001 adds/backfills `Shop.onboardingCompleted`; SHOPIFY-001
  and BACKGROUND-001 migrate current runtime writers/readers with compatibility mirroring;
  ADMIN-001 moves tenant presentation to the shared source after both writers migrate.
- 2026-10-02: API-003 materialised as the first authenticated Woo merchant business read boundary, exposing shared `Shop.onboardingCompleted` plus bounded Commerce store-profile category identity without duplicating Store Category mutation logic or touching billing.
- 2026-10-02: Internationalization made a first-class ARCH-026 invariant. DATABASE-002 materialised provider-neutral Shop store-locale/language/time-zone/country state without a Woo locale allowlist; SHOPIFY-002, BACKGROUND-002 and ADMIN-002 materialised bounded consumer migrations; API-003 and WOO-004 were tightened to consume/present international context without treating translation coverage as locale support.
- 2026-10-02: Local WooCommerce development made an explicit architecture mode rather than requiring public WordPress hosting. API-002/WOO-003 now permit a deliberate local-development path for `.local`/loopback/private HTTP fixtures while retaining HMAC proof, address pinning, credential/tenant protections and strict production public-HTTPS behavior; WOO-006 keeps the bypass disabled by default in the distributable package.
