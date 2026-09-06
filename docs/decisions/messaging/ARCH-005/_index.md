# ARCH-005 — Messaging Tasks

| Task | Description | Status | Dependencies |
|---|---|---|---|
| ARCH-005-MESSAGING-001 | Select approved WhatsApp templates by locale and market capability | Superseded — rehomed to BACKGROUND-002/003 | SHARED-002, DATABASE-001, DATABASE-002, BACKGROUND-001 |
| ARCH-005-MESSAGING-002 | Resolve conversation language and localise CommerceAgent responses | Superseded — rehomed to BACKGROUND-004 | MESSAGING-001 |
| ARCH-005-MESSAGING-003 | Remove superseded WhatsApp template-selector residue | Complete | BACKGROUND-002, BACKGROUND-003 |

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
