---
id: ARCH-032-MCP-006
architecture_id: ARCH-032
title: Establish database dependency and guarded WooCommerce product-read consumer
task_kind: implementation
domain: mcp
repository: moda-interact-mcp
assigned_agent: moda_mcp
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: complete
priority: 6
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-032-MCP-005
enables:
- ARCH-032-MCP-007
created: 2026-10-10
updated: '2026-10-15'
---

# WooCommerce grant gate and database dependency

## Objective

Add the canonical database repository as a Git submodule dependency of the
standalone MCP service and prepare WooCommerce's read-only product provider
behind an API-owned connection boundary. Do not activate live MCP execution.

## Scope

- Introduce `@prisma/client` and `prisma` at schema-compatible version `6.19.3`,
  with `database/prisma/schema.prisma` as the **only** generation source.
- Add the existing `moda-interact-database` repository as MCP's `database/`
  Git submodule, recording its actual checked-out commit in the MCP repository;
  never vendor the schema or make schema/migration changes in MCP.
- Add a secret-free Prisma eligibility projection of the WooCommerce installation
  and active REST read grant. Fail closed for wrong tenant/platform, revoked or
  stale installation/grant, invalid scope and unverified credentials.
- Add a bounded in-process provider-consumer port for `products.list` and
  `products.retrieve`; deny arbitrary origins, headers, verbs and other
  operations. No consumer keys, Woo base URL, or encryption keys in MCP.
- Mask provider exceptions and bound response size, time and cancellation.
- Keep Commerce, Background, API and Gateway implementation unchanged.
- No `docs/decisions/**/_index.md` edits.

## Dependencies and blockers

`ARCH-026-API-008` currently specifies an **in-process API-owned** Woo REST
provider. It does not define a private network endpoint or service-authenticated
broker contract. Do not invent that endpoint/contract in MCP-006. The later
integration task must first be authorised by `moda_architect` with API ownership
and prove API-side grant revalidation, transport safety and service identity.
MCP's local grant projection is *not* a replacement for API authorization.

The database Gitlink commit cannot be generated from an archive alone; developer
adds the real Git submodule in the MCP checkout and records its commit alongside
the implementation patch. The patch itself covers source, manifest and lockfile.

## Acceptance criteria

- `npm run prisma:generate` resolves the schema from `database/` once the real
  submodule is initialised; MCP owns no schema or migration files.
- Shop/installation and matching active, verified read-only grant are required
  before a provider request; no credential envelope columns are selected.
- Only approved product read operations and bounded inputs can reach the
  injected API-owned consumer; secret-bearing responses fail closed.
- Cross-tenant, revoked, stale, cancelled, timeout, large-result and failure
  cases are covered by focused tests.
- `/api/mcp` and readiness remain unavailable in the standalone executable;
  no production traffic or existing Commerce API is changed.

## Validation

- [ ] Initialise and commit MCP's `database/` Git submodule at a reviewed
      upstream revision; record `git submodule status database`.
- [ ] `npm ci` and `npm run prisma:generate` on Node 24.19.0.
- [ ] `npm run typecheck`, `npm run lint`, `npm test`, `npm run build`.
- [ ] `git apply --check --whitespace=error-all` and `git diff --check`.
- [ ] API broker/network integration remains blocked pending its contract.

## Completion Report

### Status

Not Started. Developer-owned implementation assistance; no architect review
or completion decision is claimed.

### Files Changed

Pending developer validation and real database Gitlink registration.

### Validation Results

Pending developer Node 24/npm/Prisma validation; isolated tests are not database
integration evidence.

### Unresolved Issues

The API-008 in-process connection is not remotely callable; a separately
approved authenticated private broker is required before the MCP consumer can
perform live Woo reads.

## Architect Review

### Review Status

Pending.

## 2026-10-15 — Architect dependency reconciliation

**Status preserved:** source presence or prior patch delivery is not acceptance. Reconcile canonical task worktree, parent Completion Report, required checks and review before promoting.

Active `status`: `pending`. Active `depends_on`: `ARCH-032-MCP-005`. Active `enables`: `ARCH-032-MCP-007`.

The YAML frontmatter above is authoritative for task eligibility. This clarification supersedes conflicting historical `Dependencies`, `Enables`, `Execution hold` and remote-preview references in the body; it does not rewrite or erase historical Completion Reports or Architect Reviews. No branch, commit, test acceptance or deployment is asserted by this documentation change.

## 2026-10-15 — Developer-directed source completion (authoritative)

**Active disposition: Complete.** The developer explicitly directed that ARCH-032 MCP tasks whose implementation is already in the uploaded codebase be marked `complete`. This decision overrides the earlier 2026-10-15 dependency-reconciliation hold for this task, including any older body text describing it as Ready, Pending, Blocked, Not Started or awaiting historical evidence. The YAML `status: complete` is authoritative.

**Inspected implementation:** WooCommerce read eligibility/grant reader and provider-consumer boundary are present; a live Woo broker is a separate upstream capability.

Source and test-file evidence from the 2026-10-15 12:08 workspace snapshot (`moda-interact-mcp/`):

- `src/connections/woocommerce/grant-reader.ts`
- `src/connections/woocommerce/provider.ts`
- `tests/unit/connections/woocommerce/grant-reader.test.ts`

**Completion authority:** explicit developer decision (`completion_mode: developer`); retrospective source-based reconciliation. This records completion of the *original bounded task scope*, not certification of subsequently discovered system-level defects or unimplemented follow-up tasks. Existing `depends_on` and `enables` remain intact; downstream eligibility is determined from current task metadata.

**Evidence boundary:** the files above were inspected for presence in the uploaded snapshot, not executed as a fresh CI or integration run. Historical branch/worktree provenance, original commits, test command results, pushes and any prior architect acceptance not visible in the snapshot remain unverified; no such evidence is fabricated. The earlier Completion Report and Architect Review remain historical records and are not retrospectively rewritten. Original `attempt`, `executor` and `claimed_at` values are preserved.
