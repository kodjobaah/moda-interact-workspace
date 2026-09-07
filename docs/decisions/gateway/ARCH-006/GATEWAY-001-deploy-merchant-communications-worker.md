---
id: ARCH-006-GATEWAY-001
architecture_id: ARCH-006
title: Deploy the independently scalable merchant-communications worker
task_kind: implementation
domain: gateway
repository: moda-interact-gateway
assigned_agent: moda_gateway
coordinator: moda_architect
status: review
priority: 55
executor: copilot
claimed_at: 2026-09-06T20:03:46Z
attempt: 2
depends_on:
  - ARCH-006-BACKGROUND-007
enables:
  - ARCH-006-SYSTEM-TEST-001
  - ARCH-006-SYSTEM-TEST-002
  - ARCH-006-SYSTEM-TEST-003
created: 2026-09-05
updated: 2026-09-06T20:12:00Z
---

# ARCH-006-GATEWAY-001: Deploy the independently scalable merchant-communications worker

## Architecture

`docs/architecture/ARCH-006-merchant-communications-support-inbox.md`

## Objective

Codify the new translation/reconciliation worker and its non-secret OpenAI/Batch timing configuration in the canonical Render topology without exposing any webhook route.

## Context

Current background workloads are deployed as separate Render workers. ARCH-006 adds another independently scalable worker. Translation uses provider polling; there is no OpenAI callback HTTP service to route.

## Scope

Architecture-approved `moda-interact-gateway` Render Blueprint/configuration changes for test/production worker deployment, environment wiring, scaling/readiness and OpenTelemetry identity.

## Out of Scope

- Background application implementation.
- Secret values.
- Public callback host/route.
- Admin/Shopify UI.
- Redis/Postgres durable-resource destruction.

## Requirements

Inspect actual accepted BACKGROUND-007 package script/entrypoint before editing deployment config; do not invent commands.

Declare a separate worker service for the merchant-communications runtime in each architecture-managed environment using existing DB/Redis/general/AI env-group conventions.

Add secret/config names required by the accepted implementation, including OpenAI credential and validated translation provider/model plus minute-scale Batch/reconciliation configuration. Secret values remain external (`sync: false` or current equivalent). Preserve independent test/production values.

Use stable OTel identity such as `service.name=moda-merchant-communications-worker`, existing `service.namespace`, and environment attribute conventions.

No public service or gateway route is required for OpenAI because completion is polled.

## Work Items

- [x] Inspect current test/production Render files and accepted background worker start command/env requirements.
- [x] Add merchant-communications worker declarations for test and production.
- [x] Wire Redis, PostgreSQL, OpenAI secret placeholder and translation/timing config using existing env-group conventions.
- [x] Wire correct OTel service/environment identity and readiness/startup behavior.
- [x] Validate Blueprint/config syntax with repository tooling and document deployment ordering.

## Interfaces / Contracts

Consumes accepted BACKGROUND-007 runtime only. This task does not modify `moda-interact-background` source.

Expected configuration is implementation-derived, not invented; likely categories include:

```text
OPENAI_API_KEY              secret
TRANSLATION_PROVIDER        non-secret
TRANSLATION_MODEL           non-secret
TRANSLATION_BATCH_INITIAL_POLL_MINUTES
TRANSLATION_BATCH_POLL_INTERVAL_MINUTES
TRANSLATION_RECONCILIATION_INTERVAL_MINUTES
TRANSLATION_BATCH_MAX_REQUESTS
```

Use exact names implemented/accepted by background.

## Dependencies

Explicit task dependencies are listed in YAML frontmatter.

## Enables

`ARCH-006-SYSTEM-TEST-001`, `ARCH-006-SYSTEM-TEST-002`, `ARCH-006-SYSTEM-TEST-003`

## Acceptance Criteria

- [x] Worker is independently deployable/scalable in test and production topology.
- [x] Actual accepted build/start commands are used.
- [x] Redis/Postgres dependencies are wired.
- [x] OpenAI secret is not committed.
- [x] Minute-scale config is environment-configurable.
- [x] OTel environment isolation is preserved.
- [x] No provider webhook/callback route is introduced.
- [x] Existing services remain unchanged except necessary shared env-group additions.

## Validation

Run gateway repository's declared Blueprint/config tests, typecheck/lint if applicable and `git diff --check`. Record any Render setting that cannot be represented as code.

## Implementation Notes

The canonical workspace currently uses environment-specific Render files; modify the actual architecture-owned files found in the repo rather than creating a speculative `render.yaml`.

## Completion Report

### Status
Ready for Review

### Files Changed
- `moda-interact-gateway/render.test.yaml`
- `moda-interact-gateway/render.production.yaml`
- `moda-interact-gateway/tests/validate-render-blueprints.sh`
- `moda-interact-gateway/tests/validate-render-blueprints-negative.sh`
- `moda-interact-gateway/docs/render-topology.md`

### Work Completed

- Added a dedicated `moda-merchant-communications-worker` Render worker in test and production, using the accepted `npm run start:merchant-communications-worker` command and existing Node 22 Docker build.
- Added environment-isolated OpenAI/translation configuration groups with external `OPENAI_API_KEY` placeholders and exact runtime timing/config names.
- Wired PostgreSQL, Redis, deployment environment, and existing observability configuration groups; the accepted runtime supplies stable `service.name=moda-merchant-communications-worker`, `service.namespace=moda-interact`, and dependency preflight/readiness behavior.
- Updated the canonical Render topology and deployment order to include four independent workers and OpenAI configuration.
- Attempt 2 added `TRANSLATION_RECONCILIATION_PAGE_SIZE=100` and `TRANSLATION_RECONCILIATION_CLAIM_TIMEOUT_MINUTES=15` to both environment-specific translation groups.
- Attempt 2 extended the positive validator to require and validate the translation group, exact non-secret values, secret placeholder handling, and the private merchant-communications worker's repository, runtime, command, group attachments, database wiring, and absence of public route/domain.
- Attempt 2 added negative mutations for missing translation-group attachment, wrong worker command, and missing reconciliation configuration.

### Validation Results

- `bash tests/validate-render-blueprints.sh`: passed.
- `bash tests/validate-render-blueprints-negative.sh`: passed.
- `bash -n tests/validate-render-blueprints.sh tests/validate-render-blueprints-negative.sh`: passed.
- `git diff --check`: passed.
- `bash tests/run-tests.sh`: developer-executed validation required; not run by this agent because it builds and orchestrates multiple Docker containers.

### Deviations

The Render Blueprints represent secret values with `__SET_IN_RENDER_DASHBOARD__`; actual secret population and live Render validation remain deployment-time operations.

### Assumptions

The translation model is configured as `gpt-4.1-mini`, matching the accepted background provider test/deployment contract; production model/cost suitability remains an operational deployment decision.

### Unresolved Issues

The full Docker integration suite and live Render validation remain to be executed by the developer/deployment environment.

### Architectural Concerns

None.

### Attempt 2 Result

All Attempt 2 correction-contract requirements are implemented. The task is returned to `review`; the repository agent did not commit or push.

## Architect Review

### Review Status

Returned to Ready for Attempt 2 correction.

### Attempt 1 Decision

The Render worker declaration, accepted Background start command, database/Redis wiring, OpenAI secret placeholder, no-webhook topology, OTel identity reuse and deployment-order documentation are directionally correct. The task is not accepted because the deployment contract does not yet expose all runtime reconciliation controls implemented by accepted BACKGROUND-007, and the repository Blueprint validators do not validate the new translation group or merchant-communications worker at all.

### Blocking Findings

1. **Accepted BACKGROUND-007 reconciliation controls are missing from both environment-specific translation groups.** The accepted runtime reads `TRANSLATION_RECONCILIATION_PAGE_SIZE` and `TRANSLATION_RECONCILIATION_CLAIM_TIMEOUT_MINUTES`; neither is represented in `render.test.yaml` or `render.production.yaml`. Defaults make the process start, but GATEWAY-001 explicitly owns environment-configurable deployment wiring derived from the accepted runtime. These controls must be visible and independently configurable in Render rather than remaining implicit code defaults.
2. **The positive Blueprint validator ignores the new translation group and worker.** `tests/validate-render-blueprints.sh` knows only the pre-ARCH-006 group/service set. The merchant-communications worker can be deleted, renamed, pointed at the wrong command, detached from Redis/translation configuration, or the translation secret/config group can be malformed and the advertised positive validation will still pass.
3. **The negative validator contains no ARCH-006 regression proving the new deployment contract is enforced.** At least one focused negative mutation must demonstrate that a broken merchant-communications worker/translation-group contract is rejected by the canonical validator.

### Attempt 2 Correction Contract

Attempt 2 is a bounded Gateway deployment-contract/validation correction. Do not change Background application code, schema, public gateway routing, Admin/Shopify services, or system-test status. No OpenAI callback route is allowed.

Allowed implementation/configuration files:

- `moda-interact-gateway/render.test.yaml`
- `moda-interact-gateway/render.production.yaml`
- `moda-interact-gateway/tests/validate-render-blueprints.sh`
- `moda-interact-gateway/tests/validate-render-blueprints-negative.sh`
- `moda-interact-gateway/docs/render-topology.md` only if needed to keep the documented configuration/deployment contract exact

Required behavior:

- Add `TRANSLATION_RECONCILIATION_PAGE_SIZE` and `TRANSLATION_RECONCILIATION_CLAIM_TIMEOUT_MINUTES` to both test and production translation configuration groups using bounded operational defaults consistent with accepted BACKGROUND-007 (`100` page size and `15` minute stale-request claim timeout unless a repository-documented deployment value is intentionally chosen).
- Preserve the already-correct ARCH-006 variables: `OPENAI_API_KEY`, `TRANSLATION_PROVIDER`, `TRANSLATION_MODEL`, batch-size/submit retry/initial poll/poll interval/max-auto-retry/reconciliation interval configuration.
- Extend `tests/validate-render-blueprints.sh` so the translation group is part of the canonical expected group map and its exact required keys are checked for both environments. Secret placeholder handling must remain consistent with the repository's existing Render-dashboard convention; non-secret values must be validated as deliberate configuration rather than incorrectly required to equal the secret placeholder.
- Extend the positive service contract so `moda-merchant-communications-worker-{environment}` is required and validated for the exact accepted Background repository/runtime/start command, exact group attachments (`common`, `redis`, `translation`), environment-specific `DATABASE_URL`, worker type and absence of a public route/domain.
- Add focused negative coverage that mutates at least one ARCH-006-specific invariant (for example: remove the translation group from the worker, change the start command, remove one required reconciliation key, or attach the wrong environment translation group) and prove the canonical validator rejects it. Prefer more than one mutation if the validator implementation naturally supports it.
- Preserve environment isolation: test must not reference production config/group/database and production must not reference test config/group/database.
- Keep the merchant-communications worker independently scalable and private; do not add a webhook/callback service.

Required validation:

- `bash tests/validate-render-blueprints.sh`
- `bash tests/validate-render-blueprints-negative.sh`
- `git diff --check`
- Record the developer-owned Docker/live Render validation as deferred operational validation; it does not block this bounded config correction unless the task contract explicitly requires running it.

When complete, return `ARCH-006-GATEWAY-001` to `review`, preserve `attempt: 2`, do not promote any system-test task, and STOP.
