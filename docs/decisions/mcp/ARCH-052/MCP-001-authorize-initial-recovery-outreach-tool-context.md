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
status: review
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

Implemented and validated; submitted for moda_architect review. Attempt 1 remains active.

### Files Changed

Implementation repository files:

- `package.json`, `package-lock.json`
- `src/capabilities/prisma-reader.ts`, `src/capabilities/records.ts`
- `src/execution/discount-tools.ts`, `src/execution/policy/shopify-core.ts`
- `src/mcp/ports.ts`, `src/mcp/registration.ts`, `src/mcp/service.ts`, `src/mcp/snapshot.ts`
- `src/runtime/ports.ts`, `src/runtime/service-ports.ts`
- `tests/fixtures/capabilities.ts`
- `tests/unit/capabilities/prisma-reader.test.ts`, `tests/unit/execution/discount-tools.test.ts`
- `tests/unit/mcp/service.test.ts`, `tests/unit/runtime/ports.test.ts`
- Parent workspace: this task report only.

### Work Completed

- Resumed the existing claimed attempt in the supplied worktrees. Did not rerun the launcher, create worktrees, synchronize branches, initialize submodules, increment the attempt, or make another claim.
- Verified npm publishes `@modainteract/moda-interact-shared@2.7.1` (`dist.tarball` from `npm view`) and inspected that tarball. Its `/commerce` declaration exports `CommerceOutreachToolContextSchema` with the exact strict `{ purpose: "INITIAL_RECOVERY_OUTREACH" }` shape; runtime JS exports the schema. A runtime probe accepted the exact purpose and rejected added `shopId`/`attemptId` keys.
- Verified the same `/commerce` entrypoint exports `CommerceToolInputs` and `CommerceToolOutputs` for discount options and discount details. These schemas are reused for MCP-owned built-in descriptors. The built-in details tool is MCP-owned per task scope; it is not a missing Shared contract.
- Updated MCP's exact dependency and lockfile to 2.7.1. Installation reported the existing Node engine mismatch (requires `24.19.0`, current `24.21.0`) and 11 dependency advisories.
- Implemented purpose-scoped MCP system-tool discovery outside Commerce Studio publication. NONE exposes neither tool; FIXED exposes both with current selected same-shop available IDs or the effective unexpired admin override's exact ID; AI exposes both without applying merchant selection flags. Missing, invalid, wrong-purpose, or identity-bearing context does not expose them.
- Reads current policy on each request. Calls validate Shared inputs and recheck FIXED detail IDs from the fresh request snapshot. Existing private header authentication, active shop and environment validation, published release/feature/definition pinning, conversation capabilities, and generic result protocol remain intact.
- Added tests for modes, changed FIXED selection, exact admin override expiry, context forgery/invalid purpose, unauthenticated header, wrong shop/environment, tool-list/call parity, and zero recovery/attempt table reads. Existing regression tests continue covering disabled published tools and conversation capability isolation.
- Shared 2.7.1 makes `CommerceProductSchema.variantId` nullable; existing product search now skips results without a trusted variant ID.
- No shared source, database schema, recovery/attempt state, grant/replay mechanism, provider writes, conversation identity, index, submodule pointer, or other implementation repository was changed.

### Validation Results

- Published package inspection: `npm view @modainteract/moda-interact-shared@2.7.1 version dist.tarball`, tarball declarations/runtime export inspection, and runtime schema probe all passed. Installed MCP tree reports `@modainteract/moda-interact-shared@2.7.1`.
- Focused suite: `npx tsx --test tests/unit/capabilities/prisma-reader.test.ts tests/unit/execution/discount-tools.test.ts tests/unit/mcp/service.test.ts` — 21 passed, 0 failed.
- Full suite: `npm test` — 173 passed, 0 failed.
- `npm run typecheck` — passed.
- `npm run lint` — passed (`--max-warnings=0`).
- `npm run build` — passed.
- `git diff --check` — passed.
- `npm run test:integration:docker` — attempted; Docker spent over 180 seconds pulling `pgvector/pgvector:pg16`, then reported `spawnSync docker ETIMEDOUT`. PostgreSQL startup and integration assertions did not run; cleanup completed without reporting leftover containers. Live Postgres integration evidence remains outstanding due to the image-pull timeout.
- An initial test invocation before Prisma generation saw a stale generated Prisma client. The declared `npm run prisma:generate` corrected the environment; the final full unit suite passed.

### Deviations

This task implements authorization and discovery only. Authorized built-in calls currently return the existing typed retryable `UNAVAILABLE` result until dependent MCP-002 implements discount catalogue reads. The Docker-backed Postgres integration suite could not start because its image pull timed out.

### Assumptions

The already-claimed attempt and supplied worktree paths are authoritative. No launcher, synchronization, or submodule action was repeated.

### Unresolved Issues

- Docker-backed Postgres integration validation remains outstanding due to `pgvector/pgvector:pg16` pull timeout.
- Authorized options/details catalogue execution is owned by dependent MCP-002 and was not implemented in this task.

### Architectural Concerns

None identified. The implementation uses the published Shared 2.7.1 schemas, keeps built-in tool ownership in MCP, preserves the existing generic MCP result envelope, and performs no recovery/attempt lookup.

### Physical Worktree Evidence

- Canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-052-MCP-001`, branch `task/ARCH-052-MCP-001`; prior claim/blocker report commit `fbf8132` was already published. This report is the only parent file changed.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-052-MCP-001`, branch `task/ARCH-052-MCP-001`; implementation commit `3ebff9e` pushed to `origin/task/ARCH-052-MCP-001`. Configured upstream remains `origin/main`, so the explicit task branch was used.
- No shared checkout, other implementation repository, submodule pointer, index, or unrelated file was changed.
- Launcher synchronization and recursive submodule initialization were not repeated.

## Architect Review

### Review Status

Pending moda_architect review.

### Review Notes

Implementation and validation evidence submitted for independent review. This agent has not made an architect acceptance decision.

### Reviewed Files

Pending.

### Validation Reviewed

Pending.

### Architecture Conformance

Pending independent moda_architect review.

### Follow-up

Review implementation commit `3ebff9e` and the validation/deviation evidence above. No dependent task was started.
