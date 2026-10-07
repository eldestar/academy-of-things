# Authorization and the identity lifecycle

Earlier lessons covered getting a person signed in. This lesson covers what happens next: what that person is allowed to do, and how their access stays correct from the day they join until the day they leave. Most identity audit findings come from here. Facts checked 2026-10-06 against the docs named in the text.

Our running example: **Sam** is a new hire at Example Co. who needs the customer app (the CRM) to do the job.

## What authorization is, and four ways to decide

**Authentication** asks "who are you?". **Authorization** asks "what are you allowed to do?". An **entitlement** is one specific thing a person may do, such as "read customer records" or "administer the CRM". Systems decide authorization in four common ways:

- **ACL (access control list):** each thing carries a list of names allowed in. Easy to understand, but names are rarely removed, so people pile up access over time. NIST SP 800-162 says failing to remove access over time "leads to users accumulating privileges".
- **RBAC (role-based access control):** Sam gets a role such as "Support agent", and the role carries the entitlements. Good when jobs are stable. If every odd case needs its own special role you get **role explosion**: hundreds of roles with a handful of people each.
- **ABAC (attribute-based access control):** a rule looks at facts, called **attributes**, such as department, device or location. NIST SP 800-162 defines it as deciding from attributes of the person, attributes of the thing, conditions like location, and a set of policies. It handles rules like "Sales staff on a managed laptop". The weakness is **attribute drift**: if the department field in the HR system is wrong or late, the rule gives the wrong access. (That name is informal, not a NIST term.)
- **ReBAC (relationship-based access control):** access follows relationships, such as "Sam is a member of the team that owns this folder". Good for sharing and folders inside folders. The weakness is that relationships multiply quietly, like ACL names (our own inference, not a NIST or vendor claim).

<!-- diagram:authz-models -->
<div style="position:relative;margin:20px 0">
<input type="checkbox" id="l07a-pause" class="l07a-cb" /><label for="l07a-pause" class="l07a-btn"><span class="l07a-off">Pause animation</span><span class="l07a-on">Play animation</span></label>
<div class="l07a-box" style="overflow-x:auto">
<svg class="l07a-flow" viewBox="0 0 760 551" role="img" aria-labelledby="l07a-t l07a-d" style="width:100%;min-width:640px;max-width:800px;height:auto;display:block;margin:0 auto">
<title id="l07a-t">Four ways to decide what a person may do</title>
<desc id="l07a-d">A table with one row per way of deciding and three columns: what it decides on, what speaks for it, and how it goes wrong. ACL decides on a list of names on each thing; it is easy to understand, but names are rarely removed so people pile up access. RBAC decides on a role such as Support agent; it is good when jobs are stable, and goes wrong by role explosion, hundreds of roles with a handful of people each. ABAC decides on attributes such as department, device or location; it handles rules like Sales staff on a managed laptop, and goes wrong by attribute drift when the HR department field is wrong or late. ReBAC decides on relationships, such as being a member of the team that owns a folder; it is good for sharing and folders inside folders, and goes wrong because relationships multiply quietly. The diagram highlights each row in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
<style>
.l07a-box{fill:var(--panel);stroke:var(--border-strong);stroke-width:1.5}
.l07a-hot{fill:var(--panel);stroke:var(--accent);stroke-width:2.5}
.l07a-ttl{fill:var(--text);font:600 15px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l07a-sub{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l07a-life{stroke:var(--border-strong);stroke-width:1.5;stroke-dasharray:4 5}
.l07a-front{stroke:var(--accent);stroke-width:2;fill:none}
.l07a-back{stroke:var(--muted);stroke-width:2;stroke-dasharray:7 5;fill:none}
.l07a-bad{stroke:var(--bad);stroke-width:2;fill:none}
.l07a-main{fill:var(--text);font:600 13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l07a-badt{fill:var(--bad-text)}
.l07a-dim{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l07a-badge{fill:var(--accent)}
.l07a-b-back{fill:var(--muted)}
.l07a-b-bad{fill:var(--bad)}
.l07a-b-good{fill:var(--good)}
.l07a-bt{fill:var(--on-accent);font:700 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l07a-note{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l07a-note-good{fill:var(--good-bg);stroke:var(--good);stroke-width:1.5}
.l07a-note-bad{fill:var(--bad-bg);stroke:var(--bad);stroke-width:1.5}
.l07a-nt{fill:var(--body);font:12.5px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l07a-nest{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l07a-row{fill:var(--raised);stroke:var(--border-strong);stroke-width:1}
.l07a-ttlL{fill:var(--text);font:600 14px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l07a-subL{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l07a-dimL{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l07a-dimR{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:end}
.l07a-conn{stroke:var(--accent);stroke-width:1.5;fill:none}
.l07a-edge{stroke:var(--border-strong);stroke-width:1.75;fill:none}
.l07a-hl{fill:none;stroke:var(--accent);stroke-width:3}
.l07a-hle{stroke:var(--accent);stroke-width:3;fill:none}
.l07a-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:20s;animation-timing-function:linear;animation-iteration-count:infinite}
.l07a-pk.l07a-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.l07a-pk.l07a-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.l07a-g{opacity:.45;animation-duration:20s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.l07a-flow:hover .l07a-g,svg.l07a-flow:hover .l07a-pk{animation-play-state:paused}
.l07a-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.l07a-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.l07a-btn:hover{background:var(--hover)}
.l07a-cb:focus-visible + .l07a-btn{outline:2px solid var(--accent);outline-offset:2px}
.l07a-cb:checked + .l07a-btn .l07a-off,.l07a-cb:not(:checked) + .l07a-btn .l07a-on{display:none}
.l07a-cb:checked ~ .l07a-box .l07a-g,.l07a-cb:checked ~ .l07a-box .l07a-pk{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.l07a-g{animation:none;opacity:1}.l07a-pk{animation:none;display:none}.l07a-btn{display:none}}
@keyframes l07a-g0{0%{opacity:1}25%{opacity:1}25.01%,100%{opacity:.45}}
.l07a-g0{animation-name:l07a-g0}
@keyframes l07a-g1{0%,24.99%{opacity:.45}25%{opacity:1}50%{opacity:1}50.01%,100%{opacity:.45}}
.l07a-g1{animation-name:l07a-g1}
@keyframes l07a-g2{0%,49.99%{opacity:.45}50%{opacity:1}75%{opacity:1}75.01%,100%{opacity:.45}}
.l07a-g2{animation-name:l07a-g2}
@keyframes l07a-g3{0%,74.99%{opacity:.45}75%{opacity:1}100%{opacity:1}100.01%,100%{opacity:.45}}
.l07a-g3{animation-name:l07a-g3}
</style>
<defs>
<marker id="l07a-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="l07a-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="l07a-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<rect class="l07a-box" x="240" y="10" width="162" height="62" rx="10"/><text class="l07a-ttl" x="321" y="36">Decides on</text><text class="l07a-sub" x="321" y="56"></text>
<rect class="l07a-box" x="410" y="10" width="162" height="62" rx="10"/><text class="l07a-ttl" x="491" y="36">In its favour</text><text class="l07a-sub" x="491" y="56"></text>
<rect class="l07a-box" x="580" y="10" width="162" height="62" rx="10"/><text class="l07a-ttl" x="661" y="36">Goes wrong by</text><text class="l07a-sub" x="661" y="56"></text>
<g class="l07a-g l07a-g0">
<rect class="l07a-row" x="10" y="86" width="740" height="86" rx="8"/>
<text class="l07a-ttlL" x="24" y="112">ACL</text>
<text class="l07a-subL" x="24" y="130">access control list</text>
<text class="l07a-nt" x="321" y="134">a list of names on</text>
<text class="l07a-nt" x="321" y="149">each thing</text>
<text class="l07a-nt" x="491" y="134">easy to understand</text>
<text class="l07a-nt" x="661" y="134">names rarely removed, so</text>
<text class="l07a-nt" x="661" y="149">people pile up access</text>
</g>
<g class="l07a-g l07a-g1">
<rect class="l07a-row" x="10" y="180" width="740" height="101" rx="8"/>
<text class="l07a-ttlL" x="24" y="206">RBAC</text>
<text class="l07a-subL" x="24" y="224">role-based</text>
<text class="l07a-nt" x="321" y="228">a role such as</text>
<text class="l07a-nt" x="321" y="243">"Support agent"</text>
<text class="l07a-nt" x="491" y="228">good when jobs are</text>
<text class="l07a-nt" x="491" y="243">stable</text>
<text class="l07a-nt" x="661" y="228">role explosion: hundreds</text>
<text class="l07a-nt" x="661" y="243">of roles, a handful of</text>
<text class="l07a-nt" x="661" y="258">people each</text>
</g>
<g class="l07a-g l07a-g2">
<rect class="l07a-row" x="10" y="289" width="740" height="101" rx="8"/>
<text class="l07a-ttlL" x="24" y="315">ABAC</text>
<text class="l07a-subL" x="24" y="333">attribute-based</text>
<text class="l07a-nt" x="321" y="337">attributes such as</text>
<text class="l07a-nt" x="321" y="352">department, device or</text>
<text class="l07a-nt" x="321" y="367">location</text>
<text class="l07a-nt" x="491" y="337">rules like "Sales staff</text>
<text class="l07a-nt" x="491" y="352">on a managed laptop"</text>
<text class="l07a-nt" x="661" y="337">attribute drift (informal</text>
<text class="l07a-nt" x="661" y="352">name): a wrong or late</text>
<text class="l07a-nt" x="661" y="367">department field</text>
</g>
<g class="l07a-g l07a-g3">
<rect class="l07a-row" x="10" y="398" width="740" height="101" rx="8"/>
<text class="l07a-ttlL" x="24" y="424">ReBAC</text>
<text class="l07a-subL" x="24" y="442">relationship-based</text>
<text class="l07a-nt" x="321" y="446">relationships, such as</text>
<text class="l07a-nt" x="321" y="461">member of the team that</text>
<text class="l07a-nt" x="321" y="476">owns this folder</text>
<text class="l07a-nt" x="491" y="446">sharing, and folders</text>
<text class="l07a-nt" x="491" y="461">inside folders</text>
<text class="l07a-nt" x="661" y="446">relationships multiply</text>
<text class="l07a-nt" x="661" y="461">quietly (our own</text>
<text class="l07a-nt" x="661" y="476">inference)</text>
</g>
</svg>
</div>
</div>
<!-- /diagram:authz-models -->

Read each row across: what the way of deciding looks at, what speaks for it, and how it goes wrong. The diagram steps through one row at a time.

NIST says RBAC does not easily handle decisions that depend on things like location or recent training, which is where ABAC fits better.

## Groups: the lever IT pulls

A **group** is a named set of people. Instead of giving Sam access to ten apps one by one, you add Sam to a group and assign the group to the apps. Okta describes this as assigning users to a group and then granting or denying access to the group. A **group rule** adds people automatically from an attribute. Okta's example: a user whose department is "sales" is added to the Sales group, and when the department changes they are removed from it automatically. Okta says that gives you attribute-based access control.

Groups go wrong in two ways:

- **The name says less than the grant.** A group called `Finance-Readers` that is assigned the administrator role in an app gives every member administrator rights. A name is only a label. To know what a group allows, look at what it is assigned to and with which role in that app.
- **Rules are only as good as the data.** If HR enters the wrong department, a group rule faithfully gives the wrong access.

<!-- diagram:authz-groups -->
<div style="position:relative;margin:20px 0">
<input type="checkbox" id="l07b-pause" class="l07b-cb" /><label for="l07b-pause" class="l07b-btn"><span class="l07b-off">Pause animation</span><span class="l07b-on">Play animation</span></label>
<div class="l07b-box" style="overflow-x:auto">
<svg class="l07b-flow" viewBox="0 0 760 307" role="img" aria-labelledby="l07b-t l07b-d" style="width:100%;min-width:640px;max-width:800px;height:auto;display:block;margin:0 auto">
<title id="l07b-t">What a group is made of, and why its name can mislead</title>
<desc id="l07b-d">A nested diagram. A group, such as Finance-Readers, is a named set of people: Sam is added once instead of to each app one by one. Inside it are the members, who can be added directly or by a group rule that works from an attribute such as department; if HR enters the wrong department, the rule gives the wrong access. The group is also assigned to an app with a role in that app. If that role is administrator, every member gets administrator rights, however harmless the group name sounds, so you look at what the group is assigned to and with which role, not at the name. The diagram highlights each part in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
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
.l07b-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:20s;animation-timing-function:linear;animation-iteration-count:infinite}
.l07b-pk.l07b-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.l07b-pk.l07b-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.l07b-g{opacity:.45;animation-duration:20s;animation-timing-function:linear;animation-iteration-count:infinite}
.l07b-h{opacity:0;animation-duration:20s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.l07b-flow:hover .l07b-g,svg.l07b-flow:hover .l07b-pk,svg.l07b-flow:hover .l07b-h{animation-play-state:paused}
.l07b-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.l07b-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.l07b-btn:hover{background:var(--hover)}
.l07b-cb:focus-visible + .l07b-btn{outline:2px solid var(--accent);outline-offset:2px}
.l07b-cb:checked + .l07b-btn .l07b-off,.l07b-cb:not(:checked) + .l07b-btn .l07b-on{display:none}
.l07b-cb:checked ~ .l07b-box .l07b-g,.l07b-cb:checked ~ .l07b-box .l07b-pk,.l07b-cb:checked ~ .l07b-box .l07b-h{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.l07b-g{animation:none;opacity:1}.l07b-pk{animation:none;display:none}.l07b-h{animation:none;opacity:0}.l07b-btn{display:none}}
@keyframes l07b-g0{0%{opacity:1}25%{opacity:1}25.01%,100%{opacity:.45}}
@keyframes l07b-h0{0%{opacity:1}25%{opacity:1}25.01%,100%{opacity:0}}
.l07b-g0{animation-name:l07b-g0}.l07b-h0{animation-name:l07b-h0}
@keyframes l07b-g1{0%,24.99%{opacity:.45}25%{opacity:1}50%{opacity:1}50.01%,100%{opacity:.45}}
@keyframes l07b-h1{0%,24.99%{opacity:0}25%{opacity:1}50%{opacity:1}50.01%,100%{opacity:0}}
.l07b-g1{animation-name:l07b-g1}.l07b-h1{animation-name:l07b-h1}
@keyframes l07b-g2{0%,49.99%{opacity:.45}50%{opacity:1}75%{opacity:1}75.01%,100%{opacity:.45}}
@keyframes l07b-h2{0%,49.99%{opacity:0}50%{opacity:1}75%{opacity:1}75.01%,100%{opacity:0}}
.l07b-g2{animation-name:l07b-g2}.l07b-h2{animation-name:l07b-h2}
@keyframes l07b-g3{0%,74.99%{opacity:.45}75%{opacity:1}100%{opacity:1}100.01%,100%{opacity:.45}}
@keyframes l07b-h3{0%,74.99%{opacity:0}75%{opacity:1}100%{opacity:1}100.01%,100%{opacity:0}}
.l07b-g3{animation-name:l07b-g3}.l07b-h3{animation-name:l07b-h3}
</style>
<defs>
<marker id="l07b-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="l07b-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="l07b-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<rect class="l07b-box" x="14" y="16" width="440" height="216" rx="9"/><text class="l07b-ttlL" x="28" y="37">Group</text><text class="l07b-subL" x="28" y="54">a named set of people, e.g. Finance-Readers</text>
<rect class="l07b-nest" x="26" y="62" width="416" height="46" rx="9"/><text class="l07b-ttlL" x="40" y="83">Members</text><text class="l07b-subL" x="40" y="100">added directly or by a group rule</text>
<rect class="l07b-nest" x="26" y="116" width="416" height="104" rx="9"/><text class="l07b-ttlL" x="40" y="137">Assigned to an app</text><text class="l07b-subL" x="40" y="154">with a role in that app</text>
<rect class="l07b-nest" x="38" y="162" width="392" height="46" rx="9"/><text class="l07b-ttlL" x="52" y="183">Role: administrator</text><text class="l07b-subL" x="52" y="200">if it is administrator, every member gets it</text>
<g class="l07b-g l07b-g0">
<path class="l07b-conn" d="M454,33 L462,33 L462,34 L470,34" marker-end="url(#l07b-m-front)"/>
<rect class="l07b-note" x="484" y="10" width="262" height="48" rx="8"/>
<text class="l07b-nt" x="615" y="31">Add Sam here once, not to ten</text>
<text class="l07b-nt" x="615" y="48">apps one by one</text>
<circle class="l07b-badge l07b-b-front" cx="484" cy="34" r="12"/><text class="l07b-bt" x="484" y="38.5">1</text>
</g>
<g class="l07b-g l07b-g1">
<path class="l07b-conn" d="M442,79 L466,79 L466,100 L470,100" marker-end="url(#l07b-m-front)"/>
<rect class="l07b-note-bad" x="484" y="68" width="262" height="65" rx="8"/>
<text class="l07b-nt" x="615" y="89">A rule adds people from an attribute;</text>
<text class="l07b-nt" x="615" y="106">a wrong HR department gives the</text>
<text class="l07b-nt" x="615" y="123">wrong access</text>
<circle class="l07b-badge l07b-b-bad" cx="484" cy="100" r="12"/><text class="l07b-bt" x="484" y="105.0">2</text>
</g>
<g class="l07b-g l07b-g2">
<path class="l07b-conn" d="M442,133 L470,133 L470,167 L470,167" marker-end="url(#l07b-m-front)"/>
<rect class="l07b-note-good" x="484" y="143" width="262" height="48" rx="8"/>
<text class="l07b-nt" x="615" y="164">To know what a group allows, look</text>
<text class="l07b-nt" x="615" y="181">at this and the role, not the name</text>
<circle class="l07b-badge l07b-b-good" cx="484" cy="167" r="12"/><text class="l07b-bt" x="484" y="171.5">3</text>
</g>
<g class="l07b-g l07b-g3">
<path class="l07b-conn" d="M430,179 L474,179 L474,225 L470,225" marker-end="url(#l07b-m-front)"/>
<rect class="l07b-note-bad" x="484" y="201" width="262" height="48" rx="8"/>
<text class="l07b-nt" x="615" y="222">Called Readers, but every member</text>
<text class="l07b-nt" x="615" y="239">has administrator rights</text>
<circle class="l07b-badge l07b-b-bad" cx="484" cy="225" r="12"/><text class="l07b-bt" x="484" y="229.5">4</text>
</g>
<g class="l07b-h l07b-h0">
<rect class="l07b-hl" x="14" y="16" width="440" height="216" rx="9"/>
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
<rect class="l07b-note" x="40" y="275" width="22" height="16" rx="4"/>
<text class="l07b-dim" x="70" y="287" style="text-anchor:start">why use a group</text>
<rect class="l07b-note-good" x="200" y="275" width="22" height="16" rx="4"/>
<text class="l07b-dim" x="230" y="287" style="text-anchor:start">where to look</text>
<rect class="l07b-note-bad" x="347" y="275" width="22" height="16" rx="4"/>
<text class="l07b-dim" x="377" y="287" style="text-anchor:start">where it goes wrong</text>
</svg>
</div>
</div>
<!-- /diagram:authz-groups -->

The numbers match the diagram, top to bottom. Part 1 is why IT uses groups, part 2 is where a group rule can go wrong, and parts 3 and 4 show why the name tells you less than the grant.

## The snapshot problem

When Sam signs in through single sign-on, the identity provider hands the app a signed note (a token or an assertion) that can include Sam's groups. The app trusts that note, and often keeps its own session built from it, until the note expires or that session ends. Microsoft states that group information in a token is current only when you receive the token.

So if Sam is removed from a group at 10:00, an app using a note issued at 09:30 can keep treating Sam as a member until the note expires, the app's session ends, or a new note is issued. We call this the **snapshot problem** and the out-of-date group list a **stale claim**; both are our informal names, not standard terms. When access must end sooner, apps can check live, or an admin can revoke the user's sessions.

<!-- diagram:authz-snapshot -->
<div style="position:relative;margin:20px 0">
<input type="checkbox" id="l07c-pause" class="l07c-cb" /><label for="l07c-pause" class="l07c-btn"><span class="l07c-off">Pause animation</span><span class="l07c-on">Play animation</span></label>
<div class="l07c-box" style="overflow-x:auto">
<svg class="l07c-flow" viewBox="0 0 760 563" role="img" aria-labelledby="l07c-t l07c-d" style="width:100%;min-width:640px;max-width:800px;height:auto;display:block;margin:0 auto">
<title id="l07c-t">The snapshot problem: a signed note goes stale</title>
<desc id="l07c-d">Two parties: the identity provider and the app. When Sam signs in, the identity provider hands the app a signed note issued at 09:30 that can include Sam's groups. The app trusts the note and often keeps its own session built from it. At 10:00 Sam is removed from a group. The app can keep treating Sam as a member, a stale claim, until the note expires, the app's session ends, or a new note is issued. To end access sooner, the app can check live, or an admin can revoke the user's sessions. The diagram highlights each step in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
<style>
.l07c-box{fill:var(--panel);stroke:var(--border-strong);stroke-width:1.5}
.l07c-hot{fill:var(--panel);stroke:var(--accent);stroke-width:2.5}
.l07c-ttl{fill:var(--text);font:600 15px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l07c-sub{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l07c-life{stroke:var(--border-strong);stroke-width:1.5;stroke-dasharray:4 5}
.l07c-front{stroke:var(--accent);stroke-width:2;fill:none}
.l07c-back{stroke:var(--muted);stroke-width:2;stroke-dasharray:7 5;fill:none}
.l07c-bad{stroke:var(--bad);stroke-width:2;fill:none}
.l07c-main{fill:var(--text);font:600 13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l07c-badt{fill:var(--bad-text)}
.l07c-dim{fill:var(--muted);font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l07c-badge{fill:var(--accent)}
.l07c-b-back{fill:var(--muted)}
.l07c-b-bad{fill:var(--bad)}
.l07c-b-good{fill:var(--good)}
.l07c-bt{fill:var(--on-accent);font:700 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l07c-note{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l07c-note-good{fill:var(--good-bg);stroke:var(--good);stroke-width:1.5}
.l07c-note-bad{fill:var(--bad-bg);stroke:var(--bad);stroke-width:1.5}
.l07c-nt{fill:var(--body);font:12.5px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l07c-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:18s;animation-timing-function:linear;animation-iteration-count:infinite}
.l07c-pk.l07c-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.l07c-pk.l07c-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.l07c-g{opacity:.45;animation-duration:18s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.l07c-flow:hover .l07c-g,svg.l07c-flow:hover .l07c-pk{animation-play-state:paused}
.l07c-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.l07c-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.l07c-btn:hover{background:var(--hover)}
.l07c-cb:focus-visible + .l07c-btn{outline:2px solid var(--accent);outline-offset:2px}
.l07c-cb:checked + .l07c-btn .l07c-off,.l07c-cb:not(:checked) + .l07c-btn .l07c-on{display:none}
.l07c-cb:checked ~ .l07c-box .l07c-g,.l07c-cb:checked ~ .l07c-box .l07c-pk{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.l07c-g{animation:none;opacity:1}.l07c-pk{animation:none;display:none}.l07c-btn{display:none}}
@keyframes l07c-g0{0%{opacity:1}20%{opacity:1}20.01%,100%{opacity:.45}}
@keyframes l07c-p0{0%,-0.01%{opacity:0;transform:translateX(0)}0%{opacity:1;transform:translateX(0)}20%{opacity:1;transform:translateX(506px)}20.01%,100%{opacity:0;transform:translateX(506px)}}
.l07c-g0{animation-name:l07c-g0}.l07c-p0{animation-name:l07c-p0}
@keyframes l07c-g1{0%,19.99%{opacity:.45}20%{opacity:1}40%{opacity:1}40.01%,100%{opacity:.45}}
.l07c-g1{animation-name:l07c-g1}
@keyframes l07c-g2{0%,39.99%{opacity:.45}40%{opacity:1}60%{opacity:1}60.01%,100%{opacity:.45}}
.l07c-g2{animation-name:l07c-g2}
@keyframes l07c-g3{0%,59.99%{opacity:.45}60%{opacity:1}80%{opacity:1}80.01%,100%{opacity:.45}}
.l07c-g3{animation-name:l07c-g3}
@keyframes l07c-g4{0%,79.99%{opacity:.45}80%{opacity:1}100%{opacity:1}100.01%,100%{opacity:.45}}
.l07c-g4{animation-name:l07c-g4}
</style>
<defs>
<marker id="l07c-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="l07c-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="l07c-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<line class="l07c-life" x1="110" y1="72" x2="110" y2="511"/>
<line class="l07c-life" x1="650" y1="72" x2="650" y2="511"/>
<rect class="l07c-box" x="20" y="10" width="180" height="62" rx="10"/><text class="l07c-ttl" x="110" y="36">Identity provider</text><text class="l07c-sub" x="110" y="56"></text>
<rect class="l07c-hot" x="560" y="10" width="180" height="62" rx="10"/><text class="l07c-ttl" x="650" y="36">The app</text><text class="l07c-sub" x="650" y="56">the CRM</text>
<g class="l07c-g l07c-g0">
<text class="l07c-main" x="380" y="108">Signed note, issued 09:30</text>
<text class="l07c-dim" x="380" y="124">can include Sam's groups</text>
<line class="l07c-front" x1="124" y1="138" x2="636" y2="138" marker-end="url(#l07c-m-front)"/>
<circle class="l07c-badge l07c-b-front" cx="110" cy="138" r="12"/><text class="l07c-bt" x="110" y="142.5">1</text>
</g>
<g class="l07c-g l07c-g1">
<rect class="l07c-note" x="529" y="172" width="221" height="48" rx="8"/>
<text class="l07c-nt" x="640" y="193">App trusts the note and often</text>
<text class="l07c-nt" x="640" y="210">keeps a session built from it</text>
<circle class="l07c-badge l07c-b-plain" cx="529" cy="196" r="12"/><text class="l07c-bt" x="529" y="200.5">2</text>
</g>
<g class="l07c-g l07c-g2">
<rect class="l07c-note" x="26" y="248" width="168" height="48" rx="8"/>
<text class="l07c-nt" x="110" y="269">10:00: Sam is removed</text>
<text class="l07c-nt" x="110" y="286">from a group</text>
<circle class="l07c-badge l07c-b-plain" cx="26" cy="272" r="12"/><text class="l07c-bt" x="26" y="276.5">3</text>
</g>
<g class="l07c-g l07c-g3">
<rect class="l07c-note-bad" x="450" y="324" width="300" height="65" rx="8"/>
<text class="l07c-nt" x="600" y="345">Can keep treating Sam as a member</text>
<text class="l07c-nt" x="600" y="362">(a stale claim) until the note expires,</text>
<text class="l07c-nt" x="600" y="379">the session ends, or a new note is issued</text>
<circle class="l07c-badge l07c-b-bad" cx="450" cy="356" r="12"/><text class="l07c-bt" x="450" y="361.0">4</text>
</g>
<g class="l07c-g l07c-g4">
<rect class="l07c-note-good" x="443" y="417" width="307" height="48" rx="8"/>
<text class="l07c-nt" x="596" y="438">To end access sooner: the app checks live,</text>
<text class="l07c-nt" x="596" y="455">or an admin revokes the user's sessions</text>
<circle class="l07c-badge l07c-b-good" cx="443" cy="441" r="12"/><text class="l07c-bt" x="443" y="445.5">5</text>
</g>
<circle class="l07c-pk l07c-p0" cx="130" cy="138" r="5.5"/>
<line class="l07c-front" x1="40" y1="539" x2="70" y2="539"/>
<text class="l07c-dim" x="78" y="543" style="text-anchor:start">message</text>
<rect class="l07c-note-bad" x="156" y="531" width="22" height="16" rx="4"/>
<text class="l07c-dim" x="186" y="543" style="text-anchor:start">the problem</text>
<rect class="l07c-note-good" x="290" y="531" width="22" height="16" rx="4"/>
<text class="l07c-dim" x="320" y="543" style="text-anchor:start">ends access sooner</text>
</svg>
</div>
</div>
<!-- /diagram:authz-snapshot -->

The numbers match the diagram. Step 1 is the note being issued at sign-in, step 3 is the change at 10:00, and step 4 is the app still trusting the old note. Step 5 is how to end access sooner.

## Joiner, mover, leaver

Microsoft's identity lifecycle page says many organizations model the **identity lifecycle** as three phases. A **joiner** enters the scope of needing access (Sam is hired). A **mover** moves between parts of the organization (Sam goes from Sales to Support). A **leaver** leaves the scope of needing access. Microsoft's example is a joiner process automated from a system of record such as the HR system, so an HR change, not an email to IT, can start each phase.


- **Joiner:** Sam receives **birthright access**, the baseline everyone in that job gets from day one. CIS Safeguard 6.1 asks for a documented, preferably automated process for granting access on new hire or role change.
- **Mover:** the risk is **privilege accumulation**. Sam gets Support access but keeps the Sales access, then the next move adds more. NIST SP 800-53 (PS-5) says that when someone is reassigned you must review and confirm that the old access is still needed.
- **Leaver:** CIS Safeguard 6.2 asks for revoking access "through disabling accounts immediately upon termination, rights revocation, or role change".

<!-- diagram:identity-lifecycle -->
<div style="position:relative;margin:20px 0">
<input type="checkbox" id="l07d-pause" class="l07d-cb" /><label for="l07d-pause" class="l07d-btn"><span class="l07d-off">Pause animation</span><span class="l07d-on">Play animation</span></label>
<div class="l07d-box" style="overflow-x:auto">
<svg class="l07d-flow" viewBox="0 0 760 227" role="img" aria-labelledby="l07d-t l07d-d" style="width:100%;min-width:640px;max-width:800px;height:auto;display:block;margin:0 auto">
<title id="l07d-t">Joiner, mover, leaver: one person's access over time</title>
<desc id="l07d-d">Three phases in order. Joiner: Sam is hired and receives birthright access, the baseline everyone in that job gets from day one. Mover: Sam goes from Sales to Support; the risk is privilege accumulation, because Sam keeps the Sales access, so you review and confirm that the old access is still needed. Leaver: disabling the main account is not the whole job. The diagram highlights each stage in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
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
<text class="l07d-sub" x="99" y="87">Sam is hired</text>
<text class="l07d-nt" x="99" y="114">Birthright access:</text>
<text class="l07d-nt" x="99" y="131">the baseline for the job</text>
<text class="l07d-nt" x="99" y="148">from day one</text>
<text class="l07d-main" x="240" y="64">Sam moves</text>
<line class="l07d-front" x1="193" y1="70" x2="287" y2="70" marker-end="url(#l07d-m-front)"/>
</g>
<g class="l07d-g l07d-g1">
<rect class="l07d-note-bad" x="295" y="40" width="171" height="127" rx="10"/>
<text class="l07d-ttl" x="380" y="67">Mover</text>
<text class="l07d-sub" x="380" y="87">Sales to Support</text>
<text class="l07d-nt" x="380" y="114">Risk: privilege</text>
<text class="l07d-nt" x="380" y="131">accumulation. Confirm</text>
<text class="l07d-nt" x="380" y="148">old access is needed</text>
<text class="l07d-main" x="520" y="64">Sam leaves</text>
<line class="l07d-front" x1="473" y1="70" x2="567" y2="70" marker-end="url(#l07d-m-front)"/>
</g>
<g class="l07d-g l07d-g2">
<rect class="l07d-box" x="575" y="40" width="171" height="127" rx="10"/>
<text class="l07d-ttl" x="661" y="67">Leaver</text>
<text class="l07d-sub" x="661" y="87">leaves the scope</text>
<text class="l07d-nt" x="661" y="114">Disabling the main</text>
<text class="l07d-nt" x="661" y="131">account is not the</text>
<text class="l07d-nt" x="661" y="148">whole job</text>
</g>
<circle class="l07d-pk l07d-p0" cx="199" cy="70" r="5.5"/>
<circle class="l07d-pk l07d-p1" cx="479" cy="70" r="5.5"/>
<line class="l07d-front" x1="40" y1="203" x2="70" y2="203"/>
<text class="l07d-dim" x="78" y="207" style="text-anchor:start">person moves on</text>
<rect class="l07d-note-bad" x="208" y="195" width="22" height="16" rx="4"/>
<text class="l07d-dim" x="238" y="207" style="text-anchor:start">main risk</text>
</svg>
</div>
</div>
<!-- /diagram:identity-lifecycle -->

Read left to right: one person's access over time, with the main idea for each phase. An HR change, not an email to IT, can start each phase.

**Disabling the main account is not the whole job.** In Okta, deactivating a user removes their app access and stops their Okta sessions, but the user is deprovisioned from an app only if deprovisioning is enabled for that app. Okta's API reference calls deactivation destructive (apps that are deprovisioned might lose data such as email or files, and it cannot be recovered), while suspension stops sessions and keeps app assignments, so it is the temporary hold. Apps also keep their own sessions (OpenID Connect has a back-channel logout message just to tell an app to end one). Check each of these when someone leaves:

1. Accounts, including app accounts nothing syncs automatically.
2. Sessions and tokens that are still alive.
3. API keys the person created.
4. Shared passwords they knew, which need changing.
5. Delegated access, such as mailbox delegates and forwarding rules.
6. Devices, which must come back.

## Least privilege, reviews and non-human accounts

**Least privilege** means giving only the access needed for the job (NIST SP 800-53, AC-6). **Just-in-time access** applies it over time: a person holds a powerful role only while they need it. In Microsoft Entra PIM a role is "eligible" until activated and then expires.

An **access review** (or certification) is a regular check where an owner confirms who has what and removes what is no longer needed. SOC 2 expects access to be reviewed periodically (our source is secondary summaries; the AICPA text is not freely available). **Rubber-stamping** means approving the whole list without looking at what each line allows; the paperwork exists but the check did not happen.

Not every account is a person. A **service account** is an account for a program, such as a backup job. It needs a named owner. CIS Safeguard 5.5 says to keep an inventory of service accounts with the department owner, review date and purpose. A service account with no active owner is **orphaned**. CIS Safeguard 5.3 says to delete or disable any dormant accounts after 45 days of inactivity, where supported. An **API key** is a long-lived password for a program, so when its creator leaves, someone must still own it. Okta notes that an API token is deprovisioned if the user who created it is deactivated, which breaks any job relying on it.

## Your task: spot the problems

Here is a pretend access list. Today is 2026-10-01 and the company rule is that only IT staff may hold admin entitlements.

| Account | Owner | Owner employed? | Department | Entitlement | Last sign-in |
| --- | --- | --- | --- | --- | --- |
| ana.ruiz | ana.ruiz | yes | Sales | CRM user | 2026-09-30 |
| ben.okafor | ben.okafor | yes | Support | CRM admin | 2026-09-29 |
| dee.shah | dee.shah | yes | Support | CRM user | 2026-06-02 |
| svc-backup | none | not applicable | IT | storage write | 2026-09-30 |

Find the three problems and name each: **excess privilege**, **dormant account** and **orphaned service account**. The answers: ben.okafor, dee.shah and svc-backup, in that order. Next: lesson 8 pulls the whole course into a decision guide.
