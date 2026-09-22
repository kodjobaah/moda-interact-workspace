---
id: ARCH-020-GATEWAY-002
architecture_id: ARCH-020
title: Add Commerce operational dashboards and alerts
task_kind: implementation
domain: gateway
repository: moda-interact-gateway
assigned_agent: moda_gateway
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 190
executor: null
claimed_at: null
attempt: 2
depends_on:
  - ARCH-020-GATEWAY-001
  - ARCH-020-COMMERCE-010
  - ARCH-020-BACKGROUND-002
enables:
  - ARCH-020-COMMERCE-012
  - ARCH-020-SYSTEM-TEST-001
created: 2026-09-20
updated: 2026-09-22
---

# Add Commerce operational dashboards and alerts

## Architecture

Architecture ID: ARCH-020.

Architecture document: docs/architecture/ARCH-020-commerce-agent-studio-mcp-capabilities.md.

Coordinator: moda_architect. Read the complete parent architecture and relevant dependency/contract tasks. Execution handoff: docs/architecture/ARCH-020-implementation-handoff.md.

## Objective

Expose actionable Commerce/MCP health using existing observability infrastructure.

## Context

Merchant-selected capabilities should drive WhatsApp CommerceAgent behaviour through a separate Next.js MCP server with a team-only Studio. Production conversation admission, ordering, model hosting and delivery remain in Background. This is a pre-production breaking rollout, with no implicit permission to delete durable data.

Task definition is on local workspace main by the developer's explicit 2026-09-20 review request. It is not a claim, task-branch materialisation or implementation approval. All execution fields remain unclaimed.

## Scope

Gateway-owned dashboard/alert/OTLP configuration and operational runbook.

## Out of Scope

Other repositories' implementation, unrelated refactoring, automatic execution of enabled tasks, live deployment, main integration/push and changes to billing prices/merchant entitlements. No cart/order/discount mutation, WhatsApp sending from Commerce, arbitrary executable code or arbitrary-host HTTP endpoints; C14 validated read-only GraphQL definitions are explicitly permitted. No duplicate discount catalogue/merchant configuration system. Shared indexes and architecture reconciliation remain architect-owned.

## Requirements

Follow the parent architecture's tenant/policy/revision contracts and the assigned logical owner. Preserve unrelated changes. Read repository-local AGENTS.md if present. Commerce consumes the canonical database through its nested database/ Git submodule; schema and migrations belong to moda_database. For consumers, use actual accepted and published dependency revisions, not copied task snapshots or hypothetical versions.

## Work Items

- [x] Use accepted signal inventory to add MCP error/latency, eligibility outcomes, provider throttling and conversation-lag views.
- [x] Enforce explicit environment and production-versus-preview filters; avoid duplicating framework metrics.
- [x] Configure actionable alerts for service unavailability, queue lag and systematic evidence/permission failures with documented thresholds.
- [x] Document triage for release rollback, capability disable, provider failure and preview cost without secret/customer exposure.

## Interfaces / Contracts

COMMERCE-010/Background semantic signals plus existing HTTP/client/runtime instrumentation.

### Implementation guidance

Binding companion: [ARCH-020 implementation contracts](../../../architecture/ARCH-020-implementation-contracts.md), sections **C11**. These are required acceptance inputs, not optional examples.

Deliver version-controlled dashboards/alerts using the accepted actual signal inventory and C11 initial numeric thresholds/sample floors. Include no-data state and production/preview/environment filters. Add runbook steps for unavailable service, permission denials, unknown routing sends and evidence failures.

### Deterministic review clarification

Use the accepted COMMERCE-010 inventory and exact C11 outcome denominators.
Evaluate rolling windows once per minute, separately by service/environment and
purpose=live. Threshold comparisons are strictly greater than the stated value;
minimum sample counts are inclusive. Readiness requires consecutive failures for
2 minutes; oldest pending age must exceed120 seconds continuously for5 minutes.
No samples render No data and do not trigger a failure-rate alert. Test boundary
values, low samples, recovery, preview exclusion and missing telemetry separately;
missing telemetry is observable, not fabricated success or a business failure.

### Required evidence

Static fixtures validate each query references emitted names/units and each alert excludes preview with correct sample floor/duration. Required deployed arrival/alert evidence is recorded by the developer; do not claim config syntax proves live arrival.

For this task, record a requirement-to-fixture matrix with expected side effects, actual commands and results in the Completion Report. Do not implement another repository's changes to bypass a dependency.

## Dependencies

- ARCH-020-GATEWAY-001
- ARCH-020-COMMERCE-010
- ARCH-020-BACKGROUND-002

Every dependency must be Complete and architect-accepted before execution. Reconcile accepted dependency metadata into the matching parent task branch before promotion. Developer integration or explicitly approved accepted-commit consumption is required to obtain prerequisite source. Readiness never launches a task. Commerce tasks additionally require the new-owner setup checkpoint.

## Enables

- ARCH-020-COMMERCE-012

- ARCH-020-SYSTEM-TEST-001

## Acceptance Criteria

- [x] Operational views correlate service and worker effects and cannot mistake preview/test traffic for production.
- [x] Observability requirements are version-controlled and no undocumented manual backend configuration is necessary.
- [x] Alert thresholds distinguish assumed initial values from measured capacity evidence.

## Validation

- [x] Run local dashboard/query/config validation with fixture signal names and environment filters.
- [x] Provide developer-owned backend validation instructions; acceptance requires recorded evidence for required hosted signals/alerts.

Use package.json commands actually provided by the repository. New Commerce scripts and test fixtures are deliverables, not claims that they exist today. Follow docs/agent-validation-execution-policy.md and docs/agent-live-validation-execution-policy.md. Separate local evidence from pending developer-owned long/live validation; required evidence must exist before acceptance.

## Stop Condition

After scoped work and agent-owned checks, update this task's execution/report fields, publish task-owned mirrored branches and return to review. Record exact pending developer validation where applicable. Stop; do not begin enabled tasks or mark your own task Complete. Publication tasks stop after release mechanics. System tests require explicit developer invocation even after becoming Ready.

## Implementation Notes

Normal execution uses /moda-task and scripts/start-agent-task.py preparation, dedicated parent and implementation worktrees, synchronization and recursive submodule initialisation. Follow docs/agent-vcs-ownership-policy.md, docs/agent-worktree-isolation-policy.md and docs/task-definition-materialization.md. The main-only exception applies to this review draft, not task execution. The COMMERCE route is registered in this packet; its real repository must be provisioned before execution preparation.

## Completion Report

### Status

Ready for Review. Attempt 2 implementation is complete and locally validated. The
hosted Grafana arrival/evaluation gate remains developer-owned.

### Files Changed

- `dashboards/commerce-operational.json`
- `alerts/commerce-operational.yaml`
- `docs/commerce-operational-runbook.md`
- `tests/fixtures/commerce-operational-signals.json`
- `tests/validate-commerce-observability.sh`
- `scripts/render-commerce-alerts.sh`

### Work Completed

Attempt 2 consumes the accepted dependency pins `e8b43e4604780754ba64b0653c7d6e029d58e3c3`
(ARCH-020-COMMERCE-010), `8b2f9835dcd98b5385a64fa873598b8379b2986d`
(ARCH-020-BACKGROUND-002), and `478923a` (ARCH-020-GATEWAY-001). The accepted
producer/export evidence used by the artifacts is:

- Commerce `commerce.mcp.request`, `commerce.definition.outcome`,
  `commerce.eligibility.outcome`, and `commerce.preview.outcome` semantic
  outcomes, with `purpose=live` or `purpose=preview` bounded dimensions.
- Existing framework metrics `http_server_request_duration_seconds_bucket` and
  `http_server_response_status_code_total` for MCP latency and request/error
  views, avoiding a duplicate HTTP metric.
- Commerce `/health/ready` through the existing `probe_success` readiness probe.
- Background `moda.background.queue.oldest_waiting_age_ms` for oldest pending
  queue age, in milliseconds.
- Background OpenTelemetry counter
  `moda.background.commerce.evidence.refresh`, with bounded
  `moda.commerce.evidence.outcome` values for evidence-refresh outcomes.

The dashboard now has ten panels covering MCP errors and latency, tool outcomes,
eligibility, provider throttling, queue lag, preview isolation/cost and evidence
refresh. Alert source queries have explicit Loki/Prometheus datasource bindings;
Grafana expressions use datasource `-100`; rules are rendered into independent
test and production instances without dashboard variables. The runbook documents
the Grafana Cloud HTTP API import boundary and triage for readiness, permission
and provider failures, queue lag, evidence failures, rollback, capability
disablement and preview isolation without secrets or customer data.

### Validation Results

| Requirement | Fixture / command | Expected side effect | Result |
| --- | --- | --- | --- |
| Accepted producer inventory and units | `tests/fixtures/commerce-operational-signals.json`; validator | Exact Commerce semantic names, framework latency/error metrics, readiness probe, Background queue-age/evidence exports; queue age is milliseconds | PASS |
| Grafana Cloud rendering boundary | `scripts/render-commerce-alerts.sh`; validator with synthetic datasource UIDs | Eight explicit test/production rules, no unresolved placeholders, every query has a datasource binding, expressions use `-100`, no `$environment` | PASS |
| Required operational views and isolation | `dashboards/commerce-operational.json`; validator | Ten panels include MCP errors/latency, tool outcomes, eligibility, throttling, queue lag, preview and evidence refresh; test/production selector and live/preview separation | PASS |
| Readiness semantics | readiness fixture and alert rule; validator | `/health/ready` `probe_success`, first failure pending, two-minute continuous failure firing, recovery resolved, missing telemetry NoData | PASS |
| MCP denominator and threshold | boundary fixture; validator | `F / A > 0.05`, inclusive `A >= 20`; `A=20,F=1` not firing, `A=20,F=2` firing, `A=19` not firing; denied/permission outcomes excluded; preview excluded | PASS |
| Queue lag threshold and duration | boundary fixture and alert rule; validator | `120s` not firing; `121s` for 5 minutes firing; recovery and absent series are covered as resolved/NoData | PASS |
| Evidence failure threshold and ownership | boundary fixture, alert rule and runbook; validator | `F / A > 0.10`, inclusive `A >= 20`; `A=20,F=2` not firing, `A=20,F=3` firing, `A=19` not firing, missing/non-live excluded | PASS locally; hosted Background arrival pending |
| Configuration syntax and hygiene | `bash tests/validate-commerce-observability.sh`; `bash -n tests/validate-commerce-observability.sh`; `git diff --check`; JSON/YAML parsing in validator | Configuration, fixture, rendered payload and whitespace checks pass | PASS |

Exact local result from the implementation worktree: `bash
tests/validate-commerce-observability.sh` exited 0 and printed
`commerce observability configuration validation passed`. The validator itself
ran `jq`, Python fixture/payload checks, rendered with
`LOKI_DATASOURCE_UID=synthetic-loki PROMETHEUS_DATASOURCE_UID=synthetic-prometheus`,
and verified eight rendered rules. `bash -n tests/validate-commerce-observability.sh`
passed; the validator's JSON/YAML parsing checks passed; and `git diff --check`
passed. The implementation worktree was clean at the pushed commit.

### Deviations

No scope deviation. The evidence-refresh signal remains Background-002-owned;
the gateway uses its accepted OpenTelemetry export and does not substitute
Commerce eligibility outcomes. Grafana Cloud credentials and datasource UIDs
remain external inputs.

### Assumptions

The deployed Grafana data sources and service/resource label mapping are supplied
by the developer's environment. The version-controlled alert manifest is rendered
with externally supplied Loki/Prometheus datasource UIDs and imported through the
Grafana Cloud HTTP API; no backend credentials are committed.

### Unresolved Issues

Developer-owned hosted validation remains: provision/import the rendered dashboard
and alerts in the approved test Grafana environment; verify dashboard/import
success; capture one live Commerce event, one preview event, one queue-age metric
and the Background evidence-refresh signal; exercise alert boundaries/recovery;
confirm production/live alerts exclude preview; and verify intentional NoData
behaviour. No live deployment, backend provisioning, provider call or hosted alert
evaluation was performed by this agent. Expected success is recorded hosted
arrival and alert-evaluation evidence for each item, with no production mutation.

### Architectural Concerns

The evidence-refresh alert remains NoData until the accepted Background terminal
signal arrives in the hosted environment. This is an explicit cross-repo handoff,
not an implementation of Background behavior.

### Git / VCS

Expected execution branch: `task/ARCH-020-GATEWAY-002`. Attempt: 2. The exact
Attempt 2 implementation commit is `8bae447826333c291720519168dd28cdacc3de4b`.
The implementation worktree is clean and pushed. The exact Attempt 2 parent report
commit is `7b54065a`. The final metadata-only report correction follows in the
parent branch history. The
parent worktree is dedicated and clean before this report edit; the parent report
branch will be pushed to `origin/task/ARCH-020-GATEWAY-002`. No main integration,
parent service gitlink update, live deployment or enabled-task launch is performed.

## Architect Review

### Review Status

Changes Requested — Attempt 1.

### Review Notes

No implementation submitted. This task is a reviewable definition.

### Reviewed Files

None for implementation review.

### Validation Reviewed

None for implementation review.

### Architecture Conformance

Awaiting implementation.

### Follow-up

Reconcile task/index/frontier after review; preserve the terminal/manual system-test gate.

### Attempt 1 — Changes Requested (2026-09-22)

Reviewed by `moda_architect` against the exact submitted Attempt 1 archive.
Submitted implementation evidence: `6fb2ac5`; parent report evidence:
`ccf6ecbc`.

The implementation is directionally useful and should be preserved:

- dashboard/environment controls exist;
- live versus preview intent is visible;
- queue age is converted from milliseconds to seconds;
- strict C11 numeric thresholds/sample floors appear in the rule source;
- NoData states are explicit;
- the runbook covers service/provider/queue/evidence/rollback/capability-disable and
  preview-isolation triage without embedding secrets;
- `tests/validate-commerce-observability.sh`, shell syntax, dashboard JSON parsing and
  alert YAML parsing pass locally.

Attempt 1 is **not accepted** because the submitted artifacts are not yet tied to the
accepted producer inventory or to an actually evaluable Grafana Cloud alert model.
The following items are the complete Attempt 2 correction contract.

#### A1-R1 — consume the accepted producer inventory exactly; do not invent signal names

**Gateway source/tests/report changes required.**

The task contract requires GATEWAY-002 to use the actual accepted COMMERCE-010 and
BACKGROUND-002 inventory. The current fixture instead declares, among other values:

```text
commerce.discovery.outcome
commerce.mcp.request
commerce.eligibility.outcome
commerce.preview.outcome
background.commerce.evidence_refresh.outcome
```

and marks the Background refresh event as:

```text
status = pending-owner-signal
```

That is not acceptable evidence for a task whose upstream dependencies are already
architect-accepted Complete. BACKGROUND-002's accepted report states that refresh
outcome telemetry uses the existing OpenTelemetry metrics API; GATEWAY-002 currently
queries a Loki log event name that is not established anywhere in this submitted
parent snapshot.

At start of Attempt 2, inspect the exact accepted dependency source/pins:

```text
ARCH-020-COMMERCE-010
  accepted implementation e8b43e4604780754ba64b0653c7d6e029d58e3c3

ARCH-020-BACKGROUND-002
  accepted implementation 8b2f9835dcd98b5385a64fa873598b8379b2986d

ARCH-020-GATEWAY-001
  accepted implementation 478923a
```

Record the actual file/export that owns every dashboard/alert signal and the exact
name, signal type, unit and bounded dimensions.

Required result:

```text
dashboard/alert query name
  == exact accepted producer/export name

log event
  -> Loki query only when the producer actually emits that structured log event

OpenTelemetry metric
  -> Prometheus/OTLP metric query using the actual exported metric name

no "pending-owner-signal" fixture pretending to be an implemented producer
```

If the accepted dependency source truly lacks a required C11 producer signal, do not
invent one and do not modify another repository from this task. Stop the same task as
`blocked` and return the exact upstream owner/source gap to `moda_architect`.

#### A1-R2 — correct the C11 readiness alert; discovery failure is not readiness

**Alert source/tests/runbook changes required.**

C11 requires:

```text
readiness unavailable for 2 consecutive minutes
evaluation interval = 1 minute
```

The current rule instead counts any:

```text
commerce.discovery.outcome = UNAVAILABLE
```

inside a two-minute lookback and fires immediately when the count is non-zero.
Developer-resource discovery is not Commerce `/health/ready`, and "one event in the
last two minutes" is not "readiness continuously unavailable for two minutes."

Use the actual accepted readiness/health signal available to the approved observability
stack and implement:

```text
current readiness failure condition
for: 2m
NoData remains NoData
environment/service explicit
```

Do not substitute discovery/schema/provider availability.

If no accepted readiness source can reach Grafana without violating C10's private
health-route boundary, return the task `blocked` with that concrete architecture gap;
do not guess a proxy signal.

#### A1-R3 — make the alert rules real Grafana-managed rules, not dashboard-templated YAML

**Alert provisioning/configuration/tests/runbook changes required.**

Current Grafana Alerting evaluates rules without dashboard context. Therefore alert
queries cannot rely on dashboard variables such as:

```text
$environment
```

The current alert file uses `$environment` in every rule. It also provides no concrete
Loki/Prometheus datasource binding for its query records, while mixing Loki,
Prometheus and expression queries.

Correct this with a Cloud-compatible, version-controlled rendering/import boundary.

Required behavior:

1. Alert evaluation is separated by environment without dashboard variables.
   Either:
   - render explicit test and production rules; or
   - return independent alert instances grouped by the real
     `deployment_environment_name` label.
2. Every source query has an explicit datasource UID/type in the final payload.
3. Expression/reduce queries use Grafana's expression datasource where required.
4. Loki alert inputs are instant/reduced to evaluable numeric values before threshold
   math; do not hand a raw range series directly to a scalar failure-rate condition.
5. Every alert instance carries:
   - service;
   - environment;
   - runbook link;
   - preview excluded with `purpose=live` where applicable.
6. No datasource credentials/tokens are committed.

The platform observability contract uses Grafana Cloud. Grafana Cloud does not support
server-side file provisioning from a local `provisioning/alerting` directory, so
`alerts/commerce-operational.yaml` cannot be presented as a complete deployment
mechanism by itself.

Add one documented Cloud-compatible import path, for example:

```text
version-controlled source
-> deterministic render using externally supplied Loki/Prometheus datasource UIDs
-> Grafana Dashboard HTTP API / Alerting Provisioning HTTP API
```

or the already-approved Terraform equivalent if the repository already owns such a
path. Do not introduce a second observability platform.

A dry-run/local validation path must prove that the rendered payload contains no
unresolved datasource/environment placeholders. Live credentials remain developer
owned and are not printed.

#### A1-R4 — complete the required operational views

**Dashboard/tests/runbook changes required.**

The binding parent architecture requires GATEWAY-002 to show:

```text
MCP errors
MCP latency
tool outcomes
worker queue lag
provider throttling
```

and the task also requires:

```text
eligibility outcomes
preview isolation/cost
evidence refresh
```

The submitted five-panel dashboard has request/error counts, eligibility, queue age,
preview and evidence refresh, but no actual MCP latency view, no tool-outcome view and
no provider-throttling view.

Use only accepted signals from A1-R1:

```text
MCP latency
  -> existing accepted framework/client/runtime latency signal
  -> do not create a duplicate custom HTTP metric

tool outcomes
  -> accepted Commerce semantic execution/tool signal

provider throttling
  -> accepted provider/tool outcome or client signal showing THROTTLED/rate-limit
     behavior
```

Keep preview data visibly separate from live production operations. Do not expose shop,
conversation, customer, prompt, provider payload, token or transcript as metric labels.

If one of these views has no accepted producer signal, return the exact upstream gap
rather than creating a made-up fixture.

#### A1-R5 — validate the actual alert boundaries, low samples, recovery and NoData

**Validator/fixture changes required.**

`tests/validate-commerce-observability.sh` currently proves mostly that strings exist.
It does not prove the deterministic review matrix required by this task.

Add bounded local fixtures/checks for at least:

```text
READINESS
  first failed evaluation                 -> pending, not firing
  continuously failed for 2 minutes       -> firing
  recovery                                -> resolved
  missing telemetry                       -> NoData

MCP FAILURE RATE
  A=20, F=1  (exactly 5%)                 -> not firing
  A=20, F=2  (>5%)                        -> firing
  A=19 regardless of ratio                -> not firing (sample floor)
  DENIED/REVOKED/INVALID_INPUT             -> denominator, not operational numerator
  preview purpose                          -> excluded

QUEUE AGE
  120 seconds exactly                      -> not firing
  >120 seconds continuously for 5 minutes  -> firing
  recovery                                 -> resolved
  no series                                -> NoData

EVIDENCE REFRESH
  A=20, F=2  (exactly 10%)                -> not firing
  A=20, F=3  (>10%)                        -> firing
  A=19                                     -> not firing
  missing telemetry                        -> NoData
  preview/non-live                         -> excluded
```

Use the exact accepted producer outcome names discovered under A1-R1. Do not encode a
separate business contract in the test merely to make the current alert text pass.

The validator must additionally fail when:

```text
an alert query still contains $environment
a source query lacks a datasource binding
a rendered Cloud payload retains unresolved datasource placeholders
the readiness rule is backed by discovery outcome
required latency/tool/throttle views are absent
```

#### A1-R6 — reconcile the task record and preserve the developer-hosted evidence gate

**Task/report changes required.**

The authoritative task record still has all four Work Items unchecked even though the
agent submitted the task for review, and the Git/VCS section still says commits
"will be recorded here before submission."

On Attempt 2, reconcile:

```text
Work Items
Acceptance Criteria
Validation
Completion Report
Git / VCS
```

truthfully.

Record:

```text
Attempt 2 implementation commit
Attempt 2 parent report commit
dedicated parent/implementation worktrees
clean/pushed evidence
accepted dependency pins actually consumed
actual signal-owner files/exports inspected
```

The user reported Attempt 1 implementation `6fb2ac5` and parent report `ccf6ecbc`;
preserve those as historical evidence but do not present them as Attempt 2.

The existing task text explicitly requires deployed arrival/alert evidence before
final acceptance. Keep that developer-owned gate truthful. The repository agent must
not fabricate hosted evidence and must not require live credentials to complete its
source correction.

After the agent-owned corrections return to `review`, developer evidence must record
against the approved test Grafana environment:

```text
dashboard/import success
one live Commerce signal arrival
one preview signal arrival
one queue-age metric arrival
actual Background refresh signal arrival
alert-rule evaluation for test boundary/recovery
preview exclusion from production/live alerts
NoData behavior where a signal is intentionally absent
```

No production mutation or paid-provider call is required merely for this validation.
Do not mark hosted evidence PASS until the developer actually performs it.

### Attempt 1 Reviewed Files

- `dashboards/commerce-operational.json`
- `alerts/commerce-operational.yaml`
- `docs/commerce-operational-runbook.md`
- `tests/fixtures/commerce-operational-signals.json`
- `tests/validate-commerce-observability.sh`
- C11 in `ARCH-020-implementation-contracts.md`
- accepted COMMERCE-010 and BACKGROUND-002 parent task evidence
- this task Completion Report

### Attempt 1 Validation Reviewed

Architect independently reran from the submitted archive:

```text
bash tests/validate-commerce-observability.sh
  PASS — "commerce observability configuration validation passed"

bash -n tests/validate-commerce-observability.sh
  PASS

Ruby YAML parse of alerts/commerce-operational.yaml
  PASS

jq parse of dashboards/commerce-operational.json
  PASS
```

These checks establish syntax/string invariants only; they do not establish a valid
Grafana-managed alert evaluation model or live signal arrival.

The executor-reported `git diff --check` pass is retained as submitted evidence. The
review archive is not a Git working tree, so the architect does not falsely claim an
independent Git diff check.

### Attempt 1 Architecture Conformance

Not yet conformant with C11.

The useful dashboard/runbook direction is preserved, but acceptance is blocked by the
producer-inventory mismatch, incorrect readiness semantics, non-evaluable Grafana alert
model, missing required latency/tool/throttling views, insufficient boundary fixtures
and pending hosted evidence explicitly required by the task.

### Attempt 1 Follow-up

Return the same task to:

```yaml
status: ready
attempt: 1
executor: null
claimed_at: null
```

The next:

```text
/moda-task ARCH-020-GATEWAY-002
```

must claim **Attempt 2 exactly once**.

Do not start COMMERCE-012 or SYSTEM-TEST-001. GATEWAY-003 remains independently Ready
and is not changed by this review.
