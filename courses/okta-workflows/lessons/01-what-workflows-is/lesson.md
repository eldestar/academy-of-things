# What Workflows is for

You run an Okta org. You have Group Rules, lifecycle policies and maybe an event hook or two, and someone has just asked you to "automate it in Workflows". This lesson is the map: what Workflows is, what it is not, and the vocabulary you need before you drag a single card.

Facts in this course were checked against help.okta.com on 2026-10-01. Limits and tier numbers change; re-check them before you quote them in a design review.

## The one-sentence version

Okta Workflows is a no-code, visual automation platform built into Okta. A **flow** is a left-to-right sequence of **cards**. The first card is an **event** (the trigger). Everything after it is an **action** (do something in an app) or a **function** (reshape data, branch, loop, handle errors). Data moves between cards by **mapping**: you drag an output field from one card onto an input field of a later card.

That is the whole mental model. Everything else is detail.

## The three kinds of card

| Card | What it does | Example |
| --- | --- | --- |
| Event | Starts the flow | Okta connector: *User Added to Group*; a schedule; an API endpoint; a delegated-flow button in the Admin Console |
| Action | Sends a command to an app through a **connector** | Okta: *Deactivate User*; a chat or ticketing connector's *send message* or *create ticket* card |
| Function | Manipulates data or control flow inside the engine | *Compose*, a branching card such as *Continue If*, *For Each*, *If Error* |

Actions are shipped by Okta per connector. If no connector exists for a service, the **API Connector** function cards (Get, Post, Raw Request and friends) let you call its HTTP API directly. That is covered in lesson 6.

## Flows come in two shapes

- A **parent flow** starts on its own: from an event, a schedule, an API call, or a delegated-flow button.
- A **helper flow** only runs when another flow calls it. Helper flows are how you reuse logic, process lists item by item, and centralise error handling. They used to be called child flows; old blog posts still say that.

A helper flow is inactive until something calls it. A parent flow has an explicit on/off toggle, and an *off* flow silently ignores its trigger. The number of flows you may have switched on is tiered by licence, from 5 on Starter and trial orgs up to unlimited on the top tier, so "just turn it on" is not always free.

## Where things live

- **Workflows Console**: a separate UI, opened from the Admin Console. Flows, tables and connections live here, not in the main admin UI.
- **Folders**: flows and tables are organised in folders up to five levels deep. Folder Access Control, where enabled, decides who can see and edit which folder.
- **Connections**: an authorised link to an app. The Okta connector needs its own connection to your own org, authorised by a super admin, and that connection is what the flow acts as. Lesson 2 covers why that should be a dedicated service account.
- **Tables**: simple persistent storage inside Workflows, for state that has to survive between executions. Lesson 5 covers limits.
- **Execution History**: a per-flow log of every run for the last 30 days, with the inputs and outputs of every card. This is where you will spend most of your debugging life.

## What Workflows is not

Workflows sits next to several other Okta mechanisms, and picking the wrong one is the most common architectural mistake. Short version now, full decision guide in lesson 7:

- **Group Rules** and lifecycle **Automations** in the Admin Console are declarative: a condition and a fixed action. If a Group Rule can do it, use the Group Rule. It is cheaper, faster and has no execution history to babysit.
- **Event Hooks** push an Okta event to *your* HTTP endpoint, asynchronously. Workflows event cards for the Okta connector are triggered by Okta events too, but Okta hosts the receiver for you, so you need no endpoint of your own.
- **Inline Hooks** are synchronous: Okta pauses a transaction (token minting, registration, password import) and waits up to three seconds for your answer. Workflows can serve an inline hook via an API Endpoint flow, but the three-second budget is unforgiving.
- **Custom code** against the Okta Management API is still the right answer when you need real version control, unit tests, or logic that is painful to express as cards.

> Rule of thumb: Workflows is for glue between systems and for multi-step identity processes with branching, waiting and retries. It is not a replacement for Group Rules, and it is not a general-purpose programming language.

## Vocabulary check

Before lesson 2, you should be able to say what each of these is without looking back: card, event, action, function, connector, connection, mapping, parent flow, helper flow, table, Execution History. The quiz below checks the ones people get wrong.

Next: build a flow, test it with fake data, watch it in Execution History, and only then switch it on.
