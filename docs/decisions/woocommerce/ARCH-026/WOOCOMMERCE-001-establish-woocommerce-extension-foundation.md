---
id: ARCH-026-WOOCOMMERCE-001
architecture_id: ARCH-026
title: Establish the Moda Interact WooCommerce extension foundation
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 10
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables:
  - ARCH-026-WOOCOMMERCE-002
created: 2026-10-01
updated: 2026-10-01
---

# Establish the Moda Interact WooCommerce extension foundation

## Architecture

Architecture ID:

`ARCH-026`

Architecture document:

`docs/architecture/ARCH-026-woocommerce-application-foundation.md`

Coordinator:

`moda_architect`

## Objective

Establish `moda-interact-woocommerce` as a reproducible, buildable, testable and
installable WordPress/WooCommerce extension using the official WooCommerce
extension-development model.

The completed task must prove the following bounded runtime path:

```text
moda-interact-woocommerce source
        |
        v
PHP + React/JavaScript build
        |
        v
installable WordPress plugin
        |
        v
WordPress + WooCommerce
        |
        v
activate Moda Interact
        |
        v
WooCommerce Admin
        |
        v
minimal Moda Interact React page renders
```

This task establishes the extension foundation only.

It MUST NOT connect to the Moda backend, access Moda PostgreSQL, create Woo
installation identity, implement WordPress REST application APIs, publish events,
implement billing, or implement merchant business features.

## Context

ARCH-026 introduces the WooCommerce-facing application for Moda Interact.

Unlike `moda-interact`, which is a Moda-hosted Next.js Shopify application, the
WooCommerce-facing application executes inside the merchant's WordPress installation
as a WooCommerce extension.

The target runtime boundary is therefore:

```text
merchant WordPress installation

WordPress
    |
    +-- WooCommerce
            |
            +-- Moda Interact extension
                    |
                    +-- PHP runtime
                    |
                    +-- compiled React/JavaScript UI
```

PHP owns the WordPress/WooCommerce extension runtime.

React/JavaScript provides the modern WooCommerce Admin user interface.

The Node/npm toolchain is build/test tooling only. This task MUST NOT introduce a
separately hosted Node or React server for the WooCommerce merchant UI.

WooCommerce's official extension scaffold uses the WordPress `create-block` tool with
the WooCommerce `create-woo-extension` template. Use that supported foundation rather
than creating a bespoke PHP/JavaScript build system without a demonstrated need.

### Repository-provisioning readiness gate

This task is defined before the new implementation repository exists in the supplied
workspace snapshot.

Before this task may transition from `pending` to `ready`, the architecture
coordination layer MUST have verified all of the following:

```text
workspace repository path:
    moda-interact-woocommerce/

Git repository:
    provisioned and reachable

workspace submodule:
    moda-interact-woocommerce
    registered at the canonical workspace path

decision domain:
    docs/decisions/woocommerce/

logical owner:
    moda_woocommerce

launcher route:
    WOOCOMMERCE
        folder: woocommerce
        repository: moda-interact-woocommerce
        agent: moda_woocommerce

agent definitions:
    .codex/agents/moda_woocommerce.toml
    .claude/agents/moda_woocommerce.agent.md
```

Repository provisioning and workspace `.gitmodules` registration are
architect/developer coordination prerequisites. They are NOT implementation work for
this repository task.

The repository agent MUST NOT work around a missing provisioning checkpoint by
creating an unrelated repository, using another repository's worktree, or executing
from the shared/default checkout.

## Scope

Create the initial extension foundation in:

```text
moda-interact-woocommerce/
```

The repository MUST produce an installable WordPress extension whose installed plugin
directory is:

```text
moda-interact/
```

and whose main plugin bootstrap file is:

```text
moda-interact.php
```

The public plugin name is:

```text
Moda Interact
```

The WordPress text domain is:

```text
moda-interact
```

Use the PHP root namespace:

```text
ModaInteract\WooCommerce
```

Where a global PHP symbol is unavoidable, use a Moda-specific prefix rather than an
unqualified generic WordPress symbol.

Primary expected repository areas are:

```text
moda-interact-woocommerce/
    moda-interact.php
    composer.json
    composer.lock
    package.json
    package-lock.json
    README.md
    CHANGELOG.md

    includes/
        ...

    src/
        ...

    tests/
        ...

    build/
        generated output

    .wp-env.json
```

The exact scaffold-generated layout may differ where required by the current official
WooCommerce template. Do not preserve generated sample/demo code solely to match an
example tree.

### Official scaffold

Bootstrap from the current official WooCommerce extension template:

```text
@wordpress/create-block
    template:
        @woocommerce/create-woo-extension
```

Use `moda-interact` as the WordPress plugin slug.

The resulting generated dependency versions MUST be locked in the repository
lockfiles.

Do not subsequently float dependencies to `latest` merely because newer packages
exist.

### Development baseline

Provide a reproducible local WordPress/WooCommerce environment using repository-owned
`wp-env` configuration.

For the initial ARCH-026 development baseline, pin:

```text
WordPress:
    7.1.2

WooCommerce:
    11.1.2
```

Do not use an unpinned `latest` WooCommerce package in the reproducible validation
environment.

The product-wide minimum supported WordPress, WooCommerce and PHP versions are NOT
decided by this task. ARCH-026-WOOCOMMERCE-002 owns runtime compatibility/version
gates.

Record the PHP version actually used for validation.

### Minimal Woo Admin integration

The foundation MUST register one minimal React-powered Moda Interact page inside
WooCommerce Admin.

Canonical page identity:

```text
path:
    /moda-interact

display name:
    Moda Interact
```

The page exists only to prove that:

```text
PHP plugin bootstrap
        ->
WooCommerce Admin page registration
        ->
compiled JavaScript asset loading
        ->
React component rendering
```

works correctly.

The rendered content should remain deliberately minimal, for example:

```text
Moda Interact

WooCommerce extension foundation
```

Do not build the final navigation/dashboard in this task.

Do not create a branded top-level WordPress admin menu. Integrate with the normal
WooCommerce Admin navigation/page mechanism.

### Build and validation commands

The repository MUST expose clear, repository-local commands for:

```text
install JavaScript dependencies
install PHP dependencies
development asset build/watch
production asset build
JavaScript lint
PHP lint/static checks
JavaScript unit tests
PHP unit tests
WordPress/WooCommerce local environment start
WordPress/WooCommerce local environment stop
plugin ZIP creation
```

Prefer the standard WordPress/WooCommerce tooling produced by the official scaffold.

Do not require globally installed `wp-env` when the dependency can be pinned and
executed from the repository.

The README MUST document the exact commands actually provided by the repository.

## Out of Scope

- Moda backend/API connectivity.
- `moda-interact-api` or another hosted merchant API.
- Installation credentials.
- Woo store -> Moda `Shop` association.
- WordPress REST endpoints owned by Moda business features.
- PHP `ModaApiClient`.
- Remote HTTP calls to Moda.
- Moda PostgreSQL access.
- Redis/BullMQ access.
- `moda-interact-background` changes.
- Cart events.
- Checkout events.
- Order events.
- Product integration.
- Coupon/discount integration.
- Merchant Knowledge.
- CommerceAgent integration.
- WhatsApp integration.
- Woo Marketplace SaaS billing.
- Subscription management.
- Recovery-credit purchases.
- Merchant pricing plans.
- Recovery configuration.
- Recovery listing.
- Production merchant dashboard/navigation.
- Plugin activation/deactivation policy beyond what is required for the scaffold to
  activate successfully in the pinned Woo environment.
- Final product compatibility/version policy; WOO-002 owns that.
- HPOS/order-storage behaviour; this task performs no order operations.
- Cart/Checkout block integration.
- Storefront UI.
- WordPress telemetry.
- Moda telemetry.
- External CDN-hosted application code.
- iframe-hosted Moda admin UI.
- Generic plugin framework creation.
- Changes to any existing Moda implementation repository.

## Requirements

### R1 — Genuine WordPress/WooCommerce extension

`moda-interact-woocommerce` MUST build an ordinary WordPress plugin installed under:

```text
wp-content/plugins/moda-interact/
```

There MUST NOT be a separately running Node/Next/React server required for merchant
use.

PHP and compiled browser assets must execute inside WordPress/WooCommerce.

### R2 — Official extension-development foundation

Use the current WooCommerce extension scaffold/tooling as the initial foundation.

Generated code may be simplified or reorganised where needed, but do not replace the
standard WordPress/WooCommerce build stack with custom infrastructure without a
concrete incompatibility.

Remove irrelevant generated example functionality.

Do not ship sample blocks, demo storefront behaviour or unrelated extension examples
merely because the scaffold generated them.

### R3 — Stable Moda naming

Use consistently:

```text
Plugin name:
    Moda Interact

Plugin slug:
    moda-interact

Text domain:
    moda-interact

PHP namespace:
    ModaInteract\WooCommerce
```

Repository naming remains:

```text
moda-interact-woocommerce
```

The repository name is not required to equal the installed WordPress plugin-directory
name.

### R4 — Valid plugin metadata

The main plugin bootstrap MUST contain valid WordPress/WooCommerce plugin metadata
following current WooCommerce conventions.

Do not claim compatibility with WordPress/WooCommerce/PHP versions that were not
actually tested.

WOO-002 may subsequently widen or alter the compatibility floor after explicit
compatibility testing.

### R5 — WooCommerce Admin integration

Register the Moda Interact page through WooCommerce's supported Admin-page mechanism.

The foundation MUST NOT create a separate branded top-level WordPress menu.

The React page MUST be rendered by assets built and shipped with the plugin.

Do not load executable JavaScript or CSS from a third-party CDN.

### R6 — No business/backend coupling

The minimal React page MUST render without:

```text
Moda API
Moda database
installation credential
Redis
BullMQ
Background
billing provider
```

No fake remote connection or fake merchant business state may be presented as real.

### R7 — Reproducible dependency state

Commit the appropriate dependency lockfiles.

A clean checkout MUST be able to install dependencies and reproduce the production
build without depending on an existing developer `node_modules/` or Composer `vendor/`
directory.

Generated build output must follow one documented source-of-truth policy:

```text
either
    committed runtime artifact where required by WordPress packaging

or
    deterministically generated before packaging
```

Do not leave ambiguous/manual generated assets as an undocumented prerequisite.

### R8 — Reproducible local Woo environment

Repository-owned development configuration MUST start a disposable/local WordPress +
WooCommerce environment with the extension available for activation.

Pin the ARCH-026 bootstrap baseline rather than using an unbounded latest WooCommerce
release.

The environment MUST NOT require Moda production credentials.

### R9 — Installable package

Provide a repository-local command that creates:

```text
moda-interact.zip
```

The ZIP MUST install into WordPress as:

```text
wp-content/plugins/moda-interact/
```

The package MUST NOT contain:

```text
.git/
node_modules/
tests/
local environment state
developer credentials
environment secret files
unneeded source caches
```

Development source files may be included only when required by the chosen standard
packaging mechanism; runtime execution MUST depend on built assets, not a developer
build server.

Final Marketplace/distribution packaging hardening remains WOO-006.

### R10 — No secrets

No credentials, API keys, database URLs, Redis URLs or other Moda/server secrets may
be committed.

The extension foundation MUST not require any secret to render its minimal Admin page.

## Work Items

- [ ] Scaffold the repository from the current official WooCommerce
  `create-woo-extension` template using the `moda-interact` plugin slug.
- [ ] Remove generated sample/demo behaviour unrelated to the Moda WooCommerce Admin
  foundation.
- [ ] Establish the canonical Moda plugin name, slug, text domain, PHP namespace and
  bootstrap entry point.
- [ ] Commit deterministic npm and Composer dependency metadata/lockfiles.
- [ ] Add repository-owned local WordPress/WooCommerce development configuration
  pinned to the ARCH-026 baseline.
- [ ] Register one minimal React-powered `Moda Interact` page under WooCommerce Admin
  at `/moda-interact`.
- [ ] Ensure the React page is served from plugin-built local assets and requires no
  remote Moda service.
- [ ] Establish documented build, lint, PHP check, JS test, PHP test,
  local-environment and plugin-ZIP commands.
- [ ] Generate `moda-interact.zip` with the correct plugin root and without
  development-only dependency directories/secrets.
- [ ] Add focused tests covering PHP bootstrap/Admin registration and React foundation
  rendering.
- [ ] Document clean-checkout setup and local validation in the repository README.
- [ ] Verify no Moda backend/API/database/queue integration has been introduced.

## Interfaces / Contracts

This task creates no cross-service Moda runtime contract.

### WordPress plugin identity

```text
Plugin:
    Moda Interact

Slug:
    moda-interact

Text domain:
    moda-interact

PHP namespace:
    ModaInteract\WooCommerce
```

### WooCommerce Admin page identity

```text
Woo Admin path:
    /moda-interact
```

### Future contracts

The following future boundaries are intentionally NOT defined here:

```text
React -> plugin REST
plugin -> Moda API
Woo installation -> Moda Shop
commerce event -> Moda ingress
billing provider -> Moda
```

Those must be defined by their owning later ARCH-026 tasks.

## Dependencies

None.

There are no architecture-task dependencies.

However, execution has a mandatory repository-provisioning readiness gate described
under Context.

Until that gate is complete:

```text
status: pending
```

After the repository, workspace submodule and `moda_woocommerce` ownership are
verified by `moda_architect`, the architect may promote this task to:

```text
status: ready
```

without changing its implementation scope.

## Enables

- `ARCH-026-WOOCOMMERCE-002`

WOO-002 may begin only after this task is architect-reviewed and `complete`.

## Acceptance Criteria

- [ ] `moda-interact-woocommerce` contains a conventional installable
  WordPress/WooCommerce extension rather than a separately hosted web application.
- [ ] The installed WordPress plugin directory is `moda-interact/`.
- [ ] The main plugin bootstrap is `moda-interact.php`.
- [ ] Plugin name, slug, text domain and PHP namespace match this task.
- [ ] Clean npm and Composer dependency installation succeeds from committed
  manifests/lockfiles.
- [ ] Production JavaScript build succeeds.
- [ ] PHP checks/tests succeed.
- [ ] JavaScript lint/tests succeed.
- [ ] The pinned local WordPress/WooCommerce environment starts successfully.
- [ ] The plugin installs and activates with WooCommerce active.
- [ ] WooCommerce Admin exposes the Moda Interact page without creating a branded
  top-level WordPress menu.
- [ ] Navigating to the Moda page renders the minimal React foundation successfully.
- [ ] The browser does not require or receive a Moda server credential.
- [ ] The foundation makes no network call to a Moda backend.
- [ ] `moda-interact.zip` installs with the correct root directory and contains no
  `node_modules`, `.git`, local secrets or environment state.
- [ ] No billing, recovery, event-ingress, Merchant Knowledge, CommerceAgent or
  Background behaviour has been implemented.

## Validation

Run the repository-declared commands actually created by this task and record their
exact names/results in the Completion Report.

Required validation categories:

- [ ] clean npm dependency installation from lockfile;
- [ ] clean Composer dependency installation from lockfile;
- [ ] production asset build;
- [ ] JavaScript lint;
- [ ] PHP lint/static/code-standard checks provided by the repository;
- [ ] JavaScript unit tests;
- [ ] PHP unit tests;
- [ ] `git diff --check`;
- [ ] repository clean-state check;
- [ ] local `wp-env` start using the pinned WordPress/WooCommerce baseline;
- [ ] plugin activation smoke;
- [ ] Woo Admin `/moda-interact` page smoke;
- [ ] browser/DOM evidence that the React foundation rendered;
- [ ] plugin ZIP creation;
- [ ] ZIP-content audit proving required files are present and prohibited
  development/secret files are absent;
- [ ] clean installation of the generated ZIP into a clean local
  WordPress/WooCommerce environment.

The Completion Report MUST record:

```text
Node version
npm version
PHP version
Composer version
WordPress version
WooCommerce version
resolved scaffold/tool versions
generated plugin ZIP filename
```

Do not substitute static source inspection for the required install/activation/render
smoke.

If the task execution environment genuinely cannot run the required local
WordPress/WooCommerce environment, do not report the task Ready for Review as though
runtime validation passed. Record the blocker and return according to the task
protocol.

## Stop Condition

After all defined Work Items, Acceptance Criteria and required Validation are complete:

```text
update Completion Report
        ->
set task status to review
        ->
return control to moda_architect
        ->
STOP
```

Do not begin WOO-002.

Do not implement REST APIs, Moda connectivity, store identity, billing, recovery,
products, discounts or any other follow-on capability.

## Implementation Notes

Use the official WooCommerce extension scaffold as the initial implementation
baseline.

Current WooCommerce guidance uses:

```text
@wordpress/create-block
    +
@woocommerce/create-woo-extension
```

for a hybrid PHP + modern JavaScript extension.

Use WordPress/WooCommerce supplied packages/components where appropriate rather than
bundling duplicate browser frameworks unnecessarily.

Do not edit WooCommerce or WordPress core files.

Do not consume WooCommerce APIs/classes documented as internal.

Do not create a custom generic application/plugin framework in this foundation task.

The task exists to establish the smallest viable repository/runtime foundation on
which the later ARCH-026 tasks can safely build.

Normal execution MUST use the canonical `/moda-task` preparation flow once the
WOOCOMMERCE route and repository provisioning gate have been completed.

The implementation agent must execute in dedicated parent and implementation task
worktrees created/resolved by the launcher.

## Completion Report

### Status

Not Started

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

- Repository provisioning and workspace submodule registration will be completed
  before this task is promoted to Ready.
- ARCH-026-WOOCOMMERCE-002 will own explicit runtime compatibility/version-gating
  policy.
- No remote Moda service is required by this foundation task.

### Unresolved Issues

None within the implementation scope.

### Architectural Concerns

None.

## Architect Review

### Review Status

Pending

### Review Notes

Pending implementation.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending.

### Follow-up

Pending.
