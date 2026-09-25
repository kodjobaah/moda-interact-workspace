---
id: ARCH-021-COMMERCE-035
architecture_id: ARCH-021
title: Normalize and render Shopify documentation readably
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 35
executor: copilot
claimed_at: 2026-09-25T10:39:19Z
attempt: 5
depends_on:
  - ARCH-021-COMMERCE-034
enables:
  - ARCH-021-SYSTEM-TEST-001
created: 2026-09-24
updated: 2026-09-25
---

# Normalize and render Shopify documentation readably

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Replace raw Shopify documentation blobs with one safe, bounded, structured documentation contract so search results show readable plain-text excerpts and opened documents preserve meaningful headings, paragraphs, lists and code blocks without rendering raw HTML.

## Context

Manual validation of the Explore Documentation tab exposed two production defects.

Search uses pinned Shopify Dev MCP:

```text
learn_shopify_api
search_docs_chunks
```

and `lib/discovery/upstream.ts` currently maps the returned `content` directly to:

```text
UpstreamSearchItem.text
```

up to 2,000 characters.

`components/studio-workspace.tsx` then renders that value directly inside:

```tsx
<p>{item.text}</p>
```

Shopify search chunks can contain markdown links, code, JSON and HTML-like fragments. As a result the result list exposes syntax such as:

```text
[label](https://...)
{ "query": ... }
<...>
```

instead of a readable excerpt.

Opening a result is a separate path. `fetchShopifyDocument()` safely fetches the canonical `https://shopify.dev/docs/...` HTML and verifies a `main` or `article` container. However `lib/discovery/document.ts` reduces that container to one string with:

```text
readableText(...)
replace(/\s+/g, " ")
```

and the UI renders the complete value as one paragraph:

```tsx
<p>{document.text}</p>
```

This destroys headings, paragraph boundaries, lists, code/preformatted text and other useful reading structure.

The correction must preserve the existing security boundary: Shopify documentation is untrusted remote content. Do not use raw HTML injection.

## Scope

Primary files:

```text
lib/discovery/upstream.ts
lib/discovery/document.ts
lib/discovery/service.ts
src/studio/contracts.ts
src/commerce/integration/studio/services.ts
src/studio/discovery/shopify-documentation-explorer.tsx  # new required Client Component
src/studio/discovery/shopify-documentation-article.tsx   # new required pure renderer
components/studio-workspace.tsx
app/globals.css
tests/discovery-document.test.ts
tests/discovery.test.ts
tests/studio-services.test.ts
tests/studio-workspace.test.tsx
tests/shopify-documentation-explorer.test.tsx            # new required
tests/shopify-documentation-article.test.tsx             # new required
```

Additional directly affected documentation-only files may be changed when required by the normalized contract.

## Out of Scope

- Storefront schema browsing/query generation.
- COMMERCE-032/033/034 behavior.
- Live documentation editing.
- Rendering arbitrary remote HTML.
- A general-purpose browser/Markdown engine.
- Following arbitrary external links from remote content.
- Database/Shared/Background/Gateway changes.
- Shopify Admin API.
- Provider/model calls.
- A test-only documentation port/service/context/React prop in production code.

## Requirements

### R1 — separate search excerpts from full document content

The public Studio documentation contracts must distinguish:

```text
search result excerpt
full structured document
```

Search result DTO must contain at least:

```text
title
excerpt
sourceUrl
path
```

Do not call the search excerpt `text` if it can be confused with complete document content.

Full document DTO must contain at least:

```text
title
sourceUrl
blocks
relatedFieldPaths
```

Do not expose raw remote HTML to a Client Component.

### R2 — normalize search results to plain readable excerpts

Add one pure server-side normalization function for `search_docs_chunks.content`.

The resulting excerpt must:

1. decode common HTML entities;
2. remove HTML tags rather than displaying them;
3. convert Markdown links:
   ```text
   [label](url)
   ```
   to readable label text;
4. convert Markdown images:
   ```text
   ![alt](url)
   ```
   to alt text or omit them when alt is blank;
5. remove Markdown heading/list/fence markers;
6. preserve useful inline-code text but remove the backtick markup;
7. collapse whitespace;
8. omit zero-width/control characters other than ordinary spaces;
9. contain no executable/rendered HTML;
10. be bounded to at most 600 visible characters and at most 2 KiB UTF-8.

If normalization yields an empty excerpt, return a bounded fallback such as:

```text
No preview available.
```

Do not fetch every result page merely to build search excerpts.

### R3 — structured full-document contract

Normalize the verified Shopify `main`/`article` HTML into a bounded block model.

Support exactly these public block kinds for this checkpoint:

```text
HEADING
PARAGRAPH
LIST
CODE
BLOCKQUOTE
```

Required shape:

```text
HEADING:
  level: 2 | 3 | 4
  text: string

PARAGRAPH:
  text: string

LIST:
  ordered: boolean
  items: string[]

CODE:
  text: string

BLOCKQUOTE:
  text: string
```

Unknown/unsupported readable block containers may degrade to `PARAGRAPH`.

Do not expose tag names or raw HTML in the public block contract.

### R4 — preserve meaningful document structure

The HTML normalizer must preserve:

- heading boundaries;
- paragraph boundaries;
- ordered/unordered list-item boundaries;
- `<pre>` / code-block whitespace and newlines;
- blockquote boundaries.

Inline elements inside paragraphs/headings/list items may be flattened to readable text for this checkpoint.

For example:

```html
<h2>Create a customer</h2>
<p>Use <code>customerCreate</code>.</p>
<ul><li>Create</li><li>Activate</li></ul>
<pre>mutation Example { ... }</pre>
```

must normalize into four distinct blocks, not one concatenated string.

Do not globally run `replace(/\s+/g, " ")` across code/preformatted content.

### R5 — discard non-content/sensitive browser elements

Continue excluding at least:

```text
script
style
nav
footer
iframe
object
embed
form
noscript
template
```

Also exclude interactive/browser-only controls such as:

```text
button
input
select
textarea
svg
canvas
```

Their attributes/event handlers must never reach the public DTO.

### R6 — bounded output

Retain the current bounded-fetch/security behavior:

```text
max input:  1 MiB
max redirects: 2
canonical origin: https://shopify.dev/docs/
```

The structured serialized full-document output must remain bounded to:

```text
64 KiB UTF-8
```

Additionally enforce:

```text
maximum blocks:          512
maximum list items/block: 100
maximum normal text/block: 8 KiB UTF-8
maximum code block:      16 KiB UTF-8
```

Reject documents exceeding the bounds rather than silently truncating the opened document.

Search excerpts may be deliberately truncated because they are previews.

### R7 — mandatory documentation component boundary

The Documentation tab must be extracted from `components/studio-workspace.tsx`.

Create exactly these production UI modules:

```text
src/studio/discovery/shopify-documentation-explorer.tsx
src/studio/discovery/shopify-documentation-article.tsx
```

#### `ShopifyDocumentationExplorer`

This is the Documentation-tab Client Component.

It owns exactly:

```text
search query state
search-result state
opened-document state
documentation loading state
documentation error/status state
Search documentation action
Back to results action
opening a selected result
Open related schema fields action
```

It must invoke the same production named Server Actions directly:

```ts
import {
  searchDocumentation,
  getDocumentation,
} from "../server-actions";
```

or the correct relative path to that exact module.

Do not introduce:

```text
DocumentationPort
DocumentationServices
documentationActions prop
test-only callback registry
test-only React context/provider
NODE_ENV === "test" branch
```

The only production props allowed for this component are ordinary UI composition values genuinely used by production. For this checkpoint use:

```ts
type ShopifyDocumentationExplorerProps = {
  disabled: boolean;
  onOpenRelatedSchema: () => void;
};
```

`onOpenRelatedSchema` is a real production client-to-client callback used to switch the existing Explore tab. It is not a server boundary and is not test-only.

Tests must mock the same named `searchDocumentation` / `getDocumentation` module exports that production imports.

#### `ShopifyDocumentationArticle`

This is a pure structured-document renderer.

It owns exactly:

```text
document title
canonical Open on Shopify link
HEADING block rendering
PARAGRAPH block rendering
LIST block rendering
CODE block rendering
BLOCKQUOTE block rendering
```

Its production contract must be exactly the normalized document DTO (or a single `document` prop of that type):

```ts
type ShopifyDocumentationArticleProps = {
  document: DocumentationDocument;
};
```

It must:

- contain no provider/network/data-fetching code;
- import no Server Action;
- contain no sanitizer for raw HTML;
- receive no raw HTML;
- use no `dangerouslySetInnerHTML`.

#### `StudioWorkspace`

After this task, `components/studio-workspace.tsx` may:

- own the existing `"docs" | "schema"` tab state;
- render `ShopifyDocumentationExplorer` when the Documentation tab is active;
- pass the real `disabled` value;
- pass `onOpenRelatedSchema={() => setTab("schema")}`.

It must no longer own:

```text
DocumentationItem[] state
DocumentationDocument state
documentation query state
documentation search/open functions
documentation result list markup
documentation article block markup
```

Do not move those responsibilities into another generic Studio component.

Search results rendered by `ShopifyDocumentationExplorer` must be readable result cards/list items containing:

```text
title
bounded excerpt
canonical source indication
Open/read action
```

Do not render a 2,000-character raw chunk as the result paragraph.

Opened documents rendered by `ShopifyDocumentationArticle` must use a semantic:

```tsx
<article>
```

with block-specific elements:

```text
HEADING    -> h3/h4/h5 or equivalent bounded hierarchy
PARAGRAPH  -> p
LIST       -> ul/ol + li
CODE       -> pre > code
BLOCKQUOTE -> blockquote
```

Add bounded documentation-reader CSS:

- readable line length (`max-width` around 70–80ch);
- normal paragraph spacing;
- list indentation;
- distinct headings;
- horizontally scrollable code blocks;
- code preserves whitespace;
- long unbroken content wraps safely outside code blocks.

Do not use `dangerouslySetInnerHTML`.

### R8 — canonical source link

Opened documentation may display an `Open on Shopify` link using the already canonicalized `sourceUrl`.

Requirements:

```text
target="_blank"
rel="noopener noreferrer"
```

Do not render links discovered inside remote HTML in this checkpoint.

### R9 — no raw markup regressions

Focused tests must prove search excerpts do not expose raw markup.

At minimum use search content containing all of:

```text
<h2>Heading</h2>
[Product](https://shopify.dev/docs/api/storefront/current/objects/Product)
`product`
```graphql
query X { shop { name } }
```
```

and prove the rendered search result:

- contains readable words;
- does not show `<h2>`;
- does not show `](https://`;
- does not show triple backticks.

### R10 — full-document structure regression

Use a verified HTML document containing:

```text
title
h2
two paragraphs
unordered list
ordered list
blockquote
pre/code with multiple lines
script/style noise
```

Prove the normalized block sequence and the React rendering preserve those distinct structures.

Also prove no script/style content appears.

### R11 — contract and composition parity

Tests must exercise the same normalization functions, DTOs, components and named Server Action boundary that production uses.

Do not create a richer documentation fixture shape that production never returns.

The in-memory Studio fixture must be updated to use the exact final public documentation DTO.

Component tests must:

- render the real `ShopifyDocumentationExplorer`;
- mock `searchDocumentation` and `getDocumentation` from the same named Server Action module imported by production;
- render the real `ShopifyDocumentationArticle`;
- never pass a test-only service/port/action bundle prop into either production component.

`StudioWorkspace` tests must prove that the Documentation tab composes `ShopifyDocumentationExplorer` rather than maintaining a second inline documentation implementation.

### R12 — do not broaden upstream trust

Keep the current upstream split:

```text
search:
  pinned Shopify Dev MCP search_docs_chunks

open:
  verified direct fetch from canonical shopify.dev/docs URL
```

Do not render MCP-provided full HTML as trusted content.

Do not replace the verified direct-document fetch with arbitrary URLs returned by search.

## Work Items

- [x] Add plain-text search-excerpt normalizer.
- [x] Replace `DocumentationItem.text` with bounded `excerpt`.
- [x] Add structured documentation block contract.
- [x] Refactor verified HTML extraction to preserve block structure.
- [x] Preserve code/pre whitespace.
- [x] Enforce structured-document bounds.
- [x] Update Studio service adapter/contracts.
- [x] Create `ShopifyDocumentationExplorer` with the exact production responsibilities/props in R7.
- [x] Create pure `ShopifyDocumentationArticle` with the exact production responsibilities/props in R7.
- [x] Remove documentation query/result/document/search/open/rendering state from `StudioWorkspace`.
- [x] Render search results as bounded readable cards/items in `ShopifyDocumentationExplorer`.
- [x] Render opened document as semantic structured article through `ShopifyDocumentationArticle`.
- [x] Add canonical `Open on Shopify` action in `ShopifyDocumentationArticle`.
- [x] Add readable documentation CSS.
- [x] Update in-memory fixtures to exact production DTO shape.
- [x] Mock the production named documentation Server Actions in component tests.
- [x] Add raw-markup, structured-rendering and component-boundary regressions.
- [ ] Ensure documentation search results have unique canonical `path` identities before React rendering.
- [ ] Raise only the semantic document-block ceiling from 256 to 512 while retaining the 64 KiB serialized-output cap.
- [ ] Make parser bound failures distinguish block-count/list/text/code causes from the final serialized-output bound.
- [ ] Add duplicate-result and large-semantic-document regressions from developer manual validation.
- [x] Remove task-file conflict-marker residue and reconcile the final Validation record.

## Interfaces / Contracts

Changes only Commerce-local Studio documentation contracts.

Search:

```text
DocumentationItem:
  title
  excerpt
  sourceUrl
  path
```

Full document:

```text
DocumentationDocument:
  title
  sourceUrl
  blocks
  relatedFieldPaths
```

No cross-service contract is introduced.

## Dependencies

- ARCH-021-COMMERCE-034

## Enables

- ARCH-021-SYSTEM-TEST-001

## Acceptance Criteria

- [x] Search results no longer display raw HTML/Markdown syntax.
- [x] Search results show bounded readable excerpts.
- [x] Opened documentation is not rendered as one giant paragraph.
- [x] Headings, paragraphs, lists, code and blockquotes retain separate structure.
- [x] Code/preformatted text retains meaningful newlines/whitespace.
- [x] No raw HTML reaches `dangerouslySetInnerHTML`.
- [x] Non-content/script/style elements are absent from output.
- [x] Canonical source URL remains constrained to `shopify.dev/docs`.
- [x] Existing input/output/redirect bounds remain enforced.
- [x] Tests and fixtures consume the same final documentation DTO as production.
- [x] `StudioWorkspace` no longer owns documentation search/result/open-document state or document rendering markup.
- [x] `ShopifyDocumentationExplorer` uses the production named Server Action imports directly.
- [x] `ShopifyDocumentationArticle` is a pure renderer with no Server Action/provider/network dependency.
- [x] No production documentation port/service/action-bundle prop or test-only React context/provider is introduced.
- [ ] `DocumentationItem.path` values presented to `ShopifyDocumentationExplorer` are unique within one search result set.
- [ ] Duplicate upstream/canonical search hits preserve the first-ranked result and do not render duplicate cards/React keys.
- [ ] A semantic document with more than 256 but at most 512 small blocks can be opened when its serialized DTO remains under 64 KiB.
- [ ] More than 512 semantic blocks still fail closed with a block-count-specific bounded error.
- [ ] The existing 64 KiB serialized full-document output bound remains unchanged and enforced.
- [x] The task file contains no Git conflict markers.

## Validation

- [ ] `npx vitest run tests/discovery-document.test.ts tests/discovery.test.ts tests/studio-services.test.ts tests/studio-workspace.test.tsx tests/shopify-documentation-explorer.test.tsx tests/shopify-documentation-article.test.tsx --reporter=verbose`
- [ ] targeted ESLint for every Attempt 5 changed source/test file
- [ ] `npm run typecheck` (unchanged unrelated baseline may be recorded; zero task-owned diagnostics required)
- [ ] raw-rendering source audit:
  ```text
  rg -n "dangerouslySetInnerHTML|<p>\{document\.text\}</p>|item\.text" \
    components src/studio lib/discovery
  ```
  expected: no documentation-rendering matches; unrelated transport/preview `item.text` matches may be recorded explicitly.
- [ ] `StudioWorkspace` ownership audit:
  ```text
  rg -n \
    "DocumentationItem|DocumentationDocument|searchDocumentation|getDocumentation|setItems|setDocument|async function search\(|async function open\(" \
    components/studio-workspace.tsx
  ```
  expected: no documentation implementation matches
- [ ] production test-only seam audit:
  ```text
  rg -n \
    "DocumentationPort|DocumentationServices|documentationActions|NODE_ENV.*test|fixture.*Documentation|documentation.*fixture.*prop" \
    components src/studio
  ```
  expected: no production documentation test-injection matches
- [ ] component existence audit:
  ```text
  test -f src/studio/discovery/shopify-documentation-explorer.tsx
  test -f src/studio/discovery/shopify-documentation-article.tsx
  ```
  expected: both pass
- [ ] duplicate-result identity audit:
  ```text
  rg -n "key=\{item\.path\}" src/studio/discovery/shopify-documentation-explorer.tsx
  ```
  expected: this key remains valid only because the production search boundary now guarantees unique `path` values; accompanying regression must prove that invariant.
- [ ] conflict-marker audit:
  ```text
  ! rg -n "^(<<<<<<<|=======|>>>>>>>)" \
    docs/decisions/commerce/ARCH-021/COMMERCE-035-render-shopify-documentation-readably.md
  ```
  expected: PASS
- [ ] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report, return to `moda_architect` and STOP.

Do not start SYSTEM-TEST-001.

## Implementation Notes

Do not solve readability by increasing container width alone. The data contract currently destroys/forwards the wrong structure and must be corrected first.

Do not add a heavyweight generic HTML/Markdown rendering system unless the bounded requirements above genuinely cannot be met with the existing verified parser. This task needs a small safe documentation renderer, not a CMS.

Do not render remote HTML with `dangerouslySetInnerHTML`.

The full-document parser may flatten inline formatting for this checkpoint. Preserving block structure is the required outcome.


Do not leave a compatibility copy of the old Documentation-tab implementation in `StudioWorkspace`.

Do not create `TestShopifyDocumentationExplorer`, a test-only production context, or an injectable documentation service prop. Tests mock the same named Server Actions production imports.

Keep `ShopifyDocumentationArticle` deliberately dumb: it renders the normalized DTO and nothing else.

## Completion Report

### Status

Ready for Review

### Files Changed

Attempt 1 files remain as previously recorded. Attempt 2 changed:

- `lib/discovery/upstream.ts`
- `lib/discovery/document.ts`
- `tests/discovery-document.test.ts`

Attempt 3 changed:

- `tests/discovery-document.test.ts`

Attempt 4 changed:

- `lib/discovery/document.ts`
- `lib/discovery/upstream.ts`
- `tests/discovery-document.test.ts`

### Work Completed

Attempt 1 delivered the structured documentation contract, verified HTML block normalization and bounds, the extracted documentation components, semantic rendering, readable CSS, production fixture parity and component-boundary regressions.

Attempt 2 correction checklist, all implemented:

- Finding 1: `normalizeSearchExcerpt` decodes HTML entities before removing tags; regression added.
- Finding 2: excerpt truncation iterates Unicode code points and stops before the 600-code-point or 2 KiB UTF-8 bound; boundary regression added.
- Finding 3: `readableText` maps `<br>` to a space in normal text and a newline in preformatted text; paragraph/code regressions added.

Attempt 3 correction checklist, all implemented:

- Added `normalizeSearchExcerpt('')` fallback coverage.
- Added whitespace/control/stripped-markup normalized-empty fallback coverage.
- Reconciled the Work Items, Acceptance Criteria and Validation checklists with the submitted evidence.

Attempt 4 correction checklist, all implemented:

- Finding 1: parser attributes are retained only for server-side classification; hidden, accessibility-only and control nodes are excluded before DTO creation.
- Finding 2: local hash-link anchor helpers and semantic Shopify chrome, including version selectors and feedback controls, are removed without global prose stripping.
- Finding 3: decorative-only blocks and the duplicate top-level page H1 are omitted; consecutive identical short heading/paragraph blocks are collapsed locally.
- Finding 4: search excerpts receive bounded helper/chrome cleanup while retaining the real product sentence.
- Finding 5: representative collection-document and search regressions cover the manual-validation defect and visible anchor-helper form.

Architect Review was preserved unchanged.

### Validation Results

- Focused Vitest command: PASS, 6 files and 73 tests.
- Targeted ESLint for `lib/discovery/document.ts`, `lib/discovery/upstream.ts` and `tests/discovery-document.test.ts`: PASS, 0 errors.
- `npm run typecheck`: exits 1 on unchanged unrelated baseline diagnostics; `C035_OWNED_DIAGNOSTICS=none` for `lib/discovery`, `components/studio-workspace`, documentation components and focused documentation tests.
- Raw rendering audit: PASS for documentation rendering. The only matches are allowed unrelated `item.text` uses in MCP transport (`lib/discovery/upstream.ts`) and preview UI (`src/studio/preview/preview-screen.tsx`).
- StudioWorkspace ownership audit: PASS with no matches.
- Production test-seam audit: PASS with no matches.
- Component existence audit: PASS for both required modules.
- `git diff --check`: PASS.

### Branch and Topology Evidence

- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-035`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-035`.
- Mirrored branch: `task/ARCH-021-COMMERCE-035`.
- Launcher claim commit: parent `d242d0d6345a7dab553c0113d12702397a7c1d3f`.
- Dependency `ARCH-021-COMMERCE-034`: complete.
- Database submodule: `0a8d3b9feade69690b6c1e33aeda051ea588bd45`.
- Implementation commit: `7dcfefb`, pushed to `origin/task/ARCH-021-COMMERCE-035`.
- No downstream task was started.

### Deviations

- Typecheck exits 2 on the documented unchanged Prisma/generated and unrelated Commerce integration/test diagnostics; no diagnostic references the Attempt 4-owned parser, upstream normalizer or focused test file.

### Assumptions

- The verified direct Shopify HTML fetch remains the only opened-document source, and the pinned MCP path remains search-only.

### Unresolved Issues

- None within the bounded Commerce-035 scope.

### Architectural Concerns

- None identified within the bounded Commerce-035 scope.

## Architect Review

### Review Status

Changes Requested

### Review Notes

Attempt 4 satisfies the semantic page-chrome/accessibility cleanup requested after
developer manual validation.

Architect review confirms the submitted source now:

- preserves only minimal parser-internal attributes needed for classification;
- excludes hidden/accessibility/navigation/control nodes;
- removes local `Anchor to ...` helpers without globally deleting ordinary prose;
- removes bounded Shopify version/feedback/copy/show-fields chrome;
- suppresses decorative-only blocks and the duplicate top-level page H1;
- collapses only consecutive identical short heading/paragraph blocks;
- keeps meaningful arguments/type/descriptions intact;
- applies bounded helper/chrome cleanup to search excerpts;
- preserves the accepted `ShopifyDocumentationExplorer` /
  `ShopifyDocumentationArticle` component boundary.

The representative collection-page and search-excerpt regressions are present and
the Completion Report records 6 focused files / 73 passing tests.

Two additional developer-manual-validation issues were reported while Attempt 4
was already in progress. They were intentionally not injected into the running
claim. Both remain visible in the submitted Attempt 4 source and must be resolved
before terminal system testing.

There is also architect/task-file conflict residue in the submitted task record.

#### Finding 1 — duplicate documentation paths still reach React as duplicate keys

The browser warning reported:

```text
Encountered two children with the same key,
`api/storefront/2026-07/objects/Collection`

Encountered two children with the same key,
`api/storefront/2026-07/queries/collection`
```

is legitimate.

The final production explorer still renders:

```tsx
{items.map((item) => (
  <li key={item.path}>
```

and no production boundary currently guarantees that the returned
`DocumentationItem.path` values are unique.

The Studio adapter derives `path` deterministically from `sourceUrl`, but it maps
every backend result without de-duplication.

Attempt 5 must enforce uniqueness **before React rendering**.

Preferred boundary:

```text
backend discovery search results
  -> canonical sourceUrl/path
  -> first-occurrence de-duplication by canonical path
  -> DocumentationItem[]
  -> ShopifyDocumentationExplorer
```

Implement this at the production Studio service boundary that creates `path`
(`src/commerce/integration/studio/services.ts`) or an equivalently authoritative
server boundary.

Required behavior:

```text
same canonical path repeated 3 times
  -> exactly 1 DocumentationItem
  -> preserve the first-ranked item's title/excerpt
  -> preserve relative order of all unique items
```

Do not merely change the React key to:

```text
path + index
```

because that hides the warning while still displaying duplicate search cards.

`key={item.path}` may remain once the server-side uniqueness invariant is
deterministically enforced and tested.

Required regression must provide duplicate backend search hits for:

```text
api/storefront/2026-07/queries/collection
api/storefront/2026-07/queries/collection
api/storefront/2026-07/objects/Collection
api/storefront/2026-07/objects/Collection
```

and prove the Studio search response contains each path exactly once with the
first occurrence retained.

#### Finding 2 — the logged bounded-size error is a parser-level bound, not the final 64 KiB service bound

The developer log reported exactly:

```text
Shopify documentation result exceeded the bounded size.
```

That wording originates from `lib/discovery/document.ts`.

The later 64 KiB serialized service guard uses a different message:

```text
Documentation result exceeded the bounded size.
```

Therefore the reported failure was triggered by one of the parser-level limits:

```text
normal text block: 8 KiB
code block:        16 KiB
list items:        100
semantic blocks:   256
```

rather than by the final 64 KiB serialized DTO guard.

The manually tested Shopify `Collection` object/query documentation is a
legitimate comprehensive document. A hard 256-block ceiling is too restrictive
when the final DTO is still independently bounded to 64 KiB.

Attempt 5 must change only:

```text
maximum semantic blocks: 256 -> 512
```

The following remain unchanged:

```text
max HTML input:           1 MiB
max redirects:            2
max list items/block:     100
max normal text/block:    8 KiB
max code block:           16 KiB
max serialized document:  64 KiB
```

This is an architecture correction based on developer manual validation. The
64 KiB serialized-output bound remains the final transport/UI safety ceiling.

Also stop using the same generic parser error for every parser-level bound.

Use bounded cause-specific messages, for example:

```text
Shopify documentation text block exceeded the bounded size.
Shopify documentation code block exceeded the bounded size.
Shopify documentation list exceeded the bounded item count.
Shopify documentation exceeded the 512-block limit.
```

Equivalent deterministic wording is acceptable, but each parser-level limit must
be distinguishable from the final service error:

```text
Documentation result exceeded the bounded size.
```

This is required so a future manual-validation log identifies which safety bound
actually failed.

#### Required large-document regressions

Add a parser/service regression using small semantic paragraphs so no per-block
limit is involved.

Prove:

```text
300 semantic paragraph blocks
serialized DTO < 64 KiB
-> accepted
```

This specifically proves a legitimate document is no longer rejected solely
because it crossed the previous 256-block ceiling.

Also prove:

```text
513 semantic paragraph blocks
-> rejected with the new block-count-specific error
```

Retain the existing regression:

```text
serialized DTO > 64 KiB
-> rejected by createDiscoveryService.document()
-> "Documentation result exceeded the bounded size."
```

Do not increase the 64 KiB service-output bound in Attempt 5.

If developer manual validation after this correction still produces the **service**
message:

```text
Documentation result exceeded the bounded size.
```

for the cleaned real Shopify page, return that new evidence to the architect
rather than increasing the transport bound automatically.

#### Coordination-record reconciliation — conflict-marker residue already cleared

The previous review snapshot contained Git conflict-marker residue inside
`## Validation`. In the current developer snapshot that residue has already been
removed.

Architect verification of this exact snapshot finds no standalone line
beginning with any standard Git conflict-marker prefix (seven less-than signs,
seven equals signs, or seven greater-than signs).

The explicit conflict-marker Validation audit remains part of Attempt 5 so this
coordination invariant is proved again before review, but no further source/task
edit is required solely for conflict-marker cleanup.

### Attempt 5 deterministic correction

Reclaim the same task as Attempt 5.

Preserve all accepted Attempt 1-4 production behavior.

Expected production files are limited to:

```text
src/commerce/integration/studio/services.ts
lib/discovery/document.ts
```

with directly related tests.

`ShopifyDocumentationExplorer` should not require redesign if the server-side
unique-path invariant is correctly enforced.

Change another production file only if a required regression exposes a directly
related defect.

### Required tests

Update/add focused coverage for:

1. duplicate canonical documentation paths are returned once;
2. first-ranked duplicate content is preserved;
3. unique result ordering is preserved;
4. 300 small semantic blocks are accepted below the 64 KiB service cap;
5. 513 semantic blocks fail with the block-count-specific parser error;
6. the existing >64 KiB serialized-output regression still fails with the
   service-level error;
7. all Attempt 4 semantic chrome/accessibility regressions remain passing.

### Validation

Run the restored task Validation section exactly.

Typecheck acceptance remains:

```text
unchanged documented unrelated baseline is permitted
zero C035-owned diagnostics are required
```

### Completion Report

Record:

```text
Attempt 1:
  structured docs + component extraction

Attempt 2:
  encoded-tag / Unicode / <br> correctness

Attempt 3:
  fallback regression + evidence reconciliation
  architect-accepted Complete

Manual validation / Attempt 4:
  semantic Shopify page chrome/accessibility cleanup

Additional manual logs / Attempt 5:
  duplicate search-result identity
  parser block-bound correction and bound-specific diagnostics
  task-record conflict cleanup
```

Record implementation/report commits, focused test count, ESLint, typecheck,
all audits, clean/upstream branch state and database submodule synchronization.

Return:

```yaml
status: review
executor: null
claimed_at: null
attempt: 5
```

and STOP.

Do not start `ARCH-021-SYSTEM-TEST-001`.

### Reviewed Files

- `lib/discovery/document.ts`
- `lib/discovery/upstream.ts`
- `lib/discovery/service.ts`
- `src/commerce/integration/studio/services.ts`
- `src/studio/discovery/shopify-documentation-explorer.tsx`
- `tests/discovery-document.test.ts`
- `tests/studio-services.test.ts`
- `tests/shopify-documentation-explorer.test.tsx`
- task Completion Report

### Validation Reviewed

Submitted Attempt 4 evidence:

```text
focused tests: 6 files / 73 passed
targeted ESLint: PASS
documentation source/component audits: PASS
git diff --check: PASS
typecheck: unchanged unrelated baseline only
           zero C035-owned diagnostics
```

Architect static review confirms the Attempt 4 semantic cleanup implementation is
present.

Architect static review also confirms the duplicate-key path remains possible,
the parser still uses a 256-block ceiling with generic parser-level error text,
and the task record contains conflict-marker residue.

### Architecture Conformance

Partial.

Attempt 4's semantic documentation cleanup conforms.

Acceptance is blocked by the additional manually reported duplicate-result
identity bug, the legitimate parser block-bound limitation, and task-record
conflict residue.

### Follow-up

Reclaim the same C035 task as Attempt 5.

`ARCH-021-SYSTEM-TEST-001` remains Pending.
