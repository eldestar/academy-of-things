# Authorization and the identity lifecycle

You can already get a user signed in. This lesson is about what comes after: what that user may do, where the decision is made, and how their access stays correct from joining to leaving. Most identity audit findings live here, not in the protocols. Facts checked 2026-10-06 against the cited docs; where a source is secondary, the text says so.

## Four models, and how each one fails

| Model | Decides on | Fits when | Typical failure |
| --- | --- | --- | --- |
| ACL | identity listed on the object | few objects, per-object sharing | access is never removed, so people accumulate it |
| RBAC | role assigned to the user | stable job functions | role explosion |
| ABAC | attributes of user, object and environment, plus policies | context matters (department, device, location) | attribute drift (our term) |
| ReBAC | relationship between user and object | sharing, hierarchies, many tenants | relationship sprawl (our term) |

NIST SP 800-162 defines ABAC as granting or denying requests "based on assigned attributes of the subject, assigned attributes of the object, environment conditions, and a set of policies" written in those terms. It says ACLs and RBAC are "in some ways special cases" of ABAC: an ACL works on the attribute "identity", RBAC on the attribute "role". It also says RBAC does not easily support multi-factor decisions (for example location, or recent training), and forcing it to creates many ad hoc roles with few members: "role explosion". On ACLs it notes that failure to remove access over time "leads to users accumulating privileges".

The NIST RBAC model (INCITS 359) assigns users to roles and permissions to roles, many-to-many. Its separation-of-duty constraints come in two kinds: static separation of duty limits which roles one user may be assigned, dynamic limits which roles may be active together in a session.

**Attribute drift** is our informal name for an attribute that is stale or wrong at decision time. SP 800-162 says different authorities own different attributes (HR for name, Security for clearance). Okta says group rules that fill groups from attributes give you ABAC, and that when a user's department changes they leave the Sales group automatically. So a wrong HR department silently grants or removes access.

**ReBAC** stores relationships. In the Zanzibar paper a tuple reads `doc:readme#viewer@group:eng#member`: members of group `eng` are viewers of `doc:readme`. OpenFGA, a Zanzibar-style engine, stores a user, a relation and an object, and a check returns `allowed: true` or `false`. Its docs say RBAC with per-tenant roles multiplies roles, while ReBAC needs one tuple per share. **Relationship sprawl** (our term, and our inference) is the cost: ReBAC descends from ACLs, so unreviewed tuples pile up the same way.

## Groups: the IT lever, and what they hide

Okta lets you assign a group to an app instead of assigning users one by one; when the app supports it, Okta creates the group members in the target app. A group rule fills a group from attributes; our inference is that it governs only the groups it targets, so direct assignments, app-local roles and API keys are outside it. Okta limits an org to 2000 rules, and its help page says rules "can't be used to assign users to admin groups" without defining the phrase. Our reading: that limits what a rule may fill, not which role an app assignment carries, so a group can still hold an admin role inside an app.

- **Name versus grant.** A group called `Finance-Readers` that is assigned the admin role inside an app grants more than its name says. Audit what a group is assigned to, with which app role, not its label.
- **Reuse.** Entra's access-review docs list "when a group is used for a new purpose" as a trigger to re-review, because the risk context changed.
- **Groups in tokens.** Entra puts at most 200 groups in a JWT, 150 in a SAML token and 6 with the implicit flow. Beyond that the token carries no `groups` claim, only an overage indicator (`hasgroups`, or `_claim_names` with a `groups` member), and the app must call Microsoft Graph. An app that reads "no `groups` claim" as "no groups" mishandles every overage user; whether it fails open or closed, it is wrong (our judgement). The caps are token-size limits: Microsoft's remedies are group filtering, assigning groups to app roles, or Graph, not raising the cap.
- **Better mapping.** Entra recommends assigning groups to app roles, so the token carries a `roles` claim. Always define a baseline role with no elevated rights.

## Where the decision lives

There are three places: **IdP claims** (decided at token issue, trusted by the app), **app-side checks** (the app maps a claim or its own data to permissions) and a **policy engine**. In NIST's ABAC architecture the policy decision point (PDP) computes the decision, the policy enforcement point (PEP) enforces it, the policy information point (PIP) supplies attributes and the policy administration point (PAP) manages policy.

Claims are snapshots. Microsoft states that group information in a token is current only when you receive the token, and that apps needing real-time membership should use Graph. Per Microsoft's CAE page, access tokens last about an hour by default (lesson 1: a random 60 to 90 minutes); with continuous access evaluation (CAE) they can last up to 28 hours, but critical events (user disabled or deleted, password reset, admin revoking all refresh tokens) are meant to take effect within about 15 minutes (Microsoft), and only by resource providers that subscribe to those events. Microsoft notes that group or Conditional Access changes can still take up to a day to reach its resource providers under CAE, and that "Revoke Session" applies them at once.

RFC 7009 section 3 spells out the trade-off. A self-contained token needs no call to the authorization server, so revocation needs extra backend work or short lifetimes. A handle token forces a lookup on every use. Introspection (RFC 7662) returns an `active` boolean. In Okta, revoking a refresh token revokes its access token, but revoking an access token does not revoke the refresh token.

Rule of thumb: put coarse, slow-changing facts in claims; make a live check before high-impact actions.

## Joiner, mover, leaver

Microsoft's lifecycle page says many organizations model three phases: a **joiner** enters the scope of needing access, a **mover** moves between boundaries that need different access (its example is Sales to Marketing), a **leaver** leaves that scope. It notes that joining could be automated from a system of record such as Workday; treating the HR event as the trigger for all three is the usual design, not Microsoft's rule. CIS Safeguard 6.1 asks for a documented, preferably automated process for granting access on new hire or role change; 6.2 asks for revoking it, "through disabling accounts immediately upon termination, rights revocation, or role change".

- **Birthright access** is the baseline every joiner gets from attributes (department, location). Keep it small.
- **Movers** are the quiet risk. NIST SP 800-53 PS-5 requires reviewing and confirming the ongoing need for access when someone is reassigned. Without it, old access stays and privilege accumulates.
- **Leavers** need every surface checked, not one status flipped:

| Surface | What to check |
| --- | --- |
| Account | Okta deactivation removes app access, stops Okta sessions and deprovisions apps only "if deprovisioning is enabled for an app"; Okta's API reference calls it destructive (deprovisioned apps might lose data such as email or files), while suspension stops sessions and keeps group and app assignments, so it is the temporary hold |
| App sessions | apps keep their own sessions, which is why OIDC Back-Channel Logout lets a provider tell an app to end one |
| Tokens | refresh and access tokens until expiry or revocation |
| API keys, PATs | a key made inside a SaaS app is that app's credential, and nothing in Okta's description of deactivation covers it (our reading; Okta's pages do not mention app-created keys either way). An unattended job authenticates with a key or token, not the owner's browser session, so stopping sessions does not stop it; Okta API tokens inherit their creator's privileges and are deprovisioned when the creator is deactivated, so offboarding the admin who made one breaks automation |
| Shared secrets | AC-2 requires changing shared account authenticators when individuals leave a group |
| Delegated access | mailbox delegates and forwarding rules |
| Devices | PS-4: retrieve security-related system property |

Offboarding that stops at SCIM deactivation misses many of these surfaces. In RFC 7643, `active` is the user's "administrative status" and "the definitive meaning of this attribute is determined by the service provider", so `active: false` ends sessions, keys or tokens only if a service provider chooses to, and many do not on their own. PS-4 also requires terminating or revoking the individual's authenticators and credentials, and disabling access within an organization-defined time.

## Least privilege, reviews and non-human identities

AC-6 reads: allow only the accesses "necessary to accomplish assigned organizational tasks". Just-in-time access applies it over time: in Entra PIM a role is eligible until activated, with a time limit, optional approval, MFA and a justification. CIS 5.4 adds dedicated administrator accounts.

Access reviews are how you prove it. In SOC 2 (2017 Trust Services Criteria; wording from secondary summaries, because the AICPA text is not freely retrievable) CC6.2 requires removing credentials when access is no longer authorized and lists periodic review of access appropriateness as a point of focus; CC6.3 requires roles, least privilege and segregation of duties. NIST AC-5 covers separation of duties and AC-6(7) reviewing privileges. ISO/IEC 27001:2022 Annex A has 5.18 Access rights, 5.3 Segregation of duties and 8.2 Privileged access rights (numbers from secondary publishers; the standard is paywalled). **Rubber-stamping** is approving a whole list without seeing what each entitlement allows: the evidence exists, the control does not. Entra's reviews offer reviewer recommendations.

Non-human identities need an owner; an **orphaned** service account has no active owner. CIS 5.5 requires an inventory of service accounts with department owner, review date and purpose; 5.3 says delete or disable any account inactive (dormant) for 45 days "where supported". Orphaned and dormant are different tests: an orphan that is still in use is not dormant, and disabling or deleting it blind can break whatever runs on it. Find its consumers, then assign an owner or retire it deliberately, and record owner and purpose. CIS 6.2 adds that disabling instead of deleting may be necessary to preserve audit trails. RFC 6749 section 4.4 allows the client credentials grant only for confidential clients and says a refresh token SHOULD NOT be issued. Prefer workload identity: GitHub Actions OIDC exchanges short-lived tokens so you "won't need to duplicate your cloud credentials as long-lived GitHub secrets", and AWS tells you to use roles' temporary credentials. Okta documents tokens valid 30 days from creation or last use, and recommends OAuth 2.0 over SSWS tokens.

Log every identity change (lifecycle, group membership, admin role, token creation). Okta's catalog includes `user.session.clear` and `system.api_token.revoke`.

## Your task: run an access review

Written for this lesson; the output below is real, from running it in a sandbox. Invented data, no real accounts. Save as `accounts.csv`:

```csv
account,kind,owner,owner_status,dept,entitlement,last_login
ana.ruiz,user,ana.ruiz,active,sales,crm_user,2026-09-30
ben.okafor,user,ben.okafor,active,support,crm_admin,2026-09-29
cai.wen,user,cai.wen,active,it,idp_admin,2026-09-30
dee.shah,user,dee.shah,active,support,crm_user,2026-06-02
svc-backup,service,,none,it,storage_write,2026-09-30
svc-report,service,eli.novak,terminated,finance,db_read,2026-09-30
svc-legacy-sync,service,fay.lund,active,it,crm_admin,2026-04-11
```

Save as `review.py` and run `python3 review.py`. Invented policy: admin entitlements only for dept `it`.

```python
import csv, datetime as dt

today = dt.date(2026, 10, 1)  # fixed date so the output is repeatable
for r in csv.DictReader(open("accounts.csv")):
    flags = []
    if r["kind"] == "service" and r["owner_status"] != "active":
        flags.append("ORPHANED")
    if (today - dt.date.fromisoformat(r["last_login"])).days > 45:
        flags.append("DORMANT>45d")
    if r["entitlement"].endswith("_admin") and r["dept"] != "it":
        flags.append("EXCESS-ADMIN")
    if flags:
        print(f'{r["account"]:<16} {r["entitlement"]:<14} {", ".join(flags)}')
```

```
ben.okafor       crm_admin      EXCESS-ADMIN
dee.shah         crm_user       DORMANT>45d
svc-backup       storage_write  ORPHANED
svc-report       db_read        ORPHANED
svc-legacy-sync  crm_admin      DORMANT>45d
```

Answer in writing: who should each flag go to (account owner, department head, service owner), what you would check before disabling anything, and why `svc-legacy-sync` is riskier than `dee.shah` despite the same flag. Next: lesson 8 pulls the whole course into a decision guide and a debugging method.
