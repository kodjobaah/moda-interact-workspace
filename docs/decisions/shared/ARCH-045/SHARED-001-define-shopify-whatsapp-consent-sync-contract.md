---
id: ARCH-045-SHARED-001
architecture_id: ARCH-045
title: Define Shopify consent-sync and canonical identity contracts
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: complete
priority: 20
executor: null
claimed_at: null
attempt: 2
depends_on: []
enables:
  - ARCH-045-SHARED-002
created: 2026-10-20
updated: 2026-10-22
---
# Define Shopify consent synchronisation and canonical identity contracts

## Architecture

Architecture ID: `ARCH-045`
Architecture document: `docs/architecture/ARCH-045-shopify-whatsapp-consent-gated-recovery.md`
Coordinator: `moda_architect`
**Lifecycle:** materialised and claimed using `/moda_developer_create ARCH-045-SHARED-001`. Attempt 1 was returned to ready with Changes Requested. Attempt 2 was claimed using the canonical launcher `--prepare --executor developer` flow, reconciled, and explicitly completed by the developer below. Architect review remains a separate governance record.

## Objective

Implement and test a **single published Shared implementation** containing (1) a minimal Shopify WhatsApp consent-state sync event for existing queues, (2) canonical E.164-equivalent exact-recipient phone helpers and portable golden vectors, and (3) validated Shopify numeric customer ID ↔ GraphQL Customer GID conversion. The sync event updates local consent via Background but can never request checkout reconciliation or start a recovery. `ARCH-045-SHARED-003` is Superseded and fully absorbed here; separate `ARCH-045-SHARED-002` publishes the accepted package.

## Context

Existing Shopify webhook/Background queues do not carry the WhatsApp consent-sync topic, and existing customer-phone helpers only trim/strip digits while Shopify privacy webhooks use numeric IDs versus GraphQL GIDs. All services should consume one versioned canonical event schema and one identity implementation, not independently reproduce them. Both sets of interfaces are defined and share `moda-interact-shared` ownership; this task consolidates the former SHARED-003 helper implementation into SHARED-001.

## Scope

**Shopify-to-Background event contract**
- Add the versioned `ShopifyWhatsAppConsentSyncJobV1Schema` (repository naming may vary), typed payload `{schemaVersion:1,shopId,shopifyCustomerId,deliveryId,triggeredAt}`, strict runtime validation, stable deterministic job ID and a **distinct** job name on an existing approved Shopify BullMQ queue. Exclude phone, consent Boolean, checkout key and recovery-wakeup fields; do not route it through checkout-created/updated parsing.
- Export the producer/consumer runtime schemas and constants from the Shared package entrypoints; test malformed/replayed input, duplicate IDs, cross-shop identity and existing checkout event compatibility **within Shared**. Integrating the published contract into Shopify ingress and Background is separately owned by their dependent tasks after `ARCH-045-SHARED-002` publication.

**Cross-platform exact recipient and Shopify customer identity**
- Implement one browser-safe/Node-safe canonical phone validator/normaliser that produces a verified E.164-equivalent recipient or a typed rejection. National-format numbers require **explicit verified country context**; do not infer permission or guess from locale. Provider `wa_id`/digits-only send addresses remain service-owned adapters.
- Implement validated numeric Shopify customer ID ↔ `gid://shopify/Customer/<numeric>` conversion/equality; reject malformed, zero/overflow and wrong-resource GIDs or arbitrary principal strings. Consumer services remain responsible for authenticated shop/tenant binding.
- Publish deterministic compatibility fixtures for UK national/international equivalence, ambiguity, extensions, rotation/reassigned phone, numeric webhook/GID conversion and invalid IDs; test these fixtures with the Shared Node implementation. **Executing WooCommerce PHP runtime parity against the applicable phone and recipient-lifecycle vectors belongs to `ARCH-046-WOOCOMMERCE-002`, not this Shared task.** The PHP consumer must not import Node implementation source.
- Keep only reusable codec, validator, identity/job helpers and tests in Shared; no Prisma, service secrets, API calls, business consent policy, provider sends or queue infrastructure creation.

## Out of Scope

- No new BullMQ queue, separate queue schema for Woo, HTTP handler, provider lookup, CustomerPhone write, recovery candidate, recovery retry job or source publication in this implementation task.
- No WooCommerce PHP adapter implementation or PHP-runtime fixture-parity test execution; these are consumer-owned under `ARCH-046-WOOCOMMERCE-002`.
- No Shopify webhook handler/enqueue integration, Background queue dispatch/consumer integration or live consumer import evidence. `ARCH-045-SHOPIFY-001` owns Shopify producer adoption; `ARCH-045-BACKGROUND-003` owns sync-event consumer adoption; `ARCH-045-BACKGROUND-001` owns recipient identity adoption. Those tasks verify use of the published Shared contract/helpers within their own repositories. **Their adoption is not a SHARED-001 acceptance or publication prerequisite.**

## Requirements

- [x] Exactly one versioned consent-state synchronisation schema with deterministic job identity and no authority to create checkout recovery, send messages or carry consent decisions.
- [x] Shared exports one versioned consent-sync validator, a distinct existing-queue job name and deterministic job identity, with tests proving separation from existing checkout event parsing. **Shopify ingress and Background must adopt this published validator/version in `ARCH-045-SHOPIFY-001` and `ARCH-045-BACKGROUND-003`, not in SHARED-001.**
- [x] Canonical phone identity is stable across explicitly scoped national/international representations and rejects unparseable/ambiguous input; Shared tests the portable golden fixtures in Node and publishes them for downstream PHP compatibility testing.
- [x] Numeric/GID Shopify customer identity conversion validates resource kind and format, but never substitutes for shop/customer authorisation.
- [x] No independent copies of a cross-service event schema or identity helper, new queue, provider lookup, local consent policy or recovery wakeup.

## Work Items

- [x] Add minimal versioned consent-sync schema, distinct existing-queue job name and deterministic ID generator; validate/reject extraneous consent/phone/recovery payload fields.
- [x] Implement exact international phone normalisation/validation requiring verified country context when needed; publish typed failures and deterministic vectors.
- [x] Implement strict Shopify numeric ID/GID conversion and customer-kind validation with fixtures for malformed, other-resource and out-of-range identities.
- [x] Export browser/Node-safe entrypoints and compatibility fixtures from the approved package subpaths, without importing server-only code in browser exports; keep hashing primitives in a Node-only subpath when required.
- [x] Add focused schema, idempotency, checkout queue compatibility, exact recipient, ID conversion, portable fixture and export tests **in Shared**; preserve existing published contract compatibility. PHP runtime parity is verified separately by `ARCH-046-WOOCOMMERCE-002`.

## Interfaces / Contracts

**Owner:** `moda_shared` (`moda-interact-shared`), single implementation task `ARCH-045-SHARED-001`; release owner `ARCH-045-SHARED-002`.

- **Sync event:** `ShopifyWhatsAppConsentSyncJobV1Schema` (or repository-equivalent), `{schemaVersion:1,shopId,shopifyCustomerId,deliveryId,triggeredAt}`, deterministic job ID, existing queue with distinct job name. Producer `ARCH-045-SHOPIFY-001`, consumer `ARCH-045-BACKGROUND-003`. No checkout recovery side effect. Each consumer/producer task must import and validate against the published Shared contract in its own repository; SHARED-001 is not responsible for proving those integrations.
- **Canonical recipient helper:** Node Shopify/Background/Woo API callers import the published identity entrypoint. `ARCH-045-BACKGROUND-001` owns Background adoption at the consent-sensitive recipient boundary; Shared owns only the reusable helper and its exports/tests. Shared publishes runtime-neutral JSON fixtures at `@modainteract/moda-interact-shared/identity/fixtures`; the PHP phone adapter and applicable fixture-parity execution are owned by `ARCH-046-WOOCOMMERCE-002` after `ARCH-045-SHARED-002` publication.
- **Shopify ID helper:** numeric webhook IDs and GraphQL customer GIDs compare after strict validation; shop ownership is validated by consumers.
- **Publication:** `ARCH-045-SHARED-002` publishes this *one accepted implementation task*; no implementation in publication task.

## Dependencies

None

## Enables

- `ARCH-045-SHARED-002`

## Acceptance Criteria

- [x] Event schema and deterministic ID reject malformed/PII/consent/recovery fields; existing checkout parser and event versions remain intact with distinct routing.
- [x] A valid numeric Shopify customer ID and GraphQL Customer GID normalise consistently, while invalid/wrong-resource/out-of-scope identities fail validation without granting authorisation.
- [x] Exact phone helpers produce the same canonical result under verified country context, reject ambiguous/invalid input, and provide deterministic UK, international, extension, rotation and reused-number vectors in portable JSON; **Node tests pass against those vectors**. Passing a PHP-runtime consumer suite is not a Shared acceptance gate.
- [x] Shared entrypoint exports are runtime-safe and importable after publication (no server-only secrets or Node imports in browser-safe surfaces), with package-shape/smoke validation **in Shared**. Actual producer and consumer imports/adoption are validated by their dependent Shopify/Background tasks, not SHARED-001.
- [x] No new queue, consent-triggered recovery, provider lookup or consent business policy in Shared.

## Validation

- [x] Repository-declared focused sync-event schema/job ID and checkout-queue compatibility tests. Live Shopify producer and Background consumer integration tests are outside this Shared task.
- [x] Repository-declared Node phone/Shopify ID codec tests against the portable JSON fixtures, plus fixture export/package-shape verification. **Do not require a PHP runtime or PHP parity pass in this repository.**
- [x] Entrypoint/export typecheck/build as applicable and `git diff --check`.

## Stop Condition

After completing only the defined Work Items, Acceptance Criteria and required Validation, record the canonical task worktree/branch and start-of-attempt synchronization evidence, populate the Completion Report, set `status: review`, return control to `moda_architect` and **STOP**. Do not launch enabled or unrelated tasks. Publication is separately owned by SHARED-002; stop after implementation review.

## Implementation Notes

Use existing Shopify Shared naming/style. Preserve published export compatibility. Stop at review: publication is a separate task.

**Architect-approved scope amendment — 2026-10-21:** PHP-runtime interoperability is a **consumer validation**, not an implementation or acceptance responsibility of `moda-interact-shared`. `ARCH-045-SHARED-001` owns correct, deterministic, runtime-neutral golden JSON and the Node tests and export that establish its contract. `ARCH-046-WOOCOMMERCE-002` owns testing its PHP exact-recipient normalisation against **all applicable** Shared `phoneCases` and recipient-lifecycle vectors, including negative cases. Shopify-only numeric ID/GID vectors remain covered in Shared Node tests; Woo is not required to implement a Shopify principal codec. `ARCH-045-SHARED-002` may publish following Shared acceptance without waiting for PHP tests. This amendment changes no developer claim, versioned runtime contract, event semantics or recovery scheduling.

**Architect-approved downstream adoption boundary — 2026-10-21:** SHARED-001 is complete in *scope* when it supplies and tests the canonical schema, job identity, identity helpers and safe exports; it does not implement Shopify/Background source imports or provide live consumer evidence. After separate package publication by `ARCH-045-SHARED-002`, `ARCH-045-SHOPIFY-001` must prove ingress production uses the Shared v1 schema/job identity, `ARCH-045-BACKGROUND-003` must prove existing-queue dispatch validates the same schema and does not route via checkout parsing, and `ARCH-045-BACKGROUND-001` must prove consent-sensitive recipient handling uses the canonical identity helper. Each downstream task already depends on publication (directly or through its prerequisites) and owns corresponding integration validation. No change to contract semantics, consumer dependencies, queue topology, developer attempt or status is implied. This scope amendment resolves only the **consumer-adoption** correction from Developer Self-Review; original launcher preparation/synchronisation evidence remains mandatory.

For this **developer-owned** attempt, preserve the `/moda_developer_create` claim and use `/moda_developer_update ARCH-045-SHARED-001` for reconciliation/self-review after required acceptance evidence is complete. The launcher-prepared packet and physical worktree/synchronisation evidence must be recorded, not inferred. Preserve `docs/decisions/**/_index.md` untouched until the developer explicitly closes the architecture documentation session. New runtime structured logging uses `@modainteract/moda-interact-shared/logging` where applicable. No source outside this task's owner repository may be changed unless explicitly authorised by the architecture.

## Completion Report

### Status

Complete — Attempt 2 reconciled and explicitly completed by the developer. Architect review remains a separate governance record.

### Files Changed

Observed implementation changes within `moda-interact-shared` (14 distinct files across the two patch revisions):

- `fixtures/README.md`
- `fixtures/identity-v1.json`
- `package-lock.json`
- `package.json`
- `src/identity/identity-fixtures.test.ts`
- `src/identity/index.ts`
- `src/identity/recipient-phone.ts`
- `src/identity/shopify-customer.ts`
- `src/shopify/index.ts`
- `src/shopify/node.ts`
- `src/shopify/queue-contracts.ts`
- `src/shopify/whatsapp-consent-sync.schema.ts`
- `src/shopify/whatsapp-consent-sync.test.ts`
- `tsup.config.ts`

Do not stage the untracked `typescript` terminal transcript noted in the implementation log. This parent task-document update makes no Shared source, `_index.md`, or architecture-file edits.

### Work Completed

- Implemented a strict versioned Shopify WhatsApp consent-state sync event schema and distinct existing-queue job routing with deterministic ID; payload contains only `schemaVersion`, `shopId`, `shopifyCustomerId`, `deliveryId`, and `triggeredAt`.
- Added browser-safe/Node-safe international exact-recipient phone normalisation via `libphonenumber-js/max`, requiring verified country context for national numbers, and typed rejection for invalid, reserved, ambiguous and extension-bearing numbers.
- Added validated numeric Shopify Customer IDs, strict GraphQL Customer GID conversion and shop-scoped comparison without conferring authorisation.
- Exported canonical Shared entrypoints and portable identity fixture JSON. Fixture coverage includes UK, US and France, malformed identities, number rotation/reassignment and negative cases.
- Added focused event, identity and export tests. After Attempt 1's initial implementation patch, the incremental **fixture-only** correction fixed six UK fictional-number expectations without weakening production validation.
- Deferred package publication to `ARCH-045-SHARED-002`; no new queue, provider lookup or consent-triggered recovery wakeup was introduced. Shopify ingress and Background integration remain dependent-task work and are not claimed completed here.

### Validation Results

Evidence supplied in developer terminal captures `typescript(20261021-181643)` and `typescript(20261021-182855)`; results are observations from those logs, not a claim that a remote review has occurred.

| Check | Observed result |
| --- | --- |
| Implementation patch application and `git diff --check` | Applied without displayed errors; diff check passed |
| `npm ci` | Passed; npm audit reported 1 low and 1 high vulnerability, and installation warnings (not corrected within this task) |
| `npm test` after initial implementation patch | 366 tests: **359 pass, 6 fail, 1 skip**; invalid-success expectations for Ofcom-reserved fictional UK numbers |
| `npm test` after fixture-only correction | 367 tests: **366 pass, 0 fail, 1 skip** |
| `npm run typecheck` | Passed in both recorded runs |
| `npm run build` | Passed in both recorded runs; `/identity` JavaScript and declaration entrypoints emitted |
| `npm test` during Attempt 2 self-review | **PASS**, 367 tests: 366 passed, 0 failed, 1 skipped |
| `npm run typecheck` during Attempt 2 self-review | **PASS** |
| `npm run build` during Attempt 2 self-review | **PASS**, identity and Shopify JavaScript/declaration entrypoints emitted |
| `npm pack --dry-run --json` during Attempt 2 self-review | **PASS**; package includes `dist/identity/index.js`, `dist/identity/index.d.ts`, Shopify entrypoints and `fixtures/identity-v1.json` |
| Built-package runtime smoke check | **PASS**; package-shape output confirms `/identity` and `/shopify` bundles and manifest exports `/identity`, `/identity/fixtures`, `/shopify` and `/shopify/node` |
| PHP execution against portable fixture JSON | **Not run; out of scope by the 2026-10-21 architect-approved amendment.** `ARCH-046-WOOCOMMERCE-002` must record consumer-owned PHP fixture-parity evidence |
| Implementation task branch commit/push | **Confirmed** — `12f6ff5` (`feat(shared)`) at `HEAD` and `origin/task/ARCH-045-SHARED-001` in the Shared implementation worktree |
| Parent task report commit/push | **Attempt 1 confirmed** — `7a38e513` (`docs(ARCH-045-SHARED-001): record developer attempt 1 evidence`) successfully pushed to `origin/task/ARCH-045-SHARED-001`; Attempt 2 report reconciliation is the current parent worktree change |

#### Task worktree evidence

- Latest Attempt 2 evidence: canonical launcher `--prepare --executor developer` claim, followed by `--route-only --json`, physical worktree inspection, and current validation from the dedicated implementation worktree.
- Launcher-prepared canonical parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-045-SHARED-001`, `task/ARCH-045-SHARED-001`.
- Dedicated Shared implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-045-SHARED-001`, `task/ARCH-045-SHARED-001`; implementation `HEAD` and remote are both `12f6ff5`, with clean status.
- Parent and implementation branches were each at parity `0 0` with `origin/task/ARCH-045-SHARED-001` before this report reconciliation; parent report changes are now ready to commit and push.
- Both dedicated physical worktrees and their branch associations are listed in `git worktree list --porcelain`; path naming is not the sole evidence.
- Canonical Attempt 2 `/moda_developer_create` claim: `executor: developer`, `attempt: 2`, `claimed_at: 2026-10-22T09:22:59Z`; the launcher-prepared packet and start-of-attempt synchronization evidence were recorded for this attempt.

### Deviations

A fixture-only correction was required after the first test run; production phone validation was preserved. No cross-repository implementation scope expansion was observed.

### Assumptions

The 21 October developer-claimed parent snapshot is the patch baseline. The two implementation patch revisions represent one developer-owned Attempt 1, not two separately claimed attempts. This report records observed local validation and the published Attempt 2 reconciliation. Canonical phone identity does not demonstrate phone ownership, WhatsApp reachability or consent. ARCH-045 imposes no arbitrary consent-expiry deadline.

### Unresolved Issues

1. Review npm audit warnings separately if relevant to the intended release; this task did not run dependency audit remediation.

The former downstream-ingress/Background-validator evidence item is **resolved by the architect-approved downstream adoption boundary** above, not by claiming either consumer has been implemented. The requirement and integration evidence remain mandatory in `ARCH-045-SHOPIFY-001`, `ARCH-045-BACKGROUND-003` and `ARCH-045-BACKGROUND-001` after publication; they do not block SHARED-001 review.

The former missing-PHP-runtime-validation item is **resolved by the architect-approved scope amendment above**, not by claiming that PHP parity has passed. Required PHP parity evidence remains outstanding in `ARCH-046-WOOCOMMERCE-002` and does not gate Shared acceptance or publication.

### Architectural Concerns

No new cross-service architecture change observed beyond the agreed event and identity contracts. Downstream Shopify/Background consumers must import the published Shared package (after `SHARED-002`) and must not interpret sync events as permission to create or wake checkout recoveries.

### Developer Self-Review - Passed/Accepted (Attempt 2)

- Attempt reviewed: 2. The published implementation commit `12f6ff59583ad630e12e77ac6b0ae2f69e3a2cae` is unchanged and remains synchronized with the implementation remote.
- Attempt 2 launcher preparation, canonical parent/implementation worktrees, branch associations, and synchronization state were verified. Both worktrees were clean before this report reconciliation.
- `npm test` passed with 366 passed, 0 failed, and 1 skipped; `npm run typecheck`, `npm run build`, `npm pack --dry-run --json`, and `git diff --check` passed. Package output includes the identity fixtures and Shopify/identity entrypoints required by this task.
- The Attempt 1 corrections are resolved: launcher preparation evidence is recorded for Attempt 2, and the architect-approved downstream adoption boundary assigns Shopify/Background consumer integration to their owning tasks. PHP runtime parity remains owned by `ARCH-046-WOOCOMMERCE-002`.
- State before this explicit completion decision: `status: review`, `executor: null`, `claimed_at: null`, `attempt: 2`.

### Developer Completion Decision (Attempt 2)

- The developer explicitly invoked `/moda_developer_update ARCH-045-SHARED-001 complete` after the durable Attempt 2 Passed/Accepted review.
- All Work Items and Acceptance Criteria are checked; the implementation branch is committed and pushed at `12f6ff5`, and the parent task branch is committed and pushed at `23f04974` before this completion record.
- No merge to `main` is required or performed. Downstream adoption and PHP parity remain owned by the explicitly assigned dependent tasks.
- State transition: `status: complete`, `executor: null`, `claimed_at: null`, `attempt: 2`.

## Architect Review

### Review Status

Developer self-review Accepted; task Complete — Attempt 2. No independent architect code-diff re-review was performed in this coordination pass.

### Review Notes

**Coordination reconciliation — 2026-10-22 (documentation only):** The canonical task YAML is `complete` at Attempt 2; its later developer Passed/Accepted self-review and explicit completion decision are the latest recorded outcome. Historical Architect Review status before this reconciliation: "Pending — no implementation reviewed.". All prior findings and validation notes below are preserved as historical evidence; no tests were rerun, Git remote state was not rechecked, and this is not a new independent implementation acceptance.

None.

### Reviewed Files

None — portable definition only.

### Validation Reviewed

None.

### Architecture Conformance

Not assessed.

### Follow-up

None.

## Developer Takeover and Materialisation Amendment — 2026-10-21

The developer explicitly invoked `/moda_developer_create ARCH-045-SHARED-001` for this ready agent-owned task. The portable definition was materialised on the canonical parent task branch. Execution ownership is transferred to the developer and completion requires an explicit developer decision after architect review. The logical repository owner remains `moda_shared`; task scope, dependencies, acceptance criteria and validation requirements are unchanged.

## Developer Self-Review - Changes Requested

- Attempt reviewed: 1; implementation commit `12f6ff59583ad630e12e77ac6b0ae2f69e3a2cae` is published on `origin/task/ARCH-045-SHARED-001`. Parent task history remains published; the untracked `typescript` terminal transcript was preserved and not staged.
- The Shared implementation, golden fixtures, tests and package exports were verified. `npm test` passed 366/367 tests (one skipped); typecheck, build, package dry-run, built-package entrypoint smoke check and `git diff --check` passed.
- Correction 1: provide the original launcher `--prepare` packet or contemporaneous logs proving start-of-attempt synchronization and recursive submodule preparation, or obtain an explicit architect amendment waiving/replacing that evidence. Do not rerun preparation solely to recreate history.
- Correction 2: provide evidence that Shopify ingress and Background consume this same versioned Shared runtime validator and distinct job routing, or obtain an architect scope amendment assigning consumer adoption/verification to their owning tasks. Do not implement cross-repository changes here.
- State transition: `status: ready`, `executor: null`, `claimed_at: null`, `attempt: 1`. No new attempt was created; completion was not accepted.
