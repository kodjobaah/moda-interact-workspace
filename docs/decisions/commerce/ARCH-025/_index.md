# ARCH-025 Commerce Tasks

Architecture: `docs/architecture/ARCH-025-shopify-billing-service-maintainability.md`

Assigned Agent: `moda_commerce`

Coordinator: `moda_architect`

This is an independent Commerce maintainability chain for `components/studio-workspace.tsx`. It does not depend on the Shopify, Background or Admin ARCH-025 chains. Tasks are sequential internally because every later extraction consumes the accepted workspace controller/module contracts established by earlier tasks.

Reviewed baseline:

```text
components/studio-workspace.tsx
937 lines
SHA-256: 62c5720bf07144c6cbc61ff35398dc749450feb9f500b919cf842809f8622afb
```

Frozen integration/state assets throughout COMMERCE-001..005:

```text
tests/studio-workspace.test.tsx
  13 tests
  SHA-256 400ce6b68cb5a9fdeecf9233bc2b3f58a42742c974da2c5b6ffd2b5a16ae44a7
tests/agent-configuration-screen-state.test.tsx
  3 tests
  SHA-256 72c71a09eaf5bdc2d79c686cf5ec43d5abfd49cfe421cadedbbe665140582b0a
tests/external-tools-ui.test.tsx
  90 tests
  SHA-256 97ffbc70e29d4ff60a48e5aabd0ff3faec6dea7984ed0f239fcb4a8fc868f4d3
```

COMMERCE-001 alone may change source-loading mechanics in `legacy-capability-surface.test.ts` and `arch024-preview-cleanup.test.ts` without weakening their assertions. COMMERCE-002..005 must not modify the accepted COMMERCE-001 versions.

| Task | Outcome | Status | Dependencies |
|---|---|---|---|
| [COMMERCE-001](COMMERCE-001-extract-studio-workspace-controller.md) | Workspace controller + extraction-safe source assertions | Ready | - |
| [COMMERCE-002](COMMERCE-002-extract-release-composer.md) | Immutable Release Composer | Pending | COMMERCE-001 |
| [COMMERCE-003](COMMERCE-003-extract-release-detail.md) | Release Detail clone/activation/rollback | Pending | COMMERCE-002 |
| [COMMERCE-004](COMMERCE-004-extract-shop-views.md) | Shop list + Shop Inspector | Pending | COMMERCE-003 |
| [COMMERCE-005](COMMERCE-005-reduce-studio-workspace-shell.md) | Generic page/detail routing + final thin shell | Pending | COMMERCE-004 |

## Execution frontier

`ARCH-025-COMMERCE-001` is Ready independently of `ARCH-025-BACKGROUND-001`, `ARCH-025-BACKGROUND-008`, `ARCH-025-ADMIN-001` and `ARCH-025-ADMIN-009`. COMMERCE-002..005 remain Pending until the immediately preceding Commerce task is architect-accepted Complete.
