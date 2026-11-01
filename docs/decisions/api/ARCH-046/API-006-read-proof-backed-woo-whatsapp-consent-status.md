---
id: ARCH-046-API-006
architecture_id: ARCH-046
title: Read current Woo WhatsApp consent using acknowledged shopper-bound grant evidence
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: in_progress
priority: 20
executor: developer
claimed_at: 2026-11-01T23:22:48Z
attempt: 1
depends_on:
  - ARCH-046-API-007
  - ARCH-045-DATABASE-002
  - ARCH-045-SHARED-002
enables:
  - ARCH-046-SYSTEM-TEST-001
  - ARCH-046-SYSTEM-TEST-002
created: 2026-11-01
updated: 2026-11-01
---

# Read current Woo WhatsApp consent using acknowledged shopper-bound grant evidence

## Architecture

Architecture ID: `ARCH-046`.

Architecture document: `docs/architecture/ARCH-046-woocommerce-whatsapp-consent-gated-recovery.md`.

Coordinator: `moda_architect`.

**Lifecycle:** Defined from the uploaded 2026-11-01 primary workspace snapshot and the WOO-003 task-worktree snapshot. The task file did not exist in either source. All declared dependencies are `complete` in the primary snapshot, so this portable definition is `ready` **but not materialised, claimed, committed, implemented or accepted**. The developer must materialise and claim the task through `/moda_developer_create ARCH-046-API-006`; creating this patch does not create the developer's branch/worktrees.

**Cross-task gate:** `ARCH-046-WOOCOMMERCE-003` is already `in_progress` and must not be regressed or reclaimed merely because this previously missing prerequisite is now defined. It cannot claim completed *live returning-checkout status* until this API task is completed and a real integration test passes. The system tests below explicitly depend on API-006.

## Objective

Implement the missing **read-only, installation-authenticated, proof-backed** `POST /v1/woocommerce/whatsapp-consent/status` route, allowing the existing WooCommerce Classic/Blocks client to restore `CONFIRMED_GRANTED` **only** when its server-held acknowledged GRANT evidence still matches authoritative current consent from the checkout checkbox. All other valid proof checks return opaque `UNVERIFIED`.

## Context

- API-007 completed the canonical `woo.whatsapp-consent.v2` GRANT/REVOKE writer. The writer atomically updates `commerce.CustomerPhone` and creates `commerce.WhatsAppConsentEvidence`, and has regression evidence for the exact five-key lookup tuple `(shopId,eventId,canonicalPhone,customerPhoneId,phoneConsentRevision)`.
- The inspected API has `src/woocommerce/consent/{contract,request,routes,service}.ts` for the write path, but **no** consent-status route. `src/composition/woocommerce.ts` creates only the write handler, and `src/composition/routes.ts` / `src/index.ts` register only that handler.
- The existing WooCommerce worktree implements `includes/Checkout/CheckoutConsentProof.php`, `CheckoutConsentStatusReader.php` and `includes/Api/ModaApiClient.php::wooConsentStatus()`. WordPress holds a GRANT event ID and phone only **server-side** after ACK. It POSTs `{schemaVersion,canonicalPhone,grantEventId}`; the client expects exactly `{schemaVersion,state}` with `CONFIRMED_GRANTED | UNVERIFIED`.
- Real browser diagnostics on 2026-11-01 returned `consent_status_remote_unavailable` on checkout reload even though a prior GRANT had been persisted in PostgreSQL. This task closes that hosted-read gap; it is **not** a request to reintroduce a read-before-write check for same-checkout REVOKE.

## Scope

- API-only: add a narrow status request parser, status service and route under `moda-interact-api/src/woocommerce/consent-status/` (or equivalently cohesive modules under the existing `consent/` directory), reusing the existing installation authenticator and no-store response helper.
- Wire the route explicitly into `src/composition/woocommerce.ts`, `src/composition/routes.ts` and `src/index.ts` so the **actual HTTP server** dispatches it. Preserve existing GRANT/REVOKE route selection, order and behaviour.
- Read existing `commerce.WhatsAppConsentEvidence`, `commerce.CustomerPhone`, `commerce.Customer` and current Woo installation/shop state. Prefer one bounded, indexed SQL statement with all needed joined predicates and no long-running read transaction; do not read feature preferences or subscription state.
- Add API-owned OpenAPI/HTTP documentation, fixtures and focused unit + disposable-PostgreSQL integration tests. Demonstrate live HTTP routing and compatibility with the existing Woo PHP `wooConsentStatus()` response validator.

## Out of Scope

- No new database tables, Prisma migrations, WordPress PHP/JS changes, browser cookies, principal-digest columns, caching, Redis/BullMQ, checkout recovery creation, Meta messaging, credits or subscription/feature lookup.
- Do **not** change `ARCH-046-API-007` write semantics or require this endpoint as a preflight for ordinary GRANT, same-checkout REVOKE, duplicate write retries or another outbound send.
- No phone-only lookup or inferred opt-in, no cross-phone transfer of a person's preference, and no GRANT on checkout hydration. The distinct person-level preference vs changed delivery destination policy remains an architectural follow-up, not implicit API-006 scope.
- No new generic logging implementation; use `@modainteract/moda-interact-shared/logging`. No edits to `docs/decisions/**/_index.md` or another domain's runtime source.

## Requirements

1. **Canonical HTTP v1 status contract, matching the shipped Woo consumer:**
   - `POST /v1/woocommerce/whatsapp-consent/status` with the existing `x-moda-installation-id` plus bearer authentication, `Content-Type: application/json`, no query string, no cache and **bounded strict JSON**. Require exactly three request keys; reject duplicates/extra keys, invalid version, malformed identifiers, unknown numbers or unexpected encodings. Keep request body <= 512 bytes and no larger than the existing Woo sender's limit.
   - Input:
     ```json
     {"schemaVersion":"woo.whatsapp-consent-status.v1","canonicalPhone":"447400123456","grantEventId":"woo-consent-example-01"}
     ```
   - **Only successful valid status probes** return HTTP 200 and **exactly**:
     ```json
     {"schemaVersion":"woo.whatsapp-consent-status.v1","state":"CONFIRMED_GRANTED"}
     ```
     or `{ "schemaVersion": "woo.whatsapp-consent-status.v1", "state": "UNVERIFIED" }`. Do not add `reason`, user IDs, canonical phone, evidence IDs or customer metadata to responses. Every response must carry `Cache-Control: no-store`.
   - Unauthorized installation/credential -> `401` generic `unauthorized`; syntactically invalid request -> `400` generic `invalid_request`; too-large input -> `413`; unexpected DB/provider failure -> `503` generic `consent_status_unavailable`. No `CONFIRMED_GRANTED` on any exception. Keep responses compatible with the Woo 4 KB JSON response bound.
2. **Authentication/tenant authority:** Reuse `WooInstallationAuthenticator.authenticate()` and its active installation, credential-digest, Woo platform, shop-status and revocation checks. Infer `shopId`, installation ID and current credential version **exclusively** from the principal; do not accept caller-supplied `shopId`, `customerId`, `customerPhoneId`, browser nonce, or WordPress user ID. Revalidate current installation/shop activation and credential-version relationship as part of the read (or an equivalently race-safe bounded step), without weakening credential-rotation/revocation protection.
3. **Indexed evidence proof:** Starting with `commerce.WhatsAppConsentEvidence` keyed by `(shopId,eventId)`, require evidence for `GRANT`, correct `purpose = WHATSAPP_CHECKOUT_RECOVERY`, exact `canonicalPhone`, and the **same installation** as the authenticated principal. Join `CustomerPhone` on the persisted `customerPhoneId/customerId` and `Customer` on shop-scoped customer ID. Reject missing, ambiguous, ended, foreign-shop, foreign-installation, wrong-phone or non-GRANT evidence with `UNVERIFIED`.
4. **Current checkbox consent, not historical evidence:** Require the matched active CustomerPhone to have the same canonical phone and purpose, current `whatsappConsentDecision = GRANTED`, `whatsappConsentSource = WOO_MODA_CHECKBOX`, both `whatsappConsentRevision = evidence.phoneConsentRevision` **and** `whatsappConsentDecisionSequence = evidence.decisionSequence`, and valid current verification/observation fields. An intervening checkbox REVOKE, newer checkbox decision/revision, customer/phone retirement or installation change returns `UNVERIFIED`. A newer GRANT needs its newer proof; old GRANT event IDs cannot resurrect consent.
5. **Failure/concurrency:** Treat a no-match, stale proof, mismatch or revoked checkbox consent uniformly as `UNVERIFIED`. A database exception is a logged operational failure and HTTP 503, not a fabricated valid grant. Use a consistent single-query snapshot or documented equivalent under concurrent checkbox writes; any revocation committed before the read snapshot must be reflected. Do not use out-of-band external requests, network calls inside a database transaction or a wait on checkout recovery state.
6. **Observability:** Emit bounded structured success/UNVERIFIED/unavailable events with duration, outcome, and anonymised correlation/installation scope only. Preserve original DB/provider/SDK error name, code, message, stack and relevant safe response metadata on the server using the Shared logger, with redaction; do not log bearer, event ID, raw phone, request body, disclosure, account identifiers or evidence payload. Instrument only domain-specific outcomes; reuse existing HTTP/framework telemetry.

## Work Items

- [ ] Implement exact `woo.whatsapp-consent-status.v1` request/response types, strict bounded parser and stable route error contract, separate from the v2 **write** parser.
- [ ] Implement evidence-first, tenant- and installation-scoped indexed read comparing grant evidence with the **current** CustomerPhone decision, revision and sequence; confirm no mutation or queue work.
- [ ] Register actual HTTP dispatch in `src/composition/woocommerce.ts`, `src/composition/routes.ts` and `src/index.ts`, preserving existing consent-write dispatch and authentication.
- [ ] Add unit tests for request authentication/headers/version/body limits, exact status response, no PII and safe error propagation.
- [ ] Add disposable PostgreSQL tests for current grant, lost-ACK duplicate, REVOKE/newer GRANT, wrong tenant/installation/phone, old revision, ended phone, rotation and database failure.
- [ ] Add a real HTTP contract test (authenticated API + Woo client contract fixture) and documented request/response examples; add only the minimal focused test scripts to `package.json` if the existing runner is insufficient.
- [ ] Inspect and record database query count/timing as measured results and regression-check absence of billing/feature queries, writes and recovery/send side effects.

## Interfaces / Contracts

**Provider:** `moda-interact-api`, implementation owner `moda_api`; HTTP schema owner: API-006. The authenticated WooCommerce PHP client `ModaApiClient::wooConsentStatus()` is the consumer, currently shipping the above fixed v1 contract. PHP cannot import a Node-only Shared runtime validator; keep one canonical API/OpenAPI specification and verify compatibility using cross-repository JSON fixtures, not divergent local invented wire shapes.

**Inputs:** `WooInstallationPrincipal` from `src/auth/woo-installation/authenticator.ts`; `{schemaVersion,canonicalPhone,grantEventId}` from a WordPress server-held, acknowledged shopper-bound proof. The API does not receive or verify WordPress session proof directly; **Woo owns** binding that proof to the current logged-in customer or current guest checkout. The API independently validates the exact persisted event/current-recipient relationship and current checkbox consent.

**Output:** HTTP 200 `{schemaVersion:"woo.whatsapp-consent-status.v1",state:"CONFIRMED_GRANTED"|"UNVERIFIED"}` or the stable generic HTTP error bodies described above. Exactly two response keys on successful probes, to match Woo's existing strict parser.

**Database:** Existing `commerce.WhatsAppConsentEvidence` unique `(shopId,eventId)` and `commerce.CustomerPhone` current authority; evidence has `installationId`, `canonicalPhone`, `customerId`, `customerPhoneId`, `decision`, `decisionSequence`, `phoneConsentRevision` and `purpose`. Reuse the accepted API-007 write contract and the published Shared phone canonicalisation utility for canonical validation; do not add a second phone identity table.

**Expected source locations:**

```text
moda-interact-api/src/woocommerce/consent-status/contract.ts
moda-interact-api/src/woocommerce/consent-status/request.ts
moda-interact-api/src/woocommerce/consent-status/service.ts
moda-interact-api/src/woocommerce/consent-status/routes.ts
moda-interact-api/src/composition/woocommerce.ts
moda-interact-api/src/composition/routes.ts
moda-interact-api/src/index.ts
moda-interact-api/docs/openapi/arch046-woo-consent-status-v1.yaml
moda-interact-api/docs/arch046-woo-consent-http.md
moda-interact-api/tests/unit/woocommerce/consent-status/*.test.ts
moda-interact-api/tests/integration/woocommerce/consent-status/*.postgres.test.ts
```

If a clearer cohesive arrangement reuses `src/woocommerce/consent/`, retain these same interfaces and exact composition points; document actual paths in the Completion Report. Add a focused PostgreSQL runner only when required by the existing test harness, not a second test framework.

## Dependencies

- `ARCH-046-API-007` — complete; canonical thin v2 consent writer and retrievable five-key grant evidence.
- `ARCH-045-DATABASE-002` — complete; existing immutable evidence and CustomerPhone current-consent schema.
- `ARCH-045-SHARED-002` — complete; published shared identity/consent primitives.

No implementation task depends on a system-test task. Do not reopen API-007 or schema work.

## Enables

- `ARCH-046-SYSTEM-TEST-001` — LocalWP Classic/Blocks proof-backed returning checkout capture/withdrawal certification **only after** WOO-003 is also complete.
- `ARCH-046-SYSTEM-TEST-002` — later integrated consent/recovery validation when all other independent recovery prerequisites complete.

`ARCH-046-WOOCOMMERCE-003` is already in progress: successful API-006 acceptance unblocks its **outstanding live verification**, not an implicit new claim or a status regression.

## Acceptance Criteria

- [ ] A real API-007 v2 GRANT acknowledged by Woo produces a server-held proof that API-006 returns `CONFIRMED_GRANTED` for the same installed merchant/shop/current canonical phone, with **no additional consent write** on page hydration.
- [ ] Same-shop matching phone with missing/forged/wrong-event proof is `UNVERIFIED`; no phone-only, customer-ID-only or account-ID-only authority is accepted. A separate shop using the same phone cannot learn or reuse that proof.
- [ ] REVOKE, stale evidence after later checkbox decisions and account/recipient/installation mismatch never return confirmed; a replayed old GRANT cannot restore checked state.
- [ ] Unauthorized/revoked/rotated installation, invalid HTTP/body/version and DB outage reject with correct bounded status and no leaked details; no stale grant is confirmed following a prior committed revocation.
- [ ] HTTP 200 responses exactly match `woo.whatsapp-consent-status.v1` `{schemaVersion,state}`, with `no-store` and no PII; actual Woo `wooConsentStatus()` accepts them without changing its existing validator.
- [ ] Status reads do not query subscription/feature preferences, create CheckoutRecovery, enqueue any job, send Meta messages, alter CustomerPhone or evidence, or commit billing/credits.
- [ ] Original errors are available in safe server-side Shared diagnostics without swallowing/replacing the underlying provider error; no sensitive request material in logs.
- [ ] All required API unit/PostgreSQL/HTTP contract validation passes and Completion Report includes exact changed files, measured query evidence and dedicated physical-worktree/start-of-attempt provenance.

## Validation

- [ ] Run the actual declared API unit command (`npm run test:arch046-woo-consent:unit`) plus the new focused status tests; if needed add one `test:arch046-woo-consent-status:unit` script using `tsx --test`.
- [ ] Run disposable PostgreSQL integration (`npm run test:arch046-woo-consent:postgres` plus dedicated status scenarios/runner) with real v2 GRANT + status + REVOKE and cross-tenant/installation checks. No mock-only acceptance.
- [ ] Exercise the **real HTTP route** through `createWooRoutes` / `composeApiRoutes` and a signed-in installation, including exact response accepted by the Woo PHP client; validate real start-up routing instead of testing only the service function.
- [ ] `npm run typecheck`, `npm run lint`, `npm run build` (scripts exist in the inspected API `package.json`; document unrelated known baseline failures by their baseline IDs, never ignore regressions).
- [ ] Verify OpenAPI example and current Woo client schema agreement, `git diff --check`, source-scope diff and no `_index.md`, schema or unrelated runtime changes.

## Stop Condition

After the Work Items, Acceptance Criteria and required Validation are complete, update this task's own Work Items, Validation and Completion Report; set `status: review`, release the developer claim as required by the developer review path, and STOP. Do not mark this task Complete without the configured developer completion decision. Do not start WooCommerce changes or system tests implicitly.

## Implementation Notes

1. **Performance:** The status read should be deliberately narrower than the former `/v1/merchant/feature-preferences` path. The latter incurred multiple remote database operations and has been removed from WOO consent capture. A single indexed evidence/current-state query is preferred; the authenticated installation lookup remains necessary. Do not add entitlement checks or a multi-query configuration read.
2. **Proof identity and trust:** `CheckoutConsentProof::rememberGrant()` stores account-bound proof in private WordPress user metadata or guest proof in a Woo checkout session after a hosted GRANT ACK; `forCurrentShopper()` checks shop, installation, credential version, phone digest, logged-in user or guest session/checkout key before returning `grantEventId` and canonical phone to PHP. API-006 must never trust the phone alone, but it need not reconstruct those private WordPress details. Never serialize the proof to browser HTML or diagnostics.
3. **Read-only checkbox status:** The endpoint confirms only the specific current checkbox GRANT evidence and recorded checkbox decision/revision. It does not change consent or evaluate downstream message-delivery eligibility.
4. **Unknowns/failures:** A missing proof is not an HTTP error, but the server will normally receive a status probe only after Woo has local proof; syntactically valid but unverifiable evidence is `UNVERIFIED`. Actual I/O faults are safe generic `503`, with original redacted provider error logged. Woo's current status client uses a **three-second HTTP timeout**; minimise sequential round trips without relaxing installation authentication or proof checks.
5. **Pre-production:** There are no deployed status-v1 consumers to migrate and no need for compatibility with speculative schemas. WOO-003 already expects this exact status v1 request and response. No new Gateway service, database migration or Shared publication task is justified by the inspected baseline.
6. **Ownership and worktrees:** Read `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md` and `docs/developer-task-workflow.md`. Use `/moda_developer_create ARCH-046-API-006` for canonical sibling parent/API implementation worktrees and start-of-attempt synchronization. The current snapshot is not a live checkout; do not claim developer branch creation, commit, push, physical isolation or published implementation from this definition patch.

## Completion Report

### Status

In Progress — Attempt 1 claimed by developer at 2026-11-01T23:22:48Z. Attempt 0 review history is preserved below.

### Files Changed

None (implementation not started).

### Work Completed

None.

### Validation Results

Not run. Test commands above are required for execution, not reported as passed.

### Deviations

None.

### Assumptions

The API-007 v2 writer and the WOO-003 status client remain the agreed transport baseline; no automatic consent transfer to a changed phone is approved under this task.

### Unresolved Issues

The developer must verify API-007 and ARCH-045 schema pins on the actual prepared API task branch before implementation. The older missing status endpoint is not fixed by defining this task.

### Architectural Concerns

None requiring a new schema or service. Returning-checkout identity is bound locally in Woo; the API independently verifies an exact authenticated grant/current-recipient tuple. If a different principal-binding contract is needed, stop and return to `moda_architect` rather than inventing browser identity fields.

## Architect Review

### Review Status

Pending — no implementation submitted.

### Review Notes

Canonical definition prepared from 2026-11-01 supplied snapshots, no code reviewed or accepted for API-006.

### Reviewed Files

The current API-007 consent writer and authentication/route composition, current CustomerPhone/evidence schema, and WOO-003 private proof/status client contracts.

### Validation Reviewed

Task-definition patch application only; no runtime API validation.

### Architecture Conformance

Pending implementation.

### Follow-up

Materialise and execute this developer-owned task when ready; verify actual WOO-003 integration after API completion.
