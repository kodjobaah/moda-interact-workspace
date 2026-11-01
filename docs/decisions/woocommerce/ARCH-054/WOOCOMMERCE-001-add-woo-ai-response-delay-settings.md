---
id: ARCH-054-WOOCOMMERCE-001
architecture_id: ARCH-054
title: Add WooCommerce AI delay control through protected WordPress REST
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 30
executor: codex
claimed_at: 2026-11-01T12:51:33Z
attempt: 1
depends_on:
  - ARCH-054-API-001
enables: []
created: 2026-10-31
updated: 2026-11-01
---


# ARCH-054-WOOCOMMERCE-001: Add WooCommerce AI delay control through protected WordPress REST


## Architecture

Architecture: `ARCH-054`

Document: `docs/architecture/ARCH-054-merchant-configurable-ai-response-delay.md`

Coordinator: `moda_architect`. Task **defined but not materialised**; no local Git/worktree/branch activity is claimed.


## Objective

Provide authenticated WooCommerce settings UI for all whole-minute 0–30 values through the approved hosted API, without direct database access.


## Context

ARCH-054 adds a **merchant-selectable integer 0–30 minute AI reply delay** to the existing ARCH-040 recovery-conversation processor and handover controls, leaving merchant-authored HUMAN replies without configured delay. See the parent architecture and current snapshot for specific boundaries.


## Scope

Create `includes/Rest/AiResponseDelayController.php`, `includes/Api/AiResponseDelayResponseValidator.php`, `src/ai-response-delay-client.js`, `src/ai-response-delay-controller.js`, `src/recovery-settings/ai-response-delay-panel.js`. Modify `includes/Runtime.php`, `includes/Api/ModaApiClient.php`, `src/page/controller-factory.js`, page state/render plumbing, and `src/recovery-settings/recovery-settings-screen.js`; add focused PHP/JS tests. Do not change the existing RecoveryPolicyController contract.


## Out of Scope

No unrelated architecture changes, new standalone chat service, per-user timer jobs, invented provider error explanations, or updates to `docs/decisions/**/_index.md`. No implementation outside the assigned repository.


## Requirements

- WP REST proxy path exactly `/wp-json/moda-interact/v1/merchant/ai-response-delay` GET/PUT, with `manage_woocommerce` permission and valid WP REST nonce. Server PHP reads trusted `InstallationStore`, checks current canonical SiteIdentity against stored installation, sends installation credentials through existing ModaApiClient server-to-server and rechecks installation state after response. Browser never sends bearer token, shop ID, credentials or backend URL.
- Validate the Shared v1 wire exactly in PHP: read keys `schemaVersion,revision,aiResponseDelayMinutes`; update keys `schemaVersion,expectedRevision,aiResponseDelayMinutes`; min0 max30 integer with `is_int`, `UNCONFIGURED`/UTC ISO revision, reject unknown keys; status mapping follows existing proxy. No introducing a distinct PHP business policy or caching a supposedly updated value on an ambiguous network failure.
- UI labeled 0–30 integer input, translated through existing plugin gettext text-domain, clear "Human replies are immediate" guidance, separate Save from recovery delay, pending/conflict state and read-after-save. On reload reads saved canonical setting; `Cache-Control: private, no-store`.
- Existing per-merchant Take Over and Reply composer continues to work unchanged; this setting has zero effect on the PHP/runtime human dispatch.


## Work Items

- [ ] Add PHP proxy/auth/validator + ModaApiClient method; register and route.
- [ ] Add JS controller/client/panel and recovery settings page integration.
- [ ] Test WP privilege/nonce, cross-site changed URL, installation rotation, type bounds, no-op/revision conflict, server failure, and HUMAN bypass UI copy.


## Interfaces / Contracts

Exact Shared v1 GET and PUT examples from parent architecture. Woo PHP may validate the same wire shape, but must not invent another Node/Zod contract; the hosted API consumes the published schema.


## Dependencies

- ARCH-054-API-001


## Enables

None


## Acceptance Criteria

- [ ] Only authorised WP merchant can read/write their own shop setting; all integers 0–30 supported, floats/strings rejected at server boundaries.
- [ ] No direct DB/Redis access, no credential in browser and no change to existing recovery settings or human send admission.


## Validation

- [ ] `npm run test:php`; `npm run test:js:unit`; `npm run i18n:verify:20`; `npm run lint:js`; `npm run lint:php`; `npm run build`; `git diff --check`.


## Stop Condition

After all required Work Items, Acceptance Criteria and Validation are complete, update Completion Report, set status to `review`, return control to `moda_architect` and **STOP**. Do not implement dependent tasks. Publication tasks do not rerun accepted implementation validation.


## Implementation Notes

Implement only the identified repository-owned changes; preserve original provider/SDK errors in shared structured logs and rethrow failures to the owning retry/admission boundary.


## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

Not Run

### Deviation / Assumptions / Unresolved Issues / Architectural Concerns

None

### Worktree and Git Evidence

Not materialised; implementing agent must record launcher-prepared dedicated parent/implementation worktree paths, start-of-attempt sync, branch SHAs, submodule pins and cleanup.


## Architect Review

### Review Status

Pending

### Review Notes

None

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

None
