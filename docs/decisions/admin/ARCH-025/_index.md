# ARCH-025 Admin tasks

Architecture: [`ARCH-025`](../../../architecture/ARCH-025-shopify-billing-service-maintainability.md).

Assigned agent: `moda_admin`.

Repository: `moda-interact-admin`.

Coordinator: `moda_architect`.

This directory contains two independent Admin maintainability chains. Neither depends on the Shopify or Background ARCH-025 chains. The MerchantPricingPlanBuilder chain is sequential internally because every child-step extraction consumes the accepted typed draft/controller boundary. The QueueMonitor chain is sequential internally because each hook/presentation extraction consumes the previously accepted client/control boundary.

```text
ADMIN-001 -> ADMIN-002 -> ADMIN-003 -> ADMIN-004
      -> ADMIN-005 -> ADMIN-006 -> ADMIN-007 -> ADMIN-008

ADMIN-009 -> ADMIN-010 -> ADMIN-011 -> ADMIN-012
      -> ADMIN-013 -> ADMIN-014 -> ADMIN-015
```

Current reviewed builder baseline:

```text
src/components/admin/merchant/merchant-pricing-plan-builder.tsx
1,553 lines
SHA-256: 7387fd18873e968220299cd976bd6705df8cba00b5c75f88a48b4d97a4ef05b0
```

The source hash is evidence only and is expected to change during extraction. The following pure/domain tests are frozen byte-for-byte for all eight tasks:

```text
tests/unit/merchant-pricing-builder-payload.test.ts
  a985f89cbc9f4d41901d2c1e400935faf8453a5bd866ac0834a58b0851feb243
tests/unit/merchant-pricing-plan-model.test.ts
  e953adaa54f7aceb31cc43af21f8088c800b32d69c2fc2561dff69fc27ce1086
tests/unit/merchant-pricing-plan-merchant-knowledge.test.ts
  610a7b0d0860490575cdec508f52e438a4e7bee87970a101b6b39d4591d6630f
tests/unit/merchant-pricing-economics.test.ts
  eb7164c84a7c056edfc461fd5b9213ab87e3537511ccf426d32f6bc6804e05e8
tests/unit/merchant-pricing-economics-override.test.ts
  434ad7ca05dad91bfb4fb62ce3ad5cbcd1f27355cc51c879dc7bd9a9967c79f7
tests/unit/merchant-pricing-translations.test.ts
  90e0e5e37687d3037712afac1828175fe8e6623550525572fbcb9d2dc57d8c92
tests/unit/merchant-pricing-translation-workbook.test.ts
  385e79ffcd761b046fb119be18de5f313461cb8d81d6a4f0fb23d3b7837e3ce8
```

`tests/security/admin-merchant-pricing-plan.test.mjs` starts at SHA-256 `89243548c486f68cc7b741e9cac6ded5090ba477f1049e512ae6f982ccd92856` with 13 tests. ADMIN-001 may change only its builder source-loading mechanism so the same assertions follow the bounded builder module set. ADMIN-002..008 must not modify the accepted ADMIN-001 version.

QueueMonitor reviewed baseline:

```text
src/components/admin/queue-monitor.tsx
1,058 lines
SHA-256: 851f8e5e25875a4bb6657ecd5d01bd2c4f3cf1bafa7928e342e332ce3012a4f7

src/components/admin/queue-monitor-refresh.ts
SHA-256: 14463cd5480aa82cd05ef569968ee579c14d94f610baab1d5ebdf1d31584a0cc
```

ADMIN-009 owns the bounded QueueMonitor source-loader change. ADMIN-011 has the architect-authorised jobs source-shape reconciliation in `admin-queue-monitor.test.mjs` and `admin-queue-details-drawer.test.mjs`; ADMIN-012 has one additional architect-authorised reconciliation limited to the three stale selected-detail source-shape assertions in those same two files. Neither task may change loader mechanics, test names or unrelated read-only/security/i18n assertions. `admin-failed-job-detail-panel.test.mjs` and `admin-internationalization.test.mjs` remain frozen at their accepted ADMIN-009 versions. After ADMIN-012 acceptance, ADMIN-013..015 must keep the architect-accepted ADMIN-012 versions of the first two files and the ADMIN-009 versions of the latter two unchanged. The server reader/routes and their dedicated tests remain frozen throughout ADMIN-009..015.

Individual task YAML is authoritative.

| Task | Outcome | Status | Dependencies |
|---|---|---|---|
| [ADMIN-001](ADMIN-001-extract-pricing-plan-draft-controller.md) | Typed draft/controller + extraction-safe security loader | Complete (Accepted, Attempt 2) | - |
| [ADMIN-002](ADMIN-002-extract-plan-step.md) | Plan/model/features/knowledge step | Complete (Accepted, Attempt 2) | ADMIN-001 |
| [ADMIN-003](ADMIN-003-extract-catalogue-placement-step.md) | Catalogue placement step | Complete (Accepted, Attempt 1) | ADMIN-002 |
| [ADMIN-004](ADMIN-004-extract-shopify-pricing-step.md) | Shopify pricing step | Complete (Accepted, Attempt 2) | ADMIN-003 |
| [ADMIN-005](ADMIN-005-extract-usage-events-step.md) | Usage-event/tier step | Complete (Accepted, Attempt 1) | ADMIN-004 |
| [ADMIN-006](ADMIN-006-extract-merchant-content-step.md) | Merchant content/highlights step | Ready | ADMIN-005 |
| [ADMIN-007](ADMIN-007-extract-portfolio-economics-step.md) | Portfolio economics/override step | Pending | ADMIN-006 |
| [ADMIN-008](ADMIN-008-extract-translations-review-and-reduce-builder.md) | Mounted translations/review + final thin shell | Pending | ADMIN-007 |
| [ADMIN-009](ADMIN-009-extract-queue-monitor-browser-client.md) | Browser contracts/client + extraction-safe QueueMonitor assertions | Complete (Accepted, Attempt 3) | - |
| [ADMIN-010](ADMIN-010-extract-queue-monitor-summary-hook.md) | Queue-summary polling/single-flight hook | Complete (Accepted, Attempt 2) | ADMIN-009 |
| [ADMIN-011](ADMIN-011-extract-queue-jobs-hook.md) | Queue jobs filters/page/recent-full hook | Complete (Accepted, Attempt 2) | ADMIN-010 |
| [ADMIN-012](ADMIN-012-extract-queue-job-detail-hook.md) | Selected-job detail hook | Ready | ADMIN-011 |
| [ADMIN-013](ADMIN-013-extract-resizable-queue-drawer-hook.md) | Resizable drawer viewport/pointer/keyboard hook | Pending | ADMIN-012 |
| [ADMIN-014](ADMIN-014-extract-queue-summary-table.md) | Queue summary table presentation | Pending | ADMIN-013 |
| [ADMIN-015](ADMIN-015-extract-queue-details-and-reduce-monitor.md) | Queue details presentation + final thin QueueMonitor shell | Pending | ADMIN-014 |

## Execution frontier

`ARCH-025-ADMIN-001`, `ARCH-025-ADMIN-002` and `ARCH-025-ADMIN-004` are Complete / Accepted at Attempt 2; `ARCH-025-ADMIN-003` and `ARCH-025-ADMIN-005` are Complete / Accepted at Attempt 1; `ARCH-025-ADMIN-006` is now the builder-chain Ready frontier. `ARCH-025-ADMIN-009` is Complete / Accepted at Attempt 3, `ARCH-025-ADMIN-010` is Complete / Accepted at Attempt 2, and `ARCH-025-ADMIN-011` remains the independent QueueMonitor Ready frontier in this branch snapshot. The two Admin chains remain independent of `ARCH-025-BACKGROUND-001` / `ARCH-025-BACKGROUND-008`; later tasks in each chain remain Pending until the immediately preceding task is architect-accepted Complete.
## ADMIN-005 Attempt 1 architect acceptance — 2026-10-03

**Accepted / Complete, Attempt 1.** Implementation `bbc560a...` moves the complete
Usage-events/tier presentation into a bounded child while navigation gating, event
serialization, economics evaluation/invalidation and final review remain in the
accepted controller/shell. The extracted JSX preserves the existing five-event limit,
mode/tier quirks and tier-removal behavior exactly.

Focused pricing security is 13/13, draft/controller is 14/14 and all seven frozen
hashes match independently. The unit suite retains only the two
`ARCH025-ADMIN-BUILDER-TEST-001` failures; the six broad failures are a strict subset
of `ARCH025-ADMIN-TEST-001` with no new/worsened identifier.

ADMIN-006 is promoted Ready; ADMIN-007..008 remain dependency-gated.

## ADMIN-004 Attempt 2 architect acceptance — 2026-10-03

**Accepted / Complete, Attempt 2.** The evidence-only retry built first and then
executed all three formerly skipped production-runtime telemetry tests: 3/3 passed,
0 skipped. Combined with Attempt 1, the full 235-test broad set is accounted for and
only the nine exact `ARCH025-ADMIN-TEST-001` failures remain.

No ADMIN-004 source/test change was required. Launcher implementation head
`325c5ea9...` adds only unrelated accepted ADMIN-010 QueueMonitor summary-hook files
relative to reviewed ADMIN-004 `6bf1de43...`, so the Shopify-pricing review remains
valid. ADMIN-005 is promoted Ready; ADMIN-006..008 remain dependency-gated.

## ADMIN-004 Attempt 1 architect review — 2026-10-03

**Changes Requested / Ready, Attempt 1 retained; claim clear.** The two-file Shopify
pricing presentation extraction is accepted in substance; no implementation/test
source correction is requested. Focused security 13/13, controller 14/14 and all seven
frozen hashes are satisfactory, and the nine broad failures are exact documented
Admin baseline failures.

The broad run also left three conditional production-runtime telemetry tests skipped
because `.next/BUILD_ID` did not yet exist. `ARCH025-ADMIN-BUILDER-TEST-001` does not
authorize skipped tests. Attempt 2 is evidence-only: build first, then run
`tests/observability/admin-telemetry-bootstrap.test.mjs` so the three formerly skipped
tests execute. ADMIN-005 remains Pending.

`ARCH-025-ADMIN-001` and `ARCH-025-ADMIN-002` are Complete / Accepted at Attempt 2, `ARCH-025-ADMIN-003` is Complete / Accepted at Attempt 1, and `ARCH-025-ADMIN-004` is the builder-chain Ready frontier. `ARCH-025-ADMIN-009` is Complete / Accepted at Attempt 3, `ARCH-025-ADMIN-010` is Complete / Accepted at Attempt 2, and `ARCH-025-ADMIN-011` is now the independent QueueMonitor Ready frontier. The two Admin chains remain independent of `ARCH-025-BACKGROUND-001` / `ARCH-025-BACKGROUND-008`; later tasks in each chain remain Pending until the immediately preceding task is architect-accepted Complete.
`ARCH-025-ADMIN-001` and `ARCH-025-ADMIN-002` are Complete / Accepted at Attempt 2, `ARCH-025-ADMIN-003` is Complete / Accepted at Attempt 1, and `ARCH-025-ADMIN-004` remains the builder-chain Ready frontier in this branch snapshot. `ARCH-025-ADMIN-009` is Complete / Accepted at Attempt 3, `ARCH-025-ADMIN-010` and `ARCH-025-ADMIN-011` are Complete / Accepted at Attempt 2, and `ARCH-025-ADMIN-012` is now the independent QueueMonitor Ready frontier. The two Admin chains remain independent of `ARCH-025-BACKGROUND-001` / `ARCH-025-BACKGROUND-008`; later tasks in each chain remain Pending until the immediately preceding task is architect-accepted Complete.
## ADMIN-003 Attempt 1 architect acceptance — 2026-10-03

**Accepted / Complete, Attempt 1.** Implementation `c31959af...` moves only the
Catalogue-placement JSX into a bounded child; placement derivation/transitions remain
in the accepted controller/canonical helper. Focused security 13/13, controller 14/14
and all seven frozen hashes pass. The six remaining broad failures are a subset of
`ARCH025-ADMIN-BUILDER-TEST-001`; disappeared baseline failures are treated as an
improvement and are not recreated.

ADMIN-004 is promoted Ready; ADMIN-005..008 remain dependency-gated.

## ADMIN-002 Attempt 2 architect acceptance — 2026-10-02

**Accepted / Complete, Attempt 2.** Correction commit `77a5e68f...` removes the full
persisted `plan` object from `PlanStep`, consumes existing
`controller.draft.isEditing`, and changes only the two task-authorised presentation
files. No controller/test/server/policy source changed. Focused security 13/13,
draft/controller 14/14 and all seven frozen hashes pass independently; broader failures
remain exactly within `ARCH025-ADMIN-BUILDER-TEST-001`.

ADMIN-003 is promoted Ready; ADMIN-004..008 remain dependency-gated.

## ADMIN-002 Attempt 1 architect review — 2026-10-02

**Changes Requested / Ready, Attempt 1 retained; claim clear.** The two-file Plan-step
move is accepted in substance and all focused/frozen/baseline-aware validation is
satisfactory. One bounded R2 correction remains: `PlanStep` receives the complete
persisted `MerchantPricingPlanWithChildren` object solely to compute edit/read-only
state. Attempt 2 must consume existing `controller.draft.isEditing` instead, remove the
full `plan` prop/import, rerun ADMIN-002 validation and return to review.

No ADMIN-001 controller/security/server contract change is authorised. ADMIN-003
remains Pending.
`ARCH-025-ADMIN-001` and `ARCH-025-ADMIN-002` are Complete / Accepted at Attempt 2; `ARCH-025-ADMIN-003` is Complete / Accepted at Attempt 1; `ARCH-025-ADMIN-004` remains the builder-chain Ready frontier in this branch snapshot. `ARCH-025-ADMIN-009` is Complete / Accepted at Attempt 3; `ARCH-025-ADMIN-010` and `ARCH-025-ADMIN-011` are Complete / Accepted at Attempt 2; `ARCH-025-ADMIN-012` is the QueueMonitor Ready frontier. Later tasks in each chain remain dependency-gated.

## ADMIN-001 Attempt 2 architect acceptance — 2026-10-02

**Accepted / Complete, Attempt 2.** The evidence-only retry leaves implementation
`0cd5c010926acfbfaf808fb5d727df9269b30fdb` unchanged. Same-environment comparison
against pre-task `b8da632a1fcaef7e364be1dc5cca40dfafde4703` shows identical two
unit-test failures and identical nine package-suite failure identities/reasons, while
the submitted tree adds fourteen focused controller passes and three package-suite
passes. Prepared launcher/worktree/synchronization/submodule evidence is durably
recorded.

`ARCH025-ADMIN-BUILDER-TEST-001` now records those exact inherited failures for
ADMIN-002..008. ADMIN-002 is promoted Ready; later builder tasks remain gated.

## ADMIN-001 Attempt 1 architect review — 2026-10-02

**Changes Requested / Ready, Attempt 1 retained; claim clear.** The submitted typed
draft/controller and extraction-safe security loader are accepted in substance; no
source/test correction is requested. Attempt 2 is evidence-only unless a differential
reveals a regression.

Before acceptance, compare `npm run test:unit` and `npm test` under the same
environment on pre-task Admin `b8da632a1fcaef7e364be1dc5cca40dfafde4703`
versus submitted `0cd5c010926acfbfaf808fb5d727df9269b30fdb`, recording exact
failure identities/reasons, and add the prepared launcher/worktree/synchronization/
submodule evidence to the Completion Report. ADMIN-002 remains Pending; ADMIN-009 is
independently Ready.

## ADMIN-012 Attempt 2 architect review — 2026-10-03

**Changes Requested / Ready, Attempt 2 retained; claim clear.** Attempt 2 correctly
made no source/test change because the parent task still had no durable architect
decision. The architect now resolves the contract conflict in favour of the explicit
`useQueueJobDetail` ownership boundary.

Attempt 3 is authorised to update only three stale selected-detail source-shape
assertions in `admin-queue-monitor.test.mjs` /
`admin-queue-details-drawer.test.mjs`. Loader mechanics, test names, unrelated
ADMIN-011 jobs/security/i18n assertions and the other two harness files remain frozen.
No ADMIN-012 implementation source correction is requested.

After ADMIN-012 acceptance, its updated versions of those two source-contract files
become the frozen jobs+detail baseline for ADMIN-013..015. ADMIN-013 remains Pending.

## ADMIN-011 Attempt 2 architect acceptance — 2026-10-03

**Accepted / Complete, Attempt 2.** Correction commit `57177099...` changes only the
two architect-authorised harness files and only the four stale jobs ownership
assertions. Loader mechanics, test names and unrelated security/read-only/i18n
assertions remain unchanged. The focused QueueMonitor harness is 27/29 with only the
two global i18n baseline failures; full `npm test` is 226/235 with exactly the nine
`ARCH025-ADMIN-TEST-001` failures. Jobs-state tests remain 6/6 and all frozen hashes
match.

The accepted ADMIN-011 versions of `admin-queue-monitor.test.mjs` and
`admin-queue-details-drawer.test.mjs` are now frozen for ADMIN-012..015. ADMIN-012 is
promoted Ready; ADMIN-013..015 remain dependency-gated.

## ADMIN-011 Attempt 1 architect review — 2026-10-03

**Changes Requested / Ready, Attempt 1 retained; claim clear.** The jobs-hook
implementation `1a3c757...` is accepted in substance; old-vs-new review confirms the
queue/filter/direction/View-all/pagination/request asymmetries remain intact.

The four additional broad failures are stale ADMIN-009 source-shape assertions that
require jobs logic to remain inline, contradicting ADMIN-011's explicit ownership
move. Attempt 2 is authorised to update only those assertions in
`admin-queue-monitor.test.mjs` and `admin-queue-details-drawer.test.mjs`. Loader
mechanics, test names, all unrelated security/read-only/i18n assertions and the other
two harness files remain frozen. No implementation source correction is requested.

After ADMIN-011 acceptance, its updated versions of those two harness files become the
frozen baseline for ADMIN-012..015. ADMIN-012 remains Pending.

## ADMIN-010 Attempt 2 architect acceptance — 2026-10-03

**Accepted / Complete, Attempt 2.** The evidence-only retry completed `npm test`
(235 total / 226 passed / 9 exact `ARCH025-ADMIN-TEST-001` failures), corrected the
implementation upstream to `origin/task/ARCH-025-ADMIN-010`, and records clean
local==remote implementation state at `e518c144...`. The launcher synchronization merge
contains only unrelated ADMIN-002/003 Merchant Pricing files and does not alter
QueueMonitor, frozen or dependency state. Stale task claim metadata is cleared as part
of architect completion.

ADMIN-011 is promoted Ready; ADMIN-012..015 remain dependency-gated.

## ADMIN-010 Attempt 1 architect review — 2026-10-03

**Changes Requested / Ready, Attempt 1 retained; claim clear.** The three-file summary
hook extraction is accepted in substance; no implementation/test source correction is
requested. Focused summary tests are 3/3, QueueMonitor-owned security assertions pass,
the full unit failures are inherited, and all frozen QueueMonitor hashes remain exact.

Attempt 2 is evidence/repository-state only: complete the entire
`tests/observability/*.test.mjs` + `tests/security/*.test.mjs` coverage (prefer a
terminal `npm test`; deterministic complete file-set execution is the fallback if the
monolithic runner is interrupted again) and change the Admin implementation branch
upstream from `origin/main` to `origin/task/ARCH-025-ADMIN-010`. ADMIN-011 remains
Pending.

## ADMIN-009 Attempt 3 architect acceptance — 2026-10-02

**Accepted / Complete, Attempt 3.** The final report-only retry reconciles all five
Acceptance Criteria and final branch state. The launcher-required implementation
merge head `b09d421d...` changes only already-accepted ADMIN-001 files relative to
reviewed ADMIN-009 implementation `eda069b4...`; no QueueMonitor/frozen/dependency
state changed, so the Attempt 2 validation remains authoritative. Final parent task
head is `1c9a1305...`.

ADMIN-010 is promoted Ready; ADMIN-011..015 remain dependency-gated.

## ADMIN-009 Attempt 2 architect disposition — 2026-10-02

**Changes Requested / Ready, Attempt 2 retained; claim clear.** Attempt 2 satisfies
the implementation/provenance/baseline evidence contract and leaves implementation
`eda069b4...` unchanged. The only remaining items are task-record reconciliation:
the five Acceptance Criteria remain unchecked, and the Completion Report's Final
Branch State still contains a pre-publication placeholder rather than final parent
report `9df2fa00...` plus clean local==remote evidence.

Attempt 3 is report-only. No implementation/test changes or validation reruns are
requested absent unexpected state drift. ADMIN-010 remains Pending until ADMIN-009 is
Complete.

## ADMIN-009 Attempt 1 architect disposition — 2026-10-02

**Changes Requested / Ready, Attempt 1 retained; claim clear.** The browser-local
contracts/client extraction and bounded source-loader changes are accepted in
substance; no implementation/test source correction is requested.

The former validation block is reclassified as inherited Admin baseline debt under
`ARCH025-ADMIN-TEST-001`: the focused command's only two failures are global i18n
assertions reproduced on pre-task `b8da632a...`, while every QueueMonitor-owned
assertion passes. The two unit failures and all nine submitted package-suite failing
identifiers are likewise reproduced at the starting revision.

Attempt 2 is evidence-only: record the complete prepared-launch packet, cite the
baseline, reconcile task checklists/report state, preserve implementation `eda069b...`
and return to review. ADMIN-010 remains Pending until ADMIN-009 is Complete.
## Deep coherence review — 2026-10-02

A source/task closure review against the 1,553-line post-ARCH-024 builder kept the ADMIN-001..008 graph unchanged and tightened the execution contract before ADMIN-001 starts. ADMIN-001 must establish the complete consume-only controller/action/selector interface for every later step, keep its pure reducer directly Node-testable, preserve hook-edge event/highlight identity generation and effect-driven economics-override invalidation, make the security harness scan the full bounded builder module set (including the ARCH-014 forbidden-dependency check), and preserve the exact hidden translation JSON fallback. ADMIN-002..008 may consume but not extend that accepted controller; a missing interface returns to `moda_architect`. Usage-event stale-field/tier quirks, the current empty secondary economics rows, and the workbook/final-step mount/conditional DOM semantics are explicitly preserved as move-only behaviour.
