---
id: ARCH-052-MCP-005
architecture_id: ARCH-052
title: Implement secure direct WooCommerce product REST reader in MCP
task_kind: implementation
domain: mcp
repository: moda-interact-mcp
assigned_agent: moda_mcp
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 35
executor: null
claimed_at: null
attempt: 1
depends_on: []
enables:
- ARCH-052-MCP-003
created: '2026-10-30'
updated: 2026-10-30
---

# ARCH-052-MCP-005: Implement the secure direct WooCommerce read adapter

## Architecture

ARCH-052. Parent `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`. Portable task definition.

## Objective

Provide MCP's existing `ApprovedWooProductReader` port with a **direct, read-only WooCommerce REST adapter** using MCP's existing installation/grant records. Do not call the hosted Moda API or implement published tool registration here.

## Context

`src/connections/woocommerce/provider.ts` already takes an `ApprovedWooProductReader`, `runtime/prisma.ts` exposes database access, and the current API repository's `src/woocommerce/rest-read/` is a **security reference**, not an internal HTTP proxy. MCP already has grant eligibility and shop-connection abstractions.

## Scope

- Implement `src/connections/woocommerce/direct-product-reader.ts` exporting `createDirectWooRestProductReader` satisfying the existing `ApprovedWooProductReader` interface; integrate it through the existing `src/runtime/ports.ts` composition without creating another port type.
- Resolve tenant-scoped active installation and read grant for each call; reuse the published Shared `@modainteract/moda-interact-shared/security/credentials/node` keyring, decrypt and AAD primitives; fail closed when keyring/grant missing or invalid.
- Implement bounded GET-only Woo REST product list/retrieve, safe canonical site origin, DNS resolution/pinning, TLS, redirect controls, timeouts, max response bytes, provider status/error mapping and after-read grant recheck. No user-supplied absolute URLs, no public inbound API route, no token/header leakage.
- Match existing `WooCommerceProductReadRequest` operations `products.list`/`products.retrieve`; do not create a product catalogue in PostgreSQL.
- Use Shared logger and existing MCP error mechanism; log bounded event codes, never plaintext credentials, product/customer data or provider response bodies.

## Out of Scope

No Shopify GraphQL changes, discount evaluation, MCP published tool mapping, Commerce Studio publication, API calls, customer cart writes, checkout URL generation, database schema changes or new generic security/crypto implementation.

## Requirements

The same underlying WooCommerce REST API must be contacted **directly by MCP**. Reuse Shared security primitives and current database grant records rather than copying another repository's secret-handling functions. Do not make a private link synonymous with granting arbitrary shop access; keep grants scoped to authenticated shops.

## Work Items

- [x] Implement the production direct reader and wire MCP composition through existing grant/connection interfaces.
- [x] Add fixture-based tests for active/revoked/wrong-shop grants, key rotation, wrong AAD, DNS rebinding/SSRF, redirects, GET-only constraints, timeout/large response, provider 4xx/5xx and race on credential change.
- [x] Validate actual MCP declared scripts, build and module boundaries; return Completion Report.

## Interfaces / Contracts

Use `ApprovedWooProductReader.read({shopId,request,signal,deadlineAt}): Promise<unknown>` from existing `src/connections/woocommerce/provider.ts`. `request` remains the existing `WooCommerceProductReadRequest` union in `src/connections/ports.ts`. **No new Shared schema** is required for this internal reader. MCP-003 consumes this adapter and maps provider data into the canonical Shared product output, including nullable variant IDs and category IDs after SHARED-010 publication.

## Dependencies

None. It can be implemented using existing MCP grants and published Shared credentials without waiting for new discount schemas or Commerce publication.

## Enables

- ARCH-052-MCP-003

## Acceptance Criteria

- [x] Direct authenticated Woo GET requests work without calls to Moda hosted API.
- [x] Tenant/grant/rotation/security checks fail closed with bounded errors.
- [x] Tests cover negative/adversarial origin and credential cases; no unrelated MCP tools or schema files changed.

## Validation

- [x] MCP unit tests for direct reader and selected routes; typecheck/build and `git diff --check`. Docker integration tests remain developer-executed under agent validation policy unless requested.

## Stop Condition

Set status `review`, return Completion Report and STOP; do not start MCP-003.

## Implementation Notes

This is a bounded provider-connection task. MCP-003 retains end-to-end generic tool execution, provider response projection and final product result validation.

## Completion Report

### Status

Implementation complete; submitted for architect review. Attempt 1 remains unchanged. The implementation and task report are committed and published on their task branches.

### Files Changed

- `src/connections/woocommerce/direct-product-reader.ts`
- `src/connections/woocommerce/grant-reader.ts`
- `src/connections/woocommerce/provider.ts`
- `src/runtime/ports.ts`
- `tests/unit/connections/woocommerce/direct-product-reader.test.ts`
- `tests/unit/connections/woocommerce/provider.test.ts`

### Work Completed

- Added a direct, GET-only WooCommerce REST product reader using the current tenant installation and read-grant records, Shared credential keyring/decryption/AAD primitives, canonical HTTPS origin checks, DNS resolution and pinning, peer-address verification, TLS validation, redirect rejection, bounded timeouts and response sizes, provider status mapping, and post-read generation/grant verification.
- Wired the reader into normal MCP persistence composition while retaining the existing injected reader seam for tests.
- Updated stale provider and grant comments/error identifiers to describe the MCP-owned reader.
- Added fixture tests for valid and rotated credentials, revoked and cross-tenant grants, wrong AAD, private DNS answers, redirects, provider 4xx/5xx, response limits, expired deadlines, credential-generation races, list/retrieve paths, and existing provider/runtime behavior.

### Validation Results

- `npm run build` — passed (Prisma client generation and TypeScript production build).
- `npm run lint` — passed.
- `tsc --noEmit -p tsconfig.json` — passed.
- Focused WooCommerce grant-reader/provider/direct-reader and runtime composition tests — 22 passed.
- `git diff --check` — passed.
- Docker integration suites were not run; agent validation policy leaves those developer-executed unless specifically requested.

### Deviations

No scope deviations. The HTTP adapter is MCP-owned as required by ARCH-052; no hosted Moda API call, schema change, or additional port was introduced.

### Assumptions

Production must provide `COMMERCE_CONNECTION_KEYS_JSON` containing the keyring that decrypts the stored Woo REST grant envelopes.

### Unresolved Issues

No implementation issue is known. The direct reader requires the deployment-provided `COMMERCE_CONNECTION_KEYS_JSON` keyring to decrypt stored grant credentials.

### Architectural Concerns

Escalate gaps in published security primitives rather than implement another crypto system.

### Git / VCS

Task branch: `task/ARCH-052-MCP-005`

Physical worktree isolation:
  canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
  parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-052-MCP-005`
  parent branch: `task/ARCH-052-MCP-005`
  implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-052-MCP-005`
  implementation branch: `task/ARCH-052-MCP-005`
  shared workspace checkout switched/mutated for task work: no
  shared implementation checkout switched/mutated for task work: no
  another task worktree reused: no

Start-of-attempt synchronization:
  parent remote task branch fast-forwarded: not-needed
  parent origin/main incorporated: already-current
  implementation remote task branch fast-forwarded: not-needed
  implementation origin/main incorporated: already-current

Implementation repository:
  repository: `moda-interact-mcp`
  commit: `72ca88dd35967607e6749a5aed9b42cc49339d0b`
  remote branch: `origin/task/ARCH-052-MCP-005`
  pushed: yes

Parent workspace:
  task file: `docs/decisions/mcp/ARCH-052/MCP-005-implement-direct-woocommerce-rest-product-reader.md`
  commit: this final task-report commit (see final task-branch HEAD)
  remote branch: `origin/task/ARCH-052-MCP-005`
  pushed: yes
  submodule gitlink staged: no

Merged to implementation main: no

## Architect Review

### Attempt 1 Architect Review

#### Review Status

Accepted — Complete.

#### Review Notes

No findings. The direct WooCommerce REST reader uses the existing tenant-scoped installation and active read grant, Shared credential decryption/AAD primitives, bounded GET-only requests, canonical HTTPS validation, pinned public DNS results, TLS and redirect controls, bounded response handling, and a post-read grant/credential recheck. The adapter is composed through the existing provider port. No hosted Moda API call, schema change, or unrelated implementation was introduced.

#### Reviewed Files

- Attempt 1 Completion Report, task YAML, Work Items, Acceptance Criteria and Validation.
- MCP implementation branch `task/ARCH-052-MCP-005` at `72ca88dd35967607e6749a5aed9b42cc49339d0b`, clean and pushed.
- `src/connections/woocommerce/direct-product-reader.ts`, grant reader, provider, and runtime composition.
- Direct reader and provider unit tests.

#### Validation Reviewed

Reviewed the reported build, lint, TypeScript check, 22 focused tests, and `git diff --check`. Docker integration suites were not run, as permitted by the task's validation instructions. No tests were rerun for this review.

#### Architecture Conformance

Conforms to the MCP-owned, direct, read-only adapter contract and the task's tenant, credential, network, logging, and scope boundaries.

#### Follow-up

The automatic-completion task is complete. `ARCH-052-MCP-003` may proceed when its other dependencies are satisfied.
