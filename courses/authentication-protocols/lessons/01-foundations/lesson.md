# Foundations: who is who, and why SSO exists

Facts checked 2026-10-06 against NIST SP 800-63-4 (final, 31 July 2025), RFC 6749, RFC 7519, OpenID Connect Core 1.0 and Discovery 1.0, the OASIS SAML 2.0 specifications, and the Okta and Microsoft Entra documentation. Product behaviour is quoted from those docs, not run against a live tenant.

You have configured SAML and OIDC apps. This lesson fixes the vocabulary the rest of the course uses and the model behind settings you already know: what the app trusts the IdP for, which artifact lives how long, and why "we have SSO" settles less than people assume.

## One vocabulary, four dialects

| Role | SAML | OpenID Connect | OAuth 2.0 | NIST SP 800-63C |
| --- | --- | --- | --- | --- |
| Authenticates the user | Identity Provider (IdP) | OpenID Provider (OP), an OAuth authorization server | authorization server | identity provider (IdP) |
| Consumes the result | Service Provider (SP); the glossary also uses the generic *relying party* | Relying Party (RP), an OAuth client | client | relying party (RP) |
| The person | principal or subject | End-User | resource owner | subscriber |
| Signed statement | assertion | ID token (a JWT) | access token: a permission, not an identity | assertion |

- **Authentication vs authorization.** SP 800-63B describes authentication as determining the validity of the authenticators used to claim a digital identity. Authorization decides what that identity may do: an OAuth access token is "a string representing an authorization issued to the client", limited in scope and duration (RFC 6749 section 1.4). An assertion or ID token says who authenticated, how and when. It does not grant permissions.
- **Identity** on the wire is a subject identifier scoped to an issuer: OIDC `iss` plus `sub`, which NIST calls the *federated identifier*.
- **Account.** The IdP holds the subscriber account (NIST: the CSP's record of the subscriber, their attributes and authenticators). The app holds a separate *RP subscriber account*, which must exist before an authenticated session can be created.
- **Credential** is overloaded: RFC 6749 calls an access token a credential, while NIST uses *authenticator* for passwords, passkeys and OTPs, and WebAuthn works with public-key credentials such as passkeys (lesson 6). Say which you mean.
- **Session.** A secret shared between the user's software and the service, most often a cookie. Each sign-in creates several (see below).

The SAML glossary defines an IdP as "a kind of service provider that creates, maintains, and manages identity information for principals and provides principal authentication to other service providers". NIST splits those jobs: the CSP holds the account, the IdP is the bridge to the RP. One product usually plays both, which is why the words blur. An app that binds to a directory with the user's password verifies the authenticator itself, so under NIST's definition ("without the RP directly verifying the subscriber's authenticators") it is not federation.

## Trust: what the app relies on, and how it gets it

The app trusts the IdP's *signature* and what the signed statement says: who (issuer plus subject), attributes (email, groups), and how and when. For the last one, SAML's `AuthnStatement` has required `AuthnInstant` and `AuthnContext`; OIDC's `auth_time`, `acr` and `amr` are optional, and `auth_time` becomes required only when you send `max_age` or request it as essential. NIST says the IdP SHALL pass the RP whatever it knows about how recent the authentication was. What the subject may do inside the app is never part of that trust.

| Direction | SAML | OIDC and OAuth |
| --- | --- | --- |
| App learns the IdP | IdP metadata: `entityID`, `KeyDescriptor use="signing"`, `SingleSignOnService` | discovery document at `{issuer}/.well-known/openid-configuration`: `issuer` and `jwks_uri`, the signing keys |
| IdP learns the app | SP metadata: `AssertionConsumerService` (ACS) | registered redirect URI (RFC 6749 section 3.1.2.2: MUST for public clients, SHOULD for all) |
| Key rotation | the new key must reach the app's stored copy of the metadata | the verifier re-fetches `jwks_uri` when it sees an unfamiliar `kid` (Core section 10.1.1) |

A SAML metadata root element must carry `validUntil` or `cacheDuration`. The metadata spec adds that relying parties SHOULD have some means of establishing trust in the metadata itself, and that retrieval over HTTP SHOULD use TLS. In OIDC the issuer from discovery must exactly match the token's `iss`. NIST's umbrella term for the whole arrangement is a *trust agreement*.

A rotation of the *signing* key breaks signature verification and nothing else. Metadata marks keys `use="signing"` or `use="encryption"`, and encryption is a separate optional layer in both protocols: a SAML `EncryptedAssertion` is meant for when the assertion passes through an intermediary, and an OIDC ID token must be signed and may then also be encrypted, with the keys the client registered (Core section 2). So "assertions are encrypted with the rotated key" and "ID tokens are never encrypted" are both wrong.

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

1. **Request, no session.** The user reaches the app. A SAML SP typically keeps the requested URL across the exchange: that is common practice, not a requirement, since the profile lets the SP use any means and offers RelayState as an optional mechanism. An OIDC client prepares an authentication request.
2. **Redirect.** SAML: with the HTTP-Redirect binding, an HTTP 302 or 303 to the IdP's sign-on service with an `<AuthnRequest>` in the `SAMLRequest` query variable (the profile also allows the POST and Artifact bindings for the request). OIDC: the browser is sent to the authorization endpoint.
3. **Authentication.** The IdP may reuse its own session and skip the prompt. The RP can demand a fresh login: SAML `ForceAuthn="true"`, or OIDC `max_age`, which obliges the OP to re-authenticate when the last login is older than that.
4. **Proof.** SAML: a `<Response>` holding the assertion, POSTed through the browser to the ACS (with the Artifact binding the browser carries only an artifact and the SP fetches the `<Response>` from the IdP over a back channel; an IdP-initiated variant exists with no `AuthnRequest`). OIDC code flow: a code through the browser, swapped at the token endpoint for the ID token (Core section 3.1).
5. **Validation, then session.** SAML: the signature (the Web Browser SSO profile says the assertion MUST be signed when the POST binding is used), `AudienceRestriction` (valid only if the RP is in the audience), and the bearer confirmation: `Recipient` equals the ACS URL, its `NotOnOrAfter` has not passed, and `InResponseTo` equals the request's ID (absent when the response is unsolicited). OIDC (section 3.1.3.7): `iss` matches exactly, `aud` contains the client_id, signature, `exp` in the future. NIST adds that a session may be created only from a valid assertion from the expected IdP, tied to a provisioned RP account.

## Assertion, token, cookie: who issues, who consumes, how long

| Artifact | Issued by | Consumed by | Lifetime |
| --- | --- | --- | --- |
| SAML assertion | IdP | SP, once, at the ACS | `Conditions` `NotBefore`/`NotOnOrAfter` are optional, but Web SSO requires a `NotOnOrAfter` on the bearer subject confirmation (and no `NotBefore` there); the specs fix no value (NIST gives "valid for five minutes" only as an example) |
| ID token | OP | RP, once, at sign-in | `exp` is required; the spec says it is unrelated to the lifetime of the RP-OP session |
| Access token | authorization server | resource server | `expires_in` is RECOMMENDED; Entra access tokens default to a random 60 to 90 minutes (75 on average), and up to 28 hours for CAE-capable clients |
| IdP session | IdP | IdP | IdP policy |
| App session cookie | the app | the app | the app's design; for reference, NIST's AAL2 baseline says overall reauthentication SHOULD be within 24 hours and inactivity within 1 hour |

NIST: the assertion's validity window "does not indicate the lifetime of the authenticated session at the IdP or RP", and the RP session will usually far outlive it. SAML's `SessionNotOnOrAfter` is the time when the session between the principal and the issuing SAML authority "MUST be considered ended". It describes the IdP session, with no required relationship to `NotOnOrAfter`. The Web SSO profile adds only that an SP SHOULD discard the security context it built from that assertion when the time passes (lesson 2); the attribute is optional and fixed at issuance, so it is a hint the IdP may send, not a control over your app's session.

**When the IdP session ends, the app session lives on.** NIST: ending the IdP session "will not necessarily terminate" RP sessions. Entra: "Microsoft Entra ID can't directly revoke a session token issued by an application", so the app must revoke it, and revoking refresh tokens leaves access tokens valid until they expire. Okta Single Logout is initiated only by the SP, only for apps that support it, and SWA apps don't support it. Okta Universal Logout and Entra Continuous Access Evaluation can end sessions or tokens, but only for supported apps.

## What SSO buys, and where it stops

It is a control because policy runs at one point. Entra Conditional Access is an if-then rule (if a user wants an application, they must perform MFA), enforced after first-factor authentication. Okta app sign-in policies define how a user must authenticate and check requirements such as group membership, IP zone and risk. Either runs in step 3, whichever protocol sent the user to the IdP. A disabled IdP account cannot complete step 3, so it gets no new proofs. SSO does **not**:

- **Authorize.** Attributes and groups arrive; mapping them to roles is the app's logic.
- **Deprovision.** NIST: with just-in-time provisioning an RP can accumulate accounts the IdP no longer knows about unless the IdP signals terminations. Entra's guidance is automated provisioning and deprovisioning, plus apps revoking their own session tokens.
- **End other sessions.** See above.

Side doors skip the policy entirely: a local password, an API key, a session already open, an access token already issued.

## Failure modes to look for

- **SSO treated as authorization.** Everyone who can authenticate lands with a default or admin role. Deny by default and map roles from attributes.
- **App sessions outliving the IdP.** The leaver keeps working. Combine app-side deprovisioning, SLO or Universal Logout where supported, and a bounded app session.
- **Shared accounts.** NIST requires a federated identifier to be associated with a single subscriber. Logs, MFA and policy then describe an account, not a person.
- **Email as the key.** OIDC section 5.7: only `iss` plus `sub` are guaranteed unique; an issuer MAY reuse an email value for different users over time, and `email` MUST NOT be used as a unique identifier. NIST adds that different IdPs choose subject identifiers independently, so a bare `sub` can collide across issuers. Microsoft says never to use `email`, `preferred_username` or `unique_name` for access decisions, because tenant admins or sometimes users can control them, and recommends `tid` and `oid` as a combined key.

## Your task: decode, discover, read metadata

Ran locally (jq 1.7.1, xmllint, curl). The token and the SAML file are invented samples; the discovery fetch is a real public endpoint, output as fetched while writing. Not run against a live tenant.

```bash
TOKEN='eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6InNhbXBsZS1rZXktMSJ9.eyJpc3MiOiJodHRwczovL2lkcC5leGFtcGxlLmNvbSIsInN1YiI6InUtN2YzYTljMjEiLCJhdWQiOiJzYW1wbGUtYXBwLWNsaWVudC1pZCIsImlhdCI6MTc5MDAwMDAwMCwiYXV0aF90aW1lIjoxNzg5OTk5OTkwLCJleHAiOjE3OTAwMDAzMDAsImFtciI6WyJwd2QiLCJvdHAiXSwiZW1haWwiOiJhbGV4QGV4YW1wbGUuY29tIn0.dGhpcy1pcy1ub3QtYS1yZWFsLXNpZ25hdHVyZS1zYW1wbGUtb25seQ'
echo "$TOKEN" | jq -R 'split(".")[1] | gsub("-";"+") | gsub("_";"/") | @base64d | fromjson | {exp, expires_at: (.exp|todate), expired_now: (.exp < now)}' -c
# {"exp":1790000300,"expires_at":"2026-09-21T14:18:20Z","expired_now":true}
curl -s https://accounts.google.com/.well-known/openid-configuration | jq -c '{issuer, jwks_uri}'
# {"issuer":"https://accounts.google.com","jwks_uri":"https://www.googleapis.com/oauth2/v3/certs"}
```

Save this invented IdP metadata as `idp-sample.xml`, then run `xmllint --xpath '//@entityID | //@validUntil | //@use | //@Location' idp-sample.xml`:

```xml
<EntityDescriptor xmlns="urn:oasis:names:tc:SAML:2.0:metadata" xmlns:ds="http://www.w3.org/2000/09/xmldsig#"
                  entityID="https://idp.example.com/saml/sample" validUntil="2027-01-01T00:00:00Z">
  <IDPSSODescriptor protocolSupportEnumeration="urn:oasis:names:tc:SAML:2.0:protocol">
    <KeyDescriptor use="signing">
      <ds:KeyInfo><ds:X509Data><ds:X509Certificate>SAMPLE-NOT-A-REAL-CERTIFICATE</ds:X509Certificate></ds:X509Data></ds:KeyInfo>
    </KeyDescriptor>
    <SingleSignOnService Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect" Location="https://idp.example.com/saml/sample/sso"/>
  </IDPSSODescriptor>
</EntityDescriptor>
```

Real output: `entityID="https://idp.example.com/saml/sample"`, `validUntil="2027-01-01T00:00:00Z"`, `use="signing"`, `Location="https://idp.example.com/saml/sample/sso"`. Which of these does an app store to verify signatures, and what must happen to it when the IdP rotates its signing key? Which claim would you key accounts on? Lesson 2 goes deep on SAML.
