# ARCH-005 — Messaging Tasks

| Task | Description | Status | Dependencies |
|---|---|---|---|
| MESSAGING-001 | Select approved WhatsApp templates by locale and market capability | Superseded | SHARED-002, DATABASE-001, DATABASE-002, BACKGROUND-001 |
| MESSAGING-002 | Resolve conversation language and localise CommerceAgent responses | Superseded | MESSAGING-001 |
| MESSAGING-003 | Remove superseded WhatsApp template-selector residue | Complete | BACKGROUND-002, BACKGROUND-003 |
> **State synchronization — 2026-09-08:** The task table above is regenerated from the individual task YAML frontmatter. Those task files remain authoritative. Historical narrative below may describe earlier frontiers.
## Architect ownership correction

`moda-interact-messaging` remains the stateless Meta/WhatsApp inbound ingress
boundary. It must not become the owner of Prisma-backed template selection,
proactive outbound recovery sending, conversation language persistence or
CommerceAgent execution.

Replacement tasks:

```text
ARCH-005-BACKGROUND-002
  deterministic approved-template selection

ARCH-005-BACKGROUND-003
  proactive provider-template send integration

ARCH-005-BACKGROUND-004
  active-conversation language + CommerceAgent localisation
```

`ARCH-005-MESSAGING-001` and `ARCH-005-MESSAGING-002` must never be claimed; both are architect-superseded.

`ARCH-005-MESSAGING-003` is architect-accepted and Complete. No executable ARCH-005 Messaging task remains.

The cleanup removed only the unused selector residue left by the superseded MESSAGING-001 attempt; template-selection behaviour remains owned by Background and must not be recreated in Messaging.

`ARCH-005-SYSTEM-TEST-001` is terminal/manual-gated validation. Messaging completion may satisfy one of its prerequisites, but system-test execution must only begin after explicit developer approval following manual architecture verification.
