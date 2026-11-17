---
id: ARCH-077-SHOPIFY-006
architecture_id: ARCH-077
title: Remove obsolete Shopify WhatsApp marketing-consent integration
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 80
executor: null
claimed_at: null
attempt: 0
depends_on: [ARCH-077-BACKGROUND-002, ARCH-077-SHOPIFY-005]
enables: [ARCH-077-SYSTEM-TEST-001]
created: 2026-11-17
updated: 2026-11-17
---

# Remove obsolete Shopify WhatsApp marketing-consent integration

## Architecture / status

[ARCH-077](../../../architecture/ARCH-077-shopify-owned-whatsapp-checkout-consent.md). **Definition reconciled; task remains `pending`.** This task is a preproduction cleanup, performed after BACKGROUND-002 has replaced native-provider consent reads and before final SYSTEM-TEST-001 certification. No application source change is authorised merely by applying this task definition.

## Objective and fixed decisions

Remove the unused Shopify WhatsApp **marketing-consent API** webhook/normalisation/publication integration and its obsolete Background sync processing. Shopify checkout consent is captured through the Moda S002/S003/S004 checkbox flow and materialised during eligible recovery processing by BACKGROUND-002.

- `commerce.CustomerPhone.whatsappConsentSource = SHOPIFY_NATIVE` **stays exactly as it is**. In the ARCH-077 application contract it identifies Moda's Shopify checkbox consent; it is **not** an instruction to call Shopify Messaging or Shopify's `whatsAppMarketingConsent` API.
- This is **preproduction**. Do not preserve, translate, drain, replay, or implement compatibility for obsolete native-consent jobs, webhooks, observations or test records. Do not add a legacy handler, transitional queue consumer, alias, feature flag, adapter or data migration.
- Do not flush a shared Redis database or delete unrelated cart, checkout, order, pending-recovery, BullMQ, STOP, routing or credit data. Any cleanup of preproduction native-consent jobs/test records is a separate, explicitly scoped environment operation, not application compatibility code.
- No database schema/migration, WooCommerce, `moda-interact-api`, Meta sender-pool, or general checkout event-contract changes.

## Ownership and execution boundary

**S006 owns `moda-interact` Shopify ingress and application-configuration cleanup.** BACKGROUND-002 owns replacement/removal of native Shopify consent readers, projection logic, sync consumer and final consent checks in `moda-interact-background`. S006 must **verify** that BACKGROUND-002 has completed that work; it must not independently edit Background source or duplicate its implementation task. If Background cleanup is not complete, stop and return to the architect, rather than leave a surviving native writer or introduce a compatibility shim.

Source touchpoints to inspect (verify exact paths against execution worktree):

**Shopify application (`moda-interact`):**

- `shopify.app.moda-interact.toml` (the named deployed app configuration; **not** the separate template `shopify.app.toml`).
- `app/routes/webhooks/root/route.jsx`.
- `app/services/webhooks/shopify-webhook-ingress.service.ts`.
- `app/services/webhooks/shopify-webhook-queue.server.ts`.
- `app/services/webhooks/shopify-whatsapp-consent-normalization.ts` (delete if no non-obsolete consumers remain).
- `tests/unit/webhooks/shopify-whatsapp-consent-config.test.js`.
- `tests/unit/webhooks/shopify-webhook-config.test.ts` and other tests asserting the obsolete topic, raw-body path or native publisher.

**Background completion audit only (owned by BACKGROUND-002):**

- `src/providers/shopify-whatsapp-consent.provider.ts`.
- `src/services/shopify-whatsapp-consent.service.ts` and `src/services/shopify-whatsapp-consent/projection-writer.ts`.
- `src/services/shopify-whatsapp-consent-sync-job.service.ts`.
- `src/workers/checkout.worker.ts` and `src/events/checkout-worker-dispatch.ts`.
- `src/services/checkout-recovery/recovery-consent-admission.service.ts`.
- `src/services/recovery-conversation/recovery-stored-consent.service.ts` and `src/services/recovery-conversation/recovery-runtime-eligibility.service.ts`.

## Required Shopify source changes

1. In **only** `shopify.app.moda-interact.toml`, remove `customers_whats_app_marketing_consent/update` from the existing `/webhooks` subscription. Preserve the remaining `carts/create`, `carts/update`, `checkouts/create`, `checkouts/update`, `orders/create`, discount topics, all privacy compliance topics, uninstall/scopes subscriptions, and their routes/API version.
2. In `app/routes/webhooks/root/route.jsx`, remove the consent-topic-only request clone and authenticated raw-body forwarding. Continue calling Shopify's existing `authenticate.webhook(request)` **before** trusting any webhook payload. Preserve general webhook failure logging and original errors (with redaction).
3. In `app/services/webhooks/shopify-webhook-ingress.service.ts`, remove native consent-topic classification, consent-specific raw-body input, customer-ID normalisation, consent-sync job creation/publication and consent-specific response/validation branches. Leave normal checkout/cart/order/discount processing, merchant eligibility, queue publication and observability intact.
4. In `app/services/webhooks/shopify-webhook-queue.server.ts`, remove the native-consent publisher and now-unused imports. Do **not** alter existing BullMQ queue names, connection configuration, retry settings, job IDs or other publishers. Do not invent replacement webhook work.
5. Delete the consent-only `shopify-whatsapp-consent-normalization.ts` module when all imports and owned tests have been removed. Do not delete generally shared Shopify customer-identity parsers.
6. Change static/subscription tests to assert **absence** of the native WhatsApp consent topic and **presence** of all required ordinary topics. Remove consent-topic-only unit fixtures/tests which have no remaining feature responsibility. Preserve/extend normal webhook authentication, publication and queue regression coverage.
7. Do not remove `read_customers` solely because native consent is gone: current recovery customer lookup, returning-customer consent read and recipient resolution still need customer access. Re-evaluate permissions only against real remaining consumers; do not remove scopes speculatively.

## Background completion gate (no S006 edits to Background)

Before accepting S006, inspect the accepted BACKGROUND-002 implementation and its evidence. Require all of the following:

- No Shopify GraphQL `customer.defaultPhoneNumber.whatsAppMarketingConsent` read, webhook-driven refresh, native-projection write or Shopify-native consent sync job processor remains reachable from recovery admission.
- The obsolete native-consent job case and handler have been **removed**, not replaced with a no-op compatibility branch. The existing `checkout-events` queue continues consuming only supported current cart/checkout jobs. Any obsolete preproduction jobs left in the environment are reset through explicitly scoped operations if required, not through code.
- The same `SHOPIFY_NATIVE` PostgreSQL source identifier and existing CustomerPhone consent revision, no-contact/STOP, merchant scoping and SQL final-send checks continue to operate for Moda checkbox-derived consent.
- New checkbox GRANT/REVOKE selections remain temporary Redis data until an eligible checkout is processed; subsequently persisted consent is read from PostgreSQL. Completed or ineligible checkouts do not materialise new consent.
- All native-only imports, job declarations, types and obsolete Background tests are reconciled by their owning Background task. Do not modify unrelated Shared contracts unless a distinct approved Shared task explicitly requires it.

If BACKGROUND-002 did not cover the required native worker/dispatch removal, record a blocker and request a B002 task correction before continuing; do not expand S006 into a second Background implementation assignment.

## Preproduction deployment and validation

- Confirm which Shopify app config is selected by the deployment command (`--config moda-interact`) and check the deployed app's effective webhook subscription list. Editing TOML alone is not evidence that Shopify has removed a subscription.
- Preproduction contains no required legacy-job compatibility. Any one-time cleanup must target **only** verified obsolete consent-sync job identities in the chosen environment and demonstrate that all other existing worker jobs/keys remain intact. Never call `FLUSHDB`, `FLUSHALL`, broadly delete BullMQ namespaces or blindly drain shared queues.
- Execute Shopify source lint/typecheck/build and the existing Shopify webhook unit and Redis integration suites in the actual implementation worktree. Record exact commands/results, commit SHA, selected config and dependency pins. Execute final end-to-end SYSTEM-TEST-001 **after S006**, not before.
- Use disposable Redis and PostgreSQL for tests. Confirm normal `carts/create`, `carts/update`, `checkouts/create`, `checkouts/update`, `orders/create` and discounts still publish, dispatch, reschedule/cancel as expected. Verify STOP, recipient admission, credit compensation and ARCH-076 routing are unchanged through Background integration tests.

## Acceptance criteria

- [ ] The named Shopify app configuration no longer subscribes to native WhatsApp marketing consent updates; regular webhook subscriptions are preserved exactly.
- [ ] Shopify webhook route and ingress no longer clone/parse/publish a special native-consent payload; all ordinary events still authenticate and publish.
- [ ] The native consent-only normaliser/publisher and obsolete Shopify tests are removed or updated without affecting other features.
- [ ] BACKGROUND-002 is accepted: native GraphQL consent reads, synchronisation writer/consumer and obsolete queue dispatch case are absent; no preproduction compatibility branch is retained.
- [ ] `SHOPIFY_NATIVE` enum and all current CustomerPhone/STOP/final-send database protections remain unchanged and support the Moda checkbox pathway.
- [ ] No database migration, WooCommerce/API changes, unrelated Redis mutation, job-queue replacement or extra worker has been introduced.
- [ ] Shopify webhook/Background integration tests pass and final SYSTEM-TEST-001 can run against the **post-cleanup** implementation.

## Stop conditions

Stop if a remaining native consent writer can overwrite a Moda checkbox decision, if normal checkout/cart/order processing depends on the code proposed for removal, if the named Shopify app deployment cannot be verified, or if the BACKGROUND-002 boundary is incomplete. Report the exact file, failing test and original safely redacted error to the architect; do not add legacy handling or relax existing safeguards to make the cleanup pass.
