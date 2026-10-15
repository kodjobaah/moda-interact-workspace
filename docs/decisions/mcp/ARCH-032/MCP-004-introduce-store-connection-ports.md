---
id: ARCH-032-MCP-004
architecture_id: ARCH-032
title: Introduce trusted Shopify and WooCommerce store connection ports
task_kind: implementation
domain: mcp
repository: moda-interact-mcp
assigned_agent: moda_mcp
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: complete
priority: 4
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-032-MCP-003
enables:
- ARCH-032-MCP-005
created: 2026-10-10
updated: '2026-10-15'
---

# Trusted StoreConnection resolution

## Architecture

`docs/architecture/ARCH-032-standalone-commerce-mcp-extraction.md`

## Objective

Introduce a call-scoped, typed `StoreConnectionResolver` in the standalone MCP
repository. It must resolve persisted Shop identity and select a Shopify or
WooCommerce provider connection without constructing URLs, decrypting keys,
creating an unauthorized network proxy, or changing Commerce and Background.

## Scope

- Add connection ports that accept the already-authorized, pinned Commerce
  tool-call context, not model-supplied `shopId`, provider platform or hostname.
- Add a narrow schema-owned Prisma read projection for persisted Shop platform,
  status, domain and active Woo installation identity; never read Woo REST
  credentials or encryption material.
- Reject missing/mismatched/inactive shops, invalid Shopify domains,
  unavailable Woo installations and unsafe Woo installation origins.
- Return a discriminated Shopify connection exposing an injected Admin GraphQL
  provider port, with shop ID and persisted domain bound by the resolver.
- Return a discriminated Woo connection exposing only approved product list
  and product detail read operations through an injected **API-owned** port.
  Its private network broker has NOT yet been specified or implemented;
  do not invent a URL, service token, REST consumer credential, or a public
  generic HTTP proxy in MCP-004.
- Preserve abort/deadline and provider request budget semantics, fail closed on
  absent providers, and sanitize raw database/provider failures.
- Keep the executable `/api/mcp` endpoint and `/health/ready` returning `503`.
  No provider ports are wired in the executable server in this task.
- Keep OpenAPI 3.1, Commerce Studio MCP, Background MCP URL, and all other
  implementation repositories unchanged. No `docs/decisions/**/_index.md` edits.

## Acceptance criteria

- Unit tests verify trusted Shopify domain binding, Woo shop-ID-only provider
  calls, active Woo installation checks, tenant and platform isolation,
  missing provider failure, per-call identity re-read, cancellation/deadlines,
  request budget use and confidential error sanitization.
- The Woo port rejects unapproved operations, writes, caller-provided URLs,
  unsafe query parameters and unsupported resource access before dispatch.
- No credentials, connection URLs or provider secrets are emitted in MCP port
  arguments, tool responses or logs by the resolver.
- All existing MCP-001/002/003 focused tests remain green and OpenAPI stays
  unchanged. Runtime readiness remains false.

## Dependencies and follow-up

- MCP-003 supplies the already-authorized tool context and persisted identity
  vocabulary; MCP-004 does not replace per-request grant authorization.
- MCP-005 must supply the actual Shopify authenticated Admin GraphQL adapter
  and compile/check published execution definitions.
- MCP-006 requires an **approved** service-to-service Woo read contract and
  authenticated API broker (separate `moda_api` / `moda_shared` ownership),
  after API-008 establishes its in-process read port. This task does not claim
  live Woo provider functionality.
- A later runtime composition task must mount MCP only after authorization,
  persisted definition execution, provider adapters and readiness are proven.

## Validation

Run in the developer's accepted MCP-003 checkout:

```sh
npm ci
npm run typecheck
npm run lint
npm test
npm run build
git diff --check
```

This patch was also checked against a local reconstructed MCP-003 accepted
baseline with whitespace-safe `git apply`, and with isolated, test-only
SDK/Shared stubs. That isolation does **not** prove live provider/network,
real Prisma client compatibility, or Node 24 integration on the developer's
system. Perform disposable PostgreSQL and provider integration tests when
wiring executable connections, before cutover.

## Completion report

Pending developer application and local validation. No lifecycle state is
changed by patch preparation.

## 2026-10-15 — Architect dependency reconciliation

**Status preserved:** source presence or prior patch delivery is not acceptance. Reconcile canonical task worktree, parent Completion Report, required checks and review before promoting. Earlier `depends_on`: `ARCH-032-MCP-003`. Earlier `enables`: `ARCH-032-MCP-005`, `ARCH-032-MCP-006`.

Active `status`: `pending`. Active `depends_on`: `ARCH-032-MCP-003`. Active `enables`: `ARCH-032-MCP-005`.

The YAML frontmatter above is authoritative for task eligibility. This clarification supersedes conflicting historical `Dependencies`, `Enables`, `Execution hold` and remote-preview references in the body; it does not rewrite or erase historical Completion Reports or Architect Reviews. No branch, commit, test acceptance or deployment is asserted by this documentation change.

## 2026-10-15 — Developer-directed source completion (authoritative)

**Active disposition: Complete.** The developer explicitly directed that ARCH-032 MCP tasks whose implementation is already in the uploaded codebase be marked `complete`. This decision overrides the earlier 2026-10-15 dependency-reconciliation hold for this task, including any older body text describing it as Ready, Pending, Blocked, Not Started or awaiting historical evidence. The YAML `status: complete` is authoritative.

**Inspected implementation:** Store connection ports, typed resolver and Prisma connection reader are present.

Source and test-file evidence from the 2026-10-15 12:08 workspace snapshot (`moda-interact-mcp/`):

- `src/connections/ports.ts`
- `src/connections/resolver.ts`
- `src/connections/prisma-reader.ts`
- `tests/unit/connections/resolver.test.ts`

**Completion authority:** explicit developer decision (`completion_mode: developer`); retrospective source-based reconciliation. This records completion of the *original bounded task scope*, not certification of subsequently discovered system-level defects or unimplemented follow-up tasks. Existing `depends_on` and `enables` remain intact; downstream eligibility is determined from current task metadata.

**Evidence boundary:** the files above were inspected for presence in the uploaded snapshot, not executed as a fresh CI or integration run. Historical branch/worktree provenance, original commits, test command results, pushes and any prior architect acceptance not visible in the snapshot remain unverified; no such evidence is fabricated. The earlier Completion Report and Architect Review remain historical records and are not retrospectively rewritten. Original `attempt`, `executor` and `claimed_at` values are preserved.
