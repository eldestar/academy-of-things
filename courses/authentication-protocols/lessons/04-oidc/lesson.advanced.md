# OpenID Connect and JWT validation

You are building or reviewing the relying-party side: a login callback, an API gateway, a logout endpoint. This lesson goes through what OpenID Connect Core 1.0 fixes, what it leaves to you, and the attack classes a validator has to close. Facts checked 2026-10-06 against Core, Discovery 1.0, the RP-Initiated, Front-Channel and Back-Channel Logout specs, RFC 7519, 7515, 7517, 8725, 9700, and Okta and Microsoft Learn docs for the product claims.

## What the spec fixes, and what it leaves to you

The code flow is: authentication request (`openid` scope, `state`, optional `nonce`, and `code_challenge` with `code_challenge_method=S256` for a public client), redirect with `code`, direct token request (client authentication, or `code_verifier` for a public client), token response with `id_token` and `access_token`, ID token validation, optional UserInfo.

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

1. Authentication request. `redirect_uri` is compared by simple string comparison to a pre-registered value. `nonce` is optional here, but if sent, the ID token MUST carry it and the client MUST check it. RFC 9700 section 2.1.1: public clients MUST use PKCE, and PKCE is RECOMMENDED for confidential clients; a confidential OIDC client MAY use `nonce` instead, with the additional precautions of its section 4.5.3.2. Whichever is used MUST be transaction-specific and bound to the client and user agent that started it.
2. Callback. The client checks `state`.
3. Token request. A confidential client authenticates; a public client sends the PKCE `code_verifier`, which the OP checks against the `code_challenge` (RFC 9700: it MUST enforce this when a challenge was sent, and accept a verifier only if a challenge was present). The response MUST carry `Cache-Control: no-store`.
4. ID token validation (section 3.1.3.7).
5. UserInfo. Its `sub` MUST equal the ID token's `sub`, else discard the response; the ID token is the authority.

Fixed by the spec: ID tokens MUST be signed (a JWS); `alg: none` MUST NOT be used unless the response type returns no ID token from the authorization endpoint and the client asked for `none` at registration; `iss` is an https URL with no query or fragment; `sub` is at most 255 ASCII characters, case-sensitive; signing keys come from the issuer, and ID tokens SHOULD NOT use the `jku`, `x5u`, `x5c` or `jwk` headers; keys are communicated through discovery and registration.

Left to you: the `iat` window ("client specific"), how to detect nonce replay, clock leeway, and `acr` meaning. `azp` appears only with extensions, and implementations not using them are encouraged to ignore it. For MAC algorithms (HS256) the key is the `client_secret`, and behaviour with a multi-valued `aud` is unspecified; do not allow HS256 for tokens you verify with a public key.

**The TLS exception.** For an ID token received directly from the token endpoint, Core says TLS server validation MAY replace checking the signature. Treat that as valid only for that one hop. A token that was forwarded, stored, read from a cookie or sent by a client must have its signature verified.

**Implicit and hybrid.** Implicit returns tokens in the authorization response and requires `nonce`. Hybrid `code id_token` requires `nonce` and `c_hash` (the left half of the code's hash, so the client can detect code substitution); `code id_token token` adds `at_hash`. RFC 9700 section 2.1.2 says clients SHOULD NOT use response types that issue access tokens in the authorization response and names `code id_token` as an alternative, because the token endpoint still issues the access token. For `id_token` and `code id_token` the ID token crosses the front channel.

## Attacks the validator must close

- **Algorithm confusion.** RFC 8725 section 2.1: `alg` can be changed to `none`, or RS256 changed to HS256 so the RSA public key is used as the HMAC secret. Mitigation (sections 3.1 and 3.2): the caller specifies the allowed algorithms, the library uses no others, and each key is used with exactly one algorithm. RFC 7515 section 5.2: a JWS whose algorithm is not acceptable to the application should be treated as invalid even if its signature validates. The forger writes the whole token, claims included, so `iss` and `aud` checks cannot compensate. Core makes RS256 the default `alg` (Discovery requires OPs to list it), but a default does not stop a verifier believing the header.
- **Header-driven lookups.** `kid` is a hint, and RFC 7517 says keys in a set SHOULD have distinct `kid` values, not that they must. Sanitise it against SQL or LDAP injection; never follow `jku` or `x5u` URLs blindly (SSRF), per RFC 8725 section 3.10.
- **Substitution.** Wrong `aud`, wrong `iss`, and cross-JWT confusion: RFC 8725 sections 2.7, 2.8, 3.9, 3.12. If one issuer issues several kinds of JWT, your validation rules MUST be mutually exclusive: distinct `typ`, required claims, keys, or `aud` per kind. Logout tokens show the pattern: `typ` `logout+jwt` is recommended and `nonce` is prohibited, so a logout token is not a valid ID token.
- **Loose `email_verified`.** It means the OP took steps to confirm control; the method depends on the parties' agreement. Never link or merge accounts on it alone.
- **Front-channel exposure.** Implicit and hybrid put tokens where the user agent and its scripts can see them.

## JWKS, `kid` and rotation as a cache design

Core section 10.1.1: the signer publishes a JWK Set at `jwks_uri`, names the signing key by `kid`, adds new keys ahead of use, and SHOULD keep recently decommissioned keys published for a reasonable time. The verifier re-fetches on an unfamiliar `kid`. Okta says to cache per Cache-Control, that rotation is currently four times a year and can change without notice, and that hardcoded keys can fail.

Design advice (mine, not from the specs): do not answer an unknown `kid` by trying every cached key, since a newly published key is not in the cache; treat the JWKS as a TTL cache plus a refresh-on-miss, and put a cooldown on refresh-on-miss. Without one, anyone can send tokens with random `kid` values and make you fetch the issuer's JWKS on every request. Fetch only from the configured issuer's `jwks_uri`; if a refresh fails, keep serving from the cache while it is within its TTL, and reject any token whose `kid` you cannot resolve.

## Subjects, pairwise identifiers and claim size

`iss` plus `sub` is the only guaranteed unique key (section 5.7); `email`, `preferred_username` and `name` are not unique identifiers. Core section 8 defines `public` and `pairwise` subject types: pairwise gives each client a different `sub`, computed per Sector Identifier (the host of the registered `redirect_uri`, or the host of a `sector_identifier_uri`, which is mandatory when redirect URIs span several hosts), and it must not be reversible by anyone but the OP. Microsoft documents that the Entra `sub` is pairwise per application ID, while `oid` is the same across apps and `tid` identifies the tenant; use `oid` plus `tid` to share data across services. Entra also warns `email` is mutable and not guaranteed correct.

Claim bloat: Core lets claims arrive in the ID token or from UserInfo, so my advice, not the spec's, is to keep volatile or large ones (groups) out of the ID token where you can. Entra caps `groups` at 200 for JWTs (150 for SAML) and, above that, omits it and emits an overage claim, so the app must call Microsoft Graph. An authorization check that reads a missing `groups` claim as "no groups" is a bug.

## Several issuers

RFC 8725 section 3.8: the application MUST validate that the keys used belong to the issuer. Keep an allowlist of issuers, each with its own `jwks_uri`, expected `aud` and algorithms; never fetch keys from the URL named by an unverified token's `iss` (my reading of those sections; section 2.9 says claims are SSRF vectors). Compare the `issuer` in metadata with the URL you fetched it from. For Entra multi-tenant apps, Microsoft says to use the GUID in `iss` to restrict which tenants may sign in.

## Logout design

Back-channel logout: the OP POSTs `logout_token` (form-encoded) to a registered URI. Validate it like an ID token (`none` forbidden), then require `events` containing `http://schemas.openid.net/event/backchannel-logout`, either `sub` or `sid`, and no `nonce`. Checking `jti` for replay is optional. With `sid`, end that session; with only `sub`, end all of that user's sessions at the app. Answer 200 on success, 400 on invalid or failed. Refresh tokens issued without `offline_access` SHOULD be revoked. The OP should not retransmit except after recoverable errors, so make the handler idempotent: a user who is already logged out counts as success. Limits: the URI must be reachable from the OP, an ID token already issued stays valid until `exp`, and Core section 16.18 notes access tokens may not be revocable. The spec describes delivery and the app's actions, and I found no list of events that make an OP send one, so whether an admin action does is OP-specific (not verified for Okta or Entra).

Front-channel logout renders the registered URI in an iframe, and browsers that block third-party content can defeat it. RP-initiated logout: the OP SHOULD accept an expired `id_token_hint` while the session is current or recent, and treats a mismatched `sid` as suspect.

## Your task

Written and run in this sandbox with Python and the `cryptography` package. Build `validate()`, then mint these tokens with throwaway RSA keys (sample issuer `https://idp.example.com`, client `lab-client-123`) and confirm each is rejected: wrong `aud`; extra untrusted audience; wrong `iss`; expired 120 s ago with 60 s leeway; wrong nonce; tampered payload; `alg: none`; HS256 using the public key PEM as secret; unknown `kid`.

```python
import base64, json, time
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
unb64 = lambda s: base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))
ISS, AUD, ALLOWED = "https://idp.example.com", "lab-client-123", {"RS256"}

def validate(tok, fetch_jwks, nonce, leeway=60):    # fetch_jwks(force) -> {kid: public key}
    h, p, s = tok.split(".")
    hdr = json.loads(unb64(h))
    if hdr.get("alg") not in ALLOWED:                       # alg allowlist, never the token's say-so
        raise ValueError(f"alg {hdr.get('alg')!r} not allowed")
    keys = fetch_jwks(False)
    if hdr.get("kid") not in keys:
        keys = fetch_jwks(True)                              # unfamiliar kid: refetch once
    if hdr.get("kid") not in keys:
        raise ValueError("unknown kid")
    keys[hdr["kid"]].verify(unb64(s), f"{h}.{p}".encode(), padding.PKCS1v15(), hashes.SHA256())
    c = json.loads(unb64(p))
    if c.get("iss") != ISS: raise ValueError("iss mismatch")
    aud = [c["aud"]] if isinstance(c.get("aud"), str) else c.get("aud", [])
    if AUD not in aud or set(aud) - {AUD}: raise ValueError("aud mismatch")
    if time.time() >= c["exp"] + leeway: raise ValueError("expired")
    if c.get("nonce") != nonce: raise ValueError("nonce mismatch")
    return c
```

Real output from my run (my own harness printed these lines; the extra-audience case and two lines about the believes-the-header validator are omitted here). The JWKS fetch sequence was `[False, True]`: a cache hit, then one forced refresh.

```
good token                         -> accepted, sub=u-1001
wrong aud                          -> rejected: ValueError: aud mismatch
wrong iss                          -> rejected: ValueError: iss mismatch
expired 120s ago (leeway 60s)      -> rejected: ValueError: expired
expired 30s ago (inside leeway)    -> accepted, sub=u-1001
wrong nonce                        -> rejected: ValueError: nonce mismatch
tampered payload, old signature    -> rejected: InvalidSignature:
real validator, alg=none           -> rejected: ValueError: alg 'none' not allowed
real validator, HS256 w/ public key -> rejected: ValueError: alg 'HS256' not allowed
new kid k2, cache only has k1      -> accepted, sub=u-1001
unknown kid k9                     -> rejected: ValueError: unknown kid
```

A validator that trusts the header's `alg` accepts both the `none` and the HS256 forgery (I confirmed this with a separate, unshown naive verifier). Note the sketch above refreshes on every unknown `kid`; add the cooldown. Next: SCIM.
