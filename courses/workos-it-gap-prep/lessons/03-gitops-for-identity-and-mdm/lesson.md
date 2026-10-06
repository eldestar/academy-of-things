# GitOps for identity and device management

Lessons 1 and 2 gave you the tool. GitOps is the discipline around it: nobody runs `apply` from a laptop, every change to identity or device policy is a reviewed pull request, and the pipeline is the only identity that can write. For SOC 2 and ISO 27001 you already know the payoff: the PR is the change record and the approval.

> Facts checked 2026-10-03 against HashiCorp, GitHub, AWS, Jamf, Iru and registry documentation. GitHub Actions snippets use only syntax I confirmed in GitHub's docs. The pipeline and labs were not run against a live repo or tenant.

## The loop and the repo shape

The loop: open a PR, CI runs `fmt`, `validate` and `plan`, a human reads the plan, merge to `main`, CI applies. HashiCorp's automation guide adds three habits: set `TF_IN_AUTOMATION`, pass `-input=false`, and apply a saved plan (`plan -out=tfplan`, then `apply tfplan`) so the file that was approved is the file that runs; the pipeline below does this at merge time, behind the approval gate. It says manual plan review "is always recommended unless downtime is tolerated", which for a prod identity tenant means always.

```text
okta/prod/          one state, one tenant, prod credentials
okta/preview/       separate state and separate credentials
mdm/jamf/  mdm/iru/ scripts, profiles and config, reviewed like code
.github/CODEOWNERS  .github/workflows/
```

## A workflow skeleton

Replace each `<full-commit-sha>` with the full-length SHA of the release you reviewed. GitHub says that is "the only way to use an action as an immutable release". Account IDs and names are placeholders.

```yaml
name: okta-terraform
on:
  pull_request:
    paths: ["okta/**"]
  push:
    branches: [main]
    paths: ["okta/**"]
  schedule:
    - cron: "17 6 * * 1-5"          # UTC, default branch only, may be delayed or dropped; not on the hour
  workflow_dispatch:                 # the Run workflow button needs this file on the default branch
permissions:
  contents: read
  id-token: write                    # allows the OIDC token request
env:
  TF_IN_AUTOMATION: "true"
defaults:
  run:
    working-directory: okta/prod     # for okta/preview, change this and `paths` above
jobs:
  plan:                              # read role and read-scope Okta app; PR plan and merge-time plan
    if: github.event_name == 'pull_request' || github.event_name == 'push'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@<full-commit-sha>
      - uses: aws-actions/configure-aws-credentials@<full-commit-sha>
        with: { role-to-assume: "arn:aws:iam::111111111111:role/tf-okta-plan", aws-region: us-east-1 }
      - uses: hashicorp/setup-terraform@<full-commit-sha>
        with: { terraform_wrapper: false }
      - run: terraform init -input=false
      - run: terraform fmt -check && terraform validate
      - run: terraform plan -input=false -lock-timeout=5m -out=tfplan
        env:
          OKTA_ORG_NAME: dev-123456
          OKTA_BASE_URL: okta.com
          OKTA_API_CLIENT_ID: ${{ secrets.OKTA_PLAN_CLIENT_ID }}
          OKTA_API_PRIVATE_KEY_ID: ${{ secrets.OKTA_PLAN_KEY_ID }}
          OKTA_API_PRIVATE_KEY: ${{ secrets.OKTA_PLAN_PRIVATE_KEY }}
          OKTA_API_SCOPES: okta.groups.read,okta.apps.read,okta.policies.read
      - run: terraform show -no-color tfplan >> "$GITHUB_STEP_SUMMARY"
      - if: github.event_name == 'push'
        uses: actions/upload-artifact@<full-commit-sha>
        with:
          name: tfplan
          path: okta/prod/tfplan     # artifact paths ignore working-directory
          retention-days: 1          # the plan file holds secrets in cleartext
  apply:                             # waits for approval, then applies the file plan just saved
    needs: plan
    if: github.event_name == 'push'
    runs-on: ubuntu-latest
    environment: okta-prod           # required reviewers configured in repo settings
    concurrency:
      group: okta-prod-apply
      cancel-in-progress: false
    steps:
      # checkout, credentials (tf-okta-apply), setup-terraform, init: as in plan
      - uses: actions/download-artifact@<full-commit-sha>
        with: { name: tfplan, path: okta/prod }
      - run: terraform apply -input=false tfplan     # env: manage-scope Okta app
  drift:                             # same setup as plan, read-only
    if: github.event_name == 'schedule' || github.event_name == 'workflow_dispatch'
    runs-on: ubuntu-latest
    steps:
      # checkout, credentials (read-only role), setup-terraform, init: as in plan
      - run: terraform plan -input=false -lock-timeout=5m -detailed-exitcode   # exit 2 fails the job
```

Notes. The plan a reviewer reads is the PR plan. After merge, `plan` runs again and saves `tfplan`; `apply` waits at the `okta-prod` approval, so the approver reads that merge-time plan in the step summary and `apply tfplan` executes that exact file. Terraform rejects a saved plan if state changed after it was made, so a stale approval fails safe and you re-run. HashiCorp says saved plans need identical paths, hence the same `okta/prod` in both jobs. Treat the artifact like state (lesson 1): one-day retention, narrow repo access. A concurrency group is what serialises applies: GitHub says there can be "at most one running job or workflow in a concurrency group at any time", so dropping the block would allow two applies at once against one state. `cancel-in-progress: false` matters: cancelling a running apply leaves a partial apply (lesson 1). With it false, a newly queued run waits as pending, and by default a newer pending run replaces an older pending one (a `queue` property can change that). Nothing is lost by the replacement, because every run plans the whole configuration at its own commit, so the newer commit already contains the older one's change. Plan output in PR comments is capped at 65,536 characters (GitHub's API error text; not in the docs), so the plan goes to `$GITHUB_STEP_SUMMARY`. Run the schedule off the top of the hour: GitHub says queued runs may be dropped under high load. For `pull_request` runs from forks, secrets are not passed except `GITHUB_TOKEN`. Environments exist in public repos on every plan; private repos need Pro, Team or Enterprise, and GitHub says that on Free, Pro or Team, required reviewers are only available for public repositories. The approval gate in a private repo therefore needs Enterprise. Check your plan before relying on it.

## Credentials in CI

OIDC means the job exchanges a short-lived GitHub token for an AWS role, so no long-lived AWS keys sit in the repo. The trust policy needs `token.actions.githubusercontent.com:aud` equal to `sts.amazonaws.com` and a `sub` condition, and the `sub` format depends on the repo. GitHub's OIDC reference says repositories created after 2026-07-15, or opted in, include immutable IDs (`repo:OWNER@OWNER-ID/REPO@REPO-ID:ref:refs/heads/main`); older repos use `repo:ORG/REPO:ref:refs/heads/main`. The docs show the environment form as `repo:ORG/REPO:environment:okta-prod`; on a new repo expect the ID form (my inference), so copy the exact `sub` from a decoded token or the AccessDenied message. A `pull_request` job with no environment sends `repo:ORG/REPO:pull_request`; the `push` plan job sends the branch form. Trust both on the plan role. Scope the apply role to the environment `sub`, so only a job that passed approval can assume it, and restrict the environment to `main`, or a branch can declare `environment: okta-prod` and ask for approval of its own workflow. Two facts make that gate real. First, GitHub's OIDC reference says the `sub` carries the environment name when the job references an environment, and carries the branch (or `pull_request`) form only when it does not, so the branch-form `sub` is what any job on that ref sends, approved or not, including the plan job. A trust policy that matches it, or any `sub` under the org, lets an unapproved job assume the apply role. Second, `aud` only names who the token is for (here AWS STS); GitHub says audience and subject are used in combination to scope access, so `aud` alone restricts nothing about which repo, branch or environment may assume the role.

> OIDC removes long-lived cloud keys, not the Okta credential. The provider still needs an API token or a service-app private key. Store the apply credential as an environment secret: GitHub says "A workflow job cannot access environment secrets until approval is granted by required approvers", and GitHub documents the required-reviewer control for environment secrets, not for repository secrets. A repository secret has no approval step, so any job in the repository's workflows that references it can read it, including the unapproved plan job; the plan job above reads its own read-scope secrets that way on purpose. You can also fetch the credential with `aws secretsmanager get-secret-value --secret-id <name> --query SecretString --output text`. Use two Okta service apps: read scopes for plan and drift (Okta publishes `.read` variants), manage scopes only for apply. The plan role is read-only for Okta and AWS resources, but it still needs the `.tflock` permissions from lesson 1. A PR author controls the config that plan runs with, so keep plan credentials read-only. GitHub push protection can block known secret patterns, but only those; it needs GitHub Secret Protection on repositories.

## Locking and drift

Every plan and apply takes the state lock, so give the CI role the `.tflock` permissions from lesson 1. A runner killed mid-apply leaves the lock behind; use `terraform force-unlock LOCK_ID` only after you know no apply is live. Drift detection is the scheduled job above. `-detailed-exitcode` returns 0 for no diff, 1 for error, 2 for a diff, and 2 fails the step. A diff means console drift or merged-but-unapplied config, so the alert has to say which. GitHub notes scheduled runs use the default branch, may be delayed under load, and are disabled in public repos after 60 days without activity. HCP Terraform offers drift detection as health assessments, but only in Standard and Premium editions. Atlantis is an open-source, self-hosted tool that runs `plan` and `apply` from pull request comments, if you want that model.

## Blast radius

Split states by tenant (prod, preview) and by risk domain, so a bad apply or a leaked read credential reaches one slice, and workspaces do not count as isolation. Use CODEOWNERS (in `.github/`; the last matching pattern wins) and enable "Require review from Code Owners" in branch protection or rulesets. Any one listed owner satisfies the rule, and CODEOWNERS should itself be owned, or anyone can edit who reviews what.

## MDM as code

**Jamf Pro.** There is no Jamf-published provider that I found. The registry's `deploymenttheory/jamfpro` (community tier, MPL-2.0, public preview) says it is not officially supported by Jamf, and it has about 74 resource pages including policies, scripts, smart computer groups, configuration profile plists and prestage enrollments. Its README lists Terraform 1.13.0 or later and Jamf Pro 11.20.0 or later, and warns that default parallelism 10 behaves inconsistently with Jamf; it recommends `-parallelism=1`. Jamf Cloud sits behind a load balancer where a created resource can take up to 60 seconds to appear on the other web app member, so reads right after creates can fail; the provider ships a lock resource for sticky sessions. Auth is OAuth2 client credentials from a Jamf API role and client, and Jamf says adding or removing a role on an existing client needs a secret rotation to take effect.

**Kandji, now Iru.** Its API uses tenant bearer tokens with per-route permissions and a shared limit of 10,000 requests per hour per customer. Iru's own `kandji-inc/iructl` (MIT) syncs a local repo of custom profiles, scripts and apps with the tenant (`iructl profile pull --all`, `iructl script pull --all`), and its blueprint assignment feature is marked experimental. Terraform providers exist only as individual community projects: `ja-guerrero/iru` on the registry (0.1.0), plus a `MScottBlake/terraform-provider-iru` repository I could not find on the registry API, although a search result pointed to a registry page for it. Treat both as early.

The pattern for either MDM: scripts and profiles live in Git, PR review before they reach a scope, and a staged rollout, because a profile pushed to a broad scope hits the whole fleet.

## Your task

> Written from the docs, not run against a live repo or tenant. Use the Okta sandbox from lesson 5 of the separate course `workos-test-environments`.

1. Create a repo with `okta/preview/`, a CODEOWNERS file, branch protection with code-owner review, and the workflow above pointed at the sandbox (change `working-directory` and `paths` to `okta/preview`), with two Okta apps (read and manage scopes). Decode a job's OIDC token, or read the AccessDenied message, to get the exact `sub` before writing the trust policy. Required reviewers need a public repo unless you are on Enterprise, so for a sandbox repo with no secrets in it, make it public. On a private Free, Pro or Team repo, drop the pause: make the apply a manually started run and accept that GitHub no longer records the approval.
2. Open a PR that adds a group, read the plan, merge, approve the environment (or start the apply) and watch it.
3. Change a group description in the console, start the drift job from the Run workflow button, and confirm it fails with exit code 2.
4. Write a half-page runbook for a stuck state lock, and one for a mistaken destroy plan.
