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
status: complete
priority: 8
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-032-MCP-007
enables:
- ARCH-032-MCP-009
created: 2026-10-10
updated: '2026-10-15'
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

## 2026-10-15 — Architect dependency reconciliation

**Status preserved:** source presence or prior patch delivery is not acceptance. Reconcile canonical task worktree, parent Completion Report, required checks and review before promoting.

Active `status`: `pending`. Active `depends_on`: `ARCH-032-MCP-007`. Active `enables`: `ARCH-032-MCP-009`.

The YAML frontmatter above is authoritative for task eligibility. This clarification supersedes conflicting historical `Dependencies`, `Enables`, `Execution hold` and remote-preview references in the body; it does not rewrite or erase historical Completion Reports or Architect Reviews. No branch, commit, test acceptance or deployment is asserted by this documentation change.

## 2026-10-15 — Developer-directed source completion (authoritative)

**Active disposition: Complete.** The developer explicitly directed that ARCH-032 MCP tasks whose implementation is already in the uploaded codebase be marked `complete`. This decision overrides the earlier 2026-10-15 dependency-reconciliation hold for this task, including any older body text describing it as Ready, Pending, Blocked, Not Started or awaiting historical evidence. The YAML `status: complete` is authoritative.

**Inspected implementation:** Pinned Shopify compiler, published runtime and restricted result renderer are present.

Source and test-file evidence from the 2026-10-15 12:08 workspace snapshot (`moda-interact-mcp/`):

- `src/execution/shopify/admin-compiler.ts`
- `src/execution/shopify/published-runtime.ts`
- `src/execution/rendering/renderer.ts`
- `tests/unit/execution/rendering/renderer.test.ts`

**Completion authority:** explicit developer decision (`completion_mode: developer`); retrospective source-based reconciliation. This records completion of the *original bounded task scope*, not certification of subsequently discovered system-level defects or unimplemented follow-up tasks. Existing `depends_on` and `enables` remain intact; downstream eligibility is determined from current task metadata.

**Evidence boundary:** the files above were inspected for presence in the uploaded snapshot, not executed as a fresh CI or integration run. Historical branch/worktree provenance, original commits, test command results, pushes and any prior architect acceptance not visible in the snapshot remain unverified; no such evidence is fabricated. The earlier Completion Report and Architect Review remain historical records and are not retrospectively rewritten. Original `attempt`, `executor` and `claimed_at` values are preserved.
