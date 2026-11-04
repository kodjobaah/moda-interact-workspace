---
id: ARCH-058-SHOPIFY-001
architecture_id: ARCH-058
title: Enable Shopify shipping-policy read permission through the existing installation lifecycle
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables:
- ARCH-058-MCP-003
- ARCH-058-SYSTEM-TEST-001
created: '2026-11-04'
updated: '2026-11-04'
---

# ARCH-058-SHOPIFY-001: Enable Shopify shipping-policy read permission through the existing installation lifecycle

## Architecture

Architecture ID: `ARCH-058`. Parent: `docs/architecture/ARCH-058-commerce-agent-product-discovery.md`. Normative contracts: `docs/architecture/ARCH-058/contracts.md`, especially section 2.3. Coordinator: `moda_architect`.

**Defined but not materialised.** This portable definition does not establish a task branch, worktree, commit, deployed app configuration or merchant permission. Materialise through `/moda-task ARCH-058-SHOPIFY-001 --definition <path-to-this-file>`; use the implementation worktree and canonical workspace root supplied by that launcher.

## Objective

Declare the Shopify Admin `read_legal_policies` permission required by MCP's native shipping-policy reader and document how the intended app and existing installations receive that permission. Preserve the existing installation, offline-session and scope-update lifecycle. A declaration is not evidence that a particular merchant's offline token has the grant.

## Context

- `shopify.app.moda-interact.toml` and `shopify.app.toml` describe different app identities. Both lack `read_legal_policies` in the supplied snapshot. The named app declares webhook API `2026-07`; the separate default app declares `2026-10`.
- `app/shopify.server.js` obtains OAuth credentials from the existing platform configuration and requested scopes independently from external `SCOPES`. Editing a TOML cannot update that runtime setting or an already installed merchant's token.
- The authenticated `app/routes/webhooks/app/scopes-update/route.jsx` already persists the Shopify-reported session scope and uses persisted offline scope for existing discount eligibility. `shopify.Session.scope` already exists. Shipping does not require a new scope table, webhook or credential authority.
- Accepted `ARCH-049-SHOPIFY-001` and `docs/arch-049/SHOPIFY-001-brand-read-permission.md` provide the existing distinct-app, required-scope and grant-verification precedent. Reconcile accepted `ARCH-057-SHOPIFY-009` lifecycle/configuration work at task start; do not overwrite its session-race or webhook fixes.
- `ARCH-058-MCP-003` owns policy queries, actual offline-grant preflight and missing-scope results. Existing product-read access is sufficient for the selected Shopify inventory-item shipping fields; this task adds no `read_inventory`, shipping-rate or write permission.

## Scope

In `moda-interact` only:

1. Add required `read_legal_policies` exactly once to each relevant deployable app configuration without dropping or changing existing permissions or app identity.
2. Add focused configuration tests proving the exact additive permission change and preserving the existing scope-update route/subscription contract.
3. Add a concise operator runbook for selected-app validation, external `SCOPES` alignment, normal required-scope approval and actual offline-grant verification.
4. Confirm that the existing generic authenticated scope persistence remains the authority used by downstream MCP; no new lifecycle implementation is required.

## Out of Scope

No MCP implementation, provider policy/product query in the app runtime, shipping-policy ingestion or storage, new Shared schema, Database migration, custom OAuth/optional-scope flow, new webhook, scope polling, Admin or Gateway change, app deployment, merchant reauthorisation, live cart quote, cart/checkout mutation or customer send. Do not implement or reopen ARCH-049/ARCH-057 tasks, change unrelated app versions/scopes/subscriptions, or edit any `docs/decisions/**/_index.md`.

## Requirements

### Source, ownership and exact configuration change

- Read this repository's `AGENTS.md` and use its Shopify AI Toolkit guidance in the execution host for Shopify platform work. Do not add that tooling to the application repository. Use the prepared launcher evidence and the existing task/worktree/VCS policies; do not create a second implementation checkout or infer a developer-specific absolute path.
- Inspect accepted source before editing and record the relevant ARCH-049/ARCH-057 baseline. Preserve newer accepted configuration and lifecycle fixes. If app identity or configuration ownership cannot be reconciled, return the concrete conflict to the architect.
- Append `read_legal_policies` once to the required `access_scopes.scopes` in `shopify.app.moda-interact.toml` and `shopify.app.toml`. Retain every existing scope, its relative order, the distinct client IDs, URLs, redirect URLs, distribution settings, webhook API versions and existing subscriptions. Do not add this permission to `optional_scopes` or replace either scope list with a newly invented common list.
- In the supplied source, the named app's existing scopes are `read_customers,read_discounts,read_locales,read_markets,read_orders,read_products,read_brand`; the default app's are `write_products,write_metaobjects,write_metaobject_definitions,read_brand`. These establish preservation fixtures, not permission to remove additional scopes present in accepted source.
- The accepted ARCH-049 runbook classifies `shopify.app.moda-interact.toml.good` and `.test` as snapshot artifacts. Record their disposition and leave them unchanged. If accepted deployment evidence identifies another active app configuration, stop for an explicit configuration-scope reconciliation rather than silently deploying an artifact or ignoring an active target.
- Preserve the existing `app/scopes_update` subscription and authenticated route. Do not duplicate subscriptions or add an after-auth registration mechanism. No runtime environment default may silently append a permission to `SCOPES`.

### Existing grant lifecycle and rollout evidence

- Add `docs/shipping-policy-read-permission.md`. Explain that the operator must identify the actual selected app/client and align its deployed required-scope configuration with external runtime `SCOPES`, retaining all unrelated permissions. A selected-config/API-key mismatch is a rollout failure, not permission to switch app identity.
- Reuse the current Shopify required-scope approval/authentication path for installed shops. Explain the distinction between configuration deployment, merchant approval, an authenticated scope-update notification and the currently usable persisted offline grant. Do not implement custom consent requests or fabricate scope values in Session rows.
- Document selected-app validation, including the existing named-config command `npx shopify app config validate --config moda-interact`, and the later developer-operated selected-config deployment. Commands that deploy or cause merchant approval are instructions for rollout; do not execute them as part of this implementation task.
- Document the read-only `currentAppInstallation { accessScopes { handle } }` verification using the actual installation's authorized Admin client, including inspection of GraphQL errors on HTTP 200. Verify the persisted offline session used by MCP; an online grant, a different shop/token, the webhook payload alone or an environment scope declaration does not substitute.
- State the downstream behavior precisely: MCP checks `read_legal_policies` from its trusted offline grant before requesting policy data. An absent grant produces the normal `SCOPE_NOT_GRANTED` policy outcome and leaves independent product discovery usable. A provider 401/403 or GraphQL failure after an attempted granted request remains an actual error. This task documents that contract; MCP-003 implements it.
- The existing webhook's generic scope write already handles the additional permission. Preserve its Shop-before-Session ordering, missing-session/uninstall protections, offline-scope checks and after-commit discount publication. Do not change that code merely to add a shipping-specific status field or a second source of grant truth.
- Do not require successful live approval for every shop to accept this configuration-only task. Report live deployment/grant verification as `NOT_RUN` when unavailable, and leave it as an explicit rollout prerequisite for that shop's native policy data. Never claim configuration tests prove a merchant grant.

### Diagnostics

Use the existing Shared structured logging convention if a scoped change genuinely needs runtime diagnostics: `@modainteract/moda-interact-shared/logging` and `docs/observability/shared-logging.md`. This configuration-only task does not need a new logger, telemetry framework or event. Do not put tokens, session rows, credential material, raw webhook bodies or customer data in reports or logs.

## Work Items

- [ ] Reconcile accepted app identities, active configuration files, external scope ownership and ARCH-049/ARCH-057 changes.
- [ ] Add the single required read permission to the two deployable TOMLs while preserving their existing independent configuration.
- [ ] Add `tests/unit/webhooks/shopify-shipping-scope-config.test.ts` for exact-once required scope, prior-scope preservation, distinct identities/versions and the existing scope-update subscription.
- [ ] Add the selected-app/offline-grant rollout runbook and the downstream missing-policy-scope behavior.
- [ ] Run the focused validation, record explicit live checks not performed, set status to `review` and return to the architect.

## Interfaces / Contracts

This task produces configuration and operator prerequisites for `CommerceShippingInformationSchema` consumption by MCP. It creates no API, queue, persistence or model-facing contract. `docs/architecture/ARCH-058/contracts.md` section 2.3 remains authoritative for `commerce_get_shipping_information` / `shipping.getInformation` version `1.0.0` and its policy outcomes.

Primary edit paths: `shopify.app.moda-interact.toml`, `shopify.app.toml`, new `tests/unit/webhooks/shopify-shipping-scope-config.test.ts`, and new `docs/shipping-policy-read-permission.md`. Read/reuse `app/shopify.server.js`, `app/routes/webhooks/app/scopes-update/route.jsx`, existing scope/authentication tests and `docs/arch-049/SHOPIFY-001-brand-read-permission.md`. No runtime edit is required unless the architect accepts a concrete discovered gap in this configuration-only scope.

Official references: [Admin 2026-07 ShopPolicy and its read permission](https://shopify.dev/docs/api/admin-graphql/2026-07/objects/ShopPolicy), [Admin Shop policy collection](https://shopify.dev/docs/api/admin-graphql/2026-07/objects/Shop), [ShopPolicyType](https://shopify.dev/docs/api/admin-graphql/2026-07/enums/ShopPolicyType), [manage app access scopes](https://shopify.dev/docs/apps/build/authentication-authorization/manage-access-scopes), and [manage app configuration files](https://shopify.dev/docs/apps/build/cli-for-apps/manage-app-config-files). Documentation describes provider behavior; it is not evidence of deployed app configuration or a live grant.

## Dependencies

None. This task consumes the frozen architecture, existing scope lifecycle and accepted repository baseline; it does not depend on an unpublished Shared implementation. Reconciliation with concurrent accepted ARCH-057 work is a source gate, not authority to redo that work.

## Enables

- `ARCH-058-MCP-003`: use the existing installation grant for native policy preflight and independently available product shipping facts.
- `ARCH-058-SYSTEM-TEST-001`: verify the permission-declaration and granted/missing-policy paths without blocking global product discovery.

## Acceptance Criteria

- [ ] Both deployable TOMLs parse and contain `read_legal_policies` exactly once as a required scope; every prior permission and each app's own identity/version/subscription remains intact.
- [ ] Snapshot artifact variants are accounted for and not silently promoted to deployment configurations.
- [ ] External `SCOPES` alignment, selected app identity, required-scope approval and actual persisted offline-grant verification are documented distinctly.
- [ ] Existing scope/update/authentication tests confirm the generic persisted-scope lifecycle remains intact; no shipping-specific credential store, webhook or OAuth flow was introduced.
- [ ] The runbook states the frozen missing-scope versus attempted-provider-error behavior and does not claim that policy permission is required for ordinary product reads.
- [ ] Local tests and any unperformed live deployment/grant checks are reported truthfully. No deployment, provider policy fetch, database write for a fabricated grant or customer send occurred.

## Validation

Run from the canonical launcher-provided Shopify implementation worktree. Before the first Node command: `command -v node >/dev/null 2>&1 || source "$MODA_WORKSPACE_ROOT/scripts/bootstrap-node.sh"`.

- [ ] Inspect the actual `package.json`, then run the existing test runner on the owned configuration test and relevant established lifecycle tests:

   ```bash
   npm exec -- vitest run tests/unit/webhooks/shopify-shipping-scope-config.test.ts tests/unit/webhooks/shopify-brand-scope-config.test.ts tests/unit/routes/scopes-update.test.jsx tests/unit/routes/auth-catchall.test.ts
   ```

   The new test must exercise both real TOMLs, require exact-once addition, retain existing scopes and each distinct identity/API version, and check the existing scope-update subscription. It must not hard-code a different deployed client or rely only on a new hand-built scope list.

- [ ] Parse both real files with Python 3.11+ `tomllib` or the repository's existing actual TOML parser. With Python available:

   ```bash
   python3 - <<'PY'
   import tomllib
   from pathlib import Path
   for name in ('shopify.app.toml', 'shopify.app.moda-interact.toml'):
       data = tomllib.loads(Path(name).read_text())
       scopes = [value.strip() for value in data['access_scopes']['scopes'].split(',')]
       assert scopes.count('read_legal_policies') == 1, name
       assert len(scopes) == len(set(scopes)), name
       assert 'read_legal_policies' not in data['access_scopes'].get('optional_scopes', []), name
   PY
   ```

- [ ] Run `npm run typecheck` and `git diff --check`. Do not run a production deployment or a broad unrelated test/build suite to manufacture rollout evidence. If a known baseline condition is encountered, follow `docs/development-baseline.md` only for that condition, prove no regression and record the actual result.
- [ ] Review the runbook against both source configurations, runtime `SCOPES` ownership and the authenticated offline-session flow. Record missing live access/approval as `NOT_RUN`; do not report it as passed or require a fabricated merchant grant to complete local validation.

## Stop Condition

Stop for unreconciled app identity, an additional active configuration, a required scope/lifecycle change outside the additive read permission, or an accepted ARCH-057 conflict that cannot be preserved. Return the concrete issue to `moda_architect`. When scoped work and required local validation pass, complete the report, set status to `review` and return to the architect. Do not mark complete, deploy either app, obtain merchant consent, start MCP-003, modify another repository or edit an index.

## Implementation Notes

Keep edits in the canonical dedicated implementation worktree and use the launcher's workspace root for support commands. Do not infer a production installation from a local config selection. Merchant permission becomes usable only through the existing approved installation lifecycle; the standard product feature remains separately authorized. The operator performs selected-config deployment and live grant checks after the accepted implementation is available.

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

Accepted source will preserve the existing distinct app identities and generic offline-scope lifecycle. The actual deployed configuration and installed grants will be verified during developer-operated rollout.

### Unresolved Issues

Live app deployment, external runtime scope configuration and installed merchant approval are not evidenced by this portable definition.

### Physical Worktree and Synchronization Evidence

Not materialised. Record the actual launcher preparation packet, canonical parent/implementation worktrees and start-of-attempt synchronization when execution begins; do not invent them here.

### Architectural Concerns

None beyond the explicit app-identity, accepted-source and grant-provenance gates above.

## Architect Review

### Review Status

Pending.

### Review Notes

Not reviewed.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Not assessed.

### Follow-up

None.
