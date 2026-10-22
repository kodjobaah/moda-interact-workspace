---
id: ARCH-046-API-001
architecture_id: ARCH-046
title: Accept verified Woo customer-phone consent changes
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: in_progress
priority: 25
executor: developer
claimed_at: 2026-10-22T17:45:01+01:00
attempt: 2
depends_on:
  - ARCH-045-DATABASE-002
  - ARCH-045-SHARED-002
enables:
  - ARCH-046-WOOCOMMERCE-002
  - ARCH-046-SYSTEM-TEST-001
  - ARCH-046-SYSTEM-TEST-002
created: 2026-10-20
updated: 2026-10-22
---

# Accept verified Woo customer-phone consent changes

## Architecture

Architecture ID: `ARCH-046`

Architecture document: `docs/architecture/ARCH-046-woocommerce-whatsapp-consent-gated-recovery.md`

Coordinator: `moda_architect`

### Developer Takeover

The developer explicitly invoked `/moda_developer_create ARCH-046-API-001`, taking over execution and completion authority from the prior `execution_mode: agent`, `completion_mode: automatic` definition. Execution/completion modes are now `developer`/`developer`; logical ownership remains `assigned_agent: moda_api`, and task scope, dependencies, acceptance criteria and validation requirements are unchanged. The canonical launcher will prepare the implementation task worktree and claim Attempt 1 after this amendment is published.

**Lifecycle:** portable definition from 2026-10-20 snapshot; not materialised, claimed, committed, implemented or architect-accepted. Status means definition eligibility only.

## Objective

Accept explicit authenticated Woo customer-phone GRANT/REVOKE decisions, **atomically updating current `CustomerPhone` and appending immutable `commerce.WhatsAppConsentEvidence`**, without publishing or scheduling recovery work.

## Context

The hosted API already authenticates Woo installation calls. Woo checkout activity capture is separate from visitor permission, which can be given before order submission. The consolidated ARCH-045-DATABASE-002 owns shared CustomerPhone state, WooInstallation authentication/lifecycle and `commerce.WhatsAppConsentEvidence`.

## Scope

- Implement versioned `woo.whatsapp-consent.v1` authenticated POST with shop inferred from installation, server-validated Woo checkout/checkbox action, exact current canonical phone and installation-derived merchant scope, Moda-checkbox disclosure, explicit decision GRANT/REVOKE and stable event ID/revision.
- Treat the captured permission as **WhatsApp abandoned-checkout marketing** consent, not general transactional/utility notification permission. Validate the disclosure version and merchant identity; retained `WhatsAppConsentEvidence` shows which marketing description was affirmatively accepted. Do not create a new schema or evidence table for message classification.
- In a **single PostgreSQL transaction**, verify active installation credentials/status, existing checkout-recovery feature eligibility, deliberate checkbox action and `(Customer.shopId, active CustomerPhone canonical phone)` lookup; reuse the single unambiguous customer/phone match, create an ordinary Customer/CustomerPhone when none exists, and fail closed on multiple matches. Reject new grants from feature-disabled or inactive installations, stale decisions, forged checkbox actions or forged disclosure.
- Write the latest effective decision to shared CustomerPhone and exactly one **immutable** `commerce.WhatsAppConsentEvidence` fact. Identical `(shopId,eventId)` retry returns idempotently; conflicting replay fails and cannot roll back a later withdrawal. Return success after DB commit.
- **Stop at the consent write**: no BullMQ publication, database evidence `READY`/`NOT_ACTIONABLE` state, recovery task, checkout scan, merchant notice, send or billing. Later normal checkout reconciliation reads the updated phone if it runs.
- Do not block storefront order placement if Moda API is unavailable; unacknowledged consent remains unverified. A checkout page left open across merchant feature-disable cannot grant permission merely because its checkbox was previously visible. Authenticated withdrawals and negative opt-outs must remain possible through their approved routes. Use safe structured logging without phone/PII/secrets.

- When the Woo checkout-activity v1 envelope cannot carry the authenticated installation/shop and canonical recipient consistently with the consent POST, **API-001 owns the minimal versioned API capture-contract correction**; WOOCOMMERCE-002 owns plugin production. No persistent checkout-identity model is required. Contact text alone is never a consent GRANT.

## Out of Scope

- No checkout-specific current-consent table, recovery creation, Shopify consent mutation, third-party generic checkbox detection or WordPress direct database access.

## Requirements

- [x] Current permission is shop and exact active canonical phone scoped through existing Customer/CustomerPhone, with purpose and monotonic revision; not a checkout-specific flag. No GRANT follows from lookup alone.
- [x] A recorded grant or revocation by itself creates no CheckoutRecovery and no next-run job.
- [x] A GRANT is backed by an explicit merchant-specific WhatsApp recovery **marketing** disclosure, not customer phone collection or a general service message agreement.
- [x] Duplicate/stale/forged consent input cannot grant permission or overwrite later withdrawal; no charge/Meta send.

- **C4 revised:** Authenticate the existing Woo installation and derive `shopId` server-side. Validate that the checkbox choice originated from the active Woo checkout/WordPress request using the existing server-side hooks, nonce/session protections and install credentials. Resolve or create the existing Customer/CustomerPhone by merchant-scoped canonical phone. Never trust a browser-supplied `customerId` or unverified checkbox flag; never identify a *different merchant* by the same number. One safe match may be reused; ambiguous duplicates fail closed. The phone match is **identity lookup, not consent evidence**; a GRANT additionally requires a deliberate authenticated opt-in action.
- **H3/H4:** Define an acknowledgement ordering contract: a positive pre-submit grant is eligible for a following normal checkout observation **only after the hosted transaction commits and acknowledgement returns**. If normal capture overtakes it, the candidate may miss recovery by design; neither API retries nor an eventual grant may start a consent wake-up. Require monotonic server-enforced decision ordering; an older separately named GRANT cannot overwrite a later REVOKE, including concurrent tabs, changed phone and installation/session credential rotation.
- Use the published Shared canonical phone helper; reject ambiguous country context or inconsistencies between the canonical number the Woo server observed and the number the hosted request describes. No customer phone-ownership verification or persistent guest identity table is invented here. Neither a merchant no-contact restriction nor WhatsApp `CUSTOMER_STOP` can be cleared by the Woo checkbox grant; STOP is not a consent source and cannot be reset by this API.
- Consent-task retries must be idempotent and respect newer revoke/STOP decisions.

## Work Items

- [x] Add verified Woo consent controller/validation and atomic CustomerPhone + immutable evidence transaction.
- [x] Ensure no queue/broker/outbox/evidence wakeup side effect from the route.
- [x] Test fresh grant, withdrawal, regrant, installation revocation, merchant/phone matching, feature-disabled stale checkout, duplicate conflict, stale revision, host outage and no recovery side effects (API unit/integration coverage; outage simulated in route unit tests).

- [x] Validate the authenticated installation's server-attested Woo checkout action (including required nonce/session verification flags), derive shop from the installation, resolve `(shopId, canonicalPhone)` safely, then atomically update consent plus `WhatsAppConsentEvidence`. Actual WordPress hook/nonce verification belongs to the Woo producer and was not exercised by this API test suite.
- [ ] Complete the task's full edge-case test matrix: simultaneous *different-event* GRANT/REVOKE, changed number across tabs, installation reconnect, login/logout and a concurrent STOP race. Current coverage includes concurrent *same-event* replay, sequential revoke/stale grant, recipient mismatch, installation rotation/revocation, and retained STOP precedence, but not every named scenario.

## Interfaces / Contracts

Consumes the consolidated ARCH-045-DATABASE-002 `CustomerPhone`, installation authentication/lifecycle and `commerce.WhatsAppConsentEvidence` schema. `WOOCOMMERCE-002/003` are producers of authenticated versioned HTTP decisions. `BACKGROUND-001` reads current phone and current active installation during **normal checkout reconciliation**, not evidence worklist. No Shared Redis queue.

## Dependencies

- `ARCH-045-DATABASE-002`
- `ARCH-045-SHARED-002`

## Enables

- `ARCH-046-WOOCOMMERCE-002`
- `ARCH-046-SYSTEM-TEST-001`
- `ARCH-046-SYSTEM-TEST-002`

## Acceptance Criteria

- [x] Exact current CustomerPhone reflects latest verified decision and one immutable evidence record is written atomically.
- [x] Duplicate identical event is idempotent; conflicting or older event, cross-shop phone or ambiguous duplicate customer/phone matches are rejected; no phone lookup silently changes permission.
- [x] API never queues/reconciles old checkouts, constructs CheckoutRecovery, charges or sends when customer opts in/out.

- [x] The Woo consent POST may resolve by the sole merchant-scoped active canonical phone, but does **not grant from that match alone**: a validated deliberate Moda-checkbox opt-in and durable commit are required. No checkout reconciliation job is enqueued.
- [x] A newer revoke or customer STOP always defeats delayed grants, different event IDs and retries. A newly verified Woo checkbox grant may update the consent decision/evidence but **cannot clear a previously recorded WhatsApp `CUSTOMER_STOP`**; any STOP removal requires a separate authorised and verified customer request to Moda, outside API-001.

## Validation

- [x] Hosted API authenticated integration test against disposable migrated PostgreSQL, idempotent replay, installation credential rotation/revocation, server-attestation rejection, simulated hosted failure, and no recovery/billing side effects; `git diff --check` passed.

- [ ] Complete the specified authenticated API/PostgreSQL race matrix: guest checkout CSRF from real Woo hooks, *opposing-decision* concurrent tabs, installation reconnect/login/logout, and STOP changed concurrently with a consent write. Tested subsets include cross-shop canonical phone, zero/one/ambiguous matches, deliberate opt-in vs mere lookup, simultaneous identical-event replay, credential rotation and pre-existing STOP precedence.

## Stop Condition

After completing **only** the defined Work Items, Acceptance Criteria and required Validation, record launcher-resolved dedicated parent/implementation worktrees, their physical isolation and start-of-attempt synchronization evidence in the Completion Report. Change task to `review`, return control to `moda_architect`, and **STOP**. Do not start enabled tasks. A `blocked` task must remain blocked until the architect verifies and records the external missing recovery dependency and explicitly makes it Ready.

## Implementation Notes

No new Shared v1 JS package is justified by the PHP→HTTP integration. Use API-owned OpenAPI fixtures and PHP contract tests, not an independent duplicate of the wire schema. Preserve consent audit facts without any actionability/status field, polling consumer, recovery wakeup, outbox or Shared queue contract, even after Woo recovery is enabled.

Before any implementation, use `/moda-task` deterministic preparation against the **developer's actual** primary workspace, read the latest task/Architect Review, the parent architecture, relevant agent instructions, and the repository's real `package.json` scripts. Do not invent environment variables or claim a completed checkout/recovery source from the snapshot. Do not modify another repository, architecture-wide docs or `docs/decisions/**/_index.md` in a repository task. Use `@modainteract/moda-interact-shared/logging` for Node server diagnostics; PHP uses WordPress-specific safe diagnostics. Preserve official user/merchant i18n and tenant boundaries.

## Completion Report

### Status

In Progress — developer execution, **workflow Attempt 2**. Claimed after the Attempt 1 Changes Requested review. The required opposing-decision, concurrent STOP, changed-number, installation lifecycle and Woo hook CSRF validation frontier remains to be completed. Preserve Attempt 1's review record below as history.

### Developer Claim — Attempt 2

- Claimed at `2026-10-22T17:45:01+01:00`; executor is `developer`. Canonical history records the Attempt 1 claim, submission and Changes Requested decision.
- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-046-API-001`, branch `task/ARCH-046-API-001`. It was clean before synchronization. `origin/main` was merged forward into the task branch; `origin/main` is now an ancestor.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-046-API-001`, branch `task/ARCH-046-API-001`. It was clean, already contained current `origin/main`, and its `database` submodule remained at `508a89463ccb24dcc31e5f38e04be8cfd10ad690`.
- Both canonical task worktrees are registered at their launcher-resolved paths, on the matching task branches, and isolated from the dirty shared primary checkouts. No shared checkout or submodule gitlink was changed.
- The original launcher preparation packet was not present in this invocation; exact canonical routes, physical mappings, cleanliness, branch parity and synchronization were verified directly. Parent and implementation synchronization completed before this claim.

### Files Changed

`moda-interact-api` implementation (21 source, test, script and documentation files):

- `docs/arch046-woo-consent-http.md`
- `docs/openapi/arch046-woo-consent-v1.yaml`
- `package.json`, `package-lock.json`
- `scripts/test-arch046-woo-consent-postgres.mjs`
- `src/composition/routes.ts`, `src/composition/woocommerce.ts`, `src/index.ts`
- `src/woocommerce/activity/contract.ts`
- `src/woocommerce/consent/contract.ts`, `request.ts`, `routes.ts`, `service.ts`
- `tests/contracts/woocommerce/consent-grant.v1.json`, `consent-revoke.v1.json`
- `tests/fixtures/woocommerce/consent/event.ts`
- `tests/integration/woocommerce/consent/service.postgres.test.ts`
- `tests/unit/composition/real-route-registration.test.ts`
- `tests/unit/woocommerce/activity/contract.test.ts`
- `tests/unit/woocommerce/consent/contract.test.ts`, `routes.test.ts`

The database submodule is a **dependency, not a schema change owned by API-001**. On 2026-10-22 the developer reported a clean `database` checkout at `508a89463ccb24dcc31e5f38e04be8cfd10ad690` (`heads/main`), with `git diff --submodule=short -- database` empty and no local database changes. The API implementation commit/push hash was not supplied in the available evidence and must be recorded by the developer/reviewer after publication.

### Work Completed

- Introduced `POST /v1/woocommerce/whatsapp-consent` with strict `woo.whatsapp-consent.v1` parsing, authenticated Woo installation identity, server-attested checkbox action, exact canonical phone comparison, purpose-specific merchant disclosure, and explicit GRANT/REVOKE.
- Added merchant-scoped `Customer`/`CustomerPhone` resolution (creating only when absent, rejecting ambiguous active matches), in-transaction installation/entitlement checks, monotonic decision ordering, immutable `WhatsAppConsentEvidence`, payload-digest replay protection, and scoped locking of event and recipient identities.
- Preserved an independent `CUSTOMER_STOP` no-contact restriction. Consent write does not publish a BullMQ event or outbox notification, trigger recovery scans, create `CheckoutRecovery`, bill or send WhatsApp messages.
- Added a minimal authenticated `woo.activity.v2` capture adapter, retaining the existing v1 queued activity contract; updated API route composition, OpenAPI, fixtures and test coverage.
- Corrected integration fixtures during validation: reuse the migration-seeded `checkout_recovery` feature and supply mandatory timestamps on raw customer/phone inserts.

### Validation Results

Results observed in supplied local terminal logs dated 2026-10-22:

- `npm run test:arch046-woo-consent:unit` — **PASS, 6/6**. Contract and HTTP route tests cover strict action flags, rejected identity spoofing, forged checkbox/session data, authentication and simulated API/DB failure.
- `npm run test:arch035-woo-activity:unit` — **PASS, 21/21** (existing activity compatibility/regression tests).
- `npm run test:arch046-woo-consent:postgres` — **PASS, 1/1**, against disposable PostgreSQL after **59/59** migrations, including `20261021170000_arch045_shared_woo_consent_privacy`. Covers durable evidence, replay, sequential withdrawal/stale-grant rejection, tenant scoping, ambiguous matches, feature-disable, credential rotation/revocation and retained STOP. Earlier fixture failures were corrected before the passing run.
- `npm run typecheck` — **PASS**.
- `npm run lint` — **PASS**, zero reported lint errors.
- `npm run build` — **PASS**.
- `git diff --check` — **PASS** in the supplied validation logs.
- On 2026-10-22, `git submodule status database` showed `508a89463ccb24dcc31e5f38e04be8cfd10ad690 database (heads/main)` with no leading mismatch marker; `git -C database status --short` and `git diff --submodule=short -- database` showed no changes.
- Test case coverage beyond these executable tests (including simultaneous *different-event* GRANT/REVOKE, concurrent STOP mutation, real Woo Classic/Blocks login/logout and reconnect flows) is **not demonstrated** by the supplied logs. These are not claimed as passing.

### Deviations

- The implementation added the bounded API-owned `woo.activity.v2` capture-contract adaptation permitted by the Scope; no Woo plugin changes or new Shared queue/evidence-wakeup contract were made.
- The preexisting `## Architecture` section still contains a historical portable-definition lifecycle note predating materialisation. Current YAML claim metadata and this report describe the developer's ongoing task; the historical note is left unchanged because architecture-definition edits belong to the architect.
- The developer used review assistance and correction patches. They do not change the task attempt count or transfer source ownership.

### Assumptions

- The developer-reported implementation worktree was `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-046-API-001` on `task/ARCH-046-API-001`; the uploaded parent-task snapshot is rooted at `moda-interact-workspace-task-ARCH-046-API-001/`. Launcher-resolved parent/implementation worktree preparation and start-of-attempt branch synchronization packets were **not provided for independent verification** in this review packet.
- The accepted ARCH-045 database and Shared prerequisites are available to the API integration. The database SHA above was reported clean, but no implementation commit SHA, push result or publication evidence was provided.
- WooCommerce is responsible for its actual WordPress nonce/session and checkout-action validation before submitting server-attested consent. The API rejects unverified or malformed attestations; real Woo browser/Classic/Blocks flows require producer/system validation.

### Unresolved Issues

- Required task test matrix is not fully evidenced: add focused coverage for opposing GRANT/REVOKE tab races, STOP during a consent transaction, changed-number interleaving, installation reconnect/login/logout, and real Woo Classic/Blocks guest-checkout CSRF hooks. Keep the tests scoped to the API-owned boundary and prove no stale decision or side effect wins.
- The current attempt passes available unit/typecheck/build checks, but these missing scenarios prevent acceptance. Do not create Attempt 2 in this review; the next developer-create claim may increment the attempt after corrections are implemented.

### Architectural Concerns

- No consent-driven recovery wakeup, new database schema, cross-service queue contract, WhatsApp send, billing or cross-repository implementation was introduced.
- The end-to-end validity of the Woo-side nonce/session assertion and simultaneous consent/no-contact races remains an explicit acceptance review point. This is a validation/ownership frontier, not evidence that the observed green tests failed.

## Architect Review

### Review Status

Developer Self-Review — Changes Requested, Attempt 1.

### Review Notes

The implementation branch is published and clean. Focused consent unit tests pass 6/6, typecheck passes, and build passes. Review fails because the task explicitly requires evidence for opposing decisions, concurrent STOP mutation, changed-number interleaving, installation reconnect/login/logout, and Woo hook CSRF scenarios; no matching tests were found in the implementation test suite and the report leaves the validation checkbox unchecked.

### Reviewed Files

- `src/woocommerce/consent/service.ts`
- `src/woocommerce/consent/routes.ts`
- `tests/integration/woocommerce/consent/service.postgres.test.ts`
- `tests/unit/woocommerce/consent/contract.test.ts`
- `tests/unit/woocommerce/consent/routes.test.ts`

### Validation Reviewed

- `npm run test:arch046-woo-consent:unit` — 6/6 passed.
- `npm run typecheck` — passed.
- `npm run build` — passed.
- Required concurrent/lifecycle matrix — not demonstrated; changes requested.

### Architecture Conformance

The implementation remains within the API-owned consent boundary, but acceptance is deferred until the missing race and Woo lifecycle evidence is added or the architect explicitly narrows those requirements.

### Follow-up

Return to developer execution for Attempt 1 corrections. Keep `status: ready`, `executor: null`, `claimed_at: null`, and `attempt: 1`; do not start enabled tasks.

### Developer Self-Review - Changes Requested

Attempt 1 review failed. Add focused, executable coverage for opposing GRANT/REVOKE decisions, STOP concurrent with consent, changed-number interleaving, installation reconnect/login/logout, and guest-checkout CSRF from real Woo hooks or document an architect-approved scope amendment. Re-run the relevant PostgreSQL/unit validation plus typecheck/build, publish the implementation and report, then request review again without creating Attempt 2 in this cycle.
