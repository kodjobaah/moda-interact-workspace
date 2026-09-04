# SYSTEM-TEST-006 — Reusable Render Validator Naming Migration

This document is an architect clarification for the current
`ARCH-002-SYSTEM-TEST-006` implementation.

It changes **naming and separation of responsibilities only**. It does not
change the gateway routing contract or live validation ownership.

## Replace architecture/task-specific reusable names

Migrate:

```text
npm run validate:arch002-render-test
    ->
npm run validate:render:test
```

Migrate:

```text
scripts/run-arch002-render-test-topology.js
    ->
scripts/validate-render-deployment.js
```

Migrate the current task-specific developer runner:

```text
scripts/system-test-006-developer-validation.sh
```

into two responsibilities:

```text
scripts/validate-render-test.sh
    developer-only secure Render-test input bootstrap + output redaction

scripts/developer-validation.sh
    generic TASK-ID evidence capture
```

Do not retain the old names as permanent aliases unless an architect explicitly
requires a compatibility window. Historical evidence may keep the old names.

## Package command

Target:

```json
{
  "scripts": {
    "validate:render:test":
      "node scripts/validate-render-deployment.js --environment test"
  }
}
```

Do not add a production command until production validation is actually
implemented.

## Developer execution

After the task returns to review, the developer should run:

```bash
./scripts/developer-validation.sh \
  ARCH-002-SYSTEM-TEST-006 \
  -- ./scripts/validate-render-test.sh
```

`validate-render-test.sh` must:

```text
set canonical non-secret test hosts;
prompt silently for required Shopify/Meta secrets when absent;
never print secret values;
redact secret literal and URL-encoded forms from downstream output;
invoke npm run validate:render:test;
return the same exit code.
```

The generic `developer-validation.sh` must not know about:

```text
ARCH-002
SYSTEM-TEST-006
Render hostnames
Shopify secrets
Meta secrets
```

except for the TASK_ID supplied by the developer at runtime.

## Current host matrix

The current test bootstrap owns these non-secret constants:

```text
ARCH002_TEST_GATEWAY_URL=https://moda-interact-gateway-test.onrender.com
ARCH002_TEST_APP_HOST=app-test.modainteract.com
ARCH002_TEST_ADMIN_HOST=admin-test.modainteract.com
ARCH002_TEST_MESSAGING_HOST=messaging-test.modainteract.com
```

These remain current input variable names for this test contract. Their
environment-variable names may continue to contain `ARCH002` because they are
task/test-contract inputs rather than permanent executable names.

Do not rename those input variables during the current correction unless the
architect separately asks for it.

## Live-execution hard stop

The agent MUST NOT execute any of:

```bash
npm run validate:render:test
./scripts/validate-render-test.sh
./scripts/developer-validation.sh ARCH-002-SYSTEM-TEST-006 -- ./scripts/validate-render-test.sh
```

without explicit current developer authorization.

The agent implements and locally validates; the developer launches the deployed
probe.

## Do not broaden this migration

Do not rename in this task:

```text
validate:arch002-observability
run-arch002-observability.js

validate:arch002-production-readiness
run-arch002-production-readiness.js
```

Those may be evaluated separately after SYSTEM-TEST-006 is accepted.
