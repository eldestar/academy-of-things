# OpenID Connect and JWT validation

You are building or reviewing the relying-party side: a login callback, an API gateway, a logout endpoint. This lesson goes through what OpenID Connect Core 1.0 fixes, what it leaves to you, and the attack classes a validator has to close. Facts checked 2026-10-06 against Core, Discovery 1.0, the RP-Initiated, Front-Channel and Back-Channel Logout specs, RFC 7519, 7515, 7517, 8725, 9700, and Okta and Microsoft Learn docs for the product claims.

## What the spec fixes, and what it leaves to you

The code flow is: authentication request (`openid` scope, `state`, optional `nonce`, and `code_challenge` with `code_challenge_method=S256` for a public client), redirect with `code`, direct token request (client authentication, or `code_verifier` for a public client), token response with `id_token` and `access_token`, ID token validation, optional UserInfo.

<!-- diagram:oidc-code-flow -->
<div class="oi-wrap" style="position:relative">
<input type="checkbox" id="oi-pause" class="oi-cb" /><label for="oi-pause" class="oi-btn"><span class="oi-off">Pause animation</span><span class="oi-on">Play animation</span></label>
<div class="oi-box" style="overflow-x:auto">
<svg class="oi-flow" viewBox="0 0 760 761" role="img" aria-labelledby="oi-t oi-d" style="width:760px;max-width:100%;min-width:699px;height:auto;display:block;margin:0 auto">
<title id="oi-t">The code flow with the obligations the spec and RFC 9700 put on each hop</title>
<desc id="oi-d">Two parties: the client on the relying-party side and the OP. Step 1: the authentication request, where redirect_uri is compared by simple string comparison, nonce is optional, and a public client uses PKCE with S256. Step 2: the callback carries code and state, and the client checks state. Step 3: the token request, where a confidential client authenticates or a public client sends the PKCE code_verifier; the OP must enforce the verifier against the challenge when one was sent, and the response carries id_token and access_token and must send Cache-Control no-store. Step 4: ID token validation under section 3.1.3.7; for a token received directly from the token endpoint, TLS may replace the signature check, for that one hop only. Step 5, optional: UserInfo, where sub must equal the ID token's sub or the response is discarded, because the ID token is the authority. The diagram highlights each step in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
<style>
svg.oi-flow{--ink:light-dark(#000000,#ffffff)}
.oi-box{fill:var(--panel);stroke:var(--border-strong);stroke-width:1.5}
.oi-hot{fill:var(--panel);stroke:var(--accent);stroke-width:2.5}
.oi-ttl{fill:var(--ink);font:600 15px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.oi-sub{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.oi-life{stroke:var(--border-strong);stroke-width:1.5;stroke-dasharray:4 5}
.oi-front{stroke:var(--accent);stroke-width:2;fill:none}
.oi-back{stroke:var(--muted);stroke-width:2;stroke-dasharray:7 5;fill:none}
.oi-bad{stroke:var(--bad);stroke-width:2;fill:none}
.oi-main{fill:var(--ink);font:600 13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.oi-badt{fill:var(--ink)}
.oi-dim{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.oi-badge{fill:var(--accent)}
.oi-b-back{fill:var(--muted)}
.oi-b-bad{fill:var(--bad)}
.oi-b-good{fill:var(--good)}
.oi-bt{fill:var(--on-accent);font:700 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.oi-note{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.oi-note-good{fill:var(--good-bg);stroke:var(--good);stroke-width:1.5}
.oi-note-bad{fill:var(--bad-bg);stroke:var(--bad);stroke-width:1.5}
.oi-nt{fill:var(--ink);font:500 12.5px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.oi-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:28s;animation-timing-function:linear;animation-iteration-count:infinite}
.oi-pk.oi-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.oi-pk.oi-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.oi-wrap{margin:20px 0}
@media (min-width:801px){.oi-wrap{margin-left:-44px;margin-right:-44px}}
.oi-g rect,.oi-g line,.oi-g path:not(.oi-gl){opacity:.5;animation-duration:28s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.oi-flow:hover .oi-g rect,svg.oi-flow:hover .oi-g line,svg.oi-flow:hover .oi-g path:not(.oi-gl),svg.oi-flow:hover .oi-pk{animation-play-state:paused}
.oi-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.oi-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.oi-btn:hover{background:var(--hover)}
.oi-cb:focus-visible + .oi-btn{outline:2px solid var(--accent);outline-offset:2px}
.oi-cb:checked + .oi-btn .oi-off,.oi-cb:not(:checked) + .oi-btn .oi-on{display:none}
.oi-cb:checked ~ .oi-box .oi-g rect,.oi-cb:checked ~ .oi-box .oi-g line,.oi-cb:checked ~ .oi-box .oi-g path:not(.oi-gl),.oi-cb:checked ~ .oi-box .oi-pk{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.oi-g rect,.oi-g line,.oi-g path:not(.oi-gl){animation:none;opacity:1}.oi-pk{animation:none;display:none}.oi-btn{display:none}}
@keyframes oi-g0{0%{opacity:1}21.429%{opacity:1}21.439%,100%{opacity:.5}}
@keyframes oi-p0{0%,-0.01%{opacity:0;transform:translateX(0)}0%{opacity:1;transform:translateX(0)}17.143%{opacity:1;transform:translateX(506px)}21.429%{opacity:1;transform:translateX(506px)}21.439%,100%{opacity:0;transform:translateX(506px)}}
.oi-g0 rect,.oi-g0 line,.oi-g0 path:not(.oi-gl){animation-name:oi-g0}.oi-p0{animation-name:oi-p0}
@keyframes oi-g1{0%,21.419%{opacity:.5}21.429%{opacity:1}42.857%{opacity:1}42.867%,100%{opacity:.5}}
@keyframes oi-p1{0%,21.419%{opacity:0;transform:translateX(0)}21.429%{opacity:1;transform:translateX(0)}38.571%{opacity:1;transform:translateX(-506px)}42.857%{opacity:1;transform:translateX(-506px)}42.867%,100%{opacity:0;transform:translateX(-506px)}}
.oi-g1 rect,.oi-g1 line,.oi-g1 path:not(.oi-gl){animation-name:oi-g1}.oi-p1{animation-name:oi-p1}
@keyframes oi-g2{0%,42.847%{opacity:.5}42.857%{opacity:1}64.286%{opacity:1}64.296%,100%{opacity:.5}}
@keyframes oi-p2{0%,42.847%{opacity:0;transform:translateX(0)}42.857%{opacity:1;transform:translateX(0)}60%{opacity:1;transform:translateX(-506px)}64.286%{opacity:1;transform:translateX(-506px)}64.296%,100%{opacity:0;transform:translateX(-506px)}}
.oi-g2 rect,.oi-g2 line,.oi-g2 path:not(.oi-gl){animation-name:oi-g2}.oi-p2{animation-name:oi-p2}
@keyframes oi-g3{0%,64.276%{opacity:.5}64.286%{opacity:1}78.571%{opacity:1}78.581%,100%{opacity:.5}}
.oi-g3 rect,.oi-g3 line,.oi-g3 path:not(.oi-gl){animation-name:oi-g3}
@keyframes oi-g4{0%,78.561%{opacity:.5}78.571%{opacity:1}100%{opacity:1}100.01%,100%{opacity:.5}}
@keyframes oi-p4{0%,78.561%{opacity:0;transform:translateX(0)}78.571%{opacity:1;transform:translateX(0)}95.714%{opacity:1;transform:translateX(-506px)}100%{opacity:1;transform:translateX(-506px)}100.01%,100%{opacity:0;transform:translateX(-506px)}}
.oi-g4 rect,.oi-g4 line,.oi-g4 path:not(.oi-gl){animation-name:oi-g4}.oi-p4{animation-name:oi-p4}
</style>
<defs>
<marker id="oi-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="oi-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="oi-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<line class="oi-life" x1="110" y1="72" x2="110" y2="709"/>
<line class="oi-life" x1="650" y1="72" x2="650" y2="709"/>
<rect class="oi-hot" x="20" y="10" width="180" height="62" rx="10"/><text class="oi-ttl" x="110" y="36">Client</text><text class="oi-sub" x="110" y="56">relying-party side</text>
<rect class="oi-box" x="560" y="10" width="180" height="62" rx="10"/><text class="oi-ttl" x="650" y="36">OP</text><text class="oi-sub" x="650" y="56">authorization, token endpoints</text>
<g class="oi-g oi-g0">
<text class="oi-main" x="380" y="108">authentication request</text>
<text class="oi-dim" x="380" y="124">redirect_uri: simple string comparison</text>
<text class="oi-dim" x="380" y="140">nonce optional; public client: PKCE, S256</text>
<line class="oi-front" x1="124" y1="154" x2="636" y2="154" marker-end="url(#oi-m-front)"/>
<circle class="oi-badge oi-b-front" cx="110" cy="154" r="12"/><text class="oi-bt" x="110" y="158.5">1</text>
</g>
<g class="oi-g oi-g1">
<text class="oi-main" x="380" y="194">callback: code and state</text>
<text class="oi-dim" x="380" y="210">client checks state</text>
<line class="oi-front" x1="636" y1="224" x2="124" y2="224" marker-end="url(#oi-m-front)"/>
<circle class="oi-badge oi-b-front" cx="650" cy="224" r="12"/><text class="oi-bt" x="650" y="228.5">2</text>
</g>
<g class="oi-g oi-g2">
<text class="oi-main" x="380" y="264">token request</text>
<text class="oi-dim" x="380" y="280">confidential: client authentication</text>
<text class="oi-dim" x="380" y="296">public: PKCE code_verifier</text>
<line class="oi-back" x1="124" y1="310" x2="636" y2="310" marker-end="url(#oi-m-back)"/>
<circle class="oi-badge oi-b-back" cx="110" cy="310" r="12"/><text class="oi-bt" x="110" y="314.5">3</text>
<text class="oi-main" x="380" y="350">token response: id_token, access_token</text>
<text class="oi-dim" x="380" y="366">MUST carry Cache-Control: no-store</text>
<line class="oi-back" x1="636" y1="380" x2="124" y2="380" marker-end="url(#oi-m-back)"/>
<rect class="oi-note-good" x="483" y="398" width="267" height="48" rx="8"/>
<text class="oi-nt" x="616" y="419">OP MUST enforce the verifier against</text>
<text class="oi-nt" x="616" y="436">the challenge when one was sent</text>
</g>
<g class="oi-g oi-g3">
<rect class="oi-note-good" x="10" y="474" width="307" height="65" rx="8"/>
<text class="oi-nt" x="164" y="495">ID token validation (3.1.3.7)</text>
<text class="oi-nt" x="164" y="512">direct from the token endpoint, TLS MAY</text>
<text class="oi-nt" x="164" y="529">replace the signature check: that hop only</text>
<circle class="oi-badge oi-b-good" cx="10" cy="506" r="12"/><text class="oi-bt" x="10" y="511.0">4</text>
</g>
<g class="oi-g oi-g4">
<text class="oi-main" x="380" y="573">UserInfo request (optional)</text>
<line class="oi-back" x1="124" y1="587" x2="636" y2="587" marker-end="url(#oi-m-back)"/>
<circle class="oi-badge oi-b-back" cx="110" cy="587" r="12"/><text class="oi-bt" x="110" y="591.5">5</text>
<text class="oi-main" x="380" y="627">sub MUST equal the ID token's sub,</text>
<text class="oi-dim" x="380" y="643">else discard: the ID token is the authority</text>
<line class="oi-back" x1="636" y1="657" x2="124" y2="657" marker-end="url(#oi-m-back)"/>
</g>
<circle class="oi-pk oi-p0" cx="130" cy="154" r="5.5"/>
<circle class="oi-pk oi-p1" cx="630" cy="224" r="5.5"/>
<circle class="oi-pk oi-p2 oi-pkback" cx="630" cy="380" r="5.5"/>
<circle class="oi-pk oi-p4 oi-pkback" cx="630" cy="657" r="5.5"/>
<line class="oi-front" x1="40" y1="737" x2="70" y2="737"/>
<text class="oi-dim" x="78" y="741" style="text-anchor:start">through the user agent</text>
<line class="oi-back" x1="252" y1="737" x2="282" y2="737"/>
<text class="oi-dim" x="290" y="741" style="text-anchor:start">token endpoint and UserInfo</text>
<rect class="oi-note-good" x="496" y="729" width="22" height="16" rx="4"/>
<text class="oi-dim" x="526" y="741" style="text-anchor:start">obligation or permission</text>
</svg>
</div>
</div>
<!-- /diagram:oidc-code-flow -->

Steps 1 and 2 pass through the browser, step 3 is a direct call to the token endpoint, and step 4 is the check your app must do itself.

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
<!-- diagram:oidc-alg-confusion -->
<div class="l04h-wrap" style="position:relative">
<input type="checkbox" id="l04h-pause" class="l04h-cb" /><label for="l04h-pause" class="l04h-btn"><span class="l04h-off">Pause animation</span><span class="l04h-on">Play animation</span></label>
<div class="l04h-box" style="overflow-x:auto">
<svg class="l04h-flow" viewBox="0 0 760 651" role="img" aria-labelledby="l04h-t l04h-d" style="width:760px;max-width:100%;min-width:699px;height:auto;display:block;margin:0 auto">
<title id="l04h-t">Algorithm confusion: a verifier that believes the header versus one that does not</title>
<desc id="l04h-d">Three parties: a verifier that trusts the header's alg, a forger, and a validator whose caller specifies the allowed algorithms. Step 1: the forger sends a token with alg none, or RS256 relabelled HS256 so the RSA public key is the HMAC secret; the forger writes the whole token, claims included, so iss and aud checks cannot compensate. The verifier that trusts the header accepts both forgeries, confirmed by the author with an unshown verifier. Step 2: the same token goes to the validator, which rejects it because its algorithm is not allowed; RFC 7515 says such a token should be treated as invalid even if its signature validates. The controls are that the caller lists the allowed algorithms, the library uses no others, and each key is used with exactly one algorithm. The diagram highlights each step in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
<style>
svg.l04h-flow{--ink:light-dark(#000000,#ffffff)}
.l04h-box{fill:var(--panel);stroke:var(--border-strong);stroke-width:1.5}
.l04h-hot{fill:var(--panel);stroke:var(--accent);stroke-width:2.5}
.l04h-ttl{fill:var(--ink);font:600 15px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l04h-sub{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l04h-life{stroke:var(--border-strong);stroke-width:1.5;stroke-dasharray:4 5}
.l04h-front{stroke:var(--accent);stroke-width:2;fill:none}
.l04h-back{stroke:var(--muted);stroke-width:2;stroke-dasharray:7 5;fill:none}
.l04h-bad{stroke:var(--bad);stroke-width:2;fill:none}
.l04h-main{fill:var(--ink);font:600 13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l04h-badt{fill:var(--ink)}
.l04h-dim{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l04h-badge{fill:var(--accent)}
.l04h-b-back{fill:var(--muted)}
.l04h-b-bad{fill:var(--bad)}
.l04h-b-good{fill:var(--good)}
.l04h-bt{fill:var(--on-accent);font:700 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l04h-note{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l04h-note-good{fill:var(--good-bg);stroke:var(--good);stroke-width:1.5}
.l04h-note-bad{fill:var(--bad-bg);stroke:var(--bad);stroke-width:1.5}
.l04h-nt{fill:var(--ink);font:500 12.5px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l04h-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:28s;animation-timing-function:linear;animation-iteration-count:infinite}
.l04h-pk.l04h-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.l04h-pk.l04h-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.l04h-wrap{margin:20px 0}
@media (min-width:801px){.l04h-wrap{margin-left:-44px;margin-right:-44px}}
.l04h-g rect,.l04h-g line,.l04h-g path:not(.l04h-gl){opacity:.5;animation-duration:28s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.l04h-flow:hover .l04h-g rect,svg.l04h-flow:hover .l04h-g line,svg.l04h-flow:hover .l04h-g path:not(.l04h-gl),svg.l04h-flow:hover .l04h-pk{animation-play-state:paused}
.l04h-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.l04h-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.l04h-btn:hover{background:var(--hover)}
.l04h-cb:focus-visible + .l04h-btn{outline:2px solid var(--accent);outline-offset:2px}
.l04h-cb:checked + .l04h-btn .l04h-off,.l04h-cb:not(:checked) + .l04h-btn .l04h-on{display:none}
.l04h-cb:checked ~ .l04h-box .l04h-g rect,.l04h-cb:checked ~ .l04h-box .l04h-g line,.l04h-cb:checked ~ .l04h-box .l04h-g path:not(.l04h-gl),.l04h-cb:checked ~ .l04h-box .l04h-pk{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.l04h-g rect,.l04h-g line,.l04h-g path:not(.l04h-gl){animation:none;opacity:1}.l04h-pk{animation:none;display:none}.l04h-btn{display:none}}
@keyframes l04h-g0{0%{opacity:1}21.429%{opacity:1}21.439%,100%{opacity:.5}}
@keyframes l04h-p0{0%,-0.01%{opacity:0;transform:translateX(0)}0%{opacity:1;transform:translateX(0)}17.143%{opacity:1;transform:translateX(-236px)}21.429%{opacity:1;transform:translateX(-236px)}21.439%,100%{opacity:0;transform:translateX(-236px)}}
.l04h-g0 rect,.l04h-g0 line,.l04h-g0 path:not(.l04h-gl){animation-name:l04h-g0}.l04h-p0{animation-name:l04h-p0}
@keyframes l04h-g1{0%,21.419%{opacity:.5}21.429%{opacity:1}35.714%{opacity:1}35.724%,100%{opacity:.5}}
.l04h-g1 rect,.l04h-g1 line,.l04h-g1 path:not(.l04h-gl){animation-name:l04h-g1}
@keyframes l04h-g2{0%,35.704%{opacity:.5}35.714%{opacity:1}50%{opacity:1}50.01%,100%{opacity:.5}}
.l04h-g2 rect,.l04h-g2 line,.l04h-g2 path:not(.l04h-gl){animation-name:l04h-g2}
@keyframes l04h-g3{0%,49.99%{opacity:.5}50%{opacity:1}71.429%{opacity:1}71.439%,100%{opacity:.5}}
@keyframes l04h-p3{0%,49.99%{opacity:0;transform:translateX(0)}50%{opacity:1;transform:translateX(0)}67.143%{opacity:1;transform:translateX(236px)}71.429%{opacity:1;transform:translateX(236px)}71.439%,100%{opacity:0;transform:translateX(236px)}}
.l04h-g3 rect,.l04h-g3 line,.l04h-g3 path:not(.l04h-gl){animation-name:l04h-g3}.l04h-p3{animation-name:l04h-p3}
@keyframes l04h-g4{0%,71.419%{opacity:.5}71.429%{opacity:1}85.714%{opacity:1}85.724%,100%{opacity:.5}}
.l04h-g4 rect,.l04h-g4 line,.l04h-g4 path:not(.l04h-gl){animation-name:l04h-g4}
@keyframes l04h-g5{0%,85.704%{opacity:.5}85.714%{opacity:1}100%{opacity:1}100.01%,100%{opacity:.5}}
.l04h-g5 rect,.l04h-g5 line,.l04h-g5 path:not(.l04h-gl){animation-name:l04h-g5}
</style>
<defs>
<marker id="l04h-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="l04h-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="l04h-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<line class="l04h-life" x1="110" y1="72" x2="110" y2="599"/>
<line class="l04h-life" x1="380" y1="72" x2="380" y2="599"/>
<line class="l04h-life" x1="650" y1="72" x2="650" y2="599"/>
<rect class="l04h-box" x="20" y="10" width="180" height="62" rx="10"/><text class="l04h-ttl" x="110" y="36">Verifier</text><text class="l04h-sub" x="110" y="56">trusts the header's alg</text>
<rect class="l04h-hot" x="290" y="10" width="180" height="62" rx="10"/><text class="l04h-ttl" x="380" y="36">Forger</text><text class="l04h-sub" x="380" y="56">writes the whole token</text>
<rect class="l04h-box" x="560" y="10" width="180" height="62" rx="10"/><text class="l04h-ttl" x="650" y="36">Validator</text><text class="l04h-sub" x="650" y="56">caller sets the algorithms</text>
<g class="l04h-g l04h-g0">
<text class="l04h-main l04h-badt" x="245" y="108">alg none, or RS256 relabelled</text>
<text class="l04h-dim" x="245" y="124">HS256, public key as secret</text>
<line class="l04h-bad" x1="366" y1="138" x2="124" y2="138" marker-end="url(#l04h-m-bad)"/>
<circle class="l04h-badge l04h-b-bad" cx="380" cy="138" r="12"/><text class="l04h-bt" x="380" y="142.5">1</text>
</g>
<g class="l04h-g l04h-g1">
<rect class="l04h-note-bad" x="16" y="172" width="188" height="48" rx="8"/>
<text class="l04h-nt" x="110" y="193">accepts both forgeries</text>
<text class="l04h-nt" x="110" y="210">(author's unshown check)</text>
</g>
<g class="l04h-g l04h-g2">
<rect class="l04h-note" x="282" y="248" width="195" height="65" rx="8"/>
<text class="l04h-nt" x="380" y="269">iss and aud checks cannot</text>
<text class="l04h-nt" x="380" y="286">compensate: the forger</text>
<text class="l04h-nt" x="380" y="303">writes the claims too</text>
</g>
<g class="l04h-g l04h-g3">
<text class="l04h-main" x="515" y="347">the same token</text>
<line class="l04h-front" x1="394" y1="361" x2="636" y2="361" marker-end="url(#l04h-m-front)"/>
<circle class="l04h-badge l04h-b-front" cx="380" cy="361" r="12"/><text class="l04h-bt" x="380" y="365.5">2</text>
</g>
<g class="l04h-g l04h-g4">
<rect class="l04h-note-good" x="516" y="395" width="234" height="65" rx="8"/>
<text class="l04h-nt" x="633" y="416">rejects: alg not allowed;</text>
<text class="l04h-nt" x="633" y="433">RFC 7515 5.2: should be invalid</text>
<text class="l04h-nt" x="633" y="450">even if the signature validates</text>
</g>
<g class="l04h-g l04h-g5">
<rect class="l04h-note-good" x="516" y="488" width="234" height="65" rx="8"/>
<text class="l04h-nt" x="633" y="509">caller lists the algs; library</text>
<text class="l04h-nt" x="633" y="526">uses no others; one alg per key</text>
<text class="l04h-nt" x="633" y="543">(RFC 8725 3.1, 3.2)</text>
</g>
<circle class="l04h-pk l04h-p0 l04h-pkbad" cx="360" cy="138" r="5.5"/>
<circle class="l04h-pk l04h-p3" cx="400" cy="361" r="5.5"/>
<line class="l04h-front" x1="40" y1="627" x2="70" y2="627"/>
<text class="l04h-dim" x="78" y="631" style="text-anchor:start">the same token</text>
<line class="l04h-bad" x1="201" y1="627" x2="231" y2="627"/>
<text class="l04h-dim" x="239" y="631" style="text-anchor:start">the forgery</text>
<rect class="l04h-note-good" x="343" y="619" width="22" height="16" rx="4"/>
<text class="l04h-dim" x="373" y="631" style="text-anchor:start">controls</text>
</svg>
</div>
</div>
<!-- /diagram:oidc-alg-confusion -->

Hop 1 sends the forged token to a verifier that believes the header, which accepted both forgeries in the author's own unshown check. Hop 2 sends the same token to a validator with an allowlist, which rejects it. The badges number this diagram's two hops, not the steps of the code flow.

- **Header-driven lookups.** `kid` is a hint, and RFC 7517 says keys in a set SHOULD have distinct `kid` values, not that they must. Sanitise it against SQL or LDAP injection; never follow `jku` or `x5u` URLs blindly (SSRF), per RFC 8725 section 3.10.
- **Substitution.** Wrong `aud`, wrong `iss`, and cross-JWT confusion: RFC 8725 sections 2.7, 2.8, 3.9, 3.12. If one issuer issues several kinds of JWT, your validation rules MUST be mutually exclusive: distinct `typ`, required claims, keys, or `aud` per kind. Logout tokens show the pattern: `typ` `logout+jwt` is recommended and `nonce` is prohibited, so a logout token is not a valid ID token.
- **Loose `email_verified`.** It means the OP took steps to confirm control; the method depends on the parties' agreement. Never link or merge accounts on it alone.
- **Front-channel exposure.** Implicit and hybrid put tokens where the user agent and its scripts can see them.

## JWKS, `kid` and rotation as a cache design

Core section 10.1.1: the signer publishes a JWK Set at `jwks_uri`, names the signing key by `kid`, adds new keys ahead of use, and SHOULD keep recently decommissioned keys published for a reasonable time. The verifier re-fetches on an unfamiliar `kid`. Okta says to cache per Cache-Control, that rotation is currently four times a year and can change without notice, and that hardcoded keys can fail.

Design advice (mine, not from the specs): do not answer an unknown `kid` by trying every cached key, since a newly published key is not in the cache; treat the JWKS as a TTL cache plus a refresh-on-miss, and put a cooldown on refresh-on-miss. Without one, anyone can send tokens with random `kid` values and make you fetch the issuer's JWKS on every request. Fetch only from the configured issuer's `jwks_uri`; if a refresh fails, keep serving from the cache while it is within its TTL, and reject any token whose `kid` you cannot resolve.

<!-- diagram:oidc-kid-resolution -->
<div class="l04i-wrap" style="position:relative">
<input type="checkbox" id="l04i-pause" class="l04i-cb" /><label for="l04i-pause" class="l04i-btn"><span class="l04i-off">Pause animation</span><span class="l04i-on">Play animation</span></label>
<div class="l04i-box" style="overflow-x:auto">
<svg class="l04i-flow" viewBox="0 0 760 484" role="img" aria-labelledby="l04i-t l04i-d" style="width:760px;max-width:100%;min-width:699px;height:auto;display:block;margin:0 auto">
<title id="l04i-t">Resolving a kid: the lesson's cache design</title>
<desc id="l04i-d">A decision tree for a token that arrives with a kid. If the kid is in the cache, verify with that key. If not, check whether the refresh-on-miss cooldown is still running; if it is, reject because the kid cannot be resolved. If the cooldown is not running, refetch from the configured issuer's jwks_uri; if the kid is now listed, verify with the new key, and if it is not listed or the refresh failed, reject. The diagram highlights each path in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
<style>
svg.l04i-flow{--ink:light-dark(#000000,#ffffff)}
.l04i-box{fill:var(--panel);stroke:var(--border-strong);stroke-width:1.5}
.l04i-hot{fill:var(--panel);stroke:var(--accent);stroke-width:2.5}
.l04i-ttl{fill:var(--ink);font:600 15px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l04i-sub{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l04i-life{stroke:var(--border-strong);stroke-width:1.5;stroke-dasharray:4 5}
.l04i-front{stroke:var(--accent);stroke-width:2;fill:none}
.l04i-back{stroke:var(--muted);stroke-width:2;stroke-dasharray:7 5;fill:none}
.l04i-bad{stroke:var(--bad);stroke-width:2;fill:none}
.l04i-main{fill:var(--ink);font:600 13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l04i-badt{fill:var(--ink)}
.l04i-dim{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l04i-badge{fill:var(--accent)}
.l04i-b-back{fill:var(--muted)}
.l04i-b-bad{fill:var(--bad)}
.l04i-b-good{fill:var(--good)}
.l04i-bt{fill:var(--on-accent);font:700 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l04i-note{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l04i-note-good{fill:var(--good-bg);stroke:var(--good);stroke-width:1.5}
.l04i-note-bad{fill:var(--bad-bg);stroke:var(--bad);stroke-width:1.5}
.l04i-nt{fill:var(--ink);font:500 12.5px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l04i-nest{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l04i-row{fill:var(--raised);stroke:var(--border-strong);stroke-width:1}
.l04i-ttlL{fill:var(--ink);font:600 14px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l04i-subL{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l04i-dimL{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l04i-dimR{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:end}
.l04i-conn{stroke:var(--accent);stroke-width:1.5;fill:none}
.l04i-edge{stroke:var(--border-strong);stroke-width:1.75;fill:none}
.l04i-hl{fill:none;stroke:var(--accent);stroke-width:3}
.l04i-hle{stroke:var(--accent);stroke-width:3;fill:none}
.l04i-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:18s;animation-timing-function:linear;animation-iteration-count:infinite}
.l04i-pk.l04i-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.l04i-pk.l04i-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.l04i-wrap{margin:20px 0}
@media (min-width:801px){.l04i-wrap{margin-left:-44px;margin-right:-44px}}
.l04i-g rect,.l04i-g line,.l04i-g path:not(.l04i-gl){opacity:.5;animation-duration:18s;animation-timing-function:linear;animation-iteration-count:infinite}
.l04i-h{opacity:0;animation-duration:18s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.l04i-flow:hover .l04i-g rect,svg.l04i-flow:hover .l04i-g line,svg.l04i-flow:hover .l04i-g path:not(.l04i-gl),svg.l04i-flow:hover .l04i-pk,svg.l04i-flow:hover .l04i-h{animation-play-state:paused}
.l04i-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.l04i-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.l04i-btn:hover{background:var(--hover)}
.l04i-cb:focus-visible + .l04i-btn{outline:2px solid var(--accent);outline-offset:2px}
.l04i-cb:checked + .l04i-btn .l04i-off,.l04i-cb:not(:checked) + .l04i-btn .l04i-on{display:none}
.l04i-cb:checked ~ .l04i-box .l04i-g rect,.l04i-cb:checked ~ .l04i-box .l04i-g line,.l04i-cb:checked ~ .l04i-box .l04i-g path:not(.l04i-gl),.l04i-cb:checked ~ .l04i-box .l04i-pk,.l04i-cb:checked ~ .l04i-box .l04i-h{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.l04i-g rect,.l04i-g line,.l04i-g path:not(.l04i-gl){animation:none;opacity:1}.l04i-pk{animation:none;display:none}.l04i-h{animation:none;opacity:0}.l04i-btn{display:none}}
@keyframes l04i-h0{0%{opacity:1}25%{opacity:1}25.01%,100%{opacity:0}}
.l04i-h0{animation-name:l04i-h0}
@keyframes l04i-h1{0%,24.99%{opacity:0}25%{opacity:1}50%{opacity:1}50.01%,100%{opacity:0}}
.l04i-h1{animation-name:l04i-h1}
@keyframes l04i-h2{0%,49.99%{opacity:0}50%{opacity:1}75%{opacity:1}75.01%,100%{opacity:0}}
.l04i-h2{animation-name:l04i-h2}
@keyframes l04i-h3{0%,74.99%{opacity:0}75%{opacity:1}100%{opacity:1}100.01%,100%{opacity:0}}
.l04i-h3{animation-name:l04i-h3}
</style>
<defs>
<marker id="l04i-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="l04i-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="l04i-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<path class="l04i-edge" d="M380,72 L380,101 L173,101 L173,127" marker-end="url(#l04i-m-front)"/>
<text class="l04i-dimL" x="180" y="117">in the cache</text>
<path class="l04i-edge" d="M380,72 L380,101 L443,101 L443,127" marker-end="url(#l04i-m-front)"/>
<text class="l04i-dimL" x="450" y="117">not in the cache</text>
<path class="l04i-edge" d="M443,195 L443,224 L308,224 L308,250" marker-end="url(#l04i-m-front)"/>
<text class="l04i-dimL" x="315" y="240">yes</text>
<path class="l04i-edge" d="M443,195 L443,224 L515,224 L515,250" marker-end="url(#l04i-m-front)"/>
<text class="l04i-dimL" x="522" y="240">no</text>
<path class="l04i-edge" d="M515,318 L515,347 L443,347 L443,373" marker-end="url(#l04i-m-front)"/>
<text class="l04i-dimL" x="450" y="363">yes</text>
<path class="l04i-edge" d="M515,318 L515,347 L578,347 L578,373" marker-end="url(#l04i-m-front)"/>
<text class="l04i-dimL" x="585" y="363">no, or refresh failed</text>
<rect class="l04i-note-good" x="118" y="130" width="110" height="48" rx="8"/><text class="l04i-nt" x="173" y="151">Verify with</text><text class="l04i-nt" x="173" y="168">that key</text>
<rect class="l04i-note-bad" x="244" y="253" width="128" height="48" rx="8"/><text class="l04i-nt" x="308" y="274">Reject: cannot</text><text class="l04i-nt" x="308" y="291">resolve the kid</text>
<rect class="l04i-note-good" x="388" y="376" width="110" height="48" rx="8"/><text class="l04i-nt" x="443" y="397">Verify with</text><text class="l04i-nt" x="443" y="414">the new key</text>
<rect class="l04i-note-bad" x="514" y="376" width="128" height="48" rx="8"/><text class="l04i-nt" x="578" y="397">Reject: cannot</text><text class="l04i-nt" x="578" y="414">resolve the kid</text>
<rect class="l04i-box" x="428" y="253" width="175" height="65" rx="8"/><text class="l04i-main" x="515" y="274">Refetch the configured</text><text class="l04i-nt" x="515" y="291">issuer's jwks_uri;</text><text class="l04i-nt" x="515" y="308">kid listed now?</text>
<rect class="l04i-box" x="379" y="130" width="128" height="65" rx="8"/><text class="l04i-main" x="443" y="151">Refresh-on-miss</text><text class="l04i-nt" x="443" y="168">cooldown still</text><text class="l04i-nt" x="443" y="185">running?</text>
<rect class="l04i-box" x="323" y="24" width="114" height="48" rx="8"/><text class="l04i-main" x="380" y="45">Token arrives</text><text class="l04i-nt" x="380" y="62">with a kid</text>
<g class="l04i-h l04i-h0">
<path class="l04i-hle" d="M380,72 L380,101 L173,101 L173,127" marker-end="url(#l04i-m-front)"/>
<rect class="l04i-hl" x="323" y="24" width="114" height="48" rx="8"/>
<rect class="l04i-hl" x="118" y="130" width="110" height="48" rx="8"/>
</g>
<g class="l04i-h l04i-h1">
<path class="l04i-hle" d="M380,72 L380,101 L443,101 L443,127" marker-end="url(#l04i-m-front)"/>
<path class="l04i-hle" d="M443,195 L443,224 L308,224 L308,250" marker-end="url(#l04i-m-front)"/>
<rect class="l04i-hl" x="323" y="24" width="114" height="48" rx="8"/>
<rect class="l04i-hl" x="379" y="130" width="128" height="65" rx="8"/>
<rect class="l04i-hl" x="244" y="253" width="128" height="48" rx="8"/>
</g>
<g class="l04i-h l04i-h2">
<path class="l04i-hle" d="M380,72 L380,101 L443,101 L443,127" marker-end="url(#l04i-m-front)"/>
<path class="l04i-hle" d="M443,195 L443,224 L515,224 L515,250" marker-end="url(#l04i-m-front)"/>
<path class="l04i-hle" d="M515,318 L515,347 L443,347 L443,373" marker-end="url(#l04i-m-front)"/>
<rect class="l04i-hl" x="323" y="24" width="114" height="48" rx="8"/>
<rect class="l04i-hl" x="379" y="130" width="128" height="65" rx="8"/>
<rect class="l04i-hl" x="428" y="253" width="175" height="65" rx="8"/>
<rect class="l04i-hl" x="388" y="376" width="110" height="48" rx="8"/>
</g>
<g class="l04i-h l04i-h3">
<path class="l04i-hle" d="M380,72 L380,101 L443,101 L443,127" marker-end="url(#l04i-m-front)"/>
<path class="l04i-hle" d="M443,195 L443,224 L515,224 L515,250" marker-end="url(#l04i-m-front)"/>
<path class="l04i-hle" d="M515,318 L515,347 L578,347 L578,373" marker-end="url(#l04i-m-front)"/>
<rect class="l04i-hl" x="323" y="24" width="114" height="48" rx="8"/>
<rect class="l04i-hl" x="379" y="130" width="128" height="65" rx="8"/>
<rect class="l04i-hl" x="428" y="253" width="175" height="65" rx="8"/>
<rect class="l04i-hl" x="514" y="376" width="128" height="48" rx="8"/>
</g>
<line class="l04i-front" x1="40" y1="460" x2="70" y2="460"/>
<text class="l04i-dim" x="78" y="464" style="text-anchor:start">the path being traced</text>
<rect class="l04i-note-good" x="246" y="452" width="22" height="16" rx="4"/>
<text class="l04i-dim" x="276" y="464" style="text-anchor:start">verify</text>
<rect class="l04i-note-bad" x="348" y="452" width="22" height="16" rx="4"/>
<text class="l04i-dim" x="378" y="464" style="text-anchor:start">reject</text>
</svg>
</div>
</div>
<!-- /diagram:oidc-kid-resolution -->

This is the design advice above, which is mine and not spec text; only the refetch on an unfamiliar kid comes from Core. Do not answer a miss by trying every cached key, since a newly published key is not in the cache.

## Subjects, pairwise identifiers and claim size

`iss` plus `sub` is the only guaranteed unique key (section 5.7); `email`, `preferred_username` and `name` are not unique identifiers. Core section 8 defines `public` and `pairwise` subject types: pairwise gives each client a different `sub`, computed per Sector Identifier (the host of the registered `redirect_uri`, or the host of a `sector_identifier_uri`, which is mandatory when redirect URIs span several hosts), and it must not be reversible by anyone but the OP. Microsoft documents that the Entra `sub` is pairwise per application ID, while `oid` is the same across apps and `tid` identifies the tenant; use `oid` plus `tid` to share data across services. Entra also warns `email` is mutable and not guaranteed correct.

Claim bloat: Core lets claims arrive in the ID token or from UserInfo, so my advice, not the spec's, is to keep volatile or large ones (groups) out of the ID token where you can. Entra caps `groups` at 200 for JWTs (150 for SAML) and, above that, omits it and emits an overage claim, so the app must call Microsoft Graph. An authorization check that reads a missing `groups` claim as "no groups" is a bug.

## Several issuers

RFC 8725 section 3.8: the application MUST validate that the keys used belong to the issuer. Keep an allowlist of issuers, each with its own `jwks_uri`, expected `aud` and algorithms; never fetch keys from the URL named by an unverified token's `iss` (my reading of those sections; section 2.9 says claims are SSRF vectors). Compare the `issuer` in metadata with the URL you fetched it from. For Entra multi-tenant apps, Microsoft says to use the GUID in `iss` to restrict which tenants may sign in.

## Logout design

Back-channel logout: the OP POSTs `logout_token` (form-encoded) to a registered URI. Validate it like an ID token (`none` forbidden), then require `events` containing `http://schemas.openid.net/event/backchannel-logout`, either `sub` or `sid`, and no `nonce`. Checking `jti` for replay is optional. With `sid`, end that session; with only `sub`, end all of that user's sessions at the app. Answer 200 on success, 400 on invalid or failed. Refresh tokens issued without `offline_access` SHOULD be revoked. The OP should not retransmit except after recoverable errors, so make the handler idempotent: a user who is already logged out counts as success. Limits: the URI must be reachable from the OP, an ID token already issued stays valid until `exp`, and Core section 16.18 notes access tokens may not be revocable. The spec describes delivery and the app's actions, and I found no list of events that make an OP send one, so whether an admin action does is OP-specific (not verified for Okta or Entra).

<!-- diagram:oidc-logout-token -->
<div class="l04j-wrap" style="position:relative">
<input type="checkbox" id="l04j-pause" class="l04j-cb" /><label for="l04j-pause" class="l04j-btn"><span class="l04j-off">Pause animation</span><span class="l04j-on">Play animation</span></label>
<div class="l04j-box" style="overflow-x:auto">
<svg class="l04j-flow" viewBox="0 0 760 484" role="img" aria-labelledby="l04j-t l04j-d" style="width:760px;max-width:100%;min-width:699px;height:auto;display:block;margin:0 auto">
<title id="l04j-t">Handling a back-channel logout token</title>
<desc id="l04j-d">A decision tree for a logout token posted to your registered URI. If it is not valid when checked like an ID token, with alg none forbidden, answer 400. If the events claim lacks the backchannel-logout event, or it has neither sub nor sid, or it carries a nonce, answer 400. If it has a sid, end that session and answer 200; a user already logged out counts as success. If it has only a sub, end all of that user's sessions at the app and answer 200. The diagram highlights each path in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
<style>
svg.l04j-flow{--ink:light-dark(#000000,#ffffff)}
.l04j-box{fill:var(--panel);stroke:var(--border-strong);stroke-width:1.5}
.l04j-hot{fill:var(--panel);stroke:var(--accent);stroke-width:2.5}
.l04j-ttl{fill:var(--ink);font:600 15px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l04j-sub{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l04j-life{stroke:var(--border-strong);stroke-width:1.5;stroke-dasharray:4 5}
.l04j-front{stroke:var(--accent);stroke-width:2;fill:none}
.l04j-back{stroke:var(--muted);stroke-width:2;stroke-dasharray:7 5;fill:none}
.l04j-bad{stroke:var(--bad);stroke-width:2;fill:none}
.l04j-main{fill:var(--ink);font:600 13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l04j-badt{fill:var(--ink)}
.l04j-dim{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l04j-badge{fill:var(--accent)}
.l04j-b-back{fill:var(--muted)}
.l04j-b-bad{fill:var(--bad)}
.l04j-b-good{fill:var(--good)}
.l04j-bt{fill:var(--on-accent);font:700 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l04j-note{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l04j-note-good{fill:var(--good-bg);stroke:var(--good);stroke-width:1.5}
.l04j-note-bad{fill:var(--bad-bg);stroke:var(--bad);stroke-width:1.5}
.l04j-nt{fill:var(--ink);font:500 12.5px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l04j-nest{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l04j-row{fill:var(--raised);stroke:var(--border-strong);stroke-width:1}
.l04j-ttlL{fill:var(--ink);font:600 14px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l04j-subL{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l04j-dimL{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l04j-dimR{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:end}
.l04j-conn{stroke:var(--accent);stroke-width:1.5;fill:none}
.l04j-edge{stroke:var(--border-strong);stroke-width:1.75;fill:none}
.l04j-hl{fill:none;stroke:var(--accent);stroke-width:3}
.l04j-hle{stroke:var(--accent);stroke-width:3;fill:none}
.l04j-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:18s;animation-timing-function:linear;animation-iteration-count:infinite}
.l04j-pk.l04j-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.l04j-pk.l04j-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.l04j-wrap{margin:20px 0}
@media (min-width:801px){.l04j-wrap{margin-left:-44px;margin-right:-44px}}
.l04j-g rect,.l04j-g line,.l04j-g path:not(.l04j-gl){opacity:.5;animation-duration:18s;animation-timing-function:linear;animation-iteration-count:infinite}
.l04j-h{opacity:0;animation-duration:18s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.l04j-flow:hover .l04j-g rect,svg.l04j-flow:hover .l04j-g line,svg.l04j-flow:hover .l04j-g path:not(.l04j-gl),svg.l04j-flow:hover .l04j-pk,svg.l04j-flow:hover .l04j-h{animation-play-state:paused}
.l04j-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.l04j-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.l04j-btn:hover{background:var(--hover)}
.l04j-cb:focus-visible + .l04j-btn{outline:2px solid var(--accent);outline-offset:2px}
.l04j-cb:checked + .l04j-btn .l04j-off,.l04j-cb:not(:checked) + .l04j-btn .l04j-on{display:none}
.l04j-cb:checked ~ .l04j-box .l04j-g rect,.l04j-cb:checked ~ .l04j-box .l04j-g line,.l04j-cb:checked ~ .l04j-box .l04j-g path:not(.l04j-gl),.l04j-cb:checked ~ .l04j-box .l04j-pk,.l04j-cb:checked ~ .l04j-box .l04j-h{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.l04j-g rect,.l04j-g line,.l04j-g path:not(.l04j-gl){animation:none;opacity:1}.l04j-pk{animation:none;display:none}.l04j-h{animation:none;opacity:0}.l04j-btn{display:none}}
@keyframes l04j-h0{0%{opacity:1}25%{opacity:1}25.01%,100%{opacity:0}}
.l04j-h0{animation-name:l04j-h0}
@keyframes l04j-h1{0%,24.99%{opacity:0}25%{opacity:1}50%{opacity:1}50.01%,100%{opacity:0}}
.l04j-h1{animation-name:l04j-h1}
@keyframes l04j-h2{0%,49.99%{opacity:0}50%{opacity:1}75%{opacity:1}75.01%,100%{opacity:0}}
.l04j-h2{animation-name:l04j-h2}
@keyframes l04j-h3{0%,74.99%{opacity:0}75%{opacity:1}100%{opacity:1}100.01%,100%{opacity:0}}
.l04j-h3{animation-name:l04j-h3}
</style>
<defs>
<marker id="l04j-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="l04j-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="l04j-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<path class="l04j-edge" d="M380,89 L380,118 L122,118 L122,144" marker-end="url(#l04j-m-front)"/>
<text class="l04j-dimL" x="130" y="134">no</text>
<path class="l04j-edge" d="M380,89 L380,118 L443,118 L443,144" marker-end="url(#l04j-m-front)"/>
<text class="l04j-dimL" x="450" y="134">yes</text>
<path class="l04j-edge" d="M443,212 L443,241 L248,241 L248,267" marker-end="url(#l04j-m-front)"/>
<text class="l04j-dimL" x="256" y="257">no</text>
<path class="l04j-edge" d="M443,212 L443,241 L506,241 L506,267" marker-end="url(#l04j-m-front)"/>
<text class="l04j-dimL" x="513" y="257">yes</text>
<path class="l04j-edge" d="M506,301 L506,330 L410,330 L410,356" marker-end="url(#l04j-m-front)"/>
<text class="l04j-dimL" x="418" y="346">yes</text>
<path class="l04j-edge" d="M506,301 L506,330 L605,330 L605,356" marker-end="url(#l04j-m-front)"/>
<text class="l04j-dimL" x="612" y="346">no, sub only</text>
<rect class="l04j-note-bad" x="68" y="147" width="110" height="31" rx="8"/><text class="l04j-nt" x="122" y="168">Answer 400</text>
<rect class="l04j-note-bad" x="194" y="270" width="110" height="31" rx="8"/><text class="l04j-nt" x="248" y="291">Answer 400</text>
<rect class="l04j-note-good" x="320" y="359" width="182" height="65" rx="8"/><text class="l04j-nt" x="410" y="380">End that session;</text><text class="l04j-nt" x="410" y="397">already out is success;</text><text class="l04j-nt" x="410" y="414">answer 200</text>
<rect class="l04j-note-good" x="518" y="359" width="175" height="65" rx="8"/><text class="l04j-nt" x="605" y="380">End all of that user's</text><text class="l04j-nt" x="605" y="397">sessions at the app;</text><text class="l04j-nt" x="605" y="414">answer 200</text>
<rect class="l04j-box" x="451" y="270" width="110" height="31" rx="8"/><text class="l04j-main" x="506" y="291">sid present?</text>
<rect class="l04j-box" x="352" y="147" width="182" height="65" rx="8"/><text class="l04j-main" x="443" y="168">events has backchannel-</text><text class="l04j-nt" x="443" y="185">logout; sub or sid;</text><text class="l04j-nt" x="443" y="202">no nonce?</text>
<rect class="l04j-box" x="292" y="24" width="175" height="65" rx="8"/><text class="l04j-main" x="380" y="45">Logout token POSTed:</text><text class="l04j-nt" x="380" y="62">valid like an ID token</text><text class="l04j-nt" x="380" y="79">(none forbidden)?</text>
<g class="l04j-h l04j-h0">
<path class="l04j-hle" d="M380,89 L380,118 L122,118 L122,144" marker-end="url(#l04j-m-front)"/>
<rect class="l04j-hl" x="292" y="24" width="175" height="65" rx="8"/>
<rect class="l04j-hl" x="68" y="147" width="110" height="31" rx="8"/>
</g>
<g class="l04j-h l04j-h1">
<path class="l04j-hle" d="M380,89 L380,118 L443,118 L443,144" marker-end="url(#l04j-m-front)"/>
<path class="l04j-hle" d="M443,212 L443,241 L248,241 L248,267" marker-end="url(#l04j-m-front)"/>
<rect class="l04j-hl" x="292" y="24" width="175" height="65" rx="8"/>
<rect class="l04j-hl" x="352" y="147" width="182" height="65" rx="8"/>
<rect class="l04j-hl" x="194" y="270" width="110" height="31" rx="8"/>
</g>
<g class="l04j-h l04j-h2">
<path class="l04j-hle" d="M380,89 L380,118 L443,118 L443,144" marker-end="url(#l04j-m-front)"/>
<path class="l04j-hle" d="M443,212 L443,241 L506,241 L506,267" marker-end="url(#l04j-m-front)"/>
<path class="l04j-hle" d="M506,301 L506,330 L410,330 L410,356" marker-end="url(#l04j-m-front)"/>
<rect class="l04j-hl" x="292" y="24" width="175" height="65" rx="8"/>
<rect class="l04j-hl" x="352" y="147" width="182" height="65" rx="8"/>
<rect class="l04j-hl" x="451" y="270" width="110" height="31" rx="8"/>
<rect class="l04j-hl" x="320" y="359" width="182" height="65" rx="8"/>
</g>
<g class="l04j-h l04j-h3">
<path class="l04j-hle" d="M380,89 L380,118 L443,118 L443,144" marker-end="url(#l04j-m-front)"/>
<path class="l04j-hle" d="M443,212 L443,241 L506,241 L506,267" marker-end="url(#l04j-m-front)"/>
<path class="l04j-hle" d="M506,301 L506,330 L605,330 L605,356" marker-end="url(#l04j-m-front)"/>
<rect class="l04j-hl" x="292" y="24" width="175" height="65" rx="8"/>
<rect class="l04j-hl" x="352" y="147" width="182" height="65" rx="8"/>
<rect class="l04j-hl" x="451" y="270" width="110" height="31" rx="8"/>
<rect class="l04j-hl" x="518" y="359" width="175" height="65" rx="8"/>
</g>
<line class="l04j-front" x1="40" y1="460" x2="70" y2="460"/>
<text class="l04j-dim" x="78" y="464" style="text-anchor:start">the path being traced</text>
<rect class="l04j-note-good" x="246" y="452" width="22" height="16" rx="4"/>
<text class="l04j-dim" x="276" y="464" style="text-anchor:start">success</text>
<rect class="l04j-note-bad" x="354" y="452" width="22" height="16" rx="4"/>
<text class="l04j-dim" x="384" y="464" style="text-anchor:start">invalid</text>
</svg>
</div>
</div>
<!-- /diagram:oidc-logout-token -->

Follow a logout token from the top: each path ends in the status code the endpoint returns, or the sessions it ends. Whether an OP sends one for an admin action is OP-specific and not verified here.

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
