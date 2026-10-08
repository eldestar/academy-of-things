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
<div class="wa-wrap" style="position:relative">
<input type="checkbox" id="wa-pause" class="wa-cb" /><label for="wa-pause" class="wa-btn"><span class="wa-off">Pause animation</span><span class="wa-on">Play animation</span></label>
<div class="wa-box" style="overflow-x:auto">
<svg class="wa-flow" viewBox="0 0 760 614" role="img" aria-labelledby="wa-t wa-d" style="width:760px;max-width:100%;min-width:699px;height:auto;display:block;margin:0 auto">
<title id="wa-t">What the RP checks in a WebAuthn authentication</title>
<desc id="wa-d">Three parties: the authenticator, the client, and the relying party (RP). The RP sends a fresh challenge. The client asks for a signature scoped to the origin's RP ID. The authenticator returns authenticatorData and a signature. The client sends clientDataJSON, authenticatorData and the signature to the RP. The RP checks that the credential ID is in allowCredentials if one was sent, identifies the user, checks type webauthn.get, the challenge, the origin and the rpIdHash, requires the UP flag, requires UV if configured, and then verifies the signature over authenticatorData concatenated with the SHA-256 hash of clientDataJSON, using the stored public key. The diagram highlights each step in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
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
.wa-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:28s;animation-timing-function:linear;animation-iteration-count:infinite}
.wa-pk.wa-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.wa-pk.wa-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.wa-wrap{margin:20px 0}
@media (min-width:801px){.wa-wrap{margin-left:-44px;margin-right:-44px}}
.wa-g rect,.wa-g line,.wa-g path:not(.wa-gl){opacity:.5;animation-duration:28s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.wa-flow:hover .wa-g rect,svg.wa-flow:hover .wa-g line,svg.wa-flow:hover .wa-g path:not(.wa-gl),svg.wa-flow:hover .wa-pk{animation-play-state:paused}
.wa-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.wa-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.wa-btn:hover{background:var(--hover)}
.wa-cb:focus-visible + .wa-btn{outline:2px solid var(--accent);outline-offset:2px}
.wa-cb:checked + .wa-btn .wa-off,.wa-cb:not(:checked) + .wa-btn .wa-on{display:none}
.wa-cb:checked ~ .wa-box .wa-g rect,.wa-cb:checked ~ .wa-box .wa-g line,.wa-cb:checked ~ .wa-box .wa-g path:not(.wa-gl),.wa-cb:checked ~ .wa-box .wa-pk{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.wa-g rect,.wa-g line,.wa-g path:not(.wa-gl){animation:none;opacity:1}.wa-pk{animation:none;display:none}.wa-btn{display:none}}
@keyframes wa-g0{0%{opacity:1}21.429%{opacity:1}21.439%,100%{opacity:.5}}
@keyframes wa-p0{0%,-0.01%{opacity:0;transform:translateX(0)}0%{opacity:1;transform:translateX(0)}17.143%{opacity:1;transform:translateX(-236px)}21.429%{opacity:1;transform:translateX(-236px)}21.439%,100%{opacity:0;transform:translateX(-236px)}}
.wa-g0 rect,.wa-g0 line,.wa-g0 path:not(.wa-gl){animation-name:wa-g0}.wa-p0{animation-name:wa-p0}
@keyframes wa-g1{0%,21.419%{opacity:.5}21.429%{opacity:1}42.857%{opacity:1}42.867%,100%{opacity:.5}}
@keyframes wa-p1{0%,21.419%{opacity:0;transform:translateX(0)}21.429%{opacity:1;transform:translateX(0)}38.571%{opacity:1;transform:translateX(-236px)}42.857%{opacity:1;transform:translateX(-236px)}42.867%,100%{opacity:0;transform:translateX(-236px)}}
.wa-g1 rect,.wa-g1 line,.wa-g1 path:not(.wa-gl){animation-name:wa-g1}.wa-p1{animation-name:wa-p1}
@keyframes wa-g2{0%,42.847%{opacity:.5}42.857%{opacity:1}64.286%{opacity:1}64.296%,100%{opacity:.5}}
@keyframes wa-p2{0%,42.847%{opacity:0;transform:translateX(0)}42.857%{opacity:1;transform:translateX(0)}60%{opacity:1;transform:translateX(236px)}64.286%{opacity:1;transform:translateX(236px)}64.296%,100%{opacity:0;transform:translateX(236px)}}
.wa-g2 rect,.wa-g2 line,.wa-g2 path:not(.wa-gl){animation-name:wa-g2}.wa-p2{animation-name:wa-p2}
@keyframes wa-g3{0%,64.276%{opacity:.5}64.286%{opacity:1}85.714%{opacity:1}85.724%,100%{opacity:.5}}
@keyframes wa-p3{0%,64.276%{opacity:0;transform:translateX(0)}64.286%{opacity:1;transform:translateX(0)}81.429%{opacity:1;transform:translateX(236px)}85.714%{opacity:1;transform:translateX(236px)}85.724%,100%{opacity:0;transform:translateX(236px)}}
.wa-g3 rect,.wa-g3 line,.wa-g3 path:not(.wa-gl){animation-name:wa-g3}.wa-p3{animation-name:wa-p3}
@keyframes wa-g4{0%,85.704%{opacity:.5}85.714%{opacity:1}100%{opacity:1}100.01%,100%{opacity:.5}}
.wa-g4 rect,.wa-g4 line,.wa-g4 path:not(.wa-gl){animation-name:wa-g4}
</style>
<defs>
<marker id="wa-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="wa-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="wa-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<line class="wa-life" x1="110" y1="72" x2="110" y2="562"/>
<line class="wa-life" x1="380" y1="72" x2="380" y2="562"/>
<line class="wa-life" x1="650" y1="72" x2="650" y2="562"/>
<rect class="wa-box" x="20" y="10" width="180" height="62" rx="10"/><text class="wa-ttl" x="110" y="36">Authenticator</text><text class="wa-sub" x="110" y="56">returns the signature</text>
<rect class="wa-box" x="290" y="10" width="180" height="62" rx="10"/><text class="wa-ttl" x="380" y="36">Client</text><text class="wa-sub" x="380" y="56">scopes it to the RP ID</text>
<rect class="wa-hot" x="560" y="10" width="180" height="62" rx="10"/><text class="wa-ttl" x="650" y="36">Relying party</text><text class="wa-sub" x="650" y="56">verifies the response</text>
<g class="wa-g wa-g0">
<text class="wa-main" x="515" y="108">sends a fresh challenge</text>
<line class="wa-front" x1="636" y1="122" x2="394" y2="122" marker-end="url(#wa-m-front)"/>
<circle class="wa-badge wa-b-front" cx="650" cy="122" r="12"/><text class="wa-bt" x="650" y="126.5">A1</text>
</g>
<g class="wa-g wa-g1">
<text class="wa-main" x="245" y="162">asks for a signature</text>
<text class="wa-dim" x="245" y="178">scoped to the origin's RP ID</text>
<line class="wa-front" x1="366" y1="192" x2="124" y2="192" marker-end="url(#wa-m-front)"/>
<circle class="wa-badge wa-b-front" cx="380" cy="192" r="12"/><text class="wa-bt" x="380" y="196.5">A2</text>
</g>
<g class="wa-g wa-g2">
<text class="wa-main" x="245" y="232">authenticatorData</text>
<text class="wa-dim" x="245" y="248">+ signature</text>
<line class="wa-front" x1="124" y1="262" x2="366" y2="262" marker-end="url(#wa-m-front)"/>
<circle class="wa-badge wa-b-front" cx="110" cy="262" r="12"/><text class="wa-bt" x="110" y="266.5">A3</text>
</g>
<g class="wa-g wa-g3">
<text class="wa-main" x="515" y="302">clientDataJSON,</text>
<text class="wa-dim" x="515" y="318">authenticatorData, signature</text>
<line class="wa-front" x1="394" y1="332" x2="636" y2="332" marker-end="url(#wa-m-front)"/>
<circle class="wa-badge wa-b-front" cx="380" cy="332" r="12"/><text class="wa-bt" x="380" y="336.5">A4</text>
</g>
<g class="wa-g wa-g4">
<rect class="wa-note-good" x="483" y="366" width="267" height="150" rx="8"/>
<text class="wa-nt" x="616" y="387">credential ID in allowCredentials,</text>
<text class="wa-nt" x="616" y="404">if one was sent; identifies the user</text>
<text class="wa-nt" x="616" y="421">type webauthn.get, challenge,</text>
<text class="wa-nt" x="616" y="438">origin, rpIdHash</text>
<text class="wa-nt" x="616" y="455">UP required; UV if configured</text>
<text class="wa-nt" x="616" y="472">then the signature over</text>
<text class="wa-nt" x="616" y="489">authenticatorData + SHA-256 of</text>
<text class="wa-nt" x="616" y="506">clientDataJSON, with the stored key</text>
</g>
<circle class="wa-pk wa-p0" cx="630" cy="122" r="5.5"/>
<circle class="wa-pk wa-p1" cx="360" cy="192" r="5.5"/>
<circle class="wa-pk wa-p2" cx="130" cy="262" r="5.5"/>
<circle class="wa-pk wa-p3" cx="400" cy="332" r="5.5"/>
<line class="wa-front" x1="40" y1="590" x2="70" y2="590"/>
<text class="wa-dim" x="78" y="594" style="text-anchor:start">message in the ceremony</text>
<rect class="wa-note-good" x="259" y="582" width="22" height="16" rx="4"/>
<text class="wa-dim" x="289" y="594" style="text-anchor:start">what the RP checks</text>
</svg>
</div>
</div>
<!-- /diagram:webauthn-ceremony -->

R1 to R4 register a credential; A1 to A4 authenticate with it. The diagram zooms in on authentication, A1 to A4, and on what the RP checks when the response arrives; its badges match the A1 to A4 text below, and registration is in the R1 to R4 text. Here a credential is a WebAuthn public-key credential (the spec's glossary lists passkey as a term for a discoverable one); a session cookie is a bearer credential, whose holder is accepted without proving anything else (NIST calls session secrets used this way bearer tokens).

**Registration (R1 to R4).** R1: the RP creates options with a challenge (at least 16 bytes recommended) and an RP ID. R2: the client rejects an RP ID that is not the origin's effective domain or a registrable domain suffix of it, and asks the authenticator to create a key pair after a gesture. R3: the authenticator returns the credential ID, public key and attestation. R4: the RP verifies, in order, client data type webauthn.create, the challenge, an expected origin, rpIdHash equal to the SHA-256 of its RP ID, the UP flag (unless the ceremony used conditional mediation), and UV if it requires it, the BE and BS consistency rule, the algorithm against the requested list, and the attestation per its policy.

**Authentication (A1 to A4).** A1: the RP sends a fresh challenge. A2: the client asks for a signature scoped to the origin's RP ID. A3: the authenticator returns authenticatorData and a signature. A4: the browser sends clientDataJSON, authenticatorData and the signature, and the RP checks that the credential ID is in allowCredentials if one was sent, identifies the user, checks type webauthn.get, challenge, origin and rpIdHash, requires UP, requires UV if configured, then verifies the signature over authenticatorData concatenated with the SHA-256 hash of clientDataJSON, using the stored public key.

<!-- diagram:rp-id-scope -->
<div class="l06c-wrap" style="position:relative">
<input type="checkbox" id="l06c-pause" class="l06c-cb" /><label for="l06c-pause" class="l06c-btn"><span class="l06c-off">Pause animation</span><span class="l06c-on">Play animation</span></label>
<div class="l06c-box" style="overflow-x:auto">
<svg class="l06c-flow" viewBox="0 0 760 446" role="img" aria-labelledby="l06c-t l06c-d" style="width:760px;max-width:100%;min-width:699px;height:auto;display:block;margin:0 auto">
<title id="l06c-t">Can a page on another origin use your credential?</title>
<desc id="l06c-d">A decision tree that starts with where the page runs. A page on another domain is stopped by the client, which scopes credentials by RP ID. A page on a subdomain may legitimately request the parent RP ID, so the question is whether the RP accepts subdomain origins: by default it should not, and its origin validation rejects the unexpected origin; if it does allow subdomains and untrusted code runs on one, that code can relay valid assertions. A page on an origin listed in the RP's related origins is the opt-in exception, where RP ID scoping does not hold, so list only origins you control. The diagram highlights each path in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
<style>
svg.l06c-flow{--ink:light-dark(#000000,#ffffff)}
.l06c-box{fill:var(--panel);stroke:var(--border-strong);stroke-width:1.5}
.l06c-hot{fill:var(--panel);stroke:var(--accent);stroke-width:2.5}
.l06c-ttl{fill:var(--ink);font:600 15px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l06c-sub{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l06c-life{stroke:var(--border-strong);stroke-width:1.5;stroke-dasharray:4 5}
.l06c-front{stroke:var(--accent);stroke-width:2;fill:none}
.l06c-back{stroke:var(--muted);stroke-width:2;stroke-dasharray:7 5;fill:none}
.l06c-bad{stroke:var(--bad);stroke-width:2;fill:none}
.l06c-main{fill:var(--ink);font:600 13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l06c-badt{fill:var(--ink)}
.l06c-dim{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l06c-badge{fill:var(--accent)}
.l06c-b-back{fill:var(--muted)}
.l06c-b-bad{fill:var(--bad)}
.l06c-b-good{fill:var(--good)}
.l06c-bt{fill:var(--on-accent);font:700 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l06c-note{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l06c-note-good{fill:var(--good-bg);stroke:var(--good);stroke-width:1.5}
.l06c-note-bad{fill:var(--bad-bg);stroke:var(--bad);stroke-width:1.5}
.l06c-nt{fill:var(--ink);font:500 12.5px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l06c-nest{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l06c-row{fill:var(--raised);stroke:var(--border-strong);stroke-width:1}
.l06c-ttlL{fill:var(--ink);font:600 14px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l06c-subL{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l06c-dimL{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l06c-dimR{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:end}
.l06c-conn{stroke:var(--accent);stroke-width:1.5;fill:none}
.l06c-edge{stroke:var(--border-strong);stroke-width:1.75;fill:none}
.l06c-hl{fill:none;stroke:var(--accent);stroke-width:3}
.l06c-hle{stroke:var(--accent);stroke-width:3;fill:none}
.l06c-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:20s;animation-timing-function:linear;animation-iteration-count:infinite}
.l06c-pk.l06c-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.l06c-pk.l06c-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.l06c-wrap{margin:20px 0}
@media (min-width:801px){.l06c-wrap{margin-left:-44px;margin-right:-44px}}
.l06c-g rect,.l06c-g line,.l06c-g path:not(.l06c-gl){opacity:.5;animation-duration:20s;animation-timing-function:linear;animation-iteration-count:infinite}
.l06c-h{opacity:0;animation-duration:20s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.l06c-flow:hover .l06c-g rect,svg.l06c-flow:hover .l06c-g line,svg.l06c-flow:hover .l06c-g path:not(.l06c-gl),svg.l06c-flow:hover .l06c-pk,svg.l06c-flow:hover .l06c-h{animation-play-state:paused}
.l06c-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.l06c-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.l06c-btn:hover{background:var(--hover)}
.l06c-cb:focus-visible + .l06c-btn{outline:2px solid var(--accent);outline-offset:2px}
.l06c-cb:checked + .l06c-btn .l06c-off,.l06c-cb:not(:checked) + .l06c-btn .l06c-on{display:none}
.l06c-cb:checked ~ .l06c-box .l06c-g rect,.l06c-cb:checked ~ .l06c-box .l06c-g line,.l06c-cb:checked ~ .l06c-box .l06c-g path:not(.l06c-gl),.l06c-cb:checked ~ .l06c-box .l06c-pk,.l06c-cb:checked ~ .l06c-box .l06c-h{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.l06c-g rect,.l06c-g line,.l06c-g path:not(.l06c-gl){animation:none;opacity:1}.l06c-pk{animation:none;display:none}.l06c-h{animation:none;opacity:0}.l06c-btn{display:none}}
@keyframes l06c-h0{0%{opacity:1}25%{opacity:1}25.01%,100%{opacity:0}}
.l06c-h0{animation-name:l06c-h0}
@keyframes l06c-h1{0%,24.99%{opacity:0}25%{opacity:1}50%{opacity:1}50.01%,100%{opacity:0}}
.l06c-h1{animation-name:l06c-h1}
@keyframes l06c-h2{0%,49.99%{opacity:0}50%{opacity:1}75%{opacity:1}75.01%,100%{opacity:0}}
.l06c-h2{animation-name:l06c-h2}
@keyframes l06c-h3{0%,74.99%{opacity:0}75%{opacity:1}100%{opacity:1}100.01%,100%{opacity:0}}
.l06c-h3{animation-name:l06c-h3}
</style>
<defs>
<marker id="l06c-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="l06c-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="l06c-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<path class="l06c-edge" d="M380,106 L380,135 L141,135 L141,161" marker-end="url(#l06c-m-front)"/>
<text class="l06c-dimL" x="148" y="151">another domain</text>
<path class="l06c-edge" d="M380,106 L380,135 L370,135 L370,161" marker-end="url(#l06c-m-front)"/>
<text class="l06c-dimL" x="377" y="151">a subdomain</text>
<path class="l06c-edge" d="M370,229 L370,258 L288,258 L288,301" marker-end="url(#l06c-m-front)"/>
<text class="l06c-dimL" x="295" y="291">no (default)</text>
<path class="l06c-edge" d="M370,229 L370,258 L448,258 L448,301" marker-end="url(#l06c-m-front)"/>
<text class="l06c-dimL" x="456" y="291">yes</text>
<path class="l06c-edge" d="M380,106 L380,135 L609,135 L609,161" marker-end="url(#l06c-m-front)"/>
<text class="l06c-dimL" x="616" y="151">a related origin</text>
<rect class="l06c-note-good" x="80" y="164" width="121" height="65" rx="8"/><text class="l06c-nt" x="141" y="185">Client scoping</text><text class="l06c-nt" x="141" y="202">by RP ID</text><text class="l06c-nt" x="141" y="219">stops it</text>
<rect class="l06c-note-good" x="218" y="304" width="141" height="65" rx="8"/><text class="l06c-nt" x="288" y="325">Origin check</text><text class="l06c-nt" x="288" y="342">rejects the</text><text class="l06c-nt" x="288" y="359">unexpected origin</text>
<rect class="l06c-note-bad" x="374" y="304" width="148" height="82" rx="8"/><text class="l06c-nt" x="448" y="325">If untrusted code</text><text class="l06c-nt" x="448" y="342">runs there, it can</text><text class="l06c-nt" x="448" y="359">relay valid</text><text class="l06c-nt" x="448" y="376">assertions</text>
<rect class="l06c-box" x="306" y="164" width="128" height="65" rx="8"/><text class="l06c-main" x="370" y="185">Does the RP</text><text class="l06c-nt" x="370" y="202">allow subdomain</text><text class="l06c-nt" x="370" y="219">origins?</text>
<rect class="l06c-note-bad" x="538" y="164" width="141" height="82" rx="8"/><text class="l06c-nt" x="609" y="185">RP ID scoping</text><text class="l06c-nt" x="609" y="202">does not hold;</text><text class="l06c-nt" x="609" y="219">list only origins</text><text class="l06c-nt" x="609" y="236">you control</text>
<rect class="l06c-box" x="306" y="24" width="148" height="82" rx="8"/><text class="l06c-main" x="380" y="45">A page asks to use</text><text class="l06c-nt" x="380" y="62">a credential for</text><text class="l06c-nt" x="380" y="79">your RP ID: which</text><text class="l06c-nt" x="380" y="96">origin is it on?</text>
<g class="l06c-h l06c-h0">
<path class="l06c-hle" d="M380,106 L380,135 L141,135 L141,161" marker-end="url(#l06c-m-front)"/>
<rect class="l06c-hl" x="306" y="24" width="148" height="82" rx="8"/>
<rect class="l06c-hl" x="80" y="164" width="121" height="65" rx="8"/>
</g>
<g class="l06c-h l06c-h1">
<path class="l06c-hle" d="M380,106 L380,135 L370,135 L370,161" marker-end="url(#l06c-m-front)"/>
<path class="l06c-hle" d="M370,229 L370,258 L288,258 L288,301" marker-end="url(#l06c-m-front)"/>
<rect class="l06c-hl" x="306" y="24" width="148" height="82" rx="8"/>
<rect class="l06c-hl" x="306" y="164" width="128" height="65" rx="8"/>
<rect class="l06c-hl" x="218" y="304" width="141" height="65" rx="8"/>
</g>
<g class="l06c-h l06c-h2">
<path class="l06c-hle" d="M380,106 L380,135 L370,135 L370,161" marker-end="url(#l06c-m-front)"/>
<path class="l06c-hle" d="M370,229 L370,258 L448,258 L448,301" marker-end="url(#l06c-m-front)"/>
<rect class="l06c-hl" x="306" y="24" width="148" height="82" rx="8"/>
<rect class="l06c-hl" x="306" y="164" width="128" height="65" rx="8"/>
<rect class="l06c-hl" x="374" y="304" width="148" height="82" rx="8"/>
</g>
<g class="l06c-h l06c-h3">
<path class="l06c-hle" d="M380,106 L380,135 L609,135 L609,161" marker-end="url(#l06c-m-front)"/>
<rect class="l06c-hl" x="306" y="24" width="148" height="82" rx="8"/>
<rect class="l06c-hl" x="538" y="164" width="141" height="82" rx="8"/>
</g>
<line class="l06c-front" x1="40" y1="422" x2="70" y2="422"/>
<text class="l06c-dim" x="78" y="426" style="text-anchor:start">the path being traced</text>
<rect class="l06c-note-good" x="246" y="414" width="22" height="16" rx="4"/>
<text class="l06c-dim" x="276" y="426" style="text-anchor:start">stopped</text>
<rect class="l06c-note-bad" x="354" y="414" width="22" height="16" rx="4"/>
<text class="l06c-dim" x="384" y="426" style="text-anchor:start">gets through</text>
</svg>
</div>
</div>
<!-- /diagram:rp-id-scope -->

The tree sorts the attacker's page by where it runs: another domain is stopped by the client's RP ID scoping, a subdomain by the RP's origin validation unless you allow subdomain origins, and a related origin is the opt-in exception. The two leaves marked as getting through are the ones you control.

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

<!-- diagram:dbsc -->
<div class="l06e-wrap" style="position:relative">
<input type="checkbox" id="l06e-pause" class="l06e-cb" /><label for="l06e-pause" class="l06e-btn"><span class="l06e-off">Pause animation</span><span class="l06e-on">Play animation</span></label>
<div class="l06e-box" style="overflow-x:auto">
<svg class="l06e-flow" viewBox="0 0 760 397" role="img" aria-labelledby="l06e-t l06e-d" style="width:760px;max-width:100%;min-width:699px;height:auto;display:block;margin:0 auto">
<title id="l06e-t">What Device Bound Session Credentials do and do not cover</title>
<desc id="l06e-d">One column for DBSC, a W3C Editor's Draft whose own introduction calls it a very early drafting, treated as a partial control. It is aimed at cookie reuse on another device: a server can verify that the session credential, a private key the browser protects, has not been exported from the device. It does not prevent access while an attacker is resident on the device, because the signing capability stays available to programs running as the user. It does not prevent an attack if the attacker controls the browser at registration. The diagram highlights each row in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
<style>
svg.l06e-flow{--ink:light-dark(#000000,#ffffff)}
.l06e-box{fill:var(--panel);stroke:var(--border-strong);stroke-width:1.5}
.l06e-hot{fill:var(--panel);stroke:var(--accent);stroke-width:2.5}
.l06e-ttl{fill:var(--ink);font:600 15px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l06e-sub{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l06e-life{stroke:var(--border-strong);stroke-width:1.5;stroke-dasharray:4 5}
.l06e-front{stroke:var(--accent);stroke-width:2;fill:none}
.l06e-back{stroke:var(--muted);stroke-width:2;stroke-dasharray:7 5;fill:none}
.l06e-bad{stroke:var(--bad);stroke-width:2;fill:none}
.l06e-main{fill:var(--ink);font:600 13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l06e-badt{fill:var(--ink)}
.l06e-dim{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l06e-badge{fill:var(--accent)}
.l06e-b-back{fill:var(--muted)}
.l06e-b-bad{fill:var(--bad)}
.l06e-b-good{fill:var(--good)}
.l06e-bt{fill:var(--on-accent);font:700 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l06e-note{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l06e-note-good{fill:var(--good-bg);stroke:var(--good);stroke-width:1.5}
.l06e-note-bad{fill:var(--bad-bg);stroke:var(--bad);stroke-width:1.5}
.l06e-nt{fill:var(--ink);font:500 12.5px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l06e-nest{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l06e-row{fill:var(--raised);stroke:var(--border-strong);stroke-width:1}
.l06e-ttlL{fill:var(--ink);font:600 14px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l06e-subL{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l06e-dimL{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l06e-dimR{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:end}
.l06e-conn{stroke:var(--accent);stroke-width:1.5;fill:none}
.l06e-edge{stroke:var(--border-strong);stroke-width:1.75;fill:none}
.l06e-hl{fill:none;stroke:var(--accent);stroke-width:3}
.l06e-hle{stroke:var(--accent);stroke-width:3;fill:none}
.l06e-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:16s;animation-timing-function:linear;animation-iteration-count:infinite}
.l06e-pk.l06e-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.l06e-pk.l06e-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.l06e-wrap{margin:20px 0}
@media (min-width:801px){.l06e-wrap{margin-left:-44px;margin-right:-44px}}
.l06e-g rect,.l06e-g line,.l06e-g path:not(.l06e-gl){opacity:.5;animation-duration:16s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.l06e-flow:hover .l06e-g rect,svg.l06e-flow:hover .l06e-g line,svg.l06e-flow:hover .l06e-g path:not(.l06e-gl),svg.l06e-flow:hover .l06e-pk{animation-play-state:paused}
.l06e-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.l06e-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.l06e-btn:hover{background:var(--hover)}
.l06e-cb:focus-visible + .l06e-btn{outline:2px solid var(--accent);outline-offset:2px}
.l06e-cb:checked + .l06e-btn .l06e-off,.l06e-cb:not(:checked) + .l06e-btn .l06e-on{display:none}
.l06e-cb:checked ~ .l06e-box .l06e-g rect,.l06e-cb:checked ~ .l06e-box .l06e-g line,.l06e-cb:checked ~ .l06e-box .l06e-g path:not(.l06e-gl),.l06e-cb:checked ~ .l06e-box .l06e-pk{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.l06e-g rect,.l06e-g line,.l06e-g path:not(.l06e-gl){animation:none;opacity:1}.l06e-pk{animation:none;display:none}.l06e-btn{display:none}}
@keyframes l06e-g0{0%{opacity:1}33.333%{opacity:1}33.343%,100%{opacity:.5}}
.l06e-g0 rect,.l06e-g0 line,.l06e-g0 path:not(.l06e-gl){animation-name:l06e-g0}
@keyframes l06e-g1{0%,33.323%{opacity:.5}33.333%{opacity:1}66.667%{opacity:1}66.677%,100%{opacity:.5}}
.l06e-g1 rect,.l06e-g1 line,.l06e-g1 path:not(.l06e-gl){animation-name:l06e-g1}
@keyframes l06e-g2{0%,66.657%{opacity:.5}66.667%{opacity:1}100%{opacity:1}100.01%,100%{opacity:.5}}
.l06e-g2 rect,.l06e-g2 line,.l06e-g2 path:not(.l06e-gl){animation-name:l06e-g2}
</style>
<defs>
<marker id="l06e-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="l06e-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="l06e-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<rect class="l06e-box" x="240" y="10" width="502" height="62" rx="10"/><text class="l06e-ttl" x="491" y="36">DBSC, a very early draft</text><text class="l06e-sub" x="491" y="56">treat it as a partial control</text>
<g class="l06e-g l06e-g0">
<rect class="l06e-row" x="10" y="86" width="740" height="86" rx="8"/>
<text class="l06e-ttlL" x="24" y="112">Cookie reuse</text>
<text class="l06e-subL" x="24" y="130">on another device</text>
<circle cx="491" cy="108" r="10" style="fill:var(--good)"/><path class="l06e-gl" d="M486.8,108.0 L489.6,111.4 L495.2,104.6" style="fill:none;stroke:var(--on-accent);stroke-width:2;stroke-linecap:round;stroke-linejoin:round"/>
<text class="l06e-nt" x="491" y="134">a server can verify the session key</text>
<text class="l06e-nt" x="491" y="149">has not been exported from the device</text>
</g>
<g class="l06e-g l06e-g1">
<rect class="l06e-row" x="10" y="180" width="740" height="86" rx="8"/>
<text class="l06e-ttlL" x="24" y="206">Attacker on the device</text>
<text class="l06e-subL" x="24" y="224">already resident</text>
<circle cx="491" cy="202" r="10" style="fill:var(--bad)"/><path class="l06e-gl" d="M487.6,198.6 L494.4,205.4 M494.4,198.6 L487.6,205.4" style="fill:none;stroke:var(--on-accent);stroke-width:2;stroke-linecap:round;stroke-linejoin:round"/>
<text class="l06e-nt" x="491" y="228">not prevented: the signing capability</text>
<text class="l06e-nt" x="491" y="243">stays available to programs running as the user</text>
</g>
<g class="l06e-g l06e-g2">
<rect class="l06e-row" x="10" y="274" width="740" height="71" rx="8"/>
<text class="l06e-ttlL" x="24" y="300">Attacker controls browser</text>
<text class="l06e-subL" x="24" y="318">at registration</text>
<circle cx="491" cy="296" r="10" style="fill:var(--bad)"/><path class="l06e-gl" d="M487.6,292.6 L494.4,299.4 M494.4,292.6 L487.6,299.4" style="fill:none;stroke:var(--on-accent);stroke-width:2;stroke-linecap:round;stroke-linejoin:round"/>
<text class="l06e-nt" x="491" y="322">not prevented (a stated non-goal)</text>
</g>
<circle cx="48" cy="373" r="8" style="fill:var(--good)"/><path class="l06e-gl" d="M44.6,373.0 L46.9,375.7 L51.4,370.3" style="fill:none;stroke:var(--on-accent);stroke-width:2;stroke-linecap:round;stroke-linejoin:round"/>
<text class="l06e-dim" x="64" y="377" style="text-anchor:start">aimed at</text>
<circle cx="157" cy="373" r="8" style="fill:var(--bad)"/><path class="l06e-gl" d="M154.3,370.3 L159.7,375.7 M159.7,370.3 L154.3,375.7" style="fill:none;stroke:var(--on-accent);stroke-width:2;stroke-linecap:round;stroke-linejoin:round"/>
<text class="l06e-dim" x="173" y="377" style="text-anchor:start">not covered</text>
</svg>
</div>
</div>
<!-- /diagram:dbsc -->

Each row is one threat compared with DBSC: only cookie reuse on another device is what it is aimed at, and the draft leaves the other two open. DBSC also does not replace session lifetime limits, which NIST still requires to be enforced.

## Attack classes and the four failure modes

- **Relay (AitM) phishing.** OTP and push outputs are relayed; WebAuthn fails twice for the attacker, once because the client scopes credentials by RP ID and once because the RP validates origin. After a successful relay of a weaker factor, the stolen cookie is a bearer credential. (The RP-ID scoping holds unless the phishing origin is on your related-origins list.)
- **SMS fallback downgrading policy.** The attacker chooses the weakest path any rule allows. Entra authentication strength is evaluated after initial authentication, so it does not restrict that first step. Audit every rule, enrolment policy and recovery rule, not only the sign-in rule.
- **Recovery as the weakest link.** NIST recognises four classes of recovery: saved recovery codes, issued recovery codes, recovery contacts and repeated identity proofing, and requires a notification on every recovery. Okta can require phishing-resistant authenticators for unlock and password reset: the password policy's Recovery authenticators access control must point at the authentication policy, and the Okta account management policy then needs a rule that requires a phishing-resistant possession factor.
- **Enrolment race.** NIST requires authentication at the lower of the account's maximum AAL and the new authenticator's AAL, so an account that currently has only AAL1 capability can be bound to an AAL2 authenticator after a password alone. A binding code requested from an already-authenticated endpoint (NIST's binding-across-endpoints method) does not close this: that method only needs the same lower-AAL authentication, and an attacker holding the temporary password is that endpoint. Initial binding is governed by SP 800-63A: outside a single protected session with the proofed user, the CSP SHALL confirm the intended subscriber, for example by return of a continuation code (single use, at least 64 bits, delivered in session or out of band to a mailing address, phone number or email address). Applying that to a workforce account is this lesson's reading, not a quoted rule: bind the first authenticator only on return of a single-use code sent to contact details the hire controls, and send the mandatory notification through an independent channel. The notification makes a rogue enrolment noticeable; it does not prevent one.
- **Synced passkey in a personal account on a corporate device.** BE equals 1 means the credential copies to an account you do not manage. Record BE and BS and require BE equal to 0 where policy demands device-bound keys, but trust the flag only as far as you trust the authenticator reporting it: with none attestation the statement is empty and nothing signs the registration's authenticator data, and Entra says that without enforced attestation it cannot guarantee any attribute of a passkey, including whether it is synced or device-bound.
- **Fatigue.** Rate-limit pushes (NIST SHOULD) and use number matching, then move high-value apps to phishing-resistant methods.

<!-- diagram:enrolment-race -->
<div class="l06d-wrap" style="position:relative">
<input type="checkbox" id="l06d-pause" class="l06d-cb" /><label for="l06d-pause" class="l06d-btn"><span class="l06d-off">Pause animation</span><span class="l06d-on">Play animation</span></label>
<div class="l06d-box" style="overflow-x:auto">
<svg class="l06d-flow" viewBox="0 0 760 839" role="img" aria-labelledby="l06d-t l06d-d" style="width:760px;max-width:100%;min-width:699px;height:auto;display:block;margin:0 auto">
<title id="l06d-t">The enrolment race: binding the first authenticator</title>
<desc id="l06d-d">Three parties: the new hire, an attacker who holds the temporary password, and the identity provider. NIST requires authentication at the lower of the account's maximum AAL and the new authenticator's AAL, so an account that currently has only AAL1 capability can be bound to an AAL2 authenticator after a password alone. The attacker enrols with the temporary password. A binding code sent to an already-authenticated endpoint does not close this, because the attacker holding the temporary password is that endpoint. NIST makes a notification mandatory; this lesson's reading of SP 800-63A is to send it through an independent channel, which makes a rogue enrolment noticeable but does not prevent one, and to bind the first authenticator only on return of a single-use code sent to contact details the hire controls. The diagram highlights each step in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
<style>
svg.l06d-flow{--ink:light-dark(#000000,#ffffff)}
.l06d-box{fill:var(--panel);stroke:var(--border-strong);stroke-width:1.5}
.l06d-hot{fill:var(--panel);stroke:var(--accent);stroke-width:2.5}
.l06d-ttl{fill:var(--ink);font:600 15px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l06d-sub{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l06d-life{stroke:var(--border-strong);stroke-width:1.5;stroke-dasharray:4 5}
.l06d-front{stroke:var(--accent);stroke-width:2;fill:none}
.l06d-back{stroke:var(--muted);stroke-width:2;stroke-dasharray:7 5;fill:none}
.l06d-bad{stroke:var(--bad);stroke-width:2;fill:none}
.l06d-main{fill:var(--ink);font:600 13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l06d-badt{fill:var(--ink)}
.l06d-dim{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l06d-badge{fill:var(--accent)}
.l06d-b-back{fill:var(--muted)}
.l06d-b-bad{fill:var(--bad)}
.l06d-b-good{fill:var(--good)}
.l06d-bt{fill:var(--on-accent);font:700 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l06d-note{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l06d-note-good{fill:var(--good-bg);stroke:var(--good);stroke-width:1.5}
.l06d-note-bad{fill:var(--bad-bg);stroke:var(--bad);stroke-width:1.5}
.l06d-nt{fill:var(--ink);font:500 12.5px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l06d-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:34s;animation-timing-function:linear;animation-iteration-count:infinite}
.l06d-pk.l06d-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.l06d-pk.l06d-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.l06d-wrap{margin:20px 0}
@media (min-width:801px){.l06d-wrap{margin-left:-44px;margin-right:-44px}}
.l06d-g rect,.l06d-g line,.l06d-g path:not(.l06d-gl){opacity:.5;animation-duration:34s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.l06d-flow:hover .l06d-g rect,svg.l06d-flow:hover .l06d-g line,svg.l06d-flow:hover .l06d-g path:not(.l06d-gl),svg.l06d-flow:hover .l06d-pk{animation-play-state:paused}
.l06d-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.l06d-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.l06d-btn:hover{background:var(--hover)}
.l06d-cb:focus-visible + .l06d-btn{outline:2px solid var(--accent);outline-offset:2px}
.l06d-cb:checked + .l06d-btn .l06d-off,.l06d-cb:not(:checked) + .l06d-btn .l06d-on{display:none}
.l06d-cb:checked ~ .l06d-box .l06d-g rect,.l06d-cb:checked ~ .l06d-box .l06d-g line,.l06d-cb:checked ~ .l06d-box .l06d-g path:not(.l06d-gl),.l06d-cb:checked ~ .l06d-box .l06d-pk{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.l06d-g rect,.l06d-g line,.l06d-g path:not(.l06d-gl){animation:none;opacity:1}.l06d-pk{animation:none;display:none}.l06d-btn{display:none}}
@keyframes l06d-g0{0%{opacity:1}17.647%{opacity:1}17.657%,100%{opacity:.5}}
@keyframes l06d-p0{0%,-0.01%{opacity:0;transform:translateX(0)}0%{opacity:1;transform:translateX(0)}14.118%{opacity:1;transform:translateX(236px)}17.647%{opacity:1;transform:translateX(236px)}17.657%,100%{opacity:0;transform:translateX(236px)}}
.l06d-g0 rect,.l06d-g0 line,.l06d-g0 path:not(.l06d-gl){animation-name:l06d-g0}.l06d-p0{animation-name:l06d-p0}
@keyframes l06d-g1{0%,17.637%{opacity:.5}17.647%{opacity:1}29.412%{opacity:1}29.422%,100%{opacity:.5}}
.l06d-g1 rect,.l06d-g1 line,.l06d-g1 path:not(.l06d-gl){animation-name:l06d-g1}
@keyframes l06d-g2{0%,29.402%{opacity:.5}29.412%{opacity:1}47.059%{opacity:1}47.069%,100%{opacity:.5}}
@keyframes l06d-p2{0%,29.402%{opacity:0;transform:translateX(0)}29.412%{opacity:1;transform:translateX(0)}43.529%{opacity:1;transform:translateX(236px)}47.059%{opacity:1;transform:translateX(236px)}47.069%,100%{opacity:0;transform:translateX(236px)}}
.l06d-g2 rect,.l06d-g2 line,.l06d-g2 path:not(.l06d-gl){animation-name:l06d-g2}.l06d-p2{animation-name:l06d-p2}
@keyframes l06d-g3{0%,47.049%{opacity:.5}47.059%{opacity:1}58.824%{opacity:1}58.834%,100%{opacity:.5}}
.l06d-g3 rect,.l06d-g3 line,.l06d-g3 path:not(.l06d-gl){animation-name:l06d-g3}
@keyframes l06d-g4{0%,58.814%{opacity:.5}58.824%{opacity:1}76.471%{opacity:1}76.481%,100%{opacity:.5}}
@keyframes l06d-p4{0%,58.814%{opacity:0;transform:translateX(0)}58.824%{opacity:1;transform:translateX(0)}72.941%{opacity:1;transform:translateX(-506px)}76.471%{opacity:1;transform:translateX(-506px)}76.481%,100%{opacity:0;transform:translateX(-506px)}}
.l06d-g4 rect,.l06d-g4 line,.l06d-g4 path:not(.l06d-gl){animation-name:l06d-g4}.l06d-p4{animation-name:l06d-p4}
@keyframes l06d-g5{0%,76.461%{opacity:.5}76.471%{opacity:1}88.235%{opacity:1}88.245%,100%{opacity:.5}}
.l06d-g5 rect,.l06d-g5 line,.l06d-g5 path:not(.l06d-gl){animation-name:l06d-g5}
@keyframes l06d-g6{0%,88.225%{opacity:.5}88.235%{opacity:1}100%{opacity:1}100.01%,100%{opacity:.5}}
.l06d-g6 rect,.l06d-g6 line,.l06d-g6 path:not(.l06d-gl){animation-name:l06d-g6}
</style>
<defs>
<marker id="l06d-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="l06d-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="l06d-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<line class="l06d-life" x1="110" y1="72" x2="110" y2="787"/>
<line class="l06d-life" x1="380" y1="72" x2="380" y2="787"/>
<line class="l06d-life" x1="650" y1="72" x2="650" y2="787"/>
<rect class="l06d-box" x="20" y="10" width="180" height="62" rx="10"/><text class="l06d-ttl" x="110" y="36">New hire</text><text class="l06d-sub" x="110" y="56">the real user</text>
<rect class="l06d-box" x="290" y="10" width="180" height="62" rx="10"/><text class="l06d-ttl" x="380" y="36">Attacker</text><text class="l06d-sub" x="380" y="56">holds the temporary password</text>
<rect class="l06d-hot" x="560" y="10" width="180" height="62" rx="10"/><text class="l06d-ttl" x="650" y="36">IdP</text><text class="l06d-sub" x="650" y="56">binds the authenticator</text>
<g class="l06d-g l06d-g0">
<text class="l06d-main l06d-badt" x="515" y="108">authenticates with the</text>
<text class="l06d-dim" x="515" y="124">temporary password alone</text>
<line class="l06d-bad" x1="394" y1="138" x2="636" y2="138" marker-end="url(#l06d-m-bad)"/>
<circle class="l06d-badge l06d-b-bad" cx="380" cy="138" r="12"/><text class="l06d-bt" x="380" y="142.5">1</text>
</g>
<g class="l06d-g l06d-g1">
<rect class="l06d-note-bad" x="509" y="172" width="241" height="116" rx="8"/>
<text class="l06d-nt" x="630" y="193">lower of the account's maximum</text>
<text class="l06d-nt" x="630" y="210">AAL and the new authenticator's:</text>
<text class="l06d-nt" x="630" y="227">an account with only AAL1</text>
<text class="l06d-nt" x="630" y="244">capability can bind an AAL2</text>
<text class="l06d-nt" x="630" y="261">authenticator after a password</text>
<text class="l06d-nt" x="630" y="278">alone</text>
</g>
<g class="l06d-g l06d-g2">
<text class="l06d-main l06d-badt" x="515" y="322">enrols its own</text>
<text class="l06d-dim" x="515" y="338">authenticator</text>
<line class="l06d-bad" x1="394" y1="352" x2="636" y2="352" marker-end="url(#l06d-m-bad)"/>
<circle class="l06d-badge l06d-b-bad" cx="380" cy="352" r="12"/><text class="l06d-bt" x="380" y="356.5">2</text>
</g>
<g class="l06d-g l06d-g3">
<rect class="l06d-note-bad" x="263" y="386" width="234" height="82" rx="8"/>
<text class="l06d-nt" x="380" y="407">a binding code to an already</text>
<text class="l06d-nt" x="380" y="424">authenticated endpoint does not</text>
<text class="l06d-nt" x="380" y="441">close this: the attacker is</text>
<text class="l06d-nt" x="380" y="458">that endpoint</text>
</g>
<g class="l06d-g l06d-g4">
<text class="l06d-main" x="380" y="502">notification</text>
<text class="l06d-dim" x="380" y="518">independent channel (lesson's reading)</text>
<line class="l06d-front" x1="636" y1="532" x2="124" y2="532" marker-end="url(#l06d-m-front)"/>
<circle class="l06d-badge l06d-b-front" cx="650" cy="532" r="12"/><text class="l06d-bt" x="650" y="536.5">3</text>
</g>
<g class="l06d-g l06d-g5">
<rect class="l06d-note" x="20" y="566" width="181" height="65" rx="8"/>
<text class="l06d-nt" x="110" y="587">makes a rogue enrolment</text>
<text class="l06d-nt" x="110" y="604">noticeable; does not</text>
<text class="l06d-nt" x="110" y="621">prevent one</text>
</g>
<g class="l06d-g l06d-g6">
<rect class="l06d-note-good" x="509" y="659" width="241" height="82" rx="8"/>
<text class="l06d-nt" x="630" y="680">this lesson's reading: bind only</text>
<text class="l06d-nt" x="630" y="697">on return of a single-use code</text>
<text class="l06d-nt" x="630" y="714">sent to contact details the</text>
<text class="l06d-nt" x="630" y="731">hire controls</text>
</g>
<circle class="l06d-pk l06d-p0 l06d-pkbad" cx="400" cy="138" r="5.5"/>
<circle class="l06d-pk l06d-p2 l06d-pkbad" cx="400" cy="352" r="5.5"/>
<circle class="l06d-pk l06d-p4" cx="630" cy="532" r="5.5"/>
<line class="l06d-front" x1="40" y1="815" x2="70" y2="815"/>
<text class="l06d-dim" x="78" y="819" style="text-anchor:start">notification</text>
<line class="l06d-bad" x1="188" y1="815" x2="218" y2="815"/>
<text class="l06d-dim" x="226" y="819" style="text-anchor:start">the attacker's step</text>
<rect class="l06d-note-good" x="381" y="807" width="22" height="16" rx="4"/>
<text class="l06d-dim" x="411" y="819" style="text-anchor:start">control</text>
</svg>
</div>
</div>
<!-- /diagram:enrolment-race -->

This diagram expands the enrolment race bullet above. Badges 1 to 3 number its own hops; the last note and the independent channel on hop 3 are this lesson's reading of SP 800-63A, not a quoted rule.

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
