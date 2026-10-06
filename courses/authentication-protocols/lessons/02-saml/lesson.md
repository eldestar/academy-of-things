# SAML 2.0

You have configured SAML apps in Okta or Entra and read the XML when one broke. This lesson fixes the mechanism in your head so you can say which party is wrong when a ticket lands: what moves where, what the service provider (SP) must check, which of your settings feeds which check, and what fails at 2am. Facts checked 2026-10-06 against the OASIS SAML 2.0 core, bindings, profiles and metadata specifications (all dated 15 March 2005), Okta's SAML field reference and Microsoft Learn. Product field names come from those pages; I did not test them in a tenant.

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

Certificates expire, and metadata is how a new one reaches the SP. Entra's default self-signed SAML certificate lasts three years and Entra emails at 60, 30 and 7 days before expiry. Microsoft recommends that an SP accept a primary and a secondary signing certificate and refetch metadata at least every 24 hours. Safe order: generate the new certificate while inactive, let the SP learn it, activate it, then retire the old one. Entra also says an app that does not check certificate expiry keeps accepting an expired one, so a silent expiry can mean the check is missing, not that rotation worked.

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

`RelayState` is at most 80 bytes, should be integrity protected, and the IdP must return it exactly as received. Nothing binds it to the message, so treat it as untrusted input and check it against an allowlist before redirecting.

**Single Logout** is best effort. Every participant needs a logout endpoint for it to work; the core protocol defines a `PartialLogout` status for a session authority that could not propagate logout to all participants; Entra supports redirect (GET) but not POST for it and warns two participants can race; and Okta's switch signs the user out of the app and Okta "but not out of other apps that are open". Single Logout is a user-sign-out mechanism; none of the sources I read says that deactivating a user sends a logout to every SP (not verified), so do not rely on it for offboarding. A fired employee's SP session can therefore survive until it expires: `NotOnOrAfter` only bounds when the assertion may be delivered, not how long the SP session lasts. `SessionNotOnOrAfter` in the `AuthnStatement` marks when the IdP's session with the user ends, and the profile says the SP SHOULD discard its own security context at that time (profiles 4.1.4.3). Okta documents a "Maximum app session lifetime" value sent in the assertion but its page does not name the attribute. Keep SP sessions short either way.

## What breaks at 2am

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
