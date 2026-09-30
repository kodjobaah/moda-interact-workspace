---
id: ARCH-023-BACKGROUND-002
architecture_id: ARCH-023
title: Acquire Merchant Knowledge web pages safely
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 31
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-023-BACKGROUND-001
enables:
  - ARCH-023-BACKGROUND-004
created: 2026-09-29
updated: 2026-09-30
---

# Acquire Merchant Knowledge web pages safely

## Architecture

Architecture ID: `ARCH-023`

Architecture document: `docs/architecture/ARCH-023-merchant-knowledge.md`

Coordinator: `moda_architect`

## Objective

Implement the `WEB_PAGE` acquisition adapter only: SSRF-safe HTTPS retrieval, redirect/DNS/connected-peer validation, bounded decompression, media-type validation and deterministic human-visible HTML/plain-text extraction.

This task returns extracted source text through the BACKGROUND-001 `MerchantKnowledgeWebPageAcquirer` contract. It does not normalize, truncate, chunk, embed or persist semantic content.

## Scope

Authorized primary files:

```text
package.json
package-lock.json

src/services/merchant-knowledge-web-page-acquirer.ts
src/services/merchant-knowledge-network-policy.ts
src/services/merchant-knowledge-html-extraction.ts

tests/unit/services/merchant-knowledge-network-policy.test.ts
tests/unit/services/merchant-knowledge-html-extraction.test.ts
tests/unit/services/merchant-knowledge-web-page-acquirer.test.ts
```

Use Node built-ins for DNS, TLS/HTTPS, decompression and timing. Add only the HTML parser dependency required by this task.

## Out of Scope

- BullMQ worker orchestration.
- R2.
- CSV/XLSX.
- database writes.
- normalization/content units.
- chunking.
- embeddings.
- pgvector.
- entitlement reconciliation.
- automatic crawling/scheduled refresh.
- JavaScript execution/headless browser.
- authentication/cookies sent to merchant sites.

## Requirements

### R1 — exact request policy

`MerchantKnowledgeWebPageAcquirer.acquire({requestedUrl})` must enforce:

```text
URL length <= 2048 Unicode/code-unit characters as supplied
scheme exactly https:
no username
no password
maximum 5 redirects
overall acquisition deadline 10_000 ms
maximum decompressed body 1_048_576 bytes
accepted media types exactly:
  text/html
  text/plain
```

The media type comparison ignores parameters such as `charset=UTF-8` but no other MIME type is accepted.

Do not downgrade to HTTP.

### R2 — exact destination validation

Validate the initial URL and every redirect independently.

For hostname destinations:

1. resolve all current A/AAAA answers;
2. reject if resolution returns no addresses;
3. reject the hostname if **any** returned address is non-public;
4. sort validated answers deterministically by:
   ```text
   family ASC (IPv4 before IPv6), address lexical ASC
   ```
5. select the first address for that request;
6. bind the actual HTTPS connection to that selected address via a custom lookup/connection path while preserving the original hostname for TLS SNI/certificate verification;
7. after connection, require the socket peer address to equal the selected validated address.

For an IP-literal hostname:

1. validate that literal directly;
2. connect only to that validated literal.

Every redirect repeats the full algorithm. Do not reuse the prior redirect target's DNS decision.

### R3 — public-address policy

Use a tested IP parser/classifier rather than regular-expression range detection.

Permitted destination:

```text
globally routable unicast only
```

Reject at minimum:

```text
IPv4/IPv6 unspecified
loopback
private
link-local
unique-local
carrier-grade NAT
multicast
broadcast
reserved/documentation/special-use
IPv4-mapped IPv6 when mapped IPv4 is not public
cloud/link-local metadata addresses including 169.254.169.254
```

If a hostname resolves to one public and one denied address, reject the hostname entirely.

### R4 — no credential propagation

Requests must send no:

```text
Authorization
Cookie
Proxy-Authorization
Shopify session
Moda service token
R2 credential
```

Use only a bounded generic User-Agent plus ordinary `Accept`/`Accept-Encoding` headers required by this implementation.

Do not forward headers from the merchant browser or another application request.

### R5 — redirect rules

Follow only standard redirect statuses:

```text
301
302
303
307
308
```

A redirect must contain a valid absolute or relative `Location`.

Resolve relative `Location` against the current URL, then re-run R1-R3.

More than 5 redirects is a permanent acquisition error.

### R6 — compressed response handling

Support only:

```text
identity / absent Content-Encoding
gzip
deflate
br
```

Unknown/multiple unsupported encodings fail permanently.

The 1 MiB bound applies to **decompressed bytes**. Abort the stream as soon as the bound would be exceeded.

Do not buffer an unbounded compressed or decompressed response.

### R7 — response status

Only HTTP status:

```text
200
```

is a successful source response after redirects.

Treat:

```text
408
425
429
500
502
503
504
connection reset
DNS temporary failure
request deadline
```

as transient acquisition failures.

Treat other final non-200 statuses as permanent acquisition failures.

Export bounded error classes/codes so BACKGROUND-004 can distinguish transient from permanent failures without parsing error-message text.

### R8 — deterministic HTML extraction

For `text/plain`:

1. decode UTF-8 with replacement for malformed sequences;
2. return the decoded text unchanged except no normalization performed here.

For `text/html`, parse HTML without executing anything.

Ignore entire subtrees for:

```text
script
style
noscript
template
iframe
svg
canvas
```

Also ignore elements with:

```text
hidden attribute
aria-hidden="true"
```

Do not fetch:

```text
script src
iframe src
stylesheet
image
font
media
CSS
```

Traverse the remaining DOM in document order.

Append text-node content in order.
Insert exactly one LF boundary before/after common block elements:

```text
address article aside blockquote br div dl dt dd fieldset
figcaption figure footer form h1 h2 h3 h4 h5 h6 header hr
li main nav ol p pre section table tbody td tfoot th thead tr ul
```

Collapse is **not** performed here; BACKGROUND-004 owns D3 normalization.

Return the raw extracted sequence.

### R9 — acquisition result shape

Success returns:

```ts
{
  contentType: "text/html" | "text/plain";
  extractedText: string;
  resolvedUrl: finalUrl.toString();
  fetchedAt: Date;
}
```

`resolvedUrl` is the final post-redirect public HTTPS URL.

Never return response headers wholesale.

### R10 — focused adversarial tests

Tests must prove:

```text
http: rejected before request
userinfo rejected
URL > 2048 rejected
loopback literal rejected
private literal rejected
link-local metadata rejected
IPv6 loopback/unique-local rejected
hostname with any denied DNS answer rejected
custom connection uses validated selected address
connected peer mismatch rejected
each redirect is re-resolved/revalidated
redirect to private target rejected before connection
6th redirect rejected
overall deadline enforced
decompressed > 1MiB rejected
unsupported content encoding rejected
unsupported MIME rejected
final 404 permanent
final 429 transient
final 503 transient
scripts/styles/iframes excluded
relative subresources never fetched
text order deterministic
plain text preserved for later normalization
```

Tests must use local controlled servers/fakes; no external internet dependency.

## Work Items

- [ ] Implement public-IP classification.
- [ ] Implement DNS resolution and connection binding.
- [ ] Implement redirect-safe HTTPS fetch.
- [ ] Implement bounded decompression/media validation.
- [ ] Implement deterministic HTML/plain-text extraction.
- [ ] Implement transient/permanent acquisition error types.
- [ ] Add adversarial unit tests.
- [ ] Validate no unrelated processing/persistence work was introduced.

## Interfaces / Contracts

Implements BACKGROUND-001:

```text
MerchantKnowledgeWebPageAcquirer
```

Produces:

```text
AcquiredMerchantKnowledgeDocument
```

for BACKGROUND-004.

## Dependencies

- `ARCH-023-BACKGROUND-001`

## Enables

- `ARCH-023-BACKGROUND-004`

## Acceptance Criteria

- [ ] No denied destination can be contacted, including through redirects or mixed DNS answers.
- [ ] Actual connection is bound to and verified against the validated IP.
- [ ] No merchant/Moda credentials are propagated.
- [ ] Decompressed response size is bounded at 1 MiB.
- [ ] Only HTML/plain text is accepted.
- [ ] HTML extraction executes/fetches no active content/subresources.
- [ ] Adapter returns extracted source text only.
- [ ] No database writes/normalization/embedding work exists in this task.

## Validation

- [ ] focused network-policy tests
- [ ] focused HTML-extraction tests
- [ ] focused acquirer tests
- [ ] `npm run build`
- [ ] `git diff --check`
- [ ] changed-file diagnostics clean

## Stop Condition

Set status to `review`, complete Completion Report, return to `moda_architect` and STOP. Do not start BACKGROUND-004.

## Implementation Notes

Prefer built-in `node:https`, `node:dns/promises`, `node:zlib` and a small dedicated HTML parser. Do not introduce Playwright/Puppeteer/jsdom solely to fetch or render Merchant Knowledge.

## Completion Report

### Status
Not Started
### Files Changed
None.
### Work Completed
None.
### Validation Results
None.
### Deviations
None.
### Assumptions
None.
### Unresolved Issues
None.
### Architectural Concerns
None.

## Architect Review

### Review Status
Pending
### Review Notes
Pending.
### Reviewed Files
Pending.
### Validation Reviewed
Pending.
### Architecture Conformance
Pending.
### Follow-up
Pending.
