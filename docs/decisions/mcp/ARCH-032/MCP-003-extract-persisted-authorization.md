---
id: ARCH-032-MCP-003
architecture_id: ARCH-032
title: Extract persisted MCP authorization and published capability resolution
task_kind: implementation
domain: mcp
repository: moda-interact-mcp
assigned_agent: moda_mcp
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: pending
priority: 3
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-032-MCP-002
enables:
  - ARCH-032-MCP-004
created: 2026-10-10
updated: 2026-10-10
---

# Persisted MCP authorization and published capability resolution

## Architecture

`docs/architecture/ARCH-032-standalone-commerce-mcp-extraction.md`

## Objective

Extract the Commerce runtime's persisted tenant, conversation, pinned grant,
release, entitlement, capability and trusted-prompt resolution into small,
read-only modules in `moda-interact-mcp`. Preserve MCP-002's protocol and
OpenAPI behaviour, with the existing Commerce MCP route and Background URL
untouched.

## Scope

- Use schema-owned PostgreSQL/Prisma read projections through an injected
  transaction interface. Do not own the database schema, generated client,
  credential stores or migrations in the MCP repository.
- Resolve the shop and its platform, active Woo installation where relevant,
  conversation processing lease (120 seconds), current inbound version,
  unique pinned grant or current environment release pointer.
- Enforce published revisions, grant/release identity, current capability/tool
  status, subscription/plan/feature entitlement and explicit shop preference;
  `CommerceCapability.shopPlatform` must deny cross-platform registration.
- Resolve active Platform and optional Shop instructions via published revision
  pointers from the same consistent PostgreSQL transaction. Respect a shop
  configuration with no selected prompt override.
- Use published Shared commerce manifest/grant schemas; do not duplicate a
  separate wire contract or import authoring/UI code from Commerce.
- Fail closed with stable MCP error codes; never disclose Prisma errors,
  credentials, customer data or prompt text in transport failures.
- Keep executable `/api/mcp` and readiness *unmounted* during this step.
  Schema-owned generated Prisma client creation, provider execution and a live
  readiness composition root remain subsequent integration work.
- No Commerce, Background, WooCommerce API, Shared, Database or Gateway edits.
  No `docs/decisions/**/_index.md` edits.

## Acceptance criteria

- Focused tests cover pinned grants, authorization revocations, Woo platform
  eligibility, tenant and lease mismatch, malicious/stale revisions, active
  prompt pointers and absent-grant resolve mode.
- Database read model requests an isolated `RepeatableRead` transaction and
  never trusts model-supplied tenant, platform, URL or credential authority.
- An injected MCP JSON-RPC authorization seam proves per-request revocation.
- Existing MCP-001/002 tests remain green and OpenAPI stays intact.
- The executable process remains 503 for `/api/mcp` and `/health/ready`.

## Validation

Run in `moda-interact-mcp` against the developer's installed dependencies:

```sh
npm ci
npm run typecheck
npm run lint
npm test
npm run build
```

Focused test doubles do **not** prove compatibility with generated Prisma
client types, the exact deployed database schema, or a live transaction.
Before production wiring, run a disposable PostgreSQL integration test against
the authoritative `moda-interact-database` migration state, including revoked,
stale-lease, expired-grant, disabled-plan and cross-platform cases.

## Completion report

Pending developer application and local validation. Task lifecycle status is
not changed by preparation of this patch. MCP-004 must provide provider
execution and safe composition before the server can be mounted.
