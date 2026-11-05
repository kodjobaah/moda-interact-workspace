---
id: ARCH-058-COMMERCE-002
architecture_id: ARCH-058
title: Remove cryptographic cursor validation from commerce pagination
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables: []
created: 2026-11-05
updated: 2026-11-05
---

# ARCH-058-COMMERCE-002: Remove cryptographic cursor validation

## Architecture

ARCH-058; docs/architecture/ARCH-058-commerce-agent-product-discovery.md. Coordinator: moda_architect. This explicitly overrides earlier signed-cursor requirements in ARCH-058-MCP-002 and historic product pagination definitions.

## Objective

Make Commerce preview adapters paginate without cryptographic cursor validation or a cursor secret.

## Context

Developer explicitly requested removal after absent COMMERCE_CURSOR_SECRET hid commerce_search_products. This is removal, not improved error handling. Existing tenant authorization remains the security boundary.

## Scope

Commerce local preview product pagination and adapter availability. Inspect src/commerce/products/index.ts and src/commerce/preview/local-policy-providers.ts plus owning tests/docs/environment examples. Remove the secret gate that currently returns only merchantKnowledge adapters. Cover every paginated local product adapter and any other Moda cursor crypto found in the repo. Preserve native discount-provider pagination and server-side policy authorization; do not reintroduce production execution into Studio or change standalone MCP client transport.

## Out of Scope

Other repository implementation; credential encryption; authentication; tenant isolation; new Shared wire contracts; deployment/cutover; unrelated cleanup.

## Requirements

Remove Moda cursor signing, encryption/authentication, expiry enforcement and query/shop/connection/mode/policy fingerprint binding checks. Remove COMMERCE_CURSOR_SECRET configuration, minimum-length gates and dependency injection from the owning runtime. A continuation is untrusted pagination position only; it never supplies shop identity, provider host, credentials, authorization, policy, SQL fragments or entitlement. Resolve those from the authenticated current call every time. Retain bounded string/JSON parsing, known version/shape, finite safe nonnegative offsets and bounded IDs/provider tokens, existing Shared 2048-character wire bound, page/scan/output limits, parameterized database queries and provider cancellation/deadlines. Do not add another secret, database cursor store, compatibility signature verifier or alternate generic crypto implementation.

New continuations are unsigned versioned position envelopes (base64url JSON where multiple progress fields are needed); fields contain only progress, not auth/query bindings. They are not encrypted: never serialize secrets, customer payloads or tenant context. Forward native upstream opaque cursors unchanged inside the position envelope to the current authenticated provider; never decode/rewrite provider-owned cursors or accept provider URLs/SQL. Remove cursor-based filter/mode/fingerprint mismatch rejection; apply the current call's normal filters and policy to every returned row. Changing filters may restart/skip/duplicate positions; pagination is not a snapshot or correctness authority. Current NONE/disabled policy still denies data even with a supplied cursor.

Compatibility: make a coordinated breaking deployment of these internal pre-production continuations. Old Moda HMAC product v2, encrypted catalogue and Commerce signed tokens are not migrated or verified: return the established bounded INVALID_INPUT restart instruction, allowing the caller to retry from cursor null. Do not infer legacy tokens as arbitrary valid provider cursors. No public tool names, Shared cursor field types or provider cursor protocols change. Rollback restarts pagination; no durable business data migration. Confirm actual deployment context before execution; if production compatibility is now required, return that conflict to the architect rather than inventing a bridge.


## Work Items

- [ ] Inventory all owned paginated operations and remove cursor cryptography/binding/secret gates.
- [ ] Preserve bounded parsing, current-call authorization and provider/database safety.
- [ ] Update focused tests, environment examples and runtime documentation.

## Interfaces / Contracts

Keep published Shared tool input/output schemas, cursor null/string fields and maximum lengths unchanged. Upstream cursors stay provider-owned opaque data. No cross-service credential changes or new published contract required. MCP task ARCH-058-MCP-004 owns the production private runtime.

## Dependencies

None. The existing implemented pagination surfaces are available; these repository-owned removals can be reviewed independently.

## Enables

None. Execution does not authorize follow-on tasks or system-test runs.

## Acceptance Criteria

- [ ] All owned paginated operations work with absent, short or formerly configured cursor secret, with no cursor cryptographic or binding check.
- [ ] Valid unsigned pagination progresses; malformed/oversized/unsafe progress is bounded and rejected.
- [ ] Old Moda signed/encrypted cursors request restart without secret or verification.
- [ ] Changed query/filter does not trigger old cursor binding checks.
- [ ] Cross-tenant copied/manipulated positions cannot access another shop or bypass current policy.
- [ ] Provider opaque cursors pass through unchanged; no host/query injection or unbounded scan.
- [ ] Docs/config no longer require COMMERCE_CURSOR_SECRET for owned runtime.
- [ ] No credential encryption/authentication control was removed.

## Validation

- [ ] Inspect package.json and run declared focused pagination/executor/advertisement tests.
- [ ] Cover no-secret listing/call, multiple pages, changed filters, legacy cursor restart, malformed progress, current-policy NONE/denial and two-tenant isolation.
- [ ] Run repository-declared typecheck/build required by local instructions; record exact commands/results.
- [ ] Search owned runtime/config for residual cursor secret/crypto gates; explain unrelated cryptography retained.

## Stop Condition

After Work Items, Acceptance Criteria and required Validation, finish Completion Report, set review, return to moda_architect and STOP. No deployment or follow-on execution.

## Implementation Notes

Use current code as baseline, not an old ARCH-058 patch. Retain semantic operational logging without customer/cursor payload exposure. Standard provider validation errors remain provider errors; removing Moda cursor binding does not remove authorization.

## Completion Report

### Status
Not Started

### Files Changed
None

### Work Completed
None

### Validation Results
None

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
Task definition only; no implementation claim or acceptance.

### Reviewed Files
None

### Validation Reviewed
None

### Architecture Conformance
Pending implementation.

### Follow-up
None
