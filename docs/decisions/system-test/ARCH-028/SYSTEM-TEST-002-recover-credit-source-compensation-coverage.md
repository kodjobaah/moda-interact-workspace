---
id: ARCH-028-SYSTEM-TEST-002
architecture_id: ARCH-028
title: Recover source-specific compensation acceptance coverage
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 10
executor: codex
claimed_at: 2026-11-13T15:10:32Z
attempt: 1
depends_on:
  - ARCH-028-ADMIN-001
  - ARCH-028-BACKGROUND-007
  - ARCH-028-BACKGROUND-009
  - ARCH-028-SHOPIFY-001
  - ARCH-047-ADMIN-007
  - ARCH-047-BACKGROUND-006
enables: []
created: 2026-11-13
updated: 2026-11-13
---

# Recover source-specific compensation acceptance coverage

## Architecture

ARCH-028; docs/architecture/ARCH-028-whatsapp-delivery-failure-convergence.md; coordinator moda_architect.

## Objective

Incorporate the backed-up missing source-specific131026 compensation coverage onto current main without losing newer acceptance behavior.

## Context

Primary checkout has27 tracked edits and30 untracked additions behind current main. The delta adds three PAID/PROMO/PURCHASED scenarios plus supporting fixtures/diagnostics/terminal-recipient checks. Root verified full external Git bundles, staged/unstaged binary patches and nonignored untracked archives before reconciliation. This bounded incremental acceptance slice does not complete the original broad ARCH028SYSTEM001 certification.

## Scope

Selective missing compensation scenarios, approved Admin/Meta template fixtures, settled durable capacity gate, terminal-recipient suppression/merchant-notice UI/order/idempotency observation, directly supporting bounded diagnostics/tests/catalogue/docs from the protected backup.

## Out of Scope

Application source fixes, full18-scenario ARCH028 certification, non131026/uncertain settlement policy expansion, live provider/customer calls, raw historical evidence publication, framework changes and main integration.

## Requirements

- Base execution on fresh current system-test main, preserving all ARCH075/coupon/merchant-followup scenarios and existing encryption/messaging.meta/Meta-ingress contracts. Current catalogue plus exactly three genuinely missing rows replaces neither current main nor its newer entries.
- Selectively port27 tracked/30 untracked local candidates from verified moda-local-reconciliation-backup-20261113T145749Z. Do not copy historical attempt25 transcript. Correct ported fixtures to actual current strict contracts (including required schemaVersion1); do not weaken validators/assertions.
- Exercise PAID included-current-period, active promotional and valid purchased-lot credit correction with exact source-owned balances, linked negative reporting usage and original lineage. No test may pre-create recovery reservations/usages/messages/compensation; actual accepted workers create those. Synthetic purchase issuance is explicit fixture, not a real charge.
- Signed131026 receipt must settle durable correction/suppression before the once-only merchant SYSTEM notice. Replay/stale receipts cannot double-correct, transfer credit, change suppression identity or send again. Subsequent same-shop suppressed checkout admits no extra billing/provider work. Strong MESSAGE_SENT plus exact settled ledger readiness prevents premature passes.
- Run actual synthetic tenant-isolated disposable PostgreSQL/Redis/current accepted worker images and local HTTP Meta/Shopify emulators for the three source cases and modified Free/status/settlement paths. Record exact source/image/migration identities and actual outcome. Route product defects to owners rather than patching other repositories.
- Failure-stage diagnostics must remain bounded/redacted, respect actual authenticated merchant UI/tenant boundaries and preserve truthful failures. Existing main readiness/encryption modules are reused rather than replaced with stale local versions.
- All explicit implementation prerequisites are Complete. Root's new explicit recover/test request supplies the current developer manual launch checkpoint. This is a terminal task; no implementation depends on it. Preserve original SYSTEM001 broad scope/status and accepted ARCH075 evidence. No production/full architecture certification claim.

### Bounded validation-image amendment — 2026-11-13

The exact accepted-source default Docker build exhausted V8 memory (exit134) before business assertions. Existing documented validation already records the default failure and a failed 3072MiB resource override. Reuse the approved correctness-image approach through a task-owned exact-current-source manifest/parameter; do not weaken historical pin guards or present a stale image as current proof. Pin accepted Background and nested Database full commits, source/lock and original/derived Dockerfile hashes. Retain audited JavaScript/maps/JPEG outputs only, unchanged Linux dependencies/Prisma/runtime, image digest and nonpromotable host-compiled-js labels. Validate wrong-pin refusal. Host Node24 compilation versus Linux Node22 runtime must be explicit in evidence. No application-source changes or unnecessary repeated known-failing builds. This fallback can establish business runtime behavior only; production Docker-build parity remains unverified and must be reported separately. Original broad ARCH028 certification and live acceptance are not implied.

### Bounded queue-probe timing amendment — 2026-11-13

An actual signed-checkout run hit the 12-second queue-idle deadline under host load while immediate diagnostic readback showed checkout queue empty, no failed jobs, and the intended waiting candidate/index. Permit a bounded 30-second deadline or existing configurable equivalent in System-only polling, with a slow-probe regression. Preserve exact queue-empty, business settlement and failure assertions; retain bounded timeout diagnostics and measured probe costs. Four Docker Redis calls per probe must not turn a successful drain into a premature deadline failure. Candidate waiting before recovery-worker startup is intentional, not proof of recovery completion. Actual rerun success is still required; no product implementation change is authorized by this timing amendment.

## Work Items

- [x] Reconcile backup/current-main overlap and port missing behavior only.
- [x] Validate fixtures, bounded diagnostics and meaningful integrated compensation paths.
- [x] Publish mirrored report/source, set review and stop.

## Interfaces / Contracts

Current accepted ARCH028/ARCH027 credit and provider contracts, ARCH047 approved template lifecycle and published Shared contracts remain authoritative. No new release or application source edit. Root owns full verified external backup and final integration; preserve all originals.

## Dependencies

ARCH-028-ADMIN-001, ARCH-028-BACKGROUND-007, ARCH-028-BACKGROUND-009, ARCH-028-SHOPIFY-001, ARCH-047-ADMIN-007, ARCH-047-BACKGROUND-006.

## Enables

None

## Acceptance Criteria

- [x] Three missing source scenarios and supporting coverage are incorporated without removing newer main functionality.
- [x] Actual durable source-specific accounting, suppression/notice ordering/idempotency and strict fixture contracts pass meaningful disposable tests.
- [x] Exact source/image/backup/isolation/synchronization/validation evidence is truthful; no live mutation or full certification claim.

## Validation

- [x] Actual declared full harness/unit/static/catalogue/syntax checks and privacy/diff hygiene.
- [x] Three source compensation disposable integrated runs plus modified Free/provider-status/durable-settlement paths with real PostgreSQL/Redis/worker/emulator evidence. Missing prerequisites or product failures are reported, not fabricated green.

## Stop Condition

Publish task-owned source and parent report on matching branches, set review and return to moda_architect. Do not self-accept, merge, deploy, mutate live systems or start follow-on tasks.

## Implementation Notes

You are not alone; preserve others' edits. Normal launcher owns dedicated matching parent/implementation worktrees, synchronization, recursive submodules and claim. Never reuse primary or another task worktree. Root owns final integration. No broad new architecture or credential export publication.

## Completion Report

### Status

Ready for Review. Implementation and mirrored task report are committed/pushed on `task/ARCH-028-SYSTEM-TEST-002`. No main branch merge or live validation was performed by this owner.

### Files Changed

System Test catalogue/matrix; three source-selected compensation scenarios and accounting/receipt/suppression/notice observations; approved Meta fixture authoring/fingerprints; complete current Shopify outreach model/pricing/prompt/MCP context; queue and full-entrypoint startup readiness; singleton merchant session/numeric Shop identity fixtures; bounded failure diagnostics; focused regression tests; capability-named correctness-image builder and durable evidence/manifest. No application implementation, migration history, Shared package or primary checkout was changed.

Implementation head: **e29324911185fe27543bd50480c44d6509fecbad**. Functional head before documentation: `5a1ed06`. [Source PR #8](https://github.com/kodjobaah/moda-interact-system-test/pull/8). Durable source evidence: `docs/validation/credit-source-compensation-evidence.md` and `docs/validation/credit-source-compensation-image.json` in that repository.

### Work Completed

Selectively reconciled the protected local delta onto baseline `f3914582f31c3dc261852ed10cd98537809776ad`; retained all 181 existing entries and added exactly three missing PAID/PROMO/PURCHASED rows (184 total). Preserved newer ARCH-075, coupon, merchant follow-up, ordered-message, readiness, messaging.meta and unified encryption behavior. Raw historical attempt-25 operator transcript remains protected outside Git. Worktree-aware Gateway lookup uses the authoritative MODA_WORKSPACE_ROOT.

Real accepted workers created and settled every recovery reservation/usage/message/correction. Each source case asserted one selected-source positive usage/COMMITTED reservation, Free forced to zero, then one immutable -1 correction restoring only the original source. Paid current-period credit is not forfeited; active promotional grant reopens; a consumed purchased lot reopens ACTIVE with one spendable credit and no refunding. Duplicate FAILED/stale SENT preserves lineage, correction identity, seven-day shop-scoped suppression and once-only SYSTEM notice with no extra send. Status acceptance separately proves authenticated visible merchant receipts/notice, forged-signature rejection and a later suppressed checkout producing no extra billing/provider work.

Measured fixture failures were corrected without weakening guards: mandatory itemsSummary projection and schemaVersion1; full current outreach context reused as a unit; correct provider-observation component hash (distinct from compiled projection digest); mandatory woo.couponSync and merged synthetic OAuth wrapping key map; shared canonical numeric Shopify identity; idempotent reconciliation of one existing offline Session rather than insertion of a second. Existing credentials/expiry and unrelated tenants are preserved; duplicates fail closed. Full worker startup markers replace dependency-only readiness for these paths. App failure diagnostics persist only whitelisted semantic type/code, never arbitrary HTML/messages/stacks.

### Validation Results

All six actual isolated local cases PASS, each in its own process:

| Scenario | Actual local run |
| --- | --- |
| RECOVERY-ARCH028-PAID-001 | system-test-20261113T165359276Z-741f099b |
| RECOVERY-ARCH028-PROMO-001 | system-test-20261113T165702675Z-03400ce0 |
| RECOVERY-ARCH028-PURCHASED-001 | system-test-20261113T170004480Z-84941c32 |
| RECOVERY-OUTREACH-001 | system-test-20261113T170331132Z-3b242e09 |
| RECOVERY-PROVIDER-FAILURE-001 | system-test-20261113T170509996Z-8db286e5 |
| MESSAGING-STATUS-001 | system-test-20261113T172407965Z-96ce4473 |

The first five ran `ad54844`; subsequent changes only correct merchant-emulator identity/reconcile the UI helper and add diagnostics. Numeric DB identity is byte-for-byte unchanged; the five cases do not call that UI helper, so their financial evidence is unaffected. Final status ran `5a1ed06`. Its diagnostic-only pre-cleanup snapshot hook changes no service/business behavior. Final source publication after that is documentation-only.

Final full serial validation: `node --test --test-concurrency=1` **583 tests / 581 pass / 2 intentional opt-in PostgreSQL/Redis smoke skips / 0 fail**, 128.3 seconds. All six integrated cases actually exercised those disposable data planes. `npm run lint` **PASS**, 331 JavaScript files plus source/test <=300 and index <=120 structure. `npm run validate:catalogue` **PASS**, 184 total / 81 implemented / 103 planned. `git diff --check` and changed-source/evidence privacy review **PASS**; only synthetic local credentials appear, no actual credentials/private snapshot/raw customer or operator transcript. Focused current-context/coupon37, observation/diagnostic23, final merchant singleton/auth21 tests passed and are included in the final full suite. Exact accepted Shared5.13.9 selector preflight reproduced old PROVIDER_DRIFT and selected corrected INITIAL/FOLLOW_UP hashes.

Exact accepted source/runtime identities:

- Background image revision `8add92e4633fa8c74a819f8fa3dab6e493442028`; source provenance commit `36acc5f7b88276b404dcb024275451cd7dcf56d4` has identical tree `1583ba76e1ad97d443ae86e6a5c088e25475732f`.
- Nested Database `6f42b71112efe7ac63654d55f41cd74ca569b1ae`; migration source provenance `f805897e78b41e21f0e959249909bddf3054c6c1` has identical tree `f3a687ca8249044804660989f8786cb2a82eb70a`. Accepted migrations passed in every actual run.
- App `653677f434dd832c01e189411844912496be6448`; Messaging `3b3d6b52e144bd6fb729112044b6b105c06d15aa`; exact tracked-source isolated build snapshots only.
- Nonpromotable image `moda-interact-background:correctness-8add92e4633f-compensation-host-js`, ID `sha256:d3c172a25d12192132209809bfc9a597eb5a744113b0df4e1b57154c61b7dfc1`, re-inspected unchanged. Durable manifest records source/lock/original+derived Dockerfile hashes and all1136 audited outputs.

Preservation/isolation: external coordinator-verified backup `moda-local-reconciliation-backup-20261113T145749Z` contains all original deltas. Prepared claim `82be96ffb523780ab52bb09be1c459942724c5fd`; exact canonical parent `moda-interact-workspace-task-ARCH-028-SYSTEM-TEST-002` and implementation `moda-interact-workspace.worktrees/ARCH-028-SYSTEM-TEST-002`; matching task branches synchronized by launcher. Original primary remains untouched. No live provider/customer mutation.

### Deviations

Both durable task amendments implemented: bounded queue-idle30s correction with slow-probe/timeout regressions, and exact-current-source nonpromotable correctness-image fallback. Original default production Docker build failed V8 heap OOM134 before business assertions; a known failed3072MiB override was not repeated. Host Node24.19.0/locked TypeScript6.0.2 and Shared5.13.9 compile audited JS/maps/fixed JPEG only; Linux Node22.23.5 x64 dependencies/Prisma/runtime remain unchanged. Wrong pins fail closed. This proves business runtime behavior, **not production Docker-build parity**. No production image promotion.

Earlier failures (queue bound, itemsSummary, mandatory startup policy, missing context, provider hash and merchant session identity) remain explicit failures in the durable evidence narrative. Exact App diagnosis was ShopifyOfflineTokenError/SESSION_IDENTITY_CONFLICT; only the owned fixture was fixed. No failed receipt is counted as PASS.

### Assumptions

Coordinator retains the verified complete external backup. Accepted source-tree equivalence stated above was checked directly.

### Unresolved Issues

No unresolved implementation/acceptance defect within this bounded task. Production Docker-build parity remains unverified because of the recorded default-build memory failure. Full original ARCH-028 certification, other credit disposition classes and deployed/live acceptance remain OPEN and are not prerequisites claimed complete by this task.

### Architectural Concerns

No application source defect found; strict current contracts exposed stale test prerequisites. Owner did not merge main, publish Shared or alter architecture/frontier/index/gitlinks. Return to architect for formal acceptance and root-owned integration.

## Architect Review

### Review Status

Pending

### Review Notes

None

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

Original broad SYSTEM001 certification and live production acceptance remain separate.
