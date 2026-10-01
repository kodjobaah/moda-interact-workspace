---
id: ARCH-023-GATEWAY-001
architecture_id: ARCH-023
title: Wire Merchant Knowledge deployment topology
task_kind: implementation
domain: gateway
repository: moda-interact-gateway
assigned_agent: moda_gateway
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: blocked
priority: 70
attempt: 1
depends_on:
  - ARCH-023-BACKGROUND-005
  - ARCH-023-BACKGROUND-008
  - ARCH-023-SHOPIFY-005
  - ARCH-023-COMMERCE-002
enables: []
created: 2026-09-29
updated: 2026-10-01
---

# Wire Merchant Knowledge deployment topology

## Architecture

Architecture ID: `ARCH-023`

Architecture document: `docs/architecture/ARCH-023-merchant-knowledge.md`

Coordinator: `moda_architect`

## Objective

Codify the complete ARCH-023 deployment topology in the existing Render test/production Blueprints:

1. deploy the dedicated Merchant Knowledge Background worker;
2. provide Shopify with private-R2 upload-sign/finalisation configuration;
3. provide Background with private-R2 read/delete configuration;
4. provide Background and Commerce with one identical embedding configuration per environment;
5. provide Commerce with its bootstrap `SUPER_ADMIN` identity;
6. require the private R2 bucket CORS policy needed for browser direct PUT from the exact deployed Shopify application origin(s);
7. preserve environment isolation, database/Redis wiring, observability conventions and existing services.

No new Merchant Knowledge HTTP service or Gateway route is introduced.

## Context

The repository currently uses these version-controlled Render Blueprints:

```text
render.test.yaml
render.production.yaml
```

Do not invent a new `render.yaml` in this task.

Existing application contracts fixed by accepted ARCH-023 tasks are:

### Shopify

`ARCH-023-SHOPIFY-005` reads:

```text
MERCHANT_KNOWLEDGE_R2_ENDPOINT
MERCHANT_KNOWLEDGE_R2_BUCKET
MERCHANT_KNOWLEDGE_R2_ACCESS_KEY_ID
MERCHANT_KNOWLEDGE_R2_SECRET_ACCESS_KEY
MERCHANT_KNOWLEDGE_MAX_UPLOAD_BYTES
```

Shopify requires R2 access only to generate/finalise direct browser uploads.

### Background

`ARCH-023-BACKGROUND-003/004/005` read:

```text
MERCHANT_KNOWLEDGE_R2_ENDPOINT
MERCHANT_KNOWLEDGE_R2_BUCKET
MERCHANT_KNOWLEDGE_R2_ACCESS_KEY_ID
MERCHANT_KNOWLEDGE_R2_SECRET_ACCESS_KEY
MERCHANT_KNOWLEDGE_MAX_UPLOAD_BYTES
MERCHANT_KNOWLEDGE_MAX_XLSX_UNCOMPRESSED_BYTES

EMBEDDING_PROVIDER
EMBEDDING_MODEL
EMBEDDING_DIMENSIONS
EMBEDDING_INDEX_VERSION
EMBEDDING_API_KEY
```

and expose:

```text
npm run start:merchant-knowledge-worker
npm run readiness:merchant-knowledge-worker
service readiness identity: moda-merchant-knowledge-worker
```

### Commerce

`ARCH-023-COMMERCE-001/002` read:

```text
EMBEDDING_PROVIDER
EMBEDDING_MODEL
EMBEDDING_DIMENSIONS
EMBEDDING_INDEX_VERSION
EMBEDDING_API_KEY

COMMERCE_BOOTSTRAP_ADMIN_EMAIL
```

Background and Commerce MUST receive identical embedding provider/model/dimensions/index-version for a given deployment environment.

## Scope

Authorized primary files:

```text
render.test.yaml
render.production.yaml

tests/validate-render-blueprints.sh
tests/validate-render-blueprints-negative.sh

docs/render-topology.md
docs/deployment-prerequisites.md
docs/merchant-knowledge-deployment.md
```

No application repository source code is modified.

## Out of Scope

- modifying `moda-interact`, `moda-interact-background`, `moda-interact-commerce` or `moda-interact-admin`;
- provisioning Merchant Knowledge Feature/plan data;
- creating PlatformAdmin users;
- application business logic;
- a new PostgreSQL database;
- a new Redis cluster;
- a new public/private Merchant Knowledge HTTP service;
- a Gateway/HAProxy route for Merchant Knowledge;
- a second object-storage provider;
- committing any R2/OpenAI credential value;
- choosing a different embedding provider;
- Admin/database configuration of embedding models;
- system-test fixtures.

## Requirements

### R1 — preserve current Blueprint source of truth

Modify both and only both current environment Blueprints:

```text
render.test.yaml
render.production.yaml
```

Do not create:

```text
render.yaml
```

Do not remove or rename existing services/env groups.

### R2 — add one shared Merchant Knowledge embedding group per environment

Add exactly:

```text
moda-interact-test-merchant-knowledge-embedding-config
moda-interact-production-merchant-knowledge-embedding-config
```

Each contains exactly:

```yaml
- key: EMBEDDING_PROVIDER
  value: openai
- key: EMBEDDING_MODEL
  sync: false
- key: EMBEDDING_DIMENSIONS
  sync: false
- key: EMBEDDING_INDEX_VERSION
  sync: false
- key: EMBEDDING_API_KEY
  sync: false
```

Do not reuse:

```text
OPENAI_API_KEY
COMMERCE_PREVIEW_API_KEY
WHATSAPP_OPENAI_API_KEY
```

as an implicit Merchant Knowledge embedding credential.

The same environment group must be attached to both:

```text
moda-merchant-knowledge-worker-<environment>
moda-interact-commerce-<environment>
```

This shared group is the deployment mechanism that prevents provider/model/dimensions/index-version drift between ingestion and lookup.

### R3 — add one shared private-R2 location group per environment

Add exactly:

```text
moda-interact-test-merchant-knowledge-r2-config
moda-interact-production-merchant-knowledge-r2-config
```

Each contains exactly:

```yaml
- key: MERCHANT_KNOWLEDGE_R2_ENDPOINT
  sync: false
- key: MERCHANT_KNOWLEDGE_R2_BUCKET
  sync: false
```

Do not commit Cloudflare account id, endpoint or bucket names.

The group must be attached only to:

```text
moda-interact-<environment>
moda-merchant-knowledge-worker-<environment>
```

Commerce does not receive R2 configuration.

### R4 — add separate R2 credential groups for Shopify and Background

Add exactly these per environment.

Shopify upload/finalisation credentials:

```text
moda-interact-<environment>-merchant-knowledge-r2-upload-credentials
```

Background processing/cleanup credentials:

```text
moda-interact-<environment>-merchant-knowledge-r2-background-credentials
```

Each group contains exactly:

```yaml
- key: MERCHANT_KNOWLEDGE_R2_ACCESS_KEY_ID
  sync: false
- key: MERCHANT_KNOWLEDGE_R2_SECRET_ACCESS_KEY
  sync: false
```

Attachment is exact:

```text
upload-credentials group
  -> moda-interact-<environment> only

background-credentials group
  -> moda-merchant-knowledge-worker-<environment> only
```

Do not attach both credential groups to the same service.

Do not attach either credential group to Commerce, Admin, Gateway, Messaging or unrelated Background workers.

### R5 — R2 credential/bucket deployment prerequisite

`docs/merchant-knowledge-deployment.md` must require for each environment:

1. one private Cloudflare R2 bucket dedicated to that environment;
2. no public `r2.dev`/custom-domain read exposure;
3. test and production bucket names MUST differ;
4. two distinct Cloudflare R2 S3 credential pairs:
   - Shopify upload signer/finaliser credential;
   - Background processor/cleanup credential;
5. each credential is scoped to the exact environment bucket only;
6. use Cloudflare R2 `Object Read & Write` bucket-scoped credentials, because the accepted Shopify/Background implementations require S3-compatible object operations;
7. never use account-wide/Admin R2 credentials;
8. never reuse test credentials in production or production credentials in test;
9. configure bucket CORS so browser uploads are allowed only from the exact deployed Moda Shopify application origin(s), with `PUT` and both `Content-Type` and `If-None-Match`; do not use `*` origins and do not create public GET/LIST access;
10. verify the accepted Shopify create-only signed PUT contract: the first PUT to a fresh generated key succeeds with `If-None-Match: *`, while replaying the same signed PUT/key after object creation fails with HTTP `412 PreconditionFailed` (or the equivalent non-success response) and cannot replace the existing object.

R2 CORS is a Cloudflare bucket prerequisite, not a Render Blueprint object. Document the exact operator step and verification; do not add a new Cloudflare Terraform/provider toolchain solely for this task.

The document must state that Cloudflare permanent R2 S3 credentials are bucket-scoped, not committed to Git, and are populated into the exact Render `sync:false` groups from R4.

Application code still performs no bucket-wide object listing for Merchant Knowledge.

Do not add a new Cloudflare Terraform/provider toolchain solely for ARCH-023.

### R6 — add one shared upload-safety group per environment

Add exactly:

```text
moda-interact-test-merchant-knowledge-upload-limits
moda-interact-production-merchant-knowledge-upload-limits
```

Each contains:

```yaml
- key: MERCHANT_KNOWLEDGE_MAX_UPLOAD_BYTES
  sync: false
- key: MERCHANT_KNOWLEDGE_MAX_XLSX_UNCOMPRESSED_BYTES
  sync: false
```

Attach the same group to:

```text
moda-interact-<environment>
moda-merchant-knowledge-worker-<environment>
```

Using one group guarantees `MERCHANT_KNOWLEDGE_MAX_UPLOAD_BYTES` is identical at upload issuance/finalisation and Background byte validation.

Shopify does not currently consume the XLSX uncompressed setting; receiving the extra non-secret value is acceptable and avoids duplicate limit groups.

Values are deployment configuration and are not chosen/committed by this task.

### R7 — deploy the dedicated Merchant Knowledge worker

Add test service exactly:

```yaml
- type: worker
  name: moda-merchant-knowledge-worker-test
  runtime: docker
  repo: https://github.com/kodjobaah/moda-interact-background.git
  plan: 0.5c-512mb
  numInstances: 1
  dockerCommand: npm run start:merchant-knowledge-worker
```

Add production service exactly:

```yaml
- type: worker
  name: moda-merchant-knowledge-worker-production
  runtime: docker
  repo: https://github.com/kodjobaah/moda-interact-background.git
  plan: 0.5c-1g
  numInstances: 1
  dockerCommand: npm run start:merchant-knowledge-worker
```

Attach exactly:

```text
environment common config
environment Redis config
environment Merchant Knowledge R2 config
environment Merchant Knowledge R2 background credentials
environment Merchant Knowledge upload limits
environment Merchant Knowledge embedding config
DATABASE_URL -> matching environment PostgreSQL
```

Do not attach:

```text
Shopify API credential group
WhatsApp credential group
translation config
transcription config
Merchant Knowledge R2 upload credentials
```

unless a later architecture explicitly proves the worker needs them.

The worker has no domains, no public route and no Gateway upstream.

Do not add `healthCheckPath` to the Render worker.

### R8 — wire Shopify private service

For existing:

```text
moda-interact-test
moda-interact-production
```

add exactly:

```text
Merchant Knowledge R2 config group
Merchant Knowledge R2 upload credentials group
Merchant Knowledge upload limits group
```

Do not attach:

```text
Merchant Knowledge R2 background credentials
Merchant Knowledge embedding config
EMBEDDING_API_KEY
```

to Shopify.

Do not change its repository, plan, instance count, `preDeployCommand`, database or existing Shopify/Redis groups.

### R9 — wire Commerce private service

For existing:

```text
moda-interact-commerce-test
moda-interact-commerce-production
```

attach exactly:

```text
Merchant Knowledge embedding config group
```

and add service-level:

```yaml
- key: COMMERCE_BOOTSTRAP_ADMIN_EMAIL
  sync: false
```

Do not attach any R2 group/credential/limit to Commerce.

Do not change its repository, build command, start command, database wiring or existing Commerce auth/preview configuration.

### R10 — embedding configuration must be identical by construction

Blueprint validation must reject a design where Background and Commerce define individual service-level values for any:

```text
EMBEDDING_PROVIDER
EMBEDDING_MODEL
EMBEDDING_DIMENSIONS
EMBEDDING_INDEX_VERSION
EMBEDDING_API_KEY
```

Both services must consume the one environment-specific group from R2.

No other service requires that group in ARCH-023.

### R11 — no new Merchant Knowledge network surface

Do not add:

```text
MODA_MERCHANT_KNOWLEDGE_UPSTREAM
Merchant Knowledge public host
HAProxy backend/frontend
Gateway route
Render web service
Render private HTTP service
```

Merchant Knowledge ingestion is Shopify -> PostgreSQL/BullMQ/R2 -> Background.
Lookup is through the existing Commerce service/MCP.

### R12 — preserve environment isolation

Test services use only:

```text
*-test groups
moda-interact-postgres-test
test R2 bucket/credentials
```

Production services use only:

```text
*-production groups
moda-interact-postgres-production
production R2 bucket/credentials
```

Blueprint validator must fail any cross-environment group/database reference.

### R13 — PostgreSQL/pgvector prerequisite

Do not create another database.

Deployment documentation must require:

```text
ARCH-023 database migration has successfully applied
CREATE EXTENSION vector succeeded
```

before Merchant Knowledge worker/Commerce lookup acceptance.

The existing environment PostgreSQL remains authoritative.

### R14 — Commerce bootstrap deployment prerequisites

Before deploying/restarting Commerce with COMMERCE-002 startup bootstrap enabled, operators must verify:

```text
COMMERCE_BOOTSTRAP_ADMIN_EMAIL
  -> existing active SUPER_ADMIN in same database/environment

Feature.key = merchant_knowledge
  -> provisioned/reconciled through supported ADMIN-001 + ADMIN-004 workflow
  -> active
  -> MERCHANT_OPT_IN
  -> systemRequired=false
```

Gateway does not create either database row.

The deployment documentation must state that Commerce startup is expected to fail closed when these prerequisites are absent.

### R15 — rollout order

Document this exact environment rollout order:

```text
1. Apply/verify ARCH-023 database migration and pgvector extension.
2. Populate environment-specific R2 groups, upload limits and embedding group.
3. Verify private R2 bucket + separate Shopify/Background credentials.
4. Deploy accepted Admin revision and reconcile/verify `merchant_knowledge` as `MERCHANT_OPT_IN`; verify explicit plan configurations.
5. Deploy dedicated Merchant Knowledge Background worker and verify Redis/PostgreSQL/R2/embedding configuration.
6. Verify private R2 bucket CORS allows preflight/PUT from the exact deployed Shopify application origin with `Content-Type` and `If-None-Match`, then prove first create-only PUT succeeds and replay to the same key is rejected without replacement; verify no public read/list exposure.
7. Deploy accepted Shopify revision with Merchant Knowledge configuration/R2 upload support.
8. Verify COMMERCE_BOOTSTRAP_ADMIN_EMAIL identifies an active SUPER_ADMIN.
9. Deploy/restart accepted Commerce revisions including the post-COMMERCE-002 activation follow-up.
10. Verify Commerce bootstrap succeeds and Merchant Knowledge operation can initialize.
11. Proceed to developer/manual and terminal system-test validation.
```

Do not deploy Commerce before steps 1, 5 and 9.

### R16 — rollback documentation

Document:

- removing/stopping the Merchant Knowledge worker does not delete PostgreSQL/R2 data;
- Shopify Merchant Knowledge upload UI must not be considered operational while worker is intentionally disabled;
- rolling Commerce back to a version without ARCH-023 must not delete capability/source data;
- never destroy the R2 bucket as application rollback;
- do not revoke R2 credentials until affected services are stopped/rolled back;
- database schema rollback is not performed destructively as part of service rollback.

### R17 — observability

The dedicated worker receives the existing environment common config, including the existing OTEL/Loki settings.

Do not create a new telemetry backend.

Expected service identity is application-owned:

```text
moda-merchant-knowledge-worker
```

Gateway Blueprint service name remains:

```text
moda-merchant-knowledge-worker-test
moda-merchant-knowledge-worker-production
```

If accepted BACKGROUND-005 start command does not initialise the repository's normal worker observability bootstrap, STOP and report the missing Background capability rather than editing Background from this task.

### R18 — positive Blueprint validator

Extend:

```text
tests/validate-render-blueprints.sh
```

for both environments.

It must assert exactly:

#### New env groups exist once

```text
merchant-knowledge-embedding-config
merchant-knowledge-r2-config
merchant-knowledge-r2-upload-credentials
merchant-knowledge-r2-background-credentials
merchant-knowledge-upload-limits
```

with the R2-R6 exact key/value-vs-sync:false shapes.

#### Worker

```text
exact service name
type=worker
runtime=docker
repo=moda-interact-background
dockerCommand=npm run start:merchant-knowledge-worker
numInstances=1
test plan=0.5c-512mb
production plan=0.5c-1g
matching DATABASE_URL
required fromGroup set exactly contains:
  common
  redis
  r2 config
  r2 background credentials
  upload limits
  embedding config
```

No domains/healthCheckPath.

#### Shopify

Requires:

```text
r2 config
r2 upload credentials
upload limits
```

and forbids:

```text
r2 background credentials
embedding group
```

#### Commerce

Requires:

```text
embedding group
COMMERCE_BOOTSTRAP_ADMIN_EMAIL sync:false exactly once
```

and forbids every R2 group.

#### Secret hygiene

Every key below is `sync:false` and has no committed `value`:

```text
MERCHANT_KNOWLEDGE_R2_ENDPOINT
MERCHANT_KNOWLEDGE_R2_BUCKET
MERCHANT_KNOWLEDGE_R2_ACCESS_KEY_ID
MERCHANT_KNOWLEDGE_R2_SECRET_ACCESS_KEY
MERCHANT_KNOWLEDGE_MAX_UPLOAD_BYTES
MERCHANT_KNOWLEDGE_MAX_XLSX_UNCOMPRESSED_BYTES
EMBEDDING_MODEL
EMBEDDING_DIMENSIONS
EMBEDDING_INDEX_VERSION
EMBEDDING_API_KEY
COMMERCE_BOOTSTRAP_ADMIN_EMAIL
```

Only:

```text
EMBEDDING_PROVIDER=openai
```

is committed.

### R19 — negative Blueprint validator

Extend:

```text
tests/validate-render-blueprints-negative.sh
```

with mutations proving validation fails for at least:

```text
Merchant Knowledge worker missing
wrong worker repo
wrong worker dockerCommand
worker uses wrong environment database
worker missing Redis group
worker missing embedding group
worker given upload-signer credentials

Shopify missing upload credentials
Shopify given Background R2 credentials
Shopify given embedding group

Commerce missing embedding group
Commerce given R2 credentials
Commerce missing COMMERCE_BOOTSTRAP_ADMIN_EMAIL

embedding values duplicated service-level instead of shared group
test service references production Merchant Knowledge group
production service references test Merchant Knowledge group

committed R2 credential value
committed EMBEDDING_API_KEY
new Merchant Knowledge web/pserv service or Gateway upstream added
```

### R20 — deployment documentation

Create:

```text
docs/merchant-knowledge-deployment.md
```

It must contain:

1. service topology;
2. exact test/production env-group names;
3. exact variable names;
4. which values are secret/deployment-entered;
5. R2 bucket/credential/CORS requirements from R5, including exact-origin browser PUT preflight, `If-None-Match` allowance and create-only replay rejection verification;
6. upload-limit consistency rule;
7. embedding identity rule;
8. Commerce bootstrap prerequisites;
9. rollout order;
10. rollback behavior;
11. statement that there is no new Merchant Knowledge HTTP route/service.

Update:

```text
docs/render-topology.md
docs/deployment-prerequisites.md
```

to link/reference this contract rather than duplicating conflicting instructions.

## Work Items

- [ ] Add five Merchant Knowledge env groups to test Blueprint.
- [ ] Add five Merchant Knowledge env groups to production Blueprint.
- [ ] Add dedicated test Merchant Knowledge worker.
- [ ] Add dedicated production Merchant Knowledge worker.
- [ ] Attach exact R2 groups to Shopify.
- [ ] Attach exact R2/embedding groups to Merchant Knowledge worker.
- [ ] Attach exact embedding group/bootstrap-admin key to Commerce.
- [ ] Preserve all existing service topology/routing.
- [ ] Extend positive Blueprint validation.
- [ ] Extend negative Blueprint validation.
- [ ] Add Merchant Knowledge deployment contract, including exact-origin R2 browser create-only PUT CORS prerequisite/replay verification.
- [ ] Update topology/prerequisite docs.
- [ ] Run all required Gateway validation.

## Interfaces / Contracts

Deploys accepted application contracts from:

```text
ARCH-023-SHOPIFY-005
ARCH-023-BACKGROUND-005
ARCH-023-COMMERCE-002
```

Canonical worker:

```text
repo:          moda-interact-background
command:       npm run start:merchant-knowledge-worker
service names: moda-merchant-knowledge-worker-test
               moda-merchant-knowledge-worker-production
```

No new network interface is created.

## Dependencies

- `ARCH-023-BACKGROUND-005`
- `ARCH-023-BACKGROUND-008`
- `ARCH-023-SHOPIFY-005`
- `ARCH-023-COMMERCE-002`

All must be Complete and architect-accepted before this task becomes Ready. `ARCH-023-BACKGROUND-008` is the bounded Background-owned correction materialised after Attempt 1 exercised the R17 stop condition.

## Enables

No terminal system-test task is materialised by this task.

After Gateway acceptance, ARCH-023 developer/manual validation and final system tests may depend on this task.

## Acceptance Criteria

- [ ] Dedicated Merchant Knowledge worker exists in both Render Blueprints.
- [ ] Worker uses exact accepted Background start command.
- [ ] Worker has Redis/PostgreSQL/common observability wiring.
- [ ] Test/production worker topology is environment-isolated.
- [ ] Shopify and Background use separate R2 credentials.
- [ ] Private R2 bucket CORS permits only exact deployed Shopify-app origin(s) for browser PUT with `Content-Type` and `If-None-Match`, and creates no public read/list surface.
- [ ] A deployed-origin create-only presigned PUT succeeds once and replay to the same key is rejected without replacing the object.
- [ ] R2 endpoint/bucket configuration is shared only between Shopify and Merchant Knowledge worker.
- [ ] R2 credentials are never attached to Commerce.
- [ ] Shopify does not receive embedding credentials.
- [ ] Background and Commerce consume one identical embedding group per environment.
- [ ] `EMBEDDING_PROVIDER` is exactly `openai`.
- [ ] No embedding/R2 secret value is committed.
- [ ] Commerce receives `COMMERCE_BOOTSTRAP_ADMIN_EMAIL` as deployment-entered configuration.
- [ ] No new Merchant Knowledge HTTP service/Gateway route exists.
- [ ] Current PostgreSQL/Redis services are reused.
- [ ] Deployment and rollback sequencing are documented.
- [ ] Positive and required negative Blueprint validations pass.

## Validation

Run at minimum:

```bash
bash tests/validate-render-blueprints.sh
bash tests/validate-render-blueprints-negative.sh
bash tests/validate-observability-config.sh
bash scripts/developer-validation.sh
git diff --check
```

Also parse both Blueprint YAML files with the repository's existing YAML validation mechanism.

Also perform/document one deployed-origin R2 preflight + presigned PUT validation using the accepted Shopify upload flow. The validation MUST send the accepted `Content-Type` and `If-None-Match: *` headers, prove the first PUT succeeds, and prove replaying the same signed PUT/key is rejected without replacing the object.

If application task outputs differ from the exact dependency contracts recorded above, STOP and return the mismatch to `moda_architect`; do not silently alter application commands/env names in Gateway.

## Stop Condition

After all Work Items, Acceptance Criteria and Validation are complete:

1. complete the Completion Report;
2. set task status to `review`;
3. clear the active execution claim according to the normal protocol;
4. return control to `moda_architect`;
5. STOP.

Do not begin developer validation or system-test tasks.

## Implementation Notes

This task intentionally keeps all ARCH-023 infrastructure in one Gateway task because it is one deployment topology boundary.

The two R2 credential groups are separate so Shopify and Background credentials can be independently rotated/revoked and are never shared across services.

The embedding group is intentionally shared because ingestion vectors and lookup query vectors are compatible only when provider/model/dimensions/index-version agree exactly.

The Gateway repository does not currently contain a Cloudflare provisioning toolchain. This task therefore codifies Render wiring and exact external R2 prerequisites without introducing a second infrastructure framework solely for one bucket.

## Completion Report

### Status

Blocked pending the Background-owned Merchant Knowledge observability bootstrap required by R17.

### Files Changed

No Gateway implementation files changed. This task stopped before deployment wiring.

### Work Completed

Inspected the accepted worker start contract and confirmed that `moda-interact-background/package.json` starts the Merchant Knowledge worker with `node dist/entrypoints/merchant-knowledge.js`. The entrypoint does not initialize observability; it only imports the shutdown helper. Existing Background worker start commands preload worker-specific `observability/*.mjs` modules, but no `observability/merchant-knowledge.mjs` exists.

This violates R17, which requires stopping and reporting the missing Background capability rather than editing Background from Gateway. `moda_architect` confirmed the gap and recommended a focused Background corrective task. Gateway remains blocked until that correction is accepted and the dependency is reconciled by the architect.

### Validation Results

No Blueprint or deployment validation was run because R17 blocks implementation. The required deployed-origin R2 CORS/presigned-PUT check and `bash tests/run-tests.sh` remain developer-owned validations after implementation; neither was run.

### Deviations

Stopped before all Gateway work items by design, as required by R17. No Blueprint, validator, or deployment documentation files were modified.

### Assumptions

The Gateway task must remain blocked until the Background worker initializes the repository's normal observability bootstrap.

### Unresolved Issues

Background must provide and validate normal observability initialization for `moda-merchant-knowledge-worker` before Gateway deployment topology can be safely wired.

### Architectural Concerns

The declared worker readiness/start contract currently omits the observability preload used by sibling Background workers. `moda_architect` should create or assign the Background corrective task and reconcile Gateway's dependency/status after acceptance.

## Architect Review

### Review Status

Blocked — Attempt 1

### Review Notes

The R17 stop is valid. The accepted deployment-facing command is `npm run start:merchant-knowledge-worker`, but the current Background package script resolves directly to `node dist/entrypoints/merchant-knowledge.js`. The Merchant Knowledge worker therefore does not preload the repository's accepted shared Node observability runtime before application/Prisma worker imports, unlike the sibling Background worker processes established by ARCH-002.

This is a Background-owned startup capability, not Gateway configuration. Gateway correctly stopped before editing Blueprints or application repositories and must not invent a replacement worker command, telemetry backend, service-local SDK or Gateway-owned preload.

A bounded corrective task, `ARCH-023-BACKGROUND-008`, is materialised to add the missing shared-runtime preload/profile while preserving the existing package-script name and logical service identity `moda-merchant-knowledge-worker`.

### Reviewed Files

- `docs/decisions/gateway/ARCH-023/GATEWAY-001-wire-merchant-knowledge-deployment.md`
- `docs/decisions/background/ARCH-002/BACKGROUND-005-adopt-shared-observability-runtime.md`
- `docs/observability/shared-observability-runtime.md`
- accepted ARCH-023 Background entrypoint/start-command evidence recorded in `BACKGROUND-004` and `BACKGROUND-005`
- ARCH-002 reference Background observability preload profiles

### Validation Reviewed

Reviewed the durable Gateway blocker evidence and the accepted Background observability architecture. No Gateway Blueprint/deployment validation is required while R17's explicit stop condition is active. No Gateway source change is requested.

### Architecture Conformance

Conforms. R17 intentionally prevents Gateway from compensating for an application-owned observability omission. Shared observability initialization belongs to `moda_background`; Gateway owns only deployment topology/configuration after the accepted application start contract is deployable.

### Follow-up

1. `ARCH-023-BACKGROUND-008` is Ready and must add the Merchant Knowledge worker's normal shared observability preload without changing business processing or the Gateway-facing script name.
2. `ARCH-023-GATEWAY-001` remains Blocked at Attempt 1 with its claim cleared and now depends on BACKGROUND-008 in addition to its already-complete dependencies.
3. After BACKGROUND-008 is architect-accepted Complete, reconcile this same Gateway task `blocked -> ready`, preserving `attempt: 1`; the next `/moda-task ARCH-023-GATEWAY-001` claim becomes Attempt 2.
4. Gateway Attempt 2 then performs the original Blueprint/deployment work and validation. Do not create a replacement Gateway task.
