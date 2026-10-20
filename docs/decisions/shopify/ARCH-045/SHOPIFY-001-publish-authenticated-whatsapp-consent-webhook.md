---
id: ARCH-045-SHOPIFY-001
architecture_id: ARCH-045
title: Authenticate and enqueue Shopify WhatsApp consent webhooks
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-045-SHARED-002
enables:
  - ARCH-045-BACKGROUND-003
  - ARCH-045-SYSTEM-TEST-001
created: 2026-10-20
updated: 2026-10-20
---
# Authenticate and enqueue Shopify WhatsApp consent webhooks

## Architecture

Architecture ID: `ARCH-045`
Architecture document: `docs/architecture/ARCH-045-shopify-whatsapp-consent-gated-recovery.md`
Coordinator: `moda_architect`
**Lifecycle:** portable definition, **not** materialised in a developer task worktree or committed/pushed; no execution claim exists.

## Objective

Subscribe to and durably enqueue authenticated Shopify WhatsApp marketing consent-change webhooks as the canonical Shared v1 wakeup event.

## Context

`routes/webhooks/root/route.jsx` authenticates Shopify and the ingress classifier ignores topics it does not know. Snapshot contains two divergent app TOMLs; the agent must identify the deployed Shopify app configuration, not guess.

## Scope

- Verify which Shopify app configuration the actual deploy/dev command uses; add `customers_whats_app_marketing_consent/update` to that authoritative `[webhooks.subscriptions]` using the verified API version (2026-07+).
- Verify `read_customers` on the actual installed app scope, including upgrade/re-authorisation implications; do not request write access.
- Extend the authenticated root ingress topic dispatch with minimal strict payload normalisation (`customer_id`, delivery ID, triggeredAt, resolved shopId), Shared schema validation and durable BullMQ publication using the published Shared job constants/ID.
- Preserve existing HMAC authentication, inactive-shop handling, webhook observational events, bounded enqueue failure and fast acknowledgement.

## Out of Scope

- No Shopify GraphQL consent reads during webhook ingress; no recovery state transition or customer messaging in HTTP handler.
- No storefront tracking CMP, theme App Block, pixel or script injection.
- No modification of irrelevant Shopify app TOML solely to make a template look consistent without verifying it is actually deployed.

## Requirements

- [ ] Authenticated and validated webhook enqueue succeeds before 2xx; Redis timeout/failure remains retryable, not acknowledged as success.
- [ ] Queued event does not carry phone/email/consent state; only stable customer identity and transport correlation.
- [ ] Unrecognised/invalid customer ID cannot wake up recoveries for another customer; all existing checkout/order/discount webhook behaviour remains unchanged.

## Work Items

- [ ] Verify authoritative Shopify app config, scope and topic availability in active version.
- [ ] Implement topic normalisation and Shared job publication.
- [ ] Add HMAC, config, payload and queue-failure tests.

## Interfaces / Contracts

Produces published Shared `ShopifyWhatsAppConsentChangedJobV1Schema` event with `schemaVersion:1`. Shopify topic `customers_whats_app_marketing_consent/update` is a wakeup only, not permission evidence. Contract owner: ARCH-045-SHARED-001 / publication ARCH-045-SHARED-002.

## Dependencies

- `ARCH-045-SHARED-002`

## Enables

- `ARCH-045-BACKGROUND-003`
- `ARCH-045-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Valid authenticated event durably publishes exactly the normalised v1 job before acknowledgement.
- [ ] Invalid HMAC cannot publish; inactive/unknown shop cannot cross tenant boundaries.
- [ ] Duplicate webhook re-delivery is safely deduplicated/retryable; no full customer payload or token enters queue/logs.
- [ ] Real active app config lists correct topic and required read scope.

## Validation

- [ ] Focused Shopify webhook HMAC/queue-contract and queue-failure tests plus repository-declared app checks; `git diff --check`.
- [ ] Shopify CLI subscription/config validation or documented live test-store evidence for actual deployed app config.

## Stop Condition

After completing only the defined Work Items, Acceptance Criteria and required Validation, record the canonical task worktree/branch and start-of-attempt synchronization evidence, populate the Completion Report, set `status: review`, return control to `moda_architect` and **STOP**. Do not launch enabled or unrelated tasks. For publication task, do not rerun implementation validation.

## Implementation Notes

Do not infer runtime config from filename. Shopify 2026-07 documented webhook payload uses `customer_id` and `phone_number`; never use webhook phone as identity/permission for admission. Existing `recordShopifyWebhookOutcome` is reusable.

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
