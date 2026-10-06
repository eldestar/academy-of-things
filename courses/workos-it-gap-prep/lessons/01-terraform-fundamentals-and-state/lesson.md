# Terraform fundamentals and state

You have configured Okta through the Admin Console for years, so every change lived in someone's memory and, at best, a ticket. The posting asks for Terraform "not just for cloud, but for identity and SaaS configuration". This lesson gives you the model underneath, so you can read a Terraform pull request, run the loop yourself, and talk credibly about state, which is where Terraform estates actually fail.

> Facts checked 2026-10-03 against developer.hashicorp.com, opentofu.org and the Terraform Registry. I give no Terraform version numbers unless a source did; run `terraform version` and read your own docs. Neither `terraform` nor `tofu` is installed in the authoring sandbox, so nothing here was executed.

## The model: config, state, reality

Terraform holds three things and reconciles them. Your **config** says what should exist. The **state** stores "bindings between objects in a remote system and resource instances declared in your configuration" (HashiCorp's wording). **Reality** is whatever the API returns. `terraform plan` reads the current remote objects, compares config to prior state, and proposes the actions that would make remote match config. `apply` then creates, updates in place, or destroys and recreates when the API cannot update in place. Anything in state but missing from config is destroyed.

That last sentence is the whole risk profile for identity work. Deleting an `okta_app_saml` block in a tidy-up PR is a request to delete the app in production, and the plan will say so. Reading the plan is the job.

```bash
terraform init                 # backend, modules, providers; safe to repeat, never deletes config or state
terraform fmt -check && terraform validate
terraform plan -out=tfplan     # -detailed-exitcode: 0 no diff, 1 error, 2 diff present
terraform apply tfplan         # a saved plan applies without prompting
```

> A saved plan file is as sensitive as state: HashiCorp notes sensitive values are written to it in cleartext even though the terminal hides them.

## HCL, providers and pinning

HCL is declarative blocks. Read references as `<type>.<name>.<attribute>`; Terraform builds the dependency graph from them, so you never sequence creates by hand.

```hcl
terraform {
  required_version = "~> 1.11"                  # example only: pin to what your CI runs
  required_providers {
    random = { source = "hashicorp/random", version = "~> 3.9" }
    local  = { source = "hashicorp/local",  version = "~> 2.9" }
  }
}
resource "random_pet" "name" {}
resource "local_file" "greeting" {
  filename = "${path.module}/greeting.txt"
  content  = "hello ${random_pet.name.id}"
}
```

A **provider** is the plugin that knows one API: `okta/okta`, `hashicorp/aws`. The `~>` operator lets only the right-most component rise: `~> 1.0.4` allows 1.0.5 but not 1.1.0, `~> 1.1` allows 1.10 but not 2.0. HashiCorp's guidance is that root modules use `~>` for both bounds, and reusable modules state only minimums. `init` writes `.terraform.lock.hcl`, recording the exact provider version chosen and checksums. Commit it so provider upgrades arrive as a reviewable diff; `terraform init -upgrade` deliberately re-selects the newest allowed version. `terraform providers lock` pre-records checksums for several platforms, which matters when laptops and CI runners differ.

## State: where it lives and what is in it

By default state is a local `terraform.tfstate` plus `.backup`. HashiCorp warns against keeping it in version control, or anywhere without locking and access control. A remote backend fixes sharing and locking. For S3:

```hcl
terraform {
  backend "s3" {
    bucket       = "example-tfstate-okta"       # placeholder
    key          = "okta/prod/terraform.tfstate"
    region       = "us-east-1"
    encrypt      = true
    use_lockfile = true                          # S3-native locking
  }
}
```

`use_lockfile` is the S3-native lock. DynamoDB locking (the older tutorial pattern, and what older course material teaches) is documented as deprecated and slated for removal in a future minor version; both can coexist while you migrate. Locking needs `s3:GetObject`, `s3:PutObject` and `s3:DeleteObject` on the `.tflock` object, and HashiCorp highly recommends bucket versioning for recovery. Backend blocks cannot reference variables, so inject per-environment values with `terraform init -backend-config=...`.

**State is plaintext.** The docs say that if you develop locally, Terraform "stores your state in a plaintext file, which includes any secret values you defined"; remote objects are still readable JSON. The docs also say `sensitive = true` only hides values in CLI output; they remain in state and plan files. Encrypting the bucket protects the disk, not anyone with read access to the object. Real mitigations are narrow read access to the state object, ephemeral values (Terraform 1.10 or later) and write-only arguments (1.11 or later), only where the provider supports them, and OpenTofu's state encryption. One more trap: `terraform_remote_state` gives a reader the full state snapshot, not just the outputs they were meant to see.

## Environments: workspaces versus separate states

CLI workspaces share one backend and one set of credentials. HashiCorp's own docs call them "not a suitable isolation mechanism" when deployments need different access controls. They suit a throwaway parallel copy for testing. Config is not the issue: you normally pass each workspace different input variables, and each workspace's state sits in the same configured backend (for the S3 example above, not on the runner). The lock file belongs to the working directory, so every workspace in it uses the same recorded provider versions. What workspaces cannot give you is separation of who may read and write each state. For Okta production versus preview, use separate directories, separate state keys or buckets, and separate CI credentials, so a mistake in preview cannot reach prod and a prod state reader is a short list.

## What a failed apply leaves behind

- **Partial apply.** Terraform logs the error, records the changes that completed, unlocks, and exits. It "does not automatically roll back". Fix the cause and apply again; the plan will show only what remains.
- **State write fails.** The change succeeded in the API but the backend rejected the write. Terraform saves `errored.tfstate` in the working directory. Recovery is `terraform state push errored.tfstate` (Terraform's own error message says so). HashiCorp only recommends `state push` when you must manually modify the remote state, and the error warns that running `apply` again first creates a forked state. Run `terraform state pull` first to keep a copy of what the backend holds (my advice, not HashiCorp's instruction). Push refuses a lower serial or a different lineage unless you force it, which is not recommended. In ephemeral CI, that file is gone with the runner, so versioning on the bucket is your safety net.
- **Stuck lock.** A killed job never released it. `terraform force-unlock LOCK_ID` removes the lock without touching infrastructure. HashiCorp says not to do it until you know why the lock is stuck; a second live apply is the real danger. Local state cannot be force-unlocked from another process.
- **Unmanage without destroying.** `terraform state rm` drops the binding and leaves the remote object, and HashiCorp prefers a `removed` block so the change goes through plan review. `lifecycle { prevent_destroy = true }` rejects destroy plans, but "doesn't prevent Terraform from destroying a resource if you remove its configuration".

## Terraform or OpenTofu

On 2023-08-10 HashiCorp moved its core products from MPL 2.0 to the Business Source License 1.1. Its position: end users may keep using the code commercially except to provide an offering competitive with HashiCorp. OpenTofu is the fork, started by Gruntwork, Spacelift, Harness, Env0, Scalr and others, now at the Linux Foundation, under MPL-2.0. It says the BUSL additional use grant is ambiguous, claims state compatibility up to Terraform 1.5.x, and ships state and plan encryption (AES-GCM, with KMS and other key providers). IBM announced its acquisition of HashiCorp on 2024-04-24 and completed it on 2025-02-27 (IBM's 10-Q for Q1 2025 and contemporaneous press agree; I read the press and search summaries, not the 10-Q body).

A company might choose Terraform for HCP Terraform and vendor support, or OpenTofu where legal dislikes BUSL ambiguity or wants built-in state encryption. For an internal IT team the competitive clause probably does not bite, but that is legal's call. The Okta provider repository itself is MPL-2.0. Interview answer: same HCL and providers, so ask what they run, and ask what each ships rather than assume parity; for example, OpenTofu's state and plan encryption has no Terraform equivalent.

## Your task

> Written from the docs, not run: `terraform` is not installed in the authoring sandbox. Install it or `tofu`, then run this yourself. For the Okta sandbox, see lesson 5 of the separate course `workos-test-environments`.

1. In an empty directory, write the config above plus `resource "random_password" "p" { length = 16 }` and a `local_sensitive_file` that writes `random_password.p.result`.
2. Run `init`, `plan -out=tfplan`, `apply tfplan`. Then `grep -A3 '"result"' terraform.tfstate` and find the password in plaintext.
3. Delete `greeting.txt` by hand and run `terraform plan -detailed-exitcode; echo $?`. Expect exit 2 and a recreate.
4. Open `.terraform.lock.hcl` and explain each field to yourself, then change a constraint and run `init -upgrade`.
5. Add `prevent_destroy = true` to the file resource, delete its block, and run `plan`. Write down what you saw and why.
