---
id: ARCH-003-SYSTEM-TEST-001
architecture_id: ARCH-003
title: Verify tenant attribution across operational queues
task_kind: system_test
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
status: pending
priority: 40
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-003-BACKGROUND-001
  - ARCH-003-ADMIN-019
enables: []
created: 2026-09-05
updated: 2026-09-05
---

# Verify tenant attribution across operational queues

## Architecture

`docs/architecture/ARCH-003-admin-operational-ui.md`

## Objective

Produce integrated evidence that the completed ARCH-003 queue diagnostics show
tenant identity truthfully across all four operational queues.

## Required proof

### checkout-events

```text
data.tenant.shopId
data.tenant.shopDomain
jobId begins <shopId>--
Admin shows known shop
```

### order-events

```text
data.tenant.shopId
data.tenant.shopDomain
jobId begins <shopId>--
Admin shows known shop
```

### pending-recovery-candidates

```text
data.shopId
data.shopDomain
jobId begins <shopId>--
Admin Delayed view shows known shop
```

### whatsapp-events

When no approved tenant attribution exists at ingress:

```text
Admin shows Unresolved
```

and does not guess a shop.

## Observability navigation verification

Final integrated verification must also confirm:

```text
Observability parent -> /observability/queues
submenu -> Shopify Queues + Grafana
no Overview child
```

and `/observability` contains no Shopify Queues promotional card/CTA.

## Acceptance Criteria

- [ ] Known Shopify queues show the correct tenant.
- [ ] New pending-recovery candidate shows the correct tenant.
- [ ] Delayed pending-recovery job remains visible.
- [ ] WhatsApp no-tenant ingress shows Unresolved.
- [ ] Orphan remains distinct from Unresolved.
- [ ] Known shop / Unresolved / Orphan filters behave truthfully.
- [ ] No sensitive data is exposed.
- [ ] Verification requires no queue mutation.

## Completion Report

### Status

Not started.

## Architect Review

### Review Status

Pending
