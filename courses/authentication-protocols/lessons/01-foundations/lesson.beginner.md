# Foundations: who is who, and why SSO exists

Facts checked 2026-10-06 against NIST SP 800-63-4 (final, 31 July 2025), RFC 6749, RFC 7519, OpenID Connect Core 1.0, the OASIS SAML 2.0 specifications, and the Okta and Microsoft Entra documentation.

This lesson names the parts behind a login, so later lessons on SAML, OpenID Connect and the rest have words to hang on. One example runs through it: Sam, a new employee, opens the company expense app.

## Authentication and authorization are different questions

- **Authentication** answers "who are you?" Sam proves he controls a secret, such as a password or a code from his phone. NIST describes it as checking the authenticators someone uses to claim a digital identity.
- **Authorization** answers "what may you do?" Once the app knows it is Sam, something decides whether he may only submit expenses or also approve them.

Single sign-on (SSO) answers the first question only. Four more words get mixed up constantly:

| Word | Plain meaning | Example |
| --- | --- | --- |
| **Identity** | Who someone is, as one service sees them. NIST says a digital identity is unique within one online service, so Sam can have several | Sam at the IdP, Sam at the expense app |
| **Account** | The record a service keeps: the person, their attributes, and the ways they can sign in | Sam's entry in the company directory |
| **Credential** | The secret or device used to prove it. NIST says *authenticator*; "credential" means different things in different documents (WebAuthn, in lesson 6, works with public-key credentials such as passkeys), so this course says what it means each time | a password, a phone code, a passkey |
| **Session** | The stretch of time after sign-in when a service remembers you, usually through a browser cookie the service issued | "I'm still signed in" |

## The parties: who is who

Three parties take part. **Sam** is the person. The **app** is what Sam wants to use. The **identity provider (IdP)** is the service that checks Sam's password and MFA and then tells the app who he is. Each standard names these roles differently:

| Role | SAML | OpenID Connect | NIST SP 800-63C |
| --- | --- | --- | --- |
| Service that checks the user | Identity Provider (IdP) | OpenID Provider (OP) | identity provider (IdP) |
| App that wants to know who the user is | Service Provider (SP) | Relying Party (RP) | relying party (RP) |
| The person | principal (also called subject) | End-User | subscriber |
| Signed statement about the person | assertion | ID token | assertion |

OAuth 2.0 (RFC 6749) uses a third set of names: resource owner (usually the person), client (the app), authorization server (hands out access tokens) and resource server (the API). An OAuth *access token* stands for a permission, with a scope and a duration. It is not a statement of who signed in. OpenID Connect is "a simple identity layer on top of the OAuth 2.0 protocol": its OP is an OAuth authorization server and its RP is an OAuth client. A **directory** stores accounts, such as a company's list of users. An IdP is the service that proves to apps who someone is. Many products do both jobs, which is why people blur them, but NIST keeps them apart: the IdP "provides a bridge" between the account and the app.

## Federation and SSO

NIST defines **federation** as authenticating a person to an app "without the RP directly verifying the subscriber's authenticators". The app never sees Sam's password; it trusts the IdP to check it. **SSO** is the result: Sam gets into many apps without a separate login at each. If an app asks for its own password, or checks it against the directory itself, that is not federation.

How does the app know a proof really came from the IdP? An admin sets this up once, before anyone signs in:

- **SAML:** the app is given the IdP's *metadata*, an XML file naming the IdP (its entityID), its signing keys and its sign-in URL.
- **OpenID Connect:** the app reads the IdP's *discovery document*, found at the issuer's address plus `/.well-known/openid-configuration`. It contains a `jwks_uri`, where the IdP publishes its signing keys.
- **The other direction:** the IdP is told where it may send proofs, using the app's *Assertion Consumer Service (ACS) URL* (SAML) or *redirect URI* (OpenID Connect).

<!-- diagram:trust-anatomy -->
<div style="position:relative;margin:20px 0">
<input type="checkbox" id="l01a-pause" class="l01a-cb" /><label for="l01a-pause" class="l01a-btn"><span class="l01a-off">Pause animation</span><span class="l01a-on">Play animation</span></label>
<div class="l01a-box" style="overflow-x:auto">
<svg class="l01a-flow" viewBox="0 0 760 442" role="img" aria-labelledby="l01a-t l01a-d" style="width:100%;min-width:640px;max-width:800px;height:auto;display:block;margin:0 auto">
<title id="l01a-t">What an admin sets up so the app can trust the IdP</title>
<desc id="l01a-d">A nested diagram of the one-time setup before anyone signs in. The app is given the IdP's details: in SAML, metadata, an XML file naming the IdP by its entityID with its signing keys and sign-in URL; in OpenID Connect, a discovery document with a jwks_uri where the IdP publishes its signing keys. The IdP is told where it may send proofs: the app's Assertion Consumer Service URL in SAML, or its redirect URI in OpenID Connect. The result is that the app trusts the IdP to say who Sam is, while what he may do is still the app's decision. The diagram highlights each part in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
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
.l01a-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:20s;animation-timing-function:linear;animation-iteration-count:infinite}
.l01a-pk.l01a-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.l01a-pk.l01a-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.l01a-g{opacity:.45;animation-duration:20s;animation-timing-function:linear;animation-iteration-count:infinite}
.l01a-h{opacity:0;animation-duration:20s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.l01a-flow:hover .l01a-g,svg.l01a-flow:hover .l01a-pk,svg.l01a-flow:hover .l01a-h{animation-play-state:paused}
.l01a-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.l01a-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.l01a-btn:hover{background:var(--hover)}
.l01a-cb:focus-visible + .l01a-btn{outline:2px solid var(--accent);outline-offset:2px}
.l01a-cb:checked + .l01a-btn .l01a-off,.l01a-cb:not(:checked) + .l01a-btn .l01a-on{display:none}
.l01a-cb:checked ~ .l01a-box .l01a-g,.l01a-cb:checked ~ .l01a-box .l01a-pk,.l01a-cb:checked ~ .l01a-box .l01a-h{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.l01a-g{animation:none;opacity:1}.l01a-pk{animation:none;display:none}.l01a-h{animation:none;opacity:0}.l01a-btn{display:none}}
@keyframes l01a-g0{0%{opacity:1}20%{opacity:1}20.01%,100%{opacity:.45}}
@keyframes l01a-h0{0%{opacity:1}20%{opacity:1}20.01%,100%{opacity:0}}
.l01a-g0{animation-name:l01a-g0}.l01a-h0{animation-name:l01a-h0}
@keyframes l01a-g1{0%,19.99%{opacity:.45}20%{opacity:1}40%{opacity:1}40.01%,100%{opacity:.45}}
@keyframes l01a-h1{0%,19.99%{opacity:0}20%{opacity:1}40%{opacity:1}40.01%,100%{opacity:0}}
.l01a-g1{animation-name:l01a-g1}.l01a-h1{animation-name:l01a-h1}
@keyframes l01a-g2{0%,39.99%{opacity:.45}40%{opacity:1}60%{opacity:1}60.01%,100%{opacity:.45}}
@keyframes l01a-h2{0%,39.99%{opacity:0}40%{opacity:1}60%{opacity:1}60.01%,100%{opacity:0}}
.l01a-g2{animation-name:l01a-g2}.l01a-h2{animation-name:l01a-h2}
@keyframes l01a-g3{0%,59.99%{opacity:.45}60%{opacity:1}80%{opacity:1}80.01%,100%{opacity:.45}}
@keyframes l01a-h3{0%,59.99%{opacity:0}60%{opacity:1}80%{opacity:1}80.01%,100%{opacity:0}}
.l01a-g3{animation-name:l01a-g3}.l01a-h3{animation-name:l01a-h3}
@keyframes l01a-g4{0%,79.99%{opacity:.45}80%{opacity:1}100%{opacity:1}100.01%,100%{opacity:.45}}
@keyframes l01a-h4{0%,79.99%{opacity:0}80%{opacity:1}100%{opacity:1}100.01%,100%{opacity:0}}
.l01a-g4{animation-name:l01a-g4}.l01a-h4{animation-name:l01a-h4}
</style>
<defs>
<marker id="l01a-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="l01a-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="l01a-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<rect class="l01a-box" x="14" y="16" width="440" height="368" rx="9"/><text class="l01a-ttlL" x="28" y="37">Set up once by an admin</text><text class="l01a-subL" x="28" y="54">before anyone signs in</text>
<rect class="l01a-nest" x="26" y="62" width="416" height="158" rx="9"/><text class="l01a-ttlL" x="40" y="83">What the app is given</text><text class="l01a-subL" x="40" y="100">the IdP's details</text>
<rect class="l01a-nest" x="38" y="108" width="392" height="46" rx="9"/><text class="l01a-ttlL" x="52" y="129">SAML: metadata</text><text class="l01a-subL" x="52" y="146">an XML file</text>
<rect class="l01a-nest" x="38" y="162" width="392" height="46" rx="9"/><text class="l01a-ttlL" x="52" y="183">OpenID Connect: discovery document</text><text class="l01a-subL" x="52" y="200">at the issuer's address</text>
<rect class="l01a-nest" x="26" y="228" width="416" height="144" rx="9"/><text class="l01a-ttlL" x="40" y="249">What the IdP is told</text><text class="l01a-subL" x="40" y="266">where it may send proofs</text>
<rect class="l01a-nest" x="38" y="274" width="392" height="46" rx="9"/><text class="l01a-ttlL" x="52" y="295">SAML: the ACS URL</text><text class="l01a-subL" x="52" y="312">Assertion Consumer Service</text>
<rect class="l01a-nest" x="38" y="328" width="392" height="32" rx="9"/><text class="l01a-ttlL" x="52" y="349">OpenID Connect: the redirect URI</text>
<g class="l01a-g l01a-g0">
<path class="l01a-conn" d="M454,33 L462,33 L462,42 L470,42" marker-end="url(#l01a-m-front)"/>
<rect class="l01a-note" x="484" y="10" width="262" height="65" rx="8"/>
<text class="l01a-nt" x="615" y="31">Result: the app trusts the IdP to say</text>
<text class="l01a-nt" x="615" y="48">who Sam is. What he may do is still</text>
<text class="l01a-nt" x="615" y="65">the app's decision.</text>
<circle class="l01a-badge l01a-b-front" cx="484" cy="42" r="12"/><text class="l01a-bt" x="484" y="47.0">1</text>
</g>
<g class="l01a-g l01a-g1">
<path class="l01a-conn" d="M430,125 L466,125 L466,125 L470,125" marker-end="url(#l01a-m-front)"/>
<rect class="l01a-note-good" x="484" y="101" width="262" height="48" rx="8"/>
<text class="l01a-nt" x="615" y="122">names the IdP (its entityID), its</text>
<text class="l01a-nt" x="615" y="139">signing keys and its sign-in URL</text>
<circle class="l01a-badge l01a-b-good" cx="484" cy="125" r="12"/><text class="l01a-bt" x="484" y="129.5">2</text>
</g>
<g class="l01a-g l01a-g2">
<path class="l01a-conn" d="M430,179 L470,179 L470,183 L470,183" marker-end="url(#l01a-m-front)"/>
<rect class="l01a-note-good" x="484" y="159" width="262" height="48" rx="8"/>
<text class="l01a-nt" x="615" y="180">has a jwks_uri, where the IdP</text>
<text class="l01a-nt" x="615" y="197">publishes its signing keys</text>
<circle class="l01a-badge l01a-b-good" cx="484" cy="183" r="12"/><text class="l01a-bt" x="484" y="187.5">3</text>
</g>
<g class="l01a-g l01a-g3">
<path class="l01a-conn" d="M430,291 L474,291 L474,291 L470,291" marker-end="url(#l01a-m-front)"/>
<rect class="l01a-note-good" x="484" y="276" width="262" height="31" rx="8"/>
<text class="l01a-nt" x="615" y="296">where the IdP may send proofs</text>
<circle class="l01a-badge l01a-b-good" cx="484" cy="291" r="12"/><text class="l01a-bt" x="484" y="295.5">4</text>
</g>
<g class="l01a-g l01a-g4">
<path class="l01a-conn" d="M430,345 L462,345 L462,345 L470,345" marker-end="url(#l01a-m-front)"/>
<rect class="l01a-note-good" x="484" y="330" width="262" height="31" rx="8"/>
<text class="l01a-nt" x="615" y="350">where the IdP may send proofs</text>
<circle class="l01a-badge l01a-b-good" cx="484" cy="345" r="12"/><text class="l01a-bt" x="484" y="349.5">5</text>
</g>
<g class="l01a-h l01a-h0">
<rect class="l01a-hl" x="14" y="16" width="440" height="368" rx="9"/>
</g>
<g class="l01a-h l01a-h1">
<rect class="l01a-hl" x="38" y="108" width="392" height="46" rx="9"/>
</g>
<g class="l01a-h l01a-h2">
<rect class="l01a-hl" x="38" y="162" width="392" height="46" rx="9"/>
</g>
<g class="l01a-h l01a-h3">
<rect class="l01a-hl" x="38" y="274" width="392" height="46" rx="9"/>
</g>
<g class="l01a-h l01a-h4">
<rect class="l01a-hl" x="38" y="328" width="392" height="32" rx="9"/>
</g>
<rect class="l01a-note" x="40" y="410" width="22" height="16" rx="4"/>
<text class="l01a-dim" x="70" y="422" style="text-anchor:start">who gives what</text>
<rect class="l01a-note-good" x="193" y="410" width="22" height="16" rx="4"/>
<text class="l01a-dim" x="223" y="422" style="text-anchor:start">what it contains</text>
</svg>
</div>
</div>
<!-- /diagram:trust-anatomy -->

Read the setup in two halves: what the app is given about the IdP, and what the IdP is told about the app. Callouts 2 to 5 say what each piece holds or is for; callout 1 is what the app ends up trusting the IdP for.

The app trusts the IdP to say who Sam is and to pass along attributes such as his email. What each of those lets Sam do is still the app's decision.

## The first sign-in, end to end

<!-- diagram:trust-signin -->
<div style="position:relative;margin:20px 0">
<input type="checkbox" id="tr-pause" class="tr-cb" /><label for="tr-pause" class="tr-btn"><span class="tr-off">Pause animation</span><span class="tr-on">Play animation</span></label>
<div class="tr-box" style="overflow-x:auto">
<svg class="tr-flow" viewBox="0 0 760 762" role="img" aria-labelledby="tr-t tr-d" style="width:100%;min-width:640px;max-width:800px;height:auto;display:block;margin:0 auto">
<title id="tr-t">Sam's first sign-in, in five steps</title>
<desc id="tr-d">Three parties: the app, Sam's browser, and the identity provider. Step 1: Sam opens the app and has no session with it yet. Step 2: the app redirects his browser to the identity provider, carrying a sign-in request. Step 3: Sam signs in at the identity provider with his password, MFA and company rules, and the identity provider starts its own session for him. Step 4: the identity provider returns a signed proof for the app, the assertion in SAML or a one-time code in OpenID Connect, and the browser carries it to the app. Step 5: the app checks the proof's signature, that it came from the expected identity provider, that it was addressed to this app and that it has not expired, then creates its own session, normally a cookie. The diagram highlights each step in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
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
.tr-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:15s;animation-timing-function:linear;animation-iteration-count:infinite}
.tr-pk.tr-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.tr-pk.tr-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.tr-g{opacity:.45;animation-duration:15s;animation-timing-function:linear;animation-iteration-count:infinite}
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
<line class="tr-life" x1="110" y1="72" x2="110" y2="710"/>
<line class="tr-life" x1="380" y1="72" x2="380" y2="710"/>
<line class="tr-life" x1="650" y1="72" x2="650" y2="710"/>
<rect class="tr-box" x="20" y="10" width="180" height="62" rx="10"/><text class="tr-ttl" x="110" y="36">The app</text><text class="tr-sub" x="110" y="56">what Sam wants to use</text>
<rect class="tr-box" x="290" y="10" width="180" height="62" rx="10"/><text class="tr-ttl" x="380" y="36">Sam's browser</text><text class="tr-sub" x="380" y="56">carries the messages shown</text>
<rect class="tr-hot" x="560" y="10" width="180" height="62" rx="10"/><text class="tr-ttl" x="650" y="36">The IdP</text><text class="tr-sub" x="650" y="56">checks his password and MFA</text>
<g class="tr-g tr-g0">
<text class="tr-main" x="245" y="108">Sam opens the app</text>
<text class="tr-dim" x="245" y="124">he has no session yet</text>
<line class="tr-front" x1="366" y1="138" x2="124" y2="138" marker-end="url(#tr-m-front)"/>
<circle class="tr-badge tr-b-front" cx="380" cy="138" r="12"/><text class="tr-bt" x="380" y="142.5">1</text>
</g>
<g class="tr-g tr-g1">
<text class="tr-main" x="245" y="178">redirect to the IdP</text>
<text class="tr-dim" x="245" y="194">carrying a sign-in request</text>
<line class="tr-front" x1="124" y1="208" x2="366" y2="208" marker-end="url(#tr-m-front)"/>
<circle class="tr-badge tr-b-front" cx="110" cy="208" r="12"/><text class="tr-bt" x="110" y="212.5">2</text>
<text class="tr-main" x="515" y="248">browser goes to the IdP</text>
<line class="tr-front" x1="394" y1="262" x2="636" y2="262" marker-end="url(#tr-m-front)"/>
</g>
<g class="tr-g tr-g2">
<rect class="tr-note" x="549" y="296" width="201" height="65" rx="8"/>
<text class="tr-nt" x="650" y="317">Sam signs in: password,</text>
<text class="tr-nt" x="650" y="334">MFA, company rules</text>
<text class="tr-nt" x="650" y="351">IdP starts its own session</text>
<circle class="tr-badge tr-b-plain" cx="549" cy="328" r="12"/><text class="tr-bt" x="549" y="333.0">3</text>
</g>
<g class="tr-g tr-g3">
<text class="tr-main" x="515" y="395">a signed proof for the app</text>
<text class="tr-dim" x="515" y="411">SAML: the assertion</text>
<text class="tr-dim" x="515" y="427">OIDC: a one-time code</text>
<line class="tr-front" x1="636" y1="441" x2="394" y2="441" marker-end="url(#tr-m-front)"/>
<circle class="tr-badge tr-b-front" cx="650" cy="441" r="12"/><text class="tr-bt" x="650" y="445.5">4</text>
<text class="tr-main" x="245" y="481">browser carries it to the app</text>
<line class="tr-front" x1="366" y1="495" x2="124" y2="495" marker-end="url(#tr-m-front)"/>
</g>
<g class="tr-g tr-g4">
<rect class="tr-note-good" x="10" y="529" width="241" height="65" rx="8"/>
<text class="tr-nt" x="130" y="550">checks: signature, expected IdP,</text>
<text class="tr-nt" x="130" y="567">addressed to this app,</text>
<text class="tr-nt" x="130" y="584">not expired</text>
<circle class="tr-badge tr-b-good" cx="10" cy="562" r="12"/><text class="tr-bt" x="10" y="566.0">5</text>
<text class="tr-main" x="245" y="628">its own session,</text>
<text class="tr-dim" x="245" y="644">normally a cookie</text>
<line class="tr-front" x1="124" y1="658" x2="366" y2="658" marker-end="url(#tr-m-front)"/>
</g>
<circle class="tr-pk tr-p0" cx="360" cy="138" r="5.5"/>
<circle class="tr-pk tr-p1" cx="400" cy="262" r="5.5"/>
<circle class="tr-pk tr-p3" cx="360" cy="495" r="5.5"/>
<circle class="tr-pk tr-p4" cx="130" cy="658" r="5.5"/>
<line class="tr-front" x1="40" y1="738" x2="70" y2="738"/>
<text class="tr-dim" x="78" y="742" style="text-anchor:start">message through Sam's browser</text>
<rect class="tr-note-good" x="297" y="730" width="22" height="16" rx="4"/>
<text class="tr-dim" x="327" y="742" style="text-anchor:start">what the app checks</text>
</svg>
</div>
</div>
<!-- /diagram:trust-signin -->

The badges 1 to 5 match the numbered steps below. Every arrow shown passes through the browser; the OIDC code swap in step 4 is a separate direct call from the app to the IdP, covered in lesson 4.

1. Sam opens the app. He has no session with it yet.
2. The app redirects Sam's browser to the IdP, carrying a sign-in request.
3. Sam signs in at the IdP with his password, MFA and company rules. The IdP starts its own session for him, so a second app tomorrow will find him already signed in at the IdP and skip this step.
4. The IdP returns a signed proof. In SAML it is the *assertion*. In OpenID Connect's code flow the browser carries a one-time code, which the app swaps for the *ID token*.
5. The app checks the proof's signature, that it came from the expected IdP, that it was addressed to this app, and that it has not expired. Then it creates its own session, normally a cookie.

## Proof, IdP session and app session

Three things are created along the way, each with its own clock:

| Thing | Created by | Used by | How long |
| --- | --- | --- | --- |
| Proof (assertion or ID token) | the IdP | the app, once, at sign-in | its own expiry (`exp` in an ID token is required; a SAML sign-in carries a `NotOnOrAfter` time after which the app must refuse the proof) |
| IdP session | the IdP | the IdP | set by the IdP's policy |
| App session | the app | the app | set by the app |

The proof's expiry says how long the app may accept the proof, not how long Sam stays signed in. NIST: after the app consumes an assertion, its session is independent of the assertion, and in most cases the app's session "will far outlive" it.

**What if the IdP session ends?** Say an admin disables Sam's account. NIST says the IdP ending its session "will not necessarily terminate" Sam's sessions at apps. Microsoft's Entra documentation says Entra "can't directly revoke a session token issued by an application", so the app must revoke access itself. Okta's Single Logout works only when an app starts it, and only for apps that support it. Disabling Sam stops *new* sign-ins; sessions already open may carry on.

<!-- diagram:session-gap -->
<div style="position:relative;margin:20px 0">
<input type="checkbox" id="l01b-pause" class="l01b-cb" /><label for="l01b-pause" class="l01b-btn"><span class="l01b-off">Pause animation</span><span class="l01b-on">Play animation</span></label>
<div class="l01b-box" style="overflow-x:auto">
<svg class="l01b-flow" viewBox="0 0 760 227" role="img" aria-labelledby="l01b-t l01b-d" style="width:100%;min-width:640px;max-width:800px;height:auto;display:block;margin:0 auto">
<title id="l01b-t">What happens to Sam's sessions when an admin disables him</title>
<desc id="l01b-d">Three stages. First Sam is signed in, with an IdP session and an app session open. Then an admin disables Sam's account at the IdP, which stops new sign-ins; this is not necessarily passed on to the app. The third stage is the app session, already open, which may carry on, and the app must revoke access itself. The diagram highlights each stage in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
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
.l01b-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:14s;animation-timing-function:linear;animation-iteration-count:infinite}
.l01b-pk.l01b-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.l01b-pk.l01b-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.l01b-g{opacity:.45;animation-duration:14s;animation-timing-function:linear;animation-iteration-count:infinite}
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
<rect class="l01b-box" x="14" y="40" width="171" height="127" rx="10"/>
<text class="l01b-ttl" x="99" y="67">Signed in</text>
<text class="l01b-sub" x="99" y="87">Sam is working</text>
<text class="l01b-nt" x="99" y="114">IdP session: open</text>
<text class="l01b-nt" x="99" y="131">App session: open</text>
<text class="l01b-main" x="240" y="48">admin disables</text>
<text class="l01b-dim" x="240" y="64">his account</text>
<line class="l01b-front" x1="193" y1="70" x2="287" y2="70" marker-end="url(#l01b-m-front)"/>
</g>
<g class="l01b-g l01b-g1">
<rect class="l01b-note-good" x="295" y="40" width="171" height="127" rx="10"/>
<text class="l01b-ttl" x="380" y="67">Sam disabled</text>
<text class="l01b-sub" x="380" y="87">at the IdP</text>
<text class="l01b-nt" x="380" y="114">Stops new sign-ins</text>
<text class="l01b-main" x="520" y="48">not necessarily</text>
<text class="l01b-dim" x="520" y="64">passed on</text>
<line class="l01b-front" x1="473" y1="70" x2="567" y2="70" marker-end="url(#l01b-m-front)"/>
</g>
<g class="l01b-g l01b-g2">
<rect class="l01b-note-bad" x="575" y="40" width="171" height="127" rx="10"/>
<text class="l01b-ttl" x="661" y="67">App session</text>
<text class="l01b-sub" x="661" y="87">already open</text>
<text class="l01b-nt" x="661" y="114">May carry on</text>
<text class="l01b-nt" x="661" y="131">The app must revoke</text>
<text class="l01b-nt" x="661" y="148">access itself</text>
</g>
<circle class="l01b-pk l01b-p0" cx="199" cy="70" r="5.5"/>
<circle class="l01b-pk l01b-p1" cx="479" cy="70" r="5.5"/>
<line class="l01b-front" x1="40" y1="203" x2="70" y2="203"/>
<text class="l01b-dim" x="78" y="207" style="text-anchor:start">what happens next</text>
<rect class="l01b-note-good" x="220" y="195" width="22" height="16" rx="4"/>
<text class="l01b-dim" x="250" y="207" style="text-anchor:start">what disabling does</text>
<rect class="l01b-note-bad" x="405" y="195" width="22" height="16" rx="4"/>
<text class="l01b-dim" x="435" y="207" style="text-anchor:start">what may carry on</text>
</svg>
</div>
</div>
<!-- /diagram:session-gap -->

Follow the three stages left to right: Sam is signed in, an admin disables him at the IdP, and the session he already has in the app may still be open.

## Why companies use SSO, and what it does not do

SSO is a security control because the rules live in one place. Microsoft describes a Conditional Access policy as an if-then statement: if a user wants an application, then they must perform multifactor authentication. Okta's app sign-in policies likewise define how a user must authenticate to an app. Disabling one account in one place also stops new sign-ins to every app that uses the IdP. This covers only sign-ins that go through the IdP; an app that still accepts its own passwords has a side door the IdP's rules never see.

SSO leaves three jobs undone, and two habits undermine it:

- **Authorize.** It proves who Sam is. The app still decides what he may do.
- **Remove the app's own account.** The sign-in steps above carry no "disable" message to apps. NIST warns that an app that creates accounts on first sign-in can pile up accounts the IdP no longer knows about, unless the IdP tells it. Telling the app is a separate job, provisioning (lesson 5 covers SCIM), and whether a session already open then ends is up to the app.
- **End sessions in other apps.** See the section above.
- **Habit to avoid: shared accounts.** NIST requires each federated identifier to be associated with a single subscriber, meaning one person. If three colleagues share a login, the logs show which account acted, not which person.
- **Habit to avoid: email as the identifier.** OpenID Connect says only the issuer (`iss`) plus the subject (`sub`) are guaranteed unique. An email can be reused for another person or change over time, so it must not be used as a unique identifier.

## Your task: read a token

Ran locally with jq 1.7.1; the token is an invented sample with a junk signature. A JWT is three base64url-encoded parts separated by dots, and the middle part is the payload.

```bash
TOKEN='eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6InNhbXBsZS1rZXktMSJ9.eyJpc3MiOiJodHRwczovL2lkcC5leGFtcGxlLmNvbSIsInN1YiI6InUtN2YzYTljMjEiLCJhdWQiOiJzYW1wbGUtYXBwLWNsaWVudC1pZCIsImlhdCI6MTc5MDAwMDAwMCwiYXV0aF90aW1lIjoxNzg5OTk5OTkwLCJleHAiOjE3OTAwMDAzMDAsImFtciI6WyJwd2QiLCJvdHAiXSwiZW1haWwiOiJhbGV4QGV4YW1wbGUuY29tIn0.dGhpcy1pcy1ub3QtYS1yZWFsLXNpZ25hdHVyZS1zYW1wbGUtb25seQ'
echo "$TOKEN" | jq -cR 'split(".")[1] | gsub("-";"+") | gsub("_";"/") | @base64d | fromjson'
# {"iss":"https://idp.example.com","sub":"u-7f3a9c21","aud":"sample-app-client-id","iat":1790000000,"auth_time":1789999990,"exp":1790000300,"amr":["pwd","otp"],"email":"alex@example.com"}
```

Find the issuer (`iss`) and the claim the app should use to recognise this person (`sub`, not `email`). Compare `exp` with `date +%s`: has the proof expired? Could a stranger who copied the token read it? Yes: RFC 7519 warns a JWT "may contain privacy-sensitive information", so keep secrets out of it. Lesson 2 starts on SAML.
