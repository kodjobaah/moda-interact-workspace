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
status: review
priority: 20
executor: null
claimed_at: null
attempt: 2
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

**Lifecycle:** Attempt 1 was returned to `ready` after self-review identified missing rollback, API-006 proof-key, and comparative timing evidence. Attempt 2 was claimed by the canonical launcher at `2026-10-24T14:54:35Z` and passed developer self-review. The parent claim commit `de0542ed41ccbedad1c9189b712011cea902792a` is published. The launcher preparation packet records the canonical parent task worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-046-API-007` and implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-046-API-007`; both were reused, already current with their task remotes and `origin/main`. Recursive database submodule sync/init passed at `508a89463ccb24dcc31e5f38e04be8cfd10ad690`. Implementation commit `b1ccf7842d1a6d732d900676d6e8c4250977b707` is published. Task is now `review`, Attempt 2, with cleared claim fields. `completion_mode: developer` remains in force; explicit developer completion is pending.

### Developer Takeover

The developer explicitly invoked `/moda_developer_create ARCH-046-API-007` for this ready agent-owned task. Execution and completion authority are transferred to the developer; logical ownership remains `assigned_agent: moda_api`, and the task scope, dependencies, acceptance criteria and validation requirements are unchanged. The launcher claimed Attempt 1, as reflected in the pre-review task metadata. The developer has supplied implementation and validation evidence for review; final completion is not implied.

## Objective

Make `POST /v1/woocommerce/whatsapp-consent` a minimal authenticated consent/evidence **write** by introducing a small v2 payload and removing redundant billing/installation SQL work, without weakening tenant isolation, ordering, idempotency, durable evidence or authoritative WhatsApp STOP protection.

## Context

Completed `ARCH-046-API-001` implements `woo.whatsapp-consent.v1` and is **not** reopened. In the uploaded `moda-interact-api` snapshot (`moda-interact-workspace-api(20261024-104830).zip`), `src/woocommerce/consent/contract.ts` parses an 11-field `checkoutAction` containing Classic/Blocks mode, nonce/session assertions, checkbox state, field identifier and a second phone. The API cannot independently verify those WordPress facts: the authenticated Woo server must do so. `service.ts` repeats phone canonicalisation against the second phone, performs a billing entitlement query for each nonduplicate GRANT, and issues separate transaction-time Shop and WooCommerceInstallation `FOR SHARE` reads. Those are candidates for simplification.

The real durability/correctness contract is a tenant-authenticated event, an immutable evidence fact and an ordered atomic update of the existing `CustomerPhone`. **Pre-production breaking change approved 2026-10-24:** there are no existing Moda customers; the API may remove v1 parsing without a dual-version migration. The Woo publisher is outside this task and must adopt v2 before integrated checkout consent is deployed. `ARCH-046-API-006` (shopper proof-backed status read) must wait for this write-contract correction to avoid overlapping changes.

## Scope

- In `moda-interact-api` only, make `woo.whatsapp-consent.v2` the **sole accepted transport** on the existing authenticated POST route. Remove the legacy v1 parser/types/examples and its WordPress attestation fields. Do not add dual-version routing or transitional adapters.
- Parse only the v2 wire fields specified below. Woo server verifies the active checkout/nonce/session, deliberate grant/withdrawal, canonical billing phone and consent wording **before** authenticating and POSTing to Moda. The hosted API checks payload size/shape and canonical recipient, but does not try to reconstruct WordPress UI semantics.
- Keep merchant/shop identity from the already-authenticated Woo installation; never accept `shopId`, `customerId`, installation status, nonce-verified booleans, `merchantSiteUrl` or another recipient from v2 body. Derive the fixed purpose `WHATSAPP_CHECKOUT_RECOVERY` from the endpoint.
- Remove `requireRecoveryFeature` and its subscription/plan/feature query from the v2-only consent write. Woo decides if the opt-in UI can be offered; the Background recovery-admission/final-send paths remain the authoritative feature/entitlement/consent/STOP gates. An authenticated valid GRANT may be stored even if recovery is currently disabled, but cannot create a recovery or cause a message.
- Combine the in-transaction Shop and WooCommerceInstallation authenticity/active-state checks into **one indexed SQL JOIN/read with appropriate row locking**, preserving the credential-version/status/revocation/tenant checks across rotation and revocation races. Keep initial request authentication; the recheck is intentionally not eliminated.
- Retain one short, synchronous PostgreSQL transaction for unique event deduplication, one unambiguous shop/active-phone lookup or creation, current consent revision/decision sequencing, current phone update, and one immutable `commerce.WhatsAppConsentEvidence` insertion. Do not add Redis, BullMQ, external I/O, LLM, Meta, billing or recovery work in this route.
- Update the existing API-owned docs, OpenAPI example/fixtures and focused unit/PostgreSQL tests. Record observed query count and latency/transaction timing before and after, without asserting an invented capacity benchmark.

## Out of Scope

- No WooCommerce PHP/JS producer edits, WordPress checkout UI or Classic/Blocks capture changes. An independently owned Woo v2 producer task is required **before end-to-end consent can work**; the existing Woo v1 publisher is intentionally incompatible with this breaking API correction.
- No shopper status/read implementation (`ARCH-046-API-006`), no changes to completed API-001, no new database table/migration or Shared package contract without an architect-approved gap.
- **No redesign of decision ordering or retry time policy in this task.** In particular do not replace ordering with arrival time, drop the five-minute GRANT freshness guard, accept future-dated events, remove per-recipient/event locks or weaken ambiguous-match/source-conflict behaviour without a separately reviewed correctness design and concurrency tests.
- No cosmetic refactor of unrelated Woo routes, billing services, feature preferences, checkout recovery orchestration, WhatsApp STOP processing, or generic infrastructure/telemetry.

## Requirements

**Exclusive v2 transport (exact wire contract):**

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
- **Breaking rollout:** reject v1 requests as invalid (`400`); v2 is the only accepted transport. No production in-flight v1 retries or existing user consent evidence require compatibility. Same `(shopId,eventId)` with differing v2 content remains a replay conflict; a repeat of the same v2 event returns its original result.
- Continue to reject older decisions, concurrent stale grants, ambiguous active phone matches and conflicting evidence; duplicate identical `(shopId,eventId)` must return its original acknowledged revision/sequence even after a later REVOKE or feature disable. Preserve independent `whatsappNoContact`/`CUSTOMER_STOP` fields and all STOP non-override guarantees. Failure must not partially update CustomerPhone or evidence.
- Keep the existing provider-observed timestamp/monotonic revision rules, **including v2 grant freshness and future-date rejection**, unless a later architecture task explicitly replaces them with a robust multi-tab/multi-device ordering protocol. The API may report a clock-skew limitation in the Completion Report but cannot silently trade withdrawal safety for permissiveness.
- Preserve the existing explicit route errors (unauthorized, invalid input, conflict, unavailable) and safe structured logging; never log raw phone, event ID, disclosure text, credentials or sensitive payloads. A consent ACK is issued **only after commit**, and an outage cannot turn an unacknowledged consent into permission.

## Work Items

- [x] Remove v1 parsing/types and accept only the six-field v2 request on the existing authenticated route; preserve the typed acknowledgement.
- [x] Move WordPress-only attestation interpretation out of the v2 contract; derive shop and purpose in the API. Validate one canonical recipient and exact disclosure evidence; preserve strict body-size/header protections.
- [x] Remove consent-write feature-eligibility query for v2, without modifying Background feature/STOP admission and send checks or granting recovery work.
- [x] Consolidate in-transaction installation/shop recheck to one equivalent locking JOIN query; do not remove initial installation authentication, event/phone serialisation or durable transaction.
- [x] Update API OpenAPI/docs/fixtures and add unit/PostgreSQL regression tests for the contract, auth, tenancy, duplicate retry, races and no new side effects.
- [x] Record baseline/new SQL operation counts (fresh GRANT, existing GRANT, REVOKE, duplicate retry), transaction duration and failure outcomes in the Completion Report, using the disposable PostgreSQL harness. Keep metrics cardinality low and do not add duplicate framework HTTP telemetry.

## Interfaces / Contracts

- Producer: authenticated `moda-interact-woocommerce` PHP plugin (currently v1). Consumer: `moda-interact-api` on `POST /v1/woocommerce/whatsapp-consent`. API-007 owns the **new v2 HTTP** definition; the Woo producer must adopt it under a separate Woo-owned task. No new Shared Redis contract or queue schema.
- `woo.whatsapp-consent.v2` fields and semantics are specified under Requirements above; `REVOKE` uses the same envelope with `decision: "REVOKE"` and `disclosure: null`. `eventId` must be stable for retry; `occurredAt` is the verified server-observed Woo decision time and retains existing safe ordering guards. Merchant ID and fixed purpose are server-derived.
- Result shape remains `{schemaVersion, status: "recorded" | "duplicate", decision, consentRevision, decisionSequence}`; the schema version equals the **accepted request version**. Preserve BIGINTs as decimal strings. Do not return full phone, PII, evidence details or secret material.
- Database writes continue to use `commerce.Customer`/`CustomerPhone` and immutable `commerce.WhatsAppConsentEvidence` under the published schema from `ARCH-045-DATABASE-002`; runtime phone validation uses published `@modainteract/moda-interact-shared/identity`. Other services read current CustomerPhone state, not this HTTP event.
- Producer compatibility: no v1 compatibility required in this pre-production rollout. The separately owned Woo task must switch its publisher and golden fixtures to v2 before end-to-end tests. Do not claim producer integration as part of API-007.

## Dependencies

- `ARCH-046-API-001` (existing, complete; do not reopen)
- `ARCH-045-DATABASE-002` (existing schema, complete)
- `ARCH-045-SHARED-002` (published canonical identity helper/fixtures, complete)

## Enables

- `ARCH-046-API-006` (previously drafted proof-backed shopper status lookup; NOT materialised in the supplied snapshot, to be defined/materialised separately and gated on completed API-007)
- A **future separately materialised WooCommerce producer v2 adoption task**, not implemented or claimed by API-007.

## Acceptance Criteria

- [x] The six-field v2 request succeeds for valid authenticated GRANT/REVOKE; v1 and all extra WordPress attestation, merchant URL, browser identity or duplicate phone fields are rejected.
- [x] Initial installation authentication and **one** equivalent transaction-time shop/installation locking query both enforce tenant, active status, installed credential version and revocation, including in-flight rotate/revoke races.
- [x] No `Subscription`, `BillingPlan`, `BillingPlanFeature`, `Feature` or `ShopFeaturePreference` query executes on the v2 consent write path; feature-disabled consent evidence is passive, with no recovery/send/billing side effects.
- [x] Same event replay is idempotent with identical prior ACK; changed-body/same-ID, cross-shop evidence, ambiguous existing phones, conflicting sources, late GRANT, newer REVOKE and concurrent STOP cannot corrupt current permission or remove no-contact restrictions.
- [x] Consent state and **one immutable evidence row** commit together; SQL failure rolls both back. The API does no external network, queue, worker scheduling, customer outreach or billing inside the write.
- [x] v2 events return typed status/decision/revision/sequence fields; identical v2 retries are idempotent. v1 and unknown/malformed schema versions are rejected without fallback.
- [x] Evidence from a fresh v2 GRANT remains queryable by the later proof-backed API-006 reader via the existing `(shopId,eventId,canonicalPhone,customerPhoneId,phoneConsentRevision)` keys; no status-read identity shortcut is introduced.
- [x] Focused test suite and disposable PostgreSQL races pass; query counts/transaction timings are reported as **measured**, with no unverified performance claim or new `_index.md` changes.

## Validation

- [x] `npm run test:arch046-woo-consent:unit` (v2 parse/route, explicit v1 rejection, security regression).
- [x] `npm run test:arch046-woo-consent:postgres` (disposable PostgreSQL; extend tests for revoke/GRANT races, idempotency, feature-disabled grant, STOP and auth credential rotation).
- [x] `npm run typecheck` and `npm run lint` (declared scripts in inspected API package) plus applicable existing OpenAPI fixture validation.
- [x] `git diff --check` and source diff review for no incidental schema, Woo, Background, Shopify or `_index.md` edits.

## Stop Condition

After Work Items, Acceptance Criteria and required Validation are complete, record launcher-resolved dedicated **parent and API implementation worktrees**, their start-of-attempt synchronization and recursive database submodule evidence, update only this task's execution/Completion Report fields, set `status: review`, return to `moda_architect`, and **STOP**. Never start API-006 or Woo producer migration implicitly. If a missing cross-repository contract or new schema dependency is discovered, report it rather than modifying another repository.

## Implementation Notes

**Files to inspect/change, if appropriate:** `src/woocommerce/consent/contract.ts`, `request.ts`, `routes.ts`, `service.ts`, authenticated installation helper under `src/auth/woo-installation/`, `docs/arch046-woo-consent-http.md`, `docs/openapi/arch046-woo-consent-v2.yaml` (replace legacy v1 spec), `tests/unit/woocommerce/consent/*.test.ts`, `tests/integration/woocommerce/consent/*.postgres.test.ts`, `tests/contracts/woocommerce/consent/*.json`, and the existing consent PostgreSQL runner. Update composer route registration only if existing v2 dispatch cannot reuse it. Actual file names/scripts must be rechecked against the prepared implementation branch before edit.

**Suggested design:** parse only v2 into one server-side consent event, then run the existing single consent transaction; avoid dual-version code. There are no production v1 evidence digests to preserve. A JOIN can replace separate locked Shop and installation reads, but row-lock equivalence (including credential-revocation race) is mandatory. Do **not** remove both advisory locks merely because a unique evidence index exists: reason about first-insert concurrent event/phone behaviour before proposing such a separate optimisation.

**Performance boundary:** removing a few constant-time TypeScript checks will not meaningfully improve capacity; avoid extra PostgreSQL round trips, contention and repeated synchronous billing joins. Measure SQL operations and lock waiting in the consent workload. Do not invent a target throughput or claim low p95 from unit tests; if a reliable before/after load test is unavailable, report that limitation clearly.

**Ownership:** `moda_api` implements only API code/tests/docs in this task plus its task Completion Report. `moda_architect` owns parent architecture, dependencies and indexes. No updates to `docs/decisions/**/_index.md` until the developer explicitly closes the architecture session. Only use `@modainteract/moda-interact-shared/logging` for Node structured diagnostics; no competing logger. Follow `docs/agent-vcs-ownership-policy.md` and `docs/agent-worktree-isolation-policy.md`, and use the canonical launcher for task preparation.

## Completion Report

### Status

Attempt 2 passed developer self-review on 2026-10-24. Task state is `review`, with cleared executor/claim fields and Attempt 2 retained. Attempt 1 Changes Requested history is preserved below. Because `completion_mode: developer`, explicit developer completion remains pending.

### Files Changed

**Original implementation** (`220fa2b`, 17 API-owned files):

- `src/woocommerce/consent/contract.ts`
- `src/woocommerce/consent/service.ts`
- `docs/arch046-woo-consent-http.md`
- `docs/openapi/arch046-woo-consent-v1.yaml` (deleted)
- `docs/openapi/arch046-woo-consent-v2.yaml` (created)
- `scripts/test-arch046-woo-consent-postgres.mjs`
- `tests/contracts/woocommerce/consent-grant.v1.json` (deleted)
- `tests/contracts/woocommerce/consent-grant.v2.json` (created)
- `tests/contracts/woocommerce/consent-revoke.v1.json` (deleted)
- `tests/contracts/woocommerce/consent-revoke.v2.json` (created)
- `tests/fixtures/woocommerce/consent/event.ts`
- `tests/integration/woocommerce/consent/races.postgres.test.ts`
- `tests/integration/woocommerce/consent/service.postgres.test.ts`
- `tests/integration/woocommerce/consent/v2.postgres.test.ts` (created)
- `tests/integration/woocommerce/recovery-selection/service.postgres.test.ts`
- `tests/unit/woocommerce/consent/contract.test.ts`
- `tests/unit/woocommerce/consent/routes.test.ts`

**Attempt 2 review corrections** (`b1ccf78`, four API-owned files):

- `docs/arch046-woo-consent-http.md`
- `scripts/test-arch046-woo-consent-postgres.mjs`
- `tests/integration/woocommerce/consent/v2.postgres.test.ts`
- `tests/integration/woocommerce/consent/performance.postgres.test.ts` (new)

No production consent service, database schema/migration, WooCommerce plugin, Background source or `docs/decisions/**/_index.md` file changed in the correction commit. This handoff patch modifies only the existing API-007 task record in the parent workspace.

### Work Completed

- Implemented the **v2-only**, six-field `woo.whatsapp-consent.v2` contract on the existing authenticated POST route; removed v1 and WooCommerce-specific attestation parsing under the agreed pre-production breaking rollout. Installation identity and fixed consent purpose remain server-derived.
- Removed consent-write billing/entitlement reads and consolidated the in-transaction shop/installation locked recheck, retaining atomic CustomerPhone/evidence writes, recipient/event serialisation, chronological ordering, duplicate ACKs and immutable authoritative STOP handling.
- Reconciled consent OpenAPI, API documentation, fixtures, unit, concurrency and PostgreSQL integration tests in original implementation commit `220fa2b`.
- **Attempt 2: rollback proof.** Added a PostgreSQL-test-only `BEFORE INSERT` trigger on `commerce.WhatsAppConsentEvidence` which raises an error *after* the consent service's CustomerPhone mutation. The regression asserts no change to current decision/revision/sequence/evidence for an existing phone and no leaked Customer, CustomerPhone or evidence records when a new phone is involved. The trigger/function are removed in `finally`.
- **Attempt 2: API-006 proof tuple.** Added a real PostgreSQL read matching **all five** `(shopId, eventId, canonicalPhone, customerPhoneId, phoneConsentRevision)` values from a new v2 GRANT, with rejection checks for an incorrect shop and revision. This does not implement the API-006 endpoint or establish shopper identity for that future reader.
- **Attempt 2: performance evidence.** Added an opt-in comparison runner that executes the same scenarios against the pre-API-007 v1 source (`220fa2b^`) and the current v2 code with the disposable migration-current PostgreSQL setup. It logs SQL statements, elapsed time of the Prisma `$transaction` client call, overall scenario wall time, success/rejection and whether a billing table was read. Legacy v1 code exists **only** in the temporary comparison source, not in the deployed API.
- Attempt 2 changes committed as `b1ccf78` and pushed to `origin/task/ARCH-046-API-007`, as shown in the supplied 24 October 2026 terminal recording.

### Validation Results

**Attempt 2 reconciliation rerun (24 October 2026, implementation head `b1ccf7842d1a6d732d900676d6e8c4250977b707`):**

| Check | Observed result |
|---|---|
| `npm run test:arch046-woo-consent:unit` | **6/6 passed**, zero failures. |
| `ARCH046_CONSENT_COMPARE_BASELINE=1 npm run test:arch046-woo-consent:postgres` | **11/11 primary PostgreSQL tests passed**, including the new failure-injection rollback test and API-006 proof-tuple assertions; **1/1 v1 comparison** and **1/1 v2 comparison** passed. |
| Disposable PostgreSQL migrations | 59 migrations applied successfully. |
| `npm run typecheck` | Passed; Prisma Client v6.19.3 generated and `tsc --noEmit` completed without errors. |
| `npm run lint` | Passed (`eslint . --max-warnings=0`), no error output. |
| `git diff --check origin/main...HEAD` | Passed against the published implementation branch. |
| Consent OpenAPI YAML | Parsed successfully with the repository's `yaml` package; OpenAPI `3.1.0` and the expected POST path are present. No dedicated consent OpenAPI test/script is declared in `package.json`. |
| Git commit / push | `b1ccf78` pushed, updating `task/ARCH-046-API-007` from `220fa2b` to `b1ccf78`. |
| Live WordPress and CommerceAgent end-to-end | Not executed; separate WooCommerce v2 producer/system-test ownership. |

**Comparable single-run SQL and timing evidence** (from `ARCH046_CONSENT_COMPARISON` log lines; same scenario harness on v1 and v2):

| Scenario | SQL v1 → v2 | Prisma transaction client ms v1 → v2 | Scenario wall ms v1 → v2 | Outcome v1 / v2 |
|---|---:|---:|---:|---|
| Fresh GRANT | 14 → 12 | 60.30 → 52.04 | 63.69 → 55.49 | recorded / recorded |
| Existing GRANT | 12 → 10 | 27.75 → 25.88 | 28.56 → 26.52 | recorded / recorded |
| REVOKE | 11 → 10 | 24.14 → 26.92 | 24.36 → 27.13 | recorded / recorded |
| Duplicate retry | 8 → 7 | 16.29 → 16.63 | 16.50 → 16.83 | duplicate / duplicate |
| Stale GRANT rejection | 10 → 8 | 23.06 → 17.03 | 23.30 → 17.26 | rejected / rejected |
| Injected evidence-write failure | 12 → 10 | 48.18 → 40.70 | 48.45 → 40.93 | rejected / rejected |

The benchmark captures the *elapsed client time around* Prisma `$transaction(...)`—including transaction initiation, query round trips, locking/commit or rollback, not PostgreSQL-server-only execution. It excludes scenario setup/HTTP work; the separately logged scenario wall duration includes the surrounding service call. These are **single local samples per scenario**, not p95 latency, load/capacity measurements, or proof of sustained throughput. The v1 GRANT and failure scenarios emitted a billing read; v2 emitted no billing read in the comparison scenarios. Failure-outcome measurements were recorded for both stale decision and deliberately injected evidence-insert failure. SQL counts were lower in every comparison; timings were lower in most, but not all scenarios, so no generalized latency-improvement claim is made.

**Review requirements cross-reference:**

1. **Rollback after SQL failure:** satisfied by `v2.postgres.test.ts` evidence-trigger test and passing 11/11 PostgreSQL run.
2. **Five-field API-006 evidence retrieval:** satisfied by `v2.postgres.test.ts` exact tuple query and negative tenant/revision checks.
 3. **Comparable SQL, transaction and failure measurements:** satisfied by `performance.postgres.test.ts`, the opt-in PostgreSQL runner and measured table above. Prisma transaction-client elapsed time is accepted as the transaction-duration measure, with its client/round-trip/commit-or-rollback scope explicitly documented.

### Deviations

- The developer explicitly authorised a pre-production **v2-only breaking change** because there are no existing users. The original transitional v1-compatibility wording was superseded; API-001 remains Complete and is not reopened.
- Attempt 1 implementation was published as `220fa2b`; the three in-scope review corrections were delivered in API-owned commit `b1ccf78`. No unrelated production refactor was added.
- Attempt 2 launcher packet confirms the dependency gate passed for API-001, DATABASE-002 and SHARED-002. Parent and implementation worktrees were reused on `task/ARCH-046-API-007`; remote task fast-forward was `not-needed` and `origin/main` was `already-current` for both. Recursive submodule sync/init passed with database at `508a89463ccb24dcc31e5f38e04be8cfd10ad690`. Claim commit `de0542ed41ccbedad1c9189b712011cea902792a` was committed and pushed.

### Assumptions

- Reconciliation verified implementation HEAD and `origin/task/ARCH-046-API-007` both equal `b1ccf7842d1a6d732d900676d6e8c4250977b707`; the worktree is clean. PostgreSQL, comparison, typecheck, lint, diff and OpenAPI parse validations were rerun against that worktree.
- A test-only database trigger and a pinned historical v1 benchmark are valid means of proving rollback and relative work reduction; neither is introduced into live API behaviour.
- Background admission/send, Meta messaging, WooCommerce checkout integration and future API-006 identity validation are separate ownership boundaries and are not claimed complete by API-007 tests.

### Unresolved Issues

- A separate WooCommerce-owned task must migrate the Woo consent publisher to the v2-only request before end-to-end checkout consent is functional.
- The proof-backed returning-checkout reader `ARCH-046-API-006` remains a separate task and must stay gated until API-007 is actually `complete`.
- The benchmark is one local comparison per scenario; sustained load, p95 and database-server-only execution time remain unmeasured and are not claimed. Prisma `$transaction` client elapsed time is the transaction-duration proxy measured here; it includes client/round-trip/commit-or-rollback time rather than server-only execution.

**The following Attempt 1 Changes Requested record is retained verbatim for audit; its three evidence gaps are addressed above, subject to authorised review.**

### Developer Self-Review - Changes Requested

Attempt 1 was reconciled against the current task definition and the published implementation commit `220fa2b8fe0bc6e74dd88891083fd30572b8cfa7`. Focused validation passed: unit tests **6/6**, disposable PostgreSQL tests **10/10**, `npm run typecheck`, `npm run lint`, and `git diff --check origin/main...HEAD`. The tests cover v2 contract/rejection, auth and tenancy, replay, ordering/races, STOP preservation, passive consent without billing reads, and scenario SQL counts. The following required evidence is not implemented or demonstrated, so this attempt does not pass review:

- Add a PostgreSQL failure-injection regression that fails after the `CustomerPhone` mutation and before evidence insertion, then asserts the transaction leaves both consent state and `WhatsAppConsentEvidence` unchanged. The implementation uses one transaction, but no test currently proves rollback for this failure point.
- Add a focused assertion that a fresh v2 grant's immutable evidence is retrievable by the existing API-006 proof tuple `(shopId, eventId, canonicalPhone, customerPhoneId, phoneConsentRevision)`. Current assertions read by `(shopId,eventId)` and separately inspect some evidence columns; they do not verify the complete tuple lookup contract.
- Complete the performance Work Item with comparable measured pre-change and v2 SQL operation counts for fresh GRANT, existing GRANT, REVOKE and duplicate retry, plus transaction-only duration and failure outcomes using the disposable PostgreSQL harness. Keep scenario wall time clearly distinguished from transaction duration and make no capacity/p95 claim. If a comparable baseline cannot be produced, obtain and record an explicit scope disposition rather than marking the criterion satisfied.

The launcher/provenance evidence gap has been resolved and is not a requested correction. `status: ready`, `executor: null`, `claimed_at: null`, `attempt: 1`; the next canonical developer claim will create Attempt 2. Implementation branch remains published and unmodified by this review. Do not start API-006 or the Woo producer task, and do not mark this task complete.

### Architectural Concerns

- An authenticated opt-in now stores passive consent evidence even if Checkout Recovery is disabled. Background must still enforce recovery feature eligibility, current consent and authoritative WhatsApp STOP before creating work or sending messages.
- The direct-service comparison measured 12 SQL statements for a fresh v2 grant versus 14 on the pinned v1 baseline; the HTTP integration scenario separately counted 14 statements including route/auth work. These are scenario counts, not capacity limits; further optimisation must retain tenant isolation, transactional idempotency and consent ordering.
- Review the production rollout together with the Woo v2 producer change, since v1 is intentionally rejected immediately by this API branch. Do not claim integrated functionality or change any `_index.md` before session close.

## Developer Self-Review Passed (Attempt 2)

- Reconciled Attempt 2 against the current task definition and published implementation branch `task/ARCH-046-API-007` at `b1ccf7842d1a6d732d900676d6e8c4250977b707`; implementation HEAD matches its remote and the worktree is clean.
- The rollback criterion is covered by a disposable PostgreSQL trigger that aborts evidence insertion after the phone mutation; assertions prove rollback for an existing recipient and newly created customer/phone rows. The API-006 proof tuple is queried directly using all five keys, with wrong-tenant and wrong-revision negative assertions.
- The same pre-change/v2 benchmark passed for both revisions and records SQL counts, Prisma transaction-client elapsed time, scenario wall time, and commit/rejection/rollback outcomes for fresh GRANT, existing GRANT, REVOKE, duplicate retry, stale GRANT and injected evidence-write failure. Measurements and limits are recorded above; no p95, capacity or generalized latency-improvement claim is made.
- Attempt 2 validation passed: `npm run test:arch046-woo-consent:unit` (**6/6**); `ARCH046_CONSENT_COMPARE_BASELINE=1 npm run test:arch046-woo-consent:postgres` (**11/11** integration tests plus **1/1** v1 and **1/1** v2 comparison tests); `npm run typecheck`; `npm run lint`; `git diff --check origin/main...HEAD`; and parsing `docs/openapi/arch046-woo-consent-v2.yaml` with the installed `yaml` package. The disposable PostgreSQL suite applied 59 migrations.
- Canonical Attempt 2 preparation passed the dependency gate. Both task worktrees were reused and already current with task remotes and `origin/main`; recursive submodule sync/init passed with database at `508a89463ccb24dcc31e5f38e04be8cfd10ad690`. Claim commit `de0542ed41ccbedad1c9189b712011cea902792a` is published on the parent task branch.
- No material assigned-agent assistance was used. No Woo producer, API-006, schema migration, Background code, `_index.md`, or shared checkout changes are included. End-to-end Woo producer adoption remains separately owned.
- State transition: `status: review`, `executor: null`, `claimed_at: null`, `attempt: 2`. `completion_mode: developer`; explicit developer completion is pending. Neither task branch was merged to `main`.

## Architect Review
## Developer Review Reconciliation — 2026-10-27

Reconciled the existing passing Attempt 2 review against the canonical task
worktrees. The task remains `status: review`, `attempt: 2`, with
`executor: null` and `claimed_at: null`; `completion_mode: developer` is
unchanged, so this no-action reconciliation does not record explicit
completion.

- The three declared prerequisites, `ARCH-046-API-001`,
  `ARCH-045-DATABASE-002`, and `ARCH-045-SHARED-002`, are Complete.
- The canonical parent task worktree is clean on
  `task/ARCH-046-API-007` at `760be4cdcd842cf8ad15ccf90ab571aa6e63e6bd`, equal
  to `origin/task/ARCH-046-API-007`.
- The canonical API implementation worktree is clean on
  `task/ARCH-046-API-007` at
  `b1ccf7842d1a6d732d900676d6e8c4250977b707`, equal to
  `origin/task/ARCH-046-API-007`.
- Independently rerun from the canonical API worktree: consent unit suite
  **6/6 passed**, `npm run typecheck` passed, and `npm run lint` passed.
- The disposable PostgreSQL/concurrency/performance comparison evidence remains
  the previously recorded Attempt 2 evidence; it was not rerun during this
  reconciliation. No implementation files or downstream task records changed.

The earlier Attempt 2 passing review remains durable. Explicit developer
completion is pending the separate `/moda_developer_update ARCH-046-API-007
complete` decision. No branch was merged to `main`.

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

Define and complete the repository-owned WooCommerce v2 producer adoption task before claiming end-to-end v2 coverage. v1 is removed from the API as an explicit pre-production breaking decision.
