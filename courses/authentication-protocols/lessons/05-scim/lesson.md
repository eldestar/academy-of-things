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

<!-- diagram:scim-identifiers -->
<div class="l05a-wrap" style="position:relative">
<input type="checkbox" id="l05a-pause" class="l05a-cb" /><label for="l05a-pause" class="l05a-btn"><span class="l05a-off">Pause animation</span><span class="l05a-on">Play animation</span></label>
<div class="l05a-box" style="overflow-x:auto">
<svg class="l05a-flow" viewBox="0 0 760 490" role="img" aria-labelledby="l05a-t l05a-d" style="width:760px;max-width:100%;min-width:699px;height:auto;display:block;margin:0 auto">
<title id="l05a-t">Identifiers on a SCIM user, and how they differ from the SSO account key</title>
<desc id="l05a-d">A User resource at /Users carries three identifiers. id is issued by the server, must be stable and never reassigned, and the client must not set it. userName is required, unique across the server's users and case-insensitive. externalId is issued by the client and the server does not enforce uniqueness. Separate from the resource, the match attribute is userName or externalId and is where mapping matters: Okta's Profile Editor maps attributes, and in Entra the setting Match objects using this attribute picks the matching property. The SSO account key is a different thing: a persistent NameID in SAML, iss plus sub in OIDC, and tid plus oid in Entra. The app must link the SCIM account and the SSO key explicitly and never link a sign-in to an account on the email claim or attribute. The diagram highlights each part in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
<style>
svg.l05a-flow{--ink:light-dark(#000000,#ffffff)}
.l05a-box{fill:var(--panel);stroke:var(--border-strong);stroke-width:1.5}
.l05a-hot{fill:var(--panel);stroke:var(--accent);stroke-width:2.5}
.l05a-ttl{fill:var(--ink);font:600 15px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l05a-sub{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l05a-life{stroke:var(--border-strong);stroke-width:1.5;stroke-dasharray:4 5}
.l05a-front{stroke:var(--accent);stroke-width:2;fill:none}
.l05a-back{stroke:var(--muted);stroke-width:2;stroke-dasharray:7 5;fill:none}
.l05a-bad{stroke:var(--bad);stroke-width:2;fill:none}
.l05a-main{fill:var(--ink);font:600 13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l05a-badt{fill:var(--ink)}
.l05a-dim{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l05a-badge{fill:var(--accent)}
.l05a-b-back{fill:var(--muted)}
.l05a-b-bad{fill:var(--bad)}
.l05a-b-good{fill:var(--good)}
.l05a-bt{fill:var(--on-accent);font:700 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l05a-note{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l05a-note-good{fill:var(--good-bg);stroke:var(--good);stroke-width:1.5}
.l05a-note-bad{fill:var(--bad-bg);stroke:var(--bad);stroke-width:1.5}
.l05a-nt{fill:var(--ink);font:500 12.5px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l05a-nest{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l05a-row{fill:var(--raised);stroke:var(--border-strong);stroke-width:1}
.l05a-ttlL{fill:var(--ink);font:600 14px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l05a-subL{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l05a-dimL{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l05a-dimR{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:end}
.l05a-conn{stroke:var(--accent);stroke-width:1.5;fill:none}
.l05a-edge{stroke:var(--border-strong);stroke-width:1.75;fill:none}
.l05a-hl{fill:none;stroke:var(--accent);stroke-width:3}
.l05a-hle{stroke:var(--accent);stroke-width:3;fill:none}
.l05a-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:24s;animation-timing-function:linear;animation-iteration-count:infinite}
.l05a-pk.l05a-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.l05a-pk.l05a-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.l05a-wrap{margin:20px 0}
@media (min-width:801px){.l05a-wrap{margin-left:-44px;margin-right:-44px}}
.l05a-g rect,.l05a-g line,.l05a-g path:not(.l05a-gl){opacity:.5;animation-duration:24s;animation-timing-function:linear;animation-iteration-count:infinite}
.l05a-h{opacity:0;animation-duration:24s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.l05a-flow:hover .l05a-g rect,svg.l05a-flow:hover .l05a-g line,svg.l05a-flow:hover .l05a-g path:not(.l05a-gl),svg.l05a-flow:hover .l05a-pk,svg.l05a-flow:hover .l05a-h{animation-play-state:paused}
.l05a-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.l05a-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.l05a-btn:hover{background:var(--hover)}
.l05a-cb:focus-visible + .l05a-btn{outline:2px solid var(--accent);outline-offset:2px}
.l05a-cb:checked + .l05a-btn .l05a-off,.l05a-cb:not(:checked) + .l05a-btn .l05a-on{display:none}
.l05a-cb:checked ~ .l05a-box .l05a-g rect,.l05a-cb:checked ~ .l05a-box .l05a-g line,.l05a-cb:checked ~ .l05a-box .l05a-g path:not(.l05a-gl),.l05a-cb:checked ~ .l05a-box .l05a-pk,.l05a-cb:checked ~ .l05a-box .l05a-h{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.l05a-g rect,.l05a-g line,.l05a-g path:not(.l05a-gl){animation:none;opacity:1}.l05a-pk{animation:none;display:none}.l05a-h{animation:none;opacity:0}.l05a-btn{display:none}}
@keyframes l05a-g0{0%{opacity:1}20%{opacity:1}20.01%,100%{opacity:.5}}
@keyframes l05a-h0{0%{opacity:1}20%{opacity:1}20.01%,100%{opacity:0}}
.l05a-g0 rect,.l05a-g0 line,.l05a-g0 path:not(.l05a-gl){animation-name:l05a-g0}.l05a-h0{animation-name:l05a-h0}
@keyframes l05a-g1{0%,19.99%{opacity:.5}20%{opacity:1}40%{opacity:1}40.01%,100%{opacity:.5}}
@keyframes l05a-h1{0%,19.99%{opacity:0}20%{opacity:1}40%{opacity:1}40.01%,100%{opacity:0}}
.l05a-g1 rect,.l05a-g1 line,.l05a-g1 path:not(.l05a-gl){animation-name:l05a-g1}.l05a-h1{animation-name:l05a-h1}
@keyframes l05a-g2{0%,39.99%{opacity:.5}40%{opacity:1}60%{opacity:1}60.01%,100%{opacity:.5}}
@keyframes l05a-h2{0%,39.99%{opacity:0}40%{opacity:1}60%{opacity:1}60.01%,100%{opacity:0}}
.l05a-g2 rect,.l05a-g2 line,.l05a-g2 path:not(.l05a-gl){animation-name:l05a-g2}.l05a-h2{animation-name:l05a-h2}
@keyframes l05a-g3{0%,59.99%{opacity:.5}60%{opacity:1}80%{opacity:1}80.01%,100%{opacity:.5}}
@keyframes l05a-h3{0%,59.99%{opacity:0}60%{opacity:1}80%{opacity:1}80.01%,100%{opacity:0}}
.l05a-g3 rect,.l05a-g3 line,.l05a-g3 path:not(.l05a-gl){animation-name:l05a-g3}.l05a-h3{animation-name:l05a-h3}
@keyframes l05a-g4{0%,79.99%{opacity:.5}80%{opacity:1}100%{opacity:1}100.01%,100%{opacity:.5}}
@keyframes l05a-h4{0%,79.99%{opacity:0}80%{opacity:1}100%{opacity:1}100.01%,100%{opacity:0}}
.l05a-g4 rect,.l05a-g4 line,.l05a-g4 path:not(.l05a-gl){animation-name:l05a-g4}.l05a-h4{animation-name:l05a-h4}
</style>
<defs>
<marker id="l05a-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="l05a-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="l05a-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<rect class="l05a-box" x="14" y="16" width="440" height="378" rx="9"/><text class="l05a-ttlL" x="28" y="37">Identifying one user</text><text class="l05a-subL" x="28" y="54">provisioning side and sign-in side</text>
<rect class="l05a-nest" x="26" y="62" width="416" height="212" rx="9"/><text class="l05a-ttlL" x="40" y="83">User resource</text><text class="l05a-subL" x="40" y="100">at /Users</text>
<rect class="l05a-nest" x="38" y="108" width="392" height="46" rx="9"/><text class="l05a-ttlL" x="52" y="129">id</text><text class="l05a-subL" x="52" y="146">issued by the server</text>
<rect class="l05a-nest" x="38" y="162" width="392" height="46" rx="9"/><text class="l05a-ttlL" x="52" y="183">userName</text><text class="l05a-subL" x="52" y="200">required</text>
<rect class="l05a-nest" x="38" y="216" width="392" height="46" rx="9"/><text class="l05a-ttlL" x="52" y="237">externalId</text><text class="l05a-subL" x="52" y="254">issued by the client</text>
<rect class="l05a-nest" x="26" y="282" width="416" height="46" rx="9"/><text class="l05a-ttlL" x="40" y="303">Match attribute</text><text class="l05a-subL" x="40" y="320">userName or externalId</text>
<rect class="l05a-nest" x="26" y="336" width="416" height="46" rx="9"/><text class="l05a-ttlL" x="40" y="357">SSO account key</text><text class="l05a-subL" x="40" y="374">a separate thing</text>
<g class="l05a-g l05a-g0">
<path class="l05a-conn" d="M430,125 L462,125 L462,125 L470,125" marker-end="url(#l05a-m-front)"/>
<rect class="l05a-note" x="484" y="101" width="262" height="48" rx="8"/>
<text class="l05a-nt" x="615" y="122">Stable and never reassigned;</text>
<text class="l05a-nt" x="615" y="139">the client must not set it</text>
<circle class="l05a-badge l05a-b-front" cx="484" cy="125" r="12"/><text class="l05a-bt" x="484" y="129.5">1</text>
</g>
<g class="l05a-g l05a-g1">
<path class="l05a-conn" d="M430,179 L466,179 L466,183 L470,183" marker-end="url(#l05a-m-front)"/>
<rect class="l05a-note" x="484" y="159" width="262" height="48" rx="8"/>
<text class="l05a-nt" x="615" y="180">Unique across the server's users,</text>
<text class="l05a-nt" x="615" y="197">case-insensitive</text>
<circle class="l05a-badge l05a-b-front" cx="484" cy="183" r="12"/><text class="l05a-bt" x="484" y="187.5">2</text>
</g>
<g class="l05a-g l05a-g2">
<path class="l05a-conn" d="M430,233 L470,233 L470,241 L470,241" marker-end="url(#l05a-m-front)"/>
<rect class="l05a-note" x="484" y="217" width="262" height="48" rx="8"/>
<text class="l05a-nt" x="615" y="238">The server does not enforce</text>
<text class="l05a-nt" x="615" y="255">uniqueness</text>
<circle class="l05a-badge l05a-b-front" cx="484" cy="241" r="12"/><text class="l05a-bt" x="484" y="245.5">3</text>
</g>
<g class="l05a-g l05a-g3">
<path class="l05a-conn" d="M442,299 L474,299 L474,308 L470,308" marker-end="url(#l05a-m-front)"/>
<rect class="l05a-note" x="484" y="275" width="262" height="65" rx="8"/>
<text class="l05a-nt" x="615" y="296">Mapping is your lever. Okta: Profile</text>
<text class="l05a-nt" x="615" y="313">Editor maps attributes. Entra: Match</text>
<text class="l05a-nt" x="615" y="330">objects using this attribute</text>
<circle class="l05a-badge l05a-b-front" cx="484" cy="308" r="12"/><text class="l05a-bt" x="484" y="312.0">4</text>
</g>
<g class="l05a-g l05a-g4">
<path class="l05a-conn" d="M442,353 L462,353 L462,391 L470,391" marker-end="url(#l05a-m-front)"/>
<rect class="l05a-note-good" x="484" y="350" width="262" height="82" rx="8"/>
<text class="l05a-nt" x="615" y="371">SAML: persistent NameID. OIDC: iss</text>
<text class="l05a-nt" x="615" y="388">plus sub. Entra: tid plus oid.</text>
<text class="l05a-nt" x="615" y="405">Link it to the account explicitly,</text>
<text class="l05a-nt" x="615" y="422">never on the email claim</text>
<circle class="l05a-badge l05a-b-good" cx="484" cy="391" r="12"/><text class="l05a-bt" x="484" y="395.5">5</text>
</g>
<g class="l05a-h l05a-h0">
<rect class="l05a-hl" x="38" y="108" width="392" height="46" rx="9"/>
</g>
<g class="l05a-h l05a-h1">
<rect class="l05a-hl" x="38" y="162" width="392" height="46" rx="9"/>
</g>
<g class="l05a-h l05a-h2">
<rect class="l05a-hl" x="38" y="216" width="392" height="46" rx="9"/>
</g>
<g class="l05a-h l05a-h3">
<rect class="l05a-hl" x="26" y="282" width="416" height="46" rx="9"/>
</g>
<g class="l05a-h l05a-h4">
<rect class="l05a-hl" x="26" y="336" width="416" height="46" rx="9"/>
</g>
<rect class="l05a-note" x="40" y="458" width="22" height="16" rx="4"/>
<text class="l05a-dim" x="70" y="470" style="text-anchor:start">SCIM side</text>
<rect class="l05a-note-good" x="161" y="458" width="22" height="16" rx="4"/>
<text class="l05a-dim" x="191" y="470" style="text-anchor:start">what your app must do</text>
</svg>
</div>
</div>
<!-- /diagram:scim-identifiers -->

The five numbered notes run top to bottom: the three identifiers on the User resource, then the match attribute, where mapping is your lever, then the SSO account key. The match attribute and the SSO key are separate things, and the app must link them explicitly.

## The life of an account

Okta's flow is below; Entra's is close. `{id}` is the server-issued id.

<!-- diagram:scim-protocol -->
<div class="sc-wrap" style="position:relative">
<input type="checkbox" id="sc-pause" class="sc-cb" /><label for="sc-pause" class="sc-btn"><span class="sc-off">Pause animation</span><span class="sc-on">Play animation</span></label>
<div class="sc-box" style="overflow-x:auto">
<svg class="sc-flow" viewBox="0 0 760 824" role="img" aria-labelledby="sc-t sc-d" style="width:760px;max-width:100%;min-width:699px;height:auto;display:block;margin:0 auto">
<title id="sc-t">SCIM lifecycle: create, group change, deactivate, delete</title>
<desc id="sc-d">Eight steps between an identity provider acting as SCIM client and your app acting as SCIM server, with a browser session opened earlier as a third lane. Step 1: on assignment Okta runs GET /Users with a filter on userName, and with no match sends POST /Users with userName, emails and active true. Step 2: the server answers 201 Created with the id, and the IdP keeps it. Step 3: for groups, PATCH /Groups/{id}, for example with a remove members and an add members in one request; Wizard apps send a PUT of the whole group. Step 4, leaver: active false by PATCH for OIN apps and by PUT for Wizard apps. Step 5, a failure mode: the server saves active false but the browser session opened earlier still works. Step 6: none of the operations in RFC 7644 ends a session or revokes a token, so your app must do it when it sees active false. Step 7: by default Entra sends DELETE /Users/{id} on a hard delete at the source and Okta never sends DELETE for users. Step 8: after DELETE the server must return 404 for that id. The diagram highlights each step in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
<style>
svg.sc-flow{--ink:light-dark(#000000,#ffffff)}
.sc-box{fill:var(--panel);stroke:var(--border-strong);stroke-width:1.5}
.sc-hot{fill:var(--panel);stroke:var(--accent);stroke-width:2.5}
.sc-ttl{fill:var(--ink);font:600 15px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.sc-sub{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.sc-life{stroke:var(--border-strong);stroke-width:1.5;stroke-dasharray:4 5}
.sc-front{stroke:var(--accent);stroke-width:2;fill:none}
.sc-back{stroke:var(--muted);stroke-width:2;stroke-dasharray:7 5;fill:none}
.sc-bad{stroke:var(--bad);stroke-width:2;fill:none}
.sc-main{fill:var(--ink);font:600 13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.sc-badt{fill:var(--ink)}
.sc-dim{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.sc-badge{fill:var(--accent)}
.sc-b-back{fill:var(--muted)}
.sc-b-bad{fill:var(--bad)}
.sc-b-good{fill:var(--good)}
.sc-bt{fill:var(--on-accent);font:700 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.sc-note{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.sc-note-good{fill:var(--good-bg);stroke:var(--good);stroke-width:1.5}
.sc-note-bad{fill:var(--bad-bg);stroke:var(--bad);stroke-width:1.5}
.sc-nt{fill:var(--ink);font:500 12.5px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.sc-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:46s;animation-timing-function:linear;animation-iteration-count:infinite}
.sc-pk.sc-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.sc-pk.sc-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.sc-wrap{margin:20px 0}
@media (min-width:801px){.sc-wrap{margin-left:-44px;margin-right:-44px}}
.sc-g rect,.sc-g line,.sc-g path:not(.sc-gl){opacity:.5;animation-duration:46s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.sc-flow:hover .sc-g rect,svg.sc-flow:hover .sc-g line,svg.sc-flow:hover .sc-g path:not(.sc-gl),svg.sc-flow:hover .sc-pk{animation-play-state:paused}
.sc-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.sc-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.sc-btn:hover{background:var(--hover)}
.sc-cb:focus-visible + .sc-btn{outline:2px solid var(--accent);outline-offset:2px}
.sc-cb:checked + .sc-btn .sc-off,.sc-cb:not(:checked) + .sc-btn .sc-on{display:none}
.sc-cb:checked ~ .sc-box .sc-g rect,.sc-cb:checked ~ .sc-box .sc-g line,.sc-cb:checked ~ .sc-box .sc-g path:not(.sc-gl),.sc-cb:checked ~ .sc-box .sc-pk{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.sc-g rect,.sc-g line,.sc-g path:not(.sc-gl){animation:none;opacity:1}.sc-pk{animation:none;display:none}.sc-btn{display:none}}
@keyframes sc-g0{0%{opacity:1}13.043%{opacity:1}13.053%,100%{opacity:.5}}
@keyframes sc-p0{0%,-0.01%{opacity:0;transform:translateX(0)}0%{opacity:1;transform:translateX(0)}10.435%{opacity:1;transform:translateX(236px)}13.043%{opacity:1;transform:translateX(236px)}13.053%,100%{opacity:0;transform:translateX(236px)}}
.sc-g0 rect,.sc-g0 line,.sc-g0 path:not(.sc-gl){animation-name:sc-g0}.sc-p0{animation-name:sc-p0}
@keyframes sc-g1{0%,13.033%{opacity:.5}13.043%{opacity:1}26.087%{opacity:1}26.097%,100%{opacity:.5}}
@keyframes sc-p1{0%,13.033%{opacity:0;transform:translateX(0)}13.043%{opacity:1;transform:translateX(0)}23.478%{opacity:1;transform:translateX(-236px)}26.087%{opacity:1;transform:translateX(-236px)}26.097%,100%{opacity:0;transform:translateX(-236px)}}
.sc-g1 rect,.sc-g1 line,.sc-g1 path:not(.sc-gl){animation-name:sc-g1}.sc-p1{animation-name:sc-p1}
@keyframes sc-g2{0%,26.077%{opacity:.5}26.087%{opacity:1}39.13%{opacity:1}39.14%,100%{opacity:.5}}
@keyframes sc-p2{0%,26.077%{opacity:0;transform:translateX(0)}26.087%{opacity:1;transform:translateX(0)}36.522%{opacity:1;transform:translateX(236px)}39.13%{opacity:1;transform:translateX(236px)}39.14%,100%{opacity:0;transform:translateX(236px)}}
.sc-g2 rect,.sc-g2 line,.sc-g2 path:not(.sc-gl){animation-name:sc-g2}.sc-p2{animation-name:sc-p2}
@keyframes sc-g3{0%,39.12%{opacity:.5}39.13%{opacity:1}52.174%{opacity:1}52.184%,100%{opacity:.5}}
@keyframes sc-p3{0%,39.12%{opacity:0;transform:translateX(0)}39.13%{opacity:1;transform:translateX(0)}49.565%{opacity:1;transform:translateX(236px)}52.174%{opacity:1;transform:translateX(236px)}52.184%,100%{opacity:0;transform:translateX(236px)}}
.sc-g3 rect,.sc-g3 line,.sc-g3 path:not(.sc-gl){animation-name:sc-g3}.sc-p3{animation-name:sc-p3}
@keyframes sc-g4{0%,52.164%{opacity:.5}52.174%{opacity:1}65.217%{opacity:1}65.227%,100%{opacity:.5}}
@keyframes sc-p4{0%,52.164%{opacity:0;transform:translateX(0)}52.174%{opacity:1;transform:translateX(0)}62.609%{opacity:1;transform:translateX(-236px)}65.217%{opacity:1;transform:translateX(-236px)}65.227%,100%{opacity:0;transform:translateX(-236px)}}
.sc-g4 rect,.sc-g4 line,.sc-g4 path:not(.sc-gl){animation-name:sc-g4}.sc-p4{animation-name:sc-p4}
@keyframes sc-g5{0%,65.207%{opacity:.5}65.217%{opacity:1}73.913%{opacity:1}73.923%,100%{opacity:.5}}
.sc-g5 rect,.sc-g5 line,.sc-g5 path:not(.sc-gl){animation-name:sc-g5}
@keyframes sc-g6{0%,73.903%{opacity:.5}73.913%{opacity:1}86.957%{opacity:1}86.967%,100%{opacity:.5}}
@keyframes sc-p6{0%,73.903%{opacity:0;transform:translateX(0)}73.913%{opacity:1;transform:translateX(0)}84.348%{opacity:1;transform:translateX(236px)}86.957%{opacity:1;transform:translateX(236px)}86.967%,100%{opacity:0;transform:translateX(236px)}}
.sc-g6 rect,.sc-g6 line,.sc-g6 path:not(.sc-gl){animation-name:sc-g6}.sc-p6{animation-name:sc-p6}
@keyframes sc-g7{0%,86.947%{opacity:.5}86.957%{opacity:1}100%{opacity:1}100.01%,100%{opacity:.5}}
@keyframes sc-p7{0%,86.947%{opacity:0;transform:translateX(0)}86.957%{opacity:1;transform:translateX(0)}97.391%{opacity:1;transform:translateX(-236px)}100%{opacity:1;transform:translateX(-236px)}100.01%,100%{opacity:0;transform:translateX(-236px)}}
.sc-g7 rect,.sc-g7 line,.sc-g7 path:not(.sc-gl){animation-name:sc-g7}.sc-p7{animation-name:sc-p7}
</style>
<defs>
<marker id="sc-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="sc-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="sc-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<line class="sc-life" x1="110" y1="72" x2="110" y2="772"/>
<line class="sc-life" x1="380" y1="72" x2="380" y2="772"/>
<line class="sc-life" x1="650" y1="72" x2="650" y2="772"/>
<rect class="sc-box" x="20" y="10" width="180" height="62" rx="10"/><text class="sc-ttl" x="110" y="36">Identity provider</text><text class="sc-sub" x="110" y="56">SCIM client (Okta, Entra)</text>
<rect class="sc-hot" x="290" y="10" width="180" height="62" rx="10"/><text class="sc-ttl" x="380" y="36">Your app</text><text class="sc-sub" x="380" y="56">SCIM server</text>
<rect class="sc-box" x="560" y="10" width="180" height="62" rx="10"/><text class="sc-ttl" x="650" y="36">User's browser</text><text class="sc-sub" x="650" y="56">session opened earlier</text>
<g class="sc-g sc-g0">
<text class="sc-main" x="245" y="108">GET /Users?filter=userName eq ...</text>
<text class="sc-dim" x="245" y="124">Okta looks the user up first</text>
<line class="sc-front" x1="124" y1="138" x2="366" y2="138" marker-end="url(#sc-m-front)"/>
<circle class="sc-badge sc-b-front" cx="110" cy="138" r="12"/><text class="sc-bt" x="110" y="142.5">1</text>
<text class="sc-main" x="245" y="178">POST /Users</text>
<text class="sc-dim" x="245" y="194">no match: userName, emails, active</text>
<line class="sc-front" x1="124" y1="208" x2="366" y2="208" marker-end="url(#sc-m-front)"/>
</g>
<g class="sc-g sc-g1">
<text class="sc-main" x="245" y="248">201 Created + id</text>
<text class="sc-dim" x="245" y="264">the IdP keeps the id</text>
<line class="sc-back" x1="366" y1="278" x2="124" y2="278" marker-end="url(#sc-m-back)"/>
<circle class="sc-badge sc-b-back" cx="380" cy="278" r="12"/><text class="sc-bt" x="380" y="282.5">2</text>
</g>
<g class="sc-g sc-g2">
<text class="sc-main" x="245" y="318">PATCH /Groups/{id}</text>
<text class="sc-dim" x="245" y="334">e.g. remove + add members (Wizard: PUT)</text>
<line class="sc-front" x1="124" y1="348" x2="366" y2="348" marker-end="url(#sc-m-front)"/>
<circle class="sc-badge sc-b-front" cx="110" cy="348" r="12"/><text class="sc-bt" x="110" y="352.5">3</text>
</g>
<g class="sc-g sc-g3">
<text class="sc-main" x="245" y="388">Leaver: active = false</text>
<text class="sc-dim" x="245" y="404">OIN apps: PATCH; Wizard apps: PUT</text>
<line class="sc-front" x1="124" y1="418" x2="366" y2="418" marker-end="url(#sc-m-front)"/>
<circle class="sc-badge sc-b-front" cx="110" cy="418" r="12"/><text class="sc-bt" x="110" y="422.5">4</text>
</g>
<g class="sc-g sc-g4">
<text class="sc-main sc-badt" x="515" y="458">request with the old session</text>
<text class="sc-dim" x="515" y="474">still works</text>
<line class="sc-bad" x1="636" y1="488" x2="394" y2="488" marker-end="url(#sc-m-bad)"/>
<circle class="sc-badge sc-b-bad" cx="650" cy="488" r="12"/><text class="sc-bt" x="650" y="492.5">5</text>
</g>
<g class="sc-g sc-g5">
<rect class="sc-note-good" x="243" y="522" width="274" height="48" rx="8"/>
<text class="sc-nt" x="380" y="543">no RFC 7644 operation ends a session:</text>
<text class="sc-nt" x="380" y="560">your app does it on active = false</text>
<circle class="sc-badge sc-b-good" cx="243" cy="546" r="12"/><text class="sc-bt" x="243" y="550.5">6</text>
</g>
<g class="sc-g sc-g6">
<text class="sc-main" x="245" y="604">DELETE /Users/{id}</text>
<text class="sc-dim" x="245" y="620">Entra: by default, on hard delete</text>
<text class="sc-dim" x="245" y="636">Okta: never</text>
<line class="sc-front" x1="124" y1="650" x2="366" y2="650" marker-end="url(#sc-m-front)"/>
<circle class="sc-badge sc-b-front" cx="110" cy="650" r="12"/><text class="sc-bt" x="110" y="654.5">7</text>
</g>
<g class="sc-g sc-g7">
<text class="sc-main" x="245" y="690">404 Not Found</text>
<text class="sc-dim" x="245" y="706">required for that id afterwards</text>
<line class="sc-back" x1="366" y1="720" x2="124" y2="720" marker-end="url(#sc-m-back)"/>
<circle class="sc-badge sc-b-back" cx="380" cy="720" r="12"/><text class="sc-bt" x="380" y="724.5">8</text>
</g>
<circle class="sc-pk sc-p0" cx="130" cy="208" r="5.5"/>
<circle class="sc-pk sc-p1 sc-pkback" cx="360" cy="278" r="5.5"/>
<circle class="sc-pk sc-p2" cx="130" cy="348" r="5.5"/>
<circle class="sc-pk sc-p3" cx="130" cy="418" r="5.5"/>
<circle class="sc-pk sc-p4 sc-pkbad" cx="630" cy="488" r="5.5"/>
<circle class="sc-pk sc-p6" cx="130" cy="650" r="5.5"/>
<circle class="sc-pk sc-p7 sc-pkback" cx="360" cy="720" r="5.5"/>
<line class="sc-front" x1="40" y1="800" x2="70" y2="800"/>
<text class="sc-dim" x="78" y="804" style="text-anchor:start">request</text>
<line class="sc-back" x1="156" y1="800" x2="186" y2="800"/>
<text class="sc-dim" x="194" y="804" style="text-anchor:start">response</text>
<line class="sc-bad" x1="279" y1="800" x2="309" y2="800"/>
<text class="sc-dim" x="317" y="804" style="text-anchor:start">failure mode</text>
<rect class="sc-note-good" x="427" y="792" width="22" height="16" rx="4"/>
<text class="sc-dim" x="457" y="804" style="text-anchor:start">what your app must do</text>
</svg>
</div>
</div>
<!-- /diagram:scim-protocol -->

The numbers 1 to 8 match the list below. Step 1 is two requests, the lookup and then the create. Step 5 is the failure mode.

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

<!-- diagram:scim-account-states -->
<div class="l05b-wrap" style="position:relative">
<input type="checkbox" id="l05b-pause" class="l05b-cb" /><label for="l05b-pause" class="l05b-btn"><span class="l05b-off">Pause animation</span><span class="l05b-on">Play animation</span></label>
<div class="l05b-box" style="overflow-x:auto">
<svg class="l05b-flow" viewBox="0 0 760 227" role="img" aria-labelledby="l05b-t l05b-d" style="width:760px;max-width:100%;min-width:699px;height:auto;display:block;margin:0 auto">
<title id="l05b-t">The app-side account: active, deactivated, deleted</title>
<desc id="l05b-d">Three states of the account in the app, not the user in the IdP. Active: active is true, which typically means the user can sign in. Deactivated: active is false, which typically means suspended; Okta flips it back to true on reprovisioning, and Entra expects an inactive user to still be returned. Deleted: the provider may keep the data but must return 404 for the old id and omit it from queries; Okta sends no DELETE for users, and Entra by default sends DELETE only when the user is hard-deleted. Setting active false moves the account to deactivated, reprovisioning returns it to active, and DELETE moves it to deleted. The diagram highlights each stage in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
<style>
svg.l05b-flow{--ink:light-dark(#000000,#ffffff)}
.l05b-box{fill:var(--panel);stroke:var(--border-strong);stroke-width:1.5}
.l05b-hot{fill:var(--panel);stroke:var(--accent);stroke-width:2.5}
.l05b-ttl{fill:var(--ink);font:600 15px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l05b-sub{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l05b-life{stroke:var(--border-strong);stroke-width:1.5;stroke-dasharray:4 5}
.l05b-front{stroke:var(--accent);stroke-width:2;fill:none}
.l05b-back{stroke:var(--muted);stroke-width:2;stroke-dasharray:7 5;fill:none}
.l05b-bad{stroke:var(--bad);stroke-width:2;fill:none}
.l05b-main{fill:var(--ink);font:600 13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l05b-badt{fill:var(--ink)}
.l05b-dim{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l05b-badge{fill:var(--accent)}
.l05b-b-back{fill:var(--muted)}
.l05b-b-bad{fill:var(--bad)}
.l05b-b-good{fill:var(--good)}
.l05b-bt{fill:var(--on-accent);font:700 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l05b-note{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l05b-note-good{fill:var(--good-bg);stroke:var(--good);stroke-width:1.5}
.l05b-note-bad{fill:var(--bad-bg);stroke:var(--bad);stroke-width:1.5}
.l05b-nt{fill:var(--ink);font:500 12.5px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l05b-nest{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l05b-row{fill:var(--raised);stroke:var(--border-strong);stroke-width:1}
.l05b-ttlL{fill:var(--ink);font:600 14px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l05b-subL{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l05b-dimL{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l05b-dimR{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:end}
.l05b-conn{stroke:var(--accent);stroke-width:1.5;fill:none}
.l05b-edge{stroke:var(--border-strong);stroke-width:1.75;fill:none}
.l05b-hl{fill:none;stroke:var(--accent);stroke-width:3}
.l05b-hle{stroke:var(--accent);stroke-width:3;fill:none}
.l05b-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:16s;animation-timing-function:linear;animation-iteration-count:infinite}
.l05b-pk.l05b-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.l05b-pk.l05b-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.l05b-wrap{margin:20px 0}
@media (min-width:801px){.l05b-wrap{margin-left:-44px;margin-right:-44px}}
.l05b-g rect,.l05b-g line,.l05b-g path:not(.l05b-gl){opacity:.5;animation-duration:16s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.l05b-flow:hover .l05b-g rect,svg.l05b-flow:hover .l05b-g line,svg.l05b-flow:hover .l05b-g path:not(.l05b-gl),svg.l05b-flow:hover .l05b-pk{animation-play-state:paused}
.l05b-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.l05b-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.l05b-btn:hover{background:var(--hover)}
.l05b-cb:focus-visible + .l05b-btn{outline:2px solid var(--accent);outline-offset:2px}
.l05b-cb:checked + .l05b-btn .l05b-off,.l05b-cb:not(:checked) + .l05b-btn .l05b-on{display:none}
.l05b-cb:checked ~ .l05b-box .l05b-g rect,.l05b-cb:checked ~ .l05b-box .l05b-g line,.l05b-cb:checked ~ .l05b-box .l05b-g path:not(.l05b-gl),.l05b-cb:checked ~ .l05b-box .l05b-pk{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.l05b-g rect,.l05b-g line,.l05b-g path:not(.l05b-gl){animation:none;opacity:1}.l05b-pk{animation:none;display:none}.l05b-btn{display:none}}
@keyframes l05b-g0{0%{opacity:1}37.5%{opacity:1}37.51%,100%{opacity:.5}}
@keyframes l05b-p0{0%,-0.01%{opacity:0;transform:translateX(0)}0%{opacity:1;transform:translateX(0)}30%{opacity:1;transform:translateX(88px)}37.5%{opacity:1;transform:translateX(88px)}37.51%,100%{opacity:0;transform:translateX(88px)}}
.l05b-g0 rect,.l05b-g0 line,.l05b-g0 path:not(.l05b-gl){animation-name:l05b-g0}.l05b-p0{animation-name:l05b-p0}
@keyframes l05b-g1{0%,37.49%{opacity:.5}37.5%{opacity:1}75%{opacity:1}75.01%,100%{opacity:.5}}
@keyframes l05b-p1{0%,37.49%{opacity:0;transform:translateX(0)}37.5%{opacity:1;transform:translateX(0)}67.5%{opacity:1;transform:translateX(88px)}75%{opacity:1;transform:translateX(88px)}75.01%,100%{opacity:0;transform:translateX(88px)}}
.l05b-g1 rect,.l05b-g1 line,.l05b-g1 path:not(.l05b-gl){animation-name:l05b-g1}.l05b-p1{animation-name:l05b-p1}
@keyframes l05b-g2{0%,74.99%{opacity:.5}75%{opacity:1}100%{opacity:1}100.01%,100%{opacity:.5}}
.l05b-g2 rect,.l05b-g2 line,.l05b-g2 path:not(.l05b-gl){animation-name:l05b-g2}
</style>
<defs>
<marker id="l05b-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="l05b-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="l05b-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<g class="l05b-g l05b-g0">
<rect class="l05b-note-good" x="14" y="40" width="171" height="127" rx="10"/>
<text class="l05b-ttl" x="99" y="67">Active</text>
<text class="l05b-sub" x="99" y="87">active = true</text>
<text class="l05b-nt" x="99" y="114">typically: the user</text>
<text class="l05b-nt" x="99" y="131">can sign in</text>
<text class="l05b-main" x="240" y="64">active = false</text>
<line class="l05b-front" x1="193" y1="70" x2="287" y2="70" marker-end="url(#l05b-m-front)"/>
<text class="l05b-main" x="240" y="112">Okta: set true</text>
<text class="l05b-dim" x="240" y="128">on reprovision</text>
<line class="l05b-back" x1="287" y1="94" x2="193" y2="94" marker-end="url(#l05b-m-back)"/>
</g>
<g class="l05b-g l05b-g1">
<rect class="l05b-box" x="295" y="40" width="171" height="127" rx="10"/>
<text class="l05b-ttl" x="380" y="67">Deactivated</text>
<text class="l05b-sub" x="380" y="87">active = false</text>
<text class="l05b-nt" x="380" y="114">typically: suspended</text>
<text class="l05b-nt" x="380" y="131">Entra: still returned</text>
<text class="l05b-main" x="520" y="48">Entra default:</text>
<text class="l05b-dim" x="520" y="64">hard delete</text>
<line class="l05b-front" x1="473" y1="70" x2="567" y2="70" marker-end="url(#l05b-m-front)"/>
</g>
<g class="l05b-g l05b-g2">
<rect class="l05b-box" x="575" y="40" width="171" height="127" rx="10"/>
<text class="l05b-ttl" x="661" y="67">Deleted</text>
<text class="l05b-sub" x="661" y="87">DELETE</text>
<text class="l05b-nt" x="661" y="114">must return 404</text>
<text class="l05b-nt" x="661" y="131">may keep the data</text>
<text class="l05b-nt" x="661" y="148">Okta: no DELETE sent</text>
</g>
<circle class="l05b-pk l05b-p0" cx="199" cy="70" r="5.5"/>
<circle class="l05b-pk l05b-p1" cx="479" cy="70" r="5.5"/>
<line class="l05b-front" x1="40" y1="203" x2="70" y2="203"/>
<text class="l05b-dim" x="78" y="207" style="text-anchor:start">step forward</text>
<line class="l05b-back" x1="188" y1="203" x2="218" y2="203"/>
<text class="l05b-dim" x="226" y="207" style="text-anchor:start">step back</text>
<rect class="l05b-note-good" x="317" y="195" width="22" height="16" rx="4"/>
<text class="l05b-dim" x="347" y="207" style="text-anchor:start">can sign in</text>
</svg>
</div>
</div>
<!-- /diagram:scim-account-states -->

This is the account in the app, not the user in the IdP. Look at what each IdP sends to move it between states: `active=false` goes to the middle state, and by default Entra sends a DELETE for the right-hand state only on a hard delete, while Okta never sends DELETE for users.

<!-- diagram:scim-group-push -->
<div class="l05c-wrap" style="position:relative">
<input type="checkbox" id="l05c-pause" class="l05c-cb" /><label for="l05c-pause" class="l05c-btn"><span class="l05c-off">Pause animation</span><span class="l05c-on">Play animation</span></label>
<div class="l05c-box" style="overflow-x:auto">
<svg class="l05c-flow" viewBox="0 0 760 624" role="img" aria-labelledby="l05c-t l05c-d" style="width:760px;max-width:100%;min-width:699px;height:auto;display:block;margin:0 auto">
<title id="l05c-t">Okta group membership: the three conditions and the shared-group trap</title>
<desc id="l05c-d">A chain of checks for an Okta group change that does not arrive. Okta group membership needs all three: the user is in the Okta group, is assigned to the app, and the group is pushed. If the user is not in the group, not assigned, or the group is not pushed, no membership change is sent. If all three hold but the same group is used for both assignment and Group Push, that is not supported, so make a separate push group. If all three hold and the groups are separate, Okta can send the change. The diagram highlights each path in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
<style>
svg.l05c-flow{--ink:light-dark(#000000,#ffffff)}
.l05c-box{fill:var(--panel);stroke:var(--border-strong);stroke-width:1.5}
.l05c-hot{fill:var(--panel);stroke:var(--accent);stroke-width:2.5}
.l05c-ttl{fill:var(--ink);font:600 15px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l05c-sub{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l05c-life{stroke:var(--border-strong);stroke-width:1.5;stroke-dasharray:4 5}
.l05c-front{stroke:var(--accent);stroke-width:2;fill:none}
.l05c-back{stroke:var(--muted);stroke-width:2;stroke-dasharray:7 5;fill:none}
.l05c-bad{stroke:var(--bad);stroke-width:2;fill:none}
.l05c-main{fill:var(--ink);font:600 13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l05c-badt{fill:var(--ink)}
.l05c-dim{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l05c-badge{fill:var(--accent)}
.l05c-b-back{fill:var(--muted)}
.l05c-b-bad{fill:var(--bad)}
.l05c-b-good{fill:var(--good)}
.l05c-bt{fill:var(--on-accent);font:700 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l05c-note{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l05c-note-good{fill:var(--good-bg);stroke:var(--good);stroke-width:1.5}
.l05c-note-bad{fill:var(--bad-bg);stroke:var(--bad);stroke-width:1.5}
.l05c-nt{fill:var(--ink);font:500 12.5px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l05c-nest{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l05c-row{fill:var(--raised);stroke:var(--border-strong);stroke-width:1}
.l05c-ttlL{fill:var(--ink);font:600 14px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l05c-subL{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l05c-dimL{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l05c-dimR{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:end}
.l05c-conn{stroke:var(--accent);stroke-width:1.5;fill:none}
.l05c-edge{stroke:var(--border-strong);stroke-width:1.75;fill:none}
.l05c-hl{fill:none;stroke:var(--accent);stroke-width:3}
.l05c-hle{stroke:var(--accent);stroke-width:3;fill:none}
.l05c-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:20s;animation-timing-function:linear;animation-iteration-count:infinite}
.l05c-pk.l05c-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.l05c-pk.l05c-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.l05c-wrap{margin:20px 0}
@media (min-width:801px){.l05c-wrap{margin-left:-44px;margin-right:-44px}}
.l05c-g rect,.l05c-g line,.l05c-g path:not(.l05c-gl){opacity:.5;animation-duration:20s;animation-timing-function:linear;animation-iteration-count:infinite}
.l05c-h{opacity:0;animation-duration:20s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.l05c-flow:hover .l05c-g rect,svg.l05c-flow:hover .l05c-g line,svg.l05c-flow:hover .l05c-g path:not(.l05c-gl),svg.l05c-flow:hover .l05c-pk,svg.l05c-flow:hover .l05c-h{animation-play-state:paused}
.l05c-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.l05c-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.l05c-btn:hover{background:var(--hover)}
.l05c-cb:focus-visible + .l05c-btn{outline:2px solid var(--accent);outline-offset:2px}
.l05c-cb:checked + .l05c-btn .l05c-off,.l05c-cb:not(:checked) + .l05c-btn .l05c-on{display:none}
.l05c-cb:checked ~ .l05c-box .l05c-g rect,.l05c-cb:checked ~ .l05c-box .l05c-g line,.l05c-cb:checked ~ .l05c-box .l05c-g path:not(.l05c-gl),.l05c-cb:checked ~ .l05c-box .l05c-pk,.l05c-cb:checked ~ .l05c-box .l05c-h{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.l05c-g rect,.l05c-g line,.l05c-g path:not(.l05c-gl){animation:none;opacity:1}.l05c-pk{animation:none;display:none}.l05c-h{animation:none;opacity:0}.l05c-btn{display:none}}
@keyframes l05c-h0{0%{opacity:1}20%{opacity:1}20.01%,100%{opacity:0}}
.l05c-h0{animation-name:l05c-h0}
@keyframes l05c-h1{0%,19.99%{opacity:0}20%{opacity:1}40%{opacity:1}40.01%,100%{opacity:0}}
.l05c-h1{animation-name:l05c-h1}
@keyframes l05c-h2{0%,39.99%{opacity:0}40%{opacity:1}60%{opacity:1}60.01%,100%{opacity:0}}
.l05c-h2{animation-name:l05c-h2}
@keyframes l05c-h3{0%,59.99%{opacity:0}60%{opacity:1}80%{opacity:1}80.01%,100%{opacity:0}}
.l05c-h3{animation-name:l05c-h3}
@keyframes l05c-h4{0%,79.99%{opacity:0}80%{opacity:1}100%{opacity:1}100.01%,100%{opacity:0}}
.l05c-h4{animation-name:l05c-h4}
</style>
<defs>
<marker id="l05c-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="l05c-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="l05c-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<path class="l05c-edge" d="M380,72 L380,101 L117,101 L117,127" marker-end="url(#l05c-m-front)"/>
<text class="l05c-dimL" x="124" y="117">no</text>
<path class="l05c-edge" d="M380,72 L380,101 L443,101 L443,127" marker-end="url(#l05c-m-front)"/>
<text class="l05c-dimL" x="450" y="117">yes</text>
<path class="l05c-edge" d="M443,178 L443,207 L243,207 L243,250" marker-end="url(#l05c-m-front)"/>
<text class="l05c-dimL" x="250" y="240">no</text>
<path class="l05c-edge" d="M443,178 L443,207 L506,207 L506,250" marker-end="url(#l05c-m-front)"/>
<text class="l05c-dimL" x="513" y="240">yes</text>
<path class="l05c-edge" d="M506,284 L506,313 L369,313 L369,373" marker-end="url(#l05c-m-front)"/>
<text class="l05c-dimL" x="376" y="363">no</text>
<path class="l05c-edge" d="M506,284 L506,313 L569,313 L569,373" marker-end="url(#l05c-m-front)"/>
<text class="l05c-dimL" x="576" y="363">yes</text>
<path class="l05c-edge" d="M569,441 L569,470 L504,470 L504,496" marker-end="url(#l05c-m-front)"/>
<text class="l05c-dimL" x="511" y="486">yes</text>
<path class="l05c-edge" d="M569,441 L569,470 L641,470 L641,496" marker-end="url(#l05c-m-front)"/>
<text class="l05c-dimL" x="648" y="486">no</text>
<rect class="l05c-note-bad" x="62" y="130" width="110" height="65" rx="8"/><text class="l05c-nt" x="117" y="151">Not sent:</text><text class="l05c-nt" x="117" y="168">user not in</text><text class="l05c-nt" x="117" y="185">the group</text>
<rect class="l05c-note-bad" x="188" y="253" width="110" height="65" rx="8"/><text class="l05c-nt" x="243" y="274">Not sent:</text><text class="l05c-nt" x="243" y="291">user not</text><text class="l05c-nt" x="243" y="308">assigned</text>
<rect class="l05c-note-bad" x="314" y="376" width="110" height="65" rx="8"/><text class="l05c-nt" x="369" y="397">Not sent:</text><text class="l05c-nt" x="369" y="414">group not</text><text class="l05c-nt" x="369" y="431">pushed</text>
<rect class="l05c-note-bad" x="440" y="499" width="128" height="65" rx="8"/><text class="l05c-nt" x="504" y="520">Unsupported:</text><text class="l05c-nt" x="504" y="537">make a separate</text><text class="l05c-nt" x="504" y="554">push group</text>
<rect class="l05c-note-good" x="584" y="499" width="114" height="48" rx="8"/><text class="l05c-nt" x="641" y="520">Okta can send</text><text class="l05c-nt" x="641" y="537">the change</text>
<rect class="l05c-box" x="508" y="376" width="121" height="65" rx="8"/><text class="l05c-main" x="569" y="397">Same group for</text><text class="l05c-nt" x="569" y="414">assignment and</text><text class="l05c-nt" x="569" y="431">Group Push?</text>
<rect class="l05c-box" x="449" y="253" width="114" height="31" rx="8"/><text class="l05c-main" x="506" y="274">Group pushed?</text>
<rect class="l05c-box" x="386" y="130" width="114" height="48" rx="8"/><text class="l05c-main" x="443" y="151">User assigned</text><text class="l05c-nt" x="443" y="168">to the app?</text>
<rect class="l05c-box" x="325" y="24" width="110" height="48" rx="8"/><text class="l05c-main" x="380" y="45">User in the</text><text class="l05c-nt" x="380" y="62">Okta group?</text>
<g class="l05c-h l05c-h0">
<path class="l05c-hle" d="M380,72 L380,101 L117,101 L117,127" marker-end="url(#l05c-m-front)"/>
<rect class="l05c-hl" x="325" y="24" width="110" height="48" rx="8"/>
<rect class="l05c-hl" x="62" y="130" width="110" height="65" rx="8"/>
</g>
<g class="l05c-h l05c-h1">
<path class="l05c-hle" d="M380,72 L380,101 L443,101 L443,127" marker-end="url(#l05c-m-front)"/>
<path class="l05c-hle" d="M443,178 L443,207 L243,207 L243,250" marker-end="url(#l05c-m-front)"/>
<rect class="l05c-hl" x="325" y="24" width="110" height="48" rx="8"/>
<rect class="l05c-hl" x="386" y="130" width="114" height="48" rx="8"/>
<rect class="l05c-hl" x="188" y="253" width="110" height="65" rx="8"/>
</g>
<g class="l05c-h l05c-h2">
<path class="l05c-hle" d="M380,72 L380,101 L443,101 L443,127" marker-end="url(#l05c-m-front)"/>
<path class="l05c-hle" d="M443,178 L443,207 L506,207 L506,250" marker-end="url(#l05c-m-front)"/>
<path class="l05c-hle" d="M506,284 L506,313 L369,313 L369,373" marker-end="url(#l05c-m-front)"/>
<rect class="l05c-hl" x="325" y="24" width="110" height="48" rx="8"/>
<rect class="l05c-hl" x="386" y="130" width="114" height="48" rx="8"/>
<rect class="l05c-hl" x="449" y="253" width="114" height="31" rx="8"/>
<rect class="l05c-hl" x="314" y="376" width="110" height="65" rx="8"/>
</g>
<g class="l05c-h l05c-h3">
<path class="l05c-hle" d="M380,72 L380,101 L443,101 L443,127" marker-end="url(#l05c-m-front)"/>
<path class="l05c-hle" d="M443,178 L443,207 L506,207 L506,250" marker-end="url(#l05c-m-front)"/>
<path class="l05c-hle" d="M506,284 L506,313 L569,313 L569,373" marker-end="url(#l05c-m-front)"/>
<path class="l05c-hle" d="M569,441 L569,470 L504,470 L504,496" marker-end="url(#l05c-m-front)"/>
<rect class="l05c-hl" x="325" y="24" width="110" height="48" rx="8"/>
<rect class="l05c-hl" x="386" y="130" width="114" height="48" rx="8"/>
<rect class="l05c-hl" x="449" y="253" width="114" height="31" rx="8"/>
<rect class="l05c-hl" x="508" y="376" width="121" height="65" rx="8"/>
<rect class="l05c-hl" x="440" y="499" width="128" height="65" rx="8"/>
</g>
<g class="l05c-h l05c-h4">
<path class="l05c-hle" d="M380,72 L380,101 L443,101 L443,127" marker-end="url(#l05c-m-front)"/>
<path class="l05c-hle" d="M443,178 L443,207 L506,207 L506,250" marker-end="url(#l05c-m-front)"/>
<path class="l05c-hle" d="M506,284 L506,313 L569,313 L569,373" marker-end="url(#l05c-m-front)"/>
<path class="l05c-hle" d="M569,441 L569,470 L641,470 L641,496" marker-end="url(#l05c-m-front)"/>
<rect class="l05c-hl" x="325" y="24" width="110" height="48" rx="8"/>
<rect class="l05c-hl" x="386" y="130" width="114" height="48" rx="8"/>
<rect class="l05c-hl" x="449" y="253" width="114" height="31" rx="8"/>
<rect class="l05c-hl" x="508" y="376" width="121" height="65" rx="8"/>
<rect class="l05c-hl" x="584" y="499" width="114" height="48" rx="8"/>
</g>
<line class="l05c-front" x1="40" y1="600" x2="70" y2="600"/>
<text class="l05c-dim" x="78" y="604" style="text-anchor:start">the path being traced</text>
<rect class="l05c-note-good" x="246" y="592" width="22" height="16" rx="4"/>
<text class="l05c-dim" x="276" y="604" style="text-anchor:start">the change can be sent</text>
<rect class="l05c-note-bad" x="450" y="592" width="22" height="16" rx="4"/>
<text class="l05c-dim" x="480" y="604" style="text-anchor:start">nothing is sent</text>
</svg>
</div>
</div>
<!-- /diagram:scim-group-push -->

Walk the Okta checks from the top. Membership needs all three conditions, and even then using the same group for assignment and Group Push is unsupported, so the last check is the one that sends you to a separate push group.

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
