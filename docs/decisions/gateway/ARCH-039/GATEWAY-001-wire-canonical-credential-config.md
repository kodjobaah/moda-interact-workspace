---
id: ARCH-039-GATEWAY-001
architecture_id: ARCH-039
title: Enforce canonical hosted credential-secret wiring in Render Blueprints
task_kind: implementation
domain: gateway
repository: moda-interact-gateway
assigned_agent: moda_gateway
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: in_progress
priority: 20
executor: developer
claimed_at: 2026-10-15T09:24:15Z
attempt: 1
depends_on:
  - ARCH-024-GATEWAY-001
  - ARCH-039-ADMIN-001
  - ARCH-039-ADMIN-002
  - ARCH-039-BACKGROUND-001
  - ARCH-039-BACKGROUND-002
  - ARCH-039-COMMERCE-001
  - ARCH-039-COMMERCE-002
  - ARCH-039-MCP-001
  - ARCH-039-API-002
enables:
  - ARCH-039-SYSTEM-TEST-001
created: 2026-10-14
updated: 2026-10-15
---


# Enforce canonical hosted credential-secret wiring in Render Blueprints

## Architecture

Architecture ID: `ARCH-039`
Architecture document: `docs/architecture/ARCH-039-canonical-credential-security.md`
Coordinator: `moda_architect`
Owner: `moda_gateway` / `moda-interact-gateway`

## Objective

Enforce canonical hosted credential-secret wiring in Render Blueprints. This is one bounded, repository-owned outcome; do not move to another task on completion.

## Context

ARCH-039 makes one published credential security mechanism authoritative for hosted Node services. The developer has chosen a non-production data clear rather than historical encryption-key migration. This task is part of the agreed staged adoption plan; see the parent architecture for exact cross-service invariants.

## Scope

- Update `render.test.yaml` and `render.production.yaml` only as required to attach the existing canonical credential-keyring and writer groups to authorised services, **including the API**.
- Update `tests/validate-render-blueprints.sh` and negative tests for group wiring, canonical variable names, secret access matrix and removal of Woo-specific keyring names; update deployment docs.

## Out of Scope

No application code or database modifications. No sensitive secret values in artifacts.

## Requirements

- **Mandatory closed-set credential configuration:** for AES credential encryption/decryption, credential key selection and Commerce connection-command HMAC, the **only permitted environment variable names anywhere in ARCH-039 runtime configuration** are `COMMERCE_CONNECTION_KEYS_JSON`, `COMMERCE_CONNECTION_ACTIVE_KEY_ID` and `COMMERCE_CONNECTION_COMMAND_HMAC_KEY`. No other names, aliases, old Woo keyring variables, service-specific encryption/HMAC variables, dual-read, fallback, generated defaults or alternate sources may be used for these purposes. Other unrelated application environment settings are unaffected.
- In **both** `render.test.yaml` and `render.production.yaml`, these **exact three names are the only permitted declarations** for this architecture: `COMMERCE_CONNECTION_KEYS_JSON` (authorised readers/writers), `COMMERCE_CONNECTION_ACTIVE_KEY_ID` (writers only), `COMMERCE_CONNECTION_COMMAND_HMAC_KEY` (Commerce only). Reject any legacy/alias/service-specific credential-encryption or Commerce command-HMAC declaration, group alias, per-service duplicate or fallback configuration; do not change unrelated variables.

- Reuse existing groups for `COMMERCE_CONNECTION_KEYS_JSON` (readers and writers) and `COMMERCE_CONNECTION_ACTIVE_KEY_ID` (writers only).
- `COMMERCE_CONNECTION_COMMAND_HMAC_KEY` remains a Commerce-only `sync:false` secret (not keyring group and not distributed to API/Admin/Background/MCP).
- API is authorised keyring+active-key writer; Admin/Commerce are other writers; authorised Background decryptors and MCP are readers only. Public Gateway, messaging ingress, WordPress/WooCommerce, Shopify merchant browser and unrelated workers never receive them.
- Separate test and production values; no committed secret values, no shadow/legacy Woo keyring values, no duplicate per-service key declarations.
- `ARCH-024-GATEWAY-001` must be accepted Complete before this task starts; reconcile to its final wiring rather than reintroducing Preview API-key config.

## Work Items

- [ ] Extend Blueprint static and negative checks to reject any credential-security env alias, legacy-only variable, shadow declaration and unauthorised service attachment; verify the three exact names in both test and production.

- [ ] Audit existing test/prod service attachment lists and change only demonstrated required recipients.
- [ ] Add API group attachments; revise allowlists/forbidden inputs; remove/forbid legacy Woo encryption variables.
- [ ] Update operator documentation for canonical Base64 keyring, writer selection, HMAC isolation, dev data clear-and-cutover and failure handling.
- [ ] Test positive and negative Blueprint validation for over-sharing, under-sharing and duplicate secret declarations.

## Interfaces / Contracts

- Canonical hosted environment names and secret-group distribution. No runtime key generation or deployment.

## Dependencies

- ARCH-024-GATEWAY-001
- ARCH-039-ADMIN-001
- ARCH-039-ADMIN-002
- ARCH-039-BACKGROUND-001
- ARCH-039-BACKGROUND-002
- ARCH-039-COMMERCE-001
- ARCH-039-COMMERCE-002
- ARCH-039-MCP-001
- ARCH-039-API-002

## Enables

- ARCH-039-SYSTEM-TEST-001

## Acceptance Criteria

- [ ] Both Blueprints and positive/negative validator fixtures enforce only these three credential-security identifiers and the exact service access matrix, rejecting aliases, legacy-only wiring, duplicates and forbidden recipients.

- [ ] All in-scope hosted credential users receive exactly their required canonical env vars in both manifests.
- [ ] API receives keyring+writer selector; HMAC stays Commerce-only; readers never need active selector.
- [ ] No legacy Woo encryption env or committed secret values; positive/negative Blueprint tests pass.
- [ ] Non-production clear/cutover is documented as developer-owned, not performed by Gateway.

## Validation

- [ ] Gateway `tests/validate-render-blueprints.sh`
- [ ] Gateway negative Blueprint tests
- [ ] Gateway deployment config validation scripts and `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, update only this task's allowed metadata and Completion Report, set `status: review`, return to `moda_architect`, and STOP. For developer completion, an explicit developer approval is required after accepted review.

## Implementation Notes

No live Render deployment or secret creation by the agent. No deployment metrics redesign.

Use the canonical parent/implementation task-worktree preparation protocol, preserve dedicated worktree and start-of-attempt synchronization evidence, and do not edit `docs/decisions/**/_index.md` before architecture-session confirmation. No direct changes to another agent's repository.

## Completion Report

### Status

In Progress — Attempt 1 claimed by developer at 2026-10-15T09:24:15Z. Attempt 0 review history is preserved below.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

None beyond the parent architecture.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

Pending

### Review Notes

Not yet reviewed.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending review.

### Follow-up

None.
