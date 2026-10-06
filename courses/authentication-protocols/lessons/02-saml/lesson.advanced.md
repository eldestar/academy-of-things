# SAML 2.0

You build or review the service-provider (SP) side, or you own the architecture an SP plugs into. This lesson works at spec level: what the Web Browser SSO profile obliges you to verify, what an XML signature does and does not prove, how the real attacks work, and which decisions the standard leaves to you. Facts checked 2026-10-06 against the OASIS SAML 2.0 core, bindings, profiles and metadata specifications (15 March 2005), W3C XML Signature 1.1, the GitHub advisory database, NVD, the abstract of the USENIX Security 2012 SAML paper, and Okta and Microsoft Learn pages. Section numbers are from those documents. Where I reason beyond them I say so.

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

The numbers match the diagram. Every hop passes through the browser; steps 2 and 3 are one redirect, and steps 4 and 5 are one form POST (the IdP identifies the principal between 3 and 4).

Every hop crosses the user agent.

1. The user agent requests a protected resource and the SP has no security context.
2. The SP issues an `AuthnRequest` by Redirect, POST or Artifact (profile 4.1.2). Redirect: DEFLATE, base64, URL-encode, answered with 302 or 303; the XML signature is removed and replaced by `SigAlg` and `Signature` computed over the concatenated, still URL-encoded `SAMLRequest`, `RelayState` and `SigAlg` parameters (bindings 3.4.4.1).
3. The user agent GETs the IdP's SSO endpoint. An unauthenticated request "MUST NOT be trusted except as advisory", and the IdP MUST verify that any `AssertionConsumerServiceURL` or index belongs to the SP, because failure "can result in a man-in-the-middle attack" (4.1.4.1).
4. The IdP identifies the principal by a new authentication or an existing session; `ForceAuthn` obliges a fresh one (4.1.3.4). It then returns the `Response` by POST or Artifact, never Redirect: an HTML form carrying `SAMLResponse`.
5. The user agent POSTs that form to the ACS URL. With POST the assertions MUST be signed. If the message is signed, `Destination` MUST be present and the recipient MUST check it equals the receiving URL (bindings 3.5.5.2).
6. The SP processes the Response and may establish its security context "using any session mechanism it chooses" (4.1.3.6).

What the profile obliges the SP to do (4.1.4.3, 4.1.4.5): verify signatures on the assertions or response; verify `Recipient` in the bearer `SubjectConfirmationData` equals the ACS URL the message reached; verify its `NotOnOrAfter` has not passed, "subject to allowable clock skew"; verify `InResponseTo` equals the request's ID unless the response is unsolicited, in which case it MUST be absent; verify that any assertion it relies on is valid in other respects (the `AudienceRestriction` naming the SP is one such respect; 4.1.4.2 requires the IdP to include it). An assertion that fails any check SHOULD be discarded and SHOULD NOT establish a security context; that one is a SHOULD, not a MUST. With the POST binding the SP also MUST NOT accept a bearer assertion twice, by keeping used IDs for as long as `NotOnOrAfter` would keep the assertion valid (4.1.4.5). If the `AuthnStatement` carries `SessionNotOnOrAfter`, the security context SHOULD be discarded then.

## What the signature covers

The profile says assertions MUST be signed with POST and leaves signing the Response optional. Core 5.3 says an unsigned assertion may inherit the signature of an enclosing element when the signature "applies to the `Assertion` element and all its children"; the introduction to core section 5 adds that inherited signatures need care for assertions meant to be long-lived, because the whole signed context must be retained. So the documents pull in different directions, and implementations can differ. Pick a rule per integration and write it down: require a verified signature whose Reference is the Assertion, or accept a verified Response signature only when the Assertion you consume is a descendant of the element that Reference resolved to. SP metadata can state `WantAssertionsSigned`; the IdP is "not obligated" by it.

The signature profile (core 5.4) is narrow. Signatures are enveloped, carry a single same-document `ds:Reference` of the form `URI="#ID"` for the root element signed, SHOULD use exclusive canonicalization, and SHOULD NOT contain transforms beyond enveloped-signature and exclusive c14n; a verifier MAY reject other transforms, and if it does not it MUST make sure no content is excluded. `ds:KeyInfo` MAY be absent and SAML places no restriction on it. XML Signature core validation has two steps, reference validation (digest each Reference) and signature validation over canonical `SignedInfo`, and key material may come "from `KeyInfo` or from an external source" (XMLDSig 3.2). My conclusion, not the spec's: take the verification key only from IdP metadata you pinned, never from the message.

Encryption: an `EncryptedAssertion` is "a confidentiality protection mechanism when the plain-text value passes through an intermediary" (core 2.3.4). Order matters (core 6.2): a signed assertion that is then encrypted has its signature inside the ciphertext, so decrypt first, then verify. An encrypted `NameID` or `Attribute` is the reverse: encryption was done first and the signature covers the enclosing assertion, so verify first, then decrypt. The rule is that signature validation and decryption run "in the reverse order that signing and encryption were performed".

## Signature wrapping, parser differentials and canonicalization

Core validation shows that some element still matches a signed digest. It does not show that the element your code reads next is that element. XML Signature 1.1 makes the related point in its own terms: a consumer "should operate over the data that was transformed (including canonicalization) and signed, not the original pre-transformed data" (8.1.3; 8.1.1 adds, about transforms, "only what is signed is secure"). Signature wrapping (XSW) lives in that gap. My summary of the class: the validly signed element stays where the verifier finds it by ID, and a forged element is placed where the application's own lookup finds it first. The verifier and the business logic read different nodes.

- **The research.** Somorovsky et al. (USENIX Security 2012) analysed 14 SAML frameworks and found critical XSW flaws in 11, including Salesforce, Shibboleth and IBM XS40 (abstract). They model it as information flow between two relying-party components, signature verification and assertion processing, which also yields the countermeasures.
- **CVE-2025-25291 and CVE-2025-25292.** ruby-saml, GitHub advisories published 2025-03-12, CVSS 9.8. The advisories say authentication bypass "due to a parser differential": REXML and Nokogiri "parse XML differently", producing "entirely different document structures from the same XML input", which allows a signature wrapping attack. The titles name DOCTYPE handling and namespace handling. Fixed in 1.18.0 (1.12.4 on the 1.12 line). The advisories give no exploit detail and I did not verify any.
- **CVE-2024-45409.** ruby-saml, published 2024-09-10, CVSS 10.0 (GitHub's score; NVD's own is 9.8): it "does not properly verify the signature of the SAML Response", so an unauthenticated attacker holding any document signed by the IdP can forge a Response with arbitrary contents and log in as any user. GitHub's title ends "via Incorrect XPath selector". Fixed in 1.17.0 (1.12.3 on the 1.12 line).
- **CVE-2017-11427.** python-saml 2.3.0 and earlier, per NVD, "may incorrectly utilize the results of XML DOM traversal and canonicalization APIs" so an attacker can change the SAML data without invalidating the signature. That is the canonicalization class: per CERT/CC VU#475445, these APIs handle XML comments inconsistently, so text after a comment inside a node is lost before the digest is computed, and an attacker can change it without breaking the signature. It is a comment-handling bug, not a wrapping bug; CERT/CC lists six affected libraries, python-saml among them.

Controls (design recommendations drawn from the class, not spec rules): verify and extract from one parsed tree, never two parsers; after verification, resolve the verified Reference to its element and read every security-relevant value from that node, not from a fresh whole-document XPath; reject a document whose `Assertion` count is not what you expect or in which an `ID` is declared twice (core 1.3.4 requires exactly one declaration); allowlist algorithms, transforms and canonicalization methods; schema-validate and refuse a `DOCTYPE`; and treat library patch latency as a control, since every case above was a widely used library.

## Replay, unsolicited responses and RelayState

**Replay.** Bearer means possession is enough. The mandated defence is the ID cache (4.1.4.5). IDs make sound keys because randomly generated ones must collide with probability at most 2^-128 (core 1.3.4). My reasoning on sizing: if you accept responses a few minutes past `NotOnOrAfter` for skew, hold each ID until `NotOnOrAfter` plus that allowance, or the leniency window becomes a replay window; and the cache must be shared by every node behind the load balancer, with an atomic check-and-insert: per-node caches, even with sticky sessions, fail because the attacker replaying a Response, not the SP, chooses which node receives it. `InResponseTo` is the second control: store each outstanding `AuthnRequest` ID with an expiry and consume it on first use. That covers only SP-initiated Responses (an unsolicited one carries none), so it does not remove the ID-cache requirement. A `OneTimeUse` condition adds an expectation that the relying party keeps its own cache (core 2.5.1.5).

**Unsolicited responses.** IdP-initiated SSO has no `AuthnRequest`, so `InResponseTo` MUST be absent (4.1.5) and the request-binding control is gone. The response goes to the default ACS and `RelayState` is interpreted by prior agreement; the SP SHOULD designate a default landing location. If an integration needs it, compensate: replay cache, short validity, only the registered IdP and ACS, a `RelayState` allowlist, and off by default. Okta's "Single sign-on URL" is the ACS "always used" for IdP-initiated requests.

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
