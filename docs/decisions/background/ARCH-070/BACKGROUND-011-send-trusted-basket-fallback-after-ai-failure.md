---
id: ARCH-070-BACKGROUND-011
architecture_id: ARCH-070
title: Send trusted basket fallback after eligible AI failure
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
claimed_at: 2026-11-14T23:54:36Z
attempt: 1
depends_on: []
enables: []
created: 2026-11-14
updated: 2026-11-14
---

# Send trusted basket fallback after eligible AI failure

## Architecture

ARCH-070; docs/architecture/ARCH-070-verified-recommendation-terminal-turn-recovery.md; moda_architect.

## Objective

Admit one deterministic saved-template basket reply after an eligible AI completion failure through the existing guarded delivery lifecycle.

## Context

User explicitly requests honest unable-to-answer wording, abandoned basket summary and existing shop/checkout template instead of silent AI technical failure. BG010 selection work remains separate and must be preserved. This fallback does not fix the failed AI selection or guarantee Meta delivery.

## Scope

Application-owned failure classification, trusted localized fallback body from current abandoned basket snapshot, existing saved common reference/rendering and outbound lifecycle admission; focused host/processor and real disposable lifecycle proof. Exact implementation seam must be confirmed from current source before execution.

## Out of Scope

LLM retries/new model calls, fabricated selections/product claims, human prose summaries, Shared changes/releases, model/provider/configuration changes, sending without consent/window/controls, manual outbound/DB flags, template activation/provider registration, main merges/live operations.

## Requirements

Use only authoritative current recovery/basket facts already available to the processor; do not reuse unverified AI prose/history/product observations as basket authority. State inability honestly in existing resolved locale, list complete basket item names/quantities and only trusted available money fields, preserve currency and avoid current stock/price/discount promises. Saved common template is sole shop/header/footer source, checkout exactly once in its canonical footer. Do not synthesize product-detail selections or label the fallback verified AI success.

Classify explicitly eligible model/provider AI completion failures (including invalid final/selection, output exhaustion and model unavailable) at the owning boundary. NEVER catch stale inbound, cancellation, lost lease, human takeover, optout, consent/window/cap/entitlement/authorization failure or unsafe/missing basket/common/checkout proof into a send. A model deadline may use fallback only if a fresh existing bounded delivery admission budget remains and current ownership is valid; never ignore aborted signal/deadline or extend a protected permit. Meta send failures are NOT AI fallback triggers; preserve existing retry/UNKNOWN/no-resend semantics.

Route through existing idempotent outbound/application identity, current common-template final fence, conversation/control rechecks, permit/usage/billing lifecycle and provider adapter. One admitted response per inbound, no double-send if AI admission or provider outcome is uncertain. STOP and checkout mandatory content never lost. If full basket body cannot fit branded caption safely, use existing canonical full TEXT fallback rather than truncate facts/footer; no guarantee of single image bubble for oversized basket. Missing trusted basket/source fails closed with explicit internal outcome, no invented details. Preserve original AI failure diagnostics and separate fallback outcome without raw customer/secrets in logs; reuse shared logging, no competing logger.

Before source execution, architect must reconcile read-only seam findings into this task; task remains Pending and unclaimed. Final source bases/syncs accepted BG010 and preserves its guards. No infrastructure/DB change expected; return concrete gaps instead of expanding.

## Work Items

- [ ] Confirm exact failure classification/composition/admission seams with architect.
- [ ] Add trusted localized basket fallback and guarded failure integration.
- [ ] Prove no duplicate/unsafe send and preserved provider retry/usage behavior.
- [ ] Return immutable source/report.

## Interfaces / Contracts

Existing Background recovery/common-layout/outbound contracts and published Shared machinery only. No new queue/database schema or generic runner policy.

## Dependencies

No blocking preparation dependency. Final integration must synchronize accepted BG010 source and approved published dependency; do not overwrite its work.

## Enables

Root-owned deployment and genuine failure fallback verification after all current delivery/Meta gates permit.

## Acceptance Criteria

- [ ] Eligible AI failure produces honest saved-common basket body and canonical checkout footer.
- [ ] Trusted facts only; missing/oversized inputs handled without fabricated claims/truncation.
- [ ] Control/consent/window/stale/authorization/cancel exclusions remain fail closed.
- [ ] Existing idempotency/permit/usage/UNKNOWN/retry behavior preserved.
- [ ] Original AI failure and distinct fallback outcome remain observable without sensitive data.

## Validation

- [ ] Focused classification/localization/body/footer/basket trust tests.
- [ ] Actual processor failure path and negatives for controls/stale/cancel/window/unsafe context.
- [ ] Disposable PG lifecycle: one fallback/usage; duplicate inbound, UNKNOWN no resend, missing common and revoked authority no send.
- [ ] Declared types/build/scoped lint and exact remote checks.

## Stop Condition

After defined checks, set Review, complete report and STOP. No actual provider/model/customer sends or main merges.

## Implementation Notes

Normal launcher dedicated mirrored sibling worktrees only when Ready. Not alone; preserve all other source/local work. Existing specialist read-only assessment supplies exact seam before execution.

## Completion Report

### Status

In Progress — immutable implementation checkpoint `6421c53b236872e3b62ecb6f847688cfdee4d3db`, draft Background PR236. Final exact-head build/lint/remote checks pending; no readiness or acceptance claim.

### Files Changed

- `src/services/ai-failure-fallback.ts`: application-owned typed failure classification, original-claim child timeout, twenty-locale honest copy, fresh recovery-linked saved basket and exact saved common reference.
- `src/services/outbound-whatsapp-admission.service.ts`: optional typed recovery callback only around generation, before existing failed-preparation cleanup.
- `src/services/conversation-turn-processor.service.ts`: tagged fallback outcome, original ownership/deadline/control/version checks, exact common reference comparison, no model language/product-context updates, distinct safe fallback diagnostics and normal send lifecycle.
- `src/services/recovery-template-preparation/recovery-template-items-summary.ts`: opt-in whole-entry snapshot summary; existing native formatter unchanged.
- `src/workers/whatsapp.worker.ts`: production fallback service and existing agent AbortSignal child-deadline wiring.
- Unit fallback/admission and disposable common-layout lifecycle tests.

### Work Completed

The same admitted message/idempotency enters normal common composition, moderation, final permit and delivery. Eligible failures never create a second reservation. Saved snapshot facts are names/quantities only, explicitly labelled; invalid/absent rows produce inability-only through the same authorized recovery/common/footer. Complete entries and an honest omitted-entry count replace unsafe slicing. Optional media failure uses the existing full canonical TEXT path. Missing or changed common authority is refused; no raw passthrough.

Generation receives an earlier child deadline (original processor claim end minus 15 seconds, intersected by the existing host cap/AbortSignal). At least ten seconds must remain before and after snapshot preparation for the existing bounded media preparation plus send allowance; no lease is renewed. Original processing version/start identity, inbound/control and final permit remain authoritative. Independent cancellation/denial/stale/expired/lost-lease paths do not recover.

Normal launcher created/reused canonical mirrored `task/ARCH-070-BACKGROUND-011` worktrees and claimed attempt1/codex in parent `18a136bb06309f4adca4de61bf5f06b5b5d01eaf`, baseline Background `2352d814b23b0259c3d38bcf2e2fff522b665db0`, recursive Database `6f42b71112efe7ac63654d55f41cd74ca569b1ae`. Exact BG010 runtime `c1e2fb0ce0e8a85d59a9850902a7f353fdfa9cde`, real-registry dependency `1b57fa8d4d46169f25ff5895ff7adee599cff4d1` and its three version-only test updates `cbcef46e60b4e2d05ca6d8492c44597baa06241f` were merged normally; no terminal factory edits or source copying.

### Validation Results

- First source build/types passed against exact approved 6.1.0 archive `302b91f5ad24353ac3052c1e8c5d456b3c90d072d64665edff579eb56eb249d5`.
- Real public-registry package/lock from BG010; clean `npm ci` succeeded. All 163 installed package files byte-equal that public archive; lock version 6.1.0 and normal registry URL verified.
- Final exact-head focused admission/processor/fallback/worker tests: **170 passed / four files** (`/tmp/bg011-exact-focused.log`). Actual callback, child timeout, original deadline, stale/control/cancel/denial/lost lease, unchanged common, unsafe basket, whole entry/locale and private-error-canary vectors included.
- Disposable PostgreSQL/Redis: **four passed, 52 intentional name-filter skips**, 15.09 seconds (`/tmp/bg011-pg-2.log`): actual processor and normal delivery freeze the same root, canonical footer and saved snapshot; one logical usage; duplicate processing and engine continuation do not resend; UNKNOWN remains frozen; missing common/revoked ownership send nothing. Existing engine, permit, schema and timeouts unchanged. Final diagnostic-only/finite-input guard changes are covered by the affected unit rerun; normal lifecycle runtime is unchanged.
- Initial unit call-shape assertion failed because an optional undefined second argument changed the old mock contract; retained original one-argument call when fallback is unconfigured. Initial PG run two failed/two passed: nullable Conversation tenant links were incorrectly required although the existing authoritative relationship is its Recovery. Corrected to require the real recovery shop/customer and reject every conflicting populated Conversation link; corresponding unit parity vector added. No policy/permit relaxation.
- Final build/scoped lint and two exact-head remote unit checks pending at this checkpoint. No broad unchanged local full-suite repeat.

### Deviations

No new Shared, database, queue, provider, model, template or rendering contract. No live/customer/model/provider calls, main merges or deployment changes. New semantic events use existing shared logging; no duplicate generic observability mechanism.

### Assumptions

Basket copy is explicitly a saved snapshot: final permit validates current recovery/control/consent/lifetime, not an unchanged basket generation. No current stock, price or total claim is made. Provider delivery is never guaranteed.

### Unresolved Issues

Genuine nonrecovery generation is unsupported by the existing `loadTurn` route and common checkout authority. No ad-hoc template/sender was invented. Missing authorization/current common still refuses. Final accepted BG010/main synchronization and remote checks remain before Review.

### Architectural Concerns

Prepared fallback is not a successful AI answer, does not fix the AI failure, and never catches send/UNKNOWN errors as new generation failures. Source/main merges and live verification remain root-owned.

## Architect Review

### Review Status

Pending

### Review Notes

Materialized definition only; read-only seam assessment pending.

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Background-owned fallback through existing guarded delivery; no Shared business policy.

### Follow-up

Reconcile exact seams and dependency before Ready.


### Ready preparation contract after exact seam review

Root authorizes independent isolated preparation now, not premature final readiness. Existing owner read-only review establishes exact seam ONLY around runAgent inside runCommerceAgentAfterAdmission before failPrepared. Use a typed generation outcome/callback; keep same admitted message and agent:conversation:version identity. Skip model detected-language/product-context/success writes, then enter existing composeAiOutbound with actual selectedCommonLayout locale and SAME commonRef, and existing sendPreparedConversation. Do not broadcatch processor, moderation/wrapper refusal, control/authorization/stale/cancel, or provider send/UNKNOWN paths.

Basket is absent from RecoveryAgentContext: read bounded trusted Conversation→CheckoutRecovery matching shop/customer/recovery and active lifetime. Choose explicitly SNAPSHOT-LABELLED saved basket wording, names/quantities only, no current stock/price/total claim. Freeze that saved snapshot/body through existing immutable preparation receipt and normal recovery identity/lifetime/control final checks. The final fence does NOT prove unchanged basket generation: do not claim atomic-current inventory/basket freshness. No new generation protocol is required for clearly historical saved-basket facts. Reuse existing checkout-item formatting with whole-entry bounds; never split/truncate a title, and use honest omitted-count when necessary. Normal mandatory footer and optout content remain intact.

For genuinely absent basket, use trusted inability-only body through an existing valid saved-language/template path; omit basket and checkout if not authorized/available. Never fabricate a recovery, basket, URL or raw unwrapped model output. Distinguish recovery vs genuinely nonrecovery capability; if no supported saved template path exists, return concrete architectural gap before implementing an ad-hoc one. Missing/unsafe mandatory common binding refuses existing guarded preparation, not raw passthrough. Meta unavailable remains observable existing provider retry/UNKNOWN behavior; never promise guaranteed physical delivery.

Eligible failures require explicit typed model-generation stage/reason classification; DENIED/STALE_TURN/CANCELLED/ownership/consent/control/window/cap failures never trigger a send. Deadline fallback requires valid fresh delivery admission under existing bounded signal/lease; no cancellation bypass or budget extension. Add actual PG same-admission duplicate/oneusage/UNKNOWN/no-send-control proofs. File ownership: generation helper/processor/fallback renderer/tests and narrowly required composition plumbing ONLY; no edits to BG010 terminal factory/native integration or Shared. Final sync accepted010 and registry checks before Review. No live operations/model/provider calls/main merges.

### Root copy and preparatory source lineage

Root exact English inability copy: “Unfortunately, I’m unable to answer your question right now. Here are the details of your abandoned basket.” Follow with trusted saved basket entries and saved common footer. No-basket variant omits the second sentence and facts, with no invented checkout. Existing locale mechanism must supply truthful equivalents, not new model translation. Root permits preparatory synchronization of exact BG010 remote task sourcec1e2fb0ce0e8a85d59a9850902a7f353fdfa9cde after normal launcher current-main preparation/claim; do not derive worktree from BG010 or copy its code. Record lineage. Final actualregistry/acceptedsource synchronization required; no need wait external Meta approvals to implement/test locally.

### Basket absence/invalidity clarification (2026-11-15)

Root explicitly requires no silent generation failure merely because basket rows are absent/invalid. When recovery ownership/lifetime, actual checkout URL and saved common reference remain valid, omit the basket sentence and all invalid/unavailable facts and produce trusted inability-only body through that SAME normal template/footer/admission path. This supersedes earlier broad wording that missing basket alone must refuse. Never invent line items, totals or checkout URLs. Missing recovery/common/checkout authority still fails closed through existing safety lifecycle; genuinely nonrecovery route is currently unsupported by loadTurn and must be reported as a gap, not invented raw-template passthrough. Do not recatch composition/send failures as fresh AI failures or create another reservation/root. Reuse the admitted idempotent reservation before cleanup and preserve provider unavailable/UNKNOWN retry visibility; physical delivery is never guaranteed.

### Model-timeout fallback reserve (root/architect clarification)

Establish an earlier AI child deadline BEFORE invoking generation, reserving a fixed bounded preparation/send allowance inside the ORIGINAL admitted claim/lease deadline. Derive child limit from the smaller existing AI cap and original remaining claim minus reserve; never renew or extend parent lease/deadline. Child-generation timeout may trigger eligible fallback while parent control/cancellation signal remains valid. Original parent deadline/abort, stale inbound, control change or lease loss never becomes eligible fallback and cannot receive a fresh budget. If remaining original budget cannot cover safe admission, explicitly skip AI/refuse under current policy rather than overrun. Tests must prove child timeout→fallback/preparation/permit within original deadline, plus expired parent/cancel/lease-lost NO send. Preserve bounded provider sending semantics and no physical-delivery guarantee.
