---
id: ARCH-032-MCP-013
architecture_id: ARCH-032
title: Replace conversation-scoped MCP authorization with shop capability eligibility and shared structured logging
task_kind: implementation
domain: mcp
repository: moda-interact-mcp
assigned_agent: moda_mcp
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: pending
priority: 13
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-032-MCP-012
enables: []
created: 2026-10-11
updated: 2026-10-11
---

# Shop-scoped capability resolution and shared structured logging

## Objective

Correct the standalone MCP architecture to discover and execute published
capabilities for a trusted shop without owning CommerceAgent conversations,
processing leases, per-turn grants, or instruction state. Use the canonical
`@modainteract/moda-interact-shared/logging` logger with stable internal error
codes, unique per-occurrence identifiers, and sanitized public error responses.

## Architectural contract

- Callers are already authenticated at an upstream **private ingress**. This
  task does not introduce caller authentication inside MCP, nor make the private
  identity assertion into an internet-accessible bearer credential. Service
  exposure remains disabled and requires a separately approved Gateway boundary.
- Trusted `shopId` selects the shop. Model arguments cannot override the shop.
- Use the CURRENT environment release pointer, shop subscription/plan features,
  merchant preferences, feature and capability state and `shopPlatform` to
  determine eligibility. `null` platform is generic; otherwise match persisted
  `Shop.platform`.
- Feature-to-capability is one-to-many; a capability references exactly one
  tool; multiple capabilities may reference the same tool. Advertise each
  eligible unique `CommerceCapability.key` without deduplication or aliasing.
- Re-evaluate the selected capability, release and pinned revision on `tools/call`
  and dispatch by published execution kind through a generic registry.
- Remove MCP reads of `Conversation`, `CommerceConversationGrant`, processing
  leases, and trusted instructions from generic discovery and execution.
  Optional trusted recovery IDs remain tool-specific, not conversation security.
- Log failures with the Shared logger using distinct stable internal error
  reasons, UUID occurrence `errorId`, and request `requestId`. Preserve the
  existing public Shared `CommerceToolResult` error schema; never expose
  credentials, provider secrets, database connection strings or raw causes.
- Keep Commerce, Background, API, Database, Gateway, and active routing unchanged.
- Do not create or modify any `docs/decisions/**/_index.md` file.

## Work items

- Replace conversation/turn/grant read projection with a bounded shop capability
  projection using Prisma `RepeatableRead` and the published release pointer.
- Recompose the MCP protocol's `tools/list` / `tools/call` around unique
  capability identities without introducing feature-specific dispatch.
- Preserve StoreConnection provider isolation, per-call deadlines, budgets,
  result validation and current failure-closed deployment behavior.
- Integrate shared structured logging at request and execution boundaries.
- Add exact error-code and occurrence-id coverage under `tests/unit/`, and
  migrated disposable PostgreSQL coverage under `tests/integration/`.

## Validation

- [ ] `git apply --check --whitespace=error-all` against MCP-012 Attempt 5.
- [ ] `git apply --whitespace=error-all` and `git diff --check`.
- [ ] `npm run typecheck && npm run lint && npm test && npm run build`.
- [ ] `npm run typecheck:integration && npm run test:integration:docker`.
- [ ] Verify both capabilities sharing one published tool are independently
      listed and callable; shopPlatform and revocation checks fail closed.
- [ ] Confirm no Conversation or CommerceConversationGrant access in MCP reads.
- [ ] Verify upstream private ingress requirement before any later activation.

## Completion Report

### Status

Pending developer application and local validation. No architect acceptance,
completion or production activation decision is implied.
