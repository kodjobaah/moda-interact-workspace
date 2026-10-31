# ARCH-043 Messaging Tasks

Architecture: `docs/architecture/ARCH-043-database-managed-platform-configuration.md` (28 October 2026 Messaging cutover addendum).

Assigned agent: `moda_messaging` (`moda-interact-messaging`). Coordinator: `moda_architect`.

| Task | Objective | Current status | Dependencies |
|---|---|---|---|
| `ARCH-043-MESSAGING-001` | Read the existing sealed `messaging.meta` credentials from PostgreSQL for GET/POST Meta webhook authentication, using Messaging-local code and published Shared crypto | Ready (validation correction requested) | `ARCH-043-DATABASE-001`, `ARCH-043-ADMIN-002` (both Complete in snapshot) |

Task file: [`MESSAGING-001-database-backed-meta-webhook-credentials.md`](MESSAGING-001-database-backed-meta-webhook-credentials.md).

**Implementation ownership:** Messaging repository only. There is no new Shared task, no Shared primitive and no change to other application repositories. Gateway/Render provisioning of DB and external unseal credentials remains an explicitly external deployment prerequisite, not an authorised code change in this task.

The individual task YAML is authoritative. Both dependencies are Complete; acceptance awaits the guarded PostgreSQL integration and query-timeout evidence specified in the current Architect Review. The task has been materialised and must be reclaimed through the canonical launcher.
