# ARCH-007 Shared Tasks

Architecture: `docs/architecture/ARCH-007-shopify-billing-usage-cost-control.md`

Assigned Agent: `moda_shared`

Coordinator: `moda_architect`

| Task | Description | Status | Dependencies |
|---|---|---|---|
| SHARED-001 | Define canonical ARCH-007 billing and provider-status contracts | Complete | DATABASE-003 |
| SHARED-002 | Publish the accepted ARCH-007 billing contract release | Complete | SHARED-001 |
| SHARED-003 | Correct normalized WhatsApp provider-status routing contract to schema v2 | Complete | SHARED-002 |
| SHARED-004 | Publish corrected provider-status v2 Shared release 0.7.4 | Complete | SHARED-003 |
| SHARED-005 | Add canonical recovery-credit pack billing metric | Complete | DATABASE-005 |
| SHARED-006 | Publish Shared recovery-credit billing contract | Complete | SHARED-005 |
> **State synchronization — 2026-09-08:** The task table above is regenerated from the individual task YAML frontmatter. Those task files remain authoritative. Historical narrative below may describe earlier frontiers.
The individual task YAML metadata is authoritative.

Current architect-accepted/published Shared release:

```text
@modainteract/moda-interact-shared@0.8.0
```

That release contains the accepted ARCH-007 billing contract and provider-status schema v2. `ARCH-007-MESSAGING-001` Attempt 3 is architect-accepted Complete against exact `0.7.4`.

`SHARED-005` Attempt 1 and `SHARED-006` Attempt 1 are architect-accepted Complete. `@modainteract/moda-interact-shared@0.8.0` is now the current accepted/published Shared release. The lockfile metadata correction was performed by the developer without a second publication attempt.