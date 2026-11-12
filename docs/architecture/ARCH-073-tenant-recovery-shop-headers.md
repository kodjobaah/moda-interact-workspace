---
id: ARCH-073
title: Tenant-specific recovery shop headers and optional logos
status: implemented
coordinator: moda_architect
created: 2026-11-12
updated: 2026-11-12
---

# ARCH-073: Tenant-specific recovery shop headers and optional logos

## Status / Problem

Implemented. Tenant-specific name/website headers, trusted checkout footer and optional verified logo delivery are deployed and integrated. All six source/release tasks are accepted. Genuine production image delivery and read status passed using the complete banner explicitly approved by the user as a temporary shop-logo test asset. That authorization supersedes the earlier standalone-only operational gate; it does not authorize automatic cover/banner substitution for other shops.

## Goals / Non-Goals

Use stored authenticated shop name and verified tenant website in eligible AI/HUMAN/service replies, retaining the trusted checkout footer. Use only current verified LOGO/SQUARE_LOGO media when a single image caption is appropriate. Never invent merchant identity, automatically substitute cover art or an unapproved banner as logo, overwrite an existing verified product image, send an extra logo message or truncate full text/checkout URL. Preserve consent/security/control/ordering/admission and human-authored bytes. No new database schema, credential/channel/scope grant or infrastructure is required by the accepted route.

## Inspected Architecture / Repository Responsibilities

Background owns basic Shopify shop-name acquisition, public brand-source acquisition, recovery composition and frozen delivery. Preserved historical ARCH049 source was not in main; selective reuse corrected stale token/domain-lock assumptions. Basic name uses current selected-Shop-ID authenticated Admin shop.name and independent durable shopifyNameSync. Media source owns independent shopifySourceSync, preserving name and media metadata under Shop/Brand locks.

Stable Admin2026-07/2026-10 reject historical Shop.brand/QueryRoot.branding. The validated supported source is stable tokenless Storefront2026-07 public brand metadata from the exact installed shop domain, with no cookies/credentials/read_brand request. Public source provenance is labelled honestly. CHANNEL_LOCKED, partial response and provider errors preserve known media; only complete validated successful observations mark explicit absence. Existing guarded source/generation/fingerprint/fetch/transform/R2/READY pipeline remains canonical.

Shared owns additive browser-safe SHOP_BRAND/BRAND_IMAGE provenance, schema and digest exports under @modainteract/moda-interact-shared/commerce/presentation. Existing TEXT/product IMAGE contracts and digests remain unchanged. Accepted source merge46834ef32a945606c92feade5924564ce325b326 is published as5.13.7; canonical downloaded521753-byte artifact SHA2567d1e115255e2f431d4ad302121edbd34ed81a87fa5b50c466379bb3900d3a623 matches accepted bytes. Background consumes the published package, never sibling source.

## Flow / State / Contracts

Bounded recovery-worker scan -> durable per-Shop source claim -> bounded provider read outside transactions -> locked active Shopify tenant/domain/installation check -> existing ShopBrand metadata -> eligible reply name/site header -> complete body and divider/checkout footer -> optional verified media -> immutable preparation/moderation -> final permit -> identical provider body/plan.

Name/site/divider header derives only from verified local context. Missing/unsafe name falls back to verified website without guessing/suppressing a legitimate reply. Configured pure-identity header tokens may deduplicate; custom prose and staff-authored content remain intact. Old receipt-absent applications/commands replay original bytes, never automatically gaining branding.

Optional image policy: verified product IMAGE always wins; otherwise choose LOGO then SQUARE_LOGO only. Complete caption must fit1024 Unicode codepoints; missing/unready/unsafe/config-unavailable/overlong media uses complete TEXT before freeze, never extra send or late downgrade. Official Meta image object accepts one image link/id plus caption: https://whatsapp.github.io/WhatsApp-Nodejs-SDK/api-reference/types/ImageMediaObject/ . No HTML inline logo is claimed.

New BRAND_IMAGE uses strict Background-local versioned envelope in existing outboundPresentation/preparedWrapperEvidence JSON with plan/digest, original ownership receipt, header receipt and policy reference. Legacy raw TEXT/product IMAGE stays unchanged. MESSAGE ownership is captured before media preparation and rehydrated on restart, never recaptured after takeover. HUMAN_COMMAND binds durable command/lease/control revision; a new customer inbound alone does not add a new human rejection gate. Physical IMAGE transport retains caption TEXT record semantics so merchant inbox text is not lost.

## Consistency / Security / Failure

Final Shop/Brand-ordered permit checks same tenant/domain/current READY source generation/fingerprint/key/content and stored header identity. The authoritative public-origin policy rowId/version/value comes from the same canonically validated local configuration snapshot; logo requires rowId, while existing default/legacy config consumers remain compatible. Final network-free transaction checks actual runtime environment/fixed shopBrand.publicMedia row identity/version FOR SHARE; delete/recreate/reset-version or changed policy refuses. No generic decoder is duplicated in transactions. Configuration writer lock ordering is compatible.

Immutable body/media, moderation hash, original receipt and final provider permit remain identical. Stale/malformed/tampered proof refuses without re-rendering or changing image/text after freeze. Approved Meta templates retain approved payload and checkout binding. Unbound routing cannot infer basket/shop identity; STOP/blocked/consent/security prohibitions remain. No new authorization comes from self-declared media schema/URL.

## Scale / Observability / Infrastructure

Bounded keyset scans/leases/backoff and current-token service are reused; no per-message Shopify read or broad conversation serialization. Existing shared structured logger emits bounded semantic reason codes; no competing generic logger/metric. No Gateway/topology/env or new observability task is needed. Public evidence contains coarse outcomes, not customer/provider operational identifiers.

## Decisions / Tasks

| Task | Owner | State |
|---|---|---|
| ARCH-073-BACKGROUND-001 | moda_background | Complete |
| ARCH-073-BACKGROUND-002 | moda_background | Complete |
| ARCH-073-BACKGROUND-003 | moda_background | Complete |
| ARCH-073-SHARED-001 | moda_shared | Complete |
| ARCH-073-SHARED-002 | moda_shared | Complete |
| ARCH-073-BACKGROUND-004 | moda_background | Complete |

Dependency graph: basic-name acceptance -> text-header and public-source tasks; additive Shared acceptance -> explicit authorized publication; logo consumer depends on accepted header, public source and publication. Repository tasks are authoritative for execution state.

## Rollout / Integrated Validation

PRODUCTION / COMPATIBLE ROLLOUT. All six source/release tasks are accepted and merged. Background main `51043bfe8ba62ac11f10acdf9f7f28c7d7bd60cf` and Shared main `46834ef32a945606c92feade5924564ce325b326` are pinned by merged parent integration PR989. Production rollout is Live; predecessor messaging worker stopped and surviving worker repair cycles are healthy. Old frozen records remain unchanged. Rollback requires stopping new-format preparation and draining incompatible readers/work; no silent downgrade of frozen media.

Repository proof includes focused compatibility and media tests, real PostgreSQL source/control/lease/header/policy identity races, types/scoped lint/build and final exact-head CI. This bounded same-repository mechanism uses genuine developer integrated validation rather than a separate system-test task. No database migration, new infrastructure, scope grant or credential/channel change was needed.

Production automatic shop-name acquisition passed without manual name backfill. Stable public asset acquisition remains subject to CHANNEL_LOCKED on the development store, with known media preserved. This limitation was resolved for the authorized test through an administrator-observed source path: the user approved the complete banner temporarily and personally saved it as Shopify default logo. Root verified the actual shop's default asset and public provider media identity, then registered it through the canonical guarded source-observation ingress. The existing production safe-fetch/transform/R2/verification worker produced current READY LOGO media. No READY state or provider identity was fabricated, and no unsupported Admin API, new permission, Storefront credential or password unlock was used.

Read-only production preparation selected BRAND_IMAGE/LOGO with the saved shop name, verified website, both dividers, preserved authored text and exact stored checkout footer. The complete caption fit the image limit. An authenticated Shopify merchant queued one authorized test reply to the dedicated test recipient. Actual frozen RECOVERY_BRAND_MEDIA evidence contained BRAND_IMAGE/LOGO with the exact verified R2 origin/key and matching source generation/content identity. Provider caption matched the saved body, header and checkout footer. Meta delivery and read status succeeded without provider failure, independently corroborated by the merchant UI. Exactly one image reply was sent; a preview or text fallback was not counted as image success.

Detailed customer/provider identifiers, exact private timestamps, recipient information and checkout/media URLs remain protected outside public documentation. Public acceptance records coarse outcomes only.

## Decisions / Remaining Non-blocking Follow-up

The complete banner is an explicitly authorized temporary test asset, not a newly invented standalone logo or permission to repurpose other imagery. A future standalone asset can replace it through the same verified source/READY pipeline. Product image priority, missing-media full-text fallback and LOGO/SQUARE_LOGO role restrictions remain the generic policy. The public Storefront CHANNEL_LOCKED limitation remains transparent; this test proves the authorized observed-source pipeline and actual delivery, not that every locked storefront exposes public branding.

No blocking architecture question remains. ARCH-073 is Implemented.

## Change History

- Basic shop-name and text headers proceeded independently of logo acquisition assumptions.
- Unsupported historical Admin contract was rejected after schema evidence; stable tokenless Storefront became the supported public source.
- Additive Shared5.13.7 source/release was accepted and explicitly authorized for public publication.
- Review added original ownership/header restart evidence, same-row policy identity/version fences and preserved HUMAN admission policy; no schema or cross-service envelope expansion.
- Final consumer `3982f109c1d593cbdc6d2ca9125ccbef496f09a7` was accepted after exact-head CI and affected PostgreSQL snapshot assertions passed; developer merged PR210 and parent PR989.
- User-authorized temporary complete-banner source passed canonical production READY processing and genuine single-image merchant send, Delivered/Read and exact frozen-caption/header/footer checks. The earlier standalone-only gate is superseded by that explicit test authorization.
