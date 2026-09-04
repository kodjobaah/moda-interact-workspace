# Agent Validation Execution Policy

## Purpose

Moda agents should validate their work without spending model usage merely
babysitting deterministic long-running infrastructure/test commands.

This policy separates:

```text
AGENT-EXECUTED VALIDATION
```

from:

```text
DEVELOPER-EXECUTED VALIDATION
```

The distinction is about **who launches and waits for the command**, not whether
the validation matters.

Long-running validation remains required where the task requires it.

## Core Rule

Repository agents own:

```text
implementation
fast feedback validation
clear handoff of expensive deterministic validation
accurate reporting
```

The developer normally owns execution of expensive deterministic integration,
system and live-environment validation.

The architect owns acceptance of the resulting evidence.

Use this lifecycle by default:

```text
agent claim
    ->
implement
    ->
run fast/cheap validation
    ->
return task to review with exact developer-validation command(s)
    ->
developer executes long validation
    ->
developer supplies command/result/exit code
    ->
architect reviews code + evidence
```

Do not use a reasoning agent simply as a timer or terminal babysitter.

## Agent-Executed Validation

Agents should normally run validation that is fast, deterministic and directly
useful as an implementation feedback loop.

Examples include:

```text
shell syntax checks
TypeScript compilation where bounded
lint where bounded
format/static checks
targeted unit tests
small repository-local tests
configuration/schema validators
Blueprint validators
HAProxy/NGINX config parsing when it does not require long orchestration
git diff --check
targeted grep/static regression checks
```

A repository task may identify additional cheap checks.

Agents should run these before returning work to review unless the environment
cannot support them.

## Developer-Executed Validation

Unless the developer or architect explicitly requests autonomous execution for
the specific task, repository agents MUST NOT launch or wait on validation in
these classes:

```text
multi-container Docker integration suites
architecture/system-test suites
load/performance/stress tests
live Render/environment validation
deployment smoke tests
tests that create substantial external infrastructure
long migration/integration rehearsals
commands known to take several minutes primarily waiting on deterministic tools
```

Examples in the gateway repository include:

```text
bash tests/run-tests.sh
```

when it builds Docker images and orchestrates multiple fixture/gateway
containers.

The test remains required; the developer normally executes it.

## Explicit Override

The developer or `moda_architect` may explicitly authorise the agent to run a
long validation command for a specific task.

When explicitly authorised:

```text
run it once;
wait for the command normally;
do not repeatedly poll/relaunch it without new evidence;
do not retry blindly;
do not read huge logs repeatedly;
stop and report a genuine hang/environment problem.
```

Explicit authorisation for one command/task does not permanently change this
policy.

## Task Validation Sections

A task specification may contain validation commands written before this policy
was adopted.

If a task says an agent must run a long Docker/system/live validation command,
but the developer has not explicitly requested agent-side execution, treat that
as coordination drift.

Do not silently omit the validation.

Instead report:

```text
Developer validation required:
  <exact command>

Reason:
  long-running deterministic integration/system/live validation
```

Run the fast checks yourself and return the task to `review`.

## Completion Report

When long validation is developer-owned, the Completion Report must distinguish:

```text
Agent-executed validation:
  command
  result

Developer validation required:
  exact command
  expected success condition
```

Do not claim the developer-owned validation passed until evidence is provided.

The task may still move:

```text
in_progress -> review
```

because `review` is the coordination boundary at which developer validation and
architect inspection can occur.

Do not mark the task `complete`.

## Accepting Developer Validation Evidence

If the developer supplies clear evidence such as:

```text
command:
  bash tests/run-tests.sh

summary:
  52 passed, 0 failed

exit:
  0
```

the agent/architect may use that as validation evidence.

Do not rerun the same expensive command merely because the model did not launch
it.

Rerun is appropriate only when:

```text
relevant implementation changed after that validation;
the evidence is incomplete/contradictory;
the command tested a different revision/configuration;
the architect explicitly requests a rerun.
```

## Failure Evidence

Developer-executed tests are first-class diagnostic evidence.

If the developer supplies failures:

```text
inspect the relevant implementation/test code;
identify the smallest cause;
do not reflexively rerun the whole expensive suite;
prefer a focused cheap diagnostic where possible.
```

After a correction that materially affects the failed behavior, request a
developer rerun of the relevant long suite.

## Interrupted Runs

Integration suites must be written so an interrupted previous run does not
contaminate a later run.

Where tests create local infrastructure:

```text
use run-scoped resource/container names;
install cleanup traps;
make setup fail fast;
avoid fixed global names;
make cleanup target only the current run's resources.
```

This is a test-quality requirement independent of who executes the suite.

## Model-Usage Principle

Model reasoning is valuable for:

```text
design
implementation
debugging
review
interpreting validation evidence
```

It is not valuable merely for waiting while Docker, a compiler, a load
generator or an external deployment performs deterministic work.

Prefer human/developer execution for long deterministic validation when the
developer is actively supervising the workflow.

## Scope

This policy is intended to be the workspace-wide default for repository agents.

Agent-specific instructions and task-specific architecture requirements remain
authoritative for:

```text
what must be validated
what counts as success
repository ownership
security restrictions
```

This policy determines the default **execution owner** for expensive validation.

An explicit developer/architect instruction for a specific command overrides
the execution-owner default.

## Hard Stop for Developer-Owned Validation

When a command is classified as developer-executed validation, repository agents
must not try to make that command run on the developer's behalf.

Without an explicit developer/architect request for the specific run, do not:

```text
launch the long validation;
inspect which local process/container owns a required host port;
run docker ps/lsof/netstat solely to unblock the long validation;
remove or stop unrelated/stale developer containers;
select alternate ports and retry;
relaunch after an environment collision;
poll a long-running validation repeatedly;
re-read large validation logs while waiting.
```

If a developer-owned validation command was accidentally started and fails due
to local environment state:

```text
capture the concise failure;
do not troubleshoot the developer host;
do not retry;
continue with bounded implementation/static validation;
return to review with the exact developer command.
```

The repository agent may, of course, fix a **test-harness defect** revealed by
the failure when that defect is in task scope. It should prove the correction
with cheap/static checks and then hand the long suite back to the developer.
