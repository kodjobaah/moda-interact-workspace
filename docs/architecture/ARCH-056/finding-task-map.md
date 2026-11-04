# ARCH-056 finding-to-task register

## Meaning of this register

This register covers all **37 finding references** from the updated wider database assessment, including the three focused follow-up findings U1/U2/U3. It prevents the six-task package from being mistaken for closure of the whole review.

**Selected** means the correction is included in an implementation task; it does not mean implemented or accepted. **Partial** identifies the bounded selected behavior and explicitly retains the remaining concern. **Preserved** means the updated snapshot already addresses the original concern and the new task must keep it correct. **Deferred** means no implementation is assigned in this package. Task status and runtime proof are separate from these dispositions.

Short task names in the table expand to `ARCH-056-<name>`. Paths without a repository prefix are relative to `moda-interact-background/src`; the complete ownership allowlist is in `deterministic-execution-map.json`. Every selected implementation path has one writer; read-only context does not grant edit permission.

## Complete coverage table

| Reference | Disposition | New task owner | Touchpoint and explicit boundary |
|---|---|---|---|
| U1 | Selected | API-001; SYSTEM-TEST-001 | API `database` gitlink/materialisation and normal generated client. Require the two accepted fields and all three ARCH-055 migrations. Actual recorded Git provenance must be inspected; unfinished API endpoints/readiness remain separately owned. |
| U2 | Selected | BACKGROUND-003; BACKGROUND-004; SYSTEM-TEST-001 | `services/recovery-template-integration/initial-no-offer-fallback.service.ts`, canonical UsageEvent-to-message inspection and Shopify/Woo final fences. Remove the wrong usage-key/provider-key comparison and classify owned persisted progress before preparation. |
| U3 | Selected | BACKGROUND-001; SYSTEM-TEST-001 | `services/conversation.service.ts` parent-first helper/message transaction. Preserve the accepted helper lock/current-state rules and prove FK concurrency/duplicate rollback with real services. The old language-resolution race is deferred. The receipt-order correction is a separate selected design decision below. |
| R1 | Deferred | None | `runtime/background-runtime-lease.ts`, `runtime/dynamic-leased-scheduler.ts`: false/rejected renewal, lease-loss propagation and takeover. Duplicate business effects were not established by the static finding. |
| R2 | Deferred | None | Runtime configuration polling, concurrency reconciliation and pending-turn repair. Measure per-process workload before changing coordination; no global lease is selected merely to reduce reads. |
| R3 | Partial | BACKGROUND-001; BACKGROUND-002; BACKGROUND-003; BACKGROUND-004; SYSTEM-TEST-001 | Revision 2 requires actual safe original messages, stage/correlation and paired-failure evidence throughout the selected touchpoints, including the existing WhatsApp worker failure projection and two narrow Meta diagnostic-projection corrections. Verify emitted JSON through the installed Shared package and real worker output. Remaining configuration/readiness replacement sites in `services/platform-configuration/` and other unselected files remain deferred. No whole-application logging repair is claimed. |
| C1 | Deferred | None | `services/pending-recovery-candidate/checkout-order-guard.service.ts` and materializer exclusion: ten-second unrenewed Redis lease and GET/DEL release. Sequence later changes against BACKGROUND-004's materializer work. |
| C2 | Deferred | None | `services/checkout-recovery/checkout-event-orchestrator.service.ts`: guard basket writes against the observed source/activity version after external lookup. |
| C3 | Partial | BACKGROUND-002; BACKGROUND-003; BACKGROUND-004; SYSTEM-TEST-001 | Real candidate/materializer/initiation/finalizer retry; same-message pre-permit continuation and exact-source confirmed completion. Unknown provider outcomes and unsupported historical/nonunique sources remain explicit holds. No universal eventual-completion claim after finite job exhaustion. |
| C4 | Deferred | None | `services/recovery-capacity-resume.service.ts`, `workers/recovery-capacity-resume.worker.ts`, `domain/recovery-capacity-resume.ts`: cursor/pass progress beyond an obstructed first page. Preserve per-shop eligibility. |
| C5 | Deferred | None | `services/checkout-recovery/order-recovery-correlation.service.ts`: exact observed-status CAS/history during concurrent completion. Existing terminal safety remains. |
| O1 | Deferred | None | `services/recovery-policy.service.ts`, pending-candidate and Woo checkout scheduling: purpose-specific delay reads while retaining override expiry and platform policy. |
| O2 | Deferred | None | `services/checkout-recovery/checkout-event-orchestrator.service.ts`: consider the single-update transaction only together with C2's write fencing. |
| O3 | Deferred | None | `services/checkout-recovery/latest-recovery.ts`: consumer-specific projections. A materializer using few fields does not justify narrowing every consumer. |
| O4 | Deferred | None | `services/woocommerce-recovery/woo-recovery-composition.ts` and preflight adapters: reduce repeated checks only with explicit freshness evidence. Ordinary production initial send remains disabled. |
| O5 | Deferred | None | Database CheckoutRecovery generation indexes: inspect actual index catalog and plans before a new forward migration; preserve uniqueness and historical migrations. |
| O6 | Deferred | None | `services/checkout-recovery-expiry.service.ts`: any batching must retain exact transition CAS, history and attempt cancellation together. |
| O7 | Deferred | None | `services/recovery-template-integration/automated-recovery-template.service.ts` and fallback adjacent lifetime/recovery reads. Sharing BACKGROUND-004's file does not authorise an extra read-reuse optimisation; keep later fresh checks after external awaits. |
| MSG-01 | Preserved | BACKGROUND-001 | Accepted ARCH-054 pending-turn capture now chooses from current locked Conversation state. Regression-test it; do not reopen the old unlocked-snapshot finding or weaken its lock. |
| MSG-02 | Partial | BACKGROUND-003 | Initial-template technical moderation retry must preserve resumable state and propagate a technical outcome. General AI moderation-to-turn completion through `services/conversation-turn-processor.service.ts` remains deferred. |
| MSG-03 | Partial | BACKGROUND-003 | Selected initial-template inspection/resume and guarded cleanup retain one identity. General AI reply/reservation replay and terminal turn-completion semantics remain deferred. |
| MSG-04 | Deferred | None | Durable early/unmatched provider status retention in `services/whatsapp-provider-status.service.ts` and ingress worker is not selected. BACKGROUND-002's locking-only change preserves current unknown-message behavior and does not create an inbox. |
| MSG-05 | Deferred | None | `services/recovery-routing.service.ts`: canonical indexed phone routing and cross-shop ambiguity. Returned LIMIT 2 is not a bound on scanned rows. |
| MSG-06 | Deferred | None | `services/outbound-whatsapp-admission/outbound-admission-reservation.service.ts`: all-message-ID usage aggregation inside SERIALIZABLE. Selected identity/resume work preserves existing quota logic. |
| MSG-07 | Deferred | None | `services/conversation-moderation/moderation-turn-gate.ts`, `commerce/history.ts`, `workers/whatsapp.worker.ts`: history/moderation bounds must preserve every pending fragment and watermark. BACKGROUND-001's diagnostic-only worker edit does not select this history/turn behavior. |
| MSG-08 | Deferred | None | `services/whatsapp-contact-opt-out/stop-writer.ts`: unresolved-phone scans and sorted Shop locks. Preserve merchant-specific quoted STOP and standalone global STOP semantics. |
| MSG-09 | Partial | BACKGROUND-003 | Carry the verified conversation ID into `markSent` and persist parent-before-message receipt/clock atomically. Other engagement, human-command and text Conversation rereads remain deferred. Later policy checks must remain fresh. |
| MSG-10 | Deferred | None | Measure contention and polling across Shop/Conversation locks, human-command scans and bounded pending-turn repair. Selected lock-order correctness does not establish system-wide contention or capacity improvement. |
| TEMPLATE-01 | Deferred | None | `services/template-translation/repository.ts`: set-based publication must preserve atomic claim and publication; current explicit-call model is 5 + 2N, not measured SQL latency. |
| TEMPLATE-02 | Deferred | None | `services/meta-template-management/due-poller.ts`, repository and service: repeated GET discovery across replicas is distinct from CAS-protected mutation/POST. Measure before adding claims. |
| BS-01 | Deferred | None | `services/merchant-knowledge-reconciliation.service.ts`: retained ineligible prefixes need bounded pass/cursor progress. |
| BS-02 | Deferred | None | `services/merchant-knowledge-upload-cleanup.service.ts`: external deletion lacks durable acknowledgement. Separate lifecycle/schema design is needed if selected; preserve accepted ARCH-055 cleanup-winning locks. |
| BS-03 | Deferred | None | Knowledge entitlement reconciliation/eligibility: share bounded pass context only while retaining transaction-current mutation checks. |
| BS-04 | Selected | BACKGROUND-002 | `services/paid-included-recovery-reservation.service.ts`: reuse the already validated same-transaction Shopify plan/meter handle and remove its duplicate lookup. This is mandatory narrow scope, with no generic cache or whole-flow performance claim. |
| BS-05 | Partial | BACKGROUND-002; BACKGROUND-004 | Exact proved original source permits positive settlement; multiple candidates, released history, ambiguous outcome and unsupported old-period RESERVED credit stay held. Do not choose newest/current or infer a new uncertainty policy. |
| BS-06 | Deferred | None | `services/billing-subscription-reconciliation/reconciliation-queue.service.ts`, `entrypoints/billing.ts`: global scan/future enqueue needs explicit cursor/horizon ownership. |
| BS-07 | Deferred | None | Translation batch assembly, Shopify/Woo availability catalogues and knowledge chunks are distinct later batching touchpoints. Preserve generation publication and per-merchant/chunk ownership. |

## Additional decisions selected during task design

The source findings identify problems; the following mechanisms are explicit architectural choices made while defining the correction. They are not retroactive claims that the earlier audit reproduced each race or approved a billing policy.

| Decision | Owning task | Why it is required |
|---|---|---|
| Exact typed original-source revalidation and confirmed settlement | BACKGROUND-002 | Orchestration must distinguish a committed debit from a lower-level replay that stayed AMBIGUOUS or RELEASED. |
| Shop KEY SHARE before message mutation in settlement, compensation and provider-status convergence | BACKGROUND-002 | UsageEvent insertion acquires an immediate Shop FK lock. Acquiring it only after the message can oppose the final fence's Shop-before-message order. Policy/status predicates remain unchanged. |
| Message lock before reservation SHARE in both final fences | BACKGROUND-003 | A fence must not hold reservation SHARE while waiting for a message held by settlement that next mutates that reservation. |
| Parent-first receipt persistence using verified conversation identity | BACKGROUND-003 | Same-message resumption creates a deliberate competitor with the final fence. Receipt and clock stay atomic without a reverse message-to-Conversation acquisition. |
| Preserve failed-message lineage before removing the sole usage route | BACKGROUND-003 | Missing usage cannot be mistaken for no previous provider attempt or authority to allocate a new identity. |
| Shop KEY SHARE before the atomic Support finalizer's attempt lock | BACKGROUND-004 | First-thread and recovery-linked notice FK inserts must not request parent protection after an attempt lock opposed by the final fence. Preserve the same atomic writer and identity checks. |
| Confirmed progress before current new-send gates; persisted null due date remains null | BACKGROUND-004 | Bookkeeping replay must neither send again nor recompute a finalised scheduling decision from current policy. |
| Exact accepted revision for the executed Background image | SYSTEM-TEST-001 | The existing image builder can fetch remote main independently of a source-root parameter; provenance must identify what actually ran. |
| Safe original messages at source, aggregation and worker boundaries | BACKGROUND-001/002/003/004 | Shared's inspected Error serialization omits causes, codes and aggregate members. Explicit bounded diagnostics and source-owned provider details must survive without reintroducing sensitive raw text in an outer worker. |
| Actual emitted-record logging evidence | SYSTEM-TEST-001 | Validate the resolved installed Shared package and raw process records before the harness sanitizes evidence; `arch056-logging.json` records existing case assertions. Mock logger calls and a generic final exception do not prove an original diagnostic was emitted. |

The lock choices address the selected competing paths, including immediate foreign keys. They do not certify every writer in the application as deadlock-free. Required tests use actual migrated rows, real services and deterministic barriers.

## Existing task ownership stays intact

Individual task frontmatter and latest review are authoritative. Earlier paragraphs describing a once-pending attempt do not override its later Complete state. Historical claimed tests have not been rerun by this definition pass.

| Existing task group | Snapshot state | Boundary retained |
|---|---|---|
| ARCH-028-BACKGROUND-012 | Complete, attempt 3 | Preserve checkout options-object/update re-entry and missing-recipient marker cleanup. |
| ARCH-028-BACKGROUND-013 | **Blocked**, attempt 0 | Pre-HTTP permit billing policy remains unapproved; this package does not relabel or unblock it. |
| ARCH-040-BACKGROUND-008/009; ARCH-046-BACKGROUND-004 | Complete | Retain final permit/consent/window guards and purchased lot-plus-counter semantics. |
| Relevant ARCH-050 implementation tasks | Complete | Retain atomic optional Support notice/attempt finalisation, deterministic notice key and opt-out replay. |
| ARCH-051-BACKGROUND-001 | Complete | Each new task owns its regressions; no new blanket test-remediation task. |
| ARCH-052-BACKGROUND-018 and related accepted implementation | Complete | Retain neutral fallback and merchant mode/basket/offer admission. |
| Relevant ARCH-053 implementation tasks | Complete | Retain recovery lifetime, restoration/generation and confirmed-offer ownership. |
| ARCH-054-BACKGROUND-001/002/003 | Complete | Retain locked current pending state, fixed deadline/control fences and bounded queue repair. |
| ARCH-055-DATABASE-001; ARCH-055-BACKGROUND-001; ARCH-055-API-005 | Complete | Accepted schema, persisted historical claim identity and upload intake/purpose behavior are baseline contracts. |
| ARCH-055-API-004/007 | Ready | Their unfinished endpoint behavior is not absorbed by API-001 dependency alignment. |
| ARCH-055-API-009; ARCH-055-SYSTEM-TEST-001 | Pending | Readiness/aggregate runner and all-endpoint API proof keep their existing ownership. |
| Earlier ARCH-050/052/053/054 terminal tasks | Various Ready/Pending | They remain separate certification work and are not invented prerequisites for new implementation tasks. |

## Later work and file sequencing

Deferred work can be defined later without reopening completed historical tasks. Before assigning it, inspect the accepted ARCH-056 result and give each shared production file one active writer. In particular, sequence C1/C2/C5/O3/O7 against the checkout/materializer/fallback owner; MSG-02/03/04/06/09 against outbound/status changes; and BS-05/blocked uncertainty work against the billing/compensation owner.

Index, cursor, polling and batching proposals still require workload, plan or cardinality evidence where the review called for it. A direct-call count is not a production latency measurement. No deferred finding receives acceptance merely because its file appears in a selected task's read-only context or validation.
