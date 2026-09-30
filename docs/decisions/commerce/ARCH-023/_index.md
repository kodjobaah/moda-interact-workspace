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
   direct Feature/Tool Capability + immutable release bootstrap
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
| [COMMERCE-002](COMMERCE-002-bootstrap-merchant-knowledge-publication.md) | Restart-safe `MERCHANT_OPT_IN` direct Feature/Tool Capability bootstrap with exact immutable successor-release preservation and canonical `nunjucks.v1` seed | Ready — Attempt 2 Changes Requested; next claim Attempt 3 | COMMERCE-001, ADMIN-001 |
| [COMMERCE-003](COMMERCE-003-resolve-platform-shop-instructions.md) | Additive Platform/Shop instruction resolution, reserved MCP prompts and Studio authoring retirement | Pending | DATABASE-001, SHARED-002, ADMIN-003 |


## Execution frontier

`ARCH-023-COMMERCE-001` is Complete / Accepted at Attempt 2. Its required live
PostgreSQL/pgvector proof now executes the production `retrieveMerchantKnowledge()` path
against the migrated ARCH-023 schema and proves nearest-neighbour ordering plus the
required tenant/revision/provenance exclusions.

`ARCH-023-ADMIN-001` is also Complete, so both declared dependencies of COMMERCE-002 are
satisfied. Attempt 1 correctly stopped because the task still described the removed
ARCH-020 Capability-revision/`selectionBinding` model. Architect reconciliation rewrote
COMMERCE-002 against the accepted ARCH-021 direct model. Attempt 2 then produced a valid
generic successor-release direction but returned with incomplete bootstrap implementation,
6/9 focused bootstrap tests failing and mandatory disposable-PostgreSQL proof outstanding.
That is task-owned correction work rather than an architectural blocker, so the same task
returns to Ready with Attempt 2 preserved.

```text
COMMERCE-001 -> Complete / Accepted Attempt 2
ADMIN-001    -> Complete / Accepted Attempt 2
COMMERCE-002 -> Ready / Attempt 2 Changes Requested; next claim Attempt 3
```

The corrected bootstrap uses direct `featureId` + `toolId` Capability identity,
`CommerceFeatureConfiguration.behaviourPrompt`, release-pinned exact Tool revisions and
immutable `CommerceReleaseFeature` snapshots. Application restart of an already-usable
publication is a durable no-op. When adding Merchant Knowledge to an existing release,
a bounded generic successor path must copy unrelated Tool pins and Feature Behaviour
snapshots exactly rather than re-resolving current authoring state.

Attempt 3 must first correct the focused lifecycle test-double signatures, then complete
the R20 regression matrix and the mandatory real PostgreSQL/bootstrap convergence and
immutable successor-snapshot proof. An unverified ambient `DATABASE_URL` remains forbidden;
the task now explicitly authorises one invocation-owned disposable pgvector runner.

The corrected Merchant Knowledge Feature prerequisite is now `MERCHANT_OPT_IN`, not
`ALWAYS_ENABLED`. COMMERCE-002 bootstraps only the global publication and must never
create or mutate `ShopFeaturePreference`; shop activation remains an explicit Recovery
Settings action. Attempt 3 must update the current partial bootstrap implementation and
fixtures accordingly and prove preference-neutrality in PostgreSQL.

COMMERCE-001 must consume exactly `@modainteract/moda-interact-shared@1.0.1`.

COMMERCE-003 remains Pending until `ARCH-023-ADMIN-003` is Complete/accepted; when it becomes executable it is pinned to the same Shared revision.


## MERCHANT_OPT_IN runtime boundary

COMMERCE-002 owns only the global publication/bootstrap state and must not read or write
`ShopFeaturePreference`. The accepted COMMERCE-001 implementation predates the
`MERCHANT_OPT_IN` architecture correction: its policy operation rechecks current plan
entitlement, while the generic authorization resolver uses shop preferences for initial
Tool eligibility. Before terminal ARCH-023 system acceptance, the runtime lookup boundary
must additionally recheck the current `ShopFeaturePreference.enabled = true` on every
`merchantKnowledge.lookup` request **after current-plan entitlement and before any source
read, embedding or pgvector query**. Missing/false preference must return without Merchant
Knowledge data and without vector work, including for a previously-created conversation
grant.

This is a separate bounded runtime reconciliation. It is not part of COMMERCE-002 Attempt
3 and must not be implemented by adding shop-preference reads to bootstrap code.

The accepted ADMIN-001 product-policy task also still documents `ALWAYS_ENABLED`; its
Admin-owned descriptor/state must be reconciled separately to `MERCHANT_OPT_IN` before
integrated rollout. COMMERCE-002 remains fail-closed and must not rewrite that Feature.

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
