---
id: ARCH-052-MCP-002
architecture_id: ARCH-052
title: Execute built-in discount discovery and checkout proof in MCP
task_kind: implementation
domain: mcp
repository: moda-interact-mcp
assigned_agent: moda_mcp
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 45
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-052-MCP-001
- ARCH-052-MCP-003
- ARCH-052-COMMERCE-003
- ARCH-052-WOOCOMMERCE-001
- ARCH-052-GATEWAY-001
- ARCH-052-SHARED-003
enables:
- ARCH-052-BACKGROUND-010
- ARCH-052-MCP-004
- ARCH-052-SYSTEM-TEST-001
- ARCH-052-SYSTEM-TEST-002
created: '2026-10-29'
updated: '2026-10-29'
---

# ARCH-052-MCP-002: Execute built-in discount discovery and checkout proof in MCP

## Architecture

Architecture ID: `ARCH-052`.

Architecture document: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`.

Coordinator: `moda_architect`. Portable canonical definition: **defined but not materialised**; no developer worktree, branch, commit or push has occurred.

## Objective

Implement **system-owned**, read-only MCP discount options and checkout-specific provider verification; do not author or publish Commerce Studio discount-tool revisions.

## Context

Discount catalogue, current merchant selection and settings are in existing PostgreSQL; Shopify provider checkout proof belongs to Commerce, Woo native proof to WooCommerce plugin. MCP-003 directly owns Woo grant/REST read transport.

## Scope

- Add `src/execution/policy/discount-tool-executor.ts` registered as built-in only for authorised `INITIAL_RECOVERY_OUTREACH` context in `src/runtime/service-ports.ts`. For `commerce_get_discount_options`, query existing shop-scoped `ShopifyDiscount` + catalogue tables with Prisma, FIXED selected IDs from **current** same-shop `ShopifyDiscount.isAvailable=true` rows (or an active exact-ID Admin override), never an attempt snapshot, AI provider-current discounts independent of `isAvailable`, numeric/page bounds <=50 and signed/opaque per-shop/per-attempt cursor (stable ordered `id`, no blind 8/24 candidate truncation). Return `catalogueIncomplete` when proof of exhaustion unavailable; do not claim no discounts when truncated. NONE must not call.
- For `commerce_evaluate_discount` checkout target, re-read attempt, shop, current merchant mode/selection, candidate and checkout fingerprint and reserve existing MCP execution budget. Shopify uses private-network-only Commerce-003 `POST /internal/v1/recovery/discount-proof` and Shared-005; Woo uses MCP-003’s **direct Woo REST** GET to WooCommerce-001’s native coupon-proof endpoint with authenticated read-only grant. No API-003 or generic API provider.
- Treat only strict `eligible` current provider proof with positive benefit as eligible. Distinguish ineligible vs unavailable vs incomplete vs expired/unsupported; return bounded reason codes, no codes unless confirmed and no customer PII/credentials in logs. Return timestamps/evidence to the caller; Background-008 only requests a fresh targeted lookup if proof expired or the checkout materially changed. No bulk pre-scan.
- Integration tests verify FIXED 50 selected, AI page 2+ without selected-checkbox filter, invalid merchant override, wrong shop, expired proof, Woo read-only grant, Woo credential rotation, disabled tool, provider timeout, no false absence and no MCP->API calls.

## Out of Scope

- No new database tables/columns, duplicate recovery-offer engine, unrelated UI, provider writes, or changes outside this repository and its own task report.

## Requirements

- Re-read canonical task, parent architecture, dependency task files, `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md` and launcher preparation evidence before claiming. Use launcher-resolved **dedicated mirrored parent and implementation worktrees**, not a shared checkout.
- Use the existing `@modainteract/moda-interact-shared/logging` API for new Node logs; unexpected exceptions are logged with bounded reason codes and propagated to the owning retry boundary. No silent exception swallowing, competing generic logger or secret-bearing diagnostic body.
- Never log customer PII, coupon codes, complete checkout URLs, product-image origins, provider responses, credentials or raw MCP context headers.
- Provider operations are read-only. No applying/creating coupons or mutating carts/orders except the separate customer-initiated Woo restore flow.
- Pre-production breaking cutover: **no legacy/outdated attempt parsing, old tool-version adapter, backfill or new Prisma schema**. Missing required configuration fails closed. One released Shared version and actual published Commerce capability revision must be in use; no direct sibling imports.


## Work Items

- [ ] Return the existing generic `CommerceToolResultSchema` for both tools, with only the feature `data` validated by Shared proof/catalogue schemas; preserve existing conversation inputs and tool results.
- [ ] Register built-in `commerce_get_discount_options` and `commerce_evaluate_discount` under the attempt-scoped MCP registry only; do not create Commerce Studio drafts or publication.
- [ ] Query shop-scoped existing catalogue and attempt policy with strict page limits; FIXED current selected set, AI full provider-current catalogue, NONE skipped, typed partial/incomplete budget outcomes.
- [ ] Verify checkout applicability using COMMERCE-003 private signed Shopify proof or MCP-003 direct authenticated Woo plugin native REST coupon proof; never use the hosted Moda API for Woo proof.
- [ ] Recheck current merchant mode/selection, attempt scope/fingerprint and current provider restrictions on each tool call; return Shared-005 proof only and enforce typed provider unavailable vs ineligible vs eligible.
- [ ] Test wrong shop, revoked Woo grant, expired evidence, first/second pages, concurrent policy changes, no coupon invention, no hosted API HTTP request, and `git diff --check`.

## Interfaces / Contracts

Built-in (not release-published) MCP `commerce_get_discount_options` + `commerce_evaluate_discount`, the purpose-scoped MCP-advertised input schemas and existing `CommerceToolResultSchema` envelope; Shared-005 validates feature-specific proof `data`; Shared-005 checkout proof. Woo connection from MCP-003, Shopify private route COMMERCE-003.

## Dependencies

- `ARCH-052-MCP-001` — must be Complete and architect-accepted before this task starts.
- `ARCH-052-MCP-003` — must be Complete and architect-accepted before this task starts.
- `ARCH-052-COMMERCE-003` — must be Complete and architect-accepted before this task starts.
- `ARCH-052-WOOCOMMERCE-001` — must be Complete and architect-accepted before this task starts.
- `ARCH-052-GATEWAY-001` — must be Complete and architect-accepted before this task starts.
- `ARCH-052-SHARED-003` — must be Complete and architect-accepted before this task starts.

Dependencies are authoritative in YAML; system tests are terminal validation and must never block implementation.

## Enables

- `ARCH-052-BACKGROUND-010`
- `ARCH-052-MCP-004`
- `ARCH-052-SYSTEM-TEST-001`
- `ARCH-052-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] Tool execution reads only existing catalogue/policy tables and provider proof, never a new discount table/engine.
- [ ] Both platforms have real checkout-specific provider proof; unavailable is not eligible.
- [ ] MCP makes no HTTP request to the hosted Moda API for Woo verification or product lookup.
- [ ] No manual Commerce Studio release step for system discount tools.

## Validation

- [ ] MCP registry, pagination, private proof and runtime provider integration tests.
- [ ] MCP declared unit/typecheck/lint and `git diff --check`.

Use the task repository's actual `package.json` validation scripts; do not invent unconfigured commands or claim unrun tests passed. Include `git diff --check`.

## Stop Condition

After all Work Items, Acceptance Criteria and required Validation are complete, fill the Completion Report, change the task status to `review`, return the parent task report and implementation branch to `moda_architect` and **STOP**. Do not start dependent tasks, merge, push `main`, or alter architecture/domain indexes.

## Implementation Notes

**Owning repository paths (workspace-relative; verify actual current paths at execution):**

- `moda-interact-mcp/src/runtime/service-ports.ts`
- `moda-interact-mcp/src/runtime/prisma.ts`
- `moda-interact-mcp/src/execution/policy/discount-options.ts` (new)
- `moda-interact-mcp/src/execution/policy/discount-evaluate.ts` (new)
- `moda-interact-mcp/src/execution/policy/execute.ts`
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
