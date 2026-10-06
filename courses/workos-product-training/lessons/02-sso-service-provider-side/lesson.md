# SSO from the service-provider side

You have configured SAML and OIDC apps in Okta for years. This lesson is the other end of the wire: what the vendor's code and WorkOS do with the assertion after Okta signs it. Facts checked 2026-10-03 against the WorkOS docs, the OpenAPI spec (head `v0.123.0`, 2026-10-02) and `@workos-inc/node` 11.0.0. Where the docs disagree with each other, both versions are stated.

## The flow, from behind the ACS URL

The first surprise: the vendor's app is not the SAML service provider. WorkOS is. The SP Entity ID, the ACS URL and the SP metadata you paste into Okta belong to WorkOS (the docs call them "Service Provider Details" on the connection). The vendor's app is an OAuth 2.0 client of WorkOS, which the docs describe as abstracting the IdP handshakes for SAML and OIDC alike.

<!-- diagram:saml-sp-initiated -->
<div style="position:relative;margin:20px 0">
<input type="checkbox" id="aot-pause" class="aot-cb" /><label for="aot-pause" class="aot-btn"><span class="aot-off">Pause animation</span><span class="aot-on">Play animation</span></label>
<div class="aot-box" style="overflow-x:auto">
<svg class="aot-flow" viewBox="0 0 760 695" role="img" aria-labelledby="aot-t aot-d" style="width:100%;min-width:640px;max-width:800px;height:auto;display:block;margin:0 auto">
<title id="aot-t">SP-initiated SAML sign-in through WorkOS</title>
<desc id="aot-d">Three parties: the vendor app, WorkOS, and the identity provider. The app redirects the browser to WorkOS, WorkOS redirects to the IdP with a SAML request, the IdP posts a signed assertion to WorkOS, WorkOS redirects back to the app with a code, and the app exchanges the code for a profile server to server. The diagram highlights each step in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
<style>
.aot-box{fill:var(--panel);stroke:var(--border-strong);stroke-width:1.5}
.aot-hot{fill:var(--panel);stroke:var(--accent);stroke-width:2.5}
.aot-ttl{fill:var(--text);font:600 15px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.aot-sub{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.aot-life{stroke:var(--border-strong);stroke-width:1.5;stroke-dasharray:4 5}
.aot-front{stroke:var(--accent);stroke-width:2;fill:none}
.aot-back{stroke:var(--muted);stroke-width:2;stroke-dasharray:7 5;fill:none}
.aot-bad{stroke:var(--bad);stroke-width:2;fill:none}
.aot-main{fill:var(--text);font:600 13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.aot-badt{fill:var(--bad-text)}
.aot-dim{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.aot-badge{fill:var(--accent)}
.aot-b-back{fill:var(--muted)}
.aot-b-bad{fill:var(--bad)}
.aot-b-good{fill:var(--good)}
.aot-bt{fill:var(--on-accent);font:700 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.aot-note{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.aot-note-good{fill:var(--good-bg);stroke:var(--good);stroke-width:1.5}
.aot-note-bad{fill:var(--bad-bg);stroke:var(--bad);stroke-width:1.5}
.aot-nt{fill:var(--body);font:12.5px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.aot-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:16s;animation-timing-function:linear;animation-iteration-count:infinite}
.aot-pk.aot-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.aot-pk.aot-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.aot-g{opacity:.45;animation-duration:16s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.aot-flow:hover .aot-g,svg.aot-flow:hover .aot-pk{animation-play-state:paused}
.aot-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.aot-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.aot-btn:hover{background:var(--hover)}
.aot-cb:focus-visible + .aot-btn{outline:2px solid var(--accent);outline-offset:2px}
.aot-cb:checked + .aot-btn .aot-off,.aot-cb:not(:checked) + .aot-btn .aot-on{display:none}
.aot-cb:checked ~ .aot-box .aot-g,.aot-cb:checked ~ .aot-box .aot-pk{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.aot-g{animation:none;opacity:1}.aot-pk{animation:none;display:none}.aot-btn{display:none}}
@keyframes aot-g0{0%{opacity:1}14.286%{opacity:1}14.296%,100%{opacity:.45}}
@keyframes aot-p0{0%,-0.01%{opacity:0;transform:translateX(0)}0%{opacity:1;transform:translateX(0)}14.286%{opacity:1;transform:translateX(236px)}14.296%,100%{opacity:0;transform:translateX(236px)}}
.aot-g0{animation-name:aot-g0}.aot-p0{animation-name:aot-p0}
@keyframes aot-g1{0%,14.276%{opacity:.45}14.286%{opacity:1}28.571%{opacity:1}28.581%,100%{opacity:.45}}
@keyframes aot-p1{0%,14.276%{opacity:0;transform:translateX(0)}14.286%{opacity:1;transform:translateX(0)}28.571%{opacity:1;transform:translateX(236px)}28.581%,100%{opacity:0;transform:translateX(236px)}}
.aot-g1{animation-name:aot-g1}.aot-p1{animation-name:aot-p1}
@keyframes aot-g2{0%,28.561%{opacity:.45}28.571%{opacity:1}42.857%{opacity:1}42.867%,100%{opacity:.45}}
.aot-g2{animation-name:aot-g2}
@keyframes aot-g3{0%,42.847%{opacity:.45}42.857%{opacity:1}57.143%{opacity:1}57.153%,100%{opacity:.45}}
@keyframes aot-p3{0%,42.847%{opacity:0;transform:translateX(0)}42.857%{opacity:1;transform:translateX(0)}57.143%{opacity:1;transform:translateX(-236px)}57.153%,100%{opacity:0;transform:translateX(-236px)}}
.aot-g3{animation-name:aot-g3}.aot-p3{animation-name:aot-p3}
@keyframes aot-g4{0%,57.133%{opacity:.45}57.143%{opacity:1}71.429%{opacity:1}71.439%,100%{opacity:.45}}
.aot-g4{animation-name:aot-g4}
@keyframes aot-g5{0%,71.419%{opacity:.45}71.429%{opacity:1}85.714%{opacity:1}85.724%,100%{opacity:.45}}
@keyframes aot-p5{0%,71.419%{opacity:0;transform:translateX(0)}71.429%{opacity:1;transform:translateX(0)}85.714%{opacity:1;transform:translateX(-236px)}85.724%,100%{opacity:0;transform:translateX(-236px)}}
.aot-g5{animation-name:aot-g5}.aot-p5{animation-name:aot-p5}
@keyframes aot-g6{0%,85.704%{opacity:.45}85.714%{opacity:1}100%{opacity:1}100.01%,100%{opacity:.45}}
@keyframes aot-p6{0%,85.704%{opacity:0;transform:translateX(0)}85.714%{opacity:1;transform:translateX(0)}100%{opacity:1;transform:translateX(-236px)}100.01%,100%{opacity:0;transform:translateX(-236px)}}
.aot-g6{animation-name:aot-g6}.aot-p6{animation-name:aot-p6}
</style>
<defs>
<marker id="aot-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="aot-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="aot-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<line class="aot-life" x1="110" y1="72" x2="110" y2="643"/>
<line class="aot-life" x1="380" y1="72" x2="380" y2="643"/>
<line class="aot-life" x1="650" y1="72" x2="650" y2="643"/>
<rect class="aot-box" x="20" y="10" width="180" height="62" rx="10"/><text class="aot-ttl" x="110" y="36">Vendor app</text><text class="aot-sub" x="110" y="56">OAuth 2.0 client of WorkOS</text>
<rect class="aot-hot" x="290" y="10" width="180" height="62" rx="10"/><text class="aot-ttl" x="380" y="36">WorkOS</text><text class="aot-sub" x="380" y="56">the SAML service provider</text>
<rect class="aot-box" x="560" y="10" width="180" height="62" rx="10"/><text class="aot-ttl" x="650" y="36">Okta (any IdP)</text><text class="aot-sub" x="650" y="56">the side you already run</text>
<g class="aot-g aot-g0">
<text class="aot-main" x="245" y="108">redirect to /sso/authorize</text>
<text class="aot-dim" x="245" y="124">organization, redirect_uri, state</text>
<line class="aot-front" x1="124" y1="138" x2="366" y2="138" marker-end="url(#aot-m-front)"/>
<circle class="aot-badge aot-b-front" cx="110" cy="138" r="12"/><text class="aot-bt" x="110" y="142.5">1</text>
</g>
<g class="aot-g aot-g1">
<text class="aot-main" x="515" y="178">SAML request</text>
<text class="aot-dim" x="515" y="194">HTTP-Redirect by default</text>
<line class="aot-front" x1="394" y1="208" x2="636" y2="208" marker-end="url(#aot-m-front)"/>
<circle class="aot-badge aot-b-front" cx="380" cy="208" r="12"/><text class="aot-bt" x="380" y="212.5">2</text>
</g>
<g class="aot-g aot-g2">
<rect class="aot-note" x="556" y="242" width="188" height="48" rx="8"/>
<text class="aot-nt" x="650" y="263">user signs in at the IdP</text>
<text class="aot-nt" x="650" y="280">(MFA, your policies)</text>
</g>
<g class="aot-g aot-g3">
<text class="aot-main" x="515" y="324">signed assertion</text>
<text class="aot-dim" x="515" y="340">HTTP-POST to the ACS URL</text>
<line class="aot-front" x1="636" y1="354" x2="394" y2="354" marker-end="url(#aot-m-front)"/>
<circle class="aot-badge aot-b-front" cx="650" cy="354" r="12"/><text class="aot-bt" x="650" y="358.5">3a</text>
</g>
<g class="aot-g aot-g4">
<rect class="aot-note" x="305" y="388" width="150" height="31" rx="8"/>
<text class="aot-nt" x="380" y="409">WorkOS verifies it</text>
</g>
<g class="aot-g aot-g5">
<text class="aot-main" x="245" y="453">redirect to your redirect_uri</text>
<text class="aot-dim" x="245" y="469">code (valid 10 min) and state</text>
<line class="aot-front" x1="366" y1="483" x2="124" y2="483" marker-end="url(#aot-m-front)"/>
<circle class="aot-badge aot-b-front" cx="380" cy="483" r="12"/><text class="aot-bt" x="380" y="487.5">3b</text>
</g>
<g class="aot-g aot-g6">
<text class="aot-main" x="245" y="523">POST /sso/token</text>
<line class="aot-back" x1="124" y1="537" x2="366" y2="537" marker-end="url(#aot-m-back)"/>
<circle class="aot-badge aot-b-back" cx="110" cy="537" r="12"/><text class="aot-bt" x="110" y="541.5">4</text>
<text class="aot-main" x="245" y="577">returns the profile</text>
<line class="aot-back" x1="366" y1="591" x2="124" y2="591" marker-end="url(#aot-m-back)"/>
</g>
<circle class="aot-pk aot-p0" cx="130" cy="138" r="5.5"/>
<circle class="aot-pk aot-p1" cx="400" cy="208" r="5.5"/>
<circle class="aot-pk aot-p3" cx="630" cy="354" r="5.5"/>
<circle class="aot-pk aot-p5" cx="360" cy="483" r="5.5"/>
<circle class="aot-pk aot-p6 aot-pkback" cx="360" cy="591" r="5.5"/>
<line class="aot-front" x1="40" y1="671" x2="70" y2="671"/>
<text class="aot-dim" x="78" y="675" style="text-anchor:start">through the user's browser</text>
<line class="aot-back" x1="278" y1="671" x2="308" y2="671"/>
<text class="aot-dim" x="316" y="675" style="text-anchor:start">server to server</text>
</svg>
</div>
</div>
<!-- /diagram:saml-sp-initiated -->

The numbers match the steps below; step 3 covers both the assertion post (3a) and the redirect back with the code (3b).

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
