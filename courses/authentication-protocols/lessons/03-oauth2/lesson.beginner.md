# OAuth 2.0

After this lesson you can explain, in plain words, what happens when an app asks to "connect to your account". You can name the four parties involved, say which parts of the exchange go through the browser, and recognise the mistakes that turn up as help-desk tickets. Facts checked 2026-10-06.

Throughout, you will follow one example. Priya is an employee. She uses a scheduling app called Plannr, and Plannr wants to read the work calendar that Priya keeps at a service we will call Example Cloud.

Standards cited here: RFC 6749 (the OAuth 2.0 framework, 2012), RFC 6750 (bearer tokens), RFC 7636 (PKCE) and RFC 9700 (the January 2025 security best practice).

## The problem OAuth solves

The old way to let Plannr read Priya's calendar was for Priya to hand Plannr her Example Cloud password. RFC 6749 lists what goes wrong: Plannr has to store the password, Plannr gets far broader access than it needs, Priya cannot cut off Plannr without changing her password (which cuts off every other app too), and if Plannr is breached the password is breached.

OAuth 2.0 replaces the password with an **access token**: a string that stands for a specific scope, lifetime and other access attributes (RFC 6749's wording). Plannr receives a token, not a password, and the token can be limited and cancelled on its own.

Think of a valet key: it starts the car and nothing else. The analogy is ours, not the RFC's.

> OAuth is about **authorization**: permission for an app to do something. It is not a way to prove who Priya is. Logging a person in is a different job, done by OpenID Connect, the next lesson.

## The four roles

OAuth names four roles (RFC 6749, section 1.1). In our example:

- **Resource owner**: Priya, the person who can grant access to her own calendar.
- **Client**: Plannr, the application asking for access. "Client" says nothing about where the app runs.
- **Authorization server**: Example Cloud's sign-in and consent service. It signs Priya in, asks for her approval and issues the tokens. At your company, a service such as Okta or Microsoft Entra ID can play this role.
- **Resource server**: the calendar API that holds the data and accepts access tokens.

RFC 6749 also sorts clients into two types. A **confidential** client can keep a secret, for example an app running on a locked-down server. A **public** client cannot, for example an app installed on the user's device or code running in a browser. The RFC says to assume that any secret shipped inside a native app can be extracted. The `client_id` is an identifier, not a secret.

## The authorization code flow with PKCE

A few terms first. The **authorization code** is a short-lived, single-use receipt. The **redirect URI** is the address, registered in advance, where the authorization server sends the browser back. **State** is a random value the client invents so it can recognise its own request when the browser returns. **PKCE** (RFC 7636, pronounced "pixy") is a secret the client invents for each sign-in: it sends only a fingerprint of the secret at the start (the `code_challenge`, made with SHA-256, method `S256`) and reveals the secret itself (the `code_verifier`) at the end.

<!-- diagram:oauth-code-pkce -->
<div style="position:relative;margin:20px 0">
<input type="checkbox" id="oa-pause" class="oa-cb" /><label for="oa-pause" class="oa-btn"><span class="oa-off">Pause animation</span><span class="oa-on">Play animation</span></label>
<div class="oa-box" style="overflow-x:auto">
<svg class="oa-flow" viewBox="0 0 760 816" role="img" aria-labelledby="oa-t oa-d" style="width:100%;min-width:640px;max-width:800px;height:auto;display:block;margin:0 auto">
<title id="oa-t">How Plannr gets read access to Priya's calendar</title>
<desc id="oa-d">Three parties: Plannr, the client; Example Cloud's sign-in, the authorization server; and the calendar API, the resource server. Step 1: Plannr sends Priya's browser to the authorization server, carrying its client_id, redirect URI, scope, state and code_challenge. Step 2: Priya signs in and approves, and the server remembers the fingerprint. Step 3: the browser goes back to Plannr's redirect URI with a code and the same state. Step 4: Plannr checks the state is the one it stored; RFC 9700 lets a client skip this check only if it knows the server supports PKCE. Step 5: Plannr contacts the server directly, sending the code, the code_verifier, its client_id and the same redirect URI; if the verifier matches the fingerprint, it receives an access token. Step 6: Plannr calls the calendar API, sending the access token. Step 7: the calendar API checks the token: genuine, meant for it, unexpired, and its scope covers the request. The diagram highlights each step in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
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
@keyframes oa-g0{0%{opacity:1}14.286%{opacity:1}14.296%,100%{opacity:.45}}
@keyframes oa-p0{0%,-0.01%{opacity:0;transform:translateX(0)}0%{opacity:1;transform:translateX(0)}14.286%{opacity:1;transform:translateX(236px)}14.296%,100%{opacity:0;transform:translateX(236px)}}
.oa-g0{animation-name:oa-g0}.oa-p0{animation-name:oa-p0}
@keyframes oa-g1{0%,14.276%{opacity:.45}14.286%{opacity:1}28.571%{opacity:1}28.581%,100%{opacity:.45}}
.oa-g1{animation-name:oa-g1}
@keyframes oa-g2{0%,28.561%{opacity:.45}28.571%{opacity:1}42.857%{opacity:1}42.867%,100%{opacity:.45}}
@keyframes oa-p2{0%,28.561%{opacity:0;transform:translateX(0)}28.571%{opacity:1;transform:translateX(0)}42.857%{opacity:1;transform:translateX(-236px)}42.867%,100%{opacity:0;transform:translateX(-236px)}}
.oa-g2{animation-name:oa-g2}.oa-p2{animation-name:oa-p2}
@keyframes oa-g3{0%,42.847%{opacity:.45}42.857%{opacity:1}57.143%{opacity:1}57.153%,100%{opacity:.45}}
.oa-g3{animation-name:oa-g3}
@keyframes oa-g4{0%,57.133%{opacity:.45}57.143%{opacity:1}71.429%{opacity:1}71.439%,100%{opacity:.45}}
@keyframes oa-p4{0%,57.133%{opacity:0;transform:translateX(0)}57.143%{opacity:1;transform:translateX(0)}71.429%{opacity:1;transform:translateX(-236px)}71.439%,100%{opacity:0;transform:translateX(-236px)}}
.oa-g4{animation-name:oa-g4}.oa-p4{animation-name:oa-p4}
@keyframes oa-g5{0%,71.419%{opacity:.45}71.429%{opacity:1}85.714%{opacity:1}85.724%,100%{opacity:.45}}
@keyframes oa-p5{0%,71.419%{opacity:0;transform:translateX(0)}71.429%{opacity:1;transform:translateX(0)}85.714%{opacity:1;transform:translateX(506px)}85.724%,100%{opacity:0;transform:translateX(506px)}}
.oa-g5{animation-name:oa-g5}.oa-p5{animation-name:oa-p5}
@keyframes oa-g6{0%,85.704%{opacity:.45}85.714%{opacity:1}100%{opacity:1}100.01%,100%{opacity:.45}}
.oa-g6{animation-name:oa-g6}
</style>
<defs>
<marker id="oa-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="oa-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="oa-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<line class="oa-life" x1="110" y1="72" x2="110" y2="764"/>
<line class="oa-life" x1="380" y1="72" x2="380" y2="764"/>
<line class="oa-life" x1="650" y1="72" x2="650" y2="764"/>
<rect class="oa-box" x="20" y="10" width="180" height="62" rx="10"/><text class="oa-ttl" x="110" y="36">Plannr</text><text class="oa-sub" x="110" y="56">the client</text>
<rect class="oa-hot" x="290" y="10" width="180" height="62" rx="10"/><text class="oa-ttl" x="380" y="36">Authorization server</text><text class="oa-sub" x="380" y="56">Example Cloud's sign-in</text>
<rect class="oa-box" x="560" y="10" width="180" height="62" rx="10"/><text class="oa-ttl" x="650" y="36">Resource server</text><text class="oa-sub" x="650" y="56">the calendar API</text>
<g class="oa-g oa-g0">
<text class="oa-main" x="245" y="108">send Priya's browser to sign in</text>
<text class="oa-dim" x="245" y="124">client_id, redirect URI, scope,</text>
<text class="oa-dim" x="245" y="140">state, code_challenge</text>
<line class="oa-front" x1="124" y1="154" x2="366" y2="154" marker-end="url(#oa-m-front)"/>
<circle class="oa-badge oa-b-front" cx="110" cy="154" r="12"/><text class="oa-bt" x="110" y="158.5">1</text>
</g>
<g class="oa-g oa-g1">
<rect class="oa-note" x="246" y="188" width="267" height="48" rx="8"/>
<text class="oa-nt" x="380" y="209">Priya signs in and approves;</text>
<text class="oa-nt" x="380" y="226">the server remembers the fingerprint</text>
<circle class="oa-badge oa-b-plain" cx="246" cy="212" r="12"/><text class="oa-bt" x="246" y="216.5">2</text>
</g>
<g class="oa-g oa-g2">
<text class="oa-main" x="245" y="270">back to Plannr's redirect URI</text>
<text class="oa-dim" x="245" y="286">with a code and the same state</text>
<line class="oa-front" x1="366" y1="300" x2="124" y2="300" marker-end="url(#oa-m-front)"/>
<circle class="oa-badge oa-b-front" cx="380" cy="300" r="12"/><text class="oa-bt" x="380" y="304.5">3</text>
</g>
<g class="oa-g oa-g3">
<rect class="oa-note-good" x="10" y="334" width="280" height="65" rx="8"/>
<text class="oa-nt" x="150" y="355">Plannr checks the state is the one</text>
<text class="oa-nt" x="150" y="372">it stored (RFC 9700 lets it skip this</text>
<text class="oa-nt" x="150" y="389">only if PKCE is known to be supported)</text>
<circle class="oa-badge oa-b-good" cx="10" cy="366" r="12"/><text class="oa-bt" x="10" y="371.0">4</text>
</g>
<g class="oa-g oa-g4">
<text class="oa-main" x="245" y="433">contact the server directly:</text>
<text class="oa-dim" x="245" y="449">code, code_verifier, client_id,</text>
<text class="oa-dim" x="245" y="465">the same redirect URI as step 1</text>
<line class="oa-back" x1="124" y1="479" x2="366" y2="479" marker-end="url(#oa-m-back)"/>
<circle class="oa-badge oa-b-back" cx="110" cy="479" r="12"/><text class="oa-bt" x="110" y="483.5">5</text>
<text class="oa-main" x="245" y="519">access token, if the verifier</text>
<text class="oa-dim" x="245" y="535">matches the fingerprint</text>
<line class="oa-back" x1="366" y1="549" x2="124" y2="549" marker-end="url(#oa-m-back)"/>
</g>
<g class="oa-g oa-g5">
<text class="oa-main" x="380" y="589">calendar request,</text>
<text class="oa-dim" x="380" y="605">sending the access token</text>
<line class="oa-back" x1="124" y1="619" x2="636" y2="619" marker-end="url(#oa-m-back)"/>
<circle class="oa-badge oa-b-back" cx="110" cy="619" r="12"/><text class="oa-bt" x="110" y="623.5">6</text>
</g>
<g class="oa-g oa-g6">
<rect class="oa-note-good" x="476" y="653" width="274" height="65" rx="8"/>
<text class="oa-nt" x="613" y="674">the API checks the token: genuine,</text>
<text class="oa-nt" x="613" y="691">meant for it, unexpired, scope covers</text>
<text class="oa-nt" x="613" y="708">what is being asked</text>
<circle class="oa-badge oa-b-good" cx="476" cy="686" r="12"/><text class="oa-bt" x="476" y="690.0">7</text>
</g>
<circle class="oa-pk oa-p0" cx="130" cy="154" r="5.5"/>
<circle class="oa-pk oa-p2" cx="360" cy="300" r="5.5"/>
<circle class="oa-pk oa-p4 oa-pkback" cx="360" cy="549" r="5.5"/>
<circle class="oa-pk oa-p5 oa-pkback" cx="130" cy="619" r="5.5"/>
<line class="oa-front" x1="40" y1="792" x2="70" y2="792"/>
<text class="oa-dim" x="78" y="796" style="text-anchor:start">through the user's browser</text>
<line class="oa-back" x1="278" y1="792" x2="308" y2="792"/>
<text class="oa-dim" x="316" y="796" style="text-anchor:start">direct request, not a redirect</text>
<rect class="oa-note-good" x="542" y="784" width="22" height="16" rx="4"/>
<text class="oa-dim" x="572" y="796" style="text-anchor:start">a check to perform</text>
</svg>
</div>
</div>
<!-- /diagram:oauth-code-pkce -->

Solid arrows pass through the user's browser; dashed arrows are direct requests, not browser redirects. The numbers match the list below, and the green notes are checks someone makes.

1. Plannr sends Priya's browser to the authorization server, carrying its `client_id`, redirect URI, the scope it wants, a `state` value and the `code_challenge`.
2. Priya signs in and sees a consent screen showing which scopes Plannr wants. She approves, and the authorization server remembers the fingerprint alongside the code it is about to issue.
3. The authorization server sends the browser back to Plannr's redirect URI with a `code` and the same `state`.
4. Plannr checks that the `state` is the one it stored for this browser. (RFC 9700 lets a client skip this check only if it knows the server supports PKCE, which also guards against forged requests.)
5. Plannr contacts the authorization server directly, not through the browser's address bar, sending the `code`, the `code_verifier`, its `client_id` and the same redirect URI it sent at step 1. If the verifier matches the fingerprint from step 1, it receives an access token.
6. Plannr calls the calendar API, sending the access token.
7. The calendar API checks the token before it serves the request: is it genuine, meant for this API, unexpired, and does its scope cover what is being asked?

Steps 1 and 3 pass through the browser, so anything in them can be seen by software on Priya's device, by browser history, and by logs. That is why the code is only a receipt: it expires shortly (RFC 6749 recommends a maximum of 10 minutes) and works once. Those limits shrink the window for a thief but do not close it. Steps 5 and 6 are direct requests from the client, not redirects through the browser's address bar, so the token is never placed in a URL.

PKCE closes the remaining gap. A thief who steals the code at step 3 cannot use it at step 5, because the thief never saw the `code_verifier`. RFC 9700 says public clients must use PKCE, recommends it for confidential clients too, and notes that the advice applies to web applications as well as native apps.

<!-- diagram:oauth-stolen-code -->
<div style="position:relative;margin:20px 0">
<input type="checkbox" id="l03h-pause" class="l03h-cb" /><label for="l03h-pause" class="l03h-btn"><span class="l03h-off">Pause animation</span><span class="l03h-on">Play animation</span></label>
<div class="l03h-box" style="overflow-x:auto">
<svg class="l03h-flow" viewBox="0 0 760 654" role="img" aria-labelledby="l03h-t l03h-d" style="width:100%;min-width:640px;max-width:800px;height:auto;display:block;margin:0 auto">
<title id="l03h-t">Why a stolen code is no use without the code_verifier</title>
<desc id="l03h-d">Three parties: Plannr, the authorization server and a thief. At step 1 Plannr sends the fingerprint, the code_challenge, and the server remembers it. At step 3 the server sends the code back through the browser, and the thief steals it. The thief tries step 5 without the code_verifier, because it never saw the code_verifier, so cannot use the code. At step 5 Plannr sends the code and the code_verifier, the verifier matches the fingerprint, and Plannr gets an access token. The diagram highlights each step in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
<style>
.l03h-box{fill:var(--panel);stroke:var(--border-strong);stroke-width:1.5}
.l03h-hot{fill:var(--panel);stroke:var(--accent);stroke-width:2.5}
.l03h-ttl{fill:var(--text);font:600 15px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l03h-sub{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l03h-life{stroke:var(--border-strong);stroke-width:1.5;stroke-dasharray:4 5}
.l03h-front{stroke:var(--accent);stroke-width:2;fill:none}
.l03h-back{stroke:var(--muted);stroke-width:2;stroke-dasharray:7 5;fill:none}
.l03h-bad{stroke:var(--bad);stroke-width:2;fill:none}
.l03h-main{fill:var(--text);font:600 13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l03h-badt{fill:var(--bad-text)}
.l03h-dim{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l03h-badge{fill:var(--accent)}
.l03h-b-back{fill:var(--muted)}
.l03h-b-bad{fill:var(--bad)}
.l03h-b-good{fill:var(--good)}
.l03h-bt{fill:var(--on-accent);font:700 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l03h-note{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l03h-note-good{fill:var(--good-bg);stroke:var(--good);stroke-width:1.5}
.l03h-note-bad{fill:var(--bad-bg);stroke:var(--bad);stroke-width:1.5}
.l03h-nt{fill:var(--body);font:12.5px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l03h-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:18s;animation-timing-function:linear;animation-iteration-count:infinite}
.l03h-pk.l03h-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.l03h-pk.l03h-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.l03h-g{opacity:.45;animation-duration:18s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.l03h-flow:hover .l03h-g,svg.l03h-flow:hover .l03h-pk{animation-play-state:paused}
.l03h-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.l03h-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.l03h-btn:hover{background:var(--hover)}
.l03h-cb:focus-visible + .l03h-btn{outline:2px solid var(--accent);outline-offset:2px}
.l03h-cb:checked + .l03h-btn .l03h-off,.l03h-cb:not(:checked) + .l03h-btn .l03h-on{display:none}
.l03h-cb:checked ~ .l03h-box .l03h-g,.l03h-cb:checked ~ .l03h-box .l03h-pk{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.l03h-g{animation:none;opacity:1}.l03h-pk{animation:none;display:none}.l03h-btn{display:none}}
@keyframes l03h-g0{0%{opacity:1}16.667%{opacity:1}16.677%,100%{opacity:.45}}
@keyframes l03h-p0{0%,-0.01%{opacity:0;transform:translateX(0)}0%{opacity:1;transform:translateX(0)}16.667%{opacity:1;transform:translateX(236px)}16.677%,100%{opacity:0;transform:translateX(236px)}}
.l03h-g0{animation-name:l03h-g0}.l03h-p0{animation-name:l03h-p0}
@keyframes l03h-g1{0%,16.657%{opacity:.45}16.667%{opacity:1}33.333%{opacity:1}33.343%,100%{opacity:.45}}
@keyframes l03h-p1{0%,16.657%{opacity:0;transform:translateX(0)}16.667%{opacity:1;transform:translateX(0)}33.333%{opacity:1;transform:translateX(-236px)}33.343%,100%{opacity:0;transform:translateX(-236px)}}
.l03h-g1{animation-name:l03h-g1}.l03h-p1{animation-name:l03h-p1}
@keyframes l03h-g2{0%,33.323%{opacity:.45}33.333%{opacity:1}50%{opacity:1}50.01%,100%{opacity:.45}}
@keyframes l03h-p2{0%,33.323%{opacity:0;transform:translateX(0)}33.333%{opacity:1;transform:translateX(0)}50%{opacity:1;transform:translateX(-236px)}50.01%,100%{opacity:0;transform:translateX(-236px)}}
.l03h-g2{animation-name:l03h-g2}.l03h-p2{animation-name:l03h-p2}
@keyframes l03h-g3{0%,49.99%{opacity:.45}50%{opacity:1}66.667%{opacity:1}66.677%,100%{opacity:.45}}
.l03h-g3{animation-name:l03h-g3}
@keyframes l03h-g4{0%,66.657%{opacity:.45}66.667%{opacity:1}83.333%{opacity:1}83.343%,100%{opacity:.45}}
@keyframes l03h-p4{0%,66.657%{opacity:0;transform:translateX(0)}66.667%{opacity:1;transform:translateX(0)}83.333%{opacity:1;transform:translateX(236px)}83.343%,100%{opacity:0;transform:translateX(236px)}}
.l03h-g4{animation-name:l03h-g4}.l03h-p4{animation-name:l03h-p4}
@keyframes l03h-g5{0%,83.323%{opacity:.45}83.333%{opacity:1}100%{opacity:1}100.01%,100%{opacity:.45}}
.l03h-g5{animation-name:l03h-g5}
</style>
<defs>
<marker id="l03h-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="l03h-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="l03h-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<line class="l03h-life" x1="110" y1="72" x2="110" y2="580"/>
<line class="l03h-life" x1="380" y1="72" x2="380" y2="580"/>
<line class="l03h-life" x1="650" y1="72" x2="650" y2="580"/>
<rect class="l03h-box" x="20" y="10" width="180" height="62" rx="10"/><text class="l03h-ttl" x="110" y="36">Plannr</text><text class="l03h-sub" x="110" y="56">keeps the code_verifier</text>
<rect class="l03h-hot" x="290" y="10" width="180" height="62" rx="10"/><text class="l03h-ttl" x="380" y="36">Authorization server</text><text class="l03h-sub" x="380" y="56">remembers the fingerprint</text>
<rect class="l03h-box" x="560" y="10" width="180" height="62" rx="10"/><text class="l03h-ttl" x="650" y="36">Thief</text><text class="l03h-sub" x="650" y="56">has the stolen code</text>
<g class="l03h-g l03h-g0">
<text class="l03h-main" x="245" y="108">step 1: the fingerprint</text>
<text class="l03h-dim" x="245" y="124">(code_challenge)</text>
<line class="l03h-front" x1="124" y1="138" x2="366" y2="138" marker-end="url(#l03h-m-front)"/>
<circle class="l03h-badge l03h-b-front" cx="110" cy="138" r="12"/><text class="l03h-bt" x="110" y="142.5">1</text>
</g>
<g class="l03h-g l03h-g1">
<text class="l03h-main" x="245" y="178">step 3: the code</text>
<line class="l03h-front" x1="366" y1="192" x2="124" y2="192" marker-end="url(#l03h-m-front)"/>
<circle class="l03h-badge l03h-b-front" cx="380" cy="192" r="12"/><text class="l03h-bt" x="380" y="196.5">3</text>
<rect class="l03h-note-bad" x="536" y="210" width="214" height="48" rx="8"/>
<text class="l03h-nt" x="643" y="231">steals the code at step 3,</text>
<text class="l03h-nt" x="643" y="248">never sees the code_verifier</text>
<circle class="l03h-badge l03h-b-bad" cx="536" cy="234" r="12"/><text class="l03h-bt" x="536" y="238.5">!</text>
</g>
<g class="l03h-g l03h-g2">
<text class="l03h-main l03h-badt" x="515" y="292">step 5 without the code_verifier</text>
<line class="l03h-bad" x1="636" y1="306" x2="394" y2="306" marker-end="url(#l03h-m-bad)"/>
<circle class="l03h-badge l03h-b-bad" cx="650" cy="306" r="12"/><text class="l03h-bt" x="650" y="310.5">5</text>
</g>
<g class="l03h-g l03h-g3">
<rect class="l03h-note-bad" x="266" y="340" width="228" height="48" rx="8"/>
<text class="l03h-nt" x="380" y="361">the thief cannot use the code:</text>
<text class="l03h-nt" x="380" y="378">it never saw the code_verifier</text>
<circle class="l03h-badge l03h-b-bad" cx="266" cy="364" r="12"/><text class="l03h-bt" x="266" y="368.5">!</text>
</g>
<g class="l03h-g l03h-g4">
<text class="l03h-main" x="245" y="422">step 5 with the code</text>
<text class="l03h-dim" x="245" y="438">and the code_verifier</text>
<line class="l03h-back" x1="124" y1="452" x2="366" y2="452" marker-end="url(#l03h-m-back)"/>
<circle class="l03h-badge l03h-b-back" cx="110" cy="452" r="12"/><text class="l03h-bt" x="110" y="456.5">5</text>
</g>
<g class="l03h-g l03h-g5">
<rect class="l03h-note-good" x="243" y="486" width="274" height="48" rx="8"/>
<text class="l03h-nt" x="380" y="507">the verifier matches the fingerprint:</text>
<text class="l03h-nt" x="380" y="524">Plannr receives an access token</text>
</g>
<circle class="l03h-pk l03h-p0" cx="130" cy="138" r="5.5"/>
<circle class="l03h-pk l03h-p1" cx="360" cy="192" r="5.5"/>
<circle class="l03h-pk l03h-p2 l03h-pkbad" cx="630" cy="306" r="5.5"/>
<circle class="l03h-pk l03h-p4 l03h-pkback" cx="130" cy="452" r="5.5"/>
<line class="l03h-front" x1="40" y1="608" x2="70" y2="608"/>
<text class="l03h-dim" x="78" y="612" style="text-anchor:start">through the user's browser</text>
<line class="l03h-back" x1="278" y1="608" x2="308" y2="608"/>
<text class="l03h-dim" x="316" y="612" style="text-anchor:start">direct request, not a redirect</text>
<line class="l03h-bad" x1="542" y1="608" x2="572" y2="608"/>
<text class="l03h-dim" x="580" y="612" style="text-anchor:start">the thief's attempt</text>
<rect class="l03h-note-good" x="40" y="622" width="22" height="16" rx="4"/>
<text class="l03h-dim" x="70" y="634" style="text-anchor:start">what works</text>
</svg>
</div>
</div>
<!-- /diagram:oauth-stolen-code -->

Read it from the top down. Plannr sends the fingerprint at step 1, the thief grabs the code at step 3, and only Plannr holds the code_verifier that step 5 needs. The badges reuse the step numbers from the list above; the red notes mark what the thief does and why it fails.

## Tokens, scopes and consent

Plannr sends the access token in an `Authorization: Bearer` header. "Bearer" means whoever holds the token can use it, like cash, so protect it. RFC 6750 says tokens should be short-lived (one hour or less) and should not be passed in page URLs, because URLs end up in browser history and server logs. Plannr should treat the token as an opaque string and not try to read it.

A **refresh token** is a longer-lived credential that lets Plannr obtain new access tokens without bothering Priya again. Guard it as you would a password. RFC 7009 defines a revocation endpoint where a client can ask to cancel a token.

A **scope** is a word, defined by the authorization server, naming one kind of access, such as `calendar.read`. A request lists scopes separated by spaces, and the consent screen shows them to Priya. The server may grant less than requested. Least privilege applies: an app asking for more scopes than it needs gives an attacker more to steal.

## Other ways to get a token

- **Client credentials**: no person is involved, and the app acts for itself, as a nightly script does. RFC 6749 allows it only for confidential clients.
- **Device authorization** (RFC 8628): for a TV or command-line tool with no browser. The device shows a short `user_code` and a web address; the person opens that address on a phone, types the code and signs in, while the device waits. Attackers can abuse it by emailing people a code to type, so users should enter a code only for a device they are holding.
- **Refresh token**: trading a refresh token for a new access token.

RFC 9700 steers you away from two old grants. The **implicit** grant delivers the token in the browser's address, so clients should not use it. The **resource owner password** grant has the app collect the user's password, which RFC 9700 says must not be used; it is also not designed to work with MFA. The OAuth 2.1 draft (draft 16, September 2026, still work in progress, not a standard) drops both.

## What goes wrong

- **"Redirect URI mismatch" errors.** The authorization server compares the redirect URI to the registered one exactly, character by character; RFC 9700 requires exact string matching. A trailing slash or different path fails. Do not "fix" this by registering a wildcard.
- **A secret inside a mobile or browser app.** Public clients cannot keep secrets, so the secret protects nothing. Use PKCE.
- **Treating OAuth as login.** An access token says an app may call an API. It does not prove who just signed in.
- **Tokens in URLs and logs**, **long-lived refresh tokens** and **over-broad scopes** all raise the damage when something leaks.

## Your task

The next time an app offers "Connect your account", stop at the consent screen. Write down the client, the authorization server, the resource owner and every scope listed. Then ask whether the app needs all of them. Next lesson: OpenID Connect, which adds login on top of OAuth.
