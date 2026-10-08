# Authorization and the identity lifecycle

You are designing or reviewing where authorization decisions live, how fresh their inputs are, and how access is removed when a person or workload goes away. The protocols from earlier lessons say who someone is; nothing in them keeps what they may do correct. Facts checked 2026-10-06 against the cited docs. Where a source is secondary, the text says so.

## Models at spec level, and their failure modes

NIST SP 800-162 defines ABAC as granting or denying requests "based on assigned attributes of the subject, assigned attributes of the object, environment conditions, and a set of policies". It frames ACLs and RBAC as "in some ways special cases": ACLs work on the attribute "identity", RBAC on "role"; the difference is policies as Boolean rules over many attributes. It adds that expressing ABAC needs through ACLs or RBAC makes demonstrating compliance "difficult and costly", and a changed requirement is hard to trace to every place that implements it. On ACLs it warns that failure to remove access over time "leads to users accumulating privileges". Its reference architecture has a PEP (enforces), PDP (computes the decision), PIP (retrieves attributes) and PAP (creates, manages, tests and debugs policy). A subject may be a human or a non-person entity (NPE).

The NIST RBAC model behind INCITS 359 has core RBAC (many-to-many user-role and permission-role assignment, users may exercise several roles at once), optional hierarchies, and two separation-of-duty relations. In the 2001 NIST RBAC paper (Ferraiolo et al., ACM TISSEC 4(3), section 2.2) a hierarchy is a seniority partial order in which senior roles acquire the permissions of their juniors: it is inheritance, and it does not limit which roles one person may combine. A role is **active** when the user has activated it in a session: a session activates some subset of the roles the user is assigned. **Static** SoD is a pair (role set, n): no user is assigned n or more roles from the set. **Dynamic** SoD instead constrains which roles may be active within or across a user's sessions. Example: staff who cover for each other may be assigned both invoice-creator and invoice-approver, but never have both active together. With hierarchies, static constraints must count inherited roles as well.

<!-- diagram:sod-roles -->
<div class="l07g-wrap" style="position:relative">
<input type="checkbox" id="l07g-pause" class="l07g-cb" /><label for="l07g-pause" class="l07g-btn"><span class="l07g-off">Pause animation</span><span class="l07g-on">Play animation</span></label>
<div class="l07g-box" style="overflow-x:auto">
<svg class="l07g-flow" viewBox="0 0 760 377" role="img" aria-labelledby="l07g-t l07g-d" style="width:760px;max-width:100%;min-width:699px;height:auto;display:block;margin:0 auto">
<title id="l07g-t">Separation of duty in NIST RBAC: assigned roles versus active roles</title>
<desc id="l07g-d">A nested diagram. A user is assigned roles; staff who cover for each other may hold both invoice-creator and invoice-approver. Static separation of duty is a pair of a role set and n: no user is assigned n or more roles from the set. With role hierarchies, in which senior roles acquire the permissions of their juniors, static constraints must count inherited roles as well. A session activates some subset of the assigned roles. Dynamic separation of duty constrains which roles may be active within or across a user's sessions. A role is active when the user has activated it in a session, so in the example both roles are assigned but never both active together. The diagram highlights each part in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
<style>
svg.l07g-flow{--ink:light-dark(#000000,#ffffff)}
.l07g-box{fill:var(--panel);stroke:var(--border-strong);stroke-width:1.5}
.l07g-hot{fill:var(--panel);stroke:var(--accent);stroke-width:2.5}
.l07g-ttl{fill:var(--ink);font:600 15px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l07g-sub{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l07g-life{stroke:var(--border-strong);stroke-width:1.5;stroke-dasharray:4 5}
.l07g-front{stroke:var(--accent);stroke-width:2;fill:none}
.l07g-back{stroke:var(--muted);stroke-width:2;stroke-dasharray:7 5;fill:none}
.l07g-bad{stroke:var(--bad);stroke-width:2;fill:none}
.l07g-main{fill:var(--ink);font:600 13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l07g-badt{fill:var(--ink)}
.l07g-dim{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l07g-badge{fill:var(--accent)}
.l07g-b-back{fill:var(--muted)}
.l07g-b-bad{fill:var(--bad)}
.l07g-b-good{fill:var(--good)}
.l07g-bt{fill:var(--on-accent);font:700 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l07g-note{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l07g-note-good{fill:var(--good-bg);stroke:var(--good);stroke-width:1.5}
.l07g-note-bad{fill:var(--bad-bg);stroke:var(--bad);stroke-width:1.5}
.l07g-nt{fill:var(--ink);font:500 12.5px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l07g-nest{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l07g-row{fill:var(--raised);stroke:var(--border-strong);stroke-width:1}
.l07g-ttlL{fill:var(--ink);font:600 14px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l07g-subL{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l07g-dimL{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l07g-dimR{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:end}
.l07g-conn{stroke:var(--accent);stroke-width:1.5;fill:none}
.l07g-edge{stroke:var(--border-strong);stroke-width:1.75;fill:none}
.l07g-hl{fill:none;stroke:var(--accent);stroke-width:3}
.l07g-hle{stroke:var(--accent);stroke-width:3;fill:none}
.l07g-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:24s;animation-timing-function:linear;animation-iteration-count:infinite}
.l07g-pk.l07g-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.l07g-pk.l07g-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.l07g-wrap{margin:20px 0}
@media (min-width:801px){.l07g-wrap{margin-left:-44px;margin-right:-44px}}
.l07g-g rect,.l07g-g line,.l07g-g path:not(.l07g-gl){opacity:.5;animation-duration:24s;animation-timing-function:linear;animation-iteration-count:infinite}
.l07g-h{opacity:0;animation-duration:24s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.l07g-flow:hover .l07g-g rect,svg.l07g-flow:hover .l07g-g line,svg.l07g-flow:hover .l07g-g path:not(.l07g-gl),svg.l07g-flow:hover .l07g-pk,svg.l07g-flow:hover .l07g-h{animation-play-state:paused}
.l07g-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.l07g-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.l07g-btn:hover{background:var(--hover)}
.l07g-cb:focus-visible + .l07g-btn{outline:2px solid var(--accent);outline-offset:2px}
.l07g-cb:checked + .l07g-btn .l07g-off,.l07g-cb:not(:checked) + .l07g-btn .l07g-on{display:none}
.l07g-cb:checked ~ .l07g-box .l07g-g rect,.l07g-cb:checked ~ .l07g-box .l07g-g line,.l07g-cb:checked ~ .l07g-box .l07g-g path:not(.l07g-gl),.l07g-cb:checked ~ .l07g-box .l07g-pk,.l07g-cb:checked ~ .l07g-box .l07g-h{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.l07g-g rect,.l07g-g line,.l07g-g path:not(.l07g-gl){animation:none;opacity:1}.l07g-pk{animation:none;display:none}.l07g-h{animation:none;opacity:0}.l07g-btn{display:none}}
@keyframes l07g-g0{0%{opacity:1}25%{opacity:1}25.01%,100%{opacity:.5}}
@keyframes l07g-h0{0%{opacity:1}25%{opacity:1}25.01%,100%{opacity:0}}
.l07g-g0 rect,.l07g-g0 line,.l07g-g0 path:not(.l07g-gl){animation-name:l07g-g0}.l07g-h0{animation-name:l07g-h0}
@keyframes l07g-g1{0%,24.99%{opacity:.5}25%{opacity:1}50%{opacity:1}50.01%,100%{opacity:.5}}
@keyframes l07g-h1{0%,24.99%{opacity:0}25%{opacity:1}50%{opacity:1}50.01%,100%{opacity:0}}
.l07g-g1 rect,.l07g-g1 line,.l07g-g1 path:not(.l07g-gl){animation-name:l07g-g1}.l07g-h1{animation-name:l07g-h1}
@keyframes l07g-g2{0%,49.99%{opacity:.5}50%{opacity:1}75%{opacity:1}75.01%,100%{opacity:.5}}
@keyframes l07g-h2{0%,49.99%{opacity:0}50%{opacity:1}75%{opacity:1}75.01%,100%{opacity:0}}
.l07g-g2 rect,.l07g-g2 line,.l07g-g2 path:not(.l07g-gl){animation-name:l07g-g2}.l07g-h2{animation-name:l07g-h2}
@keyframes l07g-g3{0%,74.99%{opacity:.5}75%{opacity:1}100%{opacity:1}100.01%,100%{opacity:.5}}
@keyframes l07g-h3{0%,74.99%{opacity:0}75%{opacity:1}100%{opacity:1}100.01%,100%{opacity:0}}
.l07g-g3 rect,.l07g-g3 line,.l07g-g3 path:not(.l07g-gl){animation-name:l07g-g3}.l07g-h3{animation-name:l07g-h3}
</style>
<defs>
<marker id="l07g-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="l07g-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="l07g-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<rect class="l07g-box" x="14" y="16" width="440" height="274" rx="9"/><text class="l07g-ttlL" x="28" y="37">User</text><text class="l07g-subL" x="28" y="54">staff who cover for each other (the example)</text>
<rect class="l07g-nest" x="26" y="62" width="416" height="104" rx="9"/><text class="l07g-ttlL" x="40" y="83">Assigned roles</text><text class="l07g-subL" x="40" y="100">may hold both invoice-creator and invoice-approver</text>
<rect class="l07g-nest" x="38" y="108" width="392" height="46" rx="9"/><text class="l07g-ttlL" x="52" y="129">Inherited roles</text><text class="l07g-subL" x="52" y="146">seniors acquire juniors' permissions</text>
<rect class="l07g-nest" x="26" y="174" width="416" height="104" rx="9"/><text class="l07g-ttlL" x="40" y="195">Session</text><text class="l07g-subL" x="40" y="212">activates some subset of the assigned roles</text>
<rect class="l07g-nest" x="38" y="220" width="392" height="46" rx="9"/><text class="l07g-ttlL" x="52" y="241">Active roles</text><text class="l07g-subL" x="52" y="258">in the example: never both active</text>
<g class="l07g-g l07g-g0">
<path class="l07g-conn" d="M442,79 L462,79 L462,79 L470,79" marker-end="url(#l07g-m-front)"/>
<rect class="l07g-note-good" x="484" y="46" width="262" height="65" rx="8"/>
<text class="l07g-nt" x="615" y="68">Static SoD is a pair (role set, n):</text>
<text class="l07g-nt" x="615" y="84">no user is assigned n or more</text>
<text class="l07g-nt" x="615" y="102">roles from the set</text>
<circle class="l07g-badge l07g-b-good" cx="484" cy="79" r="12"/><text class="l07g-bt" x="484" y="83.5">1</text>
</g>
<g class="l07g-g l07g-g1">
<path class="l07g-conn" d="M430,125 L466,125 L466,146 L470,146" marker-end="url(#l07g-m-front)"/>
<rect class="l07g-note-good" x="484" y="122" width="262" height="48" rx="8"/>
<text class="l07g-nt" x="615" y="142">With hierarchies, static constraints</text>
<text class="l07g-nt" x="615" y="160">must count inherited roles as well</text>
<circle class="l07g-badge l07g-b-good" cx="484" cy="146" r="12"/><text class="l07g-bt" x="484" y="150.0">2</text>
</g>
<g class="l07g-g l07g-g2">
<path class="l07g-conn" d="M442,191 L470,191 L470,212 L470,212" marker-end="url(#l07g-m-front)"/>
<rect class="l07g-note-good" x="484" y="180" width="262" height="65" rx="8"/>
<text class="l07g-nt" x="615" y="200">Dynamic SoD constrains which roles</text>
<text class="l07g-nt" x="615" y="218">may be active within or across a</text>
<text class="l07g-nt" x="615" y="234">user's sessions</text>
<circle class="l07g-badge l07g-b-good" cx="484" cy="212" r="12"/><text class="l07g-bt" x="484" y="216.5">3</text>
</g>
<g class="l07g-g l07g-g3">
<path class="l07g-conn" d="M430,237 L474,237 L474,287 L470,287" marker-end="url(#l07g-m-front)"/>
<rect class="l07g-note" x="484" y="254" width="262" height="65" rx="8"/>
<text class="l07g-nt" x="615" y="276">A role is active when the user has</text>
<text class="l07g-nt" x="615" y="292">activated it in a session. Example:</text>
<text class="l07g-nt" x="615" y="310">both assigned, never both active</text>
<circle class="l07g-badge l07g-b-front" cx="484" cy="287" r="12"/><text class="l07g-bt" x="484" y="291.5">4</text>
</g>
<g class="l07g-h l07g-h0">
<rect class="l07g-hl" x="26" y="62" width="416" height="104" rx="9"/>
</g>
<g class="l07g-h l07g-h1">
<rect class="l07g-hl" x="38" y="108" width="392" height="46" rx="9"/>
</g>
<g class="l07g-h l07g-h2">
<rect class="l07g-hl" x="26" y="174" width="416" height="104" rx="9"/>
</g>
<g class="l07g-h l07g-h3">
<rect class="l07g-hl" x="38" y="220" width="392" height="46" rx="9"/>
</g>
<rect class="l07g-note" x="40" y="345" width="22" height="16" rx="4"/>
<text class="l07g-dim" x="70" y="357" style="text-anchor:start">what it means</text>
<rect class="l07g-note-good" x="187" y="345" width="22" height="16" rx="4"/>
<text class="l07g-dim" x="217" y="357" style="text-anchor:start">what a constraint limits</text>
</svg>
</div>
</div>
<!-- /diagram:sod-roles -->

Read top to bottom. The numbers match the diagram: callouts 1 and 2 are about what is assigned (static constraints), and callouts 3 and 4 are about what is active in a session (dynamic constraints).

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

<!-- diagram:new-enemy -->
<div class="l07h-wrap" style="position:relative">
<input type="checkbox" id="l07h-pause" class="l07h-cb" /><label for="l07h-pause" class="l07h-btn"><span class="l07h-off">Pause animation</span><span class="l07h-on">Play animation</span></label>
<div class="l07h-box" style="overflow-x:auto">
<svg class="l07h-flow" viewBox="0 0 760 616" role="img" aria-labelledby="l07h-t l07h-d" style="width:760px;max-width:100%;min-width:699px;height:auto;display:block;margin:0 auto">
<title id="l07h-t">Zanzibar's new enemy problem and the zookie</title>
<desc id="l07h-d">Two parties: a client and Zanzibar, the ACL store. Bob is removed from the ACL. The new enemy problem is applying a stale ACL to new content, so Bob still reads it. The client requests an opaque zookie token for the new content version and stores it with that version. With the zookie, a check on that content is evaluated on ACL data no older than that version, using external consistency. The diagram highlights each step in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
<style>
svg.l07h-flow{--ink:light-dark(#000000,#ffffff)}
.l07h-box{fill:var(--panel);stroke:var(--border-strong);stroke-width:1.5}
.l07h-hot{fill:var(--panel);stroke:var(--accent);stroke-width:2.5}
.l07h-ttl{fill:var(--ink);font:600 15px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l07h-sub{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l07h-life{stroke:var(--border-strong);stroke-width:1.5;stroke-dasharray:4 5}
.l07h-front{stroke:var(--accent);stroke-width:2;fill:none}
.l07h-back{stroke:var(--muted);stroke-width:2;stroke-dasharray:7 5;fill:none}
.l07h-bad{stroke:var(--bad);stroke-width:2;fill:none}
.l07h-main{fill:var(--ink);font:600 13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l07h-badt{fill:var(--ink)}
.l07h-dim{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l07h-badge{fill:var(--accent)}
.l07h-b-back{fill:var(--muted)}
.l07h-b-bad{fill:var(--bad)}
.l07h-b-good{fill:var(--good)}
.l07h-bt{fill:var(--on-accent);font:700 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l07h-note{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l07h-note-good{fill:var(--good-bg);stroke:var(--good);stroke-width:1.5}
.l07h-note-bad{fill:var(--bad-bg);stroke:var(--bad);stroke-width:1.5}
.l07h-nt{fill:var(--ink);font:500 12.5px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l07h-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:28s;animation-timing-function:linear;animation-iteration-count:infinite}
.l07h-pk.l07h-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.l07h-pk.l07h-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.l07h-wrap{margin:20px 0}
@media (min-width:801px){.l07h-wrap{margin-left:-44px;margin-right:-44px}}
.l07h-g rect,.l07h-g line,.l07h-g path:not(.l07h-gl){opacity:.5;animation-duration:28s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.l07h-flow:hover .l07h-g rect,svg.l07h-flow:hover .l07h-g line,svg.l07h-flow:hover .l07h-g path:not(.l07h-gl),svg.l07h-flow:hover .l07h-pk{animation-play-state:paused}
.l07h-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.l07h-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.l07h-btn:hover{background:var(--hover)}
.l07h-cb:focus-visible + .l07h-btn{outline:2px solid var(--accent);outline-offset:2px}
.l07h-cb:checked + .l07h-btn .l07h-off,.l07h-cb:not(:checked) + .l07h-btn .l07h-on{display:none}
.l07h-cb:checked ~ .l07h-box .l07h-g rect,.l07h-cb:checked ~ .l07h-box .l07h-g line,.l07h-cb:checked ~ .l07h-box .l07h-g path:not(.l07h-gl),.l07h-cb:checked ~ .l07h-box .l07h-pk{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.l07h-g rect,.l07h-g line,.l07h-g path:not(.l07h-gl){animation:none;opacity:1}.l07h-pk{animation:none;display:none}.l07h-btn{display:none}}
@keyframes l07h-g0{0%{opacity:1}14.286%{opacity:1}14.296%,100%{opacity:.5}}
.l07h-g0 rect,.l07h-g0 line,.l07h-g0 path:not(.l07h-gl){animation-name:l07h-g0}
@keyframes l07h-g1{0%,14.276%{opacity:.5}14.286%{opacity:1}28.571%{opacity:1}28.581%,100%{opacity:.5}}
.l07h-g1 rect,.l07h-g1 line,.l07h-g1 path:not(.l07h-gl){animation-name:l07h-g1}
@keyframes l07h-g2{0%,28.561%{opacity:.5}28.571%{opacity:1}50%{opacity:1}50.01%,100%{opacity:.5}}
@keyframes l07h-p2{0%,28.561%{opacity:0;transform:translateX(0)}28.571%{opacity:1;transform:translateX(0)}45.714%{opacity:1;transform:translateX(506px)}50%{opacity:1;transform:translateX(506px)}50.01%,100%{opacity:0;transform:translateX(506px)}}
.l07h-g2 rect,.l07h-g2 line,.l07h-g2 path:not(.l07h-gl){animation-name:l07h-g2}.l07h-p2{animation-name:l07h-p2}
@keyframes l07h-g3{0%,49.99%{opacity:.5}50%{opacity:1}64.286%{opacity:1}64.296%,100%{opacity:.5}}
.l07h-g3 rect,.l07h-g3 line,.l07h-g3 path:not(.l07h-gl){animation-name:l07h-g3}
@keyframes l07h-g4{0%,64.276%{opacity:.5}64.286%{opacity:1}85.714%{opacity:1}85.724%,100%{opacity:.5}}
@keyframes l07h-p4{0%,64.276%{opacity:0;transform:translateX(0)}64.286%{opacity:1;transform:translateX(0)}81.429%{opacity:1;transform:translateX(506px)}85.714%{opacity:1;transform:translateX(506px)}85.724%,100%{opacity:0;transform:translateX(506px)}}
.l07h-g4 rect,.l07h-g4 line,.l07h-g4 path:not(.l07h-gl){animation-name:l07h-g4}.l07h-p4{animation-name:l07h-p4}
@keyframes l07h-g5{0%,85.704%{opacity:.5}85.714%{opacity:1}100%{opacity:1}100.01%,100%{opacity:.5}}
.l07h-g5 rect,.l07h-g5 line,.l07h-g5 path:not(.l07h-gl){animation-name:l07h-g5}
</style>
<defs>
<marker id="l07h-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="l07h-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="l07h-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<line class="l07h-life" x1="110" y1="72" x2="110" y2="564"/>
<line class="l07h-life" x1="650" y1="72" x2="650" y2="564"/>
<rect class="l07h-box" x="20" y="10" width="180" height="62" rx="10"/><text class="l07h-ttl" x="110" y="36">Client</text><text class="l07h-sub" x="110" y="56">zookie kept with each version</text>
<rect class="l07h-hot" x="560" y="10" width="180" height="62" rx="10"/><text class="l07h-ttl" x="650" y="36">Zanzibar</text><text class="l07h-sub" x="650" y="56">the ACL store</text>
<g class="l07h-g l07h-g0">
<rect class="l07h-note" x="542" y="102" width="208" height="31" rx="8"/>
<text class="l07h-nt" x="646" y="123">Bob is removed from the ACL</text>
<circle class="l07h-badge l07h-b-plain" cx="542" cy="118" r="12"/><text class="l07h-bt" x="542" y="122.0">1</text>
</g>
<g class="l07h-g l07h-g1">
<rect class="l07h-note-bad" x="496" y="161" width="254" height="65" rx="8"/>
<text class="l07h-nt" x="623" y="182">The new enemy problem: a stale ACL</text>
<text class="l07h-nt" x="623" y="199">applied to new content, so Bob</text>
<text class="l07h-nt" x="623" y="216">still reads it</text>
<circle class="l07h-badge l07h-b-bad" cx="496" cy="194" r="12"/><text class="l07h-bt" x="496" y="198.0">2</text>
</g>
<g class="l07h-g l07h-g2">
<text class="l07h-main" x="380" y="260">Client requests a zookie</text>
<text class="l07h-dim" x="380" y="276">for the new content version</text>
<line class="l07h-front" x1="124" y1="290" x2="636" y2="290" marker-end="url(#l07h-m-front)"/>
<circle class="l07h-badge l07h-b-front" cx="110" cy="290" r="12"/><text class="l07h-bt" x="110" y="294.5">3</text>
</g>
<g class="l07h-g l07h-g3">
<rect class="l07h-note" x="22" y="324" width="175" height="48" rx="8"/>
<text class="l07h-nt" x="110" y="345">Stores the zookie with</text>
<text class="l07h-nt" x="110" y="362">that content version</text>
<circle class="l07h-badge l07h-b-plain" cx="22" cy="348" r="12"/><text class="l07h-bt" x="22" y="352.5">4</text>
</g>
<g class="l07h-g l07h-g4">
<text class="l07h-main" x="380" y="406">Check Bob's access</text>
<text class="l07h-dim" x="380" y="422">to that content version</text>
<line class="l07h-front" x1="124" y1="436" x2="636" y2="436" marker-end="url(#l07h-m-front)"/>
<circle class="l07h-badge l07h-b-front" cx="110" cy="436" r="12"/><text class="l07h-bt" x="110" y="440.5">5</text>
</g>
<g class="l07h-g l07h-g5">
<rect class="l07h-note-good" x="489" y="470" width="261" height="48" rx="8"/>
<text class="l07h-nt" x="620" y="491">Evaluated on ACL data no older than</text>
<text class="l07h-nt" x="620" y="508">that version (external consistency)</text>
<circle class="l07h-badge l07h-b-good" cx="489" cy="494" r="12"/><text class="l07h-bt" x="489" y="498.5">6</text>
</g>
<circle class="l07h-pk l07h-p2" cx="130" cy="290" r="5.5"/>
<circle class="l07h-pk l07h-p4" cx="130" cy="436" r="5.5"/>
<line class="l07h-front" x1="40" y1="592" x2="70" y2="592"/>
<text class="l07h-dim" x="78" y="596" style="text-anchor:start">message</text>
<rect class="l07h-note-bad" x="156" y="584" width="22" height="16" rx="4"/>
<text class="l07h-dim" x="186" y="596" style="text-anchor:start">the problem</text>
<rect class="l07h-note-good" x="290" y="584" width="22" height="16" rx="4"/>
<text class="l07h-dim" x="320" y="596" style="text-anchor:start">what the zookie guarantees</text>
</svg>
</div>
</div>
<!-- /diagram:new-enemy -->

The numbers match the diagram: 1 is the ACL change, 2 names the problem, 3 and 4 are the client getting and keeping a zookie, 5 is the later check and 6 is what the zookie guarantees.

Microsoft's numbers show the layers. Group claims cap at 200 (JWT), 150 (SAML) and 6 (implicit flow); beyond that the token carries an overage indicator and you query Graph. Access tokens default to about an hour (a random 60 to 90 minutes, lesson 1); CAE sessions run up to 28 hours, with the issuer telling the resource provider to stop honouring tokens on critical events. The CAE page says latency of up to 15 minutes may be seen for critical events, yet group and Conditional Access changes "could take up to one day" to take effect. Both are on the same page, so design for the one that matches your change type. CAE is based on OpenID CAEP; CAEP 1.0 (document dated 29 August 2025) defines Session Revoked, Token Claims Change, Credential Change, Assurance Level Change, Device Compliance Change, Session Established, Session Presented and Risk Level Change events.

Design rule: classify each decision by blast radius. Coarse, slow-changing facts may live in claims, and the token lifetime is then your revocation SLA. High-impact actions call a live check, whether introspection, a PDP or Graph.

## Policy-as-code and externalized authorization

OPA "decouples policy decision-making from policy enforcement": the service queries it with structured JSON input and the policy is written in Rego. Cedar writes policies over principal, action, resource and context. OpenFGA answers a different question, a graph check. OpenFGA's own docs point pure attribute checks to attributes and infrastructure or admission policy to policy engines. Mapped to NIST: the app or gateway is the PEP, the engine is the PDP, directory, HR and token data are PIPs, and a repository with CI that tests policy is the PAP.

Pitfalls: attribute inputs that the caller can forge; PIP freshness (section 3.3.1 again); no decision logging; and unreviewed rights to change policy, which we would treat as a privileged role under AC-5 separation of duties (our inference; AC-5 does not mention policy repositories). Whether the PEP fails open or closed when the PDP is unreachable is not prescribed by these sources; decide and document it.

<!-- diagram:policy-points -->
<div class="l07i-wrap" style="position:relative">
<input type="checkbox" id="l07i-pause" class="l07i-cb" /><label for="l07i-pause" class="l07i-btn"><span class="l07i-off">Pause animation</span><span class="l07i-on">Play animation</span></label>
<div class="l07i-box" style="overflow-x:auto">
<svg class="l07i-flow" viewBox="0 0 760 344" role="img" aria-labelledby="l07i-t l07i-d" style="width:760px;max-width:100%;min-width:699px;height:auto;display:block;margin:0 auto">
<title id="l07i-t">Externalized authorization: NIST's four points and their pitfalls</title>
<desc id="l07i-d">A nested diagram mapping NIST's ABAC architecture onto real components, with the pitfalls the text names. Two pitfalls the text ties to no one point are attribute inputs the caller can forge and no decision logging. The policy enforcement point is the app or gateway and enforces the decision; whether it fails open or closed when the decision point is unreachable is not prescribed by these sources, so decide and document it. The policy decision point is the engine, for example OPA or Cedar, and computes the decision. The policy information point is directory, HR and token data and supplies attributes; a pitfall is stale attributes. The policy administration point is a repository with CI that tests policy; a pitfall is unreviewed rights to change policy, which we would treat as a privileged role under AC-5, our inference. The diagram highlights each part in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
<style>
svg.l07i-flow{--ink:light-dark(#000000,#ffffff)}
.l07i-box{fill:var(--panel);stroke:var(--border-strong);stroke-width:1.5}
.l07i-hot{fill:var(--panel);stroke:var(--accent);stroke-width:2.5}
.l07i-ttl{fill:var(--ink);font:600 15px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l07i-sub{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l07i-life{stroke:var(--border-strong);stroke-width:1.5;stroke-dasharray:4 5}
.l07i-front{stroke:var(--accent);stroke-width:2;fill:none}
.l07i-back{stroke:var(--muted);stroke-width:2;stroke-dasharray:7 5;fill:none}
.l07i-bad{stroke:var(--bad);stroke-width:2;fill:none}
.l07i-main{fill:var(--ink);font:600 13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l07i-badt{fill:var(--ink)}
.l07i-dim{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l07i-badge{fill:var(--accent)}
.l07i-b-back{fill:var(--muted)}
.l07i-b-bad{fill:var(--bad)}
.l07i-b-good{fill:var(--good)}
.l07i-bt{fill:var(--on-accent);font:700 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l07i-note{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l07i-note-good{fill:var(--good-bg);stroke:var(--good);stroke-width:1.5}
.l07i-note-bad{fill:var(--bad-bg);stroke:var(--bad);stroke-width:1.5}
.l07i-nt{fill:var(--ink);font:500 12.5px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l07i-nest{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l07i-row{fill:var(--raised);stroke:var(--border-strong);stroke-width:1}
.l07i-ttlL{fill:var(--ink);font:600 14px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l07i-subL{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l07i-dimL{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l07i-dimR{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:end}
.l07i-conn{stroke:var(--accent);stroke-width:1.5;fill:none}
.l07i-edge{stroke:var(--border-strong);stroke-width:1.75;fill:none}
.l07i-hl{fill:none;stroke:var(--accent);stroke-width:3}
.l07i-hle{stroke:var(--accent);stroke-width:3;fill:none}
.l07i-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:24s;animation-timing-function:linear;animation-iteration-count:infinite}
.l07i-pk.l07i-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.l07i-pk.l07i-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.l07i-wrap{margin:20px 0}
@media (min-width:801px){.l07i-wrap{margin-left:-44px;margin-right:-44px}}
.l07i-g rect,.l07i-g line,.l07i-g path:not(.l07i-gl){opacity:.5;animation-duration:24s;animation-timing-function:linear;animation-iteration-count:infinite}
.l07i-h{opacity:0;animation-duration:24s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.l07i-flow:hover .l07i-g rect,svg.l07i-flow:hover .l07i-g line,svg.l07i-flow:hover .l07i-g path:not(.l07i-gl),svg.l07i-flow:hover .l07i-pk,svg.l07i-flow:hover .l07i-h{animation-play-state:paused}
.l07i-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.l07i-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.l07i-btn:hover{background:var(--hover)}
.l07i-cb:focus-visible + .l07i-btn{outline:2px solid var(--accent);outline-offset:2px}
.l07i-cb:checked + .l07i-btn .l07i-off,.l07i-cb:not(:checked) + .l07i-btn .l07i-on{display:none}
.l07i-cb:checked ~ .l07i-box .l07i-g rect,.l07i-cb:checked ~ .l07i-box .l07i-g line,.l07i-cb:checked ~ .l07i-box .l07i-g path:not(.l07i-gl),.l07i-cb:checked ~ .l07i-box .l07i-pk,.l07i-cb:checked ~ .l07i-box .l07i-h{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.l07i-g rect,.l07i-g line,.l07i-g path:not(.l07i-gl){animation:none;opacity:1}.l07i-pk{animation:none;display:none}.l07i-h{animation:none;opacity:0}.l07i-btn{display:none}}
@keyframes l07i-g0{0%{opacity:1}25%{opacity:1}25.01%,100%{opacity:.5}}
@keyframes l07i-h0{0%{opacity:1}25%{opacity:1}25.01%,100%{opacity:0}}
.l07i-g0 rect,.l07i-g0 line,.l07i-g0 path:not(.l07i-gl){animation-name:l07i-g0}.l07i-h0{animation-name:l07i-h0}
@keyframes l07i-g1{0%,24.99%{opacity:.5}25%{opacity:1}50%{opacity:1}50.01%,100%{opacity:.5}}
@keyframes l07i-h1{0%,24.99%{opacity:0}25%{opacity:1}50%{opacity:1}50.01%,100%{opacity:0}}
.l07i-g1 rect,.l07i-g1 line,.l07i-g1 path:not(.l07i-gl){animation-name:l07i-g1}.l07i-h1{animation-name:l07i-h1}
@keyframes l07i-g2{0%,49.99%{opacity:.5}50%{opacity:1}75%{opacity:1}75.01%,100%{opacity:.5}}
@keyframes l07i-h2{0%,49.99%{opacity:0}50%{opacity:1}75%{opacity:1}75.01%,100%{opacity:0}}
.l07i-g2 rect,.l07i-g2 line,.l07i-g2 path:not(.l07i-gl){animation-name:l07i-g2}.l07i-h2{animation-name:l07i-h2}
@keyframes l07i-g3{0%,74.99%{opacity:.5}75%{opacity:1}100%{opacity:1}100.01%,100%{opacity:.5}}
@keyframes l07i-h3{0%,74.99%{opacity:0}75%{opacity:1}100%{opacity:1}100.01%,100%{opacity:0}}
.l07i-g3 rect,.l07i-g3 line,.l07i-g3 path:not(.l07i-gl){animation-name:l07i-g3}.l07i-h3{animation-name:l07i-h3}
</style>
<defs>
<marker id="l07i-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="l07i-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="l07i-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<rect class="l07i-box" x="14" y="16" width="440" height="266" rx="9"/><text class="l07i-ttlL" x="28" y="37">Externalized authorization</text><text class="l07i-subL" x="28" y="54">NIST's ABAC architecture mapped to real components</text>
<rect class="l07i-nest" x="26" y="62" width="416" height="46" rx="9"/><text class="l07i-ttlL" x="40" y="83">PEP: policy enforcement point</text><text class="l07i-subL" x="40" y="100">the app or gateway: enforces the decision</text>
<rect class="l07i-nest" x="26" y="116" width="416" height="46" rx="9"/><text class="l07i-ttlL" x="40" y="137">PDP: policy decision point</text><text class="l07i-subL" x="40" y="154">the engine, e.g. OPA or Cedar: computes the decision</text>
<rect class="l07i-nest" x="26" y="170" width="416" height="46" rx="9"/><text class="l07i-ttlL" x="40" y="191">PIP: policy information point</text><text class="l07i-subL" x="40" y="208">directory, HR and token data: supplies attributes</text>
<rect class="l07i-nest" x="26" y="224" width="416" height="46" rx="9"/><text class="l07i-ttlL" x="40" y="245">PAP: policy administration point</text><text class="l07i-subL" x="40" y="262">a repository with CI that tests policy: manages policy</text>
<g class="l07i-g l07i-g0">
<path class="l07i-conn" d="M454,33 L462,33 L462,42 L470,42" marker-end="url(#l07i-m-front)"/>
<rect class="l07i-note-bad" x="484" y="10" width="262" height="65" rx="8"/>
<text class="l07i-nt" x="615" y="31">Text ties these to no one point:</text>
<text class="l07i-nt" x="615" y="48">attribute inputs the caller can</text>
<text class="l07i-nt" x="615" y="65">forge; no decision logging</text>
<circle class="l07i-badge l07i-b-bad" cx="484" cy="42" r="12"/><text class="l07i-bt" x="484" y="47.0">1</text>
</g>
<g class="l07i-g l07i-g1">
<path class="l07i-conn" d="M442,79 L466,79 L466,118 L470,118" marker-end="url(#l07i-m-front)"/>
<rect class="l07i-note-bad" x="484" y="85" width="262" height="65" rx="8"/>
<text class="l07i-nt" x="615" y="106">Fail open or closed if the PDP is</text>
<text class="l07i-nt" x="615" y="123">unreachable? These sources do not</text>
<text class="l07i-nt" x="615" y="140">prescribe it: decide and document it</text>
<circle class="l07i-badge l07i-b-bad" cx="484" cy="118" r="12"/><text class="l07i-bt" x="484" y="122.0">2</text>
</g>
<g class="l07i-g l07i-g2">
<path class="l07i-conn" d="M442,187 L470,187 L470,187 L470,187" marker-end="url(#l07i-m-front)"/>
<rect class="l07i-note-bad" x="484" y="163" width="262" height="48" rx="8"/>
<text class="l07i-nt" x="615" y="184">Stale attributes (PIP freshness,</text>
<text class="l07i-nt" x="615" y="201">section 3.3.1)</text>
<circle class="l07i-badge l07i-b-bad" cx="484" cy="187" r="12"/><text class="l07i-bt" x="484" y="191.5">3</text>
</g>
<g class="l07i-g l07i-g3">
<path class="l07i-conn" d="M442,241 L474,241 L474,254 L470,254" marker-end="url(#l07i-m-front)"/>
<rect class="l07i-note-bad" x="484" y="221" width="262" height="65" rx="8"/>
<text class="l07i-nt" x="615" y="242">Unreviewed rights to change policy;</text>
<text class="l07i-nt" x="615" y="259">we would treat them as a privileged</text>
<text class="l07i-nt" x="615" y="276">role (AC-5, our inference)</text>
<circle class="l07i-badge l07i-b-bad" cx="484" cy="254" r="12"/><text class="l07i-bt" x="484" y="258.0">4</text>
</g>
<g class="l07i-h l07i-h0">
<rect class="l07i-hl" x="14" y="16" width="440" height="266" rx="9"/>
</g>
<g class="l07i-h l07i-h1">
<rect class="l07i-hl" x="26" y="62" width="416" height="46" rx="9"/>
</g>
<g class="l07i-h l07i-h2">
<rect class="l07i-hl" x="26" y="170" width="416" height="46" rx="9"/>
</g>
<g class="l07i-h l07i-h3">
<rect class="l07i-hl" x="26" y="224" width="416" height="46" rx="9"/>
</g>
<rect class="l07i-note-bad" x="40" y="312" width="22" height="16" rx="4"/>
<text class="l07i-dim" x="70" y="324" style="text-anchor:start">pitfall</text>
</svg>
</div>
</div>
<!-- /diagram:policy-points -->

Each box is a NIST point mapped to a real component. The callouts on the PEP, PIP and PAP boxes are the pitfalls the text ties to that point; forged attribute inputs and missing decision logging (callout 1, on the top box) are listed above because the text names no point for them. The numbers match the diagram; callout 2 is a decision the sources leave to you, and callout 4 is our inference.

## Non-human identities

CIS 5.1 requires an inventory of user and administrator accounts, and 5.5 a separate inventory of service accounts with department owner, review date and purpose. The client credentials grant (RFC 6749 section 4.4) is for confidential clients only, and section 4.4.3 says a refresh token SHOULD NOT be included. Federate workloads instead of storing secrets: GitHub Actions OIDC tokens carry `iss` `https://token.actions.githubusercontent.com` and a `sub` identifying the workflow source, such as `repo:octo-org/octo-repo:environment:prod`, and the workflow needs `id-token: write`. AWS advises roles with temporary credentials, and for workloads outside AWS lists `AssumeRoleWithWebIdentity` with a JWT from a configured IdP. Long-term access keys are the exception, to be updated "when an employee leaves your company".

Okta API tokens show the human-coupling trap: they inherit the creating admin's privileges, change with that admin's role, are deprovisioned when the creator is deactivated, and are valid 30 days from creation or last use. Okta recommends a service account for creating tokens and OAuth 2.0 over SSWS. Entra PIM can also assign roles to service principals and managed identities, with time bounds.

## Designing a leaver runbook with verification

Treat "deactivated" as a claim, not evidence. In RFC 7643 section 4.1.1, `active` is administrative status and "the definitive meaning of this attribute is determined by the service provider", so a successful SCIM update proves little about sessions, keys or tokens. NIST PS-4 requires disabling access within an organization-defined period, revoking authenticators and credentials, retrieving property and retaining access to information the person controlled. Okta states deletion cannot be undone, and its API reference calls deactivation destructive too: "The user is deprovisioned from all assigned apps, which might destroy their data such as email or files. This action cannot be recovered!" Suspension is the non-destructive hold: it stops sessions and retains group and app assignments. CIS 6.2 adds that disabling instead of deleting may be necessary to preserve audit trails. Which Okta state your offboarding uses, and how long data is retained before deactivation or deletion, is your policy (not Okta's rule): decide it explicitly.

<!-- diagram:leaver-verify -->
<div class="l07j-wrap" style="position:relative">
<input type="checkbox" id="l07j-pause" class="l07j-cb" /><label for="l07j-pause" class="l07j-btn"><span class="l07j-off">Pause animation</span><span class="l07j-on">Play animation</span></label>
<div class="l07j-box" style="overflow-x:auto">
<svg class="l07j-flow" viewBox="0 0 760 498" role="img" aria-labelledby="l07j-t l07j-d" style="width:760px;max-width:100%;min-width:699px;height:auto;display:block;margin:0 auto">
<title id="l07j-t">Deactivated is a claim, not evidence</title>
<desc id="l07j-d">Three parties: the offboarding runbook, the identity provider and an app that is a SCIM service provider. The runbook deactivates the user at the identity provider, which sends the app a SCIM update of active. In RFC 7643, active is administrative status and its definitive meaning is determined by the service provider. A successful SCIM update therefore proves little about sessions, keys or tokens, so the runbook verifies each surface against its expected state. The diagram highlights each step in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
<style>
svg.l07j-flow{--ink:light-dark(#000000,#ffffff)}
.l07j-box{fill:var(--panel);stroke:var(--border-strong);stroke-width:1.5}
.l07j-hot{fill:var(--panel);stroke:var(--accent);stroke-width:2.5}
.l07j-ttl{fill:var(--ink);font:600 15px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l07j-sub{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l07j-life{stroke:var(--border-strong);stroke-width:1.5;stroke-dasharray:4 5}
.l07j-front{stroke:var(--accent);stroke-width:2;fill:none}
.l07j-back{stroke:var(--muted);stroke-width:2;stroke-dasharray:7 5;fill:none}
.l07j-bad{stroke:var(--bad);stroke-width:2;fill:none}
.l07j-main{fill:var(--ink);font:600 13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l07j-badt{fill:var(--ink)}
.l07j-dim{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l07j-badge{fill:var(--accent)}
.l07j-b-back{fill:var(--muted)}
.l07j-b-bad{fill:var(--bad)}
.l07j-b-good{fill:var(--good)}
.l07j-bt{fill:var(--on-accent);font:700 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l07j-note{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l07j-note-good{fill:var(--good-bg);stroke:var(--good);stroke-width:1.5}
.l07j-note-bad{fill:var(--bad-bg);stroke:var(--bad);stroke-width:1.5}
.l07j-nt{fill:var(--ink);font:500 12.5px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l07j-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:20s;animation-timing-function:linear;animation-iteration-count:infinite}
.l07j-pk.l07j-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.l07j-pk.l07j-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.l07j-wrap{margin:20px 0}
@media (min-width:801px){.l07j-wrap{margin-left:-44px;margin-right:-44px}}
.l07j-g rect,.l07j-g line,.l07j-g path:not(.l07j-gl){opacity:.5;animation-duration:20s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.l07j-flow:hover .l07j-g rect,svg.l07j-flow:hover .l07j-g line,svg.l07j-flow:hover .l07j-g path:not(.l07j-gl),svg.l07j-flow:hover .l07j-pk{animation-play-state:paused}
.l07j-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.l07j-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.l07j-btn:hover{background:var(--hover)}
.l07j-cb:focus-visible + .l07j-btn{outline:2px solid var(--accent);outline-offset:2px}
.l07j-cb:checked + .l07j-btn .l07j-off,.l07j-cb:not(:checked) + .l07j-btn .l07j-on{display:none}
.l07j-cb:checked ~ .l07j-box .l07j-g rect,.l07j-cb:checked ~ .l07j-box .l07j-g line,.l07j-cb:checked ~ .l07j-box .l07j-g path:not(.l07j-gl),.l07j-cb:checked ~ .l07j-box .l07j-pk{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.l07j-g rect,.l07j-g line,.l07j-g path:not(.l07j-gl){animation:none;opacity:1}.l07j-pk{animation:none;display:none}.l07j-btn{display:none}}
@keyframes l07j-g0{0%{opacity:1}30%{opacity:1}30.01%,100%{opacity:.5}}
@keyframes l07j-p0{0%,-0.01%{opacity:0;transform:translateX(0)}0%{opacity:1;transform:translateX(0)}24%{opacity:1;transform:translateX(236px)}30%{opacity:1;transform:translateX(236px)}30.01%,100%{opacity:0;transform:translateX(236px)}}
.l07j-g0 rect,.l07j-g0 line,.l07j-g0 path:not(.l07j-gl){animation-name:l07j-g0}.l07j-p0{animation-name:l07j-p0}
@keyframes l07j-g1{0%,29.99%{opacity:.5}30%{opacity:1}60%{opacity:1}60.01%,100%{opacity:.5}}
@keyframes l07j-p1{0%,29.99%{opacity:0;transform:translateX(0)}30%{opacity:1;transform:translateX(0)}54%{opacity:1;transform:translateX(236px)}60%{opacity:1;transform:translateX(236px)}60.01%,100%{opacity:0;transform:translateX(236px)}}
.l07j-g1 rect,.l07j-g1 line,.l07j-g1 path:not(.l07j-gl){animation-name:l07j-g1}.l07j-p1{animation-name:l07j-p1}
@keyframes l07j-g2{0%,59.99%{opacity:.5}60%{opacity:1}80%{opacity:1}80.01%,100%{opacity:.5}}
.l07j-g2 rect,.l07j-g2 line,.l07j-g2 path:not(.l07j-gl){animation-name:l07j-g2}
@keyframes l07j-g3{0%,79.99%{opacity:.5}80%{opacity:1}100%{opacity:1}100.01%,100%{opacity:.5}}
.l07j-g3 rect,.l07j-g3 line,.l07j-g3 path:not(.l07j-gl){animation-name:l07j-g3}
</style>
<defs>
<marker id="l07j-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="l07j-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="l07j-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<line class="l07j-life" x1="110" y1="72" x2="110" y2="446"/>
<line class="l07j-life" x1="380" y1="72" x2="380" y2="446"/>
<line class="l07j-life" x1="650" y1="72" x2="650" y2="446"/>
<rect class="l07j-box" x="20" y="10" width="180" height="62" rx="10"/><text class="l07j-ttl" x="110" y="36">Offboarding</text><text class="l07j-sub" x="110" y="56">your runbook</text>
<rect class="l07j-box" x="290" y="10" width="180" height="62" rx="10"/><text class="l07j-ttl" x="380" y="36">IdP</text><text class="l07j-sub" x="380" y="56">e.g. Okta</text>
<rect class="l07j-hot" x="560" y="10" width="180" height="62" rx="10"/><text class="l07j-ttl" x="650" y="36">App</text><text class="l07j-sub" x="650" y="56">SCIM service provider</text>
<g class="l07j-g l07j-g0">
<text class="l07j-main" x="245" y="108">Deactivate</text>
<text class="l07j-dim" x="245" y="124">the user</text>
<line class="l07j-front" x1="124" y1="138" x2="366" y2="138" marker-end="url(#l07j-m-front)"/>
<circle class="l07j-badge l07j-b-front" cx="110" cy="138" r="12"/><text class="l07j-bt" x="110" y="142.5">1</text>
</g>
<g class="l07j-g l07j-g1">
<text class="l07j-main" x="515" y="178">SCIM update</text>
<text class="l07j-dim" x="515" y="194">of active</text>
<line class="l07j-front" x1="394" y1="208" x2="636" y2="208" marker-end="url(#l07j-m-front)"/>
<circle class="l07j-badge l07j-b-front" cx="380" cy="208" r="12"/><text class="l07j-bt" x="380" y="212.5">2</text>
</g>
<g class="l07j-g l07j-g2">
<rect class="l07j-note-bad" x="483" y="242" width="267" height="65" rx="8"/>
<text class="l07j-nt" x="616" y="263">active is administrative status; its</text>
<text class="l07j-nt" x="616" y="280">definitive meaning is determined by</text>
<text class="l07j-nt" x="616" y="297">the service provider</text>
<circle class="l07j-badge l07j-b-bad" cx="483" cy="274" r="12"/><text class="l07j-bt" x="483" y="279.0">3</text>
</g>
<g class="l07j-g l07j-g3">
<rect class="l07j-note-good" x="10" y="335" width="287" height="65" rx="8"/>
<text class="l07j-nt" x="154" y="356">A successful SCIM update proves little</text>
<text class="l07j-nt" x="154" y="373">about sessions, keys or tokens: verify</text>
<text class="l07j-nt" x="154" y="390">each surface against its expected state</text>
<circle class="l07j-badge l07j-b-good" cx="10" cy="368" r="12"/><text class="l07j-bt" x="10" y="372.0">4</text>
</g>
<circle class="l07j-pk l07j-p0" cx="130" cy="138" r="5.5"/>
<circle class="l07j-pk l07j-p1" cx="400" cy="208" r="5.5"/>
<line class="l07j-front" x1="40" y1="474" x2="70" y2="474"/>
<text class="l07j-dim" x="78" y="478" style="text-anchor:start">message</text>
<rect class="l07j-note-bad" x="156" y="466" width="22" height="16" rx="4"/>
<text class="l07j-dim" x="186" y="478" style="text-anchor:start">the gap</text>
<rect class="l07j-note-good" x="264" y="466" width="22" height="16" rx="4"/>
<text class="l07j-dim" x="294" y="478" style="text-anchor:start">what to do about it</text>
</svg>
</div>
</div>
<!-- /diagram:leaver-verify -->

The numbers match the diagram: the deactivation is sent to the app as a SCIM update of `active` (steps 1 and 2), but what that means is the app's decision (step 3), so step 4 is the verification the table below sets out.

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
