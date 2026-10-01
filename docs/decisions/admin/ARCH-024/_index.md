# ARCH-024 Admin tasks

Architecture: [`ARCH-024`](../../../architecture/ARCH-024-commerce-agent-model-runtime-and-test-conversations.md).

Assigned agent: `moda_admin`.

Repository: `moda-interact-admin`.

Coordinator: `moda_architect`.

Admin owns what models exist, where they are available, the optional Merchant Pricing Plan -> model product-tier association, and the environment OpenRouter credential. Admin does not select a merchant-specific active Agent model.

```text
DATABASE-001 + SHARED-002
        |
        +--------------------------+
        |                          |
        v                          v
    ADMIN-001                  ADMIN-004
Model Availability         Price Plan -> model
        |
        v
    ADMIN-002
Model Catalogue
        |
        v
    ADMIN-003
OpenRouter credential
```

| Task | Outcome | Status | Depends on |
|---|---|---|---|
| [ADMIN-001](ADMIN-001-administer-model-availability.md) | Administer the global Platform Availability and zero/one Shop Availability per Shop | Complete | DATABASE-001, SHARED-002 |
| [ADMIN-002](ADMIN-002-administer-model-catalogue-entries.md) | Create/edit/enable/disable/reassign Catalogue Entries and validated OpenRouter-style configuration | Ready | DATABASE-001, SHARED-002, ADMIN-001 |
| [ADMIN-003](ADMIN-003-manage-openrouter-credentials.md) | Set/replace/remove the encrypted OpenRouter credential for the current environment without exposing plaintext | Pending | DATABASE-001, SHARED-002, ADMIN-002 |
| [ADMIN-004](ADMIN-004-assign-commerce-model-to-merchant-pricing-plans.md) | Assign zero/one enabled Platform-available Commerce model to each Merchant Pricing Plan through the existing billing builder | Complete | DATABASE-001, SHARED-002 |

## Execution frontier

Ready: `ARCH-024-ADMIN-002`, `ARCH-024-ADMIN-004`.

ADMIN-001 is Complete at Attempt 2. ADMIN-002 is now Ready because DATABASE-001, SHARED-002 and ADMIN-001 are Complete; it consumes the accepted Database contract plus exactly `@modainteract/moda-interact-shared@1.1.0`. ADMIN-003 remains Pending behind ADMIN-002.

This isolated ADMIN-001 parent branch still carries ADMIN-004 as Ready because the separately accepted ADMIN-004 reconciliation has not been incorporated here. Preserve ADMIN-004's accepted Complete state when the parent task branches are later integrated.
Ready: `ARCH-024-ADMIN-001`.

ADMIN-001 consumes the accepted Database contract plus exactly `@modainteract/moda-interact-shared@1.1.0`. ADMIN-002 remains Pending behind ADMIN-001; ADMIN-003 remains Pending behind ADMIN-002.

ADMIN-004 is Complete at Attempt 1. It consumes the accepted Database/Shared contracts directly and remains independent of the Availability/Catalogue/Credential control-plane chain.

Commerce Studio consumes this state; it does not duplicate Admin Catalogue/Availability/Credential or Price Plan model administration.
