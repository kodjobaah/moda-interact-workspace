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
  - ARCH-035-API-013
enables:
  - ARCH-040-WOOCOMMERCE-002
created: 2026-10-14
updated: 2026-10-17
---

# ARCH-040-WOOCOMMERCE-001 — Proxy enriched Woo recovery detail reads through WordPress REST

## Architecture

Initiative: `ARCH-040`. Architecture document: `docs/architecture/ARCH-040-merchant-customer-conversations-human-handover.md`. Coordinator: `moda_architect`. **Portable definition only; defined but not materialised, no branch/commit/worktree.**

## Objective

Extend the existing Woo WordPress REST **read-only** recovery-detail facade to pass through basket and AI/HUMAN control/restriction data from API-002. The control/send/status command proxies belong to WOOCOMMERCE-003, so this task does not wait for API-003/004.

## Context

Woo merchant chooses a recovery from the existing native `Recoveries` list; ARCH-035 Woo detail shell and `ARCH-035-API-013` already define read endpoints. API-002 enriches the same read response. API-003/004 own conversation-ID keyed writes and command status. WordPress PHP alone holds connected installation credentials.

## Scope

- Use existing WordPress REST recovery-detail routes/client to expose the enriched authenticated `GET /v1/merchant/recoveries/:recoveryId`, and preserve existing `/messages` + `/related` reads.
- Defer the authenticated control/send/status WordPress REST proxy endpoints to WOOCOMMERCE-003; they are out of scope here.
- Preserve two-stage WooCommerce > Moda Interact navigation and existing recovery-detail REST client, not another menu/list.

## Out of Scope

- No new `GET /v1/merchant/conversations` inbox/detail/message facade or WordPress conversations route/menu.
- No merchant/staff account system, direct WP/PHP access to Moda database, Meta credentials or Shopify admin calls.
- No `_index.md` changes.

## Requirements

- **Read-only boundary:** use only the existing ARCH-035 recovery detail `/v1/merchant/recoveries/:id` / messages / related routes enriched by API-002; do not implement POST control/send or GET command-status routes in this task. No API-003/004 prerequisite. Preserve the existing WordPress REST route and JS/PHP separation.

1. Require existing logged-in WP `manage_woocommerce` capability and valid REST nonce for **each** browser-to-WordPress read; authenticate PHP-to-hosted with existing installation ID and server-held Bearer credential, never a browser-selected shopId. Fail closed when disconnected/rotated.
2. For reads, reuse the ARCH-035 Woo recovery detail HTTP route, returning basket snapshot, conversation ID/mode/revision/follow-up and existing message/related pages with no transformations that lose sender identity/decimal precision. Do not create or call new generic conversations GET endpoints.
3. For reads only, preserve the existing detail/message/related REST response and safe upstream error/status forwarding; command-specific errors and routes are the responsibility of WOOCOMMERCE-003.
4. Keep PHP/JS boundary isolated, sanitize incoming data and unexpected upstream payloads; no installation access token/secret to JS or logs; preserve no-store and bounded timeouts/retries.
5. Reuse installed Woo recovery detail client/controller and explicit WordPress admin navigation rather than adding a second React inbox.

### Restriction transport

- Preserve authenticated Woo hosted API `humanMessagingStatus`/`humanMessagingAllowed` in the recovery detail projection and typed command errors. Never add a WordPress-local authoritative feature toggle or locally trust a browser-provided ACTIVE state.
- Pass through only the public ACTIVE/SUSPENDED read status without internal Admin notes. The WordPress browser has no Moda database/provider credentials. Typed send-command moderation outcomes are handled later by WOOCOMMERCE-003.


## Work Items

- [ ] Extend existing WordPress recovery-detail REST client for enriched API-002 DTO (basket + control).
- [ ] Preserve the existing WordPress read-only nonce/capability and installation credential checks; **defer** command proxy actions to WOOCOMMERCE-003.
- [ ] Preserve original recovery-detail message/related proxies and do not add generic GET conversations routes.
- [ ] Add WP REST/PHP tests for reads, disconnect, nonce/role denial, bad IDs, safe upstream error/status and token privacy; write-command proxy tests belong to WOOCOMMERCE-003.

## Interfaces / Contracts

Woo browser -> WordPress recovery-detail REST facade -> hosted Woo `GET /v1/merchant/recoveries/:id`/`messages`/`related` (ARCH-035+API-002) only. Existing Woo installation authentication; command endpoints belong to WOOCOMMERCE-003. No Shopify host API integration or extra shared DTO.

## Dependencies

- ARCH-040-API-002
- ARCH-035-API-013

## Enables

- ARCH-040-WOOCOMMERCE-002

## Acceptance Criteria

- [ ] Existing Woo Recoveries navigation and detail reads continue working with basket/control data and without adding a Conversations inbox.
- [ ] Valid WordPress capability/nonce + active installation required for reads; no direct browser Moda API credentials or access to other shops.
- [ ] No human send/takeover request path is added in this read-only task; later command requests use only approved hosted endpoints in WOOCOMMERCE-003.

## Validation

- [ ] WordPress REST/PHPUnit **read** auth and error mapping tests.
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
