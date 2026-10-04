# Admin Portal, Audit Logs, Events and webhooks

You have run the IdP side of this for years: a vendor sends you a metadata URL and a checklist, and you do the clicking. This lesson is the other side. WorkOS gives the vendor a hosted UI so the vendor never sends that checklist, an audit-log pipe so the vendor can answer your SIEM team, and an event feed (Events API or webhooks) so the vendor's database stays in step with your directory. Docs, API reference and the public pricing and status pages were read on 2026-10-03; prices and limits below carry that date.

## The Organization is the unit of everything

An Organization is a top-level WorkOS resource that usually represents one of the vendor's customers. Every connection, directory and audit-log event belongs to one, and there is no cap on how many you create. The vendor must persist `organization.id` (or set `external_id`) at onboarding, because every Admin Portal session, domain, log stream and audit event is scoped to it. Think of it as the tenant record you would create in your own admin console for a SaaS app you sell.

> The Admin Portal guide states that an organization may have only one connection. I found no other page that says this, and the API reference's `ambiguous_connection_selector` error implies several SSO connections per organization are possible (see lesson 2). If a customer mid-migration from Okta to Entra needs two IdPs live at once, confirm with WorkOS before you promise it.

## Domain Verification: who may claim an email domain

An organization domain has `state` of `pending`, `verified` or `failed`, and a strategy of `dns` or `manual`. In the self-serve flow the IT contact enters the domain, WorkOS detects the DNS provider, shows TXT instructions, then polls until it finds the record. If a domain is not verified within thirty days it moves to `failed` and you restart it with the verify endpoint. The events to listen for are `organization_domain.verified` and `organization_domain.verification_failed` (reason `domain_verification_period_expired`).

Unless an organization is set to allow any domain, a verified domain is required to activate SSO. That makes this a security control, not paperwork: the reference says the organization that defines a domain policy controls authentication for that domain across your application, and, in AuthKit, a verified domain lets WorkOS treat matching SSO users as email-verified (that last point is from the AuthKit docs, not the standalone SSO API). Failure modes:

- **Self-attested domains.** Passing `state: 'verified'` when you create or update an organization skips DNS entirely. It is meant for domains you already proved elsewhere. Using it to "unblock a demo" hands that domain's policy to whoever the org is. WorkOS refuses consumer domains such as `gmail.com`.
- **Wrong domain, silent wait.** A typo'd domain sits in `pending` for thirty days, then fails. Nothing pages anybody unless you consume the failure event.
- **The TXT record format.** The API guide describes a record named for the domain with value `verification_token=...`. The object samples also carry a `verification_prefix`. Copy the record from the Admin Portal or the returned object; do not hand-write it from memory.

## Admin Portal: handing setup to the customer's IT admin

The Admin Portal is a WorkOS-hosted UI where an IT contact verifies a domain, configures an SSO or Directory Sync connection from per-IdP walkthroughs, tests sign-in, and later manages the connection. Per the pricing FAQ it is included in all accounts; custom branding and custom domains cost extra (the pricing page lists Custom domain at $99/mo; the docs list email, AuthKit, Admin Portal and the auth API as customisable, and I did not find whether one fee covers all of them). There are two ways in, and they behave very differently:

| | Dashboard setup link | API-generated portal link |
| --- | --- | --- |
| Use | Setup only | Setup and post-configuration |
| Lifetime | 30 days, or until setup completes | 5 minutes |
| Revocable | Yes; one active link at a time | No |
| Created by | "Invite IT contact" in the dashboard | `POST /portal/generate_link` |

The API call takes `organization` and an optional `intent`: `sso`, `dsync`, `audit_logs`, `log_streams`, `domain_verification`, `certificate_renewal` or `bring_your_own_key`. Pass `it_contact_emails` (up to 20 per org) and those people receive alerts such as expiring SAML certificates. That call does not email them or restrict who can open the link, so your app must deliver it, normally by redirecting the signed-in user straight away. Return and success URLs must be HTTPS.

What the admin sees afterwards: connection state, metadata, a "Test sign-in" button, and a sessions list with the request sent to the IdP and the response. Deleting a connection needs a typed `DELETE CONNECTION`.

Failure modes the docs imply: a portal link pasted into a support email is dead in five minutes (send the dashboard link, or generate on click); a stale dashboard link blocks a new one until you revoke it; IT-contact alerts come from a WorkOS-branded address until you configure a custom sender; and the button is "Invite IT contact", "Invite Admin" or "Invite contact" depending on which docs page you read, so trust your own dashboard.

## Audit Logs

Each event has `action`, `occurred_at`, `actor`, `targets` (array) and `context` required (with `location` required inside it and `user_agent` optional), plus optional `version` and `metadata` (50 keys, 40-char keys, 500-char values). Actions must be registered in the dashboard first; a metadata schema can be enforced with JSON Schema. Schemas are immutable: edits make a new version, and emitters must send `version` to opt in.

```bash
curl --request POST --url https://api.workos.com/audit_logs/events \
  --header "Authorization: Bearer sk_test_..." --header "Content-Type: application/json" \
  --header "Idempotency-Key: <uuid-v4>" -d '{"organization_id":"org_...","event":{
    "action":"user.signed_in","occurred_at":"2026-10-03T12:00:00Z","version":1,
    "actor":{"type":"user","id":"user_123"},"targets":[{"type":"team","id":"team_9"}],
    "context":{"location":"203.0.113.7","user_agent":"Chrome/104.0.0.0"}}}'
```

- **Emitting.** Idempotency keys expire after 24 hours; without one WorkOS derives a key from the content. On 2026-10-01 the status page logged about one minute of HTTP 500 and 408 on the Audit Logs API, and WorkOS wrote that events sent in that window by integrations without retry may not have been recorded. Queue and retry; do not emit inline in a request path.
- **Retention.** 30 days by default, per organization; settable to 1-11 months or 1-10 years; raising is allowed, lowering is not.
- **Export.** CSV only, one organization, last three months, the download URL expires after 10 minutes, and `state` can be `pending`, `ready` or `error` (the OpenAPI spec also lists `expired`). A request for eight-month-old events cannot be served by CSV export; the docs point to streaming for longer-term copies.
- **Streaming.** Seven destinations: Datadog, Splunk HEC, S3, Google Cloud Storage, Microsoft Sentinel, Snowflake, generic HTTPS. Customers can configure them in the Admin Portal (`log_streams`). Streams are `Active`, `Inactive`, `Error` (the docs give both "non-retryable error" and "retries are exhausted") or `Invalid` (credentials rejected). Streams never leave Error or Invalid on their own; the documented way back to Active is updating the configuration so validation succeeds, so alert on stream state after any SIEM outage. Once re-activated, delivery resumes from the last delivered event and events from the outage are delivered while still inside retention, so no CSV backfill is needed. WorkOS streams from fixed IPs, so allowlist them. For GCS, `storage.objectCreator` is not enough; retried deliveries overwrite objects, which needs delete permission (the docs name `objectAdmin`).
- **Price (pricing page, 2026-10-03).** $0 base, $125/month per SIEM connection, $99/month per million events stored. Whether the default 30-day retention is metered is not stated.

## Events API and webhooks

Both deliver the same events (`id`, `event`, `data`, `created_at`, optional `context`; for example `connection.activated`, `dsync.user.updated`, `organization_domain.verified`), and the event IDs match. WorkOS recommends the Events API for user and directory sync: you page with an `after` cursor at your own pace, ordering is consistent, you can replay (events up to 90 days old, 30 days per request), and `range_start` bootstraps a migration from webhooks. Webhooks are real time but unordered.

Webhook endpoints must be HTTPS with a hostname that resolves to a public IP; WorkOS rejects private ranges at save time, a classic surprise when DNS points at an internal load balancer. Reply 2xx fast and process off a queue. A non-2xx is retried up to six times with exponential backoff over three days in production; staging retries for minutes. The status page lists six webhook delay or latency incidents between 2026-01-02 and 2026-07-27, so build a reconciliation job that diffs state through the API.

The signature header is `WorkOS-Signature: t=<ms epoch>, v1=<hex>`. The expected value is HMAC-SHA256, keyed with the endpoint secret, over `t`, a literal `.`, then the request body as a UTF-8 string. Also reject stale timestamps; the Node SDK v11 source defaults to 180000 ms and only checks that the timestamp is not too old.

Three traps that are all yours as the receiver:

- **Out of order.** `dsync.group.user_added` can arrive before `dsync.user.created`. Each event carries full objects, so upsert, and skip user or group objects whose `updated_at` is older than what you hold. Do not apply that guard to membership events: lesson 3 covers why membership changes do not move `updated_at`, so apply `user_added` and `user_removed` as they arrive and reconcile through the API.
- **Duplicates.** Record processed event IDs and ignore repeats.
- **Raw bytes.** The docs' Node sample passes `await request.json()` to `constructEvent`, and the SDK handles an object by calling `JSON.stringify` on it. If WorkOS's bytes and that re-serialisation differ, valid events fail.

## Lab: break a signature on purpose

This lab ran locally in the sandbox with Python's `hmac`; nothing here touches WorkOS. The secret is fake. It implements the documented algorithm, then feeds it a body that a framework parsed and re-dumped.

```python
t, v1 = [p.strip() for p in header.split(",")]
ts, got = t.split("=", 1)[1], v1.split("=", 1)[1]
exp = hmac.new(SECRET, f"{ts}.{raw_body.decode()}".encode(), hashlib.sha256).hexdigest()
```

```text
1 raw bytes as received      : OK
2 python re-dump (default)   : REJECT: signature mismatch
3 compact but unescaped é    : REJECT: signature mismatch
5 replay after 10 min        : REJECT: timestamp outside tolerance
6 tampered body              : REJECT: signature mismatch
```

Case 4, a compact re-dump that happens to match the sender's escaping, passed. I do not know how WorkOS serialises, so I cannot say your parsed body will fail, only that it can. Your task: in whichever language your future glue code would use, capture the raw body before any JSON middleware, verify first, parse second, and rerun the cases above.

Next: AuthKit, sessions, RBAC and the move from "tenant roles" to resource-scoped FGA.
