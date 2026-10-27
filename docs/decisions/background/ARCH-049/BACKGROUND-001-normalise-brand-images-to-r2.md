---
id: ARCH-049-BACKGROUND-001
architecture_id: ARCH-049
title: Normalise trusted brand sources and upload verified R2 derivatives
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: complete
priority: 30
executor: null
claimed_at: null
attempt: 1
depends_on: ["ARCH-049-ADMIN-001"]
enables: ["ARCH-049-BACKGROUND-002"]
created: 2026-10-25
updated: 2026-10-27
---

# Normalise trusted brand sources and upload verified R2 derivatives

## Architecture

`ARCH-049` — `docs/architecture/ARCH-049-shopbrand-public-media-configuration.md`; coordinator `moda_architect`. This task was supplied as a portable definition and is now materialised in the canonical developer parent task worktree.

## Objective

Create one focused, injectable Background media-processor module that safely fetches one shop/role source, transforms it to a verified WhatsApp-compatible image, and writes an immutable object to the already-provisioned R2 bucket.

## Context

Do not build another bucket/proxy. Use validated `shopBrand.publicMedia` for bucket name/public origin, and separate worker-only R2 credentials. The source URL is untrusted even when Shopify or Woo supplied it. This is a pure media-transform-and-R2-writer module: its input is provided by callers, and it does not read/write ShopBrand or its JSONB schema. Consequently DATABASE-001 is not an implementation prerequisite; BG002 owns the later durable DB integration.

## Scope

- Create `src/services/shop-brand-media/` with separate safe-fetch, transformer, metadata verifier, R2 writer and service interfaces; reuse the existing Background network policy and S3 client mechanisms where compatible.
- Teach the existing Background platform configuration reader to consume `shopBrand.publicMedia` independently from `merchant.knowledge.r2`.
- Use the current Cloudflare custom-domain/bucket, write immutable content-addressed keys and verify a direct public JPEG/PNG URL.
- Implement bounded media and security tests using injected dependencies; no BullMQ worker or brand source update in this task.

## Out of Scope

- Provider Shopify/Woo source retrieval, ShopBrand state machine/leases, incoming webhook/API endpoints, WordPress access, ARCH-047 template sending/Meta sample submission, Gateway Blueprint or Cloudflare infrastructure creation.

## Requirements

### R1. Owned module and API

```typescript
interface ShopBrandMediaProcessor {
  process(input: {
    shopId: string;
    role: 'LOGO' | 'SQUARE_LOGO' | 'COVER_IMAGE';
    sourceUrl: string;
    sourceFingerprint: string;
    sourceGeneration: number;
  }): Promise<{
    objectKey: string;
    contentType: 'image/jpeg' | 'image/png';
    width: number;
    height: number;
    sizeBytes: number;
    contentSha256: string;
    sourceFingerprint: string;
    sourceGeneration: number;
  }>;
}
```

Inject `SafeFetcher`, `ImageTransformer`, `R2ObjectWriter` and public-url probe; do not import ShopBrand business workflow orchestration into the image transformer. Typed errors must distinguish permanent unsupported/unsafe inputs from transient provider/R2 failures.

### R2. Exact security and output policy

Require HTTPS, no credentials in URL, max 3 redirects, 10-second total fetch, 10 MiB input and 40 MP decoded-pixel cap. DNS-pin public IPv4/IPv6 addresses on every connection/redirect and reject metadata/private/loopback/link-local or DNS rebinding. Decode actual bytes; do not trust extensions or Content-Type. Strip EXIF/metadata. Fit/pad LOGO/SQUARE_LOGO without distortion; centre-crop COVER_IMAGE using explicit 1125×600 internal canvas policy. Produce JPEG (opaque RGB) or PNG (transparency where needed), under 5 MiB, target under 1 MiB where practical. Verify decoded output dimensions and digest after encoding. No arbitrary customer-provided URL.

### R3. R2 configuration and writes

Read `shopBrand.publicMedia` through the Background platform configuration reader, preserving Admin's default/no-write-on-read semantics. Worker-only environment settings are **exactly** `SHOPBRAND_R2_ENDPOINT`, `SHOPBRAND_R2_ACCESS_KEY_ID`, `SHOPBRAND_R2_SECRET_ACCESS_KEY`; missing/malformed values fail protected operations closed. Use S3-compatible `PutObjectCommand`/`HeadObjectCommand` or compatible existing adapters with the configured bucket. Key pattern: `shop-brands/<shopId>/<role-lowercase>/sha256-<64lowerhex>.<jpg|png>`; set immutable cache headers. Never put original images/private customer files in this public bucket. Store no secrets in logs or public URLs; `merchant.knowledge.r2` stays private and unchanged.

### R4. Public readiness prerequisite

Before returning verified metadata, prove the current custom HTTPS domain can serve test/output bytes with the expected content-type; do not accept the old screenshot's `Initializing` state as Active. If live R2/domain credentials aren't supplied in isolated test, validate via injected adapter and report the external preflight as outstanding; never claim public readiness was proven.

## Work Items

- [x] Implement processor and configuration consumer modules.
- [x] Add unit tests for transform output/headers/digest and safe fetch.
- [x] Add R2 adapter tests, missing-credentials tests and redaction tests.
- [x] Record bounded output and external-readiness validation results.

## Interfaces / Contracts

Consumes the caller-supplied source URL, shop/role, fingerprint and generation (BG002 will later read them from `commerce.ShopBrand`); returns verified derivative metadata without reading/mutating PostgreSQL or owning leases. Shares `shopBrand.publicMedia` read contract from accepted ARCH-049-ADMIN-001. The public URL is constructed only from the validated configured origin plus trusted, encoded immutable object key.

## Dependencies

- ARCH-049-ADMIN-001

## Enables

- ARCH-049-BACKGROUND-002

## Acceptance Criteria

- [x] Processor never writes ShopBrand state or performs per-send processing.
- [x] Malicious redirects, private IPs, oversized payload/pixels and malformed image bytes are rejected.
- [x] JPEG/PNG output has verified actual dimensions/hash and is under 5 MiB.
- [x] R2 object keys are immutable, idempotently reusable and isolated from private Merchant Knowledge storage.
- [x] Missing secure R2 credentials or unavailable custom-domain delivery fails closed.

## Validation

- [x] Focused unit tests for aspect-ratio/padding/cropping and PNG transparency.
- [x] Security tests including DNS rebinding, local/metadata/private hops, large payload and decompression.
- [x] R2 Put/Head/public-GET adapter tests and default platform config read.
- [x] ESLint/typecheck/focused test scripts actually present in Background package; `git diff --check` (see evidence below).

## Stop Condition

After the defined Work Items, Acceptance Criteria and Validation are complete, record the Completion Report and change task status to `review`; hand off to `moda_architect` and STOP. Do not continue into a dependent task or change an `_index.md`.

## Implementation Notes

All task work must use the canonical launcher-provided **dedicated parent and implementation worktrees**, synced task/<TASK_ID> branches and start-of-attempt evidence. Inspect the actual pinned package scripts, source and existing conventions before editing. Do not merge branches, push main, edit another repository, start an enabled task or change any `docs/decisions/**/_index.md`. Use structured logging via `@modainteract/moda-interact-shared/logging`; secrets and full untrusted URLs must not enter diagnostics. Document changed files, relevant test commands, results, security/tenant checks, commits and worktree evidence in the Completion Report.

No additional assumptions are authorised.

## Completion Report

### Status

Complete — Developer Attempt 1. The developer explicitly invoked `/moda_developer_update ARCH-049-BACKGROUND-001 complete` on 2026-10-27 after the durable passing Attempt 1 self-review. Implementation commit `75c93f5` is published to `origin/task/ARCH-049-BACKGROUND-001`; the passing review and completion decision are published on the parent task branch. No separate architect-specific file review is claimed.

### Files Changed

**Implementation repository (`moda-interact-background`): 20 files in commit `75c93f5`.**

- `package.json`
- `package-lock.json`
- `docs/arch049-shopbrand-media-processor.md`
- `src/services/platform-configuration/consumers.ts`
- `src/services/platform-configuration/contracts.ts`
- `src/services/platform-configuration/service.ts`
- `src/services/shop-brand-media/contracts.ts`
- `src/services/shop-brand-media/image-transformer.ts`
- `src/services/shop-brand-media/index.ts`
- `src/services/shop-brand-media/metadata-verifier.ts`
- `src/services/shop-brand-media/processor.ts`
- `src/services/shop-brand-media/public-probe.ts`
- `src/services/shop-brand-media/r2-config.ts`
- `src/services/shop-brand-media/r2-writer.ts`
- `src/services/shop-brand-media/safe-fetch.ts`
- `tests/unit/services/platform-configuration/service.test.ts`
- `tests/unit/services/shop-brand-media/image-transformer.test.ts`
- `tests/unit/services/shop-brand-media/processor.test.ts`
- `tests/unit/services/shop-brand-media/r2-writer.test.ts`
- `tests/unit/services/shop-brand-media/safe-fetch.test.ts`

**Parent workspace:** this task file only. The parent `moda-interact-background` submodule gitlink and shared indexes/architecture documents must not be staged by the task executor.

### Work Completed

- Implemented injectable `ShopBrandMediaProcessor` and typed, bounded error classifications. Inputs and outputs conform to the task's one-source/one-role contract; it neither imports the ShopBrand lifecycle nor reads/writes ShopBrand state.
- Implemented HTTPS-only fetching with public-destination DNS validation and pinned socket verification on each redirect, a single ten-second total deadline, three-redirect limit, and 10 MiB input cap. Disallowed response decompression and sensitive errors/URLs in logs.
- Implemented Sharp-based source decoding (maximum 40 MP), metadata stripping, 1125×600 cover-crop or logo fit/pad, transparent PNG/opaque JPEG output and independent re-decode/dimension/content hash verification. Outputs must be smaller than 5 MiB.
- Implemented dedicated Cloudflare R2 worker credential validation, immutable content-addressed keys, conditional S3-compatible writes, HEAD verification for identical reuse/concurrent write races and separate public HTTPS GET content-type/length/hash verification before emitting READY-eligible metadata.
- Added the `shopBrand.publicMedia` configuration reader and default-on-read (revision zero, no DB write) while preserving the separate private `merchant.knowledge.r2` configuration.
- Reused `@modainteract/moda-interact-shared/logging` for bounded semantic success/error events. Unexpected source/R2 exceptions are converted to safe, explicit failure codes and recorded without exposing provider exception messages or credentials.
- Added focused unit/security regression tests and operational preflight documentation. Assistant-authored Attempt 1/Attempt 2 patch files provided implementation assistance; the developer applied, corrected, validated, committed and pushed the final implementation.

### Validation Results

Developer terminal transcript: `typescript(20261027-115118)`, supplied alongside `moda-interact-workspace-ARCH-049-BACKGROUND-001.zip` (27 October 2026). The archive includes the resulting implementation and canonical parent task file; archive reconstruction is *not* proof of Git metadata beyond the supplied terminal log.

| Command / evidence | Result |
| --- | --- |
| `git submodule update --init --recursive -- database` and `ls database/prisma/schema.prisma` | **PASS**; nested database schema materialised, recorded gitlink `7cd7e955c8ede2ce76631ee40c655daba91bfdd6`. |
| `npm ci` | **PASS** in the developer's Background task worktree; earlier Attempt 1 lockfile error corrected. |
| `npm run prisma:generate` | **PASS**; Prisma Client v6.19.3 generated. |
| `npm test -- tests/unit/services/shop-brand-media tests/unit/services/platform-configuration/service.test.ts` | **PASS**; **5 test files, 53 tests passed, 0 failures** (13.92 s reported). Covers transform, SSRF/DNS, R2 race/failure, public delivery mismatch and config default-read cases. |
| `npm run lint` | **PASS**; ESLint exited without errors. |
| `npm run build` | **PASS**; Prisma generation and TypeScript `tsc` completed without reported errors. |
| `git diff --check` | **PASS in independent isolated reconstruction** of the uploaded 20-file implementation delta against the earlier snapshot, including the final developer lockfile. A separate `git show --check 75c93f5` in the actual implementation worktree is recommended to confirm the committed diff. |
| `git commit` and `git push --set-upstream origin task/ARCH-049-BACKGROUND-001` | **PASS**; implementation commit `75c93f5` pushed and upstream set, per terminal log. |
| Live Cloudflare R2 write and public custom-domain GET | **NOT RUN**; no live bucket/domain/worker-secret evidence supplied. R4 explicitly permits injected-adapter validation with external preflight outstanding. The implementation must fail closed until public bytes are provably served. |

### Deviations

None from the defined processor-only repository scope. The final solution includes the correction of Attempt 1's Sharp transitive-lockfile entry, lint-rejected regexes, and eager Prisma initialisation during tests. These corrections remained within **workflow Attempt 1**.

### Assumptions

The caller in later BG002 will supply authenticated provider-derived ShopBrand source metadata. This processor deliberately does not authenticate or discover the merchant's source itself. The external public R2 custom domain is **not assumed** to be operational; the implementation performs a real GET verification before reporting success when the production path is exercised.

### Unresolved Issues

- **External live readiness:** verify the existing Cloudflare custom domain is Active with minimum TLS 1.2 or newer; configure dedicated `SHOPBRAND_R2_*` worker secrets and prove a real upload plus public GET/content-type/hash before enabling production processing. This remains the explicit developer-owned R4 preflight and is **not claimed as tested**.
- At commit time the implementation branch had diverged from `origin/main` (one task commit versus seven newer mainline commits), as shown in the terminal log. The developer retains ownership of later synchronisation/integration; do not merge to `main` or stage a parent submodule pointer during this task handoff.
- The terminal-capture file named `typescript` remained untracked in the implementation worktree and was not included in the implementation commit. Do not stage it accidentally.

### Architectural Concerns

No new repository-boundary or data-model changes identified. `ARCH-049-BACKGROUND-002` retains the ShopBrand persistence/lease, source-acquisition and asynchronous job orchestration. No Background worker, database migration, cross-repository message contract, Gateway/Cloudflare infrastructure, or ARCH-047 template-send changes were introduced here.

**Task isolation evidence:** the existing Developer Execution Claim below documents launcher-resolved dedicated parent and Background implementation worktrees, both prepared from their own `origin/main` at the start of Attempt 1 after `fetch origin --prune`; the developer's terminal log independently shows validation and commit/push from the `task/ARCH-049-BACKGROUND-001` implementation worktree. The ZIP helper also identified and overlaid that implementation worktree. The original launcher preparation packet was not independently supplied with this submission.

## Developer Self-Review Passed (Attempt 1, 2026-10-27)

- Outcome: **passed**. The task-scoped processor requirements, Work Items and Acceptance Criteria are implemented in the published Background task branch; no required task work item is known incomplete.
- Source review: inspected the safe fetcher, processor, public probe and R2 writer. Redirects are bounded and re-resolved, destination addresses are validated and socket-pinned, response peer addresses are checked, output bytes are independently decoded and verified, object writes are immutable/content-addressed, and success metadata is withheld until a matching public HTTPS GET succeeds.
- Fresh validation in the canonical implementation worktree: `npm test -- tests/unit/services/shop-brand-media tests/unit/services/platform-configuration/service.test.ts` passed **5 files / 53 tests**; `npm run build` passed (Prisma Client generation and TypeScript compilation); `npm run lint` passed; `git show --check HEAD` passed.
- Implementation publication and isolation: canonical implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-049-BACKGROUND-001`, branch `task/ARCH-049-BACKGROUND-001`, is clean at `75c93f53f5b94b33dc1fc125f90e2fa4d314330b`, equal to `origin/task/ARCH-049-BACKGROUND-001`. Canonical parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-049-BACKGROUND-001` is registered on the matching task branch, clean before this review edit, and published at `66fc8bd9aa0d1231f27f00b4f2e95db887e47a89` before this record.
- `ARCH-049-ADMIN-001` is complete. `origin/main` is not an ancestor of the implementation task branch; no merge or push to `main` was performed. The recorded external live R2/custom-domain preflight remains outstanding as permitted by R4, and is not claimed as tested.
- Transition: retain `status: review`, `executor: null`, `claimed_at: null`, and `attempt: 1`. `completion_mode: developer` means architect review and the developer's explicit completion decision are still required. No enabled task was started or promoted.

## Developer Completion Decision (Attempt 1, 2026-10-27)

- Decision: the developer explicitly invoked `/moda_developer_update ARCH-049-BACKGROUND-001 complete` after the durable passing self-review.
- Accepted attempt: Attempt 1; `attempt` remains 1. The task is `status: complete`, `executor: null`, and `claimed_at: null`.
- Implementation publication: the canonical Background task branch remains clean and published at `75c93f53f5b94b33dc1fc125f90e2fa4d314330b`; no implementation changes were required for completion.
- Review scope: completion relies on the recorded developer self-review and explicit developer completion authority. No separate architect-specific review notes or live R2/custom-domain preflight are claimed.
- Dependency frontier: `ARCH-049-BACKGROUND-002` is now eligible (`ready`) because `ARCH-049-DATABASE-001` and this task are complete. `ARCH-049-SYSTEM-TEST-001` remains pending with other declared dependencies incomplete and remains manual-gated.
- Integration: neither task branch was merged to `main`. The shared checkout's unrelated dirty changes were left untouched.

## Developer Execution Ownership Amendment

- Date: 2026-10-27.
- The developer explicitly invoked `/moda_developer_create ARCH-049-BACKGROUND-001` for this ready agent-owned task. Execution and completion ownership are transferred to the developer (`execution_mode: developer`, `completion_mode: developer`) for this task lifecycle.
- Preserved logical ownership: `assigned_agent: moda_background`, `repository: moda-interact-background`, coordinator, task scope, dependencies, acceptance criteria and validation requirements are unchanged.
- Materialisation: this portable task definition was present in the shared workspace but had no canonical task worktree or task branch. It was materialised in `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-049-BACKGROUND-001` from parent `origin/main`; the matching Background implementation worktree was created from Background `origin/main`. The shared checkout was not edited.

## Developer Execution Claim (Attempt 1)

- Claim: `status: in_progress`, `executor: developer`, `claimed_at: 2026-10-27T10:17:51Z`, `attempt: 1`.
- Canonical launcher: `python3 scripts/start-agent-task.py ARCH-049-BACKGROUND-001 --route-only --json` from `/Users/kwadwoadomafriyie/project/moda-interact-workspace` resolved repository `moda-interact-background`, parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-049-BACKGROUND-001`, implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-049-BACKGROUND-001`, and branch `task/ARCH-049-BACKGROUND-001`.
- Dependency checked before claim: `ARCH-049-ADMIN-001` is `complete`. DATABASE-001 is not a dependency of this processor-only task, as stated in its context.
- Parent preparation: fetched `origin --prune`; no existing local/remote task branch or stale worktree registration existed. Created the canonical parent worktree from parent `origin/main` at `8956955d588ff34117c6fca73070017668b72ba9`; the worktree is clean before this claim edit.
- Implementation preparation: fetched `origin --prune`; no existing local/remote task branch or stale worktree registration existed. Created the canonical implementation worktree from Background `origin/main` at `caa415fe5743e16693da79da8ab5e81f3d09259f`; the worktree is clean. No implementation changes were made during preparation.
- No changes were made to the shared/default workspace checkout or unrelated untracked files.

## Architect Review

### Review Status

Not separately conducted. The developer's explicit completion decision follows the durable passing self-review; no separate architect-specific review notes are claimed.

### Review Notes

None.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Not reviewed.

### Follow-up

The external Cloudflare R2/custom-domain live readiness preflight remains outstanding as recorded in Unresolved Issues; it was not a task validation prerequisite under R4.
