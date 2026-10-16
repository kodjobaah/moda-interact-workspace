---
id: ARCH-032-MCP-009
architecture_id: ARCH-032
title: Compose the Shopify MCP execution ports without enabling live traffic
task_kind: implementation
domain: mcp
repository: moda-interact-mcp
assigned_agent: moda_mcp
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: complete
priority: 9
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-032-MCP-008
enables:
- ARCH-032-MCP-010
created: 2026-10-11
updated: '2026-10-15'
---

# Shopify runtime port composition and PostgreSQL tool-call proof

## Objective

Bind the existing MCP context/authentication, persisted grant resolver, Shopify
connection/provider, pinned Admin compiler and restricted Nunjucks renderer to
one in-process protocol/execution port. Preserve the legacy Commerce endpoint
and keep the new production MCP HTTP process unmounted until execution parity.

## Scope

- Compose `McpServicePorts` from the existing authorization reader, Shopify
  connection and `ShopifyPublishedToolExecutor`. Use the hash-verified pinned
  Admin schema runtime by default; test-only injected schema ports are allowed
  solely for explicitly controlled tests.
- Recheck conversation lease, pinned grant and tool revision and active
  entitlement before Shopify provider I/O; retain current per-tool deadline,
  cancellation and provider-request budget semantics.
- Avoid advertising unsupported published execution kinds as callable MCP
  tools. Their persisted manifests and grants remain unchanged; WooCommerce
  REST, policy operations and external HTTP remain fail-closed until approved
  adapters and broker dependencies exist.
- Expose the prepared service ports from the MCP-007 managed Prisma lifecycle,
  without enabling readiness or installing an HTTP handler in `src/index.ts`.
  Previously prepared ports must not reconnect after persistence is closed.
- Add focused unit coverage under `tests/unit/runtime/` for MCP list/call,
  unsupported tool filtering, revoked entitlement, tenant identity, schema
  rejection and disposal.
- Extend the existing disposable PostgreSQL integration fixture to publish a
  valid Shopify GraphQL definition and exercise a real persisted MCP list/call
  through a simulated HTTPS response. Verify a later preference revocation
  prevents another provider request.
- Do not modify Commerce, Background, API, Database, Shared, Gateway, or
  `docs/decisions/**/_index.md`.

## Acceptance Criteria

- An authorised Shopify conversation can list and execute its pinned GraphQL
  tool through composed ports using current persisted grants and revisions.
- Unsupported tool kinds cannot be advertised as executable; a Woo shop cannot
  use Shopify's executor even with a platform-generic capability.
- The pinned Admin schema artifact remains a mandatory production dependency;
  a missing/wrong artifact fails before Shopify provider I/O.
- Revoked entitlement, stale/incorrect tenant, invalid arguments, shutdown and
  cancellation fail closed and do not invoke provider I/O.
- Unit tests and real migrated disposable PostgreSQL integration tests pass.
  PostgreSQL is cleaned up even on test failure.
- `npm run typecheck`, `npm run typecheck:integration`, `npm run lint`,
  `npm test`, `npm run build` and `npm run test:integration:docker` pass on Node 24.
- `src/index.ts`, `src/server.ts`, `/api/mcp` availability and OpenAPI are
  unchanged; no production traffic moves.

## Validation

- [ ] `git apply --check --whitespace=error-all` then `git apply --whitespace=error-all`
      and `git diff --check` against the accepted MCP-008 Attempt-3 baseline.
- [ ] `npm ci` and `npm run prisma:generate` with initialised database submodule.
- [ ] `npm run typecheck`, `npm run lint`, `npm test`, `npm run build`.
- [ ] `npm run typecheck:integration`, `npm run test:integration:docker` with
      real migrations and disposable PostgreSQL/pgvector.
- [ ] Validate schema-artifact hash and production-ready tool parity before
      any later live endpoint mounting.

## Completion Report

### Status

Not started. Developer-owned patch delivery; no architect acceptance is
implied by successful local verification.

### Validation Results

Pending developer Node 24/Docker validation. Distribution records only checks
actually executed in the patch environment.

### Unresolved Issues

- Shopify Admin schema artifact must be installed and validated in deployment.
- WooCommerce's API-owned authenticated broker and remaining published tool
  execution kinds are not provided or enabled by this task.
- The standalone production endpoint remains fail-closed until the explicitly
  scoped readiness and parity work is reviewed.

## Architect Review

### Review Status

Pending.

## 2026-10-15 — Architect dependency reconciliation

**Status preserved:** source presence or prior patch delivery is not acceptance. Reconcile canonical task worktree, parent Completion Report, required checks and review before promoting.

Active `status`: `pending`. Active `depends_on`: `ARCH-032-MCP-008`. Active `enables`: `ARCH-032-MCP-010`.

The YAML frontmatter above is authoritative for task eligibility. This clarification supersedes conflicting historical `Dependencies`, `Enables`, `Execution hold` and remote-preview references in the body; it does not rewrite or erase historical Completion Reports or Architect Reviews. No branch, commit, test acceptance or deployment is asserted by this documentation change.

## 2026-10-15 — Developer-directed source completion (authoritative)

**Active disposition: Complete.** The developer explicitly directed that ARCH-032 MCP tasks whose implementation is already in the uploaded codebase be marked `complete`. This decision overrides the earlier 2026-10-15 dependency-reconciliation hold for this task, including any older body text describing it as Ready, Pending, Blocked, Not Started or awaiting historical evidence. The YAML `status: complete` is authoritative.

**Inspected implementation:** Shopify runtime composition, execution registry and service integration ports are present.

Source and test-file evidence from the 2026-10-15 12:08 workspace snapshot (`moda-interact-mcp/`):

- `src/runtime/execution-registry.ts`
- `src/composition.ts`
- `src/mcp/service.ts`
- `tests/unit/composition.test.ts`

**Completion authority:** explicit developer decision (`completion_mode: developer`); retrospective source-based reconciliation. This records completion of the *original bounded task scope*, not certification of subsequently discovered system-level defects or unimplemented follow-up tasks. Existing `depends_on` and `enables` remain intact; downstream eligibility is determined from current task metadata.

**Evidence boundary:** the files above were inspected for presence in the uploaded snapshot, not executed as a fresh CI or integration run. Historical branch/worktree provenance, original commits, test command results, pushes and any prior architect acceptance not visible in the snapshot remain unverified; no such evidence is fabricated. The earlier Completion Report and Architect Review remain historical records and are not retrospectively rewritten. Original `attempt`, `executor` and `claimed_at` values are preserved.
