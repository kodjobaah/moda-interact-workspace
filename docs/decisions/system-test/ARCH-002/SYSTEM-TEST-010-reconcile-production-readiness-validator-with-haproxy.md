---
id: ARCH-002-SYSTEM-TEST-010
architecture_id: ARCH-002
title: Reconcile production-readiness validator with accepted HAProxy gateway
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
status: ready
priority: 47
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-002-GATEWAY-014
enables: []
created: 2026-09-04
updated: 2026-09-04
---

# Reconcile Production-Readiness Validator With Accepted HAProxy Gateway

## Objective

Remove the stale NGINX assumptions from the already-existing production
Blueprint/readiness system-test validator after the accepted GATEWAY-014
migration to HAProxy.

## Current Evidence

Repository-wide:

```bash
npm test
```

currently reports a large cluster of failures because
`test/render-blueprint-validation.test.js` still reads:

```text
moda-interact-gateway/nginx/nginx.conf.template
```

That file was intentionally removed by the accepted HAProxy migration.

The corresponding validator also still asserts NGINX-specific configuration.

## Scope

Update only the system-test production-readiness validator and its tests to use
the accepted HAProxy gateway configuration/contracts.

Do not reopen GATEWAY-014 and do not modify the gateway repository merely to
restore an obsolete NGINX fixture.

## Acceptance

- [ ] no active system-test reads the removed NGINX template.
- [ ] equivalent accepted HAProxy Host-routing/private-upstream contracts are
      validated.
- [ ] production-readiness semantics are preserved.
- [ ] `npm test` returns green except for explicitly opt-in Docker tests.
- [ ] typecheck/lint/diff checks pass.
- [ ] no live deployed environment is required.
- [ ] no agent commit/push.
