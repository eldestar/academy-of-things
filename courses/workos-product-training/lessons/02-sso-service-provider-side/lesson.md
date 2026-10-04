# SSO from the service-provider side

You have configured SAML and OIDC apps in Okta for years. This lesson is the other end of the wire: what the vendor's code and WorkOS do with the assertion after Okta signs it. Facts checked 2026-10-03 against the WorkOS docs, the OpenAPI spec (head `v0.123.0`, 2026-10-02) and `@workos-inc/node` 11.0.0. Where the docs disagree with each other, both versions are stated.

## The flow, from behind the ACS URL

The first surprise: the vendor's app is not the SAML service provider. WorkOS is. The SP Entity ID, the ACS URL and the SP metadata you paste into Okta belong to WorkOS (the docs call them "Service Provider Details" on the connection). The vendor's app is an OAuth 2.0 client of WorkOS, which the docs describe as abstracting the IdP handshakes for SAML and OIDC alike.

1. The app calls `getAuthorizationUrl` with exactly one selector: `organization`, `connection` or `provider`. It also passes `redirectUri` and an optional `state`.
2. WorkOS sends the user to the IdP. By default the SAML request goes by HTTP-Redirect binding and the response comes back by HTTP-POST; support can switch a connection to POST for IdPs that need it.
3. The IdP posts the assertion to WorkOS. WorkOS verifies it and redirects to the app's redirect URI with `code` (valid 10 minutes) and your `state`.
4. The app exchanges `code` for a profile (`POST /sso/token`). The reference conflicts with itself on the token lifetime: the sample response says `expires_in: 600`, the field text says access tokens expire 5 minutes after creation. Exchange immediately and do not rely on either number.

```js
// Express, shaped like the docs' quick start plus a state check and an org check
app.get('/auth', (req, res) => {
  const organization = orgByTeam[req.query.team];          // your own table: team -> org_...
  const state = crypto.randomBytes(16).toString('hex');
  pending.set(state, req.query.team);                       // use a session or signed cookie in real code
  res.redirect(workos.sso.getAuthorizationUrl({ organization, redirectUri, clientId, state }));
});
app.get('/callback', async (req, res) => {
  const { code, state, error } = req.query;
  if (error) return res.status(400).type('text/plain').send('SSO error');   // error codes arrive as query params; never echo them
  const team = pending.get(state); pending.delete(state);
  if (!team) return res.sendStatus(400);
  const { profile } = await workos.sso.getProfileAndToken({ code, clientId });
  if (profile.organizationId !== orgByTeam[team]) return res.sendStatus(401);
  res.redirect('/');                                        // after you create your own session for the matched user
});
```

I ran a near-identical script against a local mock of the token endpoint (Node 24, SDK 11.0.0). The URL it builds is `https://api.workos.com/sso/authorize?client_id=...&organization=org_test_idp&redirect_uri=...&response_type=code&state=...`; a replayed `state` was rejected, a profile from another organization returned 401, and `error=signin_consent_denied` returned 400. The real token exchange was not exercised.

## Organizations, connections and profiles

An **organization** is your customer. A **connection** is one IdP configuration under it (types like `OktaSAML`, `AzureSAML`, `GenericOIDC`; states `requires_type`, `draft`, `active`, `validating`, `inactive`, `deleting`). A **profile** is the normalized user the exchange returns: `id` (WorkOS-assigned), `idp_id`, `connection_id`, optional `organization_id`, `email`, names, `role`/`roles`, and `custom_attributes`. The older `raw_attributes` is deprecated and the docs scheduled it to return an empty object from April 15, 2026 (already past); read `custom_attributes` instead.

Selecting by `organization` is the docs' preferred path, but if an organization has several connections WorkOS returns `ambiguous_connection_selector` and tells you to pass `connection`. The Admin Portal guide states that organizations may only have one connection. Those two statements conflict. Test it in your own environment before you promise a customer a second IdP (for example a migration from Okta to Entra).

> **Two guards, not one.** WorkOS rejects a profile whose email domain is not a verified domain of the organization (`profile_not_allowed_outside_organization`), because IdP admins can mint any address. Support can relax that for guests. The docs then say your callback must check `organizationId`, never email domain. A guest-friendly environment makes your own check the only guard.

## SP-initiated versus IdP-initiated

SP-initiated starts at the app. IdP-initiated is the Okta dashboard tile, and per the session docs it exists only for SAML; OIDC is always SP-initiated. The docs contradict each other on what happens next:

- The quick start says IdP-initiated sessions use the default redirect URI, and the customer can override it with `RelayState`.
- The Login Flows page says WorkOS redirects to a *sign-in endpoint* you configure, appending `connection_id`, and your code starts an ordinary SP-initiated request from there, specifically to avoid an unsolicited SAML response. `RelayState` supports only `client_id` and `redirect_uri`.
- A third data point: the error `idp_initiated_sso_disabled` means IdP-initiated SSO is off for that connection, and support can change it.

The SAML profile spec explains why vendors care: an unsolicited response must not carry `InResponseTo` (SAML Profiles section 4.1.4.3). WorkOS's Rippling guide tells the admin to tick a "Disable InResponseTo ... for IdP initiated SSO" box so both flows work. I cannot tell you which page is current. WorkOS's Test SSO page has an IdP-initiated scenario it calls a flow developers forget; run it, and run it again against each real IdP type. The sign-in consent screen always shows on a user's first IdP-initiated login.

## What WorkOS normalizes

Per IdP type, WorkOS maps attributes into the profile. For generic SAML it expects `id`, `email`, `firstName`, `lastName` (and `groups` for role mapping); the Okta guide sets `id` to `user.id`; the Entra guide uses the `.../2005/05/identity/claims/` URIs, with `name` mapped to the UPN; OIDC uses `sub`, `email`, `given_name`, `family_name`, `name`. Unmappable attributes come back `null`. `idp_id` and `email` are strictly required.

The generic SAML and Okta guides require an `id` attribute. Other guides configure NameID instead (Google: Name ID = primary email, and "Google SAML does not provide the option to map a user's id attribute claim"; Duo: pick the NameID that is your unique identifier), and the Entra guide maps no `id` claim. The docs I read do not say which source WorkOS uses for `idp_id` in those cases. In the SAML core spec a persistent NameID is an opaque identifier, so an email NameID is a poor stable key; check `idp_id` on a real profile. The Dashboard's Attribute Mapper and its count of profiles "awaiting reconciliation" are where this shows up.

## What breaks at 2am

- **Certificate rotation.** The docs say IdP response-signing certs are typically valid 1 to 5 years. A *monitored metadata URL* is refreshed by WorkOS; a manual upload goes stale silently. WorkOS warns within 90 days and emits `connection.saml_certificate_renewal_required` with `days_until_expiry` (weekly once expired). The API can pre-import the next cert (`POST /connections/{id}/saml_idp_signing_certs`); old certs keep working until deleted or expired. Request-signing certs are the reverse: WorkOS rotates them and the IdP must watch the SP metadata URL.
- **Clock skew.** The spec says the bearer `NotOnOrAfter` is checked "subject to allowable clock skew" without a number, and the WorkOS pages I fetched give no tolerance. Do not guess. Open the Dashboard session detail first (Organization, Connection, Sessions: 90 days, request and response shown). Sessions also time out after 5 minutes in progress.
- **Group claims.** Okta's `groups` filter of `.*` on a user with many groups can make the response too large and fail with `Payload too large`. Entra omits the group list above 150 groups, and WorkOS then falls back to the default role.
- **Signing options.** Signed assertions are required. A signed envelope and encrypted assertions are available through support; encrypted attributes are unsupported.
- **Logout.** Single Logout is only for OIDC "and limited scenarios", so a SAML user's app session usually outlives an IdP termination. Lesson 3 is the other half of that fix.

## Your task

Local part, run on this machine: build a sample IdP metadata file with a 45-day cert and check it.

```bash
xmllint --xpath 'string(//*[local-name()="KeyDescriptor"][not(@use) or @use="signing"]//*[local-name()="X509Certificate"])' metadata.xml \
 | tr -d ' \n' | base64 -d | openssl x509 -inform DER -noout -subject -enddate -checkend $((90*86400))
```

```text
subject=CN=sample-idp.example
notAfter=Nov 18 04:07:41 2026 GMT
Certificate will expire
```

Real-tenant part, written from the docs, not run against a live tenant: point the same command at your own IdP's metadata URL (only the first signing cert is checked, so rollovers need a loop), then run the four scenarios on WorkOS's Test SSO page (SP-initiated, IdP-initiated, guest domain, error response) against `org_test_idp` in staging.

Next: lesson 3 covers Directory Sync, the SCIM half.
