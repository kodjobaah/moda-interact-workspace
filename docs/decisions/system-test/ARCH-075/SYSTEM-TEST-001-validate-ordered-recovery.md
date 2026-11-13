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
status: complete
priority: 10
executor: codex
claimed_at: 2026-11-13T05:35:26Z
attempt: 1
depends_on:
  - ARCH-075-BACKGROUND-006
  - ARCH-075-ADMIN-005
  - ARCH-075-BACKGROUND-005
  - ARCH-075-GATEWAY-001
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

### Final Meta-readiness prerequisite reconciliation

Admin005, Background005 and Gateway001 are Accepted. Preserve the same claim and all prior thirteen integrated checks plus four localized-command/eight-negative followup proof. Before terminal acceptance append one bounded independent disposable flow using accepted Admin merge e52ecdb373a526f07710ecabfb7b3cefabab5018 and Background merge 2ae1eeec611cefb6dc68a3c733133d5201820525: actual confirmed all20 Meta snapshots record English review without changing hashes/registrations; exact missing-app preclaim block recovers through the operator domain method after synthetic trusted configuration repair, then unchanged ordinary claim can acquire durable creation intent. Prove an uncertain/intent-bearing registration still refuses and existing identical confirmation is idempotent. Use no real provider or deployment configuration. Reuse accepted Gateway structural evidence and identify actual messaging worker ownership; do not claim external fleet inspection from a synthetic proof reference.

A bounded temporary runtime overlay may add only freshly compiler-emitted preclaim-recovery.js/map from exact accepted source to the previous alias correctness image, after proving other runtime modules/dependencies/ENV/CMD unchanged. Record base/derived identities, source/compiler/module hashes and this non-production image limit. Admin fixture bundles exact accepted Admin source. No broader rebuild/rerun solely to duplicate unchanged prior scenarios. Return any additional source divergence before widening scope. Architecture remains In Progress pending root-owned live provider approval, coordinated activation and genuine delivery proof.

### Final strict keyed provider delta

Background006 is Accepted and merged at 8599f505c8da84a49db89f52637ebf387c317cea. Preserve the same claim and all earlier integrated, localized-command and Meta-readiness proof. Add only bounded independent actual Node22 builder/codec evidence against this exact source: keyed Batch JSONL has SDK-derived strict schemaVersion1/segments/key/text, required fields, additionalProperties:false and existing bounds; ordinary translation has no added format; actual strict restoration rejects input-only protectedTokens/context/unknown fields and retains valid marker identity. No live OpenAI/Meta request or broad rerun is required.

A temporary derivative may replace only compiler-emitted translation.provider.js, segment-codec.js and their source maps from the exact accepted source under the approved locked compiler/options. Verify all other runtime outputs/dependencies/ENV/CMD unchanged, retain prior base/new image/module manifest identities and no production-build parity/promotion claim. Return unexpected divergence before expanding. Root separately owns normal UI translation retry and semantic review after deploy.

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

Ready for Review — strict keyed provider delta passed; all earlier proofs retained.
Independent disposable integrated proof only; no production
activation or live provider-delivery claim. Implementation draft PR:
https://github.com/kodjobaah/moda-interact-system-test/pull/6

### Files Changed

Baseline implementation `f11bf99d2c082ac407dc533db81f4b378f76bd3f` on mirrored branch
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

### Accepted localized-command followup

Current combined implementation head:
`ee5bc22dc92d7c644bf146ccedbcee8e00c33583` (same draft PR #6 and mirrored task
branch). The preceding thirteen-check proof remains against its original d7a9bd1
source/image; it is not relabeled as containing the newly accepted aliases.
This bounded same-attempt continuation follows amendment a6fb84ca5 and accepted
Background merge `c5dad158175733849fb6f9ab6ff2e89841d195cf`; original claim
`9d1b0c346a17b9cbdc9175623f180b4cd5a99272` and attempt 1 remain unchanged.

Final current-source run **passed four aliases and eight strict negative
boundaries**, 2026-11-13T08:55:33.046Z through 2026-11-13T09:03:44.229Z:

- Exact `STOPP`, `DUR`, `PARAR`, `STOPPA` traverse canonical Shared-validated
  message-received Redis jobs and the real inbound worker/priority opt-out path.
  All take priority over an actually saturated `RAW_SENDER` limiter, commit durable
  CUSTOMER_STOP reason/timestamp/revision and one support notice each, and cancel
  their already prepared but unadmitted ordered tail.
- `Please STOPP`, `DURING`, `PARAR now`, `STOPPABLE`, `STOPPA123`, `PARAR?`, audio
  media named STOPP and unsupported type named STOPPA remain non-STOP boundaries.
  No-contact fields/notices stay unchanged, their ordinary path stops at the real
  limiter, and their ordered tail still sends following a delivery callback.
- No ordinary inbound persistence, model-turn job or ordinary provider reply
  occurs. The intentionally prepared prefix/tails use only the local HTTP
  simulator. Exactly four real worker STOP records/notices are observed.
- Telemetry hygiene passes over 315,924 captured bytes (37 forbidden-value
  checks). Disposable PostgreSQL/Redis/worker containers were cleaned.
- The fresh delta session again verifies all 77 owning migration checksums.
- `node --test test/harness/background-*.test.js test/harness/ordered-*.test.js test/harness/recovery-optout-image.test.js`:
  **19 passed**, zero failures/skips (includes the prior eighteen).
  Syntax/structure checks pass for 271 JavaScript files; catalogue and diff checks
  pass. New source/test helpers remain below the 300-line module limit.

Exact current source was freshly compiled with locked/installed TypeScript 6.0.2,
declared ES2022/NodeNext commands and host Node v24.19.0. Across 1,130 audited
outputs, only compiler-emitted phone.js and its map differ; every other 1,128
output matches. Full package/lockfile and both tsconfig hashes match the base.
Old/new module hashes, matching source hash and COPY-only Dockerfile hash are in
`docs/validation/recovery-opt-out-evidence.md` and the local manifest.

Base correctness image:
`sha256:18f6133e6f745619557d3c5e52b4d724ab5e9287fb14555ac93f7d2e029f6aad`.
Final immutable derivative used for every Docker invocation in the measured run:
`sha256:f1ff2479d5b1f35a85921be15d206709707b5f7d53902a1efd0915c864584c5e`.
Only the emitted phone.js/map and matching accepted TypeScript source are copied.
Original dependency layers, runtime ENV/CMD/entrypoint and Node22.23.5 remain;
NODE_OPTIONS is absent. All actual derived runtime outputs were independently
hashed inside Linux and match the current compiler manifest. No handwritten
JavaScript regex replacement, dependency rebuild, host/VM resource change or
production artifact promotion occurred.

The validator pins immutable image IDs. A preliminary tag-based run was not used
as final artifact-identity proof because a cached COPY rebuild changed image
metadata while leaving identical audited runtime bytes; the bounded delta was
repeated under the final immutable ID. No repetition of the unchanged original
thirteen checks was claimed or required. This is still source-derived local
correctness, not production-build reproducibility, signed ingress, real model /
R2 / Meta behavior, full entrypoint readiness, live activation or delivery.
No cross-owner implementation defect remains; no live request, send, replay,
production counter/credential update or merge into main was performed.

### Accepted Meta-readiness prerequisite reconciliation

Implementation `bcf1a0f8d84c3d6ae0430b224389d867b4ce66e9` pushed on the same branch.
Same attempt/claim; parent synchronized to accepted unified main
`37af6a8b992f4cac17a73087e9b16ba13a511a4c`. Admin
`e52ecdb373a526f07710ecabfb7b3cefabab5018`, Background
`2ae1eeec611cefb6dc68a3c733133d5201820525`, Gateway
`1e27ec51fea7709ad9cd8700bce10b5d5d720cd6`; Database remains `a9b6ab8`.

Bounded disposable real-PostgreSQL proof passed
2026-11-13T10:01:13.141Z–10:02:13.732Z. Actual Admin confirmation reused
20 identical immutable registrations, explicitly recorded English REVIEWED,
and replayed without another review audit/timestamp or changed hashes.
Actual Background submission service/Graph adapter produced 20 missing-app
preclaim BLOCKED records before any provider request/CREATE_INTENT. With
synthetic trusted configuration repair, actual operator recovery dry run changed
no rows; a historical intent negative refused atomically. Apply recovered all 20,
replay reported all 20 already applied, and exactly 20 recovery audits remained.
Unchanged ordinary repository claims wrote 20 durable CREATE_INTENT, refused
repeated claims, and recovery refused uncertain submitting/intent-bearing rows.
Zero provider requests/POST_INTENT; frozen snapshots unchanged. All 77 migrations
finished with matching checksums; the disposable database was cleaned.

The first fixture attempt hit the actual INITIAL-language semantics guard with
synthetic English text marked Chinese. The final test uses the existing
FOLLOW_UP fixture pattern; no guard/source validator was changed, and no
translation-quality claim is made. Gateway accepted Blueprint/ten focused
negative checks are reused, not rerun. Messaging workers own the actual Meta
poller; the operator reference is synthetic and is NOT live fleet verification.

Approved overlay adds ONLY newly compiler-emitted preclaim-recovery.js/map.
All 1,130 previous runtime outputs, whole package/lock/tsconfigs, Linux dependency
layers and ENV/CMD/entrypoint are unchanged. Exact TS6.0.2/host24.19 build,
actual Node22.23.5 runtime, NODE_OPTIONS absent. Final immutable image used for
all Docker validation operations:
`sha256:a247ea1ac436bee9b09a3b1779eee70e3fcbcc2ddbf8572bc6249168b8aa235b`.
Detailed hashes and evidence are in
`docs/validation/meta-readiness-evidence.md`; private local manifest
`/tmp/moda-readiness-image.json` and run log `/tmp/moda-readiness-run.log`.
This is source-derived runtime/domain correctness, NOT production-image/build
parity, CLI/fleet validation, provider approval, activation or live delivery.

New capability scripts `validate:meta:readiness` / `build:meta:readiness-image`,
bounded fixtures, output-allowlist test and documentation are task-owned only.
Combined neighboring Node regression selection: **20 passed**, zero failures/
skips (one new overlay test); earlier narrower selection 8 passed. Domain all 20
assertions are not counted as twenty Node test cases. Syntax 276 files, structure,
catalogue and diff checks pass. Original 13 proof and 4 alias / 8 negative proof remain
unchanged and were not broadly rerun. No owning source edit, live action, main
merge, credential/config/counter change or production-verification claim.

### Accepted strict keyed provider final delta

Implementation `62f746b2c4e585b3675229ebc139479af22800ca` on the same
mirrored task branch. Same claim/attempt; parent accepted main
`2e4712748161d4965051531838452b16d12a1a6f` merged normally, requirements
amendment7722b03d2 preserved, exact Background source
`8599f505c8da84a49db89f52637ebf387c317cea` freshly compiled. No owning
application source was edited.

**Actual Node22 bounded builder/codec proof passed**
2026-11-13T10:33:25.279Z–10:33:27.319Z, Docker networking disabled. Actual
keyed Batch JSONL contains the SDK-derived strict schemaVersion1/segments/key/
text shape, required fields, additionalProperties:false and existing bounds.
Ordinary translation has no added format and retains configured model/custom ID
and output bound. Valid marker identity restores; six root/segment extra
protectedTokens/context/unknown-field cases and a missing marker strictly refuse.
Zero provider API requests, no worker/database/poller. These are runtime
assertions, not additional Node test cases. No real translation-quality or
live provider/fleet/activation claim.

Approved derivative changes exactly four compiler-emitted translation.provider.js,
segment-codec.js/maps; every other **1,128 runtime output** stays identical.
Whole package/lock/tsconfigs, Linux dependencies/layers and ENV/CMD/entrypoint
match; TS6.0.2/host24.19 declared compile, actual Node22.23.5, NODE_OPTIONS absent.
Base readiness image `sha256:a247ea1ac436bee9b09a3b1779eee70e3fcbcc2ddbf8572bc6249168b8aa235b`;
final immutable validation image
`sha256:dd73ff316ac7eb7b6c335291163a27e673968b94392784c2afbbb50fe75fd319`.
Full source/old-new module hashes and Dockerfile identity are in
`docs/validation/keyed-translation-evidence.md`; local manifest
`/tmp/moda-keyed-image.json`, runtime log `/tmp/moda-keyed-runtime.log`.
No host native/dependency/config/credential/CLI copies or production artifact
promotion; source-derived correctness only, no production-build parity claim.

Preparation refused absent output before compilation completed and an unsupported
bare-local-SHA Docker FROM reference. Final build uses a local base tag verified
to its exact immutable ID, audits inherited layers/output hashes afterward, and
all runtime proof commands pin the derived immutable ID. No partial output was
accepted. Final bounded actual build/proof passes.

Neighboring regression tests: **21 passed**, zero failures/skips; new output guard
also passed alone. Syntax281 JS files, structure/catalogue/diff checks pass;
final base-tag identity check additionally passes node --check and actual build.
Capability scripts `validate:translation:keyed` / `build:translation:keyed-image`
and small task-owned helpers/docs added. Prior 13 integrated checks, 4 aliases /
8 negatives and all20 Meta-readiness assertions remain preserved with their
recorded source/image; no broad integrated rerun, live call, main merge or
production setting/counter change was performed. No implementation defect remains
within this bounded validation task; root owns remaining genuine rollout proof.

## Architect Review

### Review Status

Accepted

### Review Notes

Accepted exact implementation `62f746b2c4e585b3675229ebc139479af22800ca` and mirrored final report `0153642d3240a6c5b25bb11c7a84c9abea171bae`. Independently inspected actual harness, provider simulator, worker factory, assertions, image provenance and all same-claim deltas. Every explicit implementation/publication/configuration dependency is Complete. This accepts independent disposable runtime correctness; it does not complete the live architecture.

### Reviewed Files

Ordered recovery session/driver/modules, AI/HUMAN producer adapters, real BullMQ worker/repair, happy/fault/legacy scenarios, provider/telemetry checks, Admin fixture and migration ledger proof; localized consent runtime/image overlay; Meta readiness Admin/Background fixture and image audit; final keyed provider/codec runtime and image audit; focused harness tests and measured evidence guides.

### Validation Reviewed

Thirteen integrated delivery/fault/telemetry checks, four actual localized-command worker cases and eight negatives, actual Admin/common projection/atomic activation fixture, twenty-registration English-review/block/recovery/replay/claim readiness proof, and all77 owning migration checksums passed. Final exact Node22 networking-disabled strict provider/codec proof passed; 21 neighboring Node regressions plus syntax281, structure, catalogue and diff checks passed. Same original claim, canonical matching worktrees, start synchronization/recursive evidence and accepted source identities reviewed. No broad rerun is claimed for bounded later deltas.

### Architecture Conformance

Real accepted database/Redis/BullMQ/preparation/final-fence modules establish ordered2/3 parts, per-part footer and sender identity, one logical usage/context update, ACK-vs-delivery gating, callback-before-ACK/restart/uncertainty/takeover/STOP/window behavior and legacy compatibility. Exact immutable source manifests bind compiler-derived Node22 overlays and unchanged dependency/runtime outputs. Original Docker builds exhausted resources; approved host-compiled correctness images explicitly do not prove production build reproducibility or Node24-to-22 build parity and cannot be promoted. Synthetic model facts/media/approvals and worker references are not live provider, ingress, R2, fleet or semantic translation evidence. No production calls, owner-source changes or weakened guards.

### Follow-up

Root owns source merge and final parent gitlink integration. Architecture remains In Progress until live reviewed catalogue/provider approvals, correct environment copy/callback routing, coordinated common activation and genuine ordered WhatsApp delivery are verified. Preserve all protected operational evidence outside public docs. Test-only images must never be deployed. No further system task or speculative rerun is required absent a new concrete source/runtime issue.
