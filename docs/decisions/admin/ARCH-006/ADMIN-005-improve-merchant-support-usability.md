---
id: ARCH-006-ADMIN-005
architecture_id: ARCH-006
title: Improve Merchant Messages search and translation language selection
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
status: review
priority: 81
executor: copilot
claimed_at: 2026-09-07T09:26:57Z
attempt: 2
depends_on:
  - ARCH-006-ADMIN-004
enables:
  - ARCH-006-SYSTEM-TEST-001
created: 2026-09-06
updated: 2026-09-07T09:35:00Z
---

# ARCH-006-ADMIN-005: Improve Merchant Messages search and translation language selection

## Architecture

`docs/architecture/ARCH-006-merchant-communications-support-inbox.md`

## Objective

Make two bounded usability improvements to the existing Merchant Messages UI:

1. add protected shop autocomplete so a PlatformAdmin can quickly find a support thread by Shopify brand name or shop domain and open that thread directly; and
2. present the current **20 product-supported merchant languages** as a simple, human-readable per-message translation dropdown.

The underlying ARCH-006 translation server remains BCP-47 capable and unchanged. This Admin UI deliberately exposes only the 20 languages the product currently supports. Adding another product-supported language in future requires an explicit UI/task update; it must not happen implicitly because a message happens to contain another language tag.

This remains a UI/read enhancement. It must reuse the accepted Admin support-read boundary, existing Tenant Directory search semantics and accepted ARCH-006 translation action. It must not introduce a second tenant-search architecture or change translation-domain behavior.

## Context

`ARCH-006-ADMIN-004` created the Merchant Messages inbox with a submitted search that currently filters pending threads by shop domain. The existing Tenant Directory search already establishes the desired matching fields:

```text
Shop.domain
OR
ShopBrand.brandName
```

using case-insensitive matching.

This task adds type-ahead suggestions to the Merchant Messages search and improves only the **presentation/input mechanism** for requesting an additional translation. It does not change ownership, compose, translation routing, reconciliation, pending-response or queue semantics.

`ARCH-006-ADMIN-004` is now architect-accepted Complete. This task is Ready and may be claimed independently. The repository agent must not claim any system-test task in the same invocation.

## Dependency Gate

`ARCH-006-ADMIN-004` is architect-accepted `complete`, so this task is now `ready`.

When the repository agent claims it, increment `attempt` from `0` to `1` and follow the normal lifecycle:

```text
ready -> in_progress -> review -> STOP
```

Do not mark the task Complete yourself and do not invoke any system-test task.

## Scope

Implement only these two existing Merchant Messages surfaces:

1. the shop-search input; and
2. the per-message additional-translation target control.

The shop-search behavior must support both:

1. **submitted search** — pressing Enter/Search continues to filter the pending-support list; and
2. **autocomplete selection** — selecting a suggestion opens the selected shop support thread directly.

The search must match **brand name OR domain**, case-insensitively, using the same field semantics as the Tenant Directory.

Autocomplete suggestions must include only shops that already have a `MerchantSupportThread`. Do not suggest a tenant that cannot be opened as a support thread.

## Out of Scope

- Changing the global Tenant Directory search component or its route.
- Fuzzy search, typo correction, ranking services or external search providers.
- Database schema/index/migration changes.
- Searching customer names, phone numbers, email addresses or message body text.
- Creating support threads for shops that do not already have one.
- Ownership, Take/Release/Reassign behavior.
- Compose behavior.
- Translation **server/domain semantics**, including validation, canonicalisation, direction, uniqueness, queue dispatch and reconciliation. The Admin dropdown may expose the current 20 product-supported languages without changing that server capability.
- Reconciliation behavior.
- PlatformAdmin autocomplete/reassignment improvements.
- New package dependencies or UI libraries.
- Redis, BullMQ, OpenAI or Background changes.
- Any system-test execution. System tests remain manually gated by the developer.

## Translation Language Selector Contract

### Architect product/UI decision after Attempt 1

Attempt 1 implemented a message-derived dropdown plus `Other language…`. Manual UI review found that unsuitable for the Admin operator workflow.

The **Attempt 2 contract below supersedes every earlier selector instruction in this task**.

The Admin operator must not need to understand tags such as `fr-CA`, `pt-BR` or `zh-Hant`, and the normal selector must not vary according to whichever translations happen to exist on a particular message.

The dropdown must expose **exactly these 20 currently supported product languages**, in this order:

| Visible label | Submitted value |
|---|---|
| Czech | `cs` |
| Danish | `da` |
| German | `de` |
| English | `en` |
| Spanish | `es` |
| Finnish | `fi` |
| French | `fr` |
| Italian | `it` |
| Japanese | `ja` |
| Korean | `ko` |
| Norwegian Bokmål | `nb` |
| Dutch | `nl` |
| Polish | `pl` |
| Portuguese (Brazil) | `pt-BR` |
| Portuguese (Portugal) | `pt-PT` |
| Swedish | `sv` |
| Thai | `th` |
| Turkish | `tr` |
| Chinese (Simplified) | `zh-Hans` |
| Chinese (Traditional) | `zh-Hant` |

These values correspond to the current 20 merchant-language catalogues already supported by Moda Interact:

```text
cs
da
de
en
es
fi
fr
it
ja
ko
nb
nl
pl
pt-BR
pt-PT
sv
th
tr
zh-Hans
zh-Hant
```

### Exact UI behavior

For every message, render one native `<select>` with this conceptual shape:

```html
<select>
  <option value="">Select language…</option>
  <option value="cs">Czech</option>
  <option value="da">Danish</option>
  <option value="de">German</option>
  <option value="en">English</option>
  <option value="es">Spanish</option>
  <option value="fi">Finnish</option>
  <option value="fr">French</option>
  <option value="it">Italian</option>
  <option value="ja">Japanese</option>
  <option value="ko">Korean</option>
  <option value="nb">Norwegian Bokmål</option>
  <option value="nl">Dutch</option>
  <option value="pl">Polish</option>
  <option value="pt-BR">Portuguese (Brazil)</option>
  <option value="pt-PT">Portuguese (Portugal)</option>
  <option value="sv">Swedish</option>
  <option value="th">Thai</option>
  <option value="tr">Turkish</option>
  <option value="zh-Hans">Chinese (Simplified)</option>
  <option value="zh-Hant">Chinese (Traditional)</option>
</select>
```

The exact JSX may use `.map()` over a local constant rather than writing 20 literal `<option>` nodes. Prefer a single deterministic constant such as:

```ts
const SUPPORTED_TRANSLATION_LANGUAGE_OPTIONS = [
  { value: 'cs', label: 'Czech' },
  { value: 'da', label: 'Danish' },
  { value: 'de', label: 'German' },
  { value: 'en', label: 'English' },
  { value: 'es', label: 'Spanish' },
  { value: 'fi', label: 'Finnish' },
  { value: 'fr', label: 'French' },
  { value: 'it', label: 'Italian' },
  { value: 'ja', label: 'Japanese' },
  { value: 'ko', label: 'Korean' },
  { value: 'nb', label: 'Norwegian Bokmål' },
  { value: 'nl', label: 'Dutch' },
  { value: 'pl', label: 'Polish' },
  { value: 'pt-BR', label: 'Portuguese (Brazil)' },
  { value: 'pt-PT', label: 'Portuguese (Portugal)' },
  { value: 'sv', label: 'Swedish' },
  { value: 'th', label: 'Thai' },
  { value: 'tr', label: 'Turkish' },
  { value: 'zh-Hans', label: 'Chinese (Simplified)' },
  { value: 'zh-Hant', label: 'Chinese (Traditional)' },
] as const;
```

Use this exact value set and visible labels unless TypeScript syntax requires a harmless formatting variation.

### Required removal of Attempt 1 selector behavior

Remove the Attempt 1 message-derived selector machinery from this component.

The final implementation must **not** derive normal choices from:

```text
message.displayLanguageTag
message.translations[].targetLanguageTag
PLATFORM_SUPPORT_LANGUAGE_TAG
```

Remove selector-only helpers/state that are no longer required, including the current semantic equivalents of:

```text
OTHER_LANGUAGE_VALUE
languageOptionLabel()
languageOptions()
customLanguageTag
Intl.DisplayNames
```

If `PLATFORM_SUPPORT_LANGUAGE_TAG` is no longer used elsewhere in this component after this correction, remove that unused import.

Do not leave dead selector code behind.

### No `Other language…` in this Admin UI

Attempt 2 must remove:

```text
Other language…
```

and the custom BCP-47 text field entirely from the Admin Merchant Messages selector.

There must be:

```text
Select language…
+ exactly 20 supported choices
```

and nothing else.

This is an Admin product-UI constraint only. Do **not** narrow or rewrite the server's existing `LanguageTagSchema` validation. Do **not** change `requestAdditionalTranslationAction()` or `requestAdditionalTranslation()`.

The backend may remain capable of accepting other valid BCP-47 tags for future callers/features. This task only says that this Admin control exposes the current product-supported 20.

### Submission behavior

The selected `<option value>` is the exact value sent to the existing action:

```ts
requestAdditionalTranslationAction({
  messageId: message.id,
  targetLanguageTag: languageSelection,
});
```

Required examples:

```text
visible: French
sent:    fr

visible: Portuguese (Brazil)
sent:    pt-BR

visible: Chinese (Traditional)
sent:    zh-Hant
```

Do not send the visible human-readable label.

When the placeholder is selected:

```text
languageSelection === ''
```

the Translate button must remain disabled and the form must not submit a translation request.

### Existing translation history/status behavior

Do not change the existing translation history controls.

Existing rows such as:

```text
fr-FR
de-DE: failed
Retry / Reconcile
```

may continue to show their canonical target tag because they represent durable translation records, not the operator's language-picking control.

Do not use this task to rename or reformat historical translation badges/buttons.

Do not alter:

- AVAILABLE/PENDING/FAILED semantics;
- Retry/Reconcile;
- translation uniqueness;
- queue publication;
- server canonicalisation;
- translation direction;
- reconciliation.

### Accessibility

Keep the message-specific `<label>` / `<select id>` relationship already introduced in Attempt 1.

Native select keyboard behavior is sufficient.

No UI/select library may be added.

### Deterministic regression requirements

Update `tests/security/admin-merchant-support-ui.test.mjs`.

The test must prove the final **actual component contract**.

At minimum:

1. the component defines one fixed supported-language option source containing exactly 20 values;
2. the values are exactly, in order:

```text
cs, da, de, en, es, fi, fr, it, ja, ko, nb, nl, pl,
pt-BR, pt-PT, sv, th, tr, zh-Hans, zh-Hant
```

3. human-facing labels include at minimum these representative assertions:

```text
Czech
English
French
Portuguese (Brazil)
Portuguese (Portugal)
Chinese (Simplified)
Chinese (Traditional)
```

4. the normal selector begins with `Select language…`;
5. there is no `Other language…` option;
6. there is no `Custom BCP-47 language tag` input;
7. there is no selector use of `Intl.DisplayNames`;
8. the selector does not derive options from `message.displayLanguageTag`;
9. the selector does not derive options from
   `message.translations.map(...targetLanguageTag...)`;
10. the selected canonical value is still passed as `targetLanguageTag` to
    `requestAdditionalTranslationAction`;
11. Translate is disabled while no language is selected;
12. existing translation-view and Retry/Reconcile controls remain present.

Do not weaken the already-passing autocomplete tests.

## Exact Matching Contract

Use these durable fields only:

```text
commerce.Shop.domain
shopify.ShopBrand.brandName
```

Matching is case-insensitive substring matching for both fields.

Equivalent logical predicate:

```text
lower(domain) contains lower(query)
OR
lower(brandName) contains lower(query)
```

Do not search IDs as user-facing autocomplete text.

The submitted pending-list search must be extended from domain-only matching to the same brand-name-or-domain matching so Enter/Search and autocomplete do not disagree about what constitutes a shop match.

## Bounded Server Capability

Add one protected read capability in:

```text
src/lib/admin/merchant-support.ts
```

Preferred exported shape:

```ts
export type MerchantSupportShopSuggestion = {
  threadId: string;
  shopId: string;
  domain: string;
  brandName: string | null;
  needsAdminResponse: boolean;
};

export async function getMerchantSupportShopSuggestions(input: {
  query: string;
  limit?: number;
}): Promise<MerchantSupportShopSuggestion[]>;
```

Required behavior:

1. Call the existing PlatformAdmin read guard. Do not create a weaker auth path.
2. Trim the query.
3. Bound input to the existing Admin search maximum of 120 characters.
4. If the trimmed query length is less than **2 characters**, return `[]` without running an unbounded shop/thread scan.
5. Hard-cap suggestions at **8** even if the caller asks for more.
6. Join only the data needed to resolve a support thread + display brand/domain.
7. Return presentation-safe fields only.
8. Order deterministically:
   - pending-response threads first (`needsAdminResponse = true`);
   - then newest `lastMessageAt` first, nulls last;
   - then domain ascending;
   - then thread id ascending as final tie-breaker.
9. Do not calculate Tenant Directory KPIs and do not call `getTenantDirectory()` merely to obtain suggestions.

The implementation may reuse existing SQL/query helpers where doing so is clear, but must not duplicate auth or introduce a generic repository-local search framework.

## Pending Search Alignment

Update `getPendingMerchantSupportThreads()` so its existing `search` input matches:

```text
Shop.domain OR ShopBrand.brandName
```

case-insensitively.

Keep all existing pending filters and pagination semantics unchanged:

```text
all
unassigned
assigned-to-me
assigned-to-others
```

Do not change `needsAdminResponse = true` for the pending list.

## Server Action

Add one thin server action in:

```text
src/app/actions/merchant-support.ts
```

Preferred shape:

```ts
export async function getMerchantSupportShopSuggestionsAction(input: {
  query: string;
}) {
  return getMerchantSupportShopSuggestions({ query: input.query, limit: 8 });
}
```

The action must not accept or trust admin identity, shop identity, thread ownership or database filters from the browser beyond the search text.

The server capability remains the authorization boundary.

## Client Autocomplete Behavior

Modify only the existing Merchant Messages support-search UI in:

```text
src/components/admin/merchant-support-inbox.tsx
```

Do not change the global `SearchInput` used by the Tenant Directory.

### Existing form behavior must remain

The existing GET search form must still submit to:

```text
/merchant-support
```

with:

```text
search=<typed text>
filter=<current filter>
```

Pressing Enter or the Search button must continue to perform the normal server-rendered pending-list search.

### Autocomplete rules

Use the same text input as the submitted search. Do not add a second search box.

Required behavior:

1. Keep a controlled input value initialised from the `search` prop.
2. When trimmed input has fewer than 2 characters:
   - clear suggestions;
   - do not call the suggestion action.
3. When input has 2+ characters:
   - wait **250 ms** after the last keystroke before requesting suggestions;
   - request at most 8 suggestions through the protected server action.
4. Ignore stale/out-of-order results. Use a monotonically increasing request sequence/ref (or equivalent deterministic stale-response guard). An older request must never replace suggestions from a newer input value.
5. Close the suggestion list when:
   - the input becomes shorter than 2 characters;
   - Escape is pressed;
   - a suggestion is selected;
   - the input loses focus after allowing a pointer selection to complete.
6. Do not use `dangerouslySetInnerHTML` or highlight by injecting HTML.

### Suggestion rendering

Each suggestion must render:

```text
primary: brandName when present, otherwise the same domain-derived tenant display fallback used by the existing Tenant Directory formatting helper
secondary: exact shop domain
optional status: Pending response when needsAdminResponse=true
```

Reuse `tenantName()` from:

```text
src/lib/admin/format.ts
```

for the brand/domain display fallback. Do not create another domain-to-display-name formatter.

### Selection behavior

Selecting a suggestion must open the exact support thread using its server-returned `threadId`.

Use the existing `/merchant-support` route and existing query helper. Preserve the current ownership filter. Reset pending pagination to page 1. Clear the submitted pending-search query so selecting a resolved/non-pending thread does not intentionally leave an empty filtered pending list beside an otherwise valid selected thread.

Equivalent target query updates:

```text
thread=<selected threadId>
page=1
search=<removed>
filter=<preserved>
```

Do not use the shop domain as the thread identity.

## Accessibility Contract

Implement the input/suggestion relationship as an accessible combobox/listbox without adding a UI dependency.

At minimum:

- input has `role="combobox"`;
- `aria-autocomplete="list"`;
- `aria-expanded` reflects whether suggestions are visible;
- `aria-controls` points to the suggestion list when present;
- suggestion container has `role="listbox"`;
- each suggestion has `role="option"`;
- ArrowDown/ArrowUp moves the active suggestion;
- Enter selects the active suggestion **only when one is active**; otherwise normal form submission remains possible;
- Escape closes suggestions and clears active suggestion;
- active option is exposed through `aria-activedescendant` or an equivalent accessible pattern.

Do not add a third-party combobox package.

## Exact File Boundary

Production/test changes are permitted only in:

```text
src/lib/admin/merchant-support.ts
src/app/actions/merchant-support.ts
src/components/admin/merchant-support-inbox.tsx
tests/security/admin-merchant-support.test.mjs
tests/security/admin-merchant-support-ui.test.mjs
```

The translation-selector requirement should normally need changes only in
`merchant-support-inbox.tsx` and its focused UI test. Do not modify the accepted
translation server implementation merely to support the selector. The server/action
files in this boundary are present because the shop-autocomplete portion of this same
task requires them.

If a genuinely required change falls outside this list, stop, set the task `blocked`, record the reason and return to `moda_architect`.

In particular, do not edit:

```text
src/components/admin/search-input.tsx
src/components/admin/admin-shell.tsx
src/lib/admin/data.ts
database/
package.json
package-lock.json
```

The Tenant Directory files are reference material only for matching/display semantics.

## Work Items

- [x] Inspect the accepted ADMIN-004 implementation after it is Complete.
- [x] Read existing Tenant Directory matching in `src/lib/admin/data.ts` and display fallback in `src/lib/admin/format.ts` as reference only.
- [x] Add bounded protected support-thread suggestions by brand/domain.
- [x] Align submitted pending search to brand/domain matching.
- [x] Add the thin server action.
- [x] Convert the existing support search input into the bounded autocomplete without adding a second input.
- [x] Add deterministic stale-response protection and keyboard/accessibility behavior.
- [x] Add focused server/UI regression coverage.
- [x] Run complete validation.
- [x] Return this task to `review` and STOP.

## Interfaces / Contracts

Consumes the accepted ADMIN-004 support UI/read boundary and existing PlatformAdmin authentication.

No new cross-repository contract is created.

No Shared package change is required.

The browser supplies only search text. Thread identity comes from the protected server suggestion result.

## Dependencies

Explicit task dependency is authoritative:

```text
ARCH-006-ADMIN-004
```

Do not infer a dependency on system tests. System tests remain terminal/manual-gated.

## Enables

`ARCH-006-SYSTEM-TEST-001`

This is informational until `moda_architect` updates/promotes the final terminal system-test dependency state. The repository agent must not modify or claim the system-test task.

## Acceptance Criteria

- [x] Autocomplete does not execute for fewer than 2 trimmed characters.
- [x] Server returns at most 8 presentation-safe suggestions.
- [x] Suggestions include only shops with existing support threads.
- [x] Brand-name and domain substring matches are both supported case-insensitively.
- [x] Submitted pending search uses the same brand/domain matching semantics.
- [x] Existing pending ownership filters and pagination remain unchanged.
- [x] Suggestion results are PlatformAdmin-protected server reads.
- [x] Client cannot provide a trusted thread/shop/admin identity to influence the suggestion query.
- [x] Stale slower responses cannot overwrite newer suggestion results.
- [x] Selecting a suggestion opens the exact returned `threadId`, preserves filter, resets page and clears submitted search.
- [x] Enter with no active option still submits the existing search form.
- [x] Keyboard/ARIA combobox behavior is present without a new dependency.
- [x] Existing `tenantName()` fallback is reused; no duplicate domain display formatter is added.
- [x] No ownership, translation, compose, reconciliation, queue or database-schema semantics change.

## Additional Acceptance Criteria — Translation Selector

- [x] The per-message translation target is one native dropdown.
- [x] The dropdown contains exactly the 20 currently supported language choices plus the empty `Select language…` placeholder.
- [x] The 20 submitted values are exactly `cs`, `da`, `de`, `en`, `es`, `fi`, `fr`, `it`, `ja`, `ko`, `nb`, `nl`, `pl`, `pt-BR`, `pt-PT`, `sv`, `th`, `tr`, `zh-Hans`, `zh-Hant`, in that order.
- [x] Operators see human-readable names, not raw language tags, as option labels.
- [x] Portuguese (Brazil), Portuguese (Portugal), Chinese (Simplified), and Chinese (Traditional) are visibly distinguishable.
- [x] The selected canonical tag, not the display label, is sent to `requestAdditionalTranslationAction`.
- [x] `Other language…` and the custom BCP-47 text input are removed from this Admin UI.
- [x] Message-derived option construction is removed.
- [x] `Intl.DisplayNames` selector machinery is removed.
- [x] Translate is disabled when no language has been selected.
- [x] Existing translation history/view and Retry/Reconcile controls remain unchanged.
- [x] Server `LanguageTagSchema` and translation-domain behavior remain unchanged.
- [x] No new dependency is added.

## Validation

Run at minimum:

```bash
node --test tests/security/admin-merchant-support-ui.test.mjs
node --test tests/security/admin-merchant-support.test.mjs
npm test
npx tsc --noEmit --pretty false
npm run lint
npm run build
npm run prisma:validate
git diff --check
```

Focused server proof must include:

1. query shorter than 2 characters returns no suggestions without executing the suggestion database query;
2. result count is hard-capped to 8;
3. generated/read query includes domain + brandName matching;
4. suggestions contain support `threadId`, shop id, domain, brand name and pending flag only;
5. pending-list search uses the same domain + brandName predicate and retains ownership filter conditions.

Focused UI proof must include at minimum source/behavior evidence for:

1. one existing search input, not two;
2. 250 ms debounce;
3. stale-response sequence/ref protection;
4. 2-character minimum;
5. at-most-8 server action request;
6. reuse of `tenantName()`;
7. selection by returned `threadId` and query updates `thread`, `page=1`, clears `search`, preserves `filter`;
8. combobox/listbox/option ARIA roles and ArrowUp/ArrowDown/Enter/Escape handling;
9. Enter without an active suggestion does not prevent normal form submit.

Do not add a new testing framework or package to satisfy this task. Use the repository's existing Node/security test style.

The known historical full-suite Admin internationalisation assertion for Shared `0.7.0` may remain the only unchanged baseline failure. Any new failure is task-owned.

## Implementation Notes

Keep this task small. Do not refactor the global Admin shell or Tenant Directory search to create a generic autocomplete abstraction. A future repeated need may justify extraction; one support-specific use does not.

## Completion Report

### Status

Ready for Review (Attempt 2).

### Files Changed

- `moda-interact-admin/src/lib/admin/merchant-support.ts`
- `moda-interact-admin/src/app/actions/merchant-support.ts`
- `moda-interact-admin/src/components/admin/merchant-support-inbox.tsx`
- `moda-interact-admin/tests/security/admin-merchant-support.test.mjs`
- `moda-interact-admin/tests/security/admin-merchant-support-ui.test.mjs`

### Work Completed

- Attempt 2 corrected only the translation selector and its focused source-boundary regression. The accepted autocomplete production/server/action implementation was not changed.
- The selector now contains exactly 20 normal language choices, in order: `cs`, `da`, `de`, `en`, `es`, `fi`, `fr`, `it`, `ja`, `ko`, `nb`, `nl`, `pl`, `pt-BR`, `pt-PT`, `sv`, `th`, `tr`, `zh-Hans`, `zh-Hant`.
- Human-readable labels are shown while the canonical language tags remain the submitted option values. `Other language…`, custom BCP-47 input, message-derived option construction, and `Intl.DisplayNames` were removed.
- The existing `requestAdditionalTranslationAction` contract, translation history/view, and Retry/Reconcile behavior were unchanged.
- Added a PlatformAdmin-protected, bounded support-thread suggestion capability. It trims and caps input at 120 characters, skips database work below two characters, caps results at eight, joins only existing support threads, matches `Shop.domain` or `ShopBrand.brandName` case-insensitively, and orders pending-response threads deterministically.
- Aligned submitted pending search with the same brand/domain predicate while preserving ownership filters and pagination.
- Added the thin server action and an accessible native combobox with 250 ms debounce, stale-response sequence protection, 2-character minimum, eight-result bound, keyboard navigation, Escape/blur closing, and exact returned `threadId` navigation that preserves `filter`, resets `page`, and clears `search`.
- Reused `tenantName()` for suggestion display fallback and added presentation-safe pending-response status text.
- Replaced the Attempt 1 message-derived language control with a fixed native dropdown of the 20 supported product languages and human-readable labels.

### Validation Results

- Attempt 2 focused UI security tests: 7 passed.
- Attempt 2 focused server security tests: 14 passed.
- Full `npm test`: 102 passed, 1 known unchanged failure out of 103. `admin-internationalization.test.mjs` still expects Shared `0.7.0`, while the accepted dependency is `0.7.1`.
- `npx tsc --noEmit --pretty false`: passed.
- `npm run lint`: passed with only the two pre-existing `queue-monitor.tsx` hook warnings.
- `npm run build`: passed with existing Next.js workspace-root and BullMQ optional-dependency warnings.
- `npm run prisma:validate`: passed.
- `git diff --check`: passed.

### Deviations

None. No schema, migration, package, shared-contract, queue, ownership, translation-domain, compose or reconciliation semantics were changed.

### Assumptions

The existing Admin full-suite Shared-version assertion and queue-monitor lint warnings remain unchanged baselines.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review — Attempt 1 — 2026-09-07

### Review Status

**Not accepted — return to Ready for Attempt 2.**

The autocomplete portion of Attempt 1 is accepted in substance and must not be
rewritten in Attempt 2.

Manual UI review rejects only the translation-language selector presentation.
Attempt 1 derived choices from message data and exposed an `Other language…`
custom BCP-47 path. That produces a sparse/technical operator experience and
does not present the complete set of languages Moda Interact currently supports.

The developer has explicitly changed the Admin UI requirement:

```text
show all 20 currently supported languages
+
show human-readable names
+
do not require the operator to know BCP-47 tags
```

Attempt 2 is therefore a bounded UI/test correction only.

### Attempt 2 exact file boundary

Production/test changes are permitted only in:

```text
moda-interact-admin/src/components/admin/merchant-support-inbox.tsx
moda-interact-admin/tests/security/admin-merchant-support-ui.test.mjs
```

plus this task file and `docs/decisions/admin/ARCH-006/_index.md` for normal task bookkeeping.

Do **not** modify:

```text
src/lib/admin/merchant-support.ts
src/app/actions/merchant-support.ts
```

The accepted autocomplete server/action implementation must remain unchanged.

Do not modify schema, migrations, auth, packages, Shared, Shopify, Background,
Gateway or system-test code.

### Attempt 2 preservation requirements

Preserve Attempt 1 autocomplete behavior exactly:

```text
brand/domain matching
2-character minimum
250 ms debounce
8-result cap
stale-response protection
keyboard/ARIA combobox
exact threadId navigation
normal submitted search
```

Do not refactor the autocomplete while correcting the selector.

Preserve accepted ADMIN-004 behavior.

### Attempt 2 lifecycle

When claimed:

```text
attempt: 1 -> 2
status: ready -> in_progress
```

After implementation/validation:

```text
status: review
```

Then STOP.

Do not claim `ADMIN-005` follow-on work or any system-test task in the same invocation.

## Completion Report Requirements — Attempt 2

When returning Attempt 2 to `review`, report explicitly:

- autocomplete production/server/action code was not changed;
- the selector now contains exactly 20 normal language choices;
- the exact 20 values used;
- human-readable labels are shown and raw tags are retained only as option values;
- `Other language…`, custom BCP-47 input, message-derived option construction and
  `Intl.DisplayNames` selector machinery were removed;
- `requestAdditionalTranslationAction` contract was not changed;
- translation history and Retry/Reconcile behavior were not changed;
- all focused/full validation results.

Return only this task to `review` and STOP.
