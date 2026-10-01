# ARCH-024 Admin tasks

Architecture: [`ARCH-024`](../../../architecture/ARCH-024-commerce-agent-model-runtime-and-test-conversations.md).

Assigned agent: `moda_admin`.

Repository: `moda-interact-admin`.

Coordinator: `moda_architect`.

Admin owns what models exist, where they are available, the optional Merchant Pricing Plan -> model product-tier association, and the environment OpenRouter credential. Admin does not select a merchant-specific active Agent model.

```text
DATABASE-001 + SHARED-002
        |
        v
    ADMIN-001
Model Availability
        |
        v
    ADMIN-002
Model Catalogue
        |
        +--------------------+
        |                    |
        v                    v
    ADMIN-003            ADMIN-004
OpenRouter credential    Price Plan -> model
```

| Task | Outcome | Status | Depends on |
|---|---|---|---|
| [ADMIN-001](ADMIN-001-administer-model-availability.md) | Administer the global Platform Availability and zero/one Shop Availability per Shop | Pending | DATABASE-001, SHARED-002 |
| [ADMIN-002](ADMIN-002-administer-model-catalogue-entries.md) | Create/edit/enable/disable/reassign Catalogue Entries and validated OpenRouter-style configuration | Pending | DATABASE-001, SHARED-002, ADMIN-001 |
| [ADMIN-003](ADMIN-003-manage-openrouter-credentials.md) | Set/replace/remove the encrypted OpenRouter credential for the current environment without exposing plaintext | Pending | DATABASE-001, SHARED-002, ADMIN-002 |
| [ADMIN-004](ADMIN-004-assign-commerce-model-to-merchant-pricing-plans.md) | Assign zero/one enabled Platform-available Commerce model to each Merchant Pricing Plan through the existing billing builder | Pending | DATABASE-001, SHARED-002, ADMIN-002 |

## Execution frontier

No Admin task is Ready until the database and published Shared contracts/runtime are architect-accepted Complete.

Commerce Studio consumes this state; it does not duplicate Admin Catalogue/Availability/Credential or Price Plan model administration. `ADMIN-003` and `ADMIN-004` may execute independently after `ADMIN-002` is Complete.
