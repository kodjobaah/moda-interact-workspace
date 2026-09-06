# ARCH-005 — Background Tasks

| Task | Description | Status | Dependencies |
|---|---|---|---|
| ARCH-005-BACKGROUND-001 | Adopt and materialise Shopify international context | Complete — architect accepted (Attempt 4) | SHARED-004, DATABASE-001 |
| ARCH-005-BACKGROUND-002 | Select approved WhatsApp templates by locale and market capability | Complete — architect accepted (Attempt 1) | BACKGROUND-001, DATABASE-002 |
| ARCH-005-BACKGROUND-003 | Send selected approved WhatsApp template for proactive recovery | Complete — architect accepted (Attempt 2) | BACKGROUND-002 |
| ARCH-005-BACKGROUND-004 | Resolve conversation language and localise CommerceAgent responses | Complete — architect accepted (Attempt 4) | BACKGROUND-001 |

## Ownership correction

Architect review of `ARCH-005-MESSAGING-001` confirmed that template selection,
proactive outbound sending and CommerceAgent conversation processing execute in
Background, not in the inbound Messaging service.

Immediate independent Background tasks:

```text
ARCH-005-BACKGROUND-003
ARCH-005-BACKGROUND-004
```

`BACKGROUND-002` and `BACKGROUND-003` are architect-accepted. The proactive
provider-template path is complete, including truthful durable template-send history.
`BACKGROUND-004` is architect-accepted after Attempt 4. The CommerceAgent model is deployment-configurable through `GROQ_COMMERCE_MODEL`; manual real-provider validation succeeded with `qwen/qwen3.6-27b` through the production agent path. This validates the configurable model contract and does not hardcode that model into the architecture.
