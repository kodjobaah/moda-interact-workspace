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
status: review
priority: 175
executor: null
claimed_at: null
attempt: 1
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
updated: 2026-09-22
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

- [ ] Declare server-only keyring, active-key selector and stable command-HMAC secret on appropriate Commerce runtime only; no NEXT_PUBLIC or Background copies.
- [ ] Document key generation by operator, retained decrypt-key rotation, rollback, missing-config behavior and migration-before-runtime ordering.
- [ ] Validate configuration examples without printing secrets and preserve staff-only public Studio plus Background-only private MCP ingress.
- [ ] Extend the explicit public Commerce page allowlist for C21 U15 `/connections` and U16 `/connections/[id]`: GET/HEAD plus authenticated Next Server Action POST only; no deeper catch-all.

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

- [ ] X08: blueprint/config checks show exactly the three new settings in server scope, no secrets committed and no accidental public MCP route.
- [ ] Runbook explains encrypted credentials cannot be decrypted after dropping old key; missing config disables external operations without breaking Shopify.
- [ ] No live connection created, no deployment asserted; runtime behavior evidence comes from020/024 controlled tests.
- [ ] C21 U15/U16 route fixtures prove `/connections` and `/connections/<id>` GET/HEAD plus Next-Action POST are allowed, wrong methods return 405, deeper paths return 404 and public MCP denial remains unchanged.

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

### Status

Implementation complete; submitted for Architect Review. No live Render deployment, connection, provider credential, or production assertion was created.

### Files Changed

Implementation branch `task/ARCH-020-GATEWAY-003`, commit `844043f`:

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

### Validation Results

Passed:

- `./scripts/validate:arch020-external-runtime`: passed; positive blueprint validation, 51 expected negative rejections, shell syntax, exact runtime-setting checks, and bounded route/MCP invariants.
- `bash tests/validate-render-blueprints.sh`: passed.
- `bash tests/validate-render-blueprints-negative.sh`: passed, including the three new connection-runtime negative cases.
- `bash -n docker/entrypoint.sh tests/run-tests.sh tests/validate-render-blueprints.sh tests/validate-render-blueprints-negative.sh`: passed.
- `git diff --check`: passed.

Not run: `bash tests/run-tests.sh` because it is the developer-owned Docker route suite; this environment has Docker but agent policy prohibits launching long-running/container validation without explicit authorization. HAProxy binary is not installed, so direct `haproxy -c` was not run. This repository has no `package.json`, so typecheck, build, and lint scripts are unavailable. No live Render, OAuth, Background assertion, provider, PostgreSQL, or deployment validation was performed.

### Deviations

The task owns gateway blueprints, route allowlisting, validation fixtures, and the operator runbook only. Runtime application behavior remains owned by Commerce; no application implementation or fallback key was added.

### Assumptions

C21 read-only scope; the three settings are supplied externally by Render or an approved secret manager. `COMMERCE_CONNECTION_KEYS_JSON` contains key IDs mapped to base64 32-byte AES-GCM keys, the active ID must exist in that keyring, and the HMAC key remains stable for replay auditing. Recursive submodule preparation passed with no entries.

### Unresolved Issues

Developer-owned Docker route validation remains pending, including the live HAProxy render check and U15/U16 HTTP assertions. No claim is made for live deployment behavior.

### Architectural Concerns

Return contradictory accepted source facts to moda_architect before weakening contracts.

### Git / VCS

Expected mirrored branch: `task/ARCH-020-GATEWAY-003`, Attempt 1. Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-020-GATEWAY-003`; parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-020-GATEWAY-003`. Implementation commit `844043f` was pushed to `origin/task/ARCH-020-GATEWAY-003`. Parent report is being committed and pushed on the mirrored parent branch.

## Architect Review

### Review Status

Pending.

### Review Notes

Definition only; no implementation acceptance.

### Reviewed Files

Not applicable.

### Validation Reviewed

Not applicable.

### Architecture Conformance

Awaiting implementation.

### Follow-up

Reconcile readiness/indexes after prerequisite acceptance; no automatic launch.
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
