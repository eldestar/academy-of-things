# OpenID Connect and JWT validation

Priya opens ExampleCRM, a web app her company uses. She does not type a password into ExampleCRM. The app sends her to Okta, Okta signs her in, and ExampleCRM learns who she is. This lesson is about the protocol that carries that answer back, and the checks the app must make before it believes it. Facts checked 2026-10-06 against the OpenID Connect specifications, the JWT RFCs and vendor docs.

## What OpenID Connect adds

OAuth 2.0 (lesson 3) lets an app get permission to do things. On its own it does not tell the app who the user is. OpenID Connect (OIDC) is an identity layer built on top of OAuth 2.0: it adds a signed answer to "who just logged in?".

- The **relying party (RP)** is the app that relies on someone else to log users in. ExampleCRM is the RP.
- The **OpenID Provider (OP)** is the identity provider, such as Okta or Microsoft Entra ID.
- The app turns OIDC on by asking for the `openid` **scope**, a word that names what the app is asking for. Other scopes ask for groups of details: `profile` (name and similar) and `email`.

When the sign-in finishes, the app receives two things that are not interchangeable:

- The **ID token** is the OP's signed statement about the login: who the user is, who issued the statement, which app it is for, and when it expires. It is a **JWT** (JSON Web Token): three parts separated by dots, `header.payload.signature`. The details in the payload are called **claims**. The payload is only encoded, not secret, so anyone holding the token can read it. The **signature** is what makes it trustworthy.
- The **access token** is a string representing permission issued to the app, for example to call the OP's **UserInfo** endpoint, which returns more claims about the user. An app usually treats it as opaque, meaning it does not look inside.

> An app must not treat "I hold a valid access token" as proof that this person just logged in. OAuth alone cannot provide information about the authentication of the user. Only the ID token, validated, is the proof of login.

## How a sign-in works, step by step

<!-- diagram:oidc-code-flow -->
<div style="position:relative;margin:20px 0">
<input type="checkbox" id="oi-pause" class="oi-cb" /><label for="oi-pause" class="oi-btn"><span class="oi-off">Pause animation</span><span class="oi-on">Play animation</span></label>
<div class="oi-box" style="overflow-x:auto">
<svg class="oi-flow" viewBox="0 0 760 793" role="img" aria-labelledby="oi-t oi-d" style="width:100%;min-width:640px;max-width:800px;height:auto;display:block;margin:0 auto">
<title id="oi-t">OpenID Connect authorization code flow, ending in ID token validation</title>
<desc id="oi-d">Two parties: the relying party (your app) and the OpenID Provider. Step 1: the app sends the user's browser to the provider's authorization endpoint with scope openid, a state, an optional nonce and, for a public client, a PKCE code_challenge with method S256. The user signs in at the provider. Step 2: the provider redirects the browser back to the app's redirect URI with an authorization code and the state. Step 3: the app, server to server, posts the code to the token endpoint, with the PKCE code_verifier if it is a public client or with client authentication if it is a confidential client, and receives an ID token and an access token. Step 4: the app validates the ID token: signature using the provider's published keys, then iss, aud, exp and, if it sent a nonce, nonce. Step 5, optional: the app calls the UserInfo endpoint with the access token and checks that sub matches the ID token's sub. The diagram highlights each step in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
<style>
.oi-box{fill:var(--panel);stroke:var(--border-strong);stroke-width:1.5}
.oi-hot{fill:var(--panel);stroke:var(--accent);stroke-width:2.5}
.oi-ttl{fill:var(--text);font:600 15px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.oi-sub{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.oi-life{stroke:var(--border-strong);stroke-width:1.5;stroke-dasharray:4 5}
.oi-front{stroke:var(--accent);stroke-width:2;fill:none}
.oi-back{stroke:var(--muted);stroke-width:2;stroke-dasharray:7 5;fill:none}
.oi-bad{stroke:var(--bad);stroke-width:2;fill:none}
.oi-main{fill:var(--text);font:600 13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.oi-badt{fill:var(--bad-text)}
.oi-dim{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.oi-badge{fill:var(--accent)}
.oi-b-back{fill:var(--muted)}
.oi-b-bad{fill:var(--bad)}
.oi-b-good{fill:var(--good)}
.oi-bt{fill:var(--on-accent);font:700 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.oi-note{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.oi-note-good{fill:var(--good-bg);stroke:var(--good);stroke-width:1.5}
.oi-note-bad{fill:var(--bad-bg);stroke:var(--bad);stroke-width:1.5}
.oi-nt{fill:var(--body);font:12.5px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.oi-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:22s;animation-timing-function:linear;animation-iteration-count:infinite}
.oi-pk.oi-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.oi-pk.oi-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.oi-g{opacity:.45;animation-duration:22s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.oi-flow:hover .oi-g,svg.oi-flow:hover .oi-pk{animation-play-state:paused}
.oi-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.oi-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.oi-btn:hover{background:var(--hover)}
.oi-cb:focus-visible + .oi-btn{outline:2px solid var(--accent);outline-offset:2px}
.oi-cb:checked + .oi-btn .oi-off,.oi-cb:not(:checked) + .oi-btn .oi-on{display:none}
.oi-cb:checked ~ .oi-box .oi-g,.oi-cb:checked ~ .oi-box .oi-pk{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.oi-g{animation:none;opacity:1}.oi-pk{animation:none;display:none}.oi-btn{display:none}}
@keyframes oi-g0{0%{opacity:1}16.667%{opacity:1}16.677%,100%{opacity:.45}}
@keyframes oi-p0{0%,-0.01%{opacity:0;transform:translateX(0)}0%{opacity:1;transform:translateX(0)}16.667%{opacity:1;transform:translateX(506px)}16.677%,100%{opacity:0;transform:translateX(506px)}}
.oi-g0{animation-name:oi-g0}.oi-p0{animation-name:oi-p0}
@keyframes oi-g1{0%,16.657%{opacity:.45}16.667%{opacity:1}33.333%{opacity:1}33.343%,100%{opacity:.45}}
.oi-g1{animation-name:oi-g1}
@keyframes oi-g2{0%,33.323%{opacity:.45}33.333%{opacity:1}50%{opacity:1}50.01%,100%{opacity:.45}}
@keyframes oi-p2{0%,33.323%{opacity:0;transform:translateX(0)}33.333%{opacity:1;transform:translateX(0)}50%{opacity:1;transform:translateX(-506px)}50.01%,100%{opacity:0;transform:translateX(-506px)}}
.oi-g2{animation-name:oi-g2}.oi-p2{animation-name:oi-p2}
@keyframes oi-g3{0%,49.99%{opacity:.45}50%{opacity:1}66.667%{opacity:1}66.677%,100%{opacity:.45}}
@keyframes oi-p3{0%,49.99%{opacity:0;transform:translateX(0)}50%{opacity:1;transform:translateX(0)}66.667%{opacity:1;transform:translateX(-506px)}66.677%,100%{opacity:0;transform:translateX(-506px)}}
.oi-g3{animation-name:oi-g3}.oi-p3{animation-name:oi-p3}
@keyframes oi-g4{0%,66.657%{opacity:.45}66.667%{opacity:1}83.333%{opacity:1}83.343%,100%{opacity:.45}}
.oi-g4{animation-name:oi-g4}
@keyframes oi-g5{0%,83.323%{opacity:.45}83.333%{opacity:1}100%{opacity:1}100.01%,100%{opacity:.45}}
@keyframes oi-p5{0%,83.323%{opacity:0;transform:translateX(0)}83.333%{opacity:1;transform:translateX(0)}100%{opacity:1;transform:translateX(-506px)}100.01%,100%{opacity:0;transform:translateX(-506px)}}
.oi-g5{animation-name:oi-g5}.oi-p5{animation-name:oi-p5}
</style>
<defs>
<marker id="oi-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="oi-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="oi-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<line class="oi-life" x1="110" y1="72" x2="110" y2="741"/>
<line class="oi-life" x1="650" y1="72" x2="650" y2="741"/>
<rect class="oi-hot" x="20" y="10" width="180" height="62" rx="10"/><text class="oi-ttl" x="110" y="36">Relying party</text><text class="oi-sub" x="110" y="56">your app (the OAuth client)</text>
<rect class="oi-box" x="560" y="10" width="180" height="62" rx="10"/><text class="oi-ttl" x="650" y="36">OpenID Provider</text><text class="oi-sub" x="650" y="56">Okta, Entra ID, any OP</text>
<g class="oi-g oi-g0">
<text class="oi-main" x="380" y="108">redirect to the authorization endpoint</text>
<text class="oi-dim" x="380" y="124">scope=openid, state, optional nonce</text>
<text class="oi-dim" x="380" y="140">public client adds code_challenge (S256)</text>
<line class="oi-front" x1="124" y1="154" x2="636" y2="154" marker-end="url(#oi-m-front)"/>
<circle class="oi-badge oi-b-front" cx="110" cy="154" r="12"/><text class="oi-bt" x="110" y="158.5">1</text>
</g>
<g class="oi-g oi-g1">
<rect class="oi-note" x="529" y="188" width="221" height="48" rx="8"/>
<text class="oi-nt" x="640" y="209">user signs in at the provider</text>
<text class="oi-nt" x="640" y="226">(MFA, policy, consent)</text>
</g>
<g class="oi-g oi-g2">
<text class="oi-main" x="380" y="270">redirect to redirect_uri</text>
<text class="oi-dim" x="380" y="286">code and state</text>
<line class="oi-front" x1="636" y1="300" x2="124" y2="300" marker-end="url(#oi-m-front)"/>
<circle class="oi-badge oi-b-front" cx="650" cy="300" r="12"/><text class="oi-bt" x="650" y="304.5">2</text>
</g>
<g class="oi-g oi-g3">
<text class="oi-main" x="380" y="340">POST to the token endpoint</text>
<text class="oi-dim" x="380" y="356">code, plus code_verifier (public client)</text>
<text class="oi-dim" x="380" y="372">or client authentication (confidential)</text>
<line class="oi-back" x1="124" y1="386" x2="636" y2="386" marker-end="url(#oi-m-back)"/>
<circle class="oi-badge oi-b-back" cx="110" cy="386" r="12"/><text class="oi-bt" x="110" y="390.5">3</text>
<text class="oi-main" x="380" y="426">token response</text>
<text class="oi-dim" x="380" y="442">id_token and access_token</text>
<line class="oi-back" x1="636" y1="456" x2="124" y2="456" marker-end="url(#oi-m-back)"/>
</g>
<g class="oi-g oi-g4">
<rect class="oi-note-good" x="10" y="490" width="313" height="65" rx="8"/>
<text class="oi-nt" x="166" y="511">validate the ID token:</text>
<text class="oi-nt" x="166" y="528">signature (provider's JWKS), iss, aud, exp,</text>
<text class="oi-nt" x="166" y="545">nonce if one was sent</text>
<circle class="oi-badge oi-b-good" cx="10" cy="522" r="12"/><text class="oi-bt" x="10" y="527.0">4</text>
</g>
<g class="oi-g oi-g5">
<text class="oi-main" x="380" y="589">optional: GET UserInfo</text>
<text class="oi-dim" x="380" y="605">access token as Bearer</text>
<line class="oi-back" x1="124" y1="619" x2="636" y2="619" marker-end="url(#oi-m-back)"/>
<circle class="oi-badge oi-b-back" cx="110" cy="619" r="12"/><text class="oi-bt" x="110" y="623.5">5</text>
<text class="oi-main" x="380" y="659">claims; sub must equal</text>
<text class="oi-dim" x="380" y="675">the ID token's sub</text>
<line class="oi-back" x1="636" y1="689" x2="124" y2="689" marker-end="url(#oi-m-back)"/>
</g>
<circle class="oi-pk oi-p0" cx="130" cy="154" r="5.5"/>
<circle class="oi-pk oi-p2" cx="630" cy="300" r="5.5"/>
<circle class="oi-pk oi-p3 oi-pkback" cx="630" cy="456" r="5.5"/>
<circle class="oi-pk oi-p5 oi-pkback" cx="630" cy="689" r="5.5"/>
<line class="oi-front" x1="40" y1="769" x2="70" y2="769"/>
<text class="oi-dim" x="78" y="773" style="text-anchor:start">through the user's browser</text>
<line class="oi-back" x1="278" y1="769" x2="308" y2="769"/>
<text class="oi-dim" x="316" y="773" style="text-anchor:start">server to server</text>
<rect class="oi-note-good" x="452" y="761" width="22" height="16" rx="4"/>
<text class="oi-dim" x="482" y="773" style="text-anchor:start">what your handler must do</text>
</svg>
</div>
</div>
<!-- /diagram:oidc-code-flow -->

Steps 1 and 2 pass through the browser, steps 3 and 5 are server to server, and step 4 is the check your app must do itself.

The numbers in the diagram match the numbered steps that follow.

1. ExampleCRM sends Priya's browser to the OP with `scope=openid`, plus a fresh random **nonce** (new for every sign-in; the code flow makes it optional, but ExampleCRM always sends one) and a `state` value. The app keeps both. `state` only lets the app match the returning browser to the request it sent; it says nothing about who the user is. Priya signs in at the OP, including any MFA. An app that cannot keep a secret, such as a mobile app or a page that runs only in the browser, is a **public client**. It also sends a `code_challenge`, a fingerprint of a one-time secret it invents for this sign-in; this is **PKCE**, covered in lesson 3. ExampleCRM runs on a server, so it is a **confidential client**.
2. The OP sends the browser back to ExampleCRM's registered address with a **code** and the `state`.
3. ExampleCRM, server to server, trades the code at the OP's token endpoint for the ID token and the access token. It proves who it is by authenticating as a confidential client; a public client instead sends the one-time secret itself (the `code_verifier`), which the OP checks against the `code_challenge`. PKCE is recommended for confidential clients too.
4. ExampleCRM **validates** the ID token (next section). Only then does it log Priya in.
5. Optionally it calls UserInfo with the access token. The `sub` in the answer must match the ID token's `sub`; if not, the answer is discarded.

## The five checks

The ID token arrived, but a forged token looks identical. ExampleCRM checks, before trusting anything inside:

1. **Signature**: made by a key the OP published. The app decides which signing algorithm it accepts; it never trusts the token's own header to choose.
2. **`iss` (issuer)**: exactly the OP the app is configured to use, for example `https://login.example.com`.
3. **`aud` (audience)**: includes this app's own client ID. The same OP signs tokens for many apps; a token meant for another app must be rejected here.
4. **`exp` (expiry)**: the time has not passed. Servers' clocks drift, so apps may allow a small leeway, usually no more than a few minutes. This is a token lifetime, not a session lifetime.
5. **`nonce`**, if the app sent one (ExampleCRM always does): matches the random value this app created for this browser's sign-in. A captured, still-valid token replayed into another session fails because the nonce does not match.

## Keys: how the app knows the signature is real

The app does not have a secret shared with the OP. The OP publishes its **public keys** in a **JWKS** (JSON Web Key Set) at a web address called `jwks_uri`. The address is listed in the OP's discovery document, found at `/.well-known/openid-configuration` under the issuer's URL. Each key has a label, the `kid`, and the token's header says which `kid` signed it.

Providers change signing keys on a schedule; Okta documents that its schedule is currently four times a year and can change without notice. So an app must never hardcode a key. When it sees a `kid` it has not got, it fetches the JWKS again. An app with a stale or hardcoded key rejects every new token with "invalid signature", usually the morning after a rotation.

## Who is this person?

Use `sub` (subject), the OP's identifier for the user. It is never reassigned to another person. Do not identify users by email: addresses change when names change, and an issuer may give an old address to someone new. `email_verified: true` only means the OP says it checked, and how it checked depends on the OP's arrangements. Neither `preferred_username` nor `name` is guaranteed unique.

## Logging out

Signing out of ExampleCRM, when its Sign out button only clears its own session cookie, ends ExampleCRM's own session. Priya's session at the OP is separate. If she clicks Sign in again, the OP may sign her straight back in with no password. To end the OP session, the app sends the browser to the OP's logout address; the OP may still ask her whether to log out there too. Telling other apps is a separate feature (front-channel or back-channel logout, covered in the next levels).

## Your task

Below is an invented, already-decoded sample payload; assume the token has not expired (`exp` is the year 2100). ExampleCRM's client ID is `crm-client-77`, its issuer is `https://login.example.com`, and the nonce stored for this browser was `k29x`.

```json
{"iss": "https://login.example.com", "sub": "00u1a2b3", "aud": "wiki-client-12", "exp": 4102444800, "nonce": "k29x", "email": "priya@example.com"}
```

Name the check that fails, and say which field you would use to identify Priya after login. Then read the intermediate lesson to try this on a real signed token. Next: SCIM, which keeps accounts in step with the identity provider.
