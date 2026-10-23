---
id: ARCH-047-DATABASE-001
architecture_id: ARCH-047
title: Add WhatsApp template management audit actions
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: in_progress
priority: 15
executor: developer
claimed_at: 2026-10-23T17:33:17Z
attempt: 1
depends_on: []
enables:
  - ARCH-047-ADMIN-001
created: 2026-10-23
updated: 2026-10-23
---

# Add WhatsApp template management audit actions

## Architecture

`ARCH-047` — `docs/architecture/ARCH-047-admin-managed-whatsapp-template-catalogue.md`; coordinator `moda_architect`. Source snapshot: 23 October 2026, 16:40.

## Objective

Introduce only the enum values required to record durable `SUPER_ADMIN` WhatsApp-template create/update/enable/disable and bulk-assignment changes in the **existing** `commerce.CommerceAuditEvent` log.

## Context

`CommerceAuditEvent` already contains `actorAdminId`, `shopId`, `operationId`, `reason`, `metadata`, timestamps, and the necessary indexes. The `CommerceAuditAction` enum does not yet support WhatsApp-template management. Without explicit action values, Admin cannot record truthful, reviewable evidence by reusing the canonical audit log.

## Scope

- Amend `moda-interact-database/prisma/schema.prisma` `CommerceAuditAction` with bounded new action values for WhatsApp variant create, update, enable, disable, bulk assign and bulk update. Choose descriptive, stable names; examples: `CREATE_WHATSAPP_TEMPLATE_VARIANT`, `UPDATE_WHATSAPP_TEMPLATE_VARIANT`, `ENABLE_WHATSAPP_TEMPLATE_VARIANT`, `DISABLE_WHATSAPP_TEMPLATE_VARIANT`, `BULK_ASSIGN_WHATSAPP_TEMPLATE_VARIANT`, `BULK_UPDATE_WHATSAPP_TEMPLATE_VARIANT`.
- Add one additive PostgreSQL migration for these enum values, with focused schema/migration tests demonstrating that `CommerceAuditEvent` can persist and query a per-shop audited template operation.
- Preserve all existing template data, enum values, audit relations, indexes and production compatibility.

## Out of Scope

- No new master/template/assignment/audit tables; no changes to `WhatsAppTemplateVariant`, consent or sender configuration models.
- No provider category field, Meta metadata synchronisation, Admin UI or Background implementation.
- No unrelated enum action additions, audit schema redesign, production data rewrites or provider-category checks.

## Requirements

- [ ] One authoritative set of semantically correct audit actions exists in the existing `CommerceAuditAction` enum.
- [ ] Enum migration is additive and idempotent under normal Prisma migration execution; works against a previously migrated database.
- [ ] Existing `CommerceAuditEvent` supports shop-specific event `operationId`, actor, reason and bounded previous/new values in metadata without creating a new relation or table.

## Work Items

- [ ] Edit the enum and create the minimum SQL migration.
- [ ] Add focused fresh-migration and upgrade-migration tests (or existing repository-equivalent database checks).
- [ ] Demonstrate an Admin-action audit insert/select with a new enum value and unchanged historical audit records.

## Interfaces / Contracts

Produces `CommerceAuditAction` variants on the existing generated Prisma client, consumed by ARCH-047-ADMIN-001 and -002. Database package/model publication is by the repository's existing merge/submodule process; do not invent a Shared runtime contract or release.

## Dependencies

None.

## Enables

- `ARCH-047-ADMIN-001`

## Acceptance Criteria

- [ ] New audit actions are distinguishable from existing commerce prompt-template actions.
- [ ] No new persistent table, `WhatsAppTemplateVariant` column, Meta category column or default is introduced.
- [ ] Historical audit events, templates, schema constraints and migrations remain valid.
- [ ] PostgreSQL integration evidence confirms new audit actions persist with actor/shop/reason/operation ID.

## Validation

- [ ] Prisma schema validation and migration verification against clean and upgraded databases.
- [ ] Focused PostgreSQL audit tests; `git diff --check`.
- [ ] Report schema/migration filenames, expected deployment ordering and any migration baseline limitations.

## Stop Condition

After completing the defined Work Items, Acceptance Criteria and required Validation, record task-isolated parent and implementation worktrees, start-of-attempt synchronisation and relevant commit evidence in the Completion Report; set `status: review`, return control to `moda_architect`, and **STOP**. Do not implement dependent tasks or modify domain `_index.md` files.

## Implementation Notes

Respect `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, `docs/task-definition-materialization.md` and `docs/developer-task-workflow.md`. `/moda-task` owns preparation and the canonical claim; never infer worktrees from a previous task or operate in shared/default checkouts. Existing application code has evolved: inspect current implementation immediately before claiming and return cross-domain contract gaps to `moda_architect`. Use the shared structured logger where new runtime domain logging is needed, not a duplicate generic logger. All tasks are portable definitions until materialised in the developer's real workspace.

## Completion Report

### Status

In Progress — Attempt 1 claimed by developer at 2026-10-23T17:33:17Z. Attempt 0 review history is preserved below.

### Execution Ownership Amendment

On 23 October 2026, the developer explicitly invoked `/moda_developer_create ARCH-047-DATABASE-001` for this task while its authored definition still declared agent execution. The task remains assigned to `moda_database`; execution is transferred to the developer and completion remains developer-controlled for this attempt.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

Based on `moda-interact-workspace(20261023-164023).zip`; revalidate against launcher-resolved task worktree when execution begins.

### Unresolved Issues

None recorded at definition time.

### Architectural Concerns

None recorded at definition time.

## Architect Review

### Review Status

Pending — no implementation reviewed.

### Review Notes

None.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Not assessed.

### Follow-up

None.
