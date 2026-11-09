---
id: ARCH-068-SHARED-003
architecture_id: ARCH-068
title: Publish reviewed conversation image contracts
task_kind: publication
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 30
executor: null
claimed_at: null
attempt: 1
depends_on: ['ARCH-068-SHARED-001', 'ARCH-068-SHARED-002']
enables: ["ARCH-068-ADMIN-001", "ARCH-068-BACKGROUND-001", "ARCH-068-COMMERCE-001"]
created: 2026-11-09
updated: 2026-11-09
---
# Publish reviewed conversation image contracts

## Architecture and objective
Implement the owned portion of [binding ARCH-068](../../../architecture/ARCH-068-optional-conversation-product-image.md). The entire contract is normative, including exact schemas, transport/failure rules, initialization, rollout and acceptance matrix. Read it before execution.

## Context and scope
Publication only. Require SHARED-001/002 Complete/Accepted and record their exact final source/build provenance. Select an unused semver version according to existing package release policy, recording exact version here and in handoff; do not predeclare an invented version. Version metadata only, pack/publish accepted source; no implementation redesign or broad validation rerun merely for release. Verify downloaded public tarball SHA256/SRI matches reviewed archive and installed JS+declaration imports of binding/schema/plan/Node preparer and all legacy entrypoints. Record browser/Node separation, package engine/runtime dependencies and exact consumer install version/SRI. Consumers stay Pending until completion/public availability. Update owned publication receipt and dependency-ready statuses only through normal architect reconciliation. No consumer edits/main merge/deployment.

## Interfaces and contracts
The named exported schemas/APIs and exact JSON shapes in the binding contract are authoritative. Existing v1 template hashes/legacy records remain compatible. No clothing-specific fields/model image URL or Meta recovery contract extension.

## Work Items
- [x] Verify both implementation prerequisites are Complete/Accepted and identify their exact accepted source/build provenance.
- [x] Select an unused release version and apply only authorized release metadata.
- [x] Pack/publish accepted artifacts using approved release mechanics without implementation revalidation.
- [x] Verify the exact registry version and downloaded tarball hash/SRI; verify installed JS/declaration exports and legacy entrypoints.
- [x] Push release changes and the publication receipt on mirrored task branches; stop for architect review.

## Dependencies
ARCH-068-SHARED-001 and ARCH-068-SHARED-002 — both Complete / Accepted Attempt1.

## Acceptance criteria
Both accepted capabilities are included in the released artifact. Exact version, archive SHA256/SRI, registry availability, runtime/declaration imports, browser/Node separation and consumer install coordinates are recorded. Source changes are limited to release metadata. No consumer implementation, deployment or activation occurs.

## Validation
- [x] Both implementation prerequisites are Complete/Accepted before release.
- [x] Approved unused version and accepted source/build artifacts identified.
- [x] Publication succeeds and exact version is available at the intended registry.
- [x] Downloaded archive SHA256/SRI matches the reviewed release artifact.
- [x] Installed public runtime/declaration export checks pass, including legacy exports.
- [x] No unauthorized implementation source changed; do not rerun unit/integration tests, lint, typecheck or production build merely to revalidate accepted code. A package command's required artifact-packaging lifecycle is release mechanics, not a discretionary implementation rerun.

## Out of Scope
No redesign of aspects 1 and 3, Meta submission/WABA validation, inventory write, unrelated cleanup, budget increase, production mutation or automatic live initializer.

## Agent execution and review
Execution is owned by the assigned agent, not a human developer. Use /moda-task with canonical isolated parent/implementation worktrees and mirrored task branches. Do not claim on authoring. Implement only this repository portion; use published Shared APIs. If an actual source conflict contradicts the exact binding contract, report it to the architect with path/symbol/evidence; do not invent a replacement architecture or leave a placeholder. No main merge/push, production mutation, real send or live initializer execution is part of this task.

## Completion Report

Ready for Review — Attempt 1. Publication and installed-artifact checks completed; architect review and completion are pending.

### Accepted source and release scope

Both prerequisites are Complete / independently Accepted Attempt 1 in the prepared parent record. SHARED001 accepted source `0b06467c37cbc4cd6ce67fcfa6e9c3fd7da66822` is an ancestor of combined SHARED002 source `8f8a298de90803671b789ba0ef2fe03058a8023e`. Prepared release baseline `f9e565a23c8043966f5d8da2a4be009d2a844085` contains that source; no differences from accepted source exist in src/, scripts/, tsup.config.ts or pre-release package/dependency metadata. The existing accepted build configuration was used unchanged.

Registry inventory contained releases through 5.11.1 with latest=5.11.1; 5.12.0 was unused. README release policy requires a minor increment for an additive capability/export, so selected **@modainteract/moda-interact-shared@5.12.0**. Publishing identity was verified. Only package.json and package-lock.json root version values changed; no implementation, dependency graph, consumer source or validation helper changed.

### Immutable public publication receipt

- Release source commit: `12d0b85aaeefba4dfc46bb12637004f19d462b19`, pushed on implementation `task/ARCH-068-SHARED-003`.
- Exact consumer pin: `@modainteract/moda-interact-shared@5.12.0`; use this version and recorded integrity, never latest/ranges or sibling source.
- Registry: https://registry.npmjs.org/ ; public access, latest tag.
- Tarball: https://registry.npmjs.org/@modainteract/moda-interact-shared/-/moda-interact-shared-5.12.0.tgz
- Archive SHA256: `e4416c765079a6c8c8ca04894e87e3822c3af0acf19428a5d3f542effe697393`.
- Archive/registry SRI: `sha512-RD3pGDVZHK8sRwbi91SpdouRDVkyf+4rhdB4eczaG48avsnEOQRhRccqzX2YI9KhXa1jXE4S2LHfz7D9DR5PEw==`.
- npm SHA1: `e7768931e522ec7cf1f3d4213af04b5ce97814b7`; packed bytes 494518; files 153.
- Local reviewed upload and downloaded public tarball are byte-identical; independently computed SHA256/SHA512 and registry dist.integrity agree.

`npm version 5.12.0 --no-git-tag-version --ignore-scripts` updated version metadata. `npm ci --no-audit --no-fund` installed locked packaging tooling. `npm pack --json --pack-destination /tmp` ran the required prepack build once (ESM/declarations) and created the reviewed archive. `npm publish /tmp/modainteract-moda-interact-shared-5.12.0.tgz --access public --tag latest --ignore-scripts` succeeded exactly once, reporting `+ @modainteract/moda-interact-shared@5.12.0`. Initial registry reads returned 404 while npm processed the upload; only read-only availability checks followed, with no second publication.

### Installed public artifact validation

The upload and actual downloaded archive were separately installed in fresh isolated temporary consumers using ordinary npm installation. Both checks passed:

- All 33 JavaScript public entrypoints import successfully; all 3 exported JSON fixtures parse. All 36 public export entries have their declared target files present in the archive. All 35 prior 5.11.1 export definitions are identical, with only the accepted Node presentation entrypoint added.
- Binding, prepared image, delivery plan, pair, verified provenance and image-source schema imports expose parse methods; selector, plan builder and digest imports are functions. Built plan preserves the complete text body.
- Public Node coordinator and all extracted fetch/transform/network/writer/probe functions import successfully; missing-configuration smoke returns OMITTED/CONFIGURATION_UNAVAILABLE without provider I/O.
- A consumer TypeScript declaration-resolution check imports every JavaScript entrypoint and the named conversation binding/plan/image/source and Node preparation/input/dependency/credential types through public package exports. This is installed-declaration validation, not repository source typecheck.
- Installed browser presentation bundle executes in a browser-like VM; dependency graph excludes Node builtins, sharp, AWS, Prisma, logging, observability and LangChain. Node preparer is absent from the browser namespace.
- Packaging lifecycle passed. Implementation unit/integration tests, lint and repository source typecheck were not rerun for publication. `git diff --check` passed. No source redesign or unresolved source conflict.

Temporary evidence: /tmp/arch068-shared003-pack.json, /tmp/arch068-shared003-pack.log, /tmp/arch068-shared003-receipt.json, /tmp/arch068-shared003-publish.log, /tmp/arch068-shared003-registry.json, /tmp/arch068-shared003-local-smoke.log and /tmp/arch068-shared003-downloaded-smoke.log. Artifact smoke checks were generated only in temporary consumers; no repository implementation helper was changed.

### Engine and runtime dependency handoff

Package metadata declares no top-level engines constraint; this release does not invent one. Packaging and both installed-consumer checks ran with workspace Node24.19.0/npm11.17.0. Node media runtime dependencies remain exactly @aws-sdk/client-s3 3.1143.0 (declares Node>=20.0.0) and sharp0.35.4 (declares Node>=20.9.0); sharp's platform-specific native packages resolve through its ordinary optional dependency mechanism. Browser callers use /commerce/presentation, server preparation uses /commerce/presentation/node. Full unchanged public runtime dependency metadata:

```json
{
  "@aws-sdk/client-s3": "3.1143.0",
  "@langchain/core": "1.2.13",
  "@langchain/langgraph": "1.4.15",
  "@langchain/openrouter": "0.4.15",
  "@opentelemetry/api": "^1.9.0",
  "@opentelemetry/api-logs": "0.221.0",
  "@opentelemetry/context-async-hooks": "^2.10.0",
  "@opentelemetry/exporter-logs-otlp-http": "0.221.0",
  "@opentelemetry/exporter-metrics-otlp-http": "0.221.0",
  "@opentelemetry/exporter-trace-otlp-http": "0.221.0",
  "@opentelemetry/instrumentation-http": "0.221.0",
  "@opentelemetry/instrumentation-undici": "0.31.0",
  "@opentelemetry/resources": "^2.10.0",
  "@opentelemetry/sdk-logs": "0.221.0",
  "@opentelemetry/sdk-metrics": "^2.10.0",
  "@opentelemetry/sdk-node": "0.221.0",
  "@opentelemetry/sdk-trace-base": "^2.10.0",
  "@prisma/instrumentation": "^6.19.3",
  "bullmq-otel": "^2.0.1",
  "intl-messageformat": "^10.7.18",
  "libphonenumber-js": "1.12.30",
  "parse5": "8.0.1",
  "semver": "7.8.5",
  "sharp": "0.35.4",
  "winston": "3.19.0",
  "winston-loki": "6.1.7",
  "zod": "^4.0.0"
}
```

### Git / VCS and physical isolation

Task branch in both repositories: `task/ARCH-068-SHARED-003`.

- Canonical workspace: /Users/kwadwoadomafriyie/project/moda-interact-workspace.
- Parent worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-068-SHARED-003; reused. Parent remote task fast-forward not-needed; origin/main incorporated yes, preclaim head59e4902af7aa9c1245d7abeca2738b606b7c9074.
- Implementation worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-068-SHARED-003; created at f9e565a23c8043966f5d8da2a4be009d2a844085. Remote task fast-forward not-needed; origin/main already-current.
- Launcher recursive submodule sync/update passed; status ready, no entries.
- Durable claim a1f22623f62b8f7561d12013b3897c124450c76b, pushed; executor codex, Attempt1, claimed2026-11-09T22:40:26Z. No duplicate claim or attempt increment.
- Shared/default workspace and implementation checkout switched/mutated for task work: no. Another task worktree reused: no.
- Implementation release commit above is committed/pushed and clean. This matching parent task-only report is committed/pushed on its task branch; final commit identity is provided in the execution response. No gitlink staged, other task/index/architecture changed, main merge/push or force-push.

### Remaining handoff

No unresolved release issue remains. No subagent assistance was used in this publication task. Consumers remain Pending until moda_architect accepts/completes this publication and reconciles their readiness with the exact version/SRI above. No consumer edits, deployment, migration, activation, initializer, R2 operation, provider call or real message occurred. This report submits Review; it does not record architect acceptance or self-completion.

## Architect Review
Not reviewed.

## Coherence amendment — exact handoff and precedence

This section resolves terminology in earlier sections; it does not authorize another implementation. The original Background product transformer is the only product preset. Its output is strictly less than 5MiB, uses contain/white padding (not crop), and retains its quality ladder. Host configuration readers and credential loading stay in their host repositories. Only the generic media operations move to Shared.

Shared SHARED-001 also exports these exact strict provenance schemas, reusing the validators already defined above:
```ts
export const ConversationProductPairSchema = z.strictObject({
  productId: NativeProductId, variantId: NativeVariantId,
});
export const ConversationVerifiedProductsSchema = z.strictObject({
  shopId: BoundId,
  platform: z.enum(['SHOPIFY', 'WOOCOMMERCE']),
  products: z.array(CommerceProductSchema).max(3),
});
export const ConversationProductImageSourceSchema = z.strictObject({
  kind: z.literal('SOURCE'), shopId: BoundId,
  platform: z.enum(['SHOPIFY', 'WOOCOMMERCE']),
  productId: NativeProductId, variantId: NativeVariantId, sourceUrl: HttpsUrl,
});
```
Selector input is exactly `{shopId, platform, displayedPairs, verifiedProducts}`; displayedPairs is an array of ConversationProductPairSchema with maximum 3 and uniqueness by canonical productId/variantId tuple. Verified product array pairs must also be unique. Schema/provenance mismatch throws an Error with code PRODUCT_IMAGE_IDENTITY_INVALID; missing exact first pair returns PRODUCT_NOT_VERIFIED. No new native-ID format validation is introduced. This result is internal and is never accepted from a browser or model as proof of authorization. Shared task tests must cover WooCommerce simple products (`variantId:null`) and both platforms' native variant IDs.

Plan construction first validates the body and binding. Omitted binding produces TEXT/BINDING_DISABLED. A present invalid binding throws PREPARED_INVALID; it cannot silently become text. With a valid binding, precedence is NO_PRESENTED_PRODUCT, CAPTION_TOO_LONG, IMAGE_UNAVAILABLE, IMAGE_IDENTITY_MISMATCH, then IMAGE success. Host source/preparation omissions are logged with their original reason; buildConversationDeliveryPlan's IMAGE_UNAVAILABLE is the delivery-level summary. IMAGE_IDENTITY_MISMATCH logs at error severity and never dispatches that URL. Source absence or optional preparation failure still allows valid text. Hosts skip media configuration/network work when the first two applicable omission conditions already determine TEXT.

Schema files do not implement final send authorization. Background requires persisted plan.image.shopId to equal the locked message's conversation shop, and its exact pair to equal the verified selected first pair in the matching receipt. Persisted JSON alone is not a receipt. Null is legacy only: a newly prepared aspect-2 reply always persists TEXT or IMAGE. Legacy text retry remains legacy; it cannot be upgraded to IMAGE. No later retry rewrites a previously admitted plan.

SHARED-001 owns changes to Shared source only. SHARED-002 can read Background source as extraction input but writes only Shared. BACKGROUND-001 owns replacement of Background implementation bodies and updates every compatibility caller/mock. ADMIN-001 owns authoring only; ADMIN-002 owns script/extracted transaction helpers. DATABASE-001 owns schema/migration/generation validation only; it does not implement Shared validation or Background admission. Each task's acceptance applies only to its repository and explicitly owned interfaces; the whole acceptance matrix is integrated by SYSTEM-TEST-001.

SYSTEM-TEST-001 creates `src/harness/conversation-product-image/{fixtures.js,scenario.js,assertions.js}` and `test/conversation-product-image.test.js`; wires the existing package.json test command using the repository's existing test runner and documents launch in README.md. Reuse `src/whatsapp-emulator.js`, `src/harness/aimock/runtime.js`, `src/harness/environment.js` for transport/model/environment control; extend them only where IMAGE payload capture is missing. Fixtures use the same compiled wrapper, product bytes, public origin and scripted envelope for both hosts; assert complete plan equality, media omission, one provider call, body preservation and legacy behavior. Add the mandatory failure/race cases above. Tests use disposable local infrastructure/provider emulator; launching real infrastructure or sending real WhatsApp messages requires separate explicit user authorization. Do not mark blocked merely because optional live infrastructure was not authorized when local acceptance can run.

Script `--apply` is opt-in and a separate operator action. Implementation completion does not activate a wrapper. Existing occupied slots are never replaced. Source contains no header logo or fixed product facts: only response.body and the optional structured binding. Existing all-language eligibility rules remain authoritative; obtain REVIEW_LANGUAGES from its existing export, not a copied locale list or hardcoded loop count. Tests assert the current count and exact coverage from that export.

## Architect readiness handoff — 2026-11-09
Ready, Attempt0 unclaimed. Accepted SHARED001 source `0b06467c37cbc4cd6ce67fcfa6e9c3fd7da66822` is an ancestor of accepted SHARED002 source `8f8a298de90803671b789ba0ef2fe03058a8023e`. Use this exact accepted source/artifact provenance; task completion does not imply main integration. Both task records carry independent acceptance. No implementation worktree or release claim is created by readiness reconciliation. Consumers stay Pending until this publication is accepted Complete and exact public artifact coordinates are recorded.
