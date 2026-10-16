---
id: ARCH-032-MCP-005
architecture_id: ARCH-032
title: Implement Shopify offline-session connection and pinned Admin GraphQL execution
task_kind: implementation
domain: mcp
repository: moda-interact-mcp
assigned_agent: moda_mcp
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: complete
priority: 5
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-032-MCP-004
enables:
- ARCH-032-MCP-006
created: 2026-10-10
updated: '2026-10-15'
---

# Shopify authenticated connection and pinned execution

## Objective

Extend the already-authorized MCP-004 StoreConnection seam with a read-only,
authenticated Shopify Admin GraphQL provider and a pinned tool execution adapter.
Preserve the original Commerce Studio and its MCP endpoint without changes.

## Scope

- Read existing Shopify offline sessions by the trusted canonical shop domain;
  never retrieve sessions by caller-supplied input or create a credential store.
- Construct only `https://{verified myshopify.com}/admin/api/2026-07/graphql.json`;
  POST a single named read-only GraphQL operation, with bounded document/variable
  sizes and explicit redirect rejection.
- Enforce deadline/abort, provider request budget (owned by MCP-004), bounded
  responses, API version and GraphQL error handling, with no error/token leakage.
- Before executing any tool, refresh the MCP-003 persisted grant, release,
  entitlement, turn lease and exact published tool-revision authorization.
- Map validated model arguments to the pinned authoring variable mappings,
  never to destination/authentication fields.
- Require the **canonical published Admin schema compiler** and canonical
  result normalizer/Nunjucks renderer as injected ports: this snapshot does not
  contain `admin-2026-07.json`, and Shared `1.4.0` is not the replacement authoring
  definition schema. Do not silently implement a divergent schema/runtime.
- Keep `/api/mcp` and readiness returning 503 in the standalone process; do not
  alter the Commerce or Background services, routes, schemas or API connections.
- No `docs/decisions/**/_index.md` changes.

## Acceptance criteria

- Tests for validated offline sessions, exact endpoint/header binding, one named
  query, mutation/fragment/introspection rejection, max bytes, redirect, wrong
  API version, throttling, abort/deadline and confidential error sanitization.
- Tests for published revision matching, entitlement revocation, platform
  mismatch, exact grant and release identity, input mappings, no provider calls
  without canonical compiler proof and renderer availability.
- Existing MCP-001/002/003/004 tests stay green; OpenAPI stays unchanged.
- No live provider operation is enabled by this task alone.

## Dependencies / follow-up

- Source baseline: accepted MCP-004 Attempt 1 (plus MCP-002 Attempt 2).
- The canonical Admin schema compiler and renderer must be made available in the
  standalone MCP process from their agreed contract owner before process wiring.
- A later composition task must inject the schema-owned Prisma client, verify
  live Shopify provider parity and mount `/api/mcp` with real readiness.

## Validation

After applying the patch in the developer's MCP-004 baseline:

```sh
npm ci
npm run typecheck
npm run lint
npm test
npm run build
git diff --check
```

## Completion report

Pending developer application and real Node 24 verification. Patch naming
`accepted` is delivery convention only; it does not record architect approval.

## 2026-10-15 — Architect dependency reconciliation

**Status preserved:** source presence or prior patch delivery is not acceptance. Reconcile canonical task worktree, parent Completion Report, required checks and review before promoting.

Active `status`: `pending`. Active `depends_on`: `ARCH-032-MCP-004`. Active `enables`: `ARCH-032-MCP-006`.

The YAML frontmatter above is authoritative for task eligibility. This clarification supersedes conflicting historical `Dependencies`, `Enables`, `Execution hold` and remote-preview references in the body; it does not rewrite or erase historical Completion Reports or Architect Reviews. No branch, commit, test acceptance or deployment is asserted by this documentation change.

## 2026-10-15 — Developer-directed source completion (authoritative)

**Active disposition: Complete.** The developer explicitly directed that ARCH-032 MCP tasks whose implementation is already in the uploaded codebase be marked `complete`. This decision overrides the earlier 2026-10-15 dependency-reconciliation hold for this task, including any older body text describing it as Ready, Pending, Blocked, Not Started or awaiting historical evidence. The YAML `status: complete` is authoritative.

**Inspected implementation:** Shopify session resolution, GraphQL provider and published execution path are present.

Source and test-file evidence from the 2026-10-15 12:08 workspace snapshot (`moda-interact-mcp/`):

- `src/connections/shopify/session-reader.ts`
- `src/connections/shopify/provider.ts`
- `src/execution/shopify/execute.ts`
- `tests/unit/connections/shopify/provider.test.ts`

**Completion authority:** explicit developer decision (`completion_mode: developer`); retrospective source-based reconciliation. This records completion of the *original bounded task scope*, not certification of subsequently discovered system-level defects or unimplemented follow-up tasks. Existing `depends_on` and `enables` remain intact; downstream eligibility is determined from current task metadata.

**Evidence boundary:** the files above were inspected for presence in the uploaded snapshot, not executed as a fresh CI or integration run. Historical branch/worktree provenance, original commits, test command results, pushes and any prior architect acceptance not visible in the snapshot remain unverified; no such evidence is fabricated. The earlier Completion Report and Architect Review remain historical records and are not retrospectively rewritten. Original `attempt`, `executor` and `claimed_at` values are preserved.
