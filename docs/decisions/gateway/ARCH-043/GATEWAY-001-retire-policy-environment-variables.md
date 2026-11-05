---
id: ARCH-043-GATEWAY-001
architecture_id: ARCH-043
title: Remove retired application-policy environment variables
task_kind: implementation
domain: gateway
repository: moda-interact-gateway
assigned_agent: moda_gateway
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 50
executor: codex
claimed_at: 2026-11-05T15:41:10Z
attempt: 1
depends_on:
- ARCH-043-ADMIN-001
- ARCH-043-ADMIN-002
- ARCH-043-BACKGROUND-001
- ARCH-043-BACKGROUND-002
- ARCH-043-API-001
- ARCH-043-API-002
- ARCH-043-COMMERCE-001
- ARCH-043-COMMERCE-002
- ARCH-043-SHOPIFY-001
- ARCH-043-SHOPIFY-002
- ARCH-043-MCP-001
- ARCH-043-ADMIN-004
- ARCH-043-API-004
- ARCH-043-MESSAGING-001
enables:
- ARCH-043-SYSTEM-TEST-001
created: '2026-10-17'
updated: 2026-11-05
---

# Remove retired application-policy environment variables

## Architecture

- Architecture: `ARCH-043` — `docs/architecture/ARCH-043-database-managed-platform-configuration.md`.
- Proposed schema/key contract: `docs/architecture/ARCH-043-configuration-schema-review.md`.
- Repository owner: `moda-interact-gateway` / `moda_gateway`.
- Parent task definition is materialised on `task/ARCH-043-GATEWAY-001`; route-only verification resolves this canonical file as Ready. Attempt remains 0 with no execution claim. Prepare the implementation worktree and claim through the normal task launcher.

## Objective

Remove proven-unused environment declarations for policy and approved application secrets **only after** authenticated database-backed consumers and their secret import/rotation gates are accepted.

## Context

Gateway owns the Render Blueprints and deployment topology, not repository consumer source.

## Scope

- Review the Render Blueprint and environment-specific configuration for both policy and secret variables.
- Retire service-specific policy/provider declarations only after their current consumer proves database authority and safe startup/rotation. Preserve the externally required ARCH-039 credential keyring, active writer selector, Commerce-only HMAC, config-unseal roots and accepted absent-row Auth.js fallback. Messaging now has its separately accepted MESSAGING-001 database reader; do not infer that every deployment credential with a similar name is obsolete.
- Keep `DATABASE_URL`, Redis, deploy identity/URLs, `OTEL_*` and the externally managed `MODA_CONFIG_UNSEAL_KEY` or KMS identity; never commit the root value.
- No private Meta endpoint or API-002-specific internal service identity is created. Do not add API-to-Messaging connectivity. Record the environment-specific rollback matrix. Any Messaging credential retirement must be supported by its accepted direct database reader and deployment verification, without a private API resolver.

## Out of Scope

- No deletion of DB state, secrets, consumers, unrelated config and no promotion of system-test dependencies into this task.

## Requirements
### 17 October 2026 reconciliation guardrails

Do not remove `AUTH_SECRET`, `AUTH_GOOGLE_ID`, or `AUTH_GOOGLE_SECRET` for Admin/Commerce: they are deliberate fallback bundles on **absent** DB auth records and are resolved only on authentication requests. Keep `AUTH_URL`, `WOO_BILLING_ENVIRONMENT`, `MODA_WOO_REST_READ_PUBLIC_ORIGIN` and required cryptographic unwrap roots external. Inspect the accepted Messaging reader before deciding whether its old verification environment declarations are obsolete; do not remove unrelated ingress credentials. Retire only per-service credential names actually made obsolete by the eight additional accepted consumer tasks, with a rollback matrix; never assume that an Admin UI setting automatically migrates all consumers.


- Maintain test/production separation and no secret values in Blueprint.
- Render topology remains deployable with all independent service startups.

## Work Items

- [x] Audit `render.test.yaml`, `render.production.yaml` and canonical `render.yaml` where applicable for policy variables replaced by ARCH-043.
- [x] Remove obsolete settings only after the owning consumer explicitly proves database-only behaviour and safe rollback.
- [x] Keep required bootstrap variables, ingress credentials not migrated by an accepted consumer, DB/Redis, OTEL and Woo-plugin local connection environment variables. Verify the accepted Messaging reader before retiring any Messaging-specific legacy values.
- [x] Record environment-specific deploy sequencing and a rollback table.
- [x] Record actual files changed, validation results, worktree isolation and Completion Report; stop at Review.

## Interfaces / Contracts

- `PlatformConfiguration` and `PlatformConfigurationAudit` are owned by `ARCH-043-DATABASE-001`; schema supports typed non-secret objects and sealed envelopes; environment-scoped and redacted in audit.
- Closed policy shapes are specified in `docs/architecture/ARCH-043-configuration-schema-review.md`. Admin validates before writes; each service independently validates the configuration it consumes. No ARCH-043 Shared publication is required.
- Existing billing, tenant, provider credential and bootstrap contracts retain their established owners.


### 18 October Background consolidation gate

`ARCH-043-BACKGROUND-001` is the sole typed PostgreSQL reader service, and `ARCH-043-BACKGROUND-002` performs **all** Background provider/worker consumer cutovers, including the former `BACKGROUND-008/009` requirements. Both must be architect-accepted Complete before this task proceeds. No separate Background credential-resolver task remains.

## Dependencies

- ARCH-043-ADMIN-001
- ARCH-043-ADMIN-002
- ARCH-043-BACKGROUND-001
- ARCH-043-BACKGROUND-002
- ARCH-043-API-001
- ARCH-043-API-002
- ARCH-043-COMMERCE-001
- ARCH-043-COMMERCE-002
- ARCH-043-SHOPIFY-001
- ARCH-043-SHOPIFY-002
- ARCH-043-MCP-001
- ARCH-043-ADMIN-004
- ARCH-043-API-004
- ARCH-043-MESSAGING-001

## Enables

- `ARCH-043-SYSTEM-TEST-001`

### Fresh pre-production configuration ownership

No `MODA_ARCH043_DISABLE_LEGACY_POLICY_EDITORS` flag exists and Gateway must not create or enable one. ADMIN-002 removes duplicate R2 and support translation editor keys directly. Consumers move to canonical `merchant.knowledge.r2` and the existing Commerce translation provider/model authority, respectively. Gateway should only retire provider environment variables actually superseded by independently accepted reader tasks; keep infrastructure/authentication fallback variables under the approved boundary.

### Shopify Partner cutover gate

Treat accepted `ARCH-043-SHOPIFY-002` as the sole Shopify Partner billing, Shopify OAuth and Knowledge/R2 consumer cutover gate. Do not retire Shopify Partner credential environment declarations merely because SHOPIFY-001 is Complete: SHOPIFY-002 must prove both Partner billing calls use the typed database reader with no mixed-source fallback. Keep unrelated services' credentials until their **own** consumers are accepted.

## Acceptance Criteria

- [x] Maintain test/production separation and no secret values in Blueprint.
- [x] Render topology remains deployable with all independent service startups.
- [x] The bounded task implementation passes the specified validation without regressions to existing domain configuration.

## Validation

- [x] Blueprint parser/validation and diff review
- [x] Deployment environment matrix/roll-back check

## Stop Condition

Complete the defined scope and required validation, update the task and Completion Report to Review, return to `moda_architect`, and STOP. No execution of enabled tasks and no `_index.md` edits.

## Implementation Notes

- Preserve service ownership boundaries and existing published ARCH-039 credential functions. Use the ARCH-043 documented policy shapes and AAD byte convention; do not invent a new crypto codec or require new Shared publication.
- Changes to shared generic logging, if needed, must use `@modainteract/moda-interact-shared/logging`.
- Use launcher-resolved dedicated task worktrees and start-of-attempt synchronisation evidence.

## Completion Report

### Status

Ready for Review — Attempt 1, `codex`, 5 November 2026. Local implementation and bounded validation complete; live deployment acceptance remains developer-owned and is not claimed. Implementation commits `4826b08` and `2c3a7de` on mirrored `task/ARCH-043-GATEWAY-001`; publication details are recorded below.

### Files Changed

Implementation repository (`moda-interact-gateway`):

- `render.test.yaml`, `render.production.yaml`.
- `tests/validate-render-blueprints.sh`, `tests/validate-render-blueprints-negative.sh`, new `tests/validate-platform-configuration-negative.sh`.
- New `docs/platform-configuration-cutover.md`.
- `docs/merchant-knowledge-deployment.md`, `docs/commerce-deployment.md`, `docs/mcp-private-deployment.md`, `docs/render-topology.md`, `docs/deployment-prerequisites.md`, `README.md`.

Parent repository: only this task file. No gitlink, index, architecture definition or downstream task edits.

### Work Completed

- Inspected both actual Blueprints, positive/negative validators and accepted current production consumer factories at seven pinned repository revisions. Recorded the per-service variable-to-reader matrix in `docs/platform-configuration-cutover.md` before removing declarations. No canonical `render.yaml` exists.
- Retired superseded Shopify OAuth/Partner/App Events, R2/upload, translation, transcription, AI/sender, production embedding, Commerce bootstrap-email and test Woo billing credential declarations. Traced production App Events factory to `shopify.appEvents`; the remaining environment parser is not a live default consumer. Support translation remains on existing Commerce model/provider rows; no parallel `support.translation` or legacy-editor flag was created.
- Preserved infrastructure/identity/observability, Shopify scopes/app URL, Admin/Commerce absent-row auth bundles, API Woo environment/public-origin/public connection mode, ARCH-039 reader keyrings, active writer selectors and Commerce-only command HMAC. Verified protected declarations and non-environment service/resource topology against the pre-change revision.
- Corrected test unseal distribution: Gateway no longer receives it; each sealed reader receives its required external group. Added isolated production equivalents. MCP receives only its supported `MODA_CONFIG_UNSEAL_KEYS_JSON` map; the other services receive JSON-in-`MODA_CONFIG_UNSEAL_KEY` plus active ID. No secret/root values committed. This avoids the inspected MCP reader's incompatible single-base64 interpretation of `MODA_CONFIG_UNSEAL_KEY`.
- Added missing production Messaging PostgreSQL wiring and production API Woo infrastructure settings. Kept both legacy Messaging Meta declarations pending actual environment verification. The accepted reader is direct PostgreSQL; no private resolver, API-to-Messaging link or internal identity was added.
- Restored test MCP `/health/ready` configuration to the existing validator/runbook contract. Plans, instance counts, routes, hosts, other health settings, worker commands and resources remain unchanged; no material capacity/cost change.
- Updated runbooks with independent test/production import, root provisioning, reader rollout, cold-start/rotation/revocation/tamper verification and rollback gates. Canonical R2 has one sealed six-field record; existing embedding and translation authorities remain intact.
- Preserved all existing unrelated validator protections, adapted retired-group fixtures and added 90 targeted adversarial fixtures covering every sealed reader's root attachment, excess recipients, wrong MCP format, shadow/direct roots, Messaging DB isolation, retained auth/Woo/Meta inputs and retired-variable reintroduction. The standard negative suite now invokes the focused suite. Final source tracing includes `checkout.worker.ts` → `ShopifyWhatsAppConsentService` → consent provider → `getShopifyAccessToken`; this prevents incorrectly dropping the event worker's root.

### Validation Results

Passed locally in the isolated implementation worktree:

- `bash -n tests/validate-render-blueprints.sh tests/validate-render-blueprints-negative.sh tests/validate-platform-configuration-negative.sh` — exit 0.
- Psych `safe_load(..., aliases: false)` of both Blueprints — exit 0.
- `bash tests/validate-render-blueprints.sh` — exit 0 for test and production, including private routing and documentation assertions.
- `bash tests/validate-render-blueprints-negative.sh` — final combined run exit 0 after the event-worker correction: 127 adapted existing mutation fixtures, the public-MCP denial fixture and all 90 focused ARCH-043 test/production fixtures. **218 adversarial cases passed.**
- `bash tests/validate-platform-configuration-negative.sh` — standalone run exit 0; all 90 fixtures also passed in the final combined run, including required event-worker root access.
- `bash tests/validate-observability-config.sh` — exit 0.
- One-off parsed comparison to implementation starting HEAD — databases unchanged; service topology unchanged except restoring test MCP readiness; exact existing ARCH-039 and Auth.js declarations preserved.
- `git diff --check` — exit 0; reviewed Blueprint and validator diffs.

Baseline positive validation initially rejected required `MODA_WOO_REST_READ_PUBLIC_ORIGIN` via an overbroad credential-alias expression. Narrowed only that exact exception; forbidden keyring/active-key aliases still fail negative fixtures. The baseline also lacked test MCP readiness despite its existing validator requiring it; corrected the declaration.

Accepted owning-reader source and tests were inspected for cold OAuth startup, fresh operation reads, revoked/disabled records, wrong/missing wrapping roots, tampering/AAD failures, rotation and no last-good fallback. Exact source revisions and test paths are in the cutover document. Those tests were not rerun across repository ownership boundaries, and source inspection is not live deployment proof.

Developer-owned integration handoff (not executed):

```bash
bash scripts/developer-validation.sh ARCH-043-GATEWAY-001 -- bash tests/run-tests.sh
```

Expected result: exit 0 and all gateway integration checks pass. No Docker orchestration or live deployment was launched. Independently perform the environment matrix in `docs/platform-configuration-cutover.md`: accepted imports/rotations and key-ID compatibility, restart every sealed consumer, protected-operation success, controlled missing/revoked/tampered/DB-unavailable failure, next-operation rotation and safe rollback. Record bounded outcomes only, never credentials. Production uses separately approved safe probes/maintenance, not arbitrary corruption of live secrets.

### Deviations

- Messaging Meta credential retirement is deliberately deferred: accepted direct-reader code exists, but no deployed verification evidence was supplied. Existing declarations remain in both Blueprints, with an explicit release gate. No unrelated ingress credential was removed.
- Added the MCP-specific supported root variable/group because source inspection proves the generic root input has a different accepted format in MCP. No consumer or crypto codec changes were made.
- Restored missing test MCP readiness and missing production Messaging DB/API Woo infrastructure wiring as necessary independent-startup configuration corrections.

### Assumptions

Cleanup Blueprints are synchronized only after the per-environment accepted consumer deployment, credential import/rotation and rollback gates pass. Static validation establishes configuration shape and ownership; it does not establish Render acceptance, populated secrets, real provider access or runtime success.

### Unresolved Issues

No local implementation/test failures remain. Live Render validation, root/row population, cold starts, credential rotation/revocation/tamper probes, R2 exact-origin/create-only checks and deployed rollback remain developer-operated release gates. Standalone SYSTEM-TEST-001 was neither enabled nor executed by this agent. Preserve Meta declarations until its separate deployed gate passes.

### Architectural Concerns

The accepted MCP root format differs from the other readers and must stay explicitly separated until its owner changes the contract. A DB-only consumer cannot roll back by merely restoring env values; restore a compatible accepted service revision and configuration together. Never roll back to a compromised/revoked credential or delete durable configuration/audit data.

### Worktree Isolation and Publication

- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-043-GATEWAY-001`, branch `task/ARCH-043-GATEWAY-001`, starting parent `ba4250ea22403d11e0c3964750ac8b39ebe6bf80`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-043-GATEWAY-001`, matching branch, starting revision `ac092dc783d715db3b0e2136bce1cc51abaee5a1`.
- Launcher prepared/synchronized both isolated branches, verified all fourteen explicit dependencies Complete and recursive submodule state ready (Gateway has no submodule entries), then durably pushed claim `dde4e4929d214775cfd75856545caf70cf3163a8`, Attempt 1 at `2026-11-05T15:41:10Z`.
- Implementation head: `2c3a7de` (initial cleanup `4826b08`, followed by the event-worker reader correction); no other repository source edited. Implementation is pushed to `origin/task/ARCH-043-GATEWAY-001`; this report is submitted on the matching parent task branch. No merge or push to `main`; no architect acceptance decision made.

## Architect Review

### Review Status

Pending

### Review Notes

Awaiting implementation, validation evidence and architect decision.

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Not yet assessed.

### Follow-up

None

## 17 October 2026 ARCH-043 extension (architect-owned amendment)

Do not remove Admin/Commerce Auth.js env credentials until ADMIN-002 and COMMERCE-002 demonstrate DB bootstrap/rotation; remove R2/env upload fields only after all API/Shopify/Background consumers use the single sealed record. Do not remove merchant-specific WooCommerce REST credentials; global `woocommerce.auth` has no approved runtime consumer.

## Controlling consolidation — 2026-11-02

This is the single active Gateway cutover task. It owns the former GATEWAY-002 deployment/least-privilege/rollback checks as well as non-secret policy cleanup. Preserve externally required `COMMERCE_CONNECTION_KEYS_JSON`, writer `COMMERCE_CONNECTION_ACTIVE_KEY_ID`, Commerce-only `COMMERCE_CONNECTION_COMMAND_HMAC_KEY`, and config-unseal roots wherever the inspected service still consumes them. A database record named `commerce.connectionKeys` does not authorize removing another service's ARCH-039 reader keyring. Keep Admin/Commerce absent-row authentication fallback as implemented; invalid/revoked configured records remain fail-closed.

Inspect both actual Render Blueprints and their positive/negative validators. Current `ac092dc` still declares migrated Knowledge/translation/transcription settings and attaches provider groups. Produce a per-service variable-to-current-reader matrix before removing only proven obsolete references. Validate test/production separation, key distribution, revoked/tampered credentials, cold-start behavior and rollback; no deployment is performed by this definition reconciliation.

## Definition reconciliation — 2026-11-02

Source evidence: Gateway ac092dc render.test.yaml, render.production.yaml, tests/validate-render-blueprints.sh and its negative suite still contain policy/provider environment groups. Definition deduplicated and consolidated; code/deployment validation is still required. Canonical ARCH-039 keyring/authentication fallback retention is mandatory as detailed above.
