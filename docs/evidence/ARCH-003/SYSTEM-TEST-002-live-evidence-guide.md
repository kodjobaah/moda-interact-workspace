# SYSTEM-TEST-002 Live Evidence Guide

Use the companion JSON template:

```text
SYSTEM-TEST-002-live-evidence-template.json
```

Replace every placeholder with values observed from the current development
environment.

## Required live sequence

1. Authenticate to the Shopify merchant application.
2. Create a fresh checkout that becomes a delayed pending-recovery candidate.
3. Record the internal shop ID and domain.
4. Record the active BullMQ candidate job and confirm its state/data.
5. Confirm the job ID is present in the shop-scoped pending ZSET.
6. Open `/app` and record the safe Pending recoveries response.
7. Confirm manual Refresh and `Last updated`.
8. Exercise page-2 refresh with enough controlled pending candidates.
9. Exercise result shrink/fallback and confirm the subsequent refresh uses the
   effective fallback page.
10. Mature or cancel the original candidate.
11. Confirm it is absent from both the shop index and merchant response.
12. Record a cross-tenant isolation observation.
13. Record the safe Redis-unavailable Pending recoveries response while current
    and past usage remain available.
14. Confirm no full page reload and no automatic polling.

## Validation

From `moda-interact-system-test`:

```bash
npm run validate:merchant-pending-recovery:evidence -- \
  ../docs/evidence/ARCH-003/SYSTEM-TEST-002-live-evidence.json
```

Expected result:

```json
{
  "valid": true,
  "errors": []
}
```

Do not put secrets, Redis URLs, access tokens, session cookies or credentials in
the evidence file.
