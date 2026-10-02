---
id: ARCH-020-GATEWAY-003
architecture_id: ARCH-020
title: Configure external API credential runtime
task_kind: implementation
domain: gateway
repository: moda-interact-gateway
assigned_agent: moda_gateway
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: blocked
priority: 175
executor: copilot
claimed_at: 2026-10-02T14:01:45Z
attempt: 3
depends_on:
  - ARCH-020-GATEWAY-001
  - ARCH-020-COMMERCE-020
  - ARCH-020-COMMERCE-021
  - ARCH-020-COMMERCE-026
  - ARCH-020-COMMERCE-028
  - ARCH-020-COMMERCE-029
enables:
  - ARCH-020-COMMERCE-012
  - ARCH-020-SYSTEM-TEST-002
created: 2026-09-21
updated: 2026-10-02
---

# Configure external API credential runtime

## Architecture

ARCH-020. Binding specification: [C21 external API tools](../../../architecture/ARCH-020-external-api-tools.md).
Read C21 in full and existing [contracts](../../../architecture/ARCH-020-implementation-contracts.md)
C7/C14/C20 where extended. C21 resolves this task's exact fields, interfaces,
limits, errors, ownership and acceptance IDs. No model-selected replacement design.

## Objective

Own Commerce Render blueprint/configuration examples and operator runbook only. Follow C21 section7 settings and existing001 private MCP topology. Package worker/WASM runtime assets and verify process memory capacity as section2.2 requires. No real secret values, application implementation or automatic live deployment.

## Context

The user approved read-only non-Shopify APIs, visual response filtering and sandboxed response code. Existing
Shopify/policy execution and Background MCP protocol remain supported. Future
external tool definitions require publication, not another Background handler.
This is new scope, not a correction to an accepted task.

## Scope

Own Commerce Render blueprint/configuration examples and operator runbook only. Follow C21 section7 settings and existing001 private MCP topology. Package worker/WASM runtime assets and verify process memory capacity as section2.2 requires. No real secret values, application implementation or automatic live deployment.

## Out of Scope

Writes, OAuth, unsandboxed code, customer-specific lookups, live credentials or
WhatsApp sends, pricing/merchant feature overrides, automatic API discovery,
external-result caching and other owners' implementation files. No live deployment.

## Requirements

Use C21 named interfaces and bounded examples. All dependencies must be accepted
Complete before claim. Readiness is not execution. Component tasks may prove their
ports with fixtures; only024 and SYSTEM-TEST-002 claim real assembled flow.
Protect every UI command against double clicks, preserve same-operation retries,
and never expose secrets or raw external response data in errors/logs.

## Work Items

- [x] Declare server-only keyring, active-key selector and stable command-HMAC secret on appropriate Commerce runtime only; no NEXT_PUBLIC or Background copies.
- [x] Document key generation by operator, retained decrypt-key rotation, rollback, missing-config behavior and migration-before-runtime ordering.
- [x] Validate configuration examples without printing secrets and preserve staff-only public Studio plus Background-only private MCP ingress.
- [x] Extend the explicit public Commerce page allowlist for C21 U15 `/connections` and U16 `/connections/[id]`: GET/HEAD plus authenticated Next Server Action POST only; no deeper catch-all.

## Interfaces / Contracts

C21 is the shared contract between these tasks. Own only the paths identified
above. Record exact accepted dependency SHA/package version and source exports
in the Completion Report. No catch-all shared integration barrel. Return genuine
contract contradictions with a source reproduction; do not weaken validation.

## Dependencies

- ARCH-020-GATEWAY-001
- ARCH-020-COMMERCE-020
- ARCH-020-COMMERCE-021
- ARCH-020-COMMERCE-026
- ARCH-020-COMMERCE-028
- ARCH-020-COMMERCE-029

## Enables
- ARCH-020-COMMERCE-012
- ARCH-020-SYSTEM-TEST-002


## Acceptance Criteria

- [x] X08: blueprint/config checks show exactly the three new settings in server scope, no secrets committed and no accidental public MCP route.
- [x] Runbook explains encrypted credentials cannot be decrypted after dropping old key; missing config disables external operations without breaking Shopify.
- [x] No live connection created, no deployment asserted; runtime behavior evidence comes from COMMERCE-024 controlled tests.
- [x] C21 U15/U16 route fixtures prove `/connections` and `/connections/<id>` GET/HEAD plus Next-Action POST are allowed, wrong methods return 405, deeper paths return 404 and public MCP denial remains unchanged.

## Validation

Provide `validate:arch020-external-runtime` in the owning repository and document its exact scope.
Also extend the existing Gateway route fixture suite with U15/U16 exact method/path cases; do not add a blanket `/connections/**` or `/api/studio/**` proxy.
Run focused changed-boundary tests, then existing repository typecheck/build
and lint where defined. Inspect package scripts first; do not invent a claim that
an absent script passed. Use C21 controlled transports and isolated stores.
Follow current developer-owned live/container validation policy; clearly separate
actual agent results from required unrun developer checks. No arbitrary screenshot
quota or repeated full-suite runs without new changes/failures.

## Stop Condition

Submit implementation and parent report through normal mirrored task branches,
then stop at Review for moda_architect. Never self-accept, launch downstream tasks,
merge main, publish service deployments or update workspace service gitlinks.
Shared's package publication is required only for SHARED-002 as explicitly scoped.
SYSTEM-TEST-002 requires explicit developer invocation even when Ready.

## Implementation Notes

Use /moda-task launcher-resolved dedicated worktrees and preparation packet.
Task authoring on main is the user's documentation exception, not permission for
implementation on main. Preserve unrelated work and existing task claims.

## Completion Report

### Attempt 3 — Blocked (2026-10-02)

#### A2-R1 — per-replica capacity proof

**Blocked; capacity is not proven and no plan change is claimed.** The accepted
COMMERCE-029 implementation is `f22e2d6` and its accepted report is `4069f60c`.
Its production build packages and smoke-tests the pinned
`quickjs-emscripten@0.31.0` artifact, but the accepted report explicitly states
that the runtime is not wired into the typed adapter or production factory;
those integration boundaries belong to COMMERCE-026/024. The available package
smoke runs the worker independently and does not expose a way to run four fresh
workers inside the built Commerce Next host while measuring the host-plus-worker
process-tree RSS. Adding that invocation/measurement seam requires Commerce-owned
runtime or production-composition source, outside GATEWAY-003 ownership. The
canonical Commerce checkout is on `main` at `f9fa054` and contains a different
`quickjs-wasi@3.6.2` runtime artifact; it is not substituted for the accepted
task pin, and its unrelated working-tree changes are preserved.

The current Commerce plans remain `0.5c-512mb` (test) and `0.5c-1g`
(production). No measured peak RSS or 25% headroom calculation is available, so
neither plan is asserted sufficient and the plans/validators/runbook are not
changed to imply otherwise. Required architect decision: assign or approve a
Commerce-owned production-host capacity measurement seam after the runtime is
wired, then rerun this bounded proof before selecting plans. The four-worker
contract is unchanged.

#### Attempt 3 correction checklist

- **A2-R1: blocked.** The exact missing seam is an invocation from the running
  production Commerce host into its accepted `createSandboxKernel()` so four
  fresh worker threads can be exercised and the host/worker RSS peak measured.
  No Commerce source was changed by Gateway.
- **A1-R1/A1-R3/A1-R4: preserved from Attempt 2.** Their submitted Docker/HAProxy
  results, HMAC rotation wording and prior task-record reconciliation remain in
  the Attempt 2 report below; Attempt 3 rerun results and current Git evidence
  are recorded below.
- **A1-R2: not closed for capacity.** Accepted package/build identity evidence
  remains recorded below, but it does not prove per-replica host memory adequacy.

#### Validation results

Passed in the dedicated Gateway implementation worktree:

- `./scripts/validate:arch020-external-runtime`: PASS; positive configuration
  checks and all expected negative cases rejected.
- `bash tests/run-tests.sh`: PASS; 162 passed, 0 failed. The rendered HAProxy
  configuration was exercised with the actual HAProxy binary in Docker.
- `bash tests/validate-render-blueprints.sh render.test.yaml`: PASS.
- `bash tests/validate-render-blueprints.sh render.production.yaml`: PASS.
- `bash tests/validate-render-blueprints-negative.sh`: PASS.
- `bash -n docker/entrypoint.sh tests/run-tests.sh
  tests/validate-render-blueprints.sh tests/validate-render-blueprints-negative.sh`:
  PASS.
- `git diff --check` in both task worktrees: PASS.

The Attempt 3 Commerce production-host/four-worker RSS measurement and capacity
build were not run: the accepted runtime is not connected to the production host,
and the only locally checked-out Commerce runtime is a different, user-modified
mainline revision. The accepted COMMERCE-029 package/smoke/build results remain
valid for that producer commit only; they are not presented as host-capacity
evidence. No live Render deployment, external connection, provider credential,
or production mutation was used.

#### Git / VCS

- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-020-GATEWAY-003`, branch `task/ARCH-020-GATEWAY-003`; prepared claim commit `3613f652ba2cef03c9ff9180fc991fd30e4300c0`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-020-GATEWAY-003`, branch `task/ARCH-020-GATEWAY-003`; preserved starting/head commit `1102490fec44be11920f563552ceb26ec4d85f3d`, with no implementation changes.
- The parent report is the only parent-worktree change. No implementation gitlink or other task/architecture file is staged. Both task remote-tracking refs were present before report publication.
- The current task-report commit and push outcome are recorded in the execution handoff; no main branch was updated.

### Status

Attempt 2 corrections remain complete, but Attempt 3 is blocked pending a Commerce-owned production-host measurement seam and moda_architect's capacity decision. No live Render deployment, connection, provider credential, or production assertion was created.

### Files Changed

Implementation branch `task/ARCH-020-GATEWAY-003`, Attempt 2 commit `54bbecf` (based on `844043f`):

- `render.test.yaml`
- `render.production.yaml`
- `haproxy/haproxy.cfg`
- `tests/validate-render-blueprints.sh`
- `tests/validate-render-blueprints-negative.sh`
- `tests/run-tests.sh`
- `scripts/validate:arch020-external-runtime`
- `docs/commerce-deployment.md`

### Work Completed

Added exactly three Commerce-server-only Render inputs in both blueprints: `COMMERCE_CONNECTION_KEYS_JSON`, `COMMERCE_CONNECTION_ACTIVE_KEY_ID`, and `COMMERCE_CONNECTION_COMMAND_HMAC_KEY`, each service-level with `sync: false`. The validator now requires each exactly once on Commerce and rejects missing, duplicate, group-scoped, Messaging, or other-service copies.

Extended the explicit HAProxy Commerce page allowlist for U15/U16: `/connections` and one-segment `/connections/<id>` allow GET/HEAD and POST only when `Next-Action` is present. Deeper paths remain 404, wrong methods remain 405, and the existing public MCP/ambiguous-path denial is unchanged. Added route fixtures for allowed methods, missing-Next-Action rejection, and deeper-path rejection.

Added the `./scripts/validate:arch020-external-runtime` static/config validation command and documented operator key generation, retained-key rotation, rollback, missing-configuration behavior, and migration-before-runtime ordering without committing secret values.

Addressed Attempt 1 corrections: the runbook now states that HMAC-key rotation requires an explicitly designed replay/audit migration and is not an ordinary Render environment edit. It records accepted COMMERCE-029 deployment evidence: the pinned `quickjs-sync.v1` / `quickjs-emscripten@0.31.0` package, artifact SHA-256 `0c031dd404df00f2d1ed9491a6590d014e88a50424996e5fd70feff1c931c045`, 64 MiB WASM ceiling smoke, packaged worker/loader/WASM under `build/code-runtime/`, and no request-time download. Both Render Commerce build commands invoke `npm run prisma:generate && npm run build`, whose accepted Commerce build path runs package and smoke before Next build.

The accepted four-worker profile has 4 x (64 MiB V8 old-space + 16 MiB V8 young-space + 64 MiB WASM) = 576 MiB before the host process. Therefore `0.5c-512mb` test Commerce is an explicit capacity gap, not sufficient evidence; `0.5c-1g` production has more headroom but remains unproven without host-level load measurement. The four-worker cap was not silently reduced; the capacity decision is returned to architecture/deployment ownership.

### Validation Results

Passed:

- `./scripts/validate:arch020-external-runtime`: passed; positive blueprint validation, 51 expected negative rejections, shell syntax, exact runtime-setting checks, and bounded route/MCP invariants.
- `bash tests/run-tests.sh`: passed, `162 passed, 0 failed`; rendered HAProxy configuration validated with the actual HAProxy binary and exercised U15/U16 routes, deeper-path rejection, and public MCP variants.
- `bash tests/validate-render-blueprints.sh`: passed.
- `bash tests/validate-render-blueprints-negative.sh`: passed, including the three new connection-runtime negative cases.
- `bash -n docker/entrypoint.sh tests/run-tests.sh tests/validate-render-blueprints.sh tests/validate-render-blueprints-negative.sh`: passed.
- `git diff --check`: passed.

Accepted dependency evidence consumed from COMMERCE-029: `npm run code-runtime:package`, `npm run code-runtime:smoke`, and `npm run build` passed on its accepted branch/report, including packaged artifact execution and the 67,108,864-byte WASM ceiling probe. No Commerce source was modified by this gateway task. Direct host `haproxy -c` was not run because HAProxy is not installed locally; the Docker suite rendered and validated the configuration with the actual HAProxy binary. No live Render, OAuth, Background assertion, provider, PostgreSQL, or deployment validation was performed.

### Deviations

The task owns gateway blueprints, route allowlisting, validation fixtures, and the operator runbook only. Runtime application behavior remains owned by Commerce; no application implementation or fallback key was added.

### Assumptions

C21 read-only scope; the three settings are supplied externally by Render or an approved secret manager. `COMMERCE_CONNECTION_KEYS_JSON` contains key IDs mapped to base64 32-byte AES-GCM keys, the active ID must exist in that keyring, and the HMAC key remains stable for replay auditing. Recursive submodule preparation passed with no entries.

### Unresolved Issues

No local validation remains pending for this correction cycle. Capacity sufficiency for four concurrent workers on the configured Commerce plans remains an explicit architecture/deployment decision; no claim is made for live deployment behavior.

### Architectural Concerns

Return contradictory accepted source facts to moda_architect before weakening contracts.

### Git / VCS

Expected mirrored branch: `task/ARCH-020-GATEWAY-003`, Attempt 2. Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-020-GATEWAY-003`; parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-020-GATEWAY-003`. Attempt 2 implementation commit `54bbecf` and prior implementation commit `844043f` are pushed to `origin/task/ARCH-020-GATEWAY-003`; parent claim commit `a235391` is pushed, and this Attempt 2 parent report is being committed and pushed now. Both worktrees were reused with physical isolation; recursive submodule preparation was ready with no entries. Accepted dependency pin consumed: COMMERCE-029 commit `f22e2d6`, report `4069f60`, `quickjs-emscripten@0.31.0`, artifact SHA-256 `0c031dd404df00f2d1ed9491a6590d014e88a50424996e5fd70feff1c931c045`.

## Architect Review

### Review Status

Changes Requested — Attempt 2.

### Review Notes

Attempt 2 is reviewed in place. A1-R1, A1-R3 and A1-R4 are satisfied. A1-R2
correctly surfaced a deployment-capacity gap instead of weakening the accepted
four-worker C21 runtime contract. The developer subsequently reopened the task to
`ready`, Attempt 2 retained and claim clear, so the next authorized `/moda-task`
claim is Attempt 3 exactly once. Architect conflict reconciliation also produced
Gateway implementation head `1102490f`; preserve that merged validator state.

### Reviewed Files

- `render.test.yaml`
- `render.production.yaml`
- `haproxy/haproxy.cfg`
- `tests/validate-render-blueprints.sh`
- `tests/validate-render-blueprints-negative.sh`
- `tests/run-tests.sh`
- `scripts/validate:arch020-external-runtime`
- `docs/commerce-deployment.md`
- C21 §2.2 and §7
- Attempt 2 Completion Report and Developer Override

### Validation Reviewed

- Submitted `bash tests/run-tests.sh`: `162 passed, 0 failed`.
- Submitted `./scripts/validate:arch020-external-runtime`: PASS.
- Architect rerun on the exact post-merge snapshot:
  - `bash tests/validate-render-blueprints.sh render.test.yaml`: PASS.
  - `bash tests/validate-render-blueprints.sh render.production.yaml`: PASS.
  - `bash tests/validate-render-blueprints-negative.sh`: PASS.

### Architecture Conformance

Partially conformant. Secret placement, U15/U16 routing, packaged-runtime
consumption and HMAC-rotation wording conform. C21 §7 capacity remains unresolved:
the accepted four-worker hard ceilings total 576 MiB before the Commerce host, the
512 MiB test plan is insufficient, and the 1 GiB production plan has not been proven
sufficient with host/process headroom.

### Follow-up

Return through the existing `ready`, Attempt 2 state. Do not alter the four-worker
contract. Attempt 3 is bounded to the capacity correction below and final report/VCS
reconciliation; preserve implementation merge `1102490f` unless the capacity work
requires an authorized Blueprint/validator/runbook change. COMMERCE-012,
SYSTEM-TEST-002 and ARCH-024-GATEWAY-001 remain gated.
### Architect scope clarification — 2026-09-22

C21 was added after the original GATEWAY-001 U01–U14 route contract. This task now
owns the bounded public-route delta for accepted Connections pages:

```text
GET/HEAD /connections
POST /connections with Next-Action only
GET/HEAD /connections/<id>
POST /connections/<id> with Next-Action only
wrong method -> 405
deeper path -> 404
```

Preserve GATEWAY-001's public MCP/ambiguous-path denial and existing explicit route
matrix. No blanket proxy is authorized.

### Attempt 1 — Changes Requested (2026-09-22)

Reviewed by `moda_architect` against the exact submitted Attempt 1 archive.
Submitted implementation evidence: `844043f`; parent report evidence:
`ef59f012`.

Attempt 1 is well scoped and the following changes should be preserved:

- exactly the three C21 connection-runtime settings are declared as Commerce
  service-level `sync:false` inputs in both Render environments;
- the positive validator requires those settings on Commerce and rejects accepted
  Commerce secrets on non-owner services;
- the public Studio allowlist adds only `/connections` and one-segment
  `/connections/<id>` through the existing page route boundary;
- GET/HEAD are allowed and POST still requires `Next-Action`;
- deeper Connections paths remain outside the page allowlist;
- the existing public MCP/ambiguous-path denial is unchanged;
- the operator runbook correctly explains retained decrypt keys, active-key rotation,
  rollback, migration-before-runtime ordering, fail-closed missing configuration and
  no fallback application key;
- no Commerce application, database, Shared, Background or sandbox implementation
  source was modified.

The architect independently reran:

```text
./scripts/validate:arch020-external-runtime
  PASS

bash tests/validate-render-blueprints.sh
  PASS

bash tests/validate-render-blueprints-negative.sh
  PASS — all 51 submitted expected-reason cases rejected

bash -n \
  docker/entrypoint.sh \
  tests/run-tests.sh \
  tests/validate-render-blueprints.sh \
  tests/validate-render-blueprints-negative.sh
  PASS
```

Attempt 1 is **not accepted** because three bounded task-owned requirements plus task
record reconciliation remain. These are the complete Attempt 2 correction contract.

#### A1-R1 — run the local deterministic Gateway route/HAProxy validation

**Validation/report changes required. Source changes only if this proof exposes a
defect.**

The Completion Report says:

```text
bash tests/run-tests.sh
  not run because it is developer-owned Docker validation
```

That classification is incorrect under the current
`docs/agent-live-validation-execution-policy.md`.

The policy explicitly distinguishes:

```text
agent-owned:
  local deterministic integration tests
  local/mocked fixtures
  syntax/config parsing

developer-owned:
  commands that contact deployed/shared environments
```

`tests/run-tests.sh` is the repository's local deterministic Docker/HAProxy fixture
suite. It does not become developer-owned merely because it uses containers or takes
longer than a syntax check.

Attempt 2 must run, in the dedicated implementation worktree:

```bash
bash tests/run-tests.sh
```

and record the exact pass/fail count.

That proof must include the already-committed U15/U16 cases:

```text
GET  /connections                     -> routed
HEAD /connections                     -> routed
POST /connections + Next-Action       -> routed
POST /connections without Next-Action -> 405

GET  /connections/<id>                     -> routed
HEAD /connections/<id>                     -> routed
POST /connections/<id> + Next-Action       -> routed
POST /connections/<id> without Next-Action -> 405

wrong methods                         -> 405
/connections/<id>/<deeper>            -> 404
public MCP variants                   -> 404
```

The suite must exercise the rendered HAProxy configuration, not merely grep the source.
If Docker itself is unavailable or broken on the executor machine, record the concrete
local tooling failure and return the task `blocked`; do not relabel a local check as
developer-owned.

Direct host `haproxy -c` remains optional when the binary is not installed if the
Docker fixture already validates the rendered configuration with the actual HAProxy
binary.

No live Render/DNS/OAuth/provider call is required by this item.

#### A1-R2 — close C21 §7 packaged-runtime and per-replica memory evidence

**Gateway validation/runbook/report changes required. Do not modify Commerce runtime
implementation from this task.**

C21 §7 assigns GATEWAY-003 the deployment-side proof that the already accepted
COMMERCE-029 runtime package is actually viable in the Commerce deployment:

```text
Package/bundle the pinned WASM asset and Node worker entry in Commerce runtime;
never download them on requests.

Run production image/build smoke for:
  fresh worker
  WASM memory ceiling
  timeout
  4-worker cap

Keep per-replica memory sufficient for measured worst case,
or return an explicit contract/capacity gap.
```

Attempt 1 does not address this requirement at all.

Do **not** reimplement, edit or copy the QuickJS runtime. COMMERCE-029 is already the
accepted producer and records:

```text
runtimeVersion: quickjs-sync.v1
quickjs-emscripten: 0.31.0
WASM maximum: 64 MiB
worker V8 old-space: 64 MiB
worker V8 young-space: 16 MiB
maximum active workers: 4
no queue
packaged worker/loader/WASM smoke: PASS
artifact SHA-256:
  0c031dd404df00f2d1ed9491a6590d014e88a50424996e5fd70feff1c931c045
```

Gateway's job is to verify deployment consumption of that accepted producer.

Attempt 2 must:

1. inspect/record the accepted COMMERCE-029 package/build exports and commit;
2. prove the Render Commerce build command executes the accepted production build
   path that packages/smokes the pinned worker/loader/WASM artifact, with no request-time
   download;
3. run or consume an accepted local production-build/package smoke that proves a fresh
   packaged worker starts and the accepted runtime profile is loadable;
4. establish the memory-capacity decision for **both** Render Commerce plans.

The current Blueprint is:

```text
test Commerce:
  plan: 0.5c-512mb

production Commerce:
  plan: 0.5c-1g
```

Do not assume these plans are sufficient. Record the accepted/measured runtime
worst-case memory evidence and compare it with the per-replica plan.

The accepted runtime permits four concurrent workers and each worker has independent
V8/WASM limits; therefore the 512 MiB test plan cannot be declared sufficient merely
because one worker smoke passes. Either:

```text
A. provide bounded local evidence that the configured replica memory safely supports
   the four-worker contract plus the host Next.js process;
```

or:

```text
B. change the Gateway deployment plan/configuration to a plan demonstrated sufficient;
```

or, if neither is justified:

```text
C. return the task blocked with the concrete capacity gap so moda_architect can decide
   whether a future explicit C21 concurrency amendment is needed.
```

Gateway must not silently reduce the Commerce four-worker cap; that would be a runtime
contract change owned outside this task.

The proof is local/build-time. It does not require a live Render deployment and must
not expose credentials.

#### A1-R3 — document the HMAC rotation rule exactly

**Runbook/report change required.**

The current runbook correctly says:

```text
COMMERCE_CONNECTION_COMMAND_HMAC_KEY
  ... kept stable for command replay auditing
```

but C21 §7 is stronger:

```text
HMAC-key rotation needs an explicit migration of replay strategy;
it is not an automatic environment-variable change.
```

Add that exact operational consequence.

Required runbook behavior:

```text
normal keyring rotation:
  add new AES decrypt key
  make it active
  retain old decrypt keys until deliberate re-encryption completes

command HMAC key:
  do not rotate as an ordinary Render env edit
  rotation requires an explicitly designed replay/audit migration
  stop/return to architecture owner before changing it
```

Do not invent the migration in this Gateway task.

#### A1-R4 — reconcile task checklists and current VCS evidence

**Task-record changes required.**

The task was submitted for review while all Work Items and Acceptance Criteria remain
unchecked. That contradicts the normal repository-agent completion protocol.

On Attempt 2, update the checklists truthfully after A1-R1 through A1-R3.

The current Git/VCS section also says:

```text
Parent report is being committed and pushed
```

even though the developer supplied parent report commit `ef59f012`.

Attempt 2 must record:

```text
Attempt 2 implementation commit
Attempt 2 parent report commit
dedicated parent worktree
dedicated implementation worktree
push/clean evidence
accepted dependency pins consumed
exact local validation actually run
exact developer-owned live validation intentionally unrun
```

Live Render deployment, OAuth, provider credentials and production mutation remain
developer-owned/unrun and do not block the local correction cycle.

### Attempt 1 Reviewed Files

- `render.test.yaml`
- `render.production.yaml`
- `haproxy/haproxy.cfg`
- `tests/validate-render-blueprints.sh`
- `tests/validate-render-blueprints-negative.sh`
- `tests/run-tests.sh`
- `scripts/validate:arch020-external-runtime`
- `docs/commerce-deployment.md`
- C21 §2.2, §7, §8 and §9
- accepted COMMERCE-029 runtime evidence
- `docs/agent-live-validation-execution-policy.md`
- this task Completion Report

### Attempt 1 Architecture Conformance

Not yet accepted.

The connection-secret placement and U15/U16 Gateway routing implementation are
directionally conformant and remain within Gateway ownership. Acceptance is withheld
only for the missing local route proof, missing C21 §7 deployment/runtime-capacity
evidence, incomplete HMAC-rotation wording and task-record reconciliation.

### Attempt 1 Follow-up

Return the same task to:

```yaml
status: ready
attempt: 1
executor: null
claimed_at: null
```

The next:

```text
/moda-task ARCH-020-GATEWAY-003
```

must claim **Attempt 2 exactly once**.

Do not start COMMERCE-012 or SYSTEM-TEST-002. GATEWAY-002 remains Superseded.
COMMERCE-024 remains independently in Architect Review and is not changed by this
review.

## Developer Override — Reopen (2026-10-02)

- Previous accepted attempt: none. Attempt 1 received Changes Requested; Attempt 2
  was submitted for architect review but has not been accepted.
- Reopen reason: the developer explicitly requested reopening after the Attempt 2
  submission so another agent execution cycle can proceed once task preparation is
  available, specifically so the normal `/moda-task` launcher can recreate the
  missing canonical implementation worktree. The prior launcher stopped at the
  `review` status gate; this override records the developer's explicit lifecycle
  decision without claiming the task.
- Reopen transition: `review` to `ready`; executor and claimed_at remain null;
  attempt remains 2. The next authorized `/moda-task` claim increments it once to
  Attempt 3.
## Attempt 2 — Changes Requested (2026-10-02)

Attempt 2 closed A1-R1, A1-R3 and A1-R4. The only remaining acceptance gate is C21
§7 per-replica memory capacity. The developer override legitimately returned the
task from `review` to `ready` without claiming Attempt 3.

### A2-R1 — prove a sufficient Commerce replica plan without reducing concurrency

**Gateway Blueprint/validation/runbook/report changes are authorized; Commerce runtime
source changes are not.**

Preserve the accepted maximum of four active transform workers. Attempt 3 must:

1. preserve the conflict-resolved Gateway implementation head `1102490f` as its
   synchronized starting point;
2. run a bounded local production-host capacity proof using the accepted COMMERCE-029
   packaged runtime with the Commerce production build and four concurrent fresh
   workers; measure the Commerce host plus child-worker process-tree peak RSS while
   exercising the accepted worker/WASM profile;
3. configure the Commerce service plan in **both** `render.test.yaml` and
   `render.production.yaml` to a Render plan whose memory is sufficient for that
   measured peak with at least 25% operating headroom; `1c-2g` is the architect-approved
   default target unless the measured proof demonstrates another plan is sufficient;
4. update the positive/negative Blueprint validators and deployment runbook to assert
   and document the chosen Commerce plan/capacity decision;
5. rerun `./scripts/validate:arch020-external-runtime`, `bash tests/run-tests.sh`, both
   Blueprint validators, shell syntax checks and `git diff --check`;
6. record the measured peak, chosen plan, headroom calculation, Attempt 3 implementation
   commit, parent report commit, clean worktrees and remote-head equality.

Do not silently reduce the four-worker cap. If the bounded host-level proof cannot be
constructed without changing Commerce runtime source, stop and return the task
`blocked` with the exact missing measurement seam rather than inventing capacity
evidence.
