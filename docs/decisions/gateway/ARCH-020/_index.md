# ARCH-020 gateway tasks

Architecture: [ARCH-020-commerce-agent-studio-mcp-capabilities.md](../../../architecture/ARCH-020-commerce-agent-studio-mcp-capabilities.md).

Assigned agent: moda_gateway. Repository: moda-interact-gateway. Coordinator: moda_architect.

Definitions are on local main for review by explicit developer request. Individual task YAML is authoritative; no task is claimed or launched. Commerce submodule provisioning remains a prerequisite; the owner and route are defined in this packet.

| Task | Outcome | Status | Depends on |
|---|---|---|---|
| [ARCH-020-GATEWAY-001](GATEWAY-001-deploy-commerce-topology-through-the-render-blueprint.md) | Deploy Commerce topology through the Render Blueprint | ready (Changes Requested, Attempt 3) | ARCH-020-COMMERCE-002, ARCH-020-BACKGROUND-001, ARCH-020-COMMERCE-008, ARCH-020-COMMERCE-011, ARCH-020-COMMERCE-013, ARCH-020-COMMERCE-017, ARCH-020-COMMERCE-018, ARCH-020-COMMERCE-019 |
| [ARCH-020-GATEWAY-002](GATEWAY-002-add-commerce-operational-dashboards-and-alerts.md) | Add Commerce operational dashboards and alerts | pending | ARCH-020-GATEWAY-001, ARCH-020-COMMERCE-010, ARCH-020-BACKGROUND-002 |
| [ARCH-020-GATEWAY-003](GATEWAY-003-configure-external-api-credential-runtime.md) | Configure external API credential runtime | pending | ARCH-020-GATEWAY-001, ARCH-020-COMMERCE-020, ARCH-020-COMMERCE-021, ARCH-020-COMMERCE-026, ARCH-020-COMMERCE-028, ARCH-020-COMMERCE-029 |

## ARCH-020-GATEWAY-001 readiness — 2026-09-22

`ARCH-020-COMMERCE-018` is now Accepted / Complete at Attempt 8. All declared
GATEWAY-001 prerequisites are Complete in this snapshot, so GATEWAY-001 is promoted
to **Ready, Attempt 0, claim clear**. Readiness does not launch or claim the task.

## GATEWAY-001 Attempt 1 architect review — 2026-09-22

**Changes Requested / Ready, Attempt 1 retained; claim clear.** Implementation
`9dbc61c` establishes the Commerce private service and initial Gateway/Blueprint
wiring, but C5/C7.1/C9.1/C10/C15 is not yet deployable. The latest task review is the
complete deterministic Attempt 2 correction contract: actual Render private MCP input
and supported secret declarations; exact C15/discovery/C9.1/NextAuth/Server-Action
routing; Commerce 128 KiB / 100-second bounds; meaningful Blueprint negative
validation; and exact developer deployment/smoke commands.

No dependent task is promoted. GATEWAY-002, GATEWAY-003, COMMERCE-012 and
SYSTEM-TEST-001 remain gated.

## GATEWAY-001 Attempt 2 architect review — 2026-09-22

**Changes Requested / Ready, Attempt 2 retained; claim clear.** Implementation
`12ca000` closes the main Attempt 1 proxy/Blueprint defects: private MCP is now a
manual service-level input, route/method coverage is explicit, Commerce has its
131072-byte/100-second bounds and the Blueprint negative matrix is meaningful.

Two bounded GATEWAY-001 corrections remain: the Commerce public Studio hostname is
still hard-coded in the Blueprint despite being classified as a deployment input, and
the hosted smoke commands must use the real Studio auth boundary/correct Auth.js
callback path plus separate wrong-claim assertions.

C21 U15/U16 `/connections` route exposure is assigned to pending GATEWAY-003 as a
bounded downstream route delta rather than silently left unowned. No downstream task
is promoted or launched.

## GATEWAY-001 Attempt 3 architect review — 2026-09-22

**Changes Requested / Ready, Attempt 3; claim clear.** Implementation `7bd5865`
closes the Blueprint/proxy corrections from Attempt 2: Commerce public host/origin/Auth
URL are deployment inputs, no Commerce custom domain is committed, authenticated
Studio/Auth.js routing is corrected, and the positive/48-case negative validators pass.
The submitted Docker gateway suite remains 150/150.

One documentation/evidence correction remains. The hosted smoke block authenticates
requests but still sends invalid `{}` bodies to strict C5/C9.1/C15 operations, omits
C15's required `apiVersion=2026-07`, and uses literal preview ID placeholders. Attempt 4
must use externally supplied valid MCP/discovery/preview bodies and concrete matching
UUIDs. No Blueprint/HAProxy redesign is requested.

GATEWAY-002/GATEWAY-003 and later Commerce/system-test work remain gated. No task is
started automatically.
