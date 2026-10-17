---
id: ARCH-040-WOOCOMMERCE-001
architecture_id: ARCH-040
title: Proxy enriched Woo recovery detail and human commands through WordPress REST
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 40
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-040-API-002
  - ARCH-040-API-003
  - ARCH-040-API-004
  - ARCH-035-API-013
enables:
  - ARCH-040-WOOCOMMERCE-002
created: 2026-10-14
updated: 2026-10-16
---

# ARCH-040-WOOCOMMERCE-001 — Proxy enriched Woo recovery detail and human commands through WordPress REST

## Architecture

Initiative: `ARCH-040`. Architecture document: `docs/architecture/ARCH-040-merchant-customer-conversations-human-handover.md`. Coordinator: `moda_architect`. **Portable definition only; defined but not materialised, no branch/commit/worktree.**

## Objective

Expose existing Woo Recovery Detail **plus augmented basket/control data**, and proxy human-control/send operations through trusted WordPress REST. Do not add a separate Woo conversations inbox facade.

## Context

Woo merchant chooses a recovery from the existing native `Recoveries` list; ARCH-035 Woo detail shell and `ARCH-035-API-013` already define read endpoints. API-002 enriches the same read response. API-003/004 own conversation-ID keyed writes and command status. WordPress PHP alone holds connected installation credentials.

## Scope

- Use existing WordPress REST recovery-detail routes/client to expose the enriched authenticated `GET /v1/merchant/recoveries/:recoveryId`, and preserve existing `/messages` + `/related` reads.
- Provide secure WordPress REST proxy for `POST /v1/merchant/conversations/:id/control`, `POST .../:id/messages`, and `GET .../:id/send-commands/:commandId`.
- Preserve two-stage WooCommerce > Moda Interact navigation and existing recovery-detail REST client, not another menu/list.

## Out of Scope

- No new `GET /v1/merchant/conversations` inbox/detail/message facade or WordPress conversations route/menu.
- No merchant/staff account system, direct WP/PHP access to Moda database, Meta credentials or Shopify admin calls.
- No `_index.md` changes.

## Requirements

1. Require existing logged-in WP `manage_woocommerce` capability and valid REST nonce for **each** browser-to-WordPress read/command; authenticate PHP-to-hosted with existing installation ID and server-held Bearer credential, never a browser-selected shopId. Fail closed when disconnected/rotated.
2. For reads, reuse the ARCH-035 Woo recovery detail HTTP route, returning basket snapshot, conversation ID/mode/revision/follow-up and existing message/related pages with no transformations that lose sender identity/decimal precision. Do not create or call new generic conversations GET endpoints.
3. For commands only, proxy API-003/004's conversation ID routes, forwarding allowlisted expected revision/idempotency/text/approved template data unchanged and retaining upstream status codes: accepted/replay, stale conflict, window expired, follow-up used, 401/404/5xx.
4. Keep PHP/JS boundary isolated, sanitize incoming data and unexpected upstream payloads; no installation access token/secret to JS or logs; preserve no-store and bounded timeouts/retries.
5. Reuse installed Woo recovery detail client/controller and explicit WordPress admin navigation rather than adding a second React inbox.

### Restriction transport

- Preserve authenticated Woo hosted API `humanMessagingStatus`/`humanMessagingAllowed` in the recovery detail projection and typed command errors. Never add a WordPress-local authoritative feature toggle or locally trust a browser-provided ACTIVE state.
- Proxy `403 human_messaging_suspended` and safe command-state moderation outcomes without converting them into success, losing server response codes or leaking internal Admin notes. The WordPress browser still has no Moda database/provider credentials.


## Work Items

- [ ] Extend existing WordPress recovery-detail REST client for enriched API-002 DTO (basket + control).
- [ ] Add control/send/command-status REST proxy actions with nonce/capability and installation credential checks.
- [ ] Preserve original recovery-detail message/related proxies and do not add generic GET conversations routes.
- [ ] Add WP REST/PHP tests for readonly/command, disconnect, nonce/role denial, bad IDs, safe upstream error/status and token privacy.

## Interfaces / Contracts

Woo browser -> WordPress recovery-detail REST facade -> hosted Woo `GET /v1/merchant/recoveries/:id`/`messages`/`related` (ARCH-035+API-002), and **only command endpoints** on `/v1/merchant/conversations/:conversationId` (API-003/004). Existing Woo installation authentication; no Shopify host API integration or extra shared DTO.

## Dependencies

- ARCH-040-API-002
- ARCH-040-API-003
- ARCH-040-API-004
- ARCH-035-API-013

## Enables

- ARCH-040-WOOCOMMERCE-002

## Acceptance Criteria

- [ ] Existing Woo Recoveries navigation and detail reads continue working with basket/control data and without adding a Conversations inbox.
- [ ] Valid WordPress capability/nonce + active installation required for all reads/commands; no direct browser Moda API credentials or access to other shops.
- [ ] Human send and takeover requests reach only approved hosted command endpoints; no send performed in WordPress PHP.

## Validation

- [ ] WordPress REST/PHPUnit read/command auth and error mapping tests.
- [ ] Hosted API contract fixture checks, plugin build/ZIP, `git diff --check` and canonical worktree evidence.

## Implementation Notes

Keep current ARCH-035 recovery-detail clients. Do not rebuild the Woo Recoveries list or mutate pending ARCH-035 code outside the approved dependency.

## Stop Condition

After only this task's Work Items, Acceptance Criteria and Validation are complete, set status `review`, record Completion Report and return to moda_architect. STOP.

## Completion Report

### Status
Not Started

### Files Changed
None.

### Work Completed
None.

### Validation Results
Not run.

### Deviations
None.

### Assumptions
The architecture is proposed; implementation starts only after agreed/materialised task definition.

### Unresolved Issues
None recorded at definition time.

### Architectural Concerns
Return newly discovered contract or ownership gaps to moda_architect.

## Architect Review

### Review Status
Pending

### Review Notes
Not reviewed.

### Reviewed Files
None.

### Validation Reviewed
None.

### Architecture Conformance
Pending.

### Follow-up
None.
