# WooCommerce Task Toolchain and Agent-Shell Bootstrap

## Purpose

Moda Interact WooCommerce repository tasks execute in the same deterministic
`/moda-task` worktree model as the existing Moda repositories, but their local
validation requires a broader host toolchain than Node alone.

The WooCommerce task bootstrap therefore separates:

- deterministic workspace/Node selection;
- verification of host PHP, Composer and Docker prerequisites; and
- repository-owned WordPress/WooCommerce runtime dependencies such as `wp-env`.

It does not install or silently replace host software.

## Launcher boundary

`scripts/start-agent-task.py --prepare` continues to own Git/task preparation:

```text
canonical workspace
    -> parent task worktree
    -> implementation task worktree
    -> branch synchronization
    -> recursive submodules
    -> dependency gate
    -> durable task claim
```

The launcher does **not** install PHP, Composer or Docker and does not start a
WordPress environment as part of task preparation.

For `WOOCOMMERCE` tasks, the launcher-rendered execution prompt instructs the
resolved `moda_woocommerce` agent to source:

```bash
source "$MODA_WORKSPACE_ROOT/scripts/bootstrap-woocommerce.sh"
```

before the first Node/PHP/Composer/Docker/`wp-env`-related command.

Other domains retain the existing lean Node bootstrap contract.

## Host prerequisites

WooCommerce task execution requires the developer/agent host to provide:

- PHP;
- Composer;
- Docker with a reachable daemon.

The script also invokes the canonical workspace Node bootstrap, so the Node/npm
version still comes exclusively from the workspace `.nvmrc`.

The Woo bootstrap MUST NOT:

- install PHP, Composer, Docker or Node;
- use Homebrew, apt, yum or another package manager automatically;
- search the wider filesystem for alternate tool installations;
- change the declared PHP compatibility policy of an implementation task;
- pull or select an arbitrary Node version outside `.nvmrc`;
- start or replace the developer's Docker runtime.

If a prerequisite is missing, the bootstrap reports that exact condition and
stops. The developer then fixes the host environment deliberately.

## Repository-controlled dependencies

The Woo implementation repository should pin project dependencies itself.
Examples include:

```text
package-lock.json
composer.lock
@wordpress/env
WooCommerce extension build tooling
WordPress/WooCommerce versions selected by .wp-env.json
```

Do not require a globally installed `wp-env`; invoke the repository-pinned tool
through the repository's declared npm script or `npx` as appropriate.

Host PHP/Composer/Docker presence is not a substitute for the task's own
compatibility matrix. A task that needs to validate several PHP or
WordPress/WooCommerce versions must define that matrix explicitly and should use
controlled containers/runtime configuration rather than silently switching the
host toolchain.

## Usage

After deterministic `/moda-task` preparation and before the first Woo toolchain
command:

```bash
source "$MODA_WORKSPACE_ROOT/scripts/bootstrap-woocommerce.sh"
```

Successful output records the resolved workspace, Node/npm, PHP, Composer and
Docker client versions and confirms that the Docker daemon is reachable.

The script exports:

```text
MODA_WORKSPACE_ROOT
MODA_NODE_VERSION
MODA_PHP_VERSION
MODA_COMPOSER_VERSION
MODA_DOCKER_VERSION
```

These values are diagnostic execution evidence. They do not replace repository
or architecture compatibility declarations.

## Failure semantics

A Woo task must not work around bootstrap failure by:

- manually editing `PATH` to guessed PHP/Composer/Docker locations;
- installing another runtime during repository-task execution;
- bypassing Composer because it is unavailable;
- replacing the repository's `wp-env` path with an ad-hoc local WordPress
  installation;
- claiming validation passed when Docker-backed runtime validation could not run.

If the task's required environment is unavailable after the bootstrap, record
the exact blocker in the Completion Report and return according to the task
protocol.
