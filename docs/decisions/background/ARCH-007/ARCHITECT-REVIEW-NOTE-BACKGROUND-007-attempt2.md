# ARCH-007 BACKGROUND-007 Attempt 2 review note

Attempt 2 received **Changes Requested** for one remaining configuration-state integration defect.

Attempt 2 correctly implemented:

- one lazily cached default App Events client per publisher service instance;
- BACKGROUND-006 token-cache reuse across scans;
- claimed-attempt retry delays of 60s, 120s, 240s, capped at 60 minutes;
- stable permanent Shopify idempotency identity.

The remaining issue is that default-client construction currently occurs before the due-row state machine. Missing App Events credentials therefore throw out of `publishDue()` rather than moving a claimed reportable UsageEvent to `NEEDS_ATTENTION`.

The authoritative Attempt 3 correction contract is the latest `## Architect Review` in:

```text
docs/decisions/background/ARCH-007/BACKGROUND-007-durable-shopify-billing-publisher.md
```

Do not redesign the publisher or modify the already-correct token reuse/backoff behavior.
