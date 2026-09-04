# ARCH-002 — System Test Task Index

## Initiative

Render Test & Production Gateway & Infrastructure

## Owner

```yaml
architecture_id: ARCH-002
domain: system-test
assigned_agent: moda_system_test
repository: moda-interact-system-test
```

## Current Validation Plan

The former broad `SYSTEM-TEST-001` validation task has been decomposed so each
execution task has one environment and one evidence boundary.

```text
SYSTEM-TEST-002 Complete
  local deterministic observability/integration
             |
             +-------------------------------+
                                             |
SYSTEM-TEST-006 Complete                      |
  deployed Render test topology              |
             |                               |
             +-------------------------------+--> SYSTEM-TEST-008 Pending
                                             |      production capacity gate
SYSTEM-TEST-007 Complete                      |              |
  production Blueprint/readiness ------------+              v
                                                    SYSTEM-TEST-001 Pending
                                                    final evidence aggregation
```

`SYSTEM-TEST-002` is architect-accepted Complete. `SYSTEM-TEST-006` is
architect-accepted Complete for the current Render deployment-topology milestone,
with Meta verification GET explicitly deferred to the later WhatsApp/Messaging
integration stage. `SYSTEM-TEST-007` is architect-accepted Complete.

`SYSTEM-TEST-008` becomes Ready only after all three are architect-accepted
Complete.

`SYSTEM-TEST-001` becomes Ready only after `002`, `006`, `007`, and `008` are
architect-accepted Complete.

## Tasks

| Task | Description | Status | Dependencies |
|------|-------------|--------|--------------|
| SYSTEM-TEST-001 | Aggregate final ARCH-002 validation evidence | Pending | SYSTEM-TEST-002, SYSTEM-TEST-006, SYSTEM-TEST-007, SYSTEM-TEST-008 |
| SYSTEM-TEST-002 | Validate shared observability and WhatsApp worker performance | Complete | SHOPIFY-007, BACKGROUND-007, BACKGROUND-009, MESSAGING-004, MESSAGING-005, ADMIN-009, GATEWAY-006, GATEWAY-004, SYSTEM-TEST-003, SYSTEM-TEST-004, SYSTEM-TEST-005 |
| SYSTEM-TEST-003 | Add isolated ephemeral Redis test infrastructure | Complete | - |
| SYSTEM-TEST-004 | Add WhatsApp Cloud API emulator test infrastructure | Complete | BACKGROUND-010 |
| SYSTEM-TEST-005 | Add isolated ephemeral PostgreSQL test infrastructure | Complete | - |
| SYSTEM-TEST-006 | Validate deployed Render test topology | Complete | GATEWAY-004, ADMIN-004, GATEWAY-012, GATEWAY-014 |
| SYSTEM-TEST-007 | Validate production Blueprint and readiness configuration | Complete | GATEWAY-004 |
| SYSTEM-TEST-008 | Assess production-sized Shopify ingress capacity gate | Pending | SYSTEM-TEST-002, SYSTEM-TEST-006, SYSTEM-TEST-007, SYSTEM-TEST-009 |
| SYSTEM-TEST-009 | Revalidate deployment environment-group naming and isolation | Complete | GATEWAY-010, GATEWAY-011, GATEWAY-012, SYSTEM-TEST-007 |
| SYSTEM-TEST-010 | Reconcile production-readiness validator with accepted HAProxy gateway | Ready | GATEWAY-014 |

The individual task frontmatter is authoritative for task state.

## Environment Ownership

### Local deterministic validation

Owned by `SYSTEM-TEST-002` using accepted fixtures:

```text
SYSTEM-TEST-003  ephemeral Redis
SYSTEM-TEST-004  WhatsApp emulator
SYSTEM-TEST-005  ephemeral PostgreSQL
```

These local fixtures do **not** represent Render-hosted dependencies and are not
direct inputs to deployed Render validation.

### Deployed Render test validation

Owned by `SYSTEM-TEST-006`.

It uses the actual deployed Render test environment. The task is now Ready for
live execution; if a mandatory endpoint/credential/environment is genuinely
unavailable at execution time, it may return Blocked with that exact prerequisite. It must not
silently substitute local Docker fixtures.

### Production static readiness

Owned by `SYSTEM-TEST-007`.

It validates actual current Blueprint/configuration files without requiring a
live production deployment.

### Production-sized capacity

Owned by `SYSTEM-TEST-008`.

It produces exactly:

```text
PROVEN
```

or:

```text
UNMET
```

A cheap Render test environment cannot produce `PROVEN` production-capacity
evidence.

If the target environment is unavailable, `UNMET` is the correct evidence-based
result and preserves the architecture blocker.

## Luna Execution Guidance

The immediately executable system-test frontier is:

```text
ARCH-002-SYSTEM-TEST-006
```

These may run independently/in parallel.

`SYSTEM-TEST-002` is Complete and provides the accepted local deterministic
observability/integration evidence required by downstream validation.

Do **not** run `SYSTEM-TEST-001` or `SYSTEM-TEST-008` yet.

After repository-agent work returns to `review`, `moda_architect` must inspect
and accept each task before downstream promotion.

## Defect Rule

`moda_system_test` may inspect/execute the platform but must not modify another
agent's implementation merely to make validation pass.

On a defect:

1. preserve evidence;
2. identify the apparent owning boundary;
3. return Blocked or Review as the task specifies;
4. let `moda_architect` reopen/create the owning task;
5. rerun only after the fix is architect-accepted.


## SYSTEM-TEST-009 environment-group naming revalidation

`SYSTEM-TEST-007` is still architect-accepted for its validation logic, but
`GATEWAY-010` changes the canonical resource names it validates.

`SYSTEM-TEST-009` is therefore a narrow follow-on that updates naming
expectations without reopening the broader production-readiness implementation.

`SYSTEM-TEST-008` remains Pending until this revalidation is Complete.


## SYSTEM-TEST-009 architect changes requested — attempt 1

Attempt 1 correctly validates the canonical purpose-scoped group model but
does not generalize cross-environment isolation to purpose-scoped groups.

The same task is Ready for correction. Any active opposite-environment
`moda-interact-<environment>-*-config` declaration or `fromGroup` reference
must fail, while unrelated non-MODA groups remain allowed.


## Render Blueprint schema block

A real Render Blueprint creation attempt rejected the current key-only
Blueprint-managed Environment Group representation.

`SYSTEM-TEST-009` is Blocked on `ARCH-002-GATEWAY-012`.
`SYSTEM-TEST-006` also cannot resume live topology validation until the
corrected Dashboard-managed groups are created and the Blueprint can be
successfully instantiated.


## Test placeholder policy

SYSTEM-TEST-009 and SYSTEM-TEST-006 are blocked only on GATEWAY-012 for this
Render schema issue.

GATEWAY-013 is production-only and does not block the test validation path.


## GATEWAY-012 accepted — SYSTEM-TEST-009 resumed

The live Render schema defect is resolved and GATEWAY-012 is Complete.

SYSTEM-TEST-009 is Ready to finish its previously requested generalized
cross-environment isolation correction against the final placeholder-bearing
Blueprint contract.

SYSTEM-TEST-006 remains Blocked until the live test Environment Groups contain
real values and the required deployed-topology probe inputs are available.


## SYSTEM-TEST-009 architect changes requested — attempt 2

Attempt 2 now rejects all currently known opposite-environment purpose groups,
but environment isolation is still implemented as a closed purpose whitelist.

The same task is Ready for a final correction: make isolation namespace-based
so any `moda-interact-test-*-config` in production or
`moda-interact-production-*-config` in test fails, while exact canonical
group/key/consumer validation remains unchanged.


## SYSTEM-TEST-009 architect acceptance — attempt 3

Attempt 3 is architect-accepted Complete.

Cross-environment isolation is now namespace-based and future-safe while exact
canonical group ownership remains independently enforced.

The accidental task-metadata cycle was also corrected:
SYSTEM-TEST-009 enables SYSTEM-TEST-008; it does not depend on it.

SYSTEM-TEST-008 remains Pending until its other dependencies, notably live
SYSTEM-TEST-006, are Complete.


## SYSTEM-TEST-006 live frontier opened

The previous external coordination block is resolved.

Evidence now available:

```text
Render test topology created/deployed
admin-test.modainteract.com responds
app-test.modainteract.com responds
GATEWAY-012 Complete
SYSTEM-TEST-009 Complete
```

SYSTEM-TEST-006 is Ready. Provider secrets/tokens remain secure runtime inputs,
not architecture dependencies.

SYSTEM-TEST-008 remains Pending until SYSTEM-TEST-006 is architect-accepted
Complete.


## SYSTEM-TEST-006 Attempt 5 reopened

Attempt 4 stopped correctly before network access because
`ARCH002_TEST_GATEWAY_URL` was malformed.

The developer corrected the runtime URL. SYSTEM-TEST-006 is Ready again for
live execution with the existing runner unchanged.


## SYSTEM-TEST-006 Attempt 6 — stale test group correction

Copilot-side diagnostics now prove `ARCH002_TEST_GATEWAY_URL` is valid.

Architect inspection found the live topology runner still validates the
deprecated `moda-observability-test` group. Attempt 6 is Ready to replace that
bounded preflight with `moda-interact-test-config` +
`DEPLOYMENT_ENVIRONMENT_NAME=test`, then execute the live probes.


## SYSTEM-TEST-006 Attempt 7 — Admin custom-domain correction

Attempt 6 reached live Render and proved gateway, Shopify and signed Meta ingress.

The Admin probe must now call `https://admin-test.modainteract.com` directly
instead of overriding Host while connecting to the Render `onrender.com` URL.

Meta GET verification remains the accepted contract. Before Attempt 7, align
`ARCH002_TEST_META_VERIFY_TOKEN` with the live test Environment Group
`WHATSAPP_VERIFY_TOKEN` and redeploy `moda-interact-messaging-test`.


## SYSTEM-TEST-006 Attempt 8 — remove stale Admin Host probe

Attempt 7 changed Admin root/login to the real custom domain but left the old
synthetic Admin-host `/health` request in the runner.

Attempt 8 removes that obsolete request and adds safe per-probe network failure
identification so a live blocker can no longer collapse to an ambiguous
`fetch failed`.

## SYSTEM-TEST-006 dedicated Messaging ingress dependency

Live test work exposed a gateway ownership gap: Meta/WhatsApp ingress is to use
the dedicated test hostname:

```text
messaging-test.modainteract.com
```

`ARCH-002-GATEWAY-014` now owns the gateway/Blueprint implementation.

Until GATEWAY-014 is accepted and deployed:

```text
SYSTEM-TEST-006 = Blocked
```

The subsequent live attempt will add the task-owned input:

```text
ARCH002_TEST_MESSAGING_HOST=messaging-test.modainteract.com
```

and Meta probes will use the Messaging hostname rather than the Shopify/default
hostname.

## SYSTEM-TEST-006 Attempt 9 — custom-host live-probe correction

Developer live validation at Git HEAD:

```text
ad8dde78ef55bbed42368e35d4f6dff8ccc31520
```

returned exit `1`.

Useful evidence:

```text
blueprint            PASS
gateway health       PASS
ordinary /admin      PASS

Admin                 308/308 due malformed admin host with trailing slash
Shopify valid/invalid 404/404 because probes used native gateway Host
Meta GET/POST          404/404 because probes used native gateway Host
```

GATEWAY-014 is Complete. This is now a system-test runner/input correction.

Attempt 9 must use the canonical Host matrix:

```text
Gateway -> native Render gateway URL
Shopify -> app-test.modainteract.com
Admin -> admin-test.modainteract.com
Meta -> messaging-test.modainteract.com
```

The next `/moda-task ARCH-002-SYSTEM-TEST-006` claim is Attempt 9.

The live Render command remains developer-owned.

## SYSTEM-TEST-006 Attempt 11 — final live-validator correction

The developer run at `20260904T152534Z` proved:

```text
gateway health            PASS
ordinary-host isolation   PASS
Admin root                PASS
Shopify valid/invalid     PASS
Meta signed POST          PASS
```

Two items remain:

```text
Admin /login false-negative:
  runner truncates Next.js response before accepted markers.

Meta verification 403:
  live verify-token alignment/deployment prerequisite, not host routing.
```

Attempt 11 also completes the reusable Render-validator naming migration.

The separate stale NGINX production-readiness test baseline is tracked by
`SYSTEM-TEST-010` and does not expand SYSTEM-TEST-006 scope.

## SYSTEM-TEST-006 architect acceptance — deferred Meta verification

The developer run at `20260904T154320Z` subsequently proved the corrected Admin
login assertion together with the previously passing gateway, Shopify and Meta
signed-POST boundaries. Meta verification GET remained `403`.

`moda_architect` accepts `SYSTEM-TEST-006` as **Complete** for the current Render
deployment-topology milestone. The Meta GET assertion is intentionally deferred
to the later WhatsApp/Messaging integration stage and remains an unpassed test,
not a silently accepted success.

The next active Render investigation is the Shopify checkout asynchronous path:

```text
checkout -> moda-interact -> BullMQ/Redis -> moda-interact-background -> processing
```

`SYSTEM-TEST-006` does not claim that this downstream queue/worker path has yet
been proven.
