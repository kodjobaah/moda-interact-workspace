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
| [SYSTEM-TEST-002](SYSTEM-TEST-002-validate-tool-definition-template-test-review-flow.md) | Validate Create Tool -> Tool Definition -> Request -> Response -> Result Template -> Test -> Review/Save/Cancel for External + Shopify, including persisted traversal parity | Pending | COMMERCE-079, COMMERCE-081, COMMERCE-083, COMMERCE-095, COMMERCE-102, COMMERCE-103 |

SYSTEM-TEST-002 is terminal validation. At the original C095 checkpoint every then-listed Commerce dependency was architect-accepted Complete and the task became Ready. Later manual-validation corrections C102/C103 re-gate it to Pending. No Commerce implementation task depends on it.

### SYSTEM-TEST-002 re-gated for progressive new-Tool navigation — 2026-09-29

COMMERCE-095 now owns the final progressive Previous/Next and monotonic unlock
behaviour exercised by this integrated Tool-authoring scenario. SYSTEM-TEST-002
therefore also depends on COMMERCE-095 and remains Pending until C095 is
architect-accepted Complete.

### SYSTEM-TEST-002 ready after C095 Attempt 2 — 2026-09-29

COMMERCE-079, COMMERCE-081, COMMERCE-083 and COMMERCE-095 are all
architect-accepted Complete. SYSTEM-TEST-002 is therefore **Ready** as terminal
integrated validation. It is not started by this promotion; the developer may
leave it Ready while manually exercising the completed Tool-authoring flow.

## Phase 5 — Feature Capability simplification validation — 2026-09-29

| Task | Description | Status | Dependencies |
|---|---|---|---|
| [SYSTEM-TEST-003](SYSTEM-TEST-003-validate-feature-capability-authoring.md) | Validate local-first Capability creation, direct ready-phase navigation, shared Feature Behaviour, immutable release snapshots and simplified runtime | Ready | DATABASE-003, SHARED-002, COMMERCE-088..092, COMMERCE-104, BACKGROUND-002 |

SYSTEM-TEST-003 is terminal validation. COMMERCE-104 is now architect-accepted Complete and every declared implementation dependency is Complete, so SYSTEM-TEST-003 is **Ready**. No implementation/publication task depends on it; the developer may leave it Ready while manually validating the completed implementation.

### SYSTEM-TEST-002 re-gated for Tool execution safety — 2026-09-29

Manual validation exposed the COMMERCE-102 selected-shop execution-target and Tool-authoring single-flight correction. SYSTEM-TEST-002 became **Pending** on C102.

### SYSTEM-TEST-002 re-gated for persisted Tool traversal — 2026-09-29

Manual validation of an existing Tool then exposed COMMERCE-103: persisted External HTTP, Shopify Admin and Policy Operation DRAFTs need the same six-step sequential `Previous`/`Next` navigation while retaining permanently unlocked direct tabs. SYSTEM-TEST-002 is therefore **Pending** on both C102 and C103 and returns to Ready only after both are architect-accepted Complete. It remains terminal validation; no Commerce implementation task depends on it.

### SYSTEM-TEST-003 re-gated for Add Capability direct phase readiness — 2026-09-29

Manual validation exposed COMMERCE-104: Tool and Review must become directly clickable as soon as their current first-entry predicates are satisfied, without requiring `Next`, while the existing monotonic unlock frontier and current-candidate Create gate remain intact.

COMMERCE-104 Attempt 1 is now architect-accepted Complete. Every SYSTEM-TEST-003 dependency is Complete, so terminal Feature/Capability validation is **Ready**.
