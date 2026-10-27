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
status: in_progress
priority: 30
executor: developer
claimed_at: '2026-10-27T12:06:02Z'
attempt: 1
depends_on: []
enables: ["ARCH-049-SYSTEM-TEST-001"]
created: 2026-10-25
updated: 2026-10-27
---

# Publish WooCommerce Site Identity branding through the Moda API

## Architecture

`ARCH-049` — `docs/architecture/ARCH-049-shopbrand-public-media-configuration.md`; coordinator `moda_architect`. **Portable task definition, not materialised in a developer Git worktree.**

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

- [ ] Create PHP source reader and normalised payload builder.
- [ ] Add authenticated Moda API client publication and bounded retry hooks.
- [ ] Test source changes/removals and missing logo/icon through an explicit new snapshot.
- [ ] Ensure installation/connection bootstrap is idempotent; remove brand-change hooks and daily reconciliation, clean up legacy recurring actions, and expose reusable internal `requestSync()`.
- [ ] Document rollout/reconnect and version support, including that post-install branding changes are not automatically synchronised.

## Interfaces / Contracts

Produces `woo.shop-brand.v1` to `POST /v1/woocommerce/shop-brand`; consumes the response `status: updated|unchanged`. No direct database or R2 access. WordPress-origin URLs are data, never Moda-authorised fetch destinations.

## Dependencies

None. The `woo.shop-brand.v1` API route, request and response contract are already fully specified in the separately owned `ARCH-049-API-001` definition. Implement and test the plugin independently against an authenticated local HTTP fixture; do not require an API implementation commit to author a producer client. Production activation and the end-to-end System Test still require accepted API-001.

## Enables

- ARCH-049-SYSTEM-TEST-001

## Acceptance Criteria

- [ ] Against the frozen authenticated `woo.shop-brand.v1` HTTP fixture, a fresh Woo connection queues one initial branding publication, and an already-connected installation is bootstrapped once; subsequent WordPress changes **do not** publish without an explicit future sync request. The reusable `requestSync()` captures changed/removed assets correctly. Real hosted API delivery is certified only after API001 acceptance in SYSTEM-TEST-001.
- [ ] No new public WP route and no checkout latency regression.
- [ ] Stable retries do not duplicate observations or leak installation credentials.
- [ ] Removed logo/icon becomes a null source rather than retaining a false current READY.

## Validation

- [ ] PHP unit tests with stubbed WP Site Identity APIs and attachment data.
- [ ] Client API/auth body/response tests, bounded Action Scheduler retries, absence of automatic/daily triggers, cleanup of existing recurring jobs and explicit sync reuse.
- [ ] Woo plugin build/lint/JS or PHP tests required by affected code and `git diff --check`.

## Stop Condition

After the defined Work Items, Acceptance Criteria and Validation are complete, record the Completion Report and change task status to `review`; hand off to `moda_architect` and STOP. Do not continue into a dependent task or change an `_index.md`.

## Implementation Notes

All task work must use the canonical launcher-provided **dedicated parent and implementation worktrees**, synced task/<TASK_ID> branches and start-of-attempt evidence. Inspect the actual pinned package scripts, source and existing conventions before editing. Do not merge branches, push main, edit another repository, start an enabled task or change any `docs/decisions/**/_index.md`. Use structured logging via `@modainteract/moda-interact-shared/logging`; secrets and full untrusted URLs must not enter diagnostics. Document changed files, relevant test commands, results, security/tenant checks, commits and worktree evidence in the Completion Report.

No additional assumptions are authorised.

## Completion Report

### Status

In Progress — Developer Attempt 1 claimed at `2026-10-27T12:06:02Z`. The developer explicitly took over this ready agent-owned task; `assigned_agent: moda_woocommerce` and the task scope are unchanged. Canonical parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-049-WOOCOMMERCE-001` is on `task/ARCH-049-WOOCOMMERCE-001`, clean at `286a2bf371efc4bb122842943d7f1bb1ee8543c5`, created from and current with `origin/main`; no remote task branch existed at preparation. Canonical implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-049-WOOCOMMERCE-001` is on `task/ARCH-049-WOOCOMMERCE-001`, clean at `29c1d7afd94a074d6b5de2410b4d19a2adc73a1c`, created from and current with `origin/main`; no remote task branch existed at preparation. Recursive submodule status is empty (no submodules are declared). The task has no dependencies. Claim and developer takeover are committed and published on the parent task branch; implementation work begins in the canonical implementation worktree.

### Developer Takeover

On 2026-10-27, `/moda_developer_create ARCH-049-WOOCOMMERCE-001` was invoked
for this ready agent-owned task. Execution and completion authority transfer
to the developer: `execution_mode: developer`, `completion_mode: developer`.
Logical ownership remains `assigned_agent: moda_woocommerce`; task scope,
acceptance criteria, dependencies and validation requirements are unchanged.
Attempt 1 is claimed by `developer`. The canonical parent and implementation
worktrees were created from current `origin/main`, synchronized and verified
clean before the claim. There was no pre-existing local or remote task branch
and no conflicting worktree registration. Recursive implementation submodule
status was empty.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

None beyond the explicit architecture/task contract.

### Unresolved Issues

None; live environment availability is a validation prerequisite and must be reported if missing.

### Architectural Concerns

None reported.

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
