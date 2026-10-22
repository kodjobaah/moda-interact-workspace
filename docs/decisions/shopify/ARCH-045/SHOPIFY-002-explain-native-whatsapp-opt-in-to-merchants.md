---
id: ARCH-045-SHOPIFY-002
architecture_id: ARCH-045
title: Explain Shopify WhatsApp recovery consent to merchants
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: in_progress
priority: 36
executor: developer
claimed_at: 2026-10-22T10:44:49Z
attempt: 1
depends_on: []
enables:
  - ARCH-045-SYSTEM-TEST-001
created: 2026-10-20
updated: 2026-10-22
---
# Explain Shopify WhatsApp recovery consent to merchants

## Architecture

Architecture ID: `ARCH-045`
Architecture document: `docs/architecture/ARCH-045-shopify-whatsapp-consent-gated-recovery.md`
Coordinator: `moda_architect`
**Lifecycle:** supplied as a portable architect definition and materialised in the canonical parent task worktree on `task/ARCH-045-SHOPIFY-002`. No implementation attempt is claimed until the launcher completes execution preparation.

## Objective

Add a concrete **WhatsApp Customer Consent** section to the existing merchant **Recovery Settings** screen with actionable native Shopify setup guidance and the exact effect of missing or later consent.

## Context

Merchants will receive a checkout-keyed Support notice once BACKGROUND-002 is implemented, not a blocked `CheckoutRecovery`. Consent is held by Shopify and has no Moda-imposed 72-hour expiry. Only a checkout that can be safely rechecked while eligible may produce a recovery after later opt-in.

## Scope

- Render the guidance in the existing Shopify Recovery Settings view, including how to enable Shopify's native WhatsApp marketing opt-in at checkout, why consent saved on submitted checkout may not cover early abandonment and how Shopify Forms can collect opt-in beforehand. Use accurate public Shopify documentation and merchant translations already supported by the app.
- Explain no verified consent means **no CheckoutRecovery**, no customer message/charge and a checkout-keyed merchant Support notice when ordinary reconciliation encounters the problem.
- Explain later opt-in updates the customer phone preference but does **not** immediately scan or revive old abandoned checkouts; only a later **normal checkout reconciliation**, if any, may encounter the still-eligible checkout and create a recovery. No consent expiry clock or merchant bypass.
- Explicitly label abandoned-basket WhatsApp reminders as **marketing messages**, not order-confirmation/utility updates. Explain that consent must authorise WhatsApp recovery marketing, not merely allow the merchant to collect the checkout phone number. Explain that a WhatsApp STOP sent to Moda is enforced **locally**, the affected merchant receives a Moda Support notice, and Shopify consent status cannot override that STOP.

## Out of Scope

- No storefront CMP/banner/app block/pixel, Shopify consent write or new merchant manual send bypass.
- No claim that customer consent expires after 72 hours or that a previously skipped checkout is guaranteed to be found later.

## Requirements

- [ ] Text refers to a checkout that cannot be recovered yet, **not** a paused/expiring `DETECTED` recovery.
- [ ] Consent collection is native Shopify; no Customer Privacy API tracking consent is repurposed.
- [ ] The guidance describes WhatsApp abandoned-basket messaging as marketing and does not conflate it with transactional order updates or Customer Privacy tracking consent.

- Merchant instructions state that native WhatsApp marketing permission is distinct from Shopify Customer Privacy tracking, that identity may be missing for guest checkouts, and that a later grant updates current permission but does not itself re-run a discarded candidate. Explain merchant-side native consent management in Shopify Admin and Moda-side WhatsApp STOP, without suggesting a second Shopify cookie-consent banner or a duplicate Moda merchant opt-out control.

## Work Items

- [ ] Implement the dedicated Recovery Settings section and focused rendering/localisation tests. Do not modify Support notice generation, which belongs to BACKGROUND-002.
- [ ] Verify guidance differentiates absent consent from Shopify API verification unavailability, and describes next normal reconciliation rather than a consent-triggered retry.

## Interfaces / Contracts

Existing Shopify merchant Recovery Settings UI; BACKGROUND-002 owns merchant Support notice creation. No API or storefront extension.

## Dependencies

None

## Enables

- `ARCH-045-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Merchant guidance truthfully separates consent-change sync from normal checkout re-evaluation and no-contact/no-charge outcomes.
- [ ] No guarantee of automatic recovery on opt-in alone, no tracking-consent confusion or artificial 72-hour timer.

- [ ] Copy neither promises recovery on opt-in alone nor asks a merchant to bypass missing permission; merchant native WhatsApp consent can be managed in Shopify Admin, while a STOP received through Moda remains a non-overridable local restriction.

## Validation

- [ ] Focused Shopify Recovery Settings rendering, external documentation link, accessible UI/localisation and no-bypass language checks; `git diff --check`.

## Stop Condition

After completing only the defined Work Items, Acceptance Criteria and required Validation, record the canonical task worktree/branch and start-of-attempt synchronization evidence, populate the Completion Report, set `status: review`, return control to `moda_architect` and **STOP**. Do not launch enabled or unrelated tasks. For publication task, do not rerun implementation validation.

## Implementation Notes

Point to Shopify merchant settings via instructions, not invented deep links or a mandatory custom App Block.

Before claiming, use the deterministic `/moda-task` launcher and its **actual** prepared packet, read the task's complete current Architect Review, and verify task/dependency status in the developer's canonical workspace. Preserve `docs/decisions/**/_index.md` untouched until the developer explicitly closes the architecture documentation session. New runtime structured logging uses `@modainteract/moda-interact-shared/logging` where applicable. No source outside this task's owner repository may be changed unless explicitly authorised by the architecture.

## Completion Report

### Status

In Progress — Attempt 1 claimed by developer at 2026-10-22T10:44:49Z. Attempt 0 review history is preserved below.

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

## Developer Takeover Amendment - 2026-10-22

The developer explicitly invoked `/moda_developer_create ARCH-045-SHOPIFY-002` for this agent-owned task. The task is transferred to developer execution with developer-controlled completion while preserving the assigned agent `moda_app`, repository ownership, scope, dependencies, acceptance criteria and validation requirements. Attempt claim and implementation-worktree preparation remain delegated to the canonical launcher.
