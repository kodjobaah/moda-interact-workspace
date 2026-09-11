---
id: ARCH-010-ADMIN-005
architecture_id: ARCH-010
title: Grant promotional credits to a bounded targeted merchant campaign
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 84
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-010-ADMIN-004
enables:
  - ARCH-010-SYSTEM-TEST-003
created: 2026-09-11
updated: 2026-09-11
---

# ARCH-010-ADMIN-005: Grant promotional credits to a bounded targeted merchant campaign

## Objective

Build a SUPER_ADMIN-only targeted campaign workflow on top of ADMIN-004's audited one-shop grant primitive.

This task supports examples such as:

- selected beta/test merchants;
- launch/retention campaigns;
- a hand-picked merchant cohort;
- goodwill credits for multiple affected shops.

It does **not** introduce a generic marketing automation platform or expiring campaigns.

## Inspect before editing

```text
src/app/(protected)/page.tsx
src/components/admin/tenant-table.tsx
src/components/admin/tenant-row.tsx
src/components/admin/tenant-detail-panel.tsx
src/app/(protected)/billing/controls/page.tsx
src/components/admin/billing-controls.tsx
src/app/actions/billing-controls.ts
src/lib/admin/billing-controls.ts
src/lib/admin/billing-control-validation.ts
src/lib/admin/tenant*.ts   # exact existing tenant search/list implementation
tests/security/**
tests/unit/**admin**
package.json
```

Reuse existing protected tenant search/directory data. Do not add a second shop-discovery backend if the current directory can provide exact internal shop ids.

## 1. Target selection

Provide a protected multi-shop selection flow using exact internal shop ids from the Admin tenant directory/search.

Requirements:

- never accept arbitrary merchant-supplied domains as grant authority;
- deduplicate selected shop ids before submission;
- display shop identity/status/plan context before execution;
- require at least one selected shop;
- keep one request bounded. If the current UI/query layer has no smaller established bulk limit, cap one submitted batch at 100 shops.

The 100-shop cap is an operational bound, not a product limit. Larger campaigns can be submitted in additional idempotent batches.

## 2. Shared campaign grant fields

One campaign submission supplies:

```text
quantity              positive whole credits PER selected shop
grantType             normally CAMPAIGN or BETA_TESTER
reason                required
campaignReference     required, non-blank internal reference
batchRequestKey       opaque UI-generated idempotency token
```

Every selected shop receives the same quantity for that submitted batch.

Do not expose internal `campaignReference` to merchants as customer-facing copy.

## 3. Reuse the one-shop grant primitive

Do not duplicate the transaction/counter/audit algorithm from ADMIN-004.

Extract/reuse a server-side helper so the campaign action invokes the same exact one-shop semantics for each selected shop.

Derive a deterministic per-shop request key from:

```text
batchRequestKey + exact shopId
```

using an existing safe bounded hashing/key convention when necessary.

Retrying the same campaign batch with the same batchRequestKey must not double-grant shops that already succeeded.

## 4. Partial failure semantics

Do not hold a huge cross-shop database transaction open.

Process the bounded target set with per-shop exactly-once grants and return a deterministic result summary:

```text
succeeded
alreadyApplied
failed [{ shopId, bounded reason/code }]
```

A failure for one shop must not roll back successful grants to other shops.

The Admin UI must make partial completion obvious and permit retry with the same `batchRequestKey`, so already-applied shops are idempotent no-ops and failed shops can be attempted again.

Do not leak database stack traces or secrets in result details.

## 5. Lifecycle behaviour

Campaign targeting may include shops that are currently non-executable (for example beta merchants pre-provisioned before a verified plan). Their credits are owned/preserved but remain non-spendable until normal ARCH-010 execution gates allow business work.

Do not silently filter FROZEN/NO_CONTRACT/UNINSTALLED shops out after the administrator selected them. Show the lifecycle warning/status before submission instead.

## 6. No automatic expiry or merchant messaging

ARCH-010 campaign grants are lifetime-until-used.

Do not add:

- expiry scheduler;
- automatic revocation;
- Shopify billing action;
- merchant-support/system notification;
- email campaign delivery.

Merchant balance visibility is owned by SHOPIFY-020. Marketing communication can be external or defined in a future architecture.

## Required tests

At minimum prove:

1. only SUPER_ADMIN can submit campaign grants;
2. empty selection is rejected;
3. duplicate shop ids are deduplicated;
4. invalid quantity/reason/campaignReference is rejected;
5. over-bounded batch is rejected rather than silently truncated;
6. each target invokes the accepted one-shop grant semantics;
7. per-shop request key is stable for the same batch+shop;
8. retry does not double-grant previously successful shops;
9. one target failure does not roll back other successful shops;
10. result summary distinguishes success/already-applied/failure;
11. lifecycle-inactive selected shops can still receive preserved credits;
12. no Shopify/App Event call exists;
13. campaignReference is internal Admin metadata, not merchant UI output;
14. no new merchant authentication path is introduced.

Run focused Admin security/action/UI tests, repository-declared typecheck/lint/build/full tests as applicable, and `git diff --check`.

## Non-goals

Do not:

- build campaign scheduling;
- build segmentation rules/analytics;
- build email/WhatsApp marketing delivery;
- add expiration;
- add automatic revoke;
- expose Admin to merchants;
- bypass ADMIN-004 grant logic.

## Stop conditions

Stop and return to `moda_architect` if:

- the current tenant directory cannot supply exact stable shop ids;
- ADMIN-004 has not produced a reusable idempotent server grant primitive;
- a bounded partial-failure workflow would require a new cross-repository queue;
- implementation would require exposing internal Admin campaign metadata to merchants.

## Completion Report

### Status
Not started.

### Files Changed
Populate during implementation.

### Work Completed
Populate during implementation.

### Validation Results
Populate during implementation.

### Git / VCS
Populate canonical isolated worktree/branch/commit/push evidence.

### Architect Review
Pending.
