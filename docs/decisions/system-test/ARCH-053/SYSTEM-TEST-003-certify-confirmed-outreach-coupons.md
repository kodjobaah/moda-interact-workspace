---
id: ARCH-053-SYSTEM-TEST-003
architecture_id: ARCH-053
title: Certify confirmed outreach coupons with original Woo coupons and recovery links
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 95
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-052-SHARED-012
- ARCH-053-SHARED-003
- ARCH-053-SYSTEM-TEST-001
- ARCH-053-SYSTEM-TEST-002
- ARCH-053-API-003
- ARCH-053-WOOCOMMERCE-008
- ARCH-053-BACKGROUND-003
- ARCH-053-BACKGROUND-004
- ARCH-053-WOOCOMMERCE-003
- ARCH-052-BACKGROUND-008
- ARCH-048-BACKGROUND-011
- ARCH-046-WOOCOMMERCE-003
enables: []
created: 2026-10-30
updated: 2026-10-31
---

# ARCH-053-SYSTEM-TEST-003 — Certify confirmed outreach coupons with original Woo coupons and recovery links

## Architecture

`ARCH-053` — `docs/architecture/ARCH-053-woocommerce-checkout-recovery-links-and-cart-restoration.md`, coordinated by `moda_architect`. Defined but **not materialised**; no branch, worktree, commit, push or acceptance is claimed.

## Objective

Independently certify original-coupon + confirmed outreach-coupon restoration end-to-end across the *real* WooCommerce checkout runtime (Classic and Blocks), authenticated API, the provider-confirmed WhatsApp receipt, recovery generations and native discount validity/stacking.

## Context

SYSTEM-TEST-001 certifies recovery-link/basket fundamentals and SYSTEM-TEST-002 certifies **original** coupons. This terminal task covers **ARCH-052-recommended checkout discounts** interacting with them. The source of the recommendation is the recorded *confirmed initial outbound message*, not ARCH-052's current merchant settings or the immutable original snapshot. No new services or database objects are created by this test task.

## Scope

Only `moda-interact-system-test`: create a bounded scenario suite under the existing integration harness, e.g. `test/scenarios/arch053-outreach-coupon-restore.test.js`, supporting fixtures in `test/fixtures/arch053-outreach-coupon/`, and test-runner configuration **only if required by existing scripts**. Use existing local test orchestration and provider mocks; do not edit WooCommerce/API/Background source.

## Out of Scope

No production Meta sends, coupon issuance, CommerceAgent model selection, reimplementation of Woo coupon rules in fixtures, independent API auth, migration or broad system-harness rewrite.

## Requirements

### Multi-discount Woo checkout-restoration certification — 30 October 2026

Exercise `woo.restore.resolve.v1` with confirmed initial CHECKOUT_OFFERS group (2..3 items) and original customer coupon set, plus original single, automatic, alternative and no-offer branches. Assert only confirmed initial source-grounded codes are returned, read-only API remains tenant/generation safe, customer confirm is required, current Woo native coupon stacking determines every result, and a partial/expired/unverifiable group never silently removes original coupons or claims guaranteed savings. Verify explicit 10-minute nonce/session/cart-hash group choice, rollback of a partially applied group, changed merchant setting after confirmed send, retry/idempotency, Classic and Blocks **storefront-silent failure handling**, optional non-error conflict choice and true totals. No v2 resolver or checkout-link generation in ARCH-052.


- Test API-003 actual authenticated **single v1** resolver request/response, with the mandatory `outreachOffer` union; no v2 resolver is accepted. Invalid/expired/superseded/tenant-mismatched link never returns basket or offer.
- Test a real sequence-one `RecoveryOutreachAttempt.sentAt + outboundMessageId` joined to a provider-confirmed `ConversationMessage` carrying approved `recoveryPromise` and explicit `promotionTarget`; no message, unconfirmed, failed, untagged, corrupt, wrong-recovery and wrong-tenant receipts never produce a checkout code. Test DB outage separately (503, not 200 NONE).
- Test original coupon and outreach code combinations in both WC Classic and Blocks; expected truth is **actual Woo validation and recalculated cart**, with no Moda failure banners or plugin-triggered Woo error notices. Test ordinary shopper-entered coupon errors separately to prove they are not suppressed.
- Test coupon expiry after abandonment and again between first restore and explicit switch; `SAVE10` expired / `EXTRA15` valid should apply only `EXTRA15`, and vice versa. Usage exhaustion, minimum subtotal, item restriction, unknown code and individual-use must be represented.
- Test conflict UI default: never silently remove original codes; the **opt-in nonce-protected switch** revalidates offered code. Session-only choice expires/invalidates after 10 minutes/cart change/order/new restore. Client cannot supply replacement code or recovery ID.
- Test `CHECKOUT_AUTOMATIC` does not force coupons or claim a saving; `ALTERNATIVE_PRODUCT` does not insert product or coupon into the original checkout; no confirmed offer results in no extra coupon; corrupt confirmed receipt yields only a private redacted diagnostic; it never generates a storefront error notice.
- Test link previews and GET are non-mutating, explicit confirmation POST and one final checkout activity only; cross-device restore binds original checkoutKey. ARCH-048 closes old recovery and creates new generation on genuine further abandonment; old generation's URL cannot overwrite it. No arbitrary cross-generation cap.
- Test duplicate webhook, API retry, double-click, simultaneous phones, order completion, consent/STOP and the final outbound send gates; no double billing or message. No coupon/token/PII logged. Require private diagnostic evidence for real errors and no Moda-generated storefront error notices.
- All test tasks are **terminal**: this one may depend on implementation, publication, consent and ARCH-048 tasks, but no implementation depends on it. Run only after all prerequisites are Complete and architect-accepted and the developer manual verification checkpoint has been offered.

### Repository / execution safeguards

- Read `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, the launcher preparation packet and the parent ARCH-053 architecture before claiming. Work from dedicated, synchronized mirrored task worktrees; record both physical paths, initial SHAs and validation in the Completion Report. A snapshot does not establish the developer's current branch/status.
- Only change the **permitted owning-repository files** in Scope and this task's own authorised task metadata/Completion Report. No `_index.md`, no unrelated code, no other agent's task, no production WhatsApp activation, no merge/push to `main`.
- Hosted Node services use `@modainteract/moda-interact-shared/logging`; merchant-hosted WooCommerce PHP uses existing private PHP diagnostics, **never this npm export**. Preserve original safe errors/relevant response details for diagnosis but redact tokens, full URLs, coupon values and PII; no Moda-originated error, exception or debug output on the merchant storefront. Retry-owning jobs still surface failures for retries.
- Keep checkout restoration read-only in the hosted API and cart-local in WooCommerce. Never have PHP query Moda PostgreSQL/Redis or an API handler change a visitor cart. Never create a new discount, extend an expired coupon, use ARCH-052 discovery code, bypass merchant consent/STOP/order/final provider gates or impose a cross-generation outreach cap.
- When the specified receipt/provider contract is absent, conflicting or untestable, **stop and return the gap to moda_architect**; do not invent an approximation, copy a Shared schema locally or broaden the task to another repo. System-test tasks are terminal and may not gate implementation tasks.


## Work Items

- [ ] Build two merchant fixtures, generation-1+generation-2 recovery fixtures, confirmed outbound receipt fixtures and current Woo original/recommended coupons.
- [ ] Exercise single offer-aware v1 API response, signed-link authorization, confirmed receipt and coupon application on Classic and Blocks with current live Woo rules.
- [ ] Exercise all invalid/expired/conflicting/revoked/automatic/alternative/no-offer and unverified-receipt paths plus customer choice.
- [ ] Exercise cross-device, scanner GET, replay, wrong-tenant, generation, STOP/order and telemetry redaction; record a scenario-to-evidence matrix.

## Interfaces / Contracts

- Consumes published `WooRestoreResolveRequestV1Schema`, `WooRestoreResolveResponseV1Schema`, `WooRestoreOutreachOfferV1Schema` from SHARED-001 and `WooCartRestoreSnapshotV1Schema` from SHARED-001.
- Produces **no** runtime contract; test fixtures must match real API/Background/WordPress wire and current Woo store APIs.

**Mandatory evidence matrix (every row in Classic and Blocks unless API-only):**

| Original basket coupons | Confirmed outreach | Current provider state | Expected result |
|---|---|---|---|
| `SAVE10` | `EXTRA15` checkout CODE | both stack | both applied, current total |
| `SAVE10` | `EXTRA15` checkout CODE | original expired | offer applied, original rejected privately, no storefront error |
| `SAVE10` | `EXTRA15` checkout CODE | offer expired | original retained, offer rejected privately, no storefront error |
| `SAVE10` | `EXTRA15` checkout CODE | individual-use conflict | original remains; explicit choice available |
| `SAVE10` | `EXTRA15` checkout CODE | user opts in; offer valid | native recompute; original removed only by choice |
| `SAVE10` | `EXTRA15` checkout CODE | offer expires before opt-in | originals safely restored, private error evidence only |
| no coupons | checkout AUTOMATIC | eligible / ineligible | no fabricated code or guaranteed-savings claim |
| `SAVE10` | ALTERNATIVE_PRODUCT code | any | no promoted product/code applied to old basket |
| `SAVE10` | NO_OFFER | any | original attempted only |
| `SAVE10` | corrupt confirmed receipt | any | no offered code, private UNVERIFIABLE diagnostic, original attempted |
| `SAVE10` | checkout CODE promised | new generation supersedes link | link refused, no cart overwrite |
| `SAVE10` | checkout CODE promised | message pending/failed/no provider ID | no offered code supplied |

Run additional negative tests for post-only offer fields, failed bearer, mismatched installation, duplicate nonce submits, scanner GET, tampered session and unbounded log payloads. Record test command/output and screenshots for real WC Blocks.

## Dependencies

- `ARCH-053-SYSTEM-TEST-001` — core recovery-link system certification accepted.
- `ARCH-053-SYSTEM-TEST-002` — original coupon system certification accepted.
- `ARCH-053-API-003` — accepted confirmed message offer resolver.
- `ARCH-053-WOOCOMMERCE-008` — accepted private-outcome handling and optional non-error choice implementation.
- `ARCH-053-BACKGROUND-003` — accepted generation-bound checkout URL issuance.
- `ARCH-053-BACKGROUND-004` — accepted proven initial sent offer target evidence, or architect-documented supersession.
- `ARCH-053-WOOCOMMERCE-003` — accepted manual unchanged-cart return activity.
- `ARCH-052-BACKGROUND-008` — accepted dynamic discount outreach send integration; test does not change it.
- `ARCH-048-BACKGROUND-011` — accepted generation closure/worker integration.
- `ARCH-046-WOOCOMMERCE-003` — accepted returning consent capture.

## Enables

None — terminal system certification.

## Acceptance Criteria

- [ ] Confirmed checkout discount from WhatsApp is applied only if Woo currently accepts it; original coupons remain faithfully handled.
- [ ] Expired/rejected outreach codes leave accurate recalculated Woo totals and valid original coupons intact, with **no Moda-generated error or Woo notice triggered by automatic attempts**; protected diagnostics record the actual outcome.
- [ ] A real Classic and a real Blocks checkout demonstrate a working explicit stacking choice, with replay protection.
- [ ] No alternative-product discount, unverified receipt, automatic offer or stale generation causes an unsupported checkout code to apply or a Moda diagnostic to appear in storefront HTML, redirects, Woo session notices or browser console.
- [ ] One authenticated v1 API contract; invalid version/token/tenant never leaks original basket or offer.
- [ ] GET preview and old link cannot mutate; valid cross-device confirmation queues one real resumption event.
- [ ] No duplicate WhatsApp send/billing, changed recovery history, poisoned logs or unauthorised code issuance.
- [ ] Completion Report contains command/environment/scenario/evidence matrix; no app source edits by system-test agent.

## Validation

- [ ] Run system-test repository declared `npm test` / relevant scenario runner; `npm run typecheck` for JS syntax if test sources changed
- [ ] Run WordPress Classic + Blocks with real coupon configuration and mock Meta provider / API / Background / Postgres / BullMQ integration
- [ ] Run replay, failure injection, auth and no-PII-log assertions; `git diff --check`

## Stop Condition

When all defined Work Items, Acceptance Criteria and Validation are satisfied, update only this task's authorized metadata and Completion Report, set `status: review`, return to `moda_architect` and **STOP**. Do not begin Enabled tasks, self-accept, create new tasks, modify a sibling repository or merge/push main.

## Implementation Notes

A passing test does not enable live WooCommerce WhatsApp sending. Only architect review may mark this task Complete. Report any missing cross-boundary capability as a new owning-agent defect rather than implementing it in system-test.

## Completion Report

### Status

Not Started — portable task definition, not claimed.

### Files Changed

None.

### Work Completed

Not Started.

### Validation Results

Not run. Report exact commands, results and any environment blockers after execution.

### Deviations

None.

### Assumptions

Defined from the 2026-10-30 uploaded snapshot. Re-read current task and repository HEAD after launcher preparation.

### Unresolved Issues

None claimed resolved. See explicit dependency/receipt gates above.

### Architectural Concerns

Escalate contract or ownership gaps instead of inventing a new transport or persistence location.

## Architect Review

### Review Status

Pending

### Review Notes

Not reviewed.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

To be assessed after implementation.

### Follow-up

None.
