---
id: ARCH-003-SYSTEM-TEST-002
architecture_id: ARCH-003
title: Verify merchant pending-recovery visibility and tenant isolation
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
status: blocked
priority: 50
executor: null
claimed_at: null
attempt: 2
depends_on:
  - ARCH-003-SHOPIFY-002
enables: []
created: 2026-09-05
updated: 2026-09-05
---

# Verify merchant pending-recovery visibility and tenant isolation

## Objective

Verify the integrated path:

```text
Shopify checkout
  -> checkout-events
  -> Background
  -> pending-recovery-candidates
  -> shop-scoped pending index
  -> authenticated merchant Usage overview
```

## Required evidence

Verify with live/current development infrastructure where available:

- [ ] a fresh checkout creates a tenant-readable pending candidate;
- [ ] candidate data carries explicit shopId + shopDomain;
- [ ] the Background shop ZSET contains the active job ID;
- [ ] `/app` for that merchant shows the candidate;
- [ ] delayed candidate is labelled Scheduled;
- [ ] waiting/active states are represented truthfully where observable;
- [ ] sensitive checkout/cart tokens and recovery URL are not rendered;
- [ ] candidate disappears from merchant view after maturity/cancellation;
- [ ] a different tenant cannot read/display the candidate;
- [ ] Redis unavailability produces a safe degraded pending section rather than
      failing the whole Usage overview;
- [ ] current and past usage remain functional.

Record concrete evidence, timestamps and environment.

## Manual refresh verification

Final integrated verification must also confirm:

- [ ] Pending recoveries exposes manual Refresh;
- [ ] Last updated advances after a successful refresh;
- [ ] refresh does not trigger a full page reload;
- [ ] unrelated usage/billing content remains available;
- [ ] refreshed counts/rows reflect live candidate state;
- [ ] current pending page is preserved when valid;
- [ ] invalid pending page falls back to the last valid page;
- [ ] no automatic polling interval is present.

## Pagination / refresh synchronisation verification

Final integrated verification must include:

```text
page 1 -> Next -> page 2 -> Refresh
```

and confirm the refresh operates on page 2.

Also verify that if refresh reduces the result to fewer pages, the panel moves
to the last valid page and subsequent refresh uses that effective page.

## Architect Amendment 001 — Strengthen live-evidence validator

The local validator is a useful foundation, but architect review found several
cases where incomplete or misleading evidence can currently pass.

This amendment tightens the validator before live developer evidence is
collected.

### 1. Prove the indexed candidate is actually visible to the merchant

Current validation checks the internal indexed job, but it does not require the
merchant's initial Pending recoveries response to contain that same job ID.

A response such as:

```json
{
  "available": true,
  "page": 1,
  "pageSize": 10,
  "total": 0,
  "totalPages": 0,
  "items": []
}
```

can currently validate successfully even while:

```text
index.memberJobId = job-1
```

exists.

Required invariant:

```text
indexed active candidate job ID
        ==
a merchant-visible item ID in the initial/equivalent captured response
```

The validator must fail when the indexed candidate is not actually visible to
the authenticated merchant.

### 2. Prove candidate removal after maturity/cancellation

The architecture requires:

```text
candidate active
    -> merchant sees it
    -> candidate matures or is cancelled
    -> shop ZSET no longer contains it
    -> merchant refresh no longer displays it
```

The current evidence schema does not validate this lifecycle.

Extend the evidence contract with an explicit post-lifecycle section, for
example:

```json
{
  "lifecycle": {
    "action": "matured",
    "indexContainsJobAfter": false,
    "merchantAfter": {
      "...": "normal safe pending response"
    }
  }
}
```

`action` may be:

```text
matured
cancelled
```

The validator must require:

```text
indexContainsJobAfter == false
```

and the original candidate ID must not appear in the post-lifecycle merchant
response.

### 3. Make page-2 refresh evidence explicit

The current boolean:

```text
page2RefreshRequested: true
```

does not prove which page the resource loader was actually asked to refresh.

Represent the sequence explicitly, for example:

```json
{
  "page2Refresh": {
    "requestedPage": 2,
    "response": { "...": "page 2 response" }
  }
}
```

Require:

```text
requestedPage == 2
response.page == 2
```

when page 2 remains valid.

### 4. Make fallback + subsequent refresh explicit

The final architecture requires:

```text
page 2
    -> refresh
    -> result shrinks to one page
    -> effective page 1
    -> next refresh requests page 1
```

Capture and validate explicit evidence, for example:

```json
{
  "fallbackRefresh": {
    "requestedPage": 2,
    "response": {
      "page": 1,
      "totalPages": 1
    },
    "subsequentRequestedPage": 1
  }
}
```

The validator must fail unless the effective fallback page becomes the page used
by the next refresh.

### 5. Validate Last updated chronologically

Current validation only checks:

```text
before != after
```

Require both values to be valid timestamps and:

```text
after > before
```

A reversed timestamp must fail.

### 6. Scope sensitive-field checks to the browser boundary

Sensitive-field redaction applies to merchant/browser-visible DTOs.

Developer-side internal evidence may legitimately inspect BullMQ job data while
proving tenant metadata and lifecycle behavior.

Do not reject an evidence file merely because internal evidence contains:

```text
checkoutToken
cartToken
abandonedCheckoutUrl
```

Instead, enforce forbidden-key checks on the merchant/browser-visible response
objects.

The browser boundary must still reject all of:

```text
checkoutToken
cartToken
abandonedCheckoutUrl
REDIS_URL
redisUrl
redisKey
rawJobData
opts
stacktrace
```

### 7. Explicit manual-refresh UI evidence

Require evidence that the merchant panel actually exposes the manual:

```text
Refresh
```

control.

Continue to reject automatic polling.

### 8. Keep existing validations

Preserve current validation for:

- authenticated shop identity;
- shop index membership;
- `evaluate-pending-recovery` job name;
- internal job `shopId` / normalized `shopDomain`;
- active BullMQ state;
- merchant page size 10;
- Scheduled / Waiting / Processing labels;
- other-tenant exclusion;
- Redis unavailable safe state;
- current/past usage continuity;
- zero full-page reloads.

### Regression tests

Add focused tests proving the validator rejects:

- [ ] indexed candidate absent from initial merchant response;
- [ ] candidate still visible after maturity/cancellation;
- [ ] candidate still present in shop index after lifecycle completion;
- [ ] page-2 refresh that actually requested page 1;
- [ ] fallback response whose subsequent refresh still requests the old page;
- [ ] reversed/non-ISO `Last updated` timestamps;
- [ ] sensitive fields in merchant/browser DTOs.

Also prove:

- [ ] internal developer-only BullMQ evidence may contain candidate-sensitive
      fields without being mistaken for browser leakage;
- [ ] a complete lifecycle evidence document passes.

### Live evidence gate

After this validator correction is architect-accepted, the task must **not** be
marked Complete merely because local validator tests pass.

The architecture task exists to verify the live integrated system.

Because repository-agent policy prevents the agent from operating the
developer-owned authenticated Shopify/Redis environment, the expected flow is:

```text
validator implementation accepted
        ->
task held pending developer live evidence
        ->
developer captures evidence
        ->
run:
npm run validate:merchant-pending-recovery:evidence -- <evidence.json>
        ->
architect reviews concrete live evidence
        ->
SYSTEM-TEST-002 Complete
```

### Resolver / attempt handling

This amendment belongs to the same task.

This coordination correction restores:

```yaml
status: ready
executor: null
claimed_at: null
attempt: 1
```

The next normal claim becomes Attempt 2.

After the validator correction is implemented:

```text
status: review
Completion Report: Ready for Review
```

Do not claim that live integrated verification has completed unless actual
developer-owned live evidence has been supplied.

## Completion Report

### Status

Ready for Review.

### Work Items

- Added a deterministic local merchant pending-recovery evidence validator.
- Added coverage for authenticated shop/index alignment, active-state labels,
  safe DTO redaction, other-tenant isolation, Redis-unavailable degradation,
  usage continuity, manual refresh, page-2 refresh, effective-page fallback,
  Last updated advancement, full-reload detection, and polling detection.
- Added `npm run validate:merchant-pending-recovery:evidence` for validating a
  developer-captured JSON evidence file without making network requests.
- Amendment 001: require the indexed candidate in the initial merchant response;
  validate matured/cancelled disappearance from both the index and merchant
  response; require explicit page-2 and fallback refresh request/response
  evidence; require chronological ISO `Last updated` timestamps; require the
  merchant `Refresh` control; and scope sensitive-field checks to browser DTOs.
- Added regression coverage for incomplete lifecycle/pagination evidence,
  reversed timestamps, browser DTO secrets, and permitted internal job fields.

### Validation

- Focused merchant evidence tests: 5 passed.
- New validator and script syntax checks: passed.
- Repository typecheck: passed.
- Repository lint: passed.
- `git diff --check`: passed.
- Full repository tests: 23 passed, 24 failed, 2 skipped. Twenty-three
  failures are cross-repository fixture failures because
  `moda-interact-gateway/nginx/nginx.conf.template` is absent at the workspace
  path expected by `test/render-blueprint-validation.test.js`; the remaining
  WhatsApp emulator worker test fails with Node test-runner deserialization
  error `Unable to deserialize cloned data due to invalid or unsupported version`.

### Live Validation

Live Shopify/Redis/merchant-browser validation was not run. The repository
agent is prohibited from executing deployed/shared-environment commands under
the developer-owned live-validation policy.

Developer-owned validation command after capturing the required evidence:

```text
npm run validate:merchant-pending-recovery:evidence -- ./path/to/evidence.json
```

The integrated checkout/merchant flow still requires developer-provided live
evidence with an authenticated Shopify session and current development
infrastructure.

### Git / VCS

Amendment implementation ready for architect review and developer commit/push.
Repository agent did not commit or push.

## Architect Review

### Review Status

Blocked

### Review Notes

Attempt 2 / Architect Amendment 001 implementation is accepted.

The local evidence validator now correctly enforces the specific deficiencies
identified in the previous review:

- indexed active candidate must appear in the merchant's initial pending
  response;
- lifecycle completion must remove the candidate from the shop index;
- lifecycle completion must remove the candidate from the merchant response;
- page-2 refresh records the actual requested page and response page;
- fallback refresh records the effective page and the subsequent requested page;
- `Last updated` values must be valid chronological ISO timestamps;
- manual Refresh exposure is required;
- browser-visible pending responses are checked for forbidden sensitive fields;
- developer-only internal BullMQ evidence may contain candidate-sensitive fields
  without being misclassified as browser leakage.

### Reviewed Files

- `moda-interact-system-test/src/merchant-pending-recovery-validation.js`
- `moda-interact-system-test/scripts/validate-merchant-pending-recovery-evidence.js`
- `moda-interact-system-test/test/merchant-pending-recovery-validation.test.js`
- `moda-interact-system-test/package.json`
- `docs/decisions/system-test/ARCH-003/SYSTEM-TEST-002-verify-merchant-pending-recovery-view.md`

### Validation Reviewed

Architect reran:

```text
node --test test/merchant-pending-recovery-validation.test.js
```

Result:

```text
5 passed
0 failed
```

Architect also reran syntax checks for the changed validator, CLI script and
focused test file; all passed.

Implementing-agent evidence additionally reports:

- typecheck/lint: passed;
- `git diff --check`: passed.

### Architecture Conformance

The validator implementation now conforms to Amendment 001.

The task itself is **not Complete**, because `ARCH-003-SYSTEM-TEST-002` is the
integrated live verification gate rather than merely a validator-development
task.

The following still requires concrete developer-owned live evidence:

```text
Shopify checkout
    -> Background pending candidate
    -> shop-scoped Redis ZSET
    -> authenticated merchant /app
    -> Pending recoveries
    -> manual Refresh
    -> pagination/fallback behavior
    -> lifecycle removal
```

### Blocker

Repository-agent access policy prevented live authenticated
Shopify/Redis/browser execution.

The task is therefore blocked only on developer-provided live evidence.

No further repository implementation changes are currently requested.

### Completion condition

Capture the live evidence using:

```text
docs/evidence/ARCH-003/SYSTEM-TEST-002-live-evidence-template.json
```

then run from `moda-interact-system-test`:

```bash
npm run validate:merchant-pending-recovery:evidence -- \
  ../docs/evidence/ARCH-003/SYSTEM-TEST-002-live-evidence.json
```

(or provide the completed JSON to the architect for review).

When the evidence validates and the architect confirms the concrete live
observations, `ARCH-003-SYSTEM-TEST-002` may be marked Complete without another
repository implementation attempt.


## Shopify resource blocker cleared

`ARCH-003-SHOPIFY-003` has been architect-reviewed and accepted Complete.

The pending-recovery resource now returns an explicit JSON `Response`, so the
previous live collector failure:

```text
'list' object has no attribute 'get'
```

is no longer considered a source-code blocker.

`ARCH-003-SYSTEM-TEST-002` remains:

```text
blocked
```

only because the corrected Shopify application must be deployed and the
developer-owned live evidence must still be captured.

After deployment, rerun the existing CDP collector. No collector source change
is required for this response-encoding issue.
