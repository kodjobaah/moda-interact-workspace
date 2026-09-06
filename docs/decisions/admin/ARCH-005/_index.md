# ARCH-005 — Admin Tasks

| Task | Description | Status | Dependencies |
|---|---|---|---|
| ARCH-005-ADMIN-001 | Adopt shared ICU internationalisation runtime across the current Admin UI | Complete | SHARED-006 |

Current executable ARCH-005 Admin task:

```text
ARCH-005-ADMIN-001
```

Required ordering:

```text
ARCH-005-SHARED-005
  -> ARCH-005-SHARED-006
  -> ARCH-005-ADMIN-001
  -> ARCH-006-ADMIN-001
```

Attempt 1 was rejected because it internationalised reusable primitives but left substantial page-specific UI copy hard-coded in English.

Attempt 2 completed the exhaustive page/component migration and is retained. Architect review found three bounded correctness gaps only: the Admin required-key set is self-derived from the catalogue, known WhatsApp sender types still fall back to raw enum identifiers, and two Moda-owned queue job display labels are still hard-coded/displayed from the queue definition.

Attempt 3 implemented the three bounded production corrections and is retained. Architect review found two remaining acceptance-evidence gaps only: the unknown sender raw-fallback regression is not explicit, and the queue-label regression does not independently prove both the summary and detail render locations.

Attempt 4 was validation-only: both regressions were strengthened, Attempt 3 production behaviour was preserved, and `moda_architect` independently reviewed and accepted the task on 2026-09-06.
