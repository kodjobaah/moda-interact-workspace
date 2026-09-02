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

Moda Interact uses a **Luna-first** implementation strategy.

The architecture workflow deliberately keeps repository tasks bounded, gives the
agent explicit scope and acceptance criteria, resolves ownership and routing
deterministically, and sends completed work to ChatGPT acting as
`moda_architect` for independent review.

That means the repository agent normally does not need to rediscover the
architecture or independently decide the shape of the entire system.

The default strategy is therefore:

```text
                    START
                      |
                      v
                GPT-5.6 Luna
                      |
             task progressing?
                /           \
              yes            no
               |              |
               v              v
           continue      classify problem
                              |
                 +------------+------------+
                 |            |            |
                 v            v            v
              Terra     GPT-5.3-Codex     Sol
            reasoning      code/build    difficult /
                                         high-risk
```

The governing rule is:

> **Start bounded implementation work on Luna and escalate only when observed
> task behaviour justifies a stronger or more specialised model.**

This is deliberately different from assigning an expensive model up front
because a task belongs to security, infrastructure or system testing.

Risk still matters, but it is handled through:

- bounded task scope;
- explicit acceptance criteria;
- focused repository validation;
- deterministic task routing and ownership;
- independent `moda_architect` review;
- escalation when implementation reveals genuine ambiguity or complexity.

### GPT-5.6 Luna — default first-pass implementation model

Use Luna first for all normal bounded repository-agent tasks, including:

- small endpoint changes;
- database/schema tasks whose required change is explicit;
- authorization and security implementation with defined acceptance criteria;
- observability integration;
- routing/configuration;
- straightforward infrastructure-as-code changes;
- package migrations;
- focused system-test implementation;
- repetitive but bounded implementation work.

Luna should continue the task while it is making coherent progress and can
validate the required acceptance criteria.

### GPT-5.6 Terra — escalation for non-trivial reasoning

Escalate from Luna to Terra when implementation reveals reasoning difficulty
rather than merely a large number of edits.

Typical triggers include:

- unclear interaction between several existing abstractions;
- non-obvious framework behaviour;
- difficult debugging whose cause is not local;
- architectural ambiguity inside an otherwise bounded task;
- security behaviour whose correctness cannot be established from the existing
  task and tests;
- infrastructure behaviour that is not explained by the declared configuration.

Do not escalate merely because a task is labelled "security",
"infrastructure" or "database".

### GPT-5.3-Codex — escalation for broad code/build loops

Use GPT-5.3-Codex when the dominant problem becomes a broad mechanical
software-development loop, such as:

- repository-wide TypeScript cleanup;
- package/import migration across many files;
- repeated edit/build/typecheck cycles;
- production-build failures;
- mechanically constrained refactoring across a large code surface.

A task may begin on Luna and move to GPT-5.3-Codex only when this pattern is
actually encountered.

### GPT-5.6 Sol — escalation for genuinely difficult/high-risk problems

Reserve Sol for cases where Luna/Terra exposes a genuinely difficult problem,
for example:

- unresolved authentication/session-security behaviour;
- complex production infrastructure/networking failures;
- difficult multi-service integration;
- concurrency or queue correctness issues;
- performance diagnosis involving several system boundaries;
- security uncertainty that cannot be resolved from the existing contracts and
  tests;
- unexplained system-level failures spanning several repositories.

Sol should solve the difficult portion of the task rather than replaying work
that Luna has already completed successfully.

### Task decomposition feedback

Repeated Luna difficulty is also a signal about task shape.

Before automatically escalating a task, ask whether the task has become too
large or contains more than one independently reviewable outcome.

```text
Luna repeatedly loses coherence
          |
          +--> genuinely difficult engineering problem
          |        -> escalate model
          |
          +--> task contains several distinct outcomes
                   -> return to moda_architect for decomposition
```

A stronger model should not be used to hide poor task decomposition.

---

## Remaining Copilot implementation tasks

Architectural tasks already at `status: review` are not included in this table
because they are handed to ChatGPT acting as `moda_architect`.

The **starting model** is Luna for every active bounded implementation task.
The escalation column identifies the most likely next model only if the task
reveals the stated difficulty.

| Task | Current state | Starting model | Escalate only if... |
| --- | --- | --- | --- |
| `ARCH-001-GATEWAY-001` – Configure ARCH-001 deployment topology | Ready | **GPT-5.6 Luna** | Infrastructure behaviour becomes non-obvious -> Terra; difficult topology/networking issue -> Sol |
| `ARCH-002-ADMIN-001` – Add admin health/readiness | Ready | **GPT-5.6 Luna** | No expected escalation for normal implementation |
| `ARCH-002-ADMIN-003` – Google platform-admin authentication/session foundation | Pending | **GPT-5.6 Luna** | Session/security correctness becomes ambiguous -> Terra; unresolved high-risk security issue -> Sol |
| `ARCH-002-ADMIN-004` – Secure private Grafana Cloud observability access | Pending | **GPT-5.6 Luna** | Access/security/infrastructure behaviour is unclear -> Terra; unresolved external/security boundary -> Sol |
| `ARCH-002-ADMIN-005` – Protect admin pages/server reads | Pending | **GPT-5.6 Luna** | Authorization behaviour cannot be established from existing contracts/tests -> Terra |
| `ARCH-002-ADMIN-006` – Protect mutations/route handlers | Pending | **GPT-5.6 Luna** | Security semantics become non-local or ambiguous -> Terra/Sol |
| `ARCH-002-ADMIN-007` – Add admin security audit logging | Pending | **GPT-5.6 Luna** | Logging/security behaviour crosses unexpected boundaries -> Terra |
| `ARCH-002-ADMIN-008` – Validate admin security boundary | Pending | **GPT-5.6 Luna** | Validation exposes ambiguous or cross-cutting security failures -> Terra/Sol |
| `ARCH-002-ADMIN-009` – Shared observability runtime | In progress | **GPT-5.6 Luna** | Framework/provider integration becomes non-trivial -> Terra |
| `ARCH-002-ADMIN-010` – Bounded admin request metrics | Superseded | — | No implementation required |
| `ARCH-002-DATABASE-001` – Platform-admin identity registry | Ready | **GPT-5.6 Luna** | Schema/integrity implications are unclear or migration behaviour becomes non-trivial -> Terra |
| `ARCH-002-GATEWAY-003` – Render test/production deployment topology | Pending | **GPT-5.6 Luna** | Configuration work exposes difficult Render/network/topology reasoning -> Terra/Sol; consider task decomposition if scope becomes incoherent |
| `ARCH-002-GATEWAY-004` – Validate gateway/Render infrastructure | Pending | **GPT-5.6 Luna** | Validation reveals unexplained infrastructure behaviour -> Terra/Sol |
| `ARCH-002-GATEWAY-005` – Validate npm shared-package production builds | Pending | **GPT-5.6 Luna** | Work becomes a broad iterative build/fix loop -> **GPT-5.3-Codex** |
| `ARCH-002-GATEWAY-006` – Configure OpenTelemetry infrastructure | Ready | **GPT-5.6 Luna** | Telemetry/configuration integration becomes non-obvious -> Terra |
| `ARCH-002-GATEWAY-007` – Host-based admin routing | Pending | **GPT-5.6 Luna** | Routing/security behaviour becomes ambiguous -> Terra |
| `ARCH-002-MESSAGING-001` – Messaging health/readiness | Ready | **GPT-5.6 Luna** | No expected escalation for normal implementation |
| `ARCH-002-SHOPIFY-004` – Use published shared package | Ready | **GPT-5.6 Luna** | Migration expands into many mechanical code/build fixes -> **GPT-5.3-Codex** |
| `ARCH-002-SHOPIFY-005` – Eliminate TypeScript baseline debt | Ready | **GPT-5.6 Luna** | Repository-wide iterative type/build cleanup dominates the task -> **GPT-5.3-Codex** |
| `ARCH-002-SYSTEM-TEST-001` – Validate integrated test/production topology | Pending | **GPT-5.6 Luna** | Cross-service diagnosis becomes difficult -> Terra; unresolved multi-service/system failure -> Sol |
| `ARCH-002-SYSTEM-TEST-002` – Validate observability + WhatsApp performance | Pending | **GPT-5.6 Luna** | Performance/telemetry diagnosis crosses several boundaries -> Terra/Sol |

Tasks already in architect review and therefore intentionally excluded from the
Copilot implementation schedule:

```text
ARCH-001-BACKGROUND-001
ARCH-001-SHOPIFY-001
```

If the architect requests changes, return the existing task to the appropriate
repository agent. Normally restart the implementation on Luna unless the
architect's feedback specifically identifies a reason to escalate.

---

## Recommended starting-model distribution

For the task snapshot represented in this document, every active bounded
repository implementation task starts on Luna.

| Starting model | Active tasks | Role |
| --- | ---: | --- |
| **GPT-5.6 Luna** | **20** | Default first-pass implementation |
| **GPT-5.6 Terra** | 0 initially | Escalation for non-trivial reasoning/debugging |
| **GPT-5.3-Codex** | 0 initially | Escalation for broad mechanical code/build loops |
| **GPT-5.6 Sol** | 0 initially | Escalation for genuinely difficult/high-risk problems |
| **Superseded / no implementation** | 1 | No model required |

The important metric is not how many tasks are pre-assigned to a stronger
model. It is how many tasks Luna can complete coherently before an explicit
escalation trigger occurs.

This makes actual model usage a feedback signal for both cost and task quality.

---

## Escalation rule

Do not restart an entire task with a more expensive model merely because Luna
encounters friction.

First classify the problem:

```text
Luna
  |
  +--> bounded task still clear and progressing
  |        -> continue on Luna
  |
  +--> non-trivial reasoning/debugging
  |        -> Terra
  |
  +--> broad mechanical edit/build/typecheck loop
  |        -> GPT-5.3-Codex
  |
  +--> difficult high-risk security/infrastructure/
  |    concurrency/system problem
  |        -> Sol
  |
  +--> task contains several independently useful outcomes
           -> stop and return to moda_architect for decomposition
```

When escalating, preserve the existing task state and completed work. The
stronger model should resolve the difficult portion rather than replaying the
task from the beginning.

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

1. Start every normal bounded repository implementation task on GPT-5.6 Luna.
2. Keep Luna on the task while it remains coherent, bounded and able to satisfy
   the defined validation.
3. Do not pre-assign Sol merely because a task is security-, infrastructure-,
   database- or system-test-related.
4. Escalate to Terra when the implementation reveals genuinely non-trivial
   reasoning or debugging.
5. Escalate to GPT-5.3-Codex when the dominant work becomes a broad mechanical
   code/build/typecheck loop.
6. Escalate to Sol only for genuinely difficult/high-risk problems that remain
   unresolved at the cheaper reasoning level.
7. Treat repeated model difficulty as a possible task-decomposition problem,
   not automatically as a need for a stronger model.
8. Stop Copilot execution when the task reaches `status: review`.
9. Perform architect review through the separate ChatGPT workflow.
10. If changes are requested, continue the existing task rather than starting a
    new implementation conversation unnecessarily.
11. Continue reducing startup context with deterministic task routing,
    metadata-first dependency checks and workspace scripts.

The governing principle is:

> **Luna first for bounded implementation; escalate on evidence, not labels.**

A complementary engineering principle is:

> **Use model context for judgement and implementation; use deterministic
> tooling for routing, ownership, synchronization and workflow mechanics.**

---

## Updating this document

This table is a planning guide for the currently defined task graph.

Task status and task files remain authoritative. This document does not override
the architecture or task definitions.

Revisit the recommendation when:

- the architect changes task scope;
- a task gains significant new dependencies;
- implementation reveals substantially greater complexity;
- Luna repeatedly struggles with a supposedly bounded task;
- a task should be split into smaller independently reviewable outcomes;
- a task is superseded;
- the available Copilot model set changes;
- real Copilot usage shows that another escalation threshold gives a better
  cost/performance balance.

The preferred policy remains:

```text
bounded task
    -> Luna

observed difficulty
    -> targeted escalation

architectural acceptance
    -> ChatGPT / moda_architect
```
