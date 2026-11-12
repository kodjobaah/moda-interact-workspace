---
id: ARCH-073-BACKGROUND-004
architecture_id: ARCH-073
title: Deliver verified shop logos within existing recovery messages
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 15
executor: codex
claimed_at: 2026-11-12T20:00:49Z
attempt: 1
depends_on:
  - ARCH-073-BACKGROUND-002
  - ARCH-073-BACKGROUND-003
  - ARCH-073-SHARED-002
enables: []
created: 2026-11-12
updated: 2026-11-12
---

# Deliver verified shop logos within existing recovery messages

## Architecture

ARCH-073; docs/architecture/ARCH-073-tenant-recovery-shop-headers.md; coordinator moda_architect.

## Objective

Deliver verified shop logos within existing recovery messages.

## Context

User explicitly requests a shop logo where WhatsApp supports it. Existing canonical product-image plans cannot represent a brand image honestly; preserve product identity and the completed text baseline.

## Scope

Exact published Shared contract adoption, optional brand-image preparation for eligible AI/HUMAN/notices, local verified media receipts, HUMAN persisted frozen media/final permit/provider support and regression/docs.

## Out of Scope

Other tasks, source main merges/deployment, live sends, hardcoded merchant assets, fake product IDs, extra unsolicited messages, HTML image markup, database schema/new namespace/credential changes. No production permission mutation inside implementation.

## Requirements

One message only. Existing verified product image always takes priority. Otherwise-plain eligible replies may use verified current-generation same-shop/domain READY logo with complete branded text/header/footer as caption only within1024 Unicode codepoints; missing/unready/unsafe/config-unavailable/oversize image falls back full text with no logo loss of body. No extra logo message, HTML, raw client supplied logo URL, fake product IDs or unsupported plan coercion. Consume exact published Shared bytes, never sibling source. Resolve through existing tenant READY media adapter; bind selected asset provenance/digest and full body to immutable preparation, moderation, takeover/version/control fences, final committed permit and provider dispatch. HUMAN evidence must freeze text+media and replay same bytes/plan; no post-permit lookup selecting a different image. Final permit revalidates current asset/domain/source as needed outside-network-insideTX prohibition. Preserve old text/product plans and old HUMAN commands unchanged, explicit old-reader drain if incompatible. Approved template bodies and all forbidden/unbound sends unchanged. No new schema unless concrete gap returned before change.

### Frozen media and provenance clarification

Consume exact public Shared5.13.7 (accepted canonical521753-byte artifact SHA2567d1e115255e2f431d4ad302121edbd34ed81a87fa5b50c466379bb3900d3a623). Distinct BRAND_IMAGE maps to existing physical IMAGE transport; no fake product identity or new DB/Meta enum. Existing preparedWrapperEvidence and outboundPresentation JSON may carry validated additive media plan/digest if sufficient; return any demonstrated schema gap before changing it.

Selection policy is LOGO then SQUARE_LOGO only, never COVER_IMAGE, and current verified product image always wins. Extend existing READY adapter with authoritative source/generation/fingerprint/domain/content facts; no arbitrary client URL or self-attested schema alone. Final permit under existing Shop→Brand lock ordering revalidates same-tenant/domain/current READY generation/fingerprint/key/content identity; provider uses exact committed frozen image/body. HUMAN existing evidence must freeze optional plan/digest and replay it without auto-adding logo to old commands. AI and notices preserve the same body/plan/moderation identity. Capture control/inbound/version identity before preparation; do not recapture ownership after takeover.

Stable tokenless Storefront asset acquisition is accepted separately; current development store is CHANNEL_LOCKED, so controlled text fallback is expected until an authorized supported asset source becomes READY. Do not create credential/scope/channel changes, unlock stores, bootstrap production or claim fallback as logo delivery. Root is awaiting a standalone user-approved logo and owns operational source observation. No extra logo message.

### Caption/read-model compatibility

Developer merged header source at ce39ca00723a98f36751547a9acb33fcab6ee368. Root read-only audits found API/Admin/Shopify inboxes do not strict-parse the stored plan; Commerce preview's legacy parser is a separate path not fed this Background JSON. Do not expand other repositories unless an actual exposed dependency is found. Distinguish physical providerDispatchDeliveryKind IMAGE from ConversationMessage.contentType: preserve existing product-image caption record semantics, because the API maps contentType IMAGE to null text. Regression must prove new brand caption remains visible in the merchant inbox/read contract rather than accidentally blanking it. No fabricated content type or lost authored caption.

### Restart receipt envelope clarification

For new BRAND_IMAGE only, existing outboundPresentation JSON may persist a strict Background-local versioned envelope containing validated plan, original control/inbound/tenant/message receipt and canonical planDigest. Capture original ownership receipt before fresh media preparation; restart must rehydrate that same receipt, never recapture current ownership to make stale work eligible. Validate schema/unknown fields/digest/body/tenant/message/version/control consistency; malformed, missing or mutated proof refuses safely. Legacy raw TEXT/product IMAGE JSON and frozen commands remain unchanged byte-for-byte. HUMAN command's existing expected revision/identity remains authoritative; optional persisted plan must bind it. No premature provider-dispatch column writes, new schema or new Shared envelope contract. Root audited API/Admin readers as opaque, so no outside consumer change is needed for this private carrier.

### HUMAN versus automated receipt eligibility

Receipt source discriminator distinguishes MESSAGE from HUMAN_COMMAND. Automated MESSAGE retains existing inbound/version checks. HUMAN_COMMAND binds original durable command identity, lease and expected control revision; a captured inbound snapshot may be immutable evidence but must not add current-inbound equality if existing human admission allows a newer customer message. Preserve existing human policy: fresh inbound alone remains eligible, while takeover/control revision/lease changes refuse. Test both explicitly. Provenance must not silently tighten unrelated human send eligibility.

### Public-origin policy and header restart fences

Capture validated public origin and row version/identity from the same authoritative shopBrand.publicMedia adapter policy snapshot used to build the image. Persist a Background-local policy reference with immutable media receipt; no Shared/schema addition. Final network-free Shop→Brand transaction reads fixed-key public.PlatformConfiguration for the actual trusted runtime deployment environment FOR SHARE and compares captured version/row identity. Missing/changed policy refuses, without decoding or duplicating generic configuration inside the transaction. Compare existing Admin configuration writer lock order and add actual policy-change-between-preflight/final refusal proof. A frozen image's self-declared publicOrigin is not current-policy evidence.

Retain original validated recoveryShopHeader receipt in the new private envelope and rehydrate it on notice restart, so BG002 current name/domain final gate cannot disappear on replay. Never re-render/recapture identity to conceal stale prepared content. Add restart plus shop-name change refusal proof. Legacy receipt-absent raw plans remain unchanged.

### Same-row policy snapshot clarification

Background-owned platform-configuration repository/contracts/service may expose optional rowId from the SAME row already read and canonically validated. Prisma selects id; parseRow returns that identity with version/value. Existing legacy fake/default snapshots remain compatible through optional metadata, but logo authority requires rowId. Eliminate separate follow-up row-id binding: delete/recreate with same origin/reset version must not substitute another row for the validated one. Test that race and ordinary legacy/default configuration consumers. This narrowly owned metadata projection requires no Shared/schema or duplicate generic decoder.

## Work Items

- [ ] Implement only the bounded capability and document compatibility/rollout.
- [ ] Add meaningful prior-behavior red and regression/concurrency/security coverage.
- [ ] Complete required validation and mirrored task report/push.

## Interfaces / Contracts

Published @modainteract/moda-interact-shared/commerce/presentation for reusable media schemas/digests; Background owns live provider access, tenant/domain/READY evidence and lifecycle.

## Dependencies

ARCH-073-BACKGROUND-002
ARCH-073-BACKGROUND-003
ARCH-073-SHARED-002

## Enables

Dependent tasks only after architect acceptance.

## Acceptance Criteria

- [ ] Required bounded behavior works without hardcoded identity or broader permissions.
- [ ] Tenant/domain, immutable state, authorization and concurrent-update boundaries remain enforced.
- [ ] Existing unrelated media/frozen content is preserved; no secret/private proof committed.
- [ ] Canonical dedicated mirrored worktree/synchronization/recursive submodule evidence recorded.

## Validation

- [ ] Product-priority, logo/plain text, HUMAN configured/passthrough/notices, missing/stale/foreign/tampered logo, caption/Unicode/full text fallback.
- [ ] Actual PostgreSQL HUMAN frozen media/replay/moderation/final permit/provider identity and competing asset/control/domain changes; legacy text/product evidence.
- [ ] Fresh public-registry package install/integrity, focused + full CI, types/scoped lint/declared build; no live sends.
- [ ] Diff/secret hygiene and canonical isolated mirrored execution/report evidence.

## Stop Condition

After Work Items, Acceptance Criteria and required Validation complete, submit review report and STOP. Do not merge/deploy or begin enabled work.

## Implementation Notes

You are not alone. Preserve others' changes. Use prepared canonical packet. Root owns final merges/deployment; architect owns acceptance. Read historical code as evidence, not permission to restore unrelated behavior or stale API assumptions.

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

Pending

### Deviations

None

### Assumptions

None beyond explicit prerequisite gates.

## Architect Review

### Review Status

Pending

### Review Notes

Pending actual source review.

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

None
