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
status: in_progress
priority: 30
executor: developer
claimed_at: '2026-10-27T10:17:51Z'
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

- [ ] Implement processor and configuration consumer modules.
- [ ] Add unit tests for transform output/headers/digest and safe fetch.
- [ ] Add R2 adapter tests, missing-credentials tests and redaction tests.
- [ ] Record bounded output and external-readiness validation results.

## Interfaces / Contracts

Consumes the caller-supplied source URL, shop/role, fingerprint and generation (BG002 will later read them from `commerce.ShopBrand`); returns verified derivative metadata without reading/mutating PostgreSQL or owning leases. Shares `shopBrand.publicMedia` read contract from accepted ARCH-049-ADMIN-001. The public URL is constructed only from the validated configured origin plus trusted, encoded immutable object key.

## Dependencies

- ARCH-049-ADMIN-001

## Enables

- ARCH-049-BACKGROUND-002

## Acceptance Criteria

- [ ] Processor never writes ShopBrand state or performs per-send processing.
- [ ] Malicious redirects, private IPs, oversized payload/pixels and malformed image bytes are rejected.
- [ ] JPEG/PNG output has verified actual dimensions/hash and is under 5 MiB.
- [ ] R2 object keys are immutable, idempotently reusable and isolated from private Merchant Knowledge storage.
- [ ] Missing secure R2 credentials or unavailable custom-domain delivery fails closed.

## Validation

- [ ] Focused unit tests for aspect-ratio/padding/cropping and PNG transparency.
- [ ] Security tests including DNS rebinding, local/metadata/private hops, large payload and decompression.
- [ ] R2 Put/Head/public-GET adapter tests and default platform config read.
- [ ] ESLint/typecheck/focused test scripts actually present in Background package; `git diff --check`.

## Stop Condition

After the defined Work Items, Acceptance Criteria and Validation are complete, record the Completion Report and change task status to `review`; hand off to `moda_architect` and STOP. Do not continue into a dependent task or change an `_index.md`.

## Implementation Notes

All task work must use the canonical launcher-provided **dedicated parent and implementation worktrees**, synced task/<TASK_ID> branches and start-of-attempt evidence. Inspect the actual pinned package scripts, source and existing conventions before editing. Do not merge branches, push main, edit another repository, start an enabled task or change any `docs/decisions/**/_index.md`. Use structured logging via `@modainteract/moda-interact-shared/logging`; secrets and full untrusted URLs must not enter diagnostics. Document changed files, relevant test commands, results, security/tenant checks, commits and worktree evidence in the Completion Report.

No additional assumptions are authorised.

## Completion Report

### Status

In Progress — developer Attempt 1 claimed 2026-10-27 after materializing the portable definition in the canonical task worktrees.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

None beyond the explicit architecture/task contract.

### Unresolved Issues

None; live environment availability is a validation prerequisite and must be reported if missing.

### Architectural Concerns

None reported.

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

Pending.

### Review Notes

None.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Not reviewed.

### Follow-up

None.
