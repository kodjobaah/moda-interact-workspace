# ARCH-019 database tasks

Architecture: [ARCH-019](../../../architecture/ARCH-019-merchant-recovery-experience.md).

Coordinator: moda_architect. Individual task YAML and canonical task worktrees are authoritative.

| Task | Outcome | Status | Dependencies |
|---|---|---|---|
| [ARCH-019-DATABASE-001](DATABASE-001-index-merchant-recovery-read-paths.md) | Index tenant-scoped recovery browsing and transcript pagination | Complete | None |

DATABASE-001 accepted/Complete at `54c0ec2` after the authorized PostgreSQL 15.19 rehearsal. SHOPIFY-001/002 are Ready; all remaining tasks are Pending. System tests remain terminal and developer-invoked.
