# Node.js Toolchain and Agent-Shell Bootstrap

## Purpose

Moda Interact needs one predictable Node.js development toolchain across a
multi-repository workspace while avoiding a concrete Node version being copied
into agent definitions, helper commands and active documentation.

The design deliberately separates **version selection**, **workspace path
anchoring**, and **environment recovery**.

## Source of truth

The workspace root `.nvmrc` is the single source of truth for the Node.js
version selected for developer and coding-agent work.

The selected value may change over time. Agent definitions and bootstrap
instructions must remain version-independent.

## Workspace root contract

Agent tasks are expected to start from the `moda-interact-workspace` root.
Before changing directories, verify and anchor that root without invoking Node:

```bash
test -f .nvmrc && test -d .codex/agents
export MODA_WORKSPACE_ROOT="$PWD"
```

If this check fails, stop and report the unexpected working directory. Do not
search the filesystem for the project and do not reconstruct a user-specific
absolute workspace path.

Use workspace-relative repository navigation from the root:

```bash
cd moda-interact
cd moda-interact-shared
```

Return to the verified root with:

```bash
cd "$MODA_WORKSPACE_ROOT"
```

## Lean bootstrap contract

Do not bootstrap Node merely because a task has started.

Before the first Node-related command in a shell, check the environment already
provided:

```bash
command -v node >/dev/null 2>&1
```

If Node is available, continue directly.

If Node is missing, recover the workspace toolchain once through:

```bash
source "$MODA_WORKSPACE_ROOT/scripts/bootstrap-node.sh"
```

The bootstrap reads the workspace `.nvmrc`, loads NVM where needed, selects the
configured version, verifies the toolchain and exports/refreshes the workspace
root anchor as supported by the script.

The bootstrap does **not** install Node automatically. If the selected `.nvmrc`
version is not installed, that is a distinct condition that should be reported
and fixed deliberately.

## Node recovery ownership

`scripts/bootstrap-node.sh` exclusively owns Node/NVM recovery for coding-agent
shells.

An agent must not manually:

- export `$HOME/.nvm/versions/node/.../bin` or another inferred Node directory
  into `PATH`;
- call `nvm use` as a substitute for the workspace bootstrap;
- infer, copy or hardcode the `.nvmrc` version into a command;
- search `/usr/local/bin`, `/opt/homebrew/bin`, `$HOME/.nvm` or the wider
  filesystem for Node;
- install, replace or silently select a different Node version because Node is
  initially absent from `PATH`.

If bootstrap fails, report the bootstrap failure rather than creating an
alternative environment setup.

## Why agents need this

Codex and Claude may execute shell commands in non-interactive sessions. Those
sessions do not necessarily run `.zshrc`, `.bashrc`, or the developer's normal
NVM initialisation.

Therefore `node not found` before bootstrap means only that Node is not currently
on that shell's `PATH`; it does not establish that Node is not installed.

## Workspace doctor is on demand

The workspace doctor is diagnostic/validation tooling, not mandatory startup.
Do not run it merely because a task begins.

Use it when an actual environment/dependency issue is observed, relevant
Node/dependency/configuration state changes, the task Validation section requires
it, or `moda_architect` explicitly requests it:

```bash
"$MODA_WORKSPACE_ROOT/scripts/workspace-doctor.sh" --quick
"$MODA_WORKSPACE_ROOT/scripts/workspace-doctor.sh" --production
"$MODA_WORKSPACE_ROOT/scripts/workspace-doctor.sh" --full
```

Likewise, `docs/development-baseline.md` is read when environment/dependency
investigation makes it relevant, not as a ritual on every task.

## Agent definitions

Codex TOMLs are canonical. Their Node rule is intentionally version-independent
and implements the lean sequence:

```text
need Node-related tooling
        |
        v
command -v node
        |
   +----+----+
   |         |
found      missing
   |         |
continue   source workspace bootstrap
```

After changing canonical Codex definitions, regenerate Claude definitions with:

```bash
python3 sync_agents.py
```

Changing `.nvmrc` therefore does not require editing every agent.

## Version responsibilities

Three related mechanisms have different jobs:

| Mechanism | Responsibility |
| --- | --- |
| `.nvmrc` | Select the workspace development/agent Node version |
| `package.json` `engines.node` | Declare the Node versions a package/service supports |
| Render/Docker/runtime configuration | Select and validate the deployed runtime |

They should be compatible, but they should not be conflated.

## Node upgrade procedure

When deliberately moving to a new Node version:

1. change `.nvmrc`;
2. install/select that version in the developer environment as part of the
   deliberate toolchain change;
3. validate through `scripts/bootstrap-node.sh`;
4. inspect affected `package.json` `engines.node` constraints;
5. run tests/typecheck/build for every affected service;
6. validate Docker/Render runtime compatibility;
7. update service/runtime declarations only where required;
8. commit the `.nvmrc` change together with any compatibility changes.

Do not update agent TOMLs merely because the version number changed.

## Future extension

The current platform intentionally uses one workspace-selected development Node
version.

If a future service genuinely requires an independent Node major version, treat
that as a deliberate toolchain architecture change rather than adding a hidden
exception to an agent. At that point the bootstrap can be extended while
retaining the workspace default.
