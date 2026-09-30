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
| [COMMERCE-002](COMMERCE-002-bootstrap-merchant-knowledge-publication.md) | Convergent canonical Tool/Capability/release bootstrap and fixed-identity guards | Ready | COMMERCE-001, ADMIN-001 |
| [COMMERCE-003](COMMERCE-003-resolve-platform-shop-instructions.md) | Additive Platform/Shop instruction resolution, reserved MCP prompts and Studio authoring retirement | Ready | DATABASE-001, SHARED-002, ADMIN-003 |
| [COMMERCE-004](COMMERCE-004-enforce-merchant-knowledge-activation.md) | Post-COMMERCE-002 follow-up: reconcile bootstrap guard to `MERCHANT_OPT_IN` and deny lookup while merchant preference is OFF | Pending | COMMERCE-002, ADMIN-004 |


## Execution frontier

`ARCH-023-COMMERCE-001` is Complete / Accepted at Attempt 2. Its required live
PostgreSQL/pgvector proof now executes the production `retrieveMerchantKnowledge()` path
against the migrated ARCH-023 schema and proves nearest-neighbour ordering plus the
required tenant/revision/provenance exclusions.

`ARCH-023-ADMIN-001` and `ARCH-023-COMMERCE-001` are Complete, but COMMERCE-002 Attempt 3 exposed a Database-owned predecessor-trigger conflict in the required real PostgreSQL successor-release proof. The architect-defined `ARCH-023-DATABASE-004` is now an explicit prerequisite:

```text
COMMERCE-001 -> Complete / Accepted Attempt 2
ADMIN-001    -> Complete / Accepted Attempt 2
DATABASE-004 -> Ready once its supplied portable definition is materialized
                         |
                         v
COMMERCE-002 -> Blocked / Attempt 3 retained
```

After DATABASE-004 is architect-accepted Complete, COMMERCE-002 may transition `blocked -> ready` with Attempt 3 retained; the next launcher claim becomes Attempt 4. The merchant-opt-in architecture decision still does not modify COMMERCE-002 while this task is blocked/in review; COMMERCE-004 remains Pending until both COMMERCE-002 and ADMIN-004 are Complete.

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

`COMMERCE-002` is intentionally unchanged while it is in review. After it completes, `COMMERCE-004` applies the final opt-in decision to the resulting bootstrap prerequisite and independently gates `merchantKnowledge.lookup` on the exact `ShopFeaturePreference`.
