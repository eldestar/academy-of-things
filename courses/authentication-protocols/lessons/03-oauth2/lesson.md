# OAuth 2.0

You have configured OIDC and SAML apps. This lesson covers the layer underneath OIDC: how an app is given limited, revocable access to an API on a user's behalf. It covers the flow you will see in most tenants, the settings that matter, and what breaks. Facts checked 2026-10-06.

Standards cited: RFC 6749 and 6750 (2012), RFC 7636 (PKCE), RFC 7009 (revocation), RFC 7662 (introspection), RFC 8628 (device grant), RFC 8707 (resource indicators), RFC 9068 (JWT access tokens) and RFC 9700 (BCP 240, January 2025, which updates 6749, 6750 and 6819). **OAuth 2.1** is not a standard: `draft-ietf-oauth-v2-1-16`, dated 3 September 2026, is an active Internet-Draft in the OAuth working group. Treat it as the direction of travel, not as a requirement.

## Delegation, not login

The four roles (RFC 6749, section 1.1): the **resource owner** (the user), the **client** (the app), the **authorization server** (AS, which authenticates the owner and issues tokens; your IdP tenant can be one) and the **resource server** (RS, the API that accepts access tokens). A client is **confidential** if it can keep credentials secret (a server-side app) and **public** if it cannot (a native or browser app).

OAuth authorizes an app; it does not log anyone in. The AS does authenticate the user, but the client only receives an access token meant for the RS. The OAuth 2.1 draft says OAuth defines nothing for authenticating users, and that OpenID Connect builds on it for that (next lesson). Treating a valid token, or the result of a `/me` call, as proof of sign-in is outside the standard.

Consent has its own attack. In a **consent phishing** attack (the draft, section 7.9) an attacker registers a client and sends the victim a genuine authorization URL. The victim signs in normally, even with a phishing-resistant factor, and then approves the attacker's scopes. The draft says the AS should control client registration and the scopes a client may request.

## The authorization code flow with PKCE

<!-- diagram:oauth-code-pkce -->
<div style="position:relative;margin:20px 0">
<input type="checkbox" id="oa-pause" class="oa-cb" /><label for="oa-pause" class="oa-btn"><span class="oa-off">Pause animation</span><span class="oa-on">Play animation</span></label>
<div class="oa-box" style="overflow-x:auto">
<svg class="oa-flow" viewBox="0 0 760 858" role="img" aria-labelledby="oa-t oa-d" style="width:100%;min-width:640px;max-width:800px;height:auto;display:block;margin:0 auto">
<title id="oa-t">OAuth 2.0 authorization code flow with PKCE</title>
<desc id="oa-d">Three parties: the client app, the authorization server and the resource server. Step 1: the client redirects the user's browser to the authorization server with a code_challenge. Step 2: the user signs in and consents at the authorization server. Step 3: the authorization server redirects the browser back to the client's redirect URI with a code and the state value. Step 4: the client checks that the state matches the stored value, or relies on PKCE for CSRF protection where the authorization server is known to support it. Step 5: as a direct request rather than a browser redirect, the client posts the code and the code_verifier (and the redirect_uri if it was sent at step 1) to the token endpoint and receives an access token. A code stolen at step 3 is useless without the code_verifier. Step 6: the client calls the resource server with the access token. Step 7: the resource server checks that the token is genuine, meant for it, within its scope and not expired before serving the request. The diagram highlights each step in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
<style>
.oa-box{fill:var(--panel);stroke:var(--border-strong);stroke-width:1.5}
.oa-hot{fill:var(--panel);stroke:var(--accent);stroke-width:2.5}
.oa-ttl{fill:var(--text);font:600 15px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.oa-sub{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.oa-life{stroke:var(--border-strong);stroke-width:1.5;stroke-dasharray:4 5}
.oa-front{stroke:var(--accent);stroke-width:2;fill:none}
.oa-back{stroke:var(--muted);stroke-width:2;stroke-dasharray:7 5;fill:none}
.oa-bad{stroke:var(--bad);stroke-width:2;fill:none}
.oa-main{fill:var(--text);font:600 13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.oa-badt{fill:var(--bad-text)}
.oa-dim{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.oa-badge{fill:var(--accent)}
.oa-b-back{fill:var(--muted)}
.oa-b-bad{fill:var(--bad)}
.oa-b-good{fill:var(--good)}
.oa-bt{fill:var(--on-accent);font:700 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.oa-note{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.oa-note-good{fill:var(--good-bg);stroke:var(--good);stroke-width:1.5}
.oa-note-bad{fill:var(--bad-bg);stroke:var(--bad);stroke-width:1.5}
.oa-nt{fill:var(--body);font:12.5px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.oa-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:22s;animation-timing-function:linear;animation-iteration-count:infinite}
.oa-pk.oa-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.oa-pk.oa-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.oa-g{opacity:.45;animation-duration:22s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.oa-flow:hover .oa-g,svg.oa-flow:hover .oa-pk{animation-play-state:paused}
.oa-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.oa-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.oa-btn:hover{background:var(--hover)}
.oa-cb:focus-visible + .oa-btn{outline:2px solid var(--accent);outline-offset:2px}
.oa-cb:checked + .oa-btn .oa-off,.oa-cb:not(:checked) + .oa-btn .oa-on{display:none}
.oa-cb:checked ~ .oa-box .oa-g,.oa-cb:checked ~ .oa-box .oa-pk{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.oa-g{animation:none;opacity:1}.oa-pk{animation:none;display:none}.oa-btn{display:none}}
@keyframes oa-g0{0%{opacity:1}12.5%{opacity:1}12.51%,100%{opacity:.45}}
@keyframes oa-p0{0%,-0.01%{opacity:0;transform:translateX(0)}0%{opacity:1;transform:translateX(0)}12.5%{opacity:1;transform:translateX(236px)}12.51%,100%{opacity:0;transform:translateX(236px)}}
.oa-g0{animation-name:oa-g0}.oa-p0{animation-name:oa-p0}
@keyframes oa-g1{0%,12.49%{opacity:.45}12.5%{opacity:1}25%{opacity:1}25.01%,100%{opacity:.45}}
.oa-g1{animation-name:oa-g1}
@keyframes oa-g2{0%,24.99%{opacity:.45}25%{opacity:1}37.5%{opacity:1}37.51%,100%{opacity:.45}}
@keyframes oa-p2{0%,24.99%{opacity:0;transform:translateX(0)}25%{opacity:1;transform:translateX(0)}37.5%{opacity:1;transform:translateX(-236px)}37.51%,100%{opacity:0;transform:translateX(-236px)}}
.oa-g2{animation-name:oa-g2}.oa-p2{animation-name:oa-p2}
@keyframes oa-g3{0%,37.49%{opacity:.45}37.5%{opacity:1}50%{opacity:1}50.01%,100%{opacity:.45}}
.oa-g3{animation-name:oa-g3}
@keyframes oa-g4{0%,49.99%{opacity:.45}50%{opacity:1}62.5%{opacity:1}62.51%,100%{opacity:.45}}
@keyframes oa-p4{0%,49.99%{opacity:0;transform:translateX(0)}50%{opacity:1;transform:translateX(0)}62.5%{opacity:1;transform:translateX(-236px)}62.51%,100%{opacity:0;transform:translateX(-236px)}}
.oa-g4{animation-name:oa-g4}.oa-p4{animation-name:oa-p4}
@keyframes oa-g5{0%,62.49%{opacity:.45}62.5%{opacity:1}75%{opacity:1}75.01%,100%{opacity:.45}}
.oa-g5{animation-name:oa-g5}
@keyframes oa-g6{0%,74.99%{opacity:.45}75%{opacity:1}87.5%{opacity:1}87.51%,100%{opacity:.45}}
@keyframes oa-p6{0%,74.99%{opacity:0;transform:translateX(0)}75%{opacity:1;transform:translateX(0)}87.5%{opacity:1;transform:translateX(506px)}87.51%,100%{opacity:0;transform:translateX(506px)}}
.oa-g6{animation-name:oa-g6}.oa-p6{animation-name:oa-p6}
@keyframes oa-g7{0%,87.49%{opacity:.45}87.5%{opacity:1}100%{opacity:1}100.01%,100%{opacity:.45}}
.oa-g7{animation-name:oa-g7}
</style>
<defs>
<marker id="oa-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="oa-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="oa-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<line class="oa-life" x1="110" y1="72" x2="110" y2="806"/>
<line class="oa-life" x1="380" y1="72" x2="380" y2="806"/>
<line class="oa-life" x1="650" y1="72" x2="650" y2="806"/>
<rect class="oa-box" x="20" y="10" width="180" height="62" rx="10"/><text class="oa-ttl" x="110" y="36">Client app</text><text class="oa-sub" x="110" y="56">keeps the code_verifier</text>
<rect class="oa-hot" x="290" y="10" width="180" height="62" rx="10"/><text class="oa-ttl" x="380" y="36">Authorization server</text><text class="oa-sub" x="380" y="56">issues the tokens</text>
<rect class="oa-box" x="560" y="10" width="180" height="62" rx="10"/><text class="oa-ttl" x="650" y="36">Resource server</text><text class="oa-sub" x="650" y="56">the API</text>
<g class="oa-g oa-g0">
<text class="oa-main" x="245" y="108">redirect to /authorize</text>
<text class="oa-dim" x="245" y="124">client_id, redirect_uri, scope, state</text>
<text class="oa-dim" x="245" y="140">code_challenge, method S256</text>
<line class="oa-front" x1="124" y1="154" x2="366" y2="154" marker-end="url(#oa-m-front)"/>
<circle class="oa-badge oa-b-front" cx="110" cy="154" r="12"/><text class="oa-bt" x="110" y="158.5">1</text>
</g>
<g class="oa-g oa-g1">
<rect class="oa-note" x="253" y="188" width="254" height="48" rx="8"/>
<text class="oa-nt" x="380" y="209">user signs in and consents</text>
<text class="oa-nt" x="380" y="226">AS binds the challenge to the code</text>
<circle class="oa-badge oa-b-plain" cx="253" cy="212" r="12"/><text class="oa-bt" x="253" y="216.5">2</text>
</g>
<g class="oa-g oa-g2">
<text class="oa-main" x="245" y="270">redirect to your redirect_uri</text>
<text class="oa-dim" x="245" y="286">code and state</text>
<line class="oa-front" x1="366" y1="300" x2="124" y2="300" marker-end="url(#oa-m-front)"/>
<circle class="oa-badge oa-b-front" cx="380" cy="300" r="12"/><text class="oa-bt" x="380" y="304.5">3</text>
</g>
<g class="oa-g oa-g3">
<rect class="oa-note-good" x="32" y="334" width="155" height="48" rx="8"/>
<text class="oa-nt" x="110" y="355">check state matches</text>
<text class="oa-nt" x="110" y="372">(or rely on PKCE)</text>
<circle class="oa-badge oa-b-good" cx="32" cy="358" r="12"/><text class="oa-bt" x="32" y="362.5">4</text>
</g>
<g class="oa-g oa-g4">
<text class="oa-main" x="245" y="416">POST /token</text>
<text class="oa-dim" x="245" y="432">code, code_verifier, client_id</text>
<text class="oa-dim" x="245" y="448">redirect_uri if sent at step 1</text>
<line class="oa-back" x1="124" y1="462" x2="366" y2="462" marker-end="url(#oa-m-back)"/>
<circle class="oa-badge oa-b-back" cx="110" cy="462" r="12"/><text class="oa-bt" x="110" y="466.5">5</text>
<text class="oa-main" x="245" y="502">access token (maybe refresh token)</text>
<text class="oa-dim" x="245" y="518">or an error if the verifier differs</text>
<line class="oa-back" x1="366" y1="532" x2="124" y2="532" marker-end="url(#oa-m-back)"/>
</g>
<g class="oa-g oa-g5">
<rect class="oa-note-bad" x="266" y="566" width="228" height="48" rx="8"/>
<text class="oa-nt" x="380" y="587">a code stolen at step 3 fails:</text>
<text class="oa-nt" x="380" y="604">the thief has no code_verifier</text>
<circle class="oa-badge oa-b-bad" cx="266" cy="590" r="12"/><text class="oa-bt" x="266" y="594.5">!</text>
</g>
<g class="oa-g oa-g6">
<text class="oa-main" x="380" y="648">API request</text>
<text class="oa-dim" x="380" y="664">Authorization: Bearer &lt;token></text>
<line class="oa-back" x1="124" y1="678" x2="636" y2="678" marker-end="url(#oa-m-back)"/>
<circle class="oa-badge oa-b-back" cx="110" cy="678" r="12"/><text class="oa-bt" x="110" y="682.5">6</text>
</g>
<g class="oa-g oa-g7">
<rect class="oa-note-good" x="509" y="712" width="241" height="48" rx="8"/>
<text class="oa-nt" x="630" y="733">check the token:</text>
<text class="oa-nt" x="630" y="750">genuine, audience, scope, expiry</text>
<circle class="oa-badge oa-b-good" cx="509" cy="736" r="12"/><text class="oa-bt" x="509" y="740.5">7</text>
</g>
<circle class="oa-pk oa-p0" cx="130" cy="154" r="5.5"/>
<circle class="oa-pk oa-p2" cx="360" cy="300" r="5.5"/>
<circle class="oa-pk oa-p4 oa-pkback" cx="360" cy="532" r="5.5"/>
<circle class="oa-pk oa-p6 oa-pkback" cx="130" cy="678" r="5.5"/>
<line class="oa-front" x1="40" y1="834" x2="70" y2="834"/>
<text class="oa-dim" x="78" y="838" style="text-anchor:start">through the user's browser</text>
<line class="oa-back" x1="278" y1="834" x2="308" y2="834"/>
<text class="oa-dim" x="316" y="838" style="text-anchor:start">direct request, not a redirect</text>
<rect class="oa-note-good" x="542" y="826" width="22" height="16" rx="4"/>
<text class="oa-dim" x="572" y="838" style="text-anchor:start">a check to perform</text>
</svg>
</div>
</div>
<!-- /diagram:oauth-code-pkce -->

Solid arrows pass through the user's browser; dashed arrows are direct requests, not browser redirects. The numbers match the list below, and the red note marks where a stolen code fails.

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
- **Refresh token**: `grant_type=refresh_token`. The new scope cannot exceed the original.
- **Avoid implicit** (`response_type=token`): RFC 9700 says clients should not use it. Tokens in the redirect URL leak through history and logs, and cannot be sender-constrained.
- **Avoid resource owner password**: RFC 9700 says it must not be used. It hands credentials to the client and is not designed to work with MFA.

The OAuth 2.1 draft drops both grants and `plain`, makes PKCE part of the code grant, and drops bearer tokens in query strings.

## Tokens: who has to understand what

- **Client**: opaque. RFC 9068 says the client must not inspect an access token, because the AS or RS may change its format. Microsoft's Entra documentation says clients should not validate access tokens, and that tokens for Microsoft Graph may not be JWTs. Okta's documentation says tokens from the org authorization server are not meant for your apps to validate and may change without notice; use a custom authorization server for your own APIs (in production this needs the API Access Management product).
- **RS**: it must understand the token, in one of two ways. **Introspection** (RFC 7662): POST the token; the JSON answer has a required boolean `active`; the endpoint must itself require authorization, and responses may be cached at the cost of freshness. **JWT** (RFC 9068): check `typ` is `at+jwt`, the signature (never `alg` `none`), `iss`, that `aud` names this RS, and `exp`. `typ` marks the JWT as an access token rather than an ID token; it is the same for every API, so only `aud` says which API a token is for.
- **Errors** (RFC 6750): `invalid_token` should be 401, `insufficient_scope` 403 and `invalid_request` 400.
- **Audience**: the RS must refuse tokens meant for another RS. The client can say where it will use the token with the `resource` parameter (RFC 8707, an absolute URI; error `invalid_target`). Scope is typically about what access is wanted, not where it will be used (RFC 8707); some deployments encode the resource in the scope, but `resource` is the standard way to say where.
- **Lifetime and revocation**: RFC 6750 says tokens should live one hour or less. RFC 7009 revocation (`POST` with `token`) returns 200 even for an invalid token. Refresh tokens must be revocable and access tokens should be. A self-contained JWT stays valid until `exp` unless the RS checks with the AS, so short lifetimes are the control.

## Refresh tokens: rotation and reuse detection

A refresh token carries the full granted scope and is not tied to one resource, so theft lets the attacker mint access tokens. RFC 9700 says refresh tokens for public clients must be sender-constrained or rotated. In RFC 9700's **rotation** every refresh returns a new refresh token and invalidates the old one, remembering the relationship. If the old token is presented again, either the thief or the real client has it. The AS cannot tell which, so it revokes the active token and the client must obtain a new grant. Refresh tokens should also expire after inactivity.

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
