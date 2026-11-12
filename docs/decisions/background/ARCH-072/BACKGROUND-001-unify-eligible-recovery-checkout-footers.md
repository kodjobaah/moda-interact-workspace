---
id: ARCH-072-BACKGROUND-001
architecture_id: ARCH-072
title: Unify trusted checkout footers across eligible recovery sends
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 10
executor: codex
claimed_at: 2026-11-12T17:55:49Z
attempt: 1
depends_on: []
enables: []
created: 2026-11-12
updated: 2026-11-12
---

# Unify trusted checkout footers across eligible recovery sends

## Architecture

ARCH-072; docs/architecture/ARCH-072-unified-recovery-checkout-footers.md; coordinator moda_architect.

## Objective

Include one trusted checkout footer with a consistent divider in every eligible recovery freeform outbound, including human takeover replies and service/limit notices.

## Context

Existing recovery footer assembly is AI-only. Human wrapper preparation requires unchanged passthrough and frozen replay validates original text, so enabling the helper alone is insufficient. Terminal notice text paths additionally override prepared text with a fixed constant at send time. The user requests the checkout link on every recovery conversational message, ideally separated visually. ARCH070/071 remain completed and unchanged.

## Scope

Background-owned recovery-checkout-footer helper and conversation-wrappers/service/contracts/compose adapter as needed; recovery-conversation/human-wrapper-preparation.service.ts, human-prepared-command.service.ts and human-command-dispatcher.service.ts; outbound-whatsapp-admission/outbound-message-delivery.service.ts terminal text paths; directly related local contracts, tests and bounded send-path inventory documentation. Also include whatsapp-inbound-processing.service.ts audio/transcription fallback and conversation-turn-processor.service.ts oversized-current clarification, plus necessary outbound-whatsapp-admission.service.ts/local types signatures for explicit unfrozen-notice preparation. No unrelated modules.

## Out of Scope

Post-permit content mutation, weakened moderation/control/consent/security, invented/unbound checkout URL, provider-approved template body changes, new Shared/package release, schema migration, unrelated refactors, production replay and unsolicited sends.

## Requirements

Reuse the existing trusted tenant/customer/recovery status/lifetime/HTTPS-domain context and domain footer helper. Cover ordinary HUMAN and AI recovery replies, configured and no-slot/passthrough paths, and all known eligible recovery freeform service/handoff/limit/final notices. Inventory every recovery send class and record coverage/reasoned exception; do not silently promise universal coverage while leaving an eligible freeform path unchanged.

Use a language-neutral consistent visual divider before the trusted footer. Preserve authored/localized words and unrelated links/formatting. Canonicalize standalone exact trusted URL/footer once; repeated preparation is idempotent. Do not fabricate a current URL or select a tenant/basket from an unbound routing response. Approved initial/follow-up template bodies are immutable and already bind the approved checkout parameter; do not append freeform text or a divider to a successful template payload. STOP/consent/security/blocked paths must retain send prohibitions and must not be reengaged.

Compose the complete final body before freezing, moderation, hashing, admission/fence and media planning. The provider must receive the identical committed permit body. Both terminal freeform paths must stop replacing prepared text with the fixed unaugmented constant; initial reservation may be provisional only if existing preparation updates the full text before moderation. Existing consent/window/ownership/grant/admission and retry limits remain enforced.

Human no-wrapper augmentation needs explicit trusted evidence recognized in BOTH wrapper preparation and HumanPreparedCommand replay/fromRow validation. Preserve strict original-author content/provenance; never broadly accept arbitrary modified passthrough or weaken equality/includes checks. Use an explicit narrowly validated canonical transform/receipt, bound into existing hashes/immutable representation. Return any genuinely missing Shared/database contract before editing another owner.

Previously frozen/prepared applications and commands replay byte-identically, including the old no-divider footer form. New formatting must not invalidate legacy immutable evidence or append/re-render after final permit. No retroactive mutation of delivered content. Reject overlength safely before moderation/admission without cutting the URL; preserve full text fallback where image caption bounds require it. Missing/expired/mismatched/unsafe recovery context fails closed or follows the existing controlled no-URL policy, never fabricates a link.

Inventory-driven scope clarification: audio/transcription fallback and oversized-current clarification bypass wrappers and are eligible known-recovery freeform notices. A server-owned local recovery-only preparation flag may resolve trusted context outside transactions before prepare/moderation/fence, used only by these unfrozen notice callers and the terminal branch. Never derive the flag from user/model payload or use it to alter ordinary already-frozen AI/media/legacy bodies or final permits. Add actual-body/negative/no-post-permit regressions for these callers. Root approved this routine coverage within the existing task.

## Work Items

- [ ] Inventory actual outbound classes and implement one reusable domain footer/divider transform.
- [ ] Wire HUMAN/AI and eligible known-recovery notices before final freeze/moderation; preserve provider/committed-body identity.
- [ ] Preserve narrowly proven human passthrough and both new/legacy immutable replay validation.
- [ ] Validate coverage, security, bounds, retries and final provider text; return report.

## Interfaces / Contracts

Existing verified recovery wrapper context, local human prepared-command representation, moderation identity and outbound permit own provenance. Footer preparation is Background domain policy; no new cross-service contract is currently required. Existing Shared generic logging/codecs remain canonical; no competing logger or duplicated generic mechanism.

## Dependencies

None. Existing accepted ARCH070 footer and control/admission capabilities are already on implementation main.

## Enables

Developer merge/deploy and authorized genuine human recovery-message plus AI/notice verification after architect acceptance.

## Acceptance Criteria

- [ ] Every eligible known-recovery freeform send class has one trusted footer and divider, including ordinary human no-slot and both terminal text paths; inventory makes exceptions explicit.
- [ ] Strict authored-content provenance, moderation/admission/permit identity and all existing controls are preserved.
- [ ] Old frozen applications/commands remain byte-identical/replayable; new preparation is idempotent and tampering is rejected.
- [ ] Templates/unbound routing/STOP/consent/security paths are unchanged as required, with no fabricated URL or unauthorized sends.
- [ ] No unrelated source/schema/release changes or private payloads in committed evidence.
- [ ] Canonical launcher worktree isolation, synchronization and recursive submodule evidence recorded.

## Validation

- [ ] Meaningful prior-code red regression for human missing footer and terminal override.
- [ ] HUMAN/AI configured/unconfigured, labels/duplicate/divider/idempotence, legacy replay and tamper tests.
- [ ] Actual human preparation/freeze/moderation/fence/provider identical-body tests, author-text protection and takeover/cancellation races.
- [ ] Both terminal freeform paths and eligible notices, template nonmutation and forbidden/unbound/expired/mismatched context negatives.
- [ ] Final text/caption/Unicode limits, full fallback and exact URL preservation; no post-permit append.
- [ ] Relevant existing integration/disposable PostgreSQL tests where prepared persistence is affected, task-owned lint/typecheck and exact-head full CI.
- [ ] Diff/secret hygiene; public evidence synthetic/coarse only. No real Meta send or production write during implementation tests.

## Stop Condition

Complete owned work and required validation, set review, return report and STOP. Do not merge/deploy, send live messages, modify templates or start adjacent tasks.

## Implementation Notes

You are not alone. Preserve others' changes and use the complete prepared packet/branch. Read actual package scripts and prior relevant control/admission contracts. Root owns final source merge and authorized production verification. No new source/release task is needed merely to change this Background-owned domain footer.

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

Existing trusted recovery context supplies eligible URLs; a footer does not grant new consent or checkout authority.

### Unresolved Issues

Send-class inventory must be completed before claiming every eligible path covered.

### Architectural Concerns

Return cross-owner/provenance/persistence gaps instead of weakening protected boundaries.

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
