# Competitors, pros and cons, reliability

You can already tell good identity vendors from bad ones; this lesson gives you the WorkOS-specific evidence. Everything here was checked on 2026-10-03 against vendor pages, WorkOS's status page and postmortems, GitHub and Hacker News. Where a number or claim comes from a vendor about itself, or from a competitor about WorkOS, the text says so. Where I did not check something, it says that too.

## The map

WorkOS sells to the SaaS vendor and meters enterprise features per customer connection. The alternatives split by where they sit.

- **Auth0 (Okta Customer Identity Cloud).** The general-purpose incumbent, broad and extensible, metered by monthly active users. Not price-checked this session; check the live plan pages before comparing.
- **Clerk.** Strong React and Next.js developer experience. Its pricing page shows 1 SSO connection and 1 Directory Sync connection included, and says Directory Sync billing starts January 1, 2027.
- **Stytch.** The nearest architectural peer, B2B-focused. Twilio's own post says it completed the acquisition on 2025-11-14. The pricing page shows a $0 base price with 10,000 MAU and 5 SSO or SCIM connections free, then $125 per additional connection (WorkOS includes 1M free MAU; Stytch's rate beyond 10,000 members is not published). Treat the roadmap as Twilio's now.
- **Ory, BoxyHQ, Polis.** Ory's own post says it acquired BoxyHQ and renamed Jackson to Ory Polis, a self-hostable SAML/OIDC SSO and SCIM service. GitHub shows `ory/polis` under Apache-2.0, with a push as recent as 2026-07-27.
- **Keycloak, FusionAuth.** Self-hosted, so you trade per-connection fees for operating them. Not price-checked.
- **Cognito, Microsoft Entra External ID.** Cloud-native choices for teams already in AWS or Azure. Not price-checked, and I did not check how either handles per-customer self-serve IdP onboarding.
- **Frontegg, Descope, PropelAuth.** Hosted B2B-leaning rivals. Not checked this session.

Positioning here is my synthesis. Only dated numbers and named facts above were checked.

## A worked per-connection price

The pricing page lists SSO tiers of $125 for connections 1-15, $100 for 16-30, $80 for 31-50 and $65 for 51-100, and Directory Sync uses the same table. "Connection" means one enterprise customer's identity relationship, billed the same whatever the IdP or head count. The page does not say whether a tier price applies to every connection or only to the connections inside that tier. The page's own calculator script computes it as graduated (marginal), and I use that reading. Confirm in writing with sales before you quote it.

```text
SSO, 40 connections:   15 x $125 = $1,875
                       15 x $100 = $1,500
                       10 x  $80 =   $800        -> $4,175/month (avg $104.38)
Whole-volume reading:  40 x  $80 = $3,200        -> $975 lower; not what the calculator does
Directory Sync, 25:    15 x $125 + 10 x $100     -> $2,875/month
Audit log extras:      5 SIEM streams x $125 = $625; 10M events stored x $99/M = $990
Custom domain:         $99
Total/month:           4,175 + 2,875 + 625 + 990 + 99 = $8,764  (about $105K/year)
```

Caveats: the FAQ says each enterprise customer with SSO or Directory Sync counts as one connection, yet SSO and Directory Sync are separate calculators. I could not tell whether a customer using both is one connection or two; the FAQ's wording, "Each enterprise customer you support with SSO or Directory Sync is counted as one connection", leans toward one per customer. The calculator script also contains a fifth tier ($50, connections 101-200) that the visible page does not show. AuthKit adds nothing below 1M MAU.

I reproduced this arithmetic with a short Python script rather than by hand.

Against Stytch's published terms (5 free, $125 beyond, SSO only; this ignores that Stytch includes only 10,000 free MAU against WorkOS's 1M) WorkOS costs more up to 35 connections and less from 36 (at 40: $4,175 against $4,375). The real driver is your customers' contract values: at 15 connections you pay $22,500 a year, which is trivial for $200K deals and a margin problem for $5K deals.

## Lock-in and migration

Password hashes decide how painful an exit is. As of today, Auth0 and Clerk are from the vendors' own docs; the Stytch, Descope and Cognito rows are from WorkOS's migration guides (a competitor's account):

- **Auth0:** not available through the API. Request it by support ticket; the export is PGP-encrypted, asks another tenant admin to confirm (skipped if you are the sole admin) and a signed acknowledgment from a VP or above, and the download link lasts 3 days. Not available on the Free plan, and not every request qualifies.
- **Clerk:** admins can download a CSV from the dashboard that includes hashed passwords.
- **Stytch (per WorkOS's guide):** contact support for a hashed-password export.
- **Descope (per WorkOS's guide):** no direct API access; support generates a CSV.
- **Cognito (per WorkOS's guide):** the guide says Cognito offers no export of password hashes or MFA keys. I did not find AWS's own wording.
- **WorkOS itself:** the public User object has no password-hash field, and the docs describe importing hashes (`password_hash` with a type such as bcrypt) but no export. Better Auth, a competitor, states WorkOS "does not provide an export of password hashes at this time". WorkOS's docs are silent on the point, so ask support in writing. On the import side, WorkOS has guides for Auth0, Clerk, Stytch, Cognito and Descope (also Firebase, Supabase and Better Auth), but none for Ory, Keycloak, FusionAuth, Entra, Frontegg or PropelAuth.

> Not verified: whether Keycloak's documented CLI user export includes credentials, and the hash-export position of Entra External ID, FusionAuth, Frontegg and PropelAuth.

Keycloak documents a CLI user export. Connections are the other half of lock-in: each customer's IdP admin has your SP details configured, so in my read moving them is a customer-facing project.

## Reliability, from WorkOS's own record

- **2025-10-20 and 21.** Two incident periods, starting 06:50 UTC and 18:55 UTC. The first followed an AWS us-east-1 failure: AuthKit failed 100% and SSO about 50%, Directory Sync about 2%. The second traced to a feature-flag provider whose SDK default hung requests. WorkOS committed to multi-region hot standby by end of Q1 2026. I found no published confirmation that it shipped; the Vault docs mention multi-region failover as of February 2026, which is partial evidence at most.
- **2025-12-05.** A critical status incident touching six components (Dashboard, SSO, Admin Portal, Directory Sync, Audit Logs, AuthKit), about 35 minutes.
- **2026-07-16.** About 08:00 to 10:10 UTC: an ORM bug let one request hold a database connection while waiting for a second. SSO login errored about 58% overall (peak about 85%), AuthKit login about 45%, token refresh about 41%. Directory Sync and Audit Logs were unaffected.
- **2026-10-01.** About one minute of Audit Logs errors (lesson 4).
- **Count.** From 2025-11-18 to 2026-10-01 the status API lists 50 incidents by WorkOS's own labels: 1 critical, 24 major, 14 minor, 11 none. Six were webhook delivery delays.

The pricing page lists a 99.99% SLA on Annual Credits. The SLA text is public at workos.com/legal/sla (the pricing footer's "Enterprise SLA" link). It counts a minute as downtime when a covered service returns more than 10% 5xx, above a request threshold; its table lists SSO, Audit Logs and Directory Sync. Credits are 10% or 20% of monthly billing, you must ask support within the following calendar month, and staging and beta features are excluded. It defines Valid Request only for those three services, so whether AuthKit errors count depends on your Enterprise-tier agreement. The July 2026 event ran about 130 minutes with SSO errors around 58% overall (peak about 85%), which would plausibly count for SSO if your plan applies, but credits still need a request. SAMLStorm is the other fact: CVE-2025-29775 is a critical `xml-crypto` bug (GitHub advisory, 2025-03-14); WorkOS says it patched all customers within a day, a self-reported timeline.

## Pros and cons, by source

Vendor claims: easy SSO onboarding via the Admin Portal, predictable per-connection pricing (the founder said so on Hacker News in 2022), SOC 2 Type II, SOC 3 and SIG Lite compliance (WorkOS's IT FAQ), and PCI DSS by self-attested SAQ-D (changelog). Testimonials on its support-plans page are curated.

Third-party opinion: sparse and anecdotal. A Hacker News commenter in 2022 praised the predictability; a commenter in 2024 called the pricing untenable for SMB-priced B2B apps and called the major auth vendors overpriced. G2 would not load for me, so I cite no ratings.

My read: strong when enterprise deals are few and large, weak when many small customers each demand SSO, and a login-path dependency with a visible incident history.

Your task: write the two-sentence answer you would give an interviewer who asks "when would you advise against WorkOS?", using one number from this lesson.
