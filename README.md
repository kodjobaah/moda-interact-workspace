# Moda Interact Workspace

Moda Interact is a multi-service platform for Shopify checkout recovery and
conversational commerce, including WhatsApp customer interactions.

This repository is the top-level workspace for the platform. It ties together
independently versioned services using Git submodules, so a workspace commit
records the exact compatible service commits that form a platform snapshot.


## Product status

Moda Interact is being built as a company-backed commercial product, not a demo
or isolated experiment.

The company has being registered, the public website is live, and the platform is
being prepared for release in the next few weeks.

Website: https://www.modainteract.com/

## Why this project matters

Moda Interact is an AI-enabled customer engagement platform for Shopify merchants.
It combines Shopify webhooks, BullMQ background workers, WhatsApp messaging,
PostgreSQL state, and an AI CommerceAgent to recover abandoned checkouts through
conversational workflows.

Key engineering areas demonstrated:
- Multi-service architecture
- Async/event-driven processing
- AI/LLM orchestration
- External tool calling
- PostgreSQL persistence
- Redis/BullMQ queues
- Shopify and WhatsApp integrations
- Idempotency and retry design
- Production deployment planning

## Engineering relevance

This project demonstrates hands-on experience with:

- Designing a multi-service SaaS platform
- Building backend services with TypeScript/Node.js
- Processing high-volume webhook events asynchronously
- Persisting business state outside the LLM
- Building AI workflows with tool-calling and conversation state
- Integrating with Shopify, WhatsApp/Meta, PostgreSQL, Redis and external AI providers
- Designing for idempotency, retries, observability and independent worker scaling

## Quick navigation

- [Platform overview](#platform-overview)
- [High-level architecture](#high-level-architecture)
- [Architecture initiatives](#architecture-initiatives)
- [Projects and ownership](#projects-and-ownership)
- [Getting started](#getting-started)
- [Architecture-led development](#architecture-led-development)
- [Developer-owned Git and publication](#developer-owned-git-and-publication)
- [Launching an architecture task](#launching-an-architecture-task)
- [Logical agents and AI runtimes](#logical-agents-and-ai-runtimes)
- [Platform workload and scalability](#platform-workload-and-scalability)
- [Working with Git submodules](#working-with-git-submodules)

---

## Platform overview

Moda Interact is designed around a small set of explicit service boundaries:

- Shopify-facing authentication, merchant UI and webhook ingress;
- asynchronous checkout-recovery and CommerceAgent processing;
- Meta/WhatsApp webhook ingress;
- durable PostgreSQL state;
- Redis/BullMQ asynchronous coordination;
- an internal platform-admin application;
- a thin deployment gateway;
- canonical cross-service runtime contracts;
- architecture-level integrated system testing.

The platform follows several core principles:

- `Shop` / `shopId` is the tenant boundary;
- PostgreSQL is the durable source of truth;
- Redis and BullMQ coordinate asynchronous work rather than becoming the sole
  durable business state;
- webhook handlers authenticate, validate, normalise and acknowledge quickly;
- long-running and retryable processing belongs in background workers;
- cross-service contracts have one canonical owner;
- platform-admin authentication is separate from merchant Shopify
  authentication;
- architecture, task state and review state live in version-controlled files
  rather than hidden chat history.

For the broader architecture overview, see
[`docs/architecture/overview.md`](docs/architecture/overview.md).

---

## High-level architecture

The diagram below combines the core application flow with the deployment
boundary being implemented by ARCH-002.

ARCH-002 is still in progress, so the gateway/private-service boundary should be
read as the **target deployment topology**, not as a claim that every part is
already deployed in production.

```text
                      PUBLIC INTERNET
                           |
                 Render public ingress
                           |
                           v
                moda-interact-gateway
                           |
                  Render private network
          +----------------+----------------+
          |                |                |
          v                v                v
   moda-interact   moda-interact-messaging  moda-interact-admin
   Shopify app       Meta / WhatsApp          Admin console
          |                |                |
          +--------+-------+                |
                   |                        |
                   v                        |
             Redis / BullMQ                 |
                   |                        |
          +--------+---------+              |
          |        |         |              |
          v        v         v              |
      Shopify   Recovery   Messaging /      |
       event     worker    CommerceAgent     |
       worker                              |
          |        |         |              |
          +--------+---------+--------------+
                   |
                   v
               PostgreSQL

Background workers
      |
      +--> Shopify Admin API
      +--> AI / CommerceAgent providers
      +--> messaging/recovery integrations

Public marketing site
      |
      v
moda-interact-site
```

`moda-interact-database` is the authoritative owner of the shared Prisma schema
and migration history.

`moda-interact-shared` is the canonical owner of cross-service runtime
contracts, schemas, event versions and deterministic identifiers.

---

## Architecture initiatives

Architectural work is organised around stable `ARCH-XXX` initiative IDs.

An architecture ID identifies a **complete architectural outcome**, not one
implementation task.

| Architecture | Status | High-level architectural goal | Architecture decision | Copilot implementation plan |
| --- | --- | --- | --- | --- |
| **ARCH-001** | Agreed | Build a reliable, low-overhead Shopify checkout-recovery event pipeline: keep webhook ingress fast, use Redis/BullMQ for temporary recovery candidates, persist only actual `CheckoutRecovery` state, fetch current Shopify state only when recovery is required, use canonical cross-service contracts, and tolerate duplicate/concurrent asynchronous processing. | [Shopify Checkout Recovery Webhook Processing](docs/architecture/ARCH-001-shopify-checkout-recovery-webhook-processing.md) | [Copilot model and task plan] |
| **ARCH-002** | In progress | Establish a production-ready, version-controlled Render topology for test and production: thin public gateway, private application services, independently scalable background workers, environment-isolated PostgreSQL/Redis/telemetry, admin security, observability, deployment validation and capacity testing. | [Render Test and Production Gateway and Infrastructure](docs/architecture/ARCH-002-render-production-gateway-infrastructure.md) | [Copilot model and task plan](docs//models/ARCH-002/copilot-model-selection.md) |

The architecture document is authoritative for **what is being built and how the
complete system fits together**.

The Copilot plan is an implementation-planning aid. It recommends implementation
models for repository-agent work and does not override architecture or task
state. Architect review is performed separately through the `moda_architect`
workflow.

### Architecture and task documentation

The central architecture and cross-agent coordination state lives under
[`docs/`](docs/).

```text
docs/
├── architecture/
│   ├── overview.md
│   ├── ARCH-001-shopify-checkout-recovery-webhook-processing.md
│   └── ARCH-002-render-production-gateway-infrastructure.md
├── decisions/
│   ├── admin/
│   ├── background/
│   ├── database/
│   ├── gateway/
│   ├── messaging/
│   ├── shared/
│   ├── shopify/
│   ├── site/
│   └── system-test/
├── contracts/
├── coding-agent-workflow.md
├── copilot-model-selection.md
├── agent-vcs-ownership-policy.md
└── agent-task-execution-template.md
```

The source-of-truth hierarchy is:

| Source | Question answered |
| --- | --- |
| `docs/architecture/ARCH-XXX-*.md` | What are we building and how does the complete system fit together? |
| `docs/decisions/<domain>/ARCH-XXX/_index.md` | What work does this logical agent/domain own for this architecture? |
| `docs/decisions/<domain>/ARCH-XXX/<TASK>.md` | What exactly must be implemented now? |
| Repository source code | What has actually been implemented and how does it behave? |

Task YAML metadata is authoritative for task state. The parent architecture
document is authoritative for overall architectural intent. Source code is
authoritative for actual runtime behaviour. `moda_architect` must reconcile
these sources if they drift.

---

## Projects and ownership

Each service is independently versioned and has a bounded responsibility.

| Project | Responsibility |
| --- | --- |
| [`moda-interact`](https://github.com/kodjobaah/moda-interact) | Shopify application, merchant UI, Shopify authentication/webhooks, onboarding, billing and subscriptions |
| [`moda-interact-admin`](https://github.com/kodjobaah/moda-interact-admin) | Next.js platform administration console, platform-admin security, cross-merchant reporting and operational visibility |
| [`moda-interact-background`](https://github.com/kodjobaah/moda-interact-background) | BullMQ workers, high-volume Shopify event inspection/filtering, checkout recovery, CommerceAgent orchestration, retries, entitlements and usage |
| [`moda-interact-database`](https://github.com/kodjobaah/moda-interact-database) | Canonical Prisma schema, PostgreSQL migrations, constraints, indexes, seed/reference data and ERD |
| [`moda-interact-gateway`](https://github.com/kodjobaah/moda-interact-gateway) | Thin public ingress, private-service routing, Render Blueprints/topology, scaling configuration and infrastructure wiring |
| [`moda-interact-messaging`](https://github.com/kodjobaah/moda-interact-messaging) | Meta/WhatsApp webhook verification, normalisation and queue publication |
| [`moda-interact-shared`](https://github.com/kodjobaah/moda-interact-shared) | Canonical `@modainteract/moda-interact-shared` package for cross-service runtime contracts and reusable primitives |
| [`moda-interact-site`](https://github.com/kodjobaah/moda-interact-site) | Public website, product content, SEO and public-facing material |
| [`moda-interact-system-test`](https://github.com/kodjobaah/moda-interact-system-test) | Architecture-level integrated tests, architecture-specific fixtures and environment orchestration |

For more detail, see
[`docs/architecture/services.md`](docs/architecture/services.md).

---

## Why this workspace exists

Each service remains an independent Git repository with its own commit history
and deployment lifecycle.

The workspace records Gitlinks to specific service commits:

```text
moda-interact-workspace
├── moda-interact            @ <commit>
├── moda-interact-admin      @ <commit>
├── moda-interact-background @ <commit>
├── moda-interact-database   @ <commit>
├── moda-interact-gateway    @ <commit>
├── moda-interact-messaging  @ <commit>
├── moda-interact-shared     @ <commit>
├── moda-interact-site       @ <commit>
└── moda-interact-system-test @ <commit>
```

This gives the platform both:

```text
independent service ownership
        +
reproducible whole-platform snapshots
```

The workspace coordinates service versions, architecture state and agent
execution without collapsing all services into one repository.

---

## Workspace structure

```text
moda-interact-workspace/
├── .codex/
│   ├── agents/
│   └── skills/
│       └── moda-task/
│           └── SKILL.md
├── .claude/
│   ├── agents/
│   └── skills/
│       └── moda-task/
│           └── SKILL.md
├── .continue/
│   └── prompts/
│       └── moda-task.md
├── docs/
│   ├── architecture/
│   ├── contracts/
│   ├── decisions/
│   ├── agent-task-execution-template.md
│   ├── agent-vcs-ownership-policy.md
│   ├── coding-agent-workflow.md
│   ├── copilot-model-selection.md
│   ├── development-baseline.md
│   └── node-toolchain.md
├── scripts/
│   ├── apply-node-agent-policy.py
│   ├── bootstrap-node.sh
│   ├── start-agent-task.py
│   └── workspace-doctor.sh
├── .gitmodules
├── .nvmrc
├── README.md
├── sync_agents.py
├── moda-interact/
├── moda-interact-admin/
├── moda-interact-background/
├── moda-interact-database/
├── moda-interact-gateway/
├── moda-interact-messaging/
├── moda-interact-shared/
├── moda-interact-site/
├── moda-interact-system-test/
└── moda-interact.code-workspace
```

---

## Getting started

### Clone the complete workspace

Because the workspace contains Git submodules, clone it recursively:

```bash
git clone --recurse-submodules \
  https://github.com/kodjobaah/moda-interact-workspace.git

cd moda-interact-workspace
```

If the workspace was cloned without `--recurse-submodules`:

```bash
git submodule update --init --recursive
```

The `--recursive` flag matters because some services also consume
`moda-interact-database` as a nested submodule.

### Open the VS Code workspace

Open the top-level workspace rather than one service in isolation:

```bash
code moda-interact.code-workspace
```

<!-- MODA-DEVELOPMENT-BASELINE:START -->
### Development environment baseline

Coding-agent shells may be non-interactive and may not inherit the developer's
NVM environment. The workspace also contains shared runtime dependencies whose
resolution must remain consistent across services.

The development IDE should be opened at the `moda-interact-workspace` project
root. In VS Code, open the included `moda-interact.code-workspace`. Agent task
startup therefore begins by bootstrapping from the workspace root:

```bash
source scripts/bootstrap-node.sh
"$MODA_WORKSPACE_ROOT/scripts/workspace-doctor.sh" --quick
```

`bootstrap-node.sh` resolves and exports:

```text
MODA_WORKSPACE_ROOT
```

That variable is the stable workspace path for the rest of the task. If the
agent later changes into a service repository, it must continue to use:

```bash
"$MODA_WORKSPACE_ROOT/scripts/workspace-doctor.sh" --quick
```

rather than looking for a repository-local `scripts/workspace-doctor.sh`.

`.nvmrc` is the single source of truth for the workspace development Node
version. Agent definitions and bootstrap scripts do not embed a concrete Node
version.

The workspace doctor classifies known environment/dependency conditions so
agents do not repeatedly investigate the same baseline:

```text
EXPECTED
FIX
WARN
PRODUCTION GATE
```

For deployment work:

```bash
"$MODA_WORKSPACE_ROOT/scripts/workspace-doctor.sh" --production
```

For deeper dependency diagnostics:

```bash
"$MODA_WORKSPACE_ROOT/scripts/workspace-doctor.sh" --full
```

The baseline documentation is always:

```text
$MODA_WORKSPACE_ROOT/docs/development-baseline.md
```

See:

- [`docs/development-baseline.md`](docs/development-baseline.md)
- [`scripts/bootstrap-node.sh`](scripts/bootstrap-node.sh)
- [`scripts/workspace-doctor.sh`](scripts/workspace-doctor.sh)

<!-- MODA-DEVELOPMENT-BASELINE:END -->

### Node.js development toolchain

Moda Interact uses NVM for the workspace development Node.js toolchain.

The workspace root [`.nvmrc`](.nvmrc) is the **single source of truth for the
Node.js version selected for local development and coding-agent shells**.

After entering the workspace:

```bash
source scripts/bootstrap-node.sh
```

The bootstrap flow is:

```text
find workspace root
        |
        v
read .nvmrc
        |
        v
load NVM when available
        |
        v
nvm use <workspace version>
        |
        +----> if NVM shell integration is unavailable,
        |      use the matching installed NVM version directly
        v
verify node + npm
```

Coding-agent shells may be non-interactive and may not inherit the developer's
normal NVM initialization. An initial `node: command not found` does not prove
that Node.js is absent.

Agents must attempt the workspace bootstrap before searching the wider
filesystem or installing another Node version.

#### Installing the selected Node version

If the `.nvmrc` version is not installed:

```bash
export NVM_DIR="${NVM_DIR:-$HOME/.nvm}"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"

nvm install
nvm use
```

Then verify:

```bash
node --version
npm --version
```

#### Changing Node versions

Do not update every agent definition when changing Node.

Change `.nvmrc`, then:

```bash
nvm install
nvm use
```

Where a service declares `package.json` `engines.node`, keep that compatibility
range aligned intentionally.

```text
.nvmrc
    -> selects the development/agent-shell Node version

package.json engines.node
    -> declares versions an individual package supports

deployment configuration
    -> selects/validates the deployed runtime
```

A `.nvmrc` change does not itself prove every service is compatible. Validate
affected services before treating a new Node version as supported.

Detailed guidance:

[Node.js toolchain and agent-shell bootstrap](docs/node-toolchain.md)

---

## Architecture-led development

Moda Interact uses coding agents as part of a structured engineering workflow
rather than as standalone code generators.

The central principle is:

> **Conversation is temporary execution context. The repository is durable
> engineering state.**

The detailed design and rationale are documented in:

[Moda Interact Coding Agent Workflow](docs/coding-agent-workflow.md)

### Architecture execution workflow

Cross-repository architectural work follows this lifecycle:

```text
User / engineering requirement
        |
        v
moda_architect
        |
        | inspect code + define architecture
        v
docs/architecture/ARCH-XXX-*.md
        |
        | decompose into bounded tasks
        v
docs/decisions/<domain>/ARCH-XXX/<TASK>.md
        |
        | dependencies satisfied
        v
repository agent
        |
        | claim + implement + validate
        v
status: review
        |
        v
moda_architect
        |
        +--> changes requested --> same task / owner
        |
        +--> accepted --> status: complete
                              |
                              v
                 required implementation complete
                              |
                              v
                    moda_system_test
                              |
                    integrated validation
                              |
                              v
                         status: review
                              |
                              v
                        moda_architect
                              |
                              v
                 architecture: implemented
```

Repository agents do **not** approve their own architecture tasks.

Only `moda_architect` may accept:

```text
review -> complete
```

For architectures requiring integrated runtime validation, repository tasks being
complete is not sufficient. Required system-test tasks must also be reviewed and
completed.

### Developer-owned Git and publication

Git publication is deliberately separated from repository-agent implementation.

The default Moda Interact workflow is:

```text
repository agent
    |
    +--> claim
    +--> implement
    +--> validate
    +--> update Completion Report
    +--> status: review
    +--> STOP

moda_architect
    |
    +--> inspect actual uncommitted changes
    +--> request changes, or
    +--> review -> complete

developer / user
    |
    +--> git add
    +--> git commit
    +--> git push
```

Repository agents must not run `git commit` or `git push` unless the developer
explicitly grants one-off permission for that specific task.

Agents may inspect Git state and may make task-owned working-tree changes,
including updating a service's nested submodule checkout to an
architect-approved published commit. They leave the resulting source and gitlink
changes uncommitted for the developer.

If an older task says that repository changes must be committed/pushed by the
agent, that wording is coordination drift. It does not grant permission to
publish and is not, by itself, a reason to block an otherwise completed task.

Some downstream tasks require a **published** upstream commit, especially where
one repository consumes another through a Git submodule. In that case:

```text
upstream agent -> review
architect -> complete
developer -> commit + push
architect -> verify published commit
architect -> promote dependent task to ready
```

The workspace-wide policy is documented in:

[`docs/agent-vcs-ownership-policy.md`](docs/agent-vcs-ownership-policy.md).

### Task lifecycle and claiming

Task files use YAML frontmatter so execution can resume without depending on a
previous conversation.

Typical states:

```text
pending
ready
in_progress
review
complete
blocked
superseded
```

Normal lifecycle:

```text
pending
   |
   v
ready
   |
   | repository agent claims
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

`complete` is an architecture/task-review state. It does not mean the
repository agent committed or pushed the implementation.

After architect acceptance, the developer/user owns publication:

```text
git add -> git commit -> git push
```

Task discovery is not a claim.

Immediately before implementation the agent re-reads the task and verifies:

```text
status: ready
assigned_agent: <correct logical agent>
all depends_on tasks: complete
```

A claim records the active execution surface:

```yaml
status: in_progress
executor: copilot
claimed_at: <timestamp>
attempt: 1
```

Other supported executor values include `codex`, `claude` and `continue`.

An active claim must not be silently overwritten by another executor.

Each task contains checkable Work Items, Acceptance Criteria, Validation,
Completion Report and Architect Review sections.

### Shared contract workflow

Cross-service runtime contracts have one canonical owner:

```text
moda-interact-shared/
        |
        v
@modainteract/moda-interact-shared
```

Before defining a queue payload, runtime event schema, schema version, shared
enum, deterministic identifier or other cross-service primitive, producers and
consumers must check the shared package.

A typical dependency sequence is:

```text
ARCH-XXX-SHARED-001
Define canonical contract
        |
        +-------------------------+
        |                         |
        v                         v
producer task                consumer task
imports contract             imports contract
```

Repository agents must not invent competing local versions of a canonical
cross-service contract.

### Architecture-level system validation

`moda_system_test` owns architecture-level validation after the implementation
required by the scenario is complete.

It may:

- create architecture-specific fixtures and seed data;
- start PostgreSQL and required local services;
- verify Redis connectivity;
- start Shopify/background/messaging/admin services using their existing
  commands;
- use configured development APIs to create/reuse deterministic test fixtures;
- execute cross-service scenarios;
- capture logs and evidence.

It may run and inspect other repositories to orchestrate a system test, but that
does not transfer implementation ownership.

If a system test exposes an implementation defect, it reports the failure to
`moda_architect`, which routes remediation to the owning repository agent.

---

## Launching an architecture task

### Preferred interface: `moda-task <TASK_ID>`

A fresh developer or coding-agent session should normally need only the fully
qualified task ID.

Examples:

```text
Continue: /moda-task ARCH-002-SHOPIFY-001

Claude:   /moda-task ARCH-002-SHOPIFY-001

Codex:    $moda-task ARCH-002-SHOPIFY-001
          where the current Codex surface exposes project skill invocation

Copilot:  Use /moda-task for ARCH-002-SHOPIFY-001
```

All entry points route through:

```text
scripts/start-agent-task.py
```

The resolver deterministically maps:

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

The resolver is **routing-only**.

It does not:

- claim the task;
- modify execution state;
- implement the task;
- perform architect review;
- silently substitute another logical owner.

The **resolver** being routing-only does not mean the complete `/moda-task`
invocation stops after resolution.

Successful resolution continues immediately into the resolved logical-agent
execution context:

```text
/moda-task <TASK_ID>
        |
        v
start-agent-task.py
        |
        | routing only
        v
resolved logical agent + repository + rendered prompt
        |
        v
explicit dependency / eligibility verification
        |
        v
claim -> implement -> validate -> review
        |
        v
STOP
```

A successful resolver result such as `status: ready` is not a stopping
condition. The receiving logical repository agent performs authoritative
pre-claim checks, claiming, implementation, validation, Completion Report
updates and transition to `status: review`.

The agent then stops without committing or pushing.

#### Manual resolver test

From the workspace root:

```bash
python3 scripts/start-agent-task.py ARCH-002-SHOPIFY-001 --json
```

The JSON result includes the resolved architecture, domain, agent, repository,
task file, task state and execution prompt.

### Workspace-location independence

An agent may change into a service repository during implementation. A later
task launch must not depend on where the previous shell was left.

`start-agent-task.py` derives the workspace root from the script location.
Runtime launchers expose `MODA_WORKSPACE_ROOT` and call:

```bash
python3 "$MODA_WORKSPACE_ROOT/scripts/start-agent-task.py" "<TASK_ID>" --json
```

### Runtime entry points

| Entry point | Project integration | Typical task launch |
| --- | --- | --- |
| **Continue Chat** | `.continue/prompts/moda-task.md` | `/moda-task ARCH-002-SHOPIFY-001` |
| **GitHub Copilot Chat / Agent Mode** | `.claude/skills/moda-task/SKILL.md` | `Use /moda-task for ARCH-002-SHOPIFY-001` |
| **Claude Code** | `.claude/skills/moda-task/SKILL.md` | `/moda-task ARCH-002-SHOPIFY-001` |
| **Codex** | `.codex/skills/moda-task/SKILL.md` | `$moda-task ARCH-002-SHOPIFY-001` where supported |

#### Continue setup

Continue uses a project prompt stored at:

```text
.continue/prompts/moda-task.md
```

Register it in the developer's Continue configuration, for example:

```yaml
prompts:
  - uses: file:///absolute/path/to/moda-interact-workspace/.continue/prompts/moda-task.md
```

The prompt is invokable as `moda-task`.

Continue may execute the resolved logical role in its current agent context
rather than spawning a provider-specific named subagent. The durable task,
logical-agent rules and execution template remain authoritative.

#### Copilot setup

Copilot Agent Mode uses the shared project skill:

```text
.claude/skills/moda-task/SKILL.md
```

This avoids maintaining a duplicate skill under `.github/skills/`.

Copilot executes the rendered task in its Agent Mode context while following the
resolved logical agent's repository ownership and task protocol.

Copilot implementation should stop when the task reaches:

```text
status: review
```

It must leave implementation changes uncommitted and unpushed unless the
developer explicitly authorised publication for that task.

Architect review is performed separately through ChatGPT acting as
`moda_architect`.

See:

[Copilot model selection for Moda Interact tasks](docs/copilot-model-selection.md)

#### Claude Code setup

Claude logical-agent definitions live under:

```text
.claude/agents/
```

and the task launcher is:

```text
.claude/skills/moda-task/SKILL.md
```

The launcher is an invocation adapter; it must not become a competing task
source of truth.

#### Codex setup

Codex logical-agent definitions live under:

```text
.codex/agents/
```

and the task launcher is:

```text
.codex/skills/moda-task/SKILL.md
```

Where project skill invocation is exposed:

```text
$moda-task ARCH-002-SHOPIFY-001
```

The Codex launcher must preserve named logical-agent routing. If the execution
surface cannot select the configured logical agent, it should report that
limitation rather than silently substitute a generic worker.

---

## Logical agents and AI runtimes

The engineering organisation is defined in terms of **logical roles**, not AI
vendors.

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

The same logical task can be executed through different compatible runtimes
without changing architectural ownership.

### Agent responsibilities

| Logical agent | Responsibility |
| --- | --- |
| `moda_architect` | Cross-repository architecture, workload/scalability reasoning, service boundaries, task decomposition, dependency sequencing, implementation review and final integration |
| `moda_admin` | Internal Next.js administration console, platform-admin authentication/authorization, reporting and operational visibility |
| `moda_app` | Shopify application, merchant UI, authentication, webhooks, onboarding, billing and subscriptions |
| `moda_background` | BullMQ workers, event filtering, checkout recovery, order processing, CommerceAgent orchestration, retries, entitlements and usage |
| `moda_database` | Prisma schema, migrations, relationships, constraints, indexes, durable integrity and canonical/reference seed data |
| `moda_gateway` | Public ingress, reverse proxy, Render topology/Blueprints, private routing, scaling configuration and infrastructure wiring |
| `moda_messaging` | Meta/WhatsApp verification, validation, normalisation, ingress and queue publication |
| `moda_shared` | Canonical cross-service runtime contracts, schemas, event versions, deterministic IDs, enums and reusable primitives |
| `moda_site` | Public website, responsive UI, SEO, product positioning and marketing-facing content |
| `moda_system_test` | Integrated architecture validation, architecture-specific fixtures and test-environment orchestration |

Use a specialist agent for bounded repository implementation. Use
`moda_architect` when work changes repository boundaries, database/shared
contracts, queue or webhook semantics, deployment sequencing, security
boundaries or architecture-level behaviour.

### Canonical agent definitions and synchronization

Codex TOML files are the canonical authored logical-agent definitions:

```text
.codex/agents/<name>.toml
```

Claude definitions are generated runtime representations:

```text
.claude/agents/<name>.agent.md
```

The intended flow is:

```text
.codex/agents/*.toml
        |
        | canonical logical-agent behaviour
        v
   sync_agents.py
        |
        v
.claude/agents/*.agent.md
```

Do not independently maintain the same logical-agent behaviour in both
locations.

A normal agent-definition change is:

```text
1. Edit .codex/agents/<agent>.toml
2. Keep developer_instructions runtime-neutral
3. Run python3 sync_agents.py --agent <agent>
4. Review the generated Claude definition
5. Run python3 sync_agents.py --check
6. Developer reviews and commits canonical + generated changes together
```

Useful commands:

```bash
# Regenerate all Claude definitions
python3 sync_agents.py

# Verify without changing files
python3 sync_agents.py --check

# Regenerate one logical agent
python3 sync_agents.py --agent moda_background

# Regenerate selected agents
python3 sync_agents.py \
  --agent moda_app \
  --agent moda_background

# Remove obsolete generated Claude definitions
python3 sync_agents.py --prune
```

`--prune` cannot be combined with `--agent`.

#### Runtime-neutral developer instructions

Although the canonical source lives under `.codex/agents/`,
`developer_instructions` describes the **logical Moda role**, not Codex itself.

Prefer:

```text
When claiming a task, set executor to the identifier for the current execution
runtime.
```

Do not hard-code logical behaviour to:

```text
executor: codex
```

The same task may therefore record:

```text
Copilot   -> executor: copilot
Codex     -> executor: codex
Claude    -> executor: claude
Continue  -> executor: continue
```

`sync_agents.py --check` validates synchronization and is suitable for CI or
pre-commit verification.

### Agent Node.js environment

Agent shells may be non-interactive.

Before concluding that Node/npm/npx/corepack/Shopify CLI is missing, bootstrap:

```bash
source scripts/bootstrap-node.sh
```

The concrete development Node version remains in `.nvmrc`; agent definitions do
not duplicate it.

To propagate the version-independent Node bootstrap policy:

```bash
python3 scripts/apply-node-agent-policy.py
python3 sync_agents.py
```

---

### Agent startup context and token efficiency

Moda Interact deliberately separates model judgement from deterministic workflow
so context is spent on engineering rather than rediscovering stable workspace
facts.

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
relevant dependency / contract context
```

In practice this is approximately **9,000-10,000 tokens of startup context for a
typical implementation task** before substantial code inspection and
implementation begins.

The goal is not to remove governance simply to save tokens.

Token efficiency instead comes from:

- focused logical-agent definitions;
- one canonical task execution protocol;
- generated Claude definitions rather than duplicated rules;
- deterministic task/repository/agent resolution;
- metadata-first dependency checks;
- loading detailed dependency/reference material only when needed;
- moving mechanical workflow operations into scripts.

The operating principle is:

> **Use model context for judgement and engineering decisions; use deterministic
> tooling for routing, validation and workflow mechanics.**

---

## Platform workload and scalability

Moda Interact is a multi-tenant event-driven platform. Scale is not treated as
one generic number.

The platform architecture uses a raw Shopify ingress planning workload of roughly
**20,000-22,000 Shopify events per minute** depending on the specific
architecture initiative.

ARCH-002 currently defines a production ingress planning target of approximately:

```text
22,000 events/minute
≈ 367 events/second
```

This is raw Shopify ingress, **not** 22,000 recoveries, WhatsApp messages,
CommerceAgent turns or LLM requests per minute.

The intended processing shape is:

```text
Shopify event ingress
        |
        v
thin authenticated ingress
        |
        v
Redis / BullMQ durable acceptance / queue boundary
        |
        v
background event inspection
        |
        +--------------------+
        |                    |
        v                    v
irrelevant majority      actionable subset
                              |
                              v
                     recovery/business work
                              |
                              v
                       messaging subset
                              |
                              v
                    CommerceAgent / LLM
```

Capacity reasoning must distinguish:

- webhook events received;
- events queued and inspected;
- events discarded;
- durable business-state transitions;
- CheckoutRecovery workflows;
- queue depth, lag and oldest-event age;
- PostgreSQL queries/writes;
- WhatsApp messages;
- CommerceAgent turns;
- LLM requests;
- Shopify Admin API requests;
- Meta API requests.

Queue lag and oldest-event age are primary asynchronous-capacity signals.

Measured capacity, estimates and assumptions must be labelled separately.

---

## Working with Git submodules

### Working with a service

A submodule is normally checked out at the exact commit recorded by the
workspace, which may leave the service in detached HEAD state.

Before starting new implementation work:

```bash
cd moda-interact-messaging

git status
git switch main
git pull --ff-only origin main
```

For an architecture task, the repository agent makes and validates the service
change, moves the task to `review`, and stops.

After architect acceptance, the **developer/user** commits and pushes the
accepted service change:

```bash
git add .
git commit -m "describe the change"
git push
```

Return to the workspace root:

```bash
cd ..
git status
```

The workspace now sees the newer service commit:

```text
modified: moda-interact-messaging (new commits)
```

Record the new platform snapshot:

```bash
git add moda-interact-messaging
git commit -m "update messaging service"
git push
```

The two-level commit model is intentional, and both publication steps belong to
the developer/user:

```text
repository agent
    |
    +--> implementation + validation + review
             |
             v
moda_architect
    |
    +--> accept
             |
             v
developer / user
    |
    +--> service repository commit + push
             |
             v
developer / user
    |
    +--> workspace repository records compatible service commit
```

### Updating submodules

Fetch the commits already referenced by the workspace:

```bash
git submodule update --init --recursive
```

To inspect/fetch newer configured remote commits:

```bash
git submodule update --remote --recursive
```

Review changes before committing updated workspace pointers.

### Detached HEAD recovery

Detached HEAD is normal after recursive clone/update because the workspace
records commit SHAs rather than branches.

If commits were accidentally made while detached, do not discard them.

Find them:

```bash
git reflog --oneline
```

Then either cherry-pick:

```bash
git switch main
git cherry-pick <detached-commit-sha>
git push
```

or preserve a longer series:

```bash
git switch -c recover-work <latest-detached-commit-sha>
git switch main
git merge recover-work
git push
```

Afterward, update the top-level workspace submodule pointer.

### Checking submodule status

```bash
git submodule status --recursive
```

### Database submodule

`moda-interact-database` is also consumed as a nested submodule by services that
need the canonical Prisma schema.

The same repository can therefore appear at multiple paths:

```text
moda-interact-database/
moda-interact/database/
moda-interact-background/database/
```

These are independent checkouts and can point to different commits.

A typical database change flow is:

```text
1. moda_database changes + validates the database task
2. moda_database moves the task to review and STOPS
3. moda_architect accepts the database task
4. developer commits + pushes moda-interact-database
5. architect verifies the published database commit
6. affected repository agent updates its nested database submodule to the
   architect-approved published commit and implements/validates its task
7. affected repository agent moves its task to review and STOPS
8. moda_architect accepts the affected repository task
9. developer commits + pushes the affected service
10. developer updates top-level workspace submodule pointers
11. developer commits + pushes the compatible workspace snapshot
```

Keep database pointers aligned intentionally when services are meant to consume
the same schema revision.

---

## Useful commands

```bash
# Clone the complete workspace
git clone --recurse-submodules \
  https://github.com/kodjobaah/moda-interact-workspace.git

# Initialise missing submodules
git submodule update --init --recursive

# Show all submodule commits
git submodule status --recursive

# Open the VS Code workspace
code moda-interact.code-workspace

# Bootstrap Node/NVM
source scripts/bootstrap-node.sh

# Quick workspace environment/dependency validation
"$MODA_WORKSPACE_ROOT/scripts/workspace-doctor.sh" --quick

# Production-focused workspace validation
"$MODA_WORKSPACE_ROOT/scripts/workspace-doctor.sh" --production

# Regenerate Claude agents from canonical Codex definitions
python3 sync_agents.py

# Verify agent synchronization
python3 sync_agents.py --check

# Resolve an architecture task without launching it
python3 scripts/start-agent-task.py ARCH-002-SHOPIFY-001 --json

# Inspect the detailed coding-agent workflow
cat docs/coding-agent-workflow.md

# Inspect developer-owned Git/VCS publication policy
cat docs/agent-vcs-ownership-policy.md

# Inspect Copilot implementation-model planning
cat docs/copilot-model-selection.md

# Inspect current high-level architecture initiatives
cat docs/architecture/ARCH-001-shopify-checkout-recovery-webhook-processing.md
cat docs/architecture/ARCH-002-render-production-gateway-infrastructure.md
```

---

## Development principles

The workspace coordinates the platform without replacing independent service
ownership.

- Shopify-facing concerns belong in `moda-interact`.
- Platform administration belongs in `moda-interact-admin`.
- Long-running, retryable and state-correlating workflows belong in
  `moda-interact-background`.
- Shared data models and migrations belong in `moda-interact-database`.
- Public ingress, Render topology and infrastructure routing belong in
  `moda-interact-gateway`.
- Messaging-provider ingress belongs in `moda-interact-messaging`.
- Canonical cross-service runtime contracts belong in `moda-interact-shared`.
- Public product and marketing content belongs in `moda-interact-site`.
- Architecture-specific integrated validation belongs in
  `moda-interact-system-test`.
- Cross-repository architecture, sequencing, implementation review and final
  architecture acceptance belong to `moda_architect`.
- Repository agents implement and validate work but stop at `status: review`;
  Git commit/push publication belongs to the developer/user unless explicitly
  delegated for one task.

The workspace records how these independently deployed parts fit together and
provides durable architecture/task state across Copilot, Claude Code, Codex and
Continue.

---

## Related documentation

- [Architecture overview](docs/architecture/overview.md)
- [Service boundaries](docs/architecture/services.md)
- [Coding agent workflow](docs/coding-agent-workflow.md)
- [Git / VCS ownership policy](docs/agent-vcs-ownership-policy.md)
- [Copilot model selection](docs/copilot-model-selection.md)
- [Development baseline](docs/development-baseline.md)
- [Node.js toolchain](docs/node-toolchain.md)
- [ARCH-001: Shopify checkout recovery webhook processing](docs/architecture/ARCH-001-shopify-checkout-recovery-webhook-processing.md)
- [ARCH-002: Render test and production gateway and infrastructure](docs/architecture/ARCH-002-render-production-gateway-infrastructure.md)
