# ARCH-043 Messaging Tasks

Architecture: `docs/architecture/ARCH-043-database-managed-platform-configuration.md` (28 October 2026 Messaging cutover addendum).

Assigned agent: `moda_messaging` (`moda-interact-messaging`). Coordinator: `moda_architect`.

| Task | Objective | Status in 28 October snapshot | Dependencies |
|---|---|---|---|
| `ARCH-043-MESSAGING-001` | Read the existing sealed `messaging.meta` credentials from PostgreSQL for GET/POST Meta webhook authentication, using Messaging-local code and published Shared crypto | Ready (portable definition, not materialised) | `ARCH-043-DATABASE-001`, `ARCH-043-ADMIN-002` (both Complete in snapshot) |

Task file: [`MESSAGING-001-database-backed-meta-webhook-credentials.md`](MESSAGING-001-database-backed-meta-webhook-credentials.md).

**Implementation ownership:** Messaging repository only. There is no new Shared task, no Shared primitive and no change to other application repositories. Gateway/Render provisioning of DB and external unseal credentials remains an explicitly external deployment prerequisite, not an authorised code change in this task.

The individual task's YAML metadata is authoritative for the current status; this index is a planning view. The task must be materialised via the canonical launcher and isolated worktrees before an agent can claim it.
