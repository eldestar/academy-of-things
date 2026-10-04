# Okta test tenant

You can build an Okta org blindfolded, so this lesson skips how and spends its time on what is different about a free test org: which one you can still get, what it cannot do, and the ways it locks you out or leaks. Facts checked 2026-10-03 against developer.okta.com, help.okta.com, okta.com and WorkOS's Okta guides. **The click paths below are written from the docs, not run against a live tenant**; where a page and the sign-up flow disagreed, both are stated. Lesson 2 adds the second and third IdP; lesson 5 drives this org with Terraform.

## Which free Okta you can still get

The sign-up page at developer.okta.com/signup offers three tiles: an Auth0 free tier (customer identity, wrong product), a 30-day Okta Platform free trial, and the **Okta Integrator Free Plan**. Developer Edition is gone: Okta's 2025-05-13 blog says new Developer Edition orgs stopped on 2025-05-22 and existing ones were deactivated starting 2025-07-18, and every old tutorial that says "sign up for a developer org" now lands you in an Integrator org. The blog also says neither type is meant for production use.

What the Integrator Free Plan reference page (checked today) lists as provisioned: SSO, Universal Directory, Adaptive MFA, Lifecycle Management, API Access Management and Workflows. Limits it states: **10 active users**, 5 Workflows, no Org2Org app integration, email templates not editable, no email automation, limited per-minute rate limits (the pricing FAQ says 100 authentications per minute), no paid support, one org per sign-up email, and some addresses refused by location or security rules. The table does not list Device Trust or FastPass, and I did not verify whether they exist in the org; check your own Admin Console before building a lab on either.

> **Inactivity clock, sources conflict.** The sign-up form and the reference page say the org deactivates after 90 consecutive days with no user sign-in (unless you submit an app to the OIN). The pricing page FAQ says 180 days. Plan on 90 and sign in monthly. With no paid support, a deactivated org is your problem alone.

The 30-day trial is the other route; its contents and what happens at day 31 are not something I verified, so treat it as disposable. Never use your employer's tenant for this, and never register the lab with the work email you already use for production Okta. The form asks for a business email; if a personal address is refused, use an address on a domain you own, not your employer's.

## First-login hardening

You will be the only admin of an org that has no support contract, so the first hardening goal is not locking yourself out. Okta's app-integration guide recommends two or three extra admin users so your team keeps access to the integration; for a one-person lab that means at least a second admin account whose recovery you control.

1. Enroll two authenticators on the first admin before doing anything else. Okta recommends at least one phishing-resistant authenticator such as FIDO2 (WebAuthn).
2. Confirm MFA is enforced for the Admin Console. Per Okta's Identity Engine page: Applications and Resources > Applications > the Okta Admin Console app > Sign On > User authentication > View policy details > Admin app policy > Actions > Edit, then require a 2-factor option under "User must authenticate with". The Classic page words the same setting as "Prompt for factor" on the Admin App Policy rule and warns that ticking "Disable rule" disables admin MFA.
3. Open HealthInsight and act on the items it lists, starting with limiting super admins (Okta rates that Critical) and enabling ThreatInsight. I did not verify the menu path; search the Admin Console for it.
4. Write the org URL, the admin usernames and where the recovery factors live in your password manager, not in the repo.

## Safe users, groups and names

Fake people only. The only reason to put a real name, email or group export in a test org is "more realistic", and that reason is never good enough: SAML assertions, SCIM payloads and screenshots all leave the org (lesson 6). Add users under Directory > People > Add person; the docs show an "I will set password" checkbox and a "User must change password on first login" box that is ticked by default. Use that path. Activation emails to synthetic addresses go nowhere, and the plan has no editable templates or email automation to rescue you.

Use `example.com` addresses. WorkOS accepts reserved example domains, never sends mail to them, and its staging Test Organization's verified domain is `example.com`, so `alice.lab@example.com` behaves. Plan five or six synthetic users, because 10 is the cap and I did not verify whether admins count; this keeps admins plus users at or under 10 either way.

Naming is not an Okta feature, so this is my convention: prefix every lab object with `wk-lab-`. One prefix makes System Log filtering and teardown trivial. Lesson 5's Terraform objects use `tflab-`; keep the two families visibly different.

```text
users   alice.lab@example.com  bob.lab@example.com  carol.lab@example.com  (carol: deactivated-user test)
groups  wk-lab-test-users  wk-lab-scim-assign  wk-lab-scim-push
apps    wk-lab-saml  wk-lab-oidc  wk-lab-scim
```

## A SAML app and an OIDC app

Admin Console > Applications and Resources > Applications > Create App Integration. Okta's developer guide says to pick Classic experience only if the org is not an Integrator Free Plan org, while WorkOS's Okta guide says to select the Classic tab; follow whichever dialog you see.

**SAML 2.0.** Name the app, then on Configure SAML enter Single sign-on URL (the ACS URL) and Audience URI (SP Entity ID). Until WorkOS exists (lesson 3), Okta's guide offers `http://example.com/saml/sso/example-okta-com` for both fields when you are only testing the setup. WorkOS then asks for these statements under Sign On > "Show legacy configuration", plus a Group attribute statement if you want role assignment:

```text
id         -> user.id
email      -> user.email
firstName  -> user.firstName
lastName   -> user.lastName
groups     -> filter: Matches regex  wk-lab-.*     (not .*)
```

WorkOS warns that matching every group can make the response too large and fail sign-in with `Payload too large`, so keep the filter narrow and test with a user in many groups. Copy the Metadata URL from Sign On, assign a user, and test from the end-user dashboard, with Reports > System Log for failures.

**OIDC.** Choose OIDC, then Web Application. Authorization Code is mandatory for web apps; add the sign-in redirect URI. WorkOS expects the Client ID, Client Secret and a Discovery Endpoint ending in `/.well-known/openid-configuration`, and claims `sub` and `email` always, plus `given_name` and `family_name` by default. WorkOS's guide builds the discovery URL as `https://{tenant-domain}/.well-known/openid-configuration`, which is the org authorization server, not `/oauth2/default`; it also says to leave "Require PKCE as additional verification" checked. Trap: the Assignments setting defaults to Everyone. In a 10-user lab it looks harmless, and it is the habit that ships an internal app to the whole company in a real org; WorkOS's guide agrees ("Limit access to selected groups"); pick `wk-lab-test-users`.

## SCIM provisioning where available

Okta's Classic documentation says SCIM is added to a custom SAML or SWA integration built in the Classic wizard (or an OIDC one built in the newer Integration Wizard), that the provisioning feature must be enabled first, and that Okta support decides whether to enable it. Without paid support, the route WorkOS documents is better: Browse App Catalog, search for "SCIM 2.0 Test App (OAuth Bearer Token)", Add Integration. Then Provisioning > Configure API Integration > Enable API Integration, paste WorkOS's Endpoint as the SCIM 2.0 Base URL and its Bearer Token, click Test API Credentials and Save. Under To App enable Create Users, Update User Attributes and Deactivate Users. I could not verify that the catalog entry works in an Integrator org; if it does not, say so in your evidence.

Three WorkOS-documented behaviours to reproduce deliberately:

- Okta does not send push-group membership removals when the user is deactivated or unassigned, which bites when one group does both assignment and push. Keep `wk-lab-scim-assign` and `wk-lab-scim-push` separate (repair: Push now).
- Suspending a user in Okta does not change their status in WorkOS; deactivating or deleting does.
- Okta supplies only a group display name, which WorkOS stores as both `idp_id` and `name`, so renaming a group creates a different identity.

## API access: token versus service app

An SSWS token goes in the header as `Authorization: SSWS <token>` and behaves like this, per Okta's token guide:

- It inherits the privileges of the admin who created it, and follows that admin's role changes, so create it from a dedicated service admin.
- It is shown once, is valid 30 days from creation or last use (fixed, not configurable), dies if its creator is deactivated, and can be pinned to a network zone.

Okta recommends scoped OAuth 2.0 instead: an API Services app, Client Credentials only, `private_key_jwt` only, access tokens fixed at one hour. Gotchas:

- Every service app needs an admin role, and is limited to what that role covers.
- The "Public client app admins" org setting auto-assigns Super Admin; leave it off.
- Only Super Admin can grant scopes; switching the app to Public key/Private key deletes existing client secrets.

Lesson 5 uses `okta.groups.manage` and `okta.apps.manage` with this setup.

## You are done when

- [ ] A screenshot of the Applications page with no "Developer Edition provides a limited number of apps" banner (redacted org URL), and the date you must next sign in by.
- [ ] Two enrolled authenticators on the first admin, a second admin account, and the Admin Console policy page showing 2-factor.
- [ ] Only `wk-lab-` objects and `example.com` users exist; no real employee data anywhere.
- [ ] SAML and OIDC apps assigned to a group, not Everyone, with one successful test sign-in visible in System Log.
- [ ] A SCIM attempt with a recorded result, success or "not available in this org".
- [ ] Token or service-app credentials stored outside the repo, scopes minimal.

Next: lesson 2 builds the Entra and Google IdPs you will compare this one against.
