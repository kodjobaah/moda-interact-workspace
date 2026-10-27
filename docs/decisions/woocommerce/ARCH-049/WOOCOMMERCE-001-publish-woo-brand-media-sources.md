---
id: ARCH-049-WOOCOMMERCE-001
architecture_id: ARCH-049
title: Publish WooCommerce Site Identity branding through the Moda API
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: review
priority: 30
executor: null
claimed_at: null
attempt: 1
depends_on: []
enables: ["ARCH-049-WOOCOMMERCE-002", "ARCH-049-SYSTEM-TEST-001"]
created: 2026-10-25
updated: 2026-10-27
---

# Publish WooCommerce Site Identity branding through the Moda API

## Architecture

`ARCH-049` — `docs/architecture/ARCH-049-shopbrand-public-media-configuration.md`; coordinator `moda_architect`. **Materialised developer-executed task.** The dedicated parent and implementation worktrees, preparation evidence, and implementation commit are recorded in the Completion Report.

## Objective

Read site branding locally within the installed WordPress/WooCommerce plugin and publish canonical metadata to the authenticated Moda API; do not expose a new WordPress REST endpoint.

## Context

WooCommerce does not have Shopify's single Brand Admin object. WordPress Site Logo, Site Icon, site title and attachment metadata are available through native PHP functions; the plugin already owns secure server-side Moda API communication and Action Scheduler workflows. This task does not modify the hosted API, and can be independently tested with a contract fixture while that API is implemented.

## Scope

- Add a modular PHP `includes/ShopBrand/` source reader, DTO builder and publisher, plus client method in `ModaApiClient`.
- Read the site title and native WordPress logo/site-icon attachments without scraping themes or arbitrary plugin options.
- Queue the initial `woo.shop-brand.v1` publication after the first authenticated connection (or first eligible runtime for an already-connected installation); do not poll or auto-publish on later WordPress brand changes.
- Add focused WordPress/PHP unit tests for classic/block themes, missing assets, changed/deleted assets and offline API.

## Out of Scope

- New externally reachable WordPress route, requiring Background to call merchant WordPress sites, uploading R2 images, saving directly to Moda PostgreSQL or implementing merchant editor UI. A future merchant-facing **Sync branding** button and its capability/nonce-protected controller are separate work.

## Requirements

### R1. Source selection

Read brandName via `get_bloginfo('name')`. Prefer site-logo attachment ID from WordPress Site Identity (`get_theme_mod('custom_logo')` for classic themes; supported `site_logo` option when used by block themes). Read URL via `wp_get_attachment_image_url($id,'full')`, dimensions from `wp_get_attachment_metadata($id)`, alt text from `get_post_meta($id,'_wp_attachment_image_alt',true)`. For square logo use `get_site_icon_url()` / `get_option('site_icon')` with attachment metadata when available. Do not claim WordPress has a reliable native cover image; send `coverImage: null` initially. Treat absent logo/icon as explicit null; use no arbitrary theme-specific image extraction.

### R2. Publication contract

Use `ModaApiClient` existing installation credentials and exact `woo.shop-brand.v1` payload in API-001. `eventId` is stable across retries for the same canonical snapshot (e.g., deterministic installation ID + source digest); `observedAt` is the timestamp at snapshot capture and is preserved on retry. Do not include shopId credentials or hidden server settings in the body. Source URLs must be HTTPS to be eligible for media processing; if WordPress source is HTTP, submit a null/not-ready source rather than silently upgrading schemes. Leave storefront behaviour unchanged.

### R3. Triggers and retries

Installation/activation alone may precede obtaining Moda installation credentials. After the **first successful authenticated connection**, enqueue one initial ShopBrand capture. A plugin upgrade on an already-connected site performs one initial capture if its installation-scoped bootstrap marker is absent. Mark initial capture **enqueued**, not provider-delivered; do not use this marker to claim success. No automatic site-title/logo/icon/theme/attachment change hooks and no daily reconciliation are permitted. On upgrade, cancel any legacy recurring brand-reconciliation actions created by an older implementation. Keep one explicit internal, authenticated-installation-scoped `requestSync()` entry point available for a future capability/nonce-protected merchant UI; no UI or WordPress REST route is implemented here. Use Action Scheduler to coalesce captures, retry transient 408/429/5xx/network failures (20s, 60s, 5m, 15m; five attempts total) and stop on definitive 4xx. If initial enqueue fails because the scheduler is unavailable, retain eligibility to retry enqueue at next runtime startup; exhausted publication retries are logged and do not activate a periodic reconciliation. Publishing must not block storefront checkout or reveal credentials in logs. An explicitly requested future capture of a removed logo/icon publishes null for that role.

### R4. Security

Only locally read WordPress settings/attachment metadata. Never install a public merchant-server endpoint to fetch images for Background; Background later fetches only the provider's HTTPS source URL subject to its SSRF policy.

## Work Items

- [x] Create PHP source reader and normalised payload builder.
- [x] Add authenticated Moda API client publication and bounded retry hooks.
- [x] Test source changes/removals and missing logo/icon through an explicit new snapshot.
- [x] Ensure installation/connection bootstrap is idempotent; remove brand-change hooks and daily reconciliation, clean up legacy recurring actions, and expose reusable internal `requestSync()`.
- [x] Document rollout/reconnect and version support, including that post-install branding changes are not automatically synchronised.

## Interfaces / Contracts

Produces `woo.shop-brand.v1` to `POST /v1/woocommerce/shop-brand`; consumes the response `status: updated|unchanged`. No direct database or R2 access. WordPress-origin URLs are data, never Moda-authorised fetch destinations.

## Dependencies

None. The `woo.shop-brand.v1` API route, request and response contract are already fully specified in the separately owned `ARCH-049-API-001` definition. Implement and test the plugin independently against an authenticated local HTTP fixture; do not require an API implementation commit to author a producer client. Production activation and the end-to-end System Test still require accepted API-001.

## Enables

- ARCH-049-WOOCOMMERCE-002
- ARCH-049-SYSTEM-TEST-001

## Acceptance Criteria

- [x] Against the frozen authenticated `woo.shop-brand.v1` HTTP fixture, a fresh Woo connection queues one initial branding publication, and an already-connected installation is bootstrapped once; subsequent WordPress changes **do not** publish without an explicit future sync request. The reusable `requestSync()` captures changed/removed assets correctly. Real hosted API delivery is certified only after API001 acceptance in SYSTEM-TEST-001.
- [x] No new public WP route and no checkout latency regression.
- [x] Stable retries do not duplicate observations or leak installation credentials.
- [x] Removed logo/icon becomes a null source rather than retaining a false current READY.

## Validation

- [x] PHP unit tests with stubbed WP Site Identity APIs and attachment data.
- [x] Client API/auth body/response tests, bounded Action Scheduler retries, absence of automatic/daily triggers, cleanup of existing recurring jobs and explicit sync reuse.
- [x] Woo plugin build/lint/JS or PHP tests required by affected code and `git diff --check`.

## Stop Condition

After the defined Work Items, Acceptance Criteria and Validation are complete, record the Completion Report and change task status to `review`; hand off to `moda_architect` and STOP. Do not continue into a dependent task or change an `_index.md`.

## Implementation Notes

All task work must use the canonical launcher-provided **dedicated parent and implementation worktrees**, synced task/<TASK_ID> branches and start-of-attempt evidence. Inspect the actual pinned package scripts, source and existing conventions before editing. Do not merge branches, push main, edit another repository, start an enabled task or change any `docs/decisions/**/_index.md`. Use structured logging via `@modainteract/moda-interact-shared/logging`; secrets and full untrusted URLs must not enter diagnostics. Document changed files, relevant test commands, results, security/tenant checks, commits and worktree evidence in the Completion Report.

No additional assumptions are authorised.

## Completion Report

### Status

**Ready for Review — Developer Attempt 1.** The implementation was committed as `5b12eba` (`feat(arch-049-woocommerce)`) and the terminal transcript records a successful push of implementation branch `task/ARCH-049-WOOCOMMERCE-001` to `origin`. This report is prepared for review; it is not architect acceptance or the developer's explicit completion decision. `completion_mode: developer` and `attempt: 1` are preserved.

### Developer Takeover and Worktree Evidence

On 2026-10-27, `/moda_developer_create ARCH-049-WOOCOMMERCE-001` transferred execution and completion authority to the developer while preserving `assigned_agent: moda_woocommerce`. The launcher-established dedicated worktrees are:

- Parent: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-049-WOOCOMMERCE-001`, prepared on `task/ARCH-049-WOOCOMMERCE-001` from synced `origin/main` at `286a2bf371efc4bb122842943d7f1bb1ee8543c5`.
- Implementation: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-049-WOOCOMMERCE-001`, prepared on `task/ARCH-049-WOOCOMMERCE-001` from synced `origin/main` at `29c1d7afd94a074d6b5de2410b4d19a2adc73a1c`.
- No declared implementation submodules; start-of-attempt task metadata recorded clean branch state, no conflicting worktree, and satisfied empty dependency set. The supplied execution log shows tests, commit and push from the dedicated implementation worktree. The log also shows an unrelated untracked local `typescript` terminal capture, not included in the commit.

### Files Changed

The implementation commit contains 15 WooCommerce-repository files:

- `composer.json`
- `docs/arch049-woo-shop-brand.md`
- `includes/Api/ModaApiClient.php`
- `includes/Connection/ConnectionCoordinator.php`
- `includes/Runtime.php`
- `includes/ShopBrand/Publisher.php` (new)
- `includes/ShopBrand/SnapshotBuilder.php` (new)
- `includes/ShopBrand/SourceReader.php` (new)
- `package.json`
- `tests/ShopBrandPublicationTest.php` (new)
- `tests/integration/run-wordpress.mjs`
- `tests/integration/scenarios/connection-wordpress.mjs`
- `tests/integration/scenarios/shop-brand-wordpress.mjs` (new)
- `tests/integration/wordpress-api-fixture.mjs`
- `tests/integration/wordpress-api-fixture.test.mjs`

### Work Completed

- Added native WordPress Site Identity reader for brand name, selected classic/block-theme Site Logo, Site Icon, attachment URL/dimensions/alt metadata, and explicit `null` for unavailable, deleted or non-HTTPS source media; `coverImage` remains `null`.
- Implemented exact `woo.shop-brand.v1` canonical source snapshots with installation-scoped deterministic `eventId`, capture-time `observedAt`, strict source/payload validation, and no credentials or caller-authoritative shop ID in the body.
- Added authenticated `ModaApiClient::publishShopBrand()` to `POST /v1/woocommerce/shop-brand`, using existing installation credentials and verifying the `updated|unchanged` response.
- Integrated one-time initial publication on successful connection and initial bootstrap for previously connected installations. Capture is asynchronous, Action Scheduler readiness is checked before store operations, and marker state means *enqueued*, not delivered.
- Exposed internal `ShopBrand\Publisher::requestSync()` for a future capability/nonce-protected merchant action. No WordPress-brand-change hooks, daily reconciliation, public WP REST endpoint, or synchronous checkout publication; old recurring reconciliation jobs are unscheduled after Action Scheduler initialisation.
- Implemented coalescing, transient-failure retries at 20s/60s/5m/15m (five total attempts), no retry on definitive 4xx, immutable retry payload, stale-installation/site-identity protection, and bounded redacted error codes.
- Added PHPUnit coverage, local HTTPS API fixture contract tests and Docker-backed real WordPress/Action Scheduler integration coverage for initial/upgrade/bootstrap, no automatic sync, explicit sync, removal, retry and failure cases.

### Validation Results

Evidence from the developer-supplied terminal recording dated **2026-10-27**, supplemented by independent snapshot checks:

- **PASS** — `npm run test:integration:shop-brand`. Docker `wp-env` started, exercised real WordPress/WooCommerce + Action Scheduler + authenticated HTTPS fixture, and emitted `ARCH-049 Woo ShopBrand native WordPress + Action Scheduler + authenticated HTTPS integration PASS`. It stopped WordPress normally. The previously reported Action Scheduler premature-store warning and connection `200 !== 404` assertion did not recur in this run.
- **PASS** — `composer test -- --filter ShopBrandPublicationTest`: PHPUnit 11.5.56, PHP 8.5.11, **16 tests / 133 assertions**, no failures.
- **PASS** — `composer lint`: reported no PHP syntax errors across the repository's declared lint targets, including the new ShopBrand files and PHP tests.
- **PASS** — Reviewer independently ran `node --test tests/integration/wordpress-api-fixture.test.mjs` using files extracted from the uploaded worktree: **3/3** fixture tests passed, including the `woo.shop-brand.v1` contract case.
- **PASS** — Reviewer independently checked PHP syntax of modified ShopBrand, Runtime and ConnectionCoordinator files, and JavaScript syntax of the changed integration files.
- **PASS (reconstructed source diff)** — Reviewer ran `git diff --check` on all 15 changed implementation files against the earlier uploaded workspace baseline, including the six newly added files; no whitespace errors. The terminal transcript does not show a separate `git diff --check` invocation in the developer's original Git worktree; the developer may repeat `git show --check 5b12eba` before submitting review.
- **PASS (publication evidence)** — Developer terminal transcript records implementation commit `5b12eba` and successful push to `origin task/ARCH-049-WOOCOMMERCE-001`. Remote branch identity is taken from that log rather than independently queried.
- **Not part of this task's completion gate** — Hosted API-001/PostgreSQL end-to-end acceptance and final ARCH-049 system tests; these remain separately owned downstream work.

### Deviations

- **Logging implementation boundary:** The WordPress extension runs in PHP and cannot load the Node-only `@modainteract/moda-interact-shared/logging` package. It uses the existing WooCommerce logger (`wc_get_logger`) with bounded semantic reason codes and optional numeric HTTP status/attempt, falling back to PHP `error_log`. No raw URLs, exception messages or credentials are logged. The reviewer should explicitly confirm this platform-specific logging accommodation.
- No other deviations from the *revised* explicit-only synchronisation task contract were identified in the inspected implementation and test evidence.

### Assumptions

- WordPress 7.0+/WooCommerce 11.0+ native Site Identity APIs and HTTPS sources as documented in `docs/arch049-woo-shop-brand.md`.
- `ARCH-049-API-001` is the separate owner of hosted request validation and PostgreSQL persistence; this task validates its frozen HTTP contract using a local fixture.

### Unresolved Issues

- `ARCH-049-API-001` remains an independent prerequisite for real hosted publication and the later `ARCH-049-SYSTEM-TEST-001`. The WooCommerce implementation may be reviewed before those tasks are Complete.
- No known WooCommerce-local blocker remains after the reported WordPress/Action Scheduler and PHPUnit passes. Architect review may identify further changes.

### Architectural Concerns

- Confirm the PHP-native logging choice against the architect's shared-logging policy; an npm/Node logging import is not executable in merchant-hosted PHP.
- The implementation contains no new public WordPress endpoint, direct Moda database/R2 connection, or automatic brand-change polling. Idempotency and authoritative tenant selection on the hosted API are reserved for API-001 and system validation.

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
