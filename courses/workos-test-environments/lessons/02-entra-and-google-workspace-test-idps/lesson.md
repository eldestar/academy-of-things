# Entra ID and Google Workspace test IdPs

One IdP proves your SP works with Okta. A second and third prove it works with how Microsoft and Google bend the standard: different attribute names, NameID rules, certificate lifetimes and provisioning cadence. This lesson is about getting them cheaply and legitimately, and about the traps in the "free" labels. Facts checked 2026-10-03 against Microsoft Learn, Google Workspace and Cloud Identity help, the Microsoft 365 Developer Program FAQ, WorkOS's per-IdP guides and the mock IdP's own repo. **Click paths are written from the docs, not run against a live tenant.** The certificate check in the mock IdP section I did run. Lesson 1 covers Okta; lesson 3 connects all of these to WorkOS.

## What each option can and cannot cover

| Option | SAML | Directory sync / SCIM | Catch |
|---|---|---|---|
| Okta Integrator Free (lesson 1) | yes | via OIN app, unverified in a free org | 10 active users |
| Entra ID Free tenant | custom (non-gallery) app | user provisioning listed on Free; group provisioning and group assignment need P1 or P2 | creating the tenant is gated (below) |
| Microsoft 365 Developer Program | E5 includes Entra ID P1 and P2 | same, with groups | eligibility is narrow, renewable only by activity |
| Cloud Identity Free | custom SAML app, listed on Free | automated user provisioning is Premium only | needs a domain you own; user cap raised by 50 |
| Google Workspace trial | yes | WorkOS Google sync uses an admin sign-in, not SCIM | 14 days, then billed |
| Mock SAML | yes, SAML only | nothing documented | shared public service, never real data |

## Entra ID: two ways to get a tenant

**Microsoft 365 Developer Program.** The FAQ says a free renewable E5 developer subscription (25 licenses including the admin, an "instant sandbox" with sample users, Entra ID P1 and P2 in the package list) goes to: Visual Studio Professional or Enterprise subscribers, companies in the ISV Success Program or eligible Microsoft AI Cloud Partner Program tiers, and Premier or Unified Support customers. It is not a general public free tier, and Microsoft may require identity verification. Expect a short lease: the subscription lasts up to 90 days and is extended by genuine development activity (the FAQ says it renews automatically while a Visual Studio subscription is active), Microsoft says tenants "may" need recreating every 90 days, and after expiry you get 30 days to migrate, 30 more of admin-only access, then deletion. Using it for anything but development violates the terms. If you qualify, use it; it is the only no-card route here with P1 and P2. Microsoft's P1/P2 page also links an Entra ID P2 trial; I did not verify its terms or eligibility.

**Entra ID Free via a new Azure free account.** Microsoft's tenant quickstart says only paid customers can create an additional workforce tenant and that free-tenant or trial users cannot, pointing those who need a new tenant to sign up for a free account. The Azure free-account page offers 30 days, a $200 credit and spending protection ("credit card won't be charged"); continuing past that means moving to pay-as-you-go. So: sign up with a personal Microsoft account that has no tie to your employer's tenant, never create the lab tenant from your employer's Azure portal or billing, and do not upgrade. I did not verify that sign-up creates a fresh default directory or what its domain looks like (the quickstart's example is `<name>.onmicrosoft.com`); read the tenant page and record what you got.

**What Free covers.** Microsoft's licensing table lists automated user provisioning to SaaS apps under Free but automated group provisioning under P1 and above, and the assignment page says group-based assignment needs P1 or P2. On Free, expect SCIM users without groups, and for a SAML groups claim the fallback is the Security groups option (noisier, subject to the 150-group limit, see below); confirm in your tenant.

SAML app, per WorkOS's guide: Enterprise applications, New application, Create your own application, "Integrate any other application you don't find in the gallery (Non-gallery)", Single sign-on, SAML, then Basic SAML Configuration. The App Federation Metadata URL sits under SAML Signing Certificate.

## Google: Cloud Identity Free or a Workspace trial

**Cloud Identity Free** needs your company domain plus admin access to the registrar, so you need a domain you personally own (lesson 6's DNS teardown applies). Its user cap rises by 50 on sign-up. Google's editions table lists SSO to custom SAML apps on Free and "Automated user provisioning" on Premium only.

**Workspace trial** is 14 days for up to 10 users, and payment setup comes first. The card is not charged until the trial ends, but the paid subscription then starts automatically, adding an 11th user prompts you to end the trial and starts paying for all users, and with no billing at the end the account is suspended (Google's page also says deleted, depending on signup path). Use a card with a spending limit or a virtual card, and cancel deliberately before day 14 (cancel path depends on how you signed up; read Google's page).

SAML, per Google and WorkOS: Admin console, Apps, Web and mobile apps, Add App, Add custom SAML app. Set Name ID format to **UNSPECIFIED** and Name ID to Basic Information > Primary email; WorkOS says a different format can cause a policy mismatch. Turn the service ON for the organizational unit under User access: Google says changes take up to 24 hours (typically faster) and WorkOS says the connection stays inactive until then. Google's field called Start URL is the RelayState. Google's ACS URL field must start with `https://`, so a bare localhost ACS will not work.

**Directory Sync for Google is not SCIM.** WorkOS has the organization's admin authenticate with Google from the Admin Portal, pick groups to sync (users outside the chosen groups are not synced), and syncs about every 30 minutes, with a manual sync that has a five-minute cooldown. I did not verify that this works against a Cloud Identity Free domain rather than full Workspace.

## Mock IdPs: one is dead, one is a toy

**Do not use samltest.id.** Old docs and blog posts still recommend it. Checked from my network today: plain HTTP returns `410 Gone`, the HTTPS handshake fails, and Internet Archive snapshots from 2024-10-12 and 2025-12-16 both show a "Buy this domain" page. Dataverse issue IQSS/dataverse#10872 (2024-09-24) already reports the service gone and points to Mock SAML. A parked domain is worse than a dead one: you do not want a SAML response, even a fake one, posted to a hostname someone else may buy.

**Mock SAML** (mocksaml.com; source at github.com/ory/mocksaml, Apache-2.0, previously BoxyHQ) is a free SAML 2.0 IdP for testing, with a hosted service and Docker or from-source self-hosting. Its page says "Not for production use". The login screen says you may choose any username at `example.com` or `example.org` and any password works. The root domain uses a shared entity ID; the README says you create your own at `/namespace/<name>`, and I confirmed that changes the entity ID (to `.../entityid/<name>`). I ran this:

```bash
curl -s https://mocksaml.com/api/saml/metadata | tr -d '\n ' \
  | sed -E 's/.*<ds:X509Certificate>([^<]*)<.*/\1/' | fold -w 64 \
  | { echo "-----BEGIN CERTIFICATE-----"; cat; echo; echo "-----END CERTIFICATE-----"; } \
  | openssl x509 -noout -subject -dates
# subject=C=UK, O=BoxyHQ, CN=Mock SAML
# notBefore=Feb 28 21:46:38 2022 GMT
# notAfter=Jul  1 21:46:38 3021 GMT
```

The hosted Mock SAML certificate expires in 3021, so the hosted service can never exercise expiry handling. A self-hosted instance takes your own key pair (`PUBLIC_KEY` and `PRIVATE_KEY` in its `.env.example`, generated with openssl using `-days 365000`), which should let you issue a short-lived certificate; I did not test that. Its metadata also carries `WantAuthnRequestsSigned="true"`; how WorkOS reacts to that I did not test.

**Ory Polis** (github.com/ory/polis) is not an IdP. Its repo describes an SSO service for SAML and OIDC with SCIM 2.0 directory sync: the SP-side bridge, a self-hosted analogue of what WorkOS sells.

## Quirks that matter for WorkOS, and what must stay out

| | Okta | Entra ID | Google |
|---|---|---|---|
| Attributes in WorkOS's guide | `id`, `email`, `firstName`, `lastName` | claim URIs under `/claims`: `emailaddress`, `givenname`, `name` (mapped to UPN), `surname` | no id claim available |
| Signing cert | not verified, so I cannot rule out a short lifetime | 3 years by default, expiry date adjustable up to 3 years, mail at 60, 30 and 7 days to the admin who added the app | 5 years, up to 2 at a time |
| SCIM / sync cadence | real time | about every 40 minutes; Provision on demand | about 30 minutes |
| Group identity | display name is the `idp_id` | group object ID; `objectId` mapped to `externalId` | Google group id |

Practical consequences: Entra lets you choose a near expiry date, so it is the one hosted IdP here where I confirmed you can provoke WorkOS's certificate warning (the Dashboard flags certificates within 90 days of expiry); Entra's 150-group SAML limit drops the group list entirely, so test with a user in many groups; Entra sends `dsync.user.created` and then `dsync.user.updated` for a new user by design; cloud-only Entra users may need `userPrincipalName` mapped to `emails[type eq "work"].value`; reactivated "suspended" users need Restart Provisioning. With the scope the WorkOS guide expects ("Sync only assigned users and groups"), a new assignment can wait up to one cycle; a passing credentials test says the token is accepted, not that a sync has run. On the app's Provisioning tab, "Provision on demand" sends SCIM requests immediately for one chosen user, group or group membership, so use it before touching the token or widening the scope (widening pushes people you did not mean to). Never in these tenants: employee data, your employer's domains or billing, or a Mock SAML connection in a production WorkOS environment (WorkOS warns test providers can show placeholder company names and even test connections may count toward billing).

## You are done when

- [ ] You can state which route you took for Entra and Google and why, with the eligibility or limit that decided it.
- [ ] One Entra and one Google SAML app exist, each with a user assigned and the exact Name ID or claim choices recorded.
- [ ] Your signing-certificate expiry dates are written down for Entra, Google and Mock SAML.
- [ ] No trial can bill you: payment method and cancel date for each are noted.

Next: lesson 3 wires these IdPs into a WorkOS environment.
