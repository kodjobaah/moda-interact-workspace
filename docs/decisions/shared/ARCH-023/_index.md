# ARCH-023 shared tasks

Architecture: [`ARCH-023`](../../../architecture/ARCH-023-merchant-knowledge.md).

Assigned agent: `moda_shared`.

Repository: `moda-interact-shared`.

Coordinator: `moda_architect`.

The current Shared design deliberately has exactly two executable tasks:

```text
ARCH-023-DATABASE-001
        |
        v
ARCH-023-SHARED-001
    implement all C1-C4 contracts
    + Commerce runner trust change
        |
        v
ARCH-023-SHARED-002
    publish exact accepted package revision
```

Individual task YAML is authoritative.

| Task | Outcome | Status | Dependencies |
|---|---|---|---|
| [SHARED-001](SHARED-001-implement-arch023-shared-contracts.md) | Implement all ARCH-023 Shared contracts and Commerce runner trust | Ready | DATABASE-001 |
| [SHARED-002](SHARED-002-publish-arch023-shared-package.md) | Publish the accepted Shared package as one patch release | Pending | SHARED-001 |
| [SHARED-003](SHARED-003-harden-commerce-runner-instruction-trust.md) | Historical split task; folded into SHARED-001 | Superseded | — |
| [SHARED-004](SHARED-004-publish-arch023-shared-contracts.md) | Historical publication task; replaced by SHARED-002 | Superseded | — |

## Execution frontier

`ARCH-023-DATABASE-001` is Complete/accepted, so:

```text
SHARED-001 -> Ready
```

Only after SHARED-001 is Complete/accepted:

```text
SHARED-002 -> Ready
```

Consumer repositories must wait for the exact published revision from SHARED-002.
