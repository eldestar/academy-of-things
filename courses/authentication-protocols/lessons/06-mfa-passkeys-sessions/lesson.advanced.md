# MFA, passkeys and sessions

Facts checked 2026-10-06 against the W3C WebAuthn Level 3 Recommendation (25 August 2026), NIST SP 800-63-4 (final, 31 July 2025; this lesson cites its 63B volume), RFC 6238, the W3C Device Bound Session Credentials Editor's Draft (8 September 2026), a Google Workspace Updates post (28 May 2026), MDN, and Okta and Microsoft Entra documentation. You are designing or reviewing the relying-party side. This lesson is about what a verifier must check, what the standards leave to you, and which attacks survive a phishing-resistant rollout.

## Assurance levels and what a policy can express

NIST SP 800-63B defines three authentication assurance levels (AAL). Phishing resistance is defined as preventing disclosure of authentication secrets and valid authenticator outputs to an impostor verifier without relying on the claimant's vigilance. Two methods qualify: channel binding (NIST rates it more secure, because it does not depend on verifier certificates) and verifier name binding, of which WebAuthn is the named example.

| AAL | Authenticators | Phishing resistance | Reauthentication limits |
| --- | --- | --- | --- |
| AAL1 | single or multi-factor | not required | overall SHOULD be at most 30 days; inactivity timeout MAY be applied |
| AAL2 | two distinct factors | the verifier SHALL offer at least one phishing-resistant option | overall SHOULD be at most 24 hours; inactivity SHOULD be at most 1 hour |
| AAL3 | cryptographic, non-exportable key | required | overall SHALL be at most 12 hours; inactivity SHOULD be at most 15 minutes |

At AAL2, after an inactivity timeout and before the overall timeout, the verifier MAY accept a password or biometric plus the session secret; at AAL3 reauthentication must repeat full AAL3 authentication. **Syncable authenticators SHALL NOT be used at AAL3**, because they require an exportable private key. Appendix B of NIST SP 800-63B adds that central revocation of syncable or WebAuthn credentials is challenging, since keys are specific to each relying party, and suggests managing authenticators in a central identity account and using SSO and federation to limit how many RP-specific keys exist.

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

R1 to R4 register a credential; A1 to A4 authenticate with it. The numbers match the text below. Here a credential is a WebAuthn public-key credential (the spec's glossary lists passkey as a term for a discoverable one); a session cookie is a bearer credential, whose holder is accepted without proving anything else (NIST calls session secrets used this way bearer tokens).

**Registration (R1 to R4).** R1: the RP creates options with a challenge (at least 16 bytes recommended) and an RP ID. R2: the client rejects an RP ID that is not the origin's effective domain or a registrable domain suffix of it, and asks the authenticator to create a key pair after a gesture. R3: the authenticator returns the credential ID, public key and attestation. R4: the RP verifies, in order, client data type webauthn.create, the challenge, an expected origin, rpIdHash equal to the SHA-256 of its RP ID, the UP flag (unless the ceremony used conditional mediation), and UV if it requires it, the BE and BS consistency rule, the algorithm against the requested list, and the attestation per its policy.

**Authentication (A1 to A4).** A1: the RP sends a fresh challenge. A2: the client asks for a signature scoped to the origin's RP ID. A3: the authenticator returns authenticatorData and a signature. A4: the browser sends clientDataJSON, authenticatorData and the signature, and the RP checks that the credential ID is in allowCredentials if one was sent, identifies the user, checks type webauthn.get, challenge, origin and rpIdHash, requires UP, requires UV if configured, then verifies the signature over authenticatorData concatenated with the SHA-256 hash of clientDataJSON, using the stored public key.

**Origin validation is a separate check from the RP ID.** An RP ID may be a registrable domain suffix, so sub.example.org may legitimately request RP ID example.org. The RP MUST validate origin and MUST NOT accept unexpected values. By default it SHOULD NOT allow a subdomain origin. The spec's example is user content hosted on usercontent.example.org, which could exercise credentials scoped to example.org and relay valid assertions. If you do allow subdomains, you MUST NOT serve untrusted code on any of them. Related origin requests (section 5.11) are the opt-in exception to RP ID scoping: the RP lists other origins at /.well-known/webauthn so they may use its RP ID, so list only origins you control.

## Credential records, discoverability and sync flags

The credential ID is at most 1023 bytes and the RP should reject a registration whose ID already exists. The reason: attestation types other than self attestation carry no proof of private-key possession, so an attacker holding a victim's credential ID and public key could register them as their own, and with discoverable credentials the victim could end up signed in to the attacker's account. A **discoverable credential** (formerly resident key) is usable when the RP supplies no credential IDs, which enables username-less sign-in; then the response must carry a userHandle that identifies the account. The recommended record holds type, id, publicKey, signCount, transports, uvInitialized, backupEligible and backupState.

- **signCount.** The check runs only if the authenticator value or the stored value is nonzero. A new value less than or equal to the stored one is a signal, not proof, of a cloned authenticator: it can also mean a malfunction or assertions processed out of order. Whether to fail, or to update the stored value, is RP policy.
- **uvInitialized.** Until a credential has once been seen with UV set, the RP must not treat UV as an authentication factor, because no trust in the user verification exists yet.
- **BE and BS.** Both are flags in the authenticator data, present at registration and in every assertion. BE is fixed at creation. (0, 0) is single-device; (0, 1) is not allowed; (1, 0) is multi-device not backed up; (1, 1) is multi-device backed up. If BS goes from 1 to 0 the RP should guide the user through validating their other factors or adding a credential.

**Choosing between the two types.** The standards give you the decision inputs, not the decision.

| | Synced (BE 1) | Device-bound (BE 0) |
| --- | --- | --- |
| NIST AAL3 | never allowed | possible if the key is non-exportable and phishing-resistant |
| Loss of one device | credential survives in the sync service | gone; the spec says the RP should ensure extra authenticators or recovery |
| Who controls copies | the sync provider account | nobody; the key stays in one device or security key |
| Policy hook | BE and BS flags, plus Entra's Synced or Device-bound passkey type | the same flags; Entra attestation can restrict models |

## Attestation: what you can learn and what it costs

The WebAuthn Level 3 formats are packed, tpm, android-key, android-safetynet (marked deprecated), fido-u2f, none, apple and compound. Attestation types include Basic (an attestation key shared per model batch), Self and AttCA. The conveyance preference is none (the default), indirect, direct or enterprise. With none, the client replaces any non-self attestation with a None statement. A statement is made once, at registration, and describes the authenticator (for example its model); it does not change how the credential is stored afterwards. Enterprise attestation may identify individual authenticators and is meant for controlled deployments; the client must not provide it unless configuration permits it for that RP ID.

To trust a statement you need acceptable trust anchors from policy or a source such as the FIDO Metadata Service, looked up by AAGUID. Attestation does not authenticate the registration channel: a man-in-the-middle can replace the whole credential object, though the spec calls that potentially detectable, because later ceremonies would fail unless the attacker tampered with all of them. Attestation certificates can also be used to track users, and avoiding the consent needed to relay identifying information is one reason the spec gives for the none default. Request it only when policy must restrict authenticator models, as in Entra passkey profiles where you set Enforce attestation per group. How common that is across deployments was not measured here.

## Sessions, federation and token theft

NIST requires the session secret to be generated by the session host in response to authentication, at least 64 bits from an approved random bit generator, erased or invalidated at logout, and unavailable to intermediaries; it says secrets should not be placed in insecure locations such as HTML5 Local Storage. Bearer session secrets should not persist across restarts. Cookies SHALL be Secure and SHOULD be HttpOnly, carry the `__Host-` prefix with Path=/, set SameSite Lax or Strict, and hold only an opaque identifier. That SameSite advice is for the cookie that maintains the authenticated session. A Lax or Strict cookie is not sent on the cross-site POST that carries a SAML response to the ACS (lesson 2), so do not count on one to carry state across that single request; the two statements concern different requests. A session may be treated at a lower AAL than its authentication event but never a higher one.

In federation the IdP session and each RP session end independently, so an RP that demands reauthentication may receive a fresh assertion from a still-valid IdP session. The IdP can report the time and details of the authentication event, but the RP is authoritative on whether its reauthentication rules were met. NIST also says an access token's presence must not be read as the user's presence.

**Device Bound Session Credentials (DBSC)** is a W3C Editor's Draft (8 September 2026) whose own introduction calls it a very early drafting. It lets a server verify that a session credential, a private key the browser protects (for example in a TPM), has not been exported from the device. Its stated non-goals: it does not prevent access while an attacker is resident on the device, because the signing capability remains available to programs running as the user, nor an attack if the attacker controls the browser at registration. NIST mentions DBSC as emerging and still requires lifetime limits to be enforced. Google says DBSC is generally available in Chrome on Windows and on by default for Google Workspace users (Google Workspace Updates, 28 May 2026); support in other browsers was not verified. Treat it as a partial control: it aims at cookie reuse on another device, not at an attacker on the device, and it does not replace session lifetime limits.

## Attack classes and the four failure modes

- **Relay (AitM) phishing.** OTP and push outputs are relayed; WebAuthn fails twice for the attacker, once because the client scopes credentials by RP ID and once because the RP validates origin. After a successful relay of a weaker factor, the stolen cookie is a bearer credential. (The RP-ID scoping holds unless the phishing origin is on your related-origins list.)
- **SMS fallback downgrading policy.** The attacker chooses the weakest path any rule allows. Entra authentication strength is evaluated after initial authentication, so it does not restrict that first step. Audit every rule, enrolment policy and recovery rule, not only the sign-in rule.
- **Recovery as the weakest link.** NIST recognises four classes of recovery: saved recovery codes, issued recovery codes, recovery contacts and repeated identity proofing, and requires a notification on every recovery. Okta can require phishing-resistant authenticators for unlock and password reset: the password policy's Recovery authenticators access control must point at the authentication policy, and the Okta account management policy then needs a rule that requires a phishing-resistant possession factor.
- **Enrolment race.** NIST requires authentication at the lower of the account's maximum AAL and the new authenticator's AAL, so an account that currently has only AAL1 capability can be bound to an AAL2 authenticator after a password alone. A binding code requested from an already-authenticated endpoint (NIST's binding-across-endpoints method) does not close this: that method only needs the same lower-AAL authentication, and an attacker holding the temporary password is that endpoint. Initial binding is governed by SP 800-63A: outside a single protected session with the proofed user, the CSP SHALL confirm the intended subscriber, for example by return of a continuation code (single use, at least 64 bits, delivered in session or out of band to a mailing address, phone number or email address). Applying that to a workforce account is this lesson's reading, not a quoted rule: bind the first authenticator only on return of a single-use code sent to contact details the hire controls, and send the mandatory notification through an independent channel. The notification makes a rogue enrolment noticeable; it does not prevent one.
- **Synced passkey in a personal account on a corporate device.** BE equals 1 means the credential copies to an account you do not manage. Record BE and BS and require BE equal to 0 where policy demands device-bound keys, but trust the flag only as far as you trust the authenticator reporting it: with none attestation the statement is empty and nothing signs the registration's authenticator data, and Entra says that without enforced attestation it cannot guarantee any attribute of a passkey, including whether it is synced or device-bound.
- **Fatigue.** Rate-limit pushes (NIST SHOULD) and use number matching, then move high-value apps to phishing-resistant methods.

**Where sources disagree or leave it open.**

- NIST's out-of-band note says the compare-and-approve method is no longer acceptable (fatigue attacks), requires the secret to be transferred between the phone and the sign-in screen, and says choosing from a list of secrets is not sufficient, while Okta says its number challenge helps prevent phishing and lists only Passkey and FastPass as phishing-resistant. Read number matching as a fatigue control, and check that your product has the user type the number rather than only choose it.
- NIST makes AAL2 timeouts a SHOULD and AAL3 timeouts a SHALL, and lets agencies document their own limits, so a 24-hour ceiling is guidance, not a universal rule.
- WebAuthn leaves the response to a lower signCount, and the use of attestation, to RP policy. Write both down as policy rather than inheriting a library default.

## Lab: a registration ceremony (not run)

Written from the WebAuthn spec's example, not run in a browser. On a page served from http://localhost (a permitted secure origin for the API), open the developer console and run:

```js
const cred = await navigator.credentials.create({ publicKey: {
  challenge: crypto.getRandomValues(new Uint8Array(32)),
  rp: { name: "Lab", id: "localhost" },
  user: { id: crypto.getRandomValues(new Uint8Array(16)), name: "lab@example.com", displayName: "Lab user" },
  pubKeyCredParams: [{ type: "public-key", alg: -7 }], attestation: "none" } });
console.log(JSON.parse(new TextDecoder().decode(cred.response.clientDataJSON)), cred.id);
```

Expected from the spec: after a gesture, an object whose type is webauthn.create, whose challenge is the base64url of your bytes and whose origin is your page's origin including the port. Change `id: "localhost"` to `"example.com"` and expect a SecurityError, because that RP ID is not a suffix of the page's domain. Your task: list every path in your tenant that can establish, reset or add an authenticator, and mark which are phishing-resistant. Lesson 7 covers authorization and the lifecycle.
