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

1. The app redirects the browser to the OP's authorization endpoint (from discovery) with `response_type=code`, `client_id`, `redirect_uri`, `scope=openid ...`, `state`, and a `nonce`. The `redirect_uri` must exactly match a pre-registered value. `state` is recommended by OIDC and ties the callback to the browser (CSRF); RFC 9700 requires some CSRF protection here, a one-time `state` or PKCE where you know the OP supports it (lesson 3). `nonce` is optional in the code flow and binds the ID token to this client session. A public client (SPA, native app) must also send `code_challenge` and `code_challenge_method=S256` (PKCE, lesson 3). RFC 9700 section 2.1.1 recommends PKCE for confidential clients too, and lets a confidential OIDC client use `nonce` instead only with extra precautions.
2. After sign-in the OP redirects back with `code` and `state`. Verify `state` first.
3. The app posts the code to the token endpoint, server to server. A confidential client authenticates itself; a public client sends the PKCE `code_verifier` instead (lesson 3). The response carries `id_token` and `access_token` and must send `Cache-Control: no-store`.
4. The app validates the ID token, then starts its own session.
5. Optionally it calls UserInfo. The UserInfo `sub` must exactly match the ID token's `sub`, or the response must not be used.

**Implicit is legacy; hybrid needs care.** Implicit (`id_token`, `id_token token`) returns tokens in the authorization response, never touching the token endpoint, which can expose them to the user and to anything with access to the user agent. Implicit requires `nonce`. RFC 9700 section 2.1.2 says clients SHOULD NOT use response types that issue access tokens in the authorization response, and names `code id_token` as an acceptable alternative. Hybrid `code id_token` is not deprecated, but the ID token still crosses the front channel. If an app registration says implicit, ask why.

## Validating the ID token

Do these in order, and trust no claim until the signature has passed (Core lets TLS validation replace the signature check only for an ID token received directly from the token endpoint; any other ID token needs the signature check). RFC 7519 section 7.2 says step order does not matter where steps have no dependencies, so the order below is a teaching order, not a spec order.

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

## Identity claims you can trust

`sub` is locally unique and never reassigned within an issuer; `iss` plus `sub` is the only guaranteed unique identifier (Core section 5.7); in Entra `sub` is pairwise per application, so Microsoft's guidance is `tid` plus `oid` (lesson 1). `email`, `preferred_username` and `name` MUST NOT be used as unique identifiers: an issuer may reuse an email for a different person later. `email_verified: true` means the OP took steps to confirm control of the address at that time; how depends on the arrangement between the parties, so do not link or merge accounts on it without knowing how your OP verifies. Microsoft says the Entra `email` claim is mutable and not guaranteed correct, and must never be used for authorization or to store data per user.

## Logout and OIDC versus SAML

Sign-out is not token revocation. There are three common mechanisms. An ID token already issued stays valid until `exp`, and Core section 16.18 notes access tokens might not be revocable and should be short-lived; back-channel logout does ask the app to revoke refresh tokens issued without `offline_access`.

- **RP-initiated**: the app sends the browser to the OP's `end_session_endpoint` with `id_token_hint` (recommended), a pre-registered `post_logout_redirect_uri` and `state`. It is the app asking the OP to end the OP session, and only when someone signs out; the OP SHOULD ask whether to log out there too. Informing the other apps is the job of front-channel or back-channel logout.
- **Front-channel**: the OP renders each app's registered logout URI in an iframe. Browsers that block third-party content can stop it working, and the spec recommends defensive code to detect that.
- **Back-channel**: the OP POSTs a signed Logout Token straight to the app's registered URI, and the app must end the session named by the token's `sub` or `sid`. It does not depend on the browser, but the endpoint must be reachable from the OP, so it cannot sit behind a firewall or NAT for a public OP. The OP sends it when it logs a session out; whether your OP does so when an admin ends a session or terminates an account is OP-specific (not verified here for Okta or Entra), so test it.

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
