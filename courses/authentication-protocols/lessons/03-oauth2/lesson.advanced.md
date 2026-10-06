# OAuth 2.0

You are designing or reviewing the authorization-server (AS) or resource-server (RS) side. This lesson assumes you know the code flow and covers spec-level behaviour, the attack classes RFC 9700 names, token design, sender-constraining, and the places where the standards leave you a choice. Facts checked 2026-10-06.

## Where the standards stand

- **Core**: RFC 6749 and RFC 6750 (2012). **RFC 9700** is BCP 240 (January 2025); it updates RFC 6749, 6750 and 6819 and deprecates modes it considers insecure. Cite it for requirements.
- **OAuth 2.1**: `draft-ietf-oauth-v2-1-16`, dated 3 September 2026, is an active Internet-Draft and a working-group document, not an RFC. Its abstract says it would replace RFC 6749 and 6750. It consolidates RFC 6749, native apps, PKCE, the browser-based-apps draft and RFC 9700. The IETF says to cite drafts only as work in progress. Treat it as direction.
- Its listed changes: PKCE is part of the code grant, redirect URIs are matched exactly, implicit and resource owner password are omitted, bearer tokens in query strings are omitted, `plain` is removed, refresh tokens for public clients must be sender-constrained or one-time use, and `redirect_uri` leaves the token request. RFC 6749 requires `redirect_uri` at the token endpoint if it was sent at `/authorize`, so an AS serving both generations must still accept and enforce it for legacy clients.
- The draft states that OAuth is not an authentication protocol, because it defines no components for authenticating users; OpenID Connect supplies them.

## The authorization code flow with PKCE

At spec level the flow is the following.

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

1. Client to AS, through the browser: `response_type=code`, `client_id`, `redirect_uri`, `scope`, `state`, `code_challenge`, `code_challenge_method`.
2. The AS authenticates the user, obtains consent, and records the challenge and method with the code.
3. The AS redirects to `redirect_uri` with `code` and `state`.
4. The client verifies `state` (or relies on PKCE for CSRF where the AS is known to support it).
5. Client to AS, direct: `code`, `code_verifier`, `redirect_uri` if it was sent at step 1, and client authentication or `client_id`. Mismatch: `invalid_grant`.
6. Client to RS: bearer token.
7. The RS validates the token.

- **`code_challenge_method` is optional and defaults to `plain`** (RFC 7636, section 4.3). A client that sends a challenge and omits the method has put its verifier into the authorization URL. Clients that can hash must use S256, which every PKCE server must implement.
- **The verifier** is 43 to 128 characters from the RFC 3986 unreserved set (`43*128unreserved`). RFC 9700 says the challenge must be transaction-specific and bound to the client and user agent, and that servers should try to detect constant values. S256 is the only method that does not expose the verifier to someone who can read the authorization request.
- **A server that requires PKCE** returns `invalid_request` when a public client sends no challenge, and `invalid_request` for an unsupported method.
- **Codes**: single-use; on reuse the AS must deny and should revoke tokens issued from the code.
- **Client authentication**: public clients cannot keep a secret, so they send only `client_id`. For confidential clients RFC 9700 recommends asymmetric methods (mutual TLS per RFC 8705, or `private_key_jwt`) so the AS stores no shared secrets.
- **Discovery**: the AS must give clients a way to detect PKCE support; RFC 8414 `code_challenge_methods_supported` is recommended.

## Attack classes and mitigations

- **Code injection** (RFC 9700, section 4.5): the attacker plants a stolen code in their own session with the legitimate client. Client authentication and `redirect_uri` checks all pass. PKCE binds the code to the transaction that started it.
- **PKCE downgrade** (section 4.8). Preconditions: the AS supports PKCE but does not mandate it, so the presence of `code_challenge` acts as a switch the attacker controls, and the client does not use or check `state`. The attacker starts a flow on their own device, strips `code_challenge`, and sends the victim's browser to the response URL carrying that unbound code. The client sends `code_verifier`; the AS sees no stored challenge and ignores it; the client ends up with a token for the attacker's account. **Fix**: the AS must reject a token request containing a `code_verifier` when no challenge was in the authorization request. An AS that mandates PKCE gets this for free.
- **Mix-up** (section 4.4): the client talks to two or more ASes and one is hostile (via dynamic registration or compromise). The hostile AS redirects the user to the honest AS using the honest client's ID; the code returns to a client that believes it came from the hostile AS and redeems it at the hostile token endpoint. Defences:
  - The client must store, per request, the issuer it sent the request to, bound to the user agent. Storing only the AS URL is insufficient: an attacker can name an honest authorization endpoint and their own token endpoint.
  - **Issuer identification** (RFC 9207): the response carries `iss`, an `https` URL with no query or fragment, compared by simple string comparison with the issuer stored for this request; mismatch means abort. Servers advertise `authorization_response_iss_parameter_supported`. A client must reject a response lacking `iss` from a server that advertises support. Errors carry `iss` too.
  - The alternative, a distinct redirect URI per issuer, should be used only if other options are unavailable.
  - Required whenever a client uses more than one AS; not required for a single AS.
- **Redirect URIs and open redirectors** (sections 4.1, 4.11): exact matching, with a port exception for native localhost; wildcard parsing bugs and subdomain takeover; clients and ASes must not expose open redirectors. An AS must authenticate the user before redirecting, except for silent authentication, and should redirect automatically only to redirect URIs it trusts (section 4.11.2). That limits bouncing by a hostile client's invalid-scope or declined-consent requests; `prompt=none` is the excepted case, so there the AS must judge whether it trusts the URI.
- **Token leakage**: clients must not put access tokens in a URI query parameter (section 4.3.2).

## Token design

- **Opaque or JWT.** RFC 6749 allows a handle or a self-contained signed token. **RFC 9068** profiles JWT access tokens: signed, never `none`; `typ` `at+jwt`; required claims `iss`, `exp`, `aud`, `sub`, `client_id`, `iat`, `jti`. The RS validates `typ`, `iss` (exact match), `aud` (this RS), signature and `exp`, and reports failure as `invalid_token`.
- **Confusion risks.** ID tokens must not be accepted as access tokens, hence `typ`. The AS must use a distinct `aud` for access tokens issued for distinct resources, to prevent cross-JWT confusion (RFC 9068, section 5). Token type is therefore checked by `typ` and `aud`, not by the other controls: introspection `active: true` only means the AS issued the token, has not revoked it and it is within its validity window (RFC 7662, section 2.2), and DPoP (below) binds a token to a key, which says who may present it, not what kind of token it is. RFC 9068 gives the RS no way to know which published key signs access tokens, so it accepts any of them; separate signing keys for ID tokens and access tokens neither contain a leaked key nor make the RS reject an ID-token signature. Claims are readable by the client unless encrypted, and the client must not inspect them.
- **Introspection** (RFC 7662): `active` is required, the endpoint needs its own authorization, and caching trades freshness for load. RFC 7009 notes that revoking a self-contained token immediately needs non-standardized back-end signalling.
- **Audience and resource** (RFC 8707): the `resource` parameter is an absolute URI without a fragment; the AS should audience-restrict to it and may answer `invalid_target`. RFC 9068 (section 5) adds that with several resources the AS should make each scope in the token unambiguously attributable to one of them. Scope is typically about what access is wanted rather than where (RFC 8707), though RFC 9700 notes a client can also indicate the RS by encoding it in the scope value. RFC 9700 prefers a single RS or a small set, and further restriction by scope or `authorization_details` (RFC 9396).

## Sender-constrained tokens

RFC 9700 says ASes and RSes should sender-constrain access tokens, and public-client refresh tokens must be sender-constrained or rotated.

- **mutual TLS** (RFC 8705): the AS binds the token to the client certificate; in a JWT, `cnf` carries `x5t#S256`, the base64url SHA-256 of the DER certificate. The RS takes the certificate from its TLS layer; on mismatch it returns 401 `invalid_token`. RFC 9700 notes that mutual TLS lets one token serve several RSes, while audience-restricted tokens need one per RS.
- **DPoP** (RFC 9449): application-level, usable by public clients. Each request carries a `DPoP` header holding a JWT with `typ` `dpop+jwt`, the public key in `jwk`, and claims `jti`, `htm`, `htu`, `iat`, plus `ath` (a hash of the access token) at the RS and `nonce` where the server supplied one. The token response has `token_type` `DPoP`, the token is presented as `Authorization: DPoP <token>`, and a JWT token is bound through `cnf` `jkt`, the key's JWK thumbprint. The server may demand a nonce with `use_dpop_nonce`; a server must accept a proof only for a limited time after its creation (RFC 9449, section 11.1) and can store `jti` values for that window to make proofs single-use, which may not be feasible without shared state; RFC 9700 expects the RS to prevent replay.
- **Limits.** RFC 9700 says sender-constraining fails if the attacker gets both token and key, as with XSS or corrupted client software. A key held in a hardware or software module only protects against use while the client is offline.

## Token exchange (RFC 8693)

A request uses `grant_type=urn:ietf:params:oauth:grant-type:token-exchange`, requires `subject_token` and `subject_token_type`, and may add `actor_token` (optional; `actor_token_type` is required when it is present), `scope`, `requested_token_type`, and `resource` or `audience`, which name the service where the new token will be used. The response carries `issued_token_type`. With **impersonation**, the acting service is indistinguishable from the user it acts for, within the token's rights. With **delegation**, the `subject_token` represents the user and the `actor_token` the acting service. If the AS issues a composite JWT, its `act` claim names the current actor (nested `act` claims record earlier actors), so audit logs can tell service and user apart (RFC 8693, sections 1.1, 2.1, 4.1). Whether and when it issues one is a matter of AS policy and configuration, and the RFC places no requirements on the trust model, so the exchange policy is yours.

## Your task

Run this (Python 3, written for this lesson and run on 2026-10-06). Then ask whether your AS makes the same decision in the downgrade case:

```python
import base64, hashlib, secrets

b64u = lambda b: base64.urlsafe_b64encode(b).rstrip(b"=").decode()
s256 = lambda v: b64u(hashlib.sha256(v.encode("ascii")).digest())

# RFC 7636 Appendix B test vector
assert s256("dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk") == "E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM"


def token_endpoint(stored_challenge, method, verifier):
    """What the AS decides when the token request arrives (RFC 7636 4.6, RFC 9700 4.8.2)."""
    if stored_challenge is None:
        return "REJECT: verifier sent, no challenge was stored" if verifier else "tokens (no PKCE in this flow)"
    if verifier is None:
        return "invalid_grant: verifier missing"
    got = s256(verifier) if method == "S256" else verifier
    return "tokens" if got == stored_challenge else "invalid_grant"


v = b64u(secrets.token_bytes(32))
c = s256(v)
print("lengths:", len(v), len(c))
print("matching pair     ->", token_endpoint(c, "S256", v))
print("wrong verifier    ->", token_endpoint(c, "S256", b64u(secrets.token_bytes(32))))
print("downgrade attempt ->", token_endpoint(None, None, v))
print("method omitted (plain) ->", token_endpoint(v, "plain", v), "- but the verifier was in the authorize URL")
```

Output from that exact script:

```
lengths: 43 43
matching pair     -> tokens
wrong verifier    -> invalid_grant
downgrade attempt -> REJECT: verifier sent, no challenge was stored
method omitted (plain) -> tokens - but the verifier was in the authorize URL
```

Written from the docs, not run against a live tenant: against your own AS, send a token request carrying `code_verifier` for a code issued without `code_challenge`, and record the result.

Next: OpenID Connect and ID token validation.
