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
claimed_at: 2026-10-30T15:02:28Z
attempt: 2
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

Coordinator: `moda_architect`. The task was materialised and executed at Attempt 1 in dedicated parent and MCP implementation worktrees; both task branches are published. It remains unaccepted pending the required Docker/PostgreSQL integration evidence.

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

- [x] Use the trusted MCP private context with top-level `shopId`/environment and exact `toolContext: {purpose: "INITIAL_RECOVERY_OUTREACH"}`; reject missing/wrong purpose and extra identity keys.
- [x] Project both built-in discount options and discount details tool descriptors into the existing MCP tool list only for an authorised active shop and permitted current discount mode, without Commerce Studio publication. The detail tool receives the same current FIXED/AI/NONE shop-policy check as the options tool; model-provided `offerId` cannot bypass FIXED selection.
- [x] Check current mode and merchant-selected discount scope using existing ShopSettings/ShopifyDiscount records for each relevant request; FIXED is restricted to current exact IDs, while AI is not filtered by selection flags.
- [x] Preserve published product-tool release/feature/definition pin checks; existing conversation callers do not receive purpose-scoped built-in discount tools.
- [x] Add unit/protocol tests for NONE/FIXED/AI, changed selection, inactive/cross-shop failure paths, wrong shop/environment, forged shopId/attemptId, invalid purpose, unauthenticated header, published-tool isolation and conversation isolation.
- [x] Prove purpose authorization makes **no** recovery/attempt-table lookup. Keep existing trusted shop/policy reads.

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

- [x] Purpose-only context, existing outer shop identity and current merchant scope govern discount tool access; no recovery/attempt identifiers are required by `tools/list` or `tools/call`.
- [x] NONE cannot discover/use built-in discount tools; FIXED cannot use an unselected discount; AI is not constrained by merchant checkboxes but remains shop-scoped.
- [x] Revoked shop/merchant permission or forged tool context fails closed before provider I/O.
- [x] Product tools remain release-pinned and feature-authorised; conversational tools and existing generic MCP result schema are unchanged.
- [x] No recovery/attempt lifecycle queries or new grant/nonce tables are introduced.

## Validation

- [ ] Docker-backed MCP/PostgreSQL integration tests (attempted; image pull timed out). Unit Prisma-reader tests spy/assert zero `CheckoutRecovery` or `RecoveryOutreachAttempt` reads in purpose authorization.
- [x] Unit/protocol tests cover discount modes, current FIXED selection, context spoofing, tool list/call parity, shop/environment mismatch and conversation/published-tool isolation. A live Postgres run remains outstanding.
- [x] Run declared MCP scripts and `git diff --check`; document the Docker integration timeout in the Completion Report.

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

Attempt 1 implementation and unit/build validation are complete; architect review requested additional Docker/PostgreSQL integration evidence. Task returns to `ready` at Attempt 1.

### Files Changed

Implementation repository files:

- `package.json`, `package-lock.json`
- `src/capabilities/prisma-reader.ts`, `src/capabilities/records.ts`
- `src/execution/discount-tools.ts`, `src/execution/policy/shopify-core.ts`
- `src/mcp/ports.ts`, `src/mcp/registration.ts`, `src/mcp/service.ts`, `src/mcp/snapshot.ts`
- `src/runtime/ports.ts`, `src/runtime/service-ports.ts`
- `tests/fixtures/capabilities.ts`
- `tests/unit/capabilities/prisma-reader.test.ts`, `tests/unit/execution/discount-tools.test.ts`
- `tests/unit/mcp/service.test.ts`, `tests/unit/runtime/ports.test.ts`, `tests/unit/runtime/service-ports.test.ts`
- Parent workspace: this task report only.

### Work Completed

- Resumed the existing claimed attempt in the supplied worktrees. Did not rerun the launcher, create worktrees, synchronize branches, initialize submodules, increment the attempt, or make another claim.
- Verified npm publishes `@modainteract/moda-interact-shared@2.7.1` (`dist.tarball` from `npm view`) and inspected that tarball. Its `/commerce` declaration exports `CommerceOutreachToolContextSchema` with the exact strict `{ purpose: "INITIAL_RECOVERY_OUTREACH" }` shape; runtime JS exports the schema. A runtime probe accepted the exact purpose and rejected added `shopId`/`attemptId` keys.
- The packed `/commerce` declarations export strict `CommerceToolInputs` and `CommerceToolOutputs` entries for both discount tools: options accepts optional/defaulted `limit` and `cursor`; details accepts `offerId`; each has a corresponding structured output schema. MCP reuses these for its built-in descriptors and argument validation.
- Cross-checked Shared refs: published tag `v2.7.1` (`b56788dd915d75a11ae4492bd84ec134a31577f1`) matches the packed artifact. Current `task/ARCH-052-SHARED-003` (`a44472acf99e20408e1db58d15c2f7f2bfd957b8`) is inconsistent: its `outreach-context.ts` still requires `checkoutRecoveryId` and `outreachAttemptId`, and its commerce schemas do not declare `commerce_get_discount_details`. This implementation uses only the exact published package; no Shared source was changed. The branch/release drift is referred to `moda_architect` for reconciliation.
- Updated MCP's exact dependency and lockfile to 2.7.1. Installation reported the existing Node engine mismatch (requires `24.19.0`, current `24.21.0`) and 11 dependency advisories.
- Implemented purpose-scoped MCP system-tool discovery outside Commerce Studio publication. NONE exposes neither tool; FIXED exposes both with current selected same-shop available IDs or the effective unexpired admin override's exact ID; AI exposes both without applying merchant selection flags. Missing, invalid, wrong-purpose, or identity-bearing context does not expose them.
- Reads current policy on each request. Calls validate Shared inputs and recheck FIXED detail IDs from the fresh request snapshot. Existing private header authentication, active shop and environment validation, published release/feature/definition pinning, conversation capabilities, and generic result protocol remain intact.
- Added tests for modes, changed FIXED selection, exact admin override expiry, context forgery/invalid purpose, unauthenticated header, wrong shop/environment, tool-list/call parity, and zero recovery/attempt table reads. Existing regression tests continue covering disabled published tools and conversation capability isolation.
- Shared 2.7.1 makes `CommerceProductSchema.variantId` nullable; existing product search now skips results without a trusted variant ID.
- No shared source, database schema, recovery/attempt state, grant/replay mechanism, provider writes, conversation identity, index, submodule pointer, or other implementation repository was changed.

### Validation Results

- Published package inspection: `npm view @modainteract/moda-interact-shared@2.7.1 version dist.tarball`, tarball declarations/runtime export inspection, and runtime schema probe all passed. Installed MCP tree reports `@modainteract/moda-interact-shared@2.7.1`.
- Focused suite: `npx tsx --test tests/unit/capabilities/prisma-reader.test.ts tests/unit/execution/discount-tools.test.ts tests/unit/mcp/service.test.ts` — 21 passed, 0 failed.
- Full suite: `npm test` — 174 passed, 0 failed.
- `npm run typecheck` — passed.
- `npm run lint` — passed (`--max-warnings=0`).
- `npm run build` — passed.
- `git diff --check` — passed in the implementation worktree; the parent task-file report is the only parent change.
- `npm run test:integration:docker` — the prior task report records an attempt where Docker spent over 180 seconds pulling `pgvector/pgvector:pg16`, then reported `spawnSync docker ETIMEDOUT`. PostgreSQL startup and integration assertions did not run; cleanup reported no leftover containers. Not rerun during this resumption because it is a long Docker integration suite; live Postgres evidence remains outstanding.
- An initial test invocation before Prisma generation saw a stale generated Prisma client. The declared `npm run prisma:generate` corrected the environment; the final full unit suite passed.

### Deviations

This task implements authorization and discovery only. Authorized built-in calls currently return the existing typed retryable `UNAVAILABLE` result until dependent MCP-002 implements discount catalogue reads. The Docker-backed Postgres integration suite could not start because its image pull timed out.

### Assumptions

The already-claimed attempt and supplied worktree paths are authoritative. No launcher, synchronization, or submodule action was repeated.

### Unresolved Issues

- Docker-backed Postgres integration validation remains outstanding due to `pgvector/pgvector:pg16` pull timeout.
- Authorized options/details catalogue execution is owned by dependent MCP-002 and was not implemented in this task.
- The current Shared task branch does not match the published 2.7.1 contract. Architect review should reconcile its purpose schema and missing discount-details contract before promoting/merging that branch; MCP consumes the verified published artifact.

### Architectural Concerns

The implementation uses the published Shared 2.7.1 schemas, keeps built-in tool ownership in MCP, preserves the existing generic MCP result envelope, and performs no recovery/attempt lookup. The Shared task-branch/release drift is a separate cross-repository concern recorded above.

### Physical Worktree Evidence

- Canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-052-MCP-001`, branch `task/ARCH-052-MCP-001`; prior claim/blocker report commit `fbf8132` was already published. This report is the only parent file changed.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-052-MCP-001`, branch `task/ARCH-052-MCP-001`; implementation commits `3ebff9e` and `afb76ff` are pushed, and `afb76ff18502b1631a3bcebfba791f34ec653cce` is the current `origin/task/ARCH-052-MCP-001` tip. Configured upstream remains `origin/main`, so the explicit task branch was verified.
- No shared checkout, other implementation repository, submodule pointer, index, or unrelated file was changed.
- Launcher synchronization and recursive submodule initialization were not repeated.

## Architect Review — Attempt 1 (Changes Requested)

### Review Status

Changes Requested. Return the task to `ready`; preserve Attempt 1 and clear the executor claim. No new attempt is started by this review.

### Review Notes

The implementation diff appears consistent with the task's purpose-scoped discovery and authorization boundaries: it consumes the published Shared package, re-reads shop policy for requests, keeps FIXED selections shop-scoped, preserves published-tool and conversation isolation, and adds no recovery/attempt lookup. The code review found no implementation defect.

The required Docker-backed MCP/PostgreSQL integration validation remains unchecked. The report records an image-pull timeout before PostgreSQL startup, so no live database-backed authorization/integration assertion ran. Unit Prisma-reader spies are useful but do not replace the task's declared integration evidence.

The report also identifies a mismatch between the published Shared 2.7.1 artifact and the current SHARED-003 task branch. The MCP implementation used and inspected the published artifact as required; reconcile that contract/release drift with the architect before downstream integration. This is recorded as an architecture coordination item, separate from the missing database test evidence.

### Reviewed Files

Reviewed the implementation diff in `src/capabilities/prisma-reader.ts`, `src/capabilities/records.ts`, `src/execution/discount-tools.ts`, `src/execution/policy/shopify-core.ts`, MCP registration/service/snapshot and runtime ports, plus the associated tests and task Completion Report.

### Validation Reviewed

The report records 21 focused tests, 174 full-suite tests, typecheck, lint, build and package-contract probes passing. The required Docker-backed integration run timed out while pulling `pgvector/pgvector:pg16`; it did not reach PostgreSQL startup. No tests were rerun during this architect review.

### Architecture Conformance

The implementation stays within MCP's authorization and discovery ownership. The unresolved Shared package/task-branch drift requires reconciliation before dependent integration work relies on a source branch or release.

### Required Follow-up

Run the declared Docker-backed MCP/PostgreSQL integration validation when the image/runtime is available, record the result and cleanup evidence in this task report, and return the same Attempt 1 for review. Reconcile the Shared contract/release mismatch with the architect; do not change Shared source within this task. Do not begin MCP-002 or either system test from this Changes Requested state.
