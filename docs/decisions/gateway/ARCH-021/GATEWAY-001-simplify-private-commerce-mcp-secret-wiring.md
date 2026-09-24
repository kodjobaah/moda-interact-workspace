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
status: in_progress
priority: 30
executor: copilot
claimed_at: 2026-09-24T16:23:57Z
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

### Validation Results

- `bash tests/validate-render-blueprints.sh` passed.
- `bash tests/validate-render-blueprints-negative.sh` passed, including `public_mcp_exposure`, `assertion_public_on_messaging` and `mcp_service_token_on_messaging` cases.
- Ruby Psych parsing passed for `render.test.yaml` and `render.production.yaml`.
- `git diff --check` passed.

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

Attempt 1 correctly removes the RSA/JWT assertion-key environment wiring from both Render blueprints, adds no replacement MCP credential, keeps `COMMERCE_MCP_URL` only on the Background messaging worker, and preserves the public HAProxy denial for `/api/mcp`. The submitted positive/negative Blueprint validators and YAML parsing also pass.

One task-owned deployment-runbook defect remains. The accepted COMMERCE-030/BACKGROUND-001 private MCP contract is:

```text
private service link
+ X-Moda-Commerce-Context: <base64url(JSON UTF-8)>
+ ordinary JSON-RPC body
```

`docs/commerce-deployment.md` currently does not send `X-Moda-Commerce-Context`. Instead it describes three different JSON-RPC bodies as containing valid/malformed/stale context and posts only those bodies. That does not exercise the implemented private-MCP contract.

The same runbook also requires HTTP `401` for both malformed and stale context. COMMERCE-030 does not define that invariant: malformed/missing context is an `INVALID_INPUT`/`UNAUTHENTICATED`-equivalent bounded error, while DB-backed stale/mismatched context may surface `STALE_TURN`, `FORBIDDEN`, `INCOMPATIBLE_VERSION`, or another bounded non-success result. The runbook must demonstrate explicit rejection without falsely requiring stale state to be HTTP 401.

No Blueprint/topology redesign is required.

### Reviewed Files

- `moda-interact-gateway/render.production.yaml`
- `moda-interact-gateway/render.test.yaml`
- `moda-interact-gateway/haproxy/haproxy.cfg`
- `moda-interact-gateway/docs/commerce-deployment.md`
- `moda-interact-gateway/docs/gateway.md`
- `moda-interact-gateway/tests/validate-render-blueprints.sh`
- `moda-interact-gateway/tests/validate-render-blueprints-negative.sh`
- `docs/decisions/commerce/ARCH-021/COMMERCE-030-simplify-private-mcp-authentication.md`
- `docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

### Validation Reviewed

Architect independently reran from the supplied snapshot:

```text
bash tests/validate-render-blueprints.sh          PASS
bash tests/validate-render-blueprints-negative.sh PASS
Ruby Psych parse render.test.yaml                 PASS
Ruby Psych parse render.production.yaml           PASS
```

The submitted Completion Report records `git diff --check` as PASS. The review archive does not contain Git metadata, so that check was not independently repeated from the archive.

### Architecture Conformance

Changes Requested. The deployed topology and credential removal conform in substance, but the operator validation/runbook does not conform to the accepted context-header transport contract and currently encodes an incorrect fixed-401 assumption for stale DB-backed context.

### Follow-up

Reclaim this same task as Attempt 2. Make only the following bounded corrections.

1. **Correct the private MCP smoke inputs in `docs/commerce-deployment.md`.** Separate the ordinary JSON-RPC body from the context header. Use explicit inputs with these semantics:

   ```text
   PRIVATE_MCP_REQUEST_BODY
       ordinary bounded JSON-RPC/MCP request body; contains no caller context

   PRIVATE_VALID_COMMERCE_CONTEXT
       valid base64url(JSON UTF-8) value for X-Moda-Commerce-Context

   PRIVATE_MALFORMED_COMMERCE_CONTEXT
       deliberately malformed header value

   PRIVATE_STALE_COMMERCE_CONTEXT
       syntactically valid encoded context whose durable DB state is stale/mismatched
   ```

   The Background-owned harness remains responsible for producing those context values. Do not document or introduce a bearer token, API key, JWT, assertion, shared secret, or replacement credential.

2. **Send the implemented header explicitly on every private MCP smoke request.** The valid request must have this exact shape in substance:

   ```sh
   curl -fsS -X POST \
     -H 'Content-Type: application/json' \
     -H "X-Moda-Commerce-Context: ${PRIVATE_VALID_COMMERCE_CONTEXT}" \
     --data-binary "${PRIVATE_MCP_REQUEST_BODY}" \
     "${COMMERCE_MCP_URL}"
   ```

   Malformed and stale probes must use the same JSON-RPC body and vary only the `X-Moda-Commerce-Context` value.

3. **Do not require stale context to be HTTP 401.** For each malformed/stale probe, capture the HTTP status and response body deterministically. Fail the smoke check if the response is any 2xx status. Preserve/print the bounded response body so the operator can see the actual MCP error code. Do not broaden this into a new error-mapping contract and do not hard-code a stale-context status that COMMERCE-030 does not guarantee.

4. **Remove stale wording.** Replace wording such as `private MCP assertions` or request bodies `with ... context` where it implies the old signed/assertion model or context-in-body transport. The runbook must consistently describe the private-link + context-header + JSON-RPC-body contract.

5. **Add a deterministic documentation regression check.** Extend an existing Gateway validation script (prefer `tests/validate-render-blueprints.sh`; do not create a new framework) so it fails if `docs/commerce-deployment.md` no longer contains the literal header name `X-Moda-Commerce-Context`, or if the private MCP smoke section reintroduces a service `Authorization`/Bearer/JWT/assertion credential. Keep this check bounded to the Gateway-owned deployment/runbook files; do not scan unrelated Auth.js/session documentation.

6. **Re-run and record all required validation.** Required commands/results before returning to review:

   ```text
   bash tests/validate-render-blueprints.sh            PASS
   bash tests/validate-render-blueprints-negative.sh   PASS
   Ruby Psych parse render.test.yaml                   PASS
   Ruby Psych parse render.production.yaml             PASS
   git diff --check                                    PASS
   ```

   Also run a source audit over the Gateway-owned Blueprints/runbook/validators proving there is no runtime configuration for:

   ```text
   COMMERCE_ASSERTION_PUBLIC_KEYS
   COMMERCE_ASSERTION_PRIVATE_KEY
   COMMERCE_ASSERTION_KEY_ID
   COMMERCE_MCP_SERVICE_TOKEN
   COMMERCE_MCP_TOKEN
   COMMERCE_MCP_SECRET
   ```

   Negative-test fixture strings used solely to prove rejection are allowed and must be identified as such in the Completion Report.

7. **Reconcile task execution state before handoff.** On the Attempt 2 claim, increment `attempt` exactly once. After the corrections and validation pass, check the task-owned Validation boxes, update the Completion Report with the actual Attempt 2 launcher/worktree synchronization and commit/push evidence, set `status: review`, clear `executor`/`claimed_at`, return to `moda_architect`, and STOP. Do not start `ARCH-021-SYSTEM-TEST-001`.
