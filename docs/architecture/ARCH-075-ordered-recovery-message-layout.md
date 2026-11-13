---
id: ARCH-075
title: Ordered recovery logo and product message layout
status: in_progress
coordinator: moda_architect
created: 2026-11-13
updated: 2026-11-13
---

# ARCH-075: Ordered recovery logo and product message layout

## Status / Problem

In Progress. WhatsApp displays a message image before its caption; one IMAGE cannot show a separate logo above a product image. User requests shop logo/details first, product photo separately and checkout footer. Current single-provider-id ConversationMessage and HUMAN command cannot safely represent multiple provider calls. A naive extra send would lose idempotency, partial outcomes and quoted reply identity.

## Frozen Contract Decisions

- Maximum physical parts per logical response:3. Ordinals0..2, no duplicate or skipped ordinals. Roles HEADER, PRODUCT, ANSWER. Shared exports MAX_RECOVERY_DELIVERY_PARTS=3 and additive RecoveryMultipartDeliveryPlanSchema/type/digest, reusing existing perpart TEXT/IMAGE/BRAND_IMAGE validators; old exports remain unchanged.
- Shared wrapper shape: schemaVersion1, kind RECOVERY_MULTIPART, parts:[{role,plan}]. HEADER is TEXT or BRAND_IMAGE, never product IMAGE. PRODUCT is genuine product IMAGE. ANSWER is TEXT. For multiple parts HEADER first; PRODUCT follows when present; optional ANSWER last. Single ANSWER TEXT fallback may contain the whole response. No arbitrary order/duplicate roles or fake product identity.
- Typical2parts: HEADER logo image caption shop name/site/checkout footer, then PRODUCT image caption answer+checkout footer. If answer exceeds image caption: HEADER, PRODUCT caption with checkout footer, ANSWER full text+checkout footer. HUMAN/no-product: HEADER then ANSWER; missing logo uses verified text header or whole TEXT fallback, never suppresses the answer/product. All physical parts carry exact trusted checkout footer and final part ends with it. No text truncation, cover-as-logo or extra unplanned sends.
- Split only server-known trusted header/footer boundaries/receipts; preserve authored middle bytes, no regex stripping arbitrary HUMAN text/URLs/dividers. Each product component binds actual frozen verified selected product pair; no raw model image URL. Existing first-product policy need not expand to more products.

## State / Repository Ownership

Existing ConversationMessage remains ONE logical response, billing/usage/cap/history/read-model anchor. One original reservation and usage event;20 logical-response cap unchanged. Bounded fanout is layout, not extra charges/turns. Child physical outcomes aggregate using existing root status enum; no new root/API status required.

Database owns additive ConversationDeliveryPart child model: root ConversationMessage FK/cascade, unique(root,ordinal), immutable ordinal/role/payload/digest/source identity, unique local dispatch key and providerMessageId, state/timestamps/failure metadata. Ordinal check0..2 means at most3. Part states PREPARED, ADMITTED, ACKNOWLEDGED, DELIVERED, READ, FAILED, UNKNOWN, CANCELLED. Pending immutable payloads cannot be rewritten. Root/part ownership and final gates remain Background policy. Child record insertion/unique IDs and attempt CAS must survive races/restarts. No second automatic provider attempt after ADMITTED/UNKNOWN.

Database also owns minimal ConversationDeliveryStatusReceipt for normalized status-before-ACK correlation: provider message identity, bounded status/failure metadata/provider timestamp/receivedAt, unique dedupe identity, optional linked part and lookup/retention indexes. No raw webhook/customer payload. Background bounds unmatched retention (7days, bounded cleanup pages), attaches/reconciles on HTTP ACK. Duplicate/out-of-order read-before-delivered callbacks are monotonic; no status loss merely because ACK persistence is later.

Shared owns additive pure ordered plan contract/digest only; provider/database/queue orchestration stays Background. Publication separate after accepted source, tested immutable artifact and explicit public-release approval. No migration or provider call in Shared.

Background engine owns durable root/part freeze, sequential current-fenced permits, exact payload sends, ACK/status aggregation and provider-id→part→root quoted routing. A later part is admitted only after predecessor durable DELIVERED or READ; HTTP ACK alone only records acceptance and waits for delivery callback. UNKNOWN halts the tail, never blind resend. Resume only unattempted PREPARED tail under original still-valid control/tenant/consent/media/policy evidence. Partial definitive failure marks root FAILED with bounded partial reason; accepted prefix remains immutable and is not resent or wholly compensated. UNKNOWN root stays conservative PENDING/evidence, HUMAN command not SENT after header. Logical usage retained once any part accepted/uncertain; zero-accepted definitive failures retain existing safe compensation. Per-conversation ordering prevents parts from different replies interleaving; no platform-global serialization.

Root SENT only after all required physical ACKs, DELIVERED only all delivered/read, READ only all read. A root represents full logical authored reply, not an empty header placeholder. App/API existing logical projection stays usable. Status and quoted reply from any part resolve same root/tenant/recovery, with no cross-tenant fallback. Meta has no assumed server dedup guarantee; local dispatch CAS and conservative UNKNOWN policy are explicit limits, not exactly-once claims. Provider acceptance sequence is enforced; no promise of atomic multi-message display.

## Security / Moderation / Compatibility

Original AI revision/inbound or HUMAN command/lease/control identity remains authoritative. HUMAN new customer inbound alone does not invent a new gate. Every part checks STOP/consent/current control/tenant/source/policy; takeover cancels unsent tail, never recaptures newer ownership. No HTTP in transactions. Moderation binds frozen complete visible text/plan manifest and each admitted part derivation; no unmoderated authored text. Each image preserves existing verified provenance and caption limits.

Legacy raw TEXT/product IMAGE/BRAND_IMAGE and frozen commands remain exact single sends. Approved initial/follow-up Meta templates unchanged. AI/HUMAN recovery replies and eligible notices use the new composition path; unbound/security exclusions unchanged. No new permission/credential, billing policy or provider-image source.

## Infrastructure / Observability / Scale

No new service or Gateway topology. Reuse existing Background queue/worker and shared logger. Domain part outcomes add necessary ordinal/root/partial/unknown meaning, not duplicate generic HTTP/BullMQ telemetry. Metrics/logs do not emit message bodies/provider secrets. Bound max3 physical requests and existing provider rate fence; do not multiply usage charges. No new unbounded retry or status-receipt accumulation.

## Tasks / Rollout

| Task | Owner | State | Dependencies |
|---|---|---|---|
| ARCH-075-DATABASE-001 | moda_database | Complete | None |
| ARCH-075-SHARED-001 | moda_shared | Complete | None |
| ARCH-075-SHARED-002 | moda_shared | Complete | ARCH-075-SHARED-001 |
| ARCH-075-BACKGROUND-001 | moda_background | Complete | ARCH-075-DATABASE-001, ARCH-075-SHARED-002 |
| ARCH-075-BACKGROUND-002 | moda_background | Pending | ARCH-075-BACKGROUND-001 |
| ARCH-075-SYSTEM-TEST-001 | moda_system_test | Pending | All implementation/publication tasks |

PRODUCTION / COMPATIBLE ROLLOUT. Additive database migration first, accepted Shared public release, Background engine then producer integration; developer deploys/drains old readers before emitting new manifests. No production replay/reset/extra test send without authorization. New format cannot roll back to old readers blindly; stop generation/drain new pending work first, preserve all outcome records. Source tasks never depend on system test. Developer manual checkpoint precedes Ready terminal system-test invocation. Architecture Implemented only after accepted terminal validation and genuine ordered WhatsApp proof with explicit partial/unknown behavior evidence. Public documentation excludes customer/provider identifiers and URLs.

- Ordering clarification: durable DELIVERED/READ, not mere HTTP ACK, gates the next physical part. Continuation is asynchronous through existing worker/repair queues; never hold locks or a worker awaiting callbacks for minutes. Capture immutable delivery deadlineAt, use an explicitly bounded validated runtime policy, cancel only unadmitted tail on deadline without resending predecessor. This is a requirement-based visual ordering guard, not a claim Meta guarantees atomic display. Database includes indexed deadlineAt for bounded pending-tail scans; the server-owned internal policy defaults to 120 seconds from freeze and validates 30–300 seconds. Repair cadence is 5 seconds with indexed batches of at most 100; status/ACK reconciliation schedules immediate continuation where the existing queue allows. No new external configuration surface is introduced.

- Sender isolation amendment: physical parts and normalized status receipts freeze providerAccountId and providerPhoneNumberId as bounded server-resolved scalar identity. Dedupe/correlation includes both plus MetaID/status/provider timestamp. Status or quote from foreign sender cannot attach merely by providerMessageId. Background compares inbound verified account/phone to part before logical-root tenant resolution; old single-message paths remain unchanged.

- Runtime identity amendment: use the same credential snapshot for expected sender validation and actual endpoint/token selection; rotation mismatches refuse before HTTP. Frozen-sender child quote lookup precedes the current-global sender check. Known old-sender quotes may resolve their existing root, but new replies require a currently legitimate matching sender, never silent rotation. Continuation validates original AI inbound/control against current durable state without requiring the released processing lease; HUMAN retains original command/control semantics. Route multipart commands outside legacy single-send expired-permit reconciliation.

## Common Content Scope Amendment

User explicitly extends scope to all Meta templates, AI and HUMAN messages. ONE Admin-owned immutable SHARED wrapper definition/slot/locale projection is content authority, not a new table/setting or parallel hardcoded frame. Name/verified website/divider header and divider/trusted checkout footer surround family-specific body. Logo remains verified separate media; never cover-as-logo. Audience-specific body text and native opt-out content are preserved without adding a second frame. Admin freezes selected common revision into replacement Meta locale authoring JSON; existing registration snapshots remain unchanged. Coordinated activation waits for all required replacement locales to be approved. Freeform product tails remain prohibited outside the valid customer-service window; no unreviewed provider-template multipart contract is introduced.

Genuine binding gap: canonical Shared keys lack shop.websiteUrl. Shared003 adds that semantic key to existing template/wrapper validators and public types only; Shared004 publishes the tested artifact after explicit approval. Existing renderer/token contracts are reused. No new reusable frame builder is needed because the saved common projection is authority.

| Task | Owner | State | Dependencies |
|---|---|---|---|
| ARCH-075-SHARED-003 | moda_shared | Complete | ARCH-075-SHARED-002 |
| ARCH-075-SHARED-004 | moda_shared | Complete | ARCH-075-SHARED-003 |

Background001 preserves existing5.13.8 engine work but final reader support consumes published5.13.9 under the reader-first staging correction below. Background002 and Admin consumer definitions will depend on Shared004 and reference this same common projection; terminal system validation includes Meta and dynamic parity. No source implementation is authorized by this amendment outside canonical assigned tasks.

Common reference contract owner Shared003: exact schemaVersion1/definitionId/sourceHash/localeId/languageTag/contentHash/prepared (existing PreparedWrapper), strict browser-safe parser reusing existing injected-digest projection verification. Admin freezes this ref in new Meta source JSON; Background verifies active SHARED definition/source/locale hash against it. Snapshot validation alone is not authority. New Meta compiler projects common header into BODY prefix, original authored body and preserved native opt-out footer text next, then common checkout conditional as BODY suffix; native FOOTER empty. Existing initial authored Reply-tail semantics stay unchanged; final compiled limits are checked after frame insertion. Duplicate inline checkout needs explicit review, not regex deletion.

## Common-layout consumer tasks

| Task | Owner | State | Dependencies |
|---|---|---|---|
| ARCH-075-ADMIN-001 | moda_admin | Complete | ARCH-075-SHARED-004 |
| ARCH-075-ADMIN-002 | moda_admin | Pending | ARCH-075-ADMIN-001, ARCH-075-BACKGROUND-002 |

Background002 additionally depends on Shared004 and Admin001. It replaces fixed-prefix decoration for new replies with additive local receiptv2 binding the actual rendered common reference/header/footer and trusted split boundaries; v1 frozen replay remains unchanged. Admin002 coordinates approved global SHARED revision with per-shop Meta assignment safely; actual transaction gap must be returned before unsafe mixed-version activation. All required replacements approved before activation, and consumer deployed first. Terminal system-test additionally depends on Admin001/Admin002/Shared003/Shared004; no implementation depends on system-test.
Reader-first staging correction: Background001 must understand local receiptv2/commonRef and custom rendered header/footer boundaries BEFORE new producers emit them. It now consumes published Shared0045.13.9 for final reader support; Background002 remains producer composition only. Existing engine work on5.13.8 stays preserved, but no unpublished consumer artifact or new-format activation is allowed. Final exact-head engine validation/rollout follows the published dependency. This prevents an older v1-only reader from aborting new-format tails during producer overlap.
