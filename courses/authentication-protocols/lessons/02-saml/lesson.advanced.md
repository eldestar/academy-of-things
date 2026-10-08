# SAML 2.0

You build or review the service-provider (SP) side, or you own the architecture an SP plugs into. This lesson works at spec level: what the Web Browser SSO profile obliges you to verify, what an XML signature does and does not prove, how the real attacks work, and which decisions the standard leaves to you. Facts checked 2026-10-06 against the OASIS SAML 2.0 core, bindings, profiles and metadata specifications (15 March 2005), W3C XML Signature 1.1, the GitHub advisory database, NVD, the abstract of the USENIX Security 2012 SAML paper, and Okta and Microsoft Learn pages. Section numbers are from those documents. Where I reason beyond them I say so.

## The flow, step by step

<!-- diagram:saml-flow -->
<div class="sm-wrap" style="position:relative">
<input type="checkbox" id="sm-pause" class="sm-cb" /><label for="sm-pause" class="sm-btn"><span class="sm-off">Pause animation</span><span class="sm-on">Play animation</span></label>
<div class="sm-box" style="overflow-x:auto">
<svg class="sm-flow" viewBox="0 0 760 917" role="img" aria-labelledby="sm-t sm-d" style="width:760px;max-width:100%;min-width:699px;height:auto;display:block;margin:0 auto">
<title id="sm-t">Inside the SP when the Response arrives</title>
<desc id="sm-d">Four parts: the browser, the service provider's signature verifier, its assertion logic, and its ID cache. The browser posts the SAMLResponse to the ACS URL; if the message is signed, Destination must be present and equal that URL. The verifier checks the signature; the author's rule, not the spec's, is to use a key from pinned IdP metadata and never one from the message. Verification shows that some element matches a signed digest, not that the element the logic reads next is that element. A wrapping gap appears when the assertion logic then looks up the Assertion with a fresh whole-document query instead of reading the element the verified Reference points to. The control, a design recommendation and not a spec rule, is to read every security-relevant value from the verified node, use one parser, and reject a duplicate ID or an unexpected Assertion count. The logic then keeps the assertion ID in the cache. The profile requires keeping used IDs for as long as NotOnOrAfter would keep the assertion valid; the author's reasoning adds any skew allowance and one cache shared by every node. The service provider then may start its session by any mechanism it chooses. A final note says that stored AuthnRequest IDs cover only SP-initiated Responses, so the ID cache is still required. The diagram highlights each step in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
<style>
svg.sm-flow{--ink:light-dark(#000000,#ffffff)}
.sm-box{fill:var(--panel);stroke:var(--border-strong);stroke-width:1.5}
.sm-hot{fill:var(--panel);stroke:var(--accent);stroke-width:2.5}
.sm-ttl{fill:var(--ink);font:600 15px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.sm-sub{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.sm-life{stroke:var(--border-strong);stroke-width:1.5;stroke-dasharray:4 5}
.sm-front{stroke:var(--accent);stroke-width:2;fill:none}
.sm-back{stroke:var(--muted);stroke-width:2;stroke-dasharray:7 5;fill:none}
.sm-bad{stroke:var(--bad);stroke-width:2;fill:none}
.sm-main{fill:var(--ink);font:600 13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.sm-badt{fill:var(--ink)}
.sm-dim{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.sm-badge{fill:var(--accent)}
.sm-b-back{fill:var(--muted)}
.sm-b-bad{fill:var(--bad)}
.sm-b-good{fill:var(--good)}
.sm-bt{fill:var(--on-accent);font:700 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.sm-note{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.sm-note-good{fill:var(--good-bg);stroke:var(--good);stroke-width:1.5}
.sm-note-bad{fill:var(--bad-bg);stroke:var(--bad);stroke-width:1.5}
.sm-nt{fill:var(--ink);font:500 12.5px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.sm-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:44s;animation-timing-function:linear;animation-iteration-count:infinite}
.sm-pk.sm-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.sm-pk.sm-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.sm-wrap{margin:20px 0}
@media (min-width:801px){.sm-wrap{margin-left:-44px;margin-right:-44px}}
.sm-g rect,.sm-g line,.sm-g path:not(.sm-gl){opacity:.5;animation-duration:44s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.sm-flow:hover .sm-g rect,svg.sm-flow:hover .sm-g line,svg.sm-flow:hover .sm-g path:not(.sm-gl),svg.sm-flow:hover .sm-pk{animation-play-state:paused}
.sm-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.sm-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.sm-btn:hover{background:var(--hover)}
.sm-cb:focus-visible + .sm-btn{outline:2px solid var(--accent);outline-offset:2px}
.sm-cb:checked + .sm-btn .sm-off,.sm-cb:not(:checked) + .sm-btn .sm-on{display:none}
.sm-cb:checked ~ .sm-box .sm-g rect,.sm-cb:checked ~ .sm-box .sm-g line,.sm-cb:checked ~ .sm-box .sm-g path:not(.sm-gl),.sm-cb:checked ~ .sm-box .sm-pk{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.sm-g rect,.sm-g line,.sm-g path:not(.sm-gl){animation:none;opacity:1}.sm-pk{animation:none;display:none}.sm-btn{display:none}}
@keyframes sm-g0{0%{opacity:1}13.636%{opacity:1}13.646%,100%{opacity:.5}}
@keyframes sm-p0{0%,-0.01%{opacity:0;transform:translateX(0)}0%{opacity:1;transform:translateX(0)}10.909%{opacity:1;transform:translateX(146px)}13.636%{opacity:1;transform:translateX(146px)}13.646%,100%{opacity:0;transform:translateX(146px)}}
.sm-g0 rect,.sm-g0 line,.sm-g0 path:not(.sm-gl){animation-name:sm-g0}.sm-p0{animation-name:sm-p0}
@keyframes sm-g1{0%,13.626%{opacity:.5}13.636%{opacity:1}22.727%{opacity:1}22.737%,100%{opacity:.5}}
.sm-g1 rect,.sm-g1 line,.sm-g1 path:not(.sm-gl){animation-name:sm-g1}
@keyframes sm-g2{0%,22.717%{opacity:.5}22.727%{opacity:1}36.364%{opacity:1}36.374%,100%{opacity:.5}}
@keyframes sm-p2{0%,22.717%{opacity:0;transform:translateX(0)}22.727%{opacity:1;transform:translateX(0)}33.636%{opacity:1;transform:translateX(146px)}36.364%{opacity:1;transform:translateX(146px)}36.374%,100%{opacity:0;transform:translateX(146px)}}
.sm-g2 rect,.sm-g2 line,.sm-g2 path:not(.sm-gl){animation-name:sm-g2}.sm-p2{animation-name:sm-p2}
@keyframes sm-g3{0%,36.354%{opacity:.5}36.364%{opacity:1}45.455%{opacity:1}45.465%,100%{opacity:.5}}
.sm-g3 rect,.sm-g3 line,.sm-g3 path:not(.sm-gl){animation-name:sm-g3}
@keyframes sm-g4{0%,45.445%{opacity:.5}45.455%{opacity:1}54.545%{opacity:1}54.555%,100%{opacity:.5}}
.sm-g4 rect,.sm-g4 line,.sm-g4 path:not(.sm-gl){animation-name:sm-g4}
@keyframes sm-g5{0%,54.535%{opacity:.5}54.545%{opacity:1}68.182%{opacity:1}68.192%,100%{opacity:.5}}
@keyframes sm-p5{0%,54.535%{opacity:0;transform:translateX(0)}54.545%{opacity:1;transform:translateX(0)}65.455%{opacity:1;transform:translateX(146px)}68.182%{opacity:1;transform:translateX(146px)}68.192%,100%{opacity:0;transform:translateX(146px)}}
.sm-g5 rect,.sm-g5 line,.sm-g5 path:not(.sm-gl){animation-name:sm-g5}.sm-p5{animation-name:sm-p5}
@keyframes sm-g6{0%,68.172%{opacity:.5}68.182%{opacity:1}77.273%{opacity:1}77.283%,100%{opacity:.5}}
.sm-g6 rect,.sm-g6 line,.sm-g6 path:not(.sm-gl){animation-name:sm-g6}
@keyframes sm-g7{0%,77.263%{opacity:.5}77.273%{opacity:1}90.909%{opacity:1}90.919%,100%{opacity:.5}}
@keyframes sm-p7{0%,77.263%{opacity:0;transform:translateX(0)}77.273%{opacity:1;transform:translateX(0)}88.182%{opacity:1;transform:translateX(-326px)}90.909%{opacity:1;transform:translateX(-326px)}90.919%,100%{opacity:0;transform:translateX(-326px)}}
.sm-g7 rect,.sm-g7 line,.sm-g7 path:not(.sm-gl){animation-name:sm-g7}.sm-p7{animation-name:sm-p7}
@keyframes sm-g8{0%,90.899%{opacity:.5}90.909%{opacity:1}100%{opacity:1}100.01%,100%{opacity:.5}}
.sm-g8 rect,.sm-g8 line,.sm-g8 path:not(.sm-gl){animation-name:sm-g8}
</style>
<defs>
<marker id="sm-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="sm-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="sm-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<line class="sm-life" x1="110" y1="72" x2="110" y2="865"/>
<line class="sm-life" x1="290" y1="72" x2="290" y2="865"/>
<line class="sm-life" x1="470" y1="72" x2="470" y2="865"/>
<line class="sm-life" x1="650" y1="72" x2="650" y2="865"/>
<rect class="sm-box" x="30" y="10" width="160" height="62" rx="10"/><text class="sm-ttl" x="110" y="36">Browser</text><text class="sm-sub" x="110" y="56">or an attacker's replay</text>
<rect class="sm-hot" x="210" y="10" width="160" height="62" rx="10"/><text class="sm-ttl" x="290" y="36">Signature check</text><text class="sm-sub" x="290" y="56">XML-DSig verifier</text>
<rect class="sm-box" x="390" y="10" width="160" height="62" rx="10"/><text class="sm-ttl" x="470" y="36">Assertion logic</text><text class="sm-sub" x="470" y="56">reads NameID, Audience</text>
<rect class="sm-box" x="570" y="10" width="160" height="62" rx="10"/><text class="sm-ttl" x="650" y="36">ID cache</text><text class="sm-sub" x="650" y="56">keeps used IDs</text>
<g class="sm-g sm-g0">
<text class="sm-main" x="200" y="108">POST SAMLResponse</text>
<text class="sm-dim" x="200" y="124">if signed: Destination = ACS URL</text>
<line class="sm-front" x1="124" y1="138" x2="276" y2="138" marker-end="url(#sm-m-front)"/>
<circle class="sm-badge sm-b-front" cx="110" cy="138" r="12"/><text class="sm-bt" x="110" y="142.5">1</text>
</g>
<g class="sm-g sm-g1">
<rect class="sm-note-good" x="176" y="172" width="228" height="65" rx="8"/>
<text class="sm-nt" x="290" y="193">Author's rule, not the spec's:</text>
<text class="sm-nt" x="290" y="210">verify with a key from pinned</text>
<text class="sm-nt" x="290" y="227">IdP metadata, not the message</text>
</g>
<g class="sm-g sm-g2">
<text class="sm-main" x="380" y="271">Verified: some element</text>
<text class="sm-dim" x="380" y="287">matches a signed digest</text>
<line class="sm-front" x1="304" y1="301" x2="456" y2="301" marker-end="url(#sm-m-front)"/>
<circle class="sm-badge sm-b-front" cx="290" cy="301" r="12"/><text class="sm-bt" x="290" y="305.5">2</text>
</g>
<g class="sm-g sm-g3">
<rect class="sm-note-bad" x="366" y="335" width="208" height="65" rx="8"/>
<text class="sm-nt" x="470" y="356">Gap: a fresh whole-document</text>
<text class="sm-nt" x="470" y="373">lookup can read a forged,</text>
<text class="sm-nt" x="470" y="390">unsigned Assertion (XSW)</text>
</g>
<g class="sm-g sm-g4">
<rect class="sm-note-good" x="330" y="428" width="280" height="65" rx="8"/>
<text class="sm-nt" x="470" y="449">Control: read values from the</text>
<text class="sm-nt" x="470" y="466">verified node; one parser;</text>
<text class="sm-nt" x="470" y="483">reject duplicate ID or extra Assertion</text>
</g>
<g class="sm-g sm-g5">
<text class="sm-main" x="560" y="527">Keep the used</text>
<text class="sm-dim" x="560" y="543">assertion ID</text>
<line class="sm-front" x1="484" y1="557" x2="636" y2="557" marker-end="url(#sm-m-front)"/>
<circle class="sm-badge sm-b-front" cx="470" cy="557" r="12"/><text class="sm-bt" x="470" y="561.5">3</text>
</g>
<g class="sm-g sm-g6">
<rect class="sm-note-good" x="483" y="591" width="267" height="65" rx="8"/>
<text class="sm-nt" x="616" y="612">Keep ID while NotOnOrAfter would</text>
<text class="sm-nt" x="616" y="629">keep it valid; my reasoning: also</text>
<text class="sm-nt" x="616" y="646">the skew allowance, one shared cache</text>
</g>
<g class="sm-g sm-g7">
<text class="sm-main" x="290" y="690">SP may start its session</text>
<text class="sm-dim" x="290" y="706">any mechanism it chooses</text>
<line class="sm-front" x1="456" y1="720" x2="124" y2="720" marker-end="url(#sm-m-front)"/>
<circle class="sm-badge sm-b-front" cx="470" cy="720" r="12"/><text class="sm-bt" x="470" y="724.5">4</text>
</g>
<g class="sm-g sm-g8">
<rect class="sm-note" x="496" y="754" width="254" height="65" rx="8"/>
<text class="sm-nt" x="623" y="775">Stored AuthnRequest IDs cover only</text>
<text class="sm-nt" x="623" y="792">SP-initiated; the ID cache is</text>
<text class="sm-nt" x="623" y="809">still required</text>
</g>
<circle class="sm-pk sm-p0" cx="130" cy="138" r="5.5"/>
<circle class="sm-pk sm-p2" cx="310" cy="301" r="5.5"/>
<circle class="sm-pk sm-p5" cx="490" cy="557" r="5.5"/>
<circle class="sm-pk sm-p7" cx="450" cy="720" r="5.5"/>
<line class="sm-front" x1="40" y1="893" x2="70" y2="893"/>
<text class="sm-dim" x="78" y="897" style="text-anchor:start">the Response in transit</text>
<rect class="sm-note-bad" x="259" y="885" width="22" height="16" rx="4"/>
<text class="sm-dim" x="289" y="897" style="text-anchor:start">the wrapping gap</text>
<rect class="sm-note-good" x="425" y="885" width="22" height="16" rx="4"/>
<text class="sm-dim" x="455" y="897" style="text-anchor:start">controls (recommendations, not spec rules)</text>
</svg>
</div>
</div>
<!-- /diagram:saml-flow -->

The diagram zooms in on steps 5 and 6 below: what happens inside the SP once the Response arrives. Its badges number its own four hops, not the six steps of the list. The gap and the controls are covered in "Signature wrapping, parser differentials and canonicalization" and the replay cache in "Replay, unsolicited responses and RelayState".

Every hop of the end-to-end flow crosses the user agent.

1. The user agent requests a protected resource and the SP has no security context.
2. The SP issues an `AuthnRequest` by Redirect, POST or Artifact (profile 4.1.2). Redirect: DEFLATE, base64, URL-encode, answered with 302 or 303; the XML signature is removed and replaced by `SigAlg` and `Signature` computed over the concatenated, still URL-encoded `SAMLRequest`, `RelayState` and `SigAlg` parameters (bindings 3.4.4.1).
3. The user agent GETs the IdP's SSO endpoint. An unauthenticated request "MUST NOT be trusted except as advisory", and the IdP MUST verify that any `AssertionConsumerServiceURL` or index belongs to the SP, because failure "can result in a man-in-the-middle attack" (4.1.4.1).
4. The IdP identifies the principal by a new authentication or an existing session; `ForceAuthn` obliges a fresh one (4.1.3.4). It then returns the `Response` by POST or Artifact, never Redirect: an HTML form carrying `SAMLResponse`.
5. The user agent POSTs that form to the ACS URL. With POST the assertions MUST be signed. If the message is signed, `Destination` MUST be present and the recipient MUST check it equals the receiving URL (bindings 3.5.5.2).
6. The SP processes the Response and may establish its security context "using any session mechanism it chooses" (4.1.3.6).

What the profile obliges the SP to do (4.1.4.3, 4.1.4.5): verify signatures on the assertions or response; verify `Recipient` in the bearer `SubjectConfirmationData` equals the ACS URL the message reached; verify its `NotOnOrAfter` has not passed, "subject to allowable clock skew"; verify `InResponseTo` equals the request's ID unless the response is unsolicited, in which case it MUST be absent; verify that any assertion it relies on is valid in other respects (the `AudienceRestriction` naming the SP is one such respect; 4.1.4.2 requires the IdP to include it). An assertion that fails any check SHOULD be discarded and SHOULD NOT establish a security context; that one is a SHOULD, not a MUST. With the POST binding the SP also MUST NOT accept a bearer assertion twice, by keeping used IDs for as long as `NotOnOrAfter` would keep the assertion valid (4.1.4.5). If the `AuthnStatement` carries `SessionNotOnOrAfter`, the security context SHOULD be discarded then.

<!-- diagram:saml-response-anatomy -->
<div class="smr-wrap" style="position:relative">
<input type="checkbox" id="smr-pause" class="smr-cb" /><label for="smr-pause" class="smr-btn"><span class="smr-off">Pause animation</span><span class="smr-on">Play animation</span></label>
<div class="smr-box" style="overflow-x:auto">
<svg class="smr-flow" viewBox="0 0 760 549" role="img" aria-labelledby="smr-t smr-d" style="width:760px;max-width:100%;min-width:699px;height:auto;display:block;margin:0 auto">
<title id="smr-t">What the SP must check, part by part (profile and signature profile)</title>
<desc id="smr-d">A nested diagram of a Response and its Assertion, with callouts for what the profile requires. On the Response, if the message is signed Destination must be present and must equal the receiving URL; InResponseTo must equal the request's ID, or be absent when the response is unsolicited. The Assertion must be signed with the POST binding, and with POST the SP must not accept a bearer assertion twice, keeping used IDs for as long as NotOnOrAfter would keep it valid. The signature is enveloped with a single same-document Reference of the form URI equals hash ID, and should use exclusive canonicalization and not contain transforms beyond that and enveloped-signature. The bearer SubjectConfirmationData Recipient must equal the ACS URL the message reached and its NotOnOrAfter must not have passed, subject to allowable clock skew. The Conditions AudienceRestriction is one respect in which the assertion must be valid; the IdP must include it. A SessionNotOnOrAfter in the AuthnStatement means the SP should discard its security context at that time. The diagram highlights each part in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
<style>
svg.smr-flow{--ink:light-dark(#000000,#ffffff)}
.smr-box{fill:var(--panel);stroke:var(--border-strong);stroke-width:1.5}
.smr-hot{fill:var(--panel);stroke:var(--accent);stroke-width:2.5}
.smr-ttl{fill:var(--ink);font:600 15px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.smr-sub{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.smr-life{stroke:var(--border-strong);stroke-width:1.5;stroke-dasharray:4 5}
.smr-front{stroke:var(--accent);stroke-width:2;fill:none}
.smr-back{stroke:var(--muted);stroke-width:2;stroke-dasharray:7 5;fill:none}
.smr-bad{stroke:var(--bad);stroke-width:2;fill:none}
.smr-main{fill:var(--ink);font:600 13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.smr-badt{fill:var(--ink)}
.smr-dim{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.smr-badge{fill:var(--accent)}
.smr-b-back{fill:var(--muted)}
.smr-b-bad{fill:var(--bad)}
.smr-b-good{fill:var(--good)}
.smr-bt{fill:var(--on-accent);font:700 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.smr-note{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.smr-note-good{fill:var(--good-bg);stroke:var(--good);stroke-width:1.5}
.smr-note-bad{fill:var(--bad-bg);stroke:var(--bad);stroke-width:1.5}
.smr-nt{fill:var(--ink);font:500 12.5px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.smr-nest{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.smr-row{fill:var(--raised);stroke:var(--border-strong);stroke-width:1}
.smr-ttlL{fill:var(--ink);font:600 14px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.smr-subL{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.smr-dimL{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.smr-dimR{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:end}
.smr-conn{stroke:var(--accent);stroke-width:1.5;fill:none}
.smr-edge{stroke:var(--border-strong);stroke-width:1.75;fill:none}
.smr-hl{fill:none;stroke:var(--accent);stroke-width:3}
.smr-hle{stroke:var(--accent);stroke-width:3;fill:none}
.smr-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:28s;animation-timing-function:linear;animation-iteration-count:infinite}
.smr-pk.smr-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.smr-pk.smr-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.smr-wrap{margin:20px 0}
@media (min-width:801px){.smr-wrap{margin-left:-44px;margin-right:-44px}}
.smr-g rect,.smr-g line,.smr-g path:not(.smr-gl){opacity:.5;animation-duration:28s;animation-timing-function:linear;animation-iteration-count:infinite}
.smr-h{opacity:0;animation-duration:28s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.smr-flow:hover .smr-g rect,svg.smr-flow:hover .smr-g line,svg.smr-flow:hover .smr-g path:not(.smr-gl),svg.smr-flow:hover .smr-pk,svg.smr-flow:hover .smr-h{animation-play-state:paused}
.smr-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.smr-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.smr-btn:hover{background:var(--hover)}
.smr-cb:focus-visible + .smr-btn{outline:2px solid var(--accent);outline-offset:2px}
.smr-cb:checked + .smr-btn .smr-off,.smr-cb:not(:checked) + .smr-btn .smr-on{display:none}
.smr-cb:checked ~ .smr-box .smr-g rect,.smr-cb:checked ~ .smr-box .smr-g line,.smr-cb:checked ~ .smr-box .smr-g path:not(.smr-gl),.smr-cb:checked ~ .smr-box .smr-pk,.smr-cb:checked ~ .smr-box .smr-h{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.smr-g rect,.smr-g line,.smr-g path:not(.smr-gl){animation:none;opacity:1}.smr-pk{animation:none;display:none}.smr-h{animation:none;opacity:0}.smr-btn{display:none}}
@keyframes smr-g0{0%{opacity:1}14.286%{opacity:1}14.296%,100%{opacity:.5}}
@keyframes smr-h0{0%{opacity:1}14.286%{opacity:1}14.296%,100%{opacity:0}}
.smr-g0 rect,.smr-g0 line,.smr-g0 path:not(.smr-gl){animation-name:smr-g0}.smr-h0{animation-name:smr-h0}
@keyframes smr-g1{0%,14.276%{opacity:.5}14.286%{opacity:1}28.571%{opacity:1}28.581%,100%{opacity:.5}}
@keyframes smr-h1{0%,14.276%{opacity:0}14.286%{opacity:1}28.571%{opacity:1}28.581%,100%{opacity:0}}
.smr-g1 rect,.smr-g1 line,.smr-g1 path:not(.smr-gl){animation-name:smr-g1}.smr-h1{animation-name:smr-h1}
@keyframes smr-g2{0%,28.561%{opacity:.5}28.571%{opacity:1}42.857%{opacity:1}42.867%,100%{opacity:.5}}
@keyframes smr-h2{0%,28.561%{opacity:0}28.571%{opacity:1}42.857%{opacity:1}42.867%,100%{opacity:0}}
.smr-g2 rect,.smr-g2 line,.smr-g2 path:not(.smr-gl){animation-name:smr-g2}.smr-h2{animation-name:smr-h2}
@keyframes smr-g3{0%,42.847%{opacity:.5}42.857%{opacity:1}57.143%{opacity:1}57.153%,100%{opacity:.5}}
@keyframes smr-h3{0%,42.847%{opacity:0}42.857%{opacity:1}57.143%{opacity:1}57.153%,100%{opacity:0}}
.smr-g3 rect,.smr-g3 line,.smr-g3 path:not(.smr-gl){animation-name:smr-g3}.smr-h3{animation-name:smr-h3}
@keyframes smr-g4{0%,57.133%{opacity:.5}57.143%{opacity:1}71.429%{opacity:1}71.439%,100%{opacity:.5}}
@keyframes smr-h4{0%,57.133%{opacity:0}57.143%{opacity:1}71.429%{opacity:1}71.439%,100%{opacity:0}}
.smr-g4 rect,.smr-g4 line,.smr-g4 path:not(.smr-gl){animation-name:smr-g4}.smr-h4{animation-name:smr-h4}
@keyframes smr-g5{0%,71.419%{opacity:.5}71.429%{opacity:1}85.714%{opacity:1}85.724%,100%{opacity:.5}}
@keyframes smr-h5{0%,71.419%{opacity:0}71.429%{opacity:1}85.714%{opacity:1}85.724%,100%{opacity:0}}
.smr-g5 rect,.smr-g5 line,.smr-g5 path:not(.smr-gl){animation-name:smr-g5}.smr-h5{animation-name:smr-h5}
@keyframes smr-g6{0%,85.704%{opacity:.5}85.714%{opacity:1}100%{opacity:1}100.01%,100%{opacity:.5}}
@keyframes smr-h6{0%,85.704%{opacity:0}85.714%{opacity:1}100%{opacity:1}100.01%,100%{opacity:0}}
.smr-g6 rect,.smr-g6 line,.smr-g6 path:not(.smr-gl){animation-name:smr-g6}.smr-h6{animation-name:smr-h6}
</style>
<defs>
<marker id="smr-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="smr-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="smr-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<rect class="smr-box" x="14" y="16" width="440" height="378" rx="9"/><text class="smr-ttlL" x="28" y="37">Response</text><text class="smr-subL" x="28" y="54">Destination, InResponseTo</text>
<rect class="smr-nest" x="26" y="62" width="416" height="46" rx="9"/><text class="smr-ttlL" x="40" y="83">InResponseTo</text><text class="smr-subL" x="40" y="100">the request's ID</text>
<rect class="smr-nest" x="26" y="116" width="416" height="266" rx="9"/><text class="smr-ttlL" x="40" y="137">Assertion</text><text class="smr-subL" x="40" y="154">with POST: MUST be signed</text>
<rect class="smr-nest" x="38" y="162" width="392" height="46" rx="9"/><text class="smr-ttlL" x="52" y="183">Signature</text><text class="smr-subL" x="52" y="200">enveloped, one Reference</text>
<rect class="smr-nest" x="38" y="216" width="392" height="46" rx="9"/><text class="smr-ttlL" x="52" y="237">SubjectConfirmationData</text><text class="smr-subL" x="52" y="254">bearer: Recipient, NotOnOrAfter</text>
<rect class="smr-nest" x="38" y="270" width="392" height="46" rx="9"/><text class="smr-ttlL" x="52" y="291">Conditions</text><text class="smr-subL" x="52" y="308">AudienceRestriction</text>
<rect class="smr-nest" x="38" y="324" width="392" height="46" rx="9"/><text class="smr-ttlL" x="52" y="345">AuthnStatement</text><text class="smr-subL" x="52" y="362">SessionNotOnOrAfter</text>
<g class="smr-g smr-g0">
<path class="smr-conn" d="M454,33 L462,33 L462,34 L470,34" marker-end="url(#smr-m-front)"/>
<rect class="smr-note-good" x="484" y="10" width="262" height="48" rx="8"/>
<text class="smr-nt" x="615" y="31">If signed: Destination MUST be present</text>
<text class="smr-nt" x="615" y="48">and MUST equal the receiving URL</text>
<circle class="smr-badge smr-b-good" cx="484" cy="34" r="12"/><text class="smr-bt" x="484" y="38.5">1</text>
</g>
<g class="smr-g smr-g1">
<path class="smr-conn" d="M442,79 L466,79 L466,92 L470,92" marker-end="url(#smr-m-front)"/>
<rect class="smr-note-good" x="484" y="68" width="262" height="48" rx="8"/>
<text class="smr-nt" x="615" y="89">Equals the request's ID; MUST be</text>
<text class="smr-nt" x="615" y="106">absent if the response is unsolicited</text>
<circle class="smr-badge smr-b-good" cx="484" cy="92" r="12"/><text class="smr-bt" x="484" y="96.5">2</text>
</g>
<g class="smr-g smr-g2">
<path class="smr-conn" d="M442,133 L470,133 L470,158 L470,158" marker-end="url(#smr-m-front)"/>
<rect class="smr-note-good" x="484" y="126" width="262" height="65" rx="8"/>
<text class="smr-nt" x="615" y="147">POST: MUST NOT accept a bearer</text>
<text class="smr-nt" x="615" y="164">assertion twice; keep used IDs while</text>
<text class="smr-nt" x="615" y="181">NotOnOrAfter would keep it valid</text>
<circle class="smr-badge smr-b-good" cx="484" cy="158" r="12"/><text class="smr-bt" x="484" y="163.0">3</text>
</g>
<g class="smr-g smr-g3">
<path class="smr-conn" d="M430,179 L474,179 L474,242 L470,242" marker-end="url(#smr-m-front)"/>
<rect class="smr-note-good" x="484" y="201" width="262" height="82" rx="8"/>
<text class="smr-nt" x="615" y="222">Verify it. Same-document Reference</text>
<text class="smr-nt" x="615" y="239">URI="#ID"; SHOULD use exclusive c14n,</text>
<text class="smr-nt" x="615" y="256">SHOULD NOT add transforms beyond</text>
<text class="smr-nt" x="615" y="273">that and enveloped-signature</text>
<circle class="smr-badge smr-b-good" cx="484" cy="242" r="12"/><text class="smr-bt" x="484" y="246.5">4</text>
</g>
<g class="smr-g smr-g4">
<path class="smr-conn" d="M430,233 L462,233 L462,326 L470,326" marker-end="url(#smr-m-front)"/>
<rect class="smr-note-good" x="484" y="293" width="262" height="65" rx="8"/>
<text class="smr-nt" x="615" y="314">Recipient = the ACS URL it reached;</text>
<text class="smr-nt" x="615" y="331">NotOnOrAfter not passed, subject to</text>
<text class="smr-nt" x="615" y="348">allowable clock skew</text>
<circle class="smr-badge smr-b-good" cx="484" cy="326" r="12"/><text class="smr-bt" x="484" y="330.0">5</text>
</g>
<g class="smr-g smr-g5">
<path class="smr-conn" d="M430,287 L466,287 L466,400 L470,400" marker-end="url(#smr-m-front)"/>
<rect class="smr-note-good" x="484" y="368" width="262" height="65" rx="8"/>
<text class="smr-nt" x="615" y="389">Assertion must be valid in other</text>
<text class="smr-nt" x="615" y="406">respects: the IdP MUST include it,</text>
<text class="smr-nt" x="615" y="423">the SP checks it names the SP</text>
<circle class="smr-badge smr-b-good" cx="484" cy="400" r="12"/><text class="smr-bt" x="484" y="405.0">6</text>
</g>
<g class="smr-g smr-g6">
<path class="smr-conn" d="M430,341 L470,341 L470,467 L470,467" marker-end="url(#smr-m-front)"/>
<rect class="smr-note" x="484" y="443" width="262" height="48" rx="8"/>
<text class="smr-nt" x="615" y="464">If present, the SP SHOULD discard</text>
<text class="smr-nt" x="615" y="481">its security context at that time</text>
<circle class="smr-badge smr-b-front" cx="484" cy="467" r="12"/><text class="smr-bt" x="484" y="471.5">7</text>
</g>
<g class="smr-h smr-h0">
<rect class="smr-hl" x="14" y="16" width="440" height="378" rx="9"/>
</g>
<g class="smr-h smr-h1">
<rect class="smr-hl" x="26" y="62" width="416" height="46" rx="9"/>
</g>
<g class="smr-h smr-h2">
<rect class="smr-hl" x="26" y="116" width="416" height="266" rx="9"/>
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
<rect class="smr-note" x="40" y="517" width="22" height="16" rx="4"/>
<text class="smr-dim" x="70" y="529" style="text-anchor:start">SHOULD</text>
<rect class="smr-note-good" x="142" y="517" width="22" height="16" rx="4"/>
<text class="smr-dim" x="172" y="529" style="text-anchor:start">obligation</text>
</svg>
</div>
</div>
<!-- /diagram:saml-response-anatomy -->

The paragraph above, plus the signature profile from the next section, laid out by element: each green part carries something the profile or core 5.4 obliges the SP to verify, and the plain part is a SHOULD. The numbers follow the parts from the outside in.

## What the signature covers

The profile says assertions MUST be signed with POST and leaves signing the Response optional. Core 5.3 says an unsigned assertion may inherit the signature of an enclosing element when the signature "applies to the `Assertion` element and all its children"; the introduction to core section 5 adds that inherited signatures need care for assertions meant to be long-lived, because the whole signed context must be retained. So the documents pull in different directions, and implementations can differ. Pick a rule per integration and write it down: require a verified signature whose Reference is the Assertion, or accept a verified Response signature only when the Assertion you consume is a descendant of the element that Reference resolved to. SP metadata can state `WantAssertionsSigned`; the IdP is "not obligated" by it.

The signature profile (core 5.4) is narrow. Signatures are enveloped, carry a single same-document `ds:Reference` of the form `URI="#ID"` for the root element signed, SHOULD use exclusive canonicalization, and SHOULD NOT contain transforms beyond enveloped-signature and exclusive c14n; a verifier MAY reject other transforms, and if it does not it MUST make sure no content is excluded. `ds:KeyInfo` MAY be absent and SAML places no restriction on it. XML Signature core validation has two steps, reference validation (digest each Reference) and signature validation over canonical `SignedInfo`, and key material may come "from `KeyInfo` or from an external source" (XMLDSig 3.2). My conclusion, not the spec's: take the verification key only from IdP metadata you pinned, never from the message.

Encryption: an `EncryptedAssertion` is "a confidentiality protection mechanism when the plain-text value passes through an intermediary" (core 2.3.4). Order matters (core 6.2): a signed assertion that is then encrypted has its signature inside the ciphertext, so decrypt first, then verify. An encrypted `NameID` or `Attribute` is the reverse: encryption was done first and the signature covers the enclosing assertion, so verify first, then decrypt. The rule is that signature validation and decryption run "in the reverse order that signing and encryption were performed".

## Signature wrapping, parser differentials and canonicalization

Core validation shows that some element still matches a signed digest. It does not show that the element your code reads next is that element. XML Signature 1.1 makes the related point in its own terms: a consumer "should operate over the data that was transformed (including canonicalization) and signed, not the original pre-transformed data" (8.1.3; 8.1.1 adds, about transforms, "only what is signed is secure"). Signature wrapping (XSW) lives in that gap. My summary of the class: the validly signed element stays where the verifier finds it by ID, and a forged element is placed where the application's own lookup finds it first. The verifier and the business logic read different nodes.

<!-- diagram:saml-xsw -->
<div class="l02d-wrap" style="position:relative">
<input type="checkbox" id="l02d-pause" class="l02d-cb" /><label for="l02d-pause" class="l02d-btn"><span class="l02d-off">Pause animation</span><span class="l02d-on">Play animation</span></label>
<div class="l02d-box" style="overflow-x:auto">
<svg class="l02d-flow" viewBox="0 0 760 365" role="img" aria-labelledby="l02d-t l02d-d" style="width:760px;max-width:100%;min-width:699px;height:auto;display:block;margin:0 auto">
<title id="l02d-t">A wrapped Response: what the signature proves and what the code reads</title>
<desc id="l02d-d">A nested diagram of the wrapped copy of the sample Response, which holds two Assertions. The first, ID _evil, is unsigned and carries a forged NameID, admin@example.com; a naive first-assertion lookup reads it. The second, ID _assert1, is the genuine one the signature's Reference points at; the verifier finds it by the Reference ID. Inside it the Signature has a Reference with URI _assert1, which shows that some element still matches a signed digest but not that the element the code reads next is that element. Its NameID, u-7f3a9c21, is the value the control reads, by resolving the verified Reference and reading every security-relevant value from that node. The Response callout adds the control of rejecting a document whose Assertion count is not what you expect. The diagram highlights each part in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
<style>
svg.l02d-flow{--ink:light-dark(#000000,#ffffff)}
.l02d-box{fill:var(--panel);stroke:var(--border-strong);stroke-width:1.5}
.l02d-hot{fill:var(--panel);stroke:var(--accent);stroke-width:2.5}
.l02d-ttl{fill:var(--ink);font:600 15px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l02d-sub{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l02d-life{stroke:var(--border-strong);stroke-width:1.5;stroke-dasharray:4 5}
.l02d-front{stroke:var(--accent);stroke-width:2;fill:none}
.l02d-back{stroke:var(--muted);stroke-width:2;stroke-dasharray:7 5;fill:none}
.l02d-bad{stroke:var(--bad);stroke-width:2;fill:none}
.l02d-main{fill:var(--ink);font:600 13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l02d-badt{fill:var(--ink)}
.l02d-dim{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l02d-badge{fill:var(--accent)}
.l02d-b-back{fill:var(--muted)}
.l02d-b-bad{fill:var(--bad)}
.l02d-b-good{fill:var(--good)}
.l02d-bt{fill:var(--on-accent);font:700 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l02d-note{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l02d-note-good{fill:var(--good-bg);stroke:var(--good);stroke-width:1.5}
.l02d-note-bad{fill:var(--bad-bg);stroke:var(--bad);stroke-width:1.5}
.l02d-nt{fill:var(--ink);font:500 12.5px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l02d-nest{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l02d-row{fill:var(--raised);stroke:var(--border-strong);stroke-width:1}
.l02d-ttlL{fill:var(--ink);font:600 14px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l02d-subL{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l02d-dimL{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l02d-dimR{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:end}
.l02d-conn{stroke:var(--accent);stroke-width:1.5;fill:none}
.l02d-edge{stroke:var(--border-strong);stroke-width:1.75;fill:none}
.l02d-hl{fill:none;stroke:var(--accent);stroke-width:3}
.l02d-hle{stroke:var(--accent);stroke-width:3;fill:none}
.l02d-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:22s;animation-timing-function:linear;animation-iteration-count:infinite}
.l02d-pk.l02d-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.l02d-pk.l02d-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.l02d-wrap{margin:20px 0}
@media (min-width:801px){.l02d-wrap{margin-left:-44px;margin-right:-44px}}
.l02d-g rect,.l02d-g line,.l02d-g path:not(.l02d-gl){opacity:.5;animation-duration:22s;animation-timing-function:linear;animation-iteration-count:infinite}
.l02d-h{opacity:0;animation-duration:22s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.l02d-flow:hover .l02d-g rect,svg.l02d-flow:hover .l02d-g line,svg.l02d-flow:hover .l02d-g path:not(.l02d-gl),svg.l02d-flow:hover .l02d-pk,svg.l02d-flow:hover .l02d-h{animation-play-state:paused}
.l02d-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.l02d-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.l02d-btn:hover{background:var(--hover)}
.l02d-cb:focus-visible + .l02d-btn{outline:2px solid var(--accent);outline-offset:2px}
.l02d-cb:checked + .l02d-btn .l02d-off,.l02d-cb:not(:checked) + .l02d-btn .l02d-on{display:none}
.l02d-cb:checked ~ .l02d-box .l02d-g rect,.l02d-cb:checked ~ .l02d-box .l02d-g line,.l02d-cb:checked ~ .l02d-box .l02d-g path:not(.l02d-gl),.l02d-cb:checked ~ .l02d-box .l02d-pk,.l02d-cb:checked ~ .l02d-box .l02d-h{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.l02d-g rect,.l02d-g line,.l02d-g path:not(.l02d-gl){animation:none;opacity:1}.l02d-pk{animation:none;display:none}.l02d-h{animation:none;opacity:0}.l02d-btn{display:none}}
@keyframes l02d-g0{0%{opacity:1}20%{opacity:1}20.01%,100%{opacity:.5}}
@keyframes l02d-h0{0%{opacity:1}20%{opacity:1}20.01%,100%{opacity:0}}
.l02d-g0 rect,.l02d-g0 line,.l02d-g0 path:not(.l02d-gl){animation-name:l02d-g0}.l02d-h0{animation-name:l02d-h0}
@keyframes l02d-g1{0%,19.99%{opacity:.5}20%{opacity:1}40%{opacity:1}40.01%,100%{opacity:.5}}
@keyframes l02d-h1{0%,19.99%{opacity:0}20%{opacity:1}40%{opacity:1}40.01%,100%{opacity:0}}
.l02d-g1 rect,.l02d-g1 line,.l02d-g1 path:not(.l02d-gl){animation-name:l02d-g1}.l02d-h1{animation-name:l02d-h1}
@keyframes l02d-g2{0%,39.99%{opacity:.5}40%{opacity:1}60%{opacity:1}60.01%,100%{opacity:.5}}
@keyframes l02d-h2{0%,39.99%{opacity:0}40%{opacity:1}60%{opacity:1}60.01%,100%{opacity:0}}
.l02d-g2 rect,.l02d-g2 line,.l02d-g2 path:not(.l02d-gl){animation-name:l02d-g2}.l02d-h2{animation-name:l02d-h2}
@keyframes l02d-g3{0%,59.99%{opacity:.5}60%{opacity:1}80%{opacity:1}80.01%,100%{opacity:.5}}
@keyframes l02d-h3{0%,59.99%{opacity:0}60%{opacity:1}80%{opacity:1}80.01%,100%{opacity:0}}
.l02d-g3 rect,.l02d-g3 line,.l02d-g3 path:not(.l02d-gl){animation-name:l02d-g3}.l02d-h3{animation-name:l02d-h3}
@keyframes l02d-g4{0%,79.99%{opacity:.5}80%{opacity:1}100%{opacity:1}100.01%,100%{opacity:.5}}
@keyframes l02d-h4{0%,79.99%{opacity:0}80%{opacity:1}100%{opacity:1}100.01%,100%{opacity:0}}
.l02d-g4 rect,.l02d-g4 line,.l02d-g4 path:not(.l02d-gl){animation-name:l02d-g4}.l02d-h4{animation-name:l02d-h4}
</style>
<defs>
<marker id="l02d-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="l02d-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="l02d-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<rect class="l02d-box" x="14" y="16" width="440" height="270" rx="9"/><text class="l02d-ttlL" x="28" y="37">Response</text><text class="l02d-subL" x="28" y="54">the wrapped copy: two Assertions</text>
<rect class="l02d-nest" x="26" y="62" width="416" height="46" rx="9"/><text class="l02d-ttlL" x="40" y="83">Assertion ID="_evil"</text><text class="l02d-subL" x="40" y="100">unsigned, forged NameID</text>
<rect class="l02d-nest" x="26" y="116" width="416" height="158" rx="9"/><text class="l02d-ttlL" x="40" y="137">Assertion ID="_assert1"</text><text class="l02d-subL" x="40" y="154">the genuine one the Reference points at</text>
<rect class="l02d-nest" x="38" y="162" width="392" height="46" rx="9"/><text class="l02d-ttlL" x="52" y="183">Signature</text><text class="l02d-subL" x="52" y="200">Reference URI="#_assert1"</text>
<rect class="l02d-nest" x="38" y="216" width="392" height="46" rx="9"/><text class="l02d-ttlL" x="52" y="237">NameID</text><text class="l02d-subL" x="52" y="254">u-7f3a9c21</text>
<g class="l02d-g l02d-g0">
<path class="l02d-conn" d="M454,33 L462,33 L462,34 L470,34" marker-end="url(#l02d-m-front)"/>
<rect class="l02d-note" x="484" y="10" width="262" height="48" rx="8"/>
<text class="l02d-nt" x="615" y="31">Control: reject a document whose</text>
<text class="l02d-nt" x="615" y="48">Assertion count is not what you expect</text>
<circle class="l02d-badge l02d-b-front" cx="484" cy="34" r="12"/><text class="l02d-bt" x="484" y="38.5">1</text>
</g>
<g class="l02d-g l02d-g1">
<path class="l02d-conn" d="M442,79 L466,79 L466,92 L470,92" marker-end="url(#l02d-m-front)"/>
<rect class="l02d-note-bad" x="484" y="68" width="262" height="48" rx="8"/>
<text class="l02d-nt" x="615" y="89">A "first assertion" lookup reads this</text>
<text class="l02d-nt" x="615" y="106">one: admin@example.com</text>
<circle class="l02d-badge l02d-b-bad" cx="484" cy="92" r="12"/><text class="l02d-bt" x="484" y="96.5">2</text>
</g>
<g class="l02d-g l02d-g2">
<path class="l02d-conn" d="M442,133 L470,133 L470,150 L470,150" marker-end="url(#l02d-m-front)"/>
<rect class="l02d-note-good" x="484" y="126" width="262" height="48" rx="8"/>
<text class="l02d-nt" x="615" y="147">The verifier finds this one by the</text>
<text class="l02d-nt" x="615" y="164">Reference's ID</text>
<circle class="l02d-badge l02d-b-good" cx="484" cy="150" r="12"/><text class="l02d-bt" x="484" y="154.5">3</text>
</g>
<g class="l02d-g l02d-g3">
<path class="l02d-conn" d="M430,179 L474,179 L474,208 L470,208" marker-end="url(#l02d-m-front)"/>
<rect class="l02d-note-good" x="484" y="184" width="262" height="48" rx="8"/>
<text class="l02d-nt" x="615" y="205">Shows some element matches a signed</text>
<text class="l02d-nt" x="615" y="222">digest, not that your code reads it</text>
<circle class="l02d-badge l02d-b-good" cx="484" cy="208" r="12"/><text class="l02d-bt" x="484" y="212.5">4</text>
</g>
<g class="l02d-g l02d-g4">
<path class="l02d-conn" d="M430,233 L462,233 L462,274 L470,274" marker-end="url(#l02d-m-front)"/>
<rect class="l02d-note-good" x="484" y="242" width="262" height="65" rx="8"/>
<text class="l02d-nt" x="615" y="263">Control: resolve the verified</text>
<text class="l02d-nt" x="615" y="280">Reference; read every security-</text>
<text class="l02d-nt" x="615" y="297">relevant value from it</text>
<circle class="l02d-badge l02d-b-good" cx="484" cy="274" r="12"/><text class="l02d-bt" x="484" y="279.0">5</text>
</g>
<g class="l02d-h l02d-h0">
<rect class="l02d-hl" x="14" y="16" width="440" height="270" rx="9"/>
</g>
<g class="l02d-h l02d-h1">
<rect class="l02d-hl" x="26" y="62" width="416" height="46" rx="9"/>
</g>
<g class="l02d-h l02d-h2">
<rect class="l02d-hl" x="26" y="116" width="416" height="158" rx="9"/>
</g>
<g class="l02d-h l02d-h3">
<rect class="l02d-hl" x="38" y="162" width="392" height="46" rx="9"/>
</g>
<g class="l02d-h l02d-h4">
<rect class="l02d-hl" x="38" y="216" width="392" height="46" rx="9"/>
</g>
<rect class="l02d-note" x="40" y="333" width="22" height="16" rx="4"/>
<text class="l02d-dim" x="70" y="345" style="text-anchor:start">context</text>
<rect class="l02d-note-good" x="148" y="333" width="22" height="16" rx="4"/>
<text class="l02d-dim" x="178" y="345" style="text-anchor:start">the signed element</text>
<rect class="l02d-note-bad" x="327" y="333" width="22" height="16" rx="4"/>
<text class="l02d-dim" x="357" y="345" style="text-anchor:start">forged, unsigned</text>
</svg>
</div>
</div>
<!-- /diagram:saml-xsw -->

This is the wrapped copy from the task at the end of the lesson. Read the two Assertions top to bottom: the lookup of "the first Assertion" lands on the forged one, while the signature's Reference points at the lower one. The signature in the sample is a placeholder, not a real one (see the task); the picture shows the structure, not a verified signature. The numbers follow the parts from the outside in.

- **The research.** Somorovsky et al. (USENIX Security 2012) analysed 14 SAML frameworks and found critical XSW flaws in 11, including Salesforce, Shibboleth and IBM XS40 (abstract). They model it as information flow between two relying-party components, signature verification and assertion processing, which also yields the countermeasures.
- **CVE-2025-25291 and CVE-2025-25292.** ruby-saml, GitHub advisories published 2025-03-12, CVSS 9.8. The advisories say authentication bypass "due to a parser differential": REXML and Nokogiri "parse XML differently", producing "entirely different document structures from the same XML input", which allows a signature wrapping attack. The titles name DOCTYPE handling and namespace handling. Fixed in 1.18.0 (1.12.4 on the 1.12 line). The advisories give no exploit detail and I did not verify any.
- **CVE-2024-45409.** ruby-saml, published 2024-09-10, CVSS 10.0 (GitHub's score; NVD's own is 9.8): it "does not properly verify the signature of the SAML Response", so an unauthenticated attacker holding any document signed by the IdP can forge a Response with arbitrary contents and log in as any user. GitHub's title ends "via Incorrect XPath selector". Fixed in 1.17.0 (1.12.3 on the 1.12 line).
- **CVE-2017-11427.** python-saml 2.3.0 and earlier, per NVD, "may incorrectly utilize the results of XML DOM traversal and canonicalization APIs" so an attacker can change the SAML data without invalidating the signature. That is the canonicalization class: per CERT/CC VU#475445, these APIs handle XML comments inconsistently, so text after a comment inside a node is lost before the digest is computed, and an attacker can change it without breaking the signature. It is a comment-handling bug, not a wrapping bug; CERT/CC lists six affected libraries, python-saml among them.

Controls (design recommendations drawn from the class, not spec rules): verify and extract from one parsed tree, never two parsers; after verification, resolve the verified Reference to its element and read every security-relevant value from that node, not from a fresh whole-document XPath; reject a document whose `Assertion` count is not what you expect or in which an `ID` is declared twice (core 1.3.4 requires exactly one declaration); allowlist algorithms, transforms and canonicalization methods; schema-validate and refuse a `DOCTYPE`; and treat library patch latency as a control, since every case above was a widely used library.

## Replay, unsolicited responses and RelayState

**Replay.** Bearer means possession is enough. The mandated defence is the ID cache (4.1.4.5). IDs make sound keys because randomly generated ones must collide with probability at most 2^-128 (core 1.3.4). My reasoning on sizing: if you accept responses a few minutes past `NotOnOrAfter` for skew, hold each ID until `NotOnOrAfter` plus that allowance, or the leniency window becomes a replay window; and the cache must be shared by every node behind the load balancer, with an atomic check-and-insert: per-node caches, even with sticky sessions, fail because the attacker replaying a Response, not the SP, chooses which node receives it. `InResponseTo` is the second control: store each outstanding `AuthnRequest` ID with an expiry and consume it on first use. That covers only SP-initiated Responses (an unsolicited one carries none), so it does not remove the ID-cache requirement. A `OneTimeUse` condition adds an expectation that the relying party keeps its own cache (core 2.5.1.5).

<!-- diagram:saml-replay -->
<div class="l02e-wrap" style="position:relative">
<input type="checkbox" id="l02e-pause" class="l02e-cb" /><label for="l02e-pause" class="l02e-btn"><span class="l02e-off">Pause animation</span><span class="l02e-on">Play animation</span></label>
<div class="l02e-box" style="overflow-x:auto">
<svg class="l02e-flow" viewBox="0 0 760 731" role="img" aria-labelledby="l02e-t l02e-d" style="width:760px;max-width:100%;min-width:699px;height:auto;display:block;margin:0 auto">
<title id="l02e-t">Replay: why the ID cache should be shared by every node (my reasoning)</title>
<desc id="l02e-d">The shared, atomic cache shown here is the lesson's reasoning, not a profile requirement. Four parts: the client, SP node A, SP node B, and the ID cache. The client POSTs a Response to node A, which does an atomic check-and-insert of the assertion ID in the shared cache; the ID is new, so it is accepted and held for as long as NotOnOrAfter would keep the assertion valid. An attacker then replays the same Response to node B, which does the same check-and-insert; the ID is already stored, so the replay is not accepted. A per-node cache would fail here, even with sticky sessions, because the attacker, not the SP, chooses which node receives the Response. The diagram highlights each step in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
<style>
svg.l02e-flow{--ink:light-dark(#000000,#ffffff)}
.l02e-box{fill:var(--panel);stroke:var(--border-strong);stroke-width:1.5}
.l02e-hot{fill:var(--panel);stroke:var(--accent);stroke-width:2.5}
.l02e-ttl{fill:var(--ink);font:600 15px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l02e-sub{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l02e-life{stroke:var(--border-strong);stroke-width:1.5;stroke-dasharray:4 5}
.l02e-front{stroke:var(--accent);stroke-width:2;fill:none}
.l02e-back{stroke:var(--muted);stroke-width:2;stroke-dasharray:7 5;fill:none}
.l02e-bad{stroke:var(--bad);stroke-width:2;fill:none}
.l02e-main{fill:var(--ink);font:600 13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l02e-badt{fill:var(--ink)}
.l02e-dim{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l02e-badge{fill:var(--accent)}
.l02e-b-back{fill:var(--muted)}
.l02e-b-bad{fill:var(--bad)}
.l02e-b-good{fill:var(--good)}
.l02e-bt{fill:var(--on-accent);font:700 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l02e-note{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l02e-note-good{fill:var(--good-bg);stroke:var(--good);stroke-width:1.5}
.l02e-note-bad{fill:var(--bad-bg);stroke:var(--bad);stroke-width:1.5}
.l02e-nt{fill:var(--ink);font:500 12.5px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l02e-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:36s;animation-timing-function:linear;animation-iteration-count:infinite}
.l02e-pk.l02e-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.l02e-pk.l02e-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.l02e-wrap{margin:20px 0}
@media (min-width:801px){.l02e-wrap{margin-left:-44px;margin-right:-44px}}
.l02e-g rect,.l02e-g line,.l02e-g path:not(.l02e-gl){opacity:.5;animation-duration:36s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.l02e-flow:hover .l02e-g rect,svg.l02e-flow:hover .l02e-g line,svg.l02e-flow:hover .l02e-g path:not(.l02e-gl),svg.l02e-flow:hover .l02e-pk{animation-play-state:paused}
.l02e-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.l02e-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.l02e-btn:hover{background:var(--hover)}
.l02e-cb:focus-visible + .l02e-btn{outline:2px solid var(--accent);outline-offset:2px}
.l02e-cb:checked + .l02e-btn .l02e-off,.l02e-cb:not(:checked) + .l02e-btn .l02e-on{display:none}
.l02e-cb:checked ~ .l02e-box .l02e-g rect,.l02e-cb:checked ~ .l02e-box .l02e-g line,.l02e-cb:checked ~ .l02e-box .l02e-g path:not(.l02e-gl),.l02e-cb:checked ~ .l02e-box .l02e-pk{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.l02e-g rect,.l02e-g line,.l02e-g path:not(.l02e-gl){animation:none;opacity:1}.l02e-pk{animation:none;display:none}.l02e-btn{display:none}}
@keyframes l02e-g0{0%{opacity:1}16.667%{opacity:1}16.677%,100%{opacity:.5}}
@keyframes l02e-p0{0%,-0.01%{opacity:0;transform:translateX(0)}0%{opacity:1;transform:translateX(0)}13.333%{opacity:1;transform:translateX(146px)}16.667%{opacity:1;transform:translateX(146px)}16.677%,100%{opacity:0;transform:translateX(146px)}}
.l02e-g0 rect,.l02e-g0 line,.l02e-g0 path:not(.l02e-gl){animation-name:l02e-g0}.l02e-p0{animation-name:l02e-p0}
@keyframes l02e-g1{0%,16.657%{opacity:.5}16.667%{opacity:1}33.333%{opacity:1}33.343%,100%{opacity:.5}}
@keyframes l02e-p1{0%,16.657%{opacity:0;transform:translateX(0)}16.667%{opacity:1;transform:translateX(0)}30%{opacity:1;transform:translateX(326px)}33.333%{opacity:1;transform:translateX(326px)}33.343%,100%{opacity:0;transform:translateX(326px)}}
.l02e-g1 rect,.l02e-g1 line,.l02e-g1 path:not(.l02e-gl){animation-name:l02e-g1}.l02e-p1{animation-name:l02e-p1}
@keyframes l02e-g2{0%,33.323%{opacity:.5}33.333%{opacity:1}44.444%{opacity:1}44.454%,100%{opacity:.5}}
.l02e-g2 rect,.l02e-g2 line,.l02e-g2 path:not(.l02e-gl){animation-name:l02e-g2}
@keyframes l02e-g3{0%,44.434%{opacity:.5}44.444%{opacity:1}61.111%{opacity:1}61.121%,100%{opacity:.5}}
@keyframes l02e-p3{0%,44.434%{opacity:0;transform:translateX(0)}44.444%{opacity:1;transform:translateX(0)}57.778%{opacity:1;transform:translateX(326px)}61.111%{opacity:1;transform:translateX(326px)}61.121%,100%{opacity:0;transform:translateX(326px)}}
.l02e-g3 rect,.l02e-g3 line,.l02e-g3 path:not(.l02e-gl){animation-name:l02e-g3}.l02e-p3{animation-name:l02e-p3}
@keyframes l02e-g4{0%,61.101%{opacity:.5}61.111%{opacity:1}77.778%{opacity:1}77.788%,100%{opacity:.5}}
@keyframes l02e-p4{0%,61.101%{opacity:0;transform:translateX(0)}61.111%{opacity:1;transform:translateX(0)}74.444%{opacity:1;transform:translateX(146px)}77.778%{opacity:1;transform:translateX(146px)}77.788%,100%{opacity:0;transform:translateX(146px)}}
.l02e-g4 rect,.l02e-g4 line,.l02e-g4 path:not(.l02e-gl){animation-name:l02e-g4}.l02e-p4{animation-name:l02e-p4}
@keyframes l02e-g5{0%,77.768%{opacity:.5}77.778%{opacity:1}88.889%{opacity:1}88.899%,100%{opacity:.5}}
.l02e-g5 rect,.l02e-g5 line,.l02e-g5 path:not(.l02e-gl){animation-name:l02e-g5}
@keyframes l02e-g6{0%,88.879%{opacity:.5}88.889%{opacity:1}100%{opacity:1}100.01%,100%{opacity:.5}}
.l02e-g6 rect,.l02e-g6 line,.l02e-g6 path:not(.l02e-gl){animation-name:l02e-g6}
</style>
<defs>
<marker id="l02e-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="l02e-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="l02e-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<line class="l02e-life" x1="110" y1="72" x2="110" y2="679"/>
<line class="l02e-life" x1="290" y1="72" x2="290" y2="679"/>
<line class="l02e-life" x1="470" y1="72" x2="470" y2="679"/>
<line class="l02e-life" x1="650" y1="72" x2="650" y2="679"/>
<rect class="l02e-box" x="30" y="10" width="160" height="62" rx="10"/><text class="l02e-ttl" x="110" y="36">Client</text><text class="l02e-sub" x="110" y="56">user, then attacker</text>
<rect class="l02e-hot" x="210" y="10" width="160" height="62" rx="10"/><text class="l02e-ttl" x="290" y="36">SP node A</text><text class="l02e-sub" x="290" y="56">behind the balancer</text>
<rect class="l02e-box" x="390" y="10" width="160" height="62" rx="10"/><text class="l02e-ttl" x="470" y="36">SP node B</text><text class="l02e-sub" x="470" y="56">behind the balancer</text>
<rect class="l02e-box" x="570" y="10" width="160" height="62" rx="10"/><text class="l02e-ttl" x="650" y="36">ID cache</text><text class="l02e-sub" x="650" y="56">shared by every node</text>
<g class="l02e-g l02e-g0">
<text class="l02e-main" x="200" y="108">POST the Response</text>
<text class="l02e-dim" x="200" y="124">to node A</text>
<line class="l02e-front" x1="124" y1="138" x2="276" y2="138" marker-end="url(#l02e-m-front)"/>
<circle class="l02e-badge l02e-b-front" cx="110" cy="138" r="12"/><text class="l02e-bt" x="110" y="142.5">1</text>
</g>
<g class="l02e-g l02e-g1">
<text class="l02e-main" x="470" y="178">check-and-insert</text>
<text class="l02e-dim" x="470" y="194">ID (atomic)</text>
<line class="l02e-front" x1="304" y1="208" x2="636" y2="208" marker-end="url(#l02e-m-front)"/>
<circle class="l02e-badge l02e-b-front" cx="290" cy="208" r="12"/><text class="l02e-bt" x="290" y="212.5">2</text>
</g>
<g class="l02e-g l02e-g2">
<rect class="l02e-note-good" x="560" y="242" width="181" height="65" rx="8"/>
<text class="l02e-nt" x="650" y="263">ID is new: accepted;</text>
<text class="l02e-nt" x="650" y="280">held while NotOnOrAfter</text>
<text class="l02e-nt" x="650" y="297">would keep it valid</text>
</g>
<g class="l02e-g l02e-g3">
<text class="l02e-main l02e-badt" x="290" y="341">Replay the same</text>
<text class="l02e-dim" x="290" y="357">Response to node B</text>
<line class="l02e-bad" x1="124" y1="371" x2="456" y2="371" marker-end="url(#l02e-m-bad)"/>
<circle class="l02e-badge l02e-b-bad" cx="110" cy="371" r="12"/><text class="l02e-bt" x="110" y="375.5">3</text>
</g>
<g class="l02e-g l02e-g4">
<text class="l02e-main" x="560" y="411">check-and-insert</text>
<text class="l02e-dim" x="560" y="427">ID (atomic)</text>
<line class="l02e-front" x1="484" y1="441" x2="636" y2="441" marker-end="url(#l02e-m-front)"/>
<circle class="l02e-badge l02e-b-front" cx="470" cy="441" r="12"/><text class="l02e-bt" x="470" y="445.5">4</text>
</g>
<g class="l02e-g l02e-g5">
<rect class="l02e-note-good" x="575" y="475" width="150" height="48" rx="8"/>
<text class="l02e-nt" x="650" y="496">ID already stored:</text>
<text class="l02e-nt" x="650" y="513">not accepted again</text>
</g>
<g class="l02e-g l02e-g6">
<rect class="l02e-note-bad" x="366" y="551" width="208" height="82" rx="8"/>
<text class="l02e-nt" x="470" y="572">A per-node cache fails: the</text>
<text class="l02e-nt" x="470" y="589">attacker, not the SP, picks</text>
<text class="l02e-nt" x="470" y="606">the node, even with sticky</text>
<text class="l02e-nt" x="470" y="623">sessions</text>
</g>
<circle class="l02e-pk l02e-p0" cx="130" cy="138" r="5.5"/>
<circle class="l02e-pk l02e-p1" cx="310" cy="208" r="5.5"/>
<circle class="l02e-pk l02e-p3 l02e-pkbad" cx="130" cy="371" r="5.5"/>
<circle class="l02e-pk l02e-p4" cx="490" cy="441" r="5.5"/>
<line class="l02e-front" x1="40" y1="707" x2="70" y2="707"/>
<text class="l02e-dim" x="78" y="711" style="text-anchor:start">the Response</text>
<line class="l02e-bad" x1="188" y1="707" x2="218" y2="707"/>
<text class="l02e-dim" x="226" y="711" style="text-anchor:start">the replay</text>
<rect class="l02e-note-good" x="324" y="699" width="22" height="16" rx="4"/>
<text class="l02e-dim" x="354" y="711" style="text-anchor:start">what stops it</text>
</svg>
</div>
</div>
<!-- /diagram:saml-replay -->

Badges number this diagram's own four hops. The first POST is stored in the shared cache; the replay lands on a different node, but the shared cache still holds the ID. A per-node cache fails because the attacker chooses the node. The shared, atomic cache is this lesson's reasoning; the profile itself only requires keeping used IDs (4.1.4.5).

**Unsolicited responses.** IdP-initiated SSO has no `AuthnRequest`, so `InResponseTo` MUST be absent (4.1.5) and the request-binding control is gone. The response goes to the default ACS and `RelayState` is interpreted by prior agreement; the SP SHOULD designate a default landing location. If an integration needs it, compensate: replay cache, short validity, only the registered IdP and ACS, a `RelayState` allowlist, and off by default. Okta's "Single sign-on URL" is the ACS "always used" for IdP-initiated requests.

<!-- diagram:saml-ways-in -->
<div class="l02a-wrap" style="position:relative">
<input type="checkbox" id="l02a-pause" class="l02a-cb" /><label for="l02a-pause" class="l02a-btn"><span class="l02a-off">Pause animation</span><span class="l02a-on">Play animation</span></label>
<div class="l02a-box" style="overflow-x:auto">
<svg class="l02a-flow" viewBox="0 0 760 502" role="img" aria-labelledby="l02a-t l02a-d" style="width:760px;max-width:100%;min-width:699px;height:auto;display:block;margin:0 auto">
<title id="l02a-t">What InResponseTo decides: bound to a request, or unsolicited</title>
<desc id="l02a-d">A decision tree that starts with whether the Response carries InResponseTo. If it does, ask whether it matches an outstanding AuthnRequest ID. If it matches, consume the stored ID on first use; the ID cache is still required. If it matches nothing, the check fails and the assertion should be discarded. If it carries none, the Response is unsolicited, as with IdP-initiated SSO, and the request-binding control is gone. Ask whether the integration needs it. If so, compensate with a replay cache, short validity, only the registered IdP and ACS, and a RelayState allowlist; if not, the leaf says off by default, which the text also lists with the compensations. The diagram highlights each path in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
<style>
svg.l02a-flow{--ink:light-dark(#000000,#ffffff)}
.l02a-box{fill:var(--panel);stroke:var(--border-strong);stroke-width:1.5}
.l02a-hot{fill:var(--panel);stroke:var(--accent);stroke-width:2.5}
.l02a-ttl{fill:var(--ink);font:600 15px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l02a-sub{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l02a-life{stroke:var(--border-strong);stroke-width:1.5;stroke-dasharray:4 5}
.l02a-front{stroke:var(--accent);stroke-width:2;fill:none}
.l02a-back{stroke:var(--muted);stroke-width:2;stroke-dasharray:7 5;fill:none}
.l02a-bad{stroke:var(--bad);stroke-width:2;fill:none}
.l02a-main{fill:var(--ink);font:600 13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l02a-badt{fill:var(--ink)}
.l02a-dim{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l02a-badge{fill:var(--accent)}
.l02a-b-back{fill:var(--muted)}
.l02a-b-bad{fill:var(--bad)}
.l02a-b-good{fill:var(--good)}
.l02a-bt{fill:var(--on-accent);font:700 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l02a-note{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l02a-note-good{fill:var(--good-bg);stroke:var(--good);stroke-width:1.5}
.l02a-note-bad{fill:var(--bad-bg);stroke:var(--bad);stroke-width:1.5}
.l02a-nt{fill:var(--ink);font:500 12.5px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l02a-nest{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l02a-row{fill:var(--raised);stroke:var(--border-strong);stroke-width:1}
.l02a-ttlL{fill:var(--ink);font:600 14px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l02a-subL{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l02a-dimL{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l02a-dimR{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:end}
.l02a-conn{stroke:var(--accent);stroke-width:1.5;fill:none}
.l02a-edge{stroke:var(--border-strong);stroke-width:1.75;fill:none}
.l02a-hl{fill:none;stroke:var(--accent);stroke-width:3}
.l02a-hle{stroke:var(--accent);stroke-width:3;fill:none}
.l02a-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:20s;animation-timing-function:linear;animation-iteration-count:infinite}
.l02a-pk.l02a-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.l02a-pk.l02a-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.l02a-wrap{margin:20px 0}
@media (min-width:801px){.l02a-wrap{margin-left:-44px;margin-right:-44px}}
.l02a-g rect,.l02a-g line,.l02a-g path:not(.l02a-gl){opacity:.5;animation-duration:20s;animation-timing-function:linear;animation-iteration-count:infinite}
.l02a-h{opacity:0;animation-duration:20s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.l02a-flow:hover .l02a-g rect,svg.l02a-flow:hover .l02a-g line,svg.l02a-flow:hover .l02a-g path:not(.l02a-gl),svg.l02a-flow:hover .l02a-pk,svg.l02a-flow:hover .l02a-h{animation-play-state:paused}
.l02a-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.l02a-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.l02a-btn:hover{background:var(--hover)}
.l02a-cb:focus-visible + .l02a-btn{outline:2px solid var(--accent);outline-offset:2px}
.l02a-cb:checked + .l02a-btn .l02a-off,.l02a-cb:not(:checked) + .l02a-btn .l02a-on{display:none}
.l02a-cb:checked ~ .l02a-box .l02a-g rect,.l02a-cb:checked ~ .l02a-box .l02a-g line,.l02a-cb:checked ~ .l02a-box .l02a-g path:not(.l02a-gl),.l02a-cb:checked ~ .l02a-box .l02a-pk,.l02a-cb:checked ~ .l02a-box .l02a-h{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.l02a-g rect,.l02a-g line,.l02a-g path:not(.l02a-gl){animation:none;opacity:1}.l02a-pk{animation:none;display:none}.l02a-h{animation:none;opacity:0}.l02a-btn{display:none}}
@keyframes l02a-h0{0%{opacity:1}25%{opacity:1}25.01%,100%{opacity:0}}
.l02a-h0{animation-name:l02a-h0}
@keyframes l02a-h1{0%,24.99%{opacity:0}25%{opacity:1}50%{opacity:1}50.01%,100%{opacity:0}}
.l02a-h1{animation-name:l02a-h1}
@keyframes l02a-h2{0%,49.99%{opacity:0}50%{opacity:1}75%{opacity:1}75.01%,100%{opacity:0}}
.l02a-h2{animation-name:l02a-h2}
@keyframes l02a-h3{0%,74.99%{opacity:0}75%{opacity:1}100%{opacity:1}100.01%,100%{opacity:0}}
.l02a-h3{animation-name:l02a-h3}
</style>
<defs>
<marker id="l02a-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="l02a-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="l02a-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<path class="l02a-edge" d="M380,89 L380,118 L240,118 L240,144" marker-end="url(#l02a-m-front)"/>
<text class="l02a-dimL" x="246" y="134">yes</text>
<path class="l02a-edge" d="M240,212 L240,241 L164,241 L164,284" marker-end="url(#l02a-m-front)"/>
<text class="l02a-dimL" x="172" y="274">yes</text>
<path class="l02a-edge" d="M240,212 L240,241 L318,241 L318,284" marker-end="url(#l02a-m-front)"/>
<text class="l02a-dimL" x="325" y="274">no</text>
<path class="l02a-edge" d="M380,89 L380,118 L534,118 L534,144" marker-end="url(#l02a-m-front)"/>
<text class="l02a-dimL" x="540" y="134">none (unsolicited)</text>
<path class="l02a-edge" d="M534,229 L534,258 L462,258 L462,284" marker-end="url(#l02a-m-front)"/>
<text class="l02a-dimL" x="468" y="274">no</text>
<path class="l02a-edge" d="M534,229 L534,258 L602,258 L602,284" marker-end="url(#l02a-m-front)"/>
<text class="l02a-dimL" x="609" y="274">yes</text>
<rect class="l02a-note-good" x="94" y="287" width="141" height="82" rx="8"/><text class="l02a-nt" x="164" y="308">Consume the ID</text><text class="l02a-nt" x="164" y="325">on first use; the</text><text class="l02a-nt" x="164" y="342">ID cache is still</text><text class="l02a-nt" x="164" y="359">required</text>
<rect class="l02a-note-bad" x="251" y="287" width="134" height="65" rx="8"/><text class="l02a-nt" x="318" y="308">Fails the check:</text><text class="l02a-nt" x="318" y="325">SHOULD be</text><text class="l02a-nt" x="318" y="342">discarded</text>
<rect class="l02a-box" x="172" y="147" width="134" height="65" rx="8"/><text class="l02a-main" x="240" y="168">Does it match an</text><text class="l02a-nt" x="240" y="185">outstanding</text><text class="l02a-nt" x="240" y="202">AuthnRequest ID?</text>
<rect class="l02a-note-good" x="401" y="287" width="121" height="31" rx="8"/><text class="l02a-nt" x="462" y="308">Off by default</text>
<rect class="l02a-note" x="538" y="287" width="128" height="133" rx="8"/><text class="l02a-nt" x="602" y="308">Compensate:</text><text class="l02a-nt" x="602" y="325">replay cache,</text><text class="l02a-nt" x="602" y="342">short validity,</text><text class="l02a-nt" x="602" y="359">registered IdP</text><text class="l02a-nt" x="602" y="376">and ACS only,</text><text class="l02a-nt" x="602" y="393">RelayState</text><text class="l02a-nt" x="602" y="410">allowlist</text>
<rect class="l02a-box" x="466" y="147" width="134" height="82" rx="8"/><text class="l02a-main" x="534" y="168">No request to</text><text class="l02a-nt" x="534" y="185">bind it to. Does</text><text class="l02a-nt" x="534" y="202">the integration</text><text class="l02a-nt" x="534" y="219">need it?</text>
<rect class="l02a-box" x="310" y="24" width="141" height="65" rx="8"/><text class="l02a-main" x="380" y="45">Response arrives:</text><text class="l02a-nt" x="380" y="62">does it carry</text><text class="l02a-nt" x="380" y="79">InResponseTo?</text>
<g class="l02a-h l02a-h0">
<path class="l02a-hle" d="M380,89 L380,118 L240,118 L240,144" marker-end="url(#l02a-m-front)"/>
<path class="l02a-hle" d="M240,212 L240,241 L164,241 L164,284" marker-end="url(#l02a-m-front)"/>
<rect class="l02a-hl" x="310" y="24" width="141" height="65" rx="8"/>
<rect class="l02a-hl" x="172" y="147" width="134" height="65" rx="8"/>
<rect class="l02a-hl" x="94" y="287" width="141" height="82" rx="8"/>
</g>
<g class="l02a-h l02a-h1">
<path class="l02a-hle" d="M380,89 L380,118 L240,118 L240,144" marker-end="url(#l02a-m-front)"/>
<path class="l02a-hle" d="M240,212 L240,241 L318,241 L318,284" marker-end="url(#l02a-m-front)"/>
<rect class="l02a-hl" x="310" y="24" width="141" height="65" rx="8"/>
<rect class="l02a-hl" x="172" y="147" width="134" height="65" rx="8"/>
<rect class="l02a-hl" x="251" y="287" width="134" height="65" rx="8"/>
</g>
<g class="l02a-h l02a-h2">
<path class="l02a-hle" d="M380,89 L380,118 L534,118 L534,144" marker-end="url(#l02a-m-front)"/>
<path class="l02a-hle" d="M534,229 L534,258 L462,258 L462,284" marker-end="url(#l02a-m-front)"/>
<rect class="l02a-hl" x="310" y="24" width="141" height="65" rx="8"/>
<rect class="l02a-hl" x="466" y="147" width="134" height="82" rx="8"/>
<rect class="l02a-hl" x="401" y="287" width="121" height="31" rx="8"/>
</g>
<g class="l02a-h l02a-h3">
<path class="l02a-hle" d="M380,89 L380,118 L534,118 L534,144" marker-end="url(#l02a-m-front)"/>
<path class="l02a-hle" d="M534,229 L534,258 L602,258 L602,284" marker-end="url(#l02a-m-front)"/>
<rect class="l02a-hl" x="310" y="24" width="141" height="65" rx="8"/>
<rect class="l02a-hl" x="466" y="147" width="134" height="82" rx="8"/>
<rect class="l02a-hl" x="538" y="287" width="128" height="133" rx="8"/>
</g>
<line class="l02a-front" x1="40" y1="456" x2="70" y2="456"/>
<text class="l02a-dim" x="78" y="460" style="text-anchor:start">the path being traced</text>
<rect class="l02a-note" x="246" y="448" width="22" height="16" rx="4"/>
<text class="l02a-dim" x="276" y="460" style="text-anchor:start">only with compensation</text>
<rect class="l02a-note-good" x="450" y="448" width="22" height="16" rx="4"/>
<text class="l02a-dim" x="480" y="460" style="text-anchor:start">outcome that holds</text>
<rect class="l02a-note-bad" x="40" y="470" width="22" height="16" rx="4"/>
<text class="l02a-dim" x="70" y="482" style="text-anchor:start">fails the check</text>
</svg>
</div>
</div>
<!-- /diagram:saml-ways-in -->

Walk it from the top: whether the Response carries `InResponseTo` is the question that splits an SP-initiated Response from an unsolicited one. The unsolicited branch has no request to bind it to, so the compensations in the text are what is left.

**RelayState.** At most 80 bytes; it SHOULD be integrity protected with "a checksum, a pseudo-random value, or similar" (3.4.3), yet the binding defines no protection for the pairing of message and RelayState, so an attacker can recombine valid responses by switching RelayState values (3.5.5.2). Use an opaque random value that keys server-side state (target path, request ID), never a URL you redirect to blindly. That also meets the profile's "reveal as little of the request as possible" (4.1.3.1).

## Where the standard leaves you to decide

| Question | What the documents say | A defensible default (mine) |
|---|---|---|
| Clock skew tolerance | "allowable clock skew", no figure; Entra: a service "might allow" up to five minutes | configurable; start at five minutes and log observed skew |
| Audience matching | valid if the relying party is "a member of" the audiences; separate `AudienceRestriction` elements are ANDed; no comparison algorithm in the text I read | exact string match on the entity ID |
| Account key | persistent NameID is opaque, 256 characters at most, pair-wise | key on the pair (Issuer, NameID); carry email as an attribute |
| Several `SubjectConfirmation` | satisfying any one is sufficient (core 2.4.1) | require a bearer one that passes every check above |
| Metadata trust | signing is recommended when there is no secure channel (metadata 3) | fetch over TLS or verify the signature; metadata is your trust root |
| Logout | `PartialLogout` exists; Okta SLO does not reach "other apps that are open" | short SP sessions plus deprovisioning, not SLO |

## Your task

Local, run on 2026-10-06: an invented, minimal sample Response (placeholder signature, not a real one; not schema-valid, since a real assertion also carries an `AuthnStatement`) and a wrapped copy. The sample SP's entity ID is `https://app.example.com/saml` and its ACS URL is `https://app.example.com/saml/acs`. The check does not verify signatures; it shows why you must read from the signed element.

```bash
cat > response.xml <<'EOF'
<samlp:Response xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol" xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion" xmlns:ds="http://www.w3.org/2000/09/xmldsig#" ID="_resp1" Version="2.0" IssueInstant="2026-10-06T05:20:00Z" Destination="https://app.example.com/saml/acs" InResponseTo="_req42">
  <saml:Issuer>https://idp.example.com/saml/sample</saml:Issuer>
  <samlp:Status><samlp:StatusCode Value="urn:oasis:names:tc:SAML:2.0:status:Success"/></samlp:Status>
  <saml:Assertion ID="_assert1" Version="2.0" IssueInstant="2026-10-06T05:20:00Z">
    <saml:Issuer>https://idp.example.com/saml/sample</saml:Issuer>
    <ds:Signature><ds:SignedInfo><ds:Reference URI="#_assert1"><ds:DigestValue>SAMPLE-NOT-A-REAL-DIGEST</ds:DigestValue></ds:Reference></ds:SignedInfo><ds:SignatureValue>SAMPLE-NOT-A-REAL-SIGNATURE</ds:SignatureValue></ds:Signature>
    <saml:Subject><saml:NameID Format="urn:oasis:names:tc:SAML:2.0:nameid-format:persistent">u-7f3a9c21</saml:NameID><saml:SubjectConfirmation Method="urn:oasis:names:tc:SAML:2.0:cm:bearer"><saml:SubjectConfirmationData InResponseTo="_req42" Recipient="https://app.example.com/saml/acs" NotOnOrAfter="2026-10-06T05:25:00Z"/></saml:SubjectConfirmation></saml:Subject>
    <saml:Conditions NotBefore="2026-10-06T05:19:30Z" NotOnOrAfter="2026-10-06T05:25:00Z"><saml:AudienceRestriction><saml:Audience>https://app.example.com/saml</saml:Audience></saml:AudienceRestriction></saml:Conditions>
  </saml:Assertion>
</samlp:Response>
EOF
base64 < response.xml | tr -d '\n' > response.b64   # what the browser would POST as SAMLResponse
sed 's|<saml:Assertion |<saml:Assertion ID="_evil"><saml:Subject><saml:NameID>admin@example.com</saml:NameID></saml:Subject></saml:Assertion><saml:Assertion |' response.xml | base64 | tr -d '\n' > wrapped.b64
q() { echo "$x" | xmllint --xpath "$1" -; }
for f in response.b64 wrapped.b64; do
  x=$(base64 -d < $f)
  echo "$f: assertions=$(q 'count(//*[local-name()="Assertion"])')" \
       "first=$(q 'string((//*[local-name()="Assertion"])[1]//*[local-name()="NameID"])')" \
       "signed-element=$(q 'string(//*[@ID=substring-after(//*[local-name()="Reference"]/@URI,"#")]//*[local-name()="NameID"])')"
done
```

```text
response.b64: assertions=1 first=u-7f3a9c21 signed-element=u-7f3a9c21
wrapped.b64: assertions=2 first=admin@example.com signed-element=u-7f3a9c21
```

A naive "first assertion" lookup returns the forged identity from the wrapped copy, while the element the signature's Reference points at still says `u-7f3a9c21`. Extend the loop to reject any document where the two differ. Written from the docs, not run against a live tenant: ask your SP's vendor which element they read after verification. Next: lesson 3 covers OAuth 2.0.
