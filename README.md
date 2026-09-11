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
- [Inbound WhatsApp recovery flow](#inbound-whatsapp-recovery-flow)
- [Architecture initiatives](#architecture-initiatives)
- [Pricing and billing model](#pricing-and-billing-model)
- [Internationalisation and merchant communications](#internationalisation-and-merchant-communications)
- [Projects and ownership](#projects-and-ownership)
- [Getting started](#getting-started)
- [Task workflow quick start](#task-workflow-quick-start)
- [Architecture-led development](#architecture-led-development)
- [Task branches and publication](#task-branches-and-publication)
- [Launching and updating tasks](#launching-and-updating-tasks)
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

## Inbound WhatsApp recovery flow

The shopper-facing WhatsApp path crosses several architectural boundaries: Meta
webhook ingress, raw abuse admission, tenant/recovery routing, durable message
persistence, fragmented-message coalescing, multi-basket clarification,
settled-turn abuse admission, outbound safety admission and CommerceAgent/provider
execution.

The canonical end-to-end description is:

**[Inbound WhatsApp recovery and multi-basket runtime flow](docs/architecture/inbound-whatsapp-recovery-flow.md)**

That document also makes the identity model explicit:

```text
CheckoutRecovery
    = one abandoned-basket recovery lifecycle

Conversation
    = one durable conversational processing/safety scope

customer / WhatsApp sender
    = abuse boundary spanning that customer's conversations
```

A customer may have several active abandoned baskets and therefore several
candidate recoveries/conversation contexts. Those baskets do **not** multiply the
customer's sender-level abuse allowance: sender limits span conversations and
recoveries, while conversation limits remain independent per durable
`Conversation` and shop/global limits provide wider protection.

Detailed task files remain the implementation/review evidence. The consolidated
runtime-flow document is the preferred starting point for understanding how those
decisions fit together.

---

## Architecture initiatives

Architectural work is organised around stable `ARCH-XXX` initiative IDs.

An architecture ID identifies a **complete architectural outcome**, not one
implementation task.

| Architecture | Status | High-level architectural goal | Architecture decision | Copilot implementation plan |
| --- | --- | --- | --- | --- |
| **ARCH-001** | Agreed | Build a reliable, low-overhead Shopify checkout-recovery event pipeline: keep webhook ingress fast, use Redis/BullMQ for temporary recovery candidates, persist only actual `CheckoutRecovery` state, fetch current Shopify state only when recovery is required, use canonical cross-service contracts, and tolerate duplicate/concurrent asynchronous processing. | [Shopify Checkout Recovery Webhook Processing](docs/architecture/ARCH-001-shopify-checkout-recovery-webhook-processing.md) | [Copilot model and task plan] |
| **ARCH-002** | In progress | Establish a production-ready, version-controlled Render topology for test and production: thin public gateway, private application services, independently scalable background workers, environment-isolated PostgreSQL/Redis/telemetry, admin security, observability, deployment validation and capacity testing. | [Render Test and Production Gateway and Infrastructure](docs/architecture/ARCH-002-render-production-gateway-infrastructure.md) | [Copilot model and task plan](docs//models/ARCH-002/copilot-model-selection.md) |
| **ARCH-003** | In progress | Provide tenant-aware operational visibility for the asynchronous recovery platform: Admin queue health and failed-job diagnostics, safe tenant attribution, shop-scoped pending-recovery visibility in the merchant Usage experience, bounded refresh/pagination, complete BullMQ queue-performance telemetry and integrated evidence of tenant isolation. | [Admin Operational Queue Observability UI](docs/architecture/ARCH-003-admin-operational-ui.md) · [Readable overview](docs/architecture/ARCH-003-operational-observability-overview.md) | Task plans live under `docs/decisions/*/ARCH-003/` |
| **ARCH-004** | In progress | Make pending recovery an inactivity-based workflow: deterministically correlate checkout/cart activity to an existing candidate, advance a monotonic `lastActivityAt` clock, reschedule the same BullMQ candidate and shop index, ignore stale/out-of-order events, cancel confirmed empty carts and preserve existing order-cancellation semantics. | [Correlated Cart Activity Recovery Rescheduling](docs/architecture/ARCH-004-cart-activity-recovery-rescheduling.md) · [Readable overview](docs/architecture/ARCH-004-cart-activity-recovery-rescheduling-overview.md) | Task plans live under `docs/decisions/*/ARCH-004/` |
| **ARCH-005** | In progress | Make Moda Interact internationally correct by design across WhatsApp markets: keep country, language, currency, time zone and telephone country independent; use standards-based locale contracts; capture Shopify international commerce context; select approved WhatsApp template variants; support multilingual active conversations; and localise merchant-facing formatting. | [Global Internationalisation and WhatsApp Markets](docs/architecture/ARCH-005-global-internationalisation-whatsapp-markets.md) · [Readable overview](docs/architecture/ARCH-005-internationalisation-overview.md) | Task plans live under `docs/decisions/*/ARCH-005/` |
| **ARCH-006** | In progress | Add a shop-scoped internal support inbox between Moda administrators and merchants: immutable originals, multilingual translations, read state, distinct administrative/system/merchant messages, versioned automated notifications, tenant-safe access and an observable `merchant-communications` queue. | [Merchant Communications, Support Inbox and System Notifications](docs/architecture/ARCH-006-merchant-communications-support-inbox.md) · [Readable overview](docs/architecture/ARCH-006-merchant-communications-overview.md) | Task plans live under `docs/decisions/*/ARCH-006/` |
| **ARCH-007** | Partially superseded | Historical billing/cost-control foundation and completed implementation evidence. Merchant subscription, entitlement, recovery-capacity, top-up, refund and lifecycle semantics are superseded by ARCH-010; retained ARCH-007 message/provider safety primitives remain valid unless explicitly replaced. | [Historical ARCH-007 architecture](docs/architecture/ARCH-007-shopify-billing-usage-cost-control.md) · [ARCH-010 supersession map](docs/architecture/ARCH-010-supersession-map.md) | Historical task records live under `docs/decisions/*/ARCH-007/` |
| **ARCH-010** | Agreed / implementation-ready | Define the current merchant subscription and lifecycle state machine: one-time shop-lifetime Free grant, period-scoped paid allowance, promotional/purchased/lifetime capacity ordering, App Pricing top-ups, plan changes, cancellation, freeze, uninstall/reinstall, partial top-up refunds and exact execution gates. | [Merchant lifecycle state transitions](docs/architecture/ARCH-010-merchant-lifecycle-state-transitions.md) · [Current pricing/billing model](docs/product/pricing-and-billing-model.md) · [Supersession map](docs/architecture/ARCH-010-supersession-map.md) | [Implementation handoff](docs/architecture/ARCH-010-implementation-handoff.md) |

The architecture document is authoritative for **what is being built and how the
complete system fits together**.

The Copilot plan is an implementation-planning aid. It recommends implementation
models for repository-agent work and does not override architecture or task
state. Architect review is performed separately through the `moda_architect`
workflow.

### Pricing and billing model

Merchant billing and lifecycle behaviour is now governed by **ARCH-010**. ARCH-007 remains historical implementation/review evidence and retains non-superseded cost/safety primitives, but its old automatic-overage, Free-allowance-adjustment and capacity-order rules are not current product policy.

The current target catalogue is:

| Plan | Shopify recurring price* | Paid monthly included recoveries | Shop-lifetime Free grant | Automatic paid overage |
| --- | ---: | ---: | ---: | --- |
| **Free** | $0 | none | 5 once per shop | none |
| **Starter** | $35/month | 200/current verified period | 5 once per shop | none |
| **Growth** | $75/month | 500/current verified period | 5 once per shop | none |
| **Scale** | $149/month | 1,200/current verified period | 5 once per shop | none |

\* Shopify App Pricing is authoritative for the live commercial price, currency, billing cycle and pending plan change.

The five lifetime Free credits belong to the **Shop**, not to the Free subscription. They are granted once at first verified activation even when the merchant starts directly on a Paid plan, and they never reset on renewal, upgrade, downgrade, cancellation, uninstall or reinstall.

The canonical recovery-capacity order is:

```text
Paid:
  current-period monthly included
  -> promotional
  -> purchased lifetime top-ups
  -> shop-lifetime Free
  -> BLOCK NEW RECOVERY ADMISSION

Free:
  promotional
  -> purchased lifetime top-ups
  -> shop-lifetime Free
  -> BLOCK NEW RECOVERY ADMISSION
```

`BLOCK NEW RECOVERY ADMISSION` means capacity exhaustion stops a **new** recovery from being admitted. It does not disable the merchant dashboard and does not terminate an already-admitted conversation solely because capacity later reaches zero.

Promotional credits are a separate Moda-funded, non-refundable shop-specific bucket for targeted campaigns, beta/test merchants, goodwill and support. Purchased top-ups are merchant-funded lifetime credits with FIFO purchase-lot accounting and partial-unused-credit refund support.

Top-ups use the current Shopify App Pricing **usage meter + App Event** mechanism. A Free `$0` App Pricing plan may therefore still have a Shopify provider billing cycle for App Event scope; that billing cycle never replenishes the five lifetime Free credits.

For the current product model and exact supersession boundary, start with:

- **[Current pricing, billing and recovery-capacity model](docs/product/pricing-and-billing-model.md)**
- **[ARCH-010 merchant lifecycle state transitions](docs/architecture/ARCH-010-merchant-lifecycle-state-transitions.md)**
- **[ARCH-010 billing/lifecycle supersession map](docs/architecture/ARCH-010-supersession-map.md)**
- **[ARCH-010 implementation handoff](docs/architecture/ARCH-010-implementation-handoff.md)**

Do not use the historical ARCH-007 overage/allowance-adjustment model to infer current merchant billing behaviour.

### Internationalisation and merchant communications

Two current cross-service initiatives extend the platform beyond the original
checkout-recovery path:

- **ARCH-005 — Internationalisation and Global WhatsApp Markets** keeps
  language, country, currency, time zone and telephone country independent;
  uses standards-based locale identifiers; captures international Shopify
  commerce context; selects approved WhatsApp template variants; and lets active
  CommerceAgent conversations follow the customer's resolved language. See the
  [internationalisation overview](docs/architecture/ARCH-005-internationalisation-overview.md).
- **ARCH-006 — Merchant Communications, Support Inbox and System
  Notifications** adds a separate internal Moda-to-merchant communication
  channel. One thread belongs to a `Shop`; administrators and merchants can
  exchange messages, originals remain immutable, translations are stored
  separately, read state is tracked, and automated `SYSTEM` messages remain
  distinct from human administrative messages. See the
  [merchant communications overview](docs/architecture/ARCH-006-merchant-communications-overview.md).

ARCH-006 reuses ARCH-005's canonical language primitives rather than defining a
second locale model. The merchant support inbox is also deliberately separate
from shopper WhatsApp `ConversationMessage` state.

### Architecture and task documentation

The central architecture and execution state lives under [`docs/`](docs/). New
contributors should start with
[`docs/task-workflow-quickstart.md`](docs/task-workflow-quickstart.md) before
reading the deeper policy documents.

```text
docs/
├── architecture/
├── decisions/
├── contracts/
├── product/
├── task-workflow-quickstart.md
├── task-definition-materialization.md
├── developer-task-workflow.md
├── coding-agent-workflow.md
├── agent-worktree-isolation-policy.md
├── agent-vcs-ownership-policy.md
├── agent-task-execution-template.md
├── task-worktree-review-archive-helper.md
├── development-baseline.md
└── node-toolchain.md
```

The source-of-truth hierarchy is:

| Source | Question answered |
| --- | --- |
| `docs/architecture/ARCH-XXX-*.md` | What are we building and how does the complete system fit together? |
| `docs/decisions/<domain>/ARCH-XXX/_index.md` | What work does this logical agent/domain own for this architecture? |
| `docs/decisions/<domain>/ARCH-XXX/<TASK>.md` | What exactly must be implemented, what state is it in, and how was it reviewed? |
| Repository source code | What has actually been implemented and how does it behave? |
| Git history | What exact source versions existed and in what sequence? |

When a later architecture explicitly supersedes overlapping behaviour, the newer architecture governs that overlap. Older architecture/task files remain valid historical implementation and review evidence, but they must not override the newer current contract. For merchant billing/lifecycle, see [`ARCH-010-supersession-map.md`](docs/architecture/ARCH-010-supersession-map.md).

A task may first exist as a **portable task definition** outside Git. It becomes a
durable workspace task only when materialised into its canonical decision path on
`task/<TASK_ID>`. Task definition, materialisation and implementation are separate
phases; see
[`docs/task-definition-materialization.md`](docs/task-definition-materialization.md).

Task YAML metadata is authoritative for task state. The parent architecture
document is authoritative for overall architectural intent. Source code is
authoritative for actual runtime behaviour. Git is version history rather than a
substitute for Completion Reports or architectural review records.


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
│       ├── moda-task/
│       ├── moda_developer_create/
│       └── moda_developer_update/
├── .claude/
│   ├── agents/
│   └── skills/
│       ├── moda-task/
│       ├── moda_developer_create/
│       └── moda_developer_update/
├── .continue/
│   └── prompts/
├── docs/
│   ├── architecture/
│   ├── contracts/
│   ├── decisions/
│   ├── product/
│   ├── task-workflow-quickstart.md
│   ├── task-definition-materialization.md
│   ├── developer-task-workflow.md
│   ├── coding-agent-workflow.md
│   ├── agent-worktree-isolation-policy.md
│   ├── agent-vcs-ownership-policy.md
│   └── task-worktree-review-archive-helper.md
├── scripts/
│   ├── start-agent-task.py
│   ├── sync_agents.py
│   ├── sync-skills.py
│   ├── bootstrap-node.sh
│   └── workspace-doctor.sh
├── .gitmodules
├── .nvmrc
├── README.md
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

Task execution uses dedicated worktrees **beside** this canonical workspace. Their
absolute locations are derived by `scripts/start-agent-task.py`; no workflow may
assume a fixed `/Users/...`, `~/project`, `/home/...` or other checkout path.


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

The IDE should normally open the canonical `moda-interact-workspace`, but task
commands and agent sessions are not required to begin with `$PWD` at that root.
The launcher resolves the canonical workspace independently and exposes the
resolved root/worktree topology to the execution workflow.

When manually bootstrapping from the workspace root:

```bash
source scripts/bootstrap-node.sh
"$MODA_WORKSPACE_ROOT/scripts/workspace-doctor.sh" --quick
```

`MODA_WORKSPACE_ROOT` is the stable canonical workspace path for the rest of the
session. If execution later moves into a task-specific implementation worktree,
continue to invoke workspace tooling through that resolved root rather than
searching for repository-local copies.

`.nvmrc` remains the single source of truth for the workspace development Node
version. Agent definitions and task workflow documents do not embed a concrete
Node version.

The workspace doctor classifies known environment/dependency conditions as:

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

See:

- [`docs/development-baseline.md`](docs/development-baseline.md)
- [`docs/node-toolchain.md`](docs/node-toolchain.md)
- [`docs/agent-worktree-isolation-policy.md`](docs/agent-worktree-isolation-policy.md)
- [`scripts/bootstrap-node.sh`](scripts/bootstrap-node.sh)
- [`scripts/workspace-doctor.sh`](scripts/workspace-doctor.sh)

<!-- MODA-DEVELOPMENT-BASELINE:END -->

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

## Task workflow quick start

All architecture work uses the same task system whether implementation is performed
by a repository agent or directly by a developer. The task owns the architectural
contract and review history; Git remains ordinary version control.

Start here:

**[Task workflow quick start](docs/task-workflow-quickstart.md)**

The primary commands are:

| Command | Purpose |
| --- | --- |
| `/moda-task <TASK_ID>` | Materialise/prepare an agent task if needed, create or reuse canonical worktrees, claim it and hand execution to the assigned repository agent. |
| `/moda_developer_create <TASK_ID>` | Define/materialise a missing developer task when needed, or prepare/resume an existing developer task, then claim it for the developer. |
| `/moda_developer_update <TASK_ID>` | Reconcile the real implementation, validation and task record for the current developer attempt. |
| `/moda_developer_update <TASK_ID> complete` | Explicitly complete a task whose `completion_mode` is `developer`. |
| `/moda_developer_update <TASK_ID> reopen` | Reopen a completed task to `ready`; the next claim creates Attempt N+1. |

Four supported entry paths are first-class:

```text
Architect defines -> Agent implements
Architect defines -> Developer implements
Developer defines -> Developer implements
Developer reopens -> Developer implements next attempt
```

An architect may define a task outside any development environment. In that case,
the portable task definition may exist while **no branch or worktree exists yet**.
Materialisation later creates the parent task branch/worktree; the implementation
worktree is created only when execution actually starts.

Every executable task ultimately uses the launcher-resolved pair:

```text
parent task worktree:
  <workspace-parent>/<workspace-name>-task-<TASK_ID>

implementation task worktree:
  <workspace-parent>/<workspace-name>.worktrees/<TASK_ID>

branch in both repositories:
  task/<TASK_ID>
```

The launcher supplies the actual absolute paths for the current checkout. Do not
copy path examples from another developer's machine.

---

## Architecture-led development

Moda Interact treats conversation as temporary execution context and the repository
as durable engineering state. One task format supports repository-agent and
developer execution.

Detailed specifications:

- [Task workflow quick start](docs/task-workflow-quickstart.md)
- [Coding agent workflow](docs/coding-agent-workflow.md)
- [Developer-executed task workflow](docs/developer-task-workflow.md)
- [Task definition and materialisation](docs/task-definition-materialization.md)
- [Task worktree isolation](docs/agent-worktree-isolation-policy.md)
- [Git/VCS ownership](docs/agent-vcs-ownership-policy.md)

### Architecture execution workflow

Architecture and execution are deliberately separate:

```text
requirement
    |
    v
moda_architect / developer-as-architect
    |
    +--> define architecture/task
    |
    +--> portable definition may exist outside Git
    |
    v
materialise task when a development environment is available
    |
    v
status: ready
    |
    +--> /moda-task                 -> agent execution
    |
    +--> /moda_developer_create     -> developer execution
    |
    v
status: in_progress
    |
    v
implementation + validation
    |
    v
status: review
    |
    +--> automatic completion path -> authorised review -> complete
    |
    +--> developer completion mode -> explicit developer decision -> complete
```

Task frontmatter distinguishes implementation and completion authority:

```yaml
execution_mode: agent | developer
completion_mode: automatic | developer
```

Legacy tasks without these fields are interpreted as `agent` / `automatic`.
`assigned_agent` always remains the architectural/domain owner, even when the
developer is the executor.

A developer-executed task may ask its assigned agent for bounded assistance. The
agent may inspect, debug, edit explicitly requested code, add tests and run
validation in the canonical developer worktree, but it does not claim, complete,
reopen or change lifecycle ownership of the task.

### Task branches and publication

Every executable task uses two independent Git histories with the same branch name:

```text
parent workspace repository:       task/<TASK_ID>
implementation repository:         task/<TASK_ID>
```

At the beginning of each attempt, the task workflow fetches remote state,
fast-forwards from the corresponding remote task branch when possible, and
incorporates current `origin/main` **into** the task branch before new work.

At the end of an implementation/review submission, task-owned changes are committed
and pushed on the task branches. The executor must never merge the task branch into
`main`, push/update `main`, force-push, or use a remote merge action. Mainline
integration remains an explicit developer/repository-owner action outside task
execution.

```text
origin/main -> task/<TASK_ID>     allowed for synchronization
task/<TASK_ID> -> origin/main     forbidden to task executors
```

Git is not the semantic work report. One workflow attempt may contain many normal
commits, corrections, experiments and reverts. The task Completion Report explains
what was ultimately implemented and validated.

### Task lifecycle, completion and reopening

The canonical task statuses remain:

```text
pending -> ready -> in_progress -> review -> complete
```

`defined` and `materialised` are lifecycle concepts, not additional YAML states. A
portable architect definition can exist before the task is materialised into Git.

Claiming a ready task records an executor and increments the attempt. `reopen` does
not claim the next attempt:

```text
complete (Attempt N)
        |
        | /moda_developer_update TASK reopen
        v
ready (Attempt N, unclaimed)
        |
        | /moda_developer_create TASK
        v
in_progress (Attempt N+1, executor: developer)
```

Reopening preserves the previous accepted attempt and review history. Unstarted
downstream tasks may have their readiness recalculated; downstream tasks that
already have implementation history are never silently rewritten and instead
require dependency-regression review.

For `completion_mode: developer`, a successful `/moda_developer_update TASK` may
place the task in `review`, but only the explicit:

```text
/moda_developer_update TASK complete
```

records the developer's completion decision. Complete tasks from either completion
mode may later be reopened explicitly.

### Dedicated task worktrees

Task execution never switches shared/default service checkouts onto task branches.
The launcher derives and returns the canonical parent and implementation worktree
paths from the actual workspace root.

Missing worktrees are normal on first execution and are created. Existing correct
worktrees are reused across later attempts. An existing wrong repository/branch/path
mapping is workflow non-conformance and must not be repaired by repurposing a shared
checkout.

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

## Launching and updating tasks

### Agent execution: `/moda-task <TASK_ID>`

Use `/moda-task` when `execution_mode` is `agent` (or on legacy tasks where the
field is absent). The command routes through `scripts/start-agent-task.py`, resolves
the logical agent/repository/canonical task topology, materialises an available
portable task definition when necessary, creates or reuses the dedicated task
worktrees, synchronises task branches, performs eligibility checks and hands the
task to the assigned repository agent.

```text
/moda-task ARCH-007-BACKGROUND-015
```

The launcher itself is routing/topology tooling: it does not invent architecture,
claim tasks, implement code or approve reviews.

### Developer execution: `/moda_developer_create <TASK_ID>`

Use `/moda_developer_create` when the developer will perform the implementation. It
is intentionally idempotent:

```text
missing portable/materialised task -> architect-definition/materialisation -> prepare -> claim
ready developer task               -> prepare -> claim
in_progress developer task         -> verify/reuse -> resume
review developer task              -> use /moda_developer_update
complete task                      -> explicit reopen first
```

An architect-created developer task may exist only as a portable Markdown definition
until this command is run in a development environment. No parent or implementation
worktree is assumed to exist merely because the architect defined the task.

### Developer review/update

```text
/moda_developer_update <TASK_ID>
/moda_developer_update <TASK_ID> complete
/moda_developer_update <TASK_ID> reopen
```

The base update action analyses the actual implementation, working tree, task-branch
history, tests and task contract; it updates the Completion Report/review evidence
rather than reconstructing work from commit messages alone. `complete` is the
explicit completion authority for developer-controlled completion. `reopen` moves a
completed task back to `ready` without incrementing the attempt; the next claim
creates Attempt N+1.

### Portable definitions and route-only resolution

When architecture occurs outside the development environment, the architect may
return the exact canonical task Markdown as a portable definition. It can later be
materialised by the relevant task command.

For topology inspection before a task exists in Git:

```bash
python3 scripts/start-agent-task.py ARCH-007-BACKGROUND-015 --route-only --json
```

An unmaterialised route reports task topology but does **not** guess
`execution_mode` or `completion_mode`; those values come from the actual portable or
materialised task frontmatter.

### Workspace-location independence

`start-agent-task.py` resolves the canonical workspace from its own verified script
location and derives the parent/implementation worktree paths from that workspace.
Task commands must not infer canonical paths from `$PWD`, user names, home-directory
layouts or examples copied from another machine.

### Runtime integration

Canonical skills live under `.codex/skills/` and generated Claude/Copilot mirrors
live under `.claude/skills/`:

```text
moda-task
moda_developer_create
moda_developer_update
```

After changing canonical agent/skill definitions:

```bash
python3 scripts/sync_agents.py
python3 scripts/sync-skills.py
python3 scripts/sync_agents.py --check
python3 scripts/sync-skills.py --check
```

Continue/Copilot/Claude/Codex are runtime adapters around the same durable task
state and policies; they must not invent a parallel lifecycle.


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
   scripts/sync_agents.py
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
3. Run python3 scripts/sync_agents.py --agent <agent>
4. Review the generated Claude definition
5. Run python3 scripts/sync_agents.py --check
6. Developer reviews and commits canonical + generated changes together
```

Useful commands:

```bash
# Regenerate all Claude definitions
python3 scripts/sync_agents.py

# Verify without changing files
python3 scripts/sync_agents.py --check

# Regenerate one logical agent
python3 scripts/sync_agents.py --agent moda_background

# Regenerate selected agents
python3 scripts/sync_agents.py \
  --agent moda_app \
  --agent moda_background

# Remove obsolete generated Claude definitions
python3 scripts/sync_agents.py --prune
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

`scripts/sync_agents.py --check` validates synchronization and is suitable for CI or
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
python3 scripts/sync_agents.py
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

The canonical workspace records exact compatible service commits as Gitlinks, but
architecture-task implementation does **not** happen by switching the shared
submodule checkout to a task branch. Executable tasks use the launcher-resolved
dedicated implementation worktree instead.

### Task implementation

For a task such as `ARCH-007-MESSAGING-005`, execution occurs conceptually at:

```text
<workspace-parent>/<workspace-name>.worktrees/ARCH-007-MESSAGING-005
branch: task/ARCH-007-MESSAGING-005
```

The shared workspace submodule remains a reference/source checkout. The task workflow
fetches/synchronises the dedicated task branch before implementation and commits/pushes
task-owned changes there. It never merges the task branch to `main`.

### Recording accepted service commits in the workspace

Mainline merge/integration is a separate developer/repository-owner action. After an
accepted implementation branch has been intentionally integrated/published to the
service's `main`, update the canonical workspace Gitlink intentionally and review the
resulting platform snapshot before committing it on `main`. Task executors do not
automatically update the parent workspace's service Gitlink merely to record a task
report commit.

### Updating submodules

To fetch commits already referenced by the workspace:

```bash
git submodule update --init --recursive
```

To inspect/fetch newer configured remote commits:

```bash
git submodule update --remote --recursive
```

Review all resulting Gitlink changes before integrating them.

### Detached HEAD recovery

Detached HEAD is normal for a submodule reference checkout because the workspace
records commit SHAs. If manual commits were accidentally made while detached, preserve
them with `git reflog` and recover them onto an intentional branch; do not discard
unknown work. New architecture tasks should use their dedicated task worktree rather
than repairing the shared submodule into a task execution checkout.

### Checking submodule status

```bash
git submodule status --recursive
```

### Database repository and nested Gitlinks

`moda-interact-database` may appear both as a top-level workspace submodule and as a
nested submodule in services. These are independent reference checkouts and may point
to different commits. A database architecture task is implemented/published on its
own task branch first. Consumer tasks should consume only the architect-approved
published database commit required by their dependency contract and must update their
nested Gitlink deliberately inside their own dedicated task worktree.

Publication to `main` and top-level platform-snapshot Gitlink integration remain
separate developer/repository-owner operations after task acceptance.


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

# Bootstrap Node/NVM when working from the canonical workspace
source scripts/bootstrap-node.sh

# Quick workspace environment/dependency validation
"$MODA_WORKSPACE_ROOT/scripts/workspace-doctor.sh" --quick

# Resolve an existing architecture task
python3 scripts/start-agent-task.py ARCH-007-BACKGROUND-015 --json

# Resolve topology for a task that may not yet be materialised
python3 scripts/start-agent-task.py ARCH-007-BACKGROUND-015 --route-only --json

# Regenerate/check Claude/Copilot agent mirrors
python3 scripts/sync_agents.py
python3 scripts/sync_agents.py --check

# Regenerate/check Claude/Copilot skill mirrors
python3 scripts/sync-skills.py
python3 scripts/sync-skills.py --check

# Workflow onboarding
cat docs/task-workflow-quickstart.md
cat docs/developer-task-workflow.md
cat docs/task-definition-materialization.md
cat docs/agent-worktree-isolation-policy.md
cat docs/agent-vcs-ownership-policy.md
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
- Cross-repository architecture, sequencing and dependency governance belong to
  `moda_architect`; developer-mode tasks may additionally exercise explicit
  developer-as-architect completion/reopen authority.
- Agent and developer task execution uses dedicated physical worktrees and mirrored
  `task/<TASK_ID>` branches.
- Task executors commit and push task-owned task branches, but never merge or push
  `main`.
- Git records source history; task documents record architectural intent, final
  implementation evidence, validation and review decisions.
- A Complete task may be explicitly reopened by the developer; reopening preserves
  history and returns the task to `ready` before the next attempt is claimed.
- System-test tasks may become dependency-ready automatically but remain manual-gated
  until explicitly invoked where the architecture requires that gate.

The workspace provides durable architecture/task state across Copilot, Claude Code,
Codex, Continue and direct developer execution without creating separate workflow
systems for each runtime.


---

## Related documentation

### Start here for engineering workflow

- [Task workflow quick start](docs/task-workflow-quickstart.md)
- [Developer-executed architecture task workflow](docs/developer-task-workflow.md)
- [Task definition and materialisation](docs/task-definition-materialization.md)
- [Coding agent workflow](docs/coding-agent-workflow.md)
- [Task worktree isolation policy](docs/agent-worktree-isolation-policy.md)
- [Git / VCS ownership policy](docs/agent-vcs-ownership-policy.md)
- [Task review archive helper](docs/task-worktree-review-archive-helper.md)
- [Development baseline](docs/development-baseline.md)
- [Node.js toolchain](docs/node-toolchain.md)

### Architecture and product

- [Architecture overview](docs/architecture/overview.md)
- [Service boundaries](docs/architecture/services.md)
- [Inbound WhatsApp recovery and multi-basket runtime flow](docs/architecture/inbound-whatsapp-recovery-flow.md)
- [Runtime flows index](docs/architecture/runtime-flows.md)
- [Copilot model selection](docs/models/ARCH-002/copilot-model-selection.md)
- [ARCH-001: Shopify checkout recovery webhook processing](docs/architecture/ARCH-001-shopify-checkout-recovery-webhook-processing.md)
- [ARCH-002: Render test and production gateway and infrastructure](docs/architecture/ARCH-002-render-production-gateway-infrastructure.md)
- [ARCH-003: Admin operational queue observability UI](docs/architecture/ARCH-003-admin-operational-ui.md)
- [ARCH-004: Correlated cart activity recovery rescheduling](docs/architecture/ARCH-004-cart-activity-recovery-rescheduling.md)
- [ARCH-005: Global internationalisation and WhatsApp markets](docs/architecture/ARCH-005-global-internationalisation-whatsapp-markets.md)
- [ARCH-006: Merchant communications, support inbox and system notifications](docs/architecture/ARCH-006-merchant-communications-support-inbox.md)
- [Historical ARCH-007: Shopify billing, usage and cost control](docs/architecture/ARCH-007-shopify-billing-usage-cost-control.md)
- [ARCH-010: Merchant lifecycle state transitions and behavioural access](docs/architecture/ARCH-010-merchant-lifecycle-state-transitions.md)
- [ARCH-010 implementation handoff](docs/architecture/ARCH-010-implementation-handoff.md)
- [ARCH-010 billing/lifecycle supersession map](docs/architecture/ARCH-010-supersession-map.md)
- [Pricing and billing model](docs/product/pricing-and-billing-model.md)
- [Historical ARCH-007 implementation handoff](docs/architecture/ARCH-007-implementation-handoff.md)
