# Foundations: who is who, and why SSO exists

Facts checked 2026-10-06 against NIST SP 800-63-4 (final, 31 July 2025; sections cited as "63C Sec. n"), RFC 6749, RFC 7519, OpenID Connect Core 1.0 and Discovery 1.0, the OASIS SAML 2.0 specifications, and the Okta and Microsoft Entra documentation. Product behaviour is quoted from those docs, not run against a live tenant.

You build or review the relying-party side. This lesson fixes the vocabulary the course assumes, then goes where the standards are exact, ambiguous or silent: who the roles really are, what trust is anchored in, which three clocks govern a sign-in, and which attacks live at this layer.

## Roles and names: where the dialects disagree

| Role | SAML | OpenID Connect | OAuth 2.0 | NIST SP 800-63C |
| --- | --- | --- | --- | --- |
| Authenticates the user | Identity Provider (IdP) | OpenID Provider (OP): an OAuth authorization server "capable of Authenticating the End-User" | authorization server | identity provider (IdP) |
| Consumes the result | Service Provider (SP) | Relying Party (RP): an OAuth client | client | relying party (RP) |
| The person | principal or subject (the non-normative SAML Technical Overview says the two tend to be used interchangeably) | End-User | resource owner | subscriber (an individual enrolled in the CSP's service) |
| Signed statement | assertion | ID token (a JWT) | access token | assertion |

- **Names overlap.** The SAML glossary defines an IdP as "a kind of service provider" and uses *relying party* generically for any entity acting on information from another; OIDC's RP is specifically an OAuth client. NIST adds the CSP, which holds the subscriber account, with the IdP as the "bridge" to the RP.
- **"Credential" has several meanings.** RFC 6749 section 1.4: access tokens "are credentials used to access protected resources". The SP 800-63B glossary: an object that binds an identifier and attributes to an authenticator, issued by the CSP. WebAuthn has its own public-key credentials (lesson 6).
- **Proxies and brokers.** A NIST federation proxy acts as an RP upstream and an IdP downstream, so the subscriber takes part in two separate federation transactions. The federated identifier in the proxy's assertion SHALL name the proxy as issuer, the overall FAL is the lowest along the path, and a compromised proxy exposes everything that flows through it (63C Sec. 3.3.3).
- **Authorization is outside the model.** NIST: "The means by which an RP determines authorization and access is out of scope for these guidelines." An assertion or ID token carries identity, authentication facts and attributes. The OAuth access token is the authorization artifact: scopes and a duration (RFC 6749 section 1.4).

## Trust: what is asserted, and what anchors it

The RP trusts the IdP to assert the subject (`iss` plus `sub`), attributes, and authentication facts: SAML `AuthnInstant` and `AuthnContext` (both required); OIDC `auth_time` (when the login happened), `acr` (the authentication class met) and `amr` (the methods used), all optional, with `auth_time` required once you send `max_age`. For `acr` the spec says parties "will need to agree upon the meanings of the values used", so the meaning is agreed out of band.

- **SAML metadata** gives the entity ID, `KeyDescriptor` keys (`use` is `signing` or `encryption`) and endpoints. A root element MUST carry `validUntil` or `cacheDuration`. The spec says relying parties SHOULD have some means to establish trust in the metadata before relying on it, and lists XML signatures, TLS server authentication and DNS signatures. Metadata is also "not to be taken as an authoritative statement" of capabilities: an omitted option is not a claim of non-support. In effect the anchor is whatever you did to obtain the file.
- **OIDC** anchors on the https issuer URL you configured: discovery lives at `{issuer}/.well-known/openid-configuration`, the signing keys at its `jwks_uri`, and the token's `iss` must match the issuer exactly. Rotation works by `kid`: the verifier re-fetches the key set on an unfamiliar `kid`, and the set SHOULD retain recently retired keys (Core section 10.1.1).
- **The reverse direction.** The SAML profile says the IdP MUST have some means to establish that an ACS location is controlled by the SP. RFC 6749 section 3.1.2.2 says a server MUST require public clients, and confidential clients using the implicit grant, to register redirect endpoints, and SHOULD require all clients to.
- **NIST** calls the arrangement a *trust agreement* (63C Sec. 3.5), pre-established or subscriber-driven; FAL2 requires pre-established. Identifiers and keys SHALL be established securely as the agreement defines.

## The first sign-in, end to end

<!-- diagram:trust-signin -->
<div style="position:relative;margin:20px 0">
<input type="checkbox" id="tr-pause" class="tr-cb" /><label for="tr-pause" class="tr-btn"><span class="tr-off">Pause animation</span><span class="tr-on">Play animation</span></label>
<div class="tr-box" style="overflow-x:auto">
<svg class="tr-flow" viewBox="0 0 760 712" role="img" aria-labelledby="tr-t tr-d" style="width:100%;min-width:640px;max-width:800px;height:auto;display:block;margin:0 auto">
<title id="tr-t">A first federated sign-in, end to end</title>
<desc id="tr-d">Three parties: the app, the user's browser, and the identity provider. Step 1: the user opens the app through the browser and has no session. Step 2: the app redirects the browser to the identity provider with a sign-in request. Step 3: the user authenticates at the identity provider. Step 4: the identity provider returns a signed proof for the app, a SAML assertion or an OpenID Connect code that the app swaps for an ID token, and the browser delivers it to the app. Step 5: the app checks the proof's signature, issuer, audience and expiry, then sets its own session cookie in the browser. The diagram highlights each step in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
<style>
.tr-box{fill:var(--panel);stroke:var(--border-strong);stroke-width:1.5}
.tr-hot{fill:var(--panel);stroke:var(--accent);stroke-width:2.5}
.tr-ttl{fill:var(--text);font:600 15px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.tr-sub{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.tr-life{stroke:var(--border-strong);stroke-width:1.5;stroke-dasharray:4 5}
.tr-front{stroke:var(--accent);stroke-width:2;fill:none}
.tr-back{stroke:var(--muted);stroke-width:2;stroke-dasharray:7 5;fill:none}
.tr-bad{stroke:var(--bad);stroke-width:2;fill:none}
.tr-main{fill:var(--text);font:600 13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.tr-badt{fill:var(--bad-text)}
.tr-dim{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.tr-badge{fill:var(--accent)}
.tr-b-back{fill:var(--muted)}
.tr-b-bad{fill:var(--bad)}
.tr-b-good{fill:var(--good)}
.tr-bt{fill:var(--on-accent);font:700 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.tr-note{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.tr-note-good{fill:var(--good-bg);stroke:var(--good);stroke-width:1.5}
.tr-note-bad{fill:var(--bad-bg);stroke:var(--bad);stroke-width:1.5}
.tr-nt{fill:var(--body);font:12.5px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.tr-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:15s;animation-timing-function:linear;animation-iteration-count:infinite}
.tr-pk.tr-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.tr-pk.tr-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.tr-g{opacity:.45;animation-duration:15s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.tr-flow:hover .tr-g,svg.tr-flow:hover .tr-pk{animation-play-state:paused}
.tr-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.tr-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.tr-btn:hover{background:var(--hover)}
.tr-cb:focus-visible + .tr-btn{outline:2px solid var(--accent);outline-offset:2px}
.tr-cb:checked + .tr-btn .tr-off,.tr-cb:not(:checked) + .tr-btn .tr-on{display:none}
.tr-cb:checked ~ .tr-box .tr-g,.tr-cb:checked ~ .tr-box .tr-pk{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.tr-g{animation:none;opacity:1}.tr-pk{animation:none;display:none}.tr-btn{display:none}}
@keyframes tr-g0{0%{opacity:1}20%{opacity:1}20.01%,100%{opacity:.45}}
@keyframes tr-p0{0%,-0.01%{opacity:0;transform:translateX(0)}0%{opacity:1;transform:translateX(0)}20%{opacity:1;transform:translateX(-236px)}20.01%,100%{opacity:0;transform:translateX(-236px)}}
.tr-g0{animation-name:tr-g0}.tr-p0{animation-name:tr-p0}
@keyframes tr-g1{0%,19.99%{opacity:.45}20%{opacity:1}40%{opacity:1}40.01%,100%{opacity:.45}}
@keyframes tr-p1{0%,19.99%{opacity:0;transform:translateX(0)}20%{opacity:1;transform:translateX(0)}40%{opacity:1;transform:translateX(236px)}40.01%,100%{opacity:0;transform:translateX(236px)}}
.tr-g1{animation-name:tr-g1}.tr-p1{animation-name:tr-p1}
@keyframes tr-g2{0%,39.99%{opacity:.45}40%{opacity:1}60%{opacity:1}60.01%,100%{opacity:.45}}
.tr-g2{animation-name:tr-g2}
@keyframes tr-g3{0%,59.99%{opacity:.45}60%{opacity:1}80%{opacity:1}80.01%,100%{opacity:.45}}
@keyframes tr-p3{0%,59.99%{opacity:0;transform:translateX(0)}60%{opacity:1;transform:translateX(0)}80%{opacity:1;transform:translateX(-236px)}80.01%,100%{opacity:0;transform:translateX(-236px)}}
.tr-g3{animation-name:tr-g3}.tr-p3{animation-name:tr-p3}
@keyframes tr-g4{0%,79.99%{opacity:.45}80%{opacity:1}100%{opacity:1}100.01%,100%{opacity:.45}}
@keyframes tr-p4{0%,79.99%{opacity:0;transform:translateX(0)}80%{opacity:1;transform:translateX(0)}100%{opacity:1;transform:translateX(236px)}100.01%,100%{opacity:0;transform:translateX(236px)}}
.tr-g4{animation-name:tr-g4}.tr-p4{animation-name:tr-p4}
</style>
<defs>
<marker id="tr-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="tr-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="tr-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<line class="tr-life" x1="110" y1="72" x2="110" y2="660"/>
<line class="tr-life" x1="380" y1="72" x2="380" y2="660"/>
<line class="tr-life" x1="650" y1="72" x2="650" y2="660"/>
<rect class="tr-box" x="20" y="10" width="180" height="62" rx="10"/><text class="tr-ttl" x="110" y="36">App (SP / RP)</text><text class="tr-sub" x="110" y="56">trusts the IdP's signing keys</text>
<rect class="tr-box" x="290" y="10" width="180" height="62" rx="10"/><text class="tr-ttl" x="380" y="36">Browser</text><text class="tr-sub" x="380" y="56">carries every message</text>
<rect class="tr-hot" x="560" y="10" width="180" height="62" rx="10"/><text class="tr-ttl" x="650" y="36">IdP (OP)</text><text class="tr-sub" x="650" y="56">authenticates the user</text>
<g class="tr-g tr-g0">
<text class="tr-main" x="245" y="108">open the app</text>
<text class="tr-dim" x="245" y="124">no session cookie yet</text>
<line class="tr-front" x1="366" y1="138" x2="124" y2="138" marker-end="url(#tr-m-front)"/>
<circle class="tr-badge tr-b-front" cx="380" cy="138" r="12"/><text class="tr-bt" x="380" y="142.5">1</text>
</g>
<g class="tr-g tr-g1">
<text class="tr-main" x="245" y="178">redirect to the IdP</text>
<text class="tr-dim" x="245" y="194">with a sign-in request</text>
<line class="tr-front" x1="124" y1="208" x2="366" y2="208" marker-end="url(#tr-m-front)"/>
<circle class="tr-badge tr-b-front" cx="110" cy="208" r="12"/><text class="tr-bt" x="110" y="212.5">2</text>
<text class="tr-main" x="515" y="248">browser follows the redirect</text>
<line class="tr-front" x1="394" y1="262" x2="636" y2="262" marker-end="url(#tr-m-front)"/>
</g>
<g class="tr-g tr-g2">
<rect class="tr-note" x="536" y="296" width="214" height="48" rx="8"/>
<text class="tr-nt" x="643" y="317">user signs in at the IdP</text>
<text class="tr-nt" x="643" y="334">password, MFA, policy checks</text>
<circle class="tr-badge tr-b-plain" cx="536" cy="320" r="12"/><text class="tr-bt" x="536" y="324.5">3</text>
</g>
<g class="tr-g tr-g3">
<text class="tr-main" x="515" y="378">signed proof for the app</text>
<text class="tr-dim" x="515" y="394">SAML: the assertion itself</text>
<text class="tr-dim" x="515" y="410">OIDC: a code to swap for the ID token</text>
<line class="tr-front" x1="636" y1="424" x2="394" y2="424" marker-end="url(#tr-m-front)"/>
<circle class="tr-badge tr-b-front" cx="650" cy="424" r="12"/><text class="tr-bt" x="650" y="428.5">4</text>
<text class="tr-main" x="245" y="464">browser delivers it to the app</text>
<line class="tr-front" x1="366" y1="478" x2="124" y2="478" marker-end="url(#tr-m-front)"/>
</g>
<g class="tr-g tr-g4">
<rect class="tr-note" x="12" y="512" width="195" height="48" rx="8"/>
<text class="tr-nt" x="110" y="533">checks signature, issuer,</text>
<text class="tr-nt" x="110" y="550">audience and expiry</text>
<circle class="tr-badge tr-b-plain" cx="12" cy="536" r="12"/><text class="tr-bt" x="12" y="540.5">5</text>
<text class="tr-main" x="245" y="594">sets its own session cookie</text>
<line class="tr-front" x1="124" y1="608" x2="366" y2="608" marker-end="url(#tr-m-front)"/>
</g>
<circle class="tr-pk tr-p0" cx="360" cy="138" r="5.5"/>
<circle class="tr-pk tr-p1" cx="400" cy="262" r="5.5"/>
<circle class="tr-pk tr-p3" cx="360" cy="478" r="5.5"/>
<circle class="tr-pk tr-p4" cx="130" cy="608" r="5.5"/>
<line class="tr-front" x1="40" y1="688" x2="70" y2="688"/>
<text class="tr-dim" x="78" y="692" style="text-anchor:start">message through the user's browser</text>
</svg>
</div>
</div>
<!-- /diagram:trust-signin -->

The badges 1 to 5 match the numbered steps below. Every arrow shown passes through the browser; the OIDC code swap in step 4 is a separate direct call from the app to the IdP, covered in lesson 4, and the SAML Artifact binding (step 4) is not drawn.

1. **Request, no session.** RP-initiated: SAML `<AuthnRequest>`, or an OIDC authentication request. NIST says the transaction SHOULD be RP-initiated at FAL1 and SHALL be at FAL2. SAML also defines IdP-initiated SSO, with no `AuthnRequest`.
2. **Redirect.** The RP needs some way to tie the response to its request. SAML leaves the means to the SP (the profile offers RelayState as an optional mechanism, so keeping the requested URL is common practice, not a requirement), and the `<AuthnRequest>` may travel by Redirect, POST or Artifact binding. If the OIDC client sent a `nonce`, it must remember it to check the ID token.
3. **Authentication.** The IdP may reuse its session and SHALL convey whatever it knows about recency. The RP can force a new login: SAML `ForceAuthn`, or OIDC `max_age`, which obliges the OP to re-authenticate when the last login is older.
4. **Proof.** SAML POST binding: the `<Response>` goes through the browser and its assertion MUST be signed. With the Artifact binding the browser carries only an artifact and the SP fetches the `<Response>` from the IdP over a back channel (Profiles 4.1.3.5). OIDC code flow: only a code crosses the browser; the ID token comes from the token endpoint, so no token is exposed to the user agent (Core section 3.1).
5. **Validation, then session.** SAML: signature, `AudienceRestriction`, and the bearer confirmation (`Recipient` equals the ACS URL, its `NotOnOrAfter` has not passed, `InResponseTo` equals the request's ID unless the response is unsolicited; Profiles 4.1.4.3). OIDC (Core section 3.1.3.7): `iss` exact match, `aud` contains your client_id and the token is rejected if it lists untrusted extra audiences, signature, `exp`, and `nonce` MUST be checked if you sent one. NIST adds that a session SHALL be created only if the assertion is valid and from the expected IdP, that IdP is the one named in the federated identifier, and the assertion maps to a provisioned RP account (63C Sec. 3.9).

## Three clocks: assertion, IdP session, RP session

- **Assertion.** SAML `Conditions` `NotBefore` and `NotOnOrAfter` are optional, and they "do not guarantee that the statements in the assertion will be correct or accurate throughout the validity period"; without a `NotOnOrAfter` there the conditions impose "no expiry". For Web SSO, though, the bearer `SubjectConfirmationData` must carry its own `NotOnOrAfter`, the window in which the assertion can be delivered, plus `Recipient` and, when the response answers a request, `InResponseTo`, and must not carry `NotBefore` (Profiles 4.1.4.2). The SP must verify them (4.1.4.3), so a bearer assertion always has a delivery deadline. An ID token's `exp` is required, with "some small leeway, usually no more than a few minutes" for clock skew allowed. NIST: the window manages the RP's processing and "does not indicate the lifetime of the authenticated session at the IdP or RP"; a new transaction while the IdP session lives yields a new, separate assertion.
- **IdP session.** SAML `SessionNotOnOrAfter` is when the session with the issuing authority MUST be considered ended, with no required relationship to `NotOnOrAfter`. It is optional and fixed when the assertion is issued. The Web SSO profile says that if an `AuthnStatement` used to establish a security context carries it, the SP's security context SHOULD be discarded then, unless the SP re-establishes identity by repeating the profile (4.1.4.3; lesson 2). That makes it a ceiling set in advance, not event-driven revocation: it does not move when the account is later disabled. The OIDC spec says `exp` is "unrelated" to the RP-OP session.
- **RP session.** Yours to design. The RP MAY end it at any time, or restrict access if the assertion, authentication event or attributes fall short. Fetching attributes through an identity API SHALL NOT be used to establish or extend a session.
- **Recency is not issuance time.** NIST's example: a subscriber authenticates at the IdP, starts a transaction 30 minutes later, and the IdP reuses its session, so the new assertion says the last authentication was 30 minutes ago. `iat` (when the JWT was issued) is fresh; `auth_time` (when authentication occurred) is not. When you requested `auth_time` (directly or via `max_age`), the RP SHOULD check it and request re-authentication if too much time has passed.
- **Termination.** The IdP ending its session "will not necessarily terminate" RP sessions; the two MAY exchange end-session events through the protocol or shared signaling, and the IdP SHOULD signal a terminated, suspended or disabled account, suspected compromise and attribute changes. Okta Single Logout starts only from the SP, only for apps that support it, and not for SWA apps. Entra: the IdP "can't directly revoke a session token issued by an application". Okta Universal Logout and Entra Continuous Access Evaluation help only for supported apps.
- **Trade-off: session length.** Longer RP sessions mean fewer prompts and a wider leaver gap. NIST SP 800-63B-4 gives benchmarks: at AAL2, overall reauthentication SHOULD fall within 24 hours and inactivity within 1 hour; at AAL3, the overall timeout SHALL be no more than 12 hours and inactivity SHOULD be no more than 15 minutes.
- **Trade-off: where to demand strength.** Asking the IdP (`max_age`, `ForceAuthn`, `acr`) keeps policy central, but `acr` means only what you and the IdP agreed. Re-authenticating inside the app avoids that and splits policy across two places.
- **Edge case: skipping the signature.** For an ID token received directly from the token endpoint, Core section 3.1.3.7 lets TLS server validation stand in for the signature check (MAY), and requires the signature check for every other ID token.

## Identifiers, accounts and the leaver gap

- **Federated identifier = issuer plus subject.** NIST calls it imperative that an RP never process a subject identifier without the issuer, since IdPs choose them independently and may collide. OIDC `sub` is case-sensitive, at most 255 ASCII characters, locally unique and never reassigned. A JWT's `sub` is optional (RFC 7519), but an ID token's is required.
- **Not portable across apps.** OIDC subject types are `public` (same `sub` for all clients) or `pairwise` (a different `sub` per client), so you cannot join users across apps on `sub`. SAML NameID formats include email address, persistent and transient. A persistent identifier is usually issued for a single SP; a transient one is destroyed when the session ends, so it cannot key an account.
- **Email is not a key.** OIDC section 5.7: an issuer MAY reuse an email value for different users, the address MAY change, and `email` MUST NOT be a unique identifier. Microsoft adds that `email` and `preferred_username` can be controlled by tenant admins or sometimes users, and recommends `tid` plus `oid` as a combined key in Entra, where `sub` is pairwise per application. NIST: federated identifiers SHALL NOT contain plaintext personal data such as emails at FAL2.
- **Linking and resolution.** If you allow linking, the RP SHALL require an authenticated session, which SHOULD use an existing federated identifier. Resolving an assertion to an existing record SHALL use attributes sufficient to resolve uniquely, and SHALL NOT attach a record to an identifier that does not belong to that subscriber.
- **Provisioning.** The account must exist before the session (63C Sec. 3.8). *Just-in-time* creates it on the first assertion, so without signals it accumulates accounts the IdP no longer knows. *Pre-provisioning* pushes accounts ahead of use, including people who never sign in. *Ephemeral* keeps no long-term record after the session and suits RPs that fully externalize access rights to the IdP.

## Attack classes at this layer

| Attack | What it exploits | Mitigation |
| --- | --- | --- |
| Forged or modified assertion | RP accepts an unsigned or wrongly keyed statement | verify the signature with the expected IdP's key (FAL1 SHALL) |
| Wrong-audience token | a token minted for app A is accepted by app B | `aud` or `AudienceRestriction` check; FAL2 requires a single RP per assertion |
| Assertion injection | a stolen or manufactured assertion is forced into a session | RP-initiated flows with tracked state, nonces, back-channel presentation, RP authentication to the IdP, no unsolicited IdP-initiated responses, or platform APIs instead of HTTP redirects (63C Sec. 3.11.1; protection required at FAL2) |
| Replay | the same assertion is presented again | RP-enforced replay protection (SHALL at FAL1); `nonce` |
| Identifier collision or reuse | two issuers share a `sub`, or an email is reassigned | key on issuer plus subject; link only through authentication |
| Session outliving the IdP | RP session independent of IdP state | signals, provisioning, bounded RP sessions |

A stolen assertion still carries the IdP's genuine signature, so a signature check alone does not stop injection. Injection differs from forgery and replay: an attacker can obtain a fresh, genuine assertion for their own account, signed and addressed to your SP, so signature, audience and validity-window checks all pass; what fails is the binding to a transaction the RP started. Most of the mitigations NIST lists tie the response to a transaction the RP started and can track (another uses platform APIs for front-channel communication instead of HTTP redirects). FALs are a US federal baseline; treat them as a benchmark. RFC 7519 section 12 adds that a JWT "may contain privacy-sensitive information", so omit it, encrypt, or use TLS.

## Your task: check a token, then argue a design

Ran locally with jq 1.7.1. The token is the invented sample from the earlier levels (junk signature); this checks claims only and does **not** verify the signature, which a real RP must.

```bash
TOKEN='eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6InNhbXBsZS1rZXktMSJ9.eyJpc3MiOiJodHRwczovL2lkcC5leGFtcGxlLmNvbSIsInN1YiI6InUtN2YzYTljMjEiLCJhdWQiOiJzYW1wbGUtYXBwLWNsaWVudC1pZCIsImlhdCI6MTc5MDAwMDAwMCwiYXV0aF90aW1lIjoxNzg5OTk5OTkwLCJleHAiOjE3OTAwMDAzMDAsImFtciI6WyJwd2QiLCJvdHAiXSwiZW1haWwiOiJhbGV4QGV4YW1wbGUuY29tIn0.dGhpcy1pcy1ub3QtYS1yZWFsLXNpZ25hdHVyZS1zYW1wbGUtb25seQ'
echo "$TOKEN" | jq -cR 'split(".")[1] | gsub("-";"+") | gsub("_";"/") | @base64d | fromjson | {iss_ok: (.iss == "https://idp.example.com"), aud_ok: ([.aud] | flatten | index("sample-app-client-id") != null), unexpired: (.exp > now), secs_from_login_to_issue: (.iat - .auth_time), account_key: [.iss, .sub]}'
# {"iss_ok":true,"aud_ok":true,"unexpired":false,"secs_from_login_to_issue":10,"account_key":["https://idp.example.com","u-7f3a9c21"]}
```

`unexpired` is false because the sample's `exp` is long past. Now argue three points. Which claim would gate an "export all data" action, and why not `exp`? What does an unexpired token say about the user's IdP session (nothing)? Where must revocation live, given the RP session is yours? Lesson 2 goes deep on SAML.
