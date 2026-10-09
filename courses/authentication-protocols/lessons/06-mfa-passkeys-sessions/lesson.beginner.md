# MFA, passkeys and sessions

Facts checked 2026-10-06 against NIST SP 800-63-4 (final, 31 July 2025; this lesson cites its 63B volume), the W3C Web Authentication (WebAuthn) Level 3 Recommendation of 25 August 2026, the FIDO Alliance passkeys page, a Google Workspace Updates post (May 2026), and Okta and Microsoft Entra documentation.

A password is one secret that anyone can learn, guess, or be tricked into typing. This lesson follows one employee, Sam, who opens the company expense app, and shows how extra proof works, how attackers get around it, and what happens after the sign-in succeeds.

## Three kinds of proof

An *authentication factor* is a kind of proof that you are who you claim to be. There are three categories:

- **Something you know** (knowledge): a password, a PIN, the answer to a security question.
- **Something you have** (possession): a phone, a hardware security key, a laptop that holds a secret key.
- **Something you are** (inherence): a fingerprint or a face.

*Multi-factor authentication (MFA)* means proving yourself with factors from at least two different categories. A password plus a PIN is two things you know, so it is not MFA. A password plus a code from your phone is something you know plus something you have, so it is MFA. NIST (the US standards body whose SP 800-63B guideline many organisations follow) does not treat a fingerprint as proof by itself: the fingerprint match unlocks a device you have, and the device is the "something you have".

## The second factors you will meet

**SMS code.** A text message with a code. It works on any phone, but the code travels over the phone network to a phone number. If an attacker gets that number moved to a SIM card they control (a SIM change or *number porting*), the codes go to the attacker. NIST calls this kind of delivery *restricted*: it says a service must offer alternatives and should look for warning signs such as a device swap, SIM change or number porting before sending a code.

**Authenticator app code (TOTP).** The app and the website share a secret. Both compute a six-digit code from that secret and the current time, and a new code appears every 30 seconds. No phone network is involved, but Sam still reads the code and types it.

**Push approval.** The phone shows "Approve sign-in?" and Sam taps Approve. This is easy to abuse. An attacker who already has the password can trigger prompt after prompt, hoping Sam taps Approve just to make them stop. That is an *MFA fatigue* attack. Swapping push for text-message codes does not remove it: anyone who knows the password can start a sign-in again and again, and each attempt sends another prompt or another text. What stops the blind tap is *number matching*: the sign-in screen shows a number, and Sam must pick the same number on the phone, so tapping Approve without looking no longer works. NIST says the plain approve-on-the-phone method is no longer considered acceptable (it names fatigue attacks), wants the person to transfer a secret between the screen and the phone (for example by typing the shown number into the app), and says services should limit how many pushes are sent. Okta calls the feature a number challenge, and Microsoft says number matching is enabled for all Microsoft Authenticator push notifications.

## Why fake sign-in pages beat most second factors

*Phishing* is tricking someone into using a fake site. A clever fake sits in the middle (an *adversary-in-the-middle*, or AitM, relay). Sam types the password and the six-digit code into the fake page, and the fake page instantly passes both to the real site, which accepts them. The attacker is signed in as Sam.

<!-- diagram:aitm-relay -->
<div class="l06a-wrap" style="position:relative">
<input type="checkbox" id="l06a-pause" class="l06a-cb" /><label for="l06a-pause" class="l06a-btn"><span class="l06a-off">Pause animation</span><span class="l06a-on">Play animation</span></label>
<div class="l06a-box" style="overflow-x:auto">
<svg class="l06a-flow" viewBox="0 0 760 540" role="img" aria-labelledby="l06a-t l06a-d" style="width:760px;max-width:100%;min-width:699px;height:auto;display:block;margin:0 auto">
<title id="l06a-t">A fake page passes Sam's code to the real site</title>
<desc id="l06a-d">Three parties: Sam, a fake sign-in page that sits in the middle, and the real site. Sam types the password and the six-digit code into the fake page. The fake page instantly passes both to the real site, which accepts them. The attacker is signed in as Sam. A final note says that typing a code does not tie it to the one site it was meant for. The diagram highlights each step in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
<style>
svg.l06a-flow{--ink:light-dark(#000000,#ffffff)}
.l06a-box{fill:var(--panel);stroke:var(--border-strong);stroke-width:1.5}
.l06a-hot{fill:var(--panel);stroke:var(--accent);stroke-width:2.5}
.l06a-ttl{fill:var(--ink);font:600 15px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l06a-sub{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l06a-life{stroke:var(--border-strong);stroke-width:1.5;stroke-dasharray:4 5}
.l06a-front{stroke:var(--accent);stroke-width:2;fill:none}
.l06a-back{stroke:var(--muted);stroke-width:2;stroke-dasharray:7 5;fill:none}
.l06a-bad{stroke:var(--bad);stroke-width:2;fill:none}
.l06a-main{fill:var(--ink);font:600 13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l06a-badt{fill:var(--ink)}
.l06a-dim{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l06a-badge{fill:var(--accent)}
.l06a-b-back{fill:var(--muted)}
.l06a-b-bad{fill:var(--bad)}
.l06a-b-good{fill:var(--good)}
.l06a-bt{fill:var(--on-accent);font:700 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l06a-note{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l06a-note-good{fill:var(--good-bg);stroke:var(--good);stroke-width:1.5}
.l06a-note-bad{fill:var(--bad-bg);stroke:var(--bad);stroke-width:1.5}
.l06a-nt{fill:var(--ink);font:500 12.5px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l06a-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:24s;animation-timing-function:linear;animation-iteration-count:infinite}
.l06a-pk.l06a-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.l06a-pk.l06a-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.l06a-wrap{margin:20px 0}
@media (min-width:801px){.l06a-wrap{margin-left:-44px;margin-right:-44px}}
.l06a-g rect,.l06a-g line,.l06a-g path:not(.l06a-gl){opacity:.5;animation-duration:24s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.l06a-flow:hover .l06a-g rect,svg.l06a-flow:hover .l06a-g line,svg.l06a-flow:hover .l06a-g path:not(.l06a-gl),svg.l06a-flow:hover .l06a-pk{animation-play-state:paused}
.l06a-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.l06a-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.l06a-btn:hover{background:var(--hover)}
.l06a-cb:focus-visible + .l06a-btn{outline:2px solid var(--accent);outline-offset:2px}
.l06a-cb:checked + .l06a-btn .l06a-off,.l06a-cb:not(:checked) + .l06a-btn .l06a-on{display:none}
.l06a-cb:checked ~ .l06a-box .l06a-g rect,.l06a-cb:checked ~ .l06a-box .l06a-g line,.l06a-cb:checked ~ .l06a-box .l06a-g path:not(.l06a-gl),.l06a-cb:checked ~ .l06a-box .l06a-pk{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.l06a-g rect,.l06a-g line,.l06a-g path:not(.l06a-gl){animation:none;opacity:1}.l06a-pk{animation:none;display:none}.l06a-btn{display:none}}
@keyframes l06a-g0{0%{opacity:1}25%{opacity:1}25.01%,100%{opacity:.5}}
@keyframes l06a-p0{0%,-0.01%{opacity:0;transform:translateX(0)}0%{opacity:1;transform:translateX(0)}20%{opacity:1;transform:translateX(236px)}25%{opacity:1;transform:translateX(236px)}25.01%,100%{opacity:0;transform:translateX(236px)}}
.l06a-g0 rect,.l06a-g0 line,.l06a-g0 path:not(.l06a-gl){animation-name:l06a-g0}.l06a-p0{animation-name:l06a-p0}
@keyframes l06a-g1{0%,24.99%{opacity:.5}25%{opacity:1}50%{opacity:1}50.01%,100%{opacity:.5}}
@keyframes l06a-p1{0%,24.99%{opacity:0;transform:translateX(0)}25%{opacity:1;transform:translateX(0)}45%{opacity:1;transform:translateX(236px)}50%{opacity:1;transform:translateX(236px)}50.01%,100%{opacity:0;transform:translateX(236px)}}
.l06a-g1 rect,.l06a-g1 line,.l06a-g1 path:not(.l06a-gl){animation-name:l06a-g1}.l06a-p1{animation-name:l06a-p1}
@keyframes l06a-g2{0%,49.99%{opacity:.5}50%{opacity:1}66.667%{opacity:1}66.677%,100%{opacity:.5}}
.l06a-g2 rect,.l06a-g2 line,.l06a-g2 path:not(.l06a-gl){animation-name:l06a-g2}
@keyframes l06a-g3{0%,66.657%{opacity:.5}66.667%{opacity:1}83.333%{opacity:1}83.343%,100%{opacity:.5}}
.l06a-g3 rect,.l06a-g3 line,.l06a-g3 path:not(.l06a-gl){animation-name:l06a-g3}
@keyframes l06a-g4{0%,83.323%{opacity:.5}83.333%{opacity:1}100%{opacity:1}100.01%,100%{opacity:.5}}
.l06a-g4 rect,.l06a-g4 line,.l06a-g4 path:not(.l06a-gl){animation-name:l06a-g4}
</style>
<defs>
<marker id="l06a-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="l06a-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="l06a-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<line class="l06a-life" x1="110" y1="72" x2="110" y2="488"/>
<line class="l06a-life" x1="380" y1="72" x2="380" y2="488"/>
<line class="l06a-life" x1="650" y1="72" x2="650" y2="488"/>
<rect class="l06a-box" x="20" y="10" width="180" height="62" rx="10"/><text class="l06a-ttl" x="110" y="36">Sam</text><text class="l06a-sub" x="110" y="56">types into the page</text>
<rect class="l06a-box" x="290" y="10" width="180" height="62" rx="10"/><text class="l06a-ttl" x="380" y="36">Fake page</text><text class="l06a-sub" x="380" y="56">sits in the middle</text>
<rect class="l06a-box" x="560" y="10" width="180" height="62" rx="10"/><text class="l06a-ttl" x="650" y="36">Real site</text><text class="l06a-sub" x="650" y="56">the expense app</text>
<g class="l06a-g l06a-g0">
<text class="l06a-main" x="245" y="108">password and</text>
<text class="l06a-dim" x="245" y="124">six-digit code</text>
<line class="l06a-front" x1="124" y1="138" x2="366" y2="138" marker-end="url(#l06a-m-front)"/>
<circle class="l06a-badge l06a-b-front" cx="110" cy="138" r="12"/><text class="l06a-bt" x="110" y="142.5">1</text>
</g>
<g class="l06a-g l06a-g1">
<text class="l06a-main l06a-badt" x="515" y="178">passes both on</text>
<text class="l06a-dim" x="515" y="194">instantly</text>
<line class="l06a-bad" x1="394" y1="208" x2="636" y2="208" marker-end="url(#l06a-m-bad)"/>
<circle class="l06a-badge l06a-b-bad" cx="380" cy="208" r="12"/><text class="l06a-bt" x="380" y="212.5">2</text>
</g>
<g class="l06a-g l06a-g2">
<rect class="l06a-note" x="575" y="242" width="150" height="31" rx="8"/>
<text class="l06a-nt" x="650" y="263">accepts them</text>
</g>
<g class="l06a-g l06a-g3">
<rect class="l06a-note-bad" x="305" y="301" width="150" height="48" rx="8"/>
<text class="l06a-nt" x="380" y="322">the attacker is</text>
<text class="l06a-nt" x="380" y="339">signed in as Sam</text>
</g>
<g class="l06a-g l06a-g4">
<rect class="l06a-note-good" x="10" y="377" width="201" height="65" rx="8"/>
<text class="l06a-nt" x="110" y="398">typing a code does not tie</text>
<text class="l06a-nt" x="110" y="415">it to the one site it was</text>
<text class="l06a-nt" x="110" y="432">meant for</text>
</g>
<circle class="l06a-pk l06a-p0" cx="130" cy="138" r="5.5"/>
<circle class="l06a-pk l06a-p1 l06a-pkbad" cx="400" cy="208" r="5.5"/>
<line class="l06a-front" x1="40" y1="516" x2="70" y2="516"/>
<text class="l06a-dim" x="78" y="520" style="text-anchor:start">Sam's step</text>
<line class="l06a-bad" x1="176" y1="516" x2="206" y2="516"/>
<text class="l06a-dim" x="214" y="520" style="text-anchor:start">the fake page relays</text>
<rect class="l06a-note-good" x="376" y="508" width="22" height="16" rx="4"/>
<text class="l06a-dim" x="406" y="520" style="text-anchor:start">why it works</text>
</svg>
</div>
</div>
<!-- /diagram:aitm-relay -->

Badges 1 and 2 number the two hops. The note under Sam gives the reason it works: typing a code does not tie it to the one site it was meant for.

NIST says factors where a person types in a value, such as one-time codes, are not phishing-resistant, because typing does not tie the code to the one site it was meant for. *Phishing-resistant* means the method itself cannot hand a valid proof to a fake site, without relying on Sam to spot the fake. Okta lists two phishing-resistant authenticators: Passkey (FIDO2 WebAuthn) and Okta FastPass. Microsoft Entra's built-in Phishing-resistant MFA strength allows FIDO2 security keys, Windows Hello for Business and certificate-based sign-in.

## How a passkey proves who you are

A passkey is a sign-in credential built on FIDO standards that you can keep on a phone, a computer or a hardware security key. It uses a pair of keys. The *private key* is never sent to the website; it stays with the *authenticator* (the device or security key that holds it). The *public key* is not secret, and the website stores it. To sign in, the website sends a random one-time number called a *challenge*, the authenticator signs it with the private key, and the website checks the signature with the public key. No password crosses the network.

The key is tied to the website's domain name, called the *RP ID* (the relying party is the website). The browser knows which domain the page is really on. On a look-alike domain the browser cannot ask for the real RP ID, so there is nothing to sign, and Sam never has to notice the fake. Sam unlocks the key with a PIN, fingerprint or face on the device, and the website only learns that the check succeeded, not the fingerprint.

<!-- diagram:webauthn-ceremony -->
<div class="wa-wrap" style="position:relative">
<input type="checkbox" id="wa-pause" class="wa-cb" /><label for="wa-pause" class="wa-btn"><span class="wa-off">Pause animation</span><span class="wa-on">Play animation</span></label>
<div class="wa-box" style="overflow-x:auto">
<svg class="wa-flow" viewBox="0 0 760 876" role="img" aria-labelledby="wa-t wa-d" style="width:760px;max-width:100%;min-width:699px;height:auto;display:block;margin:0 auto">
<title id="wa-t">Creating a passkey and signing in with it</title>
<desc id="wa-d">Three parties: the authenticator that holds the private key, the browser, and the site. Creating the passkey, R1 to R4: the site sends a challenge and its RP ID, the browser asks the authenticator to create a key pair and Sam approves with a PIN or fingerprint, the authenticator returns the public key and an ID for the credential, and the browser sends these to the site, which checks them and stores the public key. Using the passkey later, A1 to A4: the site sends a new challenge, the browser asks the authenticator to sign it for the real RP ID, the authenticator returns a signature plus supporting data, and the browser sends these to the site, which checks the signature with the stored public key. On a look-alike domain the browser cannot ask for the real RP ID, so there is nothing to sign. The diagram highlights each step in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
<style>
svg.wa-flow{--ink:light-dark(#000000,#ffffff)}
.wa-box{fill:var(--panel);stroke:var(--border-strong);stroke-width:1.5}
.wa-hot{fill:var(--panel);stroke:var(--accent);stroke-width:2.5}
.wa-ttl{fill:var(--ink);font:600 15px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.wa-sub{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.wa-life{stroke:var(--border-strong);stroke-width:1.5;stroke-dasharray:4 5}
.wa-front{stroke:var(--accent);stroke-width:2;fill:none}
.wa-back{stroke:var(--muted);stroke-width:2;stroke-dasharray:7 5;fill:none}
.wa-bad{stroke:var(--bad);stroke-width:2;fill:none}
.wa-main{fill:var(--ink);font:600 13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.wa-badt{fill:var(--ink)}
.wa-dim{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.wa-badge{fill:var(--accent)}
.wa-b-back{fill:var(--muted)}
.wa-b-bad{fill:var(--bad)}
.wa-b-good{fill:var(--good)}
.wa-bt{fill:var(--on-accent);font:700 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.wa-note{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.wa-note-good{fill:var(--good-bg);stroke:var(--good);stroke-width:1.5}
.wa-note-bad{fill:var(--bad-bg);stroke:var(--bad);stroke-width:1.5}
.wa-nt{fill:var(--ink);font:500 12.5px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.wa-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:56s;animation-timing-function:linear;animation-iteration-count:infinite}
.wa-pk.wa-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.wa-pk.wa-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.wa-wrap{margin:20px 0}
@media (min-width:801px){.wa-wrap{margin-left:-44px;margin-right:-44px}}
.wa-g rect,.wa-g line,.wa-g path:not(.wa-gl){opacity:.5;animation-duration:56s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.wa-flow:hover .wa-g rect,svg.wa-flow:hover .wa-g line,svg.wa-flow:hover .wa-g path:not(.wa-gl),svg.wa-flow:hover .wa-pk{animation-play-state:paused}
.wa-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.wa-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.wa-btn:hover{background:var(--hover)}
.wa-cb:focus-visible + .wa-btn{outline:2px solid var(--accent);outline-offset:2px}
.wa-cb:checked + .wa-btn .wa-off,.wa-cb:not(:checked) + .wa-btn .wa-on{display:none}
.wa-cb:checked ~ .wa-box .wa-g rect,.wa-cb:checked ~ .wa-box .wa-g line,.wa-cb:checked ~ .wa-box .wa-g path:not(.wa-gl),.wa-cb:checked ~ .wa-box .wa-pk{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.wa-g rect,.wa-g line,.wa-g path:not(.wa-gl){animation:none;opacity:1}.wa-pk{animation:none;display:none}.wa-btn{display:none}}
@keyframes wa-g0{0%{opacity:1}10.714%{opacity:1}10.724%,100%{opacity:.5}}
@keyframes wa-p0{0%,-0.01%{opacity:0;transform:translateX(0)}0%{opacity:1;transform:translateX(0)}8.571%{opacity:1;transform:translateX(-236px)}10.714%{opacity:1;transform:translateX(-236px)}10.724%,100%{opacity:0;transform:translateX(-236px)}}
.wa-g0 rect,.wa-g0 line,.wa-g0 path:not(.wa-gl){animation-name:wa-g0}.wa-p0{animation-name:wa-p0}
@keyframes wa-g1{0%,10.704%{opacity:.5}10.714%{opacity:1}21.429%{opacity:1}21.439%,100%{opacity:.5}}
@keyframes wa-p1{0%,10.704%{opacity:0;transform:translateX(0)}10.714%{opacity:1;transform:translateX(0)}19.286%{opacity:1;transform:translateX(-236px)}21.429%{opacity:1;transform:translateX(-236px)}21.439%,100%{opacity:0;transform:translateX(-236px)}}
.wa-g1 rect,.wa-g1 line,.wa-g1 path:not(.wa-gl){animation-name:wa-g1}.wa-p1{animation-name:wa-p1}
@keyframes wa-g2{0%,21.419%{opacity:.5}21.429%{opacity:1}32.143%{opacity:1}32.153%,100%{opacity:.5}}
@keyframes wa-p2{0%,21.419%{opacity:0;transform:translateX(0)}21.429%{opacity:1;transform:translateX(0)}30%{opacity:1;transform:translateX(236px)}32.143%{opacity:1;transform:translateX(236px)}32.153%,100%{opacity:0;transform:translateX(236px)}}
.wa-g2 rect,.wa-g2 line,.wa-g2 path:not(.wa-gl){animation-name:wa-g2}.wa-p2{animation-name:wa-p2}
@keyframes wa-g3{0%,32.133%{opacity:.5}32.143%{opacity:1}42.857%{opacity:1}42.867%,100%{opacity:.5}}
@keyframes wa-p3{0%,32.133%{opacity:0;transform:translateX(0)}32.143%{opacity:1;transform:translateX(0)}40.714%{opacity:1;transform:translateX(236px)}42.857%{opacity:1;transform:translateX(236px)}42.867%,100%{opacity:0;transform:translateX(236px)}}
.wa-g3 rect,.wa-g3 line,.wa-g3 path:not(.wa-gl){animation-name:wa-g3}.wa-p3{animation-name:wa-p3}
@keyframes wa-g4{0%,42.847%{opacity:.5}42.857%{opacity:1}50%{opacity:1}50.01%,100%{opacity:.5}}
.wa-g4 rect,.wa-g4 line,.wa-g4 path:not(.wa-gl){animation-name:wa-g4}
@keyframes wa-g5{0%,49.99%{opacity:.5}50%{opacity:1}60.714%{opacity:1}60.724%,100%{opacity:.5}}
@keyframes wa-p5{0%,49.99%{opacity:0;transform:translateX(0)}50%{opacity:1;transform:translateX(0)}58.571%{opacity:1;transform:translateX(-236px)}60.714%{opacity:1;transform:translateX(-236px)}60.724%,100%{opacity:0;transform:translateX(-236px)}}
.wa-g5 rect,.wa-g5 line,.wa-g5 path:not(.wa-gl){animation-name:wa-g5}.wa-p5{animation-name:wa-p5}
@keyframes wa-g6{0%,60.704%{opacity:.5}60.714%{opacity:1}71.429%{opacity:1}71.439%,100%{opacity:.5}}
@keyframes wa-p6{0%,60.704%{opacity:0;transform:translateX(0)}60.714%{opacity:1;transform:translateX(0)}69.286%{opacity:1;transform:translateX(-236px)}71.429%{opacity:1;transform:translateX(-236px)}71.439%,100%{opacity:0;transform:translateX(-236px)}}
.wa-g6 rect,.wa-g6 line,.wa-g6 path:not(.wa-gl){animation-name:wa-g6}.wa-p6{animation-name:wa-p6}
@keyframes wa-g7{0%,71.419%{opacity:.5}71.429%{opacity:1}82.143%{opacity:1}82.153%,100%{opacity:.5}}
@keyframes wa-p7{0%,71.419%{opacity:0;transform:translateX(0)}71.429%{opacity:1;transform:translateX(0)}80%{opacity:1;transform:translateX(236px)}82.143%{opacity:1;transform:translateX(236px)}82.153%,100%{opacity:0;transform:translateX(236px)}}
.wa-g7 rect,.wa-g7 line,.wa-g7 path:not(.wa-gl){animation-name:wa-g7}.wa-p7{animation-name:wa-p7}
@keyframes wa-g8{0%,82.133%{opacity:.5}82.143%{opacity:1}92.857%{opacity:1}92.867%,100%{opacity:.5}}
@keyframes wa-p8{0%,82.133%{opacity:0;transform:translateX(0)}82.143%{opacity:1;transform:translateX(0)}90.714%{opacity:1;transform:translateX(236px)}92.857%{opacity:1;transform:translateX(236px)}92.867%,100%{opacity:0;transform:translateX(236px)}}
.wa-g8 rect,.wa-g8 line,.wa-g8 path:not(.wa-gl){animation-name:wa-g8}.wa-p8{animation-name:wa-p8}
@keyframes wa-g9{0%,92.847%{opacity:.5}92.857%{opacity:1}100%{opacity:1}100.01%,100%{opacity:.5}}
.wa-g9 rect,.wa-g9 line,.wa-g9 path:not(.wa-gl){animation-name:wa-g9}
</style>
<defs>
<marker id="wa-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="wa-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="wa-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<line class="wa-life" x1="110" y1="72" x2="110" y2="824"/>
<line class="wa-life" x1="380" y1="72" x2="380" y2="824"/>
<line class="wa-life" x1="650" y1="72" x2="650" y2="824"/>
<rect class="wa-box" x="20" y="10" width="180" height="62" rx="10"/><text class="wa-ttl" x="110" y="36">Authenticator</text><text class="wa-sub" x="110" y="56">the private key stays here</text>
<rect class="wa-box" x="290" y="10" width="180" height="62" rx="10"/><text class="wa-ttl" x="380" y="36">Browser</text><text class="wa-sub" x="380" y="56">knows the real domain</text>
<rect class="wa-hot" x="560" y="10" width="180" height="62" rx="10"/><text class="wa-ttl" x="650" y="36">The site</text><text class="wa-sub" x="650" y="56">keeps the public key</text>
<g class="wa-g wa-g0">
<text class="wa-main" x="515" y="108">challenge + RP ID</text>
<line class="wa-front" x1="636" y1="122" x2="394" y2="122" marker-end="url(#wa-m-front)"/>
<circle class="wa-badge wa-b-front" cx="650" cy="122" r="12"/><text class="wa-bt" x="650" y="126.5">R1</text>
</g>
<g class="wa-g wa-g1">
<text class="wa-main" x="245" y="162">create a key pair</text>
<line class="wa-front" x1="366" y1="176" x2="124" y2="176" marker-end="url(#wa-m-front)"/>
<circle class="wa-badge wa-b-front" cx="380" cy="176" r="12"/><text class="wa-bt" x="380" y="180.5">R2</text>
<rect class="wa-note" x="29" y="194" width="162" height="48" rx="8"/>
<text class="wa-nt" x="110" y="215">Sam approves with</text>
<text class="wa-nt" x="110" y="232">a PIN or fingerprint</text>
</g>
<g class="wa-g wa-g2">
<text class="wa-main" x="245" y="276">public key + ID for the credential</text>
<line class="wa-front" x1="124" y1="290" x2="366" y2="290" marker-end="url(#wa-m-front)"/>
<circle class="wa-badge wa-b-front" cx="110" cy="290" r="12"/><text class="wa-bt" x="110" y="294.5">R3</text>
</g>
<g class="wa-g wa-g3">
<text class="wa-main" x="515" y="330">sends these on</text>
<line class="wa-front" x1="394" y1="344" x2="636" y2="344" marker-end="url(#wa-m-front)"/>
<circle class="wa-badge wa-b-front" cx="380" cy="344" r="12"/><text class="wa-bt" x="380" y="348.5">R4</text>
</g>
<g class="wa-g wa-g4">
<rect class="wa-note-good" x="566" y="378" width="168" height="48" rx="8"/>
<text class="wa-nt" x="650" y="399">checks them and</text>
<text class="wa-nt" x="650" y="416">stores the public key</text>
</g>
<g class="wa-g wa-g5">
<text class="wa-main" x="515" y="460">new challenge</text>
<line class="wa-front" x1="636" y1="474" x2="394" y2="474" marker-end="url(#wa-m-front)"/>
<circle class="wa-badge wa-b-front" cx="650" cy="474" r="12"/><text class="wa-bt" x="650" y="478.5">A1</text>
</g>
<g class="wa-g wa-g6">
<text class="wa-main" x="245" y="514">sign it for the real RP ID</text>
<line class="wa-front" x1="366" y1="528" x2="124" y2="528" marker-end="url(#wa-m-front)"/>
<circle class="wa-badge wa-b-front" cx="380" cy="528" r="12"/><text class="wa-bt" x="380" y="532.5">A2</text>
<rect class="wa-note-bad" x="266" y="546" width="228" height="48" rx="8"/>
<text class="wa-nt" x="380" y="567">look-alike domain: the browser</text>
<text class="wa-nt" x="380" y="584">cannot ask for the real RP ID</text>
</g>
<g class="wa-g wa-g7">
<text class="wa-main" x="245" y="628">signature + supporting data</text>
<line class="wa-front" x1="124" y1="642" x2="366" y2="642" marker-end="url(#wa-m-front)"/>
<circle class="wa-badge wa-b-front" cx="110" cy="642" r="12"/><text class="wa-bt" x="110" y="646.5">A3</text>
</g>
<g class="wa-g wa-g8">
<text class="wa-main" x="515" y="682">sends these on</text>
<line class="wa-front" x1="394" y1="696" x2="636" y2="696" marker-end="url(#wa-m-front)"/>
<circle class="wa-badge wa-b-front" cx="380" cy="696" r="12"/><text class="wa-bt" x="380" y="700.5">A4</text>
</g>
<g class="wa-g wa-g9">
<rect class="wa-note-good" x="552" y="730" width="195" height="48" rx="8"/>
<text class="wa-nt" x="650" y="751">checks the signature with</text>
<text class="wa-nt" x="650" y="768">the stored public key</text>
</g>
<circle class="wa-pk wa-p0" cx="630" cy="122" r="5.5"/>
<circle class="wa-pk wa-p1" cx="360" cy="176" r="5.5"/>
<circle class="wa-pk wa-p2" cx="130" cy="290" r="5.5"/>
<circle class="wa-pk wa-p3" cx="400" cy="344" r="5.5"/>
<circle class="wa-pk wa-p5" cx="630" cy="474" r="5.5"/>
<circle class="wa-pk wa-p6" cx="360" cy="528" r="5.5"/>
<circle class="wa-pk wa-p7" cx="130" cy="642" r="5.5"/>
<circle class="wa-pk wa-p8" cx="400" cy="696" r="5.5"/>
<line class="wa-front" x1="40" y1="852" x2="70" y2="852"/>
<text class="wa-dim" x="78" y="856" style="text-anchor:start">one step</text>
<rect class="wa-note-bad" x="163" y="844" width="22" height="16" rx="4"/>
<text class="wa-dim" x="193" y="856" style="text-anchor:start">failure mode</text>
<rect class="wa-note-good" x="303" y="844" width="22" height="16" rx="4"/>
<text class="wa-dim" x="333" y="856" style="text-anchor:start">what the site does</text>
</svg>
</div>
</div>
<!-- /diagram:webauthn-ceremony -->

R1 to R4 create the passkey; A1 to A4 use it on a later day. The numbers match the list below. The note marked as a failure shows why a look-alike domain gets nothing.

Read the diagram with these numbers. First, creating the passkey:

- **R1**: the site sends a challenge and its RP ID.
- **R2**: the browser asks the authenticator to create a key pair, and Sam approves with a PIN or fingerprint.
- **R3**: the authenticator returns the public key and an ID for the credential.
- **R4**: the browser sends these to the site, which checks them and stores the public key.

Then, using the passkey on a later day:

- **A1**: the site sends a new challenge.
- **A2**: the browser asks the authenticator to sign it for the real RP ID.
- **A3**: the authenticator returns a signature, plus some supporting data.
- **A4**: the browser sends these to the site, which checks the signature with the stored public key.

## What passkeys change for IT

FIDO describes two kinds. A **synced passkey** is copied between a person's devices by a cloud service such as iCloud Keychain or Google Password Manager. A **device-bound passkey** stays on one device or hardware security key and never leaves it.

- **Recovery.** A lost device-bound passkey has no copy. The WebAuthn specification says a site should make sure each account has an additional authenticator or an account recovery process. A synced passkey survives a lost phone, but it lives in a cloud account that belongs to the employee, not to your directory.
- **Enrolment.** When people create their own first passkey, they need to sign in some other way first, so that first sign-in is the weak point to protect.
- **Shared devices.** A synced passkey saved in a shared computer's own sign-in account would be available to whoever uses that account. As a rule of thumb, give shared-computer users a security key they carry.

## Sessions: what happens after the sign-in

After a successful sign-in the site gives the browser a *session cookie*, a random value the browser sends with every request. The site checks only this cookie, so Sam is not asked for a password and MFA on every click. Two timers limit it. The *idle timeout* ends the session after a period with no activity. The *absolute timeout* (NIST calls it the overall timeout) ends it a fixed time after sign-in even if Sam is busy. In Okta these are the Maximum Okta global session idle time and Maximum Okta global session lifetime settings. Cookie flags help too: *Secure* means the browser sends the cookie only over HTTPS, and *HttpOnly* means scripts on the page cannot read it.

<!-- diagram:session-cookie -->
<div class="l06b-wrap" style="position:relative">
<input type="checkbox" id="l06b-pause" class="l06b-cb" /><label for="l06b-pause" class="l06b-btn"><span class="l06b-off">Pause animation</span><span class="l06b-on">Play animation</span></label>
<div class="l06b-box" style="overflow-x:auto">
<svg class="l06b-flow" viewBox="0 0 760 756" role="img" aria-labelledby="l06b-t l06b-d" style="width:760px;max-width:100%;min-width:699px;height:auto;display:block;margin:0 auto">
<title id="l06b-t">A session cookie works like a bearer ticket</title>
<desc id="l06b-d">Three parties: Sam's browser, the expense app, and an attacker's computer. Sam signs in, and MFA happens at sign-in. The app gives the browser a session cookie, and the browser sends the cookie with every request. The app checks only the cookie, so Sam is not asked for a password and MFA on every click. An idle timeout and an absolute timeout end the session. If malware copies the cookie, or an AitM relay captures it, the attacker sends the same cookie from another computer. The cookie works like a bearer ticket, so the attacker is treated as signed in and is not asked for MFA again. The diagram highlights each step in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
<style>
svg.l06b-flow{--ink:light-dark(#000000,#ffffff)}
.l06b-box{fill:var(--panel);stroke:var(--border-strong);stroke-width:1.5}
.l06b-hot{fill:var(--panel);stroke:var(--accent);stroke-width:2.5}
.l06b-ttl{fill:var(--ink);font:600 15px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l06b-sub{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l06b-life{stroke:var(--border-strong);stroke-width:1.5;stroke-dasharray:4 5}
.l06b-front{stroke:var(--accent);stroke-width:2;fill:none}
.l06b-back{stroke:var(--muted);stroke-width:2;stroke-dasharray:7 5;fill:none}
.l06b-bad{stroke:var(--bad);stroke-width:2;fill:none}
.l06b-main{fill:var(--ink);font:600 13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l06b-badt{fill:var(--ink)}
.l06b-dim{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l06b-badge{fill:var(--accent)}
.l06b-b-back{fill:var(--muted)}
.l06b-b-bad{fill:var(--bad)}
.l06b-b-good{fill:var(--good)}
.l06b-bt{fill:var(--on-accent);font:700 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l06b-note{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l06b-note-good{fill:var(--good-bg);stroke:var(--good);stroke-width:1.5}
.l06b-note-bad{fill:var(--bad-bg);stroke:var(--bad);stroke-width:1.5}
.l06b-nt{fill:var(--ink);font:500 12.5px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l06b-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:40s;animation-timing-function:linear;animation-iteration-count:infinite}
.l06b-pk.l06b-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.l06b-pk.l06b-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.l06b-wrap{margin:20px 0}
@media (min-width:801px){.l06b-wrap{margin-left:-44px;margin-right:-44px}}
.l06b-g rect,.l06b-g line,.l06b-g path:not(.l06b-gl){opacity:.5;animation-duration:40s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.l06b-flow:hover .l06b-g rect,svg.l06b-flow:hover .l06b-g line,svg.l06b-flow:hover .l06b-g path:not(.l06b-gl),svg.l06b-flow:hover .l06b-pk{animation-play-state:paused}
.l06b-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.l06b-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.l06b-btn:hover{background:var(--hover)}
.l06b-cb:focus-visible + .l06b-btn{outline:2px solid var(--accent);outline-offset:2px}
.l06b-cb:checked + .l06b-btn .l06b-off,.l06b-cb:not(:checked) + .l06b-btn .l06b-on{display:none}
.l06b-cb:checked ~ .l06b-box .l06b-g rect,.l06b-cb:checked ~ .l06b-box .l06b-g line,.l06b-cb:checked ~ .l06b-box .l06b-g path:not(.l06b-gl),.l06b-cb:checked ~ .l06b-box .l06b-pk{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.l06b-g rect,.l06b-g line,.l06b-g path:not(.l06b-gl){animation:none;opacity:1}.l06b-pk{animation:none;display:none}.l06b-btn{display:none}}
@keyframes l06b-g0{0%{opacity:1}15%{opacity:1}15.01%,100%{opacity:.5}}
@keyframes l06b-p0{0%,-0.01%{opacity:0;transform:translateX(0)}0%{opacity:1;transform:translateX(0)}12%{opacity:1;transform:translateX(236px)}15%{opacity:1;transform:translateX(236px)}15.01%,100%{opacity:0;transform:translateX(236px)}}
.l06b-g0 rect,.l06b-g0 line,.l06b-g0 path:not(.l06b-gl){animation-name:l06b-g0}.l06b-p0{animation-name:l06b-p0}
@keyframes l06b-g1{0%,14.99%{opacity:.5}15%{opacity:1}30%{opacity:1}30.01%,100%{opacity:.5}}
@keyframes l06b-p1{0%,14.99%{opacity:0;transform:translateX(0)}15%{opacity:1;transform:translateX(0)}27%{opacity:1;transform:translateX(-236px)}30%{opacity:1;transform:translateX(-236px)}30.01%,100%{opacity:0;transform:translateX(-236px)}}
.l06b-g1 rect,.l06b-g1 line,.l06b-g1 path:not(.l06b-gl){animation-name:l06b-g1}.l06b-p1{animation-name:l06b-p1}
@keyframes l06b-g2{0%,29.99%{opacity:.5}30%{opacity:1}45%{opacity:1}45.01%,100%{opacity:.5}}
@keyframes l06b-p2{0%,29.99%{opacity:0;transform:translateX(0)}30%{opacity:1;transform:translateX(0)}42%{opacity:1;transform:translateX(236px)}45%{opacity:1;transform:translateX(236px)}45.01%,100%{opacity:0;transform:translateX(236px)}}
.l06b-g2 rect,.l06b-g2 line,.l06b-g2 path:not(.l06b-gl){animation-name:l06b-g2}.l06b-p2{animation-name:l06b-p2}
@keyframes l06b-g3{0%,44.99%{opacity:.5}45%{opacity:1}55%{opacity:1}55.01%,100%{opacity:.5}}
.l06b-g3 rect,.l06b-g3 line,.l06b-g3 path:not(.l06b-gl){animation-name:l06b-g3}
@keyframes l06b-g4{0%,54.99%{opacity:.5}55%{opacity:1}65%{opacity:1}65.01%,100%{opacity:.5}}
.l06b-g4 rect,.l06b-g4 line,.l06b-g4 path:not(.l06b-gl){animation-name:l06b-g4}
@keyframes l06b-g5{0%,64.99%{opacity:.5}65%{opacity:1}75%{opacity:1}75.01%,100%{opacity:.5}}
.l06b-g5 rect,.l06b-g5 line,.l06b-g5 path:not(.l06b-gl){animation-name:l06b-g5}
@keyframes l06b-g6{0%,74.99%{opacity:.5}75%{opacity:1}90%{opacity:1}90.01%,100%{opacity:.5}}
@keyframes l06b-p6{0%,74.99%{opacity:0;transform:translateX(0)}75%{opacity:1;transform:translateX(0)}87%{opacity:1;transform:translateX(-236px)}90%{opacity:1;transform:translateX(-236px)}90.01%,100%{opacity:0;transform:translateX(-236px)}}
.l06b-g6 rect,.l06b-g6 line,.l06b-g6 path:not(.l06b-gl){animation-name:l06b-g6}.l06b-p6{animation-name:l06b-p6}
@keyframes l06b-g7{0%,89.99%{opacity:.5}90%{opacity:1}100%{opacity:1}100.01%,100%{opacity:.5}}
.l06b-g7 rect,.l06b-g7 line,.l06b-g7 path:not(.l06b-gl){animation-name:l06b-g7}
</style>
<defs>
<marker id="l06b-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="l06b-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="l06b-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<line class="l06b-life" x1="110" y1="72" x2="110" y2="704"/>
<line class="l06b-life" x1="380" y1="72" x2="380" y2="704"/>
<line class="l06b-life" x1="650" y1="72" x2="650" y2="704"/>
<rect class="l06b-box" x="20" y="10" width="180" height="62" rx="10"/><text class="l06b-ttl" x="110" y="36">Sam's browser</text><text class="l06b-sub" x="110" y="56">holds the cookie</text>
<rect class="l06b-hot" x="290" y="10" width="180" height="62" rx="10"/><text class="l06b-ttl" x="380" y="36">Expense app</text><text class="l06b-sub" x="380" y="56">checks only the cookie</text>
<rect class="l06b-box" x="560" y="10" width="180" height="62" rx="10"/><text class="l06b-ttl" x="650" y="36">Attacker</text><text class="l06b-sub" x="650" y="56">another computer</text>
<g class="l06b-g l06b-g0">
<text class="l06b-main" x="245" y="108">Sam signs in</text>
<text class="l06b-dim" x="245" y="124">MFA happens here</text>
<line class="l06b-front" x1="124" y1="138" x2="366" y2="138" marker-end="url(#l06b-m-front)"/>
<circle class="l06b-badge l06b-b-front" cx="110" cy="138" r="12"/><text class="l06b-bt" x="110" y="142.5">1</text>
</g>
<g class="l06b-g l06b-g1">
<text class="l06b-main" x="245" y="178">session cookie</text>
<text class="l06b-dim" x="245" y="194">a random value</text>
<line class="l06b-front" x1="366" y1="208" x2="124" y2="208" marker-end="url(#l06b-m-front)"/>
<circle class="l06b-badge l06b-b-front" cx="380" cy="208" r="12"/><text class="l06b-bt" x="380" y="212.5">2</text>
</g>
<g class="l06b-g l06b-g2">
<text class="l06b-main" x="245" y="248">sends the cookie</text>
<text class="l06b-dim" x="245" y="264">with every request</text>
<line class="l06b-front" x1="124" y1="278" x2="366" y2="278" marker-end="url(#l06b-m-front)"/>
<circle class="l06b-badge l06b-b-front" cx="110" cy="278" r="12"/><text class="l06b-bt" x="110" y="282.5">3</text>
</g>
<g class="l06b-g l06b-g3">
<rect class="l06b-note-good" x="305" y="312" width="150" height="48" rx="8"/>
<text class="l06b-nt" x="380" y="333">no password or MFA</text>
<text class="l06b-nt" x="380" y="350">on every click</text>
</g>
<g class="l06b-g l06b-g4">
<rect class="l06b-note-good" x="286" y="388" width="188" height="48" rx="8"/>
<text class="l06b-nt" x="380" y="409">idle and absolute</text>
<text class="l06b-nt" x="380" y="426">timeouts end the session</text>
</g>
<g class="l06b-g l06b-g5">
<rect class="l06b-note-bad" x="552" y="464" width="195" height="48" rx="8"/>
<text class="l06b-nt" x="650" y="485">copied by malware, or</text>
<text class="l06b-nt" x="650" y="502">captured by an AitM relay</text>
</g>
<g class="l06b-g l06b-g6">
<text class="l06b-main l06b-badt" x="515" y="546">the same cookie,</text>
<text class="l06b-dim" x="515" y="562">from another computer</text>
<line class="l06b-bad" x1="636" y1="576" x2="394" y2="576" marker-end="url(#l06b-m-bad)"/>
<circle class="l06b-badge l06b-b-bad" cx="650" cy="576" r="12"/><text class="l06b-bt" x="650" y="580.5">4</text>
</g>
<g class="l06b-g l06b-g7">
<rect class="l06b-note-bad" x="276" y="610" width="208" height="48" rx="8"/>
<text class="l06b-nt" x="380" y="631">whoever holds it is treated</text>
<text class="l06b-nt" x="380" y="648">as signed in: no MFA again</text>
</g>
<circle class="l06b-pk l06b-p0" cx="130" cy="138" r="5.5"/>
<circle class="l06b-pk l06b-p1" cx="360" cy="208" r="5.5"/>
<circle class="l06b-pk l06b-p2" cx="130" cy="278" r="5.5"/>
<circle class="l06b-pk l06b-p6 l06b-pkbad" cx="630" cy="576" r="5.5"/>
<line class="l06b-front" x1="40" y1="732" x2="70" y2="732"/>
<text class="l06b-dim" x="78" y="736" style="text-anchor:start">Sam's browser</text>
<line class="l06b-bad" x1="195" y1="732" x2="225" y2="732"/>
<text class="l06b-dim" x="233" y="736" style="text-anchor:start">the attacker</text>
<rect class="l06b-note-good" x="343" y="724" width="22" height="16" rx="4"/>
<text class="l06b-dim" x="373" y="736" style="text-anchor:start">what the app does</text>
</svg>
</div>
</div>
<!-- /diagram:session-cookie -->

Badges 1 to 4 number this diagram's own hops, not the steps of any list. Watch the app lane: it checks only the cookie, so a copy of the cookie is treated like the original.

> MFA happens at sign-in, not on every click. A session cookie works like a bearer ticket: whoever holds it is treated as signed in. If malware copies Sam's cookie, or an AitM relay captures it after the real site issues it, the attacker uses it from another computer and is not asked for MFA again. Shorter timeouts, ending sessions when someone leaves, and phishing-resistant sign-in all reduce the risk. Browser makers are building ways to tie a session to the device, called Device Bound Session Credentials. The specification is still a draft, and support is only starting to ship: Google says it is generally available in Chrome on Windows.

## Your task

Pick an app you use every day. Write down which factor categories your sign-in uses, whether the second factor is typed or tapped, and whether it would survive a fake page. Then find out how long the app keeps you signed in. The next lesson covers who is allowed to do what once you are in: authorization and the identity lifecycle.
