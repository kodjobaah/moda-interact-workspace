---
id: ARCH-020-GATEWAY-001
architecture_id: ARCH-020
title: Deploy Commerce topology through the Render Blueprint
task_kind: implementation
domain: gateway
repository: moda-interact-gateway
assigned_agent: moda_gateway
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 180
executor: null
claimed_at: null
attempt: 4
depends_on:
  - ARCH-020-COMMERCE-002
  - ARCH-020-BACKGROUND-001
  - ARCH-020-COMMERCE-008
  - ARCH-020-COMMERCE-011
  - ARCH-020-COMMERCE-013
  - ARCH-020-COMMERCE-017
  - ARCH-020-COMMERCE-018
  - ARCH-020-COMMERCE-019
enables:
  - ARCH-020-COMMERCE-012
  - ARCH-020-SYSTEM-TEST-001
  - ARCH-020-GATEWAY-003
created: 2026-09-20
updated: 2026-09-22
---

# Deploy Commerce topology through the Render Blueprint

## Architecture

Architecture ID: ARCH-020.

Architecture document: docs/architecture/ARCH-020-commerce-agent-studio-mcp-capabilities.md.

Coordinator: moda_architect. Read the complete parent architecture and relevant dependency/contract tasks. Execution handoff: docs/architecture/ARCH-020-implementation-handoff.md.

## Objective

Codify the new independent Commerce service and its private MCP/public staff routing.

## Context

Merchant-selected capabilities should drive WhatsApp CommerceAgent behaviour through a separate Next.js MCP server with a team-only Studio. Production conversation admission, ordering, model hosting and delivery remain in Background. This is a pre-production breaking rollout, with no implicit permission to delete durable data.

Task definition is on local workspace main by the developer's explicit 2026-09-20 review request. It is not a claim, task-branch materialisation or implementation approval. All execution fields remain unclaimed.

## Scope

Gateway render.yaml, reverse proxy rules, secret-name declarations, health/timeout and deployment documentation.

## Out of Scope

Other repositories' implementation, unrelated refactoring, automatic execution of enabled tasks, live deployment, main integration/push and changes to billing prices/merchant entitlements. No cart/order/discount mutation, WhatsApp sending from Commerce, arbitrary executable code or arbitrary-host HTTP endpoints; C14 validated read-only GraphQL definitions are explicitly permitted. No duplicate discount catalogue/merchant configuration system. Shared indexes and architecture reconciliation remain architect-owned.

## Requirements

Follow the parent architecture's tenant/policy/revision contracts and the assigned logical owner. Preserve unrelated changes. Read repository-local AGENTS.md if present. Commerce consumes the canonical database through its nested database/ Git submodule; schema and migrations belong to moda_database. For consumers, use actual accepted and published dependency revisions, not copied task snapshots or hypothetical versions.

## Work Items

- [x] Apply C7.1 hosted auth configuration: Google-only AUTH_* variables and a non-development DEPLOYMENT_ENVIRONMENT_NAME. No Render service enables the local SUPER_ADMIN override; production runtime plus development override must fail closed. Keep the private MCP assertion boundary independent of Studio auth.

- [x] Allow exactly the C15/U01–U14 UI routes and documented studio/auth methods; add /features, /tools, /explore and /shops index plus detail routes. Discovery endpoints remain staff-authorized, not a public MCP proxy.
- [x] Provision the COMMERCE-011 supervised stdio runtime/schema artifacts in the Commerce build, no extra port/service/credentials. Add optional server-only ADMIN_ORIGIN for Admin navigation. Redis is required for discovery rate limits. Child failure degrades docs search without disabling live MCP or local schema editing.

- [x] Inspect accepted Commerce build/start/port/health contracts and recursive database generation requirements before defining the service.
- [x] Add a private Render service for Commerce and an authenticated team UI host through the public gateway; block public MCP routes, transport aliases and normalised/encoded variants. Use an explicit staff UI/auth route allowlist rather than a blanket proxy.
- [x] Wire Background private MCP URL and separate staff OAuth, database, assertion-verification/signing and preview-model secret names plus existing platform Redis connectivity for bounded cross-replica preview deduplication. No new Redis service is required. Only Background receives production signing keys; Commerce receives verification keys. Other services and browser/admin identities are not authorised live MCP callers.
- [x] Configure bounded streaming/body/timeout behaviour compatible with the selected MCP client/server and environment identity.
- [x] Document additive migration ordering, affected-worker pause/resume, initial release publication, resource preservation and coordinated pre-production rollback.

## Interfaces / Contracts

Canonical moda-interact-gateway/render.yaml; actual repository/host identity supplied during setup, not guessed.

### Implementation guidance

Binding companion: [ARCH-020 implementation contracts](../../../architecture/ARCH-020-implementation-contracts.md), sections **C3, C5, C9, C10**. These are required acceptance inputs, not optional examples.

Use canonical render.yaml and actual provisioned repository/Studio host inputs. Wire the messaging worker-only signing keys and Commerce verification keys. Explicit proxy allowlist covers server-action POSTs, auth callbacks, UI/static assets but never MCP; reject ambiguous encoded paths before upstream. No separate Redis service. Deliver docs/commerce-deployment.md with exact command/health/private/public expectations.

### Deterministic review clarification

Apply C9.1 exact preview routes/methods to the public Studio allowlist; no
blanket /api/studio proxy. C10 includes AUTH_URL matching COMMERCE_STUDIO_ORIGIN.
Wire WHATSAPP_TRANSCRIPTION_PROVIDER=groq|openai on the messaging worker;
omitted/blank selects groq, other values fail closed. GROQ_TRANSCRIPTION_MODEL
defaults to whisper-large-v3-turbo and uses GROQ_API_KEY. OpenAI selection uses
OPENAI_TRANSCRIPTION_MODEL (default gpt-4o-mini-transcribe) and messaging-only
WHATSAPP_OPENAI_API_KEY, never translation-worker OPENAI_API_KEY. Model IDs are
1–128 characters, start alphanumeric and contain only alphanumeric, dot, underscore
or hyphen. No automatic provider/model fallback. Test and production settings are
independent. Validate blueprint wiring without paid provider calls or deployment;
record provider-quality evidence separately. Reconcile these names against the
accepted BACKGROUND-001 handoff before publishing configuration.

Preview MODEL wiring is separately fixed by C10/COMMERCE-033. Declare
`COMMERCE_PREVIEW_ENABLED`, `COMMERCE_PREVIEW_PROVIDER`,
`COMMERCE_PREVIEW_MODEL` and secret `COMMERCE_PREVIEW_API_KEY` on the Commerce
service; never expose them as `NEXT_PUBLIC_*`. Test/development hosted configuration is
`COMMERCE_PREVIEW_ENABLED=true`, `COMMERCE_PREVIEW_PROVIDER=groq`,
`COMMERCE_PREVIEW_MODEL=openai/gpt-oss-20b`; the API key is an external Render secret.
Production provider/model are independently configurable. Allowed providers are exactly
`openai|groq`; no fallback and no configurable preview base URL. Gateway only wires the
variables; Commerce owns provider HTTP behavior. No paid provider call is required for
Blueprint acceptance.

### Required evidence

Use existing gateway validation shell/config tooling (repository has no package.json; do not invent npm build). Add deterministic host/path/method fixtures with stub upstream; include direct private calls missing credentials and each public encoded/alias MCP attempt. Deployment credentials/real hosts remain external inputs.

For this task, record a requirement-to-fixture matrix with expected side effects, actual commands and results in the Completion Report. Do not implement another repository's changes to bypass a dependency.

## Dependencies

- ARCH-020-COMMERCE-002
- ARCH-020-BACKGROUND-001
- ARCH-020-COMMERCE-008
- ARCH-020-COMMERCE-011
- ARCH-020-COMMERCE-013
- ARCH-020-COMMERCE-017
- ARCH-020-COMMERCE-018
- ARCH-020-COMMERCE-019

All dependencies must be Complete and architect-accepted before execution.

## Enables

- ARCH-020-COMMERCE-012
- ARCH-020-SYSTEM-TEST-001
- ARCH-020-GATEWAY-003

- ARCH-020-SYSTEM-TEST-001

## Acceptance Criteria

- [x] Coordinate BACKGROUND-001 A2/C6.3 transcription configuration: the exact provider/model selector names, values/defaults and credentials below must reach the messaging worker in independent test/production settings. Preserve Groq; OpenAI is explicit, with gpt-4o-mini-transcribe the OpenAI-only default. No automatic fallback. Existing translation-worker OpenAI group is not messaging configuration; scope secrets narrowly rather than importing unrelated translation settings. Background owns any evidence-required conversion/image dependency; Gateway verifies runtime/resources and records explicit rollout/rollback. Configuration checks do not require paid live transcription.

- [x] Public staff can traverse all pages and authenticated discovery operations, but cannot access /api/mcp or invoke arbitrary developer/CLI tools; child process receives no production credentials.

- [x] Blueprint references the real new repository and correct commands; no credentials or invented remote/host are committed.
- [x] Browser-accessible staff routes work through the gateway while public MCP requests are denied and private MCP accepts only Background service assertions. Another private-network service without that identity and an administrator browser session are both denied.
- [x] Fresh builds initialise database recursively; service startup does not run migrations or destroy durable resources.

## Validation

- [x] Run local Blueprint/proxy syntax and route fixture checks covering POST/GET/OPTIONS, encoded/trailing-path/alias attempts, direct private calls without Background identity and authenticated staff UI access and git diff --check.
- [x] Provide exact developer-owned deployment/smoke commands with expected private/public/health outcomes; no live deployment is implied by task definition.

Use package.json commands actually provided by the repository. New Commerce scripts and test fixtures are deliverables, not claims that they exist today. Follow docs/agent-validation-execution-policy.md and docs/agent-live-validation-execution-policy.md. Separate local evidence from pending developer-owned long/live validation; required evidence must exist before acceptance.

## Stop Condition

After scoped work and agent-owned checks, update this task's execution/report fields, publish task-owned mirrored branches and return to review. Record exact pending developer validation where applicable. Stop; do not begin enabled tasks or mark your own task Complete. Publication tasks stop after release mechanics. System tests require explicit developer invocation even after becoming Ready.

## Implementation Notes

Normal execution uses /moda-task and scripts/start-agent-task.py preparation, dedicated parent and implementation worktrees, synchronization and recursive submodule initialisation. Follow docs/agent-vcs-ownership-policy.md, docs/agent-worktree-isolation-policy.md and docs/task-definition-materialization.md. The main-only exception applies to this review draft, not task execution. The COMMERCE route is registered in this packet; its real repository must be provisioned before execution preparation.

## Completion Report

### Status

Attempt 4 — Ready for Review (2026-09-22). A3-R1 is implemented as a runbook-only
correction and validated locally. A2-R3/U15/U16 remain assigned to GATEWAY-003.
No live Render deployment, browser OAuth completion, private assertion
verification, paid provider call, or production resource mutation was performed.

### Files Changed

The Attempt 4 implementation change is limited to
`moda-interact-gateway/docs/commerce-deployment.md`. The runbook now supplies
valid externally captured C5 MCP JSON-RPC input, valid C15 discovery payloads
and `apiVersion=2026-07`, concrete matching UUID/payload inputs for C9.1 preview
routes, and fail-fast guards for every required external smoke variable. The
accepted Attempt 3 Blueprint/proxy topology and A2-R1/A2-R2 deployment-input and
authentication corrections are preserved.

### Work Completed

Commerce uses the accepted recursive build contract, `PORT`, `/health/live`,
and no startup migration. The gateway exposes the Studio host through explicit
page/auth/asset and C9.1 preview families. `/api/mcp`, `/mcp`, trailing,
encoded-separator, duplicate-separator and dot-segment variants are denied
before proxying. Background-only MCP URL/signing configuration and Commerce-only
verification keys are separated. Test and production preview/transcription
settings are independent; Groq is retained and OpenAI is explicit. The hosted
smoke contract requires `COMMERCE_INTERNAL_SERVICE_ADDRESS`,
`COMMERCE_MCP_URL`, `COMMERCE_PUBLIC_HOST`, `GATEWAY_PUBLIC_ORIGIN`,
`STUDIO_COOKIE_HEADER`, `STUDIO_NEXT_ACTION_ID`, `STUDIO_NEXT_ACTION_BODY`, six
externally supplied Background assertions, one valid C5 request body, three
discovery bodies, and concrete matching preview IDs/bodies. The gateway does
not generate or sign tokens.

### Validation Results

| Requirement | Command / fixture | Result |
|---|---|---|
| A3-R1 runbook smoke contract | `docs/commerce-deployment.md` review | Valid C5 body reused for missing/valid/wrong-claim assertions; valid discovery bodies and `apiVersion=2026-07`; concrete matching preview IDs/bodies; all required guards present |
| Render topology and credential wiring | `bash tests/validate-render-blueprints.sh` | Passed |
| Legacy and Commerce negative mutations | `bash tests/validate-render-blueprints-negative.sh` | Passed; 48 meaningful mutations rejected for expected reasons, including all seven new A2-R1 classes |
| Routing, headers, body integrity, timeouts and MCP variants | `bash tests/run-tests.sh` (Attempt 3 executor evidence; not rerun for Markdown-only Attempt 4) | 150 passed, 0 failed |
| HAProxy rendering | Docker build plus entrypoint `haproxy -c` (Attempt 3 executor evidence) | Configuration valid |
| Shell syntax | `bash -n docker/entrypoint.sh tests/run-tests.sh tests/validate-render-blueprints.sh tests/validate-render-blueprints-negative.sh` | Passed |
| Whitespace | `git diff --check` | Passed |

The Docker suite covers every C15 page/detail route with GET/HEAD and Server
Action POST checks, NextAuth GET/POST, all four discovery methods, all seven
C9.1 preview method combinations and wrong-method cases, the 131072/131073
byte Commerce boundary, all required public MCP alias/encoded/normalisation
attempts, and legacy provider-body/header behavior.

### Deviations

`COMMERCE_PUBLIC_HOST`, `COMMERCE_STUDIO_ORIGIN` and `AUTH_URL` are explicit
service-level Render deployment inputs. The operator must attach the chosen
Commerce custom hostname to the gateway, configure DNS/TLS, and verify all
three values agree; the Blueprint does not claim that any hostname is
provisioned. `COMMERCE_MCP_URL` is also an operator-supplied service-level input
built from Render's actual Commerce Internal Service Address. The Attempt 4
smoke bodies, preview IDs and assertions remain external harness inputs. No
credential values are committed. Local fixtures do not prove hosted Google
OAuth, Commerce private assertion verification, or provider quality.

### Assumptions

Build/start/health values are transcribed from accepted C10 and COMMERCE-001
contracts. Provider keys remain Render-managed secrets and no second Redis
service is introduced.

### Unresolved Issues

Developer-owned follow-up: deploy test topology, attach and verify the chosen
Commerce hostname/DNS/TLS and matching service inputs, exercise real Google
OAuth in a browser, capture a valid authenticated Studio cookie and current
Server Action inputs, supply valid and five wrong-claim Background RS256
assertions plus a valid C5 body, provide current discovery/preview bodies and
matching UUIDs, verify private caller denial, and run the authenticated hosted
health/Server Action/discovery/preview smoke commands. No live deployment,
OAuth completion, assertion verification, or paid provider-quality result is
claimed here.

### Architectural Concerns

None newly reported. Architect should review the external Studio hostname and
the exact C9.1 route allowlist against the accepted Commerce route tree.

### Git / VCS

Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-020-GATEWAY-001`, branch `task/ARCH-020-GATEWAY-001`, Attempt 4 implementation commit **478923a**, pushed to origin. Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-020-GATEWAY-001`. No main integration, gitlink change, deployment, or enabled-task launch was performed.

## Architect Review

### Review Status

Accepted — Attempt 4.

### Review Notes

Reviewed by `moda_architect` against the exact submitted Attempt 2 snapshot identified
by the Completion Report as implementation `12ca000` and parent report `74177e18`.

Attempt 2 closes the principal Attempt 1 implementation defects and should be
preserved:

- the new GATEWAY-001 secrets and `COMMERCE_MCP_URL` are service-level external
  inputs rather than new `sync:false` environment-group entries;
- the runbook uses Render's actual Commerce Internal Service Address for the MCP URL
  instead of assuming the service name/port;
- the positive Blueprint validator derives environment from
  `DEPLOYMENT_ENVIRONMENT_NAME`, not fixture filenames;
- every negative fixture now asserts its expected failure fragment; the architect
  independently reran the submitted positive and negative validators and both pass;
- C15 U01–U14 page routes now support GET/HEAD plus Next Server Action POST only when
  `Next-Action` is present;
- NextAuth GET/POST, all four discovery routes and the exact seven C9.1 preview
  method/path combinations are explicitly routed with wrong-method rejection;
- public MCP aliases/encoded/dot-segment forms remain denied;
- Commerce has the exact 131072-byte body boundary and a dedicated 100-second backend
  read timeout without changing legacy upstream bounds;
- the submitted Docker suite reports 150 passing fixtures and the Completion Report
  accurately separates local evidence from later hosted deployment smoke.

Attempt 2 is **not accepted** because the remaining A1-R5 deployment-input/smoke
contract is not yet internally consistent. The corrections below are the complete
Attempt 2 rework contract.

#### A2-R1 — make the Commerce Studio hostname a real deployment input, not a hard-coded Blueprint claim

**Blueprint, validator and runbook changes required.**

C10 and this task both state:

```text
actual Studio hostname = deployment input
do not guess it in source
```

and the Attempt 2 Completion Report now says:

```text
COMMERCE_PUBLIC_HOST and the Commerce custom domain remain explicit Render deployment
inputs; the Blueprint does not claim DNS provisioned
```

but both Blueprints still hard-code:

```text
test:
  domains includes commerce-test.modainteract.com
  gateway COMMERCE_PUBLIC_HOST = commerce-test.modainteract.com
  Commerce AUTH_URL = https://commerce-test.modainteract.com
  Commerce COMMERCE_STUDIO_ORIGIN = https://commerce-test.modainteract.com

production:
  same pattern with commerce.modainteract.com
```

The positive validator also asserts those hard-coded values. That is not an external
deployment input and contradicts the Completion Report.

Because no durable provisioning evidence for those two Commerce hostnames exists in
the submitted task record, normalize the Blueprint to the deployment-input path.

For **both test and production**:

1. Remove the Commerce custom hostname from the gateway `domains:` list. Existing
   Admin/App/Messaging domains remain untouched.
2. Replace gateway `COMMERCE_PUBLIC_HOST` with a **service-level** external input:

```yaml
- key: COMMERCE_PUBLIC_HOST
  sync: false
```

3. Remove `COMMERCE_STUDIO_ORIGIN` from the Commerce environment group.
4. Declare on the Commerce service:

```yaml
- key: COMMERCE_STUDIO_ORIGIN
  sync: false
- key: AUTH_URL
  sync: false
```

5. The operator must set:

```text
COMMERCE_PUBLIC_HOST = <exact attached Commerce custom hostname>
COMMERCE_STUDIO_ORIGIN = https://<same hostname>
AUTH_URL = https://<same hostname>
```

6. The operator attaches that custom hostname to the **gateway web service** in
   Render and configures DNS/TLS. Commerce remains a private service and never owns a
   public custom domain.

Do not move these values into an environment group: current Render Blueprint semantics
do not support `sync:false` entries in environment groups. Service-level `sync:false`
is the intended manual input boundary. Current Render documentation also notes that
new `sync:false` values on an existing Blueprint service are manually supplied in the
Dashboard.

Update `validate-render-blueprints.sh` so:

```text
Commerce group:
  no COMMERCE_STUDIO_ORIGIN

gateway:
  COMMERCE_PUBLIC_HOST exists exactly once
  service-level sync:false
  no hard-coded value/fromGroup

Commerce service:
  COMMERCE_STUDIO_ORIGIN exists exactly once
  service-level sync:false
  AUTH_URL exists exactly once
  service-level sync:false

Commerce private service:
  no domains

gateway domains:
  do not contain a committed Commerce hostname
```

Retain exact fixed `ADMIN_ORIGIN`, preview configuration and all existing non-Commerce
domain expectations.

Add meaningful negative cases with expected fragments for:

```text
hard-coded COMMERCE_PUBLIC_HOST
hard-coded COMMERCE_STUDIO_ORIGIN
hard-coded Commerce AUTH_URL
Commerce custom domain committed to gateway Blueprint
Commerce custom domain placed on private Commerce service
missing each of the three service-level inputs
```

The runbook must state this manual/custom-domain step explicitly and describe drift
checking:

```text
Render gateway custom-domain list
  must contain the chosen COMMERCE_PUBLIC_HOST

Gateway service env:
  COMMERCE_PUBLIC_HOST

Commerce service env:
  COMMERCE_STUDIO_ORIGIN
  AUTH_URL

all three host values must agree
```

Do not claim `commerce-test.modainteract.com` or `commerce.modainteract.com` as real
unless the developer later supplies provisioning evidence.

#### A2-R2 — make hosted smoke commands executable under the actual auth boundary

**Runbook/report changes required. No application auth implementation belongs here.**

The current smoke block routes protected Studio APIs without an authenticated session:

```sh
curl ... /api/studio/discovery/...
curl ... /api/studio/preview/...
```

C9/C15 require those operations to recheck active ADMIN/SUPER_ADMIN server-side, so
an unauthenticated hosted command is expected to be denied rather than produce the
successful smoke result implied by `curl -f`.

Require these external inputs:

```sh
export COMMERCE_PUBLIC_HOST='<actual attached Commerce hostname>'
export GATEWAY_PUBLIC_ORIGIN="https://${COMMERCE_PUBLIC_HOST}"

# Full Cookie header captured from a valid hosted ADMIN/SUPER_ADMIN browser session.
# Do not commit it or echo it.
export STUDIO_COOKIE_HEADER='<actual authenticated Cookie header>'

# A current Next Server Action identifier/body captured from the deployed Studio.
export STUDIO_NEXT_ACTION_ID='<current action id>'
export STUDIO_NEXT_ACTION_BODY='<bounded action request body>'
```

All discovery/preview smoke requests must send:

```sh
-H "Cookie: ${STUDIO_COOKIE_HEADER}"
```

The authenticated Server Action smoke uses the same cookie plus:

```sh
-H "Next-Action: ${STUDIO_NEXT_ACTION_ID}"
```

and the externally supplied bounded body.

Correct the Google/Auth.js callback route. Existing Moda auth documentation and the
`/api/auth/[...nextauth]` route contract use:

```text
/api/auth/callback/google
```

not:

```text
/api/auth/google/callback
```

Do not claim a fabricated code-only callback is a successful Google OAuth login.
Provide two explicit layers:

```text
route smoke:
  /sign-in reachable
  /api/auth/signin/google reaches Auth.js/redirect path
  /api/auth/callback/google reaches Commerce rather than gateway 404/405

hosted OAuth validation:
  developer completes real Google sign-in in a browser
  confirms redirect back to the configured same-origin Studio
```

For private MCP assertion negatives, replace one malformed token pretending to cover
five claims with explicit externally supplied short-lived test assertions:

```sh
BACKGROUND_ASSERTION
BACKGROUND_ASSERTION_WRONG_ISSUER
BACKGROUND_ASSERTION_WRONG_SUBJECT
BACKGROUND_ASSERTION_WRONG_AUDIENCE
BACKGROUND_ASSERTION_WRONG_ENVIRONMENT
BACKGROUND_ASSERTION_WRONG_KID
```

Each wrong-claim assertion must be a structurally valid signed test assertion produced
by the Background-owned validation mechanism and must be denied. Gateway does not
generate/sign these tokens.

The hosted smoke section must therefore contain copy/paste commands for:

```text
private live/ready
public MCP denial
private MCP missing assertion
private MCP valid assertion
five wrong-claim assertions
sign-in/Auth.js route reachability
authenticated Server Action
all four discovery methods with authenticated cookie
all seven C9.1 preview method/path families with authenticated cookie
```

Never print session cookies, assertion private keys or provider credentials.

#### A2-R3 — assign the later C21 Connections route extension explicitly to GATEWAY-003

**Architect scope reconciliation; no GATEWAY-001 implementation change required for
this item.**

GATEWAY-001 correctly implements the task's original C15 U01–U14 allowlist. C21 was
added later and introduces two new public Studio pages:

```text
U15 /connections
U16 /connections/[id]
```

The current HAProxy allowlist does not include them, and the existing GATEWAY-003 task
did not explicitly own that extension. Leaving this unassigned would make accepted
COMMERCE-022 pages unreachable through the final public Studio host.

This Architect Review therefore amends `ARCH-020-GATEWAY-003` to own only the C21
public-route delta in addition to its existing external-runtime config:

```text
GET/HEAD /connections
POST /connections with Next-Action only

GET/HEAD /connections/<id>
POST /connections/<id> with Next-Action only

OPTIONS / arbitrary methods -> 405
deeper /connections/... paths -> 404
```

The same public MCP/ambiguous-path denial remains ahead of route proxying. No blanket
`/api/studio` proxy is introduced.

GATEWAY-003 focused route fixtures must include U15/U16 before that task can be
accepted. Do not add these routes to GATEWAY-001 Attempt 3 merely to duplicate the
downstream C21 task.

#### A2-R4 — rerun scoped validation and reconcile the current report

After A2-R1/A2-R2:

```bash
bash tests/validate-render-blueprints.sh
bash tests/validate-render-blueprints-negative.sh
bash tests/run-tests.sh

bash -n \
  docker/entrypoint.sh \
  tests/run-tests.sh \
  tests/validate-render-blueprints.sh \
  tests/validate-render-blueprints-negative.sh

git diff --check
```

Render the HAProxy test configuration and run `haproxy -c` through the existing Docker
fixture if HAProxy is not installed locally.

The architect review environment independently reran the current Attempt 2 positive
and negative Blueprint validators successfully. Docker was not available in the
architect container, so the reported `150 passed, 0 failed` gateway suite remains
submitted executor evidence rather than falsely claimed as an independent rerun.

Update the Completion Report with:

```text
Attempt 3 implementation commit
exact positive/negative totals
exact Docker route total
actual custom-host deployment-input semantics
correct authenticated hosted-smoke inputs
no claim of live deployment/OAuth completion unless actually performed
```

Then set:

```yaml
status: review
attempt: 3
executor: null
claimed_at: null
```

push both mirrored task branches and STOP.

### Attempt 2 Reviewed Files

- `moda-interact-gateway/render.test.yaml`
- `moda-interact-gateway/render.production.yaml`
- `moda-interact-gateway/haproxy/haproxy.cfg`
- `moda-interact-gateway/docker/entrypoint.sh`
- `moda-interact-gateway/tests/run-tests.sh`
- `moda-interact-gateway/tests/validate-render-blueprints.sh`
- `moda-interact-gateway/tests/validate-render-blueprints-negative.sh`
- `moda-interact-gateway/docs/commerce-deployment.md`
- C9.1, C10 and C15 in `ARCH-020-implementation-contracts.md`
- C21 Studio route extension
- this task Completion Report

### Attempt 2 Validation Reviewed

Submitted evidence:

```text
bash tests/validate-render-blueprints.sh
  PASS

bash tests/validate-render-blueprints-negative.sh
  PASS — 41 expected rejections

bash tests/run-tests.sh
  PASS — 150 passed / 0 failed

HAProxy config validation
  PASS

shell syntax / git diff --check
  PASS
```

Architect-independent checks in this review environment:

```text
bash tests/validate-render-blueprints.sh
  PASS

bash tests/validate-render-blueprints-negative.sh
  PASS with expected-reason matching

bash -n on the submitted shell validators/entrypoint
  PASS

Docker gateway suite
  not independently rerun because Docker is unavailable in the architect container
```

Current Render documentation confirms private service `hostport` is the canonical
private-network coordinate, `sync:false` is service-level only (not environment
groups), and Blueprint variable interpolation is unavailable. Those facts support the
Attempt 2 MCP/private-secret correction and the A2-R1 manual hostname boundary.

### Attempt 2 Architecture Conformance

Not yet accepted.

The private Commerce topology, explicit U01–U14/C9.1/discovery route matrix,
MCP/public denial, secret ownership, request-size and timeout behavior now conform.
Acceptance remains blocked only by the still-hard-coded unverified Commerce Studio
hostname and the hosted-smoke commands that omit the actual authentication boundary.

The later C21 U15/U16 route extension is assigned to GATEWAY-003 rather than silently
left unowned.

### Attempt 2 Follow-up

Return GATEWAY-001 to:

```yaml
status: ready
attempt: 2
executor: null
claimed_at: null
```

The next:

```text
/moda-task ARCH-020-GATEWAY-001
```

must claim **Attempt 3 exactly once**.

Implement only A2-R1/A2-R2/A2-R4, preserve the accepted Attempt 2 proxy/topology
behavior, return to review and STOP. Do not begin GATEWAY-002, GATEWAY-003,
COMMERCE-012 or system-test tasks.

### Attempt 3 — Changes Requested (2026-09-22)

Reviewed by `moda_architect` against the exact submitted Attempt 3 snapshot
identified by the Completion Report as implementation `7bd5865ae6c3e412d03e383fd2bd951fb0c47c89`
and parent report `db1f387`.

Attempt 3 closes the infrastructure/runtime defects from Attempt 2 and those changes
must be preserved:

- `COMMERCE_PUBLIC_HOST`, `COMMERCE_STUDIO_ORIGIN` and Commerce `AUTH_URL` are now
  service-level `sync:false` deployment inputs rather than committed Commerce hostnames;
- the gateway Blueprint no longer claims a Commerce custom domain and the private
  Commerce service remains domainless;
- the deployment runbook explains attaching the chosen custom hostname to the gateway
  and verifying host/origin drift;
- the Auth.js callback route is corrected to `/api/auth/callback/google`;
- hosted Studio requests now use an authenticated cookie and Server Action requests use
  the current `Next-Action` identifier/body;
- the valid assertion plus five wrong-claim assertions are externally supplied by the
  Background-owned harness;
- positive Blueprint validation passes;
- the architect independently reran the submitted negative validator and confirmed
  **48** expected-reason rejections;
- the submitted Docker gateway suite remains **150 passed / 0 failed**. Docker is not
  available in the architect review environment, so that result remains executor
  evidence rather than a falsely claimed independent rerun;
- A2-R3 remains correctly assigned to pending GATEWAY-003: C21 U15/U16 `/connections`
  routing is not duplicated into this task.

Attempt 3 is **not yet accepted** because the hosted smoke section is authenticated
but still not executable against the accepted C5/C9.1/C15 application contracts.
This is the only remaining GATEWAY-001 correction.

#### A3-R1 — use valid C5/C9.1/C15 smoke payloads and concrete IDs

**Runbook/report changes required. No Blueprint, HAProxy or application implementation
change is required unless this documentation correction exposes a separate defect.**

The current runbook sends `{}` for several operations whose accepted API contracts
require structured input, and uses literal `<runId>` / `<conversationId>` placeholders
inside commands described as copy/paste hosted smoke checks.

Because those commands use `curl -f`, an application-level `400 INVALID_INPUT` is a
failed smoke even when Gateway routing and authentication are correct.

##### C5 private MCP

The current valid-assertion command sends:

```sh
-d '{}'
```

to `/api/mcp`.

C5 requires a valid JSON-RPC Streamable HTTP request. Therefore a correct Background
assertion can still reach Commerce and fail body validation, which does not prove:

```text
private MCP + valid Background assertion -> accepted protocol request
```

Require one externally supplied Background-owned valid request body:

```sh
export BACKGROUND_MCP_REQUEST_BODY='<valid bounded C5 JSON-RPC request matching BACKGROUND_ASSERTION purpose>'
```

Do not invent or sign assertions in Gateway. The Background-owned harness supplies the
valid assertion, the five structurally valid wrong-claim assertions, and the matching
valid bounded C5 request body.

Use the **same valid MCP body** for:

```text
missing assertion
valid assertion
wrong issuer
wrong subject
wrong audience
wrong environment
wrong kid
```

so the negative checks isolate authentication rather than mixing an invalid JSON-RPC
body with claim validation.

The valid path must assert an accepted non-error HTTP/protocol result. Do not depend on
an arbitrary response substring unless that marker is explicitly supplied by the
Background test harness and documented.

##### C15 discovery

The binding contract is:

```text
POST /api/studio/discovery/search
  {query:string1..500}

POST /api/studio/discovery/document
  {path:string1..512}

GET /api/studio/discovery/schema
  apiVersion=2026-07 required
  parentType/search/cursor optional

POST /api/studio/discovery/validate
  {definition:<bounded draft definition>}
```

The current runbook sends `{}` to search/document/validate and omits the required
`apiVersion` from schema.

Use externally supplied, non-secret, current valid smoke inputs:

```sh
export STUDIO_DISCOVERY_SEARCH_BODY='<valid JSON body containing query>'
export STUDIO_DISCOVERY_DOCUMENT_BODY='<valid JSON body containing an approved canonical shopify.dev/docs path>'
export STUDIO_DISCOVERY_VALIDATE_BODY='<valid JSON body containing a bounded current draft definition>'
```

Then call schema exactly with:

```text
/api/studio/discovery/schema?apiVersion=2026-07
```

Every request retains:

```sh
-H "Cookie: ${STUDIO_COOKIE_HEADER}"
```

and every `curl -f` invocation must be capable of succeeding with the documented
inputs.

##### C9.1 preview

The binding POST inputs are not `{}` except cancellation:

```text
POST /api/studio/preview/tool-tests
  {previewRunId,toolRevisionId,fixtureId,arguments}

POST /api/studio/preview/conversations
  {previewConversationId,mode,selection,fixtureId}

POST /api/studio/preview/conversations/<id>/runs
  {previewRunId,message}

POST .../cancel
  {}
```

Client-generated preview IDs must be concrete UUIDs and the GET paths must use the same
IDs; literal `<runId>` / `<conversationId>` strings are not executable hosted smoke.

Require externally supplied bounded smoke values, for example:

```sh
export STUDIO_PREVIEW_TOOL_TEST_RUN_ID='<UUID matching tool-test body>'
export STUDIO_PREVIEW_TOOL_TEST_BODY='<valid JSON body>'

export STUDIO_PREVIEW_CONVERSATION_ID='<UUID matching conversation body>'
export STUDIO_PREVIEW_CONVERSATION_BODY='<valid FIXTURE-mode JSON body>'

export STUDIO_PREVIEW_RUN_ID='<UUID matching conversation-run body>'
export STUDIO_PREVIEW_RUN_BODY='<valid JSON body>'
```

The body values may be generated/captured by the current hosted Studio or test harness;
Gateway must not fabricate saved tool/release/capability IDs.

Use those exact values for:

```text
POST tool test
GET same tool-test run ID
POST conversation
POST run under same conversation ID
GET same conversation/run IDs
POST cancel same conversation/run IDs with {}
```

Keep FIXTURE mode for the deployment smoke unless the developer explicitly intends a
paid MODEL validation. No provider credential is printed.

##### Required shell guards

Before the smoke calls, fail fast for every required external variable using shell
parameter guards, including at least:

```text
COMMERCE_INTERNAL_SERVICE_ADDRESS
COMMERCE_PUBLIC_HOST
GATEWAY_PUBLIC_ORIGIN
STUDIO_COOKIE_HEADER
STUDIO_NEXT_ACTION_ID
STUDIO_NEXT_ACTION_BODY
BACKGROUND_ASSERTION
BACKGROUND_ASSERTION_WRONG_ISSUER
BACKGROUND_ASSERTION_WRONG_SUBJECT
BACKGROUND_ASSERTION_WRONG_AUDIENCE
BACKGROUND_ASSERTION_WRONG_ENVIRONMENT
BACKGROUND_ASSERTION_WRONG_KID
BACKGROUND_MCP_REQUEST_BODY
STUDIO_DISCOVERY_SEARCH_BODY
STUDIO_DISCOVERY_DOCUMENT_BODY
STUDIO_DISCOVERY_VALIDATE_BODY
STUDIO_PREVIEW_TOOL_TEST_RUN_ID
STUDIO_PREVIEW_TOOL_TEST_BODY
STUDIO_PREVIEW_CONVERSATION_ID
STUDIO_PREVIEW_CONVERSATION_BODY
STUDIO_PREVIEW_RUN_ID
STUDIO_PREVIEW_RUN_BODY
```

Do not echo the cookie, assertions, private keys or provider credentials.

##### Attempt 4 validation

This correction is documentation/evidence-only. Preserve the accepted Attempt 3
Blueprint/proxy implementation.

Run:

```bash
bash tests/validate-render-blueprints.sh
bash tests/validate-render-blueprints-negative.sh

bash -n \
  docker/entrypoint.sh \
  tests/run-tests.sh \
  tests/validate-render-blueprints.sh \
  tests/validate-render-blueprints-negative.sh

git diff --check
```

The existing `150 passed / 0 failed` Docker route/body suite does not need to be
rerun merely because the hosted-smoke Markdown changed, unless the executor changes
Gateway implementation/configuration again. If any Gateway implementation/configuration
file changes, rerun `bash tests/run-tests.sh` and record the exact result.

Update the Completion Report to **Attempt 4**, identifying the runbook-only correction,
validation actually rerun and any unrun hosted checks. Do not claim live Render,
Google OAuth, Background assertion or provider validation unless actually performed.

Return the task to:

```yaml
status: review
attempt: 4
executor: null
claimed_at: null
```

push both mirrored task branches and STOP. Do not start GATEWAY-002, GATEWAY-003,
COMMERCE-012 or system-test work.

### Attempt 3 Reviewed Files

- `moda-interact-gateway/render.test.yaml`
- `moda-interact-gateway/render.production.yaml`
- `moda-interact-gateway/haproxy/haproxy.cfg`
- `moda-interact-gateway/docker/entrypoint.sh`
- `moda-interact-gateway/tests/run-tests.sh`
- `moda-interact-gateway/tests/validate-render-blueprints.sh`
- `moda-interact-gateway/tests/validate-render-blueprints-negative.sh`
- `moda-interact-gateway/docs/commerce-deployment.md`
- `ARCH-020-GATEWAY-003` C21 U15/U16 assignment
- this task Completion Report and complete Attempt 2 Architect Review

### Attempt 3 Validation Reviewed

Submitted evidence:

```text
bash tests/validate-render-blueprints.sh
  PASS

bash tests/validate-render-blueprints-negative.sh
  PASS — 48 expected-reason rejections

bash tests/run-tests.sh
  PASS — 150 passed / 0 failed (executor evidence)

HAProxy render / haproxy -c
  PASS (executor evidence)

shell syntax
  PASS

git diff --check
  PASS (executor evidence)
```

Architect independently reran the positive validator, negative validator and shell
syntax checks successfully from the submitted source. The extracted review archive is
not a Git repository, so the architect does not falsely claim an independent
`git diff --check`. Docker is unavailable in the architect environment, so the 150-test
suite remains submitted executor evidence.

### Attempt 3 Architecture Conformance

Infrastructure conformance is otherwise accepted.

The private/public Render topology, external hostname boundary, C15/C9.1 gateway
allowlist, public MCP denial, Commerce 128 KiB body bound, 100-second timeout and
secret ownership now conform to ARCH-020. Acceptance is withheld only because the
developer smoke procedure still mixes correct routing/authentication with invalid
application payloads and placeholder IDs.

### Attempt 3 Follow-up

Return through:

```text
/moda-task ARCH-020-GATEWAY-001
```

after this review overlay is committed. The next successful claim must create
**Attempt 4 exactly once**. No downstream task is promoted automatically.

### Attempt 4 — Accepted (2026-09-22)

Reviewed by `moda_architect` against the exact submitted Attempt 4 archive and
the canonical Attempt 4 Completion Report. Submitted implementation evidence:
`478923a`; parent report: `cb41f7c`.

Attempt 4 is accepted.

The only Attempt 4 implementation change is the deployment runbook, and it closes
A3-R1 without reopening the accepted Attempt 3 Blueprint/proxy implementation.

The hosted validation contract now correctly separates Gateway-owned configuration
from developer/harness-owned live inputs:

```text
C5 private MCP:
  BACKGROUND_ASSERTION
  five separately signed wrong-claim assertions
  BACKGROUND_MCP_REQUEST_BODY containing one valid bounded JSON-RPC request

C15 discovery:
  valid search body
  valid canonical-document body
  schema apiVersion=2026-07
  valid bounded draft-definition validation body

C9.1 preview:
  concrete client-generated UUIDs
  matching valid POST bodies
  the same IDs reused by GET/run/cancel operations

Studio:
  authenticated Cookie header
  current Next-Action id/body

Deployment:
  actual Render Internal Service Address
  externally selected Commerce public hostname/origin
```

The runbook fail-fast guards every required external value and does not print or
commit credentials. The same valid MCP request body is reused across missing,
valid and wrong-claim assertion checks, so the negative path isolates assertion
validation rather than JSON-RPC parsing.

The discovery smoke now uses:

```text
POST search    {query}
POST document  {path}
GET schema     ?apiVersion=2026-07
POST validate  {definition}
```

and the preview smoke now requires matching externally supplied identifiers/bodies
for tool-test, conversation and conversation-run lifecycle operations. Only the
defined cancellation request uses `{}`.

The runbook continues to distinguish route reachability from successful Google OAuth:
the developer must complete the real browser login after deployment rather than
treating a curl callback probe as OAuth completion.

#### Validation reviewed

Architect independently reran from the submitted Attempt 4 source:

```text
bash tests/validate-render-blueprints.sh
  PASS

bash tests/validate-render-blueprints-negative.sh
  PASS — 48/48 expected-reason negative cases

bash -n \
  docker/entrypoint.sh \
  tests/run-tests.sh \
  tests/validate-render-blueprints.sh \
  tests/validate-render-blueprints-negative.sh
  PASS
```

Attempt 4 is Markdown/runbook-only. Per the Attempt 3 correction contract, the
Gateway Docker suite was not required to be rerun when implementation/configuration
did not change. The previously submitted Attempt 3 evidence remains:

```text
bash tests/run-tests.sh
  PASS — 150 passed / 0 failed

HAProxy render / haproxy -c
  PASS
```

The extracted review archive is not a Git working tree, so the architect does not
falsely claim an independent `git diff --check`; the executor reports that check
passed.

#### Architecture conformance

Accepted.

GATEWAY-001 now conforms to the ARCH-020 deployment boundary:

- Commerce is a private Render service;
- browser Studio traffic reaches Commerce only through the explicit gateway allowlist;
- public MCP aliases/normalisation attempts are denied;
- private MCP URL and Background signing inputs are not hard-coded;
- Commerce assertion verification remains separate from Studio OAuth;
- Commerce public hostname/origin/Auth.js origin remain service-level deployment
  inputs so future domain changes do not require a repository change;
- Commerce requests retain the accepted 128 KiB body bound and 100-second backend
  timeout;
- test and production provider/transcription configuration remain isolated;
- deployment/smoke instructions are executable once the developer supplies the real
  hosted values.

Live Render deployment, DNS/TLS attachment, browser Google OAuth, hosted assertion
verification and hosted preview/discovery execution remain an intentional
developer-owned validation checkpoint after implementation acceptance. They are not
encoded as implementation-task dependencies.

#### Frontier reconciliation

Set:

```text
ARCH-020-GATEWAY-001
  Complete — Accepted, Attempt 4
```

All declared dependencies of both following tasks are now Complete, so promote
without claiming:

```text
ARCH-020-GATEWAY-003
  Ready — Attempt 0
  priority 175

ARCH-020-GATEWAY-002
  Ready — Attempt 0
  priority 190
```

GATEWAY-003 retains ownership of the later C21 U15/U16 `/connections` route delta.

Do **not** promote COMMERCE-012 or system-test tasks yet; they retain additional
incomplete dependencies. No downstream task is automatically launched.
