---
id: ARCH-049-WOOCOMMERCE-002
architecture_id: ARCH-049
title: Add merchant-initiated WooCommerce Store branding synchronisation
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: ready
**Materialised developer-executed task definition.** Its canonical parent task worktree is recorded in the Completion Report. No implementation worktree or execution claim exists yet.
priority: 35
executor: null
claimed_at: null
attempt: 0
depends_on: ["ARCH-049-WOOCOMMERCE-001"]
enables: ["ARCH-049-SYSTEM-TEST-001"]
created: 2026-10-27
updated: 2026-10-27
---

# Add merchant-initiated WooCommerce Store branding synchronisation

## Architecture

Architecture: `ARCH-049` — `docs/architecture/ARCH-049-shopbrand-public-media-configuration.md`.

Coordinator: `moda_architect`. Owner: `moda_woocommerce` in `moda-interact-woocommerce/`.

**Portable canonical definition — defined but not materialised in the developer's Git task worktrees.** A task worktree/branch, execution claim, implementation or push must not be inferred from this patch. Materialise only through the normal task launcher after prerequisite completion.
**Canonical task definition materialised, execution not started.** The parent branch is `task/ARCH-049-WOOCOMMERCE-002`; no implementation worktree or execution claim exists. The task became ready after accepted completion of WOOCOMMERCE-001.

## Objective

Give a connected WooCommerce merchant a functioning **Store branding** panel with a **Sync branding** action and trustworthy last-accepted-sync status, using the existing ARCH-049-WOOCOMMERCE-001 publisher without introducing automatic brand-change sync or daily reconciliation.

## Context

ARCH-049-WOOCOMMERCE-001 captures Site Identity branding on first authenticated connection (or first eligible upgrade runtime), publishes `woo.shop-brand.v1` via Action Scheduler and bounded API retries, and exposes `ShopBrand\Publisher::requestSync()` for an explicit future trigger. It intentionally does **not** react to WordPress logo/theme changes or schedule daily Woo reconciliation. The current WooCommerce merchant UI has a `RecoverySettingsScreen`, client/controller patterns, and administrator-only WordPress REST routes. A scheduled capture is not evidence that the hosted API accepted it; HTTP acceptance does not prove Background has finished preparing WhatsApp-ready R2 media.

The merchant first changes their site's Site Name, Site Logo or Site Icon in WordPress, then explicitly selects **Sync branding** within the Moda Interact Recovery Settings screen. No Wordpress branding editor is added here.

## Scope

- Add the Store branding panel to the connected `RecoverySettingsScreen`; include contextual explanation, last accepted publication time, queued/retrying/failure state and the actual **Sync branding** button.
- Add one capability-protected WordPress REST read/command controller for viewing per-installation sync status and requesting capture through the **existing** publisher. No hosted API modification or new externally callable/background-driven merchant endpoint.
- Add a small, non-autoloaded WordPress options-backed status store scoped to the current installation identity, with separate requested, queued, retrying, accepted and terminal failure evidence. Capture hosted API successful acknowledgement from the existing publisher; never claim success from merely enqueuing.
- Use the existing client/controller/page session patterns to perform one server-side command and observe completion without persistent periodic sync. Include focused PHP and JS tests, and plugin i18n/build validation.

## Out of Scope

- Changing the `woo.shop-brand.v1` schema, hosted `POST /v1/woocommerce/shop-brand`, PostgreSQL ShopBrand schema, Background/R2 processor, IMAGE-template authoring, cloud infrastructure, or Shopify branding flow.
- Uploading image bytes from the browser, editing WordPress branding on this panel, direct connection from JS to Moda API, user-supplied tenant identifiers, browser-exposed installation credentials, or a public unauthenticated WordPress route.
- Reintroducing automatic `blogname`, `site_logo`, `site_icon`, theme, attachment/metadata hooks or daily `RECONCILE_ACTION`; merchant-controlled sync and existing initial capture are the only Woo source-publication triggers (aside from bounded retries).
- A new media-processing/READY-status lookup; the UI reports publication acceptance, not Meta/R2-ready images.

## Requirements

### R1. WordPress REST read and command boundary

Create `includes/Rest/ShopBrandSyncController.php` (or existing repository-equivalent name) and register from `includes/Runtime.php`. Under `moda-interact/v1`, expose:

- `GET /merchant/shop-brand/sync`: current-installation publication state and last accepted timestamp, **no browser-provided tenant identity**.
- `POST /merchant/shop-brand/sync`: no business input; request an asynchronous `ShopBrand\Publisher::requestSync()` capture and return HTTP **202** when queued or coalesced, **not** a false `SYNCED` response. Recognised command statuses: `QUEUED`, `ALREADY_QUEUED`.

Use `permission_callback` with `current_user_can('manage_woocommerce')` and the existing authenticated wp-admin REST cookie/`wp_rest` nonce (`@wordpress/api-fetch`) path. Reject non-empty JSON/body/query business input (allow only WordPress's existing `_locale=user` convention); do not accept `shopId`, installation ID, source URL or uploaded branding. Validate the local `InstallationStore` state and canonical site URL through `SiteIdentity` before reading status or scheduling capture. For disconnected/invalid/changed installations fail closed with the existing `RECONNECT_REQUIRED`, `LOCAL_STATE_INVALID`, `SITE_URL_CHANGED` distinctions and suitable HTTP 401/409. Missing Action Scheduler or enqueue failure must return a typed 503 failure, **never** report queued/synced. Use private/no-store REST responses, bounded safe error codes, and avoid leaking exception bodies or secrets.

### R2. Truthful durable status semantics

Add `includes/ShopBrand/SyncStatusStore.php` (or closely scoped equivalent) with a non-autoloaded WordPress option and tests. Record only bounded operational identifiers/timestamps and safe outcomes; **never** store provider credentials, full untrusted URLs or image payloads. Scope state by the current `installationId` and canonical site identity; do not display stale status after reconnect/site URL change. The initial capture and explicit manual capture must use the same status reporting mechanism.

Define read projection (exact field names) as:

```json
{
  "status": "NEVER_SYNCED | QUEUED | RETRYING | ACCEPTED | FAILED",
  "lastRequestedAt": null,
  "lastAcceptedAt": null
}
```

For actual responses, `status` MUST be one enum value, timestamps MUST be either UTC ISO-8601 strings or `null`, and no extra installation/shop identifiers are exposed. `lastAcceptedAt` advances only after the existing `ModaApiClient::publishShopBrand()` validates a hosted API success response with `status: updated` or `unchanged`. `QUEUED` is Action Scheduler admission only; `RETRYING` is bounded transient publication failure with retry successfully scheduled; `FAILED` means terminal provider/scheduler failure or exhausted retries. Preserve the prior accepted timestamp when a newer request fails. The bootstrap marker from WOOCOMMERCE-001 indicates initial capture was scheduled, **not** accepted; never reuse it as a success stamp. Ensure older, delayed, duplicate or stale-installation completions cannot mark a newer request accepted, erase a newer failure or cross installation boundaries. A manual action received during an in-flight capture must preserve an eventual capture of the settings current at/after that request, rather than silently losing the merchant's refresh to coalescing.

The status store and publisher should use the existing WooCommerce/PHP bounded semantic logger; log database option-write failures and Action Scheduler failures using safe reason codes, do not silently swallow exceptions, and keep logging/telemetry failure isolated from checkout. This PHP runtime must **not** import the Node-only shared logger package.

### R3. Merchant UI and action lifecycle

Create a focused UI component, e.g. `src/recovery-settings/store-brand-panel.js`, and wire it into the existing `RecoverySettingsScreen` under Moda Interact → Recovery Settings, not a parallel app. Follow existing `src/page/controller-factory.js`, `controller-session.js`, `use-moda-page-state.js`, `page-actions.js`, and `connected-workspace.js` separation. Add a dedicated client such as `src/shop-brand-sync-client.js` and controller such as `src/shop-brand-sync-controller.js`, keeping HTTP outside display components and reusing `@wordpress/api-fetch` nonce handling.

- Heading: **Store branding**. Explain the merchant edits Site Name, Site Logo and Site Icon in native WordPress and can then choose **Sync branding**.
- Button: **Sync branding**, enabled only for a connected installation with no unresolved in-flight command; disable during request to prevent duplicate submissions. Show a separate Refresh status action or bounded post-command status rechecks, with cleanup on unmount/navigation/disconnect (no daily or open-ended polling).
- Show **Last synchronised** only when `lastAcceptedAt` exists, with a real user-localised date/time from the timestamp; otherwise **Not synchronised yet**. Explain that this means the brand details were **accepted by Moda**, while background image processing may still be pending; never display unconditional "Your branding is synchronised" for queued/failed/not configured states.
- Distinguish `QUEUED`, `RETRYING`, `ACCEPTED`, `FAILED`, missing scheduler, connection required and read failure with accessible `role=status` / `role=alert` messages. Provide actionable retry (Sync branding again) for terminal failures. Preserve previously accepted date when newer attempt is pending/failed.
- Use WordPress i18n (`__`, text domain `moda-interact`), existing UI styling and responsive patterns; update required translation catalogues/tooling under the existing 20-locale policy. Do not render merchant-provided raw HTML or expose cross-shop information.

### R4. Reliability and scope isolation

Explicit sync must only enqueue existing Action Scheduler capture, not synchronously POST the hosted API from the browser or PHP REST request. Preserve initial connection behaviour, bounded publication retries, deterministic event IDs, stable `observedAt` per retry, site/installation checks and protected checkout latency. The new feature must not register new scheduled recurring jobs or change Shopify/BG002's separate source/media reconciliation mechanisms. Do not create a competing logger or separate publishing pipeline.

## Work Items

- [ ] Inspect the accepted WOOCOMMERCE-001 publisher contract and existing WordPress REST/client/session patterns in the launcher-resolved task worktrees.
- [ ] Implement and test installation-scoped `ShopBrand\SyncStatusStore`, integrated with initial/manual capture, API acceptance and bounded retry/failure paths.
- [ ] Implement and register the capability- and nonce-protected GET/POST REST controller with no-tenant-input contract and safe failure responses.
- [ ] Implement client, state controller, connected-session lifecycle and merchant-facing Store branding panel on Recovery Settings.
- [ ] Add PHP controller/publisher integration tests, JS client/controller/view tests and Local WP merchant action test evidence.
- [ ] Update relevant PHP syntax-test registration, translations, source docs and Completion Report; no unrelated refactors.

## Interfaces / Contracts

**Existing internal producer:** `ShopBrand\Publisher::requestSync(): bool` in `includes/ShopBrand/Publisher.php` (WOOCOMMERCE-001). The return value signals Action Scheduler admission, not provider acceptance. Small additive support for coalesced/admission status is permitted within WooCommerce owner boundaries; do not change `woo.shop-brand.v1` or hosted API semantics.

**Hosted API:** `ModaApiClient::publishShopBrand()` → authenticated `POST /v1/woocommerce/shop-brand` with immutable `woo.shop-brand.v1` and validated result `{ "status": "updated" | "unchanged" }`. Consumer of API-001 contract; no new API task required for the local manual trigger. Actual integrated publication still requires the hosted API to be deployed.

**Local WordPress REST:** GET state and POST enqueue at `/moda-interact/v1/merchant/shop-brand/sync`, protected by the current logged-in merchant capabilities and REST nonce. GET returns exactly `status`, `lastRequestedAt`, `lastAcceptedAt`; POST returns exactly `status: QUEUED | ALREADY_QUEUED` for HTTP 202. Error envelopes are safe enum codes and appropriate HTTP errors, with cache-control `private, no-store`.

**Local persistence:** non-autoloaded WP option keyed by the authenticated installation identity, never browser-owned. Status updates are idempotent and ordered for overlapping captures/retries; old installation observations cannot appear after reconnect.

**Presentation:** `src/recovery-settings/store-brand-panel.js` (suggested) and existing `src/page/*` controller/React session. No new separate dashboard or shared package required.

## Dependencies

- `ARCH-049-WOOCOMMERCE-001` — complete and accepted at developer Attempt 2. The accepted correction-only publisher contract is reconciled in the dependency task snapshot on this branch. This satisfies the sole explicit dependency and makes this task ready; no implementation attempt has been claimed.

The API-001 fixture is sufficient to implement/test the UI and local REST contract. Live hosted API integration is required at system-test time, not a second production implementation dependency here.

## Enables

- `ARCH-049-SYSTEM-TEST-001` — terminal integrated certification now also tests the merchant-triggered Woo refresh and last-accepted status.

## Acceptance Criteria

- [ ] A connected merchant sees Store branding on Recovery Settings, with meaningful copy and a correct last-accepted timestamp or never-synchronised state.
- [ ] Clicking Sync branding invokes one authorised WP REST command, queues a capture of current WP Site Identity and returns 202; status remains QUEUED until hosted API acceptance.
- [ ] A successful hosted API `updated`/`unchanged` response stores a UTC acceptance timestamp and moves the latest request to ACCEPTED; failed/retrying commands never claim success or erase the last prior acceptance.
- [ ] A changed WordPress logo is published **only after** the merchant explicitly requests sync; no brand option/attachment hook or recurring Woo reconciliation job remains.
- [ ] An existing queued/in-flight capture plus a later explicit request does not silently drop the later request; stale retries and reconnect cannot corrupt the current installation's sync status.
- [ ] POST/GET deny unauthorised users, missing REST nonces, foreign or malformed business input, disconnected/changed installations and invalid status payloads; no WordPress secrets/tenant IDs appear in browser responses or logs.
- [ ] Missing scheduler, API offline, HTTP 408/429/5xx retries, terminal HTTP 4xx and exhausted retries produce truthful actionable status with preserved prior acceptance and bounded logging.
- [ ] Accessible pending/success/failure feedback works on desktop and narrow/mobile WooCommerce admin widths; no unbounded polling, double-submit, screen-unmount leak or checkout hot-path impact.
- [ ] `WOOCOMMERCE-001` initial auto-sync and bounded retries still work and no changes outside `moda-interact-woocommerce/` or this task's own coordination file were implemented.

## Validation

- [ ] Relevant PHP `ShopBrandPublicationTest.php` regression and new `ShopBrandSyncControllerTest.php` unit/integration tests, including REST permissions/nonce, state persistence, failed logging, scheduling and concurrency/idempotency.
- [ ] WordPress REST integration under logged-in `manage_woocommerce` merchant and denied low-privilege/unauthenticated sessions; stub hosted API confirms real source changes and no leaked credentials.
- [ ] JS unit tests for client schema/error mapping, controller lifecycle, disabled/pending/success UI, localisation and status/date semantics; update existing recovery-settings/page-composition fixtures.
- [ ] `composer lint`, focused `composer test` or `vendor/bin/phpunit` for affected PHP, `npm run test:js:unit`, `npm run i18n:verify:20`, `npm run build`, plus `git diff --check` (run only scripts actually provided by checked-out `package.json` and task requirements; record missing dependencies honestly).
- [ ] Manually verify connected and disconnected Woo merchant screens at regular/narrow widths and confirm no outbound brand publication on editing WP branding without pressing the button.

## Stop Condition

After required work, acceptance evidence and validation, update only this task's own Work Items, Validation, Completion Report and execution metadata. Transition to `review`, return to `moda_architect` for acceptance, and **STOP**. Do not start ARCH-049-SYSTEM-TEST-001, edit another domain task/index, merge or push main.

## Implementation Notes

The definition is materialised on the canonical parent task branch `task/ARCH-049-WOOCOMMERCE-002` at the launcher-resolved parent worktree. Create/reuse the implementation worktree only when a developer claims this ready task. Record both launcher-resolved paths, start-of-attempt synchronisation, recursively materialised submodule evidence where relevant, repository branch/commit and validation in the Completion Report. Do not infer a worktree path from the previous task directory.

The WooCommerce plugin runs in merchant-controlled PHP and cannot import `@modainteract/moda-interact-shared/logging`; use existing WooCommerce `wc_get_logger()` bounded semantic events with a bounded WordPress/PHP fallback. Log exceptions and failed status persistence safely; never log raw API exceptions, secret headers, provider tokens, full source URLs or customer data. Use existing capability, nonce and tenancy enforcement rather than a new security framework. This is **not** a recurring-sync task: browser status refresh after a button click is allowed, but permanent scheduled refresh is not.

## Completion Report

### Status

Ready — the canonical parent task definition is materialised on
`task/ARCH-049-WOOCOMMERCE-002` at
`/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-049-WOOCOMMERCE-002`.
The accepted dependency `ARCH-049-WOOCOMMERCE-001` is complete at Attempt 2.
This task remains unclaimed at Attempt 0; its implementation worktree has not
been created.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

None beyond the explicit architecture and task contract.

### Unresolved Issues

No unresolved explicit dependencies. Hosted API integration remains a terminal
system-test gate; it is not a prerequisite for this task's local implementation.

### Architectural Concerns

None reported; escalate any API contract, cross-repository schema or provider capability change to `moda_architect` rather than implementing it locally.

## Architect Review

### Review Status

Pending.

### Review Notes

None.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Not reviewed.

### Follow-up

None.
