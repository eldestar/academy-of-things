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

<!-- diagram:authz-groups -->
<div style="position:relative;margin:20px 0">
<input type="checkbox" id="l07b-pause" class="l07b-cb" /><label for="l07b-pause" class="l07b-btn"><span class="l07b-off">Pause animation</span><span class="l07b-on">Play animation</span></label>
<div class="l07b-box" style="overflow-x:auto">
<svg class="l07b-flow" viewBox="0 0 760 416" role="img" aria-labelledby="l07b-t l07b-d" style="width:100%;min-width:640px;max-width:800px;height:auto;display:block;margin:0 auto">
<title id="l07b-t">What a group hides: the rule, the app role and the token</title>
<desc id="l07b-d">A nested diagram of a group. The group is assigned to an app instead of assigning users one by one. A group rule fills it from attributes; a wrong HR department silently grants or removes access, and our inference is that the rule governs only the groups it targets, so direct assignments, app-local roles and API keys sit outside it. The group is assigned to an app with a role, and a group called Finance-Readers that holds the admin role inside an app grants more than its name says, so audit what it is assigned to and with which app role. Entra recommends assigning groups to app roles so the token carries a roles claim, with a baseline role that has no elevated rights. In an Entra token, groups are capped at 200 for a JWT, 150 for SAML and 6 for the implicit flow; beyond the cap there is no groups claim, only an overage indicator, and the app must call Microsoft Graph. A group used for a new purpose is a trigger to re-review it. The diagram highlights each part in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
<style>
.l07b-box{fill:var(--panel);stroke:var(--border-strong);stroke-width:1.5}
.l07b-hot{fill:var(--panel);stroke:var(--accent);stroke-width:2.5}
.l07b-ttl{fill:var(--text);font:600 15px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l07b-sub{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l07b-life{stroke:var(--border-strong);stroke-width:1.5;stroke-dasharray:4 5}
.l07b-front{stroke:var(--accent);stroke-width:2;fill:none}
.l07b-back{stroke:var(--muted);stroke-width:2;stroke-dasharray:7 5;fill:none}
.l07b-bad{stroke:var(--bad);stroke-width:2;fill:none}
.l07b-main{fill:var(--text);font:600 13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l07b-badt{fill:var(--bad-text)}
.l07b-dim{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l07b-badge{fill:var(--accent)}
.l07b-b-back{fill:var(--muted)}
.l07b-b-bad{fill:var(--bad)}
.l07b-b-good{fill:var(--good)}
.l07b-bt{fill:var(--on-accent);font:700 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l07b-note{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l07b-note-good{fill:var(--good-bg);stroke:var(--good);stroke-width:1.5}
.l07b-note-bad{fill:var(--bad-bg);stroke:var(--bad);stroke-width:1.5}
.l07b-nt{fill:var(--body);font:12.5px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l07b-nest{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l07b-row{fill:var(--raised);stroke:var(--border-strong);stroke-width:1}
.l07b-ttlL{fill:var(--text);font:600 14px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l07b-subL{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l07b-dimL{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l07b-dimR{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:end}
.l07b-conn{stroke:var(--accent);stroke-width:1.5;fill:none}
.l07b-edge{stroke:var(--border-strong);stroke-width:1.75;fill:none}
.l07b-hl{fill:none;stroke:var(--accent);stroke-width:3}
.l07b-hle{stroke:var(--accent);stroke-width:3;fill:none}
.l07b-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:26s;animation-timing-function:linear;animation-iteration-count:infinite}
.l07b-pk.l07b-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.l07b-pk.l07b-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.l07b-g{opacity:.45;animation-duration:26s;animation-timing-function:linear;animation-iteration-count:infinite}
.l07b-h{opacity:0;animation-duration:26s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.l07b-flow:hover .l07b-g,svg.l07b-flow:hover .l07b-pk,svg.l07b-flow:hover .l07b-h{animation-play-state:paused}
.l07b-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.l07b-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.l07b-btn:hover{background:var(--hover)}
.l07b-cb:focus-visible + .l07b-btn{outline:2px solid var(--accent);outline-offset:2px}
.l07b-cb:checked + .l07b-btn .l07b-off,.l07b-cb:not(:checked) + .l07b-btn .l07b-on{display:none}
.l07b-cb:checked ~ .l07b-box .l07b-g,.l07b-cb:checked ~ .l07b-box .l07b-pk,.l07b-cb:checked ~ .l07b-box .l07b-h{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.l07b-g{animation:none;opacity:1}.l07b-pk{animation:none;display:none}.l07b-h{animation:none;opacity:0}.l07b-btn{display:none}}
@keyframes l07b-g0{0%{opacity:1}20%{opacity:1}20.01%,100%{opacity:.45}}
@keyframes l07b-h0{0%{opacity:1}20%{opacity:1}20.01%,100%{opacity:0}}
.l07b-g0{animation-name:l07b-g0}.l07b-h0{animation-name:l07b-h0}
@keyframes l07b-g1{0%,19.99%{opacity:.45}20%{opacity:1}40%{opacity:1}40.01%,100%{opacity:.45}}
@keyframes l07b-h1{0%,19.99%{opacity:0}20%{opacity:1}40%{opacity:1}40.01%,100%{opacity:0}}
.l07b-g1{animation-name:l07b-g1}.l07b-h1{animation-name:l07b-h1}
@keyframes l07b-g2{0%,39.99%{opacity:.45}40%{opacity:1}60%{opacity:1}60.01%,100%{opacity:.45}}
@keyframes l07b-h2{0%,39.99%{opacity:0}40%{opacity:1}60%{opacity:1}60.01%,100%{opacity:0}}
.l07b-g2{animation-name:l07b-g2}.l07b-h2{animation-name:l07b-h2}
@keyframes l07b-g3{0%,59.99%{opacity:.45}60%{opacity:1}80%{opacity:1}80.01%,100%{opacity:.45}}
@keyframes l07b-h3{0%,59.99%{opacity:0}60%{opacity:1}80%{opacity:1}80.01%,100%{opacity:0}}
.l07b-g3{animation-name:l07b-g3}.l07b-h3{animation-name:l07b-h3}
@keyframes l07b-g4{0%,79.99%{opacity:.45}80%{opacity:1}100%{opacity:1}100.01%,100%{opacity:.45}}
@keyframes l07b-h4{0%,79.99%{opacity:0}80%{opacity:1}100%{opacity:1}100.01%,100%{opacity:0}}
.l07b-g4{animation-name:l07b-g4}.l07b-h4{animation-name:l07b-h4}
</style>
<defs>
<marker id="l07b-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="l07b-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="l07b-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<rect class="l07b-box" x="14" y="16" width="440" height="270" rx="9"/><text class="l07b-ttlL" x="28" y="37">Group</text><text class="l07b-subL" x="28" y="54">e.g. Finance-Readers; assigned to an app, not user by user</text>
<rect class="l07b-nest" x="26" y="62" width="416" height="46" rx="9"/><text class="l07b-ttlL" x="40" y="83">Group rule</text><text class="l07b-subL" x="40" y="100">fills the group from attributes such as department</text>
<rect class="l07b-nest" x="26" y="116" width="416" height="104" rx="9"/><text class="l07b-ttlL" x="40" y="137">Assigned to an app</text><text class="l07b-subL" x="40" y="154">can hold an admin role in the app (our reading)</text>
<rect class="l07b-nest" x="38" y="162" width="392" height="46" rx="9"/><text class="l07b-ttlL" x="52" y="183">App role</text><text class="l07b-subL" x="52" y="200">token then carries a roles claim</text>
<rect class="l07b-nest" x="26" y="228" width="416" height="46" rx="9"/><text class="l07b-ttlL" x="40" y="249">Token claim</text><text class="l07b-subL" x="40" y="266">Entra caps: 200 JWT, 150 SAML, 6 implicit</text>
<g class="l07b-g l07b-g0">
<path class="l07b-conn" d="M454,33 L462,33 L462,34 L470,34" marker-end="url(#l07b-m-front)"/>
<rect class="l07b-note" x="484" y="10" width="262" height="48" rx="8"/>
<text class="l07b-nt" x="615" y="31">Used for a new purpose? Entra lists</text>
<text class="l07b-nt" x="615" y="48">that as a trigger to re-review it</text>
<circle class="l07b-badge l07b-b-front" cx="484" cy="34" r="12"/><text class="l07b-bt" x="484" y="38.5">1</text>
</g>
<g class="l07b-g l07b-g1">
<path class="l07b-conn" d="M442,79 L466,79 L466,100 L470,100" marker-end="url(#l07b-m-front)"/>
<rect class="l07b-note-bad" x="484" y="68" width="262" height="65" rx="8"/>
<text class="l07b-nt" x="615" y="89">A wrong HR department silently grants</text>
<text class="l07b-nt" x="615" y="106">or removes access. Our inference: it</text>
<text class="l07b-nt" x="615" y="123">governs only the groups it targets</text>
<circle class="l07b-badge l07b-b-bad" cx="484" cy="100" r="12"/><text class="l07b-bt" x="484" y="105.0">2</text>
</g>
<g class="l07b-g l07b-g2">
<path class="l07b-conn" d="M442,133 L470,133 L470,176 L470,176" marker-end="url(#l07b-m-front)"/>
<rect class="l07b-note-bad" x="484" y="143" width="262" height="65" rx="8"/>
<text class="l07b-nt" x="615" y="164">Name versus grant: audit what it is</text>
<text class="l07b-nt" x="615" y="181">assigned to, with which app role,</text>
<text class="l07b-nt" x="615" y="198">not its label</text>
<circle class="l07b-badge l07b-b-bad" cx="484" cy="176" r="12"/><text class="l07b-bt" x="484" y="180.0">3</text>
</g>
<g class="l07b-g l07b-g3">
<path class="l07b-conn" d="M430,179 L474,179 L474,250 L470,250" marker-end="url(#l07b-m-front)"/>
<rect class="l07b-note-good" x="484" y="218" width="262" height="65" rx="8"/>
<text class="l07b-nt" x="615" y="239">Entra's better mapping. Always define</text>
<text class="l07b-nt" x="615" y="256">a baseline role with no elevated</text>
<text class="l07b-nt" x="615" y="273">rights</text>
<circle class="l07b-badge l07b-b-good" cx="484" cy="250" r="12"/><text class="l07b-bt" x="484" y="255.0">4</text>
</g>
<g class="l07b-g l07b-g4">
<path class="l07b-conn" d="M442,245 L462,245 L462,326 L470,326" marker-end="url(#l07b-m-front)"/>
<rect class="l07b-note-bad" x="484" y="293" width="262" height="65" rx="8"/>
<text class="l07b-nt" x="615" y="314">Past the cap: no groups claim, only</text>
<text class="l07b-nt" x="615" y="331">an overage indicator; the app must</text>
<text class="l07b-nt" x="615" y="348">call Graph, not read it as no groups</text>
<circle class="l07b-badge l07b-b-bad" cx="484" cy="326" r="12"/><text class="l07b-bt" x="484" y="330.0">5</text>
</g>
<g class="l07b-h l07b-h0">
<rect class="l07b-hl" x="14" y="16" width="440" height="270" rx="9"/>
</g>
<g class="l07b-h l07b-h1">
<rect class="l07b-hl" x="26" y="62" width="416" height="46" rx="9"/>
</g>
<g class="l07b-h l07b-h2">
<rect class="l07b-hl" x="26" y="116" width="416" height="104" rx="9"/>
</g>
<g class="l07b-h l07b-h3">
<rect class="l07b-hl" x="38" y="162" width="392" height="46" rx="9"/>
</g>
<g class="l07b-h l07b-h4">
<rect class="l07b-hl" x="26" y="228" width="416" height="46" rx="9"/>
</g>
<rect class="l07b-note" x="40" y="384" width="22" height="16" rx="4"/>
<text class="l07b-dim" x="70" y="396" style="text-anchor:start">context</text>
<rect class="l07b-note-good" x="148" y="384" width="22" height="16" rx="4"/>
<text class="l07b-dim" x="178" y="396" style="text-anchor:start">what to do</text>
<rect class="l07b-note-bad" x="276" y="384" width="22" height="16" rx="4"/>
<text class="l07b-dim" x="306" y="396" style="text-anchor:start">where it goes wrong</text>
</svg>
</div>
</div>
<!-- /diagram:authz-groups -->

The numbers match the diagram, top to bottom. Parts 2 and 3 are where a group hides its real power (the rule's data and the role an app assignment carries), part 4 is the mapping Entra recommends, and part 5 is why a token cannot be trusted to list every group.

## Where the decision lives

There are three places: **IdP claims** (decided at token issue, trusted by the app), **app-side checks** (the app maps a claim or its own data to permissions) and a **policy engine**. In NIST's ABAC architecture the policy decision point (PDP) computes the decision, the policy enforcement point (PEP) enforces it, the policy information point (PIP) supplies attributes and the policy administration point (PAP) manages policy.

<!-- diagram:decision-places -->
<div style="position:relative;margin:20px 0">
<input type="checkbox" id="l07e-pause" class="l07e-cb" /><label for="l07e-pause" class="l07e-btn"><span class="l07e-off">Pause animation</span><span class="l07e-on">Play animation</span></label>
<div class="l07e-box" style="overflow-x:auto">
<svg class="l07e-flow" viewBox="0 0 760 286" role="img" aria-labelledby="l07e-t l07e-d" style="width:100%;min-width:640px;max-width:800px;height:auto;display:block;margin:0 auto">
<title id="l07e-t">The three places an authorization decision can live</title>
<desc id="l07e-d">A nested diagram. An authorization decision can live in three places. IdP claims are decided at token issue and trusted by the app, but group information in a token is current only when you receive the token. App-side checks map a claim or the app's own data to permissions. A policy engine follows NIST's ABAC architecture: the policy decision point computes the decision, the policy enforcement point enforces it, the policy information point supplies attributes and the policy administration point manages policy. The rule of thumb is to put coarse, slow-changing facts in claims and to make a live check before high-impact actions. The diagram highlights each part in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
<style>
.l07e-box{fill:var(--panel);stroke:var(--border-strong);stroke-width:1.5}
.l07e-hot{fill:var(--panel);stroke:var(--accent);stroke-width:2.5}
.l07e-ttl{fill:var(--text);font:600 15px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l07e-sub{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l07e-life{stroke:var(--border-strong);stroke-width:1.5;stroke-dasharray:4 5}
.l07e-front{stroke:var(--accent);stroke-width:2;fill:none}
.l07e-back{stroke:var(--muted);stroke-width:2;stroke-dasharray:7 5;fill:none}
.l07e-bad{stroke:var(--bad);stroke-width:2;fill:none}
.l07e-main{fill:var(--text);font:600 13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l07e-badt{fill:var(--bad-text)}
.l07e-dim{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l07e-badge{fill:var(--accent)}
.l07e-b-back{fill:var(--muted)}
.l07e-b-bad{fill:var(--bad)}
.l07e-b-good{fill:var(--good)}
.l07e-bt{fill:var(--on-accent);font:700 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l07e-note{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l07e-note-good{fill:var(--good-bg);stroke:var(--good);stroke-width:1.5}
.l07e-note-bad{fill:var(--bad-bg);stroke:var(--bad);stroke-width:1.5}
.l07e-nt{fill:var(--body);font:12.5px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l07e-nest{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l07e-row{fill:var(--raised);stroke:var(--border-strong);stroke-width:1}
.l07e-ttlL{fill:var(--text);font:600 14px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l07e-subL{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l07e-dimL{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l07e-dimR{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:end}
.l07e-conn{stroke:var(--accent);stroke-width:1.5;fill:none}
.l07e-edge{stroke:var(--border-strong);stroke-width:1.75;fill:none}
.l07e-hl{fill:none;stroke:var(--accent);stroke-width:3}
.l07e-hle{stroke:var(--accent);stroke-width:3;fill:none}
.l07e-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:18s;animation-timing-function:linear;animation-iteration-count:infinite}
.l07e-pk.l07e-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.l07e-pk.l07e-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.l07e-g{opacity:.45;animation-duration:18s;animation-timing-function:linear;animation-iteration-count:infinite}
.l07e-h{opacity:0;animation-duration:18s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.l07e-flow:hover .l07e-g,svg.l07e-flow:hover .l07e-pk,svg.l07e-flow:hover .l07e-h{animation-play-state:paused}
.l07e-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.l07e-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.l07e-btn:hover{background:var(--hover)}
.l07e-cb:focus-visible + .l07e-btn{outline:2px solid var(--accent);outline-offset:2px}
.l07e-cb:checked + .l07e-btn .l07e-off,.l07e-cb:not(:checked) + .l07e-btn .l07e-on{display:none}
.l07e-cb:checked ~ .l07e-box .l07e-g,.l07e-cb:checked ~ .l07e-box .l07e-pk,.l07e-cb:checked ~ .l07e-box .l07e-h{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.l07e-g{animation:none;opacity:1}.l07e-pk{animation:none;display:none}.l07e-h{animation:none;opacity:0}.l07e-btn{display:none}}
@keyframes l07e-g0{0%{opacity:1}33.333%{opacity:1}33.343%,100%{opacity:.45}}
@keyframes l07e-h0{0%{opacity:1}33.333%{opacity:1}33.343%,100%{opacity:0}}
.l07e-g0{animation-name:l07e-g0}.l07e-h0{animation-name:l07e-h0}
@keyframes l07e-g1{0%,33.323%{opacity:.45}33.333%{opacity:1}66.667%{opacity:1}66.677%,100%{opacity:.45}}
@keyframes l07e-h1{0%,33.323%{opacity:0}33.333%{opacity:1}66.667%{opacity:1}66.677%,100%{opacity:0}}
.l07e-g1{animation-name:l07e-g1}.l07e-h1{animation-name:l07e-h1}
@keyframes l07e-g2{0%,66.657%{opacity:.45}66.667%{opacity:1}100%{opacity:1}100.01%,100%{opacity:.45}}
@keyframes l07e-h2{0%,66.657%{opacity:0}66.667%{opacity:1}100%{opacity:1}100.01%,100%{opacity:0}}
.l07e-g2{animation-name:l07e-g2}.l07e-h2{animation-name:l07e-h2}
</style>
<defs>
<marker id="l07e-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="l07e-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="l07e-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<rect class="l07e-box" x="14" y="16" width="440" height="212" rx="9"/><text class="l07e-ttlL" x="28" y="37">An authorization decision</text><text class="l07e-subL" x="28" y="54">three places it can live</text>
<rect class="l07e-nest" x="26" y="62" width="416" height="46" rx="9"/><text class="l07e-ttlL" x="40" y="83">IdP claims</text><text class="l07e-subL" x="40" y="100">decided at token issue, trusted by the app</text>
<rect class="l07e-nest" x="26" y="116" width="416" height="46" rx="9"/><text class="l07e-ttlL" x="40" y="137">App-side checks</text><text class="l07e-subL" x="40" y="154">map a claim or the app's own data to permissions</text>
<rect class="l07e-nest" x="26" y="170" width="416" height="46" rx="9"/><text class="l07e-ttlL" x="40" y="191">Policy engine</text><text class="l07e-subL" x="40" y="208">in NIST's ABAC architecture</text>
<g class="l07e-g l07e-g0">
<path class="l07e-conn" d="M454,33 L462,33 L462,42 L470,42" marker-end="url(#l07e-m-front)"/>
<rect class="l07e-note-good" x="484" y="10" width="262" height="65" rx="8"/>
<text class="l07e-nt" x="615" y="31">Rule of thumb: coarse, slow-changing</text>
<text class="l07e-nt" x="615" y="48">facts in claims; a live check before</text>
<text class="l07e-nt" x="615" y="65">high-impact actions</text>
<circle class="l07e-badge l07e-b-good" cx="484" cy="42" r="12"/><text class="l07e-bt" x="484" y="47.0">1</text>
</g>
<g class="l07e-g l07e-g1">
<path class="l07e-conn" d="M442,79 L466,79 L466,109 L470,109" marker-end="url(#l07e-m-front)"/>
<rect class="l07e-note-bad" x="484" y="85" width="262" height="48" rx="8"/>
<text class="l07e-nt" x="615" y="106">Snapshot: group data is current only</text>
<text class="l07e-nt" x="615" y="123">when you receive the token</text>
<circle class="l07e-badge l07e-b-bad" cx="484" cy="109" r="12"/><text class="l07e-bt" x="484" y="113.5">2</text>
</g>
<g class="l07e-g l07e-g2">
<path class="l07e-conn" d="M442,187 L470,187 L470,187 L470,187" marker-end="url(#l07e-m-front)"/>
<rect class="l07e-note" x="484" y="154" width="262" height="65" rx="8"/>
<text class="l07e-nt" x="615" y="176">PDP computes the decision; PEP</text>
<text class="l07e-nt" x="615" y="192">enforces it; PIP supplies attributes;</text>
<text class="l07e-nt" x="615" y="210">PAP manages policy</text>
<circle class="l07e-badge l07e-b-front" cx="484" cy="187" r="12"/><text class="l07e-bt" x="484" y="191.5">3</text>
</g>
<g class="l07e-h l07e-h0">
<rect class="l07e-hl" x="14" y="16" width="440" height="212" rx="9"/>
</g>
<g class="l07e-h l07e-h1">
<rect class="l07e-hl" x="26" y="62" width="416" height="46" rx="9"/>
</g>
<g class="l07e-h l07e-h2">
<rect class="l07e-hl" x="26" y="170" width="416" height="46" rx="9"/>
</g>
<rect class="l07e-note" x="40" y="254" width="22" height="16" rx="4"/>
<text class="l07e-dim" x="70" y="266" style="text-anchor:start">the four NIST roles</text>
<rect class="l07e-note-good" x="225" y="254" width="22" height="16" rx="4"/>
<text class="l07e-dim" x="255" y="266" style="text-anchor:start">rule of thumb</text>
<rect class="l07e-note-bad" x="372" y="254" width="22" height="16" rx="4"/>
<text class="l07e-dim" x="402" y="266" style="text-anchor:start">where it goes wrong</text>
</svg>
</div>
</div>
<!-- /diagram:decision-places -->

The numbers match the diagram. Part 1 is the rule of thumb for choosing between the places, part 2 is the weakness of claims, and part 3 names the four roles in a policy engine.

Claims are snapshots. Microsoft states that group information in a token is current only when you receive the token, and that apps needing real-time membership should use Graph. Per Microsoft's CAE page, access tokens last about an hour by default (lesson 1: a random 60 to 90 minutes); with continuous access evaluation (CAE) they can last up to 28 hours, but critical events (user disabled or deleted, password reset, admin revoking all refresh tokens) are meant to take effect within about 15 minutes (Microsoft), and only by resource providers that subscribe to those events. Microsoft notes that group or Conditional Access changes can still take up to a day to reach its resource providers under CAE, and that "Revoke Session" applies them at once.

<!-- diagram:claims-freshness -->
<div style="position:relative;margin:20px 0">
<input type="checkbox" id="l07f-pause" class="l07f-cb" /><label for="l07f-pause" class="l07f-btn"><span class="l07f-off">Pause animation</span><span class="l07f-on">Play animation</span></label>
<div class="l07f-box" style="overflow-x:auto">
<svg class="l07f-flow" viewBox="0 0 760 506" role="img" aria-labelledby="l07f-t l07f-d" style="width:100%;min-width:640px;max-width:800px;height:auto;display:block;margin:0 auto">
<title id="l07f-t">Token lifetime and how fast a change reaches Microsoft's resource providers</title>
<desc id="l07f-d">A table of four timings from Microsoft, each with what it applies to. Access tokens last about an hour by default, and up to 28 hours with CAE. Critical events, such as a user being disabled or a password reset, are meant to take effect within about 15 minutes, and only by resource providers that subscribe to those events. Group or Conditional Access changes can still take up to a day to reach Microsoft's resource providers under CAE. Revoke Session applies those changes at once. The diagram highlights each row in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
<style>
.l07f-box{fill:var(--panel);stroke:var(--border-strong);stroke-width:1.5}
.l07f-hot{fill:var(--panel);stroke:var(--accent);stroke-width:2.5}
.l07f-ttl{fill:var(--text);font:600 15px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l07f-sub{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l07f-life{stroke:var(--border-strong);stroke-width:1.5;stroke-dasharray:4 5}
.l07f-front{stroke:var(--accent);stroke-width:2;fill:none}
.l07f-back{stroke:var(--muted);stroke-width:2;stroke-dasharray:7 5;fill:none}
.l07f-bad{stroke:var(--bad);stroke-width:2;fill:none}
.l07f-main{fill:var(--text);font:600 13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l07f-badt{fill:var(--bad-text)}
.l07f-dim{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l07f-badge{fill:var(--accent)}
.l07f-b-back{fill:var(--muted)}
.l07f-b-bad{fill:var(--bad)}
.l07f-b-good{fill:var(--good)}
.l07f-bt{fill:var(--on-accent);font:700 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l07f-note{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l07f-note-good{fill:var(--good-bg);stroke:var(--good);stroke-width:1.5}
.l07f-note-bad{fill:var(--bad-bg);stroke:var(--bad);stroke-width:1.5}
.l07f-nt{fill:var(--body);font:12.5px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l07f-nest{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l07f-row{fill:var(--raised);stroke:var(--border-strong);stroke-width:1}
.l07f-ttlL{fill:var(--text);font:600 14px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l07f-subL{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l07f-dimL{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l07f-dimR{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:end}
.l07f-conn{stroke:var(--accent);stroke-width:1.5;fill:none}
.l07f-edge{stroke:var(--border-strong);stroke-width:1.75;fill:none}
.l07f-hl{fill:none;stroke:var(--accent);stroke-width:3}
.l07f-hle{stroke:var(--accent);stroke-width:3;fill:none}
.l07f-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:18s;animation-timing-function:linear;animation-iteration-count:infinite}
.l07f-pk.l07f-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.l07f-pk.l07f-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.l07f-g{opacity:.45;animation-duration:18s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.l07f-flow:hover .l07f-g,svg.l07f-flow:hover .l07f-pk{animation-play-state:paused}
.l07f-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.l07f-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.l07f-btn:hover{background:var(--hover)}
.l07f-cb:focus-visible + .l07f-btn{outline:2px solid var(--accent);outline-offset:2px}
.l07f-cb:checked + .l07f-btn .l07f-off,.l07f-cb:not(:checked) + .l07f-btn .l07f-on{display:none}
.l07f-cb:checked ~ .l07f-box .l07f-g,.l07f-cb:checked ~ .l07f-box .l07f-pk{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.l07f-g{animation:none;opacity:1}.l07f-pk{animation:none;display:none}.l07f-btn{display:none}}
@keyframes l07f-g0{0%{opacity:1}25%{opacity:1}25.01%,100%{opacity:.45}}
.l07f-g0{animation-name:l07f-g0}
@keyframes l07f-g1{0%,24.99%{opacity:.45}25%{opacity:1}50%{opacity:1}50.01%,100%{opacity:.45}}
.l07f-g1{animation-name:l07f-g1}
@keyframes l07f-g2{0%,49.99%{opacity:.45}50%{opacity:1}75%{opacity:1}75.01%,100%{opacity:.45}}
.l07f-g2{animation-name:l07f-g2}
@keyframes l07f-g3{0%,74.99%{opacity:.45}75%{opacity:1}100%{opacity:1}100.01%,100%{opacity:.45}}
.l07f-g3{animation-name:l07f-g3}
</style>
<defs>
<marker id="l07f-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="l07f-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="l07f-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<rect class="l07f-box" x="240" y="10" width="247" height="62" rx="10"/><text class="l07f-ttl" x="364" y="36">How long</text><text class="l07f-sub" x="364" y="56"></text>
<rect class="l07f-box" x="495" y="10" width="247" height="62" rx="10"/><text class="l07f-ttl" x="618" y="36">Applies to</text><text class="l07f-sub" x="618" y="56"></text>
<g class="l07f-g l07f-g0">
<rect class="l07f-row" x="10" y="86" width="740" height="86" rx="8"/>
<text class="l07f-ttlL" x="24" y="112">Token lifetime</text>
<text class="l07f-nt" x="364" y="134">about an hour by default</text>
<text class="l07f-nt" x="364" y="149">up to 28 hours with CAE</text>
<text class="l07f-nt" x="618" y="134">access tokens</text>
</g>
<g class="l07f-g l07f-g1">
<rect class="l07f-row" x="10" y="180" width="740" height="86" rx="8"/>
<text class="l07f-ttlL" x="24" y="206">Critical event</text>
<text class="l07f-subL" x="24" y="224">user disabled, password reset</text>
<text class="l07f-nt" x="364" y="228">meant to take effect within</text>
<text class="l07f-nt" x="364" y="243">about 15 minutes (Microsoft)</text>
<text class="l07f-nt" x="618" y="228">only by resource providers that</text>
<text class="l07f-nt" x="618" y="243">subscribe to those events</text>
</g>
<g class="l07f-g l07f-g2">
<rect class="l07f-row" x="10" y="274" width="740" height="86" rx="8"/>
<text class="l07f-ttlL" x="24" y="300">Group or Conditional Access</text>
<text class="l07f-subL" x="24" y="318">change, under CAE</text>
<text class="l07f-nt" x="364" y="322">can still take up to a day</text>
<text class="l07f-nt" x="618" y="322">to reach Microsoft's</text>
<text class="l07f-nt" x="618" y="337">resource providers</text>
</g>
<g class="l07f-g l07f-g3">
<rect class="l07f-row" x="10" y="368" width="740" height="86" rx="8"/>
<text class="l07f-ttlL" x="24" y="394">Revoke Session</text>
<text class="l07f-nt" x="364" y="416">at once</text>
<text class="l07f-nt" x="618" y="416">applies the group or Conditional</text>
<text class="l07f-nt" x="618" y="431">Access changes</text>
</g>
</svg>
</div>
</div>
<!-- /diagram:claims-freshness -->

Each row is one timing from Microsoft and what it applies to. Critical events are meant to take effect quickly, but group and Conditional Access changes can still take up to a day, and Revoke Session applies them at once.

RFC 7009 section 3 spells out the trade-off. A self-contained token needs no call to the authorization server, so revocation needs extra backend work or short lifetimes. A handle token forces a lookup on every use. Introspection (RFC 7662) returns an `active` boolean. In Okta, revoking a refresh token revokes its access token, but revoking an access token does not revoke the refresh token.

Rule of thumb: put coarse, slow-changing facts in claims; make a live check before high-impact actions.

## Joiner, mover, leaver

Microsoft's lifecycle page says many organizations model three phases: a **joiner** enters the scope of needing access, a **mover** moves between boundaries that need different access (its example is Sales to Marketing), a **leaver** leaves that scope. It notes that joining could be automated from a system of record such as Workday; treating the HR event as the trigger for all three is the usual design, not Microsoft's rule. CIS Safeguard 6.1 asks for a documented, preferably automated process for granting access on new hire or role change; 6.2 asks for revoking it, "through disabling accounts immediately upon termination, rights revocation, or role change".

<!-- diagram:identity-lifecycle -->
<div style="position:relative;margin:20px 0">
<input type="checkbox" id="l07d-pause" class="l07d-cb" /><label for="l07d-pause" class="l07d-btn"><span class="l07d-off">Pause animation</span><span class="l07d-on">Play animation</span></label>
<div class="l07d-box" style="overflow-x:auto">
<svg class="l07d-flow" viewBox="0 0 760 227" role="img" aria-labelledby="l07d-t l07d-d" style="width:100%;min-width:640px;max-width:800px;height:auto;display:block;margin:0 auto">
<title id="l07d-t">Joiner, mover, leaver and what each phase needs</title>
<desc id="l07d-d">Three phases in order. A joiner enters the scope of needing access and gets birthright access: the baseline from attributes such as department and location, kept small. A mover moves between boundaries that need different access, such as Sales to Marketing; the quiet risk is that old access stays and privilege accumulates, so NIST SP 800-53 PS-5 requires reviewing the ongoing need on reassignment. A leaver leaves the scope, and every surface needs checking, not one status flipped. Treating the HR event as the trigger for all three is the usual design, not Microsoft's rule. The diagram highlights each stage in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
<style>
.l07d-box{fill:var(--panel);stroke:var(--border-strong);stroke-width:1.5}
.l07d-hot{fill:var(--panel);stroke:var(--accent);stroke-width:2.5}
.l07d-ttl{fill:var(--text);font:600 15px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l07d-sub{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l07d-life{stroke:var(--border-strong);stroke-width:1.5;stroke-dasharray:4 5}
.l07d-front{stroke:var(--accent);stroke-width:2;fill:none}
.l07d-back{stroke:var(--muted);stroke-width:2;stroke-dasharray:7 5;fill:none}
.l07d-bad{stroke:var(--bad);stroke-width:2;fill:none}
.l07d-main{fill:var(--text);font:600 13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l07d-badt{fill:var(--bad-text)}
.l07d-dim{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l07d-badge{fill:var(--accent)}
.l07d-b-back{fill:var(--muted)}
.l07d-b-bad{fill:var(--bad)}
.l07d-b-good{fill:var(--good)}
.l07d-bt{fill:var(--on-accent);font:700 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l07d-note{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l07d-note-good{fill:var(--good-bg);stroke:var(--good);stroke-width:1.5}
.l07d-note-bad{fill:var(--bad-bg);stroke:var(--bad);stroke-width:1.5}
.l07d-nt{fill:var(--body);font:12.5px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l07d-nest{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l07d-row{fill:var(--raised);stroke:var(--border-strong);stroke-width:1}
.l07d-ttlL{fill:var(--text);font:600 14px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l07d-subL{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l07d-dimL{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l07d-dimR{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:end}
.l07d-conn{stroke:var(--accent);stroke-width:1.5;fill:none}
.l07d-edge{stroke:var(--border-strong);stroke-width:1.75;fill:none}
.l07d-hl{fill:none;stroke:var(--accent);stroke-width:3}
.l07d-hle{stroke:var(--accent);stroke-width:3;fill:none}
.l07d-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:14s;animation-timing-function:linear;animation-iteration-count:infinite}
.l07d-pk.l07d-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.l07d-pk.l07d-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.l07d-g{opacity:.45;animation-duration:14s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.l07d-flow:hover .l07d-g,svg.l07d-flow:hover .l07d-pk{animation-play-state:paused}
.l07d-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.l07d-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.l07d-btn:hover{background:var(--hover)}
.l07d-cb:focus-visible + .l07d-btn{outline:2px solid var(--accent);outline-offset:2px}
.l07d-cb:checked + .l07d-btn .l07d-off,.l07d-cb:not(:checked) + .l07d-btn .l07d-on{display:none}
.l07d-cb:checked ~ .l07d-box .l07d-g,.l07d-cb:checked ~ .l07d-box .l07d-pk{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.l07d-g{animation:none;opacity:1}.l07d-pk{animation:none;display:none}.l07d-btn{display:none}}
@keyframes l07d-g0{0%{opacity:1}33.333%{opacity:1}33.343%,100%{opacity:.45}}
@keyframes l07d-p0{0%,-0.01%{opacity:0;transform:translateX(0)}0%{opacity:1;transform:translateX(0)}33.333%{opacity:1;transform:translateX(88px)}33.343%,100%{opacity:0;transform:translateX(88px)}}
.l07d-g0{animation-name:l07d-g0}.l07d-p0{animation-name:l07d-p0}
@keyframes l07d-g1{0%,33.323%{opacity:.45}33.333%{opacity:1}66.667%{opacity:1}66.677%,100%{opacity:.45}}
@keyframes l07d-p1{0%,33.323%{opacity:0;transform:translateX(0)}33.333%{opacity:1;transform:translateX(0)}66.667%{opacity:1;transform:translateX(88px)}66.677%,100%{opacity:0;transform:translateX(88px)}}
.l07d-g1{animation-name:l07d-g1}.l07d-p1{animation-name:l07d-p1}
@keyframes l07d-g2{0%,66.657%{opacity:.45}66.667%{opacity:1}100%{opacity:1}100.01%,100%{opacity:.45}}
.l07d-g2{animation-name:l07d-g2}
</style>
<defs>
<marker id="l07d-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="l07d-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="l07d-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<g class="l07d-g l07d-g0">
<rect class="l07d-box" x="14" y="40" width="171" height="127" rx="10"/>
<text class="l07d-ttl" x="99" y="67">Joiner</text>
<text class="l07d-sub" x="99" y="87">enters the scope</text>
<text class="l07d-nt" x="99" y="114">Birthright access:</text>
<text class="l07d-nt" x="99" y="131">baseline from attributes</text>
<text class="l07d-nt" x="99" y="148">(department, location)</text>
<text class="l07d-main" x="240" y="64">role change</text>
<line class="l07d-front" x1="193" y1="70" x2="287" y2="70" marker-end="url(#l07d-m-front)"/>
</g>
<g class="l07d-g l07d-g1">
<rect class="l07d-note-bad" x="295" y="40" width="171" height="127" rx="10"/>
<text class="l07d-ttl" x="380" y="67">Mover</text>
<text class="l07d-sub" x="380" y="87">e.g. Sales to Marketing</text>
<text class="l07d-nt" x="380" y="114">Quiet risk: old access</text>
<text class="l07d-nt" x="380" y="131">stays, so privilege</text>
<text class="l07d-nt" x="380" y="148">accumulates; PS-5 review</text>
<text class="l07d-main" x="520" y="64">leaves scope</text>
<line class="l07d-front" x1="473" y1="70" x2="567" y2="70" marker-end="url(#l07d-m-front)"/>
</g>
<g class="l07d-g l07d-g2">
<rect class="l07d-box" x="575" y="40" width="171" height="127" rx="10"/>
<text class="l07d-ttl" x="661" y="67">Leaver</text>
<text class="l07d-sub" x="661" y="87">leaves the scope</text>
<text class="l07d-nt" x="661" y="114">Check every surface,</text>
<text class="l07d-nt" x="661" y="131">not one status flipped</text>
</g>
<circle class="l07d-pk l07d-p0" cx="199" cy="70" r="5.5"/>
<circle class="l07d-pk l07d-p1" cx="479" cy="70" r="5.5"/>
<line class="l07d-front" x1="40" y1="203" x2="70" y2="203"/>
<text class="l07d-dim" x="78" y="207" style="text-anchor:start">role change or exit</text>
<rect class="l07d-note-bad" x="233" y="195" width="22" height="16" rx="4"/>
<text class="l07d-dim" x="263" y="207" style="text-anchor:start">quiet risk</text>
</svg>
</div>
</div>
<!-- /diagram:identity-lifecycle -->

Read left to right: the three phases in order, with what each one needs. Treating the HR event as the trigger for all three is the usual design, not Microsoft's rule.

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
