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
<div class="oa-wrap" style="position:relative">
<input type="checkbox" id="oa-pause" class="oa-cb" /><label for="oa-pause" class="oa-btn"><span class="oa-off">Pause animation</span><span class="oa-on">Play animation</span></label>
<div class="oa-box" style="overflow-x:auto">
<svg class="oa-flow" viewBox="0 0 760 778" role="img" aria-labelledby="oa-t oa-d" style="width:760px;max-width:100%;min-width:699px;height:auto;display:block;margin:0 auto">
<title id="oa-t">Code flow at spec level: what the AS records and decides</title>
<desc id="oa-d">Two parties: the client and the authorization server (AS), steps 1 to 5 of the flow. Step 1: through the browser, the client sends response_type=code, client_id, redirect_uri, scope, state, code_challenge and code_challenge_method. The method is optional and defaults to plain, so a client that omits it has put its verifier in the authorization URL. Step 2: the AS authenticates the user, obtains consent, and records the challenge and method with the code. Step 3: through the browser, the AS redirects to the redirect_uri with code and state. Step 4: the client verifies state, or relies on PKCE for CSRF where the AS is known to support it. Step 5: directly, the client sends code, code_verifier, the redirect_uri if it was sent at step 1, and client authentication or client_id; a mismatch returns invalid_grant. A code used twice must be denied, and the tokens issued from it should be revoked. Steps 6 and 7 are not drawn. The diagram highlights each step in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
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
.oa-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:34s;animation-timing-function:linear;animation-iteration-count:infinite}
.oa-pk.oa-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.oa-pk.oa-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.oa-wrap{margin:20px 0}
@media (min-width:801px){.oa-wrap{margin-left:-44px;margin-right:-44px}}
.oa-g rect,.oa-g line,.oa-g path:not(.oa-gl){opacity:.5;animation-duration:34s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.oa-flow:hover .oa-g rect,svg.oa-flow:hover .oa-g line,svg.oa-flow:hover .oa-g path:not(.oa-gl),svg.oa-flow:hover .oa-pk{animation-play-state:paused}
.oa-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.oa-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.oa-btn:hover{background:var(--hover)}
.oa-cb:focus-visible + .oa-btn{outline:2px solid var(--accent);outline-offset:2px}
.oa-cb:checked + .oa-btn .oa-off,.oa-cb:not(:checked) + .oa-btn .oa-on{display:none}
.oa-cb:checked ~ .oa-box .oa-g rect,.oa-cb:checked ~ .oa-box .oa-g line,.oa-cb:checked ~ .oa-box .oa-g path:not(.oa-gl),.oa-cb:checked ~ .oa-box .oa-pk{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.oa-g rect,.oa-g line,.oa-g path:not(.oa-gl){animation:none;opacity:1}.oa-pk{animation:none;display:none}.oa-btn{display:none}}
@keyframes oa-g0{0%{opacity:1}17.647%{opacity:1}17.657%,100%{opacity:.5}}
@keyframes oa-p0{0%,-0.01%{opacity:0;transform:translateX(0)}0%{opacity:1;transform:translateX(0)}14.118%{opacity:1;transform:translateX(506px)}17.647%{opacity:1;transform:translateX(506px)}17.657%,100%{opacity:0;transform:translateX(506px)}}
.oa-g0 rect,.oa-g0 line,.oa-g0 path:not(.oa-gl){animation-name:oa-g0}.oa-p0{animation-name:oa-p0}
@keyframes oa-g1{0%,17.637%{opacity:.5}17.647%{opacity:1}29.412%{opacity:1}29.422%,100%{opacity:.5}}
.oa-g1 rect,.oa-g1 line,.oa-g1 path:not(.oa-gl){animation-name:oa-g1}
@keyframes oa-g2{0%,29.402%{opacity:.5}29.412%{opacity:1}41.176%{opacity:1}41.186%,100%{opacity:.5}}
.oa-g2 rect,.oa-g2 line,.oa-g2 path:not(.oa-gl){animation-name:oa-g2}
@keyframes oa-g3{0%,41.166%{opacity:.5}41.176%{opacity:1}58.824%{opacity:1}58.834%,100%{opacity:.5}}
@keyframes oa-p3{0%,41.166%{opacity:0;transform:translateX(0)}41.176%{opacity:1;transform:translateX(0)}55.294%{opacity:1;transform:translateX(-506px)}58.824%{opacity:1;transform:translateX(-506px)}58.834%,100%{opacity:0;transform:translateX(-506px)}}
.oa-g3 rect,.oa-g3 line,.oa-g3 path:not(.oa-gl){animation-name:oa-g3}.oa-p3{animation-name:oa-p3}
@keyframes oa-g4{0%,58.814%{opacity:.5}58.824%{opacity:1}70.588%{opacity:1}70.598%,100%{opacity:.5}}
.oa-g4 rect,.oa-g4 line,.oa-g4 path:not(.oa-gl){animation-name:oa-g4}
@keyframes oa-g5{0%,70.578%{opacity:.5}70.588%{opacity:1}88.235%{opacity:1}88.245%,100%{opacity:.5}}
@keyframes oa-p5{0%,70.578%{opacity:0;transform:translateX(0)}70.588%{opacity:1;transform:translateX(0)}84.706%{opacity:1;transform:translateX(-506px)}88.235%{opacity:1;transform:translateX(-506px)}88.245%,100%{opacity:0;transform:translateX(-506px)}}
.oa-g5 rect,.oa-g5 line,.oa-g5 path:not(.oa-gl){animation-name:oa-g5}.oa-p5{animation-name:oa-p5}
@keyframes oa-g6{0%,88.225%{opacity:.5}88.235%{opacity:1}100%{opacity:1}100.01%,100%{opacity:.5}}
.oa-g6 rect,.oa-g6 line,.oa-g6 path:not(.oa-gl){animation-name:oa-g6}
</style>
<defs>
<marker id="oa-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="oa-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="oa-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<line class="oa-life" x1="110" y1="72" x2="110" y2="704"/>
<line class="oa-life" x1="650" y1="72" x2="650" y2="704"/>
<rect class="oa-box" x="20" y="10" width="180" height="62" rx="10"/><text class="oa-ttl" x="110" y="36">Client</text><text class="oa-sub" x="110" y="56">public or confidential</text>
<rect class="oa-hot" x="560" y="10" width="180" height="62" rx="10"/><text class="oa-ttl" x="650" y="36">Authorization server</text><text class="oa-sub" x="650" y="56">records challenge and method</text>
<g class="oa-g oa-g0">
<text class="oa-main" x="380" y="108">response_type=code, client_id, redirect_uri,</text>
<text class="oa-dim" x="380" y="124">scope, state, code_challenge,</text>
<text class="oa-dim" x="380" y="140">code_challenge_method</text>
<line class="oa-front" x1="124" y1="154" x2="636" y2="154" marker-end="url(#oa-m-front)"/>
<circle class="oa-badge oa-b-front" cx="110" cy="154" r="12"/><text class="oa-bt" x="110" y="158.5">1</text>
</g>
<g class="oa-g oa-g1">
<rect class="oa-note-bad" x="10" y="188" width="294" height="48" rx="8"/>
<text class="oa-nt" x="157" y="209">method omitted means plain: the verifier</text>
<text class="oa-nt" x="157" y="226">is in the authorization URL</text>
<circle class="oa-badge oa-b-bad" cx="10" cy="212" r="12"/><text class="oa-bt" x="10" y="216.5">!</text>
</g>
<g class="oa-g oa-g2">
<rect class="oa-note" x="417" y="264" width="333" height="48" rx="8"/>
<text class="oa-nt" x="584" y="285">authenticates the user, obtains consent,</text>
<text class="oa-nt" x="584" y="302">records the challenge and method with the code</text>
<circle class="oa-badge oa-b-plain" cx="417" cy="288" r="12"/><text class="oa-bt" x="417" y="292.5">2</text>
</g>
<g class="oa-g oa-g3">
<text class="oa-main" x="380" y="346">redirect to redirect_uri</text>
<text class="oa-dim" x="380" y="362">code and state</text>
<line class="oa-front" x1="636" y1="376" x2="124" y2="376" marker-end="url(#oa-m-front)"/>
<circle class="oa-badge oa-b-front" cx="650" cy="376" r="12"/><text class="oa-bt" x="650" y="380.5">3</text>
</g>
<g class="oa-g oa-g4">
<rect class="oa-note-good" x="10" y="410" width="280" height="48" rx="8"/>
<text class="oa-nt" x="150" y="431">verify state, or rely on PKCE for CSRF</text>
<text class="oa-nt" x="150" y="448">where the AS is known to support it</text>
<circle class="oa-badge oa-b-good" cx="10" cy="434" r="12"/><text class="oa-bt" x="10" y="438.5">4</text>
</g>
<g class="oa-g oa-g5">
<text class="oa-main" x="380" y="492">code, code_verifier, redirect_uri if sent at step 1,</text>
<text class="oa-dim" x="380" y="508">client authentication or client_id</text>
<line class="oa-back" x1="124" y1="522" x2="636" y2="522" marker-end="url(#oa-m-back)"/>
<circle class="oa-badge oa-b-back" cx="110" cy="522" r="12"/><text class="oa-bt" x="110" y="526.5">5</text>
<text class="oa-main" x="380" y="562">a mismatch returns invalid_grant</text>
<line class="oa-back" x1="636" y1="576" x2="124" y2="576" marker-end="url(#oa-m-back)"/>
</g>
<g class="oa-g oa-g6">
<rect class="oa-note-bad" x="410" y="610" width="340" height="48" rx="8"/>
<text class="oa-nt" x="580" y="631">a code used twice: the AS must deny the request</text>
<text class="oa-nt" x="580" y="648">and should revoke tokens issued from the code</text>
<circle class="oa-badge oa-b-bad" cx="410" cy="634" r="12"/><text class="oa-bt" x="410" y="638.5">!</text>
</g>
<circle class="oa-pk oa-p0" cx="130" cy="154" r="5.5"/>
<circle class="oa-pk oa-p3" cx="630" cy="376" r="5.5"/>
<circle class="oa-pk oa-p5 oa-pkback" cx="630" cy="576" r="5.5"/>
<line class="oa-front" x1="40" y1="732" x2="70" y2="732"/>
<text class="oa-dim" x="78" y="736" style="text-anchor:start">through the user's browser</text>
<line class="oa-back" x1="278" y1="732" x2="308" y2="732"/>
<text class="oa-dim" x="316" y="736" style="text-anchor:start">direct request, not a redirect</text>
<rect class="oa-note-bad" x="542" y="724" width="22" height="16" rx="4"/>
<text class="oa-dim" x="572" y="736" style="text-anchor:start">failure mode</text>
<rect class="oa-note-good" x="40" y="746" width="22" height="16" rx="4"/>
<text class="oa-dim" x="70" y="758" style="text-anchor:start">a check to perform</text>
</svg>
</div>
</div>
<!-- /diagram:oauth-code-pkce -->

Solid arrows pass through the user's browser; dashed arrows are direct requests, not browser redirects. The numbers match the list below, for steps 1 to 5; steps 6 and 7 are not drawn. The red notes mark two failure paths: an omitted method, and a code used twice.

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

<!-- diagram:oauth-pkce-downgrade -->
<div class="l03d-wrap" style="position:relative">
<input type="checkbox" id="l03d-pause" class="l03d-cb" /><label for="l03d-pause" class="l03d-btn"><span class="l03d-off">Pause animation</span><span class="l03d-on">Play animation</span></label>
<div class="l03d-box" style="overflow-x:auto">
<svg class="l03d-flow" viewBox="0 0 760 643" role="img" aria-labelledby="l03d-t l03d-d" style="width:760px;max-width:100%;min-width:699px;height:auto;display:block;margin:0 auto">
<title id="l03d-t">PKCE downgrade attack (RFC 9700, section 4.8)</title>
<desc id="l03d-d">Three parties: the attacker, the authorization server (AS) and the victim's client. Preconditions: the AS supports PKCE but does not mandate it, and the client does not use or check state. Step 1: the attacker starts a flow on their own device with code_challenge stripped and receives an unbound code. Step 2: the attacker sends the victim's browser to the response URL carrying that unbound code. Step 3: the client sends the code and its code_verifier; the AS sees no stored challenge and ignores the verifier, so the client ends up with a token for the attacker's account. Step 4, the fix: the AS must reject a token request containing a code_verifier when no challenge was in the authorization request. The diagram highlights each step in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
<style>
svg.l03d-flow{--ink:light-dark(#000000,#ffffff)}
.l03d-box{fill:var(--panel);stroke:var(--border-strong);stroke-width:1.5}
.l03d-hot{fill:var(--panel);stroke:var(--accent);stroke-width:2.5}
.l03d-ttl{fill:var(--ink);font:600 15px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l03d-sub{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l03d-life{stroke:var(--border-strong);stroke-width:1.5;stroke-dasharray:4 5}
.l03d-front{stroke:var(--accent);stroke-width:2;fill:none}
.l03d-back{stroke:var(--muted);stroke-width:2;stroke-dasharray:7 5;fill:none}
.l03d-bad{stroke:var(--bad);stroke-width:2;fill:none}
.l03d-main{fill:var(--ink);font:600 13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l03d-badt{fill:var(--ink)}
.l03d-dim{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l03d-badge{fill:var(--accent)}
.l03d-b-back{fill:var(--muted)}
.l03d-b-bad{fill:var(--bad)}
.l03d-b-good{fill:var(--good)}
.l03d-bt{fill:var(--on-accent);font:700 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l03d-note{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l03d-note-good{fill:var(--good-bg);stroke:var(--good);stroke-width:1.5}
.l03d-note-bad{fill:var(--bad-bg);stroke:var(--bad);stroke-width:1.5}
.l03d-nt{fill:var(--ink);font:500 12.5px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l03d-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:26s;animation-timing-function:linear;animation-iteration-count:infinite}
.l03d-pk.l03d-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.l03d-pk.l03d-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.l03d-wrap{margin:20px 0}
@media (min-width:801px){.l03d-wrap{margin-left:-44px;margin-right:-44px}}
.l03d-g rect,.l03d-g line,.l03d-g path:not(.l03d-gl){opacity:.5;animation-duration:26s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.l03d-flow:hover .l03d-g rect,svg.l03d-flow:hover .l03d-g line,svg.l03d-flow:hover .l03d-g path:not(.l03d-gl),svg.l03d-flow:hover .l03d-pk{animation-play-state:paused}
.l03d-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.l03d-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.l03d-btn:hover{background:var(--hover)}
.l03d-cb:focus-visible + .l03d-btn{outline:2px solid var(--accent);outline-offset:2px}
.l03d-cb:checked + .l03d-btn .l03d-off,.l03d-cb:not(:checked) + .l03d-btn .l03d-on{display:none}
.l03d-cb:checked ~ .l03d-box .l03d-g rect,.l03d-cb:checked ~ .l03d-box .l03d-g line,.l03d-cb:checked ~ .l03d-box .l03d-g path:not(.l03d-gl),.l03d-cb:checked ~ .l03d-box .l03d-pk{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.l03d-g rect,.l03d-g line,.l03d-g path:not(.l03d-gl){animation:none;opacity:1}.l03d-pk{animation:none;display:none}.l03d-btn{display:none}}
@keyframes l03d-g0{0%{opacity:1}23.077%{opacity:1}23.087%,100%{opacity:.5}}
@keyframes l03d-p0{0%,-0.01%{opacity:0;transform:translateX(0)}0%{opacity:1;transform:translateX(0)}18.462%{opacity:1;transform:translateX(-236px)}23.077%{opacity:1;transform:translateX(-236px)}23.087%,100%{opacity:0;transform:translateX(-236px)}}
.l03d-g0 rect,.l03d-g0 line,.l03d-g0 path:not(.l03d-gl){animation-name:l03d-g0}.l03d-p0{animation-name:l03d-p0}
@keyframes l03d-g1{0%,23.067%{opacity:.5}23.077%{opacity:1}46.154%{opacity:1}46.164%,100%{opacity:.5}}
@keyframes l03d-p1{0%,23.067%{opacity:0;transform:translateX(0)}23.077%{opacity:1;transform:translateX(0)}41.538%{opacity:1;transform:translateX(506px)}46.154%{opacity:1;transform:translateX(506px)}46.164%,100%{opacity:0;transform:translateX(506px)}}
.l03d-g1 rect,.l03d-g1 line,.l03d-g1 path:not(.l03d-gl){animation-name:l03d-g1}.l03d-p1{animation-name:l03d-p1}
@keyframes l03d-g2{0%,46.144%{opacity:.5}46.154%{opacity:1}69.231%{opacity:1}69.241%,100%{opacity:.5}}
@keyframes l03d-p2{0%,46.144%{opacity:0;transform:translateX(0)}46.154%{opacity:1;transform:translateX(0)}64.615%{opacity:1;transform:translateX(236px)}69.231%{opacity:1;transform:translateX(236px)}69.241%,100%{opacity:0;transform:translateX(236px)}}
.l03d-g2 rect,.l03d-g2 line,.l03d-g2 path:not(.l03d-gl){animation-name:l03d-g2}.l03d-p2{animation-name:l03d-p2}
@keyframes l03d-g3{0%,69.221%{opacity:.5}69.231%{opacity:1}84.615%{opacity:1}84.625%,100%{opacity:.5}}
.l03d-g3 rect,.l03d-g3 line,.l03d-g3 path:not(.l03d-gl){animation-name:l03d-g3}
@keyframes l03d-g4{0%,84.605%{opacity:.5}84.615%{opacity:1}100%{opacity:1}100.01%,100%{opacity:.5}}
.l03d-g4 rect,.l03d-g4 line,.l03d-g4 path:not(.l03d-gl){animation-name:l03d-g4}
</style>
<defs>
<marker id="l03d-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="l03d-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="l03d-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<line class="l03d-life" x1="110" y1="72" x2="110" y2="591"/>
<line class="l03d-life" x1="380" y1="72" x2="380" y2="591"/>
<line class="l03d-life" x1="650" y1="72" x2="650" y2="591"/>
<rect class="l03d-box" x="20" y="10" width="180" height="62" rx="10"/><text class="l03d-ttl" x="110" y="36">Attacker</text><text class="l03d-sub" x="110" y="56">on their own device</text>
<rect class="l03d-hot" x="290" y="10" width="180" height="62" rx="10"/><text class="l03d-ttl" x="380" y="36">Authorization server</text><text class="l03d-sub" x="380" y="56">supports PKCE, no mandate</text>
<rect class="l03d-box" x="560" y="10" width="180" height="62" rx="10"/><text class="l03d-ttl" x="650" y="36">Victim's client</text><text class="l03d-sub" x="650" y="56">no use or check of state</text>
<g class="l03d-g l03d-g0">
<text class="l03d-main l03d-badt" x="245" y="108">starts a flow,</text>
<text class="l03d-dim" x="245" y="124">code_challenge stripped</text>
<line class="l03d-bad" x1="124" y1="138" x2="366" y2="138" marker-end="url(#l03d-m-bad)"/>
<circle class="l03d-badge l03d-b-bad" cx="110" cy="138" r="12"/><text class="l03d-bt" x="110" y="142.5">1</text>
<text class="l03d-main l03d-badt" x="245" y="178">an unbound code</text>
<line class="l03d-bad" x1="366" y1="192" x2="124" y2="192" marker-end="url(#l03d-m-bad)"/>
</g>
<g class="l03d-g l03d-g1">
<text class="l03d-main l03d-badt" x="380" y="232">sends the victim's browser to the response URL</text>
<text class="l03d-dim" x="380" y="248">carrying that unbound code</text>
<line class="l03d-bad" x1="124" y1="262" x2="636" y2="262" marker-end="url(#l03d-m-bad)"/>
<circle class="l03d-badge l03d-b-bad" cx="110" cy="262" r="12"/><text class="l03d-bt" x="110" y="266.5">2</text>
</g>
<g class="l03d-g l03d-g2">
<text class="l03d-main" x="515" y="302">the code and the code_verifier</text>
<line class="l03d-back" x1="636" y1="316" x2="394" y2="316" marker-end="url(#l03d-m-back)"/>
<circle class="l03d-badge l03d-b-back" cx="650" cy="316" r="12"/><text class="l03d-bt" x="650" y="320.5">3</text>
<text class="l03d-main l03d-badt" x="515" y="356">a token for the attacker's account</text>
<line class="l03d-bad" x1="394" y1="370" x2="636" y2="370" marker-end="url(#l03d-m-bad)"/>
</g>
<g class="l03d-g l03d-g3">
<rect class="l03d-note-bad" x="276" y="404" width="208" height="48" rx="8"/>
<text class="l03d-nt" x="380" y="425">no stored challenge:</text>
<text class="l03d-nt" x="380" y="442">the AS ignores the verifier</text>
<circle class="l03d-badge l03d-b-bad" cx="276" cy="428" r="12"/><text class="l03d-bt" x="276" y="432.5">!</text>
</g>
<g class="l03d-g l03d-g4">
<rect class="l03d-note-good" x="220" y="480" width="320" height="65" rx="8"/>
<text class="l03d-nt" x="380" y="501">Fix: the AS must reject a token request with</text>
<text class="l03d-nt" x="380" y="518">a code_verifier when no challenge was in</text>
<text class="l03d-nt" x="380" y="535">the authorization request</text>
<circle class="l03d-badge l03d-b-good" cx="220" cy="512" r="12"/><text class="l03d-bt" x="220" y="517.0">4</text>
</g>
<circle class="l03d-pk l03d-p0 l03d-pkbad" cx="360" cy="192" r="5.5"/>
<circle class="l03d-pk l03d-p1 l03d-pkbad" cx="130" cy="262" r="5.5"/>
<circle class="l03d-pk l03d-p2 l03d-pkbad" cx="400" cy="370" r="5.5"/>
<line class="l03d-front" x1="40" y1="619" x2="70" y2="619"/>
<text class="l03d-dim" x="78" y="623" style="text-anchor:start">normal event</text>
<line class="l03d-back" x1="188" y1="619" x2="218" y2="619"/>
<text class="l03d-dim" x="226" y="623" style="text-anchor:start">direct request, not a redirect</text>
<line class="l03d-bad" x1="452" y1="619" x2="482" y2="619"/>
<text class="l03d-dim" x="490" y="623" style="text-anchor:start">the attack</text>
<rect class="l03d-note-good" x="588" y="611" width="22" height="16" rx="4"/>
<text class="l03d-dim" x="618" y="623" style="text-anchor:start">the fix</text>
</svg>
</div>
</div>
<!-- /diagram:oauth-pkce-downgrade -->

The attack in order, with its preconditions in the lane labels. Red marks the attack path; the green note is the fix. The badges number this diagram's own steps (1 to 4).

- **PKCE downgrade** (section 4.8). Preconditions: the AS supports PKCE but does not mandate it, so the presence of `code_challenge` acts as a switch the attacker controls, and the client does not use or check `state`. The attacker starts a flow on their own device, strips `code_challenge`, and sends the victim's browser to the response URL carrying that unbound code. The client sends `code_verifier`; the AS sees no stored challenge and ignores it; the client ends up with a token for the attacker's account. **Fix**: the AS must reject a token request containing a `code_verifier` when no challenge was in the authorization request. An AS that mandates PKCE gets this for free.

<!-- diagram:oauth-mix-up -->
<div class="l03e-wrap" style="position:relative">
<input type="checkbox" id="l03e-pause" class="l03e-cb" /><label for="l03e-pause" class="l03e-btn"><span class="l03e-off">Pause animation</span><span class="l03e-on">Play animation</span></label>
<div class="l03e-box" style="overflow-x:auto">
<svg class="l03e-flow" viewBox="0 0 760 621" role="img" aria-labelledby="l03e-t l03e-d" style="width:760px;max-width:100%;min-width:699px;height:auto;display:block;margin:0 auto">
<title id="l03e-t">Mix-up attack (RFC 9700, section 4.4)</title>
<desc id="l03e-d">Three parties: a client that talks to two or more authorization servers, a hostile AS and an honest AS. Step 1: the client starts a flow with the hostile AS. Step 2: the hostile AS redirects the user to the honest AS using the honest client's ID. Step 3: the code returns to the client, which believes it came from the hostile AS. Step 4: the client redeems it at the hostile token endpoint. Defences: the client stores, per request, the issuer it sent the request to, bound to the user agent, because storing only the AS URL is insufficient; and with issuer identification (RFC 9207) it compares the iss in the response with the stored issuer and aborts on a mismatch. The diagram highlights each step in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
<style>
svg.l03e-flow{--ink:light-dark(#000000,#ffffff)}
.l03e-box{fill:var(--panel);stroke:var(--border-strong);stroke-width:1.5}
.l03e-hot{fill:var(--panel);stroke:var(--accent);stroke-width:2.5}
.l03e-ttl{fill:var(--ink);font:600 15px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l03e-sub{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l03e-life{stroke:var(--border-strong);stroke-width:1.5;stroke-dasharray:4 5}
.l03e-front{stroke:var(--accent);stroke-width:2;fill:none}
.l03e-back{stroke:var(--muted);stroke-width:2;stroke-dasharray:7 5;fill:none}
.l03e-bad{stroke:var(--bad);stroke-width:2;fill:none}
.l03e-main{fill:var(--ink);font:600 13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l03e-badt{fill:var(--ink)}
.l03e-dim{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l03e-badge{fill:var(--accent)}
.l03e-b-back{fill:var(--muted)}
.l03e-b-bad{fill:var(--bad)}
.l03e-b-good{fill:var(--good)}
.l03e-bt{fill:var(--on-accent);font:700 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l03e-note{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l03e-note-good{fill:var(--good-bg);stroke:var(--good);stroke-width:1.5}
.l03e-note-bad{fill:var(--bad-bg);stroke:var(--bad);stroke-width:1.5}
.l03e-nt{fill:var(--ink);font:500 12.5px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l03e-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:32s;animation-timing-function:linear;animation-iteration-count:infinite}
.l03e-pk.l03e-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.l03e-pk.l03e-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.l03e-wrap{margin:20px 0}
@media (min-width:801px){.l03e-wrap{margin-left:-44px;margin-right:-44px}}
.l03e-g rect,.l03e-g line,.l03e-g path:not(.l03e-gl){opacity:.5;animation-duration:32s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.l03e-flow:hover .l03e-g rect,svg.l03e-flow:hover .l03e-g line,svg.l03e-flow:hover .l03e-g path:not(.l03e-gl),svg.l03e-flow:hover .l03e-pk{animation-play-state:paused}
.l03e-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.l03e-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.l03e-btn:hover{background:var(--hover)}
.l03e-cb:focus-visible + .l03e-btn{outline:2px solid var(--accent);outline-offset:2px}
.l03e-cb:checked + .l03e-btn .l03e-off,.l03e-cb:not(:checked) + .l03e-btn .l03e-on{display:none}
.l03e-cb:checked ~ .l03e-box .l03e-g rect,.l03e-cb:checked ~ .l03e-box .l03e-g line,.l03e-cb:checked ~ .l03e-box .l03e-g path:not(.l03e-gl),.l03e-cb:checked ~ .l03e-box .l03e-pk{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.l03e-g rect,.l03e-g line,.l03e-g path:not(.l03e-gl){animation:none;opacity:1}.l03e-pk{animation:none;display:none}.l03e-btn{display:none}}
@keyframes l03e-g0{0%{opacity:1}18.75%{opacity:1}18.76%,100%{opacity:.5}}
@keyframes l03e-p0{0%,-0.01%{opacity:0;transform:translateX(0)}0%{opacity:1;transform:translateX(0)}15%{opacity:1;transform:translateX(236px)}18.75%{opacity:1;transform:translateX(236px)}18.76%,100%{opacity:0;transform:translateX(236px)}}
.l03e-g0 rect,.l03e-g0 line,.l03e-g0 path:not(.l03e-gl){animation-name:l03e-g0}.l03e-p0{animation-name:l03e-p0}
@keyframes l03e-g1{0%,18.74%{opacity:.5}18.75%{opacity:1}37.5%{opacity:1}37.51%,100%{opacity:.5}}
@keyframes l03e-p1{0%,18.74%{opacity:0;transform:translateX(0)}18.75%{opacity:1;transform:translateX(0)}33.75%{opacity:1;transform:translateX(236px)}37.5%{opacity:1;transform:translateX(236px)}37.51%,100%{opacity:0;transform:translateX(236px)}}
.l03e-g1 rect,.l03e-g1 line,.l03e-g1 path:not(.l03e-gl){animation-name:l03e-g1}.l03e-p1{animation-name:l03e-p1}
@keyframes l03e-g2{0%,37.49%{opacity:.5}37.5%{opacity:1}56.25%{opacity:1}56.26%,100%{opacity:.5}}
@keyframes l03e-p2{0%,37.49%{opacity:0;transform:translateX(0)}37.5%{opacity:1;transform:translateX(0)}52.5%{opacity:1;transform:translateX(-506px)}56.25%{opacity:1;transform:translateX(-506px)}56.26%,100%{opacity:0;transform:translateX(-506px)}}
.l03e-g2 rect,.l03e-g2 line,.l03e-g2 path:not(.l03e-gl){animation-name:l03e-g2}.l03e-p2{animation-name:l03e-p2}
@keyframes l03e-g3{0%,56.24%{opacity:.5}56.25%{opacity:1}75%{opacity:1}75.01%,100%{opacity:.5}}
@keyframes l03e-p3{0%,56.24%{opacity:0;transform:translateX(0)}56.25%{opacity:1;transform:translateX(0)}71.25%{opacity:1;transform:translateX(236px)}75%{opacity:1;transform:translateX(236px)}75.01%,100%{opacity:0;transform:translateX(236px)}}
.l03e-g3 rect,.l03e-g3 line,.l03e-g3 path:not(.l03e-gl){animation-name:l03e-g3}.l03e-p3{animation-name:l03e-p3}
@keyframes l03e-g4{0%,74.99%{opacity:.5}75%{opacity:1}87.5%{opacity:1}87.51%,100%{opacity:.5}}
.l03e-g4 rect,.l03e-g4 line,.l03e-g4 path:not(.l03e-gl){animation-name:l03e-g4}
@keyframes l03e-g5{0%,87.49%{opacity:.5}87.5%{opacity:1}100%{opacity:1}100.01%,100%{opacity:.5}}
.l03e-g5 rect,.l03e-g5 line,.l03e-g5 path:not(.l03e-gl){animation-name:l03e-g5}
</style>
<defs>
<marker id="l03e-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="l03e-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="l03e-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<line class="l03e-life" x1="110" y1="72" x2="110" y2="569"/>
<line class="l03e-life" x1="380" y1="72" x2="380" y2="569"/>
<line class="l03e-life" x1="650" y1="72" x2="650" y2="569"/>
<rect class="l03e-box" x="20" y="10" width="180" height="62" rx="10"/><text class="l03e-ttl" x="110" y="36">Client</text><text class="l03e-sub" x="110" y="56">uses two or more ASes</text>
<rect class="l03e-box" x="290" y="10" width="180" height="62" rx="10"/><text class="l03e-ttl" x="380" y="36">Hostile AS</text><text class="l03e-sub" x="380" y="56">the one that is hostile</text>
<rect class="l03e-hot" x="560" y="10" width="180" height="62" rx="10"/><text class="l03e-ttl" x="650" y="36">Honest AS</text><text class="l03e-sub" x="650" y="56">the other AS</text>
<g class="l03e-g l03e-g0">
<text class="l03e-main" x="245" y="108">starts a flow with</text>
<text class="l03e-dim" x="245" y="124">the hostile AS</text>
<line class="l03e-front" x1="124" y1="138" x2="366" y2="138" marker-end="url(#l03e-m-front)"/>
<circle class="l03e-badge l03e-b-front" cx="110" cy="138" r="12"/><text class="l03e-bt" x="110" y="142.5">1</text>
</g>
<g class="l03e-g l03e-g1">
<text class="l03e-main l03e-badt" x="515" y="178">redirects the user to the honest AS</text>
<text class="l03e-dim" x="515" y="194">using the honest client's ID</text>
<line class="l03e-bad" x1="394" y1="208" x2="636" y2="208" marker-end="url(#l03e-m-bad)"/>
<circle class="l03e-badge l03e-b-bad" cx="380" cy="208" r="12"/><text class="l03e-bt" x="380" y="212.5">2</text>
</g>
<g class="l03e-g l03e-g2">
<text class="l03e-main l03e-badt" x="380" y="248">the code returns to the client, which</text>
<text class="l03e-dim" x="380" y="264">believes it came from the hostile AS</text>
<line class="l03e-bad" x1="636" y1="278" x2="124" y2="278" marker-end="url(#l03e-m-bad)"/>
<circle class="l03e-badge l03e-b-bad" cx="650" cy="278" r="12"/><text class="l03e-bt" x="650" y="282.5">3</text>
</g>
<g class="l03e-g l03e-g3">
<text class="l03e-main l03e-badt" x="245" y="318">redeems the code at the</text>
<text class="l03e-dim" x="245" y="334">hostile token endpoint</text>
<line class="l03e-bad" x1="124" y1="348" x2="366" y2="348" marker-end="url(#l03e-m-bad)"/>
<circle class="l03e-badge l03e-b-bad" cx="110" cy="348" r="12"/><text class="l03e-bt" x="110" y="352.5">4</text>
</g>
<g class="l03e-g l03e-g4">
<rect class="l03e-note-good" x="10" y="382" width="307" height="65" rx="8"/>
<text class="l03e-nt" x="164" y="403">Store, per request, the issuer it was sent</text>
<text class="l03e-nt" x="164" y="420">to, bound to the user agent. The AS URL</text>
<text class="l03e-nt" x="164" y="437">alone is insufficient</text>
<circle class="l03e-badge l03e-b-good" cx="10" cy="414" r="12"/><text class="l03e-bt" x="10" y="419.0">5</text>
</g>
<g class="l03e-g l03e-g5">
<rect class="l03e-note-good" x="10" y="475" width="307" height="48" rx="8"/>
<text class="l03e-nt" x="164" y="496">RFC 9207: compare iss in the response with</text>
<text class="l03e-nt" x="164" y="513">the stored issuer; a mismatch means abort</text>
<circle class="l03e-badge l03e-b-good" cx="10" cy="499" r="12"/><text class="l03e-bt" x="10" y="503.5">6</text>
</g>
<circle class="l03e-pk l03e-p0" cx="130" cy="138" r="5.5"/>
<circle class="l03e-pk l03e-p1 l03e-pkbad" cx="400" cy="208" r="5.5"/>
<circle class="l03e-pk l03e-p2 l03e-pkbad" cx="630" cy="278" r="5.5"/>
<circle class="l03e-pk l03e-p3 l03e-pkbad" cx="130" cy="348" r="5.5"/>
<line class="l03e-front" x1="40" y1="597" x2="70" y2="597"/>
<text class="l03e-dim" x="78" y="601" style="text-anchor:start">normal event</text>
<line class="l03e-bad" x1="188" y1="597" x2="218" y2="597"/>
<text class="l03e-dim" x="226" y="601" style="text-anchor:start">the attack</text>
<rect class="l03e-note-good" x="324" y="589" width="22" height="16" rx="4"/>
<text class="l03e-dim" x="354" y="601" style="text-anchor:start">defences</text>
</svg>
</div>
</div>
<!-- /diagram:oauth-mix-up -->

The user reaches the honest AS, but the code lands at a client that thinks it came from the hostile one. The green notes are the two defences listed below. The badges number this diagram's own steps (1 to 6).

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

<!-- diagram:oauth-token-confusion -->
<div class="l03f-wrap" style="position:relative">
<input type="checkbox" id="l03f-pause" class="l03f-cb" /><label for="l03f-pause" class="l03f-btn"><span class="l03f-off">Pause animation</span><span class="l03f-on">Play animation</span></label>
<div class="l03f-box" style="overflow-x:auto">
<svg class="l03f-flow" viewBox="0 0 760 630" role="img" aria-labelledby="l03f-t l03f-d" style="width:760px;max-width:100%;min-width:699px;height:auto;display:block;margin:0 auto">
<title id="l03f-t">Which controls check the token type</title>
<desc id="l03f-d">A matrix of five controls against two questions: what the control tells the resource server, and whether it checks the token type. The typ value at+jwt checks the type, because ID tokens must not be accepted as access tokens. A distinct aud for access tokens issued for distinct resources checks it too. Introspection active: true only means the AS issued the token, has not revoked it and it is within its validity window. DPoP binds a token to a key, which says who may present it, not what kind of token it is. Separate signing keys for ID tokens and access tokens neither contain a leaked key nor make the RS reject an ID-token signature. The diagram highlights each row in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
<style>
svg.l03f-flow{--ink:light-dark(#000000,#ffffff)}
.l03f-box{fill:var(--panel);stroke:var(--border-strong);stroke-width:1.5}
.l03f-hot{fill:var(--panel);stroke:var(--accent);stroke-width:2.5}
.l03f-ttl{fill:var(--ink);font:600 15px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l03f-sub{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l03f-life{stroke:var(--border-strong);stroke-width:1.5;stroke-dasharray:4 5}
.l03f-front{stroke:var(--accent);stroke-width:2;fill:none}
.l03f-back{stroke:var(--muted);stroke-width:2;stroke-dasharray:7 5;fill:none}
.l03f-bad{stroke:var(--bad);stroke-width:2;fill:none}
.l03f-main{fill:var(--ink);font:600 13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l03f-badt{fill:var(--ink)}
.l03f-dim{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l03f-badge{fill:var(--accent)}
.l03f-b-back{fill:var(--muted)}
.l03f-b-bad{fill:var(--bad)}
.l03f-b-good{fill:var(--good)}
.l03f-bt{fill:var(--on-accent);font:700 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l03f-note{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l03f-note-good{fill:var(--good-bg);stroke:var(--good);stroke-width:1.5}
.l03f-note-bad{fill:var(--bad-bg);stroke:var(--bad);stroke-width:1.5}
.l03f-nt{fill:var(--ink);font:500 12.5px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l03f-nest{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l03f-row{fill:var(--raised);stroke:var(--border-strong);stroke-width:1}
.l03f-ttlL{fill:var(--ink);font:600 14px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l03f-subL{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l03f-dimL{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l03f-dimR{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:end}
.l03f-conn{stroke:var(--accent);stroke-width:1.5;fill:none}
.l03f-edge{stroke:var(--border-strong);stroke-width:1.75;fill:none}
.l03f-hl{fill:none;stroke:var(--accent);stroke-width:3}
.l03f-hle{stroke:var(--accent);stroke-width:3;fill:none}
.l03f-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:20s;animation-timing-function:linear;animation-iteration-count:infinite}
.l03f-pk.l03f-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.l03f-pk.l03f-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.l03f-wrap{margin:20px 0}
@media (min-width:801px){.l03f-wrap{margin-left:-44px;margin-right:-44px}}
.l03f-g rect,.l03f-g line,.l03f-g path:not(.l03f-gl){opacity:.5;animation-duration:20s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.l03f-flow:hover .l03f-g rect,svg.l03f-flow:hover .l03f-g line,svg.l03f-flow:hover .l03f-g path:not(.l03f-gl),svg.l03f-flow:hover .l03f-pk{animation-play-state:paused}
.l03f-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.l03f-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.l03f-btn:hover{background:var(--hover)}
.l03f-cb:focus-visible + .l03f-btn{outline:2px solid var(--accent);outline-offset:2px}
.l03f-cb:checked + .l03f-btn .l03f-off,.l03f-cb:not(:checked) + .l03f-btn .l03f-on{display:none}
.l03f-cb:checked ~ .l03f-box .l03f-g rect,.l03f-cb:checked ~ .l03f-box .l03f-g line,.l03f-cb:checked ~ .l03f-box .l03f-g path:not(.l03f-gl),.l03f-cb:checked ~ .l03f-box .l03f-pk{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.l03f-g rect,.l03f-g line,.l03f-g path:not(.l03f-gl){animation:none;opacity:1}.l03f-pk{animation:none;display:none}.l03f-btn{display:none}}
@keyframes l03f-g0{0%{opacity:1}20%{opacity:1}20.01%,100%{opacity:.5}}
.l03f-g0 rect,.l03f-g0 line,.l03f-g0 path:not(.l03f-gl){animation-name:l03f-g0}
@keyframes l03f-g1{0%,19.99%{opacity:.5}20%{opacity:1}40%{opacity:1}40.01%,100%{opacity:.5}}
.l03f-g1 rect,.l03f-g1 line,.l03f-g1 path:not(.l03f-gl){animation-name:l03f-g1}
@keyframes l03f-g2{0%,39.99%{opacity:.5}40%{opacity:1}60%{opacity:1}60.01%,100%{opacity:.5}}
.l03f-g2 rect,.l03f-g2 line,.l03f-g2 path:not(.l03f-gl){animation-name:l03f-g2}
@keyframes l03f-g3{0%,59.99%{opacity:.5}60%{opacity:1}80%{opacity:1}80.01%,100%{opacity:.5}}
.l03f-g3 rect,.l03f-g3 line,.l03f-g3 path:not(.l03f-gl){animation-name:l03f-g3}
@keyframes l03f-g4{0%,79.99%{opacity:.5}80%{opacity:1}100%{opacity:1}100.01%,100%{opacity:.5}}
.l03f-g4 rect,.l03f-g4 line,.l03f-g4 path:not(.l03f-gl){animation-name:l03f-g4}
</style>
<defs>
<marker id="l03f-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="l03f-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="l03f-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<rect class="l03f-box" x="240" y="10" width="247" height="62" rx="10"/><text class="l03f-ttl" x="364" y="36">What it tells the RS</text><text class="l03f-sub" x="364" y="56"></text>
<rect class="l03f-box" x="495" y="10" width="247" height="62" rx="10"/><text class="l03f-ttl" x="618" y="36">Checks the token type?</text><text class="l03f-sub" x="618" y="56"></text>
<g class="l03f-g l03f-g0">
<rect class="l03f-row" x="10" y="86" width="740" height="86" rx="8"/>
<text class="l03f-ttlL" x="24" y="112">typ: at+jwt</text>
<text class="l03f-nt" x="364" y="134">ID tokens must not be accepted as</text>
<text class="l03f-nt" x="364" y="149">access tokens, hence typ</text>
<circle cx="618" cy="108" r="10" style="fill:var(--good)"/><path class="l03f-gl" d="M614.3,108.0 L617.1,111.4 L622.7,104.6" style="fill:none;stroke:var(--on-accent);stroke-width:2;stroke-linecap:round;stroke-linejoin:round"/>
<text class="l03f-nt" x="618" y="134">Yes: checked by typ</text>
</g>
<g class="l03f-g l03f-g1">
<rect class="l03f-row" x="10" y="180" width="740" height="86" rx="8"/>
<text class="l03f-ttlL" x="24" y="206">aud</text>
<text class="l03f-nt" x="364" y="228">The AS must use a distinct aud for</text>
<text class="l03f-nt" x="364" y="243">access tokens for distinct resources</text>
<circle cx="618" cy="202" r="10" style="fill:var(--good)"/><path class="l03f-gl" d="M614.3,202.0 L617.1,205.4 L622.7,198.6" style="fill:none;stroke:var(--on-accent);stroke-width:2;stroke-linecap:round;stroke-linejoin:round"/>
<text class="l03f-nt" x="618" y="228">Yes: checked by aud</text>
</g>
<g class="l03f-g l03f-g2">
<rect class="l03f-row" x="10" y="274" width="740" height="101" rx="8"/>
<text class="l03f-ttlL" x="24" y="300">Introspection active: true</text>
<text class="l03f-nt" x="364" y="322">Only that the AS issued the token,</text>
<text class="l03f-nt" x="364" y="337">has not revoked it and it is within</text>
<text class="l03f-nt" x="364" y="352">its validity window</text>
<circle cx="618" cy="296" r="10" style="fill:var(--bad)"/><path class="l03f-gl" d="M615.1,292.6 L621.9,299.4 M621.9,292.6 L615.1,299.4" style="fill:none;stroke:var(--on-accent);stroke-width:2;stroke-linecap:round;stroke-linejoin:round"/>
<text class="l03f-nt" x="618" y="322">No</text>
</g>
<g class="l03f-g l03f-g3">
<rect class="l03f-row" x="10" y="383" width="740" height="86" rx="8"/>
<text class="l03f-ttlL" x="24" y="409">DPoP key binding</text>
<text class="l03f-nt" x="364" y="431">Who may present the token,</text>
<text class="l03f-nt" x="364" y="446">not what kind of token it is</text>
<circle cx="618" cy="405" r="10" style="fill:var(--bad)"/><path class="l03f-gl" d="M615.1,401.6 L621.9,408.4 M621.9,401.6 L615.1,408.4" style="fill:none;stroke:var(--on-accent);stroke-width:2;stroke-linecap:round;stroke-linejoin:round"/>
<text class="l03f-nt" x="618" y="431">No</text>
</g>
<g class="l03f-g l03f-g4">
<rect class="l03f-row" x="10" y="477" width="740" height="101" rx="8"/>
<text class="l03f-ttlL" x="24" y="503">Separate signing keys</text>
<text class="l03f-nt" x="364" y="525">Neither contains a leaked key nor</text>
<text class="l03f-nt" x="364" y="540">makes the RS reject an ID-token</text>
<text class="l03f-nt" x="364" y="555">signature</text>
<circle cx="618" cy="499" r="10" style="fill:var(--bad)"/><path class="l03f-gl" d="M615.1,495.6 L621.9,502.4 M621.9,495.6 L615.1,502.4" style="fill:none;stroke:var(--on-accent);stroke-width:2;stroke-linecap:round;stroke-linejoin:round"/>
<text class="l03f-nt" x="618" y="525">No</text>
</g>
<circle cx="48" cy="606" r="8" style="fill:var(--good)"/><path class="l03f-gl" d="M44.6,606.0 L46.9,608.7 L51.4,603.3" style="fill:none;stroke:var(--on-accent);stroke-width:2;stroke-linecap:round;stroke-linejoin:round"/>
<text class="l03f-dim" x="64" y="610" style="text-anchor:start">checks the token type</text>
<circle cx="240" cy="606" r="8" style="fill:var(--bad)"/><path class="l03f-gl" d="M237.3,603.3 L242.7,608.7 M242.7,603.3 L237.3,608.7" style="fill:none;stroke:var(--on-accent);stroke-width:2;stroke-linecap:round;stroke-linejoin:round"/>
<text class="l03f-dim" x="256" y="610" style="text-anchor:start">does not check the type</text>
</svg>
</div>
</div>
<!-- /diagram:oauth-token-confusion -->

Each row is a control from the bullet above, read against one question: does it check the token type? Only `typ` and `aud` do.

- **Introspection** (RFC 7662): `active` is required, the endpoint needs its own authorization, and caching trades freshness for load. RFC 7009 notes that revoking a self-contained token immediately needs non-standardized back-end signalling.
- **Audience and resource** (RFC 8707): the `resource` parameter is an absolute URI without a fragment; the AS should audience-restrict to it and may answer `invalid_target`. RFC 9068 (section 5) adds that with several resources the AS should make each scope in the token unambiguously attributable to one of them. Scope is typically about what access is wanted rather than where (RFC 8707), though RFC 9700 notes a client can also indicate the RS by encoding it in the scope value. RFC 9700 prefers a single RS or a small set, and further restriction by scope or `authorization_details` (RFC 9396).

## Sender-constrained tokens

RFC 9700 says ASes and RSes should sender-constrain access tokens, and public-client refresh tokens must be sender-constrained or rotated.

- **mutual TLS** (RFC 8705): the AS binds the token to the client certificate; in a JWT, `cnf` carries `x5t#S256`, the base64url SHA-256 of the DER certificate. The RS takes the certificate from its TLS layer; on mismatch it returns 401 `invalid_token`. RFC 9700 notes that mutual TLS lets one token serve several RSes, while audience-restricted tokens need one per RS.
- **DPoP** (RFC 9449): application-level, usable by public clients. Each request carries a `DPoP` header holding a JWT with `typ` `dpop+jwt`, the public key in `jwk`, and claims `jti`, `htm`, `htu`, `iat`, plus `ath` (a hash of the access token) at the RS and `nonce` where the server supplied one. The token response has `token_type` `DPoP`, the token is presented as `Authorization: DPoP <token>`, and a JWT token is bound through `cnf` `jkt`, the key's JWK thumbprint. The server may demand a nonce with `use_dpop_nonce`; a server must accept a proof only for a limited time after its creation (RFC 9449, section 11.1) and can store `jti` values for that window to make proofs single-use, which may not be feasible without shared state; RFC 9700 expects the RS to prevent replay.

<!-- diagram:oauth-dpop-proof -->
<div class="l03g-wrap" style="position:relative">
<input type="checkbox" id="l03g-pause" class="l03g-cb" /><label for="l03g-pause" class="l03g-btn"><span class="l03g-off">Pause animation</span><span class="l03g-on">Play animation</span></label>
<div class="l03g-box" style="overflow-x:auto">
<svg class="l03g-flow" viewBox="0 0 760 398" role="img" aria-labelledby="l03g-t l03g-d" style="width:760px;max-width:100%;min-width:699px;height:auto;display:block;margin:0 auto">
<title id="l03g-t">A DPoP request and what the server does with each part</title>
<desc id="l03g-d">A nested diagram. A request presents the token as Authorization: DPoP followed by the token, and carries a DPoP header holding a JWT with typ dpop+jwt. The JWT holds the public key in jwk, the claims jti, htm, htu and iat, ath (a hash of the access token) at the RS, and nonce where the server supplied one. In the token response token_type is DPoP, and a JWT token is bound through cnf jkt, the key's JWK thumbprint. A server must accept a proof only for a limited time after its creation, can store jti values for that window to make proofs single-use, which may not be feasible without shared state, and may demand a nonce with use_dpop_nonce. The diagram highlights each part in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
<style>
svg.l03g-flow{--ink:light-dark(#000000,#ffffff)}
.l03g-box{fill:var(--panel);stroke:var(--border-strong);stroke-width:1.5}
.l03g-hot{fill:var(--panel);stroke:var(--accent);stroke-width:2.5}
.l03g-ttl{fill:var(--ink);font:600 15px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l03g-sub{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l03g-life{stroke:var(--border-strong);stroke-width:1.5;stroke-dasharray:4 5}
.l03g-front{stroke:var(--accent);stroke-width:2;fill:none}
.l03g-back{stroke:var(--muted);stroke-width:2;stroke-dasharray:7 5;fill:none}
.l03g-bad{stroke:var(--bad);stroke-width:2;fill:none}
.l03g-main{fill:var(--ink);font:600 13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l03g-badt{fill:var(--ink)}
.l03g-dim{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l03g-badge{fill:var(--accent)}
.l03g-b-back{fill:var(--muted)}
.l03g-b-bad{fill:var(--bad)}
.l03g-b-good{fill:var(--good)}
.l03g-bt{fill:var(--on-accent);font:700 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l03g-note{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l03g-note-good{fill:var(--good-bg);stroke:var(--good);stroke-width:1.5}
.l03g-note-bad{fill:var(--bad-bg);stroke:var(--bad);stroke-width:1.5}
.l03g-nt{fill:var(--ink);font:500 12.5px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l03g-nest{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l03g-row{fill:var(--raised);stroke:var(--border-strong);stroke-width:1}
.l03g-ttlL{fill:var(--ink);font:600 14px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l03g-subL{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l03g-dimL{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l03g-dimR{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:end}
.l03g-conn{stroke:var(--accent);stroke-width:1.5;fill:none}
.l03g-edge{stroke:var(--border-strong);stroke-width:1.75;fill:none}
.l03g-hl{fill:none;stroke:var(--accent);stroke-width:3}
.l03g-hle{stroke:var(--accent);stroke-width:3;fill:none}
.l03g-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:24s;animation-timing-function:linear;animation-iteration-count:infinite}
.l03g-pk.l03g-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.l03g-pk.l03g-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.l03g-wrap{margin:20px 0}
@media (min-width:801px){.l03g-wrap{margin-left:-44px;margin-right:-44px}}
.l03g-g rect,.l03g-g line,.l03g-g path:not(.l03g-gl){opacity:.5;animation-duration:24s;animation-timing-function:linear;animation-iteration-count:infinite}
.l03g-h{opacity:0;animation-duration:24s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.l03g-flow:hover .l03g-g rect,svg.l03g-flow:hover .l03g-g line,svg.l03g-flow:hover .l03g-g path:not(.l03g-gl),svg.l03g-flow:hover .l03g-pk,svg.l03g-flow:hover .l03g-h{animation-play-state:paused}
.l03g-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.l03g-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.l03g-btn:hover{background:var(--hover)}
.l03g-cb:focus-visible + .l03g-btn{outline:2px solid var(--accent);outline-offset:2px}
.l03g-cb:checked + .l03g-btn .l03g-off,.l03g-cb:not(:checked) + .l03g-btn .l03g-on{display:none}
.l03g-cb:checked ~ .l03g-box .l03g-g rect,.l03g-cb:checked ~ .l03g-box .l03g-g line,.l03g-cb:checked ~ .l03g-box .l03g-g path:not(.l03g-gl),.l03g-cb:checked ~ .l03g-box .l03g-pk,.l03g-cb:checked ~ .l03g-box .l03g-h{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.l03g-g rect,.l03g-g line,.l03g-g path:not(.l03g-gl){animation:none;opacity:1}.l03g-pk{animation:none;display:none}.l03g-h{animation:none;opacity:0}.l03g-btn{display:none}}
@keyframes l03g-g0{0%{opacity:1}20%{opacity:1}20.01%,100%{opacity:.5}}
@keyframes l03g-h0{0%{opacity:1}20%{opacity:1}20.01%,100%{opacity:0}}
.l03g-g0 rect,.l03g-g0 line,.l03g-g0 path:not(.l03g-gl){animation-name:l03g-g0}.l03g-h0{animation-name:l03g-h0}
@keyframes l03g-g1{0%,19.99%{opacity:.5}20%{opacity:1}40%{opacity:1}40.01%,100%{opacity:.5}}
@keyframes l03g-h1{0%,19.99%{opacity:0}20%{opacity:1}40%{opacity:1}40.01%,100%{opacity:0}}
.l03g-g1 rect,.l03g-g1 line,.l03g-g1 path:not(.l03g-gl){animation-name:l03g-g1}.l03g-h1{animation-name:l03g-h1}
@keyframes l03g-g2{0%,39.99%{opacity:.5}40%{opacity:1}60%{opacity:1}60.01%,100%{opacity:.5}}
@keyframes l03g-h2{0%,39.99%{opacity:0}40%{opacity:1}60%{opacity:1}60.01%,100%{opacity:0}}
.l03g-g2 rect,.l03g-g2 line,.l03g-g2 path:not(.l03g-gl){animation-name:l03g-g2}.l03g-h2{animation-name:l03g-h2}
@keyframes l03g-g3{0%,59.99%{opacity:.5}60%{opacity:1}80%{opacity:1}80.01%,100%{opacity:.5}}
@keyframes l03g-h3{0%,59.99%{opacity:0}60%{opacity:1}80%{opacity:1}80.01%,100%{opacity:0}}
.l03g-g3 rect,.l03g-g3 line,.l03g-g3 path:not(.l03g-gl){animation-name:l03g-g3}.l03g-h3{animation-name:l03g-h3}
@keyframes l03g-g4{0%,79.99%{opacity:.5}80%{opacity:1}100%{opacity:1}100.01%,100%{opacity:.5}}
@keyframes l03g-h4{0%,79.99%{opacity:0}80%{opacity:1}100%{opacity:1}100.01%,100%{opacity:0}}
.l03g-g4 rect,.l03g-g4 line,.l03g-g4 path:not(.l03g-gl){animation-name:l03g-g4}.l03g-h4{animation-name:l03g-h4}
</style>
<defs>
<marker id="l03g-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="l03g-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="l03g-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<rect class="l03g-box" x="14" y="16" width="440" height="324" rx="9"/><text class="l03g-ttlL" x="28" y="37">Request to the RS</text><text class="l03g-subL" x="28" y="54">Authorization: DPoP &lt;token></text>
<rect class="l03g-nest" x="26" y="62" width="416" height="266" rx="9"/><text class="l03g-ttlL" x="40" y="83">DPoP header</text><text class="l03g-subL" x="40" y="100">a JWT with typ dpop+jwt</text>
<rect class="l03g-nest" x="38" y="108" width="392" height="46" rx="9"/><text class="l03g-ttlL" x="52" y="129">jwk</text><text class="l03g-subL" x="52" y="146">the public key</text>
<rect class="l03g-nest" x="38" y="162" width="392" height="46" rx="9"/><text class="l03g-ttlL" x="52" y="183">jti, htm, htu, iat</text><text class="l03g-subL" x="52" y="200">claims in the proof</text>
<rect class="l03g-nest" x="38" y="216" width="392" height="46" rx="9"/><text class="l03g-ttlL" x="52" y="237">ath</text><text class="l03g-subL" x="52" y="254">hash of the access token, at the RS</text>
<rect class="l03g-nest" x="38" y="270" width="392" height="46" rx="9"/><text class="l03g-ttlL" x="52" y="291">nonce</text><text class="l03g-subL" x="52" y="308">where the server supplied one</text>
<g class="l03g-g l03g-g0">
<path class="l03g-conn" d="M454,33 L462,33 L462,34 L470,34" marker-end="url(#l03g-m-front)"/>
<rect class="l03g-note" x="484" y="10" width="262" height="48" rx="8"/>
<text class="l03g-nt" x="615" y="31">token_type DPoP in the token response;</text>
<text class="l03g-nt" x="615" y="48">a JWT token is bound by cnf jkt</text>
<circle class="l03g-badge l03g-b-front" cx="484" cy="34" r="12"/><text class="l03g-bt" x="484" y="38.5">1</text>
</g>
<g class="l03g-g l03g-g1">
<path class="l03g-conn" d="M442,79 L466,79 L466,92 L470,92" marker-end="url(#l03g-m-front)"/>
<rect class="l03g-note-good" x="484" y="68" width="262" height="48" rx="8"/>
<text class="l03g-nt" x="615" y="89">Accept a proof only for a limited time</text>
<text class="l03g-nt" x="615" y="106">after its creation (RFC 9449, 11.1)</text>
<circle class="l03g-badge l03g-b-good" cx="484" cy="92" r="12"/><text class="l03g-bt" x="484" y="96.5">2</text>
</g>
<g class="l03g-g l03g-g2">
<path class="l03g-conn" d="M430,125 L470,125 L470,150 L470,150" marker-end="url(#l03g-m-front)"/>
<rect class="l03g-note-good" x="484" y="126" width="262" height="48" rx="8"/>
<text class="l03g-nt" x="615" y="147">jkt in the token's cnf is the</text>
<text class="l03g-nt" x="615" y="164">key's JWK thumbprint</text>
<circle class="l03g-badge l03g-b-good" cx="484" cy="150" r="12"/><text class="l03g-bt" x="484" y="154.5">3</text>
</g>
<g class="l03g-g l03g-g3">
<path class="l03g-conn" d="M430,179 L474,179 L474,216 L470,216" marker-end="url(#l03g-m-front)"/>
<rect class="l03g-note-good" x="484" y="184" width="262" height="65" rx="8"/>
<text class="l03g-nt" x="615" y="205">Can store jti for that window to make</text>
<text class="l03g-nt" x="615" y="222">proofs single-use; may not be feasible</text>
<text class="l03g-nt" x="615" y="239">without shared state</text>
<circle class="l03g-badge l03g-b-good" cx="484" cy="216" r="12"/><text class="l03g-bt" x="484" y="221.0">4</text>
</g>
<g class="l03g-g l03g-g4">
<path class="l03g-conn" d="M430,287 L462,287 L462,287 L470,287" marker-end="url(#l03g-m-front)"/>
<rect class="l03g-note-good" x="484" y="263" width="262" height="48" rx="8"/>
<text class="l03g-nt" x="615" y="284">The server may demand one with</text>
<text class="l03g-nt" x="615" y="301">use_dpop_nonce</text>
<circle class="l03g-badge l03g-b-good" cx="484" cy="287" r="12"/><text class="l03g-bt" x="484" y="291.5">5</text>
</g>
<g class="l03g-h l03g-h0">
<rect class="l03g-hl" x="14" y="16" width="440" height="324" rx="9"/>
</g>
<g class="l03g-h l03g-h1">
<rect class="l03g-hl" x="26" y="62" width="416" height="266" rx="9"/>
</g>
<g class="l03g-h l03g-h2">
<rect class="l03g-hl" x="38" y="108" width="392" height="46" rx="9"/>
</g>
<g class="l03g-h l03g-h3">
<rect class="l03g-hl" x="38" y="162" width="392" height="46" rx="9"/>
</g>
<g class="l03g-h l03g-h4">
<rect class="l03g-hl" x="38" y="270" width="392" height="46" rx="9"/>
</g>
<rect class="l03g-note" x="40" y="366" width="22" height="16" rx="4"/>
<text class="l03g-dim" x="70" y="378" style="text-anchor:start">context</text>
<rect class="l03g-note-good" x="148" y="366" width="22" height="16" rx="4"/>
<text class="l03g-dim" x="178" y="378" style="text-anchor:start">what the server does</text>
</svg>
</div>
</div>
<!-- /diagram:oauth-dpop-proof -->

The numbered callouts say what the server does, or may do, with a part of a DPoP request, and how the token is bound to the key.

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
