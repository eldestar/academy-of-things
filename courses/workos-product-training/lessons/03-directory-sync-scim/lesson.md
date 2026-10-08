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

<!-- diagram:scim-lifecycle -->
<div class="ds-wrap" style="position:relative">
<input type="checkbox" id="ds-pause" class="ds-cb" /><label for="ds-pause" class="ds-btn"><span class="ds-off">Pause animation</span><span class="ds-on">Play animation</span></label>
<div class="ds-box" style="overflow-x:auto">
<svg class="ds-flow" viewBox="0 0 760 803" role="img" aria-labelledby="ds-t ds-d" style="width:760px;max-width:100%;min-width:699px;height:auto;display:block;margin:0 auto">
<title id="ds-t">SCIM provisioning and deprovisioning through WorkOS</title>
<desc id="ds-d">The IdP provisions a user to WorkOS over SCIM, and WorkOS sends user and group events to the vendor app, which upserts them. When the admin deactivates the user, Okta sets active to false. In the default secure flow WorkOS sends dsync.user.deleted; in the custom flow it sends dsync.user.updated with an inactive state plus dsync.group.user_removed. The vendor must revoke sessions and offboard. A late retry of an older active update can resurrect the user unless the handler keeps a tombstone with the deprovision time. The diagram highlights each step in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
<style>
svg.ds-flow{--ink:light-dark(#000000,#ffffff)}
.ds-box{fill:var(--panel);stroke:var(--border-strong);stroke-width:1.5}
.ds-hot{fill:var(--panel);stroke:var(--accent);stroke-width:2.5}
.ds-ttl{fill:var(--ink);font:600 15px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.ds-sub{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.ds-life{stroke:var(--border-strong);stroke-width:1.5;stroke-dasharray:4 5}
.ds-front{stroke:var(--accent);stroke-width:2;fill:none}
.ds-back{stroke:var(--muted);stroke-width:2;stroke-dasharray:7 5;fill:none}
.ds-bad{stroke:var(--bad);stroke-width:2;fill:none}
.ds-main{fill:var(--ink);font:600 13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.ds-badt{fill:var(--ink)}
.ds-dim{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.ds-badge{fill:var(--accent)}
.ds-b-back{fill:var(--muted)}
.ds-b-bad{fill:var(--bad)}
.ds-b-good{fill:var(--good)}
.ds-bt{fill:var(--on-accent);font:700 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.ds-note{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.ds-note-good{fill:var(--good-bg);stroke:var(--good);stroke-width:1.5}
.ds-note-bad{fill:var(--bad-bg);stroke:var(--bad);stroke-width:1.5}
.ds-nt{fill:var(--ink);font:500 12.5px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.ds-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:44s;animation-timing-function:linear;animation-iteration-count:infinite}
.ds-pk.ds-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.ds-pk.ds-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.ds-wrap{margin:20px 0}
@media (min-width:801px){.ds-wrap{margin-left:-44px;margin-right:-44px}}
.ds-g rect,.ds-g line,.ds-g path:not(.ds-gl){opacity:.5;animation-duration:44s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.ds-flow:hover .ds-g rect,svg.ds-flow:hover .ds-g line,svg.ds-flow:hover .ds-g path:not(.ds-gl),svg.ds-flow:hover .ds-pk{animation-play-state:paused}
.ds-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.ds-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.ds-btn:hover{background:var(--hover)}
.ds-cb:focus-visible + .ds-btn{outline:2px solid var(--accent);outline-offset:2px}
.ds-cb:checked + .ds-btn .ds-off,.ds-cb:not(:checked) + .ds-btn .ds-on{display:none}
.ds-cb:checked ~ .ds-box .ds-g rect,.ds-cb:checked ~ .ds-box .ds-g line,.ds-cb:checked ~ .ds-box .ds-g path:not(.ds-gl),.ds-cb:checked ~ .ds-box .ds-pk{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.ds-g rect,.ds-g line,.ds-g path:not(.ds-gl){animation:none;opacity:1}.ds-pk{animation:none;display:none}.ds-btn{display:none}}
@keyframes ds-g0{0%{opacity:1}13.636%{opacity:1}13.646%,100%{opacity:.5}}
@keyframes ds-p0{0%,-0.01%{opacity:0;transform:translateX(0)}0%{opacity:1;transform:translateX(0)}10.909%{opacity:1;transform:translateX(236px)}13.636%{opacity:1;transform:translateX(236px)}13.646%,100%{opacity:0;transform:translateX(236px)}}
.ds-g0 rect,.ds-g0 line,.ds-g0 path:not(.ds-gl){animation-name:ds-g0}.ds-p0{animation-name:ds-p0}
@keyframes ds-g1{0%,13.626%{opacity:.5}13.636%{opacity:1}27.273%{opacity:1}27.283%,100%{opacity:.5}}
@keyframes ds-p1{0%,13.626%{opacity:0;transform:translateX(0)}13.636%{opacity:1;transform:translateX(0)}24.545%{opacity:1;transform:translateX(236px)}27.273%{opacity:1;transform:translateX(236px)}27.283%,100%{opacity:0;transform:translateX(236px)}}
.ds-g1 rect,.ds-g1 line,.ds-g1 path:not(.ds-gl){animation-name:ds-g1}.ds-p1{animation-name:ds-p1}
@keyframes ds-g2{0%,27.263%{opacity:.5}27.273%{opacity:1}40.909%{opacity:1}40.919%,100%{opacity:.5}}
@keyframes ds-p2{0%,27.263%{opacity:0;transform:translateX(0)}27.273%{opacity:1;transform:translateX(0)}38.182%{opacity:1;transform:translateX(236px)}40.909%{opacity:1;transform:translateX(236px)}40.919%,100%{opacity:0;transform:translateX(236px)}}
.ds-g2 rect,.ds-g2 line,.ds-g2 path:not(.ds-gl){animation-name:ds-g2}.ds-p2{animation-name:ds-p2}
@keyframes ds-g3{0%,40.899%{opacity:.5}40.909%{opacity:1}54.545%{opacity:1}54.555%,100%{opacity:.5}}
@keyframes ds-p3{0%,40.899%{opacity:0;transform:translateX(0)}40.909%{opacity:1;transform:translateX(0)}51.818%{opacity:1;transform:translateX(236px)}54.545%{opacity:1;transform:translateX(236px)}54.555%,100%{opacity:0;transform:translateX(236px)}}
.ds-g3 rect,.ds-g3 line,.ds-g3 path:not(.ds-gl){animation-name:ds-g3}.ds-p3{animation-name:ds-p3}
@keyframes ds-g4{0%,54.535%{opacity:.5}54.545%{opacity:1}68.182%{opacity:1}68.192%,100%{opacity:.5}}
@keyframes ds-p4{0%,54.535%{opacity:0;transform:translateX(0)}54.545%{opacity:1;transform:translateX(0)}65.455%{opacity:1;transform:translateX(236px)}68.182%{opacity:1;transform:translateX(236px)}68.192%,100%{opacity:0;transform:translateX(236px)}}
.ds-g4 rect,.ds-g4 line,.ds-g4 path:not(.ds-gl){animation-name:ds-g4}.ds-p4{animation-name:ds-p4}
@keyframes ds-g5{0%,68.172%{opacity:.5}68.182%{opacity:1}77.273%{opacity:1}77.283%,100%{opacity:.5}}
.ds-g5 rect,.ds-g5 line,.ds-g5 path:not(.ds-gl){animation-name:ds-g5}
@keyframes ds-g6{0%,77.263%{opacity:.5}77.273%{opacity:1}90.909%{opacity:1}90.919%,100%{opacity:.5}}
@keyframes ds-p6{0%,77.263%{opacity:0;transform:translateX(0)}77.273%{opacity:1;transform:translateX(0)}88.182%{opacity:1;transform:translateX(236px)}90.909%{opacity:1;transform:translateX(236px)}90.919%,100%{opacity:0;transform:translateX(236px)}}
.ds-g6 rect,.ds-g6 line,.ds-g6 path:not(.ds-gl){animation-name:ds-g6}.ds-p6{animation-name:ds-p6}
@keyframes ds-g7{0%,90.899%{opacity:.5}90.909%{opacity:1}100%{opacity:1}100.01%,100%{opacity:.5}}
.ds-g7 rect,.ds-g7 line,.ds-g7 path:not(.ds-gl){animation-name:ds-g7}
</style>
<defs>
<marker id="ds-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="ds-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="ds-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<line class="ds-life" x1="110" y1="72" x2="110" y2="751"/>
<line class="ds-life" x1="380" y1="72" x2="380" y2="751"/>
<line class="ds-life" x1="650" y1="72" x2="650" y2="751"/>
<rect class="ds-box" x="20" y="10" width="180" height="62" rx="10"/><text class="ds-ttl" x="110" y="36">Okta (any SCIM IdP)</text><text class="ds-sub" x="110" y="56">pushes, on its own schedule</text>
<rect class="ds-hot" x="290" y="10" width="180" height="62" rx="10"/><text class="ds-ttl" x="380" y="36">WorkOS</text><text class="ds-sub" x="380" y="56">the SCIM server, read-only API</text>
<rect class="ds-box" x="560" y="10" width="180" height="62" rx="10"/><text class="ds-ttl" x="650" y="36">Vendor app</text><text class="ds-sub" x="650" y="56">reads WorkOS, receives events</text>
<g class="ds-g ds-g0">
<text class="ds-main" x="245" y="108">SCIM provisions the user</text>
<text class="ds-dim" x="245" y="124">create user, push group</text>
<line class="ds-front" x1="124" y1="138" x2="366" y2="138" marker-end="url(#ds-m-front)"/>
<circle class="ds-badge ds-b-front" cx="110" cy="138" r="12"/><text class="ds-bt" x="110" y="142.5">1</text>
</g>
<g class="ds-g ds-g1">
<text class="ds-main" x="515" y="178">events: dsync.user.created</text>
<text class="ds-dim" x="515" y="194">dsync.group.user_added</text>
<line class="ds-front" x1="394" y1="208" x2="636" y2="208" marker-end="url(#ds-m-front)"/>
<circle class="ds-badge ds-b-front" cx="380" cy="208" r="12"/><text class="ds-bt" x="380" y="212.5">2</text>
<rect class="ds-note" x="549" y="226" width="201" height="31" rx="8"/>
<text class="ds-nt" x="650" y="247">upsert user and membership</text>
</g>
<g class="ds-g ds-g2">
<text class="ds-main" x="245" y="291">admin deactivates the user</text>
<text class="ds-dim" x="245" y="307">Okta sets active = false</text>
<line class="ds-front" x1="124" y1="321" x2="366" y2="321" marker-end="url(#ds-m-front)"/>
<circle class="ds-badge ds-b-front" cx="110" cy="321" r="12"/><text class="ds-bt" x="110" y="325.5">3</text>
</g>
<g class="ds-g ds-g3">
<text class="ds-main" x="515" y="361">secure flow (the default)</text>
<text class="ds-dim" x="515" y="377">dsync.user.deleted</text>
<line class="ds-front" x1="394" y1="391" x2="636" y2="391" marker-end="url(#ds-m-front)"/>
<circle class="ds-badge ds-b-front" cx="380" cy="391" r="12"/><text class="ds-bt" x="380" y="395.5">4a</text>
</g>
<g class="ds-g ds-g4">
<text class="ds-main" x="515" y="431">custom flow (via support)</text>
<text class="ds-dim" x="515" y="447">dsync.user.updated, inactive</text>
<text class="ds-dim" x="515" y="463">+ dsync.group.user_removed</text>
<line class="ds-front" x1="394" y1="477" x2="636" y2="477" marker-end="url(#ds-m-front)"/>
<circle class="ds-badge ds-b-front" cx="380" cy="477" r="12"/><text class="ds-bt" x="380" y="481.5">4b</text>
</g>
<g class="ds-g ds-g5">
<rect class="ds-note-good" x="522" y="511" width="228" height="48" rx="8"/>
<text class="ds-nt" x="636" y="532">revoke sessions, offboard</text>
<text class="ds-nt" x="636" y="549">SCIM never ends a live session</text>
<circle class="ds-badge ds-b-good" cx="522" cy="535" r="12"/><text class="ds-bt" x="522" y="539.5">5</text>
</g>
<g class="ds-g ds-g6">
<text class="ds-main ds-badt" x="515" y="593">a late retry arrives</text>
<text class="ds-dim" x="515" y="609">dsync.user.updated, state active</text>
<line class="ds-bad" x1="394" y1="623" x2="636" y2="623" marker-end="url(#ds-m-bad)"/>
<circle class="ds-badge ds-b-bad" cx="380" cy="623" r="12"/><text class="ds-bt" x="380" y="627.5">6</text>
</g>
<g class="ds-g ds-g7">
<rect class="ds-note-good" x="503" y="657" width="247" height="48" rx="8"/>
<text class="ds-nt" x="626" y="678">tombstone keeps the deprovision</text>
<text class="ds-nt" x="626" y="695">time, so the old event is skipped</text>
<circle class="ds-badge ds-b-good" cx="503" cy="681" r="12"/><text class="ds-bt" x="503" y="685.5">7</text>
</g>
<circle class="ds-pk ds-p0" cx="130" cy="138" r="5.5"/>
<circle class="ds-pk ds-p1" cx="400" cy="208" r="5.5"/>
<circle class="ds-pk ds-p2" cx="130" cy="321" r="5.5"/>
<circle class="ds-pk ds-p3" cx="400" cy="391" r="5.5"/>
<circle class="ds-pk ds-p4" cx="400" cy="477" r="5.5"/>
<circle class="ds-pk ds-p6 ds-pkbad" cx="400" cy="623" r="5.5"/>
<line class="ds-front" x1="40" y1="779" x2="70" y2="779"/>
<text class="ds-dim" x="78" y="783" style="text-anchor:start">normal event</text>
<line class="ds-bad" x1="188" y1="779" x2="218" y2="779"/>
<text class="ds-dim" x="226" y="783" style="text-anchor:start">failure mode</text>
<rect class="ds-note-good" x="336" y="771" width="22" height="16" rx="4"/>
<text class="ds-dim" x="366" y="783" style="text-anchor:start">what your handler must do</text>
</svg>
</div>
</div>
<!-- /diagram:scim-lifecycle -->

Read the diagram top to bottom: steps 1 and 2 are the easy half. Step 3 onwards is where the three event shapes come from. Steps 6 and 7 are the failure the task at the end reproduces.

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
