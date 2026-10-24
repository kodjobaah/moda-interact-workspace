---
id: ARCH-046-API-007
architecture_id: ARCH-046
title: Make the Woo WhatsApp consent write API a thin, bounded persistence boundary
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: ready
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-046-API-001
  - ARCH-045-DATABASE-002
  - ARCH-045-SHARED-002
enables:
  - ARCH-046-API-006
created: 2026-10-24
updated: 2026-10-24
---

# Make the Woo WhatsApp consent write API a thin, bounded persistence boundary

## Architecture

Architecture ID: `ARCH-046`.

Architecture document: `docs/architecture/ARCH-046-woocommerce-whatsapp-consent-gated-recovery.md`.

Coordinator: `moda_architect`.

**Lifecycle:** portable canonical task definition, **defined but not materialised**. The source ZIP permits design/review, not a claim of access to the developer's actual worktrees, Git remotes or integrated API branches. `ready` reflects the three complete prerequisite task states in the 2026-10-24 11:46 workspace snapshot; re-gate with the launcher before implementation. API-006 is a separate previously drafted but absent/unmaterialised handoff in this snapshot; do not require it to exist to start API-007.

### Developer Takeover

The developer explicitly invoked `/moda_developer_create ARCH-046-API-007` for this ready agent-owned task. Execution and completion authority are transferred to the developer; logical ownership remains `assigned_agent: moda_api`, and the task scope, dependencies, acceptance criteria and validation requirements are unchanged. The task remains `ready` at Attempt 0 until canonical launcher preparation verifies prerequisites and durably claims Attempt 1.

## Objective

Make `POST /v1/woocommerce/whatsapp-consent` a minimal authenticated consent/evidence **write** by introducing a small v2 payload and removing redundant billing/installation SQL work, without weakening tenant isolation, ordering, idempotency, durable evidence or authoritative WhatsApp STOP protection.

## Context

Completed `ARCH-046-API-001` implements `woo.whatsapp-consent.v1` and is **not** reopened. In the uploaded `moda-interact-api` snapshot (`moda-interact-workspace-api(20261024-104830).zip`), `src/woocommerce/consent/contract.ts` parses an 11-field `checkoutAction` containing Classic/Blocks mode, nonce/session assertions, checkbox state, field identifier and a second phone. The API cannot independently verify those WordPress facts: the authenticated Woo server must do so. `service.ts` repeats phone canonicalisation against the second phone, performs a billing entitlement query for each nonduplicate GRANT, and issues separate transaction-time Shop and WooCommerceInstallation `FOR SHARE` reads. Those are candidates for simplification.

The real durability/correctness contract is a tenant-authenticated event, an immutable evidence fact and an ordered atomic update of the existing `CustomerPhone`. The PHP producer is outside this API task; **do not break its currently deployed/pending v1 requests**. `ARCH-046-API-006` (shopper proof-backed status read) must wait for this write-contract correction to avoid overlapping changes.

## Scope

- In `moda-interact-api` only, introduce the version discriminator `woo.whatsapp-consent.v2` **on the existing authenticated POST route**. Keep v1 request and response parsing supported during the transition; route both versions to one internally normalised consent-write service, without duplicating database mutation logic.
- Parse only the v2 wire fields specified below. Woo server verifies the active checkout/nonce/session, deliberate grant/withdrawal, canonical billing phone and consent wording **before** authenticating and POSTing to Moda. The hosted API checks payload size/shape and canonical recipient, but does not try to reconstruct WordPress UI semantics.
- Keep merchant/shop identity from the already-authenticated Woo installation; never accept `shopId`, `customerId`, installation status, nonce-verified booleans, `merchantSiteUrl` or another recipient from v2 body. Derive the fixed purpose `WHATSAPP_CHECKOUT_RECOVERY` from the endpoint.
- Remove `requireRecoveryFeature` and its subscription/plan/feature query from the consent write **for both v1 and v2**. Woo decides if the opt-in UI can be offered; the Background recovery-admission/final-send paths remain the authoritative feature/entitlement/consent/STOP gates. An authenticated valid GRANT may be stored even if recovery is currently disabled, but cannot create a recovery or cause a message.
- Combine the in-transaction Shop and WooCommerceInstallation authenticity/active-state checks into **one indexed SQL JOIN/read with appropriate row locking**, preserving the credential-version/status/revocation/tenant checks across rotation and revocation races. Keep initial request authentication; the recheck is intentionally not eliminated.
- Retain one short, synchronous PostgreSQL transaction for unique event deduplication, one unambiguous shop/active-phone lookup or creation, current consent revision/decision sequencing, current phone update, and one immutable `commerce.WhatsAppConsentEvidence` insertion. Do not add Redis, BullMQ, external I/O, LLM, Meta, billing or recovery work in this route.
- Update the existing API-owned docs, OpenAPI example/fixtures and focused unit/PostgreSQL tests. Record observed query count and latency/transaction timing before and after, without asserting an invented capacity benchmark.

## Out of Scope

- No WooCommerce PHP/JS producer edits, WordPress checkout UI or Classic/Blocks capture changes. An independently owned Woo producer adoption task is required before v1 can be retired; API-007 must not mark that migration complete.
- No shopper status/read implementation (`ARCH-046-API-006`), no changes to completed API-001, no new database table/migration or Shared package contract without an architect-approved gap.
- **No redesign of decision ordering or retry time policy in this task.** In particular do not replace ordering with arrival time, drop the five-minute GRANT freshness guard, accept future-dated events, remove per-recipient/event locks or weaken ambiguous-match/source-conflict behaviour without a separately reviewed correctness design and concurrency tests.
- No cosmetic refactor of unrelated Woo routes, billing services, feature preferences, checkout recovery orchestration, WhatsApp STOP processing, or generic infrastructure/telemetry.

## Requirements

**Minimal v2 transport (exact wire contract):**

```json
{
  "schemaVersion": "woo.whatsapp-consent.v2",
  "eventId": "a-stable-unique-consent-event-id",
  "decision": "GRANT",
  "canonicalPhone": "447400123456",
  "occurredAt": "2026-10-24T10:00:00.000Z",
  "disclosure": {
    "version": "moda.woo.whatsapp-recovery-marketing.v3",
    "locale": "en-GB",
    "text": "Send me WhatsApp shopping updates, reminders and offers."
  }
}
```

- Required top-level keys are **exactly** `schemaVersion`, `eventId`, `decision`, `canonicalPhone`, `occurredAt`, `disclosure`. `decision` is `GRANT` or `REVOKE`; `disclosure` must be populated for GRANT and `null` for REVOKE. Preserve the existing size/identifier/locale/version/text/timestamp bounds, strict JSON decoding and no-store responses. `canonicalPhone` remains **digits-only E.164**, matching the existing persisted `CustomerPhone.whatsappCanonicalPhone`; validate/canonicalise it **once** with the published Shared identity utility (using `+` + digits as its input if needed). Do not accept a second `serverObservedPhone` or `verifiedCountryCode` in v2.
- v2 has **no** `purpose`, `checkoutAction`, `checkoutKey`, `checkoutMode`, `source`, `fieldId`, `selection`, `userInitiated`, `nonceVerified`, `sessionVerified`, `merchantSiteUrl`, `shopId` or `customerId`. Woo is solely responsible for establishing an explicit server-observed customer action and attaching the exact displayed text. The authenticated installation establishes shop/merchant attribution; API does not search disclosure prose for the merchant name or URL.
- The API must **still** enforce authenticated active Woo installation/shop tenancy, a bounded well-formed canonical phone, a deliberate *decision as asserted by the authenticated Woo server*, stable event identity, disclosure evidence for GRANT, and durable per-phone ordering. These are inexpensive and/or correctness-critical; removing fake attestations is not permission to trust anonymous browser input.
- Preserve `woo.whatsapp-consent.v1` behaviour during rollout, **except for the explicitly approved removal of its grant-time feature-eligibility query**; keep prior v1 digest/idempotency semantics for in-flight retry. Do not transform a persisted v1 retry into a different v2 payload using the same `eventId`. New v2 events must use distinct stable event IDs; same `(shopId,eventId)` with differing content or schema remains a replay conflict.
- Continue to reject older decisions, concurrent stale grants, ambiguous active phone matches and conflicting evidence; duplicate identical `(shopId,eventId)` must return its original acknowledged revision/sequence even after a later REVOKE or feature disable. Preserve independent `whatsappNoContact`/`CUSTOMER_STOP` fields and all STOP non-override guarantees. Failure must not partially update CustomerPhone or evidence.
- Keep the existing provider-observed timestamp/monotonic revision rules, **including v1/v2 grant freshness and future-date rejection**, unless a later architecture task explicitly replaces them with a robust multi-tab/multi-device ordering protocol. The API may report a clock-skew limitation in the Completion Report but cannot silently trade withdrawal safety for permissiveness.
- Preserve the existing explicit route errors (unauthorized, invalid input, conflict, unavailable) and safe structured logging; never log raw phone, event ID, disclosure text, credentials or sensitive payloads. A consent ACK is issued **only after commit**, and an outage cannot turn an unacknowledged consent into permission.

## Work Items

- [ ] Map current v1 request → internal decision and add v2 parse → **same** decision; keep the existing authenticated route and type-safe response contract.
- [ ] Move WordPress-only attestation interpretation out of the v2 contract; derive shop and purpose in the API. Validate one canonical recipient and exact disclosure evidence; preserve strict body-size/header protections.
- [ ] Remove consent-write feature-eligibility query for v1/v2, without modifying Background feature/STOP admission and send checks or granting recovery work.
- [ ] Consolidate in-transaction installation/shop recheck to one equivalent locking JOIN query; do not remove initial installation authentication, event/phone serialisation or durable transaction.
- [ ] Update API OpenAPI/docs/fixtures and add unit/PostgreSQL regression tests for the contract, auth, tenancy, duplicate retry, races and no new side effects.
- [ ] Record baseline/new SQL operation counts (fresh GRANT, existing GRANT, REVOKE, duplicate retry), transaction duration and failure outcomes in the Completion Report, using the disposable PostgreSQL harness. Keep metrics cardinality low and do not add duplicate framework HTTP telemetry.

## Interfaces / Contracts

- Producer: authenticated `moda-interact-woocommerce` PHP plugin (currently v1). Consumer: `moda-interact-api` on `POST /v1/woocommerce/whatsapp-consent`. API-007 owns the **new v2 HTTP** definition; the Woo producer must adopt it under a separate Woo-owned task. No new Shared Redis contract or queue schema.
- `woo.whatsapp-consent.v2` fields and semantics are specified under Requirements above; `REVOKE` uses the same envelope with `decision: "REVOKE"` and `disclosure: null`. `eventId` must be stable for retry; `occurredAt` is the verified server-observed Woo decision time and retains existing safe ordering guards. Merchant ID and fixed purpose are server-derived.
- Result shape remains `{schemaVersion, status: "recorded" | "duplicate", decision, consentRevision, decisionSequence}`; the schema version equals the **accepted request version**. Preserve BIGINTs as decimal strings. Do not return full phone, PII, evidence details or secret material.
- Database writes continue to use `commerce.Customer`/`CustomerPhone` and immutable `commerce.WhatsAppConsentEvidence` under the published schema from `ARCH-045-DATABASE-002`; runtime phone validation uses published `@modainteract/moda-interact-shared/identity`. Other services read current CustomerPhone state, not this HTTP event.
- Producer compatibility: API must accept both v1 and v2 during migration. A future Woo-owned adoption task, after API-007 acceptance, switches the publisher and its golden request fixtures; a separate architect decision is required to remove v1 support.

## Dependencies

- `ARCH-046-API-001` (existing, complete; do not reopen)
- `ARCH-045-DATABASE-002` (existing schema, complete)
- `ARCH-045-SHARED-002` (published canonical identity helper/fixtures, complete)

## Enables

- `ARCH-046-API-006` (previously drafted proof-backed shopper status lookup; NOT materialised in the supplied snapshot, to be defined/materialised separately and gated on completed API-007)
- A **future separately materialised WooCommerce producer v2 adoption task**, not implemented or claimed by API-007.

## Acceptance Criteria

- [ ] v2 HTTP request with only the six top-level fields succeeds for valid authenticated GRANT/REVOKE; WordPress attestation fields, merchant URL and duplicate phone are not required or accepted in v2. v1 remains accepted for in-flight producer compatibility.
- [ ] Initial installation authentication and **one** equivalent transaction-time shop/installation locking query both enforce tenant, active status, installed credential version and revocation, including in-flight rotate/revoke races.
- [ ] No `Subscription`, `BillingPlan`, `BillingPlanFeature`, `Feature` or `ShopFeaturePreference` query executes on consent write for either version; feature-disabled consent evidence is passive, with no recovery/send/billing side effects.
- [ ] Same event replay is idempotent with identical prior ACK; changed-body/same-ID, cross-shop evidence, ambiguous existing phones, conflicting sources, late GRANT, newer REVOKE and concurrent STOP cannot corrupt current permission or remove no-contact restrictions.
- [ ] Consent state and **one immutable evidence row** commit together; SQL failure rolls both back. The API does no external network, queue, worker scheduling, customer outreach or billing inside the write.
- [ ] The same status/decision/revision sequence result is returned for equivalent successful v1/v2 *new* events, and v1 old-event replay remains compatible. Unknown/malformed versions are rejected without falling back to weaker parsing.
- [ ] Evidence from a fresh v2 GRANT remains queryable by the later proof-backed API-006 reader via the existing `(shopId,eventId,canonicalPhone,customerPhoneId,phoneConsentRevision)` keys; no status-read identity shortcut is introduced.
- [ ] Focused test suite and disposable PostgreSQL races pass; query counts/transaction timings are reported as **measured**, with no unverified performance claim or new `_index.md` changes.

## Validation

- [ ] `npm run test:arch046-woo-consent:unit` (v1 regression, v2 parse/route; extend existing suite).
- [ ] `npm run test:arch046-woo-consent:postgres` (disposable PostgreSQL; extend tests for revoke/GRANT races, idempotency, feature-disabled grant, STOP and auth credential rotation).
- [ ] `npm run typecheck` and `npm run lint` (declared scripts in inspected API package) plus applicable existing OpenAPI fixture validation.
- [ ] `git diff --check` and source diff review for no incidental schema, Woo, Background, Shopify or `_index.md` edits.

## Stop Condition

After Work Items, Acceptance Criteria and required Validation are complete, record launcher-resolved dedicated **parent and API implementation worktrees**, their start-of-attempt synchronization and recursive database submodule evidence, update only this task's execution/Completion Report fields, set `status: review`, return to `moda_architect`, and **STOP**. Never start API-006 or Woo producer migration implicitly. If a missing cross-repository contract or new schema dependency is discovered, report it rather than modifying another repository.

## Implementation Notes

**Files to inspect/change, if appropriate:** `src/woocommerce/consent/contract.ts`, `request.ts`, `routes.ts`, `service.ts`, authenticated installation helper under `src/auth/woo-installation/`, `docs/arch046-woo-consent-http.md`, `docs/openapi/arch046-woo-consent-v1.yaml` (extend/version; do not break v1), `tests/unit/woocommerce/consent/*.test.ts`, `tests/integration/woocommerce/consent/*.postgres.test.ts`, `tests/contracts/woocommerce/consent/*.json`, and the existing consent PostgreSQL runner. Update composer route registration only if existing v2 dispatch cannot reuse it. Actual file names/scripts must be rechecked against the prepared implementation branch before edit.

**Suggested design:** parse a versioned transport envelope into a common server-side value, then run the single current consent transaction; do not fork v1/v2 database workflows. The existing v1 event digest may depend on JSON serialisation: preserve its exact replay behaviour, including structural keys and fields. A JOIN can replace separate locked Shop and installation reads, but row-lock equivalence (including credential-revocation race) is mandatory. Do **not** remove both advisory locks merely because a unique evidence index exists: reason about first-insert concurrent event/phone behaviour before proposing such a separate optimisation.

**Performance boundary:** removing a few constant-time TypeScript checks will not meaningfully improve capacity; avoid extra PostgreSQL round trips, contention and repeated synchronous billing joins. Measure SQL operations and lock waiting in the consent workload. Do not invent a target throughput or claim low p95 from unit tests; if a reliable before/after load test is unavailable, report that limitation clearly.

**Ownership:** `moda_api` implements only API code/tests/docs in this task plus its task Completion Report. `moda_architect` owns parent architecture, dependencies and indexes. No updates to `docs/decisions/**/_index.md` until the developer explicitly closes the architecture session. Only use `@modainteract/moda-interact-shared/logging` for Node structured diagnostics; no competing logger. Follow `docs/agent-vcs-ownership-policy.md` and `docs/agent-worktree-isolation-policy.md`, and use the canonical launcher for task preparation.

## Completion Report

### Status

Not Started — portable definition, not materialised, claimed, committed or pushed in the developer's environment.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run; implementation not started.

### Deviations

None.

### Assumptions

Uploaded API snapshot is representative of the implementation branch; live branch integration and the completed prerequisite versions must be reverified at launch.

### Unresolved Issues

WooCommerce v2 producer adoption remains a **separate, as-yet-undefined task**. API-007 must retain v1 acceptance until that transition is agreed and validated.

### Architectural Concerns

Moving feature eligibility out of the consent write explicitly changes the current API-001 policy: an authenticated GRANT may be recorded while a feature is disabled. No recovery or send is permitted without the independent Background gates. Any proposal to relax chronological guards or durable locking must return to the architect for its own ordering design.

## Architect Review

### Review Status

Pending.

### Review Notes

No implementation reviewed.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Not assessed.

### Follow-up

Define the repository-owned WooCommerce v2 producer adoption task before removing v1 or claiming end-to-end v2 coverage.
