# Choosing a protocol and troubleshooting it

You are on the help desk. This lesson answers two questions you will hear every week: which sign-in technology should this app use, and what do I check when it breaks? It adds no new SSO or provisioning protocol: LDAP and Kerberos appear only here, as legacy alternatives, and everything else is restated, so you can start here. The app side of a sign-in is called the service provider (SP), or the relying party (RP) in some protocols; this lesson says SP for any protocol. Our running example is Priya, an employee opening an expense app. Facts checked 2026-10-06; confirm vendor figures in your own tenant.

## The words you need

- **Identity provider (IdP)**: the service that signs Priya in, such as Okta. The **app** she opens is the service provider (SP).
- **SAML**: the IdP sends the app an **assertion** (usually signed), a statement about Priya with an audience (which app it is for) and a validity window (two times between which it counts). It is delivered to the app's **ACS URL**, the address the app uses to receive it. The app's own ID is its **entity ID**.
- **OAuth 2.0**: lets an app get limited access to another service for a user, using an **access token**. A **bearer token** can be used by anyone who holds it, so treat it like a password.
- **OIDC**: a sign-in layer on top of OAuth 2.0. It returns an **ID token**, a **JWT**: three text parts joined by dots, which anyone can decode but which the app must also check.
- **SCIM**: lets the IdP create, update and deactivate accounts in the app automatically. Deactivating sets the account's `active` field to false; what the app does with that is up to the app.

## Which tool for which job

| Job | Tool | What it cannot do |
| --- | --- | --- |
| Priya opens a business app from her dashboard | SAML or OIDC | Create or remove her account in the app |
| An app needs limited access to another service for Priya | OAuth 2.0 | Tell the app who signed in; OIDC adds that |
| Accounts must appear, change and be switched off with HR changes | SCIM | Sign anyone in |
| The account should simply appear on her first sign-in | JIT provisioning: the app creates it from the details sent at sign-in | Delete or deactivate the account (Microsoft Learn) |
| An old app checks passwords in a company directory (LDAP) | LDAP: the app sends the name and password to the directory, so the app handles the password | Keep the password away from the app |
| Windows-style sign-in inside one company network (Kerberos) | Kerberos: tickets from a central server; computer clocks must be in step, typically within about 5 minutes | Work like a web redirect |

## Five steps for any ticket

1. **Reproduce**: same user, same app, a private window, and note the time.
2. **Capture** what the browser and app exchanged.
3. **Decode** it into readable text.
4. **Compare** each value, character for character, with the app's setup.
5. **Change one thing**, test again, and write down what you changed.

Tools you will meet:
- **Browser developer tools**, Network tab: tick Preserve log in Chrome or Persist Logs in Firefox, or each redirect clears the list.
- **SAML-tracer**: a browser extension that decodes SAML messages.
- **Token decoding offline**: never paste a real token into a website, because a bearer token can be used by whoever holds it.
- **Sign-in logs**: Okta's System Log keeps 90 days; Entra sign-in logs keep 7 days on Free and 30 on P1 and P2.
- **curl**, **openssl** (certificates), **dig** (DNS), and a clock check.

## Failure catalogue

| Symptom | Likely cause | First check |
| --- | --- | --- |
| App says the audience is wrong | The assertion is addressed to an audience; the app accepts it only if its own entity ID is listed | Audience in the capture vs the app's entity ID |
| App says wrong address, recipient or ACS | The message must name, and arrive at, the app's ACS URL | Recipient and Destination vs the ACS URL in setup |
| "Expired" or "not yet valid" | The assertion is valid only between two times, checked on the app's clock, so clocks that disagree break it | Times in the capture vs real time |
| Worked yesterday, "signature invalid" today | The app checks the signature using the IdP certificate it stored; certificates have an end date and may be replaced | Certificate end date with `openssl` |
| Signs in, but an empty new account appears | The NameID, the identifier sent for the user, can be a temporary value that changes each login | NameID Format in the capture |
| Error page at the IdP, never back to the app | The redirect URI, the address to send Priya back to, must match the registered one exactly, down to a trailing slash | `redirect_uri` in the capture vs registered |
| `invalid_grant` or `invalid_client` | The one-time code works once and expires in minutes (10 is the recommended maximum); a reload or a late retry fails. `invalid_client` means the app's own login to the IdP failed | Restart sign-in once; then check the app's client ID and secret |
| API says 401 `invalid_token` | The access token is expired, revoked or malformed | Decode it and compare `exp` (expiry time) with now |
| API says 403 `insufficient_scope` | The token is valid but its scopes (permissions) are too small | `scope` in the decoded token |
| App rejects the ID token | `iss` (issuer) must exactly match the IdP's published issuer, and `aud` must contain the app's client ID | Compare both with the app's setup |
| Email or name missing | Details are sent only when the app asks for the `email` or `profile` scope | Scopes the app requested |
| Provisioning says 409 | An account with that `userName` already exists, and `userName` ignores capital letters | Search by username before creating |
| A leaver still gets in | The app decides what `active` false means, and many apps do not cancel a session or token already issued; such a token works until its `exp` | How long the app's sessions last |
| Authenticator codes rejected | The code comes from the clock and typically changes every 30 seconds, so a wrong phone clock fails | Phone time settings |

## Eight questions for any integration

**Who issues** the proof, and for whom? **Who checks** it? **What shows it is fresh** (expiry times, one-time codes)? **What happens to a leaver**? **What is logged**, and for how long? **How do keys rotate**? **What if the IdP is down**: people already signed in to the app may keep working, new sign-ins fail. **How much damage** can a stolen token or key do?

## Triage walkthrough: Priya's ticket

Ticket 4821: "Priya clicks the Expense tile and gets: audience not valid. Two other finance users see it too; Marcus in Sales is fine in his own app."

1. **Reproduce**: Priya retries in a private window and gets the same error, so it is not her browser.
2. **Scope**: three users, one app. That points at the app's setup, not at people.
3. **Capture and decode**: you repeat the login with SAML-tracer and read the Audience: `https://app.example.com/saml/metadata`.
4. **Compare**: the app's setup says its entity ID is `https://app.example.com/saml`. They differ.
5. **Hand over**: you change nothing. You give the identity admin the decoded Audience, the entity ID, and the time, with personal details removed. The admin changes one setting and retests.

## Your task: read three sample artefacts

All artefacts are invented samples. I ran the decode command on 2026-10-06 (macOS, jq 1.7.1); output is real, and `now_utc` will differ for you.

```sh
T=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6InNhbXBsZS1rZXktMSJ9.eyJpc3MiOiJodHRwczovL2lkcC5leGFtcGxlLmNvbS9vYXV0aDIvc2FtcGxlIiwiYXVkIjoic2FtcGxlLWNsaWVudC1pZCIsInN1YiI6InVzZXItMDAwMSIsImlhdCI6MTc5MDAwMDAwMCwiZXhwIjoxNzkwMDAwMzAwLCJub25jZSI6InNhbXBsZS1ub25jZSJ9.ckGCV5aUn8_ZwBeTloXo0f8RbIphiOUgsMNSwTUXlLE
echo "$T" | jq -Rc 'split(".")[1] | gsub("-";"+") | gsub("_";"/") | @base64d | fromjson'
jq -nc '{exp_utc: (1790000300|todate), now_utc: (now|floor|todate)}'
# out: {"iss":"https://idp.example.com/oauth2/sample","aud":"sample-client-id","sub":"user-0001","iat":1790000000,"exp":1790000300,"nonce":"sample-nonce"}
# out: {"exp_utc":"2026-09-21T14:18:20Z","now_utc":"2026-10-06T05:23:23Z"}
```
1. The API answered 401 `invalid_token` for this token. Which field explains it? (`exp` is long before now: the token is expired. Ask for a new one.)
2. A SAML capture shows Audience `https://app.example.com/saml/metadata` while the sample app's entity ID is `https://app.example.com/saml`. What do you hand to the admin? (Both values; they do not match.)
3. On a mock server I ran (commands are in the intermediate version), a sample SCIM request to create `Alice@Example.com` returned `409 Conflict` with `"scimType": "uniqueness"`, and a look at the user list found `alice@example.com`. Is the server broken? (No: the account exists and `userName` ignores capitals. Link it, do not create it twice.)

Want to run the SAML and SCIM samples yourself? Switch to the intermediate level for the full commands.
