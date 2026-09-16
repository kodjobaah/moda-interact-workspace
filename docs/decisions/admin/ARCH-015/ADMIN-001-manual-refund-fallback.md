---
id: ARCH-015-ADMIN-001
architecture_id: ARCH-015
title: Replace Admin refund workflow and adapt Refund Requests UI to ARCH-015
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 80
executor: null
claimed_at: null
attempt: 2
depends_on:
- ARCH-015-BACKGROUND-003
enables:
- ARCH-015-SYSTEM-TEST-001
created: 2026-09-15
updated: 2026-09-16
---

# ARCH-015-ADMIN-001

## Objective

Perform one atomic Admin refactor so `moda-interact-admin` moves directly from the pre-ARCH-015 refund workflow to the accepted ARCH-015 workflow without an intermediate compatibility state.

This single task owns:

```text
server settlement boundary
+ refund read model/types
+ server actions
+ Billing -> Refund Requests queue/drawer
+ Admin i18n keys touched by the refund UI
+ focused security/UI tests
```

Do **not** split this implementation into a second Admin task.

## Development-state rule — no legacy compatibility

Moda Interact is still in development and has no historical merchant population requiring compatibility with superseded refund workflows.

Therefore:

- remove superseded code instead of retaining dormant compatibility paths;
- do not preserve `legacy`, `old flow`, fallback, feature-flag or compatibility branches;
- do not retain UI controls for a superseded transition merely because the function exists today;
- remove tests that assert superseded behavior and replace them with ARCH-015 assertions;
- do not add data migration/backfill logic solely to preserve the removed Admin workflow.

## Audited starting point

The 2026-09-16 workspace snapshot was correlated to Admin source around commit:

```text
9652d025652b691143894cce7ba0259cb07460bf
```

The audited starting point contains:

```text
lockRecoveryCreditRefund
rejectRecoveryCreditRefund
lockRecoveryCreditRefundAction
rejectRecoveryCreditRefundAction
READY_FOR_PROVIDER_ACTION
```

and the current Refund Requests drawer exposes Admin controls for `REQUESTED` and permits the provider evidence form for `NEEDS_ATTENTION`.

ARCH-015 supersedes those semantics.

## Accepted lifecycle boundary

```text
Merchant refund request
        |
        v
REQUESTED
        |
        | Background owns preparation/assessment
        v
+------------------------------+
| safe automatic correction    |
| -> App Event correction      |
+------------------------------+
        OR
+------------------------------+
| automatic correction unsafe  |
| -> PROVIDER_ACTION_REQUIRED  |
+------------------------------+
```

Admin does not prepare a `REQUESTED` refund.

Admin is an exceptional **manual settlement evidence** surface only after Background explicitly selects `PROVIDER_ACTION_REQUIRED`.

## Authorized implementation surface

Primary:

```text
src/lib/admin/recovery-credit-refund-settlement.ts
src/lib/admin/recovery-credit-refunds.ts
src/app/actions/recovery-credit-refunds.ts
src/lib/admin/types.ts
src/components/admin/recovery-credit-refunds.tsx
src/i18n/locales/en.json
src/i18n/required-keys.ts                 # only if the current required-key pattern requires it
tests/security/admin-recovery-credit-refund*.test.mjs
tests/security/admin-billing-progressive-disclosure.test.mjs
# directly affected Admin refund tests only
```

Read-only/reuse targets unless a compile-safe narrow adjustment is necessary:

```text
src/components/admin/admin-detail-drawer.tsx
src/app/(platform)/billing/page.tsx
src/components/admin/billing-tabs.tsx
src/lib/admin/query.ts
src/i18n/index.ts
```

Do not introduce Shopify App Event submission from Admin.

# Implementation order

Execute the phases below in order. Do not leave the repository in a state where server types and UI disagree.

## Phase 1 — remove superseded Admin-owned REQUESTED mutations

Delete implementation, exports, imports and tests for:

```text
lockRecoveryCreditRefund
rejectRecoveryCreditRefund
lockRecoveryCreditRefundAction
rejectRecoveryCreditRefundAction
```

Delete helper code that becomes unreachable solely because these operations are removed.

Do not replace either operation with a renamed equivalent.

Admin MUST NOT:

```text
REQUESTED -> PROVIDER_ACTION_REQUIRED
REQUESTED -> REJECTED
```

Admin MUST NOT calculate/freeze from REQUESTED:

```text
finalCreditQuantity
expectedProviderAmount
expectedProviderCurrency
```

Admin MUST NOT release/reapply the merchant refund hold as a REQUESTED preparation/rejection operation.

After this phase the final task state must satisfy:

```bash
rg -n "lockRecoveryCreditRefund|rejectRecoveryCreditRefund" src tests
```

Expected final result: no matches.

## Phase 2 — replace derived queue semantics

Delete Admin-only read-model literal:

```text
READY_FOR_PROVIDER_ACTION
```

Replace with:

```text
READY_FOR_REFUND_PROCESSING
```

This is an Admin DTO/UI state only. Do not add/change a Prisma enum.

Derive exactly:

```text
refund.status == REQUESTED
purchase.status == WITHDRAWN
purchase.reservedAmount > 0
  -> WAITING_FOR_RESERVATIONS

refund.status == REQUESTED
purchase.status == WITHDRAWN
purchase.reservedAmount == 0
purchase.currentAmount > 0
  -> READY_FOR_REFUND_PROCESSING
```

Unexpected/invalid REQUESTED combinations remain fail-closed as `NEEDS_ATTENTION` according to the existing read-model pattern.

Update:

```text
RecoveryCreditRefundQueueStatus
queueStatus(...)
statusWhere(...)
allowed status/filter arrays
focused tests
```

No `READY_FOR_PROVIDER_ACTION` source reference may remain.

## Phase 3 — project automatic-correction evidence from DATABASE-002

Consume the accepted typed `RecoveryCreditRefund` fields:

```text
automaticCorrectionUsageEventId
providerUsageQuantityBeforeCorrection
providerUsageCostBeforeCorrection
expectedProviderUsageQuantityAfterCorrection
expectedProviderUsageCostAfterCorrection
```

Load the explicit linked correction UsageEvent relation for detail presentation.

Expose a bounded DTO:

```text
automaticCorrection: null | {
  id
  quantity                  # Decimal -> canonical string
  shopifyReportState
  shopifyEventHandle
  shopifyIdempotencyKey
  reportAttemptCount
  lastReportAttemptAt
  reportedAt
}
```

Also expose the four correction evidence decimals as canonical strings/null.

Do not duplicate full transport diagnostics into the refund summary DTO merely because they are available. The App Event drawer owns detailed provider response/error diagnostics.

Authoritative correction-existence rule:

```text
refund.automaticCorrectionUsageEventId != null
```

Do not replace it with a loose `sourceType/sourceId` query.

## Phase 4 — harden the only remaining normal Admin refund mutation

`recordRecoveryCreditProviderEvidence(...)` remains the only normal Admin refund mutation.

Permit it only when all are true inside the existing serializable transaction:

```text
refund.status == PROVIDER_ACTION_REQUIRED
refund.automaticCorrectionUsageEventId == null
purchase.status == WITHDRAWN
purchase.reservedAmount == 0
refund.finalCreditQuantity != null
refund.finalCreditQuantity > 0
refund.expectedProviderAmount != null
refund.expectedProviderCurrency != null
```

Fail closed for:

```text
REQUESTED
NEEDS_ATTENTION
COMPLETED
REJECTED
CANCELLED
any non-null automaticCorrectionUsageEventId
missing frozen expected evidence
purchase not WITHDRAWN
reservedAmount != 0
```

A non-null automatic correction link blocks manual monetary action for every linked UsageEvent state, including:

```text
PENDING
IN_FLIGHT
RETRYABLE
REPORTED
NEEDS_ATTENTION
```

No SUPER_ADMIN bypass.

Preserve explicit evidence:

```text
providerActionKind = REFUND | CREDIT
providerReference
providerAmount
providerCurrency
explicit confirmation
```

Do not add a generic `mark complete` mutation.

Exact evidence:

```text
providerAmount == expectedProviderAmount
providerCurrency == expectedProviderCurrency
```

Exact match -> use the existing atomic entitlement/audit/system-message completion semantics.

Mismatch -> `NEEDS_ATTENTION`, persist submitted provider evidence for investigation, and do **not** allow normal monetary resubmission from NEEDS_ATTENTION.

## Phase 5 — adapt the existing Billing -> Refund Requests UI

Preserve the existing operational surface:

```text
/billing?view=refunds
RecoveryCreditRefundQueue
RecoveryCreditRefundDrawer
AdminDetailDrawer
```

Do not add:

```text
standalone /refunds route
second refund queue under tenant billing
modal duplicate of the drawer
second settlement workflow
```

### REQUESTED is read-only

For every `REQUESTED` refund render evidence/status only.

Render no:

```text
Lock provider action
Reject request
manual REFUND/CREDIT form
```

Presentation rules:

```text
WAITING_FOR_RESERVATIONS
  -> waiting for reservations; no monetary action

READY_FOR_REFUND_PROCESSING
  -> ready for Background processing; Admin must not perform provider action

REQUESTED + automaticCorrectionUsageEventId == null
  -> Background has not yet selected the settlement route

REQUESTED + automaticCorrectionUsageEventId != null
  -> automatic correction exists; show high-level provider-report/reconciliation state
```

### Manual form eligibility

Render `ProviderEvidenceForm` only when:

```text
refund.status == PROVIDER_ACTION_REQUIRED
refund.automaticCorrectionUsageEventId == null
canSettle == true
```

Never render normal manual settlement controls for `NEEDS_ATTENTION`.

Safety-invalid state:

```text
PROVIDER_ACTION_REQUIRED
+ automaticCorrectionUsageEventId != null
```

must render the architect-supplied blocking warning and no monetary form.

## Phase 6 — progressive-disclosure drawer

Do not append ARCH-015 fields to the current giant flat `DetailList`.

Restructure the existing drawer into:

### A. Settlement summary — always visible

```text
Refund ID
Shop
Request status
Queue status
final refundable credits when frozen
expected provider amount/currency when frozen
Purchase ID
original plan handle
original event handle
```

### B. Settlement route/status

Automatic route is proven by:

```text
automaticCorrectionUsageEventId != null
```

Manual route is proven by:

```text
status == PROVIDER_ACTION_REQUIRED
AND automaticCorrectionUsageEventId == null
```

Do not infer route from `reason` text.

### C. Automatic correction evidence — only if link exists

Show:

```text
correction UsageEvent id
correction quantity
Shopify report state
provider quantity before correction
provider cost before correction
expected provider quantity after correction
expected provider cost after correction
expected refund amount/currency
bounded report/attempt timestamps
```

Do not calculate provider values in the component.

### D. Purchase provenance — secondary disclosure

Keep access to:

```text
billing period snapshot
provider context/subscription snapshot
plan handle snapshot
event handle snapshot
purchase provider amount/currency
purchase meter quantity/cost before and after
provider valuation confirmation
provider price evidence
request-time credit snapshots
support/source context
```

but move it out of the primary always-visible list.

### E. Reservations/history — secondary

Preserve bounded reservation and refund history evidence.

### F. Manual provider evidence

Show only under Phase 5 eligibility.

## Phase 7 — App Event drill-through

When an automatic correction exists, link to the existing App Events surface using the current Billing query convention:

```text
/billing?view=events&eventId=<automaticCorrectionUsageEventId>
```

Use existing URL/query helpers.

Do not duplicate detailed provider error/response diagnostics in the main refund drawer. The linked App Event drawer owns them.

## Phase 8 — completed settlement presentation

Automatic completion:

```text
automaticCorrectionUsageEventId != null
providerActionKind == null
```

Present as automatic Shopify App Event correction.

Manual completion:

```text
automaticCorrectionUsageEventId == null
providerActionKind == REFUND | CREDIT
```

Present as manual provider settlement and show the recorded provider evidence.

Never label an automatic completion as manual.

# Localization contract — deterministic; no translation discovery

Canonical architect-owned translation data is provided in:

```text
docs/decisions/admin/ARCH-015/ADMIN-001-localization-matrix.json
```

The matrix contains exact values for these 20 canonical locales:

```text
cs
da
de
en
es
fi
fr
it
ja
ko
nb
nl
pl
pt-BR
pt-PT
sv
th
tr
zh-Hans
zh-Hant
```

The implementation agent MUST NOT:

- translate any supplied value;
- paraphrase, shorten or improve any supplied value;
- choose different locale identifiers;
- invent a missing refund-specific translation;
- use external translation services;
- infer wording from another Moda repository.

If a required refund-specific key is absent from the matrix, STOP and return the missing key to `moda_architect`.

## Current Admin runtime constraint

At the audited snapshot, Admin runtime imports only:

```text
src/i18n/locales/en.json
```

and `getAdminI18n(locale)` still supplies that English catalogue.

Therefore this task MUST NOT silently turn into an Admin-wide locale-routing/runtime project.

Implement exactly as follows:

1. Add/use the supplied `en` refund-specific keys in the current English Admin catalogue.
2. Reuse existing generic Admin keys for generic concepts where already present (`Shop`, status/common dates, pagination, empty/not-recorded, etc.).
3. Keep `ADMIN-001-localization-matrix.json` as the normative architect-supplied translations for all 20 canonical locales.
4. If the implementation worktree already contains an accepted Admin multi-catalogue runtime and matching locale files that are newer than the audited snapshot, populate the same refund keys in those existing locale files using the matrix verbatim.
5. If the runtime is still English-only, do **not** create/wire 19 new runtime locale files in ARCH-015. That requires a separate Admin-localization architecture task.
6. Do not leave newly touched refund-specific raw English literals in `recovery-credit-refunds.tsx` when an architect-supplied key exists.

This rule gives Luna every translation value it could need while preventing it from designing a new localization system.

# Required tests

At minimum prove:

1. `lockRecoveryCreditRefund` is absent from production/test source;
2. `rejectRecoveryCreditRefund` is absent from production/test source;
3. corresponding server actions/imports are absent;
4. no test expects Admin to promote/reject a REQUESTED refund;
5. source contains no `READY_FOR_PROVIDER_ACTION`;
6. REQUESTED + WITHDRAWN + reservations > 0 => `WAITING_FOR_RESERVATIONS`;
7. REQUESTED + WITHDRAWN + zero reservations + currentAmount > 0 => `READY_FOR_REFUND_PROCESSING`;
8. automatic correction relation/evidence projects decimals as canonical strings;
9. REQUESTED UI is read-only;
10. `READY_FOR_REFUND_PROCESSING` UI explicitly describes Background ownership;
11. `PROVIDER_ACTION_REQUIRED + automaticCorrectionUsageEventId == null + canSettle` shows manual evidence form;
12. any non-null automatic correction link blocks manual monetary action server-side and UI-side;
13. `NEEDS_ATTENTION` never shows/accepts normal manual monetary settlement;
14. exact manual evidence completes once;
15. mismatch becomes NEEDS_ATTENTION and cannot normally resubmit;
16. no generic mark-complete path exists;
17. automatic correction section uses typed evidence without client recalculation;
18. automatic correction links to `/billing?view=events&eventId=<id>`;
19. purchase provenance remains accessible through secondary disclosure;
20. automatic/manual completed settlement routes are distinguished;
21. touched refund-specific UI copy uses supplied i18n keys;
22. English runtime values exactly match the `en` block in the architect matrix;
23. if additional accepted Admin locale catalogues exist, every implemented locale value exactly matches the same matrix;
24. no implementation translation service/inference code is introduced;
25. Admin does not submit Shopify App Events;
26. entitlement/audit/system-message behavior remains exactly-once for manual completion.

# Validation

Inspect `package.json`, then run repository-supported equivalents of:

```bash
npm test
npm run typecheck
npm run lint
npm run build
rg -n "READY_FOR_PROVIDER_ACTION|Lock provider action|lockRecoveryCreditRefund|rejectRecoveryCreditRefund" src tests
rg -n "mark complete|Mark complete" src/components/admin/recovery-credit-refunds.tsx tests || true
git diff --check
```

The first `rg` must return no matches.

Also validate the localization matrix deterministically:

```text
- JSON parses;
- exactly 20 locales;
- every locale has the same key set;
- the implemented English values exactly equal matrix.locales.en;
- any other existing Admin locale catalogues touched by this task exactly equal their corresponding matrix locale values for these keys.
```

Record unrelated baseline failures exactly; do not widen scope to unrelated Admin/Billing areas.

# Stop conditions

STOP and return evidence to `moda_architect` if:

- accepted DATABASE-002 correction fields/relation are unavailable;
- BACKGROUND-003 does not leave manual fallback evidence in the agreed `PROVIDER_ACTION_REQUIRED` shape;
- existing Billing App Event route does not accept `view=events&eventId=<id>`;
- manual settlement would require allowing `NEEDS_ATTENTION` or a non-null automatic correction link;
- implementing progressive disclosure requires replacing the Admin drawer/UI system rather than adapting existing primitives;
- a required refund-specific localization key is absent from the architect matrix;
- the task would require inventing Admin-wide locale routing/catalogue loading architecture.

Do not invent compatibility paths, translations or settlement bypasses.

# Completion protocol

Update Completion Report, set `status: review`, clear claim, return to `moda_architect`, STOP.

## Completion Report

Status: Ready for Review

Implementation commit: `ec62204` (`fix(admin): correct refund presentation routes`), pushed to `task/ARCH-015-ADMIN-001` in `moda-interact-admin`.

Attempt 2 correction mapping:

- Finding 1 implemented: added exact automatic/manual completed predicates requiring `COMPLETED`, the authoritative automatic-correction FK, and the correct provider action evidence; malformed completed rows remain route-pending and unlabelled.
- Finding 2 implemented: `NEEDS_ATTENTION`, exact completed states, linked automatic corrections, manual fallback, and only then derived REQUESTED queue notices are evaluated in that order. Linked `REPORTED` corrections use `awaitingReconciliation`.
- Finding 3 implemented: Purchase provenance now retains billing/provider snapshots, valuation confirmation, request-time credit snapshots, source, requester, and source-message evidence under the existing secondary disclosure.
- Finding 4 implemented: the normal form remains limited to `PROVIDER_ACTION_REQUIRED` with no automatic link and `canSettle`; recorded evidence is shown only for exact manual completion or investigative `NEEDS_ATTENTION` rows with submitted evidence.
- Finding 5 implemented: automatic correction drill-through is exactly `/billing?view=events&eventId=<id>` and does not carry refund query state.
- Finding 6 implemented: the queue description, manual fallback, and reconciliation notices use the supplied `billing.refund` keys. No locale runtime or translation catalogue was added.
- Strengthened `admin-recovery-credit-refunds.test.mjs` to assert the exact predicates, precedence, conditional evidence, provenance fields, i18n usage, and canonical URL.

Validation:

- PASS: `npm ci` completed with declared dependencies; manifests and lockfiles were not changed.
- PASS: focused refund and settlement tests — 4 passed, 0 failed.
- PASS: `npm run build` completed successfully; existing BullMQ optional-dependency and critical-dependency warnings remain.
- PASS: `npm run lint` completed with 0 errors and 5 pre-existing warnings in `merchant-pricing-plan-builder.tsx`, `queue-monitor.tsx`, and `recovery-credit-refund-settlement.ts`.
- PASS: forbidden legacy grep returned zero matches; generic mark-complete grep returned zero matches; `git diff --check` passed.
- PASS: localization matrix validation — JSON parses, exactly 20 locales, identical 31-key sets, and English runtime values exactly match `matrix.locales.en`.
- BLOCKED baseline: `npm test` fails in existing merchant-support tests because the generated `@prisma/client` does not export `PlatformAdminRole`.
- BLOCKED baseline: `npx tsc --noEmit` reports existing errors in promotions and merchant-support, including implicit transaction types and Prisma raw-query typing; no errors were introduced in the focused refund component by the correction.

No unresolved implementation concerns remain within the bounded Admin task. No branch was merged, no force-push was used, and the Architect Review section was not edited. Parent and implementation branches are pushed and ready for moda_architect review.

## Architect Review — Attempt 1 — Changes Requested

Verdict: **Changes Requested**.

The server-side manual-settlement boundary is accepted for this attempt. Do not redesign
`recordRecoveryCreditProviderEvidence(...)`, reintroduce REQUESTED mutations, add Admin App
Event submission, or weaken the non-null automatic-correction guard. The remaining defects
are confined to the required Refund Requests presentation/drill-through contract and its
focused tests.

### Finding 1 — completed settlement route predicates are not the ARCH-015 predicates

`RecoveryCreditRefundDrawer` currently derives `manual` only from
`status == PROVIDER_ACTION_REQUIRED && automaticCorrectionUsageEventId == null`. A manually
completed refund therefore renders `routePending` even when `providerActionKind` is `REFUND`
or `CREDIT`. `stateNotice()` also labels every COMPLETED refund with a null automatic link as
manual without requiring recorded `REFUND | CREDIT` evidence.

Attempt 2 MUST use the exact completion predicates:

```text
automatic completion:
  status == COMPLETED
  automaticCorrectionUsageEventId != null
  providerActionKind == null

manual completion:
  status == COMPLETED
  automaticCorrectionUsageEventId == null
  providerActionKind == REFUND | CREDIT
```

Do not label a malformed COMPLETED row as manual or automatic merely from the absence/presence
of one field. The settlement-route section must show the manual route for both an eligible
`PROVIDER_ACTION_REQUIRED` manual fallback and an exact manual COMPLETED row.

### Finding 2 — automatic REQUESTED state is shadowed by READY_FOR_REFUND_PROCESSING

`stateNotice()` evaluates `queueStatus == READY_FOR_REFUND_PROCESSING` before the authoritative
automatic-correction FK. A REQUESTED refund with an already-linked correction UsageEvent can
therefore display "Ready for Background refund processing" instead of the automatic provider
submission/reconciliation state required by Phase 5.

Attempt 2 MUST make the authoritative route/evidence win over the derived queue label:

```text
refund.status == NEEDS_ATTENTION
  -> billing.refund.needsAttention

exact completed automatic/manual predicates
  -> completedAutomatic / completedManual

automaticCorrectionUsageEventId != null
  + linked shopifyReportState == REPORTED
    -> billing.refund.awaitingReconciliation
  + otherwise
    -> billing.refund.automaticInProgress

status == PROVIDER_ACTION_REQUIRED
automaticCorrectionUsageEventId == null
  -> billing.refund.manualRequired

then use WAITING_FOR_RESERVATIONS / READY_FOR_REFUND_PROCESSING / awaitingAssessment for
unprepared REQUESTED rows.
```

Do not infer settlement route from `reason` text.

### Finding 3 — progressive disclosure dropped required purchase provenance evidence

Phase 6 required existing purchase evidence to remain accessible under the secondary purchase
provenance disclosure. The current drawer no longer renders all of the required evidence that
the pre-ARCH-015 drawer exposed.

Attempt 2 MUST keep these values accessible under the Purchase provenance `<details>` section:

```text
billingPeriodIdSnapshot
providerSubscriptionIdSnapshot
planHandleSnapshot
eventHandleSnapshot
purchaseProviderAmountSnapshot / purchaseProviderCurrencySnapshot
purchase.providerUsageQuantityBeforeSnapshot
purchase.providerUsageCostBeforeSnapshot / currency
purchase.providerUsageQuantityAfterSnapshot
purchase.providerUsageCostAfterSnapshot / currency
purchase.providerValuationConfirmedAt
purchase.providerPriceSnapshot
purchaseCreditsGrantedSnapshot
currentAmountAtRequestSnapshot
reservedAmountAtRequestSnapshot
availableAmountAtRequestSnapshot
source
requestedByShopifyUserId
sourceMessage.id when present
```

Move/preserve this evidence; do not return to one giant always-visible DetailList.

### Finding 4 — manual evidence is rendered as an always-visible section

The drawer currently renders the `manualEvidence` heading and recorded provider fields for every
refund, including ordinary REQUESTED and automatic-correction rows. This defeats the bounded
settlement-route presentation.

Attempt 2 MUST keep the monetary form exactly where it already belongs:

```text
status == PROVIDER_ACTION_REQUIRED
automaticCorrectionUsageEventId == null
canSettle == true
```

Read-only recorded manual evidence may be shown for an exact manual COMPLETED row and for a
NEEDS_ATTENTION row that already contains submitted provider evidence for investigation, but
do not render an empty manual-settlement section on unrelated REQUESTED/automatic rows. Never
render the normal form for NEEDS_ATTENTION.

### Finding 5 — App Event drill-through is not the canonical ARCH-015 URL

The current link builds from `{ ...params, view: "events", eventId: ... }`. When opened from the
Refund Requests drawer, this carries stale `refundId`, `refundStatus`, `refundPage`, or other
refund query state into the App Events view.

The required drill-through is exactly:

```text
/billing?view=events&eventId=<automaticCorrectionUsageEventId>
```

Use the existing URL helper but do not spread Refund Requests query state into this link.

### Finding 6 — supplied refund i18n copy is present but bypassed

The architect matrix already supplies `billing.refund.description`, `manualRequired` and
`awaitingReconciliation`. The touched component still renders a raw refund-specific queue
description and the state logic never uses the latter two supplied values.

Attempt 2 MUST:

```text
use billing.refund.description for the Refund Requests description;
use billing.refund.manualRequired for the manual-fallback state;
use billing.refund.awaitingReconciliation when the linked correction event is REPORTED;
preserve all matrix values verbatim;
add no new locale runtime/catalogues.
```

Generic field labels may continue to use existing generic Admin copy where the matrix supplies
no refund-specific key. Do not invent translations.

### Authorized Attempt-2 production surface

```text
src/components/admin/recovery-credit-refunds.tsx
tests/security/admin-recovery-credit-refunds.test.mjs
src/lib/admin/recovery-credit-refund-settlement.ts   # cleanup only if lint proves dead code
```

`src/i18n/locales/en.json` should not need semantic changes because the required architect-owned
keys already exist and match the matrix. Do not change settlement/database semantics unless a
compile error directly requires a narrow type-safe adjustment.

### Required Attempt-2 regression assertions

At minimum prove:

```text
manual COMPLETED (link null + REFUND/CREDIT) => completedManual + routeManual
automatic COMPLETED (link non-null + action null) => completedAutomatic + routeAutomatic
malformed COMPLETED evidence is not silently labelled manual
REQUESTED + automatic link + REPORTED => awaitingReconciliation, not readyForProcessing
PROVIDER_ACTION_REQUIRED + no link => manualRequired
NEEDS_ATTENTION never renders the normal settlement form
plain REQUESTED/automatic rows do not render an empty manual-evidence section
purchase secondary disclosure contains every Phase-6-D evidence field listed above
App Event href is exactly /billing?view=events&eventId=<id> with no refund query parameters
Refund Requests description uses billing.refund.description
```

Strengthen the existing focused source tests so they assert predicates/URL construction and the
required evidence fields, not merely the presence of the strings `completedAutomatic`,
`completedManual`, `purchaseProvenance`, `view: "events"`, and `eventId` somewhere in the file.

### Validation

From the Admin task worktree, first install the declared repository dependencies without editing
package manifests/lockfiles, then run the repository-supported checks:

```bash
npm ci
node --test tests/security/admin-recovery-credit-refunds.test.mjs tests/security/admin-recovery-credit-refund-settlement.test.mjs
npm test
npx tsc --noEmit
npm run lint
npm run build
rg -n "READY_FOR_PROVIDER_ACTION|Lock provider action|lockRecoveryCreditRefund|rejectRecoveryCreditRefund" src tests
rg -n "mark complete|Mark complete" src/components/admin/recovery-credit-refunds.tsx tests || true
git diff --check
```

Re-run the deterministic 20-locale/31-key matrix check and require English runtime equality with
`matrix.locales.en`. If dependency installation or an unrelated baseline still prevents a broad
check, record the exact external failure; do not weaken the focused ARCH-015 assertions or change
production code to work around missing tools.

### Stop conditions

STOP and return evidence to `moda_architect` if the corrections would require a new route, new
refund mutation, Admin Shopify App Event submission, a Prisma/schema change, translation
invention, or a new Admin-wide locale runtime. Otherwise return this same task with
`status: review`, `executor: null`, `claimed_at: null`, and `attempt: 2` after the next claim.
