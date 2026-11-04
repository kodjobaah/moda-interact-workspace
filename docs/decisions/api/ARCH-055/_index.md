# ARCH-055 API Tasks

Architecture: [ARCH-055](../../../architecture/ARCH-055-woocommerce-api-database-correctness-and-efficiency.md).

Reconciled 2026-11-04. Individual task frontmatter and review reports are authoritative.

| Task | Outcome | Status | Dependencies |
|---|---|---|---|
| [ARCH-055-API-001](API-001-harden-installation-and-read-authorization-lifecycle.md) | Harden installation and read authorization lifecycle | Complete | `ARCH-055-DATABASE-001` |
| [ARCH-055-API-002](API-002-streamline-consent-and-recovery-ingress.md) | Streamline consent and recovery ingress | Complete | `ARCH-055-DATABASE-001` |
| [ARCH-055-API-003](API-003-consolidate-merchant-settings-and-category-projections.md) | Consolidate merchant settings and category projections | Complete | `ARCH-055-DATABASE-001` |
| [ARCH-055-API-004](API-004-correct-recovery-inbox-and-human-send-persistence.md) | Correct recovery inbox and human-send persistence | Complete | `ARCH-055-DATABASE-001`, `ARCH-055-BACKGROUND-001` |
| [ARCH-055-API-005](API-005-correct-knowledge-source-and-upload-lifecycle.md) | Correct knowledge-source and upload lifecycle | Complete | `ARCH-055-DATABASE-001` |
| [ARCH-055-API-006](API-006-optimise-commercial-settings-and-reporting-projections.md) | Optimise commercial settings and reporting projections | Complete | — |
| [ARCH-055-API-007](API-007-harden-durable-billing-command-admission.md) | Harden durable billing-command admission | Complete | `ARCH-055-API-001` |
| [ARCH-055-API-008](API-008-consolidate-support-inbox-persistence.md) | Consolidate Support-inbox persistence | Complete | — |
| [ARCH-055-API-009](API-009-bound-readiness-and-reconcile-api-validation.md) | Bound readiness and reconcile API validation | Complete / Accepted Attempt 2 | `ARCH-055-API-001` through `ARCH-055-API-008` |

Current frontier: all API implementation tasks are Complete. `ARCH-055-SYSTEM-TEST-001` is Ready at Attempt 0 and remains unclaimed.
