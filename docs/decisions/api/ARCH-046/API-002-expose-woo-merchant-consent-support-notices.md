---
id: ARCH-046-API-002
architecture_id: ARCH-046
title: Expose Woo merchant Support system notices read-only
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: superseded
priority: 32
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables: []
created: 2026-10-20
updated: 2026-10-21
---

# Expose Woo merchant Support system notices read-only

## Architecture

Architecture ID: `ARCH-046`

Architecture document: `docs/architecture/ARCH-046-woocommerce-whatsapp-consent-gated-recovery.md`

Coordinator: `moda_architect`

**Lifecycle:** portable definition from 2026-10-20 snapshot; not materialised, claimed, committed, implemented or architect-accepted. Status means definition eligibility only.

## 21 October 2026 architectural supersession

**Not executable.** Following approval of Shopify-equivalent *two-way* Woo Support, this narrowly scoped read-only Support API is superseded by `ARCH-035-API-020`. Its source body and original acceptance criteria are historical only; there has been no implementation, claim, publication or acceptance for this task. Consent-related SYSTEM messages will be read in the same Support thread through the full implementation. Do not start or materialise this task. ARCH-046's other consent tasks and separately blocked recovery-engine gate remain unchanged.

## Objective

Provide a narrow, paginated, installation-authenticated read-only view of existing merchant system Support messages for the Woo Support screen.

## Context

The Woo Support screen currently has `read:false`, and the hosted Woo API has no approved merchant Support read route. Messages exist in `support.MerchantSupportMessage` with shop-unique thread and deterministic `sourceKey`.

## Scope

- Implement authenticated `GET /v1/merchant/support-notices` (path pinned by API owner), returning tenant-owned `SYSTEM` notices, pagination and bounded display fields in chronological order.
- Derive shop from installation, verify active Woo platform and grant; use existing Support schema, not a new message table.
- Exclude cross-merchant/support-admin messages outside merchant-safe projection and sensitive metadata; stable DTO/explicit error semantics for WordPress proxy.

## Out of Scope

- No merchant Support send, platform admin reply, mark-read or support ticket workflow.
- No Shopify session authentication reuse and no WordPress plugin/React edits.
- Do not email/WhatsApp the merchant or create a new notification queue.

## Requirements

- No client-supplied shopId; strictly bounded cursor/page/pageSize and no cross-tenant leakage.
- Preserve message source key deduplication, safe normalised text and existing translation/display fallback.
- 401/403/cross-shop fail closed and do not leak existence of other tenants' messages.

## Work Items

- [ ] Define narrow Support notice read DTO and versioned route.
- [ ] Add integration tests for shop isolation, empty/large threads, inactive/rotated installation.
- [ ] Wire API composition and document Woo proxy contract.

## Interfaces / Contracts

API-owned read-only HTTP route; consumer WOOCOMMERCE-004. Data source existing `MerchantSupportThread`/`MerchantSupportMessage`, no new runtime Shared contract.

## Dependencies

None

## Enables

- `ARCH-046-WOOCOMMERCE-004`
- `ARCH-046-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] Tenant A cannot read B's notices, even when passing B's identifiers.
- [ ] Correct pagination, ordering and safe body projection; no write endpoints added.
- [ ] Woo installation auth and revoked credential behaviour verified.

## Validation

- [ ] Focused API route/read DB tests plus repository-declared typecheck/build and `git diff --check`.

## Stop Condition

After completing **only** the defined Work Items, Acceptance Criteria and required Validation, record launcher-resolved dedicated parent/implementation worktrees, their physical isolation and start-of-attempt synchronization evidence in the Completion Report. Change task to `review`, return control to `moda_architect`, and **STOP**. Do not start enabled tasks. A `blocked` task must remain blocked until the architect verifies and records the external missing recovery dependency and explicitly makes it Ready.

## Implementation Notes

Expose only what is needed for the visible system-notice feature; do not reconstruct an entire Support backend.

Before any implementation, use `/moda-task` deterministic preparation against the **developer's actual** primary workspace, read the latest task/Architect Review, the parent architecture, relevant agent instructions, and the repository's real `package.json` scripts. Do not invent environment variables or claim a completed checkout/recovery source from the snapshot. Do not modify another repository, architecture-wide docs or `docs/decisions/**/_index.md` in a repository task. Use `@modainteract/moda-interact-shared/logging` for Node server diagnostics; PHP uses WordPress-specific safe diagnostics. Preserve official user/merchant i18n and tenant boundaries.

## Completion Report

### Status

Not Started — portable, not materialised.

### Files Changed

None — no runtime implementation in this documentation patch.

### Work Completed

None.

### Validation Results

Not run by a repository agent; no developer worktree/remote access is available from this snapshot.

### Deviations

None.

### Assumptions

Source is the supplied 2026-10-20 snapshot, not necessarily latest developer worktree. Versioned APIs/schema and future Woo recovery capability must be verified when eligible. Consent has no Moda-imposed waiting/expiry period. Recheck the current customer-phone permission and independently applicable checkout validity; do not invent a retention deadline.

### Unresolved Issues

None recorded at definition time; raise actual missing cross-repository contract/rollout dependencies to moda_architect before scope drift.

### Architectural Concerns

None recorded beyond explicit context and gates.

## Architect Review

### Review Status

Pending — no implementation reviewed or accepted.

### Review Notes

None.

### Reviewed Files

None — portable definition only.

### Validation Reviewed

None.

### Architecture Conformance

Not assessed.

### Follow-up

None.
