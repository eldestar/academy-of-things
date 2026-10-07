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

The browser carries every message. In this flow the IdP and the app never talk to each other directly.

1. Priya opens Acme Tracker. The app finds no session for her (a *session* is the app remembering that she is signed in).
2. The app creates a sign-in request (an `AuthnRequest`, short for authentication request) and tells her browser to go to the IdP with it. It attaches `RelayState`, a short note the IdP must hand back unchanged, usually where Priya was heading.
3. The browser follows the instruction and asks the IdP.
4. The IdP identifies Priya: it asks her to sign in, or it recognises that she is already signed in at the IdP. Then it sends back the Response with the signed assertion, wrapped in a web form.
5. Her browser submits that form to the app's ACS URL.
6. The app checks the Response, creates its own session for her, and sends her to the page she wanted.

<!-- diagram:saml-flow -->
<div style="position:relative;margin:20px 0">
<input type="checkbox" id="sm-pause" class="sm-cb" /><label for="sm-pause" class="sm-btn"><span class="sm-off">Pause animation</span><span class="sm-on">Play animation</span></label>
<div class="sm-box" style="overflow-x:auto">
<svg class="sm-flow" viewBox="0 0 760 837" role="img" aria-labelledby="sm-t sm-d" style="width:100%;min-width:640px;max-width:800px;height:auto;display:block;margin:0 auto">
<title id="sm-t">One SAML sign-in, one click at a time</title>
<desc id="sm-d">Three parties: the app (Acme Tracker), Priya's browser, and the identity provider. Priya opens the app and it finds no session. The app tells her browser to go and sign in at the identity provider, passing a sign-in request and a RelayState note. The browser follows that instruction. The identity provider signs her in, or sees she is already signed in. It sends back a signed assertion inside a web form, and the browser submits that form to the app's ACS URL. The app checks the signature, the audience, the address, the time window and that the response has not been used before, then creates its own session and sends her to the page. A final note says that when sign-in starts at the identity provider there is no sign-in request, so the app loses one check. The diagram highlights each step in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
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
.sm-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:16s;animation-timing-function:linear;animation-iteration-count:infinite}
.sm-pk.sm-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.sm-pk.sm-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.sm-g{opacity:.45;animation-duration:16s;animation-timing-function:linear;animation-iteration-count:infinite}
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
<rect class="sm-hot" x="20" y="10" width="180" height="62" rx="10"/><text class="sm-ttl" x="110" y="36">Acme Tracker</text><text class="sm-sub" x="110" y="56">the app (SP)</text>
<rect class="sm-box" x="290" y="10" width="180" height="62" rx="10"/><text class="sm-ttl" x="380" y="36">Priya's browser</text><text class="sm-sub" x="380" y="56">the courier</text>
<rect class="sm-box" x="560" y="10" width="180" height="62" rx="10"/><text class="sm-ttl" x="650" y="36">Identity provider</text><text class="sm-sub" x="650" y="56">Okta, Entra ID (IdP)</text>
<g class="sm-g sm-g0">
<text class="sm-main" x="245" y="108">Priya opens the app</text>
<text class="sm-dim" x="245" y="124">it sees no session</text>
<line class="sm-front" x1="366" y1="138" x2="124" y2="138" marker-end="url(#sm-m-front)"/>
<circle class="sm-badge sm-b-front" cx="380" cy="138" r="12"/><text class="sm-bt" x="380" y="142.5">1</text>
</g>
<g class="sm-g sm-g1">
<text class="sm-main" x="245" y="178">"Go sign in at the IdP"</text>
<text class="sm-dim" x="245" y="194">sign-in request + RelayState</text>
<line class="sm-front" x1="124" y1="208" x2="366" y2="208" marker-end="url(#sm-m-front)"/>
<circle class="sm-badge sm-b-front" cx="110" cy="208" r="12"/><text class="sm-bt" x="110" y="212.5">2</text>
</g>
<g class="sm-g sm-g2">
<text class="sm-main" x="515" y="248">Browser asks the IdP</text>
<text class="sm-dim" x="515" y="264">same request, same RelayState</text>
<line class="sm-front" x1="394" y1="278" x2="636" y2="278" marker-end="url(#sm-m-front)"/>
<circle class="sm-badge sm-b-front" cx="380" cy="278" r="12"/><text class="sm-bt" x="380" y="282.5">3</text>
</g>
<g class="sm-g sm-g3">
<rect class="sm-note" x="483" y="312" width="267" height="48" rx="8"/>
<text class="sm-nt" x="616" y="333">IdP identifies Priya:</text>
<text class="sm-nt" x="616" y="350">signs her in, or sees she already is</text>
</g>
<g class="sm-g sm-g4">
<text class="sm-main" x="515" y="394">Signed assertion in a web form</text>
<text class="sm-dim" x="515" y="410">RelayState handed back unchanged</text>
<line class="sm-front" x1="636" y1="424" x2="394" y2="424" marker-end="url(#sm-m-front)"/>
<circle class="sm-badge sm-b-front" cx="650" cy="424" r="12"/><text class="sm-bt" x="650" y="428.5">4</text>
</g>
<g class="sm-g sm-g5">
<text class="sm-main" x="245" y="464">Browser submits the form</text>
<text class="sm-dim" x="245" y="480">to the app's ACS URL</text>
<line class="sm-front" x1="366" y1="494" x2="124" y2="494" marker-end="url(#sm-m-front)"/>
<circle class="sm-badge sm-b-front" cx="380" cy="494" r="12"/><text class="sm-bt" x="380" y="498.5">5</text>
</g>
<g class="sm-g sm-g6">
<rect class="sm-note-good" x="10" y="528" width="241" height="65" rx="8"/>
<text class="sm-nt" x="130" y="549">App checks: signature, audience,</text>
<text class="sm-nt" x="130" y="566">right address, time window,</text>
<text class="sm-nt" x="130" y="583">not used before</text>
</g>
<g class="sm-g sm-g7">
<text class="sm-main" x="245" y="627">App creates its own session</text>
<text class="sm-dim" x="245" y="643">and sends her to the page</text>
<line class="sm-front" x1="124" y1="657" x2="366" y2="657" marker-end="url(#sm-m-front)"/>
<circle class="sm-badge sm-b-front" cx="110" cy="657" r="12"/><text class="sm-bt" x="110" y="661.5">6</text>
</g>
<g class="sm-g sm-g8">
<rect class="sm-note" x="489" y="691" width="261" height="48" rx="8"/>
<text class="sm-nt" x="620" y="712">Starting at the IdP instead:</text>
<text class="sm-nt" x="620" y="729">no sign-in request, one fewer check</text>
</g>
<circle class="sm-pk sm-p0" cx="360" cy="138" r="5.5"/>
<circle class="sm-pk sm-p1" cx="130" cy="208" r="5.5"/>
<circle class="sm-pk sm-p2" cx="400" cy="278" r="5.5"/>
<circle class="sm-pk sm-p4" cx="630" cy="424" r="5.5"/>
<circle class="sm-pk sm-p5" cx="360" cy="494" r="5.5"/>
<circle class="sm-pk sm-p7" cx="130" cy="657" r="5.5"/>
<line class="sm-front" x1="40" y1="813" x2="70" y2="813"/>
<text class="sm-dim" x="78" y="817" style="text-anchor:start">the browser carries every message</text>
<rect class="sm-note-good" x="323" y="805" width="22" height="16" rx="4"/>
<text class="sm-dim" x="353" y="817" style="text-anchor:start">what the app checks</text>
</svg>
</div>
</div>
<!-- /diagram:saml-flow -->

The numbers match the list above. Every hop passes through the browser; steps 2 and 3 are one redirect (the app's instruction, then the browser following it), and steps 4 and 5 are one form POST (the IdP's form, then the browser submitting it). The IdP identifies Priya between steps 3 and 4.

## What the app checks before letting her in

The browser is only a courier, so the app trusts the signature, not the courier. It checks that:

- the **signature** is valid for the certificate it holds for this IdP;
- the **audience** in the assertion equals the app's own entity ID, so the letter was meant for this app;
- the Response arrived at the **right address**: the ACS URL named inside it (`Recipient`);
- the time now is inside the assertion's **valid window** (`NotBefore` to `NotOnOrAfter`), allowing a small tolerance for clocks that differ. The standard gives no figure; Microsoft says a service "might allow" up to five minutes beyond the lifetime, so think of a few minutes, not an hour (a product's own setting may differ). A server whose clock is off by more than that fails this check;
- the Response answers the request the app sent (`InResponseTo`) and has **not been used before**. The standard requires the app to remember the IDs of assertions it has accepted, because an assertion works for whoever presents it.

<!-- diagram:saml-response-anatomy -->
<div style="position:relative;margin:20px 0">
<input type="checkbox" id="smr-pause" class="smr-cb" /><label for="smr-pause" class="smr-btn"><span class="smr-off">Pause animation</span><span class="smr-on">Play animation</span></label>
<div class="smr-box" style="overflow-x:auto">
<svg class="smr-flow" viewBox="0 0 760 344" role="img" aria-labelledby="smr-t smr-d" style="width:100%;min-width:640px;max-width:800px;height:auto;display:block;margin:0 auto">
<title id="smr-t">The envelope and the letter: what the app checks in each part</title>
<desc id="smr-d">A nested diagram. The Response is the envelope and the Assertion inside it is the letter. Numbered callouts say what the app checks in each part. On the envelope, the Response must arrive at the right address and must answer the request the app sent. On the Assertion, the app checks it has not been used before. Inside the Assertion: the signature must be valid for the certificate the app holds for this IdP; the audience must equal the app's own entity ID; and the time now must be inside the valid window, allowing a small tolerance for clocks. The diagram highlights each part in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
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
.smr-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:18s;animation-timing-function:linear;animation-iteration-count:infinite}
.smr-pk.smr-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.smr-pk.smr-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.smr-g{opacity:.45;animation-duration:18s;animation-timing-function:linear;animation-iteration-count:infinite}
.smr-h{opacity:0;animation-duration:18s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.smr-flow:hover .smr-g,svg.smr-flow:hover .smr-pk,svg.smr-flow:hover .smr-h{animation-play-state:paused}
.smr-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.smr-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.smr-btn:hover{background:var(--hover)}
.smr-cb:focus-visible + .smr-btn{outline:2px solid var(--accent);outline-offset:2px}
.smr-cb:checked + .smr-btn .smr-off,.smr-cb:not(:checked) + .smr-btn .smr-on{display:none}
.smr-cb:checked ~ .smr-box .smr-g,.smr-cb:checked ~ .smr-box .smr-pk,.smr-cb:checked ~ .smr-box .smr-h{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.smr-g{animation:none;opacity:1}.smr-pk{animation:none;display:none}.smr-h{animation:none;opacity:0}.smr-btn{display:none}}
@keyframes smr-g0{0%{opacity:1}20%{opacity:1}20.01%,100%{opacity:.45}}
@keyframes smr-h0{0%{opacity:1}20%{opacity:1}20.01%,100%{opacity:0}}
.smr-g0{animation-name:smr-g0}.smr-h0{animation-name:smr-h0}
@keyframes smr-g1{0%,19.99%{opacity:.45}20%{opacity:1}40%{opacity:1}40.01%,100%{opacity:.45}}
@keyframes smr-h1{0%,19.99%{opacity:0}20%{opacity:1}40%{opacity:1}40.01%,100%{opacity:0}}
.smr-g1{animation-name:smr-g1}.smr-h1{animation-name:smr-h1}
@keyframes smr-g2{0%,39.99%{opacity:.45}40%{opacity:1}60%{opacity:1}60.01%,100%{opacity:.45}}
@keyframes smr-h2{0%,39.99%{opacity:0}40%{opacity:1}60%{opacity:1}60.01%,100%{opacity:0}}
.smr-g2{animation-name:smr-g2}.smr-h2{animation-name:smr-h2}
@keyframes smr-g3{0%,59.99%{opacity:.45}60%{opacity:1}80%{opacity:1}80.01%,100%{opacity:.45}}
@keyframes smr-h3{0%,59.99%{opacity:0}60%{opacity:1}80%{opacity:1}80.01%,100%{opacity:0}}
.smr-g3{animation-name:smr-g3}.smr-h3{animation-name:smr-h3}
@keyframes smr-g4{0%,79.99%{opacity:.45}80%{opacity:1}100%{opacity:1}100.01%,100%{opacity:.45}}
@keyframes smr-h4{0%,79.99%{opacity:0}80%{opacity:1}100%{opacity:1}100.01%,100%{opacity:0}}
.smr-g4{animation-name:smr-g4}.smr-h4{animation-name:smr-h4}
</style>
<defs>
<marker id="smr-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="smr-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="smr-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<rect class="smr-box" x="14" y="16" width="440" height="270" rx="9"/><text class="smr-ttlL" x="28" y="37">Response</text><text class="smr-subL" x="28" y="54">the envelope</text>
<rect class="smr-nest" x="26" y="62" width="416" height="212" rx="9"/><text class="smr-ttlL" x="40" y="83">Assertion</text><text class="smr-subL" x="40" y="100">the signed letter: who she is, which app, how long</text>
<rect class="smr-nest" x="38" y="108" width="392" height="46" rx="9"/><text class="smr-ttlL" x="52" y="129">Signature</text><text class="smr-subL" x="52" y="146">made with the IdP's private key</text>
<rect class="smr-nest" x="38" y="162" width="392" height="46" rx="9"/><text class="smr-ttlL" x="52" y="183">Audience</text><text class="smr-subL" x="52" y="200">which app it is for</text>
<rect class="smr-nest" x="38" y="216" width="392" height="46" rx="9"/><text class="smr-ttlL" x="52" y="237">Valid window</text><text class="smr-subL" x="52" y="254">NotBefore to NotOnOrAfter</text>
<g class="smr-g smr-g0">
<path class="smr-conn" d="M454,33 L462,33 L462,34 L470,34" marker-end="url(#smr-m-front)"/>
<rect class="smr-note-good" x="484" y="10" width="262" height="48" rx="8"/>
<text class="smr-nt" x="615" y="31">Right address (Recipient), and it</text>
<text class="smr-nt" x="615" y="48">answers my request (InResponseTo)</text>
<circle class="smr-badge smr-b-good" cx="484" cy="34" r="12"/><text class="smr-bt" x="484" y="38.5">1</text>
</g>
<g class="smr-g smr-g1">
<path class="smr-conn" d="M442,79 L466,79 L466,92 L470,92" marker-end="url(#smr-m-front)"/>
<rect class="smr-note-good" x="484" y="68" width="262" height="48" rx="8"/>
<text class="smr-nt" x="615" y="89">Not used before: the app remembers</text>
<text class="smr-nt" x="615" y="106">the IDs it has accepted</text>
<circle class="smr-badge smr-b-good" cx="484" cy="92" r="12"/><text class="smr-bt" x="484" y="96.5">2</text>
</g>
<g class="smr-g smr-g2">
<path class="smr-conn" d="M430,125 L470,125 L470,150 L470,150" marker-end="url(#smr-m-front)"/>
<rect class="smr-note-good" x="484" y="126" width="262" height="48" rx="8"/>
<text class="smr-nt" x="615" y="147">Valid for the certificate the app</text>
<text class="smr-nt" x="615" y="164">holds for this IdP</text>
<circle class="smr-badge smr-b-good" cx="484" cy="150" r="12"/><text class="smr-bt" x="484" y="154.5">3</text>
</g>
<g class="smr-g smr-g3">
<path class="smr-conn" d="M430,179 L474,179 L474,200 L470,200" marker-end="url(#smr-m-front)"/>
<rect class="smr-note-good" x="484" y="184" width="262" height="31" rx="8"/>
<text class="smr-nt" x="615" y="205">Equals the app's own entity ID</text>
<circle class="smr-badge smr-b-good" cx="484" cy="200" r="12"/><text class="smr-bt" x="484" y="204.0">4</text>
</g>
<g class="smr-g smr-g4">
<path class="smr-conn" d="M430,233 L462,233 L462,249 L470,249" marker-end="url(#smr-m-front)"/>
<rect class="smr-note-good" x="484" y="225" width="262" height="48" rx="8"/>
<text class="smr-nt" x="615" y="246">Now is inside it, allowing a small</text>
<text class="smr-nt" x="615" y="263">tolerance for clocks</text>
<circle class="smr-badge smr-b-good" cx="484" cy="249" r="12"/><text class="smr-bt" x="484" y="253.5">5</text>
</g>
<g class="smr-h smr-h0">
<rect class="smr-hl" x="14" y="16" width="440" height="270" rx="9"/>
</g>
<g class="smr-h smr-h1">
<rect class="smr-hl" x="26" y="62" width="416" height="212" rx="9"/>
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
<rect class="smr-note-good" x="40" y="312" width="22" height="16" rx="4"/>
<text class="smr-dim" x="70" y="324" style="text-anchor:start">what the app checks</text>
</svg>
</div>
</div>
<!-- /diagram:saml-response-anatomy -->

Read it from the outside in: the Response is the envelope and the Assertion is the letter inside it. Each green part is one of the checks above, and the numbers run from the outside in.

## Who is she? NameID and attributes

Inside the assertion, the **NameID** is the label the IdP uses for Priya, and **attributes** are extra facts such as email, name and groups. The app matches the NameID to one of its accounts, and an admin chooses its format. An **email address** is easy to read but changes when someone changes their name; if the app filed her account under the old address, the new one looks like a stranger and she gets an empty second account. An **unspecified** NameID format promises nothing: the IdP sends whatever form it likes, and the app has to already know how to read it; it is not an instruction to look anyone up by name. A value built from her full name would change on a rename just as the email does. A **persistent** NameID is a random, meaningless label that the standard defines as opaque, at most 256 characters, and specific to one IdP and app pair, so it does not change when her name does. Using it as the account key is a design judgement, not a rule of the standard, which allows both. Attributes arrive only if an admin mapped them: an attribute that is not mapped is missing, and the app sees "no role". Microsoft Entra ID sends at most 150 groups in a SAML assertion and, above that, leaves the group list out altogether.

## Two ways in, and logging out

**SP-initiated** (above) starts at the app. **IdP-initiated** starts at the IdP, for example Priya clicking an app tile in the Okta dashboard: there is no sign-in request, so the Response cannot answer one. That is a weaker position, because the app cannot match the Response to a request it made, so it loses one of its checks. Whether to allow this way in is a design decision.

<!-- diagram:saml-ways-in -->
<div style="position:relative;margin:20px 0">
<input type="checkbox" id="l02a-pause" class="l02a-cb" /><label for="l02a-pause" class="l02a-btn"><span class="l02a-off">Pause animation</span><span class="l02a-on">Play animation</span></label>
<div class="l02a-box" style="overflow-x:auto">
<svg class="l02a-flow" viewBox="0 0 760 461" role="img" aria-labelledby="l02a-t l02a-d" style="width:100%;min-width:640px;max-width:800px;height:auto;display:block;margin:0 auto">
<title id="l02a-t">Two ways in: starting at the app or at the IdP</title>
<desc id="l02a-d">A comparison of SP-initiated and IdP-initiated sign-in in four rows. Where Priya starts: at the app, or at the IdP, for example an app tile in the Okta dashboard. The sign-in request: the app creates one when sign-in starts at the app, and there is none when it starts at the IdP. Matching the Response to a request: the app can match it when it sent a request, and has nothing to match it to when it did not. The app's checks: all the checks above when sign-in starts at the app, and one fewer, a weaker position, when it starts at the IdP. The diagram highlights each row in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
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
.l02a-nest{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l02a-row{fill:var(--raised);stroke:var(--border-strong);stroke-width:1}
.l02a-ttlL{fill:var(--text);font:600 14px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l02a-subL{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l02a-dimL{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l02a-dimR{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:end}
.l02a-conn{stroke:var(--accent);stroke-width:1.5;fill:none}
.l02a-edge{stroke:var(--border-strong);stroke-width:1.75;fill:none}
.l02a-hl{fill:none;stroke:var(--accent);stroke-width:3}
.l02a-hle{stroke:var(--accent);stroke-width:3;fill:none}
.l02a-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:16s;animation-timing-function:linear;animation-iteration-count:infinite}
.l02a-pk.l02a-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.l02a-pk.l02a-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.l02a-g{opacity:.45;animation-duration:16s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.l02a-flow:hover .l02a-g,svg.l02a-flow:hover .l02a-pk{animation-play-state:paused}
.l02a-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.l02a-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.l02a-btn:hover{background:var(--hover)}
.l02a-cb:focus-visible + .l02a-btn{outline:2px solid var(--accent);outline-offset:2px}
.l02a-cb:checked + .l02a-btn .l02a-off,.l02a-cb:not(:checked) + .l02a-btn .l02a-on{display:none}
.l02a-cb:checked ~ .l02a-box .l02a-g,.l02a-cb:checked ~ .l02a-box .l02a-pk{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.l02a-g{animation:none;opacity:1}.l02a-pk{animation:none;display:none}.l02a-btn{display:none}}
@keyframes l02a-g0{0%{opacity:1}25%{opacity:1}25.01%,100%{opacity:.45}}
.l02a-g0{animation-name:l02a-g0}
@keyframes l02a-g1{0%,24.99%{opacity:.45}25%{opacity:1}50%{opacity:1}50.01%,100%{opacity:.45}}
.l02a-g1{animation-name:l02a-g1}
@keyframes l02a-g2{0%,49.99%{opacity:.45}50%{opacity:1}75%{opacity:1}75.01%,100%{opacity:.45}}
.l02a-g2{animation-name:l02a-g2}
@keyframes l02a-g3{0%,74.99%{opacity:.45}75%{opacity:1}100%{opacity:1}100.01%,100%{opacity:.45}}
.l02a-g3{animation-name:l02a-g3}
</style>
<defs>
<marker id="l02a-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="l02a-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="l02a-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<rect class="l02a-box" x="240" y="10" width="247" height="62" rx="10"/><text class="l02a-ttl" x="364" y="36">SP-initiated</text><text class="l02a-sub" x="364" y="56">starts at the app</text>
<rect class="l02a-box" x="495" y="10" width="247" height="62" rx="10"/><text class="l02a-ttl" x="618" y="36">IdP-initiated</text><text class="l02a-sub" x="618" y="56">starts at the IdP</text>
<g class="l02a-g l02a-g0">
<rect class="l02a-row" x="10" y="86" width="740" height="86" rx="8"/>
<text class="l02a-ttlL" x="24" y="112">Where Priya starts</text>
<text class="l02a-nt" x="364" y="134">The app (the flow above)</text>
<text class="l02a-nt" x="618" y="134">For example an app tile in</text>
<text class="l02a-nt" x="618" y="149">the Okta dashboard</text>
</g>
<g class="l02a-g l02a-g1">
<rect class="l02a-row" x="10" y="180" width="740" height="71" rx="8"/>
<text class="l02a-ttlL" x="24" y="206">The sign-in request</text>
<circle cx="364" cy="202" r="10" style="fill:var(--good)"/><path d="M359.3,202.0 L362.1,205.4 L367.7,198.6" style="fill:none;stroke:var(--on-accent);stroke-width:2;stroke-linecap:round;stroke-linejoin:round"/>
<text class="l02a-nt" x="364" y="228">The app creates one</text>
<circle cx="618" cy="202" r="10" style="fill:var(--bad)"/><path d="M615.1,198.6 L621.9,205.4 M621.9,198.6 L615.1,205.4" style="fill:none;stroke:var(--on-accent);stroke-width:2;stroke-linecap:round;stroke-linejoin:round"/>
<text class="l02a-nt" x="618" y="228">There is none</text>
</g>
<g class="l02a-g l02a-g2">
<rect class="l02a-row" x="10" y="259" width="740" height="71" rx="8"/>
<text class="l02a-ttlL" x="24" y="285">Response matches a request</text>
<text class="l02a-subL" x="24" y="303">the InResponseTo check</text>
<circle cx="364" cy="281" r="10" style="fill:var(--good)"/><path d="M359.3,281.0 L362.1,284.4 L367.7,277.6" style="fill:none;stroke:var(--on-accent);stroke-width:2;stroke-linecap:round;stroke-linejoin:round"/>
<text class="l02a-nt" x="364" y="307">The app can match it</text>
<circle cx="618" cy="281" r="10" style="fill:var(--bad)"/><path d="M615.1,277.6 L621.9,284.4 M621.9,277.6 L615.1,284.4" style="fill:none;stroke:var(--on-accent);stroke-width:2;stroke-linecap:round;stroke-linejoin:round"/>
<text class="l02a-nt" x="618" y="307">Nothing to match it to</text>
</g>
<g class="l02a-g l02a-g3">
<rect class="l02a-row" x="10" y="338" width="740" height="71" rx="8"/>
<text class="l02a-ttlL" x="24" y="364">The app's checks</text>
<circle cx="364" cy="360" r="10" style="fill:var(--good)"/><path d="M359.3,360.0 L362.1,363.4 L367.7,356.6" style="fill:none;stroke:var(--on-accent);stroke-width:2;stroke-linecap:round;stroke-linejoin:round"/>
<text class="l02a-nt" x="364" y="386">All of the checks above</text>
<circle cx="618" cy="360" r="10" style="fill:var(--muted)"/><path d="M614.3,360.0 L622.7,360.0" style="fill:none;stroke:var(--on-accent);stroke-width:2;stroke-linecap:round;stroke-linejoin:round"/>
<text class="l02a-nt" x="618" y="386">One fewer: a weaker position</text>
</g>
<circle cx="48" cy="437" r="8" style="fill:var(--good)"/><path d="M44.6,437.0 L46.9,439.7 L51.4,434.3" style="fill:none;stroke:var(--on-accent);stroke-width:2;stroke-linecap:round;stroke-linejoin:round"/>
<text class="l02a-dim" x="64" y="441" style="text-anchor:start">present</text>
<circle cx="150" cy="437" r="8" style="fill:var(--muted)"/><path d="M146.6,437.0 L153.4,437.0" style="fill:none;stroke:var(--on-accent);stroke-width:2;stroke-linecap:round;stroke-linejoin:round"/>
<text class="l02a-dim" x="166" y="441" style="text-anchor:start">weaker</text>
<circle cx="246" cy="437" r="8" style="fill:var(--bad)"/><path d="M243.3,434.3 L248.7,439.7 M248.7,434.3 L243.3,439.7" style="fill:none;stroke:var(--on-accent);stroke-width:2;stroke-linecap:round;stroke-linejoin:round"/>
<text class="l02a-dim" x="262" y="441" style="text-anchor:start">missing</text>
</svg>
</div>
</div>
<!-- /diagram:saml-ways-in -->

Compare the two columns row by row. The last row is the point: starting at the IdP means there is no sign-in request, so the app loses one of its checks.

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
