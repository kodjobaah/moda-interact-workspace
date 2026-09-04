# ARCH-002 Gateway Tasks

Architecture:

`docs/architecture/ARCH-002-render-production-gateway-infrastructure.md`

Assigned Agent:

`moda_gateway`

Coordinator:

`moda_architect`

| Task | Description | Status | Dependencies |
|------|-------------|--------|--------------|
| GATEWAY-001 | Inspect platform and define deployment prerequisites | Complete | - |
| GATEWAY-002 | Create public Moda Interact gateway | Complete | GATEWAY-001 |
| GATEWAY-007 | Implement host-based admin gateway routing | Complete | GATEWAY-002, ADMIN-008 |
| GATEWAY-005 | Validate npm-based shared package production builds | Complete | GATEWAY-001, SHOPIFY-004, BACKGROUND-004 |
| GATEWAY-006 | Configure OpenTelemetry transport/environment wiring | Complete | GATEWAY-002, SHOPIFY-006, MESSAGING-003, ADMIN-009, BACKGROUND-005 |
| GATEWAY-003 | Create Render test and production deployment topology | Complete | GATEWAY-002, GATEWAY-005, GATEWAY-006, GATEWAY-007, SHOPIFY-001, SHOPIFY-002, MESSAGING-001, ADMIN-001, ADMIN-008, BACKGROUND-001, BACKGROUND-002 |
| GATEWAY-004 | Validate gateway and Render infrastructure | Complete | GATEWAY-003 |
| GATEWAY-008 | Fix Admin Render build dependency installation | Complete | GATEWAY-003, ADMIN-004, ADMIN-009 |
| GATEWAY-009 | Codify Render test custom domains in the canonical Blueprint | Complete | GATEWAY-003, GATEWAY-008, GATEWAY-010, GATEWAY-011 |
| GATEWAY-010 | Establish concrete Moda Interact deployment configuration groups | Complete | GATEWAY-008 |
| GATEWAY-011 | Move externally supplied Render configuration into reusable environment groups | Complete | GATEWAY-010 |
| GATEWAY-012 | Bootstrap Render Environment Groups with explicit placeholder values | Complete | GATEWAY-009, GATEWAY-011 |
| GATEWAY-013 | Finalize production Render Environment Group ownership | Pending | GATEWAY-012 |
| GATEWAY-014 | Migrate test gateway to HAProxy with explicit host routing | Complete | GATEWAY-009, GATEWAY-012 |

Canonical ARCH-002 Render Blueprints:

```text
moda-interact-gateway/render.test.yaml
moda-interact-gateway/render.production.yaml
```

The two Blueprints must manage distinct resources.

`GATEWAY-003` must remain Pending until every declared dependency is
architect-accepted Complete.

`GATEWAY-006` is gated by accepted deployable runtime/exporter contracts, not by
every later semantic telemetry signal. `SHOPIFY-007`, `MESSAGING-004`,
`MESSAGING-005`, `BACKGROUND-007` and `BACKGROUND-009` remain required inputs
to `SYSTEM-TEST-002`, where end-to-end telemetry arrival and behaviour are
validated.

The production Admin browser contract is host based:

```text
admin.modainteract.com -> gateway -> private moda-interact-admin
```

`GATEWAY-007` resolves the provisional `/admin/*` mapping without reopening the
accepted GATEWAY-002 task.

`SYSTEM-TEST-001` already exists and remains Pending on the final
`GATEWAY-004` infrastructure-validation gate.

The individual task file is authoritative for task state.


## Current unresolved GATEWAY-003 prerequisites

After architect acceptance of `GATEWAY-006`, the unresolved direct
`GATEWAY-003` prerequisites are:

```text
GATEWAY-005
GATEWAY-007
ADMIN-001
ADMIN-008
```

The individual `GATEWAY-003` task file remains authoritative.


## Post-ADMIN-008 GATEWAY-003 dependency re-evaluation

`ARCH-002-ADMIN-008` is Complete, so it is no longer an unresolved
`GATEWAY-003` prerequisite.

`ARCH-002-GATEWAY-007` now has all direct dependencies Complete and is Ready.

The current unresolved direct prerequisites for `ARCH-002-GATEWAY-003` are:

```text
ARCH-002-GATEWAY-005
ARCH-002-GATEWAY-007
ARCH-002-ADMIN-001
```

`GATEWAY-005` remains Pending because `ARCH-002-SHOPIFY-004` is Ready but not
yet Complete.

No downstream task is started automatically.


## GATEWAY-007 architect acceptance

`ARCH-002-GATEWAY-007` is architect-accepted Complete.

The production Admin ingress contract is:

```text
admin.modainteract.com
  -> Render public edge
  -> moda-interact-gateway
  -> private moda_admin
```

The default host rejects the former `/admin` and `/admin/*` proxy mapping.

After reconciling the already accepted `GATEWAY-005` state, the remaining
unresolved direct `GATEWAY-003` prerequisites are:

```text
ADMIN-001
```

No downstream task is automatically started.


## MESSAGING-001 dependency satisfaction

`ARCH-002-MESSAGING-001` is architect-accepted Complete.

`ARCH-002-GATEWAY-003` remains Pending.

Its only unresolved direct prerequisite is now:

```text
ARCH-002-ADMIN-001
```

No gateway task is automatically started.


## ADMIN-001 dependency satisfaction

`ARCH-002-ADMIN-001` is architect-accepted Complete.

This clears the final known unresolved direct dependency for
`ARCH-002-GATEWAY-003`.

Based on the accepted dependency graph:

```text
GATEWAY-002    Complete
GATEWAY-005    Complete
GATEWAY-006    Complete
GATEWAY-007    Complete
SHOPIFY-001    Complete
SHOPIFY-002    Complete
MESSAGING-001  Complete
ADMIN-001      Complete
ADMIN-008      Complete
BACKGROUND-001 Complete
BACKGROUND-002 Complete
```

No known declared direct prerequisite remains unresolved.

`GATEWAY-003` is not automatically promoted here. The architect must inspect
its authoritative current task file before changing its coordination state.


## GATEWAY-003 final readiness promotion

The architect re-read the authoritative `GATEWAY-003` task and re-evaluated
only its explicit `depends_on` list.

Every declared direct prerequisite is Complete.

```text
GATEWAY-003
  pending -> ready
```

No task has been claimed or started by this coordination update.

`GATEWAY-004` remains Pending.


## GATEWAY-003 architect acceptance

`ARCH-002-GATEWAY-003` is architect-accepted Complete.

Accepted canonical topology sources:

```text
moda-interact-gateway/render.test.yaml
moda-interact-gateway/render.production.yaml
```

The Admin custom-domain `/health` correction is included and validated.

The only direct dependency of `ARCH-002-GATEWAY-004` is now Complete, so:

```text
GATEWAY-004
  pending -> ready
```

No executor has been claimed and no downstream task has been started.


## GATEWAY-004 architect acceptance

`ARCH-002-GATEWAY-004` is architect-accepted Complete.

The accepted infrastructure validation evidence covers the gateway integration
suite, Blueprint schema/topology validation, observability configuration,
environment isolation, worker/service boundaries, secret handling and
deployment/rollback documentation.

The ARCH-002 gateway/infrastructure implementation chain is now:

```text
GATEWAY-001 Complete
GATEWAY-002 Complete
GATEWAY-003 Complete
GATEWAY-004 Complete
GATEWAY-005 Complete
GATEWAY-006 Complete
GATEWAY-007 Complete
```

System-test tasks are not automatically promoted; their authoritative direct
dependency lists remain the eligibility source.


## GATEWAY-008 Admin Render build unblock

A real `moda-interact-admin-test` deployment exposed a Render build-contract
defect: the service has `NODE_ENV=production`, while its Blueprint uses plain
`npm ci` even though Next/PostCSS build tooling is intentionally in
`devDependencies`.

`GATEWAY-008` is architect-accepted Complete and owns the canonical test/production Blueprint correction. No Admin source/dependency reclassification is required by the
current evidence.


## GATEWAY-009 test custom-domain IaC task

The Render test gateway is live and Cloudflare now has DNS-only CNAME records
for:

```text
admin-test.modainteract.com
app-test.modainteract.com
```

both targeting `moda-interact-gateway-test.onrender.com`.

`GATEWAY-009` is Ready to codify those two test custom domains on the canonical
Render test gateway service. Production custom domains remain out of scope.


## GATEWAY-010 deployment configuration naming correction

The live Render test environment proved that the shared group is functioning as
deployment configuration, not as an observability-only resource.

Canonical names are now:

```text
moda-interact-test-config
moda-interact-production-config
```

`GATEWAY-010` is Ready. `GATEWAY-009` waits for this rename so custom-domain
work applies to the final canonical Blueprint state.


## GATEWAY-010 architect acceptance / GATEWAY-011 promotion

`ARCH-002-GATEWAY-010` is architect-accepted Complete after review of the
actual gateway workspace.

`ARCH-002-GATEWAY-011` is now Ready and owns the follow-on conversion from
repeated service-level `sync: false` declarations to purpose-scoped,
Dashboard-populated Render Environment Groups.

`GATEWAY-009` remains Pending until GATEWAY-011 is Complete so both tasks do
not concurrently modify the canonical test Blueprint.


## GATEWAY-011 architect changes requested — attempt 1

Attempt 1 broadened the Shopify API credential group to the Shopify event
worker, which did not consume those credentials in the accepted pre-GATEWAY-011
Blueprint.

The same task is Ready for correction. The Shopify event worker must retain
only its common/telemetry + Redis group attachments (plus direct Render
database wiring), and validation must reject attaching the Shopify API group to
that worker.


## GATEWAY-011 architect acceptance — attempt 2

Attempt 2 is architect-accepted Complete.

The Shopify event workers no longer receive Shopify API credentials, the
positive attachment matrix matches that boundary, and an explicit negative
regression rejects reintroducing the credential group.

`GATEWAY-009` is now Ready. Its scope remains the test gateway custom-domain
declarations and deterministic validation.


## GATEWAY-009 architect acceptance

`ARCH-002-GATEWAY-009` is architect-accepted Complete.

The canonical test gateway owns both test custom domains, private services own
neither, and missing/wrong-domain regression coverage is in place.

Live Render verification remains part of `SYSTEM-TEST-006`.




## GATEWAY-012 test placeholder policy

For test, `__SET_IN_RENDER_DASHBOARD__` remains permanently in
`render.test.yaml`.

A future Blueprint sync may reset test Dashboard overrides; re-entering test
values is an accepted operational cost before live integration testing.

`GATEWAY-013` is production-only and does not block SYSTEM-TEST-009 or
SYSTEM-TEST-006.


## GATEWAY-012 architect changes requested — Shopify app URL ownership

Attempt 1 fixed the Render key/value schema, but test `SHOPIFY_APP_URL` remains
a direct service-level value.

The same task is Ready for correction. Move `SHOPIFY_APP_URL` into
`moda-interact-test-shopify-app-config` with the standard placeholder, remove
the direct service value, and update validation/checklists accordingly.


## GATEWAY-012 architect acceptance

GATEWAY-012 Attempt 2 is architect-accepted Complete.

The real Render test Blueprint now passes schema validation and instantiates the
full resource topology. Test `SHOPIFY_APP_URL` is Environment Group-owned and
Dashboard-editable, with redeployment still required for changes to take
effect.

`SYSTEM-TEST-009` may resume. `SYSTEM-TEST-006` remains blocked until real live
test values and required probe inputs are available.

`GATEWAY-013` remains production-only.

## GATEWAY-014 Attempt 2 — HAProxy redesign

Attempt 1 introduced the dedicated test Messaging hostname using NGINX, but the
developer/architect completed the ingress design before acceptance.

The same task is Ready for Attempt 2 and now owns the reverse-proxy migration:

```text
NGINX
  -> HAProxy 3.4.4

APP_PUBLIC_HOST=app-test.modainteract.com
  -> moda_interact

ADMIN_PUBLIC_HOST=admin-test.modainteract.com
  -> moda_admin

MESSAGING_PUBLIC_HOST=messaging-test.modainteract.com
  -> moda_messaging

unknown non-health Host
  -> reject
```

Final gateway rule:

```text
HOST selects service.
PATH belongs to selected service.
UNKNOWN HOST is rejected.
```

`/health` remains gateway-local so Render can validate the gateway independently
of application backends.

GATEWAY-014 remains **test-only**. `render.production.yaml` must not be modified
and no production app/messaging hostname may be invented.

`SYSTEM-TEST-006` remains blocked until the HAProxy implementation is
architect-accepted and the developer deploys the updated test gateway.

## GATEWAY-014 Attempt 2 architect review

Attempt 2 established the correct HAProxy test ingress architecture but was
interrupted before normal task closure.

Architect review accepts the core migration and requests only bounded Attempt-3
corrections:

```text
1. restore the accepted forwarded-header chain/original-client semantics;
2. make Docker integration resource names run-scoped and setup fail-fast;
3. remove stale active NGINX/default-app documentation and test wording;
4. write the Completion Report and return the same task to review.
```

Do not reopen the reverse-proxy choice or Host-routing design.

`SYSTEM-TEST-006` remains blocked until GATEWAY-014 is accepted and the updated
test gateway is deployed.

## Developer-executed long validation policy

GATEWAY-014 Attempt 3 adopts the workspace validation execution policy:

```text
Luna/repository agent:
  fast syntax/static/config validation

Developer:
  long deterministic Docker integration suite
```

For this task Luna must **not** run:

```text
bash tests/run-tests.sh
```

during normal execution.

Luna returns the task to `review` with the exact command. The developer runs the
suite and supplies the exit/result evidence to `moda_architect`.

This changes who waits for expensive deterministic validation; it does not
remove or weaken the validation requirement.

## GATEWAY-014 Attempt 4 — host-port isolation

Attempt 3 proved run-scoped container names work but exposed a remaining
collision on the fixed host port `18080`.

Attempt 4 requires:

```text
default Docker-assigned ephemeral loopback ports;
explicit GATEWAY_PORT* values only as optional overrides;
no implicit 18080/18081/18082 defaults;
no Luna execution/diagnosis/retry of the long integration suite.
```

Luna performs implementation + bounded validation and returns to review.

Developer then runs:

```bash
cd moda-interact-gateway
bash tests/run-tests.sh
echo "exit=$?"
```

## GATEWAY-014 Attempt 5 — developer validation changes requested

Attempt-4 developer validation returned:

```text
50 passed, 9 failed
exit=1
```

Architect review reduces the failures to:

```text
1. duplicate/incorrect effective X-Forwarded-For handling + last-hop X-Real-IP;
2. recovery-path gateway restarts combined with ephemeral host ports, causing
   stale-port status 000 cascades;
3. line-wrap-sensitive observability contract validation;
4. stale "default host" test wording.
```

Keep the accepted HAProxy Host architecture and Attempt-4 ephemeral-port
isolation.

Next claim is Attempt 5.

Luna performs bounded validation only and returns to review. Developer then
reruns:

```bash
cd moda-interact-gateway
bash tests/run-tests.sh
echo "exit=$?"
```

`SYSTEM-TEST-006` remains blocked until GATEWAY-014 is accepted and deployed.

## GATEWAY-014 Attempt 6 — forwarding snapshot + runtime DNS

Attempt-5 developer validation returned:

```text
55 passed, 5 failed
exit=1
```

Architect review identifies:

```text
1. XFF construction still uses a comma-splitting fetch instead of the full
   original header and computes X-Real-IP after mutation;

2. HAProxy resolves private-service hostnames at startup but has no runtime
   resolver, so backend address renewal behind the stable service hostname does
   not recover while the gateway remains running;

3. observability validation remains line-wrap sensitive.
```

Attempt 6 must use the runtime resolver from `/etc/resolv.conf`, keep recovery
through the running gateway, and preserve the full original forwarding chain.

Next claim is Attempt 6.

Developer validation remains external to Luna.

## GATEWAY-014 Attempt 7 — runtime DNS initial readiness

Attempt-6 developer validation failed before ordinary integration assertions:

```text
app backend did not become ready through the gateway
```

Attempt 7 keeps the runtime-DNS architecture and the Attempt-6 forwarding
snapshot, but tunes resolver behaviour for dynamic service discovery:

```text
accepted_payload_size 4096
explicit IPv4 preference
negative DNS holds shorter than the bounded readiness window
safe readiness-failure DNS/network diagnostics
```

Next claim is Attempt 7.

The long Docker suite remains developer-executed.

## GATEWAY-014 Attempt 8 — live Render hostport correction

Attempt-7 local integration passed:

```text
58 passed, 0 failed
```

Live Render then showed all three private backends as `<NOSRV>` while Host routing
was correct.

The developer manually removed HAProxy runtime resolvers from the three normal
Render `hostport` backend servers and redeployed.

Live result after that change:

```text
gateway 200
app 200
admin 200
admin /login 200
messaging 200
```

Attempt 8 makes this live-proven configuration authoritative and corrects the
Docker recovery test so it validates health recovery of the same service
identity rather than recreated-container IP rediscovery.

Next claim is Attempt 8.

## GATEWAY-014 final architect acceptance — Attempt 8

`GATEWAY-014` is Complete after the live Render test deployment corrected the
earlier runtime-DNS assumption.

Final accepted model:

```text
Render fromService hostport
    ->
normal HAProxy/system startup resolution
    ->
HAProxy health checks
```

Final evidence:

```text
local Docker:
  58 passed, 0 failed
  exit=0

live Render:
  gateway 200
  app 200
  admin 200
  admin /login 200
  messaging 200

unknown public Host:
  403 at Cloudflare edge
```

Local/direct HAProxy retains strict unknown-Host `404`.

This clears the GATEWAY-014 dependency for `SYSTEM-TEST-006`.
