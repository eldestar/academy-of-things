# SCIM 2.0 provisioning

Single sign-on (SSO) lets Dana open the company's task app with her work login. It does not make sure Dana has an account in that app on her first day, or that the account is switched off on her last. That job is **provisioning**, and the standard for it is **SCIM** (System for Cross-domain Identity Management). Facts checked 2026-10-06 against RFC 7642, RFC 7643, RFC 7644, Okta's documentation and Microsoft's Entra documentation. Where a vendor does something different from the standard, the text says so.

## Why SSO is not enough

- **Provisioning** means creating and updating an account. **Deprovisioning** means switching it off, or removing it, when someone leaves.
- Some apps create an account the first time someone signs in. This course calls that **just-in-time (JIT) creation**. RFC 7642 contrasts SCIM with protocols such as SAML web SSO and says SCIM provisions and deprovisions in a separate context from authentication. (RFC 7642 itself puts the label "just-in-time provisioning" on that separate SCIM mode, so JIT here is this course's narrower word for an account created at sign-in, not the RFC's usage.)
- JIT has two gaps. The app only learns about Dana when she shows up, and nothing happens at sign-in time when she leaves: a person who has left is no longer signing in, and if the IdP refuses her login, that refusal happens at the IdP and the app sees nothing. (That second gap is reasoning about how sign-in works, not a rule in a standard.)
- With SCIM the identity provider pushes the change whether or not anyone signs in.

## The two sides

- The **identity provider (IdP)**, such as Okta or Microsoft Entra ID, is the **SCIM client**. It sends the requests.
- Your app is the **SCIM server**. The RFCs call the app the **service provider**, the same word SAML uses for the app.
- They talk over HTTPS using ordinary web requests with JSON bodies. **POST** creates a record, **GET** reads one, **PATCH** changes part of a record, **PUT** replaces a whole record and **DELETE** removes one. An admin pastes the app's base URL and a secret token (a **bearer token**: whoever holds it can call the server, so treat it like a password) into the IdP.
- There are two kinds of record: **Users** at `/Users` and **Groups** at `/Groups`. A group holds a list of members.
- One person has three names. `userName` is the login name: the app requires it to be unique and does not treat it as case-sensitive, and it can be edited, so it can change. `externalId` is a label the IdP chooses for her, and the app does not enforce that it is unique. `id` is assigned by the app, never changes and is never reused. The IdP stores the `id` and uses it in later requests.

## The life of an account

IT teams call the three moments in an account's life **joiner** (a new hire), **mover** (someone who changes team) and **leaver** (someone who leaves). `{id}` stands for the real id.

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

1. **Joiner.** The IdP sends `POST /Users` with her `userName`, her `externalId` and `active=true`. Okta first checks whether the app already has that `userName`, and only creates the user if it does not.
2. The app answers **201 Created** and includes the `id` it assigned.
3. **Mover.** When Dana joins a team, the IdP sends `PATCH /Groups/{id}` to add her to that group's member list. Removing her uses the same request. (Okta sends a `PUT` of the whole group instead to apps built with Okta's App Integration Wizard, the tool an admin uses to connect a custom app.)
4. **Leaver.** The IdP **deactivates** her by setting `active` to `false`. For an app from Okta's catalogue (the Okta Integration Network, OIN) that is `PATCH /Users/{id}`. Apps built with the App Integration Wizard get a `PUT /Users/{id}` carrying `active=false` instead.
5. **Failure.** The app has saved `active=false`, but Dana's browser still has a session from before. Unless the app acts, her old session still works.
6. **Fix.** None of the requests that RFC 7644 defines ends a session, so a SCIM server is not required to end one. Your app must end her sessions itself when it sees `active=false`.
7. Some IdPs send `DELETE /Users/{id}` when a user is removed for good. Entra does this by default for a hard delete; Okta never sends DELETE for users.
8. After a DELETE the app answers **404 Not Found** for every later request about that `id`.

## Deactivate or delete

- `active` is the user's administrative status. RFC 7643 says its definitive meaning is decided by the app. Typically `true` means the user can sign in and `false` means the account is suspended.
- A deactivated account still exists, so it can be switched back on. Okta's own examples are a return from parental leave and a rehired contractor. That is the app's copy of the account. Deactivating the user inside Okta is a different, destructive step (Okta's Users API reference says it cannot be recovered; lesson 7 covers it), and suspending a user in Okta sends the app nothing.
- A deleted account is gone. The standard lets an app keep the data privately, but it must answer 404 for every later request about it.
- Okta deprovisioning sets `active=false` in the app's own account record, so it does reach the app. If an admin later deletes the already deactivated profile in Okta, Okta sends nothing more.
- Entra disables the user in the app when a user leaves scope, is disabled or is soft-deleted, and by default deletes it only when the user is hard-deleted at the source. Microsoft says apps that do not support soft-delete (switching an account off instead of removing it) can get a DELETE earlier, that a few catalogue apps are set up that way.

## What goes wrong

- **409 Conflict, "userName already in use".** The app refuses to create a second user with the same `userName`. Look for an older or duplicate account.
- **401 Unauthorized.** The token is wrong, missing or expired, so every request fails. In Entra, when most calls keep failing (for example with invalid credentials), the job enters *quarantine* and runs gradually less often, down to once a day.
- **429 Too Many Requests.** The app is rate-limiting the IdP. Okta pauses, waits the number of seconds in the `Retry-After` header (five minutes if there is none), doubles the wait on each retry and stops after 10 attempts, so a person must then step in.
- **Group changes do not arrive.** Okta only sends a membership change when the user is in the Okta group, is assigned to the app, and the group is pushed on the *Push Groups* tab. Okta does not support using the same group for both assignment and push, so make a separate push group. Okta sources memberships, so edits made to a pushed group inside the app cause sync problems.
- **A renamed login.** Keep `userName` stable. Okta advises against using an email address as the user ID because emails often change.

## Your task

This sample is invented, not from a real system. Read it and answer without scrolling up.

```text
POST /Users   {"userName": "dana@example.com", "externalId": "00u1abc", "active": true}
```

Which field is the login name? Which value will the app invent and send back, and in which reply? If the app already holds `dana@example.com`, which status code comes back? Check yourself against steps 1 and 2 and the first bullet under *What goes wrong*.

Next: lesson 6 covers MFA and sessions, and lesson 7 covers the joiner-mover-leaver process that SCIM carries out.
