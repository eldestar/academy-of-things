# Terraform for Okta and SaaS configuration

You know what every Okta policy, rule and app setting does. This lesson is about expressing that estate as code without breaking production, and about the places where the Okta provider's behaviour will surprise someone who thinks in Admin Console terms.

> Facts checked 2026-10-03 against the Terraform Registry API, the `okta/terraform-provider-okta` repository docs (7.0.0, published 2026-08-24, registry tier "partner"), Okta's developer guides, and the registry and GitHub pages named below. Resource and attribute names come from those docs. Provider docs change between releases, so confirm against the version you pin.

## What the provider covers

The `okta/okta` docs directory lists about 160 resources and over 100 data sources. Names you will use: `okta_group`, `okta_group_rule`, `okta_group_memberships`, `okta_app_saml`, `okta_app_oauth`, `okta_app_group_assignments`, `okta_app_signon_policy` and `okta_app_signon_policy_rule(s)`, `okta_policy_signon` and `okta_policy_rule_signon`, `okta_policy_mfa` and `okta_policy_rule_mfa`, `okta_authenticator`, `okta_network_zone`, `okta_behavior`, `okta_trusted_origin`, `okta_event_hook`, `okta_inline_hook`, and per-platform `okta_policy_device_assurance_*` (macOS, Windows, iOS, Android, ChromeOS).

What is not there matters in an interview. I found no resource or data source named for Okta Workflows; the only workflow-related name is `okta_oauth2_v1_clients_role_workflows_admin`, an admin role assignment. Treat Workflows as click-ops or API-driven unless your pinned version shows otherwise. Okta also tells you not to manage the same objects with Terraform and the Admin Console, because it "can introduce synchronization issues". Pick an owner per object type. Users are manageable (`okta_user`), but Okta's import guide says to avoid importing users, since their memberships and assignments make state huge; lifecycle belongs to your HRIS and Workflows.

> The app sign-on (authentication) policy resources work on Identity Engine only; the docs say Classic orgs have no public API for them. `okta_policy_signon` and `okta_policy_rule_signon` are separate resources (the rule resource documents attributes such as `primary_factor` that only work on Identity Engine). Check which policy type each manages in your org before you import.

## Authentication for the provider

The provider supports `api_token` (SSWS, which the docs call a "legacy authorization scheme") or an OAuth 2.0 service app using `client_id`, `private_key_id`, `private_key` and `scopes`. `api_token` conflicts with the OAuth arguments. Okta's provider docs and its Terraform guide recommend OAuth, and its API token guide says tokens "inherit the privilege level of the admin account that is used to create them", are valid 30 days from creation or last use, and can be pinned to network zones. A pipeline that only runs quarterly will meet an expired token.

Okta's Terraform guide sets up an API Services app (client credentials), assigns it an admin role, and grants scopes. It names Organization Administrator or Super Administrator for its group example and the scope `okta.groups.manage`, and says that for production you should "create a custom role and narrow the set of admin permissions" to what Terraform controls. Granting scopes to a service app needs Super Administrator. Okta's scope reference lists, among others, `okta.apps.manage`, `okta.policies.manage`, `okta.authenticators.manage`, `okta.networkZones.manage`, `okta.behaviors.manage` and `okta.deviceAssurance.manage`. Set them per what you manage.

```bash
export OKTA_ORG_NAME="dev-123456"            # placeholders; load from your secret store
export OKTA_BASE_URL="okta.com"              # or oktapreview.com
export OKTA_API_CLIENT_ID="0oa..."
export OKTA_API_PRIVATE_KEY_ID="<kid>"
export OKTA_API_PRIVATE_KEY="<PEM or file path>"   # PKCS#1 or PKCS#8, unencrypted
export OKTA_API_SCOPES="okta.groups.manage,okta.apps.manage"
```
```hcl
provider "okta" {}   # reads the variables above, so no credential sits in a .tf file
```

> Gotcha from the `okta_app_oauth` docs: its `groups_claim` block requires SSWS authentication. With OAuth credentials it is silently skipped (Terraform emits a warning) and the claim is never written. The docs mark `groups_claim` deprecated; `okta_auth_server_claim` is the alternative, but it needs a Custom Authorization Server (API Access Management subscription).

## Adopting click-ops configuration

You will not rebuild a mature tenant from scratch. Terraform's `import` block (introduced in 1.5; Okta's import guide lists Terraform 1.8.5 or later as a prerequisite) binds an existing object to a resource address, and `terraform plan -generate-config-out=generated.tf` writes draft HCL for it.

```hcl
import {
  to = okta_group.engineering
  id = "00g_EXAMPLE"      # the Okta group ID, from the admin URL or API
}
```

Okta's import guide gives the loop: write import blocks, generate config, copy it in, prune it to the arguments you need, replace raw IDs with references, then run `plan` until it shows no changes, and only then apply. HashiCorp flags generation as experimental: output may be invalid where attributes conflict, and the target must not already exist in your config. Policy rule IDs are not in Admin Console URLs, so Okta says to find them through its REST API or SDK. Each resource documents its import ID format, and rules use `<policy_id>/<rule_id>`. A policy's default rule can be imported and updated but not created, renamed or deleted, and Okta manages some of its fields.

## Drift and the console

Drift means someone clicked. `terraform plan` shows it as a diff to revert. `terraform plan -refresh-only` updates state to match reality but leaves config alone, so it records the change without adopting it and the next normal plan proposes reverting it again. Decide per change: revert through apply, or copy the new value into config via a PR. Two documented traps:

- `okta_group_memberships` by default only tracks the users you list, so extra members added in the console are not drift unless you set `track_all_users`.
- If Okta marks a group rule `INVALID`, the provider deletes and recreates it. Okta's rate-limit guide also says to give Okta "sufficient and accurate information" so it does not adjust objects itself, which is how perpetual diffs begin.

## Failure modes at 2am

- **Rate limits.** Provider defaults: exponential backoff on, `min_wait_seconds` 30, `max_wait_seconds` 300, `max_retries` 5. `max_api_capacity` (1 to 100) caps the share of the org's per-minute management API capacity the provider uses. Remove unused resources, and run Terraform in a window that does not starve your Workflows. Okta's Reports > Rate Limits page shows the pressure.
- **Ordering.** `priority` on `okta_policy_signon` errors on invalid values, and the API defaults to last. `okta_app_signon_policy_rules` says to update in priority order and caps custom rules at 99, with a system catch-all at 99. A rename without an explicit `id` is a delete plus create. Separate `okta_app_signon_policy_rule` resources can hit API concurrency problems, so chain them with `depends_on`.
- **A fan-out that never converges.** `for_each` over groups on one `okta_app_group_assignments` makes every instance delete the groups it does not own. Use one resource with a `dynamic "group"` block.
- **Destroy on prod.** Destroying `okta_app_signon_policy` reassigns every app that used it to the default policy; destroying `okta_api_token` revokes the token. Removing a block destroys the object, so gate applies on a human reading the plan.
- **Secrets in state.** `okta_app_oauth` stores `client_secret` in plaintext state unless `omit_secret = true`; flipping it back to false recreates the app. For Terraform 1.11 or later there is `client_basic_secret_wo` (write-only), with `client_basic_secret_wo_version` to trigger a change.

## Other SaaS providers

Registry facts as of 2026-10-03. `hashicorp/googleworkspace` is community tier, its last release was 0.7.0 on 2022-06-10, its README calls it a technical preview not intended for production, and its repository is archived. Unvetted forks exist, for example `SamuZad/googleworkspace` (0.12.0, 2026-08-29). Partner-tier providers I confirmed: `integrations/github`, `auth0/auth0` (Okta's overview points Customer Identity Cloud users there), `pagerduty/pagerduty`, `DataDog/datadog` and `cloudflare/cloudflare`. `pablovarela/slack` is community and last released 2023-04-14. A pragmatic read: Okta usually owns Google Workspace users and groups, so Terraform there is a smaller, riskier win than Okta itself.

## Your task

> Written from the docs, not run against a live tenant. The Okta sandbox and its Terraform setup are in lesson 5 of the separate course `workos-test-environments`; do this there, not in a real org.

1. Create a service app with a narrow custom role and only `okta.groups.manage` and `okta.apps.manage`. Export the variables above.
2. Hand-create a group and a SAML app in the console. Write import blocks, generate config, prune, and reach a zero-diff plan.
3. Change the group description in the console. Run `plan`, then `plan -refresh-only`, and explain the difference out loud.
4. Add an `okta_app_group_assignments` resource with a `dynamic` block, and break it on purpose with `for_each` to see the churn.
