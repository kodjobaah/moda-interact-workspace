# Service Boundaries

The workspace is composed of independently versioned projects. Changes should
stay within the owning service unless a shared contract must change.

| Service | Owns | Does not own |
| --- | --- | --- |
| `moda-interact` | Shopify authentication, merchant UI, Shopify webhooks, onboarding, billing and merchant settings | Long-running recovery workflows, AI processing and Meta webhook ingress |
| `moda-interact-admin` | Platform-admin UI, cross-merchant reporting, operational visibility and admin workflows | Merchant Shopify UI, usage recording and database migrations |
| `moda-interact-background` | BullMQ workers, recovery processing, order processing, Commerce Agent, Shopify tools, entitlements and usage recording | Merchant UI and provider-specific webhook ingress |
| `moda-interact-database` | Prisma schema, PostgreSQL migrations, constraints, indexes, seed data and ERD | Application routes and business workflows |
| `moda-interact-messaging` | Meta/WhatsApp webhook verification, event normalisation and queue publishing | AI generation, recovery workflows and Shopify product logic |
| `moda-interact-site` | Public marketing website, product content and public legal pages | Authenticated application behavior and platform workflows |
| `shopify-webhook-downloader` | Developer tooling that scrapes and refreshes sample Shopify webhook payloads used as reference fixtures | Runtime webhook handling, any production application logic |

## Ownership rules

- Database schema changes originate in `moda-interact-database`.
- Queue payload changes require coordination between producers and consumers.
- Provider payloads are normalised at the messaging boundary.
- Recovery and usage business logic belongs in the background service.
- Admin reporting must enforce platform-admin authorization server-side.
- Cross-repository changes should be planned by `moda_architect`.

## Shared dependencies

The database repository is consumed as a nested submodule by services that need
the canonical Prisma schema. Generated Prisma clients must use the same Prisma
version as the shared schema and should be regenerated after schema updates.

The workspace root records compatible submodule commits so a platform snapshot
can be reproduced.
