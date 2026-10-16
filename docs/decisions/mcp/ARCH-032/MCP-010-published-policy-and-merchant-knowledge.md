---
id: ARCH-032-MCP-010
architecture_id: ARCH-032
title: Extract published policy dispatch and Merchant Knowledge lookup
task_kind: implementation
domain: mcp
repository: moda-interact-mcp
assigned_agent: moda_mcp
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: complete
priority: 10
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-032-MCP-009
enables:
- ARCH-032-MCP-011
created: 2026-10-11
updated: '2026-10-15'
---

# Published policy-operation dispatch and Merchant Knowledge runtime

## Objective

Extend MCP-009's composed Shopify ports with a narrow, read-only published
policy-operation path. Extract only `merchantKnowledge.lookup@1.0.0` from
Commerce, preserving per-call authorization, independent entitlement checks,
reference trust boundaries, and the restricted response renderer. The existing
Commerce endpoint remains available and the new MCP HTTP process remains closed.

## Scope

- Verify the current pinned published definition, operation identity/version,
  tool descriptor, argument mappings and template before executing.
- Register only `merchantKnowledge.lookup@1.0.0`. Do not advertise remaining
  policy operations or external HTTP until their dedicated extraction tasks.
- Extract Merchant Knowledge input/output contracts, entitlement gating,
  source filtering, pgvector retrieval and bounded embedding HTTP helper.
- Receive embedding configuration through an injected credential-resolved
  runtime port. Do not copy Commerce encryption-keyring management into MCP or
  put credential data into published tool/model inputs.
- Preserve `UNTRUSTED_REFERENCE`, max five matches, source revocations, shop
  isolation, deadline checks, provider-request budgets and restricted Nunjucks
  rendering.
- Integrate optional policy ports in existing MCP-009 in-process composition;
  no changes to `src/index.ts`, `src/server.ts`, health, or OpenAPI.
- Unit tests in `tests/unit/execution/policy/` and real migrated disposable
  PostgreSQL integration for entitlement and preference revocation.

## Acceptance Criteria

- A pinned and entitled Merchant Knowledge tool can be listed and called
  through MCP with an injected approved adapter; a missing adapter suppresses it.
- Shopify and WooCommerce support platform-generic Merchant Knowledge only
  when their own persisted shop identity, grant and entitlements are valid.
- Arbitrary policy identities, stale/pinned-mismatch tools, invalid input,
  missing embedding runtime and malformed retrieval output fail closed.
- Merchant Knowledge retrieves only its tenant's entitled sources using
  bounded pgvector reads and does not surface provider credentials.
- Error fallback preserves the existing error contract without leaking raw
  Prisma/provider exceptions.
- All Node 24 unit, typecheck, lint and build checks plus the disposable
  migrated PostgreSQL integration suite pass locally.
- No authoring, Gateway, API, Database, Shared, Background or Commerce
  implementation changes, and no `docs/decisions/**/_index.md` edits.

## Validation

- [ ] `git apply --check --whitespace=error-all` against accepted MCP-009 Attempt 1.
- [ ] `git apply --whitespace=error-all` and `git diff --check`.
- [ ] `npm ci`, `npm run prisma:generate`.
- [ ] `npm run typecheck`, `npm run lint`, `npm test`, `npm run build`.
- [ ] `npm run typecheck:integration`, `npm run test:integration:docker`.
- [ ] Confirm private endpoint remains fail-closed.

## Completion Report

### Status

Not started. Developer-owned patch delivery; no architect acceptance is implied.

## 2026-10-15 — Architect dependency reconciliation

**Status preserved:** source presence or prior patch delivery is not acceptance. Reconcile canonical task worktree, parent Completion Report, required checks and review before promoting.

Active `status`: `pending`. Active `depends_on`: `ARCH-032-MCP-009`. Active `enables`: `ARCH-032-MCP-011`.

The YAML frontmatter above is authoritative for task eligibility. This clarification supersedes conflicting historical `Dependencies`, `Enables`, `Execution hold` and remote-preview references in the body; it does not rewrite or erase historical Completion Reports or Architect Reviews. No branch, commit, test acceptance or deployment is asserted by this documentation change.

## 2026-10-15 — Developer-directed source completion (authoritative)

**Active disposition: Complete.** The developer explicitly directed that ARCH-032 MCP tasks whose implementation is already in the uploaded codebase be marked `complete`. This decision overrides the earlier 2026-10-15 dependency-reconciliation hold for this task, including any older body text describing it as Ready, Pending, Blocked, Not Started or awaiting historical evidence. The YAML `status: complete` is authoritative.

**Inspected implementation:** Published policy executor and merchant-knowledge execution adapter are present.

Source and test-file evidence from the 2026-10-15 12:08 workspace snapshot (`moda-interact-mcp/`):

- `src/execution/policy/execute.ts`
- `src/execution/merchant-knowledge/adapter.ts`
- `tests/unit/execution/policy/merchant-knowledge.test.ts`

**Completion authority:** explicit developer decision (`completion_mode: developer`); retrospective source-based reconciliation. This records completion of the *original bounded task scope*, not certification of subsequently discovered system-level defects or unimplemented follow-up tasks. Existing `depends_on` and `enables` remain intact; downstream eligibility is determined from current task metadata.

**Evidence boundary:** the files above were inspected for presence in the uploaded snapshot, not executed as a fresh CI or integration run. Historical branch/worktree provenance, original commits, test command results, pushes and any prior architect acceptance not visible in the snapshot remain unverified; no such evidence is fabricated. The earlier Completion Report and Architect Review remain historical records and are not retrospectively rewritten. Original `attempt`, `executor` and `claimed_at` values are preserved.
