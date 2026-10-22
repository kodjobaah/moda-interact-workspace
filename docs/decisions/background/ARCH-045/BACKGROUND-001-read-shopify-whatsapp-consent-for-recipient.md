---
id: ARCH-045-BACKGROUND-001
architecture_id: ARCH-045
title: Synchronise and evaluate current Shopify phone consent
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: in_progress
priority: 20
executor: developer
claimed_at: 2026-10-22T16:41:25Z
attempt: 2
depends_on:
  - ARCH-045-DATABASE-002
  - ARCH-045-SHARED-002
enables:
  - ARCH-045-BACKGROUND-002
  - ARCH-045-BACKGROUND-003
  - ARCH-045-BACKGROUND-004
  - ARCH-045-SYSTEM-TEST-001
created: 2026-10-20
updated: 2026-10-22
---
# Synchronise and evaluate current Shopify phone consent

## Architecture

Architecture ID: `ARCH-045`
Architecture document: `docs/architecture/ARCH-045-shopify-whatsapp-consent-gated-recovery.md`
Coordinator: `moda_architect`

### Developer Takeover

The developer invoked `/moda_developer_create ARCH-045-BACKGROUND-001`, taking over execution and completion authority from the prior `execution_mode: agent`, `completion_mode: automatic` definition. Execution/completion modes remain `developer`/`developer`; logical repository ownership remains `assigned_agent: moda_background`. The task metadata records **developer Attempt 1 claimed at `2026-10-22T13:18:19Z`**. Corrections labelled "Attempt 2" in the exchanged patch filenames are iterations within this existing task claim, **not** a new `/moda_developer_create` claim.
**Lifecycle:** developer implementation and required local validation are recorded below; **review submission is not yet published** in the supplied evidence. Keep `status: in_progress` until both task branches are committed/pushed and mandatory physical-worktree/start-of-attempt evidence is reconciled. The archived parent worktree and terminal-confirmed implementation worktree do not by themselves prove every launcher synchronization step.

## Objective

Provide one injected Shopify-native WhatsApp-consent reader and current-state synchroniser for an existing shop-owned customer and **exact active `CustomerPhone` recipient**. Every **distinct new checkout** uses its live Shopify permission check before first recovery creation; subsequent proactive sends read the stored `CustomerPhone` permission without another Shopify read. Consent-sync webhooks reuse the same read-only synchronisation operation. WhatsApp STOP is an independent local prohibition owned by BACKGROUND-005 and is never sent to Shopify.

## Context

Shopify is the source of truth for its native WhatsApp marketing opt-in. `ARCH-045-DATABASE-002` holds the current local `CustomerPhone` projection, not a separate Shopify consent table. `BACKGROUND-003` handles webhook job routing; `BACKGROUND-002` owns first recovery creation; `BACKGROUND-004` owns final proactive-send integration.

## Scope

- Implement `src/providers/shopify-whatsapp-consent.provider.ts` as the **read-only Shopify API provider**. Use the existing `getShopifyAccessToken(shopDomain)` from `src/services/shopify-session.service.ts`, the shop's 2026-07 Admin GraphQL endpoint and an injectable HTTP transport with bounded timeout. The provider returns a typed observation or unavailable/not-found result; it performs **no Prisma writes or recovery decisions**. A GraphQL HTTP 200 with `errors`, protected-field denial, malformed/missing fields or an unusable response must not yield an affirmative grant.
- Implement `src/services/shopify-whatsapp-consent.service.ts` as the **shop/customer/recipient eligibility and projection service**, injecting the typed provider interface and the existing Prisma database access. This is the only owner of CustomerPhone selection, monotonic Shopify consent synchronisation, local no-contact precedence, and the `ALLOWED` / `NOT_AUTHORISED` / `UNAVAILABLE` / `AMBIGUOUS` decision. No generic consent-provider registry or new dependency-injection framework.
- Resolve Shopify identity through the existing shop-owned `Customer` and Shared numeric/GID helper. Do **not** attach a Shopify customer ID to an existing Customer solely because its phone matches, or permit an unidentified guest to inherit a consent grant.
- Compare the checkout recipient with the Shopify-authoritative current phone using Shared canonical international-phone rules and an explicit country context where required. Use/update only the associated **active** `CustomerPhone`; a changed, missing or ambiguous phone cannot carry a previous number's grant.
- On **each distinct new Shopify checkout recovery evaluation**, call `readCurrent()` for the verified shop/customer and exact recipient (not on duplicate delivery of the same checkout). Set the native consent decision on CustomerPhone to the current provider result and timestamp, including `GRANTED` when Shopify reports `SUBSCRIBED`. Preserve monotonic observation ordering and never convert provider errors into a grant. Local STOP/merchant suppression are independent effective-send checks: neither an older nor a newer Shopify `SUBSCRIBED` observation can clear a local STOP. The observed native decision is still updated to `GRANTED` when Shopify reports `SUBSCRIBED`.
- A Shopify native grant never re-authorises a locally STOP-blocked shop/recipient, regardless of its `updatedAt`. STOP can be cleared only through a **separate, explicitly authorised, verified customer request to Moda**, which is not implemented by this task. A sync event refreshes native consent only; it never creates a checkout/recovery.
- Expose `evaluateRecipient()` for **fresh live verification at new-checkout admission** and `evaluateStoredRecipient()` for **database-only** proactive send permission. Both provide exact recipient, `customerPhoneId`, current consent and no-contact revisions. BACKGROUND-004 uses only stored consent and the existing short final SQL fence: **no Shopify read before every follow-up**.
- Do **not** implement Shopify consent writes, `unsubscribeRecipient()`, STOP-to-Shopify retries, `write_customers` scope requests or any Shopify mutation. BACKGROUND-005 records local STOP and merchant Support notices independently of this read-only provider.
- Test source failures, duplicates/reordering, shop isolation, changed phone, phone-only legacy merges, GraphQL read/write access denial and local revision races. Use the published Shared logging API without customer phone or payload logging.

## Out of Scope

- No checkout materialisation or merchant notices, consent-event worker routing, new consent/identity/erasure table, generic customer-identity redesign, recipient-reachability schema change, or consent-triggered checkout queue.

## Requirements

- [x] A matching current Shopify-native `SUBSCRIBED` decision for the correct existing Shopify customer and exact recipient is necessary for a positive result; unknown, revoked, wrong-number, ambiguous and unavailable states fail closed.
- [x] Phone equality is not proof of Shopify customer identity or consent. Local STOP and merchant suppression cannot be cleared by a delayed native grant.
- [x] Expose the live-read service operation for one current Shopify permission check per distinct new checkout evaluation and for consent-sync consumers using `readCurrent()`; expose stored-only CustomerPhone consent/no-contact eligibility for follow-up consumers without any Shopify read. Actual consumer wiring is deferred as stated below.

**Implementation boundary:** the provider/service implement and test one native read per invocation of `evaluateRecipient()` and `syncCustomer()`, and no native read in `evaluateStoredRecipient()`. Deduplication **per distinct checkout**, checkout call-site invocation, webhook routing, and proactive-send integration are explicitly owned by `ARCH-045-BACKGROUND-002/003/004`; they are **not** claimed to be wired or end-to-end verified by BACKGROUND-001.


## Work Items

- [x] Add `src/providers/shopify-whatsapp-consent.provider.ts` with only the 2026-07 GraphQL **read**, typed outcomes, bounded timeouts, GraphQL errors handling and existing offline-token reuse.
- [x] Add `src/services/shopify-whatsapp-consent.service.ts` with injected read-only provider operation, customer/default-phone validation, current CustomerPhone native-consent projection, live first-checkout eligibility and stored database-only eligibility that always respects local STOP.
- [x] Add `tests/unit/providers/shopify-whatsapp-consent.provider.test.ts` and `tests/unit/services/shopify-whatsapp-consent.service.test.ts`.
- [x] Add `tests/integration/shopify-whatsapp-consent.integration.test.ts` for real PostgreSQL/Prisma recipient, concurrency and monotonic revision assertions. Do not duplicate consumer wiring owned by BACKGROUND-002/003/004.

## Interfaces / Contracts

**Canonical Background-local interfaces and entrypoints:**

- **Provider:** `ShopifyWhatsAppConsentReader.readCurrent(input)` in `src/providers/shopify-whatsapp-consent.provider.ts`, implemented by `ShopifyWhatsAppConsentProvider`. The provider accepts the shop's validated `shopDomain` and a Shared-validated Shopify customer GID, **not** an unverified customer phone lookup.
- **Service:** `ShopifyWhatsAppConsentService.syncCustomer(input)`, `.evaluateRecipient(input)` and `.evaluateStoredRecipient(input)` in `src/services/shopify-whatsapp-consent.service.ts`. Constructor-inject the narrow read-only `ShopifyWhatsAppConsentReader` port so tests can supply fakes; use the repository's existing Prisma client, not a second persistence abstraction unless tests require a narrow injected port.

```typescript
// Provider-local contract; these exported names and paths are required.
export type ShopifyWhatsAppConsentObservation =
  | {
      kind: "OBSERVED";
      customerGid: string;
      phoneNumber: string;
      state: "SUBSCRIBED" | "UNSUBSCRIBED" | "PENDING" | "NEVER_SUBSCRIBED" | "REDACTED";
      updatedAt: string | null;
    }
  | { kind: "NOT_FOUND" }
  | { kind: "UNAVAILABLE"; reason: "TIMEOUT" | "HTTP" | "GRAPHQL" | "ACCESS_DENIED" | "INVALID_RESPONSE" };

export interface ShopifyWhatsAppConsentReader {
  readCurrent(input: {
    shopDomain: string;
    customerGid: string;
  }): Promise<ShopifyWhatsAppConsentObservation>;
}

// Service-local contract, exported from shopify-whatsapp-consent.service.ts.
export type ShopifyWhatsAppConsentEligibility =
  | {
      status: "ALLOWED";
      customerPhoneId: string;
      canonicalRecipient: string;
      consentRevision: bigint;
      noContactRevision: bigint;
    }
  | { status: "NOT_AUTHORISED"; reason: string }
  | { status: "UNAVAILABLE"; reason: string }
  | { status: "AMBIGUOUS"; reason: string };

export type ShopifyWhatsAppConsentSyncResult =
  | { status: "UPDATED" | "UNCHANGED"; customerPhoneId: string }
  | { status: "NOT_AUTHORISED" | "UNAVAILABLE" | "AMBIGUOUS"; reason: string };

export interface ShopifyWhatsAppConsentServicePort {
  syncCustomer(input: { shopId: string; shopifyCustomerId: string }): Promise<ShopifyWhatsAppConsentSyncResult>;
  evaluateRecipient(input: {
    shopId: string;
    customerId: string;
    shopifyCustomerId: string;
    recipient: string;
  }): Promise<ShopifyWhatsAppConsentEligibility>;
  evaluateStoredRecipient(input: {
    shopId: string;
    customerId: string;
    recipient: string;
  }): Promise<ShopifyWhatsAppConsentEligibility>;
}
```

The GraphQL read operation is explicitly:

```graphql
query CustomerWhatsAppConsent($id: ID!) {
  customer(id: $id) {
    id
    defaultPhoneNumber {
      phoneNumber
      whatsAppMarketingConsent { state updatedAt }
    }
  }
}
```

The query uses Shopify Admin GraphQL **2026-07** and requires available `read_customers`/protected customer-data access. The provider uses the existing Shopify offline-session token mechanism. A missing customer, missing default phone, HTTP/GraphQL error, unknown state or insufficient scope never authorises messaging. Do not use deprecated SMS consent fields.

`syncCustomer` is called by **BACKGROUND-003** after receiving a consent-sync event; it only updates the correct existing `CustomerPhone`. `evaluateRecipient` is injected by **BACKGROUND-002** at normal recovery admission. `evaluateStoredRecipient` is injected by **BACKGROUND-004** and checks only durable CustomerPhone state/revisions. BACKGROUND-005 owns durable local STOP and merchant Support notices; neither this provider nor its service calls Shopify to change consent. The reader/service **do not** modify those consumers as part of BACKGROUND-001.

Consumes `ARCH-045-DATABASE-002` current CustomerPhone schema and published `ARCH-045-SHARED-001/002` phone and Shopify customer identity helpers. No new inter-service contract or queue.

## Dependencies

- `ARCH-045-DATABASE-002`
- `ARCH-045-SHARED-002`

## Enables

- `ARCH-045-BACKGROUND-002`
- `ARCH-045-BACKGROUND-003`
- `ARCH-045-BACKGROUND-004`
- `ARCH-045-SYSTEM-TEST-001`

## Acceptance Criteria

- [x] Verified native consent is projected to the correct tenant-scoped active CustomerPhone even when Shopify reports `SUBSCRIBED` after STOP; that projection must not change local `whatsappNoContact`, reason, timestamp or revision.
- [x] No mismatched, unidentified or changed recipient is considered authorised by phone equality alone; a stale timestamp on a changed Shopify default phone must also fail closed for stored eligibility of the old number. No recovery is created by this reader/synchroniser. **Attempt 2 regression:** stored authorisation for the displaced phone is withdrawn even when the new default phone's provider `updatedAt` predates the prior grant; stale observations cannot grant the new phone, and local STOP remains effective.
- [x] Provider errors, absent fields and ambiguous identities cannot authorise first recovery creation; follow-up denial uses current stored consent/STOP. No API read, including a later `SUBSCRIBED`, clears local STOP; no Shopify mutation/write scope or STOP retry is present.

## Validation

- [x] `npx vitest run tests/unit/providers/shopify-whatsapp-consent.provider.test.ts tests/unit/services/shopify-whatsapp-consent.service.test.ts`: exercise fresh checkout consent, stored-only follow-ups, subscribed/revoked/unknown, HTTP-200 GraphQL errors, read scope denial, native grant after local STOP, wrong default phone, customer-ID conversion, ambiguous identity and timeouts with injected fakes. **38/38 passed** in the Attempt 2 rerun `typescript(20261022-162629)` (provider 22; service 16). The original Attempt 1 rerun was 34/34.
- [x] Run `tests/integration/shopify-whatsapp-consent.integration.test.ts` with the repository's existing `scripts/test-integration.mjs` harness: verify real PostgreSQL active-recipient matching, duplicate/out-of-order observations, monotonic revisions and concurrent STOP/revocation. No live Shopify access is required. **3/3 passed** in the Attempt 2 rerun `typescript(20261022-162629)` via `npm run test:integration -- tests/integration/shopify-whatsapp-consent.integration.test.ts`, including the older-`updatedAt` displaced-grant regression. The original Attempt 1 rerun was 2/2.
- [x] Run repository-declared `npm run build` and targeted `npm run lint` (or the equivalent existing validation contract) and `git diff --check`. Prove that initial live Shopify reads occur **outside** database transactions, and subsequent outbound eligibility uses stored revisions without GraphQL calls or Shopify writes. **Build/Prisma generation passed; targeted `npx eslint` passed; `git diff --check` emitted no errors** in the Attempt 2 rerun `typescript(20261022-162629)`. The Background-local source uses no database transaction around `readCurrent()`; stored eligibility uses database reads only.

## Stop Condition

After completing only the defined Work Items, Acceptance Criteria and required Validation, record the canonical task worktree/branch and start-of-attempt synchronization evidence, populate the Completion Report, set `status: review`, return control to `moda_architect` and **STOP**. Do not launch enabled or unrelated tasks. For publication task, do not rerun implementation validation.

## Implementation Notes

**Required file layout (relative to `moda-interact-background/`):**

```text
src/providers/shopify-whatsapp-consent.provider.ts
src/services/shopify-whatsapp-consent.service.ts
tests/unit/providers/shopify-whatsapp-consent.provider.test.ts
tests/unit/services/shopify-whatsapp-consent.service.test.ts
tests/integration/shopify-whatsapp-consent.integration.test.ts
```

The provider owns Shopify HTTP/GraphQL/token interaction only. The service owns local customer/phone resolution, synchronisation and a typed consent decision. Existing `src/services/shopify-session.service.ts` is **reused, not rewritten**. This task must not add a generic `ConsentProvider` registry, a new queue, a local copy of Shared phone/ID normalisation, a new consent data table, or call-site integration owned by BACKGROUND-002/003/004.

Exact Shopify customer GID must be constructed only from a Shared-validated shop-linked customer identifier. Do not use a recovery phone number to search for another customer. Constructor injection of the narrow read-only `ShopifyWhatsAppConsentReader` port is sufficient; no framework is required. Structured logging uses the published Shared logger with no raw phone numbers, tokens or GraphQL payloads.

Before claiming, use the deterministic `/moda-task` launcher and its **actual** prepared packet, read the task's complete current Architect Review, and verify task/dependency status in the developer's canonical workspace. Preserve `docs/decisions/**/_index.md` untouched until the developer explicitly closes the architecture documentation session. New runtime structured logging uses `@modainteract/moda-interact-shared/logging` where applicable. No source outside this task's owner repository may be changed unless explicitly authorised by the architecture.

## Completion Report

### Status

In Progress — Attempt 2 claimed by developer at 2026-10-22T16:41:25Z. Attempt 1 review history is preserved below.

### Files Changed

Relative to `moda-interact-background/`:

- `src/providers/shopify-whatsapp-consent.provider.ts` (new)
- `src/services/shopify-whatsapp-consent.service.ts` (new)
- `tests/unit/providers/shopify-whatsapp-consent.provider.test.ts` (new)
- `tests/unit/services/shopify-whatsapp-consent.service.test.ts` (new)
- `tests/integration/shopify-whatsapp-consent.integration.test.ts` (new)
- `package.json` and `package-lock.json` (consume Shared `2.5.0`)
- `database` nested submodule pointer in the implementation repository: accepted `ARCH-045-DATABASE-002` commit `e0ab833d2e2395e3ed3cfe4aee6d07c716173e44`

**Attempt 2 correction files (against the reviewed Attempt 1 implementation):**

- `src/services/shopify-whatsapp-consent.service.ts` — fail-closed displacement and retained ordering fence.
- `tests/unit/services/shopify-whatsapp-consent.service.test.ts` — older-observation, retry, STOP and Database-trigger regression cases.
- `tests/integration/shopify-whatsapp-consent.integration.test.ts` — real PostgreSQL changed-default-phone ordering and local STOP coverage.

The provider, Shared dependency and Database schema remain unchanged in the Attempt 2 correction.

This task/report update modifies **only this task document** in the parent workspace; no `docs/decisions/**/_index.md`, parent architecture, another task, or parent implementation-repository gitlink is included in the report patch.

### Work Completed

- Added read-only `ShopifyWhatsAppConsentProvider.readCurrent()` against 2026-07 Admin GraphQL with offline-token reuse, injected transport, timeout/abort, response bounds and fail-closed handling for HTTP, GraphQL, access and malformed-result failures.
- Added `ShopifyWhatsAppConsentService.syncCustomer()`, `.evaluateRecipient()` and `.evaluateStoredRecipient()` using shop-owned Shopify customer identity, Shared international-phone canonicalisation and the **exact active** `CustomerPhone`.
- Persisted native `GRANTED`/`REVOKED`/`UNKNOWN` decisions with monotonic observation/revision checks; native writes deliberately exclude local STOP/no-contact flags, reasons, timestamps and revisions.
- Enforced no-contact precedence, shop and customer isolation, changed-default-phone rejection, legacy-phone ambiguity and safe provider failure outcomes. Stored-send eligibility performs no Shopify lookup.
- Added isolated unit tests and real PostgreSQL/Prisma integration tests for the service/provider boundary. Confirmed no checkout creation, consent webhook consumer wiring, outbound-send call-site integration, Shopify consent mutation or STOP notification was added.
- Resolved initial local validation failures: aligned the nested Database schema to accepted DATABASE-002, corrected the BigInt revision test double and corrected a service return-type narrowing issue. Re-ran the applicable validation successfully.

**Attempt 2 response to the architect's Changes Requested:**

- Closed the stale-authorisation path when Shopify's current default phone changes from A to B but B's `updatedAt` predates A's stored grant. Invalidation now withdraws A's effective native grant with a revision-guarded update, sets its native decision to `UNKNOWN`, clears the active Shopify-native consent source, and retains the historical provider-observation timestamp; no fabricated later observation is written.
- Preserved monotonic consent-observation ordering by treating the retained timestamp as a fence even after A's active native source has been cleared. Duplicate or slightly newer-but-still-stale observations for B cannot regrant B; a genuinely newer Shopify observation can update B's native consent without overriding B's independently recorded local STOP.
- Kept local `whatsappNoContact`, its reason/time and no-contact revision untouched. Clearing the consent source also respects the accepted PostgreSQL trigger, which rejects a consent-decision change with a non-null source and no newer provider timestamp.
- Added and locally validated unit and PostgreSQL regression coverage for the displaced recipient, stale retries, changed checkout eligibility, observation ordering, trigger behaviour and concurrent STOP preservation.

### Validation Results

**Attempt 1 historical evidence** (previously reviewed; retained for traceability):


| Command / check | Final result | Evidence |
| --- | --- | --- |
| `npm run build` (`npm run prisma:generate && tsc`) | **PASS** | Prisma Client 6.19.3 generated against accepted DATABASE-002 schema; no final `tsc` diagnostics |
| `npx vitest run tests/unit/providers/shopify-whatsapp-consent.provider.test.ts tests/unit/services/shopify-whatsapp-consent.service.test.ts` | **PASS — 34/34** | 22 provider cases, 12 service cases; `typescript(20261022-144656)` |
| `npm run test:integration -- tests/integration/shopify-whatsapp-consent.integration.test.ts` | **PASS — 2/2** | Real PostgreSQL projection, ordering, STOP independence, changed-recipient and customer isolation; `typescript(20261022-144656)` |
| Targeted `npx eslint` over the two new source files and three new test files | **PASS** | Exit without diagnostics; `typescript(20261022-145923)` |
| `git diff --check` | **PASS** | No whitespace diagnostics; `typescript(20261022-145923)` |
| Task branch and nested Database revision | **CONFIRMED FOR IMPLEMENTATION WORKTREE** | `task/ARCH-045-BACKGROUND-001`; `+e0ab833... database` (local nested gitlink differs from its original recorded pointer); `typescript(20261022-145923)` |

Earlier failed checks (`typescript(20261022-140614)`, `typescript(20261022-142108)`, `typescript(20261022-144127)`) were superseded by the successful **Attempt 1** rerun after Database alignment and test/service corrections: **34 unit + 2 PostgreSQL tests passed**. That baseline did not cover the architect's stale changed-default-phone defect.

**Attempt 2 focused validation — 2026-10-22 (terminal capture `typescript(20261022-162629)`):**

| Command / check | Result | Evidence |
| --- | --- | --- |
| `npm run build` (Prisma generate, then TypeScript `tsc`) | **PASS** | Prisma Client 6.19.3 generated; no TypeScript build diagnostics |
| `npx vitest run tests/unit/providers/shopify-whatsapp-consent.provider.test.ts tests/unit/services/shopify-whatsapp-consent.service.test.ts` | **PASS — 38/38** | 22 Shopify provider tests + 16 service tests |
| `npm run test:integration -- tests/integration/shopify-whatsapp-consent.integration.test.ts` | **PASS — 3/3** | Real PostgreSQL projection, changed-default-phone with older `updatedAt`, retry/ordering fence, local STOP and cross-customer isolation |
| Targeted `npx eslint` for service and modified unit/integration test files | **PASS** | No diagnostics after the test runs |
| `git diff --check` | **PASS** | No whitespace diagnostics |

**Total in the latest run: 41 tests passed, zero failed.** The unit suite uses an injected provider; the PostgreSQL suite exercises the real Database trigger and consent projection. These checks do not substitute for a live Shopify protected-customer-data permission test or the downstream BACKGROUND-002/003/004 integration work.

### Deviations

No change to the task's architecture or repository ownership. The implementation required the already-accepted Database commit `e0ab833` for Prisma fields and Shared `2.5.0` for identity/phone helpers. Focused ESLint used the repository's existing `npx eslint` executable rather than linting all unrelated files. Multiple earlier delivery patches were corrective iterations under **canonical Attempt 1**, not a second claim. The **later** stale-default-phone changes are the architect-requested rework proposed for **Attempt 2**; a patch filename or successful test run is not evidence of the required separate developer claim. No new database migration, queue contract, provider write or consumer call-site change was introduced. The architect did not make missing Shared lockfile integrity metadata a blocker for this correction.

### Assumptions

- Native consent reads use Shopify Admin GraphQL 2026-07, the shop's existing offline-session token and the task-defined `read_customers`/protected customer-data access. Live provider permissions still require integrated verification.
- Checkout deduplication and admission wiring are performed by BACKGROUND-002; consent-sync webhook routing by BACKGROUND-003; stored-final-send enforcement by BACKGROUND-004; STOP recording and Support notices by BACKGROUND-005. This task exposes the tested provider/service APIs only.
- No consent-expiry window is imposed; eligibility is based on current native consent projection, exact recipient identity and separately authoritative local no-contact state.

### Unresolved Issues

- **No known remaining source/test failure for the reviewed stale-consent defect.** The original issue (A's stored grant surviving when Shopify changes the default to B with an older provider `updatedAt`) is addressed by withdrawing A's active consent source/decision while retaining the provider timestamp as an ordering fence; the passing unit and PostgreSQL tests exercise this behaviour. This closes the **technical** correction request, not the formal architect review.
- **Attempt 2 claim evidence not supplied:** the most recent parent task snapshot still shows `status: ready`, `attempt: 1`, `executor: null` and `claimed_at: null`. A successful `/moda_developer_create ARCH-045-BACKGROUND-001` claim (including recorded preparation/synchronisation evidence) is required before marking the task `in_progress` at Attempt 2 or submitting it as `review`. Do not increment the attempt by hand merely because patches are labelled Attempt 2.
- **Final Git evidence not supplied:** the 2026-10-22 17:25–17:26 validation capture does not include the final Background implementation commit SHA, proof of its push to `origin/task/ARCH-045-BACKGROUND-001`, or the parent task/report submission commit. Retain the prior accepted attempt's Git identifiers below as **Attempt 1 history only**, not as proof that the latest correction was pushed.
- **Start-of-attempt launch packet:** the Attempt 1 launcher packet was not retained; preserve known physical worktree paths and observed branch/revision evidence below, and include the actual Attempt 2 launcher-resolved isolation, synchronisation and recursive submodule evidence in the eventual submitted Completion Report.
- **Non-blocking observation:** Shared `2.5.0` lockfile integrity metadata was noted in Attempt 1 but was not made a correction blocker by the reviewing architect. Live Shopify protected-customer-data authorisation and downstream send-path coverage belong to their defined integration/system-test gates.

### Architectural Concerns

No unapproved new schema, queue contract, Shopify writes, STOP-to-Shopify propagation, or cross-repository consumer wiring was added. The Attempt 2 correction honours the existing Database trigger and keeps provider-observation ordering distinct from default-phone identity invalidation. Verify deployed Shopify protected-customer-data access and final send-path integration under downstream ARCH-045 tasks/system testing. No new architectural decision is proposed by this implementation.

### Git / VCS — review reconciliation

```text
Task branch:
  task/ARCH-045-BACKGROUND-001

Physical worktree isolation:
  canonical workspace root: /Users/kwadwoadomafriyie/project/moda-interact-workspace
  parent worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-045-BACKGROUND-001
  parent branch: task/ARCH-045-BACKGROUND-001
  implementation worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-045-BACKGROUND-001
  implementation branch: task/ARCH-045-BACKGROUND-001
  both canonical worktrees were clean at review; each task branch matched its origin task ref
  shared checkout reuse: none observed during review; original launcher packet unavailable

Start-of-attempt synchronization:
  original launcher packet and exact four sync decisions: unavailable
  implementation branch base: 3be52d6; current origin/main is f9659c1 and contains two later commits not in this task branch
  parent branch synchronization at claim: current ancestry confirms task branch history, but the launcher packet was not retained

Implementation repository:
  repository: moda-interact-background
  commit: 8cb11ff71845ec131883815c4130840fb1120dc0
  remote branch: origin/task/ARCH-045-BACKGROUND-001
  pushed: yes; local HEAD matches remote task branch
  nested database dependency: e0ab833d2e2395e3ed3cfe4aee6d07c716173e44 (initialized at the recorded gitlink)

Parent workspace:
  task file: docs/decisions/background/ARCH-045/BACKGROUND-001-read-shopify-whatsapp-consent-for-recipient.md
  review-submission commit before this Changes Requested record: b90961f30
  remote branch: origin/task/ARCH-045-BACKGROUND-001
  pushed: yes; parent branch matched its remote before this review update
  parent implementation-repository submodule gitlink staged: no

Merged to implementation main: not reported
Merged to workspace main: not reported
```

**Attempt 1 review VCS evidence above remains historical.** Its implementation SHA (`8cb11ff71845ec131883815c4130840fb1120dc0`) and prior parent submission SHA (`b90961f30`) do not establish publication of the Attempt 2 correction. The subsequent Changes Requested parent review record was reported committed/pushed as `2426ce906a42d18c16c77605575f8debc7ee5e7b` (per developer-provided review handoff).

**Attempt 2 follow-up evidence (to reconcile before submission):**

```text
Latest supplied parent task snapshot: status=ready, attempt=1, executor=null, claimed_at=null
Attempt 2 launcher claim / claimed_at: not supplied
Attempt 2 launcher-resolved isolation, synchronisation, submodule packet: not supplied
Implementation worktree used for successful local tests:
  /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-045-BACKGROUND-001
Local test capture: typescript(20261022-162629), 2026-10-22 17:25–17:26 UK time
Implementation commit with Attempt 2 correction: not supplied
Implementation push / remote parity: not supplied
Parent task/report submission commit and remote parity: not supplied
```

**Submission stop point:** Verify/reconcile the canonical Attempt 2 claim through the developer launcher, record its actual metadata and preparation evidence, commit/push the corrected Background files on `task/ARCH-045-BACKGROUND-001`, then transition the parent task to `review` with the actual SHA/remote evidence and push its task report. Preserve all Attempt 1 review history and leave `docs/decisions/**/_index.md` untouched. Stop for `moda_architect`; developer final completion remains a later explicit decision after passing review.

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

## Developer Self-Review - Changes Requested

- Attempt reviewed: 1. No new claim or attempt increment was made.
- Implementation branch: `task/ARCH-045-BACKGROUND-001`, commit `8cb11ff71845ec131883815c4130840fb1120dc0`, published to `origin/task/ARCH-045-BACKGROUND-001`; implementation worktree was clean at review.
- Parent review-submission branch was `task/ARCH-045-BACKGROUND-001`, commit `b90961f30` before this correction record. Parent task/report changes remain restricted to this file; do not stage a submodule gitlink or merge to `main`.
- Focused checks independently rerun: provider/service unit tests 34/34 passed; PostgreSQL integration 2/2 passed; `npm run build` passed; targeted ESLint passed; `git diff --check` passed. These checks do not cover the stale changed-default-phone timestamp case described above.
- Required correction: add the stale-timestamp changed-default-phone regression and ensure stored eligibility for the previous phone is denied without moving observation ordering backwards or mutating local STOP state. Validate with focused unit and PostgreSQL tests, then rerun the required build/lint/diff checks.
- Result: Changes Requested. Transition to `status: ready`, clear `executor` and `claimed_at`, preserve Attempt 1. No completion decision or merge to `main`.
