# Authorization and the identity lifecycle

You are designing or reviewing where authorization decisions live, how fresh their inputs are, and how access is removed when a person or workload goes away. The protocols from earlier lessons say who someone is; nothing in them keeps what they may do correct. Facts checked 2026-10-06 against the cited docs. Where a source is secondary, the text says so.

## Models at spec level, and their failure modes

NIST SP 800-162 defines ABAC as granting or denying requests "based on assigned attributes of the subject, assigned attributes of the object, environment conditions, and a set of policies". It frames ACLs and RBAC as "in some ways special cases": ACLs work on the attribute "identity", RBAC on "role"; the difference is policies as Boolean rules over many attributes. It adds that expressing ABAC needs through ACLs or RBAC makes demonstrating compliance "difficult and costly", and a changed requirement is hard to trace to every place that implements it. On ACLs it warns that failure to remove access over time "leads to users accumulating privileges". Its reference architecture has a PEP (enforces), PDP (computes the decision), PIP (retrieves attributes) and PAP (creates, manages, tests and debugs policy). A subject may be a human or a non-person entity (NPE).

The NIST RBAC model behind INCITS 359 has core RBAC (many-to-many user-role and permission-role assignment, users may exercise several roles at once), optional hierarchies, and two separation-of-duty relations. In the 2001 NIST RBAC paper (Ferraiolo et al., ACM TISSEC 4(3), section 2.2) a hierarchy is a seniority partial order in which senior roles acquire the permissions of their juniors: it is inheritance, and it does not limit which roles one person may combine. A role is **active** when the user has activated it in a session: a session activates some subset of the roles the user is assigned. **Static** SoD is a pair (role set, n): no user is assigned n or more roles from the set. **Dynamic** SoD instead constrains which roles may be active within or across a user's sessions. Example: staff who cover for each other may be assigned both invoice-creator and invoice-approver, but never have both active together. With hierarchies, static constraints must count inherited roles as well.

Zanzibar's relation tuples (paper section 2.1), which OpenFGA calls ReBAC (the paper does not use that term), are `object#relation@user`, where the user may be a userset `object#relation`. "Groups are simply ACLs with membership semantics", and usersets give nested groups: `doc:readme#viewer@group:eng#member`. OpenFGA defines ReBAC as permissions modelled as relationships between users and resources rather than roles assigned to users or attributes attached to objects, so a share to one customer is a relationship, not a user attribute. Its current DSL expresses roles as relations (from its modeling-roles guide; not run here):

```
model
  schema 1.1

type user

type organization
  relations
    define admin: [user]
    define can_create_project: admin
```

Failure modes at this level share a root cause: a second copy of truth.

- **Role explosion.** 800-162 attributes it to forcing dynamic, multi-factor decisions into roles, producing ad hoc roles with limited membership. OpenFGA's docs add that per-tenant roles multiply (admin of org 42 versus 43) while ReBAC needs one tuple per share; that is a vendor's claim. A hierarchy relates roles by inheritance, so it does not remove the per-tenant role multiplication (our reading).
- **Attribute drift.** (Our term.) Section 2.4.2 says attributes come from authorities (HR for name, Security for clearance), must be normalised, and must be mapped between the enterprise schema and application schemas. Drift is those authorities and copies disagreeing at decision time.
- **Relationship sprawl.** (Our term.) OpenFGA's token-claims guide admits that synchronising directory data into tuples "can be challenging". Unsynchronised or unreviewed tuples accumulate like ACL entries.

## Claims versus live checks

RFC 9068 section 2.2.2 observes that authorization servers often put resource-owner attributes in access tokens so resource servers avoid "further round trips" to introspection or UserInfo. RFC 7009 section 3 then names the cost: a self-contained token needs no call to the authorization server, so immediate revocation needs non-standardized backend signalling; a handle token forces a lookup on every use; short-lived tokens bound the revoked-but-valid window. Introspection returns `active`, which generally means issued here, not revoked, and inside its validity window (RFC 7662 section 2.2).

NIST 800-162 section 3.3.1 states the same trade-off for attributes: caching helps latency, but "attributes that are not refreshed as often will ultimately be less secure". OpenFGA documents using token claims as contextual tuples and warns that if relationships change before the token expires, users keep the access the token granted. Zanzibar attacks the problem inside the store, with the cooperation of its clients: the "new enemy" problem is applying a stale ACL to new content (remove Bob, save new content, Bob still reads it). It uses external consistency and opaque `zookie` tokens, which the client requests and stores with each content version, so a check is evaluated on ACL data no older than that version.

Microsoft's numbers show the layers. Group claims cap at 200 (JWT), 150 (SAML) and 6 (implicit flow); beyond that the token carries an overage indicator and you query Graph. Access tokens default to about an hour (a random 60 to 90 minutes, lesson 1); CAE sessions run up to 28 hours, with the issuer telling the resource provider to stop honouring tokens on critical events. The CAE page says latency of up to 15 minutes may be seen for critical events, yet group and Conditional Access changes "could take up to one day" to take effect. Both are on the same page, so design for the one that matches your change type. CAE is based on OpenID CAEP; CAEP 1.0 (document dated 29 August 2025) defines Session Revoked, Token Claims Change, Credential Change, Assurance Level Change, Device Compliance Change, Session Established, Session Presented and Risk Level Change events.

Design rule: classify each decision by blast radius. Coarse, slow-changing facts may live in claims, and the token lifetime is then your revocation SLA. High-impact actions call a live check, whether introspection, a PDP or Graph.

## Policy-as-code and externalized authorization

OPA "decouples policy decision-making from policy enforcement": the service queries it with structured JSON input and the policy is written in Rego. Cedar writes policies over principal, action, resource and context. OpenFGA answers a different question, a graph check. OpenFGA's own docs point pure attribute checks to attributes and infrastructure or admission policy to policy engines. Mapped to NIST: the app or gateway is the PEP, the engine is the PDP, directory, HR and token data are PIPs, and a repository with CI that tests policy is the PAP.

Pitfalls: attribute inputs that the caller can forge; PIP freshness (section 3.3.1 again); no decision logging; and unreviewed rights to change policy, which we would treat as a privileged role under AC-5 separation of duties (our inference; AC-5 does not mention policy repositories). Whether the PEP fails open or closed when the PDP is unreachable is not prescribed by these sources; decide and document it.

## Non-human identities

CIS 5.1 requires an inventory of user and administrator accounts, and 5.5 a separate inventory of service accounts with department owner, review date and purpose. The client credentials grant (RFC 6749 section 4.4) is for confidential clients only, and section 4.4.3 says a refresh token SHOULD NOT be included. Federate workloads instead of storing secrets: GitHub Actions OIDC tokens carry `iss` `https://token.actions.githubusercontent.com` and a `sub` identifying the workflow source, such as `repo:octo-org/octo-repo:environment:prod`, and the workflow needs `id-token: write`. AWS advises roles with temporary credentials, and for workloads outside AWS lists `AssumeRoleWithWebIdentity` with a JWT from a configured IdP. Long-term access keys are the exception, to be updated "when an employee leaves your company".

Okta API tokens show the human-coupling trap: they inherit the creating admin's privileges, change with that admin's role, are deprovisioned when the creator is deactivated, and are valid 30 days from creation or last use. Okta recommends a service account for creating tokens and OAuth 2.0 over SSWS. Entra PIM can also assign roles to service principals and managed identities, with time bounds.

## Designing a leaver runbook with verification

Treat "deactivated" as a claim, not evidence. In RFC 7643 section 4.1.1, `active` is administrative status and "the definitive meaning of this attribute is determined by the service provider", so a successful SCIM update proves little about sessions, keys or tokens. NIST PS-4 requires disabling access within an organization-defined period, revoking authenticators and credentials, retrieving property and retaining access to information the person controlled. Okta states deletion cannot be undone, and its API reference calls deactivation destructive too: "The user is deprovisioned from all assigned apps, which might destroy their data such as email or files. This action cannot be recovered!" Suspension is the non-destructive hold: it stops sessions and retains group and app assignments. CIS 6.2 adds that disabling instead of deleting may be necessary to preserve audit trails. Which Okta state your offboarding uses, and how long data is retained before deactivation or deletion, is your policy (not Okta's rule): decide it explicitly.

| Surface | Action | Verify with |
| --- | --- | --- |
| Owned non-human credentials | reassign before deactivating | inventory query for creator = person |
| IdP account and sessions | suspend as the reversible hold, or deactivate once app data has been handled; clear sessions, optionally OAuth tokens | account state; sessions = 0 |
| App accounts (no SCIM) | disable by hand | per-app export |
| App sessions and tokens | back-channel logout or CAEP Session Revoked; else wait out the TTL | per-app test |
| Keys, shared secrets | revoke; rotate (AC-2) | key list; rotation date |
| Delegation, devices | remove forwarding and delegates; collect device | mailbox audit; asset record |

Log each step (AU-12 generates records for the event types you define); Okta's catalogue includes `user.session.clear` and `system.api_token.revoke`. SOC 2 CC6.2 (wording from secondary summaries; the AICPA text is not freely retrievable) requires credentials removed when access is no longer authorized; ISO/IEC 27001:2022 control 6.5 (secondary sources) covers termination or change of employment.

## Your task: verify, do not trust

Written for this lesson; the output is real from a sandbox run, with invented evidence. Save as `evidence.json` the post-leaver checks for one person (expect versus observed), then run the jq commands.

```json
[
  {"surface": "idp account",                   "expect": "deactivated", "observed": "deactivated"},
  {"surface": "idp sessions",                  "expect": "0",           "observed": "0"},
  {"surface": "crm account (no SCIM)",         "expect": "disabled",    "observed": "active"},
  {"surface": "crm api keys made by user",     "expect": "0",           "observed": "2"},
  {"surface": "oauth grants / refresh tokens", "expect": "0",           "observed": "1"},
  {"surface": "mail forwarding rule",          "expect": "none",        "observed": "to a personal address"},
  {"surface": "shared secrets user could read","expect": "rotated",     "observed": "not rotated"},
  {"surface": "laptop",                        "expect": "returned",    "observed": "returned"}
]
```

```
$ jq -r '.[] | select(.expect != .observed) | "FAIL \(.surface): expected \(.expect), found \(.observed)"' evidence.json
FAIL crm account (no SCIM): expected disabled, found active
FAIL crm api keys made by user: expected 0, found 2
FAIL oauth grants / refresh tokens: expected 0, found 1
FAIL mail forwarding rule: expected none, found to a personal address
FAIL shared secrets user could read: expected rotated, found not rotated
$ jq -r 'length as $n | map(select(.expect != .observed)) | length as $f | "\($f) of \($n) checks failed"' evidence.json
5 of 8 checks failed
```

Task: extend the runbook table with an owner and a deadline per row, then write the check that makes the ticket impossible to close while any row fails (`jq -e 'all(.[]; .expect == .observed)'` exits 1 here). Next: lesson 8 turns this into a review checklist.
