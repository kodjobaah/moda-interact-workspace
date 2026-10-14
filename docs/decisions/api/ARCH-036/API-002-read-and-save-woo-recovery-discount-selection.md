---
id: ARCH-036-API-002
architecture_id: ARCH-036
title: "Read and save Woo coupon selections using existing discount flags"
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: ready
priority: 45
executor: null
claimed_at: null
attempt: 1
depends_on: ["ARCH-036-BACKGROUND-001"]
enables: ["ARCH-036-WOOCOMMERCE-003", "ARCH-036-SYSTEM-TEST-001"]
created: 2026-10-12
updated: 2026-10-14
---

# ARCH-036-API-002 — Read and persist Woo merchant coupon selections

## Architecture

- Architecture ID: `ARCH-036`.
- Parent: `docs/architecture/ARCH-036-shared-commerce-discount-catalogue.md`.
- Coordinator: `moda_architect`.
- Materialised on parent branch `task/ARCH-036-API-002`; attempt 1 was claimed by the developer. The canonical parent and implementation worktrees exist at the launcher-resolved paths. The implementation worktree is clean and its task branch commit is published.

## Objective

Provide shop-authorised paginated **active** Woo coupon listing and atomic merchant-owned multi-checkbox selection using existing `ShopifyDiscount.isAvailable` and the existing `ShopSettings.fixedShopifyDiscountId` FK. No database migration.

## Architecture clarification — 14 October 2026

The developer explicitly chose to keep provider eligibility and merchant checkbox ownership separate. This decision **supersedes** the task's earlier requirement for revision-CAS and provider-eligibility checks on PUT. `GET /discount-catalogue` remains restricted to successfully synchronised, current eligible coupons; on PUT, check only authenticated shop identity, actual Woo row ownership, request bounds and existing SQL/FK constraints. Background never writes Woo `isAvailable`. Historical Attempt 1 review findings remain recorded below, but the first two require review against this clarified design rather than implementing contrary behaviour. The search/start-date predicate defect remains a required correction. This clarification changes no task lifecycle fields or dependencies.

## Context


For **WooCommerce records only**, `isAvailable=true` means selected by the merchant; for Shopify it retains its existing provider-availability meaning. Provider status, fixedSelectable, dates and catalogue freshness decide which coupons appear. The API reads the existing catalogue maintained by BACKGROUND-001 and writes selected flags plus the **real internal** `ShopSettings.fixedShopifyDiscountId` anchor to satisfy unchanged FIXED SQL checks. The API does **not** retrieve Woo coupon pages from the provider, determine which coupon to offer, or prove checkout eligibility. Neither offer execution nor CommerceAgent is in this session.

## Scope

Implement versioned paginated GET `/v1/merchant/discount-catalogue` and GET/PUT `/v1/merchant/discount-offers` on existing models. Authenticate and verify the Woo Shop, serialize merchant Saves with a Shop-row lock, and atomically update **one Woo Shop's flags, mode and anchor**. The Save is a full-set replacement with last-writer-wins semantics; a returned read revision is informational, not a Save precondition. A Save checks the identity and same-Shop ownership of selected Woo rows, **not** their provider status, expiry, selectable flag or catalogue generation/status. Allow 1–50 selected coupon row IDs in FIXED; the bound is an API validation rule, not new DDL.

## Out of Scope

- No new PostgreSQL discount/coupon catalogue, selection, sync staging or join **tables**; reuse existing physical `ShopifyDiscountCatalogue`, `ShopifyDiscount`, policy and attempt records.
- No other repository's implementation, incidental feature work, migration-history rewrite, or `_index.md` modification.
- No new unsupported coupon promises, billing changes or checkout mutation.
- No implementation of tasks listed under Enables; return to the architect at the defined stop point.

## Requirements


- Catalogue GET lists all shop-scoped CURRENT, ACTIVE, fixedSelectable, in-date, supported positive-value coupons with bounded stable pagination/search, **including unchecked** rows; checked state comes from `isAvailable`. A missing, stale or non-current catalogue is not an empty successful catalogue.
- Authenticated Woo installation uses the existing PHP privileged WordPress REST boundary; no browser-to-Moda hosted direct call and no new Shared data-schema dependency. Define the endpoint's own versioned OpenAPI contract in `moda-interact-api`.
- PUT validates the full set of existing same-Shop Woo internal row IDs (1–50 for FIXED) and atomically persists `isAvailable`, mode and FK anchor under a Shop-row lock. Reject foreign or unknown IDs, but **do not** reject merchant selections because the coupon has expired, been removed, is unselectable or absent from the latest generation; those are Background-owned provider facts. The merchant may Save while a later Background scan is active or unavailable; the successful initial sync remains a gate for GET catalogue browsing. All writes are constrained to `Shop.platform=WOOCOMMERCE`. Only the merchant-selection API writes Woo selected flags; provider sync never auto-selects or clears them.
- For FIXED use one **deterministically chosen real selected same-Shop `ShopifyDiscount.id`** (e.g. minimum internal ID) as existing `fixedShopifyDiscountId` FK compatibility anchor; it is not the customer-facing coupon choice. For NONE/AI clear the anchor as the current SQL CHECK requires; dormant selected flags may be retained. Shopify's single-FK setting and Admin override are unchanged. A last-coupon removal while FIXED is rejected unless mode changes.
- Idempotent identical Saves, serialized concurrent Saves (last writer wins), and denied/invalid/revoked installations must not partially update rows or write across tenants. Report conflicts for actual transactional/identity failures, not for a changed catalogue generation. A policy Save is not coupon applicability proof.
- No additional HTTP proxy/proof API, Shared schema, Prisma migration, customer-sensitive data, or cross-tenant selection write.

## Work Items

- [ ] Implement shop-authorised CURRENT active-coupon catalogue read with cursor/page metadata and selected flags.
- [ ] Implement one transactional Woo-only full-set Save updating `isAvailable`, mode and real-row FK anchor under Shop lock, without catalogue freshness/generation checks on Save.
- [ ] Test serialized last-writer-wins Saves, concurrent scan/save preserving provider facts and checkbox ownership, repeated calls, mode switching, last-coupon selection removal, invalid/foreign IDs, permitted previously removed/unavailable selections, Shopify isolation and unchanged delay/follow-up.
- [ ] Verify legacy SQL FIXED FK/CHECK constraints and existing Shopify API behavior using a migrated disposable PostgreSQL database.

## Interfaces / Contracts


API-owned versioned GET `/v1/merchant/discount-catalogue` and GET/PUT `/v1/merchant/discount-offers`, authenticated Woo installation and existing WordPress REST facade. Existing `ShopSettings` and `ShopifyDiscount` only. **No new Shared contract or provider REST read/proof endpoint.**

## Dependencies


- `ARCH-036-BACKGROUND-001` — complete, current normalized coupons needed for listing and selection.

## Enables


- `ARCH-036-WOOCOMMERCE-003`
- `ARCH-036-BACKGROUND-003`
- `ARCH-036-SYSTEM-TEST-001`

## Acceptance Criteria

- [x] Multiple Woo checkbox flags are written and returned in the save projection; the PostgreSQL test saves and reads a multi-selection.
- [x] `FIXED` save satisfies existing SQL checks using a real referenced selected discount ID; no fake FK or new schema.
- [x] NONE/AI clear the compatibility FIXED anchor and persist the requested mode; no outbound offer behaviour is implemented or asserted.
- [ ] Unknown/foreign IDs are rejected atomically; valid same-Shop historical Woo IDs can remain selected regardless of Background provider availability.
- [ ] Merchant full-set Saves are serialized under Shop lock (last-writer-wins) and preserve effective Admin override; Shopify settings untouched.

## Validation

- [ ] Focused API contract/route/unit tests and OpenAPI checks.
- [ ] Disposable PostgreSQL existing-constraint, serialized Save, same-Shop identity/foreign-shop and GET search/date predicate cases; verify no schema migration needed.
- [ ] Declared API typecheck/lint/test/build and `git diff --check`.

## Stop Condition

After the bounded work, Acceptance Criteria and required Validation are complete, update the Completion Report, set the task to `review`, return to `moda_architect`, and STOP. Do not start dependent tasks or write `_index.md`.

## Implementation Notes


Implement only Woo merchant-facing catalogue read and selection persistence. Background owns the provider coupon-list sync; send-time proof and CommerceAgent are outside this session. Preserve current policy delay/follow-up and admin override without introducing false discount eligibility claims. Use the API repository's own contract tests and real existing-schema PostgreSQL concurrency/FK checks.

## Completion Report

### Status

Changes Requested — Developer attempt 1 reviewed on 2026-10-14. The implementation is committed and published, but required revision-CAS and eligibility behavior is missing. The task is returned to `ready`; attempt remains 1.

### Files Changed

- `openapi/woocommerce-discount-offers-v1.yaml`
- `package.json`
- `scripts/test-arch036-discount-offers-postgres.mjs`
- `src/index.ts`
- `src/merchant/discount-offers/contract.test.ts`
- `src/merchant/discount-offers/contract.ts`
- `src/merchant/discount-offers/routes.test.ts`
- `src/merchant/discount-offers/routes.ts`
- `src/merchant/discount-offers/service.postgres.test.ts`
- `src/merchant/discount-offers/service.ts`
- `src/woocommerce/installation/routes.ts`

### Work Completed

- Added versioned Woo merchant catalogue and offers endpoints, installation-authenticated route handling, pagination/search contract, persistence of Woo `isAvailable` flags, recovery mode and a real selected-discount FK anchor.
- Added OpenAPI, contract, route and PostgreSQL coverage. The service preserves the Shopify discount row and existing delay/follow-up fields in the tested save path.
- Implementation commit `b628a54a1fafe471834ff0e814f5bf43faa7bcaf` is present on and matches `origin/task/ARCH-036-API-002`. The implementation worktree is clean.
- No implementation schema migration or parent-workspace submodule pointer change was made. No assigned-agent assistance was used.

### Validation Results

- `npm exec -- tsx --test src/merchant/discount-offers/contract.test.ts src/merchant/discount-offers/routes.test.ts src/merchant/discount-offers/service.postgres.test.ts`: 4 passed; the database test skipped without its opt-in URL.
- `npm run test:arch036-discount-offers:postgres`: 1 passed against a disposable PostgreSQL database after applying all 39 existing migrations. It verifies the real FK/CHECK anchor and selected-row/Shopify isolation, but does not exercise concurrent CAS or scan/save races; it currently asserts that stale/ineligible saves succeed.
- `npm test`: 239 passed, 42 skipped, 0 failed. The skipped tests are opt-in database tests.
- `npm run typecheck`, `npm run lint`, and `npm run build`: passed.
- OpenAPI parsing/contract checks passed as part of the focused tests. `git diff --check` remains to be run on the implementation branch after corrections.

### Deviations

The implementation treats the GET revision as informational and removes it from PUT, contrary to the task's required optimistic revision. It also permits selection saves during catalogue sync/outage and for removed/unselectable coupons. The new contract and PostgreSQL tests encode that contrary behavior. Catalogue search can also bypass the start-date filter because the search `OR` replaces the eligibility `OR`.

### Assumptions

Attempt 1 was reviewed from the canonical implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-036-API-002` and parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-036-API-002`; both were clean at review. Both use `task/ARCH-036-API-002`. The parent task branch contains the claim commit and is 11 commits ahead, 0 behind its task remote; the implementation branch is one commit ahead of `origin/main` and its task commit is published.

### Unresolved Issues

- PUT has no submitted revision precondition. `offerRevision` is documented as informational, `parseSaveDiscountOffers` rejects `expectedRevision`, and the service never compares `ShopSettings.updatedAt` plus catalogue state/generation under the Shop lock. A stale draft or concurrent scan can therefore be silently saved.
- PUT validates selected IDs only by same-Shop Woo identity. It accepts removed, unavailable, expired, unselectable, wrong-generation coupons and saves while the catalogue is syncing or unavailable. Revalidate the current catalogue snapshot and requested coupon eligibility transactionally; stale/conflicting saves must fail atomically.
- Search combines title/code with an `OR` that overwrites the eligibility start-date `OR`; future-start coupons matching search can appear. Compose the predicates without replacing date eligibility.
- PostgreSQL tests must cover stale/missing revision, conflicting concurrent saves, concurrent scan/save, stale/ineligible IDs, atomic rollback and search/date interaction. Replace tests that currently codify revision-free and stale-catalogue saves.

### Architectural Concerns

No schema, cross-service, provider-proof or scope expansion was observed. Keep the implementation within existing tables and preserve the real FK/CHECK anchor behavior already verified.

## Architect Review

### Review Status

Pending architect review. Developer self-review for attempt 1 requests changes; no architect acceptance or developer completion decision has been recorded.

### Review Notes

See the attempt 1 developer self-review below. The current implementation is not ready for architect acceptance.

### Reviewed Files

The 11 implementation files listed in the Completion Report, plus the task definition and current canonical worktree/branch state.

### Validation Reviewed

Typecheck, lint, build and full unit suite passed. The disposable PostgreSQL test passed its implemented assertions, but does not validate the required CAS/concurrency contract and currently encodes behavior that must change.

### Architecture Conformance

Partial. The API remains Woo-scoped and uses existing models/constraints, but save revision/freshness and coupon-eligibility semantics do not conform to the task.

### Follow-up

Developer must claim attempt 2 after the corrections are committed and the task is ready. Then rerun required focused validation and request review.

## Developer Self-Review - Changes Requested

### Reviewed Attempt

Attempt 1, developer execution. Review date: 2026-10-14. The attempt is not accepted.

### Required Corrections

1. Restore a required revision precondition on PUT. The submitted revision must cover `ShopSettings.updatedAt` and catalogue status/generation/update state. Under the Shop lock, compare it with the current state and reject stale or conflicting writes without changing coupon flags, mode or anchor. Keep the transaction atomic and return the documented conflict/unavailable response.
2. Revalidate requested selection IDs against the current, complete catalogue snapshot under transaction protection. Reject foreign, removed, expired, unavailable, unselectable and stale-generation rows; do not allow a save to report success during an active sync or unavailable/stale catalogue. Preserve any allowed dormant-selection behavior for NONE/AI without treating stale incoming IDs as newly valid selections.
3. Fix catalogue search predicate composition so title/code matching is ANDed with all eligibility predicates. Add a matching future-start coupon and prove it is excluded both with and without search.
4. Replace the revision-free and save-during-sync expectations in contract/service tests. Add PostgreSQL tests for stale revision, two conflicting concurrent saves, scan/save generation races, invalid eligibility and rollback/no partial writes; retain FK/CHECK and Shopify-isolation coverage.

### State Transition

`status: ready`, `executor: null`, `claimed_at: null`, `attempt: 1`. Attempt 2 is not created by this review; the next developer claim increments the attempt exactly once.
