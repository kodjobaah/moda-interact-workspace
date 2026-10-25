---
id: ARCH-049
title: ShopBrand public-media configuration
status: Agreed
coordinator: moda_architect
created: 2026-10-25
updated: 2026-10-25
---

# ARCH-049: ShopBrand public-media configuration

## Problem

Admin needs a platform-level, non-secret configuration namespace for future
ShopBrand public-media delivery. The broader ShopBrand media-ingestion and
processing design remains unresolved.

## Goals

- Let SUPER_ADMIN configure a public media origin and bucket name.
- Provide usable defaults when no explicit configuration has been saved.
- Preserve the separate private Merchant Knowledge R2 configuration unchanged.

## Non-Goals

This decision does not approve media ingestion, image processing, upload or
delivery behavior; a database schema change; credentials; or a runtime READY
media contract.

## Decision

The configuration contract is:

    shopBrand.publicMedia.publicOrigin = "https://shop-brands.modainteract.com"
    shopBrand.publicMedia.bucketName = "moda-interact-shop-brands"

Both values are non-secret configuration. The public origin is an HTTPS origin,
not an authorization mechanism or proof that an object is available.

Reads resolve saved values or return these defaults without persisting them.
Only an explicit SUPER_ADMIN save persists configuration. Authorization is
enforced server-side. Invalid values are rejected; reads and rejected saves
must not mutate stored configuration.

Use the existing platform-configuration persistence facility. If it cannot
persist this namespace without a database schema change, stop and return the
gap to moda_architect for a separate decision.

## Repository Responsibilities

- `moda_admin` owns the Admin configuration contract, access control, UI and
  use of the existing platform-configuration persistence facility.
- Database schema and migrations are out of scope.
- This decision assigns no media-processing, storage-delivery or worker work.

## Interfaces / Contracts

The non-secret configuration object is:

    {
      "shopBrand": {
        "publicMedia": {
          "publicOrigin": "https://shop-brands.modainteract.com",
          "bucketName": "moda-interact-shop-brands"
        }
      }
    }

Reads may return defaults when no explicit saved value exists. A successful
explicit save returns and persists the validated values. Do not alias,
overwrite, or migrate `merchant.knowledge.r2`.

## Persistence and Failure

A read must never create or update a configuration record. An explicit save
persists both validated values through the existing platform-config mechanism.
If persistence fails, report failure; do not claim the settings were saved.

No database transaction, schema, migration, queue, or object-storage operation
is introduced by this decision.

## Security

Only SUPER_ADMIN may save the configuration. Enforce this at the server
boundary, not only by hiding UI controls. Do not include credentials or secret
fields in this contract.

## Rollout

This is a configuration-surface change only. It does not enable public-media
uploads or change private merchant knowledge storage. No database migration or
deployment sequencing decision is required.

## Decisions / Tasks

| Task | Owner | Status | Depends On |
|------|-------|--------|------------|
| ARCH-049-ADMIN-001 | moda_admin | Ready | None |

Canonical task definition:
`docs/decisions/admin/ARCH-049/ADMIN-001-configure-shopbrand-public-media.md`.

## Open Questions

The full media pipeline remains unresolved, including brand-source ownership,
processing and validation, public delivery operations, retention, and the
runtime READY-media contract. Those decisions are not prerequisites for this
configuration-only task.

## Change History

- 2026-10-25: Agreed the bounded Admin public-media configuration contract;
  left media-pipeline decisions open.