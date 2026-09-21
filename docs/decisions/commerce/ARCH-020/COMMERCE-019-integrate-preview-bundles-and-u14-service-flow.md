---
id: ARCH-020-COMMERCE-019
architecture_id: ARCH-020
title: Integrate preview bundles and the U14 service flow
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: blocked
priority: 145
executor:
claimed_at:
attempt: 2
depends_on:
  - ARCH-020-COMMERCE-013
  - ARCH-020-COMMERCE-009
  - ARCH-020-COMMERCE-017
  - ARCH-020-COMMERCE-008
  - ARCH-020-COMMERCE-002
  - ARCH-020-COMMERCE-033
  - ARCH-020-COMMERCE-034
enables:
  - ARCH-020-COMMERCE-012
  - ARCH-020-SYSTEM-TEST-001
  - ARCH-020-GATEWAY-001
  - ARCH-020-COMMERCE-024
  - ARCH-020-COMMERCE-031
created: 2026-09-21
updated: 2026-09-21
---

# Integrate preview bundles and the U14 service flow

## Architecture

ARCH-020. [Implementation contracts](../../../architecture/ARCH-020-implementation-contracts.md)
C4/C5/C7/C9/C14–C19 remain binding. The integration ownership specification is
[C20](../../../architecture/ARCH-020-implementation-contracts.md#c20-integration-task-ownership-and-parallel-execution).
Use actual accepted prerequisite source, never copied snapshots or new schemas.

## Objective

Connect saved definitions and prompts to the009 preview lifecycle and017 U14 client, using real Redis and isolated provider/model fixtures. Own preview assembly only; no U01–U13 service wiring.

## Context

The former013 combined backend, Studio and preview integration. This definition
replaces that combined scope;018 and019 can execute concurrently after013 and
their own component prerequisites complete. No task was claimed by this amendment.

## Scope

Connect saved definitions and prompts to the009 preview lifecycle and017 U14 client, using real Redis and isolated provider/model fixtures. Own preview assembly only; no U01–U13 service wiring.

## Out of Scope

Other integration owners' files; new business features/pages; new Shared release,
database migration or external-service implementation; deployment, paid live
provider calls or WhatsApp delivery. Do not replace real components with fixtures.

## Requirements

Follow C20 file ownership and mapping rules. Authorize each protected request using
the accepted auth library. Reuse source schemas, field bounds, hashes and replay/CAS
semantics. Preserve all active work. No production test-adapter registration.
At preparation verify each source/export against its accepted commit and record
that SHA in the mapping document; pending producer symbols must not be guessed.

## Work Items

- [x] Own `src/commerce/integration/preview/` and minimal composition in `lib/preview/runtime.ts` plus U14 client injection. Do not edit018 Studio services/actions or013 backend factory.
- [x] Implement PreviewBundleLoader, PreviewPromptLoader and PreviewToolExecutionPort from accepted009 types using013 read facade and authorized saved revisions. Do not replace authored prompts with generic strings.
- [x] Freeze exact revision content, response definition and synthetic grant at start. After a saved draft changes, an existing conversation still executes its frozen definition; no reloading latest tool content during later turns.
- [ ] Instantiate009 PreviewService/RedisPreviewStateStore and typed ports. Use014 actual interpreter with isolated fixture operation adapters; explicit MODEL mode uses separate model config, never production credentials. The accepted `PreviewModelPort` injection seam is preserved, but no accepted provider transport exists for `COMMERCE_PREVIEW_MODEL` and `COMMERCE_PREVIEW_API_KEY`; production composition remains fail-closed and this gap is reported below.
- [x] Connect017 PreviewClient to exact C9.1 routes. Retain008 layout handoff and Back restoration using component fixture mounting where needed; no dependency on018 service adapters.
- [x] Provide `docs/commerce-preview-integration.md` and `test:arch020-preview-integration` plus `test:arch020-preview-integration:redis`; preserve existing quotas/replay/cancel logic instead of duplicating it.

## Interfaces / Contracts

Source: `src/commerce/preview/types.ts: PreviewBundleLoader, PreviewPromptLoader,
PreviewToolExecutionPort` and `service.ts: PreviewServiceDependencies`.
`lib/preview/types.ts`/`service.ts` re-export these; do not create a second service.
Destination: `lib/preview/runtime.ts:getPreviewService`, replacing unavailableLoader
with real preview adapters.017's accepted PreviewClient supplies frontend route
calls; record actual file/export once017 is accepted, not a guessed symbol.
013 provides read-only saved-definition access and interpreter factory;019 supplies
fixture transports explicitly. Never reuse the live policy/provider registry.
PreviewResult and body/error shapes remain009/C9.1, not UI-specific alternatives.

## Dependencies

- ARCH-020-COMMERCE-013
- ARCH-020-COMMERCE-009
- ARCH-020-COMMERCE-017
- ARCH-020-COMMERCE-008
- ARCH-020-COMMERCE-002

All dependencies must be Complete and architect-accepted before execution.
Readiness never launches a task; use the normal dedicated mirrored worktrees.

## Enables

- ARCH-020-COMMERCE-012
- ARCH-020-SYSTEM-TEST-001
- ARCH-020-GATEWAY-001
- ARCH-020-COMMERCE-024
- ARCH-020-COMMERCE-031

## Acceptance Criteria

- [x] P01: real017 UI ->009 route -> real saved loader -> Shared runner/interpreter -> Redis -> reply/details flow; no fake preview service or constant EVAL response.
- [ ] P02: N10/N11/N13 preview portion covers release/draft/tool entry, sidebar, Back and refresh loss. Tool-test entry is integrated; Conversation source gating is now owned by COMMERCE-034. Do not fabricate a capability or prompt in COMMERCE-019.
- [x] P03: repeated/concurrent Send, same-ID changed payload, cancel/complete race, expired/unknown state and quota boundaries preserve one reservation/model start per logical run across two service instances.
- [x] P04: edit/publish saved content between turns; frozen prompts/tool definitions and language/history persist. New conversation sees new selection; no production grant/reset/write.
- [x] P05: denied staff or foreign/missing revision fails before loading sensitive content; fixture/model credentials remain isolated and no WhatsApp/live-Shopify transport is constructed.
- [x] P06: fail unavailable if loader/Redis/model config is absent; same-code default FIXTURE run works without paid credentials. Real Redis tests verify counters/locks/results/TTL, not merely Lua source text.

## Validation

Use the C20 shared isolated seed contract and this task's named scenarios. Assert
rows, operation IDs, provider calls and state, not only HTTP200 or screenshots.
Substitute external provider/model transports only; application services under
integration remain real. Run focused integration tests during work, then repository
typecheck/lint/build before submission. No redundant full-suite reruns without new
changes/failures. PostgreSQL/Redis/container checks obey the existing execution
policy: provide the command and actual evidence separately; a not-run required
check is not a pass. No paid model, live Shopify or production credentials required.
Document owned commands and exact outputs in the report; C20 maps every former
I01–I09 requirement to an owner so no acceptance coverage disappears.

## Stop Condition

After scoped work and agent-owned checks, update this task's execution/report fields, publish task-owned mirrored branches and return to review. Record exact pending developer validation where applicable. Stop; do not begin enabled tasks or mark your own task Complete. Publication tasks stop after release mechanics. System tests require explicit developer invocation even after becoming Ready.

## Implementation Notes

Normal execution uses /moda-task and scripts/start-agent-task.py preparation, dedicated parent and implementation worktrees, synchronization and recursive submodule initialisation. Follow docs/agent-vcs-ownership-policy.md, docs/agent-worktree-isolation-policy.md and docs/task-definition-materialization.md. The main-only exception applies to this review draft, not task execution. The COMMERCE route is registered in this packet; consume the accepted COMMERCE-001 foundation.

## Completion Report

### Status

Review, Attempt 2 rework submitted after the Architect Changes Requested review.

### Files Changed

- `moda-interact-commerce/lib/preview/runtime.ts`
- `moda-interact-commerce/src/commerce/integration/preview/adapters.ts`
- `moda-interact-commerce/src/commerce/preview/types.ts`
- `moda-interact-commerce/src/commerce/preview/service.ts`
- `moda-interact-commerce/src/commerce/preview/redis-store.ts`
- `moda-interact-commerce/tests/preview-integration.test.ts`
- `moda-interact-commerce/docs/commerce-preview-integration.md`
- `moda-interact-commerce/package.json`

### Work Completed

Connected production `PreviewService` composition to Redis, the accepted COMMERCE-013
saved-selection facade, authored prompt loading, and fixture tool execution. The
creation-time authorized read now returns a bounded private snapshot containing exact
selected definitions and authored prompts; Redis persists it with the conversation and
later fixture turns consume that snapshot. Process-global Maps were removed, so
restart/replica execution does not depend on local memory and mutable draft edits
cannot overwrite an older conversation. Limits are enforced at 32 definitions,
65,536 bytes per definition, 64,000 authored prompt characters and 3 MiB serialized,
with fail-closed validation. The direct saved-tool test uses the accepted
empty-capability DRAFT selection and the accepted interpreter with a synthetic query
boundary.

### Validation Results

- `npm run test:arch020-preview-integration`: 4 files passed, 37 tests passed.
- `npm run test:arch020-preview-integration:redis`: 1 file passed, 4 tests passed; Redis snapshot state round-tripped and atomic capacity protection passed.
- `npm run typecheck`: passed.
- `npm run lint`: passed with 2 pre-existing warnings in
  `scripts/code-runtime-manifest.mjs` and `src/commerce/code-response/runtime/kernel.ts`.
- `npm run build`: passed; Next.js production build completed and emitted all expected
  Commerce routes.
- `git diff --check`: passed.
- Recursive database submodule initialized at `7f920e8f2ad523e78e566f4dbdfbb1f68118b082`.

### Deviations

The generic MODEL adapter remains fail-closed because no separate preview model
configuration was installed. The repository has no accepted provider transport
implementing `PreviewModelPort` from the configured `COMMERCE_PREVIEW_MODEL` and
`COMMERCE_PREVIEW_API_KEY`. No live provider, Shopify, WhatsApp, PostgreSQL, or
production credential validation was performed.

### Assumptions

Use the parent architecture and actual accepted dependency revisions. Return contradictory source facts to moda_architect.

### Unresolved Issues

Commerce repository/submodule provisioning is complete; consume the accepted
COMMERCE-001 foundation. U14's accepted tool-entry Start payload has zero capability
revisions, while the accepted Shared manifest requires at least one capability and
COMMERCE-013 supplies no authored BASE data for a synthetic capability. This exact
interface gap is documented for Architect resolution; the direct saved-tool test
path is executable without fabricating a capability or prompt.

### Architectural Concerns

None newly reported.

Connected production `PreviewService` composition to Redis, the accepted COMMERCE-013 saved-selection facade, authored prompt loading, and fixture tool execution. The creation-time authorized read now returns a bounded private snapshot containing the exact selected definitions and authored prompts; the snapshot is persisted with the Redis conversation and is passed to later fixture turns. Process-global Maps were removed, so restart/replica execution does not depend on local memory and mutable draft edits cannot overwrite an older conversation. Snapshot limits are enforced at 32 definitions, 65,536 bytes per definition, 64,000 authored prompt characters and 3 MiB serialized, with fail-closed validation. The direct saved-tool test uses the accepted empty-capability DRAFT selection and the accepted interpreter with a synthetic query boundary.
`origin/task/ARCH-020-COMMERCE-019`. Canonical parent worktree:
`/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-020-COMMERCE-019`,
branch `task/ARCH-020-COMMERCE-019`. COMMERCE-013 accepted source commit:
`4d529773fde26599027aef2d76fbd70bc974b352`. No parent service gitlink or main
integration was performed.

## Architect Review

### Attempt 2 — Blocked (2026-09-21)

Reviewer: moda_architect. **Blocked; task status `blocked`, Attempt 2 retained,
executor/claimed_at null. Not accepted or returned for another implementation
attempt yet.** Reviewed the exact submitted
`moda-interact-workspace-ARCH-020-COMMERCE-019(1).zip`, parent report commit
`1d4007959b30fcde0163d0531681579d6d362569` (verified as the current remote
`task/ARCH-020-COMMERCE-019` parent head), the reported implementation commit
`3d0caf3`, C9/C10/C20 and the accepted U14 contract. The implementation repository
commit is not independently addressable through the current GitHub connector, so
implementation inspection is grounded in the exact submitted archive.

Attempt 2 materially resolves the implementable A1 corrections and those changes
must be preserved:

- the exact selected definitions and authored prompts now form a bounded
  `PreviewFrozenSnapshot`;
- that snapshot is serialized into Redis conversation state and restored through
  `StoredConversationSchema`, so later turns no longer depend on process-global
  Maps;
- later fixture execution receives the stored snapshot and does not re-read mutable
  draft definitions for an existing conversation;
- the saved-tool test path now uses the accepted DRAFT read shape with
  `capabilityRevisionIds: []` and the exact tool revision;
- snapshot bounds fail closed at 32 definitions, 65,536 bytes per definition,
  64,000 authored prompt characters and 3 MiB serialized;
- the submitted focused integration/Redis suites, typecheck, lint, build and diff
  check are useful supporting evidence. No larger arbitrary test matrix is required.

Two remaining blockers are not safe for COMMERCE-019 to invent around.

#### A2-B1 — U14 tool-only Conversation Start conflicts with the accepted manifest/prompt contract

Accepted U14 currently permits Conversation Start while a saved tool is the only
selected source. `PreviewScreen.conversationPayload()` then sends:

```text
kind: DRAFT
capabilityRevisionIds: []
toolRevisionIds: [selectedToolRevisionId]
```

The accepted COMMERCE-013 `saved.readSelection` correctly returns the authorized
tool but no capability revision or authored prompt for that selection. The
COMMERCE-019 bundle loader therefore has zero capabilities. The Shared
`CommerceManifestSchema` requires a non-empty capability set including
`conversation_core`, and each granted tool must have selected capability
provenance. C20 also requires the real selected authored prompt and explicitly
forbids replacing it with a hard-coded generic prompt. There is therefore no valid
COMMERCE-019-only transformation from a tool-only saved selection into the required
conversation manifest.

This is now an integration-discovered defect at the accepted U14 source-selection
boundary. The U14 contract says Conversation uses saved behaviour revisions or a
release; tool entry is valid for Tool test. Resolution belongs to the U14 owner:
either reopen `ARCH-020-COMMERCE-017` or create a bounded Commerce correction task
that makes Conversation Start require an actual conversation source
(release/behaviour draft) while preserving saved-tool preselection for Tool test.
COMMERCE-019 must not fabricate a `conversation_core` revision, prompt or capability
ID. No COMMERCE-017 state is changed by this review because developer reopen
authority has not been exercised.

#### A2-B2 — Preview MODEL transport has no accepted provider protocol/implementation

C9/C10/C20 require explicit MODEL mode to use a separately configured preview-only
model transport and the accepted configuration names
`COMMERCE_PREVIEW_ENABLED`, `COMMERCE_PREVIEW_MODEL` and
`COMMERCE_PREVIEW_API_KEY`. The current production composition still installs
`createUnavailableModel()` when preview is enabled, so there is no configured state
that can execute a production MODEL preview.

Attempt 1 explicitly permitted the repository agent to report an architectural gap
rather than invent a provider transport. That gap is confirmed. ARCH-020 defines
the model identifier and credential names but does not define the provider/protocol,
endpoint, request/response adapter, authentication convention or failure mapping,
and the Commerce repository contains no accepted `PreviewModelPort` provider
implementation to reuse. Those details materially affect external I/O and secret
handling and must not be guessed by the repository agent.

Architect resolution is required before another COMMERCE-019 claim: select and
document the preview model provider/transport contract, then either create a bounded
Commerce provider task and add it as a dependency of COMMERCE-019 or explicitly
amend COMMERCE-019 with the resolved transport contract. FIXTURE mode remains valid
and credential-free; no Background/production credential fallback is permitted.

### Disposition

COMMERCE-019 is blocked on the two items above. Preserve all accepted Attempt 2
implementation; do not churn the Redis snapshot, tool-test or working preview
lifecycle while these dependencies are resolved. `ARCH-020-COMMERCE-012`,
`ARCH-020-COMMERCE-024`, `ARCH-020-COMMERCE-031`, `ARCH-020-GATEWAY-001` and
`ARCH-020-SYSTEM-TEST-001` remain gated. Nothing is promoted or launched
automatically.

### Attempt 1 — Changes Requested — 2026-09-21

Reviewer: moda_architect. **Changes Requested; Ready, Attempt 1 retained;
executor/claimed_at null. Not accepted.** Reviewed the exact submitted
`moda-interact-workspace-ARCH-020-COMMERCE-019.zip`, parent report commit
`5e89f15c647559daee4af6fc95fd0b4840d5c8a0`, C9/C20 and the task acceptance
criteria. The submitted implementation identifies `197d5c6` as its implementation
The generic MODEL adapter remains fail-closed because the repository has no accepted provider transport implementing `PreviewModelPort` from the configured `COMMERCE_PREVIEW_MODEL` and `COMMERCE_PREVIEW_API_KEY`. No live provider, Shopify, WhatsApp, PostgreSQL, or production credential validation was performed.

The implementation materially connects the accepted PreviewService to Redis, the
COMMERCE-013 saved-selection facade, authored prompts and the accepted definition
executor. The reported 37 focused tests, 4 executable Redis tests, typecheck, lint,
build and diff check are useful supporting evidence. This review does not require
an arbitrary larger test count. The blockers below are functional integration
failures in the submitted source.

#### A1-R1 — P1 — Make frozen tool definitions Redis/replica/restart durable

Files: `src/commerce/integration/preview/adapters.ts`, the private preview snapshot
shape/store plumbing needed by C20, `lib/preview/runtime.ts` only if composition
changes, and focused integration tests.

The submitted adapter keeps the selected `PreviewSelection` and exact tool
definitions in module-global process-local Maps (`selections` and `definitions`).
The durable Redis conversation stores the manifest/grant/prompts/history, but not
the exact definitions used to execute later turns. `execute(..., bundle)` therefore
looks up `definitions.get(bundleKey(...))`; after a process restart or on another
Commerce replica the Redis conversation still exists while that Map is empty, so
Attempt: 2. Implementation worktree:
branch `task/ARCH-020-COMMERCE-019`, commit `3d0caf3` (including prior task
history), pushed to

There is also an in-process overwrite case: `bundleKey` hashes only the manifest. A
draft edit can change execution/response-template content while keeping the same
revision identity and descriptor-visible fields. Starting a new conversation then
writes the new definition under the same Map key; an older conversation can execute
the newer definition. That violates P04's "existing conversation still executes its
frozen definition" requirement.

Replace the process-local Maps as correctness authority with a bounded frozen
snapshot owned by the preview conversation. Persist the exact selected definitions
with the Redis conversation or persist an opaque Redis snapshot handle that resolves
to the exact immutable snapshot. Take prompts/definitions/response definition from
the authorized creation-time selection, not by re-reading mutable draft content on
a later turn. Preserve the public C9.1 payloads. Enforce C20's snapshot bounds: at
most 32 definitions, each definition <=65,536 bytes, total authored prompts <=64,000
characters and total serialized snapshot <=3 MiB; fail closed rather than dropping
content. No new database table or browser field is required.

Acceptance reproduction: start a tool-using conversation on service instance A,
execute a later turn on instance B sharing only Redis/backend state, and repeat after
a fresh service construction; both must execute the original definition. Also edit
only execution/response-template content so the descriptor/manifest identity remains
otherwise unchanged, start a second conversation, and prove conversation A still
executes its original definition while conversation B sees the edited definition.

#### A1-R2 — P1 — Make the real saved-tool test and tool-entry paths executable

Files: `src/commerce/integration/preview/adapters.ts` and focused real-facade
integration coverage; do not weaken COMMERCE-013 authorization.

`PreviewToolExecutionPort.load()` currently calls the accepted saved facade with
`capabilityRevisionIds: ['preview-capability']`. COMMERCE-013 validates that every
requested capability revision exists, so the production U14 tool-test path is rejected
unless a database row happens to use that fabricated ID. Use the accepted DRAFT
shape for an authorized tool-only read (`capabilityRevisionIds: []`, exact
`toolRevisionIds: [toolRevisionId]`) or another already-accepted facade path; do not
invent a capability identity. The fixture executor must continue to use the accepted
interpreter and synthetic query boundary only.

Also reconcile U14's accepted tool-entry Start flow. The accepted screen sends a
DRAFT selection with zero capability revisions and one tool revision when entered
from a saved tool. The current bundle loader produces zero capabilities and therefore
cannot satisfy `CommerceManifestSchema`; Start fails before a preview conversation is
created. P02 explicitly includes tool entry. Support the accepted tool-entry behavior
without fabricating a generic authored prompt or live grant. If the accepted
COMMERCE-013 facade genuinely lacks the authored BASE data needed to form a valid
synthetic conversation bundle, record that exact interface gap for architect
resolution instead of silently claiming P02 complete. Tool-test execution itself must
work regardless.

Acceptance reproduction should exercise the production adapter against a
COMMERCE-013-compatible saved facade, not a stub that accepts arbitrary IDs: a real
saved tool test succeeds with zero live Shopify/WhatsApp/provider calls, missing or
foreign revisions fail before execution, and the U14 tool-entry Start path either
creates a valid frozen conversation or returns an explicitly documented architectural
gap for resolution.

#### A1-R3 — P2 — Reconcile MODEL mode with the accepted preview configuration

Files: `lib/preview/runtime.ts`, preview integration adapter/config wiring and focused
composition tests.

The production runtime checks `PREVIEW_MODEL_URL`, which is not an ARCH-020 preview
configuration name, and when present installs `createUnavailableModel()`, whose every
call throws `UNAVAILABLE`. Under the accepted C10 configuration
`COMMERCE_PREVIEW_ENABLED=true` with `COMMERCE_PREVIEW_MODEL` and
`COMMERCE_PREVIEW_API_KEY`, `MODEL` therefore remains unavailable; adding the
unapproved variable still cannot produce a model turn. That is not the task's stated
"explicit MODEL mode uses separate model config" integration.

Use the accepted preview-enable/model/API-key configuration and a separately injected
preview model transport. `FIXTURE` must remain the default and require no paid
credentials. Disabled/missing preview/model configuration must fail closed before
model dispatch, and MODEL must never fall back to Background/production credentials
or enable live tools. No paid/live provider call is required for review: prove this
with an injected configured model transport and call counts. If no accepted provider
transport contract exists in the current source, report that exact architectural gap
instead of inventing `PREVIEW_MODEL_URL` or claiming MODEL integration complete.

#### Resubmission

Preserve the working Redis quota/replay/cancellation logic, authored prompt loading,
fixture query boundary and accepted Shared runner/interpreter composition. This is not
a request for broader refactoring or exhaustive tests. Add only targeted regressions
that demonstrate the corrected functional paths above, rerun this task's focused
integration/Redis checks plus repository typecheck/lint/build, update the Completion
Report with the actual Attempt 2 preparation/commits, set `status: review`, clear the
claim and stop. No dependent task is promoted or launched until COMMERCE-019 is
architect-accepted Complete.


### Attempt 2 — Blocked with deterministic prerequisites — 2026-09-21

Reviewer: moda_architect. **Blocked; Attempt 2 retained; executor/claimed_at null.**
Reviewed the exact Attempt 2 submission reporting implementation `3d0caf3` and
parent report `1d400795`. The submitted 37 focused checks, 4 Redis checks, typecheck,
lint, build and diff check are supporting evidence; no broader test-count expansion is
requested.

The following Attempt 1 corrections are functionally accepted and MUST NOT be redone:

- **A1-R1 complete:** creation-time definitions/prompts now form a bounded private
  `PreviewFrozenSnapshot` persisted with the Redis conversation. Process-global
  selection/definition registries are removed, so replica/restart execution and later
  draft edits no longer change an existing conversation's executable snapshot.
- **A1-R2 saved-tool execution complete:** the direct tool-test loader uses the accepted
  DRAFT read shape with `capabilityRevisionIds: []` and the exact selected
  `toolRevisionIds`. The fixture interpreter/synthetic query boundary remains intact.

No further source change is authorised in019 for those mechanisms unless a new defect is
reproduced. Two missing capabilities sit outside019's current ownership and are now
resolved by explicit prerequisite tasks rather than by asking the next executor to
redesign them.

#### A2-B1 — U14 tool-entry source semantics — owned by ARCH-020-COMMERCE-034

Architect decision: **a saved tool revision is a Tool-test source, not a Conversation
source.** U14 Conversation mode requires a real saved behaviour/release source carrying
authored capability revisions. Never synthesize `conversation_core`, a generic prompt,
or a fake capability revision merely because U06 supplied a tool.

COMMERCE-034 owns the frontend correction in the already accepted U14 component:

1. Tool-entry from U06 continues to open U14 in **Tool test** mode with that exact tool
   preselected and `Run tool test` working unchanged.
2. Switching to **Conversation** with only a tool selected must leave
   `Start conversation` disabled and show bounded guidance such as
   `Select a saved release or behaviour draft to start a conversation.`
3. `conversationPayload()` must never place a standalone selected tool into
   `selection.toolRevisionIds`.
4. RELEASE payload remains `{kind:'RELEASE', releaseId}`.
5. DRAFT Conversation payload comes only from the selected saved/unsaved behaviour
   source's actual `member.capabilityRevisionId` values and its validated
   `responseContract`; `toolRevisionIds` is `[]`.
6. Existing Tool-test selection and Conversation release selection may coexist, but
   neither silently changes the other. Back still returns to the originating source.
7. No backend/API/Shared schema change is authorised by this correction.

COMMERCE-034 contains the exact files, regressions and stop condition.019 must not
work around this gap.

#### A2-B2 — OpenAI/Groq MODEL transport — owned by ARCH-020-COMMERCE-033

Architect decision: support **both OpenAI-direct and Groq** behind the existing
provider-neutral `PreviewModelPort`. The test/development hosted environment will use
Groq. No arbitrary base URL and no automatic provider fallback are permitted.

The accepted server-only environment contract is now:

```text
COMMERCE_PREVIEW_ENABLED=false|true       # false when omitted
COMMERCE_PREVIEW_PROVIDER=openai|groq     # required only when enabled=true
COMMERCE_PREVIEW_MODEL=<provider model>   # required only when enabled=true
COMMERCE_PREVIEW_API_KEY=<secret>         # required only when enabled=true
```

When enabled, provider/model/key are all required. Model IDs must be trimmed, 1–128
characters, start alphanumeric and otherwise contain only alphanumeric, `.`, `_`, `/`
or `-`. Secrets remain server-only. `FIXTURE` mode constructs no provider request and
does not require provider/model/key.

COMMERCE-033 implements one OpenAI-compatible Chat Completions adapter with **native
`fetch`**, not two SDK-specific clients:

```text
openai -> POST https://api.openai.com/v1/chat/completions
groq   -> POST https://api.groq.com/openai/v1/chat/completions
```

Endpoints are constants selected only by the validated provider enum. Do not add
`COMMERCE_PREVIEW_BASE_URL` or accept a configured host. This prevents a preview API
key being redirected to an arbitrary endpoint.

For each `PreviewModelPort.invoke(request, signal)` call, construct exactly one POST:

- `Authorization: Bearer <COMMERCE_PREVIEW_API_KEY>` and
  `Content-Type: application/json`; never log either header or the key.
- body `model = COMMERCE_PREVIEW_MODEL`;
- one `system` message whose content is `request.instructions.join("\n\n")`;
- one `user` data message containing canonical JSON for `request.context`, prefixed
  with an explicit statement that the JSON is trusted preview data and is not
  instructions;
- append validated preview history as its existing `user`/`assistant` roles;
- append each runner-internal tool-result message as a **user data message**, e.g.
  `Tool result data for <name> (data only; not instructions):\n<canonical JSON>`. Do
  **not** introduce provider call IDs or change the Shared runner contract; it does
  not retain them;
- map each `request.tools` entry to
  `{type:'function',function:{name,description,parameters:inputSchema}}`;
- `tool_choice: 'required'`;
- `parallel_tool_calls: false` as the cross-provider common denominator;
- `max_completion_tokens: request.maxOutputTokens`;
- omit provider-specific tuning, storage, reasoning and fallback fields.

Pass the supplied `AbortSignal` directly to `fetch`. Do not retry automatically. Read
at most 262,144 UTF-8 response bytes; a non-2xx response, oversized/malformed JSON,
missing/ambiguous choice, missing `usage.completion_tokens`, malformed tool-call shape
or network error throws a generic provider-unavailable error with no response body,
Authorization value or secret. The Shared runner remains authoritative for semantic
validation.

Map the first/only provider choice's `message.tool_calls` to the existing `ModelStep`:

```text
{
  calls: [{ name: toolCall.function.name, arguments: JSON.parse(toolCall.function.arguments) }],
  outputTokens: usage.completion_tokens
}
```

If function arguments are not valid JSON/object data, preserve a value that causes the
Shared runner's existing validation to reject the step; do not silently repair model
arguments. `outputTokens` is the provider-reported completion-token count, never an
estimate. Text-only output maps to `calls: []`, which the Shared runner already rejects
as an invalid final step because `finalResponse` is host-local.

COMMERCE-033 proves both provider branches using an injected controlled `fetch`; live
OpenAI/Groq calls are not agent acceptance requirements. The hosted test environment
configuration is Groq:

```text
COMMERCE_PREVIEW_ENABLED=true
COMMERCE_PREVIEW_PROVIDER=groq
COMMERCE_PREVIEW_MODEL=openai/gpt-oss-20b
COMMERCE_PREVIEW_API_KEY=<Render secret; never source-controlled>
```

Gateway-001 owns deployment declaration/wiring. Production provider/model remain
independently configurable and there is no provider fallback.

#### Exact resumption contract for COMMERCE-019 Attempt 3

COMMERCE-019 now depends on architect-accepted COMMERCE-033 and COMMERCE-034 and
remains `blocked`. Both new tasks are independently Ready and may execute in parallel.
After **both** are Complete, moda_architect—not the repository agent—changes019 from
Blocked -> Ready. The next normal claim becomes Attempt 3.

Attempt 3 must be narrow and deterministic:

1. In `lib/preview/runtime.ts`, consume the validated preview model config from
   `lib/server/config.ts`; when enabled, inject COMMERCE-033's accepted
   `createPreviewModel(...)` into `PreviewService`; when disabled, leave `model`
   undefined so FIXTURE remains credential-free.
2. Remove `createUnavailableModel` from production composition and remove the helper
   from `src/commerce/integration/preview/adapters.ts` if it becomes unused. Do not
   modify the accepted frozen-snapshot/tool-executor implementation.
3. Consume COMMERCE-034's U14 source gating as-is; do not reimplement its UI logic.
4. Update `docs/commerce-preview-integration.md` so the mapping table records the
   accepted provider adapter/export and the U14 source-gating owner instead of the
   two former architectural gaps.
5. Add only composition-level regressions proving:
   - FIXTURE creates/runs with preview provider disabled and zero provider fetches;
   - MODEL with accepted config invokes the injected provider adapter exactly once per
     model step;
   - missing enabled provider config fails closed before dispatch;
   - U14 tool-only entry cannot dispatch Conversation creation, while a real
     release/draft source can.
6. Rerun this task's existing focused preview integration/Redis checks plus repository
   typecheck, lint, build and `git diff --check`; no unrelated refactor/full-suite
   expansion is requested.
7. Return the same task to `review`, clear the claim and STOP.

No downstream task is promoted by this Blocked review.019's existing Redis snapshot,
quota/replay/cancel and fixture execution corrections are preserved.

### Review Status

Blocked.

### Review Notes

Attempt 2 resolves the in-scope frozen-snapshot and saved-tool execution defects. The
remaining missing capabilities are materialised as COMMERCE-033 and COMMERCE-034 with
complete implementation contracts;019 must not invent replacements.

### Reviewed Files

Attempt 2 implementation/report plus `src/commerce/preview/types.ts`,
`src/commerce/preview/redis-store.ts`, `src/commerce/integration/preview/adapters.ts`,
`lib/preview/runtime.ts`, `lib/server/config.ts`, U14 source/payload handling and the
C9/C10/C20/U14 architecture.

### Validation Reviewed

37 focused tests, 4 Redis tests, typecheck, lint, production build and diff check were
reported passing. Review disposition is functional/architectural, not a request for
additional exhaustive testing.

### Architecture Conformance

Snapshot/tool-test corrections conform. Conversation source semantics and MODEL
provider transport require the two explicit prerequisite tasks above before019 can
complete.

### Follow-up

Execute COMMERCE-033 and COMMERCE-034 independently. After both are architect-accepted
Complete, reconcile019 to Ready for its narrow Attempt 3 composition. No automatic
launch, main merge or downstream promotion.


### Readiness reconciliation after COMMERCE-013 Attempt 9 acceptance — 2026-09-21

Ready, Attempt 0 retained; executor/claimed_at null. COMMERCE-013 implementation
`4d52977` is architect accepted and all other explicit prerequisites are Complete.
No claim or automatic launch. Consume the actual backend via normal preparation.
Preserve native-basic monetary discount profiles as UNSUPPORTED while provider
rounding semantics are unproven; do not estimate savings or implement missing
provider semantics in this composition task. PostgreSQL adapter timeout diagnosis
and live infrastructure evidence remain separately developer-owned.
