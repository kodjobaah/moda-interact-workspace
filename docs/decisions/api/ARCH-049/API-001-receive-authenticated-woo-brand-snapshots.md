---
id: ARCH-049-API-001
architecture_id: ARCH-049
title: Accept authenticated WooCommerce ShopBrand snapshots
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on: ["ARCH-049-DATABASE-001"]
enables: ["ARCH-049-WOOCOMMERCE-001", "ARCH-049-SYSTEM-TEST-001"]
created: 2026-10-25
updated: 2026-10-25
---

# Accept authenticated WooCommerce ShopBrand snapshots

## Architecture

`ARCH-049` — `docs/architecture/ARCH-049-shopbrand-public-media-configuration.md`; coordinator `moda_architect`. **Portable task definition, not materialised in a developer Git worktree.**

## Objective

Add a tenant-authenticated hosted Moda API command to accept WooCommerce's WordPress-native site identity, save the current ShopBrand sources in `commerce.ShopBrand`, and trigger recoverable Background processing without exposing WordPress endpoints.

## Context

WooCommerce runs on merchant-owned infrastructure. The current Moda API has an installation authenticator, bounded request-body utilities and tenant-scoped transaction helpers. Reuse them; do not create a new token protocol.

## Scope

- Add `src/woocommerce/shop-brand/contract.ts`, `request.ts`, `service.ts`, `routes.ts` and focused tests.
- Register an authenticated `POST /v1/woocommerce/shop-brand` route using the canonical Woo installation authenticator.
- Validate bounded body, canonical source fields, timestamps and shop ownership, then persist original ShopBrand data and per-role media source generations using row-level locking.
- Return deterministic idempotent success only after PostgreSQL commit; leave media processing to Background.

## Out of Scope

- Calling merchant WordPress endpoints, fetching/decoding images, R2 uploads, JWT/installation auth redesign, queued events as sole durability, or any new Prisma media table.

## Requirements

### R1. Exact HTTP contract

`POST /v1/woocommerce/shop-brand`, `application/json`, maximum decoded body 16 KiB; installation credentials must authenticate **before** reading the body. Request does not contain and may not override `shopId`; resolve it from authenticated installation principal. Accept exact keys (nullable media fields explicitly null when absent):

```json
{
  "schemaVersion": "woo.shop-brand.v1",
  "eventId": "stable-event-identifier",
  "observedAt": "2026-10-25T12:00:00Z",
  "brandName": "Example Store",
  "logo": {"url":"https://store.example/wp-content/uploads/logo.png", "attachmentId":123, "altText":"Store logo", "width":1200, "height":400},
  "siteIcon": {"url":"https://store.example/wp-content/uploads/icon.png", "attachmentId":456, "altText":null, "width":512, "height":512},
  "coverImage": null
}
```

`brandName` is trimmed Unicode text (max 160 characters), nullable; attachment IDs are positive integers, `url` must be a bounded HTTPS URL (max 2048 chars) or null; pixel dimensions if supplied must be positive integers, metadata names bounded; invalid/missing field set is 400, oversized request 413, unauthorised 401, upstream/DB temporary failure 503. Reject arbitrary extra keys, duplicate headers, malformed encoding and untrusted caller shopId. `observedAt` is UTC ISO-8601; events more than 5 minutes in the future or older than last stored provider observation cannot overwrite current media fields. `eventId` is an opaque stable identifier for retry diagnostics; idempotency is based on canonical source snapshot and observedAt, not an additional events table.

### R2. Canonical mapping

`logo` -> `logoUrl`/alt/dimensions and LOGO role; `siteIcon` -> `squareLogoUrl`/alt and SQUARE_LOGO role; absent cover -> `coverImageUrl=null` and COVER_IMAGE MISSING. `shopId` is the authenticated principal. A successfully authenticated complete snapshot can clear old source roles; transient or malformed requests never do. Preserve `Shop.brand` identity across platform instances, and only allow active matched Woo installations.

### R3. Transaction/idempotency

In a short PostgreSQL transaction, upsert/lock `ShopBrand` by unique shopId, skip duplicate/older canonical snapshots, atomically update brand text/source URLs and affected role JSON generations without losing other roles. Return `200 {"status":"updated"|"unchanged"}` after commit. Do not perform network/R2/BullMQ calls in the transaction. Optional wake is non-authoritative; BG002 due scanner guarantees processing.

### R4. Failure/security

Authenticate using the existing Woo installation boundary, enforce tenant/platform/is-active status, redact image URLs and tokens in structured logs, use the existing no-store JSON response helper, and avoid leaking DB/provider errors to Woo clients.

## Work Items

- [ ] Define exact request/response decoder and authenticated route.
- [ ] Implement PostgreSQL transaction with per-role generations and stale ordering.
- [ ] Register route and add integration tests with current auth harness.
- [ ] Verify no image fetch, WordPress inbound auth change or R2 code.

## Interfaces / Contracts

Producer: Woo plugin `ModaApiClient`. Consumer: Moda API-owned HTTP contract; both implement the same documented `woo.shop-brand.v1` payload. Durable result: `commerce.ShopBrand` source fields and `whatsAppMedia` generation/work statuses. BG002 later processes the PENDING media without a direct API→Background call.

## Dependencies

- ARCH-049-DATABASE-001

## Enables

- ARCH-049-WOOCOMMERCE-001
- ARCH-049-SYSTEM-TEST-001

## Acceptance Criteria

- [ ] Unauthenticated and cross-installation requests cannot mutate ShopBrand.
- [ ] Valid complete snapshot writes source generations atomically and responds only after PostgreSQL commit.
- [ ] Duplicate/older observations do not create new generations or overwrite newer source.
- [ ] Missing/removed source is distinguished from failed request.
- [ ] No new table/queue contract or WordPress server endpoint.

## Validation

- [ ] API contract and body-size/headers/security tests.
- [ ] Database-backed tenant/idempotent/ordering/multi-role update integration tests.
- [ ] Register route in existing composition and verify startup/typecheck/lint/test commands.
- [ ] `git diff --check`.

## Stop Condition

After the defined Work Items, Acceptance Criteria and Validation are complete, record the Completion Report and change task status to `review`; hand off to `moda_architect` and STOP. Do not continue into a dependent task or change an `_index.md`.

## Implementation Notes

All task work must use the canonical launcher-provided **dedicated parent and implementation worktrees**, synced task/<TASK_ID> branches and start-of-attempt evidence. Inspect the actual pinned package scripts, source and existing conventions before editing. Do not merge branches, push main, edit another repository, start an enabled task or change any `docs/decisions/**/_index.md`. Use structured logging via `@modainteract/moda-interact-shared/logging`; secrets and full untrusted URLs must not enter diagnostics. Document changed files, relevant test commands, results, security/tenant checks, commits and worktree evidence in the Completion Report.

Ensure the plugin uses the existing installation credential scheme; no source data or shop IDs are accepted from the untrusted caller as authority for tenant selection.

## Completion Report

### Status

Not Started — defined but not materialised.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

None beyond the explicit architecture/task contract.

### Unresolved Issues

None; live environment availability is a validation prerequisite and must be reported if missing.

### Architectural Concerns

None reported.

## Architect Review

### Review Status

Pending.

### Review Notes

None.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Not reviewed.

### Follow-up

None.
