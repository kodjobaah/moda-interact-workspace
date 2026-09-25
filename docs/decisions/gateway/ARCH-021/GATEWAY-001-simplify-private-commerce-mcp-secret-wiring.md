---
id: ARCH-021-GATEWAY-001
architecture_id: ARCH-021
title: Remove Commerce MCP assertion-key wiring and preserve private link
task_kind: implementation
domain: gateway
repository: moda-interact-gateway
assigned_agent: moda_gateway
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 30
executor: null
claimed_at: null
attempt: 3
depends_on:
  - ARCH-021-COMMERCE-030
  - ARCH-021-BACKGROUND-001
enables:
  - ARCH-021-SYSTEM-TEST-001
created: 2026-09-24
updated: 2026-09-24
---

# Remove Commerce MCP assertion-key wiring and preserve private link

## Architecture

Architecture ID:

ARCH-021

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Preserve the existing private Commerce MCP topology and public denial while deleting all RSA/JWT assertion-key environment wiring. Add **no replacement MCP token or secret**.

## Context

ARCH-020 already routes Background to the Commerce internal service address and denies public `/api/mcp` routes. COMMERCE-030/BACKGROUND-001 remove application-layer MCP authentication; private network placement is therefore the only caller trust boundary and PostgreSQL remains the business-authorization boundary.

## Scope

Primary files:

```text
render.production.yaml
render.test.yaml
docs/commerce-deployment.md
docs/gateway.md
tests/validate-render-blueprints.sh
tests/validate-render-blueprints-negative.sh
```

## Out of Scope

- Application code.
- Making MCP public.
- Adding a shared token/API key/mTLS/key pair.
- Automatic deployment.

## Requirements

### R1. Preserve exact private topology

Keep `COMMERCE_MCP_URL` attached only to the Background messaging worker and pointing to Commerce's internal/private service address `/api/mcp`.

Keep the existing public gateway denial for `/api/mcp`, aliases, encoded separators, dot segments and trailing/path variants.

### R2. Remove all MCP authentication secret/key wiring

Remove from production/test Blueprint, docs and validators:

```text
COMMERCE_ASSERTION_PUBLIC_KEYS
COMMERCE_ASSERTION_PRIVATE_KEY
COMMERCE_ASSERTION_KEY_ID
COMMERCE_MCP_SERVICE_TOKEN
```

Do not add any replacement MCP secret/key/token environment variable.

### R3. Commerce service remains private for MCP

The Blueprint/gateway contract must continue to make `/api/mcp` reachable through the Commerce internal service address only. Staff/public Studio routes may remain exposed through the existing approved public routing; that must not expose `/api/mcp`.

### R4. Deployment runbook

Replace JWT/token examples with context-only private requests. Runbook must demonstrate:

```text
private service address + valid DB-backed context -> protocol response
private service address + malformed/stale context -> explicit denial/error
public /api/mcp -> denied before Commerce MCP execution
```

No secret generation/distribution/rotation step remains.

### R5. Blueprint tests

Positive validation asserts:

```text
COMMERCE_MCP_URL exists only where already authorised (Background messaging worker)
old assertion key env vars absent
no replacement MCP credential env var added
public MCP denial remains
```

Negative validation must fail when public MCP exposure is introduced or old key variables return.

## Work Items

- [x] Remove assertion-key env declarations from production/test Blueprints.
- [x] Add no replacement secret.
- [x] Update gateway/commerce deployment docs.
- [x] Update positive/negative Blueprint validators.

## Interfaces / Contracts

Consumes COMMERCE-030/BACKGROUND-001 context-only private MCP contract.

## Dependencies

- ARCH-021-COMMERCE-030
- ARCH-021-BACKGROUND-001

## Enables

- ARCH-021-SYSTEM-TEST-001

## Acceptance Criteria

- [x] `/api/mcp` remains private-only.
- [x] No RSA/JWT assertion env remains.
- [x] No bearer/API/shared secret replacement is introduced.
- [x] `COMMERCE_MCP_URL` remains attached only to the messaging worker as a Render-managed private input.
- [x] Public MCP denial remains validated.

## Validation

- [x] `bash tests/validate-render-blueprints.sh`
- [x] `bash tests/validate-render-blueprints-negative.sh`
- [x] repository-declared YAML/config validation
- [x] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, return the Completion Report to `moda_architect` and STOP. Do not begin enabled or follow-on tasks.

## Implementation Notes

Do not introduce a replacement credential merely because the old key variables are removed. The agreed trust boundary is the private service link.

## Completion Report

### Status

Ready for architect review

### Files Changed

- `render.production.yaml`
- `render.test.yaml`
- `docs/commerce-deployment.md`
- `docs/gateway.md`
- `tests/validate-render-blueprints.sh`
- `tests/validate-render-blueprints-negative.sh`

### Work Completed

- Removed Commerce assertion public-key and Background assertion private-key/key-id environment declarations from both Render blueprints.
- Kept `COMMERCE_MCP_URL` only on each messaging worker and added no replacement MCP credential.
- Replaced JWT/Bearer deployment examples with private-service, DB-backed context examples for valid, malformed and stale requests.
- Extended positive validation to assert public MCP denial and credential absence; added negative mutations for legacy credentials, replacement service tokens and removed denial rules.
- Added the required Commerce `/health/live` check to both blueprints so the validator's existing liveness contract is explicit.
- Corrected the private MCP smoke checks to send the ordinary JSON-RPC body separately from the `X-Moda-Commerce-Context` header.
- Changed malformed/stale probes to print bounded response bodies and reject any 2xx response without imposing an undocumented HTTP 401 status.
- Added a positive validator regression check for the context header and forbidden service credential wording in the private MCP smoke section.

### Validation Results

- `bash tests/validate-render-blueprints.sh` passed.
- `bash tests/validate-render-blueprints-negative.sh` passed, including `public_mcp_exposure`, `assertion_public_on_messaging` and `mcp_service_token_on_messaging` cases.
- Ruby Psych parsing passed for `render.test.yaml` and `render.production.yaml`.
- `git diff --check` passed.
- Semantic runtime credential audit passed for both blueprints and the smoke documentation; validator references are limited to intentional negative fixtures and absence guards.
- Attempt 3 report reconciliation: the launcher confirmed `attempt: 3`, `status: in_progress` at claim time, dependency gate passed, and dedicated worktrees resolved from the canonical primary workspace.
- Launcher-resolved parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-GATEWAY-001`, branch `task/ARCH-021-GATEWAY-001`.
- Launcher-resolved implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-GATEWAY-001`, branch `task/ARCH-021-GATEWAY-001`.
- Attempt 2 start synchronization: parent and implementation remote task branches were not fast-forwarded; `origin/main` was already current in both worktrees. Implementation submodule sync and recursive initialization passed; recursive submodule entries were empty and status was ready.
- Implementation commit: `fc25bfc`; parent Completion Report commit: `0c18805e`.
- Final Attempt 2 verification: implementation and parent worktrees were clean and their branches matched their respective upstream task branches after push.
- Attempt 3 report-only final check: `git diff --check` passed.
- No follow-on task was started; control returns to `moda_architect`.

### Deviations

None.

### Assumptions

- Commerce owns validation of the DB-backed private request context; Gateway only preserves the private service link and public denial.

### Unresolved Issues

- Long-running developer-owned integration validation remains for the developer/system-test workflow; it was not run by the agent.

### Architectural Concerns

None.

## Architect Review

### Review Status

Accepted

### Review Notes

Attempt 3 completes the report-only reconciliation requested after Attempt 2. No Gateway implementation files changed in Attempt 3.

The accepted implementation preserves the ARCH-021 context-only private MCP trust boundary:

- Commerce MCP remains reachable only through the Render private service link.
- `COMMERCE_MCP_URL` remains the only MCP-specific runtime configuration and is attached only to the Background messaging worker.
- public `/api/mcp` access remains denied by Gateway routing;
- RSA/JWT assertion-key wiring is removed;
- no Bearer token, API key, service token, shared secret or replacement MCP credential was introduced;
- the private MCP runbook sends an ordinary JSON-RPC body separately from `X-Moda-Commerce-Context`;
- malformed/stale context probes reject every 2xx result without assuming an undocumented fixed HTTP 401;
- validator coverage protects the context-header smoke contract and obsolete/replacement credential absence.

The Attempt 3 durable task record is now reconciled:

- task returned with `status: review`, `attempt: 3`, `executor: null`, `claimed_at: null`;
- all task-owned Validation items are checked;
- launcher-resolved dedicated parent and implementation worktrees are recorded;
- start-of-attempt synchronization and submodule/materialisation evidence is recorded;
- implementation commit `fc25bfc` and the earlier Attempt 2 report commit `0c18805e` are recorded;
- submitted Attempt 3 parent report commit is `2fa17a3`;
- final parent and implementation branches are recorded clean and equal to their upstream task refs;
- no follow-on task was started.

### Reviewed Files

- `moda-interact-gateway/render.production.yaml`
- `moda-interact-gateway/render.test.yaml`
- `moda-interact-gateway/haproxy/haproxy.cfg`
- `moda-interact-gateway/docs/commerce-deployment.md`
- `moda-interact-gateway/docs/gateway.md`
- `moda-interact-gateway/tests/validate-render-blueprints.sh`
- `moda-interact-gateway/tests/validate-render-blueprints-negative.sh`
- `docs/decisions/gateway/ARCH-021/GATEWAY-001-simplify-private-commerce-mcp-secret-wiring.md`
- `docs/decisions/gateway/ARCH-021/_index.md`
- `docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

### Validation Reviewed

Implementation validation already independently reviewed after Attempt 2:

```text
bash tests/validate-render-blueprints.sh            PASS
bash tests/validate-render-blueprints-negative.sh   PASS
Ruby Psych parse render.test.yaml                   PASS
Ruby Psych parse render.production.yaml             PASS
```

Attempt 3 report-only validation:

```text
git diff --check                                  PASS
```

The Completion Report also records the semantic credential audit as PASS.

### Architecture Conformance

Conforms.

The Gateway implementation preserves private-only MCP transport, removes obsolete application-layer assertion credentials without replacing them, and leaves PostgreSQL-backed Commerce context authorization at the Commerce boundary as required by ARCH-021.

Long-running integrated validation remains correctly assigned to the terminal developer/system-test workflow and is not an implementation blocker for this Gateway task.

### Follow-up

`ARCH-021-GATEWAY-001` is Complete.

`ARCH-021-SYSTEM-TEST-001` remains Pending because its full checkpoint dependency set is not yet Complete; in particular `ARCH-021-COMMERCE-028` and `ARCH-021-COMMERCE-029` remain outstanding.

Do not start system-test work solely because this Gateway task is now Complete.
