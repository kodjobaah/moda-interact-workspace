---
id: ARCH-075-BACKGROUND-002
architecture_id: ARCH-075
title: Compose and integrate ordered recovery logo and product replies
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 10
executor: codex
claimed_at: 2026-11-13T03:20:23Z
attempt: 1
depends_on:
  - ARCH-075-BACKGROUND-001
  - ARCH-075-SHARED-004
  - ARCH-075-ADMIN-001
enables: []
created: 2026-11-13
updated: 2026-11-13
---

# Compose and integrate ordered recovery logo and product replies

## Architecture

ARCH-075; docs/architecture/ARCH-075-ordered-recovery-message-layout.md; coordinator moda_architect. Read all frozen contract constants and lifecycle decisions before implementation.

## Objective

Compose and integrate ordered recovery logo and product replies.

## Context

User requests logo/shop details before a distinct product image and checkout footer. Existing single-provider-id response cannot safely loop multiple sends. This task owns one bounded prerequisite capability; preserve completed prior behavior.

## Scope

Server-known header/footer composition for AI/HUMAN/eligible notices, wrapper/provenance preparation and processor/dispatcher integration with accepted engine, end-to-end tests/docs.

## Out of Scope

Other repositories/tasks, source main merges/deployment, production sends/replays/resets, billing/usage/cap changes, provider credentials/permissions, unsupported exactly-once assumptions, unbounded fanout/retries, unrelated refactors. Return actual cross-owner gaps.

## Requirements

Build canonical2/3part layout and singleTEXT fallback; eachpart exactcheckoutfooter. Preserve author middle bytes via known receipts/boundaries, never heuristic regex stripping. Actual verified first selected product pair/image only; brandheaderfromcurrentREADYlogo, no cover substitute. Header/detail image precedes separate product; answer fits productcaption then2parts, otherwise finalANSWER third. Missinglogo verifiedtextheader/fullanswer and missingproduct image safeTEXT; no suppressing otherwise legitimate response. Freeze original body/manifest/moderation/authority before firstsend; no postpermit edits/ownership recapture. AIoriginalversion, HUMANcommand/control/lease with newinboundpolicy unchanged, STOP/security/templates oldexact compatibility. One logical reservation/usage/cap, max3physical, no new merchantUIfeature. Handle returned partial/unknown truthfully and preserve inter-response conversation order.

### Common content authority amendment

Consume published5.13.9 commonRef/website binding and Admin001 immutable common revision, not a new hardcoded header/footer builder. Existing RecoveryShopHeaderReceiptv1 helpers enforce a fixed prefix and must remain legacy-only. Introduce additive local receiptv2 (existing JSON only) binding canonical commonRef, actual rendered header/footer and trusted split boundaries from the existing renderer, tenant/name/website/checkout facts and original source/control; final current-slot/source/locale/policy checks preserve original evidence. Frozen v1 replay stays byte-exact, no automatic upgrade. Eliminate fixed common prefix decoration for newly framed replies; audience/family-specific content remains body only. Custom common header/footer edits must visibly match Meta/AI/HUMAN goldens, proving one editable source rather than equal default strings. No regex stripping arbitrary authored HUMAN bytes. Update multipart frozen parser/derivation to recognize new receipt only after strict validation, preserve old plan/digest semantics.

Background website resolvers derive canonical saved tenant domain with existing HTTPS/origin policy. Meta registration preparation validates frozen commonRef against selected common revision; no mutation/recompile of provider snapshots at send. New Meta outreach still uses approved native template transport outside window, never freeform product tail. Product photos remain separate only under valid transport/window and frozen part provenance. Runtime consumer deployment precedes Admin002 activation; return any global-slot/per-shop assignment race gap.

### Logical admission and staged producer rules

Reuse the accepted engine reader/frozen source/part helpers and published validator; do not invent a second lifecycle, content renderer or receipt decoder. Use deterministic HUMAN root identity from commandId. Existing HUMAN Redis anti-spam/rate admission remains ONCE per logical command, not once per part; preserve original billing/usage/cap policy. No separate Meta HTTP rate limiter exists to reuse, so do not claim or invent one; transport is bounded by max3 parts and existing provider behavior. Initial HUMAN claim duration must cover its immutable logical delivery deadline using the existing bounded claim API (up to300seconds); do not extend/reacquire admitted authority after freeze. Existing default60seconds is shorter than default120second group deadline and is insufficient for initial prepermit waiting.

Production generation remains off until root verifies accepted compatible-engine Live and old-reader drain in BOTH test/production. Source can be implemented once dependencies are accepted, but producer merge/deployment activation is root-gated on that runtime evidence. Preserve actual AGENT/HUMAN sender semantics; do not retag AUTOMATION marketing/notices to bypass their existing final policy. If any eligible notice truly uses an unsupported actor, return the concrete gap rather than widen transport authorization.

### Confirmed AUTOMATION notice boundary

Eligible terminal/template-fallback notices may use actual AUTOMATION, which the accepted ordered engine intentionally does not authorize. Apply the SAME saved common textual header/checkout footer while preserving that actor and existing single-send/current-policy fences; no product pair requires no multipart transport. Never retag as AGENT or create a new actor permit. Preserve verified logo through an existing safely supported single BRAND_IMAGE path where available. If that actual actor path is only TEXT with no safe logo option, return the concrete gap before final acceptance and do not claim full logo parity. Persist/currently validate common-source provenance without rewriting legacy frozen notices or inventing an unreadable envelope; return any real staged-reader contract gap.

### Single-send common reader staging gate

Confirmed local gap: single BRAND_MEDIA header decoder/final fence is v1-only, and new singleTEXT common notice needs a strict private persistedv2 receipt. This task may add existing JSON envelope/header union v1|v2 and currentCommonLayoutMatches to existing single-send paths alongside their producers, preserving actual AUTOMATION policy/actor and safely supported existing logo behavior. No new public schema, database migration, setting or actor authorization. Legacy frozenv1 remains byte-exact; new text/common source authority must not be dropped on restart.

This combined reader/producer rollout is authorized ONLY because actual SHARED slot is absent in BOTH test and production. Root must reverify that absence immediately before merge and keep SHARED unactivated until BG002 is Live and predecessor readers drained in BOTH environments. No new common/v2 single-send or multipart format may emit without selected eligible SHARED common mode. Admin002 activation stays root-owned after those gates. If a SHARED slot exists/changes before rollout, STOP merge and return for separately staged compatible readers; never assume an unrecorded absence or add an unsafe flag. Record coarse runtime proof privately/publicly appropriately, no sensitive identifiers in public docs.

### Existing product follow-up context preservation

Ordered AI delivery must not silently lose the already-supported server-owned productContextUpdate. Optional private frozen carrier uses the existing canonical Shared context schema; source/part digest binds it. Reuse existing current-control/inbound/version/hash final-fence logic at ordinal0 only, atomically with the first irreversible permit; suppression/duplicate/failed admission must not commit a context mutation. Later parts never reapply or overwrite newer context. No new Shared release/schema/policy. Add actual successful and suppressed/duplicate first-part regressions. New optional private format remains covered by the explicit SHARED-absence/drain operational gate above.

### Meta common frame final-race contract

For newly authored approved registrations with commonRef, carry canonical commonRef plus exact verified tenant name/site/checkout values in existing Background-local templateRegistration identity. Bind that data to existing frozen registration identity, never arbitrary caller context. Final existing SQL permit re-reads actual registration locale authoring.commonLayout and REQUIRES matching carrier when present (omission refuses), validates public schema, locks/rechecks current SHARED definition/source/locale and current tenant facts. Reuse/factor current common source/fact checker, no duplicate renderer/SQL policy or new Shared/database schema. Never compile/mutate provider components at send time. Preserve old frozen registration eligibility by its existing identity, no retrofit of current frame. Test slot/source/domain/name/checkout change between preparation and permit, missing/tampered carrier, positive real approved snapshot and legacy behavior.

## Work Items

- [x] Implement only assigned capability and document compatibility.
- [x] Complete meaningful required checks and regression/negative evidence.
- [x] Publish mirrored branch/report and return review, then stop.

## Interfaces / Contracts

Use canonical ARCH075 frozen decisions. Shared owns ordered schema/digest and existing perpart media exports; Database owns durable child/status identity; Background owns provider/current authorization and logical aggregation. Never duplicate validators or fabricate product/provider identity.

## Dependencies

ARCH-075-BACKGROUND-001
ARCH-075-SHARED-004
ARCH-075-ADMIN-001

## Enables

Only dependent tasks after architect acceptance; never begin them implicitly.

## Acceptance Criteria

- [x] Assigned bounded capability and frozen contract behavior satisfied.
- [x] Legacy reads/records remain compatible; no unauthorized cross-owner/billing/security change.
- [x] Durable/contract identity and fault cases satisfy required checks without silent fallback.
- [x] Canonical dedicated mirrored worktree, synchronization and recursive evidence recorded; no private proof committed.

## Validation

- [x] Actual AI Free/normal admission→full composition→engine→mockMeta2/3 ordered calls; HUMAN/no-product/notices + missingmedia/longcaption/author bytes and everyfooter.
- [x] Real PG original receipts/moderation/fullmanifest/partial/unknown/takeover/restart plus existing single-send/caption read-model tests.
- [x] Types/scoped lint/build/exact-head CI and no real production sends.
- [x] Diff/privacy hygiene and report actual results, no production sends or secrets.

## Stop Condition

After required work and validation, set review, submit Completion Report and STOP. No main merge/deploy or enabled task execution.

## Implementation Notes

Accepted compatible engine merged at `02e624478fbaf4f4d2c755bfa88e86d4a1a4154c`; launcher implementation must incorporate that main source. Admin001 accepted source merged `73831bb661731bc6d7dd478475ea7acad1ffc4dd`, public Shared5.13.9 actual bytes verified. Root retains producer merge/deployment gate until engine Live/healthy and predecessor drain proof in BOTH environments; implementation may proceed in isolation while that operational proof is pending.

You are not alone. Preserve others' edits and canonical prepared isolation. Root owns final merges/deployment. Architecture constants resolve inter-agent assumptions; report genuine gaps before expanding scope.

## Completion Report

### Status

Ready for Review. Implementation and required validation completed; source committed/pushed `7652253ed2eba273b8e60297756344e15c25ed7b`, draft PR https://github.com/kodjobaah/moda-interact-background/pull/213. Both exact-head CI runs passed: [push43363446451](https://github.com/kodjobaah/moda-interact-background/actions/runs/43363446451)2m43s and [PR43363456590](https://github.com/kodjobaah/moda-interact-background/actions/runs/43363456590)2m00s. Final complete unit suite:382files/4154tests passed. Awaiting moda_architect review. This report does not claim architect review acceptance, activation or production sends.

### Files Changed

- `recovery-multipart/composition.ts` and `preparation.ts`: consume one selected Admin SHARED common revision through published renderer; exact header/body/footer boundaries; verified optional logo and separate first selected product media; bounded two/three-part or complete-text fallback; original persisted HUMAN preparation.
- Conversation wrapper service/contracts/AI adapter/application identity and repository: new common authority, trusted saved website, custom-frame provenance and immutable replay; malformed active SHARED refuses instead of falling through an audience override.
- Conversation processor/outbound admission/delivery and HUMAN preparation/dispatcher: one existing logical reservation and truthful pending outcome; original revision/inbound and command/lease; existing moderation/rate screen; deterministic root/engine integration; 180-second bounded initial HUMAN claim.
- Existing single-send media/receipt/current-header readers: strict common TEXT envelope and legacy/brand v1|v2 header proof; current source/tenant facts at final permit; no automatic rewrite of existing frozen records.
- Existing ordered source/fence/engine: optional canonical product-context carrier bound by frozen source digest and committed only atomically with ordinal-zero provider permit; later/duplicate parts do not reapply.
- Recovery template website resolver/preparer/repository/types/new common reader and local final registration/send adapters: saved-domain website; exact canonical common values captured from the same resolver used for provider parameters; mandatory actual-registration reference/current source/current facts/parameter snapshot at final SQL permit. Approved compiled registration components/bindings are not rebuilt or mutated.
- Focused composition/Meta units and actual disposable PostgreSQL normal-Free AI processor, HUMAN producer, logo/product ordering, optional media, context atomics, notices and Meta final-race regressions.

### Work Completed

- One editable Admin SHARED source frames newly activated Meta/AI/HUMAN/common eligible notice bodies. Renderer-derived boundaries preserve exact merchant-authored middle bytes, including URLs/trailing whitespace; no regex stripping or duplicate fixed prefix. Legacy no-SHARED and already-frozen v1 paths remain compatible.
- Logo is current durable READY LOGO/SQUARE only. It occupies HEADER; verified first selected product IMAGE occupies a separate PRODUCT. Complete answer shares product caption if it fits; otherwise third ANSWER carries full text. Missing media retains complete text. Each physical part ends with the exact trusted checkout footer; no truncation or extra unplanned sends.
- Existing ordered engine retains original authority, one reservation/usage/logical cap, sender binding, DELIVERED/READ continuation and conservative partial/unknown lifecycle. AI completion logs pending while the root is incomplete. HUMAN uses genuine RENDERED/SHARED evidence and original immutable command bytes; initial claim is bounded180seconds and admitted ownership is not reacquired. Existing rate admission runs once per logical command, not per part.
- HUMAN final admission additionally compares new frozen command multipart plan/policy/original receipt byte-for-byte with the root preparation. A different syntactically valid manifest is refused before any provider permit; old v2 reader evidence without the new field stays compatible.
- Canonical presented-product context is in the frozen source and commits with the first irreversible permit, with existing original inbound/control validation. Failed/suppressed/takeover first admission cannot leave a context write; later parts and duplicate continuation do not increment it.
- Eligible AGENT notices retain one existing transport and common source proof, including restart/current-name checks. Actual AUTOMATION actor remains unchanged: its pre-existing Marketing-template requirement still refuses freeform notices; tests assert no provider call rather than bypassing policy or falsely claiming delivery parity.
- Meta preparation resolves shop.websiteUrl from the saved tenant domain. A new source's explicit common reference must validate/current-match before preparation and at final SQL admission, including current definition/locale/source and tenant name/site/checkout facts. Missing/mismatched carrier or actual parameter snapshot refuses. Legacy registration absence remains legacy; no send-time compilation or mutation of approved snapshots.
- No production provider call, replay/reset, SHARED activation, source main merge or deployment by this agent.

### Validation Results

- Canonical exact lockfile install and Prisma generation completed by root; published Shared5.13.9 and accepted Database a9b6ab852a8245dfd14447808aac288a23b113d0 unchanged from prepared base02e624478fbaf4f4d2c755bfa88e86d4a1a4154c.
- Focused new composition units8/8; affected legacy units166/166 across9files; new Meta preparation positive rerun1/1 after local-only authoring metadata was excluded from the unchanged strict published provider projection.
- Actual disposable PostgreSQL: all **67 distinct relevant cases proved passing** across the common producer/Meta/notice suite (27), existing v1 ordered engine (28), and normal-contract legacy branding compatibility (12). Combined run passed65/66; one unchanged5-second interactive-transaction timeout under concurrent full-suite contention was rerun alone and passed. The final new HUMAN conflicting-valid-manifest case also passed in that isolated2/2 run. No SQL timeout or policy was relaxed.
- Earlier meaningful regressions found and corrected: AI common application key omitted trusted-checkout digest; strict public provider projection cannot include local localeAst metadata. Fixture language was made explicitly en instead of guessing English from null. Full persisted HUMAN command is read for prepared-byte assertions; lifecycle-only fixture helper does not select those fields. No validator/policy assertion was weakened.
- Initial complete unit run:4150passed/4failed across382files. Three unchanged observability subprocess5-second timeouts passed10/10 when rerun alone after host contention. One strict module-boundary lexical guard correctly flagged Set.add; the bounded local set was replaced by array push/includes, and unchanged boundary test passed1/1. No test/timeout weakening. Final declared build passed, including both TypeScript compilers; final scoped lint passed after removing five erased unused imports. Both final exact-head CI runs passed (push43363446451, PR43363456590);382files/4154tests passed.
- Tests use synthetic recipients, disposable PostgreSQL/Redis and mock media/provider transports; no inherited live database or real Meta/Shopify requests.

Physical worktree isolation / launcher evidence:
- Primary workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-075-BACKGROUND-002`, branch `task/ARCH-075-BACKGROUND-002`.
- Implementation `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-075-BACKGROUND-002`, same branch.
- Parent/implementation remote task branch fast-forward not needed; both origin/main already current. Recursive submodule sync/update/init passed at accepted Database commit above.
- Prepared claim38886d358c3ccb5a055ff0cca6ebc55b3cbbb46e already committed/pushed; no repeat claim/startup or shared/another-task checkout switch.

### Deviations

Restricted child runtime cannot write sibling canonical worktrees. Under root's explicit instruction this agent prepared immutable task-scoped `/tmp` patches; root applied them only to the authoritative task worktree and runs tests/commit/push mechanically. Source ownership/review remains this agent's. Architect/root explicitly approved same-task local single-send common reader proof and Meta final-race carrier; no Shared/schema/actor expansion.

### Assumptions

Provider acceptance is not guaranteed visual atomic delivery. Existing engine ordering depends on durable delivery callbacks and may cancel an unattempted tail at its original deadline; UNKNOWN never authorizes a blind resend.

### Unresolved Issues

Implementation branch committed/pushed `7652253ed2eba273b8e60297756344e15c25ed7b`, PR213 above; canonical implementation worktree clean. No source/required-validation issues remain; this mirrored parent task report returns the implementation for review. Production common generation is gated by the existing SHARED activation pointer, currently absent in both environments per root's read-only evidence. Root must reverify absence immediately before source merge and keep activation withheld until BG002 Live plus old-reader drain in both environments. This report does not assert live message/layout proof.

### Architectural Concerns

Existing AUTOMATION freeform notice final policy requires verified proactive Marketing template metadata. This task preserves that policy and no-send outcome; it does not retag these notices as AGENT or expand engine actors. All eligible AGENT/HUMAN/common source paths use the same authority. Admin002 owns coordinated common/template assignment activation; all replacements must be approved before activation. No schema/public package release/new configuration/provider grant/new rate limiter was introduced. New common single-send/private receipt readers require the same no-SHARED-before-rollout staging gate; old frozen bytes are never automatically upgraded.

## Architect Review

### Review Status

Pending

### Review Notes

Pending actual implementation review.

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

None
