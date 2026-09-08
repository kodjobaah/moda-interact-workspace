# ARCH-006 Admin Tasks

Architecture: `docs/architecture/ARCH-006-merchant-communications-support-inbox.md`

Assigned Agent: `moda_admin`

Coordinator: `moda_architect`

| Task | Description | Status | Dependencies |
|---|---|---|---|
| ADMIN-001 | Implement Admin merchant-support server capability | Complete | DATABASE-002, SHARED-002, SHARED-004, ARCH-005-ADMIN-001 |
| ADMIN-002 | Add merchant-communications to the existing Admin queue monitor | Complete | BACKGROUND-007 |
| ADMIN-003 | Implement pending-support queries and exclusive ownership commands | Complete | ADMIN-001 |
| ADMIN-004 | Build the Admin merchant-support inbox UI | Complete | ADMIN-003, BACKGROUND-007 |
| ADMIN-005 | Improve Merchant Messages search and translation language selection | **Review — Attempt 2** | ADMIN-004 |
> **State synchronization — 2026-09-08:** The task table above is regenerated from the individual task YAML frontmatter. Those task files remain authoritative. Historical narrative below may describe earlier frontiers.
The individual task file YAML metadata is authoritative.

`ADMIN-001` Attempt 3 is architect-accepted Complete. The non-English `PROCESSING` compose path now preserves `needsAdminResponse` and `lastAdministrativeMessageAt` until BACKGROUND-006 makes the merchant-language translation AVAILABLE; the English AVAILABLE path may complete the matching response boundary immediately.

`ADMIN-003` Attempt 1 is architect-accepted Complete after independent review. Atomic claim, owner-only release, SUPER_ADMIN reassignment, bounded pending queries, and authorization/concurrency coverage satisfy the task contract.

`BACKGROUND-007` is architect-accepted Complete. `ADMIN-004` Attempt 6 is independently architect-accepted Complete after schema-qualified casts were added for the remaining dynamic PostgreSQL enum-bound parameters (`MerchantSupportMessage.state` and `MerchantMessageTranslation.direction`) with generated-SQL regression coverage. The earlier development-admin materialisation and `FOR UPDATE OF t` corrections remain intact. Terminal ARCH-006 system testing remains deliberately deferred behind the developer manual-validation checkpoint. `ADMIN-002` Attempt 1 is architect-accepted Complete.

The reported 89/90 full-suite result retains one known pre-existing out-of-scope ARCH-005 assertion expecting historical Shared `0.7.0`; that baseline failure did not block ADMIN-001 acceptance.

System-test tasks are terminal/manual-gated and never block these Admin implementation tasks.

`ADMIN-005` Attempt 1 autocomplete is accepted in substance. Manual UI review returned only
the translation selector for Attempt 2. The Admin selector must expose exactly the 20
currently supported merchant languages with human-readable labels and canonical tag
values; the Attempt 1 message-derived / `Other language…` selector is superseded.

Terminal ARCH-006 system testing remains deliberately deferred behind the developer's
manual-validation checkpoint.
