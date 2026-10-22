---
id: ARCH-046-BACKGROUND-001
architecture_id: ARCH-046
title: Read current Woo customer-phone consent for exact recipient
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: in_progress
priority: 27
executor: developer
claimed_at: 2026-10-22T20:42:09+01:00
attempt: 1
depends_on:
  - ARCH-045-DATABASE-002
  - ARCH-045-SHARED-002
enables:
  - ARCH-046-BACKGROUND-002
  - ARCH-046-BACKGROUND-004
  - ARCH-046-SYSTEM-TEST-002
created: 2026-10-20
updated: 2026-10-22
---

# Read current Woo customer-phone consent for exact recipient

## Architecture

Architecture ID: `ARCH-046`

Architecture document: `docs/architecture/ARCH-046-woocommerce-whatsapp-consent-gated-recovery.md`

Coordinator: `moda_architect`

**Lifecycle:** materialised on the canonical parent task branch and claimed for developer Attempt 1 on 2026-10-22. The portable-snapshot wording in the initial Completion Report is retained as historical source context; this task is now actively in progress. `assigned_agent: moda_background` remains the logical owner.

## Objective

Provide a small injectable WooCommerce consent reader for **normal checkout reconciliation and existing authorised recovery sending**, using an unambiguous merchant-scoped active `CustomerPhone`, the existing Woo installation status and current no-contact restrictions.

## Context

`ARCH-045-DATABASE-002` stores current consent on CustomerPhone and immutable Woo grant/withdrawal evidence for audit. Consent evidence is **not** a current-state lookup, polling worklist or recovery trigger. The reader can be implemented and tested before the separate Woo recovery engine exists.

## Scope

- Resolve the shop from the authenticated Woo installation/approved job context and canonicalise the exact checkout recipient using published Shared phone rules; use `Customer.shopId` plus active `CustomerPhone` to select exactly one unambiguous shop-scoped match. Zero, ambiguous or changed-phone matches fail closed; never merge customers because their phone numbers match.
- Require current `GRANTED` WhatsApp checkout-recovery permission from a verified Moda checkbox, no customer STOP and no merchant recovery suppression, and an active installation. A merchant's customer enable toggle cannot create a grant; optional merchant disable is a separate negative restriction.
- Treat recovery as **business-initiated WhatsApp Marketing**, not a utility/transactional notification. The current CustomerPhone permission must cover that marketing purpose; merely capturing the checkout phone, or selecting a customer in merchant admin, is not consent.
- Return typed allowed/not-authorised/unavailable/ambiguous results and an exact-recipient snapshot with current consent/no-contact revision for use by future pre-create and final outbound fences. DB read failures deny; Woo requires **no Shopify HTTP preflight**.
- Reuse an injectable Background policy shape compatible with Shopify first-send/follow-up consumers without duplicating consent decision rules. Test one/no/multiple matches, cross-shop duplicate numbers, canonical-country ambiguity, activation/disconnect, revoke, STOP, merchant enable/disable and DB failure.

## Out of Scope

- No Woo recovery materialisation engine (BACKGROUND-002), evidence scan/polling (BACKGROUND-003 superseded), checkout UI/API capture, external plugin adapter, new identity table or installation consent configuration.

## Requirements

- [ ] Only one exact active CustomerPhone linked to the authenticated shop, a current valid GRANTED permission, no stronger local no-contact and active Woo installation can authorise proactive recovery.
- [ ] A phone match or merchant checkbox/toggle alone never grants permission; stale or withdrawn source decisions cannot be inherited by changed phone or another customer.
- [ ] This reader never schedules checkout work; it remains testable while ARCH-035 is capture-only.
- [ ] A standalone WhatsApp STOP propagated by ARCH-045-BACKGROUND-005 to all registered matching CustomerPhones also blocks the Woo merchant; a quoted STOP for another shop must not modify Woo permission.

## Work Items

- [ ] Implement injected current Woo CustomerPhone/installation consent reader with canonical shop-scoped recipient lookup and typed decision/snapshot.
- [ ] Test missing/ambiguous/cross-shop/changed phone, grant/revoke, STOP, merchant suppression and installation lifecycle without a live Woo recovery engine.

## Interfaces / Contracts

Consumes `ARCH-045-DATABASE-002` CustomerPhone and existing WooCommerceInstallation (no added consent columns), published `ARCH-045-SHARED-001/002` phone canonicalisation. The API is the writer; future `ARCH-046-BACKGROUND-002/004` inject this reader. No Shared Woo consent queue schema.

## Dependencies

- `ARCH-045-DATABASE-002`
- `ARCH-045-SHARED-002`

## Enables

- `ARCH-046-BACKGROUND-002`
- `ARCH-046-BACKGROUND-004`
- `ARCH-046-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] Same-shop unique exact phone and current granted consent plus active installation are required; cross-shop duplicates never leak permission, same-shop duplicates deny.
- [ ] Customer STOP overrides a grant (including a fresh Woo checkbox grant) for every outbound WhatsApp message; merchant recovery re-enable never manufactures consent or clears STOP. Clearing STOP requires a separate, verified customer-requested Moda flow outside this task.
- [ ] Reader does not consume evidence history, trigger recovery, require a Woo checkout identity table or use Shopify provider calls.

## Validation

- [ ] Focused DB-backed exact-recipient canonical-phone, cross-tenant, zero/one/multiple matches, installation revoke/reconnect, grant/revoke/STOP and failure tests.
- [ ] Injectability/typed decision and revision-snapshot tests plus `git diff --check`.

## Stop Condition

After completing **only** the defined Work Items, Acceptance Criteria and required Validation, record launcher-resolved dedicated parent/implementation worktrees, their physical isolation and start-of-attempt synchronization evidence in the Completion Report. Change task to `review`, return control to `moda_architect`, and **STOP**. Do not start enabled tasks. A `blocked` task must remain blocked until the architect verifies and records the external missing recovery dependency and explicitly makes it Ready.

## Implementation Notes

This task is safe to implement before a Woo recovery engine exists; do not include admission integration here.

Before any implementation, use `/moda-task` deterministic preparation against the **developer's actual** primary workspace, read the latest task/Architect Review, the parent architecture, relevant agent instructions, and the repository's real `package.json` scripts. Do not invent environment variables or claim a completed checkout/recovery source from the snapshot. Do not modify another repository, architecture-wide docs or `docs/decisions/**/_index.md` in a repository task. Use `@modainteract/moda-interact-shared/logging` for Node server diagnostics; PHP uses WordPress-specific safe diagnostics. Preserve official user/merchant i18n and tenant boundaries.

## Completion Report

### Status

In Progress — developer takeover of the ready agent-owned task, Attempt 1. Completion authority is developer (`completion_mode: developer`).

### Files Changed

No implementation files yet. The parent task record contains the durable claim and preparation evidence; implementation work will occur only in the canonical Background task worktree.

### Work Completed

- Verified both explicit dependencies, `ARCH-045-DATABASE-002` and `ARCH-045-SHARED-002`, are `complete`.
- Created and synchronized the canonical parent and implementation task worktrees on `task/ARCH-046-BACKGROUND-001`, each from its repository's current `origin/main`.
- Initialized the implementation worktree's recorded `database` submodule at `e0ab833d2e2395e3ed3cfe4aee6d07c716173e44`.
- Took over execution as `developer` without changing `assigned_agent: moda_background`; no source implementation has started.

### Validation Results

Preparation validation only: both dedicated task worktrees were clean and at their current `origin/main` tips before claim; `database` submodule resolved to the task-recorded commit. No implementation validation has run yet.

### Deviations

None.

### Assumptions

The canonical launcher-resolved workspace is `/Users/kwadwoadomafriyie/project/moda-interact-workspace`. Consent has no Moda-imposed waiting/expiry period. Recheck the current customer-phone permission and independently applicable checkout validity; do not invent a retention deadline. The separate live Woo recovery engine remains blocked and is outside this task.

### Unresolved Issues

Verify the exact current CustomerPhone schema and published Shared phone-canonicalisation contract in the synchronized worktree before implementation. Raise any actual missing cross-repository contract to moda_architect rather than expanding scope.

### Architectural Concerns

None recorded beyond explicit context and gates.

## Developer Takeover — Attempt 1

- Explicit `/moda_developer_create ARCH-046-BACKGROUND-001` invocation took over the `execution_mode: agent` task. `execution_mode` and `completion_mode` are now `developer`; logical ownership remains `assigned_agent: moda_background`.
- Claimed at `2026-10-22T20:42:09+01:00`; executor `developer`; attempt 1. Claim is published on the parent `task/ARCH-046-BACKGROUND-001` branch.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-046-BACKGROUND-001`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-046-BACKGROUND-001`.
- Parent source/reference checkout and implementation source/reference checkout were both dirty with unrelated user changes. They were left untouched. Both canonical task worktrees were created from their respective `origin/main` tips and verified clean before claim.
- Parent synchronization base: `5615c931b76f742f04e2aaccde05c8a7b287087a` (`origin/main`). Implementation synchronization base: `6279d89eb3a2b57a8e220faffabf60c0876d67c3` (`origin/main`). No remote task branch existed at preparation time.
- Implementation `database` submodule initialized at `e0ab833d2e2395e3ed3cfe4aee6d07c716173e44`, matching the recorded gitlink.

## Architect Review

### Review Status

Pending — no implementation reviewed or accepted.

### Review Notes

None.

### Reviewed Files

None — portable definition only.

### Validation Reviewed

None.

### Architecture Conformance

Not assessed.

### Follow-up

None.

**2026-10-22 architect coordination:** Promoted `pending -> ready` because all declared dependencies in the supplied snapshot are `complete`. Task remains unclaimed (`executor: null`, `claimed_at: null`, `attempt: 0`). This eligibility change does not materialise a branch/worktree or start implementation.
