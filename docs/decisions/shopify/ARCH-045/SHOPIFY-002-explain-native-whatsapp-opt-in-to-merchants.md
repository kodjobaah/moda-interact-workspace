---
id: ARCH-045-SHOPIFY-002
architecture_id: ARCH-045
title: Explain Shopify WhatsApp recovery consent to merchants
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: review
priority: 36
executor: null
claimed_at: null
attempt: 1
depends_on: []
enables:
  - ARCH-045-SYSTEM-TEST-001
created: 2026-10-20
updated: 2026-10-22
---
# Explain Shopify WhatsApp recovery consent to merchants

## Architecture

Architecture ID: `ARCH-045`
Architecture document: `docs/architecture/ARCH-045-shopify-whatsapp-consent-gated-recovery.md`
Coordinator: `moda_architect`
**Lifecycle:** materialised and claimed by the developer on 2026-10-22 (Attempt 1). Shopify implementation published as `d37aa1c0e326308c02247277d3c8a726164a7941` on `task/ARCH-045-SHOPIFY-002`; this record is submitted for architect review, not final acceptance or developer completion.

## Objective

Add a concrete **WhatsApp Customer Consent** section to the existing merchant **Recovery Settings** screen with actionable native Shopify setup guidance and the exact effect of missing or later consent.

## Context

Merchants will receive a checkout-keyed Support notice once BACKGROUND-002 is implemented, not a blocked `CheckoutRecovery`. Consent is held by Shopify and has no Moda-imposed 72-hour expiry. Only a checkout that can be safely rechecked while eligible may produce a recovery after later opt-in.

## Scope

- Render the guidance in the existing Shopify Recovery Settings view, including how to enable Shopify's native WhatsApp marketing opt-in at checkout, why consent saved on submitted checkout may not cover early abandonment and how Shopify Forms can collect opt-in beforehand. Use accurate public Shopify documentation and merchant translations already supported by the app.
- Explain no verified consent means **no CheckoutRecovery**, no customer message/charge and a checkout-keyed merchant Support notice when ordinary reconciliation encounters the problem.
- Explain later opt-in updates the customer phone preference but does **not** immediately scan or revive old abandoned checkouts; only a later **normal checkout reconciliation**, if any, may encounter the still-eligible checkout and create a recovery. No consent expiry clock or merchant bypass.
- Explicitly label abandoned-basket WhatsApp reminders as **marketing messages**, not order-confirmation/utility updates. Explain that consent must authorise WhatsApp recovery marketing, not merely allow the merchant to collect the checkout phone number. Explain that a WhatsApp STOP sent to Moda is enforced **locally**, the affected merchant receives a Moda Support notice, and Shopify consent status cannot override that STOP.

## Out of Scope

- No storefront CMP/banner/app block/pixel, Shopify consent write or new merchant manual send bypass.
- No claim that customer consent expires after 72 hours or that a previously skipped checkout is guaranteed to be found later.

## Requirements

- [x] Text refers to a checkout that cannot be recovered yet, **not** a paused/expiring `DETECTED` recovery.
- [x] Consent collection is native Shopify; no Customer Privacy API tracking consent is repurposed.
- [x] The guidance describes WhatsApp abandoned-basket messaging as marketing and does not conflate it with transactional order updates or Customer Privacy tracking consent.

- Merchant instructions state that native WhatsApp marketing permission is distinct from Shopify Customer Privacy tracking, that identity may be missing for guest checkouts, and that a later grant updates current permission but does not itself re-run a discarded candidate. Explain merchant-side native consent management in Shopify Admin and Moda-side WhatsApp STOP, without suggesting a second Shopify cookie-consent banner or a duplicate Moda merchant opt-out control.

## Work Items

- [x] Implement the dedicated Recovery Settings section and focused rendering/localisation tests. Do not modify Support notice generation, which belongs to BACKGROUND-002.
- [x] Verify guidance differentiates absent consent from Shopify API verification unavailability, and describes next normal reconciliation rather than a consent-triggered retry.

## Interfaces / Contracts

Existing Shopify merchant Recovery Settings UI; BACKGROUND-002 owns merchant Support notice creation. No API or storefront extension.

## Dependencies

None

## Enables

- `ARCH-045-SYSTEM-TEST-001`

## Acceptance Criteria

- [x] Merchant guidance truthfully separates consent-change sync from normal checkout re-evaluation and no-contact/no-charge outcomes.
- [x] No guarantee of automatic recovery on opt-in alone, no tracking-consent confusion or artificial 72-hour timer.

- [x] Copy neither promises recovery on opt-in alone nor asks a merchant to bypass missing permission; merchant native WhatsApp consent can be managed in Shopify Admin, while a STOP received through Moda remains a non-overridable local restriction.

## Validation

- [x] Focused Shopify Recovery Settings rendering, external documentation link, accessible UI/localisation and no-bypass language checks; `git diff --check`.

## Stop Condition

After completing only the defined Work Items, Acceptance Criteria and required Validation, record the canonical task worktree/branch and start-of-attempt synchronization evidence, populate the Completion Report, set `status: review`, return control to `moda_architect` and **STOP**. Do not launch enabled or unrelated tasks. For publication task, do not rerun implementation validation.

## Implementation Notes

Point to Shopify merchant settings via instructions, not invented deep links or a mandatory custom App Block.

Before claiming, use the deterministic `/moda-task` launcher and its **actual** prepared packet, read the task's complete current Architect Review, and verify task/dependency status in the developer's canonical workspace. Preserve `docs/decisions/**/_index.md` untouched until the developer explicitly closes the architecture documentation session. New runtime structured logging uses `@modainteract/moda-interact-shared/logging` where applicable. No source outside this task's owner repository may be changed unless explicitly authorised by the architecture.

## Completion Report

### Status

**Ready for Architect Review — developer Attempt 1 (2026-10-22).** Implementation committed and pushed to `moda-interact` branch `task/ARCH-045-SHOPIFY-002` at `d37aa1c0e326308c02247277d3c8a726164a7941` (`feat(shopify)`). The parent task is moved to `review` with `executor`/`claimed_at` cleared; `attempt: 1`, `execution_mode: developer`, and `completion_mode: developer` remain unchanged. This is a review submission, **not** an Accepted review or a completion decision.

### Files Changed

The published Shopify implementation commit changes **25 files**, all within `moda-interact`:

- Recovery Settings UI: `app/routes/app/recovery-settings/WhatsAppCustomerConsent.tsx` (new), `RecoverySettingsView.tsx` and `RecoverySettingsRoute.css`.
- Translations: `app/i18n/locales/{cs,da,de,en,es,fi,fr,it,ja,ko,nb,nl,pl,pt-BR,pt-PT,sv,th,tr,zh-Hans,zh-Hant}.json` (20 existing merchant locales).
- Tests: `tests/unit/arch045-whatsapp-consent-guidance.test.tsx` (new) and `tests/unit/recovery-settings-i18n.test.ts`.

No database schema, Background Support-notice implementation, Shopify checkout capture/consent writes, storefront extensions, or `docs/decisions/**/_index.md` files were changed by this implementation commit.

### Work Completed

- Added an accessible, read-only **WhatsApp Customer Consent** panel to the existing Recovery Settings view; no merchant consent override, new settings form or duplicate opt-out control.
- Provided native Shopify **Settings → Checkout → Marketing opt-in** guidance with a link to Shopify customer-contact documentation, and a Shopify Forms link for collecting WhatsApp opt-in before checkout submission. Warned that early abandonment and guest checkouts may lack a saved permission/identity.
- Described abandoned-basket WhatsApp outreach as **marketing**, distinct from order/utility messages, phone-number collection and Shopify Customer Privacy **tracking** consent.
- Explained that missing verified WhatsApp marketing permission means no `CheckoutRecovery`, outbound message or recovery credit; the separately owned Background reconciliation is expected to create a checkout-keyed Moda Support notice when it detects missing consent.
- Distinguished *missing permission* from *Shopify verification unavailable*: a verification outage is not equivalent to a customer's refusal and does not justify bypassing the gate.
- Explained that later opt-in updates current phone permission but does **not** itself replay or revive old checkouts; only subsequent ordinary reconciliation may encounter an otherwise eligible checkout. No arbitrary 72-hour expiry or guaranteed later recovery.
- Documented Moda-local WhatsApp STOP suppression and merchant Support notice; a later Shopify consent grant cannot override STOP.
- Added deterministic rendering/document-link/no-bypass guidance tests and 15 populated, non-fallback translation keys in all 20 supported locales.

### Validation Results

Developer terminal evidence from the canonical Shopify implementation worktree on **2026-10-22**:

- `npm test -- tests/unit/arch045-whatsapp-consent-guidance.test.tsx tests/unit/recovery-settings-i18n.test.ts tests/unit/merchant-i18n.test.ts` — **PASS, 21/21 tests in 3/3 files** (guidance 4/4, recovery-settings localisation 2/2, merchant localisation 15/15).
- `npm run lint` — **PASS** (no reported ESLint errors).
- `npm run build` — **PASS** (React Router client/server bundles built; Prisma Client v6.19.3 generated by `npm run prisma:generate`).
- `npm run typecheck` — **PASS on rerun** after Prisma Client generation; the first typecheck (before generation) failed with missing Prisma types. That initial failure is superseded by the successful rerun, not reported as an implementation change.
- `git diff --check` — **PASS** (no whitespace errors in the supplied terminal run).
- `git commit -m "feat(shopify)"` — **PASS**, implementation commit `d37aa1c0e326308c02247277d3c8a726164a7941` (25 files, 501 insertions), and `git push -u origin task/ARCH-045-SHOPIFY-002` — **PASS**. The branch head was independently verified at that SHA.
- The 21 focused tests and source build are not a full end-to-end Shopify/customer consent system test; terminal ARCH-045 system-test responsibility remains separate.

### Deviations

No Shopify implementation scope expansion was found in the published 25-file commit. The initial TypeScript failure was caused by an out-of-date/un-generated Prisma Client; repository build regenerated it and the subsequent typecheck passed. No application-code workaround was added.

### Assumptions

The merchant guidance states the agreed cross-service behaviour; **ARCH-045-BACKGROUND-002**, not this Shopify UI task, owns checkout-keyed Support notices and backend consent reconciliation. This UI addition does not itself enforce or verify customer consent.

### Unresolved Issues

No outstanding failure is recorded for the focused Shopify guidance checks. Full end-to-end consent/recovery behaviour and the separately owned Background components remain for their respective tasks and terminal `ARCH-045-SYSTEM-TEST-001`; do not infer their completion from these Shopify UI tests.

### Architectural Concerns

The implementation is guidance-only and introduces neither an alternative WhatsApp consent authority nor a tracking-cookie consent substitute. Formal architect review of the published implementation diff and validation remains pending.

## Architect Review

### Review Status

Pending — developer Attempt 1 submitted for review; not yet Accepted.

### Review Notes

Review requested for published Shopify implementation `d37aa1c` and the Completion Report evidence. No architect review outcome is recorded.

### Reviewed Files

None recorded by the architect yet; see the 25-file published implementation inventory under Completion Report.

### Validation Reviewed

Not yet architect-reviewed. Developer-supplied focused Vitest, lint, build, typecheck and whitespace evidence is recorded above.

### Architecture Conformance

Not assessed.

### Follow-up

Architect to review the published Shopify diff and evidence. With `completion_mode: developer`, an Accepted review leaves the explicit developer completion decision outstanding.

## Developer Takeover Amendment - 2026-10-22

The developer explicitly invoked `/moda_developer_create ARCH-045-SHOPIFY-002` for this agent-owned task. The task is transferred to developer execution with developer-controlled completion while preserving the assigned agent `moda_app`, repository ownership, scope, dependencies, acceptance criteria and validation requirements. Attempt claim and implementation-worktree preparation remain delegated to the canonical launcher.

## Developer Claim and Publication Evidence — Attempt 1

- Claim was recorded in the parent task frontmatter at `2026-10-22T10:44:49Z` with `executor: developer`, `attempt: 1`. This handoff clears the **active** claim after moving to Review; it does not create Attempt 2.
- Canonical parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-045-SHOPIFY-002`, branch `task/ARCH-045-SHOPIFY-002`; published task-claim commit `44e408892adfbdf5d1a447a3113cf5c28f209d7d` was verified before this documentation update.
- Canonical implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-045-SHOPIFY-002`, branch `task/ARCH-045-SHOPIFY-002`; published head `d37aa1c0e326308c02247277d3c8a726164a7941` has parent `4d3dbc39d6d7a7f79baa431a1e1be2112f5ea180`.
- The claimed, materialised task and independently confirmed publication establish branch/commit provenance. No additional start-of-attempt merge, rebasing, or unrecorded synchronization step is asserted.

## Developer Self-Review Passed/Accepted — Attempt 1

- The published implementation at `d37aa1c0e326308c02247277d3c8a726164a7941` remains clean and synchronized with `origin/task/ARCH-045-SHOPIFY-002`; the parent task report is clean and synchronized with its remote branch.
- Review confirms the 25-file change is within the task-owned Shopify repository scope: the Recovery Settings guidance component, existing view/style integration, 20 locale catalogues, and focused tests only. No backend consent authority, storefront extension, Support notice generation, database schema, or documentation index was changed.
- The task report records all Work Items, Acceptance Criteria, and Validation entries complete. Supplied validation evidence passes: focused tests `21/21`, lint, build, typecheck after Prisma generation, and `git diff --check`.
- The guidance correctly distinguishes Shopify WhatsApp marketing permission from phone collection and Customer Privacy tracking consent, explains missing-consent no-contact/no-charge behavior, separates verification unavailability from refusal, describes ordinary reconciliation after later opt-in, and preserves Moda-local STOP suppression.
- **Review outcome:** accepted for architect review. Because `completion_mode: developer`, the task remains `status: review` with `executor: null`, `claimed_at: null`, and `attempt: 1`; explicit developer completion is still pending. No enabled task was launched.
