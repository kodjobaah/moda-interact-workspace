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
├── .gitignore
├── .gitmodules
├── README.md
├── moda-interact/
├── moda-interact-background/
├── moda-interact-database/
├── moda-interact-messaging/
├── moda-interact-site/
├── moda-interact.code-workspace
└── .git/
```

## Projects

| Project | Responsibility |
| --- | --- |
| [`moda-interact`](https://github.com/kodjobaah/moda-interact) | Shopify app, merchant UI, Shopify webhooks, onboarding, billing and subscription flows |
| [`moda-interact-background`](https://github.com/kodjobaah/moda-interact-background) | BullMQ workers, checkout recovery workflows, commerce agent, Shopify tools, entitlements and usage |
| [`moda-interact-database`](https://github.com/kodjobaah/moda-interact-database) | Shared Prisma schema, PostgreSQL migrations, seed data and ERD |
| [`moda-interact-messaging`](https://github.com/kodjobaah/moda-interact-messaging) | WhatsApp/Meta webhook ingress and queue publishing |
| [`moda-interact-site`](https://github.com/kodjobaah/moda-interact-site) | Public Moda Interact website and product-facing content |

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

Enter a service normally:

```bash
cd moda-interact-messaging
```

Make and push changes in that repository:

```bash
git add .
git commit -m "describe the change"
git push
```

Then return to the workspace root:

```bash
cd ..
git status
```

The workspace will show the service as having a new submodule commit, for example:

```text
modified: moda-interact-messaging (new commits)
```

Record the updated service version in the workspace:

```bash
git add moda-interact-messaging
git commit -m "update messaging service"
git push
```

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
1. Change and commit moda-interact-database
2. Update the database submodule in affected services
3. Test and commit each affected service
4. Update the corresponding service pointers in this workspace
5. Commit the workspace snapshot
```

## VS Code

Open the included workspace with:

```bash
code moda-interact.code-workspace
```

## Codex agents

Workspace-level Codex agents live under:

```text
.codex/agents/
```

The intended model is:

```text
moda_architect
├── moda_app
├── moda_background
├── moda_database
├── moda_messaging
└── moda_site
```

The repository agents focus on their own service boundaries, while `moda_architect` handles cross-repository design and coordination.

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
```

## Development principle

The workspace coordinates the platform but does not replace the independent ownership of each service.

- Shopify-facing concerns belong in `moda-interact`.
- Long-running and retryable workflows belong in `moda-interact-background`.
- Shared data models and migrations belong in `moda-interact-database`.
- Messaging provider ingress belongs in `moda-interact-messaging`.
- Public product and marketing content belongs in `moda-interact-site`.

The workspace records how those independently deployed parts fit together.
