# ARCH-023 background tasks

Architecture: [`ARCH-023`](../../../architecture/ARCH-023-merchant-knowledge.md).

Assigned agent: `moda_background`.

Repository: `moda-interact-background`.

Coordinator: `moda_architect`.

The current Background decomposition follows runtime/security boundaries rather than file count:

```text
ARCH-023-DATABASE-001 + ARCH-023-SHARED-002
                 |
                 v
          BACKGROUND-001
      worker/entitlement/repair
          /           \
         v             v
BACKGROUND-002     BACKGROUND-003
WEB_PAGE           R2 + CSV/XLSX
acquisition        acquisition/cleanup
         \             /
          \           /
           v         v
          BACKGROUND-004
      normalize/chunk/embed/
       promote + final entrypoint
                 |
                 v
          BACKGROUND-005
       entitlement reconciliation
                 |
                 v
        planned GATEWAY-001
```

Individual task YAML is authoritative.

| Task | Outcome | Status | Depends on |
|---|---|---|---|
| [BACKGROUND-001](BACKGROUND-001-establish-merchant-knowledge-worker-foundation.md) | Dedicated worker foundation, current entitlement and durable PENDING reconciliation | Ready — Changes Requested (Attempt 3; next claim Attempt 4) | DATABASE-001, SHARED-002 |
| [BACKGROUND-002](BACKGROUND-002-acquire-merchant-knowledge-web-pages.md) | SSRF-safe WEB_PAGE acquisition and extraction | Pending | BACKGROUND-001 |
| [BACKGROUND-003](BACKGROUND-003-acquire-merchant-knowledge-uploads.md) | Private R2 CSV/XLSX acquisition/extraction and safe asset cleanup | Pending | BACKGROUND-001 |
| [BACKGROUND-004](BACKGROUND-004-process-and-promote-merchant-knowledge-revisions.md) | Common normalization/chunk/embed/promote pipeline and final dedicated entrypoint | Pending | BACKGROUND-002, BACKGROUND-003 |
| [BACKGROUND-005](BACKGROUND-005-reconcile-merchant-knowledge-entitlements.md) | Non-destructive plan entitlement/content-limit reconciliation | Pending | BACKGROUND-004 |

## Execution frontier

DATABASE-001 and SHARED-002 are Complete/architect-accepted, so:

```text
BACKGROUND-001 -> Ready — Changes Requested (Attempt 3; next claim Attempt 4)
```

BACKGROUND-001 remains on exact `@modainteract/moda-interact-shared@1.0.1`. Attempt 3
resolved the Shared C4 schema-version and execution-provenance corrections. Architect acceptance
is now withheld only for the required queue-loss integration proof. Attempt 4 is authorised to
provision its own task-local disposable pgvector-capable PostgreSQL Docker container, apply the
real migrations, run the existing integration test, and tear the container down; no shared helper
or permanent integration-harness change is required.

BACKGROUND-002 and BACKGROUND-003 remain Pending. After BACKGROUND-001 is accepted Complete:

```text
BACKGROUND-002 and BACKGROUND-003 -> Ready in parallel
```

After both are Complete:

```text
BACKGROUND-004 -> Ready
```

After BACKGROUND-004:

```text
BACKGROUND-005 -> Ready
```

Gateway deployment must not begin before BACKGROUND-005 is Complete/architect-accepted.
