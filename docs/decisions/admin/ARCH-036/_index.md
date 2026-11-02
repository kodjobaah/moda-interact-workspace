# ARCH-036 Admin Tasks

Architecture: [ARCH-036-shared-commerce-discount-catalogue](../../../architecture/ARCH-036-shared-commerce-discount-catalogue.md).

Reconciled on 2026-11-02. Individual task frontmatter and review reports are authoritative. Superseded tasks must not be executed.

| Task | Outcome | Status | Dependencies |
|---|---|---|---|
| [ARCH-036-ADMIN-001](ADMIN-001-make-internal-discount-catalogue-provider-aware.md) | Show provider status and merchant selection separately in Admin | complete | `ARCH-036-BACKGROUND-001` |

Admin reads and override writes must independently validate same-Shop provider choices; selection flags do not prove checkout eligibility. See the task’s 2 November readiness correction.

Attempt 1 accepted and explicitly developer-completed on 2026-11-02; implementation and report published.
