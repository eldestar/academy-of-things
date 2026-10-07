# MFA, passkeys and sessions

Facts checked 2026-10-06 against NIST SP 800-63-4 (final, 31 July 2025; this lesson cites its 63B volume), the W3C WebAuthn Level 3 Recommendation (25 August 2026), RFC 6238, MDN, and Okta and Microsoft Entra documentation. You already run Okta or Entra and have enforced MFA. This lesson separates the factors that stop password theft from the ones that stop phishing, then covers what survives MFA (a stolen session) and the paths around it (recovery, enrolment).

## Factors, and which attack each one stops

The factor categories are knowledge (something you know), possession (something you have) and inherence (something you are). MFA needs two different categories. NIST treats a biometric as an activation factor for a physical authenticator, not as an authenticator alone.

| Method | Stops reuse of a stolen password | Stops a relay (AitM) phishing page | Known weakness |
| --- | --- | --- | --- |
| SMS or voice code | yes | no, the user types it | SIM change, number porting; NIST calls PSTN delivery restricted |
| TOTP app | yes | no, the user types it | shared secret on both sides; clock drift |
| Push approve | yes | no | MFA fatigue |
| Push with number matching | yes | not listed as phishing-resistant by Okta or Entra | blind approval is gone, but the user still types or picks the number |
| Passkey, Okta FastPass, FIDO2 key, Windows Hello for Business | yes | yes | recovery and enrolment become the weak paths |

**TOTP** is HOTP(K, T) with T = floor((now - T0) / X). The RFC 6238 defaults are X = 30 seconds and T0 = 0 (the Unix epoch), with HMAC-SHA-1 as the base and SHA-256 or SHA-512 allowed. The server recomputes the code for the current step and accepts a bounded window around it; the RFC recommends allowing at most one time step as network delay, plus a set resync limit for drift, and it forbids accepting the same OTP twice. One ticket you can get is a phone clock that is minutes off: the phone computes a different T, so every code is rejected until the clock is corrected.

**Push and number matching.** Approve-only push invites fatigue attacks. NIST's out-of-band note calls the method where the user compares secrets on two channels and approves on the phone no longer acceptable, citing fatigue attacks, and requires the secret to be transferred between the phone and the sign-in screen. It adds that choosing from a list of secrets is not sufficient; typing the displayed number into the authenticator is one of the two accepted transfers, and Microsoft says the user enters the number into Authenticator. NIST also says verifiers should limit pushes sent since the last successful authentication. In Okta the Push notification (number challenge) option has three values: Never, Only for high risk sign-in attempts (used when the attempt is considered risky), and All push challenges, and the setting is org-wide, so you cannot enable it for one group. Entra enables number matching for all Microsoft Authenticator push notifications. Okta says the number challenge helps prevent phishing, yet its own phishing-resistant list names only Passkey and FastPass, so treat number matching as a fatigue control.

**SMS.** NIST allows PSTN delivery only as a restricted authenticator: alternatives must be available to every subscriber, and verifiers should weigh risk indicators (device swap, SIM change, number porting) first.

## Phishing resistance, defined and enforced

NIST defines phishing resistance as preventing disclosure of authentication secrets and valid authenticator outputs to an impostor verifier, without relying on the vigilance of the claimant. Manual-entry authenticators (OTP, out-of-band codes) are never phishing-resistant, because an impostor can relay the output to the real verifier. NIST recognises two methods, channel binding and verifier name binding, and names WebAuthn as an example of verifier name binding.

<!-- diagram:aitm-relay -->
<div style="position:relative;margin:20px 0">
<input type="checkbox" id="l06a-pause" class="l06a-cb" /><label for="l06a-pause" class="l06a-btn"><span class="l06a-off">Pause animation</span><span class="l06a-on">Play animation</span></label>
<div class="l06a-box" style="overflow-x:auto">
<svg class="l06a-flow" viewBox="0 0 760 568" role="img" aria-labelledby="l06a-t l06a-d" style="width:100%;min-width:640px;max-width:800px;height:auto;display:block;margin:0 auto">
<title id="l06a-t">Why a relay beats manual-entry factors</title>
<desc id="l06a-d">Three parties: the user, an impostor verifier, and the real verifier. The user types a one-time code into the impostor, which relays the output to the real verifier. The real site returns a session cookie that the relay sees. A note says manual-entry authenticators such as OTP and out-of-band codes are never phishing-resistant, because an impostor can relay the output to the real verifier. A final note says that with a passkey, a page on another domain can neither request your RP ID nor get a signature for it. The diagram highlights each step in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
<style>
.l06a-box{fill:var(--panel);stroke:var(--border-strong);stroke-width:1.5}
.l06a-hot{fill:var(--panel);stroke:var(--accent);stroke-width:2.5}
.l06a-ttl{fill:var(--text);font:600 15px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l06a-sub{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l06a-life{stroke:var(--border-strong);stroke-width:1.5;stroke-dasharray:4 5}
.l06a-front{stroke:var(--accent);stroke-width:2;fill:none}
.l06a-back{stroke:var(--muted);stroke-width:2;stroke-dasharray:7 5;fill:none}
.l06a-bad{stroke:var(--bad);stroke-width:2;fill:none}
.l06a-main{fill:var(--text);font:600 13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l06a-badt{fill:var(--bad-text)}
.l06a-dim{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l06a-badge{fill:var(--accent)}
.l06a-b-back{fill:var(--muted)}
.l06a-b-bad{fill:var(--bad)}
.l06a-b-good{fill:var(--good)}
.l06a-bt{fill:var(--on-accent);font:700 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l06a-note{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l06a-note-good{fill:var(--good-bg);stroke:var(--good);stroke-width:1.5}
.l06a-note-bad{fill:var(--bad-bg);stroke:var(--bad);stroke-width:1.5}
.l06a-nt{fill:var(--body);font:12.5px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l06a-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:18s;animation-timing-function:linear;animation-iteration-count:infinite}
.l06a-pk.l06a-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.l06a-pk.l06a-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.l06a-g{opacity:.45;animation-duration:18s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.l06a-flow:hover .l06a-g,svg.l06a-flow:hover .l06a-pk{animation-play-state:paused}
.l06a-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.l06a-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.l06a-btn:hover{background:var(--hover)}
.l06a-cb:focus-visible + .l06a-btn{outline:2px solid var(--accent);outline-offset:2px}
.l06a-cb:checked + .l06a-btn .l06a-off,.l06a-cb:not(:checked) + .l06a-btn .l06a-on{display:none}
.l06a-cb:checked ~ .l06a-box .l06a-g,.l06a-cb:checked ~ .l06a-box .l06a-pk{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.l06a-g{animation:none;opacity:1}.l06a-pk{animation:none;display:none}.l06a-btn{display:none}}
@keyframes l06a-g0{0%{opacity:1}20%{opacity:1}20.01%,100%{opacity:.45}}
@keyframes l06a-p0{0%,-0.01%{opacity:0;transform:translateX(0)}0%{opacity:1;transform:translateX(0)}20%{opacity:1;transform:translateX(236px)}20.01%,100%{opacity:0;transform:translateX(236px)}}
.l06a-g0{animation-name:l06a-g0}.l06a-p0{animation-name:l06a-p0}
@keyframes l06a-g1{0%,19.99%{opacity:.45}20%{opacity:1}40%{opacity:1}40.01%,100%{opacity:.45}}
@keyframes l06a-p1{0%,19.99%{opacity:0;transform:translateX(0)}20%{opacity:1;transform:translateX(0)}40%{opacity:1;transform:translateX(236px)}40.01%,100%{opacity:0;transform:translateX(236px)}}
.l06a-g1{animation-name:l06a-g1}.l06a-p1{animation-name:l06a-p1}
@keyframes l06a-g2{0%,39.99%{opacity:.45}40%{opacity:1}60%{opacity:1}60.01%,100%{opacity:.45}}
@keyframes l06a-p2{0%,39.99%{opacity:0;transform:translateX(0)}40%{opacity:1;transform:translateX(0)}60%{opacity:1;transform:translateX(-236px)}60.01%,100%{opacity:0;transform:translateX(-236px)}}
.l06a-g2{animation-name:l06a-g2}.l06a-p2{animation-name:l06a-p2}
@keyframes l06a-g3{0%,59.99%{opacity:.45}60%{opacity:1}80%{opacity:1}80.01%,100%{opacity:.45}}
.l06a-g3{animation-name:l06a-g3}
@keyframes l06a-g4{0%,79.99%{opacity:.45}80%{opacity:1}100%{opacity:1}100.01%,100%{opacity:.45}}
.l06a-g4{animation-name:l06a-g4}
</style>
<defs>
<marker id="l06a-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="l06a-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="l06a-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<line class="l06a-life" x1="110" y1="72" x2="110" y2="516"/>
<line class="l06a-life" x1="380" y1="72" x2="380" y2="516"/>
<line class="l06a-life" x1="650" y1="72" x2="650" y2="516"/>
<rect class="l06a-box" x="20" y="10" width="180" height="62" rx="10"/><text class="l06a-ttl" x="110" y="36">User</text><text class="l06a-sub" x="110" y="56">types the code</text>
<rect class="l06a-box" x="290" y="10" width="180" height="62" rx="10"/><text class="l06a-ttl" x="380" y="36">Impostor verifier</text><text class="l06a-sub" x="380" y="56">the relay page</text>
<rect class="l06a-box" x="560" y="10" width="180" height="62" rx="10"/><text class="l06a-ttl" x="650" y="36">Real verifier</text><text class="l06a-sub" x="650" y="56">the real site</text>
<g class="l06a-g l06a-g0">
<text class="l06a-main" x="245" y="108">user types the OTP</text>
<text class="l06a-dim" x="245" y="124">manual entry</text>
<line class="l06a-front" x1="124" y1="138" x2="366" y2="138" marker-end="url(#l06a-m-front)"/>
<circle class="l06a-badge l06a-b-front" cx="110" cy="138" r="12"/><text class="l06a-bt" x="110" y="142.5">1</text>
</g>
<g class="l06a-g l06a-g1">
<text class="l06a-main l06a-badt" x="515" y="178">relays the output</text>
<text class="l06a-dim" x="515" y="194">to the real verifier</text>
<line class="l06a-bad" x1="394" y1="208" x2="636" y2="208" marker-end="url(#l06a-m-bad)"/>
<circle class="l06a-badge l06a-b-bad" cx="380" cy="208" r="12"/><text class="l06a-bt" x="380" y="212.5">2</text>
</g>
<g class="l06a-g l06a-g2">
<text class="l06a-main l06a-badt" x="515" y="248">session cookie</text>
<text class="l06a-dim" x="515" y="264">the relay sees it</text>
<line class="l06a-bad" x1="636" y1="278" x2="394" y2="278" marker-end="url(#l06a-m-bad)"/>
<circle class="l06a-badge l06a-b-bad" cx="650" cy="278" r="12"/><text class="l06a-bt" x="650" y="282.5">3</text>
</g>
<g class="l06a-g l06a-g3">
<rect class="l06a-note-bad" x="270" y="312" width="221" height="65" rx="8"/>
<text class="l06a-nt" x="380" y="333">OTP and out-of-band codes are</text>
<text class="l06a-nt" x="380" y="350">never phishing-resistant: an</text>
<text class="l06a-nt" x="380" y="367">impostor can relay the output</text>
</g>
<g class="l06a-g l06a-g4">
<rect class="l06a-note-good" x="256" y="405" width="247" height="65" rx="8"/>
<text class="l06a-nt" x="380" y="426">passkey: a page on another domain</text>
<text class="l06a-nt" x="380" y="443">can neither request your RP ID</text>
<text class="l06a-nt" x="380" y="460">nor get a signature for it</text>
</g>
<circle class="l06a-pk l06a-p0" cx="130" cy="138" r="5.5"/>
<circle class="l06a-pk l06a-p1 l06a-pkbad" cx="400" cy="208" r="5.5"/>
<circle class="l06a-pk l06a-p2 l06a-pkbad" cx="630" cy="278" r="5.5"/>
<line class="l06a-front" x1="40" y1="544" x2="70" y2="544"/>
<text class="l06a-dim" x="78" y="548" style="text-anchor:start">the user's step</text>
<line class="l06a-bad" x1="208" y1="544" x2="238" y2="544"/>
<text class="l06a-dim" x="246" y="548" style="text-anchor:start">relay (AitM)</text>
<rect class="l06a-note-good" x="356" y="536" width="22" height="16" rx="4"/>
<text class="l06a-dim" x="386" y="548" style="text-anchor:start">phishing-resistant</text>
</svg>
</div>
</div>
<!-- /diagram:aitm-relay -->

Badges 1 to 3 number the hops of one relay. The first note states why manual-entry factors fail here; the second is the passkey contrast, covered under RP ID scope below.

**Okta.** Okta lists Passkey (FIDO2 WebAuthn) and Okta FastPass as its phishing-resistant authenticators. You enforce them in an app sign-in policy rule with Possession factor constraints are: Phishing resistant. FastPass verifies that the request does not come from a malicious site, and a blocked attempt is logged in the System Log with a message such as Okta FastPass declined phishing attempt. Known limits: apps whose WebView implementation Okta does not support fail with an Access denied message when the policy requires phishing resistance; on macOS you need an SSO extension for Safari; and DNS Rebind Protection on a router can stop Okta Verify connecting to browsers or native apps on the device, which fails the check there too.

**Entra.** The built-in Phishing-resistant MFA authentication strength allows Windows Hello for Business or a platform credential, a FIDO2 security key, and certificate-based authentication (multifactor). Microsoft Authenticator phone sign-in satisfies the MFA and Passwordless MFA strengths but not this one. Conditional Access is evaluated only after initial authentication, so a user can still type a password first and must then use a phishing-resistant method.

## How a passkey proves who you are

<!-- diagram:webauthn-ceremony -->
<div style="position:relative;margin:20px 0">
<input type="checkbox" id="wa-pause" class="wa-cb" /><label for="wa-pause" class="wa-btn"><span class="wa-off">Pause animation</span><span class="wa-on">Play animation</span></label>
<div class="wa-box" style="overflow-x:auto">
<svg class="wa-flow" viewBox="0 0 760 1023" role="img" aria-labelledby="wa-t wa-d" style="width:100%;min-width:640px;max-width:800px;height:auto;display:block;margin:0 auto">
<title id="wa-t">WebAuthn registration and authentication ceremonies</title>
<desc id="wa-d">Three parties: the user with an authenticator, the browser, and the relying party (RP). Registration: the RP sends a challenge with its RP ID, the browser checks that the RP ID is the page's domain or a registrable domain suffix of it and asks the authenticator to create a key pair, the user approves with a gesture, the authenticator returns the public key and credential ID, and the browser sends the registration response to the RP, which checks the client data type webauthn.create, the challenge, the origin and the rpIdHash and stores the public key and credential ID. Authentication: the RP sends a fresh challenge, the browser asks the authenticator to sign for the origin's RP ID, the authenticator returns authenticatorData and a signature, and the browser sends clientDataJSON, authenticatorData and the signature to the RP, which finds the credential, checks type webauthn.get, the challenge, the origin, the rpIdHash and the user presence flag, and verifies the signature with the stored public key. A page on another domain can neither request your RP ID nor get a signature for it. The diagram highlights each step in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
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
<line class="wa-life" x1="110" y1="72" x2="110" y2="971"/>
<line class="wa-life" x1="380" y1="72" x2="380" y2="971"/>
<line class="wa-life" x1="650" y1="72" x2="650" y2="971"/>
<rect class="wa-box" x="20" y="10" width="180" height="62" rx="10"/><text class="wa-ttl" x="110" y="36">User + authenticator</text><text class="wa-sub" x="110" y="56">creates the key pair</text>
<rect class="wa-box" x="290" y="10" width="180" height="62" rx="10"/><text class="wa-ttl" x="380" y="36">Browser</text><text class="wa-sub" x="380" y="56">checks the RP ID</text>
<rect class="wa-hot" x="560" y="10" width="180" height="62" rx="10"/><text class="wa-ttl" x="650" y="36">Relying party</text><text class="wa-sub" x="650" y="56">the RP</text>
<g class="wa-g wa-g0">
<text class="wa-main" x="515" y="108">challenge</text>
<text class="wa-dim" x="515" y="124">and the RP ID</text>
<line class="wa-front" x1="636" y1="138" x2="394" y2="138" marker-end="url(#wa-m-front)"/>
<circle class="wa-badge wa-b-front" cx="650" cy="138" r="12"/><text class="wa-bt" x="650" y="142.5">R1</text>
</g>
<g class="wa-g wa-g1">
<text class="wa-main" x="245" y="178">create a key pair</text>
<text class="wa-dim" x="245" y="194">only if the RP ID fits the page's domain</text>
<line class="wa-front" x1="366" y1="208" x2="124" y2="208" marker-end="url(#wa-m-front)"/>
<circle class="wa-badge wa-b-front" cx="380" cy="208" r="12"/><text class="wa-bt" x="380" y="212.5">R2</text>
<rect class="wa-note" x="10" y="226" width="214" height="31" rx="8"/>
<text class="wa-nt" x="117" y="247">user approves with a gesture</text>
</g>
<g class="wa-g wa-g2">
<text class="wa-main" x="245" y="291">public key + credential ID</text>
<line class="wa-front" x1="124" y1="305" x2="366" y2="305" marker-end="url(#wa-m-front)"/>
<circle class="wa-badge wa-b-front" cx="110" cy="305" r="12"/><text class="wa-bt" x="110" y="309.5">R3</text>
</g>
<g class="wa-g wa-g3">
<text class="wa-main" x="515" y="345">sent on to the RP</text>
<text class="wa-dim" x="515" y="361">public key, credential ID, client data</text>
<line class="wa-front" x1="394" y1="375" x2="636" y2="375" marker-end="url(#wa-m-front)"/>
<circle class="wa-badge wa-b-front" cx="380" cy="375" r="12"/><text class="wa-bt" x="380" y="379.5">R4</text>
</g>
<g class="wa-g wa-g4">
<rect class="wa-note-good" x="503" y="409" width="247" height="65" rx="8"/>
<text class="wa-nt" x="626" y="430">checks type webauthn.create,</text>
<text class="wa-nt" x="626" y="447">challenge, origin, rpIdHash;</text>
<text class="wa-nt" x="626" y="464">stores public key + credential ID</text>
</g>
<g class="wa-g wa-g5">
<text class="wa-main" x="515" y="508">a fresh challenge</text>
<line class="wa-front" x1="636" y1="522" x2="394" y2="522" marker-end="url(#wa-m-front)"/>
<circle class="wa-badge wa-b-front" cx="650" cy="522" r="12"/><text class="wa-bt" x="650" y="526.5">A1</text>
</g>
<g class="wa-g wa-g6">
<text class="wa-main" x="245" y="562">sign this challenge</text>
<text class="wa-dim" x="245" y="578">for the origin's RP ID</text>
<line class="wa-front" x1="366" y1="592" x2="124" y2="592" marker-end="url(#wa-m-front)"/>
<circle class="wa-badge wa-b-front" cx="380" cy="592" r="12"/><text class="wa-bt" x="380" y="596.5">A2</text>
<rect class="wa-note-bad" x="273" y="610" width="214" height="65" rx="8"/>
<text class="wa-nt" x="380" y="631">a page on another domain can</text>
<text class="wa-nt" x="380" y="648">neither request your RP ID</text>
<text class="wa-nt" x="380" y="665">nor get a signature for it</text>
</g>
<g class="wa-g wa-g7">
<text class="wa-main" x="245" y="709">authenticatorData + signature</text>
<line class="wa-front" x1="124" y1="723" x2="366" y2="723" marker-end="url(#wa-m-front)"/>
<circle class="wa-badge wa-b-front" cx="110" cy="723" r="12"/><text class="wa-bt" x="110" y="727.5">A3</text>
</g>
<g class="wa-g wa-g8">
<text class="wa-main" x="515" y="763">sent on to the RP</text>
<text class="wa-dim" x="515" y="779">clientDataJSON, authenticatorData,</text>
<text class="wa-dim" x="515" y="795">signature</text>
<line class="wa-front" x1="394" y1="809" x2="636" y2="809" marker-end="url(#wa-m-front)"/>
<circle class="wa-badge wa-b-front" cx="380" cy="809" r="12"/><text class="wa-bt" x="380" y="813.5">A4</text>
</g>
<g class="wa-g wa-g9">
<rect class="wa-note-good" x="483" y="843" width="267" height="82" rx="8"/>
<text class="wa-nt" x="616" y="864">finds the credential; checks type</text>
<text class="wa-nt" x="616" y="881">webauthn.get, challenge, origin,</text>
<text class="wa-nt" x="616" y="898">rpIdHash, UP flag; verifies the</text>
<text class="wa-nt" x="616" y="915">signature with the stored public key</text>
</g>
<circle class="wa-pk wa-p0" cx="630" cy="138" r="5.5"/>
<circle class="wa-pk wa-p1" cx="360" cy="208" r="5.5"/>
<circle class="wa-pk wa-p2" cx="130" cy="305" r="5.5"/>
<circle class="wa-pk wa-p3" cx="400" cy="375" r="5.5"/>
<circle class="wa-pk wa-p5" cx="630" cy="522" r="5.5"/>
<circle class="wa-pk wa-p6" cx="360" cy="592" r="5.5"/>
<circle class="wa-pk wa-p7" cx="130" cy="723" r="5.5"/>
<circle class="wa-pk wa-p8" cx="400" cy="809" r="5.5"/>
<line class="wa-front" x1="40" y1="999" x2="70" y2="999"/>
<text class="wa-dim" x="78" y="1003" style="text-anchor:start">message in the ceremony</text>
<rect class="wa-note-bad" x="259" y="991" width="22" height="16" rx="4"/>
<text class="wa-dim" x="289" y="1003" style="text-anchor:start">failure mode</text>
<rect class="wa-note-good" x="399" y="991" width="22" height="16" rx="4"/>
<text class="wa-dim" x="429" y="1003" style="text-anchor:start">what the RP checks</text>
</svg>
</div>
</div>
<!-- /diagram:webauthn-ceremony -->

R1 to R4 register a credential; A1 to A4 authenticate with it. The numbers match the text below, and the note marked as a failure shows what a page on another domain cannot do. In this lesson a credential is a WebAuthn public-key credential, the key pair and its credential ID; the spec's glossary lists passkey as a term for a discoverable one. A session cookie is a different kind of credential, a bearer one, covered at the end.

**Registration (R1 to R4).** R1: the relying party (RP) generates a challenge, which the spec says should be at least 16 bytes, and sends it with its RP ID. R2: the browser checks that the RP ID is the page's domain or a registrable domain suffix of it, then asks the authenticator to create a key pair; the user approves with a gesture. R3: the authenticator returns the public key and credential ID. R4: the RP checks that the client data type is webauthn.create, the challenge matches, the origin is expected and rpIdHash is the SHA-256 of its RP ID, then stores the public key and credential ID.

**Authentication (A1 to A4).** A1: the RP sends a fresh challenge. A2: the browser asks the authenticator to sign for the origin's RP ID. A3: the authenticator returns authenticatorData and a signature over authenticatorData and the hash of clientDataJSON. A4: the browser sends clientDataJSON, authenticatorData and the signature; the RP finds the credential, checks type webauthn.get and the challenge and origin in clientDataJSON, then rpIdHash and the user presence (UP) flag in authenticatorData, and verifies the signature with the stored public key.

<!-- diagram:rp-id-scope -->
<div style="position:relative;margin:20px 0">
<input type="checkbox" id="l06c-pause" class="l06c-cb" /><label for="l06c-pause" class="l06c-btn"><span class="l06c-off">Pause animation</span><span class="l06c-on">Play animation</span></label>
<div class="l06c-box" style="overflow-x:auto">
<svg class="l06c-flow" viewBox="0 0 760 266" role="img" aria-labelledby="l06c-t l06c-d" style="width:100%;min-width:640px;max-width:800px;height:auto;display:block;margin:0 auto">
<title id="l06c-t">Which RP IDs a page can use</title>
<desc id="l06c-d">Nested domains for a page at the origin https://login.example.com. The outermost box is com, which is not a valid RP ID. Inside it, example.com is a valid RP ID. Inside that, login.example.com, the page's own domain, is a valid RP ID. Inside that, m.login.example.com is not a valid RP ID. The valid RP IDs are login.example.com and example.com, not m.login.example.com and not com. The diagram highlights each part in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
<style>
.l06c-box{fill:var(--panel);stroke:var(--border-strong);stroke-width:1.5}
.l06c-hot{fill:var(--panel);stroke:var(--accent);stroke-width:2.5}
.l06c-ttl{fill:var(--text);font:600 15px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l06c-sub{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l06c-life{stroke:var(--border-strong);stroke-width:1.5;stroke-dasharray:4 5}
.l06c-front{stroke:var(--accent);stroke-width:2;fill:none}
.l06c-back{stroke:var(--muted);stroke-width:2;stroke-dasharray:7 5;fill:none}
.l06c-bad{stroke:var(--bad);stroke-width:2;fill:none}
.l06c-main{fill:var(--text);font:600 13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l06c-badt{fill:var(--bad-text)}
.l06c-dim{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l06c-badge{fill:var(--accent)}
.l06c-b-back{fill:var(--muted)}
.l06c-b-bad{fill:var(--bad)}
.l06c-b-good{fill:var(--good)}
.l06c-bt{fill:var(--on-accent);font:700 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l06c-note{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l06c-note-good{fill:var(--good-bg);stroke:var(--good);stroke-width:1.5}
.l06c-note-bad{fill:var(--bad-bg);stroke:var(--bad);stroke-width:1.5}
.l06c-nt{fill:var(--body);font:12.5px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l06c-nest{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l06c-row{fill:var(--raised);stroke:var(--border-strong);stroke-width:1}
.l06c-ttlL{fill:var(--text);font:600 14px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l06c-subL{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l06c-dimL{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l06c-dimR{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:end}
.l06c-conn{stroke:var(--accent);stroke-width:1.5;fill:none}
.l06c-edge{stroke:var(--border-strong);stroke-width:1.75;fill:none}
.l06c-hl{fill:none;stroke:var(--accent);stroke-width:3}
.l06c-hle{stroke:var(--accent);stroke-width:3;fill:none}
.l06c-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:14s;animation-timing-function:linear;animation-iteration-count:infinite}
.l06c-pk.l06c-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.l06c-pk.l06c-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.l06c-g{opacity:.45;animation-duration:14s;animation-timing-function:linear;animation-iteration-count:infinite}
.l06c-h{opacity:0;animation-duration:14s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.l06c-flow:hover .l06c-g,svg.l06c-flow:hover .l06c-pk,svg.l06c-flow:hover .l06c-h{animation-play-state:paused}
.l06c-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.l06c-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.l06c-btn:hover{background:var(--hover)}
.l06c-cb:focus-visible + .l06c-btn{outline:2px solid var(--accent);outline-offset:2px}
.l06c-cb:checked + .l06c-btn .l06c-off,.l06c-cb:not(:checked) + .l06c-btn .l06c-on{display:none}
.l06c-cb:checked ~ .l06c-box .l06c-g,.l06c-cb:checked ~ .l06c-box .l06c-pk,.l06c-cb:checked ~ .l06c-box .l06c-h{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.l06c-g{animation:none;opacity:1}.l06c-pk{animation:none;display:none}.l06c-h{animation:none;opacity:0}.l06c-btn{display:none}}
@keyframes l06c-g0{0%{opacity:1}25%{opacity:1}25.01%,100%{opacity:.45}}
@keyframes l06c-h0{0%{opacity:1}25%{opacity:1}25.01%,100%{opacity:0}}
.l06c-g0{animation-name:l06c-g0}.l06c-h0{animation-name:l06c-h0}
@keyframes l06c-g1{0%,24.99%{opacity:.45}25%{opacity:1}50%{opacity:1}50.01%,100%{opacity:.45}}
@keyframes l06c-h1{0%,24.99%{opacity:0}25%{opacity:1}50%{opacity:1}50.01%,100%{opacity:0}}
.l06c-g1{animation-name:l06c-g1}.l06c-h1{animation-name:l06c-h1}
@keyframes l06c-g2{0%,49.99%{opacity:.45}50%{opacity:1}75%{opacity:1}75.01%,100%{opacity:.45}}
@keyframes l06c-h2{0%,49.99%{opacity:0}50%{opacity:1}75%{opacity:1}75.01%,100%{opacity:0}}
.l06c-g2{animation-name:l06c-g2}.l06c-h2{animation-name:l06c-h2}
@keyframes l06c-g3{0%,74.99%{opacity:.45}75%{opacity:1}100%{opacity:1}100.01%,100%{opacity:.45}}
@keyframes l06c-h3{0%,74.99%{opacity:0}75%{opacity:1}100%{opacity:1}100.01%,100%{opacity:0}}
.l06c-g3{animation-name:l06c-g3}.l06c-h3{animation-name:l06c-h3}
</style>
<defs>
<marker id="l06c-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="l06c-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="l06c-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<rect class="l06c-box" x="14" y="16" width="440" height="192" rx="9"/><text class="l06c-ttlL" x="28" y="37">com</text>
<rect class="l06c-nest" x="26" y="48" width="416" height="148" rx="9"/><text class="l06c-ttlL" x="40" y="69">example.com</text><text class="l06c-subL" x="40" y="86">a registrable domain suffix of the page's domain</text>
<rect class="l06c-nest" x="38" y="94" width="392" height="90" rx="9"/><text class="l06c-ttlL" x="52" y="115">login.example.com</text><text class="l06c-subL" x="52" y="132">the page's own domain (origin https://login.example.com)</text>
<rect class="l06c-nest" x="50" y="140" width="368" height="32" rx="9"/><text class="l06c-ttlL" x="64" y="161">m.login.example.com</text>
<g class="l06c-g l06c-g0">
<path class="l06c-conn" d="M454,33 L462,33 L462,33 L470,33" marker-end="url(#l06c-m-front)"/>
<rect class="l06c-note-bad" x="484" y="18" width="262" height="31" rx="8"/>
<text class="l06c-nt" x="615" y="38">Not a valid RP ID</text>
<circle class="l06c-badge l06c-b-bad" cx="484" cy="33" r="12"/><text class="l06c-bt" x="484" y="37.5">1</text>
</g>
<g class="l06c-g l06c-g1">
<path class="l06c-conn" d="M442,65 L466,65 L466,74 L470,74" marker-end="url(#l06c-m-front)"/>
<rect class="l06c-note-good" x="484" y="58" width="262" height="31" rx="8"/>
<text class="l06c-nt" x="615" y="80">Valid RP ID</text>
<circle class="l06c-badge l06c-b-good" cx="484" cy="74" r="12"/><text class="l06c-bt" x="484" y="78.5">2</text>
</g>
<g class="l06c-g l06c-g2">
<path class="l06c-conn" d="M430,111 L470,111 L470,115 L470,115" marker-end="url(#l06c-m-front)"/>
<rect class="l06c-note-good" x="484" y="100" width="262" height="31" rx="8"/>
<text class="l06c-nt" x="615" y="120">Valid RP ID</text>
<circle class="l06c-badge l06c-b-good" cx="484" cy="115" r="12"/><text class="l06c-bt" x="484" y="119.5">3</text>
</g>
<g class="l06c-g l06c-g3">
<path class="l06c-conn" d="M418,157 L474,157 L474,157 L470,157" marker-end="url(#l06c-m-front)"/>
<rect class="l06c-note-bad" x="484" y="142" width="262" height="31" rx="8"/>
<text class="l06c-nt" x="615" y="162">Not a valid RP ID</text>
<circle class="l06c-badge l06c-b-bad" cx="484" cy="157" r="12"/><text class="l06c-bt" x="484" y="161.5">4</text>
</g>
<g class="l06c-h l06c-h0">
<rect class="l06c-hl" x="14" y="16" width="440" height="192" rx="9"/>
</g>
<g class="l06c-h l06c-h1">
<rect class="l06c-hl" x="26" y="48" width="416" height="148" rx="9"/>
</g>
<g class="l06c-h l06c-h2">
<rect class="l06c-hl" x="38" y="94" width="392" height="90" rx="9"/>
</g>
<g class="l06c-h l06c-h3">
<rect class="l06c-hl" x="50" y="140" width="368" height="32" rx="9"/>
</g>
<rect class="l06c-note-good" x="40" y="234" width="22" height="16" rx="4"/>
<text class="l06c-dim" x="70" y="246" style="text-anchor:start">valid RP ID</text>
<rect class="l06c-note-bad" x="174" y="234" width="22" height="16" rx="4"/>
<text class="l06c-dim" x="204" y="246" style="text-anchor:start">not valid</text>
</svg>
</div>
</div>
<!-- /diagram:rp-id-scope -->

Read the boxes from outside in (callouts 1 to 4): for a page at https://login.example.com, only the page's own domain and the domain suffix example.com are valid RP IDs.

**RP ID scope.** For an origin of https://login.example.com the valid RP IDs are login.example.com and example.com, not m.login.example.com and not com. A phishing page on another domain can neither request your RP ID nor get a signature for it, which is the phishing resistance. The one opt-in exception is related origin requests (WebAuthn Level 3 section 5.11): an RP can list other origins at /.well-known/webauthn that may use its RP ID, so list only origins you control.

**Synced and device-bound.** The authenticator data carries a backup-eligible (BE) flag, fixed for the life of the credential, and a backup-state (BS) flag. BE 0 means a single-device credential; BE 1 means a multi-device (synced) credential. For single-device credentials the spec says the RP should ensure extra authenticators or a recovery process exist.

**What passkeys change for IT.**

- **Recovery.** A device-bound credential is lost with its device, so enrol a second authenticator or keep a recovery process; a synced one survives, but depends on the owner's cloud account.
- **Enrolment.** In self-service enrolment the first passkey is registered by someone who is already signed in some other way, so that earlier sign-in sets the real assurance. A preconfigured key, as in the next bullet, moves that trust to how you deliver it.
- **Shared devices.** The WebAuthn spec's employer example mails a security key preconfigured with a device-bound passkey and sends the temporary PIN out of band. As a rule of thumb (not from a source), a synced passkey saved in a shared computer's own sign-in account is available to everyone who uses that account.

**Attestation.** The default conveyance preference is none, so you receive no verifiable statement about the authenticator model. The enterprise value is intended for controlled deployments that tie registrations to specific authenticators. Entra passkey profiles let you enforce attestation and choose device-bound or synced types per group.

## Sessions, step-up and what MFA does not stop

A session secret, usually a cookie, proves a past authentication. NIST wants it to inherit the assurance of the authentication that created it, never higher; a higher level needs step-up reauthentication. In Okta the global session policy controls how long a session is valid (Maximum Okta global session lifetime and Maximum Okta global session idle time) while the app sign-in policy controls reauthentication frequency. In Entra a strength plus a sign-in frequency can be satisfied at different times: a 24-hour-old passkey sign-in and a fresh Windows Hello unlock together meet a policy that wanted both at once.

Cookie attributes (MDN): Secure sends only over HTTPS. HttpOnly forbids JavaScript reading the cookie, but the browser still sends it on script-initiated requests. SameSite is Strict, Lax or None, and None requires Secure. A cookie with no Max-Age or Expires is a session cookie. A name starting with `__Host-` must be Secure, have no Domain attribute (so the cookie is host-only) and use Path=/. NIST adds that cookies should be HttpOnly and that Secure is mandatory, and advises SameSite Lax or Strict on the cookie that keeps the authenticated session; a Lax or Strict cookie is not sent on the cross-site POST that carries a SAML response to the ACS (lesson 2). Idle timeout ends a session after inactivity; absolute timeout ends it a fixed time after authentication.

<!-- diagram:session-cookie -->
<div style="position:relative;margin:20px 0">
<input type="checkbox" id="l06b-pause" class="l06b-cb" /><label for="l06b-pause" class="l06b-btn"><span class="l06b-off">Pause animation</span><span class="l06b-on">Play animation</span></label>
<div class="l06b-box" style="overflow-x:auto">
<svg class="l06b-flow" viewBox="0 0 760 703" role="img" aria-labelledby="l06b-t l06b-d" style="width:100%;min-width:640px;max-width:800px;height:auto;display:block;margin:0 auto">
<title id="l06b-t">A stolen session cookie skips MFA</title>
<desc id="l06b-d">Three parties: the user's browser, the real site, and an attacker. The user authenticates and the site returns a session cookie, a session secret that proves a past authentication. NIST wants a session to inherit the assurance of the authentication that created it, never higher. An AitM relay sees the cookie the real site returns, and malware can copy it from the browser. The attacker presents the stolen cookie, a bearer credential, and MFA does not help after that. Short lifetimes, ending sessions, and phishing-resistant sign-in help. The diagram highlights each step in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
<style>
.l06b-box{fill:var(--panel);stroke:var(--border-strong);stroke-width:1.5}
.l06b-hot{fill:var(--panel);stroke:var(--accent);stroke-width:2.5}
.l06b-ttl{fill:var(--text);font:600 15px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l06b-sub{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l06b-life{stroke:var(--border-strong);stroke-width:1.5;stroke-dasharray:4 5}
.l06b-front{stroke:var(--accent);stroke-width:2;fill:none}
.l06b-back{stroke:var(--muted);stroke-width:2;stroke-dasharray:7 5;fill:none}
.l06b-bad{stroke:var(--bad);stroke-width:2;fill:none}
.l06b-main{fill:var(--text);font:600 13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l06b-badt{fill:var(--bad-text)}
.l06b-dim{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l06b-badge{fill:var(--accent)}
.l06b-b-back{fill:var(--muted)}
.l06b-b-bad{fill:var(--bad)}
.l06b-b-good{fill:var(--good)}
.l06b-bt{fill:var(--on-accent);font:700 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l06b-note{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l06b-note-good{fill:var(--good-bg);stroke:var(--good);stroke-width:1.5}
.l06b-note-bad{fill:var(--bad-bg);stroke:var(--bad);stroke-width:1.5}
.l06b-nt{fill:var(--body);font:12.5px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l06b-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:22s;animation-timing-function:linear;animation-iteration-count:infinite}
.l06b-pk.l06b-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.l06b-pk.l06b-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.l06b-g{opacity:.45;animation-duration:22s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.l06b-flow:hover .l06b-g,svg.l06b-flow:hover .l06b-pk{animation-play-state:paused}
.l06b-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.l06b-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.l06b-btn:hover{background:var(--hover)}
.l06b-cb:focus-visible + .l06b-btn{outline:2px solid var(--accent);outline-offset:2px}
.l06b-cb:checked + .l06b-btn .l06b-off,.l06b-cb:not(:checked) + .l06b-btn .l06b-on{display:none}
.l06b-cb:checked ~ .l06b-box .l06b-g,.l06b-cb:checked ~ .l06b-box .l06b-pk{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.l06b-g{animation:none;opacity:1}.l06b-pk{animation:none;display:none}.l06b-btn{display:none}}
@keyframes l06b-g0{0%{opacity:1}14.286%{opacity:1}14.296%,100%{opacity:.45}}
@keyframes l06b-p0{0%,-0.01%{opacity:0;transform:translateX(0)}0%{opacity:1;transform:translateX(0)}14.286%{opacity:1;transform:translateX(236px)}14.296%,100%{opacity:0;transform:translateX(236px)}}
.l06b-g0{animation-name:l06b-g0}.l06b-p0{animation-name:l06b-p0}
@keyframes l06b-g1{0%,14.276%{opacity:.45}14.286%{opacity:1}28.571%{opacity:1}28.581%,100%{opacity:.45}}
@keyframes l06b-p1{0%,14.276%{opacity:0;transform:translateX(0)}14.286%{opacity:1;transform:translateX(0)}28.571%{opacity:1;transform:translateX(-236px)}28.581%,100%{opacity:0;transform:translateX(-236px)}}
.l06b-g1{animation-name:l06b-g1}.l06b-p1{animation-name:l06b-p1}
@keyframes l06b-g2{0%,28.561%{opacity:.45}28.571%{opacity:1}42.857%{opacity:1}42.867%,100%{opacity:.45}}
.l06b-g2{animation-name:l06b-g2}
@keyframes l06b-g3{0%,42.847%{opacity:.45}42.857%{opacity:1}57.143%{opacity:1}57.153%,100%{opacity:.45}}
.l06b-g3{animation-name:l06b-g3}
@keyframes l06b-g4{0%,57.133%{opacity:.45}57.143%{opacity:1}71.429%{opacity:1}71.439%,100%{opacity:.45}}
@keyframes l06b-p4{0%,57.133%{opacity:0;transform:translateX(0)}57.143%{opacity:1;transform:translateX(0)}71.429%{opacity:1;transform:translateX(-236px)}71.439%,100%{opacity:0;transform:translateX(-236px)}}
.l06b-g4{animation-name:l06b-g4}.l06b-p4{animation-name:l06b-p4}
@keyframes l06b-g5{0%,71.419%{opacity:.45}71.429%{opacity:1}85.714%{opacity:1}85.724%,100%{opacity:.45}}
.l06b-g5{animation-name:l06b-g5}
@keyframes l06b-g6{0%,85.704%{opacity:.45}85.714%{opacity:1}100%{opacity:1}100.01%,100%{opacity:.45}}
.l06b-g6{animation-name:l06b-g6}
</style>
<defs>
<marker id="l06b-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="l06b-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="l06b-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<line class="l06b-life" x1="110" y1="72" x2="110" y2="651"/>
<line class="l06b-life" x1="380" y1="72" x2="380" y2="651"/>
<line class="l06b-life" x1="650" y1="72" x2="650" y2="651"/>
<rect class="l06b-box" x="20" y="10" width="180" height="62" rx="10"/><text class="l06b-ttl" x="110" y="36">User's browser</text><text class="l06b-sub" x="110" y="56">holds the cookie</text>
<rect class="l06b-hot" x="290" y="10" width="180" height="62" rx="10"/><text class="l06b-ttl" x="380" y="36">Real site</text><text class="l06b-sub" x="380" y="56">returns the cookie</text>
<rect class="l06b-box" x="560" y="10" width="180" height="62" rx="10"/><text class="l06b-ttl" x="650" y="36">Attacker</text><text class="l06b-sub" x="650" y="56">relay or malware</text>
<g class="l06b-g l06b-g0">
<text class="l06b-main" x="245" y="108">user authenticates</text>
<text class="l06b-dim" x="245" y="124">MFA is satisfied here</text>
<line class="l06b-front" x1="124" y1="138" x2="366" y2="138" marker-end="url(#l06b-m-front)"/>
<circle class="l06b-badge l06b-b-front" cx="110" cy="138" r="12"/><text class="l06b-bt" x="110" y="142.5">1</text>
</g>
<g class="l06b-g l06b-g1">
<text class="l06b-main" x="245" y="178">session cookie</text>
<text class="l06b-dim" x="245" y="194">proves a past authentication</text>
<line class="l06b-front" x1="366" y1="208" x2="124" y2="208" marker-end="url(#l06b-m-front)"/>
<circle class="l06b-badge l06b-b-front" cx="380" cy="208" r="12"/><text class="l06b-bt" x="380" y="212.5">2</text>
</g>
<g class="l06b-g l06b-g2">
<rect class="l06b-note-good" x="263" y="242" width="234" height="65" rx="8"/>
<text class="l06b-nt" x="380" y="263">NIST wants it to inherit the</text>
<text class="l06b-nt" x="380" y="280">assurance of the authentication</text>
<text class="l06b-nt" x="380" y="297">that created it, never higher</text>
</g>
<g class="l06b-g l06b-g3">
<rect class="l06b-note-bad" x="522" y="335" width="228" height="48" rx="8"/>
<text class="l06b-nt" x="636" y="356">an AitM relay sees the cookie;</text>
<text class="l06b-nt" x="636" y="373">malware can copy it</text>
</g>
<g class="l06b-g l06b-g4">
<text class="l06b-main l06b-badt" x="515" y="417">presents the stolen cookie</text>
<text class="l06b-dim" x="515" y="433">a bearer credential</text>
<line class="l06b-bad" x1="636" y1="447" x2="394" y2="447" marker-end="url(#l06b-m-bad)"/>
<circle class="l06b-badge l06b-b-bad" cx="650" cy="447" r="12"/><text class="l06b-bt" x="650" y="451.5">3</text>
</g>
<g class="l06b-g l06b-g5">
<rect class="l06b-note-bad" x="273" y="481" width="214" height="31" rx="8"/>
<text class="l06b-nt" x="380" y="502">MFA does not help after that</text>
</g>
<g class="l06b-g l06b-g6">
<rect class="l06b-note-good" x="10" y="540" width="214" height="65" rx="8"/>
<text class="l06b-nt" x="117" y="561">what helps: short lifetimes,</text>
<text class="l06b-nt" x="117" y="578">ending sessions, phishing-</text>
<text class="l06b-nt" x="117" y="595">resistant sign-in</text>
</g>
<circle class="l06b-pk l06b-p0" cx="130" cy="138" r="5.5"/>
<circle class="l06b-pk l06b-p1" cx="360" cy="208" r="5.5"/>
<circle class="l06b-pk l06b-p4 l06b-pkbad" cx="630" cy="447" r="5.5"/>
<line class="l06b-front" x1="40" y1="679" x2="70" y2="679"/>
<text class="l06b-dim" x="78" y="683" style="text-anchor:start">the user's session</text>
<line class="l06b-bad" x1="227" y1="679" x2="257" y2="679"/>
<text class="l06b-dim" x="265" y="683" style="text-anchor:start">the attacker</text>
<rect class="l06b-note-good" x="375" y="671" width="22" height="16" rx="4"/>
<text class="l06b-dim" x="405" y="683" style="text-anchor:start">what holds or helps</text>
</svg>
</div>
</div>
<!-- /diagram:session-cookie -->

Badges 1 to 3 number this diagram's own hops. The cookie is issued after MFA, so whoever presents a copy skips it.

> A stolen session cookie is a bearer credential (NIST calls session secrets used this way bearer tokens): MFA was already satisfied when it was issued. An AitM relay sees the cookie the real site returns, and malware can copy it from the browser. MFA does not help after that; short lifetimes, ending sessions, and phishing-resistant sign-in (which removes the relay path) do. The IdP session and each app session are separate, so ending one does not end the other.

## Four failure modes

- **SMS fallback downgrades the policy.** An attacker picks the weakest method your rules allow. Entra's strength does not restrict initial authentication, and Okta's guide has you move the phishing-resistant rule to the top of the priority list. Remove SMS from enrolment for those groups and check which method each sign-in used (in Identity Engine orgs the user.authentication.auth_via_mfa events record each primary and second-factor verification).
- **Recovery is the weakest link.** A reset that accepts SMS or email undoes a passkey rollout. Okta can require phishing-resistant authenticators for unlock and password reset in two steps: set the Access control condition in the password policy rule's Recovery authenticators section to Authentication policy, then add a rule to the Okta account management policy that requires a phishing-resistant possession factor. The password policy setting only hands recovery to the authentication policy; the requirement lives in the account management rule.
- **Enrolment race.** If first enrolment is protected only by a password or temporary password, whoever completes it first owns the factor. NIST requires a notification through a channel independent of the enrolment, so a rogue enrolment can be noticed.
- **Synced passkey in a personal account on a corporate device.** The credential syncs to the owner's personal cloud account, outside your control. The BE flag shows it only if you can trust the flag: with the default none attestation the statement is empty and nothing signs the registration's authenticator data, and Entra says that with Enforce attestation set to No it cannot guarantee any attribute of a passkey, including whether it is synced or device-bound (it also says synced passkeys do not support attestation). Entra's own example profile for IT admins uses device-bound passkeys with attestation enforced. An Okta equivalent was not verified.

## Lab: compute a TOTP code

Save as `totp.py`. The secret is a widely used sample secret, not a real credential.

```python
import base64, hashlib, hmac, struct, sys
def hotp(key, counter, digits=6):
    mac = hmac.new(key, struct.pack(">Q", counter), hashlib.sha1).digest()
    off = mac[-1] & 0x0F
    return str((int.from_bytes(mac[off:off+4], "big") & 0x7FFFFFFF) % 10**digits).zfill(digits)
def totp(key, now, step=30, digits=6):
    return hotp(key, int(now // step), digits)
assert totp(b"12345678901234567890", 59, digits=8) == "94287082"   # RFC 6238 Appendix B vector
key = base64.b32decode("JBSWY3DPEHPK3PXP")                          # widely used sample secret
now = float(sys.argv[1])
for label, t in (("previous", now - 30), ("current ", now), ("next    ", now + 30)):
    print(label, "T=%d" % (t // 30), "code=" + totp(key, t))
```

I ran this code as written with Python 3.14.6 and got:

```
$ python3 totp.py 1750000019
previous T=58333332 code=036800
current  T=58333333 code=509970
next     T=58333334 code=629898
$ python3 totp.py 1750000020
previous T=58333333 code=509970
current  T=58333334 code=629898
next     T=58333335 code=217841
```

One second later the step changed, so 629898 became the current code and 509970 the previous one. Your task: change the secret by one character and explain why every code changes, then explain what a relay would do with 509970 typed at 1750000019. Lesson 7 covers authorization and the lifecycle.
