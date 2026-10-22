---
id: ARCH-046-WOOCOMMERCE-002
architecture_id: ARCH-046
title: Capture affirmative pre-submit Woo consent and publish durable evidence
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 27
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-035-WOOCOMMERCE-007
  - ARCH-046-API-001
  - ARCH-046-WOOCOMMERCE-001
enables:
  - ARCH-046-WOOCOMMERCE-003
  - ARCH-046-SYSTEM-TEST-001
  - ARCH-046-SYSTEM-TEST-002
created: 2026-10-20
updated: 2026-10-22
---

# Capture affirmative pre-submit Woo consent and publish durable evidence

## Architecture

Architecture ID: `ARCH-046`

Architecture document: `docs/architecture/ARCH-046-woocommerce-whatsapp-consent-gated-recovery.md`

Coordinator: `moda_architect`

**Lifecycle:** portable definition from 2026-10-20 snapshot; not materialised, claimed, committed, implemented or architect-accepted. Status means definition eligibility only.

## Objective

Securely publish an explicit Woo WhatsApp recovery opt-in/withdrawal **before order placement** and resolve it to an existing merchant-scoped customer and exact phone through Moda’s own optional checkout field.

## Context

Classic/Blocks additional checkout field persistence at order completion does not guarantee Moda can recognise consent before abandonment. Hosted API-001 records current customer-phone permission. The plugin must authenticate the active checkout checkbox action server-side; the hosted API locates `Customer` through the authenticated shop and canonical phone.

**Architect-approved validation handoff (2026-10-21):** Shared `ARCH-045-SHARED-001` supplies runtime-neutral golden identity fixtures and Node coverage; after `ARCH-045-SHARED-002` publishes them, this WooCommerce consumer task owns **PHP-runtime** parity for the applicable exact-recipient and recipient-lifecycle vectors. Runtime PHP parity is intentionally not a Shared-task acceptance or publication prerequisite.

## Scope

- In Classic and Blocks, capture a deliberate checkbox GRANT or withdrawal through supported UI hooks and server-verified live Woo checkout action with exact canonical phone. Do not infer opt-in from a default checked field or completed order metadata.
- Use the existing verified WordPress installation authentication to POST to API-001, with stable event ID on retry; protect the guest checkbox action against forgery using normal WordPress/WooCommerce server-side session and nonce controls; phone lookup alone is not a GRANT.
- Persist consent **before order placement** when the hosted API is available; on outage checkout may proceed but current permission remains unverified. Consent submission itself never schedules a recovery/reconciliation job.
- Preserve 20-locale opt-in wording, both checkout implementations, and Moda checkbox registration controlled by existing installation/feature eligibility.

- Update the existing Woo plugin checkout activity publisher to carry the same authenticated installation/shop context and canonical recipient accepted by API-001, under an agreed version/compatibility transition. Do not change ARCH-035 capture-only business semantics or turn consent submission into checkout reconciliation.

## Out of Scope

- No recovery creation, Shopify code, new WP consent table, arbitrary third-party checkbox integration or unilateral consent grants from admin. Shopify numeric customer ID/GID conversion fixtures are not applicable to Woo PHP; Shared already owns their Node contract tests.

## Requirements

- [ ] A pre-submit affirmative checkbox action must refer to the specific merchant's WhatsApp **abandoned-basket marketing** disclosure shown to the customer; the default unchecked field or receipt of a phone number cannot establish permission. Preserve disclosure version and locale for API-001 evidence.

- [ ] Positive action is persisted in hosted CustomerPhone before abandonment when connectivity succeeds; mere completed-order field does not suffice.
- [ ] A guest checkbox action is server-validated; the API may locate the one unambiguous existing customer in that shop by canonical phone, but neither a phone match nor a checkout observation creates new consent. An unavailable host allows checkout but not outbound permission.

- **C4/H3:** For Classic and Blocks, verify the checkout field action server-side and pass the canonical number through authenticated plugin-to-API transport. Do not persist a separate WooCheckoutCustomerIdentity. The API uses installation-derived merchant and existing Customer/CustomerPhone; stale guest/session actions and phone edits must fail validation.
- Choose and document the pre-submit consent publication point independently for each checkout mode. The UI must not show success or allow recovery eligibility until the hosted API acknowledges a durable consent write; normal checkout activity published before ACK must remain potentially ineligible. Do not fabricate consent from order-meta/checkbox render state or schedule a special recovery wake-up to fix races.
- Make retried HTTP publication idempotent with stable event ID and server-ordered decision revision; a revoke must not be overtaken by late GRANT after a multi-tab or Action Scheduler retry. Woo checkout itself must remain usable on hosted outage.

## Work Items

- [ ] Implement isolated Classic/Blocks pre-submit change capture, server-validated checkout action and canonical phone capture and server-to-server retry.
- [ ] Test abandon-before-order, guest/registered checkout, new phone, withdrawn consent, disabled recovery feature, retries, API outage, HPOS and active locale.

- [ ] Implement server-validated checkout action and nonce/guest-session replay tests in Classic and Blocks with independently observable API ACK vs checkout event ordering.
- [ ] Test abandonment before Place Order, API delayed/failure, lost ACK/retry, Blocks Store API nonce/cart-token, Classic CSRF, new phone, logout and cross-device ambiguous guest.
- [ ] Add parameterised PHP compatibility tests loading `@modainteract/moda-interact-shared/identity/fixtures` from the approved published Shared version; exercise all applicable `phoneCases` and recipient-lifecycle safeguards and record the Shared version and test results in the Completion Report.

## Interfaces / Contracts

Consumes WOOCOMMERCE-001 Moda field, ARCH-035 checkoutKey support and API-001 versioned customer-phone consent contract.

**Portable fixture contract:** `ARCH-045-SHARED-001` owns the canonical JSON (published by `ARCH-045-SHARED-002` at `@modainteract/moda-interact-shared/identity/fixtures`). PHP consumes the portable test data, not Shared JavaScript/TypeScript source. `ARCH-046-API-001` already depends on `ARCH-045-SHARED-002`, so publication is an existing transitive prerequisite for this task; no new dependency is necessary.

## Dependencies

- `ARCH-035-WOOCOMMERCE-007`
- `ARCH-046-API-001`
- `ARCH-046-WOOCOMMERCE-001`

## Enables

- `ARCH-046-WOOCOMMERCE-003`
- `ARCH-046-SYSTEM-TEST-001`
- `ARCH-046-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] Verified explicit pre-submit phone consent updates hosted CustomerPhone with immutable evidence exactly once per decision.
- [ ] Unselected checkbox, inactive installation or hosted outage does not grant consent or block Woo order submission.
- [ ] Consent change alone causes no checkout candidate/recovery enqueue or WhatsApp/billing action.
- [ ] PHP test evidence demonstrates parity with the applicable published Shared phone/recipient identity fixtures without adding Shopify-only identity code or inferring consent from a matching phone.

- [ ] With ACK first, a subsequent normal checkout reconciliation sees the same consent and customer; with checkout first/no ACK, no recovery is promised, no wake-up invented, and order placement remains unaffected.

## Validation

- [ ] LocalWP guest/registered Classic/Blocks pre-order integration and API/PostgreSQL assertion, PHP/JS unit tests, declared lint/build and `git diff --check`.

- [ ] End-to-end LocalWP Classic/Blocks pre-submit ordering tests with queued checkout activity and hosted API captured independently.
- [ ] PHP fixture-parity suite passes against the versioned Shared `identity/fixtures` artifact; capture command, results and fixture/package version in the Completion Report.

## Stop Condition

After completing **only** the defined Work Items, Acceptance Criteria and required Validation, record launcher-resolved dedicated parent/implementation worktrees, their physical isolation and start-of-attempt synchronization evidence in the Completion Report. Change task to `review`, return control to `moda_architect`, and **STOP**. Do not start enabled tasks. A `blocked` task must remain blocked until the architect verifies and records the external missing recovery dependency and explicitly makes it Ready.

## Implementation Notes

Keep session binding, field observation and remote publication in separate small classes/modules. Avoid one large `Runtime.php` or `page.js` handler; use existing server transport and Action Scheduler where available.

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
