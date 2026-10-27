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
status: ready
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

Installation/activation alone may precede obtaining Moda installation credentials. After the **first successful authenticated connection**, enqueue one initial ShopBrand capture. A plugin upgrade on an already-connected site performs one initial capture if its installation-scoped bootstrap marker is absent. Mark initial capture **enqueued**, not provider-delivered; do not use this marker to claim success. No automatic site-title/logo/icon/theme/attachment change hooks and no daily reconciliation are permitted. This ShopBrand feature has **never been deployed**: do not introduce legacy recurring-action cleanup or migration markers, and never query the scheduler store for obsolete jobs at bootstrap. Keep one explicit internal, authenticated-installation-scoped `requestSync()` entry point available for a future capability/nonce-protected merchant UI; no UI or WordPress REST route is implemented here. Use Action Scheduler to coalesce captures, retry transient 408/429/5xx/network failures (20s, 60s, 5m, 15m; five attempts total) and stop on definitive 4xx. If initial enqueue fails because the scheduler is unavailable, retain eligibility to retry enqueue at next runtime startup; exhausted publication retries are logged and do not activate a periodic reconciliation. Publishing must not block storefront checkout or reveal credentials in logs. An explicitly requested future capture of a removed logo/icon publishes null for that role.

### R4. Security

Only locally read WordPress settings/attachment metadata. Never install a public merchant-server endpoint to fetch images for Background; Background later fetches only the provider's HTTPS source URL subject to its SSRF policy.

## Work Items

- [x] Create PHP source reader and normalised payload builder.
- [x] Add authenticated Moda API client publication and bounded retry hooks.
- [x] Test source changes/removals and missing logo/icon through an explicit new snapshot.
- [x] Ensure installation/connection bootstrap is idempotent; register no brand-change hooks or daily reconciliation, avoid legacy cleanup/store queries on already-bootstrapped requests, and expose reusable internal `requestSync()`.
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
- [x] No new public WP route.
- [x] No recurring Action Scheduler/store lookup on already-bootstrapped requests; checkout latency remains unaffected.
- [x] Stable retries do not duplicate observations or leak installation credentials.
- [x] Removed logo/icon becomes a null source rather than retaining a false current READY.

## Validation

- [x] PHP unit tests with stubbed WP Site Identity APIs and attachment data.
- [x] Client API/auth body/response tests, bounded Action Scheduler retries, absence of automatic/daily triggers, no scheduler-store lookups on already-bootstrapped requests, and explicit sync reuse.
- [x] Woo plugin build/lint/JS or PHP tests required by affected code and `git diff --check`.

## Stop Condition

After the defined Work Items, Acceptance Criteria and Validation are complete, record the Completion Report and change task status to `review`; hand off to `moda_architect` and STOP. Do not continue into a dependent task or change an `_index.md`.

## Implementation Notes

All task work must use the canonical launcher-provided **dedicated parent and implementation worktrees**, synced task/<TASK_ID> branches and start-of-attempt evidence. Inspect the actual pinned package scripts, source and existing conventions before editing. Do not merge branches, push main, edit another repository, start an enabled task or change any `docs/decisions/**/_index.md`. Use `@modainteract/moda-interact-shared/logging` in Node runtimes. **Approved PHP exception for this WooCommerce ShopBrand publisher:** use WooCommerce's existing `wc_get_logger()` with bounded reason codes and optional numeric HTTP status/attempt; use a similarly redacted `error_log` fallback if needed. Never log credentials, full untrusted URLs, exception messages or payloads; diagnostic failures must not change publication behaviour. Do not create a separate generic PHP logger. Document changed files, relevant test commands, results, security/tenant checks, commits and worktree evidence in the Completion Report.

No additional assumptions are authorised.

## Completion Report

### Status

**Developer Self-Review - Changes Requested — corrected submission, Attempt 1.** The corrections are present in implementation commit `01b3be5` and its latest focused PHPUnit suite passed 17 tests / 139 assertions during review. However, the correction was submitted without a new launcher claim after the Changes Requested transition: parent history moves from `60dac3ec` (Changes Requested) through correction/report commits to `b21fd880` (review submission), with no Attempt 2 claim or start-of-attempt synchronization record. Per the developer workflow, the next `/moda_developer_create ARCH-049-WOOCOMMERCE-001` must claim Attempt 2 and record synchronization evidence before the corrected submission can be accepted. Current state is `ready`, with `executor: null`, `claimed_at: null`, and `attempt: 1` unchanged. The code fixes are not rejected; this is a lifecycle-evidence correction, not completion or architect acceptance.

### Developer Takeover and Worktree Evidence

On 2026-10-27, `/moda_developer_create ARCH-049-WOOCOMMERCE-001` transferred execution and completion authority to the developer while preserving `assigned_agent: moda_woocommerce`. The launcher-established dedicated worktrees are:

- Parent: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-049-WOOCOMMERCE-001`, prepared on `task/ARCH-049-WOOCOMMERCE-001` from synced `origin/main` at `286a2bf371efc4bb122842943d7f1bb1ee8543c5`.
- Implementation: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-049-WOOCOMMERCE-001`, prepared on `task/ARCH-049-WOOCOMMERCE-001` from synced `origin/main` at `29c1d7afd94a074d6b5de2410b4d19a2adc73a1c`.
- No declared implementation submodules; start-of-attempt task metadata recorded clean branch state, no conflicting worktree, and satisfied empty dependency set. The supplied execution log shows tests, commit and push from the dedicated implementation worktree. The log also shows an unrelated untracked local `typescript` terminal capture, not included in the commit.

### Files Changed

The initial implementation commit `5b12eba` contains 15 WooCommerce-repository files:

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

Follow-up published commit **`01b3be5`** changes seven files to address the review findings and repeatable integration execution:

- `docs/arch049-woo-shop-brand.md`
- `includes/ShopBrand/Publisher.php`
- `tests/ShopBrandPublicationTest.php`
- `tests/integration/run-wordpress.mjs`
- `tests/integration/scenarios/connection-wordpress.mjs`
- `tests/integration/scenarios/shop-brand-wordpress.mjs`
- `tests/integration/scenarios/shop-brand-runner.test.mjs` (new)

### Work Completed

- Added native WordPress Site Identity reader for brand name, selected classic/block-theme Site Logo, Site Icon, attachment URL/dimensions/alt metadata, and explicit `null` for unavailable, deleted or non-HTTPS source media; `coverImage` remains `null`.
- Implemented exact `woo.shop-brand.v1` canonical source snapshots with installation-scoped deterministic `eventId`, capture-time `observedAt`, strict source/payload validation, and no credentials or caller-authoritative shop ID in the body.
- Added authenticated `ModaApiClient::publishShopBrand()` to `POST /v1/woocommerce/shop-brand`, using existing installation credentials and verifying the `updated|unchanged` response.
- Integrated one-time initial publication on successful connection and initial bootstrap for previously connected installations. Capture is asynchronous, Action Scheduler readiness is checked before store operations, and marker state means *enqueued*, not delivered.
- Exposed internal `ShopBrand\Publisher::requestSync()` for a future capability/nonce-protected merchant action. No WordPress-brand-change hooks, daily reconciliation, public WP REST endpoint, or synchronous checkout publication. Because this ShopBrand feature has never been deployed, obsolete recurring-job cleanup code and tests have been **removed**, not replaced with migration markers.
- Implemented coalescing, transient-failure retries at 20s/60s/5m/15m (five total attempts), no retry on definitive 4xx, immutable retry payload, stale-installation/site-identity protection, and bounded redacted error codes.
- Added PHPUnit coverage, local HTTPS API fixture contract tests and Docker-backed real WordPress/Action Scheduler integration coverage for initial/upgrade/bootstrap, no automatic sync, explicit sync, removal, retry and failure cases. New focused tests verify zero scheduler-store lookups after initial bootstrap, no recurring branding actions, and retry continuity if the WooCommerce logger throws. Reordered connection integration assertions to validate the first capture *before* credential rotation; reset only the dedicated fixture installation when repeating a test.

### Validation Results

Evidence from the supplied 2026-10-27 terminal recordings and independent checks on worktree snapshot `(6)`:

- **PASS (latest source, live integration)** — `WP_ENV_PORT=8899 npm run test:integration:shop-brand` emitted `ARCH-049 Woo ShopBrand native WordPress + Action Scheduler + authenticated HTTPS integration PASS`. `wp-env` started on port 8899, ran real WordPress/WooCommerce hooks, Action Scheduler and the local authenticated HTTPS fixture, then stopped cleanly. The previous initial-capture assertion and port conflict did not recur. **One passing invocation is visible in the latest recording; a second consecutive passing run is not evidenced.**
- **PASS (earlier developer PHPUnit execution)** — `composer test -- --filter ShopBrandPublicationTest` reported **17 tests / 139 assertions** in the 14:30 terminal recording. This predates the final published `01b3be5` changes, which add/replace logging and bootstrap-regression test cases; **a fresh PHPUnit run against the published head is not present** in the latest log and should be supplied for review.
- **PASS (independently rerun during review on published HEAD `01b3be5`)** — `composer test -- --filter ShopBrandPublicationTest`: PHPUnit 11.5.56, PHP 8.5.11, **17 tests / 139 assertions**, no failures. This closes the final-head PHPUnit evidence gap.
- **PASS (latest snapshot, independent PHP syntax validation)** — all **88/88** PHP targets declared in `composer.json` passed `php -l`, including the updated publisher and PHPUnit test file. The earlier developer `composer lint` output also passed its declared targets.
- **PASS (latest snapshot, independent focused Node tests)** — `node --test tests/integration/scenarios/shop-brand-runner.test.mjs tests/integration/wordpress-api-fixture.test.mjs`: **6/6 passed**, including first-connection ordering, retry-safe fixture behaviour and the `woo.shop-brand.v1` authenticated fixture contract.
- **PASS (latest snapshot)** — JavaScript syntax checks passed for the four modified integration files. The source inspection confirms no legacy reconciliation method/constant, no recurring registration and no brand-change hook. Unit test code specifically counts store lookups across repeated bootstrapped requests, verifies `requestSync()` coalescing and guards the logging-failure retry path.
- **PASS (Git publication evidence)** — the terminal transcript shows commit `01b3be5` (7 files) and a successful push advancing `task/ARCH-049-WOOCOMMERCE-001` from `5b12eba` to `01b3be5`. Remote-state evidence comes from the developer's transcript; this ZIP is not an independent remote checkout.
- **PASS (Git publication evidence, independently verified)** — implementation HEAD `01b3be50ba8409f97d5dc9074f30a7b66d0020d8` matches `origin/task/ARCH-049-WOOCOMMERCE-001`; implementation worktree is clean. Parent HEAD `b21fd880d822e1783ce0be5d902f0bd3783712af` matches its origin task ref.
- **Out of scope for WooCommerce-local acceptance** — real hosted `ARCH-049-API-001` processing, PostgreSQL/R2 and `ARCH-049-SYSTEM-TEST-001` remain later separately owned integration gates.

**Review follow-up:** before final acceptance, request a fresh `composer test -- --filter ShopBrandPublicationTest` log on `01b3be5` and confirm whether the launcher recorded a new correction-cycle claim and start-of-attempt synchronisation. No evidence is invented for either item.

### Deviations

- **Architect-approved PHP runtime accommodation:** WordPress cannot import the Node-only `@modainteract/moda-interact-shared/logging` entrypoint. The 2026-10-27 task/architecture decision approves `wc_get_logger()` with bounded semantic reason codes, optional numeric status/attempt, and redacted `error_log` fallback. The updated tests exercise diagnostic failure isolation. This is not an outstanding logging design deviation; the reviewer should still verify the implementation and tests.
- No other deviations from the *revised* explicit-only synchronisation task contract were identified in the inspected implementation and test evidence.

### Assumptions

- WordPress 7.0+/WooCommerce 11.0+ native Site Identity APIs and HTTPS sources as documented in `docs/arch049-woo-shop-brand.md`.
- `ARCH-049-API-001` is the separate owner of hosted request validation and PostgreSQL persistence; this task validates its frozen HTTP contract using a local fixture.

### Unresolved Issues

- `ARCH-049-API-001` remains an independent prerequisite for real hosted publication and the later `ARCH-049-SYSTEM-TEST-001`. The WooCommerce implementation may be reviewed before those tasks are Complete.
- The latest WordPress/Action Scheduler integration passes, and the fresh PHPUnit run on `01b3be5` also passes. The correction-cycle claim/synchronization evidence remains unresolved. The next developer preparation must claim Attempt 2 and record the synchronized canonical worktrees before resubmitting.
- The canonical parent task worktree currently contains an untracked `typescript` item. It was not changed or staged during review and must be preserved unless its owner explicitly directs otherwise. The implementation worktree is clean.

### Architectural Concerns

- The PHP-native ShopBrand logging boundary is explicitly approved for this PHP plugin; the new logger-failure test and bounded metadata controls are present. Final PHP test execution on the updated branch should be confirmed at review.
- The implementation contains no new public WordPress endpoint, direct Moda database/R2 connection, or automatic brand-change polling. Idempotency and authoritative tenant selection on the hosted API are reserved for API-001 and system validation.

## Developer Self-Review - Changes Requested

### Required Corrections

- **Superseded by architect on 2026-10-27:** the requirement to perform a one-time legacy cleanup and retain legacy-action removal tests. This feature has never been deployed; instead **remove** the obsolete cleanup method, constants, test scaffolding and synthetic recurring-action fixture. Prove that already-bootstrapped requests do not look up Action Scheduler jobs and that no recurring branding jobs are scheduled. Keep the first-connection/upgrade bootstrap and bounded retries.
- **Architect decision recorded 2026-10-27:** WooCommerce's native PHP logger is approved for this ShopBrand publisher, because the shared Node logging export cannot run inside WordPress PHP. Preserve redacted semantic codes and exception isolation; review the updated test evidence before marking accepted.

### Review Evidence

- `composer test -- --filter ShopBrandPublicationTest`: PASS, 16 tests / 133 assertions.
- `git show --check 5b12ebacb1dd34b4aede037d0ee8ecea2d02e828`: PASS.
- Implementation worktree was clean at published commit `5b12eba`; parent task branch was clean and matched its published task ref before this review update.

### Review Decision

Attempt 1 requires the corrections above. No new attempt is created by this review. `status` is `ready`, `executor` and `claimed_at` are null, and `attempt` remains 1. Re-enter with `/moda_developer_create ARCH-049-WOOCOMMERCE-001` after the corrections are ready for a new cycle.

## Developer Self-Review - Corrected Submission

### Submission

On 2026-10-27 the developer published corrected WooCommerce commit `01b3be5` after receiving Attempt 1 Changes Requested. The latest upload shows a dedicated implementation worktree and successful live `wp-env` integration; the parent task record is being updated to `review` solely for architect examination. Initial connection and explicit-only sync remain intact. The unused undeployed legacy cleanup was removed; the reviewed logging exception is now a documented approved PHP boundary. This submission does **not** complete the task or promote `ARCH-049-WOOCOMMERCE-002`.

### Evidence and reconciliation note

The current task frontmatter remains at `attempt: 1` because the supplied parent snapshot did not record a subsequent `/moda_developer_create` claim. The existing Attempt 1 worktree evidence remains on record; latest commit/push and test execution occurred in the same dedicated implementation worktree. The reviewer should explicitly reconcile the missing correction-cycle preparation record and request updated PHPUnit evidence before acceptance rather than manufacture a claimed attempt or infer that all fresh tests were run.

## Architect Review

## Developer Self-Review - Changes Requested — Corrected Submission

### Review Findings

- The corrected implementation is published at `01b3be50ba8409f97d5dc9074f30a7b66d0020d8`; the latest `composer test -- --filter ShopBrandPublicationTest` passed 17 tests / 139 assertions. The commit passes `git show --check`.
- The parent task history shows `60dac3ec3f68a4c54566e1cd7d6f9f4d4c36e351` as the Changes Requested decision, followed by implementation/report corrections and review submission `b21fd880d822e1783ce0be5d902f0bd3783712af`; there is no subsequent durable developer claim or start-of-attempt synchronization record.
- The parent task worktree has an untracked `typescript` item. It was left untouched. The implementation task worktree is clean.

### Required Correction

Return the task to `ready` and invoke `/moda_developer_create
ARCH-049-WOOCOMMERCE-001` to claim Attempt 2. Reuse the same canonical task
branches/worktrees, record the actual synchronization evidence, and preserve
the already-published implementation commits unless a concrete code correction
is needed. Re-run or explicitly validate the focused final-head PHPUnit suite in
the claimed attempt, then resubmit through `/moda_developer_update`.

### Decision

Review is **Changes Requested** for lifecycle evidence only. No new attempt is
created here. `status: ready`, `executor: null`, `claimed_at: null`,
`attempt: 1` unchanged. No implementation or unrelated untracked file was
modified by this review.

## Architect Review

### Review Status

Pending.

### Review Notes

**Scope clarification (2026-10-27):** The ARCH-049 WooCommerce ShopBrand feature has not been deployed, so no merchant site can hold a production legacy ShopBrand reconciliation schedule. Legacy cleanup/migration work and its tests are withdrawn. Remove the unused cleanup entirely; retain a test proving no Action Scheduler store lookups during repeated already-bootstrapped requests, and verify no recurring branding jobs are created. The prior developer self-review requirement to retain legacy cleanup coverage is superseded.

**PHP logging decision (2026-10-27):** Approve `wc_get_logger()` as the existing native PHP sink for this ShopBrand feature, with a redacted `error_log` fallback and no extra generic adapter. The Node-only Shared logger remains mandatory for Node services. The developer still needs to demonstrate bounded diagnostics, absence of sensitive values, and failure isolation.

This is a task-scope decision, **not** acceptance of the implementation. At the time the clarification was made, the task remained `ready`; the subsequent corrected submission is now presented with `status: review` for consideration. Review Status remains Pending until the authorised reviewer examines the updated evidence.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Not reviewed.

### Follow-up

None.
