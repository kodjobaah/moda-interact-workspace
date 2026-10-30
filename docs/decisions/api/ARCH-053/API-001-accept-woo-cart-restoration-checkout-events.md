---
id: ARCH-053-API-001
architecture_id: ARCH-053
title: Accept Woo checkout v3 with coupon/restoration data
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-053-SHARED-002
enables:
- ARCH-053-WOOCOMMERCE-001
created: 2026-10-29
updated: 2026-10-29
---

# ARCH-053-API-001 — Accept Woo checkout v3 with coupon/restoration data

## Architecture

Architecture ID: `ARCH-053`. Document: `docs/architecture/ARCH-053-woocommerce-checkout-recovery-links-and-cart-restoration.md`. Coordinator: `moda_architect`. **Portable canonical task: defined but not materialised**; no Git branch, worktree, commit, push, review or producer deployment claimed.

## Objective

Accept Woo checkout v3 with coupon/restoration data. One bounded outcome in `moda-interact-api` owned by `moda_api`.

## Context

The uploaded workspace snapshot is dated 2026-10-29. ARCH-052 owns dynamic discount discovery and must not be used for these checkout-URL changes. An ARCH-048 next-generation dependency exists only as a separate *portable* proposal until accepted/materialised. This task is **Pending** from the snapshot/dependency inventory, subject to fresh launcher re-gating.

## Scope

- Extend `src/woocommerce/activity/contract.ts`, `request.ts`, `producer.ts` / `redis-producer.ts` and associated tests to strictly accept a new **HTTP-only** `woo.activity.v3` CHECKOUT_UPDATED request with the same existing event identity and v2 normalized phone validation, plus optional `checkout.restoration` defined by the published Shared schema.
- Canonicalise v3 into existing `woo.activity.v1` queue-job envelope and add `checkout.restoration` iff verified; do not send v3 to Background as an unrecognised envelope. Keep `WOO_CHECKOUT_QUEUE`, existing deterministic jobId/contentDigest/correlation behaviour and 65,536-byte cap. Keep v1/v2 existing inputs accepted during transition, with missing restoration meaning unavailable.
- Extend `src/woocommerce/activity/routes.ts` error outcomes only as required; do not create a new public activity route.

## Out of Scope

No Background code, plugin coupon capture, checkout link route, database write, discounts or Woo order events changes.

No execution of Enabled tasks, unrelated cross-repository implementation, extra database objects or new generic logger.

## Requirements

- Input from WC plugin remains authenticated with `WooInstallationAuthenticator`, not a shopId supplied in body. Reject malformed coupon/attribute snapshots, unexpected fields, unknown schema versions, overlarge payload, forged tenant id, tampered digest and unchanged-event replay conflicts.
- If the shared validator/publication is not available, stop: never copy a service-local Zod restore schema. The canonical phone normalizer and marketing-consent separation remain unchanged. Do not call Woo provider from ingress or perform recovery admission synchronously.

### Mandatory workflow/security invariants

- Inspect `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, `docs/developer-task-workflow.md`, `docs/task-definition-materialization.md` and the launcher preparation evidence. Use the **dedicated, synchronized parent and implementation task worktrees**; do not operate from a shared checkout or claim a branch was pushed without evidence. Implement only the owning repository and assigned task metadata. No unrelated refactors, migrations, agent handoffs or remote pushes to `main`.
- Read the ARCH-053 parent architecture and all dependency tasks before claiming Ready. Any missing contract or incorrect owner is a blocking architect question; do not invent a local parallel schema or silently change another agent's task. System-test tasks must remain terminal.
- Never swallow unexpected errors: Node uses `@modainteract/moda-interact-shared/logging`; PHP uses the existing safe plugin diagnostics (not a competing generic Node logger). Report bounded event codes, ids and outcomes, propagate retryable failures to their owning boundary, omit tokens, full URLs, coupon codes and customer personal data from logs.
- The plugin cannot access PostgreSQL/Redis. The API cannot mutate merchant WordPress cart sessions. Background cannot directly call an unverified merchant endpoint to mint URLs. Do not enable Woo production WhatsApp sending, relax final consent/STOP/order gates, or add cross-generation outreach caps/cooldowns.

## Work Items

- [ ] Accept and project `woo.activity.v3` while preserving v1/v2 and existing queue contract.
- [ ] Include complete original coupon codes and supported/unsupported restoration evidence in queue serialization/digest.
- [ ] Test version/identity/phone/tenant/limit/replay errors and JSON canonicalization.

## Interfaces / Contracts

Producer HTTP: `POST /v1/woocommerce/activity` with `schemaVersion: 'woo.activity.v3'`, existing `eventType:'CHECKOUT_UPDATED'`, eventId, checkoutKey, occurredAt and `checkout.restoration` per Shared. Consumer queue: `woo.activity.v1` with optional extension. No new shared phone-normalization library.

## Dependencies

- `ARCH-053-SHARED-002` (must be architect-accepted Complete)

## Enables

- `ARCH-053-WOOCOMMERCE-001`

## Acceptance Criteria

- [ ] Accept and project `woo.activity.v3` while preserving v1/v2 and existing queue contract.
- [ ] Include complete original coupon codes and supported/unsupported restoration evidence in queue serialization/digest.
- [ ] Test version/identity/phone/tenant/limit/replay errors and JSON canonicalization.
- [ ] No regression in tenant isolation, historical generation preservation, valid shopper cart or consent/STOP/terminal order guards.
- [ ] Tests demonstrate invalid/stale/replayed and unexpected errors do not produce silent success or malformed URLs.
- [ ] No change outside assigned domain repository code plus owned task Completion Report; no ARCH-052 work.

## Validation

- [ ] `npm run test:arch035-woo-activity:unit` plus new v3 focused tests
- [ ] `npm run test:arch035-woo-activity:redis` if isolated Redis available
- [ ] `npm run typecheck`, `npm run lint`; `git diff --check`

## Stop Condition

When Work Items, Acceptance Criteria and required Validation are complete, update ONLY this task's authorised execution metadata, checklists and Completion Report, set `status: review` and return to `moda_architect`; **STOP**. Do not begin Enables, merge task branches, push `main` or change Architect Review yourself.

## Implementation Notes

Producer runtime deployment is gated on Background-001 accepting the additive queue extension; definition dependencies cover source availability while architect rollout order covers safe producer activation.

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
