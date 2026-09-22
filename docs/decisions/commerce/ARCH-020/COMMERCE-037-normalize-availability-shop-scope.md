---
id: ARCH-020-COMMERCE-037
architecture_id: ARCH-020
title: Normalize external availability merchant shop scope
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 151
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-020-COMMERCE-028
enables:
  - ARCH-020-COMMERCE-032
created: 2026-09-22
updated: 2026-09-22
---

# Normalize external availability merchant shop scope

## Architecture

ARCH-020 C21 sections 4 and 9.2/9.5.

This task corrects the accepted COMMERCE-028 `checkConnectionAvailability` input
semantics discovered during COMMERCE-032 Attempt 1 review. It does not change
credential storage, encryption, mutation, decryption or connection lifecycle.

## Objective

Make the COMMERCE-028 read-only availability projection accept the trusted merchant
shop ID used by COMMERCE-032 and internally map it to the correct credential scope:

```text
PLATFORM -> credential row shopId = null
PER_SHOP -> credential row shopId = trusted merchant shop ID
```

## Context

Current accepted behavior conflicts:

```text
COMMERCE-032:
  resolve({shopId,candidates,grant})
  passes trusted merchant shopId to availability projection

COMMERCE-028 current:
  interprets availability shopId as credential-row scope key
  PLATFORM therefore requires null
```

A valid PLATFORM external tool is consequently reported as
`CREDENTIAL_MISSING` in the assembled flow.

C21 now defines the availability port's `shopId` as merchant identity, not the
credential-row selector.

## Scope

Only:

- `src/commerce/connections/credentials/index.ts`;
- `tests/external-credentials.test.ts`;
- package metadata only if an existing focused script genuinely needs no suitable
  command (normally no package change is required).

## Out of Scope

Do not modify:

- credential encryption/AES-GCM/AAD/key rotation;
- credential mutation/CAS/replay;
- `getCredentialStatus`;
- `setCredential`;
- `removeCredential`;
- `resolveConnection`;
- COMMERCE-032 source;
- connection lifecycle;
- database schema/migrations;
- Shared;
- UI;
- HTTP execution;
- final composition.

## Requirements

Change only the availability projection contract to:

```ts
checkConnectionAvailability(input: {
  connectionRevisionId: string;
  shopId: string;
}): Promise<
  | {kind:'available'}
  | {
      kind:'excluded';
      reason:
        | 'CONNECTION_DISABLED'
        | 'CONNECTION_REVISION_MISSING'
        | 'CREDENTIAL_MISSING'
        | 'CREDENTIAL_KEY_UNAVAILABLE';
    }
  | {kind:'unavailable'}
>
```

`shopId` is a trusted server-owned merchant ID and is always non-null.

After loading the exact immutable connection revision:

```ts
const credentialShopId =
  revision.scope === 'PLATFORM'
    ? null
    : input.shopId;
```

Then preserve the existing checks:

```text
missing revision
  -> CONNECTION_REVISION_MISSING

disabled connection
  -> CONNECTION_DISABLED

authMode NONE
  -> available
  (PER_SHOP+NONE is already prohibited by lifecycle/database contract)

authenticated revision:
  credential lookup uses credentialShopId

missing exact credential
  -> CREDENTIAL_MISSING

credential key absent/invalid
  -> CREDENTIAL_KEY_UNAVAILABLE

unexpected database/runtime lookup failure
  -> unavailable
```

Do not decrypt credentials in this path.

Do not fall back from a missing PER_SHOP credential to a PLATFORM credential or another
shop.

Do not use caller-provided null to mean PLATFORM in this API; the revision's immutable
scope determines the credential-row selector.

The following existing methods retain their current contracts unchanged:

```text
getCredentialStatus
setCredential
removeCredential
resolveConnection
```

where nullable `shopId` still represents the actual credential scope key.

## Work Items

- [ ] Change only `checkConnectionAvailability` to merchant-shop semantics.
- [ ] Preserve exact PLATFORM/PER_SHOP credential lookup rules.
- [ ] Preserve bounded excluded/unavailable reasons and zero secret decryption.
- [ ] Add focused PLATFORM/PER_SHOP/outage regressions.

## Interfaces / Contracts

Producer:

```text
COMMERCE-028 createCredentialService().checkConnectionAvailability
```

Consumer:

```text
COMMERCE-032 createExternalAvailabilityResolver
```

Canonical consumer call:

```ts
checkConnectionAvailability({
  connectionRevisionId: candidate.connectionRevisionId,
  shopId: trustedMerchantShopId,
})
```

COMMERCE-032 must not need connection scope metadata.

## Dependencies

- ARCH-020-COMMERCE-028

## Enables

- ARCH-020-COMMERCE-032

## Acceptance Criteria

- [ ] PLATFORM + NONE called with merchant `shop-A` returns available without requiring a credential row.
- [ ] PLATFORM + BEARER/API_KEY called with merchant `shop-A` reads the null-scope credential row and returns available when configured.
- [ ] PER_SHOP called with merchant `shop-A` reads only the `shop-A` credential.
- [ ] PER_SHOP called with `shop-B` cannot use the `shop-A` credential and returns `CREDENTIAL_MISSING`.
- [ ] Missing revision, disabled connection and unavailable key preserve the existing exact exclusion reasons.
- [ ] Unexpected lookup failure returns typed `{kind:'unavailable'}`.
- [ ] No secret is decrypted or returned and no mutation/audit occurs.
- [ ] Existing `getCredentialStatus` / mutation / `resolveConnection` contracts remain unchanged.

## Validation

Extend the existing credential focused suite with a dedicated describe block for
availability merchant-scope normalization.

Required focused cases:

```text
PLATFORM NONE + shop-A
  -> available

PLATFORM BEARER + stored credential at revision:null + shop-A input
  -> available
  -> credential lookup key uses null, not shop-A

PER_SHOP API_KEY + stored shop-A credential + shop-A input
  -> available

same revision + shop-B input
  -> CREDENTIAL_MISSING
  -> never reads/falls back to shop-A

disabled
  -> CONNECTION_DISABLED

missing revision
  -> CONNECTION_REVISION_MISSING

credential references absent key
  -> CREDENTIAL_KEY_UNAVAILABLE

underlying lookup throws
  -> {kind:'unavailable'}
```

Run exactly:

```bash
npm run test:arch020-external-credentials

npx eslint \
  src/commerce/connections/credentials \
  tests/external-credentials.test.ts

npm run lint
npm run typecheck
npm run build
git diff --check
```

If repository-wide lint/typecheck/build retain only the existing unrelated baseline,
record exact diagnostics and prove no task-owned diagnostic.

## Stop Condition

After the source correction and focused regressions pass:

```text
update Work Items / Acceptance Criteria / Validation
complete the Completion Report
set status: review
clear executor / claimed_at
push implementation and parent task branches
return to moda_architect
STOP
```

Do not begin COMMERCE-032 or COMMERCE-024 automatically.

## Implementation Notes

This is a read-only availability-port normalization only.

The invariant is:

```text
Availability asks:
  "Can merchant shop X use this pinned connection revision now?"

Credential storage asks:
  "Which credential row is addressed by this revision scope?"

These are not the same shopId semantics for PLATFORM.
```

## Completion Report

### Status

Not Started.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

None beyond the binding contract above.

### Unresolved Issues

None known.

### Architectural Concerns

None beyond the producer/consumer mismatch this task resolves.

## Architect Review

### Review Status

Pending.

### Review Notes

Pending implementation.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending.

### Follow-up

Execute only after an authorized `/moda-task ARCH-020-COMMERCE-037` claim.
