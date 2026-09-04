# Validation Command Naming Convention

## Principle

Name a reusable validator after **what it validates**, not after **the
architecture task that first created it**.

Architecture identifiers are coordination metadata, not permanent product/tool
names.

Prefer:

```text
validate:<platform-or-capability>:<environment-or-mode>
```

over:

```text
validate:archNNN-...
```

when the validator is expected to survive beyond one architecture initiative.

## Where architecture IDs belong

Architecture/task IDs remain useful and should be preserved in:

```text
docs/decisions/... task files
Completion Reports
developer validation report metadata
.validation/<TASK-ID>-<timestamp>/
architect review/acceptance history
```

Example:

```bash
./scripts/developer-validation.sh \
  ARCH-002-SYSTEM-TEST-006 \
  -- ./scripts/validate-render-test.sh
```

Here:

```text
ARCH-002-SYSTEM-TEST-006
```

identifies **why this evidence is being collected**.

The executable:

```text
validate-render-test.sh
```

identifies **what is being validated**.

## Render validation convention

Target public npm command:

```bash
npm run validate:render:test
```

Target Node entrypoint:

```bash
node scripts/validate-render-deployment.js --environment test
```

Target secure developer bootstrap:

```bash
./scripts/validate-render-test.sh
```

Target reusable evidence wrapper:

```bash
./scripts/developer-validation.sh \
  <TASK_ID> \
  -- <validation-command>
```

## Responsibilities

### `scripts/validate-render-deployment.js`

Owns the actual Render deployment probe logic.

It should:

```text
validate the requested environment
consume already-resolved inputs
emit bounded/sanitized result data
return stable exit codes
avoid task/architecture-specific naming
```

### `scripts/validate-render-test.sh`

Owns test-environment developer bootstrap.

It may:

```text
set canonical non-secret test hosts
prompt silently for missing live secrets
export required inputs
redact secret literal/encoded forms from validator output
invoke npm run validate:render:test
preserve the validator exit code
```

It should not generate architecture-specific evidence paths.

### `scripts/developer-validation.sh`

Owns generic evidence capture.

It receives:

```text
<TASK_ID> -- <command>
```

and writes:

```text
.validation/<TASK_ID>-<timestamp>/
  full.log
  report.md
```

It must remain agnostic about Render, Shopify, Meta, ARCH-002 and
SYSTEM-TEST-006.

The command it wraps is responsible for producing secret-safe output.

## Future expansion

The stable naming permits future additions such as:

```text
validate:render:test
validate:render:production
```

using the same deployment validator with different environment configuration.

A later architecture may therefore run:

```bash
./scripts/developer-validation.sh \
  ARCH-007-SYSTEM-TEST-003 \
  -- ./scripts/validate-render-test.sh
```

without creating a new `arch007` validator.

## Historical names

Do not rewrite historical Completion Reports merely because a reusable command
was renamed.

Old evidence may correctly say:

```text
validate:arch002-render-test
run-arch002-render-test-topology.js
```

because that was the executable name at the time.

New active code/docs should use the generic convention after migration.

## Scope control

Do not opportunistically rename every architecture-prefixed validation command
while fixing one task.

For the current SYSTEM-TEST-006 work, migrate the Render test deployment
validator only.

Existing ARCH-002 observability and production-readiness validators should be
reviewed separately after the current deployed test gate is accepted.
