---
id: ARCH-026-DATABASE-001
architecture_id: ARCH-026
title: Persist WooCommerce installation identity and shared onboarding milestone
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 15
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables:
  - ARCH-026-API-002
  - ARCH-026-SHOPIFY-001
  - ARCH-026-BACKGROUND-001
created: 2026-10-02
updated: 2026-10-02
---

# Persist WooCommerce installation identity and shared onboarding milestone

## Architecture

Architecture ID:

`ARCH-026`

Architecture document:

`docs/architecture/ARCH-026-woocommerce-application-foundation.md`

Coordinator:

`moda_architect`

## Objective

Add the minimum durable database boundary required to represent a WooCommerce-backed Moda `Shop`, authenticate one connected WordPress/WooCommerce installation, and introduce the provider-neutral one-time merchant onboarding milestone on shared `commerce.Shop` without removing the existing Shopify compatibility field.

The target durable relationship is:

```text
commerce.Shop
    |
    +-- platform = SHOPIFY | WOOCOMMERCE
    +-- onboardingCompleted = provider-neutral one-time milestone
    |
    `-- 0..1 woocommerce.WooCommerceInstallation
            |
            +-- canonicalSiteUrl
            +-- credentialDigest (one-way only)
            +-- credentialVersion
            +-- current ACTIVE / REVOKED state
            `-- credential/revocation timestamps
```

Existing Shopify rows must continue to behave as Shopify rows without requiring immediate application-code changes. The existing `shopify.ShopSettings.onboardingCompleted` column remains present during this transition; DATABASE-001 does not remove it.

This task owns schema, migration and database-level integrity only. It MUST NOT implement the connection handshake, issue credentials, authenticate HTTP requests, create Woo shops from application code or add Woo business features.

## Context

The current durable tenant model is `commerce.Shop`:

```text
Shop
    id
    domain             UNIQUE
    shopifyShopId?     UNIQUE
    status
    installedAt
    uninstalledAt?
    reinstallPendingAt?
    ... existing billing / recovery / Commerce relations
```

`Shop.domain` is already the canonical merchant-domain identifier used throughout Moda. Existing Shopify application code creates and resolves `Shop` directly and may create rows with `shopifyShopId = NULL`, including tests and non-provider fixtures.

ARCH-026 must therefore avoid a broad provider-identity rewrite in this task. Specifically:

- do not rename `Shop.domain`;
- do not rename or remove `Shop.shopifyShopId`;
- do not generalise billing fields;
- do not alter `Customer.shopifyCustomerId`;
- do not create Woo-specific copies of `Shop`, `Customer`, `Subscription`, `BillingPeriod` or recovery models;
- do not remove `shopify.ShopSettings.onboardingCompleted` in this task.

The smallest coherent change is to add an explicit platform discriminator and provider-neutral one-time onboarding milestone to `Shop`, default/backfill existing rows from the current Shopify state, and add one provider-specific installation record for the WordPress/WooCommerce edge.

The existing one-time onboarding milestone is currently persisted in `shopify.ShopSettings.onboardingCompleted` and consumed by the Shopify app/background/admin flows. ARCH-026 must not create a Woo-specific duplicate onboarding flag. Instead, DATABASE-001 adds `commerce.Shop.onboardingCompleted` as the shared migration target and backfills it from the existing Shopify setting.

This task intentionally **retains** `shopify.ShopSettings.onboardingCompleted`. It does not add a database trigger or claim both fields are permanently authoritative. Follow-on ARCH-026 Shopify/Background tasks migrate runtime reads/writes to the shared `Shop` field while mirroring successful completion to the legacy field for compatibility. Until those consumer tasks are accepted, existing runtime code may continue to use the legacy field.

The future hosted Moda API will use this durable state to:

```text
installation id + presented raw installation secret
        |
        v
load WooCommerceInstallation
        |
        v
hash presented secret
        |
        v
compare to credentialDigest
        |
        v
resolve shopId
```

The raw installation secret is never durable database state. The future API task owns secret generation, hashing, constant-time comparison, canonical-site-URL normalization, credential rotation commands and HTTP authentication.

ARCH-026 is pre-production for WooCommerce. There is no Woo installation state to migrate. Existing Shopify development state must be preserved.

## Scope

Modify only `moda-interact-database` files required for this exact schema/migration boundary.

Expected primary implementation files:

```text
prisma/schema.prisma
prisma/migrations/20261002090000_arch026_woocommerce_installation_identity/migration.sql
scripts/validate-arch026-woocommerce-installation-schema.mjs
scripts/validate-arch026-woocommerce-installation-migration.mjs
package.json
docs/generated/prisma-erd.puml
```

Update the generated ERD through the repository's normal schema-change workflow.

### Required `ShopPlatform` enum

Add exactly:

```prisma
enum ShopPlatform {
  SHOPIFY
  WOOCOMMERCE

  @@schema("commerce")
}
```

### Required `Shop` additions

Add to `Shop`:

```prisma
platform                ShopPlatform             @default(SHOPIFY)
onboardingCompleted     Boolean                  @default(false)
wooCommerceInstallation WooCommerceInstallation?
```

`onboardingCompleted` is the provider-neutral one-time Moda merchant onboarding milestone. It is not an installation or billing status and must remain monotonic in normal application flows: once `true`, normal runtime code must not reset it to `false`.

Retain all existing Shopify identity fields and relations, including the existing `shopify.ShopSettings.onboardingCompleted` compatibility field.

Add:

```prisma
@@index([platform, status])
```

The migration MUST preserve every existing `Shop` row and establish `platform = SHOPIFY` for all rows that existed before ARCH-026.

The migration MUST also backfill the shared milestone from current Shopify development state:

```text
commerce.Shop.onboardingCompleted = true
    when the related shopify.ShopSettings.onboardingCompleted = true

otherwise
    commerce.Shop.onboardingCompleted = false
```

The backfill must be deterministic and idempotent for the accepted migration path. Do not delete or rename `shopify.ShopSettings.onboardingCompleted` in this task.

### Required PostgreSQL / Prisma schema registration

Add the provider-owned PostgreSQL schema to the Prisma datasource's `schemas` list:

```text
woocommerce
```

Retain every existing schema registration.

The migration MUST create the schema idempotently before creating Woo-owned objects:

```sql
CREATE SCHEMA IF NOT EXISTS "woocommerce";
```

`commerce` remains the owner of shared tenant state such as `Shop` and `ShopPlatform`.
WooCommerce-specific installation/authentication state belongs to `woocommerce`.

### Required `WooCommerceInstallationStatus` enum

Add exactly:

```prisma
enum WooCommerceInstallationStatus {
  ACTIVE
  REVOKED

  @@schema("woocommerce")
}
```

### Required `WooCommerceInstallation` model

Add exactly this logical Prisma shape:

```prisma
model WooCommerceInstallation {
  id               String                            @id @default(cuid()) @db.Text
  shopId           String                            @unique @db.Text
  shop             Shop                              @relation(fields: [shopId], references: [id], onDelete: Cascade, onUpdate: Restrict)
  canonicalSiteUrl String                            @unique @db.VarChar(512)
  status           WooCommerceInstallationStatus    @default(ACTIVE)
  credentialDigest Bytes
  credentialVersion Int                             @default(1)
  credentialIssuedAt DateTime                       @default(now()) @db.Timestamptz(3)
  revokedAt        DateTime?                         @db.Timestamptz(3)
  createdAt        DateTime                          @default(now()) @db.Timestamptz(3)
  updatedAt        DateTime                          @default(now()) @updatedAt @db.Timestamptz(3)

  @@index([status, shopId])
  @@schema("woocommerce")
}
```

Formatting may be adjusted by Prisma, but field names, types, nullability, relation semantics and indexes above are architectural requirements.

### Required database constraints

Create deterministic migration-level constraints/indexes with these names and semantics:

```text
Shop_platform_shopify_id_check
    platform = SHOPIFY
    OR shopifyShopId IS NULL

Shop_platform_status_idx
    (platform, status)

WooCommerceInstallation_shopId_key
    UNIQUE(shopId)

WooCommerceInstallation_canonicalSiteUrl_key
    UNIQUE(canonicalSiteUrl)

WooCommerceInstallation_canonical_site_url_check
    btrim(canonicalSiteUrl) <> ''

WooCommerceInstallation_credential_digest_length_check
    octet_length(credentialDigest) = 32

WooCommerceInstallation_credential_version_check
    credentialVersion > 0

WooCommerceInstallation_status_revoked_at_check
    (status = ACTIVE AND revokedAt IS NULL)
    OR
    (status = REVOKED AND revokedAt IS NOT NULL)

WooCommerceInstallation_status_shopId_idx
    (status, shopId)
```

Create the FK:

```text
woocommerce.WooCommerceInstallation.shopId
    -> commerce.Shop.id
    ON DELETE CASCADE
    ON UPDATE RESTRICT
```

Add a bounded update guard using deterministic names:

```text
woocommerce.arch026_woocommerce_installation_guard()
arch026_woocommerce_installation_guard
```

The guard MUST reject updates that change:

```text
id
shopId
```

The guard MUST NOT prevent deletion. Deleting a `Shop` must be able to cascade-delete its `WooCommerceInstallation` as part of existing tenant/data-deletion behaviour.

The guard MUST NOT make `canonicalSiteUrl`, credential state or revocation state immutable; later connection-management code must be able to update those fields under application-owned validation.

### Credential-storage contract

`credentialDigest` stores exactly a 32-byte SHA-256 digest of a future high-entropy installation credential.

The database MUST NOT contain a raw installation credential.

Do not add columns named or intended to store plaintext values such as:

```text
credential
credentialSecret
secret
accessToken
bearerToken
apiToken
```

`credentialVersion` identifies the current credential generation and begins at `1`.

This task does not define overlapping/grace-period credentials. ARCH-026 v1 has exactly one current credential digest per Woo installation. A future architecture may introduce a credential-history/rotation table if simultaneous credentials become necessary.

### Site-URL contract

`canonicalSiteUrl` is the future API's canonical absolute WordPress/Woo site URL and is limited to 512 characters.

This task does not implement URL normalization. The future API task must normalize before persistence. Database uniqueness applies to the canonical value supplied by that API.

Do not derive tenant authorization from the URL alone. `WooCommerceInstallation.id` + credential verification resolves the authoritative `shopId`.

## Out of Scope

- Creating `moda-interact-api`.
- Woo plugin -> Moda connection handshake.
- HTTP/API authentication implementation.
- Raw installation-secret generation or delivery.
- Constant-time credential comparison code.
- Credential hashing implementation outside the database contract.
- Credential grace periods or credential-history tables.
- WordPress REST endpoints.
- PHP Moda API client.
- Creating/updating Woo `Shop` rows from application code.
- Reconnect/reinstall application workflows.
- Woo webhook/event ingress.
- BullMQ contracts or Background changes.
- Billing or Woo Marketplace SaaS Billing API.
- `MerchantPricingPlan`, `BillingPlan`, `Subscription`, `BillingPeriod` or credit changes.
- Recovery models or recovery settings.
- Product/coupon/discount persistence.
- Customer provider-ID generalisation.
- Renaming `shopifyShopId`, `shopifyCustomerId` or Shopify-specific billing columns.
- A generic provider-installation framework.
- A generic credential vault.
- Storing Woo REST consumer keys/secrets.
- Persisting WordPress user identity.
- Audit-event design for connection management; later API/Admin work may define it when commands exist.
- Changes to any repository other than `moda-interact-database` plus the assigned parent task report.

## Requirements

### R1 — `Shop.platform` is explicit and backwards-compatible

Every `Shop` has a non-null `ShopPlatform`.

Existing rows migrate to:

```text
SHOPIFY
```

Current Shopify callers that omit `platform` when creating test/development rows continue to receive the Prisma default `SHOPIFY`.

This task MUST NOT require current Shopify application code to change.

### R2 — Woo shops cannot carry a Shopify shop GID

The database constraint must reject:

```text
platform = WOOCOMMERCE
shopifyShopId IS NOT NULL
```

It must continue to allow:

```text
platform = SHOPIFY
shopifyShopId IS NULL
```

because existing tests/development records and lifecycle states already rely on nullable `shopifyShopId`.

### R3 — One Woo installation per Shop

`WooCommerceInstallation.shopId` is unique.

A second installation row for the same `Shop` must be rejected.

### R4 — One canonical Woo site URL per installation identity

`canonicalSiteUrl` is unique and non-blank.

The database does not implement URL canonicalization; the future API must supply a normalized value.

### R5 — Credential material is one-way only

The model stores only a 32-byte `credentialDigest` and integer `credentialVersion`.

No raw credential/secret/token column may be introduced.

### R6 — Credential generation is valid

`credentialVersion` must be strictly greater than zero.

### R7 — Revocation state is internally consistent

Valid states are exactly:

```text
ACTIVE  -> revokedAt IS NULL
REVOKED -> revokedAt IS NOT NULL
```

Inconsistent writes must be rejected by PostgreSQL.

### R8 — Installation cannot be reassigned to another tenant

After creation, `WooCommerceInstallation.id` and `shopId` are immutable.

Changing site URL, credential digest/version/issued time, status or revocation time remains possible for future application-owned lifecycle commands.

### R9 — Shop deletion owns installation deletion

Deleting a `Shop` cascades to its `WooCommerceInstallation`.

The installation guard must not block this cascade.

### R10 — No Woo row is seeded

The migration MUST NOT create a WooCommerce `Shop` or `WooCommerceInstallation` fixture/production row.

### R11 — Existing Shopify state is preserved

Upgrade rehearsal must prove representative existing Shopify rows retain:

```text
id
domain
shopifyShopId
status
installation lifecycle timestamps
```

with only `platform = SHOPIFY` added.

### R12 — Unrelated schemas are unchanged

No ARCH-026 migration change is allowed in:

```text
billing
shopify
whatsapp
support
public
```

except for Prisma-generated relation metadata where the schema source references `Shop`.

Physical migration SQL for ARCH-026 may:

```text
commerce
    add ShopPlatform
    add Shop.platform
    add the required Shop index/check

woocommerce
    create the schema
    create WooCommerceInstallationStatus
    create WooCommerceInstallation
    create the required FK/indexes/checks/guard function/trigger
```

It MUST NOT create `WooCommerceInstallation`, `WooCommerceInstallationStatus` or the Woo installation guard function in `commerce`.

In particular, this task MUST NOT change billing plan/subscription/usage schema.

## Work Items

- [ ] Add `commerce.ShopPlatform` with exactly `SHOPIFY` and `WOOCOMMERCE`.
- [ ] Add `Shop.platform` with default `SHOPIFY` and the `platform,status` index.
- [ ] Add provider-neutral `Shop.onboardingCompleted` with default `false`.
- [ ] Backfill shared `Shop.onboardingCompleted` from existing `shopify.ShopSettings.onboardingCompleted` without removing or renaming the legacy field.
- [ ] Add the database check preventing Woo shops from carrying `shopifyShopId`.
- [ ] Register/create the `woocommerce` PostgreSQL schema without altering existing schema registrations.
- [ ] Add `woocommerce.WooCommerceInstallationStatus` with exactly `ACTIVE` and `REVOKED`.
- [ ] Add `woocommerce.WooCommerceInstallation` with the exact identity, credential and lifecycle shape defined by this task.
- [ ] Add the one-to-one inverse relation on `Shop`.
- [ ] Add required uniqueness, digest-length, version, revocation-state and non-blank-site constraints.
- [ ] Add the `shopId` FK with `ON DELETE CASCADE` / `ON UPDATE RESTRICT`.
- [ ] Add the bounded update guard for immutable `id` and `shopId`.
- [ ] Create `20261002090000_arch026_woocommerce_installation_identity/migration.sql` without rewriting historical migrations.
- [ ] Add a static schema/migration validator for the ARCH-026 contract.
- [ ] Add a PostgreSQL migration rehearsal covering both fresh and upgrade paths.
- [ ] Prove existing Shopify rows are preserved and backfilled as `SHOPIFY` during upgrade.
- [ ] Prove existing Shopify onboarding completion is backfilled to shared `Shop.onboardingCompleted` while the legacy ShopSettings value remains intact.
- [ ] Prove fresh Shops default shared `onboardingCompleted` to false.
- [ ] Prove Woo identity/credential/revocation constraints against PostgreSQL.
- [ ] Prove Shop deletion cascades to the Woo installation row.
- [ ] Add focused package scripts for ARCH-026 schema and migration validation.
- [ ] Regenerate the Prisma ERD through the repository's canonical generator.
- [ ] Verify no raw installation credential is represented in schema/migration/ERD.

## Interfaces / Contracts

This task creates a durable database contract, not an HTTP or queue contract.

### Tenant platform contract

```text
commerce.Shop.platform

SHOPIFY
WOOCOMMERCE
```

Existing Shopify producers continue to rely on the default `SHOPIFY` until/unless a later explicit migration changes them.

Future Woo shop creation MUST set:

```text
platform = WOOCOMMERCE
shopifyShopId = NULL
```

### Woo installation contract

The provider-specific record is physically owned by:

```text
woocommerce.WooCommerceInstallation
```

```text
WooCommerceInstallation.id
    stable Moda installation identifier

WooCommerceInstallation.shopId
    authoritative tenant association

WooCommerceInstallation.canonicalSiteUrl
    canonical merchant WordPress/Woo site URL

WooCommerceInstallation.credentialDigest
    SHA-256(raw installation credential), 32 bytes

WooCommerceInstallation.credentialVersion
    positive current credential generation

WooCommerceInstallation.status / revokedAt
    current authentication eligibility state
```

The future hosted API must treat:

```text
installation id + verified credential digest -> shopId
```

as the authorization identity. Site URL alone is not authentication.

### Contract owner

Schema and integrity owner:

`ARCH-026-DATABASE-001` / `moda_database`

No Shared-package export is required by this database-only task. If a later cross-service HTTP/queue contract requires reusable runtime validation, that later architecture task must assign it to `moda_shared` rather than duplicating validators across services.

## Dependencies

None.

This database capability is independent of the WordPress/PHP scaffold and can execute while WOO-001/WOO-002 are blocked or pending.

Its lack of dependency MUST NOT be interpreted as permission to begin future API integration before those API tasks are separately defined and made Ready.

## Enables

- `ARCH-026-API-002`
- `ARCH-026-SHOPIFY-001`
- `ARCH-026-BACKGROUND-001`

API-002 consumes the Woo installation identity contract. SHOPIFY-001 and BACKGROUND-001 migrate current runtime onboarding lifecycle reads/writes to the shared Shop milestone while retaining the legacy Shopify field as a compatibility mirror.

## Acceptance Criteria

- [ ] `ShopPlatform` exists with exactly `SHOPIFY` and `WOOCOMMERCE`.
- [ ] `Shop.platform` is non-null with Prisma/PostgreSQL default `SHOPIFY`.
- [ ] `Shop.onboardingCompleted` exists, is non-null, and defaults to `false`.
- [ ] Existing pre-ARCH-026 Shop rows are `SHOPIFY` after upgrade migration.
- [ ] Existing Shopify rows with `ShopSettings.onboardingCompleted=true` are backfilled to `Shop.onboardingCompleted=true`.
- [ ] Existing Shopify rows without a true legacy milestone remain `Shop.onboardingCompleted=false`.
- [ ] `shopify.ShopSettings.onboardingCompleted` remains present and unchanged in shape.
- [ ] `Shop_platform_shopify_id_check` rejects a WOOCOMMERCE Shop with non-null `shopifyShopId`.
- [ ] A SHOPIFY Shop with null `shopifyShopId` remains valid.
- [ ] `Shop_platform_status_idx` exists.
- [ ] PostgreSQL schema `woocommerce` exists and is registered in the Prisma datasource.
- [ ] `WooCommerceInstallationStatus` exists in `woocommerce` with exactly `ACTIVE` and `REVOKED`.
- [ ] `WooCommerceInstallation` exists in `woocommerce`, not `commerce`.
- [ ] The Woo installation guard function/trigger is owned by `woocommerce`, not `commerce`.
- [ ] `WooCommerceInstallation.shopId` is one-to-one with `Shop`.
- [ ] `WooCommerceInstallation.canonicalSiteUrl` is unique and rejects blank/whitespace-only values.
- [ ] `WooCommerceInstallation.credentialDigest` rejects any value that is not exactly 32 bytes.
- [ ] `WooCommerceInstallation.credentialVersion` rejects zero and negative values.
- [ ] ACTIVE + non-null `revokedAt` is rejected.
- [ ] REVOKED + null `revokedAt` is rejected.
- [ ] Updating installation `id` is rejected.
- [ ] Updating installation `shopId` is rejected.
- [ ] Updating allowed credential/site/revocation fields remains possible when constraints are satisfied.
- [ ] Deleting a Shop cascades to its WooCommerceInstallation.
- [ ] The migration seeds no Woo Shop or installation row.
- [ ] No raw credential/secret/token field is added.
- [ ] Existing representative Shopify data is preserved through upgrade rehearsal.
- [ ] Billing schema is unchanged by the ARCH-026 migration.
- [ ] Fresh migration rehearsal succeeds from the complete migration history and new Shops default shared onboarding completion to false.
- [ ] Upgrade migration rehearsal succeeds from the immediately preceding migration history and proves shared onboarding backfill while retaining legacy values.
- [ ] Generated ERD reflects `Shop.platform` and `WooCommerceInstallation`.

## Validation

Inspect `package.json` first and use the repository's actual scripts plus the focused ARCH-026 scripts added by this task.

Required validation:

- [ ] clean dependency installation from the repository lockfile;
- [ ] `prisma format` leaves `prisma/schema.prisma` clean;
- [ ] Prisma schema validation passes;
- [ ] Prisma client generation passes;
- [ ] focused static ARCH-026 schema/migration/ERD validator passes;
- [ ] PostgreSQL catalog validation proves the Woo table, enum, guard function and trigger are owned by `woocommerce` and no duplicate Woo objects exist in `commerce`;
- [ ] fresh PostgreSQL migration rehearsal passes;
- [ ] upgrade PostgreSQL migration rehearsal passes;
- [ ] migration rehearsal proves existing Shopify Shop platform preservation/backfill;
- [ ] migration rehearsal proves `Shop.onboardingCompleted` backfill from legacy Shopify settings while the legacy column/value remains intact;
- [ ] migration rehearsal proves fresh Shop onboarding default false;
- [ ] migration rehearsal proves `commerce.Shop` -> `woocommerce.WooCommerceInstallation` cross-schema FK behaviour;
- [ ] migration rehearsal proves Woo installation uniqueness/FK/check/trigger behaviour;
- [ ] migration rehearsal proves cascade deletion;
- [ ] migration rehearsal proves no Woo rows are seeded;
- [ ] migration rehearsal proves no unrelated billing schema mutation;
- [ ] ERD generation succeeds;
- [ ] `git diff --check` passes;
- [ ] changed-file/repository checks required by `moda_database` pass.

The PostgreSQL rehearsal must use disposable local databases only.

Because the existing migration history includes pgvector, use an architecture-approved PostgreSQL image/runtime that can replay the full history, such as:

```text
pgvector/pgvector:pg17
```

Do not point migration validation at development/staging/production durable databases.

The focused migration validator should support explicit isolated URLs/modes rather than discovering arbitrary local databases. Recommended environment names:

```text
ARCH026_FRESH_DATABASE_URL
ARCH026_UPGRADE_DATABASE_URL
```

and explicit modes:

```text
--mode fresh
--mode upgrade
```

If Docker/PostgreSQL required by this validation is unavailable, record the exact environment blocker rather than weakening or skipping required database proof.

## Stop Condition

After all defined Work Items, Acceptance Criteria and required Validation are complete:

```text
finish Completion Report
        ->
set task status to review
        ->
return to moda_architect
        ->
STOP
```

Do not begin a future API, Shared, Gateway or WooCommerce task.

## Implementation Notes

This is intentionally a narrow additive schema change.

Do not use this task as an opportunity to remove historical Shopify naming from the database. That provider-neutralisation work is materially broader and belongs to later architecture where required.

`Shop.platform` is introduced now because future shared Background/API provider dispatch requires an explicit durable platform discriminator. The default `SHOPIFY` protects existing callers and fixtures.

`WooCommerceInstallation` is provider-specific because it represents the security/install boundary of merchant-controlled WordPress infrastructure. It is not a second tenant/domain model; `Shop.id` remains the Moda tenant identity used by shared services.

The raw installation credential is intentionally absent from durable state. SHA-256 is appropriate for a future cryptographically random high-entropy bearer credential; the future API task must generate sufficient entropy and perform constant-time verification.

Do not persist WooCommerce REST consumer secrets in this model. Store/API access is a separate provider-integration question and may not require long-lived consumer credentials at all.

Do not add billing-provider identity here. Woo store platform and billing provider are separate concepts and ARCH-026 billing is explicitly outside this foundation task.

## Completion Report

### Status

Not Started

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

- Existing Shop rows in the current database represent Shopify-era tenants and may safely default to `SHOPIFY` for this pre-production migration.
- One current Woo installation credential per Shop is sufficient for the first connection architecture; overlapping credential rotation is not required yet.
- The future hosted API will canonicalize site URLs before persistence and will never authorize solely from site URL.

### Unresolved Issues

None within this task's database boundary.

### Architectural Concerns

None.

## Architect Review

### Review Status

Pending

### Review Notes

Pending implementation.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending.

### Follow-up

Pending.
