---
id: ARCH-043-API-001
architecture_id: ARCH-043
title: Read Merchant Knowledge upload policy from database
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
depends_on:
- ARCH-043-DATABASE-001
- ARCH-043-ADMIN-002
enables:
- ARCH-043-GATEWAY-001
- ARCH-043-SYSTEM-TEST-001
created: '2026-10-17'
updated: '2026-10-17'
---

# Read Merchant Knowledge upload policy from database

## Architecture

- Architecture: `ARCH-043` — `docs/architecture/ARCH-043-database-managed-platform-configuration.md`.
- Proposed schema/key contract: `docs/architecture/ARCH-043-configuration-schema-review.md`.
- Repository owner: `moda-interact-api` / `moda_api`.
- Portable definition only: **defined but not materialised**; task worktrees, claims and Git commits must be established by normal task launcher.

## Objective

Use the single sealed `merchant.knowledge.r2` environment-scoped configuration to obtain the complete six-field R2 upload snapshot for Merchant Knowledge operations. API-002/003 retain their other independently scoped capabilities.

## Context

API-017 upload handling currently reads environment limits and R2 storage location.

## Scope

- Read one sealed `merchant.knowledge.r2` row for each relevant upload intent/finalisation operation, with the current version and all six validated fields; do not read `merchantKnowledge.upload` or merge external R2 secrets after cutover.
- Apply upload and XLSX hard caps before signing, upload finalisation and validation.
- Decrypt the complete R2 tuple server-side with the approved ARCH-039 Node crypto/AAD; never expose credentials in signed responses, logs or browser, and fail closed for missing/revoked/malformed rows.
- Update config/documentation and focus on preserving existing idempotency and source revision lifecycle.

## Out of Scope

- No Commerce keyring, Meta ingress secret service, or bootstrap secret implementation.

## Requirements

- Invalid/unconfigured R2 location must fail closed.
- Cross-environment config may not be read by another deployment.
- No per-request database read for config at normal throughput.

## Work Items

- [ ] Read one sealed `merchant.knowledge.r2` snapshot afresh per relevant upload operation; no cross-operation cache or legacy policy fallback.
- [ ] Apply upload and XLSX hard caps before signing, upload finalisation and validation.
- [ ] Decrypt and validate complete R2 endpoint/bucket, access/secret keys and both limits server-side; never expose credentials or fall back to env after cutover.
- [ ] Update config/documentation and focus on preserving existing idempotency and source revision lifecycle.
- [ ] Record actual files changed, validation results, worktree isolation and Completion Report; stop at Review.

## Interfaces / Contracts

- `PlatformConfiguration` and `PlatformConfigurationAudit` are owned by `ARCH-043-DATABASE-001`; schema supports typed non-secret objects and sealed envelopes; environment-scoped and redacted in audit.
- Closed policy shapes are specified in `docs/architecture/ARCH-043-configuration-schema-review.md`. Admin validates before writes; each service independently validates the configuration it consumes. No ARCH-043 Shared publication is required.
- Existing billing, tenant, provider credential and bootstrap contracts retain their established owners.

## Dependencies

- `ARCH-043-DATABASE-001`

## Enables

- `ARCH-043-GATEWAY-001`
- `ARCH-043-SYSTEM-TEST-001`

### 18 October R2 migration review contract

- Required actual source inspection: `src/merchant/merchant-knowledge/upload-r2.ts`, `upload.service.ts`, their route/composition and tests. Preserve integrity of presigned upload intent/finalisation, safe endpoint allowlist/HTTPS, XLSX cap and size checks.
- For an existing legacy revision, prove migration into a single `merchant.knowledge.r2` snapshot without silently changing endpoint/bucket or caps; conflicts with already-configured sealed values require operator resolution. A failed read/decipher must not reuse `merchantKnowledge.upload` or environment credentials once cut over.
- Validate real upload against configured bucket and retention/in-flight relocation rules; no automatic asset migration in this task. Verify no unused per-request DB lookups beyond the bounded operation and no changes to API shop authentication.


## Acceptance Criteria

- [ ] Invalid/unconfigured R2 location must fail closed.
- [ ] Cross-environment config may not be read by another deployment.
- [ ] No per-request database read for config at normal throughput.
- [ ] The bounded task implementation passes the specified validation without regressions to existing domain configuration.

## Validation

- [ ] Upload policy and R2 endpoint validation unit tests
- [ ] Existing API-017 PostgreSQL integration regression
- [ ] Fresh-read-on-next-operation, environment scoping, missing/invalid config tests
- [ ] Typecheck/lint/build

## Stop Condition

Complete the defined scope and required validation, update the task and Completion Report to Review, return to `moda_architect`, and STOP. No execution of enabled tasks and no `_index.md` edits.

## Implementation Notes

- Preserve service ownership boundaries and existing published ARCH-039 credential functions. Use the ARCH-043 documented policy shapes and AAD byte convention; do not invent a new crypto codec or require new Shared publication.
- Changes to shared generic logging, if needed, must use `@modainteract/moda-interact-shared/logging`.
- Use launcher-resolved dedicated task worktrees and start-of-attempt synchronisation evidence.

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

Not run

### Deviations

None

### Assumptions

None

### Unresolved Issues

None

### Architectural Concerns

None

## Architect Review

### Review Status

Pending

### Review Notes

Awaiting implementation, validation evidence and architect decision.

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Not yet assessed.

### Follow-up

None

## 17 October 2026 ARCH-043 extension (architect-owned amendment)

Read one sealed `merchant.knowledge.r2` record (all six fields) via ARCH-039 decrypt and strict validation. It replaces `merchantKnowledge.upload` as authoritative after cutover; include endpoint/bucket/keys/limits in one read. Requires ADMIN-002 and the developer forward migration, and preserve API-017 hard cap/SSRF. The previous non-secret policy reader description is superseded; do not keep credential environment reads after verified cutover.
