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
status: pending
priority: 36
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-045-BACKGROUND-002
enables:
  - ARCH-045-SYSTEM-TEST-001
created: 2026-10-20
updated: 2026-10-20
---
# Explain Shopify WhatsApp recovery consent to merchants

## Architecture

Architecture ID: `ARCH-045`
Architecture document: `docs/architecture/ARCH-045-shopify-whatsapp-consent-gated-recovery.md`
Coordinator: `moda_architect`
**Lifecycle:** portable definition, **not** materialised in a developer task worktree or committed/pushed; no execution claim exists.

## Objective

Make Shopify WhatsApp recovery-consent requirements and the native opt-in path understandable to merchants without introducing a custom storefront consent UI.

## Context

A merchant who receives the Support inbox notice needs actionable setup guidance. The existing Shopify merchant Recovery Settings and Support inbox are the canonical interfaces.

## Scope

- Add concise Shopify-only guidance to existing Recovery Settings/help context explaining how to enable WhatsApp marketing opt-in through Shopify checkout/Forms and the importance of consent **before** customers abandon checkout.
- Explain that missing consent pauses initial recovery for at most 72 hours, no credit is consumed, and later Shopify opt-in can resume only an eligible unchanged checkout.
- Ensure the merchant Support message can be read in the existing UI with correct wording; do not create a competing notifications page.

## Out of Scope

- No app blocks, banner, cookie CMP, web pixel or `setTrackingConsent` use.
- No merchant button that overrides consent, no automatic creation of Shopify customer opt-in and no new staff/auth roles.
- No live privacy settings mutation; guidance only.

## Requirements

- [ ] Marketing-cookie tracking consent and WhatsApp marketing opt-in are clearly distinguished.
- [ ] Advice does not promise resumption for unmatched guest customer ID or after expiry.
- [ ] Follow existing merchant UI localisation/navigation standards where applicable; no new admin route.

## Work Items

- [ ] Add bounded copy in existing Recovery Settings.
- [ ] Add focused component/text validation.
- [ ] Check existing Support inbox notice presentation and merchant translation/localisation contract.

## Interfaces / Contracts

Consumes existing Support inbox (`MerchantSupportMessage` SYSTEM) and ARCH-045-BACKGROUND-002 notice wording; no cross-service UI contract.

## Dependencies

- `ARCH-045-BACKGROUND-002`

## Enables

- `ARCH-045-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Merchant can discover native Shopify opt-in setup and correct missing-consent explanation.
- [ ] No merchant action can bypass Shopify consent or silently record an opt-in.
- [ ] Existing Shopify navigation and Support inbox unchanged except for bounded copy.

## Validation

- [ ] Focused Shopify merchant UI/test assertion, localisation smoke where touched and repository-declared build; `git diff --check`.

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

Use the 2026-10-20 snapshot for orientation; revalidate active code/configuration when the task is materially claimed. ARCH-045's provisional 72-hour consent-wait deadline is the exact v1 task contract unless the developer and architect amend it before implementation.

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
