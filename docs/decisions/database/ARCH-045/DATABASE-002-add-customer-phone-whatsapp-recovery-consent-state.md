---
id: ARCH-045-DATABASE-002
architecture_id: ARCH-045
title: Implement Shopify and Moda-checkbox Woo consent, evidence and privacy schema
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: in_progress
priority: 20
executor: developer
claimed_at: 2026-10-21T18:04:20Z
attempt: 1
depends_on: []
enables:
  - ARCH-045-BACKGROUND-001
  - ARCH-045-BACKGROUND-003
  - ARCH-045-BACKGROUND-005
  - ARCH-045-SHOPIFY-003
  - ARCH-045-SHOPIFY-004
  - ARCH-045-SHOPIFY-005
  - ARCH-046-API-001
  - ARCH-046-API-004
  - ARCH-046-API-005
  - ARCH-046-BACKGROUND-001
  - ARCH-045-SYSTEM-TEST-001
  - ARCH-046-SYSTEM-TEST-001
  - ARCH-046-SYSTEM-TEST-002
created: 2026-10-21
updated: 2026-10-21
---
# Implement Shopify and Moda-checkbox Woo consent, evidence and privacy schema

## Architecture

Architecture ID: `ARCH-045`
Architecture document: `docs/architecture/ARCH-045-shopify-whatsapp-consent-gated-recovery.md`
Coordinator: `moda_architect`

**In-flight amendment, 2026-10-21:** The developer has already claimed Attempt 1 and produced an **unmerged** implementation in `moda-interact-database`. Amend this same task and correct that implementation before review; preserve its existing claim/attempt and any subsequent execution evidence. The old `SUPPORTED_EXTERNAL`/`APPROVED_EXTERNAL` path is no longer an approved requirement. This is not a second implementation task or an approval of the current code.

## Objective

Deliver one reviewed Database-owned schema and migration set for ARCH-045 and ARCH-046: default-deny, exact-recipient WhatsApp checkout-recovery consent on existing `commerce.CustomerPhone` for **Shopify native consent and Moda's own WooCommerce checkbox only**, one immutable Woo consent-evidence history, verified Woo account/guest checkout identity, local STOP/no-contact overrides, and durable privacy erasure protection. Do not store a merchant-selectable Woo consent source or integrate third-party consent plugins. No `CheckoutRecovery` exists merely because a checkout lacked consent; consent changes do not schedule recovery.

## Context

This is the consolidated replacement for the superseded `ARCH-045-DATABASE-003` and `ARCH-046-DATABASE-001` tasks. The attached unmerged Attempt 1 schema/migration/tests currently contain `WOO_APPROVED_EXTERNAL`, `APPROVED_EXTERNAL`, `NOT_CONFIGURED` and `MODA_CHECKBOX` selection, provider ID, installation source epoch/revision and evidence source-mode/provider/epoch fields. **Remove those abandoned facilities from the unmerged implementation rather than layering a new migration to undo them.** Preserve the valid customer-phone current state, immutable evidence, privacy, identity and permanent opt-out mechanisms that are independent of external integration.

The WooCommerce plugin collects consent through its own initially unchecked optional checkout field when the authorised installation is connected and the existing checkout-recovery feature is enabled. No merchant consent-source selector and no extra merchant consent-enabled flag are introduced by this task; plugin registration/gating and feature availability are consumer-owned.

## Scope

**A. Cross-platform current consent and recipient protection**

- Extend the existing `commerce.CustomerPhone` for `WHATSAPP_CHECKOUT_RECOVERY`: `UNKNOWN`/default deny, `GRANTED` and `REVOKED`; only `SHOPIFY_NATIVE` and `WOO_MODA_CHECKBOX` are valid provenance. Keep verified shop/customer/active canonical recipient, provider observation/verification times where applicable, monotonic current-state/decision revisions and permanent no-contact precedence. Provenance is an audit attribute, **not a merchant-selectable source**.
- Eliminate the Woo-only provider ID and consent source-epoch fields from `CustomerPhone` when they exist only to support external selection; remove `WOO_APPROVED_EXTERNAL` from the consent-source enum. Preserve essential independent ordering/replay protections. Do not infer consent from phone equality, checkout capture, a cookie flag or any other plugin.
- Preserve constrained active-phone rotation/uniqueness, canonicalisation, conditional revision checks and a short SQL dispatch fence for the exact recipient, no-contact and privacy state. Reuse `whatsapp.WhatsAppRecipientReachability` only as a **negative-only** permanent STOP safety fence when the recipient cannot safely be resolved to one CustomerPhone.

**B. WooCommerce Moda-checkbox consent evidence and identity**

- Reuse existing `woocommerce.WooCommerceInstallation` for authenticated installation/shop identity and its existing `status`, `credentialVersion` and credential lifecycle. **Do not add** `WooWhatsAppConsentCollectionMode`, `whatsappConsentMode`, merchant-selected provider, source epoch/revision or any consent-provider configuration table. Connection, disconnection and reactivation are application lifecycle checks, not consent-source selection.
- Create exactly one immutable `WooWhatsAppConsentEvidence`-equivalent table for Moda checkbox `GRANT`/`REVOKE`: scoped shop, verified customer/active canonical phone and checkout identity, declared purpose, unique `(shopId,eventId)`, canonical payload digest and same-ID/different-body protection, server-enforced decision ordering, current phone consent revision, accurate disclosure text/version/locale and decision/recorded timestamps. The originating collector is **fixed** to Moda's checkbox, implicit in this Woo table or an explicit fixed-value column if necessary; do not store a selectable `sourceMode`, `providerId`, `sourceEpoch` or `sourceRevision`. No queue/poller/wakeup/claim/ack state.
- Define only the verified account-or-cryptographically-bound guest session → checkout → existing `commerce.Customer` linkage required for consent and later **normal** checkout reconciliation. Reject unauthenticated session reuse, changed phone, forged checkout key, cross-shop identity and phone/email-only customer merging. Reuse existing identity models where sufficient; justify any minimal non-consent link.
- Keep monotonic sequencing and revision/idempotency protections for concurrent grant, revoke, resend and credential/session rotation. A newer withdrawal, STOP or erasure cannot be defeated by delayed positive evidence. Do not require a source-switch ABA epoch to enforce ordering.

**C. Privacy erasure and negative-only opt-out**

- Retain shop/platform-principal privacy-erasure fencing, redaction of current and historical `CustomerPhone` PII and lawful evidence anonymisation, including protection against delayed Shopify consent sync and Woo retries.
- Keep durable permanent STOP/merchant opt-out, including a shop/recipient negative-only fallback when no verified CustomerPhone is available; never treat that record as positive consent.

**D. Delivery and migration correction**

- Revise the **same unmerged** Prisma schema, `20261021170000_arch045_shared_woo_consent_privacy/migration.sql`, schema validator and disposable PostgreSQL integration test scripts. Remove external-provider/source-switch columns, enum variants, constraints, triggers and fixtures; revise tests around active installation, exact customer/phone, ordering, evidence and erasure instead. Do not add an inverse migration just to remove unmerged columns.
- Verify all surviving Prisma-to-SQL contracts agree, including uniqueness, foreign keys, replay digests, disclosure integrity, privacy/STOP precedence and the immutable evidence exception for verified erasure.

## Out of Scope

- Any external consent plugin adapter, provider registry, CMP integration, duplicate-checkbox detection/management, merchant source selector or `SUPPORTED_EXTERNAL` support.
- Any Shopify/Woo HTTP route, Woo checkout UI, merchant Recoveries settings UI, third-party plugin configuration, Meta processor, recovery engine or Redis/BullMQ consent wake-up contract.
- Any consent-only CheckoutRecovery row, `WHATSAPP_CONSENT_MISSING` admission enum, arbitrary consent expiry or checkout polling triggered by a grant.
- Reimplementation of unrelated customer or checkout identity services beyond necessary database constraints.

## Requirements

- Migrated and new `CustomerPhone` values default to unknown/not authorised. Only the exact currently active, independently verified customer/recipient with valid Shopify native state or Moda-checkbox evidence is eligible; no source/provider setting can grant permission.
- Shopify's native consent remains externally authoritative and is synchronised into `CustomerPhone` by service-owned workflows. Woo uses verified Moda checkbox writes through the hosted API; the Woo evidence table is audit history, not a second current-consent source.
- Current grants, revocations, regrants, STOP, merchant opt-out and privacy erasure are correctly ordered under concurrency, retries, phone rotation and credential/session replacement. Local no-contact and erasure cannot be erased by delayed events.
- WooInstallation ACTIVE status and valid installation credentials are admission prerequisites to hosted Woo consent writes. Neither activation nor feature enablement automatically grants customer consent; an independently valid grant is required. Whether the checkout field is rendered is owned by WOOCOMMERCE-001.
- Reuse the published Shared canonical phone/Shopify principal helpers and fixtures. Never derive customer identity solely from contact data or guess dialling country without verified context.
- All sensitive DB updates/dispatch fences are short transactions; no provider or Redis network operations inside SQL transactions. No change schedules recovery or consumes usage credits.
- Retain tenant isolation, migration fresh/upgrade safety, privacy-safe evidence handling, idempotent replay, verified identity and declared runtime contracts.

## Work Items

- [ ] Reconcile the existing unmerged Attempt 1 schema, SQL migration and tests with the **Moda-checkbox-only** contract, removing all external source modes, provider IDs and source epochs/revisions used only for consent-source switching.
- [ ] Preserve/validate shared `CustomerPhone` default-deny exact-recipient state and monotonic decision/revision plus local permanent no-contact precedence; retain Shopify native and Woo Moda checkbox provenance only.
- [ ] Preserve/validate shop-recipient permanent negative-only STOP when customer attribution is ambiguous, separately from temporary reachability suppression.
- [ ] Keep `WooCommerceInstallation` on existing lifecycle/credential fields without new merchant consent-mode/provider configuration.
- [ ] Simplify the single Woo evidence schema, SQL constraints/triggers and replay tests to Moda checkbox-only, retaining immutable grant/revoke facts, event digest, disclosure, stable identity and decision ordering.
- [ ] Preserve/validate verified Woo guest/account/checkout association with session rotation, tenant isolation and no phone-only joins.
- [ ] Preserve/validate customer erasure fence, active/historical phone erasure, lawful evidence anonymisation, STOP dominance and delayed-event rehydration protection.
- [ ] Update schema-level validation and disposable PostgreSQL fresh/upgrade/race/erasure tests; specifically assert that `APPROVED_EXTERNAL`, `WOO_APPROVED_EXTERNAL`, `WooWhatsAppConsentCollectionMode`, installation mode/provider/epoch and evidence source-mode/provider/epoch **do not exist**.
- [ ] Record changed schema/migration/test files and actual validation results in the same task's Completion Report; do not mark the task accepted or completed without review.

## Interfaces / Contracts

- **Owner:** `moda_database`; one shared Database task for ARCH-045 and ARCH-046.
- **Current state:** `commerce.CustomerPhone` with native Shopify / Moda-checkbox Woo provenance; source is fixed by the authenticated platform integration, not merchant selection.
- **Woo installation:** existing `woocommerce.WooCommerceInstallation` authentication, status, `credentialVersion`, shop relation; no consent-source configuration.
- **Woo audit:** one immutable `WooWhatsAppConsentEvidence` table for authenticated Moda checkbox grants/withdrawals, idempotency and privacy; not a queue or current-consent table.
- **Woo identity:** verified installation-scoped account/guest-session/checkout → `commerce.Customer` association.
- **Privacy:** shop/platform-principal erasure fence, historical phone sanitation, consent evidence erasure/anonymisation and permanent negative-only no-contact.
- **Consumers:** ARCH-045 Background/Shopify and ARCH-046 API-001/API-004/API-005, WooCommerce plugin and future Background reconciliation. `ARCH-046-API-003` and `ARCH-046-WOOCOMMERCE-005` are **Superseded**; they are not schema consumers.
- **Shared contract:** merged `ARCH-045-SHARED-001`, published by `ARCH-045-SHARED-002`. No shared Woo queue schema.

## Dependencies

None. The in-progress developer task remains the sole shared DB foundation.

## Enables

- `ARCH-045-BACKGROUND-001`
- `ARCH-045-BACKGROUND-003`
- `ARCH-045-BACKGROUND-005`
- `ARCH-045-SHOPIFY-003`
- `ARCH-045-SHOPIFY-004`
- `ARCH-045-SHOPIFY-005`
- `ARCH-046-API-001`
- `ARCH-046-API-004`
- `ARCH-046-API-005`
- `ARCH-046-BACKGROUND-001`
- `ARCH-045-SYSTEM-TEST-001`
- `ARCH-046-SYSTEM-TEST-001`
- `ARCH-046-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] `CustomerPhone` is the only shared current permission authority with default unknown, exact verified customer/recipient, revision, STOP and privacy-fence precedence; only Shopify-native and Woo-Moda-checkout provenance remain.
- [ ] No third-party consent enum option, Woo installation source setting/provider/epoch, evidence source-mode/provider/epoch, provider-specific consent adapter or source-switch constraint exists in the revised unmerged migration/schema.
- [ ] One Woo evidence table supports recorded grant, revocation and regrant with fixed Moda provenance, disclosure and idempotent digest; conflict/stale ordering is rejected even under concurrent tabs and credential/session rotation.
- [ ] `WooCommerceInstallation` remains reusable for authenticated connection lifecycle without granting customer consent automatically; invalid/revoked installations cannot authorise new Woo grants.
- [ ] Verified Woo guest/account checkout linkage cannot be spoofed, confused across tenants or inferred from matching phones; canonical recipient/rotation protections remain intact.
- [ ] Permanent local STOP and merchant opt-out dominate stale positive consent; unbound STOP never becomes positive consent.
- [ ] Privacy erasure sanitises ended/current CustomerPhone and Woo evidence where required and prevents stale rehydration.
- [ ] Disposable PostgreSQL fresh/upgrade, identity, replay, consent-ordering, STOP/privacy and send-fence tests pass; migration is coherent with Prisma and published shared identity fixtures.
- [ ] No consent-triggered recovery, initial unconsented CheckoutRecovery, arbitrary consent timeout or charge is added.

## Validation

- [ ] Run actual database package Prisma validate/generate scripts and target schema-contract test.
- [ ] Run disposable PostgreSQL fresh and upgrade migration tests, asserting default deny and **absence** of withdrawn external-mode fields.
- [ ] Run targeted concurrent grant/revoke/regrant, same-ID/different-payload, lost ACK, customer-phone rotation, install revoked/reconnected, STOP and privacy erasure race fixtures.
- [ ] Run verified Woo guest-session/login/logout and cross-shop isolation fixtures, evidence privacy export/erase, SQL short-fence checks and `git diff --check`.
- [ ] Re-run required tests after changing the existing unmerged implementation; attach actual results rather than relying on earlier tests targeting the abandoned schema.

## Stop Condition

After all revised Work Items, Acceptance Criteria and validation pass, update the **existing Attempt 1** Completion Report, set the task to `review`, return it for the authorised review/developer completion decision, and STOP. No separate rework task, no opportunistic Woo or API implementation and no domain `_index.md` edits.

## Implementation Notes

The developer is permitted to amend the in-progress task because its implementation is unmerged. The current snapshot's task report still says `Files Changed: None` despite unmerged schema/migration/test files being present; reconcile the actual branch diff and report accurately before review. Do not infer a Git commit/push, task acceptance or test pass from this snapshot. Keep the existing developer claim/attempt and any durable prior review intact. The change removes hypothetical external-provider support without weakening verified customer identity, grant ordering, privacy or durable opt-outs. The accepted ARCH-045 Shared task remains a separate publication dependency, not a new Database task.

## Completion Report

### Status

In Progress — Attempt 1 claimed by developer at 2026-10-21T18:04:20Z. Attempt 0 review history is preserved below.

### Files Changed
None.

### Work Completed
None.

### Validation Results
Not run; this is a task definition.

### Deviations
None.

### Assumptions
Current supplied schema is a point-in-time reference; verify real implementation branch.

### Unresolved Issues
None recorded.

### Architectural Concerns
None recorded.

## Architect Review

### Review Status
Pending — no implementation reviewed.

### Review Notes
None.

### Reviewed Files
None.

### Validation Reviewed
None.

### Architecture Conformance
Not assessed.

### Follow-up
None.

## Developer Execution Ownership Amendment — 2026-10-21

The developer explicitly invoked `/moda_developer_create ARCH-045-DATABASE-002` for this agent-owned task. Execution and completion authority are transferred to the developer; `assigned_agent: moda_database`, repository ownership, scope, dependencies and acceptance criteria are unchanged. Canonical launcher preparation will record the developer attempt after worktree synchronization and dependency verification.
