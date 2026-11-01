---
id: ARCH-047-SYSTEM-TEST-001
architecture_id: ARCH-047
title: Certify Moda-authored multilingual recovery templates and conversation wrappers
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 80
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-047-DATABASE-001
  - ARCH-047-ADMIN-003
  - ARCH-047-ADMIN-004
  - ARCH-047-ADMIN-005
  - ARCH-047-ADMIN-006
  - ARCH-047-ADMIN-007
  - ARCH-047-ADMIN-008
  - ARCH-047-SHARED-002
  - ARCH-047-MESSAGING-001
  - ARCH-047-BACKGROUND-001
  - ARCH-047-BACKGROUND-002
  - ARCH-047-BACKGROUND-003
  - ARCH-047-BACKGROUND-004
  - ARCH-047-BACKGROUND-005
  - ARCH-047-BACKGROUND-006
  - ARCH-047-BACKGROUND-007
  - ARCH-047-BACKGROUND-008
  - ARCH-047-BACKGROUND-009
  - ARCH-047-SHOPIFY-001
  - ARCH-047-API-001
  - ARCH-047-WOOCOMMERCE-001
enables: []
created: 2026-10-23
updated: 2026-10-26
---

# Certify Moda-authored multilingual recovery templates and conversation wrappers

## Architecture

`ARCH-047` — `docs/architecture/ARCH-047-admin-managed-whatsapp-template-catalogue.md`; coordinator `moda_architect`. This supersedes the former import-and-copy testing **scope**, but retains the canonical `SYSTEM-TEST-001` task identity and its terminal system-validation role.

## Objective

Independently certify the real integrated Moda Admin → Background/Messaging → PostgreSQL → Meta workflow for immutable centrally authored, multilingual recovery templates and checkout-associated AI/human response wrappers, including failure safety, merchant-facing parity and **absence of superseded sending code**.

## Context

The initial ARCH-047 test specified externally authored Meta imports, refreshed snapshots, and shop-to-shop copying. Those behaviours are forbidden. There are now six recovery purposes, 20 translation locales, per-language provider approvals, Admin publication, a DB-backed final provider fence, and prepared AI/HUMAN wrappers. The completed BG004 offer resolver contains default **unavailable** Shopify and Woo checkout-specific eligibility adapters: a passing No Offer fallback is not proof that positive discounts are supported. Shopify and hosted Woo admission still contained legacy `purpose: "checkout-recovery"` filters in the source snapshot, and the Woo UI hard-disabled template selection. Separate owning tasks must remove those gaps before certification.

## Scope

Implement isolated black-box scenarios in `moda-interact-system-test`, with tests split into fixtures, executors, assertions, orchestration and data helpers; avoid oversized catch-all files. Exercise real authenticated service boundaries with disposable PostgreSQL/Redis where required and controlled Meta/translation-provider emulators. Include representative Shopify and WooCommerce shops, both recovery stages, all six purposes where independently verifiable, correct WABA/languages and a second shop to test isolation.

## Out of Scope

- No creating/editing application code, provider SDKs, schema/migrations or task implementations in system-test.
- No external Meta-template import, same-ID in-place content editing, shop-to-shop assignment copying, or unsupported provider checkout mutations.
- No external R2 image-header certification before ARCH-049 READY media is available; validate text-only flow and media-unavailable fail-closed independently of the separate media initiative.

## Requirements

**R1 — Source and translations.** Through authenticated Admin author a new English AST, immutable-save and Clone as New, persist keyed translation segments and protected placeholders, process 19 target languages with retry/partial failure, review, compile and persist frozen text/body/button mappings. A malformed/lost/duplicated placeholder fails before Meta submission. No old template is mutated.

**R2 — Meta lifecycle.** Submit only Admin-created compiled components, each WABA/language separately; verify recorded provider ID/status, approved/pending/rejected cases, provider drift, duplicate and repeating approval transitions through Messaging → `whatsapp-events` BullMQ → BG003 → PostgreSQL. A PAUSED/DISABLED observation immediately makes registration unavailable before a failed Meta GET, and stale provider verification over 60 minutes blocks final send. No imported/external registration is adopted.

**R3 — Publication and selection.** One, selected and all eligible shop publication with per-shop/per-language targets, true old/new comparison, override confirmation, out-of-scope shop protection, idempotency and concurrency races. No template becomes active merely because Meta approved it.

**R4 — Automated initial and follow-up.** Shopify and Woo initial plus scheduled follow-up must use BG004/BG001 six-purpose selection, frozen params and same authoritative late send fence. Exercise trustable shop name/checkout CTA and absent READY image no-send. Verify language fallback, prior-offer consistency, one sequence-two, order-completion suppression, consent/STOP, moderation, credit compensation and recipient isolation.

**R5 — Discount capability is an explicit gate.** Run a no-live-evaluator fixture for both Shopify and Woo: FIXED/AI safely produce `NO_OFFER` and never claim a verified saving or add/apply a coupon. Run separately injected, independently validated checkout-specific provider-evidence scenarios proving CODE and AUTOMATIC selection/expiry/currency/fingerprint, as available. **Do not certify live positive-offer support** merely from injected fixtures or the completed BG004 status. If no approved provider-read adapter exists in production, record a named **blocking functional gap** and keep full six-purpose certification blocked until an architect-defined owner closes it. Do not waive or relabel this as passed.

**R6 — Merchant interfaces and human/AI wrappers.** Shopify merchant's current Follow-up picker/admission and Woo API/plugin authorised list must expose only published approved `FOLLOW_UP_*` variants (no legacy `checkout-recovery`), respect WABA/language, human control, rolling window, sequence-two due/used and server-side parameters; forged template parameters/variant IDs are rejected. In-window HUMAN and AI responses are each wrapped exactly once, use valid checkout context and undergo whole-message moderation. Outside the window no free-form wrapper is sent.

**R7 — Delete obsolete runtime code.** Inspect the actual integrated source after BG006/BG007 and merchant-interface tasks: ensure no active old selector/category verifier/API per-send Meta category GET, deprecated `purpose: "checkout-recovery"` server allowlists, obsolete imported-template UI, or hardcoded Woo `canTemplate: false` path is reachable. All production references removed where superseded; do not delete unrelated legacy provider safeguards still used by other approved paths. Obsolete tests must be replaced with authoritative regression tests, not merely skipped.

**R8 — Deployment/evidence boundaries.** System Test begins only after all formal `depends_on` implementation/publication dependencies are accepted and complete. Developer manual validation may precede execution. Never depend on an unfinished system test from application tasks. For live Meta/R2-dependent scenarios, explicitly record emulation boundaries and any residual readiness limitation.

## Work Items

- [ ] Build per-domain fixtures for template authoring/translations, approved releases, WABA/locale/merchant scope, discount evidence, billing, consent/STOP and Meta provider events.
- [ ] Run separate integrated scenario executors for Admin lifecycle, Messaging/BullMQ/provider reconciliation, automated recovery, Shopify/Woo human follow-up and AI/HUMAN wrappers.
- [ ] Run negative/replay/race and source-level legacy-path absence checks; store actual results/evidence in the repository's approved evidence layout.
- [ ] Record explicit positive-discount provider-evidence capability status; if absent, return a blocking architect follow-up rather than claiming end-to-end completion.
- [ ] Return terminal Completion Report with actual commands, skips and evidence paths.

## Interfaces / Contracts

Consumes current Admin DB-first compiled payloads; shared Meta status event v2; `WhatsAppTemplateMetaRegistration`, `WhatsAppTemplateVariant`; BG001/BG004 prepared decisions; the existing provider/outbound-admission, Shopify recovery-server action, hosted Woo messages GET/POST and Woo WordPress proxy/client. Never import an AST compiler into the system-test repository or invent a new API shape. Respect independent versioned provider fixture contracts.

## Dependencies

All entries in YAML `depends_on` are terminal prerequisites; the superseded `ARCH-047-ADMIN-002` dependency has been **removed**. No system-test task appears in an implementation task's `depends_on`.

## Enables

None.

## Acceptance Criteria

- [ ] Admin-only immutable authoring, protected-keyed 20-language translation, Meta submission/approval/rejection and explicit merchant publication are proven via actual permitted boundaries.
- [ ] PAUSED + failed provider GET, drift, duplicate webhook, stale-status final fence, tenant/WABA/recipient isolation and STOP/credit races fail closed without sending or charging.
- [ ] Both Shopify and Woo automated outreach and human post-window selection are integrated; no obsolete `checkout-recovery` purpose allowlist, old Meta category GET or unowned template parameter injection remains in active send paths.
- [ ] No Offer fallback is proven separately from real positive-offer eligibility. A missing production checkout-specific evaluator is marked a **blocking gap**, not disguised as passing all six purposes.
- [ ] Human/AI wrappers, in-window checks, whole-message moderation and idempotency are proven independently.
- [ ] All necessary consumer tasks are accepted/merged and no outdated code, test fixture or duplicate send path persists after intended cutover.

## Validation

- [ ] Inspect and run only actual `moda-interact-system-test` package/scenario runner commands. Do **not** use unsupported `--workspace-root` argument.
- [ ] Validate isolated fixture cleanup, worker/HTTP/Meta requests, relevant PostgreSQL/Redis integration, regression probes, coverage evidence and `git diff --check`.

## Stop Condition

After required Work Items, Acceptance Criteria and Validation complete, update Completion Report, set `status: review`, return to `moda_architect`, STOP. If a required production discount evaluator or merchant integration is missing, record `blocked` with evidence rather than calling it Complete; do not implement another repository's missing code. Do not touch `_index.md`.

## Implementation Notes

Use the approved system-test fixture/executor/assertion/orchestration split with black-box focus. Follow `docs/agent-vcs-ownership-policy.md` and dedicated mirrored task worktrees. Treat normal Meta template-status API reads by BG003 as reconciliation, not ordinary send-time category validation. No claim that live Meta accepted a template unless that was actually observed.

## Completion Report

### Status
Not Started — pending terminal validation.

### Files Changed
None.

### Work Completed
None.

### Validation Results
Not run.

### Deviations
None.

### Assumptions
Text-only ARCH-047 can be certified independently of ARCH-049 image readiness.

### Unresolved Issues
Actual provider-specific read-only checkout discount eligibility remains unverified for positive-offer certification in the snapshot.

### Architectural Concerns
Source had legacy merchant allowlists and automated per-send Meta template metadata paths.

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
Reconcile verified implementation evidence and final architecture only after all required tests pass.
