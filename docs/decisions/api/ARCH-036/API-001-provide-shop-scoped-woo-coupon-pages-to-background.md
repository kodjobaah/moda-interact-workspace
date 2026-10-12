---
id: ARCH-036-API-001
architecture_id: ARCH-036
title: "Provide bounded Woo coupon pages to Background through API-owned read grant"
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: pending
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on: ["ARCH-026-API-008", "ARCH-036-SHARED-003"]
enables: ["ARCH-036-BACKGROUND-001", "ARCH-036-API-003", "ARCH-036-SYSTEM-TEST-001"]
created: 2026-10-12
updated: 2026-10-12
---
# ARCH-036-API-001 — Provide bounded Woo coupon pages to Background through API-owned read grant

## Architecture

- Architecture: `ARCH-036` — `docs/architecture/ARCH-036-shared-commerce-discount-catalogue.md`.
- Coordinator: `moda_architect`; owner: `moda_api` / `moda-interact-api`.
- **Defined but not materialised.** No task branch, dedicated worktree, implementation commit or push has been created.

## Objective

Extend the approved Woo REST read connection with coupon listing and a private, authenticated, shop-scoped page-read operation for Background.

## Context

The API owns Woo outbound REST credentials and private service access. Background will pull *all* coupons through this adapter. Existing database requires no new fields: BACKGROUND-001 maps provider coupon IDs into the required `shopifyDiscountNodeId` field.

## Scope

In `moda-interact-api` extend the API-008 outbound GET allowlist to **`coupons.list`** at canonical `/wp-json/wc/v3/coupons`, with `page` and `per_page` bounds and deterministic `orderby=id&order=asc` where supported. Implement a *private API-to-Background* page operation (proposed `POST /internal/v1/woocommerce/coupons/pages`), independently authenticated as the Background service and scoped to a trusted Shop ID. Only approved API route composition may expose it; verify the route is actually private before claiming completion. Parse Woo coupon response/`X-WP-Total`/`X-WP-TotalPages`, normalise to Shared read-page v1 and enforce response bounds. Add tests with a fake authenticated Woo server and disposable grant fixtures.

## Out of Scope

No WordPress-to-Moda snapshot push, sync begin/page/complete ingestion, coupon DB writes, sync-generation ownership, merchant browser endpoint, generic provider REST proxy, arbitrary origin/URL, new credential store or plugin code.

## Requirements

- Extend only approved `ARCH-026-API-008` read operations with `GET /wp-json/wc/v3/coupons`; whitelist pagination and sort options, bounded bytes/deadlines and no redirects.
- Authenticate a service-to-service private caller and resolve the Shop, current Woo installation and encrypted coupon read grant. No arbitrary URL/path/credential injection or host leakage.
- Validate provider numeric coupon IDs, code, amount, type, dates, usage limits and restrictions; redact secrets/PII. Provider fields are **not** merchant selection state.
- Never set/read `ShopifyDiscount.isAvailable` here; it is a merchant-owned selection flag, not an API list availability flag.
- Missing/contradictory headers, partial pagination or unreachable provider are explicit errors, never successful empty results.

## Work Items

- [ ] Inspect accepted ARCH-026-API-008 and extend GET operation allowlist for bounded coupon list.
- [ ] Implement authenticated internal read-page endpoint/port using Shared read-page schema.
- [ ] Add provider header/JSON parsing and privacy-safe normalisation.
- [ ] Test missing/revoked/wrong-shop grants, forged caller, SSRF, redirect, bounds, provider failures, empty/multiple pages and product-read regressions.
- [ ] Prove private service routing without leaking Woo credentials or expanding public endpoints.

## Interfaces / Contracts

Producer: API-owned `woo.coupons.read-page.v1`; consumer: BACKGROUND-001 through a private authenticated API adapter. Source of trust: ARCH-026 Woo encrypted read grant, **not** Woo plugin installation bearer. No direct Background Woo REST calls or credentials.

## Dependencies

- `ARCH-026-API-008`
- `ARCH-036-SHARED-003`

## Enables

- `ARCH-036-BACKGROUND-001`
- `ARCH-036-API-003`
- `ARCH-036-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Bounded Woo coupon-page response is available only to authorised Background callers.
- [ ] No provider credentials reach Background/React/logs.
- [ ] API response contains provider data, not inferred merchant selection or checkout eligibility.
- [ ] Product-read behavior and authentication remain unchanged.

## Validation

- [ ] API typecheck, lint, focused provider REST/OpenAPI/service-auth tests
- [ ] Fake Woo server tests: single/multi-page, malformed headers, redirects, credential denial/revocation and two-shop isolation
- [ ] Integration proving approved private API-to-Background calling path and `git diff --check`

## Stop Condition

After bounded work, acceptance checks and required validation: document the Completion Report, set the task to `review` and STOP. Do not begin dependent tasks. For `superseded` tasks, do not execute or claim.

## Implementation Notes

Stop if ARCH-026-API-008 or approved internal service-auth infrastructure is unavailable. No implicit credential forwarding or upgrade from product-read allowlist by assumption.

For developer execution, materialise/prepare the canonical `task/<TASK_ID>` parent and implementation worktrees through `/moda_developer_create`; for agent execution use `/moda-task`. Record launcher-resolved paths, start-of-attempt sync, recursive submodule evidence, branch/commit and actual test results. Do not edit shared/default checkouts or domain `_index.md` files.

## Completion Report

### Status

Not Started.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run; task not claimed.

### Deviations

None.

### Assumptions

The executor will verify checkout, actual dependencies, task worktrees and available toolchain at claim time.

### Unresolved Issues

None recorded.

### Architectural Concerns

Stop and return cross-repository, credential, provider compatibility or schema deviations to `moda_architect`.

## Architect Review

### Review Status

Pending.

### Review Notes

Portable revised definition; no implementation submitted or accepted.

### Reviewed Files

Source snapshot and task contract only. No execution files reviewed.

### Validation Reviewed

No implementation tests have run as part of this definition.

### Architecture Conformance

To be determined after implementation review.

### Follow-up

Await real task materialisation, execution, Completion Report and Architect review.
