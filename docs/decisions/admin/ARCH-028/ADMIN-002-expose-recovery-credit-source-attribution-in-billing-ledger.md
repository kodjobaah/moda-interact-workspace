---
id: ARCH-028-ADMIN-002
architecture_id: ARCH-028
title: Expose exact recovery-credit source and purchase in Admin billing audit
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-010-DATABASE-002
  - ARCH-010-DATABASE-007
  - ARCH-010-DATABASE-009
  - ARCH-010-DATABASE-014
  - ARCH-028-DATABASE-001
enables: []
created: 2026-10-22
updated: 2026-10-22
---

# ARCH-028-ADMIN-002 — Expose exact recovery-credit source and purchase in Admin billing audit

## Architecture

Architecture: `docs/architecture/ARCH-028-whatsapp-delivery-failure-convergence.md`.
Coordinator: `moda_architect`. Owner: `moda_admin` / `moda-interact-admin`.
**Portable canonical definition; defined but not materialised** in the developer's parent/implementation task worktrees.

## Objective

Allow an authorised Moda platform administrator to inspect a recovery conversation's committed billing usage and determine, from its **persisted attribution**, whether it consumed a paid billing-period allowance, lifetime free credits, a specific purchased-credit lot, or a promotional grant—and whether the charge was subsequently compensated.

## Context

The existing Admin Billing > Events list and event drawer are driven by:

- `src/lib/admin/billing.ts`: `billingLedgerSelect`, `billingLedgerProjection`, `getBillingLedger`, `getBillingLedgerItem`.
- `src/lib/admin/types.ts`: `BillingLedgerItem`.
- `src/components/admin/billing-overview.tsx` and `src/components/admin/billing-drawers.tsx`.
- `src/app/(protected)/billing/page.tsx` (existing `view=events`, `eventId` detail).

The current event projection omits `UsageEvent.sourceType`/`sourceId` and the committed/compensated `UsageReservation` source links. The authoritative schema already provides `UsageEvent.committedReservation` and `compensatedReservation`, `UsageReservation.purchasedCreditPurchaseId`, period counter, Shop entitlement counter, promotional grant ID and `RecoveryCreditPurchase`. The current `Conversation` model has no direct billing-source column. The implementation must not pretend that every `UsageEvent` is a recovery charge, or that a credit-pack *purchase/acquisition* UsageEvent is a *spend* event.

## Scope

- Extend the **existing** Admin Billing > Events list/detail read model and drawer, reusing current authorisation, pagination, filters and localisation.
- For `RECOVERY_CONVERSATION` usage, present the persisted `UsageEvent` category/source ID plus the exact linked reservation ID, source key, quantity, status and original committed UsageEvent identity. Show compensation event/reason/disposition where present; distinguish **reserved**, **committed**, **compensated** and **unattributed/unavailable** without treating reservations as charges before commitment.
- Resolve source category **from persisted reservation ownership**, never from the merchant's current plan or available balances: exact purchased-credit purchase ID (even where a purchased reservation also has `counterId`); paid billing-period entitlement/counter; lifetime-free Shop entitlement; promotional grant. Show purchase ID/status (and a safe link to existing Admin pack detail) only for the actual linked purchase, not some other currently-active pack.
- Where the canonical `sourceKey` demonstrably identifies a `RecoveryOutreachAttempt` for the **same shop**, show the verified attempt, recovery and conversation IDs in the event drawer when the relationship exists. Require exact validated lineage; otherwise show `Unknown/unavailable` rather than guessing from phone, most-recent conversation or arbitrary parsing. An existing correlation can be used without adding a foreign key.
- Resolve ordinary/compensation/correction `UsageEvent` associations explicitly using the existing Prisma relations, including negative events and cases where the originating reservation is not available. Use bounded Prisma select/include or batch loads; avoid per-row unbounded N+1 queries.
- Add focused server projection, permission, edge-case and UI tests for this read-only audit capability.

## Out of Scope

- New billing ledger/table, migrations, new database columns or changing accounting source-selection priority.
- Editing reservation/usage events, credit purchases, corrections or monetary refund flows.
- Merchant-facing billing/Recovery Detail UI, public APIs, or new navigation.
- New Background credit-commit structured logging (owned by `moda_background`, not `moda_admin`). Durable PostgreSQL provenance, not operational logs, is the accounting source of truth; separately request a Background telemetry task only if a specific operational log is approved.
- Broad conversation search, historical inference of deleted purchase records, or changing ARCH-028 `131026` policy.

## Requirements

1. Keep `requirePlatformAdminRead()` and all server-side internal Admin access controls. Do not expose cross-shop provenance in tenant applications or embed personal phone/message content in the audit.
2. Use **immutable IDs actually present in the usage/reservation lineage**. For purchased reservations, `counterId + purchasedCreditPurchaseId` is a valid paired source and MUST classify as `PURCHASED` rather than `LIFETIME_FREE` or invalid; the specific purchase ID must be shown.
3. For a compensated charge show the original commitment and the compensating event distinctly; never present a restored/held/historical-only credit as though its status were an uncorrected charge.
4. Other UsageEvent metrics and purchase-acquisition UsageEvents retain their existing presentation, with `Not applicable`/`Unavailable` rather than fabricated recovery attribution.
5. Preserve existing ledger pagination, order, state/date/shop filters, detail open/close behaviour and retry controls. A row's source detail must not require loading all shop purchases or all conversations.
6. Prefer the existing Admin i18n conventions for headings/source labels, including unambiguous purchased/paid/free/promotional/unknown states.

## Work Items

- [ ] Confirm precise Prisma event/reservation/correction/purchase relations against the pinned database client; identify the safe event-to-outreach correlation path before implementing.
- [ ] Extend the Admin billing read-model select/projection and `BillingLedgerItem` contract with optional provenance fields and bounded cross-shop-safe resolution.
- [ ] Render source category, reservation/source IDs, exact purchase ID/link, compensation and safe recovery/attempt/conversation correlation in the existing Billing Events drawer (and a compact source indication in the list if readable).
- [ ] Add permission, pagination, source-classification, purchase-lot, compensation and non-recovery regression tests.
- [ ] Record exact files and validation evidence in the Completion Report; stop after this bounded Admin capability.

## Interfaces / Contracts

- Read-only: `billing.UsageEvent`, `billing.UsageReservation`, `billing.RecoveryCreditPurchase`, `billing.BillingPeriodEntitlementCounter`, `billing.ShopEntitlementCounter`, `billing.PromotionalCreditGrant`, `commerce.RecoveryOutreachAttempt`, `commerce.CheckoutRecovery`, `whatsapp.Conversation` as applicable and authorised.
- Existing internal Prisma client and Admin read model are the interface. No Shared package changes or provider calls.
- Source ownership (original database tasks): `ARCH-010-DATABASE-002/007/009/014`; ARCH-028 compensation provenance: `ARCH-028-DATABASE-001`.

## Dependencies

- `ARCH-010-DATABASE-002` — Complete, paid period allowance counter.
- `ARCH-010-DATABASE-007` — Complete, purchased credit lot accounting.
- `ARCH-010-DATABASE-009` — Complete, promotional credit ledger.
- `ARCH-010-DATABASE-014` — Complete, purchase lifecycle/provenance.
- `ARCH-028-DATABASE-001` — Complete, durable compensation/source linkage.

## Enables

None; this is a separately reviewable, read-only Admin audit improvement. Do not gate an already-running ARCH-028 compensation task or the original terminal-recipient system test on this presentation change.

## Acceptance Criteria

- [ ] An Admin can inspect one recovery commit and identify paid period / lifetime free / **exact purchased lot ID** / promotional grant from persisted references, together with the correct attempt/recovery/conversation where verifiable.
- [ ] A purchased reservation that holds both the purchased counter ID and purchase ID is shown as purchased; multiple merchant purchases cannot cross-attribute the spend.
- [ ] Compensation and correction evidence is visible and does not appear as a new paid conversation or erase the original source.
- [ ] Absent/legacy/ambiguous associations display unavailable; non-recovery usage and acquisition events are not misclassified.
- [ ] Existing access control, filters, pagination, event retry action and tenant safety remain intact; no new write/ledger behaviour.

## Validation

- [ ] Focused Admin billing query/projection tests (four funding sources, compensated, multiple purchases, and missing links).
- [ ] Admin billing table/drawer component tests and authorisation/non-recovery regression.
- [ ] Run relevant declared Admin repository typecheck, lint and test commands; inspect `package.json` before choosing commands.
- [ ] `git diff --check` and task worktree/branch evidence in Completion Report.

## Implementation Notes

The `UsageEvent.sourceType/sourceId` strings alone are not always sufficient to resolve a purchased lot. Follow the **committed or compensated reservation relation** to `purchasedCreditPurchaseId`. A purchased reservation legitimately has its Shop purchased-counter FK **and** its lot FK; never use “exactly one non-null capacity FK” as a category discriminator. Do not infer a purchase from its acquisition UsageEvent or merchant's most recent pack. For source-key-derived outreach linking, fail closed if the format or same-Shop ownership cannot be proven; do not make the parser a new cross-service runtime contract merely for UI display.

## Stop Condition

After the scoped Admin read-model/UI changes and focused validation, set `review`, supply Completion Report to `moda_architect`, and STOP. Do not change Background or Database code.

## Completion Report

### Status

Not Started.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

Existing Prisma relations are present in the pinned Admin database client; verify before implementation.

### Unresolved Issues

None identified in task definition.

### Architectural Concerns

Report any missing immutable provenance or cross-repository schema gap; do not add a shadow ledger.

## Architect Review

### Review Status

Pending.

### Review Notes

Awaiting implementation and real worktree evidence.

### Reviewed Files

Not applicable before implementation.

### Validation Reviewed

Not applicable before implementation.

### Architecture Conformance

Pending implementation.

### Follow-up

None.
