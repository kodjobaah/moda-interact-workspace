# ARCH-003 — System Test Decisions

## Tasks

| Task | Description | Status | Dependencies |
|---|---|---|---|
| SYSTEM-TEST-001 | Verify tenant attribution across operational queues | Pending / manual-gated | BACKGROUND-001, ADMIN-019 |
| SYSTEM-TEST-002 | Verify merchant pending-recovery visibility and tenant isolation | **Blocked** | SHOPIFY-002 |
> **State synchronization — 2026-09-08:** The task table above is regenerated from the individual task YAML frontmatter. Those task files remain authoritative. Historical narrative below may describe earlier frontiers.
## SYSTEM-TEST-002 state

Validator implementation:

```text
Accepted
```

Authoritative task metadata:

```yaml
status: blocked
executor: null
claimed_at: null
attempt: 2
```

Blocker:

```text
developer-owned live Shopify / Redis / browser evidence
```

No further repository-agent implementation is currently required.

Use:

```text
docs/evidence/ARCH-003/SYSTEM-TEST-002-live-evidence-template.json
```

to capture the integrated evidence, then validate it with:

```bash
npm run validate:merchant-pending-recovery:evidence -- <evidence.json>
```


## Current SYSTEM-TEST-002 blocker

The Shopify explicit-JSON resource correction is now Complete.

Remaining gate:

```text
deploy corrected moda-interact
    -> capture authenticated live CDP evidence
    -> validate evidence JSON
    -> architect review
```
