---
id: ARCH-043-API-002
architecture_id: ARCH-043
title: Apply database-managed configuration to hosted API consumers
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 35
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-043-API-001
  - ARCH-043-ADMIN-002
enables:
  - ARCH-043-GATEWAY-001
  - ARCH-043-SYSTEM-TEST-001
created: 2026-10-17
updated: 2026-10-17
---

# Apply database-managed configuration to hosted API consumers

## Architecture

- Parent: `docs/architecture/ARCH-043-database-managed-platform-configuration.md`.
- Contracts: `docs/architecture/ARCH-043-configuration-schema-review.md`.
- Repository owner: `moda-interact-api` / `moda_api`.
- This is a portable task definition; readiness is dependent on accepted `API-001` and `ADMIN-002` completions, not merely the existence of their source code.

## Objective

Connect the accepted `API-001` platform configuration service to the existing hosted API call sites and add the previously agreed, **private Meta-purpose resolver capability** without integrating the Messaging application.

## Context

- Merchant Knowledge reads/commands use `process.env.MERCHANT_KNOWLEDGE_MAX_UPLOAD_BYTES` in `src/composition/merchant.ts`; upload signing/finalisation use `loadUploadR2Configuration()` in `src/merchant/merchant-knowledge/upload-r2.ts` and `upload.service.ts`.
- `src/runtime-config.ts` currently reads the Commerce keyring at process startup; `src/composition/woocommerce.ts` supplies it to `WooReadAuthorizationService`, which holds a single configuration object.
- API private Meta secret resolution has no existing registered route; the capability was previously `ARCH-043-API-003` and is retained **within this task**, not eliminated.

## Scope

**A. Merchant Knowledge:**

- Compose the `API-001` reader once (as an object, not a cached value) and inject it into existing Merchant Knowledge read, command and upload pathways.
- For each upload intent/finalisation, retrieve current `merchantKnowledge.upload` policy and apply maximum upload bytes, XLSX uncompressed limit where consumed, validated endpoint and bucket. Retrieve a consistent policy **once per operation**; never read inside a transaction if external R2 calls would follow within that transaction.
- Replace environment-derived Knowledge policy reads in `src/composition/merchant.ts`, `src/merchant/merchant-knowledge/read.service.ts`, `src/merchant/merchant-knowledge/upload-r2.ts`, `upload.service.ts` and other confirmed API consumers, preserving installation authentication, tenant scoping, upload integrity, idempotency and existing R2 external access-key storage.
- Keep `r2Endpoint` and `r2Bucket` **fully editable**. Do not implement separate asset relocation/in-flight safety workflows, which have other owners; do not silently lock the fields.

**B. Commerce connection keyring:**

- Replace `COMMERCE_CONNECTION_KEYS_JSON` and `COMMERCE_CONNECTION_ACTIVE_KEY_ID` reads in the API REST-read credential path with `requireCommerceConnectionSecurity()` from API-001.
- Refactor `src/runtime-config.ts`, `src/composition/woocommerce.ts`, `src/woocommerce/rest-read/config.ts`, `authorization.service.ts` and directly related handlers as necessary so the current keyring is resolved at the relevant **start/callback/verification operation**, rather than captured only at process startup. Preserve configured public origin and connection-mode security as deployment settings; do not move unrelated variables.
- Preserve ARCH-039 grant ciphertext AAD, old-key decryption during rotation, signed return-locale proofs and callback replay protection. Never recompute a signature using an unrelated later config version within the same operation.
- Ensure a malformed or missing database keyring causes the protected operation to fail closed rather than silently disabling the entire REST-read route or switching back to environment credentials.

**C. Purpose-scoped private Meta secret resolver (former API-003):**

- Create a **private** authenticated route/handler that uses `API-001.requireMetaWebhookSecrets()` and reveals only the fixed `messaging.meta` purpose to an explicitly approved internal service principal. There is **no browser, merchant, generic key name parameter or public secret endpoint**.
- Authenticate the service principal using the architecture-approved Gateway private identity mechanism. Verify provenance, purpose, replay/expiry constraints and that the principal is authorised specifically for the Meta purpose **before** accessing the sealed secret. Never trust spoofable forwarding headers as identity.
- Deny requests if that private identity policy is not provisioned; do not register a publicly reachable permissive fallback. Require Gateway review of private routing/identity before activating this capability. Return `cache-control: no-store`; never log secrets, ciphertext or proof material.
- Do **not** add a Messaging consumer, provide Messaging a Prisma client, issue a Messaging service credential, or change the existing `META_APP_SECRET` / `WHATSAPP_VERIFY_TOKEN` deployment verification path. Their cutover is explicitly excluded from ARCH-043.

## Out of Scope

- No new database schema, Shared cryptography, Admin editor, Messaging runtime change, new secret import mechanism, R2 storage relocation or arbitrary secret-list endpoint.
- No Woo billing credential migration: legacy `API-003-woo-billing-credential-reader.md` belongs to an obsolete prior proposal and is not in the canonical 15-task architecture.
- No environment variable removal from Gateway, unrelated route refactors or `_index.md` changes.

## Requirements

- Every business operation retrieves the required current PostgreSQL row via API-001. No process/Redis cache, TTL snapshots, refresh loop or stale fallback; reuse one read only within the same operation.
- Database/unseal failure, disabled secret tombstone, wrong environment and invalid configuration must fail closed with bounded safe errors. Neither authentication credentials nor R2 signing secrets may appear in merchant/API output or logs.
- Admin-managed secrets must be imported and available before DB-only consumer activation; API-002 depends on architect-accepted `ADMIN-002`.
- Preserve deployment-origin validation, Woo tenant boundaries, webhook callback integrity, upload transaction boundaries and existing API readiness behaviour.
- The private Meta resolver is independently testable, but has **no current Messaging caller**; do not treat endpoint existence as authorization to remove Messaging env secrets.

## Work Items

- [ ] Integrate fresh Knowledge policy reads into upload, finalisation, read projection and other actual limit consumers.
- [ ] Integrate per-operation Commerce keyring retrieval into REST-read authorization and callback/return proof paths; remove only superseded local env reads.
- [ ] Implement fixed-purpose, privately authenticated Meta secret resolver and route gating; coordinate Gateway identity/routing constraints.
- [ ] Add unit, HTTP and disposable PostgreSQL regression tests including credential rotation, tenant security and failures.
- [ ] Record actual files, source branch/worktree evidence, validation results and Completion Report; stop at Review.

## Interfaces / Contracts

- `API-001` server-only typed configuration reader; no duplicate Prisma key lookup, envelope decoder or decryption logic at individual consumers.
- `ADMIN-002` owns authenticated encryption, write-only secrets and secure import; existing `@modainteract/moda-interact-shared/security/credentials/node` owns cryptographic implementations.
- Existing Woo and Merchant route/auth contracts remain authoritative; add no public generic configuration endpoint.
- Gateway owns private routing and internal service identity; API must enforce identity/purpose, not treat network placement alone as authentication.

## Dependencies

- `ARCH-043-API-001`
- `ARCH-043-ADMIN-002`

## Enables

- `ARCH-043-GATEWAY-001`
- `ARCH-043-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Merchant Knowledge read, upload intent/finalisation and size limits use the validated database policy, and existing API-017 lifecycle tests remain green.
- [ ] Woo REST-read start/callback/return authentication and key rotation work without process restart or configuration cache; invalid database keyring does not enable insecure behaviour.
- [ ] Private Meta endpoint rejects public, merchant, unapproved service, spoofed identity, replay and expired proofs; it never returns arbitrary purposes or secrets in logs.
- [ ] No Messaging integration or Messaging environment credential cutover is implemented.
- [ ] Missing/invalid configuration fails closed without falling back to retired env values; health/live and readiness remain unaffected when their own dependencies are healthy.
- [ ] No unrelated source or `_index.md` files modified; task worktree and start-of-attempt evidence present.

## Validation

- [ ] API-017 Merchant Knowledge focused and disposable PostgreSQL upload tests
- [ ] Woo REST-read authorization callback/rotation/locale tests
- [ ] Private Meta endpoint authentication, authorization, replay and route-exposure tests
- [ ] End-to-end API integration against database with changed settings visible on the next operation
- [ ] Full API typecheck, lint, unit tests and production build
- [ ] `git diff --check`

## Stop Condition

After the scoped implementation is validated, fill the Completion Report, set status `review`, return to `moda_architect` and **STOP**. Do not implement Gateway, Messaging or System Test.

## Implementation Notes

- Use existing API handler composition in `src/index.ts`, `src/composition/routes.ts` and `src/composition/woocommerce.ts` without bypassing route auth.
- Provider and cryptographic operations must not run inside a PostgreSQL transaction purely to align secrets; use explicit per-operation snapshots where required.
- Any missing approved Gateway service identity mechanism is an architectural blocker to securely enabling the private resolver, not permission to invent an unauthenticated route.
- Physical parent and implementation worktree isolation with launcher synchronisation evidence is required; no commits or pushes are made by this task definition.

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

Awaiting implementation and validation.

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Not assessed.

### Follow-up

None
