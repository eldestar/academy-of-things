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

<!-- diagram:scim-identifiers -->
<div class="l05a-wrap" style="position:relative">
<input type="checkbox" id="l05a-pause" class="l05a-cb" /><label for="l05a-pause" class="l05a-btn"><span class="l05a-off">Pause animation</span><span class="l05a-on">Play animation</span></label>
<div class="l05a-box" style="overflow-x:auto">
<svg class="l05a-flow" viewBox="0 0 760 302" role="img" aria-labelledby="l05a-t l05a-d" style="width:760px;max-width:100%;min-width:699px;height:auto;display:block;margin:0 auto">
<title id="l05a-t">One person, three names in a SCIM user record</title>
<desc id="l05a-d">A user record at /Users, with the three names one person has. userName is the login name: the app requires it to be unique and does not treat it as case-sensitive, and it can be edited, so it can change. externalId is a label the IdP chooses for her, and the app does not enforce that it is unique. id is assigned by the app, never changes and is never reused; the IdP stores it and uses it in later requests. The diagram highlights each part in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
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
.l05a-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:14s;animation-timing-function:linear;animation-iteration-count:infinite}
.l05a-pk.l05a-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.l05a-pk.l05a-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.l05a-wrap{margin:20px 0}
@media (min-width:801px){.l05a-wrap{margin-left:-44px;margin-right:-44px}}
.l05a-g rect,.l05a-g line,.l05a-g path:not(.l05a-gl){opacity:.5;animation-duration:14s;animation-timing-function:linear;animation-iteration-count:infinite}
.l05a-h{opacity:0;animation-duration:14s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.l05a-flow:hover .l05a-g rect,svg.l05a-flow:hover .l05a-g line,svg.l05a-flow:hover .l05a-g path:not(.l05a-gl),svg.l05a-flow:hover .l05a-pk,svg.l05a-flow:hover .l05a-h{animation-play-state:paused}
.l05a-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.l05a-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.l05a-btn:hover{background:var(--hover)}
.l05a-cb:focus-visible + .l05a-btn{outline:2px solid var(--accent);outline-offset:2px}
.l05a-cb:checked + .l05a-btn .l05a-off,.l05a-cb:not(:checked) + .l05a-btn .l05a-on{display:none}
.l05a-cb:checked ~ .l05a-box .l05a-g rect,.l05a-cb:checked ~ .l05a-box .l05a-g line,.l05a-cb:checked ~ .l05a-box .l05a-g path:not(.l05a-gl),.l05a-cb:checked ~ .l05a-box .l05a-pk,.l05a-cb:checked ~ .l05a-box .l05a-h{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.l05a-g rect,.l05a-g line,.l05a-g path:not(.l05a-gl){animation:none;opacity:1}.l05a-pk{animation:none;display:none}.l05a-h{animation:none;opacity:0}.l05a-btn{display:none}}
@keyframes l05a-g0{0%{opacity:1}33.333%{opacity:1}33.343%,100%{opacity:.5}}
@keyframes l05a-h0{0%{opacity:1}33.333%{opacity:1}33.343%,100%{opacity:0}}
.l05a-g0 rect,.l05a-g0 line,.l05a-g0 path:not(.l05a-gl){animation-name:l05a-g0}.l05a-h0{animation-name:l05a-h0}
@keyframes l05a-g1{0%,33.323%{opacity:.5}33.333%{opacity:1}66.667%{opacity:1}66.677%,100%{opacity:.5}}
@keyframes l05a-h1{0%,33.323%{opacity:0}33.333%{opacity:1}66.667%{opacity:1}66.677%,100%{opacity:0}}
.l05a-g1 rect,.l05a-g1 line,.l05a-g1 path:not(.l05a-gl){animation-name:l05a-g1}.l05a-h1{animation-name:l05a-h1}
@keyframes l05a-g2{0%,66.657%{opacity:.5}66.667%{opacity:1}100%{opacity:1}100.01%,100%{opacity:.5}}
@keyframes l05a-h2{0%,66.657%{opacity:0}66.667%{opacity:1}100%{opacity:1}100.01%,100%{opacity:0}}
.l05a-g2 rect,.l05a-g2 line,.l05a-g2 path:not(.l05a-gl){animation-name:l05a-g2}.l05a-h2{animation-name:l05a-h2}
</style>
<defs>
<marker id="l05a-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="l05a-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="l05a-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<rect class="l05a-box" x="14" y="16" width="440" height="212" rx="9"/><text class="l05a-ttlL" x="28" y="37">Dana's user record</text><text class="l05a-subL" x="28" y="54">a User, at /Users</text>
<rect class="l05a-nest" x="26" y="62" width="416" height="46" rx="9"/><text class="l05a-ttlL" x="40" y="83">userName</text><text class="l05a-subL" x="40" y="100">the login name</text>
<rect class="l05a-nest" x="26" y="116" width="416" height="46" rx="9"/><text class="l05a-ttlL" x="40" y="137">externalId</text><text class="l05a-subL" x="40" y="154">a label the IdP chooses</text>
<rect class="l05a-nest" x="26" y="170" width="416" height="46" rx="9"/><text class="l05a-ttlL" x="40" y="191">id</text><text class="l05a-subL" x="40" y="208">assigned by the app</text>
<g class="l05a-g l05a-g0">
<path class="l05a-conn" d="M442,79 L462,79 L462,79 L470,79" marker-end="url(#l05a-m-front)"/>
<rect class="l05a-note" x="484" y="46" width="262" height="65" rx="8"/>
<text class="l05a-nt" x="615" y="68">Must be unique; the app does not</text>
<text class="l05a-nt" x="615" y="84">treat it as case-sensitive. It can be</text>
<text class="l05a-nt" x="615" y="102">edited, so it can change</text>
<circle class="l05a-badge l05a-b-front" cx="484" cy="79" r="12"/><text class="l05a-bt" x="484" y="83.5">1</text>
</g>
<g class="l05a-g l05a-g1">
<path class="l05a-conn" d="M442,133 L466,133 L466,146 L470,146" marker-end="url(#l05a-m-front)"/>
<rect class="l05a-note" x="484" y="122" width="262" height="48" rx="8"/>
<text class="l05a-nt" x="615" y="142">The app does not enforce that</text>
<text class="l05a-nt" x="615" y="160">it is unique</text>
<circle class="l05a-badge l05a-b-front" cx="484" cy="146" r="12"/><text class="l05a-bt" x="484" y="150.0">2</text>
</g>
<g class="l05a-g l05a-g2">
<path class="l05a-conn" d="M442,187 L470,187 L470,212 L470,212" marker-end="url(#l05a-m-front)"/>
<rect class="l05a-note" x="484" y="180" width="262" height="65" rx="8"/>
<text class="l05a-nt" x="615" y="200">Never changes and is never reused.</text>
<text class="l05a-nt" x="615" y="218">The IdP stores it and uses it in</text>
<text class="l05a-nt" x="615" y="234">later requests</text>
<circle class="l05a-badge l05a-b-front" cx="484" cy="212" r="12"/><text class="l05a-bt" x="484" y="216.5">3</text>
</g>
<g class="l05a-h l05a-h0">
<rect class="l05a-hl" x="26" y="62" width="416" height="46" rx="9"/>
</g>
<g class="l05a-h l05a-h1">
<rect class="l05a-hl" x="26" y="116" width="416" height="46" rx="9"/>
</g>
<g class="l05a-h l05a-h2">
<rect class="l05a-hl" x="26" y="170" width="416" height="46" rx="9"/>
</g>
</svg>
</div>
</div>
<!-- /diagram:scim-identifiers -->

The three numbered notes follow the three names in order. The `userName` can be edited and so can change; the `externalId` is only a label the IdP chooses; the app assigns the `id` and it never changes. The IdP stores the `id` and uses it in later requests.

## The life of an account

IT teams call the three moments in an account's life **joiner** (a new hire), **mover** (someone who changes team) and **leaver** (someone who leaves). `{id}` stands for the real id.

<!-- diagram:scim-protocol -->
<div class="sc-wrap" style="position:relative">
<input type="checkbox" id="sc-pause" class="sc-cb" /><label for="sc-pause" class="sc-btn"><span class="sc-off">Pause animation</span><span class="sc-on">Play animation</span></label>
<div class="sc-box" style="overflow-x:auto">
<svg class="sc-flow" viewBox="0 0 760 770" role="img" aria-labelledby="sc-t sc-d" style="width:760px;max-width:100%;min-width:699px;height:auto;display:block;margin:0 auto">
<title id="sc-t">SCIM lifecycle: create, group change, deactivate, delete</title>
<desc id="sc-d">Eight steps between an identity provider acting as SCIM client and your app acting as SCIM server, with Dana's already-open browser session as a third lane. Step 1: the IdP sends POST /Users with her userName, externalId and active true. Step 2: the app answers 201 Created and includes the id it assigned. Step 3: the IdP sends PATCH /Groups/{id} to add her to the group's member list; removing her uses the same request; some Okta apps get a PUT of the whole group instead. Step 4: the IdP deactivates her by setting active to false, by PATCH /Users/{id}; some Okta apps get a PUT instead. Step 5, a failure mode: her browser still has a session from before, and unless the app acts her old session still works. Step 6: your app must end her sessions itself when it sees active false. Step 7: DELETE /Users/{id}, removed for good; Okta never sends it. Step 8: the app answers 404 Not Found for every later request about that id. The diagram highlights each step in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
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
<line class="sc-life" x1="110" y1="72" x2="110" y2="718"/>
<line class="sc-life" x1="380" y1="72" x2="380" y2="718"/>
<line class="sc-life" x1="650" y1="72" x2="650" y2="718"/>
<rect class="sc-box" x="20" y="10" width="180" height="62" rx="10"/><text class="sc-ttl" x="110" y="36">Identity provider</text><text class="sc-sub" x="110" y="56">SCIM client (Okta, Entra)</text>
<rect class="sc-hot" x="290" y="10" width="180" height="62" rx="10"/><text class="sc-ttl" x="380" y="36">Your app</text><text class="sc-sub" x="380" y="56">SCIM server</text>
<rect class="sc-box" x="560" y="10" width="180" height="62" rx="10"/><text class="sc-ttl" x="650" y="36">Dana's browser</text><text class="sc-sub" x="650" y="56">already signed in</text>
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
<text class="sc-dim" x="245" y="264">add or remove her as a member</text>
<text class="sc-dim" x="245" y="280">some Okta apps: PUT instead</text>
<line class="sc-front" x1="124" y1="294" x2="366" y2="294" marker-end="url(#sc-m-front)"/>
<circle class="sc-badge sc-b-front" cx="110" cy="294" r="12"/><text class="sc-bt" x="110" y="298.5">3</text>
</g>
<g class="sc-g sc-g3">
<text class="sc-main" x="245" y="334">PATCH /Users/{id}</text>
<text class="sc-dim" x="245" y="350">active = false: deactivate her</text>
<text class="sc-dim" x="245" y="366">some Okta apps: PUT instead</text>
<line class="sc-front" x1="124" y1="380" x2="366" y2="380" marker-end="url(#sc-m-front)"/>
<circle class="sc-badge sc-b-front" cx="110" cy="380" r="12"/><text class="sc-bt" x="110" y="384.5">4</text>
</g>
<g class="sc-g sc-g4">
<text class="sc-main sc-badt" x="515" y="420">request on her old session</text>
<text class="sc-dim" x="515" y="436">still works unless the app acts</text>
<line class="sc-bad" x1="636" y1="450" x2="394" y2="450" marker-end="url(#sc-m-bad)"/>
<circle class="sc-badge sc-b-bad" cx="650" cy="450" r="12"/><text class="sc-bt" x="650" y="454.5">5</text>
</g>
<g class="sc-g sc-g5">
<rect class="sc-note-good" x="276" y="484" width="208" height="48" rx="8"/>
<text class="sc-nt" x="380" y="505">on active = false, your app</text>
<text class="sc-nt" x="380" y="522">ends her sessions itself</text>
<circle class="sc-badge sc-b-good" cx="276" cy="508" r="12"/><text class="sc-bt" x="276" y="512.5">6</text>
</g>
<g class="sc-g sc-g6">
<text class="sc-main" x="245" y="566">DELETE /Users/{id}</text>
<text class="sc-dim" x="245" y="582">removed for good; Okta never sends it</text>
<line class="sc-front" x1="124" y1="596" x2="366" y2="596" marker-end="url(#sc-m-front)"/>
<circle class="sc-badge sc-b-front" cx="110" cy="596" r="12"/><text class="sc-bt" x="110" y="600.5">7</text>
</g>
<g class="sc-g sc-g7">
<text class="sc-main" x="245" y="636">404 Not Found</text>
<text class="sc-dim" x="245" y="652">for every later request on that id</text>
<line class="sc-back" x1="366" y1="666" x2="124" y2="666" marker-end="url(#sc-m-back)"/>
<circle class="sc-badge sc-b-back" cx="380" cy="666" r="12"/><text class="sc-bt" x="380" y="670.5">8</text>
</g>
<circle class="sc-pk sc-p0" cx="130" cy="138" r="5.5"/>
<circle class="sc-pk sc-p1 sc-pkback" cx="360" cy="208" r="5.5"/>
<circle class="sc-pk sc-p2" cx="130" cy="294" r="5.5"/>
<circle class="sc-pk sc-p3" cx="130" cy="380" r="5.5"/>
<circle class="sc-pk sc-p4 sc-pkbad" cx="630" cy="450" r="5.5"/>
<circle class="sc-pk sc-p6" cx="130" cy="596" r="5.5"/>
<circle class="sc-pk sc-p7 sc-pkback" cx="360" cy="666" r="5.5"/>
<line class="sc-front" x1="40" y1="746" x2="70" y2="746"/>
<text class="sc-dim" x="78" y="750" style="text-anchor:start">request</text>
<line class="sc-back" x1="156" y1="746" x2="186" y2="746"/>
<text class="sc-dim" x="194" y="750" style="text-anchor:start">response</text>
<line class="sc-bad" x1="279" y1="746" x2="309" y2="746"/>
<text class="sc-dim" x="317" y="750" style="text-anchor:start">failure mode</text>
<rect class="sc-note-good" x="427" y="738" width="22" height="16" rx="4"/>
<text class="sc-dim" x="457" y="750" style="text-anchor:start">what your app must do</text>
</svg>
</div>
</div>
<!-- /diagram:scim-protocol -->

The numbers 1 to 8 match the list below. Step 5 is the failure mode: the third lane shows why your app has to end her session itself (step 6).

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

<!-- diagram:scim-account-states -->
<div class="l05b-wrap" style="position:relative">
<input type="checkbox" id="l05b-pause" class="l05b-cb" /><label for="l05b-pause" class="l05b-btn"><span class="l05b-off">Pause animation</span><span class="l05b-on">Play animation</span></label>
<div class="l05b-box" style="overflow-x:auto">
<svg class="l05b-flow" viewBox="0 0 760 210" role="img" aria-labelledby="l05b-t l05b-d" style="width:760px;max-width:100%;min-width:699px;height:auto;display:block;margin:0 auto">
<title id="l05b-t">An account in the app: active, deactivated, deleted</title>
<desc id="l05b-d">Three states of the app's copy of an account. Active: active is true, which typically means the user can sign in. Deactivated: active is false, which typically means the account is suspended; it still exists, so it can be switched back on. Deleted: the account is gone, and the app must answer 404 for every later request about it, though the standard lets an app keep the data privately. Setting active to false moves the account to deactivated, switching it back on returns it to active, and an account removed for good moves to deleted. The diagram highlights each stage in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
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
<rect class="l05b-note-good" x="14" y="40" width="171" height="110" rx="10"/>
<text class="l05b-ttl" x="99" y="67">Active</text>
<text class="l05b-sub" x="99" y="87">active = true</text>
<text class="l05b-nt" x="99" y="114">typically: the user</text>
<text class="l05b-nt" x="99" y="131">can sign in</text>
<text class="l05b-main" x="240" y="64">active = false</text>
<line class="l05b-front" x1="193" y1="70" x2="287" y2="70" marker-end="url(#l05b-m-front)"/>
<text class="l05b-main" x="240" y="112">switched back on</text>
<line class="l05b-back" x1="287" y1="94" x2="193" y2="94" marker-end="url(#l05b-m-back)"/>
</g>
<g class="l05b-g l05b-g1">
<rect class="l05b-box" x="295" y="40" width="171" height="110" rx="10"/>
<text class="l05b-ttl" x="380" y="67">Deactivated</text>
<text class="l05b-sub" x="380" y="87">active = false</text>
<text class="l05b-nt" x="380" y="114">typically: suspended</text>
<text class="l05b-nt" x="380" y="131">the account still exists</text>
<text class="l05b-main" x="520" y="48">removed for</text>
<text class="l05b-dim" x="520" y="64">good</text>
<line class="l05b-front" x1="473" y1="70" x2="567" y2="70" marker-end="url(#l05b-m-front)"/>
</g>
<g class="l05b-g l05b-g2">
<rect class="l05b-box" x="575" y="40" width="171" height="110" rx="10"/>
<text class="l05b-ttl" x="661" y="67">Deleted</text>
<text class="l05b-sub" x="661" y="87">the account is gone</text>
<text class="l05b-nt" x="661" y="114">404 for every later</text>
<text class="l05b-nt" x="661" y="131">request about it</text>
</g>
<circle class="l05b-pk l05b-p0" cx="199" cy="70" r="5.5"/>
<circle class="l05b-pk l05b-p1" cx="479" cy="70" r="5.5"/>
<line class="l05b-front" x1="40" y1="186" x2="70" y2="186"/>
<text class="l05b-dim" x="78" y="190" style="text-anchor:start">step forward</text>
<line class="l05b-back" x1="188" y1="186" x2="218" y2="186"/>
<text class="l05b-dim" x="226" y="190" style="text-anchor:start">step back</text>
<rect class="l05b-note-good" x="317" y="178" width="22" height="16" rx="4"/>
<text class="l05b-dim" x="347" y="190" style="text-anchor:start">can sign in</text>
</svg>
</div>
</div>
<!-- /diagram:scim-account-states -->

Read left to right. Setting `active` to `false` deactivates the account, and it can be switched back on. A deleted account is different: it is gone, and the app answers 404 for every later request about it.

## What goes wrong

- **409 Conflict, "userName already in use".** The app refuses to create a second user with the same `userName`. Look for an older or duplicate account.
- **401 Unauthorized.** The token is wrong, missing or expired, so every request fails. In Entra, when most calls keep failing (for example with invalid credentials), the job enters *quarantine* and runs gradually less often, down to once a day.
- **429 Too Many Requests.** The app is rate-limiting the IdP. Okta pauses, waits the number of seconds in the `Retry-After` header (five minutes if there is none), doubles the wait on each retry and stops after 10 attempts, so a person must then step in.
- **Group changes do not arrive.** Okta only sends a membership change when the user is in the Okta group, is assigned to the app, and the group is pushed on the *Push Groups* tab. Okta does not support using the same group for both assignment and push, so make a separate push group. Okta sources memberships, so edits made to a pushed group inside the app cause sync problems.
- **A renamed login.** Keep `userName` stable. Okta advises against using an email address as the user ID because emails often change.

<!-- diagram:scim-group-push -->
<div class="l05c-wrap" style="position:relative">
<input type="checkbox" id="l05c-pause" class="l05c-cb" /><label for="l05c-pause" class="l05c-btn"><span class="l05c-off">Pause animation</span><span class="l05c-on">Play animation</span></label>
<div class="l05c-box" style="overflow-x:auto">
<svg class="l05c-flow" viewBox="0 0 760 450" role="img" aria-labelledby="l05c-t l05c-d" style="width:760px;max-width:100%;min-width:699px;height:auto;display:block;margin:0 auto">
<title id="l05c-t">Why an Okta group change does not arrive in the app</title>
<desc id="l05c-d">A chain of three checks. Okta only sends a membership change when the user is in the Okta group, is assigned to the app, and the group is pushed on the Push Groups tab. If the user is not in the group, nothing is sent. If the user is in the group but not assigned to the app, nothing is sent. If the user is in the group and assigned but the group is not pushed, nothing is sent. If all three hold, Okta can send the change. The diagram highlights each path in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
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
.l05c-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:16s;animation-timing-function:linear;animation-iteration-count:infinite}
.l05c-pk.l05c-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.l05c-pk.l05c-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.l05c-wrap{margin:20px 0}
@media (min-width:801px){.l05c-wrap{margin-left:-44px;margin-right:-44px}}
.l05c-g rect,.l05c-g line,.l05c-g path:not(.l05c-gl){opacity:.5;animation-duration:16s;animation-timing-function:linear;animation-iteration-count:infinite}
.l05c-h{opacity:0;animation-duration:16s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.l05c-flow:hover .l05c-g rect,svg.l05c-flow:hover .l05c-g line,svg.l05c-flow:hover .l05c-g path:not(.l05c-gl),svg.l05c-flow:hover .l05c-pk,svg.l05c-flow:hover .l05c-h{animation-play-state:paused}
.l05c-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.l05c-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.l05c-btn:hover{background:var(--hover)}
.l05c-cb:focus-visible + .l05c-btn{outline:2px solid var(--accent);outline-offset:2px}
.l05c-cb:checked + .l05c-btn .l05c-off,.l05c-cb:not(:checked) + .l05c-btn .l05c-on{display:none}
.l05c-cb:checked ~ .l05c-box .l05c-g rect,.l05c-cb:checked ~ .l05c-box .l05c-g line,.l05c-cb:checked ~ .l05c-box .l05c-g path:not(.l05c-gl),.l05c-cb:checked ~ .l05c-box .l05c-pk,.l05c-cb:checked ~ .l05c-box .l05c-h{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.l05c-g rect,.l05c-g line,.l05c-g path:not(.l05c-gl){animation:none;opacity:1}.l05c-pk{animation:none;display:none}.l05c-h{animation:none;opacity:0}.l05c-btn{display:none}}
@keyframes l05c-h0{0%{opacity:1}25%{opacity:1}25.01%,100%{opacity:0}}
.l05c-h0{animation-name:l05c-h0}
@keyframes l05c-h1{0%,24.99%{opacity:0}25%{opacity:1}50%{opacity:1}50.01%,100%{opacity:0}}
.l05c-h1{animation-name:l05c-h1}
@keyframes l05c-h2{0%,49.99%{opacity:0}50%{opacity:1}75%{opacity:1}75.01%,100%{opacity:0}}
.l05c-h2{animation-name:l05c-h2}
@keyframes l05c-h3{0%,74.99%{opacity:0}75%{opacity:1}100%{opacity:1}100.01%,100%{opacity:0}}
.l05c-h3{animation-name:l05c-h3}
</style>
<defs>
<marker id="l05c-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="l05c-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="l05c-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<path class="l05c-edge" d="M380,72 L380,101 L148,101 L148,127" marker-end="url(#l05c-m-front)"/>
<text class="l05c-dimL" x="154" y="117">no</text>
<path class="l05c-edge" d="M380,72 L380,101 L455,101 L455,127" marker-end="url(#l05c-m-front)"/>
<text class="l05c-dimL" x="462" y="117">yes</text>
<path class="l05c-edge" d="M455,178 L455,207 L308,207 L308,233" marker-end="url(#l05c-m-front)"/>
<text class="l05c-dimL" x="315" y="223">no</text>
<path class="l05c-edge" d="M455,178 L455,207 L540,207 L540,233" marker-end="url(#l05c-m-front)"/>
<text class="l05c-dimL" x="548" y="223">yes</text>
<path class="l05c-edge" d="M540,284 L540,313 L466,313 L466,339" marker-end="url(#l05c-m-front)"/>
<text class="l05c-dimL" x="472" y="329">no</text>
<path class="l05c-edge" d="M540,284 L540,313 L612,313 L612,339" marker-end="url(#l05c-m-front)"/>
<text class="l05c-dimL" x="620" y="329">yes</text>
<rect class="l05c-note-bad" x="80" y="130" width="134" height="48" rx="8"/><text class="l05c-nt" x="148" y="151">Not sent: user</text><text class="l05c-nt" x="148" y="168">not in the group</text>
<rect class="l05c-note-bad" x="230" y="236" width="155" height="48" rx="8"/><text class="l05c-nt" x="308" y="257">Not sent: user not</text><text class="l05c-nt" x="308" y="274">assigned to the app</text>
<rect class="l05c-note-bad" x="402" y="342" width="128" height="48" rx="8"/><text class="l05c-nt" x="466" y="363">Not sent: group</text><text class="l05c-nt" x="466" y="380">is not pushed</text>
<rect class="l05c-note-good" x="546" y="342" width="134" height="48" rx="8"/><text class="l05c-nt" x="612" y="363">All three hold:</text><text class="l05c-nt" x="612" y="380">Okta can send it</text>
<rect class="l05c-box" x="463" y="236" width="155" height="48" rx="8"/><text class="l05c-main" x="540" y="257">Is the group pushed</text><text class="l05c-nt" x="540" y="274">on Push Groups?</text>
<rect class="l05c-box" x="374" y="130" width="162" height="48" rx="8"/><text class="l05c-main" x="455" y="151">Is the user assigned</text><text class="l05c-nt" x="455" y="168">to the app?</text>
<rect class="l05c-box" x="316" y="24" width="128" height="48" rx="8"/><text class="l05c-main" x="380" y="45">Is the user in</text><text class="l05c-nt" x="380" y="62">the Okta group?</text>
<g class="l05c-h l05c-h0">
<path class="l05c-hle" d="M380,72 L380,101 L148,101 L148,127" marker-end="url(#l05c-m-front)"/>
<rect class="l05c-hl" x="316" y="24" width="128" height="48" rx="8"/>
<rect class="l05c-hl" x="80" y="130" width="134" height="48" rx="8"/>
</g>
<g class="l05c-h l05c-h1">
<path class="l05c-hle" d="M380,72 L380,101 L455,101 L455,127" marker-end="url(#l05c-m-front)"/>
<path class="l05c-hle" d="M455,178 L455,207 L308,207 L308,233" marker-end="url(#l05c-m-front)"/>
<rect class="l05c-hl" x="316" y="24" width="128" height="48" rx="8"/>
<rect class="l05c-hl" x="374" y="130" width="162" height="48" rx="8"/>
<rect class="l05c-hl" x="230" y="236" width="155" height="48" rx="8"/>
</g>
<g class="l05c-h l05c-h2">
<path class="l05c-hle" d="M380,72 L380,101 L455,101 L455,127" marker-end="url(#l05c-m-front)"/>
<path class="l05c-hle" d="M455,178 L455,207 L540,207 L540,233" marker-end="url(#l05c-m-front)"/>
<path class="l05c-hle" d="M540,284 L540,313 L466,313 L466,339" marker-end="url(#l05c-m-front)"/>
<rect class="l05c-hl" x="316" y="24" width="128" height="48" rx="8"/>
<rect class="l05c-hl" x="374" y="130" width="162" height="48" rx="8"/>
<rect class="l05c-hl" x="463" y="236" width="155" height="48" rx="8"/>
<rect class="l05c-hl" x="402" y="342" width="128" height="48" rx="8"/>
</g>
<g class="l05c-h l05c-h3">
<path class="l05c-hle" d="M380,72 L380,101 L455,101 L455,127" marker-end="url(#l05c-m-front)"/>
<path class="l05c-hle" d="M455,178 L455,207 L540,207 L540,233" marker-end="url(#l05c-m-front)"/>
<path class="l05c-hle" d="M540,284 L540,313 L612,313 L612,339" marker-end="url(#l05c-m-front)"/>
<rect class="l05c-hl" x="316" y="24" width="128" height="48" rx="8"/>
<rect class="l05c-hl" x="374" y="130" width="162" height="48" rx="8"/>
<rect class="l05c-hl" x="463" y="236" width="155" height="48" rx="8"/>
<rect class="l05c-hl" x="546" y="342" width="134" height="48" rx="8"/>
</g>
<line class="l05c-front" x1="40" y1="426" x2="70" y2="426"/>
<text class="l05c-dim" x="78" y="430" style="text-anchor:start">the path being traced</text>
<rect class="l05c-note-good" x="246" y="418" width="22" height="16" rx="4"/>
<text class="l05c-dim" x="276" y="430" style="text-anchor:start">the change can be sent</text>
<rect class="l05c-note-bad" x="450" y="418" width="22" height="16" rx="4"/>
<text class="l05c-dim" x="480" y="430" style="text-anchor:start">nothing is sent</text>
</svg>
</div>
</div>
<!-- /diagram:scim-group-push -->

Follow the questions from the top. Okta only sends a membership change when all three answers are yes, so a single no means nothing is sent.

## Your task

This sample is invented, not from a real system. Read it and answer without scrolling up.

```text
POST /Users   {"userName": "dana@example.com", "externalId": "00u1abc", "active": true}
```

Which field is the login name? Which value will the app invent and send back, and in which reply? If the app already holds `dana@example.com`, which status code comes back? Check yourself against steps 1 and 2 and the first bullet under *What goes wrong*.

Next: lesson 6 covers MFA and sessions, and lesson 7 covers the joiner-mover-leaver process that SCIM carries out.
