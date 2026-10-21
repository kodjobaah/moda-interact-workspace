---
id: ARCH-045-SHOPIFY-002
architecture_id: ARCH-045
title: Explain Shopify WhatsApp recovery consent to merchants
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 36
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables:
  - ARCH-045-SYSTEM-TEST-001
created: 2026-10-20
updated: 2026-10-21
---
# Explain Shopify WhatsApp recovery consent to merchants

## Architecture

Architecture ID: `ARCH-045`
Architecture document: `docs/architecture/ARCH-045-shopify-whatsapp-consent-gated-recovery.md`
Coordinator: `moda_architect`
**Lifecycle:** portable definition, **not** materialised in a developer task worktree or committed/pushed; no execution claim exists.

## Objective

Explain Shopify's native WhatsApp recovery opt-in and accurately communicate why an unconsented checkout did not create a recovery.

## Context

Merchants will receive a checkout-keyed Support notice once BACKGROUND-002 is implemented, not a blocked `CheckoutRecovery`. Consent is held by Shopify and has no Moda-imposed 72-hour expiry. Only a checkout that can be safely rechecked while eligible may produce a recovery after later opt-in.

## Scope

- Update existing Shopify merchant guidance for native WhatsApp marketing opt-in via checkout/Forms and the distinction from tracking-cookie consent.
- Explain no verified consent means **no CheckoutRecovery**, no customer message/charge and a checkout-keyed merchant Support notice when ordinary reconciliation encounters the problem.
- Explain later opt-in updates the customer phone preference but does **not** immediately scan or revive old abandoned checkouts; only a later **normal checkout reconciliation**, if any, may encounter the still-eligible checkout and create a recovery. No consent expiry clock or merchant bypass.

## Out of Scope

- No storefront CMP/banner/app block/pixel, Shopify consent write or new merchant manual send bypass.
- No claim that customer consent expires after 72 hours or that a previously skipped checkout is guaranteed to be found later.

## Requirements

- [ ] Text refers to a checkout that cannot be recovered yet, **not** a paused/expiring `DETECTED` recovery.
- [ ] Consent collection is native Shopify; no Customer Privacy API tracking consent is repurposed.

- Merchant instructions state that native WhatsApp marketing permission is distinct from Shopify Customer Privacy tracking, that identity may be missing for guest checkouts, and that a later grant updates current permission but does not itself re-run a discarded candidate. Include off-channel STOP handling and data privacy information without suggesting a second Shopify cookie-consent banner.

## Work Items

- [ ] Update copy in existing merchant Recovery Settings/Support UX and required locale handling.
- [ ] Verify checkout-keyed notice wording with denied and verification-unavailable cases.

## Interfaces / Contracts

Existing merchant Recovery Settings and Support; depends on ARCH-045-BACKGROUND-002 notice semantics. No new API.

## Dependencies

None

## Enables

- `ARCH-045-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Merchant guidance truthfully separates consent-change sync from normal checkout re-evaluation and no-contact/no-charge outcomes.
- [ ] No guarantee of automatic recovery on opt-in alone, no tracking-consent confusion or artificial 72-hour timer.

- [ ] Copy neither promises recovery on opt-in alone nor asks a merchant to bypass missing permission; merchant no-contact can be recorded via the authorised merchant workflow.

## Validation

- [ ] Existing Shopify merchant UI tests/localisation and focused Support notice assertion; `git diff --check`.

## Stop Condition

After completing only the defined Work Items, Acceptance Criteria and required Validation, record the canonical task worktree/branch and start-of-attempt synchronization evidence, populate the Completion Report, set `status: review`, return control to `moda_architect` and **STOP**. Do not launch enabled or unrelated tasks. For publication task, do not rerun implementation validation.

## Implementation Notes

Point to Shopify merchant settings via instructions, not invented deep links or a mandatory custom App Block.

Before claiming, use the deterministic `/moda-task` launcher and its **actual** prepared packet, read the task's complete current Architect Review, and verify task/dependency status in the developer's canonical workspace. Preserve `docs/decisions/**/_index.md` untouched until the developer explicitly closes the architecture documentation session. New runtime structured logging uses `@modainteract/moda-interact-shared/logging` where applicable. No source outside this task's owner repository may be changed unless explicitly authorised by the architecture.

## Completion Report

### Status

Not Started — external portable definition, not materialised.

### Files Changed

None — not implemented.

### Work Completed

None.

### Validation Results

Not run; the supplied snapshot is not the developer's task worktree.

### Deviations

None.

### Assumptions

Use the 2026-10-20 snapshot only as a baseline; verify current active code on task claim. Consent has no fixed 72-hour wait or expiry; checkout eligibility follows the authoritative lifecycle.

### Unresolved Issues

None recorded at definition time; report any discovered cross-repository dependency rather than implementing outside ownership.

### Architectural Concerns

None recorded at definition time.

## Architect Review

### Review Status

Pending — no implementation reviewed.

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
