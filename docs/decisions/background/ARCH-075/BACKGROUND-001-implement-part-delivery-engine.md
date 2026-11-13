---
id: ARCH-075-BACKGROUND-001
architecture_id: ARCH-075
title: Implement durable ordered physical delivery lifecycle
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
claimed_at: 2026-11-13T01:07:59Z
attempt: 1
depends_on:
  - ARCH-075-DATABASE-001
  - ARCH-075-SHARED-002
  - ARCH-075-SHARED-004
enables: []
created: 2026-11-13
updated: 2026-11-13
---

# Implement durable ordered physical delivery lifecycle

## Architecture

ARCH-075; docs/architecture/ARCH-075-ordered-recovery-message-layout.md; coordinator moda_architect. Read all frozen contract constants and lifecycle decisions before implementation.

## Objective

Implement durable ordered physical delivery lifecycle.

## Context

User requests logo/shop details before a distinct product image and checkout footer. Existing single-provider-id response cannot safely loop multiple sends. This task owns one bounded prerequisite capability; preserve completed prior behavior.

## Scope

Adopt accepted database submodule and exact published Shared package; owning part freeze/permit/dispatch/ACK/status/reply lookup/reconciliation engine with deterministic tests, no live producer activation.

## Out of Scope

Other repositories/tasks, source main merges/deployment, production sends/replays/resets, billing/usage/cap changes, provider credentials/permissions, unsupported exactly-once assumptions, unbounded fanout/retries, unrelated refactors. Return actual cross-owner gaps.

## Requirements

Implement canonical root logical/perpart physical lifecycle. Atomic immutable manifest/part creation, unique stable identities, perpart same-tenant original control/consent/media/policy checks and no HTTP TX. Admit later part only after durable predecessor DELIVERED/READ; HTTP ACK waits for callback, never synchronously holds a worker/transaction. Immutable deadlineAt from bounded validated policy cancels unadmitted tail via asynchronous queue/repair continuation without resend; one automatic HTTP attempt after ADMITTED, UNKNOWN halts tail and never resends accepted prefix. Recover only PREPARED unattempted tail under original still-valid authority. Persist each MetaID, reconcile status-beforeACK receipt, monotonic duplicate/read-before-delivered aggregation, bounded7day receipt cleanup. Any quoted part resolves exact logical root/recovery safely. RootSENT onlyallACK, DELIVERED onlyall appropriate, READ onlyallREAD; definitive tail fail rootFAILED/partial reason, unknown conservativePENDING. HUMAN command notSENT afterheader. One logical usage/cap admission; retain original usage if prefixaccepted/unknown, no blanket compensation. Preserve old single-plan paths and current sender rate fence. Return any actual App/API projection gap rather than silently changing readers.

### Sender-bound provider correlation

Freeze actual server-selected providerAccountId/providerPhoneNumberId on every physical part. Normalized callback and quote must match both before attaching status/provider IDs or mapping root/recovery. Unknown sender events are not authority to claim a part with the same MetaID. Unmatched receipt dedupe/retention uses these IDs; existing single-message compatibility is preserved.

Runtime policy: server-owned default 120-second deadline from freeze, validated bounds 30–300 seconds; indexed repair batches at most 100 on 5-second cadence, plus immediate status/ACK continuation where supported. No new external configuration. Sender validation must use the same credential snapshot as the HTTP endpoint/token; optional server-only expected sender input leaves legacy callers unchanged. Frozen-sender child quote lookup occurs before current-global checks; old-sender root resolution cannot silently authorize a reply through a rotated sender. Continuation checks original AI inbound/control against current state without retaining the original processing lease; HUMAN admission remains original command/control based. Multipart commands must not fall into legacy single-send expired-permit reconciliation.

### Reader-first common layout compatibility

Scope now includes additive receiptv2/commonRef/custom-boundary READER and final verification support before engine rollout. Producers remain disabled here. Existing v1 frozen parser uses fixed header/footer helpers and cannot interpret future v2, so accepting a v1-only engine would permit producer-rollout overlap to cancel/drop legitimate new tails. Consume actual published Shared0045.13.9 parser, never sibling source or unpublished tarball. Until that dependency completes preserve ongoing legacy engine work/tests and design v2 read-only; do not claim final checks/rollout readiness.

Readerv2 binds canonical commonRef, actual rendered header/footer/trusted boundaries and original tenant/control/source/policy evidence; re-read active immutable SHARED source/locale hashes and existing current saved identity facts. No hardcoded prefix added over custom common content. Legacyv1 exact bytes remain readable. Status/ACK outcome persistence must retain real provider evidence even if full source becomes unavailable; invalid/unknown preparation never grants a fresh send or cancels arbitrary foreign work. HUMAN original admission/new-inbound policy unchanged. Final engine exact-head tests include mixedv1/v2 readers, custom boundaries, stale/tampered reference, callbacks/ACK race and no producer activation.

### Private v2 boundary receipt

Keep old receiptv1 exact. New Background-local recoveryShopHeader union member is strict `{schemaVersion:2,kind:RECOVERY_COMMON_LAYOUT,shopId,commonRef,variables:{shop.name,shop.websiteUrl,checkout.url},boundaries:{header,body,footer}}`; public commonRef remains Shared schemaVersion1. Original actor/control/source/policy receipt remains separate. Complete root equals header+body+footer and exact existing renderPreparedWrapper(commonRef.prepared, trusted variables, body). Derive canonical header/footer by a collision-checked internal response marker through the same existing renderer; marker never sent, exactly one split required, no arbitrary authored substring stripping or parallel formatter. Re-read current immutable SHARED definition/source/locale hashes and saved identity/checkout facts before admission.

Freeze variables from existing owning verified identity helper: valid sanitized saved name, else exact verified saved-domain hostname (explicit domain fallback, no invented brand name); normalized saved-domain website and existing trusted checkout resolver. Recompute identically on final validation. Unsafe/missing website cannot authorize v2. Strict bounds and original moderation/source identity remain; HUMAN new inbound alone does not invent a refusal gate. Final tests prove custom common header/footer, source/ref/fact tampering and v1 replay compatibility.

### HUMAN v2 evidence and physical derivation

Extend the existing genuine RENDERED/audienceSHARED prepared-evidence branch with local recoveryShopHeader v1|v2, not PASSTHROUGH/NOT_CONFIGURED when the common slot is configured. Definition/locale/contentHash must match commonRef and actual selected slotEditVersion. Explicitly version the v2 application-key inputs binding original command, full commonRef/variables/boundaries; preserve old v1 key algorithm exactly. Parse/fromRow/currentHumanWrapperMatches read and verify v2 before rollout. Frozen root source must exactly match command v2 evidence; no caller metadata omission bypass. For this body-only common layout HUMAN boundaries.body equals original command.textBody exactly. Preserve current HUMAN admission policy on newer inbound.

Only server-proven boundaries derive physical payloads: HEADER=header+footer; final PRODUCT/ANSWER=body+footer; optional middle PRODUCT=footer; single ANSWER=full root. Keep renderer separators byte-exact, never regex-strip authored text. Validate actual provider outcome persistence independently of current source parse, without granting another send.

## Work Items

- [x] Implement only assigned capability and document compatibility.
- [x] Complete meaningful required checks and regression/negative evidence.
- [x] Publish mirrored branch/report and return review, then stop.

## Interfaces / Contracts

Use canonical ARCH075 frozen decisions. Shared owns ordered schema/digest and existing perpart media exports; Database owns durable child/status identity; Background owns provider/current authorization and logical aggregation. Never duplicate validators or fabricate product/provider identity.

## Dependencies

ARCH-075-DATABASE-001
ARCH-075-SHARED-002

## Enables

Only dependent tasks after architect acceptance; never begin them implicitly.

## Acceptance Criteria

- [x] Assigned bounded capability and frozen contract behavior satisfied.
- [x] Legacy reads/records remain compatible; no unauthorized cross-owner/billing/security change.
- [x] Durable/contract identity and fault cases satisfy required checks without silent fallback.
- [x] Canonical dedicated mirrored worktree, synchronization and recursive evidence recorded; no private proof committed.

## Validation

- [x] Real PostgreSQL concurrent root/part creation, perpart CAS, crash-before/after permit/ACK, unknown halting, tail resume/control/STOP cancellation, prefix preservation and logical usage tests.
- [x] Status-beforeACK, duplicate/out-of-order/read-before-delivered, root aggregation and quoted anypart tenant tests.
- [x] Legacy single-send/reconciliation, package integrity/install, types/scoped lint/build and exact-head full CI.
- [x] Diff/privacy hygiene and report actual results, no production sends or secrets.

## Stop Condition

After required work and validation, set review, submit Completion Report and STOP. No main merge/deploy or enabled task execution.

## Implementation Notes

Accepted Database source merged at `a9b6ab852a8245dfd14447808aac288a23b113d0`; update the task-owned nested database gitlink to that exact source and generate Prisma. Preserve current5.13.8 engine work; final reader integration consumes published Shared5.13.9 from canonical public registry after Shared004 acceptance, verifying installed integrity. This task must wire active queue/repair/status/quote readers and continuation lifecycle in deployed entrypoints, not leave an unused engine. It must not enable new producer manifests; Background002 does that only after engine rollout and old-reader drain proof. Root requires engine Live/healthy evidence in both environments before producer merge.

You are not alone. Preserve others' edits and canonical prepared isolation. Root owns final merges/deployment. Architecture constants resolve inter-agent assumptions; report genuine gaps before expanding scope.

## Completion Report

### Status

Ready for Review. Implementation, required validation and both corrected exact-head CI runs passed. Awaiting moda_architect review; this report does not claim architect acceptance or production rollout.

### Files Changed

- Adopt accepted nested Database commit `a9b6ab852a8245dfd14447808aac288a23b113d0` and exact public Shared `5.13.9` with matching lockfile and consumer version assertions.
- `src/services/recovery-multipart/{frozen,common-layout,fence,engine,quote,runtime}.ts`: bounded immutable preparation, published contract readers, original authority, physical permits/outcomes, continuation and correlation.
- Existing recovery final fence and HUMAN preparation/dispatcher readers: per-part policy reuse, true common-layout RENDERED evidence, legacy reconciliation exclusion and safe crash-gap deferral.
- Messaging worker/entrypoint and both routing readers: active continuation/repair/status integration and sender-bound quote handling.
- WhatsApp transport types/service: optional server-only expected sender validated against the same credential snapshot used for HTTP.
- Existing trusted wrapper URL resolver export; no formatter/content definition duplicated.
- Owned unit/PostgreSQL fixtures and regressions; existing legacy routing unit isolation and installed-package assertions.

### Work Completed

- One logical message/reservation with at most three immutable physical parts; deterministic per-part identities and deterministic HUMAN root identity. Duplicate freeze/admission cannot issue another provider attempt or replace frozen bytes.
- Every send goes through the existing Shop/Conversation current tenant/control, window, STOP, consent, entitlement/usage, moderation and media/policy final fence. Later parts require durable predecessor DELIVERED/READ; ACK alone waits asynchronously.
- Original AI inbound/control and HUMAN command/control/lease authority survive released processor leases. A new HUMAN customer inbound does not add an AI version gate. Admitted groups are excluded from legacy expired single-send reconciliation.
- Default deadline120s, validated30–300s, repair batch<=100 on5s cadence. Deadline cancels only unadmitted tails; ADMITTED/UNKNOWN never returns to an automatic transport attempt. Missing/in-progress exact moderation may wait only within that original deadline; no send without the final exact ALLOW record.
- Sender-bound normalized status receipts reconcile before/after ACK, including commit-order races, duplicate/out-of-order/read-before-delivered and late original ACK after expiry. Immutable part/root outcome provenance retains real provider evidence after source corruption/current authorization changes; this never grants another send.
- Logical SENT only all ACK; DELIVERED/READ only complete corresponding physical evidence. Partial definitive failures retain accepted prefix; UNKNOWN remains conservative. Known-zero-accepted automated failure releases only its exact unused logical usage; accepted/uncertain prefix is retained. Delivered usage records once per logical root.
- Quotes from any accepted physical part resolve their logical root without inventing root sentAt. Frozen sender IDs and real ACK timestamps are required. Foreign/current-rotation identities cannot cause guidance or a new reply through a different sender.
- Published5.13.9 commonRef validation supports additive v2 receipt with exact renderer-derived boundaries/trusted variables and fresh locked SHARED definition/source/locale/facts checks. Legacy v1 and old single TEXT/product IMAGE/BRAND_IMAGE records remain readable without rewriting.
- HUMAN v2 uses true RENDERED/SHARED evidence, explicitly versioned application identity and byte-exact original authored body. No fake NOT_CONFIGURED or legacy flattening; absent-root crash gaps use existing prepermit claim defer/backoff and preserve frozen evidence for the owning producer to resume.
- HUMAN v2 resume runs the existing exact-body moderation assessment/retry/block flow before delegating to ordered transport; a producer crash before assessment cannot leave the reader waiting without creating the required assessment. Frozen evidence and original authority remain unchanged.
- A copied envelope from another logical root is refused at the actual selected root before any source-derived cleanup; only that root can be cancelled.
- Producer generation remains disabled. No Meta source compilation, template activation, production send/replay/reset or merge was performed by this agent.

### Validation Results

- Public Shared `5.13.9` registry installation and lock integrity verified in the canonical worktree: `sha512-bLXw6dofV8bq/TJzE8STzk9/jT0WSHM5R01x4d1Ki+xVQ+VAfVg63+hzewXas5KYjUMtBOMxBX60gtB4U/uVfg==`. No sibling-source or file dependency.
- Focused units: 91/91 passed across five files, then final root-binding guard focused units 30/30 passed (root-executed canonical validation).
- PostgreSQL: **35/35 passed across both owned integration files (174 seconds)**. Includes actual normal Free billing admission, current SQL fence, concurrency/unknown/partial outcomes, sender correlation, v1/v2, custom common source and HUMAN crash-gap cases. Earlier fixture-only failures were corrected with valid synthetic phone/native consent observations, proper source confirmation, valid recovery closure instead of prohibited unlink, and locale-before-definition cleanup; no production policy guard or assertion was relaxed.
- Typecheck: passed; declared `npm run build` passed (exit 0), including Prisma generation and both TypeScript builds.
- Full unit suite: **4,142/4,142 passed across 381 files (229.84 seconds)** before the final one-line root-binding guard. After that guard: **28/28 engine PostgreSQL cases, 30/30 focused units, typecheck and changed-file lint passed**. The earlier combined 35 PostgreSQL cases include the unchanged common-layout cases. Declared build and changed-file lint passed. Both exact-head `18ede9eca6b599974c55ca0143818df142499b8b` CI runs passed (push 2m5s, PR 2m29s). Final bounded HUMAN moderation-resume correction: **9/9 common-layout PostgreSQL cases, 160/160 affected HUMAN units, typecheck and changed-file lint passed**. Corrected source head is `d41f1764dd274b343f4c56013a7531cf46fd4662`; both exact-head CI runs passed: [push43357237420](https://github.com/kodjobaah/moda-interact-background/actions/runs/43357237420) (2m12s) and [PR43357241653](https://github.com/kodjobaah/moda-interact-background/actions/runs/43357241653) (1m41s).
- No live database/Redis/provider was used for tests. PostgreSQL tests are guarded disposable integration runs with synthetic recipients and mock transports.

Physical worktree isolation (launcher evidence):
- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-075-BACKGROUND-001`, branch `task/ARCH-075-BACKGROUND-001`.
- Implementation: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-075-BACKGROUND-001`, same branch.
- Shared/default/another task checkout switched or used for implementation: no.
- Parent remote task fast-forward: not needed; parent main incorporated: yes. Implementation remote task fast-forward: not needed; implementation main: already current.
- Recursive submodule sync/update/init passed at launcher preparation, recorded Database base `5329d5390d346042895219663f3a040ea54ae168`; task explicitly advances it to accepted Database source above.
- Claim already prepared/pushed `c423f670492f6e9bb5ec73b47470c66afb531436`; no repeated claim.

### Deviations

The child runtime retained restricted write access to sibling canonical worktrees. With root's explicit direction, this agent prepared task-scoped patches under `/tmp`; root applied them only in the authoritative task worktree and executed validation/publication mechanically. No alternate implementation checkout was used. Source/review ownership remained with this agent. Public9/common v2 reader scope was explicitly amended by the architect during the existing claim; dependency completed before consuming its published exports.

### Assumptions

Provider acceptance is not exactly-once delivery. A committed ambiguous transport attempt is never blindly resent. Public reference snapshots are validation inputs, never current authorization by themselves.

### Unresolved Issues

No implementation or required-validation issues remain. Source commit `d41f1764dd274b343f4c56013a7531cf46fd4662` is pushed on `task/ARCH-075-BACKGROUND-001`; draft implementation PR: https://github.com/kodjobaah/moda-interact-background/pull/212. Canonical implementation worktree is clean. Parent review-report publication is on the same mirrored task branch. Production rollout/genuine ordered-message verification belongs to root after review and dependent producer/common-source tasks; it is not asserted by this engine-only report.

### Architectural Concerns

No Background-owned schema/queue ingress contract, merchant charge/cap, credential, provider permission or global infrastructure change. The declared nested Database dependency is adopted without editing its schema/migrations. ExistingJSON stores private frozen transport/receipt data. Matched provider facts are retained; unmatched receipt cleanup is bounded7days/100rows using the accepted partial index. New producers must use the same deterministic HUMAN root helper and original frozen authority. Old single-send records are not upgraded automatically. Rollback requires stopping new generation and preserving/draining new groups; old readers cannot safely interpret new manifests.

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
