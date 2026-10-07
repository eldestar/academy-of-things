# Choosing a protocol and troubleshooting it

You have configured SAML and OIDC apps in Okta. This capstone turns that into a decision guide and a debugging routine. It adds no new SSO or provisioning protocol: LDAP and Kerberos appear only here, as legacy alternatives, and everything else is restated so you can start here. SP and RP both mean the app side of a sign-in; this lesson says SP for any protocol. Facts checked 2026-10-06; confirm vendor figures in your own tenant.

## Which tool for which job

<!-- diagram:which-tool -->
<div style="position:relative;margin:20px 0">
<input type="checkbox" id="l08a-pause" class="l08a-cb" /><label for="l08a-pause" class="l08a-btn"><span class="l08a-off">Pause animation</span><span class="l08a-on">Play animation</span></label>
<div class="l08a-box" style="overflow-x:auto">
<svg class="l08a-flow" viewBox="0 0 760 521" role="img" aria-labelledby="l08a-t l08a-d" style="width:100%;min-width:640px;max-width:800px;height:auto;display:block;margin:0 auto">
<title id="l08a-t">SSO and lifecycle are separate problems</title>
<desc id="l08a-d">Four tools against three jobs. SAML 2.0 signs a user in and cannot manage the account lifecycle. OIDC signs a user in through an ID token and cannot create or remove accounts. SCIM 2.0 signs no one in, provisions accounts over HTTP and JSON, and deactivates by setting active to false, though the service provider decides what that means. JIT provisioning creates the user from the claims in the SAML token but cannot delete or deactivate. The diagram highlights each row in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
<style>
.l08a-box{fill:var(--panel);stroke:var(--border-strong);stroke-width:1.5}
.l08a-hot{fill:var(--panel);stroke:var(--accent);stroke-width:2.5}
.l08a-ttl{fill:var(--text);font:600 15px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l08a-sub{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l08a-life{stroke:var(--border-strong);stroke-width:1.5;stroke-dasharray:4 5}
.l08a-front{stroke:var(--accent);stroke-width:2;fill:none}
.l08a-back{stroke:var(--muted);stroke-width:2;stroke-dasharray:7 5;fill:none}
.l08a-bad{stroke:var(--bad);stroke-width:2;fill:none}
.l08a-main{fill:var(--text);font:600 13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l08a-badt{fill:var(--bad-text)}
.l08a-dim{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l08a-badge{fill:var(--accent)}
.l08a-b-back{fill:var(--muted)}
.l08a-b-bad{fill:var(--bad)}
.l08a-b-good{fill:var(--good)}
.l08a-bt{fill:var(--on-accent);font:700 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l08a-note{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l08a-note-good{fill:var(--good-bg);stroke:var(--good);stroke-width:1.5}
.l08a-note-bad{fill:var(--bad-bg);stroke:var(--bad);stroke-width:1.5}
.l08a-nt{fill:var(--body);font:12.5px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l08a-nest{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l08a-row{fill:var(--raised);stroke:var(--border-strong);stroke-width:1}
.l08a-ttlL{fill:var(--text);font:600 14px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l08a-subL{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l08a-dimL{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l08a-dimR{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:end}
.l08a-conn{stroke:var(--accent);stroke-width:1.5;fill:none}
.l08a-edge{stroke:var(--border-strong);stroke-width:1.75;fill:none}
.l08a-hl{fill:none;stroke:var(--accent);stroke-width:3}
.l08a-hle{stroke:var(--accent);stroke-width:3;fill:none}
.l08a-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:16s;animation-timing-function:linear;animation-iteration-count:infinite}
.l08a-pk.l08a-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.l08a-pk.l08a-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.l08a-g{opacity:.45;animation-duration:16s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.l08a-flow:hover .l08a-g,svg.l08a-flow:hover .l08a-pk{animation-play-state:paused}
.l08a-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.l08a-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.l08a-btn:hover{background:var(--hover)}
.l08a-cb:focus-visible + .l08a-btn{outline:2px solid var(--accent);outline-offset:2px}
.l08a-cb:checked + .l08a-btn .l08a-off,.l08a-cb:not(:checked) + .l08a-btn .l08a-on{display:none}
.l08a-cb:checked ~ .l08a-box .l08a-g,.l08a-cb:checked ~ .l08a-box .l08a-pk{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.l08a-g{animation:none;opacity:1}.l08a-pk{animation:none;display:none}.l08a-btn{display:none}}
@keyframes l08a-g0{0%{opacity:1}25%{opacity:1}25.01%,100%{opacity:.45}}
.l08a-g0{animation-name:l08a-g0}
@keyframes l08a-g1{0%,24.99%{opacity:.45}25%{opacity:1}50%{opacity:1}50.01%,100%{opacity:.45}}
.l08a-g1{animation-name:l08a-g1}
@keyframes l08a-g2{0%,49.99%{opacity:.45}50%{opacity:1}75%{opacity:1}75.01%,100%{opacity:.45}}
.l08a-g2{animation-name:l08a-g2}
@keyframes l08a-g3{0%,74.99%{opacity:.45}75%{opacity:1}100%{opacity:1}100.01%,100%{opacity:.45}}
.l08a-g3{animation-name:l08a-g3}
</style>
<defs>
<marker id="l08a-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="l08a-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="l08a-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<rect class="l08a-box" x="240" y="10" width="162" height="62" rx="10"/><text class="l08a-ttl" x="321" y="36">Signs a user in</text><text class="l08a-sub" x="321" y="56"></text>
<rect class="l08a-box" x="410" y="10" width="162" height="62" rx="10"/><text class="l08a-ttl" x="491" y="36">Creates accounts</text><text class="l08a-sub" x="491" y="56"></text>
<rect class="l08a-box" x="580" y="10" width="162" height="62" rx="10"/><text class="l08a-ttl" x="661" y="36">Removes</text><text class="l08a-sub" x="661" y="56">or deactivates</text>
<g class="l08a-g l08a-g0">
<rect class="l08a-row" x="10" y="86" width="740" height="86" rx="8"/>
<text class="l08a-ttlL" x="24" y="112">SAML 2.0</text>
<circle cx="321" cy="108" r="10" style="fill:var(--good)"/><path d="M316.8,108.0 L319.6,111.4 L325.2,104.6" style="fill:none;stroke:var(--on-accent);stroke-width:2;stroke-linecap:round;stroke-linejoin:round"/>
<text class="l08a-nt" x="321" y="134">POST binding: the</text>
<text class="l08a-nt" x="321" y="149">assertion must be signed</text>
<circle cx="491" cy="108" r="10" style="fill:var(--bad)"/><path d="M487.6,104.6 L494.4,111.4 M494.4,104.6 L487.6,111.4" style="fill:none;stroke:var(--on-accent);stroke-width:2;stroke-linecap:round;stroke-linejoin:round"/>
<text class="l08a-nt" x="491" y="134">cannot manage the</text>
<text class="l08a-nt" x="491" y="149">account lifecycle</text>
<circle cx="661" cy="108" r="10" style="fill:var(--bad)"/><path d="M657.6,104.6 L664.4,111.4 M664.4,104.6 L657.6,111.4" style="fill:none;stroke:var(--on-accent);stroke-width:2;stroke-linecap:round;stroke-linejoin:round"/>
</g>
<g class="l08a-g l08a-g1">
<rect class="l08a-row" x="10" y="180" width="740" height="86" rx="8"/>
<text class="l08a-ttlL" x="24" y="206">OIDC</text>
<circle cx="321" cy="202" r="10" style="fill:var(--good)"/><path d="M316.8,202.0 L319.6,205.4 L325.2,198.6" style="fill:none;stroke:var(--on-accent);stroke-width:2;stroke-linecap:round;stroke-linejoin:round"/>
<text class="l08a-nt" x="321" y="228">the app validates an</text>
<text class="l08a-nt" x="321" y="243">ID token (a JWT)</text>
<circle cx="491" cy="202" r="10" style="fill:var(--bad)"/><path d="M487.6,198.6 L494.4,205.4 M494.4,198.6 L487.6,205.4" style="fill:none;stroke:var(--on-accent);stroke-width:2;stroke-linecap:round;stroke-linejoin:round"/>
<text class="l08a-nt" x="491" y="228">cannot create or</text>
<text class="l08a-nt" x="491" y="243">remove accounts</text>
<circle cx="661" cy="202" r="10" style="fill:var(--bad)"/><path d="M657.6,198.6 L664.4,205.4 M664.4,198.6 L657.6,205.4" style="fill:none;stroke:var(--on-accent);stroke-width:2;stroke-linecap:round;stroke-linejoin:round"/>
<text class="l08a-nt" x="661" y="228">cannot remove</text>
<text class="l08a-nt" x="661" y="243">accounts</text>
</g>
<g class="l08a-g l08a-g2">
<rect class="l08a-row" x="10" y="274" width="740" height="101" rx="8"/>
<text class="l08a-ttlL" x="24" y="300">SCIM 2.0</text>
<circle cx="321" cy="296" r="10" style="fill:var(--bad)"/><path d="M317.6,292.6 L324.4,299.4 M324.4,292.6 L317.6,299.4" style="fill:none;stroke:var(--on-accent);stroke-width:2;stroke-linecap:round;stroke-linejoin:round"/>
<text class="l08a-nt" x="321" y="322">signs no one in</text>
<circle cx="491" cy="296" r="10" style="fill:var(--good)"/><path d="M486.8,296.0 L489.6,299.4 L495.2,292.6" style="fill:none;stroke:var(--on-accent);stroke-width:2;stroke-linecap:round;stroke-linejoin:round"/>
<text class="l08a-nt" x="491" y="322">HTTP/JSON</text>
<text class="l08a-nt" x="491" y="337">provisioning</text>
<circle cx="661" cy="296" r="10" style="fill:var(--muted)"/><path d="M656.8,296.0 L665.2,296.0" style="fill:none;stroke:var(--on-accent);stroke-width:2;stroke-linecap:round;stroke-linejoin:round"/>
<text class="l08a-nt" x="661" y="322">sets active to false;</text>
<text class="l08a-nt" x="661" y="337">the SP defines what</text>
<text class="l08a-nt" x="661" y="352">that means</text>
</g>
<g class="l08a-g l08a-g3">
<rect class="l08a-row" x="10" y="383" width="740" height="86" rx="8"/>
<text class="l08a-ttlL" x="24" y="409">JIT provisioning</text>
<circle cx="491" cy="405" r="10" style="fill:var(--good)"/><path d="M486.8,405.0 L489.6,408.4 L495.2,401.6" style="fill:none;stroke:var(--on-accent);stroke-width:2;stroke-linecap:round;stroke-linejoin:round"/>
<text class="l08a-nt" x="491" y="431">from the claims in</text>
<text class="l08a-nt" x="491" y="446">the SAML token</text>
<circle cx="661" cy="405" r="10" style="fill:var(--bad)"/><path d="M657.6,401.6 L664.4,408.4 M664.4,401.6 L657.6,408.4" style="fill:none;stroke:var(--on-accent);stroke-width:2;stroke-linecap:round;stroke-linejoin:round"/>
<text class="l08a-nt" x="661" y="431">cannot delete or</text>
<text class="l08a-nt" x="661" y="446">deactivate</text>
</g>
<circle cx="48" cy="497" r="8" style="fill:var(--good)"/><path d="M44.6,497.0 L46.9,499.7 L51.4,494.3" style="fill:none;stroke:var(--on-accent);stroke-width:2;stroke-linecap:round;stroke-linejoin:round"/>
<text class="l08a-dim" x="64" y="501" style="text-anchor:start">does this</text>
<circle cx="163" cy="497" r="8" style="fill:var(--muted)"/><path d="M159.6,497.0 L166.4,497.0" style="fill:none;stroke:var(--on-accent);stroke-width:2;stroke-linecap:round;stroke-linejoin:round"/>
<text class="l08a-dim" x="179" y="501" style="text-anchor:start">does this, with a catch</text>
<circle cx="368" cy="497" r="8" style="fill:var(--bad)"/><path d="M365.3,494.3 L370.7,499.7 M370.7,494.3 L365.3,499.7" style="fill:none;stroke:var(--on-accent);stroke-width:2;stroke-linecap:round;stroke-linejoin:round"/>
<text class="l08a-dim" x="384" y="501" style="text-anchor:start">cannot do this</text>
</svg>
</div>
</div>
<!-- /diagram:which-tool -->

Read across each row: SAML and OIDC prove who signed in now, SCIM decides whether the account exists and is active, and JIT creates and updates the user from the token's claims but cannot delete or deactivate. A SAML app with only JIT leaves a leaver's account alive in the app, and SCIM's catch is that the SP decides what active false means. The empty cell means this lesson does not rate JIT provisioning on signing in. The table below adds OAuth 2.0, LDAP and Kerberos.

| Need | Right tool | What it cannot do |
| --- | --- | --- |
| Browser SSO to a SAML app | SAML 2.0: the IdP sends a Response whose assertion names an audience and a validity window; with the POST binding the assertion must be signed | Manage the account's lifecycle; it signs a user in |
| Sign-in for a web or mobile app | OIDC: an identity layer on OAuth 2.0; the app validates an ID token (a JWT) | Create or remove accounts |
| An app calling an API for a user | OAuth 2.0: limited access to an HTTP service through an access token, usually a bearer token that any holder can use | Say who signed in; that is what OIDC adds |
| Account create, update, deactivate | SCIM 2.0: an HTTP/JSON provisioning protocol; deactivation sets `active` to false | Sign anyone in |
| Account created at first sign-in, no connector | JIT provisioning: the SP creates and updates the user from the claims in the SAML token | Delete or deactivate the user (Microsoft Learn) |
| A legacy app that only knows directories | LDAP simple bind: the client sends a DN and a password, so the app handles the password; implementations must be able to protect it with TLS (StartTLS) | Keep the password away from the app |
| Clients and services in one Kerberos realm | Kerberos: tickets from a KDC using shared-secret cryptography; clocks must be loosely synchronized, typically within 5 minutes | Act as a browser redirect protocol; it is its own client, KDC and service exchange |

SSO and lifecycle are separate problems. SAML or OIDC prove who signed in now; SCIM decides whether the account exists and is active. A SAML app with only JIT leaves a leaver's account alive in the app.

## A method that works on every protocol

**Reproduce** with one user, one app and a private window, noting whether the login began at the app (SP-initiated) or at the Okta tile (IdP-initiated). **Capture** what crossed the wire, **decode** it, **compare** every identifier character for character with the configuration, then **change one thing**, retest and write it down.

- **Browser capture**: Chrome DevTools has a Preserve log checkbox and Firefox calls it Persist Logs; without it, redirects wipe the Network list. In the code flow the token request goes from the client application straight to the token endpoint, so for a server-side app it never appears in the browser.
- **SAML**: the SAML-tracer extension (Firefox, Chrome/Edge) decodes messages. The POST binding carries base64 XML in a hidden form field named `SAMLResponse`; the Redirect binding uses DEFLATE, then base64, then URL-encoding.
- **JWT**: three base64url parts joined by dots; decode offline with jq (lab below). Decoding is not validating, and a bearer token pasted into an online decoder is a token you gave away.
- **Logs**: Okta's System Log is `GET /api/v1/logs` with `filter`, `q`, `since`; without `since` it covers only the 7 days before `until` (which defaults to now), so set `since` for a longer window; events carry `eventType`, `outcome.result` and `outcome.reason`. `user.session.start` means Okta issued a session to an authenticating user; `user.authentication.sso` is an SSO attempt to an app; separately from that default window, data older than 90 days is never returned. Entra sign-in logs are kept 7 days on Free and 30 days on P1 and P2; look an AADSTS code up at `login.microsoftonline.com/error`, and never code against codes, which Microsoft says change.
- **curl** for token and SCIM endpoints (SCIM media type `application/scim+json`), **openssl** for certificates, **dig** for DNS, an NTP query for clock offset.

## Failure catalogue

| Symptom | Likely cause (the fact behind it) | First check |
| --- | --- | --- |
| SAML: audience error | The assertion's `<Audience>` must include the SP's entity ID; the condition is valid only if the SP is a listed audience | Decoded `Audience` vs the entity ID (Okta: Audience URI (SP Entity ID)) |
| SAML: ACS, recipient or reply-address error (Entra AADSTS50011) | `Recipient` in the bearer confirmation must equal the ACS URL that received the Response | `Recipient` and `Destination` vs the configured Single sign-on URL |
| SAML: expired or not yet valid, intermittent | `NotBefore` and `NotOnOrAfter` are checked on the SP's clock, subject to allowable skew | Decoded window vs `date -u` on the SP; NTP offset |
| SAML: signature fails after an IdP change | The SP verifies with the key it holds; IdP metadata lists the signing keys; certificates have a notAfter date | `openssl x509 -fingerprint -enddate` vs the SP's copy |
| SAML: login works, empty or duplicate account | A `transient` NameID is opaque and temporary; `unspecified` leaves its meaning to the implementation | NameID `Format` vs what the SP maps (Okta: Name ID format) |
| OAuth: error page at the IdP, never back to the app | `redirect_uri` is compared by exact string; the server must not redirect to an invalid one | Request's `redirect_uri` vs registered: scheme, host, path, trailing slash |
| `invalid_grant` or `invalid_client` at the token endpoint | Code expired (10 minutes at most recommended), reused, redirect URI differing from the first request, other client, or wrong PKCE verifier; or client authentication failed | Seconds from redirect to token call; callback fired twice; client ID, secret and method via curl |
| API 401 `invalid_token` or 403 `insufficient_scope` | 401: token expired, revoked or malformed. 403: valid token, privileges too low | Decode `exp` and `scope` |
| ID token rejected, or unknown `kid` after rotation | `iss` must equal the discovery `issuer` exactly and `aud` must contain the app's `client_id`; keys come from `jwks_uri` and `kid` picks the key during rollover | Decoded claims vs `/.well-known/openid-configuration`; header `kid` vs the JWK Set |
| `email` or name missing | Claims arrive via the `email` and `profile` scopes; OIDC Core returns them from UserInfo when an access token is issued, but some providers also put them in the ID token, so they may be in either place | Requested `scope`; check the ID token and call UserInfo |
| SCIM 409 on create | `userName` is unique and case-insensitive; the answer is 409 with `scimType` `uniqueness` | `GET /Users?filter=userName eq "..."` |
| Leaver can still work | SCIM only sets `active`, and the service provider decides what that means, so many apps do not end sessions on their own; a JWT checked locally stays good until `exp`; a SAML SP SHOULD discard its security context at `SessionNotOnOrAfter` if sent | Session and token lifetime in the SP |
| TOTP or Kerberos fails for one user | RFC 6238 recommends 30-second TOTP steps and at most one step of delay; Kerberos rejects skew beyond its limit (KRB_AP_ERR_SKEW) | The device's clock |
| Passkey not offered | A passkey works only for the RP ID it was registered with, which must be the site's domain or a registrable parent domain, never a public suffix such as `com` | Hostname vs RP ID |

## The Okta admin's checklist

Incident: after editing a SAML app, thirty users get an audience error. Written from the docs, not run against a live tenant.

<!-- diagram:audience-error-checklist -->
<div style="position:relative;margin:20px 0">
<input type="checkbox" id="l08c-pause" class="l08c-cb" /><label for="l08c-pause" class="l08c-btn"><span class="l08c-off">Pause animation</span><span class="l08c-on">Play animation</span></label>
<div class="l08c-box" style="overflow-x:auto">
<svg class="l08c-flow" viewBox="0 0 760 395" role="img" aria-labelledby="l08c-t l08c-d" style="width:100%;min-width:640px;max-width:800px;height:auto;display:block;margin:0 auto">
<title id="l08c-t">The Okta admin's first two checks after an audience error</title>
<desc id="l08c-d">A decision tree for the incident in the lesson, where thirty users get an audience error after a SAML app is edited. Start with the System Log and read outcome.result and outcome.reason. If Okta issued the assertion successfully, the SP raised the audience error, so ask the SP owner for the SP's log. Otherwise, compare the decoded response with the app's fields, using one failing login captured with SAML-tracer: Destination and Recipient against the Single sign-on URL, Audience against the Audience URI (SP Entity ID), and NameID against the Name ID format. Written from the docs, not run against a live tenant. The diagram highlights each path in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
<style>
.l08c-box{fill:var(--panel);stroke:var(--border-strong);stroke-width:1.5}
.l08c-hot{fill:var(--panel);stroke:var(--accent);stroke-width:2.5}
.l08c-ttl{fill:var(--text);font:600 15px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l08c-sub{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l08c-life{stroke:var(--border-strong);stroke-width:1.5;stroke-dasharray:4 5}
.l08c-front{stroke:var(--accent);stroke-width:2;fill:none}
.l08c-back{stroke:var(--muted);stroke-width:2;stroke-dasharray:7 5;fill:none}
.l08c-bad{stroke:var(--bad);stroke-width:2;fill:none}
.l08c-main{fill:var(--text);font:600 13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l08c-badt{fill:var(--bad-text)}
.l08c-dim{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l08c-badge{fill:var(--accent)}
.l08c-b-back{fill:var(--muted)}
.l08c-b-bad{fill:var(--bad)}
.l08c-b-good{fill:var(--good)}
.l08c-bt{fill:var(--on-accent);font:700 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l08c-note{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l08c-note-good{fill:var(--good-bg);stroke:var(--good);stroke-width:1.5}
.l08c-note-bad{fill:var(--bad-bg);stroke:var(--bad);stroke-width:1.5}
.l08c-nt{fill:var(--body);font:12.5px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l08c-nest{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l08c-row{fill:var(--raised);stroke:var(--border-strong);stroke-width:1}
.l08c-ttlL{fill:var(--text);font:600 14px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l08c-subL{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l08c-dimL{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l08c-dimR{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:end}
.l08c-conn{stroke:var(--accent);stroke-width:1.5;fill:none}
.l08c-edge{stroke:var(--border-strong);stroke-width:1.75;fill:none}
.l08c-hl{fill:none;stroke:var(--accent);stroke-width:3}
.l08c-hle{stroke:var(--accent);stroke-width:3;fill:none}
.l08c-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:18s;animation-timing-function:linear;animation-iteration-count:infinite}
.l08c-pk.l08c-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.l08c-pk.l08c-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.l08c-g{opacity:.45;animation-duration:18s;animation-timing-function:linear;animation-iteration-count:infinite}
.l08c-h{opacity:0;animation-duration:18s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.l08c-flow:hover .l08c-g,svg.l08c-flow:hover .l08c-pk,svg.l08c-flow:hover .l08c-h{animation-play-state:paused}
.l08c-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.l08c-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.l08c-btn:hover{background:var(--hover)}
.l08c-cb:focus-visible + .l08c-btn{outline:2px solid var(--accent);outline-offset:2px}
.l08c-cb:checked + .l08c-btn .l08c-off,.l08c-cb:not(:checked) + .l08c-btn .l08c-on{display:none}
.l08c-cb:checked ~ .l08c-box .l08c-g,.l08c-cb:checked ~ .l08c-box .l08c-pk,.l08c-cb:checked ~ .l08c-box .l08c-h{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.l08c-g{animation:none;opacity:1}.l08c-pk{animation:none;display:none}.l08c-h{animation:none;opacity:0}.l08c-btn{display:none}}
@keyframes l08c-h0{0%{opacity:1}25%{opacity:1}25.01%,100%{opacity:0}}
.l08c-h0{animation-name:l08c-h0}
@keyframes l08c-h1{0%,24.99%{opacity:0}25%{opacity:1}50%{opacity:1}50.01%,100%{opacity:0}}
.l08c-h1{animation-name:l08c-h1}
@keyframes l08c-h2{0%,49.99%{opacity:0}50%{opacity:1}75%{opacity:1}75.01%,100%{opacity:0}}
.l08c-h2{animation-name:l08c-h2}
@keyframes l08c-h3{0%,74.99%{opacity:0}75%{opacity:1}100%{opacity:1}100.01%,100%{opacity:0}}
.l08c-h3{animation-name:l08c-h3}
</style>
<defs>
<marker id="l08c-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="l08c-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="l08c-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<path class="l08c-edge" d="M380,106 L380,135 L161,135 L161,161" marker-end="url(#l08c-m-front)"/>
<text class="l08c-dimL" x="168" y="151">assertion issued</text>
<path class="l08c-edge" d="M380,106 L380,135 L458,135 L458,161" marker-end="url(#l08c-m-front)"/>
<text class="l08c-dimL" x="466" y="151">otherwise</text>
<path class="l08c-edge" d="M458,229 L458,258 L322,258 L322,284" marker-end="url(#l08c-m-front)"/>
<text class="l08c-dimL" x="328" y="274">Destination, Recipient</text>
<path class="l08c-edge" d="M458,229 L458,258 L472,258 L472,284" marker-end="url(#l08c-m-front)"/>
<text class="l08c-dimL" x="479" y="274">Audience</text>
<path class="l08c-edge" d="M458,229 L458,258 L609,258 L609,284" marker-end="url(#l08c-m-front)"/>
<text class="l08c-dimL" x="616" y="274">NameID</text>
<rect class="l08c-note" x="90" y="164" width="141" height="65" rx="8"/><text class="l08c-nt" x="161" y="185">The SP raised it:</text><text class="l08c-nt" x="161" y="202">ask the SP owner</text><text class="l08c-nt" x="161" y="219">for the SP's log</text>
<rect class="l08c-note" x="248" y="287" width="148" height="31" rx="8"/><text class="l08c-nt" x="322" y="308">Single sign-on URL</text>
<rect class="l08c-note" x="412" y="287" width="121" height="48" rx="8"/><text class="l08c-nt" x="472" y="308">Audience URI</text><text class="l08c-nt" x="472" y="325">(SP Entity ID)</text>
<rect class="l08c-note" x="548" y="287" width="121" height="31" rx="8"/><text class="l08c-nt" x="609" y="308">Name ID format</text>
<rect class="l08c-box" x="381" y="164" width="155" height="65" rx="8"/><text class="l08c-main" x="458" y="185">Compare the decoded</text><text class="l08c-nt" x="458" y="202">response with the</text><text class="l08c-nt" x="458" y="219">app's fields</text>
<rect class="l08c-box" x="306" y="24" width="148" height="82" rx="8"/><text class="l08c-main" x="380" y="45">Audience error</text><text class="l08c-nt" x="380" y="62">after an app edit:</text><text class="l08c-nt" x="380" y="79">what does the</text><text class="l08c-nt" x="380" y="96">System Log show?</text>
<g class="l08c-h l08c-h0">
<path class="l08c-hle" d="M380,106 L380,135 L161,135 L161,161" marker-end="url(#l08c-m-front)"/>
<rect class="l08c-hl" x="306" y="24" width="148" height="82" rx="8"/>
<rect class="l08c-hl" x="90" y="164" width="141" height="65" rx="8"/>
</g>
<g class="l08c-h l08c-h1">
<path class="l08c-hle" d="M380,106 L380,135 L458,135 L458,161" marker-end="url(#l08c-m-front)"/>
<path class="l08c-hle" d="M458,229 L458,258 L322,258 L322,284" marker-end="url(#l08c-m-front)"/>
<rect class="l08c-hl" x="306" y="24" width="148" height="82" rx="8"/>
<rect class="l08c-hl" x="381" y="164" width="155" height="65" rx="8"/>
<rect class="l08c-hl" x="248" y="287" width="148" height="31" rx="8"/>
</g>
<g class="l08c-h l08c-h2">
<path class="l08c-hle" d="M380,106 L380,135 L458,135 L458,161" marker-end="url(#l08c-m-front)"/>
<path class="l08c-hle" d="M458,229 L458,258 L472,258 L472,284" marker-end="url(#l08c-m-front)"/>
<rect class="l08c-hl" x="306" y="24" width="148" height="82" rx="8"/>
<rect class="l08c-hl" x="381" y="164" width="155" height="65" rx="8"/>
<rect class="l08c-hl" x="412" y="287" width="121" height="48" rx="8"/>
</g>
<g class="l08c-h l08c-h3">
<path class="l08c-hle" d="M380,106 L380,135 L458,135 L458,161" marker-end="url(#l08c-m-front)"/>
<path class="l08c-hle" d="M458,229 L458,258 L609,258 L609,284" marker-end="url(#l08c-m-front)"/>
<rect class="l08c-hl" x="306" y="24" width="148" height="82" rx="8"/>
<rect class="l08c-hl" x="381" y="164" width="155" height="65" rx="8"/>
<rect class="l08c-hl" x="548" y="287" width="121" height="31" rx="8"/>
</g>
<line class="l08c-front" x1="40" y1="371" x2="70" y2="371"/>
<text class="l08c-dim" x="78" y="375" style="text-anchor:start">the path being traced</text>
</svg>
</div>
</div>
<!-- /diagram:audience-error-checklist -->

This tree covers steps 1 and 2 of the checklist below; steps 3 to 5 are in the list. A leaf is where to look next, not a verdict. Like the checklist, it is written from the docs, not run against a live tenant.

1. Query the System Log (`eventType eq "user.authentication.sso"`, with a `since` that covers the incident) and read `outcome.result` and `outcome.reason`; capture one failing login with SAML-tracer. Okta may show nothing wrong: if it issued the assertion successfully, the SP raised the audience error, so ask the SP owner for the SP's log.
2. Compare the decoded response with the app's fields: Single sign-on URL against `Destination` and `Recipient` (the "Use this for Recipient URL and Destination URL" checkbox keeps them equal), Audience URI (SP Entity ID) against `Audience`, Name ID format against `NameID`.
3. Check the signing certificate's expiry and fingerprint, then the SP's clock.
4. For provisioning, Okta checks existence with `GET /Users?filter=userName eq "..."`, its guide shows the SP answering a duplicate create with 409, and Okta links a match it finds, so a 409 suggests the server's filter missed a record it holds (for example by comparing case-sensitively). With Deactivate Users enabled on the app's Provisioning To App tab, deactivation sends `active` false; suspending a user sends nothing.
5. Change one setting, retest, log it in the ticket, and strip the user's attributes before sending a capture to a vendor.

## Questions to ask of any integration

1. **Who issues** the proof (`iss`, entity ID) and for whom (`aud`, Audience)? 2. **Who validates**, and which checks? 3. **What proves freshness**: validity windows, `exp`, `nonce` (if sent), single-use codes? 4. **What happens to a leaver** in the SP, its sessions and its tokens? 5. **What is logged**, for how long? 6. **How do keys rotate**: `kid`, `jwks_uri`, metadata `validUntil`? 7. **What if the IdP is down**: existing SP sessions continue, new logins fail; is there a break-glass admin? 8. **Blast radius**: what can a stolen bearer token, signing key or SCIM token do?

## Your task: decode and diagnose three samples

All artefacts are invented samples. I ran every command on 2026-10-06 (macOS, jq 1.7.1); the output after each `# out:` line is real, and `now_utc` will differ for you.

```sh
T=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6InNhbXBsZS1rZXktMSJ9.eyJpc3MiOiJodHRwczovL2lkcC5leGFtcGxlLmNvbS9vYXV0aDIvc2FtcGxlIiwiYXVkIjoic2FtcGxlLWNsaWVudC1pZCIsInN1YiI6InVzZXItMDAwMSIsImlhdCI6MTc5MDAwMDAwMCwiZXhwIjoxNzkwMDAwMzAwLCJub25jZSI6InNhbXBsZS1ub25jZSJ9.ckGCV5aUn8_ZwBeTloXo0f8RbIphiOUgsMNSwTUXlLE
echo "$T" | jq -Rc 'split(".")[0:2][] | gsub("-";"+") | gsub("_";"/") | @base64d | fromjson'
jq -nc '{exp_utc: (1790000300|todate), now_utc: (now|floor|todate)}'
# out: {"alg":"HS256","typ":"JWT","kid":"sample-key-1"}
# out: {"iss":"https://idp.example.com/oauth2/sample","aud":"sample-client-id","sub":"user-0001","iat":1790000000,"exp":1790000300,"nonce":"sample-nonce"}
# out: {"exp_utc":"2026-09-21T14:18:20Z","now_utc":"2026-10-06T05:23:23Z"}
```
1. **Expired JWT.** The API answers 401 `invalid_token`. `exp` is long before now, so the token is expired: get a new one, do not debug the API.

```sh
cat > resp.xml <<'EOF'
<samlp:Response xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol" xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion" Destination="https://app.example.com/saml/acs"><saml:Assertion><saml:Subject><saml:NameID Format="urn:oasis:names:tc:SAML:2.0:nameid-format:transient">_7f3c91</saml:NameID><saml:SubjectConfirmation Method="urn:oasis:names:tc:SAML:2.0:cm:bearer"><saml:SubjectConfirmationData Recipient="https://app.example.com/saml/acs" NotOnOrAfter="2026-10-05T09:05:00Z"/></saml:SubjectConfirmation></saml:Subject><saml:Conditions NotBefore="2026-10-05T08:59:30Z" NotOnOrAfter="2026-10-05T09:05:00Z"><saml:AudienceRestriction><saml:Audience>https://app.example.com/saml/metadata</saml:Audience></saml:AudienceRestriction></saml:Conditions></saml:Assertion></samlp:Response>
EOF
grep -oE '(Destination|Recipient|NotBefore|NotOnOrAfter|Format)="[^"]*"|<saml:Audience>[^<]*' resp.xml
# out: Destination="https://app.example.com/saml/acs"
# out: Format="urn:oasis:names:tc:SAML:2.0:nameid-format:transient"
# out: Recipient="https://app.example.com/saml/acs"
# out: NotOnOrAfter="2026-10-05T09:05:00Z"
# out: NotBefore="2026-10-05T08:59:30Z"
# out: NotOnOrAfter="2026-10-05T09:05:00Z"
# out: <saml:Audience>https://app.example.com/saml/metadata
```
2. **Audience mismatch.** The sample SP expects entity ID `https://app.example.com/saml` and ACS URL `https://app.example.com/saml/acs`. `Destination` and `Recipient` match the ACS URL, but `Audience` ends in `/metadata` and the entity ID does not. Fix the Audience URI (SP Entity ID) field. The transient NameID may bite later.

A mock SCIM server (a sample: it rejects a duplicate `userName` ignoring case, has no auth, and ignores `?filter`). Save it as `mock.py` and run `python3 mock.py &`:

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
3. **SCIM 409.** The record exists under another letter case and has no `externalId`, which suggests (does not prove) that something other than your sync created it. Link it; do not delete it. Stop the mock with `kill %1`.
