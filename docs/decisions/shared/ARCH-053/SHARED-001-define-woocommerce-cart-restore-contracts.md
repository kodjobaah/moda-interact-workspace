---
id: ARCH-053-SHARED-001
architecture_id: ARCH-053
title: Define canonical Woo restoration wire schemas
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables:
- ARCH-053-SHARED-002
created: 2026-10-29
updated: 2026-10-29
---

# ARCH-053-SHARED-001 — Define canonical Woo restoration wire schemas

## Architecture

Architecture ID: `ARCH-053`. Document: `docs/architecture/ARCH-053-woocommerce-checkout-recovery-links-and-cart-restoration.md`. Coordinator: `moda_architect`. **Portable canonical task: defined but not materialised**; no Git branch, worktree, commit, push, review or producer deployment claimed.

## Objective

Define canonical Woo restoration wire schemas. One bounded outcome in `moda-interact-shared` owned by `moda_shared`.

## Context

The uploaded workspace snapshot is dated 2026-10-29. ARCH-052 owns dynamic discount discovery and must not be used for these checkout-URL changes. An ARCH-048 next-generation dependency exists only as a separate *portable* proposal until accepted/materialised. This task is **Ready** from the snapshot/dependency inventory, subject to fresh launcher re-gating.

## Scope

- Create a browser-safe published subpath in `moda-interact-shared/src/woocommerce/` for `WooCartRestoreSnapshotV1Schema`, `WooCartRestoreSnapshotV1`, `WooRestoreResolveRequestV1Schema`, `WooRestoreResolveResponseV1Schema`; update `package.json` exports/build entrypoints and focused tests.
- Define snapshot: `{schemaVersion:'woo.cart-restore.v1',kind:'supported',appliedCouponCodes:string[],lines:[...1..50]}` or `{schemaVersion:'woo.cart-restore.v1',kind:'unsupported',reason:<enum>,appliedCouponCodes:string[]}`. Each supported line: integer decimal productId >0, quantity 1..100000, optional integer variationId >0, optional `attributes` map (max 10 entries, keys 1..80, values 1..200 safe Unicode); coupon list max 10, codes 1..128, no control characters; reason enum `ITEMS_UNAVAILABLE|UNSUPPORTED_PRODUCT_TYPE|CUSTOM_CART_ITEM_DATA|INVALID_VARIATION|COUPONS_UNAVAILABLE|LIMIT_EXCEEDED`.
- Add v3 HTTP checkout extension type / normalization helpers representing `checkout.restoration?` without duplicating the existing Woo contact/identity fields. Strict object validation; no permissive passthrough, URL construction, HMAC secret or WC-specific price calculation.
- Document JSON serialization/golden fixture in `src/woocommerce/__fixtures__/woo-restore-v1.json` so Woo PHP and API/Background tests exercise the same canonical wire format.

## Out of Scope

No Woo plugin/API/Background implementation; no package publication in this task; no ARCH-052 discount selection contracts.

No execution of Enabled tasks, unrelated cross-repository implementation, extra database objects or new generic logger.

## Requirements

- A supported snapshot MUST have every exact line and the complete coupon list, not a partially captured basket; unsupported MUST have no lines. Reject missing line IDs, duplicate/ambiguous attribute keys, extra fields, overlong coupon codes and PII inside restoration. Empty coupon array means verified none; absent restoration means unknown and cannot support a link.
- Resolver request `{schemaVersion:'woo.restore.resolve.v1', recoveryId:boundedId,token:43-base64url}`; positive response `{schemaVersion, status:'eligible', recoveryId,checkoutKey,snapshot:<supported>}`; unavailable response uses a stable no-detail error outside the schema; no shop/customer-provided identity or raw URL in API body.
- Schema only handles shape; WooCommerce itself owns product/variation availability, currency/price and coupon validity. Shared must not import Prisma, WordPress or other service code.

### Mandatory workflow/security invariants

- Inspect `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, `docs/developer-task-workflow.md`, `docs/task-definition-materialization.md` and the launcher preparation evidence. Use the **dedicated, synchronized parent and implementation task worktrees**; do not operate from a shared checkout or claim a branch was pushed without evidence. Implement only the owning repository and assigned task metadata. No unrelated refactors, migrations, agent handoffs or remote pushes to `main`.
- Read the ARCH-053 parent architecture and all dependency tasks before claiming Ready. Any missing contract or incorrect owner is a blocking architect question; do not invent a local parallel schema or silently change another agent's task. System-test tasks must remain terminal.
- Never swallow unexpected errors: Node uses `@modainteract/moda-interact-shared/logging`; PHP uses the existing safe plugin diagnostics (not a competing generic Node logger). Report bounded event codes, ids and outcomes, propagate retryable failures to their owning boundary, omit tokens, full URLs, coupon codes and customer personal data from logs.
- The plugin cannot access PostgreSQL/Redis. The API cannot mutate merchant WordPress cart sessions. Background cannot directly call an unverified merchant endpoint to mint URLs. Do not enable Woo production WhatsApp sending, relax final consent/STOP/order gates, or add cross-generation outreach caps/cooldowns.

## Work Items

- [ ] Publish strict versioned snapshots and request/response schemas via package export.
- [ ] Add deterministic positive/negative fixtures including multiple coupon codes, attributes, unsupported basket and malicious/oversized payloads.
- [ ] Confirm importing package from API and Background without browser-unsafe imports.

## Interfaces / Contracts

Owner: `moda_shared`; consumers: API `ARCH-053-API-001` and `API-002`, Background `ARCH-053-BACKGROUND-001/002`, Woo PHP via exact golden vectors (PHP cannot import the Node package). API v3 transport wraps the schema; existing `woo.activity.v1` queue envelope can carry optional verified restoration.

## Dependencies

None — independently executable after materialisation / launcher gate.

## Enables

- `ARCH-053-SHARED-002`

## Acceptance Criteria

- [ ] Publish strict versioned snapshots and request/response schemas via package export.
- [ ] Add deterministic positive/negative fixtures including multiple coupon codes, attributes, unsupported basket and malicious/oversized payloads.
- [ ] Confirm importing package from API and Background without browser-unsafe imports.
- [ ] No regression in tenant isolation, historical generation preservation, valid shopper cart or consent/STOP/terminal order guards.
- [ ] Tests demonstrate invalid/stale/replayed and unexpected errors do not produce silent success or malformed URLs.
- [ ] No change outside assigned domain repository code plus owned task Completion Report; no ARCH-052 work.

## Validation

- [ ] Shared `package.json` declared unit tests
- [ ] Shared package build/typecheck/export smoke
- [ ] Golden fixture round-trip/negative vectors; `git diff --check`

## Stop Condition

When Work Items, Acceptance Criteria and required Validation are complete, update ONLY this task's authorised execution metadata, checklists and Completion Report, set `status: review` and return to `moda_architect`; **STOP**. Do not begin Enables, merge task branches, push `main` or change Architect Review yourself.

## Implementation Notes

Inspect existing Shared entrypoint layout and use its established export conventions. If existing Shared already has a suitable Woo subpath, extend it rather than creating a competing path. Keep crypto Node-only if any reusable crypto becomes needed (not required by this contract).

## Completion Report

### Status

Not Started

### Files Changed

None — portable task definition only.

### Work Completed

Not Started.

### Validation Results

Not Run — no implementation claimed.

### Deviations

None.

### Assumptions

Design based on uploaded 2026-10-29 source snapshot; re-check source and prior task acceptance before implementation.

### Unresolved Issues

None asserted as executed; dependencies must be materialised/accepted.

### Architectural Concerns

Return any cross-service schema/provider/transaction concern to `moda_architect` before improvising.

## Architect Review

### Review Status

Pending

### Review Notes

Not Reviewed — task not executed.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

To be assessed after implementation.

### Follow-up

None.
