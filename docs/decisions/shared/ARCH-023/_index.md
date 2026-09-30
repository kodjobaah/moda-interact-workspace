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
| [SHARED-001](SHARED-001-implement-arch023-shared-contracts.md) | Implement all ARCH-023 Shared contracts and Commerce runner trust | Complete | DATABASE-001 |
| [SHARED-002](SHARED-002-publish-arch023-shared-package.md) | Publish the accepted Shared package as one patch release | Complete | SHARED-001 |
| [SHARED-003](SHARED-003-harden-commerce-runner-instruction-trust.md) | Historical split task; folded into SHARED-001 | Superseded | — |
| [SHARED-004](SHARED-004-publish-arch023-shared-contracts.md) | Historical publication task; replaced by SHARED-002 | Superseded | — |

## Execution frontier

Shared implementation and publication are now complete:

```text
SHARED-001 -> Complete / Accepted Attempt 2
SHARED-002 -> Complete / Accepted Attempt 1
```

Canonical ARCH-023 Shared release:

```text
@modainteract/moda-interact-shared@1.0.1
integrity: sha512-xwVRw1rZWZIlfvrnml+psA5roRz+qMoTl7Znob1myNA1PTXIuHYX4lQHCof8Ef2F1QElrvi09jKstOc6QHdcKg==
```

Consumer tasks must use that exact revision unless `moda_architect` explicitly reconciles a later ARCH-023 Shared release.
