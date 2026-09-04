# Agent Live Validation Execution Policy

## Purpose

This policy separates:

```text
agent-owned local/deterministic validation
```

from:

```text
developer-owned validation against deployed/shared environments
```

The distinction is based on **where the command executes against**, not how long
it takes.

```text
fast/bounded != agent-owned
```

## Agent-owned validation

Agents may normally execute bounded checks that stay local to the workspace or
use local/mocked fixtures:

```text
unit tests
local deterministic integration tests
syntax/config parsing
typecheck
lint
static Blueprint/config validation
git diff --check
```

## Developer-owned live validation

Without explicit current authorization for the exact command, an agent MUST NOT
execute a command that contacts a deployed/shared environment, including:

```text
Render services
public custom domains
Shopify test/development endpoints
Meta/WhatsApp deployed endpoints
managed/shared databases or queues
other remote test/staging/production services
```

This remains true even if the command:

```text
takes seconds
is described as bounded
is read-only
has all required environment variables
has secrets already present in the shell
appears in historical task validation instructions
```

For the reusable Render test deployment validator, developer-owned commands
include:

```bash
npm run validate:render:test
node scripts/validate-render-deployment.js --environment test
./scripts/validate-render-test.sh

./scripts/developer-validation.sh \
  ARCH-002-SYSTEM-TEST-006 \
  -- ./scripts/validate-render-test.sh
```

During migration, the old names remain developer-owned as well:

```bash
npm run validate:arch002-render-test
node scripts/run-arch002-render-test-topology.js
./scripts/system-test-006-developer-validation.sh
```

## Secret boundary

An agent MUST NOT inspect or enumerate live secret values merely to decide
whether the live validator can run.

The agent may validate:

```text
required environment-variable names
fail-closed handling
local signing helpers
redaction behavior using synthetic values
```

The agent must not:

```text
print real secret values
dump live credential-bearing environment state
decide to launch a remote probe because secrets happen to exist
fill one missing host/input and then launch the remote validator
```

## Workflow

```text
agent implements/fixes validator
        |
        v
agent runs local/static checks
        |
        v
task -> review
        |
        v
developer runs live validator
        |
     +--+--+
     |     |
    PASS  FAIL/BLOCKED
     |     |
     v     v
report   report + full.log + matching workspace ZIP
to agent             |
     |               v
     v          moda_architect
record evidence
without rerun
```

Successful developer evidence is first-class evidence. The agent does not rerun
the live command merely because it did not launch it.

A failed or blocked run is not blindly retried. It is diagnosed first.

## Explicit override

The developer can authorize a specific live command for a specific execution,
for example:

```text
Run `npm run validate:render:test` now.
```

Generic task wording such as “run validation” or “execute system tests” is not
sufficient authorization for deployed-environment execution.
