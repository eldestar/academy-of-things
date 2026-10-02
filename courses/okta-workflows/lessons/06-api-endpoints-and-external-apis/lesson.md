# API endpoints and external APIs

Flows are not only started by Okta. They can be started by anything that can make an HTTP request, and they can call any service that has an HTTP API. Both directions have rules that bite.

## Inbound: the API Endpoint card

A flow whose first card is **API Endpoint** exposes a URL. Anything that can call it can start the flow: an inline hook, a script, another system's webhook.

**Security** is set on the card, in the endpoint settings. You pick a security level and choose which applications may call it: any app that holds the right scope, or a selected list. For OAuth 2.0 invocation the scope is `okta.workflows.invoke.manage`, and the app must have it granted in its API scopes. The calling client gets an access token from your org's token endpoint and presents it to the flow's invoke URL. A client-token option also exists; this course has not covered its details, so read Okta's page before choosing it.

> An API endpoint with weak security is an unauthenticated way to start identity automation in your org. Treat the choice of security level as a security decision, review it, and rotate client credentials like any other.

### Time limits

| Case | Limit |
| --- | --- |
| Synchronous flow behind an incoming HTTP connection | 60 seconds |
| Request waiting on an asynchronous action | dropped after 120 seconds |
| Okta inline or event hook calling you | 3 seconds, so effectively your budget |
| Invocations per flow | 10 per second, then HTTP 429 |

### The pattern Okta recommends

Structure API-endpoint flows to be **asynchronous**: the caller should not need to wait for the real work. Concretely:

1. Put the **Close** card for the API connection first, so the HTTP connection is released to the caller immediately.
2. Do the real work afterwards, ideally by handing it to a helper with **Call Flow Async**.
3. When you need a precise response, combine Call Flow Async with **Return Raw**, which gives fine-grained control over the HTTP response.

The trade-off, from lesson 5: using the Close card makes the flow asynchronous, and asynchronous flows leave low-latency mode. Decide per flow: a hook that must answer in three seconds should respond fast and do nothing slow; a webhook receiver that just needs to acknowledge can close early and process afterwards.

Avoid external network calls in a **synchronous** flow. The caller is waiting, and so is its timeout.

## Outbound: calling services without a connector

When no connector covers a service, the **API Connector** cards call its HTTP API: Get, Post, Raw Request and so on. Authentication is configured on a connection and comes in three kinds:

- **Basic**: username and password.
- **OAuth 2.0**: Authorization Code or Client Credentials grant types. For client authentication, sending credentials as a basic auth header is the recommended option; sending them in the body is also available.
- **Custom**: for API keys and similar, such as a header with a name and secret value you define.

Use **Raw Request** when you need full control: XML services, programmatically built headers (other API Connector cards fix header names at design time), unusual response handling.

## Rate limits and retries on outbound calls

- A card's own error handling retries **only on 429** (lesson 4). Treat a 5xx as your problem.
- Under load, the right fix for a rate-limited target is usually fewer concurrent calls (the list card's concurrency), not more retries.
- Okta's own APIs have their own rate limits. Heavy flows against the Okta connector share your org's budget with everything else that uses it. Concurrency is a shared resource; check Okta's rate-limit and concurrency pages before launching a bulk job on a busy org.

## Failure modes

- **Secrets in flows.** An API key typed into a card is visible to anyone who can open the flow. Put credentials in the connection, not in cards or tables, and remember exports strip connections but not literals you typed into cards.
- **The endpoint nobody remembers.** A flow with an API endpoint stays callable as long as it is on. Inventory them.
- **The timeout surprise.** A flow that takes 70 seconds works in a test run and fails for the HTTP caller at 60. Split the work and respond early.
- **Assuming the caller retries.** Okta event and inline hooks retry or fail according to their own rules; your flow may see duplicates. Make handlers idempotent.

## Your task

Design an API-endpoint flow that receives a webhook from a third-party app, acknowledges at once, and creates an Okta user in the background. Write down which card closes the connection, which helper does the work, what happens on failure, and which security level you choose and why.

Next: how to organise, move and govern all of this at scale.
