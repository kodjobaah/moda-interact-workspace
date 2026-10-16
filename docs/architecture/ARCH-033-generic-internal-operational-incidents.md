---
id: ARCH-033
title: Generic internal operational incident management
status: in_progress
coordinator: moda_architect
created: 2026-10-11
updated: 2026-10-16
---

# ARCH-033 — Generic internal operational incident management

## Status
In Progress — implementation and publication have been reconciled against the 2026-10-16 workspace snapshot. Seven task records are Complete by explicit developer-directed code-based acceptance, the Background pilot is Superseded, and terminal SYSTEM-TEST-001 is Ready and unexecuted. No Git merges or fresh test runs are claimed by this reconciliation.

## 2026-10-16 — Approved implementation and rollout reconciliation

**Classification:** Pre-production / breaking rollout for the legacy MCP incident subsystem. The developer confirmed that retaining the old MCP-specific incident/event process or its historical rows is unnecessary. The existing generic incident-schema migration and subsequent `DROP TABLE` cleanup are approved **without** a legacy backfill; unrelated merchant-support and billing tables/data remain protected. This decision supersedes earlier preservation requirements in task drafts and historical planning notes.

**Reporting policy:** The internal generic reporter is canonical. MCP maps its existing actionable classifications and original error identities into the published Shared reporter; it does not write old MCP tables. A merchant-support SYSTEM message is **optional**, only when a producer explicitly enables an appropriate safe notification policy. Absence of the former automatic projection does not block MCP-001 under this approved internal-only scope; it does not authorise deleting unrelated merchant-support data.

**Published package:** The developer supplied a successful `npm view @modainteract/moda-interact-shared@2.4.1`, including a registry tarball URL, SHA-1, SHA-512 integrity and `latest: 2.4.1`. The 16 October source contains the `./incidents` export and an MCP dependency/import of 2.4.1. That constitutes the developer-approved publication evidence for SHARED-003. No independent clean-install unpack/import test was executed during this reconciliation.

**Task state (task YAML is authoritative):**

| Task | Reconciled status | Basis |
|---|---|---|
| ARCH-033-DATABASE-001 | Complete | Generic schema, migration, PostgreSQL test sources; legacy table cleanup explicitly approved |
| ARCH-033-SHARED-001 | Complete | Versioned incident contract and validation |
| ARCH-033-SHARED-002 | Complete | Transactional reporter, injected persistence and test sources |
| ARCH-033-SHARED-003 | Complete | Published npm package 2.4.1; existing consumer use |
| ARCH-033-MCP-001 | Complete | Shared reporter adoption, bounded actionable classification; optional support notification |
| ARCH-033-ADMIN-001 | Complete | Internal generic incident listing and investigation |
| ARCH-033-ADMIN-002 | Complete | Atomic case assignment, audited resolution and test sources |
| ARCH-033-BACKGROUND-001 | Superseded | Developer explicitly removed Background producer pilot from ARCH-033 |
| ARCH-033-SYSTEM-TEST-001 | Ready | Terminal MCP/Shared/Database/Admin black-box certification still to run; no Background dependency |

**Dependency direction:** `DATABASE-001` and `SHARED-001` → `SHARED-002` → `SHARED-003` → independently `MCP-001` and `ADMIN-001` → `ADMIN-002`; all completed implementation prerequisites → `SYSTEM-TEST-001`. BACKGROUND-001 is removed from the active graph. SYSTEM-TEST-001 is terminal and must not block other implementation tasks.

**Completion boundary:** ARCH-033 remains **in_progress**, not Implemented, until SYSTEM-TEST-001 is completed or an explicit separate no-system-test architectural decision is recorded. Source-based task completion does not assert any fresh tests, remote Git states, deployment, or system-test evidence.

## Problem
ARCH-032-MCP-014 proves an actionable failure can create an incident, an occurrence event and a deduplicated merchant-support SYSTEM message transactionally, and the test Admin dashboard can resolve incidents. However, the persistent models (`McpOperationalIncident`, `McpOperationalEvent`), reporter and Admin UI are MCP-specific. No incident ownership is implemented; the merchant-support thread has separate ownership. Other services (particularly Background) should use the same internal investigation workflow without duplicating it.

## Goals
- Internal-only authenticated Moda platform-admin incident triage, assignment, investigation, resolution, reopening and audit.
- Domain-specific producers use one versioned, validated shared reporting contract while retaining responsibility for deciding which failures are actionable.
- Durable event/occurrence deduplication; one incident per stable correlation identity; safe bounded metadata; tenant and environment separation.
- Preserve the existing MCP reporting semantics and existing merchant-support workflow.
- Reuse existing shared structured logger and PostgreSQL; do not add a deployable service without need.

## Non-goals
- No merchant-facing incident dashboard or API; no direct tenant access to diagnostics.
- No automatic tickets for every exception, ordinary retry, validation error or rate limit.
- No automatic merchant communication by default. An explicit producer policy may author a safe support SYSTEM message.
- No change to Commerce/MCP extraction ownership or activation of standalone MCP endpoint.
- No new log collection framework; incidents are not a replacement for metrics, tracing or logs.

## Inspected current implementation
- `moda-interact-database/prisma/migrations/20261011120000_arch032_mcp_operational_events/migration.sql` adds support-scoped MCP incident and event tables, keyed by a shop and capability, with an event per failure ID.
- `moda-interact-mcp/src/operational/notifications.ts` defines bounded actionable reason codes and a PostgreSQL `$transaction` that inserts an event (skip duplicates), upserts an incident and upserts a merchant support SYSTEM message by sourceKey.
- `moda-interact-admin/src/lib/admin/mcp-operational-issues.ts` requires platform-admin auth; resolution sets RESOLVED and creates an event with `actorAdminId`.
- `moda-interact-admin/src/lib/admin/merchant-support.ts` already implements thread Take/Release/Reassign with conditional updates; thread ownership is *not* incident ownership.
- Live Render TEST reporter output and screenshots, supplied by the developer, demonstrate notification and support-message visibility; end-to-end resolution persistence still needs explicit evidence.

## Proposed architecture

### Responsibilities
- **Shared**: own `@modainteract/moda-interact-shared/incidents`, including versioned occurrence schemas, bounded identifiers, deduplication, lifecycle and a transaction-safe reporter accepting an injected database persistence adapter. Do not create a global Prisma client or own secrets in Shared.
- **Database**: new general `OperationalIncident` and append-only `OperationalIncidentEvent` tables under the support schema; own constraints, indexes and upgrade/fresh validation.
- **Reporting boundary**: one reusable, transaction-safe reporter implemented in `moda-interact-shared/incidents`, relying on an injected persistence/transaction port implemented by the consuming server-side runtime using canonical Prisma models. Preserve atomic occurrence, incident update and optional safe notification; never instantiate a global Prisma connection inside Shared. Merchant-hosted WooCommerce must call an approved Moda API, not access PostgreSQL directly.
- **MCP**: translate its existing classified actionable failures into the canonical reporter; do not broaden classification.
- **Background**: adopt only selected safe, actionable failures in a later explicit producer task; no automatic incident creation for all job failures.
- **Admin**: one internal `Operational Incidents` page with filters, case details, ownership, timeline, resolve/reopen and optional links to merchant support threads. Preserve existing role checks.
- **Gateway**: assess deployment and env wiring from actual implementation; no new service assumed.

### Data model (proposed)
`OperationalIncident`: ID; stable incidentKey (unique); sourceService; category; reasonCode; resourceKey or stable bounded fingerprint; nullable shopId (platform incidents allowed); environment identifier; severity; OPEN/RESOLVED status; occurrenceCount; first/last occurrence timestamps; lastCorrelationId; ownerPlatformAdminId (nullable); assignedAt; resolvedAt; resolvedByPlatformAdminId; resolutionNote (bounded); revision/version for race control.

`OperationalIncidentEvent`: unique event ID; incidentId foreign key; eventType (OCCURRED/CLAIMED/RELEASED/REASSIGNED/RESOLVED/REOPENED); actorPlatformAdminId nullable for system events; timestamp; bounded safe correlation/metadata. Occurrence event identity must remain stable across duplicate delivery. Use DB constraints/FKs for ownership/tenant integrity, and concurrency-safe conditional updates for transitions. Events must not contain raw provider errors, credentials, stack traces, tool arguments or customer payloads.

An optional relation to `MerchantSupportMessage` (or stable reference) permits a notification without requiring every incident to have a shop/support thread. Do not use support-thread ownership for incident accountability.

### Lifecycle and concurrency
- On actionable report: deterministic incident key from explicitly versioned tuple including source service, environment, affected tenant/resource and bounded reason; insert unique occurrence event, then increment incident only if event was newly inserted. Reopen a resolved incident atomically when new occurrence policy requires it.
- Take: only if OPEN and owner null; assign the authenticated admin atomically and append CLAIMED.
- Release: owner or authorised elevated role; clear owner atomically and append RELEASED.
- Reassign: elevated authorised role; atomically change owner and append REASSIGNED.
- Resolve: assigned admin only (agreed proposed policy); record actor, time and optional bounded reason, atomically append RESOLVED; repeated resolution does not create duplicate events.
- Admin should display resolved-by attribution and immutable transition history, including if the incident later reopens.
- Concurrent claims, resolution-versus-occurrence and duplicate reports need explicit transaction/integration tests.

### Isolation and information safety
- Admin incident APIs server-side only; authenticated and role-authorised. No merchant-facing incident routes, queries or cross-tenant telemetry.
- Distinguish Render test/staging from production in incident identity and Admin views; test harness fails closed on production database targets.
- Stable bounded reason codes and opaque correlations only; no raw failure bodies. Shared logger remains canonical.

### Migration strategy
- **Do not drop MCP tables or lose existing data without a deliberate migration plan.** Decide whether to migrate existing incidents/events and links to new generic tables or to seed clean generic tables only when development/non-production conditions are verified; record the chosen classification explicitly.
- Sequence: database/schema + disposable PostgreSQL fresh/upgrade tests; shared contract and (if needed) package publication; generic reporter; Admin generic UI and claim/resolve; MCP adoption; independent integration test; Background pilot; system-test acceptance.
- Do not introduce compatibility adapters solely for hypothetical production consumers, but do not assume Render test state is disposable.

## Candidate bounded tasks (not yet materialised)
1. `ARCH-033-DATABASE-001` — Generic incident and audit schema, constraints, migration and disposable PostgreSQL fresh/upgrade tests.
2. `ARCH-033-SHARED-001` — Versioned, bounded cross-service incident occurrence contract and runtime validator.
3. `ARCH-033-SHARED-002` — Canonical, transaction-safe reporter implementation and focused concurrent/idempotent integration tests; separate package publication gate if published library changes.
4. `ARCH-033-ADMIN-001` — Generic incident list/detail and existing audit attribution display.
5. `ARCH-033-ADMIN-002` — Ownership transitions and resolve/reopen actions with race-safe tests.
6. `ARCH-033-MCP-001` — Map accepted MCP actionable failure classifier into canonical reporter; verify no duplicate incident writes and parity of support message rules.
7. `ARCH-033-BACKGROUND-001` — Select and implement one Background actionable incident pilot, with suppression/retry behaviour verified.
8. `ARCH-033-SYSTEM-TEST-001` — Terminal cross-service tests of persistence, deduplication, auth, ownership, resolution, reopening and environment isolation; must depend on all required implementation/publication/infrastructure tasks.

Task ownership and dependency graph are materialised as portable, unclaimed definitions in this bundle. Existing MCP records must be preserved unless an explicitly verified non-production disposal decision is subsequently approved. No `_index.md` file has been changed.

## Open questions requiring decisions
1. Reporter ownership settled: canonical reusable reporter is `@modainteract/moda-interact-shared/incidents`; implementation must use injected transactional persistence ports, not a global Prisma client.
2. Which existing Render test incidents and historical audit events must be preserved when genericising?
3. Should resolved incidents reopen automatically for an identical new occurrence, and should an owner persist across a reopening? Suggested: reopen, reset owner; retain history.
4. For platform-wide (shopless) failures, which grouping dimensions avoid a single noisy global incident?
5. Should a resolution note be required? Suggested: require a bounded rationale for audit, with a consistent admin UI form.

## Change history
2026-10-11: Shared owns the generic reporter and contracts; generated portable ARCH-033 task definitions and terminal system-test dependency plan. No `_index.md` files changed.
2026-10-11: Initial draft based on developer's internal-only agreement, MCP-014 implementation inspection and Render test evidence. No source edits.
