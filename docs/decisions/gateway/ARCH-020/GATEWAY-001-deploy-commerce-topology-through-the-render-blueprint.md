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
status: review
priority: 180
executor: null
claimed_at: null
attempt: 2
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
  - ARCH-020-GATEWAY-002
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
- ARCH-020-GATEWAY-002
- ARCH-020-GATEWAY-003

- ARCH-020-SYSTEM-TEST-001
- ARCH-020-GATEWAY-002

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

Attempt 2 — Ready for Review (2026-09-22). The Attempt 1 review corrections are
implemented locally; no live Render deployment, OAuth login, private assertion
call, paid provider call, or production resource mutation was performed.

### Files Changed

Implementation changes add the private Commerce Render service and C7.1/C9.1/
C10 configuration, Commerce upstream and explicit Studio routing, public MCP
denial, worker-only MCP signing scope, transcription/preview wiring, Docker
fixtures, strict positive/negative blueprint validators, and deployment/
rollback documentation.

### Work Completed

Commerce uses the accepted recursive build contract, `PORT`, `/health/live`,
and no startup migration. The gateway exposes the Studio host through explicit
page/auth/asset and C9.1 preview families. `/api/mcp`, `/mcp`, trailing,
encoded-separator, duplicate-separator and dot-segment variants are denied
before proxying. Background-only MCP URL/signing configuration and Commerce-only
verification keys are separated. Test and production preview/transcription
settings are independent; Groq is retained and OpenAI is explicit.

### Validation Results

| Requirement | Command / fixture | Result |
|---|---|---|
| Render topology and credential wiring | `bash tests/validate-render-blueprints.sh` | Passed |
| Legacy and Commerce negative mutations | `bash tests/validate-render-blueprints-negative.sh` | Passed; 41 meaningful mutations rejected for expected reasons |
| Routing, headers, body integrity, timeouts and MCP variants | `bash tests/run-tests.sh` | 150 passed, 0 failed |
| HAProxy rendering | Docker build plus entrypoint `haproxy -c` | Configuration valid |
| Shell and whitespace | `bash -n docker/entrypoint.sh tests/run-tests.sh`; `git diff --check` | Passed |

The Docker suite covers every C15 page/detail route with GET/HEAD and Server
Action POST checks, NextAuth GET/POST, all four discovery methods, all seven
C9.1 preview method combinations and wrong-method cases, the 131072/131073
byte Commerce boundary, all required public MCP alias/encoded/normalisation
attempts, and legacy provider-body/header behavior.

### Deviations

`COMMERCE_PUBLIC_HOST` and the Commerce custom domain remain explicit Render
deployment inputs; the Blueprint does not claim that `commerce-test` or
`commerce` DNS is provisioned. `COMMERCE_MCP_URL` is also an operator-supplied
service-level input built from Render's actual Commerce Internal Service
Address. No credential values are committed. Local fixtures do not prove
hosted Google OAuth or Commerce private assertion verification.

### Assumptions

Build/start/health values are transcribed from accepted C10 and COMMERCE-001
contracts. Provider keys remain Render-managed secrets and no second Redis
service is introduced.

### Unresolved Issues

Developer-owned follow-up: deploy test topology, exercise Google OAuth, verify
valid Background RS256 assertions and denial of other private callers, confirm
Render DNS/TLS, and run hosted health checks.

### Architectural Concerns

None newly reported. Architect should review the external Studio hostname and
the exact C9.1 route allowlist against the accepted Commerce route tree.

### Git / VCS

Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-020-GATEWAY-001`, branch `task/ARCH-020-GATEWAY-001`, Attempt 2 commit **12ca000**, pushed to origin. Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-020-GATEWAY-001`. No main integration, gitlink change, deployment, or enabled-task launch was performed.

## Architect Review

### Review Status

Changes Requested — Attempt 1.

### Review Notes

Reviewed by `moda_architect` against the exact submitted snapshot associated by the
Completion Report with implementation `9dbc61c` and parent handoff `f05023bc`.

Attempt 1 establishes a useful Gateway foundation and should be preserved:

- a private Commerce Render service is declared for test and production;
- the accepted recursive Commerce build/start/liveness contract is represented;
- Commerce receives database, Redis, hosted-auth, assertion-verification and preview
  configuration while Background messaging owns MCP signing configuration;
- no second Redis service is introduced;
- public Commerce traffic is host-routed through HAProxy and `/api/mcp` is denied on
  the public Commerce host;
- test/production preview/transcription configuration is separated;
- rollback/migration sequencing is documented;
- submitted local gateway, HAProxy and Blueprint-positive validation evidence is
  useful.

Attempt 1 is **not accepted** because the committed Blueprint/proxy cannot yet satisfy
C5/C7/C9/C10/C15 on Render. The corrections below are the complete Attempt 1 rework
contract. Keep the work inside `moda-interact-gateway`; do not change Commerce or
Background application source to compensate for infrastructure defects.

#### A1-R1 — remove guessed private MCP coordinates and use supported Render configuration forms

**Blueprint, validator and deployment-document changes required.**

The Blueprint currently commits:

```text
http://moda-interact-commerce-test:3000/api/mcp
http://moda-interact-commerce-production:3000/api/mcp
```

for `COMMERCE_MCP_URL`.

This is not a valid deployment contract. Render assigns each web/private service a
stable **internal service address** and the actual HTTP port is a service property.
The Blueprint reference exposes `fromService.property = host|port|hostport`; the
service name plus `:3000` is not that property. Commerce itself binds `PORT`, which is
Render-owned in hosted Node services.

Render Blueprints also do **not** support variable interpolation, so a Blueprint cannot
safely concatenate `http://` + `hostport` + `/api/mcp` in one `value` field.

Use this deterministic boundary:

1. Remove `COMMERCE_MCP_URL` from the `commerce-mcp` env-var group and delete that
   hard-coded group if it becomes empty.
2. Declare `COMMERCE_MCP_URL` **directly on the messaging worker** as a service-level
   external deployment input (`sync:false`). No other service receives it.
3. `docs/commerce-deployment.md` must instruct the deployer to obtain the exact
   Commerce **Internal Service Address** from Render after Blueprint provisioning and
   set:

   ```text
   COMMERCE_MCP_URL=http://<exact-render-commerce-host:port>/api/mcp
   ```

4. The deployment smoke section must verify that the host:port portion of the configured
   URL equals the currently provisioned Commerce internal service address and that the
   URL ends exactly in `/api/mcp`.
5. Blueprint validation must reject a committed literal `COMMERCE_MCP_URL` value and
   reject the key on Commerce/Admin/Gateway/any non-messaging service.

Do **not** invent a private DNS hostname or fixed port merely to keep the value in YAML.
If the architecture later adds a Gateway-owned startup interpolation mechanism, that
must consume Render's `hostport`; it must not change Background's accepted
`COMMERCE_MCP_URL` contract inside this task.

Current Render Blueprint semantics also do not support `sync:false` inside
`envVarGroups`. For every **GATEWAY-001-added** secret/external value, use a supported
service-level declaration rather than an env-group `sync:false` entry. At minimum:

```text
Commerce service:
  AUTH_SECRET
  AUTH_GOOGLE_ID
  AUTH_GOOGLE_SECRET
  COMMERCE_ASSERTION_PUBLIC_KEYS
  COMMERCE_PREVIEW_API_KEY

Production Commerce external configuration where intentionally operator-supplied:
  COMMERCE_PREVIEW_PROVIDER
  COMMERCE_PREVIEW_MODEL

Messaging worker:
  COMMERCE_MCP_URL
  COMMERCE_ASSERTION_PRIVATE_KEY
  COMMERCE_ASSERTION_KEY_ID
  WHATSAPP_OPENAI_API_KEY
```

Keep non-secret fixed values in environment groups only where the Blueprint format
supports them. Do not duplicate the same key through two attached groups/service-level
entries. Do not broaden this correction into an unrelated migration of every legacy
ARCH-002 environment group; only make the new ARCH-020 requirements deployable and
record any retained baseline separately.

Required validator regressions:

```text
fixed/hard-coded COMMERCE_MCP_URL               -> reject
COMMERCE_MCP_URL on Commerce                    -> reject
signing private key on Commerce                  -> reject
assertion public keys on messaging worker        -> reject
new ARCH-020 secret declared as group sync:false -> reject
missing worker COMMERCE_MCP_URL declaration      -> reject
```

#### A1-R2 — implement the exact C15/C9.1 public allowlist and NextAuth/Server Action methods

**HAProxy and route-fixture changes required.**

The current public Commerce allowlist is incomplete and method-incompatible:

```text
missing page families:
  /capabilities
  /capabilities/<id>
  /releases
  /releases/<id>
  /features/<id>
  /tools/<id>
  /sign-in
  /access-denied

missing C15 discovery APIs:
  POST /api/studio/discovery/search
  POST /api/studio/discovery/document
  GET  /api/studio/discovery/schema
  POST /api/studio/discovery/validate

current page rule:
  GET/HEAD only
  -> required Next.js Server Action POSTs are rejected 405

current /api/auth/* rule:
  GET/HEAD only
  -> NextAuth POST sign-in/callback/sign-out flows are rejected 405
```

The preview ACL is also too broad: GET and POST are accepted for every preview regex,
so undocumented combinations such as `GET /api/studio/preview/conversations` or
`POST /api/studio/preview/tool-tests/<runId>` can reach Commerce.

Implement the binding route/method matrix exactly.

**Pages**

```text
GET/HEAD:
  /
  /features
  /features/<one segment>
  /tools
  /tools/<one segment>
  /explore
  /capabilities
  /capabilities/<one segment>
  /releases
  /releases/<one segment>
  /shops
  /shops/<one segment>
  /preview
  /sign-in
  /access-denied
```

Allow POST to those Studio page/detail routes **only for a Next Server Action request**
(the request must carry the Next Action header used by the accepted Next runtime).
All other page methods reject before proxying.

**NextAuth**

```text
/api/auth/* -> GET or POST only
```

Do not use the current broad `/auth/` prefix as a substitute for the C15 page routes.

**Discovery**

```text
POST /api/studio/discovery/search
POST /api/studio/discovery/document
GET  /api/studio/discovery/schema
POST /api/studio/discovery/validate
```

No other discovery method/path is public.

**Preview C9.1**

```text
GET  /api/studio/preview/fixtures
POST /api/studio/preview/tool-tests
GET  /api/studio/preview/tool-tests/<runId>
POST /api/studio/preview/conversations
POST /api/studio/preview/conversations/<conversationId>/runs
GET  /api/studio/preview/conversations/<conversationId>/runs/<runId>
POST /api/studio/preview/conversations/<conversationId>/runs/<runId>/cancel
```

Reject all undocumented GET/POST/OPTIONS combinations.

**Assets**

Keep the existing bounded `/_next/*`/favicon handling and do not let an asset wildcard
cover `/api/*`.

**MCP**

Public Commerce `/api/mcp` remains 404 for every verb and normalization attempt. Add
fixtures for at least:

```text
/api/mcp
/api/mcp/
/mcp
/API/MCP
/api%2fmcp
/api%252fmcp
/api//mcp
/api/./mcp
/api/../api/mcp
/api/%2e/mcp
/api/%252e/mcp
/api%5cmcp
/api%255cmcp
```

The implementation may reject ambiguous encoded separators/dot segments generically
before route classification; do not depend on Next.js normalizing them safely.

Required route tests must cover every page/API family above plus wrong-method negative
cases. A passing root page plus one preview fixture is insufficient acceptance evidence.

#### A1-R3 — apply the Commerce-specific 128 KiB body bound and 100-second read timeout

**HAProxy + focused test changes required.**

C10 requires for the public Commerce upstream:

```text
request body bound = 128 KiB
read timeout       = 100 seconds
```

The submitted gateway currently uses the legacy global defaults:

```text
CLIENT_MAX_BODY_SIZE = 10m
PROXY_READ_TIMEOUT   = 60s
```

and the Blueprint does not override them. Therefore Commerce is neither 128 KiB
bounded nor configured for the accepted preview timeout.

Do not silently change unrelated Shopify/Admin/Messaging limits just to satisfy
Commerce.

Implement a Commerce-specific request guard before proxying:

```text
body size <= 131072 bytes -> eligible for normal route processing
body size > 131072 bytes  -> 413
```

Preserve the existing legacy global limit for non-Commerce hosts unless another
architecture task changes it.

Set the Commerce backend's upstream server/read timeout to exactly `100s` without
changing other backends' accepted timeout unless necessary for HAProxy correctness.

Focused evidence:

```text
Commerce body 131072 bytes -> not rejected by size guard
Commerce body 131073 bytes -> 413 and zero upstream call
same oversized payload on existing non-Commerce fixture -> retains legacy behavior
rendered commerce_backend config -> timeout server 100s
legacy backend timeout remains unchanged
```

No 100-second wall-clock test is required; validate the rendered HAProxy configuration
and use a short deterministic fixture for route/body behavior.

#### A1-R4 — make Blueprint negative validation meaningful, not filename-dependent false positives

**Validator changes required.**

`validate-render-blueprints.sh` currently determines environment from the **file
name**:

```ruby
environment = path.include?("production") ? "production" : "test"
```

but `validate-render-blueprints-negative.sh` writes every mutated fixture to a generic
temporary filename such as `/tmp/.../group_sync_false.yaml`.

As a result, every negative case built from `render.production.yaml` is evaluated as a
**test** Blueprint and can fail merely because `moda-interact-test-config` is absent.
That is a false-positive rejection and makes the reported "37 rejected" count
insufficient evidence of the intended mutations.

Fix environment discovery so it is derived from Blueprint content, not the path. A
permitted deterministic rule is:

```text
read DEPLOYMENT_ENVIRONMENT_NAME from the common config group
accept exactly test | production
cross-check group/service/database names against that value
```

Then strengthen the negative runner:

```text
run_negative_case <environment> <case> <expected-error-fragment>
```

It must fail if:

1. the mutated Blueprint unexpectedly validates; or
2. validation fails for a reason that does not contain the expected error fragment.

This prevents unrelated missing-group errors from satisfying a negative test.

The existing `group_sync_false` case must become a **real mutation**. Do not set a
field to the value it already has and count that as a rejected fixture.

Add negative cases for the GATEWAY-001-specific failures in A1-R1/A1-R2/A1-R3.

After correction, record the exact number of meaningful negative fixtures and their
expected failure reasons; do not reuse the current `37 rejected` claim without rerun.

#### A1-R5 — provide exact developer deployment/smoke commands and resolve the unverified Studio hostname claim

**Documentation/report changes required.**

The task Validation explicitly requires exact developer-owned deployment/smoke
commands with expected public/private/health outcomes. `docs/commerce-deployment.md`
currently describes these checks in prose but does not provide executable commands.

Add one copy/paste smoke section with external inputs named explicitly. It must cover:

```text
1. obtain the actual Commerce Internal Service Address from Render
2. set/verify COMMERCE_MCP_URL on the messaging worker
3. private GET /health/live -> 200 {status:ok}
4. private GET /health/ready -> 200 {status:ready}
5. public Commerce /api/mcp -> 404 even with browser/admin cookies
6. private POST /api/mcp without assertion -> denied
7. private POST /api/mcp with a short-lived valid Background RS256 assertion -> accepted MCP response
8. same private request with wrong issuer/subject/audience/environment/kid -> denied
9. public sign-in page and NextAuth Google callback path reach Commerce through gateway
10. one authenticated Studio page Server Action POST reaches Commerce
11. every C9.1 preview family and C15 discovery family has one hosted smoke request
```

Use environment variables/placeholders for credentials/tokens; commands must not echo
private key material or committed secrets. The valid assertion itself may be supplied
as an external short-lived `$BACKGROUND_ASSERTION`; this task does not reimplement the
Background signer.

The Completion Report currently calls `commerce-test.modainteract.com` /
`commerce.modainteract.com` an established convention while also saying external DNS
is still a deployment input. Resolve that contradiction before acceptance:

```text
either
  record durable developer/provisioning evidence that these are the supplied Studio
  hostnames
or
  treat the Commerce custom domain/COMMERCE_PUBLIC_HOST as an explicit deployment
  input and document how it is applied/drift-checked
```

Do not claim an unprovisioned hostname is "real" merely because it follows the Admin
naming convention.

Live deployment itself is still **not required** for this task's architect acceptance;
the exact smoke procedure and local evidence are required. Hosted results remain a
later developer/system-test layer.

#### A1-R6 — reconcile task evidence/checklists and rerun the scoped validation

Before Attempt 2 returns to Review:

1. Update Work Items, Acceptance Criteria and Validation checkboxes truthfully.
2. Replace the current requirement matrix with one that maps each C7.1/C9.1/C10/C15
   requirement to an exact fixture/test and observed result.
3. Record the Render Blueprint semantics used for service-level external secrets and
   the manual/dynamic MCP URL input.
4. Run exactly:

```bash
bash tests/validate-render-blueprints.sh
bash tests/validate-render-blueprints-negative.sh
bash tests/run-tests.sh
bash -n docker/entrypoint.sh tests/run-tests.sh \
  tests/validate-render-blueprints.sh \
  tests/validate-render-blueprints-negative.sh

git diff --check
```

5. Render the HAProxy configuration with the same test environment used by
   `tests/run-tests.sh` and run `haproxy -c` (Docker is acceptable if HAProxy is not
   installed locally).
6. Record the exact positive/negative/route test totals after the corrected matrices.
7. Set `status: review`, clear claim metadata, push implementation and parent task
   branches and STOP.

No live Render sync/deployment and no enabled-task execution is authorized by this
correction.

### Reviewed Files

- `moda-interact-gateway/render.test.yaml`
- `moda-interact-gateway/render.production.yaml`
- `moda-interact-gateway/haproxy/haproxy.cfg`
- `moda-interact-gateway/docker/entrypoint.sh`
- `moda-interact-gateway/tests/run-tests.sh`
- `moda-interact-gateway/tests/validate-render-blueprints.sh`
- `moda-interact-gateway/tests/validate-render-blueprints-negative.sh`
- `moda-interact-gateway/docs/commerce-deployment.md`
- C5, C7.1, C9.1, C10 and C15 in `ARCH-020-implementation-contracts.md`
- this task Completion Report

### Validation Reviewed

Submitted evidence:

```text
tests/run-tests.sh
  reported 67 passed / 0 failed

validate-render-blueprints.sh
  PASS

validate-render-blueprints-negative.sh
  reported 37 rejected

HAProxy config validation
  reported PASS

shell checks / git diff --check
  reported PASS
```

Architect independently reran the submitted positive and negative Blueprint scripts.
The positive validator passes. The negative runner prints all cases as rejected, but
inspection/reproduction proves production-derived fixtures are currently classified as
`test` from their temporary filename; at least those rejections are not evidence that
the intended mutations were caught.

Current Render Blueprint documentation was also checked during review: service
`hostport` is the supported private-network coordinate; Blueprint variable
interpolation is not supported; and `sync:false` is not supported inside environment
groups. The submitted GATEWAY-001 configuration conflicts with those deployment
semantics for its new MCP/secret wiring.

### Architecture Conformance

Not yet conformant with C5/C7.1/C9.1/C10/C15.

The service topology and ownership direction are correct, but acceptance is blocked by
invalid private MCP coordinates/secret declaration semantics, incomplete and
method-incorrect public Studio routing, wrong Commerce body/timeout bounds, unreliable
negative Blueprint evidence and missing exact deployment smoke commands.

### Follow-up

Return the same task to:

```yaml
status: ready
attempt: 1
executor: null
claimed_at: null
```

The next:

```text
/moda-task ARCH-020-GATEWAY-001
```

must claim **Attempt 2 exactly once**.

Implement only A1-R1 through A1-R6, rerun the bounded validation, update the current
Completion Report, return to `review`, clear the claim, push both mirrored branches and
STOP.

Do not begin GATEWAY-002, GATEWAY-003, COMMERCE-012 or SYSTEM-TEST-001.
