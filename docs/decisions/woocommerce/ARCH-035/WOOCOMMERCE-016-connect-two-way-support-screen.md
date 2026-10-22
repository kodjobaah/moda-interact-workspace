---
id: ARCH-035-WOOCOMMERCE-016
architecture_id: ARCH-035
title: Connect native Woo Support screen to hosted two-way Support
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: in_progress
priority: 32
executor: developer
claimed_at: 2026-10-22T00:19:37Z
attempt: 1
depends_on:
  - ARCH-035-API-020
enables:
  - ARCH-035-SYSTEM-TEST-005
  - ARCH-046-WOOCOMMERCE-007
  - ARCH-046-SYSTEM-TEST-002
created: 2026-10-21
updated: 2026-10-22
---

# ARCH-035-WOOCOMMERCE-016: Connect native Woo Support screen to hosted two-way Support

## Architecture

Architecture ID: `ARCH-035`. Architecture document: `docs/architecture/ARCH-035-woocommerce-merchant-experience-parity.md`. Coordinator: `moda_architect`.

**Lifecycle:** Architect definition was materialised on the canonical parent task branch after dependency `ARCH-035-API-020` became Complete. The developer explicitly requested takeover from the default agent execution mode; the canonical launcher will prepare/synchronize both worktrees and claim the first developer attempt.

## Objective

Enable the already-implemented WooCommerce merchant Support thread and composer against the approved two-way hosted Support API, using a privileged WordPress REST proxy.

## Context

`ARCH-035-WOOCOMMERCE-001` is Complete as a UI task, but `src/support/support-client.js` still reports all three capabilities unavailable. `ARCH-035-API-020` provides the missing authoritative read, compose and mark-read operations. ARCH-046 SYSTEM notices must appear in that same conversation, not a separate view.

## Scope

- Extend the existing Woo PHP ModaApiClient and privileged WP REST controller with three operations corresponding to API-020.
- Replace the unavailable-only Support client with real list/send/markRead methods and connect it to the existing controller/UI.
- Preserve existing native WordPress Support navigation, translations, thread/component separation and Shopify-parity styling.
- Add focused PHP proxy/authentication and JS async controller/network tests, plus 20-locale build verification.

## Out of Scope

- No new WordPress Support data store, new top-level menu, hosted API changes, schemas or background translation processing.
- Do not implement customer WhatsApp messaging, Shopify refunds, platform-admin responses or ARCH-046 merchant no-contact action (owned by WOOCOMMERCE-007).

## Requirements

- Every WordPress browser request requires capability `manage_woocommerce` or the current narrower approved merchant-admin capability plus a verified REST nonce. PHP obtains current authenticated installation credentials server-side and calls hosted API over HTTPS; never expose credentials in JS, browser HTML or logs.
- Render paginated `MERCHANT`, `ADMINISTRATIVE` and `SYSTEM` records, original/translated switch, accurate read/unread badges, and actionable only validated provider-safe system links.
- Use stable UUID actionId per attempted send and reuse on safe retries; persist the actionId only for pending client retry, not as authoritative message storage. Double-click prevention and only confirm send upon authenticated hosted ACK.
- Disable send/read/markRead on disconnected, revoked, stale or denied installation; abort or ignore in-flight operations after disconnect/reconnect, credential rotation and unmount. Provide clear permission/error/unavailable states.
- Keep 20 administrator UI locales with WordPress admin preference and site fallback; language of customer conversations and Shop default remain unchanged.
- No locally fabricated data or success, and no direct call to Shopify app routes.

## Work Items

- [ ] [ ] Inspect existing `src/support` controller and WP REST/API client code; map API-020 response/error contracts.
- [ ] [ ] Wire privileged PHP proxy and strict plugin-side transport validation.
- [ ] [ ] Enable real read, send and markRead in separate `support-client`/controller modules; retain fixture-only test seams.
- [ ] [ ] Test disconnected, stale response, nonce denial, invalid body, duplicate send, translated reply and SYSTEM notice read path.
- [ ] [ ] Run WordPress PHP/JS and 20-language tooling, build and ZIP.

## Interfaces / Contracts

- Consumes API-owned three-route Support v1 contract of `ARCH-035-API-020`; hosted API derives tenant from Woo installation.
- Browser → nonce/capability-checked WordPress REST → authenticated PHP ModaApiClient → hosted API → existing PostgreSQL Support thread.

## Dependencies

- `ARCH-035-API-020` (must be architect-accepted Complete)

## Enables

- `ARCH-035-SYSTEM-TEST-005`
- `ARCH-046-WOOCOMMERCE-007`
- `ARCH-046-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] Connected merchant can read paginated Support history, send a message and see subsequent Moda admin reply in the same thread.
- [ ] System/ARCH-046 consent notices appear among ordinary Support messages; existing translated/original and read/unread flows operate.
- [ ] Non-admin, bad nonce, another tenant, stale installation and malformed API responses fail closed without presenting fake success.
- [ ] No duplicate sends on double-click/network retry; all 20 locale assets pass strict verification.
- [ ] Existing Woo onboarding, Billing, Recoveries and Shopify Support unaffected.

## Validation

- [ ] Run focused JS Support client/controller/UI and PHPUnit REST nonce/capability/credential tests, plus negative disconnect/reconnect tests.
- [ ] Run project-declared `npm run test:js`, `npm run test:i18n`, `npm run i18n:verify:20`, `npm run test:php`, `npm run build`, `npm run plugin-zip` and `git diff --check` as available.
- [ ] Record developer manual LocalWP checkout/connected Support verification separately from repository agent automated acceptance; do not invent manual evidence.

## Stop Condition

After all required Work Items, Acceptance Criteria and task-specific Validation are satisfied, update the task Completion Report and `status: review`, return to `moda_architect` and STOP. Do not perform dependent tasks, create new task implementation worktrees, merge or push main, or change `docs/decisions/**/_index.md`.

## Implementation Notes

Retain current Support component boundaries; do not enlarge a catch-all page module. ARCH-046-WOOCOMMERCE-007 may add an independent merchant no-contact action later; it must not be bundled into the Support messaging implementation.

Start with `scripts/start-agent-task.py --prepare` through the normal `/moda-task` path. The prepared packet proves canonical parent/implementation worktree identity, synchronization and submodule state; record that packet in the Completion Report. Re-read the latest task and architect review before claiming. Use actual repository scripts. The architect in this externally supplied ZIP session has not created any Git branches or worktrees.

## Completion Report

### Status

In Progress — Attempt 1 claimed by developer at 2026-10-22T00:19:37Z. Attempt 0 review history is preserved below.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

Inspect current canonical developer workspace when materialising; this source ZIP may lag task branches.

### Unresolved Issues

None identified at definition time.

### Architectural Concerns

None identified at definition time.

## Architect Review

### Review Status

Pending — no implementation reviewed.

### Review Notes

Definition approved for handoff; no implementation has been accepted.

## Developer Takeover Amendment — 2026-10-22

The developer explicitly invoked `/moda_developer_create ARCH-035-WOOCOMMERCE-016` for this ready agent-owned task. Execution and completion ownership are transferred to the developer (`execution_mode: developer`, `completion_mode: developer`); logical ownership remains `assigned_agent: moda_woocommerce`, and task scope, dependency, acceptance criteria, and validation requirements are unchanged. The canonical launcher will record the developer claim after worktree preparation and dependency verification.
