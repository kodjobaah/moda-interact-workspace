# Node.js Toolchain and Agent-Shell Bootstrap

## Purpose

Moda Interact needs one predictable Node.js development toolchain across a
multi-repository workspace while avoiding a concrete Node version being copied
into agent definitions, helper scripts and documentation.

The design deliberately separates **version selection** from **environment
bootstrap**.

## Source of truth

The workspace root `.nvmrc` selects the Node.js version used by developers and
coding-agent shells.

Example:

```text
24.19.0
```

The value may change over time. No bootstrap script or agent definition should
need modification solely because the selected Node version changes.

## Bootstrap contract

Every fresh shell that needs Node-related tooling should run:

```bash
source scripts/bootstrap-node.sh
```

The script discovers the Moda Interact workspace root by walking upward until it
finds both `.nvmrc` and `.codex/agents/`. This means it can be sourced from the
workspace root or from inside a service submodule.

It then:

1. reads the workspace `.nvmrc`;
2. loads `$HOME/.nvm/nvm.sh` if NVM is not already active;
3. asks NVM to select the `.nvmrc` version;
4. falls back to the matching already-installed NVM directory only when NVM
   shell integration cannot be loaded and `.nvmrc` contains an exact version;
5. verifies `node` and `npm`;
6. reports the resolved tool paths and versions.

The bootstrap does **not** install Node automatically. Missing runtime
installation is a distinct condition that should be fixed deliberately with
`nvm install`.

## Why agents need this

Codex and Claude may execute shell commands in non-interactive sessions. Those
sessions do not necessarily run `.zshrc`, `.bashrc`, or the developer's normal
NVM initialisation.

Therefore:

```text
node not found
```

before bootstrap means only:

```text
Node is not currently on this shell's PATH
```

It does not establish that Node is not installed.

Agents must run the workspace bootstrap before searching the filesystem,
installing Node or declaring the toolchain unavailable.

## Agent definitions

Codex TOMLs are canonical. Their Node rule is intentionally version-independent:

```text
source scripts/bootstrap-node.sh
```

Install/update the rule with:

```bash
python3 scripts/apply-node-agent-policy.py
```

Then regenerate Claude definitions:

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

When moving to a new Node version:

1. change `.nvmrc`;
2. run `nvm install` and `nvm use`;
3. source `scripts/bootstrap-node.sh`;
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
exception to an agent. At that point the bootstrap can be extended to support
service-local version selection while retaining the workspace default.
