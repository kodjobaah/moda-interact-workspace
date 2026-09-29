# ARCH-021 System-Test Tasks

Architecture:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Assigned Agent:

`moda_system_test`

Coordinator:

`moda_architect`

## Pre-Phase-3 simplification checkpoint

| Task | Description | Status | Dependencies |
|---|---|---|---|
| [SYSTEM-TEST-001](SYSTEM-TEST-001-validate-simplified-studio-and-private-mcp.md) | Validate reduced configuration, dynamic Storefront schema authoring, readable Shopify documentation, unified authorization and context-only private MCP | Ready | DATABASE-002, COMMERCE-025..030, COMMERCE-032..035, BACKGROUND-001, GATEWAY-001 |

### SYSTEM-TEST-001 ready after C035 Attempt 5 — 2026-09-25

COMMERCE-035 Attempt 5 is architect-accepted Complete. Every implementation task
listed under SYSTEM-TEST-001 `depends_on` is Complete, so terminal architecture
validation is **Ready** again.

The developer may leave it Ready while manually re-checking the Shopify pages that
surfaced the latest documentation defects.

### SYSTEM-TEST-001 returned Pending after manual validation — 2026-09-25

Developer manual validation exposed remaining Shopify documentation page chrome
after C035 Attempt 3 acceptance. C035 is reopened for Attempt 4, so terminal
SYSTEM-TEST-001 returns to **Pending** until that implementation dependency is
again architect-accepted Complete.

### SYSTEM-TEST-001 ready — 2026-09-25

COMMERCE-035 Attempt 3 is architect-accepted Complete. Every implementation task
listed under SYSTEM-TEST-001 `depends_on` is now Complete, so the terminal
architecture-validation task is **Ready**.

The developer may intentionally leave it Ready while manually exercising the
completed checkpoint. Phase-3 implementation remains paused until terminal
checkpoint validation/reconciliation.

### SYSTEM-TEST-001 returned Pending — 2026-09-24

Manual validation exposed the Storefront schema-builder contract defect after
COMMERCE-029 acceptance. SYSTEM-TEST-001 is therefore Pending again and now depends
on COMMERCE-032, COMMERCE-033, COMMERCE-034 and COMMERCE-035. This preserves the invariant that
terminal system validation runs only after all required implementation corrections
are architect-accepted Complete.

## Tool creation authoring-flow refinement — 2026-09-28

| Task | Description | Status | Dependencies |
|---|---|---|---|
| [SYSTEM-TEST-002](SYSTEM-TEST-002-validate-tool-definition-template-test-review-flow.md) | Validate Create Tool -> Tool Definition -> Request -> Response -> Result Template -> Test -> Review/Save/Cancel for External + Shopify | Pending | COMMERCE-079, COMMERCE-081, COMMERCE-083 |

SYSTEM-TEST-002 is terminal validation and must remain Pending until every listed Commerce dependency is architect-accepted Complete. No Commerce implementation task depends on it.

## Phase 5 — Feature Capability simplification validation — 2026-09-29

| Task | Description | Status | Dependencies |
|---|---|---|---|
| [SYSTEM-TEST-003](SYSTEM-TEST-003-validate-feature-capability-authoring.md) | Validate local-first Capability creation, shared Feature Behaviour, immutable release snapshots and simplified runtime | Pending | DATABASE-003, SHARED-002, COMMERCE-088..092, BACKGROUND-002 |

SYSTEM-TEST-003 is terminal validation. No implementation/publication task depends on it, and the developer may leave it Pending/Ready while manually exercising the completed Feature flow.
