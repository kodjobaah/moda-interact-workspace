---
id: ARCH-049-WOOCOMMERCE-001
architecture_id: ARCH-049
title: Publish WooCommerce Site Identity branding through the Moda API
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on: ["ARCH-049-API-001"]
enables: ["ARCH-049-SYSTEM-TEST-001"]
created: 2026-10-25
updated: 2026-10-25
---

# Publish WooCommerce Site Identity branding through the Moda API

## Architecture

`ARCH-049` — `docs/architecture/ARCH-049-shopbrand-public-media-configuration.md`; coordinator `moda_architect`. **Portable task definition, not materialised in a developer Git worktree.**

## Objective

Read site branding locally within the installed WordPress/WooCommerce plugin and publish canonical metadata to the authenticated Moda API; do not expose a new WordPress REST endpoint.

## Context

WooCommerce does not have Shopify's single Brand Admin object. WordPress Site Logo, Site Icon, site title and attachment metadata are available through native PHP functions; the plugin already owns secure server-side Moda API communication and Action Scheduler workflows.

## Scope

- Add a modular PHP `includes/ShopBrand/` source reader, DTO builder and publisher, plus client method in `ModaApiClient`.
- Read the site title and native WordPress logo/site-icon attachments without scraping themes or arbitrary plugin options.
- Send `woo.shop-brand.v1` to the authenticated Moda API at install/connect and after relevant site identity changes, with bounded transient retries.
- Add focused WordPress/PHP unit tests for classic/block themes, missing assets, changed/deleted assets and offline API.

## Out of Scope

- New externally reachable WordPress route, requiring Background to call merchant WordPress sites, uploading R2 images, saving directly to Moda PostgreSQL or implementing merchant editor UI.

## Requirements

### R1. Source selection

Read brandName via `get_bloginfo('name')`. Prefer site-logo attachment ID from WordPress Site Identity (`get_theme_mod('custom_logo')` for classic themes; supported `site_logo` option when used by block themes). Read URL via `wp_get_attachment_image_url($id,'full')`, dimensions from `wp_get_attachment_metadata($id)`, alt text from `get_post_meta($id,'_wp_attachment_image_alt',true)`. For square logo use `get_site_icon_url()` / `get_option('site_icon')` with attachment metadata when available. Do not claim WordPress has a reliable native cover image; send `coverImage: null` initially. Treat absent logo/icon as explicit null; use no arbitrary theme-specific image extraction.

### R2. Publication contract

Use `ModaApiClient` existing installation credentials and exact `woo.shop-brand.v1` payload in API-001. `eventId` is stable across retries for the same canonical snapshot (e.g., deterministic installation ID + source digest); `observedAt` is the timestamp at snapshot capture and is preserved on retry. Do not include shopId credentials or hidden server settings in the body. Source URLs must be HTTPS to be eligible for media processing; if WordPress source is HTTP, submit a null/not-ready source rather than silently upgrading schemes. Leave storefront behaviour unchanged.

### R3. Triggers and retries

Publish after successful installation/connect and on WordPress site title/logo/site-icon changes (use supported WP action/option hooks as appropriate), with a bounded once-daily reconciliation as a recovery path for missed hooks. Use Action Scheduler if available, with deterministic job identity to coalesce duplicate triggers, retry transient 408/429/5xx/network failures (e.g., 20s, 60s, 5m, maximum five attempts) and stop on definitive 4xx. Publishing must not block storefront checkout or reveal credentials in logs. Source removal publishes a complete snapshot containing null for the removed role.

### R4. Security

Only locally read WordPress settings/attachment metadata. Never install a public merchant-server endpoint to fetch images for Background; Background later fetches only the provider's HTTPS source URL subject to its SSRF policy.

## Work Items

- [ ] Create PHP source reader and normalised payload builder.
- [ ] Add authenticated Moda API client publication and bounded retry hooks.
- [ ] Test source changes/removals and missing logo/icon.
- [ ] Document rollout/reconnect and version support.

## Interfaces / Contracts

Produces `woo.shop-brand.v1` to `POST /v1/woocommerce/shop-brand`; consumes the response `status: updated|unchanged`. No direct database or R2 access. WordPress-origin URLs are data, never Moda-authorised fetch destinations.

## Dependencies

- ARCH-049-API-001

## Enables

- ARCH-049-SYSTEM-TEST-001

## Acceptance Criteria

- [ ] Fresh Woo connection publishes site branding, and subsequent changes update it.
- [ ] No new public WP route and no checkout latency regression.
- [ ] Stable retries do not duplicate observations or leak installation credentials.
- [ ] Removed logo/icon becomes a null source rather than retaining a false current READY.

## Validation

- [ ] PHP unit tests with stubbed WP Site Identity APIs and attachment data.
- [ ] Client API/auth body/response tests and Action Scheduler retries.
- [ ] Woo plugin build/lint/JS or PHP tests required by affected code and `git diff --check`.

## Stop Condition

After the defined Work Items, Acceptance Criteria and Validation are complete, record the Completion Report and change task status to `review`; hand off to `moda_architect` and STOP. Do not continue into a dependent task or change an `_index.md`.

## Implementation Notes

All task work must use the canonical launcher-provided **dedicated parent and implementation worktrees**, synced task/<TASK_ID> branches and start-of-attempt evidence. Inspect the actual pinned package scripts, source and existing conventions before editing. Do not merge branches, push main, edit another repository, start an enabled task or change any `docs/decisions/**/_index.md`. Use structured logging via `@modainteract/moda-interact-shared/logging`; secrets and full untrusted URLs must not enter diagnostics. Document changed files, relevant test commands, results, security/tenant checks, commits and worktree evidence in the Completion Report.

No additional assumptions are authorised.

## Completion Report

### Status

Not Started — defined but not materialised.

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
