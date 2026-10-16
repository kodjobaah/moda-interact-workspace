---
id: ARCH-035-WOOCOMMERCE-013
architecture_id: ARCH-035
title: Build native Woo Recovery Detail UI shell (Stage 1)
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 40
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-035-WOOCOMMERCE-009
enables:
  - ARCH-035-WOOCOMMERCE-010
  - ARCH-035-SYSTEM-TEST-001
created: 2026-10-11
updated: 2026-10-16
---

# ARCH-035-WOOCOMMERCE-013: Build native Woo Recovery Detail UI shell (Stage 1)

## Architecture

- Architecture ID: `ARCH-035`
- Architecture document: `docs/architecture/ARCH-035-woocommerce-merchant-experience-parity.md`
- Coordinator: `moda_architect`
- Source baseline: `moda-interact-workspace(20261011-192347).zip`; portable definition, not a materialised parent/implementation task branch.

## Objective

Build an independently reviewable, responsive **Recovery Detail UI shell** matching the Shopify visual reference. Stage 1 delivers real list-to-detail/back navigation and modular presentation components, but no detail API calls or simulated production records.

## Context

The reference is Shopify `app/routes/app/recovery-detail/RecoveryDetail.tsx` with customer header, conversation, collapsible checkout context/milestones and independently paginated related recoveries. Woo's previously implemented ARCH-035-WOOCOMMERCE-009 list uses a paginated hosted **list-only** API. Preserve the exact live WordPress navigation: `WooCommerce > Moda Interact` enters the experience; top-level `Moda Interact > Recoveries` remains the active submenu for both list and detail.

Developer-agreed three stages:

1. **Stage 1 (current task):** shell, navigation, fixture-only presentation tests and production unavailable states.
2. **Stage 2 (new separately scoped API task after shell approval):** authenticated detail summary, bounded/cursor-paged conversation and related-recovery read contracts if absent.
3. **Stage 3 (future Woo integration task):** privileged WordPress REST proxy and modular React controller/hooks to populate the approved shell.

No later stage may be hidden inside this shell implementation.

## Scope

- React shell with distinct customer/summary header, conversation and safe message renderer, native expandable checkout context, milestones and separately paginated related-recovery section.
- Keep the existing WordPress `page=moda-interact-recoveries` menu slug and use an allowlisted `recoveryId` query parameter for detail. Back to list preserves applied `from`, `to`, `q`, `status`, `page` and `pageSize`; encode the list page as `recoveryPage` so it does not conflict with WordPress's `page`.
- Style Shopify-equivalent two-column desktop and single-column tablet/mobile layout; accessible labels, buttons, focus and keyboard behaviour.
- Add test-only populated message/related fixtures and production unavailable/loading/empty/error UI states. Never produce fake merchant records.
- Extend native gettext/PO translations using reviewed Shopify equivalents for the full 20 UI languages.

## Out of Scope

- Hosted detail API implementation, WordPress detail REST proxy, real detail fetches or live transcript/related pagination (future Stages 2/3).
- New Database/Shared/Background work, order ingress, merchant writes, coupons, billing and Shopify code changes.
- Native WordPress navigation replacement, extra menus, React tabs, production fixture data, external detail URLs.
- Any `docs/decisions/**/_index.md` updates before developer-approved reconciliation.

## Requirements

- Use WordPress Admin as the shell, React via @wordpress/element for content, native gettext/i18n, and existing Woo installation, nonce, capability and disconnect protections.
- Source alignment, accessibility, section placement and state meanings must follow the Shopify reference files named here; only platform chrome/provider-specific actions may differ.
- UI composition and state/transport must be modular; do not enlarge src/page.js or create new catch-all files (target <=200 lines, maximum 300 new production lines per file).
- The assigned task is **UI-only**: no DB schema/migrations, Shared contracts, hosted API implementation, background jobs, event ingestion, order reconciliation, coupon-provenance, payment-provider commands or business-rule changes.
- Do not invent new endpoints or use Shopify authentication from WordPress. The browser may use only an already-approved privileged WordPress API proxy; server-side Woo integration must remain within existing accepted contracts.
- A missing external dependency must not be silently faked. Fixture data are for tests/storyboards only; production shows honest unavailable/disabled states while preserving the page design.
- State requests are single-flight or otherwise protected against duplicate clicks, and stale callbacks after disconnect/credential rotation cannot modify current UI.

## Work Items

- [ ] Map the Shopify detail page to existing WordPress page and Woo list data.
- [ ] Build bounded modular React summary, conversation, message, milestones and related-recovery components.
- [ ] Implement valid recovery ID URL routing and restore applied list filters/page on back/refresh.
- [ ] Test safe HTTP(S) linkification, invalid IDs, unavailable/loading/empty/error and independent disabled pagination controls.
- [ ] Add 20-language translations, desktop/tablet/mobile responsive styles and focused tests.
- [ ] Report missing detail read APIs for Stage 2; no live data integration in this patch.

## Interfaces / Contracts

- Existing `GET /v1/merchant/recoveries` is the accepted **paginated list** read; it does not supply detail, conversation or related data.
- Native detail URL: `admin.php?page=moda-interact-recoveries&recoveryId=<validated-id>`, with allowlisted `from`, `to`, `q`, `status`, `recoveryPage`, `pageSize` for return navigation; omit all other inputs.
- Stage 1 message/summary/related objects are **test-only presentation props**, not new hosted-service DTOs. No new REST route is introduced.
- Future API reads must be shop-scoped, bounded, independently paginated and revalidated in a future task.

## Dependencies

- `ARCH-035-WOOCOMMERCE-009` (architect-accepted Complete)

## Enables

- `ARCH-035-WOOCOMMERCE-010`
- `ARCH-035-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Customer name opens detail while WordPress's existing Recoveries menu remains highlighted; Back to recoveries restores applied filters and the server page after full document navigation/reload.
- [ ] Shopify-like desktop 2-column detail, mobile single-column context below conversation without horizontal overflow.
- [ ] Read-only message content rendered safely; only credential-free HTTP(S) links become anchors; invalid recovery IDs show safe unavailable state.
- [ ] Independent conversation and related pagination, refresh, loading, error and empty states are presentation-testable, but all production actions remain disabled without an approved detail API.
- [ ] No real customer data is fabricated from list IDs; no direct browser-to-hosted API requests, no new WordPress/hosted routes or schema changes.
- [ ] Twenty-language native gettext remains complete; other WordPress merchant screens and two-stage menus are unchanged.

## Validation

- [ ] `npm run test:i18n` and `npm run i18n:verify:20`.
- [ ] Focused Recovery Detail navigation, safe-link, fixture and state tests and existing Recoveries list/controller regressions; `npm run test:js`.
- [ ] `npm run lint:js`, `npm run lint:css`, `npm run build`, `npm run plugin-zip`.
- [ ] LocalWP desktop/tablet/mobile screenshots, native list/detail/back/refresh behaviour and disabled data states.
- [ ] `git apply --check --whitespace=error-all` against verified Attempts 1–5; `git diff --check` and actual worktree/launcher evidence if materialised.
- [ ] Record that details/conversation/related reads remain Stage 2 dependencies.

## Stop Condition

When Work Items, UI-only Acceptance Criteria and required validation are complete, finish the Completion Report, set task to `review` and STOP for moda_architect. Do not implement deferred cross-repository capabilities. Report unavailable validation accurately.

## Implementation Notes

One task, one independent outcome: **Stage 1 shell only**. The live WordPress `page` query parameter is reserved for its menu slug; use `recoveryPage` for list pagination in links. Keep components small and separate presentation/route helpers from any later API client. No monolithic `page.js`, no additional native menu. Stop after shell review and return to architect.

## ASCII Page Design

Desktop — reference layout (no illustrative records included in production):

```text
+------------------------------------------------------------------------------------+
| WP Admin: Moda Interact > Recoveries [active]                                     |
+------------------------------------------------------------------------------------+
| < Back to recoveries (dates / search / status / page retained)                    |
|                                                                                    |
| Recovery details             Checkout value      Status          Started          |
| [Customer/Unavailable]       [Value/Unavailable] [Status/--]     [Date/--]        |
| [Email if known]                                                                   |
+----------------------------------------------------+-------------------------------+
| Conversation                             [Refresh] | v Checkout context            |
| Read-only conversation history.                    | Milestones                    |
| Time zone: [store TZ / unavailable]                | [Known events only]           |
| [Previous] [Jump to latest] [Next]                 |-------------------------------|
|   +------------------------------------------+     | Related recoveries  [Refresh] |
|   | [Assistant bubble + receipt if known]    |     | [Related checkout rows]       |
|   +------------------------------------------+     | [Previous]          [Next]    |
| +---------------------------------------+          +-------------------------------+
| | [Customer bubble]                     |                                         |
| +---------------------------------------+                                         |
+------------------------------------------------------------------------------------+
```

Mobile — stack panels; keep independent pagination controls reachable:

```text
+--------------------------------------+
| < Back to recoveries                 |
| Recovery details                     |
| [Customer]                            |
| Checkout value / Status / Started    |
+--------------------------------------+
| Conversation                [Refresh] |
| [Previous] [Jump latest] [Next]      |
| [Safe message bubbles]               |
+--------------------------------------+
| v Checkout context                   |
| Milestones (known only)              |
| Related recoveries         [Refresh] |
| [Previous]                [Next]     |
+--------------------------------------+
```

Production before Stage 2/3:

```text
< Back to recoveries
Recovery details      Value: Unavailable  Status: Unavailable
[This section is not yet available for WooCommerce.]
Conversation [Refresh disabled] [Previous disabled] [Jump latest disabled] [Next disabled]
[This section is not yet available for WooCommerce.]
Checkout context / Milestones: unavailable
Related recoveries [Refresh/Previous/Next disabled]
```

Use populated data **only in isolated tests**. A disconnected read model is not a verified empty conversation.

## Completion Report

### Status

Not Started.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

This definition is portable and has not been claimed. Any missing hosted API capability is external to ARCH-035 and may require a separate architecture.

### Unresolved Issues

No backend capability is asserted by this UI-only task. Document discovered API gaps in the completion report.

### Architectural Concerns

None reported at definition time.

## Architect Review

### Review Status

Accepted — retrospective code-based review, 16 October 2026.

### Review Notes

Recovery Detail screen and list-to-detail/back navigation, separately paginated conversation and related records, safe rendering and real WordPress read adapter.

This is a **retrospective, source-code-based architectural reconciliation** against the developer-provided 2026-10-16 10:58:55 workspace ZIP. The source snapshot is not the historical paired task worktrees or Git branches; an original launcher packet, accepted task commit, Completion Report validation and LocalWP run cannot be reconstructed from it. Retain `attempt: 0` and the original developer/agent Completion Report; no historical execution claim or test pass is manufactured.

### Reviewed Files

- `moda-interact-woocommerce/src/recoveries/detail/{recovery-detail-screen.js,recovery-detail-controller.js,detail-navigation.js}`
- `moda-interact-woocommerce/src/recoveries/detail/{conversation,context,api,hooks}/`
- `moda-interact-woocommerce/includes/Rest/RecoveryDetailController.php`
- `moda-interact-woocommerce/tests/js/{recovery-detail-shell.test.js,recovery-detail-integration.test.js}`

### Validation Reviewed

This session directly passed `npm run test:i18n` (28 tests) and `npm run i18n:verify:20` (332 current PHP/React gettext strings, 19 translation packs / 20 canonical locales). Related Woo PHP controller and native navigation files passed `php -l`. JS component/integration tests and API TypeScript test cases were inspected as source, but `node_modules` are absent from the ZIP and their execution, PHP integration, LocalWP browser evidence, production build, package ZIP, disposable PostgreSQL proof and launcher worktree verification were **not** run in this session.

### Architecture Conformance

The inspected implementation provides the task's bounded capability and uses the approved architecture/repository boundary. The source-based reconciliation is not a claim of unobserved runtime validation, task worktree isolation or release certification.

### Follow-up

Continue normal work only for other, incomplete ARCH-035 tasks. The terminal SYSTEM-TEST-001 remains blocked until every required UI implementation is Complete.
