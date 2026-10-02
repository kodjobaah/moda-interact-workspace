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

This architecture is being defined iteratively. `ARCH-026-WOOCOMMERCE-001` and
`ARCH-026-WOOCOMMERCE-002` are currently materialised. Later tasks must be added only
after their precise runtime, security and ownership boundaries have been discussed
and inspected.

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

## Non-Goals

The WOO-001/WOO-002 foundation stage does not implement:

- Moda-hosted merchant APIs or database reads/writes;
- installation credentials or Woo store -> Moda Shop association;
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

Future remote Moda integration is expected to use an architecture-approved HTTPS
service boundary:

```text
React UI
    -> local WordPress REST
    -> PHP plugin
    -> authenticated HTTPS
    -> Moda-hosted API
```

That hosted API is not defined by WOO-001.

## Repository Responsibilities

### `moda-interact-woocommerce` / `moda_woocommerce`

Owns the installable WordPress/WooCommerce extension, including PHP plugin runtime,
WooCommerce Admin integration, browser-to-plugin REST boundaries, Woo-supported
hooks/APIs and later Woo-specific provider edges when explicitly assigned.

It does not own Moda durable-state schema, Background workflows, Shared internal
contracts, Gateway infrastructure or private platform credentials.

## Data Model

None for WOO-001.

Woo installation identity and Moda `Shop` association will be defined by a later
ARCH-026 database/API task after that boundary is agreed.

## Contracts

WOO-001 and WOO-002 create no cross-service runtime contract.

WOO-001 establishes stable local plugin identities:

```text
Plugin name:   Moda Interact
Plugin slug:   moda-interact
Text domain:   moda-interact
PHP namespace: ModaInteract\WooCommerce
Woo Admin path: /moda-interact
```

## Consistency and Transactions

Not applicable to WOO-001; it performs no Moda durable-state mutation.

## Ordering

Not applicable to WOO-001.

## Failure Handling

The foundation must fail safely when its local development/runtime prerequisites are
not present and must not require Moda production secrets or remote services to render
the minimal Admin page. WOO-002 owns the local WordPress/WooCommerce/PHP compatibility
contract, delayed Woo initialisation, bounded administrator dependency feedback and
non-destructive activation/deactivation lifecycle.

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

## Observability

No new Moda-hosted telemetry requirement is introduced by WOO-001. Do not add a
second generic logger or remote telemetry pipeline merely for scaffolding.

## Rollout / Migration

This is a pre-production foundation with no existing WooCommerce Moda installation
state to migrate. No backwards-compatibility adapter is required.

The WooCommerce repository-provisioning checkpoint has been satisfied. WOO-001 must
complete and be architect-accepted before WOO-002 can execute. WOO-002 changes only
local plugin runtime/lifecycle behaviour and requires no deployment migration or
backwards-compatibility adapter.

## Decisions / Tasks

| Task | Owner | Status | Depends On |
|---|---|---|---|
| ARCH-026-WOOCOMMERCE-001 | moda_woocommerce | Blocked | - |
| ARCH-026-WOOCOMMERCE-002 | moda_woocommerce | Pending | ARCH-026-WOOCOMMERCE-001 |

WOO-002 remains Pending until WOO-001 is architect-accepted Complete. Later ARCH-026
tasks remain intentionally iterative and are not frozen by the existence of WOO-002.

## Open Questions

- Exact hosted Moda merchant-API repository/service boundary for later real database
  reads and merchant commands.
- Secure Woo installation identity/credential handshake.
- Exact first DB-backed merchant capability after the plugin foundation.
- Commerce-event and shared Background integration.
- Woo Marketplace billing architecture.

## Change History

- 2026-10-01: Initial iterative ARCH-026 foundation defined; WOO-001 materialised as
  the first bounded implementation task and `moda_woocommerce` ownership introduced.
- 2026-10-02: Repository provisioning completed and WOO-002 materialised to establish
  local plugin dependency, compatibility, initialisation and lifecycle behaviour after
  WOO-001 completes.
