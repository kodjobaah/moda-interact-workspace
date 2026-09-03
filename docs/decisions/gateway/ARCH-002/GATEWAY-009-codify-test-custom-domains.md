---
id: ARCH-002-GATEWAY-009
architecture_id: ARCH-002
title: Codify Render test custom domains in the canonical Blueprint
domain: gateway
repository: moda-interact-gateway
assigned_agent: moda_gateway
coordinator: moda_architect
status: complete
priority: 5
executor: copilot
claimed_at: 2026-09-03T15:45:00Z
attempt: 1
depends_on:
  - ARCH-002-GATEWAY-003
  - ARCH-002-GATEWAY-008
  - ARCH-002-GATEWAY-010
  - ARCH-002-GATEWAY-011
enables:
  - ARCH-002-SYSTEM-TEST-006
created: 2026-09-03
updated: 2026-09-03
---

# Codify Render Test Custom Domains in the Canonical Blueprint

## Architecture

Architecture ID:

`ARCH-002`

Architecture document:

`docs/architecture/ARCH-002-render-production-gateway-infrastructure.md`

Coordinator:

`moda_architect`

## Current Execution State

This task is **Ready for Review**.

`ARCH-002-GATEWAY-010` and `ARCH-002-GATEWAY-011` are architect-accepted
Complete.

The canonical deployment configuration/environment-group model is now stable,
so this task may finish the test gateway custom-domain Infrastructure-as-Code
contract.

The Render test gateway is now live at:

```text
https://moda-interact-gateway-test.onrender.com
```

Cloudflare DNS has been configured with DNS-only CNAME records:

```text
admin-test.modainteract.com
  -> moda-interact-gateway-test.onrender.com

app-test.modainteract.com
  -> moda-interact-gateway-test.onrender.com
```

The test gateway already uses:

```text
ADMIN_PUBLIC_HOST=admin-test.modainteract.com
```

for host-based Admin routing.

The remaining infrastructure-as-code gap is that the two test custom domains
must be declared on the Render **web service** in the canonical test Blueprint
instead of depending on manual Render dashboard configuration.

## Objective

Make the canonical Render test Blueprint own these two gateway custom domains:

```text
admin-test.modainteract.com
app-test.modainteract.com
```

so Render can register and manage the test gateway's custom-domain/TLS
configuration from infrastructure as code.

## Required Solution

In:

```text
moda-interact-gateway/render.test.yaml
```

declare the two test domains on the `moda-interact-gateway-test` web service
using Render Blueprint's service-level custom-domain declaration.

Expected shape:

```yaml
- type: web
  name: moda-interact-gateway-test
  # existing service configuration...

  domains:
    - admin-test.modainteract.com
    - app-test.modainteract.com
```

Exact placement may follow the existing Blueprint style.

Preserve:

```text
ADMIN_PUBLIC_HOST=admin-test.modainteract.com
```

and all existing public/private routing.

Do **not** add these domains to the private Admin or Shopify application
services. Both names terminate at the public gateway.

## Routing Contract

The two hostnames have different application semantics even though they resolve
to the same public gateway:

```text
admin-test.modainteract.com
        ↓
moda-interact-gateway-test
        ↓
Host == ADMIN_PUBLIC_HOST
        ↓
private moda-interact-admin-test
```

and:

```text
app-test.modainteract.com
        ↓
moda-interact-gateway-test
        ↓
ordinary/default gateway routing
        ↓
private moda-interact-test
```

The gateway's generated Render hostname remains valid for ordinary gateway
access and system-test probes.

## Scope

Owned repository:

```text
moda-interact-gateway
```

Expected implementation files:

```text
moda-interact-gateway/render.test.yaml
moda-interact-gateway/tests/validate-render-blueprints.sh
```

Update additional gateway-owned validation only if necessary.

The task file may be updated under the normal coordination-document exception.

Do not modify:

```text
render.production.yaml
moda-interact
moda-interact-admin
moda-interact-messaging
moda-interact-background
```

for this task.

Production custom domains are deliberately out of scope until the production
Shopify hostname is explicitly agreed.

## Work Items

- [x] add `admin-test.modainteract.com` to the test gateway service's custom
      domains;
- [x] add `app-test.modainteract.com` to the same test gateway service;
- [x] prove no private service receives either public custom-domain declaration;
- [x] preserve `ADMIN_PUBLIC_HOST=admin-test.modainteract.com`;
- [x] preserve gateway default routing for the Shopify app hostname;
- [x] extend deterministic Blueprint validation for the two domain declarations;
- [x] ensure the validator rejects a missing/wrong test domain;
- [x] run gateway validation;
- [x] update Completion Report and return to `review`.

## Interfaces / Contracts

Consumes accepted gateway routing from:

```text
ARCH-002-GATEWAY-003
```

Consumes the accepted Admin build/deployment Blueprint from:

```text
ARCH-002-GATEWAY-008
```

Enables live deployed-topology validation:

```text
ARCH-002-SYSTEM-TEST-006
```

after Render has synchronized the Blueprint and verified the custom domains.

## Dependencies

- `ARCH-002-GATEWAY-003` — Complete.
- `ARCH-002-GATEWAY-008` — Complete.

## Acceptance Criteria

- [x] `moda-interact-gateway-test` declares exactly the required ARCH-002 test
      custom domains:
      `admin-test.modainteract.com` and `app-test.modainteract.com`;
- [x] neither domain is declared on a private service;
- [x] `ADMIN_PUBLIC_HOST` remains `admin-test.modainteract.com`;
- [x] `app-test.modainteract.com` remains ordinary/default gateway traffic and
      is not added as an Admin host;
- [x] the generated Render gateway hostname remains usable;
- [x] no production domain is invented or added;
- [x] Blueprint validation fails if either required test custom domain is
      removed or misdeclared;
- [x] no secret value is committed.

## Validation

Inspect the actual gateway repository scripts first.

At minimum run:

```text
bash tests/run-tests.sh
bash tests/validate-observability-config.sh
bash tests/validate-render-blueprints.sh
git diff --check
```

Where the accepted system-test static validator is locally runnable, also run:

```text
cd ../moda-interact-system-test
npm run validate:arch002-production-readiness
```

If its local dependencies are not installed, record the exact limitation
rather than modifying that repository.

Also inspect the resulting `render.test.yaml` and prove:

```text
moda-interact-gateway-test:
  domains:
    admin-test.modainteract.com
    app-test.modainteract.com
```

and prove the private services do not declare those domains.

## Live Deployment Follow-up

A static pass does not itself prove Render accepted the custom domains.

After architect acceptance, the developer should commit/push the gateway
Blueprint and allow Render to sync.

Expected live follow-up:

1. Render sync recognizes both test custom domains;
2. Render verifies DNS for both;
3. Render provisions TLS;
4. `https://admin-test.modainteract.com` reaches the Admin login boundary via
   the gateway;
5. `https://app-test.modainteract.com` reaches the Shopify application via the
   gateway.

Those live checks remain part of `ARCH-002-SYSTEM-TEST-006`.

## Failure Handling

If Render Blueprint validation rejects the `domains` declaration:

1. capture the exact Render schema/sync error;
2. do not move the domains to private services;
3. do not silently fall back to undocumented manual dashboard configuration;
4. return the evidence to `moda_architect`.

## Non-Goals

- production custom domains;
- Cloudflare DNS mutation;
- Shopify app/TOML URL migration;
- Admin OAuth callback configuration;
- changing NGINX routing behavior;
- changing application source;
- changing Render plans;
- production deployment.

## Completion Report

### Status

Complete

### Files Changed

The custom-domain declarations in `render.test.yaml` and their positive
validation in `tests/validate-render-blueprints.sh` were already present in the
immediately preceding architect-reviewed GATEWAY-011 workspace.

This attempt added the missing/wrong-domain regression fixtures in
`tests/validate-render-blueprints-negative.sh` and updated this task report.

No production or application repository files were modified.

### Work Completed

The task verified and finalized the canonical custom-domain contract already
present in the submitted gateway state:

```text
admin-test.modainteract.com
app-test.modainteract.com
```

Both terminate on `moda-interact-gateway-test`.

`ADMIN_PUBLIC_HOST` remains `admin-test.modainteract.com`; the app hostname
follows ordinary/default gateway routing. Private services have no custom-domain
declarations and production domains remain unchanged.

This attempt added deterministic negative regression coverage for a missing or
wrong test domain.

### Validation Results

`bash tests/validate-render-blueprints.sh`: passed.

`bash tests/validate-render-blueprints-negative.sh`: passed; canonical and all configuration/domain rejection fixtures passed.

`bash tests/validate-observability-config.sh`: passed.

`bash tests/run-tests.sh`: passed, 49 tests passed and 0 failed.

`git diff --check`: passed.

`npm run validate:arch002-production-readiness`: not rerun; the known local limitation remains the missing `yaml` Node module (`MODULE_NOT_FOUND`).

### Deviations

None.

### Assumptions

Cloudflare DNS-only CNAME records for both test domains already point to the
live Render test gateway hostname.

### Unresolved Issues

Render must still synchronize and verify the custom domains after the code
change is accepted and published. Live DNS/TLS verification remains part of
`ARCH-002-SYSTEM-TEST-006`.

### Architectural Concerns

The custom domains must terminate on the public gateway so Admin and Shopify
remain private services.

## Architect Review

### Review Status

Accepted

### Review Notes

GATEWAY-009 is accepted.

Architect reviewed the actual submitted gateway workspace and confirmed:

- `moda-interact-gateway-test` declares exactly
  `admin-test.modainteract.com` and `app-test.modainteract.com`;
- neither custom domain is declared on any private service;
- `ADMIN_PUBLIC_HOST` remains `admin-test.modainteract.com`;
- the Shopify hostname remains ordinary/default gateway traffic;
- production custom-domain configuration was not broadened;
- the positive Blueprint validator requires the exact two-domain test set;
- the negative validator includes missing/wrong test-domain cases.

Architect independently executed:

```text
bash tests/validate-render-blueprints.sh
bash tests/validate-render-blueprints-negative.sh
bash tests/validate-observability-config.sh
```

All passed.

Architect also mutated each required test domain independently in temporary
Blueprint fixtures and confirmed the positive validator rejects:

```text
missing admin-test.modainteract.com
wrong   admin-test.modainteract.com
missing app-test.modainteract.com
wrong   app-test.modainteract.com
```

The submitted ZIP is not a Git working tree, so `git diff --check` cannot be
independently reproduced from it. The architect environment also does not
provide Docker, so the Docker-backed gateway suite cannot be independently
rerun here. The repository agent reported 49/49 gateway checks and
`git diff --check` passing.

Coordination reconciliation: the custom-domain declarations and positive
validator were already present in the immediately preceding submitted workspace.
Attempt 1 added the negative-domain regression coverage and formalized the task
evidence. The completion report was corrected during acceptance so it does not
claim those pre-existing lines were newly introduced by this task.

Live Render DNS/TLS/application reachability remains owned by
`ARCH-002-SYSTEM-TEST-006` after the Blueprint and Environment Groups are
recreated and synchronized.
