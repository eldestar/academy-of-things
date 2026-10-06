# Choosing a protocol and troubleshooting it

You design or build the service-provider side of identity integrations. This capstone adds no new SSO or provisioning protocol: LDAP and Kerberos appear only here, as legacy alternatives, and everything else is restated, so you can start here. SP and RP both mean the app side; this lesson says SP for any protocol. Facts checked 2026-10-06: standards were read from the primary text; confirm vendor figures in your tenant.

## The decision matrix and its edges

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
