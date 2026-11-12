---
id: ARCH-073
title: Tenant-specific recovery shop headers and optional logos
status: in_progress
coordinator: moda_architect
created: 2026-11-12
updated: 2026-11-12
---

# ARCH-073: Tenant-specific recovery shop headers and optional logos

## Status / Problem

In Progress. Recovery messages need clear tenant shop-name/website branding and an optional actual shop logo where WhatsApp supports one. Current baseline text functionality is deployed; final logo consumer review/integration is underway. A standalone approved logo and genuine production logo delivery remain operational gates, not assumed success.

## Goals / Non-Goals

Use stored authenticated shop name and verified tenant website in eligible AI/HUMAN/service replies, retaining the trusted checkout footer. Use only current verified LOGO/SQUARE_LOGO media when a single image caption is appropriate. Never invent merchant identity, use a cover/banner as logo, overwrite an existing verified product image, send an extra logo message or truncate full text/checkout URL. Preserve consent/security/control/ordering/admission and human-authored bytes. No new database schema, credential/channel/scope grant or infrastructure is required by the accepted route.

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
| ARCH-073-BACKGROUND-004 | moda_background | In Progress |

Dependency graph: basic-name acceptance -> text-header and public-source tasks; additive Shared acceptance -> explicit authorized publication; logo consumer depends on accepted header, public source and publication. Repository tasks are authoritative for execution state.

## Rollout / Validation / Completion Gate

PRODUCTION / COMPATIBLE ROLLOUT. Basic-name source, supported public asset source and text header are merged/deployed. Genuine automatic name capture was verified without manual backfill. Public asset runtime reports controlled CHANNEL_LOCKED; that is not proof of logo readiness. Text-header replacement worker/drain and production read-only preparation preview passed, but preview is not a Meta delivery claim.

After final consumer acceptance developer merges source, pins actual Shared/Background main commits and deploys. Drain old messaging workers before creating incompatible new HUMAN/media evidence; do not rewrite historical records or queue payloads. Old readers may refuse new BRAND_IMAGE, while new readers retain old plans. Rollback requires stopping new-format preparation and draining incompatible work; no silent downgrade of frozen media.

Focused/unit, real PostgreSQL identity/receipt/source/control/policy races, types/scoped lint/declared build and exact-head CI are required. A same-repository bounded mechanism uses developer genuine integrated verification rather than a separate system-test task. Final architecture remains In Progress until operationally approved asset readiness and real logo delivery/fallback behavior are honestly verified. User is providing a standalone asset; a marketing banner is not implicitly approved. Any one-time administrator-observed source bootstrap must use existing canonical observation/processing, never fabricated READY/provenance or an undocumented customer asset bypass.

## Change History / Open Questions

- Basic shop-name and text headers proceeded independently of logo permission assumptions.
- Unsupported historical Admin contract replaced after schema evidence with stable public Storefront route.
- Additive Shared5.13.7 source/release accepted with explicit public publication authorization.
- Review added original restart/header receipts, same-row policy revision/identity fences and preserved HUMAN admission policy; no schema or cross-service envelope expansion.
- Remaining operational question: approved standalone logo/source readiness and genuine Meta delivery. No production logo success is yet claimed.
