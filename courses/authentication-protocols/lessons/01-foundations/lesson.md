# Foundations: who is who, and why SSO exists

Facts checked 2026-10-06 against NIST SP 800-63-4 (final, 31 July 2025), RFC 6749, RFC 7519, OpenID Connect Core 1.0 and Discovery 1.0, the OASIS SAML 2.0 specifications, and the Okta and Microsoft Entra documentation. Product behaviour is quoted from those docs, not run against a live tenant.

You have configured SAML and OIDC apps. This lesson fixes the vocabulary the rest of the course uses and the model behind settings you already know: what the app trusts the IdP for, which artifact lives how long, and why "we have SSO" settles less than people assume.

## One vocabulary, four dialects

| Role | SAML | OpenID Connect | OAuth 2.0 | NIST SP 800-63C |
| --- | --- | --- | --- | --- |
| Authenticates the user | Identity Provider (IdP) | OpenID Provider (OP), an OAuth authorization server | authorization server | identity provider (IdP) |
| Consumes the result | Service Provider (SP); the glossary also uses the generic *relying party* | Relying Party (RP), an OAuth client | client | relying party (RP) |
| The person | principal or subject | End-User | resource owner | subscriber |
| Signed statement | assertion | ID token (a JWT) | access token: a permission, not an identity | assertion |

- **Authentication vs authorization.** SP 800-63B describes authentication as determining the validity of the authenticators used to claim a digital identity. Authorization decides what that identity may do: an OAuth access token is "a string representing an authorization issued to the client", limited in scope and duration (RFC 6749 section 1.4). An assertion or ID token says who authenticated, how and when. It does not grant permissions.
- **Identity** on the wire is a subject identifier scoped to an issuer: OIDC `iss` plus `sub`, which NIST calls the *federated identifier*.
- **Account.** The IdP holds the subscriber account (NIST: the CSP's record of the subscriber, their attributes and authenticators). The app holds a separate *RP subscriber account*, which must exist before an authenticated session can be created.
- **Credential** is overloaded: RFC 6749 calls an access token a credential, while NIST uses *authenticator* for passwords, passkeys and OTPs, and WebAuthn works with public-key credentials such as passkeys (lesson 6). Say which you mean.
- **Session.** A secret shared between the user's software and the service, most often a cookie. Each sign-in creates several (see below).

The SAML glossary defines an IdP as "a kind of service provider that creates, maintains, and manages identity information for principals and provides principal authentication to other service providers". NIST splits those jobs: the CSP holds the account, the IdP is the bridge to the RP. One product usually plays both, which is why the words blur. An app that binds to a directory with the user's password verifies the authenticator itself, so under NIST's definition ("without the RP directly verifying the subscriber's authenticators") it is not federation.

## Trust: what the app relies on, and how it gets it

The app trusts the IdP's *signature* and what the signed statement says: who (issuer plus subject), attributes (email, groups), and how and when. For the last one, SAML's `AuthnStatement` has required `AuthnInstant` and `AuthnContext`; OIDC's `auth_time`, `acr` and `amr` are optional, and `auth_time` becomes required only when you send `max_age` or request it as essential. NIST says the IdP SHALL pass the RP whatever it knows about how recent the authentication was. What the subject may do inside the app is never part of that trust.

<!-- diagram:trust-anatomy -->
<div style="position:relative;margin:20px 0">
<input type="checkbox" id="l01a-pause" class="l01a-cb" /><label for="l01a-pause" class="l01a-btn"><span class="l01a-off">Pause animation</span><span class="l01a-on">Play animation</span></label>
<div class="l01a-box" style="overflow-x:auto">
<svg class="l01a-flow" viewBox="0 0 760 506" role="img" aria-labelledby="l01a-t l01a-d" style="width:100%;min-width:640px;max-width:800px;height:auto;display:block;margin:0 auto">
<title id="l01a-t">What the app relies on the IdP for</title>
<desc id="l01a-d">A nested diagram of the IdP's signed statement, an assertion or an ID token. The app trusts the signature, checked with the signing key from metadata or from the jwks_uri. It trusts who the subject is, the issuer plus subject that NIST calls the federated identifier. It trusts the attributes, such as email and groups, though mapping them to roles is the app's logic. It trusts how and when the user authenticated: SAML AuthnStatement has required AuthnInstant and AuthnContext, while OpenID Connect auth_time, acr and amr are optional, and auth_time becomes required only with max_age or an essential request. What the subject may do inside the app is never part of that trust. The diagram highlights each part in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
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
.l01a-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:24s;animation-timing-function:linear;animation-iteration-count:infinite}
.l01a-pk.l01a-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.l01a-pk.l01a-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.l01a-g{opacity:.45;animation-duration:24s;animation-timing-function:linear;animation-iteration-count:infinite}
.l01a-h{opacity:0;animation-duration:24s;animation-timing-function:linear;animation-iteration-count:infinite}
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
<rect class="l01a-box" x="14" y="16" width="440" height="432" rx="9"/><text class="l01a-ttlL" x="28" y="37">The IdP's signed statement</text><text class="l01a-subL" x="28" y="54">assertion or ID token</text>
<rect class="l01a-nest" x="26" y="62" width="416" height="46" rx="9"/><text class="l01a-ttlL" x="40" y="83">Signature</text><text class="l01a-subL" x="40" y="100">the IdP's</text>
<rect class="l01a-nest" x="26" y="116" width="416" height="46" rx="9"/><text class="l01a-ttlL" x="40" y="137">Who</text><text class="l01a-subL" x="40" y="154">issuer plus subject</text>
<rect class="l01a-nest" x="26" y="170" width="416" height="46" rx="9"/><text class="l01a-ttlL" x="40" y="191">Attributes</text><text class="l01a-subL" x="40" y="208">email, groups</text>
<rect class="l01a-nest" x="26" y="224" width="416" height="158" rx="9"/><text class="l01a-ttlL" x="40" y="245">How and when</text><text class="l01a-subL" x="40" y="262">the authentication facts</text>
<rect class="l01a-nest" x="38" y="270" width="392" height="46" rx="9"/><text class="l01a-ttlL" x="52" y="291">SAML AuthnStatement</text><text class="l01a-subL" x="52" y="308">AuthnInstant, AuthnContext</text>
<rect class="l01a-nest" x="38" y="324" width="392" height="46" rx="9"/><text class="l01a-ttlL" x="52" y="345">OIDC claims</text><text class="l01a-subL" x="52" y="362">auth_time, acr, amr</text>
<rect class="l01a-nest" x="26" y="390" width="416" height="46" rx="9"/><text class="l01a-ttlL" x="40" y="411">What the subject may do in the app</text><text class="l01a-subL" x="40" y="428">never part of that trust</text>
<g class="l01a-g l01a-g0">
<path class="l01a-conn" d="M442,79 L462,79 L462,79 L470,79" marker-end="url(#l01a-m-front)"/>
<rect class="l01a-note-good" x="484" y="55" width="262" height="48" rx="8"/>
<text class="l01a-nt" x="615" y="76">Checked with the signing key from</text>
<text class="l01a-nt" x="615" y="93">metadata, or from jwks_uri in OIDC</text>
<circle class="l01a-badge l01a-b-good" cx="484" cy="79" r="12"/><text class="l01a-bt" x="484" y="83.5">1</text>
</g>
<g class="l01a-g l01a-g1">
<path class="l01a-conn" d="M442,133 L466,133 L466,137 L470,137" marker-end="url(#l01a-m-front)"/>
<rect class="l01a-note-good" x="484" y="113" width="262" height="48" rx="8"/>
<text class="l01a-nt" x="615" y="134">OIDC iss plus sub; NIST calls it</text>
<text class="l01a-nt" x="615" y="151">the federated identifier</text>
<circle class="l01a-badge l01a-b-good" cx="484" cy="137" r="12"/><text class="l01a-bt" x="484" y="141.5">2</text>
</g>
<g class="l01a-g l01a-g2">
<path class="l01a-conn" d="M442,187 L470,187 L470,195 L470,195" marker-end="url(#l01a-m-front)"/>
<rect class="l01a-note-good" x="484" y="171" width="262" height="48" rx="8"/>
<text class="l01a-nt" x="615" y="192">Mapping them to roles is the</text>
<text class="l01a-nt" x="615" y="209">app's logic</text>
<circle class="l01a-badge l01a-b-good" cx="484" cy="195" r="12"/><text class="l01a-bt" x="484" y="199.5">3</text>
</g>
<g class="l01a-g l01a-g3">
<path class="l01a-conn" d="M430,287 L474,287 L474,287 L470,287" marker-end="url(#l01a-m-front)"/>
<rect class="l01a-note-good" x="484" y="272" width="262" height="31" rx="8"/>
<text class="l01a-nt" x="615" y="292">Both required</text>
<circle class="l01a-badge l01a-b-good" cx="484" cy="287" r="12"/><text class="l01a-bt" x="484" y="291.5">4</text>
</g>
<g class="l01a-g l01a-g4">
<path class="l01a-conn" d="M430,341 L462,341 L462,341 L470,341" marker-end="url(#l01a-m-front)"/>
<rect class="l01a-note-good" x="484" y="317" width="262" height="48" rx="8"/>
<text class="l01a-nt" x="615" y="338">Optional. auth_time is required only</text>
<text class="l01a-nt" x="615" y="355">with max_age or as an essential claim</text>
<circle class="l01a-badge l01a-b-good" cx="484" cy="341" r="12"/><text class="l01a-bt" x="484" y="345.5">5</text>
</g>
<g class="l01a-g l01a-g5">
<path class="l01a-conn" d="M442,407 L466,407 L466,407 L470,407" marker-end="url(#l01a-m-front)"/>
<rect class="l01a-note-bad" x="484" y="392" width="262" height="31" rx="8"/>
<text class="l01a-nt" x="615" y="412">SSO does not authorize</text>
<circle class="l01a-badge l01a-b-bad" cx="484" cy="407" r="12"/><text class="l01a-bt" x="484" y="411.5">6</text>
</g>
<g class="l01a-h l01a-h0">
<rect class="l01a-hl" x="26" y="62" width="416" height="46" rx="9"/>
</g>
<g class="l01a-h l01a-h1">
<rect class="l01a-hl" x="26" y="116" width="416" height="46" rx="9"/>
</g>
<g class="l01a-h l01a-h2">
<rect class="l01a-hl" x="26" y="170" width="416" height="46" rx="9"/>
</g>
<g class="l01a-h l01a-h3">
<rect class="l01a-hl" x="38" y="270" width="392" height="46" rx="9"/>
</g>
<g class="l01a-h l01a-h4">
<rect class="l01a-hl" x="38" y="324" width="392" height="46" rx="9"/>
</g>
<g class="l01a-h l01a-h5">
<rect class="l01a-hl" x="26" y="390" width="416" height="46" rx="9"/>
</g>
<rect class="l01a-note-good" x="40" y="474" width="22" height="16" rx="4"/>
<text class="l01a-dim" x="70" y="486" style="text-anchor:start">what the app relies on</text>
<rect class="l01a-note-bad" x="244" y="474" width="22" height="16" rx="4"/>
<text class="l01a-dim" x="274" y="486" style="text-anchor:start">outside the trust</text>
</svg>
</div>
</div>
<!-- /diagram:trust-anatomy -->

Read the tree from the signed statement down: each green part is something the app relies on the IdP for, and the red part is never part of that trust. The callouts are numbered in reading order.

| Direction | SAML | OIDC and OAuth |
| --- | --- | --- |
| App learns the IdP | IdP metadata: `entityID`, `KeyDescriptor use="signing"`, `SingleSignOnService` | discovery document at `{issuer}/.well-known/openid-configuration`: `issuer` and `jwks_uri`, the signing keys |
| IdP learns the app | SP metadata: `AssertionConsumerService` (ACS) | registered redirect URI (RFC 6749 section 3.1.2.2: MUST for public clients, SHOULD for all) |
| Key rotation | the new key must reach the app's stored copy of the metadata | the verifier re-fetches `jwks_uri` when it sees an unfamiliar `kid` (Core section 10.1.1) |

A SAML metadata root element must carry `validUntil` or `cacheDuration`. The metadata spec adds that relying parties SHOULD have some means of establishing trust in the metadata itself, and that retrieval over HTTP SHOULD use TLS. In OIDC the issuer from discovery must exactly match the token's `iss`. NIST's umbrella term for the whole arrangement is a *trust agreement*.

A rotation of the *signing* key breaks signature verification and nothing else. Metadata marks keys `use="signing"` or `use="encryption"`, and encryption is a separate optional layer in both protocols: a SAML `EncryptedAssertion` is meant for when the assertion passes through an intermediary, and an OIDC ID token must be signed and may then also be encrypted, with the keys the client registered (Core section 2). So "assertions are encrypted with the rotated key" and "ID tokens are never encrypted" are both wrong.

## The first sign-in, end to end

<!-- diagram:trust-signin -->
<div style="position:relative;margin:20px 0">
<input type="checkbox" id="tr-pause" class="tr-cb" /><label for="tr-pause" class="tr-btn"><span class="tr-off">Pause animation</span><span class="tr-on">Play animation</span></label>
<div class="tr-box" style="overflow-x:auto">
<svg class="tr-flow" viewBox="0 0 760 827" role="img" aria-labelledby="tr-t tr-d" style="width:100%;min-width:640px;max-width:800px;height:auto;display:block;margin:0 auto">
<title id="tr-t">The first sign-in with SAML and OpenID Connect names</title>
<desc id="tr-d">Three parties: the app (SP or RP), the user's browser, and the identity provider (IdP or OP). Step 1: the user reaches the app with no session. Step 2: the app redirects the browser to the IdP, with a SAML AuthnRequest or an OpenID Connect request to the authorization endpoint. Step 3: the IdP may reuse its own session, and the app can force a new login with ForceAuthn in SAML or max_age in OpenID Connect. Step 4: the IdP returns the proof through the browser. In SAML it is a Response holding the assertion, POSTed to the ACS. In OpenID Connect it is a code; the app swaps it for the ID token in a direct call. Step 5: the app validates the proof. SAML checks the signature, AudienceRestriction, Recipient, NotOnOrAfter and InResponseTo, which is absent if the response is unsolicited. OpenID Connect checks iss, aud, signature and exp. The app then creates its own session, most often a cookie. The diagram highlights each step in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
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
.tr-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:18s;animation-timing-function:linear;animation-iteration-count:infinite}
.tr-pk.tr-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.tr-pk.tr-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.tr-g{opacity:.45;animation-duration:18s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.tr-flow:hover .tr-g,svg.tr-flow:hover .tr-pk{animation-play-state:paused}
.tr-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.tr-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.tr-btn:hover{background:var(--hover)}
.tr-cb:focus-visible + .tr-btn{outline:2px solid var(--accent);outline-offset:2px}
.tr-cb:checked + .tr-btn .tr-off,.tr-cb:not(:checked) + .tr-btn .tr-on{display:none}
.tr-cb:checked ~ .tr-box .tr-g,.tr-cb:checked ~ .tr-box .tr-pk{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.tr-g{animation:none;opacity:1}.tr-pk{animation:none;display:none}.tr-btn{display:none}}
@keyframes tr-g0{0%{opacity:1}20%{opacity:1}20.01%,100%{opacity:.45}}
@keyframes tr-p0{0%,-0.01%{opacity:0;transform:translateX(0)}0%{opacity:1;transform:translateX(0)}20%{opacity:1;transform:translateX(-236px)}20.01%,100%{opacity:0;transform:translateX(-236px)}}
.tr-g0{animation-name:tr-g0}.tr-p0{animation-name:tr-p0}
@keyframes tr-g1{0%,19.99%{opacity:.45}20%{opacity:1}40%{opacity:1}40.01%,100%{opacity:.45}}
@keyframes tr-p1{0%,19.99%{opacity:0;transform:translateX(0)}20%{opacity:1;transform:translateX(0)}40%{opacity:1;transform:translateX(236px)}40.01%,100%{opacity:0;transform:translateX(236px)}}
.tr-g1{animation-name:tr-g1}.tr-p1{animation-name:tr-p1}
@keyframes tr-g2{0%,39.99%{opacity:.45}40%{opacity:1}60%{opacity:1}60.01%,100%{opacity:.45}}
.tr-g2{animation-name:tr-g2}
@keyframes tr-g3{0%,59.99%{opacity:.45}60%{opacity:1}80%{opacity:1}80.01%,100%{opacity:.45}}
@keyframes tr-p3{0%,59.99%{opacity:0;transform:translateX(0)}60%{opacity:1;transform:translateX(0)}80%{opacity:1;transform:translateX(-236px)}80.01%,100%{opacity:0;transform:translateX(-236px)}}
.tr-g3{animation-name:tr-g3}.tr-p3{animation-name:tr-p3}
@keyframes tr-g4{0%,79.99%{opacity:.45}80%{opacity:1}100%{opacity:1}100.01%,100%{opacity:.45}}
@keyframes tr-p4{0%,79.99%{opacity:0;transform:translateX(0)}80%{opacity:1;transform:translateX(0)}100%{opacity:1;transform:translateX(236px)}100.01%,100%{opacity:0;transform:translateX(236px)}}
.tr-g4{animation-name:tr-g4}.tr-p4{animation-name:tr-p4}
</style>
<defs>
<marker id="tr-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="tr-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="tr-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<line class="tr-life" x1="110" y1="72" x2="110" y2="775"/>
<line class="tr-life" x1="380" y1="72" x2="380" y2="775"/>
<line class="tr-life" x1="650" y1="72" x2="650" y2="775"/>
<rect class="tr-box" x="20" y="10" width="180" height="62" rx="10"/><text class="tr-ttl" x="110" y="36">App (SP / RP)</text><text class="tr-sub" x="110" y="56">consumes the result</text>
<rect class="tr-box" x="290" y="10" width="180" height="62" rx="10"/><text class="tr-ttl" x="380" y="36">Browser</text><text class="tr-sub" x="380" y="56">carries the messages shown</text>
<rect class="tr-hot" x="560" y="10" width="180" height="62" rx="10"/><text class="tr-ttl" x="650" y="36">IdP (OP)</text><text class="tr-sub" x="650" y="56">authenticates the user</text>
<g class="tr-g tr-g0">
<text class="tr-main" x="245" y="108">user reaches the app</text>
<text class="tr-dim" x="245" y="124">no session</text>
<line class="tr-front" x1="366" y1="138" x2="124" y2="138" marker-end="url(#tr-m-front)"/>
<circle class="tr-badge tr-b-front" cx="380" cy="138" r="12"/><text class="tr-bt" x="380" y="142.5">1</text>
</g>
<g class="tr-g tr-g1">
<text class="tr-main" x="245" y="178">redirect to the IdP:</text>
<text class="tr-dim" x="245" y="194">SAML AuthnRequest, or</text>
<text class="tr-dim" x="245" y="210">OIDC authorization endpoint</text>
<line class="tr-front" x1="124" y1="224" x2="366" y2="224" marker-end="url(#tr-m-front)"/>
<circle class="tr-badge tr-b-front" cx="110" cy="224" r="12"/><text class="tr-bt" x="110" y="228.5">2</text>
<text class="tr-main" x="515" y="264">browser is sent on to the IdP</text>
<line class="tr-front" x1="394" y1="278" x2="636" y2="278" marker-end="url(#tr-m-front)"/>
</g>
<g class="tr-g tr-g2">
<rect class="tr-note" x="529" y="312" width="221" height="65" rx="8"/>
<text class="tr-nt" x="640" y="333">may reuse its own session;</text>
<text class="tr-nt" x="640" y="350">app can force a login:</text>
<text class="tr-nt" x="640" y="367">SAML ForceAuthn, OIDC max_age</text>
<circle class="tr-badge tr-b-plain" cx="529" cy="344" r="12"/><text class="tr-bt" x="529" y="349.0">3</text>
</g>
<g class="tr-g tr-g3">
<text class="tr-main" x="515" y="411">proof for the app</text>
<text class="tr-dim" x="515" y="427">SAML: Response with the assertion</text>
<text class="tr-dim" x="515" y="443">OIDC: a code</text>
<line class="tr-front" x1="636" y1="457" x2="394" y2="457" marker-end="url(#tr-m-front)"/>
<circle class="tr-badge tr-b-front" cx="650" cy="457" r="12"/><text class="tr-bt" x="650" y="461.5">4</text>
<text class="tr-main" x="245" y="497">SAML: POSTed to the ACS</text>
<text class="tr-dim" x="245" y="513">OIDC: the code; the app swaps it</text>
<text class="tr-dim" x="245" y="529">for the ID token in a direct call</text>
<line class="tr-front" x1="366" y1="543" x2="124" y2="543" marker-end="url(#tr-m-front)"/>
</g>
<g class="tr-g tr-g4">
<rect class="tr-note-good" x="10" y="577" width="274" height="82" rx="8"/>
<text class="tr-nt" x="147" y="598">SAML: signature, AudienceRestriction,</text>
<text class="tr-nt" x="147" y="615">Recipient, NotOnOrAfter,</text>
<text class="tr-nt" x="147" y="632">InResponseTo (absent if unsolicited)</text>
<text class="tr-nt" x="147" y="649">OIDC: iss, aud, signature, exp</text>
<circle class="tr-badge tr-b-good" cx="10" cy="618" r="12"/><text class="tr-bt" x="10" y="622.5">5</text>
<text class="tr-main" x="245" y="693">app creates its own session,</text>
<text class="tr-dim" x="245" y="709">most often a cookie</text>
<line class="tr-front" x1="124" y1="723" x2="366" y2="723" marker-end="url(#tr-m-front)"/>
</g>
<circle class="tr-pk tr-p0" cx="360" cy="138" r="5.5"/>
<circle class="tr-pk tr-p1" cx="400" cy="278" r="5.5"/>
<circle class="tr-pk tr-p3" cx="360" cy="543" r="5.5"/>
<circle class="tr-pk tr-p4" cx="130" cy="723" r="5.5"/>
<line class="tr-front" x1="40" y1="803" x2="70" y2="803"/>
<text class="tr-dim" x="78" y="807" style="text-anchor:start">message through the user's browser</text>
<rect class="tr-note-good" x="329" y="795" width="22" height="16" rx="4"/>
<text class="tr-dim" x="359" y="807" style="text-anchor:start">what the app validates</text>
</svg>
</div>
</div>
<!-- /diagram:trust-signin -->

The badges 1 to 5 match the numbered steps below. Every arrow shown passes through the browser; the OIDC code swap in step 4 is a separate direct call from the app to the IdP, covered in lesson 4, and the SAML Artifact binding (step 4) is not drawn.

1. **Request, no session.** The user reaches the app. A SAML SP typically keeps the requested URL across the exchange: that is common practice, not a requirement, since the profile lets the SP use any means and offers RelayState as an optional mechanism. An OIDC client prepares an authentication request.
2. **Redirect.** SAML: with the HTTP-Redirect binding, an HTTP 302 or 303 to the IdP's sign-on service with an `<AuthnRequest>` in the `SAMLRequest` query variable (the profile also allows the POST and Artifact bindings for the request). OIDC: the browser is sent to the authorization endpoint.
3. **Authentication.** The IdP may reuse its own session and skip the prompt. The RP can demand a fresh login: SAML `ForceAuthn="true"`, or OIDC `max_age`, which obliges the OP to re-authenticate when the last login is older than that.
4. **Proof.** SAML: a `<Response>` holding the assertion, POSTed through the browser to the ACS (with the Artifact binding the browser carries only an artifact and the SP fetches the `<Response>` from the IdP over a back channel; an IdP-initiated variant exists with no `AuthnRequest`). OIDC code flow: a code through the browser, swapped at the token endpoint for the ID token (Core section 3.1).
5. **Validation, then session.** SAML: the signature (the Web Browser SSO profile says the assertion MUST be signed when the POST binding is used), `AudienceRestriction` (valid only if the RP is in the audience), and the bearer confirmation: `Recipient` equals the ACS URL, its `NotOnOrAfter` has not passed, and `InResponseTo` equals the request's ID (absent when the response is unsolicited). OIDC (section 3.1.3.7): `iss` matches exactly, `aud` contains the client_id, signature, `exp` in the future. NIST adds that a session may be created only from a valid assertion from the expected IdP, tied to a provisioned RP account.

## Assertion, token, cookie: who issues, who consumes, how long

| Artifact | Issued by | Consumed by | Lifetime |
| --- | --- | --- | --- |
| SAML assertion | IdP | SP, once, at the ACS | `Conditions` `NotBefore`/`NotOnOrAfter` are optional, but Web SSO requires a `NotOnOrAfter` on the bearer subject confirmation (and no `NotBefore` there); the specs fix no value (NIST gives "valid for five minutes" only as an example) |
| ID token | OP | RP, once, at sign-in | `exp` is required; the spec says it is unrelated to the lifetime of the RP-OP session |
| Access token | authorization server | resource server | `expires_in` is RECOMMENDED; Entra access tokens default to a random 60 to 90 minutes (75 on average), and up to 28 hours for CAE-capable clients |
| IdP session | IdP | IdP | IdP policy |
| App session cookie | the app | the app | the app's design; for reference, NIST's AAL2 baseline says overall reauthentication SHOULD be within 24 hours and inactivity within 1 hour |

NIST: the assertion's validity window "does not indicate the lifetime of the authenticated session at the IdP or RP", and the RP session will usually far outlive it. SAML's `SessionNotOnOrAfter` is the time when the session between the principal and the issuing SAML authority "MUST be considered ended". It describes the IdP session, with no required relationship to `NotOnOrAfter`. The Web SSO profile adds only that an SP SHOULD discard the security context it built from that assertion when the time passes (lesson 2); the attribute is optional and fixed at issuance, so it is a hint the IdP may send, not a control over your app's session.

**When the IdP session ends, the app session lives on.** NIST: ending the IdP session "will not necessarily terminate" RP sessions. Entra: "Microsoft Entra ID can't directly revoke a session token issued by an application", so the app must revoke it, and revoking refresh tokens leaves access tokens valid until they expire. Okta Single Logout is initiated only by the SP, only for apps that support it, and SWA apps don't support it. Okta Universal Logout and Entra Continuous Access Evaluation can end sessions or tokens, but only for supported apps.

<!-- diagram:session-gap -->
<div style="position:relative;margin:20px 0">
<input type="checkbox" id="l01b-pause" class="l01b-cb" /><label for="l01b-pause" class="l01b-btn"><span class="l01b-off">Pause animation</span><span class="l01b-on">Play animation</span></label>
<div class="l01b-box" style="overflow-x:auto">
<svg class="l01b-flow" viewBox="0 0 760 227" role="img" aria-labelledby="l01b-t l01b-d" style="width:100%;min-width:640px;max-width:800px;height:auto;display:block;margin:0 auto">
<title id="l01b-t">Proof, IdP session and app session over time</title>
<desc id="l01b-d">Four stages, in an order that is only for reading. Signed in: the proof is used once, the IdP session is open and the app session is open. Proof expires, at NotOnOrAfter or exp, which is not the session's lifetime. IdP session end: app sessions are not necessarily terminated. App session: it may live on, and for Entra the app must revoke it. The diagram highlights each stage in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
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
.l01b-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:16s;animation-timing-function:linear;animation-iteration-count:infinite}
.l01b-pk.l01b-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.l01b-pk.l01b-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.l01b-g{opacity:.45;animation-duration:16s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.l01b-flow:hover .l01b-g,svg.l01b-flow:hover .l01b-pk{animation-play-state:paused}
.l01b-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.l01b-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.l01b-btn:hover{background:var(--hover)}
.l01b-cb:focus-visible + .l01b-btn{outline:2px solid var(--accent);outline-offset:2px}
.l01b-cb:checked + .l01b-btn .l01b-off,.l01b-cb:not(:checked) + .l01b-btn .l01b-on{display:none}
.l01b-cb:checked ~ .l01b-box .l01b-g,.l01b-cb:checked ~ .l01b-box .l01b-pk{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.l01b-g{animation:none;opacity:1}.l01b-pk{animation:none;display:none}.l01b-btn{display:none}}
@keyframes l01b-g0{0%{opacity:1}25%{opacity:1}25.01%,100%{opacity:.45}}
@keyframes l01b-p0{0%,-0.01%{opacity:0;transform:translateX(0)}0%{opacity:1;transform:translateX(0)}25%{opacity:1;transform:translateX(58px)}25.01%,100%{opacity:0;transform:translateX(58px)}}
.l01b-g0{animation-name:l01b-g0}.l01b-p0{animation-name:l01b-p0}
@keyframes l01b-g1{0%,24.99%{opacity:.45}25%{opacity:1}50%{opacity:1}50.01%,100%{opacity:.45}}
@keyframes l01b-p1{0%,24.99%{opacity:0;transform:translateX(0)}25%{opacity:1;transform:translateX(0)}50%{opacity:1;transform:translateX(58px)}50.01%,100%{opacity:0;transform:translateX(58px)}}
.l01b-g1{animation-name:l01b-g1}.l01b-p1{animation-name:l01b-p1}
@keyframes l01b-g2{0%,49.99%{opacity:.45}50%{opacity:1}75%{opacity:1}75.01%,100%{opacity:.45}}
@keyframes l01b-p2{0%,49.99%{opacity:0;transform:translateX(0)}50%{opacity:1;transform:translateX(0)}75%{opacity:1;transform:translateX(58px)}75.01%,100%{opacity:0;transform:translateX(58px)}}
.l01b-g2{animation-name:l01b-g2}.l01b-p2{animation-name:l01b-p2}
@keyframes l01b-g3{0%,74.99%{opacity:.45}75%{opacity:1}100%{opacity:1}100.01%,100%{opacity:.45}}
.l01b-g3{animation-name:l01b-g3}
</style>
<defs>
<marker id="l01b-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="l01b-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="l01b-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<g class="l01b-g l01b-g0">
<rect class="l01b-box" x="14" y="40" width="123" height="127" rx="10"/>
<text class="l01b-ttl" x="76" y="67">Signed in</text>
<text class="l01b-nt" x="76" y="114">Proof: used once</text>
<text class="l01b-nt" x="76" y="131">IdP session: open</text>
<text class="l01b-nt" x="76" y="148">App session: open</text>
<line class="l01b-front" x1="145" y1="70" x2="209" y2="70" marker-end="url(#l01b-m-front)"/>
</g>
<g class="l01b-g l01b-g1">
<rect class="l01b-box" x="217" y="40" width="123" height="127" rx="10"/>
<text class="l01b-ttl" x="278" y="67">Proof expires</text>
<text class="l01b-sub" x="278" y="87">NotOnOrAfter, exp</text>
<text class="l01b-nt" x="278" y="114">Not the session's</text>
<text class="l01b-nt" x="278" y="131">lifetime</text>
<line class="l01b-front" x1="348" y1="70" x2="412" y2="70" marker-end="url(#l01b-m-front)"/>
</g>
<g class="l01b-g l01b-g2">
<rect class="l01b-box" x="420" y="40" width="123" height="127" rx="10"/>
<text class="l01b-ttl" x="482" y="67">IdP session end</text>
<text class="l01b-nt" x="482" y="114">App sessions are</text>
<text class="l01b-nt" x="482" y="131">not necessarily</text>
<text class="l01b-nt" x="482" y="148">terminated</text>
<line class="l01b-front" x1="551" y1="70" x2="615" y2="70" marker-end="url(#l01b-m-front)"/>
</g>
<g class="l01b-g l01b-g3">
<rect class="l01b-note-bad" x="623" y="40" width="123" height="127" rx="10"/>
<text class="l01b-ttl" x="684" y="67">App session</text>
<text class="l01b-sub" x="684" y="87">may live on</text>
<text class="l01b-nt" x="684" y="114">Entra: the app</text>
<text class="l01b-nt" x="684" y="131">must revoke it</text>
</g>
<circle class="l01b-pk l01b-p0" cx="151" cy="70" r="5.5"/>
<circle class="l01b-pk l01b-p1" cx="354" cy="70" r="5.5"/>
<circle class="l01b-pk l01b-p2" cx="557" cy="70" r="5.5"/>
<line class="l01b-front" x1="40" y1="203" x2="70" y2="203"/>
<text class="l01b-dim" x="78" y="207" style="text-anchor:start">next stage</text>
<rect class="l01b-note-bad" x="176" y="195" width="22" height="16" rx="4"/>
<text class="l01b-dim" x="206" y="207" style="text-anchor:start">the gap to close</text>
</svg>
</div>
</div>
<!-- /diagram:session-gap -->

Read left to right. The proof's expiry and the IdP session have no required relationship, so the order of the first three stages is only for reading. The proof's expiry is not the session's lifetime, and when the IdP session ends the app session may still be open; Entra says the app has to revoke it itself.

## What SSO buys, and where it stops

It is a control because policy runs at one point. Entra Conditional Access is an if-then rule (if a user wants an application, they must perform MFA), enforced after first-factor authentication. Okta app sign-in policies define how a user must authenticate and check requirements such as group membership, IP zone and risk. Either runs in step 3, whichever protocol sent the user to the IdP. A disabled IdP account cannot complete step 3, so it gets no new proofs. SSO does **not**:

- **Authorize.** Attributes and groups arrive; mapping them to roles is the app's logic.
- **Deprovision.** NIST: with just-in-time provisioning an RP can accumulate accounts the IdP no longer knows about unless the IdP signals terminations. Entra's guidance is automated provisioning and deprovisioning, plus apps revoking their own session tokens.
- **End other sessions.** See above.

Side doors skip the policy entirely: a local password, an API key, a session already open, an access token already issued.

## Failure modes to look for

- **SSO treated as authorization.** Everyone who can authenticate lands with a default or admin role. Deny by default and map roles from attributes.
- **App sessions outliving the IdP.** The leaver keeps working. Combine app-side deprovisioning, SLO or Universal Logout where supported, and a bounded app session.
- **Shared accounts.** NIST requires a federated identifier to be associated with a single subscriber. Logs, MFA and policy then describe an account, not a person.
- **Email as the key.** OIDC section 5.7: only `iss` plus `sub` are guaranteed unique; an issuer MAY reuse an email value for different users over time, and `email` MUST NOT be used as a unique identifier. NIST adds that different IdPs choose subject identifiers independently, so a bare `sub` can collide across issuers. Microsoft says never to use `email`, `preferred_username` or `unique_name` for access decisions, because tenant admins or sometimes users can control them, and recommends `tid` and `oid` as a combined key.

## Your task: decode, discover, read metadata

Ran locally (jq 1.7.1, xmllint, curl). The token and the SAML file are invented samples; the discovery fetch is a real public endpoint, output as fetched while writing. Not run against a live tenant.

```bash
TOKEN='eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6InNhbXBsZS1rZXktMSJ9.eyJpc3MiOiJodHRwczovL2lkcC5leGFtcGxlLmNvbSIsInN1YiI6InUtN2YzYTljMjEiLCJhdWQiOiJzYW1wbGUtYXBwLWNsaWVudC1pZCIsImlhdCI6MTc5MDAwMDAwMCwiYXV0aF90aW1lIjoxNzg5OTk5OTkwLCJleHAiOjE3OTAwMDAzMDAsImFtciI6WyJwd2QiLCJvdHAiXSwiZW1haWwiOiJhbGV4QGV4YW1wbGUuY29tIn0.dGhpcy1pcy1ub3QtYS1yZWFsLXNpZ25hdHVyZS1zYW1wbGUtb25seQ'
echo "$TOKEN" | jq -R 'split(".")[1] | gsub("-";"+") | gsub("_";"/") | @base64d | fromjson | {exp, expires_at: (.exp|todate), expired_now: (.exp < now)}' -c
# {"exp":1790000300,"expires_at":"2026-09-21T14:18:20Z","expired_now":true}
curl -s https://accounts.google.com/.well-known/openid-configuration | jq -c '{issuer, jwks_uri}'
# {"issuer":"https://accounts.google.com","jwks_uri":"https://www.googleapis.com/oauth2/v3/certs"}
```

Save this invented IdP metadata as `idp-sample.xml`, then run `xmllint --xpath '//@entityID | //@validUntil | //@use | //@Location' idp-sample.xml`:

```xml
<EntityDescriptor xmlns="urn:oasis:names:tc:SAML:2.0:metadata" xmlns:ds="http://www.w3.org/2000/09/xmldsig#"
                  entityID="https://idp.example.com/saml/sample" validUntil="2027-01-01T00:00:00Z">
  <IDPSSODescriptor protocolSupportEnumeration="urn:oasis:names:tc:SAML:2.0:protocol">
    <KeyDescriptor use="signing">
      <ds:KeyInfo><ds:X509Data><ds:X509Certificate>SAMPLE-NOT-A-REAL-CERTIFICATE</ds:X509Certificate></ds:X509Data></ds:KeyInfo>
    </KeyDescriptor>
    <SingleSignOnService Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect" Location="https://idp.example.com/saml/sample/sso"/>
  </IDPSSODescriptor>
</EntityDescriptor>
```

Real output: `entityID="https://idp.example.com/saml/sample"`, `validUntil="2027-01-01T00:00:00Z"`, `use="signing"`, `Location="https://idp.example.com/saml/sample/sso"`. Which of these does an app store to verify signatures, and what must happen to it when the IdP rotates its signing key? Which claim would you key accounts on? Lesson 2 goes deep on SAML.
