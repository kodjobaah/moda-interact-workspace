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
status: ready
priority: 20
executor: null
claimed_at: null
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

- [x] Implement exact `woo.whatsapp-consent-status.v1` request/response types, strict bounded parser and stable route error contract, separate from the v2 **write** parser.
- [x] Implement evidence-first, tenant- and installation-scoped indexed read comparing grant evidence with the **current** CustomerPhone decision, revision and sequence; service query tests enforce one joined read and no feature/subscription query.
- [x] Register status dispatch in `src/composition/woocommerce.ts`, `src/composition/routes.ts` and `src/index.ts`, preserving existing consent-write dispatch and authentication.
- [x] Add unit tests for authentication order, headers/version/body limits, exact status response, no-store behavior and generic error propagation.
- [ ] Complete disposable PostgreSQL coverage for the full required matrix. Current integration exercises current grant, wrong event/phone, other shop, REVOKE/newer GRANT, credential rotation and revoked installation; it does not explicitly exercise lost-ACK status replay, same-shop alternate installation, ended phone, old revision as a separate case, or a database failure through the integrated route.
- [ ] Complete a real HTTP contract test against the Woo PHP client contract fixture. The authenticated API route is exercised through `createWooRoutes` and `composeApiRoutes`, and the PHP validator was inspected, but no cross-repository fixture invokes/verifies the client contract.
- [ ] Record query timing and explicitly prove absence of writes and all recovery/send side effects. Integration records three observed SQL statements and one joined evidence query; the requirement for measured status-query timing and the full no-side-effect assertion remains incomplete.

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
- [x] Same-shop wrong-event/phone and cross-shop same-phone probes return `UNVERIFIED`; no caller-supplied customer or installation fields are accepted. Missing evidence is tested as `UNVERIFIED` at the service/unit boundary.
- [ ] REVOKE, stale evidence and credential rotation are covered, but same-shop alternate installation, ended-phone and explicit account/customer mismatch integration cases remain untested.
- [x] Unauthorized/revoked installation, malformed HTTP/body/version and a database failure are covered by route/unit tests; REVOKE followed by an old proof returns `UNVERIFIED`. The DB-failure case is a mocked route failure, not a disposable PostgreSQL outage.
- [ ] Exact HTTP 200 body and `no-store` are verified through the real composed API HTTP route, and the current PHP validator was inspected; automated compatibility with the actual Woo client fixture remains unverified.
- [ ] Unit SQL inspection excludes subscription/feature queries and the integration checks no recovery rows for the covered flow; no complete assertion yet proves there are no writes, enqueued jobs, sends or billing/credit effects for every status probe.
- [ ] The route preserves provider error metadata and has phone-redaction tests, but redaction tests do not prove event/shop/customer/installation identifiers cannot appear in error message, stack or cause.
- [ ] Focused unit/PostgreSQL, typecheck and build pass. Repository lint has one unrelated `no-empty` error; query timing, full PostgreSQL matrix and automated Woo client contract validation are still outstanding, so full acceptance is not demonstrated.

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

Developer Self-Review — Changes Requested, Attempt 1. The endpoint, composition wiring and core proof checks are implemented, and focused unit, PostgreSQL, typecheck and build validation pass. Acceptance is not demonstrated: required PostgreSQL scenarios, the Woo PHP contract fixture, measured query timing/full no-side-effect assertions, and complete diagnostic redaction evidence remain outstanding. Repository-wide lint reports one error in unchanged `src/merchant/support/routes.ts`. Attempt 1 execution claim is cleared; do not increment the attempt until the next developer claim.

### Files Changed

- Implementation commit `53df5aa` changes 16 API files: status-v1 contract/parser/service/route, composition wiring, OpenAPI and HTTP documentation, focused unit and PostgreSQL tests, package script, and disposable integration runner. No implementation worktree files are uncommitted.
- Parent task file updated for this developer self-review; no unrelated task or index file changed.

### Work Completed

- Implemented the read-only authenticated status route. It returns the exact two-key status-v1 body with `Cache-Control: no-store`; uses the existing Woo installation authenticator; and performs one joined, parameterized evidence/current-consent SQL read after authentication.
- The SQL scopes evidence to authenticated shop, installation, event and phone; joins the current CustomerPhone and shop-scoped Customer; checks active Woo installation/shop and credential version; requires matching GRANT purpose, decision, source, revision, decision sequence, verification fields, and excludes ended phones.
- The actual route is registered in the HTTP composition path. Tests instantiate a real HTTP server around `composeApiRoutes`, exercise the real v2 writer and status handler, and verify one joined evidence query, cross-shop rejection, stale proof after REVOKE/newer GRANT, credential rotation and revoked installation behavior.
- Reviewed `ModaApiClient::wooConsentStatus()` and confirmed its exact successful response keys/version/state match the API response shape. Automated invocation of the Woo PHP client or a cross-repository contract fixture was not found.
- No schema, Woo PHP source, billing, recovery, queue, or message-send behavior was changed.

### Validation Results

- Environment: macOS, Node `v24.21.0`, npm `11.19.0`; API package pins Node `24.19.0`; database submodule at the launcher-prepared revision. Implementation task worktree is clean and its task branch tracks the remote.
- `npm run test:arch046-woo-consent-status:unit`: passed, 10/10 tests.
- `npm run test:arch046-woo-consent:unit`: passed, 6/6 tests.
- `npm run test:arch046-woo-consent:postgres`: passed, 12/12 integration tests on a disposable PostgreSQL database after all 68 migrations. The status route reported `actual_status_read_sql_statements=3; joined_evidence_queries=1`; this is count evidence, not query timing. No end-to-end status-probe duration was recorded.
- `npm run typecheck`: passed.
- `npm run build`: passed.
- `npm run lint`: failed on the existing unrelated `src/merchant/support/routes.ts:75` `no-empty` diagnostic. No task-changed files were implicated.
- Focused `npx eslint src/woocommerce/consent-status src/composition/routes.ts src/composition/woocommerce.ts src/index.ts tests/unit/woocommerce/consent-status tests/unit/composition/routes.test.ts tests/integration/woocommerce/consent-status scripts/test-arch046-woo-consent-postgres.mjs`: passed with no diagnostics.
- `git diff --check origin/main...HEAD`: passed. No implementation files are uncommitted.
- Integration-runner output reported 12/12 pass. Three other containers with the runner's name prefix were present from earlier runs (created at 23:24, 23:25 and 23:44 UTC); their database names did not match this run's database, so none were removed. The current run's dedicated database name was not among those containers. Do not claim global prefix cleanup from this check.

### Deviations

- This review does not mark the task passing because the acceptance criteria require more than the current focused evidence. The specific remaining coverage/evidence gaps are listed in Work Items, Acceptance Criteria and Developer Self-Review below.

### Assumptions

The API-007 v2 writer and the WOO-003 status client remain the agreed transport baseline; no automatic consent transfer to a changed phone is approved under this task.

### Unresolved Issues

- Add disposable PostgreSQL cases for lost-ACK status replay, same-shop alternate installation, ended phone, explicit old revision and DB failure as applicable to the fixture contract.
- Add the Woo PHP client contract fixture/compatibility test; record status-query duration as well as SQL statement count and assert absence of writes/side effects.
- Expand diagnostic redaction tests to cover event/shop/customer/installation identifiers in error message, stack and cause without dropping safe provider name/code/status.
- Repository lint has an unrelated existing error in `src/merchant/support/routes.ts:75`.

### Architectural Concerns

None requiring a new schema or service. Returning-checkout identity is bound locally in Woo; the API independently verifies an exact authenticated grant/current-recipient tuple. If a different principal-binding contract is needed, stop and return to `moda_architect` rather than inventing browser identity fields.

## Developer Self-Review — Changes Requested (Attempt 1)

### Review Outcome

Changes Requested. The current endpoint implementation and focused validations are promising, but required evidence and several explicitly named integration scenarios are incomplete. This is a review result, not a completion decision. The task transitions to `ready`; `executor` and `claimed_at` are cleared; `attempt` remains 1.

### Required Corrections

1. Extend the disposable PostgreSQL status scenarios to verify lost-ACK duplicate/replay behavior, same-shop alternate installation rejection, ended CustomerPhone rejection, explicit stale-revision behavior, and database failure handling at the appropriate integration boundary.
2. Add an automated compatibility fixture/test for the actual Woo `wooConsentStatus()` response validator, rather than relying only on source inspection and matching JSON literals.
3. Measure status-read duration and query timing in the disposable integration test, and assert the status probe performs no writes or recovery/send/billing side effects. Retain the existing one joined evidence query assertion.
4. Prove diagnostic redaction for event, shop, customer and installation identifiers across error message, stack and cause. Keep safe provider error name/code/status while preventing sensitive identifiers from reaching logs.
5. Rerun the focused unit and disposable PostgreSQL suites, typecheck, build, changed-file lint and `git diff --check`; retain the repository-wide lint result as an unrelated existing failure unless the owner resolves it.

### Evidence Reviewed

- API implementation branch commit `53df5aa` (`feat(arch046-api-006)`), published on `origin/task/ARCH-046-API-006`; changed 16 files, with no uncommitted implementation changes.
- Parent task branch initially at `e7db39226`, with developer claim commit `d9e16f187`; dedicated parent and implementation worktrees are clean before this review update.
- Focused status unit tests 10/10; existing consent unit tests 6/6; disposable PostgreSQL integration 12/12; typecheck/build passed; changed-file lint passed; full lint failed only at unchanged `src/merchant/support/routes.ts:75` (`no-empty`).
- The PostgreSQL integration logged three SQL statements for status and one joined evidence query. Query timing was not measured. The integration assertions do not cover the full scenario matrix listed above.
- The Woo PHP validator was inspected and uses the same exact status-v1 schema/state keys, but no cross-repository executable compatibility fixture was run.
- A check found three unrelated pre-existing containers matching the disposable runner prefix; their database names were different from this run. They were not removed because ownership was not established.

### Lifecycle

`status: ready`, `executor: null`, `claimed_at: null`, `attempt: 1`. The next `/moda_developer_create ARCH-046-API-006` claim creates Attempt 2. Completion remains pending; do not mark Complete until a passing review and explicit developer completion decision.

## Architect Review — Initial Definition

### Review Status

Pending at task definition time; no API implementation had been submitted for architect review then. The later Attempt 1 implementation and developer self-review are recorded above.

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
