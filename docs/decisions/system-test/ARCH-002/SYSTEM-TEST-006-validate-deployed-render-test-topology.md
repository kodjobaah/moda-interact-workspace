---
id: ARCH-002-SYSTEM-TEST-006
architecture_id: ARCH-002
title: Validate deployed Render test topology
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
status: complete
priority: 46
executor: copilot
claimed_at: 2026-09-04T15:34:18Z
attempt: 11
depends_on:
  - ARCH-002-GATEWAY-004
  - ARCH-002-ADMIN-004
  - ARCH-002-SHOPIFY-008
  - ARCH-002-GATEWAY-008
  - ARCH-002-GATEWAY-009
  - ARCH-002-GATEWAY-010
  - ARCH-002-GATEWAY-012
  - ARCH-002-GATEWAY-014
enables:
  - ARCH-002-SYSTEM-TEST-008
  - ARCH-002-SYSTEM-TEST-001
created: 2026-09-03
updated: 2026-09-04
---

# Validate Deployed Render Test Topology

## Current Execution State

This task is **Complete — architect accepted for the current Render deployment-topology milestone**.

The developer-owned live run at `20260904T154320Z` established the deployment
and routing evidence required for this milestone. The remaining Meta verification
GET `403` is explicitly deferred because WhatsApp/Meta end-to-end integration is
not yet the active delivery boundary. The assertion remains valid and must be
revalidated in a subsequent WhatsApp/Messaging system-test stage; it is not
considered passed.

The next active Render investigation is the deployed Shopify checkout-processing
path: `checkout -> moda-interact -> BullMQ/Redis -> moda-interact-background ->
checkout processing`. Completion of this task does not claim that downstream
queue consumption has already been proven.

Attempt 8 produced useful deployed evidence, but subsequent manual validation
identified an architecture boundary that must be corrected upstream before the
Meta/WhatsApp assertions can be treated as final.

The canonical test topology must first establish:

```text
messaging-test.modainteract.com
  -> public moda-interact-gateway-test
  -> private moda-interact-messaging-test
```

through:

```text
ARCH-002-GATEWAY-014
```

`SYSTEM-TEST-006` must not implement gateway routing itself.

Attempt 10 follows the accepted gateway ingress correction and preserves the
system-test ownership boundary. Live Render execution remains developer-owned;
the agent will perform only local, unit, static and fail-closed validation.

Manual test evidence already established that the Admin custom domain itself is
reachable and serves the expected login boundary. Do not reopen gateway/Admin
implementation merely because earlier system-test probes used malformed host
input.


## Objective

Prove that the deployed ARCH-002 Render test environment conforms to the agreed
public/private topology without weakening production boundaries for test
convenience.

Target logical topology:

```text
Internet
   |
Render public load balancer
   |
moda-interact-gateway-test
   |
Render private network
   +--> moda-interact-test
   +--> moda-interact-messaging-test
   +--> moda-interact-admin-test

Redis / PostgreSQL / workers remain deployment dependencies, not public HTTP
upstreams.
```

## Required Preflight

Before writing or running live probes, inspect the current accepted:

```text
moda-interact-gateway/render.test.yaml
moda-interact-gateway/nginx/nginx.conf.template
moda-interact-gateway/docs/
```

and the owning repositories only as needed to discover actual health/readiness
and webhook contracts.

Do not invent routes, secrets, host names or authentication behavior.

### Live environment input

The test runner may introduce task-owned **system-test input names** such as:

```text
ARCH002_TEST_GATEWAY_URL
ARCH002_TEST_ADMIN_HOST
ARCH002_TEST_MESSAGING_HOST
ARCH002_TEST_SHOPIFY_API_SECRET
ARCH002_TEST_META_APP_SECRET
ARCH002_TEST_META_VERIFY_TOKEN
```

when those inputs are needed for a deterministic probe.

These names are system-test runner inputs, not new production platform
configuration contracts.

Secret values must be supplied outside source control and must never be written
to logs, reports or committed fixtures.

If the deployed Render test environment, required endpoint, or required secret
for a mandatory live assertion is unavailable, record the exact missing
prerequisite and return this task **Blocked**. Do not substitute a developer
process and do not claim a static Blueprint check as live evidence.

## Exact Validation Boundary

### A. Public gateway reachability

Using the actual deployed test gateway URL:

- verify the gateway is reachable over the expected public protocol;
- verify its gateway-local `/health` contract;
- capture request ID/correlation behavior that is externally observable;
- record bounded response/status evidence.

### B. Gateway routing

Exercise only routes supported by the accepted gateway/application contracts.
Where the required test credentials are available:

- send a bounded synthetic Shopify webhook through the public gateway with a
  valid signature and verify it reaches the intended private application
  boundary;
- send an invalid Shopify signature and verify it is rejected by the owning
  application boundary;
- exercise Meta/WhatsApp verification and/or signed inbound webhook behavior
  through the public gateway using test credentials;
- verify required signature/query/header material survives proxying without
  being emitted in system-test output.

Do not send production customer payloads.

### C. Admin host routing boundary

Using the deployed gateway and the test environment's configured
`ADMIN_PUBLIC_HOST` value:

- verify the Admin host selects the private Admin upstream rather than the
  default Shopify upstream;
- verify the Admin application remains root-based and does not require a
  Next.js `/admin` base path;
- verify `/admin` on the ordinary/default host is not a privileged Admin route;
- verify an anonymous request does not gain privileged Admin capability.

Do not automate Google credentials into source control. Existing accepted Admin
repository evidence remains authoritative for privileged identity semantics;
this task validates the deployed routing/authentication boundary that can be
observed safely.

### D. Private-service exposure

Verify the current Render test Blueprint declares application, messaging and
Admin services as private services and background consumers as workers.

Do **not** add public endpoints merely to prove that private services exist.

Where a private health/readiness route cannot be reached from the external test
runner without weakening topology, combine:

```text
accepted owning-repository health/readiness evidence
+
current Render private-service declaration
+
externally observable gateway behavior
```

and state that evidence boundary explicitly.

### E. Test-state isolation

Verify the deployed test Blueprint uses test-scoped resource/environment
identity, including the Render test PostgreSQL resource and test observability
environment identity.

Do not infer production capacity from the deployed test plans.

## Implementation Guidance for Luna

Keep implementation small and deterministic.

Preferred system-test structure when new code is needed:

```text
moda-interact-system-test/src/render-test-topology.js
moda-interact-system-test/scripts/run-arch002-render-test-topology.js
moda-interact-system-test/test/render-test-topology.test.js
```

A package script may be added, for example:

```text
validate:arch002-render-test
```

The exact internal helper structure may follow repository conventions, but do
not modify `moda-interact-gateway` or another owning repository.

Unit tests should cover input validation and response classification without
requiring live Render access. The live validation command must fail/Block rather
than silently skip a mandatory deployed assertion.

## Scope

- implement bounded deployed-test probes in `moda-interact-system-test`;
- inspect current gateway/test Blueprint configuration;
- validate externally observable gateway routing and test isolation;
- validate private exposure from architecture-approved declarations without
  making services public;
- record exact environment prerequisites and live evidence.

## Out of Scope

- local ephemeral Redis/PostgreSQL/WhatsApp integration;
- production Blueprint validation (SYSTEM-TEST-007);
- production-sized load testing (SYSTEM-TEST-008);
- changing Render application/gateway implementation;
- weakening authentication or service exposure;
- using production data or credentials.

## Work Items

- [x] Inspect current test Blueprint/gateway route contracts.
- [x] Define bounded task-owned live test inputs without committing secrets.
- [x] Implement unit-testable deployed topology validation helpers/runner.
- [ ] Validate public gateway reachability and health.
- [ ] Validate bounded Shopify gateway route integrity when required test secret is available.
- [ ] Validate bounded Meta/WhatsApp gateway route integrity when required test credentials are available.
- [ ] Validate Admin host/default-host routing boundary.
- [ ] Validate private-service/worker declarations without exposing new public routes.
- [ ] Validate test PostgreSQL/telemetry environment isolation declarations.
- [x] Run repository test/typecheck/lint commands actually defined in package.json.
- [ ] Run the live deployed-test validation command to completion.
- [x] Record evidence or exact blocker; do not fake/skips-as-pass.
- [x] Return to `blocked` when mandatory live prerequisites are unavailable.

## Acceptance Criteria

- [ ] live evidence comes from the deployed Render test environment, not local substitutes;
- [ ] gateway reachability/health are proven;
- [ ] required public ingress routing is proven through the gateway;
- [ ] Admin host/default-host boundary is proven without exposing Admin directly;
- [x] private application services remain private in the current test Blueprint;
- [x] background consumers remain worker services rather than HTTP upstreams;
- [x] test PostgreSQL/telemetry identity is distinct from production declarations;
- [x] no secret value is committed or emitted in validation evidence;
- [x] mandatory unavailable live prerequisites cause Blocked, not a false pass;
- [x] repository validation is green for changed system-test code;
- [ ] task returns to `review` only after mandatory live assertions have executed.

## Validation

Inspect `moda-interact-system-test/package.json` first and run the commands it
actually declares.

Expected validation after implementation normally includes:

```text
npm test
npm run typecheck
npm run lint
```

plus the new bounded deployed test command.

Do not invent an alternative repository validation contract if scripts differ.

## Architect Correction Request — attempt 2

`moda_architect` reviewed the attempt-1 implementation. Preserve the existing
Blueprint validation, timeout/redaction behavior, package script and test
structure. Correct only the following live-probe contracts.

### 1. Use the correct provider-specific HMAC formats

The current runner uses one helper:

```js
function signedBody(secret, body) {
  return `sha256=${crypto.createHmac("sha256", secret).update(body).digest("hex")}`;
}
```

That format is correct for the accepted Meta ingress implementation, but it must
not be reused for Shopify.

Create bounded provider-specific helpers:

```text
Shopify:
HMAC-SHA256(raw body, SHOPIFY_API_SECRET)
-> base64 digest
-> X-Shopify-Hmac-Sha256: <base64>

Meta:
HMAC-SHA256(raw body, META_APP_SECRET)
-> hexadecimal digest
-> X-Hub-Signature-256: sha256=<hex>
```

Do not change the owning application implementations.

### 2. Send the Shopify headers required by the accepted webhook boundary

The accepted Shopify route authenticates through `authenticate.webhook(request)`
and then requires provider metadata including a delivery ID.

For the bounded synthetic probe, send deterministic non-secret provider
metadata including:

```text
X-Shopify-Hmac-Sha256
X-Shopify-Topic
X-Shopify-Shop-Domain
X-Shopify-Webhook-Id
X-Shopify-API-Version
```

Use a deterministic synthetic `*.myshopify.com` shop domain. It does not need
to represent an active merchant; a valid authenticated delivery may be
quarantined by the application and still prove that the gateway preserved the
provider contract.

Prefer a bounded topic/payload that cannot trigger meaningful production-like
business work in the test environment. Do not use customer data.

Add an invalid-signature probe using the same bounded body/metadata and prove
the owning Shopify boundary rejects it. The invalid case must not be considered
successful merely because it reached the gateway.

### 3. Strengthen the Admin-host proof

The current:

```text
admin root -> any redirect/401/403
```

classifier is too broad to prove that the request reached
`moda-interact-admin`.

Use the accepted Admin contract to make the proof deterministic without Google
credentials. For example:

```text
Host = ARCH002_TEST_ADMIN_HOST
GET /
-> anonymous Admin redirect specifically targets /login

and/or

Host = ARCH002_TEST_ADMIN_HOST
GET /login
-> bounded response characteristic of the Admin login page
```

Do not authenticate a privileged user.

Continue proving that `/admin` on the ordinary/default gateway host is not the
privileged Admin route. Prefer the actual gateway URL's normal/default Host for
that assertion rather than inventing an unrelated Host if the Render edge would
make that ambiguous.

### 4. Unit-test the corrected classifiers/signing helpers

Add focused tests that prove at minimum:

- Shopify signing output is the expected base64 HMAC form and does not contain
  the Meta `sha256=` prefix;
- Meta signing remains `sha256=<hex>`;
- the valid/invalid Shopify response classifiers are distinct;
- Admin anonymous routing requires the accepted Admin login boundary rather
  than accepting any redirect.

Do not duplicate owning-repository authentication tests.

### Live prerequisites remain external

After the deterministic corrections, the live command still requires values for:

```text
ARCH002_TEST_GATEWAY_URL
ARCH002_TEST_ADMIN_HOST
ARCH002_TEST_SHOPIFY_API_SECRET
ARCH002_TEST_META_APP_SECRET
ARCH002_TEST_META_VERIFY_TOKEN
```

These must correspond to the deployed Render **test** environment and must stay
outside source control and reports.

If they are unavailable during attempt 2:

1. run all repository/unit validation;
2. invoke the live command and confirm it fails closed listing only input names;
3. return `status: blocked`;
4. record that the deterministic corrections are complete;
5. STOP.

If they are available, run the complete live validation and return to `review`
only if every mandatory assertion passes.

### Attempt-2 validation

Run the actual scripts declared by `moda-interact-system-test/package.json`,
including:

```text
npm test
npm run typecheck
npm run lint
npm run validate:arch002-render-test
git diff --check
```

Do not modify `moda-interact-gateway`, `moda-interact`,
`moda-interact-messaging` or `moda-interact-admin`.

## Architect Correction Request — attempt 3

Preserve every accepted attempt-2 change. Correct only these two live-probe
contracts.

### 1. Meta POST must use the real gateway/default Host

The current Meta POST sends:

```js
host: "ordinary.test.invalid"
```

That is not a valid deployed-Render proof. Render's public edge may reject an
unrecognised Host before the request reaches the gateway NGINX process, making
the result ambiguous.

For the ordinary/default-host Meta POST, use the actual host from
`ARCH002_TEST_GATEWAY_URL`, equivalent to:

```js
new URL(base).host
```

or simply allow the HTTP client to generate the Host from that URL.

Do not invent an unrelated Host header.

The Admin-host probe remains separate and must continue using
`ARCH002_TEST_ADMIN_HOST`.

Add/adjust focused unit coverage or deterministic helper coverage so the
ordinary Meta probe cannot regress to an invented host.

### 2. Shopify probe API version must match the accepted app contract

The accepted Shopify application currently configures:

```text
ApiVersion.July26
```

Therefore the synthetic webhook metadata must use:

```text
X-Shopify-API-Version: 2026-07
```

not the future/mismatched `2026-10` value currently in the runner.

Keep the existing bounded synthetic shop domain, webhook ID, topic, HMAC and
invalid-signature probe. Do not change the Shopify application.

Prefer one named test-owned constant/helper for the accepted probe API version
rather than duplicating the literal across implementation and tests.

Add focused coverage proving the generated Shopify metadata uses `2026-07`.

### External prerequisites remain unchanged

After these two corrections the mandatory live inputs remain:

```text
ARCH002_TEST_GATEWAY_URL
ARCH002_TEST_ADMIN_HOST
ARCH002_TEST_SHOPIFY_API_SECRET
ARCH002_TEST_META_APP_SECRET
ARCH002_TEST_META_VERIFY_TOKEN
```

If they are unavailable:

1. run the repository validation;
2. invoke `npm run validate:arch002-render-test`;
3. confirm it fails closed before network access and lists only missing input
   names;
4. set the task back to `blocked`;
5. record that the deterministic probe implementation is architect-ready for
   live execution;
6. STOP.

If all five are available, execute the full live validation and return to
`review` only if all mandatory assertions pass.

### Validation

Run the scripts actually declared by `moda-interact-system-test/package.json`,
including:

```text
npm test
npm run typecheck
npm run lint
npm run validate:arch002-render-test
git diff --check
```

Do not modify another repository and do not commit/push.



## GATEWAY-012 Resolution

The Render Blueprint schema block is resolved: GATEWAY-012 is
architect-accepted and the full test topology has been instantiated.

This task remains Blocked for live execution until the externally supplied test
Environment Group placeholders have been replaced with real values and the
required live probe inputs are available.

Do not treat a Render `Deployed` status alone as proof that provider-backed
application flows are ready for SYSTEM-TEST-006.


## Architect Coordination Update — Live Frontier Open

The live Render test topology is now instantiated and both public test
hostnames respond through the gateway.

`SYSTEM-TEST-006` is therefore Ready. The required provider secrets/tokens are
execution inputs and should be injected securely into the shell/agent
environment before the task is launched.

No new implementation work is authorized unless the live runner demonstrates
a defect.


## Architect Coordination Update — Attempt 5 Reopened

Attempt 4 is retained below as historical evidence.

Its sole blocker was:

```text
ARCH002_TEST_GATEWAY_URL -> malformed URL
```

The developer has corrected that runtime input, so the coordination blocker is
resolved.

The task is reopened without code changes. Attempt 5 should run the already
accepted live runner unchanged.


## Architect Correction — Attempt 6

### Stale Environment Group Check

The submitted live topology validator currently contains logic equivalent to:

```js
const envGroup = document?.envVarGroups?.find(
  (group) => group.name === "moda-observability-test"
);
```

and reports:

```text
test observability environment identity is missing
```

That group name is obsolete.

The architect-accepted/live GATEWAY-012 test Blueprint now defines:

```text
moda-interact-test-config
```

with:

```text
DEPLOYMENT_ENVIRONMENT_NAME=test
```

and no `moda-observability-test` group.

The live runner currently calls:

```text
getLiveInputs()
validateRenderTestBlueprint(...)
network probes...
```

So once the now-correct URL passes `getLiveInputs()`, the stale group-name
check would reject the accepted Blueprint before network execution.

### Required Correction

In:

```text
moda-interact-system-test/src/render-test-topology.js
```

update the bounded test-environment identity validation to require:

```text
group name: moda-interact-test-config
DEPLOYMENT_ENVIRONMENT_NAME: test
```

Do not restore or accept deprecated:

```text
moda-observability-test
```

Update the validation error wording to describe the current deployment
environment identity rather than the deprecated observability ownership model.

For example:

```text
test deployment environment identity is missing
```

### Unit Regression

Update:

```text
moda-interact-system-test/test/render-test-topology.test.js
```

so its valid Blueprint fixture uses:

```text
moda-interact-test-config
```

Add/retain deterministic coverage proving:

```text
moda-interact-test-config + DEPLOYMENT_ENVIRONMENT_NAME=test -> valid
moda-observability-test only -> invalid
missing DEPLOYMENT_ENVIRONMENT_NAME=test -> invalid
```

Do not duplicate the full SYSTEM-TEST-009 static Environment Group validator
inside SYSTEM-TEST-006. SYSTEM-TEST-009 already owns the exhaustive canonical
group/key/consumer contract.

SYSTEM-TEST-006 only needs enough static preflight to establish that it is
probing the accepted test deployment identity/topology.

### Live Execution

After the correction, run the existing live command with the existing runtime
inputs.

Do not print the Shopify/Meta secret/token values.

The required non-secret inputs remain:

```text
ARCH002_TEST_GATEWAY_URL=https://moda-interact-gateway-test.onrender.com
ARCH002_TEST_ADMIN_HOST=admin-test.modainteract.com
```

The three provider secret/token inputs are already expected to be present in
the execution environment.

The goal of Attempt 6 is to proceed beyond preflight and actually execute the
bounded network assertions.

If a network assertion then exposes a genuine new implementation or deployment
defect, record the exact assertion/result without broadening this correction.

### Validation

Run:

```text
node --test test/render-test-topology.test.js
npm test
npm run typecheck
npm run lint
npm run validate:arch002-render-test
git diff --check
```

If the unrelated WhatsApp emulator full-suite issue reappears while its test
passes independently, record both results and do not change unrelated emulator
implementation in this task.

Return the same task to `review` if the live mandatory assertions complete.

Return to `blocked` only for a genuine external live prerequisite that remains
unavailable.


## Architect Correction — Attempt 7

### 1. Admin proof must use the real Admin custom domain

Attempt 6 sends Admin probes to:

```text
ARCH002_TEST_GATEWAY_URL
```

while manually overriding:

```http
Host: admin-test.modainteract.com
```

That is not the correct deployed custom-domain proof.

The accepted Render topology now exposes the Admin boundary through the actual
custom domain:

```text
https://admin-test.modainteract.com
```

Both custom domains terminate on the same gateway service, but Render's edge
and TLS/custom-domain handling are part of the deployed path. Do not assume
that connecting to the `onrender.com` hostname while overriding the HTTP Host
is equivalent to browsing the verified custom domain.

Construct the Admin base URL from the accepted Admin host and the gateway
scheme, for example:

```js
const gateway = new URL(inputs.gatewayUrl);
const adminBase = `${gateway.protocol}//${inputs.adminHost}`;
```

Then perform the Admin probes against:

```text
GET <adminBase>/
GET <adminBase>/login
```

Do **not** add a manual `Host` header to those requests.

The ordinary/default-host `/admin` negative assertion must continue using
`ARCH002_TEST_GATEWAY_URL`.

### 2. Admin acceptance boundary

The accepted Admin application is root-based and defines an explicit `/login`
page.

The strongest unauthenticated routing proof is therefore:

```text
GET https://admin-test.modainteract.com/login
-> 200
-> page characteristic of Moda Interact Platform Admin login
```

using the existing bounded markers:

```text
Platform Admin
Continue with Google
```

For the root request, do not require only an HTTP 30x response.

Next.js server rendering/streaming may represent a server-component redirect in
a response shape that is not a simple transport-level 302. The test must not
mistake that framework behavior for privileged access.

The root assertion should prove that an anonymous caller does **not** receive
privileged Admin content. Acceptable bounded evidence may include:

```text
transport redirect to /login
OR
framework redirect/login response that does not expose privileged page markers
```

Do not add Google authentication.

Do not weaken the direct `/login` proof.

At minimum, privileged markers such as the actual protected dashboard heading
must not be returned to an anonymous root request.

### 3. Meta verification is not a code correction

Do not change:

```text
/webhook/whatsapp
hub.mode
hub.verify_token
hub.challenge
```

or its `200 + exact challenge` success contract merely because Attempt 6
returned `403`.

Attempt 6's signed Meta POST passed. That establishes:

```text
gateway messaging route       reachable
Meta signature forwarding     working
ARCH002_TEST_META_APP_SECRET  consistent with deployed messaging service
```

A verification GET `403` is therefore treated as a live configuration mismatch
unless subsequent evidence proves otherwise.

Before running Attempt 7, require the developer to align:

```text
ARCH002_TEST_META_VERIFY_TOKEN
Render Environment Group:
  moda-interact-test-meta-webhook-config
  WHATSAPP_VERIFY_TOKEN
```

and redeploy:

```text
moda-interact-messaging-test
```

after changing the Environment Group.

Never emit the token values.

### 4. Regression coverage

Update the focused system-test unit coverage so it proves:

```text
Admin custom-domain URL derives from ARCH002_TEST_ADMIN_HOST
Admin requests do not depend on a manual Host override
/login 200 + accepted Admin login markers -> PASS
ordinary/default gateway /admin remains 404 -> PASS
```

Retain provider HMAC/signature tests and all accepted Attempt-6 Blueprint
identity checks.

Do not modify Admin, Gateway, Shopify or Messaging repositories in this task.

### 5. Live execution

After the bounded Admin-probe correction and after the Meta verify token has
been aligned/redeployed, execute:

```text
npm run validate:arch002-render-test
```

The goal is to complete every mandatory deployed assertion.

If a mandatory assertion fails, record only:

```text
assertion name
status
bounded non-secret classification evidence
```

Do not emit provider secrets/tokens.

### Validation

Run:

```text
node --test test/render-test-topology.test.js
npm test
npm run typecheck
npm run lint
npm run validate:arch002-render-test
git diff --check
```

Return the same task to `review` when all mandatory live assertions pass.

Return to `blocked` only if the corrected direct-domain Admin probe or aligned
Meta verification still demonstrates a genuine live deployment/configuration
failure.


## Architect Correction — Attempt 8

### 1. Remove the obsolete synthetic Admin health request

Attempt 7 correctly introduced:

```text
https://admin-test.modainteract.com/
https://admin-test.modainteract.com/login
```

for the actual Admin routing proof.

However the submitted runner still executes:

```js
const adminHealth = await request(`${base}/health`, {
  headers: { host: inputs.adminHost }
});
```

This is the exact synthetic Host-override pattern that Attempt 7 was intended
to remove from the Admin boundary proof.

Delete this probe and its result:

```text
adminHostHealth
```

It is redundant.

The accepted Admin proof is:

```text
ordinary/default gateway /admin -> not privileged Admin
real Admin custom domain /       -> anonymous/no privileged content
real Admin custom domain /login  -> Admin login page markers
```

Gateway-local `/health` remains tested once on the actual gateway URL.

Do not replace `adminHostHealth` with `/health` on the Admin custom domain.
`/login` is the deterministic owning-application boundary.

### 2. Make a network failure identify the probe, not the secret material

The runner currently performs all requests and only emits results after every
request completes. Any `fetch()` rejection therefore exits through:

```js
run().catch(...)
```

with only:

```text
fetch failed
```

This is too weak to diagnose a mandatory live assertion.

Update the bounded request helper/call sites so a network-level failure reports
a **non-secret probe identifier**, for example:

```text
gateway-health
ordinary-admin-isolation
admin-root
admin-login
shopify-valid
shopify-invalid-signature
meta-verification
meta-signed-post
```

Acceptable error output:

```text
live request failed: admin-login
live request failed: shopify-valid (UND_ERR_CONNECT_TIMEOUT)
live request failed: meta-verification (AbortError)
```

Do not print:

```text
full request URL
query string
request headers
request body
HMAC/signature
Shopify secret
Meta app secret
Meta verify token
```

If a safe underlying network code is available, such as:

```js
error.cause?.code
```

it may be included.

Do not dump the full error object or stack if it contains request details.

### 3. Do not weaken response assertions

A returned HTTP response is not a network failure.

Keep all existing classification contracts:

```text
gateway /health
ordinary /admin isolation
Admin root/login
Shopify valid signature
Shopify invalid signature
Meta GET verification exact challenge
Meta signed POST
```

If Meta GET returns 403 after the verify-token value has been aligned and the
messaging service redeployed, report that as:

```text
meta-verification: HTTP 403
```

rather than changing the verification contract.

### 4. Meta prerequisite

The developer has already been instructed to align:

```text
ARCH002_TEST_META_VERIFY_TOKEN
==
moda-interact-test-meta-webhook-config.WHATSAPP_VERIFY_TOKEN
```

A Render Environment Group update triggers deployment of linked services in
the observed test environment.

If the developer has already completed that update and
`moda-interact-messaging-test` shows Deployed afterward, do not demand another
manual redeployment.

Never inspect or emit the actual token values.

### 5. Regression coverage

Update focused tests to prove:

```text
Admin custom-domain proof does not require a Host override
no adminHostHealth synthetic probe/result remains
safe probe labels are used for network failures
error classification does not expose URL/query/header/body/secret material
```

Do not duplicate provider implementation tests.

### 6. Live execution

After the narrow correction, run:

```text
npm run validate:arch002-render-test
```

If all mandatory assertions execute and pass:

```text
status: review
```

If a response assertion fails, record the bounded result by assertion name and
HTTP status.

If a network request fails, record the safe probe identifier and safe network
classification supplied by the corrected runner.

Do not return another generic `fetch failed` blocker.

### Validation

Run:

```text
node --test test/render-test-topology.test.js
npm test
npm run typecheck
npm run lint
npm run validate:arch002-render-test
git diff --check
```

Do not modify another repository.

## Architect Dependency Amendment — Dedicated Test Messaging Ingress

Live validation established that Meta/WhatsApp ingress must be tested against
the service-owning public hostname rather than the Shopify/default hostname.

After `ARCH-002-GATEWAY-014` is accepted and deployed, the runner contract is:

```text
ARCH002_TEST_GATEWAY_URL=https://moda-interact-gateway-test.onrender.com
ARCH002_TEST_ADMIN_HOST=admin-test.modainteract.com
ARCH002_TEST_MESSAGING_HOST=messaging-test.modainteract.com
```

`ARCH002_TEST_ADMIN_HOST` and `ARCH002_TEST_MESSAGING_HOST` are **hostnames
only**:

```text
no https:// prefix
no path
no trailing slash
```

Secret input contracts remain unchanged:

```text
ARCH002_TEST_SHOPIFY_API_SECRET
ARCH002_TEST_META_APP_SECRET
ARCH002_TEST_META_VERIFY_TOKEN
```

Do not emit their values.

### Meta/WhatsApp live probes

Construct the Meta public base from the accepted gateway scheme plus:

```text
ARCH002_TEST_MESSAGING_HOST
```

and exercise the accepted Messaging route:

```text
/webhook/whatsapp
```

through:

```text
https://messaging-test.modainteract.com
```

Do not send Meta verification or signed webhook probes through
`app-test.modainteract.com` merely because that hostname also terminates at the
same Render gateway.

### Gateway/application ownership evidence

The system test should prove the externally observable host boundary:

```text
admin host      -> Admin application boundary
messaging host  -> Messaging application boundary
default/app     -> Shopify application boundary
```

It must not require NGINX to manufacture application-level `404` responses for
routes the selected application does not own.

Static proof that the private Messaging service remains `pserv` and that the
public hostname is attached only to the gateway remains part of this task's
Blueprint evidence.

### Blocking rule

Until GATEWAY-014 is architect-accepted and the updated gateway is deployed:

```text
SYSTEM-TEST-006 = blocked
```

Do not claim another live-validation attempt against the superseded ingress
contract.

## Completion Report — Attempt 8

### Status

Blocked

### Environment Tested

The live runner used the deployed Render test environment without emitting
secret or token values. The obsolete synthetic Admin health Host-override
probe was removed, and network failures now identify only a safe probe label.

### Files Changed

- `moda-interact-system-test/src/render-test-topology.js` — add bounded network
  error classification.
- `moda-interact-system-test/scripts/run-arch002-render-test-topology.js` —
  remove the synthetic Admin health probe and identify request failures by
  safe probe name.
- `moda-interact-system-test/test/render-test-topology.test.js` — cover safe
  network error classification.
- This task record.

### Validation Results

- `node --test test/render-test-topology.test.js`: 5 passed.
- `npm run typecheck`: passed.
- `npm run lint`: passed.
- `npm run validate:arch002-render-test`: blocked at `admin-root` with the
  bounded network error `fetch failed`.
- `npm test`: 40 passed, 1 failed, 2 opt-in Docker tests skipped. The failure
  is the pre-existing WhatsApp emulator worker deserialization error and is
  unrelated to this task.
- `git diff --check` for task-scoped files: passed.

### Blockers

The mandatory live validation cannot complete because the direct Admin custom
domain root probe fails with `fetch failed`. Independent endpoint connectivity
was previously observed, but the runner-level Admin request remains
unresolved. Meta verify-token alignment/redeployment also remains an external
prerequisite and was not inspected or emitted.

### Deviations

None.

### Assumptions

No secret or token values were printed, inspected, or recorded.

### Unresolved Issues

Investigate the deployed Admin custom-domain root request and rerun the live
validator after the Meta verify-token prerequisite is confirmed.

### Architectural Concerns

No application or gateway repository was modified. Return the safe
`admin-root` network failure to `moda_architect`.

## Completion Report — Attempt 7

### Status

Blocked

### Environment Tested

The bounded Admin probe was corrected to use the actual Admin custom domain
derived from the gateway URL scheme, with no manual `Host` override. The live
runner was invoked against the deployed test environment without emitting
secret or token values.

### Files Changed

- `moda-interact-system-test/src/render-test-topology.js` — add Admin custom
  domain derivation and bounded anonymous-content classification.
- `moda-interact-system-test/scripts/run-arch002-render-test-topology.js` —
  probe the Admin custom domain directly.
- `moda-interact-system-test/test/render-test-topology.test.js` — cover custom
  domain derivation and anonymous Admin classification.
- This task record.

### Validation Results

- `node --test test/render-test-topology.test.js`: 4 passed.
- `npm test`: 41 passed, 2 opt-in Docker tests skipped.
- `npm run typecheck`: passed.
- `npm run lint`: passed.
- `git diff --check` for task-scoped files: passed.
- `npm run validate:arch002-render-test`: blocked with bounded reason
  `fetch failed` before assertion output.
- Independent non-secret connectivity checks returned HTTP 200 for the
  deployed gateway `/health` endpoint and Admin custom-domain `/login`.

### Blockers

The mandatory live validation did not complete because the runner failed with
`fetch failed` before producing assertion results. The required Meta verify
token alignment with the deployed Render Environment Group also remains an
external prerequisite and was not inspected or emitted.

### Deviations

None.

### Assumptions

The live environment inputs are intended to target the deployed Render test
environment; secret and token values were not printed or recorded.

### Unresolved Issues

The cause of the runner-level `fetch failed` remains unresolved despite both
public endpoints responding to independent bounded connectivity checks. Meta
verification must be rerun after the external verify-token alignment and
messaging-service redeployment are confirmed.

### Architectural Concerns

No owning application, gateway, or messaging repository was modified. Return
the live-runner failure and pending Meta configuration prerequisite to
`moda_architect`.

## Completion Report — Attempt 6

### Status

Blocked

### Environment Tested

The deployed Render test gateway was contacted at the valid configured URL.
No secret or token values were emitted.

### Files Changed

- `moda-interact-system-test/src/render-test-topology.js` — use the accepted
  `moda-interact-test-config` deployment identity and updated error wording.
- `moda-interact-system-test/test/render-test-topology.test.js` — update the
  valid fixture and cover deprecated/missing deployment identity cases.
- This task record.

### Validation Results

- `node --test test/render-test-topology.test.js`: 4 passed.
- `npm test`: 41 passed, 2 opt-in Docker tests skipped.
- `npm run typecheck`: passed.
- `npm run lint`: passed.
- `git diff --check`: passed.
- `npm run validate:arch002-render-test`: reached the deployed gateway but
  failed mandatory Admin and Meta verification assertions. Blueprint,
  gateway health, Admin-host health, ordinary-host `/admin`, Shopify valid
  webhook, Shopify invalid-signature rejection, and signed Meta POST passed.
  Admin root returned 200 instead of the required `/login` redirect, Admin
  `/login` returned 404, and Meta verification returned 403.

### Blockers

The deployed Admin host routing/authentication boundary is not proven: the
configured Admin host did not expose the accepted root-based Admin login
boundary. Meta verification also rejected the supplied verification input.
These deployed-boundary failures require deployment/configuration or owning
service investigation before the mandatory live assertions can pass.

### Deviations

None.

### Assumptions

The configured live inputs are intended to correspond to the deployed Render
test environment; their values were not printed or recorded.

### Unresolved Issues

Admin host routing/login boundary and Meta verification remain unresolved in
the deployed test environment.

### Architectural Concerns

No source changes were made outside `moda-interact-system-test`. Return the
Admin and Meta deployment findings to `moda_architect` and the owning agents.

## Completion Report — Attempt 5

### Status

Blocked

### Environment Tested

No deployed Render environment was contacted. The accepted live runner stopped
at its input gate before network access because `ARCH002_TEST_GATEWAY_URL` is
present but invalid/unparseable as an HTTP(S) URL.

### Files Changed

- This task record only. No implementation files were changed.

### Live Inputs Used

No secret values were emitted or recorded. The required input names were
present, including `ARCH002_TEST_ADMIN_HOST` and the three secret/token names;
only the gateway URL failed validation.

### Scenarios Executed

The existing bounded live validation command was invoked unchanged and failed
closed before any network request.

### Results

`npm run validate:arch002-render-test`: blocked before network access with
`Invalid URL`; no endpoint, secret, or token value was emitted.

`node --test test/render-test-topology.test.js`: 4 passed.

`npm run typecheck`: passed.

`npm run lint`: passed.

`npm test`: 39 passed, 1 failed, 2 skipped. The failure is the existing
`test/whatsapp-emulator.test.js` worker error `Unable to deserialize cloned
data due to invalid or unsupported version`; it is unrelated to this
documentation-only Attempt 5.

`git diff --check` in `moda-interact-system-test`: passed. Workspace-wide
`git diff --check` still reports an unrelated blank line at EOF in
`docs/architecture/ARCH-002-render-production-gateway-infrastructure.md`.

### Blockers

Replace `ARCH002_TEST_GATEWAY_URL` in the execution environment with the
deployed test gateway's valid HTTP(S) URL, then reopen this task as `ready` for
another attempt. Live gateway reachability/routing, provider ingress, Admin
host routing, and deployed-boundary assertions remain unexecuted.

### Deviations

None. The accepted runner was executed unchanged as required.

### Architectural Concerns

None. No owning repository or deployment topology was modified.

## Completion Report — Attempt 4

### Status

Blocked

### Environment Tested

No deployed Render environment was contacted. The local checks validated the
accepted `render.test.yaml` declarations, corrected provider probe contracts,
including the attempt-3 gateway-host and Shopify API-version corrections, and
the live runner's fail-closed input handling. Attempt 4 reached the live input
gate but stopped before network access because the supplied gateway URL was not
parseable as HTTP or HTTPS.

### Files Changed

- `moda-interact-system-test/src/render-test-topology.js` — structured
  Blueprint validation, live-input validation, and response classifiers.
- `moda-interact-system-test/scripts/run-arch002-render-test-topology.js` —
  bounded live Render probes with redacted output and fail-closed prerequisites.
- `moda-interact-system-test/test/render-test-topology.test.js` — focused unit
  coverage for topology, inputs, and boundary classification.
- `moda-interact-system-test/package.json` and `package-lock.json` — `yaml`
  parser dependency and `validate:arch002-render-test` command.
- This task record.

### Live Inputs Used

No secret values were emitted or recorded. All five required input names were
present in the execution environment, but `ARCH002_TEST_GATEWAY_URL` was not a
valid HTTP(S) URL; the other four input names were present.

### Scenarios Executed

Unit classification tests and repository checks executed. The live runner was
invoked but stopped before any network request because its mandatory input gate
failed.

### Results

`node --test test/render-test-topology.test.js`: 4 passed.

`npm test`: 41 passed, 2 existing opt-in Docker tests skipped.

`npm run typecheck`: passed.

`npm run lint`: passed.

`npm run validate:arch002-render-test`: blocked before network access with
`Invalid URL`; no network request, secret, or endpoint value was emitted.

`git diff --check`: passed.

### Blockers

`ARCH002_TEST_GATEWAY_URL` is present but malformed and must be replaced with
the deployed test gateway's valid HTTP(S) URL. The task contract requires
Blocked status instead of substituting local fixtures or treating static
Blueprint checks as live evidence.

### Deviations

Live gateway, Shopify, Meta/WhatsApp, and Admin-host assertions could not run
because the supplied gateway URL failed input validation before any network
request.

Attempt 3 corrected the Meta POST to use the actual gateway URL host and
centralized the accepted Shopify API version as `2026-07`; focused coverage
proves both contracts. Attempt 4 made no implementation changes.

### Architectural Concerns

None. No owning repository or deployment topology was modified.

## Architect Review — Attempt 4

### Review Status

Blocked

### Review Notes

Attempt 3's deterministic implementation is accepted as ready for live
execution.

Architect review confirmed the two attempt-3 corrections:

1. Meta POST traffic now uses the actual host derived from
   `ARCH002_TEST_GATEWAY_URL` rather than an invented Host value.
2. Shopify synthetic webhook metadata now uses the accepted test-owned
   `SHOPIFY_API_VERSION = "2026-07"` contract.

The previously accepted provider-specific HMAC behavior, Shopify metadata and
invalid-signature probe, Admin `/login` proof, Blueprint validation, bounded
timeouts/redaction and fail-closed input gate remain intact.

Repository validation is reported green except for an unrelated pre-existing
workspace documentation whitespace condition noted in the Completion Report.

No further system-test implementation change is requested.

The task remains Blocked solely because the deployed Render test environment
values below were not supplied:

```text
ARCH002_TEST_GATEWAY_URL
ARCH002_TEST_ADMIN_HOST
ARCH002_TEST_SHOPIFY_API_SECRET
ARCH002_TEST_META_APP_SECRET
ARCH002_TEST_META_VERIFY_TOKEN
```

When all five values are available, `moda_architect` should move this same task
back to `ready` for the next execution attempt. That attempt should run the
existing live validation unchanged and return to `review` only when all
mandatory deployed assertions execute successfully.


## Architect Review — Current

### Review Status

Ready for Attempt 5

### Review Notes

No implementation correction is requested.

Attempt 4 proved the fail-closed live-input gate works as intended. The
malformed `ARCH002_TEST_GATEWAY_URL` has now been corrected externally.

Execute the existing live runner unchanged and return to `review` only after
the mandatory deployed assertions have actually executed.


## Architect Review — Attempt 6

### Review Status

Changes Requested / Ready

### Review Notes

The URL itself is now proven valid inside the Copilot execution environment.

The only authorized implementation change for Attempt 6 is to update
SYSTEM-TEST-006's stale test environment-group identity check from
`moda-observability-test` to the architect-accepted
`moda-interact-test-config` contract and update its bounded unit fixture.

After that correction, execute the live runner in the same attempt.

Do not modify gateway/application repositories.


## Architect Review — Attempt 7

### Review Status

Changes Requested / Ready

### Review Notes

Attempt 6 produced useful live evidence and is not rejected wholesale.

Accepted live evidence from Attempt 6:

```text
gateway health
ordinary-host /admin isolation
Shopify signed ingress
Shopify invalid-signature rejection
Meta signed POST
```

The Admin failure is caused by the system-test probe addressing the Render
`onrender.com` URL with a synthetic Host override instead of calling the real
Admin custom domain.

Correct that bounded probe in SYSTEM-TEST-006 only.

The Meta GET 403 is not authorization to change the Meta verification contract.
Align the task input `ARCH002_TEST_META_VERIFY_TOKEN` with the deployed
`WHATSAPP_VERIFY_TOKEN`, redeploy messaging after any group change, and rerun.


## Architect Review — Attempt 8

### Review Status

Changes Requested / Ready

### Review Notes

Attempt 7 is not accepted because the submitted live runner still performs the
obsolete Admin synthetic Host-override health request:

```text
gateway onrender.com /health
+ Host: admin-test.modainteract.com
```

That request must be removed now that the direct Admin custom-domain root/login
probes exist.

The generic `fetch failed` blocker is also not sufficient evidence because it
does not identify which mandatory probe experienced a network-level failure.

Add only safe per-probe failure identification, preserve all response
assertions, and rerun the live test.

---

# Architect Review — Developer Live Validation After GATEWAY-014 Completion

## Decision

**Changes Requested — same task, next claim Attempt 9**

The developer executed the task-owned live validation wrapper against the
deployed Render test environment.

Recorded evidence:

```text
Task: ARCH-002-SYSTEM-TEST-006
Git HEAD: ad8dde78ef55bbed42368e35d4f6dff8ccc31520
Started:  20260904T145611Z
Finished: 20260904T145616Z
Exit:     1
```

The full sanitized live result was:

```json
{
  "passed": false,
  "results": {
    "blueprint": {
      "valid": true,
      "errors": []
    },
    "gatewayHealth": {
      "passed": true,
      "status": 200,
      "requestIdPresent": true
    },
    "ordinaryHostAdmin": {
      "passed": true,
      "status": 404
    },
    "adminAnonymous": {
      "passed": false,
      "status": 308,
      "loginPath": "/"
    },
    "adminLogin": {
      "passed": false,
      "status": 308
    },
    "shopifyWebhook": {
      "passed": false,
      "status": 404,
      "validSignature": true
    },
    "invalidShopifyWebhook": {
      "passed": false,
      "status": 404,
      "validSignature": false
    },
    "metaVerification": {
      "passed": false,
      "status": 404
    },
    "metaWebhook": {
      "passed": false,
      "status": 404
    }
  }
}
```

This is primarily a **SYSTEM-TEST-006 runner/input defect**, not evidence that
the deployed App/Admin/Messaging services are broken.

The live gateway itself had already been independently proven after
GATEWAY-014 Attempt 8:

```text
gateway /health  -> 200
App root         -> 200
Admin root       -> 200
Admin /login     -> 200
Messaging root   -> 200
```

---

## Finding 1 — Admin Host Input Was Malformed

The developer validation report recorded:

```text
admin_host=admin-test.modainteract.com/
                                      ^
```

`ARCH002_TEST_ADMIN_HOST` is a hostname, not a URL/path.

The current helper:

```js
function createAdminBaseUrl(gatewayUrl, adminHost) {
  const gateway = new URL(gatewayUrl);
  return `${gateway.protocol}//${adminHost}`;
}
```

therefore generated a URL with an extra slash before `/login`, producing the
observed `308` redirects.

### Required correction

Treat all public-host inputs as **hostnames only**.

The canonical test values are:

```text
ARCH002_TEST_APP_HOST=app-test.modainteract.com
ARCH002_TEST_ADMIN_HOST=admin-test.modainteract.com
ARCH002_TEST_MESSAGING_HOST=messaging-test.modainteract.com
```

Reject malformed values containing:

```text
scheme
path
query
fragment
trailing slash
```

rather than silently probing a malformed URL.

The task-specific developer wrapper must also stop inheriting stale values for
these known non-secret topology constants. It should set/export the canonical
ARCH-002 test hosts explicitly for this task.

Do not print secret values.

---

## Finding 2 — App and Messaging Host Inputs Are Not Consumed By The Runner

The current `INPUT_NAMES` still contains only:

```text
ARCH002_TEST_GATEWAY_URL
ARCH002_TEST_ADMIN_HOST
ARCH002_TEST_SHOPIFY_API_SECRET
ARCH002_TEST_META_APP_SECRET
ARCH002_TEST_META_VERIFY_TOKEN
```

It does **not** require/read:

```text
ARCH002_TEST_APP_HOST
ARCH002_TEST_MESSAGING_HOST
```

even though the accepted GATEWAY-014 architecture is:

```text
App Host       -> App
Admin Host     -> Admin
Messaging Host -> Messaging
```

### Required correction

Add both host inputs to the mandatory live input contract:

```text
ARCH002_TEST_APP_HOST
ARCH002_TEST_MESSAGING_HOST
```

and expose normalized values from `getLiveInputs()`.

A small generic helper is preferred, e.g. conceptually:

```text
createPublicBaseUrl(gatewayUrl, host)
```

so App/Admin/Messaging base URLs are constructed consistently from the gateway
protocol plus each canonical custom hostname.

---

## Finding 3 — Shopify Probes Still Use The Native Render Gateway Host

The current runner creates Shopify headers with:

```js
new URL(base).host
```

and sends:

```js
POST `${base}/webhooks`
```

where `base` is:

```text
https://moda-interact-gateway-test.onrender.com
```

After GATEWAY-014, that native/default gateway Host is **not** the App Host.

The 404 result therefore does not test Shopify HMAC behaviour at all; it proves
the request was not sent through the accepted App ingress.

### Required correction

Build:

```text
appBase = protocol + ARCH002_TEST_APP_HOST
```

and send both valid and invalid Shopify probes to:

```text
https://app-test.modainteract.com/webhooks
```

The generated Shopify `Host` metadata must also correspond to the App public
host.

Preserve the already-correct:

```text
base64 Shopify HMAC
2026-07 API version
synthetic shop
synthetic webhook ID
invalid-signature comparison
```

Do not modify the Shopify application.

---

## Finding 4 — Meta Probes Still Use The Native Render Gateway Host

The current runner sends Meta GET/POST to:

```text
`${base}/webhook/whatsapp`
```

with:

```text
Host = new URL(base).host
```

That is the obsolete/default-host ingress model.

GATEWAY-014 established the dedicated Messaging public host:

```text
messaging-test.modainteract.com
```

The resulting live `404` values are therefore expected from the wrong Host.

### Required correction

Build:

```text
messagingBase = protocol + ARCH002_TEST_MESSAGING_HOST
```

and send both:

```text
GET  /webhook/whatsapp?...verification query...
POST /webhook/whatsapp
```

to:

```text
https://messaging-test.modainteract.com
```

Do not route Meta through:

```text
moda-interact-gateway-test.onrender.com
app-test.modainteract.com
```

Preserve:

```text
verify token secrecy
challenge equality check
Meta sha256=<hex> signature
bounded empty synthetic WhatsApp payload
```

---

## Finding 5 — Native Gateway Assertions Remain Separate

Keep these probes on:

```text
ARCH002_TEST_GATEWAY_URL=https://moda-interact-gateway-test.onrender.com
```

because they validate the gateway itself:

```text
GET /health
ordinary/default Host does not expose Admin
```

Do not move gateway-local health to a custom application hostname.

`ordinaryHostAdmin` already passed with `404` in the failed run and should be
preserved.

---

## Required Canonical Probe Matrix

Attempt 9 must make the live runner explicit:

```text
Gateway-local:
  https://moda-interact-gateway-test.onrender.com/health

Ordinary/default-host Admin rejection:
  https://moda-interact-gateway-test.onrender.com/admin

App/Shopify:
  https://app-test.modainteract.com/webhooks

Admin:
  https://admin-test.modainteract.com/
  https://admin-test.modainteract.com/login

Messaging/Meta:
  https://messaging-test.modainteract.com/webhook/whatsapp
```

The public Host chooses the service; the path belongs to that service.

---

## Unit Coverage Required

Update `test/render-test-topology.test.js` to prove at minimum:

```text
APP_PUBLIC test host is mandatory;
ADMIN_PUBLIC test host is mandatory;
MESSAGING_PUBLIC test host is mandatory;

hostname-only values are accepted;

admin-test.modainteract.com/ is rejected as malformed;

App base URL is app-test.modainteract.com;
Admin base URL is admin-test.modainteract.com;
Messaging base URL is messaging-test.modainteract.com;

Shopify probe construction cannot regress to the native Render gateway host;

Meta probe construction cannot regress to the native Render gateway host.
```

Do not require live network access in unit tests.

---

## Developer Validation Wrapper

Update:

```text
scripts/system-test-006-developer-validation.sh
```

so this task's known non-secret topology values are set canonically rather than
inherited from stale shell state:

```text
ARCH002_TEST_GATEWAY_URL=https://moda-interact-gateway-test.onrender.com
ARCH002_TEST_APP_HOST=app-test.modainteract.com
ARCH002_TEST_ADMIN_HOST=admin-test.modainteract.com
ARCH002_TEST_MESSAGING_HOST=messaging-test.modainteract.com
```

Continue to prompt silently for:

```text
ARCH002_TEST_SHOPIFY_API_SECRET
ARCH002_TEST_META_APP_SECRET
ARCH002_TEST_META_VERIFY_TOKEN
```

Continue redacting secret literal and URL-encoded forms from captured output.

---

## Validation Ownership

Luna performs only bounded repository validation:

```bash
npm test
npm run typecheck
npm run lint
git diff --check
```

Luna MUST NOT run:

```bash
npm run validate:arch002-render-test
```

against the live Render environment.

The developer owns the live execution after Attempt 9 returns to review:

```bash
./scripts/system-test-006-developer-validation.sh
```

PASS:

```text
provide report.md to moda_system_test;
agent records evidence;
agent does not rerun live test;
task returns to review.
```

FAIL or BLOCKED:

```text
provide report.md + full.log + latest system-test workspace ZIP to moda_architect.
```

---

## Attempt 9 Acceptance Criteria

- [x] task requires App/Admin/Messaging public host inputs explicitly.
- [x] hostname inputs reject schemes/paths/trailing slash.
- [x] developer wrapper exports canonical non-secret host values.
- [x] gateway health stays on native Render gateway URL.
- [x] ordinary/default-host Admin rejection stays on native gateway URL.
- [x] Shopify valid/invalid probes use App custom host.
- [x] Admin probes use Admin custom host.
- [x] Meta verification/signed POST use Messaging custom host.
- [x] no provider secret is logged or committed.
- [x] Shopify signing/API-version behavior remains unchanged.
- [x] Meta signing/challenge behavior remains unchanged.
- [x] unit tests cover host-selection regression.
- [ ] repository test/typecheck/lint pass.
- [x] Luna does not execute live Render validation.
- [x] Completion Report distinguishes the failed Attempt-8 live evidence from
      the Attempt-9 implementation correction.
- [x] task returns to review for developer execution.
- [x] no agent commit/push.

---

## Completion Report — Attempt 10

### Status

Ready for Review

### Files Changed

The Attempt 9 validator implementation and focused tests were already present in
the working tree when Attempt 10 was claimed. Attempt 10 updated this task
document and validated the existing implementation. The relevant system-test
files are:

- `moda-interact-system-test/src/render-test-topology.js`
- `moda-interact-system-test/scripts/run-arch002-render-test-topology.js`
- `moda-interact-system-test/scripts/system-test-006-developer-validation.sh`
- `moda-interact-system-test/test/render-test-topology.test.js`
- this task document

### Work Completed

Confirmed the deterministic deployed-topology validator uses the canonical
App, Admin and Messaging public hosts while keeping gateway-local health and
ordinary-host Admin rejection on the native gateway URL. Confirmed provider-
specific Shopify base64 HMAC/API-version metadata, Meta hexadecimal HMAC
metadata, strict hostname-only input validation, bounded Admin login
classification, and secret-safe network-error classification.

The developer wrapper exports the known non-secret test topology values,
prompts silently for the three required secrets, redacts literal and encoded
secret values, and preserves the live validator exit code. No gateway or
application repository was modified.

### Validation Results

Agent-owned checks passed:

```text
node --test test/render-test-topology.test.js
  5 passed, 0 failed
npm run typecheck
  passed
npm run lint
  passed
git diff --check
  passed
```

The declared full `npm test` command was also run. It reported `44 tests`,
`19 passed`, `23 failed`, and `2 skipped`; the failures are the known
gateway-migration baseline where blueprint tests still open the removed
`moda-interact-gateway/nginx/nginx.conf.template`. The focused topology suite
passed independently, and no Attempt 10 change introduced those failures.

The live Render validator was not run by the agent. The developer-owned
command for live evidence is:

```bash
cd moda-interact-system-test
./scripts/system-test-006-developer-validation.sh
```

### Deviations

The full repository test command remains red because of the pre-existing NGINX
template path baseline described above. Live deployed assertions remain pending
developer execution under the live-validation policy.

### Assumptions

The accepted Attempt 9 validator implementation and its current untracked
working-tree files are the intended system-test changes for this task.

### Unresolved Issues

Developer live validation is still required. The known unrelated blueprint-test
baseline should be resolved by the owning migration work rather than by this
system-test task.

### Architectural Concerns

None. The validator continues to consume the gateway/application contracts and
does not implement gateway routing or expose private services.

---

# Architect Review — Attempt 10 Developer Live Evidence

## Decision

**Changes Requested — same task, Ready for Attempt 11**

The developer-owned live run at:

```text
20260904T152534Z
Git HEAD ad8dde78ef55bbed42368e35d4f6dff8ccc31520
```

produced:

```text
blueprint                 PASS
gateway /health           PASS 200
ordinary gateway /admin   PASS 404
Admin root                PASS 200
Admin /login              FAIL 200
Shopify valid HMAC        PASS 200
Shopify invalid HMAC      PASS 401
Meta verification GET     FAIL 403
Meta signed POST          PASS 200
```

This is substantial progress. Host routing is now correct for all three public
application hosts.

## Finding A — Admin `/login` Is a Validator False Negative

The live response is HTTP `200`.

The current request helper discards all response body content after the first:

```text
2,000 bytes
```

before `classifyAdminLogin()` looks for:

```text
Platform Admin
Continue with Google
```

Prior direct developer evidence proves the real Next.js `/login` response
contains both accepted markers later in the streamed HTML, after the initial
loading/streaming shell.

Attempt 11 must therefore correct only the bounded response capture. It must not
weaken the Admin marker assertion and must not modify the Admin application.

Accepted direction:

```text
bounded response capture materially larger than 2 KB
+
no response body emitted to logs/reports
+
focused regression proving markers after byte 2,000 are retained
```

## Finding B — Meta GET `403` Is Not a Runner/Host-Routing Defect

The same run returned:

```text
Meta signed POST -> 200
Meta GET verify  -> 403
```

Both use:

```text
https://messaging-test.modainteract.com/webhook/whatsapp
```

This proves the Messaging Host/path is reachable and the signed POST contract is
working.

Do **not** change the verification route, query names, success status, or exact
challenge assertion.

A `403` verification response remains evidence that the supplied:

```text
ARCH002_TEST_META_VERIFY_TOKEN
```

does not match the value currently used by the deployed Messaging service:

```text
moda-interact-test-meta-webhook-config.WHATSAPP_VERIFY_TOKEN
```

or that the deployed Messaging revision has not yet picked up the aligned value.

The developer must align those values outside source control before the next
live execution. Never print or record either token.

## Required Reusable Naming Migration

Attempt 10 still uses the architecture-specific permanent names:

```text
validate:arch002-render-test
run-arch002-render-test-topology.js
system-test-006-developer-validation.sh
```

Attempt 11 must complete the previously accepted reusable naming migration:

```text
npm run validate:render:test

scripts/validate-render-deployment.js --environment test

scripts/validate-render-test.sh

scripts/developer-validation.sh <TASK_ID> -- <command>
```

Architecture IDs belong in validation evidence metadata, not in the permanent
Render validator executable name.

The developer-owned command after Attempt 11 returns to review is:

```bash
./scripts/developer-validation.sh \
  ARCH-002-SYSTEM-TEST-006 \
  -- ./scripts/validate-render-test.sh
```

The agent MUST NOT execute this command.

## Agent-Owned Validation

Run only:

```bash
node --test test/render-test-topology.test.js
npm run typecheck
npm run lint
git diff --check
```

The current full `npm test` baseline contains unrelated stale production-
readiness tests that still open the removed NGINX template after GATEWAY-014
migrated the gateway to HAProxy.

That repository-wide migration debt is tracked separately by:

```text
ARCH-002-SYSTEM-TEST-010
```

It does not authorize weakening or deleting unrelated tests inside this task.

## Attempt 11 Acceptance Criteria

- [x] reusable command is `npm run validate:render:test`.
- [x] reusable Node entrypoint is `scripts/validate-render-deployment.js`.
- [x] secure test bootstrap is `scripts/validate-render-test.sh`.
- [x] generic evidence wrapper remains `scripts/developer-validation.sh`.
- [x] no active package command uses `validate:arch002-render-test`.
- [x] Admin response capture retains accepted markers beyond byte 2,000.
- [x] Admin `/login` still requires HTTP 200 + both accepted markers.
- [x] Meta verification remains HTTP 200 + exact challenge.
- [x] Meta POST signing contract remains unchanged.
- [x] focused topology tests pass.
- [x] typecheck and lint pass.
- [x] git diff --check passes.
- [x] agent does not run deployed Render validation.
- [x] no agent commit/push.
- [x] task returns to review for developer-owned live execution.

---

## Completion Report — Attempt 11

### Status

Ready for Review

### Files Changed

- `moda-interact-system-test/package.json`
- `moda-interact-system-test/src/render-test-topology.js`
- `moda-interact-system-test/scripts/validate-render-deployment.js`
- `moda-interact-system-test/scripts/validate-render-test.sh`
- `moda-interact-system-test/scripts/developer-validation.sh`
- `moda-interact-system-test/test/render-test-topology.test.js`
- this task document

Historical task-specific validator names remain only in prior `.validation`
evidence; no active package command uses them.

### Work Completed

Completed the reusable Render test validator naming migration. The active
package command now invokes `scripts/validate-render-deployment.js` through
`npm run validate:render:test`. Secure test input bootstrap is isolated in
`scripts/validate-render-test.sh`, while generic evidence capture remains
`scripts/developer-validation.sh <TASK_ID> -- <command>`.

Increased bounded response capture to retain streamed Admin login markers beyond
the former 2 KB limit without emitting response bodies to logs or reports. The
Admin classifier still requires HTTP 200 plus both accepted login markers.
Meta verification and signed POST contracts remain unchanged.

### Validation Results

```text
node --test test/render-test-topology.test.js
  6 passed, 0 failed
npm run typecheck
  passed
npm run lint
  passed
git diff --check
  passed
active package command check
  validate:render:test -> node scripts/validate-render-deployment.js --environment test
  no validate:arch002-render-test script present
```

The agent did not execute the deployed Render validator. The developer-owned
command after review is:

```bash
cd moda-interact-system-test
./scripts/developer-validation.sh \
  ARCH-002-SYSTEM-TEST-006 \
  -- ./scripts/validate-render-test.sh
```

The previous developer evidence showed Meta verification `403` while the
Messaging signed POST passed; the report correctly identified that as a
deployed verify-token alignment issue, not a runner routing defect. Do not
record or print either token.

### Deviations

None in Attempt 11. Live execution remains developer-owned by policy.

### Assumptions

Historical `.validation` records are retained as evidence and are not active
commands or migration regressions.

### Unresolved Issues

Developer live validation remains pending. Its Meta verification input must
match the deployed test Messaging configuration before treating that assertion
as passed.

### Architectural Concerns

None. The changes remain within the system-test repository and do not implement
gateway routing or expose private services.


---

## Architect Acceptance — 2026-09-04

### Decision

`moda_architect` accepts `ARCH-002-SYSTEM-TEST-006` as **Complete** for the
current Render deployment-topology milestone.

The latest developer-owned live evidence established:

```text
Blueprint / topology             PASS
Gateway health                   PASS
Ordinary gateway /admin          PASS
Admin anonymous root             PASS
Admin /login                     PASS
Shopify valid webhook            PASS
Shopify invalid webhook          PASS
Meta signed POST                 PASS
Meta verification GET            DEFERRED (observed 403)
```

### Deferred WhatsApp verification

The Meta verification GET `403` is safe to ignore **only as an acceptance gate
for this task**. WhatsApp integration has not yet reached the final end-to-end
acceptance stage. Do not change or weaken the verification route, expected HTTP
`200`, exact challenge assertion, token handling, gateway routing, or test merely
to produce a green result. Do not claim that Meta verification passed.

The existing assertion must remain available for a subsequent WhatsApp/Messaging
integration system test, where verify-token alignment and the complete inbound
WhatsApp flow will be validated deliberately.

### What this task proves

For the current milestone, the accepted evidence is sufficient to establish that
the Render-deployed public/private topology and ingress boundaries required to
continue Shopify checkout validation are operational. In particular, the public
gateway is reachable, Shopify host/path routing is functional, valid Shopify
webhook authentication is accepted, invalid authentication is rejected, and the
private application deployment is reachable through the approved ingress path.

### What this task does not prove

This task does **not** claim that the complete asynchronous checkout-processing
flow has been proven on Render. That remains the next active investigation:

```text
Shopify checkout event
        ->
moda-interact gateway/application ingress
        ->
BullMQ / Redis publication
        ->
moda-interact-background consumption
        ->
checkout event processing
```

The immediate platform objective is to establish this flow before treating the
not-yet-complete WhatsApp integration as a release gate.

### Agent instruction

Do not reopen `SYSTEM-TEST-006`, rerun the live validator solely to reproduce the
known Meta `403`, or modify runtime code as part of this completed task. Preserve
the existing validation evidence. Any further Shopify-to-background Render
investigation must be performed under a separate architect-authorised task or
overlay.

### Final status

```text
ARCH-002-SYSTEM-TEST-006
Status: Complete
Architect decision: Accepted with deferred WhatsApp verification
```
