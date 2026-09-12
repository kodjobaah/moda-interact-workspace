---
id: ARCH-010-SYSTEM-TEST-003
architecture_id: ARCH-010
title: Validate partial top-up refunds and opt-in promotional campaigns
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: manual
status: pending
priority: 102
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-010-BACKGROUND-014
  - ARCH-010-BACKGROUND-019
  - ARCH-010-ADMIN-003
  - ARCH-010-ADMIN-005
  - ARCH-010-ADMIN-006
  - ARCH-010-SHOPIFY-017
  - ARCH-010-SHOPIFY-020
  - ARCH-010-SHOPIFY-021
  - ARCH-010-SHOPIFY-022
enables:
  - ARCH-010-SYSTEM-TEST-004
created: 2026-09-11
updated: 2026-09-12
---

# ARCH-010-SYSTEM-TEST-003: Validate partial top-up refunds and opt-in promotional campaigns

## Terminal/manual gate

Do **not** auto-start. The developer explicitly invokes this terminal/manual validation after relevant implementation is integrated and manually smoke-checked. No implementation task depends on this task.

## Objective

Validate:

1. purchased top-up FIFO lot accounting and partial human-settled refunds;
2. optional GLOBAL/PLAN/SHOP promotional campaigns;
3. one selected promotion per merchant;
4. promo-first recovery consumption;
5. campaign expiry/close/reopen and permanent merchant/campaign history.

## Promotion scenarios

At minimum validate end-to-end:

1. Admin creates GLOBAL campaign; eligible merchant sees it but receives no credits before selection;
2. PLAN campaign is visible/selectable only on its exact current mapped plan;
3. SHOP campaign is visible only to exact target Shop;
4. multiple campaigns can run concurrently and one merchant can see multiple eligible offers;
5. merchant selects one campaign and gets exactly one allocation;
6. a different still-usable selected promo prevents switching;
7. promo is consumed **before Paid monthly included** and before every other bucket;
8. Free consumes promo before purchased/lifetime Free;
9. selected promo expiry stops new promo reservations without killing a recovery already reserved before expiry;
10. selected PLAN promo becomes ineligible after plan change and another eligible promo can be selected;
11. campaign close stops new selection/reservation immediately while preserving history;
12. Admin reopens the same campaign by extending expiry; same campaign ID/history remains;
13. partially-used merchant can reselect reopened campaign and only original remainder returns;
14. exhausted merchant gets no new quantity when campaign is reopened;
15. same merchant cannot claim same campaign twice under concurrency/retry;
16. two-tab selection of two promotions yields exactly one current selection;
17. merchant history distinguishes selected-but-unused, used, exhausted and expired/closed/reopened cases;
18. Admin catalogue retains all campaigns and lifecycle events;
19. Admin usage report distinguishes merchants selected vs actually used;
20. promotional usage creates no Shopify normal-recovery/top-up App Event and is non-refundable;
21. FROZEN/NO_CONTRACT/inactive shop cannot spend selected promo;
22. no automatic paid overage exists.

## Refund scenarios

Retain the accepted DATABASE-007/BACKGROUND-014/ADMIN-002/003/SHOPIFY-017 partial-refund matrix, including exact purchased lot selection, refund hold, human provider settlement evidence, multiple partial refunds, concurrency safety and strict exclusion of promotional/lifetime-Free credits from refundable quantity.

## Evidence

Capture deterministic fixtures, relevant DB rows/counters/reservations, merchant/Admin UI evidence and provider-call absence/presence needed to prove the above. Do not expose secrets.

## Non-goals

Do not implement missing behaviour from the system-test task. Report defects to `moda_architect` for routing to the owning repository task.

## Completion Report

### Status
Not started/manual-gated.

### Validation Results
Populate when explicitly invoked.

### Architect Review
Pending.
