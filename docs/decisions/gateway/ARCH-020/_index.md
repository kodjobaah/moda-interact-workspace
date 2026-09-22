# ARCH-020 gateway tasks

Architecture: [ARCH-020-commerce-agent-studio-mcp-capabilities.md](../../../architecture/ARCH-020-commerce-agent-studio-mcp-capabilities.md).

Assigned agent: moda_gateway. Repository: moda-interact-gateway. Coordinator: moda_architect.

Definitions are on local main for review by explicit developer request. Individual task YAML is authoritative; no task is claimed or launched. Commerce submodule provisioning remains a prerequisite; the owner and route are defined in this packet.

| Task | Outcome | Status | Depends on |
|---|---|---|---|
| [ARCH-020-GATEWAY-001](GATEWAY-001-deploy-commerce-topology-through-the-render-blueprint.md) | Deploy Commerce topology through the Render Blueprint | complete (Accepted, Attempt 4) | ARCH-020-COMMERCE-002, ARCH-020-BACKGROUND-001, ARCH-020-COMMERCE-008, ARCH-020-COMMERCE-011, ARCH-020-COMMERCE-013, ARCH-020-COMMERCE-017, ARCH-020-COMMERCE-018, ARCH-020-COMMERCE-019 |
| [ARCH-020-GATEWAY-002](GATEWAY-002-add-commerce-operational-dashboards-and-alerts.md) | Add Commerce operational dashboards and alerts | superseded (developer-managed Grafana, Attempt 2) | ARCH-020-GATEWAY-001, ARCH-020-COMMERCE-010, ARCH-020-BACKGROUND-002 |
| [ARCH-020-GATEWAY-003](GATEWAY-003-configure-external-api-credential-runtime.md) | Configure external API credential runtime | ready (Changes Requested, Attempt 1) | ARCH-020-GATEWAY-001, ARCH-020-COMMERCE-020, ARCH-020-COMMERCE-021, ARCH-020-COMMERCE-026, ARCH-020-COMMERCE-028, ARCH-020-COMMERCE-029 |

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


## GATEWAY-001 Attempt 4 architect acceptance — 2026-09-22

**Accepted / Complete, Attempt 4; claim clear.** The runbook-only implementation
`478923a` closes the final A3-R1 evidence contract: valid externally supplied C5,
C15 and C9.1 bodies/identifiers, required `apiVersion=2026-07`, authenticated Studio
inputs and fail-fast guards are now documented without embedding credentials.

Architect reran the positive Blueprint validator, all 48 expected-reason negative
cases and the required shell syntax checks successfully. Attempt 4 did not change
Gateway configuration, so the accepted Attempt 3 Docker/HAProxy evidence remains
150/150 and configuration-valid.

All dependencies of GATEWAY-002 and GATEWAY-003 are now Complete. Both are promoted
to **Ready, Attempt 0, claim clear**. GATEWAY-003 retains the later C21 U15/U16
`/connections` route extension. COMMERCE-012 and system-test tasks remain gated by
additional dependencies. No task is automatically launched.

## GATEWAY-002 Attempt 1 architect review — 2026-09-22

**Changes Requested / Ready, Attempt 1; claim clear.** Implementation `6fb2ac5`
adds a useful first dashboard/alert/runbook set, but C11 is not yet satisfied.
The latest task review requires the next attempt to bind every query to the exact
accepted COMMERCE-010/BACKGROUND-002 producer inventory; replace discovery-based
"readiness"; make Grafana Cloud alert payloads actually evaluable/provisionable
without dashboard `$environment` variables; add the required MCP latency,
tool-outcome and provider-throttling views; and replace string-presence validation
with the exact boundary/low-sample/recovery/NoData matrix.

Hosted Grafana arrival/alert evidence remains developer-owned and is explicitly
required before final acceptance; the repository agent must not fabricate it.
GATEWAY-003 remains independently Ready. COMMERCE-012 and SYSTEM-TEST-001 are not
promoted.


## GATEWAY-002 superseded — 2026-09-22

The developer explicitly chose to manage Commerce custom dashboards and alerts directly
in the existing Grafana Cloud workspace. GATEWAY-002 therefore has no remaining
repository implementation deliverable and is **Superseded, Attempt 2**.

Attempts 1/2 are not accepted or merged. Existing Commerce/Background telemetry and the
GATEWAY-001 OTLP/Loki/environment wiring remain authoritative. COMMERCE-012 and
SYSTEM-TEST-001 no longer depend on GATEWAY-002; both retain other incomplete gates.


## GATEWAY-003 Attempt 1 architect review — 2026-09-22

**Changes Requested / Ready, Attempt 1; claim clear.** Implementation `844043f`
correctly scopes the three Commerce-only connection settings and U15/U16 Gateway
routing, and the architect independently reproduced the static/config validators.

Attempt 2 is bounded to four remaining items: run the local Docker/HAProxy route suite
(which is agent-owned local validation under the current policy); close C21 §7's
accepted QuickJS package/deployment and per-replica memory-capacity evidence without
editing Commerce runtime source; state explicitly that command-HMAC rotation requires
a replay-strategy migration rather than an env-only rotation; and reconcile task/VCS
checklists.

GATEWAY-002 remains Superseded. COMMERCE-012 and SYSTEM-TEST-002 remain Pending.
