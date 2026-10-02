---
id: ARCH-026-WOOCOMMERCE-002
architecture_id: ARCH-026
title: Establish the WooCommerce plugin runtime and lifecycle boundary
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 20
executor: copilot
claimed_at: 2026-10-02T13:42:53Z
attempt: 1
depends_on:
  - ARCH-026-WOOCOMMERCE-001
enables:
  - ARCH-026-WOOCOMMERCE-003
created: 2026-10-02
updated: 2026-10-02
---

# Establish the WooCommerce plugin runtime and lifecycle boundary

## Architecture

Architecture ID:

`ARCH-026`

Architecture document:

`docs/architecture/ARCH-026-woocommerce-application-foundation.md`

Coordinator:

`moda_architect`

## Objective

Turn the installable extension foundation produced by
`ARCH-026-WOOCOMMERCE-001` into a safe, explicit WordPress/WooCommerce runtime
boundary with deterministic compatibility metadata, dependency gating,
initialisation, activation and deactivation behaviour.

The completed runtime path must be:

```text
WordPress evaluates Moda Interact
        |
        v
native plugin requirements + Moda runtime guard
        |
        +---- unsupported/missing ----> Moda application remains inert
        |                              + privileged admin explanation
        |                              + no Moda-caused fatal error
        |
        v
supported WooCommerce runtime loaded
        |
        v
initialise Moda plugin runtime exactly once
        |
        v
register the WOO-001 WooCommerce Admin foundation
```

This task establishes local plugin lifecycle and compatibility behaviour only.
It MUST NOT add remote Moda connectivity, WordPress REST application endpoints,
store registration, billing, recovery/event processing or merchant business
features.

## Context

WOO-001 owns the extension scaffold, local development environment, production
asset build, installable plugin package and minimal React-powered WooCommerce
Admin page.

WOO-002 makes that foundation safe to run on merchant-controlled WordPress
infrastructure.

A WordPress plugin cannot assume that:

- WooCommerce is installed or remains active;
- WooCommerce has reached a safe public extension load boundary when the main
  plugin file is first evaluated;
- the installed WordPress/WooCommerce/PHP versions fall inside Moda's supported
  window;
- activation and deactivation happen only through the normal happy-path Admin UI;
- dependency state cannot change after Moda Interact was originally activated.

WooCommerce currently documents an L-1 compatibility policy for Woo-owned
extensions: the current and immediately previous WordPress and WooCommerce
release series, using the latest patch in each series. ARCH-026 adopts that
same narrow window for the initial Moda extension. Third-party extensions own
their own requirements, so this is an explicit Moda support decision rather
than an assumption that Woo imposes it on Moda.

For this task the compatibility window is frozen to:

```text
WordPress release series:
    minimum supported: 7.0
    tested/current:     7.1

WooCommerce release series:
    minimum supported: 11.0
    tested/current:     11.1

Moda PHP minimum:
    8.1
```

The exact patch versions used for deterministic validation are defined below.
Do not advance them during this task merely because a newer release becomes
available.

PHP 8.1 is a Moda product minimum for this new extension. It is deliberately
stricter than the minimum required by the currently pinned WooCommerce 11.0/11.1
releases and avoids establishing new Moda support on runtimes that Woo has
already announced it will leave behind in an upcoming core release.

## Scope

### 1. Canonical plugin requirement metadata

The main plugin file MUST declare, using the supported WordPress/WooCommerce
plugin header fields:

```text
Requires at least: 7.0
Tested up to: 7.1
Requires PHP: 8.1
Requires Plugins: woocommerce
WC requires at least: 11.0
WC tested up to: 11.1
```

The repository README and any WordPress plugin readme metadata introduced by
WOO-001 MUST remain consistent with these values.

Do not claim a wider support window in this task.

### 2. Deterministic compatibility matrices

Use repository-owned `wp-env` configuration to validate both ends of the
supported WordPress/WooCommerce window with controlled PHP containers.

Minimum compatibility matrix:

```text
WordPress:   7.0.6
WooCommerce: 11.0.1
PHP:         8.1
```

Current ARCH-026 compatibility matrix:

```text
WordPress:   7.1.2
WooCommerce: 11.1.2
PHP:         8.1
```

The implementation may use separate checked-in `wp-env` configuration files or
a small deterministic repository-owned wrapper around `wp-env --config`, but
the exact versions above MUST be explicit and version-controlled.

Do not require the developer host to switch between PHP versions. `wp-env`
container `phpVersion` configuration owns the compatibility runtime for these
matrix checks.

The host PHP resolved by `scripts/bootstrap-woocommerce.sh` is still required
for repository-local Composer/PHP tooling and MUST be recorded in validation
evidence, but it does not replace the controlled compatibility matrices.

### 3. Thin plugin bootstrap

Keep:

```text
moda-interact.php
```

as a thin WordPress plugin bootstrap.

It may:

- declare plugin metadata/constants;
- guard against direct file execution;
- load the Composer/package bootstrap required by the plugin;
- register bounded activation/deactivation hooks;
- register the runtime boot hook.

It MUST NOT become the implementation location for Admin screens, future REST
controllers, provider clients or business workflows.

Applicable directly executable PHP entry files MUST use the standard WordPress
direct-access guard or an equivalent established by the WOO-001 scaffold.

### 4. Runtime dependency/compatibility guard

WooCommerce is a hard dependency.

Use native WordPress plugin dependency/requirement handling where WordPress
already provides it, including:

```text
Requires Plugins: woocommerce
Requires at least
Requires PHP
```

Also retain a bounded runtime guard because dependencies/version state can be
invalid outside the ordinary activation path or can change after activation.

Before normal Moda runtime initialisation, verify at least:

```text
WooCommerce is loaded/available
WooCommerce version >= 11.0
```

Do not build a generic plugin-dependency framework.

### 5. Delayed, single-run Woo initialisation

Woo-dependent Moda code MUST initialise only after WordPress/WooCommerce have
reached a supported extension load boundary.

Introduce one clear plugin/runtime coordinator responsible for the transition:

```text
requirements satisfied
        ->
WooCommerce/public APIs available
        ->
register Moda runtime services/hooks
```

The coordinator may use the WordPress/WooCommerce hooks provided by the WOO-001
scaffold or another documented public boundary, but MUST NOT depend on plugin
filesystem ordering or Woo internal implementation classes.

Initialisation MUST be idempotent within a single request. Repeated invocation
must not duplicate the Moda Admin page, hooks or services.

Do not introduce a generic dependency-injection container solely for startup.

### 6. Missing/inactive WooCommerce behaviour

When WooCommerce is unavailable at runtime:

```text
Moda normal application initialisation:
    MUST NOT occur

Woo-dependent classes/functions:
    MUST NOT be invoked

Moda-caused PHP fatal:
    MUST NOT occur

privileged administrator feedback:
    MUST explain that WooCommerce is required
```

Do not emit this dependency notice on storefront/customer-facing requests.

Do not automatically install, activate, update or modify WooCommerce.

### 7. Unsupported WooCommerce behaviour

When the detected WooCommerce runtime is below the supported minimum series
(`11.0`):

- do not initialise the normal Moda merchant application;
- do not partially register the WOO-001 merchant page;
- do not invoke unsupported Woo APIs;
- do not fatal;
- show a bounded, localisable notice to an appropriately privileged
  administrator;
- include the detected version and Moda minimum requirement in the explanation;
- do not alter WooCommerce state.

Do not automatically deactivate Moda solely because the runtime guard is
triggered. The plugin may remain installed/active but inert so the administrator
can correct the dependency safely.

### 8. Activation lifecycle

Activation MUST remain local and bounded.

Activation MAY:

- validate Moda-owned local prerequisites not already enforced by WordPress;
- establish plugin-local lifecycle hooks required by the foundation;
- initialise a plugin schema/version marker only if WOO-001 created a concrete
  need for one.

Activation MUST NOT:

- call a Moda-hosted service;
- create a remote installation or Moda `Shop`;
- create billing state;
- enqueue Background work;
- install/activate/update WooCommerce;
- modify WooCommerce store/cart/order/customer data;
- create arbitrary options/transients merely to demonstrate persistence;
- make external network calls.

Do not instantiate the full Woo-dependent application simply because the
activation hook is running.

### 9. Deactivation lifecycle

Deactivation MUST be non-destructive and must be treated as different from
uninstall/account deletion.

Deactivation MUST NOT delete present or future:

- merchant configuration;
- Woo installation identity;
- remote Moda state;
- recovery/configuration state;
- WordPress/WooCommerce business data.

At WOO-002 there should be no such remote/business data yet. The task establishes
the lifecycle invariant for later ARCH-026 work.

Only ephemeral plugin-owned runtime resources that genuinely exist and require
cleanup may be removed on deactivation. Do not invent cron jobs, options or
transients solely to exercise deactivation handling.

### 10. Preserve the WOO-001 merchant foundation

On both supported compatibility matrices, the minimal React-powered Moda Interact
WooCommerce Admin page created by WOO-001 MUST continue to register and render.

When the runtime is missing/unsupported, the normal merchant page MUST NOT be
presented as though Moda were operational; the bounded administrative dependency
state replaces it.

### 11. Public WooCommerce APIs only

Production code MUST NOT depend on WooCommerce classes/functions explicitly
marked internal, including `Automattic\\WooCommerce\\Internal\\*`, solely to
implement lifecycle/version checks.

Use public WordPress/WooCommerce extension APIs and documented hooks.

### 12. No premature feature compatibility declarations

Do not add a new positive/negative compatibility declaration for:

```text
custom_order_tables
cart_checkout_blocks
```

solely as lifecycle scaffolding.

WOO-002 performs no order-storage or Cart/Checkout behaviour. The future task
that introduces those behaviours must inspect and validate the applicable Woo
compatibility contract before making a declaration.

## Out of Scope

- Moda-hosted Merchant API.
- Moda API credentials or installation credentials.
- Woo store -> Moda `Shop` association.
- WordPress REST application endpoints.
- PHP Moda API client.
- Moda PostgreSQL access.
- Redis/BullMQ access.
- `moda-interact-background` changes.
- Woo Marketplace SaaS billing.
- Recovery-credit purchases.
- Recovery configuration/listing.
- Cart/checkout event capture.
- Order event capture.
- Product integration.
- Coupon/discount integration.
- Merchant Knowledge.
- CommerceAgent.
- WhatsApp.
- HPOS implementation/querying.
- Cart/Checkout Blocks integration.
- Storefront UI or customer-facing scripts.
- Production merchant navigation/dashboard redesign.
- Automatic WordPress/WooCommerce/PHP upgrades.
- Automatic WooCommerce installation/activation.
- Plugin uninstall/data-erasure policy.
- Remote telemetry.
- Generic dependency/plugin framework creation.
- Refactoring unrelated WOO-001 scaffold code.

## Requirements

### R1 — Native requirements remain authoritative

Use standard WordPress/WooCommerce plugin requirement metadata for the declared
support window. Do not create a competing metadata system.

### R2 — WooCommerce is mandatory

Normal Moda WooCommerce application runtime must not initialise without an
active, supported WooCommerce runtime.

### R3 — Dependency failure is safe

Missing, inactive or unsupported WooCommerce must result in an inert Moda runtime
and bounded administrator feedback, not a Moda-caused PHP fatal or partially
functioning merchant UI.

### R4 — Woo initialisation is delayed

Woo-dependent code must not execute from top-level plugin-file evaluation before
the documented public Woo/WordPress load boundary.

### R5 — Initialisation is single-run

A single request must not register the same Moda hooks/services/page more than
once even if the boot callback is invoked repeatedly in a test or unusual plugin
lifecycle path.

### R6 — Activation has no remote/business effects

Activation performs no external network operation and creates no remote Moda,
billing, recovery or commerce-event state.

### R7 — Deactivation is non-destructive

Deactivation must not be treated as uninstall or merchant-account deletion.

### R8 — Supported matrices preserve WOO-001

The WOO-001 Admin foundation must activate and render under both deterministic
compatibility matrices.

### R9 — Support metadata and executable tests agree

The plugin must not claim a WordPress/WooCommerce/PHP support window wider than
the versions exercised or explicitly proven by this task.

### R10 — Public Woo extension APIs only

No Woo internal API dependency may be introduced to solve plugin lifecycle,
version or dependency checks.

## Work Items

- [ ] Inspect the WOO-001 scaffold/runtime entry points before changing lifecycle behaviour.
- [ ] Add/verify canonical WordPress/WooCommerce/PHP requirement headers.
- [ ] Align README/plugin readme compatibility metadata with the canonical headers.
- [ ] Add deterministic checked-in `wp-env` configurations for the minimum and current ARCH-026 compatibility matrices.
- [ ] Introduce a bounded runtime-requirements/compatibility check for conditions not safely covered by native WordPress metadata.
- [ ] Keep `moda-interact.php` as a thin lifecycle/bootstrap file.
- [ ] Add direct-access guards to applicable PHP entry files if the WOO-001 scaffold does not already provide them.
- [ ] Introduce one clear Moda plugin/runtime coordinator.
- [ ] Delay Woo-dependent initialisation until the selected documented public load boundary.
- [ ] Make runtime initialisation idempotent within one request.
- [ ] Implement safe missing/inactive WooCommerce behaviour.
- [ ] Implement safe unsupported-WooCommerce-version behaviour.
- [ ] Add privileged/localisable administrator dependency/version notices.
- [ ] Add bounded activation handling with no remote/business side effects.
- [ ] Add bounded non-destructive deactivation handling.
- [ ] Preserve WOO-001 Admin-page registration/rendering on both supported matrices.
- [ ] Add focused lifecycle/compatibility tests.
- [ ] Document the support matrix and lifecycle behaviour.
- [ ] Verify no future feature compatibility declaration was introduced prematurely.

## Interfaces / Contracts

This task creates no Moda cross-service runtime contract.

### WordPress/WooCommerce runtime compatibility contract

```text
WordPress:
    supported series: 7.0, 7.1

PHP:
    minimum: 8.1

required WordPress plugin:
    woocommerce

WooCommerce:
    supported series: 11.0, 11.1
```

### Deterministic compatibility evidence

```text
minimum matrix:
    WordPress 7.0.6
    WooCommerce 11.0.1
    PHP 8.1

current matrix:
    WordPress 7.1.2
    WooCommerce 11.1.2
    PHP 8.1
```

### Plugin runtime contract

```text
plugin evaluated
      |
      v
requirements/dependency valid?
      |
 +----+----+
 |         |
 no       yes
 |         |
 v         v
inert     wait for supported Woo load boundary
+ notice         |
                 v
             initialise once
```

No HTTP/API/queue/database contract is created.

## Dependencies

- `ARCH-026-WOOCOMMERCE-001`

WOO-001 must be architect-accepted with `status: complete` before WOO-002 may
transition from `pending` to `ready`.

## Enables

- `ARCH-026-WOOCOMMERCE-003`

WOO-003 remains a future ARCH-026 task and must not begin merely because WOO-002
has been defined. It becomes eligible only after it is materialised and all of
its actual dependencies are Complete.

## Acceptance Criteria

- [ ] Main plugin metadata declares `Requires at least: 7.0`.
- [ ] Main plugin metadata declares `Tested up to: 7.1`.
- [ ] Main plugin metadata declares `Requires PHP: 8.1`.
- [ ] Main plugin metadata declares `Requires Plugins: woocommerce`.
- [ ] Woo metadata declares `WC requires at least: 11.0`.
- [ ] Woo metadata declares `WC tested up to: 11.1`.
- [ ] Checked-in compatibility configuration pins WordPress 7.0.6 + WooCommerce 11.0.1 + PHP 8.1.
- [ ] Checked-in compatibility configuration pins WordPress 7.1.2 + WooCommerce 11.1.2 + PHP 8.1.
- [ ] The plugin activates and the WOO-001 Moda Admin foundation renders on both compatibility matrices.
- [ ] Native WordPress plugin requirements remain in use for WordPress/PHP/plugin dependency validation.
- [ ] Missing/inactive WooCommerce cannot cause a Moda PHP fatal.
- [ ] WooCommerce below 11.0 does not initialise the normal Moda application runtime.
- [ ] Unsupported dependency/version state produces a bounded notice only for an appropriately privileged administrator.
- [ ] Dependency/version notices do not leak into storefront/customer-facing output.
- [ ] Woo-dependent code is not invoked before the selected public load boundary.
- [ ] Runtime initialisation occurs at most once per request.
- [ ] Activation makes no external network request and creates no remote/business state.
- [ ] Deactivation is non-destructive.
- [ ] React/Woo Admin foundation remains functional after deactivate/reactivate on a supported runtime.
- [ ] Production code contains no dependency on `Automattic\\WooCommerce\\Internal\\*` or another Woo API explicitly marked internal for lifecycle/version handling.
- [ ] No HPOS or Cart/Checkout compatibility declaration was added without a corresponding feature implementation/validation.
- [ ] No Moda remote API, billing, recovery, event-ingress, product, discount, Merchant Knowledge or Background capability was introduced.

## Validation

Before the first Node, PHP, Composer, Docker or `wp-env` command in the attempt,
source exactly once for the shell:

```bash
source "$MODA_WORKSPACE_ROOT/scripts/bootstrap-woocommerce.sh"
```

Record the resolved host Node/npm/PHP/Composer/Docker versions in the Completion
Report.

Then run the repository-declared validation commands actually established by
WOO-001/WOO-002 and record their exact command lines/results.

Required validation categories:

- [ ] clean npm dependency installation from lockfile;
- [ ] clean Composer dependency installation from lockfile;
- [ ] production asset build;
- [ ] JavaScript lint/tests where affected;
- [ ] PHP lint/code-standard/static checks declared by the repository;
- [ ] focused PHP runtime/lifecycle tests;
- [ ] plugin-header requirement assertions;
- [ ] missing/inactive-Woo runtime test;
- [ ] unsupported-Woo-version runtime test;
- [ ] privileged-admin notice test;
- [ ] storefront no-notice test;
- [ ] duplicate runtime-initialisation test;
- [ ] activation no-network-side-effect test;
- [ ] deactivation non-destructive test;
- [ ] minimum `wp-env` compatibility matrix: WordPress 7.0.6 + WooCommerce 11.0.1 + PHP 8.1;
- [ ] current `wp-env` compatibility matrix: WordPress 7.1.2 + WooCommerce 11.1.2 + PHP 8.1;
- [ ] plugin activation smoke on each supported matrix;
- [ ] Woo Admin `/moda-interact` render smoke on each supported matrix;
- [ ] deactivate/reactivate smoke on a supported matrix;
- [ ] source scan proving no new `Automattic\\WooCommerce\\Internal\\` dependency;
- [ ] source/config scan proving no HPOS/Cart-Checkout compatibility declaration was introduced by this task;
- [ ] `git diff --check`;
- [ ] implementation worktree clean after commit/push;
- [ ] implementation task branch matches its remote task branch.

If the task's controlled compatibility matrix cannot run because Docker/`wp-env`
or another required prepared prerequisite is unavailable, do not substitute a
host-only smoke and do not report Ready for Review. Record the exact blocker and
return according to the task protocol.

The Completion Report MUST record:

```text
host bootstrap:
    Node version
    npm version
    PHP version
    Composer version
    Docker client version

controlled compatibility matrices:
    WordPress version
    WooCommerce version
    PHP container version
```

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are
complete:

```text
finish Completion Report
        ->
set task status to review
        ->
return control to moda_architect
        ->
STOP
```

Do not begin WOO-003.

Do not implement remote Moda connectivity or any merchant business feature.

## Implementation Notes

Prefer native WordPress dependency/requirement semantics over bespoke runtime
machinery. The additional Moda guard exists only to keep the plugin safe when
runtime state no longer matches the normal activation path or when WooCommerce
is below the supported series.

Use `wp-env`'s version-controlled `core`/plugin and `phpVersion` support for the
compatibility matrices. Do not ask the developer host to switch PHP versions to
simulate the minimum runtime.

The WOO-001 toolchain bootstrap remains the required host prerequisite gate; it
must not install or silently select PHP, Composer, Docker or Node.

Do not add compatibility shims for WordPress/WooCommerce versions outside the
specified ARCH-026 window.

Do not create persistent data simply to prove activation/deactivation behaviour.

Do not reimplement the WOO-001 Admin page. Preserve it behind the new runtime
boundary.

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

- WOO-001 will provide the canonical plugin scaffold, dependency lockfiles,
  local build/test commands and minimal Woo Admin page before this task becomes
  Ready.
- `wp-env` supports controlled PHP-version selection for the required
  compatibility matrices.
- ARCH-026 intentionally adopts an L-1 WordPress/WooCommerce support window for
  its initial Woo extension.

### Unresolved Issues

None.

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
