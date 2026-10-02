---
id: ARCH-024-GATEWAY-001
architecture_id: ARCH-024
title: Wire database-backed OpenRouter runtime configuration
task_kind: implementation
domain: gateway
repository: moda-interact-gateway
assigned_agent: moda_gateway
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 60
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-020-GATEWAY-003
  - ARCH-024-ADMIN-003
  - ARCH-024-COMMERCE-007
  - ARCH-024-BACKGROUND-001
enables: []
created: 2026-10-01
updated: 2026-10-02
---

# Wire database-backed OpenRouter runtime configuration

## Architecture

Architecture ID:

`ARCH-024`

Architecture document:

`docs/architecture/ARCH-024-commerce-agent-model-runtime-and-test-conversations.md`

Coordinator:

`moda_architect`

## Objective

Make the Render Blueprint match the accepted ARCH-024 model-runtime boundary:

1. remove all static Preview model/provider/API-key deployment inputs;
2. preserve `COMMERCE_PREVIEW_ENABLED` as the only Preview model-execution kill switch;
3. reuse the existing Commerce credential encryption keyring established by ARCH-020 rather than adding an OpenRouter-specific secret;
4. make the **same decryption keyring** available, with least privilege, to:
   - Admin, for OpenRouter credential SET/REPLACE encryption;
   - Commerce, for Test Conversation OpenRouter credential decryption and existing External Connection credential operations;
   - the Background messaging worker, for production CommerceAgent OpenRouter credential decryption;
5. keep the active encryption-key selector available only to credential writers (Admin and Commerce), not the Background messaging worker;
6. keep the External Connection command-HMAC secret Commerce-only;
7. preserve the existing Groq transcription credential/configuration independently from CommerceAgent model execution.

The resulting deployment topology MUST make ordinary OpenRouter API-key rotation a **database/admin operation** that does not require a Render secret change or service restart.

The task owns Blueprint/configuration source and operator documentation only. It MUST NOT deploy live services, generate real secrets, create an OpenRouter credential row, or alter application business logic.

## Context

The current integrated Render Blueprint still carries the ARCH-020/021 Preview model configuration:

```text
COMMERCE_PREVIEW_ENABLED
COMMERCE_PREVIEW_PROVIDER
COMMERCE_PREVIEW_MODEL
COMMERCE_PREVIEW_API_KEY
```

Current `render.test.yaml` additionally fixes:

```text
COMMERCE_PREVIEW_PROVIDER=groq
COMMERCE_PREVIEW_MODEL=openai/gpt-oss-20b
```

and injects `COMMERCE_PREVIEW_API_KEY` into the private Commerce service.

Current `render.production.yaml` exposes the provider/model/key as service-level external inputs.

ARCH-024 replaces that design:

```text
Admin Model Catalogue + Model Availability
        ↓
Commerce Studio selects one effective active model
        ↓
model identity/configuration stored in PostgreSQL
        ↓
OpenRouter credential stored encrypted in PostgreSQL
        ↓
Admin / Commerce / Background share only the encryption keyring required
for their bounded responsibilities
```

ARCH-024-ADMIN-003 uses:

```text
COMMERCE_CONNECTION_KEYS_JSON
COMMERCE_CONNECTION_ACTIVE_KEY_ID
```

for SET/REPLACE encryption of the environment's `CommerceOpenRouterCredential`.

ARCH-024-COMMERCE-007 uses:

```text
COMMERCE_CONNECTION_KEYS_JSON
```

for decryption before each Test Conversation model invocation. It does **not** need the active key ID merely to decrypt an existing row.

ARCH-024-BACKGROUND-001 uses:

```text
COMMERCE_CONNECTION_KEYS_JSON
```

for decryption before each production CommerceAgent model invocation. It also does **not** need the active key ID merely to decrypt an existing row.

ARCH-020-GATEWAY-003 establishes the existing External Connection credential runtime and owns the original configuration names:

```text
COMMERCE_CONNECTION_KEYS_JSON
COMMERCE_CONNECTION_ACTIVE_KEY_ID
COMMERCE_CONNECTION_COMMAND_HMAC_KEY
```

That accepted implementation is a prerequisite. ARCH-024 extends the keyring's deployment scope deliberately; it does not create a second encryption root.

The existing messaging worker still needs `GROQ_API_KEY` through the existing AI/transcription path. ARCH-024-BACKGROUND-001 explicitly preserves that independent speech-transcription use. Do not remove it merely because CommerceAgent model execution moves to OpenRouter.

## Scope

Primary implementation targets in `moda-interact-gateway/`:

```text
render.test.yaml
render.production.yaml

tests/validate-render-blueprints.sh
tests/validate-render-blueprints-negative.sh

docs/commerce-deployment.md
```

Additional Gateway-owned files may be changed only when mechanically required to keep the accepted Blueprint validation/runbook consistent with this task. Every additional file MUST be named and justified in the Completion Report.

### Required target topology

For each Render environment (`test`, `production`) create exactly these two ARCH-024 shared groups:

```yaml
envVarGroups:
  - name: moda-interact-<environment>-commerce-credential-keyring
    envVars:
      - key: COMMERCE_CONNECTION_KEYS_JSON
        sync: false

  - name: moda-interact-<environment>-commerce-credential-writer-config
    envVars:
      - key: COMMERCE_CONNECTION_ACTIVE_KEY_ID
        sync: false
```

Do not add any other key to either group.

Attach the groups exactly as follows:

```text
moda-interact-admin-<environment>
    commerce-credential-keyring
    commerce-credential-writer-config

moda-interact-commerce-<environment>
    commerce-credential-keyring
    commerce-credential-writer-config

moda-messaging-worker-<environment>
    commerce-credential-keyring ONLY
```

No other service/worker may reference either group.

`COMMERCE_CONNECTION_COMMAND_HMAC_KEY` remains a Commerce-only service-level secret as established by accepted ARCH-020-GATEWAY-003. Do not attach it to Admin or Background.

### Required final Preview configuration

The existing Commerce config group MUST contain exactly the existing Admin origin plus the Preview kill switch for this concern:

```yaml
- name: moda-interact-test-commerce-config
  envVars:
    - key: ADMIN_ORIGIN
      value: https://admin-test.modainteract.com
    - key: COMMERCE_PREVIEW_ENABLED
      value: "true"
```

```yaml
- name: moda-interact-production-commerce-config
  envVars:
    - key: ADMIN_ORIGIN
      value: https://admin.modainteract.com
    - key: COMMERCE_PREVIEW_ENABLED
      value: "false"
```

The following keys MUST be absent from **both** Blueprint files, all environment groups, and all service-level env-var declarations:

```text
COMMERCE_PREVIEW_PROVIDER
COMMERCE_PREVIEW_MODEL
COMMERCE_PREVIEW_API_KEY
OPENROUTER_API_KEY
COMMERCE_OPENROUTER_API_KEY
GROQ_COMMERCE_MODEL
```

Do not replace them with differently named static model/provider/API-key variables.

### Exact variable-ownership matrix

The accepted Blueprint after this task MUST satisfy this matrix:

| Variable / group | Admin | Commerce | Messaging worker | Other services/workers |
|---|---:|---:|---:|---:|
| common `DEPLOYMENT_ENVIRONMENT_NAME` | yes | yes | yes | existing topology unchanged |
| `commerce-credential-keyring` group | yes | yes | yes | **no** |
| `COMMERCE_CONNECTION_KEYS_JSON` | via group | via group | via group | **absent** |
| `commerce-credential-writer-config` group | yes | yes | **no** | **no** |
| `COMMERCE_CONNECTION_ACTIVE_KEY_ID` | via group | via group | **absent** | **absent** |
| `COMMERCE_CONNECTION_COMMAND_HMAC_KEY` | **absent** | service-level `sync:false` | **absent** | **absent** |
| `COMMERCE_PREVIEW_ENABLED` | absent | via Commerce config group | absent | absent |
| `COMMERCE_PREVIEW_PROVIDER` | absent | absent | absent | absent |
| `COMMERCE_PREVIEW_MODEL` | absent | absent | absent | absent |
| `COMMERCE_PREVIEW_API_KEY` | absent | absent | absent | absent |
| `OPENROUTER_API_KEY` / equivalent | absent | absent | absent | absent |
| `GROQ_API_KEY` | existing Admin state unchanged | existing Commerce state unchanged | retain existing AI/transcription wiring | existing topology unchanged |

The matrix is a least-privilege contract, not documentation commentary.

## Out of Scope

- Live Render deployment or Blueprint sync in the Render dashboard.
- Generating, rotating or disclosing any real encryption key or API credential.
- Creating/updating/deleting `CommerceOpenRouterCredential` database rows.
- Admin credential UI/source implementation; ARCH-024-ADMIN-003 owns it.
- Commerce model runtime/source implementation; ARCH-024-COMMERCE-007 owns it.
- Background model runtime/source implementation; ARCH-024-BACKGROUND-001 owns it.
- Model Catalogue/Availability persistence or UI.
- Changing the ARCH-024 effective active-model rules.
- Changing Tool execution, MCP authorization or private/public routing.
- Changing the actual value of `COMMERCE_PREVIEW_ENABLED` for test or production.
- Removing `GROQ_API_KEY` while it remains required by WhatsApp speech transcription.
- Changing transcription provider/model configuration.
- Encryption-key re-encryption tooling.
- OpenRouter API-key validation/network calls.
- Adding LangChain/OpenRouter packages to Gateway.
- Adding a new service, worker, database, Redis instance or public route.

## Requirements

### R1 — depend on the accepted application capabilities before removing legacy deployment inputs

Do not claim or execute this task until every dependency in YAML is architect-accepted Complete.

In particular:

- ARCH-020-GATEWAY-003 must already establish the Commerce External Connection credential runtime and original keyring/HMAC configuration;
- ARCH-024-ADMIN-003 must already implement encrypted OpenRouter credential SET/REPLACE/REMOVE;
- ARCH-024-COMMERCE-007 must already stop reading `COMMERCE_PREVIEW_PROVIDER`, `COMMERCE_PREVIEW_MODEL` and `COMMERCE_PREVIEW_API_KEY`;
- ARCH-024-BACKGROUND-001 must already consume the database-backed OpenRouter model runtime and require only the decrypt keyring for credential access.

If any accepted dependency still requires a key that this task says to remove, STOP and return the contradiction to `moda_architect`. Do not remove a still-required runtime input and do not silently retain stale architecture.

### R2 — create one shared decryption-keyring group per Render environment

In both Blueprints create exactly:

```text
moda-interact-test-commerce-credential-keyring
moda-interact-production-commerce-credential-keyring
```

Each group contains exactly:

```yaml
- key: COMMERCE_CONNECTION_KEYS_JSON
  sync: false
```

No default/example/placeholder key material may be committed.

Do not duplicate `COMMERCE_CONNECTION_KEYS_JSON` as service-level `sync:false` entries after the group exists.

The purpose of this group is to guarantee that Admin, Commerce and the production CommerceAgent worker receive the **same environment keyring** rather than three independently entered copies.

### R3 — create one shared writer-config group per Render environment

In both Blueprints create exactly:

```text
moda-interact-test-commerce-credential-writer-config
moda-interact-production-commerce-credential-writer-config
```

Each contains exactly:

```yaml
- key: COMMERCE_CONNECTION_ACTIVE_KEY_ID
  sync: false
```

Although the key ID is not secret, it is operator-controlled rotation state and MUST NOT be hard-coded in Git.

Attach this group only to Admin and Commerce because those are the two credential writers:

- Admin writes OpenRouter credentials;
- Commerce retains existing External Connection credential mutation responsibilities.

The Background messaging worker is decrypt-only and MUST NOT receive `COMMERCE_CONNECTION_ACTIVE_KEY_ID`.

### R4 — attach the keyring group only to the three authorized runtimes

For both environments:

#### Admin

`moda-interact-admin-<environment>` MUST reference:

```text
moda-interact-<environment>-commerce-credential-keyring
moda-interact-<environment>-commerce-credential-writer-config
```

Admin needs:

```text
COMMERCE_CONNECTION_KEYS_JSON
COMMERCE_CONNECTION_ACTIVE_KEY_ID
```

for ARCH-024-ADMIN-003 SET/REPLACE encryption.

#### Commerce

`moda-interact-commerce-<environment>` MUST reference both groups.

Commerce needs:

```text
COMMERCE_CONNECTION_KEYS_JSON
```

for ARCH-024-COMMERCE-007 OpenRouter credential decryption and existing External Connection credential reads, plus:

```text
COMMERCE_CONNECTION_ACTIVE_KEY_ID
```

for the accepted External Connection credential write path.

#### Background messaging worker

`moda-messaging-worker-<environment>` MUST reference **only**:

```text
moda-interact-<environment>-commerce-credential-keyring
```

It needs only `COMMERCE_CONNECTION_KEYS_JSON` for ARCH-024-BACKGROUND-001 decryption.

Do not attach either group to:

```text
moda-interact-<environment>
moda-interact-messaging-<environment>
moda-shopify-event-worker-<environment>
moda-billing-worker-<environment>
moda-recovery-worker-<environment>
moda-merchant-communications-worker-<environment>
moda-interact-gateway-<environment>
```

or any later unrelated runtime.

### R5 — keep the External Connection command-HMAC secret Commerce-only

Preserve accepted ARCH-020-GATEWAY-003 ownership of:

```text
COMMERCE_CONNECTION_COMMAND_HMAC_KEY
```

It MUST remain attached only to:

```text
moda-interact-commerce-test
moda-interact-commerce-production
```

as service-level `sync:false` input unless the accepted GATEWAY-003 implementation provides an architect-approved equivalent Commerce-only source.

Do not put this secret in either new shared group.

Admin and Background do not need the command-HMAC key.

### R6 — remove static Preview provider/model/API-key configuration completely

Delete all declarations of:

```text
COMMERCE_PREVIEW_PROVIDER
COMMERCE_PREVIEW_MODEL
COMMERCE_PREVIEW_API_KEY
```

from both Blueprints.

This includes:

- test Commerce config group provider/model values;
- production Commerce service provider/model `sync:false` entries;
- test and production `COMMERCE_PREVIEW_API_KEY` service-level entries;
- validation fixtures/allowlists that treat these as required or permitted deployment inputs;
- operator documentation that instructs users to configure them.

After this task, searching the Gateway repository for those three names may return only deliberately historical architecture/task material outside this repository's runtime/config/docs scope; no active Gateway Blueprint, validation script or operator runbook may require them.

### R7 — preserve `COMMERCE_PREVIEW_ENABLED` exactly

Do not remove or rename:

```text
COMMERCE_PREVIEW_ENABLED
```

Its values remain:

```text
test        -> "true"
production  -> "false"
```

It remains in the existing environment-specific Commerce config group.

Do not add a second Preview model-execution switch.

### R8 — prohibit replacement plaintext/static model secrets

Both Blueprint validators MUST reject introduction of any of:

```text
OPENROUTER_API_KEY
COMMERCE_OPENROUTER_API_KEY
COMMERCE_MODEL_API_KEY
COMMERCE_MODEL_PROVIDER
COMMERCE_MODEL_ID
GROQ_COMMERCE_MODEL
```

or the legacy Preview provider/model/key variables.

Do not invent a renamed static secret merely to satisfy the new runtime.

This does not prohibit independent provider configuration owned by unrelated functionality such as translation or speech transcription.

### R9 — preserve Groq transcription configuration independently

The messaging worker currently consumes the existing AI/transcription configuration used by WhatsApp speech transcription.

Do not remove:

```text
GROQ_API_KEY
WHATSAPP_TRANSCRIPTION_PROVIDER
GROQ_TRANSCRIPTION_MODEL
OPENAI_TRANSCRIPTION_MODEL
```

or `WHATSAPP_OPENAI_API_KEY` merely because CommerceAgent model execution no longer uses Groq directly.

The Blueprint validation must continue proving that transcription configuration remains on its existing authorized worker boundary.

### R10 — update Blueprint validation to enforce the exact new groups and attachments

Update `tests/validate-render-blueprints.sh` so its expected group map includes exactly:

```text
commerce_keyring
commerce_credential_writer
```

mapping to:

```text
moda-interact-<environment>-commerce-credential-keyring
moda-interact-<environment>-commerce-credential-writer-config
```

Expected group keys:

```text
commerce_keyring:
    COMMERCE_CONNECTION_KEYS_JSON

commerce_credential_writer:
    COMMERCE_CONNECTION_ACTIVE_KEY_ID
```

Expected service group attachments become:

```text
moda-interact-admin-<environment>
    common
    redis
    admin_auth
    commerce_keyring
    commerce_credential_writer

moda-interact-commerce-<environment>
    common
    redis
    commerce
    commerce_keyring
    commerce_credential_writer

moda-messaging-worker-<environment>
    common
    redis
    shopify_api
    whatsapp
    ai
    transcription
    commerce_keyring
```

All other existing service/group relationships remain unchanged unless the accepted ARCH-020-GATEWAY-003 baseline already added an explicitly required Commerce-only group that must be preserved.

The validator MUST additionally prove:

1. both new groups exist exactly once;
2. the keyring group contains exactly one `sync:false` key and no value;
3. the writer group contains exactly one `sync:false` key and no value;
4. only the three authorized runtimes receive the keyring group;
5. only Admin and Commerce receive the writer group;
6. `COMMERCE_CONNECTION_COMMAND_HMAC_KEY` is Commerce-only;
7. legacy/static model variables in R8 are absent everywhere;
8. `COMMERCE_PREVIEW_ENABLED` remains exactly one Commerce config-group entry with the required environment-specific value;
9. `GROQ_API_KEY`/transcription wiring remains unchanged where required;
10. no committed secret values appear in the new groups.

### R11 — extend negative Blueprint validation with explicit architecture failures

Add deterministic negative cases to `tests/validate-render-blueprints-negative.sh` (or its existing fixture mechanism) covering at least:

```text
N1  keyring group missing
N2  keyring group contains committed value
N3  keyring group attached to recovery worker
N4  keyring group absent from Admin
N5  keyring group absent from Commerce
N6  keyring group absent from messaging worker
N7  writer group attached to messaging worker
N8  writer group absent from Admin
N9  writer group absent from Commerce
N10 COMMERCE_CONNECTION_COMMAND_HMAC_KEY attached to Admin
N11 COMMERCE_CONNECTION_COMMAND_HMAC_KEY attached to messaging worker
N12 COMMERCE_PREVIEW_PROVIDER reintroduced
N13 COMMERCE_PREVIEW_MODEL reintroduced
N14 COMMERCE_PREVIEW_API_KEY reintroduced
N15 OPENROUTER_API_KEY or COMMERCE_OPENROUTER_API_KEY introduced
N16 GROQ_COMMERCE_MODEL introduced
N17 COMMERCE_PREVIEW_ENABLED removed
N18 test COMMERCE_PREVIEW_ENABLED != "true"
N19 production COMMERCE_PREVIEW_ENABLED != "false"
```

Each mutation must fail the positive validator for the intended reason. Do not satisfy this requirement with one generic malformed-YAML case.

### R12 — update the Commerce deployment runbook with exact secret ownership

Update `docs/commerce-deployment.md` to describe the final ARCH-024 boundary.

The runbook MUST state explicitly:

```text
Model selection:
    PostgreSQL / Agent Configuration

Model configuration:
    PostgreSQL / CommerceModelCatalogueEntry.configuration

OpenRouter API credential:
    encrypted PostgreSQL CommerceOpenRouterCredential

Encryption/decryption keyring:
    Render COMMERCE_CONNECTION_KEYS_JSON

Encryption active key ID:
    Render COMMERCE_CONNECTION_ACTIVE_KEY_ID
    Admin + Commerce only

External Connection command HMAC:
    Render COMMERCE_CONNECTION_COMMAND_HMAC_KEY
    Commerce only
```

It MUST distinguish two rotations:

#### Ordinary OpenRouter credential rotation

```text
Admin -> replace encrypted CommerceOpenRouterCredential row
        -> next Commerce/Background model invocation uses replacement credential
        -> NO Render environment change
        -> NO Commerce/Background restart required by ARCH-024
```

#### Encryption-keyring rotation

This is rare infrastructure work and may restart services when Render environment values change.

Document the safe order:

```text
1. generate a new 32-byte encryption key outside source control;
2. add it to COMMERCE_CONNECTION_KEYS_JSON while retaining all still-referenced old keys;
3. update the shared keyring group so Admin, Commerce and messaging worker have the same complete keyring;
4. after the new key is present, update COMMERCE_CONNECTION_ACTIVE_KEY_ID for Admin and Commerce;
5. new/replaced credentials are encrypted with the new active key;
6. existing rows encrypted under old key IDs remain decryptable while those old keys are retained;
7. do not remove an old key until no durable credential row references that key ID;
8. re-encryption of existing rows is a separate controlled operation and is not implemented by this task.
```

Never place real keys or example plaintext API credentials in the runbook.

### R13 — update Preview smoke wording to the accepted ARCH-024 conversation contract

`docs/commerce-deployment.md` currently describes the Preview conversation body as a `FIXTURE`-mode conversation.

Because C001/C004/C005/C007 are prerequisites, update the active smoke-runbook wording so:

```text
STUDIO_PREVIEW_CONVERSATION_BODY
```

means a bounded valid current **Feature-composed Test Conversation** start body, not the removed human Fixture/Release/Draft composition.

Do not invent a request body in the Gateway repository. Continue requiring it to be captured/supplied from the deployed accepted Commerce contract.

Existing Tool Authoring preview/tool-test smoke routes may remain where still supported by accepted C001/C007; do not delete unrelated route checks merely because the human Test Conversation UI was simplified.

### R14 — do not change public/private service topology

ARCH-024 does not require a new service or new route.

Preserve:

```text
public HAProxy gateway
private moda-interact-commerce service
private moda-interact-admin service
existing Background workers
private MCP boundary
existing public Studio route allowlist
```

Do not expose Admin, Commerce health routes, database-backed credential APIs or OpenRouter secrets through new public routes.

### R15 — deployment order is configuration-last

Document, but do not execute, this deployment order:

```text
1. ARCH-024 database migration deployed.
2. ARCH-024 Shared package published and consumers built against the accepted version.
3. ARCH-024 Admin implementation deployed.
4. ARCH-024 Commerce implementation deployed.
5. ARCH-024 Background implementation deployed.
6. ARCH-024 Gateway Blueprint/configuration change applied.
7. Populate/verify the shared keyring and active-key inputs in Render.
8. Use Admin to SET the environment OpenRouter credential if not already configured.
9. Verify Admin status, Commerce readiness/Test Conversation, then production Background model execution.
10. Only after successful validation remove any out-of-band legacy Preview provider/model/key values left in the Render dashboard.
```

The Gateway task itself stops before step 6 live deployment.

Do not configure the OpenRouter credential before the relevant Admin/database implementation exists.

### R16 — failure isolation

Missing or malformed keyring configuration must fail only the operations that need the keyring:

```text
Admin SET/REPLACE OpenRouter credential -> unavailable
Commerce model/credential decrypt        -> unavailable
Background model/credential decrypt      -> unavailable
```

It must not make unrelated Shopify webhook processing, billing, messaging ingress, translation or transcription fail solely because ARCH-024 OpenRouter model execution is unavailable.

Gateway validation must ensure no keyring variable is made a generic requirement of runtimes that do not need it.

## Work Items

- [x] Re-read accepted ARCH-020-GATEWAY-003, ARCH-024-ADMIN-003, ARCH-024-COMMERCE-007 and ARCH-024-BACKGROUND-001 before editing Blueprint configuration.
- [x] Add exactly one Commerce credential-keyring env group to `render.test.yaml`.
- [x] Add exactly one Commerce credential-keyring env group to `render.production.yaml`.
- [x] Add exactly one Commerce credential-writer-config env group to each Blueprint.
- [x] Attach keyring group exactly to Admin, Commerce and messaging worker in each environment.
- [x] Attach writer-config group exactly to Admin and Commerce in each environment.
- [x] Preserve Commerce-only command-HMAC secret wiring from accepted ARCH-020-GATEWAY-003.
- [x] Remove `COMMERCE_PREVIEW_PROVIDER` from both active Blueprints/configuration.
- [x] Remove `COMMERCE_PREVIEW_MODEL` from both active Blueprints/configuration.
- [x] Remove `COMMERCE_PREVIEW_API_KEY` from both active Blueprints/configuration.
- [x] Preserve `COMMERCE_PREVIEW_ENABLED=true` in test.
- [x] Preserve `COMMERCE_PREVIEW_ENABLED=false` in production.
- [x] Preserve existing Groq/OpenAI transcription configuration required by the messaging worker.
- [x] Update positive Blueprint validator for exact new groups, attachments and forbidden legacy/static model variables.
- [x] Add all required negative validator cases R11.
- [x] Update Commerce deployment runbook with ARCH-024 model/config/credential/keyring ownership.
- [x] Document ordinary OpenRouter credential rotation as database-only/no-restart.
- [x] Document bounded encryption-keyring rotation and retained-old-key rule.
- [x] Update Test Conversation smoke wording to the current Feature-composed contract without inventing a payload.
- [x] Run focused Blueprint validation.
- [x] Run repository validation commands required below; the Docker integration harness was attempted and its unavailable prerequisite is recorded below.
- [x] Record exact files changed, commands, results and any warnings in the Completion Report.

## Interfaces / Contracts

### Deployment input contract

The final ARCH-024 infrastructure inputs relevant to this task are exactly:

```text
COMMERCE_PREVIEW_ENABLED
COMMERCE_CONNECTION_KEYS_JSON
COMMERCE_CONNECTION_ACTIVE_KEY_ID
COMMERCE_CONNECTION_COMMAND_HMAC_KEY
```

with the ownership matrix in Scope.

No OpenRouter API credential is a Render input.

### Keyring JSON contract

This task does not redefine the accepted application parser. The Render value MUST conform to the contract established by accepted ARCH-020/024 application tasks:

```json
{
  "<keyId>": "<base64 encoding of exactly 32 bytes>"
}
```

Properties:

```text
object only
at least one retained decrypt key when credential operations are enabled
key IDs nonblank and unique by JSON object semantics
values base64-decode to exactly 32 bytes
active key ID must name one key in the object for writer runtimes
```

Do not commit an example with usable key material.

### OpenRouter credential boundary

The OpenRouter API credential is **not** part of the Blueprint contract.

It is stored by ARCH-024-DATABASE-001 as encrypted durable state and mutated by ARCH-024-ADMIN-003.

Consumers decrypt it using the shared keyring at runtime.

### Environment identity

Continue using the existing common-group:

```text
DEPLOYMENT_ENVIRONMENT_NAME=test
DEPLOYMENT_ENVIRONMENT_NAME=production
```

Do not introduce another environment selector for ARCH-024.

Application repositories own normalization from deployment environment name to `CommerceEnvironment`.

## Dependencies

- `ARCH-020-GATEWAY-003`
- `ARCH-024-ADMIN-003`
- `ARCH-024-COMMERCE-007`
- `ARCH-024-BACKGROUND-001`

## Enables

None in this architecture session. Terminal ARCH-024 integrated system-test task materialisation is deliberately deferred to a later architecture session.

## Acceptance Criteria

- [x] Both Blueprints contain exactly one environment-specific `commerce-credential-keyring` group containing only `COMMERCE_CONNECTION_KEYS_JSON` with `sync: false` and no committed value.
- [x] Both Blueprints contain exactly one environment-specific `commerce-credential-writer-config` group containing only `COMMERCE_CONNECTION_ACTIVE_KEY_ID` with `sync: false` and no committed value.
- [x] Admin, Commerce and messaging worker receive the same keyring group for their environment; no other runtime receives it.
- [x] Admin and Commerce receive the writer-config group; messaging worker and all other runtimes do not.
- [x] `COMMERCE_CONNECTION_COMMAND_HMAC_KEY` remains Commerce-only.
- [x] `COMMERCE_PREVIEW_PROVIDER`, `COMMERCE_PREVIEW_MODEL` and `COMMERCE_PREVIEW_API_KEY` are absent from active Gateway Blueprints, validation contracts and operator runbook; occurrences are confined to validator deny-lists and negative fixtures.
- [x] No `OPENROUTER_API_KEY`, `COMMERCE_OPENROUTER_API_KEY`, renamed static model API key or `GROQ_COMMERCE_MODEL` is introduced as active configuration.
- [x] `COMMERCE_PREVIEW_ENABLED` remains `true` in test and `false` in production.
- [x] Existing transcription configuration/credentials required by the messaging worker remain intact.
- [x] Positive Blueprint validation enforces the exact variable/group ownership matrix.
- [x] Negative validation independently rejects every R11 architecture failure.
- [x] Operator documentation distinguishes database OpenRouter-credential rotation from encryption-keyring rotation.
- [x] Operator documentation states that ordinary OpenRouter credential replacement requires no Render config change or Commerce/Background restart.
- [x] Operator documentation does not contain plaintext credentials or encryption keys.
- [x] No public/private route, service type, database, Redis resource, service count or worker topology is changed by ARCH-024.
- [x] No live Render deployment is claimed or performed by this task.

## Validation

Before the first repository validation command, inspect the Gateway repository's existing scripts. Do not invent npm validation commands for a repository that does not expose them.

Required focused validation:

```bash
cd "$MODA_WORKSPACE_ROOT/moda-interact-gateway"

bash tests/validate-render-blueprints.sh
bash tests/validate-render-blueprints-negative.sh

git diff --check
```

Also run the repository's existing broader Gateway test harness if it remains applicable to the changed Blueprint/route boundary:

```bash
bash tests/run-tests.sh
```

If `tests/run-tests.sh` requires unavailable local services or developer-owned prerequisites, do not fake success. Record the exact blocker and run every self-contained validation it documents that is available in the prepared task environment.

### Static secret/config search

Run a bounded search across active Gateway runtime/config/docs files and record the result:

```bash
grep -RIn \
  --exclude-dir=.git \
  -E 'COMMERCE_PREVIEW_PROVIDER|COMMERCE_PREVIEW_MODEL|COMMERCE_PREVIEW_API_KEY|OPENROUTER_API_KEY|COMMERCE_OPENROUTER_API_KEY|GROQ_COMMERCE_MODEL' \
  render.test.yaml \
  render.production.yaml \
  tests \
  docs \
  README.md || true
```

Any remaining match in **active** Blueprint/validator/runbook content must be explained and corrected unless it is explicitly historical documentation that the task is not authorized to rewrite. The Completion Report must distinguish active from historical matches.

### Keyring ownership search

Record a bounded search proving intended references:

```bash
grep -RIn \
  --exclude-dir=.git \
  -E 'COMMERCE_CONNECTION_KEYS_JSON|COMMERCE_CONNECTION_ACTIVE_KEY_ID|COMMERCE_CONNECTION_COMMAND_HMAC_KEY' \
  render.test.yaml \
  render.production.yaml \
  tests/validate-render-blueprints.sh \
  tests/validate-render-blueprints-negative.sh \
  docs/commerce-deployment.md
```

The result must agree with the ownership matrix; textual runbook/test references are expected, runtime injection is restricted as specified.

### No secret-value validation

The implementing agent MUST inspect the changed diff and prove no actual value was committed for:

```text
COMMERCE_CONNECTION_KEYS_JSON
COMMERCE_CONNECTION_ACTIVE_KEY_ID
COMMERCE_CONNECTION_COMMAND_HMAC_KEY
```

Blueprint values for those inputs must use `sync: false` through the exact groups/service boundary defined above.

## Stop Condition

After all defined Work Items, Acceptance Criteria and required Validation are complete:

1. update the Completion Report;
2. set task status to `review`;
3. clear no architect-owned fields;
4. push the implementation task branch and parent report task branch through the normal mirrored workflow;
5. return control to `moda_architect`;
6. STOP.

Do not:

- deploy/sync the Blueprint to Render;
- populate real Render secret values;
- create an OpenRouter credential row;
- invent or start terminal ARCH-024 system-test tasks;
- merge implementation branches;
- push main;
- modify another repository to work around missing application capability.

## Implementation Notes

### Exact target summary

After this task the deployment model is:

```text
                         Render environment
                                │
              ┌─────────────────┴─────────────────┐
              │                                   │
 commerce-credential-keyring            commerce-credential-writer-config
 COMMERCE_CONNECTION_KEYS_JSON           COMMERCE_CONNECTION_ACTIVE_KEY_ID
              │                                   │
        ┌─────┼──────────┐                    ┌───┴────┐
        │     │          │                    │        │
      Admin Commerce  Messaging             Admin   Commerce
                     worker
```

Commerce separately retains:

```text
COMMERCE_CONNECTION_COMMAND_HMAC_KEY
```

and the Commerce config group separately retains:

```text
COMMERCE_PREVIEW_ENABLED
```

There is no static OpenRouter/model/provider API credential in Render.

### Why the messaging worker receives only the keyring

The worker decrypts an already-stored OpenRouter credential. It does not create encrypted credentials and therefore must not receive:

```text
COMMERCE_CONNECTION_ACTIVE_KEY_ID
COMMERCE_CONNECTION_COMMAND_HMAC_KEY
```

This is intentional least privilege.

### Why Admin receives the active key ID

Admin SET/REPLACE is a credential-writing operation. It must encrypt new ciphertext under the current active key and persist that key ID alongside the envelope.

### Why Commerce receives both groups

Commerce decrypts the OpenRouter credential for Test Conversations and also retains the accepted External Connection credential administration/runtime from ARCH-020, which needs the active key for credential writes.

### ARCH-020 interaction

ARCH-020-GATEWAY-003 is a hard prerequisite because it establishes the original architecture-approved Commerce credential keyring/HMAC runtime.

ARCH-024 intentionally broadens only the **keyring** and **active-key writer** deployment scope required by accepted Admin/Background capabilities. It does not change External Connection business semantics.

If accepted ARCH-020-GATEWAY-003 implemented materially different variable names or cryptographic ownership than the architecture referenced by ARCH-024 application tasks, return the conflict to the architect before editing.

### Pre-production rollout

ARCH-024 remains pre-production/breaking for this model-runtime change. There is no requirement to preserve obsolete Preview provider/model/API-key deployment settings.

Do preserve unrelated durable infrastructure and secrets. Pre-production status is not permission to destroy PostgreSQL, Redis or unrelated provider configuration.

## Completion Report

### Status

Ready for Review.

### Files Changed

- Implementation repository (`moda-interact-gateway/`):
  - `render.test.yaml`
  - `render.production.yaml`
  - `tests/validate-render-blueprints.sh`
  - `tests/validate-render-blueprints-negative.sh`
  - `docs/commerce-deployment.md`
- Parent workspace: this task definition/report only.

### Work Completed

Added exactly one environment-specific `commerce-credential-keyring` group and one `commerce-credential-writer-config` group to each Blueprint. Admin and Commerce receive both; the messaging worker receives only the keyring; no other runtime receives either. `COMMERCE_CONNECTION_COMMAND_HMAC_KEY` remains a Commerce-only service-level `sync: false` input. No key material or active key ID value is committed.

Removed static Preview provider/model/API-key declarations. The Commerce config groups now contain only their existing `ADMIN_ORIGIN` plus `COMMERCE_PREVIEW_ENABLED` (`true` in test, `false` in production). Existing `GROQ_API_KEY`, transcription provider/model configuration, and `WHATSAPP_OPENAI_API_KEY` wiring remain unchanged.

Updated the positive validator to enforce exact groups, values, attachments and uniqueness; Commerce-only HMAC; Preview switch cardinality/value; transcription retention; and rejection of the legacy/static model variable set. Added all 19 required ARCH-024 negative mutations. Updated the deployment runbook with the model/config/credential ownership boundary, no-restart database credential rotation, retained-key keyring rotation, failure isolation, configuration-last rollout, and current Feature-composed Test Conversation smoke wording. No service, route, service type, count, database, Redis resource, or worker topology was changed. No live Render deployment or credential operation was performed.

### Validation Results

Passed:

- `bash tests/validate-render-blueprints.sh` — PASS for both test and production Blueprints; YAML parsed and the exact ownership/Preview/transcription contracts validated.
- `bash tests/validate-render-blueprints-negative.sh` — PASS; all 92 existing and new negative mutations were rejected for their expected reasons, including the 19 required ARCH-024 cases.
- `bash -n tests/validate-render-blueprints.sh tests/validate-render-blueprints-negative.sh tests/run-tests.sh` — PASS.
- Bounded forbidden-variable search across both Blueprints, tests, docs and README — no active configuration or operator-runbook matches. Matches are intentional validator deny-list entries and negative fixtures proving rejection.
- Bounded ownership search — Blueprint declarations are exactly the two shared-group keys per environment and Commerce-only HMAC; validator and runbook references match that ownership contract.
- Changed diff inspection — both shared values use `sync: false` without `value`; Commerce HMAC uses service-level `sync: false`; no secret values are present.
- `git diff --check` — PASS.

Blocked by local tooling:

- `bash tests/run-tests.sh` — NOT COMPLETED. It exited before image/container creation at line 196 with `docker: command not found`; no containers were started. The developer must rerun this exact command in a Docker-capable environment. Expected result: the local gateway/upstream integration suite completes with all tests passing.

Gateway repository has no `package.json`; no npm validation command is declared. `rg` is unavailable in this shell, so the required bounded searches used `grep`. No live Render validation was run or claimed.

### Deviations

The requested broader Docker integration harness could not run because Docker is not installed/available in this execution environment. Fast self-contained Blueprint/shell checks all passed; the broader result remains unverified pending developer execution.

### Assumptions

Accepted dependencies were Complete before execution and their reports agree with this task's contracts: ARCH-020-GATEWAY-003 preserves the three existing key/HMAC names and Commerce-only HMAC; ARCH-024-ADMIN-003 consumes the shared keyring plus active key ID; ARCH-024-COMMERCE-007 and ARCH-024-BACKGROUND-001 decrypt using the shared keyring and do not require the active selector. Admin, Commerce, and Background report the accepted Shared package `@modainteract/moda-interact-shared@1.1.0`. Reviewed implementation evidence includes Admin `b0a894d65878b81bf533212fab98a48296b34fcf`, Commerce `c3a7fe7ff4414fa8c731361dbc171f52f39bb59d`, Background `9304da2599800c63b2b649dd7a414286859faeac`, and accepted Gateway prerequisite head `1102490fec44be11920f563552ceb26ec4d85f3d`.

### Unresolved Issues

The task-explicit repository integration suite remains pending developer execution in an environment with Docker.

### Architectural Concerns

None. Accepted dependency contracts and implemented ownership agree.

### Git / VCS

Prepared execution evidence:

- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-024-GATEWAY-001`, branch `task/ARCH-024-GATEWAY-001`.
- Gateway implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-024-GATEWAY-001`, branch `task/ARCH-024-GATEWAY-001`.
- Launcher synchronization: both worktrees were newly created; task-branch fast-forward was not needed; `origin/main` was already current; recursive submodule operations passed with no submodules.
- Dependency gate passed for ARCH-020-GATEWAY-003, ARCH-024-ADMIN-003, ARCH-024-COMMERCE-007 and ARCH-024-BACKGROUND-001.
- Durable parent claim commit: `215f3867e566907df8218deb84abbdaf0e85e59b`.
- Implementation start commit before edits: `c321ded98cc06244e6abc06fe3ede2f7316ca088`.
- Implementation commit: `6b574199dc76589e12dc6ca37e15f8ad658ce905`; published explicitly to `origin/task/ARCH-024-GATEWAY-001` (the new remote task ref).
- The local implementation branch's configured upstream pointed at `origin/main`; it was not used for publication. The task branch was pushed using an explicit task-ref destination. No push to `main` occurred.
- Parent Completion Report commit, final push results, clean status and remote-head equality are recorded in the final handoff after publication.

No unrelated task file, architecture/index file, implementation gitlink, or `main` branch was modified.

## Architect Review

### Review Status

Pending

### Review Notes

Definition only; implementation has not been reviewed.

### Reviewed Files

Not applicable.

### Validation Reviewed

Not applicable.

### Architecture Conformance

Awaiting implementation.

### Follow-up

After acceptance, return control to `moda_architect`. Terminal integrated system-test task materialisation is deliberately deferred to a later architecture session; do not invent or launch one from this task.
