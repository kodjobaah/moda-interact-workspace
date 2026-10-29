---
id: ARCH-052-MCP-001
architecture_id: ARCH-052
title: Authorize outreach-scoped built-in discount tools and published product tools
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

# ARCH-052-MCP-001: Authorize outreach-scoped built-in discount tools and published product tools

## Architecture

Architecture ID: `ARCH-052`.

Architecture document: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`.

Coordinator: `moda_architect`. Portable canonical definition: **defined but not materialised**; no developer worktree, branch, commit or push has occurred.

## Objective

Add a trusted `INITIAL_RECOVERY_OUTREACH` attempt identity to the existing private MCP request context; **system-defined** discount tools are authorised by validated recovery/attempt policy, while published product tools still obey the Commerce release/capability registry.

## Context

`moda-interact-mcp/src/mcp/authentication.ts` already parses `X-Moda-Commerce-Context` and passes an opaque `toolContext`; `src/runtime/execution-registry.ts` reloads published shop capability/release before each tools/call. Neither currently authorises an initial recovery attempt against the shop's **current** discount settings for built-in discount operations.

Source evidence: `moda-interact-workspace(20261029-080732).zip`. This task changes documentation in the parent only until materialised by the developer.

## Scope

- Extend `src/mcp/authentication.ts`, `src/mcp/service.ts`, `src/mcp/registration.ts`, `src/mcp/snapshot.ts` with strict validated `CommerceOutreachToolContextSchema` purpose; never accept `shopId`, policies or product credentials from model tool arguments. Re-read shop, CheckoutRecovery and RecoveryOutreachAttempt by shopId+IDs and current merchant mode, selected `ShopifyDiscount.isAvailable` rows and effective override on every tools/list and tools/call; require attempt initial-send eligible, merchant active, no STOP/withdrawal and recovery fingerprint fresh.
- Add a guarded *system capability* projection for built-in `commerce_get_discount_options` and `commerce_evaluate_discount` to existing MCP advertised snapshot and executor dispatch only for this purpose. These tools do not need Commerce Studio drafts, release pointers or capability membership; they must still be unavailable for unscoped/conversation/bad-auth contexts. Published product tools `commerce_search_products` and `commerce_get_product` remain subject to their immutable release/feature entitlement and pin.
- Validate tools/call against the exact tools/list snapshot and recheck policy just before execution; prevent replay, cross-tenant selected-set expansion, admin override mixing and spoofed conversation assertions. Preserve existing Commerce conversation tools/list, grant handling and `runCommerceTurn` behavior unchanged.
- Security tests: NONE -> zero discount tools, FIXED selected IDs only, AI all provider-current candidates (not unchecked flag), expired attempt and revoked merchant/shop, wrong environment, malicious toolContext, unauthenticated header, disabled published tool and concurrent policy edit rejects a now-unauthorised offer and makes the next tool call use fresh settings.

## Out of Scope

- No new database tables/columns, policy snapshot or duplicate recovery-offer engine, unrelated UI, provider writes, or changes outside this repository and its own task report.

## Requirements

- Re-read canonical task, parent architecture, dependency task files, `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md` and launcher preparation evidence before claiming. Use launcher-resolved **dedicated mirrored parent and implementation worktrees**, not a shared checkout.
- Use the existing `@modainteract/moda-interact-shared/logging` API for new Node logs; unexpected exceptions are logged with bounded reason codes and propagated to the owning retry boundary. No silent exception swallowing, competing generic logger or secret-bearing diagnostic body.
- Never log customer PII, coupon codes, complete checkout URLs, product-image origins, provider responses, credentials or raw MCP context headers.
- Provider operations are read-only. No applying/creating coupons or mutating carts/orders except the separate customer-initiated Woo restore flow.
- Pre-production breaking cutover: **no legacy/outdated attempt parsing, old tool-version adapter, backfill or new Prisma schema**. Missing required configuration fails closed. One released Shared version and actual published Commerce capability revision must be in use; no direct sibling imports.


## Work Items

- [ ] Extend `X-Moda-Commerce-Context` parsing to require trusted `INITIAL_RECOVERY_OUTREACH` purpose and bound `{shopId,checkoutRecoveryId,outreachAttemptId,environment}`; the model cannot set identity.
- [ ] Re-read recovery attempt/merchant/current discount mode and selected rows through existing MCP Prisma on every tools/list and tools/call; enforce attempt expiry, tenant, checkout fingerprint, admin override and current FIXED discount set.
- [ ] Register built-in discount tools only for valid outreach context; continue the existing published release/feature/definition pin checks for `commerce_search_products` and `commerce_get_product`. No public unauthenticated global exposure.
- [ ] Test revocation, wrong tenant, NONE, FIXED, AI, invalid environment, entitlement removal and conversation-tool isolation; no invented conversation or lease.

## Interfaces / Contracts

Shared-006 `CommerceOutreachToolContextSchema`; built-in discount capability names `commerce_get_discount_options` and `commerce_evaluate_discount`; published product names `commerce_search_products` and `commerce_get_product`; existing `X-Moda-Commerce-Context` private transport, no fabricated conversation.

## Dependencies

- `ARCH-052-SHARED-003` — must be Complete and architect-accepted before this task starts.

Dependencies are authoritative in YAML; system tests are terminal validation and must never block implementation.

## Enables

- `ARCH-052-MCP-002`
- `ARCH-052-MCP-004`
- `ARCH-052-SYSTEM-TEST-001`
- `ARCH-052-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] Only trusted initial attempts see built-in discount tools and never any session-only tool; current conversation users do not inherit initial outreach tools.
- [ ] Published product tools are still release-pinned/entitlement checked, while discount tools do not require authoring/release.
- [ ] Revocation/wrong-tenant fail closed before provider I/O.

## Validation

- [ ] MCP auth/Prisma/registry integration tests with both shop platforms and a real or test PostgreSQL harness.
- [ ] MCP declared typecheck/test/lint and `git diff --check`.

Use the task repository's actual `package.json` validation scripts; do not invent unconfigured commands or claim unrun tests passed. Include `git diff --check`.

## Stop Condition

After all Work Items, Acceptance Criteria and required Validation are complete, fill the Completion Report, change the task status to `review`, return the parent task report and implementation branch to `moda_architect` and **STOP**. Do not start dependent tasks, merge, push `main`, or alter architecture/domain indexes.

## Implementation Notes

**Owning repository paths (workspace-relative; verify actual current paths at execution):**

- `moda-interact-mcp/src/mcp/authentication.ts`
- `moda-interact-mcp/src/runtime/service-ports.ts`
- `moda-interact-mcp/src/runtime/prisma.ts`
- `moda-interact-mcp/src/runtime/execution-registry.ts`
- `moda-interact-mcp/src/execution/policy/` (new scoped discount read port)
- `moda-interact-mcp/tests/`

The owning logical agent may modify its assigned task report only outside its source repository. Architecture and indexes belong to `moda_architect`.

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

Escalate any unexpected provider API/auth/Shared/schema/contract gap to `moda_architect` without inventing a second implementation.

## Architect Review

### Review Status

Pending.

### Review Notes

Task definition only. No implementation accepted.

### Reviewed Files

Relevant October 29, 2026 code snapshot and task definition; no implementation source changes for this task reviewed.

### Validation Reviewed

None for implementation.

### Architecture Conformance

Pending implementation review.

### Follow-up

Materialise through the canonical launcher only after all dependency task YAMLs are Complete.
