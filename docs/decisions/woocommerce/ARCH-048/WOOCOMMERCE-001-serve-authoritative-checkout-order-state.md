---
id: ARCH-048-WOOCOMMERCE-001
architecture_id: ARCH-048
title: Serve bounded authoritative Woo checkout and order state
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 25
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-035-WOOCOMMERCE-007
  - ARCH-035-WOOCOMMERCE-008
enables:
  - ARCH-048-API-001
created: 2026-10-23
updated: 2026-10-23
---

# ARCH-048-WOOCOMMERCE-001: Serve bounded authoritative Woo checkout and order state

## Architecture

- Architecture ID: `ARCH-048`.
- Canonical architecture: `docs/architecture/ARCH-048-woocommerce-checkout-recovery-pipeline.md`.
- Coordinator: `moda_architect`.
- **Lifecycle:** portable review definition based on the 23 October 2026 workspace snapshot, **defined but not materialised**. No branch/worktree, commit, claim, implementation or acceptance is implied. Re-gate against the developer's canonical workspace before execution.

## Objective

Expose one authenticated, read-only, bounded Woo-owned current-state operation that resolves the existing checkout key to a live guest/customer cart where safely possible and to any linked Woo order, without inventing a new checkout database.

## Context

`CheckoutKey::current()` stores `moda_interact_checkout_key` in a Woo session and copies it as `_moda_checkout_key` on the Woo order. It is not a Woo session ID, and standard Woo product REST reads cannot retrieve a live guest basket with it. The original checkout/order event producers remain unchanged.

## Scope

- Use supported Woo/WordPress interfaces to resolve a shop-local checkoutKey to the **same current guest/customer session** and, where present, the order with matching `_moda_checkout_key` (HPOS-compatible CRUD; avoid postmeta/SQL assumptions).
- If a checkoutKey-to-session reverse association is necessary, create only a bounded, expiring plugin-local association tied to the observed real Woo session; never create another Moda table, a global cart enumeration route or an indefinitely retained customer dataset.
- Provide a narrow read-only plugin endpoint for the already authorised hosted API; return a versioned normalized state projection with checkout identity, observation time, basket empty/nonempty and currency/total/item bounds, and matched order ID/status/payment evidence.
- Make `paid`, `cancelled`, `empty`, `not-found`, `expired`, `unavailable` and `ambiguous` meaningfully distinct; an unknown or expired guest session must not be reported as safely abandoned.

## Out of Scope

- Checkout event publication changes (WOOCOMMERCE-002 owns empty-cart publication).
- Recovery jobs, new Moda tables, billing, consent decisions, WhatsApp, or merchant UI.
- Arbitrary access to other shopper carts, order enumeration or a raw URL proxy.
- No `docs/decisions/**/_index.md` updates before the developer explicitly ends architecture reconciliation.

## Requirements

- Server-side installation/provider authentication must be shown against the existing read-authorisation boundary; never trust a browser-supplied shop ID or expose session identifiers.
- A read grant that authorises product reads is not assumed to authorise a custom route until explicitly validated. If existing Woo/WP auth cannot protect this endpoint, stop and report the smallest required authentication contract to the architect.
- Guest and registered customers, Classic and Blocks, session expiration and HPOS orders must all have explicit behaviours. No use of unsafe session deserialisation or unbounded Woo session-table scans.
- `ORDER_PLACED`/unpaid cannot be conflated with paid; checkout/order identity mismatch or multiple matches returns an ambiguous denial. Protect raw PII and credentials from logs and error responses.

## Work Items

- [ ] Implement checkoutKey/current Woo session correlation with bounded lifecycle/expiry and cleanup.
- [ ] Implement HPOS-safe verified order association and explicit payment/cancelled classification.
- [ ] Expose narrow authenticated projection; add Classic/Blocks, guest/customer and session/credential/expiry integration tests.

## Interfaces / Contracts

- Input: validated opaque `checkoutKey` and optionally already-linked `orderId` under the currently authenticated installation. No arbitrary WordPress session identifier or URL supplied by a caller.
- Output: bounded schema-versioned current observation; exact checkout key and verified order correlation, basket snapshot when available and explicit terminal/error outcomes. API-001 will own hosted normalization and private transport.
- Retain existing `woo.activity.v1` public activity route and `_moda_checkout_key` order metadata.

## Dependencies

- `ARCH-035-WOOCOMMERCE-007`
- `ARCH-035-WOOCOMMERCE-008`

## Enables

- `ARCH-048-API-001`

## Acceptance Criteria

- [ ] Live checkout lookup maps the same shopper session to the original key; wrong shop/key and unrelated order data never leak.
- [ ] Payment/cancellation/empty basket and session expiry cannot be misreported as recoverable.
- [ ] No unsupported direct session ID guessing, Woo table scans or new Moda persistence.
- [ ] Classic/Blocks, HPOS, duplicate key and authentication failure tests pass.

## Validation

- [ ] Focused PHPUnit tests and WordPress/LocalWP integration for guest/authenticated Classic + Blocks, HPOS, expiry, cancelled/paid/unpaid cases.
- [ ] Plugin PHP lint/build and relevant existing checkout/order regressions, `git diff --check`.

## Stop Condition

After the specified work, acceptance criteria and required validation are satisfied, record launcher-resolved **dedicated** parent/implementation task worktrees, start-of-attempt synchronization and recursive submodule evidence in the Completion Report. Change task state to `review`, return to `moda_architect` and **STOP**. Do not start an enabled task. The repo agent must not mark its own task Complete.

## Implementation Notes

A proof-of-capability is required here: if official Woo storage does not permit a safe live session lookup by the key, return the gap to `moda_architect` before claiming Shopify-equivalent parity. A provider error must not become a fabricated current-cart snapshot.

Respect `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, and `docs/developer-task-workflow.md`. Prepare through `/moda-task` or `/moda_developer_create` in the developer's actual workspace. Use service-owned existing runtime facilities; reuse `@modainteract/moda-interact-shared/logging` for new generic Node application logs, not an alternate logger. Follow the actual owning repository's declared checks; no unrelated refactors or cross-repository edits.

## Completion Report

### Status

Not Started — portable task definition; implementation execution not claimed.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run. Required validation is listed above for the future assigned executor.

### Deviations

None.

### Assumptions

The uploaded snapshot is not the current remote/branch authority. Dependencies and task paths must be rechecked on materialisation.

### Unresolved Issues

None recorded at task-definition stage beyond the review gates in the parent architecture.

### Architectural Concerns

Escalate missing cross-repository contracts, Woo guest-session read impossibility, authentication or deployment requirements to `moda_architect` before inventing a workaround.

## Architect Review

### Review Status

Pending — not yet reviewed as an implementation.

### Review Notes

Awaiting future repository implementation and evidence.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Not yet assessed.

### Follow-up

None.
