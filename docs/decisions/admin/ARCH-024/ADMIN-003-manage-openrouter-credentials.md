---
id: ARCH-024-ADMIN-003
architecture_id: ARCH-024
title: Manage OpenRouter credentials
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 32
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-024-DATABASE-001
  - ARCH-024-SHARED-002
  - ARCH-024-ADMIN-002
enables:
  - ARCH-024-GATEWAY-001
created: 2026-10-01
updated: 2026-10-01
---

# Manage OpenRouter credentials

## Architecture

Architecture ID:

`ARCH-024`

Architecture document:

`docs/architecture/ARCH-024-commerce-agent-model-runtime-and-test-conversations.md`

Coordinator:

`moda_architect`

## Objective

Add the Admin-only control-plane surface for setting, replacing, inspecting status of, and removing the **single encrypted OpenRouter credential for the current deployed Commerce environment**.

The completed behaviour must be exactly:

```text
Admin deployment resolves one current CommerceEnvironment
        |
        v
CommerceOpenRouterCredential(environment)
        |
        +-- row absent  -> Not configured
        |
        +-- row present -> Configured

SUPER_ADMIN may:
    SET       when no row exists
    REPLACE   when a row exists and editVersion matches
    REMOVE    when a row exists and editVersion matches

Platform ADMIN may:
    read status only

No caller may:
    read the stored plaintext
    read ciphertext/nonce/authTag/keyId through the browser
    choose a different environment from the UI
```

Credential mutation must use the Shared-owned `createCommerceOpenRouterCredentialAad(...)` cross-repository contract published by `ARCH-024-SHARED-002`, so credentials written by Admin can be decrypted independently by Commerce and Background without any application-to-application implementation dependency.

Credential replacement must take effect for the next Commerce model invocation without an Admin or Commerce process restart. This task owns only Admin mutation/status behaviour; runtime use is owned by `ARCH-024-COMMERCE-007` and production Background integration.

## Context

`ARCH-024-DATABASE-001` defines:

```prisma
model CommerceOpenRouterCredential {
  id               String              @id @default(cuid()) @db.Text
  environment      CommerceEnvironment @unique
  ciphertext       Bytes
  nonce            Bytes
  authTag           Bytes
  keyId             String              @db.VarChar(64)
  editVersion       Int                 @default(1)
  updatedByAdminId String              @db.Text
  createdAt         DateTime            @default(now()) @db.Timestamptz(3)
  updatedAt         DateTime            @default(now()) @updatedAt @db.Timestamptz(3)

  updatedBy PlatformAdmin @relation(
    "CommerceOpenRouterCredentialUpdater",
    fields: [updatedByAdminId],
    references: [id],
    onDelete: Restrict,
    onUpdate: Restrict
  )

  @@schema("commerce")
}
```

with exactly one credential row per `CommerceEnvironment` and database checks requiring:

```text
nonce        = 12 bytes
authTag      = 16 bytes
ciphertext   = 1..8192 bytes
keyId        = nonblank
editVersion  > 0
```

Absence of a row means OpenRouter is not configured for that environment.

The database audit contract adds exactly:

```text
SET_OPENROUTER_CREDENTIAL
REPLACE_OPENROUTER_CREDENTIAL
REMOVE_OPENROUTER_CREDENTIAL
```

and these actions target `CommerceAuditEvent.environment`. There is deliberately no credential FK on the audit row because REMOVE deletes the credential row.

The exact cross-repository sealed-secret envelope is defined by the parent architecture and its AAD bytes are constructed by the published Shared `createCommerceOpenRouterCredentialAad(...)` helper:

```text
cipher: AES-256-GCM
key:    keyring[keyId], exactly 32 bytes
nonce:  exactly 12 random bytes
authTag: exactly 16 bytes
AAD: canonical UTF-8 JSON of:

{
  credentialType: "OPENROUTER",
  environment: <CommerceEnvironment>,
  keyId: <stored keyId>
}
```

Admin MUST obtain that canonical JSON string by calling the published Shared `createCommerceOpenRouterCredentialAad(...)` helper, not by rebuilding the object locally with `JSON.stringify(...)` or another canonicalizer.

The existing external-connection credential runtime already establishes the architecture-approved keyring environment names:

```text
COMMERCE_CONNECTION_KEYS_JSON
COMMERCE_CONNECTION_ACTIVE_KEY_ID
```

ARCH-024 intentionally reuses that encryption root rather than introducing another OpenRouter-specific keyring.

Admin needs the keyring only for SET/REPLACE encryption. Status reads and REMOVE do not decrypt the secret.

## Scope

Primary implementation targets:

```text
moda-interact-admin/src/app/(protected)/commerce-models/credentials/page.tsx
moda-interact-admin/src/app/actions/openrouter-credential.ts
moda-interact-admin/src/lib/admin/openrouter-credential.ts
moda-interact-admin/src/lib/admin/openrouter-credential-validation.ts
moda-interact-admin/src/lib/admin/openrouter-credential-environment.ts
moda-interact-admin/src/lib/admin/openrouter-credential-keyring.ts
moda-interact-admin/src/lib/admin/openrouter-credential-crypto.ts
moda-interact-admin/src/components/admin/openrouter-credential/openrouter-credential-panel.tsx
moda-interact-admin/src/components/admin/openrouter-credential/openrouter-credential-form.tsx
moda-interact-admin/src/components/admin/openrouter-credential/openrouter-credential-submit-button.tsx
moda-interact-admin/src/components/admin/sidebar.tsx
moda-interact-admin/src/components/admin/admin-shell.tsx

moda-interact-admin/tests/unit/openrouter-credential-validation.test.ts
moda-interact-admin/tests/unit/openrouter-credential-environment.test.ts
moda-interact-admin/tests/unit/openrouter-credential-keyring.test.ts
moda-interact-admin/tests/unit/openrouter-credential-crypto.test.ts
moda-interact-admin/tests/unit/openrouter-credential-service.test.ts
moda-interact-admin/tests/security/admin-openrouter-credential.test.mjs
moda-interact-admin/tests/security/admin-sidebar-navigation.test.mjs
```

The nested Admin `database/` submodule/gitlink may move only to the architect-accepted `ARCH-024-DATABASE-001` database commit required by this task.

`package.json` / `package-lock.json` may change only if mechanically required by accepted Shared package consumption. No new cryptography dependency is authorized: use Node `node:crypto`.

Additional Admin files may be changed only when required to integrate this exact Credential surface or keep focused validation/build green. Every additional file MUST be named and justified in the Completion Report.

Do not modify the database schema/migration inside this task.

## Out of Scope

- Model Availability administration; `ARCH-024-ADMIN-001` owns it.
- Model Catalogue entry administration; `ARCH-024-ADMIN-002` owns it.
- Agent model selection.
- Commerce Studio changes.
- Test Conversation model invocation; `ARCH-024-COMMERCE-007` owns it.
- Background model invocation.
- Gateway/Render environment wiring. A later `moda_gateway` task owns deployment of the keyring variables to the required services.
- Adding `OPENROUTER_API_KEY`, `COMMERCE_OPENROUTER_API_KEY`, or another plaintext provider credential environment variable.
- Adding a second encryption keyring.
- Adding a credential FK to `CommerceModelCatalogueEntry`.
- Adding a credential FK to `CommerceAuditEvent`.
- Storing an OpenRouter credential per model or per Shop.
- Reading or displaying an existing OpenRouter credential.
- Showing ciphertext, nonce, authTag or keyId in browser payloads.
- Adding a "reveal", "copy", "download" or "test credential" operation.
- Calling OpenRouter from Admin.
- Validating that a credential is accepted by OpenRouter over the network.
- Rotating the encryption keyring itself.
- Re-encrypting all stored credentials after a keyring change.
- Allowing one Admin deployment to mutate another environment's credential.
- Merchant-facing credential administration.
- Logging secrets or secret-derived fingerprints.

## Requirements

### R1 — Consume accepted Database, Shared and Admin dependencies first

Before implementation:

1. synchronize the nested `database/` submodule to the architect-accepted `ARCH-024-DATABASE-001` implementation;
2. retain the exact `@modainteract/moda-interact-shared` version already adopted through `ARCH-024-SHARED-002` / `ARCH-024-ADMIN-002`;
3. confirm `ARCH-024-ADMIN-002` is architect-accepted Complete and retain the existing Availability + Catalogue routes/navigation;
4. regenerate Prisma:

```bash
npm run prisma:generate
```

5. validate Prisma:

```bash
npm run prisma:validate
```

Admin MUST import and use published Shared `createCommerceOpenRouterCredentialAad(...)` for credential AAD construction. Do not rebuild the payload with `canonicalJson(...)`, `JSON.stringify(...)` or another local helper.

### R2 — Manage only the current deployed environment

Create one exact server-only resolver in:

```text
src/lib/admin/openrouter-credential-environment.ts
```

with an exported contract equivalent to:

```ts
export function resolveCommerceEnvironment(): CommerceEnvironment;
```

Resolution order is exactly:

1. `DEPLOYMENT_ENVIRONMENT_NAME` when nonblank;
2. otherwise `NODE_ENV` when nonblank;
3. otherwise fail closed.

Normalize to lowercase and map only:

```text
local       -> LOCAL
test        -> TEST
development -> DEVELOPMENT
staging     -> STAGING
production  -> PRODUCTION
```

Any other value, including `unknown`, MUST fail with a bounded configuration error.

The `/commerce-models/credentials` page MUST NOT contain an environment selector.

Every status query and mutation MUST call `resolveCommerceEnvironment()` server-side and target only that returned environment.

This prevents a Development Admin deployment/keyring from writing a Production credential row.

### R3 — Parse the existing Commerce credential keyring exactly

Create:

```text
src/lib/admin/openrouter-credential-keyring.ts
```

with a server-only contract equivalent to:

```ts
export type CredentialKeyring = Readonly<Record<string, Uint8Array>>;

export type ActiveCredentialKeyring = {
  keyring: CredentialKeyring;
  activeKeyId: string;
};

export function loadActiveCredentialKeyring(): ActiveCredentialKeyring;
```

`loadActiveCredentialKeyring()` MUST:

1. read `COMMERCE_CONNECTION_KEYS_JSON`;
2. require it to parse as a JSON object whose keys are nonblank key IDs and whose values are base64 strings;
3. decode every value using base64;
4. require every decoded key to contain exactly 32 bytes;
5. read `COMMERCE_CONNECTION_ACTIVE_KEY_ID`;
6. require the active key ID to be nonblank and present in the parsed keyring;
7. return only the parsed keyring and active key ID;
8. fail with one bounded `OpenRouter credential encryption is unavailable.` error when any requirement fails.

MUST NOT log:

```text
raw JSON
base64 values
decoded key bytes
active key contents
```

Do not read or require `COMMERCE_CONNECTION_COMMAND_HMAC_KEY`; it is unrelated to OpenRouter credential encryption.

### R4 — Seal OpenRouter credentials with one exact AES-256-GCM contract

Create:

```text
src/lib/admin/openrouter-credential-crypto.ts
```

using only:

```ts
import { createCipheriv, randomBytes } from 'node:crypto';
```

Expose one server-only function equivalent to:

```ts
export type SealedOpenRouterCredential = {
  ciphertext: Uint8Array;
  nonce: Uint8Array;
  authTag: Uint8Array;
  keyId: string;
};

export function sealOpenRouterCredential(input: {
  environment: CommerceEnvironment;
  secret: string;
  keyring: Readonly<Record<string, Uint8Array>>;
  activeKeyId: string;
}): SealedOpenRouterCredential;
```

The function MUST perform these operations in this exact order:

1. validate `secret` using R5 before any encryption;
2. require `keyring[activeKeyId]` to exist and be exactly 32 bytes;
3. generate exactly 12 random nonce bytes with `randomBytes(12)`;
4. build the AAD string with the published Shared contract exactly:

```ts
createCommerceOpenRouterCredentialAad({
  environment: input.environment,
  keyId: input.activeKeyId,
})
```

5. encode that returned canonical string as UTF-8 bytes;
6. call `createCipheriv('aes-256-gcm', key, nonce)`;
7. call `cipher.setAAD(aadBytes)` before encryption;
8. encrypt the exact UTF-8 secret bytes without trimming or normalizing them;
9. concatenate all `cipher.update(...)` and `cipher.final()` output into `ciphertext`;
10. call `cipher.getAuthTag()` and require exactly 16 bytes;
11. return `{ ciphertext, nonce, authTag, keyId: activeKeyId }`.

Do not prepend the nonce/authTag/keyId to ciphertext. They are separate database columns.

Do not hash the credential or store a fingerprint.

### R5 — Validate secret input exactly

Create a canonical server-side input validator in:

```text
src/lib/admin/openrouter-credential-validation.ts
```

A credential secret is valid only when:

```text
UTF-8 byte length >= 1
UTF-8 byte length <= 8192
contains no \r
contains no \n
contains no NUL (\0)
```

Do not trim or otherwise alter a valid secret before encryption.

Reject empty, oversized or forbidden-control-character input using the exact client-safe message:

```text
OpenRouter credential is invalid.
```

The validator MUST NOT include any part of the rejected secret in an error message.

Mutation `reason` MUST:

```text
trim to 1..1000 characters
```

`operationId` MUST:

```text
trim to 1..128 characters
```

`expectedEditVersion` when present MUST be a positive integer.

### R6 — Expose one secret-free status contract

Create the Admin read service in:

```text
src/lib/admin/openrouter-credential.ts
```

with a returned status equivalent to:

```ts
export type OpenRouterCredentialStatus = {
  environment: CommerceEnvironment;
  configured: boolean;
  editVersion: number | null;
  updatedAt: string | null;
  updatedByAdminId: string | null;
};
```

The read path MUST:

1. require `requirePlatformAdminRead()`;
2. resolve the current environment using R2;
3. query by `CommerceOpenRouterCredential.environment` only;
4. return `configured: false` with null version/update fields when no row exists;
5. return `configured: true` plus only `editVersion`, `updatedAt`, and `updatedByAdminId` when a row exists.

The status object MUST NOT contain:

```text
id
ciphertext
nonce
authTag
keyId
secret
credential length
credential prefix/suffix
fingerprint/hash
```

No read path may decrypt the credential.

### R7 — Implement SET as insert-only and atomic with audit

Expose a server mutation equivalent to:

```ts
setOpenRouterCredential(input: {
  operationId: string;
  reason: string;
  secret: string;
}): Promise<OpenRouterCredentialStatus>;
```

The server action MUST independently call `requirePlatformAdminMutation()` and require:

```text
principal.role === SUPER_ADMIN
```

Do not trust UI hiding.

SET MUST:

1. resolve the current environment;
2. validate operationId/reason/secret;
3. load the active keyring;
4. seal the secret using R4;
5. open one Prisma transaction;
6. require that no `CommerceOpenRouterCredential` row exists for the environment;
7. INSERT exactly one row with:

```text
environment      = current environment
ciphertext       = sealed ciphertext
nonce            = sealed nonce
authTag          = sealed authTag
keyId            = sealed keyId
editVersion      = 1
updatedByAdminId = principal.id
```

8. INSERT one `CommerceAuditEvent` in the same transaction:

```text
actorType    = PLATFORM_ADMIN
actorAdminId = principal.id
operationId  = validated operationId
action       = SET_OPENROUTER_CREDENTIAL
environment  = current environment
reason       = validated reason
metadata     = { "editVersion": 1 }
```

9. commit both or neither;
10. return a fresh secret-free R6 status.

If a row already exists, return the exact client-safe conflict message:

```text
OpenRouter credential is already configured. Use Replace.
```

A database uniqueness race must map to the same conflict message.

Audit metadata MUST NOT contain keyId, ciphertext, nonce, authTag, secret, length or fingerprints.

### R8 — Implement REPLACE as CAS update and atomic audit

Expose:

```ts
replaceOpenRouterCredential(input: {
  operationId: string;
  reason: string;
  expectedEditVersion: number;
  secret: string;
}): Promise<OpenRouterCredentialStatus>;
```

REPLACE MUST:

1. independently require SUPER_ADMIN mutation authorization;
2. resolve current environment;
3. validate all input;
4. load active keyring and seal the replacement secret;
5. open one Prisma transaction;
6. require a credential row to exist;
7. require its current `editVersion` to equal `expectedEditVersion`;
8. update only the row matching:

```text
environment = current environment
editVersion = expectedEditVersion
```

9. replace `ciphertext`, `nonce`, `authTag`, `keyId`;
10. set `updatedByAdminId = principal.id`;
11. increment `editVersion` by exactly 1;
12. insert one audit event in the same transaction:

```text
action      = REPLACE_OPENROUTER_CREDENTIAL
environment = current environment
metadata    = {
  "previousEditVersion": expectedEditVersion,
  "editVersion": expectedEditVersion + 1
}
```

13. commit both or neither;
14. return fresh R6 status.

When no row exists, return:

```text
OpenRouter credential is not configured. Use Set.
```

When CAS fails, return:

```text
OpenRouter credential changed. Refresh and try again.
```

Do not retry automatically with a different expected version.

### R9 — Implement REMOVE as CAS delete and atomic audit

Expose:

```ts
removeOpenRouterCredential(input: {
  operationId: string;
  reason: string;
  expectedEditVersion: number;
}): Promise<OpenRouterCredentialStatus>;
```

REMOVE MUST:

1. independently require SUPER_ADMIN mutation authorization;
2. resolve current environment;
3. validate operationId/reason/expectedEditVersion;
4. NOT require or load the encryption keyring;
5. open one Prisma transaction;
6. require the current row to exist and match `expectedEditVersion`;
7. delete only that matching credential row;
8. insert one audit event in the same transaction:

```text
action      = REMOVE_OPENROUTER_CREDENTIAL
environment = current environment
metadata    = {
  "previousEditVersion": expectedEditVersion
}
```

9. commit both or neither;
10. return `{ configured: false, ...nulls }` for the current environment.

No row -> exact client-safe message:

```text
OpenRouter credential is not configured.
```

CAS conflict -> exact client-safe message:

```text
OpenRouter credential changed. Refresh and try again.
```

Removing the OpenRouter credential MUST NOT alter Model Availability, Catalogue entries, Agent Configuration, Test Conversation state, or any other credential table.

### R10 — Add Server Actions with no secret echo

Create:

```text
src/app/actions/openrouter-credential.ts
```

with exactly these mutation actions:

```text
setOpenRouterCredentialAction
replaceOpenRouterCredentialAction
removeOpenRouterCredentialAction
```

The actions MUST:

- invoke the R7/R8/R9 server services;
- return only bounded success/error/status data;
- never return the submitted secret;
- never return encryption material;
- never serialize raw caught errors to the client;
- call `revalidatePath('/commerce-models/credentials')` after successful mutation.

A submitted secret MUST NOT appear in:

```text
Server Action return value
redirect URL
query string
form error
React state after success
console output
structured application log
audit metadata
```

### R11 — Add the protected Credentials Admin route exactly

Create:

```text
/commerce-models/credentials
```

at:

```text
src/app/(protected)/commerce-models/credentials/page.tsx
```

The page MUST use the existing protected Platform Admin page/auth shell.

The server page loads only R6 status and principal role. It MUST NOT load/decrypt the secret.

After this task, the existing `Commerce models` navigation group MUST contain exactly these implemented destinations:

```text
Commerce models
    Availability -> /commerce-models/availability
    Catalogue    -> /commerce-models/catalogue
    Credentials  -> /commerce-models/credentials
```

Add active key:

```text
openrouter-credentials
```

Do not add another model-management navigation group.

### R12 — Render one environment-specific status panel

The page MUST show:

```text
OpenRouter credential
Environment: <current environment>
Status: Configured | Not configured
```

When configured, also show:

```text
Edit version: <n>
Updated: <timestamp>
Updated by: <admin id>
```

Do not show keyId or any encryption-envelope field.

Platform `ADMIN` readers see status but no mutation form/buttons.

`SUPER_ADMIN` readers see mutation controls appropriate to the current state:

```text
Not configured:
    Set credential

Configured:
    Replace credential
    Remove credential
```

There is no Reveal button.

There is no Test credential button.

There is no environment dropdown.

### R13 — Credential form interaction is deterministic and single-flight

Create one reusable client form component for SET/REPLACE with:

```text
Credential  <input type="password">
Reason      <textarea/input>
Submit
```

Credential input requirements:

```text
type="password"
autoComplete="new-password"
spellCheck=false
no defaultValue
no server-rendered secret
```

For REPLACE, the form receives only the current `expectedEditVersion`.

REMOVE requires an explicit reason and a confirmation control/button; it does not require re-entering the existing secret.

For every SET/REPLACE/REMOVE submit:

1. create one operationId for that user activation;
2. synchronously acquire a `useRef`/imperative in-flight gate **before** starting the Server Action;
3. disable the mutation controls visibly while pending;
4. ignore same-tick click/keyboard/programmatic re-entry while the gate is held;
5. clear the credential input immediately after a successful SET/REPLACE;
6. on bounded failure, clear the submitted secret from component state before displaying the error;
7. on CAS conflict, require page/status refresh before another REPLACE/REMOVE attempt;
8. release the local gate after the handled action result.

Do not rely only on React's asynchronous `pending` render state for double-click correctness.

The database uniqueness/CAS constraints remain the durable concurrency boundary.

### R14 — Read access and mutation authorization are separate

All authenticated Platform Admins may read credential status.

Every Server Action mutation MUST independently call:

```text
requirePlatformAdminMutation()
```

and require:

```text
role === SUPER_ADMIN
```

Direct action invocation by an ordinary `ADMIN` must fail even if UI controls are hidden.

Development bypass may behave only according to the existing Admin authentication rules; do not add a credential-specific bypass.

### R15 — Fail closed when encryption configuration is unavailable

Status reads MUST continue to work when keyring environment variables are absent or invalid because they do not decrypt or encrypt.

REMOVE MUST continue to work without the keyring because deletion does not require decryption.

SET and REPLACE MUST fail closed with exactly:

```text
OpenRouter credential encryption is unavailable.
```

when the active keyring cannot be loaded.

Do not fall back to plaintext persistence.

Do not generate an ephemeral encryption key.

Do not silently choose a different key ID.

### R16 — Audit is transactional and secret-free

Every successful mutation must write exactly one corresponding `CommerceAuditEvent` inside the same database transaction as the credential mutation.

Required targets:

```text
SET_OPENROUTER_CREDENTIAL
REPLACE_OPENROUTER_CREDENTIAL
REMOVE_OPENROUTER_CREDENTIAL
    -> environment = current environment
```

Required actor:

```text
actorType    = PLATFORM_ADMIN
actorAdminId = current PlatformAdmin.id
```

Audit metadata may contain only bounded non-secret version/status information described in R7-R9.

Audit metadata MUST NOT contain:

```text
secret
ciphertext
nonce
authTag
keyId
secret length
prefix/suffix
hash/fingerprint
request headers
```

An audit insert failure MUST roll back SET/REPLACE/REMOVE.

### R17 — Do not verify the credential by calling OpenRouter

This Admin task performs no provider network call.

`Configured` means only:

```text
a structurally valid encrypted row exists for the current environment
```

It does not mean OpenRouter has accepted the credential.

Runtime/provider validation belongs to Commerce/System Test.

### R18 — Unit test the exact sealed-secret interoperability contract

`tests/unit/openrouter-credential-crypto.test.ts` MUST use deterministic test keys and assert at least:

1. SET sealing creates 12-byte nonce and 16-byte authTag;
2. ciphertext does not contain the plaintext credential as a UTF-8 substring;
3. the exact AAD bytes equal the UTF-8 encoding of published Shared `createCommerceOpenRouterCredentialAad({ environment, keyId })`;
4. a test-only `createDecipheriv('aes-256-gcm', ...)` using the **published Shared AAD contract** decrypts the sealed value to the exact original secret;
5. changing environment causes authentication failure;
6. changing keyId in AAD causes authentication failure;
7. changing authTag causes authentication failure;
8. changing ciphertext causes authentication failure;
9. the source implementation contains no secret logging/fingerprinting helper.

The test-only decrypt helper MUST remain inside the test file. Do not add an Admin production decrypt function.

### R19 — Service tests must exercise real CAS semantics

`tests/unit/openrouter-credential-service.test.ts` MUST cover at least:

```text
SET when absent -> configured v1 + SET audit
SET when present -> conflict
REPLACE v1 -> v2 + REPLACE audit
REPLACE stale v1 against v2 -> conflict; row unchanged
REMOVE v2 -> row absent + REMOVE audit
REMOVE stale -> conflict
ADMIN mutation -> rejected
SUPER_ADMIN mutation -> allowed
audit failure -> credential mutation rolls back
keyring unavailable -> SET/REPLACE fail; no row/audit written
keyring unavailable -> REMOVE still succeeds
status read -> never decrypts and returns no envelope fields
```

Where an in-memory Prisma mock cannot prove transaction/CAS behaviour faithfully, use the repository's existing test doubles only for pure branch coverage and add the PostgreSQL proof in R20.

### R20 — Disposable PostgreSQL credential lifecycle proof is mandatory

Add a task-owned validation script or test, named exactly:

```text
scripts/validate-arch024-openrouter-credential-admin.mjs
```

The proof MUST run against a disposable PostgreSQL instance/schema with the accepted ARCH-024 migration applied and perform this exact sequence:

1. create one active `PlatformAdmin` SUPER_ADMIN fixture;
2. choose one non-production test environment, `TEST`;
3. assert no credential row exists for `TEST`;
4. using a deterministic 32-byte test key and active key ID `arch024-test-key`, seal `credential-A` with the exact R4 contract;
5. INSERT credential A with editVersion 1 and matching SET audit in one transaction;
6. read the stored row and decrypt it **inside the validation script only** using the exact published Shared `createCommerceOpenRouterCredentialAad(...)` contract; assert exact plaintext `credential-A` without printing it;
7. CAS replace v1 with sealed `credential-B`, set editVersion 2, and insert matching REPLACE audit in one transaction;
8. assert stale v1 replacement affects zero rows / is rejected and does not add another successful mutation audit;
9. decrypt the current row in-process and assert exact plaintext `credential-B` without printing it;
10. CAS delete v2 and insert REMOVE audit in one transaction;
11. assert the credential row is absent;
12. assert exactly one successful SET, one REPLACE and one REMOVE audit exists for the fixture operation IDs;
13. assert no audit metadata contains credential A/B, key ID, ciphertext, nonce or auth tag;
14. clean up the disposable database/container/network owned by this validation.

Do not print plaintext credentials or encryption key material to stdout/stderr.

### R21 — Security/UI regression tests are mandatory

`tests/security/admin-openrouter-credential.test.mjs` and the focused component/service tests MUST prove at least:

1. unauthenticated access follows existing protected Admin behaviour;
2. Platform `ADMIN` can read status but has no mutation controls;
3. direct Platform `ADMIN` Server Action mutation is rejected;
4. `SUPER_ADMIN` sees SET when not configured;
5. `SUPER_ADMIN` sees REPLACE + REMOVE when configured;
6. no Reveal/Test/environment-selector control exists;
7. HTML/serialized status/action responses do not contain submitted secret, ciphertext, nonce, authTag or keyId;
8. successful SET/REPLACE clears the client secret field;
9. failed SET/REPLACE clears the client secret field before displaying bounded error;
10. same-tick repeated SET dispatches exactly one Server Action;
11. same-tick repeated REPLACE dispatches exactly one Server Action;
12. same-tick repeated REMOVE dispatches exactly one Server Action;
13. sidebar contains Availability + Catalogue + Credentials exactly once under `Commerce models`.

## Work Items

- [x] Consume accepted ARCH-024 Database/Shared/Admin prerequisites and regenerate Prisma.
- [x] Add current-environment resolver with exact deployment-name mapping.
- [x] Add exact existing-keyring parser for Admin encryption.
- [x] Add server-only AES-256-GCM OpenRouter credential sealer using Shared canonical JSON AAD.
- [x] Add bounded secret/reason/operation/CAS validation.
- [x] Add secret-free current-environment status reader.
- [x] Add atomic SET + audit transaction.
- [x] Add atomic CAS REPLACE + audit transaction.
- [x] Add atomic CAS REMOVE + audit transaction.
- [x] Add bounded Server Actions with no secret echo.
- [x] Add `/commerce-models/credentials` protected Admin route.
- [x] Extend Commerce models sidebar to Availability + Catalogue + Credentials.
- [x] Add current-environment status UI and SUPER_ADMIN-only controls.
- [x] Add synchronous single-flight mutation guards and secret clearing behaviour.
- [x] Add unit/security/UI regression coverage.
- [x] Add disposable PostgreSQL credential lifecycle/interoperability proof.
- [x] Run required validation and complete the Completion Report.

## Interfaces / Contracts

### Durable database owner

`ARCH-024-DATABASE-001`

Durable model:

```text
CommerceOpenRouterCredential
    environment UNIQUE
    ciphertext
    nonce
    authTag
    keyId
    editVersion
    updatedByAdminId
    createdAt
    updatedAt
```

### Shared-owned AAD contract

Published Shared package:

```text
@modainteract/moda-interact-shared/commerce/model
    createCommerceOpenRouterCredentialAad
```

Do not duplicate canonicalization or AAD object construction locally.

### Cross-repository sealed-secret contract

Independent writer/consumers:

```text
moda-interact-admin / ARCH-024-ADMIN-003         seal
moda-interact-commerce / ARCH-024-COMMERCE-007  decrypt
moda-interact-background / ARCH-024-BACKGROUND-001 decrypt
```

Contract:

```text
AES-256-GCM
key = keyring[keyId] exactly 32 bytes
nonce = 12 bytes
authTag = 16 bytes
AAD string = createCommerceOpenRouterCredentialAad({ environment, keyId })
AAD bytes = UTF-8 encoding of that returned canonical string
```

Any implementation conflict with the published Shared contract is architectural. Stop and return to `moda_architect`; do not invent another AAD or envelope.

### Server Action inputs

SET:

```ts
{
  operationId: string;
  reason: string;
  secret: string;
}
```

REPLACE:

```ts
{
  operationId: string;
  reason: string;
  expectedEditVersion: number;
  secret: string;
}
```

REMOVE:

```ts
{
  operationId: string;
  reason: string;
  expectedEditVersion: number;
}
```

No action accepts `environment` from the browser.

### Public status result

```ts
{
  environment: CommerceEnvironment;
  configured: boolean;
  editVersion: number | null;
  updatedAt: string | null;
  updatedByAdminId: string | null;
}
```

No secret/envelope property may be added to that result.

## Dependencies

- `ARCH-024-DATABASE-001`
- `ARCH-024-SHARED-002`
- `ARCH-024-ADMIN-002`

## Enables

- `ARCH-024-GATEWAY-001`

## Acceptance Criteria

- [x] `/commerce-models/credentials` manages only the current deployed `CommerceEnvironment`; there is no environment selector.
- [x] At most one OpenRouter credential exists for the current environment, enforced by the database uniqueness constraint.
- [x] Platform Admin readers can inspect configured/not-configured status but cannot mutate credentials.
- [x] Every SET/REPLACE/REMOVE mutation independently requires `SUPER_ADMIN`.
- [x] SET is insert-only and creates editVersion 1.
- [x] REPLACE uses exact CAS and increments editVersion by one.
- [x] REMOVE uses exact CAS and deletes the credential row.
- [x] SET/REPLACE/REMOVE audit and credential mutation are atomic.
- [x] Audit target is the current environment and contains no secret/encryption material.
- [x] Credential sealing uses AES-256-GCM, 12-byte nonce, 16-byte auth tag and the exact AAD returned by published Shared `createCommerceOpenRouterCredentialAad(...)`.
- [x] Admin production code has no decrypt/reveal path.
- [x] The stored secret is never returned to the browser after SET/REPLACE.
- [x] Keyring/environment configuration errors fail SET/REPLACE closed without plaintext fallback.
- [x] REMOVE does not require the encryption keyring.
- [x] Credential replacement does not require an Admin process restart.
- [x] The page does not call OpenRouter to verify a credential.
- [x] Same-tick repeated SET/REPLACE/REMOVE activation dispatches one action only.
- [x] The Commerce models sidebar contains Availability, Catalogue and Credentials and no duplicate/dead destinations.
- [x] No Model Availability, Catalogue Entry or Agent Configuration state is mutated by credential lifecycle operations.
- [x] Disposable PostgreSQL proof demonstrates SET -> REPLACE -> REMOVE with decryption compatibility against the exact published Shared AAD contract.

## Validation

Before Node-related commands:

```bash
command -v node >/dev/null 2>&1 || \
  source "$MODA_WORKSPACE_ROOT/scripts/bootstrap-node.sh"
```

From the dedicated `moda-interact-admin` task worktree, inspect `package.json` first, then run:

```bash
npm run prisma:generate
npm run prisma:validate
```

Focused unit tests:

```bash
node --experimental-strip-types --test \
  tests/unit/openrouter-credential-validation.test.ts \
  tests/unit/openrouter-credential-environment.test.ts \
  tests/unit/openrouter-credential-keyring.test.ts \
  tests/unit/openrouter-credential-crypto.test.ts \
  tests/unit/openrouter-credential-service.test.ts
```

Focused security/UI tests:

```bash
node --test \
  tests/security/admin-openrouter-credential.test.mjs \
  tests/security/admin-sidebar-navigation.test.mjs
```

Disposable PostgreSQL proof:

```bash
node scripts/validate-arch024-openrouter-credential-admin.mjs
```

Targeted formatting:

```bash
npx prettier --check \
  'src/app/(protected)/commerce-models/credentials/page.tsx' \
  src/app/actions/openrouter-credential.ts \
  src/lib/admin/openrouter-credential.ts \
  src/lib/admin/openrouter-credential-validation.ts \
  src/lib/admin/openrouter-credential-environment.ts \
  src/lib/admin/openrouter-credential-keyring.ts \
  src/lib/admin/openrouter-credential-crypto.ts \
  src/components/admin/openrouter-credential/openrouter-credential-panel.tsx \
  src/components/admin/openrouter-credential/openrouter-credential-form.tsx \
  src/components/admin/openrouter-credential/openrouter-credential-submit-button.tsx \
  src/components/admin/sidebar.tsx \
  src/components/admin/admin-shell.tsx \
  tests/unit/openrouter-credential-validation.test.ts \
  tests/unit/openrouter-credential-environment.test.ts \
  tests/unit/openrouter-credential-keyring.test.ts \
  tests/unit/openrouter-credential-crypto.test.ts \
  tests/unit/openrouter-credential-service.test.ts \
  tests/security/admin-openrouter-credential.test.mjs \
  tests/security/admin-sidebar-navigation.test.mjs \
  scripts/validate-arch024-openrouter-credential-admin.mjs
```

Targeted ESLint:

```bash
npx eslint \
  'src/app/(protected)/commerce-models/credentials/page.tsx' \
  src/app/actions/openrouter-credential.ts \
  src/lib/admin/openrouter-credential.ts \
  src/lib/admin/openrouter-credential-validation.ts \
  src/lib/admin/openrouter-credential-environment.ts \
  src/lib/admin/openrouter-credential-keyring.ts \
  src/lib/admin/openrouter-credential-crypto.ts \
  src/components/admin/openrouter-credential/openrouter-credential-panel.tsx \
  src/components/admin/openrouter-credential/openrouter-credential-form.tsx \
  src/components/admin/openrouter-credential/openrouter-credential-submit-button.tsx \
  src/components/admin/sidebar.tsx \
  src/components/admin/admin-shell.tsx
```

Production build (the repository has no standalone `typecheck` npm script; the production build remains the declared TypeScript/build gate):

```bash
npm run build
```

Whitespace:

```bash
git diff --check
```

The PostgreSQL validation must use task-owned disposable resources and clean them up. Do not reuse another task's container/database/network.

If validation encounters a documented baseline condition, follow `docs/development-baseline.md` according to the architect baseline policy. Do not expand this task into unrelated baseline repair.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete:

1. finish the Completion Report;
2. set task status to `review`;
3. return control to `moda_architect`;
4. STOP.

Do not begin a Gateway task, System Test, Commerce runtime task, or any other follow-on work. COMMERCE-007 is independently gated and does not depend on this task.

## Implementation Notes

- `CommerceOpenRouterCredential` is intentionally one row per environment, not one per model. Model identity/configuration and credential lifecycle remain separate.
- The Admin instance manages only its current deployed environment. This is intentional because the encryption keyring and deployment trust boundary are environment-specific.
- Reuse of `COMMERCE_CONNECTION_KEYS_JSON` / `COMMERCE_CONNECTION_ACTIVE_KEY_ID` is deliberate. ARCH-024 does not create an OpenRouter-specific encryption root.
- Admin owns encryption/mutation only. Commerce owns decryption/runtime use.
- There is deliberately no production Admin decrypt function. The only decryption in this task is test/validation code proving interoperability with the published Shared AAD contract used independently by Commerce and Background.
- A configured row indicates durable encrypted configuration only; it does not prove OpenRouter network validity.
- Do not add provider-specific credential fields to the Model Catalogue.
- Do not cache plaintext credentials in process globals, React state after completion, localStorage, cookies, URLs, telemetry, or audit metadata.

## Completion Report

### Status

Ready for Architect Review.

### Files Changed

Implementation changes in the dedicated `moda-interact-admin` task worktree:

- Added the current-environment resolver, existing keyring parser, credential validator, AES-256-GCM sealer, and secret-free transactional Admin service.
- Added the three independently authorized Server Actions, protected Credentials route, status panel, single-flight SET/REPLACE/REMOVE controls, and Credentials navigation destination.
- Added five focused unit tests, credential security regressions, and the sidebar navigation regression.
- Added `scripts/validate-arch024-openrouter-credential-admin.mjs` for the required disposable PostgreSQL lifecycle/interoperability proof.
- No database schema, migration, `package.json`, or lockfile changes.

### Work Completed

The Admin route manages only the resolved deployment environment. SET is insert-only; REPLACE and REMOVE use exact edit-version CAS; each credential change and environment-targeted audit event share one serializable transaction. SET/REPLACE use the existing connection keyring and Shared `createCommerceOpenRouterCredentialAad(...)`; REMOVE and status reads do not load or decrypt keys. All status/action return values are secret-free. The UI exposes mutations only to `SUPER_ADMIN`, clears password input after handled results, synchronously gates duplicate submissions, and requires refresh after CAS conflicts.

### Validation Results

- `npm run prisma:generate` — passed.
- `npm run prisma:validate` — passed.
- Focused unit suite — 13 passed, 0 failed.
- Focused crypto contract test after adding the explicit Shared-AAD UTF-8 source assertion — 2 passed, 0 failed.
- Focused credential security and sidebar navigation suites — 12 passed, 0 failed.
- Targeted ESLint — passed.
- Targeted Prettier check — passed.
- `npm run build` — passed, including TypeScript and `/commerce-models/credentials` route generation. Existing BullMQ dynamic-dependency and optional `@valkey/valkey-glide` warnings remain non-blocking.
- `node scripts/validate-arch024-openrouter-credential-admin.mjs` — passed against accepted migrations on task-owned disposable PostgreSQL; SET/REPLACE/stale CAS/REMOVE, Shared-AAD decrypt interoperability, secret-free audits, and audit-failure rollback verified; owned container/network cleanup passed.
- `git diff --check` — passed.

### Deviations

The credential helper/service modules do not import the `server-only` marker package because it is not present in this Admin dependency tree and the initial Node test runner could not resolve it. They are used only from the protected Server Component and Server Actions; no client component imports them. No dependency was added. Security regression checks are source-level guards rather than browser-driven interaction tests. The accepted database schema and Shared package version were retained; no provider network call was added.

### Assumptions

- `ARCH-024-DATABASE-001` supplies `CommerceOpenRouterCredential` and required credential audit actions.
- `ARCH-024-SHARED-002` supplies the accepted Shared Commerce package, including canonical JSON support.
- `ARCH-024-ADMIN-002` has already established the `Commerce models` Admin navigation group.
- A later Gateway task will wire the existing Commerce credential keyring variables to the Admin runtime; source implementation must fail closed until that configuration exists.

### Unresolved Issues

None at definition time.

### Architectural Concerns

If the accepted Database schema, published Shared `createCommerceOpenRouterCredentialAad(...)` contract, or deployed credential keyring contract differs from this task, stop and return the contradiction to `moda_architect`. Do not silently change the encryption envelope.

### Git / VCS

Launcher-prepared parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-024-ADMIN-003`.

Launcher-prepared implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-024-ADMIN-003`.

Both worktrees use `task/ARCH-024-ADMIN-003`. The parent task branch began at claim commit `a81e4b0e70f6f02ed07482c1bcb10c838d5cf154`; the Admin implementation branch began at `d431f4c8b6ba92c3f6e8b62c7787b5b4f9d12eeb`. Admin implementation commits are `bd08ee6` and `b0a894d`; both are published to `origin/task/ARCH-024-ADMIN-003`. The parent task packet is being committed to its existing `origin/task/ARCH-024-ADMIN-003` branch. The recursive `database/` submodule remains at accepted commit `cfeeb12456b4e05067a96857a8c47837d7e33bbd`; `@modainteract/moda-interact-shared` remains at `1.1.0`. The parent report commit is available in that branch's history; final clean-worktree evidence is checked after publication.

## Architect Review

### Review Status

Changes Requested

### Review Notes

Attempt 1 implementation is architecturally conformant. The current-environment resolver, accepted connection-keyring reuse, AES-256-GCM envelope, published Shared `createCommerceOpenRouterCredentialAad(...)` construction and explicit UTF-8 encoding, secret-free status contract, independent SUPER_ADMIN Server Action boundary, insert-only SET, CAS REPLACE/REMOVE, serializable credential-plus-audit transactions, secret-free UI, synchronous single-flight controls and disposable PostgreSQL lifecycle/interoperability proof all match the task and parent architecture.

The reported absence of a direct `server-only` marker package is not a source correction: no new dependency is authorised by this task, the sensitive modules have server-side runtime call sites only, the client imports the status contract as a type only, and the production build passed. The source-level security regressions are also acceptable when combined with direct inspection of the action/service/UI boundaries and the successful build.

The remaining deficiency is durable execution evidence only. The Completion Report names the prepared worktrees and implementation commits, but does not record the complete prepared-launch synchronization/recursive-submodule evidence or the exact final parent report commit and final local/remote/clean identities. Those facts must be durable in the task file rather than exist only in the conversational handoff. No implementation source or test change is requested unless the evidence contradicts the submitted state.

### Reviewed Files

- `moda-interact-admin/src/lib/admin/openrouter-credential-environment.ts`
- `moda-interact-admin/src/lib/admin/openrouter-credential-keyring.ts`
- `moda-interact-admin/src/lib/admin/openrouter-credential-crypto.ts`
- `moda-interact-admin/src/lib/admin/openrouter-credential-validation.ts`
- `moda-interact-admin/src/lib/admin/openrouter-credential.ts`
- `moda-interact-admin/src/app/actions/openrouter-credential.ts`
- `moda-interact-admin/src/app/(protected)/commerce-models/credentials/page.tsx`
- `moda-interact-admin/src/components/admin/openrouter-credential/openrouter-credential-panel.tsx`
- `moda-interact-admin/src/components/admin/openrouter-credential/openrouter-credential-form.tsx`
- `moda-interact-admin/src/components/admin/openrouter-credential/openrouter-credential-submit-button.tsx`
- `moda-interact-admin/src/components/admin/sidebar.tsx`
- `moda-interact-admin/src/components/admin/admin-shell.tsx`
- focused unit/security/navigation tests
- `moda-interact-admin/scripts/validate-arch024-openrouter-credential-admin.mjs`
- this task Completion Report and parent ARCH-024 architecture

### Validation Reviewed

Reviewed the submitted evidence for Prisma generation/validation, 13 focused unit tests, the 2-test Shared-AAD/UTF-8 crypto contract rerun, 12 focused security/navigation tests, targeted ESLint and Prettier, production build, disposable PostgreSQL SET -> REPLACE -> stale-CAS -> REMOVE/interoperability/rollback proof, cleanup evidence and `git diff --check`. The uploaded review snapshot has no `node_modules`, so these Node/PostgreSQL commands were not independently rerun in the architect environment.

### Architecture Conformance

Implementation conforms to ARCH-024, ADMIN-003 scope, the accepted Database contract and published Shared 1.1.0 AAD contract. Secret plaintext/envelope material is not exposed through the status or action result contracts, ordinary Platform ADMIN mutation is rejected before form parsing, REMOVE does not depend on the keyring, and no OpenRouter provider call or production Admin decrypt path was introduced. Acceptance is withheld only for the missing durable preparation/publication evidence.

### Follow-up

**A1-R1 — evidence only; no source/test changes requested.** Reclaim the same task for Attempt 2 and update only the Completion Report/checklist metadata needed to record the launcher-prepared execution packet completely: canonical `workspace_root`; dedicated parent and Admin implementation worktree paths; both `task/ARCH-024-ADMIN-003` branches; start-of-attempt synchronization/base identities; recursive `database/` submodule materialisation at accepted `cfeeb12456b4e05067a96857a8c47837d7e33bbd`; exact Shared `1.1.0` consumption; implementation head `b0a894d65878b81bf533212fab98a48296b34fcf`; final parent report head `3b692a6cd12cc23780e12f4196c14de9316b551a`; proof that each local task head equals its corresponding `origin/task/ARCH-024-ADMIN-003` head; and final clean-worktree evidence for both worktrees. Preserve the Attempt 1 Architect Review unchanged when returning for re-review.

Existing successful implementation validation may be referenced; do not rerun the expensive PostgreSQL/build/test gates solely for this evidence-only correction unless the recorded repository state has changed or the evidence exposes a discrepancy. `git diff --check` and the task-report consistency checks should remain clean. Gateway remains gated until ADMIN-003 is actually Complete and its other dependencies are satisfied.
