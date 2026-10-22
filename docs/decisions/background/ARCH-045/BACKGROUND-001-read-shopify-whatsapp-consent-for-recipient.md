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
claimed_at: 2026-10-22T13:18:19Z
attempt: 1
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
- [x] No mismatched, unidentified or changed recipient is considered authorised by phone equality alone; no recovery is created by this reader/synchroniser.
- [x] Provider errors, absent fields and ambiguous identities cannot authorise first recovery creation; follow-up denial uses current stored consent/STOP. No API read, including a later `SUBSCRIBED`, clears local STOP; no Shopify mutation/write scope or STOP retry is present.

## Validation

- [x] `npx vitest run tests/unit/providers/shopify-whatsapp-consent.provider.test.ts tests/unit/services/shopify-whatsapp-consent.service.test.ts`: exercise fresh checkout consent, stored-only follow-ups, subscribed/revoked/unknown, HTTP-200 GraphQL errors, read scope denial, native grant after local STOP, wrong default phone, customer-ID conversion, ambiguous identity and timeouts with injected fakes. **34/34 passed** in the final 2026-10-22 terminal log (provider 22; service 12).
- [x] Run `tests/integration/shopify-whatsapp-consent.integration.test.ts` with the repository's existing `scripts/test-integration.mjs` harness: verify real PostgreSQL active-recipient matching, duplicate/out-of-order observations, monotonic revisions and concurrent STOP/revocation. No live Shopify access is required. **2/2 passed** via `npm run test:integration -- tests/integration/shopify-whatsapp-consent.integration.test.ts`.
- [x] Run repository-declared `npm run build` and targeted `npm run lint` (or the equivalent existing validation contract) and `git diff --check`. Prove that initial live Shopify reads occur **outside** database transactions, and subsequent outbound eligibility uses stored revisions without GraphQL calls or Shopify writes. **Build/Prisma generation passed; targeted `npx eslint` passed; `git diff --check` emitted no errors**. The Background-local source uses no database transaction around `readCurrent()`; stored eligibility uses database reads only.

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

**Implementation and local validation complete; developer Attempt 1 remains `in_progress` pending review submission.** The 2026-10-22 validation captures show 36 passing tests, successful TypeScript/Prisma build, targeted lint and diff checks. Patch-file "Attempt 2" corrections were applied within the existing **canonical task Attempt 1** claim, not claimed as a separate task execution attempt. Update task YAML to `status: review` and this paragraph to "Ready for Review" only after publishing both mirrored task branches and recording the outstanding VCS/launcher evidence below.

### Files Changed

Relative to `moda-interact-background/`:

- `src/providers/shopify-whatsapp-consent.provider.ts` (new)
- `src/services/shopify-whatsapp-consent.service.ts` (new)
- `tests/unit/providers/shopify-whatsapp-consent.provider.test.ts` (new)
- `tests/unit/services/shopify-whatsapp-consent.service.test.ts` (new)
- `tests/integration/shopify-whatsapp-consent.integration.test.ts` (new)
- `package.json` and `package-lock.json` (consume Shared `2.5.0`)
- `database` nested submodule pointer in the implementation repository: accepted `ARCH-045-DATABASE-002` commit `e0ab833d2e2395e3ed3cfe4aee6d07c716173e44`

This task/report update modifies **only this task document** in the parent workspace; no `docs/decisions/**/_index.md`, parent architecture, another task, or parent implementation-repository gitlink is included in the report patch.

### Work Completed

- Added read-only `ShopifyWhatsAppConsentProvider.readCurrent()` against 2026-07 Admin GraphQL with offline-token reuse, injected transport, timeout/abort, response bounds and fail-closed handling for HTTP, GraphQL, access and malformed-result failures.
- Added `ShopifyWhatsAppConsentService.syncCustomer()`, `.evaluateRecipient()` and `.evaluateStoredRecipient()` using shop-owned Shopify customer identity, Shared international-phone canonicalisation and the **exact active** `CustomerPhone`.
- Persisted native `GRANTED`/`REVOKED`/`UNKNOWN` decisions with monotonic observation/revision checks; native writes deliberately exclude local STOP/no-contact flags, reasons, timestamps and revisions.
- Enforced no-contact precedence, shop and customer isolation, changed-default-phone rejection, legacy-phone ambiguity and safe provider failure outcomes. Stored-send eligibility performs no Shopify lookup.
- Added isolated unit tests and real PostgreSQL/Prisma integration tests for the service/provider boundary. Confirmed no checkout creation, consent webhook consumer wiring, outbound-send call-site integration, Shopify consent mutation or STOP notification was added.
- Resolved initial local validation failures: aligned the nested Database schema to accepted DATABASE-002, corrected the BigInt revision test double and corrected a service return-type narrowing issue. Re-ran the applicable validation successfully.

### Validation Results

Developer terminal captures dated **2026-10-22** (provided with this review preparation):

| Command / check | Final result | Evidence |
| --- | --- | --- |
| `npm run build` (`npm run prisma:generate && tsc`) | **PASS** | Prisma Client 6.19.3 generated against accepted DATABASE-002 schema; no final `tsc` diagnostics |
| `npx vitest run tests/unit/providers/shopify-whatsapp-consent.provider.test.ts tests/unit/services/shopify-whatsapp-consent.service.test.ts` | **PASS — 34/34** | 22 provider cases, 12 service cases; `typescript(20261022-144656)` |
| `npm run test:integration -- tests/integration/shopify-whatsapp-consent.integration.test.ts` | **PASS — 2/2** | Real PostgreSQL projection, ordering, STOP independence, changed-recipient and customer isolation; `typescript(20261022-144656)` |
| Targeted `npx eslint` over the two new source files and three new test files | **PASS** | Exit without diagnostics; `typescript(20261022-145923)` |
| `git diff --check` | **PASS** | No whitespace diagnostics; `typescript(20261022-145923)` |
| Task branch and nested Database revision | **CONFIRMED FOR IMPLEMENTATION WORKTREE** | `task/ARCH-045-BACKGROUND-001`; `+e0ab833... database` (local nested gitlink differs from its original recorded pointer); `typescript(20261022-145923)` |

Earlier failed checks (`typescript(20261022-140614)`, `typescript(20261022-142108)`, `typescript(20261022-144127)`) were superseded by the successful rerun after the Database alignment and test/service corrections. **36 tests passed, zero failed** in the final successful run. These are local development tests with injected Shopify reads, not a live protected-customer-data Shopify permission test.

### Deviations

No change to the task's architecture or repository ownership. The implementation required the already-accepted Database commit `e0ab833` for Prisma fields and Shared `2.5.0` for identity/phone helpers. Focused ESLint used the repository's existing `npx eslint` executable rather than linting all unrelated files. Multiple delivery patches were corrective iterations under **canonical Attempt 1**, not a second claim.

### Assumptions

- Native consent reads use Shopify Admin GraphQL 2026-07, the shop's existing offline-session token and the task-defined `read_customers`/protected customer-data access. Live provider permissions still require integrated verification.
- Checkout deduplication and admission wiring are performed by BACKGROUND-002; consent-sync webhook routing by BACKGROUND-003; stored-final-send enforcement by BACKGROUND-004; STOP recording and Support notices by BACKGROUND-005. This task exposes the tested provider/service APIs only.
- No consent-expiry window is imposed; eligibility is based on current native consent projection, exact recipient identity and separately authoritative local no-contact state.

### Unresolved Issues

- **Review submission VCS evidence pending.** The last supplied `git status --short` showed uncommitted dependency/source changes and an unrelated untracked `typescript` terminal capture. No implementation branch commit SHA or successful push was shown; do not stage the `typescript` file.
- **Mandatory launcher/start-of-attempt evidence pending.** The supplied ZIP and logs do not establish the canonical workspace root, resolved parent physical worktree, parent branch checkout, all four sync decisions, or absence of shared-checkout/task-worktree reuse. Record the actual launcher packet or worktree/sync evidence below rather than inventing it.
- The Shared `2.5.0` lockfile package entry in the supplied snapshot has a `resolved` tarball but no `integrity` value. The recorded final tests/build do not show a clean `npm ci` from this lockfile; regenerate/pin metadata if required by the repository's dependency policy before submission.
- Parent task/report branch commit SHA and push outcome are not in the supplied terminal captures. Record these during the submission step; do not claim an architect review or developer completion yet.

### Architectural Concerns

No unapproved new schema, queue contract, Shopify writes, STOP-to-Shopify propagation, or cross-repository consumer wiring was added. Verify deployed Shopify protected-customer-data access and final send-path integration under downstream ARCH-045 tasks/system testing. No new architectural decision is proposed by this implementation.

### Git / VCS — pre-submission evidence, to reconcile before `status: review`

```text
Task branch:
  task/ARCH-045-BACKGROUND-001

Physical worktree isolation:
  canonical workspace root: NOT PRESENT IN SUPPLIED EVIDENCE — record launcher-resolved absolute path
  parent worktree: archive directory named moda-interact-workspace-task-ARCH-045-BACKGROUND-001; absolute launcher path NOT VERIFIED
  parent branch: task/ARCH-045-BACKGROUND-001 (task metadata); parent git branch command NOT PROVIDED
  implementation worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-045-BACKGROUND-001 (terminal working directory)
  implementation branch: task/ARCH-045-BACKGROUND-001 (git branch --show-current)
  shared workspace checkout switched/mutated for task work: NOT EVIDENCED
  shared implementation checkout switched/mutated for task work: NOT EVIDENCED
  another task worktree reused: NOT EVIDENCED

Start-of-attempt synchronization:
  parent remote task branch fast-forwarded: NOT EVIDENCED (expected yes|not-needed)
  parent origin/main incorporated: NOT EVIDENCED (expected yes|already-current)
  implementation remote task branch fast-forwarded: NOT EVIDENCED (expected yes|not-needed)
  implementation origin/main incorporated: NOT EVIDENCED (expected yes|already-current)

Implementation repository:
  repository: moda-interact-background
  commit: PENDING — record git rev-parse HEAD after current-task implementation commit
  remote branch: origin/task/ARCH-045-BACKGROUND-001
  pushed: NOT SHOWN in supplied capture
  nested database dependency: e0ab833d2e2395e3ed3cfe4aee6d07c716173e44 (working-tree submodule status showed +)

Parent workspace:
  task file: docs/decisions/background/ARCH-045/BACKGROUND-001-read-shopify-whatsapp-consent-for-recipient.md
  commit: PENDING — record task/report publication commit or pre-submission claim commit and use remote branch to identify the final report
  remote branch: origin/task/ARCH-045-BACKGROUND-001
  pushed: NOT SHOWN in supplied capture
  parent submodule gitlink staged: NOT EVIDENCED — must remain no

Merged to implementation main: not reported
Merged to workspace main: not reported
```

**Submission stop point:** once the implementation branch is committed/pushed and the mandatory evidence is filled from the actual launcher and Git state, change this task's YAML `status` from `in_progress` to `review`, change `### Status` to "Ready for Review", commit/push **only this task document** on the matching parent branch, and return control to `moda_architect`. Developer final completion remains a separate explicit action after a passing review.

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
