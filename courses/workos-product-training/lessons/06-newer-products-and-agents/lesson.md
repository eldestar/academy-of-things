# Radar, Vault, Pipes, agent auth and the newer products

The first five lessons covered what WorkOS was built for. Since late 2025 the changelog has become a long list of adjacent products, many aimed at AI agents. This lesson is a map, not a tutorial. For each product it records what it is, what status the docs give it, what the public pricing page says about price, and, in my own judgement, when an IT engineer would meet it. Everything below was read on 2026-10-03: docs, the pricing page, the changelog, and GitHub release pages.

## Reading status at WorkOS

Docs here rarely say "GA". What they do say, where they say anything, is one of: "beta", "early access", "preview", or "must be enabled for your environment, contact your account team". The absence of a label is not a promise of general availability, and an enablement note means you cannot try it on a self-serve account. The pricing page lists prices only for AuthKit, SSO, Directory Sync, Audit Logs, Radar and Custom Domain. Every other product below has no published price, so "not published" means ask sales, not "free". The public status page tracks seven components: SSO, Directory Sync, Audit Logs, AuthKit, FGA, Dashboard and Admin Portal. None of the products in this lesson has its own component, so an outage in one of them will not show up as one.

## Shipped building blocks

Each entry gives what it is, then status and price, then my read on when you would meet it.

- **Radar.** Bot and abuse protection on AuthKit sign-in using device fingerprinting; it can block or challenge.
  - Status: hosted AuthKit, no label. Radar in the User Management APIs and Standalone Radar are described as in preview. Price: first 1,000 checks free, then $100/month per 50K checks.
  - IT angle: credential stuffing and fake signups against the vendor's login; watch the `authentication.radar_risk_detected` event.
- **Vault.** Encrypted key-value store and key management per organization, user or context, with BYOK (AWS KMS, Google Cloud KMS, Azure Key Vault).
  - Status: no label; keys fail over across regions since February 2026. Price: not published.
  - IT angle: customer questionnaires ask who holds the keys, and the Admin Portal has a `bring_your_own_key` intent.
- **Pipes.** Users connect third-party accounts (GitHub, Slack, Google, Salesforce and more) while WorkOS handles OAuth, refresh and credential storage. Changelog launch date: 2025-12-12.
  - Status: no label. Price: not published.
  - IT angle: replaces per-app OAuth token sprawl, but you must review where those tokens now live.
- **Widgets.** React components (user management, organization switcher, API keys, Pipes) plus a session-aware GraphQL Widgets API (2026-07-03).
  - Status: no label. Price: not published.
  - IT angle: embedding self-serve admin screens so customers stop filing tickets.
- **Feature Flags.** Flags read from the access token, targeting organizations or users.
  - Status: no label. Price: not published.
  - IT angle: staged rollout of a new SSO or SCIM option to one customer.
- **API Keys.** Organization-scoped and user-scoped keys managed through a widget and validated by API; user scope added 2026-05-19.
  - Status: no label. Price: not published.
  - IT angle: machine credentials for customers' integrations, and their revocation.
- **Groups.** Native groups inside an organization; roles and FGA roles can be assigned to a group; API dated 2026-04-22.
  - Status: no label. Price: not published.
  - IT angle: distinct from directory groups, which arrive from the IdP through SCIM; do not conflate them.
- **Waitlist.** Replaces sign-up with a request form that you approve or deny; API dated 2026-08-28.
  - Status: no label. Price: not published.
  - IT angle: gated launches. Approval sends an invitation that outlives deleting the entry.

> **Node SDK v11.0.0 (2026-09-28) carries a breaking change for Pipes.** The release notes mark "Support organization-owned and multiple connections" as breaking. The pull request says it is an SDK type change, not an HTTP wire change: `DataIntegration.credentials` can now be `null` for non-OAuth integrations, credential responses are discriminated unions, and exhaustive switches may fail to compile. Pin the version and read the PR before upgrading anything that touches Pipes.

## Agents and MCP

- **Agent Auth.** Blueprints define a permission ceiling and token lifetimes. Short-lived scoped tokens are minted as delegated (user) or autonomous (organization) agent instances. First-party agents only.
  - Status: the 2026-09-02 changelog says early access; the docs say it must be enabled for your environment. Price: not published.
  - IT angle: agent identities you can revoke instantly instead of shared API keys.
- **auth.md and Agent Registration.** An `auth.md` file an app hosts tells agents how to register on a user's behalf. AuthKit supports `anonymous`, `service_auth` and `refresh` identity types with a claim ceremony.
  - Status: docs say it must be enabled; the workos.com/auth-md page offers early access. Price: not published.
  - IT angle: the user-binding step is where an IT team asks who approved which agent.
- **AuthKit as OAuth server for MCP.** AuthKit, through WorkOS Connect, is the authorization server for the vendor's own MCP server, with Client ID Metadata Documents (changelog 2025-11-30; off by default, a dashboard toggle under Connect, with DCR kept for older clients) and resource indicators (2026-05-13).
  - Status: core, no label. Enterprise-Managed Authorization (2026-09-04) is access on request, and Cross App Access is early access. Price: not published.
  - IT angle: EMA lets an IdP pre-approve MCP servers, so you would configure the IdP side.
- **API Gateway.** Managed reverse proxy that authenticates by API key or AuthKit session and forwards a signed assertion header.
  - Status: documented as beta. Price: not published.
  - IT angle: the origin trusts a JWT of roughly 60 seconds, RS256-signed, instead of re-authenticating.
- **Airlock.** Intent-based access control: policy and runtime checks on agent calls, with approvals routed to an IT admin in the vendor's demo.
  - Status: early access. Price: not published.
  - IT angle: the closest product to your day job, covering policy, Slack approvals and an audit trail for agent actions.
- **Relay.** Forward proxy that attaches a user's provider credential server-side so an agent never holds it.
  - Status: early access. Price: not published.
  - IT angle: token exposure in agent runtimes.

WorkOS also runs a management MCP server (`https://mcp.workos.com/mcp`, 2026-07-01) that acts as you with your dashboard role. That is a delegated credential on a hosted service: treat its OAuth consent like any other privileged integration.

## Emulate and testing in CI

WorkOS Emulate is an in-memory local emulator of the WorkOS API for tests: authorization and code exchange, sessions, organization selection, signed webhooks, and injected failures. The docs call it open source and warn it performs no real authentication and must never see production secrets. The GitHub repository's latest release is v0.14.0 (2026-09-24), which is pre-1.0. The repository ships a `LICENSE.txt` that reads MIT (GitHub's detector reports "other"). The docs also point to a supported-features matrix, so check it before relying on an endpoint.

This one matters for the role as written: it is how you would test the webhook receiver from lesson 4 without a tenant.

## Your task

Pick the three products above you would put on a 12-month evaluation list for an internal tool that issues credentials to AI agents against company systems. For each, write one sentence on the status gate you would need cleared first (enablement, early access, beta), and one on what you would ask WorkOS about price. Written from the docs; nothing here was run against a live tenant.

Next: how WorkOS compares with the alternatives, and what its own incident record says.
