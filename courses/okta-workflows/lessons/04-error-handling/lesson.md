# Error handling that survives 2am

A flow with no error handling does one thing when something fails: it stops, with the failure recorded in Execution History where nobody is looking. This lesson covers the three tools Workflows gives you, and the traps in each.

## Layer 1: per-card error handling

Open any action card's settings and you can say what happens when *that card* errors. The options for "then" are:

1. **Halt Flow**: stop the flow with an error.
2. **Return Values**: stop with an error, but send a custom message, built from fields you choose, to the calling flow.
3. **Run another Flow**: stop with an error, but first run a helper flow. The helper receives the error details on its **Error** output field.

Option 3 is the foundation of a central "report this failure" helper, described below.

### Retries only cover one error

The same settings have a retry count (default **0**) and a wait between retries (default **5 minutes**). Here is the trap: **only HTTP 429 Too Many Requests triggers an automatic retry.** The documentation lists 400, 401, 402, 403, 404, 405, 409, 413, 421, 422, 500, 503 and 504 as errors that do *not* retry.

So a 504 Gateway Timeout from a flaky downstream API will not be retried by setting "retry 3 times". If you need to retry on 504, build it yourself with If Error.

## Layer 2: the If Error card

If Error is Workflows' try/catch. It is a container with a **Try** section, an **If Error** section, and optional **Outputs**.

- Put the risky cards in Try. If any fails, the flow jumps to the If Error section and carries on instead of halting.
- In the If Error section an **error object** is available with these fields: `message`, `code`, `method` (the ID of the step that failed), `flo` (the flow ID) and `execution` (the execution ID).
- `flo` and `execution` are what make a Slack alert useful: they identify exactly which run to open.

### Four gotchas

- **Nest at most three deep.** Okta recommends no more than three nested If Error blocks, to avoid parsing errors. If you need more, split into helper flows.
- **You cannot map outputs from inside Try or If Error to cards after the container.** A step inside might not have run. Use the container's own **Outputs** fields and set them in both sections.
- **Return and Continue If behave differently inside.** Inside Try or If Error, a Return card returns to the parent *container*, not out of the whole flow. A guard clause that worked at top level may no longer stop what you think it stops.
- **An If Error that does nothing hides the failure.** If the error section is empty, the flow continues as if everything succeeded. Always report or record.

## Layer 3: a central error flow

Build one helper flow, in a shared folder, that takes an error message, a flow ID and an execution ID, and posts them to wherever your team looks, a chat channel or a ticket queue. Then point every important card's *Run another Flow* option, or every If Error section, at it. Failures now announce themselves, with the IDs to find the run in seconds.

A support article from Okta describes an error-notification flow of this kind; treat it as a pattern to adapt, and test it by deliberately forcing a failure.

## Putting it together: the lesson 3 task

For the "deactivate every user in a group" job: stream the list, give the helper a single user ID, wrap the deactivate card in If Error, and in the error section call the central reporter with the user ID and the error object. The loop survives one bad user and you hear about each. Note that this decides that partial success is acceptable. If it is not, halt instead.

## Failure modes in the error handlers themselves

- **The reporter fails.** If the Slack token behind your error flow has expired, you now have an error in the error path. Test it periodically, and consider a second channel for the reporter's own failure.
- **Retry storms.** Retrying a 429 five times with a 5-minute wait, inside a loop of thousands of items, queues thousands of waiting executions. Retry settings sit on the card, so they apply to every item the loop sends through it.
- **Swallowed 4xx.** A 404 caught by If Error and ignored usually means a wrong ID, not "user not found, fine".

> Where to look when a flow is silent: Execution History, filtered by status. The error message appears on the card that failed, and search matches error text across everything that passed through the flow.

Next: the limits that decide what a flow can do at all.
