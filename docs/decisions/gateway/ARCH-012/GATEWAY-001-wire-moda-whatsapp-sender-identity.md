---
id: ARCH-012-GATEWAY-001
architecture_id: ARCH-012
title: Wire Moda WhatsApp WABA and sender identity in Render configuration
task_kind: implementation
domain: gateway
repository: moda-interact-gateway
assigned_agent: moda_gateway
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 31
executor: null
claimed_at: null
attempt: 1
depends_on:
- ARCH-012-BACKGROUND-003
enables:
- ARCH-012-SYSTEM-TEST-001
- ARCH-012-SYSTEM-TEST-002
created: 2026-09-14
updated: 2026-09-16
---

# ARCH-012-GATEWAY-001

## Objective
Update the canonical Render test/production topology so the Background messaging worker receives the WABA/account identity required by BACKGROUND-003 while preserving existing Moda-owned phone/token configuration.

## Current topology
The snapshot already wires `WHATSAPP_ACCESS_TOKEN`, `WHATSAPP_PHONE_NUMBER_ID` and `GROQ_API_KEY` to the messaging worker. ARCH-012 adds one missing identity:

```text
WHATSAPP_BUSINESS_ACCOUNT_ID
```

No new service or network exposure is required.

## Authorized implementation surface

```text
render.test.yaml
render.production.yaml
docs/deployment-prerequisites.md
tests/validate-render-blueprints.sh
other existing gateway validation fixture only if required by the changed declaration
```

Do not edit application repositories.

## Exact configuration
For `moda-messaging-worker-test` and `moda-messaging-worker-production`:

- declare `WHATSAPP_BUSINESS_ACCOUNT_ID` using the same secret/environment-group governance pattern as existing WhatsApp credentials;
- do not commit the actual WABA ID value if the existing blueprint treats provider identities as externally supplied configuration;
- preserve `WHATSAPP_PHONE_NUMBER_ID`, `WHATSAPP_ACCESS_TOKEN`, `GROQ_API_KEY`, Redis/Postgres/Shopify and OTEL configuration;
- do not expose Meta/WhatsApp credentials to services that do not require them;
- no new public route/service.

`GROQ_TRANSCRIPTION_MODEL` is optional in BACKGROUND-002 and therefore does **not** require a blueprint variable in this task unless the accepted BACKGROUND-002 implementation makes it mandatory. If that implementation changes the requirement, STOP for architect reconciliation rather than silently extending scope.

## Required tests
Update blueprint validation to prove:

- both messaging workers have WABA ID + phone-number ID + token;
- WABA ID is not substituted for phone-number ID;
- no secret literal is committed;
- unrelated services do not gain WhatsApp credentials;
- test and production topology remains otherwise unchanged.

## Acceptance Criteria

- [ ] application can distinguish WABA/account identity from sender phone-number identity in both environments;
- [ ] no new infrastructure service is introduced;
- [ ] credential least-privilege is preserved.

## Validation
Use existing gateway scripts exactly as declared, including at minimum:

```text
bash tests/validate-render-blueprints.sh
bash tests/validate-render-blueprints-negative.sh
bash tests/run-tests.sh
git diff --check
```

Run other existing required gateway/developer validation scripts if `package`/README/task conventions require them.

## Stop conditions
STOP if Render cannot represent the required variable without manual drift or if BACKGROUND-003 does not actually require `WHATSAPP_BUSINESS_ACCOUNT_ID` after architect acceptance.

## Completion protocol
Return GATEWAY-001 to `review`; STOP.

## Completion Report

### Status
Ready for Review.

### Files Changed
- `moda-interact-gateway/render.test.yaml`
- `moda-interact-gateway/render.production.yaml`
- `moda-interact-gateway/tests/validate-render-blueprints.sh`
- `moda-interact-gateway/tests/validate-render-blueprints-negative.sh`

Implementation commit: `64cb326` (`feat(gateway): wire WhatsApp business account identity`), pushed to `task/ARCH-012-GATEWAY-001`.

### Validation Results
- `bash tests/validate-render-blueprints.sh`: passed for test and production Blueprints.
- `bash tests/validate-render-blueprints-negative.sh`: passed; all negative cases rejected, including WABA-for-phone-number substitution.
- `bash -n tests/validate-render-blueprints.sh tests/validate-render-blueprints-negative.sh`: passed.
- `git diff --check`: passed.
- `bash tests/run-tests.sh`: explicitly run once; gateway integration checks passed through the final visible sensitive-query upstream-failure section, but the terminal command timed out at 120 seconds before returning an exit summary. No retry was performed. Developer validation remains required at the implementation revision.

Developer validation required:
- `bash tests/run-tests.sh` from `moda-interact-gateway/`; expected success is exit code 0 with the final suite summary reporting zero failures.

## Architect Review

### Review Status
Not reviewed.

### Review Notes
TBD.
