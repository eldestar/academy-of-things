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

1. Plannr sends Priya's browser to the authorization server, carrying its `client_id`, redirect URI, the scope it wants, a `state` value and the `code_challenge`.
2. Priya signs in and sees a consent screen showing which scopes Plannr wants. She approves, and the authorization server remembers the fingerprint alongside the code it is about to issue.
3. The authorization server sends the browser back to Plannr's redirect URI with a `code` and the same `state`.
4. Plannr checks that the `state` is the one it stored for this browser. (RFC 9700 lets a client skip this check only if it knows the server supports PKCE, which also guards against forged requests.)
5. Plannr contacts the authorization server directly, not through the browser's address bar, sending the `code`, the `code_verifier`, its `client_id` and the same redirect URI it sent at step 1. If the verifier matches the fingerprint from step 1, it receives an access token.
6. Plannr calls the calendar API, sending the access token.
7. The calendar API checks the token before it serves the request: is it genuine, meant for this API, unexpired, and does its scope cover what is being asked?

Steps 1 and 3 pass through the browser, so anything in them can be seen by software on Priya's device, by browser history, and by logs. That is why the code is only a receipt: it expires shortly (RFC 6749 recommends a maximum of 10 minutes) and works once. Those limits shrink the window for a thief but do not close it. Steps 5 and 6 are direct requests from the client, not redirects through the browser's address bar, so the token is never placed in a URL.

PKCE closes the remaining gap. A thief who steals the code at step 3 cannot use it at step 5, because the thief never saw the `code_verifier`. RFC 9700 says public clients must use PKCE, recommends it for confidential clients too, and notes that the advice applies to web applications as well as native apps.

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
