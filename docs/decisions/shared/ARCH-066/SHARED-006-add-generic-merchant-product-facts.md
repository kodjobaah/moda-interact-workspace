---
id: ARCH-066-SHARED-006
architecture_id: ARCH-066
title: Add generic merchant product facts without breaking options contracts
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: pending
priority: 50
executor: null
claimed_at: null
attempt: 0
depends_on: ["ARCH-066-SHARED-003"]
enables: ["ARCH-066-SHARED-004", "ARCH-066-SHARED-005"]
created: 2026-11-08
updated: 2026-11-08
---
# Add generic merchant product facts without breaking options contracts

## Authority and owned touch points
Read [consumer contract](../../../architecture/ARCH-066-consumer-contract.md) sectionsA–C/E. Own Shared only: src/commerce/schemas.ts, index.ts, NEW product-facts.ts/product-facts.test.ts, src/commerce/presentation/{schemas,compose,index}.ts, NEW presentation/facts.ts and fact-messages.ts/tests, runner/tool-execution.ts and canonical product normalization tests, package.json/lockfile for pinned parser. No publishing or service edits.

## Exact additive data contracts
Retain all accepted5.6.0 fields and PRODUCT_OPTIONS renderer/selection semantics. Add optional CommerceProductSchema fields:

```ts
description: {
  status: 'AVAILABLE'|'NOT_PROVIDED'|'PARTIAL'; text: string
}
attributes: {
  status: 'AVAILABLE'|'NOT_PROVIDED'|'PARTIAL';
  items: Array<{name: string; values: string[]}>
}
```

Export strict CommerceProductDescriptionSchema and CommerceProductAttributesSchema, with normalization helpers normalizeCommerceProductDescription(source,format) and normalizeCommerceProductAttributes(source). Inferred types only; no z.custom. Description normalized text<=4096 Unicode code points; explicit absent/empty input=>NOT_PROVIDED text='', complete nonempty=>AVAILABLE, clipped/malformed source=>PARTIAL. NOT_PROVIDED must be empty. Raw input>65536 UTF8 bytes=>PARTIAL empty. format is PLAIN_TEXT or HTML, never guessed from characters. Plain text trims, CRLF->LF, collapses horizontal whitespace and>2 consecutive newlines to2; disallowed controls omit and mark PARTIAL. Truncate description by Unicode code points and mark PARTIAL, never split surrogate pairs. Legacy missing optional field stays absent, not verified absence.

For HTML use exact parse5@8.0.1 dependency with locked integrity and parseFragment. Walk text nodes in order; skip script/style/template/noscript subtrees entirely; br/p/div/li/ul/ol/h1..h6/table/tr boundaries emit newline; ignore all attributes/URLs and comments; parser decodes entities. Apply same text normalization/bounds. No HTML execution, raw HTML return, regex-only stripping or product-type inference. HTML helper is provider normalization, not a model reply renderer.

Attributes: max16 items; name trimmed1..128 code points; max64 distinct values per item, each trimmed1..128. CR/LF/tab become spaces; collapse whitespace. Omit empty/invalid/overlong strings rather than altering factual units/labels; mark PARTIAL when omitted/truncated collections. Exact duplicates removed in provider order; equal name items merge values preserving first-name order. Missing/empty source=>NOT_PROVIDED empty items; AVAILABLE complete nonempty; NOT_PROVIDED contradictory nonempty=>PARTIAL, not data deletion. Non-string names/values omitted and PARTIAL. Expose open labels only; no size/colour/species enums, aliases or prose extraction. Shared helper accepts canonical {name,values} objects; native mapping belongs to consumers.

## Exact presentation contract
Add CommerceProductFactSchema {productId,variantId,title,description,attributes,options,selectedOptions}; identity/title bounds existing; new fields nonoptional in verified facts, with legacy absent description/attributes projected PARTIAL empty (unknown), not NOT_PROVIDED.

Export verifyCommerceProductFacts(selection,currentProducts) with the exact selection rules/return discriminants of verifyCommerceOptionFacts but productFacts instead of optionFacts. max3 distinct exact pairs; duplicate/invalid => limitation INVALID_SELECTION, absent/ambiguous exact pair=>PRODUCT_NOT_FOUND, malformed product=>PRODUCT_INVALID. Caller proves tenant/provider/currentness. No title guessing.

Extend CommerceVerifiedPresentationSchema with optional productFacts max3 default empty and additive PRODUCT_DETAILS disposition. Existing accepted callers parse without changes. PRODUCT_DETAILS requires nonempty productFacts, no simultaneous optionFacts/products; invalid combinations refuse INVALID_INPUT. PRODUCT_OPTIONS remains unchanged. Final-response model details remain generic validated profile data; consumers explicitly publish productDetailSelections as per consumer contract.

Render PRODUCT_DETAILS as plain text per product: title, nonempty merchant description, then every attribute as 'label: values', then selectedOptions under localized selected label. Append option labels not already present in attributes (exact label+values equality); never repeat identical fact lines. Missing all facts=>localized details unavailable. PARTIAL field emits localized incomplete-information line once per product. NOT_PROVIDED means field unavailable, never 'product has no size'. Preserve labels/units verbatim as inert text. No merchandise-specific formatting. Use existing full/first-product/minimal complete candidates, wrapper/locale/referral precedence and4096 bounds; minimal truthful unavailable line. Add translated details-unavailable/incomplete/selected labels for all existing supported locales, preserving legacy goldens.

Retain normalized canonical products at runner/tool-execution boundary before profile validation, model history/evidence/context updates, as accepted001 does for options. Malformed mandatory original product fields remain fatal; bounded malformed new optional fields normalize to PARTIAL without mutating original provider objects. No new grant/feature key/schema version.

## Required acceptance evidence
- [ ] Legacy5.6.0 product/options/context/presentation fixtures still parse and render identically.
- [ ] HTML/entity/control/Unicode/bounds, exact label merge/dedup, missing/partial/new facts, no inference fixtures.
- [ ] Both platform mappings use one canonical helper contract; clothing/nail varnish/trees/custom label fixtures use same schemas/renderer.
- [ ] Runner-boundary test captures actual normalized next-model payload/evidence, not only helper output.
- [ ] New disposition/invalid combinations, exact-ID selector, localized output and complete wrapper candidate bounds.
- [ ] Typecheck, focused tests, build, existing entrypoint/presentation validators and pack public-import checks. Record actual scripts and unavailable lint honestly. SHARED-005 publishes accepted source, not this task.

## Execution record
Pending, Attempt0/unclaimed. Definitions only; preserve unrelated work. No completed task reopened or immutable version changed.
