# Foundations: who is who, and why SSO exists

Facts checked 2026-10-06 against NIST SP 800-63-4 (final, 31 July 2025; sections cited as "63C Sec. n"), RFC 6749, RFC 7519, OpenID Connect Core 1.0 and Discovery 1.0, the OASIS SAML 2.0 specifications, and the Okta and Microsoft Entra documentation. Product behaviour is quoted from those docs, not run against a live tenant.

You build or review the relying-party side. This lesson fixes the vocabulary the course assumes, then goes where the standards are exact, ambiguous or silent: who the roles really are, what trust is anchored in, which three clocks govern a sign-in, and which attacks live at this layer.

## Roles and names: where the dialects disagree

| Role | SAML | OpenID Connect | OAuth 2.0 | NIST SP 800-63C |
| --- | --- | --- | --- | --- |
| Authenticates the user | Identity Provider (IdP) | OpenID Provider (OP): an OAuth authorization server "capable of Authenticating the End-User" | authorization server | identity provider (IdP) |
| Consumes the result | Service Provider (SP) | Relying Party (RP): an OAuth client | client | relying party (RP) |
| The person | principal or subject (the non-normative SAML Technical Overview says the two tend to be used interchangeably) | End-User | resource owner | subscriber (an individual enrolled in the CSP's service) |
| Signed statement | assertion | ID token (a JWT) | access token | assertion |

- **Names overlap.** The SAML glossary defines an IdP as "a kind of service provider" and uses *relying party* generically for any entity acting on information from another; OIDC's RP is specifically an OAuth client. NIST adds the CSP, which holds the subscriber account, with the IdP as the "bridge" to the RP.
- **"Credential" has several meanings.** RFC 6749 section 1.4: access tokens "are credentials used to access protected resources". The SP 800-63B glossary: an object that binds an identifier and attributes to an authenticator, issued by the CSP. WebAuthn has its own public-key credentials (lesson 6).
- **Proxies and brokers.** A NIST federation proxy acts as an RP upstream and an IdP downstream, so the subscriber takes part in two separate federation transactions. The federated identifier in the proxy's assertion SHALL name the proxy as issuer, the overall FAL is the lowest along the path, and a compromised proxy exposes everything that flows through it (63C Sec. 3.3.3).
- **Authorization is outside the model.** NIST: "The means by which an RP determines authorization and access is out of scope for these guidelines." An assertion or ID token carries identity, authentication facts and attributes. The OAuth access token is the authorization artifact: scopes and a duration (RFC 6749 section 1.4).

## Trust: what is asserted, and what anchors it

The RP trusts the IdP to assert the subject (`iss` plus `sub`), attributes, and authentication facts: SAML `AuthnInstant` and `AuthnContext` (both required); OIDC `auth_time` (when the login happened), `acr` (the authentication class met) and `amr` (the methods used), all optional, with `auth_time` required once you send `max_age`. For `acr` the spec says parties "will need to agree upon the meanings of the values used", so the meaning is agreed out of band.

- **SAML metadata** gives the entity ID, `KeyDescriptor` keys (`use` is `signing` or `encryption`) and endpoints. A root element MUST carry `validUntil` or `cacheDuration`. The spec says relying parties SHOULD have some means to establish trust in the metadata before relying on it, and lists XML signatures, TLS server authentication and DNS signatures. Metadata is also "not to be taken as an authoritative statement" of capabilities: an omitted option is not a claim of non-support. In effect the anchor is whatever you did to obtain the file.
- **OIDC** anchors on the https issuer URL you configured: discovery lives at `{issuer}/.well-known/openid-configuration`, the signing keys at its `jwks_uri`, and the token's `iss` must match the issuer exactly. Rotation works by `kid`: the verifier re-fetches the key set on an unfamiliar `kid`, and the set SHOULD retain recently retired keys (Core section 10.1.1).
- **The reverse direction.** The SAML profile says the IdP MUST have some means to establish that an ACS location is controlled by the SP. RFC 6749 section 3.1.2.2 says a server MUST require public clients, and confidential clients using the implicit grant, to register redirect endpoints, and SHOULD require all clients to.
- **NIST** calls the arrangement a *trust agreement* (63C Sec. 3.5), pre-established or subscriber-driven; FAL2 requires pre-established. Identifiers and keys SHALL be established securely as the agreement defines.

<!-- diagram:trust-anatomy -->
<div style="position:relative;margin:20px 0">
<input type="checkbox" id="l01a-pause" class="l01a-cb" /><label for="l01a-pause" class="l01a-btn"><span class="l01a-off">Pause animation</span><span class="l01a-on">Play animation</span></label>
<div class="l01a-box" style="overflow-x:auto">
<svg class="l01a-flow" viewBox="0 0 760 465" role="img" aria-labelledby="l01a-t l01a-d" style="width:100%;min-width:640px;max-width:800px;height:auto;display:block;margin:0 auto">
<title id="l01a-t">What anchors the trust agreement</title>
<desc id="l01a-d">A nested diagram of the trust agreement, which NIST describes as pre-established or subscriber-driven and which FAL2 requires to be pre-established. SAML metadata gives the entity ID, keys and endpoints; a root element must carry validUntil or cacheDuration, and in effect the anchor is whatever you did to obtain the file. OpenID Connect anchors on the https issuer URL you configured: discovery gives the jwks_uri, the token's iss must match the issuer exactly, and the verifier re-fetches the key set on an unfamiliar kid, with the set retaining recently retired keys. In the reverse direction the IdP must have some means to establish that an ACS location is controlled by the SP, and for OAuth a server must require public clients and implicit-grant confidential clients to register redirect endpoints, and should require all clients to. The diagram highlights each part in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
<style>
.l01a-box{fill:var(--panel);stroke:var(--border-strong);stroke-width:1.5}
.l01a-hot{fill:var(--panel);stroke:var(--accent);stroke-width:2.5}
.l01a-ttl{fill:var(--text);font:600 15px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l01a-sub{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l01a-life{stroke:var(--border-strong);stroke-width:1.5;stroke-dasharray:4 5}
.l01a-front{stroke:var(--accent);stroke-width:2;fill:none}
.l01a-back{stroke:var(--muted);stroke-width:2;stroke-dasharray:7 5;fill:none}
.l01a-bad{stroke:var(--bad);stroke-width:2;fill:none}
.l01a-main{fill:var(--text);font:600 13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l01a-badt{fill:var(--bad-text)}
.l01a-dim{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l01a-badge{fill:var(--accent)}
.l01a-b-back{fill:var(--muted)}
.l01a-b-bad{fill:var(--bad)}
.l01a-b-good{fill:var(--good)}
.l01a-bt{fill:var(--on-accent);font:700 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l01a-note{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l01a-note-good{fill:var(--good-bg);stroke:var(--good);stroke-width:1.5}
.l01a-note-bad{fill:var(--bad-bg);stroke:var(--bad);stroke-width:1.5}
.l01a-nt{fill:var(--body);font:12.5px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l01a-nest{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l01a-row{fill:var(--raised);stroke:var(--border-strong);stroke-width:1}
.l01a-ttlL{fill:var(--text);font:600 14px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l01a-subL{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l01a-dimL{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l01a-dimR{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:end}
.l01a-conn{stroke:var(--accent);stroke-width:1.5;fill:none}
.l01a-edge{stroke:var(--border-strong);stroke-width:1.75;fill:none}
.l01a-hl{fill:none;stroke:var(--accent);stroke-width:3}
.l01a-hle{stroke:var(--accent);stroke-width:3;fill:none}
.l01a-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:26s;animation-timing-function:linear;animation-iteration-count:infinite}
.l01a-pk.l01a-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.l01a-pk.l01a-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.l01a-g{opacity:.45;animation-duration:26s;animation-timing-function:linear;animation-iteration-count:infinite}
.l01a-h{opacity:0;animation-duration:26s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.l01a-flow:hover .l01a-g,svg.l01a-flow:hover .l01a-pk,svg.l01a-flow:hover .l01a-h{animation-play-state:paused}
.l01a-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.l01a-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.l01a-btn:hover{background:var(--hover)}
.l01a-cb:focus-visible + .l01a-btn{outline:2px solid var(--accent);outline-offset:2px}
.l01a-cb:checked + .l01a-btn .l01a-off,.l01a-cb:not(:checked) + .l01a-btn .l01a-on{display:none}
.l01a-cb:checked ~ .l01a-box .l01a-g,.l01a-cb:checked ~ .l01a-box .l01a-pk,.l01a-cb:checked ~ .l01a-box .l01a-h{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.l01a-g{animation:none;opacity:1}.l01a-pk{animation:none;display:none}.l01a-h{animation:none;opacity:0}.l01a-btn{display:none}}
@keyframes l01a-g0{0%{opacity:1}16.667%{opacity:1}16.677%,100%{opacity:.45}}
@keyframes l01a-h0{0%{opacity:1}16.667%{opacity:1}16.677%,100%{opacity:0}}
.l01a-g0{animation-name:l01a-g0}.l01a-h0{animation-name:l01a-h0}
@keyframes l01a-g1{0%,16.657%{opacity:.45}16.667%{opacity:1}33.333%{opacity:1}33.343%,100%{opacity:.45}}
@keyframes l01a-h1{0%,16.657%{opacity:0}16.667%{opacity:1}33.333%{opacity:1}33.343%,100%{opacity:0}}
.l01a-g1{animation-name:l01a-g1}.l01a-h1{animation-name:l01a-h1}
@keyframes l01a-g2{0%,33.323%{opacity:.45}33.333%{opacity:1}50%{opacity:1}50.01%,100%{opacity:.45}}
@keyframes l01a-h2{0%,33.323%{opacity:0}33.333%{opacity:1}50%{opacity:1}50.01%,100%{opacity:0}}
.l01a-g2{animation-name:l01a-g2}.l01a-h2{animation-name:l01a-h2}
@keyframes l01a-g3{0%,49.99%{opacity:.45}50%{opacity:1}66.667%{opacity:1}66.677%,100%{opacity:.45}}
@keyframes l01a-h3{0%,49.99%{opacity:0}50%{opacity:1}66.667%{opacity:1}66.677%,100%{opacity:0}}
.l01a-g3{animation-name:l01a-g3}.l01a-h3{animation-name:l01a-h3}
@keyframes l01a-g4{0%,66.657%{opacity:.45}66.667%{opacity:1}83.333%{opacity:1}83.343%,100%{opacity:.45}}
@keyframes l01a-h4{0%,66.657%{opacity:0}66.667%{opacity:1}83.333%{opacity:1}83.343%,100%{opacity:0}}
.l01a-g4{animation-name:l01a-g4}.l01a-h4{animation-name:l01a-h4}
@keyframes l01a-g5{0%,83.323%{opacity:.45}83.333%{opacity:1}100%{opacity:1}100.01%,100%{opacity:.45}}
@keyframes l01a-h5{0%,83.323%{opacity:0}83.333%{opacity:1}100%{opacity:1}100.01%,100%{opacity:0}}
.l01a-g5{animation-name:l01a-g5}.l01a-h5{animation-name:l01a-h5}
</style>
<defs>
<marker id="l01a-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="l01a-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="l01a-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<rect class="l01a-box" x="14" y="16" width="440" height="354" rx="9"/><text class="l01a-ttlL" x="28" y="37">Trust agreement</text><text class="l01a-subL" x="28" y="54">NIST 63C Sec. 3.5: pre-established or subscriber-driven</text>
<rect class="l01a-nest" x="26" y="62" width="416" height="46" rx="9"/><text class="l01a-ttlL" x="40" y="83">SAML metadata</text><text class="l01a-subL" x="40" y="100">entity ID, keys, endpoints</text>
<rect class="l01a-nest" x="26" y="116" width="416" height="104" rx="9"/><text class="l01a-ttlL" x="40" y="137">OIDC issuer URL</text><text class="l01a-subL" x="40" y="154">the https URL you configured</text>
<rect class="l01a-nest" x="38" y="162" width="392" height="46" rx="9"/><text class="l01a-ttlL" x="52" y="183">jwks_uri key set</text><text class="l01a-subL" x="52" y="200">rotation works by kid</text>
<rect class="l01a-nest" x="26" y="228" width="416" height="130" rx="9"/><text class="l01a-ttlL" x="40" y="249">Reverse direction</text><text class="l01a-subL" x="40" y="266">where proofs may be sent</text>
<rect class="l01a-nest" x="38" y="274" width="392" height="32" rx="9"/><text class="l01a-ttlL" x="52" y="295">SAML ACS location</text>
<rect class="l01a-nest" x="38" y="314" width="392" height="32" rx="9"/><text class="l01a-ttlL" x="52" y="335">OAuth redirect endpoints</text>
<g class="l01a-g l01a-g0">
<path class="l01a-conn" d="M454,33 L462,33 L462,33 L470,33" marker-end="url(#l01a-m-front)"/>
<rect class="l01a-note" x="484" y="18" width="262" height="31" rx="8"/>
<text class="l01a-nt" x="615" y="38">FAL2 requires pre-established</text>
<circle class="l01a-badge l01a-b-front" cx="484" cy="33" r="12"/><text class="l01a-bt" x="484" y="37.5">1</text>
</g>
<g class="l01a-g l01a-g1">
<path class="l01a-conn" d="M442,79 L466,79 L466,91 L470,91" marker-end="url(#l01a-m-front)"/>
<rect class="l01a-note-good" x="484" y="58" width="262" height="65" rx="8"/>
<text class="l01a-nt" x="615" y="80">In effect, the anchor is whatever you</text>
<text class="l01a-nt" x="615" y="96">did to obtain the file. validUntil or</text>
<text class="l01a-nt" x="615" y="114">cacheDuration MUST be present.</text>
<circle class="l01a-badge l01a-b-good" cx="484" cy="91" r="12"/><text class="l01a-bt" x="484" y="95.5">2</text>
</g>
<g class="l01a-g l01a-g2">
<path class="l01a-conn" d="M442,133 L470,133 L470,158 L470,158" marker-end="url(#l01a-m-front)"/>
<rect class="l01a-note-good" x="484" y="134" width="262" height="48" rx="8"/>
<text class="l01a-nt" x="615" y="154">Discovery gives jwks_uri; iss must</text>
<text class="l01a-nt" x="615" y="172">match the issuer exactly</text>
<circle class="l01a-badge l01a-b-good" cx="484" cy="158" r="12"/><text class="l01a-bt" x="484" y="162.0">3</text>
</g>
<g class="l01a-g l01a-g3">
<path class="l01a-conn" d="M430,179 L474,179 L474,224 L470,224" marker-end="url(#l01a-m-front)"/>
<rect class="l01a-note-good" x="484" y="192" width="262" height="65" rx="8"/>
<text class="l01a-nt" x="615" y="212">Re-fetch on an unfamiliar kid.</text>
<text class="l01a-nt" x="615" y="230">The set SHOULD retain recently</text>
<text class="l01a-nt" x="615" y="246">retired keys.</text>
<circle class="l01a-badge l01a-b-good" cx="484" cy="224" r="12"/><text class="l01a-bt" x="484" y="228.5">4</text>
</g>
<g class="l01a-g l01a-g4">
<path class="l01a-conn" d="M430,291 L462,291 L462,291 L470,291" marker-end="url(#l01a-m-front)"/>
<rect class="l01a-note-good" x="484" y="267" width="262" height="48" rx="8"/>
<text class="l01a-nt" x="615" y="288">The IdP MUST have some means to</text>
<text class="l01a-nt" x="615" y="305">establish the SP controls it</text>
<circle class="l01a-badge l01a-b-good" cx="484" cy="291" r="12"/><text class="l01a-bt" x="484" y="295.5">5</text>
</g>
<g class="l01a-g l01a-g5">
<path class="l01a-conn" d="M430,331 L466,331 L466,366 L470,366" marker-end="url(#l01a-m-front)"/>
<rect class="l01a-note-good" x="484" y="325" width="262" height="82" rx="8"/>
<text class="l01a-nt" x="615" y="346">Server MUST require public and</text>
<text class="l01a-nt" x="615" y="363">implicit-grant confidential clients</text>
<text class="l01a-nt" x="615" y="380">to register; SHOULD require all</text>
<text class="l01a-nt" x="615" y="397">(RFC 6749 3.1.2.2)</text>
<circle class="l01a-badge l01a-b-good" cx="484" cy="366" r="12"/><text class="l01a-bt" x="484" y="370.5">6</text>
</g>
<g class="l01a-h l01a-h0">
<rect class="l01a-hl" x="14" y="16" width="440" height="354" rx="9"/>
</g>
<g class="l01a-h l01a-h1">
<rect class="l01a-hl" x="26" y="62" width="416" height="46" rx="9"/>
</g>
<g class="l01a-h l01a-h2">
<rect class="l01a-hl" x="26" y="116" width="416" height="104" rx="9"/>
</g>
<g class="l01a-h l01a-h3">
<rect class="l01a-hl" x="38" y="162" width="392" height="46" rx="9"/>
</g>
<g class="l01a-h l01a-h4">
<rect class="l01a-hl" x="38" y="274" width="392" height="32" rx="9"/>
</g>
<g class="l01a-h l01a-h5">
<rect class="l01a-hl" x="38" y="314" width="392" height="32" rx="9"/>
</g>
<rect class="l01a-note" x="40" y="433" width="22" height="16" rx="4"/>
<text class="l01a-dim" x="70" y="445" style="text-anchor:start">context</text>
<rect class="l01a-note-good" x="148" y="433" width="22" height="16" rx="4"/>
<text class="l01a-dim" x="178" y="445" style="text-anchor:start">what anchors it</text>
</svg>
</div>
</div>
<!-- /diagram:trust-anatomy -->

Read the callouts in order: the agreement itself, then what anchors SAML and OpenID Connect, then the reverse direction, where the IdP learns where it may send proofs.

## The first sign-in, end to end

<!-- diagram:trust-signin -->
<div style="position:relative;margin:20px 0">
<input type="checkbox" id="tr-pause" class="tr-cb" /><label for="tr-pause" class="tr-btn"><span class="tr-off">Pause animation</span><span class="tr-on">Play animation</span></label>
<div class="tr-box" style="overflow-x:auto">
<svg class="tr-flow" viewBox="0 0 760 887" role="img" aria-labelledby="tr-t tr-d" style="width:100%;min-width:640px;max-width:800px;height:auto;display:block;margin:0 auto">
<title id="tr-t">What crosses the browser and what does not</title>
<desc id="tr-d">Three parties: the relying party, the browser, and the identity provider. Step 1: the request arrives with no session, and the transaction should be RP-initiated, which NIST says SHOULD hold at FAL1 and SHALL at FAL2, with the response tied to the RP's request. Step 2: the relying party redirects the browser to the IdP with a sign-in request: a SAML AuthnRequest by Redirect, POST or Artifact binding, or an OpenID Connect authentication request. Step 3: the IdP may reuse its session and SHALL convey whatever it knows about how recent the authentication was, and the RP can force a new login with ForceAuthn or max_age. Step 4: the proof reaches the RP through the browser. With the SAML POST binding the Response goes through the browser and its assertion MUST be signed. In the OpenID Connect code flow only a code crosses the browser. A dashed back-channel arrow from the RP to the IdP shows the other path: with the SAML Artifact binding the SP fetches the Response, and in OpenID Connect the code is swapped at the token endpoint, so no token is exposed to the user agent. Step 5: a session is created only if the assertion is valid, from the expected IdP, and maps to a provisioned RP account. The diagram highlights each step in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
<style>
.tr-box{fill:var(--panel);stroke:var(--border-strong);stroke-width:1.5}
.tr-hot{fill:var(--panel);stroke:var(--accent);stroke-width:2.5}
.tr-ttl{fill:var(--text);font:600 15px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.tr-sub{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.tr-life{stroke:var(--border-strong);stroke-width:1.5;stroke-dasharray:4 5}
.tr-front{stroke:var(--accent);stroke-width:2;fill:none}
.tr-back{stroke:var(--muted);stroke-width:2;stroke-dasharray:7 5;fill:none}
.tr-bad{stroke:var(--bad);stroke-width:2;fill:none}
.tr-main{fill:var(--text);font:600 13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.tr-badt{fill:var(--bad-text)}
.tr-dim{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.tr-badge{fill:var(--accent)}
.tr-b-back{fill:var(--muted)}
.tr-b-bad{fill:var(--bad)}
.tr-b-good{fill:var(--good)}
.tr-bt{fill:var(--on-accent);font:700 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.tr-note{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.tr-note-good{fill:var(--good-bg);stroke:var(--good);stroke-width:1.5}
.tr-note-bad{fill:var(--bad-bg);stroke:var(--bad);stroke-width:1.5}
.tr-nt{fill:var(--body);font:12.5px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.tr-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:24s;animation-timing-function:linear;animation-iteration-count:infinite}
.tr-pk.tr-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.tr-pk.tr-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.tr-g{opacity:.45;animation-duration:24s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.tr-flow:hover .tr-g,svg.tr-flow:hover .tr-pk{animation-play-state:paused}
.tr-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.tr-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.tr-btn:hover{background:var(--hover)}
.tr-cb:focus-visible + .tr-btn{outline:2px solid var(--accent);outline-offset:2px}
.tr-cb:checked + .tr-btn .tr-off,.tr-cb:not(:checked) + .tr-btn .tr-on{display:none}
.tr-cb:checked ~ .tr-box .tr-g,.tr-cb:checked ~ .tr-box .tr-pk{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.tr-g{animation:none;opacity:1}.tr-pk{animation:none;display:none}.tr-btn{display:none}}
@keyframes tr-g0{0%{opacity:1}14.286%{opacity:1}14.296%,100%{opacity:.45}}
@keyframes tr-p0{0%,-0.01%{opacity:0;transform:translateX(0)}0%{opacity:1;transform:translateX(0)}14.286%{opacity:1;transform:translateX(-236px)}14.296%,100%{opacity:0;transform:translateX(-236px)}}
.tr-g0{animation-name:tr-g0}.tr-p0{animation-name:tr-p0}
@keyframes tr-g1{0%,14.276%{opacity:.45}14.286%{opacity:1}28.571%{opacity:1}28.581%,100%{opacity:.45}}
.tr-g1{animation-name:tr-g1}
@keyframes tr-g2{0%,28.561%{opacity:.45}28.571%{opacity:1}42.857%{opacity:1}42.867%,100%{opacity:.45}}
@keyframes tr-p2{0%,28.561%{opacity:0;transform:translateX(0)}28.571%{opacity:1;transform:translateX(0)}42.857%{opacity:1;transform:translateX(236px)}42.867%,100%{opacity:0;transform:translateX(236px)}}
.tr-g2{animation-name:tr-g2}.tr-p2{animation-name:tr-p2}
@keyframes tr-g3{0%,42.847%{opacity:.45}42.857%{opacity:1}57.143%{opacity:1}57.153%,100%{opacity:.45}}
.tr-g3{animation-name:tr-g3}
@keyframes tr-g4{0%,57.133%{opacity:.45}57.143%{opacity:1}71.429%{opacity:1}71.439%,100%{opacity:.45}}
@keyframes tr-p4{0%,57.133%{opacity:0;transform:translateX(0)}57.143%{opacity:1;transform:translateX(0)}71.429%{opacity:1;transform:translateX(-236px)}71.439%,100%{opacity:0;transform:translateX(-236px)}}
.tr-g4{animation-name:tr-g4}.tr-p4{animation-name:tr-p4}
@keyframes tr-g5{0%,71.419%{opacity:.45}71.429%{opacity:1}85.714%{opacity:1}85.724%,100%{opacity:.45}}
@keyframes tr-p5{0%,71.419%{opacity:0;transform:translateX(0)}71.429%{opacity:1;transform:translateX(0)}85.714%{opacity:1;transform:translateX(506px)}85.724%,100%{opacity:0;transform:translateX(506px)}}
.tr-g5{animation-name:tr-g5}.tr-p5{animation-name:tr-p5}
@keyframes tr-g6{0%,85.704%{opacity:.45}85.714%{opacity:1}100%{opacity:1}100.01%,100%{opacity:.45}}
.tr-g6{animation-name:tr-g6}
</style>
<defs>
<marker id="tr-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="tr-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="tr-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<line class="tr-life" x1="110" y1="72" x2="110" y2="835"/>
<line class="tr-life" x1="380" y1="72" x2="380" y2="835"/>
<line class="tr-life" x1="650" y1="72" x2="650" y2="835"/>
<rect class="tr-box" x="20" y="10" width="180" height="62" rx="10"/><text class="tr-ttl" x="110" y="36">RP (SP / client)</text><text class="tr-sub" x="110" y="56">consumes the result</text>
<rect class="tr-box" x="290" y="10" width="180" height="62" rx="10"/><text class="tr-ttl" x="380" y="36">Browser</text><text class="tr-sub" x="380" y="56">the user agent</text>
<rect class="tr-hot" x="560" y="10" width="180" height="62" rx="10"/><text class="tr-ttl" x="650" y="36">IdP (OP)</text><text class="tr-sub" x="650" y="56">authenticates the user</text>
<g class="tr-g tr-g0">
<text class="tr-main" x="245" y="108">request, no session</text>
<line class="tr-front" x1="366" y1="122" x2="124" y2="122" marker-end="url(#tr-m-front)"/>
<circle class="tr-badge tr-b-front" cx="380" cy="122" r="12"/><text class="tr-bt" x="380" y="126.5">1</text>
</g>
<g class="tr-g tr-g1">
<rect class="tr-note-good" x="10" y="156" width="221" height="65" rx="8"/>
<text class="tr-nt" x="120" y="177">RP-initiated: SHOULD at FAL1,</text>
<text class="tr-nt" x="120" y="194">SHALL at FAL2. Tie the</text>
<text class="tr-nt" x="120" y="211">response to its request</text>
</g>
<g class="tr-g tr-g2">
<text class="tr-main" x="245" y="255">redirect with a sign-in request</text>
<text class="tr-dim" x="245" y="271">SAML: Redirect, POST or Artifact</text>
<text class="tr-dim" x="245" y="287">OIDC: authentication request</text>
<line class="tr-front" x1="124" y1="301" x2="366" y2="301" marker-end="url(#tr-m-front)"/>
<circle class="tr-badge tr-b-front" cx="110" cy="301" r="12"/><text class="tr-bt" x="110" y="305.5">2</text>
<text class="tr-main" x="515" y="341">browser carries it on</text>
<line class="tr-front" x1="394" y1="355" x2="636" y2="355" marker-end="url(#tr-m-front)"/>
</g>
<g class="tr-g tr-g3">
<rect class="tr-note" x="489" y="389" width="261" height="65" rx="8"/>
<text class="tr-nt" x="620" y="410">may reuse its session; SHALL convey</text>
<text class="tr-nt" x="620" y="427">whatever it knows about recency.</text>
<text class="tr-nt" x="620" y="444">RP can force: ForceAuthn, max_age</text>
<circle class="tr-badge tr-b-plain" cx="489" cy="422" r="12"/><text class="tr-bt" x="489" y="426.0">3</text>
</g>
<g class="tr-g tr-g4">
<text class="tr-main" x="515" y="488">SAML POST: Response, assertion</text>
<text class="tr-dim" x="515" y="504">MUST be signed</text>
<text class="tr-dim" x="515" y="520">OIDC code flow: only a code</text>
<line class="tr-front" x1="636" y1="534" x2="394" y2="534" marker-end="url(#tr-m-front)"/>
<circle class="tr-badge tr-b-front" cx="650" cy="534" r="12"/><text class="tr-bt" x="650" y="538.5">4</text>
<text class="tr-main" x="245" y="574">proof reaches the RP</text>
<line class="tr-front" x1="366" y1="588" x2="124" y2="588" marker-end="url(#tr-m-front)"/>
</g>
<g class="tr-g tr-g5">
<text class="tr-main" x="380" y="628">back channel, not through the browser:</text>
<text class="tr-dim" x="380" y="644">SAML Artifact binding: the SP fetches the Response</text>
<text class="tr-dim" x="380" y="660">OIDC: code swapped at the token endpoint,</text>
<text class="tr-dim" x="380" y="676">so no token is exposed to the user agent</text>
<line class="tr-back" x1="124" y1="690" x2="636" y2="690" marker-end="url(#tr-m-back)"/>
</g>
<g class="tr-g tr-g6">
<rect class="tr-note-good" x="10" y="724" width="287" height="65" rx="8"/>
<text class="tr-nt" x="154" y="745">session only if the assertion is valid,</text>
<text class="tr-nt" x="154" y="762">from the expected IdP, and maps to</text>
<text class="tr-nt" x="154" y="779">a provisioned RP account</text>
<circle class="tr-badge tr-b-good" cx="10" cy="756" r="12"/><text class="tr-bt" x="10" y="761.0">5</text>
</g>
<circle class="tr-pk tr-p0" cx="360" cy="122" r="5.5"/>
<circle class="tr-pk tr-p2" cx="400" cy="355" r="5.5"/>
<circle class="tr-pk tr-p4" cx="360" cy="588" r="5.5"/>
<circle class="tr-pk tr-p5 tr-pkback" cx="130" cy="690" r="5.5"/>
<line class="tr-front" x1="40" y1="863" x2="70" y2="863"/>
<text class="tr-dim" x="78" y="867" style="text-anchor:start">through the browser</text>
<line class="tr-back" x1="233" y1="863" x2="263" y2="863"/>
<text class="tr-dim" x="271" y="867" style="text-anchor:start">back channel, no browser</text>
<rect class="tr-note-good" x="458" y="855" width="22" height="16" rx="4"/>
<text class="tr-dim" x="488" y="867" style="text-anchor:start">RP controls</text>
</svg>
</div>
</div>
<!-- /diagram:trust-signin -->

The badges 1 to 5 match the numbered steps below. Solid arrows pass through the browser; the dashed arrow is the back channel that the SAML Artifact binding and the OIDC code swap use in step 4, and it has no badge of its own. Lesson 4 covers the code swap.

1. **Request, no session.** RP-initiated: SAML `<AuthnRequest>`, or an OIDC authentication request. NIST says the transaction SHOULD be RP-initiated at FAL1 and SHALL be at FAL2. SAML also defines IdP-initiated SSO, with no `AuthnRequest`.
2. **Redirect.** The RP needs some way to tie the response to its request. SAML leaves the means to the SP (the profile offers RelayState as an optional mechanism, so keeping the requested URL is common practice, not a requirement), and the `<AuthnRequest>` may travel by Redirect, POST or Artifact binding. If the OIDC client sent a `nonce`, it must remember it to check the ID token.
3. **Authentication.** The IdP may reuse its session and SHALL convey whatever it knows about recency. The RP can force a new login: SAML `ForceAuthn`, or OIDC `max_age`, which obliges the OP to re-authenticate when the last login is older.
4. **Proof.** SAML POST binding: the `<Response>` goes through the browser and its assertion MUST be signed. With the Artifact binding the browser carries only an artifact and the SP fetches the `<Response>` from the IdP over a back channel (Profiles 4.1.3.5). OIDC code flow: only a code crosses the browser; the ID token comes from the token endpoint, so no token is exposed to the user agent (Core section 3.1).
5. **Validation, then session.** SAML: signature, `AudienceRestriction`, and the bearer confirmation (`Recipient` equals the ACS URL, its `NotOnOrAfter` has not passed, `InResponseTo` equals the request's ID unless the response is unsolicited; Profiles 4.1.4.3). OIDC (Core section 3.1.3.7): `iss` exact match, `aud` contains your client_id and the token is rejected if it lists untrusted extra audiences, signature, `exp`, and `nonce` MUST be checked if you sent one. NIST adds that a session SHALL be created only if the assertion is valid and from the expected IdP, that IdP is the one named in the federated identifier, and the assertion maps to a provisioned RP account (63C Sec. 3.9).

<!-- diagram:step5-checks -->
<div style="position:relative;margin:20px 0">
<input type="checkbox" id="l01c-pause" class="l01c-cb" /><label for="l01c-pause" class="l01c-btn"><span class="l01c-off">Pause animation</span><span class="l01c-on">Play animation</span></label>
<div class="l01c-box" style="overflow-x:auto">
<svg class="l01c-flow" viewBox="0 0 760 615" role="img" aria-labelledby="l01c-t l01c-d" style="width:100%;min-width:640px;max-width:800px;height:auto;display:block;margin:0 auto">
<title id="l01c-t">What the RP validates in step 5, SAML against OpenID Connect</title>
<desc id="l01c-d">A table with one row per question and one column per protocol. Signature: a SAML assertion must be signed with the POST binding; an OpenID Connect ID token needs its signature checked, except that TLS may stand in for a token received directly from the token endpoint. Right issuer: SAML relies on the expected IdP; OpenID Connect needs an exact iss match. Meant for me: SAML checks AudienceRestriction and that Recipient equals the ACS URL; OpenID Connect needs aud to contain your client_id and rejects untrusted extra audiences. Still valid: SAML checks that the bearer NotOnOrAfter has not passed; OpenID Connect checks exp, with small clock-skew leeway. Answers my request: SAML checks InResponseTo equals the request's ID unless the response is unsolicited; OpenID Connect must check the nonce if one was sent. The diagram highlights each row in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
<style>
.l01c-box{fill:var(--panel);stroke:var(--border-strong);stroke-width:1.5}
.l01c-hot{fill:var(--panel);stroke:var(--accent);stroke-width:2.5}
.l01c-ttl{fill:var(--text);font:600 15px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l01c-sub{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l01c-life{stroke:var(--border-strong);stroke-width:1.5;stroke-dasharray:4 5}
.l01c-front{stroke:var(--accent);stroke-width:2;fill:none}
.l01c-back{stroke:var(--muted);stroke-width:2;stroke-dasharray:7 5;fill:none}
.l01c-bad{stroke:var(--bad);stroke-width:2;fill:none}
.l01c-main{fill:var(--text);font:600 13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l01c-badt{fill:var(--bad-text)}
.l01c-dim{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l01c-badge{fill:var(--accent)}
.l01c-b-back{fill:var(--muted)}
.l01c-b-bad{fill:var(--bad)}
.l01c-b-good{fill:var(--good)}
.l01c-bt{fill:var(--on-accent);font:700 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l01c-note{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l01c-note-good{fill:var(--good-bg);stroke:var(--good);stroke-width:1.5}
.l01c-note-bad{fill:var(--bad-bg);stroke:var(--bad);stroke-width:1.5}
.l01c-nt{fill:var(--body);font:12.5px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l01c-nest{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l01c-row{fill:var(--raised);stroke:var(--border-strong);stroke-width:1}
.l01c-ttlL{fill:var(--text);font:600 14px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l01c-subL{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l01c-dimL{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l01c-dimR{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:end}
.l01c-conn{stroke:var(--accent);stroke-width:1.5;fill:none}
.l01c-edge{stroke:var(--border-strong);stroke-width:1.75;fill:none}
.l01c-hl{fill:none;stroke:var(--accent);stroke-width:3}
.l01c-hle{stroke:var(--accent);stroke-width:3;fill:none}
.l01c-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:20s;animation-timing-function:linear;animation-iteration-count:infinite}
.l01c-pk.l01c-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.l01c-pk.l01c-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.l01c-g{opacity:.45;animation-duration:20s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.l01c-flow:hover .l01c-g,svg.l01c-flow:hover .l01c-pk{animation-play-state:paused}
.l01c-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.l01c-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.l01c-btn:hover{background:var(--hover)}
.l01c-cb:focus-visible + .l01c-btn{outline:2px solid var(--accent);outline-offset:2px}
.l01c-cb:checked + .l01c-btn .l01c-off,.l01c-cb:not(:checked) + .l01c-btn .l01c-on{display:none}
.l01c-cb:checked ~ .l01c-box .l01c-g,.l01c-cb:checked ~ .l01c-box .l01c-pk{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.l01c-g{animation:none;opacity:1}.l01c-pk{animation:none;display:none}.l01c-btn{display:none}}
@keyframes l01c-g0{0%{opacity:1}20%{opacity:1}20.01%,100%{opacity:.45}}
.l01c-g0{animation-name:l01c-g0}
@keyframes l01c-g1{0%,19.99%{opacity:.45}20%{opacity:1}40%{opacity:1}40.01%,100%{opacity:.45}}
.l01c-g1{animation-name:l01c-g1}
@keyframes l01c-g2{0%,39.99%{opacity:.45}40%{opacity:1}60%{opacity:1}60.01%,100%{opacity:.45}}
.l01c-g2{animation-name:l01c-g2}
@keyframes l01c-g3{0%,59.99%{opacity:.45}60%{opacity:1}80%{opacity:1}80.01%,100%{opacity:.45}}
.l01c-g3{animation-name:l01c-g3}
@keyframes l01c-g4{0%,79.99%{opacity:.45}80%{opacity:1}100%{opacity:1}100.01%,100%{opacity:.45}}
.l01c-g4{animation-name:l01c-g4}
</style>
<defs>
<marker id="l01c-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="l01c-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="l01c-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<rect class="l01c-box" x="240" y="10" width="247" height="62" rx="10"/><text class="l01c-ttl" x="364" y="36">SAML</text><text class="l01c-sub" x="364" y="56">assertion</text>
<rect class="l01c-box" x="495" y="10" width="247" height="62" rx="10"/><text class="l01c-ttl" x="618" y="36">OpenID Connect</text><text class="l01c-sub" x="618" y="56">ID token</text>
<g class="l01c-g l01c-g0">
<rect class="l01c-row" x="10" y="86" width="740" height="101" rx="8"/>
<text class="l01c-ttlL" x="24" y="112">Signature</text>
<text class="l01c-nt" x="364" y="134">Assertion MUST be signed</text>
<text class="l01c-nt" x="364" y="149">(POST binding)</text>
<text class="l01c-nt" x="618" y="134">Signature checked; TLS may</text>
<text class="l01c-nt" x="618" y="149">stand in for a token from</text>
<text class="l01c-nt" x="618" y="164">the token endpoint</text>
</g>
<g class="l01c-g l01c-g1">
<rect class="l01c-row" x="10" y="195" width="740" height="71" rx="8"/>
<text class="l01c-ttlL" x="24" y="221">Right issuer</text>
<text class="l01c-nt" x="364" y="243">The expected IdP (NIST)</text>
<text class="l01c-nt" x="618" y="243">iss: exact match</text>
</g>
<g class="l01c-g l01c-g2">
<rect class="l01c-row" x="10" y="274" width="740" height="101" rx="8"/>
<text class="l01c-ttlL" x="24" y="300">Meant for me</text>
<text class="l01c-nt" x="364" y="322">AudienceRestriction;</text>
<text class="l01c-nt" x="364" y="337">Recipient = ACS URL</text>
<text class="l01c-nt" x="618" y="322">aud contains your client_id;</text>
<text class="l01c-nt" x="618" y="337">reject untrusted extra</text>
<text class="l01c-nt" x="618" y="352">audiences</text>
</g>
<g class="l01c-g l01c-g3">
<rect class="l01c-row" x="10" y="383" width="740" height="86" rx="8"/>
<text class="l01c-ttlL" x="24" y="409">Still valid</text>
<text class="l01c-nt" x="364" y="431">Bearer NotOnOrAfter</text>
<text class="l01c-nt" x="364" y="446">has not passed</text>
<text class="l01c-nt" x="618" y="431">exp (small clock-skew</text>
<text class="l01c-nt" x="618" y="446">leeway allowed)</text>
</g>
<g class="l01c-g l01c-g4">
<rect class="l01c-row" x="10" y="477" width="740" height="86" rx="8"/>
<text class="l01c-ttlL" x="24" y="503">Answers my request</text>
<text class="l01c-nt" x="364" y="525">InResponseTo = request ID,</text>
<text class="l01c-nt" x="364" y="540">unless unsolicited</text>
<text class="l01c-nt" x="618" y="525">nonce: MUST check it if</text>
<text class="l01c-nt" x="618" y="540">you sent one</text>
</g>
</svg>
</div>
</div>
<!-- /diagram:step5-checks -->

Each row is one question the RP asks in step 5; read across for the SAML check and the OpenID Connect check.

## Three clocks: assertion, IdP session, RP session

- **Assertion.** SAML `Conditions` `NotBefore` and `NotOnOrAfter` are optional, and they "do not guarantee that the statements in the assertion will be correct or accurate throughout the validity period"; without a `NotOnOrAfter` there the conditions impose "no expiry". For Web SSO, though, the bearer `SubjectConfirmationData` must carry its own `NotOnOrAfter`, the window in which the assertion can be delivered, plus `Recipient` and, when the response answers a request, `InResponseTo`, and must not carry `NotBefore` (Profiles 4.1.4.2). The SP must verify them (4.1.4.3), so a bearer assertion always has a delivery deadline. An ID token's `exp` is required, with "some small leeway, usually no more than a few minutes" for clock skew allowed. NIST: the window manages the RP's processing and "does not indicate the lifetime of the authenticated session at the IdP or RP"; a new transaction while the IdP session lives yields a new, separate assertion.
- **IdP session.** SAML `SessionNotOnOrAfter` is when the session with the issuing authority MUST be considered ended, with no required relationship to `NotOnOrAfter`. It is optional and fixed when the assertion is issued. The Web SSO profile says that if an `AuthnStatement` used to establish a security context carries it, the SP's security context SHOULD be discarded then, unless the SP re-establishes identity by repeating the profile (4.1.4.3; lesson 2). That makes it a ceiling set in advance, not event-driven revocation: it does not move when the account is later disabled. The OIDC spec says `exp` is "unrelated" to the RP-OP session.
- **RP session.** Yours to design. The RP MAY end it at any time, or restrict access if the assertion, authentication event or attributes fall short. Fetching attributes through an identity API SHALL NOT be used to establish or extend a session.
- **Recency is not issuance time.** NIST's example: a subscriber authenticates at the IdP, starts a transaction 30 minutes later, and the IdP reuses its session, so the new assertion says the last authentication was 30 minutes ago. `iat` (when the JWT was issued) is fresh; `auth_time` (when authentication occurred) is not. When you requested `auth_time` (directly or via `max_age`), the RP SHOULD check it and request re-authentication if too much time has passed.
- **Termination.** The IdP ending its session "will not necessarily terminate" RP sessions; the two MAY exchange end-session events through the protocol or shared signaling, and the IdP SHOULD signal a terminated, suspended or disabled account, suspected compromise and attribute changes. Okta Single Logout starts only from the SP, only for apps that support it, and not for SWA apps. Entra: the IdP "can't directly revoke a session token issued by an application". Okta Universal Logout and Entra Continuous Access Evaluation help only for supported apps.
- **Trade-off: session length.** Longer RP sessions mean fewer prompts and a wider leaver gap. NIST SP 800-63B-4 gives benchmarks: at AAL2, overall reauthentication SHOULD fall within 24 hours and inactivity within 1 hour; at AAL3, the overall timeout SHALL be no more than 12 hours and inactivity SHOULD be no more than 15 minutes.
- **Trade-off: where to demand strength.** Asking the IdP (`max_age`, `ForceAuthn`, `acr`) keeps policy central, but `acr` means only what you and the IdP agreed. Re-authenticating inside the app avoids that and splits policy across two places.
- **Edge case: skipping the signature.** For an ID token received directly from the token endpoint, Core section 3.1.3.7 lets TLS server validation stand in for the signature check (MAY), and requires the signature check for every other ID token.

<!-- diagram:session-gap -->
<div style="position:relative;margin:20px 0">
<input type="checkbox" id="l01b-pause" class="l01b-cb" /><label for="l01b-pause" class="l01b-btn"><span class="l01b-off">Pause animation</span><span class="l01b-on">Play animation</span></label>
<div class="l01b-box" style="overflow-x:auto">
<svg class="l01b-flow" viewBox="0 0 760 244" role="img" aria-labelledby="l01b-t l01b-d" style="width:100%;min-width:640px;max-width:800px;height:auto;display:block;margin:0 auto">
<title id="l01b-t">How the RP session can end</title>
<desc id="l01b-d">Three stages. First the sign-in: the assertion is valid and the relying party creates its own session, which is its to design. Then the IdP session ends or the account is disabled: the RP session is independent of IdP state and SessionNotOnOrAfter does not move. Finally the RP session can end by three routes: the IdP signals (SHOULD), the RP ends it (MAY), or SessionNotOnOrAfter passes, if it was sent (SHOULD). The diagram highlights each stage in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
<style>
.l01b-box{fill:var(--panel);stroke:var(--border-strong);stroke-width:1.5}
.l01b-hot{fill:var(--panel);stroke:var(--accent);stroke-width:2.5}
.l01b-ttl{fill:var(--text);font:600 15px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l01b-sub{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l01b-life{stroke:var(--border-strong);stroke-width:1.5;stroke-dasharray:4 5}
.l01b-front{stroke:var(--accent);stroke-width:2;fill:none}
.l01b-back{stroke:var(--muted);stroke-width:2;stroke-dasharray:7 5;fill:none}
.l01b-bad{stroke:var(--bad);stroke-width:2;fill:none}
.l01b-main{fill:var(--text);font:600 13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l01b-badt{fill:var(--bad-text)}
.l01b-dim{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l01b-badge{fill:var(--accent)}
.l01b-b-back{fill:var(--muted)}
.l01b-b-bad{fill:var(--bad)}
.l01b-b-good{fill:var(--good)}
.l01b-bt{fill:var(--on-accent);font:700 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l01b-note{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l01b-note-good{fill:var(--good-bg);stroke:var(--good);stroke-width:1.5}
.l01b-note-bad{fill:var(--bad-bg);stroke:var(--bad);stroke-width:1.5}
.l01b-nt{fill:var(--body);font:12.5px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l01b-nest{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l01b-row{fill:var(--raised);stroke:var(--border-strong);stroke-width:1}
.l01b-ttlL{fill:var(--text);font:600 14px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l01b-subL{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l01b-dimL{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l01b-dimR{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:end}
.l01b-conn{stroke:var(--accent);stroke-width:1.5;fill:none}
.l01b-edge{stroke:var(--border-strong);stroke-width:1.75;fill:none}
.l01b-hl{fill:none;stroke:var(--accent);stroke-width:3}
.l01b-hle{stroke:var(--accent);stroke-width:3;fill:none}
.l01b-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:18s;animation-timing-function:linear;animation-iteration-count:infinite}
.l01b-pk.l01b-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.l01b-pk.l01b-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.l01b-g{opacity:.45;animation-duration:18s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.l01b-flow:hover .l01b-g,svg.l01b-flow:hover .l01b-pk{animation-play-state:paused}
.l01b-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.l01b-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.l01b-btn:hover{background:var(--hover)}
.l01b-cb:focus-visible + .l01b-btn{outline:2px solid var(--accent);outline-offset:2px}
.l01b-cb:checked + .l01b-btn .l01b-off,.l01b-cb:not(:checked) + .l01b-btn .l01b-on{display:none}
.l01b-cb:checked ~ .l01b-box .l01b-g,.l01b-cb:checked ~ .l01b-box .l01b-pk{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.l01b-g{animation:none;opacity:1}.l01b-pk{animation:none;display:none}.l01b-btn{display:none}}
@keyframes l01b-g0{0%{opacity:1}33.333%{opacity:1}33.343%,100%{opacity:.45}}
@keyframes l01b-p0{0%,-0.01%{opacity:0;transform:translateX(0)}0%{opacity:1;transform:translateX(0)}33.333%{opacity:1;transform:translateX(88px)}33.343%,100%{opacity:0;transform:translateX(88px)}}
.l01b-g0{animation-name:l01b-g0}.l01b-p0{animation-name:l01b-p0}
@keyframes l01b-g1{0%,33.323%{opacity:.45}33.333%{opacity:1}66.667%{opacity:1}66.677%,100%{opacity:.45}}
@keyframes l01b-p1{0%,33.323%{opacity:0;transform:translateX(0)}33.333%{opacity:1;transform:translateX(0)}66.667%{opacity:1;transform:translateX(88px)}66.677%,100%{opacity:0;transform:translateX(88px)}}
.l01b-g1{animation-name:l01b-g1}.l01b-p1{animation-name:l01b-p1}
@keyframes l01b-g2{0%,66.657%{opacity:.45}66.667%{opacity:1}100%{opacity:1}100.01%,100%{opacity:.45}}
.l01b-g2{animation-name:l01b-g2}
</style>
<defs>
<marker id="l01b-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="l01b-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="l01b-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<g class="l01b-g l01b-g0">
<rect class="l01b-box" x="14" y="40" width="171" height="144" rx="10"/>
<text class="l01b-ttl" x="99" y="67">Sign-in</text>
<text class="l01b-sub" x="99" y="87">step 5</text>
<text class="l01b-nt" x="99" y="114">Assertion valid</text>
<text class="l01b-nt" x="99" y="131">RP creates its session</text>
<text class="l01b-nt" x="99" y="148">(yours to design)</text>
<line class="l01b-front" x1="193" y1="70" x2="287" y2="70" marker-end="url(#l01b-m-front)"/>
</g>
<g class="l01b-g l01b-g1">
<rect class="l01b-note-bad" x="295" y="40" width="171" height="144" rx="10"/>
<text class="l01b-ttl" x="380" y="67">IdP session ends</text>
<text class="l01b-sub" x="380" y="87">or account disabled</text>
<text class="l01b-nt" x="380" y="114">RP session is</text>
<text class="l01b-nt" x="380" y="131">independent of IdP state</text>
<text class="l01b-nt" x="380" y="148">SessionNotOnOrAfter</text>
<text class="l01b-nt" x="380" y="165">does not move</text>
<text class="l01b-main" x="520" y="64">can end by</text>
<line class="l01b-front" x1="473" y1="70" x2="567" y2="70" marker-end="url(#l01b-m-front)"/>
</g>
<g class="l01b-g l01b-g2">
<rect class="l01b-note-good" x="575" y="40" width="171" height="144" rx="10"/>
<text class="l01b-ttl" x="661" y="67">RP session ends</text>
<text class="l01b-sub" x="661" y="87">what can end it</text>
<text class="l01b-nt" x="661" y="114">IdP signals (SHOULD)</text>
<text class="l01b-nt" x="661" y="131">RP ends it (MAY)</text>
<text class="l01b-nt" x="661" y="148">SessionNotOnOrAfter</text>
<text class="l01b-nt" x="661" y="165">passes, if sent (SHOULD)</text>
</g>
<circle class="l01b-pk l01b-p0" cx="199" cy="70" r="5.5"/>
<circle class="l01b-pk l01b-p1" cx="479" cy="70" r="5.5"/>
<line class="l01b-front" x1="40" y1="220" x2="70" y2="220"/>
<text class="l01b-dim" x="78" y="224" style="text-anchor:start">time passes</text>
<rect class="l01b-note-good" x="182" y="212" width="22" height="16" rx="4"/>
<text class="l01b-dim" x="212" y="224" style="text-anchor:start">ways it can end</text>
<rect class="l01b-note-bad" x="342" y="212" width="22" height="16" rx="4"/>
<text class="l01b-dim" x="372" y="224" style="text-anchor:start">independent of IdP state</text>
</svg>
</div>
</div>
<!-- /diagram:session-gap -->

Read left to right: the sign-in, the IdP session ending, and the ways the RP session can then end.

## Identifiers, accounts and the leaver gap

- **Federated identifier = issuer plus subject.** NIST calls it imperative that an RP never process a subject identifier without the issuer, since IdPs choose them independently and may collide. OIDC `sub` is case-sensitive, at most 255 ASCII characters, locally unique and never reassigned. A JWT's `sub` is optional (RFC 7519), but an ID token's is required.
- **Not portable across apps.** OIDC subject types are `public` (same `sub` for all clients) or `pairwise` (a different `sub` per client), so you cannot join users across apps on `sub`. SAML NameID formats include email address, persistent and transient. A persistent identifier is usually issued for a single SP; a transient one is destroyed when the session ends, so it cannot key an account.
- **Email is not a key.** OIDC section 5.7: an issuer MAY reuse an email value for different users, the address MAY change, and `email` MUST NOT be a unique identifier. Microsoft adds that `email` and `preferred_username` can be controlled by tenant admins or sometimes users, and recommends `tid` plus `oid` as a combined key in Entra, where `sub` is pairwise per application. NIST: federated identifiers SHALL NOT contain plaintext personal data such as emails at FAL2.
- **Linking and resolution.** If you allow linking, the RP SHALL require an authenticated session, which SHOULD use an existing federated identifier. Resolving an assertion to an existing record SHALL use attributes sufficient to resolve uniquely, and SHALL NOT attach a record to an identifier that does not belong to that subscriber.
- **Provisioning.** The account must exist before the session (63C Sec. 3.8). *Just-in-time* creates it on the first assertion, so without signals it accumulates accounts the IdP no longer knows. *Pre-provisioning* pushes accounts ahead of use, including people who never sign in. *Ephemeral* keeps no long-term record after the session and suits RPs that fully externalize access rights to the IdP.

## Attack classes at this layer

| Attack | What it exploits | Mitigation |
| --- | --- | --- |
| Forged or modified assertion | RP accepts an unsigned or wrongly keyed statement | verify the signature with the expected IdP's key (FAL1 SHALL) |
| Wrong-audience token | a token minted for app A is accepted by app B | `aud` or `AudienceRestriction` check; FAL2 requires a single RP per assertion |
| Assertion injection | a stolen or manufactured assertion is forced into a session | RP-initiated flows with tracked state, nonces, back-channel presentation, RP authentication to the IdP, no unsolicited IdP-initiated responses, or platform APIs instead of HTTP redirects (63C Sec. 3.11.1; protection required at FAL2) |
| Replay | the same assertion is presented again | RP-enforced replay protection (SHALL at FAL1); `nonce` |
| Identifier collision or reuse | two issuers share a `sub`, or an email is reassigned | key on issuer plus subject; link only through authentication |
| Session outliving the IdP | RP session independent of IdP state | signals, provisioning, bounded RP sessions |

<!-- diagram:assertion-injection -->
<div style="position:relative;margin:20px 0">
<input type="checkbox" id="l01d-pause" class="l01d-cb" /><label for="l01d-pause" class="l01d-btn"><span class="l01d-off">Pause animation</span><span class="l01d-on">Play animation</span></label>
<div class="l01d-box" style="overflow-x:auto">
<svg class="l01d-flow" viewBox="0 0 760 568" role="img" aria-labelledby="l01d-t l01d-d" style="width:100%;min-width:640px;max-width:800px;height:auto;display:block;margin:0 auto">
<title id="l01d-t">Assertion injection: why the signature checks pass</title>
<desc id="l01d-d">Three parties: the IdP, an attacker, and the relying party. Step 1: the attacker obtains an assertion for their own account. Step 2: the IdP returns a fresh, genuine assertion, signed and addressed to the relying party's SP. Step 3: the attacker forces that assertion into a session at the relying party. The relying party's signature, audience and validity-window checks all pass. What fails is the binding to a transaction the relying party started, and the mitigations NIST lists include tracked state, nonces, back-channel presentation and refusing unsolicited IdP-initiated responses. The diagram highlights each step in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
<style>
.l01d-box{fill:var(--panel);stroke:var(--border-strong);stroke-width:1.5}
.l01d-hot{fill:var(--panel);stroke:var(--accent);stroke-width:2.5}
.l01d-ttl{fill:var(--text);font:600 15px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l01d-sub{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l01d-life{stroke:var(--border-strong);stroke-width:1.5;stroke-dasharray:4 5}
.l01d-front{stroke:var(--accent);stroke-width:2;fill:none}
.l01d-back{stroke:var(--muted);stroke-width:2;stroke-dasharray:7 5;fill:none}
.l01d-bad{stroke:var(--bad);stroke-width:2;fill:none}
.l01d-main{fill:var(--text);font:600 13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l01d-badt{fill:var(--bad-text)}
.l01d-dim{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l01d-badge{fill:var(--accent)}
.l01d-b-back{fill:var(--muted)}
.l01d-b-bad{fill:var(--bad)}
.l01d-b-good{fill:var(--good)}
.l01d-bt{fill:var(--on-accent);font:700 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l01d-note{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l01d-note-good{fill:var(--good-bg);stroke:var(--good);stroke-width:1.5}
.l01d-note-bad{fill:var(--bad-bg);stroke:var(--bad);stroke-width:1.5}
.l01d-nt{fill:var(--body);font:12.5px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l01d-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:18s;animation-timing-function:linear;animation-iteration-count:infinite}
.l01d-pk.l01d-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.l01d-pk.l01d-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.l01d-g{opacity:.45;animation-duration:18s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.l01d-flow:hover .l01d-g,svg.l01d-flow:hover .l01d-pk{animation-play-state:paused}
.l01d-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.l01d-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.l01d-btn:hover{background:var(--hover)}
.l01d-cb:focus-visible + .l01d-btn{outline:2px solid var(--accent);outline-offset:2px}
.l01d-cb:checked + .l01d-btn .l01d-off,.l01d-cb:not(:checked) + .l01d-btn .l01d-on{display:none}
.l01d-cb:checked ~ .l01d-box .l01d-g,.l01d-cb:checked ~ .l01d-box .l01d-pk{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.l01d-g{animation:none;opacity:1}.l01d-pk{animation:none;display:none}.l01d-btn{display:none}}
@keyframes l01d-g0{0%{opacity:1}20%{opacity:1}20.01%,100%{opacity:.45}}
@keyframes l01d-p0{0%,-0.01%{opacity:0;transform:translateX(0)}0%{opacity:1;transform:translateX(0)}20%{opacity:1;transform:translateX(-236px)}20.01%,100%{opacity:0;transform:translateX(-236px)}}
.l01d-g0{animation-name:l01d-g0}.l01d-p0{animation-name:l01d-p0}
@keyframes l01d-g1{0%,19.99%{opacity:.45}20%{opacity:1}40%{opacity:1}40.01%,100%{opacity:.45}}
@keyframes l01d-p1{0%,19.99%{opacity:0;transform:translateX(0)}20%{opacity:1;transform:translateX(0)}40%{opacity:1;transform:translateX(236px)}40.01%,100%{opacity:0;transform:translateX(236px)}}
.l01d-g1{animation-name:l01d-g1}.l01d-p1{animation-name:l01d-p1}
@keyframes l01d-g2{0%,39.99%{opacity:.45}40%{opacity:1}60%{opacity:1}60.01%,100%{opacity:.45}}
@keyframes l01d-p2{0%,39.99%{opacity:0;transform:translateX(0)}40%{opacity:1;transform:translateX(0)}60%{opacity:1;transform:translateX(236px)}60.01%,100%{opacity:0;transform:translateX(236px)}}
.l01d-g2{animation-name:l01d-g2}.l01d-p2{animation-name:l01d-p2}
@keyframes l01d-g3{0%,59.99%{opacity:.45}60%{opacity:1}80%{opacity:1}80.01%,100%{opacity:.45}}
.l01d-g3{animation-name:l01d-g3}
@keyframes l01d-g4{0%,79.99%{opacity:.45}80%{opacity:1}100%{opacity:1}100.01%,100%{opacity:.45}}
.l01d-g4{animation-name:l01d-g4}
</style>
<defs>
<marker id="l01d-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="l01d-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="l01d-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<line class="l01d-life" x1="110" y1="72" x2="110" y2="516"/>
<line class="l01d-life" x1="380" y1="72" x2="380" y2="516"/>
<line class="l01d-life" x1="650" y1="72" x2="650" y2="516"/>
<rect class="l01d-box" x="20" y="10" width="180" height="62" rx="10"/><text class="l01d-ttl" x="110" y="36">IdP</text><text class="l01d-sub" x="110" y="56">signs genuinely</text>
<rect class="l01d-box" x="290" y="10" width="180" height="62" rx="10"/><text class="l01d-ttl" x="380" y="36">Attacker</text><text class="l01d-sub" x="380" y="56">has their own account</text>
<rect class="l01d-hot" x="560" y="10" width="180" height="62" rx="10"/><text class="l01d-ttl" x="650" y="36">RP (your SP)</text><text class="l01d-sub" x="650" y="56">checks the response</text>
<g class="l01d-g l01d-g0">
<text class="l01d-main" x="245" y="108">obtains an assertion</text>
<text class="l01d-dim" x="245" y="124">for their own account</text>
<line class="l01d-front" x1="366" y1="138" x2="124" y2="138" marker-end="url(#l01d-m-front)"/>
<circle class="l01d-badge l01d-b-front" cx="380" cy="138" r="12"/><text class="l01d-bt" x="380" y="142.5">1</text>
</g>
<g class="l01d-g l01d-g1">
<text class="l01d-main" x="245" y="178">fresh, genuine assertion:</text>
<text class="l01d-dim" x="245" y="194">signed, addressed to your SP</text>
<line class="l01d-front" x1="124" y1="208" x2="366" y2="208" marker-end="url(#l01d-m-front)"/>
<circle class="l01d-badge l01d-b-front" cx="110" cy="208" r="12"/><text class="l01d-bt" x="110" y="212.5">2</text>
</g>
<g class="l01d-g l01d-g2">
<text class="l01d-main l01d-badt" x="515" y="248">assertion forced</text>
<text class="l01d-dim" x="515" y="264">into a session</text>
<line class="l01d-bad" x1="394" y1="278" x2="636" y2="278" marker-end="url(#l01d-m-bad)"/>
<circle class="l01d-badge l01d-b-bad" cx="380" cy="278" r="12"/><text class="l01d-bt" x="380" y="282.5">3</text>
</g>
<g class="l01d-g l01d-g3">
<rect class="l01d-note-bad" x="556" y="312" width="188" height="48" rx="8"/>
<text class="l01d-nt" x="650" y="333">Signature, audience and</text>
<text class="l01d-nt" x="650" y="350">validity window all pass</text>
</g>
<g class="l01d-g l01d-g4">
<rect class="l01d-note-good" x="377" y="388" width="373" height="82" rx="8"/>
<text class="l01d-nt" x="564" y="409">What fails: the binding to a transaction</text>
<text class="l01d-nt" x="564" y="426">the RP started. Mitigations NIST lists include</text>
<text class="l01d-nt" x="564" y="443">tracked state, nonces, back-channel</text>
<text class="l01d-nt" x="564" y="460">presentation, no unsolicited IdP-initiated responses</text>
</g>
<circle class="l01d-pk l01d-p0" cx="360" cy="138" r="5.5"/>
<circle class="l01d-pk l01d-p1" cx="130" cy="208" r="5.5"/>
<circle class="l01d-pk l01d-p2 l01d-pkbad" cx="400" cy="278" r="5.5"/>
<line class="l01d-front" x1="40" y1="544" x2="70" y2="544"/>
<text class="l01d-dim" x="78" y="548" style="text-anchor:start">genuine message</text>
<line class="l01d-bad" x1="208" y1="544" x2="238" y2="544"/>
<text class="l01d-dim" x="246" y="548" style="text-anchor:start">the injection</text>
<rect class="l01d-note-good" x="363" y="536" width="22" height="16" rx="4"/>
<text class="l01d-dim" x="393" y="548" style="text-anchor:start">what fails and what helps</text>
</svg>
</div>
</div>
<!-- /diagram:assertion-injection -->

Badges 1 to 3 number the attacker's path. The red note is what the RP's signature, audience and validity checks see. The green note names what fails and lists some of the mitigations NIST gives.

A stolen assertion still carries the IdP's genuine signature, so a signature check alone does not stop injection. Injection differs from forgery and replay: an attacker can obtain a fresh, genuine assertion for their own account, signed and addressed to your SP, so signature, audience and validity-window checks all pass; what fails is the binding to a transaction the RP started. Most of the mitigations NIST lists tie the response to a transaction the RP started and can track (another uses platform APIs for front-channel communication instead of HTTP redirects). FALs are a US federal baseline; treat them as a benchmark. RFC 7519 section 12 adds that a JWT "may contain privacy-sensitive information", so omit it, encrypt, or use TLS.

## Your task: check a token, then argue a design

Ran locally with jq 1.7.1. The token is the invented sample from the earlier levels (junk signature); this checks claims only and does **not** verify the signature, which a real RP must.

```bash
TOKEN='eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6InNhbXBsZS1rZXktMSJ9.eyJpc3MiOiJodHRwczovL2lkcC5leGFtcGxlLmNvbSIsInN1YiI6InUtN2YzYTljMjEiLCJhdWQiOiJzYW1wbGUtYXBwLWNsaWVudC1pZCIsImlhdCI6MTc5MDAwMDAwMCwiYXV0aF90aW1lIjoxNzg5OTk5OTkwLCJleHAiOjE3OTAwMDAzMDAsImFtciI6WyJwd2QiLCJvdHAiXSwiZW1haWwiOiJhbGV4QGV4YW1wbGUuY29tIn0.dGhpcy1pcy1ub3QtYS1yZWFsLXNpZ25hdHVyZS1zYW1wbGUtb25seQ'
echo "$TOKEN" | jq -cR 'split(".")[1] | gsub("-";"+") | gsub("_";"/") | @base64d | fromjson | {iss_ok: (.iss == "https://idp.example.com"), aud_ok: ([.aud] | flatten | index("sample-app-client-id") != null), unexpired: (.exp > now), secs_from_login_to_issue: (.iat - .auth_time), account_key: [.iss, .sub]}'
# {"iss_ok":true,"aud_ok":true,"unexpired":false,"secs_from_login_to_issue":10,"account_key":["https://idp.example.com","u-7f3a9c21"]}
```

`unexpired` is false because the sample's `exp` is long past. Now argue three points. Which claim would gate an "export all data" action, and why not `exp`? What does an unexpired token say about the user's IdP session (nothing)? Where must revocation live, given the RP session is yours? Lesson 2 goes deep on SAML.
