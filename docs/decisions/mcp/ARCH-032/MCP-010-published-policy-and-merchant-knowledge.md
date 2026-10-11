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
status: pending
priority: 10
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-032-MCP-009
enables:
  - ARCH-032-MCP-011
created: 2026-10-11
updated: 2026-10-11
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
