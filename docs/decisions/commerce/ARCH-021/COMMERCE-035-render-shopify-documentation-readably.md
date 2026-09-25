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
status: ready
priority: 35
executor: null
claimed_at: null
attempt: 3
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
maximum blocks:          256
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

## Validation

- [x] `npx vitest run tests/discovery-document.test.ts tests/discovery.test.ts tests/studio-services.test.ts tests/studio-workspace.test.tsx tests/shopify-documentation-explorer.test.tsx tests/shopify-documentation-article.test.tsx --reporter=verbose`
- [x] targeted ESLint for every Attempt 3 changed source/test file
- [x] `npm run typecheck` (unchanged unrelated baseline may be recorded; zero task-owned diagnostics required)
- [x] raw-rendering source audit:
  ```text
  rg -n "dangerouslySetInnerHTML|<p>\{document\.text\}</p>|item\.text" \
    components src/studio lib/discovery
  ```
  expected: no documentation-rendering matches; unrelated transport/preview `item.text` matches may be recorded explicitly.
- [x] `StudioWorkspace` ownership audit:
  ```text
  rg -n \
    "DocumentationItem|DocumentationDocument|searchDocumentation|getDocumentation|setItems|setDocument|async function search\(|async function open\(" \
    components/studio-workspace.tsx
  ```
  expected: no documentation implementation matches
- [x] production test-only seam audit:
  ```text
  rg -n \
    "DocumentationPort|DocumentationServices|documentationActions|NODE_ENV.*test|fixture.*Documentation|documentation.*fixture.*prop" \
    components src/studio
  ```
  expected: no production documentation test-injection matches
- [x] component existence audit:
  ```text
  test -f src/studio/discovery/shopify-documentation-explorer.tsx
  test -f src/studio/discovery/shopify-documentation-article.tsx
  ```
  expected: both pass
- [x] `git diff --check`

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

Architect Review was preserved unchanged.

### Validation Results

- Focused Vitest command: PASS, 6 files and 71 tests.
- Targeted ESLint for `tests/discovery-document.test.ts`: PASS, 0 errors.
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
- Launcher claim commit: parent `d461868dbbf4dc447bb9d090827c20dd50e63f0a`.
- Dependency `ARCH-021-COMMERCE-034`: complete.
- Database submodule: `0a8d3b9feade69690b6c1e33aeda051ea588bd45`.
- Implementation commit: `a03b618`, pushed to `origin/task/ARCH-021-COMMERCE-035`.
- No downstream task was started.

### Deviations

- Typecheck remains blocked by the documented unchanged Prisma/generated and unrelated Commerce integration/test diagnostics. No C035-owned diagnostic was reported.

### Assumptions

- The verified direct Shopify HTML fetch remains the only opened-document source, and the pinned MCP path remains search-only.

### Unresolved Issues

- None within the bounded Commerce-035 scope.

### Architectural Concerns

- None identified within the bounded Commerce-035 scope.

## Architect Review

### Review Status

Changes Requested After Manual Validation

### Review Notes

COMMERCE-035 Attempt 3 was architect-accepted Complete, but developer manual
validation before terminal SYSTEM-TEST exposed an additional readability defect in
the same documentation capability.

The accepted Attempt 1-3 implementation solved:

```text
raw HTML/Markdown leakage
one giant flattened document paragraph
unsafe raw HTML rendering
encoded-tag normalization order
Unicode-safe excerpt bounds
<br> separator preservation
```

Those accepted behaviors must remain unchanged.

The new manual-validation screenshot shows that the structured parser still
includes Shopify documentation **page chrome and accessibility helper text** as if
it were article content.

Observed examples include:

```text
Choose a version:
2026-07
latest
Anchor to collection
Anchor to Arguments
Anchor to handle
•
Was this section helpful?
Anchor to Possible returnsPossible returns
```

This matches the current Shopify generated documentation representation: the
source page itself contains version-selector text, "Anchor to ..." helper labels,
feedback controls, "Show fields"/"Copy" controls and similar documentation chrome.

This is not primarily a CSS problem. The server parser must separate semantic
article content from Shopify page/navigation/accessibility chrome before producing
the public `DocumentationBlock[]`.

### Attempt 4 objective

Produce a **clean semantic article** from the already-verified Shopify HTML while
preserving the accepted safe block contract.

Target presentation for a query page should resemble:

```text
collection

Retrieves a single Collection by its ID or handle.
Use the products field to access items in the collection.

Arguments

• handle (String)
  The handle of the Collection.

• id (ID)
  The ID of the Collection.

Possible returns

• Collection
  A group of products organized by a merchant ...
```

It must not expose:

```text
Choose a version
latest
Anchor to ...
Was this section helpful?
Show fields
Show input fields
Show enum values
Copy
Copy MD
Install AI Toolkit
Ask about this page
Hide content
Full index
standalone decorative bullets
```

as article paragraphs/headings.

### Deterministic correction contract

#### 1. Preserve minimal HTML attributes for server-side classification only

The current `HtmlNode` keeps only:

```ts
{ tag, children }
```

so the parser cannot distinguish visually-hidden/accessibility/navigation nodes
from meaningful inline content.

Extend the **server-only internal parser node** to preserve only the minimal
attributes required for classification, for example:

```text
class
aria-hidden
aria-label
role
href
```

You may use an equivalent minimal set if inspection of the real Shopify markup
shows another attribute is required.

Requirements:

- these attributes are parser-internal only;
- they must never be exposed in `DocumentationBlock`;
- event-handler/style/raw-HTML attributes remain irrelevant and must not be
  surfaced;
- do not introduce `dangerouslySetInnerHTML`;
- do not switch the browser UI to remote HTML rendering.

#### 2. Exclude visually-hidden/accessibility helper nodes

Add one pure server-side classification helper, for example:

```ts
isNonContentNode(node): boolean
```

It must exclude at minimum:

```text
aria-hidden="true"
role="navigation"
role="menu"
role="button"
role="tab"
role="combobox"
```

and common visually-hidden class tokens case-insensitively, including at least:

```text
visually-hidden
visuallyhidden
sr-only
screen-reader
screenreader
```

Do not exclude arbitrary content merely because it has a CSS class.

If real Shopify markup uses another clearly accessibility-only class/token for the
"Anchor to ..." helper, add that exact bounded token and record it in the
Completion Report.

#### 3. Suppress local section-anchor helper text

For local hash-link/accessibility helper content, do not emit the helper label.

At minimum these must never survive as article text:

```text
Anchor to collection
Anchor to Arguments
Anchor to handle
Anchor to Possible returns
```

Prefer structural classification from the parsed attributes.

Add a bounded textual fallback only for a standalone/helper fragment matching:

```text
^Anchor to\s+
```

Do not globally remove those words from normal prose paragraphs.

A heading represented by accessibility helper + visible label:

```text
Anchor to Possible returnsPossible returns
```

must normalize to exactly:

```text
Possible returns
```

not to an empty heading and not to the duplicated text.

#### 4. Suppress Shopify documentation UI chrome

Create one bounded semantic-chrome predicate operating on complete candidate block
text / classified container, not on arbitrary substrings in prose.

Exclude standalone/control content for at least:

```text
Choose a version:
Install AI Toolkit
Ask about this page
Copy MD
Copy
Full index
Show fields
Show input fields
Show enum values
Show filters
Hide content
Was this section helpful?
Query Reference
```

Also suppress the version-selector values belonging to the same selector
container, including:

```text
2026-07
latest
```

Do **not** globally remove `2026-07` or `latest` from ordinary prose. Suppress the
version selector as a semantic container/group.

Likewise, feedback controls such as `Yes` / `No` are excluded only within the
identified feedback-control container; do not globally remove those words.

#### 5. Do not emit decorative-only blocks

Do not produce article blocks whose normalized text is only decoration, including:

```text
•
·
*
---
```

or equivalent single-glyph separators.

Horizontal rules may simply be omitted for this checkpoint.

#### 6. Suppress the duplicate page H1 already represented by the article header

`ShopifyDocumentationArticle` already renders:

```text
document.title
```

in its own header.

Do not emit the page's duplicate top-level `<h1>` as a second article block.

For a title such as:

```text
collection - Storefront API
```

a page H1 of:

```text
collection
```

must not appear again as a standalone paragraph/heading immediately beneath the
article header.

Do not suppress normal later headings that happen to contain the same word.

#### 7. Consecutive short duplicate block cleanup

After semantic chrome removal, collapse **consecutive identical short textual
blocks** produced from the same Shopify generated field/type widget.

This is specifically to avoid patterns such as:

```text
Collection
Collection
```

that result only from the page widget's duplicated visible/accessibility labels.

Bound the rule:

```text
same normalized text
consecutive blocks
text <= 128 characters
same block family (heading/paragraph or explicit compatible rule)
```

Do not perform global document-wide de-duplication.

#### 8. Preserve useful content and accepted block semantics

The cleanup must retain real documentation such as:

```text
Arguments
handle (String)
id (ID)
The handle of the Collection.
The ID of the Collection.
Possible returns
Collection
A group of products organized by a merchant ...
Examples
code blocks
ordered/unordered lists
blockquotes
```

Do not remove a block merely because it is short.

Do not remove actual GraphQL type names such as:

```text
String
ID
Collection
Product
```

unless it is an exact consecutive duplicate under rule 7.

#### 9. Apply equivalent bounded cleanup to search excerpts

Search excerpts can contain the same generated Shopify chrome.

After the existing safe plain-text normalization, suppress standalone/bounded
Shopify helper/chrome phrases such as:

```text
Anchor to ...
Choose a version:
Was this section helpful?
Show fields
Copy MD
```

without deleting those words when they occur naturally inside normal prose.

Do not fetch result pages to perform this cleanup.

#### 10. Keep UI changes minimal

This correction is primarily server normalization.

Do not redesign:

```text
ShopifyDocumentationExplorer
ShopifyDocumentationArticle
StudioWorkspace
```

unless a directly required presentation regression exposes a small CSS defect.

The current semantic `<article>`, heading/list/code/blockquote rendering boundary
is accepted.

### Required representative regression

Add a fixture representing the semantic content visible in manual validation,
including at minimum:

```html
<main>
  <div>
    <span>Choose a version:</span>
    <select><option>2026-07</option></select>
    <span>latest</span>
  </div>

  <a href="#collection">
    <span class="visually-hidden">Anchor to collection</span>
  </a>
  <h1>collection</h1>
  <span>query</span>

  <p>Retrieves a single Collection by its ID or handle.</p>

  <a href="#arguments">
    <span class="visually-hidden">Anchor to Arguments</span>
  </a>
  <h2>Arguments</h2>

  <ul>
    <li>handle (String)</li>
    <li>id (ID)</li>
  </ul>

  <a href="#handle">
    <span class="visually-hidden">Anchor to handle</span>
  </a>
  <p>handle</p>
  <p>•</p>
  <p>String</p>
  <p>The handle of the Collection.</p>

  <div>
    <span>Was this section helpful?</span>
    <button>Yes</button>
    <button>No</button>
  </div>

  <h2>
    <span class="visually-hidden">Anchor to Possible returns</span>
    Possible returns
  </h2>

  <p>Collection</p>
  <p>•</p>
  <p>Collection</p>
  <p>A group of products organized by a merchant.</p>
</main>
```

Use the actual parser-compatible surrounding `<html><head><title>...</title>...`
wrapper required by `fetchShopifyDocument()`.

The normalized result must contain useful article content but none of:

```text
Choose a version
latest
Anchor to
Was this section helpful
Yes
No
standalone •
```

and the `Possible returns` heading must occur once, not as:

```text
Anchor to Possible returnsPossible returns
```

#### Search-excerpt regression

Provide representative search content containing:

```text
Anchor to ProductsProducts
Show fields
Was this section helpful?
A product represents an item a merchant sells.
```

The resulting excerpt must retain the actual product sentence and must not expose
the standalone generated UI/helper phrases.

### Manual-validation acceptance examples

For the Shopify collection query page, the developer-facing rendered article
should no longer begin with:

```text
Choose a version:
2026-07
latest
Anchor to collection
collection
query
```

It should begin with the meaningful query description / article content beneath
the existing document header.

A section should no longer render:

```text
Anchor to Possible returnsPossible returns
```

It should render:

```text
Possible returns
```

### Validation

Run:

```bash
npx vitest run \
  tests/discovery-document.test.ts \
  tests/discovery.test.ts \
  tests/studio-services.test.ts \
  tests/studio-workspace.test.tsx \
  tests/shopify-documentation-explorer.test.tsx \
  tests/shopify-documentation-article.test.tsx \
  --reporter=verbose
```

Run targeted ESLint for every Attempt 4 changed file.

Run:

```bash
npm run typecheck
```

Only the documented unchanged unrelated baseline may remain; zero C035-owned
diagnostics are required.

Run all existing documentation source/component audits and:

```bash
git diff --check
```

All must pass under their existing allowed conditions.

### Completion Report

Record this as developer-manual-validation correction after the previously
accepted Attempt 3:

```text
Attempt 1:
  structured docs + component extraction

Attempt 2:
  encoded-tag / Unicode / <br> correctness

Attempt 3:
  fallback regression + evidence reconciliation
  architect-accepted Complete

Manual validation:
  Shopify page chrome/accessibility text still visible

Attempt 4:
  semantic page-chrome filtering / de-duplication
```

Record:

```text
Attempt 4 implementation commit
final parent report commit
focused tests/count
ESLint
typecheck baseline + zero task-owned diagnostics
source/component audits
git diff --check
branch/worktree synchronization
database submodule synchronization
```

Return:

```yaml
status: review
executor: null
claimed_at: null
attempt: 4
```

and STOP.

Do not start `ARCH-021-SYSTEM-TEST-001`.

### Reviewed Manual Evidence

Developer manual validation screenshot showed the accepted structured renderer
still surfacing Shopify page chrome/accessibility labels such as:

```text
Choose a version:
Anchor to ...
Was this section helpful?
Anchor to Possible returnsPossible returns
```

This is sufficient to reopen the same documentation-normalization task before
terminal system testing.

### Architecture Conformance

Previously accepted C035 safety/component architecture remains conformant.

The reopened correction is limited to semantic server-side cleanup of Shopify
generated documentation chrome.

### Follow-up

`ARCH-021-COMMERCE-035` is reopened Ready for Attempt 4.

`ARCH-021-SYSTEM-TEST-001` returns to Pending because a required implementation
dependency is no longer Complete.
