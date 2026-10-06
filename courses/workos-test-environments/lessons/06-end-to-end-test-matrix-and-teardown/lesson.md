# End-to-end test matrix and teardown

With the IdPs, the WorkOS staging environment, a local app and a Terraform sandbox in place, this lesson is the part that turns a lab into evidence: a fixed matrix, a debugging order, a way to screenshot without leaking, and a teardown you can prove. Facts checked 2026-10-03 against WorkOS docs, the WorkOS OpenAPI spec, Chrome and Okta documentation. **Written from the docs, not run against a live tenant.** Where the docs I read state no result, the cell says "verify in your tenant", and that is a finding to record, not a gap to fill with a guess.

## The SSO matrix

Run it in the staging environment. For the IdP-initiated case the docs say to disable AuthKit first. Use `example.com` style addresses for synthetic users; WorkOS docs say it accepts them and never sends mail to them.

| # | Case | Trigger | Expected, if documented |
|---|------|---------|-------------------------|
| S1 | SP-initiated | Your `/login` redirects to WorkOS | Callback receives `code`; exchange returns a profile with `connectionId` and `organizationId`. Staging also ships a Test IdP and a Dashboard Test SSO page with SP-initiated, IdP-initiated, guest-domain and error scenarios. |
| S2 | IdP-initiated | Click the app tile in Okta | Docs conflict: Login Flows says WorkOS redirects to a sign-in endpoint you set under the application's Redirects, appending `connection_id`; the SSO quick start says the default redirect URI is used. If disabled on the connection you get `idp_initiated_sso_disabled`. Record which one your app saw. |
| S3 | New vs existing user | Sign in with a never-seen and a known user | WorkOS does not manage your user table; the docs tell you to key records on profile `id` and constrain email matching to `organization_id`. Your app's result: verify in your tenant. |
| S4 | Deactivated user | Deactivate in Okta, then sign in | Okta refuses to issue an assertion. What your callback receives: verify in your tenant. Existing app sessions are your app's problem. |
| S5 | Group change | Move the user between groups | Profile has a `groups` field in the v11.0.0 SDK type; whether it is populated depends on the group attribute statement you configured. Verify in your tenant. |
| S6 | Attribute change | Edit the user's name in Okta | Not stated in the docs for a user edit in the IdP. Profile fields are read from the assertion at each sign-in, so expect the new name at next sign-in: verify in your tenant. (The docs' "next sign-in" line is about changing WorkOS attribute settings.) |
| S7 | Cert rotation | Generate a new signing cert in Okta | Docs: certificates typically last 1 to 5 years, WorkOS flags expiry within 90 days (a warning window, not an assertion lifetime), and a monitored metadata URL is refreshed automatically while a manual upload needs a manual update. WorkOS checks the signature on SAML responses against the IdP certificate stored on the connection, so a stale manual upload breaks every login while WorkOS itself is unchanged; the Dashboard also offers a renewal link for the IT contact (Admin Portal). That is a different certificate from WorkOS's own request-signing certificate on the SP metadata URL. The exact error your app sees when stale: verify in your tenant. |
| S8 | Clock skew | See below | Not stated in the docs I read. |
| S9 | Wrong domain | Sign in as `someone@guest.example.org` | Documented: `profile_not_allowed_outside_organization`, unless the domain is added to the org or support relaxes the policy. |
| S10 | Expired setup link | Use a stale Admin Portal link | Dashboard-shared links expire after 30 days or on setup completion; only one is active; an API-generated portal link expires after 5 minutes and cannot be revoked. The page you see: verify in your tenant. |
| S11 | Duplicate email | Two Okta users, same email | Your app's result: verify in your tenant. |

S8 is the honest one: you cannot move Okta's or WorkOS's clock, so the only skew you can test is yours. Run the lesson 4 offset test against your webhook receiver (a correctly signed request 600 seconds old is rejected) and check your app's session lifetimes. Do not claim you tested SAML `NotOnOrAfter` handling.

## The SCIM matrix

| # | Case | Expected, if documented |
|---|------|-------------------------|
| D1 | Assign a user to the SCIM app | `dsync.user.created` webhook, and a directory user visible in the Dashboard. |
| D2 | Change an attribute | `dsync.user.updated` with `previous_attributes` showing the shallow diff. |
| D3 | Add or remove a group member | `dsync.group.user_added` or `dsync.group.user_removed`. |
| D4 | Deactivate in Okta | Sources differ in emphasis: the events page says most providers soft-delete, giving `dsync.user.updated` with `state` `inactive`; the Handle Inactive Users page says the default "secure flow" deletes inactive users, and that environments created after 19 Oct 2023 behave that way. So the difference is a per-environment inactive-user setting (secure flow deletes, giving `dsync.user.deleted`; a custom management flow retains, giving `dsync.user.updated` with `state` `inactive`, and WorkOS support enables it), not Okta varying by tenant. Handle both shapes as a deprovision signal; `dsync.user.deleted` is a user event, not a group-membership one. Record which event you got. |
| D5 | Duplicate email or external ID | Docs: the request is declined and that user will not sync until the conflict is fixed. |
| D6 | Username change | Docs: most providers then re-provision the person as a new user; map `userName` to a stable value. |
| D7 | Revoke the bearer token | Requests using it fail immediately after revocation; up to two tokens can be active, so rotate by generating a second first. |

Okta's side of D1 to D4 is the Provisioning tab, the "To App" options (Create Users, Update User Attributes, Deactivate Users) and Push Groups, per the WorkOS Okta SCIM guide. A missed webhook can be reconciled with `GET /events` (the `events` type filter is required).

## Debugging toolkit

Work from the browser inward: (1) the Network panel with **Preserve log** on (Chrome keeps all requests until you disable it), so the redirect chain through your callback survives navigation; (2) SAML-tracer, a browser extension (its README lists Firefox and Chrome & Edge) that decodes SAML messages, which pass through the browser because WorkOS uses the HTTP POST binding to receive responses; (3) Okta's System Log under Reports in the Admin Console (events are kept 90 days per Okta); (4) WorkOS: for `server_error` the docs point at the Sessions tab on the connection page, the endpoint detail page has Send test event, staging allows manual webhook retry from the Dashboard, and the Events API reconciles. I could not confirm a general request-log page in the WorkOS Dashboard, so do not plan around one.

Triage order when a login fails, cheapest signal first:

1. Did your callback get `error` and `error_description`? Look the code up in the authorization-URL error table; each code names a different layer (selector, connection state, domain policy, IdP denial).
2. Did it get `server_error`? Open the connection's Sessions tab in the Dashboard before touching the IdP.
3. Did the browser never come back at all? Read the Network panel for the last hop, then SAML-tracer for what the IdP actually posted, then the Okta System Log for whether Okta issued anything. Each of the three tells you which side of the SAML POST the failure lives on.
4. Did the callback succeed but your app misbehave? Print the profile fields from lesson 4 and compare `organizationId` and `connectionId` with what you expect before suspecting WorkOS.

## Capturing evidence without leaking

Secrets that appear in good evidence: `sk_` API keys, webhook signing secrets, SCIM bearer tokens (shown once at creation), SAML responses and authorization `code` values, session cookies, Okta client secrets and private keys, org and tenant ids, real names and emails. Chrome's default HAR export is "sanitized" (mainly `Cookie`, `Set-Cookie` and `Authorization` headers are stripped), but the SAML response travels in a POST form body and the code in a URL, so do not treat a HAR as safe. Rules: use opaque boxes, not blur; re-open the exported file to check; save only the redacted copy; keep an index like this one.

```text
ID   | Proves                               | File             | Redacted                  | Date
S9   | wrong domain rejected, error shown   | s9-domain.png    | org id, email, tab URL    | 2026-10-03
D2   | dsync.user.updated carries diff      | d2-event.png     | directory id, email       | 2026-10-03
``` If a one-time secret ever appears in a screenshot, chat or terminal log, it is burned: rotate it.

## Teardown checklist

Each line ends with what happens if you skip it.

- [ ] **SCIM bearer tokens first:** revoke them, then delete the directory. Skipped: a token that outlives its directory is a credential you can no longer see or manage; revoked tokens fail immediately.
- [ ] **WorkOS connections, directories, organizations:** delete them; the API deletes are permanent (`DELETE /connections/{id}`, `/directories/{id}`, `/organizations/{id}`). Skipped: stale test data and live connections in the environment you later demo from.
- [ ] **Webhook endpoints:** delete or disable them (`DELETE /webhook_endpoints/{id}`). Skipped: deliveries keep retrying into a dead tunnel. I found no doc on how long a secret stays valid for an undeleted endpoint, so treat it as live until the endpoint is gone.
- [ ] **API keys:** rotate or delete the staging key you used; confirm the path in the Dashboard, I did not verify it. Skipped: a key that sat in shell history, a screenshot or a tunnel inspector stays valid.
- [ ] **Tunnels:** stop the process; if an ngrok authtoken was ever pasted anywhere, remove it from the machine and revoke or rotate it in the ngrok dashboard (I did not verify that path). Deleting the local copy alone revokes nothing. Skipped: an open public path to your laptop.
- [ ] **Terraform:** first check the `org_name` your variables point at is the sandbox org, then run `terraform plan -destroy -out=destroy.tfplan`, read every line, and apply that file (lesson 5's allowlist guard is what stops a copied `terraform.tfvars` from aiming this at a real org; if you skipped the guard, do not run this step until you have added it). Confirm in the console, delete state and plan files and the `OKTA_API_*` variables, then deactivate and delete the Terraform OAuth service app in Okta (this removes its admin role), not just its key. It is not in your config, so destroy never touches it. Skipped: orphaned apps and a credential that can still write to the org.
- [ ] **IdP apps and test users:** deactivate, then delete, the Okta SAML and SCIM apps and the synthetic users, plus the Entra and Google equivalents from lesson 2. Skipped: stale apps and users. I expect Okta to log provisioning failures against a deleted directory but did not verify it; check the System Log.
- [ ] **Secrets that touched a third party:** rotate any webhook secret, token or key pasted into a ticket, chat or screenshot. Payload bodies cross the tunnel provider, so keep PII out of them.
- [ ] **DNS:** remove TXT records created for domain verification, and any CNAME you pointed at a tunnel hostname. Skipped: dangling records, and a CNAME to a hostname someone else could claim.

## Your task

Done when you have: (1) the SSO and SCIM matrices filled with observed results, each "verify in your tenant" turned into a recorded observation or an explicit "not reproducible"; (2) a redacted evidence index with one artifact per case; (3) the teardown checklist ticked with a console screenshot of each empty list; (4) a one-paragraph note of every place your tenant disagreed with the docs. The disagreements are the part a hiring manager reads.
