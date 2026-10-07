# SAML 2.0

You have configured SAML apps in Okta or Entra and read the XML when one broke. This lesson fixes the mechanism in your head so you can say which party is wrong when a ticket lands: what moves where, what the service provider (SP) must check, which of your settings feeds which check, and what fails at 2am. Facts checked 2026-10-06 against the OASIS SAML 2.0 core, bindings, profiles and metadata specifications (all dated 15 March 2005), Okta's SAML field reference and Microsoft Learn. Product field names come from those pages; I did not test them in a tenant.

## The flow, step by step

<!-- diagram:saml-flow -->
<div style="position:relative;margin:20px 0">
<input type="checkbox" id="sm-pause" class="sm-cb" /><label for="sm-pause" class="sm-btn"><span class="sm-off">Pause animation</span><span class="sm-on">Play animation</span></label>
<div class="sm-box" style="overflow-x:auto">
<svg class="sm-flow" viewBox="0 0 760 837" role="img" aria-labelledby="sm-t sm-d" style="width:100%;min-width:640px;max-width:800px;height:auto;display:block;margin:0 auto">
<title id="sm-t">SAML 2.0 Web Browser SSO, SP-initiated</title>
<desc id="sm-d">Three parties: the service provider (the app), the user's browser, and the identity provider. Every message travels through the browser. The browser asks the app for a page and has no session. The app answers with a redirect carrying an authentication request and optionally a RelayState value. The browser sends that request to the identity provider, which identifies the user either by a new sign-in or an existing session. The identity provider returns an HTML form carrying the signed SAML Response and the RelayState, which the browser posts to the app's assertion consumer service URL. The app validates the Response and redirects the browser to the original page with its own session. A final note says IdP-initiated sign-in starts at the form step, with no authentication request and therefore no InResponseTo value. The diagram highlights each step in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
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
<text class="sm-main" x="245" y="108">Request the protected page</text>
<text class="sm-dim" x="245" y="124">no session yet</text>
<line class="sm-front" x1="366" y1="138" x2="124" y2="138" marker-end="url(#sm-m-front)"/>
<circle class="sm-badge sm-b-front" cx="380" cy="138" r="12"/><text class="sm-bt" x="380" y="142.5">1</text>
</g>
<g class="sm-g sm-g1">
<text class="sm-main" x="245" y="178">302 or 303: AuthnRequest</text>
<text class="sm-dim" x="245" y="194">HTTP-Redirect binding</text>
<line class="sm-front" x1="124" y1="208" x2="366" y2="208" marker-end="url(#sm-m-front)"/>
<circle class="sm-badge sm-b-front" cx="110" cy="208" r="12"/><text class="sm-bt" x="110" y="212.5">2</text>
</g>
<g class="sm-g sm-g2">
<text class="sm-main" x="515" y="248">GET the SSO URL</text>
<text class="sm-dim" x="515" y="264">SAMLRequest, optional RelayState</text>
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
<text class="sm-main" x="245" y="627">Redirect back to the page</text>
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

The numbers match the diagram. Every hop passes through the browser; steps 2 and 3 are one redirect, and steps 4 and 5 are one form POST (the IdP identifies the user between 3 and 4).

The browser carries every message; in this flow the IdP and SP never talk to each other directly.

1. The user requests a resource and the SP finds no session.
2. The SP replies with a 302 or 303 whose `Location` is the IdP's SSO URL plus `SAMLRequest` (the `AuthnRequest`) and optionally `RelayState`. This is the HTTP-Redirect binding: the XML is DEFLATE-compressed, base64-encoded, then URL-encoded, and a signed request carries its signature in separate `SigAlg` and `Signature` query parameters.
3. The browser issues a GET to the IdP.
4. The IdP identifies the user, by a new sign-in or by reusing an existing IdP session (`ForceAuthn="true"` in the request obliges a fresh sign-in; Okta's switch for it is "Honor Force Authentication"). It then returns an HTML form carrying `SAMLResponse` (base64 XML, not compressed) and the echoed `RelayState`. This is the HTTP-POST binding. The profile forbids HTTP-Redirect for the Response because it "will typically exceed the URL length" browsers allow.
5. The browser POSTs that form to the SP's ACS (assertion consumer service) URL.
6. The SP validates the Response, starts its own session by whatever mechanism it chooses, and redirects the user to the original page.

A third binding, HTTP-Artifact, sends only a short `SAMLart` reference through the browser; the SP then fetches the real Response from the IdP over a direct back-channel SOAP call, so it needs a network path to the IdP (and, my inference from the design rather than a stated rule, the IdP must keep the real Response available until the artifact is fetched).

## What the Response carries and what the SP checks

A `Response` has an `ID`, a `Status` and, only on success, one or more `Assertion` elements. It normally also carries an `Issuer`, a `Destination` and, when it answers a request, `InResponseTo`; an error Response must not contain an assertion. The assertion is the part that matters:

<!-- diagram:saml-response-anatomy -->
<div style="position:relative;margin:20px 0">
<input type="checkbox" id="smr-pause" class="smr-cb" /><label for="smr-pause" class="smr-btn"><span class="smr-off">Pause animation</span><span class="smr-on">Play animation</span></label>
<div class="smr-box" style="overflow-x:auto">
<svg class="smr-flow" viewBox="0 0 760 560" role="img" aria-labelledby="smr-t smr-d" style="width:100%;min-width:640px;max-width:800px;height:auto;display:block;margin:0 auto">
<title id="smr-t">Anatomy of a SAML Response and what the SP checks in each part</title>
<desc id="smr-d">A nested diagram. The Response, which carries an ID, Status, Issuer, Destination and InResponseTo, contains the Assertion on success. The Assertion contains the Issuer, a Signature, the Subject with its NameID, the bearer SubjectConfirmationData, the Conditions, the AuthnStatement and the AttributeStatement. Numbered callouts say what the service provider verifies in each part. The Response holds one or more Assertions on success and none on error. Accepted assertion IDs are remembered until they expire, which the POST binding makes a MUST. The issuer is the IdP it holds metadata for. The signature is valid with a key from the IdP's metadata. The NameID maps to exactly one local account. Recipient equals the ACS URL, the assertion has not expired, and InResponseTo equals the request's ID when the Response answers a request. The time window holds, with the skew allowance the SP chooses, and the SP's own entity ID is one of the Audience values. SessionIndex is needed only for Single Logout. The attributes the SP needs are present. The diagram highlights each part in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
<style>
.smr-box{fill:var(--panel);stroke:var(--border-strong);stroke-width:1.5}
.smr-hot{fill:var(--panel);stroke:var(--accent);stroke-width:2.5}
.smr-ttl{fill:var(--text);font:600 15px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.smr-sub{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.smr-life{stroke:var(--border-strong);stroke-width:1.5;stroke-dasharray:4 5}
.smr-front{stroke:var(--accent);stroke-width:2;fill:none}
.smr-back{stroke:var(--muted);stroke-width:2;stroke-dasharray:7 5;fill:none}
.smr-bad{stroke:var(--bad);stroke-width:2;fill:none}
.smr-main{fill:var(--text);font:600 13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.smr-badt{fill:var(--bad-text)}
.smr-dim{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.smr-badge{fill:var(--accent)}
.smr-b-back{fill:var(--muted)}
.smr-b-bad{fill:var(--bad)}
.smr-b-good{fill:var(--good)}
.smr-bt{fill:var(--on-accent);font:700 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.smr-note{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.smr-note-good{fill:var(--good-bg);stroke:var(--good);stroke-width:1.5}
.smr-note-bad{fill:var(--bad-bg);stroke:var(--bad);stroke-width:1.5}
.smr-nt{fill:var(--body);font:12.5px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.smr-nest{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.smr-row{fill:var(--raised);stroke:var(--border-strong);stroke-width:1}
.smr-ttlL{fill:var(--text);font:600 14px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.smr-subL{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.smr-dimL{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.smr-dimR{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:end}
.smr-conn{stroke:var(--accent);stroke-width:1.5;fill:none}
.smr-edge{stroke:var(--border-strong);stroke-width:1.75;fill:none}
.smr-hl{fill:none;stroke:var(--accent);stroke-width:3}
.smr-hle{stroke:var(--accent);stroke-width:3;fill:none}
.smr-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:24s;animation-timing-function:linear;animation-iteration-count:infinite}
.smr-pk.smr-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.smr-pk.smr-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.smr-g{opacity:.45;animation-duration:24s;animation-timing-function:linear;animation-iteration-count:infinite}
.smr-h{opacity:0;animation-duration:24s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.smr-flow:hover .smr-g,svg.smr-flow:hover .smr-pk,svg.smr-flow:hover .smr-h{animation-play-state:paused}
.smr-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.smr-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.smr-btn:hover{background:var(--hover)}
.smr-cb:focus-visible + .smr-btn{outline:2px solid var(--accent);outline-offset:2px}
.smr-cb:checked + .smr-btn .smr-off,.smr-cb:not(:checked) + .smr-btn .smr-on{display:none}
.smr-cb:checked ~ .smr-box .smr-g,.smr-cb:checked ~ .smr-box .smr-pk,.smr-cb:checked ~ .smr-box .smr-h{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.smr-g{animation:none;opacity:1}.smr-pk{animation:none;display:none}.smr-h{animation:none;opacity:0}.smr-btn{display:none}}
@keyframes smr-g0{0%{opacity:1}11.111%{opacity:1}11.121%,100%{opacity:.45}}
@keyframes smr-h0{0%{opacity:1}11.111%{opacity:1}11.121%,100%{opacity:0}}
.smr-g0{animation-name:smr-g0}.smr-h0{animation-name:smr-h0}
@keyframes smr-g1{0%,11.101%{opacity:.45}11.111%{opacity:1}22.222%{opacity:1}22.232%,100%{opacity:.45}}
@keyframes smr-h1{0%,11.101%{opacity:0}11.111%{opacity:1}22.222%{opacity:1}22.232%,100%{opacity:0}}
.smr-g1{animation-name:smr-g1}.smr-h1{animation-name:smr-h1}
@keyframes smr-g2{0%,22.212%{opacity:.45}22.222%{opacity:1}33.333%{opacity:1}33.343%,100%{opacity:.45}}
@keyframes smr-h2{0%,22.212%{opacity:0}22.222%{opacity:1}33.333%{opacity:1}33.343%,100%{opacity:0}}
.smr-g2{animation-name:smr-g2}.smr-h2{animation-name:smr-h2}
@keyframes smr-g3{0%,33.323%{opacity:.45}33.333%{opacity:1}44.444%{opacity:1}44.454%,100%{opacity:.45}}
@keyframes smr-h3{0%,33.323%{opacity:0}33.333%{opacity:1}44.444%{opacity:1}44.454%,100%{opacity:0}}
.smr-g3{animation-name:smr-g3}.smr-h3{animation-name:smr-h3}
@keyframes smr-g4{0%,44.434%{opacity:.45}44.444%{opacity:1}55.556%{opacity:1}55.566%,100%{opacity:.45}}
@keyframes smr-h4{0%,44.434%{opacity:0}44.444%{opacity:1}55.556%{opacity:1}55.566%,100%{opacity:0}}
.smr-g4{animation-name:smr-g4}.smr-h4{animation-name:smr-h4}
@keyframes smr-g5{0%,55.546%{opacity:.45}55.556%{opacity:1}66.667%{opacity:1}66.677%,100%{opacity:.45}}
@keyframes smr-h5{0%,55.546%{opacity:0}55.556%{opacity:1}66.667%{opacity:1}66.677%,100%{opacity:0}}
.smr-g5{animation-name:smr-g5}.smr-h5{animation-name:smr-h5}
@keyframes smr-g6{0%,66.657%{opacity:.45}66.667%{opacity:1}77.778%{opacity:1}77.788%,100%{opacity:.45}}
@keyframes smr-h6{0%,66.657%{opacity:0}66.667%{opacity:1}77.778%{opacity:1}77.788%,100%{opacity:0}}
.smr-g6{animation-name:smr-g6}.smr-h6{animation-name:smr-h6}
@keyframes smr-g7{0%,77.768%{opacity:.45}77.778%{opacity:1}88.889%{opacity:1}88.899%,100%{opacity:.45}}
@keyframes smr-h7{0%,77.768%{opacity:0}77.778%{opacity:1}88.889%{opacity:1}88.899%,100%{opacity:0}}
.smr-g7{animation-name:smr-g7}.smr-h7{animation-name:smr-h7}
@keyframes smr-g8{0%,88.879%{opacity:.45}88.889%{opacity:1}100%{opacity:1}100.01%,100%{opacity:.45}}
@keyframes smr-h8{0%,88.879%{opacity:0}88.889%{opacity:1}100%{opacity:1}100.01%,100%{opacity:0}}
.smr-g8{animation-name:smr-g8}.smr-h8{animation-name:smr-h8}
</style>
<defs>
<marker id="smr-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="smr-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="smr-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<rect class="smr-box" x="14" y="16" width="440" height="486" rx="9"/><text class="smr-ttlL" x="28" y="37">Response</text><text class="smr-subL" x="28" y="54">ID, Status, Issuer, Destination, InResponseTo</text>
<rect class="smr-nest" x="26" y="62" width="416" height="428" rx="9"/><text class="smr-ttlL" x="40" y="83">Assertion</text><text class="smr-subL" x="40" y="100">the part that matters</text>
<rect class="smr-nest" x="38" y="108" width="392" height="46" rx="9"/><text class="smr-ttlL" x="52" y="129">Issuer</text><text class="smr-subL" x="52" y="146">the IdP's entity ID</text>
<rect class="smr-nest" x="38" y="162" width="392" height="46" rx="9"/><text class="smr-ttlL" x="52" y="183">Signature</text><text class="smr-subL" x="52" y="200">enveloped, URI="#ID"</text>
<rect class="smr-nest" x="38" y="216" width="392" height="46" rx="9"/><text class="smr-ttlL" x="52" y="237">Subject / NameID</text><text class="smr-subL" x="52" y="254">who the user is</text>
<rect class="smr-nest" x="38" y="270" width="392" height="46" rx="9"/><text class="smr-ttlL" x="52" y="291">SubjectConfirmationData</text><text class="smr-subL" x="52" y="308">Recipient, NotOnOrAfter, InResponseTo</text>
<rect class="smr-nest" x="38" y="324" width="392" height="46" rx="9"/><text class="smr-ttlL" x="52" y="345">Conditions</text><text class="smr-subL" x="52" y="362">NotBefore, NotOnOrAfter, AudienceRestriction</text>
<rect class="smr-nest" x="38" y="378" width="392" height="46" rx="9"/><text class="smr-ttlL" x="52" y="399">AuthnStatement</text><text class="smr-subL" x="52" y="416">when and how; SessionIndex</text>
<rect class="smr-nest" x="38" y="432" width="392" height="46" rx="9"/><text class="smr-ttlL" x="52" y="453">AttributeStatement</text><text class="smr-subL" x="52" y="470">name/value pairs</text>
<g class="smr-g smr-g0">
<path class="smr-conn" d="M454,33 L462,33 L462,34 L470,34" marker-end="url(#smr-m-front)"/>
<rect class="smr-note" x="484" y="10" width="262" height="48" rx="8"/>
<text class="smr-nt" x="615" y="31">On success it holds one or more</text>
<text class="smr-nt" x="615" y="48">Assertions; an error holds none</text>
<circle class="smr-badge smr-b-front" cx="484" cy="34" r="12"/><text class="smr-bt" x="484" y="38.5">1</text>
</g>
<g class="smr-g smr-g1">
<path class="smr-conn" d="M442,79 L466,79 L466,92 L470,92" marker-end="url(#smr-m-front)"/>
<rect class="smr-note-good" x="484" y="68" width="262" height="48" rx="8"/>
<text class="smr-nt" x="615" y="89">Keep accepted IDs until they expire</text>
<text class="smr-nt" x="615" y="106">(POST binding: MUST, 4.1.4.5)</text>
<circle class="smr-badge smr-b-good" cx="484" cy="92" r="12"/><text class="smr-bt" x="484" y="96.5">2</text>
</g>
<g class="smr-g smr-g2">
<path class="smr-conn" d="M430,125 L470,125 L470,142 L470,142" marker-end="url(#smr-m-front)"/>
<rect class="smr-note-good" x="484" y="126" width="262" height="31" rx="8"/>
<text class="smr-nt" x="615" y="147">It is the IdP I hold metadata for</text>
<circle class="smr-badge smr-b-good" cx="484" cy="142" r="12"/><text class="smr-bt" x="484" y="146.0">3</text>
</g>
<g class="smr-g smr-g3">
<path class="smr-conn" d="M430,179 L474,179 L474,191 L470,191" marker-end="url(#smr-m-front)"/>
<rect class="smr-note-good" x="484" y="167" width="262" height="48" rx="8"/>
<text class="smr-nt" x="615" y="188">Valid with a key from the IdP's</text>
<text class="smr-nt" x="615" y="205">metadata</text>
<circle class="smr-badge smr-b-good" cx="484" cy="191" r="12"/><text class="smr-bt" x="484" y="195.5">4</text>
</g>
<g class="smr-g smr-g4">
<path class="smr-conn" d="M430,233 L462,233 L462,240 L470,240" marker-end="url(#smr-m-front)"/>
<rect class="smr-note-good" x="484" y="225" width="262" height="31" rx="8"/>
<text class="smr-nt" x="615" y="246">Maps to exactly one local account</text>
<circle class="smr-badge smr-b-good" cx="484" cy="240" r="12"/><text class="smr-bt" x="484" y="245.0">5</text>
</g>
<g class="smr-g smr-g5">
<path class="smr-conn" d="M430,287 L466,287 L466,298 L470,298" marker-end="url(#smr-m-front)"/>
<rect class="smr-note-good" x="484" y="266" width="262" height="65" rx="8"/>
<text class="smr-nt" x="615" y="287">Recipient = ACS URL it arrived at;</text>
<text class="smr-nt" x="615" y="304">not expired; InResponseTo = request</text>
<text class="smr-nt" x="615" y="321">ID, when it answers a request</text>
<circle class="smr-badge smr-b-good" cx="484" cy="298" r="12"/><text class="smr-bt" x="484" y="303.0">6</text>
</g>
<g class="smr-g smr-g6">
<path class="smr-conn" d="M430,341 L470,341 L470,365 L470,365" marker-end="url(#smr-m-front)"/>
<rect class="smr-note-good" x="484" y="341" width="262" height="48" rx="8"/>
<text class="smr-nt" x="615" y="362">Now is inside the window (plus skew);</text>
<text class="smr-nt" x="615" y="379">my entity ID is an Audience</text>
<circle class="smr-badge smr-b-good" cx="484" cy="365" r="12"/><text class="smr-bt" x="484" y="369.5">7</text>
</g>
<g class="smr-g smr-g7">
<path class="smr-conn" d="M430,395 L474,395 L474,423 L470,423" marker-end="url(#smr-m-front)"/>
<rect class="smr-note" x="484" y="399" width="262" height="48" rx="8"/>
<text class="smr-nt" x="615" y="420">SessionIndex is needed only for</text>
<text class="smr-nt" x="615" y="437">Single Logout</text>
<circle class="smr-badge smr-b-front" cx="484" cy="423" r="12"/><text class="smr-bt" x="484" y="427.5">8</text>
</g>
<g class="smr-g smr-g8">
<path class="smr-conn" d="M430,449 L462,449 L462,472 L470,472" marker-end="url(#smr-m-front)"/>
<rect class="smr-note-good" x="484" y="457" width="262" height="31" rx="8"/>
<text class="smr-nt" x="615" y="478">The attributes I need are present</text>
<circle class="smr-badge smr-b-good" cx="484" cy="472" r="12"/><text class="smr-bt" x="484" y="477.0">9</text>
</g>
<g class="smr-h smr-h0">
<rect class="smr-hl" x="14" y="16" width="440" height="486" rx="9"/>
</g>
<g class="smr-h smr-h1">
<rect class="smr-hl" x="26" y="62" width="416" height="428" rx="9"/>
</g>
<g class="smr-h smr-h2">
<rect class="smr-hl" x="38" y="108" width="392" height="46" rx="9"/>
</g>
<g class="smr-h smr-h3">
<rect class="smr-hl" x="38" y="162" width="392" height="46" rx="9"/>
</g>
<g class="smr-h smr-h4">
<rect class="smr-hl" x="38" y="216" width="392" height="46" rx="9"/>
</g>
<g class="smr-h smr-h5">
<rect class="smr-hl" x="38" y="270" width="392" height="46" rx="9"/>
</g>
<g class="smr-h smr-h6">
<rect class="smr-hl" x="38" y="324" width="392" height="46" rx="9"/>
</g>
<g class="smr-h smr-h7">
<rect class="smr-hl" x="38" y="378" width="392" height="46" rx="9"/>
</g>
<g class="smr-h smr-h8">
<rect class="smr-hl" x="38" y="432" width="392" height="46" rx="9"/>
</g>
<rect class="smr-note" x="40" y="528" width="22" height="16" rx="4"/>
<text class="smr-dim" x="70" y="540" style="text-anchor:start">context</text>
<rect class="smr-note-good" x="148" y="528" width="22" height="16" rx="4"/>
<text class="smr-dim" x="178" y="540" style="text-anchor:start">what the SP verifies</text>
</svg>
</div>
</div>
<!-- /diagram:saml-response-anatomy -->

Read it from the outside in. Each green part is something the SP verifies; callouts 3 to 9 are the rows of the table below, callout 2 is the replay rule in the paragraph after it, and callout 1 only says what a Response holds. `AuthnStatement` is not green because its `SessionIndex` is needed only for Single Logout.

| Element | Says | The SP verifies |
|---|---|---|
| `Issuer` | the IdP's entity ID | it is the IdP it holds metadata for |
| `Signature` | enveloped XML signature over the element | valid with a key from the IdP's metadata |
| `Subject/NameID` | who the user is | maps to exactly one local account |
| bearer `SubjectConfirmationData` | `Recipient`, `NotOnOrAfter`, `InResponseTo` | `Recipient` equals the ACS URL the POST arrived at; not expired; `InResponseTo` equals the ID of its `AuthnRequest` |
| `Conditions` | `NotBefore`, `NotOnOrAfter`, `AudienceRestriction` | now is inside the window, with whatever clock-skew allowance the SP chooses; its own entity ID is one of the `Audience` values |
| `AuthnStatement` | when and how the user authenticated; `SessionIndex` | `SessionIndex` is needed only for Single Logout |
| `AttributeStatement` | name/value pairs | the ones it needs are present |

The `Conditions` times are optional in the schema, but the bearer confirmation for Web SSO must carry `NotOnOrAfter` (and `Recipient`) and must not carry `NotBefore`, so a bearer assertion always has an expiry. And because a bearer assertion is valid for whoever presents it, the SP must keep the IDs of assertions it has accepted until they would expire; for the POST binding the profile makes that a MUST (section 4.1.4.5).

**Signing: Response, Assertion, or both.** With the POST binding the profile says the enclosed assertions MUST be signed (4.1.4.5); signing the Response too is optional. Okta shows two settings, "Response" and "Assertion Signature", and an SP's metadata can state `WantAssertionsSigned`. The core spec also lets an unsigned assertion "inherit" the signature of a signed Response that encloses it (core 5.3), so implementations can differ on what they accept. If a vendor reports "signature not found" and you sign only the Response, switch Assertion Signature on. The signature is enveloped, and its one `ds:Reference` points at the signed element's `ID` as `URI="#ID"`.

**Encryption** (`EncryptedAssertion`) hides the assertion from the browser that carries it. The POST binding gives no confidentiality from the user agent, and a signature proves origin without hiding content. Okta's "Assertion Encryption" uses an encryption certificate you upload. If the assertion is also signed, the signature is calculated first and sits inside the encrypted element, so the SP must decrypt before it can verify.

## Entities, metadata and certificates

Each side has an `entityID`, a URI of at most 1,024 characters (a URL on your own domain is recommended; it need not resolve). Metadata is the XML each side publishes: the IdP's `SingleSignOnService` locations per binding, the SP's `AssertionConsumerService` locations (with `index` and `isDefault`), `NameIDFormat` values, and `KeyDescriptor` elements marked `use="signing"` or `use="encryption"`. A root metadata element must carry `validUntil` or `cacheDuration`, the signal for when to refetch. A manual upload never refreshes; a metadata URL can.

<!-- diagram:saml-metadata -->
<div style="position:relative;margin:20px 0">
<input type="checkbox" id="l02b-pause" class="l02b-cb" /><label for="l02b-pause" class="l02b-btn"><span class="l02b-off">Pause animation</span><span class="l02b-on">Play animation</span></label>
<div class="l02b-box" style="overflow-x:auto">
<svg class="l02b-flow" viewBox="0 0 760 557" role="img" aria-labelledby="l02b-t l02b-d" style="width:100%;min-width:640px;max-width:800px;height:auto;display:block;margin:0 auto">
<title id="l02b-t">What each side's metadata lists, and where those values show up</title>
<desc id="l02b-d">Two parties: the service provider and the identity provider. The IdP's metadata, uploaded or fetched from a URL, carries its entityID, its SingleSignOnService locations and its signing KeyDescriptor. At the SP the entityID is the Issuer it must recognise and the signing key is a key the signature must be valid with. A manual upload never refreshes; a metadata URL can, and validUntil or cacheDuration says when to refetch. The SP's metadata carries its entityID and its AssertionConsumerService, the ACS URL. At the IdP the SP entity ID feeds the Audience URI field and the ACS URL is the Single sign-on URL, from which Recipient and Destination default. The diagram highlights each step in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
<style>
.l02b-box{fill:var(--panel);stroke:var(--border-strong);stroke-width:1.5}
.l02b-hot{fill:var(--panel);stroke:var(--accent);stroke-width:2.5}
.l02b-ttl{fill:var(--text);font:600 15px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l02b-sub{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l02b-life{stroke:var(--border-strong);stroke-width:1.5;stroke-dasharray:4 5}
.l02b-front{stroke:var(--accent);stroke-width:2;fill:none}
.l02b-back{stroke:var(--muted);stroke-width:2;stroke-dasharray:7 5;fill:none}
.l02b-bad{stroke:var(--bad);stroke-width:2;fill:none}
.l02b-main{fill:var(--text);font:600 13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l02b-badt{fill:var(--bad-text)}
.l02b-dim{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l02b-badge{fill:var(--accent)}
.l02b-b-back{fill:var(--muted)}
.l02b-b-bad{fill:var(--bad)}
.l02b-b-good{fill:var(--good)}
.l02b-bt{fill:var(--on-accent);font:700 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l02b-note{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l02b-note-good{fill:var(--good-bg);stroke:var(--good);stroke-width:1.5}
.l02b-note-bad{fill:var(--bad-bg);stroke:var(--bad);stroke-width:1.5}
.l02b-nt{fill:var(--body);font:12.5px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l02b-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:18s;animation-timing-function:linear;animation-iteration-count:infinite}
.l02b-pk.l02b-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.l02b-pk.l02b-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.l02b-g{opacity:.45;animation-duration:18s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.l02b-flow:hover .l02b-g,svg.l02b-flow:hover .l02b-pk{animation-play-state:paused}
.l02b-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.l02b-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.l02b-btn:hover{background:var(--hover)}
.l02b-cb:focus-visible + .l02b-btn{outline:2px solid var(--accent);outline-offset:2px}
.l02b-cb:checked + .l02b-btn .l02b-off,.l02b-cb:not(:checked) + .l02b-btn .l02b-on{display:none}
.l02b-cb:checked ~ .l02b-box .l02b-g,.l02b-cb:checked ~ .l02b-box .l02b-pk{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.l02b-g{animation:none;opacity:1}.l02b-pk{animation:none;display:none}.l02b-btn{display:none}}
@keyframes l02b-g0{0%{opacity:1}20%{opacity:1}20.01%,100%{opacity:.45}}
@keyframes l02b-p0{0%,-0.01%{opacity:0;transform:translateX(0)}0%{opacity:1;transform:translateX(0)}20%{opacity:1;transform:translateX(-506px)}20.01%,100%{opacity:0;transform:translateX(-506px)}}
.l02b-g0{animation-name:l02b-g0}.l02b-p0{animation-name:l02b-p0}
@keyframes l02b-g1{0%,19.99%{opacity:.45}20%{opacity:1}40%{opacity:1}40.01%,100%{opacity:.45}}
.l02b-g1{animation-name:l02b-g1}
@keyframes l02b-g2{0%,39.99%{opacity:.45}40%{opacity:1}60%{opacity:1}60.01%,100%{opacity:.45}}
.l02b-g2{animation-name:l02b-g2}
@keyframes l02b-g3{0%,59.99%{opacity:.45}60%{opacity:1}80%{opacity:1}80.01%,100%{opacity:.45}}
@keyframes l02b-p3{0%,59.99%{opacity:0;transform:translateX(0)}60%{opacity:1;transform:translateX(0)}80%{opacity:1;transform:translateX(506px)}80.01%,100%{opacity:0;transform:translateX(506px)}}
.l02b-g3{animation-name:l02b-g3}.l02b-p3{animation-name:l02b-p3}
@keyframes l02b-g4{0%,79.99%{opacity:.45}80%{opacity:1}100%{opacity:1}100.01%,100%{opacity:.45}}
.l02b-g4{animation-name:l02b-g4}
</style>
<defs>
<marker id="l02b-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="l02b-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="l02b-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<line class="l02b-life" x1="110" y1="72" x2="110" y2="505"/>
<line class="l02b-life" x1="650" y1="72" x2="650" y2="505"/>
<rect class="l02b-hot" x="20" y="10" width="180" height="62" rx="10"/><text class="l02b-ttl" x="110" y="36">Service provider</text><text class="l02b-sub" x="110" y="56">the app (SP)</text>
<rect class="l02b-box" x="560" y="10" width="180" height="62" rx="10"/><text class="l02b-ttl" x="650" y="36">Identity provider</text><text class="l02b-sub" x="650" y="56">Okta, Entra ID (IdP)</text>
<g class="l02b-g l02b-g0">
<text class="l02b-main" x="380" y="108">IdP metadata (an upload, or fetched from a URL)</text>
<text class="l02b-dim" x="380" y="124">entityID, SingleSignOnService, KeyDescriptor use="signing"</text>
<line class="l02b-front" x1="636" y1="138" x2="124" y2="138" marker-end="url(#l02b-m-front)"/>
</g>
<g class="l02b-g l02b-g1">
<rect class="l02b-note-good" x="10" y="172" width="333" height="48" rx="8"/>
<text class="l02b-nt" x="176" y="193">Issuer: it is the IdP I hold metadata for</text>
<text class="l02b-nt" x="176" y="210">Signature: valid with a key from this metadata</text>
</g>
<g class="l02b-g l02b-g2">
<rect class="l02b-note" x="10" y="248" width="320" height="48" rx="8"/>
<text class="l02b-nt" x="170" y="269">A manual upload never refreshes; a URL can</text>
<text class="l02b-nt" x="170" y="286">validUntil or cacheDuration: when to refetch</text>
</g>
<g class="l02b-g l02b-g3">
<text class="l02b-main" x="380" y="330">SP metadata</text>
<text class="l02b-dim" x="380" y="346">entityID, AssertionConsumerService (the ACS URL)</text>
<line class="l02b-front" x1="124" y1="360" x2="636" y2="360" marker-end="url(#l02b-m-front)"/>
</g>
<g class="l02b-g l02b-g4">
<rect class="l02b-note-good" x="443" y="394" width="307" height="65" rx="8"/>
<text class="l02b-nt" x="596" y="415">Audience URI (SP Entity ID) feeds Audience</text>
<text class="l02b-nt" x="596" y="432">Single sign-on URL is the ACS URL</text>
<text class="l02b-nt" x="596" y="449">Recipient and Destination default to it</text>
</g>
<circle class="l02b-pk l02b-p0" cx="630" cy="138" r="5.5"/>
<circle class="l02b-pk l02b-p3" cx="130" cy="360" r="5.5"/>
<line class="l02b-front" x1="40" y1="533" x2="70" y2="533"/>
<text class="l02b-dim" x="78" y="537" style="text-anchor:start">metadata moving</text>
<rect class="l02b-note-good" x="208" y="525" width="22" height="16" rx="4"/>
<text class="l02b-dim" x="238" y="537" style="text-anchor:start">where it ends up</text>
</svg>
</div>
</div>
<!-- /diagram:saml-metadata -->

The upper arrow is the IdP's metadata reaching the SP, the lower is the SP's reaching the IdP, and the green notes say which check or Okta field each listed value shows up in.

Certificates expire, and metadata is how a new one reaches the SP. Entra's default self-signed SAML certificate lasts three years and Entra emails at 60, 30 and 7 days before expiry. Microsoft recommends that an SP accept a primary and a secondary signing certificate and refetch metadata at least every 24 hours. Safe order: generate the new certificate while inactive, let the SP learn it, activate it, then retire the old one. Entra also says an app that does not check certificate expiry keeps accepting an expired one, so a silent expiry can mean the check is missing, not that rotation worked.

<!-- diagram:saml-cert-rotation -->
<div style="position:relative;margin:20px 0">
<input type="checkbox" id="smc-pause" class="smc-cb" /><label for="smc-pause" class="smc-btn"><span class="smc-off">Pause animation</span><span class="smc-on">Play animation</span></label>
<div class="smc-box" style="overflow-x:auto">
<svg class="smc-flow" viewBox="0 0 760 210" role="img" aria-labelledby="smc-t smc-d" style="width:100%;min-width:640px;max-width:800px;height:auto;display:block;margin:0 auto">
<title id="smc-t">Rotating a SAML signing certificate safely</title>
<desc id="smc-d">Four stages in a safe order. First only the old certificate exists: the IdP signs with it and the SP trusts it. Then the new certificate is generated while inactive and the SP learns it from metadata, so the SP knows both. Then the new certificate is activated: the IdP signs with the new one and the SP still knows both. Finally the old certificate is retired. The diagram highlights each stage in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
<style>
.smc-box{fill:var(--panel);stroke:var(--border-strong);stroke-width:1.5}
.smc-hot{fill:var(--panel);stroke:var(--accent);stroke-width:2.5}
.smc-ttl{fill:var(--text);font:600 15px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.smc-sub{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.smc-life{stroke:var(--border-strong);stroke-width:1.5;stroke-dasharray:4 5}
.smc-front{stroke:var(--accent);stroke-width:2;fill:none}
.smc-back{stroke:var(--muted);stroke-width:2;stroke-dasharray:7 5;fill:none}
.smc-bad{stroke:var(--bad);stroke-width:2;fill:none}
.smc-main{fill:var(--text);font:600 13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.smc-badt{fill:var(--bad-text)}
.smc-dim{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.smc-badge{fill:var(--accent)}
.smc-b-back{fill:var(--muted)}
.smc-b-bad{fill:var(--bad)}
.smc-b-good{fill:var(--good)}
.smc-bt{fill:var(--on-accent);font:700 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.smc-note{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.smc-note-good{fill:var(--good-bg);stroke:var(--good);stroke-width:1.5}
.smc-note-bad{fill:var(--bad-bg);stroke:var(--bad);stroke-width:1.5}
.smc-nt{fill:var(--body);font:12.5px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.smc-nest{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.smc-row{fill:var(--raised);stroke:var(--border-strong);stroke-width:1}
.smc-ttlL{fill:var(--text);font:600 14px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.smc-subL{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.smc-dimL{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.smc-dimR{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:end}
.smc-conn{stroke:var(--accent);stroke-width:1.5;fill:none}
.smc-edge{stroke:var(--border-strong);stroke-width:1.75;fill:none}
.smc-hl{fill:none;stroke:var(--accent);stroke-width:3}
.smc-hle{stroke:var(--accent);stroke-width:3;fill:none}
.smc-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:14s;animation-timing-function:linear;animation-iteration-count:infinite}
.smc-pk.smc-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.smc-pk.smc-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.smc-g{opacity:.45;animation-duration:14s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.smc-flow:hover .smc-g,svg.smc-flow:hover .smc-pk{animation-play-state:paused}
.smc-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.smc-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.smc-btn:hover{background:var(--hover)}
.smc-cb:focus-visible + .smc-btn{outline:2px solid var(--accent);outline-offset:2px}
.smc-cb:checked + .smc-btn .smc-off,.smc-cb:not(:checked) + .smc-btn .smc-on{display:none}
.smc-cb:checked ~ .smc-box .smc-g,.smc-cb:checked ~ .smc-box .smc-pk{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.smc-g{animation:none;opacity:1}.smc-pk{animation:none;display:none}.smc-btn{display:none}}
@keyframes smc-g0{0%{opacity:1}25%{opacity:1}25.01%,100%{opacity:.45}}
@keyframes smc-p0{0%,-0.01%{opacity:0;transform:translateX(0)}0%{opacity:1;transform:translateX(0)}25%{opacity:1;transform:translateX(58px)}25.01%,100%{opacity:0;transform:translateX(58px)}}
.smc-g0{animation-name:smc-g0}.smc-p0{animation-name:smc-p0}
@keyframes smc-g1{0%,24.99%{opacity:.45}25%{opacity:1}50%{opacity:1}50.01%,100%{opacity:.45}}
@keyframes smc-p1{0%,24.99%{opacity:0;transform:translateX(0)}25%{opacity:1;transform:translateX(0)}50%{opacity:1;transform:translateX(58px)}50.01%,100%{opacity:0;transform:translateX(58px)}}
.smc-g1{animation-name:smc-g1}.smc-p1{animation-name:smc-p1}
@keyframes smc-g2{0%,49.99%{opacity:.45}50%{opacity:1}75%{opacity:1}75.01%,100%{opacity:.45}}
@keyframes smc-p2{0%,49.99%{opacity:0;transform:translateX(0)}50%{opacity:1;transform:translateX(0)}75%{opacity:1;transform:translateX(58px)}75.01%,100%{opacity:0;transform:translateX(58px)}}
.smc-g2{animation-name:smc-g2}.smc-p2{animation-name:smc-p2}
@keyframes smc-g3{0%,74.99%{opacity:.45}75%{opacity:1}100%{opacity:1}100.01%,100%{opacity:.45}}
.smc-g3{animation-name:smc-g3}
</style>
<defs>
<marker id="smc-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="smc-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="smc-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<g class="smc-g smc-g0">
<rect class="smc-box" x="14" y="40" width="123" height="110" rx="10"/>
<text class="smc-ttl" x="76" y="67">Old cert only</text>
<text class="smc-sub" x="76" y="87">steady state</text>
<text class="smc-nt" x="76" y="114">IdP signs: old</text>
<text class="smc-nt" x="76" y="131">SP knows: old</text>
<text class="smc-main" x="177" y="64">generate</text>
<line class="smc-front" x1="145" y1="70" x2="209" y2="70" marker-end="url(#smc-m-front)"/>
</g>
<g class="smc-g smc-g1">
<rect class="smc-note-good" x="217" y="40" width="123" height="110" rx="10"/>
<text class="smc-ttl" x="278" y="67">New inactive</text>
<text class="smc-sub" x="278" y="87">SP learns it</text>
<text class="smc-nt" x="278" y="114">IdP signs: old</text>
<text class="smc-nt" x="278" y="131">SP knows: both</text>
<text class="smc-main" x="380" y="64">activate</text>
<line class="smc-front" x1="348" y1="70" x2="412" y2="70" marker-end="url(#smc-m-front)"/>
</g>
<g class="smc-g smc-g2">
<rect class="smc-note-good" x="420" y="40" width="123" height="110" rx="10"/>
<text class="smc-ttl" x="482" y="67">New active</text>
<text class="smc-sub" x="482" y="87">old still known</text>
<text class="smc-nt" x="482" y="114">IdP signs: new</text>
<text class="smc-nt" x="482" y="131">SP knows: both</text>
<text class="smc-main" x="583" y="64">retire old</text>
<line class="smc-front" x1="551" y1="70" x2="615" y2="70" marker-end="url(#smc-m-front)"/>
</g>
<g class="smc-g smc-g3">
<rect class="smc-box" x="623" y="40" width="123" height="110" rx="10"/>
<text class="smc-ttl" x="684" y="67">Old retired</text>
<text class="smc-sub" x="684" y="87">last step</text>
<text class="smc-nt" x="684" y="114">IdP signs: new</text>
<text class="smc-nt" x="684" y="131">old one retired</text>
</g>
<circle class="smc-pk smc-p0" cx="151" cy="70" r="5.5"/>
<circle class="smc-pk smc-p1" cx="354" cy="70" r="5.5"/>
<circle class="smc-pk smc-p2" cx="557" cy="70" r="5.5"/>
<line class="smc-front" x1="40" y1="186" x2="70" y2="186"/>
<text class="smc-dim" x="78" y="190" style="text-anchor:start">step in the safe order</text>
<rect class="smc-note-good" x="252" y="178" width="22" height="16" rx="4"/>
<text class="smc-dim" x="282" y="190" style="text-anchor:start">SP knows both</text>
</svg>
</div>
</div>
<!-- /diagram:saml-cert-rotation -->

Read left to right; each arrow is one action in the safe order. In the two green stages the SP knows both certificates, so it has learned the new one before the IdP signs with it.

## Settings that matter, and what they feed

| Okta field | Feeds | Wrong value looks like |
|---|---|---|
| Single sign-on URL | the ACS URL; the default ACS, "always used" for IdP-initiated | POST lands on the wrong endpoint |
| Recipient URL, Destination URL | `Recipient` and `Destination` (both default to the SSO URL) | SP rejects: `Recipient` is not the URL it received the POST at |
| Audience URI (SP Entity ID) | `Audience` | audience restriction not satisfied |
| Name ID format | `NameID Format`; default Unspecified; must match `NameIdPolicy` when the request has one | SP-initiated fails, IdP-initiated works |
| Signed Requests | validates request signatures with the uploaded Signature Certificate; the request must include `NameIDPolicy` | SP-initiated fails after enabling it |
| Default RelayState | where the user lands | wrong landing page |

**NameID.** Formats you meet: `emailAddress`, `unspecified`, `persistent`, `transient`. The spec defines persistent as an opaque, pseudo-random identifier for one IdP and SP pair, at most 256 characters, with no discernible relationship to the username; transient is opaque and temporary. Key the SP's accounts on a persistent or other opaque, never-reassigned ID and carry email as an attribute. That is design judgement, not a spec rule: email is a valid format, but an address changes on a rename or is later reissued to someone else, and an SP keyed on it then orphans or merges accounts. An SP-initiated request may carry `NameIDPolicy` (`Format`, `AllowCreate`); if the IdP cannot satisfy it, the Response must be an error, optionally with the second-level status `InvalidNameIDPolicy`. Okta requires the Name ID format to match the request's policy; Entra honors the requested format and otherwise uses the one you configured.

**Attributes** carry a `Name` and a `NameFormat` (`unspecified`, `uri` or `basic`). A mismatched `Name` or an empty source field typically leaves the attribute missing and the user arriving with no role (usual behaviour; not verified against a vendor page). Group claims are the size trap: Entra emits at most 150 groups in a SAML assertion (200 in a JWT) and above that omits the group claim entirely rather than truncating it. Okta imposes no limit on the number of attributes, but warns that the app or browser may reject large payloads (a rejected payload means no sign-in at all, so users who sign in with no role were not hit by that). Send only the groups the app needs; Entra can emit only groups assigned to the application.

## IdP-initiated, RelayState and logout

IdP-initiated sign-in (the Okta dashboard tile) skips steps 1 to 3: the IdP sends an unsolicited Response. With no `AuthnRequest` there is nothing to answer (and no `NameIDPolicy` to satisfy), so the Response must not carry `InResponseTo`, and the SP cannot tie it to a request it made. Every other check (signature, `Recipient`, `Audience`, times, replay) still applies. That is a weaker position: the SP loses its strongest tie between a Response and a request it made, so whether to allow the flow is a design decision. It goes to the SP's default ACS, and `RelayState` carries the target page by prior agreement.

<!-- diagram:saml-ways-in -->
<div style="position:relative;margin:20px 0">
<input type="checkbox" id="l02a-pause" class="l02a-cb" /><label for="l02a-pause" class="l02a-btn"><span class="l02a-off">Pause animation</span><span class="l02a-on">Play animation</span></label>
<div class="l02a-box" style="overflow-x:auto">
<svg class="l02a-flow" viewBox="0 0 760 686" role="img" aria-labelledby="l02a-t l02a-d" style="width:100%;min-width:640px;max-width:800px;height:auto;display:block;margin:0 auto">
<title id="l02a-t">IdP-initiated sign-in: steps 1 to 3 never happen</title>
<desc id="l02a-d">Three parties: the service provider, the browser and the identity provider. The user clicks the app tile in the IdP dashboard. There is no AuthnRequest, so there is nothing to answer and no NameIDPolicy to satisfy. The IdP returns an unsolicited Response in an HTML form, which must not carry InResponseTo, and RelayState carries the target page by prior agreement. The browser POSTs the form to the SP's default ACS. At the SP, the Response cannot be tied to a request the SP made, so the SP loses its strongest tie; every other check still applies: signature, Recipient, Audience, times and replay. RelayState is untrusted input and is checked against an allowlist before redirecting. The diagram highlights each step in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
<style>
.l02a-box{fill:var(--panel);stroke:var(--border-strong);stroke-width:1.5}
.l02a-hot{fill:var(--panel);stroke:var(--accent);stroke-width:2.5}
.l02a-ttl{fill:var(--text);font:600 15px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l02a-sub{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l02a-life{stroke:var(--border-strong);stroke-width:1.5;stroke-dasharray:4 5}
.l02a-front{stroke:var(--accent);stroke-width:2;fill:none}
.l02a-back{stroke:var(--muted);stroke-width:2;stroke-dasharray:7 5;fill:none}
.l02a-bad{stroke:var(--bad);stroke-width:2;fill:none}
.l02a-main{fill:var(--text);font:600 13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l02a-badt{fill:var(--bad-text)}
.l02a-dim{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l02a-badge{fill:var(--accent)}
.l02a-b-back{fill:var(--muted)}
.l02a-b-bad{fill:var(--bad)}
.l02a-b-good{fill:var(--good)}
.l02a-bt{fill:var(--on-accent);font:700 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l02a-note{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l02a-note-good{fill:var(--good-bg);stroke:var(--good);stroke-width:1.5}
.l02a-note-bad{fill:var(--bad-bg);stroke:var(--bad);stroke-width:1.5}
.l02a-nt{fill:var(--body);font:12.5px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l02a-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:18s;animation-timing-function:linear;animation-iteration-count:infinite}
.l02a-pk.l02a-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.l02a-pk.l02a-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.l02a-g{opacity:.45;animation-duration:18s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.l02a-flow:hover .l02a-g,svg.l02a-flow:hover .l02a-pk{animation-play-state:paused}
.l02a-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.l02a-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.l02a-btn:hover{background:var(--hover)}
.l02a-cb:focus-visible + .l02a-btn{outline:2px solid var(--accent);outline-offset:2px}
.l02a-cb:checked + .l02a-btn .l02a-off,.l02a-cb:not(:checked) + .l02a-btn .l02a-on{display:none}
.l02a-cb:checked ~ .l02a-box .l02a-g,.l02a-cb:checked ~ .l02a-box .l02a-pk{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.l02a-g{animation:none;opacity:1}.l02a-pk{animation:none;display:none}.l02a-btn{display:none}}
@keyframes l02a-g0{0%{opacity:1}14.286%{opacity:1}14.296%,100%{opacity:.45}}
@keyframes l02a-p0{0%,-0.01%{opacity:0;transform:translateX(0)}0%{opacity:1;transform:translateX(0)}14.286%{opacity:1;transform:translateX(236px)}14.296%,100%{opacity:0;transform:translateX(236px)}}
.l02a-g0{animation-name:l02a-g0}.l02a-p0{animation-name:l02a-p0}
@keyframes l02a-g1{0%,14.276%{opacity:.45}14.286%{opacity:1}28.571%{opacity:1}28.581%,100%{opacity:.45}}
.l02a-g1{animation-name:l02a-g1}
@keyframes l02a-g2{0%,28.561%{opacity:.45}28.571%{opacity:1}42.857%{opacity:1}42.867%,100%{opacity:.45}}
@keyframes l02a-p2{0%,28.561%{opacity:0;transform:translateX(0)}28.571%{opacity:1;transform:translateX(0)}42.857%{opacity:1;transform:translateX(-236px)}42.867%,100%{opacity:0;transform:translateX(-236px)}}
.l02a-g2{animation-name:l02a-g2}.l02a-p2{animation-name:l02a-p2}
@keyframes l02a-g3{0%,42.847%{opacity:.45}42.857%{opacity:1}57.143%{opacity:1}57.153%,100%{opacity:.45}}
@keyframes l02a-p3{0%,42.847%{opacity:0;transform:translateX(0)}42.857%{opacity:1;transform:translateX(0)}57.143%{opacity:1;transform:translateX(-236px)}57.153%,100%{opacity:0;transform:translateX(-236px)}}
.l02a-g3{animation-name:l02a-g3}.l02a-p3{animation-name:l02a-p3}
@keyframes l02a-g4{0%,57.133%{opacity:.45}57.143%{opacity:1}71.429%{opacity:1}71.439%,100%{opacity:.45}}
.l02a-g4{animation-name:l02a-g4}
@keyframes l02a-g5{0%,71.419%{opacity:.45}71.429%{opacity:1}85.714%{opacity:1}85.724%,100%{opacity:.45}}
.l02a-g5{animation-name:l02a-g5}
@keyframes l02a-g6{0%,85.704%{opacity:.45}85.714%{opacity:1}100%{opacity:1}100.01%,100%{opacity:.45}}
.l02a-g6{animation-name:l02a-g6}
</style>
<defs>
<marker id="l02a-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="l02a-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="l02a-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<line class="l02a-life" x1="110" y1="72" x2="110" y2="634"/>
<line class="l02a-life" x1="380" y1="72" x2="380" y2="634"/>
<line class="l02a-life" x1="650" y1="72" x2="650" y2="634"/>
<rect class="l02a-hot" x="20" y="10" width="180" height="62" rx="10"/><text class="l02a-ttl" x="110" y="36">Service provider</text><text class="l02a-sub" x="110" y="56">the app (SP)</text>
<rect class="l02a-box" x="290" y="10" width="180" height="62" rx="10"/><text class="l02a-ttl" x="380" y="36">Browser</text><text class="l02a-sub" x="380" y="56">the user agent</text>
<rect class="l02a-box" x="560" y="10" width="180" height="62" rx="10"/><text class="l02a-ttl" x="650" y="36">Identity provider</text><text class="l02a-sub" x="650" y="56">Okta, Entra ID (IdP)</text>
<g class="l02a-g l02a-g0">
<text class="l02a-main" x="515" y="108">User clicks the app tile</text>
<text class="l02a-dim" x="515" y="124">in the IdP dashboard</text>
<line class="l02a-front" x1="394" y1="138" x2="636" y2="138" marker-end="url(#l02a-m-front)"/>
</g>
<g class="l02a-g l02a-g1">
<rect class="l02a-note" x="489" y="172" width="261" height="48" rx="8"/>
<text class="l02a-nt" x="620" y="193">No AuthnRequest: nothing to answer,</text>
<text class="l02a-nt" x="620" y="210">no NameIDPolicy to satisfy</text>
</g>
<g class="l02a-g l02a-g2">
<text class="l02a-main" x="515" y="254">Unsolicited Response in an HTML form</text>
<text class="l02a-dim" x="515" y="270">no InResponseTo; RelayState by prior agreement</text>
<line class="l02a-front" x1="636" y1="284" x2="394" y2="284" marker-end="url(#l02a-m-front)"/>
<circle class="l02a-badge l02a-b-front" cx="650" cy="284" r="12"/><text class="l02a-bt" x="650" y="288.5">4</text>
</g>
<g class="l02a-g l02a-g3">
<text class="l02a-main" x="245" y="324">Browser POSTs the form</text>
<text class="l02a-dim" x="245" y="340">to the SP's default ACS</text>
<line class="l02a-front" x1="366" y1="354" x2="124" y2="354" marker-end="url(#l02a-m-front)"/>
<circle class="l02a-badge l02a-b-front" cx="380" cy="354" r="12"/><text class="l02a-bt" x="380" y="358.5">5</text>
</g>
<g class="l02a-g l02a-g4">
<rect class="l02a-note-bad" x="10" y="388" width="287" height="48" rx="8"/>
<text class="l02a-nt" x="154" y="409">Cannot tie it to a request the SP made:</text>
<text class="l02a-nt" x="154" y="426">its strongest tie is gone</text>
</g>
<g class="l02a-g l02a-g5">
<rect class="l02a-note-good" x="10" y="464" width="267" height="48" rx="8"/>
<text class="l02a-nt" x="144" y="485">Still applies: signature, Recipient,</text>
<text class="l02a-nt" x="144" y="502">Audience, times, replay</text>
</g>
<g class="l02a-g l02a-g6">
<rect class="l02a-note" x="10" y="540" width="287" height="48" rx="8"/>
<text class="l02a-nt" x="154" y="561">RelayState is untrusted input: check an</text>
<text class="l02a-nt" x="154" y="578">allowlist before redirecting</text>
</g>
<circle class="l02a-pk l02a-p0" cx="400" cy="138" r="5.5"/>
<circle class="l02a-pk l02a-p2" cx="630" cy="284" r="5.5"/>
<circle class="l02a-pk l02a-p3" cx="360" cy="354" r="5.5"/>
<line class="l02a-front" x1="40" y1="662" x2="70" y2="662"/>
<text class="l02a-dim" x="78" y="666" style="text-anchor:start">every hop goes through the user's browser</text>
<rect class="l02a-note-bad" x="374" y="654" width="22" height="16" rx="4"/>
<text class="l02a-dim" x="404" y="666" style="text-anchor:start">the check that is lost</text>
<rect class="l02a-note-good" x="578" y="654" width="22" height="16" rx="4"/>
<text class="l02a-dim" x="608" y="666" style="text-anchor:start">what still applies</text>
</svg>
</div>
</div>
<!-- /diagram:saml-ways-in -->

Badges 4 and 5 reuse the numbers of the main flow; steps 1 to 3 are skipped because nothing starts at the SP. Read the three notes under the SP: one check is lost, the rest still apply, and RelayState must be treated as untrusted.

`RelayState` is at most 80 bytes, should be integrity protected, and the IdP must return it exactly as received. Nothing binds it to the message, so treat it as untrusted input and check it against an allowlist before redirecting.

**Single Logout** is best effort. Every participant needs a logout endpoint for it to work; the core protocol defines a `PartialLogout` status for a session authority that could not propagate logout to all participants; Entra supports redirect (GET) but not POST for it and warns two participants can race; and Okta's switch signs the user out of the app and Okta "but not out of other apps that are open". Single Logout is a user-sign-out mechanism; none of the sources I read says that deactivating a user sends a logout to every SP (not verified), so do not rely on it for offboarding. A fired employee's SP session can therefore survive until it expires: `NotOnOrAfter` only bounds when the assertion may be delivered, not how long the SP session lasts. `SessionNotOnOrAfter` in the `AuthnStatement` marks when the IdP's session with the user ends, and the profile says the SP SHOULD discard its own security context at that time (profiles 4.1.4.3). Okta documents a "Maximum app session lifetime" value sent in the assertion but its page does not name the attribute. Keep SP sessions short either way.

<!-- diagram:saml-session-survival -->
<div style="position:relative;margin:20px 0">
<input type="checkbox" id="l02c-pause" class="l02c-cb" /><label for="l02c-pause" class="l02c-btn"><span class="l02c-off">Pause animation</span><span class="l02c-on">Play animation</span></label>
<div class="l02c-box" style="overflow-x:auto">
<svg class="l02c-flow" viewBox="0 0 760 227" role="img" aria-labelledby="l02c-t l02c-d" style="width:100%;min-width:640px;max-width:800px;height:auto;display:block;margin:0 auto">
<title id="l02c-t">Why deactivating a user may not end their SP session</title>
<desc id="l02c-d">Three stages over time. First the user has signed in: the SP has started its own session. Then the user is deactivated at the IdP: none of the sources read says a logout is sent to every SP, which is not verified, so do not rely on it for offboarding. Then the SP session can live on until it expires: the assertion's NotOnOrAfter only bounds when the assertion may be delivered, not how long the SP session lasts, so keep SP sessions short. The diagram highlights each stage in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
<style>
.l02c-box{fill:var(--panel);stroke:var(--border-strong);stroke-width:1.5}
.l02c-hot{fill:var(--panel);stroke:var(--accent);stroke-width:2.5}
.l02c-ttl{fill:var(--text);font:600 15px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l02c-sub{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l02c-life{stroke:var(--border-strong);stroke-width:1.5;stroke-dasharray:4 5}
.l02c-front{stroke:var(--accent);stroke-width:2;fill:none}
.l02c-back{stroke:var(--muted);stroke-width:2;stroke-dasharray:7 5;fill:none}
.l02c-bad{stroke:var(--bad);stroke-width:2;fill:none}
.l02c-main{fill:var(--text);font:600 13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l02c-badt{fill:var(--bad-text)}
.l02c-dim{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l02c-badge{fill:var(--accent)}
.l02c-b-back{fill:var(--muted)}
.l02c-b-bad{fill:var(--bad)}
.l02c-b-good{fill:var(--good)}
.l02c-bt{fill:var(--on-accent);font:700 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l02c-note{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l02c-note-good{fill:var(--good-bg);stroke:var(--good);stroke-width:1.5}
.l02c-note-bad{fill:var(--bad-bg);stroke:var(--bad);stroke-width:1.5}
.l02c-nt{fill:var(--body);font:12.5px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l02c-nest{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l02c-row{fill:var(--raised);stroke:var(--border-strong);stroke-width:1}
.l02c-ttlL{fill:var(--text);font:600 14px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l02c-subL{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l02c-dimL{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l02c-dimR{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:end}
.l02c-conn{stroke:var(--accent);stroke-width:1.5;fill:none}
.l02c-edge{stroke:var(--border-strong);stroke-width:1.75;fill:none}
.l02c-hl{fill:none;stroke:var(--accent);stroke-width:3}
.l02c-hle{stroke:var(--accent);stroke-width:3;fill:none}
.l02c-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:14s;animation-timing-function:linear;animation-iteration-count:infinite}
.l02c-pk.l02c-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.l02c-pk.l02c-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.l02c-g{opacity:.45;animation-duration:14s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.l02c-flow:hover .l02c-g,svg.l02c-flow:hover .l02c-pk{animation-play-state:paused}
.l02c-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.l02c-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.l02c-btn:hover{background:var(--hover)}
.l02c-cb:focus-visible + .l02c-btn{outline:2px solid var(--accent);outline-offset:2px}
.l02c-cb:checked + .l02c-btn .l02c-off,.l02c-cb:not(:checked) + .l02c-btn .l02c-on{display:none}
.l02c-cb:checked ~ .l02c-box .l02c-g,.l02c-cb:checked ~ .l02c-box .l02c-pk{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.l02c-g{animation:none;opacity:1}.l02c-pk{animation:none;display:none}.l02c-btn{display:none}}
@keyframes l02c-g0{0%{opacity:1}33.333%{opacity:1}33.343%,100%{opacity:.45}}
@keyframes l02c-p0{0%,-0.01%{opacity:0;transform:translateX(0)}0%{opacity:1;transform:translateX(0)}33.333%{opacity:1;transform:translateX(88px)}33.343%,100%{opacity:0;transform:translateX(88px)}}
.l02c-g0{animation-name:l02c-g0}.l02c-p0{animation-name:l02c-p0}
@keyframes l02c-g1{0%,33.323%{opacity:.45}33.333%{opacity:1}66.667%{opacity:1}66.677%,100%{opacity:.45}}
@keyframes l02c-p1{0%,33.323%{opacity:0;transform:translateX(0)}33.333%{opacity:1;transform:translateX(0)}66.667%{opacity:1;transform:translateX(88px)}66.677%,100%{opacity:0;transform:translateX(88px)}}
.l02c-g1{animation-name:l02c-g1}.l02c-p1{animation-name:l02c-p1}
@keyframes l02c-g2{0%,66.657%{opacity:.45}66.667%{opacity:1}100%{opacity:1}100.01%,100%{opacity:.45}}
.l02c-g2{animation-name:l02c-g2}
</style>
<defs>
<marker id="l02c-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="l02c-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="l02c-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<g class="l02c-g l02c-g0">
<rect class="l02c-box" x="14" y="40" width="171" height="127" rx="10"/>
<text class="l02c-ttl" x="99" y="67">Signed in</text>
<text class="l02c-sub" x="99" y="87">SP starts a session</text>
<text class="l02c-nt" x="99" y="114">SP session: its own</text>
<text class="l02c-nt" x="99" y="131">mechanism</text>
<text class="l02c-main" x="240" y="64">deactivate</text>
<line class="l02c-front" x1="193" y1="70" x2="287" y2="70" marker-end="url(#l02c-m-front)"/>
</g>
<g class="l02c-g l02c-g1">
<rect class="l02c-box" x="295" y="40" width="171" height="127" rx="10"/>
<text class="l02c-ttl" x="380" y="67">User deactivated</text>
<text class="l02c-sub" x="380" y="87">at the IdP</text>
<text class="l02c-nt" x="380" y="114">None of the sources read</text>
<text class="l02c-nt" x="380" y="131">says every SP is sent</text>
<text class="l02c-nt" x="380" y="148">a logout (not verified)</text>
<text class="l02c-main l02c-badt" x="520" y="48">SP session</text>
<text class="l02c-dim" x="520" y="64">may stay open</text>
<line class="l02c-bad" x1="473" y1="70" x2="567" y2="70" marker-end="url(#l02c-m-bad)"/>
</g>
<g class="l02c-g l02c-g2">
<rect class="l02c-note-bad" x="575" y="40" width="171" height="127" rx="10"/>
<text class="l02c-ttl" x="661" y="67">SP session can live on</text>
<text class="l02c-sub" x="661" y="87">until it expires</text>
<text class="l02c-nt" x="661" y="114">NotOnOrAfter bounds</text>
<text class="l02c-nt" x="661" y="131">delivery, not this;</text>
<text class="l02c-nt" x="661" y="148">keep SP sessions short</text>
</g>
<circle class="l02c-pk l02c-p0" cx="199" cy="70" r="5.5"/>
<circle class="l02c-pk l02c-p1 l02c-pkbad" cx="479" cy="70" r="5.5"/>
<line class="l02c-front" x1="40" y1="203" x2="70" y2="203"/>
<text class="l02c-dim" x="78" y="207" style="text-anchor:start">what happens next</text>
<line class="l02c-bad" x1="220" y1="203" x2="250" y2="203"/>
<text class="l02c-dim" x="258" y="207" style="text-anchor:start">the session can survive</text>
<rect class="l02c-note-bad" x="439" y="195" width="22" height="16" rx="4"/>
<text class="l02c-dim" x="469" y="207" style="text-anchor:start">state to avoid</text>
</svg>
</div>
</div>
<!-- /diagram:saml-session-survival -->

Read left to right as one fired employee's timeline. The last stage is the surprise: the sources read do not say a logout reaches the SP, so its session can survive until it expires, and the assertion's `NotOnOrAfter` is not that limit.

## What breaks at 2am

<!-- diagram:saml-triage -->
<div style="position:relative;margin:20px 0">
<input type="checkbox" id="smt-pause" class="smt-cb" /><label for="smt-pause" class="smt-btn"><span class="smt-off">Pause animation</span><span class="smt-on">Play animation</span></label>
<div class="smt-box" style="overflow-x:auto">
<svg class="smt-flow" viewBox="0 0 760 624" role="img" aria-labelledby="smt-t smt-d" style="width:100%;min-width:640px;max-width:800px;height:auto;display:block;margin:0 auto">
<title id="smt-t">Triage for a failing SAML app</title>
<desc id="smt-d">A decision tree that starts with who is affected. If NotBefore or NotOnOrAfter errors hit only one node or one user, the first check is clocks. If everyone fails, ask whether it started on a date: yes means the signing certificate expired or the IdP rotated it and the SP holds the old one. If it did not start on a date, ask whether only SP-initiated sign-in fails, which points at NameIDPolicy against the configured Name ID format. If both flows fail, read the error name: an Audience error means comparing the Audience with the SP entity ID, and a Recipient or Destination error means comparing the ACS URL the POST reached with both fields. The diagram highlights each path in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
<style>
.smt-box{fill:var(--panel);stroke:var(--border-strong);stroke-width:1.5}
.smt-hot{fill:var(--panel);stroke:var(--accent);stroke-width:2.5}
.smt-ttl{fill:var(--text);font:600 15px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.smt-sub{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.smt-life{stroke:var(--border-strong);stroke-width:1.5;stroke-dasharray:4 5}
.smt-front{stroke:var(--accent);stroke-width:2;fill:none}
.smt-back{stroke:var(--muted);stroke-width:2;stroke-dasharray:7 5;fill:none}
.smt-bad{stroke:var(--bad);stroke-width:2;fill:none}
.smt-main{fill:var(--text);font:600 13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.smt-badt{fill:var(--bad-text)}
.smt-dim{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.smt-badge{fill:var(--accent)}
.smt-b-back{fill:var(--muted)}
.smt-b-bad{fill:var(--bad)}
.smt-b-good{fill:var(--good)}
.smt-bt{fill:var(--on-accent);font:700 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.smt-note{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.smt-note-good{fill:var(--good-bg);stroke:var(--good);stroke-width:1.5}
.smt-note-bad{fill:var(--bad-bg);stroke:var(--bad);stroke-width:1.5}
.smt-nt{fill:var(--body);font:12.5px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.smt-nest{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.smt-row{fill:var(--raised);stroke:var(--border-strong);stroke-width:1}
.smt-ttlL{fill:var(--text);font:600 14px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.smt-subL{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.smt-dimL{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.smt-dimR{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:end}
.smt-conn{stroke:var(--accent);stroke-width:1.5;fill:none}
.smt-edge{stroke:var(--border-strong);stroke-width:1.75;fill:none}
.smt-hl{fill:none;stroke:var(--accent);stroke-width:3}
.smt-hle{stroke:var(--accent);stroke-width:3;fill:none}
.smt-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:20s;animation-timing-function:linear;animation-iteration-count:infinite}
.smt-pk.smt-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.smt-pk.smt-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.smt-g{opacity:.45;animation-duration:20s;animation-timing-function:linear;animation-iteration-count:infinite}
.smt-h{opacity:0;animation-duration:20s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.smt-flow:hover .smt-g,svg.smt-flow:hover .smt-pk,svg.smt-flow:hover .smt-h{animation-play-state:paused}
.smt-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.smt-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.smt-btn:hover{background:var(--hover)}
.smt-cb:focus-visible + .smt-btn{outline:2px solid var(--accent);outline-offset:2px}
.smt-cb:checked + .smt-btn .smt-off,.smt-cb:not(:checked) + .smt-btn .smt-on{display:none}
.smt-cb:checked ~ .smt-box .smt-g,.smt-cb:checked ~ .smt-box .smt-pk,.smt-cb:checked ~ .smt-box .smt-h{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.smt-g{animation:none;opacity:1}.smt-pk{animation:none;display:none}.smt-h{animation:none;opacity:0}.smt-btn{display:none}}
@keyframes smt-h0{0%{opacity:1}20%{opacity:1}20.01%,100%{opacity:0}}
.smt-h0{animation-name:smt-h0}
@keyframes smt-h1{0%,19.99%{opacity:0}20%{opacity:1}40%{opacity:1}40.01%,100%{opacity:0}}
.smt-h1{animation-name:smt-h1}
@keyframes smt-h2{0%,39.99%{opacity:0}40%{opacity:1}60%{opacity:1}60.01%,100%{opacity:0}}
.smt-h2{animation-name:smt-h2}
@keyframes smt-h3{0%,59.99%{opacity:0}60%{opacity:1}80%{opacity:1}80.01%,100%{opacity:0}}
.smt-h3{animation-name:smt-h3}
@keyframes smt-h4{0%,79.99%{opacity:0}80%{opacity:1}100%{opacity:1}100.01%,100%{opacity:0}}
.smt-h4{animation-name:smt-h4}
</style>
<defs>
<marker id="smt-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="smt-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="smt-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<path class="smt-edge" d="M380,89 L380,118 L106,118 L106,144" marker-end="url(#smt-m-front)"/>
<text class="smt-dimL" x="113" y="134">NotBefore/NotOnOrAfter error, one node or user</text>
<path class="smt-edge" d="M380,89 L380,118 L443,118 L443,144" marker-end="url(#smt-m-front)"/>
<text class="smt-dimL" x="450" y="134">everyone</text>
<path class="smt-edge" d="M443,195 L443,224 L238,224 L238,267" marker-end="url(#smt-m-front)"/>
<text class="smt-dimL" x="244" y="257">yes</text>
<path class="smt-edge" d="M443,195 L443,224 L512,224 L512,267" marker-end="url(#smt-m-front)"/>
<text class="smt-dimL" x="518" y="257">no</text>
<path class="smt-edge" d="M512,318 L512,347 L378,347 L378,390" marker-end="url(#smt-m-front)"/>
<text class="smt-dimL" x="385" y="380">yes</text>
<path class="smt-edge" d="M512,318 L512,347 L584,347 L584,390" marker-end="url(#smt-m-front)"/>
<text class="smt-dimL" x="590" y="380">no, both fail</text>
<path class="smt-edge" d="M584,441 L584,470 L518,470 L518,496" marker-end="url(#smt-m-front)"/>
<text class="smt-dimL" x="526" y="486">Audience</text>
<path class="smt-edge" d="M584,441 L584,470 L652,470 L652,496" marker-end="url(#smt-m-front)"/>
<text class="smt-dimL" x="659" y="486">Recipient</text>
<rect class="smt-note" x="51" y="147" width="110" height="65" rx="8"/><text class="smt-nt" x="106" y="168">Clocks:</text><text class="smt-nt" x="106" y="185">NotBefore or</text><text class="smt-nt" x="106" y="202">NotOnOrAfter</text>
<rect class="smt-note" x="177" y="270" width="121" height="65" rx="8"/><text class="smt-nt" x="238" y="291">Cert expired,</text><text class="smt-nt" x="238" y="308">or IdP rotated</text><text class="smt-nt" x="238" y="325">and SP has old</text>
<rect class="smt-note" x="314" y="393" width="128" height="48" rx="8"/><text class="smt-nt" x="378" y="414">NameIDPolicy vs</text><text class="smt-nt" x="378" y="431">Name ID format</text>
<rect class="smt-note" x="458" y="499" width="121" height="48" rx="8"/><text class="smt-nt" x="518" y="520">Audience vs SP</text><text class="smt-nt" x="518" y="537">entityID</text>
<rect class="smt-note" x="595" y="499" width="114" height="65" rx="8"/><text class="smt-nt" x="652" y="520">ACS URL vs</text><text class="smt-nt" x="652" y="537">Recipient and</text><text class="smt-nt" x="652" y="554">Destination</text>
<rect class="smt-box" x="528" y="393" width="110" height="48" rx="8"/><text class="smt-main" x="584" y="414">Which error</text><text class="smt-nt" x="584" y="431">name?</text>
<rect class="smt-box" x="456" y="270" width="110" height="48" rx="8"/><text class="smt-main" x="512" y="291">SP-initiated</text><text class="smt-nt" x="512" y="308">only?</text>
<rect class="smt-box" x="388" y="147" width="110" height="48" rx="8"/><text class="smt-main" x="443" y="168">Started on a</text><text class="smt-nt" x="443" y="185">date?</text>
<rect class="smt-box" x="313" y="24" width="134" height="65" rx="8"/><text class="smt-main" x="380" y="45">Sign-in fails:</text><text class="smt-nt" x="380" y="62">everyone, or one</text><text class="smt-nt" x="380" y="79">node or user?</text>
<g class="smt-h smt-h0">
<path class="smt-hle" d="M380,89 L380,118 L106,118 L106,144" marker-end="url(#smt-m-front)"/>
<rect class="smt-hl" x="313" y="24" width="134" height="65" rx="8"/>
<rect class="smt-hl" x="51" y="147" width="110" height="65" rx="8"/>
</g>
<g class="smt-h smt-h1">
<path class="smt-hle" d="M380,89 L380,118 L443,118 L443,144" marker-end="url(#smt-m-front)"/>
<path class="smt-hle" d="M443,195 L443,224 L238,224 L238,267" marker-end="url(#smt-m-front)"/>
<rect class="smt-hl" x="313" y="24" width="134" height="65" rx="8"/>
<rect class="smt-hl" x="388" y="147" width="110" height="48" rx="8"/>
<rect class="smt-hl" x="177" y="270" width="121" height="65" rx="8"/>
</g>
<g class="smt-h smt-h2">
<path class="smt-hle" d="M380,89 L380,118 L443,118 L443,144" marker-end="url(#smt-m-front)"/>
<path class="smt-hle" d="M443,195 L443,224 L512,224 L512,267" marker-end="url(#smt-m-front)"/>
<path class="smt-hle" d="M512,318 L512,347 L378,347 L378,390" marker-end="url(#smt-m-front)"/>
<rect class="smt-hl" x="313" y="24" width="134" height="65" rx="8"/>
<rect class="smt-hl" x="388" y="147" width="110" height="48" rx="8"/>
<rect class="smt-hl" x="456" y="270" width="110" height="48" rx="8"/>
<rect class="smt-hl" x="314" y="393" width="128" height="48" rx="8"/>
</g>
<g class="smt-h smt-h3">
<path class="smt-hle" d="M380,89 L380,118 L443,118 L443,144" marker-end="url(#smt-m-front)"/>
<path class="smt-hle" d="M443,195 L443,224 L512,224 L512,267" marker-end="url(#smt-m-front)"/>
<path class="smt-hle" d="M512,318 L512,347 L584,347 L584,390" marker-end="url(#smt-m-front)"/>
<path class="smt-hle" d="M584,441 L584,470 L518,470 L518,496" marker-end="url(#smt-m-front)"/>
<rect class="smt-hl" x="313" y="24" width="134" height="65" rx="8"/>
<rect class="smt-hl" x="388" y="147" width="110" height="48" rx="8"/>
<rect class="smt-hl" x="456" y="270" width="110" height="48" rx="8"/>
<rect class="smt-hl" x="528" y="393" width="110" height="48" rx="8"/>
<rect class="smt-hl" x="458" y="499" width="121" height="48" rx="8"/>
</g>
<g class="smt-h smt-h4">
<path class="smt-hle" d="M380,89 L380,118 L443,118 L443,144" marker-end="url(#smt-m-front)"/>
<path class="smt-hle" d="M443,195 L443,224 L512,224 L512,267" marker-end="url(#smt-m-front)"/>
<path class="smt-hle" d="M512,318 L512,347 L584,347 L584,390" marker-end="url(#smt-m-front)"/>
<path class="smt-hle" d="M584,441 L584,470 L652,470 L652,496" marker-end="url(#smt-m-front)"/>
<rect class="smt-hl" x="313" y="24" width="134" height="65" rx="8"/>
<rect class="smt-hl" x="388" y="147" width="110" height="48" rx="8"/>
<rect class="smt-hl" x="456" y="270" width="110" height="48" rx="8"/>
<rect class="smt-hl" x="528" y="393" width="110" height="48" rx="8"/>
<rect class="smt-hl" x="595" y="499" width="114" height="65" rx="8"/>
</g>
<line class="smt-front" x1="40" y1="600" x2="70" y2="600"/>
<text class="smt-dim" x="78" y="604" style="text-anchor:start">the path being traced</text>
</svg>
</div>
</div>
<!-- /diagram:saml-triage -->

Start at the top with who is affected and follow the branch that fits; each end box is the first thing to check; the table below gives these first checks by symptom and adds three the tree leaves out (no role, signature not found, redirect loop).

| Symptom | First check |
|---|---|
| `NotBefore` or `NotOnOrAfter` errors, one node or one user | Clocks. The spec gives no tolerance figure; Entra says a service "might allow" up to five minutes beyond the lifetime |
| Every user of one app fails on a date | Signing certificate expired, or the IdP rotated and the SP holds the old one |
| Audience error | `Audience` against the SP's `entityID`; copy it from the SP's metadata |
| Recipient or Destination error | the ACS URL the POST arrived at against both fields |
| User signed in with no role | attribute name, empty source field, group count over 150 |
| Error status for SP-initiated only | `NameIDPolicy` against the configured Name ID format |
| "Signature not found" or invalid | which element is signed, the certificate, the algorithm |
| Redirect loop | the SP rejects the Response and restarts, and the IdP's existing session answers instantly; or a cookie the SP needs while handling the ACS POST is not sent (MDN: a `SameSite=Lax` cookie is not sent on a cross-site POST such as the one to the ACS, apart from a two-minute exception where Lax is the browser default). My reasoning: that means a cookie set before the redirect to the IdP, for example one holding request state; the SameSite Lax or Strict advice for session cookies in lesson 6 concerns the session cookie the SP sets after it validates |

## Your task

Local, run on 2026-10-06 (your date will differ): build a minimal sample IdP metadata file (not schema-valid: a real `IDPSSODescriptor` also needs a `SingleSignOnService`) with a 45-day certificate and check every signing certificate in it.

```bash
openssl req -x509 -newkey rsa:2048 -nodes -keyout /dev/null -out cert.pem -days 45 -subj "/CN=sample-idp.example"
CERT=$(grep -v CERTIFICATE cert.pem | tr -d '\n')
cat > metadata.xml <<EOF
<md:EntityDescriptor xmlns:md="urn:oasis:names:tc:SAML:2.0:metadata" xmlns:ds="http://www.w3.org/2000/09/xmldsig#" entityID="https://idp.example.com/saml/sample" validUntil="2026-12-31T00:00:00Z"><md:IDPSSODescriptor protocolSupportEnumeration="urn:oasis:names:tc:SAML:2.0:protocol"><md:KeyDescriptor use="signing"><ds:KeyInfo><ds:X509Data><ds:X509Certificate>$CERT</ds:X509Certificate></ds:X509Data></ds:KeyInfo></md:KeyDescriptor></md:IDPSSODescriptor></md:EntityDescriptor>
EOF
for i in $(seq 1 $(xmllint --xpath 'count(//*[local-name()="KeyDescriptor"][@use="signing"])' metadata.xml)); do
  xmllint --xpath "string((//*[local-name()=\"KeyDescriptor\"][@use=\"signing\"])[$i]//*[local-name()=\"X509Certificate\"])" metadata.xml \
    | tr -d ' \n' | base64 -d | openssl x509 -inform DER -noout -subject -enddate -checkend $((60*86400))
done
```

```text
subject=CN=sample-idp.example
notAfter=Nov 20 16:49:53 2026 GMT
Certificate will expire
```

Output shown is OpenSSL 3 (for example Homebrew's). macOS's built-in LibreSSL 3.3.6 prints `subject= /CN=sample-idp.example` and no "Certificate will expire" line, but `-checkend` still exits 1. `-checkend` exits non-zero when the certificate ends inside the window, so the same loop fits a monitoring job. Real-tenant part, written from the docs, not run against a live tenant: point the loop at your own IdP's metadata URL after `curl -s`, and during a rollover expect two signing certificates. Next: lesson 3 covers OAuth 2.0.
