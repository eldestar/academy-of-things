# Running IT with an MSP

Your resume shows you as the tier 2/3 backstop above an existing tier 1. The posting describes something different: "We have an MSP partner handling tier 1 support. Your job is to architect the systems the MSP executes against, automate everything upstream, and serve as the escalation point for complex tier 2/3 issues." Facts checked 2026-10-03 against vendor docs. Anything marked **Opinion** is practitioner judgment, not vendor fact; check it against your own experience and say so in an interview.

## The model: who owns what

- **The MSP** works a queue against runbooks you wrote. It executes; it does not decide.
- **You** own the access model, the automation, the runbooks, the audit trail and the escalation path. If the MSP cannot do something safely from a runbook, that is a defect in your design.
- **The contract vocabulary.** Opinion, from common ITIL usage (glossaries differ, and none was checked for this lesson): an SLA is a commitment to a customer, an OLA is a commitment between internal teams, and an underpinning contract is a commitment from an outside supplier. The OLAs are the ones you write with People Ops (hire and exit dates) and Security (incident handoff). Most teams say "SLA" for all three; ask what is actually committed and measured.

Opinion: a starting split, to argue with rather than copy.

| Work | MSP executes | You own |
| --- | --- | --- |
| Password and MFA reset, unlock | Yes, after the identity check in the runbook | The check, the role scope, the log review |
| Joiner and mover access | Verifies completion | The automation and the access model |
| Leaver access removal | Confirms and collects hardware | Timing, the automation, the checklist |
| App or policy changes | No | Everything |
| Incident, tier 2 and 3 | Escalates with a handoff payload | Resolution and the runbook fix |

Opinion: the failure pattern is a vendor given broad admin so tickets close faster, with no one owning what that access can do at 3am. The role the posting describes is the person who narrows it.

## Scoping what the MSP can touch

Start from what each vendor can actually scope:

- **Okta.** The Help Desk Administrator role can reset passwords, reset MFA, unlock accounts, clear user sessions, set a password to activate Pending users, and view profiles in assigned groups. It cannot create or activate users, suspend or delete users, assign users to apps or groups, or create API tokens, and it can be limited to selected groups. Custom roles plus resource sets cover finer cases: up to 100 roles per org, 10,000 resource sets, 1,000 resources per set. Okta's page says permissions are currently limited to user, group and app activity and profile source imports, so check whether your needed action is scopable before promising it.
- **Google Workspace.** Help Desk Admin resets passwords for non-admin users and views profiles. User Management Admin acts on non-admin users and can be limited to organizational units. Custom admin roles exist for anything between.
- **Jamf Pro.** Privilege sets are Administrator, Auditor (all read privileges), Enrollment Only and Custom. Jamf warns a Custom account may need privileges on several objects for one task, so test each runbook as the MSP account. Docs (version 10.25) also advise keeping one non-LDAP administrator for when the directory link breaks; confirm in current docs.

Traps worth naming in a design review:

- **The help desk role is an account takeover primitive.** Reset MFA plus clear sessions in the wrong hands, or the wrong requester's hands, is a takeover. Verifying who is asking is a runbook step, not a courtesy. Opinion: require manager approval or a step-up check for MFA resets.
- **API tokens inherit their creator.** Okta says an SSWS token carries the privilege of the admin who made it, changes when that admin's role changes, and is deprovisioned when that admin is deactivated. It also expires after 30 days unused and can be restricted to a network range. Okta strongly recommends OAuth 2.0 instead. A token minted by an engineer who then leaves is how an MSP integration dies on a Friday.
- **Shared accounts.** Opinion: named accounts per MSP person, through your IdP and your MFA policy where possible. If MSP staff come from their directory, you inherit their offboarding delay.

## Runbooks, SLAs and escalation

A runbook the MSP can follow has the same parts every time (Opinion): trigger, who may request it, identity check, exact steps in the admin console or script, expected result, how to confirm, what to log, and a stop condition that says escalate.

- **Hard stops.** Write the cases tier 1 never decides: executive or admin accounts, anything involving a departure under dispute, any request that contradicts the runbook, any repeated MFA reset for one user in a short window.
- **Escalation shape.** Name the severity, the channel, the handoff payload (user, app, what was tried, error text, timestamps) and the response time. Escalate on stated triggers, not on feel; an MSP penalized for escalating will stop escalating.
- **Where your time goes.** Each recurring escalation is a runbook gap or an automation candidate. Track them; the posting says "automate everything upstream".

## Offboarding as a controlled workflow

The MSP should verify offboarding, not decide it. Opinion on shape: HR event triggers your automation; the automation clears sessions and tokens, then deactivates in Okta; a checklist covers what automation cannot; the MSP confirms and collects hardware. The docs read for this lesson do not say what Clear User Sessions does on an already-deactivated user, so test that before reversing the order. Facts that make the checklist necessary:

- Okta's Clear User Sessions action has an option to include Logout-enabled apps and API tokens, which invokes Universal Logout; without it, Okta's docs say it revokes OIDC and OAuth refresh and access tokens and clears IdP sessions. Universal Logout is configurable for generic SAML and OIDC apps. Whether an app's own session dies depends on the app, so test it per app before you promise "access removed".
- AWS: ending an AWS access portal session does not affect the console session, whose length comes from the permission set (default 1 hour, up to 12). SCIM only helps if the token has not expired (lesson 4).
- Apps without SCIM keep their own local accounts and need a named owner on the checklist.

Opinion: involuntary exits belong with you or the on-call engineer, not tier 1.

## Auditing the MSP

- **Okta log streaming** targets Amazon EventBridge or Splunk Cloud. Delivery is at least once, can be out of order or duplicated, has no guaranteed latency, and after only two delivery attempts with no wait Okta deactivates the stream. A dead stream is a silent audit gap; alert when events stop. In-org System Log retention is 90 days.
- **Google Workspace** admin log events are retained 6 months, with export to BigQuery for longer retention and queries.
- **Jamf Pro** Change Management records time, administrator, object, action and details. In the 10.25 docs, log-file or syslog output is on-premise only and Jamf Cloud changes "cannot be exported"; confirm for your version, because it decides how you audit MDM changes.
- Opinion: alert on MSP admin actions that bypass the runbook (role changes, API token creation, bulk exports) and review a sample of closed tickets weekly against their logs.

## Measuring the vendor, and what AI ITSM changes

Define terms before you negotiate; vendors define them differently (Opinion):

- **Deflection:** requests resolved with no ticket, over all requests. It needs chat-channel data, not only the ticket system.
- **Reopen rate:** tickets reopened after the MSP closed them, over tickets the MSP closed. Watch the denominator.
- **Escalation rate and quality:** share escalated, and share escalated with a complete handoff payload.

Opinion, a worked example (illustrative numbers) of why the denominator matters. Last quarter the MSP closed 1,000 tickets and 100 were reopened (10 percent). This quarter an agent resolves password and MFA resets in chat before any ticket exists, so the MSP closes 500 tickets, all of them harder, and 40 reopen (8 percent). The rate fell, but the two quarters are not comparable: the easy, rarely reopened requests left the denominator, so a lower rate says little about the MSP's quality. Falling ticket volume is the expected effect of deflection, not evidence of better service and not gaming, since reopen rate is a ratio and closing fewer tickets does not by itself lower it. Compare reopen rate within the same ticket category across quarters, and measure deflection from request-level data (chat plus tickets), not from ticket counts. Do not credit or penalise the MSP on reopen rate alone.

AI ITSM such as Console changes the boundary. Console's own site describes an agent in Slack and Teams that handles onboarding and offboarding, password and MFA resets, FileVault or BitLocker key retrieval and group changes, with deterministic approvals, step-up MFA, custom RBAC and OCSF audit logs. It also claims "75%+" automation; that is a vendor claim, not a benchmark. Opinion: tier 1 stops being "what a human can follow from a runbook" and becomes "what you will let an agent do with a service credential", so the agent's integration account is your highest-privilege non-human identity and deserves the scoping and auditing above. Opinion: ask how the MSP is priced; ticket-based pricing and deflection pull in opposite directions.

## Your task

*Written from the docs, not run against a live tenant, except the jq filter, which ran in the sandbox on a synthetic ten-row sample.* First, for each system you manage, write the MSP role you would grant (Okta, Google, Jamf) and the one action you would refuse to let tier 1 do. Second, build `tickets.json` with rows like `{"handled_by":"msp","ticket":true,"reopened":false,"escalated":false}` (the sample: ten rows, two with `"ticket":false`, six MSP rows of which two are reopened) and run:

```sh
jq -r 'def pct(a;b): "\((a*1000/b|floor)/10)% (\(a)/\(b))"; ([.[]|select(.ticket==false)]|length) as $n | [.[]|select(.handled_by=="msp")] as $m | "deflection: "+pct($n;length), "MSP reopen: "+pct([$m[]|select(.reopened)]|length;$m|length)' tickets.json
```

Real output on the synthetic sample (not real statistics): `deflection: 20% (2/10)` and `MSP reopen: 33.3% (2/6)`.
