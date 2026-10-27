---
id: ARCH-049-SYSTEM-TEST-001
architecture_id: ARCH-049
title: Certify ShopBrand source ingestion, R2 READY media and WhatsApp image headers
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 90
executor: null
claimed_at: null
attempt: 0
depends_on: ["ARCH-049-ADMIN-001", "ARCH-049-DATABASE-001", "ARCH-049-SHOPIFY-001", "ARCH-049-BACKGROUND-001", "ARCH-049-BACKGROUND-002", "ARCH-049-BACKGROUND-003", "ARCH-049-API-001", "ARCH-049-WOOCOMMERCE-001", "ARCH-049-ADMIN-002", "ARCH-049-BACKGROUND-004", "ARCH-047-ADMIN-005", "ARCH-047-BACKGROUND-001", "ARCH-047-BACKGROUND-003", "ARCH-047-BACKGROUND-006"]
enables: []
created: 2026-10-25
updated: 2026-10-25
---

# Certify ShopBrand source ingestion, R2 READY media and WhatsApp image headers

## Architecture

`ARCH-049` — `docs/architecture/ARCH-049-shopbrand-public-media-configuration.md`; coordinator `moda_architect`. **Portable task definition, not materialised in a developer Git worktree.**

## Objective

Independently validate the integrated Shopify and WooCommerce brand-source flows, durable background image processing, Cloudflare public-media delivery and ARCH-047 approved WhatsApp image-header use without changing implementation repositories.

## Context

This terminal task starts only when its complete ARCH-049 implementation and the **relevant, already-accepted ARCH-047 automated-recovery** consumer dependencies are Complete. Its scope deliberately does not require ARCH-047-BACKGROUND-007 (merchant post-window dispatch). The user may manually test first; System Test validates the system after final integration, not as a prerequisite for more feature implementation.

## Scope

- Build modular black-box fixture/executor/assertion/orchestration/test-data helpers in `moda-interact-system-test` rather than a giant catch-all script.
- Run source ingestion for a Shopify test shop and a Woo WordPress test site through normal authenticated boundaries, then inspect ShopBrand source and processed R2 state.
- Run local test public HTTPS/R2/Meta media mocks plus at least one real custom-domain fetch with approved disposable asset when credentials/environment permit.
- Exercise missing/unsafe/transient/stale media, retries, duplicate events, lost wakes, cross-tenant access and full ARCH-047 image-header payload.

## Out of Scope

- Implementing fixes in app repositories, changing infrastructure configuration, modifying ShopBrand schema or providing a new Meta template authoring service.

## Requirements

### R1. Provider and source scenarios

Prove Shopify `read_brand` capability plus Background initial/daily sync; Woo plugin read→installation-authenticated API→ShopBrand source writes; duplicate or stale provider observations do not corrupt current source; source removal clears current-media eligibility. Include a same-URL changed-byte fixture that is detected by scheduled revalidation.

### R2. Media processing and persistence

Valid JPEG/PNG and padded logo/cover produce immutable content-addressed R2 derivatives with real MIME, width, height, byte count, SHA-256 and matching READY generation. Test malicious URL redirects/metadata targets, too-large/decompression bombs, invalid bytes, R2 outage, retry and worker-crash lease recovery. Verify one role update never deletes another role or crosses shop boundaries.

### R3. R2 external preflight

Verify the user's configured custom domain changes from the screenshot's Initializing to Active, minimum TLS is >=1.2, a disposable image GET returns actual image bytes and matching content-type, and only Background has upload credentials. `r2.dev` public development URL is not used for production media. If the external environment is unavailable, record blocked validation, not a fabricated PASS. If Meta image-header example upload/handle acquisition is missing from the implemented Admin/Background services, record that missing provider prerequisite and stop image-template certification; do not claim full IMAGE-template create/send coverage from mocks alone.

### R4. ARCH-047 consumer behaviour

Admin selects only READY IMAGE role, Meta sample media is distinct from per-shop READY logo, and the ARCH-049-BACKGROUND-004 prepared-media adapter sends one compliant image header from the matching shop in **automated initial and scheduled follow-up recovery**. Merchant-initiated post-window recovery is validated separately by ARCH-047-SYSTEM-TEST-001 after ARCH-047-BACKGROUND-007; it is not an ARCH-049 implementation prerequisite. If no matching READY asset exists, fall back only to an independently approved text-only template or typed no-send; do not send original unprocessed images. Consent/STOP/billing/final-send guards and text-only messages remain unchanged. Verify no AI cart/checkout mutation.

### R5. Evidence

Record actual scenario IDs, seed/cleanup, commands, stdout excerpts/log paths, provider mocks and cross-service correlation IDs. Reconcile observed environment limits without altering ownership or pretending omitted live checks passed.

## Work Items

- [ ] Implement black-box scenarios separated into fixtures/executors/assertions/orchestration.
- [ ] Run valid/error/duplicate/out-of-order/retry/R2 public-delivery paths.
- [ ] Validate ARCH-047 automated recovery image header using the real READY-media resolver and text-only recovery safety. Record that Meta IMAGE creation requires a genuine provider sample handle; do not treat a mock handle as evidence of real provider approval.
- [ ] Record evidence and return for architect acceptance.

## Interfaces / Contracts

Consumes accepted production implementation and its agreed contracts, including existing ARCH-047 runtime image/header preparation. It does not own application data models or write new cross-repository runtime schemas.

## Dependencies

- ARCH-049-ADMIN-001
- ARCH-049-DATABASE-001
- ARCH-049-SHOPIFY-001
- ARCH-049-BACKGROUND-001
- ARCH-049-BACKGROUND-002
- ARCH-049-BACKGROUND-003
- ARCH-049-API-001
- ARCH-049-WOOCOMMERCE-001
- ARCH-049-ADMIN-002
- ARCH-049-BACKGROUND-004
- ARCH-047-ADMIN-005
- ARCH-047-BACKGROUND-001
- ARCH-047-BACKGROUND-003
- ARCH-047-BACKGROUND-006

## Enables

None.

## Acceptance Criteria

- [ ] Both Shopify and Woo source→READY flows are verified end-to-end through authenticated boundaries.
- [ ] A processed image is publicly fetchable over verified HTTPS under the configured domain without exposing private Merchant Knowledge storage.
- [ ] Stale/unsafe/missing images cannot be sent; role/tenant and consent/STOP safeguards are preserved.
- [ ] No relevant planned test is silently skipped or marked passed without evidence.

## Validation

- [ ] Run existing system-test runner with supported arguments only (inspect `--help`, do not use unsupported `--workspace-root`).
- [ ] Execute all ARCH-049 scenario suites in disposable data/environment.
- [ ] Record real public-domain/R2 validation when available and caveat missing credentials.
- [ ] Verify `git diff --check` and report architect acceptance evidence.

## Stop Condition

After the defined Work Items, Acceptance Criteria and Validation are complete, record the Completion Report and change task status to `review`; hand off to `moda_architect` and STOP. Do not continue into a dependent task or change an `_index.md`.

## Implementation Notes

All task work must use the canonical launcher-provided **dedicated parent and implementation worktrees**, synced task/<TASK_ID> branches and start-of-attempt evidence. Inspect the actual pinned package scripts, source and existing conventions before editing. Do not merge branches, push main, edit another repository, start an enabled task or change any `docs/decisions/**/_index.md`. Use structured logging via `@modainteract/moda-interact-shared/logging`; secrets and full untrusted URLs must not enter diagnostics. Document changed files, relevant test commands, results, security/tenant checks, commits and worktree evidence in the Completion Report.

No additional assumptions are authorised.

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
