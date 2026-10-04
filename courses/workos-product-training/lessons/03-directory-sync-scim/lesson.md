# Directory Sync and SCIM

You know SCIM from the Okta side: a provisioning tab, Push Groups, and a ticket when a group does not land. In Directory Sync WorkOS is the receiving SCIM server, and the vendor's app reads WorkOS rather than speaking SCIM itself. Facts checked 2026-10-03 against the WorkOS docs, the OpenAPI spec (`v0.123.0`), RFC 7643 and RFC 7644, and Okta's developer docs. Where the docs disagree with each other or leave a gap, the text says so.

## Push or pull

WorkOS describes the Directory Sync API as read-only: it never mutates a customer's directory. Data arrives two ways.

- **SCIM providers push.** WorkOS gives the customer an endpoint plus either a bearer token (up to two active at a time, so rotate by generate, switch, revoke) or OAuth 2.0 client credentials (token URL, client ID and secret; the secret is shown once, and the docs state no limit on active secrets). The IdP's own schedule sets latency. WorkOS's Entra guide says about every 40 minutes by default, with "provision on demand" for single users.
- **Non-SCIM providers are pulled.** The directory `type` enum in the OpenAPI spec includes `gsuite directory`, `workday`, `hibob`, `bamboohr`, `sftp` and `s3` beside `okta scim v2.0`, `azure scim v2.0` and `generic scim v2.0`. WorkOS's guides say Google, Workday and HiBob sync roughly every 30 minutes; SFTP syncs on file change and every 30 minutes. A manual sync (`POST /directories/{id}/sync`) works only for Google Workspace, returns 202 when queued, and shares a five-minute cooldown (409 if running, 429 in cooldown, 503 if syncing is paused).

The vendor reads state through `GET /directories`, `/directory_users` and `/directory_groups` (filters such as `group` and `user`) and receives changes as events. Events versus webhooks is lesson 4.

## Objects and events

A **directory** has a `state` (`linked`, `validating`, `invalid_credentials`, `unlinked`, `deleting`). A **directory user** has `idp_id`, `email` (top-level `job_title`, `username` and `emails` were scheduled for removal on April 15, 2026, already past), `state`, `custom_attributes` and `role`/`roles` (group-to-role mapping works only for SCIM and Google directories). A **directory group** has `idp_id` and `name`.

The documented events are `dsync.activated`, `dsync.deleted`, `dsync.user.created`, `.updated`, `.deleted`, `dsync.group.created`, `.updated`, `.deleted`, `dsync.group.user_added` and `.user_removed`. Behaviours that bite:

- The first sync emits a `dsync.user.created` per existing user, usually followed by `group.created` and `group.user_added`. Entra sends a new user as two actions, so you also get an `updated` straight after the `created`.
- `updated` events carry a shallow `previous_attributes` diff.
- `dsync.deleted` is a single event; no per-user or per-group delete events follow it.
- When a group is deleted, `user_removed` events are not sent for its members. The docs say members "have been deleted in WorkOS" but do not say whether the users or only the memberships go. Test it before you build on it.

## Deprovisioning is three different events

The standards leave this to the provider. RFC 7643 defines `active` as the user's administrative status and says its meaning is up to the service provider. RFC 7644 lets a provider keep a deleted resource but requires 404s for it afterwards. Real IdPs differ:

- **Okta** deprovisioning sets `active=false` on the SCIM app; deleting an already-deactivated profile sends nothing more (Okta docs).
- **Entra**: a user deleted from the whole directory may be soft-deleted, and WorkOS reports state `suspended`. Reactivating does not restore group membership; the admin must choose Restart Provisioning.
- **WorkOS** says soft deletes arrive as `dsync.user.updated` with `state: inactive` (custom flow; the secure flow deletes instead), and hard deletes as `dsync.user.deleted`. Environments created after Oct. 19, 2023 delete users that move to inactive by default (the "secure flow"); support can enable a custom flow that keeps them, so a returning user keeps the same record.

So a safe handler treats `inactive` or `suspended` updates, `user.deleted` and `dsync.deleted` as offboarding. The Handle Inactive Users diagram shows the secure flow (default) emitting `dsync.user.deleted` and the custom flow emitting `dsync.user.updated` (inactive/suspended) plus `dsync.group.user_removed`. The diagram is an image and labels the event `dsync.user_deleted`; confirm in staging. Which one you get depends on the environment, so handle all of them. They also disagree on user states: the attributes page lists `active` and `inactive`, the OpenAPI spec lists `active`, `suspended` and `inactive`. Trust the spec, and confirm in staging.

SCIM versus SSO: SSO proves identity at login and, with JIT, creates users then. SCIM changes the directory whether or not anyone logs in. Neither kills a live session. WorkOS says Single Logout covers only OIDC "and limited scenarios", so the vendor must revoke sessions on the offboarding event. Inference: a user removed from the SCIM app but still assigned to the SAML app can still sign in and be recreated by JIT. Also confirm that a SAML profile's `idp_id` equals the directory user's `idp_id` in your tenant; the docs suggest the link but depend on how the IdP maps `id`.

## What the IdP admin sees

From WorkOS's guides (not run against my tenant). **Okta**: add "SCIM 2.0 Test App (OAuth Bearer Token)" from the catalog, then Provisioning, Configure API Integration, paste the SCIM 2.0 Base URL and token, Test API Credentials, and enable Create Users, Update User Attributes and Deactivate Users. Assign people, then Push Groups by name with Push Immediately. **Entra**: a non-gallery enterprise app, Provisioning set to Automatic, Tenant URL and Secret Token, Test Connection, map `objectId` to `externalId`, assign users and groups, status On with scope "Sync only assigned users and groups". **Google**: the admin signs in through the Admin Portal and picks which groups to sync; a user leaves the directory when removed from every selected group. Customers can follow these steps in the Admin Portal, whose setup links from the Dashboard expire in 30 days and whose API-generated links expire in 5 minutes.

## Where sync breaks

- **Okta group membership.** WorkOS documents an Okta bug: removals are not sent when the user is deactivated or unassigned, typically because one group is used for both assignment and push. Fix: Push now. Okta's own page says the same group cannot be used for assignment and Group Push; use a separate push group.
- **Username changes.** WorkOS identifies a user by SCIM username, and most providers re-provision a renamed user as new. Keep userName stable. Email and external ID must be unique per directory, or the update is declined and that user stops syncing (RFC 7643 also requires userName uniqueness).
- **Attribute gaps.** Entra may send no email unless `userPrincipalName` is mapped to `emails[type eq "work"].value`. Custom-attribute changes can take up to an hour and emit one `dsync.user.updated` per user.
- **Ordering and retries.** Webhooks carry no ordering guarantee, may repeat, and retry for up to 3 days; the Events API is ordered and replayable for 90 days. WorkOS also lists a known issue, under data reconciliation, that membership changes do not alter `updated_at`, so reconciling by timestamp is of limited use for memberships; compare memberships by state instead.
- **Stale reconciliation docs.** The recipe reads `groups` off each user, but that field is deprecated and empty by default for teams created from May 1, 2026. Use `GET /directory_groups?user=...`.
- **Rate limits.** Okta honours `Retry-After` on a 429, defaults to five minutes, doubles each retry and gives up after 10. WorkOS's pages I read give no SCIM endpoint limit, and Okta's Group Push page states no group-size limit. Treat both as unknown.

> **Not verified.** What group deletion does to users; WorkOS's SCIM rate limits; whether SAML and SCIM `idp_id` values match.

## Your task

Local, run on this machine (Python 3): this applier handles the documented event shapes. The core is below; the output is real except for the arrow note I added.

```python
# excerpt: users is a dict of id -> {updated_at}; drop(id, why) removes the user and logs why
def apply(e):
    ev, d = e["event"], e["data"]
    if ev in ("dsync.user.created", "dsync.user.updated"):
        u = users.get(d["id"])
        if u and u["updated_at"] > d["updated_at"]: return "skip stale"
        if d["state"] != "active": return drop(d["id"], "state=" + d["state"])
        users[d["id"]] = {"updated_at": d["updated_at"]}; return "upsert"
    if ev == "dsync.user.deleted": return drop(d["id"], "hard delete")
```

```text
dsync.group.user_added   member +
dsync.user.created       upsert
dsync.user.updated       skip stale
dsync.user.updated       deprovision state=inactive
dsync.user.updated       upsert        <- a late "active" retry resurrected the leaver
```

Fix the last line with a tombstone that keeps the deprovision time. Real-tenant part, written from the docs, not run against a live tenant: create a Directory Sync connection with Okta in staging, deactivate a test user, and record which event arrives in your environment.

Next: lesson 4 covers the Admin Portal, Audit Logs, events and webhook verification.
