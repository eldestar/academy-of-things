# OAuth 2.0

You have configured OIDC and SAML apps. This lesson covers the layer underneath OIDC: how an app is given limited, revocable access to an API on a user's behalf. It covers the flow you will see in most tenants, the settings that matter, and what breaks. Facts checked 2026-10-06.

Standards cited: RFC 6749 and 6750 (2012), RFC 7636 (PKCE), RFC 7009 (revocation), RFC 7662 (introspection), RFC 8628 (device grant), RFC 8707 (resource indicators), RFC 9068 (JWT access tokens) and RFC 9700 (BCP 240, January 2025, which updates 6749, 6750 and 6819). **OAuth 2.1** is not a standard: `draft-ietf-oauth-v2-1-16`, dated 3 September 2026, is an active Internet-Draft in the OAuth working group. Treat it as the direction of travel, not as a requirement.

## Delegation, not login

The four roles (RFC 6749, section 1.1): the **resource owner** (the user), the **client** (the app), the **authorization server** (AS, which authenticates the owner and issues tokens; your IdP tenant can be one) and the **resource server** (RS, the API that accepts access tokens). A client is **confidential** if it can keep credentials secret (a server-side app) and **public** if it cannot (a native or browser app).

OAuth authorizes an app; it does not log anyone in. The AS does authenticate the user, but the client only receives an access token meant for the RS. The OAuth 2.1 draft says OAuth defines nothing for authenticating users, and that OpenID Connect builds on it for that (next lesson). Treating a valid token, or the result of a `/me` call, as proof of sign-in is outside the standard.

Consent has its own attack. In a **consent phishing** attack (the draft, section 7.9) an attacker registers a client and sends the victim a genuine authorization URL. The victim signs in normally, even with a phishing-resistant factor, and then approves the attacker's scopes. The draft says the AS should control client registration and the scopes a client may request.

## The authorization code flow with PKCE

<!-- diagram:oauth-code-pkce -->
<div class="oa-wrap" style="position:relative">
<input type="checkbox" id="oa-pause" class="oa-cb" /><label for="oa-pause" class="oa-btn"><span class="oa-off">Pause animation</span><span class="oa-on">Play animation</span></label>
<div class="oa-box" style="overflow-x:auto">
<svg class="oa-flow" viewBox="0 0 760 864" role="img" aria-labelledby="oa-t oa-d" style="width:760px;max-width:100%;min-width:699px;height:auto;display:block;margin:0 auto">
<title id="oa-t">OAuth 2.0 authorization code flow with PKCE</title>
<desc id="oa-d">Three parties: the client app, the authorization server (AS) and the resource server (RS). Step 1: the client redirects the user's browser to the AS with client_id, redirect_uri, scope, state and a code_challenge using method S256. Step 2: the AS authenticates the user, obtains consent and binds the challenge to the code. Step 3: the AS redirects the browser to the redirect_uri with a code and state. Step 4: the client checks the state against the stored one, or relies on PKCE for CSRF protection if it knows the AS supports PKCE. Step 5: as a direct request rather than a browser redirect, the client posts the code, the code_verifier, the client_id (or client authentication) and the redirect_uri if it was sent at step 1 to the token endpoint, and receives an access token. If the recomputed challenge does not match, the AS returns invalid_grant. Step 6: the client calls the RS with Authorization: Bearer and the token. Step 7: the RS validates the token, by JWT checks or by introspection. The diagram highlights each step in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
<style>
svg.oa-flow{--ink:light-dark(#000000,#ffffff)}
.oa-box{fill:var(--panel);stroke:var(--border-strong);stroke-width:1.5}
.oa-hot{fill:var(--panel);stroke:var(--accent);stroke-width:2.5}
.oa-ttl{fill:var(--ink);font:600 15px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.oa-sub{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.oa-life{stroke:var(--border-strong);stroke-width:1.5;stroke-dasharray:4 5}
.oa-front{stroke:var(--accent);stroke-width:2;fill:none}
.oa-back{stroke:var(--muted);stroke-width:2;stroke-dasharray:7 5;fill:none}
.oa-bad{stroke:var(--bad);stroke-width:2;fill:none}
.oa-main{fill:var(--ink);font:600 13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.oa-badt{fill:var(--ink)}
.oa-dim{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.oa-badge{fill:var(--accent)}
.oa-b-back{fill:var(--muted)}
.oa-b-bad{fill:var(--bad)}
.oa-b-good{fill:var(--good)}
.oa-bt{fill:var(--on-accent);font:700 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.oa-note{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.oa-note-good{fill:var(--good-bg);stroke:var(--good);stroke-width:1.5}
.oa-note-bad{fill:var(--bad-bg);stroke:var(--bad);stroke-width:1.5}
.oa-nt{fill:var(--ink);font:500 12.5px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.oa-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:40s;animation-timing-function:linear;animation-iteration-count:infinite}
.oa-pk.oa-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.oa-pk.oa-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.oa-wrap{margin:20px 0}
@media (min-width:801px){.oa-wrap{margin-left:-44px;margin-right:-44px}}
.oa-g rect,.oa-g line,.oa-g path:not(.oa-gl){opacity:.5;animation-duration:40s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.oa-flow:hover .oa-g rect,svg.oa-flow:hover .oa-g line,svg.oa-flow:hover .oa-g path:not(.oa-gl),svg.oa-flow:hover .oa-pk{animation-play-state:paused}
.oa-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.oa-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.oa-btn:hover{background:var(--hover)}
.oa-cb:focus-visible + .oa-btn{outline:2px solid var(--accent);outline-offset:2px}
.oa-cb:checked + .oa-btn .oa-off,.oa-cb:not(:checked) + .oa-btn .oa-on{display:none}
.oa-cb:checked ~ .oa-box .oa-g rect,.oa-cb:checked ~ .oa-box .oa-g line,.oa-cb:checked ~ .oa-box .oa-g path:not(.oa-gl),.oa-cb:checked ~ .oa-box .oa-pk{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.oa-g rect,.oa-g line,.oa-g path:not(.oa-gl){animation:none;opacity:1}.oa-pk{animation:none;display:none}.oa-btn{display:none}}
@keyframes oa-g0{0%{opacity:1}15%{opacity:1}15.01%,100%{opacity:.5}}
@keyframes oa-p0{0%,-0.01%{opacity:0;transform:translateX(0)}0%{opacity:1;transform:translateX(0)}12%{opacity:1;transform:translateX(236px)}15%{opacity:1;transform:translateX(236px)}15.01%,100%{opacity:0;transform:translateX(236px)}}
.oa-g0 rect,.oa-g0 line,.oa-g0 path:not(.oa-gl){animation-name:oa-g0}.oa-p0{animation-name:oa-p0}
@keyframes oa-g1{0%,14.99%{opacity:.5}15%{opacity:1}25%{opacity:1}25.01%,100%{opacity:.5}}
.oa-g1 rect,.oa-g1 line,.oa-g1 path:not(.oa-gl){animation-name:oa-g1}
@keyframes oa-g2{0%,24.99%{opacity:.5}25%{opacity:1}40%{opacity:1}40.01%,100%{opacity:.5}}
@keyframes oa-p2{0%,24.99%{opacity:0;transform:translateX(0)}25%{opacity:1;transform:translateX(0)}37%{opacity:1;transform:translateX(-236px)}40%{opacity:1;transform:translateX(-236px)}40.01%,100%{opacity:0;transform:translateX(-236px)}}
.oa-g2 rect,.oa-g2 line,.oa-g2 path:not(.oa-gl){animation-name:oa-g2}.oa-p2{animation-name:oa-p2}
@keyframes oa-g3{0%,39.99%{opacity:.5}40%{opacity:1}50%{opacity:1}50.01%,100%{opacity:.5}}
.oa-g3 rect,.oa-g3 line,.oa-g3 path:not(.oa-gl){animation-name:oa-g3}
@keyframes oa-g4{0%,49.99%{opacity:.5}50%{opacity:1}65%{opacity:1}65.01%,100%{opacity:.5}}
@keyframes oa-p4{0%,49.99%{opacity:0;transform:translateX(0)}50%{opacity:1;transform:translateX(0)}62%{opacity:1;transform:translateX(-236px)}65%{opacity:1;transform:translateX(-236px)}65.01%,100%{opacity:0;transform:translateX(-236px)}}
.oa-g4 rect,.oa-g4 line,.oa-g4 path:not(.oa-gl){animation-name:oa-g4}.oa-p4{animation-name:oa-p4}
@keyframes oa-g5{0%,64.99%{opacity:.5}65%{opacity:1}75%{opacity:1}75.01%,100%{opacity:.5}}
.oa-g5 rect,.oa-g5 line,.oa-g5 path:not(.oa-gl){animation-name:oa-g5}
@keyframes oa-g6{0%,74.99%{opacity:.5}75%{opacity:1}90%{opacity:1}90.01%,100%{opacity:.5}}
@keyframes oa-p6{0%,74.99%{opacity:0;transform:translateX(0)}75%{opacity:1;transform:translateX(0)}87%{opacity:1;transform:translateX(506px)}90%{opacity:1;transform:translateX(506px)}90.01%,100%{opacity:0;transform:translateX(506px)}}
.oa-g6 rect,.oa-g6 line,.oa-g6 path:not(.oa-gl){animation-name:oa-g6}.oa-p6{animation-name:oa-p6}
@keyframes oa-g7{0%,89.99%{opacity:.5}90%{opacity:1}100%{opacity:1}100.01%,100%{opacity:.5}}
.oa-g7 rect,.oa-g7 line,.oa-g7 path:not(.oa-gl){animation-name:oa-g7}
</style>
<defs>
<marker id="oa-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="oa-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="oa-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<line class="oa-life" x1="110" y1="72" x2="110" y2="790"/>
<line class="oa-life" x1="380" y1="72" x2="380" y2="790"/>
<line class="oa-life" x1="650" y1="72" x2="650" y2="790"/>
<rect class="oa-box" x="20" y="10" width="180" height="62" rx="10"/><text class="oa-ttl" x="110" y="36">Client app</text><text class="oa-sub" x="110" y="56">the app asking for access</text>
<rect class="oa-hot" x="290" y="10" width="180" height="62" rx="10"/><text class="oa-ttl" x="380" y="36">Authorization server</text><text class="oa-sub" x="380" y="56">issues the tokens</text>
<rect class="oa-box" x="560" y="10" width="180" height="62" rx="10"/><text class="oa-ttl" x="650" y="36">Resource server</text><text class="oa-sub" x="650" y="56">the API</text>
<g class="oa-g oa-g0">
<text class="oa-main" x="245" y="108">redirect to the AS</text>
<text class="oa-dim" x="245" y="124">client_id, redirect_uri, scope, state</text>
<text class="oa-dim" x="245" y="140">code_challenge, method S256</text>
<line class="oa-front" x1="124" y1="154" x2="366" y2="154" marker-end="url(#oa-m-front)"/>
<circle class="oa-badge oa-b-front" cx="110" cy="154" r="12"/><text class="oa-bt" x="110" y="158.5">1</text>
</g>
<g class="oa-g oa-g1">
<rect class="oa-note" x="233" y="188" width="294" height="48" rx="8"/>
<text class="oa-nt" x="380" y="209">AS authenticates the user and obtains</text>
<text class="oa-nt" x="380" y="226">consent; binds the challenge to the code</text>
<circle class="oa-badge oa-b-plain" cx="233" cy="212" r="12"/><text class="oa-bt" x="233" y="216.5">2</text>
</g>
<g class="oa-g oa-g2">
<text class="oa-main" x="245" y="270">redirect to the redirect_uri</text>
<text class="oa-dim" x="245" y="286">code and state</text>
<line class="oa-front" x1="366" y1="300" x2="124" y2="300" marker-end="url(#oa-m-front)"/>
<circle class="oa-badge oa-b-front" cx="380" cy="300" r="12"/><text class="oa-bt" x="380" y="304.5">3</text>
</g>
<g class="oa-g oa-g3">
<rect class="oa-note-good" x="10" y="334" width="267" height="48" rx="8"/>
<text class="oa-nt" x="144" y="355">check state matches (or rely on PKCE</text>
<text class="oa-nt" x="144" y="372">if the AS is known to support it)</text>
<circle class="oa-badge oa-b-good" cx="10" cy="358" r="12"/><text class="oa-bt" x="10" y="362.5">4</text>
</g>
<g class="oa-g oa-g4">
<text class="oa-main" x="245" y="416">POST to the token endpoint</text>
<text class="oa-dim" x="245" y="432">code, code_verifier, client_id or client auth</text>
<text class="oa-dim" x="245" y="448">redirect_uri if sent at step 1</text>
<line class="oa-back" x1="124" y1="462" x2="366" y2="462" marker-end="url(#oa-m-back)"/>
<circle class="oa-badge oa-b-back" cx="110" cy="462" r="12"/><text class="oa-bt" x="110" y="466.5">5</text>
<text class="oa-main" x="245" y="502">access token</text>
<line class="oa-back" x1="366" y1="516" x2="124" y2="516" marker-end="url(#oa-m-back)"/>
</g>
<g class="oa-g oa-g5">
<rect class="oa-note-bad" x="230" y="550" width="300" height="48" rx="8"/>
<text class="oa-nt" x="380" y="571">AS recomputes the challenge and compares:</text>
<text class="oa-nt" x="380" y="588">a mismatch returns invalid_grant</text>
<circle class="oa-badge oa-b-bad" cx="230" cy="574" r="12"/><text class="oa-bt" x="230" y="578.5">!</text>
</g>
<g class="oa-g oa-g6">
<text class="oa-main" x="380" y="632">API request</text>
<text class="oa-dim" x="380" y="648">Authorization: Bearer &lt;token></text>
<line class="oa-back" x1="124" y1="662" x2="636" y2="662" marker-end="url(#oa-m-back)"/>
<circle class="oa-badge oa-b-back" cx="110" cy="662" r="12"/><text class="oa-bt" x="110" y="666.5">6</text>
</g>
<g class="oa-g oa-g7">
<rect class="oa-note-good" x="529" y="696" width="221" height="48" rx="8"/>
<text class="oa-nt" x="640" y="717">the RS validates the token</text>
<text class="oa-nt" x="640" y="734">(JWT checks or introspection)</text>
<circle class="oa-badge oa-b-good" cx="529" cy="720" r="12"/><text class="oa-bt" x="529" y="724.5">7</text>
</g>
<circle class="oa-pk oa-p0" cx="130" cy="154" r="5.5"/>
<circle class="oa-pk oa-p2" cx="360" cy="300" r="5.5"/>
<circle class="oa-pk oa-p4 oa-pkback" cx="360" cy="516" r="5.5"/>
<circle class="oa-pk oa-p6 oa-pkback" cx="130" cy="662" r="5.5"/>
<line class="oa-front" x1="40" y1="818" x2="70" y2="818"/>
<text class="oa-dim" x="78" y="822" style="text-anchor:start">through the user's browser</text>
<line class="oa-back" x1="278" y1="818" x2="308" y2="818"/>
<text class="oa-dim" x="316" y="822" style="text-anchor:start">direct request, not a redirect</text>
<rect class="oa-note-bad" x="542" y="810" width="22" height="16" rx="4"/>
<text class="oa-dim" x="572" y="822" style="text-anchor:start">failure mode</text>
<rect class="oa-note-good" x="40" y="832" width="22" height="16" rx="4"/>
<text class="oa-dim" x="70" y="844" style="text-anchor:start">a check to perform</text>
</svg>
</div>
</div>
<!-- /diagram:oauth-code-pkce -->

Solid arrows pass through the user's browser; dashed arrows are direct requests, not browser redirects. The numbers match the list below, and the red note marks the failure at step 5: a challenge mismatch returns `invalid_grant`.

1. The client redirects the browser to the AS: `response_type=code`, `client_id`, `redirect_uri`, `scope`, `state`, `code_challenge`, `code_challenge_method=S256`.
2. The AS authenticates the user and obtains consent, and binds the challenge to the code it will issue.
3. The AS redirects to the `redirect_uri` with `code` and `state`.
4. The client checks `state` against the one stored for this browser, or relies on PKCE for CSRF protection if it knows the AS supports PKCE (see below).
5. The client POSTs to the token endpoint over a direct connection: `grant_type=authorization_code`, `code`, `code_verifier`, `redirect_uri` if it was sent at step 1, and `client_id` (or client authentication). The AS recomputes the challenge and compares. A mismatch returns `invalid_grant` (RFC 7636, section 4.6).
6. The client calls the API with `Authorization: Bearer <token>`.
7. The RS validates the token.

The details that decide whether it is safe:

- **Code**: must expire shortly (10 minutes maximum recommended) and be single-use. If a code is used twice, the AS must deny the request and should revoke the tokens already issued from it. The code is bound to the client and the redirect URI.
- **Verifier**: 43 to 128 characters from `A-Z a-z 0-9 - . _ ~`; RFC 7636 suggests base64url of 32 random octets, which is 43 characters. Challenge = base64url(SHA-256(verifier)). **S256** is the method to use; `plain` only exists for clients that cannot hash.
- **Who needs PKCE**: RFC 9700 says the AS must support it and enforce `code_verifier` when a challenge was sent, public clients must use it, and confidential clients are recommended to. It also stops code injection and CSRF.
- **Client authentication**: confidential clients must authenticate at the token endpoint. Public clients send only `client_id`, and must register their redirect URI.
- **`state`**: RFC 9700 requires CSRF protection. A client may rely on PKCE for it only if it knows the AS supports PKCE; otherwise it needs a one-time `state` bound to the browser.
- **Redirect URI**: the AS must use exact string matching (native apps on localhost may vary the port). No patterns, no wildcards.

## Grants that matter, and two to avoid

- **Client credentials**: no user; the client authenticates as itself. Confidential clients only, and a refresh token should not be issued.
- **Device authorization** (RFC 8628): the device gets `device_code`, `user_code` and `verification_uri`, shows the code, and polls the token endpoint. The default poll `interval` is 5 seconds. `authorization_pending` means keep polling. `slow_down` means add 5 seconds to the interval for this and all later requests. `expired_token` and `access_denied` end the session. A device should start only when the user asks. Attackers can email a victim a code to enter, so the AS should show what is being authorized and ask the user to confirm the device is in their hands.

<!-- diagram:oauth-device-grant -->
<div class="l03c-wrap" style="position:relative">
<input type="checkbox" id="l03c-pause" class="l03c-cb" /><label for="l03c-pause" class="l03c-btn"><span class="l03c-off">Pause animation</span><span class="l03c-on">Play animation</span></label>
<div class="l03c-box" style="overflow-x:auto">
<svg class="l03c-flow" viewBox="0 0 760 744" role="img" aria-labelledby="l03c-t l03c-d" style="width:760px;max-width:100%;min-width:699px;height:auto;display:block;margin:0 auto">
<title id="l03c-t">Device authorization grant (RFC 8628)</title>
<desc id="l03c-d">Three parties: the device, the authorization server and the user. Step 1: the device starts, which it should do only when the user asks, and receives device_code, user_code and verification_uri. Step 2: the device shows the code. Step 3: the user enters the code; the AS should show what is being authorized and ask the user to confirm the device is in their hands. Step 4: the device polls the token endpoint, by default every 5 seconds, and authorization_pending means keep polling. Step 5: slow_down means add 5 seconds to the interval for this and all later requests. Step 6: expired_token and access_denied end the session. The diagram highlights each step in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
<style>
svg.l03c-flow{--ink:light-dark(#000000,#ffffff)}
.l03c-box{fill:var(--panel);stroke:var(--border-strong);stroke-width:1.5}
.l03c-hot{fill:var(--panel);stroke:var(--accent);stroke-width:2.5}
.l03c-ttl{fill:var(--ink);font:600 15px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l03c-sub{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l03c-life{stroke:var(--border-strong);stroke-width:1.5;stroke-dasharray:4 5}
.l03c-front{stroke:var(--accent);stroke-width:2;fill:none}
.l03c-back{stroke:var(--muted);stroke-width:2;stroke-dasharray:7 5;fill:none}
.l03c-bad{stroke:var(--bad);stroke-width:2;fill:none}
.l03c-main{fill:var(--ink);font:600 13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l03c-badt{fill:var(--ink)}
.l03c-dim{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l03c-badge{fill:var(--accent)}
.l03c-b-back{fill:var(--muted)}
.l03c-b-bad{fill:var(--bad)}
.l03c-b-good{fill:var(--good)}
.l03c-bt{fill:var(--on-accent);font:700 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l03c-note{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l03c-note-good{fill:var(--good-bg);stroke:var(--good);stroke-width:1.5}
.l03c-note-bad{fill:var(--bad-bg);stroke:var(--bad);stroke-width:1.5}
.l03c-nt{fill:var(--ink);font:500 12.5px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l03c-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:28s;animation-timing-function:linear;animation-iteration-count:infinite}
.l03c-pk.l03c-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.l03c-pk.l03c-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.l03c-wrap{margin:20px 0}
@media (min-width:801px){.l03c-wrap{margin-left:-44px;margin-right:-44px}}
.l03c-g rect,.l03c-g line,.l03c-g path:not(.l03c-gl){opacity:.5;animation-duration:28s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.l03c-flow:hover .l03c-g rect,svg.l03c-flow:hover .l03c-g line,svg.l03c-flow:hover .l03c-g path:not(.l03c-gl),svg.l03c-flow:hover .l03c-pk{animation-play-state:paused}
.l03c-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.l03c-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.l03c-btn:hover{background:var(--hover)}
.l03c-cb:focus-visible + .l03c-btn{outline:2px solid var(--accent);outline-offset:2px}
.l03c-cb:checked + .l03c-btn .l03c-off,.l03c-cb:not(:checked) + .l03c-btn .l03c-on{display:none}
.l03c-cb:checked ~ .l03c-box .l03c-g rect,.l03c-cb:checked ~ .l03c-box .l03c-g line,.l03c-cb:checked ~ .l03c-box .l03c-g path:not(.l03c-gl),.l03c-cb:checked ~ .l03c-box .l03c-pk{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.l03c-g rect,.l03c-g line,.l03c-g path:not(.l03c-gl){animation:none;opacity:1}.l03c-pk{animation:none;display:none}.l03c-btn{display:none}}
@keyframes l03c-g0{0%{opacity:1}21.429%{opacity:1}21.439%,100%{opacity:.5}}
@keyframes l03c-p0{0%,-0.01%{opacity:0;transform:translateX(0)}0%{opacity:1;transform:translateX(0)}17.143%{opacity:1;transform:translateX(-236px)}21.429%{opacity:1;transform:translateX(-236px)}21.439%,100%{opacity:0;transform:translateX(-236px)}}
.l03c-g0 rect,.l03c-g0 line,.l03c-g0 path:not(.l03c-gl){animation-name:l03c-g0}.l03c-p0{animation-name:l03c-p0}
@keyframes l03c-g1{0%,21.419%{opacity:.5}21.429%{opacity:1}35.714%{opacity:1}35.724%,100%{opacity:.5}}
.l03c-g1 rect,.l03c-g1 line,.l03c-g1 path:not(.l03c-gl){animation-name:l03c-g1}
@keyframes l03c-g2{0%,35.704%{opacity:.5}35.714%{opacity:1}50%{opacity:1}50.01%,100%{opacity:.5}}
.l03c-g2 rect,.l03c-g2 line,.l03c-g2 path:not(.l03c-gl){animation-name:l03c-g2}
@keyframes l03c-g3{0%,49.99%{opacity:.5}50%{opacity:1}71.429%{opacity:1}71.439%,100%{opacity:.5}}
@keyframes l03c-p3{0%,49.99%{opacity:0;transform:translateX(0)}50%{opacity:1;transform:translateX(0)}67.143%{opacity:1;transform:translateX(-236px)}71.429%{opacity:1;transform:translateX(-236px)}71.439%,100%{opacity:0;transform:translateX(-236px)}}
.l03c-g3 rect,.l03c-g3 line,.l03c-g3 path:not(.l03c-gl){animation-name:l03c-g3}.l03c-p3{animation-name:l03c-p3}
@keyframes l03c-g4{0%,71.419%{opacity:.5}71.429%{opacity:1}85.714%{opacity:1}85.724%,100%{opacity:.5}}
.l03c-g4 rect,.l03c-g4 line,.l03c-g4 path:not(.l03c-gl){animation-name:l03c-g4}
@keyframes l03c-g5{0%,85.704%{opacity:.5}85.714%{opacity:1}100%{opacity:1}100.01%,100%{opacity:.5}}
.l03c-g5 rect,.l03c-g5 line,.l03c-g5 path:not(.l03c-gl){animation-name:l03c-g5}
</style>
<defs>
<marker id="l03c-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="l03c-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="l03c-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<line class="l03c-life" x1="110" y1="72" x2="110" y2="670"/>
<line class="l03c-life" x1="380" y1="72" x2="380" y2="670"/>
<line class="l03c-life" x1="650" y1="72" x2="650" y2="670"/>
<rect class="l03c-box" x="20" y="10" width="180" height="62" rx="10"/><text class="l03c-ttl" x="110" y="36">Device</text><text class="l03c-sub" x="110" y="56">shows the code, then polls</text>
<rect class="l03c-hot" x="290" y="10" width="180" height="62" rx="10"/><text class="l03c-ttl" x="380" y="36">Authorization server</text><text class="l03c-sub" x="380" y="56">issues the codes</text>
<rect class="l03c-box" x="560" y="10" width="180" height="62" rx="10"/><text class="l03c-ttl" x="650" y="36">User</text><text class="l03c-sub" x="650" y="56">the person who authorizes</text>
<g class="l03c-g l03c-g0">
<text class="l03c-main" x="245" y="108">start (a device should do this</text>
<text class="l03c-dim" x="245" y="124">only when the user asks)</text>
<line class="l03c-front" x1="124" y1="138" x2="366" y2="138" marker-end="url(#l03c-m-front)"/>
<circle class="l03c-badge l03c-b-front" cx="110" cy="138" r="12"/><text class="l03c-bt" x="110" y="142.5">1</text>
<text class="l03c-main" x="245" y="178">device_code, user_code,</text>
<text class="l03c-dim" x="245" y="194">verification_uri</text>
<line class="l03c-front" x1="366" y1="208" x2="124" y2="208" marker-end="url(#l03c-m-front)"/>
</g>
<g class="l03c-g l03c-g1">
<rect class="l03c-note" x="32" y="242" width="155" height="31" rx="8"/>
<text class="l03c-nt" x="110" y="263">shows the user_code</text>
<circle class="l03c-badge l03c-b-plain" cx="32" cy="258" r="12"/><text class="l03c-bt" x="32" y="262.0">2</text>
</g>
<g class="l03c-g l03c-g2">
<rect class="l03c-note" x="575" y="301" width="150" height="31" rx="8"/>
<text class="l03c-nt" x="650" y="322">enters the code</text>
<circle class="l03c-badge l03c-b-plain" cx="575" cy="316" r="12"/><text class="l03c-bt" x="575" y="321.0">3</text>
<rect class="l03c-note-good" x="207" y="226" width="346" height="48" rx="8"/>
<text class="l03c-nt" x="380" y="247">should show what is being authorized and ask</text>
<text class="l03c-nt" x="380" y="264">the user to confirm the device is in their hands</text>
</g>
<g class="l03c-g l03c-g3">
<text class="l03c-main" x="245" y="366">polls the token endpoint</text>
<text class="l03c-dim" x="245" y="382">default interval: 5 seconds</text>
<line class="l03c-back" x1="124" y1="396" x2="366" y2="396" marker-end="url(#l03c-m-back)"/>
<circle class="l03c-badge l03c-b-back" cx="110" cy="396" r="12"/><text class="l03c-bt" x="110" y="400.5">4</text>
<text class="l03c-main" x="245" y="436">authorization_pending:</text>
<text class="l03c-dim" x="245" y="452">keep polling</text>
<line class="l03c-back" x1="366" y1="466" x2="124" y2="466" marker-end="url(#l03c-m-back)"/>
</g>
<g class="l03c-g l03c-g4">
<rect class="l03c-note" x="10" y="500" width="294" height="48" rx="8"/>
<text class="l03c-nt" x="157" y="521">slow_down: add 5 seconds to the interval</text>
<text class="l03c-nt" x="157" y="538">(this and all later requests)</text>
<circle class="l03c-badge l03c-b-plain" cx="10" cy="524" r="12"/><text class="l03c-bt" x="10" y="528.5">5</text>
</g>
<g class="l03c-g l03c-g5">
<rect class="l03c-note-bad" x="10" y="576" width="234" height="48" rx="8"/>
<text class="l03c-nt" x="127" y="597">expired_token or access_denied:</text>
<text class="l03c-nt" x="127" y="614">the session ends</text>
<circle class="l03c-badge l03c-b-bad" cx="10" cy="600" r="12"/><text class="l03c-bt" x="10" y="604.5">6</text>
</g>
<circle class="l03c-pk l03c-p0" cx="360" cy="208" r="5.5"/>
<circle class="l03c-pk l03c-p3 l03c-pkback" cx="360" cy="466" r="5.5"/>
<line class="l03c-front" x1="40" y1="698" x2="70" y2="698"/>
<text class="l03c-dim" x="78" y="702" style="text-anchor:start">request or response</text>
<line class="l03c-back" x1="233" y1="698" x2="263" y2="698"/>
<text class="l03c-dim" x="271" y="702" style="text-anchor:start">polling the token endpoint</text>
<rect class="l03c-note-bad" x="471" y="690" width="22" height="16" rx="4"/>
<text class="l03c-dim" x="501" y="702" style="text-anchor:start">the session ends</text>
<rect class="l03c-note-good" x="40" y="712" width="22" height="16" rx="4"/>
<text class="l03c-dim" x="70" y="724" style="text-anchor:start">what the AS should do</text>
</svg>
</div>
</div>
<!-- /diagram:oauth-device-grant -->

The device shows the code and polls while the user enters it, so hops 3 and 4 overlap in time. The badges number this diagram's own hops and notes (1 to 6), not the steps of the authorization code flow.

- **Refresh token**: `grant_type=refresh_token`. The new scope cannot exceed the original.
- **Avoid implicit** (`response_type=token`): RFC 9700 says clients should not use it. Tokens in the redirect URL leak through history and logs, and cannot be sender-constrained.
- **Avoid resource owner password**: RFC 9700 says it must not be used. It hands credentials to the client and is not designed to work with MFA.

The OAuth 2.1 draft drops both grants and `plain`, makes PKCE part of the code grant, and drops bearer tokens in query strings.

## Tokens: who has to understand what

<!-- diagram:oauth-tokens -->
<div class="l03a-wrap" style="position:relative">
<input type="checkbox" id="l03a-pause" class="l03a-cb" /><label for="l03a-pause" class="l03a-btn"><span class="l03a-off">Pause animation</span><span class="l03a-on">Play animation</span></label>
<div class="l03a-box" style="overflow-x:auto">
<svg class="l03a-flow" viewBox="0 0 760 482" role="img" aria-labelledby="l03a-t l03a-d" style="width:760px;max-width:100%;min-width:699px;height:auto;display:block;margin:0 auto">
<title id="l03a-t">Who has to understand an access token</title>
<desc id="l03a-d">A nested diagram. The access token is opaque to the client, which must not inspect it because the AS or RS may change its format. The resource server must understand it in one of two ways. In the JWT form (RFC 9068) it checks that typ is at+jwt, which marks an access token rather than an ID token; the signature, never alg none; iss and exp; and that aud names this resource server, the only claim that says which API a token is for. In the introspection form (RFC 7662) it POSTs the token to an endpoint that must itself require authorization, and the JSON answer has a required boolean active; answers may be cached at the cost of freshness. The diagram highlights each part in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
<style>
svg.l03a-flow{--ink:light-dark(#000000,#ffffff)}
.l03a-box{fill:var(--panel);stroke:var(--border-strong);stroke-width:1.5}
.l03a-hot{fill:var(--panel);stroke:var(--accent);stroke-width:2.5}
.l03a-ttl{fill:var(--ink);font:600 15px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l03a-sub{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l03a-life{stroke:var(--border-strong);stroke-width:1.5;stroke-dasharray:4 5}
.l03a-front{stroke:var(--accent);stroke-width:2;fill:none}
.l03a-back{stroke:var(--muted);stroke-width:2;stroke-dasharray:7 5;fill:none}
.l03a-bad{stroke:var(--bad);stroke-width:2;fill:none}
.l03a-main{fill:var(--ink);font:600 13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l03a-badt{fill:var(--ink)}
.l03a-dim{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l03a-badge{fill:var(--accent)}
.l03a-b-back{fill:var(--muted)}
.l03a-b-bad{fill:var(--bad)}
.l03a-b-good{fill:var(--good)}
.l03a-bt{fill:var(--on-accent);font:700 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l03a-note{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l03a-note-good{fill:var(--good-bg);stroke:var(--good);stroke-width:1.5}
.l03a-note-bad{fill:var(--bad-bg);stroke:var(--bad);stroke-width:1.5}
.l03a-nt{fill:var(--ink);font:500 12.5px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l03a-nest{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l03a-row{fill:var(--raised);stroke:var(--border-strong);stroke-width:1}
.l03a-ttlL{fill:var(--ink);font:600 14px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l03a-subL{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l03a-dimL{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l03a-dimR{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:end}
.l03a-conn{stroke:var(--accent);stroke-width:1.5;fill:none}
.l03a-edge{stroke:var(--border-strong);stroke-width:1.75;fill:none}
.l03a-hl{fill:none;stroke:var(--accent);stroke-width:3}
.l03a-hle{stroke:var(--accent);stroke-width:3;fill:none}
.l03a-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:28s;animation-timing-function:linear;animation-iteration-count:infinite}
.l03a-pk.l03a-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.l03a-pk.l03a-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.l03a-wrap{margin:20px 0}
@media (min-width:801px){.l03a-wrap{margin-left:-44px;margin-right:-44px}}
.l03a-g rect,.l03a-g line,.l03a-g path:not(.l03a-gl){opacity:.5;animation-duration:28s;animation-timing-function:linear;animation-iteration-count:infinite}
.l03a-h{opacity:0;animation-duration:28s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.l03a-flow:hover .l03a-g rect,svg.l03a-flow:hover .l03a-g line,svg.l03a-flow:hover .l03a-g path:not(.l03a-gl),svg.l03a-flow:hover .l03a-pk,svg.l03a-flow:hover .l03a-h{animation-play-state:paused}
.l03a-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.l03a-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.l03a-btn:hover{background:var(--hover)}
.l03a-cb:focus-visible + .l03a-btn{outline:2px solid var(--accent);outline-offset:2px}
.l03a-cb:checked + .l03a-btn .l03a-off,.l03a-cb:not(:checked) + .l03a-btn .l03a-on{display:none}
.l03a-cb:checked ~ .l03a-box .l03a-g rect,.l03a-cb:checked ~ .l03a-box .l03a-g line,.l03a-cb:checked ~ .l03a-box .l03a-g path:not(.l03a-gl),.l03a-cb:checked ~ .l03a-box .l03a-pk,.l03a-cb:checked ~ .l03a-box .l03a-h{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.l03a-g rect,.l03a-g line,.l03a-g path:not(.l03a-gl){animation:none;opacity:1}.l03a-pk{animation:none;display:none}.l03a-h{animation:none;opacity:0}.l03a-btn{display:none}}
@keyframes l03a-g0{0%{opacity:1}14.286%{opacity:1}14.296%,100%{opacity:.5}}
@keyframes l03a-h0{0%{opacity:1}14.286%{opacity:1}14.296%,100%{opacity:0}}
.l03a-g0 rect,.l03a-g0 line,.l03a-g0 path:not(.l03a-gl){animation-name:l03a-g0}.l03a-h0{animation-name:l03a-h0}
@keyframes l03a-g1{0%,14.276%{opacity:.5}14.286%{opacity:1}28.571%{opacity:1}28.581%,100%{opacity:.5}}
@keyframes l03a-h1{0%,14.276%{opacity:0}14.286%{opacity:1}28.571%{opacity:1}28.581%,100%{opacity:0}}
.l03a-g1 rect,.l03a-g1 line,.l03a-g1 path:not(.l03a-gl){animation-name:l03a-g1}.l03a-h1{animation-name:l03a-h1}
@keyframes l03a-g2{0%,28.561%{opacity:.5}28.571%{opacity:1}42.857%{opacity:1}42.867%,100%{opacity:.5}}
@keyframes l03a-h2{0%,28.561%{opacity:0}28.571%{opacity:1}42.857%{opacity:1}42.867%,100%{opacity:0}}
.l03a-g2 rect,.l03a-g2 line,.l03a-g2 path:not(.l03a-gl){animation-name:l03a-g2}.l03a-h2{animation-name:l03a-h2}
@keyframes l03a-g3{0%,42.847%{opacity:.5}42.857%{opacity:1}57.143%{opacity:1}57.153%,100%{opacity:.5}}
@keyframes l03a-h3{0%,42.847%{opacity:0}42.857%{opacity:1}57.143%{opacity:1}57.153%,100%{opacity:0}}
.l03a-g3 rect,.l03a-g3 line,.l03a-g3 path:not(.l03a-gl){animation-name:l03a-g3}.l03a-h3{animation-name:l03a-h3}
@keyframes l03a-g4{0%,57.133%{opacity:.5}57.143%{opacity:1}71.429%{opacity:1}71.439%,100%{opacity:.5}}
@keyframes l03a-h4{0%,57.133%{opacity:0}57.143%{opacity:1}71.429%{opacity:1}71.439%,100%{opacity:0}}
.l03a-g4 rect,.l03a-g4 line,.l03a-g4 path:not(.l03a-gl){animation-name:l03a-g4}.l03a-h4{animation-name:l03a-h4}
@keyframes l03a-g5{0%,71.419%{opacity:.5}71.429%{opacity:1}85.714%{opacity:1}85.724%,100%{opacity:.5}}
@keyframes l03a-h5{0%,71.419%{opacity:0}71.429%{opacity:1}85.714%{opacity:1}85.724%,100%{opacity:0}}
.l03a-g5 rect,.l03a-g5 line,.l03a-g5 path:not(.l03a-gl){animation-name:l03a-g5}.l03a-h5{animation-name:l03a-h5}
@keyframes l03a-g6{0%,85.704%{opacity:.5}85.714%{opacity:1}100%{opacity:1}100.01%,100%{opacity:.5}}
@keyframes l03a-h6{0%,85.704%{opacity:0}85.714%{opacity:1}100%{opacity:1}100.01%,100%{opacity:0}}
.l03a-g6 rect,.l03a-g6 line,.l03a-g6 path:not(.l03a-gl){animation-name:l03a-g6}.l03a-h6{animation-name:l03a-h6}
</style>
<defs>
<marker id="l03a-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="l03a-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="l03a-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<rect class="l03a-box" x="14" y="16" width="440" height="408" rx="9"/><text class="l03a-ttlL" x="28" y="37">Access token</text><text class="l03a-subL" x="28" y="54">opaque to the client, understood by the RS</text>
<rect class="l03a-nest" x="26" y="62" width="416" height="238" rx="9"/><text class="l03a-ttlL" x="40" y="83">JWT form (RFC 9068)</text><text class="l03a-subL" x="40" y="100">one way for the RS to understand it</text>
<rect class="l03a-nest" x="38" y="108" width="392" height="46" rx="9"/><text class="l03a-ttlL" x="52" y="129">typ</text><text class="l03a-subL" x="52" y="146">at+jwt</text>
<rect class="l03a-nest" x="38" y="162" width="392" height="32" rx="9"/><text class="l03a-ttlL" x="52" y="183">Signature</text>
<rect class="l03a-nest" x="38" y="202" width="392" height="32" rx="9"/><text class="l03a-ttlL" x="52" y="223">iss, exp</text>
<rect class="l03a-nest" x="38" y="242" width="392" height="46" rx="9"/><text class="l03a-ttlL" x="52" y="263">aud</text><text class="l03a-subL" x="52" y="280">which API the token is for</text>
<rect class="l03a-nest" x="26" y="308" width="416" height="104" rx="9"/><text class="l03a-ttlL" x="40" y="329">Introspection (RFC 7662)</text><text class="l03a-subL" x="40" y="346">the other way for the RS</text>
<rect class="l03a-nest" x="38" y="354" width="392" height="46" rx="9"/><text class="l03a-ttlL" x="52" y="375">active</text><text class="l03a-subL" x="52" y="392">required boolean in the JSON answer</text>
<g class="l03a-g l03a-g0">
<path class="l03a-conn" d="M454,33 L462,33 L462,34 L470,34" marker-end="url(#l03a-m-front)"/>
<rect class="l03a-note" x="484" y="10" width="262" height="48" rx="8"/>
<text class="l03a-nt" x="615" y="31">Client: must not inspect it (RFC 9068)</text>
<text class="l03a-nt" x="615" y="48">The AS or RS may change its format</text>
<circle class="l03a-badge l03a-b-front" cx="484" cy="34" r="12"/><text class="l03a-bt" x="484" y="38.5">1</text>
</g>
<g class="l03a-g l03a-g1">
<path class="l03a-conn" d="M430,125 L466,125 L466,125 L470,125" marker-end="url(#l03a-m-front)"/>
<rect class="l03a-note-good" x="484" y="101" width="262" height="48" rx="8"/>
<text class="l03a-nt" x="615" y="122">Must be at+jwt: marks an access</text>
<text class="l03a-nt" x="615" y="139">token, not an ID token</text>
<circle class="l03a-badge l03a-b-good" cx="484" cy="125" r="12"/><text class="l03a-bt" x="484" y="129.5">2</text>
</g>
<g class="l03a-g l03a-g2">
<path class="l03a-conn" d="M430,179 L470,179 L470,179 L470,179" marker-end="url(#l03a-m-front)"/>
<rect class="l03a-note-good" x="484" y="164" width="262" height="31" rx="8"/>
<text class="l03a-nt" x="615" y="184">Check it (never alg none)</text>
<circle class="l03a-badge l03a-b-good" cx="484" cy="179" r="12"/><text class="l03a-bt" x="484" y="183.5">3</text>
</g>
<g class="l03a-g l03a-g3">
<path class="l03a-conn" d="M430,219 L474,219 L474,220 L470,220" marker-end="url(#l03a-m-front)"/>
<rect class="l03a-note-good" x="484" y="204" width="262" height="31" rx="8"/>
<text class="l03a-nt" x="615" y="226">Check both</text>
<circle class="l03a-badge l03a-b-good" cx="484" cy="220" r="12"/><text class="l03a-bt" x="484" y="224.5">4</text>
</g>
<g class="l03a-g l03a-g4">
<path class="l03a-conn" d="M430,259 L462,259 L462,270 L470,270" marker-end="url(#l03a-m-front)"/>
<rect class="l03a-note-good" x="484" y="246" width="262" height="48" rx="8"/>
<text class="l03a-nt" x="615" y="266">Must name this RS: the only claim</text>
<text class="l03a-nt" x="615" y="284">that says which API it is for</text>
<circle class="l03a-badge l03a-b-good" cx="484" cy="270" r="12"/><text class="l03a-bt" x="484" y="274.0">5</text>
</g>
<g class="l03a-g l03a-g5">
<path class="l03a-conn" d="M442,325 L466,325 L466,328 L470,328" marker-end="url(#l03a-m-front)"/>
<rect class="l03a-note-good" x="484" y="304" width="262" height="48" rx="8"/>
<text class="l03a-nt" x="615" y="324">POST the token; the endpoint must</text>
<text class="l03a-nt" x="615" y="342">itself require authorization</text>
<circle class="l03a-badge l03a-b-good" cx="484" cy="328" r="12"/><text class="l03a-bt" x="484" y="332.0">6</text>
</g>
<g class="l03a-g l03a-g6">
<path class="l03a-conn" d="M430,371 L470,371 L470,386 L470,386" marker-end="url(#l03a-m-front)"/>
<rect class="l03a-note-good" x="484" y="362" width="262" height="48" rx="8"/>
<text class="l03a-nt" x="615" y="382">Required in the JSON answer; answers</text>
<text class="l03a-nt" x="615" y="400">may be cached, at a cost in freshness</text>
<circle class="l03a-badge l03a-b-good" cx="484" cy="386" r="12"/><text class="l03a-bt" x="484" y="390.0">7</text>
</g>
<g class="l03a-h l03a-h0">
<rect class="l03a-hl" x="14" y="16" width="440" height="408" rx="9"/>
</g>
<g class="l03a-h l03a-h1">
<rect class="l03a-hl" x="38" y="108" width="392" height="46" rx="9"/>
</g>
<g class="l03a-h l03a-h2">
<rect class="l03a-hl" x="38" y="162" width="392" height="32" rx="9"/>
</g>
<g class="l03a-h l03a-h3">
<rect class="l03a-hl" x="38" y="202" width="392" height="32" rx="9"/>
</g>
<g class="l03a-h l03a-h4">
<rect class="l03a-hl" x="38" y="242" width="392" height="46" rx="9"/>
</g>
<g class="l03a-h l03a-h5">
<rect class="l03a-hl" x="26" y="308" width="416" height="104" rx="9"/>
</g>
<g class="l03a-h l03a-h6">
<rect class="l03a-hl" x="38" y="354" width="392" height="46" rx="9"/>
</g>
<rect class="l03a-note" x="40" y="450" width="22" height="16" rx="4"/>
<text class="l03a-dim" x="70" y="462" style="text-anchor:start">a rule for the client</text>
<rect class="l03a-note-good" x="238" y="450" width="22" height="16" rx="4"/>
<text class="l03a-dim" x="268" y="462" style="text-anchor:start">what the RS does or checks</text>
</svg>
</div>
</div>
<!-- /diagram:oauth-tokens -->

Read it from the top down. The first callout is the client's rule for the whole token; the green callouts are what a resource server does or checks, depending on whether it reads a JWT or asks the AS by introspection.

- **Client**: opaque. RFC 9068 says the client must not inspect an access token, because the AS or RS may change its format. Microsoft's Entra documentation says clients should not validate access tokens, and that tokens for Microsoft Graph may not be JWTs. Okta's documentation says tokens from the org authorization server are not meant for your apps to validate and may change without notice; use a custom authorization server for your own APIs (in production this needs the API Access Management product).
- **RS**: it must understand the token, in one of two ways. **Introspection** (RFC 7662): POST the token; the JSON answer has a required boolean `active`; the endpoint must itself require authorization, and responses may be cached at the cost of freshness. **JWT** (RFC 9068): check `typ` is `at+jwt`, the signature (never `alg` `none`), `iss`, that `aud` names this RS, and `exp`. `typ` marks the JWT as an access token rather than an ID token; it is the same for every API, so only `aud` says which API a token is for.
- **Errors** (RFC 6750): `invalid_token` should be 401, `insufficient_scope` 403 and `invalid_request` 400.
- **Audience**: the RS must refuse tokens meant for another RS. The client can say where it will use the token with the `resource` parameter (RFC 8707, an absolute URI; error `invalid_target`). Scope is typically about what access is wanted, not where it will be used (RFC 8707); some deployments encode the resource in the scope, but `resource` is the standard way to say where.
- **Lifetime and revocation**: RFC 6750 says tokens should live one hour or less. RFC 7009 revocation (`POST` with `token`) returns 200 even for an invalid token. Refresh tokens must be revocable and access tokens should be. A self-contained JWT stays valid until `exp` unless the RS checks with the AS, so short lifetimes are the control.

## Refresh tokens: rotation and reuse detection

A refresh token carries the full granted scope and is not tied to one resource, so theft lets the attacker mint access tokens. RFC 9700 says refresh tokens for public clients must be sender-constrained or rotated. In RFC 9700's **rotation** every refresh returns a new refresh token and invalidates the old one, remembering the relationship. If the old token is presented again, either the thief or the real client has it. The AS cannot tell which, so it revokes the active token and the client must obtain a new grant. Refresh tokens should also expire after inactivity.

<!-- diagram:oauth-refresh-rotation -->
<div class="l03b-wrap" style="position:relative">
<input type="checkbox" id="l03b-pause" class="l03b-cb" /><label for="l03b-pause" class="l03b-btn"><span class="l03b-off">Pause animation</span><span class="l03b-on">Play animation</span></label>
<div class="l03b-box" style="overflow-x:auto">
<svg class="l03b-flow" viewBox="0 0 760 669" role="img" aria-labelledby="l03b-t l03b-d" style="width:760px;max-width:100%;min-width:699px;height:auto;display:block;margin:0 auto">
<title id="l03b-t">Refresh token rotation (RFC 9700) and reuse detection</title>
<desc id="l03b-d">Three parties: the client, the authorization server and whoever presents an old refresh token, who may be a thief or the real client. This is RFC 9700's rotation. Step 1: the client sends its refresh token with grant_type=refresh_token and the AS returns a new access token and a new refresh token. Step 2: the AS invalidates the old refresh token and remembers the relationship. Step 3: the old refresh token is presented again. Step 4: the AS cannot tell the thief from the real client, so it revokes the active token. Step 5: the client must obtain a new grant. In Okta the log event for reuse is app.oauth2.as.token.detect_reuse for a custom authorization server. The diagram highlights each step in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
<style>
svg.l03b-flow{--ink:light-dark(#000000,#ffffff)}
.l03b-box{fill:var(--panel);stroke:var(--border-strong);stroke-width:1.5}
.l03b-hot{fill:var(--panel);stroke:var(--accent);stroke-width:2.5}
.l03b-ttl{fill:var(--ink);font:600 15px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l03b-sub{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l03b-life{stroke:var(--border-strong);stroke-width:1.5;stroke-dasharray:4 5}
.l03b-front{stroke:var(--accent);stroke-width:2;fill:none}
.l03b-back{stroke:var(--muted);stroke-width:2;stroke-dasharray:7 5;fill:none}
.l03b-bad{stroke:var(--bad);stroke-width:2;fill:none}
.l03b-main{fill:var(--ink);font:600 13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l03b-badt{fill:var(--ink)}
.l03b-dim{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l03b-badge{fill:var(--accent)}
.l03b-b-back{fill:var(--muted)}
.l03b-b-bad{fill:var(--bad)}
.l03b-b-good{fill:var(--good)}
.l03b-bt{fill:var(--on-accent);font:700 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l03b-note{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l03b-note-good{fill:var(--good-bg);stroke:var(--good);stroke-width:1.5}
.l03b-note-bad{fill:var(--bad-bg);stroke:var(--bad);stroke-width:1.5}
.l03b-nt{fill:var(--ink);font:500 12.5px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l03b-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:28s;animation-timing-function:linear;animation-iteration-count:infinite}
.l03b-pk.l03b-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.l03b-pk.l03b-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.l03b-wrap{margin:20px 0}
@media (min-width:801px){.l03b-wrap{margin-left:-44px;margin-right:-44px}}
.l03b-g rect,.l03b-g line,.l03b-g path:not(.l03b-gl){opacity:.5;animation-duration:28s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.l03b-flow:hover .l03b-g rect,svg.l03b-flow:hover .l03b-g line,svg.l03b-flow:hover .l03b-g path:not(.l03b-gl),svg.l03b-flow:hover .l03b-pk{animation-play-state:paused}
.l03b-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.l03b-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.l03b-btn:hover{background:var(--hover)}
.l03b-cb:focus-visible + .l03b-btn{outline:2px solid var(--accent);outline-offset:2px}
.l03b-cb:checked + .l03b-btn .l03b-off,.l03b-cb:not(:checked) + .l03b-btn .l03b-on{display:none}
.l03b-cb:checked ~ .l03b-box .l03b-g rect,.l03b-cb:checked ~ .l03b-box .l03b-g line,.l03b-cb:checked ~ .l03b-box .l03b-g path:not(.l03b-gl),.l03b-cb:checked ~ .l03b-box .l03b-pk{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.l03b-g rect,.l03b-g line,.l03b-g path:not(.l03b-gl){animation:none;opacity:1}.l03b-pk{animation:none;display:none}.l03b-btn{display:none}}
@keyframes l03b-g0{0%{opacity:1}21.429%{opacity:1}21.439%,100%{opacity:.5}}
@keyframes l03b-p0{0%,-0.01%{opacity:0;transform:translateX(0)}0%{opacity:1;transform:translateX(0)}17.143%{opacity:1;transform:translateX(-236px)}21.429%{opacity:1;transform:translateX(-236px)}21.439%,100%{opacity:0;transform:translateX(-236px)}}
.l03b-g0 rect,.l03b-g0 line,.l03b-g0 path:not(.l03b-gl){animation-name:l03b-g0}.l03b-p0{animation-name:l03b-p0}
@keyframes l03b-g1{0%,21.419%{opacity:.5}21.429%{opacity:1}35.714%{opacity:1}35.724%,100%{opacity:.5}}
.l03b-g1 rect,.l03b-g1 line,.l03b-g1 path:not(.l03b-gl){animation-name:l03b-g1}
@keyframes l03b-g2{0%,35.704%{opacity:.5}35.714%{opacity:1}57.143%{opacity:1}57.153%,100%{opacity:.5}}
@keyframes l03b-p2{0%,35.704%{opacity:0;transform:translateX(0)}35.714%{opacity:1;transform:translateX(0)}52.857%{opacity:1;transform:translateX(-236px)}57.143%{opacity:1;transform:translateX(-236px)}57.153%,100%{opacity:0;transform:translateX(-236px)}}
.l03b-g2 rect,.l03b-g2 line,.l03b-g2 path:not(.l03b-gl){animation-name:l03b-g2}.l03b-p2{animation-name:l03b-p2}
@keyframes l03b-g3{0%,57.133%{opacity:.5}57.143%{opacity:1}71.429%{opacity:1}71.439%,100%{opacity:.5}}
.l03b-g3 rect,.l03b-g3 line,.l03b-g3 path:not(.l03b-gl){animation-name:l03b-g3}
@keyframes l03b-g4{0%,71.419%{opacity:.5}71.429%{opacity:1}85.714%{opacity:1}85.724%,100%{opacity:.5}}
.l03b-g4 rect,.l03b-g4 line,.l03b-g4 path:not(.l03b-gl){animation-name:l03b-g4}
@keyframes l03b-g5{0%,85.704%{opacity:.5}85.714%{opacity:1}100%{opacity:1}100.01%,100%{opacity:.5}}
.l03b-g5 rect,.l03b-g5 line,.l03b-g5 path:not(.l03b-gl){animation-name:l03b-g5}
</style>
<defs>
<marker id="l03b-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="l03b-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="l03b-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<line class="l03b-life" x1="110" y1="72" x2="110" y2="617"/>
<line class="l03b-life" x1="380" y1="72" x2="380" y2="617"/>
<line class="l03b-life" x1="650" y1="72" x2="650" y2="617"/>
<rect class="l03b-box" x="20" y="10" width="180" height="62" rx="10"/><text class="l03b-ttl" x="110" y="36">Client</text><text class="l03b-sub" x="110" y="56">holds a refresh token</text>
<rect class="l03b-hot" x="290" y="10" width="180" height="62" rx="10"/><text class="l03b-ttl" x="380" y="36">Authorization server</text><text class="l03b-sub" x="380" y="56">remembers the relationship</text>
<rect class="l03b-box" x="560" y="10" width="180" height="62" rx="10"/><text class="l03b-ttl" x="650" y="36">Old token holder</text><text class="l03b-sub" x="650" y="56">thief or the real client</text>
<g class="l03b-g l03b-g0">
<text class="l03b-main" x="245" y="108">grant_type=refresh_token</text>
<text class="l03b-dim" x="245" y="124">sends the current refresh token</text>
<line class="l03b-front" x1="124" y1="138" x2="366" y2="138" marker-end="url(#l03b-m-front)"/>
<circle class="l03b-badge l03b-b-front" cx="110" cy="138" r="12"/><text class="l03b-bt" x="110" y="142.5">1</text>
<text class="l03b-main" x="245" y="178">a new access token and</text>
<text class="l03b-dim" x="245" y="194">a new refresh token</text>
<line class="l03b-front" x1="366" y1="208" x2="124" y2="208" marker-end="url(#l03b-m-front)"/>
</g>
<g class="l03b-g l03b-g1">
<rect class="l03b-note" x="243" y="242" width="274" height="48" rx="8"/>
<text class="l03b-nt" x="380" y="263">the old refresh token is invalidated;</text>
<text class="l03b-nt" x="380" y="280">the AS remembers the relationship</text>
<circle class="l03b-badge l03b-b-plain" cx="243" cy="266" r="12"/><text class="l03b-bt" x="243" y="270.5">2</text>
</g>
<g class="l03b-g l03b-g2">
<text class="l03b-main l03b-badt" x="515" y="324">presents the old</text>
<text class="l03b-dim" x="515" y="340">refresh token again</text>
<line class="l03b-bad" x1="636" y1="354" x2="394" y2="354" marker-end="url(#l03b-m-bad)"/>
<circle class="l03b-badge l03b-b-bad" cx="650" cy="354" r="12"/><text class="l03b-bt" x="650" y="358.5">3</text>
</g>
<g class="l03b-g l03b-g3">
<rect class="l03b-note-bad" x="250" y="388" width="261" height="48" rx="8"/>
<text class="l03b-nt" x="380" y="409">cannot tell the thief from the real</text>
<text class="l03b-nt" x="380" y="426">client: revokes the active token</text>
<circle class="l03b-badge l03b-b-bad" cx="250" cy="412" r="12"/><text class="l03b-bt" x="250" y="416.5">4</text>
</g>
<g class="l03b-g l03b-g4">
<rect class="l03b-note" x="20" y="464" width="181" height="31" rx="8"/>
<text class="l03b-nt" x="110" y="485">must obtain a new grant</text>
<circle class="l03b-badge l03b-b-plain" cx="20" cy="480" r="12"/><text class="l03b-bt" x="20" y="484.0">5</text>
</g>
<g class="l03b-g l03b-g5">
<rect class="l03b-note-good" x="246" y="523" width="267" height="48" rx="8"/>
<text class="l03b-nt" x="380" y="544">Okta log event on reuse (custom AS):</text>
<text class="l03b-nt" x="380" y="561">app.oauth2.as.token.detect_reuse</text>
</g>
<circle class="l03b-pk l03b-p0" cx="360" cy="208" r="5.5"/>
<circle class="l03b-pk l03b-p2 l03b-pkbad" cx="630" cy="354" r="5.5"/>
<line class="l03b-front" x1="40" y1="645" x2="70" y2="645"/>
<text class="l03b-dim" x="78" y="649" style="text-anchor:start">refresh request or response</text>
<line class="l03b-bad" x1="284" y1="645" x2="314" y2="645"/>
<text class="l03b-dim" x="322" y="649" style="text-anchor:start">the old token reused</text>
<rect class="l03b-note-good" x="484" y="637" width="22" height="16" rx="4"/>
<text class="l03b-dim" x="514" y="649" style="text-anchor:start">where to look in the logs</text>
</svg>
</div>
</div>
<!-- /diagram:oauth-refresh-rotation -->

The first refresh is normal; the second use of the same old token is the signal. The badges number this diagram's own hops and notes (1 to 5), not the steps of the authorization code flow. This is RFC 9700's rotation; the Okta paragraph below says Okta's behaviour differs.

Per Okta's refresh-token guide: with the Refresh Token grant enabled, SPAs rotate by default and mobile and web apps use persistent tokens. Reuse detection invalidates the most recently issued refresh token and all access tokens issued since the user authenticated. A grace period (default 30 seconds, 0 to 60) keeps the previous token valid for clients on poor networks. Log events: `app.oauth2.as.token.detect_reuse` (custom AS) and `app.oauth2.token.detect_reuse` (org AS). The documented default refresh token lifetime is Unlimited, so set one; the same page says a refresh token expires after seven days if it has not been used. It also says whether Okta returns a new refresh token with a new access token depends on the refresh token lifetime setting: while the lifetime has not expired, only a new access token comes back. That differs from the every-refresh rotation described above, so confirm in your own org.

## What breaks

- **Loose redirect URIs.** RFC 9700 shows a registered `https://*.somesite.example/*` accepting `https://attacker.example/.somesite.example`. Even correct wildcards fail to a subdomain takeover.
- **No PKCE on a public client**: an intercepted code is redeemable by the interceptor.
- **Tokens in URLs.** RFC 9700 says clients must not send access tokens in a query parameter.
- **Open redirectors** on a client or AS can leak codes. **Over-broad scopes** and **client secrets in public clients** are the other repeat offenders.

## Your task

Reproduce parts 1 and 2 on your own machine; both were run while this lesson was written. Part 3 was not.

**Part 1: build and verify a PKCE pair.** Hash the RFC 7636 Appendix B verifier first, to prove your pipeline matches the RFC, then make a fresh pair (OpenSSL 3.6.3 here):

```sh
printf '%s' dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk | openssl dgst -sha256 -binary | openssl base64 -A | tr '+/' '-_' | tr -d '='; echo
V=$(openssl rand -base64 32 | tr '+/' '-_' | tr -d '=\n')
C=$(printf '%s' "$V" | openssl dgst -sha256 -binary | openssl base64 -A | tr '+/' '-_' | tr -d '=')
echo "verifier  ($(printf %s "$V" | wc -c | tr -d ' ') chars): $V"
echo "challenge ($(printf %s "$C" | wc -c | tr -d ' ') chars): $C"
```

Output of one run (the pair is a throwaway sample; yours will differ, and both values should be 43 characters):

```
E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM
verifier  (43 chars): fYSaK2hcKKD0xXvzY88Tv1XRG_04JzLX5WE_L6e-5mU
challenge (43 chars): 2i4u6olXjljpL7rlLjVjRH6hdW3mm276CuGynD0WNrA
```

The first line is exactly the challenge printed in RFC 7636 Appendix B. The `tr` steps turn standard base64 into base64url and drop the padding.

**Part 2: read an AS's advertised PKCE support.** Run this and read the answer (run 2026-10-06):

```sh
curl -sS https://accounts.google.com/.well-known/openid-configuration | jq -c '{code_challenge_methods_supported, authorization_response_iss_parameter_supported}'
```

```
{"code_challenge_methods_supported":["plain","S256"],"authorization_response_iss_parameter_supported":true}
```

That server accepts `plain`. Support on the server is not permission to use it: your clients still send S256. Repeat the query against your own AS's metadata URL.

**Part 3, written from the docs, not run against a live tenant:** in a dev tenant, create a test app with the authorization code grant, send `/authorize` without a `code_challenge`, and record whether it is refused. The outcome depends on app settings, which this lesson did not verify.

Next: OpenID Connect and how to validate the ID token.
