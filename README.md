# Moda Interact Workspace

This repository is the top-level workspace for the **Moda Interact** platform.

It ties together the independently versioned Moda Interact services using Git submodules, so the workspace records which exact commit of each service belongs to a given platform version.

## Clone the complete workspace

Because this repository contains Git submodules, clone it recursively:

```bash
git clone --recurse-submodules \
  https://github.com/kodjobaah/moda-interact-workspace.git
```

Then enter the workspace:

```bash
cd moda-interact-workspace
```

If you already cloned the workspace without `--recurse-submodules`, initialise all submodules with:

```bash
git submodule update --init --recursive
```

The `--recursive` flag is important because some Moda Interact services also include `moda-interact-database` as a nested submodule.

## Workspace structure

The workspace root contains the Git metadata, the included workspace file, and the submodule directories for each service. After a normal recursive clone or `git submodule update --init --recursive`, each service directory is populated with its own repository checkout.

```text
moda-interact-workspace/
├── .codex/
│   └── agents/
├── .claude/
│   └── agents/
├── docs/
│   ├── agent-task-execution-template.md
│   ├── architecture/
│   ├── contracts/
│   └── decisions/
├── .gitignore
├── .gitmodules
├── README.md
├── sync_agents.py
├── moda-interact/
├── moda-interact-background/
├── moda-interact-database/
├── moda-interact-admin/
├── moda-interact-messaging/
├── moda-interact-site/
├── moda-interact-shared/
├── moda-interact.code-workspace
└── .git/
```

## Projects

| Project | Responsibility |
| --- | --- |
| [`moda-interact`](https://github.com/kodjobaah/moda-interact) | Shopify app, merchant UI, Shopify webhooks, onboarding, billing and subscription flows |
| [`moda-interact-background`](https://github.com/kodjobaah/moda-interact-background) | BullMQ workers, checkout recovery workflows, commerce agent, Shopify tools, entitlements and usage |
| [`moda-interact-database`](https://github.com/kodjobaah/moda-interact-database) | Shared Prisma schema, PostgreSQL migrations, seed data and ERD |
| `moda-interact-admin` | Next.js platform administration console for cross-merchant usage and operational visibility |
| [`moda-interact-messaging`](https://github.com/kodjobaah/moda-interact-messaging) | WhatsApp/Meta webhook ingress and queue publishing |
| [`moda-interact-site`](https://github.com/kodjobaah/moda-interact-site) | Public Moda Interact website and product-facing content |
| [`moda-interact-shared`](https://github.com/kodjobaah/moda-interact-shared) | Canonical shared TypeScript package (`@kodjobaah/moda-interact-shared`) for cross-service runtime contracts, validation schemas, event versions, deterministic identifiers and genuinely reusable code |

## High-level architecture

```text
                     Shopify
                        |
                        v
                 moda-interact
                        |
                        v
                  Redis / BullMQ
                        |
                        v
            moda-interact-background
                 /              \
                v                v
          PostgreSQL         Commerce Agent
                                  |
                           Shopify / AI tools

WhatsApp / Meta
      |
      v
moda-interact-messaging
      |
      +----------------------> Redis / BullMQ

Public website
      |
      v
moda-interact-site
```

`moda-interact-database` is the authoritative owner of the shared Prisma schema and migration history.

## Architecture documentation

The central architecture and cross-agent coordination state is maintained in [`docs/`](docs/).

Architecture work is organised around stable architecture initiative IDs:

```text
ARCH-001
ARCH-002
ARCH-003
...
```

An `ARCH-XXX` identifies one architectural initiative, not one implementation task.

Overall architecture documents live under:

```text
docs/architecture/
```

For example:

```text
docs/architecture/ARCH-001-shopify-webhook-reliability.md
```

Implementation tasks are decomposed by owning domain:

```text
docs/decisions/
├── admin/
├── background/
├── database/
├── messaging/
├── shared/
├── shopify/
└── site/
```

Each affected domain receives an `ARCH-XXX` directory containing its bounded tasks. For example:

```text
docs/decisions/
├── shared/
│   └── ARCH-001/
│       ├── _index.md
│       └── SHARED-001-define-shopify-event-contract.md
├── shopify/
│   └── ARCH-001/
│       ├── _index.md
│       └── SHOPIFY-001-persist-webhook.md
└── background/
    └── ARCH-001/
        ├── _index.md
        └── BACKGROUND-001-consume-shopify-event.md
```

The fully qualified task IDs are:

```text
ARCH-001-SHARED-001
ARCH-001-SHOPIFY-001
ARCH-001-BACKGROUND-001
```

The architecture document answers: **What are we building and how does the complete system fit together?**

The domain `_index.md` answers: **What work does this logical agent/domain own for this architecture?**

The individual task file answers: **What exactly must be implemented now?**

The individual task file is authoritative for task state. The parent architecture document is authoritative for overall architectural intent. The source code is authoritative for actual runtime behaviour.

The architect must reconcile these sources if they drift rather than silently allowing documentation and implementation to diverge.

## Why this workspace exists

Each service remains an independent Git repository with its own commit history and deployment lifecycle.

The workspace repository stores Gitlinks to specific service commits:

```text
moda-interact-workspace
├── moda-interact            @ <commit>
├── moda-interact-background @ <commit>
├── moda-interact-database   @ <commit>
├── moda-interact-messaging  @ <commit>
└── moda-interact-site       @ <commit>
```

This makes a workspace commit a reproducible snapshot of the complete platform.

## Working with a service

Each service in this workspace is a Git submodule.

A submodule is normally checked out at the exact commit recorded by the workspace. This means that after cloning the workspace or running `git submodule update`, a service can be in a **detached HEAD** state.

Before making changes inside a service, switch to the branch you intend to work on.

For example:

```bash
cd moda-interact-messaging

git status
git switch main
git pull --ff-only origin main
```

Then make, commit, and push the service changes normally:

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

The workspace will now show that the submodule points at a newer commit, for example:

```text
modified: moda-interact-messaging (new commits)
```

Record that new service commit in the workspace:

```bash
git add moda-interact-messaging
git commit -m "update messaging service"
git push
```

This two-level commit process is intentional:

```text
service repository
    |
    +--> commit and push the code change
             |
             v
workspace repository
    |
    +--> commit the new submodule pointer
```

The service repository owns the code change. The workspace repository records which version of that service belongs to the current platform snapshot.

## Codex and Claude agents

Workspace-level agents exist as logical Moda agent roles and can be executed through either Codex or Claude.

The logical roles are:

```text
moda_architect
├── moda_admin
├── moda_app
├── moda_background
├── moda_database
├── moda_messaging
├── moda_shared
└── moda_site
```

Codex definitions live under `.codex/agents/<name>.toml`. Claude definitions live under `.claude/agents/<name>.agent.md`. The two files represent the same logical role and should express the same repository ownership, architectural responsibilities and task protocol even though runtime-specific configuration may differ.

### Canonical agent definitions and sync

The Codex TOML files are the canonical authored definitions. Claude agent files are generated from them with:

```bash
python3 sync_agents.py
```

Run the command from the workspace root, where both `.codex/` and `.claude/` are present. The sync process copies the logical agent name, description and developer instructions into Claude agent Markdown while leaving Codex-only execution settings such as `sandbox_mode` out of the Claude definition.

After changing a Codex agent definition:

```text
.codex/agents/moda_background.toml
        |
        v
python3 sync_agents.py
        |
        v
.claude/agents/moda_background.agent.md
```

Do not manually allow the Claude and Codex definitions for one logical agent to develop different ownership or architecture rules.

### Agent responsibilities

- **`moda_architect`**: Owns cross-repository architecture, workload/scalability reasoning, service boundaries, architecture documents, task decomposition, dependency sequencing, agent handoff, implementation review and integrated verification.
- **`moda_admin`**: Owns the Next.js platform administration console, internal authentication, cross-merchant usage views, operational visibility and admin workflows.
- **`moda_app`**: Owns the Shopify application, authentication, merchant UI, Shopify webhook ingress, onboarding, billing, subscriptions and shop services.
- **`moda_background`**: Owns BullMQ workers, high-volume Shopify event inspection/filtering, checkout recovery, order processing, commerce-agent orchestration, Shopify tools, retries, entitlements and usage recording.
- **`moda_database`**: Owns the Prisma schema, PostgreSQL migrations, relationships, constraints, indexes, seed data, durable integrity and ERD generation.
- **`moda_messaging`**: Owns Meta/WhatsApp webhook verification, signature validation, event normalisation, messaging ingress, queue publication and fast webhook acknowledgement.
- **`moda_shared`**: Owns the canonical `@kodjobaah/moda-interact-shared` package for cross-service runtime contracts, validation schemas, event versions, deterministic identifiers, shared enums and genuinely reusable primitives.
- **`moda_site`**: Owns the public website, responsive UI, SEO, product positioning, documentation links and marketing-facing content.

Use a specialist agent for work contained within one repository. Use `moda_architect` when work changes repository boundaries, shared database models, cross-service contracts, queue payloads, webhook contracts, billing or entitlement semantics, migration order or deployment sequencing.

## Architecture execution workflow

Cross-repository architectural work follows a durable filesystem-based workflow. Agents must not rely on hidden Claude/Codex conversation state to coordinate implementation.

```text
User
  |
  v
moda_architect
  | inspect current code and discuss the design
  v
docs/architecture/ARCH-XXX-*.md
  | decompose architecture
  v
docs/decisions/<domain>/ARCH-XXX/<TASK>.md
  | task becomes ready when dependencies are complete
  v
repository agent
  | claim + implement + validate
  v
status: review
  |
  v
moda_architect
  |
  +--> Changes Requested --> same repository agent/task
  |
  +--> Accepted --> status: complete --> unblock dependants
                                      |
                                      v
                             integrated review
                                      |
                                      v
                          architecture: implemented
```

### Starting a repository agent

The standard kickoff template for architecture tasks is:

```text
docs/agent-task-execution-template.md
```

Use this template when handing an executable architecture task to either Codex
or Claude.

The template is parameterised with:

```text
<AGENT>
<ARCH_ID>
<TASK_ID>
<TASK_FILE>
```

For example:

```text
AGENT:
moda_background

ARCH_ID:
ARCH-001

TASK_ID:
ARCH-001-BACKGROUND-001

TASK_FILE:
docs/decisions/background/ARCH-001/BACKGROUND-001-consume-shopify-event.md
```

A completed kickoff prompt therefore starts conceptually as:

```text
You are acting as the logical moda_background agent for the Moda Interact
workspace.

Implement the following architectural task:

Architecture:
ARCH-001

Task:
ARCH-001-BACKGROUND-001

Task file:
docs/decisions/background/ARCH-001/BACKGROUND-001-consume-shopify-event.md
```

The remainder of `agent-task-execution-template.md` defines the standard
execution protocol and should normally be supplied unchanged.

The template requires the repository agent to:

```text
read task + architecture + dependencies
        |
        v
verify status: ready
        |
        v
claim task
        |
        v
status: in_progress
        |
        v
implement bounded scope
        |
        v
update Work Items / Acceptance Criteria / Validation
        |
        v
complete Completion Report
        |
        v
status: review
        |
        v
return to moda_architect
```

The template is execution-environment neutral except for the runtime claim:

```yaml
executor: codex
```

or:

```yaml
executor: claude
```

The logical owner remains the same in both environments. For example, both
Codex and Claude may execute a task whose task metadata contains:

```yaml
assigned_agent: moda_background
```

The kickoff template does not replace the task file. The task file remains the
authoritative source for:

- implementation scope;
- dependencies;
- interfaces/contracts;
- Work Items;
- Acceptance Criteria;
- Validation;
- Completion Report.

The kickoff template exists to make every invocation follow the same startup,
claiming, execution and return-to-architect protocol.

Do not copy architectural requirements into an ad-hoc conversational prompt and
allow that prompt to become a competing source of truth.

Prefer:

```text
agent-task-execution-template.md
        +
task identity
        +
task file
```

over writing a one-off implementation prompt.

### Task state and claiming

Task files use YAML frontmatter so agents can discover and resume work without conversation history. A typical task begins with metadata such as:

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

Supported task states are `pending`, `ready`, `in_progress`, `review`, `complete`, `blocked` and `superseded`. Repository agents may transition assigned work from `ready -> in_progress -> review` or `in_progress -> blocked`. Only `moda_architect` may accept a reviewed task and set `status: complete`.

Task discovery is not a claim. Before starting a `ready` task, an agent re-reads it and claims it by setting the execution metadata for the current runtime, for example:

```yaml
status: in_progress
executor: codex
claimed_at: 2026-08-28T15:30:00+01:00
attempt: 1
```

A claimed task must not be silently overwritten by another executor. If a task is stranded in `in_progress`, `moda_architect` reviews the repository and task state before returning it to `ready`.

Each task contains checkable Work Items, Acceptance Criteria and Validation, plus a Completion Report and Architect Review. The repository agent returns implementation with `status: review`; the architect then inspects the actual code and either accepts the work, requests changes within the same task, or blocks the task because a new architectural dependency has been discovered.

### Shared contract workflow

Cross-service runtime contracts have one canonical owner: `moda-interact-shared/`, published as `@kodjobaah/moda-interact-shared`.

Before a producer or consumer defines a queue payload, runtime event schema, schema-version constant, shared enum, deterministic event/job ID helper or other cross-service primitive, it must first check the shared package. If the canonical definition exists, use it instead of creating a local copy.

When a new shared contract is required, the architect should normally sequence the work as:

```text
ARCH-001-SHARED-001
Define canonical shared contract
        |
        +--------------------------+
        |                          |
        v                          v
ARCH-001-SHOPIFY-001      ARCH-001-BACKGROUND-001
producer imports it       consumer imports it
```

Producer and consumer tasks should depend on the shared-contract task rather than independently inventing matching types. For a shared contract, the architecture should identify the contract owner, package/export name, producer repositories, consumer repositories, runtime validation schema, schema version and compatibility/rollout requirements. The architect reviews producer and consumer implementations to ensure they import the canonical contract and have not introduced duplicate local definitions.

## Platform workload and scalability model

Moda Interact is a multi-tenant event-driven platform. "Scale" is not treated as one generic number.

The reference Shopify ingress workload used for architecture analysis is approximately **20,000 Shopify events per minute** unless an architecture initiative defines another target. This is raw event ingress, not 20,000 recoveries, WhatsApp messages or LLM calls per minute.

```text
Shopify event ingress
        |
        v
thin authenticated ingress
        |
        v
Redis / BullMQ or another architecture-defined durable acceptance point
        |
        v
background event inspection/filtering
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

`moda-interact` should keep Shopify webhook ingress lightweight and acknowledge Shopify quickly after reaching the architecture's defined durable acceptance point. It must not discard an authenticated business event merely because the event looks immediately uninteresting when its relevance depends on evolving order, checkout, recovery, customer, conversation or previous-event state. Most business significance filtering belongs in `moda-interact-background`.

When reasoning about scalability, distinguish Shopify webhook events received, events queued, events inspected, events discarded, durable business-state transitions, CheckoutRecovery workflows, Redis/BullMQ queue depth and queue lag, PostgreSQL queries/writes, WhatsApp messages, CommerceAgent turns, LLM requests, Shopify Admin API requests and Meta API requests. Queue lag and oldest-event age are primary signals for whether asynchronous processing is keeping up.

For capacity claims, distinguish measured results from estimates and assumptions. Do not describe an assumed or estimated throughput as measured capacity.

## Updating submodules

Fetch the commits referenced by the workspace:

```bash
git submodule update --init --recursive
```

To fetch newer remote commits for configured submodule branches:

```bash
git submodule update --remote --recursive
```

Review changes before committing updated submodule pointers to the workspace.


## Detached HEAD and submodules

Seeing `HEAD detached at <commit>` inside a service is normal after a recursive clone or `git submodule update`.

The workspace records a commit SHA for each service, not a branch. Git therefore checks out that exact commit.

Before starting new work in a service, use:

```bash
git switch main
git pull --ff-only origin main
```

If you accidentally make commits while detached, do **not** discard them. Recover them with the reflog:

```bash
git reflog --oneline
```

Then either cherry-pick the detached commit onto `main`:

```bash
git switch main
git cherry-pick <detached-commit-sha>
git push
```

or preserve a longer detached series on a temporary branch first:

```bash
git switch -c recover-work <latest-detached-commit-sha>
git switch main
git merge recover-work
git push
```

After pushing the recovered service commit, return to the workspace root and update the submodule pointer:

```bash
cd ..
git add <service-directory>
git commit -m "update <service-name>"
git push
```


## Checking submodule status

```bash
git submodule status --recursive
```

## Database submodule

`moda-interact-database` is also consumed as a nested submodule by services that need the shared Prisma schema.

That means the same database repository can appear in multiple paths:

```text
moda-interact-database/
moda-interact/database/
moda-interact-background/database/
```

These are separate Git submodule checkouts and can theoretically point to different commits.

When making a database change, keep dependent service pointers aligned intentionally.

A typical database change flow is:

```text
1. Change, test, commit, and push moda-interact-database
2. Update the nested database submodule in every affected service
3. Test, commit, and push each affected service
4. Return to the workspace root
5. Update the top-level service and database submodule pointers
6. Commit and push the workspace snapshot
```

For example, after pushing a new database commit:

```bash
# Update the database checkout used by moda-interact
cd moda-interact/database
git fetch origin
git switch main
git pull --ff-only origin main

cd ..
git add database
git commit -m "update shared database schema"
git push
```

Repeat that for each service that consumes the new schema.

Then, from the workspace root, record the compatible platform versions:

```bash
git add   moda-interact-database   moda-interact   moda-interact-background   moda-interact-messaging

git commit -m "update platform database dependencies"
git push
```

Only include services that actually changed.

The top-level `moda-interact-database/` checkout and nested `database/` submodules are independent Git checkouts. Keep their commit pointers aligned intentionally when they are meant to consume the same schema version.

## VS Code

Open the included workspace with:

```bash
code moda-interact.code-workspace
```

## Useful commands

```bash
# Clone everything
git clone --recurse-submodules \
  https://github.com/kodjobaah/moda-interact-workspace.git

# Initialise missing submodules
git submodule update --init --recursive

# Show all submodule commits
git submodule status --recursive

# Open the VS Code workspace
code moda-interact.code-workspace

# Regenerate Claude agent definitions from canonical Codex TOML files
python3 sync_agents.py

# View the standard repository-agent kickoff template
cat docs/agent-task-execution-template.md
```

## Development principle

The workspace coordinates the platform but does not replace the independent ownership of each service.

- Shopify-facing concerns belong in `moda-interact`.
- Long-running, retryable and state-correlating workflows belong in `moda-interact-background`.
- Shared data models and migrations belong in `moda-interact-database`.
- Messaging provider ingress belongs in `moda-interact-messaging`.
- Canonical cross-service runtime contracts belong in `moda-interact-shared` and should be consumed through `@kodjobaah/moda-interact-shared`.
- Platform administration and cross-merchant operational views belong in `moda-interact-admin`.
- Public product and marketing content belongs in `moda-interact-site`.
- Cross-repository architecture, sequencing and implementation review belong to `moda_architect`.

The workspace records how those independently deployed parts fit together and provides the durable architecture/task state used by Codex and Claude agents.
