# ARCH-023 Commerce tasks

Architecture: [`ARCH-023`](../../../architecture/ARCH-023-merchant-knowledge.md).

Assigned agent: `moda_commerce`.

Repository: `moda-interact-commerce`.

Coordinator: `moda_architect`.

The Commerce decomposition follows runtime/security/lifecycle ownership rather than UI/file count:

```text
DATABASE-001 + SHARED-002 + ARCH-021-COMMERCE-096
                        |
                        v
                  COMMERCE-001
        merchantKnowledge.lookup@1.0.0
          entitlement + embedding + pgvector
                        |
                        v
                  COMMERCE-002
        canonical Tool/Capability/release bootstrap
                        ^
                        |
                     ADMIN-001


DATABASE-001 + SHARED-002 + ADMIN-003
                        |
                        v
                  COMMERCE-003
      additive Platform + Shop instruction resolution
      + reserved MCP prompts + Studio ownership cleanup
```

COMMERCE-001 and COMMERCE-003 are independent once their own prerequisites are complete.

Individual task YAML is authoritative.

| Task | Outcome | Status | Depends on |
|---|---|---|---|
| [COMMERCE-001](COMMERCE-001-implement-merchant-knowledge-policy-operation.md) | Register/execute `merchantKnowledge.lookup@1.0.0` with operation-level entitlement and exact pgvector retrieval | Complete — Accepted Attempt 2 | DATABASE-001, SHARED-002, ARCH-021-COMMERCE-096 |
| [COMMERCE-002](COMMERCE-002-bootstrap-merchant-knowledge-publication.md) | Convergent canonical Tool/Capability/release bootstrap and fixed-identity guards | Complete — Accepted Attempt 4 | COMMERCE-001, ADMIN-001, DATABASE-004 |
| [COMMERCE-003](COMMERCE-003-resolve-platform-shop-instructions.md) | Additive Platform/Shop instruction resolution, reserved MCP prompts and Studio authoring retirement | Ready | DATABASE-001, SHARED-002, ADMIN-003 |
| [COMMERCE-004](COMMERCE-004-enforce-merchant-knowledge-activation.md) | Require request-time Merchant Knowledge opt-in and deny lookup while merchant preference is OFF | Pending | COMMERCE-002, ADMIN-004 |


## Execution frontier

`ARCH-023-COMMERCE-001` is Complete / Accepted at Attempt 2. Its required live
PostgreSQL/pgvector proof now executes the production `retrieveMerchantKnowledge()` path
against the migrated ARCH-023 schema and proves nearest-neighbour ordering plus the
required tenant/revision/provenance exclusions.

`ARCH-023-COMMERCE-002` is Complete / Accepted Attempt 4 after consuming the architect-accepted DATABASE-004 guard correction and passing the full disposable PostgreSQL successor-preservation proof. The accepted bootstrap already requires the `MERCHANT_OPT_IN` Feature mode and remains preference-neutral.

```text
COMMERCE-001 -> Complete / Accepted Attempt 2
ADMIN-001    -> Complete / Accepted Attempt 2
DATABASE-004 -> Complete / Accepted Attempt 1
                         |
                         v
COMMERCE-002 -> Complete / Accepted Attempt 4
                         |
                         +--> COMMERCE-004 remains Pending on ADMIN-004
```

This readiness promotion does not claim or start COMMERCE-002. ADMIN-004 is now Complete / Accepted Attempt 1. The merchant-opt-in architecture decision does not modify COMMERCE-002 while it is in review; COMMERCE-004 remains Pending only until COMMERCE-002 is Complete.
COMMERCE-004 is narrowed to request-time merchant activation enforcement; it no longer owns a bootstrap activation-mode correction.

COMMERCE-001 must consume exactly `@modainteract/moda-interact-shared@1.0.1`.

COMMERCE-003 is Ready because `ARCH-023-ADMIN-003`, `ARCH-023-DATABASE-001` and `ARCH-023-SHARED-002` are Complete/accepted. It remains pinned to the same Shared revision and is not claimed or started by this promotion.

## ARCH-021 Policy Operation relationship

ARCH-023 does not reimplement generic `POLICY_OPERATION` Studio support.

```text
ARCH-021-COMMERCE-096
  canonical registry/descriptors
      ↓
ARCH-023-COMMERCE-001
  registers merchantKnowledge.lookup

ARCH-021-COMMERCE-097..100
  generic existing Policy Operation Studio UI/test/save/publish
```

COMMERCE-002 runtime/bootstrap correctness does not wait for C097-C100. Once the generic ARCH-021 tasks are complete, the fixed Merchant Knowledge Tool must work through them without another execution-kind implementation.

## Required cross-domain follow-up

Production `runCommerceTurn` is currently invoked by `moda-interact-background`.

COMMERCE-003 exposes exact trusted instruction texts through standard MCP prompts:

```text
commerce/platform-instructions
commerce/shop-instructions
```

A bounded Background task is still required to fetch those prompts and append them to trusted `hostInstructions` in Platform-then-Shop order before invoking the Shared runner.

This follow-up is required before final ARCH-023 system acceptance.

## Merchant opt-in reconciliation

`COMMERCE-002` is Complete / Accepted Attempt 4 with the final `MERCHANT_OPT_IN` bootstrap prerequisite and zero `ShopFeaturePreference` writes. `COMMERCE-004` therefore owns only the remaining request-time authority check: plan entitlement plus an explicit enabled `ShopFeaturePreference` before embedding or pgvector retrieval.
