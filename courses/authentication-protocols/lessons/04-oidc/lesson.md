# OpenID Connect and JWT validation

You have configured OIDC apps in Okta or Entra ID. This lesson is the mechanism underneath the settings: what the app receives, what it must check before it believes it, and what breaks when it does not. Facts checked 2026-10-06 against OpenID Connect Core 1.0, Discovery 1.0, the RP-Initiated, Front-Channel and Back-Channel Logout specs, RFC 7519, RFC 7515, RFC 8725 and RFC 9700, plus Okta and Microsoft docs for the product claims.

## What OIDC adds to OAuth

OIDC is an identity layer on top of OAuth 2.0. An app opts in by sending the `openid` scope; without it the behaviour is unspecified. Three artifacts come back, and they are not interchangeable:

- **ID token**: a signed JWT (a JWS) about the authentication, addressed to the client: `aud` contains your `client_id`.
- **Access token**: permission issued to the client, usually opaque to it (RFC 6749 section 1.4).
- **UserInfo**: the OP's endpoint, called with the access token as a Bearer token, returning claims such as `email`.

> Never treat "we hold a valid access token" as proof of login. Core section 1 says OAuth alone cannot provide information about the authentication of the user. Core section 16.11 describes token substitution, where an attacker copies a token from one session into another; the ID token's `iss`, `sub`, `aud` and hashes let the client detect it, which an opaque access token does not.

Standard scopes request claim groups: `profile` (name, `preferred_username`, `picture` and others), `email` (`email`, `email_verified`), `address`, `phone`, and `offline_access` for a refresh token. An OP may return fewer claims than requested, and that is not an error. Scope-requested claims may arrive in the ID token or only at UserInfo, depending on the OP and the response type, so check both.

## The code flow, step by step

<!-- diagram:oidc-code-flow -->
<div style="position:relative;margin:20px 0">
<input type="checkbox" id="oi-pause" class="oi-cb" /><label for="oi-pause" class="oi-btn"><span class="oi-off">Pause animation</span><span class="oi-on">Play animation</span></label>
<div class="oi-box" style="overflow-x:auto">
<svg class="oi-flow" viewBox="0 0 760 728" role="img" aria-labelledby="oi-t oi-d" style="width:100%;min-width:640px;max-width:800px;height:auto;display:block;margin:0 auto">
<title id="oi-t">OpenID Connect authorization code flow, ending in ID token validation</title>
<desc id="oi-d">Two parties: the app, which is the client, and the OP. Step 1: the app redirects the browser to the authorization endpoint with scope openid, a state, an optional nonce and, for a public client, a PKCE code_challenge with method S256. The user signs in at the OP. Step 2: the OP redirects to the redirect_uri with a code and the state, and the app verifies state first. Step 3: the app posts the code to the token endpoint, server to server, with client authentication if it is a confidential client or the PKCE code_verifier if it is a public client, and receives an id_token and an access_token with Cache-Control no-store. Step 4: the app validates the ID token, then starts its own session. Step 5, optional: the app calls UserInfo with the access token as a Bearer token, and the sub must equal the ID token's sub or the response is not used. The diagram highlights each step in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
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
.oi-g5{animation-name:oi-g5}
</style>
<defs>
<marker id="oi-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="oi-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="oi-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<line class="oi-life" x1="110" y1="72" x2="110" y2="676"/>
<line class="oi-life" x1="650" y1="72" x2="650" y2="676"/>
<rect class="oi-hot" x="20" y="10" width="180" height="62" rx="10"/><text class="oi-ttl" x="110" y="36">App (the client)</text><text class="oi-sub" x="110" y="56">has a client_id</text>
<rect class="oi-box" x="560" y="10" width="180" height="62" rx="10"/><text class="oi-ttl" x="650" y="36">OP</text><text class="oi-sub" x="650" y="56">the issuer: Okta, Entra ID</text>
<g class="oi-g oi-g0">
<text class="oi-main" x="380" y="108">redirect to the authorization endpoint</text>
<text class="oi-dim" x="380" y="124">scope=openid, state, optional nonce</text>
<text class="oi-dim" x="380" y="140">public client adds code_challenge (S256)</text>
<line class="oi-front" x1="124" y1="154" x2="636" y2="154" marker-end="url(#oi-m-front)"/>
<circle class="oi-badge oi-b-front" cx="110" cy="154" r="12"/><text class="oi-bt" x="110" y="158.5">1</text>
</g>
<g class="oi-g oi-g1">
<rect class="oi-note" x="560" y="188" width="181" height="31" rx="8"/>
<text class="oi-nt" x="650" y="209">user signs in at the OP</text>
</g>
<g class="oi-g oi-g2">
<text class="oi-main" x="380" y="253">redirect to redirect_uri</text>
<text class="oi-dim" x="380" y="269">code and state (verify state first)</text>
<line class="oi-front" x1="636" y1="283" x2="124" y2="283" marker-end="url(#oi-m-front)"/>
<circle class="oi-badge oi-b-front" cx="650" cy="283" r="12"/><text class="oi-bt" x="650" y="287.5">2</text>
</g>
<g class="oi-g oi-g3">
<text class="oi-main" x="380" y="323">POST to the token endpoint</text>
<text class="oi-dim" x="380" y="339">code, plus code_verifier (public client)</text>
<text class="oi-dim" x="380" y="355">or client authentication (confidential)</text>
<line class="oi-back" x1="124" y1="369" x2="636" y2="369" marker-end="url(#oi-m-back)"/>
<circle class="oi-badge oi-b-back" cx="110" cy="369" r="12"/><text class="oi-bt" x="110" y="373.5">3</text>
<text class="oi-main" x="380" y="409">token response</text>
<text class="oi-dim" x="380" y="425">id_token and access_token</text>
<text class="oi-dim" x="380" y="441">Cache-Control: no-store</text>
<line class="oi-back" x1="636" y1="455" x2="124" y2="455" marker-end="url(#oi-m-back)"/>
</g>
<g class="oi-g oi-g4">
<rect class="oi-note-good" x="10" y="489" width="241" height="48" rx="8"/>
<text class="oi-nt" x="130" y="510">validate the ID token,</text>
<text class="oi-nt" x="130" y="527">then start the app's own session</text>
<circle class="oi-badge oi-b-good" cx="10" cy="513" r="12"/><text class="oi-bt" x="10" y="517.5">4</text>
</g>
<g class="oi-g oi-g5">
<rect class="oi-note" x="10" y="565" width="346" height="65" rx="8"/>
<text class="oi-nt" x="183" y="586">optional: call UserInfo, access token as Bearer;</text>
<text class="oi-nt" x="183" y="603">sub must equal the ID token's sub,</text>
<text class="oi-nt" x="183" y="620">or discard</text>
<circle class="oi-badge oi-b-plain" cx="10" cy="598" r="12"/><text class="oi-bt" x="10" y="602.0">5</text>
</g>
<circle class="oi-pk oi-p0" cx="130" cy="154" r="5.5"/>
<circle class="oi-pk oi-p2" cx="630" cy="283" r="5.5"/>
<circle class="oi-pk oi-p3 oi-pkback" cx="630" cy="455" r="5.5"/>
<line class="oi-front" x1="40" y1="704" x2="70" y2="704"/>
<text class="oi-dim" x="78" y="708" style="text-anchor:start">through the user's browser</text>
<line class="oi-back" x1="278" y1="704" x2="308" y2="704"/>
<text class="oi-dim" x="316" y="708" style="text-anchor:start">server to server</text>
<rect class="oi-note-good" x="452" y="696" width="22" height="16" rx="4"/>
<text class="oi-dim" x="482" y="708" style="text-anchor:start">what your app must do</text>
</svg>
</div>
</div>
<!-- /diagram:oidc-code-flow -->

Steps 1 and 2 pass through the browser, step 3 is server to server, and step 4 is the check your app must do itself. Step 5 is optional.

The numbers in the diagram match the numbered steps that follow.

1. The app redirects the browser to the OP's authorization endpoint (from discovery) with `response_type=code`, `client_id`, `redirect_uri`, `scope=openid ...`, `state`, and a `nonce`. The `redirect_uri` must exactly match a pre-registered value. `state` is recommended by OIDC and ties the callback to the browser (CSRF); RFC 9700 requires some CSRF protection here, a one-time `state` or PKCE where you know the OP supports it (lesson 3). `nonce` is optional in the code flow and binds the ID token to this client session. A public client (SPA, native app) must also send `code_challenge` and `code_challenge_method=S256` (PKCE, lesson 3). RFC 9700 section 2.1.1 recommends PKCE for confidential clients too, and lets a confidential OIDC client use `nonce` instead only with extra precautions.
2. After sign-in the OP redirects back with `code` and `state`. Verify `state` first.
3. The app posts the code to the token endpoint, server to server. A confidential client authenticates itself; a public client sends the PKCE `code_verifier` instead (lesson 3). The response carries `id_token` and `access_token` and must send `Cache-Control: no-store`.
4. The app validates the ID token, then starts its own session.
5. Optionally it calls UserInfo. The UserInfo `sub` must exactly match the ID token's `sub`, or the response must not be used.

**Implicit is legacy; hybrid needs care.** Implicit (`id_token`, `id_token token`) returns tokens in the authorization response, never touching the token endpoint, which can expose them to the user and to anything with access to the user agent. Implicit requires `nonce`. RFC 9700 section 2.1.2 says clients SHOULD NOT use response types that issue access tokens in the authorization response, and names `code id_token` as an acceptable alternative. Hybrid `code id_token` is not deprecated, but the ID token still crosses the front channel. If an app registration says implicit, ask why.

## Validating the ID token

Do these in order, and trust no claim until the signature has passed (Core lets TLS validation replace the signature check only for an ID token received directly from the token endpoint; any other ID token needs the signature check). RFC 7519 section 7.2 says step order does not matter where steps have no dependencies, so the order below is a teaching order, not a spec order.

<!-- diagram:oidc-validation-order -->
<div style="position:relative;margin:20px 0">
<input type="checkbox" id="l04d-pause" class="l04d-cb" /><label for="l04d-pause" class="l04d-btn"><span class="l04d-off">Pause animation</span><span class="l04d-on">Play animation</span></label>
<div class="l04d-box" style="overflow-x:auto">
<svg class="l04d-flow" viewBox="0 0 874 730" role="img" aria-labelledby="l04d-t l04d-d" style="width:100%;min-width:640px;max-width:800px;height:auto;display:block;margin:0 auto">
<title id="l04d-t">Validating an ID token in teaching order</title>
<desc id="l04d-d">A chain of checks, each with one way out. First the algorithm must be one you configured and the signature must be valid; if not, reject and trust no claim. Then iss must equal the configured issuer. Then aud must contain your client_id and no audience you distrust; otherwise it is rejected as another app or an untrusted audience. Then the current time must be before exp, with a small leeway. Then, if you sent a nonce, it must be present and equal; otherwise it is rejected as a nonce mismatch. A token that passes all of these is accepted, optionally checking acr and auth_time. The diagram highlights each path in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
<style>
.l04d-box{fill:var(--panel);stroke:var(--border-strong);stroke-width:1.5}
.l04d-hot{fill:var(--panel);stroke:var(--accent);stroke-width:2.5}
.l04d-ttl{fill:var(--text);font:600 15px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l04d-sub{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l04d-life{stroke:var(--border-strong);stroke-width:1.5;stroke-dasharray:4 5}
.l04d-front{stroke:var(--accent);stroke-width:2;fill:none}
.l04d-back{stroke:var(--muted);stroke-width:2;stroke-dasharray:7 5;fill:none}
.l04d-bad{stroke:var(--bad);stroke-width:2;fill:none}
.l04d-main{fill:var(--text);font:600 13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l04d-badt{fill:var(--bad-text)}
.l04d-dim{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l04d-badge{fill:var(--accent)}
.l04d-b-back{fill:var(--muted)}
.l04d-b-bad{fill:var(--bad)}
.l04d-b-good{fill:var(--good)}
.l04d-bt{fill:var(--on-accent);font:700 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l04d-note{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l04d-note-good{fill:var(--good-bg);stroke:var(--good);stroke-width:1.5}
.l04d-note-bad{fill:var(--bad-bg);stroke:var(--bad);stroke-width:1.5}
.l04d-nt{fill:var(--body);font:12.5px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l04d-nest{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l04d-row{fill:var(--raised);stroke:var(--border-strong);stroke-width:1}
.l04d-ttlL{fill:var(--text);font:600 14px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l04d-subL{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l04d-dimL{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l04d-dimR{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:end}
.l04d-conn{stroke:var(--accent);stroke-width:1.5;fill:none}
.l04d-edge{stroke:var(--border-strong);stroke-width:1.75;fill:none}
.l04d-hl{fill:none;stroke:var(--accent);stroke-width:3}
.l04d-hle{stroke:var(--accent);stroke-width:3;fill:none}
.l04d-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:22s;animation-timing-function:linear;animation-iteration-count:infinite}
.l04d-pk.l04d-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.l04d-pk.l04d-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.l04d-g{opacity:.45;animation-duration:22s;animation-timing-function:linear;animation-iteration-count:infinite}
.l04d-h{opacity:0;animation-duration:22s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.l04d-flow:hover .l04d-g,svg.l04d-flow:hover .l04d-pk,svg.l04d-flow:hover .l04d-h{animation-play-state:paused}
.l04d-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.l04d-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.l04d-btn:hover{background:var(--hover)}
.l04d-cb:focus-visible + .l04d-btn{outline:2px solid var(--accent);outline-offset:2px}
.l04d-cb:checked + .l04d-btn .l04d-off,.l04d-cb:not(:checked) + .l04d-btn .l04d-on{display:none}
.l04d-cb:checked ~ .l04d-box .l04d-g,.l04d-cb:checked ~ .l04d-box .l04d-pk,.l04d-cb:checked ~ .l04d-box .l04d-h{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.l04d-g{animation:none;opacity:1}.l04d-pk{animation:none;display:none}.l04d-h{animation:none;opacity:0}.l04d-btn{display:none}}
@keyframes l04d-h0{0%{opacity:1}16.667%{opacity:1}16.677%,100%{opacity:0}}
.l04d-h0{animation-name:l04d-h0}
@keyframes l04d-h1{0%,16.657%{opacity:0}16.667%{opacity:1}33.333%{opacity:1}33.343%,100%{opacity:0}}
.l04d-h1{animation-name:l04d-h1}
@keyframes l04d-h2{0%,33.323%{opacity:0}33.333%{opacity:1}50%{opacity:1}50.01%,100%{opacity:0}}
.l04d-h2{animation-name:l04d-h2}
@keyframes l04d-h3{0%,49.99%{opacity:0}50%{opacity:1}66.667%{opacity:1}66.677%,100%{opacity:0}}
.l04d-h3{animation-name:l04d-h3}
@keyframes l04d-h4{0%,66.657%{opacity:0}66.667%{opacity:1}83.333%{opacity:1}83.343%,100%{opacity:0}}
.l04d-h4{animation-name:l04d-h4}
@keyframes l04d-h5{0%,83.323%{opacity:0}83.333%{opacity:1}100%{opacity:1}100.01%,100%{opacity:0}}
.l04d-h5{animation-name:l04d-h5}
</style>
<defs>
<marker id="l04d-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="l04d-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="l04d-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<path class="l04d-edge" d="M437,89 L437,118 L71,118 L71,144" marker-end="url(#l04d-m-front)"/>
<text class="l04d-dimL" x="78" y="134">no</text>
<path class="l04d-edge" d="M437,89 L437,118 L502,118 L502,144" marker-end="url(#l04d-m-front)"/>
<text class="l04d-dimL" x="509" y="134">yes</text>
<path class="l04d-edge" d="M502,212 L502,241 L201,241 L201,267" marker-end="url(#l04d-m-front)"/>
<text class="l04d-dimL" x="208" y="257">no</text>
<path class="l04d-edge" d="M502,212 L502,241 L567,241 L567,267" marker-end="url(#l04d-m-front)"/>
<text class="l04d-dimL" x="574" y="257">yes</text>
<path class="l04d-edge" d="M567,335 L567,364 L341,364 L341,390" marker-end="url(#l04d-m-front)"/>
<text class="l04d-dimL" x="348" y="380">no</text>
<path class="l04d-edge" d="M567,335 L567,364 L642,364 L642,390" marker-end="url(#l04d-m-front)"/>
<text class="l04d-dimL" x="649" y="380">yes</text>
<path class="l04d-edge" d="M642,441 L642,470 L488,470 L488,513" marker-end="url(#l04d-m-front)"/>
<text class="l04d-dimL" x="495" y="503">no</text>
<path class="l04d-edge" d="M642,441 L642,470 L714,470 L714,513" marker-end="url(#l04d-m-front)"/>
<text class="l04d-dimL" x="721" y="503">yes</text>
<path class="l04d-edge" d="M714,564 L714,593 L625,593 L625,619" marker-end="url(#l04d-m-front)"/>
<text class="l04d-dimL" x="632" y="609">no</text>
<path class="l04d-edge" d="M714,564 L714,593 L779,593 L779,619" marker-end="url(#l04d-m-front)"/>
<text class="l04d-dimL" x="786" y="609">yes</text>
<rect class="l04d-note-bad" x="14" y="147" width="114" height="48" rx="8"/><text class="l04d-nt" x="71" y="168">Reject: trust</text><text class="l04d-nt" x="71" y="185">no claim</text>
<rect class="l04d-note-bad" x="144" y="270" width="114" height="48" rx="8"/><text class="l04d-nt" x="201" y="291">Reject: wrong</text><text class="l04d-nt" x="201" y="308">issuer</text>
<rect class="l04d-note-bad" x="274" y="393" width="134" height="65" rx="8"/><text class="l04d-nt" x="341" y="414">Reject: another</text><text class="l04d-nt" x="341" y="431">app or untrusted</text><text class="l04d-nt" x="341" y="448">audience</text>
<rect class="l04d-note-bad" x="424" y="516" width="128" height="31" rx="8"/><text class="l04d-nt" x="488" y="537">Reject: expired</text>
<rect class="l04d-note-bad" x="568" y="622" width="114" height="48" rx="8"/><text class="l04d-nt" x="625" y="643">Reject: nonce</text><text class="l04d-nt" x="625" y="660">mismatch</text>
<rect class="l04d-note-good" x="698" y="622" width="162" height="48" rx="8"/><text class="l04d-nt" x="779" y="643">Accept; optionally</text><text class="l04d-nt" x="779" y="660">check acr, auth_time</text>
<rect class="l04d-box" x="623" y="516" width="182" height="48" rx="8"/><text class="l04d-main" x="714" y="537">nonce: if you sent</text><text class="l04d-nt" x="714" y="554">one, present and equal?</text>
<rect class="l04d-box" x="578" y="393" width="128" height="48" rx="8"/><text class="l04d-main" x="642" y="414">now before exp</text><text class="l04d-nt" x="642" y="431">(small leeway)?</text>
<rect class="l04d-box" x="490" y="270" width="155" height="65" rx="8"/><text class="l04d-main" x="567" y="291">aud has your</text><text class="l04d-nt" x="567" y="308">client_id and no</text><text class="l04d-nt" x="567" y="325">untrusted audience?</text>
<rect class="l04d-box" x="432" y="147" width="141" height="65" rx="8"/><text class="l04d-main" x="502" y="168">iss exactly equal</text><text class="l04d-nt" x="502" y="185">to the configured</text><text class="l04d-nt" x="502" y="202">issuer?</text>
<rect class="l04d-box" x="360" y="24" width="155" height="65" rx="8"/><text class="l04d-main" x="437" y="45">ID token arrives:</text><text class="l04d-nt" x="437" y="62">alg you configured,</text><text class="l04d-nt" x="437" y="79">signature valid?</text>
<g class="l04d-h l04d-h0">
<path class="l04d-hle" d="M437,89 L437,118 L71,118 L71,144" marker-end="url(#l04d-m-front)"/>
<rect class="l04d-hl" x="360" y="24" width="155" height="65" rx="8"/>
<rect class="l04d-hl" x="14" y="147" width="114" height="48" rx="8"/>
</g>
<g class="l04d-h l04d-h1">
<path class="l04d-hle" d="M437,89 L437,118 L502,118 L502,144" marker-end="url(#l04d-m-front)"/>
<path class="l04d-hle" d="M502,212 L502,241 L201,241 L201,267" marker-end="url(#l04d-m-front)"/>
<rect class="l04d-hl" x="360" y="24" width="155" height="65" rx="8"/>
<rect class="l04d-hl" x="432" y="147" width="141" height="65" rx="8"/>
<rect class="l04d-hl" x="144" y="270" width="114" height="48" rx="8"/>
</g>
<g class="l04d-h l04d-h2">
<path class="l04d-hle" d="M437,89 L437,118 L502,118 L502,144" marker-end="url(#l04d-m-front)"/>
<path class="l04d-hle" d="M502,212 L502,241 L567,241 L567,267" marker-end="url(#l04d-m-front)"/>
<path class="l04d-hle" d="M567,335 L567,364 L341,364 L341,390" marker-end="url(#l04d-m-front)"/>
<rect class="l04d-hl" x="360" y="24" width="155" height="65" rx="8"/>
<rect class="l04d-hl" x="432" y="147" width="141" height="65" rx="8"/>
<rect class="l04d-hl" x="490" y="270" width="155" height="65" rx="8"/>
<rect class="l04d-hl" x="274" y="393" width="134" height="65" rx="8"/>
</g>
<g class="l04d-h l04d-h3">
<path class="l04d-hle" d="M437,89 L437,118 L502,118 L502,144" marker-end="url(#l04d-m-front)"/>
<path class="l04d-hle" d="M502,212 L502,241 L567,241 L567,267" marker-end="url(#l04d-m-front)"/>
<path class="l04d-hle" d="M567,335 L567,364 L642,364 L642,390" marker-end="url(#l04d-m-front)"/>
<path class="l04d-hle" d="M642,441 L642,470 L488,470 L488,513" marker-end="url(#l04d-m-front)"/>
<rect class="l04d-hl" x="360" y="24" width="155" height="65" rx="8"/>
<rect class="l04d-hl" x="432" y="147" width="141" height="65" rx="8"/>
<rect class="l04d-hl" x="490" y="270" width="155" height="65" rx="8"/>
<rect class="l04d-hl" x="578" y="393" width="128" height="48" rx="8"/>
<rect class="l04d-hl" x="424" y="516" width="128" height="31" rx="8"/>
</g>
<g class="l04d-h l04d-h4">
<path class="l04d-hle" d="M437,89 L437,118 L502,118 L502,144" marker-end="url(#l04d-m-front)"/>
<path class="l04d-hle" d="M502,212 L502,241 L567,241 L567,267" marker-end="url(#l04d-m-front)"/>
<path class="l04d-hle" d="M567,335 L567,364 L642,364 L642,390" marker-end="url(#l04d-m-front)"/>
<path class="l04d-hle" d="M642,441 L642,470 L714,470 L714,513" marker-end="url(#l04d-m-front)"/>
<path class="l04d-hle" d="M714,564 L714,593 L625,593 L625,619" marker-end="url(#l04d-m-front)"/>
<rect class="l04d-hl" x="360" y="24" width="155" height="65" rx="8"/>
<rect class="l04d-hl" x="432" y="147" width="141" height="65" rx="8"/>
<rect class="l04d-hl" x="490" y="270" width="155" height="65" rx="8"/>
<rect class="l04d-hl" x="578" y="393" width="128" height="48" rx="8"/>
<rect class="l04d-hl" x="623" y="516" width="182" height="48" rx="8"/>
<rect class="l04d-hl" x="568" y="622" width="114" height="48" rx="8"/>
</g>
<g class="l04d-h l04d-h5">
<path class="l04d-hle" d="M437,89 L437,118 L502,118 L502,144" marker-end="url(#l04d-m-front)"/>
<path class="l04d-hle" d="M502,212 L502,241 L567,241 L567,267" marker-end="url(#l04d-m-front)"/>
<path class="l04d-hle" d="M567,335 L567,364 L642,364 L642,390" marker-end="url(#l04d-m-front)"/>
<path class="l04d-hle" d="M642,441 L642,470 L714,470 L714,513" marker-end="url(#l04d-m-front)"/>
<path class="l04d-hle" d="M714,564 L714,593 L779,593 L779,619" marker-end="url(#l04d-m-front)"/>
<rect class="l04d-hl" x="360" y="24" width="155" height="65" rx="8"/>
<rect class="l04d-hl" x="432" y="147" width="141" height="65" rx="8"/>
<rect class="l04d-hl" x="490" y="270" width="155" height="65" rx="8"/>
<rect class="l04d-hl" x="578" y="393" width="128" height="48" rx="8"/>
<rect class="l04d-hl" x="623" y="516" width="182" height="48" rx="8"/>
<rect class="l04d-hl" x="698" y="622" width="162" height="48" rx="8"/>
</g>
<line class="l04d-front" x1="40" y1="706" x2="70" y2="706"/>
<text class="l04d-dim" x="78" y="710" style="text-anchor:start">the path being traced</text>
<rect class="l04d-note-good" x="246" y="698" width="22" height="16" rx="4"/>
<text class="l04d-dim" x="276" y="710" style="text-anchor:start">accept</text>
<rect class="l04d-note-bad" x="348" y="698" width="22" height="16" rx="4"/>
<text class="l04d-dim" x="378" y="710" style="text-anchor:start">reject</text>
</svg>
</div>
</div>
<!-- /diagram:oidc-validation-order -->

Walk each path from the top: every check has one way out, and the single accepting path is a token that passes them all. As the text says, the order is a teaching order, not a spec order. The list below gives the detail for each check.

1. **Algorithm**: accept only the algorithm(s) you configured, never whatever the header says. `alg: none` and an RS256 token relabelled HS256 and checked with the public key as the HMAC secret are the classic forgeries (RFC 8725 sections 2.1 and 3.1).
2. **Signature**, using a key from the issuer's JWKS selected by `kid`.
3. **`iss`**: exactly equal to the configured issuer.
4. **`aud`**: contains your `client_id`. One OP, with one issuer, signs tokens for many apps, so `iss` cannot tell them apart. Reject if it lists audiences you do not trust. In the code flow the token comes from your own token-endpoint call, so a wrong `aud` is rare; the check bites when a token reaches you another way (implicit or hybrid, or an ID token forwarded to a backend). ID tokens are addressed to the client, so APIs must not accept them as access tokens (cross-JWT confusion, RFC 8725 section 2.8).
5. **`exp`** (and `iat`): current time must be before `exp`. A small leeway for clock skew is allowed (Core and RFC 7519 say usually no more than a few minutes). `exp` is the token's life, unrelated to the session at the OP.
6. **`nonce`**: if you sent one, the claim must be present and equal; replay detection is up to you.
7. Optionally `acr` and `auth_time`, if you asked for them.

Failure modes: a missing `aud` check accepts a token minted for another app of the same OP wherever tokens can reach you from outside your own token call; a missing `iss` check matters most once you trust more than one issuer; accepting "any key in the JWKS" without matching `kid` and algorithm; skewed clocks produce intermittent "expired" errors on one server; and ID tokens delivered in front-channel responses, which implicit and hybrid flows do.

## Keys, discovery and rotation

`<issuer>/.well-known/openid-configuration` returns the OP's metadata, including `jwks_uri`, `authorization_endpoint`, `token_endpoint` and `userinfo_endpoint`. The metadata `issuer` must be identical to the issuer URL you fetched it from and to the `iss` in ID tokens.

Core section 10.1.1 describes rotation: the OP adds a new key to the JWKS and starts signing with it, signalling the change through `kid`. The verifier goes back to `jwks_uri` when it sees an unfamiliar `kid`, and the OP SHOULD keep recently retired keys published for a while. Okta documents caching the `jwks_uri` response per its Cache-Control headers, says its rotation schedule is currently four times a year and can change without notice, and warns that apps that hardcode keys might fail. A stale cache after rotation shows up as "invalid signature" for every new login.

<!-- diagram:oidc-key-rotation -->
<div style="position:relative;margin:20px 0">
<input type="checkbox" id="l04e-pause" class="l04e-cb" /><label for="l04e-pause" class="l04e-btn"><span class="l04e-off">Pause animation</span><span class="l04e-on">Play animation</span></label>
<div class="l04e-box" style="overflow-x:auto">
<svg class="l04e-flow" viewBox="0 0 760 227" role="img" aria-labelledby="l04e-t l04e-d" style="width:100%;min-width:640px;max-width:800px;height:auto;display:block;margin:0 auto">
<title id="l04e-t">A signing key rotates and the verifier's cache catches up</title>
<desc id="l04e-d">Four stages. First, before rotation, the OP signs with the old key, the JWKS holds the old key and the verifier's cache holds the old key. Then the OP adds a new key to the JWKS and starts signing with it, while the verifier's cache still holds only the old key; a stale cache fails with invalid signature. When the verifier sees an unfamiliar kid it goes back to jwks_uri, and its cache then holds both keys. Later the old key is retired; the OP SHOULD keep recently retired keys published for a while. The diagram highlights each stage in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
<style>
.l04e-box{fill:var(--panel);stroke:var(--border-strong);stroke-width:1.5}
.l04e-hot{fill:var(--panel);stroke:var(--accent);stroke-width:2.5}
.l04e-ttl{fill:var(--text);font:600 15px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l04e-sub{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l04e-life{stroke:var(--border-strong);stroke-width:1.5;stroke-dasharray:4 5}
.l04e-front{stroke:var(--accent);stroke-width:2;fill:none}
.l04e-back{stroke:var(--muted);stroke-width:2;stroke-dasharray:7 5;fill:none}
.l04e-bad{stroke:var(--bad);stroke-width:2;fill:none}
.l04e-main{fill:var(--text);font:600 13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l04e-badt{fill:var(--bad-text)}
.l04e-dim{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l04e-badge{fill:var(--accent)}
.l04e-b-back{fill:var(--muted)}
.l04e-b-bad{fill:var(--bad)}
.l04e-b-good{fill:var(--good)}
.l04e-bt{fill:var(--on-accent);font:700 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l04e-note{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l04e-note-good{fill:var(--good-bg);stroke:var(--good);stroke-width:1.5}
.l04e-note-bad{fill:var(--bad-bg);stroke:var(--bad);stroke-width:1.5}
.l04e-nt{fill:var(--body);font:12.5px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l04e-nest{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l04e-row{fill:var(--raised);stroke:var(--border-strong);stroke-width:1}
.l04e-ttlL{fill:var(--text);font:600 14px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l04e-subL{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l04e-dimL{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l04e-dimR{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:end}
.l04e-conn{stroke:var(--accent);stroke-width:1.5;fill:none}
.l04e-edge{stroke:var(--border-strong);stroke-width:1.75;fill:none}
.l04e-hl{fill:none;stroke:var(--accent);stroke-width:3}
.l04e-hle{stroke:var(--accent);stroke-width:3;fill:none}
.l04e-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:16s;animation-timing-function:linear;animation-iteration-count:infinite}
.l04e-pk.l04e-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.l04e-pk.l04e-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.l04e-g{opacity:.45;animation-duration:16s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.l04e-flow:hover .l04e-g,svg.l04e-flow:hover .l04e-pk{animation-play-state:paused}
.l04e-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.l04e-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.l04e-btn:hover{background:var(--hover)}
.l04e-cb:focus-visible + .l04e-btn{outline:2px solid var(--accent);outline-offset:2px}
.l04e-cb:checked + .l04e-btn .l04e-off,.l04e-cb:not(:checked) + .l04e-btn .l04e-on{display:none}
.l04e-cb:checked ~ .l04e-box .l04e-g,.l04e-cb:checked ~ .l04e-box .l04e-pk{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.l04e-g{animation:none;opacity:1}.l04e-pk{animation:none;display:none}.l04e-btn{display:none}}
@keyframes l04e-g0{0%{opacity:1}25%{opacity:1}25.01%,100%{opacity:.45}}
@keyframes l04e-p0{0%,-0.01%{opacity:0;transform:translateX(0)}0%{opacity:1;transform:translateX(0)}25%{opacity:1;transform:translateX(58px)}25.01%,100%{opacity:0;transform:translateX(58px)}}
.l04e-g0{animation-name:l04e-g0}.l04e-p0{animation-name:l04e-p0}
@keyframes l04e-g1{0%,24.99%{opacity:.45}25%{opacity:1}50%{opacity:1}50.01%,100%{opacity:.45}}
@keyframes l04e-p1{0%,24.99%{opacity:0;transform:translateX(0)}25%{opacity:1;transform:translateX(0)}50%{opacity:1;transform:translateX(58px)}50.01%,100%{opacity:0;transform:translateX(58px)}}
.l04e-g1{animation-name:l04e-g1}.l04e-p1{animation-name:l04e-p1}
@keyframes l04e-g2{0%,49.99%{opacity:.45}50%{opacity:1}75%{opacity:1}75.01%,100%{opacity:.45}}
@keyframes l04e-p2{0%,49.99%{opacity:0;transform:translateX(0)}50%{opacity:1;transform:translateX(0)}75%{opacity:1;transform:translateX(58px)}75.01%,100%{opacity:0;transform:translateX(58px)}}
.l04e-g2{animation-name:l04e-g2}.l04e-p2{animation-name:l04e-p2}
@keyframes l04e-g3{0%,74.99%{opacity:.45}75%{opacity:1}100%{opacity:1}100.01%,100%{opacity:.45}}
.l04e-g3{animation-name:l04e-g3}
</style>
<defs>
<marker id="l04e-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="l04e-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="l04e-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<g class="l04e-g l04e-g0">
<rect class="l04e-box" x="14" y="40" width="123" height="127" rx="10"/>
<text class="l04e-ttl" x="76" y="67">Before</text>
<text class="l04e-sub" x="76" y="87">before rotation</text>
<text class="l04e-nt" x="76" y="114">OP signs: old key</text>
<text class="l04e-nt" x="76" y="131">JWKS: old key</text>
<text class="l04e-nt" x="76" y="148">cache: old key</text>
<text class="l04e-main" x="177" y="48">OP adds</text>
<text class="l04e-dim" x="177" y="64">new key</text>
<line class="l04e-front" x1="145" y1="70" x2="209" y2="70" marker-end="url(#l04e-m-front)"/>
</g>
<g class="l04e-g l04e-g1">
<rect class="l04e-note-bad" x="217" y="40" width="123" height="127" rx="10"/>
<text class="l04e-ttl" x="278" y="67">New key added</text>
<text class="l04e-sub" x="278" y="87">stale cache fails</text>
<text class="l04e-nt" x="278" y="114">OP signs: new key</text>
<text class="l04e-nt" x="278" y="131">JWKS: both keys</text>
<text class="l04e-nt" x="278" y="148">cache: old key</text>
<text class="l04e-main" x="380" y="32">unfamiliar</text>
<text class="l04e-dim" x="380" y="48">kid, so</text>
<text class="l04e-dim" x="380" y="64">refetch</text>
<line class="l04e-front" x1="348" y1="70" x2="412" y2="70" marker-end="url(#l04e-m-front)"/>
</g>
<g class="l04e-g l04e-g2">
<rect class="l04e-note-good" x="420" y="40" width="123" height="127" rx="10"/>
<text class="l04e-ttl" x="482" y="67">Refetched</text>
<text class="l04e-sub" x="482" y="87">unfamiliar kid</text>
<text class="l04e-nt" x="482" y="114">OP signs: new key</text>
<text class="l04e-nt" x="482" y="131">JWKS: both keys</text>
<text class="l04e-nt" x="482" y="148">cache: both keys</text>
<text class="l04e-main" x="583" y="48">old key</text>
<text class="l04e-dim" x="583" y="64">retired</text>
<line class="l04e-front" x1="551" y1="70" x2="615" y2="70" marker-end="url(#l04e-m-front)"/>
</g>
<g class="l04e-g l04e-g3">
<rect class="l04e-box" x="623" y="40" width="123" height="127" rx="10"/>
<text class="l04e-ttl" x="684" y="67">Old key retired</text>
<text class="l04e-sub" x="684" y="87">OP SHOULD keep it</text>
<text class="l04e-nt" x="684" y="114">OP signs: new key</text>
<text class="l04e-nt" x="684" y="131">JWKS: old key</text>
<text class="l04e-nt" x="684" y="148">still published</text>
</g>
<circle class="l04e-pk l04e-p0" cx="151" cy="70" r="5.5"/>
<circle class="l04e-pk l04e-p1" cx="354" cy="70" r="5.5"/>
<circle class="l04e-pk l04e-p2" cx="557" cy="70" r="5.5"/>
<line class="l04e-front" x1="40" y1="203" x2="70" y2="203"/>
<text class="l04e-dim" x="78" y="207" style="text-anchor:start">step</text>
<rect class="l04e-note-good" x="137" y="195" width="22" height="16" rx="4"/>
<text class="l04e-dim" x="167" y="207" style="text-anchor:start">cache caught up</text>
<rect class="l04e-note-bad" x="297" y="195" width="22" height="16" rx="4"/>
<text class="l04e-dim" x="327" y="207" style="text-anchor:start">a stale cache fails here</text>
</svg>
</div>
</div>
<!-- /diagram:oidc-key-rotation -->

Read left to right. The second stage is the one where a stale cache fails: new tokens carry a kid the verifier does not know, and refetching from jwks_uri on an unfamiliar kid is what moves it to the third stage.

## Identity claims you can trust

`sub` is locally unique and never reassigned within an issuer; `iss` plus `sub` is the only guaranteed unique identifier (Core section 5.7); in Entra `sub` is pairwise per application, so Microsoft's guidance is `tid` plus `oid` (lesson 1). `email`, `preferred_username` and `name` MUST NOT be used as unique identifiers: an issuer may reuse an email for a different person later. `email_verified: true` means the OP took steps to confirm control of the address at that time; how depends on the arrangement between the parties, so do not link or merge accounts on it without knowing how your OP verifies. Microsoft says the Entra `email` claim is mutable and not guaranteed correct, and must never be used for authorization or to store data per user.

<!-- diagram:oidc-claims-matrix -->
<div style="position:relative;margin:20px 0">
<input type="checkbox" id="l04f-pause" class="l04f-cb" /><label for="l04f-pause" class="l04f-btn"><span class="l04f-off">Pause animation</span><span class="l04f-on">Play animation</span></label>
<div class="l04f-box" style="overflow-x:auto">
<svg class="l04f-flow" viewBox="0 0 760 694" role="img" aria-labelledby="l04f-t l04f-d" style="width:100%;min-width:640px;max-width:800px;height:auto;display:block;margin:0 auto">
<title id="l04f-t">Which identity claims can identify or link a user</title>
<desc id="l04f-d">One column asks whether a claim is safe to identify or link a user by. sub is locally unique and never reassigned, but only within one issuer. iss plus sub is the only guaranteed unique identifier. In Entra, sub is pairwise per application, so Microsoft's guidance is tid plus oid. email must not be used as a unique identifier because an issuer may reuse it for a different person, and Entra says it is mutable. email_verified true means the OP took steps to confirm control at that time, so do not link or merge accounts on it without knowing how. preferred_username and name must not be used as unique identifiers. The diagram highlights each row in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
<style>
.l04f-box{fill:var(--panel);stroke:var(--border-strong);stroke-width:1.5}
.l04f-hot{fill:var(--panel);stroke:var(--accent);stroke-width:2.5}
.l04f-ttl{fill:var(--text);font:600 15px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l04f-sub{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l04f-life{stroke:var(--border-strong);stroke-width:1.5;stroke-dasharray:4 5}
.l04f-front{stroke:var(--accent);stroke-width:2;fill:none}
.l04f-back{stroke:var(--muted);stroke-width:2;stroke-dasharray:7 5;fill:none}
.l04f-bad{stroke:var(--bad);stroke-width:2;fill:none}
.l04f-main{fill:var(--text);font:600 13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l04f-badt{fill:var(--bad-text)}
.l04f-dim{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l04f-badge{fill:var(--accent)}
.l04f-b-back{fill:var(--muted)}
.l04f-b-bad{fill:var(--bad)}
.l04f-b-good{fill:var(--good)}
.l04f-bt{fill:var(--on-accent);font:700 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l04f-note{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l04f-note-good{fill:var(--good-bg);stroke:var(--good);stroke-width:1.5}
.l04f-note-bad{fill:var(--bad-bg);stroke:var(--bad);stroke-width:1.5}
.l04f-nt{fill:var(--body);font:12.5px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l04f-nest{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l04f-row{fill:var(--raised);stroke:var(--border-strong);stroke-width:1}
.l04f-ttlL{fill:var(--text);font:600 14px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l04f-subL{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l04f-dimL{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l04f-dimR{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:end}
.l04f-conn{stroke:var(--accent);stroke-width:1.5;fill:none}
.l04f-edge{stroke:var(--border-strong);stroke-width:1.75;fill:none}
.l04f-hl{fill:none;stroke:var(--accent);stroke-width:3}
.l04f-hle{stroke:var(--accent);stroke-width:3;fill:none}
.l04f-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:20s;animation-timing-function:linear;animation-iteration-count:infinite}
.l04f-pk.l04f-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.l04f-pk.l04f-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.l04f-g{opacity:.45;animation-duration:20s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.l04f-flow:hover .l04f-g,svg.l04f-flow:hover .l04f-pk{animation-play-state:paused}
.l04f-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.l04f-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.l04f-btn:hover{background:var(--hover)}
.l04f-cb:focus-visible + .l04f-btn{outline:2px solid var(--accent);outline-offset:2px}
.l04f-cb:checked + .l04f-btn .l04f-off,.l04f-cb:not(:checked) + .l04f-btn .l04f-on{display:none}
.l04f-cb:checked ~ .l04f-box .l04f-g,.l04f-cb:checked ~ .l04f-box .l04f-pk{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.l04f-g{animation:none;opacity:1}.l04f-pk{animation:none;display:none}.l04f-btn{display:none}}
@keyframes l04f-g0{0%{opacity:1}16.667%{opacity:1}16.677%,100%{opacity:.45}}
.l04f-g0{animation-name:l04f-g0}
@keyframes l04f-g1{0%,16.657%{opacity:.45}16.667%{opacity:1}33.333%{opacity:1}33.343%,100%{opacity:.45}}
.l04f-g1{animation-name:l04f-g1}
@keyframes l04f-g2{0%,33.323%{opacity:.45}33.333%{opacity:1}50%{opacity:1}50.01%,100%{opacity:.45}}
.l04f-g2{animation-name:l04f-g2}
@keyframes l04f-g3{0%,49.99%{opacity:.45}50%{opacity:1}66.667%{opacity:1}66.677%,100%{opacity:.45}}
.l04f-g3{animation-name:l04f-g3}
@keyframes l04f-g4{0%,66.657%{opacity:.45}66.667%{opacity:1}83.333%{opacity:1}83.343%,100%{opacity:.45}}
.l04f-g4{animation-name:l04f-g4}
@keyframes l04f-g5{0%,83.323%{opacity:.45}83.333%{opacity:1}100%{opacity:1}100.01%,100%{opacity:.45}}
.l04f-g5{animation-name:l04f-g5}
</style>
<defs>
<marker id="l04f-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="l04f-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="l04f-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<rect class="l04f-box" x="240" y="10" width="502" height="62" rx="10"/><text class="l04f-ttl" x="491" y="36">Safe to identify or link a user by?</text><text class="l04f-sub" x="491" y="56"></text>
<g class="l04f-g l04f-g0">
<rect class="l04f-row" x="10" y="86" width="740" height="86" rx="8"/>
<text class="l04f-ttlL" x="24" y="112">sub</text>
<text class="l04f-subL" x="24" y="130">within one issuer</text>
<circle cx="491" cy="108" r="10" style="fill:var(--muted)"/><path d="M486.8,108.0 L495.2,108.0" style="fill:none;stroke:var(--on-accent);stroke-width:2;stroke-linecap:round;stroke-linejoin:round"/>
<text class="l04f-nt" x="491" y="134">locally unique and never reassigned,</text>
<text class="l04f-nt" x="491" y="149">but only within one issuer</text>
</g>
<g class="l04f-g l04f-g1">
<rect class="l04f-row" x="10" y="180" width="740" height="86" rx="8"/>
<text class="l04f-ttlL" x="24" y="206">iss + sub</text>
<circle cx="491" cy="202" r="10" style="fill:var(--good)"/><path d="M486.8,202.0 L489.6,205.4 L495.2,198.6" style="fill:none;stroke:var(--on-accent);stroke-width:2;stroke-linecap:round;stroke-linejoin:round"/>
<text class="l04f-nt" x="491" y="228">the only guaranteed unique identifier</text>
<text class="l04f-nt" x="491" y="243">(Core section 5.7)</text>
</g>
<g class="l04f-g l04f-g2">
<rect class="l04f-row" x="10" y="274" width="740" height="86" rx="8"/>
<text class="l04f-ttlL" x="24" y="300">sub in Entra</text>
<text class="l04f-subL" x="24" y="318">pairwise per application</text>
<circle cx="491" cy="296" r="10" style="fill:var(--muted)"/><path d="M486.8,296.0 L495.2,296.0" style="fill:none;stroke:var(--on-accent);stroke-width:2;stroke-linecap:round;stroke-linejoin:round"/>
<text class="l04f-nt" x="491" y="322">differs per application, so Microsoft's</text>
<text class="l04f-nt" x="491" y="337">guidance is tid plus oid</text>
</g>
<g class="l04f-g l04f-g3">
<rect class="l04f-row" x="10" y="368" width="740" height="86" rx="8"/>
<text class="l04f-ttlL" x="24" y="394">email</text>
<circle cx="491" cy="390" r="10" style="fill:var(--bad)"/><path d="M487.6,386.6 L494.4,393.4 M494.4,386.6 L487.6,393.4" style="fill:none;stroke:var(--on-accent);stroke-width:2;stroke-linecap:round;stroke-linejoin:round"/>
<text class="l04f-nt" x="491" y="416">MUST NOT: an issuer may reuse it for a</text>
<text class="l04f-nt" x="491" y="431">different person later; in Entra it is mutable</text>
</g>
<g class="l04f-g l04f-g4">
<rect class="l04f-row" x="10" y="462" width="740" height="101" rx="8"/>
<text class="l04f-ttlL" x="24" y="488">email_verified: true</text>
<circle cx="491" cy="484" r="10" style="fill:var(--muted)"/><path d="M486.8,484.0 L495.2,484.0" style="fill:none;stroke:var(--on-accent);stroke-width:2;stroke-linecap:round;stroke-linejoin:round"/>
<text class="l04f-nt" x="491" y="510">the OP took steps to confirm control at that</text>
<text class="l04f-nt" x="491" y="525">time; do not link or merge accounts on it</text>
<text class="l04f-nt" x="491" y="540">without knowing how</text>
</g>
<g class="l04f-g l04f-g5">
<rect class="l04f-row" x="10" y="571" width="740" height="71" rx="8"/>
<text class="l04f-ttlL" x="24" y="597">preferred_username, name</text>
<circle cx="491" cy="593" r="10" style="fill:var(--bad)"/><path d="M487.6,589.6 L494.4,596.4 M494.4,589.6 L487.6,596.4" style="fill:none;stroke:var(--on-accent);stroke-width:2;stroke-linecap:round;stroke-linejoin:round"/>
<text class="l04f-nt" x="491" y="619">MUST NOT be used as unique identifiers</text>
</g>
<circle cx="48" cy="670" r="8" style="fill:var(--good)"/><path d="M44.6,670.0 L46.9,672.7 L51.4,667.3" style="fill:none;stroke:var(--on-accent);stroke-width:2;stroke-linecap:round;stroke-linejoin:round"/>
<text class="l04f-dim" x="64" y="674" style="text-anchor:start">use it</text>
<circle cx="144" cy="670" r="8" style="fill:var(--muted)"/><path d="M140.6,670.0 L147.4,670.0" style="fill:none;stroke:var(--on-accent);stroke-width:2;stroke-linecap:round;stroke-linejoin:round"/>
<text class="l04f-dim" x="160" y="674" style="text-anchor:start">with care</text>
<circle cx="259" cy="670" r="8" style="fill:var(--bad)"/><path d="M256.3,667.3 L261.7,672.7 M261.7,667.3 L256.3,672.7" style="fill:none;stroke:var(--on-accent);stroke-width:2;stroke-linecap:round;stroke-linejoin:round"/>
<text class="l04f-dim" x="275" y="674" style="text-anchor:start">do not</text>
</svg>
</div>
</div>
<!-- /diagram:oidc-claims-matrix -->

Read down the column: iss plus sub is the only guaranteed unique identifier, `sub` alone holds only within one issuer, and the other claims need care or must not be used as a key.

## Logout and OIDC versus SAML

Sign-out is not token revocation. There are three common mechanisms. An ID token already issued stays valid until `exp`, and Core section 16.18 notes access tokens might not be revocable and should be short-lived; back-channel logout does ask the app to revoke refresh tokens issued without `offline_access`.

- **RP-initiated**: the app sends the browser to the OP's `end_session_endpoint` with `id_token_hint` (recommended), a pre-registered `post_logout_redirect_uri` and `state`. It is the app asking the OP to end the OP session, and only when someone signs out; the OP SHOULD ask whether to log out there too. Informing the other apps is the job of front-channel or back-channel logout.
- **Front-channel**: the OP renders each app's registered logout URI in an iframe. Browsers that block third-party content can stop it working, and the spec recommends defensive code to detect that.
- **Back-channel**: the OP POSTs a signed Logout Token straight to the app's registered URI, and the app must end the session named by the token's `sub` or `sid`. It does not depend on the browser, but the endpoint must be reachable from the OP, so it cannot sit behind a firewall or NAT for a public OP. The OP sends it when it logs a session out; whether your OP does so when an admin ends a session or terminates an account is OP-specific (not verified here for Okta or Entra), so test it.

<!-- diagram:oidc-logout-matrix -->
<div style="position:relative;margin:20px 0">
<input type="checkbox" id="l04g-pause" class="l04g-cb" /><label for="l04g-pause" class="l04g-btn"><span class="l04g-off">Pause animation</span><span class="l04g-on">Play animation</span></label>
<div class="l04g-box" style="overflow-x:auto">
<svg class="l04g-flow" viewBox="0 0 760 532" role="img" aria-labelledby="l04g-t l04g-d" style="width:100%;min-width:640px;max-width:800px;height:auto;display:block;margin:0 auto">
<title id="l04g-t">Three logout mechanisms compared</title>
<desc id="l04g-d">Two columns, path and limits, for three mechanisms. RP-initiated logout: the app sends the browser to the OP's end_session_endpoint with id_token_hint, post_logout_redirect_uri and state; it asks the OP to end its session only when someone signs out, the OP should ask whether to log out there too, and informing other apps is left to front-channel or back-channel logout. Front-channel: the OP renders each app's registered logout URI in an iframe, and browsers that block third-party content can stop it. Back-channel: the OP posts a signed Logout Token to the app's registered URI, which does not depend on the browser but must be reachable from the OP; whether an admin action makes the OP send it is OP-specific and not verified. The diagram highlights each row in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
<style>
.l04g-box{fill:var(--panel);stroke:var(--border-strong);stroke-width:1.5}
.l04g-hot{fill:var(--panel);stroke:var(--accent);stroke-width:2.5}
.l04g-ttl{fill:var(--text);font:600 15px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l04g-sub{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l04g-life{stroke:var(--border-strong);stroke-width:1.5;stroke-dasharray:4 5}
.l04g-front{stroke:var(--accent);stroke-width:2;fill:none}
.l04g-back{stroke:var(--muted);stroke-width:2;stroke-dasharray:7 5;fill:none}
.l04g-bad{stroke:var(--bad);stroke-width:2;fill:none}
.l04g-main{fill:var(--text);font:600 13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l04g-badt{fill:var(--bad-text)}
.l04g-dim{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l04g-badge{fill:var(--accent)}
.l04g-b-back{fill:var(--muted)}
.l04g-b-bad{fill:var(--bad)}
.l04g-b-good{fill:var(--good)}
.l04g-bt{fill:var(--on-accent);font:700 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l04g-note{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l04g-note-good{fill:var(--good-bg);stroke:var(--good);stroke-width:1.5}
.l04g-note-bad{fill:var(--bad-bg);stroke:var(--bad);stroke-width:1.5}
.l04g-nt{fill:var(--body);font:12.5px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l04g-nest{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l04g-row{fill:var(--raised);stroke:var(--border-strong);stroke-width:1}
.l04g-ttlL{fill:var(--text);font:600 14px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l04g-subL{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l04g-dimL{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l04g-dimR{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:end}
.l04g-conn{stroke:var(--accent);stroke-width:1.5;fill:none}
.l04g-edge{stroke:var(--border-strong);stroke-width:1.75;fill:none}
.l04g-hl{fill:none;stroke:var(--accent);stroke-width:3}
.l04g-hle{stroke:var(--accent);stroke-width:3;fill:none}
.l04g-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:20s;animation-timing-function:linear;animation-iteration-count:infinite}
.l04g-pk.l04g-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.l04g-pk.l04g-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.l04g-g{opacity:.45;animation-duration:20s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.l04g-flow:hover .l04g-g,svg.l04g-flow:hover .l04g-pk{animation-play-state:paused}
.l04g-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.l04g-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.l04g-btn:hover{background:var(--hover)}
.l04g-cb:focus-visible + .l04g-btn{outline:2px solid var(--accent);outline-offset:2px}
.l04g-cb:checked + .l04g-btn .l04g-off,.l04g-cb:not(:checked) + .l04g-btn .l04g-on{display:none}
.l04g-cb:checked ~ .l04g-box .l04g-g,.l04g-cb:checked ~ .l04g-box .l04g-pk{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.l04g-g{animation:none;opacity:1}.l04g-pk{animation:none;display:none}.l04g-btn{display:none}}
@keyframes l04g-g0{0%{opacity:1}33.333%{opacity:1}33.343%,100%{opacity:.45}}
.l04g-g0{animation-name:l04g-g0}
@keyframes l04g-g1{0%,33.323%{opacity:.45}33.333%{opacity:1}66.667%{opacity:1}66.677%,100%{opacity:.45}}
.l04g-g1{animation-name:l04g-g1}
@keyframes l04g-g2{0%,66.657%{opacity:.45}66.667%{opacity:1}100%{opacity:1}100.01%,100%{opacity:.45}}
.l04g-g2{animation-name:l04g-g2}
</style>
<defs>
<marker id="l04g-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="l04g-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="l04g-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<rect class="l04g-box" x="240" y="10" width="247" height="62" rx="10"/><text class="l04g-ttl" x="364" y="36">Path</text><text class="l04g-sub" x="364" y="56"></text>
<rect class="l04g-box" x="495" y="10" width="247" height="62" rx="10"/><text class="l04g-ttl" x="618" y="36">Limits</text><text class="l04g-sub" x="618" y="56"></text>
<g class="l04g-g l04g-g0">
<rect class="l04g-row" x="10" y="86" width="740" height="131" rx="8"/>
<text class="l04g-ttlL" x="24" y="112">RP-initiated</text>
<text class="l04g-subL" x="24" y="130">the app starts it</text>
<text class="l04g-nt" x="364" y="134">browser sent to the OP's</text>
<text class="l04g-nt" x="364" y="149">end_session_endpoint with</text>
<text class="l04g-nt" x="364" y="164">id_token_hint (recommended),</text>
<text class="l04g-nt" x="364" y="179">post_logout_redirect_uri, state</text>
<text class="l04g-nt" x="618" y="134">asks the OP to end its session,</text>
<text class="l04g-nt" x="618" y="149">only when someone signs out; the</text>
<text class="l04g-nt" x="618" y="164">OP SHOULD ask whether to log out</text>
<text class="l04g-nt" x="618" y="179">there too; other apps: front- or</text>
<text class="l04g-nt" x="618" y="194">back-channel</text>
</g>
<g class="l04g-g l04g-g1">
<rect class="l04g-row" x="10" y="225" width="740" height="116" rx="8"/>
<text class="l04g-ttlL" x="24" y="251">Front-channel</text>
<text class="l04g-subL" x="24" y="269">the OP starts it</text>
<text class="l04g-nt" x="364" y="273">OP renders each app's registered</text>
<text class="l04g-nt" x="364" y="288">logout URI in an iframe</text>
<text class="l04g-nt" x="618" y="273">browsers that block third-party</text>
<text class="l04g-nt" x="618" y="288">content can stop it working;</text>
<text class="l04g-nt" x="618" y="303">the spec recommends defensive</text>
<text class="l04g-nt" x="618" y="318">code to detect that</text>
</g>
<g class="l04g-g l04g-g2">
<rect class="l04g-row" x="10" y="349" width="740" height="131" rx="8"/>
<text class="l04g-ttlL" x="24" y="375">Back-channel</text>
<text class="l04g-subL" x="24" y="393">the OP starts it</text>
<text class="l04g-nt" x="364" y="397">OP POSTs a signed Logout Token to</text>
<text class="l04g-nt" x="364" y="412">the app's registered URI; the app must</text>
<text class="l04g-nt" x="364" y="427">end the session named by sub or sid</text>
<text class="l04g-nt" x="618" y="397">does not depend on the browser, but</text>
<text class="l04g-nt" x="618" y="412">the endpoint must be reachable from</text>
<text class="l04g-nt" x="618" y="427">the OP; whether an admin action makes</text>
<text class="l04g-nt" x="618" y="442">the OP send it is OP-specific (not</text>
<text class="l04g-nt" x="618" y="457">verified here for Okta or Entra)</text>
</g>
</svg>
</div>
</div>
<!-- /diagram:oidc-logout-matrix -->

Compare the three row by row. None of them revokes an ID token that was already issued: it stays valid until exp.

Versus SAML (lesson 2): in the SAML Web Browser SSO profile the response, or an artifact standing for it, reaches the service provider through the user's browser (HTTP POST or Artifact binding); in the OIDC code flow the ID token arrives on a direct call to the token endpoint. SAML is XML, OIDC is JSON and JWT. OIDC sits on OAuth, so the same login can also yield an access token for APIs.

## Your task: decode, verify, tamper

Run in this sandbox (bash, openssl 3.6, jq). The key is generated in a temp directory and thrown away; the token is a sample.

```bash
#!/usr/bin/env bash
set -euo pipefail
cd "$(mktemp -d)"
b64u()   { openssl base64 -A | tr '+/' '-_' | tr -d '='; }
unb64u() { tr '_-' '/+' | awk '{while (length($0)%4) $0=$0"="; print}' | openssl base64 -d -A; }
openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048 -out key.pem 2>/dev/null   # throwaway
openssl pkey -in key.pem -pubout -out pub.pem
now=$(date +%s)
hdr=$(printf '%s' '{"alg":"RS256","typ":"JWT","kid":"lab-key-1"}' | b64u)
pay=$(jq -nc --argjson n "$now" '{iss:"https://idp.example.com",sub:"lab-user-0001",aud:"lab-client-123",
      iat:$n,exp:($n+300),nonce:"lab-nonce-8f3a",email:"alice@example.com",email_verified:true}' | b64u)
sig=$(printf '%s.%s' "$hdr" "$pay" | openssl dgst -sha256 -sign key.pem | b64u)
jwt="$hdr.$pay.$sig"
printf '%s' "$jwt" | cut -d. -f1 | unb64u | jq -c .      # header: readable by anyone
printf '%s' "$jwt" | cut -d. -f2 | unb64u | jq -c .      # payload: readable, not yet verified
check() {   # verify header.payload against the signature
  printf '%s' "${1##*.}" | unb64u > sig.bin
  printf '%s' "${1%.*}" | openssl dgst -sha256 -verify pub.pem -signature sig.bin 2>&1 | tail -1 || true
}
check "$jwt"
bad=$(printf '%s' "$pay" | unb64u | jq -c '.sub="lab-user-ADMIN"' | b64u)   # change one claim
check "$hdr.$bad.$sig"                                                     # keep the old signature
```

Real output (the `iat` and `exp` numbers differ on every run):

```
{"alg":"RS256","typ":"JWT","kid":"lab-key-1"}
{"iss":"https://idp.example.com","sub":"lab-user-0001","aud":"lab-client-123","iat":1791263809,"exp":1791264109,"nonce":"lab-nonce-8f3a","email":"alice@example.com","email_verified":true}
Verified OK
Verification failure
```

Decoding needed no key; only the signature check did. Changing `sub` broke the signature. Now check the `iss`, `aud`, `exp` and `nonce` of the decoded payload by hand: the signature alone never covers those. Next: SCIM, which provisions the accounts these logins land in.
