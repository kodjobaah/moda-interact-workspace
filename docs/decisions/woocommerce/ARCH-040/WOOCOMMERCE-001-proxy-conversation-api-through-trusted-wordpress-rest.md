---
id: ARCH-040-WOOCOMMERCE-001
architecture_id: ARCH-040
title: Proxy conversation API through trusted WordPress REST
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 40
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-040-API-002
  - ARCH-040-API-003
  - ARCH-040-API-004
  - ARCH-035-API-013
enables:
  - ARCH-040-WOOCOMMERCE-002
created: 2026-10-14
updated: 2026-10-14
---

# ARCH-040-WOOCOMMERCE-001 — Proxy conversation API through trusted WordPress REST

## Architecture

Initiative: `ARCH-040`. Architecture document: `docs/architecture/ARCH-040-merchant-customer-conversations-human-handover.md`. Coordinator: `moda_architect`. **Portable definition only; defined but not materialised, no branch/commit/worktree.**

## Objective

Expose secure WordPress-side customer inbox/hand-over/reply facade to the hosted API without direct browser access.

## Context

The approved direction is one existing `Conversation` for one `CheckoutRecovery` generation, with author-distinguished messages and one recovery-wide post-24-hour follow-up shared between human and AI. This task changes only the assigned repository boundary.

## Scope

- Implement the bounded woocommerce capability described by the objective.
- Add focused tests and evidence for that capability.

## Out of Scope

- No creation of a second Conversation for human chat or a recovery follow-up.
- No independent human-only follow-up allowance or duplicate usage counter.
- No updates to docs/decisions/**/_index.md pending explicit user confirmation.
- No opportunistic cross-repository work or additional task execution.

## Requirements

- Retain existing two-stage WordPress navigation: `WooCommerce > Moda Interact` entry, then active top-level Moda Interact submenu. Do not move or duplicate navigation.
- For **each** WordPress REST browser request require existing logged-in capability `manage_woocommerce` and a valid REST nonce; continue using current installed/connected Moda credential on PHP server side only. No new staff roles or identification/assignment.
- PHP server proxy calls only the Woo-specific hosted routes: `GET /v1/merchant/conversations`, `GET /v1/merchant/conversations/{id}`, `GET /v1/merchant/conversations/{id}/messages`, `POST /v1/merchant/conversations/{id}/control`, `POST /v1/merchant/conversations/{id}/messages`, and `GET /v1/merchant/conversations/{id}/send-commands/{commandId}`.
- Forward only allowlisted cursor/limit and validated command payload fields. Maintain idempotency keys/expected revisions unchanged end to end; do not invent browser shopId/staff IDs or permit credentials/tokens in the JS bundle.
- Map hosted API error codes/statuses faithfully to WordPress REST so UI can distinguish 202 accepted, 200 replay, 400 bad request, 401 disconnected/unauthorized, 404 foreign/not found, 409 stale/window/follow-up errors, and 5xx transport/provider failures.
- Bound retries/timeouts and sanitize unexpected responses. A disconnected/rotated installation fails closed; PHP never accesses Moda PostgreSQL/Redis or calls Meta directly.
- Reuse ARCH-035 recovery detail shell/read contracts where compatible. Preserve the platform support inbox separately; no UI network credential exposure.

## Work Items

- [ ] Add WordPress REST facades for Woo-hosted inbox, detail and message pages, preserving bounded query params.
- [ ] Add WordPress REST facades for control POST, human send POST and send-command status GET with exact upstream errors.
- [ ] Use existing WordPress nonce/capability + server-only installation bearer/header mechanism for every call; handle disconnect/rotation.
- [ ] Add PHP route tests and mock hosted API contract/timeout/replay/tenant isolation cases.

## Interfaces / Contracts

The *only* hosted API callers for ARCH-040 are WooCommerce PHP server requests. Exact upstream paths/DTOs/errors are defined by `API-002/003/004`; WordPress REST exposes safe equivalents to authenticated WP-admin JavaScript. No new Shopify assertion or browser-to-hosted-API direct call. Neither Woo plugin nor browser accesses Moda database or Meta credentials.

## Dependencies

- ARCH-040-API-002
- ARCH-040-API-003
- ARCH-040-API-004
- ARCH-035-API-013

## Enables

- ARCH-040-WOOCOMMERCE-002

## Acceptance Criteria

- [ ] Tampered nonce/capability/cross-shop and disconnected installation cannot send.
- [ ] Browser sees only WordPress REST nonce, never Moda installation bearer.
- [ ] Hosted API detail reads are reused, not replaced with fake Woo records.

## Validation

- [ ] WordPress REST/PHPUnit security tests
- [ ] Hosted integration contract tests
- [ ] git diff --check; review canonical task-worktree and dependency-sync evidence

## Stop Condition

After only this task’s Work Items, Acceptance Criteria and Validation are complete, record implementation evidence, set status to review and return control to moda_architect. Do not begin dependent tasks.

## Implementation Notes

Use `scripts/start-agent-task.py --prepare` in the actual developer workspace when this definition is materialised; keep matching parent and implementation task branches in separate launcher-resolved worktrees, as documented in workspace policy. Check actual repository scripts before validation. Structured logging must use the published shared logger; no credentials or full customer content in logs. Preserve current production compatibility unless architect specifically establishes a safe pre-production breaking rollout.

## Completion Report

### Status
Not Started

### Files Changed
None.

### Work Completed
None.

### Validation Results
Not run.

### Deviations
None.

### Assumptions
The architecture is proposed; implementation starts only after agreed/materialised task definition.

### Unresolved Issues
None recorded at definition time.

### Architectural Concerns
Return newly discovered contract or ownership gaps to moda_architect.

## Architect Review

### Review Status
Pending

### Review Notes
Not reviewed.

### Reviewed Files
None.

### Validation Reviewed
None.

### Architecture Conformance
Pending.

### Follow-up
None.
