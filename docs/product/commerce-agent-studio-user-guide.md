# CommerceAgent Studio user guide

**Audience:** Moda team members who configure and test the assistant used in WhatsApp checkout-recovery conversations.  
**Edition:** Pre-release · 21 September 2026.

This guide describes the approved Studio workflow. In the checkout inspected for
this edition, the screens and component services exist, but production Studio
data and saved-preview loading still use unavailable adapters. Backend, Studio
and preview integration are tracked by COMMERCE-013, COMMERCE-018 and COMMERCE-019.
The instructions below describe the intended connected experience, not a claim
that every operation is available in a deployed environment today. The approved
prototype contains sample data and simulated actions.

## Contents

- [Understand what you are configuring](#understand-what-you-are-configuring)
- [Sign in and find your way around](#sign-in-and-find-your-way-around)
- [Configure a feature](#configure-a-feature)
- [Create and test a tool](#create-and-test-a-tool)
- [Explore Shopify without leaving Studio](#explore-shopify-without-leaving-studio)
- [Publish and activate a release](#publish-and-activate-a-release)
- [Change response instructions and structured details](#change-response-instructions-and-structured-details)
- [Test conversations](#test-conversations)
- [Inspect a merchant's available tools](#inspect-a-merchants-available-tools)
- [Worked example: help customers with a discount](#worked-example-help-customers-with-a-discount)
- [Maintain configurations and resolve problems](#maintain-configurations-and-resolve-problems)
- [Page reference](#page-reference)

## Understand what you are configuring

Studio lets the Moda team define what CommerceAgent can do and how it should
respond. Merchants receive behaviour according to their eligible features and
configuration. Customers continue using WhatsApp; they do not use Studio.

| Term | Meaning |
|---|---|
| Feature | An offering managed in Moda Admin, with plan and merchant eligibility rules. Studio configures its conversational behaviour. |
| Tool | A reusable action the assistant can choose when it needs facts. Its definition explains when to use it, what information it accepts, how information is retrieved and how results are presented. |
| Behaviour / capability | Instructions, settings and a selection of exact tool versions. A feature can have more than one behaviour configuration. |
| Draft | Saved work that can still be edited. Saving does not make it live. |
| Published version or revision | A validated, fixed copy of a tool or behaviour. Later changes require another draft. |
| Release | A fixed collection of published behaviour revisions, plus response instructions and the response-details definition. |
| Active release | The release selected for new conversations in the environment. Creating a release does not activate it. |

The usual workflow is:

**Create tool → Test and publish tool version → Attach it to behaviour → Publish
behaviour revision → Create release → Test → Activate.**

You can reuse an existing published tool and skip tool creation. A behaviour can
also contain instructions without any tool bindings.

At the start of a conversation, the system identifies the merchant and recovery,
then selects the permitted tools from the release and merchant configuration.
CommerceAgent chooses among those tools when answering. It cannot gain newly
published tools midway through that conversation. When the available tools cannot
support an answer, it should refer the customer to the store rather than invent
information.

## Sign in and find your way around

1. Open the Studio address provided by your team.
2. Sign in using the Google account provisioned for your Moda administrator account.
3. Confirm your role and the active release shown in the application header.

Google sign-in alone does not grant Studio access. **Access denied** means the
account does not currently have the required active staff permission. Ask a Moda
administrator to check your account. Use **Sign out** to change accounts.

| Role | What you can do |
|---|---|
| ADMIN | Create and edit drafts, explore Shopify, validate definitions and test configurations. |
| SUPER_ADMIN | All ADMIN actions, plus publishing, creating releases, activation, rollback and enabling or disabling tools and configurations. |

The sidebar contains **Features**, **Tools**, **Explore Shopify**, **Test
conversations**, **Releases** and **Merchants**, in that order. **Platform
configurations** is a link on the Features page, not a separate sidebar item.

Forms do not autosave. Use **Save draft** before leaving an editor. When warned
about unsaved changes, choose **Stay** to continue editing or **Discard unsaved
changes** to leave without saving local edits. This does not delete a saved draft.
Refreshing, signing out or losing access can discard unsaved work.

## Configure a feature

1. Open **Features** and search by the feature's name or key.
2. Select **Configure behaviour** for the feature.
3. Review its existing configurations. Open one to edit it, or choose **Add
   behaviour** and supply a unique capability key, display name and description.
4. In the behaviour editor, select **Create draft**. Start from a published
   revision or supply an initial prompt for a new configuration.
5. Write instructions describing the help this behaviour should provide and
   what to do when facts are unavailable.
6. Set the result limits where needed: search results from 1–20 and
   recommendations from 1–3. These limits do not override stricter system limits.
7. Choose **Add tool** and select a published, enabled tool and its exact version.
   Repeat for each required tool. **Create tool** opens the tool-authoring flow
   and preserves a return path to this configuration.
8. Select **Save draft**, then **Test behaviour**.
9. After reviewing the results, a SUPER_ADMIN can publish the capability revision.
   Continue to release creation when it is ready for use.

**Change version** updates the selected draft binding after you review the
definition difference. **Remove** removes a binding from the draft; it does not
delete the reusable tool. Neither change is saved until you select **Save draft**.

The feature catalogue belongs to Moda Admin. Use **Manage feature in Admin** to
change feature metadata, plans or availability. Studio does not create features
or edit merchant preferences. A feature without conversational behaviour is not
necessarily incomplete; some features only concern billing or other services.

| Status | How to interpret it |
|---|---|
| Not configured | No Commerce behaviour is linked to this feature. |
| Draft only | Configurations exist, but none is included in the active release. |
| Live | At least one linked configuration is included in the active release. Check merchant eligibility separately. |
| Unpublished changes | Draft changes differ from the version in use. |
| Disabled configuration | A configuration is disabled, even if published versions exist. |

For shared platform instructions, open **Features → Platform configurations**.
These include the core conversation instructions and recovery-policy behaviour.
The page does not create new reserved platform configurations.

## Create and test a tool

Open **Tools → New tool**. Enter a display name, an immutable MCP name—the name
the assistant sees—and an optional staff description. Creating this record does
not attach it to a feature. Select **Create draft** and choose a proposed version;
a first version starts at `1.0.0`.

The tool editor has **Metadata**, **Definition** and **History** tabs. The
Definition tab guides you through six steps:

| Step | What to enter or check |
|---|---|
| 1. Purpose | Explain what the tool does and when the assistant should use it. Review the proposed version. |
| 2. Inputs | Define the fields the assistant may supply: name, description, type, whether required and allowed bounds. |
| 3. Retrieve information | Choose a **Public Shopify query** or an available **Recovery/discount operation**. Select the documented operation/version or build a permitted query. |
| 4. Map inputs | Map each required argument to a declared **Agent input** or a type-valid **Fixed value**. Resolve missing or incompatible mappings. |
| 5. Response | Choose **Text** or **List**, select the result path and insert the allowed field chips. Supply unavailable text and, for lists, empty-result text. |
| 6. Review and test | Inspect the assistant-facing descriptor separately from the retrieval definition, resolve validation errors and test the saved revision. |

Shop identity and credentials are supplied by the system, not by editable tool
inputs. Response templates present retrieved facts; they do not add calculations
or unsupported expressions. CommerceAgent uses the result to compose the
customer-facing reply.

You can save an incomplete draft when its structure is valid. It remains **Not
ready to publish** until the required definition and validation are complete.
Save before moving to Explore Shopify or Test conversations. Any meaningful edit
makes earlier validation and test results stale; validate and test again.

A SUPER_ADMIN selects **Publish tool version**, reviews the differences, version,
validation and affected configurations, then supplies a reason and confirms.
Publishing does not update existing feature bindings or activate a release.
If you arrived from a behaviour, **Attach this version** returns to its association
dialog; save the behaviour draft to retain the binding.

Use **History** to open or compare exact versions. Published versions are read-only.
The tool's display name and staff description can be edited in Metadata; its MCP
name remains fixed.

## Explore Shopify without leaving Studio

Open **Explore Shopify**, or choose **Browse Shopify** while editing a tool.

- **Documentation:** search, select a result and read it in Studio. Source links
  are references; leaving Studio is not required for the supported authoring flow.
- **Schema and query builder:** browse available types, fields and arguments,
  read their descriptions and select permitted fields to build a query. Advanced
  users can inspect and edit GraphQL through the same validation rules.

Check the API version shown on the page. This design uses the pinned Shopify
Storefront API version `2026-07`. Documentation may describe APIs or fields that
this execution service cannot use. Restricted or token-required fields can be
explained without being available for selection.

Select **Validate** to check the query against the supported schema. **Use in
tool** shows the proposed retrieval changes and returns to the tool editor; select
**Save draft** there to keep them. If you started without a tool draft, Studio
takes you through tool and draft creation first.

Schema validation confirms the query's supported structure. It does not confirm
a merchant's current inventory, prices or discount eligibility. The query builder
does not invoke a live merchant tool.

## Publish and activate a release

1. Open **Releases → Create release**.
2. In **Members**, select one published revision for each included behaviour.
   Keep the required core conversation configuration. Review the exact tool
   versions and resolve any conflicting versions of a shared tool.
3. In **Response contract**, review the response instructions and details
   definition. Validate any changes.
4. Test the selection using **Test conversation**, then return to the composer.
5. In **Review**, check differences from the active release and enter a reason.
6. A SUPER_ADMIN selects **Create release**. Studio opens the resulting release.
7. Review the release, then select **Activate** and confirm its effect on new
   conversations.

**Save**, **Publish**, **Create release** and **Activate** are separate stages.
Completing an earlier stage does not complete a later one. A failure later in the
process does not remove versions already published.

Activation affects new conversations. Existing conversations retain the versions
and tools granted when they began. They do not automatically adopt the new release.

To roll back, open a previous compatible release from **Releases**, select
**Rollback to this release**, review the target and supply a reason. Rollback
changes the selection for new conversations; it does not rewrite release history
or replace existing conversation grants.

## Change response instructions and structured details

Open a release's **Response contract** tab. Select **Edit as new release** to
start from that exact release's members and response definition.

The composer separates:

- **Fixed delivery fields:** the fields the messaging system requires. These are
  shown with descriptions and cannot be changed here.
- **Instructions:** editable guidance for producing the response.
- **Details JSON Schema:** the supported structure for additional response data.
  Use the built-in baseline, examples and keyword reference.

Enter an example final response and select **Validate**. Resolve the indicated
field errors before testing or creating the release. If you do not need additional
structured information, use the supplied empty-details baseline.

In the preview, **Reply** shows customer-facing text and **Structured details**
shows the additional data separately. Structured details are not sent as the
WhatsApp reply. Do not require facts the available tools cannot establish.

The normal path is **Edit as new release → Response contract → Validate → Test
conversation → Back → Review → Create → Activate**. Test-and-return preserves the
unsaved composer within the current signed-in tab. Refreshing or signing out
clears that handoff; **Draft unavailable—return to Releases** means it must be
recreated. Testing never publishes or activates the draft.

## Test conversations

Open **Test conversations** from the sidebar or use a Test action in a tool,
behaviour, release or merchant page. Entry from another page preselects its saved
configuration and provides a return link.

### Test one tool

1. Select **Tool test** and choose a saved tool revision.
2. Select a synthetic scenario: success, empty result, missing fact or provider failure.
3. Enter the required tool inputs and select **Run** once.
4. Review mapped inputs, structured facts, rendered text and any validation errors.
5. Return to the tool editor to change its definition, save and test again.

These tests use fixtures, not live Shopify inventory. Changing the test input
invalidates the displayed success until you run it again.

### Test a conversation

1. Select **Conversation** and choose saved behaviour revisions or a release.
2. Set the synthetic feature flags and fixture basket.
3. Start in **Fixture** mode for repeatable scripted results. If configured,
   explicitly select **Model** mode to test model behaviour within the displayed
   preview budget. Model mode still uses fixture tools and inventory.
4. Select **Start conversation** to freeze that preview's instructions and tools.
5. Enter a customer message, select **Send**, and review the reply and trace.
6. Check which tools were discovered and called, their inputs and returned facts,
   and whether the final answer was supported.

Useful checks include a normal product question, missing information, an
unavailable provider, an unrelated request that should be referred to the store,
and a clear customer message in a different language. The intended language rule
is to start from the shop's configured language and respond to a clearly detected
different language during the conversation; a customer's phone prefix does not
select the language.

Use **Cancel run** to request cancellation and wait for a confirmed status.
**Reset conversation** abandons the synthetic state and starts a fresh preview.
Changing the selected release, tools or flags requires a reset; an existing
preview must not silently gain new tools.

The designed preview limits include 20 turns, bounded history and 24-hour state
retention, with additional model budgets shown in the UI. Previewing does not send
WhatsApp messages, modify a real checkout or test a merchant's live inventory.

## Inspect a merchant's available tools

1. Open **Merchants** and search by shop ID or domain.
2. Open the merchant to review its plan, active release and feature eligibility.
3. Read the individual inclusion or exclusion reasons: feature availability,
   plan mapping, activation mode, merchant preference and published behaviour.
4. Review **Agent tool list · new conversation** for the resulting names, exact
   versions and source configurations.
5. Expand **Agent descriptor** to see what the assistant receives: the tool's
   name, description and input definition.

The Tools library lists reusable tools across Studio. The merchant inspection page
shows the filtered selection for that merchant. A published tool in the library
is not necessarily available to every merchant.

This is a read-only preview of a **new** conversation's selection. It does not
create a conversation grant, show an existing customer's conversation or change
the merchant's plan and preferences. **Test this configuration** copies the
selection into a synthetic preview; it does not copy live merchant credentials
or inventory.

## Worked example: help customers with a discount

This example assumes the feature already exists in Moda Admin and the required
discount and product operations are available in Studio. Names are illustrative;
select actual published tools and documented operations from your environment.

1. Find the relevant feature in **Features** and choose **Add behaviour**.
2. Draft instructions to check the recovery basket and permitted offer, explain
   eligibility using returned facts, and suggest qualifying or similar products
   only when the available tools support that conclusion.
3. Reuse published tools for the required checks, or create them through the
   documented retrieval operations. Test each new tool and publish its version.
4. Attach the exact versions to the behaviour and save the draft.
5. Test a qualifying basket, a non-qualifying basket, no suitable alternative and
   unavailable discount facts. Check that the reply makes no unsupported promise
   of savings or eligibility.
6. Publish the behaviour revision, include it in a release, test the release and
   activate it after review.
7. Open **Merchants** and confirm that an eligible merchant receives the intended
   tools and that exclusion reasons explain why another merchant does not.

The assistant chooses among its granted tools while answering; the team does not
write a fixed tool sequence for every possible customer message. Configuring this
behaviour does not itself create a Shopify discount or alter its rules.

## Maintain configurations and resolve problems

For an ordinary improvement, create a draft from the exact published version,
edit, test, publish and assemble a new release. Review shared-tool usage before
changing bindings. Publishing a newer tool version does not replace references
to older versions automatically.

**Disable tool** is a separate control with a broader effect: it blocks execution
of that tool, including calls from existing grants. Review the usage information
and confirmation before disabling it. Enabling it does not add new tool versions
to old conversations.

| What you see | What to do |
|---|---|
| Action is pending | Wait for its result. Conflicting actions are disabled to prevent duplicate submissions. |
| Unknown outcome or a timeout after submitting | Use the offered reconciliation/retry for that original action. Do not create a second tool, release or operation to guess whether the first succeeded. |
| Another user changed the record | Keep your local input, reload the current record, compare changes and deliberately save against the refreshed version. |
| Activation conflict | Refresh the active-release information and confirm again only after reviewing the new state. |
| Validation errors | Correct the indicated fields. Test success from before an edit does not validate the edited definition. |
| Service or schema unavailable | Retain your draft and retry when the service returns. Unavailable is not the same as an empty result. |
| Publish or Activate is unavailable for your role | Ask a SUPER_ADMIN to review and perform the publication step. |
| A tool is absent from a merchant's list | Check feature eligibility, enabled state, exact published bindings and active-release membership in Merchants. |
| New behaviour is absent from an existing conversation | Existing conversations retain their initial selection. Inspect the new-conversation list or start a fresh synthetic preview. |
| Preview is Unknown, expired or over budget | Reconcile an uncertain run first. Reset expired state or follow the displayed budget limits; do not repeatedly submit the same message. |

## Page reference

Routes below are relative to the Studio address. `[id]` means the selected record,
not text to type into the address bar.

| Page | Where to find it | Purpose / return path |
|---|---|---|
| U01 · Sign in | `/sign-in` | Google staff sign-in; returns to the requested page or Features. |
| U02 · Access denied | `/access-denied` | Explains missing permission; Sign out to change account. |
| U03 · Features | `/features` | Feature catalogue and Platform configurations link. |
| U04 · Feature detail | `/features/[id]` | Linked behaviours and Admin link; back to Features. |
| U05 · Tools | `/tools` | Reusable tool library and New tool. |
| U06 · Tool editor | `/tools/[id]` | Metadata, definition and history; back to Tools or originating behaviour. |
| U07 · Explore Shopify | `/explore` | Documentation and query builder; return to originating tool when applicable. |
| U08 · Platform configurations | `/capabilities` | Core/recovery configurations; back to Features. |
| U09 · Behaviour editor | `/capabilities/[id]` | Instructions and exact tool bindings; back to feature or platform list. |
| U10 · Releases | `/releases` | History and release composer. |
| U11 · Release detail | `/releases/[id]` | Exact versions, response contract, activation and rollback; back to Releases. |
| U12 · Merchants | `/shops` | Merchant search. |
| U13 · Merchant detail | `/shops/[id]` | Eligibility and new-conversation tool list; back to Merchants. |
| U14 · Test conversations | `/preview` | Tool tests and synthetic conversations; back to source or Features. |

### Reference for maintaining this guide

This guide follows the [approved page and navigation specification](../architecture/ARCH-020-studio-ui-design.md)
and [implementation contracts](../architecture/ARCH-020-implementation-contracts.md),
including C20's integration ownership. Recheck labels and connected workflows
against the accepted implementation before marking this guide as a released edition.
