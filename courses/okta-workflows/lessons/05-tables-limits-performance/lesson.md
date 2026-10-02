# Tables, limits and performance

Every platform has numbers that quietly decide what you can build. This lesson lists Workflows' documented limits as of 2026-10-01, shows what each one does to a design, and covers the mode that makes some flows much faster and the habits that knock a flow out of it.

> Numbers below come from help.okta.com's system-limits page. Several vary by licence tier and Okta changes them. In a design document, link the page rather than copying the figure.

## Limits that shape designs

| Limit | Documented value | What it means in practice |
| --- | --- | --- |
| Memory per flow instance | 100 MB | Large lists held in memory break flows; stream instead |
| Steps per flow | 2 million | Loops over huge lists add up; split into helpers |
| Maximum pause | 30 days | A flow waiting longer than this cannot be built with a single pause |
| Execution history | 30 days | Your only audit trail inside Workflows; export what you must keep |
| Helper flow recursion | 250 | A self-calling helper needs a real stop condition |
| Payload size | 1 MB | Do not push big documents through cards |
| Flow API invocation rate | 10 per second per flow | Above that, callers get HTTP 429 |
| Active flows | 5 on Starter and trial, 50 Light, 150 Medium, unlimited at the top tier | A pilot can hit this long before it hits anything technical |

## Tables: what they are and what they are not

A Workflows **table** is a small persistent store inside the Workflows platform, queried with table cards. Use one for state that must survive between executions: "have I already processed this user?", a lookup of old ID to new ID, a queue of items waiting for a follow-up.

Documented limits:

- **500,000 rows** and **64 columns** per table.
- **16 KB** per cell, which is about 16,000 characters.
- Tables per org: the limits page lists **100** for free-tier orgs and **200** for paid. A separate documentation page cites 100 per folder on import, so treat the exact boundary as something to confirm in your org before designing around it.

Tables are **not** a database for business data. They have no joins, no migrations and no export beyond what Workflows offers, and **exporting a flow or folder strips table data** (lesson 7). Keep tables to flow state and small lookups.

## The throttle you cannot see

Okta throttles Workflows per resource: CPU time, table requests, memory held, and helper flows invoked. Excess usage "can result in latency spikes". The cheap mistakes are the usual ones:

- Reading the same table row in every iteration of a loop. Read it once, pass the value in.
- Passing entire objects into helpers. Pass fields.
- Calling a helper per item when a single filter would drop 95% of the items first.

## Low-latency mode

Flows that start from an **API Endpoint card** (inline hooks), from **Okta connector event cards** (first-party event hooks), from a **third-party webhook** through a connector card, or from a **delegated flow** event card, may run in a low-latency environment with less resource contention. It exists to help latency-sensitive flows, such as inline hooks, stay within their three-second budget.

A flow **drops out** of that mode if it:

- exceeds resource limits or triggers a 429,
- uses **Wait For, Wait Until or Pause**,
- runs longer than **60 seconds**,
- uses streaming actions or other asynchronous features, including the **HTTP Close** card,
- or includes function cards the docs mark as large-data, helper-flow, looping or table-heavy.

Tables are called out specifically: the tables feature runs separately from the core runtime, so a table read in a latency-sensitive flow can cost more than you expect.

## Failure modes

- **The inline hook that "usually" works.** It meets three seconds in testing, then a table read or a helper call pushes it out of low-latency mode and the hook times out in production. Keep latency-critical flows to cards on the core path, and test under load.
- **The unbounded table.** A table that logs every execution grows until it hits 500,000 rows. Decide on retention when you create it.
- **The quiet 30-day edge.** Nobody notices Execution History is rolling until an incident needs day 31.

## Your task

Pick a flow you own. Write down its trigger, its longest wait, the biggest list it handles, and every table it touches. Check each against the limits above and against the low-latency exclusions. Anything near a limit becomes a design change, not a note.

Next: calling flows from outside and calling other systems from inside.
