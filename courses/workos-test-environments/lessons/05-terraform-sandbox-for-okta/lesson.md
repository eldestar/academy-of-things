# A safe Terraform sandbox for Okta

You know what a safe Okta change looks like; what you lack is the muscle memory of a tool that applies changes without asking twice. This lesson builds a lab where a mistake costs nothing. It does not re-teach state, backends or the provider tour: for those see `workos-it-gap-prep`, lessons 1 to 3 (Terraform fundamentals and state; Terraform for Okta and SaaS configuration; GitOps for identity and device management). Facts checked 2026-10-03: Terraform 1.16.5 (HashiCorp's version-check API), OpenTofu v1.13.1 (GitHub release, 2026-10-01), `okta/okta` provider 7.0.0 (registry, 2026-08-24).

> **Not run.** Neither `terraform` nor `tofu` is installed in the sandbox where this was written, so `init`, `validate`, `plan` and `apply` below are **written from the docs, not run against a live tenant**, and the HCL has not been through `terraform validate`. Resource and attribute names were each checked against the provider's v7.0.0 docs. Run `terraform validate` first and trust its output over this page.

## Blast-radius rules before any HCL

1. A separate Okta org built for this (lesson 1 of this course), never your employer's tenant, never an org with real users.
2. A credential that can only touch that org, with the smallest scopes that work (next section).
3. A guard in code so a copied `terraform.tfvars` cannot point the lab at the wrong org. The provider takes `org_name` and `base_url` (`okta.com` or `oktapreview.com`), so make both explicit and allowlist the org:

```hcl
variable "okta_org_name" {
  type = string
  validation {
    condition     = contains(["dev-123456"], var.okta_org_name) # your sandbox org(s) only
    error_message = "Refusing to run: this org is not on the sandbox allowlist."
  }
}
variable "okta_base_url" { type = string } # "okta.com" or "oktapreview.com"
```

4. Pin the provider. Version 7.0.0 is a new major whose changelog lists five breaking changes (four resources and one data source, none used here), and the 6.15.0 notes say they resolved breaking changes reported in 6.14.0. A floating version is a surprise waiting for a Friday.

## Credentials with least privilege

The provider supports an OAuth 2.0 service app (`client_id`, `private_key_id`, `private_key`, `scopes`), a pre-obtained `access_token`, or a legacy SSWS `api_token`; these groups are mutually exclusive, and the docs say Okta recommends OAuth 2.0. All can come from `OKTA_*` environment variables (`OKTA_API_CLIENT_ID`, `OKTA_API_PRIVATE_KEY_ID`, `OKTA_API_PRIVATE_KEY`, `OKTA_API_SCOPES`, `OKTA_API_TOKEN`).

Okta's service-app guide adds the constraints that bite: client credentials with `private_key_jwt` is the only supported method for Okta scopes, **every service app needs an admin role assigned** (standard or custom, and the app is limited to what that role covers), scopes are validated against the app's explicit grants, and access tokens last one hour. For this config start with `okta.groups.manage` and `okta.apps.manage`. Whether `plan` needs extra read scopes for refresh is not something I verified; a 403 naming a scope is your answer, and widening one scope at a time beats granting Super Admin to make the error vanish. The private key is a PKCS#1 or PKCS#8 unencrypted PEM; keep the file outside the repo and out of shell history.

## State for a lab

HashiCorp's own guidance: local state is a plaintext file that includes any secret values in your configuration. The remote options for a lab, per current docs: HCP Terraform (free organizations limited to 500 managed resources; state encrypted at rest), or the S3 backend, which needs an AWS account and where `use_lockfile` is the documented locking option and `dynamodb_table` is deprecated. For one operator and a throwaway org, local state is defensible if you accept two rules: it is gitignored, and you treat the directory as secret-bearing.

```gitignore
*.tfstate
*.tfstate.*
.terraform/
*.tfplan
*.tfvars
*.pem
```

Commit `.terraform.lock.hcl`; HashiCorp says to, so provider hash changes get reviewed. Saved plans (`-out`) keep sensitive values in cleartext, hence `*.tfplan`. Where do real secrets land? `okta_app_oauth` persists the auto-generated `client_secret` in state unless `omit_secret = true` (flipping false to true drops it from state, and the secret as of that apply stays in Okta; flipping true back to false recreates the app, to regenerate a secret the provider can store), and its `client_basic_secret_wo` write-only attribute needs Terraform 1.11 or newer. Run `gitleaks protect --staged` (`gitleaks git --staged` in current releases; both exist in v8.30.1 here) anyway; state is not the only way a key reaches a commit.

## A group, a SAML app and an assignment

All names below come from the v7.0.0 resource docs (`okta_group`, `okta_app_saml`, `okta_app_group_assignment`). Values are placeholders from the docs' own example.

```hcl
terraform {
  required_providers { okta = { source = "okta/okta", version = "~> 7.0.0" } }
}
provider "okta" { # credentials come from OKTA_API_* env vars
  org_name = var.okta_org_name
  base_url = var.okta_base_url
}
resource "okta_group" "lab" {
  name        = "tflab-test-users"
  description = "Terraform sandbox lab"
}
resource "okta_app_saml" "lab" {
  label                    = "tflab-sp"
  sso_url                  = "https://sp.example.test/acs"
  recipient                = "https://sp.example.test/acs"
  destination              = "https://sp.example.test/acs"
  audience                 = "https://sp.example.test/audience"
  subject_name_id_template = "$${user.userName}"
  subject_name_id_format   = "urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress"
  response_signed          = true
  signature_algorithm      = "RSA_SHA256"
  digest_algorithm         = "SHA256"
  attribute_statements {
    type         = "GROUP"
    name         = "groups"
    filter_type  = "REGEX"
    filter_value = ".*"
  }
}
resource "okta_app_group_assignment" "lab" {
  app_id   = okta_app_saml.lab.id
  group_id = okta_group.lab.id
}
```

The docs flag one dev-org trap on `okta_app_saml`: "You do not have permission to access the feature you are requesting" means the org needs the `ADVANCED_SSO` feature flag, which only Okta support can add. The `$$` is HCL escaping for a literal `${`; drop one and Terraform tries to interpolate. Apply status changes carry order: the docs say a changed `status` activates or deactivates the app first, then applies the rest.

## Plan, import, drift, destroy

1. **Plan before apply, always.** `terraform plan -out=lab.tfplan`, read the resource counts and the org in your tfvars, then `terraform apply lab.tfplan`. Applying a saved plan means what you reviewed is what runs.
2. **Import.** Create a group by hand in the console (`tflab-console-group`), copy its id from the console, add an empty-ish `okta_group.console` block with the same `name`, then `terraform import okta_group.console <group_id>` (the documented syntax). Plan afterwards: anything other than "No changes" means your HCL differs from reality, so fix the HCL, not the org. The alternative is an `import { to = ..., id = ... }` block plus `terraform plan -generate-config-out="generated.tf"`; the file must not already exist, and Terraform labels this feature experimental and tells you to review the output before committing it.
3. **Force drift.** Edit the lab group's description in the console, then `terraform plan`. You should see an in-place update reverting it. `terraform plan -refresh-only` reports the drift without proposing to revert it, which is the mode for deciding whether the console edit or the code is right.
4. **Destroy cleanly.** `terraform plan -destroy -out=destroy.tfplan`, read it, apply it. Everything imported is destroyed too, so import only objects you are willing to lose. Afterwards confirm in the console, not in the state file, that nothing tagged `tflab` remains.

What breaks at 2am: rate limiting (the provider backs off by default, minimum 30 s, maximum 300 s, 5 retries, and `max_api_capacity` caps the share of the rate limit it will use); a lost state file leaving orphaned objects that need re-import; a provider upgrade changing a plan you thought was empty; and `-auto-approve` copied from a tutorial into CI before you have a review gate.

## Your task

Done when you have: (1) the provider version, org allowlist guard and gitignore committed, with `gitleaks protect --staged` clean and no `*.tfstate` in `git ls-files`; (2) `terraform validate` output pasted, with your Terraform or OpenTofu version; (3) a reviewed plan showing 3 to add, applied, and the group, app and assignment visible in the console; (4) the import of `tflab-console-group` ending in a "No changes" plan; (5) a drift screenshot plus the plan that reverts it; (6) a destroy plan, its apply, and a console check showing the objects gone. Redact org names and ids before saving any of it as portfolio evidence (lesson 6).
