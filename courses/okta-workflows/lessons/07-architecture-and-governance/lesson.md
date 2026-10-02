# Architecture and governance

By now you can build and harden a flow. This lesson is for the person who decides what gets built where, how it moves between environments, and who is allowed to change it.

## Which mechanism? A decision guide

| Need | Reach for | Why |
| --- | --- | --- |
| Group membership from attributes; basic lifecycle rules | **Group Rules / Automations** in the Admin Console | Declarative, no execution history to maintain |
| React to an Okta event with several steps, other apps, waiting or retries | **Workflows** with an Okta event card | Okta hosts the receiver; visual logic; history |
| Send events to your own service | **Event Hook** | Asynchronous push to your endpoint |
| Change an in-flight Okta transaction (token claims, registration) | **Inline Hook** | Synchronous, but about 3 seconds |
| Logic needing tests, code review, real version control | **Code** against the Management API | Cards are hard to diff and unit test |
| An assigned admin should trigger a process on demand | **Delegated flow** | Run by assigned admin users from the Admin Console |

Facts to design around, from Okta's event hook documentation:

- Events are delivered **at least once**, with **no ordering guarantee**. Use the published timestamp to order and the event ID to dedupe.
- Delivery has a **3 second** timeout and **at most one retry**; 4xx responses are not retried, 5xx are.
- Each org is limited to **400,000** applicable events in 24 hours; hooks stop triggering when it is reached. Up to **25** active verified event hooks per org.

If a Group Rule could do it, using a flow instead means more to monitor for no gain.

## Environments and moving flows

The documentation this course checked describes **export and import**, not a built-in dev/test/prod promotion pipeline. If your org has one, use it. Otherwise:

- A single flow exports as a `.flow` file; a folder as a `.folder` file (maximum 27 MB).
- Export **strips all connection information and table data**. Tables arrive empty with their schema. Every connection must be re-established in the target org after import.
- References between exported objects are preserved. If a flow depends on a helper you did not export, import makes you choose a replacement. Export parents and helpers together, as a folder.
- Folders nest to **five levels**. Export capacity per 15 minutes is tiered, 10 flows on Starter and trial up to 1,000 at the top tier.

So the practice is: build in a sandbox org, export the folder, import into production, reconnect, test with fake data, switch on. Keep exports in git so you have a diff trail. Okta also documents a flow-backup template built on its export functions; read it before building your own.

Be honest about what you have not verified: this course did not confirm whether Workflows offers environment variables, per-environment connection mapping, or a card-level change history. Check your org, and compensate with naming, a changelog and exports in git until you know.

## Access control

- **Folder Access Control**, when enabled, scopes who can see and edit folders. With it on, a flow's **org-level connections must be added to the destination folder before import**, and flows holding folder-level connections cannot be imported into a different folder.
- **Connections** run as the account that authorised them. Use dedicated service accounts, scoped to what the flows need, and customise OAuth scopes rather than accepting the broadest default if the flows are narrow. Reauthorise after changing scopes.
- Reauthorising needs super admin, Workflows Administrator or Connection Manager.

## A review checklist

Use this before a flow goes live:

1. Could a Group Rule or Automation do this?
2. What triggers it, and what happens if the trigger fires twice or out of order?
3. Is every failure visible: error reporting wired in, helper failures surfaced?
4. What are the limits it approaches: memory, steps, rate, 3-second hooks?
5. Whose account does it act as, with what scopes?
6. Is anything secret typed into a card?
7. Is it exported and in git, and does it have a documented owner?

## Failure modes at platform level

- **Flow sprawl.** Hundreds of unnamed flows, none owned. Name by system and purpose, and keep the folder tree to what people can navigate in five levels.
- **The invisible dependency.** A helper changed for one parent silently changes every parent. Treat shared helpers as shared code: announce changes, and export before editing.
- **Active-flow ceiling.** Hitting the licence cap in production during an incident.
- **Single point of expertise.** If one person understands the flows, you have a bus-factor problem the tool will not fix.

## Where this course stops

This course has not covered Connector Builder, the full catalogue of connectors, or Okta Identity Governance integration. Lesson 8 is a stub for that reason. A short, true course beats a padded one.
