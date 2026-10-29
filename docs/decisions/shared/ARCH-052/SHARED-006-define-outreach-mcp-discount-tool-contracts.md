---
id: ARCH-052-SHARED-006
architecture_id: ARCH-052
title: Define the minimal outreach MCP execution-context contract
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 10
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables:
- ARCH-052-SHARED-003
created: '2026-10-29'
updated: '2026-10-29'
---

# ARCH-052-SHARED-006: Define the minimal outreach MCP execution-context contract

## Architecture

Architecture ID: `ARCH-052`.

Architecture document: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`.

Coordinator: `moda_architect`. Portable canonical definition: **defined but not materialised**; no developer worktree, branch, commit or push has occurred.

## Objective

Define only the trusted `INITIAL_RECOVERY_OUTREACH` MCP call context shared by Background and MCP. Do not create a new MCP response format, duplicate a tool registry, or modify the existing conversational CommerceAgent input/output contract.

## Context

`commerce_get_discount_options` / `commerce_evaluate_discount` are already named Shared schemas but the standalone MCP runtime lacks handlers. `CommerceModelInvoker` is conversation-independent; the new Background agent will use it directly. System tools are available only under validated outreach purpose, not in general conversation tool discovery.

## Scope

- Extend existing commerce assertion/context parsing with a strict discriminant `{purpose:"INITIAL_RECOVERY_OUTREACH",checkoutRecoveryId:string,outreachAttemptId:string}` under an authenticated shop/environment context. No customer message, inbound version, conversation ID or lease is fabricated. MCP must independently compare identity with current PostgreSQL recovery/attempt records.
- Reuse **unchanged** `CommerceToolResultSchema`, `commerceToolResultSchema(data)`, and MCP `structuredContent` for all feature calls. Do **not** introduce `OutreachToolResult`, an outreach-only envelope, or override current conversation `CommerceToolInputs.commerce_get_discount_options` (`{}`) and `CommerceToolInputs.commerce_evaluate_discount` (`{offerId,proposal}`).
- System-defined discount tool names remain `commerce_get_discount_options` and `commerce_evaluate_discount`. Their **outreach-scoped advertised inputSchema**, execution and feature-specific result validation belong to MCP-002; define only reusable types needed at the Background/MCP context boundary. Product tool inputs/outputs remain SHARED-008.
- MCP enforces current mode/selected discount authorization from existing merchant state at each call. No policy snapshot digest, frozen IDs in trusted assertion, merchant configuration fetch tool or duplicate selection-JSON schema is introduced.
- Tests cover correctly scoped context, invalid identity/purpose, attempted model-authored shop/attempt overrides, result-envelope reuse and unchanged conversation tool schemas.

## Out of Scope

- No new database tables/columns, duplicate recovery-offer engine, unrelated UI, provider writes, or changes outside this repository and its own task report.

## Requirements

- Re-read canonical task, parent architecture, dependency task files, `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md` and launcher preparation evidence before claiming. Use launcher-resolved **dedicated mirrored parent and implementation worktrees**, not a shared checkout.
- Use the existing `@modainteract/moda-interact-shared/logging` API for new Node logs; unexpected exceptions are logged with bounded reason codes and propagated to the owning retry boundary. No silent exception swallowing, competing generic logger or secret-bearing diagnostic body.
- Never log customer PII, coupon codes, complete checkout URLs, product-image origins, provider responses, credentials or raw MCP context headers.
- Provider operations are read-only. No applying/creating coupons or mutating carts/orders except the separate customer-initiated Woo restore flow.
- Pre-production breaking cutover: **no legacy/outdated attempt parsing, old tool-version adapter, backfill or new Prisma schema**. Missing required configuration fails closed. One released Shared version and actual published Commerce capability revision must be in use; no direct sibling imports.


## Work Items

- [ ] Add the strict outreach assertion/context discriminant to existing Shared commerce types and exports.
- [ ] Prove existing generic result and conversational tool schemas remain unchanged.
- [ ] Add negative identity/purpose tests and run Shared declared validation.

## Interfaces / Contracts

`@modainteract/moda-interact-shared/commerce`: `CommerceOutreachToolContextSchema` (or the existing assertion union extended with that discriminant), existing `CommerceToolResultSchema`. MCP-002 advertises and validates its tool input/output schemas; no new generic tool-result contract.

## Dependencies

None.

Dependencies are authoritative in YAML; system tests are terminal validation and must never block implementation.

## Enables

- `ARCH-052-SHARED-003`

## Acceptance Criteria

- [ ] Background and MCP can share a trusted outreach attempt identity without a conversation.
- [ ] Existing generic MCP envelope and conversational discount tool shapes remain unchanged.
- [ ] No `commerce_get_outreach_context` tool or frozen-policy schema is introduced.

## Validation

- [ ] Schema unit/negative cases and `src/commerce/contracts.test.ts`.
- [ ] Shared declared typecheck, build, lint where configured.

Use the task repository's actual `package.json` validation scripts; do not invent unconfigured commands or claim unrun tests passed. Include `git diff --check`.

## Stop Condition

After all Work Items, Acceptance Criteria and required Validation are complete, fill the Completion Report, change the task status to `review`, return the parent task report and implementation branch to `moda_architect` and **STOP**. Do not start dependent tasks, merge, push `main`, or alter architecture/domain indexes.

## Implementation Notes

**Owning repository paths (workspace-relative; verify actual current paths at execution):**

- `moda-interact-shared/src/commerce/schemas.ts`
- `moda-interact-shared/src/commerce/definitions.ts`
- `moda-interact-shared/src/commerce/contracts.test.ts`
- `moda-interact-shared/src/commerce/index.ts`

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
