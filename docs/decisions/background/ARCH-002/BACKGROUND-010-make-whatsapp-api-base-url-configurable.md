---
id: ARCH-002-BACKGROUND-010
architecture_id: ARCH-002
title: Make outbound WhatsApp API base URL configurable
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
status: complete
priority: 32
executor: copilot
claimed_at: 2026-09-02T22:39:51Z
attempt: 1
depends_on: []
enables:
  - ARCH-002-SYSTEM-TEST-004
created: 2026-09-02
updated: 2026-09-02
---

# Make Outbound WhatsApp API Base URL Configurable

## Architecture

Architecture ID:

`ARCH-002`

Architecture document:

`docs/architecture/ARCH-002-render-production-gateway-infrastructure.md`

Coordinator:

`moda_architect`

## Objective

Add the smallest production-safe configuration seam required for architecture
system tests to point Moda's existing outbound WhatsApp Cloud API client at the
test-owned emulator.

The current production client hard-codes:

```text
https://graph.facebook.com/v25.0/${phoneNumberId}/messages
```

in:

```text
moda-interact-background/src/services/whatsapp.service.ts
```

The system-test emulator cannot exercise a real Moda outbound call until the
owning Background service can override that API base URL.

## Scope

Modify only `moda-interact-background` behavior and documentation/tests required
for this configuration seam.

The implementation must:

- introduce an optional outbound WhatsApp API base-URL configuration;
- preserve the exact current Meta Graph API URL when no override is configured;
- allow system tests to point the client at a local/emulated HTTP endpoint;
- continue appending the configured phone-number ID and `/messages` path;
- preserve the existing access-token authorization behavior;
- preserve the existing WhatsApp request payload;
- preserve the existing response/error contract.

## Required Configuration Contract

Use:

```text
WHATSAPP_API_BASE_URL
```

as the optional override.

Default when unset or blank:

```text
https://graph.facebook.com/v25.0
```

The final outbound URL must be logically equivalent to:

```text
<normalized-base-url>/<phoneNumberId>/messages
```

A trailing slash in `WHATSAPP_API_BASE_URL` must not produce a double slash
before the phone-number ID.

Examples:

```text
unset:
  https://graph.facebook.com/v25.0/123/messages

WHATSAPP_API_BASE_URL=http://127.0.0.1:45678:
  http://127.0.0.1:45678/123/messages
```

Do not change the required:

```text
WHATSAPP_PHONE_NUMBER_ID
WHATSAPP_ACCESS_TOKEN
```

contract.

## Requirements

### Production compatibility

With `WHATSAPP_API_BASE_URL` unset, outbound behavior must remain exactly on the
existing Meta endpoint family:

```text
https://graph.facebook.com/v25.0
```

This task must not silently upgrade or change the Graph API version.

### Test injection

With `WHATSAPP_API_BASE_URL` set, the actual `WhatsAppService` outbound request
must use that base URL.

Do not implement a test-only HTTP interception layer.

### Security

Do not:

- commit any Meta credential;
- log the access token;
- expose the access token in errors;
- weaken outbound authorization;
- bypass provider signature verification;
- allow this task to modify inbound webhook verification behavior.

The configurable URL is deployment/test configuration, not a credential.

### Ownership

This task belongs only to:

```text
moda_background
```

Do not modify `moda-interact-system-test` from this task.

`SYSTEM-TEST-004` will consume the new capability after architect acceptance.

## Out of Scope

- implementing the WhatsApp emulator fixture;
- changing Meta webhook verification;
- changing WhatsApp message business logic;
- changing message persistence/correlation;
- changing retry or queue semantics;
- changing Graph API version;
- sending a real WhatsApp message;
- changing production credentials;
- modifying another repository.

## Work Items

- [x] inspect the current WhatsApp service and focused tests;
- [x] add the optional `WHATSAPP_API_BASE_URL` configuration seam;
- [x] preserve the current production default;
- [x] normalize a trailing slash safely;
- [x] add focused executable tests for default and overridden URLs;
- [x] prove auth/payload behavior remains intact;
- [x] document the optional configuration;
- [x] run task-relevant repository validation;
- [x] update the Completion Report;
- [x] transition `in_progress -> review`;
- [x] stop without commit/push.

## Validation

At minimum add executable tests proving:

```text
WHATSAPP_API_BASE_URL unset
  -> request uses
     https://graph.facebook.com/v25.0/<phoneNumberId>/messages

WHATSAPP_API_BASE_URL custom
  -> request uses
     <custom-base>/<phoneNumberId>/messages

WHATSAPP_API_BASE_URL custom with trailing slash
  -> no double slash before <phoneNumberId>

all cases
  -> Authorization: Bearer <configured token>
  -> existing WhatsApp text payload preserved
```

Use a mocked/injected `fetch` or equivalent deterministic HTTP test mechanism.
Do not send a real Meta request.

Run only task-relevant validation plus the Background repository's normal
required checks where practical.

## Acceptance Criteria

- [x] production default remains `https://graph.facebook.com/v25.0`;
- [x] actual outbound WhatsApp calls can use an injected base URL;
- [x] phone-number ID and `/messages` path are preserved;
- [x] trailing slash normalization is deterministic;
- [x] access-token authorization remains unchanged;
- [x] request payload remains unchanged;
- [x] no real Meta request is made by tests;
- [x] no production credential is committed;
- [x] no unrelated Background behavior is changed;
- [x] Completion Report records validation evidence;
- [x] repository agent transitions `in_progress -> review`;
- [x] repository agent does not commit or push.

## Completion Report

### Status

Ready for Review

### Files Changed

- `src/services/whatsapp.service.ts`
- `tests/unit/services/whatsapp.service.test.ts`
- `README.md`

### Work Completed

Added the optional `WHATSAPP_API_BASE_URL` configuration. Blank or unset values
use the unchanged default `https://graph.facebook.com/v25.0`; configured values
are trimmed of trailing slashes before appending the existing phone-number ID
and `/messages` path. The existing bearer authorization, text payload, response
handling, and required phone-number/access-token variables are unchanged.

Added deterministic mocked-fetch tests for unset, blank, custom, and
trailing-slash base URLs, including URL, authorization, and payload assertions.
Documented the optional environment variable.

### Validation Results

- Focused test: `npm test -- tests/unit/services/whatsapp.service.test.ts` passed
  6/6.
- Build/typecheck: `npm run build` passed, including TypeScript compilation.
- Diff hygiene: `git diff --check` passed.
- Full suite: `npm test` had 17 passing files, 2 skipped files, and one unrelated
  pre-existing failure in `tests/unit/services/recovery-routing.service.test.ts`
  because its mock lacks `customerPhone.findMany`. No WhatsApp task test failed.
- Tests use mocked fetch only; no real Meta request or credential was used.

### Deviations

The full repository suite is not fully green because of the unrelated
`recovery-routing.service.test.ts` mock failure described above. That test was
not modified.

### Assumptions

`WHATSAPP_API_BASE_URL` is deployment/test configuration and, when set, includes
the API host and optional path prefix before the phone-number ID.

### Unresolved Issues

None for this task. The unrelated full-suite failure remains outside scope.

### Architectural Concerns

None. The change is limited to outbound URL configuration and preserves the
existing Graph API version and messaging behavior.

## Architect Review

### Review Status

Accepted / Complete

### Review Notes

`ARCH-002-BACKGROUND-010` is architect-accepted.

The implementation adds only the configuration seam required by the
architecture-owned WhatsApp emulator.

### Runtime Contract Reviewed

The actual outbound client now defines:

```text
DEFAULT_WHATSAPP_API_BASE_URL
  = https://graph.facebook.com/v25.0
```

and resolves:

```text
WHATSAPP_API_BASE_URL
  -> trim whitespace
  -> fall back to the exact existing Meta v25.0 base when blank/unset
  -> remove trailing slashes
  -> append /<WHATSAPP_PHONE_NUMBER_ID>/messages
```

Therefore production behavior remains:

```text
https://graph.facebook.com/v25.0/<phoneNumberId>/messages
```

unless an explicit deployment/test override is supplied.

### Provider Contract Preservation Reviewed

The implementation preserves:

```text
Authorization: Bearer <WHATSAPP_ACCESS_TOKEN>
Content-Type: application/json

{
  messaging_product: "whatsapp",
  to,
  type: "text",
  text: {
    body: text
  }
}
```

Existing response/error behavior is unchanged.

No inbound webhook verification behavior is modified.

### Focused Tests Reviewed

The submitted executable tests cover:

```text
WHATSAPP_API_BASE_URL undefined
WHATSAPP_API_BASE_URL empty
WHATSAPP_API_BASE_URL whitespace-only
custom localhost base
custom localhost base with trailing slash
custom localhost base with multiple trailing slashes
```

They assert:

```text
exact default Graph API URL
custom emulator URL
no duplicate slash before phone-number ID
Bearer authorization
unchanged text payload
provider message ID handling
```

The tests inject/mock `fetch`; they do not contact Meta.

### Validation Evidence Reviewed

The repository-agent Completion Report records:

```text
focused WhatsApp service tests
  6/6 PASS

npm run build
  PASS

git diff --check
  PASS
```

The full repository suite still contains the previously known unrelated
`recovery-routing.service.test.ts` mock failure because its mock lacks
`customerPhone.findMany`.

No WhatsApp task test failed.

The architect could not independently execute the Node test/build commands from
the submitted archive because dependency installation (`node_modules`) is not
included in the review bundle. Source and focused-test inspection are
consistent with the reported validation.

### Architecture Conformance

Accepted.

The task modifies only the Background-owned outbound provider configuration
boundary.

It does not:

```text
change Graph API version
change queue/retry semantics
change messaging business logic
modify system-test implementation
send a real WhatsApp message
commit a production credential
```

### Git / Publication

The repository agent stopped at Review and did not commit or push.

Accepted Background changes are ready for developer commit/push.

### Downstream Coordination

`ARCH-002-BACKGROUND-010` is Complete.

The only direct dependency of:

```text
ARCH-002-SYSTEM-TEST-004
```

is therefore satisfied.

The architect transitions:

```text
SYSTEM-TEST-004
  blocked -> ready
```

The previous blocked execution claim is cleared.

The next repository-agent claim should create a new attempt according to the
normal task protocol.

`SYSTEM-TEST-001` and `SYSTEM-TEST-002` remain Pending until all of their own
explicit direct dependencies are Complete.

No downstream implementation is automatically started.
