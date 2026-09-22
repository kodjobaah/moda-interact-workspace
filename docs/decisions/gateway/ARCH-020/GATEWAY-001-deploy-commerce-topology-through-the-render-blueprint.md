---
id: ARCH-020-GATEWAY-001
architecture_id: ARCH-020
title: Deploy Commerce topology through the Render Blueprint
task_kind: implementation
domain: gateway
repository: moda-interact-gateway
assigned_agent: moda_gateway
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 180
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-020-COMMERCE-002
  - ARCH-020-BACKGROUND-001
  - ARCH-020-COMMERCE-008
  - ARCH-020-COMMERCE-011
  - ARCH-020-COMMERCE-013
  - ARCH-020-COMMERCE-017
  - ARCH-020-COMMERCE-018
  - ARCH-020-COMMERCE-019
enables:
  - ARCH-020-COMMERCE-012
  - ARCH-020-SYSTEM-TEST-001
  - ARCH-020-GATEWAY-002
  - ARCH-020-GATEWAY-003
created: 2026-09-20
updated: 2026-09-20
---

# Deploy Commerce topology through the Render Blueprint

## Architecture

Architecture ID: ARCH-020.

Architecture document: docs/architecture/ARCH-020-commerce-agent-studio-mcp-capabilities.md.

Coordinator: moda_architect. Read the complete parent architecture and relevant dependency/contract tasks. Execution handoff: docs/architecture/ARCH-020-implementation-handoff.md.

## Objective

Codify the new independent Commerce service and its private MCP/public staff routing.

## Context

Merchant-selected capabilities should drive WhatsApp CommerceAgent behaviour through a separate Next.js MCP server with a team-only Studio. Production conversation admission, ordering, model hosting and delivery remain in Background. This is a pre-production breaking rollout, with no implicit permission to delete durable data.

Task definition is on local workspace main by the developer's explicit 2026-09-20 review request. It is not a claim, task-branch materialisation or implementation approval. All execution fields remain unclaimed.

## Scope

Gateway render.yaml, reverse proxy rules, secret-name declarations, health/timeout and deployment documentation.

## Out of Scope

Other repositories' implementation, unrelated refactoring, automatic execution of enabled tasks, live deployment, main integration/push and changes to billing prices/merchant entitlements. No cart/order/discount mutation, WhatsApp sending from Commerce, arbitrary executable code or arbitrary-host HTTP endpoints; C14 validated read-only GraphQL definitions are explicitly permitted. No duplicate discount catalogue/merchant configuration system. Shared indexes and architecture reconciliation remain architect-owned.

## Requirements

Follow the parent architecture's tenant/policy/revision contracts and the assigned logical owner. Preserve unrelated changes. Read repository-local AGENTS.md if present. Commerce consumes the canonical database through its nested database/ Git submodule; schema and migrations belong to moda_database. For consumers, use actual accepted and published dependency revisions, not copied task snapshots or hypothetical versions.

## Work Items

- [ ] Apply C7.1 hosted auth configuration: Google-only AUTH_* variables and a non-development DEPLOYMENT_ENVIRONMENT_NAME. No Render service enables the local SUPER_ADMIN override; production runtime plus development override must fail closed. Keep the private MCP assertion boundary independent of Studio auth.

- [ ] Allow exactly the C15/U01–U14 UI routes and documented studio/auth methods; add /features, /tools, /explore and /shops index plus detail routes. Discovery endpoints remain staff-authorized, not a public MCP proxy.
- [ ] Provision the COMMERCE-011 supervised stdio runtime/schema artifacts in the Commerce build, no extra port/service/credentials. Add optional server-only ADMIN_ORIGIN for Admin navigation. Redis is required for discovery rate limits. Child failure degrades docs search without disabling live MCP or local schema editing.

- [ ] Inspect accepted Commerce build/start/port/health contracts and recursive database generation requirements before defining the service.
- [ ] Add a private Render service for Commerce and an authenticated team UI host through the public gateway; block public MCP routes, transport aliases and normalised/encoded variants. Use an explicit staff UI/auth route allowlist rather than a blanket proxy.
- [ ] Wire Background private MCP URL and separate staff OAuth, database, assertion-verification/signing and preview-model secret names plus existing platform Redis connectivity for bounded cross-replica preview deduplication. No new Redis service is required. Only Background receives production signing keys; Commerce receives verification keys. Other services and browser/admin identities are not authorised live MCP callers.
- [ ] Configure bounded streaming/body/timeout behaviour compatible with the selected MCP client/server and environment identity.
- [ ] Document additive migration ordering, affected-worker pause/resume, initial release publication, resource preservation and coordinated pre-production rollback.

## Interfaces / Contracts

Canonical moda-interact-gateway/render.yaml; actual repository/host identity supplied during setup, not guessed.

### Implementation guidance

Binding companion: [ARCH-020 implementation contracts](../../../architecture/ARCH-020-implementation-contracts.md), sections **C3, C5, C9, C10**. These are required acceptance inputs, not optional examples.

Use canonical render.yaml and actual provisioned repository/Studio host inputs. Wire the messaging worker-only signing keys and Commerce verification keys. Explicit proxy allowlist covers server-action POSTs, auth callbacks, UI/static assets but never MCP; reject ambiguous encoded paths before upstream. No separate Redis service. Deliver docs/commerce-deployment.md with exact command/health/private/public expectations.

### Deterministic review clarification

Apply C9.1 exact preview routes/methods to the public Studio allowlist; no
blanket /api/studio proxy. C10 includes AUTH_URL matching COMMERCE_STUDIO_ORIGIN.
Wire WHATSAPP_TRANSCRIPTION_PROVIDER=groq|openai on the messaging worker;
omitted/blank selects groq, other values fail closed. GROQ_TRANSCRIPTION_MODEL
defaults to whisper-large-v3-turbo and uses GROQ_API_KEY. OpenAI selection uses
OPENAI_TRANSCRIPTION_MODEL (default gpt-4o-mini-transcribe) and messaging-only
WHATSAPP_OPENAI_API_KEY, never translation-worker OPENAI_API_KEY. Model IDs are
1–128 characters, start alphanumeric and contain only alphanumeric, dot, underscore
or hyphen. No automatic provider/model fallback. Test and production settings are
independent. Validate blueprint wiring without paid provider calls or deployment;
record provider-quality evidence separately. Reconcile these names against the
accepted BACKGROUND-001 handoff before publishing configuration.

Preview MODEL wiring is separately fixed by C10/COMMERCE-033. Declare
`COMMERCE_PREVIEW_ENABLED`, `COMMERCE_PREVIEW_PROVIDER`,
`COMMERCE_PREVIEW_MODEL` and secret `COMMERCE_PREVIEW_API_KEY` on the Commerce
service; never expose them as `NEXT_PUBLIC_*`. Test/development hosted configuration is
`COMMERCE_PREVIEW_ENABLED=true`, `COMMERCE_PREVIEW_PROVIDER=groq`,
`COMMERCE_PREVIEW_MODEL=openai/gpt-oss-20b`; the API key is an external Render secret.
Production provider/model are independently configurable. Allowed providers are exactly
`openai|groq`; no fallback and no configurable preview base URL. Gateway only wires the
variables; Commerce owns provider HTTP behavior. No paid provider call is required for
Blueprint acceptance.

### Required evidence

Use existing gateway validation shell/config tooling (repository has no package.json; do not invent npm build). Add deterministic host/path/method fixtures with stub upstream; include direct private calls missing credentials and each public encoded/alias MCP attempt. Deployment credentials/real hosts remain external inputs.

For this task, record a requirement-to-fixture matrix with expected side effects, actual commands and results in the Completion Report. Do not implement another repository's changes to bypass a dependency.

## Dependencies

- ARCH-020-COMMERCE-002
- ARCH-020-BACKGROUND-001
- ARCH-020-COMMERCE-008
- ARCH-020-COMMERCE-011
- ARCH-020-COMMERCE-013
- ARCH-020-COMMERCE-017
- ARCH-020-COMMERCE-018
- ARCH-020-COMMERCE-019

All dependencies must be Complete and architect-accepted before execution.

## Enables

- ARCH-020-COMMERCE-012
- ARCH-020-SYSTEM-TEST-001
- ARCH-020-GATEWAY-002
- ARCH-020-GATEWAY-003

- ARCH-020-SYSTEM-TEST-001
- ARCH-020-GATEWAY-002

## Acceptance Criteria

- [ ] Coordinate BACKGROUND-001 A2/C6.3 transcription configuration: the exact provider/model selector names, values/defaults and credentials below must reach the messaging worker in independent test/production settings. Preserve Groq; OpenAI is explicit, with gpt-4o-mini-transcribe the OpenAI-only default. No automatic fallback. Existing translation-worker OpenAI group is not messaging configuration; scope secrets narrowly rather than importing unrelated translation settings. Background owns any evidence-required conversion/image dependency; Gateway verifies runtime/resources and records explicit rollout/rollback. Configuration checks do not require paid live transcription.

- [ ] Public staff can traverse all pages and authenticated discovery operations, but cannot access /api/mcp or invoke arbitrary developer/CLI tools; child process receives no production credentials.

- [ ] Blueprint references the real new repository and correct commands; no credentials or invented remote/host are committed.
- [ ] Browser-accessible staff routes work through the gateway while public MCP requests are denied and private MCP accepts only Background service assertions. Another private-network service without that identity and an administrator browser session are both denied.
- [ ] Fresh builds initialise database recursively; service startup does not run migrations or destroy durable resources.

## Validation

- [ ] Run local Blueprint/proxy syntax and route fixture checks covering POST/GET/OPTIONS, encoded/trailing-path/alias attempts, direct private calls without Background identity and authenticated staff UI access and git diff --check.
- [ ] Provide exact developer-owned deployment/smoke commands with expected private/public/health outcomes; no live deployment is implied by task definition.

Use package.json commands actually provided by the repository. New Commerce scripts and test fixtures are deliverables, not claims that they exist today. Follow docs/agent-validation-execution-policy.md and docs/agent-live-validation-execution-policy.md. Separate local evidence from pending developer-owned long/live validation; required evidence must exist before acceptance.

## Stop Condition

After scoped work and agent-owned checks, update this task's execution/report fields, publish task-owned mirrored branches and return to review. Record exact pending developer validation where applicable. Stop; do not begin enabled tasks or mark your own task Complete. Publication tasks stop after release mechanics. System tests require explicit developer invocation even after becoming Ready.

## Implementation Notes

Normal execution uses /moda-task and scripts/start-agent-task.py preparation, dedicated parent and implementation worktrees, synchronization and recursive submodule initialisation. Follow docs/agent-vcs-ownership-policy.md, docs/agent-worktree-isolation-policy.md and docs/task-definition-materialization.md. The main-only exception applies to this review draft, not task execution. The COMMERCE route is registered in this packet; its real repository must be provisioned before execution preparation.

## Completion Report

### Status

Not Started.

### Files Changed

None; implementation has not started.

### Work Completed

None; task definition only.

### Validation Results

Not run. At execution, distinguish agent checks from exact developer validation required.

### Deviations

Task definition authored on local main by explicit developer request. Normal execution policy remains unchanged.

### Assumptions

Use the parent architecture and actual accepted dependency revisions. Return contradictory source facts to moda_architect.

### Unresolved Issues

See parent architecture review assumptions; no implementation evidence asserted.

### Architectural Concerns

None newly reported.

### Git / VCS

Expected execution branch: task/ARCH-020-GATEWAY-001. Attempt: 0. No implementation worktree, commit, push or validation is asserted. At submission record canonical workspace, both physical worktrees/branches, synchronization, recursive database submodule SHA/evidence, implementation and parent commit/push results, and confirmation that no parent service gitlink or main integration was performed.

## Architect Review

### Review Status

Pending.

### Review Notes

No implementation submitted. This task is a reviewable definition.

### Reviewed Files

None for implementation review.

### Validation Reviewed

None for implementation review.

### Architecture Conformance

Awaiting implementation.

### Follow-up

Reconcile task/index/frontier after review; preserve the terminal/manual system-test gate.
