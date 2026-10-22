---
id: ARCH-045-BACKGROUND-001
architecture_id: ARCH-045
title: Synchronise and evaluate current Shopify phone consent
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-045-DATABASE-002
  - ARCH-045-SHARED-002
enables:
  - ARCH-045-BACKGROUND-002
  - ARCH-045-BACKGROUND-003
  - ARCH-045-BACKGROUND-004
  - ARCH-045-SYSTEM-TEST-001
created: 2026-10-20
updated: 2026-10-21
---
# Synchronise and evaluate current Shopify phone consent

## Architecture

Architecture ID: `ARCH-045`
Architecture document: `docs/architecture/ARCH-045-shopify-whatsapp-consent-gated-recovery.md`
Coordinator: `moda_architect`
**Lifecycle:** portable definition, **not** materialised in a developer task worktree or committed/pushed; no execution claim exists.

## Objective

Provide one injected Shopify-native WhatsApp-consent reader and current-state synchroniser for an existing shop-owned customer and **exact active `CustomerPhone` recipient**. Both ordinary checkout admission and proactive sending consume this policy; consent-sync webhooks reuse its synchronisation operation.

## Context

Shopify is the source of truth for its native WhatsApp marketing opt-in. `ARCH-045-DATABASE-002` holds the current local `CustomerPhone` projection, not a separate Shopify consent table. `BACKGROUND-003` handles webhook job routing; `BACKGROUND-002` owns first recovery creation; `BACKGROUND-004` owns final proactive-send integration.

## Scope

- Implement `src/providers/shopify-whatsapp-consent.provider.ts` as the **Shopify API-only reader**. Use the existing `getShopifyAccessToken(shopDomain)` from `src/services/shopify-session.service.ts`, the shop's 2026-07 Admin GraphQL endpoint and an injectable HTTP transport with bounded timeout. The provider returns a typed observation or unavailable/not-found result; it performs **no Prisma writes or recovery decisions**. A GraphQL HTTP 200 with `errors`, protected-field denial, malformed/missing fields or an unusable response must not yield an affirmative grant.
- Implement `src/services/shopify-whatsapp-consent.service.ts` as the **shop/customer/recipient eligibility and projection service**, injecting the typed provider interface and the existing Prisma database access. This is the only owner of CustomerPhone selection, monotonic Shopify consent synchronisation, local no-contact precedence, and the `ALLOWED` / `NOT_AUTHORISED` / `UNAVAILABLE` / `AMBIGUOUS` decision. No generic consent-provider registry or new dependency-injection framework.
- Resolve Shopify identity through the existing shop-owned `Customer` and Shared numeric/GID helper. Do **not** attach a Shopify customer ID to an existing Customer solely because its phone matches, or permit an unidentified guest to inherit a consent grant.
- Compare the checkout recipient with the Shopify-authoritative current phone using Shared canonical international-phone rules and an explicit country context where required. Use/update only the associated **active** `CustomerPhone`; a changed, missing or ambiguous phone cannot carry a previous number's grant.
- Project the provider's current state and observation timestamp monotonically onto CustomerPhone; newer revoke/unknown state and local customer STOP/merchant no-contact take precedence over stale positives. A sync event may refresh an already verified Customer/phone but must never create a checkout or recovery.
- Expose one injectable eligibility/snapshot interface used by `BACKGROUND-002/004`, including exact recipient, `customerPhoneId`, current consent revision and no-contact revision. Provide a **fresh Shopify preflight outside** the final short database send transaction; the final fence rechecks durable local revisions, not Shopify over the network under SQL locks.
- Test source failures, duplicates/reordering, shop isolation, changed phone, phone-only legacy merges, GraphQL access denial and preflight/revision races. Use the published Shared logging API without customer phone or payload logging.

## Out of Scope

- No checkout materialisation or merchant notices, consent-event worker routing, new consent/identity/erasure table, generic customer-identity redesign, recipient-reachability schema change, or consent-triggered checkout queue.

## Requirements

- [ ] A matching current Shopify-native `SUBSCRIBED` decision for the correct existing Shopify customer and exact recipient is necessary for a positive result; unknown, revoked, wrong-number, ambiguous and unavailable states fail closed.
- [ ] Phone equality is not proof of Shopify customer identity or consent. Local STOP and merchant suppression cannot be cleared by a delayed native grant.
- [ ] The current-state synchroniser and fresh-provider preflight are reusable by both normal admission and proactive dispatch without duplicated GraphQL/parsing logic.


## Work Items

- [ ] Add `src/providers/shopify-whatsapp-consent.provider.ts` with the 2026-07 GraphQL query, typed reader interface, bounded timeouts, safe response parsing and existing offline-token reuse.
- [ ] Add `src/services/shopify-whatsapp-consent.service.ts` with injected reader, shop-linked customer validation, active exact-recipient selection, monotonic CustomerPhone synchronisation, typed eligibility result and fresh preflight.
- [ ] Add `tests/unit/providers/shopify-whatsapp-consent.provider.test.ts` and `tests/unit/services/shopify-whatsapp-consent.service.test.ts`.
- [ ] Add `tests/integration/shopify-whatsapp-consent.integration.test.ts` for real PostgreSQL/Prisma recipient, concurrency and monotonic revision assertions. Do not duplicate consumer wiring owned by BACKGROUND-002/003/004.

## Interfaces / Contracts

**Canonical Background-local interfaces and entrypoints:**

- **Provider:** `ShopifyWhatsAppConsentReader.readCurrent(input)` in `src/providers/shopify-whatsapp-consent.provider.ts`, implemented by `ShopifyWhatsAppConsentProvider`. The provider accepts the shop's validated `shopDomain` and a Shared-validated Shopify customer GID, **not** an unverified customer phone lookup.
- **Service:** `ShopifyWhatsAppConsentService.syncCustomer(input)`, `.evaluateRecipient(input)` and `.preflightRecipient(input)` in `src/services/shopify-whatsapp-consent.service.ts`. Constructor-inject `ShopifyWhatsAppConsentReader` so tests can supply a fake; use the repository's existing Prisma client, not a second persistence abstraction unless tests require a narrow injected port.

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
  preflightRecipient(input: {
    shopId: string;
    customerId: string;
    shopifyCustomerId: string;
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

`syncCustomer` is called by **BACKGROUND-003** after receiving a consent-sync event; it only updates the correct existing `CustomerPhone`. `evaluateRecipient` is injected by **BACKGROUND-002** at normal recovery admission. `preflightRecipient` is injected by **BACKGROUND-004** outside the final send transaction; the final fence then checks the returned consent/no-contact revisions under its existing short transaction. The reader/service **do not** modify those consumers as part of BACKGROUND-001.

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

- [ ] Verified native consent is projected to the correct tenant-scoped active CustomerPhone; newer revocation/local STOP never regresses due to stale synchronisation.
- [ ] No mismatched, unidentified or changed recipient is considered authorised by phone equality alone; no recovery is created by this reader/synchroniser.
- [ ] Provider errors, absent fields, ambiguous identities and stale preflight results cannot authorise a proactive send; no provider HTTP/Redis I/O occurs inside the SQL send fence.

## Validation

- [ ] `npx vitest run tests/unit/providers/shopify-whatsapp-consent.provider.test.ts tests/unit/services/shopify-whatsapp-consent.service.test.ts`: exercise subscribed/revoked/unknown, HTTP-200 GraphQL errors, scope denial, shop/customer-ID conversion, UK/international variants, ambiguous identity, changed phone, STOP and timeout handling using injected fakes.
- [ ] Run `tests/integration/shopify-whatsapp-consent.integration.test.ts` with the repository's existing `scripts/test-integration.mjs` harness: verify real PostgreSQL active-recipient matching, duplicate/out-of-order observations, monotonic revisions and concurrent STOP/revocation. No live Shopify access is required.
- [ ] Run repository-declared `npm run build` and targeted `npm run lint` (or the equivalent existing validation contract) and `git diff --check`. Prove that preflight uses the provider **outside** any database transaction and returns revisions suitable for BACKGROUND-004's final fence.

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

Exact Shopify customer GID must be constructed only from a Shared-validated shop-linked customer identifier. Do not use a recovery phone number to search for another customer. Constructor injection of the narrow `ShopifyWhatsAppConsentReader` interface is sufficient; no framework is required. Structured logging uses the published Shared logger with no raw phone numbers, tokens or GraphQL payloads.

Before claiming, use the deterministic `/moda-task` launcher and its **actual** prepared packet, read the task's complete current Architect Review, and verify task/dependency status in the developer's canonical workspace. Preserve `docs/decisions/**/_index.md` untouched until the developer explicitly closes the architecture documentation session. New runtime structured logging uses `@modainteract/moda-interact-shared/logging` where applicable. No source outside this task's owner repository may be changed unless explicitly authorised by the architecture.

## Completion Report

### Status

Not Started — external portable definition, not materialised.

### Files Changed

None — not implemented.

### Work Completed

None.

### Validation Results

Not run; the supplied snapshot is not the developer's task worktree.

### Deviations

None.

### Assumptions

Use the 2026-10-20 snapshot for orientation; revalidate active code/configuration when the task is materially claimed. ARCH-045 does not impose a consent-expiry window; current Shopify consent and actual checkout eligibility are separate.

### Unresolved Issues

None recorded at definition time; report any discovered cross-repository dependency rather than implementing outside ownership.

### Architectural Concerns

None recorded at definition time.

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
