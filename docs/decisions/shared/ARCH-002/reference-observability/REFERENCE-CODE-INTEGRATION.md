# Reference observability code integration

The reference files are staged architecture guidance, not one monolithic patch.

## SHARED-007

Use:

```text
src/observability/index.ts
src/observability/node.ts
```

The SHARED-007 `node.ts` intentionally supports only:

```text
HTTP/HTTPS
Undici/fetch
traces
metrics
sampling
OTLP
logging integration
runtime lifecycle
```

It must not import Prisma or BullMQ packages.

## SHARED-008

Use:

```text
src/observability/bullmq.ts
prisma-node-extension.reference.md
```

SHARED-008 adds the `prisma` profile extension to the already accepted Node
runtime and adds the BullMQ adapter.

## SHARED-009

Use the GenAI reference only for active span mechanics:

```text
src/observability/genai.ts
```

SHARED-009 owns conversation-turn, agent and tool active spans, parent/child
nesting, status and bounded safe span attributes.

It does not add operational metrics.

## SHARED-011

Extend the accepted SHARED-009 helper boundary with bounded duration/error
metrics.

Arbitrary agent/tool names must remain absent from metric attributes. String
truncation alone is not treated as a cardinality bound.

## SHARED-010


Only after SHARED-007, SHARED-008, SHARED-009 and SHARED-011 are
architect-accepted should `moda_shared` publish the exact release and record it
for consumer tasks.

SHARED-010 is a publication task. Do not rerun implementation tests, typecheck,
integration suites or other code validation already accepted in prerequisite
tasks. An existing `prepack` build that runs automatically as part of
`npm publish` is a release-packaging mechanic, not a new validation cycle.

## Service consumers

Service examples under `services/` represent the **final post-SHARED-010 API**.
They may therefore include `prisma: true` even though SHARED-007 alone does not.

All consumer agents must also read:

`docs/observability/shared-observability-runtime.md`
