---
id: ARCH-026-WOOCOMMERCE-006
architecture_id: ARCH-026
title: Harden production WooCommerce packaging and upgrade lifecycle
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 60
executor: null
claimed_at: null
attempt: 2
depends_on:
  - ARCH-026-WOOCOMMERCE-005
  - ARCH-026-GATEWAY-001
enables: []
created: 2026-10-02
updated: 2026-10-08
---

# Harden production WooCommerce packaging and upgrade lifecycle

## Architecture

Architecture ID:

`ARCH-026`

Architecture document:

`docs/architecture/ARCH-026-woocommerce-application-foundation.md`

Coordinator:

`moda_architect`

## Objective

Turn the accepted ARCH-026 WooCommerce application into a production-distribution candidate whose generated `moda-interact.zip` is self-contained, secret-safe, internationalization-ready and safe to install, upgrade, deactivate and reactivate on a merchant WordPress/WooCommerce site without requiring Node, npm, Composer or a development server on that merchant host.

The completed release path is:

```text
clean moda-interact-woocommerce checkout
        |
        | repository-owned production package command
        v
moda-interact.zip
        |
        +-- moda-interact.php
        +-- production PHP/autoload runtime
        +-- includes/
        +-- build/
        +-- languages/
        +-- WordPress readme/release documentation
        `-- no development/runtime secrets
        |
        v
clean WordPress + WooCommerce
        |
        +-- fresh install/activate
        |
        `-- upgrade from accepted WOO-005 baseline
                |
                +-- preserve local connection state
                +-- preserve non-destructive lifecycle semantics
                `-- render accepted Woo Admin application
```

This task owns release-artifact hardening and the local WordPress install/upgrade lifecycle only. It MUST NOT add billing, onboarding completion, recovery processing, commerce-event ingress, product/coupon integration, Merchant Knowledge, CommerceAgent behavior or another hosted Moda service.

## Context

WOO-001 already proved that the repository can produce an installable ZIP with the correct `moda-interact/` root, local compiled assets and the Composer autoloader. It also established an explicit package allowlist after discovering that a naive npm packlist omitted the required production `vendor/autoload.php`.

WOO-002 established native WordPress/WooCommerce/PHP requirements plus non-destructive activation/deactivation behavior.

WOO-003 owns the server-side Moda connection record and long-lived installation credential. Deactivation does not delete that record.

WOO-004/WOO-005 establish the real React Admin shell, connection experience and first authenticated merchant Overview.

GATEWAY-001 establishes the canonical production hosted API ingress:

```text
https://api.modainteract.com
```

with the API service private behind the public Gateway. WOO-006 is therefore the point where the distributable plugin may acquire that canonical production API origin as its server-side default. Development/test overrides remain server-side only and must continue to use the accepted WOO-003 configuration boundary.

ARCH-026 internationalization is first-class. The release artifact must retain the `moda-interact` text domain, package its translation template/assets correctly and MUST NOT introduce a fixed Woo/WordPress locale allowlist.

ARCH-026 remains pre-production. This task hardens the first distribution candidate; it does not need to preserve an older public Marketplace release contract. It must, however, prove upgrade safety from the architect-accepted WOO-005 implementation because merchant-local connection state already exists by that point in the architecture.

## Scope

Modify only `moda-interact-woocommerce` files required for production package construction, version/release metadata, production API-origin defaulting, translation/readme assets and focused packaging/install/upgrade validation.

Expected implementation areas may include:

```text
moda-interact.php
package.json
package-lock.json
composer.json
composer.lock
.distignore / package allowlist
README.md
readme.txt
CHANGELOG.md
languages/
includes/Api/ModaApiConfiguration.php   # or accepted WOO-003 owner
scripts/ or repository-local packaging helpers
package-focused tests
```

Exact filenames may follow the accepted WOO-005 repository structure.

### Production API origin

The distributable plugin MUST have one canonical server-side production default:

```text
https://api.modainteract.com
```

Requirements:

- the default is owned by the PHP/server-side WOO-003 API configuration boundary;
- browser JavaScript cannot choose or override it;
- the raw installation credential remains PHP/server-side;
- the accepted explicit local-development/test override mechanism remains available without weakening production HTTPS validation;
- local-development mode is disabled by default in the packaged runtime and requires deliberate server-side developer configuration;
- no production runtime path defaults to `api-test.modainteract.com`, localhost, wp-env ports or a test fixture origin;
- the built browser JS bundle must not contain the production API origin because browser code does not call the hosted API directly.

Do not add the API base URL as an editable WordPress merchant setting merely to make packaging convenient.

### Package identity and version consistency

Preserve the current ARCH-026 package version unless an explicit architect/developer release version has been chosen before execution. Do not invent a version bump merely for this task.

Whatever version is packaged must be consistent across all applicable release surfaces, including at minimum:

```text
WordPress plugin Version header
package.json
package-lock.json root package metadata
CHANGELOG.md current release heading
```

If a runtime version constant/cache-busting version is present or introduced, it must use the same value rather than establishing another independently maintained version source.

The installed plugin directory and primary file remain:

```text
moda-interact/
moda-interact/moda-interact.php
```

Do not rename the plugin slug, text domain or PHP namespace.

### Canonical packaging command

Provide one repository-owned production packaging command that can run from a clean checkout after the normal locked dependency installation and build steps.

The command MUST:

1. build production browser assets;
2. materialize the production Composer autoloader/runtime without development-only Composer packages;
3. create `moda-interact.zip` with the single root folder `moda-interact/`;
4. leave tracked repository files unchanged;
5. fail if required runtime files are missing;
6. fail if prohibited development/secret material would enter the archive.

Reusing `wp-scripts plugin-zip` and the existing explicit `package.json.files` allowlist is preferred unless the accepted repository state demonstrates a concrete gap. Do not replace the standard packager with a bespoke archive framework merely for stylistic reasons.

If packaging temporarily changes generated/untracked `vendor/` content from development to production dependencies, validation must restore/verify the normal development environment before running the remainder of repository tests. A staging-directory implementation is allowed when it reduces mutation, but is not required if the final behavior is deterministic and clean.

### Required runtime package contents

The final archive must include every file required to execute the accepted WOO-005 application without developer tooling, including at minimum where present:

```text
moda-interact.php
includes/
build/
production Composer autoload files under vendor/
languages/
readme.txt
README.md and CHANGELOG.md when retained by the canonical package allowlist
```

The package must contain the built WordPress dependency metadata generated by the accepted JS build (for example `*.asset.php`) where the application requires it.

Do not require Composer, Node/npm, wp-env or source compilation on the merchant server after ZIP installation.

### Prohibited package contents

The distribution artifact MUST NOT contain development-only or sensitive material, including:

```text
.git/
.github/
node_modules/
src/
tests/
phpunit.xml*
.wp-env*.json
local Docker/wp-env state
.env*
editor/workspace files
coverage output
logs
caches
__pycache__/
.DS_Store
package manager caches
vendor/bin/
PHPUnit or another Composer require-dev package
real credentials/tokens/secrets
local/test fixture certificates or private keys
```

Package manifests/lockfiles may remain excluded when they are not runtime requirements. Runtime PHP autoload metadata required by `moda-interact.php` must remain included.

Reject accidental JavaScript source maps unless the architecture explicitly records a reason to distribute them. Normal production packaging should contain minified/built runtime assets rather than developer source artifacts.

### Internationalization release assets

Correct any scaffold-residue translation metadata before distribution.

The canonical translation domain is:

```text
moda-interact
```

The release must provide/update a translation template named consistently for Moda, for example:

```text
languages/moda-interact.pot
```

using WordPress-compatible extraction tooling over the merchant-visible PHP/JavaScript source.

The template/project metadata and extracted strings must identify Moda Interact rather than the original Woo scaffold/template project.

Do not enumerate a fixed set of supported Woo locales in package code, metadata or validation. Translation coverage may be incomplete; valid WordPress/WooCommerce locale identity must still remain supported structurally.

Any JavaScript translation metadata required by `wp_set_script_translations`/the accepted Woo Admin build must remain present in the artifact.

### Standard WordPress readme and external-service disclosure

Add/maintain a standard WordPress plugin `readme.txt` suitable for an installable extension artifact.

It must accurately describe only capabilities that exist by WOO-005 and must not advertise billing, recoveries or other future functionality as implemented.

Because the plugin connects to the external Moda hosted service, the packaged documentation must clearly disclose that server-to-server connection and the bounded categories of information currently sent by the accepted ARCH-026 implementation, such as site/installation identity and authenticated merchant bootstrap requests.

Do not invent a privacy-policy, terms URL or legal claim that is not supplied/owned by the developer. Marketplace-submission copy, screenshots, pricing and legal-policy publication remain outside this task.

### Fresh-install smoke

Using the canonical supported/current local Woo test matrix established by WOO-002, install the generated ZIP into a clean WordPress/WooCommerce instance where Moda is absent.

Prove at minimum:

```text
ZIP installs successfully
plugin activates successfully
Woo dependency/runtime gates remain correct
WooCommerce -> Moda Interact page loads from packaged local assets
no Node/npm/Composer service is required by the installed site
no outbound Moda connection is initiated merely by install/activation
```

The UI may report its real disconnected/configuration state according to accepted WOO-004 behavior; do not fabricate a connection solely for the smoke.

### Upgrade baseline

Use the architect-accepted WOO-005 implementation commit as the upgrade baseline.

Create/install a baseline package from that exact accepted implementation rather than reconstructing a hypothetical old plugin by deleting current files.

Record the WOO-005 implementation commit SHA used for the upgrade rehearsal.

Before upgrading, establish a deterministic **fake/test-only** local WOO-003 connection option matching the accepted schema, including a clearly non-production installation ID, Shop ID, canonical site URL, credential version and synthetic high-entropy credential.

The fixture MUST NOT contain any real Moda credential.

Record the logical fixture before upgrade.

### Upgrade behavior

Upgrade the installed WOO-005 baseline plugin in place using the new WOO-006 candidate ZIP through a normal WordPress/WP-CLI plugin ZIP update/replacement path.

The upgrade must prove:

- the plugin remains installed under `moda-interact/`;
- activation state is preserved or restored through the documented update command;
- the WOO-003 local connection option remains logically unchanged;
- no automatic reconnect/credential rotation occurs merely because code was upgraded;
- no onboarding, billing, entitlement or merchant business state is reset;
- the accepted WOO-005 Admin application still renders from the candidate package;
- no package installation step requires Node/npm/Composer on the WordPress runtime;
- no outbound Moda API request is required to complete the file upgrade itself.

If WordPress invokes plugin lifecycle hooks during the chosen update path, those hooks must preserve the accepted WOO-002/WOO-003 non-destructive semantics.

### Deactivate/reactivate behavior

From the upgraded candidate:

```text
deactivate Moda Interact
        -> verify local connection option retained
reactivate Moda Interact
        -> verify same local connection option retained
```

Do not introduce uninstall/data-erasure behavior in this task.

### Package safety scan

Perform a deterministic archive-content scan and a bounded source/runtime string scan.

At minimum verify:

- package root is exactly `moda-interact/`;
- expected runtime files exist;
- prohibited paths/files are absent;
- no real secrets/tokens are present;
- no local/test API origin is present in packaged runtime PHP/JS;
- `https://api.modainteract.com` is present only where expected in PHP/server-side runtime/configuration and not in built browser JS;
- scaffold-residue package/translation identity is not present in merchant-facing runtime/translation metadata;
- no executable JS/CSS/font asset is remotely loaded merely to render the Admin application.

Do not scan dependency minified code with an unbounded generic secret heuristic that makes the validation non-deterministic. Keep package safety assertions targeted to the architecture-defined risks.

## Out of Scope

- Woo Marketplace submission/review itself.
- Marketplace billing or SaaS Billing API.
- Pricing/subscriptions/top-ups.
- Merchant onboarding completion commands.
- Store Category mutations.
- Recovery/event/background integration.
- Merchant Knowledge.
- Product/coupon/discount APIs.
- CommerceAgent/WhatsApp.
- Installation uninstall/data-erasure policy.
- Site/domain migration.
- WordPress.org publication.
- Automatic plugin update server/licensing infrastructure.
- Code signing/notarization not required by the selected Woo distribution channel.
- Real production merchant credentials in validation.
- New compatibility declarations unrelated to functionality implemented by ARCH-026.
- A custom package manager or installer.

## Requirements

### R1 — Self-contained merchant artifact

`moda-interact.zip` contains everything required to run the accepted WOO-005 PHP + React application on a supported WordPress/WooCommerce host without Node/npm/Composer on that host.

### R2 — Stable package identity

The archive root, plugin slug, main file, text domain and PHP namespace remain the accepted Moda identities and are suitable for an in-place WordPress plugin update.

### R3 — Production API origin is server-side

The packaged PHP runtime defaults to `https://api.modainteract.com`; browser bundles do not contain/use the remote Moda API origin or credential.

### R4 — No development/secret leakage

The archive contains no prohibited development files, test secrets, real credentials, local environment state or Composer development executables/packages.

### R5 — Internationalization-ready package

Merchant-visible PHP/JS strings remain WordPress-translatable under `moda-interact`, the packaged translation template carries Moda identity, and no fixed Woo locale allowlist is introduced.

### R6 — Fresh install remains valid

A clean supported WordPress/WooCommerce environment can install, activate and render the packaged plugin without a developer build environment.

### R7 — Upgrade preserves local connection state

An in-place update from the accepted WOO-005 baseline to the WOO-006 candidate retains the exact logical WOO-003 connection state and does not automatically reconnect or rotate credentials.

### R8 — Deactivation remains non-destructive

Deactivation/reactivation after upgrade leaves the WOO-003 connection record intact.

### R9 — Packaging itself has no business side effect

Install/update/deactivate/reactivate does not complete onboarding, activate billing, mutate merchant business state or require a hosted Moda API write.

### R10 — Package command is reproducible and clean

The repository-owned package command succeeds from a clean checkout with locked dependencies and leaves tracked source unchanged.

### R11 — External service is documented accurately

The packaged WordPress readme discloses the current Moda hosted-service dependency without advertising unimplemented capabilities or inventing legal-policy URLs.

### R12 — WOO-001 packaging regressions stay fixed

The final package retains the required Composer autoloader/runtime while excluding `vendor/bin`, Composer development packages and other WOO-001-discovered packaging hazards.

## Work Items

- [x] Freeze the canonical server-side production API default to `https://api.modainteract.com` while retaining accepted explicit local-development/test injection with the bypass disabled by default.
- [x] Reconcile package/release version metadata so all package surfaces use one current version.
- [x] Harden the canonical production packaging command/allowlist around accepted WOO-005 runtime files.
- [x] Ensure production Composer autoload/runtime is included without Composer development packages or `vendor/bin`.
- [x] Add/update a standard WordPress `readme.txt` describing only implemented capability and the external Moda service dependency.
- [x] Replace/update scaffold-residue translation template metadata with the `moda-interact` translation template.
- [x] Add deterministic package manifest/safety validation for required and prohibited contents.
- [x] Add targeted validation proving local/test API origins and secrets cannot enter packaged runtime/browser assets.
- [x] Build the WOO-006 candidate ZIP from a clean task worktree.
- [x] Perform clean supported-environment ZIP install/activation/Admin-render smoke.
- [x] Build/install the exact architect-accepted WOO-005 baseline package and record its implementation SHA.
- [x] Establish a synthetic non-production WOO-003 connection-option fixture on the baseline installation.
- [x] Upgrade that installation in place to the WOO-006 candidate ZIP.
- [x] Prove the connection option and merchant lifecycle state are preserved and no automatic reconnect occurs.
- [x] Prove post-upgrade deactivate/reactivate preserves the connection option.
- [x] Restore/verify development dependencies after packaging where the packaging command temporarily materializes production-only Composer state.
- [x] Document artifact creation, package manifest, upgrade rehearsal and local validation in the Completion Report.

## Interfaces / Contracts

### Plugin artifact

```text
moda-interact.zip
    `-- moda-interact/
        `-- moda-interact.php
```

### Production hosted API origin

```text
https://api.modainteract.com
```

Owner of public routing:

`ARCH-026-GATEWAY-001`

Consumer/config owner:

`ARCH-026-WOOCOMMERCE-003` configuration boundary, hardened by this task for distribution.

### Local connection-state contract

Owner:

`ARCH-026-WOOCOMMERCE-003`

WOO-006 MUST preserve that accepted non-autoloaded option schema and must not reinterpret the raw credential as browser/application configuration.

### Merchant UI contract

Owner:

`ARCH-026-WOOCOMMERCE-004` / `ARCH-026-WOOCOMMERCE-005`

WOO-006 packages the accepted application; it does not redefine merchant-data contracts.

### Translation identity

```text
text domain: moda-interact
translation template: languages/moda-interact.pot
```

Locale support remains open-ended according to WordPress/WooCommerce locale identity; translation coverage is not an allowlist.

## Dependencies

- `ARCH-026-WOOCOMMERCE-005`
- `ARCH-026-GATEWAY-001`

Both tasks must be architect-accepted `complete` before WOO-006 becomes Ready.

WOO-006 uses the exact architect-accepted WOO-005 implementation commit as the upgrade baseline and the canonical production API host established by accepted GATEWAY-001.

## Enables

None currently materialised.

A later terminal ARCH-026 system-test task may depend on WOO-006 together with the complete API/database/gateway implementation set. WOO-006 must not begin that system-test work itself.

## Acceptance Criteria

- [x] One repository-owned command builds the production `moda-interact.zip` from a clean checkout with locked dependencies.
- [x] Packaging leaves tracked repository files unchanged.
- [x] ZIP root is exactly `moda-interact/` and main plugin file is `moda-interact/moda-interact.php`.
- [x] Package version metadata is consistent across plugin header, npm package metadata/lockfile and current changelog entry.
- [x] Package contains all accepted PHP runtime, built JS/CSS/dependency metadata, production Composer autoload files and translation/readme assets required by WOO-005.
- [x] Package excludes `node_modules`, source/test/development environment files, `vendor/bin`, Composer development packages, source maps, caches/logs and real credentials/secrets.
- [x] Packaged production PHP defaults to `https://api.modainteract.com` through the accepted server-side configuration owner.
- [x] Built browser JS contains no production/test Moda API origin and no installation credential/bootstrap secret.
- [x] Packaged runtime contains no localhost/wp-env/test API origin as a production default and does not enable local-development connection mode unless a server-side developer explicitly opts in.
- [x] `languages/moda-interact.pot` reflects Moda Interact/text-domain identity and merchant-visible strings; scaffold translation identity is removed from the package.
- [x] No fixed WordPress/WooCommerce locale allowlist is introduced.
- [x] Standard packaged `readme.txt` accurately discloses the current external Moda hosted-service dependency and does not advertise unimplemented features.
- [x] Clean supported WordPress/WooCommerce environment installs and activates the candidate ZIP successfully.
- [x] Packaged Woo Admin application renders from local plugin assets without Node/npm/Composer on the WordPress runtime.
- [x] Install/activation itself performs no automatic Moda connection/reconnect or business-state mutation.
- [x] Upgrade baseline is built from the exact architect-accepted WOO-005 implementation commit and that SHA is recorded.
- [x] In-place upgrade to the candidate ZIP preserves the synthetic WOO-003 connection option exactly in logical content.
- [x] Upgrade does not automatically rotate/reconnect the installation credential or reset onboarding/billing/entitlement state.
- [x] Candidate remains usable/renderable after upgrade.
- [x] Deactivate/reactivate after upgrade preserves the same connection option.
- [x] No billing, recovery, Merchant Knowledge, product/discount, commerce-event or Background functionality is introduced.

## Validation

Run the Woo repository's declared validation commands and record exact commands/results.

Required validation categories:

- [x] required `scripts/bootstrap-woocommerce.sh` toolchain bootstrap succeeds before repository validation;
- [x] clean npm install from lockfile (`npm ci`);
- [x] clean Composer development install from lockfile (`composer install --no-interaction`);
- [x] production build (`npm run build`, run by `npm run package:production`);
- [x] PHP lint (`composer lint`); no separate code-standard/static-analysis script is declared in `composer.json`;
- [x] JavaScript lint/tests (`npm run lint:js`, `npm run test:js`);
- [x] PHP tests (`composer test`);
- [x] translation-template generation/validation for `moda-interact` (`npm run i18n:makepot`, package identity audit);
- [x] package version-consistency check (production package audit);
- [x] production package command succeeds (`npm run package:production`);
- [x] `unzip -t moda-interact.zip` succeeds;
- [x] deterministic archive manifest audit for required/prohibited paths (33 entries; production package audit);
- [x] Composer production-runtime audit proving required autoload files are present and require-dev packages/`vendor/bin` are absent;
- [x] targeted packaged-runtime secret/API-origin scan;
- [x] clean current supported WordPress/WooCommerce ZIP install + activation smoke;
- [x] packaged `/moda-interact` Admin render smoke from local assets;
- [x] network fixture/assertion proving install/activation does not require a Moda API request;
- [x] accepted WOO-005 baseline package build from its recorded implementation SHA;
- [x] baseline install/activation with deterministic synthetic WOO-003 connection-option fixture;
- [x] in-place candidate ZIP update/upgrade smoke;
- [x] pre/post-upgrade logical connection-option equality assertion;
- [x] post-upgrade Admin render smoke;
- [x] post-upgrade deactivate/reactivate smoke with connection-option preservation;
- [x] restore/verify development dependency state after production package creation (`composer install`; PHPUnit present);
- [x] `git diff --check`;
- [x] implementation worktree clean-state evidence recorded after commit/push.

The Completion Report MUST record:

```text
candidate plugin version
candidate ZIP filename
candidate ZIP SHA-256
candidate archive manifest summary
WordPress/WooCommerce/PHP versions used
accepted WOO-005 baseline implementation SHA
baseline package version
connection-option preservation evidence
production API default evidence
```

Do not use a real merchant installation credential or production merchant site in packaging/upgrade validation.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete:

```text
finish Completion Report
        ->
set status: review
        ->
return control to moda_architect
        ->
STOP
```

Do not begin Marketplace submission, billing work or terminal system testing.

## Implementation Notes

Preserve the standard WordPress/WooCommerce package shape rather than inventing a custom installer.

`@wordpress/scripts` provides `plugin-zip` specifically for WordPress plugin ZIP construction and honors the package file allowlist. Continue using that standard path unless the accepted repository proves it cannot satisfy one of this task's explicit requirements.

WooCommerce extensions are ordinary WordPress plugins. The distribution artifact should follow WordPress/Woo extension conventions, include a standard plugin readme, use the matching `moda-interact` text domain, and keep executable application assets local to the plugin. The intentional external request boundary is the documented server-to-server Moda hosted API connection.

The synthetic upgrade fixture exists only to prove local data preservation. Do not treat its fake credential as a valid remote principal and do not weaken API authentication to make the upgrade smoke pass.

Do not turn this packaging task into Marketplace marketing/legal submission work. When a policy URL or merchant-facing legal statement is not supplied by the developer, leave that publication work for the appropriate later release process rather than inventing it.

## Completion Report

### Status

Ready for Review

### Files Changed

- `.distignore`, `README.md`, `includes/Api/ModaApiConfiguration.php`, `includes/Runtime.php`, `package.json`, `package-lock.json`, `readme.txt`.
- Replaced `languages/woo-plugin-setup.pot` with generated `languages/moda-interact.pot`.
- Added `scripts/package-production.mjs` and `scripts/make-pot.mjs`.
- Added `tests/integration/run-package-lifecycle.mjs`.
- Updated `tests/ModaApiConfigurationTest.php` and `tests/ConnectionControllerTest.php`.

### Work Completed

- The server-side API configuration now defaults to `https://api.modainteract.com`; explicit local-development injection remains available. A regression test proves the default, and the package audit proves the origin exists only in PHP configuration, not browser assets.
- Kept release version `0.1.0` consistent across `package.json`, lockfile root, plugin header, changelog and `readme.txt`.
- Added the canonical `npm run package:production` command. It builds the React assets, materializes production-only Composer runtime, uses `wp-scripts plugin-zip`, checks tracked diff stability, and audits version identity, required/prohibited entries, Composer contents, translation/readme identity, bounded secret/API-origin/executable-asset patterns, and ZIP integrity.
- Added the WordPress readme with current WOO-005 capability scope and explicit server-to-server Moda service/data disclosure. Generated the Moda-owned POT; added translator context for the WooCommerce version placeholders.
- A1-R1: POT generation now pins the `moda-interact` slug/package identity and explicitly empties `Report-Msgid-Bugs-To`; the production archive audit requires that empty header and rejects numeric `ARCH-` task IDs of any width. Regeneration from the task-named wp-env mount retained `X-Domain: moda-interact` and emitted no internal task identifier.
- Final artifact: `moda-interact.zip`, version `0.1.0`, SHA-256 `276327aa22fa5bf4ef9e1b9054a52bc16de2040a0b6f571a916b633ff5350286`, 33 entries. It includes the plugin entrypoint, 13 PHP runtime files, compiled JS/CSS plus asset metadata, Composer production autoload/runtime, `languages/moda-interact.pot`, `readme.txt`, README and changelog. Archive root is only `moda-interact/`.
- The production archive audit found no development/test/source-map/cache paths, `vendor/bin`, Composer development packages, local/test API origin, private key or recognized secret. Built browser JavaScript contains neither the Moda API origin nor credential/bootstrap material. `unzip -t` passed.
- Rehearsed fresh install and accepted-baseline upgrade in isolated WordPress 7.1.2 / WooCommerce 11.1.2 / container PHP 8.1 environments using WP-CLI ZIP install/force-replacement. Both installs activated at `moda-interact/moda-interact.php`; packaged `/moda-interact` rendered its local JS/CSS in Woo Admin.
- Built the upgrade baseline from exact accepted WOO-005 implementation commit `98273e4ebdfa9a78146cb897fb905ef97a6814e7`; baseline package version is `0.1.0`. Seeded the exact WOO-003 connection option with a synthetic fixture only: installation `install_w006_synthetic_upgrade_fixture`, shop `shop_w006_synthetic_upgrade_fixture`, site `https://merchant-w006-fixture.invalid`, credential version `7`, and synthetic credential SHA-256 `cb475c4e3ce8a4ed49c22558ab5ea137ba7ef3c24b21ff4bae6de6569285fad9`.
- The fixture option compared equal before/after candidate upgrade and after deactivate/reactivate. The test network guard observed no Moda API request during either install/activation, the file update, or deactivate/reactivate. Browser runtime made no direct request to `api.modainteract.com`.
- Restored Composer development dependencies after the final package build; PHPUnit is present in the development install and absent from the ZIP.

### Validation Results

- `source "$MODA_WORKSPACE_ROOT/scripts/bootstrap-woocommerce.sh"`: passed; Node 24.19.0/npm 11.17.0, PHP 8.5.11, Composer 2.10.3, Docker 29.7.2 with daemon available.
- `npm ci`: passed from the updated lockfile.
- `composer install --no-interaction`: passed from lockfile; 27 development packages installed/restored.
- `npm run lint:js`: passed (repository emitted its existing legacy ESLint-config warning).
- `npm run test:js`: passed, 6 test files / 47 tests.
- `npm run lint:css`: passed.
- `composer test`: passed, 33 tests / 152 assertions.
- `composer lint`: passed for all declared PHP files.
- `npm run i18n:makepot`: passed; generated `languages/moda-interact.pot` with Moda domain identity and translator placeholder comment.
- `npm run package:production`: passed after POT regeneration and audit broadening; version/manifest/Composer/runtime safety checks passed. Final ZIP has 33 entries and SHA-256 `276327aa22fa5bf4ef9e1b9054a52bc16de2040a0b6f571a916b633ff5350286`.
- Packaged POT inspection: `Report-Msgid-Bugs-To` is empty, `X-Domain` is `moda-interact`, and no `ARCH-[0-9]+` task identifier is present; ZIP integrity check passed.
- `unzip -tq moda-interact.zip`: passed; no compressed-data errors.
- `npm run test:integration:package-lifecycle`: passed for the final artifact. Fresh install and activation, local Admin render, exact WOO-005 baseline package install, synthetic fixture preservation over in-place upgrade, post-upgrade Admin render, deactivation/reactivation preservation and zero install/update/lifecycle Moda API requests all passed.
- `node --check` for `scripts/package-production.mjs`, `scripts/make-pot.mjs` and `tests/integration/run-package-lifecycle.mjs`: passed.
- `git diff --check`: passed.
- No PHP code-standard or static-analysis script is declared in this repository's `composer.json`; declared PHP lint/tests were run. npm install reported 47 dependency audit findings and existing peer/install-script warnings; no dependency upgrade/remediation was in scope.

### Attempt 2 Review Corrections and VCS Provenance

- Launcher preparation on 2026-10-08 claimed Attempt 2 (`copilot`) after the task was Ready; the claim was committed and pushed as parent task commit `329d705dc82823fa57bb994660038b62dbfcf9c6`. Dependency gate passed for WOO-005 and GATEWAY-001.
- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`. Dedicated parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-026-WOOCOMMERCE-006`, branch `task/ARCH-026-WOOCOMMERCE-006`; launcher reused it, remote task fast-forward was not needed, `origin/main` was incorporated, and its pre-claim head was `77ed8eed3e7a93bfee4c4103736f9e2eb3b49626`.
- Dedicated implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-026-WOOCOMMERCE-006`, branch `task/ARCH-026-WOOCOMMERCE-006`; launcher reused it, remote task fast-forward was not needed, `origin/main` was already current, and its start-of-attempt head was `c6a17eedefee34f6c4c0f538017363fe9de7135a`.
- Recursive submodule preparation passed (`git submodule sync --recursive` and `git submodule update --init --recursive`); launcher reported status `ready`, recursive `true`, and no submodule entries.
- Attempt 2 POT correction commits: `7388b420d18c57c55f3f8d2ab29faff3f40751e4` (stable generator metadata) and `02aabc0219fb8a2815d52c8dcac5d9e8d501b7a1` (identifier audit plus regenerated POT); both were pushed to the implementation task branch. The attempt-1 parent report revision was `e22ba8fb1046d51264954ea2f25aaeaef4ec4a90`; the current Completion Report is committed and pushed on the same parent task branch. Post-publication verification confirmed matching remote task branches and clean worktrees.
- No task work was performed in the shared implementation checkout, no main branch was changed, and no submodule gitlink was updated.

### Deviations

- The lifecycle runner creates a temporary isolated wp-env project and repository-local Docker-shared staging mount, uses a test-only MU plugin to serve staged ZIP bytes through WordPress's HTTP API and establish an ephemeral admin render session, and deletes both after the run. This preserves the normal WP-CLI ZIP install/update path without external package downloads or persistent test fixtures.
- WordPress/WooCommerce emitted a WooCommerce textdomain timing notice during wp-env startup; lifecycle assertions passed and no Moda source change was implicated.

### Assumptions

- WOO-005 provides the complete merchant-facing functionality intended for the ARCH-026 foundation distribution candidate.
- GATEWAY-001 establishes `https://api.modainteract.com` as the canonical production API ingress.
- WOO-003 connection state remains server-side/non-autoloaded and survives normal plugin deactivation.
- No public/Marketplace Moda plugin version predates this ARCH-026 development initiative, so no external backwards-compatibility adapter is required.

### Unresolved Issues

- npm reports 47 dependency audit findings in the existing development dependency tree; remediation is outside this bounded packaging task.

### Architectural Concerns

None.

## Architect Review

### Review Status

Accepted — Attempt 2 (2026-10-08).

### Review Notes

`ARCH-026-WOOCOMMERCE-006` Attempt 2 is **Accepted**. The two bounded Attempt 1 corrections are closed without broadening the packaging task or changing the accepted Woo-005 merchant application, WOO-003 connection-state contract or canonical Gateway API origin.

- **A1-R1 — Closed.** `scripts/make-pot.mjs` supplies the stable `moda-interact` slug and `Moda Interact` package name and explicitly clears `Report-Msgid-Bugs-To`. The regenerated repository and packaged `languages/moda-interact.pot` are byte-identical, retain `X-Domain: moda-interact`, contain no internal architecture identifier, and no longer invent a WordPress.org support URL. `scripts/package-production.mjs` independently asserts an empty support header and rejects `ARCH-\d+-[A-Z0-9-]+` identifiers without assuming a three-digit architecture number. The two Attempt 2 implementation commits change only the POT, its generator and its package audit.
- **A1-R2 — Closed.** The Completion Report records the launcher-resolved canonical primary workspace, dedicated sibling parent and implementation worktrees, the matching `task/ARCH-026-WOOCOMMERCE-006` branches, start-of-attempt remote/`origin/main` synchronization, recursive submodule preparation, clean/pushed states and the implementation/parent commit chain. The uploaded task document and the relevant Woo source-file Git blobs match their live GitHub task-branch versions. Physical worktree execution and the complete lifecycle run remain developer-submitted evidence; they were not independently recreated in this external review environment.

The accepted package version remains `0.1.0`; the exact uploaded `moda-interact.zip` has 33 entries and SHA-256 `276327aa22fa5bf4ef9e1b9054a52bc16de2040a0b6f571a916b633ff5350286`. The production origin remains PHP-owned and absent from browser JavaScript. No schema, billing, onboarding, provider integration or Marketplace functionality was introduced by Attempt 2.

### Reviewed Files

- `docs/decisions/woocommerce/ARCH-026/WOOCOMMERCE-006-harden-production-packaging-upgrade-lifecycle.md`, including the Completion Report and prior Architect Review.
- `moda-interact-woocommerce/scripts/make-pot.mjs`, `scripts/package-production.mjs`, `languages/moda-interact.pot` and the actual packaged `moda-interact.zip`.
- `moda-interact-woocommerce/tests/integration/run-package-lifecycle.mjs`, `includes/Api/ModaApiConfiguration.php`, `includes/Runtime.php`, `moda-interact.php`, `readme.txt` and release metadata.
- The accepted WOO-005 and GATEWAY-001 task records, ARCH-026 parent architecture, mirrored task-branch commits and GitHub task-branch source blobs.

### Validation Reviewed

- Independently checked the submitted ZIP: correct SHA-256, 33-file single plugin root, complete production Composer autoloader, PHP/JS/CSS + WordPress asset metadata, no source maps or development packages, empty POT support header, correct translation domain and no embedded internal architecture identifier. ZIP integrity passed.
- Independently verified 14 focused artifact and policy assertions, including a regex challenge using one-, three- and nine-digit `ARCH-` identifiers; all passed. `node --check` passed for `make-pot.mjs`, `package-production.mjs` and the lifecycle runner; `php -l` passed for `ModaApiConfiguration.php`, `Runtime.php` and `moda-interact.php`.
- Confirmed the local snapshot Git blob SHAs match the corresponding files on the two pushed GitHub task branches, and reviewed Attempt 2 implementation file scope. The final parent report commit changes only this task document.
- Developer-submitted and reviewed, but **not independently rerun** in this environment: 47 JS tests; 33 PHP tests / 152 assertions; JavaScript/CSS/PHP lint; `npm ci`; Composer dependency restoration; production packaging; WP-CLI fresh install, exact accepted WOO-005-baseline upgrade, Admin render and deactivate/reactivate preservation. The 47 npm dependency audit findings remain a separately recorded, out-of-scope dependency concern, not an unreported test success.

### Architecture Conformance

Accepted. The self-contained plugin artifact preserves the accepted WOO-005 read-only merchant application and WOO-003 server-side credential/connection semantics, uses the Gateway-established HTTPS API default in PHP only, includes WordPress i18n/release assets, and makes no additional hosted service or business-state commitments. The submitted synthetic-state lifecycle evidence establishes unchanged connection state over fresh install/upgrade/deactivate/reactivate; no real merchant credential is used. The mandatory mirrored-branch and dedicated-worktree provenance is now sufficiently recorded. No additional implementation correction is required for this task.

### Follow-up

- Mark `ARCH-026-WOOCOMMERCE-006` **Complete / Accepted**, retaining `attempt: 2` and cleared executor/claim fields.
- The developer owns merging the accepted Woo implementation branch, updating the parent submodule gitlink to the merged implementation-main commit where applicable, then merging the parent task/report branch. This external review made no Git commits, pushes or merges.
- Keep ARCH-026 itself **Proposed**, pending explicit architecture-level finalization and any required terminal system tests. Do not start a downstream task implicitly.
- Do not create or update any `docs/decisions/**/_index.md` until the user explicitly requests architecture-session index reconciliation.

### Historical Attempt 1 Architect Review (superseded)

The original correction contract is retained below. Its `Changes Requested` outcome has been superseded by the Attempt 2 acceptance above.


#### Review Status

Changes Requested — Attempt 1 (2026-10-08).

#### Review Notes

- **A1-R1 — Correct release translation metadata and guard its generation.** The production `moda-interact.zip` and checked-in `languages/moda-interact.pot` contain `Report-Msgid-Bugs-To: https://wordpress.org/support/plugin/ARCH-026-WOOCOMMERCE-006`. This points to the internal task-worktree identifier rather than a valid Moda plugin support destination. Fix `scripts/make-pot.mjs` (or its WP-CLI invocation and related metadata post-processing) so generated POT metadata is independent of the worktree name; do not fabricate a WordPress.org support listing or unrelated legal/support URL. Regenerate `languages/moda-interact.pot`. Extend the existing `scripts/package-production.mjs` package audit to fail on internal `ARCH-` task identifiers or another invalid task-worktree-derived support link in packaged translation metadata, while retaining the `moda-interact` domain and existing extracted strings. Rebuild and inspect the package to prove the defect cannot recur. This is an implementation-source/test correction within the original task scope; do not solve it by hand-editing only the generated POT or ZIP.
- **A1-R2 — Complete the canonical task's VCS/worktree evidence.** The Completion Report provides package and validation evidence but omits the required launcher-resolved dedicated parent/implementation worktree paths and start-of-attempt synchronization/recursive-submodule evidence required by `docs/agent-worktree-isolation-policy.md`. Record both exact worktree paths, matching `task/ARCH-026-WOOCOMMERCE-006` branch identities, launcher/preparation evidence or accurate limitations, synchronization with the task remotes/current main, recursive submodule preparation status, and the implementation/report commit identifiers with pushed/clean-state evidence. Do not invent retrospective evidence or introduce code churn solely to create another implementation commit; this correction is documentation/evidence-only.
- Preserve the accepted WOO-005 upgrade baseline `98273e4ebdfa9a78146cb897fb905ef97a6814e7`, the standard `wp-scripts plugin-zip` path, production API origin and WOO-003 connection-state semantics. No new plugin version bump, billing/onboarding implementation, Marketplace submission or unrelated dependency remediation is authorized.

#### Reviewed Files

- `moda-interact-woocommerce/scripts/package-production.mjs`, `scripts/make-pot.mjs`, `.distignore`, `package.json`, `package-lock.json`.
- `moda-interact-woocommerce/includes/Api/ModaApiConfiguration.php`, `includes/Runtime.php`, `moda-interact.php`.
- `moda-interact-woocommerce/readme.txt`, `languages/moda-interact.pot`, `moda-interact.zip` (actual 33-entry artifact).
- `moda-interact-woocommerce/tests/integration/run-package-lifecycle.mjs`, focused PHP test changes, Completion Report, parent ARCH-026 architecture, prerequisite WOO-005 and GATEWAY-001 task records.
- Remote implementation commit `c6a17eedefee34f6c4c0f538017363fe9de7135a` and parent report commit `e22ba8fb1046d51264954ea2f25aaeaef4ec4a90` (scope and submitted branch state).

#### Validation Reviewed

- Independently inspected the uploaded distribution ZIP: SHA-256 `78d594eb6ab979f4a461d1681e350f73853d488b74515a599ebc67cce2164ca8`, 33 entries, single root `moda-interact/`, required Composer PSR-4/classmap runtime, JavaScript/CSS and WordPress asset metadata. `unzip -tq` passed.
- Independently ran `node --check` on the new packaging, translation and lifecycle scripts and `php -l` on the changed PHP configuration/runtime files; passed in the review environment.
- Confirmed the invalid task-ID `Report-Msgid-Bugs-To` header appears in both the repository POT and packaged POT. Existing production package audit checks domain/project identity but misses this header.
- Submitted validation reviewed but not reproduced in this environment: 47 JS tests; 33 PHP tests / 152 assertions; JS/CSS/PHP lint; clean production packaging; fresh installation, exact WOO-005-baseline upgrade, local option preservation and deactivate/reactivate rehearsal. Existing dependency audit findings remain a separately documented baseline, not part of this correction.

#### Architecture Conformance

- Production package construction, PHP-only hosted API configuration, secret-exclusion scanning, bounded merchant Overview scope and synthetic WOO-003 upgrade-state preservation are consistent with ARCH-026 based on reviewed code and submitted validation.
- The misleading generated translation support destination fails the intended stable plugin identity and release-metadata requirements. The missing durable task-worktree provenance also prevents formal acceptance under the mandated task workflow.
- No source or test change outside the two bounded correction areas is required.

#### Follow-up

- Return the **same task** to `status: ready`, with `executor: null`, `claimed_at: null` and `attempt: 1` preserved. On the next legitimate launcher claim, Attempt 2 begins.
- The repository agent must read this entire latest Architect Review before implementation, correct A1-R1, add A1-R2 evidence to the Completion Report, rerun the focused translation/package audits and task-required validation affected by the correction, then resubmit to `review` and STOP.
- Keep downstream system-test validation gated; do not modify any `docs/decisions/**/_index.md` file during this architecture session.
