# AuthKit, RBAC and FGA

Lessons 2 to 4 covered the enterprise side of a customer's identity: their IdP, their directory, their admin. This lesson covers the other half of the same product: the sign-in, session and permission layer for the vendor's own users. You will recognise the concepts from the IdP side (sessions, MFA policy, role mapping from groups), but here you choose token lifetimes and decide where authorization lives. Facts checked against the live docs, pricing page and changelog on 2026-10-03.

## AuthKit, User Management, and the naming mess

WorkOS's docs call its user-management product AuthKit: a hosted sign-in UI plus APIs for email and password, social login, MFA, Magic Auth, passkeys, SSO, invitations, organizations and memberships. The API and SDKs have not followed the rename:

- Endpoints are under `/user_management/...`.
- The Node SDK still exposes `workos.userManagement`.
- The pricing page's product menu lists both "User Management" and "AuthKit".

Same product; do not go hunting for two. Pricing (pricing page, 2026-10-03): the first 1 million monthly active users are free, then $2,500/month per additional million. A user is active if they sign up, sign in or update a profile in the calendar month. RBAC, MFA, passkeys and Magic Auth are all listed as available on all accounts.

## Sessions and JWTs

A successful sign-in returns an access token (a JWT) and a refresh token. You validate the JWT on every request against the environment's JWKS. The sessions guide lists these claims: `sub` (user), `sid` (session, used for sign-out), `iss`, `org_id`, `role`, `permissions`, `exp`, `iat`. Session length, access-token lifetime and inactivity timeout are set per application in the dashboard.

> The sessions guide shows the JWKS URL as `http://api.workos.com/sso/jwks/<clientId>`; the API reference and its curl example use `https://`. Use https.

Refresh tokens are single-use and rotate, and the failure mode is concurrency: two requests notice an expired access token and both refresh.

- **Grace period.** WorkOS applies 30 seconds in which replaying the same refresh token returns the same new tokens. After that the old token is dead and you get `invalid_grant`.
- **Terminal vs transient.** `invalid_grant` is terminal: sign the user out. Timeouts, 408, 429 and 5xx are transient: keep the session and retry with backoff. Treating a blip as terminal turns an incident into a mass sign-out. Put that line in your runbook.
- **Who handles it.** Per the docs, the framework SDKs (Next.js, Remix, React Router and others) and `authkit-js` do this for you; backend SDKs return a typed result and leave the decision to you. Older versions of some framework SDKs signed users out on any refresh failure, so version matters.
- **Org context.** `org_id`, `role` and `permissions` reflect the organization selected at sign-in. Switching means refreshing with `organization_id`; if the user is not authorised for it they must re-authenticate.

## Sign-in methods, and what each one breaks

- **MFA.** Hosted AuthKit's built-in MFA is TOTP, enabled per environment. SMS lives in a separate standalone MFA API (US numbers only) that your app integrates itself. The pricing page says "TOTP and SMS" without that distinction. The MFA requirement does not apply to SSO users; the customer's IdP policy is the control there, which is your Okta policy design to own.
- **Passkeys.** Hosted UI only today. They bind to the domain they were created on, so set an AuthKit custom domain before enabling them in production; adding one later strands every enrolled passkey. There is no self-service screen to manage them, and an admin deletes them in the dashboard. A passkey with user verification satisfies MFA.
- **Magic Auth vs Magic Link.** Magic Auth emails a six-digit code that expires in 10 minutes. The modelling guide states that WorkOS has deprecated Magic Links in favour of Magic Auth, because enterprise email scanners pre-click links and burn them. So the deprecation claim checks out, and the reason matches what you have seen with mail security gateways.
- **Identity linking.** A user is identified by verified email. A new credential attaches to an existing user only if inbox access is verified; otherwise the sign-in stops. A verified organization domain lets SSO users skip email verification; without one they must be invited first. Directory Sync and SSO users link on the IdP's stable identifier before email, so an email change does not duplicate users.
- **Invitations.** An invitation targets one email address, usually one organization (the docs also allow application-wide invitations with no organization). For consumer domains the accepting email must match exactly; for corporate domains any address on that domain works. A new user who signs up with the exact invited address within 10 minutes of the email counts as email-verified (changelog, 2026-08-13).

## Roles and permissions (RBAC)

Roles and permissions are defined per environment, their slugs are immutable, and roles are assigned to organization memberships and shipped in the JWT.

- Every membership gets the default `member` role until changed. Customers can have custom roles (an explicitly supplied custom slug must start with `org-`).
- Multiple roles per membership is an environment-wide switch, off by default.
- IdP role assignment overrides roles set by API or dashboard. With SSO group mapping the role updates on each sign-in; with directory groups it updates on each directory event. Conflicts resolve by role priority.
- Deleting a role is asynchronous.

Two failure modes. Permissions ride in the session cookie, and the docs warn of a 4 KB browser limit, so keep slugs short. And a role change made in the IdP is not instant for SSO users; it lands on their next sign-in.

## FGA: resource-scoped roles, not Zanzibar

Fine-Grained Authorization (FGA) was announced on 2026-02-17 as an extension of RBAC. You declare resource types in the dashboard (organization, workspace, project, app), register resource instances as your app creates them, define roles scoped to a type, and assign a role to an organization membership or a group on a specific resource. Permissions flow down the hierarchy. A check endpoint (`POST /authorization/organization_memberships/{id}/check`) evaluates direct, inherited and org-wide grants. Org-scoped roles stay in the JWT; resource-scoped roles deliberately do not, to avoid token bloat and staleness.

> **Old material is still out there.** WorkOS acquired Warrant, a Google-Zanzibar-style service, in April 2024 and relaunched it as WorkOS FGA. Tutorials and memories of "warrants", relation tuples and a schema DSL describe that model. Current docs describe no DSL and no tuples, and their OpenFGA, SpiceDB and Oso migration guides treat WorkOS FGA as a different approach. Old `/docs/fga/warrants` URLs now land on the new overview. The warrant.dev page's own description says Warrant "has been deprecated and is now WorkOS FGA" (vendor-stated); I did not find what that means for existing customers.

Documented limits and gaps:

- Each resource instance has exactly one parent (a type may allow several parent types), a depth of five, 50 resource types per environment, and up to 10 child types per type. The depth is called a soft limit.
- A soft 5,000 instances per type per organization. High-cardinality things like files stay in your own database and you check access on their parent.
- Subjects are organization memberships and groups only. Per-user permission exclusions are listed as coming soon.
- WorkOS markets sub-50 ms p95 checks and strong consistency. Those are vendor claims. No FGA price is on the pricing page.

## Lab: when does the token outgrow the cookie?

Ran locally; the claim set follows the documented claims, and the RS256 signature size is my assumption.

```text
5 permissions -> 911 bytes
25 permissions -> 1471 bytes
50 permissions -> 2171 bytes
100 permissions -> 3571 bytes
150 permissions -> 4971 bytes
200 permissions -> 6371 bytes
first count over 4096 bytes (18-char slugs): 119
```

The cookie also holds more than the access token, so real headroom is smaller. Your task: take a customer's Okta group-to-role model (say 40 groups) and decide which permissions stay as role-level slugs in the JWT and which belong to resource-scoped FGA checks.

Next: the newer products, what is GA and what is early access, and agent authorization.
