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
status: in_progress
priority: 35
executor: copilot
claimed_at: 2026-10-30T11:53:54Z
attempt: 1
depends_on:
- ARCH-052-SHARED-003
enables:
- ARCH-052-MCP-002
- ARCH-052-SYSTEM-TEST-001
- ARCH-052-SYSTEM-TEST-002
created: '2026-10-29'
updated: 2026-10-30
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
- At `tools/list` and `tools/call`, use shop-scoped Prisma reads to enforce **current merchant discount policy** and selected discount permissions: mode NONE advertises no built-in discount tools; FIXED limits discount results to selected `ShopifyDiscount.isAvailable=true` IDs (or an effective, current, exact-ID admin override); AI considers provider-current catalogue irrespective of merchant selection flags. Recheck merchant policy on calls so a changed selection is not usable through an old tool-list snapshot.
- Preserve tool-list/call parity, existing shop/tenant isolation, published product release/feature membership, descriptor pinning, existing private-ingress authentication and typed failures. The built-in `commerce_get_discount_options` and `commerce_get_discount_details` tools are not Commerce Studio published tools; only the trusted outreach purpose exposes them.
- **Do not query `CheckoutRecovery` or `RecoveryOutreachAttempt` as an MCP authorisation precondition.** Do not require a recovery ID, attempt ID, checkout fingerprint or conversation lease in the generic `toolContext`. Background owns recovery/attempt checks and final-send admission.
- Reject an invalid/untrusted context or tool request without leaking data; preserve current conversational CommerceAgent tool behaviour and isolate purpose-only built-in tools from conversational callers.

## Out of Scope

- No new database state, frozen policy, HMAC framework, recovery/attempt replay-store, synthetic conversation, provider writes or new MCP success/error envelope.
- Do not implement MCP-002 discount catalogue queries, MCP-003 provider product search, or Commerce Studio product descriptor authoring in this task.
- Use existing shop-scoped MCP tool context; no provider-proof schema, recovery/attempt lookups or model-generated tenant identity fields.

## Requirements

- Use the existing `@modainteract/moda-interact-shared/commerce` published `CommerceOutreachToolContextSchema`, not a local duplicate. The context is a structural discriminator, not a business grant.
- MCP independently enforces trusted outer-shop identity, current shop settings and permitted tool capability. Valid purpose text alone must not bypass existing private-ingress or tenant checks.
- No `CheckoutRecovery`/`RecoveryOutreachAttempt` lookup or attempt expiry/checkout-fingerprint check in MCP's generic tool-list/call authorisation. Those remain Background's responsibility.
- Preserve existing authentication of private ingress and published-tool entitlement, and fail closed on missing/malformed context, revoked merchant settings or unavailable configuration.
- Follow dedicated mirrored task-worktree, launcher packet and Completion Report requirements (`docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`). Use `@modainteract/moda-interact-shared/logging` for new Node logs, emit bounded identifiers/reason codes, and propagate unexpected exceptions; never log raw context headers, credentials, customer data, coupon codes or full checkout URLs.
- Read-only commerce operations; no cart/order mutation and no new legacy compatibility machinery in this pre-production initiative.

## Work Items

- [ ] Use the trusted MCP private context with top-level `shopId`/environment and exact `toolContext: {purpose: "INITIAL_RECOVERY_OUTREACH"}`; reject missing/wrong purpose and extra identity keys.
- [ ] Project both built-in discount options and discount details tool descriptors into the existing MCP tool list only for an authorised active shop and permitted current discount mode, without Commerce Studio publication. The detail tool must receive the same current FIXED/AI/NONE shop-policy check as the options tool; model-provided `offerId` is never a bypass.
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

Built-in tool names: `commerce_get_discount_options`, `commerce_get_discount_details`. Published product names: `commerce_search_products`, `commerce_get_product`. Reuse MCP's current generic `CommerceToolResultSchema` and existing `tools/list` / `tools/call` transport. No outreach-specific result envelope, context lookup tool or model-supplied shop identity.

## Dependencies

- ARCH-052-SHARED-003

## Enables

- ARCH-052-MCP-002
- ARCH-052-SYSTEM-TEST-001
- ARCH-052-SYSTEM-TEST-002

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

Keep public API and conversation identity handling unchanged. This task only changes purpose-scoped tool availability and authorisation; no provider-proof request is involved.

## Completion Report

### Status

Blocked — task claimed as Attempt 1; implementation has not started because the required Shared contracts do not match the task definition.

### Files Changed

No implementation files changed. This task file is updated only to record the blocker.

### Work Completed

- Confirmed the canonical parent and implementation worktrees are on `task/ARCH-052-MCP-001` and clean; did not repeat launcher synchronization or submodule preparation.
- Installed the implementation worktree's locked npm dependencies for contract inspection. The pinned `@modainteract/moda-interact-shared@2.4.1` package does not export `CommerceOutreachToolContextSchema`.
- Inspected published Shared `2.6.0` and `origin/task/ARCH-052-SHARED-003`: both still define `CommerceOutreachToolContextSchema` with required `checkoutRecoveryId` and `outreachAttemptId`; neither exposes `commerce_get_discount_details`.
- Stopped before implementation to avoid duplicating or locally redefining a missing cross-repository contract.

### Validation Results

- `npm ci`: completed; emitted the existing Node engine mismatch warning (required `24.19.0`, current `24.21.0`) and reported 11 dependency advisories.
- Focused runtime export check against the pinned package: failed because `CommerceOutreachToolContextSchema` is not exported by version `2.4.1`.
- Contract inspection of published Shared `2.6.0` and the completed Shared task branch confirmed the identity-bearing context and missing discount-details descriptor.
- MCP tests, typecheck, lint, and build were not run because no implementation edit was made and the required cross-repository contracts are unresolved. `git diff --check` on this parent task-file update passed; there is no implementation diff to check.

### Deviations

Implementation and both task-branch publication steps are deferred pending explicit architect sequencing for the Shared contract mismatch. Task remains `in_progress`; it is not being returned to review.

### Assumptions

The launcher packet is authoritative for completed synchronization and recursive database submodule preparation; neither was repeated.

### Unresolved Issues

- Shared must publish/export the purpose-only `CommerceOutreachToolContextSchema` required by this task, and the discount-details tool contract must be established in the owning shared boundary before MCP implements it.

### Architectural Concerns

The completed Shared task and published package artifacts do not contain the contracts this task specifies. Request `moda_architect` to sequence the Shared correction and update the MCP dependency before resuming; do not create local schema copies or identity compatibility behavior.

### Physical Worktree Evidence

- Canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-052-MCP-001`, branch `task/ARCH-052-MCP-001`, clean and up to date with `origin/task/ARCH-052-MCP-001`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-052-MCP-001`, branch `task/ARCH-052-MCP-001`, clean; its configured upstream is `origin/main`.
- Shared workspace checkout switched/mutated for task work: no.
- Shared implementation checkout switched/mutated for task work: no.
- Another task worktree reused: no.
- Launcher synchronization: not repeated per instruction; prepared packet confirms `prepared_execution=true` and parent claim commit `4559545ecf891496fd7bd1763f781fc8afca4d40`.
- Recursive database submodule: launcher packet confirms initialized at `139765042baad3901682cfe9c54a3d6bba73e75c`; no submodule command was rerun.

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
