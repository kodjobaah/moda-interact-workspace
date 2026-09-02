# Copilot Model Selection for Moda Interact Tasks

## Purpose

This document defines the recommended GitHub Copilot model to use for the remaining Moda Interact repository-agent implementation tasks.

The objective is to balance:

- implementation quality;
- task complexity;
- security and infrastructure risk;
- model capability;
- Copilot Pro+ token / AI-credit efficiency.

This document applies only to **repository-agent implementation and repository-level validation performed through Copilot**.

Architectural review is deliberately excluded.

Moda Interact uses a separate review path:

```text
Copilot repository agent
        |
        v
implement + validate task
        |
        v
status: review
        |
        v
STOP
        |
        v
package / ZIP relevant workspace state
        |
        v
ChatGPT acting as moda_architect
        |
        +-------------------+
        |                   |
        v                   v
     ACCEPT          CHANGES REQUESTED
        |                   |
        v                   v
    complete         return same task
                    to repository agent
```

Therefore, Copilot capacity should be planned around implementation work rather than architect-review usage.

---

## Model-selection principle

Use the least expensive model that is appropriate for the engineering risk and reasoning complexity of the task.

The normal hierarchy is:

```text
                   DEFAULT
                      |
                      v
                GPT-5.6 Terra
                 /          \
                /            \
      small / bounded       code-heavy
            |                   |
            v                   v
      GPT-5.6 Luna       GPT-5.3-Codex

                      |
                      | difficult / high-risk
                      v
                 GPT-5.6 Sol
```

### GPT-5.6 Luna

Use for small, bounded changes; deterministic endpoint work; lightweight instrumentation; straightforward service wiring; and low-risk repetitive implementation.

### GPT-5.6 Terra

Use as the default implementation model for normal application work, database/schema tasks, bounded authorization work, observability integration, routing/configuration, and infrastructure tasks whose architecture is already defined.

### GPT-5.3-Codex

Use for code-heavy refactoring, package/import migrations, TypeScript cleanup, build failures, iterative edit/build/test loops, and broad but mechanically constrained code changes.

### GPT-5.6 Sol

Reserve for authentication and session security, difficult infrastructure work, production topology, security validation, multi-service integration, performance investigations, complex queue/telemetry failures, and system-level debugging where several services may be involved.

---

## Remaining Copilot implementation tasks

Architectural tasks already at `status: review` are not included in this table because they are handed to ChatGPT acting as `moda_architect`.

| Task | Current state | Recommended Copilot model | Reason |
| --- | --- | --- | --- |
| `ARCH-001-GATEWAY-001` – Configure ARCH-001 deployment topology | Ready | **GPT-5.6 Terra** | Bounded infrastructure implementation with defined architecture |
| `ARCH-002-ADMIN-001` – Add admin health/readiness | Ready | **GPT-5.6 Luna** | Small, deterministic endpoint work |
| `ARCH-002-ADMIN-003` – Google platform-admin authentication/session foundation | Pending | **GPT-5.6 Sol** | Authentication/session security and higher blast radius |
| `ARCH-002-ADMIN-004` – Secure private Grafana Cloud observability access | Pending | **GPT-5.6 Sol** | Security, infrastructure and external observability boundary |
| `ARCH-002-ADMIN-005` – Protect admin pages/server reads | Pending | **GPT-5.6 Terra** | Bounded authorization implementation |
| `ARCH-002-ADMIN-006` – Protect mutations/route handlers | Pending | **GPT-5.6 Terra** | Bounded security-sensitive implementation |
| `ARCH-002-ADMIN-007` – Add admin security audit logging | Pending | **GPT-5.6 Terra** | Normal application implementation with clear scope |
| `ARCH-002-ADMIN-008` – Validate admin security boundary | Pending | **GPT-5.6 Sol** | Validation across several security controls and assumptions |
| `ARCH-002-ADMIN-009` – Shared observability runtime | In progress | **GPT-5.6 Terra** | Medium-complexity implementation already underway |
| `ARCH-002-ADMIN-010` – Bounded admin request metrics | Pending | **GPT-5.6 Luna** | Small instrumentation task |
| `ARCH-002-DATABASE-001` – Platform-admin identity registry | Ready | **GPT-5.6 Terra** | Schema, migration and integrity work |
| `ARCH-002-GATEWAY-003` – Render test/production deployment topology | Pending | **GPT-5.6 Sol** | Large infrastructure task with many dependencies and failure modes |
| `ARCH-002-GATEWAY-004` – Validate gateway/Render infrastructure | Pending | **GPT-5.6 Terra** | Structured infrastructure verification; escalate only if diagnosis becomes complex |
| `ARCH-002-GATEWAY-005` – Validate npm shared-package production builds | Pending | **GPT-5.3-Codex** | Build/debug/edit/test loop with code-heavy iteration |
| `ARCH-002-GATEWAY-006` – Configure OpenTelemetry infrastructure | Ready | **GPT-5.6 Terra** | Configuration and service integration with defined architecture |
| `ARCH-002-GATEWAY-007` – Host-based admin routing | Pending | **GPT-5.6 Terra** | Routing/configuration with bounded scope |
| `ARCH-002-MESSAGING-001` – Messaging health/readiness | Ready | **GPT-5.6 Luna** | Small deterministic service task |
| `ARCH-002-SHOPIFY-004` – Use published shared package | Ready | **GPT-5.3-Codex** | Package/import/build migration across existing code |
| `ARCH-002-SHOPIFY-005` – Eliminate TypeScript baseline debt | Ready | **GPT-5.3-Codex** | Broad code-heavy cleanup and iterative compilation |
| `ARCH-002-SYSTEM-TEST-001` – Validate integrated test/production topology | Pending | **GPT-5.6 Sol** | Cross-service integration and difficult failure diagnosis |
| `ARCH-002-SYSTEM-TEST-002` – Validate observability + WhatsApp performance | Pending | **GPT-5.6 Sol** | Performance, queues, telemetry and multi-service behaviour |

Tasks already in architect review and therefore intentionally excluded from the Copilot implementation schedule:

```text
ARCH-001-BACKGROUND-001
ARCH-001-SHOPIFY-001
```

If the architect requests changes, return the existing task to the appropriate repository agent and normally continue with the same implementation model recommended for that task.

---

## Recommended model distribution

For the currently defined remaining Copilot implementation work:

| Model | Tasks | Approximate share |
| --- | ---: | ---: |
| **GPT-5.6 Luna** | 3 | 14% |
| **GPT-5.6 Terra** | 8 | 38% |
| **GPT-5.3-Codex** | 3 | 14% |
| **GPT-5.6 Sol** | 7 | 33% |
| **Total** | **21** | **100%** |

This allocation is intentionally weighted toward stronger models for the remaining security, deployment and integrated-system work.

It does **not** mean every task should begin with the most capable model.

---

## Escalation rule

Do not restart an entire task with a more expensive model merely because the initial model encounters a problem.

Escalate only when the nature of the problem changes.

For example:

```text
GPT-5.6 Luna
     |
     | task proves less trivial than expected
     v
GPT-5.6 Terra
```

For code-heavy work:

```text
GPT-5.6 Terra
     |
     | broad mechanical edits / build-fix loop
     v
GPT-5.3-Codex
```

For difficult engineering problems:

```text
GPT-5.6 Terra
     |
     | architectural ambiguity
     | security uncertainty
     | complex infrastructure behaviour
     | concurrency / queue failure
     | unexplained cross-service integration failure
     v
GPT-5.6 Sol
```

The stronger model should be used to resolve the difficult portion of the task, not automatically replay all work already completed successfully.

---

## Architect-review boundary

Repository agents must follow the normal Moda Interact task lifecycle:

```text
ready
  |
  v
in_progress
  |
  | implement + repository validation
  v
review
  |
  v
STOP
```

At `status: review`, Copilot work stops.

The task is then reviewed separately through ChatGPT acting as `moda_architect`.

ChatGPT may:

```text
accept task
    -> status: complete

request changes
    -> return same task to repository agent

identify new architectural dependency
    -> architect creates / sequences appropriate work
```

Copilot should not consume additional model budget performing an independent architect review of work that is already being reviewed through the separate architecture workflow.

---

## Cost-control rules

To keep Copilot Pro+ usage efficient:

1. Start with the model assigned in this document.
2. Do not use GPT-5.6 Sol for routine implementation merely because it is the strongest available model.
3. Prefer GPT-5.3-Codex for broad mechanical code/build work rather than using Sol as a general-purpose refactoring model.
4. Use GPT-5.6 Luna for genuinely small and deterministic tasks.
5. Use GPT-5.6 Terra as the normal implementation default.
6. Escalate to Sol only when the task involves high-risk reasoning or when a cheaper model exposes a genuinely difficult problem.
7. Stop Copilot execution when the task reaches `status: review`.
8. Perform architect review through the separate ChatGPT workflow.
9. If changes are requested, continue the existing task rather than starting a new implementation conversation unnecessarily.
10. Continue reducing startup context by using deterministic task routing, metadata-first dependency checks and workspace scripts.

The governing principle is:

> **Spend expensive model reasoning where engineering judgement is expensive; use cheaper models and deterministic tooling everywhere else.**

---

## Updating this document

This table is a planning guide for the currently defined task graph.

Revisit the recommendation when:

- the architect changes the task scope;
- a task gains significant new dependencies;
- implementation reveals substantially greater complexity;
- a task is split into smaller tasks;
- a task is superseded;
- the available Copilot model set changes;
- real usage data shows that a different model provides a better cost/performance balance.

Task status and task files remain authoritative. This document does not override the architecture or task definitions.
