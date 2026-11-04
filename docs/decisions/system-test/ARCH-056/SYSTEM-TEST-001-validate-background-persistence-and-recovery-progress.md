---
id: ARCH-056-SYSTEM-TEST-001
architecture_id: ARCH-056
title: Validate Background persistence and recovery progress at the selected boundaries
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 90
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-056-API-001
- ARCH-056-BACKGROUND-001
- ARCH-056-BACKGROUND-002
- ARCH-056-BACKGROUND-003
- ARCH-056-BACKGROUND-004
enables:
- ARCH-056-SYSTEM-TEST-002
created: '2026-11-03'
updated: '2026-11-04'
---

# ARCH-056-SYSTEM-TEST-001: Validate Background persistence and recovery progress at the selected boundaries

## Architecture

Architecture: `ARCH-056`. Parent: `docs/architecture/ARCH-056-background-persistence-and-recovery-progress.md`. Coordinator: `moda_architect`.

Definition revision: 3. **Defined but not materialised.** This is the integrated behavior validation task; the final naming cleanup task follows its acceptance. All five named implementation prerequisites must be Complete and architect-accepted before it is claimed. No execution, acceptance, task branch, worktree, commit or push is asserted by this definition.

## Objective

Independently prove the accepted dependency, ingress, outbound, settlement and initial-recovery contracts through the real entry points that own them. Produce nine complete scenario results with truthful evidence classes, exact executed-source and consumed-logger provenance, reproducible interruption/replay evidence and verified original failure diagnostics in actual emitted records.

## Context

The updated snapshot review identified U1, U2, U3 and C3. The follow-up specified exact-source settlement, safe pre-permit resumption/cleanup and explicit holds where outcome or lineage remains unproved. ARCH-056 additionally selects the same-message receipt lock order/verified Conversation identity part of MSG-09 and the same-transaction paid-meter projection reuse in BS-04. O7 and the broader review remain deferred according to the parent coverage register.

This task consumes the implementation contracts. It does not implement them, replace them with a test model, or approve uncertain-send billing. ARCH-028-BACKGROUND-013 remains blocked. Current Woo production composition still disables a new initial send; confirmed-send reconciliation must run before that gate. Finite candidate retries require an explicit failed-job repair action after exhaustion and do not establish universal eventual progress.

## Scope

One owning repository: `moda-interact-system-test`. Paths below are relative to it. The parent package's `docs/architecture/ARCH-056/deterministic-execution-map.json` records the complete file allowlist, nine scenarios and commands. This task and its parent package are self-contained; an earlier review patch is not an execution prerequisite. No application repository or nested Database source may be edited.

### Existing files to modify

| Path / symbol | Exact edit |
|---|---|
| `catalogue/scenarios.json` | Register exactly the nine rows below, with the complete required metadata, declared evidence class and `sourceRequirements: ["ARCH-056-SYSTEM-TEST-001"]`. |
| `catalogue/historical-system-test-map.json` | Add the symmetric mapping for this task to exactly those nine IDs. `sourceFile` is `docs/decisions/system-test/ARCH-056/SYSTEM-TEST-001-validate-background-persistence-and-recovery-progress.md`; record definition-baseline `historicalStatus: "pending"`, not a fabricated acceptance. |
| `docs/SHOPIFY-COVERAGE-MATRIX.md` | Regenerate through `npm run validate:catalogue -- --write`. Do not hand-edit generated rows. |
| `src/harness/selection.js:SUITES` | Import the frozen `BACKGROUND_PERSISTENCE_SCENARIO_IDS` from the new contracts module and add `"background-persistence": scenario => BACKGROUND_PERSISTENCE_SCENARIO_IDS.includes(scenario.id)`. Do not select by governance source requirements, implementation status or available executor. |
| `src/harness/cli.js:usage` | Add `background-persistence` to the existing suite help text only. Existing argument parsing remains unchanged. |
| `scripts/run-system-tests.js:createDefaultExecutors` | Require and merge `createBackgroundPersistenceExecutors` through the existing duplicate-registration guard. No executor registration belongs in generic `runner.js`. |
| `scripts/run-system-tests.js:createDefaultProvenanceProvider` | Include API with its `database` submodule and canonical Database for every selected ID in `BACKGROUND_PERSISTENCE_SCENARIO_IDS`; preserve existing selected-service descriptors and avoid duplicate names. Capture Background, Shopify and Messaging when executed. |
| `scripts/run-system-tests.js:main` | For `--suite background-persistence`, validate the complete nine-row plan and final result set using the new contract helper. Preserve ordinary evidence writing and nonzero failure exit. Attach the scoped case/provenance/logging artifacts through the existing artifact facility. Do not create a parallel runner or modify unrelated suite behavior. |
| `package.json:scripts` | Add only `system:background-persistence:plan = node scripts/run-system-tests.js --suite background-persistence --list` and `system:background-persistence = node scripts/run-system-tests.js --suite background-persistence --execute`. Existing `test:harness` already includes the new tests. |

### Exact new files

| New path | Responsibility |
|---|---|
| `src/harness/background-persistence/contracts.js` | Dependency-free frozen `BACKGROUND_PERSISTENCE_SCENARIO_IDS`, evidence classes, layers, required case IDs and per-case logging assertions; original source-requirement inclusion, symmetric provenance and plan/result completeness checks. |
| `src/harness/background-persistence/executors.js` | Nine executor registrations and mandatory business/logging/cleanup case-completion enforcement. |
| `src/harness/background-persistence/runtime.js` | Compose existing data-plane/runtime/provider/image factories at verified revisions; capture the actual worker stdout/stderr and installed Shared identity. |
| `src/harness/background-persistence/integration-driver.js` | Harness-owned direct-service driver for INTEGRATION rows only; load accepted modules, delegate real Prisma and use the consumed Shared factory for real sink capture. |
| `src/harness/background-persistence/fixtures.js` | Run-scoped tenants, recoveries, attempts, messages and mandatory template/consent state. |
| `src/harness/background-persistence/billing-fixtures.js` | Exact valid source-kind/status/period/counter/positive-event fixtures. |
| `src/harness/background-persistence/fault-controls.js` | Bounded disposable-DB barriers/faults, external provider/queue controls, harmless diagnostic markers, private synthetic sensitive sentinels and real Shared throwing-sink control. |
| `src/harness/background-persistence/observations.js` | Tenant-scoped durable state, queue/provider counts, lock/SQL observations and bounded actual JSON log capture before harness redaction. |
| `src/harness/background-persistence/assertions.js` | Identity, no-extra-effect, ledger/replay and raw-record message/stage/correlation/privacy/component assertions; deduplicate repeated buffer observations. |
| `src/harness/background-persistence/evidence.js` | Redacted case-result, execution/package provenance and logging-assertion sidecars within the existing run evidence directory. |
| `src/harness/background-persistence/queue-repair.js` | Retry the retained failed candidate through its original queue identity/data and the real worker. |
| `src/harness/background-persistence/dependency-scenario.js` | Dependency/source/build contract row and actual installed Shared package/entrypoint evidence. |
| `src/harness/background-persistence/ingress-scenario.js` | Real transaction ordering, duplicate and post-helper rollback row. |
| `src/harness/background-persistence/candidate-scenario.js` | Signed checkout and real candidate retry row. |
| `src/harness/background-persistence/admission-scenario.js` | Same-message delivery/cleanup/receipt races row. |
| `src/harness/background-persistence/uncertainty-scenario.js` | Real provider admission and unknown-outcome containment row. |
| `src/harness/background-persistence/settlement-scenario.js` | Exact positive/held billing and meter-read row. |
| `src/harness/background-persistence/lock-order-cases.js` | Settlement/compensation/final-permit contention cases for the settlement row. |
| `src/harness/background-persistence/finalization-scenario.js` | Actual initial finalization and follow-up replay row. |
| `src/harness/background-persistence/woo-scenario.js` | Normal disabled composition and confirmed-before-gate row. |
| `src/harness/background-persistence/repair-scenario.js` | Finite exhaustion and explicit retained-job repair row. |
| `test/harness/background-persistence-contracts.test.js` | Exact IDs/classes/cases/required logging assertions and rejection of incomplete or incorrect evidence. |
| `test/harness/background-persistence-registration.test.js` | Catalogue/map/selector/executor symmetry and unchanged unrelated selection. |
| `test/harness/background-persistence-provenance.test.js` | API/nested Database and consumed Shared inclusion; reject source/image/package resolution mismatches. |
| `test/harness/background-persistence-fault-controls.test.js` | Bounded barriers, failure propagation, sensitive sentinel isolation, real sink controls and cleanup. |
| `test/harness/background-persistence-results.test.js` | Missing/duplicate/blocked/not-run cases or logging assertions cannot become PASS; safe evidence survives failure. |
| `docs/BACKGROUND-PERSISTENCE-VALIDATION.md` | Commands, exact scenario/case/logging map, fixture boundaries, three sidecars, actual package capture and replay/cleanup instructions. |

Use `background-persistence`, `BackgroundPersistence` and `BACKGROUND_PERSISTENCE` for new test-owned directories, filenames, suite/command/artifact names, fixtures and symbols. Keep architecture/task IDs only as governance provenance; no old executable alias is introduced. The frozen contracts module must not import selection, executors or the runner and create a dependency cycle.

Every new JavaScript source/test file is below 300 lines. Split responsibilities across this exact list; do not hide a monolith in generated strings. Existing helpers are reusable read-only dependencies. Any additional path or upstream change requires an architect scope amendment.

## Out of Scope

No production implementation edits, application test edits, new application schema/migration, live provider account, live Meta/Shopify/Woo calls, paid charge/refund, production rollout, remote-collector configuration/query/retention/access verification, automatic recurring repair, unknown-send billing policy, global QPS/capacity claim, entire-ARCH-055 certification, unrelated performance optimization or `_index.md` edit. Do not reclassify existing containment scenarios or reopen accepted tasks.

## Requirements

### Real execution and source provenance

1. Read the accepted ARCH-056 implementation definitions/reviews and recheck their five canonical statuses. Use the launcher-resolved System-Test and parent task worktrees. Record actual paths, branch/HEAD, working cleanliness, nested recorded gitlinks and working submodule revisions. A ZIP or historical task SHA is insufficient provenance for execution.
2. Reuse `DisposableDataPlane`, PostgreSQL 17 + pgvector, existing Redis, `RecoveryCandidateRuntime`, `prepareOutreachRuntime`, messaging helpers, `ProductionBackgroundImage`, `BackgroundWorkerContainer`, command recording, cleanup and redaction. No new generic container framework, ORM model or system runner.
3. The default recovery runtime fetches Background `main` independently of its `backgroundRoot`. The scoped runtime must supply the existing `ProductionBackgroundImage` constructor with the verified accepted Background **full SHA** as `ref`, then compare the returned revision and image revision label to captured execution provenance. Record `/app/database/prisma/schema.prisma` and migration hashes from the image against its recorded dependency/approved contract. An opaque reused image or floating `main` mismatch is BLOCKED. Do not change the image builder or upstream source to bypass this check.
4. API is absent from current default provenance. Add `moda-interact-api` with `submodules: ["database"]`, plus canonical Database, even for the standalone REPOSITORY row. Require a recorded nested gitlink, a materialized working SHA, schema/migration hashes and a verified accepted relationship. Capture every actually executed service revision; never present local checkout provenance as image provenance when they differ.
5. Use only disposable, harness-created targets and synthetic secrets/tenants. External providers are deterministic local emulators. The BLACK_BOX rows enter through real ingress/queue/worker/HTTP boundaries; do not call `continueInitialOutreach` directly and label that a worker proof. The INTEGRATION rows may invoke actual service/fence methods with real Prisma, migrated PostgreSQL and explicit test-only instrumentation. Mocking the progress, billing, admission or finalization owner cannot satisfy either runtime class.
6. Every race uses independently observed PostgreSQL session IDs, explicit barriers and bounded waits. Every barrier has a `finally` release; fixture faults affect only that run's IDs and are removed during cleanup. A plain `Promise.all`, arbitrary sleep, helper mock, hand-written SQL behavioral model or direct state rewrite of an expected outcome is not race proof. Test-only transient trigger/control objects may exist solely inside disposable fixtures; they are not application migrations.
7. Preserve original application errors in propagation and verify their permitted diagnostics at the **actual Shared logging output boundary**. The approved consumer API is `logger.error(eventName, { ...safeFields, error })` (and the corresponding `warn` method). Do not accept a mocked `logger.error` call as evidence that a record was emitted. Assert parsed JSON from the real consumed Shared logger's sink or the actual service process's stdout/stderr, before the harness redacts or truncates evidence. A distinct safe originating message must remain identifiable with the correct failure stage and available correlation IDs; a generic replacement such as `PERSISTENCE_FAILURE`, a reason code alone, an omitted record or an error argument in the wrong position fails this obligation. Preserve only actually supplied, allowlisted provider/SDK/Prisma diagnostics. Never print or persist synthetic secret/PII sentinels used by negative tests. A fault must be observed at its intended boundary; a readiness or unrelated provider failure is not a passing reproduction.

### Actual Shared logging and failure evidence

**Consume the installed package.** The reviewed Background dependency and lockfile select published `@modainteract/moda-interact-shared` **3.0.0**. The sibling Shared source tree declares **3.1.0** and is explanatory source only. Record the declared dependency, locked version/resolved identity/integrity, actual resolved `/logging` entry point, installed package version, and relevant installed artifact hash for the executable used by each logger probe or runtime case. Obtain this evidence from the exact Background image or accepted direct-service execution environment. A sibling-source import, test alias, local rebuilt Shared copy, or a logger created with the System-Test repository's unrelated dependency is not consumer-runtime evidence. Do not upgrade Shared in this task. Missing or mismatched installed artifact provenance blocks the affected run.

**Test real records.** For an INTEGRATION case whose actual service accepts a logger, inject `createLogger` from that service's installed package with a sink that captures its already-sanitized `LogRecord`; serialize each captured record using `JSON.stringify` and assert the parsed JSON. Where the module owns its logger, observe the real default console sink in a scoped driver process. Never replace `createLogger` or the logging methods with a test double. For BLACK_BOX cases, parse actual complete JSON records from the running worker's existing container log snapshot. Existing `src/harness/background-worker-container.js:BackgroundWorkerContainer.snapshot()` and `src/harness/processes.js:ManagedProcess` buffers provide raw bytes from both stdout and stderr. Assert the actual envelope keys `event`, `level`, `service.name` and `deployment.environment.name`, plus the selected `data` diagnostic fields. Read and check those bytes before `src/harness/redaction.js:redactValue`, compact summaries or evidence writing. Repeated buffer snapshots must not count one record twice. Capture the relevant window before its bounded tail is lost; report truncation or incomplete JSON. Missing evidence cannot become PASS because the harness later scrubbed it or a log buffer discarded it.

**Separate propagation from serialization.** The approved Shared wire contract retains bounded `Error.name` and `Error.message`; it does not promise stack, `.cause`, arbitrary error properties, Prisma metadata, `AggregateError.errors`, or provider response serialization. Do not add stack logging or a generic error walker. If a selected semantic boundary creates an aggregate or owns a known cause, assert that it explicitly emits the safe original component diagnostics there, under explicit `operationError` / `cleanupError` fields or equally explicit fixed-role fields/correlated source records, and retains the original error objects for propagation. An aggregate wrapper message alone is insufficient proof that both original failures remain diagnosable. Existing WhatsApp `sourceError` / bounded `causeChain` projections remain the owning provider adapter's contract. The caller's local failure is not a second provider response. Preserve actual Prisma `code` and `clientVersion` when present; any metadata projection permits only safe model/constraint/field identifiers, never a complete `meta`, query or parameter dump.

**Keep diagnostic origin truthful.** An actual provider error may include only its supplied, safely extracted provider name, operation, status, request/trace ID, original error code/message and bounded details/non-JSON error excerpt. Preserve source wording apart from security redaction and explicit truncation. Record `redactionApplied` / `truncated` where the domain projection transforms data; the Shared factory does not automatically supply those flags. Internal SQL, finalization, queue-publication or cleanup failures use internal stage/correlation diagnostics and must not acquire fabricated `providerError` or `origin: provider_response` fields. A typed expected hold, duplicate or disabled gate without an upstream exception requires no invented original exception. Source errors converted to a retry/fallback still emit once at the boundary that received them; downstream records may add stage/outcome/correlation without duplicating the original response body.

**Preserve moderation's explicit privacy boundary.** The existing moderation adapter retains a bounded scrubbed original exception preview privately and emits `exceptionMessage` only in test/development. Exercise the real adapter and assert that preview in the allowed environment, plus its existing stage/code, assessment identity and retry outcome. In production configuration, assert bounded stage/code and absence of that original preview/raw SDK cause or input. Do not relax this contract, attach a raw SDK cause to the retry result, or synthesize a provider message downstream. This is the documented source-specific exception to ordinary originating-message diagnostics, not a claim that the retry consumer can reconstruct a discarded cause.

**Assert privacy before artifact redaction.** Use distinctive harmless diagnostic markers and separate synthetic secret/PII sentinels. On the real emitted records, assert the safe marker survives while the injected token, credential, signed URL, email/phone and specifically exercised prohibited payload portions do not. Verify the approved provider-specific bounds and flags, including the selected Meta trace-ID validation and nested array/detail flag propagation. Test the concrete allowed projection and fixture values; do not claim this proves recognition of every possible PII string. Do not pass arbitrary customer/provider objects to Shared and assume its generic redactor can recognize secrets or names embedded in free text. The original application exception remains unchanged for propagation; if a diagnostic portion cannot safely be retained, emit literal `[REDACTED]` for that portion with the appropriate flag.

**Logging stays best-effort.** In an INTEGRATION variant, use the real consumed Shared factory with a deliberately throwing sink. The actual ingress operation must still propagate its original database error and roll back exactly as in the nonthrowing-sink variant. The logger failure must not replace that exception or create another business mutation/retry/charge. Do not inject a throwing mock logging method, which bypasses Shared's isolation. A capture sink throwing while it records a harmless fixture marker is evidence of isolation, not a requirement for a log to survive its failed destination. Test spies and sink changes must be scoped and restored.

**Use bounded semantic fields.** Require the available opaque identity appropriate to the owner: shop/recovery/attempt/message/conversation/assessment ID, or the existing safe hashed candidate job ID plus attempt information. Hash-derived IDs are acceptable where the current contract deliberately avoids raw payload-derived job identifiers. Stage and correlation state must remain local to the invocation; concurrent cases must not inherit another job's mutable logger context. Do not require every ID before it exists, add message text/recipient/customer details, or modify public request/provider wire formats for logging. The stable event, `failureStage` or equivalent existing domain stage, `reasonCode`/outcome and known diagnostic code must distinguish ingress persistence, preparation/moderation, provider transport/response, receipt persistence, exact credit settlement, initial finalization, follow-up enqueue and candidate-index cleanup when those boundaries are exercised. Keep classifications separate from the source message.

Do not emit or accept a final applied/settled/sent-success record from a transaction that later rolls back. Assert bounded retry numbers and eventual disposition where the selected owner retries. BG-001 owns the accepted WhatsApp worker failure projection, BG-002 owns billing/status/compensation source diagnostics, BG-003 owns admission/receipt/Woo fence and existing Meta adapter diagnostics, and BG-004 owns initial progress/finalization/candidate cleanup diagnostics. This task only observes those accepted implementations.

The logging evidence ends at the actual Shared sink and emitted stdout/stderr records. It establishes no remote collector ingestion, indexing/searchability, retention or access guarantee. The parent execution plan's deployment-specific release-readiness handoff owns those checks when a collector will be the production debugging route; this task authorizes no collector access, configuration or deployment.

### Nine fixed scenarios

`contracts.js` exports `BACKGROUND_PERSISTENCE_SCENARIO_IDS` as the frozen, dependency-free list below and freezes each row's case and evidence contract. Every row uses `automation: "automated"`, `liveAuthorizationRequired: false`, `requiredFor: []`, the stated class for both `evidenceClass` and `requiredEvidenceClass`, and the task source requirement. This suite establishes selected ARCH-056 evidence, not a global release or capacity gate. `status: "implemented"` requires a registered executable implementation; a missing prerequisite remains a runtime BLOCKED result.

| Scenario ID | Domain / layer / class | Providers | Required case IDs |
|---|---|---|---|
| `REPOSITORY-BACKGROUND-DEPENDENCY-001` | REPOSITORY / L1 / CONTRACT | shared | D1, D2 |
| `MESSAGING-INBOUND-PERSISTENCE-001` | MESSAGING / L2 / INTEGRATION | shared, shopify, woocommerce | I1, I2, I3 |
| `RECOVERY-CANDIDATE-PROGRESS-001` | RECOVERY / L3 / BLACK_BOX | shopify | C1, C2, C3 |
| `RECOVERY-INITIAL-ADMISSION-001` | RECOVERY / L2 / INTEGRATION | shopify, woocommerce | A1, A2, A3, A4 |
| `RECOVERY-INITIAL-UNCERTAINTY-001` | RECOVERY / L3 / BLACK_BOX | shopify | U1, U2, U3 |
| `BILLING-INITIAL-OUTREACH-SETTLEMENT-001` | BILLING / L2 / INTEGRATION | shopify, woocommerce | B1, B2, B3, B4, B5, B6 |
| `RECOVERY-INITIAL-FINALIZATION-001` | RECOVERY / L3 / BLACK_BOX | shopify | F1, F2, F3, F4 |
| `RECOVERY-WOO-INITIAL-GATE-001` | RECOVERY / L2 / INTEGRATION | woocommerce | W1, W2 |
| `RECOVERY-FAILED-CANDIDATE-REPAIR-001` | RECOVERY / L3 / BLACK_BOX | shopify | R1, R2, R3 |

#### D — Dependency coherence and executed revisions

- **D1:** Inspect actual API `database` recorded/working revisions; require `followUpClaimKey`, `intentPurposeKey` and unchanged ARCH-055 migrations `20261102120000_arch055_rest_read_lifecycle`, `20261102121000_arch055_human_follow_up_claim_identity`, `20261102122000_arch055_upload_intake_identity`. Run the existing API `npm run typecheck` and `npm run build` through command recording without alternate schema overrides. Verify both normal scripts regenerate from API's nested schema. This is source/build CONTRACT evidence, not a runtime human-send certification.
- **D2:** Prove provenance includes API and its Database pin, canonical migration application, the actual Background image SHA/schema and each executed service. Deliberately mismatched/absent nested or image provenance fails the harness contract test and blocks a real run. Preserve historical stored claim keys; do not assume they equal new command UUIDs. Source-only equality does not certify deployment/quiescence.

#### I — Actual ingress serialization and rollback

- **I1:** Invoke the accepted real receive service against migrated PostgreSQL for distinct same-conversation provider IDs. Pause A after its parent/helper lock; observe B waiting before its child INSERT. Release A; both messages commit once, versions advance consecutively and only the first processable input establishes the frozen pending anchor/deadline/revision. Cover Shopify and Woo recovery fixtures and a standalone control.
- **I2:** Force both early duplicate lookups to miss. A commits; B's helper runs, then its unique INSERT loses. The whole losing transaction rolls back, the original error propagates, retry returns the existing duplicate, and only one message/version/pending update persists. Separately inject a post-helper/pre-insert error and prove zero partial helper/message/clock state.
- **I3:** Complete the old turn between the initial read and the new locked helper, then receive the next message; current state opens the next turn. Exercise HUMAN/control and audio/text lock winner orders with real service operations; preserve current revision, frozen future deadline and watermark behavior. Do not assert an aborted receive can be reconstructed by pending-turn repair.

#### C — Real candidate progression through durable interruptions

- **C1:** Create the candidate through signed Shopify checkout ingress. Fail after recovery insertion but before initial-attempt completion; allow the actual candidate job retry. Retain the same shop/checkout/generation/recovery and finish through the real worker, rather than direct initiation.
- **C2:** Fail after the sequence-one attempt exists and during required preparation. Retry must re-enter durable progress instead of acknowledging `no-op-existing`; reuse the same attempt and current eligibility checks. An unavailable dependency fails/retries visibly and is never reported as a sent/settled recovery.
- **C3:** Interrupt with exact retained credit and a PENDING unpermitted template message, then replay through the real worker. Reuse message, hard-limit usage, reservation and attempt identities; the final actual emulator request and committed credit occur at most once. Validate the real Shopify permit identity, not `recovery-outreach:<attemptId>` in a permit column. A historical missing usage/message link that prevents absence proof must hold, not invent fresh identity.

#### A — Same-message resumption, cleanup and receipt order

- **A1:** Compete two real template resume paths with dispatch key/admitted-at/control-revision all null and no provider ID or sent/delivered/read/failed timestamp. Revalidate the retained exact source, use the same canonical message/usage and current prepared template fields, then permit at most one provider request through the existing final CAS. A PENDING row carrying any receipt/failure timestamp must hold. Use the actual Shopify fence and Woo's explicitly test-enabled fence. No test enable setting is applied to ordinary Woo composition.
- **A2:** Let conditional pre-permit cleanup win. FAILED marking and exact usage deletion commit together; the losing delivery cannot use stale prepared state and must reclassify. Inject a failure between cleanup writes to prove rollback of both. Cover guarded historical FAILED-plus-usage residue without deleting admitted history.
- **A3:** Let permit acquisition win, including one-field-only permit evidence and a populated `providerDispatchControlRevision` without the other permit fields. Cleanup affects zero rows and preserves message/usage/credit ownership. It must reclassify and must not use an earlier unlocked read to delete another execution's admitted message. Any `MerchantConversationSendCommand` attached to the supposedly AUTOMATION initial message is a lineage conflict, never an initial-send replay identity.
- **A4:** Compete the accepted parent-first `markSent` transaction with final admission/replay on the same message. Observe Conversation-before-message receipt locking, reuse the verified Conversation ID, retain atomic receipt/clock persistence and avoid lock inversion. This is validation of the newly selected BG-003 architecture decision, not a claim that the earlier audit lead was reproduced. No blanket query-reduction claim follows from replacing a reread with a required lock.

#### U — Durable uncertainty, including a received HTTP success

- **U1:** Persist a permit without confirmed receipt, including legacy/partial permit evidence and an attempt currently marked FAILED; replay through the actual worker. Retain identities/credits, report held uncertainty, do not acknowledge a false successful completion and make zero additional provider requests. Permit/age/FAILED is not provider rejection or permission to charge/release.
- **U2:** The real emulator accepts a request while the existing failure proxy loses/withholds its response. Observe the durable permit and unresolved receipt, restart/retry as appropriate, and prove no resend, extra charge, release or replacement attempt. Retain expected RESERVED/AMBIGUOUS semantics according to the actual failure path.
- **U3:** Let the actual worker receive successful provider HTTP, then inject one failure in its receipt-persistence transaction. Prove provider acceptance preceded the failed database write. Replay keeps the same admitted PENDING message and exact held source; a missing persisted provider ID must not be guessed from recipient or a different provider event. No unconditional `failPrepared` usage deletion and no second HTTP call are allowed.

#### B — Exact settlement, source concurrency and bounded read reuse

- **B1:** Use actual `settleConfirmedInitialOutreach` with valid confirmed message/sentAt and exact original free, paid, purchased and promotional sources, for both platforms where valid. RESERVED commits through its existing owner; a repeated call returns `settled/already-committed` with the same original positive UsageEvent, reservation and source key, without another debit. Preserve purchased aggregate-counter plus exact-lot ownership and provider-specific reporting.
- **B2:** An exact already-COMMITTED paid source with its verified positive event replays after period rollover. A still-RESERVED historical paid source that cannot commit under current/open-period rules returns `held/paid-period-not-current`; it must not switch to a newer period or credit kind.
- **B3:** Exercise message-not-confirmed, absent/nonunique/cross-tenant lineage, AMBIGUOUS, RELEASED, compensated and noncommitted settlement outcomes. Require the accepted explicit held reason and zero partial ledger mutation/finalization. A resolved promise, returned replay token or arbitrary first/newest reservation is insufficient proof of settlement.
- **B4:** With actual independent transactions, race confirmed settlement against the actual 131026 status/compensation path in both legitimate winner orders. The selected settlement/compensation order is an exact owned pointer → Shop FOR KEY SHARE → message FOR UPDATE → authoritative unchanged-ownership reread → original ledger counter/reservation order. Provider-status likewise acquires Shop KEY SHARE from its preliminary exact pointer before its authoritative message read and unchanged CAS/attempt/command/UsageEvent writes; downstream compensation stays after commit. The exact original source changes at most once per authorized transition, corrected usage is not mistaken for the original positive event, and losing paths reclassify. Also settle two independently confirmed messages sharing an owner counter; verify counter/source invariants and bounded real retry behavior. Execute real positive, negative and delivered UsageEvent INSERTs and immediate foreign-key checks: an explicit-lock-only test that omits ledger/status inserts cannot prove this order safe.
- **B5:** Exercise final permit versus settlement using reachable states: PENDING admission wins, then the waiting settlement returns message-not-confirmed; confirmed settlement wins, then admission observes the existing receipt and makes no request. Do not manufacture one row that is simultaneously PENDING and confirmed to force both success branches. Observe final-fence Shop FOR UPDATE → Conversation → attempt → message FOR UPDATE → exact reservation FOR SHARE → permit CAS, and settlement/compensation Shop FOR KEY SHARE → message FOR UPDATE → original source-owner order. A fence holding Shop UPDATE makes settlement/status/compensation wait at Shop **before** message ownership; in the reverse order their Shop KEY SHARE makes the fence wait before it can hold descendants. Include the reachable status case of a SENT message with an unfinalized PENDING initial attempt. Pre-acquiring Shop's compatible referenced-row lock prevents the UsageEvent Shop FK from requesting an unacquired parent lock after message ownership. Settlement takes no later unacquired Shop/Conversation/attempt lock; the selected status writer retains its existing guarded attempt updates under the early Shop fence. The permit source lock is on the exact reservation, not an invented counter lock. Observe the real status handler's outer transaction rather than assuming a correct inner compensator proves the caller safe. Also force a stale final fence against the first Support finalization with no pre-existing thread: observe the actual finalizer's routing pointer → Shop FOR KEY SHARE → attempt FOR UPDATE → unchanged identity → real thread/notice inserts. Exercise immediate Shop/CheckoutRecovery FK checks in both Shop-lock winner orders; the fence cannot hold Shop/Recovery and wait for the finalizer's attempt while that finalizer waits for a new parent lock. This direct real-service/migrated-DB race belongs to this INTEGRATION case; a pre-created thread or mocked insert is insufficient.
- **B6:** Trace the actual selected paid commit path and prove the duplicate same-transaction meter/plan read removed by BG-002 stays removed, while Shopify's required handle and Woo's nonreportable null-handle behavior remain correct. Separate resolver/settlement SQL, locks, retries and delegated queries from this narrow read budget. Report the fixture and exact observed reads; do not infer total latency, fleet savings or QPS.

#### F — Confirmed finalization and follow-up state

- **F1:** Through the real worker/provider route, interrupt after confirmed receipt and exact credit settlement but before the initial finalizer finishes. Replay skips new offer/AI/template/admission/provider work, verifies original settlement and finishes records once.
- **F2:** Interrupt after the atomic sequence-one attempt/optional Support notice commits but before recovery status convergence. Replay retains exact receipt/sentAt and deterministic Support identity, emits no second notice/charge/send and converges only the allowed recovery transition. Preserve opt-out replay and newer ENGAGED/terminal state.
- **F3:** Persist `followUpDueAt: null`, change current follow-up policy and replay; null remains authoritative. Separately preserve a non-null persisted due date across policy change and a failed queue publication. Repair uses that date and deterministic queue ID, not a newly derived date or duplicate future job.
- **F4:** Interleave consent/STOP, order completion, expiry and terminal-state changes with replay. Current guards prohibit an unsent request; they do not erase a genuinely confirmed receipt or redirect its accounting. Finalization must not overwrite newer terminal/engaged state or manufacture fresh send eligibility.

#### W — Woo gate placement and parity

- **W1:** Instantiate the actual normal Woo composition without its test-only enable callback. New and prepared-but-unpermitted initial sends remain production-disabled with no provider request or new charge. Assert this expected gate behavior as a passing case; it is different from the harness being BLOCKED by missing prerequisites.
- **W2:** Seed valid exact confirmed Woo receipt/attempt/source lineage and invoke the actual Woo entry/continuation path with ordinary production composition still disabled. Confirmed settlement/finalization runs before the gate, preserves original identities and provider-safe accounting, and performs no new HTTP call. Corrupt/ambiguous lineage holds. This direct-service/migrated-DB evidence is INTEGRATION and does not claim Woo initial sending is enabled in production.

#### R — Exhausted jobs and explicit repair

- **R1:** Keep a controlled post-insert required-state failure active for all configured candidate attempts. Observe the real retained failed job, its original ID/data and finite attempts; it must not be recorded completed by `no-op-existing`. No recurring scanner or extra task is added.
- **R2:** Remove that fault and explicitly retry the retained job with the existing queue retry operation. The actual handler reaches `materializeMaturedCandidate(originalJob.data, {jobId: originalJob.id, ...existing options})`, reuses all durable identities and completes eligible progress once. Do not invoke a mocked progress owner or create a fresh recovery/generation/job merely to obtain a passing case.
- **R3:** Explicit repair of an uncertain/lineage-conflicted retained job continues to hold with `InitialOutreachHeldError`, no provider/debit/release and a noncompleted job result. Record that exhaustion, lost future jobs and absent future triggers require an explicit owner/action; the tested route is bounded repair, not a claim of automatic eventual completion.

### Required logging evidence within existing cases

The following assertions/subruns are mandatory within the existing cases; no scenario or case ID is added. A hard process termination cannot emit a post-termination error; such a subrun proves its interruption using durable state and the process/provider chronology. Its exception-injection companion supplies any required error-emission assertion.

| Existing case | Added logging evidence |
|---|---|
| **D2** | Capture the actual consumed Shared 3.0.0 package and `/logging` resolution from the accepted execution environment/image, alongside existing source/schema provenance. A real factory probe confirms event-plus-fields usage, nested Error name/message output and omission of stack. A negative harness test rejects absent/mismatched package provenance and mocked/sibling-source capture as terminal evidence. This remains CONTRACT evidence. |
| **I2** | The duplicate/controlled post-helper failure is attributed to ingress persistence with the actual safe originating name/message and Conversation correlation. Verify rollback/rethrow alongside emitted JSON. Repeat the controlled failure with a throwing real Shared sink and prove the original error/rollback are unchanged. Also run one scoped inbound failure through the accepted real WhatsApp worker, observing its actual `whatsapp.job.failed` record with original safe message/code and job/attempt context, without a second raw field reintroducing sensitive text. A separate post-commit engagement failure must be labeled after-commit while retaining the committed receive. Rejection-only, service-only or mock-callback evidence cannot certify worker output. Missing fields caused by wrong logger argument placement must fail the emitted-record assertions; no deliberate production corruption is needed. |
| **C2** | A required preparation dependency failure produces a source-boundary diagnostic even when converted to the initial-template technical retry. Through the real moderation/SDK adapter and local provider fixture, check the permitted original safe preview in test/development, assessment/stage/code and retry correlation. The paired production-configuration privacy check belongs to A2's INTEGRATION driver. A worker result such as `OutboundPreparationRetryError` or a reason code alone is insufficient source evidence. Initial scope remains retryable and retains its pending message/usage. C2 retains its required real worker/HTTP route; direct service execution cannot replace it. |
| **A2** | Capture the original cleanup SQL failure from the actual rollback variant with exact message/attempt correlation. Add a legitimate known-rejection/reconciliation-failure variant through the real provider adapter and migrated DB: both the primary and reconciliation component messages must be observable under the same attempt/message correlation, while the thrown aggregate retains both original objects. For the source Meta response variants exercise structured and non-JSON errors, safe original code/message, bounded details, invalid nested `fbtrace_id` rejection/redaction, and nested detail/array redaction/truncation flags. Check synthetic sensitive values are absent in emitted JSON. In the actual moderation adapter's production-configuration companion, assert safe stage/code and absence of original preview/raw SDK cause/input; use the real adapter and local provider fixture through this INTEGRATION driver. Do not force the selected technical-moderation retry to run destructive cleanup solely to manufacture this aggregate. |
| **U1** | A permit/partial-permit unknown outcome is classified as a held initial outcome with the existing message/attempt correlation; it is not reported as successful reconciliation or a new provider rejection. No fabricated provider-error body is permitted when replay received no new upstream error. |
| **U2** | The real lost-response path emits the actual source SDK/transport diagnostic with its available bounded cause diagnostics, then contextual uncertainty/retry classification. Match the failure to the observed emulator request, permit and worker attempt. No provider response code/body is invented where none reached the SDK. Source emission occurs once for that request failure, while a later worker failure may add context. |
| **U3** | Distinguish successful provider HTTP from the subsequent local receipt-write failure in log stage/origin and provider/DB chronology. The original safe database message/code and message/attempt correlation survive. There is no fabricated provider rejection/error body and no erroneous `afterProviderError` invocation. Replay reports uncertainty without a second request or destructive cleanup. |
| **B3** | Existing expected held reasons remain distinguishable from technical settlement failure. In a controlled exact-source read/commit failure companion, assert the original bounded SQL/Prisma message and safe code with source/message correlation and the same zero-partial-write invariant. Do not infer that a held result itself had a provider exception. |
| **B5** | In a controlled actual Woo final-permit SQL-failure companion, capture the real dependency diagnostic rather than `new Error("PERSISTENCE_FAILURE")`. Assert original safe message/code and permit-stage identity; preserve the real exception. Logging controls must not replace real FK-sensitive contention or the original two winner-order observations. |
| **F1, F2, F3** | On exception-based receipt/settlement/finalization/status/follow-up publication interruption variants, capture the originating message and correct stage/identities before replay. Finalization or queue publication errors are internal, not Meta errors. Successful replay must distinguish confirmed reconciliation from fresh sending. For F3 preserve the original stored-null/date and deterministic job identity; an error-only log without those durable assertions does not pass. A deliberate hard kill is recorded truthfully without requiring impossible after-kill emission. |
| **W1, W2** | Expected ordinary Woo disabled-gate and confirmed-before-gate outcomes must not fabricate a provider failure. A corrupt/ambiguous lineage hold remains observable as its accepted reason/outcome and opaque identity, without pretending a new HTTP request was made. |
| **R1** | Finite retry exhaustion retains the actual source failure diagnostics and failed-job/attempt correlation. Include one bounded actual worker materialization-plus-candidate-index-cleanup failure variant; capture both original component messages at the known aggregate creation/source boundary, then contextual worker failure. A single aggregate wrapper or concatenated synthetic replacement is insufficient. A source exception converted to a lookup/retry outcome still has its source log. |
| **R3** | Explicit repair that remains held preserves the accepted held reason and original retained job correlation. `InitialOutreachHeldError` is a truthful internal control outcome, not an upstream error. The retained noncompleted job, zero extra effects and any actually available original source diagnostic are proved separately; do not invent missing historical source details. |

All other case IDs remain in the complete case ledger with their existing business assertions. An absence-of-error assertion cannot substitute for the listed positive failure/emission checks. Log matching must include case-specific opaque fixture identity/attempt or a proven causal association with the actual provider request and failure schedule; a matching string from an unrelated case is insufficient.

### Complete, truthful result enforcement

`contracts.js` holds exactly nine IDs and all case IDs above. The suite predicate selects by membership in `BACKGROUND_PERSISTENCE_SCENARIO_IDS`; governance source requirements do not determine selection. Contract checks reject a missing/extra/duplicate row, wrong domain prefix/class/layer, missing original source requirement, asymmetric historical mapping or absent executor. Initial rows contain `sourceRequirements: ["ARCH-056-SYSTEM-TEST-001"]`; require that entry by inclusion, not an exclusive singleton. Later architect-approved requirements with valid symmetric historical mappings are allowed, including `ARCH-056-SYSTEM-TEST-002` after the naming migration. Its provenance attachment must not change suite membership, evidence classes, case IDs or logging assertions. `--suite background-persistence` with narrowing selectors cannot masquerade as the complete plan. Targeted debugging may use `--scenario` alone but does not satisfy this task.

Each executor records every required case outcome and explicitly returns PASS only after every required business, logging and cleanup assertion passes. `contracts.js` also freezes the required logging assertions by existing case ID. Missing emission, a generic replacement, wrong stage/origin, a missing aggregate component, a secret hidden only by final evidence redaction, truncated capture, wrong-package/mocked capture or an unexecuted required logging assertion prevents PASS. Wrap the nine executors so an omitted case, unexecuted subcase, undefined result or swallowed fault cannot exploit the generic runner's default PASS normalization. Infrastructure/setup unavailability returns the existing `ScenarioBlockedError`; violated behavior returns `ScenarioFailureError`, with original redacted cause evidence. BLOCKED, FAIL, NOT_RUN and NOT_APPLICABLE all prevent this task's acceptance. Do not map a business held outcome to a harness failure when held is the required behavior; assert the durable/job result and pass that case only when the hold is correct.

Preserve the normal run JSON, summary and command evidence for failures. Write `background-persistence-cases.json`, `background-persistence-execution-provenance.json` and `background-persistence-logging.json` as redacted artifacts in the same existing run directory. Include run/scenario/case IDs, observed failure boundary, real entry route, fixture IDs, before/after durable state summaries, provider/request and credit-effect counts, barrier schedules, exact image/dependency/consumed-Shared identities and cleanup result. Record actual results, never prefilled PASS. A suite completeness failure must produce a nonzero exit and clearly failed/blocked evidence, not a successful summary beside a hidden missing-case warning. Do not alter generic runner/result schemas or other suites to implement this scoped guard.

The logging sidecar records run/scenario/case ID, assertion ID, actual result, boundary/event, capture mode (`shared-sink-json` or `runtime-json`), environment, service identity, installed package provenance reference, safe correlation IDs, original-safe-message/paired-component presence, stage/origin correctness, sensitive-sentinel absence, bounds/flag checks, source-emission count and any buffer truncation. Persist only the selected safe parsed records/fields and truthful results. Never retain a raw Error object expecting the generic evidence redactor to preserve its message; it does not. Keep raw captures and sensitive fixture values in bounded temporary memory, assert them before harness redaction, and omit them from artifacts/progress output/failure diffs. On a privacy failure retain a safe failing assertion identifier, not the leaked sentinel. The existing evidence writer still applies its normal secondary redaction before persistence.

Extend the already owned contract/provenance/fault-control/result tests to reject each missing or invalid logging obligation above. Use FAIL for incorrect emitted behavior and BLOCKED when the required accepted source/runtime/control or complete capture cannot be established. Preserve safe failed/blocked artifacts; neither result satisfies acceptance.

## Work Items

- [ ] Verify all five accepted prerequisite revisions, actual source/image/dependency relationships and consumed Shared package identity.
- [ ] Register exactly nine scenarios, symmetric historical mapping, generated matrix, suite, executors and API provenance.
- [ ] Implement the named modules with actual service/worker/provider routes and scoped bounded fault controls.
- [ ] Implement strict case/plan/result/logging guards and tests for missing, blocked, incorrect-class, wrong-package, privacy-only-after-redaction and mismatched-revision evidence.
- [ ] Execute the nine-scenario suite and capture source, case, command, concurrency, actual emitted JSON/logging assertion and cleanup artifacts.
- [ ] Return defects to their owning task/architect; record exactly which required case remains blocked or failed.

## Interfaces / Contracts

Consume accepted BG-002 `settleConfirmedInitialOutreach({shopId, recoveryId, outreachAttemptId, outboundMessageId})` results: `settled` with `committed`/`already-committed` and exact source evidence, or `held` with its documented reason. Consume its existing-source revalidation contract; never call current admission to manufacture historical settlement.

Consume BG-003 `inspectInitialOutreachAdmission(scope)` classification `absent | prepared | confirmed | failed | held`, and `resumeInitialTemplate` with the same canonical message, exact retained source and current prepared template fields. Preserve existing `findExistingAdmission` compatibility. Safe preparation requires no permit/receipt/control-revision evidence; either primary permit field or standalone dispatch-control revision is uncertainty evidence, and any human command linkage conflicts with initial AUTOMATION ownership.

Consume BG-004 `continueInitialOutreach({shopId, recoveryId})` results `needs-preparation | reconciled | blocked | held`; actual worker holds propagate `InitialOutreachHeldError`. Direct calls are permitted only in the explicitly INTEGRATION rows. Real candidate retry/repair keeps the original worker entry and options, including accepted ARCH-028-BACKGROUND-012 semantics.

No public API, queue schema, Shared package or application database contract is changed by this task. All source class/field names must match the accepted upstream definitions; an integration mismatch is an owner handoff, not authority to patch another repository.

## Dependencies

- `ARCH-056-API-001` — accepted API dependency and normal generation contract.
- `ARCH-056-BACKGROUND-001` — accepted ingress transaction order and existing WhatsApp worker failure diagnostics.
- `ARCH-056-BACKGROUND-002` — accepted exact-source settlement/revalidation and paid read reuse.
- `ARCH-056-BACKGROUND-003` — accepted persisted admission, safe cleanup/resumption, receipt order and existing Meta adapter diagnostic corrections.
- `ARCH-056-BACKGROUND-004` — accepted initial continuation and explicit worker repair route.

These are the only task dependencies. Do not add blanket ARCH-055-API-009 or other terminal-suite dependencies. A real missing build/service prerequisite is reported precisely as BLOCKED. A developer's optional manual checkpoint is not a synthetic dependency or approval flow.

## Enables

- `ARCH-056-SYSTEM-TEST-002` — final System-Test naming migration and existing-validator guard, after this task is accepted. This task does not begin that work or change its pending status.

## Acceptance Criteria

- [ ] All five upstream tasks are accepted/Complete and actual executed revisions match the recorded evidence.
- [ ] The semantic `background-persistence` CLI plan selects exactly nine expected IDs independently of governance metadata, with registered executors and the frozen evidence classes/case sets. Later valid symmetric source-requirement additions preserve the same selection.
- [ ] Actual ingress serialization/rollback, candidate re-entry, same-message/cleanup/receipt races and both provider-uncertainty boundaries pass with deterministic observations.
- [ ] Exact source settlement/holds, concurrent accounting/final-fence cases and the selected paid read budget pass without unknown-outcome policy changes.
- [ ] Support/status/stored-null due-date/queue replay, Woo disabled/confirmed-before-gate behavior and finite failed-job repair pass through their declared boundaries.
- [ ] All required cases run; no mock owner, fixture-written result, missing executor, implicit PASS, skipped case or BLOCKED result is accepted as complete proof.
- [ ] Required real Shared-sink/runtime JSON assertions pass against the consumed published package, preserving permitted original messages/correlation, source fallback logs and paired errors, with redaction, production moderation privacy and sink-failure isolation.
- [ ] Normal artifacts and all three sidecars contain actual API/nested Database/image/Shared provenance, required logging results and complete cleanup. Mock-only logging assertions or artifacts sanitized only after emission do not certify behavior.
- [ ] All changes remain inside the exact System-Test allowlist and every new JavaScript module/test is below 300 lines.
- [ ] Evidence makes no deployment, live-provider, full-ARCH-055, broad-review closure or production capacity claim.

## Validation

Use the existing workspace Node bootstrap and locked repository dependencies. Run from the launcher-resolved implementation worktree. The two `system:background-persistence` scripts are new deliverables, not baseline commands.

```bash
npm run validate:catalogue -- --write
npm run validate:catalogue
npm run lint
npm run test:harness
npm run system:background-persistence:plan -- --json
npm run system:background-persistence -- --json
git diff --check
```

The dependency scenario additionally executes API `npm run typecheck` and `npm run build` via the existing command recorder. The runtime applies the canonical migrations and builds/starts the exact accepted service image through existing helpers. Do not replace these operations with an unrelated generated client, `db push`, live database or test-only schema override.

Preserve existing `RECOVERY-PROVIDER-AMBIGUOUS-001`, `RECOVERY-PROVIDER-CRASH-001`, `RECOVERY-PROVIDER-UNKNOWN-ID-001` and `MESSAGING-STATUS-001` contracts. Their old containment claims do not certify uncertain billing, general early-status retention or every new initial continuation boundary. The nine selected scenarios provide this task's evidence; avoid unrelated broad reruns unless a concrete changed harness contract requires them.

Report command exit/result, exact scenario/case/logging assertion outcomes, required versus actual evidence class, failed/blocked boundary, capture/package identity and resources cleaned. The existing validation commands also execute the scoped logging completeness/negative tests; no additional broad suite or live provider is required. Test duration, bounded local waits and selected SQL observations are fixture evidence; they are not throughput/latency-capacity measurements. Run output and a local source-count comparison cannot establish production QPS.

## Implementation Notes

Follow the parent architecture's common worktree, logging and evidence requirements. Existing tooling can return BLOCKED when required containers, builds or migrations are unavailable; preserve that distinction from a failed business invariant. New fixtures/control code belongs exclusively to System-Test. The final naming task follows acceptance and reruns the same nine scenarios, 30 cases and 39 logging assertions. No execution result is supplied by this definition.

### Stop Condition

Stop and return a precise blocked/failed owner handoff if an upstream contract or accepted revision is unavailable, a deterministic required boundary cannot be exercised with the allowed harness, or a correction needs an application/schema/unnamed-file edit. Do not weaken assertions, delete an inconvenient scenario, change evidence class to make it pass, or supply a hand-written progress implementation.

After the complete selected suite and validation pass, finish this task's Completion Report with actual provenance/results, publish the normal mirrored task evidence, set `status: review`, return to `moda_architect` and stop. Do not mark the architecture Complete, begin another task, merge to main or amend another task/index.

## Completion Report

This section belongs to the implementing repository agent. No implementation is recorded by this definition.

### Status

Not Started

### Files Changed

Pending implementation.

### Work Completed

Pending implementation.

### Validation Results

Not run. Record exact commands, exit results, failures, warnings, source/build/schema provenance, scenario evidence and cleanup; do not copy planned checks as completed results.

### Deviations

None at definition time. Record actual deviations and their architect disposition before review.

### Assumptions

The reviewed snapshot and accepted prerequisite contracts are the definition baseline. Recheck the real current checkout and task state at launch.

### Unresolved Issues

Pending implementation evidence. Preserve the task's explicit held/deferred and blocked-policy boundaries.

### Architectural Concerns

Return changes to ownership, contracts, schema, transaction boundaries, durable-state semantics, queue behavior, security or another repository to moda_architect before expanding scope.

## Architect Review

This section belongs only to moda_architect. Definition authoring is not implementation acceptance.

### Review Status

Pending

### Review Notes

Awaiting an implementation submission and its evidence.

### Reviewed Files

No implementation submitted.

### Validation Reviewed

No implementation validation submitted.

### Architecture Conformance

Pending review against the parent architecture, task allowlist, interface contracts, repository boundaries and failure requirements.

### Follow-up

Pending implementation review; no enabled task may be started by this task's executor.
