---
id: ARCH-035-API-017
architecture_id: ARCH-035
title: Enable Woo knowledge file upload, finalisation and reprocessing
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 46
executor: null
claimed_at: null
attempt: 0
depends_on: [ARCH-035-API-015]
enables: [ARCH-035-WOOCOMMERCE-014]
created: 2026-10-16
updated: 2026-10-16
---

# ARCH-035-API-017 — Enable Woo knowledge file upload, finalisation and reprocessing

## Architecture

- Parent: `docs/architecture/ARCH-035-woocommerce-merchant-experience-parity.md`, approved 16 October functional knowledge extension.
- Owner: `moda_api`, repository `moda-interact-api`; coordinator: `moda_architect`.


## Objective

Provide authenticated Woo CSV/XLSX upload intents and verified durable finalisation/replacement/reprocess lifecycle over the existing R2 and knowledge revision records.

## Context

Shopify `upload.server.ts` supports upload intent/finalise/edit/reprocess but assumes a myshopify.com upload domain. Woo installations use arbitrary store domains. API must not reuse that provider-specific validation or break existing Shopify R2 paths.

## Scope

- Implement signed short-lived upload-intent and verified finalize endpoints plus upload-source metadata edit/replace/reprocess where the existing source model supports them.
- Derive R2 object namespace solely from authenticated Shop: `merchant-knowledge/<env>/woocommerce/<validated-shop-id>/<asset-uuid>/source.<csv|xlsx>`; prove Background can read that namespace and preserve legacy Shopify object-key semantics.
- Enforce allowed source pairs, entitlement/count/file size, accepted MIME/extension, bounds, SHA-256/integrity and object metadata verification; never trust browser-supplied object key, storage URL or shop ID.
- Make intent/finalize idempotent under retries; mark accepted assets/revisions durably, leave eligible durable `PENDING` revisions for Background reconciliation; expire abandoned intents. Fail closed on R2/network/configuration errors.
- Document signed PUT host/expiry/header contract for PHP server-side proxy, strict OpenAPI and bounded secret-free logging.

## Out of Scope

- Direct browser-to-Moda database/Redis/R2 credential access, new unbounded CORS wildcard, WordPress file persistence, Shopify object-key migrations.
- Changing existing Background worker implementation unless a specific gap is escalated and separately approved.

## Requirements

- Preserve existing tenant, credential, platform, entitlement and transaction boundaries; use the source-inspected contracts and Shared package where applicable, not independently guessed interfaces.
- Fail closed on missing or malformed configuration, unauthorised operations and external provider failures. Record bounded structured logging through `@modainteract/moda-interact-shared/logging` when changing generic application logs.
- Keep production components modular and independently testable; no monolithic files or cross-repository implementation changes. Preserve Shopify runtime and existing Woo merchant Billing, recovery and navigation behaviour.
- If implementation discovers a genuine missing Background/Shared/Gateway capability, stop and return the precise evidence to `moda_architect` rather than extending another repository's scope.

## Work Items

- [ ] Implement signed short-lived upload-intent and verified finalize endpoints plus upload-source metadata edit/replace/reprocess where the existing source model supports them.
- [ ] Derive R2 object namespace solely from authenticated Shop: `merchant-knowledge/<env>/woocommerce/<validated-shop-id>/<asset-uuid>/source.<csv|xlsx>`; prove Background can read that namespace and preserve legacy Shopify object-key semantics.
- [ ] Enforce allowed source pairs, entitlement/count/file size, accepted MIME/extension, bounds, SHA-256/integrity and object metadata verification; never trust browser-supplied object key, storage URL or shop ID.
- [ ] Make intent/finalize idempotent under retries; mark accepted assets/revisions durably, leave eligible durable `PENDING` revisions for Background reconciliation; expire abandoned intents. Fail closed on R2/network/configuration errors.
- [ ] Document signed PUT host/expiry/header contract for PHP server-side proxy, strict OpenAPI and bounded secret-free logging.
- [ ] Add focused positive and negative coverage and complete the required validation/Completion Report.

## Interfaces / Contracts

- POST `/v1/merchant/merchant-knowledge/upload-intents`; POST `/v1/merchant/merchant-knowledge/upload-finalize`; PATCH `/v1/merchant/merchant-knowledge/uploads/{sourceId}`; POST `/v1/merchant/merchant-knowledge/uploads/{sourceId}/reprocess`.
- Versioned short-lived upload authorization is for server-side PHP to R2 only; API-015 defines canonical source read-back.

## Dependencies

- `ARCH-035-API-015` (must be Complete and architect accepted)

## Enables

- `ARCH-035-WOOCOMMERCE-014`

## Acceptance Criteria

- [ ] Valid CSV and XLSX uploads produce exactly one owned asset and correct source/revision on repeated finalize; expired/tampered/wrong-Shop file fails closed.
- [ ] `*.myshopify.com` restriction is not bypassed for Shopify; Woo uses authenticated stable Shop identity and Background reads the stored asset.
- [ ] Large, wrong MIME, wrong hash, invalid file extension, quota, inaccessible R2 and revoked installation have explicit safe errors.
- [ ] Merchant-off configuration remains possible while off without claiming ingestion; source replacement/reprocess observes existing lifecycle.
- [ ] No `_index.md` files or unrelated domains modified; canonical dual-worktree/branch validation evidence recorded in real development workspace.

## Validation

- [ ] Focused R2 signer/object validation tests, disposable PostgreSQL upload/replace/retry tests and representative Background asset retrieval proof.
- [ ] Typecheck, lint, build, bounded security/log review and `git diff --check`.
- [ ] Record concrete commands and results, implementation and parent task branch/commit evidence, canonical physical-isolation/synchronisation evidence, plus deviations and unresolved issues.

## Stop Condition

When this bounded task's Work Items, Acceptance Criteria and required Validation are satisfied, update Completion Report, set `status: review`, return to `moda_architect` and STOP. Do not start tasks listed under Enables.

## Implementation Notes

### Reconciled API-structure handoff (2026-10-16 22:56 snapshot)

- Implement upload/finalise/replace/reprocess as separate, bounded modules under `src/merchant/merchant-knowledge/` with API-only R2 signing/object verification dependencies. Register via `src/composition/merchant.ts`, with Woo authentication from `src/auth/woo-installation/` and HTTP helpers from `src/http/`. Do not import `moda-interact/app/services/merchant-knowledge/upload.server.ts` (it depends on Remix aliases, Shopify domain identity and Shopify server configuration); use it only to preserve existing model/revision semantics.
- The uploaded API `src/runtime-config.ts` does **not** yet define Merchant Knowledge R2 configuration, and `package.json` does not currently declare an R2/AWS signing SDK. Explicitly add bounded, injectable server-only configuration/dependencies where needed, without making unrelated merchant read routes depend on R2 startup availability. Fail closed on upload operations if signing/bucket/environment settings are missing or malformed. Record any new deployment secret/Render Blueprint requirement for architect/Gateway ownership; never commit secret values.
- Derive Woo R2 keys from the authenticated Shop ID, validated deployment environment and server-generated asset UUID, preserving all Shopify keys. Confirm Background's uploaded-asset acquisition reads the persisted object key independently of Shopify domain pattern. Document the signed PUT destination and required headers for the WordPress server-side transport, with redirects, private/loopback destinations and unintended hosts rejected by the plugin.
- Keep durable asset intent/finalise and source revisions transactionally safe; verified R2 metadata (size/type/SHA-256) must match the expected intent before activating. Background's existing durable `PENDING` revision reconciler provides eventual queue delivery; do not introduce an unapproved BullMQ requirement or a network call in the transaction. Cover repeated finalise, aborted upload/expiry, replacement, wrong bytes and error isolation.
- Unit/R2 simulation tests belong under `tests/unit/merchant/merchant-knowledge/`, PostgreSQL lifecycle tests under `tests/integration/merchant/merchant-knowledge/`, with runner integration and `openapi/merchant-knowledge-v1.yaml` updates.

The historical superseded ARCH-035-API-003/004/005 must **not** be revived; this task follows the newly agreed architecture amendment and consumes only approved contract owners. An unimplemented API or feature must never be represented as operational. Do not update any `docs/decisions/**/_index.md` until the developer closes the architectural session.

## Completion Report

### Status

Not Started.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

The uploaded ZIP represents a portable design baseline, not the developer's current on-disk branches. Confirm source, task status and dependency state with the launcher before execution.

### Unresolved Issues

None evidenced beyond the explicit implementation and test dependencies above.

### Architectural Concerns

Report any cross-repository contract, R2 identity, reconciliation or security mismatch to `moda_architect`.

## Architect Review

### Review Status

Pending.

### Review Notes

Awaiting implementation and validation evidence.

### Reviewed Files

None.

### Validation Reviewed

Not run.

### Architecture Conformance

Pending.

### Follow-up

None until implementation submission.
