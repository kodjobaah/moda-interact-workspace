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
status: pending
priority: 60
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-026-WOOCOMMERCE-005
  - ARCH-026-GATEWAY-001
enables: []
created: 2026-10-02
updated: 2026-10-02
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
- the accepted development/test override mechanism remains available without weakening production HTTPS validation;
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

- [ ] Freeze the canonical server-side production API default to `https://api.modainteract.com` while retaining accepted test/development injection.
- [ ] Reconcile package/release version metadata so all package surfaces use one current version.
- [ ] Harden the canonical production packaging command/allowlist around accepted WOO-005 runtime files.
- [ ] Ensure production Composer autoload/runtime is included without Composer development packages or `vendor/bin`.
- [ ] Add/update a standard WordPress `readme.txt` describing only implemented capability and the external Moda service dependency.
- [ ] Replace/update scaffold-residue translation template metadata with the `moda-interact` translation template.
- [ ] Add deterministic package manifest/safety validation for required and prohibited contents.
- [ ] Add targeted validation proving local/test API origins and secrets cannot enter packaged runtime/browser assets.
- [ ] Build the WOO-006 candidate ZIP from a clean task worktree.
- [ ] Perform clean supported-environment ZIP install/activation/Admin-render smoke.
- [ ] Build/install the exact architect-accepted WOO-005 baseline package and record its implementation SHA.
- [ ] Establish a synthetic non-production WOO-003 connection-option fixture on the baseline installation.
- [ ] Upgrade that installation in place to the WOO-006 candidate ZIP.
- [ ] Prove the connection option and merchant lifecycle state are preserved and no automatic reconnect occurs.
- [ ] Prove post-upgrade deactivate/reactivate preserves the connection option.
- [ ] Restore/verify development dependencies after packaging where the packaging command temporarily materializes production-only Composer state.
- [ ] Document artifact creation, package manifest, upgrade rehearsal and local validation in the Completion Report.

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

- [ ] One repository-owned command builds the production `moda-interact.zip` from a clean checkout with locked dependencies.
- [ ] Packaging leaves tracked repository files unchanged.
- [ ] ZIP root is exactly `moda-interact/` and main plugin file is `moda-interact/moda-interact.php`.
- [ ] Package version metadata is consistent across plugin header, npm package metadata/lockfile and current changelog entry.
- [ ] Package contains all accepted PHP runtime, built JS/CSS/dependency metadata, production Composer autoload files and translation/readme assets required by WOO-005.
- [ ] Package excludes `node_modules`, source/test/development environment files, `vendor/bin`, Composer development packages, source maps, caches/logs and real credentials/secrets.
- [ ] Packaged production PHP defaults to `https://api.modainteract.com` through the accepted server-side configuration owner.
- [ ] Built browser JS contains no production/test Moda API origin and no installation credential/bootstrap secret.
- [ ] Packaged runtime contains no localhost/wp-env/test API origin as a production default.
- [ ] `languages/moda-interact.pot` reflects Moda Interact/text-domain identity and merchant-visible strings; scaffold translation identity is removed from the package.
- [ ] No fixed WordPress/WooCommerce locale allowlist is introduced.
- [ ] Standard packaged `readme.txt` accurately discloses the current external Moda hosted-service dependency and does not advertise unimplemented features.
- [ ] Clean supported WordPress/WooCommerce environment installs and activates the candidate ZIP successfully.
- [ ] Packaged Woo Admin application renders from local plugin assets without Node/npm/Composer on the WordPress runtime.
- [ ] Install/activation itself performs no automatic Moda connection/reconnect or business-state mutation.
- [ ] Upgrade baseline is built from the exact architect-accepted WOO-005 implementation commit and that SHA is recorded.
- [ ] In-place upgrade to the candidate ZIP preserves the synthetic WOO-003 connection option exactly in logical content.
- [ ] Upgrade does not automatically rotate/reconnect the installation credential or reset onboarding/billing/entitlement state.
- [ ] Candidate remains usable/renderable after upgrade.
- [ ] Deactivate/reactivate after upgrade preserves the same connection option.
- [ ] No billing, recovery, Merchant Knowledge, product/discount, commerce-event or Background functionality is introduced.

## Validation

Run the Woo repository's declared validation commands and record exact commands/results.

Required validation categories:

- [ ] required `scripts/bootstrap-woocommerce.sh` toolchain bootstrap succeeds before repository validation;
- [ ] clean npm install from lockfile;
- [ ] clean Composer development install from lockfile;
- [ ] production build;
- [ ] PHP lint/code-standard/static checks;
- [ ] JavaScript lint/tests;
- [ ] PHP tests;
- [ ] translation-template generation/validation for `moda-interact`;
- [ ] package version-consistency check;
- [ ] production package command succeeds;
- [ ] `unzip -t` succeeds;
- [ ] deterministic archive manifest audit for required/prohibited paths;
- [ ] Composer production-runtime audit proving required autoload files are present and require-dev packages/`vendor/bin` are absent;
- [ ] targeted packaged-runtime secret/API-origin scan;
- [ ] clean current supported WordPress/WooCommerce ZIP install + activation smoke;
- [ ] packaged `/moda-interact` Admin render smoke from local assets;
- [ ] network fixture/assertion proving install/activation does not require a Moda API request;
- [ ] accepted WOO-005 baseline package build from its recorded implementation SHA;
- [ ] baseline install/activation with deterministic synthetic WOO-003 connection-option fixture;
- [ ] in-place candidate ZIP update/upgrade smoke;
- [ ] pre/post-upgrade logical connection-option equality assertion;
- [ ] post-upgrade Admin render smoke;
- [ ] post-upgrade deactivate/reactivate smoke with connection-option preservation;
- [ ] restore/verify development dependency state after production package creation when applicable;
- [ ] `git diff --check`;
- [ ] implementation worktree clean-state evidence required by the normal task protocol.

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

- WOO-005 provides the complete merchant-facing functionality intended for the ARCH-026 foundation distribution candidate.
- GATEWAY-001 establishes `https://api.modainteract.com` as the canonical production API ingress.
- WOO-003 connection state remains server-side/non-autoloaded and survives normal plugin deactivation.
- No public/Marketplace Moda plugin version predates this ARCH-026 development initiative, so no external backwards-compatibility adapter is required.

### Unresolved Issues

None within the packaging/upgrade scope.

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
