---
id: ARCH-045-SYSTEM-TEST-001
architecture_id: ARCH-045
title: Certify Shopify phone-consent sync and normal reconciliation gating
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 60
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-045-DATABASE-002
  - ARCH-045-SHARED-002
  - ARCH-045-SHOPIFY-001
  - ARCH-045-SHOPIFY-002
  - ARCH-045-BACKGROUND-001
  - ARCH-045-BACKGROUND-002
  - ARCH-045-BACKGROUND-003
  - ARCH-045-BACKGROUND-004
  - ARCH-045-SHARED-001
  - ARCH-045-BACKGROUND-005
enables: []
created: 2026-10-20
updated: 2026-10-22
---
# Certify Shopify phone-consent sync and normal reconciliation gating

## Architecture

Architecture ID: `ARCH-045`
Architecture document: `docs/architecture/ARCH-045-shopify-whatsapp-consent-gated-recovery.md`
Coordinator: `moda_architect`
**Lifecycle:** portable definition, **not** materialised in a developer task worktree or committed/pushed; no execution claim exists.

## Objective

Black-box certify Shopify native consent changes update **current CustomerPhone** but do **not** trigger recovery, and that **the next ordinary checkout reconciliation** reads the latest consent before first recovery creation.

## Context

Terminal validation after all implementation, migration and Shared publication tasks are architect-accepted. Old `DETECTED+WHATSAPP_CONSENT_MISSING`, 72-hour consent wait and immediate-consent-webhook recovery scenarios are superseded. **This task explicitly owns the live Shopify release verification moved from `ARCH-045-SHOPIFY-001`: deployed app configuration, installed consent-read/protected-data access, read-only non-production GraphQL query and real signed webhook smoke.** These checks are terminal release gates, not prerequisites to the SHOPIFY-001 code task's completion.

## Scope

- Identify the actually deployed Shopify app/configuration (do not infer deployment from a TOML filename); verify the selected API version and live `customers_whats_app_marketing_consent/update` webhook subscription. For an authorised non-production shop, verify the **installed** `read_customers` grant and protected-customer-data approval; record any required reauthorisation without adding `write_customers`.
- With that non-production installed-shop token, issue a **read-only** Shopify customer WhatsApp-consent GraphQL query for a known customer; verify actual field access, a response free of GraphQL `errors`/field denial, and exact customer GID equality with Shared-normalised numeric webhook identity. HTTP 200 or TOML-declared scopes alone are insufficient.
- Deliver an actual HMAC-valid consent-change webhook against the deployed non-production ingress; prove durable enqueue of the published Shared existing-queue sync job **before** successful acknowledgement, then verify compatible `ARCH-045-BACKGROUND-003` consumption, fresh Shopify GraphQL read, correct `commerce.CustomerPhone` update and absence of checkout candidate/CheckoutRecovery/charge/notice effects **from consent event alone**. Do not activate provider delivery until the consumer is deployed and compatible.
- Exercise normal abandoned-checkout event with missing/unknown consent: zero recovery, sequence-one attempt, provider sends or credit, one shop+checkout-keyed merchant Support notice.
- Later native SUBSCRIBED change with **no further checkout event**: assert phone state updates but no new recovery. Then emit a real normal checkout update/reconciliation for the same still-abandoned/unpaid checkout: assert one first recovery, correct billing and no duplicate send.
- Exercise no subsequent checkout event, removed/matured candidate, completed checkout, changed exact phone or customer, duplicate/out-of-order sync, sync outage, provider state changes, **one fresh Shopify read per distinct new checkout**, **zero Shopify GraphQL reads on later follow-up sends**, stored-state final send gate and redacted diagnostics.
- No 72-hour consent expiry. Source authority and checkout business eligibility remain independent.

- **Consent release gates (C1/C2/C3/C6, H1/H2):** Include phone-only legacy merge, two customers sharing the number, UK local vs `+44`, ambiguous country, changed phone, missing Shopify guest/customer identity, provider 200-with-errors, numeric webhook vs GID, old consent-sync replay, recipient STOP and Shopify-native merchant consent change (without a separate Moda merchant opt-out screen).
- Trace every first send entry: matured candidate, direct initiation, suppression/capacity unblocking, existing DETECTED history, scheduled sequence-two and merchant post-window human template. Assert fresh consent at new-checkout admission, later stored-only revision checks under concurrent revocation, and **confirmed Meta Marketing category** for abandoned-basket templates, not Utility/Authentication.
- Observe bounded Support notices and retry behaviour, consent change without subsequent checkout event (no recovery), and later legitimate normal checkout update (first recovery if still eligible).
- Validate **quoted STOP** suppresses the identified merchant's phone only, **standalone STOP** suppresses every registered merchant sharing that canonical phone, and an **unresolvable quoted reference** follows the number-wide rule. For all affected Shopify and Woo merchants, verify **one Moda Support notice per merchant**, immediate local STOP enforcement, native `SUBSCRIBED` **even after STOP** updating only the native decision without lifting STOP, and no outbound WhatsApp to stopped recipients (including in-window human/AI replies). No Shopify mutation or `write_customers` access is used; do not invent a global STOP store.

## Out of Scope

- No actual production messaging, source-code implementation or fabricated integration PASS when live Shopify fixture unavailable.

## Requirements

- [ ] Black-box production-like boundaries, durable DB credit/candidate evidence, tenant isolation and redacted logs.
- [ ] Missing Docker/test-shop capability recorded as incomplete, not PASS.

## Work Items

- [ ] Identify the deployed non-production Shopify app/TOML, API version and consent topic; record installed `read_customers` permission and protected-data access, including any missing-grant or re-authorisation blocker.
- [ ] Run read-only customer-consent GraphQL smoke: no `errors`/field denial, exact GID mapping from a real numeric-ID webhook, and no Shopify mutations or `write_customers` requirement.
- [ ] Build consolidated black-box fixtures for local CustomerPhone plus Shopify provider authority, **real signed consent webhook** and checkout/event queue, preserving captured provider evidence.
- [ ] Verify live authenticated webhook acknowledgement follows durable sync-job enqueue and Background consumption; record selected app/consumer versions, redacted identifiers and failure/retry behaviour.
- [ ] Run no-grant, webhook-only no-recovery, later genuine checkout reconciliation, duplicate/stale and outbound revoked tests.
- [ ] Record DB/customer-phone/provider/merchant Support and credits evidence with explicit missing-live-Shopify gaps.

## Interfaces / Contracts

ARCH-045-DATABASE-002, published SHARED-001/002 **sync** event, SHOPIFY-001/002, BACKGROUND-001/002/003/004. No consent-driven recovery wakeup or superseded DATABASE-001.

## Dependencies

- `ARCH-045-DATABASE-002`
- `ARCH-045-SHARED-002`
- `ARCH-045-SHOPIFY-001`
- `ARCH-045-SHOPIFY-002`
- `ARCH-045-BACKGROUND-001`
- `ARCH-045-BACKGROUND-002`
- `ARCH-045-BACKGROUND-003`
- `ARCH-045-BACKGROUND-004`
- `ARCH-045-SHARED-001`
- `ARCH-045-BACKGROUND-005`

## Enables

None

## Acceptance Criteria

- [ ] The **deployed non-production** Shopify app has the intended API version and live consent topic, and its installed token is authorised (`read_customers` plus protected-customer-data approval) to read the exact customer's consent field without GraphQL errors or field denial; no `write_customers` required.
- [ ] A **real signed** Shopify consent webhook maps numeric/GID identity correctly, is durably queued before success acknowledgement and consumed by the compatible Background handler; verify failures/retries without creating unrelated checkout work.
- [ ] Consent change updates exact CustomerPhone and **alone causes no recovery, candidate or send**.
- [ ] Without consent, ordinary reconciliation creates zero recovery/credit with correctly scoped Support notice.
- [ ] A **subsequent actual** reconciliation on eligible checkout can create exactly one first recovery after grant; without event there is no guaranteed re-evaluation.
- [ ] Locally recorded STOP cannot be cleared by a Shopify grant, a webhook or merchant enable; it blocks every outbound type, while a merchant-owned restriction and later stored revocation also block proactive sends; subsequent messages check durable CustomerPhone, **not** Shopify on every follow-up. The Shopify consent-webhook flow is tested separately for timely mirror updates and its outage/staleness trade-off; no arbitrary 72-hour clock.

- [ ] Verified no recovery before consent; no initial or proactive send after STOP/phone change; no customer identity leakage or Meta charge on denial.
- [ ] Marketing recovery uses Meta-approved Marketing templates; Utility/Authentication or unverifiable category is blocked before send. Standalone multi-merchant STOP, quoted single-merchant STOP and idempotent affected-merchant Support notices work with **zero** Shopify writes; refreshed provider `GRANTED` never releases STOP.

## Validation

- [ ] Consolidated PostgreSQL/BullMQ and **real non-production Shopify provider** evidence: deployed app/topic/version, installed customer-read permission and protected-data approval, GraphQL no-error field access/customer ID equality, signed webhook-to-queue-to-Background handoff, billing/Support assertions, trusted vs stubbed provider boundaries, `git diff --check`. Never treat source TOML or a mock as proof of deployed access.

- [ ] Realistic queued event/DB and provider/mock tests cover all review cases rather than only isolated task mocks.

## Stop Condition

After completing only the defined Work Items, Acceptance Criteria and required Validation, record the canonical task worktree/branch and start-of-attempt synchronization evidence, populate the Completion Report, set `status: review`, return control to `moda_architect` and **STOP**. Do not launch enabled or unrelated tasks. For publication task, do not rerun implementation validation.

## Implementation Notes

This is terminal validation. Do not mark ARCH-045 Implemented until the architect reviews complete cross-service evidence.

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
