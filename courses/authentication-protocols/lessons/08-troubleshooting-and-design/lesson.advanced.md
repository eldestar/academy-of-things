# Choosing a protocol and troubleshooting it

You design or build the service-provider side of identity integrations. This capstone adds no new SSO or provisioning protocol: LDAP and Kerberos appear only here, as legacy alternatives, and everything else is restated, so you can start here. SP and RP both mean the app side; this lesson says SP for any protocol. Facts checked 2026-10-06: standards were read from the primary text; confirm vendor figures in your tenant.

## The decision matrix and its edges

<!-- diagram:sp-checks -->
<div style="position:relative;margin:20px 0">
<input type="checkbox" id="l08d-pause" class="l08d-cb" /><label for="l08d-pause" class="l08d-btn"><span class="l08d-off">Pause animation</span><span class="l08d-on">Play animation</span></label>
<div class="l08d-box" style="overflow-x:auto">
<svg class="l08d-flow" viewBox="0 0 760 664" role="img" aria-labelledby="l08d-t l08d-d" style="width:100%;min-width:640px;max-width:800px;height:auto;display:block;margin:0 auto">
<title id="l08d-t">SAML assertion against OIDC ID token, side by side</title>
<desc id="l08d-d">Two columns, a SAML assertion over the POST binding and an OIDC ID token, compared across six rows. When to choose it: SAML when the SP speaks only SAML, OIDC when a client also needs API tokens. Audience: SAML checks that Audience lists the SP and that Recipient equals the ACS URL; OIDC checks that aud contains the client_id. Signature: the POST binding requires the assertion to be signed; for a JWT, verify with an algorithm allow-list set by the caller and reject none. Time: NotOnOrAfter allowing for skew, against exp. Also checked: InResponseTo and a replay set of assertion IDs for SAML; iss equal to the discovery issuer and nonce if sent for OIDC. Stable user key: IdP entity ID plus a persistent NameID for SAML, iss plus sub for OIDC. The diagram highlights each row in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
<style>
.l08d-box{fill:var(--panel);stroke:var(--border-strong);stroke-width:1.5}
.l08d-hot{fill:var(--panel);stroke:var(--accent);stroke-width:2.5}
.l08d-ttl{fill:var(--text);font:600 15px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l08d-sub{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l08d-life{stroke:var(--border-strong);stroke-width:1.5;stroke-dasharray:4 5}
.l08d-front{stroke:var(--accent);stroke-width:2;fill:none}
.l08d-back{stroke:var(--muted);stroke-width:2;stroke-dasharray:7 5;fill:none}
.l08d-bad{stroke:var(--bad);stroke-width:2;fill:none}
.l08d-main{fill:var(--text);font:600 13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l08d-badt{fill:var(--bad-text)}
.l08d-dim{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l08d-badge{fill:var(--accent)}
.l08d-b-back{fill:var(--muted)}
.l08d-b-bad{fill:var(--bad)}
.l08d-b-good{fill:var(--good)}
.l08d-bt{fill:var(--on-accent);font:700 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l08d-note{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l08d-note-good{fill:var(--good-bg);stroke:var(--good);stroke-width:1.5}
.l08d-note-bad{fill:var(--bad-bg);stroke:var(--bad);stroke-width:1.5}
.l08d-nt{fill:var(--body);font:12.5px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l08d-nest{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l08d-row{fill:var(--raised);stroke:var(--border-strong);stroke-width:1}
.l08d-ttlL{fill:var(--text);font:600 14px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l08d-subL{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l08d-dimL{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l08d-dimR{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:end}
.l08d-conn{stroke:var(--accent);stroke-width:1.5;fill:none}
.l08d-edge{stroke:var(--border-strong);stroke-width:1.75;fill:none}
.l08d-hl{fill:none;stroke:var(--accent);stroke-width:3}
.l08d-hle{stroke:var(--accent);stroke-width:3;fill:none}
.l08d-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:22s;animation-timing-function:linear;animation-iteration-count:infinite}
.l08d-pk.l08d-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.l08d-pk.l08d-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.l08d-g{opacity:.45;animation-duration:22s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.l08d-flow:hover .l08d-g,svg.l08d-flow:hover .l08d-pk{animation-play-state:paused}
.l08d-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.l08d-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.l08d-btn:hover{background:var(--hover)}
.l08d-cb:focus-visible + .l08d-btn{outline:2px solid var(--accent);outline-offset:2px}
.l08d-cb:checked + .l08d-btn .l08d-off,.l08d-cb:not(:checked) + .l08d-btn .l08d-on{display:none}
.l08d-cb:checked ~ .l08d-box .l08d-g,.l08d-cb:checked ~ .l08d-box .l08d-pk{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.l08d-g{animation:none;opacity:1}.l08d-pk{animation:none;display:none}.l08d-btn{display:none}}
@keyframes l08d-g0{0%{opacity:1}16.667%{opacity:1}16.677%,100%{opacity:.45}}
.l08d-g0{animation-name:l08d-g0}
@keyframes l08d-g1{0%,16.657%{opacity:.45}16.667%{opacity:1}33.333%{opacity:1}33.343%,100%{opacity:.45}}
.l08d-g1{animation-name:l08d-g1}
@keyframes l08d-g2{0%,33.323%{opacity:.45}33.333%{opacity:1}50%{opacity:1}50.01%,100%{opacity:.45}}
.l08d-g2{animation-name:l08d-g2}
@keyframes l08d-g3{0%,49.99%{opacity:.45}50%{opacity:1}66.667%{opacity:1}66.677%,100%{opacity:.45}}
.l08d-g3{animation-name:l08d-g3}
@keyframes l08d-g4{0%,66.657%{opacity:.45}66.667%{opacity:1}83.333%{opacity:1}83.343%,100%{opacity:.45}}
.l08d-g4{animation-name:l08d-g4}
@keyframes l08d-g5{0%,83.323%{opacity:.45}83.333%{opacity:1}100%{opacity:1}100.01%,100%{opacity:.45}}
.l08d-g5{animation-name:l08d-g5}
</style>
<defs>
<marker id="l08d-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="l08d-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="l08d-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<rect class="l08d-box" x="240" y="10" width="247" height="62" rx="10"/><text class="l08d-ttl" x="364" y="36">SAML assertion (POST)</text><text class="l08d-sub" x="364" y="56"></text>
<rect class="l08d-box" x="495" y="10" width="247" height="62" rx="10"/><text class="l08d-ttl" x="618" y="36">OIDC ID token</text><text class="l08d-sub" x="618" y="56"></text>
<g class="l08d-g l08d-g0">
<rect class="l08d-row" x="10" y="86" width="740" height="71" rx="8"/>
<text class="l08d-ttlL" x="24" y="112">Choose it when</text>
<text class="l08d-nt" x="364" y="134">the SP speaks only SAML</text>
<text class="l08d-nt" x="618" y="134">a client also needs API tokens</text>
</g>
<g class="l08d-g l08d-g1">
<rect class="l08d-row" x="10" y="165" width="740" height="86" rx="8"/>
<text class="l08d-ttlL" x="24" y="191">Audience</text>
<text class="l08d-nt" x="364" y="213">Audience lists the SP;</text>
<text class="l08d-nt" x="364" y="228">Recipient equals the ACS URL</text>
<text class="l08d-nt" x="618" y="213">aud contains the client_id</text>
</g>
<g class="l08d-g l08d-g2">
<rect class="l08d-row" x="10" y="259" width="740" height="86" rx="8"/>
<text class="l08d-ttlL" x="24" y="285">Signature</text>
<text class="l08d-nt" x="364" y="307">POST binding: the assertion</text>
<text class="l08d-nt" x="364" y="322">itself MUST be signed</text>
<text class="l08d-nt" x="618" y="307">verify with an alg allow-list</text>
<text class="l08d-nt" x="618" y="322">set by the caller; reject none</text>
</g>
<g class="l08d-g l08d-g3">
<rect class="l08d-row" x="10" y="353" width="740" height="71" rx="8"/>
<text class="l08d-ttlL" x="24" y="379">Time</text>
<text class="l08d-nt" x="364" y="401">NotOnOrAfter, allowing for skew</text>
<text class="l08d-nt" x="618" y="401">exp</text>
</g>
<g class="l08d-g l08d-g4">
<rect class="l08d-row" x="10" y="432" width="740" height="86" rx="8"/>
<text class="l08d-ttlL" x="24" y="458">Also checked</text>
<text class="l08d-nt" x="364" y="480">InResponseTo (absent when</text>
<text class="l08d-nt" x="364" y="495">unsolicited); replay set of IDs</text>
<text class="l08d-nt" x="618" y="480">iss equals the discovery issuer;</text>
<text class="l08d-nt" x="618" y="495">nonce, if the SP sent one</text>
</g>
<g class="l08d-g l08d-g5">
<rect class="l08d-row" x="10" y="526" width="740" height="86" rx="8"/>
<text class="l08d-ttlL" x="24" y="552">Stable user key</text>
<text class="l08d-nt" x="364" y="574">IdP entity ID plus a</text>
<text class="l08d-nt" x="364" y="589">persistent NameID</text>
<text class="l08d-nt" x="618" y="574">iss plus sub</text>
</g>
</svg>
</div>
</div>
<!-- /diagram:sp-checks -->

Read down each column to see what the SP does with each artefact. The SAML column is the POST-binding case. The table below adds the other tools and the limits of each.

| Need | Tool and the spec facts that decide it | Limits |
| --- | --- | --- |
| Browser SSO | SAML 2.0 Web SSO, the choice when the SP speaks only SAML. With the POST binding the assertion MUST be signed. The SP verifies signatures, `Recipient` against the ACS URL, `NotOnOrAfter` (allowing for skew) and `InResponseTo` (absent when unsolicited), and keeps used assertion IDs until `NotOnOrAfter` (plus any skew allowance you accept; lesson 2) to stop replay | Bearer `SubjectConfirmationData` carries `Recipient` and `NotOnOrAfter` and must not carry `NotBefore`; no account lifecycle |
| Sign-in for apps | OIDC, an identity layer on OAuth 2.0, the choice when a client also needs API tokens. The SP checks `iss` (exact match to the discovery issuer), `aud` (contains its `client_id`), the signature, `exp` and, if it sent one, `nonce`. For OIDC only `iss` plus `sub` is a stable user key | Scope-requested claims such as `email` are voluntary; email can be reused or change |
| Delegated API access | OAuth 2.0 with RFC 9700: exact redirect URI matching, PKCE required for public clients. Access tokens are bearer unless sender-constrained | Not authentication; JWT access tokens (RFC 9068) are validated locally |
| Lifecycle | SCIM 2.0: `userName` unique and case-insensitive, duplicate create answers 409 with `scimType` `uniqueness`, a deleted resource should not block re-creation | Pair it with SAML or OIDC, which do not handle leavers; the meaning of `active` is defined by the service provider |
| First-login accounts | JIT from SAML claims: creates and updates users | A fallback only: cannot delete or deactivate (Microsoft Learn) |
| Directory-bound apps | LDAP simple bind: DN plus password sent by the client; implementations must be able to protect it with TLS (StartTLS) | The app holds the user's password; bad credentials return `invalidCredentials` |
| One realm | Kerberos: KDC tickets, shared-secret cryptography, clocks loosely synchronized, per-server skew typically 5 minutes | Skew errors (KRB_AP_ERR_SKEW); its own exchanges, not redirects |

## Method and instruments

Reproduce, capture, decode, compare to config, change one thing. Instruments:
- **Browser**: Chrome's Preserve log or Firefox's Persist Logs keeps redirects visible. For a server-side app only front-channel traffic shows, because its token request (`grant_type`, `code`, `redirect_uri`, `client_id`) goes straight to the token endpoint; a browser-based client's token request also appears in the Network tab.
- **SAML**: SAML-tracer decodes. POST binding is base64 XML in a hidden `SAMLResponse` field; Redirect binding is DEFLATE, base64, then URL-encoding.
- **JWT**: three base64url parts. Decoding proves nothing; verify with an algorithm allow-list set by the caller (RFC 8725), and reject `none`. The `kid` header only hints which key; keys come from `jwks_uri`.
- **Logs**: Okta System Log (`GET /api/v1/logs`, `filter`, `q`; `outcome.result`, `outcome.reason`; `user.authentication.sso` is an SSO attempt, `user.session.start` a session issued; 90 days). Entra sign-in logs (7 days Free, 30 days P1/P2; AADSTS lookup at `login.microsoftonline.com/error`, codes change).
- **Shell**: curl (`application/scim+json`), `openssl x509 -enddate -fingerprint -checkend`, dig, an NTP offset query.

## Failure catalogue

<!-- diagram:mixup-defences -->
<div style="position:relative;margin:20px 0">
<input type="checkbox" id="l08f-pause" class="l08f-cb" /><label for="l08f-pause" class="l08f-btn"><span class="l08f-off">Pause animation</span><span class="l08f-on">Play animation</span></label>
<div class="l08f-box" style="overflow-x:auto">
<svg class="l08f-flow" viewBox="0 0 760 585" role="img" aria-labelledby="l08f-t l08f-d" style="width:100%;min-width:640px;max-width:800px;height:auto;display:block;margin:0 auto">
<title id="l08f-t">What stops an OAuth mix-up</title>
<desc id="l08f-d">Five candidate defences against mix-up, where the client sends the code to the attacker's token endpoint. Storing the issuer bound to each request and comparing it with iss on return (RFC 9207) is the defence. Distinct redirect URIs are a fallback only if other options are unavailable (RFC 9700). By the lesson's own reasoning from RFC 9700 4.4.1, an aud check on a returned token comes too late, exact redirect matching passes because the shared URI is the client's own, and PKCE is not a defence because the client sends its verifier to the attacker's token endpoint with the code. The diagram highlights each row in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
<style>
.l08f-box{fill:var(--panel);stroke:var(--border-strong);stroke-width:1.5}
.l08f-hot{fill:var(--panel);stroke:var(--accent);stroke-width:2.5}
.l08f-ttl{fill:var(--text);font:600 15px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l08f-sub{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l08f-life{stroke:var(--border-strong);stroke-width:1.5;stroke-dasharray:4 5}
.l08f-front{stroke:var(--accent);stroke-width:2;fill:none}
.l08f-back{stroke:var(--muted);stroke-width:2;stroke-dasharray:7 5;fill:none}
.l08f-bad{stroke:var(--bad);stroke-width:2;fill:none}
.l08f-main{fill:var(--text);font:600 13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l08f-badt{fill:var(--bad-text)}
.l08f-dim{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l08f-badge{fill:var(--accent)}
.l08f-b-back{fill:var(--muted)}
.l08f-b-bad{fill:var(--bad)}
.l08f-b-good{fill:var(--good)}
.l08f-bt{fill:var(--on-accent);font:700 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l08f-note{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l08f-note-good{fill:var(--good-bg);stroke:var(--good);stroke-width:1.5}
.l08f-note-bad{fill:var(--bad-bg);stroke:var(--bad);stroke-width:1.5}
.l08f-nt{fill:var(--body);font:12.5px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l08f-nest{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l08f-row{fill:var(--raised);stroke:var(--border-strong);stroke-width:1}
.l08f-ttlL{fill:var(--text);font:600 14px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l08f-subL{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l08f-dimL{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l08f-dimR{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:end}
.l08f-conn{stroke:var(--accent);stroke-width:1.5;fill:none}
.l08f-edge{stroke:var(--border-strong);stroke-width:1.75;fill:none}
.l08f-hl{fill:none;stroke:var(--accent);stroke-width:3}
.l08f-hle{stroke:var(--accent);stroke-width:3;fill:none}
.l08f-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:18s;animation-timing-function:linear;animation-iteration-count:infinite}
.l08f-pk.l08f-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.l08f-pk.l08f-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.l08f-g{opacity:.45;animation-duration:18s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.l08f-flow:hover .l08f-g,svg.l08f-flow:hover .l08f-pk{animation-play-state:paused}
.l08f-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.l08f-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.l08f-btn:hover{background:var(--hover)}
.l08f-cb:focus-visible + .l08f-btn{outline:2px solid var(--accent);outline-offset:2px}
.l08f-cb:checked + .l08f-btn .l08f-off,.l08f-cb:not(:checked) + .l08f-btn .l08f-on{display:none}
.l08f-cb:checked ~ .l08f-box .l08f-g,.l08f-cb:checked ~ .l08f-box .l08f-pk{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.l08f-g{animation:none;opacity:1}.l08f-pk{animation:none;display:none}.l08f-btn{display:none}}
@keyframes l08f-g0{0%{opacity:1}20%{opacity:1}20.01%,100%{opacity:.45}}
.l08f-g0{animation-name:l08f-g0}
@keyframes l08f-g1{0%,19.99%{opacity:.45}20%{opacity:1}40%{opacity:1}40.01%,100%{opacity:.45}}
.l08f-g1{animation-name:l08f-g1}
@keyframes l08f-g2{0%,39.99%{opacity:.45}40%{opacity:1}60%{opacity:1}60.01%,100%{opacity:.45}}
.l08f-g2{animation-name:l08f-g2}
@keyframes l08f-g3{0%,59.99%{opacity:.45}60%{opacity:1}80%{opacity:1}80.01%,100%{opacity:.45}}
.l08f-g3{animation-name:l08f-g3}
@keyframes l08f-g4{0%,79.99%{opacity:.45}80%{opacity:1}100%{opacity:1}100.01%,100%{opacity:.45}}
.l08f-g4{animation-name:l08f-g4}
</style>
<defs>
<marker id="l08f-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="l08f-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="l08f-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<rect class="l08f-box" x="240" y="10" width="502" height="62" rx="10"/><text class="l08f-ttl" x="491" y="36">Does it stop mix-up?</text><text class="l08f-sub" x="491" y="56">the client sends the code to the attacker's token endpoint</text>
<g class="l08f-g l08f-g0">
<rect class="l08f-row" x="10" y="86" width="740" height="86" rx="8"/>
<text class="l08f-ttlL" x="24" y="112">Store issuer, check iss</text>
<text class="l08f-subL" x="24" y="130">RFC 9207</text>
<circle cx="491" cy="108" r="10" style="fill:var(--good)"/><path d="M486.8,108.0 L489.6,111.4 L495.2,104.6" style="fill:none;stroke:var(--on-accent);stroke-width:2;stroke-linecap:round;stroke-linejoin:round"/>
<text class="l08f-nt" x="491" y="134">Issuer is bound to each request and compared</text>
<text class="l08f-nt" x="491" y="149">with iss on return</text>
</g>
<g class="l08f-g l08f-g1">
<rect class="l08f-row" x="10" y="180" width="740" height="86" rx="8"/>
<text class="l08f-ttlL" x="24" y="206">Distinct redirect URIs</text>
<text class="l08f-subL" x="24" y="224">RFC 9700</text>
<circle cx="491" cy="202" r="10" style="fill:var(--muted)"/><path d="M486.8,202.0 L495.2,202.0" style="fill:none;stroke:var(--on-accent);stroke-width:2;stroke-linecap:round;stroke-linejoin:round"/>
<text class="l08f-nt" x="491" y="228">A fallback, used only if other options</text>
<text class="l08f-nt" x="491" y="243">are unavailable</text>
</g>
<g class="l08f-g l08f-g2">
<rect class="l08f-row" x="10" y="274" width="740" height="71" rx="8"/>
<text class="l08f-ttlL" x="24" y="300">aud check on the token</text>
<text class="l08f-subL" x="24" y="318">our reasoning, RFC 9700 4.4.1</text>
<circle cx="491" cy="296" r="10" style="fill:var(--bad)"/><path d="M487.6,292.6 L494.4,299.4 M494.4,292.6 L487.6,299.4" style="fill:none;stroke:var(--on-accent);stroke-width:2;stroke-linecap:round;stroke-linejoin:round"/>
<text class="l08f-nt" x="491" y="322">Too late: that endpoint controls the token</text>
</g>
<g class="l08f-g l08f-g3">
<rect class="l08f-row" x="10" y="353" width="740" height="86" rx="8"/>
<text class="l08f-ttlL" x="24" y="379">Exact redirect matching</text>
<text class="l08f-subL" x="24" y="397">our reasoning, RFC 9700 4.4.1</text>
<circle cx="491" cy="375" r="10" style="fill:var(--bad)"/><path d="M487.6,371.6 L494.4,378.4 M494.4,371.6 L487.6,378.4" style="fill:none;stroke:var(--on-accent);stroke-width:2;stroke-linecap:round;stroke-linejoin:round"/>
<text class="l08f-nt" x="491" y="401">Passes: the shared URI is the client's own</text>
<text class="l08f-nt" x="491" y="416">registered one</text>
</g>
<g class="l08f-g l08f-g4">
<rect class="l08f-row" x="10" y="447" width="740" height="86" rx="8"/>
<text class="l08f-ttlL" x="24" y="473">PKCE</text>
<text class="l08f-subL" x="24" y="491">our reasoning, RFC 9700 4.4.1</text>
<circle cx="491" cy="469" r="10" style="fill:var(--bad)"/><path d="M487.6,465.6 L494.4,472.4 M494.4,465.6 L487.6,472.4" style="fill:none;stroke:var(--on-accent);stroke-width:2;stroke-linecap:round;stroke-linejoin:round"/>
<text class="l08f-nt" x="491" y="495">Not a defence: the client sends its verifier</text>
<text class="l08f-nt" x="491" y="510">to the attacker's token endpoint with the code</text>
</g>
<circle cx="48" cy="561" r="8" style="fill:var(--good)"/><path d="M44.6,561.0 L46.9,563.7 L51.4,558.3" style="fill:none;stroke:var(--on-accent);stroke-width:2;stroke-linecap:round;stroke-linejoin:round"/>
<text class="l08f-dim" x="64" y="565" style="text-anchor:start">the defence</text>
<circle cx="176" cy="561" r="8" style="fill:var(--muted)"/><path d="M172.6,561.0 L179.4,561.0" style="fill:none;stroke:var(--on-accent);stroke-width:2;stroke-linecap:round;stroke-linejoin:round"/>
<text class="l08f-dim" x="192" y="565" style="text-anchor:start">fallback only</text>
<circle cx="317" cy="561" r="8" style="fill:var(--bad)"/><path d="M314.3,558.3 L319.7,563.7 M319.7,558.3 L314.3,563.7" style="fill:none;stroke:var(--on-accent);stroke-width:2;stroke-linecap:round;stroke-linejoin:round"/>
<text class="l08f-dim" x="333" y="565" style="text-anchor:start">does not stop it</text>
</svg>
</div>
</div>
<!-- /diagram:mixup-defences -->

The top mark is the defence and the second is a fallback. The marks on the last three rows are the lesson's own reasoning from RFC 9700 4.4.1.

<!-- diagram:leaver-paths -->
<div style="position:relative;margin:20px 0">
<input type="checkbox" id="l08e-pause" class="l08e-cb" /><label for="l08e-pause" class="l08e-btn"><span class="l08e-off">Pause animation</span><span class="l08e-on">Play animation</span></label>
<div class="l08e-box" style="overflow-x:auto">
<svg class="l08e-flow" viewBox="0 0 921 323" role="img" aria-labelledby="l08e-t l08e-d" style="width:100%;min-width:640px;max-width:800px;height:auto;display:block;margin:0 auto">
<title id="l08e-t">A leaver keeps access: which path holds it</title>
<desc id="l08e-d">A tree over places a leaver's access can live. An established SP session is the SP's own, and the SP SHOULD discard its security context at SessionNotOnOrAfter. For a JWT checked locally, local validation never asks the IdP, so the token is good until exp. Separately, introspection (RFC 7662) reports whether a token is active, and revocation (RFC 7009) invalidates tokens from a grant. After SCIM sets active to false, the service provider defines what that means. The diagram highlights each path in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
<style>
.l08e-box{fill:var(--panel);stroke:var(--border-strong);stroke-width:1.5}
.l08e-hot{fill:var(--panel);stroke:var(--accent);stroke-width:2.5}
.l08e-ttl{fill:var(--text);font:600 15px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l08e-sub{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l08e-life{stroke:var(--border-strong);stroke-width:1.5;stroke-dasharray:4 5}
.l08e-front{stroke:var(--accent);stroke-width:2;fill:none}
.l08e-back{stroke:var(--muted);stroke-width:2;stroke-dasharray:7 5;fill:none}
.l08e-bad{stroke:var(--bad);stroke-width:2;fill:none}
.l08e-main{fill:var(--text);font:600 13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l08e-badt{fill:var(--bad-text)}
.l08e-dim{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l08e-badge{fill:var(--accent)}
.l08e-b-back{fill:var(--muted)}
.l08e-b-bad{fill:var(--bad)}
.l08e-b-good{fill:var(--good)}
.l08e-bt{fill:var(--on-accent);font:700 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l08e-note{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l08e-note-good{fill:var(--good-bg);stroke:var(--good);stroke-width:1.5}
.l08e-note-bad{fill:var(--bad-bg);stroke:var(--bad);stroke-width:1.5}
.l08e-nt{fill:var(--body);font:12.5px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l08e-nest{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l08e-row{fill:var(--raised);stroke:var(--border-strong);stroke-width:1}
.l08e-ttlL{fill:var(--text);font:600 14px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l08e-subL{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l08e-dimL{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l08e-dimR{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:end}
.l08e-conn{stroke:var(--accent);stroke-width:1.5;fill:none}
.l08e-edge{stroke:var(--border-strong);stroke-width:1.75;fill:none}
.l08e-hl{fill:none;stroke:var(--accent);stroke-width:3}
.l08e-hle{stroke:var(--accent);stroke-width:3;fill:none}
.l08e-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:18s;animation-timing-function:linear;animation-iteration-count:infinite}
.l08e-pk.l08e-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.l08e-pk.l08e-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.l08e-g{opacity:.45;animation-duration:18s;animation-timing-function:linear;animation-iteration-count:infinite}
.l08e-h{opacity:0;animation-duration:18s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.l08e-flow:hover .l08e-g,svg.l08e-flow:hover .l08e-pk,svg.l08e-flow:hover .l08e-h{animation-play-state:paused}
.l08e-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.l08e-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.l08e-btn:hover{background:var(--hover)}
.l08e-cb:focus-visible + .l08e-btn{outline:2px solid var(--accent);outline-offset:2px}
.l08e-cb:checked + .l08e-btn .l08e-off,.l08e-cb:not(:checked) + .l08e-btn .l08e-on{display:none}
.l08e-cb:checked ~ .l08e-box .l08e-g,.l08e-cb:checked ~ .l08e-box .l08e-pk,.l08e-cb:checked ~ .l08e-box .l08e-h{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.l08e-g{animation:none;opacity:1}.l08e-pk{animation:none;display:none}.l08e-h{animation:none;opacity:0}.l08e-btn{display:none}}
@keyframes l08e-h0{0%{opacity:1}20%{opacity:1}20.01%,100%{opacity:0}}
.l08e-h0{animation-name:l08e-h0}
@keyframes l08e-h1{0%,19.99%{opacity:0}20%{opacity:1}40%{opacity:1}40.01%,100%{opacity:0}}
.l08e-h1{animation-name:l08e-h1}
@keyframes l08e-h2{0%,39.99%{opacity:0}40%{opacity:1}60%{opacity:1}60.01%,100%{opacity:0}}
.l08e-h2{animation-name:l08e-h2}
@keyframes l08e-h3{0%,59.99%{opacity:0}60%{opacity:1}80%{opacity:1}80.01%,100%{opacity:0}}
.l08e-h3{animation-name:l08e-h3}
@keyframes l08e-h4{0%,79.99%{opacity:0}80%{opacity:1}100%{opacity:1}100.01%,100%{opacity:0}}
.l08e-h4{animation-name:l08e-h4}
</style>
<defs>
<marker id="l08e-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="l08e-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="l08e-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<path class="l08e-edge" d="M460,89 L460,118 L130,118 L130,144" marker-end="url(#l08e-m-front)"/>
<text class="l08e-dimL" x="136" y="134">SP session</text>
<path class="l08e-edge" d="M460,89 L460,118 L300,118 L300,144" marker-end="url(#l08e-m-front)"/>
<text class="l08e-dimL" x="308" y="134">JWT, checked locally</text>
<path class="l08e-edge" d="M460,89 L460,144" marker-end="url(#l08e-m-front)"/>
<text class="l08e-dimL" x="468" y="134">introspection</text>
<path class="l08e-edge" d="M460,89 L460,118 L632,118 L632,144" marker-end="url(#l08e-m-front)"/>
<text class="l08e-dimL" x="638" y="134">revocation</text>
<path class="l08e-edge" d="M460,89 L460,118 L802,118 L802,144" marker-end="url(#l08e-m-front)"/>
<text class="l08e-dimL" x="809" y="134">SCIM active false</text>
<rect class="l08e-note" x="48" y="147" width="162" height="116" rx="8"/><text class="l08e-nt" x="130" y="168">An established SP</text><text class="l08e-nt" x="130" y="185">session is the SP's</text><text class="l08e-nt" x="130" y="202">own; the SP SHOULD</text><text class="l08e-nt" x="130" y="219">discard its security</text><text class="l08e-nt" x="130" y="236">context at</text><text class="l08e-nt" x="130" y="253">SessionNotOnOrAfter</text>
<rect class="l08e-note" x="226" y="147" width="148" height="65" rx="8"/><text class="l08e-nt" x="300" y="168">Good until exp:</text><text class="l08e-nt" x="300" y="185">local validation</text><text class="l08e-nt" x="300" y="202">never asks the IdP</text>
<rect class="l08e-note" x="390" y="147" width="141" height="65" rx="8"/><text class="l08e-nt" x="461" y="168">RFC 7662: reports</text><text class="l08e-nt" x="461" y="185">whether a token</text><text class="l08e-nt" x="461" y="202">is active</text>
<rect class="l08e-note" x="548" y="147" width="168" height="48" rx="8"/><text class="l08e-nt" x="632" y="168">RFC 7009: invalidates</text><text class="l08e-nt" x="632" y="185">tokens from a grant</text>
<rect class="l08e-note" x="732" y="147" width="141" height="65" rx="8"/><text class="l08e-nt" x="802" y="168">The SP defines</text><text class="l08e-nt" x="802" y="185">what active false</text><text class="l08e-nt" x="802" y="202">means</text>
<rect class="l08e-box" x="400" y="24" width="121" height="65" rx="8"/><text class="l08e-main" x="460" y="45">Leaver still</text><text class="l08e-nt" x="460" y="62">has access:</text><text class="l08e-nt" x="460" y="79">what holds it?</text>
<g class="l08e-h l08e-h0">
<path class="l08e-hle" d="M460,89 L460,118 L130,118 L130,144" marker-end="url(#l08e-m-front)"/>
<rect class="l08e-hl" x="400" y="24" width="121" height="65" rx="8"/>
<rect class="l08e-hl" x="48" y="147" width="162" height="116" rx="8"/>
</g>
<g class="l08e-h l08e-h1">
<path class="l08e-hle" d="M460,89 L460,118 L300,118 L300,144" marker-end="url(#l08e-m-front)"/>
<rect class="l08e-hl" x="400" y="24" width="121" height="65" rx="8"/>
<rect class="l08e-hl" x="226" y="147" width="148" height="65" rx="8"/>
</g>
<g class="l08e-h l08e-h2">
<path class="l08e-hle" d="M460,89 L460,144" marker-end="url(#l08e-m-front)"/>
<rect class="l08e-hl" x="400" y="24" width="121" height="65" rx="8"/>
<rect class="l08e-hl" x="390" y="147" width="141" height="65" rx="8"/>
</g>
<g class="l08e-h l08e-h3">
<path class="l08e-hle" d="M460,89 L460,118 L632,118 L632,144" marker-end="url(#l08e-m-front)"/>
<rect class="l08e-hl" x="400" y="24" width="121" height="65" rx="8"/>
<rect class="l08e-hl" x="548" y="147" width="168" height="48" rx="8"/>
</g>
<g class="l08e-h l08e-h4">
<path class="l08e-hle" d="M460,89 L460,118 L802,118 L802,144" marker-end="url(#l08e-m-front)"/>
<rect class="l08e-hl" x="400" y="24" width="121" height="65" rx="8"/>
<rect class="l08e-hl" x="732" y="147" width="141" height="65" rx="8"/>
</g>
<line class="l08e-front" x1="40" y1="299" x2="70" y2="299"/>
<text class="l08e-dim" x="78" y="303" style="text-anchor:start">the path being traced</text>
</svg>
</div>
</div>
<!-- /diagram:leaver-paths -->

Each branch is a place a leaver's access can live. The session branch repeats the lesson's statement about an established SP session, which sits in the IdP-down question and is not tied there to a leaver. The introspection and revocation branches say what each mechanism does; nothing here says a given SP uses them.

| Symptom | Cause (the fact behind it) | First check |
| --- | --- | --- |
| SAML audience, recipient or destination error | `<Audience>` values are a disjunction and the condition holds only if the SP is a member; bearer `Recipient` must equal the ACS URL that received the Response | `Audience` vs the per-tenant entity ID; `Recipient` and `Destination` vs the ACS |
| SAML intermittent expiry | Windows are checked on the SP's clock subject to allowable skew (Profiles 4.1.4.3); for JWTs, RFC 7519 says leeway is usually no more than a few minutes | Window vs `date -u`; NTP offset |
| SAML signature fails or assertion unsigned | The SP verifies with the key it holds; metadata lists zero or more `KeyDescriptor` keys and may carry `validUntil`; POST binding requires the assertion itself signed, and Okta offers Response and Assertion signing as separate choices | Certificate fingerprint in the response vs the stored one; Assertion Signature setting |
| SAML assertion accepted twice | Bearer assertions must not be replayed; the SP keeps used IDs until `NotOnOrAfter` plus any skew allowance (lesson 2) | Is there a replay set |
| Duplicate accounts per login | `transient` NameIDs are temporary; `persistent` ones are pair-wise and, per SAML Core 8.3.7, must not appear in logs without controls | NameID `Format` |
| OAuth redirect error | Exact string match; the server must not redirect to an invalid URI | Request vs registered URI |
| `invalid_grant` | Code expired (10 minutes at most recommended), reused (the server SHOULD revoke tokens from it), `redirect_uri` differing from the request, other client, or PKCE verifier mismatch | Timing, double callback, verifier |
| Tokens sent to the wrong issuer | With two or more authorization servers, mix-up is possible: the client sends the code to the attacker's token endpoint, before any ID token exists. The defence is to store the issuer bound to each request and compare it with `iss` on return (RFC 9207); RFC 9700 treats distinct redirect URIs as a fallback, to be used only if other options are unavailable. An `aud` check on a returned token comes too late and that endpoint controls the token; exact redirect matching passes, because the shared URI is the client's own registered one; PKCE is not a defence, since the client sends its verifier to the attacker's token endpoint with the code (our reasoning from RFC 9700 4.4.1) | Stored issuer vs response `iss` |
| ID token rejected | `iss` must exactly equal the discovery issuer; `aud` must contain `client_id`; if a `nonce` was sent, the token must carry it and it must match | Decoded claims vs discovery |
| Unknown `kid` after rotation | `kid` selects a key within the JWK Set during rollover; the cache predates the new key | Refetch `jwks_uri` on an unfamiliar `kid` (OIDC Core 10.1.1); rate-limiting it is our advice, not spec text |
| Missing `email` | Scope claims are voluntary and may be in the ID token or only at UserInfo, depending on the provider and response type | `scope`; the ID token and UserInfo |
| SCIM 409, 400 or 404 | 409 duplicate `userName`; 400 carries a `scimType` such as `invalidPath`; 404 for a missing or deleted `id` | `GET /Users?filter=userName eq "..."` |
| Leaver keeps access | Local validation never asks the IdP, so a JWT is good until `exp`; time claims (`exp`, `nbf`, `iat`) are fixed at issuance and say nothing about later account state; introspection (RFC 7662) reports whether a token is active, commonly not expired and not revoked, and revocation (RFC 7009) invalidates tokens from a grant | Token lifetime vs deprovision path |
| TOTP, Kerberos or passkey fails | TOTP's recommended step is 30 seconds, with at most one step of delay advised; Kerberos has a skew limit; a passkey works only with its RP ID | Clock; RP ID vs hostname |

## Eight review questions

**Who issues** (`iss`, entity ID) and for whom? **Who validates**, exactly what? **What proves freshness** (windows, `exp`, `nonce` if sent, single-use codes, replay set)? **Leaver**: SP account, sessions, tokens? **What is logged**, retained how long? **Key rotation**: `kid`, `jwks_uri`, `KeyDescriptor`? **IdP down**: an established SP session is the SP's own, whose security context the SP SHOULD discard at `SessionNotOnOrAfter` (Profiles 4.1.4.3); new logins fail. **Blast radius**: what one key or token exposes.

## Review walkthrough: Acme Notes, a multi-IdP SaaS

Hypothetical: customers bring their own IdP over SAML or OIDC, plus SCIM and a JIT fallback. Findings:

| Finding | Why it matters | Fix |
| --- | --- | --- |
| Users matched by email | Email can be reused or change | Key on issuer plus subject, per tenant: `iss` plus `sub` for OIDC, the IdP entity ID plus a persistent NameID for SAML (lessons 1 and 2) |
| One OIDC redirect URI for every customer IdP | Mix-up risk | Bind issuer to the request and compare `iss` (RFC 9207); one URI per issuer only as a fallback |
| No replay set for assertion IDs | Captured POSTs replay inside the window | Store IDs until `NotOnOrAfter` plus any skew allowance |
| Library takes `alg` from the header | Algorithm confusion, `none` | Caller-set allow-list |
| JIT-only tenants | Leavers keep accounts | Offer SCIM; define `active` false to end sessions and revoke refresh tokens |

## Your task: decode and diagnose

All artefacts are invented samples. I ran the commands on 2026-10-06 (macOS, jq 1.7.1, OpenSSL 3.6.3); output after `# out:` is real, but `now_utc`, certificate dates, fingerprints and NTP offsets will differ for you.
```sh
T=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6InNhbXBsZS1rZXktMSJ9.eyJpc3MiOiJodHRwczovL2lkcC5leGFtcGxlLmNvbS9vYXV0aDIvc2FtcGxlIiwiYXVkIjoic2FtcGxlLWNsaWVudC1pZCIsInN1YiI6InVzZXItMDAwMSIsImlhdCI6MTc5MDAwMDAwMCwiZXhwIjoxNzkwMDAwMzAwLCJub25jZSI6InNhbXBsZS1ub25jZSJ9.ckGCV5aUn8_ZwBeTloXo0f8RbIphiOUgsMNSwTUXlLE
echo "$T" | jq -Rc 'split(".")[0:2][] | gsub("-";"+") | gsub("_";"/") | @base64d | fromjson'
jq -nc '{exp_utc: (1790000300|todate), now_utc: (now|floor|todate)}'
SI=${T%.*}; printf '%s' "$SI" | openssl dgst -sha256 -hmac 'sample-secret-not-real' -binary | openssl base64 -A | tr '+/' '-_' | tr -d '='; echo; echo "${T##*.}"
# out: {"alg":"HS256","typ":"JWT","kid":"sample-key-1"}
# out: {"iss":"https://idp.example.com/oauth2/sample","aud":"sample-client-id","sub":"user-0001","iat":1790000000,"exp":1790000300,"nonce":"sample-nonce"}
# out: {"exp_utc":"2026-09-21T14:18:20Z","now_utc":"2026-10-06T05:23:23Z"}
# out: ckGCV5aUn8_ZwBeTloXo0f8RbIphiOUgsMNSwTUXlLE
# out: ckGCV5aUn8_ZwBeTloXo0f8RbIphiOUgsMNSwTUXlLE
```
1. **Expired JWT.** The signature recomputes (HS256, invented key), so the token is untampered, yet `exp` is long past: valid signature, expired token. A real IdP would use an asymmetric key, so you would verify against its `jwks_uri`.

```sh
cat > resp.xml <<'EOF'
<samlp:Response xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol" xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion" Destination="https://app.example.com/saml/acs"><saml:Assertion><saml:Subject><saml:NameID Format="urn:oasis:names:tc:SAML:2.0:nameid-format:transient">_7f3c91</saml:NameID><saml:SubjectConfirmation Method="urn:oasis:names:tc:SAML:2.0:cm:bearer"><saml:SubjectConfirmationData Recipient="https://app.example.com/saml/acs" NotOnOrAfter="2026-10-05T09:05:00Z"/></saml:SubjectConfirmation></saml:Subject><saml:Conditions NotBefore="2026-10-05T08:59:30Z" NotOnOrAfter="2026-10-05T09:05:00Z"><saml:AudienceRestriction><saml:Audience>https://app.example.com/saml/metadata</saml:Audience></saml:AudienceRestriction></saml:Conditions></saml:Assertion></samlp:Response>
EOF
grep -oE '(Destination|Recipient|NotBefore|NotOnOrAfter)="[^"]*"|<saml:Audience>[^<]*' resp.xml
# out: Destination="https://app.example.com/saml/acs"
# out: Recipient="https://app.example.com/saml/acs"
# out: NotOnOrAfter="2026-10-05T09:05:00Z"
# out: NotBefore="2026-10-05T08:59:30Z"
# out: NotOnOrAfter="2026-10-05T09:05:00Z"
# out: <saml:Audience>https://app.example.com/saml/metadata
```
2. **Audience mismatch.** The sample SP's entity ID is `https://app.example.com/saml`, its ACS URL `https://app.example.com/saml/acs`. `Destination` and `Recipient` match; `Audience` does not. The window is long past, so replaying this capture fails on time too; `NotBefore` sits in `Conditions`, not in the confirmation data, as required.

Save this mock SCIM server (sample: case-insensitive unique `userName`, no auth, ignores `?filter`) as `mock.py` and run `python3 mock.py &`:

```python
import json, http.server; U = {}
class H(http.server.BaseHTTPRequestHandler):
    def out(s, c, b): s.send_response(c); s.send_header("Content-Type", "application/scim+json"); s.end_headers(); s.wfile.write(json.dumps(b).encode() + b"\n")
    def do_POST(s):
        u = json.loads(s.rfile.read(int(s.headers["Content-Length"]))); k = u["userName"].lower()
        if k in U: s.out(409, {"schemas": ["urn:ietf:params:scim:api:messages:2.0:Error"], "status": "409", "scimType": "uniqueness", "detail": "userName already in use"})
        else: U[k] = {**u, "id": "sample-id-%d" % (len(U) + 1)}; s.out(201, U[k])
    def do_GET(s): s.out(200, {"Resources": list(U.values())})
    def log_message(s, *a): pass
http.server.HTTPServer(("127.0.0.1", 8731), H).serve_forever()
```
```sh
B=http://127.0.0.1:8731/scim/v2/Users; H='Content-Type: application/scim+json'
curl -s -X POST $B -H "$H" -d '{"userName":"alice@example.com"}' >/dev/null
curl -si -X POST $B -H "$H" -d '{"userName":"Alice@Example.com","externalId":"hr-9001"}' | sed -n '1p;$p'
curl -s $B
# out: HTTP/1.0 409 Conflict
# out: {"schemas": ["urn:ietf:params:scim:api:messages:2.0:Error"], "status": "409", "scimType": "uniqueness", "detail": "userName already in use"}
# out: {"Resources": [{"userName": "alice@example.com", "id": "sample-id-1"}]}
```
3. **SCIM 409.** A record with no `externalId` already holds the name, which suggests a non-sync path created it. Correlate by `userName`, set `externalId`, never delete. Stop the mock with `kill %1`. A real server must support the `userName eq` filter. Last, certificates, clocks and DNS on a throwaway certificate; do not add `-S` or `-s` to `sntp`, which set the system clock.

```sh
openssl req -x509 -newkey rsa:2048 -nodes -keyout k.pem -out c.pem -days 1 -subj "/CN=sample-idp-signing" 2>/dev/null
openssl x509 -in c.pem -noout -enddate -fingerprint -sha256; openssl x509 -in c.pem -noout -checkend 172800 >/dev/null || echo "expires within 48h"
sntp pool.ntp.org; dig +short example.com A | head -1
# out: notAfter=Oct  7 13:11:17 2026 GMT
# out: sha256 Fingerprint=90:4C:25:98:69:C2:B8:8B:75:AD:A3:40:2D:81:23:58:22:9C:77:30:07:DD:41:BE:B3:09:B3:BC:37:F7:22:03
# out: expires within 48h
# out: +0.088845 +/- 0.020725 pool.ntp.org 99.28.14.242
# out: 104.20.23.154
```
