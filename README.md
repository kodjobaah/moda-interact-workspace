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
├── .claude/
│   └── agents/
├── .gitignore
├── .gitmodules
├── README.md
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
| [`moda-interact-shared`](https://github.com/kodjobaah/moda-interact-shared) | Shared TypeScript package (`@kodjobaah/moda-interact-shared`) for code common to multiple services |

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

The central architecture documentation is maintained in [`docs/`](docs/).

- [Architecture overview](docs/architecture/overview.md)
- [Service boundaries](docs/architecture/services.md)
- [Architecture decisions](docs/decisions/)

The workspace README explains how to work with the repositories and submodules;
the architecture documentation explains how the platform behaves and where each
responsibility belongs.

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

Workspace-level agents are authored for both Codex and Claude. The same agent
definitions are maintained in parallel under two locations:

```text
.codex/agents/<name>.toml
.claude/agents/<name>.agent.md
```

Each `.agent.md` file wraps the same underlying configuration as its `.toml`
counterpart (Markdown with frontmatter around the TOML body). Both locations
are actively used — which one applies depends on which tool (Codex or Claude)
is handling a given task — so changes to an agent's instructions should be
applied to both files to keep them in sync.

The intended model is:

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

The repository agents focus on their own service boundaries, while `moda_architect` handles cross-repository design and coordination.

Agent responsibilities:

- **`moda_architect`**: Coordinates cross-repository design, ownership decisions,
      integration contracts, migration planning and deployment sequencing.
- **`moda_admin`**: Owns the Next.js platform administration console, internal
      authentication, cross-merchant usage views, operational visibility and
      admin workflows.
- **`moda_app`**: Owns the Shopify application, authentication, merchant UI,
      Shopify webhooks, onboarding, billing, subscriptions and shop services.
- **`moda_background`**: Owns BullMQ workers, checkout recovery, order
      processing, commerce-agent orchestration, Shopify tools, entitlements,
      retries and usage recording.
- **`moda_database`**: Owns the Prisma schema, PostgreSQL migrations,
      relationships, constraints, indexes, seed data and ERD generation.
- **`moda_messaging`**: Owns Meta/WhatsApp webhook verification, signature
      validation, event normalisation, Redis/BullMQ publishing and fast webhook
      acknowledgement.
- **`moda_shared`**: Owns the `@kodjobaah/moda-interact-shared` package —
      code intended to be reused across multiple Moda Interact services.
- **`moda_site`**: Owns the public website, responsive UI, SEO, product
      positioning, documentation links and marketing-facing content.

Use a specialist agent for changes contained within one repository. Use
`moda_architect` when a change affects shared database models, queue payloads,
webhook contracts, billing and entitlement behavior, environment variables or
deployment order.

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
```

## Development principle

The workspace coordinates the platform but does not replace the independent ownership of each service.

- Shopify-facing concerns belong in `moda-interact`.
- Long-running and retryable workflows belong in `moda-interact-background`.
- Shared data models and migrations belong in `moda-interact-database`.
- Messaging provider ingress belongs in `moda-interact-messaging`.
- Public product and marketing content belongs in `moda-interact-site`.

The workspace records how those independently deployed parts fit together.
