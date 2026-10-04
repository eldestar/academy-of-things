# WorkOS sandbox and Dashboard

This is the SP and vendor side you have never administered. The goal is a WorkOS account where you can break things safely, know which key opens which door, and can name the five or six actions that cannot be undone. Facts checked 2026-10-03 against workos.com/docs (environments, Dashboard, Admin Portal, SSO, Directory Sync and reference pages) and workos.com/pricing. **The Dashboard steps are written from the docs, not run against a live account**; I did not create one. The secret-scanning experiment near the end I did run, with real output.

## Account, team and environments

Dashboard accounts belong to exactly one team, and an email already on a team cannot be invited to another, so do not assume your work address is free to join a second team. I did not verify the sign-up form. Everything (environments, configuration, customer data) belongs to the team, and a team holds projects, which hold environments. First hardening, in Settings > Authentication (Admin role only): enroll MFA on your own profile, then require it for the team. That requirement is unavailable once the team signs in through SSO, and SSO and directory provisioning for the dashboard both need a verified domain plus an active production environment, so a lab team uses MFA. Roles include Admin, Developer and **Sandbox Developer**, which can manage staging but is read-only in production; give CI or a colleague that one.

> **Staging or sandbox?** The environments guide, billing page and quick starts say "staging". The redirect URI and Directory Sync pages say "sandbox environment", the role is called Sandbox Developer, and the MCP setting says "sandbox environments". Treat them as one thing and confirm the label in your own Dashboard; I could not.

One setting to flip early: under the WorkOS MCP section, Enable, Allow production access and Allow write access are all on by default. If you will ever connect an agent, turn off production access and write access first.

| | Staging | Production |
|---|---|---|
| Redirect URIs | `http://` and `localhost` allowed | `https://` for web apps |
| API key | viewable any time | shown once at creation |
| Test IdP | built in | none |
| Billing | free, no card | needs billing info; enterprise connections charged |
| Custom domains | no | yes |
| Rate limits | same as production | same as staging |

## Keys, client IDs and where they go

Staging ships with a pre-generated API key. API keys are prefixed `sk_`, can perform any API request, and travel as `Authorization: Bearer`; a wrong key returns 401 and a valid key without permission returns 403. The Client ID belongs to an Application: each environment starts with a default application (the first one listed), and the Applications section holds that application's API keys, Redirects and Sessions. WorkOS's docs name the variables `WORKOS_API_KEY` and `WORKOS_CLIENT_ID`; the quick start's `org_test_idp` is the staging Test Organization id.

```bash
# .env.example (committed; no values)        # real file: gitignored, per environment
WORKOS_API_KEY=
WORKOS_CLIENT_ID=
```

Staging and production share nothing: different keys, client IDs, organizations, connections and webhook endpoints. Never put the production key in the same file or shell profile as staging.

## An organization and a test connection

Fastest path: staging already has a Test Organization with an active connection on the Test Identity Provider. The Dashboard's Test SSO page walks through four scenarios: SP-initiated, IdP-initiated (disable AuthKit first), a guest email domain (the test org's verified domain is `example.com`) and an error response. Run all four against your lesson 4 app before touching a real IdP.

To make your own, create an organization (Organizations in the Dashboard, or `POST /organizations` with `name`, optional `domain_data` of `{domain, state}`, `external_id` and `metadata`). Domains added through the API start `pending` or `verified`; domains added by hand in the Dashboard count as verified automatically, and SSO needs a verified domain or users are sent back with `profile_not_allowed_outside_organization`. So the check is only as honest as what you typed: use `example.com`, never a domain you do not control. Then connect a real IdP either by "Manually Configure Connection" on the organization and picking the provider, or by inviting an IT contact (next section). Okta's guide pastes the IdP metadata URL under "Edit configuration" > Dynamic configuration; Google's uploads an XML file.

## Admin Portal link and redirect URIs

The Dashboard button that makes an Admin Portal setup link is named differently across docs:

| Label in the docs | Where |
|---|---|
| Invite IT contact | Admin Portal guide; the API reference calls the person an IT contact |
| Invite admin | Test SSO page; Vault BYOK guide; Google Directory Sync guide ("Invite Admin") |
| Invite contact | Log Streams guide |

All describe one flow: pick features, enter an email or Copy setup link. Only one dashboard link is active at a time; Manage revokes it; it expires after 30 days or on setup completion. A link generated by the API expires after 5 minutes and cannot be revoked, so redirect to it immediately and never email it.

Redirect URIs live under Applications > Redirects, with one default. A flow pointed at an undefined URI errors and users cannot sign in; a `redirect_uri` parameter overrides the default. Production forbids `http` and `localhost`, though the environments guide says `http://127.0.0.1` stays allowed for native clients, so test your actual case. Wildcards: one `*`, in the subdomain furthest from the root, never across levels, never on public suffix domains (the docs' example is `*.ngrok-free.app`), and never as the default. A port wildcard is allowed only on localhost and loopback. Your redirect URI is your app's callback, not the webhook tunnel from lesson 4.

IdP-initiated SSO is described three ways. Login Flows: configure a sign-in endpoint under the application's Redirects; WorkOS sends the user there with `connection_id` appended. The SSO guide: the default redirect URI is used, and the customer may set a separate one as `RelayState` (the Login Flows page also documents `RelayState` overrides, `client_id` and `redirect_uri`, so the pages partly reconcile). The Applications page: the default application is used. Record which behaviour the Test IdP shows.

## Limits, billing and the irreversible list

Staging is free for every connection type and needs no card. Production needs billing information even for an AuthKit-only app, which is free under 1 million monthly active users. On workos.com/pricing, SSO and Directory Sync each list tiers starting at "$125 / ea" for 1 to 15 connections (the row does not state a period; confirm on the billing page), and a custom domain is listed at $99 a month. WorkOS warns that any enterprise connection in production may count toward billing, even a test one, so do all SSO testing in staging.

Cannot be undone:

- The API deletes for a connection, directory and organization are each documented as permanent and "cannot be undone"; I did not verify whether the Dashboard offers an undo.
- Deleting the team is permanent (two-step confirmation), and a team with an active subscription needs support.
- Production API keys are shown once; lose it and you rotate.
- No promote from staging to production, and no self-serve conversion of an environment between them.
- Moving an environment into a new project is effectively irreversible.

## Secrets and the gitleaks gate

Keys go in environment variables or your secret manager, never the repo, a screenshot, a ticket or chat. Your pre-commit rule is `gitleaks protect --staged`. I ran gitleaks 8.30.1 against throwaway files holding random fake values: `protect` still ran but is not listed in `gitleaks --help`, which lists `git`, so use `gitleaks git --staged`, and update any hook or written rule that still says `protect`, since an undocumented subcommand can disappear. Real results with default rules:

```text
WORKOS_API_KEY=sk_test_<random>            -> stripe-access-token   (prefix coincidence)
export WORKOS_API_KEY="sk_test_<random>"   -> stripe-access-token
OKTA_API_TOKEN=00<random>                  -> okta-access-token
Authorization: SSWS 00<random>             -> no leak found
okta-key.pem (RSA private key)             -> private-key
```

WorkOS keys were caught only because `sk_test_` looks like a Stripe key; I did not verify the real WorkOS key format beyond the documented `sk_` prefix. An Okta token pasted as a curl header slipped through. Add a project rule and test it with a fake first.

## You are done when

- [ ] MFA is required on the team; MCP production and write access are off.
- [ ] Staging API key and Client ID are in a gitignored file, `.env.example` is committed, and a staged fake key makes your hook fail.
- [ ] You ran all four Test SSO scenarios and recorded what IdP-initiated did.
- [ ] One organization of yours exists with `example.com`, and you can state the buttons your Dashboard labels "invite".
- [ ] You have listed what you would delete on teardown (lesson 6) and nothing exists in production.

Next: lesson 4 builds the app that receives these redirects and webhooks.
