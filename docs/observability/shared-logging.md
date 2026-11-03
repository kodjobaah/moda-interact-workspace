# Shared Structured Logging

## Status

Architecture-approved shared logging contract.

Implementation owner:

```text
ARCH-002-SHARED-002
moda_shared
moda-interact-shared
```

Consumer package:

```text
@modainteract/moda-interact-shared/logging
```

Consumers must not depend on this export until the shared task/version they
consume actually contains it.

## Purpose

Moda Interact has multiple runtime services that need the same basic logging
capabilities.

The platform must not accumulate separate generic loggers in:

```text
moda-interact
moda-interact-background
moda-interact-messaging
moda-interact-admin
```

Generic structured logging belongs in `moda-interact-shared`.

Service-specific semantic adapters are allowed when they add domain meaning,
but they must use the shared logger rather than reimplementing:

```text
JSON serialisation
log levels
redaction
error serialisation
log size bounds
service/environment envelope
sink failure isolation
```

## Import

```ts
import {
  createLogger,
  type StructuredLogger,
} from "@modainteract/moda-interact-shared/logging";
```

## Create One Service Logger

Each deployable process supplies its canonical identity.

Example application:

```ts
const logger = createLogger({
  serviceName: "moda-interact",
  environment: deploymentEnvironment,
});
```

Example background worker:

```ts
const logger = createLogger({
  serviceName: "moda-recovery-worker",
  environment: deploymentEnvironment,
});
```

The default namespace is:

```text
moda-interact
```

The emitted canonical identity is:

```text
service.namespace=moda-interact
service.name=<logical service/process>
deployment.environment.name=<environment>
```

For deployed ARCH-002 environments:

```text
deployment.environment.name=test
deployment.environment.name=production
```

The shared library deliberately does not read service-specific environment
variables itself. The owning service resolves its environment and passes it to
`createLogger`.

## Basic Use

```ts
logger.info("shopify.webhook.outcome", {
  topic: "checkouts/create",
  outcome: "ENQUEUED",
  ackMs: 18,
});

logger.warn("queue.retry", {
  queue: "recovery",
  attempt: 2,
});

logger.error("recovery.failed", {
  recoveryId,
  error,
});
```

## Child Loggers

Use child context for stable process/component context:

```ts
const workerLogger = logger.child({
  queue: "recovery",
  worker: "materialize",
});

workerLogger.info("job.started", {
  jobId,
});

workerLogger.info("job.completed", {
  jobId,
  durationMs,
});
```

Do not create a child logger containing customer records or complete provider
payloads.

## Output Contract

The default sink emits one JSON string per console call:

```json
{
  "timestamp": "2026-08-30T12:00:00.000Z",
  "level": "info",
  "event": "shopify.webhook.outcome",
  "service.namespace": "moda-interact",
  "service.name": "moda-interact",
  "deployment.environment.name": "test",
  "data": {
    "topic": "checkouts/create",
    "outcome": "ENQUEUED",
    "ackMs": 18
  }
}
```

Do not prefix the JSON with a second free-form argument such as:

```ts
console.info("shopify_webhook", JSON.stringify(data));
```

The single JSON record is the logging transport boundary.

## Event Names

Use stable machine-readable semantic event names.

Prefer:

```text
shopify.webhook.outcome
meta.webhook.outcome
queue.job.started
queue.job.completed
queue.job.failed
recovery.materialized
agent.message.failed
```

Avoid:

```text
Something happened
DEBUG HERE
webhook log 1
```

Changing an event name used by dashboards/alerts should be treated deliberately.

## Log Levels

Use:

```text
debug
    detailed diagnostics normally unnecessary for routine operation

info
    expected meaningful operational event

warn
    abnormal/retry/degraded event that does not yet represent final failure

error
    failed operation requiring investigation or final failure path
```

Do not use `error` simply because an HTTP provider returned a normal,
business-handled outcome.

## Sensitive Data

The logger provides defense-in-depth redaction, but consumers must still avoid
passing prohibited data.

Do not intentionally log:

```text
access tokens
refresh tokens
authorization headers
cookies
OAuth codes
passwords
API keys
private keys
webhook verification secrets
complete provider webhook payloads
complete HTTP request/response bodies
customer email/phone/address/name
payment/card data
```

Do not treat the redactor as permission to log an entire object and hope it
removes everything sensitive.

Prefer constructing a small explicit logging object.

## High-Cardinality Data

Operational logs may contain safe high-cardinality correlation identifiers when
needed, for example:

```text
deliveryId
eventId
jobId
recoveryId
traceId
```

provided they are not credentials or prohibited customer data.

This does **not** mean those values are safe metric labels.

Metric cardinality remains independently bounded by service-specific
OpenTelemetry code.

## Error Logging

Pass errors as a field:

```ts
logger.error("queue.job.failed", {
  jobId,
  error,
});
```

The shared logger serialises `Error` to a bounded object containing:

```text
name
message
```

Stack is omitted by default.

Consumers must still avoid wrapping secrets/provider payloads into custom error
messages.

### Provider-origin errors (mandatory for external integration failures)

An internal reason code such as `MODEL_INVOCATION_FAILED`, `MCP_HTTP_SERVER_ERROR` or
`MCP_WOOCOMMERCE_PROVIDER_FAILED` is a **classification**, NOT the original failure.
When an upstream provider, MCP server or SDK actually supplies an error, preserve
and log **that original returned error**, not a guessed/paraphrased explanation.
This requirement applies equally to failure outcomes that are caught and converted
to a typed fallback or retry result.

At the owning source/adapter boundary, emit through the existing Shared logger a
bounded structured failure containing, where the source actually supplied them:

- `origin`: `provider_response`, `mcp_response`, `sdk_exception` or `internal`;
  never label an internally generated message as provider-supplied;
- `provider`, `operation`, `httpStatus`, `providerRequestId` and
  `providerError.code`/`providerError.message` with the **source's original
  code/message** (not an operator explanation);
- original safe `providerError.details` (from the provider's structured error
  object), or `providerErrorBody` when the provider returned a non-JSON error;
- original SDK/transport `error.name` and `error.message` when no provider
  response exists, plus the available `cause` chain at the application boundary;
- separate Moda-owned `reasonCode`, correlation IDs, `redactionApplied` and
  `truncated` flags. Do not populate missing upstream fields with guessed values.

**Preserve source wording and value semantics.** The only permitted transformations
of originating error text in logs are security redaction and bounded truncation;
make these visible via `redactionApplied` / `truncated`. Extract the original
provider error object, rather than the entire successful response, request, model
completion, webhook, GraphQL data payload, MCP tool result or full response
headers. For GraphQL HTTP 200 with `errors`, retain the actual provider
`errors[].message`, `extensions.code` and safely bounded details. For an HTTP
error with no structured `error` key, retain a bounded and safely redacted error
response body if possible. Never log unfiltered provider response bodies.

**Security before emission:** Provider error text is untrusted and can echo tokens,
credentials, prompt text, headers, signed URLs, email/phone/address, customer
names and payment data. Provider-specific adapters must remove those sensitive
spans/fields **before** passing diagnostics to the Shared logger; the Shared
logger's generic redaction is only a second defence. If safe extraction is
impossible, record `redactionApplied: true` and the literal `[REDACTED]`
for the unsafe portion, keeping real safe status/code/request ID and source
exception metadata. Never substitute an invented provider explanation. Enforce
Shared bounds and stricter per-provider size budgets where needed; never persist
provider error bodies in discount snapshots, outreach prompts, MCP tool results,
customer messages or analytics.

Preserve actual exception `cause` in application error propagation; do not discard
it to construct a new generic Error. Log the provider/SDK error **once at the
boundary that received it**, with contextual downstream reason codes/correlation
as needed. An expected fallback/no-send does not suppress the source failure log.
Logging remains best-effort: a logging sink failure must not change business
success, retries, cancellation, authorisation or customer-visible behaviour.

Acceptance tests for each affected provider adapter inject a distinct real
upstream message and check it survives in the emitted record (apart from explicit
redaction/truncation), while injected secrets/PII do not; tests must also prove
that no upstream error produces no fabricated `providerError` field. No new
logging utility, Shared wire schema or generic error-response envelope is implied.

## Logging Failure Isolation

Logging is best-effort.

A sink/serialisation failure must not:

```text
reject a Shopify webhook
fail a BullMQ job
change a database transaction
change HTTP success/failure semantics
```

This is why logger emission swallows logging-internal failures.

## Logging and OpenTelemetry Are Separate

The shared logger does not emit metrics or spans.

Do not implement:

```text
logger.info(...)
    -> automatically increment metric
    -> automatically create span
```

Logs and OTel have different cardinality/lifecycle constraints.

Correct pattern:

```text
service-specific operation
        |
        +--> shared structured logger
        |
        +--> service-owned OTel instrumentation
```

Example Shopify:

```ts
logger.info("shopify.webhook.outcome", safeLogFields);
recordShopifyWebhookTelemetry(telemetryEntry);
```

The Shopify metric/span implementation remains in `moda-interact`.

## Service-Specific Adapters

A small semantic adapter is allowed.

For example:

```ts
export function recordShopifyWebhookOutcome(
  entry: ShopifyWebhookObservation,
): void {
  logger.info("shopify.webhook.outcome", {
    topic: entry.topic,
    deliveryId: entry.deliveryId,
    eventId: entry.eventId,
    queue: entry.queue,
    jobId: entry.jobId,
    outcome: entry.outcome,
    shopId: entry.shopId,
    shopDomain: entry.shopDomain,
    ackMs: entry.ackMs,
  });

  recordShopifyWebhookTelemetry(entry);
}
```

That adapter is Shopify-specific and may remain in `moda-interact`.

What must not remain is another local implementation of:

```text
create logger
JSON sink
redaction
generic levels
generic error serialisation
generic size bounds
```

## Tests

Service tests should test semantic logging through an injected/shared logger
sink where appropriate.

The shared package itself owns tests proving:

```text
canonical envelope
redaction
Error serialisation
child context
sink failure isolation
circular-value handling
size/depth bounds
```

## New Service Rule

Before adding generic structured logging to a Moda Interact runtime:

1. read this document;
2. check that the consumed shared package exposes `./logging`;
3. use `createLogger`;
4. keep service-specific semantics in the owning repository;
5. keep service-specific OpenTelemetry separate;
6. if the shared capability is missing, return the dependency to
   `moda_architect` instead of creating another generic logger.

## Shopify Migration

`ARCH-002-SHOPIFY-003` is explicitly blocked on
`ARCH-002-SHARED-002`.

When resumed, Shopify must:

```text
remove its local generic logging implementation
use @modainteract/moda-interact-shared/logging
retain Shopify-specific OTel metrics/spans locally
retain only a thin Shopify semantic observability adapter if useful
```

See:

```text
docs/decisions/shopify/ARCH-002/SHOPIFY-003-add-opentelemetry.md
```
