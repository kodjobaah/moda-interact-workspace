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
status: complete
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

- [x] Implement only the bounded capability and document compatibility/rollout.
- [x] Add meaningful prior-behavior red and regression/concurrency/security coverage.
- [x] Complete required validation and mirrored task report/push.

## Interfaces / Contracts

Published @modainteract/moda-interact-shared/commerce/presentation for reusable media schemas/digests; Background owns live provider access, tenant/domain/READY evidence and lifecycle.

## Dependencies

ARCH-073-BACKGROUND-002
ARCH-073-BACKGROUND-003
ARCH-073-SHARED-002

## Enables

Dependent tasks only after architect acceptance.

## Acceptance Criteria

- [x] Required bounded behavior works without hardcoded identity or broader permissions.
- [x] Tenant/domain, immutable state, authorization and concurrent-update boundaries remain enforced.
- [x] Existing unrelated media/frozen content is preserved; no secret/private proof committed.
- [x] Canonical dedicated mirrored worktree/synchronization/recursive submodule evidence recorded.

## Validation

- [x] Product-priority, logo/plain text, HUMAN configured/passthrough/notices, missing/stale/foreign/tampered logo, caption/Unicode/full text fallback.
- [x] Actual PostgreSQL HUMAN frozen media/replay/moderation/final permit/provider identity and competing asset/control/domain changes; legacy text/product evidence.
- [x] Fresh public-registry package install/integrity, focused + full CI, types/scoped lint/declared build; no live sends.
- [x] Diff/secret hygiene and canonical isolated mirrored execution/report evidence.

## Stop Condition

After Work Items, Acceptance Criteria and required Validation complete, submit review report and STOP. Do not merge/deploy or begin enabled work.

## Implementation Notes

You are not alone. Preserve others' changes. Use prepared canonical packet. Root owns final merges/deployment; architect owns acceptance. Read historical code as evidence, not permission to restore unrelated behavior or stale API assumptions.

## Completion Report

### Status

Ready for Review. Implementation and validation complete; awaiting moda_architect review.

### Files Changed

- Background dependency/lock and exact-version consumer assertions adopt public Shared 5.13.7.
- `conversation-brand-media.ts`, `conversation-delivery-plan.ts` and the existing READY resolver implement current LOGO→SQUARE selection, canonical published plans, full-caption fallback and strict local immutable envelope.
- Wrapper/AI/HUMAN preparation, dispatcher and outbound delivery/fence carry the same complete body, original authority/header, plan and media-policy snapshot through moderation, persistence and one physical IMAGE send.
- Background platform-configuration repository/contracts/service add optional same-validated-row `rowId`; ordinary/default snapshots remain compatible.
- Focused unit and disposable PostgreSQL logo tests cover composition, policy/source/domain/control/lease changes, original pending work and caption records. The old fresh arch047 passthrough expectation now includes the already accepted domain header; previously frozen content expectations remain exact. Existing real-row configuration integration assertions include the actual inserted rowId alongside the original exact key/version/value fields.

### Work Completed

- Product imagery retains priority. Only a current same-shop/domain READY LOGO or SQUARE_LOGO can produce BRAND_IMAGE; cover art, original URLs and fake product identities are excluded.
- Complete header/authored reply/checkout footer remains unchanged; caption over 1024 Unicode codepoints, missing/unready/config-unavailable media retains complete text before preparation. No extra logo message or post-freeze downgrade.
- New private envelope freezes original MESSAGE or HUMAN_COMMAND authority, published plan/digest, original verified header and same validated configuration row identity/version. Restart reuses it without ownership/header/media recapture. Legacy raw TEXT/product IMAGE and old HUMAN evidence remain supported unchanged.
- HUMAN newer inbound remains eligible under existing lease/control policy. Automated MESSAGE retains original version checks. Final DB-only admission revalidates stored header, active shop/domain/current READY source and actual runtime-environment fixed-key policy row under existing lock boundaries.
- Provider transport uses IMAGE while persisted caption contentType remains TEXT, preserving the merchant read-model contract. HUMAN provider caption/plan is taken from committed admission; notices/AI use the identical persisted/moderated expected body.
- Read-only Admin writer inspection: `src/lib/admin/platform-configuration/repository.ts:writeConfiguration` performs configuration CAS plus audit in one serializable transaction, without acquiring Shop/ShopBrand locks; no inverted Shop lock cycle was introduced. No Admin edits.

### Validation Results

- Prepared packet `/tmp/moda-arch073-bg004-prepare.json`: canonical isolated mirrored task branches, base ce39ca00723a98f36751547a9acb33fcab6ee368, recursive submodules and claim 91248b201cd14c58703068d59417a642f0de1188 supplied by launcher; no repeated claim/startup changes.
- Fresh cache `npm ci --ignore-scripts` and Prisma generation succeeded. Independent actual public tarball download HTTP200: 521753 bytes, SHA256 `7d1e115255e2f431d4ad302121edbd34ed81a87fa5b50c466379bb3900d3a623`; public SHA512 equals lock integrity; installed version 5.13.7. No local artifact dependency.
- Prior-behavior proof: the actual published legacy ConversationDeliveryPlanSchema rejects the valid BRAND_IMAGE accepted by the new canonical union/current Background boundary.
- Existing wrapper/HUMAN/outbound group: 345/345 passed. Final focused package/config/READY/composition group: 47/47 passed, including configured/unconfigured AI, configured HUMAN, product priority, Unicode/full-body fallback, role preference and immutable replay.
- Disposable PostgreSQL combined batch: 20/20 passed (new logo tests + existing header/HUMAN send tests). One local readiness timeout recovered via existing bounded startup retry. Initial fixture mutations were rejected by existing DB invariants; tests now use legal control transitions, an actually stale lease token and explicit immutable-write refusal.
- Final logo PostgreSQL file: 15/15 passed, including both terminal text/template routes sending exactly one image with complete moderated/persisted caption; HUMAN newer inbound; stale asset/domain/name/control/lease; policy revision and delete/recreate same-origin/reset-version refusal; original-header/ownership restart; pending legacy TEXT/product IMAGE preservation; Shop-lock asset race.
- Typecheck and scoped ESLint passed; diff whitespace passed. Declared `npm run build` passed after the final PostgreSQL run (no overlapping Prisma generation).
- Implementation source commit 4500bf7 plus final test-only commit 3982f109c1d593cbdc6d2ca9125ccbef496f09a7; PR https://github.com/kodjobaah/moda-interact-background/pull/210. Source-head CI runs 43303901738 (3m13s) and 43303941613 (3m21s) passed on 4500bf7eb3153a128f85f7d2f111d37b1435aff7: 4090 tests / 378 files. Final test-only commit 3982f109c1d593cbdc6d2ca9125ccbef496f09a7 preserves exact configuration snapshot assertions including actual inserted rowId; affected disposable PostgreSQL file passed 3/3 and scoped lint passed. Both final-head required checks passed: [43305033811](https://github.com/kodjobaah/moda-interact-background/actions/runs/43305033811) (1m57s) and [43305046165](https://github.com/kodjobaah/moda-interact-background/actions/runs/43305046165) (1m30s). Runtime source is unchanged from the fully validated source head. No production database, provider, credential, permission or send mutation.

### Deviations

Necessary bounded amendments were coordinated in the assigned task: a private existing-JSON envelope retains original ownership/header/policy proof; same-row optional configuration identity metadata prevents delete/recreate substitution. No schema, Shared contract/release, generic decoder or other implementation repository changed.

### Assumptions

Queue contracts, usage accounting and send idempotency keys are unchanged; the optional media work is outbound action-path preparation and one provider call. Persisted authority and existing final dispatch CAS preserve retry safety.

Logo authority requires an explicit persisted, validated public-media policy row with identity; default row-absent policy cannot authorize a logo. Full text remains available. Provider IMAGE caption limit is enforced before freeze; after freeze stale proof refuses rather than substituting content.

### Unresolved Issues

The selected development store remains CHANNEL_LOCKED and the standalone user-approved logo/operational READY observation is root-owned. This task did not bootstrap a production asset or send live messages; text fallback is not claimed as logo delivery. Root must perform deployment and genuine provider/image proof.

### Architectural Concerns

Rolling overlap requires draining old messaging/recovery readers before generating new augmented HUMAN commands or new BRAND_IMAGE envelopes. Old readers do not understand the additive private evidence/plan; new readers preserve old frozen bytes. No post-permit media lookup or extra message is used to work around this compatibility boundary.

## Architect Review

### Review Status

Accepted

### Review Notes

Reviewed actual runtime `4500bf7eb3153a128f85f7d2f111d37b1435aff7`, final test-only `3982f109c1d593cbdc6d2ca9125ccbef496f09a7` and durable report `11e8678b4`. Final existing configuration PG expectation correctly binds actual inserted rowId; runtime unchanged. Earlier header-restart and same-row policy identity findings are fixed. No outstanding implementation findings.

### Reviewed Files

Published-package pin/lock, canonical-media adapter/helper/envelope, wrapper/AI composition, HUMAN frozen evidence/dispatcher, notice admission/delivery, final source/policy/header fence, local optional configuration-row identity projection and unit/PostgreSQL tests.

### Validation Reviewed

Fresh public5.13.7 integrity/install; focused47 and compatibility345; real PostgreSQL combined20/logo15/affected existing config3; types/scoped lint/build. Runtime source full CI4090 tests/378 files and both final test-only-head CI green. Prepared canonical mirrored worktree/base/recursive evidence matches packet. No duplicate checks needed.

### Architecture Conformance

Conforms to additive published media contract and Background ownership, no schema/new provider enum/permission/credential changes. Product image priority, LOGO/SQUARE only, complete-caption TEXT record compatibility, old frozen replay and HUMAN admission policy preserved. Strict existing-JSON receipt keeps original ownership/header and same validated policy row identity/version; final network-free transaction rejects stale proof. No post-freeze downgrade or extra logo send.

### Follow-up

Developer merges/deploys and drains old readers before new-format preparation. All six source/release tasks are Complete, but architecture stays In Progress: approved standalone asset/authoritative READY observation and genuine Meta logo delivery remain operational gates. Controlled text fallback is not logo success. Root owns operational writes and final provider verification; public proof stays coarse.
