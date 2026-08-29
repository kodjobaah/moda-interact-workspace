# ARCH-002-SYSTEM-TEST-001 — Validate integrated production topology

## Metadata

```yaml
id: ARCH-002-SYSTEM-TEST-001
architecture: ARCH-002
status: Blocked
assigned_agent: moda_system_test
repository: moda-interact-system-test
domain: system-test
depends_on:
  - ARCH-002-GATEWAY-002
  - ARCH-002-GATEWAY-003
  - ARCH-002-GATEWAY-004
  - every prerequisite implementation task created from GATEWAY-001 findings
architect_review_required: true
```

## Objective

Validate observable end-to-end behaviour of the production gateway/private-service/worker topology after all required implementation and infrastructure tasks are Complete.

This task proves the architecture. It does not own fixes in other repositories.

## Required validation areas

Where relevant to the implemented architecture, validate:

- public gateway reachability;
- Shopify routing;
- Meta/WhatsApp routing;
- private-service routing;
- provider webhook verification compatibility;
- Redis/BullMQ connectivity;
- worker processing;
- PostgreSQL state transitions;
- retries;
- duplicate handling;
- correlation IDs;
- tenant isolation;
- recovery flow;
- messaging flow;
- failure behaviour.

## Required topology assertions

Verify the observable deployment behaves consistently with:

```text
Internet
   |
Render public load balancer
   |
moda-interact-gateway
   |
Render private network
   +--> moda-interact
   +--> moda-interact-messaging
   +--> moda-interact-admin
```

and that background work is distributed through BullMQ/Redis rather than through an HTTP load-balancing tier.

## Webhook integrity assertions

Verify that gateway routing does not prevent the owning ingress service from validating provider signatures.

Where test facilities exist:

- confirm Shopify webhook verification still succeeds through the gateway;
- confirm Meta/WhatsApp verification still succeeds through the gateway;
- confirm required provider-signature headers survive proxying;
- confirm request-body handling remains compatible with signature verification.

## Failure-path assertions

Where practical, validate observable behaviour for:

- unavailable private upstream;
- transient queue/worker failure;
- retryable work;
- duplicate event delivery;
- invalid provider signature;
- dependency outage/failure modes defined by the architecture.

Do not introduce destructive production-data operations merely for validation.

## Ownership boundary

`moda_system_test` may:

- execute the platform;
- call public interfaces;
- observe queues/services;
- inspect resulting state;
- run architecture test scenarios;
- record failures.

`moda_system_test` must not modify another repository's implementation just to make the test pass.

If a defect is found:

1. record the failing scenario and evidence;
2. identify the apparent owning component;
3. return the defect to `moda_architect`;
4. allow `moda_architect` to create/reopen the owning implementation task;
5. rerun the affected architecture validation after the fix is accepted.

## Acceptance criteria

- [ ] public gateway is reachable;
- [ ] Shopify traffic reaches the intended private service;
- [ ] Meta/WhatsApp traffic reaches the intended private service;
- [ ] private application services are not directly exposed where the architecture requires them to remain private;
- [ ] provider verification remains compatible with gateway proxying;
- [ ] Redis/BullMQ connectivity works for required producers/consumers;
- [ ] required worker types can process their owned work;
- [ ] PostgreSQL state transitions required by exercised flows are observable;
- [ ] retry behaviour is validated where applicable;
- [ ] duplicate handling is validated where applicable;
- [ ] correlation/request identifiers are preserved where required;
- [ ] tenant isolation is not weakened by the topology;
- [ ] recovery flow is validated where applicable;
- [ ] messaging flow is validated where applicable;
- [ ] relevant failure behaviour is validated;
- [ ] defects are returned to the architect rather than silently repaired across ownership boundaries;
- [ ] test evidence is recorded;
- [ ] task is ready for architect acceptance.

## Architecture completion gate

Completion of this task is required before `ARCH-002` may be marked `Implemented`, unless `moda_architect` explicitly records that a particular system-test area is not applicable.

## Completion Report

To be completed by `moda_system_test`.

### Summary

TBD

### Environment/topology tested

TBD

### Scenarios executed

TBD

### Results

TBD

### Defects identified

TBD

### Follow-up tasks requested

TBD

### Final validation status

TBD
