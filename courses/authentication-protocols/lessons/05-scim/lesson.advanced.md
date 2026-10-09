# SCIM 2.0 provisioning

You are building or reviewing the service-provider (server) side of SCIM and need to know where the standard is firm, where it leaves room, and where the two big IdPs bend it. Facts checked 2026-10-06 against RFC 7642, RFC 7643 and RFC 7644 (section numbers below), Okta's SCIM 2.0 reference and rate-limit pages, and Microsoft Learn's Entra provisioning pages. Where Microsoft's own pages disagree, the text says so.

## Identifiers and what the RFCs leave to you

- **`id`** (RFC 7643 §3.1): issued by the server, unique across all its resources, stable, **non-reassignable**, never set by the client. `bulkId` is a reserved string. **`externalId`**: issued by the client, interpreted as scoped to its provisioning domain; the server does not enforce uniqueness.
- Okta's reference is inconsistent about `externalId`: its create example sends it in the `POST` body, a note under a second example says it was not in the `POST` and was generated and returned by the server, and the prose says Okta stores the server's unique ID as `externalId` in the Okta profile. The RFC says only the client issues it. Key your records on `id` and log what you receive. The SCIM match attribute (`userName` or `externalId`) is separate from the SSO account key (a persistent NameID in SAML, `iss` plus `sub` in OIDC, and `tid` plus `oid` in Entra, where `sub` is pairwise per application; lesson 1): the app must link them explicitly and never link a sign-in to an account on the email claim or attribute. A `userName` that happens to look like an email address is only the SCIM match attribute, not the SSO account key.
- **`userName`** (§4.1.1): required, unique across all Users, case-insensitive, and `readWrite`, so a rename keeps the `id`. Before comparing for uniqueness a provider MUST apply the PRECIS rules of RFC 7613 (RFC 7644 §5). Entra's SCIM validator checks that a `PATCH` can change its joining property (for example `userName`) and that a filter on the new value then finds the user.
- **`active`** (§4.1.1): boolean administrative status whose definitive meaning the provider decides. **DELETE** (RFC 7644 §3.6): the provider MAY keep the data but MUST return 404 for every later operation on that resource, MUST omit it from queries, and SHOULD NOT count it in conflict calculation, so a `POST` with the deleted `userName` SHOULD NOT get 409.
- Recommendation: model `active=false` as a reversible suspension that still appears in queries, and DELETE as removal that 404s and frees the `userName`. Entra's documentation fits this: it queries the target by its matching attribute, creates only when nothing matches, and wants an inactive user returned, with only a hard-deleted one absent.
- **Groups** (§4.2): `members[].value` holds the member's `id`; the `groups` attribute on a User is `readOnly`, so membership changes go through the Group resource. The extension URN `urn:ietf:params:scim:schemas:extension:enterprise:2.0:User` joins `schemas` when an extension attribute is addressed by its fully qualified name (RFC 7644 §3.5.2). Entra requires unique group `displayName`, which the RFC does not.

<!-- diagram:scim-identifiers -->
<div class="l05a-wrap" style="position:relative">
<input type="checkbox" id="l05a-pause" class="l05a-cb" /><label for="l05a-pause" class="l05a-btn"><span class="l05a-off">Pause animation</span><span class="l05a-on">Play animation</span></label>
<div class="l05a-box" style="overflow-x:auto">
<svg class="l05a-flow" viewBox="0 0 760 486" role="img" aria-labelledby="l05a-t l05a-d" style="width:760px;max-width:100%;min-width:699px;height:auto;display:block;margin:0 auto">
<title id="l05a-t">Identifier and membership rules in the SCIM User resource</title>
<desc id="l05a-d">A User resource and the rules the RFCs set for each part. id (RFC 7643 section 3.1) is issued by the server, unique across all its resources, stable, non-reassignable and never set by the client. externalId is issued by the client and the server does not enforce uniqueness. userName (section 4.1.1) is required, unique across all Users, case-insensitive and readWrite, so a rename keeps the id; before comparing for uniqueness a provider MUST apply the PRECIS rules of RFC 7613. active (section 4.1.1) is a boolean administrative status whose definitive meaning the provider decides. The groups attribute on a User is readOnly, so membership changes go through the Group resource, where members[].value holds the member's id. The diagram highlights each part in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
<style>
svg.l05a-flow{--ink:light-dark(#000000,#ffffff)}
.l05a-box{fill:var(--panel);stroke:var(--border-strong);stroke-width:1.5}
.l05a-hot{fill:var(--panel);stroke:var(--accent);stroke-width:2.5}
.l05a-ttl{fill:var(--ink);font:600 15px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l05a-sub{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l05a-life{stroke:var(--border-strong);stroke-width:1.5;stroke-dasharray:4 5}
.l05a-front{stroke:var(--accent);stroke-width:2;fill:none}
.l05a-back{stroke:var(--muted);stroke-width:2;stroke-dasharray:7 5;fill:none}
.l05a-bad{stroke:var(--bad);stroke-width:2;fill:none}
.l05a-main{fill:var(--ink);font:600 13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l05a-badt{fill:var(--ink)}
.l05a-dim{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l05a-badge{fill:var(--accent)}
.l05a-b-back{fill:var(--muted)}
.l05a-b-bad{fill:var(--bad)}
.l05a-b-good{fill:var(--good)}
.l05a-bt{fill:var(--on-accent);font:700 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l05a-note{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l05a-note-good{fill:var(--good-bg);stroke:var(--good);stroke-width:1.5}
.l05a-note-bad{fill:var(--bad-bg);stroke:var(--bad);stroke-width:1.5}
.l05a-nt{fill:var(--ink);font:500 12.5px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l05a-nest{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l05a-row{fill:var(--raised);stroke:var(--border-strong);stroke-width:1}
.l05a-ttlL{fill:var(--ink);font:600 14px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l05a-subL{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l05a-dimL{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l05a-dimR{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:end}
.l05a-conn{stroke:var(--accent);stroke-width:1.5;fill:none}
.l05a-edge{stroke:var(--border-strong);stroke-width:1.75;fill:none}
.l05a-hl{fill:none;stroke:var(--accent);stroke-width:3}
.l05a-hle{stroke:var(--accent);stroke-width:3;fill:none}
.l05a-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:24s;animation-timing-function:linear;animation-iteration-count:infinite}
.l05a-pk.l05a-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.l05a-pk.l05a-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.l05a-wrap{margin:20px 0}
@media (min-width:801px){.l05a-wrap{margin-left:-44px;margin-right:-44px}}
.l05a-g rect,.l05a-g line,.l05a-g path:not(.l05a-gl){opacity:.5;animation-duration:24s;animation-timing-function:linear;animation-iteration-count:infinite}
.l05a-h{opacity:0;animation-duration:24s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.l05a-flow:hover .l05a-g rect,svg.l05a-flow:hover .l05a-g line,svg.l05a-flow:hover .l05a-g path:not(.l05a-gl),svg.l05a-flow:hover .l05a-pk,svg.l05a-flow:hover .l05a-h{animation-play-state:paused}
.l05a-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.l05a-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.l05a-btn:hover{background:var(--hover)}
.l05a-cb:focus-visible + .l05a-btn{outline:2px solid var(--accent);outline-offset:2px}
.l05a-cb:checked + .l05a-btn .l05a-off,.l05a-cb:not(:checked) + .l05a-btn .l05a-on{display:none}
.l05a-cb:checked ~ .l05a-box .l05a-g rect,.l05a-cb:checked ~ .l05a-box .l05a-g line,.l05a-cb:checked ~ .l05a-box .l05a-g path:not(.l05a-gl),.l05a-cb:checked ~ .l05a-box .l05a-pk,.l05a-cb:checked ~ .l05a-box .l05a-h{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.l05a-g rect,.l05a-g line,.l05a-g path:not(.l05a-gl){animation:none;opacity:1}.l05a-pk{animation:none;display:none}.l05a-h{animation:none;opacity:0}.l05a-btn{display:none}}
@keyframes l05a-g0{0%{opacity:1}20%{opacity:1}20.01%,100%{opacity:.5}}
@keyframes l05a-h0{0%{opacity:1}20%{opacity:1}20.01%,100%{opacity:0}}
.l05a-g0 rect,.l05a-g0 line,.l05a-g0 path:not(.l05a-gl){animation-name:l05a-g0}.l05a-h0{animation-name:l05a-h0}
@keyframes l05a-g1{0%,19.99%{opacity:.5}20%{opacity:1}40%{opacity:1}40.01%,100%{opacity:.5}}
@keyframes l05a-h1{0%,19.99%{opacity:0}20%{opacity:1}40%{opacity:1}40.01%,100%{opacity:0}}
.l05a-g1 rect,.l05a-g1 line,.l05a-g1 path:not(.l05a-gl){animation-name:l05a-g1}.l05a-h1{animation-name:l05a-h1}
@keyframes l05a-g2{0%,39.99%{opacity:.5}40%{opacity:1}60%{opacity:1}60.01%,100%{opacity:.5}}
@keyframes l05a-h2{0%,39.99%{opacity:0}40%{opacity:1}60%{opacity:1}60.01%,100%{opacity:0}}
.l05a-g2 rect,.l05a-g2 line,.l05a-g2 path:not(.l05a-gl){animation-name:l05a-g2}.l05a-h2{animation-name:l05a-h2}
@keyframes l05a-g3{0%,59.99%{opacity:.5}60%{opacity:1}80%{opacity:1}80.01%,100%{opacity:.5}}
@keyframes l05a-h3{0%,59.99%{opacity:0}60%{opacity:1}80%{opacity:1}80.01%,100%{opacity:0}}
.l05a-g3 rect,.l05a-g3 line,.l05a-g3 path:not(.l05a-gl){animation-name:l05a-g3}.l05a-h3{animation-name:l05a-h3}
@keyframes l05a-g4{0%,79.99%{opacity:.5}80%{opacity:1}100%{opacity:1}100.01%,100%{opacity:.5}}
@keyframes l05a-h4{0%,79.99%{opacity:0}80%{opacity:1}100%{opacity:1}100.01%,100%{opacity:0}}
.l05a-g4 rect,.l05a-g4 line,.l05a-g4 path:not(.l05a-gl){animation-name:l05a-g4}.l05a-h4{animation-name:l05a-h4}
</style>
<defs>
<marker id="l05a-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="l05a-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="l05a-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<rect class="l05a-box" x="14" y="16" width="440" height="320" rx="9"/><text class="l05a-ttlL" x="28" y="37">User</text><text class="l05a-subL" x="28" y="54">RFC 7643</text>
<rect class="l05a-nest" x="26" y="62" width="416" height="46" rx="9"/><text class="l05a-ttlL" x="40" y="83">id</text><text class="l05a-subL" x="40" y="100">section 3.1</text>
<rect class="l05a-nest" x="26" y="116" width="416" height="46" rx="9"/><text class="l05a-ttlL" x="40" y="137">externalId</text><text class="l05a-subL" x="40" y="154">issued by the client</text>
<rect class="l05a-nest" x="26" y="170" width="416" height="46" rx="9"/><text class="l05a-ttlL" x="40" y="191">userName</text><text class="l05a-subL" x="40" y="208">section 4.1.1</text>
<rect class="l05a-nest" x="26" y="224" width="416" height="46" rx="9"/><text class="l05a-ttlL" x="40" y="245">active</text><text class="l05a-subL" x="40" y="262">section 4.1.1</text>
<rect class="l05a-nest" x="26" y="278" width="416" height="46" rx="9"/><text class="l05a-ttlL" x="40" y="299">groups</text><text class="l05a-subL" x="40" y="316">readOnly on a User</text>
<g class="l05a-g l05a-g0">
<path class="l05a-conn" d="M442,79 L462,79 L462,79 L470,79" marker-end="url(#l05a-m-front)"/>
<rect class="l05a-note-good" x="484" y="46" width="262" height="65" rx="8"/>
<text class="l05a-nt" x="615" y="68">Server-issued, unique across all its</text>
<text class="l05a-nt" x="615" y="84">resources, stable, non-reassignable,</text>
<text class="l05a-nt" x="615" y="102">never set by the client</text>
<circle class="l05a-badge l05a-b-good" cx="484" cy="79" r="12"/><text class="l05a-bt" x="484" y="83.5">1</text>
</g>
<g class="l05a-g l05a-g1">
<path class="l05a-conn" d="M442,133 L466,133 L466,154 L470,154" marker-end="url(#l05a-m-front)"/>
<rect class="l05a-note-good" x="484" y="122" width="262" height="65" rx="8"/>
<text class="l05a-nt" x="615" y="142">Scoped to its provisioning domain;</text>
<text class="l05a-nt" x="615" y="160">the server does not enforce</text>
<text class="l05a-nt" x="615" y="176">uniqueness</text>
<circle class="l05a-badge l05a-b-good" cx="484" cy="154" r="12"/><text class="l05a-bt" x="484" y="158.5">2</text>
</g>
<g class="l05a-g l05a-g2">
<path class="l05a-conn" d="M442,187 L470,187 L470,238 L470,238" marker-end="url(#l05a-m-front)"/>
<rect class="l05a-note-good" x="484" y="196" width="262" height="82" rx="8"/>
<text class="l05a-nt" x="615" y="218">Required, unique, case-insensitive,</text>
<text class="l05a-nt" x="615" y="234">readWrite, so a rename keeps the id.</text>
<text class="l05a-nt" x="615" y="252">Apply PRECIS (RFC 7613) before</text>
<text class="l05a-nt" x="615" y="268">comparing for uniqueness</text>
<circle class="l05a-badge l05a-b-good" cx="484" cy="238" r="12"/><text class="l05a-bt" x="484" y="242.0">3</text>
</g>
<g class="l05a-g l05a-g3">
<path class="l05a-conn" d="M442,241 L474,241 L474,321 L470,321" marker-end="url(#l05a-m-front)"/>
<rect class="l05a-note" x="484" y="288" width="262" height="65" rx="8"/>
<text class="l05a-nt" x="615" y="310">Boolean administrative status; the</text>
<text class="l05a-nt" x="615" y="326">provider decides its definitive</text>
<text class="l05a-nt" x="615" y="344">meaning</text>
<circle class="l05a-badge l05a-b-front" cx="484" cy="321" r="12"/><text class="l05a-bt" x="484" y="325.5">4</text>
</g>
<g class="l05a-g l05a-g4">
<path class="l05a-conn" d="M442,295 L462,295 L462,396 L470,396" marker-end="url(#l05a-m-front)"/>
<rect class="l05a-note-good" x="484" y="364" width="262" height="65" rx="8"/>
<text class="l05a-nt" x="615" y="384">Change membership through the Group</text>
<text class="l05a-nt" x="615" y="402">resource: members[].value holds the</text>
<text class="l05a-nt" x="615" y="418">member's id</text>
<circle class="l05a-badge l05a-b-good" cx="484" cy="396" r="12"/><text class="l05a-bt" x="484" y="400.5">5</text>
</g>
<g class="l05a-h l05a-h0">
<rect class="l05a-hl" x="26" y="62" width="416" height="46" rx="9"/>
</g>
<g class="l05a-h l05a-h1">
<rect class="l05a-hl" x="26" y="116" width="416" height="46" rx="9"/>
</g>
<g class="l05a-h l05a-h2">
<rect class="l05a-hl" x="26" y="170" width="416" height="46" rx="9"/>
</g>
<g class="l05a-h l05a-h3">
<rect class="l05a-hl" x="26" y="224" width="416" height="46" rx="9"/>
</g>
<g class="l05a-h l05a-h4">
<rect class="l05a-hl" x="26" y="278" width="416" height="46" rx="9"/>
</g>
<rect class="l05a-note" x="40" y="454" width="22" height="16" rx="4"/>
<text class="l05a-dim" x="70" y="466" style="text-anchor:start">left to the provider</text>
<rect class="l05a-note-good" x="232" y="454" width="22" height="16" rx="4"/>
<text class="l05a-dim" x="262" y="466" style="text-anchor:start">set by the RFC</text>
</svg>
</div>
</div>
<!-- /diagram:scim-identifiers -->

The five numbered notes mark which rules the RFCs set and which they leave to the provider. In this picture only `active` is marked as left to the provider, which decides what it definitively means. Membership is changed on the Group resource, because `groups` on a User is read-only.

<!-- diagram:scim-create-conflict -->
<div class="l05e-wrap" style="position:relative">
<input type="checkbox" id="l05e-pause" class="l05e-cb" /><label for="l05e-pause" class="l05e-btn"><span class="l05e-off">Pause animation</span><span class="l05e-on">Play animation</span></label>
<div class="l05e-box" style="overflow-x:auto">
<svg class="l05e-flow" viewBox="0 0 760 378" role="img" aria-labelledby="l05e-t l05e-d" style="width:760px;max-width:100%;min-width:699px;height:auto;display:block;margin:0 auto">
<title id="l05e-t">What a POST /Users with an existing userName should get</title>
<desc id="l05e-d">A decision for a create request. userName is unique across all Users and case-insensitive. If no record matches the userName, the create succeeds with 201 and a Location header. If a record matches but it was deleted, a POST with the deleted userName SHOULD NOT get 409, because a deleted resource should not count in conflict calculation. If a record matches and it is still there, the create MUST get 409 with the uniqueness rule; a replayed create after a lost 201 lands here. The diagram highlights each path in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
<style>
svg.l05e-flow{--ink:light-dark(#000000,#ffffff)}
.l05e-box{fill:var(--panel);stroke:var(--border-strong);stroke-width:1.5}
.l05e-hot{fill:var(--panel);stroke:var(--accent);stroke-width:2.5}
.l05e-ttl{fill:var(--ink);font:600 15px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l05e-sub{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l05e-life{stroke:var(--border-strong);stroke-width:1.5;stroke-dasharray:4 5}
.l05e-front{stroke:var(--accent);stroke-width:2;fill:none}
.l05e-back{stroke:var(--muted);stroke-width:2;stroke-dasharray:7 5;fill:none}
.l05e-bad{stroke:var(--bad);stroke-width:2;fill:none}
.l05e-main{fill:var(--ink);font:600 13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l05e-badt{fill:var(--ink)}
.l05e-dim{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l05e-badge{fill:var(--accent)}
.l05e-b-back{fill:var(--muted)}
.l05e-b-bad{fill:var(--bad)}
.l05e-b-good{fill:var(--good)}
.l05e-bt{fill:var(--on-accent);font:700 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l05e-note{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l05e-note-good{fill:var(--good-bg);stroke:var(--good);stroke-width:1.5}
.l05e-note-bad{fill:var(--bad-bg);stroke:var(--bad);stroke-width:1.5}
.l05e-nt{fill:var(--ink);font:500 12.5px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l05e-nest{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l05e-row{fill:var(--raised);stroke:var(--border-strong);stroke-width:1}
.l05e-ttlL{fill:var(--ink);font:600 14px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l05e-subL{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l05e-dimL{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l05e-dimR{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:end}
.l05e-conn{stroke:var(--accent);stroke-width:1.5;fill:none}
.l05e-edge{stroke:var(--border-strong);stroke-width:1.75;fill:none}
.l05e-hl{fill:none;stroke:var(--accent);stroke-width:3}
.l05e-hle{stroke:var(--accent);stroke-width:3;fill:none}
.l05e-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:16s;animation-timing-function:linear;animation-iteration-count:infinite}
.l05e-pk.l05e-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.l05e-pk.l05e-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.l05e-wrap{margin:20px 0}
@media (min-width:801px){.l05e-wrap{margin-left:-44px;margin-right:-44px}}
.l05e-g rect,.l05e-g line,.l05e-g path:not(.l05e-gl){opacity:.5;animation-duration:16s;animation-timing-function:linear;animation-iteration-count:infinite}
.l05e-h{opacity:0;animation-duration:16s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.l05e-flow:hover .l05e-g rect,svg.l05e-flow:hover .l05e-g line,svg.l05e-flow:hover .l05e-g path:not(.l05e-gl),svg.l05e-flow:hover .l05e-pk,svg.l05e-flow:hover .l05e-h{animation-play-state:paused}
.l05e-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.l05e-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.l05e-btn:hover{background:var(--hover)}
.l05e-cb:focus-visible + .l05e-btn{outline:2px solid var(--accent);outline-offset:2px}
.l05e-cb:checked + .l05e-btn .l05e-off,.l05e-cb:not(:checked) + .l05e-btn .l05e-on{display:none}
.l05e-cb:checked ~ .l05e-box .l05e-g rect,.l05e-cb:checked ~ .l05e-box .l05e-g line,.l05e-cb:checked ~ .l05e-box .l05e-g path:not(.l05e-gl),.l05e-cb:checked ~ .l05e-box .l05e-pk,.l05e-cb:checked ~ .l05e-box .l05e-h{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.l05e-g rect,.l05e-g line,.l05e-g path:not(.l05e-gl){animation:none;opacity:1}.l05e-pk{animation:none;display:none}.l05e-h{animation:none;opacity:0}.l05e-btn{display:none}}
@keyframes l05e-h0{0%{opacity:1}33.333%{opacity:1}33.343%,100%{opacity:0}}
.l05e-h0{animation-name:l05e-h0}
@keyframes l05e-h1{0%,33.323%{opacity:0}33.333%{opacity:1}66.667%{opacity:1}66.677%,100%{opacity:0}}
.l05e-h1{animation-name:l05e-h1}
@keyframes l05e-h2{0%,66.657%{opacity:0}66.667%{opacity:1}100%{opacity:1}100.01%,100%{opacity:0}}
.l05e-h2{animation-name:l05e-h2}
</style>
<defs>
<marker id="l05e-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="l05e-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="l05e-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<path class="l05e-edge" d="M380,89 L380,118 L232,118 L232,144" marker-end="url(#l05e-m-front)"/>
<text class="l05e-dimL" x="238" y="134">no</text>
<path class="l05e-edge" d="M380,89 L380,118 L445,118 L445,144" marker-end="url(#l05e-m-front)"/>
<text class="l05e-dimL" x="452" y="134">yes</text>
<path class="l05e-edge" d="M445,195 L445,224 L360,224 L360,250" marker-end="url(#l05e-m-front)"/>
<text class="l05e-dimL" x="366" y="240">yes</text>
<path class="l05e-edge" d="M445,195 L445,224 L508,224 L508,250" marker-end="url(#l05e-m-front)"/>
<text class="l05e-dimL" x="515" y="240">no</text>
<rect class="l05e-note-good" x="174" y="147" width="114" height="48" rx="8"/><text class="l05e-nt" x="232" y="168">201 Created</text><text class="l05e-nt" x="232" y="185">with Location</text>
<rect class="l05e-note-good" x="304" y="253" width="110" height="48" rx="8"/><text class="l05e-nt" x="360" y="274">SHOULD NOT</text><text class="l05e-nt" x="360" y="291">get a 409</text>
<rect class="l05e-note-bad" x="430" y="253" width="155" height="65" rx="8"/><text class="l05e-nt" x="508" y="274">409 (uniqueness).</text><text class="l05e-nt" x="508" y="291">A replay after a</text><text class="l05e-nt" x="508" y="308">lost 201 lands here</text>
<rect class="l05e-box" x="381" y="147" width="128" height="48" rx="8"/><text class="l05e-main" x="445" y="168">Was that</text><text class="l05e-nt" x="445" y="185">record deleted?</text>
<rect class="l05e-box" x="302" y="24" width="155" height="65" rx="8"/><text class="l05e-main" x="380" y="45">POST /Users: does a</text><text class="l05e-nt" x="380" y="62">record match the</text><text class="l05e-nt" x="380" y="79">userName?</text>
<g class="l05e-h l05e-h0">
<path class="l05e-hle" d="M380,89 L380,118 L232,118 L232,144" marker-end="url(#l05e-m-front)"/>
<rect class="l05e-hl" x="302" y="24" width="155" height="65" rx="8"/>
<rect class="l05e-hl" x="174" y="147" width="114" height="48" rx="8"/>
</g>
<g class="l05e-h l05e-h1">
<path class="l05e-hle" d="M380,89 L380,118 L445,118 L445,144" marker-end="url(#l05e-m-front)"/>
<path class="l05e-hle" d="M445,195 L445,224 L360,224 L360,250" marker-end="url(#l05e-m-front)"/>
<rect class="l05e-hl" x="302" y="24" width="155" height="65" rx="8"/>
<rect class="l05e-hl" x="381" y="147" width="128" height="48" rx="8"/>
<rect class="l05e-hl" x="304" y="253" width="110" height="48" rx="8"/>
</g>
<g class="l05e-h l05e-h2">
<path class="l05e-hle" d="M380,89 L380,118 L445,118 L445,144" marker-end="url(#l05e-m-front)"/>
<path class="l05e-hle" d="M445,195 L445,224 L508,224 L508,250" marker-end="url(#l05e-m-front)"/>
<rect class="l05e-hl" x="302" y="24" width="155" height="65" rx="8"/>
<rect class="l05e-hl" x="381" y="147" width="128" height="48" rx="8"/>
<rect class="l05e-hl" x="430" y="253" width="155" height="65" rx="8"/>
</g>
<line class="l05e-front" x1="40" y1="354" x2="70" y2="354"/>
<text class="l05e-dim" x="78" y="358" style="text-anchor:start">the path being traced</text>
<rect class="l05e-note-good" x="246" y="346" width="22" height="16" rx="4"/>
<text class="l05e-dim" x="276" y="358" style="text-anchor:start">no conflict</text>
<rect class="l05e-note-bad" x="380" y="346" width="22" height="16" rx="4"/>
<text class="l05e-dim" x="410" y="358" style="text-anchor:start">conflict</text>
</svg>
</div>
</div>
<!-- /diagram:scim-create-conflict -->

Three outcomes for a create whose `userName` may already exist. The middle question is the one the RFC answers with SHOULD NOT: a deleted record does not count in conflict calculation. Anything still there gets a 409, which includes a replayed create after a lost `201`.

## The life of an account

Okta and Entra differ most at steps 3 and 4.

<!-- diagram:scim-protocol -->
<div class="sc-wrap" style="position:relative">
<input type="checkbox" id="sc-pause" class="sc-cb" /><label for="sc-pause" class="sc-btn"><span class="sc-off">Pause animation</span><span class="sc-on">Play animation</span></label>
<div class="sc-box" style="overflow-x:auto">
<svg class="sc-flow" viewBox="0 0 760 803" role="img" aria-labelledby="sc-t sc-d" style="width:760px;max-width:100%;min-width:699px;height:auto;display:block;margin:0 auto">
<title id="sc-t">SCIM lifecycle on the server: where Okta and Entra differ</title>
<desc id="sc-d">Eight steps between an identity provider and your SCIM server, with a session or token issued before the update as a third lane. Step 1: Okta first runs a GET with a filter on userName, then POSTs the profile. Step 2: the server answers 201 with Location and meta.location, both SHALL, and the id comes back in that 201; Entra caches it. Step 3, group change: Okta PATCHes either a remove plus an add on members or a replace of the whole members list, or PUTs the group for Wizard apps, while Entra sends Add and Remove on members with the ids in value. Step 4, leaver: Okta sends a path-less replace of an object holding active false by PATCH, or a full PUT for Wizard apps; Entra sends op Replace with path active. Step 5, a failure mode: the PATCH succeeds but a session or token issued before it still validates. Step 6: no operation or endpoint in RFC 7644 ends a session, so revoke sessions, refresh tokens and API tokens when the update lands, or check active on every authenticated use. Step 7: Okta never sends DELETE for users; by default Entra sends DELETE only for a hard delete, 30 days after a soft delete. Step 8: return 204 for the DELETE, then 404 with the Error schema for every later request on that id. The diagram highlights each step in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
<style>
svg.sc-flow{--ink:light-dark(#000000,#ffffff)}
.sc-box{fill:var(--panel);stroke:var(--border-strong);stroke-width:1.5}
.sc-hot{fill:var(--panel);stroke:var(--accent);stroke-width:2.5}
.sc-ttl{fill:var(--ink);font:600 15px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.sc-sub{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.sc-life{stroke:var(--border-strong);stroke-width:1.5;stroke-dasharray:4 5}
.sc-front{stroke:var(--accent);stroke-width:2;fill:none}
.sc-back{stroke:var(--muted);stroke-width:2;stroke-dasharray:7 5;fill:none}
.sc-bad{stroke:var(--bad);stroke-width:2;fill:none}
.sc-main{fill:var(--ink);font:600 13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.sc-badt{fill:var(--ink)}
.sc-dim{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.sc-badge{fill:var(--accent)}
.sc-b-back{fill:var(--muted)}
.sc-b-bad{fill:var(--bad)}
.sc-b-good{fill:var(--good)}
.sc-bt{fill:var(--on-accent);font:700 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.sc-note{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.sc-note-good{fill:var(--good-bg);stroke:var(--good);stroke-width:1.5}
.sc-note-bad{fill:var(--bad-bg);stroke:var(--bad);stroke-width:1.5}
.sc-nt{fill:var(--ink);font:500 12.5px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.sc-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:46s;animation-timing-function:linear;animation-iteration-count:infinite}
.sc-pk.sc-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.sc-pk.sc-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.sc-wrap{margin:20px 0}
@media (min-width:801px){.sc-wrap{margin-left:-44px;margin-right:-44px}}
.sc-g rect,.sc-g line,.sc-g path:not(.sc-gl){opacity:.5;animation-duration:46s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.sc-flow:hover .sc-g rect,svg.sc-flow:hover .sc-g line,svg.sc-flow:hover .sc-g path:not(.sc-gl),svg.sc-flow:hover .sc-pk{animation-play-state:paused}
.sc-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.sc-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.sc-btn:hover{background:var(--hover)}
.sc-cb:focus-visible + .sc-btn{outline:2px solid var(--accent);outline-offset:2px}
.sc-cb:checked + .sc-btn .sc-off,.sc-cb:not(:checked) + .sc-btn .sc-on{display:none}
.sc-cb:checked ~ .sc-box .sc-g rect,.sc-cb:checked ~ .sc-box .sc-g line,.sc-cb:checked ~ .sc-box .sc-g path:not(.sc-gl),.sc-cb:checked ~ .sc-box .sc-pk{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.sc-g rect,.sc-g line,.sc-g path:not(.sc-gl){animation:none;opacity:1}.sc-pk{animation:none;display:none}.sc-btn{display:none}}
@keyframes sc-g0{0%{opacity:1}13.043%{opacity:1}13.053%,100%{opacity:.5}}
@keyframes sc-p0{0%,-0.01%{opacity:0;transform:translateX(0)}0%{opacity:1;transform:translateX(0)}10.435%{opacity:1;transform:translateX(236px)}13.043%{opacity:1;transform:translateX(236px)}13.053%,100%{opacity:0;transform:translateX(236px)}}
.sc-g0 rect,.sc-g0 line,.sc-g0 path:not(.sc-gl){animation-name:sc-g0}.sc-p0{animation-name:sc-p0}
@keyframes sc-g1{0%,13.033%{opacity:.5}13.043%{opacity:1}26.087%{opacity:1}26.097%,100%{opacity:.5}}
@keyframes sc-p1{0%,13.033%{opacity:0;transform:translateX(0)}13.043%{opacity:1;transform:translateX(0)}23.478%{opacity:1;transform:translateX(-236px)}26.087%{opacity:1;transform:translateX(-236px)}26.097%,100%{opacity:0;transform:translateX(-236px)}}
.sc-g1 rect,.sc-g1 line,.sc-g1 path:not(.sc-gl){animation-name:sc-g1}.sc-p1{animation-name:sc-p1}
@keyframes sc-g2{0%,26.077%{opacity:.5}26.087%{opacity:1}39.13%{opacity:1}39.14%,100%{opacity:.5}}
@keyframes sc-p2{0%,26.077%{opacity:0;transform:translateX(0)}26.087%{opacity:1;transform:translateX(0)}36.522%{opacity:1;transform:translateX(236px)}39.13%{opacity:1;transform:translateX(236px)}39.14%,100%{opacity:0;transform:translateX(236px)}}
.sc-g2 rect,.sc-g2 line,.sc-g2 path:not(.sc-gl){animation-name:sc-g2}.sc-p2{animation-name:sc-p2}
@keyframes sc-g3{0%,39.12%{opacity:.5}39.13%{opacity:1}52.174%{opacity:1}52.184%,100%{opacity:.5}}
@keyframes sc-p3{0%,39.12%{opacity:0;transform:translateX(0)}39.13%{opacity:1;transform:translateX(0)}49.565%{opacity:1;transform:translateX(236px)}52.174%{opacity:1;transform:translateX(236px)}52.184%,100%{opacity:0;transform:translateX(236px)}}
.sc-g3 rect,.sc-g3 line,.sc-g3 path:not(.sc-gl){animation-name:sc-g3}.sc-p3{animation-name:sc-p3}
@keyframes sc-g4{0%,52.164%{opacity:.5}52.174%{opacity:1}65.217%{opacity:1}65.227%,100%{opacity:.5}}
@keyframes sc-p4{0%,52.164%{opacity:0;transform:translateX(0)}52.174%{opacity:1;transform:translateX(0)}62.609%{opacity:1;transform:translateX(-236px)}65.217%{opacity:1;transform:translateX(-236px)}65.227%,100%{opacity:0;transform:translateX(-236px)}}
.sc-g4 rect,.sc-g4 line,.sc-g4 path:not(.sc-gl){animation-name:sc-g4}.sc-p4{animation-name:sc-p4}
@keyframes sc-g5{0%,65.207%{opacity:.5}65.217%{opacity:1}73.913%{opacity:1}73.923%,100%{opacity:.5}}
.sc-g5 rect,.sc-g5 line,.sc-g5 path:not(.sc-gl){animation-name:sc-g5}
@keyframes sc-g6{0%,73.903%{opacity:.5}73.913%{opacity:1}86.957%{opacity:1}86.967%,100%{opacity:.5}}
@keyframes sc-p6{0%,73.903%{opacity:0;transform:translateX(0)}73.913%{opacity:1;transform:translateX(0)}84.348%{opacity:1;transform:translateX(236px)}86.957%{opacity:1;transform:translateX(236px)}86.967%,100%{opacity:0;transform:translateX(236px)}}
.sc-g6 rect,.sc-g6 line,.sc-g6 path:not(.sc-gl){animation-name:sc-g6}.sc-p6{animation-name:sc-p6}
@keyframes sc-g7{0%,86.947%{opacity:.5}86.957%{opacity:1}100%{opacity:1}100.01%,100%{opacity:.5}}
@keyframes sc-p7{0%,86.947%{opacity:0;transform:translateX(0)}86.957%{opacity:1;transform:translateX(0)}97.391%{opacity:1;transform:translateX(-236px)}100%{opacity:1;transform:translateX(-236px)}100.01%,100%{opacity:0;transform:translateX(-236px)}}
.sc-g7 rect,.sc-g7 line,.sc-g7 path:not(.sc-gl){animation-name:sc-g7}.sc-p7{animation-name:sc-p7}
</style>
<defs>
<marker id="sc-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="sc-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="sc-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<line class="sc-life" x1="110" y1="72" x2="110" y2="751"/>
<line class="sc-life" x1="380" y1="72" x2="380" y2="751"/>
<line class="sc-life" x1="650" y1="72" x2="650" y2="751"/>
<rect class="sc-box" x="20" y="10" width="180" height="62" rx="10"/><text class="sc-ttl" x="110" y="36">Identity provider</text><text class="sc-sub" x="110" y="56">Okta or Entra</text>
<rect class="sc-hot" x="290" y="10" width="180" height="62" rx="10"/><text class="sc-ttl" x="380" y="36">Your SCIM server</text><text class="sc-sub" x="380" y="56">service provider</text>
<rect class="sc-box" x="560" y="10" width="180" height="62" rx="10"/><text class="sc-ttl" x="650" y="36">Session or token</text><text class="sc-sub" x="650" y="56">issued before the PATCH</text>
<g class="sc-g sc-g0">
<text class="sc-main" x="245" y="108">GET filter, then POST</text>
<text class="sc-dim" x="245" y="124">Okta: lookup on userName first</text>
<line class="sc-front" x1="124" y1="138" x2="366" y2="138" marker-end="url(#sc-m-front)"/>
<circle class="sc-badge sc-b-front" cx="110" cy="138" r="12"/><text class="sc-bt" x="110" y="142.5">1</text>
</g>
<g class="sc-g sc-g1">
<text class="sc-main" x="245" y="178">201 + Location + meta.location</text>
<text class="sc-dim" x="245" y="194">the id comes back; Entra caches it</text>
<line class="sc-back" x1="366" y1="208" x2="124" y2="208" marker-end="url(#sc-m-back)"/>
<circle class="sc-badge sc-b-back" cx="380" cy="208" r="12"/><text class="sc-bt" x="380" y="212.5">2</text>
</g>
<g class="sc-g sc-g2">
<text class="sc-main" x="245" y="248">Group change (PATCH; Wizard: PUT)</text>
<text class="sc-dim" x="245" y="264">Okta: remove + add, or replace</text>
<text class="sc-dim" x="245" y="280">Entra: Add and Remove, ids in value</text>
<line class="sc-front" x1="124" y1="294" x2="366" y2="294" marker-end="url(#sc-m-front)"/>
<circle class="sc-badge sc-b-front" cx="110" cy="294" r="12"/><text class="sc-bt" x="110" y="298.5">3</text>
</g>
<g class="sc-g sc-g3">
<text class="sc-main" x="245" y="334">Leaver: PATCH active = false</text>
<text class="sc-dim" x="245" y="350">Okta: replace, no path (Wizard: PUT)</text>
<text class="sc-dim" x="245" y="366">Entra: Replace with path active</text>
<line class="sc-front" x1="124" y1="380" x2="366" y2="380" marker-end="url(#sc-m-front)"/>
<circle class="sc-badge sc-b-front" cx="110" cy="380" r="12"/><text class="sc-bt" x="110" y="384.5">4</text>
</g>
<g class="sc-g sc-g4">
<text class="sc-main sc-badt" x="515" y="420">use of that credential</text>
<text class="sc-dim" x="515" y="436">still validates</text>
<line class="sc-bad" x1="636" y1="450" x2="394" y2="450" marker-end="url(#sc-m-bad)"/>
<circle class="sc-badge sc-b-bad" cx="650" cy="450" r="12"/><text class="sc-bt" x="650" y="454.5">5</text>
</g>
<g class="sc-g sc-g5">
<rect class="sc-note-good" x="243" y="484" width="274" height="65" rx="8"/>
<text class="sc-nt" x="380" y="505">no RFC 7644 operation ends a session:</text>
<text class="sc-nt" x="380" y="522">revoke on the update, or check active</text>
<text class="sc-nt" x="380" y="539">on every authenticated use</text>
<circle class="sc-badge sc-b-good" cx="243" cy="516" r="12"/><text class="sc-bt" x="243" y="521.0">6</text>
</g>
<g class="sc-g sc-g6">
<text class="sc-main" x="245" y="583">DELETE</text>
<text class="sc-dim" x="245" y="599">Okta: never sent for users</text>
<text class="sc-dim" x="245" y="615">Entra: default, hard delete only</text>
<line class="sc-front" x1="124" y1="629" x2="366" y2="629" marker-end="url(#sc-m-front)"/>
<circle class="sc-badge sc-b-front" cx="110" cy="629" r="12"/><text class="sc-bt" x="110" y="633.5">7</text>
</g>
<g class="sc-g sc-g7">
<text class="sc-main" x="245" y="669">204, then 404 + Error schema</text>
<text class="sc-dim" x="245" y="685">for every later request on that id</text>
<line class="sc-back" x1="366" y1="699" x2="124" y2="699" marker-end="url(#sc-m-back)"/>
<circle class="sc-badge sc-b-back" cx="380" cy="699" r="12"/><text class="sc-bt" x="380" y="703.5">8</text>
</g>
<circle class="sc-pk sc-p0" cx="130" cy="138" r="5.5"/>
<circle class="sc-pk sc-p1 sc-pkback" cx="360" cy="208" r="5.5"/>
<circle class="sc-pk sc-p2" cx="130" cy="294" r="5.5"/>
<circle class="sc-pk sc-p3" cx="130" cy="380" r="5.5"/>
<circle class="sc-pk sc-p4 sc-pkbad" cx="630" cy="450" r="5.5"/>
<circle class="sc-pk sc-p6" cx="130" cy="629" r="5.5"/>
<circle class="sc-pk sc-p7 sc-pkback" cx="360" cy="699" r="5.5"/>
<line class="sc-front" x1="40" y1="779" x2="70" y2="779"/>
<text class="sc-dim" x="78" y="783" style="text-anchor:start">request</text>
<line class="sc-back" x1="156" y1="779" x2="186" y2="779"/>
<text class="sc-dim" x="194" y="783" style="text-anchor:start">response</text>
<line class="sc-bad" x1="279" y1="779" x2="309" y2="779"/>
<text class="sc-dim" x="317" y="783" style="text-anchor:start">failure mode</text>
<rect class="sc-note-good" x="427" y="771" width="22" height="16" rx="4"/>
<text class="sc-dim" x="457" y="783" style="text-anchor:start">what your server must do</text>
</svg>
</div>
</div>
<!-- /diagram:scim-protocol -->

The numbers 1 to 8 match the list below. Step 5 is the failure mode. Steps 3 and 4 list what Okta and Entra each send.

1. **Joiner.** Okta first runs `GET /Users?filter=userName eq "..."`, then `POST`s the profile. Its body carries a `password` placeholder even when password sync is off. The server answers `201` with `Location` and `meta.location` (both SHALL) and should include the full representation in the body (RFC 7644 §3.3).
2. The `id` comes back in that `201`; Entra caches it and uses it for every later operation on the user.
3. **Mover and groups.** Okta's OIN apps `PATCH` groups, either `remove members[value eq "..."]` plus `add members`, or a `replace` of the whole `members` list; apps built with Okta's App Integration Wizard `PUT` the group. Entra sends `Add` and `Remove` on `members` with the ids in `value`, expects `204` and advises against returning the member list.
4. **Leaver.** Okta sends `{"op":"replace","value":{"active":false}}` (no path) by `PATCH`, or a full `PUT` for Wizard apps. Entra sends `op` `Replace` with `path` `active`.
5. The `PATCH` succeeds but a session or token issued before it still validates.
6. None of the operations or endpoints in RFC 7644 (§3.2, Table 2) ends a session; the RFC mentions sessions only when discussing how a client authenticates. Revoke sessions, refresh tokens and API tokens when the update lands, or check `active` on every authenticated use; do both for long-lived credentials.
7. Okta never sends `DELETE` for users, and nothing is sent when you delete an already deactivated profile. By default Entra sends `DELETE` only for a hard delete, 30 days after a soft delete. Microsoft adds two exceptions: when the target app does not support soft-delete, the service sends `DELETE` for the soft-delete, unassign and out-of-scope events as well, and a few gallery apps are set up that way and not configurable by customers. A customer can also leave "Delete" unticked in the target object actions, so that nothing is sent on a hard delete.
8. Return `204` for the DELETE, then `404` with the Error schema for every later request on that `id`.

## PATCH, PUT, ETags and bulk

- **PUT** MUST be supported; **PATCH** is optional but SHOULD be offered because groups can be large (§3.5). Entra provisions groups only if you support PATCH. On PUT, `readOnly` values are ignored, an `immutable` value that differs SHOULD get `400 mutability`, and omitted `readWrite` attributes MAY be cleared or defaulted.
- A PATCH request is **atomic** and its operations apply in order (§3.5.2). `remove` requires a `path` (else `400 noTarget`); `replace` on a missing path acts as `add`; a `replace` whose `valuePath` filter matches nothing is `400 noTarget`; removing a non-member succeeds with no change. SCIM drops JSON Patch's array indexes and `move`.
- **Dialects.** Entra emits `Add`, `Replace`, `Remove` and says not to require a case-sensitive match. Its documented group removal is `Remove` on `members` with the ids in `value`, and a server that rejects it cannot take removals from Entra by default. The RFC (§3.5.2.2) defines `remove` by `path` alone: a multi-valued target with no filter has the attribute and all its values removed, and its own "Remove all members of a group" example is `remove` with `path` `members` and no `value`. It does not define a `value` on `remove`, so Entra's form (a bare `members` path plus a `value` list) is outside what the RFC specifies, and a handler that applied the path-only rule to it would empty the group. Honour the ids in `value` when present; empty the group only for a path-only `remove`. Entra's compatibility page lists the RFC-shaped `remove members[value eq "..."]` behind a tenant URL flag (`aadOptscim062020`) and lists the fix as not done, with the date to be decided.
- The same compatibility page shows the default deactivation as `Replace` `active` with the **string** `"False"`, a boolean `false` behind the flag, and, behind the flag, one path-less `replace` whose value object uses dotted keys such as `name.givenName`. Microsoft's main SCIM page shows a boolean with a capitalised `Replace`. Accept every variant.
- **ETags** (RFC 7643 §3.1; RFC 7644 §3.14): `meta.version` must equal the `ETag` header, weak validators are prefixed `W/`, and clients MAY send `If-Match` on PUT and PATCH. Table 8 lists 409 for a version mismatch and 412 for "resource has changed"; pick one and document it. The Okta and Entra pages I read do not mention `If-Match`, so I could not verify either IdP sends it.
- **Bulk** (§3.7) is optional: `failOnErrors`, client `bulkId`, and `maxOperations` and `maxPayloadSize` in `ServiceProviderConfig`. Entra's page says it does not support `/Bulk`; the Okta pages I read do not mention it.

<!-- diagram:scim-patch-remove -->
<div class="l05d-wrap" style="position:relative">
<input type="checkbox" id="l05d-pause" class="l05d-cb" /><label for="l05d-pause" class="l05d-btn"><span class="l05d-off">Pause animation</span><span class="l05d-on">Play animation</span></label>
<div class="l05d-box" style="overflow-x:auto">
<svg class="l05d-flow" viewBox="0 0 760 272" role="img" aria-labelledby="l05d-t l05d-d" style="width:760px;max-width:100%;min-width:699px;height:auto;display:block;margin:0 auto">
<title id="l05d-t">Handling a remove operation on a Group</title>
<desc id="l05d-d">A decision on what a PATCH remove carries, matching the op without regard to case because Entra sends Remove. A remove with no path is a 400 noTarget. A remove whose path is members with a filter on one value, the form Okta sends, removes that member. A remove whose path is members with the ids in a value list, Entra's form, is outside what RFC 7644 specifies: honour the ids in value. A remove whose path is members with no value is the RFC's path-only rule and empties the group, so decide which clients may reach it. The diagram highlights each path in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
<style>
svg.l05d-flow{--ink:light-dark(#000000,#ffffff)}
.l05d-box{fill:var(--panel);stroke:var(--border-strong);stroke-width:1.5}
.l05d-hot{fill:var(--panel);stroke:var(--accent);stroke-width:2.5}
.l05d-ttl{fill:var(--ink);font:600 15px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l05d-sub{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l05d-life{stroke:var(--border-strong);stroke-width:1.5;stroke-dasharray:4 5}
.l05d-front{stroke:var(--accent);stroke-width:2;fill:none}
.l05d-back{stroke:var(--muted);stroke-width:2;stroke-dasharray:7 5;fill:none}
.l05d-bad{stroke:var(--bad);stroke-width:2;fill:none}
.l05d-main{fill:var(--ink);font:600 13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l05d-badt{fill:var(--ink)}
.l05d-dim{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l05d-badge{fill:var(--accent)}
.l05d-b-back{fill:var(--muted)}
.l05d-b-bad{fill:var(--bad)}
.l05d-b-good{fill:var(--good)}
.l05d-bt{fill:var(--on-accent);font:700 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l05d-note{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l05d-note-good{fill:var(--good-bg);stroke:var(--good);stroke-width:1.5}
.l05d-note-bad{fill:var(--bad-bg);stroke:var(--bad);stroke-width:1.5}
.l05d-nt{fill:var(--ink);font:500 12.5px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l05d-nest{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l05d-row{fill:var(--raised);stroke:var(--border-strong);stroke-width:1}
.l05d-ttlL{fill:var(--ink);font:600 14px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l05d-subL{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l05d-dimL{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l05d-dimR{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:end}
.l05d-conn{stroke:var(--accent);stroke-width:1.5;fill:none}
.l05d-edge{stroke:var(--border-strong);stroke-width:1.75;fill:none}
.l05d-hl{fill:none;stroke:var(--accent);stroke-width:3}
.l05d-hle{stroke:var(--accent);stroke-width:3;fill:none}
.l05d-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:18s;animation-timing-function:linear;animation-iteration-count:infinite}
.l05d-pk.l05d-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.l05d-pk.l05d-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.l05d-wrap{margin:20px 0}
@media (min-width:801px){.l05d-wrap{margin-left:-44px;margin-right:-44px}}
.l05d-g rect,.l05d-g line,.l05d-g path:not(.l05d-gl){opacity:.5;animation-duration:18s;animation-timing-function:linear;animation-iteration-count:infinite}
.l05d-h{opacity:0;animation-duration:18s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.l05d-flow:hover .l05d-g rect,svg.l05d-flow:hover .l05d-g line,svg.l05d-flow:hover .l05d-g path:not(.l05d-gl),svg.l05d-flow:hover .l05d-pk,svg.l05d-flow:hover .l05d-h{animation-play-state:paused}
.l05d-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.l05d-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.l05d-btn:hover{background:var(--hover)}
.l05d-cb:focus-visible + .l05d-btn{outline:2px solid var(--accent);outline-offset:2px}
.l05d-cb:checked + .l05d-btn .l05d-off,.l05d-cb:not(:checked) + .l05d-btn .l05d-on{display:none}
.l05d-cb:checked ~ .l05d-box .l05d-g rect,.l05d-cb:checked ~ .l05d-box .l05d-g line,.l05d-cb:checked ~ .l05d-box .l05d-g path:not(.l05d-gl),.l05d-cb:checked ~ .l05d-box .l05d-pk,.l05d-cb:checked ~ .l05d-box .l05d-h{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.l05d-g rect,.l05d-g line,.l05d-g path:not(.l05d-gl){animation:none;opacity:1}.l05d-pk{animation:none;display:none}.l05d-h{animation:none;opacity:0}.l05d-btn{display:none}}
@keyframes l05d-h0{0%{opacity:1}25%{opacity:1}25.01%,100%{opacity:0}}
.l05d-h0{animation-name:l05d-h0}
@keyframes l05d-h1{0%,24.99%{opacity:0}25%{opacity:1}50%{opacity:1}50.01%,100%{opacity:0}}
.l05d-h1{animation-name:l05d-h1}
@keyframes l05d-h2{0%,49.99%{opacity:0}50%{opacity:1}75%{opacity:1}75.01%,100%{opacity:0}}
.l05d-h2{animation-name:l05d-h2}
@keyframes l05d-h3{0%,74.99%{opacity:0}75%{opacity:1}100%{opacity:1}100.01%,100%{opacity:0}}
.l05d-h3{animation-name:l05d-h3}
</style>
<defs>
<marker id="l05d-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="l05d-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="l05d-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<path class="l05d-edge" d="M380,89 L380,118 L151,118 L151,144" marker-end="url(#l05d-m-front)"/>
<text class="l05d-dimL" x="158" y="134">no path</text>
<path class="l05d-edge" d="M380,89 L380,118 L282,118 L282,144" marker-end="url(#l05d-m-front)"/>
<text class="l05d-dimL" x="290" y="134">members[value eq ...]</text>
<path class="l05d-edge" d="M380,89 L380,118 L433,118 L433,144" marker-end="url(#l05d-m-front)"/>
<text class="l05d-dimL" x="440" y="134">members + value list</text>
<path class="l05d-edge" d="M380,89 L380,118 L594,118 L594,144" marker-end="url(#l05d-m-front)"/>
<text class="l05d-dimL" x="600" y="134">members, no value</text>
<rect class="l05d-note-bad" x="96" y="147" width="110" height="31" rx="8"/><text class="l05d-nt" x="151" y="168">400 noTarget</text>
<rect class="l05d-note" x="222" y="147" width="121" height="48" rx="8"/><text class="l05d-nt" x="282" y="168">Remove that id</text><text class="l05d-nt" x="282" y="185">(Okta's form)</text>
<rect class="l05d-note" x="359" y="147" width="148" height="65" rx="8"/><text class="l05d-nt" x="433" y="168">Remove the ids</text><text class="l05d-nt" x="433" y="185">in value (Entra's</text><text class="l05d-nt" x="433" y="202">form; outside RFC)</text>
<rect class="l05d-note-bad" x="523" y="147" width="141" height="65" rx="8"/><text class="l05d-nt" x="594" y="168">Empties the group</text><text class="l05d-nt" x="594" y="185">(RFC path-only</text><text class="l05d-nt" x="594" y="202">rule): who may?</text>
<rect class="l05d-box" x="310" y="24" width="141" height="65" rx="8"/><text class="l05d-main" x="380" y="45">PATCH remove on a</text><text class="l05d-nt" x="380" y="62">Group (op in any</text><text class="l05d-nt" x="380" y="79">case): what path?</text>
<g class="l05d-h l05d-h0">
<path class="l05d-hle" d="M380,89 L380,118 L151,118 L151,144" marker-end="url(#l05d-m-front)"/>
<rect class="l05d-hl" x="310" y="24" width="141" height="65" rx="8"/>
<rect class="l05d-hl" x="96" y="147" width="110" height="31" rx="8"/>
</g>
<g class="l05d-h l05d-h1">
<path class="l05d-hle" d="M380,89 L380,118 L282,118 L282,144" marker-end="url(#l05d-m-front)"/>
<rect class="l05d-hl" x="310" y="24" width="141" height="65" rx="8"/>
<rect class="l05d-hl" x="222" y="147" width="121" height="48" rx="8"/>
</g>
<g class="l05d-h l05d-h2">
<path class="l05d-hle" d="M380,89 L380,118 L433,118 L433,144" marker-end="url(#l05d-m-front)"/>
<rect class="l05d-hl" x="310" y="24" width="141" height="65" rx="8"/>
<rect class="l05d-hl" x="359" y="147" width="148" height="65" rx="8"/>
</g>
<g class="l05d-h l05d-h3">
<path class="l05d-hle" d="M380,89 L380,118 L594,118 L594,144" marker-end="url(#l05d-m-front)"/>
<rect class="l05d-hl" x="310" y="24" width="141" height="65" rx="8"/>
<rect class="l05d-hl" x="523" y="147" width="141" height="65" rx="8"/>
</g>
<line class="l05d-front" x1="40" y1="248" x2="70" y2="248"/>
<text class="l05d-dim" x="78" y="252" style="text-anchor:start">the path being traced</text>
<rect class="l05d-note" x="246" y="240" width="22" height="16" rx="4"/>
<text class="l05d-dim" x="276" y="252" style="text-anchor:start">removes only what is named</text>
<rect class="l05d-note-bad" x="476" y="240" width="22" height="16" rx="4"/>
<text class="l05d-dim" x="506" y="252" style="text-anchor:start">the problem</text>
</svg>
</div>
</div>
<!-- /diagram:scim-patch-remove -->

Branch on what the `remove` carries. Okta's and Entra's forms differ in where the id sits (inside the path filter, or in `value`), while the path-only form is the RFC reading and empties the group, so which clients may reach that last leaf is a decision to write down.

## Queries, pagination and discovery

- **Filter** support is optional. Okta needs `eq` on its identifier and on group `displayName`; Entra uses only `eq` and `and`, and every attribute you treat as unique must be filterable. An unknown operator is `400 invalidFilter`; no match is `200` with `totalResults: 0` (§3.4.2), and Okta also accepts a `404` Error.
- **Pagination** is `startIndex` (1-based) and `count`, stateless: clients MUST expect inconsistent results, and the server MUST NOT return more than `count`. `ListResponse` defines `totalResults`, `Resources`, `startIndex` and `itemsPerPage`, no cursor. Okta pages with `count=100`, advances `startIndex` by 100, wants integers not strings, and requires the same ordering for any `count` and `startIndex`. My recommendation, not from a source: order by an immutable key, because `lastModified` moves a user on every edit.
- **Discovery** (§4, RFC 7643 §5-6): `/ServiceProviderConfig` reports `patch`, `bulk`, `filter`, `changePassword`, `sort`, `etag` and `authenticationSchemes` (SHOULD be readable without authentication); `/ResourceTypes` and `/Schemas` ignore paging, and a `filter` there SHOULD get 403. Entra reads `/Schemas` on gallery apps, not custom ones, and only adds attributes.

## Authentication, retries and failure

- RFC 7644 §2 defines no scheme; servers MUST support TLS 1.2 (§7.2). **Bearer tokens MUST have a limited lifetime** (§7.4, "Bearer Token and Cookie Considerations"). I read this as the credential the SCIM client presents; the RFC does not say whose token it means, and I do not read it as a rule about your users' tokens. Entra's *Secret Token* field takes a "long-lived bearer token" and warns that test tokens do not belong in production. Okta accepts OAuth 2.0 authorization code, Basic or an Authorization header, and refreshes only if your authorization server issues refresh tokens. Okta forbids `_` in a base URL, and one server can serve many Okta orgs with a per-org base URL.
- **No idempotency.** RFC 7643 and 7644 define no idempotency key. A replayed create after a lost `201` hits the uniqueness rule and MUST get `409` (§3.3); do not silently upsert, and expect clients to resolve it with a lookup.
- **429.** RFC 7644 never mentions it. Okta waits integer `Retry-After` seconds, else five minutes, doubles each time and fails the task after 10 attempts; an HTTP-date value is ignored. Entra retries failed items on later cycles with less frequency, quarantines the job when most calls fail, and disables it after four weeks.

## Conformance pitfalls

- **Shape.** Okta wants `totalResults`, `startIndex` and `itemsPerPage` as integers, treats an empty body on create as a failed provisioning, and needs `GET /Groups/{id}` to return `members` when no query parameters are given. Entra wants `id` in every response except an empty `ListResponse`, `application/scim+json` on every response, and `excludedAttributes=members` honoured on group queries.
- **Fidelity.** Entra says to store values exactly as sent, rejecting bad ones with an actionable error rather than normalising them, and `type` values inside a multi-valued attribute such as `emails` must be unique.

## Your task

Local, run on this machine, a toy that normalises both group dialects and stays atomic. The output is real.

```python
import copy, re
def apply_patch(group, ops):  # TOY: members and displayName only
    g = copy.deepcopy(group)  # RFC 7644 3.5.2: atomic, so edit a copy and return it only on success
    for o in ops:
        op, path = o["op"].lower(), o.get("path", "")  # Entra sends Add/Remove/Replace
        m = re.fullmatch(r'members\[value eq "([^"]+)"\]', path)
        if op == "remove" and m: ids = [m[1]]  # Okta style: the id is inside the path filter
        elif op == "remove" and path == "members":  # Entra style: ids in value; RFC 3.5.2.2: no value and no filter removes all values
            ids = [v["value"] for v in o["value"]] if "value" in o else [x["value"] for x in g["members"]]
        elif op == "add" and path == "members":
            have = {x["value"] for x in g["members"]}
            g["members"] += [{"value": v["value"]} for v in o["value"] if v["value"] not in have]; continue
        elif op == "replace" and path == "displayName": g["displayName"] = o["value"]; continue
        else: raise ValueError(f"400 noTarget/invalidPath: {o['op']} {path!r}")
        g["members"] = [x for x in g["members"] if x["value"] not in ids]  # a non-member removal changes nothing
    return g
G = {"displayName": "eng", "members": [{"value": "u1"}, {"value": "u2"}]}
print("okta :", apply_patch(G, [{"op": "remove", "path": 'members[value eq "u1"]'}, {"op": "add", "path": "members", "value": [{"value": "u3"}]}]))
print("entra:", apply_patch(G, [{"op": "Remove", "path": "members", "value": [{"value": "u2"}]}]))
print("path-only remove empties the group:", apply_patch(G, [{"op": "remove", "path": "members"}])["members"])
print("non-member removal is a no-op:", apply_patch(G, [{"op": "remove", "path": 'members[value eq "u9"]'}]) == G)
try: apply_patch(G, [{"op": "add", "path": "members", "value": [{"value": "u4"}]}, {"op": "move", "path": "x"}])
except ValueError as e: print("rejected:", e, "| group unchanged:", G["members"])
```

```text
okta : {'displayName': 'eng', 'members': [{'value': 'u2'}, {'value': 'u3'}]}
entra: {'displayName': 'eng', 'members': [{'value': 'u1'}]}
path-only remove empties the group: []
non-member removal is a no-op: True
rejected: 400 noTarget/invalidPath: move 'x' | group unchanged: [{'value': 'u1'}, {'value': 'u2'}]
```

The path-only `remove members` line is the RFC reading and it empties the group. Decide which clients may reach it (a flag, a permission, a log line) and write that down. The same logic for `active` belongs in the user handler, next to the revocation from step 6. Lesson 7 covers the joiner-mover-leaver process around it.
