# Your first flow, tested properly

Most first flows are built, switched on, and only then discovered to be wrong. This lesson builds one in the order that avoids that: connection, event, action, test with fake data, read the history, then switch on.

The example: when a user is added to a group called `contractors`, post a message to a Slack channel. Swap Slack for email or a ticket system; the shape is identical.

## Step 0: the Okta connection, and whose account it is

The Okta connector needs a **connection** to your own org. Three facts about it matter more than the click-path:

1. The account that authorises it must be a **super admin**. Reauthorising later needs super admin, Workflows Administrator, or Connection Manager.
2. Every action the flow performs is attributed to that account. Create a dedicated service account for Workflows and authorise with it. Otherwise your own name is on every deactivation the flow ever does.
3. The connection carries **OAuth scopes**. "Use default scopes" grants what the Okta connector cards need. If you later customise scopes, or Okta adds a card needing a new scope, you must **reauthorise** the connection before it works.

> When a card that worked last month suddenly returns a permissions error, check whether the connection's scopes changed or its authorising account lost a role. Both are invisible from the flow itself.

## Step 1: the event card

In the Workflows Console, create a folder for the project, then **New Flow**. The first card is always an event. Pick **Okta → User Added to Group**.

Event cards expose outputs: details of the user and the group, which are what you map from. Check the card's output list in your own console for the exact field names. Plan on filtering *which* group inside the flow rather than relying on the event card to do it; if your card does offer a filter, use it and treat the branch below as a second check.

## Step 2: filter early, then act

Add a **Branching → Continue If** card and map the group name output into it, comparing against `contractors`. If the comparison is false, the flow stops there, cleanly. Filtering before any action is a habit worth forming now: it keeps unneeded executions short and the history readable.

Then add a chat action such as Slack's send-message card (card names vary by connector and release; use whatever your connector calls it). Map the user's login and the group name into the message text with a **Compose** card, which lets you mix literal text and mapped fields.

Save. The flow is still **off**, which is what you want.

## Step 3: test with fake data, not a real user

Click **Run** at the top of the flow. The event card turns into a form: type a fake login, name and group name into its output fields and run. This executes the flow once with that data without waiting for a real event.

Test both branches: once with `contractors`, once with another group. A flow that is only tested on the happy path has only been half tested.

## Step 4: read Execution History

Open **Execution History** for the flow. Each run shows every card with its inputs and outputs. A green tick with a duration means the card ran; a card with an error badge shows the message. Click into a card to see the exact values that passed through.

Three things to look for on your first flows:

- The Continue If card shows **false** on the non-matching run and the flow stopped there. If it did not, your comparison is wrong (case, whitespace, group name vs group ID).
- The Compose card output reads as a human sentence, not `undefined` or an object dump. If a field is empty, the mapping points at the wrong output.
- The action card's output contains whatever the app returned. For Slack that is the posted message; for Okta actions it is usually the updated object.

History is kept for **30 days**. Searching it matches any text that passed through any card, including error text, so it doubles as an audit trail for a month.

## Step 5: switch it on, then trigger a real event

Toggle the flow **on**. Now add a test user to the real `contractors` group and watch a new execution appear. Event delivery is asynchronous, so allow seconds rather than milliseconds. Expect the flow to be triggered by group-adds beyond this one group, which is why the early filter matters.

If nothing arrives: the flow is off, the connection is unauthorised, or the event card was saved after the connection changed. Those three cover almost every "my flow doesn't fire" ticket.

## Your task

Build the flow above against a test org or a sandbox folder. Deliberately break it once by mapping the group *ID* into the Continue If instead of the name, run with test data, and find the failure in Execution History before fixing it. Being able to read history is the skill; the flow is just the excuse.

Next: when one flow needs to do the same thing for fifty users, you need helper flows and lists.
