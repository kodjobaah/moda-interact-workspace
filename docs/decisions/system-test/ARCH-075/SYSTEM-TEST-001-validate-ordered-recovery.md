---
id: ARCH-075-SYSTEM-TEST-001
architecture_id: ARCH-075
title: Validate ordered recovery delivery across worker restarts
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
claimed_at: 2026-11-13T05:35:26Z
attempt: 1
depends_on:
  - ARCH-075-BACKGROUND-004
  - ARCH-075-ADMIN-004
  - ARCH-075-ADMIN-003
  - ARCH-075-BACKGROUND-003
  - ARCH-075-SHARED-003
  - ARCH-075-SHARED-004
  - ARCH-075-ADMIN-001
  - ARCH-075-ADMIN-002
  - ARCH-075-DATABASE-001
  - ARCH-075-SHARED-001
  - ARCH-075-SHARED-002
  - ARCH-075-BACKGROUND-001
  - ARCH-075-BACKGROUND-002
enables: []
created: 2026-11-13
updated: 2026-11-13
---

# Validate ordered recovery delivery across worker restarts

## Architecture

ARCH-075; docs/architecture/ARCH-075-ordered-recovery-message-layout.md; coordinator moda_architect. Read all frozen contract constants and lifecycle decisions before implementation.

## Objective

Validate ordered recovery delivery across worker restarts.

## Context

User requests logo/shop details before a distinct product image and checkout footer. Existing single-provider-id response cannot safely loop multiple sends. This task owns one bounded prerequisite capability; preserve completed prior behavior.

## Scope

Terminal independent integrated fixtures/validation only after all dependencies accepted and developer manual checkpoint; actual PostgreSQL/Redis with provider simulator.

## Out of Scope

Other repositories/tasks, source main merges/deployment, production sends/replays/resets, billing/usage/cap changes, provider credentials/permissions, unsupported exactly-once assumptions, unbounded fanout/retries, unrelated refactors. Return actual cross-owner gaps.

## Requirements

Also prove common editable Admin revision custom header/footer parity across compiled approved Meta projection and actual AI/HUMAN runtime receipts, checkout-last/opt-out preservation, stale common reference/activation refusal and legacy frozen compatibility. Never send freeform product tail outside the valid customer window.

Exercise real accepted contracts/migration/worker producer+status queue+part engine, ordered2/3 sends, quoted eachpart, exactfooter, one logical usage, callbackbeforeACK/readbefore-delivered, process death/restart, unknown/no prefix resend and takeovercancel. Validate legacy compatibility and absence of customer/secret telemetry. No source implementation, paid service or unauthorized live send. This terminal test never gates unfinished implementation tasks.

### Bounded accepted localized-command followup

Retain the completed thirteen integrated checks and same original claim. Before final acceptance, independently validate accepted Background merge c5dad158175733849fb6f9ab6ff2e89841d195cf: exact STOPP, DUR, PARAR and STOPPA must reach the real opt-out priority/durable CUSTOMER_STOP path and suppress an unadmitted ordered tail; demonstrate no ordinary model/provider response, plus sentence/substrings/nontext negatives. Existing full proof remains valid for unchanged code; record the delta rather than claiming its earlier image contained new aliases.

A separate temporary derivative of the approved correctness image may replace only compiler-emitted changed phone.js/source-map (and matching source provenance) from the exact accepted source with the locked TypeScript/options. Record base/derived image IDs, source commit and old/new module hashes, and verify other runtime modules/dependencies/ENV/CMD remain unchanged. No handwritten JavaScript regex substitution, dependency rebuild, production artifact promotion or broader resource change. If additional emitted runtime modules differ unexpectedly, return the evidence before broadening the overlay. Same-attempt continuation is authorized; no claim reset/reprepare. Owner updates in-progress/report fields while preserving earlier proof.

## Work Items

- [x] Implement only assigned capability and document compatibility.
- [x] Complete meaningful required checks and regression/negative evidence.
- [x] Publish mirrored branch/report and return review, then stop.

## Interfaces / Contracts

Use canonical ARCH075 frozen decisions. Shared owns ordered schema/digest and existing perpart media exports; Database owns durable child/status identity; Background owns provider/current authorization and logical aggregation. Never duplicate validators or fabricate product/provider identity.

## Dependencies

ARCH-075-DATABASE-001; ARCH-075-SHARED-001; ARCH-075-SHARED-002; ARCH-075-SHARED-003; ARCH-075-SHARED-004; ARCH-075-ADMIN-001; ARCH-075-ADMIN-002; ARCH-075-ADMIN-003; ARCH-075-BACKGROUND-001; ARCH-075-BACKGROUND-002; ARCH-075-BACKGROUND-003.

The developer manual checkpoint is satisfied. Independent disposable integrated fixtures may run while live translation review/provider approval is pending; simulator validation does not claim live activation or delivery.

## Enables

Only dependent tasks after architect acceptance; never begin them implicitly.

## Acceptance Criteria

- [x] Assigned bounded capability and frozen contract behavior satisfied.
- [x] Legacy reads/records remain compatible; no unauthorized cross-owner/billing/security change.
- [x] Durable/contract identity and fault cases satisfy required checks without silent fallback.
- [x] Canonical dedicated mirrored worktree, synchronization and recursive evidence recorded; no private proof committed.

## Validation

- [x] Deterministic integrated realPG/Redis/worker provider-fault scenarios and independently recorded accepted revision/package/migration evidence.
- [x] Isolation/privacy checks and report measured outcomes/limits; no genuine production send unless separately authorized.
- [x] Diff/privacy hygiene and report actual results, no production sends or secrets.

## Stop Condition

After required work and validation, set review, submit Completion Report and STOP. No main merge/deploy or enabled task execution.

## Implementation Notes

Admin004 is now Accepted; preserve this same active claim and independent fixture progress. Root merged corrected Admin source c765be827cd6086157d38060ab5a200745b25052; validate that accepted revision before final completion. No reset or re-claim is authorized.

You are not alone. Preserve others' edits and canonical prepared isolation. Root owns final merges/deployment. Architecture constants resolve inter-agent assumptions; report genuine gaps before expanding scope.

### Bounded test build-resource accommodation

The exact pinned Background Docker build encountered a V8 heap exhaustion (exit 134) during TypeScript compilation. A reversible test-only Dockerfile overlay is authorized: derive from the exact pinned Dockerfile and change only `RUN npm run build` to `RUN NODE_OPTIONS=--max-old-space-size=3072 npm run build`. Keep Node base, lockfiles, source/submodule bytes, runtime ENV and CMD unchanged; do not persist NODE_OPTIONS or change Docker host resource settings. Record the initial failure, exact one-line overlay diff/hash and resulting image identity. Verify the resulting runtime environment has no heap override. This supports integrated correctness under adjusted build resources, not byte-identical production-image or production build-memory parity. If the bounded increase fails, return evidence before further changes; do not invent a source correction.

### Host-compiled correctness-image fallback

The bounded 3072 MiB compiler override also exhausted Docker build resources. Further memory/VM changes are not authorized. For integrated correctness only, compile exact pinned source and lockfile with its declared TypeScript 6.0.2 ES2022/NodeNext commands under observed host Node24.19, then copy only audited dist/dist-cli JavaScript, source maps and declared fixed JPEG assets into a test image. Retain exact pinned Node22.23.5 base and its own Linux npm dependencies, Prisma generation/binary, sharp, observability/scripts/assets/database, runtime ENV and CMD. Never copy host node_modules, generated Prisma clients/native binaries, credentials, environment files, symlinks or arbitrary config. Runtime NODE_OPTIONS must be absent.

Record source/database commits, compiler and host/runtime versions, exact base digest, overlay diff and output allowlist hashes/sizes, published Shared integrity and both failed Docker build diagnostics. Execute tests inside the actual Node22 runtime. This validates source-derived runtime behavior under adjusted test build mechanics; it does not prove production Docker build reproducibility or host/runtime build parity and must not produce/promote a production artifact. Any actual incompatible output returns as evidence, not normalization or source changes.

## Completion Report

### Status

Ready for Review. Independent disposable integrated proof only; no production
activation or live provider-delivery claim. Implementation draft PR:
https://github.com/kodjobaah/moda-interact-system-test/pull/6

### Files Changed

Implementation `f11bf99d2c082ac407dc533db81f4b378f76bd3f` on mirrored branch
`task/ARCH-075-SYSTEM-TEST-001` (earlier partial checkpoint `806f251`).

- `src/harness/ordered-recovery/`: independent actual Admin compiler/activation,
  verified product/HUMAN preparation, local provider, real worker process,
  fault scenarios, migration proof and bounded correctness-image helpers.
- `scripts/validate-ordered-recovery.js`,
  `scripts/build-ordered-correctness-image.js` and capability package scripts.
- Opt-in approved build-heap option in the existing image helper; focused tests.
- Three `test/harness/ordered-*.test.js` files; validation guide and evidence
  under `docs/validation/ordered-recovery*.md`.
- Only this parent task report changed; no implementation submodule gitlink,
  domain index, architecture, other task, policy or rollup independently staged.

### Work Completed

Prepared canonical isolated implementation/parent worktrees and original claim
were reused. Start packet claim `9d1b0c346a17b9cbdc9175623f180b4cd5a99272`,
attempt 1, executor codex; no reprepare/reclaim or branch rewriting.
Final self-review preserved the existing image helper's original default result
shape; only opt-in heap builds add overlay metadata (final compatibility commit
`f11bf99`, integrated implementation `9f4045f`). The parent
branch was subsequently fast-forwarded to accepted `origin/main` at
`ff66c06e2d990047eb2ed3c482691356026b4d52`; implementation main was unchanged.

Exact accepted inputs: Background `d7a9bd1b0d1cceb908dd8ee23942dc93a9cf0417`,
database `a9b6ab852a8245dfd14447808aac288a23b113d0`, corrected Admin source
`d63ba84cca54732c776e9c1be7d5ff4f11c52f34` / accepted merge
`c765be827cd6086157d38060ab5a200745b25052`, public Shared 5.13.9 and its locked
SRI (recorded in implementation evidence). Admin004 was accepted before the
integrated run; no dependency gate was bypassed.

The actual accepted AI/HUMAN preparation/delivery services, PostgreSQL final
fences, multipart engine, Redis BullMQ status/continuation consumer and repair
run with deterministic verified product fixtures and a local HTTP provider.
The worker factory is real; unrelated external-provider pollers are excluded.
Common editable Admin source and compiled synthetic-approved Meta projection
share the custom header/footer used by actual AI/HUMAN receipts. Logo and
product images remain separate; the checkout URL is last without truncation.

### Validation Results

Final capability run: **12 delivery/fault/legacy scenarios plus one telemetry
check**, 13 integrated checks total, all passed. Recorded execution:
2026-11-13T06:23:59.845Z through 2026-11-13T06:28:43.352Z.

- Two/three-part logo/product/answer layout; complete authored text; exact footer.
- Actual HUMAN preparation/claim and one command completion with authored whitespace.
- HTTP ACK gate, READ-before-ACK, duplicate/out-of-order status monotonicity;
  sender-bound physical part quote lookup, one logical automated usage and
  product-context revision despite duplicate continuation.
- Actual worker process death/restart resumes only tail; uncertain transport is
  not replayed after repair/restart; definitive failure retains accepted prefix.
- Takeover, stale common source, CUSTOMER_STOP and expired verified customer
  window cancel unsent tails; no freeform product tail escapes its window.
- Legacy v1 frozen record sends once with its original layout.
- Captured application telemetry excludes authored answers, recipients, checkout
  URLs and synthetic credentials; Meta contact response identifiers are redacted.

Separate actual Admin fixture assertions passed: twenty synthetic APPROVED locale
targets atomically switched, custom source/Meta checkout-last and opt-out preserved,
stale preview rejected without writes, replay/audit stable and original snapshots
unchanged. Synthetic approval is not a live Meta approval claim.

All **77 owning migrations** finished on disposable PostgreSQL and matched the
image's exact migration.sql SHA-256 ledger, including
`20261113004310_arch075_ordered_delivery_parts` checksum
`1693a27606d6e661369cc76fbb8a71ab98da44c8aab510602e7038014352adb8`.
Actual container-installed versions independently read: Shared 5.13.9,
Prisma 6.19.3 and TypeScript 6.0.2.

Agent-owned checks passed:

- `npm run validate:recovery:ordered -- --image-manifest <local-manifest> --admin-root <accepted-admin-worktree>`.
- `node --test test/harness/ordered-*.test.js test/harness/background-production-image.test.js`: **10 passed**, zero failures/skips.
- Neighboring image/runtime/container plus ordered harness regression command:
  `node --test test/harness/background-*.test.js test/harness/ordered-*.test.js`: **18 passed**, zero failures/skips (includes the ten focused tests).
- `npm run typecheck`: 265 JavaScript files parsed; syntax rechecked after the
  default image-metadata compatibility refinement.
- `npm run lint`: syntax and source/test 300-line/module structure passed.
- `npm run validate:catalogue` and `git diff --check`: passed.
- Actual Node22 container parsed harness JS. Disposable PG/Redis/worker containers
  were cleaned; no deployed/shared service requests, live sends/replays or
  production counter/credential changes occurred.

### Deviations

Both exact production Docker compilation and the authorized 3072 MiB build-stage
only override exhausted local resources (exit 134 and Docker exit 102). The
architect-approved f00b01888 fallback compiled exact source/lock with locked
TypeScript 6.0.2, ES2022/NodeNext under host Node v24.19.0. Only audited JS/maps
and declared fixed JPEG outputs entered a separate Linux context; no host
node_modules, Prisma clients, native binaries, environment files or symlinks.

The final test image preserves its own Linux npm/Prisma/sharp and original runtime
ENV/CMD. Exact Node22.23.5 base digest, 1,130 allowed output hashes/sizes
(5,946,937 bytes), both failed-build diagnostics and original/derived Dockerfile
hashes are recorded. Actual runtime NODE_OPTIONS is absent. Image identity:
`sha256:18f6133e6f745619557d3c5e52b4d724ab5e9287fb14555ac93f7d2e029f6aad`.

This validates source-derived runtime correctness under adjusted test build
mechanics, **not** production build reproducibility, build-memory performance or
Node24-to-Node22 build parity. The image must never be promoted.

### Assumptions

Verified product facts/media metadata, provider approvals and customer data are
explicit disposable fixtures. Model execution, signed ingress, full entrypoint
readiness, real R2 image processing, translation quality and live Meta delivery
are outside this boundary and not claimed. Root separately owns live verification.

### Unresolved Issues

No integrated implementation defect remains. Initial failures were bounded build
resources or fixture packaging / missing linked Shopify customer / no-contact
consistency setup; those fixtures were corrected without relaxing production
validators, database constraints or source-owner code. Production Docker build
parity remains an explicit approved proof limitation, not a passing result.

### Architectural Concerns

No source implementation changes in other repositories, duplicated production
validators, billing/security bypass or unsupported exactly-once claim. Raw local
artifacts stay ignored; committed evidence is sanitized. Review is requested only
for the bounded independent proof described above; no main merge or deployment
was performed by this task.

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
