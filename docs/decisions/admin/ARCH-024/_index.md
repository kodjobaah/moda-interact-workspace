# ARCH-024 Admin tasks

Architecture: [`ARCH-024`](../../../architecture/ARCH-024-commerce-agent-model-runtime-and-test-conversations.md).

Assigned agent: `moda_admin`.

Repository: `moda-interact-admin`.

Coordinator: `moda_architect`.

Admin owns what models exist, where they are available, and the environment OpenRouter credential. Admin does not select the active Agent model.

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
        v
    ADMIN-003
OpenRouter credential
```

| Task | Outcome | Status | Depends on |
|---|---|---|---|
| [ADMIN-001](ADMIN-001-administer-model-availability.md) | Administer the global Platform Availability and zero/one Shop Availability per Shop | Pending | DATABASE-001, SHARED-002 |
| [ADMIN-002](ADMIN-002-administer-model-catalogue-entries.md) | Create/edit/enable/disable/reassign Catalogue Entries and validated OpenRouter-style configuration | Pending | DATABASE-001, SHARED-002, ADMIN-001 |
| [ADMIN-003](ADMIN-003-manage-openrouter-credentials.md) | Set/replace/remove the encrypted OpenRouter credential for the current environment without exposing plaintext | Pending | DATABASE-001, SHARED-002, ADMIN-002 |

## Execution frontier

No Admin task is Ready until the database and published Shared contracts are architect-accepted Complete.

Commerce Studio consumes this state; it does not duplicate Admin Catalogue/Availability/Credential administration.
