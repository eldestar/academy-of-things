# SCIM 2.0 provisioning

You have configured SAML and OIDC apps and clicked through an app's **Provisioning** tab. This lesson explains what SCIM sends over the wire and why it breaks. Facts checked 2026-10-06 against RFC 7642, RFC 7643, RFC 7644, Okta's SCIM 2.0 reference, Group Push and rate-limit pages, and Microsoft Learn's Entra provisioning pages. Vendor behaviour is as those pages read that day, so confirm it in your own tenant.

## Why SCIM sits next to SSO

- RFC 7642 contrasts SCIM with protocols such as SAML web SSO and says SCIM provisions and deprovisions in a separate context from authentication. RFC 7642 itself puts the label "just-in-time provisioning" on that separate SCIM mode, so this lesson uses JIT in a narrower sense: an account created at first sign-in by the sign-in protocol. That is this course's usage, not the RFC's.
- The author's reasoning, not a quote or a rule from any standard: JIT creation only fires when someone signs in. It cannot pre-create the account with groups before day one, it never fires for a leaver who no longer signs in, and it cannot see a mover's change until their next login. SCIM runs when the directory changes, whether or not anyone signs in.
- Roles: the IdP is the **SCIM client**. The app is the **SCIM server**, which RFC 7643 calls the **service provider** (the same side as the SAML SP).

## Resources, identifiers and mapping

- **Resources** (RFC 7643): `User`, `Group` and the enterprise extension `urn:ietf:params:scim:schemas:extension:enterprise:2.0:User` (`employeeNumber`, `costCenter`, `organization`, `division`, `department`, `manager`). Endpoints are `/Users` and `/Groups`; `/ServiceProviderConfig`, `/Schemas` and `/ResourceTypes` describe what the server supports.
- **`id`** is issued by the server, must be stable and never reassigned, and the client must not set it. **`userName`** is required, unique across the server's users and case-insensitive. **`externalId`** is issued by the client; the server does not enforce uniqueness.
- Okta requires a server to store `userName`, `name.givenName`, `name.familyName` and `emails`, and advises a user ID distinct from the email address because emails change.
- **Mapping** is your lever: Okta's Profile Editor maps attributes between the Okta profile and the app. In Entra, *Match objects using this attribute* picks the matching property, and Microsoft's SCIM endpoint page has an example mapping table that maps `userPrincipalName` to `userName` and `mailNickname` to `externalId`.
- The SCIM match attribute (`userName` or `externalId`) and the SSO account key are separate things. The key is a persistent NameID in SAML, `iss` plus `sub` in OIDC, and in Entra, where `sub` is pairwise per application, Microsoft's guidance is `tid` plus `oid` (lesson 1). The app must link the two explicitly, and must never link a sign-in to an account on the email claim or attribute. A `userName` that happens to look like an email address is only the SCIM match attribute, not the SSO account key.

## The life of an account

Okta's flow is below; Entra's is close. `{id}` is the server-issued id.

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

1. **Joiner.** On assignment Okta runs `GET /Users?filter=userName eq "..."` on the identifier you configured. No match means `POST /Users` (`userName`, `emails`, `active: true`; Okta's create example also shows an `externalId`, see the first bullet under *What breaks* for why not to rely on it). A duplicate `userName` must get `409` with `scimType: uniqueness` (RFC 7644 §3.3).
2. The server answers `201 Created` with the `id`. The IdP keeps it and addresses later calls to `/Users/{id}`; Entra says it caches the target system's ID.
3. **Mover.** Okta's OIN integrations send most user updates as `GET` then `PUT` with the whole body. Apps built with Okta's App Integration Wizard (Wizard apps) send every update as `PUT`. For groups, OIN integrations send `PATCH /Groups/{id}`, for example one `remove members[value eq "..."]` plus one `add members` in the same request, while Wizard apps send a `PUT` of the whole group.
4. **Leaver.** Deprovisioning sends `active: false`: a `PATCH` for OIN apps (`{"op":"replace","value":{"active":false}}`, no path), a `PUT` for Wizard apps.
5. The server saves `active=false` but a browser session opened earlier still works.
6. None of the operations in RFC 7644 ends a session or revokes a token, so your app must do it when it sees `active=false`.
7. By default Entra sends `DELETE /Users/{id}` when a user is hard-deleted at the source (see the next section for its exceptions); Okta never sends DELETE for users.
8. After DELETE the server must return `404` for that `id`.

## Deactivate, delete and group scope

- RFC 7643: `active` is administrative status and **the service provider defines its meaning**; typically `true` can sign in, `false` is suspended. RFC 7644 §3.6: on DELETE a provider **may keep the data** but **must return 404** for the old id and must omit it from queries; it **should not** count it as a `userName` conflict.
- **Okta** sets `active=false`, flips it back to `true` on reprovisioning (parental leave, a rehired contractor), sends nothing when you delete an already deactivated profile, and sends no deprovisioning event for users suspended in Okta. This is the app-side account, not the Okta user: deactivating the user in Okta is a different, destructive step (Okta's Users API reference says it cannot be recovered; lesson 7), and suspending a user sends the app nothing.
- **Entra** disables the user in the app when it leaves scope, is unassigned, disabled or soft-deleted, and by default sends DELETE only when the user is hard-deleted (30 days after soft delete). Microsoft adds that an app which does not support soft-delete can receive DELETE for the other events too, and that a few gallery apps are set up that way. It expects an inactive user to still be returned; only a hard-deleted user should not be.
- **Okta group membership** needs all three: the user is in the Okta group, is assigned to the app, and the group is pushed. Okta does not support using the same group for assignment and Group Push; make a separate push group. Pushed groups are managed from Okta, and changes made in the target app cause sync problems.
- **Entra scope** most commonly comes from assignments. It cannot read nested groups, only immediate members of an assigned group, and it provisions group objects only if the app supports them (which needs PATCH).

## What breaks

- **Duplicate `userName`.** If the lookup filter is unsupported or returns nothing for an existing user, the IdP concludes the user is new, `POST`s, and gets `409`. Okta requires `eq` on the identifier it uses, and accepts either an empty list or a `404` as "not found". In Okta's documentation the lookup filter is always written on `userName`, with the value taken from the unique identifier you configured for the integration (for example the email), so the lookup is not on `externalId`. Okta's reference describes `externalId` three inconsistent ways: its prose says Okta stores the server's returned ID as `externalId` in the Okta profile, its create example sends `externalId` in the `POST` body, and a note under another example says it was not in the `POST` but was generated by the server. RFC 7643 says only the client issues it. This lesson relies on none of the three: key your records on the server `id` and the lookup on `userName`. In Okta's documented flow a create follows only when the lookup finds nothing, so a `409` for a user the app already holds means the lookup missed them: fix the filter rather than ignore the error (my reading of that flow).
- **Renames.** The IdP links by cached `id`, so a rename should be an update. If it has to match again, as Okta does on every assignment, and the server still holds the old `userName`, the lookup finds nothing and a second account is created (inference from the documented flow). Let `userName` change via `PUT` or `PATCH` with the same `id`.
- **PATCH dialects.** Entra emits `op` as `Add`, `Replace` and `Remove` and tells servers not to require a case-sensitive match; the RFC examples are lowercase. Every PATCH example on Microsoft's SCIM page, for users and groups, uses the capitalised form, while Okta's examples (deactivate, group remove and add) are lowercase, so a server that compares `op` exactly can pass Okta and fail Entra's PATCH calls, user and group alike, while POST creates carry no `op` and succeed. Entra provisions groups only through PATCH and says it does not support `/Bulk`. Okta deactivates with a path-less `replace` of an object, Entra with `path: "active"`.
- **Rate limits.** RFC 7644 never mentions 429. Okta honours integer-seconds `Retry-After`, otherwise waits five minutes, doubles each retry and fails the task after 10 attempts. An HTTP-date `Retry-After` is ignored, so the five minutes applies.
- **Tokens.** A rejected token fails every call. Entra quarantines a job when most calls fail (it names invalid credentials as an example), cycles drop to once a day and the job is disabled after four weeks. Okta uses a refresh token only if your authorization server issues one.

## Your task

Local, run on this machine. This is a toy (in memory, no TLS, no paging, no `remove` support), only for seeing the shapes. Save it as `toy_scim.py`.

```python
import itertools, json, re
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import unquote_plus
USERS, IDS = {}, itertools.count(1)
class H(BaseHTTPRequestHandler):
    def reply(self, code, obj=None):
        self.send_response(code); self.send_header("Content-Type", "application/scim+json"); self.end_headers()
        if obj is not None: self.wfile.write(json.dumps(obj).encode())
    def route(self):
        err = lambda c, d, t=None: self.reply(c, {"schemas": ["urn:ietf:params:scim:api:messages:2.0:Error"], "status": str(c), "detail": d, **({"scimType": t} if t else {})})
        if self.headers.get("Authorization") != "Bearer demo-token": return err(401, "bad token")
        body = json.loads(self.rfile.read(int(self.headers.get("Content-Length") or 0)) or "{}")
        path, _, qs = self.path.partition("?"); u = USERS.get(path.split("/")[-1])
        if self.command == "POST":
            if any(x["userName"].lower() == body["userName"].lower() for x in USERS.values()): return err(409, "userName already in use", "uniqueness")
            uid = f"u{next(IDS)}"; USERS[uid] = {**body, "id": uid, "active": body.get("active", True)}; return self.reply(201, USERS[uid])
        if self.command == "GET" and path == "/Users":
            m = re.search(r'userName eq "([^"]+)"', unquote_plus(qs)); hits = [x for x in USERS.values() if m and x["userName"].lower() == m[1].lower()]
            return self.reply(200, {"totalResults": len(hits), "Resources": hits})
        if not u: return err(404, "no such user")
        if self.command == "DELETE": del USERS[u["id"]]; return self.reply(204)
        if self.command == "PATCH":
            for op in body["Operations"]: u.update(op["value"] if "path" not in op else {op["path"]: op["value"]})  # Okta: no path. Entra: a path.
            u["active"] = str(u["active"]).lower() == "true"  # Entra's compatibility page shows the string "False"
        self.reply(200, u)
    do_GET = do_POST = do_PATCH = do_DELETE = route
HTTPServer(("127.0.0.1", 8765), H).serve_forever()
```

Run `python3 toy_scim.py &`, then predict each status before you run these. The output is real, from this session.

```bash
H='Authorization: Bearer demo-token'; B=http://127.0.0.1:8765
curl -s -w ' [%{http_code}]\n' -H "$H" -X POST $B/Users -d '{"userName":"dana@example.com","externalId":"00u1abc"}'
curl -s -w ' [%{http_code}]\n' -H "$H" -X POST $B/Users -d '{"userName":"Dana@Example.com"}'
curl -s -w ' [%{http_code}]\n' -H "$H" -X PATCH $B/Users/u1 -d '{"Operations":[{"op":"replace","value":{"active":false}}]}'
curl -s -w ' [%{http_code}]\n' -H "$H" -X PATCH $B/Users/u1 -d '{"Operations":[{"op":"Replace","path":"active","value":"True"}]}'
curl -s -o /dev/null -w '[%{http_code}]\n' -H "$H" -X DELETE $B/Users/u1; curl -s -w ' [%{http_code}]\n' -H "$H" $B/Users/u1
```

```text
{"userName": "dana@example.com", "externalId": "00u1abc", "id": "u1", "active": true} [201]
{"schemas": ["urn:ietf:params:scim:api:messages:2.0:Error"], "status": "409", "detail": "userName already in use", "scimType": "uniqueness"} [409]
{"userName": "dana@example.com", "externalId": "00u1abc", "id": "u1", "active": false} [200]
{"userName": "dana@example.com", "externalId": "00u1abc", "id": "u1", "active": true} [200]
[204]
{"schemas": ["urn:ietf:params:scim:api:messages:2.0:Error"], "status": "404", "detail": "no such user"} [404]
```

Notice the case-insensitive 409, both PATCH dialects landing on one handler, and the 404 after DELETE. Stop the server with `kill %1`. Then ask what it does not do: step 6, paging and the `remove` operation. Lesson 6 covers sessions in general; lesson 7 covers the joiner-mover-leaver runbook, including what to check beyond `active=false`, that step 6 belongs to.
