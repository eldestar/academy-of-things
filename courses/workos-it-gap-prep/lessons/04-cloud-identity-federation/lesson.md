# Cloud identity federation on GCP and AWS

The posting lists "Cloud infrastructure experience (GCP or AWS)" as nice-to-have. You are not being asked to run Kubernetes. You are being asked whether you can wire a workforce IdP into a cloud, keep access least-privilege, and not leave long-lived credentials lying around. Facts checked 2026-10-03 against AWS and Google Cloud docs; limits and defaults below are dated and can change.

## What you know and what is new

| | You already know | New to you |
| --- | --- | --- |
| AWS | Okta to IAM Identity Center (SAML + SCIM) | Direct IAM SAML federation, IAM roles, trust policies |
| Google | Workspace admin, Okta provisioning into Workspace | Cloud IAM, org policy, Workforce Identity Federation, service accounts |

The mental shift: in the cloud the IdP is only the front door. Authorization lives in the cloud's own policy engine (permission sets, role trust policies, IAM bindings), and that is where an auditor or an incident will look.

## AWS: Identity Center versus direct IAM federation

**Identity Center** is AWS's recommended path for workforce access to many accounts. SAML authenticates; SCIM is how Identity Center learns who exists, because SAML cannot be queried for users and groups. **Direct IAM SAML federation** has no directory: you register the IdP as a SAML provider in IAM, write a role trust policy naming it, and the assertion carries a `https://aws.amazon.com/SAML/Attributes/Role` attribute with a role ARN and provider ARN pair. AWS's own emergency-access guidance uses direct federation as the fallback path. Opinion: humans through Identity Center, direct federation only for break-glass or a single odd account.

Failure modes that the docs state and the happy-path tutorial buries:

- **SCIM token expiry.** The access token is valid one year. AWS reminds you at 90 days or less, in the console and the AWS Health Dashboard. If it expires, sync stops: no creates, updates or deletes. Offboardings silently stop propagating. Put the rotation date on a calendar you own; do not rely on a reminder reaching the right inbox.
- **Group sync scope.** Only users and groups assigned to the Okta app are provisioned. Using the same Okta group for assignment and for Push Groups is not supported, so keep a separate push group. Entitlements and role attributes do not sync. You can assign both people and groups to the app, so mixed assignment is not an error, though AWS's Okta guide recommends assigning and pushing groups rather than individual users. Multi-Region Identity Center does not split the user store: workforce identities replicate from the primary Region, and the additional-Region documentation covers access portal and ACS endpoints, so a provisioning failure for specific users is not a per-Region problem.
- **Required attributes.** First name, last name, username and display name must all exist or the user is not provisioned. Multivalue attributes make sync fail. The attribute you send as the SAML `NameID` must be the one mapped to Username, or sign-in fails.
- **Console-side edits drift.** Identity Store mutation APIs stay open under SCIM, and SCIM syncs deltas, so a manual group add can survive and become unreviewed privilege. AWS shows an SCP denying `identitystore:Create*`, `Update*` and `Delete*` on the delegated admin account; it does not apply to the management account.
- **Session layers.** Permission-set session duration defaults to 1 hour (range 1 to 12). The access-portal session defaults to 8 hours (15 minutes to 90 days). Ending a portal session does not shorten an already-open console session. In direct federation the optional `SessionDuration` attribute is 900 to 43200 seconds, one hour if absent.
- **Silent cert drift (direct IAM federation).** IAM does not act on X.509 expiry in SAML metadata, so you monitor IdP signing-cert dates yourself.

## Google Cloud: two ways in

1. **Google identities.** Cloud Identity or Workspace owns the accounts; Okta provisions into them and acts as SAML IdP.
   - Creating a project under a Workspace or Cloud Identity account auto-provisions the **organization** resource.
   - SSO needs both a Google account and a matching IdP identity, so a missed provisioning run is a sign-in failure.
   - Super admins bypass SSO by design and sign in with a Google password, so your IdP's MFA does not cover them. Google says super-admin SSO is supported only on the legacy SSO profile and recommends migrating off it.
2. **Workforce Identity Federation.** OIDC or SAML 2.0, with no synced accounts: Google stores no user accounts.
   - A **workforce pool** is created at organization level; a **provider** describes the IdP; `google.subject` must be mapped.
   - Session length is 15 minutes to 12 hours, default 1 hour, and covers console and gcloud sessions.
   - Google's Okta guide gives this SAML mapping:

```
google.subject=assertion.subject, google.groups=assertion.attributes['groups'], attribute.department=assertion.attributes['department'][0]
```

IAM then references `principal://iam.googleapis.com/locations/global/workforcePools/POOL_ID/subject/...` or `principalSet://.../group/GROUP_ID`. Traps:

- An Okta OIDC app from the App Catalog sends up to 100 groups by default.
- A multi-tenant IdP with a single issuer needs attribute conditions, or another tenant's users qualify.
- A deleted pool or provider can be undeleted for 30 days, which is useful in a drill and worth knowing during an incident.

## Authorization: IAM, org policy, service accounts

- **Roles.** Google says not to grant basic roles in production unless there is no alternative. Prefer predefined, then custom (300 per organization and 300 per project; none at folder level). Grants inherit downward, additively.
- **Org policy.** Google's key-management constraints are `iam.managed.disableServiceAccountKeyCreation` and `iam.managed.disableServiceAccountKeyUpload`; the older `iam.disableServiceAccountKeyCreation` and `iam.disableServiceAccountKeyUpload` are labelled legacy managed constraints. `iam.serviceAccountKeyExpiryHours` sets expiry. Google recommends applying creation and upload constraints at the organization root, and says organizations created on or after 2024-05-03 have the legacy ones enforced by default, so check what your org inherits. They are not retroactive, so keys that already exist keep working. That is how **orphaned keys** survive a "we locked it down" project.
- **Keys versus workload identity.** Google's guidance is to avoid user-managed keys. Alternatives: attached service accounts, and Workload Identity Federation, which exchanges an external OIDC, SAML or AWS/Azure credential for a short-lived token, either by direct resource access or by impersonating a service account. Google advises against key expiry on production workloads because the expiry itself causes an outage. Find leftovers with the key authentication events metric (Cloud Monitoring keeps service account metrics for 6 weeks) and service account insights (no authentication in 90 days). Google notes domain-wide delegation to Workspace APIs is not tracked by insights, so a service account using it can look unused; check those separately, since you own Workspace.

## Break-glass

- **AWS.** Emergency access via direct IAM federation from your IdP works only while IAM and the IdP are both up. If you do not want the IdP dependency, AWS points to its standard break-glass design instead.
- **Timing.** AWS says to deploy emergency access before an outage, because you cannot create the IAM roles during one, and to test it periodically.
- **Google.** Super admins can bypass SSO. Google says this keeps them able to get in when the SSO config is wrong or the IdP is down. Your IdP's MFA does not apply to them.
- Opinion: keep two or three named break-glass identities per cloud with hardware MFA, outside the IdP, alert on any use, and test them each quarter. The hard part is not creating them; it is noticing when one is used.

## Your task

*Written from the docs, not run against a live tenant, except the jq check, which was run in the sandbox on 2026-10-03.* AWS's console role wizard adds a `saml:aud` condition to SAML trust policies. Save this as `good.json`, copy it to `bad.json` with the `Condition` removed, and lint both:

```json
{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Federated":"arn:aws:iam::111122223333:saml-provider/ExampleOrgSSOProvider"},"Action":"sts:AssumeRoleWithSAML","Condition":{"StringEquals":{"saml:aud":"https://signin.aws.amazon.com/saml"}}}]}
```

```sh
for f in good.json bad.json; do jq -r --arg f $f '.Statement[]|select(.Action=="sts:AssumeRoleWithSAML")|"\($f): "+(if ((.Condition.StringEquals//{})|has("saml:aud")) then "ok, saml:aud pinned" else "WARN, no saml:aud condition" end)' $f; done
```

Real output: `good.json: ok, saml:aud pinned` then `bad.json: WARN, no saml:aud condition`. The wizard's global audience is valid, but AWS recommends Regional endpoints (`https://REGION.signin.aws.amazon.com/saml`) for resiliency, so check which your IdP sends. Then write down, for your own AWS and Google estate: the SCIM token expiry date, IdP signing-cert expiry, who holds break-glass, and which service accounts still have keys.

Next: when SSO breaks, it is usually DNS, TLS, cookies or a clock.
