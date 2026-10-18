---
id: ARCH-043-SHOPIFY-002
architecture_id: ARCH-043
title: Wire all Shopify platform configuration consumers
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: review
priority: 40
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-043-SHOPIFY-001
  - ARCH-043-ADMIN-002
enables:
  - ARCH-043-GATEWAY-001
  - ARCH-043-SYSTEM-TEST-001
created: 2026-10-17
updated: 2026-10-18
---

# Wire all Shopify platform configuration consumers

## Architecture

- Parent: `docs/architecture/ARCH-043-database-managed-platform-configuration.md`.
- Source reader: `ARCH-043-SHOPIFY-001`.
- Admin secure secret import/rotation: `ARCH-043-ADMIN-002`.
- Owner: `moda_app` / `moda-interact`; **defined but not materialised**.

## Objective

Replace Shopify's applicable environment-backed configuration consumption with the accepted `SHOPIFY-001` service in **Merchant Knowledge uploads, Shopify OAuth/bootstrap, and Shopify Partner billing**, without introducing another configuration reader.

## Context

In the 17 October snapshot:
- `app/services/merchant-knowledge/r2-config.server.ts` reads `MERCHANT_KNOWLEDGE_R2_ENDPOINT`, `MERCHANT_KNOWLEDGE_R2_BUCKET` and `MERCHANT_KNOWLEDGE_MAX_UPLOAD_BYTES` alongside external R2 credentials. `upload.server.ts` uses that synchronous configuration for both intent signing and finalisation.
- `app/shopify.server.js` builds `shopifyApp({...})` **synchronously at module evaluation**, using `SHOPIFY_API_KEY` and `SHOPIFY_API_SECRET`, then exports bound `authenticate`, `login`, `registerWebhooks`, session storage and other helpers.
SHOPIFY-001 provides three typed service readers; this task adapts call sites and proves that OAuth secrets are available **before** this synchronous client is constructed.

## Scope

1. Integrate `requireMerchantKnowledgeR2Configuration()` into the existing server-side R2/upload configuration flow as one six-field sealed operation snapshot; preserve existing upload security, tenant scoping, plan entitlements and R2 signing operations.
2. Integrate `requireShopifyOAuthCredentials()` with a verified load-before-serve bootstrap path for `shopifyApp` construction. Adapt startup/module import sequencing only as required for the deployed React Router runtime; preserve existing Shopify session, webhook and OAuth behaviour.
3. Replace Partner API identity/token reads in `app/services/billing/providers/shopify-billing.provider.ts`, covering **both** `getActiveSubscription()` and the other Partner GraphQL operation in that provider. Obtain the complete `{accessToken,organizationId,appId,apiVersion?}` tuple from `requireShopifyPartnerCredentials()` for each Partner operation. Keep existing billing correlation, subscription lifecycle, duplicate/idempotency protections, error handling and provider response shapes unchanged. Do not conflate Partner credentials with Shopify OAuth or merchant session credentials.
4. Review `app/services/billing/hosted-plan-change.service.ts` and `app/services/billing/subscription-activation.service.ts` for any indirect calls into the provider, and preserve their existing workflows without introducing duplicate credential parsing, new provider clients or network calls inside database transactions.
5. Update relevant existing server-side callers and tests; ensure all affected readers use SHOPIFY-001 rather than a new local `process.env` parser, extra Prisma query or duplicated decryptor.
6. Document safe activation, restart/rotation limitations and rollback procedures; remove corresponding **application runtime** environment reads after source-level cutover and automated validation. Live/deployed verification is not a task acceptance gate.

## Out of Scope

- No new `PlatformConfiguration` tables, migrations, Shared package, Admin editor or new decryptor.
- R2 credentials move only through the accepted server-side sealed `merchant.knowledge.r2` reader; Shopify scopes/app URL, CLI tooling configuration and the external unseal root remain deployment-owned.
- Do not change unrelated Shopify webhook filtering/recovery workflows or Background's separate OAuth/token-refresh integration.
- No new merchant UI or tenant-access API for platform secrets.

## Requirements

### Merchant Knowledge integration

- Extend or adapt `app/services/merchant-knowledge/r2-config.server.ts` and `upload.server.ts` to obtain the complete sealed `endpoint`, `bucket`, `accessKeyId`, `secretAccessKey`, `maxUploadBytes` and `maxXlsxUncompressedBytes` snapshot from SHOPIFY-001 on the server; **do not combine it with external R2 credentials after cutover**. Keep existing R2 client, HTTPS/host checks, upload format limits, size caps and signed request expiry.
- The existing upload-intent/finalisation endpoints continue to authenticate and resolve shop identity through `settingsAccess()`, enforce plan entitlement and verify object metadata. No browser receives R2 key material or config envelope. Do not create new remote signing endpoints without a separate architecture decision.
- A missing, invalid or unsafe policy fails without issuing a signed upload. Allow R2 endpoint and bucket edits; their data-migration and in-flight-asset handling are owned by separately agreed tasks, not ARCH-043. Keep a single fetched policy within one operation; document and test in-flight object/bucket continuity. Do not silently corrupt existing assets if storage settings change (the current `MerchantKnowledgeUploadedAsset` has `objectKey`, not a bucket snapshot).
- Fetch and validate the current policy via SHOPIFY-001 for each upload operation, without cross-operation caching. Preserve environment isolation and explicit operational configuration (no invented production bucket).

### Shopify Partner API / billing integration

- Use `requireShopifyPartnerCredentials()` from SHOPIFY-001 for each actual Partner GraphQL operation, **not** an independently invented reader or environment lookup. `accessToken`, `organizationId`, `appId` and optional `apiVersion` must be from the same DB record/revision.
- Remove `SHOPIFY_PARTNER_ACCESS_TOKEN`, `SHOPIFY_PARTNER_API_TOKEN`, `SHOPIFY_PARTNER_ORG_ID`, `SHOPIFY_PARTNER_ORGANIZATION_ID`, `SHOPIFY_APP_ID` and `SHOPIFY_PARTNER_API_VERSION` as runtime credential reads **where present in the Shopify repository**, only after tested cutover. An approved default Partner API version is permitted when optional `apiVersion` is absent; it must never silently select another credential source.
- Preserve both existing `ShopifyBillingProvider` Partner API operations, including session-independent Partner billing calls, errors, provider data contracts and idempotency. Test revoked/rotated/unavailable configuration and ensure no token reaches browser data, logs or error responses.

### Shopify OAuth bootstrap integration

- Use the SHOPIFY-001 sealed `shopify.oauth` reader to provide **both** `apiKey` and `apiSecret` before constructing the existing `shopifyApp({...})` object. Preserve synchronous exported auth helpers (`authenticate`, `login`, `registerWebhooks`, `sessionStorage`) and existing session/route imports; do not export half-initialised clients or use placeholder secrets.
- Prove a concrete startup mechanism compatible with the actual package scripts / React Router server module load (e.g., a same-process preinitialisation mechanism verified by tests). Do not assume an asynchronous database lookup is safe inside the current synchronous module expression; never start serving protected routes before bootstrap is completed.
- On absent, revoked, malformed, undecryptable or wrong-environment secret, **fail closed** at bootstrap/readiness (no blank key, hidden env fallback or unauthenticated bypass). On database/unseal outage, retain only explicitly approved bounded rollback semantics; no indefinite stale credential acceptance.
- Preserve Shopify client, session and webhook HMAC behaviour, scoped `apiKey` exports, and token refresh interactions. Cover fail-closed, startup ordering and credential revision behaviour with existing source-level regression tests. Document signing-secret/rotation limitations without inventing multi-key support. Deployed OAuth sessions and live webhook-HMAC exercises are not mandatory for this task.
- Require that `ARCH-043-ADMIN-002` has securely imported active `shopify.oauth` values before a DB-only release. Safe local development/bootstrap must be documented without placing OAuth secrets into browser output or source control.

### 18 October upload consumer correction (controlling)

`app/services/merchant-knowledge/r2-config.server.ts` and `upload.server.ts` must consume `SHOPIFY-001.requireMerchantKnowledgeR2Configuration()` as **one immutable six-field operation snapshot**, without merging legacy `merchantKnowledge.upload` or R2 credential environment values. Validate upload intent/finalisation, signed headers, shop authentication, tenant caps, existing assets and safe bucket-location changes. Browser response must never include `accessKeyId`, `secretAccessKey` or sealed envelope. Legacy config and environment fallbacks cannot silently override the selected row. The Shopify OAuth/startup requirements of this task are unchanged.


## Work Items

- [x] Identify upload call sites and adapt `r2-config.server.ts` / `upload.server.ts` to consume the Shopify configuration service; preserve validated R2 signing and tenant checks while moving credentials to the single sealed record.
- [x] Test upload-intent and finalisation with valid/invalid/missing policies, fresh revisions after editable R2 location changes, pending uploads rejected against a newly selected bucket, and environmental mismatch.
- [x] Inspect `shopifyApp` module evaluation; implement and unit-test the SHOPIFY-001 load-before-construction bootstrap.
- [x] Adapt `app/shopify.server.js` and startup composition; preserve existing synchronous exports after module initialization and Shopify auth semantics.
- [x] Replace both Partner operations in `app/services/billing/providers/shopify-billing.provider.ts` with `requireShopifyPartnerCredentials()`; test Partner queries/version, billing regression, rotation, revocation and no mixed credential sources.
- [x] Review indirect billing callers and verify no listed Shopify configuration credential environment reads remain under application runtime `app/**`.
- [x] Publish startup/deployment ordering, active credential provisioning, restart/rotation limitations and rollback guidance, and the exact application-runtime environment-variable retirement handoff for GATEWAY-001. The committed cutover note distinguishes Shopify CLI and diagnostic tool settings.
- [x] Record launcher-resolved branch/worktree synchronization and automated validation evidence below. The historical live-check follow-up is superseded by the controlling Architect Amendment; no live/deployed check is claimed or required.

## Interfaces / Contracts

- Consume only `ARCH-043-SHOPIFY-001` server-only typed readers (R2, OAuth and Partner); do not duplicate query, AAD or decryption code or introduce a config cache.
- `ARCH-043-ADMIN-002` owns secure writer/import; current `shopify.oauth` envelope and frozen AAD contract stay unchanged.
- Keep existing `shopifyApp` exported session/auth/webhook helpers and existing Merchant Knowledge upload route/error contracts.
- Do not change `MerchantKnowledgeUploadedAsset` schema, `Shop`/session schema or existing encrypted Commerce credential formats.

## Dependencies

- `ARCH-043-SHOPIFY-001`
- `ARCH-043-ADMIN-002`

## Enables

- `ARCH-043-GATEWAY-001`
- `ARCH-043-SYSTEM-TEST-001`

## Acceptance Criteria

- [x] Shopify Merchant Knowledge upload/finalise and R2 signing use validated database policy, with the sealed R2 credentials and original security checks preserved.
- [x] Each new upload request reads the current editable R2 endpoint/bucket values; an in-flight upload targeting a newly selected bucket fails closed, and historical asset location remains with the separate storage-relocation tasks.
- [x] Shopify OAuth key/secret are loaded and decrypted **before** any `shopifyApp` construction; unit tests prove fail-closed module initialization and no unsafe environment fallback.
- [x] Both Shopify Partner billing operations consume a fresh, atomic `shopify.partner` tuple through SHOPIFY-001, preserve existing billing behaviour, and fail closed on missing/revoked/invalid secrets without mixing database and environment fields.
- [x] Automated OAuth bootstrap, webhook-route/HMAC, tenant-isolation and existing Shopify regression tests pass; missing/tampered/revoked secrets cause closed failures in tested paths. Live Shopify login/session or webhook delivery evidence is not required.
- [x] The committed cutover note documents startup ordering, active credential provisioning, restart/rotation limitations, rollback guidance and Gateway environment-variable retirement; CLI infrastructure variables are not removed indiscriminately. No deployed runtime execution evidence is required.

## Validation

- [x] Merchant Knowledge upload-intent/finalisation tests and R2 security tests
- [x] Shopify OAuth bootstrap cold-start/failure/restart-rotation unit tests and webhook route regression tests
- [x] Shopify Partner billing provider and indirect subscription lifecycle regression tests for both Partner queries, version default, rotation and revoked credentials
- [x] Typecheck, lint, production build and relevant repository-defined **automated** regression tests; deployed/manual OAuth, webhook HMAC, readiness and rotation checks are not required
- [x] `git diff --check`, worktree/branch evidence and application runtime environment-read removal check

## Stop Condition

Complete defined integrations and validation, update task/Completion Report to Review, return to `moda_architect`, and STOP. Do not perform Gateway cleanup, system testing or `_index.md` edits.

## Implementation Notes

This task absorbs the previous `ARCH-043-SHOPIFY-003` Partner credential consumer. The old task is removed from active discovery, and downstream Gateway/System Test depend on SHOPIFY-002 for **all three** Shopify configuration cutovers. Keep runtime implementation exclusively in `moda-interact`; Admin manages credential import, Background owns its separate Partner provider, and Gateway owns environment-variable removal.


Prefer modular adapters over an oversized `shopify.server.js` or a generic config framework. Inspect the real Shopify SDK and React Router startup contract first. If authenticated load-before-serve cannot be achieved without a new entrypoint/service lifecycle decision, **report the architectural blocker** rather than writing a partially initialised or insecure fallback. Reuse approved Shared logging and ARCH-039 cryptography. Treat R2 endpoint/bucket changes as an explicit in-flight upload safety concern, not an invisible generic config refresh.

## Completion Report

### Status

Developer Self-Review Accepted — Attempt 1, 2026-10-18. Updated acceptance criteria are satisfied by published implementation and cutover-note commits plus automated validation. Per `completion_mode: developer`, status is `review` pending the explicit developer completion decision; attempt remains unchanged.

### Files Changed

Implementation commit range `dae1fc7..815c3c1` on `origin/task/ARCH-043-SHOPIFY-002` changes the Shopify OAuth bootstrap, Merchant Knowledge R2 configuration/upload callers, Partner billing provider, affected route configuration, Vite SSR target, focused tests, and `docs/arch-043/SHOPIFY-002-cutover-validation.md` (published by `815c3c1`). No task-owned staged implementation changes remain.

### Work Completed

Wired the sealed SHOPIFY-001 R2, OAuth and Partner readers into the Shopify runtime. Both Partner GraphQL operations use one fresh credential tuple. Upload intent/finalisation use one six-field snapshot, including fail-closed behavior when an in-flight object is absent from a newly selected bucket. OAuth module initialization awaits the sealed record before constructing/exporting the Shopify SDK. No retired configuration credential reads remain under application `app/**`. Published the startup/provisioning/rotation/rollback and Gateway environment-variable retirement handoff.

### Validation Results

Passed from the canonical implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-043-SHOPIFY-002`:

- `npm test -- tests/unit/platform-configuration tests/unit/merchant-knowledge-upload.test.ts tests/unit/services/shopify-billing.provider.test.ts tests/unit/routes/reinstalling-route.test.ts` — 6 files, 54 tests passed.
- `npm test -- tests/unit/platform-configuration/shopify-oauth-bootstrap.test.ts tests/unit/webhooks/webhooks-route.test.js tests/unit/webhooks/shopify-webhook-ingress.service.test.js tests/unit/webhooks/shopify-webhook-metadata.test.js tests/unit/services/billing/subscription-activation.service.test.ts tests/unit/services/billing/hosted-plan-change.service.test.ts tests/unit/services/billing/subscription-sync.test.ts tests/unit/services/billing/shopify-billing-operation.service.test.ts` — 7 files, 86 tests passed.
- Final combined automated regression run after the acceptance amendment: 12 files, 137 tests passed, covering the platform-configuration suite, upload, Partner provider, OAuth bootstrap, webhook routes and billing lifecycle.
- `npm run typecheck` — passed.
- `npm run lint` — passed.
- `npm run build` — passed; emitted dependency annotation and large-chunk warnings.
- `git diff --check origin/main...HEAD` — passed.
- Scoped runtime-credential search under `app/**` — no matches for the retired Shopify Partner, OAuth or Merchant Knowledge R2 environment keys.

Not run: optional disposable PostgreSQL upload integration and live/deployed React Router readiness, Shopify login/session, webhook delivery, and deployed rotation/rollback checks. The controlling Architect Amendment excludes those as acceptance gates; no result is claimed for them.

### Deviations

The earlier Changes Requested report is preserved as review history and superseded by the controlling Architect Amendment and the latest Accepted self-review. The cutover note is now committed and pushed; no live/deployed evidence is represented as completed.

### Assumptions

ADMIN-002 remains the secure writer/import owner. The cutover document makes active-value provisioning a precondition for a DB-only deployment; deployed provisioning is operational, not an implementation acceptance test under the controlling amendment.

### Unresolved Issues

No known task acceptance issues remain. Live/deployed readiness, session, webhook delivery and rotation checks are optional operational follow-up under the controlling amendment, not blockers. Gateway owns the actual deployment environment-variable removal.

### Architectural Concerns

No source-level or task-acceptance blocker remains. Existing fail-closed behavior is preserved; the note describes deployment preconditions without claiming live verification.

## Architect Review

### Review Status

Developer Self-Review — Accepted. Explicit developer completion is pending.

### Review Notes

The published implementation revision `815c3c1` is present on `origin/task/ARCH-043-SHOPIFY-002`; cutover note and Gateway variable inventory are committed. The final focused regression run passed 137 tests in 12 files; typecheck, lint, production SSR build and diff checks passed. OAuth bootstrap tests prove construction ordering, fail-closed initialization and restart-based revision loading; upload tests cover the sealed snapshot, fresh policy reads, tenant checks and bucket-change failure; Partner and indirect billing tests pass. The controlling Architect Amendment excludes live/deployed checks from acceptance, and none are claimed.

### Reviewed Files

Implementation diff `origin/main..815c3c1` in `moda-interact`, including `app/shopify.server.js`, Merchant Knowledge R2/upload services, Shopify billing provider, affected routes, Vite SSR configuration, focused tests and committed cutover note.

### Validation Reviewed

Final focused automated regression: 137 passed in 12 files; typecheck, lint, production build and `git diff --check` passed. Optional disposable PostgreSQL upload integration and live/deployed checks were not run and are not required by the controlling amendment.

### Architecture Conformance

The published source follows the SHOPIFY-001 reader contract and preserves separate OAuth and Partner credentials. It does not introduce a new decryptor, schema, cache or browser secret exposure. The source-level behavior and committed operational handoff conform to the amended acceptance criteria.

### Follow-up

Review is Accepted. The explicit developer completion decision is recorded in the subsequent task update. Do not perform Gateway cleanup or System Test work from this task update.

### Developer Self-Review

- Decision: Accepted
- Attempt: 1
- Implementation revision: `815c3c1` (`origin/task/ARCH-043-SHOPIFY-002`)
- Parent task branch: `task/ARCH-043-SHOPIFY-002`, synchronized with `origin/task/ARCH-043-SHOPIFY-002` before this report update.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-043-SHOPIFY-002`.
- Evidence: 137 focused tests across 12 files, typecheck, lint, production SSR build, diff check, and runtime environment-read scan passed. Cutover note published in `815c3c1`.
- Findings: No known incomplete acceptance criteria remain under the controlling Architect Amendment. Live/deployed checks are explicitly not task gates and are not claimed. Explicit developer completion is pending.

### Architect Amendment — 2026-10-18 (controlling Changes Requested scope)

- **Superseded:** The historical Attempt 1 Completion Report, Architect Review and Developer Self-Review remain preserved as review history, but their instruction to perform and record **live/deployed runtime checks** is withdrawn as a requirement for `ARCH-043-SHOPIFY-002`. In particular, deployed `@react-router/serve` readiness, real Shopify OAuth session/login, live webhook HMAC delivery, deployed credential rotation/restart/rollback and disposable PostgreSQL upload-integration demonstrations are **not mandatory acceptance evidence**. Do not report those checks as passed unless actually performed.
- **Still required:** Existing automated OAuth bootstrap/fail-closed, webhook-route, R2, Partner billing and credential revision tests, plus typecheck, lint and production build, remain the implementation validation contract. Existing runtime security behaviour is not weakened by this change.
- **Outstanding Changes Requested:** Publish the staged `docs/arch-043/SHOPIFY-002-cutover-validation.md` note as the durable startup/provisioning/rotation and Gateway handoff, then update the Completion Report using available automated validation and task/worktree evidence. No live-runtime result is required for the note to be published.
- **Task state unchanged:** `status: ready`, `attempt: 1`, `execution_mode: developer`, `completion_mode: developer`. The historical Changes Requested decision remains until the remaining non-live requirements are satisfied and the task receives its authorised review/completion decision. This amendment does not constitute acceptance.

## 17 October 2026 ARCH-043 extension (architect-owned amendment)

Replace R2 endpoint, bucket, credentials and size reads with one sealed `merchant.knowledge.r2` record; no duplicate `merchantKnowledge.upload` policy after cutover. Validate endpoint/SSRF and relocation safety. Requires ADMIN-002 and verification of the developer forward migration before cutover.

## Developer execution takeover amendment

This ready task was explicitly invoked through `/moda_developer_create`, transferring execution ownership to the developer. `assigned_agent: moda_app` remains unchanged for domain ownership. Completion is developer-controlled; the task will stop at Review for developer reconciliation and architect review.
