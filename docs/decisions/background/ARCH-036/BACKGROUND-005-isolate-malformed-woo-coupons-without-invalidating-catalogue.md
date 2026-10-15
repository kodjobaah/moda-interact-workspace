---
id: ARCH-036-BACKGROUND-005
architecture_id: ARCH-036
title: Isolate malformed individual Woo coupons without invalidating the catalogue
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: ready
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on: ["ARCH-036-BACKGROUND-001"]
enables: []
created: 2026-10-15
updated: 2026-10-15
---

# ARCH-036-BACKGROUND-005 — Isolate malformed individual Woo coupons

## Architecture

- Parent: `docs/architecture/ARCH-036-shared-commerce-discount-catalogue.md`.
- This is a bounded follow-up to completed `ARCH-036-BACKGROUND-001`; it does **not** reopen the accepted dispatcher, lease, queue, credential or pagination designs.
- Owner: `moda_background`, repository `moda-interact-background`; coordinator: `moda_architect`.
- Portable task definition only; **not yet materialised or claimed**. The dependency has been reported complete.

## Observed defect

A Render Background scan for WooCommerce shop `cmv9kgh2b0000poammusu116y` completed successfully at `2026-10-15 13:21:18.624`, then a later run set `ShopifyDiscountCatalogue.status=ERROR` and `lastErrorCode=invalid_coupon` although previously valid coupons remained. `normalizeWooCoupons()` currently maps all items with throwing `normalizeWooCoupon()`; **one malformed individual item fails the entire otherwise complete catalogue**. API-002 consequently rejects catalogue GET with `catalogue_not_current`, hiding valid coupons.

## Objective

After a **complete, authentic, consistent WooCommerce response**, reconcile all usable coupon records and keep `ShopifyDiscountCatalogue` `CURRENT` even if some individually malformed but reliably identified coupons must be quarantined. Retain fail-closed handling for **untrustworthy catalogue-wide data** (missing or ambiguous provider identity, duplicates, incomplete/unstable pages, transport or grant failures).

## Scope and invariants

- Change only the Woo coupon normalisation/reconciliation path and focused tests in `moda-interact-background`.
- Preserve the full-page read invariants, HTTPS/DNS-pinning and credential checks, PostgreSQL per-shop `activeSyncToken`/`syncGeneration` fencing, generation ordering and two-successful-scan removal semantics.
- Do not write `ShopifyDiscount.isAvailable` for Woo records, in success, quarantine, expiry or failure paths. Existing merchant checkbox selections must survive.
- Keep Shopify sync semantics unchanged (`isAvailable` continues to mean Shopify provider availability).
- No new database tables, columns, migrations, API endpoints, background schedulers or CommerceAgent behaviour; do not change `docs/decisions/**/_index.md`.

## Required behaviour

1. **Global integrity first:** the paginated Woo response must still be fully retrieved and verified; the returned list must have unique, stable, positive provider coupon IDs. A missing/invalid/duplicated ID is a catalogue-wide failure because absence/removal cannot be determined safely. Likewise reject incomplete, unstable or contradictory pagination and unusable grants.
2. **Per-item quarantine:** for an item with a valid unique provider ID but malformed or unsafe *individual* content (e.g., blank/control-character code, malformed amount, invalid restrictions or timestamp), continue processing the other coupons. Do not invent a redeem code, money value or eligibility.
3. **Previously stored malformed item:** if `woo:coupon:<provider-id>` already exists, mark that Woo row `providerStatus=UNSUPPORTED`, `fixedSelectable=false` and seen in the **current successful generation**; preserve `isAvailable`, the internal row ID, FK/history, and avoid writing PII. A subsequent valid scan may restore ACTIVE eligibility while retaining merchant selection.
4. **Never-stored malformed item:** if an item has a valid provider ID but cannot be safely represented under existing mandatory fields/constraints (including an invalid code), do not create a fabricated selectable discount row. Still count its observed ID as present for reconciliation/removal safety. An unsupported-but-well-formed zero-value coupon follows the existing normaliser and remains representable as `UNSUPPORTED`.
5. **Correct removal:** a coupon present in the provider response but quarantined must **not** count as absent in either the first or second successful missing scan. Only genuinely absent identities advance the existing two-successful-complete-miss removal rule. Provider outages and incomplete scans never count as success/misses.
6. **Catalogue state:** once valid rows and known malformed identities are atomically accounted for under the current token/generation fence, commit `CURRENT` and `lastSuccessfulSyncAt`. A mixed scan can contain zero usable coupons; this alone is not a transport failure.
7. **Observability:** structured counters for total observed, normalised, individually rejected/quarantined, and reason-code aggregates. Never log provider bodies, arbitrary codes, customer PII or credentials. Do not emit misleading `scanned`/`skipped` totals from unrelated snapshots.

## Implementation guidance

Keep item classification separate from transactional writes: return the safe set of normalised rows **and** observed provider IDs with bounded per-item issue codes; don't swallow structural identity errors. Reconcile valid rows, pre-existing quarantined rows, and true absences in one fenced transaction. Prefer existing fields (`providerStatus`, `fixedSelectable`, `lastSeenSyncGeneration`, `lastSyncedAt`) to schema changes. Avoid making a failed scan look successful through blanket catch-and-continue.

## ASCII workflow

```text
Woo full paginated GET  ── fails/unstable ──> ERROR (no writes/misses)
          |
          v
validate IDs: positive, unique, trustworthy
          | invalid/missing/duplicate ID ──> ERROR (no writes/misses)
          v
  ┌───────────────────────────┬─────────────────────────────┐
  | valid individual coupon   | malformed with valid ID     |
  v                           v                             |
normalise normally        quarantine existing row           |
                            as UNSUPPORTED                  |
                          (or skip unsafe new row)          |
  └───────────────────────────┴─────────────────────────────┘
                          |
                          v
 fenced atomic reconcile + true-missing detection
                          |
                          v
           CURRENT; preserve isAvailable
```

## Acceptance criteria

- [ ] A mixed complete scan with five valid coupons and one malformed, identified coupon produces `CURRENT` and makes the five valid coupons visible to API-002's catalogue query.
- [ ] A previously saved malformed coupon keeps its `isAvailable` flag and FK/history but is no longer selectable; it cannot be marked REMOVED merely because normalisation rejected it.
- [ ] A never-stored malformed item with valid ID does not create a synthetic selectable row; correcting it later makes it appear normally.
- [ ] Duplicate/missing/invalid provider IDs, incomplete pagination and an invalid read grant still fail the whole scan with no partial writes or false removals.
- [ ] Two verified complete absences remove a genuinely absent coupon, including sequences interleaved with malformed-but-present and failed scans.
- [ ] Recovery from a previous catalogue `ERROR` works without resetting merchant selections or altering the scheduler.

## Required validation

- [ ] Focused normaliser tests covering blank code, malformed date, invalid numeric amount, zero-value supported-shape UNSUPPORTED, duplicate IDs and missing identity.
- [ ] Disposable PostgreSQL catalogue-reconciliation tests for mixed valid/invalid data, generation bookkeeping, two-miss removal, stale-owner fencing, atomic rollback and merchant-selection persistence.
- [ ] Run the existing ARCH-036 Woo catalogue/dispatch PostgreSQL-Redis suites, unit tests, typecheck/build and `git diff --check`; record exact commands and results.
- [ ] Provide structured evidence of the `ERROR -> CURRENT` recovery for the affected behaviour; never claim a live Render test without running it.

## Stop condition

After validated bounded implementation, submit the developer Completion Report and set the task to `review`; return to `moda_architect`. No automatic next-task execution, no unrelated source changes, and no `_index.md` changes.

## Completion Report

### Status

Not started; portable definition only.

### Files Changed

None in application source.

### Work Completed

None.

### Validation Results

Not run by implementation executor.

### Deviations

None recorded.

### Unresolved Issues

None yet; actual malformed field(s) in the live Woo response have not been independently identified.

## Architect Review

### Review Status

Pending implementation evidence.
