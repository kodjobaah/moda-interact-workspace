---
id: ARCH-040-BACKGROUND-001
architecture_id: ARCH-040
title: Implement recovery conversation human/AI services
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: review
priority: 40
executor: null
claimed_at: null
attempt: 2
depends_on:
  - ARCH-040-DATABASE-001
enables:
  - ARCH-040-BACKGROUND-002
created: 2026-10-14
updated: 2026-10-17
---

# ARCH-040-BACKGROUND-001 — Implement recovery conversation human/AI services

## Architecture

Initiative: `ARCH-040`. Architecture document: `docs/architecture/ARCH-040-merchant-customer-conversations-human-handover.md`. Coordinator: `moda_architect`. This task is materialized on its canonical parent task branch; launcher-resolved paths remain authoritative.

## Developer Ownership Amendment

On 2026-10-17, `/moda_developer_create ARCH-040-BACKGROUND-001` was invoked to take over this ready task. `execution_mode` and `completion_mode` are now `developer`; `assigned_agent: moda_background`, repository ownership, task scope, dependencies, requirements and acceptance criteria are unchanged.

Attempt 2 claim (2026-10-17): the developer clarified that the Background `database` submodule must advance because ARCH-040 database schema changes landed after Attempt 1 began. Implementation commit `923c9e3` records the gitlink to published database `origin/main` commit `d00492ad1c10e78ab50d415acefc12bf872c17af`. The canonical implementation worktree was synchronized to `origin/task/ARCH-040-BACKGROUND-001`; `origin/main` was already included; recursive submodule sync/update/status completed with the exact recorded gitlink. The parent task worktree was likewise synchronized, with `origin/main` already included. No shared/default checkout or parent workspace submodule pointer was changed.

## Objective

Implement **modular, directly testable services and policy operations** for shared recovery conversation ownership, durable HUMAN message dispatch, single recovery follow-up/credit, administrative suspension and deterministic HUMAN abuse screening. Define their callable interfaces, transaction guarantees and outcomes; leave attaching them to production workers and schedulers to BACKGROUND-002.

## Context

ARCH-040 is **recovery-only**. There is exactly one `Conversation` per `CheckoutRecovery` generation. CommerceAgent, merchant and customer messages share its existing `ConversationMessage` history. Consolidated `DATABASE-001` defines the Prisma fields, mode revisions, send commands, follow-up provenance, shop restriction and audit state. Reuse the current outbound-admission, provider-status, recovery-billing and follow-up mechanics; do not create a generic chat subsystem.

## Scope

- Implement small, cohesive services/functions under existing Background service conventions; a thin coordinating facade may expose them, but **do not create one monolithic 300+-line service** or a second WhatsApp sender.
- Implement the decision and state-transition logic, injected persistence/clock/provider-admission interfaces and stable outcomes, with focused unit and database concurrency tests.
- Ensure no service relies on Shopify UI or Woo hosted API; both producers use the same persisted `MerchantConversationSendCommand` and recovery context.

## Out of Scope

- No worker registration, recurring-job scheduling, `whatsapp.worker.ts`/`conversation-turn-processor.service.ts` orchestration rewiring or global runtime bootstrap in this task; BACKGROUND-002 owns those call sites.
- No browser/API/controller changes, new Prisma migrations, standalone human conversations, second conversation history, second delivery transport, second recovery-credit ledger or new ARCH-040 Shared package.
- No staff identities or roles, new chat inbox, external LLM/content moderation provider, semantic abuse classifier, automatic shop suspension or full-store `Shop.status` changes.

## Requirements

### Service operations to implement

The exact TypeScript names are repository-local, but BACKGROUND-002 must be able to invoke all of these independently (document the actual exported methods and accepted inputs/results):

1. **AI ownership and stale-turn policy** — load current recovery-linked conversation mode/revision, decide admission for an expected revision before agent work, after LLM/tool awaits and before provider submission. `HUMAN` or stale revision suppresses an unsent AI turn; old revision cannot become valid after Resume AI. Customer inbound persistence is never suppressed by HUMAN mode.
2. **Durable HUMAN command processing** — safely claim/lease commands by stable ID, validate recovery/shop and conversation binding, HUMAN ownership/revision, recipient eligibility and approved message kind, prepare a send via the existing `OutboundMessageDeliveryService`/WhatsApp transport abstractions, and persist deduplicated terminal/retryable outcomes and `ConversationMessage.senderType=HUMAN`. Command records are **intent**, not separate transcript or receipt state.
3. **Window and follow-up policy** — use the most recent authenticated CUSTOMER inbound to decide 24-hour free-text eligibility; never convert expired queued text to a template. Preserve existing scheduled **no-response-only** follow-up policy, while explicitly merchant-initiated eligible post-window templates may claim the **same unique sequence-2 `RecoveryOutreachAttempt`** where still actionable. Share existing checkout/recovery lock and `RecoveryBillingService` source identity (`recovery-outreach:<attempt.id>`); no second scheduler, follow-up allowance or debit. Suppress scheduled follow-up in HUMAN mode.
4. **Shop suspension policy** — authoritative database-backed human-messaging restriction, checked for every HUMAN command at initial processing and at final admission. Suspend/restore history is ADMIN-001's responsibility; this service must reject already queued/leased commands when suspended. Do not block AGENT/AUTOMATION, normal customer ingress or merchant Resume AI. Terminal suspension rejections do not auto-requeue when restored.
5. **HUMAN deterministic abuse policy** — bounded payload/length checks, shop/recipient rate limits, normalized repeated unsolicited-message detection, Redis atomic counters/TTL where appropriate, stable command replay non-amplification, durable safe reason codes and reviewable structured signals. Legitimate responses must not be arbitrarily blocked; document configurable thresholds. Fail closed for HUMAN dispatch when screening is unavailable, with a distinguishable bounded retryable outcome; do not infer semantic threats from keywords or automatically suspend the shop.
6. **Final provider admission/failure policy** — design a testable, durable ordering/fencing contract for concurrent Take Over, shop suspension, command dispatch and provider submission. Mere pre-send reads are not sufficient proof. No long PostgreSQL transaction held across Meta HTTP; define the precise accepted-before/after provider boundary and behaviour when already irreversibly sent. Reuse provider receipts and recovery credit reserve/commit/compensation, distinguishing definitive failure from provider-unknown state.

### Stable outcomes and persistence

- Use the Prisma schema from DATABASE-001; prefer existing domain statuses and codes. Ensure readable outcomes for stale revision, HUMAN inactive, follow-up already used, customer window closed, `human_messaging_suspended`, `human_rate_limited`, `human_repeated_spam`, `human_content_invalid`, and `human_screening_unavailable` where applicable.
- Keep tenant scoping on `CheckoutRecovery.shopId` for recovery-linked conversations. Reject standalone/nonmatching conversation commands. Do not accept client-provided `shopId` as authority.
- Command retries/duplicate submissions cannot trigger second Meta sends, screening counts or recovery debits. Provider uncertainty remains recoverable without unsafe resend.
- No HUMAN policy check silently skips normal provider/recipient, plan/capacity or existing recovery-terminal rules.

## Concrete implementation blueprint — service layer only

**Baseline reviewed:** `moda-interact-background` source in `moda-interact-workspace(20261017-115551).zip`. Names under `src/services/recovery-conversation/` below are **proposed new, repository-local modules** (they do not exist yet); existing paths are actual files in that snapshot. A repository owner may make an equivalent small-file naming choice but must preserve the specified callable contracts and test seams. Implement policy here; BACKGROUND-002 owns calling it from production workers.

### 1. Existing implementation to reuse — not replace

| Existing source | Reuse precisely | Must not do in BG001 |
|---|---|---|
| `src/services/conversation.service.ts` | `getTurnState`, `claimTurn`, `releaseTurn`, `completeTurn`, `hasChanged`; preserve customer `receiveMessage` and inbound-version logic | Do not create an alternative inbound conversation/turn store |
| `src/services/outbound-whatsapp-admission/outbound-admission-reservation.service.ts` | Existing AGENT/AUTOMATION quota reservation and `ConversationMessage(PENDING)` idempotency | Do not insert HUMAN into the existing automated-message quota by casting sender types |
| `src/services/outbound-whatsapp-admission/outbound-message-delivery.service.ts` | Existing provider adapter, prepared-send flow, final shop eligibility check, SENT/FAILED/unknown-message handling | Do not implement another raw Meta HTTP sender or mutate live production call sites here |
| `src/services/checkout-recovery/recovery-outreach-follow-up-processor.service.ts` | Current due-date/engagement suppression, checkout lock, template selection and sequence-2 finalisation | Do not create another follow-up scheduler or redefine automatic follow-up eligibility |
| `src/services/recovery-outreach-attempt.service.ts`, `src/services/recovery-billing.service.ts` | Existing attempt identity, `admit`, `revalidateBeforeProvider`, release/finalise and source key `recovery-outreach:<attempt.id>` | Do not add human-specific recovery-credit accounts or independent sequence-2 rows |
| `src/services/whatsapp-provider-status.service.ts`, `src/services/whatsapp.service.ts` | Canonical provider-message receipt transitions and existing provider transport | No parallel provider-status reconciliation or duplicate send implementation |
| `src/services/inbound-whatsapp-abuse-admission.service.ts` | Read as an example of injectable atomic Redis admission only | Never apply inbound customer-abuse counters to outbound merchant messages |

### 2. New modules and *exact behavioural* methods

Create cohesive files, not one large orchestrator. The signatures below describe inputs/outputs; final TypeScript naming may follow local conventions and should be recorded under Completion Report. Each receives injectable database/clock/Redis/policy dependencies for focused tests.

| New file (proposed) | Public methods to implement | Required result behaviour |
|---|---|---|
| `src/services/recovery-conversation/ai-turn-ownership.service.ts` | `readTurnOwnership(conversationId)` -> `{mode, revision, recoveryId, shopId}`; `checkAutomatedTurn(conversationId, expectedRevision, phase)` | `allowed` only for recovery-linked `AI` mode and exact revision. Return `human-controlled`, `stale-control-revision`, `not-recovery-linked` or `shop-mismatch` without modifying inbound records. Capture original revision once at turn start; never load a fresh revision after Resume AI and treat a previously started turn as current. |
| `src/services/recovery-conversation/merchant-send-command.service.ts` | `claimDueCommands(limit, now)` -> leased command IDs with tokens; `loadClaimedCommand(commandId, leaseToken)`; `completeCommand`/`rejectCommand`/`deferCommand` by expected lease token | Claim with a short SQL transaction, stable row identity and lease CAS. Validate command `shopId` against `CheckoutRecovery.shopId`, exact conversation and recovery, `expectedControlRevision` and immutable recipient snapshot. Reject terminally invalid/stale commands; retry only eligible transient failures. |
| `src/services/recovery-conversation/recovery-follow-up-policy.service.ts` | `checkServiceWindow(conversationId, now)`; `validateHumanFollowUp(command)`; `claimSequenceTwo(recoveryId, initiator, initiationKey)` | Most recent **verified inbound customer** timestamp controls 24 hours. Free text is refused when closed, never silently converted into a template. A permitted HUMAN template uses the **already-linked** unique sequence-2 row, without replacing the initiator or the original automatic no-response semantics; return `already-claimed` for a losing human/AI race. |
| `src/services/recovery-conversation/human-send-policy.service.ts` | `checkRestriction(shopId)`; `screenHumanCommand(commandId, shopId, recipient, normalizedContent)` | A SUSPENDED restriction blocks HUMAN only; do not block customer inbound, automated recovery or Resume AI. Bound text/template payloads, shop/recipient send rate and repeat spam with atomic Redis operations. The **same command ID** cannot consume counter capacity on a retry. Emit stable policy codes; Redis failure produces `human_screening_unavailable`, not an unchecked send. |
| `src/services/recovery-conversation/outbound-send-fence.service.ts` | `admitFinalSend({messageId, commandId?, leaseToken?, expectedControlRevision, senderType, shopId, recoveryId})` | In one short durable transaction, atomically decide ownership, shop restriction for HUMAN, follow-up ownership, and **who wins the send-vs-takeover/suspension race**. Return `admitted` with a durable provider-dispatch identity or an explicit refusal. No provider network call inside that transaction. The lease claim alone is *not* equivalent to provider-send admission. |
| `src/services/recovery-conversation/human-send-reconciliation.service.ts` | `recordProviderAccepted(commandId, leaseToken, messageId, providerMessageId)`; `recordDefinitiveFailure`; `recordProviderUnknown`; `reconcileUnknown` | Bind a command to at most one canonical `ConversationMessage(senderType=HUMAN)`/provider send; reuse status and billing services, and distinguish queued/claimed from SENT/DELIVERED/READ. An UNKNOWN provider disposition cannot be retried by issuing another provider request without a proven safe reconciliation outcome. |

Avoid constructing a second `ConversationMessage` for an already-admitted command. `MerchantConversationSendCommand` is a durable **intent**, not a second chat transcript; successful results attach it to the existing canonical outbound message. Preserve no staff/operator account fields.

### 3. Mandatory transaction and concurrency contracts

**AI takeover.** AI begins with `(conversationId, controlRevision=r)` captured before the model/tool call. A human takeover commits `r+1`. All later checks for that **original** AI turn must fail, even if someone resumes AI at `r+2`. An AI reply never sends when its ownership check loses the final admission race; customer inbound is still stored normally.

**Final provider fence.** Use `Conversation.controlRevision` and the relevant shop restriction row under a consistent database-lock/CAS order, with a *durable* provider-dispatch decision recorded before network I/O. Precisely document the linearisation point: a takeover/suspension committed **before** final dispatch admission wins and blocks the send; a send durably admitted first may reach Meta even if takeover commits before its HTTP call. Do **not** claim a read-then-HTTP check has atomic precedence. Do **not** hold a PostgreSQL transaction open during Meta HTTP. `MerchantConversationSendState.CLAIMED` is only a worker lease; if the approved DATABASE-001 columns do not adequately record a distinct durable provider-dispatch decision for this contract, return the concrete schema gap to `moda_architect` for DATABASE-001 correction, instead of treating the lease as proof or silently adding an incompatible column in Background.

**Follow-up.** Both human and automatic actions use one sequence-2 `RecoveryOutreachAttempt` and its existing credit idempotency source. Sequence-2 claimant must be set once, including when an unclaimed row already exists. An automated no-response job retains the existing customer-engaged suppression. The HUMAN path is an explicit approved post-window template request, not an automatic follow-up schedule. While `HUMAN` mode is active, scheduled automated follow-up is suppressed. Reject invalid/terminal recovery, closed-window free text and unsupported recipient *before* provider send; do not charge rejected/definitively unsent work.

**Command lifecycle.** Only `ACCEPTED`/due retryable work is leasable. A lost/expired lease may be reclaimed, but a stale lease holder cannot send or finalise. `UNKNOWN` requires provider/status reconciliation; it is never treated as a fresh command. Store only bounded error codes and redacted metadata in logs. Normal provider billing, execution eligibility, recipient suppression and recovery-terminal checks still apply; do not bypass them in a HUMAN-specific shortcut.

### 4. BG001 targeted tests (new files; direct service invocation)

Place related tests in e.g. `tests/unit/services/recovery-conversation/` and use the repository's existing disposable PostgreSQL/Redis integration harness for real locking and uniqueness proofs. Cover:

1. AI revision `0 -> HUMAN(1) -> AI(2)`: an old revision-0 model completion is denied; an inbound customer message is still recorded.
2. Two simultaneous human send leases for the same command: exactly one claim/dispatch; expiry permits only safe reconciliation, not duplicate provider submission.
3. Tenant mismatch and standalone conversation: rejected even if a raw `Conversation.shopId` is null; tenancy derives from `CheckoutRecovery.shopId`.
4. Human/automatic sequence-2 claim race: one winner, one attempt row, one `recovery-outreach:<attempt.id>` credit source; an existing unclaimed PENDING row is reusable.
5. Open versus expired customer service window, verified inbound timestamp, clock boundary, text-vs-template; queued text expiring before dispatch is refused.
6. Shop suspension just before the final send fence denies HUMAN; AGENT/AUTOMATION unaffected; restore does not resurrect terminal rejections.
7. Redis rate/admission atomicity, short/long windows, duplicate command retries, repeated content and failed Redis connection; no counter amplification or unsafe pass-through.
8. Provider definitive rejection versus network timeout/UNKNOWN; provider reconciliation, idempotency, retry safety and no phantom SENT/credit.
9. SQL races between control change, restriction change, and final provider-dispatch decision, proving the recorded admission order and no DB transaction held during mocked provider I/O.

**Stop point:** BG001 ends with exported/tested methods, documented interface and passing direct-service tests. Do not register a worker, modify runtime entrypoints, change the existing sender/turn/follow-up call sites or claim end-to-end message delivery; those are BG002's responsibilities.

### Platform-agnostic service contracts and execution ownership (Attempt 15)

All six services in the proposed `src/services/recovery-conversation/` module operate only on canonical Prisma entities and trusted `shopId`/`recoveryId`/`conversationId`/`commandId` data. No commerce-platform discriminator, Shopify session, WordPress nonce, Woo installation credential, platform-specific BullMQ job, or platform-owned provider sender is accepted by any BG001 business method. Existing shop/provider adapters can resolve messaging configuration by `shopId` without platform-dependent *policy* branches.

**Durable dispatcher seam:** expose `claimDueHumanCommands({limit, now, ownerToken})`, `evaluateHumanCommand(commandId, leaseToken, now)`, `admitProviderDispatch(...)` and `reconcileProviderOutcome(...)` as producer-neutral ports. Claim runs via indexed PostgreSQL due scan, short `FOR UPDATE SKIP LOCKED`/CAS and lease expiry; never query Shopify/Woo REST or synchronously publish Redis. BG001 **does not** register its own timer/worker; BG002 owns one dispatcher loop.

**Exact final admission:** `admitProviderDispatch` must take the immutable control revision captured at AI-turn start or HUMAN command acceptance and the canonical message/command dispatch identity. Under the shared DATABASE-001 short-transaction fence, check mode/revision, current HUMAN restriction (if applicable), recipient suppression, live service-window eligibility, follow-up claimant and shop entitlement; atomically record the one-way provider permit. `CLAIMED` never grants permission by itself. If a takeover/suspension commits first, reject; if permit commits first, an eventual provider call may be allowed and is not recallable. Do not hold a transaction across provider HTTP. A crashed/ambiguous admitted submission becomes UNKNOWN/reconciliation-only; never infer exactly-once Meta delivery without provider evidence.

**Sender-aware agent context:** change the context projection *interface* so inbound CUSTOMER messages are user turns, AI/AGENT/AUTOMATION turns retain their true origin, and HUMAN outbound messages become **explicitly labelled, untrusted merchant-authored history**, not assistant role messages or elevated system/developer instructions. Define bounded chronological context and preserve merchant promises as attributed statements rather than instructions the model is authorised to execute. Do not mutate original `ConversationMessage` sender types. The real `ConversationService.toAgentMessage`/history integration belongs to BG002.

**Monotonic inbound-clock port:** provide deterministic `latestVerifiedCustomerInbound(current, incoming, now)` semantics and a database-safe max update contract for `Conversation.lastInboundAt` and, where appropriate, `lastMessageAt`. Allow validated provider timestamp skew; ignore stale/out-of-order events for advancing these fields, but still persist/deduplicate their messages. The customer-service window must be derived from the **maximum verified customer inbound** time, never outbound activity or last-delivery time. Audio transcription arrival does not reset the window independently from the original verified inbound WhatsApp event.

**Follow-up:** implement a single atomic sequence-2 claim service, accepting an explicit intent (`scheduled_no_response` or eligible `merchant_post_window`) but no platform parameter. Preserve the scheduled job's engaged-customer suppression, HUMAN ownership suppression of automation, and existing unique attempt/credit identity. Ensure an unclaimed PENDING scheduled row can be claimed by a HUMAN without replacing claimed recipient/template/provider evidence. Terminal/unavailable recoveries cannot initiate sends. Provider-UNKNOWN blocks release of a claimed follow-up.

**Abuse/restriction:** evaluate human-only rules and definitive failures once per command identity, not once per lease/scan. Redis screening outage fails closed for HUMAN send admission when screening is mandatory; it must not pause inbound or unrelated AI delivery. Platform suspension is manual/admin-owned and is not automatically created by the moderation heuristic. Logs use IDs and bounded reason codes only.


## Work Items

- [x] Implement and document the modular service API for the six operations above, including injection seams used by BACKGROUND-002.
- [x] Implement focused ownership/CAS, durable command, service-window/follow-up, restriction, screening and provider-admission logic using existing services/models.
- [x] Implement explicit terminal/retryable/provider-unknown result handling and reuse existing message receipts and credit lifecycle.
- [x] Add and pass focused unit and PostgreSQL/Redis concurrency tests against direct service calls; avoid relying on worker registration to establish service correctness.

## Interfaces / Contracts

- Persisted contract owner: consolidated `ARCH-040-DATABASE-001`, Prisma `Conversation`, `ConversationControlEvent`, `ConversationMessage`, `RecoveryOutreachAttempt`, `MerchantConversationSendCommand`, shop restriction and restriction audit. No new Shared package.
- Existing runtime components to inspect/reuse: `src/services/outbound-whatsapp-admission/outbound-message-delivery.service.ts`, `src/services/checkout-recovery/recovery-outreach-follow-up-processor.service.ts`, `src/services/recovery-billing.service.ts`, `src/services/whatsapp-provider-status.service.ts`, `src/services/whatsapp.service.ts` and the existing inbound abuse service **as reference only** (not as HUMAN policy).
- Export a documented module or thin facade (not a second sender) with testable operations for turn admission, command claim/admission, recovery follow-up claim, restriction and screening decisions, final provider gate, and outcome reconciliation. BACKGROUND-002 owns production registration/call sites and calls these operations.

## Dependencies

- ARCH-040-DATABASE-001

## Enables

- ARCH-040-BACKGROUND-002

- [x] All human command, ownership, dispatch, follow-up and abuse policy methods are producer-neutral and require no commerce-platform enum/import/job; a command with identical persisted fields is processed identically regardless of whether Shopify or Woo accepted it.
- [x] Direct-service tests cover labelled HUMAN model context (never an AI/assistant utterance), late/out-of-order verified inbound timestamps and a resumed-AI transcript.
- [x] Durable admission is separate from lease, preserves a one-way provider identity and tests takeover/suspension precedence plus the admitted-first external race and UNKNOWN recovery.

## Acceptance Criteria

- [x] The six proposed service modules (or documented equivalent small-file grouping) expose all listed method contracts with injected dependencies; **every BG001 listed service and test file is accounted for** without altering live worker registration.
- [x] One recovery conversation, exactly one sequence-2 follow-up opportunity and one credit identity are preserved under human/AI concurrent attempts; both PostgreSQL race winners assert one shared sequence-2 row and its `recovery-outreach:<attemptId>` billing identity.
- [x] HUMAN suspension/rate rejections cannot cause provider sends or credit consumption; denial tests assert no durable provider-dispatch admission, and AI/customer ingress paths remain unchanged by this service-layer-only implementation.
- [x] Testable final-admission fence defines provider-submit ordering and reports the limit of recalls; a read-only preflight masquerading as atomic fencing is not accepted.
- [x] No duplicate Meta transport, receipts, ledger, scheduler or giant all-purpose module is introduced.

## Validation

- [x] Focused unit tests for the exported methods and machine outcomes
- [x] Disposable PostgreSQL contention/cas/retry/follow-up/credit tests
- [x] Disposable Redis rate/TTL/retry/failure tests where required
- [x] Provider mock admission ordering and definitive/unknown receipt tests
- [x] Typecheck, changed-file lint, applicable builds/tests from actual package scripts and `git diff --check`

## Stop Condition

After implementing only the listed scope and completing validation, record worktree, tests, and files in Completion Report, set task to `review`, return to `moda_architect` and **STOP**. Do not execute another task automatically.

## Implementation Notes

Use the canonical launcher-resolved dedicated parent/implementation task worktrees and matching `task/<TASK_ID>` branches. Check the repository scripts before selecting validation commands. Use the published `@modainteract/moda-interact-shared/logging` API; log stable identifiers and reason codes only, never message bodies, credentials, personal details or admin notes. Avoid editing `docs/decisions/**/_index.md` until this architectural session is explicitly closed. This architecture targets fresh development-schema validation; do not add historical migration/backfill work.

## Completion Report

### Status

Review — Attempt 2 passed developer self-review for implementation and validation. The developer supplied a passing disposable PostgreSQL/Redis run (11/11 tests); the acceptance and validation criteria are reconciled below. Because `completion_mode: developer`, the task remains in `review` until the developer explicitly records completion.

### Files Changed
Implementation commits `0cf37887716c871b8e9cc8fe542c88fc44612701` (`feat(background)`), `85ce5e899531506d3cffbc5b729aaa1eec9b882a` (`fix(ARCH-040-BACKGROUND-001): fence human follow-up claims and complete integration evidence`), `f21cb075a5ff667dc326fe74359ac73aca7e99ed` (`test(ARCH-040-BACKGROUND-001): prove follow-up races and billing denial`), and `923c9e3` (required DATABASE-001 gitlink update) are published on `task/ARCH-040-BACKGROUND-001`.

- `package.json`
- `src/services/recovery-conversation/README.md`
- `src/services/recovery-conversation/ai-turn-ownership.service.ts`
- `src/services/recovery-conversation/human-command-evaluation.service.ts`
- `src/services/recovery-conversation/human-send-policy.service.ts`
- `src/services/recovery-conversation/human-send-reconciliation.service.ts`
- `src/services/recovery-conversation/index.ts`
- `src/services/recovery-conversation/merchant-send-command.service.ts`
- `src/services/recovery-conversation/outbound-send-fence.service.ts`
- `src/services/recovery-conversation/recovery-conversation.sql.ts`
- `src/services/recovery-conversation/recovery-follow-up-billing.service.ts`
- `src/services/recovery-conversation/recovery-follow-up-policy.service.ts`
- `tests/integration/recovery-conversation.services.integration.test.ts`
- `tests/unit/services/recovery-conversation/recovery-conversation-services.test.ts`

Implementation commit `923c9e3` advances the nested `database` gitlink to published ARCH-040 schema commit `d00492ad1c10e78ab50d415acefc12bf872c17af`. The developer confirmed this dependency update is intentional and required.

### Work Completed
Implemented and documented the modular recovery-conversation service API: AI ownership and attributed history projection; due HUMAN command leasing/evaluation; 24-hour window and shared sequence-two follow-up policy; HUMAN suspension/content/rate/replay screening; the durable final provider-admission fence; provider outcome reconciliation; and a bridge to the existing recovery-billing lifecycle. The follow-up claim requires current HUMAN ownership and an exact expected control revision under Shop/Conversation locks; zero history limit returns an empty projection. The expanded integration tests now cover both follow-up race winners, same-command concurrent leasing, suspension/rate denial before durable billing admission, definitive failure and UNKNOWN reconciliation. No production worker registration or second sender was added. The database gitlink update to published commit `d00492ad1c10e78ab50d415acefc12bf872c17af` is intentional, committed as `923c9e3`, and required by the developer-confirmed schema dependency.

### Validation Results
Agent-executed checks passed:

- `npm run test:arch040-recovery-conversation` — 1 file, 15 tests passed on the current implementation branch.
- `npm run build` — Prisma client generation and TypeScript compilation passed.
- `./node_modules/.bin/eslint src/services/recovery-conversation tests/unit/services/recovery-conversation tests/integration/recovery-conversation.services.integration.test.ts --max-warnings=0` — passed.
- `git diff --check` — passed on the current implementation and task-report changes.

The developer supplied the terminal result for `npm run test:arch040-recovery-conversation:postgres` from the canonical implementation worktree at `923c9e316b3be49335270ca5b5c51c968f3b5487`: one integration file passed, 11/11 tests, including PostgreSQL concurrency and Redis screening cases (3.73 seconds). The test output includes both sequence-two race winners, suspension and rate denial, command-claim concurrency, definitive failure, UNKNOWN reconciliation, and Redis idempotency/rate/TTL checks.

An independent rerun in this review environment could not start because `docker` is not available on its PATH (`spawn docker ENOENT`); that rerun executed no tests. The developer-provided successful result is recorded as the validation evidence, and the implementation branch was independently verified clean at the same commit with the expected database gitlink.

Source review confirms the integration additions exercise controlled races in both directions (HUMAN takeover wins before the scheduled claim, and scheduled claim commits while HUMAN takeover/claim contend), assert one shared sequence-2 row and billing identity, and prove suspension/rate-screening denials stop before durable eligibility/provider admission. The passing result above closes the prior validation gap.

### Deviations
The first integration attempt in the developer's environment and this review environment lacked Docker; the developer later supplied a passing run from the canonical implementation worktree. The developer explicitly confirmed the database gitlink advance was required; it is included in implementation commit `923c9e3`, pointing to database `origin/main` `d00492ad1c10e78ab50d415acefc12bf872c17af`. No parent workspace submodule pointer was changed.

### Physical Worktree Isolation and Synchronization
- Canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
- Parent worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-040-BACKGROUND-001`, `task/ARCH-040-BACKGROUND-001`
- Implementation worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-040-BACKGROUND-001`, `task/ARCH-040-BACKGROUND-001`
- Shared workspace checkout switched/mutated for task work: no
- Shared implementation checkout switched/mutated for task work: no
- Another task worktree reused: no
- Parent task branch fast-forwarded from origin: not needed; already current
- Parent `origin/main` incorporated: already current
- Implementation task branch fast-forwarded from origin: not needed; already current
- Implementation `origin/main` incorporated: already current
- Recursive implementation submodules: initialized and verified against recorded gitlinks; Background `database` points to published commit `d00492ad1c10e78ab50d415acefc12bf872c17af`

### Assumptions
Use the accepted consolidated DATABASE-001 schema; don't implement new schema in Background.

### Unresolved Issues
- Developer-controlled completion decision is pending; the developer must explicitly invoke `/moda_developer_update ARCH-040-BACKGROUND-001 complete` to transition this task from `review` to `complete`.
- Architect review remains pending.

### Architectural Concerns
No runtime wiring was attempted. Architect review remains pending; review the implementation contract and any cross-repository schema/dispatch concerns after the validation gaps are resolved.

## Developer Self-Review - Changes Requested (Attempt 1)

Attempt 1 was returned to ready because disposable PostgreSQL/Redis validation was unavailable and the test matrix did not yet prove the HUMAN/automation claim race or rejection-side-effect behavior. The developer subsequently added `f21cb07` addressing those test gaps and clarified the required database gitlink update. Attempt 1 history is preserved; the current Attempt 2 review is recorded below.

## Developer Self-Review Accepted (Attempt 2, Initial Review)

Code review found no remaining implementation defect in the revised follow-up fencing, zero-limit history projection, controlled follow-up race tests, or billing-denial assertions. Focused unit tests (15/15), build/TypeScript, changed-file ESLint and `git diff --check` passed. At this initial review, the required disposable PostgreSQL/Redis suite was attempted but blocked before test startup by missing Docker (`spawn docker ENOENT`). The task remained in `review` for developer validation; explicit developer completion was not recorded.

## Developer Self-Review Passed (Attempt 2, Validation Follow-Up)

The developer supplied a passing disposable PostgreSQL/Redis suite result (11/11 tests) from the canonical implementation worktree at commit `923c9e316b3be49335270ca5b5c51c968f3b5487`. The test criteria and acceptance items are now evidenced. Code review found no remaining implementation defect in the revised follow-up fencing, zero-limit history projection, controlled follow-up races, denial-side-effect checks, provider admission ordering, or definitive/UNKNOWN reconciliation. Focused unit tests (15/15), build/TypeScript, changed-file ESLint and `git diff --check` also pass. This passing review leaves the task in `review` because `completion_mode: developer` requires an explicit developer completion decision; none is recorded here.

## Architect Review

### Review Status
Pending.

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
