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
status: ready
priority: 30
executor: null
claimed_at: null
attempt: 2
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

- [ ] `bash tests/validate-render-blueprints.sh`
- [ ] `bash tests/validate-render-blueprints-negative.sh`
- [ ] repository-declared YAML/config validation
- [ ] `git diff --check`

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

Changes Requested

### Review Notes

Attempt 2 resolves the only implementation defect from Attempt 1. The private MCP deployment runbook now:

- uses one ordinary JSON-RPC request body that contains no caller context;
- sends `X-Moda-Commerce-Context` explicitly for valid, malformed and stale probes;
- varies only the context-header value between the malformed/stale probes;
- rejects every 2xx malformed/stale response without imposing an undocumented fixed HTTP 401;
- prints a bounded rejection body for operator diagnosis;
- retains the private Render service-link trust boundary and public `/api/mcp` denial;
- introduces no replacement Bearer token, API key, JWT, assertion, shared secret or MCP credential.

The Gateway-owned validator now also fails if the smoke section loses the literal `X-Moda-Commerce-Context` header or reintroduces service-credential wording.

Architect independently reran the implementation validation from the supplied Attempt 2 snapshot:

```text
bash tests/validate-render-blueprints.sh            PASS
bash tests/validate-render-blueprints-negative.sh   PASS
Ruby Psych parse render.test.yaml                   PASS
Ruby Psych parse render.production.yaml             PASS
```

Architect also inspected both Blueprints and confirmed that the only MCP-specific runtime configuration is `COMMERCE_MCP_URL` on the messaging worker in each environment. The legacy credential strings remain only in validator absence guards / intentional negative fixtures.

No Gateway source, Blueprint, topology or deployment-runbook correction remains.

The task cannot yet be accepted because the durable task record was not reconciled as required by the Attempt 1 correction contract:

1. all four task-owned `## Validation` checkboxes remain unchecked even though the Completion Report says they passed;
2. the task frontmatter still carried an active executor/claim on return to review;
3. the Completion Report does not record the Attempt 2 launcher-prepared parent/implementation worktree evidence, start-of-attempt synchronization evidence, recursive submodule/materialization evidence where applicable, or final implementation/report commit-and-push evidence.

Those are task-protocol/reporting defects only. Do not modify Gateway implementation files to address this review.

### Reviewed Files

- `moda-interact-gateway/render.production.yaml`
- `moda-interact-gateway/render.test.yaml`
- `moda-interact-gateway/haproxy/haproxy.cfg`
- `moda-interact-gateway/docs/commerce-deployment.md`
- `moda-interact-gateway/docs/gateway.md`
- `moda-interact-gateway/tests/validate-render-blueprints.sh`
- `moda-interact-gateway/tests/validate-render-blueprints-negative.sh`
- `docs/decisions/gateway/ARCH-021/GATEWAY-001-simplify-private-commerce-mcp-secret-wiring.md`
- `docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

### Validation Reviewed

Architect independently verified:

```text
bash tests/validate-render-blueprints.sh            PASS
bash tests/validate-render-blueprints-negative.sh   PASS
Ruby Psych parse render.test.yaml                   PASS
Ruby Psych parse render.production.yaml             PASS
```

The submitted Completion Report records `git diff --check` and the semantic credential audit as PASS. The supplied review archive contains no Git metadata, so commit ancestry/upstream cleanliness could not be independently reconstructed from the archive.

### Architecture Conformance

Implementation conforms to the ARCH-021 context-only private MCP trust boundary. The remaining work is report/task-state reconciliation only.

### Follow-up

Reclaim this same task as Attempt 3 and perform **only** the following deterministic report correction. Do not modify Gateway source, Blueprint, HAProxy, runbook or validator files unless the report reconciliation itself exposes a factual mismatch.

1. Immediately after the Attempt 3 launcher claim, verify the task is `in_progress`, `attempt: 3`, and that the launcher resolved dedicated parent and implementation worktrees from the canonical primary workspace. Record the actual prepared packet evidence; do not invent paths or SHAs.

2. In `## Validation`, change exactly these four existing checkboxes from `[ ]` to `[x]`, because Attempt 2 already executed them successfully:

   ```text
   bash tests/validate-render-blueprints.sh
   bash tests/validate-render-blueprints-negative.sh
   repository-declared YAML/config validation
   git diff --check
   ```

   Do not rerun the Gateway validators solely to reproduce evidence already obtained in Attempt 2 unless the task record correction unexpectedly changes a Gateway-owned implementation file.

3. Reconcile `## Completion Report` so it durably records the actual Attempt 2 execution evidence:

   - launcher-resolved parent task worktree;
   - launcher-resolved implementation worktree;
   - start-of-attempt parent synchronization/base evidence;
   - start-of-attempt implementation synchronization/base evidence;
   - recursive submodule/materialization evidence where applicable;
   - implementation commit: `fc25bfc`;
   - parent Completion Report commit: `0c18805e`;
   - final implementation branch clean and equal to its upstream;
   - final parent task branch clean and equal to its upstream;
   - no follow-on task started.

   If any of those facts cannot be established from Git/launcher evidence, do not guess. Record the exact missing evidence and return the task `blocked`.

4. Preserve the existing successful Attempt 2 validation results and semantic credential audit in the Completion Report. Remove no valid implementation evidence.

5. After the report-only correction is complete, set:

   ```yaml
   status: review
   executor: null
   claimed_at: null
   attempt: 3
   ```

   Set Completion Report status to `Ready for architect review`.

6. Run only the report-level final check required by the files changed in Attempt 3:

   ```text
   git diff --check
   ```

   Record the result.

7. Commit and push the parent task-report correction according to the normal task workflow, verify the parent branch is clean and equals its upstream, return to `moda_architect`, and STOP. Do not start `ARCH-021-SYSTEM-TEST-001`.

No further Gateway implementation work is authorized by this review.
