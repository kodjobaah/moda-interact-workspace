---
id: ARCH-002-SHARED-005
architecture_id: ARCH-002
title: Publish OpenTelemetry and Loki shared logger release
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
status: complete
priority: 28
executor: codex
claimed_at: 2026-08-30T23:59:00Z
attempt: 1
depends_on:
  - ARCH-002-SHARED-004
  - ARCH-002-SHARED-006
enables:
  - ARCH-002-SHARED-007
created: 2026-08-30
updated: 2026-08-31
---
# Publish OpenTelemetry and Loki Shared Logger Release

## Loki Release Addition

SHARED-005 must now publish one package containing both accepted capabilities:

```text
SHARED-004
    OpenTelemetry Logs fan-out

SHARED-006
    direct Grafana Loki fan-out
```

If the package is still `0.2.0`, the approved target remains:

```text
0.3.0
```

The external clean-consumer smoke test must additionally verify:

```ts
import {
  initNodeLokiLogging,
} from "@modainteract/moda-interact-shared/logging/node";
```

and prove the registry-installed package can POST one sanitized test log to a
bounded local Loki-compatible `/loki/api/v1/push` receiver.

The release README must document direct Loki configuration and the warning
against routing OTel Logs into the same Loki backend while direct Loki is also
enabled, unless duplicate storage is intentional.

## Objective

Publish the architect-accepted SHARED-004 and SHARED-006 implementations to npm and prove that
both:

```text
@modainteract/moda-interact-shared/logging
@modainteract/moda-interact-shared/logging/node
```

work from a clean external exact-version install.

## Version

Current accepted public package:

```text
0.2.0
```

SHARED-004 adds a new public `./logging/node` capability and OTel log emission
while preserving the existing API.

If the package is still `0.2.0`, the architect-approved target is:

```text
0.3.0
```

If current version differs, stop and return the observed version to the
architect rather than guessing.

## Required Release Validation

Before publish:

```bash
npm test
npm run typecheck
npm run build
npm pack --dry-run
npm whoami
npm view @modainteract/moda-interact-shared@0.3.0 version
```

The target version must not already exist.

Publish:

```bash
npm publish --access public
```

Then independently verify:

```bash
npm view @modainteract/moda-interact-shared version
npm view @modainteract/moda-interact-shared@0.3.0 version
```

Create a clean temporary consumer and install:

```bash
npm install @modainteract/moda-interact-shared@0.3.0
```

Smoke test both:

```ts
import {
  createLogger
} from "@modainteract/moda-interact-shared/logging";

import {
  initNodeOpenTelemetryLogging
} from "@modainteract/moda-interact-shared/logging/node";
```

Use a bounded local OTLP HTTP receiver to prove the registry-installed package
can send an OTel log to `/v1/logs`.

Also smoke-test existing Shopify exports so the release does not regress the
existing package surface.

## README

Update the public README so users can discover:

```text
structured stdout logging
OpenTelemetry log emission
Node process bootstrap
./logging versus ./logging/node
OTLP environment variables
trace correlation behavior
failure isolation
```

Make very clear:

```text
application modules -> ./logging
Node process bootstrap -> ./logging/node
```

and that `./logging/node` must not be pulled through browser/Vite bundles.

## Acceptance Criteria

- [x] SHARED-004 is Complete before publication;
- [x] package/package-lock version are `0.3.0` if starting from `0.2.0`;
- [x] all tests/typecheck/build/pack pass;
- [x] `./logging` and `./logging/node` are included;
- [x] target did not already exist;
- [x] npm publish succeeds;
- [x] registry reports `0.3.0`;
- [x] clean exact-version install succeeds;
- [x] external stdout logger smoke test succeeds;
- [x] external OTLP `/v1/logs` smoke test succeeds;
- [x] external direct-Loki `/loki/api/v1/push` smoke test succeeds;
- [x] registry-installed `initNodeLokiLogging` import succeeds;
- [x] registry-installed package preserves the `./logging` Vite-safe boundary;
- [x] existing Shopify export smoke tests succeed;
- [x] public README documents bootstrap boundary;
- [x] exact published version is recorded;
- [x] task returns `status: review`.

## Completion Report

### Status

Complete — released, registry-verified, and externally smoke-tested.
Returned to `moda_architect` for review (`status: review`).

### Starting Package Version

0.2.0

Confirmed in both `moda-interact-shared/package.json` and
`package-lock.json`, and as the published registry `latest` before release.
The architect-approved target `0.3.0` did not yet exist on the registry.

### Published Package Version

0.3.0

```text
+ @modainteract/moda-interact-shared@0.3.0
```

Published `2026-08-31T00:18:24Z` with the `latest` tag. Both
`package.json` and `package-lock.json` were bumped to `0.3.0` before publish.
No re-publish occurred.

### Validation Results

All run from `moda-interact-shared` at version `0.3.0` (Node v24.19.0 via
`scripts/bootstrap-node.sh`), immediately before publish:

- `npm test` — 49/49 pass, 0 fail.
- `npm run typecheck` — pass (`tsc --noEmit`).
- `npm run build` — pass; `dist/logging/index.js`, `dist/logging/node.js`,
  the shared chunk, and the `.d.ts` files were emitted.
- `npm pack --dry-run` — 21 files, 32.1 kB; both `./logging` and
  `./logging/node` entries are included in the publish artifact.
- `npm whoami` — `kwadwoafriyie` (authenticated publisher).
- `npm view @modainteract/moda-interact-shared@0.3.0 version` — E404:
  the target version did not already exist, so publish was permitted.

### Registry Verification

After publish:

- `npm view @modainteract/moda-interact-shared version` — `0.3.0`
- `npm view @modainteract/moda-interact-shared@0.3.0 version` — `0.3.0`
- `dist.tarball` —
  `https://registry.npmjs.org/@modainteract/moda-interact-shared/-/moda-interact-shared-0.3.0.tgz`
- `dist.integrity` —
  `sha512-hxhoL+lDv9KkhqRsjD9ZeNAQ/gxQoDFZmt62qifOKp9SYo9JjKkN8tR76Q+ZACQD4hOAZ/kT6Oae24ZdTbvtig==`
- registry `time` — `0.3.0`: `2026-08-31T00:18:24.358Z`

### Clean External Consumer Install

A fresh consumer was created outside the repository at
`/tmp/moda-shared005-consumer` and installed the exact published version:

```bash
npm install --save-exact @modainteract/moda-interact-shared@0.3.0
```

Result: exit 0, `added 60 packages`; the resolved installed version was
confirmed as `0.3.0`.

### External Smoke Tests

All five independent smoke tests ran as child processes against the
registry-installed package and passed (`ALL SMOKE TESTS PASSED`, exit 0):

1. **Stdout logger** (`smoke-stdout.mjs`) — `createLogger` from
   `@modainteract/moda-interact-shared/logging` wrote one canonical structured
   JSON record: `service.namespace=moda-interact`,
   `service.name=smoke-stdout`, `deployment.environment.name=test`,
   `event=smoke.stdout`, `data={hello:world,n:42}`.
2. **OTLP `/v1/logs`** (`smoke-otlp.mjs`) — `initNodeOpenTelemetryLogging`
   from `.../logging/node` with a bounded local receiver POSTed an OTel log to
   `http://127.0.0.1:<port>/v1/logs` (HTTP 200; `application/json`,
   1147-byte body; `Content-Type` matched the allowed `json|protobuf`
   contract).
3. **Direct Loki `/loki/api/v1/push`** (`smoke-loki.mjs`) —
   `initNodeLokiLogging` from `.../logging/node` with a bounded local
   Loki-compatible receiver POSTed one sanitized record to
   `/loki/api/v1/push`. Verified canonical labels
   `service_namespace`/`service_name`/`environment`, secret value absent,
   `apiKey` -> `[REDACTED]`, and high-cardinality `jobId` present only in the
   JSON body (never a label).
4. **Shopify exports** (`smoke-shopify.mjs`) — the registry-installed
   `@modainteract/moda-interact-shared/shopify` and `/shopify/node` surfaces
   are intact: commerce/recovery event constants, schema versions, queue
   contracts, and the deterministic `createShopifyWebhookJobId` /
   `createShopifyCheckoutJobId` / `createShopifyOrderJobId` /
   `createPendingRecoveryCandidateJobId` SHA-256-prefixed id helpers.
5. **`./logging` vs `./logging/node` boundary** (`smoke-boundary.mjs`) —
   `dist/logging/index.js` contains no `winston`, no `node:` imports, and
   retains the `emitLokiLog` bridge; `dist/logging/node.js` imports `winston`
   and `winston-loki`; the two entries are distinct bundles.

### winston-loki Behaviour Observed

During external smoke testing it was observed — and confirmed in the installed
`winston-loki@6.1.7` source (`lokiLabels = { level: level }` merged with
`this.labels`) — that the winston-loki transport always adds a
low-cardinality `level` label to every stream, **in addition to** Moda's three
explicitly configured labels. The shared package therefore emits exactly four
labels per stream:

```text
service_namespace
service_name
environment
level        (added by winston-loki itself)
```

This is transport-library behaviour, not a Moda configuration change: Moda's
configured label set remains exactly the three canonical low-cardinality
labels with `useWinstonMetaAsLabels: false`, and no high-cardinality
operational identifier ever becomes a stream label.

### README

`README.md` already documents, and remains accurate for the release:

```text
structured stdout logging
OpenTelemetry log emission
Node process bootstrap
./logging versus ./logging/node
OTLP environment variables
trace correlation behavior
failure isolation
direct Loki configuration
duplicate-delivery warning
```

including the explicit rule that `./logging/node` must be imported and
initialized only from the Node process bootstrap, never through
Vite/application/browser bundles.

### Git Commit / Push Information

Two commits were created on `moda-interact-shared` `main` and pushed to
`origin/main` (https://github.com/kodjobaah/moda-interact-shared.git):

```text
28aed03  feat(logging): release OpenTelemetry and Loki shared logger
         15 files changed, 3038 insertions(+), 65 deletions(-)
         (the intertwined SHARED-004 + SHARED-006 + release working tree
          that produced the published 0.3.0 tarball; one truthful commit,
          no artificial history reconstruction)

1398af7  docs(logging): document winston-loki level label
         README.md only, 8 insertions(+), 2 deletions(-)
         (post-release documentation-only correction)
```

Push results:

```text
git push origin main  ->  68104fd..28aed03  main -> main   (release commit)
git push origin main  ->  28aed03..1398af7  main -> main   (docs commit)
```

Final branch / upstream state:

```text
## main...origin/main          (local clean, in sync with upstream)
```

Final `git status --short`:

```text
(empty — working tree clean)
```

The published `0.3.0` artifact was produced from the pre-commit working tree
(HEAD `68104fd`); commit `28aed03` records exactly that accepted source. No
npm republish was performed for the documentation-only correction.

## Architect Review

### Review Status

Pending — returned to `moda_architect` for review.

### Handoff Notes

The published package is `0.3.0`; all external smoke tests pass. The only
observed transport-level behaviour is winston-loki's own `level` label (see
Completion Report), now documented in the README and the pushed `1398af7`
docs commit. Git/VCS completion is done: `main` is at `1398af7`, clean and
synchronized with `origin/main`.

## Architect Review — Accepted (2026-08-31)

Review status: **Accepted / Complete**.

The recorded SHARED-005 completion evidence demonstrates publication of
`@modainteract/moda-interact-shared@0.3.0`, exact clean-consumer installation,
stdout logging, OTLP Logs, direct Loki, browser-boundary and Shopify-export
smoke validation. The compressed workspace archive intentionally omits
`node_modules`; that packaging fact is not a regression in the published shared
release and does not invalidate the recorded release validation.

Dependency decision:

```text
ARCH-002-SHARED-005 -> Complete
ARCH-002-SHARED-007 -> Ready
```
