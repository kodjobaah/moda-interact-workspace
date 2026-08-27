# ADR-0003: Separate Platform Admin Application

## Status

Accepted

## Context

The Shopify application is merchant-scoped. It authenticates a Shopify
merchant and displays data for the current shop. Platform operators need a
separate view across all merchants for usage reporting, recovery visibility and
operational support.

Extending the merchant application with platform-wide access would mix two
authorization models and increase the risk of exposing one merchant's data to
another.

## Decision

Create `moda-interact-admin` as a separate Next.js application for authorized
platform administrators.

The application will:

- use platform-admin authentication and role checks;
- perform privileged data loading on the server;
- query reporting data with explicit pagination and tenant-aware boundaries;
- consume the canonical Prisma schema through the database submodule; and
- keep database migrations and usage recording owned by their existing services.

## Consequences

### Positive

- Merchant and platform-admin authorization remain separate.
- Platform-wide reporting has a focused application boundary.
- Operational workflows can evolve without complicating the Shopify app.
- Admin-specific audit and support controls can be added independently.

### Tradeoffs

- A new application introduces another deployment and authentication surface.
- Shared contracts and schema changes require coordination across repositories.
- Reporting queries may eventually need dedicated read models or an internal API.

## Implementation order

1. Establish the Next.js application and admin authentication boundary.
2. Add read-only cross-merchant reporting with bounded queries.
3. Add audit logging and operational health views.
4. Add administrative mutations only after authorization and audit behavior are tested.
