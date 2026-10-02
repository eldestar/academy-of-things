# Helper flows and lists

Workflows has no loop card in the programming sense. To do something for every item in a list, you hand each item to a **helper flow**. That one design decision explains most of the shape of a real Workflows project, and most of its performance problems.

## Two ways to call a helper flow

| Card | Waits for the helper? | Can return values? | Use it when |
| --- | --- | --- | --- |
| **Call Flow** | Yes. Your flow resumes when the helper finishes | Yes | You need the answer before continuing |
| **Call Flow Async** | No. Starts the helper and moves on | No | You are fanning out work, or want the parent free |

You can place several Call Flow Async cards in one flow to start different branches of work in parallel. Because the parent never hears back, an async helper that fails does not fail the parent. You find out only by looking in the helper's own Execution History, or by building error reporting into it (lesson 4).

A helper flow declares its inputs and outputs with Flow Control cards at its start and end. When you pick it in the Choose Flow dialog, its inputs appear on the calling card automatically.

## Lists: For Each, Map, and friends

The List function cards each call a helper flow once per item:

- **For Each** runs the helper for every item and returns **no output**. Use it for side effects: deactivate each user, post each message.
- **Map** runs the helper per item and builds a new list. The output list always has **the same number of items** as the input. Use it to transform.
- Filter, Find, Reduce, Sort and Unique also take helper flows to decide or combine.

Two rules that save hours:

1. **Pass only what the helper needs.** In For Each, the *With the following values* section lets you pull individual fields out of the item. Pass the user's ID, not the whole user object. Whole objects inflate memory and make the helper's history unreadable.
2. **Filter before you loop.** A Filter card ahead of For Each is cheaper than a helper that starts, checks, and returns early.

## Streaming: the answer to "my list is huge"

Cards that list large result sets, such as the Okta connector's *Find Users*, *List Users with Search* and *List Users Assigned to Applications*, offer **Stream Matching Records in the Result Set**. With it on, the parent pages through results and starts a helper flow per record asynchronously, holding very little in memory. Without it, the card loads the whole list into the flow's memory first.

Streaming has a **concurrency** field: how many items to process in parallel.

- `1` when order matters or the downstream system cannot cope with parallel writes.
- A higher number such as 5 or 10 finishes sooner when items are independent.

The flow's memory ceiling is **100 MB**, and a flow may execute at most **2 million steps**. A non-streamed list of tens of thousands of full user objects is how you meet the first limit.

> Streamed flows are also a different kind of flow. The platform's low-latency mode excludes flows that use streaming or asynchronous features (see lesson 5). Do not mix a streaming list job with an API-endpoint or hook-driven flow; split them.

## The platform throttles by resource

Workflows tracks four resources per org: CPU time, table requests, memory, and **how many helper flows you invoke**. Heavy use can cause latency spikes for your own flows. A For Each over a large list calls a helper once per item, so it is the usual suspect. The documented recursion limit for helper flows is **250**; a helper that calls itself needs a stop condition you have actually tested.

## Failure modes worth knowing

- **Errors inside the helper show in the helper's history**, not the parent's. When a For Each fails, open the helper flow's Execution History and read the failing run. The parent only tells you that something below it went wrong.
- **Type conversion on lists.** A list of text does not auto-convert to a list of numbers the way a single value does. Heterogeneous lists, mixing types, are especially fragile. Use Map to convert, or convert inside the helper per item.
- **"Ignore errors" variants exist.** There is a *For Each - Ignore Errors* card. Read its card documentation before using it: skipping failures silently is a choice about your data, not a free convenience. This course has not verified its exact semantics.

## Your task

Design, on paper, a flow that deactivates every user in a group. Decide: streamed or not, what concurrency, what the helper receives, and where a failure for one user is reported. Then compare with lesson 4's answer.

Next: making failures visible instead of silent.
