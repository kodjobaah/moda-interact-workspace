---
id: ARCH-035-GATEWAY-001
architecture_id: ARCH-035
title: Configure approved Woo origins for browser-direct R2 upload
task_kind: implementation
domain: gateway
repository: moda-interact-gateway
assigned_agent: moda_gateway
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 48
executor: null
claimed_at: null
attempt: 0
depends_on: [ARCH-035-API-018]
enables: [ARCH-035-WOOCOMMERCE-015, ARCH-035-SYSTEM-TEST-004]
created: 2026-10-17
updated: 2026-10-17
---

# ARCH-035-GATEWAY-001 — Controlled Cloudflare R2 CORS for Woo direct uploads

## Architecture

- Parent: `docs/architecture/ARCH-035-woocommerce-merchant-experience-parity.md`.
- Owner: `moda_gateway`, `moda-interact-gateway`. **Defined but not materialised**; do not claim a branch/worktree in this snapshot.

## Objective

Provision a bounded, auditable R2 CORS and approved-origin enrolment configuration so merchant browsers can perform only API-018-approved presigned `PUT` uploads directly to R2.

## Context

A valid presigned R2 PUT is insufficient for a browser from a WooCommerce store's origin: cross-origin preflight must be allowed by bucket policy. Shopify's existing upload and storage configuration must remain unaffected. Merchant WordPress domains are not trustworthy simply because they are supplied in a request; the policy may grow with authorised installations and is subject to provider origin-count limits.

## Scope

- Inspect the actual R2 bucket, environment, CORS policy and API-018 signed-header evidence before selecting provider-supported, reproducible configuration.
- Implement an operator-controlled, reviewable enrolment/removal and drift-detection mechanism for **approved exact Woo admin origins**; distinguish environment (production/staging/development). Do not trust arbitrary request `Origin` headers or silently edit a shared bucket from the browser.
- Configure only required CORS methods (typically `PUT`) and necessary signed request headers, **including** `Content-Type`, `If-None-Match`, `x-amz-meta-sha256` when API-018 requires them. Keep MaxAge bounded, prohibit wildcard `AllowedOrigins: ["*"]` and broad credentialed access; do not add unrelated public bucket reads.
- Provide deployment instructions for onboarding/new URL/changed origin, policy capacity, safe rollback and failure detection. If approved-origin scale exceeds reliable R2 policy capacity, return a bounded architectural blocker instead of introducing a hidden wildcard or unapproved extra infrastructure.
- Verify allowed and denied preflight behaviour, unchanged Shopify access and any required R2 provider observations, while keeping credentials and signed URLs out of reports.

## Out of Scope

- Issuing signed URLs, hosted API business logic, WordPress/React source, replacing R2 asset storage, database migrations or a new public upload relay.

## Requirements

- CORS is a browser-enforced transport condition, **not** an authentication or tenancy control; signature/metadata/server finalisation remain authoritative.
- Follow Gateway infrastructure/configuration ownership. No committed cloud secrets, no permissive public read and no logged signed URL query strings.
- Do not modify another repository; report any missing deployment/secret wiring separately to `moda_architect`.

## Work Items

- [ ] Inspect API-018 signed-header contract and existing approved R2 bucket CORS.
- [ ] Implement reproducible approved-origin policy with operator reconciliation, drift detection and rollback.
- [ ] Record origin onboarding/removal, scale, environment and deployment instructions.
- [ ] Verify permitted/denied preflight and direct PUT policy without weakening Shopify security.
- [ ] Complete focused infra validation and Completion Report.

## Interfaces / Contracts

- Consumes API-018 signed PUT host/method/required-header contract. Authorised origins must match the administrator browser's real HTTPS Origin exactly. Browser sends **no** Moda credentials to R2.
- R2 S3 API endpoint is used for presigned PUT; no custom public domain is inferred.

## Dependencies

- `ARCH-035-API-018` — must be Complete and architect accepted.

## Enables

- `ARCH-035-WOOCOMMERCE-015`
- `ARCH-035-SYSTEM-TEST-004`

## Acceptance Criteria

- [ ] Approved-origin browser OPTIONS/preflight and signed PUT work; disallowed origins fail browser preflight.
- [ ] Only approved method/headers, exact origin set and environment are configured; existing Shopify CORS preserved.
- [ ] Repeatable provisioning/drift/rollback instructions and missing-origin diagnosis exist; no wildcard origin or unsigned public read/write grant.
- [ ] R2 policy scale/limits and enrolment responsibility documented; any infeasible limit is reported as a blocker.
- [ ] No unrelated repository or `_index.md` files changed.

## Validation

- [ ] Provider-policy/lint/configuration checks, fixture OPTIONS requests and bounded real R2 preflight/PUT tests when credentials permit.
- [ ] `git diff --check`, secret scan and Completion Report with exact evidence or explicit provider-environment limitation.

## Stop Condition

When scoped work and validation finish, set `status: review`, return to architect and STOP; do not begin WOO integration.

## Implementation Notes

- Source-of-truth policy belongs to Gateway even if the provider requires a separately documented API/CLI step. Do not assume R2 CORS accepts dynamic per-request custom origins.
- If R2 policy length/scale makes per-store origin registration infeasible, stop and report the design gap rather than silently expanding scope.

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

None beyond the inspected baseline.

### Unresolved Issues

None yet verified.

### Architectural Concerns

Report R2 origin scale, policy limits or transport conflicts to `moda_architect`.

## Architect Review

### Review Status

Pending.

### Review Notes

Awaiting implementation.

### Reviewed Files

None.

### Validation Reviewed

Not run.

### Architecture Conformance

Pending.

### Follow-up

None.
