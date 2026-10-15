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
status: complete
priority: 13
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-032-MCP-012
enables:
- ARCH-032-MCP-014
created: 2026-10-11
updated: '2026-10-15'
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

## 2026-10-15 — Architect dependency reconciliation

**Status preserved:** source presence or prior patch delivery is not acceptance. Reconcile canonical task worktree, parent Completion Report, required checks and review before promoting. Earlier `depends_on`: `ARCH-032-MCP-012`. Earlier `enables`: None.

Active `status`: `pending`. Active `depends_on`: `ARCH-032-MCP-012`. Active `enables`: `ARCH-032-MCP-014`.

The YAML frontmatter above is authoritative for task eligibility. This clarification supersedes conflicting historical `Dependencies`, `Enables`, `Execution hold` and remote-preview references in the body; it does not rewrite or erase historical Completion Reports or Architect Reviews. No branch, commit, test acceptance or deployment is asserted by this documentation change.

## 2026-10-15 — Developer-directed source completion (authoritative)

**Active disposition: Complete.** The developer explicitly directed that ARCH-032 MCP tasks whose implementation is already in the uploaded codebase be marked `complete`. This decision overrides the earlier 2026-10-15 dependency-reconciliation hold for this task, including any older body text describing it as Ready, Pending, Blocked, Not Started or awaiting historical evidence. The YAML `status: complete` is authoritative.

**Inspected implementation:** Shop-scoped capability eligibility resolution, MCP tool projection and structured-logging tests are present.

Source and test-file evidence from the 2026-10-15 12:08 workspace snapshot (`moda-interact-mcp/`):

- `src/capabilities/resolve.ts`
- `src/mcp/registration.ts`
- `tests/unit/capabilities/resolve.test.ts`
- `tests/unit/mcp/structured-logging.test.ts`

**Completion authority:** explicit developer decision (`completion_mode: developer`); retrospective source-based reconciliation. This records completion of the *original bounded task scope*, not certification of subsequently discovered system-level defects or unimplemented follow-up tasks. Existing `depends_on` and `enables` remain intact; downstream eligibility is determined from current task metadata.

**Evidence boundary:** the files above were inspected for presence in the uploaded snapshot, not executed as a fresh CI or integration run. Historical branch/worktree provenance, original commits, test command results, pushes and any prior architect acceptance not visible in the snapshot remain unverified; no such evidence is fabricated. The earlier Completion Report and Architect Review remain historical records and are not retrospectively rewritten. Original `attempt`, `executor` and `claimed_at` values are preserved.
