# Moda implementation repository provisioning

Use repository provisioning when the workspace needs a new implementation
repository before normal `/moda-task` execution can create an implementation
worktree.

The deterministic entry point is:

```text
scripts/provision-moda-repository.py
```

The user-facing skill is:

```text
/moda_provision_repository
```

Repository provisioning is repository-centric. An architecture task is optional
verification context, not the identity of the repository being provisioned.

## Example

Validate without changing state:

```bash
python3 scripts/provision-moda-repository.py \
  moda-interact-woocommerce \
  --remote https://github.com/kodjobaah/moda-interact-woocommerce.git \
  --dry-run \
  --json
```

The dry-run is intentionally usable when unrelated workspace files/submodules are
dirty. It reports the dirty state and any blockers that would prevent a real run,
but does not create a remote, add a submodule, commit, or push.

Optionally verify the repository against an architecture task route:

```bash
python3 scripts/provision-moda-repository.py \
  moda-interact-woocommerce \
  --remote https://github.com/kodjobaah/moda-interact-woocommerce.git \
  --task ARCH-026-WOOCOMMERCE-001 \
  --dry-run \
  --json
```

Create the private GitHub repository when it does not yet exist and register it:

```bash
python3 scripts/provision-moda-repository.py \
  moda-interact-woocommerce \
  --remote https://github.com/kodjobaah/moda-interact-woocommerce.git \
  --create-private \
  --description "Moda Interact WooCommerce WordPress extension" \
  --json
```

`--create-private` is always explicit. The script never derives or invents the
remote URL.

## Canonical workspace preconditions

Both dry-run and real execution require the script to be running from the
canonical primary workspace infrastructure and require:

```text
branch: main
HEAD: exactly the remote origin/main SHA
```

A dry-run may have arbitrary dirty/staged workspace files; they are reported.

A **real** provisioning run additionally requires:

```text
pre-existing staged paths: none
.gitmodules: clean
```

Unrelated **unstaged** changes are allowed. This matters when existing submodules
have local work in progress: provisioning does not stage, reset or commit those
changes.

Before committing, the script verifies that the staged path set is exactly:

```text
.gitmodules
<new implementation repository gitlink>
```

After committing/pushing, it verifies the pre-existing unrelated workspace status
is unchanged.

For an existing implementation remote, the remote must already have:

```text
default branch: main
at least one commit on main
```

For a missing GitHub remote, `--create-private` uses the authenticated `gh` CLI
to create a private repository with an initial README commit. The flag is never
implicit.

## Workspace result

A new provisioning operation changes/commits only:

```text
.gitmodules
<implementation-repository gitlink>
```

The gitlink uses Git mode `160000` and is pinned to the validated remote `main`
commit. The script pushes the resulting workspace provisioning commit to
`origin/main`.

It does not scaffold application source.

## Optional task verification

Supplying:

```text
--task ARCH-XXX-DOMAIN-NNN
```

causes the script to call:

```text
scripts/start-agent-task.py --route-only --json
```

and verify that the materialized task expects the same implementation repository.
The task is not used to infer the repository or remote.

Repository provisioning does not claim, execute or change the state of the task.

Typical architecture lifecycle:

```text
architect materializes pending repository task
        |
        v
/moda_provision_repository <repository> --task <task>
        |
        v
remote repository + workspace submodule exist
        |
        v
provisioning evidence returned
        |
        v
moda_architect records evidence / verifies readiness
        |
        v
pending -> ready
        |
        v
/moda-task
```

Provisioning may also be used without a task when establishing repository
infrastructure before task authoring.

## Existing/partial registration

The script is intentionally conservative.

A correctly registered submodule at the current remote `main` SHA is treated as
already provisioned and produces evidence without another commit.

A partial or conflicting registration stops. The script does not silently:

- repoint remotes;
- rewrite an existing submodule registration;
- update an existing gitlink;
- delete directories;
- deinitialize submodules;
- reset unrelated workspace changes;
- stage unrelated files;
- reset workspace history.
