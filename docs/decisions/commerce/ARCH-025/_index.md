# ARCH-025 Commerce Tasks

Architecture: `docs/architecture/ARCH-025-shopify-billing-service-maintainability.md`

Assigned Agent: `moda_commerce`

Coordinator: `moda_architect`

ARCH-025 Commerce now contains two staged UI maintainability chains. COMMERCE-001..005 refactor `components/studio-workspace.tsx`. COMMERCE-006..010 refactor `src/studio/tools/tool-editor.tsx`. The ToolEditor chain is deliberately gated behind COMMERCE-005 because COMMERCE-001..005 freeze `tests/external-tools-ui.test.tsx`, while COMMERCE-006 owns one controlled source-loader change in that same regression asset. This is a test-baseline coordination dependency, not a runtime dependency.

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
| [COMMERCE-001](COMMERCE-001-extract-studio-workspace-controller.md) | Workspace controller + extraction-safe source assertions | Complete | ARCH-024-COMMERCE-003 (Complete) |
| [COMMERCE-002](COMMERCE-002-extract-release-composer.md) | Immutable Release Composer | Complete | COMMERCE-001 (Complete) |
| [COMMERCE-003](COMMERCE-003-extract-release-detail.md) | Release Detail clone/activation/rollback | Complete | COMMERCE-002 (Complete) |
| [COMMERCE-004](COMMERCE-004-extract-shop-views.md) | Shop list + Shop Inspector | Complete | COMMERCE-003 (Complete) |
| [COMMERCE-005](COMMERCE-005-reduce-studio-workspace-shell.md) | Generic page/detail routing + final thin shell | Complete | COMMERCE-004 (Complete) |

## Execution frontier

`ARCH-025-COMMERCE-001` is Complete / Accepted at Attempt 2 and establishes durable Commerce baseline `ARCH025-COMMERCE-TEST-001`. `ARCH-025-COMMERCE-002` is Complete / Accepted at Attempt 1. `ARCH-025-COMMERCE-003` is Complete / Accepted at Attempt 2. `ARCH-025-COMMERCE-004` is Complete / Accepted at Attempt 3 after closing the production-build reproducibility gate without code-runtime or dependency changes. `ARCH-025-COMMERCE-005` is Complete / Accepted at Attempt 1; the StudioWorkspace tranche is complete. `ARCH-025-COMMERCE-006` is Complete / Accepted at Attempt 2 after exact full-suite baseline classification and an evidence-only retry. `ARCH-025-COMMERCE-007` is Complete / Accepted at Attempt 2 after the evidence-only physical-isolation reconciliation. `ARCH-025-COMMERCE-008` is Complete / Accepted at Attempt 2 after report-only full-suite classification and a green production-build rerun. `ARCH-025-COMMERCE-009` is Complete / Accepted at Attempt 1; `ARCH-025-COMMERCE-010` is now Ready and is the final persisted ToolEditor execution frontier. These Commerce chains remain independently executable from the Background and Admin tranches.


## ToolEditor persisted-authoring tranche

Reviewed baseline:

```text
src/studio/tools/tool-editor.tsx
916 lines
SHA-256: c91ff89cb47d5e9afd50dec2b0aeb24e59c57dfc37e2013e6511f87d15be54fa
```

Frozen throughout COMMERCE-006..010:

```text
tests/shopify-admin-tools-ui.test.tsx
  SHA-256 d856cac3626605670e08a21826cfcc1a8e6595dcffc764e20d9ef59c2ff78446
tests/tool-authoring-screen.test.tsx
  SHA-256 2245e54996589f7289639bb28c6b364f1726ec291debec390e208a5c304b6c20
tests/new-tool-authoring-state.test.ts
  SHA-256 267352261520b38eaa9845f93dc09eb8860e75a4010d9da26827c6617bcdcf63
```

`tests/external-tools-ui.test.tsx` starts at SHA-256 `97ffbc70e29d4ff60a48e5aabd0ff3faec6dea7984ed0f239fcb4a8fc868f4d3`. COMMERCE-006 may change only its bounded source-loader for the existing persisted-External uniqueness assertion; COMMERCE-007..010 must keep the accepted COMMERCE-006 version unchanged.

Supplementary behaviour/follow-up register: `docs/architecture/ARCH-025-tool-editor-refactor-observations.md`.

| Task | Outcome | Status | Dependencies |
|---|---|---|---|
| [COMMERCE-006](COMMERCE-006-extract-persisted-tool-authoring-controller.md) | Persisted Tool authoring controller + extraction-safe External source assertion | Complete | COMMERCE-005 (Complete) |
| [COMMERCE-007](COMMERCE-007-extract-policy-operation-persisted-editor.md) | Persisted Policy Operation wrapper | Complete | COMMERCE-006 (Complete) |
| [COMMERCE-008](COMMERCE-008-extract-external-http-persisted-editor.md) | Persisted External HTTP wrapper | Complete | COMMERCE-007 (Complete) |
| [COMMERCE-009](COMMERCE-009-extract-shopify-admin-persisted-editor.md) | Persisted Shopify Admin wrapper | Complete | COMMERCE-008 (Complete) |
| [COMMERCE-010](COMMERCE-010-reduce-tool-editor-shell.md) | Revision/read-only/generic extraction + thin ToolEditor dispatch | Ready | COMMERCE-009 (Complete) |
