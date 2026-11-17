---
id: ARCH-077-SHOPIFY-002
architecture_id: ARCH-077
title: Issue Shopify signed checkout-attribute consent receipts and read returning consent
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 45
executor: copilot
claimed_at: 2026-11-17T19:22:48Z
attempt: 3
depends_on: [ARCH-077-SHOPIFY-001, ARCH-077-SHARED-001]
enables: [ARCH-077-BACKGROUND-001, ARCH-077-SHOPIFY-003, ARCH-077-SHOPIFY-004, ARCH-077-SHOPIFY-005]
created: 2026-11-17
updated: 2026-11-17
---

# Shopify consent receipt service — architect-directed rework of S002

**Current architect disposition (17 November 2026, Attempt 3 review): Accepted; `complete` within SHOPIFY-002 producer scope.** The Shopify implementation now uses Shared credential AEAD/keyring and the frozen signed checkout-attribute receipt contract, without temporary Redis consent choices. Earlier Redis/HMAC attempts and Changes Requested decisions are retained below as history. This is **not** acceptance of live Shopify Plus attribute writes, real cart-to-checkout signed receipt propagation, Background's independent decoder or the integrated outbound system: those remain owned by their separately gated tasks.

## Objective and file-by-file implementation instructions

Implement **one server-owned, stateless receipt issuer** and returning-customer SQL status reader in `moda-interact`. The Shopify checkbox will write the returned receipt into the single Shopify attribute `moda_wa_consent_v1` under S003/S004. S002 does not itself touch the customer's cart, write PostgreSQL consent, create a recovery, or enqueue a consent job.

1. **Replace** `app/services/shopify-consent/shopify-consent.server.ts` Redis-heavy implementations `prepareCartMarker`, `recordCartChoice`, `readCartConsentStatus`, marker index, revisions, cart key/TTL and Redis errors with `app/services/shopify-consent/consent-receipt.server.ts`, implementing `issueConsentReceipt`, `verifyConsentReceipt`, and a focused `readReturningShopperConsentStatus`. Preserve only applicable provider-error logging and the exact English disclosure constant. Preserve the already-approved `ShopifyConsentServiceError` style as a typed server error where useful; do not keep unused Redis code or a compatibility path.
2. **Delete** `app/services/shopify-consent/marker.ts` if it becomes unused. Do not write `m1_`, `moda_cart_correlation_v1`, `shopify:consent:*` Redis keys or alter BullMQ indexes. The permanent Shopify webhook processing remains unaffected.
3. **Refactor** `app/routes/shopify/consent/route.ts`: remove old `cart/prepare`, `cart/choice` and marker status; implement signed App Proxy `GET cart/status` (verified shop+optional Shopify customer, SQL read only) and `POST cart/receipt` (explicit action choice; issue kind `c` receipt). Keep independent React Router registration `route('shopify/consent/*', ...)`. Existing `[app_proxy]` can remain once verified live; avoid duplicate Shopify proxy routes. Verify Shopify signed `timestamp` within ±300 seconds, the rule that browser Origin, if present, must be well-formed HTTPS but **must not** be compared to the `.myshopify.com` shop identity (Shopify SDK signature and bounded timestamp are the authentication boundary), approved `path_prefix`, max request body, JSON and a valid base Ajax cart token; do not treat a signed shop as proof of an anonymous shopper or trust body customer IDs.
4. **Add** a separate authenticated Plus Checkout UI Extension issuer route in `app/routes.ts` and a narrowly focused new route under `app/routes/shopify/checkout-receipt/route.ts` (distinct from App Proxy and embedded UI). Authenticate `Authorization: Bearer <Shopify checkout session token>` with the installed SDK checkout authentication, require verified shop/audience/session claims, supplied current checkout token, explicit action and locale, then issue kind `x` receipt. If installed SDK/target cannot provide verified shop/checkout context, stop and report a concrete SDK blocker; do not invent new claims or bypass authentication. S004 owns writing this receipt through `applyAttributeChange` and proving capability/readback.
5. **Revert only S002-specific marker projection** in `app/services/webhooks/checkout-normalization.ts` and related S002 ingestion changes: authenticated `CHECKOUTS_CREATE`/`CHECKOUTS_UPDATE` remain unchanged, but no new `cartCorrelationMarker` producer data is needed. Do not remove the accepted optional SHARED-001 fields from the Shared package; they remain optional/unused. Preserve all existing queue names/IDs and original checkout metadata.
6. **Key configuration (superseded HMAC contract):** use only the existing `MODA_ENCRYPTION_KEYS_JSON` and `MODA_ENCRYPTION_ACTIVE_KEY_ID` already consumed by Shopify platform configuration. Reuse the published `@modainteract/moda-interact-shared/security/credentials/node` operations `parseCredentialKeyring`, `resolveActiveCredentialKey`, `encryptCredential`, `decryptCredential` and `CredentialEnvelope`. Never create `SHOPIFY_CONSENT_RECEIPT_KEY_V1`, another HMAC signing key, a local AES implementation, alternative key rotation or extra Redis/SQL state. Decrypt by the envelope's existing `keyId`, not by assuming the current active key. The receipt has **no independent TTL**; it remains a Shopify checkout attribute until Shopify's normal checkout lifecycle.
7. **Existing PostgreSQL status:** read only an unambiguous current shop+verified Shopify customer `CustomerPhone` decision/STOP/recipient association; checked only for verified current GRANTED. A guest starts unchecked unless the current cart already contains a **verified** receipt. An initial render or status read never mints a new selection. A returning customer's explicit REVOKE is only a receipt in Shopify until the checkout is recoverable.
8. **Wire contract (updated v1 before release):** implement the *exact* versioned AES-256-GCM envelope encoding, canonical JSON payload and consent-specific AAD bytes in the linked architecture contract. Shared owns the AEAD/keyring mechanics; do not duplicate cryptography. Test round-trip across a Shopify-issued fixture and an independently constructed Background reader using the published Shared exports; incorrect AAD/shop/cart-or-checkout binding, malformed/duplicate attribute, wrong kind, future timestamp, missing/retired key and ciphertext/tag tampering fail closed. Test active-key change with a previous key retained, relying on Shared's existing `keyId` selection rather than a new rotation algorithm. Check 512-byte attribute bound and real Shopify readback in downstream S003/S004. Document same-checkout valid-receipt replay as an accepted **limitation**, not a passed replay-security property.
9. **No shopper-facing errors:** on SDK, signing, status or network failure, return typed non-sensitive failure; the S003/S004 control hides/restores unacknowledged selection and checkout always remains functional. Server preserves original useful SDK/Shopify/Prisma error details with redaction; never print raw tokens/receipts/customer data.

## Precise acceptance and tests

- Replace old `tests/integration/shopify-consent.redis.integration.test.ts` with receipt-focused deterministic tests, and update `tests/unit/routes/shopify-consent-route.test.ts`; do not delete independent `tests/integration/shopify-webhook-publication.redis.integration.test.ts` or queue regression coverage.
- Test signed custom-storefront-domain POST and each supported signed App Proxy prefix and subpath (do not hardcode `/apps/moda-consent` or `myshopify.com` as origin), fresh/stale/future signed timestamps, invalid/replayed signature, Shop A versus B, signed customer versus guest, changed cart token and Plus session token rejection; use the installed SDK or label mocks explicitly.
- Unit-test a real `cart/update.js` receipt readback fixture, checkout note attribute fixture and authoritative GraphQL `customAttributes` fixture. Tests must distinguish the previously verified marker experiment from **new** real receipt behavior, and must not claim Plus live functionality without a Plus checkout test.
- Verify no `redis` import or consent TTL in reworked issuer; no SQL consent writes from any S002 action; optional Shared marker fields unused; no queue naming changes; existing Shopify webhook integration tests pass. For verified returning status, select and check `whatsappConsentSource` and current purpose/no-contact/STOP fields, rather than treating an old Shopify-native marketing API observation as automatically Moda checkbox consent.
- Execute actual `npm run build`, targeted lint/typecheck and source-controlled tests; report the five known pre-existing webhook-root implicit-any type errors separately if still present. Provide exact changed files, SHA, package pins and meaningful redacted original provider errors.

**STOP conditions:** the verified Shopify checkout token cannot be bound to Plus receipt issuance, signed App Proxy origin/shop cannot be verified, the receipt attribute cannot round-trip intact, a newly added route weakens authentication, or the agent would need a new DB/Redis consent state to complete the task. Return the specific blocker; do not silently reintroduce the abandoned Redis design. The architect has returned this task to `ready` for an unclaimed correction attempt. After implementation and validation, the implementing agent must set it to `review` and stop for architect acceptance.


## Architect Review

### Latest review — Attempt 3: Accepted (17 November 2026)

**Decision:** `Accepted` for ARCH-077-SHOPIFY-002. Set task YAML to `status: complete`; retain `attempt: 3` and the submitted executor/claim metadata as execution evidence. This acceptance is limited to the Shopify application's stateless receipt issuer, authenticated routes and read-only returning-customer consent status. Do not interpret it as deployed Shopify Plus or Background acceptance.

**Implementation reviewed:** supplied `moda-interact-workspace-ARCH-077-SHOPIFY-002(3).zip`; agent-reported implementation SHA `96ad35f` and parent report SHA `8ae1840`. This ZIP snapshot does not contain Git history, so the SHAs and pushed/clean branch state are **agent reported**, not independently Git-verified. Inspected actual `app/services/shopify-consent/consent-receipt.server.ts`, `receipt-request.server.ts`, `app/routes/shopify/consent/route.ts`, `app/routes/shopify/checkout-receipt/route.ts`, `app/routes.ts`, package metadata and focused route/receipt unit tests.

**Conformance:** issuer and verifier consume `parseCredentialKeyring`, `resolveActiveCredentialKey`, `encryptCredential` and `decryptCredential` from published `@modainteract/moda-interact-shared/security/credentials/node`; no independent key rotation, HMAC secret, encryption implementation or Redis consent lifecycle. The v1 five-part envelope, canonical payload/AAD, shop/kind/token/customer binding, 512-byte attribute limit, duplicate/malformed attribute denial, active/previous key behaviour, and provider-error handling are implemented in the inspected source. Signed App Proxy requests enforce shop/session/scope, approved signed path prefixes and bounded timestamps; custom HTTPS storefront Origin is not incorrectly compared to `.myshopify.com`. Returning-customer display reads only qualifying current source/purpose/verification and STOP/no-contact state from PostgreSQL; no consent write occurs from these endpoints. The separate Plus receipt route authenticates the Shopify checkout session and issues kind `x`, but its live checkout-token and extension capabilities remain a downstream integration gate.

**Validation evidence:** agent reports 46 focused tests, 168 webhook unit tests, 9 Redis webhook regression tests, targeted ESLint, build, and `git diff --check` passed. This review independently inspected the checked-in test source and implementation, **not** the installed-dependency test execution or live provider. `npm run typecheck` is still reported failing on five unchanged implicit-any errors in `app/routes/webhooks/root/route.jsx`; accepted as an identified pre-existing baseline for this bounded task only, not a general typecheck pass or permission for new errors.

**Explicit downstream gates (not SHOPIFY-002 defects):** SHOPIFY-003 proves actual non-Plus browser `cart/update.js` signed-receipt write and GraphQL readback; SHOPIFY-004 proves supported Plus checkout session/checkout-token access and `applyAttributeChange` readback, with unsupported/accelerated checkout fail-closed; BACKGROUND-001/002 independently implement and test the exact Shared AEAD envelope/AAD decoding, candidate token, merchant/customer binding, recoverable-only PostgreSQL materialisation and proactive final-send controls; SYSTEM-TEST-001 verifies cross-service end-to-end behaviour. Preserve the accepted same-checkout historical valid-receipt replay limitation. Do not claim those results from the Shopify issuer's mocked/producer fixtures.

**Publication/configuration:** the app reports `@modainteract/moda-interact-shared@5.3.0`, whose imported credential Node API is used in the supplied source. Deployment must confirm the installed/published build exposes these exports and that Shopify/Background each have the required existing `MODA_ENCRYPTION_KEYS_JSON` (writer additionally `MODA_ENCRYPTION_ACTIVE_KEY_ID`); use the existing Shared `CredentialEnvelope.keyId` rotation behaviour, not any additional secret or rotation implementation. Real provider validation, deployed configuration and Background version/pin checks belong to the downstream integration/release gates.

**Decision and handoff:** unblock only direct dependants whose YAML prerequisites are now complete: `ARCH-077-SHOPIFY-003`, `ARCH-077-SHOPIFY-004`, and `ARCH-077-BACKGROUND-001` -> `ready`. `ARCH-077-SHOPIFY-005` and `ARCH-077-BACKGROUND-002` remain `pending` until their other dependencies pass architect review; final system test remains terminal. Do not change `docs/decisions/**/_index.md` prior to the separately requested final reconciliation. Architect does not merge or push implementation branches.

### Latest review — Attempt 2 implementation; Changes Requested (17 November 2026)

**Disposition:** `Changes Requested`; task YAML is now `status: ready`, `executor: null`, `claimed_at: null`, `attempt: 2` (preserved). The launcher alone claims Attempt 3 and increments the attempt. S001 and SHARED-001 remain `complete`; S003/S004/S005/B001 remain gated. This review supersedes conflicting HMAC/signing-key instructions elsewhere in this task; the amended canonical checkout-attribute v1 contract is binding. The Attempt 2 Completion Report and code commits are preserved as historical implementation evidence, **not** accepted runtime.

**Reviewed source:** supplied `moda-interact-workspace-ARCH-077-SHOPIFY-002(2).zip`; implementation commit `4d8b08806cf48e534d11367ca4e3b85f5146253c` and parent task report `9353a2bbef1ae80280ea43d5a23f7e1b538a9602` as agent-reported references. Inspected `app/services/shopify-consent/consent-receipt.server.ts`, `app/routes/shopify/consent/route.ts`, the receipt route/tests, platform-configuration keyring usage, and Shared credential `node.ts`, `keyring.ts`, `aead.ts` from supplied SHARED-001 worktree. Shared already exposes working keyring parsing, active-key selection and authenticated encryption/decryption. Source review, not a new execution of tests. Agent-reported Attempt 2: 98 receipt/route tests, 168 webhook tests, 9 Redis webhook regressions, lint and build passed; five unchanged webhook-root `implicit any` type errors reported. No live Plus provider validation or deployed receipt round-trip was established.

**Mandatory rework; same task, no new task ID or cryptographic infrastructure:**

1. **Replace dedicated key/HMAC code.** Remove `SHOPIFY_CONSENT_RECEIPT_KEY_V1`, `initializeConsentReceiptSigningKey`, `decodeSigningKey`, local `createHmac`/`timingSafeEqual` receipt path and every related secret/test/deployment reference from `app/services/shopify-consent/consent-receipt.server.ts`, routes, `app/shopify.server.js`, tests and configuration. Use only `MODA_ENCRYPTION_KEYS_JSON` / `MODA_ENCRYPTION_ACTIVE_KEY_ID`, with the existing published `@modainteract/moda-interact-shared/security/credentials/node` exports. Do not extract Shared's private AES key bytes, reimplement AES-GCM, add per-receipt secrets, key rotation services or new Redis/SQL persistence.
2. **Implement exact cross-service receipt bytes.** Replace the unshipped HMAC dot-separated value with `v1.<keyId>.<nonce>.<ciphertext>.<authTag>` (five dot-separated ASCII fields), with the three binary components canonical unpadded base64url and key selection delegated to Shared. The encrypted UTF-8 plaintext is the exact ordered JSON array `[1,shopId,kind,bindingDigest,decision,"1",locale,acceptedAt,customerId]`. Use exactly `JSON.stringify(["moda-shopify-wa-consent",1,shopId,kind,bindingDigest])` as Shared AEAD `aad` for both writer and reader. Derive AAD only from verified merchant and authoritative expected cart/checkout token (digest), never from unauthenticated receipt claims; enforce existing locale, decision, time, customer and max-512-byte rules after decrypt. The central `checkout-attribute-consent-v1.md` is the authoritative byte contract. A previous HMAC receipt is unreleased and **must be rejected** rather than supported via a compatibility reader.
3. **Use Shared's existing key rotation.** Issue using `resolveActiveCredentialKey` and `encryptCredential`; verify using `decryptCredential` and the envelope `keyId`. A previous-key receipt stays decryptable when the old key remains in `MODA_ENCRYPTION_KEYS_JSON`; unknown/removed keys and invalid/tag-tampered receipts fail closed. No separate rotation implementation, key hierarchy or extra fallback. Read-only Background will need the same **existing** keyring configuration and canonical AAD/serialization, not a new receipt-specific secret.
4. **Preserve existing API/security boundary.** In `app/routes/shopify/consent/route.ts`, remove exact `/apps/moda-consent` hardcoding: validate Shopify-signed `path_prefix` with the supported `(a|apps|community|tools)` prefix and a safe nonempty merchant-selected subpath. Keep SDK app-proxy signature, bounded timestamp, HTTPS Origin shape, canonical shop and verified signed customer; no trust in client-supplied shop/customer IDs. Tests: custom domains, all supported prefixes, altered/missing signed parameters, expiry/future timestamps, guest/authenticated separation, body limits and error redaction. Do not modify the Shopify Plus extension's downstream writer in S002.
5. **Returning-customer status:** in the existing SQL read-only `CustomerPhone` selection, include `whatsappConsentSource` and verify the **current approved Moda Shopify permission** (`SHOPIFY_NATIVE` under ARCH-077, with purpose, verified contact, no-contact/STOP and shop/customer match). Do not infer Moda checkbox permission from an obsolete provider-sync observation or grant on render. Document any indistinguishable legacy data as preproduction cleanup/retirement under S006 rather than fabricating a source distinction the current enum cannot encode.
6. **Focused verification:** use Shared's actual Node AEAD in receipt tests, including wrong AAD, shop, plan kind, token, customer, malformed/corrupt envelope, missing/invalid keyring, key-ID switching/previous-key decryption, duplicate checkout attribute, canonical base64url, future clock, provider/SDK logging and 512-byte limit. Add a stable cross-service fixture checked by both producer and Background consumer contract tests without introducing new Shared helpers. The actual cart attribute and authoritative GraphQL transport remain S003/S004/B001/system-test evidence and must not be misreported as already live-verified. Run impacted tests/lint/build; report the actual typecheck and distinguish pre-existing errors from regressions. Keep the configured Shared package pin verified as containing the required exports; do not require unrelated Shared 6.2.0 marker transport just for the new receipt.

**Scope exclusions / retained decisions:** only one checkout attribute, one control per plan, no click-time SQL GRANT/REVOKE, materialise only at recoverability, no new Redis consent TTL/keys, queue, schema or service; same-checkout valid-receipt replay remains explicitly accepted; all proactive-message and STOP fences remain. Existing S002 implementation branch, commits and Completion Report must be preserved. Agent must claim Attempt 3 via `/moda-task`, implement these exact corrections, record files/test evidence and set `status: review` on completion. No merge/deployment before renewed architect acceptance; no `_index.md` edits.

### Prior review — Attempt 1 (historical)

**Changes Requested — 17 November 2026.** Architect-approved attribute-based reconciliation is complete as a *document decision*, not as a verified runtime implementation. The submitted Attempt 1 Shopify implementation is not accepted under the new contract. The task is returned from `review` to `ready` for the same `moda_app` agent to claim Attempt 2 through the normal launcher. Do not manually mark this task `in_progress` or increment `attempt` before the launcher claims it.

### Review Notes and precise correction contract

The accepted `docs/architecture/ARCH-077/checkout-attribute-consent-v1.md` replaces the Redis cart/checkout choice, marker preparation and TTL architecture. The existing code still implements those obsolete mechanisms. Rework the **same** SHOPIFY-002 implementation rather than launching a separate feature or merging the obsolete code. The numbered instructions and tests above are mandatory, not suggestions. In particular:

1. Replace Redis choice/marker issuer with the stateless signed `moda_wa_consent_v1` receipt issuer and verifier, using the *exact* approved versioned wire contract. No additional Redis consent retention or cleanup task.
2. Change the authenticated cart App Proxy endpoints to `GET cart/status` and `POST cart/receipt` with the approved shop, request-freshness, input and storefront-domain handling. No client-supplied merchant identity or guest identity is authoritative.
3. Introduce the separate authenticated Plus checkout receipt-issuance boundary specified above. Do not implement S004's checkout checkbox/attribute writer inside S002.
4. Remove obsolete `m1_` marker preparation, Redis GRANT/REVOKE keys, TTL/revision scripts and S002 webhook-marker projection. Do not alter the accepted optional Shared schema fields, existing checkout-event queues or unrelated BullMQ processing.
5. Preserve returning-customer PostgreSQL **read-only** status, with no GRANT/REVOKE materialisation until Background independently verifies recoverability; preserve STOP and existing reactive-message semantics.
6. Replace Redis-specific task tests with receipt/signature, signed App Proxy, isolation, token binding, webhook regression and failure-path tests listed above. Preserve unrelated passing tests. Report real SDK/Plus test constraints; no fabricated provider evidence.

### Reviewed Files / Evidence

- Submitted SHOPIFY-002 implementation worktree and earlier completion report: implementation commit `c0c2cca` (reported); parent report `c4f2e158` (reported)
- `app/services/shopify-consent/shopify-consent.server.ts` and `app/routes/shopify/consent/route.ts` from prior architect inspection, containing the superseded Redis path
- Accepted non-Plus cart attribute propagation evidence and authoritative `AbandonedCheckout.customAttributes` query
- Reconciled ARCH-077 parent and `docs/architecture/ARCH-077/checkout-attribute-consent-v1.md`

### Validation Reviewed

The prior agent reported 173 webhook tests, 9 Redis webhook integrations, 4 consent Redis tests and a successful production build. Those runs demonstrate the **previous Redis implementation**, not the new receipt contract; they cannot be carried forward as acceptance for Attempt 2. This document/status correction has no runtime changes. No receipt runtime tests were executed by this architect amendment.

### Architecture Conformance

**Not yet conformant:** current submitted runtime uses Redis consent choice/marker lifecycle, now superseded. The new single Shopify attribute receipt contract is approved at the document level. Preserve unchanged merchant plan placement (cart for non-Plus, checkout for Plus), delayed consent materialisation, proactive vs reactive conversation rules and no new database/queue.

### Rework Handoff and Stop

`assigned_agent: moda_app`, repository `moda-interact`, task `ARCH-077-SHOPIFY-002`, `attempt: 1` preserved until the launcher claims Attempt 2. `executor` and `claimed_at` are cleared. Dependencies S001 and SHARED-001 remain `complete`. S003, S004, S005 and B001 remain gated until SHOPIFY-002 passes architect acceptance and reaches `complete`. The implementation agent must read this entire latest Architect Review before changing code; after correction and validation it must set the task to `review`, submit the updated Completion Report and stop. Do not modify task indexes, advance dependent tasks, merge branches or mark S002 `complete` during this rework.

## Completion Report

### Attempt 2 result

Replaced the superseded Redis consent choice and `m1_` marker path with a stateless, HMAC-signed `moda_wa_consent_v1` receipt issuer/verifier, read-only returning-shopper status lookup, authenticated App Proxy endpoints, and a separate authenticated Plus checkout receipt endpoint. Removed the S002 webhook-marker projection and obsolete Redis consent integration test. No consent state, receipt TTL, SQL consent write, or queue change was added.

The implementation branch is `task/ARCH-077-SHOPIFY-002`, commit `4d8b08806cf48e534d11367ca4e3b85f5146253c`.

### Changed files

- Added: `app/services/shopify-consent/consent-receipt.server.ts`, `app/services/shopify-consent/receipt-request.server.ts`, `app/routes/shopify/checkout-receipt/route.ts`, `tests/unit/services/shopify-consent-receipt.service.test.ts`.
- Updated: `app/routes.ts`, `app/routes/shopify/consent/route.ts`, `app/services/observability/shopify-runtime-observability.server.ts`, `app/services/webhooks/checkout-normalization.ts`, `app/shopify.server.js`, `package.json`, `package-lock.json`, `tests/unit/platform-configuration/shopify-oauth-bootstrap.test.ts`, `tests/unit/routes/shopify-consent-route.test.ts`, `tests/unit/server-error-privacy.test.ts`, `tests/unit/webhooks/shopify-normalization.test.js`, `tests/unit/webhooks/shopify-webhook-ingress.service.test.js`.
- Deleted: `app/services/shopify-consent/marker.ts`, `app/services/shopify-consent/shopify-consent.server.ts`, `tests/integration/shopify-consent.redis.integration.test.ts`.

The `@modainteract/moda-interact-shared` dependency remains pinned at `5.3.0`; no new dependency was added.

### Validation evidence

- Receipt and route-focused Vitest selection: 6 files, 98 tests passed.
- Shopify webhook unit regression suite: 15 files, 168 tests passed.
- `npm run test:shopify-webhooks:redis`: 2 files, 9 tests passed, including publication and queue telemetry regressions.
- Targeted ESLint on changed app and unit-test files passed.
- `npm run build` passed with a locally generated ephemeral receipt key; no key was persisted. Existing dependency/chunk warnings remain.
- `npm run typecheck` still reports five implicit-`any` errors in unchanged `app/routes/webhooks/root/route.jsx`; no changed file was reported.

### Configuration and limits

Deployment must configure the same `SHOPIFY_CONSENT_RECEIPT_KEY_V1` value in the Shopify app and Background services. It must be canonical unpadded base64url for 32 random bytes; app startup fails closed if invalid or missing. No production key was generated or committed. Valid receipts can be replayed into the same checkout attribute; this is the approved limitation, not replay prevention.

No live Shopify store or Plus checkout was available. Checkout authentication tests use explicit SDK-boundary mocks; no live Plus functionality is claimed. No live provider error occurred, so no provider error evidence is reported; tests verify session-token redaction in SDK error output. The `cart/update.js`, checkout-note, and authoritative GraphQL `customAttributes` readback fixtures were not exercised in S002 because those browser/checkout writers and webhook recovery readers are owned by S003/S004/B001 and are not implemented here. Architect review should confirm whether those cross-task fixtures are required before S002 acceptance.

### Attempt 3 result

Replaced Attempt 2's unapproved HMAC receipt/key design with the approved `@modainteract/moda-interact-shared` credential AEAD and existing keyring. Receipts use the contract's `v1.<keyId>.<nonce>.<ciphertext>.<authTag>` envelope, canonical plaintext and AAD, strict framing/base64url validation, a 512-byte attribute limit, and customer/shop/kind/token binding. Issuance uses the configured active key; verification resolves the envelope key ID from the configured keyring so retained keys support rotation, while malformed configuration or removed keys fail closed. No dedicated receipt secret, local AES implementation, Redis state, database state, TTL, or dependency was added.

Updated the signed App Proxy boundary to accept safe merchant-configured `path_prefix` values under `/a`, `/apps`, `/community`, or `/tools`, with a nonempty safe subpath, instead of assuming one fixed prefix. Returning-shopper status requires current native Shopify consent evidence and continues to honor STOP/no-contact fences; it does not infer a new enum or grant consent from legacy records with insufficient source evidence.

The implementation branch is `task/ARCH-077-SHOPIFY-002`, commit `96ad35f`. The launcher claimed Attempt 3 and pushed the parent task claim as `768d8984ae605880b2f3dc8ba4a688259a77356b`.

### Changed files

- Updated: `app/services/shopify-consent/consent-receipt.server.ts`, `app/routes/shopify/consent/route.ts`, `app/routes/shopify/checkout-receipt/route.ts`, `app/shopify.server.js`, `tests/unit/services/shopify-consent-receipt.service.test.ts`, `tests/unit/routes/shopify-consent-route.test.ts`, `tests/unit/platform-configuration/shopify-oauth-bootstrap.test.ts`, `tests/unit/server-error-privacy.test.ts`.
- `@modainteract/moda-interact-shared` remains pinned at `5.3.0`; its published Node keyring and credential AEAD APIs are used.

### Validation evidence

- Focused consent, route, OAuth bootstrap, and privacy Vitest selection: 4 files, 46 tests passed.
- Shopify webhook unit regression suite: 15 files, 168 tests passed.
- `npm run test:shopify-webhooks:redis`: 2 files, 9 tests passed.
- Targeted ESLint on changed app and unit-test files passed.
- `npm run build` passed; existing dependency/chunk warnings remain.
- `npm run typecheck` still reports five implicit-`any` errors in unchanged `app/routes/webhooks/root/route.jsx`; no changed file was reported.
- `git diff --check` passed.

### Configuration and limits

The app uses the existing `MODA_ENCRYPTION_ACTIVE_KEY_ID` and `MODA_ENCRYPTION_KEYS_JSON` configuration. During rotation, old key IDs must remain in the keyring until receipts issued with them are no longer relevant. No new secret or receipt-specific startup gate is required.

Producer-side tests cover the Shared AEAD contract, binding, key rotation, malformed/corrupt envelopes, the size bound, duplicate matching attributes, status-source checks, safe prefixes, and stale/future App Proxy timestamps. The Background consumer task's independent contract test was not changed or run from this repository. No live Shopify store, Plus checkout, or authoritative Shopify GraphQL `customAttributes` readback was available; the producer fixture does not establish deployed cross-service transport compatibility. S003/S004/B001 remain responsible for their owned writers/readback paths, and architect acceptance should confirm consumer-side parity before dependent work proceeds. No live provider error occurred; the privacy test verifies session-token redaction in SDK error output.
