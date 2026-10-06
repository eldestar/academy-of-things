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

NIST says factors where a person types in a value, such as one-time codes, are not phishing-resistant, because typing does not tie the code to the one site it was meant for. *Phishing-resistant* means the method itself cannot hand a valid proof to a fake site, without relying on Sam to spot the fake. Okta lists two phishing-resistant authenticators: Passkey (FIDO2 WebAuthn) and Okta FastPass. Microsoft Entra's built-in Phishing-resistant MFA strength allows FIDO2 security keys, Windows Hello for Business and certificate-based sign-in.

## How a passkey proves who you are

<!-- diagram:webauthn-ceremony -->
<div style="position:relative;margin:20px 0">
<input type="checkbox" id="wa-pause" class="wa-cb" /><label for="wa-pause" class="wa-btn"><span class="wa-off">Pause animation</span><span class="wa-on">Play animation</span></label>
<div class="wa-box" style="overflow-x:auto">
<svg class="wa-flow" viewBox="0 0 760 1037" role="img" aria-labelledby="wa-t wa-d" style="width:100%;min-width:640px;max-width:800px;height:auto;display:block;margin:0 auto">
<title id="wa-t">WebAuthn registration and authentication ceremonies</title>
<desc id="wa-d">Three parties: the user with an authenticator, the browser, and the relying party. Registration: the relying party sends creation options with a challenge and its RP ID, the browser asks the authenticator to create a key pair if the RP ID fits the page origin, the user approves with a gesture, the authenticator returns the public key and credential ID, and the browser sends the registration response to the relying party, which checks the challenge, origin and RP ID hash and stores the public key. Authentication: the relying party sends a fresh challenge, the browser asks the authenticator to sign it for the RP ID of the real origin, the user approves, the authenticator returns a signature and authenticator data, and the browser sends the assertion response (client data, authenticator data and signature) to the relying party, which verifies the signature with the stored public key and checks the challenge, origin, RP ID hash and user presence flag. On a look-alike domain the browser cannot request the real RP ID, so no credential signs. The diagram highlights each step in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
<style>
.wa-box{fill:var(--panel);stroke:var(--border-strong);stroke-width:1.5}
.wa-hot{fill:var(--panel);stroke:var(--accent);stroke-width:2.5}
.wa-ttl{fill:var(--text);font:600 15px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.wa-sub{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.wa-life{stroke:var(--border-strong);stroke-width:1.5;stroke-dasharray:4 5}
.wa-front{stroke:var(--accent);stroke-width:2;fill:none}
.wa-back{stroke:var(--muted);stroke-width:2;stroke-dasharray:7 5;fill:none}
.wa-bad{stroke:var(--bad);stroke-width:2;fill:none}
.wa-main{fill:var(--text);font:600 13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.wa-badt{fill:var(--bad-text)}
.wa-dim{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.wa-badge{fill:var(--accent)}
.wa-b-back{fill:var(--muted)}
.wa-b-bad{fill:var(--bad)}
.wa-b-good{fill:var(--good)}
.wa-bt{fill:var(--on-accent);font:700 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.wa-note{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.wa-note-good{fill:var(--good-bg);stroke:var(--good);stroke-width:1.5}
.wa-note-bad{fill:var(--bad-bg);stroke:var(--bad);stroke-width:1.5}
.wa-nt{fill:var(--body);font:12.5px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.wa-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:32s;animation-timing-function:linear;animation-iteration-count:infinite}
.wa-pk.wa-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.wa-pk.wa-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.wa-g{opacity:.45;animation-duration:32s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.wa-flow:hover .wa-g,svg.wa-flow:hover .wa-pk{animation-play-state:paused}
.wa-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.wa-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.wa-btn:hover{background:var(--hover)}
.wa-cb:focus-visible + .wa-btn{outline:2px solid var(--accent);outline-offset:2px}
.wa-cb:checked + .wa-btn .wa-off,.wa-cb:not(:checked) + .wa-btn .wa-on{display:none}
.wa-cb:checked ~ .wa-box .wa-g,.wa-cb:checked ~ .wa-box .wa-pk{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.wa-g{animation:none;opacity:1}.wa-pk{animation:none;display:none}.wa-btn{display:none}}
@keyframes wa-g0{0%{opacity:1}10%{opacity:1}10.01%,100%{opacity:.45}}
@keyframes wa-p0{0%,-0.01%{opacity:0;transform:translateX(0)}0%{opacity:1;transform:translateX(0)}10%{opacity:1;transform:translateX(-236px)}10.01%,100%{opacity:0;transform:translateX(-236px)}}
.wa-g0{animation-name:wa-g0}.wa-p0{animation-name:wa-p0}
@keyframes wa-g1{0%,9.99%{opacity:.45}10%{opacity:1}20%{opacity:1}20.01%,100%{opacity:.45}}
@keyframes wa-p1{0%,9.99%{opacity:0;transform:translateX(0)}10%{opacity:1;transform:translateX(0)}20%{opacity:1;transform:translateX(-236px)}20.01%,100%{opacity:0;transform:translateX(-236px)}}
.wa-g1{animation-name:wa-g1}.wa-p1{animation-name:wa-p1}
@keyframes wa-g2{0%,19.99%{opacity:.45}20%{opacity:1}30%{opacity:1}30.01%,100%{opacity:.45}}
@keyframes wa-p2{0%,19.99%{opacity:0;transform:translateX(0)}20%{opacity:1;transform:translateX(0)}30%{opacity:1;transform:translateX(236px)}30.01%,100%{opacity:0;transform:translateX(236px)}}
.wa-g2{animation-name:wa-g2}.wa-p2{animation-name:wa-p2}
@keyframes wa-g3{0%,29.99%{opacity:.45}30%{opacity:1}40%{opacity:1}40.01%,100%{opacity:.45}}
@keyframes wa-p3{0%,29.99%{opacity:0;transform:translateX(0)}30%{opacity:1;transform:translateX(0)}40%{opacity:1;transform:translateX(236px)}40.01%,100%{opacity:0;transform:translateX(236px)}}
.wa-g3{animation-name:wa-g3}.wa-p3{animation-name:wa-p3}
@keyframes wa-g4{0%,39.99%{opacity:.45}40%{opacity:1}50%{opacity:1}50.01%,100%{opacity:.45}}
.wa-g4{animation-name:wa-g4}
@keyframes wa-g5{0%,49.99%{opacity:.45}50%{opacity:1}60%{opacity:1}60.01%,100%{opacity:.45}}
@keyframes wa-p5{0%,49.99%{opacity:0;transform:translateX(0)}50%{opacity:1;transform:translateX(0)}60%{opacity:1;transform:translateX(-236px)}60.01%,100%{opacity:0;transform:translateX(-236px)}}
.wa-g5{animation-name:wa-g5}.wa-p5{animation-name:wa-p5}
@keyframes wa-g6{0%,59.99%{opacity:.45}60%{opacity:1}70%{opacity:1}70.01%,100%{opacity:.45}}
@keyframes wa-p6{0%,59.99%{opacity:0;transform:translateX(0)}60%{opacity:1;transform:translateX(0)}70%{opacity:1;transform:translateX(-236px)}70.01%,100%{opacity:0;transform:translateX(-236px)}}
.wa-g6{animation-name:wa-g6}.wa-p6{animation-name:wa-p6}
@keyframes wa-g7{0%,69.99%{opacity:.45}70%{opacity:1}80%{opacity:1}80.01%,100%{opacity:.45}}
@keyframes wa-p7{0%,69.99%{opacity:0;transform:translateX(0)}70%{opacity:1;transform:translateX(0)}80%{opacity:1;transform:translateX(236px)}80.01%,100%{opacity:0;transform:translateX(236px)}}
.wa-g7{animation-name:wa-g7}.wa-p7{animation-name:wa-p7}
@keyframes wa-g8{0%,79.99%{opacity:.45}80%{opacity:1}90%{opacity:1}90.01%,100%{opacity:.45}}
@keyframes wa-p8{0%,79.99%{opacity:0;transform:translateX(0)}80%{opacity:1;transform:translateX(0)}90%{opacity:1;transform:translateX(236px)}90.01%,100%{opacity:0;transform:translateX(236px)}}
.wa-g8{animation-name:wa-g8}.wa-p8{animation-name:wa-p8}
@keyframes wa-g9{0%,89.99%{opacity:.45}90%{opacity:1}100%{opacity:1}100.01%,100%{opacity:.45}}
.wa-g9{animation-name:wa-g9}
</style>
<defs>
<marker id="wa-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="wa-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="wa-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<line class="wa-life" x1="110" y1="72" x2="110" y2="985"/>
<line class="wa-life" x1="380" y1="72" x2="380" y2="985"/>
<line class="wa-life" x1="650" y1="72" x2="650" y2="985"/>
<rect class="wa-box" x="20" y="10" width="180" height="62" rx="10"/><text class="wa-ttl" x="110" y="36">User + authenticator</text><text class="wa-sub" x="110" y="56">the key pair lives here</text>
<rect class="wa-box" x="290" y="10" width="180" height="62" rx="10"/><text class="wa-ttl" x="380" y="36">Browser</text><text class="wa-sub" x="380" y="56">knows the real origin</text>
<rect class="wa-hot" x="560" y="10" width="180" height="62" rx="10"/><text class="wa-ttl" x="650" y="36">Relying party</text><text class="wa-sub" x="650" y="56">the site or the IdP</text>
<g class="wa-g wa-g0">
<text class="wa-main" x="515" y="108">creation options</text>
<text class="wa-dim" x="515" y="124">challenge, RP ID, user</text>
<line class="wa-front" x1="636" y1="138" x2="394" y2="138" marker-end="url(#wa-m-front)"/>
<circle class="wa-badge wa-b-front" cx="650" cy="138" r="12"/><text class="wa-bt" x="650" y="142.5">R1</text>
</g>
<g class="wa-g wa-g1">
<text class="wa-main" x="245" y="178">create a key pair</text>
<text class="wa-dim" x="245" y="194">only if the RP ID fits the origin</text>
<line class="wa-front" x1="366" y1="208" x2="124" y2="208" marker-end="url(#wa-m-front)"/>
<circle class="wa-badge wa-b-front" cx="380" cy="208" r="12"/><text class="wa-bt" x="380" y="212.5">R2</text>
<rect class="wa-note" x="10" y="226" width="214" height="48" rx="8"/>
<text class="wa-nt" x="117" y="247">user approves with a gesture</text>
<text class="wa-nt" x="117" y="264">(touch, PIN, biometric)</text>
</g>
<g class="wa-g wa-g2">
<text class="wa-main" x="245" y="308">public key + credential ID</text>
<text class="wa-dim" x="245" y="324">plus an attestation object</text>
<line class="wa-front" x1="124" y1="338" x2="366" y2="338" marker-end="url(#wa-m-front)"/>
<circle class="wa-badge wa-b-front" cx="110" cy="338" r="12"/><text class="wa-bt" x="110" y="342.5">R3</text>
</g>
<g class="wa-g wa-g3">
<text class="wa-main" x="515" y="378">registration response</text>
<text class="wa-dim" x="515" y="394">clientDataJSON, attestationObject</text>
<line class="wa-front" x1="394" y1="408" x2="636" y2="408" marker-end="url(#wa-m-front)"/>
<circle class="wa-badge wa-b-front" cx="380" cy="408" r="12"/><text class="wa-bt" x="380" y="412.5">R4</text>
</g>
<g class="wa-g wa-g4">
<rect class="wa-note-good" x="516" y="442" width="234" height="48" rx="8"/>
<text class="wa-nt" x="633" y="463">checks type, challenge, origin,</text>
<text class="wa-nt" x="633" y="480">rpIdHash; stores the public key</text>
</g>
<g class="wa-g wa-g5">
<text class="wa-main" x="515" y="524">request options</text>
<text class="wa-dim" x="515" y="540">fresh challenge, RP ID</text>
<line class="wa-front" x1="636" y1="554" x2="394" y2="554" marker-end="url(#wa-m-front)"/>
<circle class="wa-badge wa-b-front" cx="650" cy="554" r="12"/><text class="wa-bt" x="650" y="558.5">A1</text>
</g>
<g class="wa-g wa-g6">
<text class="wa-main" x="245" y="594">sign this challenge</text>
<text class="wa-dim" x="245" y="610">for the RP ID of this origin</text>
<line class="wa-front" x1="366" y1="624" x2="124" y2="624" marker-end="url(#wa-m-front)"/>
<circle class="wa-badge wa-b-front" cx="380" cy="624" r="12"/><text class="wa-bt" x="380" y="628.5">A2</text>
<rect class="wa-note-bad" x="266" y="642" width="228" height="48" rx="8"/>
<text class="wa-nt" x="380" y="663">look-alike domain: the browser</text>
<text class="wa-nt" x="380" y="680">cannot request the real RP ID</text>
</g>
<g class="wa-g wa-g7">
<text class="wa-main" x="245" y="724">assertion</text>
<text class="wa-dim" x="245" y="740">signature + authenticatorData</text>
<line class="wa-front" x1="124" y1="754" x2="366" y2="754" marker-end="url(#wa-m-front)"/>
<circle class="wa-badge wa-b-front" cx="110" cy="754" r="12"/><text class="wa-bt" x="110" y="758.5">A3</text>
</g>
<g class="wa-g wa-g8">
<text class="wa-main" x="515" y="794">assertion response</text>
<text class="wa-dim" x="515" y="810">clientDataJSON, authenticatorData,</text>
<text class="wa-dim" x="515" y="826">signature</text>
<line class="wa-front" x1="394" y1="840" x2="636" y2="840" marker-end="url(#wa-m-front)"/>
<circle class="wa-badge wa-b-front" cx="380" cy="840" r="12"/><text class="wa-bt" x="380" y="844.5">A4</text>
</g>
<g class="wa-g wa-g9">
<rect class="wa-note-good" x="476" y="874" width="274" height="65" rx="8"/>
<text class="wa-nt" x="613" y="895">verifies the signature with the</text>
<text class="wa-nt" x="613" y="912">stored public key; checks challenge,</text>
<text class="wa-nt" x="613" y="929">origin, rpIdHash, UP (UV if required)</text>
</g>
<circle class="wa-pk wa-p0" cx="630" cy="138" r="5.5"/>
<circle class="wa-pk wa-p1" cx="360" cy="208" r="5.5"/>
<circle class="wa-pk wa-p2" cx="130" cy="338" r="5.5"/>
<circle class="wa-pk wa-p3" cx="400" cy="408" r="5.5"/>
<circle class="wa-pk wa-p5" cx="630" cy="554" r="5.5"/>
<circle class="wa-pk wa-p6" cx="360" cy="624" r="5.5"/>
<circle class="wa-pk wa-p7" cx="130" cy="754" r="5.5"/>
<circle class="wa-pk wa-p8" cx="400" cy="840" r="5.5"/>
<line class="wa-front" x1="40" y1="1013" x2="70" y2="1013"/>
<text class="wa-dim" x="78" y="1017" style="text-anchor:start">message in the ceremony</text>
<rect class="wa-note-good" x="259" y="1005" width="22" height="16" rx="4"/>
<text class="wa-dim" x="289" y="1017" style="text-anchor:start">what the relying party checks</text>
</svg>
</div>
</div>
<!-- /diagram:webauthn-ceremony -->

R1 to R4 register a credential; A1 to A4 authenticate with it. The numbers match the list below.

A passkey is a sign-in credential built on FIDO standards that you can keep on a phone, a computer or a hardware security key. It uses a pair of keys. The *private key* is never sent to the website; it stays with the *authenticator* (the device or security key that holds it). The *public key* is not secret, and the website stores it. To sign in, the website sends a random one-time number called a *challenge*, the authenticator signs it with the private key, and the website checks the signature with the public key. No password crosses the network.

The key is tied to the website's domain name, called the *RP ID* (the relying party is the website). The browser knows which domain the page is really on. On a look-alike domain the browser cannot ask for the real RP ID, so there is nothing to sign, and Sam never has to notice the fake. Sam unlocks the key with a PIN, fingerprint or face on the device, and the website only learns that the check succeeded, not the fingerprint.

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

> MFA happens at sign-in, not on every click. A session cookie works like a bearer ticket: whoever holds it is treated as signed in. If malware copies Sam's cookie, or an AitM relay captures it after the real site issues it, the attacker uses it from another computer and is not asked for MFA again. Shorter timeouts, ending sessions when someone leaves, and phishing-resistant sign-in all reduce the risk. Browser makers are building ways to tie a session to the device, called Device Bound Session Credentials. The specification is still a draft, and support is only starting to ship: Google says it is generally available in Chrome on Windows.

## Your task

Pick an app you use every day. Write down which factor categories your sign-in uses, whether the second factor is typed or tapped, and whether it would survive a fake page. Then find out how long the app keeps you signed in. The next lesson covers who is allowed to do what once you are in: authorization and the identity lifecycle.
