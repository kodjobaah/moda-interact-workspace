---
id: ARCH-074
title: Recovery branding independent of billing scope
status: in_progress
coordinator: moda_architect
created: 2026-11-12
updated: 2026-11-12
---

# ARCH-074: Recovery branding independent of billing scope

## Status / Problem

In Progress. A normal/free billing contract correctly yields executionScope general, while the conversation remains durably recovery-linked. The new branded-image early guard incorrectly requires recovery billing scope, suppressing a legitimate AI recovery reply before provider admission. An empty pending placeholder can remain and the processor may report agent-response-sent despite suppression. This is a new bounded correction; completed ARCH-073 remains historical accepted functionality.

## Agreed Design / Ownership

Background keeps billing/usage policy unchanged. BRAND_IMAGE eligibility uses the existing current AiTurnOwnershipService durable Conversation→CheckoutRecovery identity with exact tenant/current AI control and original receipt checks, not the billing classification. An actual general/unbound conversation still cannot use a recovery brand image. Existing final Shop/recovery/consent/header/media/policy fences remain mandatory. No new local tenant inference, broad ownership fallback or control/version recapture.

Deterministic pre-provider refusal invokes existing conditional failPrepared cleanup, leaving no phantom unsent pending row. Existing already-admitted, duplicate, ambiguous provider-attempt and committed permits must not be rewritten or retried. Processor result handling/log outcome reflects suppression rather than claiming a provider send. Keep this change to the affected prepared-send path; no broad lifecycle refactor.

## Flow / State / Contracts

Unchanged billing admission -> exact durably linked current recovery/control proof -> original full body/media/receipt preparation -> existing moderation/current policy/source/control permit -> provider. PostgreSQL remains authority, existing queue contracts and conditional cleanup retained. No schema, Shared/publication, infrastructure or permission change.

## Security / Failure / Observability / Scale

Preserve exact Shop/recovery recipient/tenant, AI control/revision/inbound, STOP/consent, immutable media/header/public-origin identity and provider idempotency. Never authorize BRAND_IMAGE from caller/model executionScope alone. No external calls in transactions, new global serialisation or generic telemetry. Existing shared structured logging/semantic turn outcome suffices. This is action-path correctness, not a throughput claim.

## Rollout / Validation

PRODUCTION / COMPATIBLE ROLLOUT. Single Background source acceptance -> developer merge/deploy -> old worker drain -> fresh genuine customer question. No production requeue/reset/replay or extra diagnostic message is authorized by this task. Existing frozen evidence and billing contract semantics remain unchanged. Root verifies actual provider delivery only after deployment. Same-repository regression uses real PostgreSQL and genuine developer integrated proof; no separate system-test dependency is required.

## Tasks

| Task | Owner | State | Dependencies |
|---|---|---|---|
| ARCH-074-BACKGROUND-001 | moda_background | Ready | None |

## Completion Gate / Open Questions

Meaningful original-behavior red, normal/free contract recovery branded AI send, generic/unbound refusal, conditional cleanup and duplicate/uncertain-provider protection, relevant PostgreSQL and exact-head checks required. Architecture remains In Progress until fresh production delivery is verified. No blocking design question remains; no private customer/provider operational data belongs in public docs.
