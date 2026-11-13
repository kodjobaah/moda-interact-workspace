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

Legacy raw TEXT/product IMAGE/BRAND_IMAGE and frozen commands remain exact single sends. Existing approved initial/follow-up Meta snapshots remain immutable; reviewed common-layout replacements are cloned/approved under the common-content amendment. AI/HUMAN recovery replies and eligible notices use the new composition path; unbound/security exclusions unchanged. No new permission/credential, billing policy or provider-image source.

## Infrastructure / Observability / Scale

No new service or Gateway topology. Reuse existing Background queue/worker and shared logger. Domain part outcomes add necessary ordinal/root/partial/unknown meaning, not duplicate generic HTTP/BullMQ telemetry. Metrics/logs do not emit message bodies/provider secrets. Bound max3 physical requests and existing provider rate fence; do not multiply usage charges. No new unbounded retry or status-receipt accumulation.

## Tasks / Rollout

| Task | Owner | State | Dependencies |
|---|---|---|---|
| ARCH-075-DATABASE-001 | moda_database | Complete | None |
| ARCH-075-SHARED-001 | moda_shared | Complete | None |
| ARCH-075-SHARED-002 | moda_shared | Complete | ARCH-075-SHARED-001 |
| ARCH-075-BACKGROUND-001 | moda_background | Complete | ARCH-075-DATABASE-001, ARCH-075-SHARED-002, ARCH-075-SHARED-004 |
| ARCH-075-BACKGROUND-002 | moda_background | Complete | ARCH-075-BACKGROUND-001, ARCH-075-SHARED-004, ARCH-075-ADMIN-001 |
| ARCH-075-SYSTEM-TEST-001 | moda_system_test | Complete | All implementation/publication tasks |

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
| ARCH-075-ADMIN-002 | moda_admin | Complete | ARCH-075-ADMIN-001, ARCH-075-BACKGROUND-002 |

Background002 additionally depends on Shared004 and Admin001. It replaces fixed-prefix decoration for new replies with additive local receiptv2 binding the actual rendered common reference/header/footer and trusted split boundaries; v1 frozen replay remains unchanged. Admin002 coordinates approved global SHARED revision with per-shop Meta assignment safely; actual transaction gap must be returned before unsafe mixed-version activation. All required replacements approved before activation, and consumer deployed first. Terminal system-test additionally depends on Admin001/Admin002/Shared003/Shared004; no implementation depends on system-test.
Reader-first staging correction: Background001 must understand local receiptv2/commonRef and custom rendered header/footer boundaries BEFORE new producers emit them. It now consumes published Shared0045.13.9 for final reader support; Background002 remains producer composition only. Existing engine work on5.13.8 stays preserved, but no unpublished consumer artifact or new-format activation is allowed. Final exact-head engine validation/rollout follows the published dependency. This prevents an older v1-only reader from aborting new-format tails during producer overlap.

Single-send notice staging exception: Background002 adds privatev2 common singleTEXT/BRAND_MEDIA readers with producers while preserving AUTOMATION and existing final fences. This is safe only under root-verified absence of SHARED active slot in both environments; reverify immediately before producer merge. Keep SHARED unactivated until Background002 Live plus predecessor reader drain in BOTH environments, then root-owned Admin002 coordination. No new format emits without eligible SHARED common mode. If absence changes, stop and stage compatible readers separately. No new setting/schema/actor permission is introduced.

## Compatible reader rollout evidence

Root verified accepted compatible-engine source02e62447 Live with healthy runtime in both environments using supplied deployment/runtime evidence. Predecessor termination is a documented-platform inference rather than a claimed observed stopped line: Render applies the sequence to background workers and force-terminates predecessors after its bounded shutdown interval; the conservative interval had elapsed with successful current deployments. No rollback/custom support override was evidenced, and no Redis or restricted Render-origin workaround was used. Source: [Render deployment lifecycle](https://render.com/docs/deploys). This satisfies the reader-stage rollout gate; root must still reverify no active SHARED slot before producer merge and wait for producer Live/drain before common activation. Actual Meta approval, catalogue copy and genuine ordered messages remain pending.

### Coordinated activation transaction refinement

Admin inspection established that existing per-definition/per-shop publication cannot atomically switch a global common pointer. Admin002 therefore uses an existing-JSON versioned coordinator and a single bounded serializable activation transaction covering the entire affected selectable cohort, assignments and SHARED CAS/audit. Bounds are six scenario definitions, 50 shops, 1,000 replacement targets and 1,000 existing affected variants, and a 1 MiB snapshot. Overflow refuses; this is not a measured scalability claim. Ordinary assignment/common-pointer writers participate in the shared fence or equivalent verified conflicts. Historical audience slots remain intact because accepted Background common-mode precedence is explicit. No new schema, external provider action or partial activation is introduced.

### Translation website parity correction

Actual common-source translation revealed Admin protected-segment validation omitted the canonical shop.websiteUrl binding. Admin003 owns the narrow producer correction; Background003 verifies actual existing generic marker codec roundtrip without speculative runtime changes. Both are Ready on accepted dependencies. No schema or Shared release is required. System validation additionally depends on both accepted corrections; architecture remains In Progress.

| ARCH-075-ADMIN-003 | moda_admin | Complete | ARCH-075-ADMIN-002, ARCH-075-SHARED-004 |
| ARCH-075-BACKGROUND-003 | moda_background | Complete | ARCH-075-BACKGROUND-002, ARCH-075-SHARED-004 |

### Reviewed common editor lifecycle parity

Admin004 corrects new editable empty static footer production and selector/eligibility staging status parity, preserving all immutable saved AST/compiler/hash bytes and strict 20-locale proof. A genuine cloned source is required for existing noncanonical empty-token footer. No Shared release, database status rewrite or Background runtime change. Terminal system acceptance additionally requires Admin004; independent unaffected fixtures may continue, but no architecture completion claim is made.

| ARCH-075-ADMIN-004 | moda_admin | Complete | ARCH-075-ADMIN-003, ARCH-075-SHARED-004 |

### Explicit localized opt-out parity

Actual translated customer instructions use exact STOPP, DUR, PARAR and STOPPA. Background004 owns matching those whole commands through the unchanged durable consent path; no substring/NLP or new provider policy. Hold affected live approvals until corrected runtime is deployed. This is a terminal acceptance prerequisite without resetting existing independent system-test work. Architecture remains In Progress.

| ARCH-075-BACKGROUND-004 | moda_background | Complete | ARCH-075-BACKGROUND-003, ARCH-075-SHARED-004 |

### Confirmed Meta submission readiness corrections

Admin005 moves explicit English Meta review to the existing all20 submission confirmation, before provider intent, preserving snapshots and wrapper lifecycle. Background005 provides audited bounded operator recovery only for proven missing-app preclaim BLOCKED rows; no uncertain/provider-created state may reset. Gateway001 declares server-owned META_APP_ID sync:false on the actual test/production messaging workers; no app ID/secret is committed. Tasks are independent; live recovery requires repaired configuration, reviewed source and accepted recovery method. No Shared/schema change. System completion additionally requires these accepted corrections, preserving prior independent proof and claim. Architecture remains In Progress.

| ARCH-075-ADMIN-005 | moda_admin | Complete | ARCH-075-ADMIN-004 |
| ARCH-075-BACKGROUND-005 | moda_background | Complete | ARCH-075-BACKGROUND-004 |
| ARCH-075-GATEWAY-001 | moda_gateway | Complete | None |

### Keyed provider result shape correction

Actual Responses translation echoed input-only protectedTokens fields, correctly rejected by strict ingestion. Background006 constrains keyed Responses Batch generation to the exact existing result JSON schema while preserving all local strict marker/key/hash validation and generic translation behavior. No field stripping, manual candidates, new model or Shared/schema release. Architecture remains In Progress; terminal accepted-current-source reconciliation includes this correction.

| ARCH-075-BACKGROUND-006 | moda_background | Complete | ARCH-075-BACKGROUND-005, ARCH-075-SHARED-004 |

### Durable app sample-throttle correction

Actual sample HTTP403/numeric Meta code4 was misclassified as permanent. Existing registration retry dates, fixed scheduler leases and event/config JSON cannot safely represent app-scoped backoff/fencing. Database002 adds dedicated environment/app state; Background007 enforces one120second bounded sample lease,15minute exponential cooldown capped6hours and conservative preclaim deferral across replicas. Timing is internal safety policy, not a provider reset guarantee. No cache/reuse or new Shared release. Generic old REJECTED records require exact root operator external-evidence attestation and strict preclaim/source/CAS/audit guards; never blanket recovery.

Rollout: additive migration test/prod, accepted Background schema/client adoption, messaging worker rollout and old-reader drain, then exact root-only historical recovery respecting cooldown. Existing creates/POST uncertainty remain unreplayable. Terminal SystemTest002 independently validates the new capability after accepted dependencies/manual checkpoint. Preserve accepted SystemTest001 without reopening or discarding its proof. Architecture remains In Progress.

| ARCH-075-DATABASE-002 | moda_database | Complete | ARCH-075-DATABASE-001 |
| ARCH-075-BACKGROUND-007 | moda_background | Complete | ARCH-075-DATABASE-002, ARCH-075-BACKGROUND-006 |
| ARCH-075-SYSTEM-TEST-002 | moda_system_test | Complete | ARCH-075-DATABASE-002, ARCH-075-BACKGROUND-007, ARCH-075-SYSTEM-TEST-001, ARCH-075-ADMIN-006 |

### Independent system validation accepted

The terminal system task is Accepted after actual disposable PostgreSQL/Redis/worker delivery and fault scenarios, canonical Admin activation, localized consent, Meta preclaim readiness and strict translation provider deltas. Exact source/image provenance and approved host-build limitations are recorded in its report. Architecture remains In Progress: synthetic fixtures do not replace live provider approvals, coherent environment copy, coordinated activation or genuine ordered recipient delivery.

### Repeated translation retry audit identity

Admin006 corrects a confirmed second-retry collision with the existing unique audit operation identity. Each nonempty serialized retry decision needs its own server identity; empty/concurrent repeats stay no-ops. Existing audit history/index, completed locales and provider policy remain unchanged. This independent task may run beside throttle work; terminal SystemTest002 includes its accepted reconciliation.

| ARCH-075-ADMIN-006 | moda_admin | Complete | ARCH-075-ADMIN-005 |

### Evidenced resumable upload identity correction

Production sample-session requests now return HTTP200 but the local uploader rejects their identifier before byte upload/create intent. Background008 owns only evidenced opaque Upload-ID preservation with trusted Graph destination/path/query validation and existing durable app-operation/deadline/config fences unchanged. Primary Meta documentation and protected actual structural evidence gate the final grammar; no raw signed identifier or secret is committed/logged. Historical403/code4 recovery stays the separate accepted BG007 exact-attestation path. No Shared release/schema/template rewrite is required. New source correction does not depend on terminal SystemTest002; its accepted prior throttle proof remains historical, not proof of this new correction. Common activation/provider approvals and genuine ordered recipient proof remain pending, so ARCH-075 stays In Progress.

| ARCH-075-BACKGROUND-008 | moda_background | Complete | ARCH-075-BACKGROUND-007 |

Background008 is Accepted/Complete at exact source36acc5f/report127c84b. Actual211-character signed Upload-ID structure is reproduced without live values, safe URL construction and diagnostic redaction pass152 focused/4,294 full tests, build and scoped lint. Four unrelated unchanged full-lint findings are explicitly retained. Root retains both exact-head hosted CI passes as an integration gate and owns deployment, historical recovery and live proof. Source acceptance does not establish Meta approval or common activation; architecture remains In Progress.

## Confirmed provider-boundary correction — 2026-11-13

All120 reviewed registrations failed template_create HTTP400/code100/subcode2388299. Root verified official Meta error-code documentation: leading/trailing BODY parameters are forbidden. Current Admin concatenation begins with shop.name and ends checkout.url. ADMIN007 owns the minimal provider-only correction: final common header, scenario body, checkout conditional, then existing reviewed localized static opt-out. New common header must itself have meaningful reviewed translated prefix; no transport-injected English/punctuation. Shared finalURL/common reference and AI/human ordered frame remain unchanged. Validate projected common and noncommon BODY boundaries before submission, preserve frozen submitted snapshots and exact preview/hash/bindings. No Shared release or broad120 retry. Root clones/reviews new immutable sources and submits one English canary before expansion; failed records remain history. Real approval, coordinated activation and Eugene Meta/AI/human/logo/product/checkout proof remain required; architecture remains In Progress.

| ARCH-075-ADMIN-007 | moda_admin | Ready | ARCH-075-ADMIN-001, ARCH-075-ADMIN-005 |
