---
id: ARCH-052-COMMERCE-006
architecture_id: ARCH-052
title: Bootstrap version-controlled product search and exact-product MCP tool definitions
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
depends_on:
- ARCH-052-SHARED-003
enables:
- ARCH-052-COMMERCE-007
- ARCH-052-MCP-003
- ARCH-052-SYSTEM-TEST-001
- ARCH-052-SYSTEM-TEST-002
created: '2026-10-29'
updated: 2026-10-30
---

# ARCH-052-COMMERCE-006: Bootstrap version-controlled product search and exact-product MCP tool definitions

## Architecture

Architecture ID: `ARCH-052`. Architecture document: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`. Coordinator: `moda_architect`. **Defined but not materialised**; no Git branch or worktree created.

## Objective

Create deterministic code-defined Commerce tool identity/definitions for `commerce_search_products` and `commerce_get_product`, without manual Commerce Studio authoring.

## Context

`src/commerce/bootstrap/merchant-knowledge.ts` is the existing idempotent lifecycle precedent. `commerce_search_products` Shared input/output already exists, but the current executable Shopify core mapping is Shopify-specific. Use a single platform-neutral product lookup operation across both providers.

## Scope

- Add `src/commerce/bootstrap/initial-outreach-products.ts` as a code-owned canonical descriptor and idempotent *prepared bootstrap* for two tool identities and capability keys `commerce_search_products` and `commerce_get_product`, with immutable, fixed names, feature `recovery_initial_outreach` (ensure exact existing feature row or create through existing approved feature-authoring service; do not invent a new DB schema). Tool `definitionVersion:"1.0.0"`, `execution:{kind:"POLICY_OPERATION",operation:"products.search"|"products.get",operationVersion:"1.0.0"}`; mapped inputs are exact published Shared schemas, response templates bounded and safe. Existing Shopify `shopify.searchProducts` remains valid for current conversations; the new product operation is provider-neutral and uses its implementation rather than duplicating search rules.
- Extend Commerce publication authoring/validation metadata in `src/commerce/execution/policy-operation-authoring.ts` and existing Shared definition metadata (`SHARED-008`) so product operations can be authored/validated/published with no manually constructed draft. The bootstrap must be idempotent: compare canonical definition JSON, reject conflicting existing tool/capability, preserve unrelated release members and never silently overwrite merchant-authored definitions.
- **Do not activate a release in this implementation task.** Expose an authorised explicit bootstrap command callable by COMMERCE-007 only; no automatic mutation at ordinary Commerce startup before architect acceptance.
- Tests: exact names/schema/version, repeated prepare, conflicting tool identity, missing SUPER_ADMIN, unsupported platform, no mutation to existing release, missing provider/executable readiness fail closed.

## Out of Scope

No additional database table/column/migration, migration backfill, alternate provider proxy, customer-facing product database/cache, secret-bearing logs, unrelated architecture or other repository implementation.

## Requirements

- Only assigned repository code and this task report may be changed. Do not implement Enabled tasks.
- Follow `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, the exact launcher packet and dedicated mirrored parent/implementation worktrees. Re-read the authoritative task before claiming.
- Use `@modainteract/moda-interact-shared/logging` for new Node structured logs; record unexpected exceptions with bounded reason codes and propagate to the owning error/retry boundary. Never log credentials, complete URLs, coupon codes, raw provider payloads or customer personal data.
- Authenticate every shop/grant/call with its trusted identity, enforce provider deadlines, bounded pagination, strict response projection, customer/tenant separation and read-only provider behavior.
- This is a **pre-production breaking design**. Do not add legacy adapters/backfills or change conversation CommerceAgent lifecycle.

## Work Items

- [ ] Implement exactly the scoped files and runtime behavior.
- [ ] Add deterministic unit and negative/security tests.
- [ ] Run the required validation; record all commands and evidence in Completion Report.

## Interfaces / Contracts

Tool *published names* and `CommerceCapability.key`: `commerce_search_products`, `commerce_get_product`. POLICY_OPERATION keys `products.search`, `products.get` version `1.0.0`; definition version `1.0.0` on first publication. Shared-008 owns schemas; MCP-003 owns execution. Existing Commerce lifecycle remains sole publication authority.

## Dependencies

- `ARCH-052-SHARED-003` — must be Complete and architect-accepted before this task starts.

Dependencies are authoritative in YAML; system tests are terminal validation and must never block implementation.

## Enables

- `ARCH-052-COMMERCE-007`
- `ARCH-052-MCP-003`
- `ARCH-052-SYSTEM-TEST-001`
- `ARCH-052-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] Both tools are bootstrappable solely from version-controlled definitions, not manual Studio UI.
- [ ] Prepared implementation does not activate a tool before MCP executable adapter acceptance.
- [ ] Existing published Commerce features and releases remain intact; reruns are deterministic.

## Validation

- [ ] Commerce authoring/bootstrap unit and integration tests, including no accidental activation.
- [ ] Commerce declared typecheck, lint, build and `git diff --check`.

Use the scripts actually declared by the repository's package/tooling. Record unrun checks as unverified; include `git diff --check`.

## Stop Condition

Once Work Items, acceptance criteria and validation are met, set task status to `review`, complete its report, return to `moda_architect` and **STOP**. Do not mark it Complete, publish another task, merge branches or push `main`.

## Implementation Notes

Expected workspace-relative owned source paths (confirm paths exist in checked-out worktree before editing):

- `moda-interact-commerce/src/commerce/bootstrap/initial-outreach-products.ts` (new)
- `moda-interact-commerce/src/commerce/bootstrap/index.ts`
- `moda-interact-commerce/src/commerce/execution/policy-operation-authoring.ts`
- `moda-interact-commerce/src/commerce/publication/lifecycle.ts` (consume existing interface, no new framework)
- `moda-interact-commerce/tests/`

## Completion Report

### Status

Not Started — portable definition; no task claim.

### Files Changed

None yet.

### Work Completed

None yet.

### Validation Results

Not run.

### Deviations

None reported.

### Assumptions

Confirm execution baseline in dedicated task worktree.

### Unresolved Issues

None established.

### Architectural Concerns

Return material contract/security/proof gaps to `moda_architect` without inventing a workaround.

## Architect Review

### Review Status

Pending.

### Review Notes

Definition only; no implementation accepted.

### Reviewed Files

Task definition and uploaded 29 October 2026 snapshot only.

### Validation Reviewed

No implementation tests yet.

### Architecture Conformance

Pending implementation review.

### Follow-up

Materialise through canonical task launcher only after dependencies are Complete.
