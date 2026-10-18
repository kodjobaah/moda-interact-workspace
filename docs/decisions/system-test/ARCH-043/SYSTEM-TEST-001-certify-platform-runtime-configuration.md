---
id: ARCH-043-SYSTEM-TEST-001
architecture_id: ARCH-043
title: Certify runtime policy configuration across services
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 60
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-043-DATABASE-001
- ARCH-043-ADMIN-001
- ARCH-043-ADMIN-002
- ARCH-043-ADMIN-002
- ARCH-043-BACKGROUND-001
- ARCH-043-BACKGROUND-002
- ARCH-043-API-001
- ARCH-043-API-002
- ARCH-043-API-003
- ARCH-043-COMMERCE-001
- ARCH-043-COMMERCE-002
- ARCH-043-SHOPIFY-001
- ARCH-043-SHOPIFY-002
- ARCH-043-MCP-001
- ARCH-043-ADMIN-004
- ARCH-043-API-004
- ARCH-043-BACKGROUND-008
- ARCH-043-BACKGROUND-009
- ARCH-043-SHOPIFY-003
- ARCH-043-GATEWAY-001
enables: []
created: '2026-10-17'
updated: '2026-10-17'
---

# Certify runtime policy configuration across services

## Architecture

- Architecture: `ARCH-043` — `docs/architecture/ARCH-043-database-managed-platform-configuration.md`.
- Proposed schema/key contract: `docs/architecture/ARCH-043-configuration-schema-review.md`.
- Repository owner: `moda-interact-system-test` / `moda_system_test`.
- Portable definition only: **defined but not materialised**; task worktrees, claims and Git commits must be established by normal task launcher.

## Objective

Independently certify non-secret policy refresh **and** sealed-secret bootstrap, encryption, validation, private distribution and rotation across the required runtime boundaries.

## Context

The system test is terminal and begins after architect acceptance of every implementation/publication prerequisite; the developer may first validate manually.

## Scope

- Run documented non-secret policy scenarios from the six allowlisted policy keys.
- Verify Admin/Commerce/Shopify protected cold starts with encrypted DB secrets and unavailable DB/KMS fail-closed behaviour.
- Verify Commerce keyring decrypts previously stored ciphertext without changing AAD/format; expired/unknown root keys are rejected.
- Verify `messaging.meta` is persisted encrypted and Admin discloses only redacted status; existing Messaging challenge/HMAC verification remains unchanged and continues using its deployment credentials. Do not test a database-backed Messaging integration in ARCH-043.
- Verify the API-003 private resolver denies unapproved identities and protects environment/purpose boundaries; test redacted audit and absence of secrets in logs/browser. No Messaging client is introduced.
- Validate rotation, rollback and Gateway environment cleanup sequencing.

## Out of Scope

- No new implementation code outside test harness; no new deployment secrets, no direct merchant WordPress DB access.

## Requirements
### 17 October 2026 reconciliation acceptance extension

Terminal certification additionally covers `woocommerce.billing`, `shopify.partner` (all three consumers), `shopify.appEvents`, `messaging.sender`, `ai.providers` (both Background operations), explicit reveal/redacted-log checks, and retained Auth.js absent-row-only fallback. Do not claim cursor signing or EmbeddingConfiguration replacement as certified by this extension. System-test execution begins only after all implementation, Gateway and Admin dependencies are architect-accepted Complete.


- No non-system-test task may depend on this test.
- Test should exercise actual supported endpoints/workflows, not only mocks.
- Do not claim architecture Implemented before passing evidence and architect acceptance.

## Work Items

- [ ] Test trusted admin write/audit/CAS with create-clear-stale replay, failed attempts and cross-environment access.
- [ ] Verify configured values take effect for subsequent operations in Background, API, Commerce and Shopify without application-policy redeploy where frameworks permit; document any required worker restart for process construction.
- [ ] Test fresh per-operation reads, Postgres outage, invalid/missing values, no stale cache fallback, editable R2 endpoint/bucket updates, rollback and secret-free persistence/logs.
- [ ] Verify removed environment declarations no longer influence configured runtime.
- [ ] Record actual files changed, validation results, worktree isolation and Completion Report; stop at Review.

## Interfaces / Contracts

- `PlatformConfiguration` and `PlatformConfigurationAudit` are owned by `ARCH-043-DATABASE-001`; schema supports typed non-secret objects and sealed envelopes; environment-scoped and redacted in audit.
- Closed policy shapes are specified in `docs/architecture/ARCH-043-configuration-schema-review.md`. Admin validates before writes; each service independently validates the configuration it consumes. No ARCH-043 Shared publication is required.
- Existing billing, tenant, provider credential and bootstrap contracts retain their established owners.

## Dependencies

- `ARCH-043-DATABASE-001`
- `ARCH-043-ADMIN-001`
- `ARCH-043-ADMIN-002`
- `ARCH-043-BACKGROUND-001`
- `ARCH-043-BACKGROUND-002`
- `ARCH-043-API-001`
- `ARCH-043-API-002`
- `ARCH-043-API-003`
- `ARCH-043-COMMERCE-001`
- `ARCH-043-COMMERCE-002`
- `ARCH-043-SHOPIFY-001`
- `ARCH-043-SHOPIFY-002`
- `ARCH-043-MCP-001`
- `ARCH-043-GATEWAY-001`

## Enables

None

### 18 October non-duplication terminal scenarios

- After cutover, only `merchant.knowledge.r2` controls endpoint, bucket, all R2 credentials and both size limits for API/Shopify/Background; editing a retained legacy `merchantKnowledge.upload` row cannot influence any upload. Conflicting old/new values require explicit reconciliation; audits stay intact; simulated missing/invalid R2 fails without signing/upload.
- Support-message translation uses the **existing Translations** encrypted OpenAI provider credential plus enabled automatic model. Changes to retired `support.translation` and `ai.providers.openAiTranslationApiKey` never affect new support work. An existing queued job retains its selected model; disabled/missing defaults/credentials fail without choosing a second source. Merchant Pricing/Store Category regression workflows retain their own existing behaviour.
- Platform Configuration no longer displays editable duplicate Merchant Knowledge uploads or Support-message translation tabs **after** all dependent implementations are complete; Admin still offers one R2 editor, speech controls and existing System Controls → Translations model/credential pages. No logs/audit/history leak secrets; no new database model/migration or duplicate Background resolver method is required.


## Acceptance Criteria

- [ ] No non-system-test task may depend on this test.
- [ ] Test should exercise actual supported endpoints/workflows, not only mocks.
- [ ] Do not claim architecture Implemented before passing evidence and architect acceptance.
- [ ] The bounded task implementation passes the specified validation without regressions to existing domain configuration.

## Validation

- [ ] Disposable/Postgres integrated execution
- [ ] Real service and environment isolation scenarios
- [ ] Failure-recovery and no-secret assertions

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

Add integrated coverage for Admin/Commerce auth cold-start/login/rotation, Commerce bootstrap admin selector, full six-field R2 cutover, and SQL sealed/redacted protections for the three new keys. WooCommerce global key storage is not a substitute for per-shop grants and must not be called as such.
