# ARCH-021 Commerce Tasks

Architecture:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Assigned Agent:

`moda_commerce`

Coordinator:

`moda_architect`

## Phase 1 — real Studio service wiring and shop execution context

Phase 1 is deliberately Commerce-only. It does not introduce model/prompt persistence,
Shared contracts, Background changes or live provider execution.

| Task | Description | Status | Dependencies |
|---|---|---|---|
| [COMMERCE-001](COMMERCE-001-expose-production-connections-studio-port.md) | Expose production Connections through Studio server actions | Complete | ARCH-020-COMMERCE-020, 024, 028 |
| [COMMERCE-002](COMMERCE-002-switch-connections-routes-to-production-port.md) | Switch U15/U16 routes from fixtures to production ConnectionPort | Complete | COMMERCE-001, ARCH-020-COMMERCE-022 |
| [COMMERCE-003](COMMERCE-003-expose-studio-shop-execution-context.md) | Expose server-validated selected-shop execution context | Complete | ARCH-020-COMMERCE-013, 018 |
| [COMMERCE-004](COMMERCE-004-add-studio-selected-shop-context.md) | Add Studio-wide selected-shop URL/navigation context | Complete | COMMERCE-003 |
| [COMMERCE-005](COMMERCE-005-wire-real-connections-into-tool-authoring.md) | Wire persisted connection revisions into U06 Tool authoring | Complete | COMMERCE-001, COMMERCE-004, ARCH-020-COMMERCE-023 |
| [COMMERCE-006](COMMERCE-006-install-javascript-response-panel-production-composition.md) | Install production JavaScript response-panel composition | Complete | COMMERCE-005, ARCH-020-COMMERCE-026, 027, 031 |

## Execution frontier

COMMERCE-001 through COMMERCE-006 are architect-accepted Complete. Phase 1 has no
remaining executable implementation task.

```text
Phase 1 frontier: none — implementation set complete
```

The parent ARCH-021 Phase 1 exit criteria are reconciled. Phase 2 is materialised below. DATABASE-001, COMMERCE-007, COMMERCE-008, COMMERCE-009 and COMMERCE-011 are architect-accepted Complete. The current executable Phase 2 Commerce frontier is COMMERCE-010, COMMERCE-013 and COMMERCE-014; COMMERCE-012 remains gated on COMMERCE-010.

## Phase 1 dependency graph

```text
ARCH-021-COMMERCE-001 ─────> ARCH-021-COMMERCE-002
          |
          +------------------------------+
                                         |
ARCH-021-COMMERCE-003 -> COMMERCE-004 -> COMMERCE-005 -> COMMERCE-006
                                         ^
                                         |
                              COMMERCE-001+
```

Phase 1 is architect-accepted Complete: COMMERCE-001 through COMMERCE-006 are Complete
and the parent ARCH-021 Phase 1 exit criteria are reconciled. Phase 2 is materialised below
with DATABASE-001 as the initial Ready frontier.

## Phase 2 — model catalogue and platform/shop Agent Configuration

Phase 1 is architect-accepted Complete. Phase 2 adds the new Agent Configuration domain without
reopening the accepted Connections/shop-context/Tool-authoring composition.

| Task | Description | Status | Dependencies |
|---|---|---|---|
| [COMMERCE-007](COMMERCE-007-implement-model-configuration-service.md) | Implement model catalogue/default/shop-override service | Complete | DATABASE-001, ARCH-020-COMMERCE-002 |
| [COMMERCE-008](COMMERCE-008-implement-prompt-template-service.md) | Implement category-organised reusable prompt-template service | Complete | DATABASE-001, ARCH-020-COMMERCE-002 |
| [COMMERCE-009](COMMERCE-009-implement-prompt-lifecycle-service.md) | Implement platform/shop prompt lifecycle and active pointers | Complete | DATABASE-001, COMMERCE-008, ARCH-020-COMMERCE-002 |
| [COMMERCE-010](COMMERCE-010-resolve-effective-agent-configuration.md) | Resolve effective shop/platform model + prompt independently | Ready | COMMERCE-003, COMMERCE-007, COMMERCE-009 |
| [COMMERCE-011](COMMERCE-011-build-platform-agent-configuration-ui.md) | Build Agent Configuration shell + platform model UI | Complete | COMMERCE-006, COMMERCE-007 |
| [COMMERCE-012](COMMERCE-012-build-shop-agent-configuration-ui.md) | Build selected-shop model/prompt override surface | Pending | COMMERCE-004, COMMERCE-007, COMMERCE-008, COMMERCE-009, COMMERCE-010, COMMERCE-011 |
| [COMMERCE-013](COMMERCE-013-build-platform-prompt-template-ui.md) | Build category-organised platform prompt-template library UI | Ready | COMMERCE-008, COMMERCE-011 |
| [COMMERCE-014](COMMERCE-014-build-platform-prompt-authoring-ui.md) | Build application-wide CommerceAgent prompt authoring UI | Ready | COMMERCE-008, COMMERCE-009, COMMERCE-011 |

The current Phase 2 Commerce execution frontier on this task branch is:

```text
ARCH-021-COMMERCE-010   Ready — mandatory platform-baseline/snapshot correction
ARCH-021-COMMERCE-013   Ready — platform prompt-template library UI
ARCH-021-COMMERCE-014   Ready — platform prompt authoring UI
```

COMMERCE-009 is architect-accepted Complete after focused PostgreSQL proof of prompt draft/pointer CAS, durable same-operation replay, explicit pointer audit targets, exact template-revision copying and generation-aware shop ABA protection. COMMERCE-010 Attempt 1 has been returned to Ready for a bounded mandatory-platform-baseline and coherent-snapshot correction. COMMERCE-014 remains independently Ready from COMMERCE-008/009/011, and COMMERCE-013 remains independently Ready from COMMERCE-008/011. COMMERCE-012 remains Pending because it still depends on COMMERCE-010.

Prompt templates are platform-wide copy-on-use authoring assets in Phase 2. They are organised
under data-driven categories/classifications such as `Clothing & Fashion`; a category may contain
multiple templates. Categories are not a code enum. Using a published template revision copies
its exact text into a prompt draft and records provenance; later category/template changes do not
mutate that prompt.

Phase 2 also performs an incremental Studio decomposition. COMMERCE-011 creates the dedicated
Agent Configuration route/module and platform model UI. Once that shell exists, COMMERCE-012
(selected-shop overrides), COMMERCE-013 (template library) and COMMERCE-014 (platform prompt
authoring) are independently reviewable UI capabilities with their own service dependencies; they
must not be artificially serialized. All Agent Configuration state/actions stay outside
`StudioWorkspace`, and unrelated Studio domains are not rewritten merely to reduce file size.
