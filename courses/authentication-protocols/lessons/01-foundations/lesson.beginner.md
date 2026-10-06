# Foundations: who is who, and why SSO exists

Facts checked 2026-10-06 against NIST SP 800-63-4 (final, 31 July 2025), RFC 6749, RFC 7519, OpenID Connect Core 1.0, the OASIS SAML 2.0 specifications, and the Okta and Microsoft Entra documentation.

This lesson names the parts behind a login, so later lessons on SAML, OpenID Connect and the rest have words to hang on. One example runs through it: Sam, a new employee, opens the company expense app.

## Authentication and authorization are different questions

- **Authentication** answers "who are you?" Sam proves he controls a secret, such as a password or a code from his phone. NIST describes it as checking the authenticators someone uses to claim a digital identity.
- **Authorization** answers "what may you do?" Once the app knows it is Sam, something decides whether he may only submit expenses or also approve them.

Single sign-on (SSO) answers the first question only. Four more words get mixed up constantly:

| Word | Plain meaning | Example |
| --- | --- | --- |
| **Identity** | Who someone is, as one service sees them. NIST says a digital identity is unique within one online service, so Sam can have several | Sam at the IdP, Sam at the expense app |
| **Account** | The record a service keeps: the person, their attributes, and the ways they can sign in | Sam's entry in the company directory |
| **Credential** | The secret or device used to prove it. NIST says *authenticator*; "credential" means different things in different documents (WebAuthn, in lesson 6, works with public-key credentials such as passkeys), so this course says what it means each time | a password, a phone code, a passkey |
| **Session** | The stretch of time after sign-in when a service remembers you, usually through a browser cookie the service issued | "I'm still signed in" |

## The parties: who is who

Three parties take part. **Sam** is the person. The **app** is what Sam wants to use. The **identity provider (IdP)** is the service that checks Sam's password and MFA and then tells the app who he is. Each standard names these roles differently:

| Role | SAML | OpenID Connect | NIST SP 800-63C |
| --- | --- | --- | --- |
| Service that checks the user | Identity Provider (IdP) | OpenID Provider (OP) | identity provider (IdP) |
| App that wants to know who the user is | Service Provider (SP) | Relying Party (RP) | relying party (RP) |
| The person | principal (also called subject) | End-User | subscriber |
| Signed statement about the person | assertion | ID token | assertion |

OAuth 2.0 (RFC 6749) uses a third set of names: resource owner (usually the person), client (the app), authorization server (hands out access tokens) and resource server (the API). An OAuth *access token* stands for a permission, with a scope and a duration. It is not a statement of who signed in. OpenID Connect is "a simple identity layer on top of the OAuth 2.0 protocol": its OP is an OAuth authorization server and its RP is an OAuth client. A **directory** stores accounts, such as a company's list of users. An IdP is the service that proves to apps who someone is. Many products do both jobs, which is why people blur them, but NIST keeps them apart: the IdP "provides a bridge" between the account and the app.

## Federation and SSO

NIST defines **federation** as authenticating a person to an app "without the RP directly verifying the subscriber's authenticators". The app never sees Sam's password; it trusts the IdP to check it. **SSO** is the result: Sam gets into many apps without a separate login at each. If an app asks for its own password, or checks it against the directory itself, that is not federation.

How does the app know a proof really came from the IdP? An admin sets this up once, before anyone signs in:

- **SAML:** the app is given the IdP's *metadata*, an XML file naming the IdP (its entityID), its signing keys and its sign-in URL.
- **OpenID Connect:** the app reads the IdP's *discovery document*, found at the issuer's address plus `/.well-known/openid-configuration`. It contains a `jwks_uri`, where the IdP publishes its signing keys.
- **The other direction:** the IdP is told where it may send proofs, using the app's *Assertion Consumer Service (ACS) URL* (SAML) or *redirect URI* (OpenID Connect).

The app trusts the IdP to say who Sam is and to pass along attributes such as his email. What each of those lets Sam do is still the app's decision.

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

The badges 1 to 5 match the numbered steps below. Every arrow shown passes through the browser; the OIDC code swap in step 4 is a separate direct call from the app to the IdP, covered in lesson 4.

1. Sam opens the app. He has no session with it yet.
2. The app redirects Sam's browser to the IdP, carrying a sign-in request.
3. Sam signs in at the IdP with his password, MFA and company rules. The IdP starts its own session for him, so a second app tomorrow will find him already signed in at the IdP and skip this step.
4. The IdP returns a signed proof. In SAML it is the *assertion*. In OpenID Connect's code flow the browser carries a one-time code, which the app swaps for the *ID token*.
5. The app checks the proof's signature, that it came from the expected IdP, that it was addressed to this app, and that it has not expired. Then it creates its own session, normally a cookie.

## Proof, IdP session and app session

Three things are created along the way, each with its own clock:

| Thing | Created by | Used by | How long |
| --- | --- | --- | --- |
| Proof (assertion or ID token) | the IdP | the app, once, at sign-in | its own expiry (`exp` in an ID token is required; a SAML sign-in carries a `NotOnOrAfter` time after which the app must refuse the proof) |
| IdP session | the IdP | the IdP | set by the IdP's policy |
| App session | the app | the app | set by the app |

The proof's expiry says how long the app may accept the proof, not how long Sam stays signed in. NIST: after the app consumes an assertion, its session is independent of the assertion, and in most cases the app's session "will far outlive" it.

**What if the IdP session ends?** Say an admin disables Sam's account. NIST says the IdP ending its session "will not necessarily terminate" Sam's sessions at apps. Microsoft's Entra documentation says Entra "can't directly revoke a session token issued by an application", so the app must revoke access itself. Okta's Single Logout works only when an app starts it, and only for apps that support it. Disabling Sam stops *new* sign-ins; sessions already open may carry on.

## Why companies use SSO, and what it does not do

SSO is a security control because the rules live in one place. Microsoft describes a Conditional Access policy as an if-then statement: if a user wants an application, then they must perform multifactor authentication. Okta's app sign-in policies likewise define how a user must authenticate to an app. Disabling one account in one place also stops new sign-ins to every app that uses the IdP. This covers only sign-ins that go through the IdP; an app that still accepts its own passwords has a side door the IdP's rules never see.

SSO leaves three jobs undone, and two habits undermine it:

- **Authorize.** It proves who Sam is. The app still decides what he may do.
- **Remove the app's own account.** The sign-in steps above carry no "disable" message to apps. NIST warns that an app that creates accounts on first sign-in can pile up accounts the IdP no longer knows about, unless the IdP tells it. Telling the app is a separate job, provisioning (lesson 5 covers SCIM), and whether a session already open then ends is up to the app.
- **End sessions in other apps.** See the section above.
- **Habit to avoid: shared accounts.** NIST requires each federated identifier to be associated with a single subscriber, meaning one person. If three colleagues share a login, the logs show which account acted, not which person.
- **Habit to avoid: email as the identifier.** OpenID Connect says only the issuer (`iss`) plus the subject (`sub`) are guaranteed unique. An email can be reused for another person or change over time, so it must not be used as a unique identifier.

## Your task: read a token

Ran locally with jq 1.7.1; the token is an invented sample with a junk signature. A JWT is three base64url-encoded parts separated by dots, and the middle part is the payload.

```bash
TOKEN='eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6InNhbXBsZS1rZXktMSJ9.eyJpc3MiOiJodHRwczovL2lkcC5leGFtcGxlLmNvbSIsInN1YiI6InUtN2YzYTljMjEiLCJhdWQiOiJzYW1wbGUtYXBwLWNsaWVudC1pZCIsImlhdCI6MTc5MDAwMDAwMCwiYXV0aF90aW1lIjoxNzg5OTk5OTkwLCJleHAiOjE3OTAwMDAzMDAsImFtciI6WyJwd2QiLCJvdHAiXSwiZW1haWwiOiJhbGV4QGV4YW1wbGUuY29tIn0.dGhpcy1pcy1ub3QtYS1yZWFsLXNpZ25hdHVyZS1zYW1wbGUtb25seQ'
echo "$TOKEN" | jq -cR 'split(".")[1] | gsub("-";"+") | gsub("_";"/") | @base64d | fromjson'
# {"iss":"https://idp.example.com","sub":"u-7f3a9c21","aud":"sample-app-client-id","iat":1790000000,"auth_time":1789999990,"exp":1790000300,"amr":["pwd","otp"],"email":"alex@example.com"}
```

Find the issuer (`iss`) and the claim the app should use to recognise this person (`sub`, not `email`). Compare `exp` with `date +%s`: has the proof expired? Could a stranger who copied the token read it? Yes: RFC 7519 warns a JWT "may contain privacy-sensitive information", so keep secrets out of it. Lesson 2 starts on SAML.
