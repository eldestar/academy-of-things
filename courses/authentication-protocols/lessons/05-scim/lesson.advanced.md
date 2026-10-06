# SCIM 2.0 provisioning

You are building or reviewing the service-provider (server) side of SCIM and need to know where the standard is firm, where it leaves room, and where the two big IdPs bend it. Facts checked 2026-10-06 against RFC 7642, RFC 7643 and RFC 7644 (section numbers below), Okta's SCIM 2.0 reference and rate-limit pages, and Microsoft Learn's Entra provisioning pages. Where Microsoft's own pages disagree, the text says so.

## Identifiers and what the RFCs leave to you

- **`id`** (RFC 7643 §3.1): issued by the server, unique across all its resources, stable, **non-reassignable**, never set by the client. `bulkId` is a reserved string. **`externalId`**: issued by the client, interpreted as scoped to its provisioning domain; the server does not enforce uniqueness.
- Okta's reference is inconsistent about `externalId`: its create example sends it in the `POST` body, a note under a second example says it was not in the `POST` and was generated and returned by the server, and the prose says Okta stores the server's unique ID as `externalId` in the Okta profile. The RFC says only the client issues it. Key your records on `id` and log what you receive. The SCIM match attribute (`userName` or `externalId`) is separate from the SSO account key (a persistent NameID in SAML, `iss` plus `sub` in OIDC, and `tid` plus `oid` in Entra, where `sub` is pairwise per application; lesson 1): the app must link them explicitly and never link a sign-in to an account on the email claim or attribute. A `userName` that happens to look like an email address is only the SCIM match attribute, not the SSO account key.
- **`userName`** (§4.1.1): required, unique across all Users, case-insensitive, and `readWrite`, so a rename keeps the `id`. Before comparing for uniqueness a provider MUST apply the PRECIS rules of RFC 7613 (RFC 7644 §5). Entra's SCIM validator checks that a `PATCH` can change its joining property (for example `userName`) and that a filter on the new value then finds the user.
- **`active`** (§4.1.1): boolean administrative status whose definitive meaning the provider decides. **DELETE** (RFC 7644 §3.6): the provider MAY keep the data but MUST return 404 for every later operation on that resource, MUST omit it from queries, and SHOULD NOT count it in conflict calculation, so a `POST` with the deleted `userName` SHOULD NOT get 409.
- Recommendation: model `active=false` as a reversible suspension that still appears in queries, and DELETE as removal that 404s and frees the `userName`. Entra's documentation fits this: it queries the target by its matching attribute, creates only when nothing matches, and wants an inactive user returned, with only a hard-deleted one absent.
- **Groups** (§4.2): `members[].value` holds the member's `id`; the `groups` attribute on a User is `readOnly`, so membership changes go through the Group resource. The extension URN `urn:ietf:params:scim:schemas:extension:enterprise:2.0:User` joins `schemas` when an extension attribute is addressed by its fully qualified name (RFC 7644 §3.5.2). Entra requires unique group `displayName`, which the RFC does not.

## The life of an account

Okta and Entra differ most at steps 3 and 4.

<!-- diagram:scim-protocol -->
<div style="position:relative;margin:20px 0">
<input type="checkbox" id="sc-pause" class="sc-cb" /><label for="sc-pause" class="sc-btn"><span class="sc-off">Pause animation</span><span class="sc-on">Play animation</span></label>
<div class="sc-box" style="overflow-x:auto">
<svg class="sc-flow" viewBox="0 0 760 738" role="img" aria-labelledby="sc-t sc-d" style="width:100%;min-width:640px;max-width:800px;height:auto;display:block;margin:0 auto">
<title id="sc-t">SCIM lifecycle: create, group change, deactivate, delete</title>
<desc id="sc-d">Eight steps between an identity provider acting as SCIM client and your app acting as SCIM server, with the user's already-open browser session as a third lane. Step 1: the IdP sends POST /Users to create a user with userName, externalId and active true. Step 2: the app answers 201 Created and returns the id it assigned, which the IdP stores. Step 3: the IdP sends PATCH /Groups/{id} to add or remove one member. Step 4: the IdP deactivates the user with PATCH /Users/{id} setting active to false (Okta sends PUT instead to apps built with its App Integration Wizard). Step 5, failure mode: a request on the user's old session is still served unless the app revokes it. Step 6: on active false your app revokes sessions and tokens itself, because RFC 7644 defines no call that ends a session. Step 7: a hard delete is DELETE /Users/{id}, which Entra sends by default on a hard delete and Okta never sends for users. Step 8: the app answers 404 Not Found for every later request for that id. The diagram highlights each step in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
<style>
.sc-box{fill:var(--panel);stroke:var(--border-strong);stroke-width:1.5}
.sc-hot{fill:var(--panel);stroke:var(--accent);stroke-width:2.5}
.sc-ttl{fill:var(--text);font:600 15px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.sc-sub{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.sc-life{stroke:var(--border-strong);stroke-width:1.5;stroke-dasharray:4 5}
.sc-front{stroke:var(--accent);stroke-width:2;fill:none}
.sc-back{stroke:var(--muted);stroke-width:2;stroke-dasharray:7 5;fill:none}
.sc-bad{stroke:var(--bad);stroke-width:2;fill:none}
.sc-main{fill:var(--text);font:600 13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.sc-badt{fill:var(--bad-text)}
.sc-dim{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.sc-badge{fill:var(--accent)}
.sc-b-back{fill:var(--muted)}
.sc-b-bad{fill:var(--bad)}
.sc-b-good{fill:var(--good)}
.sc-bt{fill:var(--on-accent);font:700 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.sc-note{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.sc-note-good{fill:var(--good-bg);stroke:var(--good);stroke-width:1.5}
.sc-note-bad{fill:var(--bad-bg);stroke:var(--bad);stroke-width:1.5}
.sc-nt{fill:var(--body);font:12.5px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.sc-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:24s;animation-timing-function:linear;animation-iteration-count:infinite}
.sc-pk.sc-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.sc-pk.sc-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.sc-g{opacity:.45;animation-duration:24s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.sc-flow:hover .sc-g,svg.sc-flow:hover .sc-pk{animation-play-state:paused}
.sc-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.sc-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.sc-btn:hover{background:var(--hover)}
.sc-cb:focus-visible + .sc-btn{outline:2px solid var(--accent);outline-offset:2px}
.sc-cb:checked + .sc-btn .sc-off,.sc-cb:not(:checked) + .sc-btn .sc-on{display:none}
.sc-cb:checked ~ .sc-box .sc-g,.sc-cb:checked ~ .sc-box .sc-pk{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.sc-g{animation:none;opacity:1}.sc-pk{animation:none;display:none}.sc-btn{display:none}}
@keyframes sc-g0{0%{opacity:1}12.5%{opacity:1}12.51%,100%{opacity:.45}}
@keyframes sc-p0{0%,-0.01%{opacity:0;transform:translateX(0)}0%{opacity:1;transform:translateX(0)}12.5%{opacity:1;transform:translateX(236px)}12.51%,100%{opacity:0;transform:translateX(236px)}}
.sc-g0{animation-name:sc-g0}.sc-p0{animation-name:sc-p0}
@keyframes sc-g1{0%,12.49%{opacity:.45}12.5%{opacity:1}25%{opacity:1}25.01%,100%{opacity:.45}}
@keyframes sc-p1{0%,12.49%{opacity:0;transform:translateX(0)}12.5%{opacity:1;transform:translateX(0)}25%{opacity:1;transform:translateX(-236px)}25.01%,100%{opacity:0;transform:translateX(-236px)}}
.sc-g1{animation-name:sc-g1}.sc-p1{animation-name:sc-p1}
@keyframes sc-g2{0%,24.99%{opacity:.45}25%{opacity:1}37.5%{opacity:1}37.51%,100%{opacity:.45}}
@keyframes sc-p2{0%,24.99%{opacity:0;transform:translateX(0)}25%{opacity:1;transform:translateX(0)}37.5%{opacity:1;transform:translateX(236px)}37.51%,100%{opacity:0;transform:translateX(236px)}}
.sc-g2{animation-name:sc-g2}.sc-p2{animation-name:sc-p2}
@keyframes sc-g3{0%,37.49%{opacity:.45}37.5%{opacity:1}50%{opacity:1}50.01%,100%{opacity:.45}}
@keyframes sc-p3{0%,37.49%{opacity:0;transform:translateX(0)}37.5%{opacity:1;transform:translateX(0)}50%{opacity:1;transform:translateX(236px)}50.01%,100%{opacity:0;transform:translateX(236px)}}
.sc-g3{animation-name:sc-g3}.sc-p3{animation-name:sc-p3}
@keyframes sc-g4{0%,49.99%{opacity:.45}50%{opacity:1}62.5%{opacity:1}62.51%,100%{opacity:.45}}
@keyframes sc-p4{0%,49.99%{opacity:0;transform:translateX(0)}50%{opacity:1;transform:translateX(0)}62.5%{opacity:1;transform:translateX(-236px)}62.51%,100%{opacity:0;transform:translateX(-236px)}}
.sc-g4{animation-name:sc-g4}.sc-p4{animation-name:sc-p4}
@keyframes sc-g5{0%,62.49%{opacity:.45}62.5%{opacity:1}75%{opacity:1}75.01%,100%{opacity:.45}}
.sc-g5{animation-name:sc-g5}
@keyframes sc-g6{0%,74.99%{opacity:.45}75%{opacity:1}87.5%{opacity:1}87.51%,100%{opacity:.45}}
@keyframes sc-p6{0%,74.99%{opacity:0;transform:translateX(0)}75%{opacity:1;transform:translateX(0)}87.5%{opacity:1;transform:translateX(236px)}87.51%,100%{opacity:0;transform:translateX(236px)}}
.sc-g6{animation-name:sc-g6}.sc-p6{animation-name:sc-p6}
@keyframes sc-g7{0%,87.49%{opacity:.45}87.5%{opacity:1}100%{opacity:1}100.01%,100%{opacity:.45}}
@keyframes sc-p7{0%,87.49%{opacity:0;transform:translateX(0)}87.5%{opacity:1;transform:translateX(0)}100%{opacity:1;transform:translateX(-236px)}100.01%,100%{opacity:0;transform:translateX(-236px)}}
.sc-g7{animation-name:sc-g7}.sc-p7{animation-name:sc-p7}
</style>
<defs>
<marker id="sc-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="sc-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="sc-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<line class="sc-life" x1="110" y1="72" x2="110" y2="686"/>
<line class="sc-life" x1="380" y1="72" x2="380" y2="686"/>
<line class="sc-life" x1="650" y1="72" x2="650" y2="686"/>
<rect class="sc-box" x="20" y="10" width="180" height="62" rx="10"/><text class="sc-ttl" x="110" y="36">Identity provider</text><text class="sc-sub" x="110" y="56">SCIM client (Okta, Entra)</text>
<rect class="sc-hot" x="290" y="10" width="180" height="62" rx="10"/><text class="sc-ttl" x="380" y="36">Your app</text><text class="sc-sub" x="380" y="56">SCIM server</text>
<rect class="sc-box" x="560" y="10" width="180" height="62" rx="10"/><text class="sc-ttl" x="650" y="36">User's browser</text><text class="sc-sub" x="650" y="56">already signed in</text>
<g class="sc-g sc-g0">
<text class="sc-main" x="245" y="108">POST /Users</text>
<text class="sc-dim" x="245" y="124">userName, externalId, active=true</text>
<line class="sc-front" x1="124" y1="138" x2="366" y2="138" marker-end="url(#sc-m-front)"/>
<circle class="sc-badge sc-b-front" cx="110" cy="138" r="12"/><text class="sc-bt" x="110" y="142.5">1</text>
</g>
<g class="sc-g sc-g1">
<text class="sc-main" x="245" y="178">201 Created + id</text>
<text class="sc-dim" x="245" y="194">the IdP stores the id</text>
<line class="sc-back" x1="366" y1="208" x2="124" y2="208" marker-end="url(#sc-m-back)"/>
<circle class="sc-badge sc-b-back" cx="380" cy="208" r="12"/><text class="sc-bt" x="380" y="212.5">2</text>
</g>
<g class="sc-g sc-g2">
<text class="sc-main" x="245" y="248">PATCH /Groups/{id}</text>
<text class="sc-dim" x="245" y="264">add or remove one member</text>
<line class="sc-front" x1="124" y1="278" x2="366" y2="278" marker-end="url(#sc-m-front)"/>
<circle class="sc-badge sc-b-front" cx="110" cy="278" r="12"/><text class="sc-bt" x="110" y="282.5">3</text>
</g>
<g class="sc-g sc-g3">
<text class="sc-main" x="245" y="318">PATCH /Users/{id}</text>
<text class="sc-dim" x="245" y="334">active = false (Okta Wizard apps: PUT)</text>
<line class="sc-front" x1="124" y1="348" x2="366" y2="348" marker-end="url(#sc-m-front)"/>
<circle class="sc-badge sc-b-front" cx="110" cy="348" r="12"/><text class="sc-bt" x="110" y="352.5">4</text>
</g>
<g class="sc-g sc-g4">
<text class="sc-main sc-badt" x="515" y="388">request with the old session</text>
<text class="sc-dim" x="515" y="404">still served unless you revoke</text>
<line class="sc-bad" x1="636" y1="418" x2="394" y2="418" marker-end="url(#sc-m-bad)"/>
<circle class="sc-badge sc-b-bad" cx="650" cy="418" r="12"/><text class="sc-bt" x="650" y="422.5">5</text>
</g>
<g class="sc-g sc-g5">
<rect class="sc-note-good" x="276" y="452" width="208" height="48" rx="8"/>
<text class="sc-nt" x="380" y="473">on active = false, your app</text>
<text class="sc-nt" x="380" y="490">revokes sessions and tokens</text>
<circle class="sc-badge sc-b-good" cx="276" cy="476" r="12"/><text class="sc-bt" x="276" y="480.5">6</text>
</g>
<g class="sc-g sc-g6">
<text class="sc-main" x="245" y="534">DELETE /Users/{id}</text>
<text class="sc-dim" x="245" y="550">hard delete (Entra default; Okta never)</text>
<line class="sc-front" x1="124" y1="564" x2="366" y2="564" marker-end="url(#sc-m-front)"/>
<circle class="sc-badge sc-b-front" cx="110" cy="564" r="12"/><text class="sc-bt" x="110" y="568.5">7</text>
</g>
<g class="sc-g sc-g7">
<text class="sc-main" x="245" y="604">404 Not Found</text>
<text class="sc-dim" x="245" y="620">for every later request</text>
<line class="sc-back" x1="366" y1="634" x2="124" y2="634" marker-end="url(#sc-m-back)"/>
<circle class="sc-badge sc-b-back" cx="380" cy="634" r="12"/><text class="sc-bt" x="380" y="638.5">8</text>
</g>
<circle class="sc-pk sc-p0" cx="130" cy="138" r="5.5"/>
<circle class="sc-pk sc-p1 sc-pkback" cx="360" cy="208" r="5.5"/>
<circle class="sc-pk sc-p2" cx="130" cy="278" r="5.5"/>
<circle class="sc-pk sc-p3" cx="130" cy="348" r="5.5"/>
<circle class="sc-pk sc-p4 sc-pkbad" cx="630" cy="418" r="5.5"/>
<circle class="sc-pk sc-p6" cx="130" cy="564" r="5.5"/>
<circle class="sc-pk sc-p7 sc-pkback" cx="360" cy="634" r="5.5"/>
<line class="sc-front" x1="40" y1="714" x2="70" y2="714"/>
<text class="sc-dim" x="78" y="718" style="text-anchor:start">request</text>
<line class="sc-back" x1="156" y1="714" x2="186" y2="714"/>
<text class="sc-dim" x="194" y="718" style="text-anchor:start">response</text>
<line class="sc-bad" x1="279" y1="714" x2="309" y2="714"/>
<text class="sc-dim" x="317" y="718" style="text-anchor:start">failure mode</text>
<rect class="sc-note-good" x="427" y="706" width="22" height="16" rx="4"/>
<text class="sc-dim" x="457" y="718" style="text-anchor:start">what your app must do</text>
</svg>
</div>
</div>
<!-- /diagram:scim-protocol -->

The numbers 1 to 8 match the list below. Step 5 is the failure mode.

1. **Joiner.** Okta first runs `GET /Users?filter=userName eq "..."`, then `POST`s the profile. Its body carries a `password` placeholder even when password sync is off. The server answers `201` with `Location` and `meta.location` (both SHALL) and should include the full representation in the body (RFC 7644 §3.3).
2. The `id` comes back in that `201`; Entra caches it and uses it for every later operation on the user.
3. **Mover and groups.** Okta's OIN apps `PATCH` groups, either `remove members[value eq "..."]` plus `add members`, or a `replace` of the whole `members` list; apps built with Okta's App Integration Wizard `PUT` the group. Entra sends `Add` and `Remove` on `members` with the ids in `value`, expects `204` and advises against returning the member list.
4. **Leaver.** Okta sends `{"op":"replace","value":{"active":false}}` (no path) by `PATCH`, or a full `PUT` for Wizard apps. Entra sends `op` `Replace` with `path` `active`.
5. The `PATCH` succeeds but a session or token issued before it still validates.
6. None of the operations or endpoints in RFC 7644 (§3.2, Table 2) ends a session; the RFC mentions sessions only when discussing how a client authenticates. Revoke sessions, refresh tokens and API tokens when the update lands, or check `active` on every authenticated use; do both for long-lived credentials.
7. Okta never sends `DELETE` for users, and nothing is sent when you delete an already deactivated profile. By default Entra sends `DELETE` only for a hard delete, 30 days after a soft delete. Microsoft adds two exceptions: when the target app does not support soft-delete, the service sends `DELETE` for the soft-delete, unassign and out-of-scope events as well, and a few gallery apps are set up that way and not configurable by customers. A customer can also leave "Delete" unticked in the target object actions, so that nothing is sent on a hard delete.
8. Return `204` for the DELETE, then `404` with the Error schema for every later request on that `id`.

## PATCH, PUT, ETags and bulk

- **PUT** MUST be supported; **PATCH** is optional but SHOULD be offered because groups can be large (§3.5). Entra provisions groups only if you support PATCH. On PUT, `readOnly` values are ignored, an `immutable` value that differs SHOULD get `400 mutability`, and omitted `readWrite` attributes MAY be cleared or defaulted.
- A PATCH request is **atomic** and its operations apply in order (§3.5.2). `remove` requires a `path` (else `400 noTarget`); `replace` on a missing path acts as `add`; a `replace` whose `valuePath` filter matches nothing is `400 noTarget`; removing a non-member succeeds with no change. SCIM drops JSON Patch's array indexes and `move`.
- **Dialects.** Entra emits `Add`, `Replace`, `Remove` and says not to require a case-sensitive match. Its documented group removal is `Remove` on `members` with the ids in `value`, and a server that rejects it cannot take removals from Entra by default. The RFC (§3.5.2.2) defines `remove` by `path` alone: a multi-valued target with no filter has the attribute and all its values removed, and its own "Remove all members of a group" example is `remove` with `path` `members` and no `value`. It does not define a `value` on `remove`, so Entra's form (a bare `members` path plus a `value` list) is outside what the RFC specifies, and a handler that applied the path-only rule to it would empty the group. Honour the ids in `value` when present; empty the group only for a path-only `remove`. Entra's compatibility page lists the RFC-shaped `remove members[value eq "..."]` behind a tenant URL flag (`aadOptscim062020`) and lists the fix as not done, with the date to be decided.
- The same compatibility page shows the default deactivation as `Replace` `active` with the **string** `"False"`, a boolean `false` behind the flag, and, behind the flag, one path-less `replace` whose value object uses dotted keys such as `name.givenName`. Microsoft's main SCIM page shows a boolean with a capitalised `Replace`. Accept every variant.
- **ETags** (RFC 7643 §3.1; RFC 7644 §3.14): `meta.version` must equal the `ETag` header, weak validators are prefixed `W/`, and clients MAY send `If-Match` on PUT and PATCH. Table 8 lists 409 for a version mismatch and 412 for "resource has changed"; pick one and document it. The Okta and Entra pages I read do not mention `If-Match`, so I could not verify either IdP sends it.
- **Bulk** (§3.7) is optional: `failOnErrors`, client `bulkId`, and `maxOperations` and `maxPayloadSize` in `ServiceProviderConfig`. Entra's page says it does not support `/Bulk`; the Okta pages I read do not mention it.

## Queries, pagination and discovery

- **Filter** support is optional. Okta needs `eq` on its identifier and on group `displayName`; Entra uses only `eq` and `and`, and every attribute you treat as unique must be filterable. An unknown operator is `400 invalidFilter`; no match is `200` with `totalResults: 0` (§3.4.2), and Okta also accepts a `404` Error.
- **Pagination** is `startIndex` (1-based) and `count`, stateless: clients MUST expect inconsistent results, and the server MUST NOT return more than `count`. `ListResponse` defines `totalResults`, `Resources`, `startIndex` and `itemsPerPage`, no cursor. Okta pages with `count=100`, advances `startIndex` by 100, wants integers not strings, and requires the same ordering for any `count` and `startIndex`. My recommendation, not from a source: order by an immutable key, because `lastModified` moves a user on every edit.
- **Discovery** (§4, RFC 7643 §5-6): `/ServiceProviderConfig` reports `patch`, `bulk`, `filter`, `changePassword`, `sort`, `etag` and `authenticationSchemes` (SHOULD be readable without authentication); `/ResourceTypes` and `/Schemas` ignore paging, and a `filter` there SHOULD get 403. Entra reads `/Schemas` on gallery apps, not custom ones, and only adds attributes.

## Authentication, retries and failure

- RFC 7644 §2 defines no scheme; servers MUST support TLS 1.2 (§7.2). **Bearer tokens MUST have a limited lifetime** (§7.4, "Bearer Token and Cookie Considerations"). I read this as the credential the SCIM client presents; the RFC does not say whose token it means, and I do not read it as a rule about your users' tokens. Entra's *Secret Token* field takes a "long-lived bearer token" and warns that test tokens do not belong in production. Okta accepts OAuth 2.0 authorization code, Basic or an Authorization header, and refreshes only if your authorization server issues refresh tokens. Okta forbids `_` in a base URL, and one server can serve many Okta orgs with a per-org base URL.
- **No idempotency.** RFC 7643 and 7644 define no idempotency key. A replayed create after a lost `201` hits the uniqueness rule and MUST get `409` (§3.3); do not silently upsert, and expect clients to resolve it with a lookup.
- **429.** RFC 7644 never mentions it. Okta waits integer `Retry-After` seconds, else five minutes, doubles each time and fails the task after 10 attempts; an HTTP-date value is ignored. Entra retries failed items on later cycles with less frequency, quarantines the job when most calls fail, and disables it after four weeks.

## Conformance pitfalls

- **Shape.** Okta wants `totalResults`, `startIndex` and `itemsPerPage` as integers, treats an empty body on create as a failed provisioning, and needs `GET /Groups/{id}` to return `members` when no query parameters are given. Entra wants `id` in every response except an empty `ListResponse`, `application/scim+json` on every response, and `excludedAttributes=members` honoured on group queries.
- **Fidelity.** Entra says to store values exactly as sent, rejecting bad ones with an actionable error rather than normalising them, and `type` values inside a multi-valued attribute such as `emails` must be unique.

## Your task

Local, run on this machine, a toy that normalises both group dialects and stays atomic. The output is real.

```python
import copy, re
def apply_patch(group, ops):  # TOY: members and displayName only
    g = copy.deepcopy(group)  # RFC 7644 3.5.2: atomic, so edit a copy and return it only on success
    for o in ops:
        op, path = o["op"].lower(), o.get("path", "")  # Entra sends Add/Remove/Replace
        m = re.fullmatch(r'members\[value eq "([^"]+)"\]', path)
        if op == "remove" and m: ids = [m[1]]  # Okta style: the id is inside the path filter
        elif op == "remove" and path == "members":  # Entra style: ids in value; RFC 3.5.2.2: no value and no filter removes all values
            ids = [v["value"] for v in o["value"]] if "value" in o else [x["value"] for x in g["members"]]
        elif op == "add" and path == "members":
            have = {x["value"] for x in g["members"]}
            g["members"] += [{"value": v["value"]} for v in o["value"] if v["value"] not in have]; continue
        elif op == "replace" and path == "displayName": g["displayName"] = o["value"]; continue
        else: raise ValueError(f"400 noTarget/invalidPath: {o['op']} {path!r}")
        g["members"] = [x for x in g["members"] if x["value"] not in ids]  # a non-member removal changes nothing
    return g
G = {"displayName": "eng", "members": [{"value": "u1"}, {"value": "u2"}]}
print("okta :", apply_patch(G, [{"op": "remove", "path": 'members[value eq "u1"]'}, {"op": "add", "path": "members", "value": [{"value": "u3"}]}]))
print("entra:", apply_patch(G, [{"op": "Remove", "path": "members", "value": [{"value": "u2"}]}]))
print("path-only remove empties the group:", apply_patch(G, [{"op": "remove", "path": "members"}])["members"])
print("non-member removal is a no-op:", apply_patch(G, [{"op": "remove", "path": 'members[value eq "u9"]'}]) == G)
try: apply_patch(G, [{"op": "add", "path": "members", "value": [{"value": "u4"}]}, {"op": "move", "path": "x"}])
except ValueError as e: print("rejected:", e, "| group unchanged:", G["members"])
```

```text
okta : {'displayName': 'eng', 'members': [{'value': 'u2'}, {'value': 'u3'}]}
entra: {'displayName': 'eng', 'members': [{'value': 'u1'}]}
path-only remove empties the group: []
non-member removal is a no-op: True
rejected: 400 noTarget/invalidPath: move 'x' | group unchanged: [{'value': 'u1'}, {'value': 'u2'}]
```

The path-only `remove members` line is the RFC reading and it empties the group. Decide which clients may reach it (a flag, a permission, a log line) and write that down. The same logic for `active` belongs in the user handler, next to the revocation from step 6. Lesson 7 covers the joiner-mover-leaver process around it.
