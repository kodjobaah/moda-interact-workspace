# ARCH-066 definition review — 2026-11-08

Scope: current local architecture/task definitions checked against relevant source boundaries. This is not an implementation acceptance, registry verification, remote-main reconciliation or a claim that pending tasks are deployed. Completed task reports are retained; their source/test/publication claims were not independently rerun during this review.

## Findings and disposition

| Finding | Disposition |
|---|---|
| SHARED-004 supplied names and broad prose without implementable contracts | Rewritten task points to normative outreach contract specifying Zod payloads, ports, relocation map, ordered state transitions, refusal reasons, result/render fields and tests |
| Outreach consumers depended on completed SHARED-003 although5.6.0 excludes outreach | New SHARED-005 publication task; explicit consumer dependencies corrected; completed003 untouched |
| Existing graph allows alternative-product outreach, contradicting checkout-only requirement | Explicit new checkout-only decision schema; unexpected alternative refuses OUTSIDE_CHECKOUT; Background historical receipt handling and later conversational recommendations retained |
| Production context builder requires real active outreach attempt; preview must not create one | Reusable contract has run/checkout identity only; real attempt/credit/send fences remain host-owned |
| NONE policy currently skips live price reconciliation | New evaluator requires exact product read and final recheck for every distinct checkout identity even in NONE; zero offer/model calls in NONE |
| Template preparation facade includes WABA/database/media resolution | Pure helpers identified individually; hosts pass frozen validated projections; Studio uses ready existing media/TEXT fallback without upload/Meta calls |
| Claimed Studio route used nonexistent src/app directory | Commerce task now uses actual app/api/studio/preview/initial-outreach route family with list/start/status/cancel contracts and status codes |
| Duplicate/stale reads, changed checkout, retry budget and historical/current price semantics unspecified | Exact first-occurrence ordering, two reads per distinct ready basket pair, counted calls, no hidden retry, fingerprint fence and typed change refusal defined |
| Database task no longer contained previously requested Prisma block | Restored exact model/backrelations and CHECK SQL, JSON shape and ownership responsibilities |
| Architecture/index snapshots contradicted newer task state | Current summary/indexes rebuilt from frontmatter; historical completion notes retained and labelled historical |
| Earlier generic-description/attribute amendment absent from accepted5.6.0 contract | Resolved as new additive SHARED-006; provider/bootstrap/profile/host/system tasks now depend on SHARED-005 publication. Accepted5.6.0 history unchanged |

## Current task-record state

- Complete: SHARED-001, SHARED-002, SHARED-003 (original conversational scope,5.6.0).
- Ready: DATABASE-001.
- Pending: SHARED-004/005/006, MCP-001, BACKGROUND-001/002, COMMERCE-001/002, SYSTEM-TEST-001/002.
- Total14 tasks. MCP-001 readiness changed from Ready to Pending because its amended scope requires new SHARED-005; Attempt0/unclaimed unchanged. No implementation-cycle claim/completion performed in this review. Satisfied dependencies do not automatically claim/launch SHARED-004.

## Execution order

SHARED-006 (generic facts) -> SHARED-004 (outreach evaluator/rendering) -> SHARED-005 (new combined immutable artifact). DATABASE-001 independently remains Ready. MCP-001 adopts the new artifact; BACKGROUND-001/COMMERCE-001 follow MCP and their explicit database/host prerequisites, then SYSTEM-TEST-001. BACKGROUND-002 follows new005 and001; COMMERCE-002 follows new005, Commerce001 and Background002, then SYSTEM-TEST-002. Original completed5.6.0 is preserved as baseline; every pending consumer now pins new005 artifact when accepted.

## Remaining-task review corrections

The consumer contract fixes row-lock/CAS signatures and canonical equality; shared remaining budget for post-run verification; exact old/new fact selection semantics; single persisted AI-wrapper boundary and replay; final composed-body moderation; Redis atomic history/context/result fencing, accounting and purge; actual Next app paths; profile/descriptor immutable publication; generic provider mapping; integration fixtures/call-count expectations and coordinated activation compatibility. Every pending task now has an owned implementation checklist and required evidence. Completed task attempts were inspected as baseline, not silently reopened or re-accepted. New work belongs to006/004/005 and consumers.

## Validation performed

All task routes resolved with canonical route-only launcher. Dependency IDs, missing targets, cycles, inverse enables edges and domain-index rows checked locally. No service tests run for documentation-only change; no package publication, database migration, live provider calls or task execution started. This is a concrete definition repair; production readiness still requires each pending implementation and integration gate.
