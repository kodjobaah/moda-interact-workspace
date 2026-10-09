---
id: ARCH-026-WOOCOMMERCE-007
architecture_id: ARCH-026
title: Synchronize WooCommerce store international context
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 40
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-026-WOOCOMMERCE-003
  - ARCH-026-WOOCOMMERCE-005
  - ARCH-026-API-004
enables: []
created: 2026-10-09
updated: 2026-10-09
---

# Synchronize WooCommerce store international context

## Architecture

Architecture ID: `ARCH-026`

Architecture document: `docs/architecture/ARCH-026-woocommerce-application-foundation.md`

Coordinator: `moda_architect`.

## Objective

Allow an already-connected WooCommerce merchant to synchronize authoritative WordPress/WooCommerce store locale, language, named time zone and store country into provider-neutral Moda `Shop` context, independently of reconnecting or reactivating Free credits.

## Context

The accepted WOO-005 overview displays four international-context values returned by the API-003 bootstrap read. Those persisted Shop columns are currently null after a successful LocalWP connection because WOO-003's connect request sends only `siteUrl`, `attemptId` and `bootstrapSecret` and no provider-specific international-context writer exists. This task consumes `ARCH-026-API-004`, which owns the authenticated context-only command; it must not change the established site verification or connection flows.

## Scope

`moda-interact-woocommerce` only:

- Add a PHP store-context resolver for authoritative WordPress/WooCommerce site/store settings.
- Add a PHP client method for API-004's authenticated context-only `PUT` command.
- Expose one administrator-authorized, zero-input WordPress REST action to synchronize those settings server-side.
- Add an explicit, translatable **Sync store settings** action/state to the connected WooCommerce Admin overview, then reread the existing merchant bootstrap document after success.
- After a successful first Connect, trigger one separate best-effort sync (outside installation/Free activation); failure cannot delay, undo or misreport the successful connection. Never sync implicitly on ordinary GET/page load.
- Add focused PHP/JS/WordPress integration coverage.

## Out of Scope

- Changing the existing Connect request/response schema, site-control challenge, credential rotation or HTTP timeouts.
- Sending installation credentials, Woo store values or authenticated Moda API calls from browser JavaScript.
- Shopify tenant updates or direct Moda PostgreSQL/Redis access.
- Automatic Commerce category assignment, product-category taxonomy mapping, a merchant category picker or prompt activation.
- General Woo checkout/order event integration or billing.
- Store context synchronization on every page read, cron schedule or background job.

## Requirements

1. **True store locale:** Derive provider-native locale from the WordPress site's configured locale (`get_locale()`/site configuration), not the current admin's `get_user_locale()` or `_locale=user`. Preserve a valid WordPress-native value such as `en_GB`, `pt_BR` or a locale with a legitimate variant exactly; do not enforce a fixed list based on available Moda translations.
2. **Independent normalized language:** Supply a BCP-47-compatible language tag only when the store locale can be normalized *safely and unambiguously*, or when another authoritative store-language configuration is available. Do not blindly replace every underscore with a hyphen (e.g. variant locales can be complex). When normalization is uncertain, send `null`, not an assumed English value. The React administrator UI locale remains independent.
3. **Time zone:** Read the WordPress **site** time-zone setting. Send a named IANA value such as `Europe/London` only when present/valid; WordPress sites configured with a bare UTC offset must send `null` rather than pretending that offset is an IANA identifier. Do not infer country from time zone.
4. **Country:** Prefer the WooCommerce store/base location (`wc_get_base_location()` or equivalent supported Woo settings). Send a legitimate upper-case two-letter store country such as `GB`; send `null` if unset/unsupported. Do not infer it from a visitor IP, user profile, browser locale or address text.
5. **Boundary/security:** A WordPress REST `POST /wp-json/moda-interact/v1/merchant/store-context/sync` action accepts no business data or tenant ID from the browser. Authorize with `manage_woocommerce` and normal WordPress REST nonce/cookie protection. The server must validate installed connection state and site URL continuity, then send the derived snapshot to API-004 over the existing server-side `ModaApiClient` using the stored installation credential. Do not expose credentials or sensitive headers in the response, logs or JavaScript.
6. **Failure isolation:** A failed context update must never disconnect a previously connected Shop, force a new Connect, rotate credentials, reset the Free plan/credits, change category state or fabricate context values. Show a bounded retryable sync error while leaving the established Connected state intact. Remote outage/malformed responses remain distinct from success.
7. **User experience:** The connected overview displays the existing `Not available` values honestly until synchronization succeeds. **Sync store settings** is an actual working action and reloads `GET /wp-json/moda-interact/v1/merchant/bootstrap` on success; avoid placeholder controls. New visible strings use the `moda-interact` text domain and WordPress localization, without a translation-coverage allowlist.
8. **LocalWP verification:** An existing connected `woocommerce-sandbox.local` installation must synchronize available context **without reconnecting**. On a site with configured UK base country, `en_GB` site locale and `Europe/London` site timezone, the overview should show the actual provider values and a safe normalized language tag where supported. If site settings differ, display those actual values; do not hardcode this example.

## Work Items

- [ ] Add a bounded, independently tested PHP store-context resolver.
- [ ] Add authenticated API-004 client transport using the existing connection/credential store and exact API contract.
- [ ] Add administrator-only no-body WordPress REST sync route with site-URL continuity checks and predictable failure mapping.
- [ ] Add explicit connected-Overview sync action/status; trigger one independent post-Connect sync, and refresh the existing read-only bootstrap result on sync success.
- [ ] Confirm Connect/Reconnect/Free credit behaviour is unaltered, including when context sync fails.
- [ ] Add PHPUnit, JS controller and WordPress integration coverage for new and already-connected stores.

## Interfaces / Contracts

**Remote API:** `ARCH-026-API-004` (`PUT /v1/merchant/store-context`, OpenAPI `v1`, install-principal authenticated), not a new local invented schema.

**Local REST:** `POST /wp-json/moda-interact/v1/merchant/store-context/sync` with no user-provided context or tenant ID, privileged administrator only.

**Readback:** Existing `GET /wp-json/moda-interact/v1/merchant/bootstrap` → `GET /v1/merchant/bootstrap` → database Shop values. No read-response contract changes.

## Dependencies

- `ARCH-026-WOOCOMMERCE-003` — accepted connection and server-only installation credential.
- `ARCH-026-WOOCOMMERCE-005` — accepted overview bootstrap presentation.
- `ARCH-026-API-004` — the authenticated context update API must be architect-accepted Complete before this task is Ready.

## Enables

None. Integrated system-test work may be defined once the complete implementation/deployment/observability dependency set is identified and accepted.

## Acceptance Criteria

- [ ] A logged-in WooCommerce administrator can synchronize a connected store and immediately see source-derived context on the existing Overview; a non-admin cannot.
- [ ] A store site locale does not change merely because a different WordPress administrator uses a different UI language.
- [ ] WordPress locale variants preserve their native identity, and ambiguous language tags remain null; no closed locale allowlist appears.
- [ ] UTC-offset-only WordPress time zone is not misrepresented as a named IANA time zone; an unset Woo base country remains null.
- [ ] Browser requests cannot control the remote Shop ID, site identity, API origin, context payload or installation credentials.
- [ ] Post-Connect synchronization succeeds independently when the API is available; when sync fails, connection remains successful and a manual retry cannot change Connected status, credential version, Shop/installation identity, Free plan or the remaining five lifetime credits.
- [ ] No Commerce category state is created or changed; an unselected category remains visibly unselected.
- [ ] Existing WooCommerce Admin connection, overview and HPOS/navigation fixes remain functional after replacing the built plugin ZIP in LocalWP.

## Validation

- [ ] `composer lint`
- [ ] `composer test`
- [ ] `npm run test:js`
- [ ] `npm run lint:js`
- [ ] `npm run plugin-zip`
- [ ] LocalWP WordPress administrator/unauthorised REST matrix and real API-004 read-after-write test, including one deliberate simulated failure/retry.
- [ ] `git diff --check` and task-isolated worktree/report evidence.

## Stop Condition

After the Work Items, Acceptance Criteria and required Validation are satisfied, set the task to `review`, complete the Completion Report, return to `moda_architect` and STOP. Do not begin Commerce category selection, Background processing or paid-billing tasks.

## Implementation Notes

The API-004 command is an independent **business-context update** after installation authentication. An already-connected installation need not rotate credentials or run the Free activation transaction to refresh its WordPress/WooCommerce settings. The existing Merchant Overview bootstrap GET stays a read; do not introduce a mutation side effect in its GET handler. Avoid a new service-local JSON logger; WordPress/WooCommerce provider-specific failure handling remains local, while the hosted API uses Shared structured logging.

## Completion Report

### Status

Not Started.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

None.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

Pending.

### Review Notes

Pending implementation review.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending.

### Follow-up

Await repository implementation and Completion Report.
