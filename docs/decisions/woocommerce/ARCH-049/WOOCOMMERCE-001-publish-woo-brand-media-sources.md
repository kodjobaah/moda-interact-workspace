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
status: complete
priority: 30
executor: null
claimed_at: null
attempt: 2
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

Evidence from the 2026-10-27 terminal recordings and Attempt 2 focused runs:

- **PASS (live integration, before Attempt 2)** — `WP_ENV_PORT=8899 npm run test:integration:shop-brand` passed against WordPress, WooCommerce, Action Scheduler, and the local authenticated HTTPS fixture. It was not rerun in Attempt 2 because no source changed.
- **PASS (Attempt 2, published HEAD `01b3be5`)** — `composer test -- --filter ShopBrandPublicationTest`: 17 tests / 139 assertions.
- **PASS (Attempt 2)** — `node --test tests/integration/scenarios/shop-brand-runner.test.mjs tests/integration/wordpress-api-fixture.test.mjs`: 6/6 passed.
- **PASS** — PHP syntax validation covered all 88 targets declared in `composer.json`; JavaScript syntax checks passed for the four modified integration files.
- **PASS (publication)** — implementation HEAD `01b3be50ba8409f97d5dc9074f30a7b66d0020d8` matches `origin/task/ARCH-049-WOOCOMMERCE-001`; its worktree is clean. The Attempt 2 parent claim `1155a8300d9b31a9d38305fd0f61febc88ddae2b` was published.
- **PASS** — `git show --check HEAD` and parent task `git diff --check` passed.
- **Not rerun in Attempt 2** — Docker-backed WordPress/Action Scheduler integration; the existing passing evidence predates Attempt 2, which introduced no source changes.
- **Out of scope for WooCommerce-local acceptance** — hosted `ARCH-049-API-001` processing, PostgreSQL/R2, and `ARCH-049-SYSTEM-TEST-001` remain separately owned integration gates.

### Deviations

- **Architect-approved PHP runtime accommodation:** WordPress cannot import the Node-only `@modainteract/moda-interact-shared/logging` entrypoint. The 2026-10-27 task/architecture decision approves `wc_get_logger()` with bounded semantic reason codes, optional numeric status/attempt, and redacted `error_log` fallback. The updated tests exercise diagnostic failure isolation. This is not an outstanding logging design deviation; the reviewer should still verify the implementation and tests.
- No other deviations from the *revised* explicit-only synchronisation task contract were identified in the inspected implementation and test evidence.

### Assumptions

- WordPress 7.0+/WooCommerce 11.0+ native Site Identity APIs and HTTPS sources as documented in `docs/arch049-woo-shop-brand.md`.
- `ARCH-049-API-001` is the separate owner of hosted request validation and PostgreSQL persistence; this task validates its frozen HTTP contract using a local fixture.

### Unresolved Issues

- `ARCH-049-API-001` remains an independent prerequisite for real hosted publication and the later `ARCH-049-SYSTEM-TEST-001`. The WooCommerce implementation may be reviewed before those tasks are Complete.
- The canonical parent task worktree currently contains an untracked `typescript` item. It was not changed or staged during review and must be preserved unless its owner explicitly directs otherwise. The implementation worktree is clean.

### Architectural Concerns

- The PHP-native ShopBrand logging boundary is explicitly approved for this PHP plugin; the new logger-failure test and bounded metadata controls are present and the focused PHPUnit suite passed during Attempt 2.
- The implementation contains no new public WordPress endpoint, direct Moda database/R2 connection, or automatic brand-change polling. Idempotency and authoritative tenant selection on the hosted API are reserved for API-001 and system validation.

## Developer Self-Review - Corrected Submission
## Historical Developer Submission — Attempt 1
## Historical Developer Submission — Attempt 1

### Submission

On 2026-10-27 the developer published corrected WooCommerce commit `01b3be5` after the Attempt 1 Changes Requested decision. This historical submission included a dedicated implementation worktree and successful live `wp-env` integration. Initial connection and explicit-only sync remain intact. The unused undeployed legacy cleanup was removed, and the logging boundary was approved. This submission did **not** complete the task or promote `ARCH-049-WOOCOMMERCE-002`.

### Evidence and reconciliation note

At the time of this Attempt 1 submission, the parent snapshot did not record a subsequent `/moda_developer_create` claim. That historical gap prompted the Changes Requested decision below. Attempt 2 now records the developer claim and canonical-worktree synchronization, and its focused PHPUnit and Node tests have been rerun successfully.
The historical Attempt 1 review requested lifecycle evidence only: a durable correction-cycle claim, synchronized canonical worktrees, and focused PHPUnit results on the published implementation. Attempt 2 records the claim and synchronization and reran the focused PHPUnit and Node suites successfully; no source changes were required.

## Developer Self-Review Passed — Attempt 2

Attempt 2 passes developer self-review. The Attempt 1 Changes Requested item
was lifecycle evidence only; this attempt now has a durable developer claim and
recorded synchronization of the canonical parent worktree. The corrected
implementation remains committed and published at
`01b3be50ba8409f97d5dc9074f30a7b66d0020d8`. The acceptance criteria and work
items remain complete, and focused validation passed. No source changes or
scope deviations were introduced during Attempt 2.

### Evidence Reviewed

- Parent task branch was synchronized from current `origin/main` by merge
  `39549ff369cf38d24e69aa783f39f28e8bd0462a`; Attempt 2 claim commit
  `1155a8300d9b31a9d38305fd0f61febc88ddae2b` was published.
- Implementation worktree is clean at published
  `01b3be50ba8409f97d5dc9074f30a7b66d0020d8`; current implementation
  `origin/main` was already an ancestor.
- `composer test -- --filter ShopBrandPublicationTest`: **17 tests / 139
  assertions passed**.
- `node --test tests/integration/scenarios/shop-brand-runner.test.mjs
  tests/integration/wordpress-api-fixture.test.mjs`: **6/6 passed**.
- `git show --check HEAD` and parent task `git diff --check` passed.
- The parent worktree's unrelated untracked `typescript` file was preserved and
  not staged. Existing Docker-backed WordPress/Action Scheduler integration
  evidence is recorded above; it was not rerun in Attempt 2 because no source
  changed.

### Attempt State

Transitioned to `review`; `executor: null`, `claimed_at: null`, `attempt: 2`.
`completion_mode: developer` remains in force, so explicit developer completion
was pending at self-review. No downstream task was started, and no branch was
merged to `main`.

## Architect Review

### Review Status

Accepted — the explicit completion request supplied the architect decision
“Architect Review Accepted” on 2026-10-27. The current Attempt 2 developer
self-review and recorded validation were accepted. This task acceptance does
not certify hosted API processing or replace the terminal SYSTEM-TEST-001 gate.

### Review Notes

The accepted implementation follows the clarified scope: this undeployed feature
does not add legacy recurring-action cleanup, and the PHP-native WooCommerce
logger is used with bounded/redacted diagnostics and failure isolation.

### Reviewed Files

The task-owned implementation is published at
`01b3be50ba8409f97d5dc9074f30a7b66d0020d8` in the canonical
`moda-interact-woocommerce` task worktree.

### Validation Reviewed

Attempt 2 focused PHPUnit: 17 tests / 139 assertions passed. Focused Node
fixtures: 6/6 passed. The Docker-backed WordPress/Action Scheduler integration
passed before Attempt 2 and was not rerun because Attempt 2 made no source
changes.

### Architecture Conformance

Accepted within WooCommerce-local scope. Hosted API persistence and integrated
R2/system behavior remain separately owned gates.

### Follow-up

Proceed with the independent ARCH-049 dependency-frontier update. Keep
ARCH-049-SYSTEM-TEST-001 pending until all declared implementation dependencies
are complete and its normal manual gate is satisfied.

## Developer Completion Decision — Attempt 2

The developer explicitly invoked `/moda_developer_update
ARCH-049-WOOCOMMERCE-001 complete` on 2026-10-27 after the passing Attempt 2
self-review and architect acceptance recorded above. All Work Items and
Acceptance Criteria are checked. The implementation task branch is clean and
published at `01b3be50ba8409f97d5dc9074f30a7b66d0020d8`; the parent task record
is being committed and pushed on `task/ARCH-049-WOOCOMMERCE-001`. Attempt number
remains 2. No task branch was merged into `main`.
