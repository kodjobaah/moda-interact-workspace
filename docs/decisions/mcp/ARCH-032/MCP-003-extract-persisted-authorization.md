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
status: complete
priority: 3
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-032-MCP-002
enables:
- ARCH-032-MCP-004
created: 2026-10-10
updated: '2026-10-15'
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

## 2026-10-15 — Architect dependency reconciliation

**Status preserved:** source presence or prior patch delivery is not acceptance. Reconcile canonical task worktree, parent Completion Report, required checks and review before promoting.

Active `status`: `pending`. Active `depends_on`: `ARCH-032-MCP-002`. Active `enables`: `ARCH-032-MCP-004`.

The YAML frontmatter above is authoritative for task eligibility. This clarification supersedes conflicting historical `Dependencies`, `Enables`, `Execution hold` and remote-preview references in the body; it does not rewrite or erase historical Completion Reports or Architect Reviews. No branch, commit, test acceptance or deployment is asserted by this documentation change.

## 2026-10-15 — Developer-directed source completion (authoritative)

**Active disposition: Complete.** The developer explicitly directed that ARCH-032 MCP tasks whose implementation is already in the uploaded codebase be marked `complete`. This decision overrides the earlier 2026-10-15 dependency-reconciliation hold for this task, including any older body text describing it as Ready, Pending, Blocked, Not Started or awaiting historical evidence. The YAML `status: complete` is authoritative.

**Inspected implementation:** Persisted shop release/capability resolution and authentication exist; current shop-scoped semantics supersede earlier conversation-grant expectations.

Source and test-file evidence from the 2026-10-15 12:08 workspace snapshot (`moda-interact-mcp/`):

- `src/capabilities/prisma-reader.ts`
- `src/capabilities/resolve.ts`
- `src/mcp/authentication.ts`
- `tests/unit/capabilities/resolve.test.ts`

**Completion authority:** explicit developer decision (`completion_mode: developer`); retrospective source-based reconciliation. This records completion of the *original bounded task scope*, not certification of subsequently discovered system-level defects or unimplemented follow-up tasks. Existing `depends_on` and `enables` remain intact; downstream eligibility is determined from current task metadata.

**Evidence boundary:** the files above were inspected for presence in the uploaded snapshot, not executed as a fresh CI or integration run. Historical branch/worktree provenance, original commits, test command results, pushes and any prior architect acceptance not visible in the snapshot remain unverified; no such evidence is fabricated. The earlier Completion Report and Architect Review remain historical records and are not retrospectively rewritten. Original `attempt`, `executor` and `claimed_at` values are preserved.
