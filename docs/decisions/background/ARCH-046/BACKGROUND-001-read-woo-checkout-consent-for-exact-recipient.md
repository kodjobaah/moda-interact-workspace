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
status: review
priority: 27
executor: null
claimed_at: null
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

**Lifecycle:** materialised and claimed for developer Attempt 1 on 2026-10-22; implementation committed and pushed as `c4c8a180187b315c3f1c94c17f585f2f2db1a48d`. Submitted for architectural review, not yet accepted or complete. `assigned_agent: moda_background` remains the logical owner.

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

- [x] Only one exact active CustomerPhone linked to the authenticated shop, a current valid GRANTED permission, no stronger local no-contact and active Woo installation can authorise proactive recovery.
- [x] A phone match or merchant checkbox/toggle alone never grants permission; stale or withdrawn source decisions cannot be inherited by changed phone or another customer.
- [x] This reader never schedules checkout work; it remains testable while ARCH-035 is capture-only.
- [x] A standalone WhatsApp STOP propagated by ARCH-045-BACKGROUND-005 to all registered matching CustomerPhones also blocks the Woo merchant; a quoted STOP for another shop must not modify Woo permission.

## Work Items

- [x] Implement injected current Woo CustomerPhone/installation consent reader with canonical shop-scoped recipient lookup and typed decision/snapshot.
- [x] Test missing/ambiguous/cross-shop/changed phone, grant/revoke, STOP, merchant suppression and installation lifecycle without a live Woo recovery engine.

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

- [x] Same-shop unique exact phone and current granted consent plus active installation are required; cross-shop duplicates never leak permission, same-shop duplicates deny.
- [x] Customer STOP overrides a grant (including a fresh Woo checkbox grant) for every outbound WhatsApp message; merchant recovery re-enable never manufactures consent or clears STOP. Clearing STOP requires a separate, verified customer-requested Moda flow outside this task.
- [x] Reader does not consume evidence history, trigger recovery, require a Woo checkout identity table or use Shopify provider calls.

## Validation

- [x] Focused DB-backed exact-recipient canonical-phone, cross-tenant, zero/one/multiple matches, installation revoke/reconnect, grant/revoke/STOP and failure tests.
- [x] Injectability/typed decision and revision-snapshot tests plus `git diff --check`.

## Stop Condition

After completing **only** the defined Work Items, Acceptance Criteria and required Validation, record launcher-resolved dedicated parent/implementation worktrees, their physical isolation and start-of-attempt synchronization evidence in the Completion Report. Change task to `review`, return control to `moda_architect`, and **STOP**. Do not start enabled tasks. A `blocked` task must remain blocked until the architect verifies and records the external missing recovery dependency and explicitly makes it Ready.

## Implementation Notes

This task is safe to implement before a Woo recovery engine exists; do not include admission integration here.

Before any implementation, use `/moda-task` deterministic preparation against the **developer's actual** primary workspace, read the latest task/Architect Review, the parent architecture, relevant agent instructions, and the repository's real `package.json` scripts. Do not invent environment variables or claim a completed checkout/recovery source from the snapshot. Do not modify another repository, architecture-wide docs or `docs/decisions/**/_index.md` in a repository task. Use `@modainteract/moda-interact-shared/logging` for Node server diagnostics; PHP uses WordPress-specific safe diagnostics. Preserve official user/merchant i18n and tenant boundaries.

## Completion Report

### Status

Ready for Review — developer Attempt 1. Implementation commit `c4c8a180187b315c3f1c94c17f585f2f2db1a48d` was pushed to `moda-interact-background` branch `task/ARCH-046-BACKGROUND-001`. The task is in `review`, not `complete`; architect acceptance and explicit developer completion remain outstanding.

### Files Changed

Implementation repository `moda-interact-background` (four committed files):

- `package.json` — dedicated unit and PostgreSQL test scripts.
- `src/services/woocommerce-recovery-consent.service.ts` — injectable, read-only exact-recipient consent reader.
- `tests/unit/services/woocommerce-recovery-consent/reader.test.ts` — 19 unit tests.
- `tests/integration/woo-recovery-consent-reader.integration.test.ts` — 3 migrated-PostgreSQL integration tests.

Parent task: this Completion Report, completion checkboxes and task-review metadata only. No `_index.md`, parent architecture, database schema or other repository source changed under this task.

### Work Completed

- Implemented an injectable Woo recipient-consent reader returning typed `ALLOWED`, `NOT_AUTHORISED`, `UNAVAILABLE` or `AMBIGUOUS` results and a current consent/no-contact revision snapshot for future outbound checks.
- Resolved the exact canonical recipient from the approved Woo shop/installation context. One active, unambiguous `CustomerPhone` belonging to that merchant is required; missing, duplicated, changed-phone and cross-shop matches fail closed.
- Required an active Woo installation and current verified `WOO_MODA_CHECKBOX` marketing-purpose `GRANTED` consent; rejected missing, withdrawn, stale, unsupported or unverified permission.
- Enforced `CUSTOMER_STOP` and merchant suppression over grants; a fresh checkbox grant or merchant enable toggle cannot clear STOP or manufacture permission.
- Kept this reader read-only: no audit-evidence scan, Shopify HTTP preflight, recovery creation, queue publication, billing or outbound messages.
- Used the task's canonical isolated parent and implementation worktrees. The preserved `## Developer Takeover — Attempt 1` section below contains the launcher-derived roots, physical isolation, synchronization bases and submodule initialization evidence.

### Validation Results

- `npm ci` — succeeded (603 packages installed). npm reported 15 dependency vulnerabilities (8 moderate, 7 high), plus deprecation/install-script warnings.
- `npm run test:arch046-woo-consent-reader:unit` — **PASS 19/19**.
- `npm run test:arch046-woo-consent-reader:postgres` — **PASS 3/3** against migrated PostgreSQL. Covered unique/ambiguous/missing phone, country-context ambiguity, cross-tenant grants, withdrawal, phone replacement, merchant suppression/re-enable, `CUSTOMER_STOP`, reconnect/stale installation credentials and inactive shops.
- `npm run lint` — **PASS**.
- `npm run build` — **PASS** (`prisma generate` v6.19.3 and `tsc`).
- `git diff --check` — **PASS** (no whitespace errors).
- Database checkout: `e0ab833d2e2395e3ed3cfe4aee6d07c716173e44` (task-recorded gitlink); verified `CustomerPhone.whatsappConsentDecision` and `whatsappConsentDecisionSequence` were present.
- Implementation commit `c4c8a180187b315c3f1c94c17f585f2f2db1a48d` includes exactly the four files listed above; user confirmed successful push to `origin/task/ARCH-046-BACKGROUND-001`.
- Start-of-attempt evidence: parent and Background task worktree paths, synchronized clean bases `5615c931b76f742f04e2aaccde05c8a7b287087a` and `6279d89eb3a2b57a8e220faffabf60c0876d67c3`, plus recursive database initialization, are retained under `## Developer Takeover — Attempt 1` below.

### Deviations

None from the reader-only scope. No dependent recovery/sending task was started.

### Assumptions

`CustomerPhone` current permission, not immutable consent-evidence history, determines eligibility; consent has no invented expiry period. Future Background consumers must recheck the exact recipient and independently evaluate checkout/recovery validity before acting.

### Unresolved Issues

No known task-owned failing test. npm dependency audit warnings remain for separate security/dependency triage, not an automatic fix in this bounded task. Await architect review and explicit developer completion.

### Architectural Concerns

This task provides only the reader. `ARCH-046-BACKGROUND-002/004` must integrate its typed decision and final-send revalidation under their own scopes. No cross-service queue contract or database migration was introduced.

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
