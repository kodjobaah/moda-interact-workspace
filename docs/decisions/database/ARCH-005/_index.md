# ARCH-005 — Database Tasks

| Task | Description | Status | Dependencies |
|---|---|---|---|
| ARCH-005-DATABASE-001 | Persist merchant and conversation international context | Complete | SHARED-001 |
| ARCH-005-DATABASE-002 | Persist locale-aware WhatsApp template variants | Complete | DATABASE-001 |

Immediate executable Database task:

```text
None — ARCH-005 Database tasks are complete.
```


## Architect review — DATABASE-001 attempt 1

```text
Changes Requested
```

Schema and migration are accepted in principle. Regenerate the repository ERD
artifacts so generated documentation matches the new Prisma schema.

Current execution:

```text
ARCH-005-DATABASE-001   Ready — ERD regeneration correction
ARCH-005-DATABASE-002   Pending
```


## Architect review — DATABASE-001 attempt 2

```text
Accepted
```

Current Database state:

```text
ARCH-005-DATABASE-001   Complete
ARCH-005-DATABASE-002   Ready
```


## Architect review — DATABASE-002 attempt 1

```text
Changes Requested
```

The catalogue shape is accepted in principle. Before acceptance, DATABASE-002
must enforce two distinct invariants:

```text
provider identity
  shop/account/purpose/providerTemplateName/providerLanguageCode

selectable identity
  at most one APPROVED + enabled row for
  shop/account/purpose/canonical languageTag
```

The selectable invariant must be a predicate-aware database constraint (normally
a PostgreSQL partial unique index), so pending/disabled replacement variants may
coexist with the currently selectable template.

The same canonical task is Ready for correction. MESSAGING-001 remains gated
until architect acceptance.


## Architect review — DATABASE-002 attempt 2

```text
Accepted
```

Both provider-record identity and selectable-template identity are now enforced.
The follow-up migration preserves the already-applied Attempt 1 migration and
allows staged non-selectable replacement variants.

Current Database state:

```text
ARCH-005-DATABASE-001   Complete
ARCH-005-DATABASE-002   Complete
```

Dependency note:

```text
ARCH-005-MESSAGING-001 remains Pending
  because ARCH-005-BACKGROUND-001 is still Pending.
```
