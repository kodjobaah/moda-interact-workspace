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
status: in_progress
priority: 20
executor: developer
claimed_at: 2026-10-21T17:59:48Z
attempt: 1
depends_on: []
enables:
  - ARCH-045-SHARED-002
created: 2026-10-20
updated: 2026-10-21
---
# Define Shopify consent synchronisation and canonical identity contracts

## Architecture

Architecture ID: `ARCH-045`
Architecture document: `docs/architecture/ARCH-045-shopify-whatsapp-consent-gated-recovery.md`
Coordinator: `moda_architect`
**Lifecycle:** materialised and claimed using `/moda_developer_create ARCH-045-SHARED-001`. The canonical developer execution claim is **Attempt 1** (`status: in_progress`, `executor: developer`, `claimed_at: 2026-10-21T17:59:48Z`). The two implementation patch revisions are not separate task attempts. The implementation is ready for developer reconciliation once the remaining evidence/acceptance requirements below are resolved; this task is **not** yet in review or architect-accepted.

## Objective

Implement and test a **single published Shared implementation** containing (1) a minimal Shopify WhatsApp consent-state sync event for existing queues, (2) canonical E.164-equivalent exact-recipient phone helpers and portable golden vectors, and (3) validated Shopify numeric customer ID ↔ GraphQL Customer GID conversion. The sync event updates local consent via Background but can never request checkout reconciliation or start a recovery. `ARCH-045-SHARED-003` is Superseded and fully absorbed here; separate `ARCH-045-SHARED-002` publishes the accepted package.

## Context

Existing Shopify webhook/Background queues do not carry the WhatsApp consent-sync topic, and existing customer-phone helpers only trim/strip digits while Shopify privacy webhooks use numeric IDs versus GraphQL GIDs. All services should consume one versioned canonical event schema and one identity implementation, not independently reproduce them. Both sets of interfaces are defined and share `moda-interact-shared` ownership; this task consolidates the former SHARED-003 helper implementation into SHARED-001.

## Scope

**Shopify-to-Background event contract**
- Add the versioned `ShopifyWhatsAppConsentSyncJobV1Schema` (repository naming may vary), typed payload `{schemaVersion:1,shopId,shopifyCustomerId,deliveryId,triggeredAt}`, strict runtime validation, stable deterministic job ID and a **distinct** job name on an existing approved Shopify BullMQ queue. Exclude phone, consent Boolean, checkout key and recovery-wakeup fields; do not route it through checkout-created/updated parsing.
- Export producer/consumer runtime schemas and constants from published `@modainteract/moda-interact-shared` entrypoints; test malformed/replayed input, duplicate IDs, cross-shop identity and existing checkout event compatibility.

**Cross-platform exact recipient and Shopify customer identity**
- Implement one browser-safe/Node-safe canonical phone validator/normaliser that produces a verified E.164-equivalent recipient or a typed rejection. National-format numbers require **explicit verified country context**; do not infer permission or guess from locale. Provider `wa_id`/digits-only send addresses remain service-owned adapters.
- Implement validated numeric Shopify customer ID ↔ `gid://shopify/Customer/<numeric>` conversion/equality; reject malformed, zero/overflow and wrong-resource GIDs or arbitrary principal strings. Consumer services remain responsible for authenticated shop/tenant binding.
- Publish deterministic compatibility fixtures for UK national/international equivalence, ambiguity, extensions, rotation/reassigned phone, numeric webhook/GID conversion and invalid IDs. WooCommerce PHP code must pass matching vectors without importing Node implementation source.
- Keep only reusable codec, validator, identity/job helpers and tests in Shared; no Prisma, service secrets, API calls, business consent policy, provider sends or queue infrastructure creation.

## Out of Scope

- No new BullMQ queue, separate queue schema for Woo, HTTP handler, provider lookup, CustomerPhone write, recovery candidate, recovery retry job or source publication in this implementation task.

## Requirements

- [x] Exactly one versioned consent-state synchronisation schema with deterministic job identity and no authority to create checkout recovery, send messages or carry consent decisions.
- [ ] Distinct job routing on existing queue infrastructure cannot be confused with checkout event parsing; Shopify ingress and Background use the same published runtime validator and version.
- [ ] Canonical phone identity is stable across explicitly scoped national/international representations and rejects unparseable/ambiguous input; shared fixtures cover Node writers/readers and Woo PHP compatibility.
- [x] Numeric/GID Shopify customer identity conversion validates resource kind and format, but never substitutes for shop/customer authorisation.
- [x] No independent copies of a cross-service event schema or identity helper, new queue, provider lookup, local consent policy or recovery wakeup.

## Work Items

- [x] Add minimal versioned consent-sync schema, distinct existing-queue job name and deterministic ID generator; validate/reject extraneous consent/phone/recovery payload fields.
- [x] Implement exact international phone normalisation/validation requiring verified country context when needed; publish typed failures and deterministic vectors.
- [x] Implement strict Shopify numeric ID/GID conversion and customer-kind validation with fixtures for malformed, other-resource and out-of-range identities.
- [x] Export browser/Node-safe entrypoints and compatibility fixtures from the approved package subpaths, without importing server-only code in browser exports; keep hashing primitives in a Node-only subpath when required.
- [ ] Add focused schema, idempotency, checkout queue compatibility, exact recipient, ID conversion, PHP fixture parity and export tests; preserve existing published contract compatibility.

## Interfaces / Contracts

**Owner:** `moda_shared` (`moda-interact-shared`), single implementation task `ARCH-045-SHARED-001`; release owner `ARCH-045-SHARED-002`.

- **Sync event:** `ShopifyWhatsAppConsentSyncJobV1Schema` (or repository-equivalent), `{schemaVersion:1,shopId,shopifyCustomerId,deliveryId,triggeredAt}`, deterministic job ID, existing queue with distinct job name. Producer `ARCH-045-SHOPIFY-001`, consumer `ARCH-045-BACKGROUND-003`. No checkout recovery side effect.
- **Canonical recipient helper:** Node Shopify/Background/Woo API callers import the published identity entrypoint; Woo PHP consumers test equivalent golden vectors.
- **Shopify ID helper:** numeric webhook IDs and GraphQL customer GIDs compare after strict validation; shop ownership is validated by consumers.
- **Publication:** `ARCH-045-SHARED-002` publishes this *one accepted implementation task*; no implementation in publication task.

## Dependencies

None

## Enables

- `ARCH-045-SHARED-002`

## Acceptance Criteria

- [x] Event schema and deterministic ID reject malformed/PII/consent/recovery fields; existing checkout parser and event versions remain intact with distinct routing.
- [x] A valid numeric Shopify customer ID and GraphQL Customer GID normalise consistently, while invalid/wrong-resource/out-of-scope identities fail validation without granting authorisation.
- [ ] Exact phone helpers produce the same canonical result under verified country context, reject ambiguous/invalid input, and have deterministic UK, international, extension, rotation, reused number and PHP parity vectors.
- [ ] Published entrypoint exports are runtime safe (no server-only secret or Node imports in browser-safe surfaces); all downstream consumers can import one shared contract without copying helpers.
- [x] No new queue, consent-triggered recovery, provider lookup or consent business policy in Shared.

## Validation

- [x] Repository-declared focused sync-event schema/job ID and checkout-queue compatibility tests.
- [ ] Repository-declared phone/Shopify ID codec fixture tests and PHP interoperability golden vectors.
- [x] Entrypoint/export typecheck/build as applicable and `git diff --check`.

## Stop Condition

After completing only the defined Work Items, Acceptance Criteria and required Validation, record the canonical task worktree/branch and start-of-attempt synchronization evidence, populate the Completion Report, set `status: review`, return control to `moda_architect` and **STOP**. Do not launch enabled or unrelated tasks. Publication is separately owned by SHARED-002; stop after implementation review.

## Implementation Notes

Use existing Shopify Shared naming/style. Preserve published export compatibility. Stop at review: publication is a separate task.

For this **developer-owned** attempt, preserve the `/moda_developer_create` claim and use `/moda_developer_update ARCH-045-SHARED-001` for reconciliation/self-review after required acceptance evidence is complete. The launcher-prepared packet and physical worktree/synchronisation evidence must be recorded, not inferred. Preserve `docs/decisions/**/_index.md` untouched until the developer explicitly closes the architecture documentation session. New runtime structured logging uses `@modainteract/moda-interact-shared/logging` where applicable. No source outside this task's owner repository may be changed unless explicitly authorised by the architecture.

## Completion Report

### Status

In Progress — canonical **Attempt 1** claimed via `/moda_developer_create` at 2026-10-21T17:59:48Z. The initial implementation patch and follow-up fixture correction were both applied within this one claimed attempt. Passing local validation is recorded below; remaining formal review prerequisites are not yet evidenced. Developer self-review and explicit completion are separately controlled by `/moda_developer_update`.

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
- Deferred package publication to `ARCH-045-SHARED-002`; no new queue, provider lookup or consent-triggered recovery wakeup was introduced.

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
| PHP execution against portable fixture JSON | **Not evidenced**; Node fixtures do not prove PHP-runtime parity |
| Implementation task branch commit/push | **Confirmed** — `12f6ff5` (`feat(shared)`) at `HEAD` and `origin/task/ARCH-045-SHARED-001` in the Shared implementation worktree |
| Parent task report commit/push | **Confirmed** — `7a38e513` (`docs(ARCH-045-SHARED-001): record developer attempt 1 evidence`) successfully pushed to `origin/task/ARCH-045-SHARED-001` |

#### Task worktree evidence

- Latest evidence source: developer terminal capture `typescript(20261021-191359)`. This records launcher `--route-only --json`, Git status/log and Git `worktree list --porcelain` for both repositories, followed by successful parent commit and push.
- Launcher confirms canonical parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-045-SHARED-001`, `task/ARCH-045-SHARED-001`. Parent branch was at `ebc327e35` before report commit `7a38e513`; push to `origin/task/ARCH-045-SHARED-001` succeeded.
- Launcher confirms dedicated Shared implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-045-SHARED-001`, `task/ARCH-045-SHARED-001`. Git status reported a clean branch with implementation commit `12f6ff5` at `HEAD` and `origin/task/ARCH-045-SHARED-001`.
- Both dedicated physical worktrees and their branch associations are listed in `git worktree list --porcelain`; path naming is not the sole evidence.
- Canonical `/moda_developer_create` parent task claim: `executor: developer`, `attempt: 1`, `claimed_at: 2026-10-21T17:59:48Z`.
- **Still outstanding:** actual launcher `--prepare` packet and start-of-attempt synchronization/recursive submodule evidence were not included. The later `--route-only` output is route confirmation, not a substitute for the preparation packet.

### Deviations

A fixture-only correction was required after the first test run; production phone validation was preserved. No cross-repository implementation scope expansion was observed. Remaining workflow evidence must be reconciled before self-review.

### Assumptions

The 21 October developer-claimed parent snapshot is the patch baseline. The two implementation patch revisions represent one developer-owned Attempt 1, not two separately claimed attempts. This report records observed local validation, without asserting remote publication. Canonical phone identity does not demonstrate phone ownership, WhatsApp reachability or consent. ARCH-045 imposes no arbitrary consent-expiry deadline.

### Unresolved Issues

1. Locate the original `/moda_developer_create`/launcher `--prepare` packet or other contemporaneous start-of-attempt evidence proving parent/implementation synchronization and recursive submodule preparation. The physical worktree locations, branches and latest commits are now independently evidenced. Do not rerun a claim/prepare command against an already claimed task solely to manufacture evidence.
2. The explicit PHP fixture-parity criterion remains unchecked: supply actual PHP interoperability test evidence or obtain an architecture-approved scope change assigning PHP parity execution to the downstream WooCommerce consumer task. A JSON file's parseability in PHP is not equivalence validation.
3. Review npm audit warnings separately if relevant to the intended release; this task did not run a dependency audit remediation.

### Architectural Concerns

No new cross-service architecture change observed beyond the agreed event and identity contracts. Downstream Shopify/Background consumers must import the published Shared package (after `SHARED-002`) and must not interpret sync events as permission to create or wake checkout recoveries.

## Architect Review

### Review Status

Pending — no implementation reviewed.

### Review Notes

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
