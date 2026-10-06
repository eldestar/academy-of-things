# Choosing a protocol and troubleshooting it

You have configured SAML and OIDC apps in Okta. This capstone turns that into a decision guide and a debugging routine. It adds no new SSO or provisioning protocol: LDAP and Kerberos appear only here, as legacy alternatives, and everything else is restated so you can start here. SP and RP both mean the app side of a sign-in; this lesson says SP for any protocol. Facts checked 2026-10-06; confirm vendor figures in your own tenant.

## Which tool for which job

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
