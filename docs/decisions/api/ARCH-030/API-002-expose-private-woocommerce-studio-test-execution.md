---
id: ARCH-030-API-002
architecture_id: ARCH-030
title: Expose an authenticated private WooCommerce Studio test execution boundary
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 26
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-030-API-001
enables:
  - ARCH-030-GATEWAY-001
  - ARCH-030-COMMERCE-001
created: 2026-10-14
updated: 2026-10-14
---

# Expose an authenticated private WooCommerce Studio test execution boundary

## Architecture

Architecture ID: `ARCH-030`.

Architecture document: `docs/architecture/ARCH-030-woocommerce-commerce-tool-authoring.md`.

Coordinator: `moda_architect`.

## Objective

Give Commerce Studio a strictly authenticated, shop-bound and bounded internal API to execute the accepted Woo GET operation contract.

## Context

API-001 owns provider execution. This task establishes the separately reviewed Commerce->API trust and transport contract; the existing merchant-installation credential must not be reused as a Studio service credential.

## Scope

- Add a private server-to-server read-test route/handler using published Shared runtime validation.
- Authenticate the Commerce service identity; check audience, expiry and request integrity; bind the operation to the server-authorized Shop and allowed caller permissions.
- Map provider result/status to bounded safe responses, with coherent HTTP/API error semantics.

## Out of Scope

- No public merchant-installation proxy or WordPress plugin changes.
- No Commerce UI or new credential storage, `GET` surface outside the approved catalogue, or automatic permission escalation.
- No assumption that private networking by itself grants tenant read authorization.

## Requirements

- Explicitly select and document an approved service authentication mechanism after inspecting current API/Commerce runtime conventions; no browser-held service key.
- Enforce least privilege for request caller, Shop and operation; reject arbitrary forged shop IDs and unknown operations.
- Support future merchant authorization via a server-verified shop principal boundary, but do not expose a merchant Studio role/route today.
- Use hard request/body/time/result limits; preserve API-001 neutral 403-vs-invalid-grant behavior.
- No raw provider diagnostic or credential emitted via JSON, redirects, logs or traces.

## Work Items

- [ ] Implement authenticated private route and explicit ownership of server-trusted Shop context.
- [ ] Add negative tests for missing/wrong/replayed/expired caller identity, cross-Shop spoofing, unsupported method/operation and oversize content.
- [ ] Verify 401/403 provider outcomes survive as safe distinguishable test results and service auth denials fail closed.
- [ ] Document private route and required non-secret configuration names for Gateway wiring.

## Interfaces / Contracts

Uses Shared-001/002 test request/result validators. API-001 supplies approved provider execution. The API service is the credential owner; Commerce is a client only. Do not treat the Woo installation principal as the caller identity for this internal route.

## Dependencies

- `ARCH-030-API-001`

## Enables

- `ARCH-030-GATEWAY-001`
- `ARCH-030-COMMERCE-001`

## Acceptance Criteria

- [ ] Only authorized Commerce service calls against an authorized Shop execute a Woo GET.
- [ ] Forged Shop/operation, expired identity, untrusted request and public/browser requests fail without touching Woo.
- [ ] Endpoint-permission denied is visible with a safe reason; connection remains active when neutral verification passes.
- [ ] Creds/raw provider errors never appear in response or log.

## Validation

- [ ] Focused route auth, tenant isolation, provider-denial and negative-boundary tests.
- [ ] Integration exercise using real API route -> provider fixture against shop/grant state where possible.
- [ ] API build/typecheck/lint declared by package plus git diff --check.

## Stop Condition

After all required Work Items, Acceptance Criteria and Validation pass, record a truthful Completion Report, set `status: review`, return control to `moda_architect` and **STOP**. Do not start dependent tasks or mark this task Complete.

## Implementation Notes

Do not invent a second general-purpose Moda proxy. Document whether existing Render private network/deployment needs Gateway implementation; GATEWAY-001 explicitly owns its wiring.

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

None.

### Unresolved Issues

None recorded yet.

### Architectural Concerns

None recorded yet.

## Architect Review

### Review Status

Pending.

### Review Notes

Not reviewed: portable task definition only.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending implementation.

### Follow-up

Await dependency-gated, launcher-materialised execution and independent review.
