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

**Okta.** Okta lists Passkey (FIDO2 WebAuthn) and Okta FastPass as its phishing-resistant authenticators. You enforce them in an app sign-in policy rule with Possession factor constraints are: Phishing resistant. FastPass verifies that the request does not come from a malicious site, and a blocked attempt is logged in the System Log with a message such as Okta FastPass declined phishing attempt. Known limits: apps whose WebView implementation Okta does not support fail with an Access denied message when the policy requires phishing resistance; on macOS you need an SSO extension for Safari; and DNS Rebind Protection on a router can stop Okta Verify connecting to browsers or native apps on the device, which fails the check there too.

**Entra.** The built-in Phishing-resistant MFA authentication strength allows Windows Hello for Business or a platform credential, a FIDO2 security key, and certificate-based authentication (multifactor). Microsoft Authenticator phone sign-in satisfies the MFA and Passwordless MFA strengths but not this one. Conditional Access is evaluated only after initial authentication, so a user can still type a password first and must then use a phishing-resistant method.

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

R1 to R4 register a credential; A1 to A4 authenticate with it. The numbers match the text below. In this lesson a credential is a WebAuthn public-key credential, the key pair and its credential ID; the spec's glossary lists passkey as a term for a discoverable one. A session cookie is a different kind of credential, a bearer one, covered at the end.

**Registration (R1 to R4).** R1: the relying party (RP) generates a challenge, which the spec says should be at least 16 bytes, and sends it with its RP ID. R2: the browser checks that the RP ID is the page's domain or a registrable domain suffix of it, then asks the authenticator to create a key pair; the user approves with a gesture. R3: the authenticator returns the public key and credential ID. R4: the RP checks that the client data type is webauthn.create, the challenge matches, the origin is expected and rpIdHash is the SHA-256 of its RP ID, then stores the public key and credential ID.

**Authentication (A1 to A4).** A1: the RP sends a fresh challenge. A2: the browser asks the authenticator to sign for the origin's RP ID. A3: the authenticator returns authenticatorData and a signature over authenticatorData and the hash of clientDataJSON. A4: the browser sends clientDataJSON, authenticatorData and the signature; the RP finds the credential, checks type webauthn.get and the challenge and origin in clientDataJSON, then rpIdHash and the user presence (UP) flag in authenticatorData, and verifies the signature with the stored public key.

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
