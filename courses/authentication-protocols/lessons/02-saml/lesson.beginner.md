# SAML 2.0

Priya starts today at Example Corp. She opens a work app called Acme Tracker and, with no new password, lands inside it signed in as herself. This lesson follows that one click in order, so you can tell which part broke when a ticket says "SSO is down for Acme Tracker". You need no protocol background. Facts checked 2026-10-06 against vendor documentation and the published SAML 2.0 standard.

## Words you need first

- **SAML 2.0**: a standard (published by the OASIS standards body in 2005) for one system to tell another, in signed XML, that a person has already proved who they are. XML is a text format made of tags such as `<Audience>`.
- **Identity provider (IdP)**: the system that checks Priya's password and MFA and vouches for her. Okta and Microsoft Entra ID are IdPs.
- **Service provider (SP)**: the app that wants proof, here Acme Tracker. The SP never sees her password.
- **Assertion**: the signed statement from the IdP: who Priya is, when it was made, which app it is for, and how long it stays good.
- **Response**: the envelope the assertion arrives in. The assertion is the letter, the Response is the envelope.
- **Signature and certificate**: the IdP signs the assertion with a private key only it holds. The app keeps a copy of the matching public certificate and uses it to check the signature. A certificate has an end date.
- **Metadata**: a small XML file each side publishes, listing its entity ID, its web addresses and its certificate. Admins often upload it instead of typing values.
- **Entity ID**: the unique name of a system, usually written like a web address (it does not have to open a page). Both the IdP and the SP have one.
- **ACS URL** (assertion consumer service): the address on the app that accepts the Response.
- **Base64**: a way of writing data as plain letters and digits so it fits in a web form. It is not encryption; anyone can reverse it.

## The flow, step by step

<!-- diagram:saml-flow -->
<div style="position:relative;margin:20px 0">
<input type="checkbox" id="sm-pause" class="sm-cb" /><label for="sm-pause" class="sm-btn"><span class="sm-off">Pause animation</span><span class="sm-on">Play animation</span></label>
<div class="sm-box" style="overflow-x:auto">
<svg class="sm-flow" viewBox="0 0 760 837" role="img" aria-labelledby="sm-t sm-d" style="width:100%;min-width:640px;max-width:800px;height:auto;display:block;margin:0 auto">
<title id="sm-t">SAML 2.0 Web Browser SSO, SP-initiated</title>
<desc id="sm-d">Three parties: the service provider (the app), the user's browser, and the identity provider. Every message travels through the browser. The browser asks the app for a page and has no session. The app answers with a redirect carrying an authentication request and a RelayState value. The browser sends that request to the identity provider, which identifies the user either by a new sign-in or an existing session. The identity provider returns an HTML form carrying the signed SAML Response and the RelayState, which the browser posts to the app's assertion consumer service URL. The app validates the Response and redirects the browser to the original page with its own session. A final note says IdP-initiated sign-in starts at the form step, with no authentication request and therefore no InResponseTo value. The diagram highlights each step in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
<style>
.sm-box{fill:var(--panel);stroke:var(--border-strong);stroke-width:1.5}
.sm-hot{fill:var(--panel);stroke:var(--accent);stroke-width:2.5}
.sm-ttl{fill:var(--text);font:600 15px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.sm-sub{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.sm-life{stroke:var(--border-strong);stroke-width:1.5;stroke-dasharray:4 5}
.sm-front{stroke:var(--accent);stroke-width:2;fill:none}
.sm-back{stroke:var(--muted);stroke-width:2;stroke-dasharray:7 5;fill:none}
.sm-bad{stroke:var(--bad);stroke-width:2;fill:none}
.sm-main{fill:var(--text);font:600 13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.sm-badt{fill:var(--bad-text)}
.sm-dim{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.sm-badge{fill:var(--accent)}
.sm-b-back{fill:var(--muted)}
.sm-b-bad{fill:var(--bad)}
.sm-b-good{fill:var(--good)}
.sm-bt{fill:var(--on-accent);font:700 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.sm-note{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.sm-note-good{fill:var(--good-bg);stroke:var(--good);stroke-width:1.5}
.sm-note-bad{fill:var(--bad-bg);stroke:var(--bad);stroke-width:1.5}
.sm-nt{fill:var(--body);font:12.5px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.sm-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:20s;animation-timing-function:linear;animation-iteration-count:infinite}
.sm-pk.sm-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.sm-pk.sm-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.sm-g{opacity:.45;animation-duration:20s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.sm-flow:hover .sm-g,svg.sm-flow:hover .sm-pk{animation-play-state:paused}
.sm-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.sm-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.sm-btn:hover{background:var(--hover)}
.sm-cb:focus-visible + .sm-btn{outline:2px solid var(--accent);outline-offset:2px}
.sm-cb:checked + .sm-btn .sm-off,.sm-cb:not(:checked) + .sm-btn .sm-on{display:none}
.sm-cb:checked ~ .sm-box .sm-g,.sm-cb:checked ~ .sm-box .sm-pk{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.sm-g{animation:none;opacity:1}.sm-pk{animation:none;display:none}.sm-btn{display:none}}
@keyframes sm-g0{0%{opacity:1}11.111%{opacity:1}11.121%,100%{opacity:.45}}
@keyframes sm-p0{0%,-0.01%{opacity:0;transform:translateX(0)}0%{opacity:1;transform:translateX(0)}11.111%{opacity:1;transform:translateX(-236px)}11.121%,100%{opacity:0;transform:translateX(-236px)}}
.sm-g0{animation-name:sm-g0}.sm-p0{animation-name:sm-p0}
@keyframes sm-g1{0%,11.101%{opacity:.45}11.111%{opacity:1}22.222%{opacity:1}22.232%,100%{opacity:.45}}
@keyframes sm-p1{0%,11.101%{opacity:0;transform:translateX(0)}11.111%{opacity:1;transform:translateX(0)}22.222%{opacity:1;transform:translateX(236px)}22.232%,100%{opacity:0;transform:translateX(236px)}}
.sm-g1{animation-name:sm-g1}.sm-p1{animation-name:sm-p1}
@keyframes sm-g2{0%,22.212%{opacity:.45}22.222%{opacity:1}33.333%{opacity:1}33.343%,100%{opacity:.45}}
@keyframes sm-p2{0%,22.212%{opacity:0;transform:translateX(0)}22.222%{opacity:1;transform:translateX(0)}33.333%{opacity:1;transform:translateX(236px)}33.343%,100%{opacity:0;transform:translateX(236px)}}
.sm-g2{animation-name:sm-g2}.sm-p2{animation-name:sm-p2}
@keyframes sm-g3{0%,33.323%{opacity:.45}33.333%{opacity:1}44.444%{opacity:1}44.454%,100%{opacity:.45}}
.sm-g3{animation-name:sm-g3}
@keyframes sm-g4{0%,44.434%{opacity:.45}44.444%{opacity:1}55.556%{opacity:1}55.566%,100%{opacity:.45}}
@keyframes sm-p4{0%,44.434%{opacity:0;transform:translateX(0)}44.444%{opacity:1;transform:translateX(0)}55.556%{opacity:1;transform:translateX(-236px)}55.566%,100%{opacity:0;transform:translateX(-236px)}}
.sm-g4{animation-name:sm-g4}.sm-p4{animation-name:sm-p4}
@keyframes sm-g5{0%,55.546%{opacity:.45}55.556%{opacity:1}66.667%{opacity:1}66.677%,100%{opacity:.45}}
@keyframes sm-p5{0%,55.546%{opacity:0;transform:translateX(0)}55.556%{opacity:1;transform:translateX(0)}66.667%{opacity:1;transform:translateX(-236px)}66.677%,100%{opacity:0;transform:translateX(-236px)}}
.sm-g5{animation-name:sm-g5}.sm-p5{animation-name:sm-p5}
@keyframes sm-g6{0%,66.657%{opacity:.45}66.667%{opacity:1}77.778%{opacity:1}77.788%,100%{opacity:.45}}
.sm-g6{animation-name:sm-g6}
@keyframes sm-g7{0%,77.768%{opacity:.45}77.778%{opacity:1}88.889%{opacity:1}88.899%,100%{opacity:.45}}
@keyframes sm-p7{0%,77.768%{opacity:0;transform:translateX(0)}77.778%{opacity:1;transform:translateX(0)}88.889%{opacity:1;transform:translateX(236px)}88.899%,100%{opacity:0;transform:translateX(236px)}}
.sm-g7{animation-name:sm-g7}.sm-p7{animation-name:sm-p7}
@keyframes sm-g8{0%,88.879%{opacity:.45}88.889%{opacity:1}100%{opacity:1}100.01%,100%{opacity:.45}}
.sm-g8{animation-name:sm-g8}
</style>
<defs>
<marker id="sm-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="sm-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="sm-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<line class="sm-life" x1="110" y1="72" x2="110" y2="785"/>
<line class="sm-life" x1="380" y1="72" x2="380" y2="785"/>
<line class="sm-life" x1="650" y1="72" x2="650" y2="785"/>
<rect class="sm-hot" x="20" y="10" width="180" height="62" rx="10"/><text class="sm-ttl" x="110" y="36">Service provider</text><text class="sm-sub" x="110" y="56">the app (SP)</text>
<rect class="sm-box" x="290" y="10" width="180" height="62" rx="10"/><text class="sm-ttl" x="380" y="36">Browser</text><text class="sm-sub" x="380" y="56">the user agent</text>
<rect class="sm-box" x="560" y="10" width="180" height="62" rx="10"/><text class="sm-ttl" x="650" y="36">Identity provider</text><text class="sm-sub" x="650" y="56">Okta, Entra ID (IdP)</text>
<g class="sm-g sm-g0">
<text class="sm-main" x="245" y="108">GET the protected page</text>
<text class="sm-dim" x="245" y="124">no session yet</text>
<line class="sm-front" x1="366" y1="138" x2="124" y2="138" marker-end="url(#sm-m-front)"/>
<circle class="sm-badge sm-b-front" cx="380" cy="138" r="12"/><text class="sm-bt" x="380" y="142.5">1</text>
</g>
<g class="sm-g sm-g1">
<text class="sm-main" x="245" y="178">302: AuthnRequest, RelayState</text>
<text class="sm-dim" x="245" y="194">HTTP-Redirect binding</text>
<line class="sm-front" x1="124" y1="208" x2="366" y2="208" marker-end="url(#sm-m-front)"/>
<circle class="sm-badge sm-b-front" cx="110" cy="208" r="12"/><text class="sm-bt" x="110" y="212.5">2</text>
</g>
<g class="sm-g sm-g2">
<text class="sm-main" x="515" y="248">GET the SSO URL</text>
<text class="sm-dim" x="515" y="264">SAMLRequest, RelayState</text>
<line class="sm-front" x1="394" y1="278" x2="636" y2="278" marker-end="url(#sm-m-front)"/>
<circle class="sm-badge sm-b-front" cx="380" cy="278" r="12"/><text class="sm-bt" x="380" y="282.5">3</text>
</g>
<g class="sm-g sm-g3">
<rect class="sm-note" x="516" y="312" width="234" height="48" rx="8"/>
<text class="sm-nt" x="633" y="333">IdP identifies the user:</text>
<text class="sm-nt" x="633" y="350">new sign-in or existing session</text>
</g>
<g class="sm-g sm-g4">
<text class="sm-main" x="515" y="394">HTML form: SAMLResponse</text>
<text class="sm-dim" x="515" y="410">RelayState, HTTP-POST binding</text>
<line class="sm-front" x1="636" y1="424" x2="394" y2="424" marker-end="url(#sm-m-front)"/>
<circle class="sm-badge sm-b-front" cx="650" cy="424" r="12"/><text class="sm-bt" x="650" y="428.5">4</text>
</g>
<g class="sm-g sm-g5">
<text class="sm-main" x="245" y="464">POST to the ACS URL</text>
<text class="sm-dim" x="245" y="480">SAMLResponse, RelayState</text>
<line class="sm-front" x1="366" y1="494" x2="124" y2="494" marker-end="url(#sm-m-front)"/>
<circle class="sm-badge sm-b-front" cx="380" cy="494" r="12"/><text class="sm-bt" x="380" y="498.5">5</text>
</g>
<g class="sm-g sm-g6">
<rect class="sm-note-good" x="10" y="528" width="247" height="65" rx="8"/>
<text class="sm-nt" x="134" y="549">SP validates signature, Audience,</text>
<text class="sm-nt" x="134" y="566">Recipient, InResponseTo, times,</text>
<text class="sm-nt" x="134" y="583">and replay check (POST)</text>
</g>
<g class="sm-g sm-g7">
<text class="sm-main" x="245" y="627">302 back to the page</text>
<text class="sm-dim" x="245" y="643">SP starts its own session</text>
<line class="sm-front" x1="124" y1="657" x2="366" y2="657" marker-end="url(#sm-m-front)"/>
<circle class="sm-badge sm-b-front" cx="110" cy="657" r="12"/><text class="sm-bt" x="110" y="661.5">6</text>
</g>
<g class="sm-g sm-g8">
<rect class="sm-note" x="509" y="691" width="241" height="48" rx="8"/>
<text class="sm-nt" x="630" y="712">IdP-initiated starts at step 4:</text>
<text class="sm-nt" x="630" y="729">no AuthnRequest, no InResponseTo</text>
</g>
<circle class="sm-pk sm-p0" cx="360" cy="138" r="5.5"/>
<circle class="sm-pk sm-p1" cx="130" cy="208" r="5.5"/>
<circle class="sm-pk sm-p2" cx="400" cy="278" r="5.5"/>
<circle class="sm-pk sm-p4" cx="630" cy="424" r="5.5"/>
<circle class="sm-pk sm-p5" cx="360" cy="494" r="5.5"/>
<circle class="sm-pk sm-p7" cx="130" cy="657" r="5.5"/>
<line class="sm-front" x1="40" y1="813" x2="70" y2="813"/>
<text class="sm-dim" x="78" y="817" style="text-anchor:start">every hop goes through the user's browser</text>
<rect class="sm-note-good" x="374" y="805" width="22" height="16" rx="4"/>
<text class="sm-dim" x="404" y="817" style="text-anchor:start">what the SP checks</text>
</svg>
</div>
</div>
<!-- /diagram:saml-flow -->

The numbers match the diagram. Every hop passes through the browser; steps 2 and 3 are one redirect (the app's instruction, then the browser following it), and steps 4 and 5 are one form POST (the IdP's form, then the browser submitting it). The IdP identifies Priya between steps 3 and 4.

The browser carries every message. In this flow the IdP and the app never talk to each other directly.

1. Priya opens Acme Tracker. The app finds no session for her (a *session* is the app remembering that she is signed in).
2. The app creates a sign-in request (an `AuthnRequest`, short for authentication request) and tells her browser to go to the IdP with it. It attaches `RelayState`, a short note the IdP must hand back unchanged, usually where Priya was heading.
3. The browser follows the instruction and asks the IdP.
4. The IdP identifies Priya: it asks her to sign in, or it recognises that she is already signed in at the IdP. Then it sends back the Response with the signed assertion, wrapped in a web form.
5. Her browser submits that form to the app's ACS URL.
6. The app checks the Response, creates its own session for her, and sends her to the page she wanted.

## What the app checks before letting her in

The browser is only a courier, so the app trusts the signature, not the courier. It checks that:

- the **signature** is valid for the certificate it holds for this IdP;
- the **audience** in the assertion equals the app's own entity ID, so the letter was meant for this app;
- the Response arrived at the **right address**: the ACS URL named inside it (`Recipient`);
- the time now is inside the assertion's **valid window** (`NotBefore` to `NotOnOrAfter`), allowing a small tolerance for clocks that differ. The standard gives no figure; Microsoft says a service "might allow" up to five minutes beyond the lifetime, so think of a few minutes, not an hour (a product's own setting may differ). A server whose clock is off by more than that fails this check;
- the Response answers the request the app sent (`InResponseTo`) and has **not been used before**. The standard requires the app to remember the IDs of assertions it has accepted, because an assertion works for whoever presents it.

## Who is she? NameID and attributes

Inside the assertion, the **NameID** is the label the IdP uses for Priya, and **attributes** are extra facts such as email, name and groups. The app matches the NameID to one of its accounts, and an admin chooses its format. An **email address** is easy to read but changes when someone changes their name; if the app filed her account under the old address, the new one looks like a stranger and she gets an empty second account. An **unspecified** NameID format promises nothing: the IdP sends whatever form it likes, and the app has to already know how to read it; it is not an instruction to look anyone up by name. A value built from her full name would change on a rename just as the email does. A **persistent** NameID is a random, meaningless label that the standard defines as opaque, at most 256 characters, and specific to one IdP and app pair, so it does not change when her name does. Using it as the account key is a design judgement, not a rule of the standard, which allows both. Attributes arrive only if an admin mapped them: an attribute that is not mapped is missing, and the app sees "no role". Microsoft Entra ID sends at most 150 groups in a SAML assertion and, above that, leaves the group list out altogether.

## Two ways in, and logging out

**SP-initiated** (above) starts at the app. **IdP-initiated** starts at the IdP, for example Priya clicking an app tile in the Okta dashboard: there is no sign-in request, so the Response cannot answer one. That is a weaker position, because the app cannot match the Response to a request it made, so it loses one of its checks. Whether to allow this way in is a design decision.

**Single Logout** (SLO) tries to sign a person out of every app at once. It is unreliable: every app must support it, and the standard even has a "partial logout" status for when the IdP could not reach everyone. Okta says its SLO switch signs the user out of that app and Okta, "but not out of other apps that are open". So ending someone's IdP session does not end their app sessions.

## What goes wrong, and who fixes it

| Symptom | Likely cause | Who changes what |
|---|---|---|
| "Assertion expired" or "not yet valid", often for everyone | One side's clock differs from the other by more than the allowed tolerance (a few minutes) | Fix the clock on the server that is wrong |
| One app fails for everyone starting on the same day | The IdP signing certificate reached its end date, or the IdP switched to a new one the app does not have | Give the app the new certificate or metadata |
| "Audience" or "entity ID" error | The two sides disagree on the app's entity ID | Copy it from the app's metadata instead of retyping it |
| "Recipient" or "ACS" error | The ACS URL on the IdP differs from the app's own | Correct the ACS URL on the IdP |
| Signed in, but no role or name | The attribute was not mapped, or the user is in too many groups for the list to be sent | IdP admin maps it or trims the groups |
| "User not found" or a second account | The NameID format or value differs from what the app expects | Agree one NameID format with the vendor |
| Endless bouncing between app and IdP (a redirect loop) | The app rejects the Response and starts over, and the IdP signs her straight back in | Read the app's own error for the real cause |

## Your task

Written from the docs, not run against a live tenant: ask the admin of one SAML app to show you its settings, and write down its entity ID, ACS URL, the end date of the IdP certificate, the NameID format, and whether Single Logout is on.

Run locally (this was run on 2026-10-06): a SAML message is only base64 text. This fragment is an invented sample, not from a real system.

```bash
echo 'PENvbmRpdGlvbnMgTm90QmVmb3JlPSIyMDI2LTEwLTA2VDA1OjE5OjMwWiIgTm90T25PckFmdGVyPSIyMDI2LTEwLTA2VDA1OjI1OjAwWiI+PEF1ZGllbmNlUmVzdHJpY3Rpb24+PEF1ZGllbmNlPmh0dHBzOi8vYXBwLmV4YW1wbGUuY29tL3NhbWw8L0F1ZGllbmNlPjwvQXVkaWVuY2VSZXN0cmljdGlvbj48L0NvbmRpdGlvbnM+' | base64 -d
```

```text
<Conditions NotBefore="2026-10-06T05:19:30Z" NotOnOrAfter="2026-10-06T05:25:00Z"><AudienceRestriction><Audience>https://app.example.com/saml</Audience></AudienceRestriction></Conditions>
```

Find the valid window and the audience in that output (the audience sits inside an `AudienceRestriction` tag). Next: lesson 3 covers OAuth 2.0.
