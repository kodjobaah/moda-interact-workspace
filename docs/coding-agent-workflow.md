# Moda Interact Coding Agent Workflow

## Overview

Moda Interact uses coding agents as part of a structured engineering workflow rather than as standalone coding assistants.

The core idea is simple:

> **Conversation is temporary execution context. The repository is durable engineering state.**

Instead of relying on a long-running chat to remember architecture, ownership, dependencies and implementation status, those concerns are recorded in version-controlled files that any compatible coding agent can read.

This makes the workflow portable across execution environments such as Codex, Claude, Continue and other capable coding agents.

---

## Why this workflow exists

A typical coding-agent workflow looks like this:

```text
Developer
    |
    v
"Implement feature X"
    |
    v
Coding agent
    |
    v
Explore repository
    |
    v
Edit files
    |
    v
Developer reviews diff
```

That works well for many local tasks, but becomes less reliable when a system spans:

- multiple repositories;
- shared database models;
- queue/event contracts;
- asynchronous workers;
- webhook producers and consumers;
- deployment sequencing;
- idempotency requirements;
- tenant isolation;
- shared runtime schemas;
- multiple AI execution environments;
- integrated architecture/system validation.

Moda Interact therefore adds a coordination layer above the individual coding agent.

---

# Agent organisation

The platform uses logical engineering roles:

```text
moda_architect
├── moda_admin
├── moda_app
├── moda_background
├── moda_database
├── moda_gateway
├── moda_messaging
├── moda_shared
├── moda_site
└── moda_system_test
```

Each logical agent has a bounded responsibility.

| Agent | Primary responsibility |
| --- | --- |
| `moda_architect` | Cross-repository architecture, decomposition, dependencies, sequencing, review and integration |
| `moda_app` | Shopify app, merchant UI, Shopify ingress, onboarding, billing and subscriptions |
| `moda_background` | BullMQ workers, event processing, recovery workflows, CommerceAgent and retryable background work |
| `moda_database` | Prisma schema, PostgreSQL migrations, constraints, indexes, canonical/reference seed data and durable integrity |
| `moda_gateway` | Public ingress, reverse proxy, Render topology, infrastructure-as-code, scaling configuration and infrastructure wiring |
| `moda_messaging` | Meta/WhatsApp webhook ingress, validation, normalisation and queue publication |
| `moda_shared` | Canonical cross-service runtime contracts and shared primitives |
| `moda_admin` | Platform administration, reporting and operational visibility |
| `moda_site` | Public website, product content and SEO |
| `moda_system_test` | Architecture-level system tests, architecture-specific test fixtures/seed data, environment orchestration and integrated validation |

Repository ownership is explicit.

For example:

```text
moda_app
    -> moda-interact/

moda_background
    -> moda-interact-background/

moda_database
    -> moda-interact-database/

moda_gateway
    -> moda-interact-gateway/

moda_shared
    -> moda-interact-shared/

moda_system_test
    -> moda-interact-system-test/
```

This reduces the chance that an implementation agent silently expands a task into unrelated repositories.

---

# Architect and repository-agent separation

The architect coordinates work rather than implementing substantial repository-specific changes when an owner agent exists.

The normal flow is:

```text
User
  |
  v
moda_architect
  |
  | inspect current code
  | define architecture
  v
Architecture document
  |
  | decompose into bounded tasks
  v
Repository implementation tasks
  |
  v
Specialist repository agents
  |
  | implement + validate
  v
status: review
  |
  v
moda_architect
  |
  | inspect actual implementation
  v
implementation task: complete
  |
  | once all dependencies required for integrated validation are complete
  v
moda_system_test
  |
  | prepare environment + fixtures
  | run architecture-level system scenarios
  v
status: review
  |
  v
moda_architect
  |
  | inspect system-test evidence
  v
system-test task: complete
  |
  v
architecture: implemented
```

The implementation agent does **not** decide that its own architectural task is complete.

Likewise, `moda_system_test` does not decide that its own system-test task is complete.

Only `moda_architect` can transition:

```text
review -> complete
```

For architectures that require integrated runtime validation, repository implementation tasks being complete does **not** by itself make the architecture implemented. The required system-test task or tasks must also be reviewed and completed.

This creates a separation similar to implementation, independent system validation and review in a human engineering team.

---

# Architecture-level system validation

`moda_system_test` provides a distinct validation phase after the required architectural implementation has been completed.

It owns:

```text
moda-interact-system-test/
```

and its architecture decision domain is:

```text
docs/decisions/system-test/
```

System-test task IDs use:

```text
ARCH-XXX-SYSTEM-TEST-NNN
```

For example:

```text
ARCH-001-SYSTEM-TEST-001
```

## Purpose

Repository agents validate their bounded implementation.

For example:

```text
moda_app
    -> validates Shopify-app implementation

moda_background
    -> validates worker/background implementation

moda_database
    -> validates schema/migrations

moda_shared
    -> validates shared contracts
```

`moda_system_test` validates that the required parts work together as the architecture describes:

```text
repository-level validation
          |
          v
implementation tasks complete
          |
          v
moda_system_test
          |
          v
integrated architecture behaviour
```

It should test externally observable architecture behaviour rather than duplicate every unit test owned by repository agents.

## Environment orchestration

For a system-test task, `moda_system_test` is responsible for preparing the local environment required by the parent architecture.

This can include:

- starting the PostgreSQL Docker container used for local testing;
- using the standard local Moda Interact PostgreSQL database defined by the workspace;
- assuming Redis is already running, but verifying connectivity before dependent tests begin;
- starting Shopify development through the existing commands in `moda-interact/`;
- starting background, messaging or other Moda Interact services when the scenario requires them;
- collecting relevant service logs and evidence.

The system-test agent may execute commands in other repositories for startup and observation.

That operational access does **not** transfer implementation ownership.

If startup or execution exposes a defect in another repository, `moda_system_test` records the failure and returns it to `moda_architect`.

It must not silently modify the owning repository to make the system test pass.

## Architecture-specific test fixtures and seed data

`moda_system_test` owns the data required specifically to execute architecture-level system scenarios.

Examples include:

- architecture-specific local database records;
- deterministic test customers;
- checkout/recovery scenarios;
- conversation/message fixtures;
- task-specific identifiers;
- other test state required by the architecture.

The ownership boundary is:

```text
moda_database
    -> canonical/permanent application or reference seed data

moda_system_test
    -> architecture-specific system-test fixtures and seed data
```

This avoids turning system-test setup into ownership of permanent application data.

System-test fixtures should be deterministic, repeatable and idempotent where practical.

## Shopify-side test data

When a system scenario requires a Shopify customer, `moda_system_test` uses the Shopify API to find or create the required test customer.

The fixture flow should be:

```text
determine stable test identifier
          |
          v
search Shopify for existing test customer
          |
     +----+----+
     |         |
   found     missing
     |         |
     v         v
   reuse     create
     |         |
     +----+----+
          |
          v
continue system scenario
```

The agent should reuse existing deterministic fixtures where possible rather than create uncontrolled duplicates.

Shopify credentials and access tokens must come from the configured development environment and must not be hard-coded into the system-test repository.

The agent must not delete or mutate unrelated merchant data.

## Failure ownership

When a system test fails, the system-test task should record:

- scenario;
- expected behaviour;
- actual behaviour;
- test command;
- relevant logs;
- database state where useful;
- queue state where useful;
- Shopify state where useful;
- likely failing service/repository where it can be identified.

The failure is then returned to `moda_architect`.

The architect decides which repository agent owns the follow-up implementation work.

## Architecture completion gate

For architectures that require integrated system validation:

```text
implementation tasks complete
          |
          v
system-test task ready
          |
          v
moda_system_test executes scenarios
          |
          v
status: review
          |
          v
moda_architect reviews evidence
          |
          v
system-test task complete
          |
          v
architecture implemented
```

If integrated system testing is not applicable to a particular architecture, that should be explicit in the architecture document rather than assumed.

---

# Architecture initiatives

Cross-repository work is organised into architecture initiatives.

Examples:

```text
ARCH-001
ARCH-002
ARCH-003
```

An architecture ID identifies an initiative, not an individual implementation task.

An architecture document may look like:

```text
docs/architecture/ARCH-001-shopify-webhook-reliability.md
```

The document describes the complete design:

- problem being solved;
- affected repositories;
- workload assumptions;
- data flow;
- contracts;
- transaction boundaries;
- deployment order;
- scalability considerations;
- security constraints;
- migration requirements.

---

# Architecture task decomposition

The architect decomposes an architecture into domain-owned tasks.

Example:

```text
ARCH-001
├── ARCH-001-SHARED-001
├── ARCH-001-DATABASE-001
├── ARCH-001-SHOPIFY-001
├── ARCH-001-BACKGROUND-001
└── ARCH-001-SYSTEM-TEST-001
```

The task files live under the owning decision domain:

```text
docs/decisions/
├── shared/
│   └── ARCH-001/
│       └── SHARED-001-define-recovery-webhook-contracts.md
├── database/
│   └── ARCH-001/
├── shopify/
│   └── ARCH-001/
├── background/
│   └── ARCH-001/
└── system-test/
    └── ARCH-001/
        └── SYSTEM-TEST-001-validate-recovery-webhook-flow.md
```

A task contains both human-readable implementation instructions and machine-readable execution metadata.

Example:

```yaml
---
id: ARCH-001-BACKGROUND-001
architecture_id: ARCH-001
title: Consume versioned Shopify event
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
status: ready
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-001-SHARED-001
enables: []
created: 2026-08-28
updated: 2026-08-28
---
```

This means an agent can discover:

- what it owns;
- whether the task is executable;
- which dependencies must already be complete;
- whether another runtime has claimed it;
- what work it enables after completion.

A system-test task normally depends on the implementation required for its scenario. For example:

```yaml
---
id: ARCH-001-SYSTEM-TEST-001
architecture_id: ARCH-001
title: Validate recovery webhook flow
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
status: pending
priority: 90
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-001-SHARED-001
  - ARCH-001-DATABASE-001
  - ARCH-001-SHOPIFY-001
  - ARCH-001-BACKGROUND-001
enables: []
created: 2026-08-29
updated: 2026-08-29
---
```

The task becomes `ready` only when the dependencies required for integrated validation are `complete`.

---

# Task lifecycle

Tasks use a controlled status model:

```text
pending
ready
in_progress
review
complete
blocked
superseded
```

The intended lifecycle is:

```text
pending
   |
   v
ready
   |
   | repository agent claims task
   v
in_progress
   |
   | implementation + validation
   v
review
   |
   | architect accepts
   v
complete
```

A repository agent may also return:

```text
in_progress -> blocked
```

when the implementation reveals a missing dependency, architectural conflict or unsafe assumption.

---

# Task claiming

Task discovery is not a claim.

Immediately before implementation, the agent re-reads the task and verifies:

```text
status: ready
assigned_agent: <correct agent>
all depends_on tasks: complete
```

The task is then claimed using execution metadata:

```yaml
status: in_progress
executor: <current runtime>
claimed_at: 2026-08-28T15:30:00+01:00
attempt: 1
```

where `<current runtime>` identifies the active execution surface, for example `codex`, `claude`, `continue` or `copilot`.

The agent must not overwrite another executor's active claim.

This allows multiple coding environments to work against the same durable task state without silently duplicating work.

---

# Standard repository-agent kickoff

## Task-ID launcher

The preferred task kickoff is the runtime `moda-task` launcher.

The developer supplies the fully qualified task ID, for example:

```text
ARCH-002-SHOPIFY-001
```

Supported entry points include:

```text
Continue: /moda-task ARCH-002-SHOPIFY-001

Claude:   /moda-task ARCH-002-SHOPIFY-001

Codex:    $moda-task ARCH-002-SHOPIFY-001
          where the current Codex surface exposes project skill invocation

Copilot:  Use /moda-task for ARCH-002-SHOPIFY-001
```

The launcher calls:

```text
scripts/start-agent-task.py
```

which deterministically resolves:

```text
TASK_ID
  |
  v
architecture ID
  |
  v
decision domain
  |
  v
task file
  |
  v
logical Moda agent
  |
  v
repository
  |
  v
rendered docs/agent-task-execution-template.md
```

The launcher and resolver are **routing-only**.

They MUST NOT:

- claim the task;
- modify task execution state;
- implement the task;
- perform architect review;
- silently substitute a different logical owner.

The receiving logical agent performs the authoritative verify/claim/execute/review protocol.

The resolver can be tested directly from the workspace root:

```bash
python3 scripts/start-agent-task.py ARCH-002-SHOPIFY-001 --json
```

The result includes the resolved task, architecture, domain, logical agent, repository, task file, current status and rendered execution prompt.

## Canonical execution template

The standard template remains:

```text
docs/agent-task-execution-template.md
```

It is parameterised with:

```text
<AGENT>
<ARCH_ID>
<TASK_ID>
<TASK_FILE>
```

For example:

```text
<AGENT>     = moda_shared
<ARCH_ID>   = ARCH-001
<TASK_ID>   = ARCH-001-SHARED-001
<TASK_FILE> = docs/decisions/shared/ARCH-001/SHARED-001-define-recovery-webhook-contracts.md
```

The template requires the repository agent to:

```text
read logical-agent definition
        |
        v
read assigned task
        |
        v
read parent architecture / relevant architecture context
        |
        v
check dependency metadata
        |
        +--> read full dependency/contract content only when the current
        |    task consumes its output, decision or interface
        v
verify task is ready
        |
        v
claim task using the current execution runtime
        |
        v
implement bounded scope
        |
        v
run required validation
        |
        v
complete Completion Report
        |
        v
status: review
        |
        v
STOP and return to moda_architect
```

Dependency gating should be **metadata-first**.

An implementation agent does not need to load the entire body of every completed dependency merely to establish:

```text
status: complete
```

It should load a dependency body when the current task actually consumes a contract, decision, migration, generated artifact or other dependency output.

The task file remains authoritative for:

- implementation scope;
- dependencies;
- interfaces/contracts;
- Work Items;
- Acceptance Criteria;
- Validation;
- Completion Report.

The parent architecture remains authoritative for overall architectural intent.

The kickoff template is an execution wrapper, not a competing source of truth.

---

# Codex, Claude and other runtimes

The logical engineering role is deliberately independent of the AI vendor.

For example:

```text
Codex -----\
            \
             -> moda_background
            /
Claude ----/
```

The logical role is:

```text
moda_background
```

not:

```text
claude_background
codex_background
```

The durable architecture/task workflow may be entered through Codex, Claude,
Continue or GitHub Copilot without changing logical ownership.

## Canonical agent definitions

The Codex TOML files are the **canonical authored definitions**:

```text
.codex/agents/<name>.toml
```

Claude agent files are generated runtime representations:

```text
.claude/agents/<name>.agent.md
```

Do not independently maintain the same logical-agent rules in both places.

When repository ownership, architecture rules, task protocol or agent-specific
engineering constraints change, edit the Codex TOML and regenerate Claude.

The normal workflow is:

```text
edit .codex/agents/moda_background.toml
        |
        v
python3 sync_agents.py
        |
        v
.claude/agents/moda_background.agent.md
```

The sync script copies the canonical:

```text
name
description
developer_instructions
```

while leaving Codex-only TOML execution settings such as model or sandbox/runtime
configuration outside the generated Claude definition.

Generated Claude files should be treated as generated artifacts and should not
be edited directly.

## Runtime-neutral developer instructions

Although the authored source lives under `.codex/agents/`,
`developer_instructions` describes the **logical Moda agent**, not Codex itself.

Behavioural instructions must therefore remain runtime-neutral.

Prefer:

```text
When claiming a task, set `executor` to the identifier for the current
execution runtime.
```

Do not hard-code:

```text
executor: codex
```

and do not make logical-agent behaviour depend on wording such as:

```text
In this Codex agent definition...
Codex must...
Codex should...
```

unless Codex is being discussed only as one supported runtime or configuration
location.

The same logical task may therefore record:

```text
Codex     -> executor: codex
Claude    -> executor: claude
Continue  -> executor: continue
Copilot   -> executor: copilot
```

## Synchronising Codex and Claude definitions

Regenerate all Claude definitions with:

```bash
python3 sync_agents.py
```

Verify synchronization without changing files with:

```bash
python3 sync_agents.py --check
```

A missing or stale generated Claude definition causes a non-zero exit status,
making `--check` suitable for CI or pre-commit verification.

Regenerate one logical agent with:

```bash
python3 sync_agents.py --agent moda_background
```

Multiple agents may be selected:

```bash
python3 sync_agents.py \
  --agent moda_app \
  --agent moda_background
```

Remove obsolete generated Claude definitions whose canonical Codex source has
been deliberately removed with:

```bash
python3 sync_agents.py --prune
```

`--prune` cannot be combined with `--agent`.

A normal agent-definition change should therefore follow:

```text
1. Edit .codex/agents/<agent>.toml
2. Keep developer_instructions runtime-neutral
3. Run python3 sync_agents.py --agent <agent>
4. Review the generated Claude file
5. Run python3 sync_agents.py --check
6. Commit the canonical Codex and generated Claude changes together
```

The engineering organisation therefore survives a change of AI model or provider
because the durable role, task and architecture state are not owned by one
runtime.

---

# Canonical shared contracts

Cross-service runtime contracts are centrally owned by:

```text
moda-interact-shared/
```

and consumed through:

```text
@modainteract/moda-interact-shared
```

This package is not merely a miscellaneous utility library.

It is the canonical home for cross-service runtime boundaries such as:

- queue payload types;
- event schemas;
- runtime validators;
- schema-version constants;
- shared enums;
- deterministic event/job identifiers;
- correlation and ordering identifiers.

Instead of this:

```text
Producer
  -> local CheckoutEvent definition

Consumer
  -> another local CheckoutEvent definition
```

the intended model is:

```text
                 moda_shared
                     |
          canonical CheckoutEvent
                     |
             +-------+-------+
             |               |
             v               v
         producer         consumer
```

If a required cross-service contract does not exist, a repository agent should not invent a competing local version.

The missing contract is returned to `moda_architect`, which can create or sequence a `moda_shared` task.

---

# Dependency-driven contract rollout

Shared-contract tasks can explicitly gate producers and consumers.

Example:

```text
ARCH-001-SHARED-001
Define canonical contract
        |
        +--------------------------+
        |                          |
        v                          v
ARCH-001-SHOPIFY-001      ARCH-001-BACKGROUND-001
producer imports it       consumer imports it
```

This makes deployment and compatibility requirements visible before implementation begins.

---

# Durable project state

One of the main principles of the workflow is:

```text
Conversation = temporary execution context

Repository/docs = durable engineering state
```

A fresh agent should be able to reconstruct:

```text
Who am I?
What repository do I own?
What task am I executing?
Why does it exist?
What does it depend on?
What contracts apply?
What may I change?
How must I validate it?
Who accepts completion?
```

without relying on hidden chat history.

This is particularly important when tasks may be executed by different models at different times.

---

# Agent startup context and token efficiency

Moda Interact deliberately separates architectural judgement from deterministic
workflow so coding agents spend as much of their context as possible on the
actual engineering task.

A typical repository-agent invocation currently loads roughly:

```text
logical agent definition
        +
task execution protocol
        +
assigned task
        +
parent architecture context
        +
relevant dependency/contract context
```

In practice, this is approximately **9,000–10,000 tokens of startup context for
a typical implementation task** before substantial code inspection and
implementation begins.

The goal is not to remove governance rules simply to reduce token usage.

Repository ownership, architectural invariants, task lifecycle rules, security
constraints, review gates and failure-handling rules remain explicit.

Token efficiency is instead improved by:

- keeping logical-agent definitions focused on durable ownership and engineering rules;
- keeping task execution lifecycle rules in one canonical execution template;
- generating Claude definitions from canonical Codex definitions instead of maintaining duplicate rule sets;
- resolving task IDs, repositories and logical agents deterministically in `scripts/start-agent-task.py`;
- checking dependency metadata before loading complete dependency task bodies;
- loading detailed technical reference material only when it is relevant to the current task;
- moving mechanical workflow operations into deterministic scripts where practical.

The operating principle is:

> **Use model context for judgement and engineering decisions; use deterministic tooling for routing, validation and workflow mechanics.**

As more mechanical task operations are automated and architecture context becomes
more targeted, startup context can be reduced further without weakening the
engineering governance model.

---

# Benefits of the approach

## 1. Reduced agent drift

A repository agent receives explicit ownership and bounded task scope.

It is less likely to "helpfully" refactor unrelated code or redesign another repository.

---

## 2. Cross-repository changes become explicit

A change that affects:

```text
shared contract
    +
database
    +
producer
    +
consumer
```

becomes a visible dependency graph instead of an implicit sequence inside one AI conversation.

---

## 3. Better review boundaries

Implementation and acceptance are separated.

```text
repository agent
      |
      v
status: review
      |
      v
moda_architect
      |
      v
status: complete
```

This reduces the risk of the implementation agent deciding that its own assumptions are correct.

---

## 4. AI-provider independence

The workflow is organised around logical engineering roles rather than vendor-specific agents.

A task can move between compatible execution environments without changing its architectural ownership.

---

## 5. Better recovery from interrupted work

Because execution state is stored in the task file, a new agent can determine whether work is:

```text
ready
in_progress
blocked
review
complete
```

without needing the previous conversation.

---

## 6. Explicit dependency management

Tasks cannot safely become executable until their dependencies are complete.

This is useful for:

- schema before application code;
- shared contract before producer/consumer;
- migration before dependent deployment;
- infrastructure before runtime integration.

---

## 7. Central contract ownership

Producer and consumer services are less likely to drift into structurally similar but semantically incompatible event definitions.

---

## 8. Easier multi-agent collaboration

Agents can work independently when their tasks do not conflict.

The architecture/task graph provides a common coordination mechanism.

---

## 9. Better auditability

Architecture decisions, dependencies, implementation reports and review status are stored in version control.

This makes it possible to understand not just **what changed**, but also:

- why it changed;
- which architecture required it;
- which agent implemented it;
- what validation was performed;
- what assumptions or concerns remained.

---

## 10. Integrated architecture verification

Repository-level tests can pass while the complete architecture still fails because of configuration, sequencing, contract, queue, database or environment interactions.

The dedicated system-test phase adds an explicit integrated check:

```text
repository tests pass
        |
        v
moda_system_test
        |
        v
cross-service scenario passes
        |
        v
architecture accepted
```

This provides evidence that the architecture works as a system, not just as a set of individually valid repository changes.

---

## 11. More meaningful agent evaluation

Models can be compared using the same bounded task specification.

Instead of asking only:

> Did the model generate valid TypeScript?

the workflow can evaluate:

```text
Did it read the correct architecture?
Did it respect dependencies?
Did it claim the task correctly?
Did it stay inside its repository?
Did it reuse shared contracts?
Did it run the required validation?
Did it report unresolved concerns?
Did it return the task for review?
```

This is a more realistic test of coding-agent reliability.

---

## 12. Deterministic routing

The agent does not need to infer which repository, task file or logical role owns
a fully qualified architecture task.

```text
TASK_ID
  |
  v
scripts/start-agent-task.py
  |
  +--> architecture
  +--> domain
  +--> logical agent
  +--> repository
  +--> task file
  +--> rendered execution prompt
```

This reduces both ambiguity and unnecessary model reasoning.

---

## 13. Token-efficient governance

The workflow deliberately distinguishes between rules that require model
judgement and mechanics that software can enforce.

Governance is retained, but repeated discovery, routing and synchronization work
is progressively moved into deterministic tooling.

This allows agent context to be spent on implementation and architectural
reasoning rather than rediscovering stable workspace facts.

---

# How this compares with typical coding-agent usage

A useful maturity spectrum is:

| Level | Typical usage |
| --- | --- |
| 1 | AI autocomplete |
| 2 | Chat about code |
| 3 | Agent given a feature or issue |
| 4 | Repo-aware agent with rules/instructions |
| 5 | Durable tasks, dependencies and review |
| 6 | Multi-agent engineering workflow with specialist ownership and coordination |

Many developer workflows currently sit around levels 2-4.

Moda Interact is intentionally moving toward levels 5-6.

| Typical agent workflow | Moda Interact workflow |
| --- | --- |
| Prompt is the main instruction | Task file is authoritative |
| Agent explores freely | Repository ownership is explicit |
| Developer coordinates manually | Architect coordinates |
| State lives mainly in chat | State lives in version-controlled files |
| Dependencies are implicit | Dependencies are machine-readable |
| Agent may edit multiple domains | Changes are bounded by logical ownership |
| Agent declares work finished | Architect accepts completion |
| Integrated testing is often ad hoc/manual | Dedicated `moda_system_test` phase validates integrated architecture behaviour |
| Interfaces may be recreated locally | Shared contracts have canonical ownership |
| Workflow often depends on one AI vendor | Logical agents are runtime-independent |

---

# When to use the full architecture workflow

The architecture workflow is intended for changes that affect system boundaries or require coordination.

Examples:

- new cross-service event contract;
- database model or migration;
- producer/consumer protocol change;
- queue semantics;
- idempotency or ordering;
- tenant isolation;
- deployment sequencing;
- billing/entitlement behaviour;
- high-volume processing architecture.

For a small local change, the full process may be unnecessary.

Example:

```text
LOCAL / LOW-RISK CHANGE

repository agent
      |
      v
implement directly
```

versus:

```text
ARCHITECTURAL / CROSS-BOUNDARY CHANGE

moda_architect
      |
      v
architecture
      |
      v
task graph
      |
      v
repository agents
      |
      v
architect review of implementation
      |
      v
moda_system_test
      |
      v
architect final acceptance
```

The goal is governance where it adds value, not bureaucracy for every edit.

---

# Trade-offs

The approach introduces additional structure.

Potential costs include:

- more documentation;
- task-file maintenance;
- coordination overhead for small changes;
- generated agent definitions that must remain synchronized with their canonical source;
- need to maintain task and architecture indexes;
- risk of rules becoming stale if deterministic validation does not keep pace with the workflow;
- context overhead when tasks load more architecture/reference material than they actually require.

The workflow therefore works best when architecture tasks are reserved for
changes whose complexity justifies the coordination.

The objective is not to minimise process at all costs.

It is to keep governance where it protects architecture while moving repeatable
mechanics into deterministic tooling.

---

# Current maturity assessment

The workflow is strong in architecture, durable coordination and provider
independence, with a growing deterministic automation layer.

Approximate assessment:

| Area | Assessment |
| --- | ---: |
| Logical agent separation | 9.5 / 10 |
| Repository ownership | 9 / 10 |
| Architecture/task decomposition | 9 / 10 |
| Durable coordination state | 9.5 / 10 |
| Shared contract governance | 9 / 10 |
| Review/acceptance model | 9 / 10 |
| Architecture-level system validation design | 9 / 10 |
| AI-provider independence | 9.5 / 10 |
| Deterministic task routing | 9 / 10 |
| Agent-definition synchronization | 9 / 10 |
| Workflow automation | 8 / 10 |
| Overhead/context control | 8 / 10 |

Overall:

```text
~8.8 / 10
```

The main opportunity is not adding more rules.

It is continuing to automate and selectively load the rules that already exist.

---

# Next step: automate workflow validation

The next major automation step is a workspace architecture validator such as:

```bash
python3 scripts/validate_architecture.py
```

or:

```bash
npm run architecture:validate
```

It could automatically verify:

```text
task IDs are valid
dependencies exist
ready tasks have complete dependencies
assigned_agent matches repository/domain
only one active executor has claimed a task
architecture references are valid
shared-contract tasks exist where required
required system-test tasks exist for architectures that require integrated validation
system-test dependencies point to valid implementation tasks
task indexes are consistent
```

Codex/Claude synchronization is already independently enforceable with:

```bash
python3 sync_agents.py --check
```

A future architecture validator should call or incorporate that check instead of
reimplementing synchronization logic.

Further workflow automation can move mechanical task operations out of agent
prompts, for example:

```text
claim task
        -> deterministic validation + state transition

submit task for review
        -> deterministic Completion Report/state validation

architecture validation
        -> dependency/ownership/index checks
```

Example validation output:

```text
✓ ARCH-001-SHARED-001 valid
✓ dependency graph valid
✓ repository ownership valid
✓ no duplicate active claims
✓ agent definitions synchronized
✓ architecture task graph valid
```

At that point, governance moves further from:

```text
instructions the agent must remember
```

toward:

```text
constraints the workspace can enforce
```

---

# Desired end state

The long-term goal is that a completely fresh coding agent or developer needs to
provide only:

```text
TASK_ID
```

For example:

```text
ARCH-002-SHOPIFY-001
```

Deterministic tooling should then resolve:

```text
TASK_ID
  |
  v
architecture
  |
  v
task file
  |
  v
domain
  |
  v
logical agent
  |
  v
repository
  |
  v
canonical execution template
```

The resolved logical agent should then be able to determine:

```text
who it is
what it owns
what it must read
what it depends on
what contracts apply
what it may change
how it must validate the change
whether integrated system validation is required
how it reports completion
and who must approve it
```

The desired separation is:

```text
judgement / architecture / implementation reasoning
        -> model

routing / ownership lookup / metadata validation / synchronization
        -> deterministic tooling
```

If that works consistently across different coding models and execution
environments, then the workflow has moved beyond ordinary AI-assisted coding
into a durable multi-agent engineering system.

---

## Related workspace documentation

The workflow is implemented through:

```text
.codex/agents/
.codex/skills/moda-task/SKILL.md
.claude/agents/
.claude/skills/moda-task/SKILL.md
.continue/prompts/moda-task.md
docs/architecture/
docs/decisions/
docs/decisions/system-test/
docs/contracts/
docs/agent-task-execution-template.md
scripts/start-agent-task.py
sync_agents.py
moda-interact-gateway/
moda-interact-system-test/
```

See the workspace README for repository layout, submodule management, runtime
launcher setup, agent synchronization and local development guidance.
