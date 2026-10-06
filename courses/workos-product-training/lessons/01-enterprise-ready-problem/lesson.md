# The enterprise-ready problem

**Facts checked 2026-10-03** against workos.com/pricing, WorkOS docs and blog, Grinich's 2020 Show HN thread and the live "Systems Engineer" posting. Prices and product lists move; re-check before you quote them.

You have spent twelve years on the buying side of this problem: you are the person a vendor's sales engineer is trying to get past. WorkOS is a company built to make that conversation easy for other vendors. This lesson is the business picture. Lessons 2 and 3 are the protocol picture.

## The deal that dies in procurement

A fast-growing B2B app hits its first large customer. The security review comes back with three asks, and none of them is a product feature:

- **SSO.** WorkOS's own docs call it the requirement enterprises ask for most. You know why: it is where MFA, conditional access and offboarding are enforced.
- **Directory provisioning (SCIM).** WorkOS's docs call user lifecycle management table stakes and describe manual add/remove as the way directory and app state drift apart. You know the version of that story with a leaver whose access survived.
- **Audit logs.** WorkOS describes them as a paper trail of sensitive actions kept for compliance and security reasons, not for live alerting. That is your SOC 2 evidence request, seen from the other side.

The vendor can build all three. Every vendor then discovers that each customer brings a different IdP and an admin who needs a setup guide. WorkOS's Admin Portal docs frame exactly that, per-IdP walkthroughs so customers onboard without high-touch support from the vendor's team, as the cost it removes. SAML is also easy to get wrong in a way that matters: SAMLStorm (March 2025) was a signature-verification bypass in the Node library `xml-crypto` (CVE-2025-29774 and CVE-2025-29775) that let attackers forge SAML responses in apps built on it. WorkOS says it patched its own customers within 24 hours and found no sign of compromise; that part is self-reported.

## Origin: Nylas, then a bet on "boring"

In the 2020 Show HN launch thread, Michael Grinich says he previously founded Nylas, which could not monetize and shut down Nylas Mail. His stated main reason: it could not be sold to enterprises because it lacked enterprise features. He pitched WorkOS there as "Plaid for enterprise IT systems" and said it ran under the hood of other products, the way an OS does. The thread is dated 2020-03-17.

Two details from that thread are worth remembering. He said the product is popular with VPs of Sales, who may not know what SAML or SCIM means but know it is blocking a deal. And he said SSO was free at launch. Today it is not (next section), so treat pricing as something that moves.

Funding, from WorkOS's own posts: Series B, $80M led by Greenoaks, 2022-06-01 (with the Modulz acquisition); Series C, $100M at a $2B valuation led by Meritech and Sapphire, 2026-03-02. I found no revenue figure on the WorkOS pages I read; numbers you may see elsewhere are analyst estimates, not company statements.

## What it sells and what it costs

WorkOS sits between your customer's IdP and the vendor's app. It never replaces the customer's Okta or Entra. The standalone SSO API intentionally does not manage the vendor's user database; AuthKit (lesson 5) is the full-stack option. The site nav lists: User Management, Enterprise SSO, Directory Sync, Admin Portal, Audit Logs, AuthKit, MFA, RBAC, Radar, Vault, Pipes, MCP Auth, and newer items (Airlock, auth.md, Atlas) covered in lesson 6.

Published prices, pay-as-you-go, 2026-10-03:

| Item | Price |
| --- | --- |
| AuthKit | first 1M MAU free; +$2,500/mo per extra 1M |
| SSO and Directory Sync | per connection: 1-15 $125; 16-30 $100; 31-50 $80; 51-100 $65; 101+ contact sales |
| Audit Logs | $125/mo per SIEM stream; $99/mo per 1M events retained |
| Support | Standard free; Scale $1,000/mo; Enterprise custom |
| Annual Credits | custom; adds prepay discount, 99.99% uptime SLA, guided migration |

A connection is the relationship between WorkOS and one customer's identity provider, and the pricing FAQ says it is billed the same whatever the IdP or user count. Staging is free; only production bills. The SSO launch checklist narrows it further: only enterprise connections (the SAML and OIDC ones) in Production are charged, while OAuth connections in Production, such as social sign-in through WorkOS, are free. Admin Portal is included; custom branding and custom domains cost extra ($99/mo for the domain).

> **Read the fine print.** The page does not say whether a tier discount applies to every connection or only to those inside the band. It also lists SSO and Directory Sync as separate tables while its FAQ says each customer "with SSO or Directory Sync" counts as one connection. A customer using both could be one connection or two. Confirm both with sales before you model anything.

## Who buys it, and what is a claim

WorkOS bills the SaaS vendor, not the vendor's customer. Whether the vendor passes the cost on is the vendor's decision, and WorkOS publishes no rule about it.

Claims you will hear, all from WorkOS itself: "3,000+ companies" (customers page), "over 200 paying customers in less than 2 years" (Series B post, 2022), and a Series C list of AI names including OpenAI, Anthropic, Cursor and Perplexity. None of these say which product a logo uses, so "OpenAI uses WorkOS for SCIM" is not something the sources support. Treat the logo wall as marketing and say "WorkOS lists X as a customer".

## Where you fit

The posting (Ashby, published 2026-07-23, US and Canada remote) says an MSP handles tier 1 and you architect what it executes against, owning identity, device management, SaaS lifecycle and the automation layer. It asks for SAML, OAuth and SCIM understood well enough to troubleshoot and architect.

Inference, not stated by WorkOS: every enterprise customer's IT admin is your mirror image. They run Okta or Entra, push groups, rotate certificates, and open tickets when a profile does not map. An internal IT lead who can reproduce what those admins see is useful. WorkOS's IT-team FAQ shows it also answers vendor-security questions (SOC 2 Type II, SOC 3, SIG Lite, GDPR), so internal IT sits on the receiving end of the questionnaires you now send. The posting says the role owns identity on Okta (SSO, MFA, Workflows, SCIM provisioning, lifecycle) and Google Workspace, with Terraform and macOS MDM, so staff SSO is on Okta, not on WorkOS. What it does not say is whether WorkOS tests its own product internally. Ask.

## Your task

Written from the docs, not run against a live tenant. The arithmetic below is local and was run.

```python
bands=[(15,125),(30,100),(50,80),(100,65)]
def marginal(n): return sum(max(0,min(n,hi)-lo)*p for (lo,(hi,p)) in zip([0,15,30,50],bands))
def whole(n): return n*next(p for hi,p in bands if n<=hi)
for n in (10,25,60): print(n, marginal(n), whole(n))
```

```text
10 1250 1250
25 2875 2500
60 5625 3900
```

Run it, double it for a customer base using both products, and write the gap between the two readings for 60 customers ($1,725 per product per month). Then draft three questions for the interview: which reading is true, how connections are counted when a customer has both SSO and SCIM, and whether WorkOS uses its own product internally for anything IT owns.

Next: lesson 2 takes the SSO half apart from the service-provider side.
