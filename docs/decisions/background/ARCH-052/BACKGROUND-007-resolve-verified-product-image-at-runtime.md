---
id: ARCH-052-BACKGROUND-007
architecture_id: ARCH-052
title: Resolve optional checkout or promoted-product image via MCP at runtime
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 50
executor: null
claimed_at: null
attempt: 2
depends_on:
- ARCH-052-BACKGROUND-008
- ARCH-052-ADMIN-002
- ARCH-052-MCP-003
- ARCH-052-COMMERCE-007
- ARCH-049-BACKGROUND-001
- ARCH-049-BACKGROUND-004
enables:
- ARCH-052-SYSTEM-TEST-001
- ARCH-052-SYSTEM-TEST-002
created: '2026-10-29'
updated: 2026-11-01
---

# ARCH-052-BACKGROUND-007: Resolve optional checkout or promoted-product image via MCP at runtime

## Architecture

Architecture ID: `ARCH-052`.

Architecture document: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`.

Coordinator: `moda_architect`. This task was materialised and claimed by the canonical launcher for Attempt 1. The mirrored task branches and dedicated parent/implementation worktrees are recorded in the Completion Report.

## Objective

Produce one **verified, standard 1125 x 600 JPEG** for the exact, currently
source-backed checkout or alternative product, store it under a **merchant-readable,
UTC-outreach-preparation-date and attempt-specific R2 object key**, and supply
**only** the verified public R2 URL to a separately approved Meta IMAGE-header
variant. Preserve the already implemented TEXT fallback. This is the optional
post-BACKGROUND-008 IMAGE enhancement, not a second outreach sender.

## Context

- Current `commerce_get_product` is the authenticated, tenant-scoped exact
  Shopify/Woo product reader; Background must not create a new hosted API or
  Commerce image proxy.
- Accepted ARCH-049-BACKGROUND-001 already provides secure bounded image fetch,
  Sharp decoding, byte verification, immutable S3-compatible R2 writes and a
  public GET/hash probe. Its writer and brand path validator **only accept**
  `shop-brands/...`; do not pass product keys to that validator or duplicate its
  security mechanics. ARCH-049-BACKGROUND-004 only resolves existing READY brand
  media; it does not process product images.
- Authoritative identities are `commerce.CheckoutRecovery.shopId`,
  `commerce.RecoveryOutreachAttempt.id`/`checkoutRecoveryId`,
  `commerce.Shop.platform`/`domain`, and for WooCommerce
  `woocommerce.WooCommerceInstallation.canonicalSiteUrl` (one per shop).
- No `CheckoutRecovery` or outreach price/coupon logic, checkout URL generation,
  new database table, new R2 bucket, new deployment service or new Shared wire
  contract is required for this product-image enhancement.

## Scope

Implement only in `moda-interact-background/` and this task document:

1. Resolve exact authenticated product/variant metadata via the published MCP
   `commerce_get_product` tool **on every IMAGE preparation/retry**, using
   its projected effective `imageUrl` after exact product/variant checks.
2. Load the trusted shop/platform/URL and persisted outreach-attempt ownership
   from PostgreSQL, never from an AI argument, untrusted product URL or customer.
3. Reuse ARCH-049 safe fetch/verification, image decoder, R2 connection/config,
   guarded immutable put, HEAD verification and public GET/hash probe. Implement
   one product-specific **contain + pad** JPEG preset and strict key validator.
4. Generate the exact key, write/verify the derivative, then bind the verified R2
   URL only to an **approved** IMAGE header; otherwise choose a separately
   approved TEXT variant or typed no-send, without blocking eligible TEXT sends.
5. Retain the selected R2 link in the established prepared/confirmed outbound
   Meta template parameters; rely on the existing
   `RecoveryOutreachAttempt.outboundMessageId -> ConversationMessage.content`
   receipt plus `sentAt` for successful-send evidence. No new media table.

**This task follows the accepted text-first BACKGROUND-008 implementation.**
It must not change Background's general Meta send admission, billing, STOP,
moderation, human handover or follow-up orchestration.

## Out of Scope

- No ShopBrand schema/media-role change, brand key migration, cross-shop image
  cache, reusable product catalogue or provider image proxy.
- No new Prisma model/migration, signed R2 URL/token, public R2 credential or
  Meta template CREATE/sample-handle upload (BACKGROUND-012 owns that).
- No checkout URL verification/generation, coupon application, price
  reconciliation, additional proactive message or unapproved template wording.
- No wholesale ARCH-049 module copy, competing logger or network call from a
  model-authored URL. Do not modify `docs/decisions/**/_index.md`.

## Requirements

### R1. Exact merchant identity and human-readable, injective namespace

**Trusted source:** Query `Shop` by recovery `shopId` and require a matching
`RecoveryOutreachAttempt` linked to this recovery, with the current matching
recovery generation. For `SHOPIFY`, use the persisted `Shop.domain` (the
registered Shopify shop domain), **not** a provider product URL or arbitrary
custom storefront hostname. For `WOOCOMMERCE`, require the active, same-shop
`WooCommerceInstallation.canonicalSiteUrl` and require its value to match the
persisted `Shop.domain`; preserve its installation path. A missing/mismatched
identity returns `UNAVAILABLE: MERCHANT_IDENTITY_UNAVAILABLE`. Never pick the
most recent merchant, infer an alias, or replace a persisted domain with an
LLM-provided value.

Define the **pure** `normalizeOutreachMerchantSite(site: string): string | null`
codec in `src/services/recovery-product-media/merchant-site-segment.ts` with
these exact operations, in order:

1. Reject an empty/over-512-byte UTF-8 input, controls, whitespace surrounding
   the value, malformed percent encoding, non-HTTPS explicit schemes, userinfo,
   non-default ports and non-public/IP/localhost hostnames. A bare hostname is
   parsed as `https://<hostname>` for namespace purposes only. The two trusted
   data sources above remain authoritative; parsing does not authenticate a
   caller-supplied hostname.
2. Use WHATWG `URL.hostname` as the **lowercase ASCII/punycode** hostname; do
   not strip `www`, do not substitute a custom storefront domain and do not
   include protocol, query, fragment or trailing `/` in the key. Reject
   decoded `/` or `\` **inside a path segment** (for example `%2F`),
   control characters and dot-only segments (`.` or `..`), including encoded
   forms. Inspect the raw path before WHATWG URL dot-segment normalization;
   reject `/a/../b`, `/a/%2E%2E/b`, and `/a/./b`, not just the
   normalized URL pathname.
3. Split the canonical path on literal `/`, remove trailing empty segments and
   reject empty **interior** segments; decode each segment with
   `decodeURIComponent` **exactly once**. Do not lowercase path segments:
   Woo/WordPress paths may be case-sensitive.
4. Encode each decoded segment as its UTF-8 bytes: keep ASCII `A-Z`, `a-z`,
   `0-9`, `.`, `_` literally; encode **every other byte** as `~` followed by two
   **uppercase hexadecimal** characters (e.g. `-` => `~2D`, `~` => `~7E`).
   Join encoded segments with a **single** `-` and prefix them with
   `<lowercase-hostname>-`. If there is no path, use the hostname alone.
   Reject a result over 512 ASCII bytes and reject any path segment over
   200 decoded UTF-8 bytes; no lossy truncation, slug collisions or fallback
   to an opaque shop database ID.
5. This encoding is deliberately injective for path segments:
   `/a-b -> myshop.com-a~2Db`, whereas `/a/b -> myshop.com-a-b`.
   Distinct stored merchant identities cannot borrow each other's R2 assets,
   even if a public domain is reassigned; each object key additionally includes
   the globally unique persisted outreach attempt ID, and all reads retain
   authoritative `shopId` checks.

**Fixed examples, required verbatim in unit tests:**

| Trusted site | Namespace |
|---|---|
| `https://myshop.com` | `myshop.com` |
| `myshop.com` | `myshop.com` |
| `https://myshop.com/myshop` | `myshop.com-myshop` |
| `https://myshop.com/myshop/` | `myshop.com-myshop` |
| `https://myshop.com/store/london` | `myshop.com-store-london` |
| `https://MYSHOP.COM` | `myshop.com` |
| `https://myshop.com/a-b` | `myshop.com-a~2Db` |
| `https://myshop.com/a/b` | `myshop.com-a-b` |
| `https://myshop.com/A` | `myshop.com-A` |
| `https://myshop.com/a` | `myshop.com-a` |

### R2. Immutable product-image object key and date semantics

Implement `buildOutreachProductObjectKey()` in
`src/services/recovery-product-media/outreach-product-object-key.ts`. It accepts
**trusted, validated** `platform`, `merchantSite`, `outreachAttemptId`,
`providerProductId`, nullable `providerVariantId`, `preparedAt: Date` and
**SHA-256 of final encoded JPEG bytes**. Its output MUST be **exactly**:

```text
outreach-products/<platform>/<merchant-site>/<YYYY>/<MM>/<DD>/<outreach-attempt-id>/p-<product-sha256>/v-<variant-sha256-or-none>/sha256-<output-sha256>.jpg
```

- `<platform>` is exactly lowercase `shopify` or `woocommerce`, derived from
  persisted `Shop.platform`, never untrusted input.
- `<merchant-site>` is exactly R1's normalized segment.
- `YYYY/MM/DD` comes from **one** injected UTC `preparedAt` clock read taken
  immediately before this IMAGE preparation; zero-pad month/day. It is the
  **media preparation date**, not proof of a successful WhatsApp send. Retries
  across midnight may create a second immutable object under the new date.
- `<outreach-attempt-id>` is the persisted globally unique
  `RecoveryOutreachAttempt.id`, validated as one safe `[A-Za-z0-9_-]{1,128}`
  segment. A new follow-up has its own attempt ID. Never substitute recovery
  ID, checkout token, customer phone, timestamp, or a merchant-supplied string.
- `p-<product-sha256>` = lowercase SHA-256 hex of the UTF-8 bytes
  `lowercasePlatform + "\0" + exactProviderProductId`.
- `v-<variant-sha256-or-none>` = literal `v-none` if the source variant ID is
  `null`, else `v-` plus lowercase SHA-256 hex of the UTF-8 bytes
  `lowercasePlatform + "\0" + exactProviderVariantId`. This safely supports Shopify
  GIDs/URL delimiters and Woo numeric IDs without raw, ambiguous path segments.
- `sha256-<output-sha256>.jpg` uses lowercase 64-character hexadecimal SHA-256
  of **transformed JPEG bytes**; output always JPEG, never `.png`.
- Reject invalid input/unsafe key and any key exceeding 1024 UTF-8 bytes;
  do not silently correct, truncate or substitute a shop-id folder. There must be **exactly ten** path components when split on `/`:
  prefix, platform, site, year, month, day, attempt, product, variant, file.

For `https://myshop.com/myshop`, an upload prepared on 31 October 2026 has
this human-browsable structure (the angle-bracketed hashes are placeholders):

```text
outreach-products/woocommerce/myshop.com-myshop/2026/10/31/attempt_7d91b/p-<64-hex>/v-<64-hex>/sha256-<64-hex>.jpg
```

### R3. Product lookup and standard 1125 x 600 JPEG processing

1. Invoke **the published exact** MCP `commerce_get_product` in the current
   authenticated shop context. Product ID and selected variant ID must exactly
   match the chosen checkout line or source-supported alternative product;
   use the `CommerceProduct.imageUrl` returned by that exact result. The
   current Woo reader chooses variation.image before product.images[0]. The
   current Shopify reader only projects `product.featuredImage`, even when a
   variant ID is requested; it does **not** project variant.image. Therefore
   this task MUST NOT fabricate or claim a Shopify variant-specific image:
   use the source-supported product featured image as fallback. A separate
   MCP contract/reader change would be required to add Shopify variant
   image precedence; do not silently extend that completed MCP task.
   No fuzzy search, LLM-created URL or cross-shop source substitution.
2. Each preparation/retry re-fetches current product facts and rechecks image
   identity/source revocation before using an R2 object. A previous READY URL
   is never an attestation for a later retry; no five-minute proof/TTL contract.
3. Use the existing ARCH-049 `createSafeImageFetcher()` (HTTPS, pinned DNS and
   socket peer, redirects rechecked, bounded bytes/deadline). Cap source at
   **10 MiB** and input decoding at **40 million pixels**; reject malformed
   source, decompression abuse and remote SVG references using the existing
   safe image security rules. Use actual decoded bytes, not Content-Type alone.
4. Add `createOutreachProductImageTransformer()` using the existing sharp media
   primitives: apply EXIF rotation, convert to sRGB, **resize 1125 x 600** with
   `fit: contain`, centred, white (`#ffffff`) padding/background, set
   `withoutEnlargement: false` (upscale/downscale allowed), flatten alpha,
   first frame only, strip metadata. Do **not** use `fit: cover` (would crop
   the product). Always encode **JPEG** with `mozjpeg`, qualities
   `[86,76,66,56,46]` in that order, stop on first <=1 MiB, otherwise use
   the smallest result, and require final size **strictly less than 5 MiB**.
   Do not claim upscaling restores lost image detail.
5. Independently decode/verify transformed bytes: JPEG magic/format, exactly
   1125x600, single frame, no EXIF/XMP/IPTC/ICC payload, SHA-256 and size
   match; reject any mismatch before writing or returning READY.
6. Reuse `shopBrand.publicMedia` public HTTPS origin/bucket and
   `merchant.knowledge.r2` worker-only R2 credentials via the current
   Background configuration readers. **Reuse only the underlying R2 transport
   and guarded immutable PUT/HEAD mechanics** from ARCH-049: its public
   `createShopBrandR2Writer` and `publicBrandImageUrl` currently reject all
   non-`shop-brands` keys. Extract the common mechanics without changing
   existing brand behaviour, and implement a distinct strict
   `outreach-products` key checker before calling them. No new bucket/secret,
   server-side URL-signed operation or new network service.
7. PUT with `IfNoneMatch: "*"`, do not overwrite a hash/key collision, HEAD and
   verify ContentType `image/jpeg`, size, sha256 metadata and immutable cache
   header. Verify the resulting configured public HTTPS URL with the existing
   safe public GET/hash probe before reporting READY. Do not build public URLs
   from merchant origins or expose credentials. Public GET may fail until the
   R2 custom domain is configured; return UNAVAILABLE rather than source URL.

### R4. Typed result, final send and failure behaviour

- Return the Background-local `READY`/`UNAVAILABLE` contract below. R2 image
  source failures and upload failures can only produce a separately approved
  TEXT fallback or typed no-send. The already-accepted TEXT-only path is not
  allowed to block waiting for the media pipeline; cap total optional media
  work by a **30,000 ms total preparation budget** (MCP exact lookup,
  source fetch, decode, R2 upload/HEAD and public probe combined). Preserve
  ARCH-049's independent 10,000 ms deadline for each safe-fetch. Once the
  total budget expires, ignore late READY results, abort cancellable work,
  emit `UNAVAILABLE: PRODUCT_IMAGE_UNAVAILABLE` with a distinct timeout
  diagnostic, and use approved TEXT/no-send. An object uploaded just before
  timeout may remain unsent; do not interpret it as a send receipt.
- Immediately before template binding, revalidate shop, recovery generation,
  outreach attempt/recipient and chosen product/variant identity. Only
  `READY.publicImageUrl` may populate an approved Meta IMAGE header; never bind
  source `imageUrl`, ShopBrand artwork, an unverified R2 URL or a prior
  attempt's URL. If no approved IMAGE revision, do not do optional image work.
- Preserve current `RecoveryOutreachAttempt.outboundMessageId` and confirmed
  `ConversationMessage.content` with actual Meta image-header link and
  confirmed `sentAt`; no new media row, second message or credit. Failure to
  send does **not** convert a successfully uploaded object into a sent outreach.
  If media was prepared on Oct 31 but delivered on Nov 1, **only** the persisted
  confirmed message timestamp describes when the customer was contacted.
- Use `@modainteract/moda-interact-shared/logging`. Log shopId, recoveryId,
  attemptId, platform, readable merchant namespace, object hash/key if safe,
  UTC preparation day, media source stage, dimensions, bytes, result and
  duration. Preserve the actual originating MCP/image/R2 error text and cause
  **after bounded sensitive-value redaction**, with a separate Moda reason
  code; do not fabricate a provider error, swallow an unexpected exception
  or log raw product source URLs, signed query, customer PII or credentials.
  Expected unavailable media should still have diagnostic provenance.

### R5. Independence from current checkout pricing (BACKGROUND-016)

Image quality/provenance and pricing are **separate guards**. BG007 must not use an R2 image, its source product catalogue price, successful upload, image timestamp, or merchant-domain R2 folder as evidence that the saved checkout unit price is still payable. Revalidate the selected **same product/variant identity** against the currently admitted attempt and the BG008/BG016 price-sensitive admission decision before IMAGE binding. If BG008 has invalidated the price-dependent offer or the recovery generation, a successfully uploaded R2 image **must not** force the send through; retain it only as an immutable unsent object and return typed no-send or an independently authorised TEXT/no-offer variant. Media failure alone may choose an approved TEXT fallback but cannot relax a failed price/discount gate. BG007 does not reimplement BG016, does not fetch prices beyond its current exact product read, and does not change the 30-second media budget.

## Work Items

- [x] Add R1 site normalizer with exact test vectors, including Woo subpaths,
      uppercase case preservation and non-colliding slash/hyphen encodings.
- [x] Add R2 key builder/strict validator with injected UTC clock, source
      identity digests, exact output hash and attempt-specific key.
- [x] Add R3 product JPEG transformer and isolated tests reusing ARCH-049
      safe-fetch and metadata validation; verify no regression to brand roles.
- [x] Extract common guarded R2 PUT/HEAD mechanics without widening brand-key
      acceptance; implement new outreach key validator, public URL and GET probe.
- [x] Implement current-shop MCP exact-product selection and R4 local
      READY/UNAVAILABLE resolver; re-check on retries and final binding.
- [x] Wire optional IMAGE variant into existing Meta template/send pipeline;
      preserve confirmed message receipt and independent TEXT fallback.
- [x] Add mocked provider, R2, clock, and shop repository tests for both
      platforms; add service-level send/fallback/receipt tests.
- [x] Record actual source provider/media exceptions with safe redaction; run
      required validation and report worktree/branch evidence.

## Interfaces / Contracts

**All new interfaces are Background-local**, not cross-service Zod or Shared
exports. In `src/services/recovery-product-media/recovery-product-image-resolver.ts`
use the following exact union (additional private dependency-injection
interfaces may be local to their owning files):

```typescript
export type OutreachProductMediaResult = Readonly<
  | {
      kind: "READY";
      shopId: string;
      checkoutRecoveryId: string;
      outreachAttemptId: string;
      productId: string;
      variantId: string | null;
      objectKey: string;
      publicImageUrl: string;
      contentSha256: string;
      width: 1125;
      height: 600;
      contentType: "image/jpeg";
      preparedAt: Date;
    }
  | {
      kind: "UNAVAILABLE";
      reason:
        | "MERCHANT_IDENTITY_UNAVAILABLE"
        | "ATTEMPT_MISMATCH"
        | "PRODUCT_IDENTITY_MISMATCH"
        | "PRODUCT_IMAGE_UNAVAILABLE"
        | "UNSAFE_IMAGE_SOURCE"
        | "IMAGE_TRANSFORM_FAILED"
        | "R2_UNAVAILABLE"
        | "PUBLIC_IMAGE_UNAVAILABLE";
    }
>;
```

`READY` is private to one current preparation, **not** a persisted proof.
The `UNAVAILABLE` reason is an internal classification, never a substitute
for originating provider errors in diagnostics.

Define/export the two **pure** helpers at their stated paths:

```typescript
normalizeOutreachMerchantSite(site: string): string | null;
buildOutreachProductObjectKey(input: Readonly<{
  platform: "SHOPIFY" | "WOOCOMMERCE";
  merchantSite: string;
  preparedAt: Date;
  outreachAttemptId: string;
  providerProductId: string;
  providerVariantId: string | null;
  contentSha256: string;
}>): string;
```

No MCP tool contract change: consume the **published**
`CommerceToolOutputs.commerce_get_product` and existing Shopify/Woo variant
identities. No new cloud media presign contract or ShopBrand READY JSON.

## Dependencies

- `ARCH-052-BACKGROUND-008` — approved **text-first** initial outreach;
  optional image enhancement depends on it, not vice versa.
- `ARCH-052-ADMIN-002` — immutable Meta-approved optional IMAGE variant.
- `ARCH-052-MCP-003` — exact authenticated product reader.
- `ARCH-052-COMMERCE-007` — published product tool.
- `ARCH-049-BACKGROUND-001` — accepted safe fetch, transform and R2 primitives.
- `ARCH-049-BACKGROUND-004` — accepted runtime READY-media binding semantics;
  do not modify its ShopBrand-only role protocol.

## Enables

- `ARCH-052-SYSTEM-TEST-001`
- `ARCH-052-SYSTEM-TEST-002`

**BACKGROUND-007 must never list BACKGROUND-008 as enabled:** BACKGROUND-008
is deliberately its prerequisite and its TEXT path remains independent.

## Acceptance Criteria

- [x] A verified R2 product image does not validate a stale checkout price, changed generation or unverified discount threshold; price invalidation prevents IMAGE and offer-bearing sends even if media preparation succeeded, while the existing approved price-neutral TEXT path remains available.

- [x] All ten positive merchant examples above and host/path negative cases
      produce exact expected slugs or null; `/a-b` and `/a/b` are distinct,
      as are `/A` and `/a`, and `www` is not silently removed.
- [x] Shopify key uses trusted persisted `Shop.domain`; Woo key uses same-shop
      `WooCommerceInstallation.canonicalSiteUrl` including path. No agent,
      source image URL or user-controlled host influences the slug.
- [x] For a fixed `preparedAt` and verified input, key bytes are exactly
      reproducible; UTC midnight, leap day, retry-after-midnight, different
      attempt IDs, null versus variant ID and cross-shop identity are tested.
- [x] Exact source product/variant and original source revocation are checked
      on every preparation/retry; a previous ready object never substitutes
      for current shop/source proof.
- [x] Transparent/portrait/tiny/oversized images produce correctly padded,
      white-background, single-frame 1125x600 JPEG below 5 MiB, or a typed
      failure. No cropping, EXIF, invalid bytes or unsafe secondary fetch.
- [x] New outreach R2 objects use the same bucket/public origin as brand, but
      strict independent `outreach-products` key shape; BRAND writer still
      accepts **only** `shop-brands` keys and passes all existing tests.
- [x] A matching public GET/hash is mandatory for READY. Missing credentials,
      output mismatch, R2 collision, wrong tenant or probe failure yields
      UNAVAILABLE and approved TEXT fallback or no-send, not original URL.
- [x] Only a real Meta-approved IMAGE variant may send the R2 public URL;
      otherwise the accepted TEXT-only path is unchanged. No duplicate
      WhatsApp send, extra conversation credit or customer-visible provider
      diagnostics.
- [x] Confirmed Meta outbound receipt contains actual image header link and
      providerMessageId/sentAt; key path date represents preparation only,
      and failed sends cannot be mistaken for successful outreach.
- [x] Original MCP/R2/media failure diagnostics survive bounded security
      redaction, with separate internal reason code and no swallowed exceptions.
- [x] No new Prisma schema, Shared contract, hosted API product proxy, R2
      bucket, separate worker or archive/index change.

## Validation

- [x] Add cross-boundary test for READY IMAGE preparation plus stale current price admission; assert no IMAGE send, no offer-bearing send, no extra credit commit, and no sentAt attribution to prepared-but-unused media.

- [x] `npx vitest run tests/unit/services/recovery-product-media` (new focused
      suite: normalizer, exact key, transformer, R2 adapter, resolver).
- [x] `npx vitest run tests/unit/services/shop-brand-media` (regression across
      the reused ARCH-049 transport/decoder/writer).
- [x] Existing Background prepared-template/Meta-send/receipt tests covering
      image header and text fallback, 30,000 ms media deadline and cancellation;
      run actual repository-declared scripts.
- [x] `npm run lint`, `npm run build`, `git diff --check`.
- [x] Integration verification with injected/fake R2 and real bytes; live R2
      public-domain smoke only when configured. Mark unavailable live checks
      **not run**, never silently claim a live public GET.

## Stop Condition

After Work Items, Acceptance Criteria and required Validation pass, complete
the report, set `status: review`, hand the implementation branch and parent
task report to `moda_architect` and STOP. Do not begin system tests, merge,
push main, or update architecture indexes.

## Implementation Notes

**Required owning repository file plan** (relative to
`moda-interact-background/`; existing paths are verified in this snapshot):

| File | Work |
|---|---|
| `src/services/recovery-product-media/merchant-site-segment.ts` (new) | R1 pure codec |
| `src/services/recovery-product-media/outreach-product-object-key.ts` (new) | R2 pure key builder/validator |
| `src/services/recovery-product-media/product-image-transformer.ts` (new) | R3 deterministic JPEG preset |
| `src/services/recovery-product-media/product-r2-writer.ts` (new) | Product-key validation + shared guarded writer transport |
| `src/services/recovery-product-media/recovery-product-image-resolver.ts` (new) | MCP exact lookup, trusted shop/attempt read, current source & READY/UNAVAILABLE |
| `src/services/shop-brand-media/{safe-fetch,image-transformer,r2-writer,metadata-verifier,public-probe}.ts` (existing) | Extract **only** reusable implementation mechanics as needed; preserve brand behaviour |
| `src/services/platform-configuration/consumers.ts` (existing) | Reuse `readShopBrandPublicMediaConfiguration` + `readR2Configuration`; no new keys |
| `src/services/recovery-template-preparation/{recovery-template-brand,recovery-template.types}.ts` (existing) | Optional approved product IMAGE binding, not ShopBrand role reuse |
| `src/services/recovery-template-integration/{automated-recovery-template.service,prepared-template-send}.ts` (existing) | Optional IMAGE/receipt integration without second sender |
| `tests/unit/services/recovery-product-media/*.test.ts` (new) | Exact site, date/key, JPEG, R2, MCP, retry, tenant cases |

Before editing read `docs/agent-vcs-ownership-policy.md`,
`docs/agent-worktree-isolation-policy.md`, the actual task preparation packet
and the existing ARCH-049 source/tests. Maintain dedicated parent and
implementation worktrees and report their Git SHAs, sync evidence and
submodule pins. Use the Shared logger. No extra implementation task or
separate service is authorised by this definition.

## Completion Report

### Status

Ready for architect review. Attempt 2 addresses the requested namespace-guard correction; the task remains in `review` and has not been accepted or merged.

### Files Changed

In `moda-interact-background`:

- Added the merchant-site namespace normalizer, strict attempt-specific product R2 key builder, product JPEG transformer, isolated product-key writer and `RecoveryProductImageResolver`.
- Reused ARCH-049 safe fetch, image verification, immutable PUT/HEAD and public GET/hash mechanisms while preserving the brand writer’s `shop-brands`-only boundary.
- Added optional approved `CHECKOUT_PRODUCT` IMAGE selection and binding with final attempt revalidation and approved TEXT fallback.
- Added resolver/key/transformer/writer tests, IMAGE/TEXT preparer tests, stale-price no-send coverage and Shared logger diagnostic assertions.
- Corrected the strict merchant-site segment guard to accept canonical uppercase path bytes and final uppercase `~XX` escapes, while rejecting malformed/noncanonical escapes, invalid UTF-8 and dot-only path segments.
- Added regressions proving normalized `/A` and `/store-` values pass the segment guard, `buildOutreachProductObjectKey()` and `isOutreachProductObjectKey()`.
- Changed no Prisma schema, Shared contract, API, bucket, worker, architecture index or downstream task definition.

### Work Completed

The resolver reads trusted Shop, Woo installation, recovery and current attempt identity; selects the exact current product/variant through the authenticated MCP `commerce_get_product`; fetches and verifies the current image; creates and verifies a white-padded 1125x600 JPEG; writes an immutable, content-hashed, UTC-dated object under `outreach-products`; and requires a matching public GET/hash before returning READY. It rechecks attempt/generation/recipient/product context before IMAGE binding. Source and persistence failures retain bounded, redacted diagnostics through the Shared logger.

The send path binds the URL only to an approved IMAGE registration frozen as `CHECKOUT_PRODUCT`. Missing or stale product media falls back only to an independently approved TEXT variant. A stale price-sensitive admission still prevents IMAGE and offer-bearing sends after successful preparation; no receipt, credit commit, or sentAt attribution is created for unused media.

Attempt preparation evidence: launcher claim commit `c4e27437d587494cb3216cefb8fe4e2f4aa2797c`; parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-052-BACKGROUND-007` began at `b928728edcf9ade7a3fbebfce37c031364efc655`; implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-052-BACKGROUND-007` began at `d144efc4c77415280523719b168e8b1c8feeb486`. Both were dedicated `task/ARCH-052-BACKGROUND-007` worktrees with the task/dependency synchronization performed by the canonical launcher. Required dependencies were Complete. The Background `database` submodule was ready at `7c377282aa5819b3008b7d7f3018f44f4161523e`.

While execution was in progress, Background `origin/main` advanced to `0c08cf55a260723d563212b8a8292e9e9d9a37ea`; the task branch was fast-forwarded to that commit before final revalidation. Implementation is committed and pushed as `17961151846e3b6d92225ceb564556a9949fc22b` on `task/ARCH-052-BACKGROUND-007`.

Attempt 2 launcher evidence: claim commit `0697d715cb4d2b167d25b326f38b70b52c7fe5d4` was pushed before execution. Parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-052-BACKGROUND-007` was synchronized at `6e62d9a1f8e7d50b64be538f713697129213548a`; implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-052-BACKGROUND-007` was synchronized at `17961151846e3b6d92225ceb564556a9949fc22b`. The launcher reported both task branches already current, all dependencies Complete and recursive submodules ready; `database` remained pinned at `7c377282aa5819b3008b7d7f3018f44f4161523e`.

Architect correction disposition: implemented in `src/services/recovery-product-media/merchant-site-segment.ts`; fixed-vector regressions in `tests/unit/services/recovery-product-media/merchant-site-segment.test.ts` and key-construction/guard regressions in `tests/unit/services/recovery-product-media/outreach-product-object-key.test.ts`. Implementation commit `690c39301da0c7c713822eb08fc6358a6f0691f4` was pushed to `task/ARCH-052-BACKGROUND-007`.

### Validation Results

Attempt 1 validation before the requested correction passed:

- `npx vitest run tests/unit/services/recovery-product-media tests/unit/services/shop-brand-media tests/unit/services/recovery-template-preparation tests/unit/services/recovery-template-integration tests/unit/services/checkout-recovery/recovery-initiation.service.test.ts` — 23 files, 259 tests.
- The focused coverage includes both merchant platforms, exact product identity, retries and revocation, date/key vectors, real image bytes with injected R2/probe ports, approved IMAGE binding, unavailable/stale TEXT fallback, 30-second deadline cancellation, and stale price admission blocking an already prepared IMAGE/offer before send or receipt/credit attribution.
- `npm run lint` — passed.
- `npm run build` (including Prisma client generation and TypeScript compilation) — passed.
- `git diff --check` — passed.

Attempt 2 correction validation passed:

- `npx vitest run tests/unit/services/recovery-product-media/merchant-site-segment.test.ts tests/unit/services/recovery-product-media/outreach-product-object-key.test.ts` — 2 files, 50 tests.
- `npm run lint` — passed.
- `npm run build` (including Prisma client generation and TypeScript compilation) — passed.
- `git diff --check` — passed.

Live R2 credentials/public-domain smoke was not run. The R2 write and public GET/hash path were validated with injected fake ports and real transformed JPEG bytes; no live public GET is claimed.

### Deviations

The required product-image deadline and cancellation checks were added to the isolated resolver suite. IMAGE/TEXT selection and fallback were tested through the existing `RecoveryTemplatePreparer`; the current-price no-send fence was tested through the existing recovery initiation service. Live R2 verification remains unrun because this task environment did not provide a configured live R2 smoke setup.

### Assumptions

Existing BG008/BG016 admission remains authoritative for current price and discounts. The current selected product/variant image is only media evidence and is never treated as offer or price evidence.

### Unresolved Issues

None known. Live R2 public-origin behavior remains to be verified in a configured environment if required by architect review.

### Architectural Concerns

Report discovered cross-repository/credential/provider-proof issues to `moda_architect`.


## Architect Review

### Review Status

Accepted

### Review Notes

The namespace guard now accepts the canonical output grammar from `normalizeOutreachMerchantSite()`: preserved uppercase path bytes and final uppercase `~XX` escapes. It rejects lowercase/malformed escapes, noncanonical escaped literal bytes, invalid UTF-8, path separators, controls, and dot-only segments. Regressions prove normalized `/A` and `/store-` pass the segment guard and both object-key construction and validation. The original implementation also satisfies the trusted source identity, exact key/date/hash, bounded image processing, immutable R2 write and public verification, approved IMAGE binding, and TEXT fallback requirements based on inspected code and the Attempt 1 report.

### Reviewed Files

- `src/services/recovery-product-media/merchant-site-segment.ts`
- `src/services/recovery-product-media/outreach-product-object-key.ts`
- `src/services/recovery-product-media/recovery-product-image-resolver.ts`
- `src/services/recovery-product-media/product-image-transformer.ts`
- `src/services/recovery-product-media/product-r2-writer.ts`
- `src/services/recovery-template-preparation/recovery-template-preparer.service.ts`
- `tests/unit/services/recovery-product-media/merchant-site-segment.test.ts`
- `tests/unit/services/recovery-product-media/outreach-product-object-key.test.ts`
- `tests/unit/services/recovery-product-media/recovery-product-image-resolver.test.ts`

### Validation Reviewed

Reviewed Attempt 2 correction validation: 50 focused tests across the namespace and key suites, lint, build, and `git diff --check` passed. Attempt 1's broader 259 focused tests also passed before the isolated guard change. Live R2 public-origin smoke was not run because no live R2 smoke configuration was available; the report records fake R2 ports and real transformed JPEG bytes. No tests were rerun during this review.

### Architecture Conformance

Accepted. The implementation preserves the trusted merchant identity boundary, injective path encoding, attempt-specific immutable object keys, safe image processing, separate product R2 key guard, current-product revalidation, approved IMAGE-only URL binding, and TEXT fallback.

### Follow-up

No dependent task is newly eligible. `ARCH-052-BACKGROUND-017` remains Pending because `ARCH-052-ADMIN-004` is Ready; `ARCH-052-SYSTEM-TEST-001`, `ARCH-052-SYSTEM-TEST-002`, and `ARCH-052-SYSTEM-TEST-004` remain gated by their other prerequisites.
