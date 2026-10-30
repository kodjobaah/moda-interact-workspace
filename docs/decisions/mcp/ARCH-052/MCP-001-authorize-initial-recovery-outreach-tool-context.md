---
id: ARCH-052-MCP-001
architecture_id: ARCH-052
title: Authorize purpose-scoped MCP commerce tools for initial outreach
task_kind: implementation
domain: mcp
repository: moda-interact-mcp
assigned_agent: moda_mcp
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 35
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-052-SHARED-003
enables:
- ARCH-052-MCP-002
- ARCH-052-MCP-004
- ARCH-052-SYSTEM-TEST-001
- ARCH-052-SYSTEM-TEST-002
created: '2026-10-29'
updated: '2026-10-29'
---

# ARCH-052-MCP-001: Authorize purpose-scoped MCP commerce tools for initial outreach

## Architecture

Architecture ID: `ARCH-052`.

Architecture document: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`.

Coordinator: `moda_architect`. Portable canonical definition: **defined but not materialised**; no developer worktree, branch, commit or push is asserted.

## Objective

Authorise the `INITIAL_RECOVERY_OUTREACH` **purpose** within MCP's existing private, shop-scoped tool-discovery and execution boundary. The purpose is **not** a recovery/attempt identity: Background is responsible for admission of the actual recovery attempt. Continue existing release/feature authorisation for published product tools and add narrowly scoped system-owned discount tools.

## Context

`moda-interact-mcp/src/mcp/authentication.ts` already receives an authenticated private-ingress top-level `shopId` and optional opaque `toolContext` via `X-Moda-Commerce-Context`. The Shared-006 schema now contains only `purpose`. MCP already has Prisma access for current shop, merchant discount settings, catalogue and selected flags. The Background recovery workflow owns the checkout, attempt, consent/STOP and final-send lifecycle; it passes checkout context to the agent without making MCP an outreach lifecycle manager.

## Scope

- Parse the **existing** private MCP context, requiring `CommerceOutreachToolContextSchema` only for outreach-purpose tool access. The exact `toolContext` is `{ purpose: "INITIAL_RECOVERY_OUTREACH" }`. The authenticated outer context supplies `shopId` and environment; never accept those from model-authored tool arguments.
- At `tools/list` and `tools/call`, use shop-scoped Prisma reads to enforce **current merchant discount policy** and selected discount permissions: mode NONE advertises no built-in discount tools; FIXED limits discount results/evaluation to selected `ShopifyDiscount.isAvailable=true` IDs (or an effective, current, exact-ID admin override); AI considers provider-current catalogue irrespective of merchant selection flags. Recheck merchant policy on calls so a changed selection is not usable through an old tool-list snapshot.
- Preserve tool-list/call parity, existing shop/tenant isolation, published product release/feature membership, descriptor pinning, existing private-ingress authentication and typed failures. Built-in `commerce_get_discount_options` / `commerce_evaluate_discount` are not Commerce Studio published tools; only the trusted outreach purpose exposes them.
- **Do not query `CheckoutRecovery` or `RecoveryOutreachAttempt` as an MCP authorisation precondition.** Do not require a recovery ID, attempt ID, checkout fingerprint or conversation lease in the generic `toolContext`. Background owns recovery/attempt checks and final-send admission.
- Reject an invalid/untrusted context or tool request without leaking data; preserve current conversational CommerceAgent tool behaviour and isolate purpose-only built-in tools from conversational callers.

## Out of Scope

- No new database state, frozen policy, HMAC framework, recovery/attempt replay-store, synthetic conversation, provider writes or new MCP success/error envelope.
- Do not implement MCP-002 discount catalogue/proof algorithms, MCP-003 provider product search, or Commerce Studio product descriptor authoring in this task.
- SHARED-005 provider-proof messages are distinct from the generic MCP `toolContext`; this task does not change that proof schema or authorise model-generated recovery/attempt identity fields.

## Requirements

- Use the existing `@modainteract/moda-interact-shared/commerce` published `CommerceOutreachToolContextSchema`, not a local duplicate. The context is a structural discriminator, not a business grant.
- MCP independently enforces trusted outer-shop identity, current shop settings and permitted tool capability. Valid purpose text alone must not bypass existing private-ingress or tenant checks.
- No `CheckoutRecovery`/`RecoveryOutreachAttempt` lookup or attempt expiry/checkout-fingerprint check in MCP's generic tool-list/call authorisation. Those remain Background's responsibility.
- Preserve existing authentication of private ingress and published-tool entitlement, and fail closed on missing/malformed context, revoked merchant settings or unavailable configuration.
- Follow dedicated mirrored task-worktree, launcher packet and Completion Report requirements (`docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`). Use `@modainteract/moda-interact-shared/logging` for new Node logs, emit bounded identifiers/reason codes, and propagate unexpected exceptions; never log raw context headers, credentials, customer data, coupon codes or full checkout URLs.
- Read-only commerce operations; no cart/order mutation and no new legacy compatibility machinery in this pre-production initiative.

## Work Items

- [ ] Use the trusted MCP private context with top-level `shopId`/environment and exact `toolContext: {purpose: "INITIAL_RECOVERY_OUTREACH"}`; reject missing/wrong purpose and extra identity keys.
- [ ] Project built-in discount tool descriptors into the existing MCP tool list only for an authorised active shop and permitted current discount mode, without Commerce Studio publication.
- [ ] Check current mode and merchant-selected discount scope using the existing ShopSettings/ShopifyDiscount tables for each relevant tool call; prevent FIXED from reading/using unselected discounts and AI from being incorrectly filtered by the selection flag.
- [ ] Preserve published product-tool release/feature/definition pin checks; prevent conversations and other purposes from inheriting initial-outreach-only built-in discount tools.
- [ ] Add tests for NONE/FIXED/AI, changed discount selection, revoked shop, wrong shop/environment, forged shopId or attemptId in `toolContext`, invalid purpose, unauthenticated header, published tool disabled and conversation isolation.
- [ ] Prove MCP's purpose authorisation makes **no** recovery/attempt-table lookup. Keep existing trusted shop/policy reads.

## Interfaces / Contracts

**Shared-006 purpose-only toolContext (exact):**

```typescript
{
  purpose: "INITIAL_RECOVERY_OUTREACH"
}
```

**Existing private request context (outer shape owned by MCP; example):**

```json
{
  "shopId": "shop_123",
  "toolContext": {
    "purpose": "INITIAL_RECOVERY_OUTREACH"
  }
}
```

Built-in tool names: `commerce_get_discount_options`, `commerce_evaluate_discount`. Published product names: `commerce_search_products`, `commerce_get_product`. Reuse MCP's current generic `CommerceToolResultSchema` and existing `tools/list` / `tools/call` transport. No outreach-specific result envelope, context lookup tool or model-supplied shop identity.

## Dependencies

- `ARCH-052-SHARED-003` — published Shared-006 purpose-only schema must be Complete and architect-accepted before this task starts.

## Enables

- `ARCH-052-MCP-002`
- `ARCH-052-MCP-004`
- `ARCH-052-SYSTEM-TEST-001`
- `ARCH-052-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] Purpose-only context, existing outer shop identity and current merchant scope govern discount tool access; no recovery/attempt identifiers are required by `tools/list` or `tools/call`.
- [ ] NONE cannot discover/use built-in discount tools; FIXED cannot use an unselected discount; AI is not constrained by merchant checkboxes but remains shop-scoped.
- [ ] Revoked shop/merchant permission or forged tool context fails closed before provider I/O.
- [ ] Product tools remain release-pinned and feature-authorised; conversational tools and existing generic MCP result schema are unchanged.
- [ ] No recovery/attempt lifecycle queries or new grant/nonce tables are introduced.

## Validation

- [ ] MCP auth, registry and shop-policy integration tests with PostgreSQL fixtures; spy/assert zero `CheckoutRecovery` or `RecoveryOutreachAttempt` reads in MCP purpose authorisation.
- [ ] Test both shop platforms, revoked merchant/discount permissions, dynamic FIXED selection changes, context spoofing, tool list/call parity and conversation isolation.
- [ ] Run only scripts declared by MCP's `package.json` plus `git diff --check`; document failures and missing scripts in the Completion Report.

## Stop Condition

After Work Items, Acceptance Criteria and required Validation, complete the task report, set `status: review`, return branch/worktree evidence to `moda_architect` and **STOP**. Do not implement dependent tasks, merge, push main or modify parent architecture/indexes.

## Implementation Notes

Owning repository paths (workspace-relative; verify before edit):

- `moda-interact-mcp/src/mcp/authentication.ts`
- `moda-interact-mcp/src/mcp/service.ts`
- `moda-interact-mcp/src/mcp/registration.ts`
- `moda-interact-mcp/src/mcp/snapshot.ts`
- `moda-interact-mcp/src/runtime/prisma.ts`
- `moda-interact-mcp/src/runtime/execution-registry.ts`
- `moda-interact-mcp/tests/`

Keep public API and conversation identity handling unchanged. The proof-specific request governed by SHARED-005 remains separate; this task only changes purpose-scoped tool availability/authorisation.

## Completion Report

### Status

Not Started — portable definition, no task claim.

### Files Changed

None yet.

### Work Completed

None yet.

### Validation Results

Not run.

### Deviations

None reported.

### Assumptions

Implementation must confirm package versions and the current task worktree baseline.

### Unresolved Issues

None established by implementation.

### Architectural Concerns

Escalate unexpected auth/contract/provider concerns to `moda_architect`; do not invent a second result envelope or conversation access path.

## Architect Review

### Review Status

Pending.

### Review Notes

Task definition only. No implementation accepted.

### Reviewed Files

Relevant October 29, 2026 snapshot and task definition; no implementation source changes reviewed.

### Validation Reviewed

None for implementation.

### Architecture Conformance

Pending implementation review.

### Follow-up

Materialise through the canonical launcher only after its task dependencies are Complete.
