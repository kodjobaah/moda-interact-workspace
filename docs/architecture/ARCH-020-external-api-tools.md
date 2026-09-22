# ARCH-020: Read-only external API tools (C21)

Status: approved scope for task definition; implementation not started.
The user selected **read-only tools first**. This extends C14/C20 without replacing
Shopify execution, MCP tool discovery/call envelopes or the conversation grant.
New tasks are DATABASE-003, SHARED-002, COMMERCE-020–032, GATEWAY-003 and
SYSTEM-TEST-002. DATABASE-002 remains retired; do not reuse its identifier.

## 1. Product scope and invariants

A feature remains an Admin-owned global catalogue record with current plan and
merchant eligibility. Its Studio behaviour can bind Shopify, policy or external
HTTP tools using the same exact tool-revision associations. No new feature type,
merchant override or pricing mechanism is introduced here.

Support administrator-approved, read-only **HTTPS GET** operations returning JSON or UTF-8 text (including HTML, XML and CSV):
public catalogue facts, availability descriptions, documentation and similar
non-customer-specific information. This is not a customer account lookup API.
An administrator must confirm the selected endpoint is read-only: GET alone does
not prove an upstream endpoint has no side effects. No POST/PUT/PATCH/DELETE,
request body, binary downloads, cookies, customer identity forwarding,
OAuth/browser authorization or automatic pagination in v1. Authored JavaScript
is permitted only for isolated response processing under section2.2. Bearer
and API-key header authentication are supported. A later action executor requires
separate confirmation/idempotency design; do not quietly permit writes here.

Connections may use one platform credential or a credential for each shop. Only
trusted server turn identity selects the shop. Merchant-specific credentials never
fall back to platform credentials or another shop. Platform connections must be
approved for shared access to the configured data; they cannot represent a single
merchant's private account. API calls remain in Commerce; Background receives the
same descriptor/result envelopes and has no endpoint or credential configuration.

No deployed extension is claimed. Existing in-progress/accepted task scopes stay
unchanged. Integration024 adds the extension after C20's base wiring is accepted.

## 2. Frozen definition and result contract (SHARED-002)

Add this strict member to CommerceExecutionSchema, retaining both current members:

```ts
type ExternalHttpExecution = {
  kind: 'EXTERNAL_HTTP';
  executorVersion: '1.0.0';
  connectionRevisionId: string; // existing IdSchema
  method: 'GET';
  path: string;                // fixed absolute path on approved origin
  query: Record<string, {input: string; omitIfMissing?: true} | {literal: string | number | boolean}>;
  responseFormat: {mode:'JSON'|'TEXT'; mediaTypes:string[]};
  resultPath: string;          // visual JSON selection; empty required for JAVASCRIPT
  responseProcessing: ResponseProcessing; // visual rules OR versioned JavaScript
  resultSchema: SubsetSchema;  // existing DetailsSchemaSchema, closed object root
};
```

No optional additional fields. path <=1024 ASCII characters, begins with exactly
one slash; segment characters are [A-Za-z0-9._~-], separated by slash. Reject dot
segments, percent escapes, backslash, braces, query/hash, empty internal segments
and authority forms. `/` is allowed; a trailing slash is allowed. No templated
path variables in v1. Query has <=32 safeName keys, each <=128 chars; scalar strings
<=2048 UTF-8 bytes, finite numbers and booleans only. Agent mappings reference only
top-level declared scalar inputs; optional absent values omit only when
omitIfMissing=true, otherwise fail INVALID_INPUT. Encode query with URLSearchParams;
stringify booleans/numbers without locale formatting. Sort keys lexically; do not
serialize arrays/objects or allow raw query concatenation. Final URL <=8192 bytes.
Retain existing authority-input exclusions and add credential/header names to
query-key/mapping restrictions: authorization, cookie, set-cookie, host, x-api-key,
api_key, apikey, access_token, token, secret, password (case insensitive).

Tool definition keeps the same six top-level fields and 65,536-byte storage bound.
Extend all execution-kind branches explicitly, including definition validation,
mapToolArguments, publication compiler and hashing; no implicit POLICY_OPERATION
fallback. Export ExternalHttpExecutionSchema/type, ExternalHttpResultDataSchema/type
and the provider-neutral connection schemas/DTO types in section4 from /commerce.
Do not expose crypto, DNS or HTTP implementation in Shared. One published package
version, consumed exactly by extension tasks; update README and complete export
inventory. Existing manifest/grant/response versions stay commerce.v1/response.v1.
The new execution schema lives server-side; Background need not understand it.

Visual mode requires JSON: select the object or array at resultPath using own
properties, then apply section2.1. Code mode uses the complete section2.2 response
input and requires empty resultPath. Both modes validate the processed output
without coercion against resultSchema, rejecting undeclared fields. Unselected upstream fields never
reach the model, result logs or rendered templates.
No inference of production schema from a single sample. Wrap a successful result:

```json
{
  "contractVersion": "commerce.v1",
  "status": "OK",
  "data": {
    "source": "EXTERNAL_HTTP",
    "connectionRevisionId": "opaque-revision-id",
    "observedAt": "2026-09-21T12:00:00.000Z",
    "values": {"title": "Illustrative external item"}
  },
  "renderedText": "Illustrative external item"
}
```

Templates use `{{result.values.title}}` or list `itemsPath: "values.items"`;
publication derives that wrapper's schema from resultSchema. Preserve existing
ResponseTemplateSchema rules. External lists use maxSearchResults, capped at20;
validate the whole bounded response before rendering the bounded list. External
output is untrusted factual data, never prompt instructions, discount evidence,
contact handoff authorization or authority to call another URL. No evidenceIds
are synthesized. Existing discount evidence checks are unchanged.

Example execution (connection revision is illustrative, not a seed):

```json
{
  "kind": "EXTERNAL_HTTP", "executorVersion": "1.0.0",
  "connectionRevisionId": "connection_revision_example", "method": "GET",
  "path": "/catalogue/item", "query": {"sku": {"input": "sku"}},
  "responseFormat": {"mode":"JSON","mediaTypes":["application/json"]},
  "resultPath": "data",
  "responseProcessing": {"kind":"OBJECT", "fields":{"title":{"path":"title"}}},
  "resultSchema": {
    "type": "object", "properties": {"title": {"type": "string", "maxLength": 200}},
    "required": ["title"], "additionalProperties": false
  }
}
```

## 2.1. Response processing (COMMERCE-025; Shared owns schemas)

The user requested BOTH visual filtering and generic code. This section defines
the visual branch and editable JSON configuration of those same operations.
Section2.2 defines the separate JAVASCRIPT branch. Visual rules are not converted
into arbitrary code, and arbitrary code is never silently converted into visual rules.

```ts
type FieldProjection = Record<string, {path:string; omitIfMissing?:true}>;
type Scalar = string | number | boolean | null;
type ResponseFilter =
  | {path:string; op:'EQ'|'NE'|'GT'|'GTE'|'LT'|'LTE'|'CONTAINS'|'STARTS_WITH'; value:Scalar}
  | {path:string; op:'IN'; values:Scalar[]};
type VisualResponseProcessing =
  | {kind:'OBJECT'; fields:FieldProjection}
  | {kind:'LIST'; fields:FieldProjection; filters:ResponseFilter[];
     sort:null|{path:string;direction:'ASC'|'DESC'}; limit:number};
type ResponseProcessing = VisualResponseProcessing
  | {kind:'JAVASCRIPT';runtimeVersion:'quickjs-sync.v1';source:string};
```

All objects strict; field names use safeName, source paths safePath, maximum32
projected fields (at least1),8 filters ANDed in listed order, IN1..20 values,
strings<=2048 UTF-8 bytes, finite numbers, LIST limit integer1..20. Reject prototype
keys in paths and fields. OBJECT takes an object and returns the selected/renamed
scalar fields. LIST takes an array of at most1000 objects and returns
`{items:[projected objects]}`. A larger input fails, never silently truncates before
filtering. Missing source field fails unless omitIfMissing=true; null is a value,
not missing. Selected arrays/objects are unsupported projection values in v1;
choose nested scalar paths. Never copy original source objects into results.

Pipeline: select resultPath -> validate input bounds -> filter -> stable sort ->
limit to min(configured limit, call.limits.maxSearchResults) -> project -> validate
resultSchema -> existing response template. No stage calls another API. Missing or
non-scalar filter fields do not match, including NE. EQ/NE require identical scalar
types, no coercion; GT/GTE/LT/LTE require finite numbers; CONTAINS/STARTS_WITH require
strings and are case-sensitive; IN uses strict same-type equality. Sort supports
strings (Unicode code-point lexicographic) or finite numbers, consistent non-null
type across rows; missing/null last in either direction, ties preserve original
index. Mixed types or invalid input fails processing rather than coercing it.
Unsorted uses original order. Empty results produce {items:[]} and the existing
empty template. resultSchema must describe actual projected output (OBJECT fields
or LIST items object); publication rejects incompatible required names/types.

Export server-only `createResponseProcessor({now})` under
`src/commerce/external-response/`; `.process({source,processing,limits,signal})`
returns `{ok:true,values}` or `{ok:false,code:'INVALID_RESPONSE'|'DEADLINE'|'CANCELLED'}`.
limits={maxSearchResults:number,deadlineAt:number}. Check abort/deadline before
processing and at least every32 rows.021 injects this port;025 implements it with
no network, persistence or UI. Shared exports ResponseProcessingSchema,
ResponseProcessing, VisualResponseProcessing, ResponseFilterSchema,
FieldProjectionSchema, VisualResponseProcessorInput and VisualResponseProcessorResult; no executable transforms in Shared.025 accepts only
VisualResponseProcessing;026 accepts only JAVASCRIPT.024 selects the correct port. Existing 256KiB/depth20
HTTP bounds still apply to the raw body. Stored configuration counts against the
same65536-byte complete tool-definition limit and immutable content hash.

Worked example: resultPath `data.products`, LIST filters
`[{path:"available",op:"EQ",value:true}]`, sort `{path:"price",direction:"ASC"}`,
limit3, fields `{name:{path:"title"},price:{path:"price"}}` returns at most three
available rows with only name and price. No discount eligibility or currency
conversion is inferred from this operation. Tests cover wrong types, missing/null,
empty arrays, duplicate sort values, Unicode, bounds, prototype keys, cancellation
and two simultaneous calls with different data. No shared mutable processing state.

## 2.2. Raw response decoding and authored JavaScript (COMMERCE-026)

responseFormat is explicit, not guessed from endpoint or sample. mediaTypes is an
array of1..8 unique lowercase exact MIME values, max128 chars each, no parameters or
wildcards. JSON mode permits application/json and application/*+json concrete types;
TEXT mode permits text/* concrete types, application/xml, application/*+xml and the
JSON types. Match response Content-Type without parameters case-insensitively;
missing/unapproved MIME fails. Only UTF-8/US-ASCII charsets supported initially;
reject other declared encodings, invalid UTF-8 and NUL. No executable HTML rendering,
PDF/image/binary processing, network parsing or automatic source URL traversal.
HTML/XML/CSV are passed as text; they are not assumed to be JSON or a DOM.

After021's bounded download/decompression, decode into this data-only input:

```ts
type TransformResponse = {
  status: number;             // successful 2xx only
  contentType: string;        // normalized MIME, no other headers
  bodyText: string;           // <=256KiB UTF-8
  json: Json | null;          // parsed only in JSON mode; null in TEXT mode
};
```

User source <=16384 UTF-8 bytes declares a synchronous `function transform(response)`
and returns a JSON-compatible object. Source is part of the immutable tool revision
and content hash, with runtimeVersion quickjs-sync.v1. No fetch, process, require,
import/module loader, filesystem, credentials, request arguments, environment,
timers or host callbacks are exposed. Standard JavaScript strings, arrays, regex,
JSON and arithmetic are available; no DOM or third-party import in v1. Users can
write their own parsers for text formats; Studio must explain these available APIs
instead of pretending browser APIs/libraries exist. Runtime upgrades require a new
version and explicit republishing; no silent reinterpretation of published code.

```js
function transform(response) {
  // Example provider body: "Stock: available\nDelivery: 2 days"
  const facts = Object.fromEntries(response.bodyText.split(/\r?\n/)
    .filter(line => line.includes(":"))
    .map(line => {
      const split = line.indexOf(":");
      return [line.slice(0, split).trim(), line.slice(split + 1).trim()];
    }));
  return { availability: facts.Stock ?? "unknown", delivery: facts.Delivery ?? "unknown" };
}
```

Examples are synthetic transformations, not proof of live facts. Result must satisfy
resultSchema before values enter the existing template/model flow. Reject primitive,
array-root, undefined, functions, symbol, BigInt, nonfinite values, cycles, accessors,
custom prototypes/toJSON, prototype-pollution keys, >20 depth or >48KiB serialized
output. Do not stringify away invalid values or silently truncate. Arrays nested in
output max20 elements and max call.limits.maxSearchResults; exceeding fails, code
must explicitly select results. JSON serialization/validation stays under execution
limits; hostile getters/proxies cannot hang the host or execute host functions.

Implementation uses the synchronous QuickJS WebAssembly engine via
quickjs-emscripten, in a dedicated Node Worker per invocation. Create a fresh WASM
module/runtime/context for each invocation and terminate/dispose it afterward; no
shared guest globals or cached mutable contexts. Never use node:vm, host eval or
Function as the isolation boundary. Pin dependency and WASM artifact hashes in the
implementation lockfile/evidence. Sandbox setup has its own wall budget but remains
inside the existing turn deadline. User source is never evaluated on Next's request
thread or the operator's browser.

Concrete limits: source16KiB, raw body256KiB, output48KiB; QuickJS heap16MiB,
stack512KiB, finite WASM linear-memory maximum64MiB.029 must verify/build the pinned
sync WASM variant with an enforced maximum (a QuickJS allocator limit alone is not
proof of an overall WASM bound). Worker V8 old-space64MiB/young-space16MiB; these
limits do not substitute for the WASM limit. Disable guest Date and Math.random so
sample/live transformations cannot depend on clock/randomness; pass no host objects.
Use interrupt checks for500ms guest execution including result extraction; supervisor
hard termination at min(2000ms since dispatch, remaining turn deadline), including
startup. Abort terminates worker promptly. Maximum4 active transform workers per
Commerce process, no queue: capacity exhaustion returns THROTTLED. Semaphore released
in finally for success/error/timeout/startup failure/abort. Document replica capacity;
never spawn unlimited workers or share a context to improve throughput.

Export server-only createCodeResponseProcessor from
`src/commerce/code-response/processor.ts`;029 owns the runtime subdirectory. `.process({response,processing,limits,signal})`
where processing is JAVASCRIPT variant and limits={maxSearchResults,deadlineAt}.
Return {ok:true,values} or {ok:false,code:'INVALID_RESPONSE'|'DEADLINE'|'CANCELLED'|
'THROTTLED',diagnostic?:{code:string,line:number|null,column:number|null}}.
Shared additionally exports CodeResponseProcessorInput, CodeResponseProcessorResult,
TransformResponseSchema/type and ExternalResponseFormatSchema/type with the exact
shapes above. Diagnostic code is closed: SYNTAX_ERROR, EXECUTION_ERROR, INVALID_OUTPUT,
RESOURCE_LIMIT, RUNTIME_UNAVAILABLE. Never expose exception messages containing body
content, stack/paths, source, credentials or console logs. Preview can show bounded
code/line/column; production maps INVALID_RESPONSE to UNAVAILABLE false, THROTTLED
true, deadline/cancel to existing corresponding errors. Sandbox unavailable fails
closed; visual tools remain usable. No automatic code fix or raw-text fallback.

Syntax validation compiles in the same sandbox, does not execute arbitrary top-level
source outside it. Publication requires syntax pass, explicit supported runtime and
sample output-schema validation; sample success is not correctness proof for all
responses. Runtime always revalidates. Published code edits require new tool revision,
behaviour/release publication; old grants retain original source and runtime version.
No new database table for source: it is stored in existing tool definition JSON.

Preview uses this SAME server-side engine on synthetic response samples, including
TEXT mode and Model preview. Zero provider fetches/decryptions in preview; source is
never run by the editor. Authenticated validation/sample execution require ADMIN,
Origin check, per-admin maximum1 concurrent run plus process cap4; a5-second per-admin
cooldown between starts is enforced across replicas using existing Redis SET NX PX.
Key derived from authenticated admin ID/environment; failure to check limiter fails
unavailable. Script execution result is not cached or used as another script's input.
029 provides the proven runtime kernel,026 the typed processor adapter;031 owns
authorized Redis-limited sample services.024 only binds accepted services to UI.

Engine references for implementation: [QuickJS runtime API](https://github.com/justjake/quickjs-emscripten/blob/main/doc/quickjs-emscripten/classes/QuickJSRuntime.md)
provides memory/stack/interrupt controls. [Node VM documentation](https://nodejs.org/api/vm.html)
explicitly excludes node:vm as a security mechanism. These APIs inform the design;
acceptance still requires real resource-exhaustion and isolation tests.

## 2.3. Output validation and sample interfaces

One output path for both modes: decode -> process -> validate the returned object
against resultSchema -> wrap as data.values -> render -> existing CommerceToolResult
validation -> agent. Validation is fail-closed, without coercion, default values,
stripping unknown keys or fallback to raw body. Cap all processed values at48KiB
UTF-8, depth20 and schema subset limits. Existing whole-result bounds also apply.
Output schema is explicitly authored, never inferred as authoritative from a sample.
Visual publication checks that projection output names/array shape match the schema;
code publication checks syntax/runtime and the tested output. Neither is proof of
factual accuracy. Every real result is checked again. New error paths map to existing
MCP errors, not a new Background protocol.

Shared exports `TransformSampleSchema`/type = {status:integer200..299,
contentType:string1..128,bodyText:string<=256KiB UTF-8}; unsafe content is data only.
The response mode comes from the saved tool definition, never inferred. Header charset
may be included in contentType for decoding; compare normalized MIME separately.
Sample total serialized request <=512KiB; reject oversize request explicitly.

Component ports (server resolves principal; browser cannot submit identity):
- validateCode({source,runtimeVersion,contentHash}) -> {kind:'ok',contentHash} or
  {kind:'invalid',contentHash,issues:[{path,message,line,column}]} or unavailable.
  contentHash=SHA256 canonical {source,runtimeVersion}; server recomputes/compares.
  Uses026 compiler and same quotas. No source execution for syntactic validation;
  any engine setup/evaluation stays inside limits. At most32 bounded issues; no raw
  provider content in message.
- Tool/sample execution reuses009 previewRunId, toolRevisionId, fixtureId, arguments,
  status/read/cancel/replay.031 extends ToolTestBodySchema with optional
  externalResponseFixture:TransformSample (only accepted for EXTERNAL_HTTP).
  U06 **Run sample** first saves current draft and uses its returned revision/editVersion;
  failed or unknown save prevents dispatch. Tests hash the complete frozen definition
  plus sample, arguments and runtime. Changed content invalidates old displayed success.
- ConversationBodySchema may additionally carry
  externalResponseFixtures:Record<toolRevisionId,TransformSample>, max32 entries,
  total sample UTF-8 body bytes256KiB.031 validates ownership against frozen selected
  tools; reject unknown IDs/non-external tools. Freeze in existing preview Redis state,
  preserve24h retention/admin/environment isolation and unchanged empty-map behavior.
  Each external fixture is static per tool for that synthetic conversation; reset to
  change it. Keep successful processed preview data <=48KiB and trace<=8KiB so the
  existing64KiB preview envelope remains valid. Do not enlarge other public limits.

These are additive **Studio preview** contract changes, not MCP tools/call changes.
031 owns matching server/store schema changes,030 owns receipts and027/023 clients; existing009/017
work is not reopened. Accept old preview requests unchanged. No new arbitrary source
payload on production MCP calls or guest access to credentials/real provider.

A successful saved-revision sample run records a24h Redis publication receipt keyed
by environment + toolRevisionId + canonical complete definition hash + runtimeVersion
(use `visual.v1` for visual rules). Contains testedByAdminId, sampledAt, sampleHash,
validatedOutputHash only, no source/sample body/output. Written only by authorized
sample service AFTER schema/render validation. SUPER_ADMIN publication recomputes
hash and requires a matching unexpired receipt plus fresh compiler/schema/connection
checks. Display missing/expired/stale receipt as **Run a sample test before publishing**.
Receipt may originate from another active staff author's successful test; test details
remain isolated to that author's preview. Deactivated tester receipt is invalid.
Redis outage fails publication unavailable, never bypasses validation. This is bounded
evidence of a sample, not a production approval or proof about future provider data.

Cases X13: required field missing; wrong number/string; extra field; null versus
missing; nested/array mismatch; invalid/nonfinite/cyclic/code output; output limit;
unsafe/malformed input; changed source after success; expired test receipt; current
code passes sample but different production response fails. Error display uses JSON
Pointer + expected type/rule and no raw rejected value. Production returns bounded
unavailable/referral handling, no fabricated values or partial result. Owned by
SHARED-002 schema tests,030 validation,031 preview,024 assembly and SYSTEM-TEST-002
real-call evidence. Section9 defines the narrowed acceptance evidence.

## 3. Database contract (DATABASE-003)

Create these models in existing `commerce` schema. All IDs are String/text @id
@default(cuid()); timestamps DateTime/timestamptz(3), createdAt default now and
updatedAt @updatedAt where present. No live seed, destructive rewrite, copied
Prisma schema or changes to capability/tool/grant tables. Normalized origins and
connection cross-row checks belong to020; credential scope checks belong to028,
not claimed as SQL checks.

| Model | Required fields and defaults | Relations, indexes and constraints |
|---|---|---|
| CommerceExternalConnection | key String/varchar128 unique; displayName String/varchar255; description String/text default empty; enabled Boolean default true; editVersion Int default1; createdAt, updatedAt | CHECK editVersion>0, key regex `^[a-z][a-z0-9_]{0,127}$`; nonblank displayName, description <=4096 chars. No deletion API. |
| CommerceExternalConnectionRevision | connectionId String/text; revisionNumber Int; origin String/varchar2048; scope enum PLATFORM/PER_SHOP; authMode enum NONE/BEARER/API_KEY; authHeader String?/varchar128; documentation String/text default empty; createdByAdminId String/text; createdAt | Connection and PlatformAdmin FKs RESTRICT; unique(connectionId,revisionNumber), unique(id,connectionId); CHECK revisionNumber>0; authHeader null unless API_KEY, required nonblank for API_KEY; documentation <=16000 chars; immutable after creation by SQL UPDATE/DELETE rejection trigger. |
| CommerceExternalCredential | connectionRevisionId String/text; shopId String?/text; ciphertext Bytes/bytea; nonce Bytes/bytea; authTag Bytes/bytea; keyId String/varchar64; editVersion Int default1; updatedByAdminId String/text; createdAt, updatedAt | Revision, Shop, PlatformAdmin FKs RESTRICT. Partial unique index on revision WHERE shopId IS NULL, and unique(revision,shopId) WHERE shopId IS NOT NULL. CHECK nonce length12, tag length16, ciphertext length1..8192, nonblank keyId, editVersion>0. Null shop represents PLATFORM only;028 enforces scope and NONE prohibition transactionally. |
| CommerceExternalConnectionAudit | actorAdminId String/text; operationId String/varchar128; action enum CREATE_CONNECTION/UPDATE_METADATA/CREATE_REVISION/SET_ENABLED/SET_CREDENTIAL/REMOVE_CREDENTIAL; requestDigest String/char64; connectionId String/text; connectionRevisionId String?/text; shopId String?/text; reason String/varchar1000; result Json/jsonb; createdAt | FK actor/connection/revision/shop RESTRICT; unique(actorAdminId,operationId); index(connectionId,createdAt,id); digest lowercase64hex; reason trimmed nonblank; result object <=16384 bytes; immutable UPDATE/DELETE trigger. No secret/ciphertext/raw request in result. |

All immutable triggers allow normal inserts only; isolated-test cleanup uses a fresh
schema/database, not disabling protections in production. Exact Prisma enum names:
CommerceExternalConnectionScope, CommerceExternalAuthMode,
CommerceExternalConnectionAction. Add backrelations to Shop/PlatformAdmin.
Database acceptance proves both partial unique indexes, foreign keys, rollback and
immutability through real PostgreSQL; document disposable migration rehearsal.

## 4. Connection service contract (020 lifecycle;028 credentials)

Section9 splits this contract between020 lifecycle/command kernel and028 credential
service.024 composes their facade without adding behavior. No React, MCP or global
request principal in producers.021 remains independent against the agreed resolver
port; it does not require028 implementation to begin.

Export `ConnectionRevisionView` containing id, connectionId, revisionNumber, origin,
scope, authMode, authHeader, documentation, createdAt. `ConnectionView` contains id,
key, displayName, description, enabled, editVersion, revisions sorted descending.
`CredentialStatus` contains connectionRevisionId, shopId, configured, editVersion
(null when absent), updatedAt (null when absent). Never return secret bytes,
ciphertext, nonce, authTag, masked secret suffix or authentication header value.
Shared DTOs use ISO timestamps and the existing IdSchema, strict objects throughout.

`ConnectionCommand` is {operationId,reason}; operationId existing IdSchema, reason
1..1000 trimmed characters. New create/update requests use the table bounds.
`RevisionInput` = {origin,scope,authMode,authHeader,documentation}. Normalize origin
with URL parser to https://lowercase-host[:443]; store without trailing slash,
explicit443 or path; reject userinfo, any non443 port, IP literals, query/fragment,
nonroot paths and single-label/local hostnames. API_KEY authHeader must match HTTP
token grammar and cannot be Host, Cookie, Set-Cookie, Content-Length, Transfer-Encoding,
Connection, Proxy-Authorization, Accept, Authorization or any Sec-/Proxy- prefix.
BEARER always uses Authorization. Secret value1..8192 bytes, no CR/LF/NUL.

Service methods (principal supplied separately from trusted server auth):

- list({search,cursor,limit}): search name/key; stable displayName,id cursor; limit25
  default,1..100; return {items:ConnectionView[],nextCursor:string|null}.
- get({connectionId}): ConnectionView; getCredentialStatus({connectionRevisionId,shopId}).
- create({...ConnectionCommand,key,displayName,description,revision:RevisionInput})
  -> {connectionId,connectionRevisionId,editVersion:1} atomically creates initial revision.
- updateMetadata({...ConnectionCommand,connectionId,expectedEditVersion,displayName,description})
  -> {connectionId,editVersion}; key immutable.
- createRevision({...ConnectionCommand,connectionId,expectedEditVersion,revision:RevisionInput})
  -> {connectionId,connectionRevisionId,revisionNumber,editVersion}; next number allocated
  under connection-row lock. Does not copy credentials or change published tools.
- setEnabled({...ConnectionCommand,connectionId,expectedEditVersion,enabled})
  -> {connectionId,editVersion}; explicit desired value, never toggle.
- setCredential({...ConnectionCommand,connectionRevisionId,shopId,expectedEditVersion,
  secret}) -> CredentialStatus. expectedEditVersion=null means create only.
- removeCredential({...ConnectionCommand,connectionRevisionId,shopId,expectedEditVersion})
  -> CredentialStatus; integer expected version required, return absent status.

ADMIN reads metadata/status. Only SUPER_ADMIN mutates connection metadata,
revisions, secrets or enabled state. Active staff authorization is repeated per
request, Origin checked for browser mutations. Credential merchant selector uses
authorized shop-ID/domain lookup, never a free-form secret-bearing URL.
All results use {kind:'ok',value:T}, not-found, forbidden, unavailable,
{kind:'invalid',issues:[{path,message}]}, or conflict with STALE_CAS/CONFLICTING_REPLAY;
uncertain server-action response -> {kind:'unknown',operationId} in UI transport.
Messages bounded512 chars, issues max32. DTO names: ConnectionRevisionView,
ConnectionView, CredentialStatus, ConnectionCommand, RevisionInput,
ConnectionResult<T>; Shared owns these names and schemas.

Use READ COMMITTED transactions with locked connection/credential rows; unique
constraints arbitrate first insert. Authorize BEFORE audit replay. Replay key is
(actorAdminId,operationId); digest HMAC-SHA256 over canonical {action,input}, using
COMMERCE_CONNECTION_COMMAND_HMAC_KEY. Same digest returns stored nonsecret result
without repeated effect; changed input conflicts. Audit and business write commit
in one transaction; stale/invalid/denied writes create no success audit. On unique
conflict reread committed audit to return winner, not a second command. Secret
material enters only in-memory command digest/encryption, never stored audit JSON.

Encrypt secrets with AES-256-GCM; random12-byte nonce,16-byte authTag; authenticate
canonical {connectionRevisionId,shopId,keyId} as AAD. Keyring injected from validated
environment; no app default. Only active encryption key used for new writes;
retain old keys for decryption until credentials are deliberately re-encrypted.
Credential rotation uses setCredential CAS and affects future calls, including
existing grants; endpoint/scope/auth changes require a NEW immutable revision.
Connection disable blocks calls in old and new grants. Decrypt failure -> unavailable.

Provide server-only `resolveConnection({connectionRevisionId,shopId,signal})` for021:
return {kind:'ok',value:{revision:ConnectionRevisionView,authentication:null|{headerName,headerValue}}}
or not-found/forbidden/unavailable. This sensitive return type is local to Commerce,
not Shared/browser DTO. Verify enabled, immutable revision and exact scope/credential
on every call; Reject PER_SHOP+NONE at revision creation; every PER_SHOP connection requires an
exact-shop credential, so tenant authorization is never ambiguous.
PLATFORM+NONE uses null authentication. Missing PER_SHOP credential -> forbidden.
No live connection-check HTTP action in020/028;021 owns all outbound network execution.

## 5. HTTP execution (COMMERCE-021)

Own `src/commerce/external-http/**` (025 owns separate external-response), add explicit dispatch in014 executor/renderer
only;030 owns publication validation. Export `createExternalHttpExecutionPort`
with injected resolveConnection, responseProcessor, transport, DNS resolver and clock. Its execute
input is {context:AuthorizedToolCall,execution:ExternalHttpExecution,
query:Record<string,string|number|boolean>}; return existing CommerceToolResult.
No dependency on028/025/026 implementation; use section4 and2.1/2.2 port fixtures. Reuse the existing
shared call budget/deadline/AbortSignal, never reset it for a provider operation.

Before dispatch check current grant/turn via existing authorization and resolve
exact pinned connection revision from server shopId. Resolve all DNS addresses,
reject if any is not globally routable (IPv4/IPv6, mapped IPv4, localhost, private,
link-local, multicast, unspecified and reserved included). Pin an approved resolved
IP to the actual socket while retaining original TLS SNI/Host and certificate
validation. Recheck on each new socket; never validate one resolution and let fetch
perform an unchecked second resolution. No redirects, proxy environment fallback,
IP-literal escape, custom port, cookie jar, upstream URL discovery or request headers
from the model. Transport tests must assert the actual connected address. Use a
maintained address classifier, with official special-address fixtures, not a few
string prefixes. Only static administrator-selected path + encoded query are sent.
Headers: Accept application/json plus configured auth; no incoming request headers.

Bound DNS/connect/body by min(5 seconds, remaining turn deadline); cancel closes
request. Max decoded response256KiB including decompression, JSON nesting<=20 when parsed,
request URL8192 bytes, successful whole result <=256KiB after wrapper/rendering.
No automatic transport retries; each invocation consumes one remote budget unit
and at most one HTTP request. Shared runner's existing bounded retry can re-invoke
only retryable unavailable/throttled results. No endpoint polling/pagination.
Decode declared responseFormat under section2.2. Reject MIME/charset mismatch,
invalid JSON in JSON mode, unsafe keys or missing visual resultPath. TEXT mode
passes bodyText to code without attempting JSON parsing. Pass selected visual
source or TransformResponse to the injected processing dispatcher; INVALID_RESPONSE maps to
UNAVAILABLE false. At the published `CommerceToolResult` boundary, both processor
deadline and processor cancellation map to nonretryable DEADLINE because accepted
Shared 0.14.2 does not expose CANCELLED in `CommerceErrorCodeSchema`; runner-level
turn cancellation remains CANCELLED. No raw fallback.

Error mapping: missing/disabled/foreign credential -> DENIED nonretryable; invalid
arguments -> INVALID_INPUT false; remote401/403/404, redirect, bad JSON/schema/body
bound/DNS target -> UNAVAILABLE false;429 -> THROTTLED true;5xx/connection failure ->
UNAVAILABLE true; deadline -> DEADLINE false; abort/cancel -> DEADLINE false at the
`CommerceToolResult` boundary. Runner-level `RunCommerceTurnResult` cancellation
remains CANCELLED; COMMERCE-021 must not locally widen the accepted Shared 0.14.2
result union. No raw provider body, credentials or URL query in returned errors/logs. Bound numeric status and
connection revision ID may appear in diagnostic fields with shared logging.
Do not turn a missing field into a made-up success. Templates retain unavailable text.

Publication verifies known enabled revision/auth shape/result schema/template paths
without live HTTP. PER_SHOP credentials need not exist for every shop at publish:
merchant inspection lists missing credentials as an explicit exclusion. Both
pre-call authorization and U13 selection use current connection availability;
existing grants cannot gain revisions after credentials/configuration change.
No caching for EXTERNAL_HTTP in012: bypass lookup, counters, locks and storage.
Shared platform credentials are not evidence that results can be shared across shops.

## 6. Studio pages and traversal

This adds U15/U16 and the **Connections** sidebar item AFTER Explore Shopify and
BEFORE Test conversations; the other order remains unchanged. Use existing visual
components, auth, loading/empty/not-found/forbidden/unavailable states and navigation
memory rules. Every mutation/test has immediate duplicate-click protection,
pending state, retained operation identity and known-error input retention.
No credentials in URLs, localStorage, sessionStorage, analytics or browser logs.
Secrets are cleared after confirmed success/sign-out; an unknown credential command
retains the SAME in-memory payload/operation until reconciliation or deliberate
page exit (explain that outcome must be checked before resubmission).

### COMMERCE-022: U15/U16 connections frontend

Own `src/studio/connections/**`, `app/connections/page.tsx`,
`app/connections/[id]/page.tsx` and the single sidebar addition. Component acceptance
uses section4 typed ports; no backend/crypto implementation and no changes to U06.

U15 `/connections`: search name/key, enabled filter, name/id pagination, columns
Name/Scope of latest revision/Auth/Enabled/Latest revision; Open ->U16. SUPER_ADMIN
**New connection** dialog: immutable key, display name, description, origin, scope,
auth mode, API-key header conditionally, inline documentation. Checkbox **I confirm
this connection will only be used for read-only operations** required to submit;
UI gate not a claim of automatic upstream verification. Create ->U16 initial revision.
ADMIN sees explanation in place of create/modify actions.

U16 `/connections/[id]`: tabs **Overview**, **Revisions**, **Credentials**.
Overview shows metadata, enabled state, referencing tool versions (read-only), Edit
metadata and explicit Enable/Disable with reason/impact on existing grants.
Revisions shows exact immutable fields and documentation; **New revision** copies
visible fields into dialog but not secrets; save creates revision and explains that
existing tools still reference old revision. Selecting revision updates Credentials
context; never switch silently to latest. Back ->U15 retains search/cursor.
Credentials shows PLATFORM single status or PER_SHOP shop search/status list;
**Set credential / Replace credential / Remove credential** SUPER_ADMIN dialogs
with reason and CAS, no reveal. NONE mode shows **No authentication required**.
Missing environment key shows unavailable, never pretends save succeeded.

### COMMERCE-023: U06/U14 external tool authoring frontend

Own `src/studio/external-http/**`, U06 external editor section and U14 fixture
controls. No connections routes/sidebar/backend implementation. Use section4
read-only connection ports; can develop alongside020/021/022.

U06 **Retrieve information** adds **External API (read-only)** beside existing
choices. Select connection -> exact revision -> display scope/auth/inline connection
documentation -> enter fixed path -> map query fields. No mandatory visit to an
external documentation site. **Manage connections** opens U16 with validated
return tool/revision context, after save/discard guard; return restores source.
Response format selects JSON or Text and accepted media types; show UTF-8 and
textual-format support. Text requires Code mode; visual controls explain JSON-only
input without silently parsing HTML/XML/CSV. No OpenAPI importer or remote documentation fetch is required: administrators
supply documented endpoint instructions in U16.

Add **Process response** between retrieval/mapping and the existing Response step:
**Visual rules / JavaScript** mode selector;023 owns the visual panel and a typed
slot for027 code panel. Switching a dirty mode requires Keep editing/Discard, never
silent conversion. Saved definition contains only the selected mode. Object/List selector; source path; Add/Remove filter with field/operator/typed value;
AND explanation; optional Sort and direction; Limit; output name/source field rows.
An **Advanced configuration** JSON view edits the same ResponseProcessing schema;
no separate visual syntax. The distinct JavaScript tab is specified below. Show original synthetic JSON and
processed JSON side by side with matching input/output row counts. **Apply to
sample** calls a supplied pure processor port (fixtures for component acceptance);
no server credentials or network. Schema/path errors retain input and highlight
the affected row. Any processing change invalidates previous test/validation.

Add **Response shape** editor for the supported closed object schema with inline
keyword reference, editable synthetic JSON and **Validate sample**. resultPath
empty means root; explain templates reference wrapper `values`. Schema-derived
field chips in existing Response step; missing/type-invalid fields identify exact
path. Sample validation is not proof of a live provider response. Review panel
shows connection name/revision, GET path, redacted mapping names, output schema and
unchanged agent descriptor. Never display credential values or put literal sensitive
data into sample defaults. Save/Publish follow existing version/CAS/reason workflow.

U14 **Tool test** offers success/empty/missing-field/provider-failure fixtures for
external tools, with supplied JSON or raw TEXT fixture processed by its selected
mode and the resulting object validated by resultSchema. Conversation
preview uses the same frozen external definition and scripted facts in Fixture AND
Model modes. No live request or decryption in either preview mode. Changing schema,
query, connection revision or sample invalidates prior success; save before leaving
U06; return goes to exact tool revision. Reset required to change frozen conversation.

### COMMERCE-027: JavaScript editor and raw-response samples (U06/U14)

Own `src/studio/code-response/**` only, exporting CodeResponsePanel and
RawResponseSamplePanel. Do not edit023's U06 host routes, visual editor, U14 root or
sidebar;024 installs these panels through the agreed slot. May develop concurrently
with023/025/026 against Shared types and injected compile/run ports.

Code panel has source editor with line numbers and JavaScript highlighting, embedded
`transform(response)` signature, API/limit reference, example selector (JSON mapping,
plain-text key/value extraction, HTML string extraction, XML string extraction,
CSV simple-line extraction; label simple string examples as limited, not full parsers),
Validate code, Run sample, Cancel run and Restore saved draft. No remote CDN/editor
scripts. Use existing code editor dependency if present; otherwise CodeMirror6 with
locally bundled JavaScript mode. Do not execute source via browser eval/Function.

Sample panel includes response status(2xx), content-type, JSON/Text format, raw sample
textarea (literal escaped display, never innerHTML), validated processed JSON and
rendered response beside it. Invalid/malicious HTML stays text. MIME/UTF-8/code/output
failures have separate bounded messages. User code may parse strings but output must
be object matching Response shape schema. No live API button or input of real secrets.

Every source/sample/schema edit invalidates validation by content hash; late results
apply only to same draft/hash. Disable duplicate runs, show cooldown/Running/Cancelled/
Unknown, preserve input on known failure. Cancel waits for backend confirmation; an
unknown call is reconciled via its original preview run identity before resubmission.
Unsaved navigation follows save/discard. Published source read-only; Create draft to
edit. ADMIN authors/tests, SUPER_ADMIN publishes with source diff and reason.
XN04: U06 Text ->JavaScript ->sample->Validate->Save->Run->schema error->fix->Save->Run->
U14 conversation->Back->Publish.024 proves real engine wiring;027 tests typed ports.

Acceptance paths: XN01 U15->New->U16->New revision->Credentials->U15;
XN02 U09->Create tool->U06 external->U16->Return->U06->U14->Return->Publish->U09;
XN03 U09 publish->U10 release->U11 activate->U13 availability->U14 synthetic test.
UI ownership022 proves XN01 with ports;023 proves XN02 owned segments with ports;
024 proves all three against real services. No arbitrary screenshot count.

## 7. Final wiring and deployment

COMMERCE-024 is composition only under `src/commerce/integration/external/**`,
with minimal accepted backend/Studio/preview factories, Server Action delegation,
U13 result presentation and023/027 panel slots.020 lifecycle,028 credentials,
021 HTTP,025/026 processing,030 publication/receipts,031 preview and032 availability
must be accepted before wiring. No new algorithm, persistence, eligibility, quota
or receipt implementation belongs in024. It also waits for base013/018/019 and
022/023/027 UI components. Preserve source hashes, exact pins and existing MCP
contracts. Missing producer behavior is corrected in that producer, not absorbed
into integration. Section9 defines exact exports and ownership.

GATEWAY-003 owns blueprint/config documentation only, after001 and020/021/028/029/026.
New settings: COMMERCE_CONNECTION_KEYS_JSON (secret object: keyId -> base64 exactly
32bytes), COMMERCE_CONNECTION_ACTIVE_KEY_ID (nonsecret matching key),
COMMERCE_CONNECTION_COMMAND_HMAC_KEY (secret base64 exactly32bytes; stable for audit
replay). Inject only into Commerce server runtime, never NEXT_PUBLIC, Background,
Messaging or browser builds. No generated real secrets in Git. Package/bundle the pinned WASM asset and Node
worker entry in Commerce runtime; never download them on requests. Run production
image smoke for fresh worker, memory ceiling, timeout and4-worker cap before enabling
code mode. Keep per-replica memory sufficient for measured worst case, or reduce
replica concurrency through a future explicit contract amendment; do not ignore caps. Missing/invalid
keys disable credential mutations/external calls with unavailable while existing
Shopify paths continue; public health never prints config. HMAC-key rotation needs
an explicit migration of replay strategy; not an automatic env change. Document
keyring rotation and rollback with retained decrypt keys. Keep MCP private per001;
Connections uses authenticated public Studio. Do not deploy/enable a live external
connection as a side effect of this task.

Existing C20 tasks retain readiness.012 waits for new implementation tasks and
explicitly excludes EXTERNAL_HTTP caching. SYSTEM-TEST-002 is a separate manual
extension acceptance gate; SYSTEM-TEST-001 includes its completion for overall
ARCH-020 acceptance. No circular dependency on012 or SYSTEM-TEST-001 in002.

## 8. Acceptance evidence and ownership

| Case | Required evidence | Owner |
|---|---|---|
| X01 | Schema rejects methods/body/URL authority/invalid mapping; accepts example and retains existing two execution kinds | SHARED-002 |
| X02 | PostgreSQL partial uniqueness, immutable revisions/audit, FK and rollback; no plaintext secret columns | DATABASE-003 |
| X03 | Lifecycle concurrency/replay/CAS and staff authorization; encryption/credential isolation | COMMERCE-020 CL01–03; COMMERCE-028 CR01–03 |
| X04 | Actual socket DNS pin, private/mapped IPv6/rebinding/redirect denial, timeout/cancel/decompressed bound and provider-error mapping | COMMERCE-021 |
| X05 | XN01, role-aware controls, no reveal/storage leaks, double-click and unknown-operation recovery | COMMERCE-022 |
| X06 | XN02 owned segments, schema/template chips and stale validation, zero live preview calls | COMMERCE-023 |
| X07 | XN01–03 real service flow, immutable connection revision, per-shop missing-credential exclusion, platform/per-shop isolation, visual/code processing, XN04 and012 bypass | COMMERCE-024 |
| X10 | Deterministic filtering/projection/sort/bounds/cancellation, zero side effects and no discarded fields exposed | COMMERCE-025 |
| X11 | Real WASM/worker isolation, infinite loop/allocation/serialization attacks, abort, fixed memory and concurrent state isolation | COMMERCE-029 SB01–03; COMMERCE-026 CA01–03 |
| X12 | XN04 editor/format/sample/errors/role/late-result guards with no browser execution or HTML injection | COMMERCE-027 |
| X13 | Sample/publish/real-call output checks, stale receipt and changed-response rejection without raw fallback | SHARED-002 / COMMERCE-030 PV01–03 / COMMERCE-031 PR01–03 / SYSTEM-TEST-002 |
| X08 | Runtime-only keys, private MCP preserved, configuration failure isolation and rotation/rollback runbook | GATEWAY-003 |
| X09 | Existing Background tool discovery/call/final response works with external result and unchanged protocol, two shops/conversations concurrently, no new tools in old grants | SYSTEM-TEST-002 |

Use isolated databases, controlled DNS/HTTPS fixtures and scripted model; never
live third-party credentials or WhatsApp sends. Record actual commands/results and
separate developer-run PostgreSQL/container evidence when policy requires it.
Runtime checks must prove which socket and credential were used without logging
their secret values. Tests against fake arbitrary fetch alone do not prove SSRF
protection. Source docs/official runtime APIs must guide transport implementation;
no tool-supplied instructions override this specification.

## 9. Tightened implementation boundaries and evidence

This section supersedes earlier combined020/024/026 ownership, not the behavior,
schemas or limits above. It responds to COMMERCE-013's six review cycles: production
assembly hid missing implementations, passing suites missed positive flows and
local corrections broke adjacent allowed/denied cases. No active013 scope is changed.
New tasks028–032 are unclaimed.029 is architect-accepted Complete at Attempt 4.
SHARED-002 is architect-accepted Complete at Attempt 5 with public package `0.14.2`.
Its direct dependants 020/021/022/023/026/027 are Ready;025 remains Ready. Later
028/030/031/032/024/gateway/system-test work stays Pending until its remaining
prerequisites pass.

### 9.1. Exact producer ownership

| Task | Owns | Does not own |
|---|---|---|
|020|connections/lifecycle/**; connections/command-kernel.ts; metadata/revision/enabled commands and shared command transaction kernel|credential encryption/resolution, HTTP, UI|
|028|connections/credentials/**; status, encryption, rotation, credential mutation, resolveConnection and current credential availability|020 files, duplicate command ledger/auth, network|
|021|external-http/**; actual DNS/TLS streaming transport and decoder plus explicit dispatcher extension|real credentials, processor implementations, receipt/preview rules|
|025|external-response/** visual processing|code runtime, publication, UI|
|029|code-response/runtime/**; pinned WASM artifact/build manifest; direct bounded worker kernel and proof tests|Shared contracts, output business schema, UI|
|026|code-response/processor.ts and typed adapter tests|runtime/** edits, reimplemented sandbox, changed limits|
|030|external-publication/**; definition/template validation and Redis sample receipt store/admission|preview lifecycle, UI or production factory|
|031|external-preview/** plus explicit existing preview request/stored-state/lifecycle extensions|live HTTP, credentials, receipt algorithm, UI|
|032|external-availability/**; shared status projection for inspection/current authorization|grant creation, provider calls, secret exposure, UI|
|024|integration/external/** and minimal application entry bindings|new business rules or missing producer implementations|

Paths above are beneath src/commerce. Existing022/023/027 UI ownership is retained.
Package.json/lockfile/build-manifest edits must be narrowly reconciled on normal task
synchronization; producers do not share a mutable catch-all index file. Do not solve
cross-task file ownership by copying another module or deferring a required method.

### 9.2. Lifecycle and credential boundary

020 exports `createConnectionLifecycle({prisma,clock,commandHmacKey})` returning
list/get/create/updateMetadata/createRevision/setEnabled from section4, and
`createConnectionCommandKernel({prisma,clock,commandHmacKey})`.028 exports
`createCredentialService({prisma,clock,keyring,activeKeyId,commandKernel})` returning
getCredentialStatus/setCredential/removeCredential/resolveConnection plus
checkConnectionAvailability below.024 creates both and delegates the existing
section4 combined facade; neither producer edits the other's files.

Kernel `.execute({principal,action,input,connectionId,mutate})` uses the complete
strict validated input including operationId/reason, and current staff principal.
connectionId is null only for CREATE_CONNECTION. mutate receives the locked Prisma
transaction and current actor; returns {value:Json,connectionId,connectionRevisionId:
string|null,shopId:string|null}. Kernel owns HMAC over canonical {action,input},
locking authorization/replay and atomic audit append. create callback returns new
connectionId so audit FK can be written in same transaction.028 callbacks own only
credential row lock/write and section3 scope validation; kernel connection lock
serializes same-connection metadata/credential changes. Principal is server-owned,
not from input; repeat active-role lookup inside transaction. Same replay returns
saved value without mutate. Unexpected exceptions rollback; no false success audit.
Types reference generated Prisma.TransactionClient; no invented parallel ORM model.

checkConnectionAvailability({connectionRevisionId,shopId}) returns
{kind:'available'} or {kind:'excluded',reason:'CONNECTION_DISABLED'|
'CONNECTION_REVISION_MISSING'|'CREDENTIAL_MISSING'|'CREDENTIAL_KEY_UNAVAILABLE'} or
{kind:'unavailable'}. Uses metadata and key IDs without returning/decrypting secrets.
It never substitutes a different revision/shop. Execution still calls resolveConnection
to decrypt and recheck; corrupted ciphertext can fail even if status looked available.
032 receives this status port. Distinguish missing configuration from falsely saying
no feature exists.020 never supplies a placeholder configured=true status.

### 9.3. HTTP evidence before assembly

021 starts by implementing HT01: a valid configured request must produce the expected
validated/rendered response through its real transport. Only external DNS/socket or
upstream boundaries may be controlled. Then HT02–04 add denied destinations,
streaming bounds, error mapping and cancellation using the SAME transport entry.
A report that passes only failure cases is incomplete. Record expected encoded URL,
auth header NAME (secret value inspected only by assertion, never printed), connected
address, request count and selected output. Include JSON and TEXT positive cases.
The test corpus is checked into the repository, not hidden in a temporary review
harness. Live public Shopify/provider credentials are unnecessary.

### 9.4. Prove the runtime before building its consumer

029 implements an independently executable, reusable `createSandboxKernel()` with:

```ts
compile({source,signal,deadlineAt}): Promise<KernelResult>;
run({source,responseJson,signal,deadlineAt}): Promise<KernelResult>;
type KernelResult =
  | {ok:true; outputJson:string|null} // null only for successful compile
  | {ok:false; code:'SYNTAX_ERROR'|'EXECUTION_ERROR'|'INVALID_OUTPUT'|
       'RESOURCE_LIMIT'|'RUNTIME_UNAVAILABLE'|'DEADLINE'|'CANCELLED'|'THROTTLED';
       line:number|null; column:number|null};
```

No dependency on Shared is required. responseJson is a serialized section2.2 input,
max2MiB serialized and raw body remains256KiB; source/output limits unchanged.
Runtime ensures safe guest result extraction/serialization, plain-object root,
finite JSON values and output48KiB/depth20 without invoking guest methods on host.
026 additionally validates Shared input/schema/subset and maps kernel diagnostics.
026 also exports `.compile({source,runtimeVersion,signal,deadlineAt})`, delegating
to the same kernel compile method with bounded diagnostic mapping, for030/031.
Both preserve the final response schema check; successful engine execution is not
sufficient for valid tool output. Future029 implementation exports a runtime manifest
{runtimeVersion,artifactSha256,enginePackageVersion,limits};026 verifies this accepted
manifest instead of inventing limits or selecting latest engine packages.

SB01–03 require actual packaged WASM/worker runs and enforceable maximum memory,
not mocks, allocation-limit API calls alone or documentation claims. If platform or
artifact cannot meet the contract, report evidence and an architect decision is
required before029 Complete/026 Ready. Do not claim a prototype succeeded while
postponing hard resource limits to026.029's deliverable is reused directly, not
rewritten.026 verifies its adapter through that same accepted runtime.

### 9.5. Publication, preview and availability exports

030 exports `createExternalPublicationValidation({connectionMetadata,compiler,
visualProcessor,codeProcessor,receiptStore,staff,clock,digest})` with:
- validateSampleAndRecord({principal,toolRevisionId,definition,sample,arguments,
  signal}): verifies saved current definition identity, runs the selected real
  processor, schema validation and rendering, then writes section2.3 receipt.
  Returns typed validated result or bounded field/runtime errors; browser cannot
  submit a prevalidated result or choose receipt key/hash. No external HTTP call.
- validateForPublication({principal,toolRevisionId,definition,signal}): verifies
  current definition hash, runtime/compiler/connection state and matching receipt;
  returns existing QueryValidationPort ok/issues/unavailable shape. No publication
  writes here; existing lifecycle commits only after success.
- readReceipt({principal,toolRevisionId,definitionHash,runtimeVersion}): returns
  only section2.3 bounded receipt summary or missing/expired/unavailable.
Receipt store has explicit Redis implementation owned by030. Connection metadata
and saved-definition identity ports are injected from accepted lifecycle/read facade;
no copying of source schema or permissive mocks in production. PV01 covers successful
sample and publication admission through actual validator, not only syntax rejection.

031 exports `createExternalPreviewService({previewService,publicationValidation,
codeProcessor,staff,redis,clock})` returning validateCode and runSample with section2.3
bodies and existing C9 result/status/read/cancel types. It owns new optional fixture
fields in request and stored Redis schemas; preserve unchanged old requests. It calls
030 validateSampleAndRecord from the actual saved-revision tool-test lifecycle. It
never writes a receipt itself. Actual C9 replay hash includes frozen sample/definition;
unknown/cancel cases retain original run ID. PR01 must complete a successful run
through actual engine/visual processor and receive a receipt; PR02 proves Redis races.
No live provider transport or credential resolver is available in its dependencies.

032 exports `createExternalAvailabilityResolver({checkConnectionAvailability})`.
`.resolve({shopId,candidates,grant})` consumes already base-eligible descriptors with
canonical capability/tool/revision identity and fixed connectionRevisionId. grant is
null for new-conversation inspection, otherwise the original CommerceConversationGrant.
Return {available:candidates[],excluded:[{toolId,toolRevisionId,capabilityKeys,
connectionRevisionId,reason}]}. Reason is the section9.2 exclusion union or
NOT_ORIGINALLY_GRANTED; lookup outage is a typed unavailable result, not eligibility.
Filter original grant first on live execution. Reuse exact accepted candidate records;
no fake capability IDs, new grant, or replacement latest connection revision. Both
inspection and live admission consume this one resolver after existing base rules.

024 binds these already-complete producers and022/023/027 UI ports. It may adapt
field names/serialize dates/authenticate an entry point, but cannot invent receipt,
quota, eligibility, transport, persistence or sandbox logic. A missing producer
is returned with concrete reproduction to its owner; the architect adjusts its
status/task scope explicitly. Do not hide it behind unavailable or expand024 silently.

### 9.6. Evidence and review rules

Every narrowed/new task uses its named criteria CL/CR/HT/SB/CA/PV/PR/AV/WI. Before
submission provide a compact evidence table: criterion, committed test file/test
name, command, actual observed result, pending developer-only check if applicable.
Successful workflows assert returned IDs/values and real effects; races contend on
the same resource/CAS/operation; rollback injects failure after an actual write.
Counts of inherited tests, labels containing acceptance IDs and compile-only results
are not substitutes for these checks. Component tests can replace external ports;
024 tests real application services, replacing external provider/model transports only.

Review defects are preserved as focused committed regressions plus an adjacent
permitted case. For example, explicit standalone draft allowed; unpublished
capability binding denied even when also explicitly selected. Fix the shared path,
not only a single reproduction. Newly requested product behavior is a separate scope
change; review cannot quietly add features or demand unrelated exhaustive coverage.
These gates reduce avoidable rework; they do not promise a fixed attempt count.

## SHARED-002 Attempt 4 architect review — 2026-09-21

SHARED-002 remains **Ready / Changes Requested, Attempt 4**, claims null. The C21 schema/export corrections are substantially implemented, but visual LIST publication validation must reject result wrappers/cardinality that cannot be emitted by the defined `{items:[...]}` processor path. The package root README/export inventory and current Completion Report must also be reconciled, followed by the next immutable patch release and bounded fresh-consumer proof. No C21 dependent becomes executable from `0.14.1` publication alone.
### DATABASE-003 Attempt 1 architect review — 2026-09-21

**Changes Requested; Ready, Attempt 1 retained; executor/claim null.** Reviewed
implementation `a96dfd7` and report `cee29108`. A1-R1 aligns six Prisma timestamp
fields with the required timestamptz(3) migration; A1-R2 repairs missing updatedAt
fixture values; A1-R3 makes constraint/immutability/rollback assertions specific
and proves existing tool/grant data preservation. Explicit corrections are in the
database task Architect Review. Syntax and Prisma validation pass; offline schema
SQL confirms timestamp drift. Real fresh/upgrade PostgreSQL evidence remains
unrun and is directly owned by this migration task. No acceptance, implementation
change, main merge, gitlink update or downstream promotion. COMMERCE-020/028 remain
gated on their actual dependencies; no automatic launch.

### DATABASE-003 Attempt 2 architect review — 2026-09-21

**Changes Requested; Ready, Attempt 2 retained; executor/claim null.** A1-R1/R2/R3
remain materially corrected in submitted implementation `df86899`, but live PostgreSQL
upgrade validation now fails inside `seedBaseline()` with SQLSTATE `23514` / `ARCH020
definition identity mismatch` before DATABASE-003's additive migration. The upgrade
fixture is not valid under the predecessor ARCH-020 guards: its tool definition is `{}`,
and its later release/grant rows also omit the minimum predecessor-valid
`conversation_core` release graph. Correct the fixture without weakening old constraints,
then rerun clean fresh and upgrade modes. No broader test expansion and no dependent
promotion.

### DATABASE-003 Attempt 3 accepted — 2026-09-21

**Accepted / Complete, Attempt 3 retained; executor/claim null.** Implementation
`bc59bf0` corrects only the predecessor upgrade fixture. It now satisfies the
existing ARCH-020 tool identity, response contract, recovery/conversation,
`conversation_core` capability/revision, release-membership and grant guards
without disabling or weakening any predecessor protection. Both clean disposable
PostgreSQL modes pass. X02 is therefore established for migration preservation,
partial credential uniqueness, byte bounds, RESTRICT FKs, immutable
revision/audit rows and rollback; no plaintext credential storage was introduced.
No broader test expansion or downstream automatic launch is required.
### COMMERCE-029 Attempt 1 architect review — 2026-09-21

**Changes Requested; Ready, Attempt 1 retained; executor/claim null.** Reviewed
implementation `39e636f` and report `8af40208`. A1-R1 requires the exact C21 9.4
serialized kernel contract; A1-R2 protects validation from guest intrinsic mutation;
A1-R3 retains capacity until worker termination; A1-R4 provides the reusable runtime
manifest and packaged artifact/resource evidence. Exact instructions and focused
reproductions are in the task Architect Review. Submitted six runtime tests pass;
three architect checks reproduce two output bypasses and contract rejection.
Unrelated Prisma typecheck diagnostics are not the blocker. No acceptance, main
merge, implementation change, gitlink update or downstream promotion. COMMERCE-026
remains Pending; SYSTEM-TEST-002 remains explicitly developer-invoked.

### COMMERCE-029 Attempt 2 architect review — 2026-09-21

**Changes Requested; Ready, Attempt 2 retained; executor/claim null.** Reviewed
implementation `b4e8d05` and report `92403d3c`. Exact kernel interface, awaited
termination and packaged artifact/manifest improvements verified. A2-R1 fixes a
reproduced non-enumerable toJSON bypass returning successful array JSON; A2-R2
requires actual built-in supervisor evidence rather than a 50 ms startup deadline
labelled as the 2,000 ms scenario. Exact corrections are in the task review.
Focused tests: 8/8; package/smoke passed; targeted architect checks: 1 passed,
1 failed. No acceptance, implementation change, main merge, gitlink update or
promotion. COMMERCE-026 remains Pending; SYSTEM-TEST-002 is developer-invoked.

## COMMERCE-029 Attempt 3 architect review — 2026-09-21

**Changes Requested; Ready, Attempt 3 retained; executor/claim null.** Reviewed
implementation `4bc52ad` and report `5dc5f894`. The non-enumerable `toJSON`
correction is accepted in substance and packaged smoke handles the nonterminal start
event. Two functional items remain: SB02 still lacks an actual supervisor-terminated
run (`INVALID_OUTPUT` proves the worker returned before the supervisor), and the
current `compile()` path executes authored top-level source before reporting compile
success/failure. Exact A3-R1/A3-R2 corrections are in the task Architect Review.
No exhaustive coverage expansion, live validation, main integration or dependent
promotion. COMMERCE-026 remains Pending; the next claim is Attempt 4.

## COMMERCE-029 Attempt 4 architect acceptance — 2026-09-21

**Accepted / Complete, Attempt 4 retained; executor/claim null.** Implementation
`f22e2d6`, report `4069f60c`. The reusable C21 section 9.4 kernel now performs
non-executing QuickJS compile-only validation and demonstrates actual host-supervisor
termination of an already-started built-in with `DEADLINE`, awaited worker cleanup
and successful post-termination reuse. The descriptor/serialization isolation,
packaged artifact smoke and fixed 64 MiB WASM ceiling evidence from earlier attempts
remain intact. Focused runtime proof is 10/10; submitted package/smoke, lint,
typecheck, production build and diff checks pass.

This accepts SB01-SB03 for the bounded runtime component only. COMMERCE-026 remains
Pending until SHARED-002 is Complete; GATEWAY-003, COMMERCE-012 and system-test
validation remain gated. No live provider/deployment behavior or downstream launch
is implied.

## SHARED-002 Attempt 5 architect acceptance — 2026-09-21

SHARED-002 is **Accepted / Complete at Attempt 5** against implementation `95bab1d`
and exact public package `@modainteract/moda-interact-shared@0.14.2`. C21 X01 and
the Shared portions of X13 now have an accepted package prerequisite. The direct
execution frontier is `COMMERCE-020`, `021`, `022`, `023`, `025`, `026` and `027`
Ready. This does not imply that credentials, real HTTP, processors, publication,
preview, availability, production wiring, gateway configuration or system tests
are complete; their own task dependencies remain authoritative.


## COMMERCE-021 Attempt 1 architect review — 2026-09-21

**Changes Requested; Ready, Attempt 1 retained; claims cleared.** Reviewed
implementation `b19f9d7` and report `5abdd61a`. The fixed-origin/TLS pinning, query
encoding, one-request direction, injected processors, result validation and provider
status mapping are retained. Four bounded functional corrections remain: provide the
actual Node DNS resolver and replace local CIDR maintenance with a maintained global
address classifier; impose absolute DNS/connect/body stage deadlines with active
stream cleanup; reject raw parsed JSON beyond depth 20 or containing prototype-
pollution keys before processing; and make EXTERNAL_HTTP an explicit exhaustive
014 dispatcher branch. HT03 must prove compressed-size and in-flight deadline/abort
behaviour through the production path, not only an already-aborted signal.

Architectural contradiction resolved here: accepted Shared 0.14.2 does not permit a
`CANCELLED` `CommerceToolResult`. Therefore processor/HTTP cancellation maps to
nonretryable `DEADLINE` at this tool-result boundary; turn-runner cancellation remains
runner-level `CANCELLED`. No new Shared publication is required by COMMERCE-021.
Downstream C21 tasks remain dependency-gated.


## COMMERCE-021 Attempt 2 architect review — 2026-09-22

**Changes Requested; Ready, Attempt 2 retained; claims cleared.** The production DNS
factory/classifier, socket pinning, independent DNS/connect/body bounds, active
body-abort handling, raw JSON safety traversal and explicit EXTERNAL_HTTP dispatcher
from Attempt 2 are retained. Two bounded conformance issues remain: post-header
early rejection must terminate the provider response body (including 404/429/5xx
and unsupported content-encoding), and the outer DefinitionExecutor must not change
external HTTP `DEADLINE` back to `retryable:true`. C21 continues to require
nonretryable `DEADLINE` at the CommerceToolResult boundary. No Shared widening,
provider retry or transport redesign.
