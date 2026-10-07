# OpenID Connect and JWT validation

Priya opens ExampleCRM, a web app her company uses. She does not type a password into ExampleCRM. The app sends her to Okta, Okta signs her in, and ExampleCRM learns who she is. This lesson is about the protocol that carries that answer back, and the checks the app must make before it believes it. Facts checked 2026-10-06 against the OpenID Connect specifications, the JWT RFCs and vendor docs.

## What OpenID Connect adds

OAuth 2.0 (lesson 3) lets an app get permission to do things. On its own it does not tell the app who the user is. OpenID Connect (OIDC) is an identity layer built on top of OAuth 2.0: it adds a signed answer to "who just logged in?".

- The **relying party (RP)** is the app that relies on someone else to log users in. ExampleCRM is the RP.
- The **OpenID Provider (OP)** is the identity provider, such as Okta or Microsoft Entra ID.
- The app turns OIDC on by asking for the `openid` **scope**, a word that names what the app is asking for. Other scopes ask for groups of details: `profile` (name and similar) and `email`.

When the sign-in finishes, the app receives two things that are not interchangeable:

- The **ID token** is the OP's signed statement about the login: who the user is, who issued the statement, which app it is for, and when it expires. It is a **JWT** (JSON Web Token): three parts separated by dots, `header.payload.signature`. The details in the payload are called **claims**. The payload is only encoded, not secret, so anyone holding the token can read it. The **signature** is what makes it trustworthy.
- The **access token** is a string representing permission issued to the app, for example to call the OP's **UserInfo** endpoint, which returns more claims about the user. An app usually treats it as opaque, meaning it does not look inside.

> An app must not treat "I hold a valid access token" as proof that this person just logged in. OAuth alone cannot provide information about the authentication of the user. Only the ID token, validated, is the proof of login.

## How a sign-in works, step by step

<!-- diagram:oidc-code-flow -->
<div style="position:relative;margin:20px 0">
<input type="checkbox" id="oi-pause" class="oi-cb" /><label for="oi-pause" class="oi-btn"><span class="oi-off">Pause animation</span><span class="oi-on">Play animation</span></label>
<div class="oi-box" style="overflow-x:auto">
<svg class="oi-flow" viewBox="0 0 760 681" role="img" aria-labelledby="oi-t oi-d" style="width:100%;min-width:640px;max-width:800px;height:auto;display:block;margin:0 auto">
<title id="oi-t">How a sign-in with OpenID Connect works, in five steps</title>
<desc id="oi-d">Two parties: ExampleCRM, the relying party, and the OpenID Provider such as Okta. Step 1: ExampleCRM sends Priya's browser to the OP with scope openid, a nonce and a state. Priya signs in at the OP, including any MFA. Step 2: the OP sends the browser back to ExampleCRM with a code and the state. Step 3: ExampleCRM, server to server, trades the code at the token endpoint for the ID token and the access token. Step 4: ExampleCRM checks the ID token with the five checks, and only then logs Priya in. Step 5, optional: ExampleCRM calls UserInfo with the access token, and the sub in the answer must match the ID token's sub or the answer is discarded. The diagram highlights each step in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
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
<line class="oi-life" x1="110" y1="72" x2="110" y2="629"/>
<line class="oi-life" x1="650" y1="72" x2="650" y2="629"/>
<rect class="oi-hot" x="20" y="10" width="180" height="62" rx="10"/><text class="oi-ttl" x="110" y="36">ExampleCRM</text><text class="oi-sub" x="110" y="56">the relying party (RP)</text>
<rect class="oi-box" x="560" y="10" width="180" height="62" rx="10"/><text class="oi-ttl" x="650" y="36">Okta</text><text class="oi-sub" x="650" y="56">the OpenID Provider (OP)</text>
<g class="oi-g oi-g0">
<text class="oi-main" x="380" y="108">send Priya's browser to the OP</text>
<text class="oi-dim" x="380" y="124">scope=openid, a nonce, a state</text>
<line class="oi-front" x1="124" y1="138" x2="636" y2="138" marker-end="url(#oi-m-front)"/>
<circle class="oi-badge oi-b-front" cx="110" cy="138" r="12"/><text class="oi-bt" x="110" y="142.5">1</text>
</g>
<g class="oi-g oi-g1">
<rect class="oi-note" x="556" y="172" width="188" height="48" rx="8"/>
<text class="oi-nt" x="650" y="193">Priya signs in at the OP</text>
<text class="oi-nt" x="650" y="210">(including any MFA)</text>
</g>
<g class="oi-g oi-g2">
<text class="oi-main" x="380" y="254">send the browser back to ExampleCRM</text>
<text class="oi-dim" x="380" y="270">a code and the state</text>
<line class="oi-front" x1="636" y1="284" x2="124" y2="284" marker-end="url(#oi-m-front)"/>
<circle class="oi-badge oi-b-front" cx="650" cy="284" r="12"/><text class="oi-bt" x="650" y="288.5">2</text>
</g>
<g class="oi-g oi-g3">
<text class="oi-main" x="380" y="324">trade the code at the token endpoint</text>
<text class="oi-dim" x="380" y="340">server to server</text>
<line class="oi-back" x1="124" y1="354" x2="636" y2="354" marker-end="url(#oi-m-back)"/>
<circle class="oi-badge oi-b-back" cx="110" cy="354" r="12"/><text class="oi-bt" x="110" y="358.5">3</text>
<text class="oi-main" x="380" y="394">the ID token and the access token</text>
<line class="oi-back" x1="636" y1="408" x2="124" y2="408" marker-end="url(#oi-m-back)"/>
</g>
<g class="oi-g oi-g4">
<rect class="oi-note-good" x="10" y="442" width="267" height="48" rx="8"/>
<text class="oi-nt" x="144" y="463">check the ID token (the five checks)</text>
<text class="oi-nt" x="144" y="480">only then log Priya in</text>
<circle class="oi-badge oi-b-good" cx="10" cy="466" r="12"/><text class="oi-bt" x="10" y="470.5">4</text>
</g>
<g class="oi-g oi-g5">
<rect class="oi-note" x="10" y="518" width="333" height="65" rx="8"/>
<text class="oi-nt" x="176" y="539">optional: call UserInfo with the access token;</text>
<text class="oi-nt" x="176" y="556">its sub must match the ID token's sub,</text>
<text class="oi-nt" x="176" y="573">else the answer is discarded</text>
<circle class="oi-badge oi-b-plain" cx="10" cy="550" r="12"/><text class="oi-bt" x="10" y="555.0">5</text>
</g>
<circle class="oi-pk oi-p0" cx="130" cy="138" r="5.5"/>
<circle class="oi-pk oi-p2" cx="630" cy="284" r="5.5"/>
<circle class="oi-pk oi-p3 oi-pkback" cx="630" cy="408" r="5.5"/>
<line class="oi-front" x1="40" y1="657" x2="70" y2="657"/>
<text class="oi-dim" x="78" y="661" style="text-anchor:start">through Priya's browser</text>
<line class="oi-back" x1="259" y1="657" x2="289" y2="657"/>
<text class="oi-dim" x="297" y="661" style="text-anchor:start">server to server</text>
<rect class="oi-note-good" x="433" y="649" width="22" height="16" rx="4"/>
<text class="oi-dim" x="463" y="661" style="text-anchor:start">the check the app must do</text>
</svg>
</div>
</div>
<!-- /diagram:oidc-code-flow -->

Steps 1 and 2 pass through the browser, step 3 is server to server, and step 4 is the check your app must do itself. Step 5 is optional.

The numbers in the diagram match the numbered steps that follow.

1. ExampleCRM sends Priya's browser to the OP with `scope=openid`, plus a fresh random **nonce** (new for every sign-in; the code flow makes it optional, but ExampleCRM always sends one) and a `state` value. The app keeps both. `state` only lets the app match the returning browser to the request it sent; it says nothing about who the user is. Priya signs in at the OP, including any MFA. An app that cannot keep a secret, such as a mobile app or a page that runs only in the browser, is a **public client**. It also sends a `code_challenge`, a fingerprint of a one-time secret it invents for this sign-in; this is **PKCE**, covered in lesson 3. ExampleCRM runs on a server, so it is a **confidential client**.
2. The OP sends the browser back to ExampleCRM's registered address with a **code** and the `state`.
3. ExampleCRM, server to server, trades the code at the OP's token endpoint for the ID token and the access token. It proves who it is by authenticating as a confidential client; a public client instead sends the one-time secret itself (the `code_verifier`), which the OP checks against the `code_challenge`. PKCE is recommended for confidential clients too.
4. ExampleCRM **validates** the ID token (next section). Only then does it log Priya in.
5. Optionally it calls UserInfo with the access token. The `sub` in the answer must match the ID token's `sub`; if not, the answer is discarded.

## The five checks

<!-- diagram:oidc-id-token-anatomy -->
<div style="position:relative;margin:20px 0">
<input type="checkbox" id="l04a-pause" class="l04a-cb" /><label for="l04a-pause" class="l04a-btn"><span class="l04a-off">Pause animation</span><span class="l04a-on">Play animation</span></label>
<div class="l04a-box" style="overflow-x:auto">
<svg class="l04a-flow" viewBox="0 0 760 560" role="img" aria-labelledby="l04a-t l04a-d" style="width:100%;min-width:640px;max-width:800px;height:auto;display:block;margin:0 auto">
<title id="l04a-t">What is inside an ID token, and which check reads which part</title>
<desc id="l04a-d">An ID token is a JWT in three parts: a header that names the key that signed it, a payload of claims, and a signature. The payload holds iss, who issued the token; sub, who the user is; aud, which app it is for; exp, when it expires; and nonce, if the app sent one. Callouts say what the app checks in each part: iss is exactly the OP the app is configured to use, aud includes the app's own client ID, exp has not passed, nonce matches the value the app created, and the signature was made by a key the OP published. The payload is only encoded, so anyone holding the token can read it. The diagram highlights each part in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
<style>
.l04a-box{fill:var(--panel);stroke:var(--border-strong);stroke-width:1.5}
.l04a-hot{fill:var(--panel);stroke:var(--accent);stroke-width:2.5}
.l04a-ttl{fill:var(--text);font:600 15px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l04a-sub{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l04a-life{stroke:var(--border-strong);stroke-width:1.5;stroke-dasharray:4 5}
.l04a-front{stroke:var(--accent);stroke-width:2;fill:none}
.l04a-back{stroke:var(--muted);stroke-width:2;stroke-dasharray:7 5;fill:none}
.l04a-bad{stroke:var(--bad);stroke-width:2;fill:none}
.l04a-main{fill:var(--text);font:600 13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l04a-badt{fill:var(--bad-text)}
.l04a-dim{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l04a-badge{fill:var(--accent)}
.l04a-b-back{fill:var(--muted)}
.l04a-b-bad{fill:var(--bad)}
.l04a-b-good{fill:var(--good)}
.l04a-bt{fill:var(--on-accent);font:700 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l04a-note{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l04a-note-good{fill:var(--good-bg);stroke:var(--good);stroke-width:1.5}
.l04a-note-bad{fill:var(--bad-bg);stroke:var(--bad);stroke-width:1.5}
.l04a-nt{fill:var(--body);font:12.5px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l04a-nest{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l04a-row{fill:var(--raised);stroke:var(--border-strong);stroke-width:1}
.l04a-ttlL{fill:var(--text);font:600 14px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l04a-subL{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l04a-dimL{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l04a-dimR{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:end}
.l04a-conn{stroke:var(--accent);stroke-width:1.5;fill:none}
.l04a-edge{stroke:var(--border-strong);stroke-width:1.75;fill:none}
.l04a-hl{fill:none;stroke:var(--accent);stroke-width:3}
.l04a-hle{stroke:var(--accent);stroke-width:3;fill:none}
.l04a-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:20s;animation-timing-function:linear;animation-iteration-count:infinite}
.l04a-pk.l04a-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.l04a-pk.l04a-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.l04a-g{opacity:.45;animation-duration:20s;animation-timing-function:linear;animation-iteration-count:infinite}
.l04a-h{opacity:0;animation-duration:20s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.l04a-flow:hover .l04a-g,svg.l04a-flow:hover .l04a-pk,svg.l04a-flow:hover .l04a-h{animation-play-state:paused}
.l04a-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.l04a-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.l04a-btn:hover{background:var(--hover)}
.l04a-cb:focus-visible + .l04a-btn{outline:2px solid var(--accent);outline-offset:2px}
.l04a-cb:checked + .l04a-btn .l04a-off,.l04a-cb:not(:checked) + .l04a-btn .l04a-on{display:none}
.l04a-cb:checked ~ .l04a-box .l04a-g,.l04a-cb:checked ~ .l04a-box .l04a-pk,.l04a-cb:checked ~ .l04a-box .l04a-h{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.l04a-g{animation:none;opacity:1}.l04a-pk{animation:none;display:none}.l04a-h{animation:none;opacity:0}.l04a-btn{display:none}}
@keyframes l04a-g0{0%{opacity:1}20%{opacity:1}20.01%,100%{opacity:.45}}
@keyframes l04a-h0{0%{opacity:1}20%{opacity:1}20.01%,100%{opacity:0}}
.l04a-g0{animation-name:l04a-g0}.l04a-h0{animation-name:l04a-h0}
@keyframes l04a-g1{0%,19.99%{opacity:.45}20%{opacity:1}40%{opacity:1}40.01%,100%{opacity:.45}}
@keyframes l04a-h1{0%,19.99%{opacity:0}20%{opacity:1}40%{opacity:1}40.01%,100%{opacity:0}}
.l04a-g1{animation-name:l04a-g1}.l04a-h1{animation-name:l04a-h1}
@keyframes l04a-g2{0%,39.99%{opacity:.45}40%{opacity:1}60%{opacity:1}60.01%,100%{opacity:.45}}
@keyframes l04a-h2{0%,39.99%{opacity:0}40%{opacity:1}60%{opacity:1}60.01%,100%{opacity:0}}
.l04a-g2{animation-name:l04a-g2}.l04a-h2{animation-name:l04a-h2}
@keyframes l04a-g3{0%,59.99%{opacity:.45}60%{opacity:1}80%{opacity:1}80.01%,100%{opacity:.45}}
@keyframes l04a-h3{0%,59.99%{opacity:0}60%{opacity:1}80%{opacity:1}80.01%,100%{opacity:0}}
.l04a-g3{animation-name:l04a-g3}.l04a-h3{animation-name:l04a-h3}
@keyframes l04a-g4{0%,79.99%{opacity:.45}80%{opacity:1}100%{opacity:1}100.01%,100%{opacity:.45}}
@keyframes l04a-h4{0%,79.99%{opacity:0}80%{opacity:1}100%{opacity:1}100.01%,100%{opacity:0}}
.l04a-g4{animation-name:l04a-g4}.l04a-h4{animation-name:l04a-h4}
</style>
<defs>
<marker id="l04a-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="l04a-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="l04a-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<rect class="l04a-box" x="14" y="16" width="440" height="486" rx="9"/><text class="l04a-ttlL" x="28" y="37">ID token</text><text class="l04a-subL" x="28" y="54">a JWT: header.payload.signature</text>
<rect class="l04a-nest" x="26" y="62" width="416" height="46" rx="9"/><text class="l04a-ttlL" x="40" y="83">Header</text><text class="l04a-subL" x="40" y="100">names the key that signed it</text>
<rect class="l04a-nest" x="26" y="116" width="416" height="320" rx="9"/><text class="l04a-ttlL" x="40" y="137">Payload</text><text class="l04a-subL" x="40" y="154">the claims; encoded, not secret</text>
<rect class="l04a-nest" x="38" y="162" width="392" height="46" rx="9"/><text class="l04a-ttlL" x="52" y="183">iss</text><text class="l04a-subL" x="52" y="200">who issued the token</text>
<rect class="l04a-nest" x="38" y="216" width="392" height="46" rx="9"/><text class="l04a-ttlL" x="52" y="237">sub</text><text class="l04a-subL" x="52" y="254">who the user is</text>
<rect class="l04a-nest" x="38" y="270" width="392" height="46" rx="9"/><text class="l04a-ttlL" x="52" y="291">aud</text><text class="l04a-subL" x="52" y="308">which app it is for</text>
<rect class="l04a-nest" x="38" y="324" width="392" height="46" rx="9"/><text class="l04a-ttlL" x="52" y="345">exp</text><text class="l04a-subL" x="52" y="362">when it expires</text>
<rect class="l04a-nest" x="38" y="378" width="392" height="46" rx="9"/><text class="l04a-ttlL" x="52" y="399">nonce</text><text class="l04a-subL" x="52" y="416">only if the app sent one</text>
<rect class="l04a-nest" x="26" y="444" width="416" height="46" rx="9"/><text class="l04a-ttlL" x="40" y="465">Signature</text><text class="l04a-subL" x="40" y="482">what makes it trustworthy</text>
<g class="l04a-g l04a-g0">
<path class="l04a-conn" d="M430,179 L462,179 L462,179 L470,179" marker-end="url(#l04a-m-front)"/>
<rect class="l04a-note-good" x="484" y="155" width="262" height="48" rx="8"/>
<text class="l04a-nt" x="615" y="176">Exactly the OP the app is</text>
<text class="l04a-nt" x="615" y="193">configured to use</text>
<circle class="l04a-badge l04a-b-good" cx="484" cy="179" r="12"/><text class="l04a-bt" x="484" y="183.5">1</text>
</g>
<g class="l04a-g l04a-g1">
<path class="l04a-conn" d="M430,287 L466,287 L466,287 L470,287" marker-end="url(#l04a-m-front)"/>
<rect class="l04a-note-good" x="484" y="272" width="262" height="31" rx="8"/>
<text class="l04a-nt" x="615" y="292">Includes this app's own client ID</text>
<circle class="l04a-badge l04a-b-good" cx="484" cy="287" r="12"/><text class="l04a-bt" x="484" y="291.5">2</text>
</g>
<g class="l04a-g l04a-g2">
<path class="l04a-conn" d="M430,341 L470,341 L470,341 L470,341" marker-end="url(#l04a-m-front)"/>
<rect class="l04a-note-good" x="484" y="326" width="262" height="31" rx="8"/>
<text class="l04a-nt" x="615" y="346">The time has not passed</text>
<circle class="l04a-badge l04a-b-good" cx="484" cy="341" r="12"/><text class="l04a-bt" x="484" y="345.5">3</text>
</g>
<g class="l04a-g l04a-g3">
<path class="l04a-conn" d="M430,395 L474,395 L474,395 L470,395" marker-end="url(#l04a-m-front)"/>
<rect class="l04a-note-good" x="484" y="371" width="262" height="48" rx="8"/>
<text class="l04a-nt" x="615" y="392">Matches the value this app created</text>
<text class="l04a-nt" x="615" y="409">for this browser's sign-in</text>
<circle class="l04a-badge l04a-b-good" cx="484" cy="395" r="12"/><text class="l04a-bt" x="484" y="399.5">4</text>
</g>
<g class="l04a-g l04a-g4">
<path class="l04a-conn" d="M442,461 L462,461 L462,461 L470,461" marker-end="url(#l04a-m-front)"/>
<rect class="l04a-note-good" x="484" y="446" width="262" height="31" rx="8"/>
<text class="l04a-nt" x="615" y="466">Made by a key the OP published</text>
<circle class="l04a-badge l04a-b-good" cx="484" cy="461" r="12"/><text class="l04a-bt" x="484" y="465.5">5</text>
</g>
<g class="l04a-h l04a-h0">
<rect class="l04a-hl" x="38" y="162" width="392" height="46" rx="9"/>
</g>
<g class="l04a-h l04a-h1">
<rect class="l04a-hl" x="38" y="270" width="392" height="46" rx="9"/>
</g>
<g class="l04a-h l04a-h2">
<rect class="l04a-hl" x="38" y="324" width="392" height="46" rx="9"/>
</g>
<g class="l04a-h l04a-h3">
<rect class="l04a-hl" x="38" y="378" width="392" height="46" rx="9"/>
</g>
<g class="l04a-h l04a-h4">
<rect class="l04a-hl" x="26" y="444" width="416" height="46" rx="9"/>
</g>
<rect class="l04a-note-good" x="40" y="528" width="22" height="16" rx="4"/>
<text class="l04a-dim" x="70" y="540" style="text-anchor:start">what the app checks</text>
</svg>
</div>
</div>
<!-- /diagram:oidc-id-token-anatomy -->

This is the ID token opened up. Each numbered callout is one of the five checks below, placed on the part of the token it reads. The badges number this diagram from top to bottom, so they do not match the numbers in the list. `sub` has no callout: it is not a check, it is the field you use to identify the user, covered under "Who is this person?".

The ID token arrived, but a forged token looks identical. ExampleCRM checks, before trusting anything inside:

1. **Signature**: made by a key the OP published. The app decides which signing algorithm it accepts; it never trusts the token's own header to choose.
2. **`iss` (issuer)**: exactly the OP the app is configured to use, for example `https://login.example.com`.
3. **`aud` (audience)**: includes this app's own client ID. The same OP signs tokens for many apps; a token meant for another app must be rejected here.
4. **`exp` (expiry)**: the time has not passed. Servers' clocks drift, so apps may allow a small leeway, usually no more than a few minutes. This is a token lifetime, not a session lifetime.
5. **`nonce`**, if the app sent one (ExampleCRM always does): matches the random value this app created for this browser's sign-in. A captured, still-valid token replayed into another session fails because the nonce does not match.

## Keys: how the app knows the signature is real

The app does not have a secret shared with the OP. The OP publishes its **public keys** in a **JWKS** (JSON Web Key Set) at a web address called `jwks_uri`. The address is listed in the OP's discovery document, found at `/.well-known/openid-configuration` under the issuer's URL. Each key has a label, the `kid`, and the token's header says which `kid` signed it.

Providers change signing keys on a schedule; Okta documents that its schedule is currently four times a year and can change without notice. So an app must never hardcode a key. When it sees a `kid` it has not got, it fetches the JWKS again. An app with a stale or hardcoded key rejects every new token with "invalid signature", usually the morning after a rotation.

<!-- diagram:oidc-key-lookup -->
<div style="position:relative;margin:20px 0">
<input type="checkbox" id="l04b-pause" class="l04b-cb" /><label for="l04b-pause" class="l04b-btn"><span class="l04b-off">Pause animation</span><span class="l04b-on">Play animation</span></label>
<div class="l04b-box" style="overflow-x:auto">
<svg class="l04b-flow" viewBox="0 0 760 643" role="img" aria-labelledby="l04b-t l04b-d" style="width:100%;min-width:640px;max-width:800px;height:auto;display:block;margin:0 auto">
<title id="l04b-t">How the app finds the key that checks the signature</title>
<desc id="l04b-d">Two parties: ExampleCRM and the OP. Step 1: ExampleCRM fetches the OP's discovery document at /.well-known/openid-configuration, which lists the jwks_uri address. Step 2: ExampleCRM fetches the JWKS from jwks_uri and gets the OP's public keys, each with a kid. Step 3: the token's header says which kid signed it. Step 4: when ExampleCRM sees a kid it does not have, it fetches the JWKS again. A note says an app with a stale or hardcoded key rejects every new token with invalid signature, usually the morning after a rotation. The diagram highlights each step in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
<style>
.l04b-box{fill:var(--panel);stroke:var(--border-strong);stroke-width:1.5}
.l04b-hot{fill:var(--panel);stroke:var(--accent);stroke-width:2.5}
.l04b-ttl{fill:var(--text);font:600 15px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l04b-sub{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l04b-life{stroke:var(--border-strong);stroke-width:1.5;stroke-dasharray:4 5}
.l04b-front{stroke:var(--accent);stroke-width:2;fill:none}
.l04b-back{stroke:var(--muted);stroke-width:2;stroke-dasharray:7 5;fill:none}
.l04b-bad{stroke:var(--bad);stroke-width:2;fill:none}
.l04b-main{fill:var(--text);font:600 13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l04b-badt{fill:var(--bad-text)}
.l04b-dim{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l04b-badge{fill:var(--accent)}
.l04b-b-back{fill:var(--muted)}
.l04b-b-bad{fill:var(--bad)}
.l04b-b-good{fill:var(--good)}
.l04b-bt{fill:var(--on-accent);font:700 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l04b-note{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l04b-note-good{fill:var(--good-bg);stroke:var(--good);stroke-width:1.5}
.l04b-note-bad{fill:var(--bad-bg);stroke:var(--bad);stroke-width:1.5}
.l04b-nt{fill:var(--body);font:12.5px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l04b-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:20s;animation-timing-function:linear;animation-iteration-count:infinite}
.l04b-pk.l04b-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.l04b-pk.l04b-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.l04b-g{opacity:.45;animation-duration:20s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.l04b-flow:hover .l04b-g,svg.l04b-flow:hover .l04b-pk{animation-play-state:paused}
.l04b-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.l04b-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.l04b-btn:hover{background:var(--hover)}
.l04b-cb:focus-visible + .l04b-btn{outline:2px solid var(--accent);outline-offset:2px}
.l04b-cb:checked + .l04b-btn .l04b-off,.l04b-cb:not(:checked) + .l04b-btn .l04b-on{display:none}
.l04b-cb:checked ~ .l04b-box .l04b-g,.l04b-cb:checked ~ .l04b-box .l04b-pk{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.l04b-g{animation:none;opacity:1}.l04b-pk{animation:none;display:none}.l04b-btn{display:none}}
@keyframes l04b-g0{0%{opacity:1}20%{opacity:1}20.01%,100%{opacity:.45}}
@keyframes l04b-p0{0%,-0.01%{opacity:0;transform:translateX(0)}0%{opacity:1;transform:translateX(0)}20%{opacity:1;transform:translateX(-506px)}20.01%,100%{opacity:0;transform:translateX(-506px)}}
.l04b-g0{animation-name:l04b-g0}.l04b-p0{animation-name:l04b-p0}
@keyframes l04b-g1{0%,19.99%{opacity:.45}20%{opacity:1}40%{opacity:1}40.01%,100%{opacity:.45}}
@keyframes l04b-p1{0%,19.99%{opacity:0;transform:translateX(0)}20%{opacity:1;transform:translateX(0)}40%{opacity:1;transform:translateX(-506px)}40.01%,100%{opacity:0;transform:translateX(-506px)}}
.l04b-g1{animation-name:l04b-g1}.l04b-p1{animation-name:l04b-p1}
@keyframes l04b-g2{0%,39.99%{opacity:.45}40%{opacity:1}60%{opacity:1}60.01%,100%{opacity:.45}}
.l04b-g2{animation-name:l04b-g2}
@keyframes l04b-g3{0%,59.99%{opacity:.45}60%{opacity:1}80%{opacity:1}80.01%,100%{opacity:.45}}
@keyframes l04b-p3{0%,59.99%{opacity:0;transform:translateX(0)}60%{opacity:1;transform:translateX(0)}80%{opacity:1;transform:translateX(506px)}80.01%,100%{opacity:0;transform:translateX(506px)}}
.l04b-g3{animation-name:l04b-g3}.l04b-p3{animation-name:l04b-p3}
@keyframes l04b-g4{0%,79.99%{opacity:.45}80%{opacity:1}100%{opacity:1}100.01%,100%{opacity:.45}}
.l04b-g4{animation-name:l04b-g4}
</style>
<defs>
<marker id="l04b-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="l04b-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="l04b-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<line class="l04b-life" x1="110" y1="72" x2="110" y2="591"/>
<line class="l04b-life" x1="650" y1="72" x2="650" y2="591"/>
<rect class="l04b-hot" x="20" y="10" width="180" height="62" rx="10"/><text class="l04b-ttl" x="110" y="36">ExampleCRM</text><text class="l04b-sub" x="110" y="56">the app</text>
<rect class="l04b-box" x="560" y="10" width="180" height="62" rx="10"/><text class="l04b-ttl" x="650" y="36">Okta</text><text class="l04b-sub" x="650" y="56">the OP</text>
<g class="l04b-g l04b-g0">
<text class="l04b-main" x="380" y="108">fetch the discovery document</text>
<text class="l04b-dim" x="380" y="124">/.well-known/openid-configuration</text>
<line class="l04b-front" x1="124" y1="138" x2="636" y2="138" marker-end="url(#l04b-m-front)"/>
<circle class="l04b-badge l04b-b-front" cx="110" cy="138" r="12"/><text class="l04b-bt" x="110" y="142.5">1</text>
<text class="l04b-main" x="380" y="178">it lists the jwks_uri address</text>
<line class="l04b-front" x1="636" y1="192" x2="124" y2="192" marker-end="url(#l04b-m-front)"/>
</g>
<g class="l04b-g l04b-g1">
<text class="l04b-main" x="380" y="232">fetch the JWKS from jwks_uri</text>
<line class="l04b-front" x1="124" y1="246" x2="636" y2="246" marker-end="url(#l04b-m-front)"/>
<circle class="l04b-badge l04b-b-front" cx="110" cy="246" r="12"/><text class="l04b-bt" x="110" y="250.5">2</text>
<text class="l04b-main" x="380" y="286">the OP's public keys, each with a kid</text>
<line class="l04b-front" x1="636" y1="300" x2="124" y2="300" marker-end="url(#l04b-m-front)"/>
</g>
<g class="l04b-g l04b-g2">
<rect class="l04b-note" x="10" y="334" width="247" height="48" rx="8"/>
<text class="l04b-nt" x="134" y="355">the token's header says which kid</text>
<text class="l04b-nt" x="134" y="372">signed it</text>
<circle class="l04b-badge l04b-b-plain" cx="10" cy="358" r="12"/><text class="l04b-bt" x="10" y="362.5">3</text>
</g>
<g class="l04b-g l04b-g3">
<text class="l04b-main" x="380" y="416">a kid I have not got:</text>
<text class="l04b-dim" x="380" y="432">fetch the JWKS again</text>
<line class="l04b-front" x1="124" y1="446" x2="636" y2="446" marker-end="url(#l04b-m-front)"/>
<circle class="l04b-badge l04b-b-front" cx="110" cy="446" r="12"/><text class="l04b-bt" x="110" y="450.5">4</text>
</g>
<g class="l04b-g l04b-g4">
<rect class="l04b-note-bad" x="10" y="480" width="280" height="65" rx="8"/>
<text class="l04b-nt" x="150" y="501">a stale or hardcoded key rejects every</text>
<text class="l04b-nt" x="150" y="518">new token as invalid signature,</text>
<text class="l04b-nt" x="150" y="535">usually the morning after a rotation</text>
</g>
<circle class="l04b-pk l04b-p0" cx="630" cy="192" r="5.5"/>
<circle class="l04b-pk l04b-p1" cx="630" cy="300" r="5.5"/>
<circle class="l04b-pk l04b-p3" cx="130" cy="446" r="5.5"/>
<line class="l04b-front" x1="40" y1="619" x2="70" y2="619"/>
<text class="l04b-dim" x="78" y="623" style="text-anchor:start">a request and its answer</text>
<rect class="l04b-note-bad" x="265" y="611" width="22" height="16" rx="4"/>
<text class="l04b-dim" x="295" y="623" style="text-anchor:start">what goes wrong</text>
</svg>
</div>
</div>
<!-- /diagram:oidc-key-lookup -->

Read it from the top: the app finds the address, fetches the keys, and the token's header picks the key by its kid. The badges number this diagram's own four hops, not the steps of the sign-in.

## Who is this person?

Use `sub` (subject), the OP's identifier for the user. It is never reassigned to another person. Do not identify users by email: addresses change when names change, and an issuer may give an old address to someone new. `email_verified: true` only means the OP says it checked, and how it checked depends on the OP's arrangements. Neither `preferred_username` nor `name` is guaranteed unique.

## Logging out

Signing out of ExampleCRM, when its Sign out button only clears its own session cookie, ends ExampleCRM's own session. Priya's session at the OP is separate. If she clicks Sign in again, the OP may sign her straight back in with no password. To end the OP session, the app sends the browser to the OP's logout address; the OP may still ask her whether to log out there too. Telling other apps is a separate feature (front-channel or back-channel logout, covered in the next levels).

<!-- diagram:oidc-logout-sessions -->
<div style="position:relative;margin:20px 0">
<input type="checkbox" id="l04c-pause" class="l04c-cb" /><label for="l04c-pause" class="l04c-btn"><span class="l04c-off">Pause animation</span><span class="l04c-on">Play animation</span></label>
<div class="l04c-box" style="overflow-x:auto">
<svg class="l04c-flow" viewBox="0 0 760 220" role="img" aria-labelledby="l04c-t l04c-d" style="width:100%;min-width:640px;max-width:800px;height:auto;display:block;margin:0 auto">
<title id="l04c-t">Signing out of the app is not signing out of the OP</title>
<desc id="l04c-d">Three stages. First Priya is signed in at ExampleCRM and at the OP, two separate sessions. When ExampleCRM's Sign out button only clears its own session cookie, ExampleCRM's session ends but the OP session is still there, and if she signs in again the OP may sign her straight back in. When the app sends the browser to the OP's logout address, that is how the OP session is ended, though the OP may still ask her whether to log out there too. The diagram highlights each stage in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
<style>
.l04c-box{fill:var(--panel);stroke:var(--border-strong);stroke-width:1.5}
.l04c-hot{fill:var(--panel);stroke:var(--accent);stroke-width:2.5}
.l04c-ttl{fill:var(--text);font:600 15px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l04c-sub{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l04c-life{stroke:var(--border-strong);stroke-width:1.5;stroke-dasharray:4 5}
.l04c-front{stroke:var(--accent);stroke-width:2;fill:none}
.l04c-back{stroke:var(--muted);stroke-width:2;stroke-dasharray:7 5;fill:none}
.l04c-bad{stroke:var(--bad);stroke-width:2;fill:none}
.l04c-main{fill:var(--text);font:600 13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l04c-badt{fill:var(--bad-text)}
.l04c-dim{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l04c-badge{fill:var(--accent)}
.l04c-b-back{fill:var(--muted)}
.l04c-b-bad{fill:var(--bad)}
.l04c-b-good{fill:var(--good)}
.l04c-bt{fill:var(--on-accent);font:700 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l04c-note{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l04c-note-good{fill:var(--good-bg);stroke:var(--good);stroke-width:1.5}
.l04c-note-bad{fill:var(--bad-bg);stroke:var(--bad);stroke-width:1.5}
.l04c-nt{fill:var(--body);font:12.5px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l04c-nest{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l04c-row{fill:var(--raised);stroke:var(--border-strong);stroke-width:1}
.l04c-ttlL{fill:var(--text);font:600 14px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l04c-subL{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l04c-dimL{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l04c-dimR{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:end}
.l04c-conn{stroke:var(--accent);stroke-width:1.5;fill:none}
.l04c-edge{stroke:var(--border-strong);stroke-width:1.75;fill:none}
.l04c-hl{fill:none;stroke:var(--accent);stroke-width:3}
.l04c-hle{stroke:var(--accent);stroke-width:3;fill:none}
.l04c-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:14s;animation-timing-function:linear;animation-iteration-count:infinite}
.l04c-pk.l04c-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.l04c-pk.l04c-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.l04c-g{opacity:.45;animation-duration:14s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.l04c-flow:hover .l04c-g,svg.l04c-flow:hover .l04c-pk{animation-play-state:paused}
.l04c-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.l04c-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.l04c-btn:hover{background:var(--hover)}
.l04c-cb:focus-visible + .l04c-btn{outline:2px solid var(--accent);outline-offset:2px}
.l04c-cb:checked + .l04c-btn .l04c-off,.l04c-cb:not(:checked) + .l04c-btn .l04c-on{display:none}
.l04c-cb:checked ~ .l04c-box .l04c-g,.l04c-cb:checked ~ .l04c-box .l04c-pk{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.l04c-g{animation:none;opacity:1}.l04c-pk{animation:none;display:none}.l04c-btn{display:none}}
@keyframes l04c-g0{0%{opacity:1}33.333%{opacity:1}33.343%,100%{opacity:.45}}
@keyframes l04c-p0{0%,-0.01%{opacity:0;transform:translateX(0)}0%{opacity:1;transform:translateX(0)}33.333%{opacity:1;transform:translateX(88px)}33.343%,100%{opacity:0;transform:translateX(88px)}}
.l04c-g0{animation-name:l04c-g0}.l04c-p0{animation-name:l04c-p0}
@keyframes l04c-g1{0%,33.323%{opacity:.45}33.333%{opacity:1}66.667%{opacity:1}66.677%,100%{opacity:.45}}
@keyframes l04c-p1{0%,33.323%{opacity:0;transform:translateX(0)}33.333%{opacity:1;transform:translateX(0)}66.667%{opacity:1;transform:translateX(88px)}66.677%,100%{opacity:0;transform:translateX(88px)}}
.l04c-g1{animation-name:l04c-g1}.l04c-p1{animation-name:l04c-p1}
@keyframes l04c-g2{0%,66.657%{opacity:.45}66.667%{opacity:1}100%{opacity:1}100.01%,100%{opacity:.45}}
.l04c-g2{animation-name:l04c-g2}
</style>
<defs>
<marker id="l04c-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="l04c-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="l04c-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<g class="l04c-g l04c-g0">
<rect class="l04c-box" x="14" y="40" width="171" height="110" rx="10"/>
<text class="l04c-ttl" x="99" y="67">Signed in</text>
<text class="l04c-sub" x="99" y="87">two separate sessions</text>
<text class="l04c-nt" x="99" y="114">ExampleCRM: signed in</text>
<text class="l04c-nt" x="99" y="131">OP: signed in</text>
<text class="l04c-main" x="240" y="48">Sign out button:</text>
<text class="l04c-dim" x="240" y="64">clears cookie</text>
<line class="l04c-front" x1="193" y1="70" x2="287" y2="70" marker-end="url(#l04c-m-front)"/>
<text class="l04c-main" x="240" y="112">sign in again:</text>
<text class="l04c-dim" x="240" y="128">OP may sign her</text>
<text class="l04c-dim" x="240" y="144">straight in</text>
<line class="l04c-back" x1="287" y1="94" x2="193" y2="94" marker-end="url(#l04c-m-back)"/>
</g>
<g class="l04c-g l04c-g1">
<rect class="l04c-box" x="295" y="40" width="171" height="110" rx="10"/>
<text class="l04c-ttl" x="380" y="67">App signed out</text>
<text class="l04c-sub" x="380" y="87">OP session is separate</text>
<text class="l04c-nt" x="380" y="114">ExampleCRM: ended</text>
<text class="l04c-nt" x="380" y="131">OP: still signed in</text>
<text class="l04c-main" x="520" y="32">browser sent to</text>
<text class="l04c-dim" x="520" y="48">OP's logout</text>
<text class="l04c-dim" x="520" y="64">address</text>
<line class="l04c-front" x1="473" y1="70" x2="567" y2="70" marker-end="url(#l04c-m-front)"/>
</g>
<g class="l04c-g l04c-g2">
<rect class="l04c-note-good" x="575" y="40" width="171" height="110" rx="10"/>
<text class="l04c-ttl" x="661" y="67">Sent to OP logout</text>
<text class="l04c-sub" x="661" y="87">the OP may ask her</text>
<text class="l04c-nt" x="661" y="114">ExampleCRM: ended</text>
<text class="l04c-nt" x="661" y="131">OP: asked to end it</text>
</g>
<circle class="l04c-pk l04c-p0" cx="199" cy="70" r="5.5"/>
<circle class="l04c-pk l04c-p1" cx="479" cy="70" r="5.5"/>
<line class="l04c-front" x1="40" y1="196" x2="70" y2="196"/>
<text class="l04c-dim" x="78" y="200" style="text-anchor:start">step</text>
<line class="l04c-back" x1="137" y1="196" x2="167" y2="196"/>
<text class="l04c-dim" x="175" y="200" style="text-anchor:start">what can happen next</text>
<rect class="l04c-note-good" x="337" y="188" width="22" height="16" rx="4"/>
<text class="l04c-dim" x="367" y="200" style="text-anchor:start">OP asked to end it</text>
</svg>
</div>
</div>
<!-- /diagram:oidc-logout-sessions -->

The app's session and the OP's session are separate, so ending the app's session does not end the OP's. The dashed arrow shows what can happen when only the app's session is cleared.

## Your task

Below is an invented, already-decoded sample payload; assume the token has not expired (`exp` is the year 2100). ExampleCRM's client ID is `crm-client-77`, its issuer is `https://login.example.com`, and the nonce stored for this browser was `k29x`.

```json
{"iss": "https://login.example.com", "sub": "00u1a2b3", "aud": "wiki-client-12", "exp": 4102444800, "nonce": "k29x", "email": "priya@example.com"}
```

Name the check that fails, and say which field you would use to identify Priya after login. Then read the intermediate lesson to try this on a real signed token. Next: SCIM, which keeps accounts in step with the identity provider.
