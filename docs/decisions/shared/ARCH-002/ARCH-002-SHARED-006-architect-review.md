# ARCH-002-SHARED-006 Architect Review

## Decision

**Accepted / Complete**

The direct Grafana Loki transport implementation is accepted.

## Actual implementation reviewed

The architect inspected the returned shared workspace including:

```text
moda-interact-shared/src/logging/loki.ts
moda-interact-shared/src/logging/logger.ts
moda-interact-shared/src/logging/node/loki.ts
moda-interact-shared/src/logging/node/loki.test.ts
moda-interact-shared/src/logging/node.ts
moda-interact-shared/package.json
moda-interact-shared/package-lock.json
moda-interact-shared/README.md
moda-interact-shared/tsup.config.ts
docs/decisions/shared/ARCH-002/SHARED-006-add-direct-loki-transport.md
```

## Findings

Accepted:

- application-facing `./logging` API is unchanged;
- the canonical sanitized `LogRecord` fans out independently to:
  - stdout/custom sink;
  - OpenTelemetry Logs API;
  - optional direct Loki;
- `winston` and `winston-loki` are isolated behind `./logging/node`;
- no Winston Console transport was introduced;
- the lightweight Loki bridge uses `globalThis` as designed so separately
  bundled `./logging` and `./logging/node` entries can share the emitter;
- only static low-cardinality Loki labels are configured:
  - `service_namespace`;
  - `service_name`;
  - `environment`;
- `useWinstonMetaAsLabels` remains false;
- direct Loki failure is best-effort and cannot escape into business logic;
- connection failures are not recursively logged through the shared logger;
- package version remains `0.2.0`;
- `winston@3.19.0` and `winston-loki@6.1.7` are exact runtime dependencies;
- resolved `protobufjs@7.6.6` satisfies the task's `>=7.6.5` requirement;
- README documents console + OTel Logs + Loki, the Node bootstrap boundary,
  Loki environment variables, cardinality rules, and duplicate-delivery risk.

## Reference comparison

All architecture-supplied implementation files match the reference exactly
except for one accepted package-script correction.

Actual:

```json
"test": "tsx --test \"src/**/*.test.ts\""
```

Reference:

```json
"test": "tsx --test src/**/*.test.ts"
```

The quoted pattern is accepted.

The implementing agent established that npm executes the script through
`/bin/sh`, where the unquoted recursive glob did not execute the complete
nested test suite. Passing the pattern through to the Node test runner causes
the intended recursive discovery.

This is a correctness improvement to validation rather than an architectural
deviation.

## Validation reviewed

The Completion Report records:

```text
npm test:             49/49 pass
npm run typecheck:    pass
npm run build:        pass
npm pack --dry-run:   pass
```

The 49 tests include:

```text
6 shared logger tests
4 OTel node tests
1 direct-Loki integration test
7 shopify/node tests
31 nested Shopify v1/v2 tests
```

The direct-Loki integration test exercises:

```text
createLogger(...)
    ->
winston-loki
    ->
POST /loki/api/v1/push
```

and verifies:

```text
canonical labels present
event/body present
secret absent
[REDACTED] present
high-cardinality value remains body data rather than architecture label
```

The build inspection records:

```text
dist/logging/index.js
    no winston
    no winston-loki
    no Node networking imports

dist/logging/node.js
    OpenTelemetry Node logging dependencies
    winston
    winston-loki
```

This satisfies the browser/Vite boundary.

## Security review

The returned lockfile contains:

```text
winston             3.19.0
winston-loki        6.1.7
protobufjs          7.6.6
```

The Completion Report records one low-severity pre-existing development-only
`esbuild` audit finding and no new high/critical vulnerability from this task.

No dependency override was silently introduced.

## Architecture conformance

Accepted.

The shared logging architecture is now:

```text
application
    |
    v
@modainteract/moda-interact-shared/logging
    |
    +--> structured stdout
    +--> OpenTelemetry Logs API
    +--> optional direct Loki
```

Node transport configuration remains isolated in:

```text
@modainteract/moda-interact-shared/logging/node
```

Infrastructure owns endpoint/secret injection; the shared library owns the
reusable delivery implementation.

## Release outcome

Do not resume Shopify yet.

The next dependency is:

```text
ARCH-002-SHARED-005
```

which must publish one package containing both:

```text
SHARED-004  OpenTelemetry Logs
SHARED-006  Direct Loki
```

Expected release version, if the current package is still `0.2.0`:

```text
0.3.0
```

The release must independently smoke-test the registry-installed package
against both:

```text
/v1/logs
/loki/api/v1/push
```

before Shopify resumes.
