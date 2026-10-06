# Authorization and the identity lifecycle

Earlier lessons covered getting a person signed in. This lesson covers what happens next: what that person is allowed to do, and how their access stays correct from the day they join until the day they leave. Most identity audit findings come from here. Facts checked 2026-10-06 against the docs named in the text.

Our running example: **Sam** is a new hire at Example Co. who needs the customer app (the CRM) to do the job.

## What authorization is, and four ways to decide

**Authentication** asks "who are you?". **Authorization** asks "what are you allowed to do?". An **entitlement** is one specific thing a person may do, such as "read customer records" or "administer the CRM". Systems decide authorization in four common ways:

- **ACL (access control list):** each thing carries a list of names allowed in. Easy to understand, but names are rarely removed, so people pile up access over time. NIST SP 800-162 says failing to remove access over time "leads to users accumulating privileges".
- **RBAC (role-based access control):** Sam gets a role such as "Support agent", and the role carries the entitlements. Good when jobs are stable. If every odd case needs its own special role you get **role explosion**: hundreds of roles with a handful of people each.
- **ABAC (attribute-based access control):** a rule looks at facts, called **attributes**, such as department, device or location. NIST SP 800-162 defines it as deciding from attributes of the person, attributes of the thing, conditions like location, and a set of policies. It handles rules like "Sales staff on a managed laptop". The weakness is **attribute drift**: if the department field in the HR system is wrong or late, the rule gives the wrong access. (That name is informal, not a NIST term.)
- **ReBAC (relationship-based access control):** access follows relationships, such as "Sam is a member of the team that owns this folder". Good for sharing and folders inside folders. The weakness is that relationships multiply quietly, like ACL names (our own inference, not a NIST or vendor claim).

NIST says RBAC does not easily handle decisions that depend on things like location or recent training, which is where ABAC fits better.

## Groups: the lever IT pulls

A **group** is a named set of people. Instead of giving Sam access to ten apps one by one, you add Sam to a group and assign the group to the apps. Okta describes this as assigning users to a group and then granting or denying access to the group. A **group rule** adds people automatically from an attribute. Okta's example: a user whose department is "sales" is added to the Sales group, and when the department changes they are removed from it automatically. Okta says that gives you attribute-based access control.

Groups go wrong in two ways:

- **The name says less than the grant.** A group called `Finance-Readers` that is assigned the administrator role in an app gives every member administrator rights. A name is only a label. To know what a group allows, look at what it is assigned to and with which role in that app.
- **Rules are only as good as the data.** If HR enters the wrong department, a group rule faithfully gives the wrong access.

## The snapshot problem

When Sam signs in through single sign-on, the identity provider hands the app a signed note (a token or an assertion) that can include Sam's groups. The app trusts that note, and often keeps its own session built from it, until the note expires or that session ends. Microsoft states that group information in a token is current only when you receive the token.

So if Sam is removed from a group at 10:00, an app using a note issued at 09:30 can keep treating Sam as a member until the note expires, the app's session ends, or a new note is issued. We call this the **snapshot problem** and the out-of-date group list a **stale claim**; both are our informal names, not standard terms. When access must end sooner, apps can check live, or an admin can revoke the user's sessions.

## Joiner, mover, leaver

Microsoft's identity lifecycle page says many organizations model the **identity lifecycle** as three phases. A **joiner** enters the scope of needing access (Sam is hired). A **mover** moves between parts of the organization (Sam goes from Sales to Support). A **leaver** leaves the scope of needing access. Microsoft's example is a joiner process automated from a system of record such as the HR system, so an HR change, not an email to IT, can start each phase.

- **Joiner:** Sam receives **birthright access**, the baseline everyone in that job gets from day one. CIS Safeguard 6.1 asks for a documented, preferably automated process for granting access on new hire or role change.
- **Mover:** the risk is **privilege accumulation**. Sam gets Support access but keeps the Sales access, then the next move adds more. NIST SP 800-53 (PS-5) says that when someone is reassigned you must review and confirm that the old access is still needed.
- **Leaver:** CIS Safeguard 6.2 asks for revoking access "through disabling accounts immediately upon termination, rights revocation, or role change".

**Disabling the main account is not the whole job.** In Okta, deactivating a user removes their app access and stops their Okta sessions, but the user is deprovisioned from an app only if deprovisioning is enabled for that app. Okta's API reference calls deactivation destructive (apps that are deprovisioned might lose data such as email or files, and it cannot be recovered), while suspension stops sessions and keeps app assignments, so it is the temporary hold. Apps also keep their own sessions (OpenID Connect has a back-channel logout message just to tell an app to end one). Check each of these when someone leaves:

1. Accounts, including app accounts nothing syncs automatically.
2. Sessions and tokens that are still alive.
3. API keys the person created.
4. Shared passwords they knew, which need changing.
5. Delegated access, such as mailbox delegates and forwarding rules.
6. Devices, which must come back.

## Least privilege, reviews and non-human accounts

**Least privilege** means giving only the access needed for the job (NIST SP 800-53, AC-6). **Just-in-time access** applies it over time: a person holds a powerful role only while they need it. In Microsoft Entra PIM a role is "eligible" until activated and then expires.

An **access review** (or certification) is a regular check where an owner confirms who has what and removes what is no longer needed. SOC 2 expects access to be reviewed periodically (our source is secondary summaries; the AICPA text is not freely available). **Rubber-stamping** means approving the whole list without looking at what each line allows; the paperwork exists but the check did not happen.

Not every account is a person. A **service account** is an account for a program, such as a backup job. It needs a named owner. CIS Safeguard 5.5 says to keep an inventory of service accounts with the department owner, review date and purpose. A service account with no active owner is **orphaned**. CIS Safeguard 5.3 says to delete or disable any dormant accounts after 45 days of inactivity, where supported. An **API key** is a long-lived password for a program, so when its creator leaves, someone must still own it. Okta notes that an API token is deprovisioned if the user who created it is deactivated, which breaks any job relying on it.

## Your task: spot the problems

Here is a pretend access list. Today is 2026-10-01 and the company rule is that only IT staff may hold admin entitlements.

| Account | Owner | Owner employed? | Department | Entitlement | Last sign-in |
| --- | --- | --- | --- | --- | --- |
| ana.ruiz | ana.ruiz | yes | Sales | CRM user | 2026-09-30 |
| ben.okafor | ben.okafor | yes | Support | CRM admin | 2026-09-29 |
| dee.shah | dee.shah | yes | Support | CRM user | 2026-06-02 |
| svc-backup | none | not applicable | IT | storage write | 2026-09-30 |

Find the three problems and name each: **excess privilege**, **dormant account** and **orphaned service account**. The answers: ben.okafor, dee.shah and svc-backup, in that order. Next: lesson 8 pulls the whole course into a decision guide.
