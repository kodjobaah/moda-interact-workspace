---
name: moda-task
description: Launch a Moda Interact architecture task by task ID.
invokable: true
---

You begin in a task-launcher phase. Do not claim, implement, modify task state
or perform architect review until the deterministic resolver has routed the task
and the resolved repository-agent protocol has verified eligibility.

A successful resolver response ends the launcher phase but does **not** end the
`/moda-task` invocation. Continue in the same context as the resolved logical
agent unless the runtime provides and uses a supported named-agent handoff.

Extract exactly one fully qualified Moda Interact task ID from the invocation, for example `ARCH-002-SHOPIFY-001`.

## Mandatory first action

Resolve the workspace root only from an existing `MODA_WORKSPACE_ROOT` or the current directory's parent chain, then invoke:

```bash
TASK_ID="<TASK_ID>"
ROOT="${MODA_WORKSPACE_ROOT:-}"

if [ -z "$ROOT" ]; then
  CANDIDATE="$PWD"
  while [ "$CANDIDATE" != "/" ]; do
    if [ -f "$CANDIDATE/.nvmrc" ] &&
       [ -f "$CANDIDATE/scripts/start-agent-task.py" ] &&
       [ -f "$CANDIDATE/docs/agent-task-execution-template.md" ]; then
      ROOT="$CANDIDATE"
      break
    fi
    CANDIDATE="$(dirname "$CANDIDATE")"
  done
fi

if [ -z "$ROOT" ] ||
   [ ! -f "$ROOT/scripts/start-agent-task.py" ] ||
   [ ! -f "$ROOT/docs/agent-task-execution-template.md" ]; then
  echo "MODA_TASK_ERROR: unable to resolve Moda Interact workspace root" >&2
  exit 64
fi

export MODA_WORKSPACE_ROOT="$ROOT"
python3 "$MODA_WORKSPACE_ROOT/scripts/start-agent-task.py" "$TASK_ID" --json
```

Do not search the wider filesystem or rediscover architecture/domain/agent/repository values that the resolver returns.

The resolver output is authoritative for the task file, architecture, logical
agent, repository, current task status and rendered execution prompt.

After successful resolution, immediately adopt the rendered prompt unchanged and
follow the resolved logical agent definition. Do not return a final response
merely summarising the resolver result or saying that no claim/implementation
was performed.

## Eligibility rule

Before inspecting implementation source or claiming the task, verify only the authoritative current-task gate:

```text
status: ready
assigned_agent: <resolved agent>
all tasks explicitly listed in depends_on: complete
```

Dependency gating is metadata-first and limited to the current task's explicit `depends_on` list.

Do **not** infer extra dependency gates from the parent architecture, domain indexes, `enables` lists, sibling tasks, transitive references, historical notes, or superseded task records.

A task marked `superseded` elsewhere does not block the current task merely because it is mentioned. It matters only when it is still explicitly listed in the current task's `depends_on`, or when the current task's own scope directly duplicates the superseded capability. In those cases, report the exact coordination/scope conflict to `moda_architect` and stop.

Do not stop solely because an unrelated or historical task is marked `superseded`.

After eligibility is verified, claim and execute the task according to the resolved repository-agent protocol, validate it, move it to `review`, and return control to `moda_architect`.


## Successful-resolution continuation rule

When the resolver succeeds:

```text
resolver
  -> resolved logical agent
  -> explicit eligibility verification
  -> claim
  -> implement
  -> validate
  -> review
```

Stop before claiming only when:

- resolver/workspace resolution failed;
- the task is not Ready;
- an explicit `depends_on` task is not Complete;
- there is a concrete scope/ownership conflict; or
- the runtime genuinely cannot perform logical-agent handoff/adoption.

Successful routing to `status: ready` is not itself a stopping condition.


## Git / VCS ownership

Read and obey `docs/agent-vcs-ownership-policy.md`.

The resolved repository agent must leave implementation changes uncommitted and
unpushed unless the developer explicitly grants one-off permission for the
specific task.

The normal terminal state is:

```text
task -> review
agent -> STOP
developer -> commit/push after architect review
```

Do not treat stale "commit/push required" wording as permission or as a blocker.
