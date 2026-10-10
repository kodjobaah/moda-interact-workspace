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
status: pending
priority: 5
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-032-MCP-004
enables:
  - ARCH-032-MCP-006
created: 2026-10-10
updated: 2026-10-10
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
