---
id: ARCH-032-MCP-008
architecture_id: ARCH-032
title: Extract pinned Shopify Admin compiler and restricted response renderer
task_kind: implementation
domain: mcp
repository: moda-interact-mcp
assigned_agent: moda_mcp
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: pending
priority: 8
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-032-MCP-007
enables:
  - ARCH-032-MCP-009
created: 2026-10-10
updated: 2026-10-10
---

# Pinned Shopify Admin compiler and restricted response renderer

## Objective

Provide the formerly missing `ShopifyPublishedDefinitionRuntime` compiler and
Nunjucks renderer port within the standalone MCP repository, maintaining
Commerce's published-definition validation and bounded result behaviour.

## Scope

- Extract the existing Commerce Admin GraphQL compilation/derivation rules and
  canonical result-schema validation for Shopify published definitions.
- Preserve the exact Commerce 2026-07 Admin artifact SHA-256 and provenance.
  The archived snapshot does **not** contain the artifact. Provide an explicit
  hash-verifying installation command, not a guessed schema.
- Extract the restricted Nunjucks AST validator and response renderer,
  including AST limits, bounded traversal, prohibited accessors, forbidden
  filters/globals and division/modulo-by-zero protection.
- Keep shop authorization, existing provider transport, OpenAPI and endpoint
  mounting unchanged. Do not enable the live MCP endpoint.
- Do not copy third-party credentials, change database schema, or add a network
  schema download. Keep the existing Commerce source operational.
- Keep tests under `tests/unit/`; include positive and negative GraphQL
  compiler fixtures and renderer parity/failure cases.
- No `docs/decisions/**/_index.md` changes.

## Acceptance Criteria

- No published Shopify definition is considered compatible unless its named
  read-only GraphQL query, argument mappings and derived result shape validate
  against the pinned schema and the restricted response template is valid.
- Wrong/missing schema artifacts fail closed before Shopify provider I/O.
- The renderer verifies normalized bounded structured results and produces
  Commerce-compatible `CommerceToolResult` envelopes.
- Unit tests cover publisher-schema hash rejection, forged result schema,
  mutation/unbounded selections, optional data, unsafe Nunjucks, runtime
  arithmetic failure and output bounds.
- `npm ci`, `npm run typecheck`, `npm run lint`, `npm test` and `npm run build`
  pass on the repository's required Node toolchain.
- No source or tests are created in Commerce, Background, API, Database,
  Gateway or Shared; no new PostgreSQL-migrating code is introduced.
- Existing MCP-007 disposable PostgreSQL integration remains a required
  regression test, but this task does not add an unrelated database fixture.

## Validation

- [ ] Confirm artifact provenance with Commerce-generated `admin-2026-07.json`
      from pinned `@shopify/dev-mcp@1.15.4` and verify installed SHA-256.
- [ ] `npm ci`, `npm run typecheck`, `npm run lint`, `npm test`, `npm run build`.
- [ ] `npm run typecheck:integration`, `npm run test:integration:docker`
      if the environment supports the MCP-007 disposable PostgreSQL harness.
- [ ] `git apply --check --whitespace=error-all`,
      `git apply --whitespace=error-all`, `git diff --check` against the
      accepted MCP-007 Attempt-5 baseline.
- [ ] Run real-schema parity assertions before enabling the MCP runtime.

## Completion Report

### Status

Not started. Developer-owned patch delivery; neither source validation nor
this task file constitutes an architect acceptance decision.

### Validation Results

Local Node 24 and Docker-backed integration are pending developer validation.
The distribution packet records only tests actually executed in its environment.

### Unresolved Issues

The standalone MCP endpoint remains disabled. The pinned schema artifact needs
deployment provisioning. The WooCommerce broker and remaining tool-execution
adapters remain subsequent, separately owned tasks.

## Architect Review

### Review Status

Pending.
