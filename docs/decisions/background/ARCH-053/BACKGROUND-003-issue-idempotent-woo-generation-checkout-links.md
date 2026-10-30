---
id: ARCH-053-BACKGROUND-003
architecture_id: ARCH-053
title: Issue immutable, safe generation-specific Woo resume URLs
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 50
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-053-BACKGROUND-002
- ARCH-048-BACKGROUND-011
enables:
- ARCH-053-SYSTEM-TEST-001
- ARCH-053-SYSTEM-TEST-002
created: 2026-10-29
updated: 2026-10-30
---

# ARCH-053-BACKGROUND-003 — Issue immutable, safe generation-specific Woo resume URLs

## Architecture

Architecture ID: `ARCH-053`. Document: `docs/architecture/ARCH-053-woocommerce-checkout-recovery-links-and-cart-restoration.md`. Coordinator: `moda_architect`. **Portable canonical task: defined but not materialised**; no Git branch, worktree, commit, push, review or producer deployment claimed.

## Objective

Issue immutable, safe generation-specific Woo resume URLs. One bounded outcome in `moda-interact-background` owned by `moda_background`.

## Context

The inspected snapshot is dated 2026-10-30 07:59. ARCH-052 owns dynamic discount discovery and is not a checkout-URL implementation domain. ARCH-048-BACKGROUND-007..011 task files are present, but none has been accepted Complete in this snapshot (007 Ready, 008–011 Pending). This task is **Pending** from the snapshot/dependency inventory, subject to fresh launcher re-gating.

## Scope

- Modify `src/services/woocommerce-recovery/woo-recovery-admission.service.ts` only for transactional URL creation and `woo-recovery-admission-evidence.ts` or a narrowly owned `woo-recovery-link-issuer.ts` helper; update Woo Background admission/outreach/template regression tests. Consume generation-aware admission already accepted under ARCH-048-BACKGROUND-011; do not reimplement the new generation lifecycle.
- For a **supported, fully persisted** `wooRestoreSnapshot`, resolve active `WooCommerceInstallation.canonicalSiteUrl` from the authoritative shop. Validate HTTPS/public site and hostname equality with `Shop.domain` (support home subpath). Generate 32 cryptographically random bytes to base64url 43-character token and construct `<canonicalSiteUrl>/?moda_interact_resume=1&r=<new-recovery-id>&t=<token>`; insert row with `CheckoutRecovery.checkoutUrl` atomically as part of the existing recovery admission transaction (create row, then update URL within same tx, if generated recovery ID required).
- For missing/unsupported snapshot, invalid canonical site, revoked installation or host mismatch, store `checkoutUrl:null` and record bounded omission reason; never fall back to bare `wc_get_checkout_url()` or product-ID `/checkout-link/`. If template requires URL, obey established no-link fallback or no-send rather than sending misleading CTA.
- Do not regenerate token/URL for duplicate delivery, already-created generation or resend/retry: return existing immutable link; one unique URL per recovery ID/generation. Confirm existing `checkout.url` templating and `trustedHttpsUrl` host gate still accepts the verified URL, and that Meta preparation/redaction does not emit token in logs. Do not activate Woo production sends.

## Out of Scope

No schema migration, Woo WordPress endpoint, API resolver, discount discovery or modification to ARCH-048-BACKGROUND-011 generation orchestration.

No execution of Enabled tasks, unrelated cross-repository implementation, extra database objects or new generic logger.

## Requirements

- Issuance does not depend on ARCH-052 discount discovery, private Woo provider call, WP transient or extra HMAC key. No network/Redis inside admission transaction; entropy failure is retryable and must not admit a partial row with a phantom URL.
- A new generation receives a different URL and fresh snapshot; the old link remains stored historically but API resolver refuses it immediately once old generation is terminal/superseded. New arrivals can send their independently eligible initial outreach under ARCH-048.
- Ensure 7-day checkout freshness for URL resolution is consistent with existing Background template freshness. Historical confirmed billing/sends are never altered by link creation.

### Mandatory workflow/security invariants

- Inspect `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, `docs/developer-task-workflow.md`, `docs/task-definition-materialization.md` and the launcher preparation evidence. Use the **dedicated, synchronized parent and implementation task worktrees**; do not operate from a shared checkout or claim a branch was pushed without evidence. Implement only the owning repository and assigned task metadata. No unrelated refactors, migrations, agent handoffs or remote pushes to `main`.
- Read the ARCH-053 parent architecture and all dependency tasks before claiming Ready. Any missing contract or incorrect owner is a blocking architect question; do not invent a local parallel schema or silently change another agent's task. System-test tasks must remain terminal.
- Never swallow unexpected errors: Node uses `@modainteract/moda-interact-shared/logging`; PHP uses the existing safe plugin diagnostics (not a competing generic Node logger). Report bounded event codes, ids and outcomes, propagate retryable failures to their owning boundary, omit tokens, full URLs, coupon codes and customer personal data from logs.
- The plugin cannot access PostgreSQL/Redis. The API cannot mutate merchant WordPress cart sessions. Background cannot directly call an unverified merchant endpoint to mint URLs. Do not enable Woo production WhatsApp sending, relax final consent/STOP/order gates, or add cross-generation outreach caps/cooldowns.

## Work Items

- [ ] Generate bounded deterministic URL **format** with random per-generation token and canonical site URL.
- [ ] Write exactly one URL in generation admission transaction, safe retry and uniqueness conflict handling.
- [ ] Test supported/unrestorable, subpath, host mismatch, generation 1→2, duplicate admission, token uniqueness, template bind and zero token logging.

## Interfaces / Contracts

Recovery DB: `CheckoutRecovery.checkoutUrl String?` (existing) and new `wooRestoreSnapshot`. URL params are `moda_interact_resume=1&r=<recoveryId>&t=<43-char-token>`, matching API-002 and WOOCOMMERCE-002. No raw coupon/product/identity data in URL. Confirm every consumer uses stored URL rather than generating another from `wc_get_checkout_url()`.

## Dependencies

- `ARCH-053-BACKGROUND-002` (must be architect-accepted Complete)
- `ARCH-048-BACKGROUND-011` (must be architect-accepted Complete)

## Enables

- `ARCH-053-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Generate bounded deterministic URL **format** with random per-generation token and canonical site URL.
- [ ] Write exactly one URL in generation admission transaction, safe retry and uniqueness conflict handling.
- [ ] Test supported/unrestorable, subpath, host mismatch, generation 1→2, duplicate admission, token uniqueness, template bind and zero token logging.
- [ ] No regression in tenant isolation, historical generation preservation, valid shopper cart or consent/STOP/terminal order guards.
- [ ] Tests demonstrate invalid/stale/replayed and unexpected errors do not produce silent success or malformed URLs.
- [ ] No change outside assigned domain repository code plus owned task Completion Report; no ARCH-052 work.

## Validation

- [ ] Background admission transaction and URL issuer unit tests, mature job retry and two generation integration
- [ ] Template binding/host validation and secret-redaction regression tests
- [ ] Package declared typecheck/lint and `git diff --check`

## Stop Condition

When Work Items, Acceptance Criteria and required Validation are complete, update ONLY this task's authorised execution metadata, checklists and Completion Report, set `status: review` and return to `moda_architect`; **STOP**. Do not begin Enables, merge task branches, push `main` or change Architect Review yourself.

## Implementation Notes

Dependency `ARCH-048-BACKGROUND-011` is **defined and Pending in this snapshot**, not Complete: do not mark this Ready until it is architect-accepted and the launcher confirms readiness. Confirm actual field/method names at that accepted commit; stop for architect if conflict.

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

Design reconciled against uploaded 2026-10-30 07:59 source snapshot; re-check source and prior task acceptance before implementation.

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
