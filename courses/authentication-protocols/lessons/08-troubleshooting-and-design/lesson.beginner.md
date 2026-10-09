# Choosing a protocol and troubleshooting it

You are on the help desk. This lesson answers two questions you will hear every week: which sign-in technology should this app use, and what do I check when it breaks? It adds no new SSO or provisioning protocol: LDAP and Kerberos appear only here, as legacy alternatives, and everything else is restated, so you can start here. The app side of a sign-in is called the service provider (SP), or the relying party (RP) in some protocols; this lesson says SP for any protocol. Our running example is Priya, an employee opening an expense app. Facts checked 2026-10-06; confirm vendor figures in your own tenant.

## The words you need

- **Identity provider (IdP)**: the service that signs Priya in, such as Okta. The **app** she opens is the service provider (SP).
- **SAML**: the IdP sends the app an **assertion** (usually signed), a statement about Priya with an audience (which app it is for) and a validity window (two times between which it counts). It is delivered to the app's **ACS URL**, the address the app uses to receive it. The app's own ID is its **entity ID**.
- **OAuth 2.0**: lets an app get limited access to another service for a user, using an **access token**. A **bearer token** can be used by anyone who holds it, so treat it like a password.
- **OIDC**: a sign-in layer on top of OAuth 2.0. It returns an **ID token**, a **JWT**: three text parts joined by dots, which anyone can decode but which the app must also check.
- **SCIM**: lets the IdP create, update and deactivate accounts in the app automatically. Deactivating sets the account's `active` field to false; what the app does with that is up to the app.

## Which tool for which job

<!-- diagram:which-tool -->
<div class="l08a-wrap" style="position:relative">
<input type="checkbox" id="l08a-pause" class="l08a-cb" /><label for="l08a-pause" class="l08a-btn"><span class="l08a-off">Pause animation</span><span class="l08a-on">Play animation</span></label>
<div class="l08a-box" style="overflow-x:auto">
<svg class="l08a-flow" viewBox="0 0 760 397" role="img" aria-labelledby="l08a-t l08a-d" style="width:760px;max-width:100%;min-width:699px;height:auto;display:block;margin:0 auto">
<title id="l08a-t">Signing in is not the same as managing accounts</title>
<desc id="l08a-d">A table of three tools against three jobs. SAML or OIDC signs Priya in but cannot create or remove her account. SCIM signs nobody in, creates accounts automatically, and sets them inactive by setting the active field to false, though what the app does with that is up to the app. JIT provisioning creates the account from the details sent at sign-in but cannot delete or deactivate it. The diagram highlights each row in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
<style>
svg.l08a-flow{--ink:light-dark(#000000,#ffffff)}
.l08a-box{fill:var(--panel);stroke:var(--border-strong);stroke-width:1.5}
.l08a-hot{fill:var(--panel);stroke:var(--accent);stroke-width:2.5}
.l08a-ttl{fill:var(--ink);font:600 15px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l08a-sub{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l08a-life{stroke:var(--border-strong);stroke-width:1.5;stroke-dasharray:4 5}
.l08a-front{stroke:var(--accent);stroke-width:2;fill:none}
.l08a-back{stroke:var(--muted);stroke-width:2;stroke-dasharray:7 5;fill:none}
.l08a-bad{stroke:var(--bad);stroke-width:2;fill:none}
.l08a-main{fill:var(--ink);font:600 13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l08a-badt{fill:var(--ink)}
.l08a-dim{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l08a-badge{fill:var(--accent)}
.l08a-b-back{fill:var(--muted)}
.l08a-b-bad{fill:var(--bad)}
.l08a-b-good{fill:var(--good)}
.l08a-bt{fill:var(--on-accent);font:700 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l08a-note{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l08a-note-good{fill:var(--good-bg);stroke:var(--good);stroke-width:1.5}
.l08a-note-bad{fill:var(--bad-bg);stroke:var(--bad);stroke-width:1.5}
.l08a-nt{fill:var(--ink);font:500 12.5px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l08a-nest{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l08a-row{fill:var(--raised);stroke:var(--border-strong);stroke-width:1}
.l08a-ttlL{fill:var(--ink);font:600 14px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l08a-subL{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l08a-dimL{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:start}
.l08a-dimR{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:end}
.l08a-conn{stroke:var(--accent);stroke-width:1.5;fill:none}
.l08a-edge{stroke:var(--border-strong);stroke-width:1.75;fill:none}
.l08a-hl{fill:none;stroke:var(--accent);stroke-width:3}
.l08a-hle{stroke:var(--accent);stroke-width:3;fill:none}
.l08a-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:14s;animation-timing-function:linear;animation-iteration-count:infinite}
.l08a-pk.l08a-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.l08a-pk.l08a-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.l08a-wrap{margin:20px 0}
@media (min-width:801px){.l08a-wrap{margin-left:-44px;margin-right:-44px}}
.l08a-g rect,.l08a-g line,.l08a-g path:not(.l08a-gl){opacity:.5;animation-duration:14s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.l08a-flow:hover .l08a-g rect,svg.l08a-flow:hover .l08a-g line,svg.l08a-flow:hover .l08a-g path:not(.l08a-gl),svg.l08a-flow:hover .l08a-pk{animation-play-state:paused}
.l08a-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.l08a-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.l08a-btn:hover{background:var(--hover)}
.l08a-cb:focus-visible + .l08a-btn{outline:2px solid var(--accent);outline-offset:2px}
.l08a-cb:checked + .l08a-btn .l08a-off,.l08a-cb:not(:checked) + .l08a-btn .l08a-on{display:none}
.l08a-cb:checked ~ .l08a-box .l08a-g rect,.l08a-cb:checked ~ .l08a-box .l08a-g line,.l08a-cb:checked ~ .l08a-box .l08a-g path:not(.l08a-gl),.l08a-cb:checked ~ .l08a-box .l08a-pk{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.l08a-g rect,.l08a-g line,.l08a-g path:not(.l08a-gl){animation:none;opacity:1}.l08a-pk{animation:none;display:none}.l08a-btn{display:none}}
@keyframes l08a-g0{0%{opacity:1}33.333%{opacity:1}33.343%,100%{opacity:.5}}
.l08a-g0 rect,.l08a-g0 line,.l08a-g0 path:not(.l08a-gl){animation-name:l08a-g0}
@keyframes l08a-g1{0%,33.323%{opacity:.5}33.333%{opacity:1}66.667%{opacity:1}66.677%,100%{opacity:.5}}
.l08a-g1 rect,.l08a-g1 line,.l08a-g1 path:not(.l08a-gl){animation-name:l08a-g1}
@keyframes l08a-g2{0%,66.657%{opacity:.5}66.667%{opacity:1}100%{opacity:1}100.01%,100%{opacity:.5}}
.l08a-g2 rect,.l08a-g2 line,.l08a-g2 path:not(.l08a-gl){animation-name:l08a-g2}
</style>
<defs>
<marker id="l08a-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="l08a-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="l08a-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<rect class="l08a-box" x="240" y="10" width="162" height="62" rx="10"/><text class="l08a-ttl" x="321" y="36">Signs a user in</text><text class="l08a-sub" x="321" y="56"></text>
<rect class="l08a-box" x="410" y="10" width="162" height="62" rx="10"/><text class="l08a-ttl" x="491" y="36">Creates accounts</text><text class="l08a-sub" x="491" y="56"></text>
<rect class="l08a-box" x="580" y="10" width="162" height="62" rx="10"/><text class="l08a-ttl" x="661" y="36">Removes</text><text class="l08a-sub" x="661" y="56">the account</text>
<g class="l08a-g l08a-g0">
<rect class="l08a-row" x="10" y="86" width="740" height="71" rx="8"/>
<text class="l08a-ttlL" x="24" y="112">SAML or OIDC</text>
<circle cx="321" cy="108" r="10" style="fill:var(--good)"/><path class="l08a-gl" d="M316.8,108.0 L319.6,111.4 L325.2,104.6" style="fill:none;stroke:var(--on-accent);stroke-width:2;stroke-linecap:round;stroke-linejoin:round"/>
<text class="l08a-nt" x="321" y="134">opens the app</text>
<circle cx="491" cy="108" r="10" style="fill:var(--bad)"/><path class="l08a-gl" d="M487.6,104.6 L494.4,111.4 M494.4,104.6 L487.6,111.4" style="fill:none;stroke:var(--on-accent);stroke-width:2;stroke-linecap:round;stroke-linejoin:round"/>
<circle cx="661" cy="108" r="10" style="fill:var(--bad)"/><path class="l08a-gl" d="M657.6,104.6 L664.4,111.4 M664.4,104.6 L657.6,111.4" style="fill:none;stroke:var(--on-accent);stroke-width:2;stroke-linecap:round;stroke-linejoin:round"/>
</g>
<g class="l08a-g l08a-g1">
<rect class="l08a-row" x="10" y="165" width="740" height="86" rx="8"/>
<text class="l08a-ttlL" x="24" y="191">SCIM</text>
<circle cx="321" cy="187" r="10" style="fill:var(--bad)"/><path class="l08a-gl" d="M317.6,183.6 L324.4,190.4 M324.4,183.6 L317.6,190.4" style="fill:none;stroke:var(--on-accent);stroke-width:2;stroke-linecap:round;stroke-linejoin:round"/>
<circle cx="491" cy="187" r="10" style="fill:var(--good)"/><path class="l08a-gl" d="M486.8,187.0 L489.6,190.4 L495.2,183.6" style="fill:none;stroke:var(--on-accent);stroke-width:2;stroke-linecap:round;stroke-linejoin:round"/>
<text class="l08a-nt" x="491" y="213">automatically</text>
<circle cx="661" cy="187" r="10" style="fill:var(--muted)"/><path class="l08a-gl" d="M656.8,187.0 L665.2,187.0" style="fill:none;stroke:var(--on-accent);stroke-width:2;stroke-linecap:round;stroke-linejoin:round"/>
<text class="l08a-nt" x="661" y="213">sets active to false;</text>
<text class="l08a-nt" x="661" y="228">the app decides the rest</text>
</g>
<g class="l08a-g l08a-g2">
<rect class="l08a-row" x="10" y="259" width="740" height="86" rx="8"/>
<text class="l08a-ttlL" x="24" y="285">First sign-in</text>
<text class="l08a-subL" x="24" y="303">JIT provisioning</text>
<circle cx="491" cy="281" r="10" style="fill:var(--good)"/><path class="l08a-gl" d="M486.8,281.0 L489.6,284.4 L495.2,277.6" style="fill:none;stroke:var(--on-accent);stroke-width:2;stroke-linecap:round;stroke-linejoin:round"/>
<text class="l08a-nt" x="491" y="307">from the details sent</text>
<text class="l08a-nt" x="491" y="322">at sign-in</text>
<circle cx="661" cy="281" r="10" style="fill:var(--bad)"/><path class="l08a-gl" d="M657.6,277.6 L664.4,284.4 M664.4,277.6 L657.6,284.4" style="fill:none;stroke:var(--on-accent);stroke-width:2;stroke-linecap:round;stroke-linejoin:round"/>
<text class="l08a-nt" x="661" y="307">cannot delete or</text>
<text class="l08a-nt" x="661" y="322">deactivate</text>
</g>
<circle cx="48" cy="373" r="8" style="fill:var(--good)"/><path class="l08a-gl" d="M44.6,373.0 L46.9,375.7 L51.4,370.3" style="fill:none;stroke:var(--on-accent);stroke-width:2;stroke-linecap:round;stroke-linejoin:round"/>
<text class="l08a-dim" x="64" y="377" style="text-anchor:start">does this</text>
<circle cx="163" cy="373" r="8" style="fill:var(--muted)"/><path class="l08a-gl" d="M159.6,373.0 L166.4,373.0" style="fill:none;stroke:var(--on-accent);stroke-width:2;stroke-linecap:round;stroke-linejoin:round"/>
<text class="l08a-dim" x="179" y="377" style="text-anchor:start">does this, with a catch</text>
<circle cx="368" cy="373" r="8" style="fill:var(--bad)"/><path class="l08a-gl" d="M365.3,370.3 L370.7,375.7 M370.7,370.3 L365.3,375.7" style="fill:none;stroke:var(--on-accent);stroke-width:2;stroke-linecap:round;stroke-linejoin:round"/>
<text class="l08a-dim" x="384" y="377" style="text-anchor:start">cannot do this</text>
</svg>
</div>
</div>
<!-- /diagram:which-tool -->

Read across each row: signing in and managing accounts are different jobs. SAML or OIDC signs her in but does not create or remove her account, and SCIM manages accounts but signs no one in. SCIM's last cell carries a catch, because what the app does when active is set to false is up to the app. The empty cell means this lesson does not rate the first-sign-in row on signing in. The table below adds OAuth 2.0, LDAP and Kerberos.

| Job | Tool | What it cannot do |
| --- | --- | --- |
| Priya opens a business app from her dashboard | SAML or OIDC | Create or remove her account in the app |
| An app needs limited access to another service for Priya | OAuth 2.0 | Tell the app who signed in; OIDC adds that |
| Accounts must appear, change and be switched off with HR changes | SCIM | Sign anyone in |
| The account should simply appear on her first sign-in | JIT provisioning: the app creates it from the details sent at sign-in | Delete or deactivate the account (Microsoft Learn) |
| An old app checks passwords in a company directory (LDAP) | LDAP: the app sends the name and password to the directory, so the app handles the password | Keep the password away from the app |
| Windows-style sign-in inside one company network (Kerberos) | Kerberos: tickets from a central server; computer clocks must be in step, typically within about 5 minutes | Work like a web redirect |

## Five steps for any ticket

1. **Reproduce**: same user, same app, a private window, and note the time.
2. **Capture** what the browser and app exchanged.
3. **Decode** it into readable text.
4. **Compare** each value, character for character, with the app's setup.
5. **Change one thing**, test again, and write down what you changed.

Tools you will meet:
- **Browser developer tools**, Network tab: tick Preserve log in Chrome or Persist Logs in Firefox, or each redirect clears the list.
- **SAML-tracer**: a browser extension that decodes SAML messages.
- **Token decoding offline**: never paste a real token into a website, because a bearer token can be used by whoever holds it.
- **Sign-in logs**: Okta's System Log keeps 90 days; Entra sign-in logs keep 7 days on Free and 30 on P1 and P2.
- **curl**, **openssl** (certificates), **dig** (DNS), and a clock check.

## Failure catalogue

| Symptom | Likely cause | First check |
| --- | --- | --- |
| App says the audience is wrong | The assertion is addressed to an audience; the app accepts it only if its own entity ID is listed | Audience in the capture vs the app's entity ID |
| App says wrong address, recipient or ACS | The message must name, and arrive at, the app's ACS URL | Recipient and Destination vs the ACS URL in setup |
| "Expired" or "not yet valid" | The assertion is valid only between two times, checked on the app's clock, so clocks that disagree break it | Times in the capture vs real time |
| Worked yesterday, "signature invalid" today | The app checks the signature using the IdP certificate it stored; certificates have an end date and may be replaced | Certificate end date with `openssl` |
| Signs in, but an empty new account appears | The NameID, the identifier sent for the user, can be a temporary value that changes each login | NameID Format in the capture |
| Error page at the IdP, never back to the app | The redirect URI, the address to send Priya back to, must match the registered one exactly, down to a trailing slash | `redirect_uri` in the capture vs registered |
| `invalid_grant` or `invalid_client` | The one-time code works once and expires in minutes (10 is the recommended maximum); a reload or a late retry fails. `invalid_client` means the app's own login to the IdP failed | Restart sign-in once; then check the app's client ID and secret |
| API says 401 `invalid_token` | The access token is expired, revoked or malformed | Decode it and compare `exp` (expiry time) with now |
| API says 403 `insufficient_scope` | The token is valid but its scopes (permissions) are too small | `scope` in the decoded token |
| App rejects the ID token | `iss` (issuer) must exactly match the IdP's published issuer, and `aud` must contain the app's client ID | Compare both with the app's setup |
| Email or name missing | Details are sent only when the app asks for the `email` or `profile` scope | Scopes the app requested |
| Provisioning says 409 | An account with that `userName` already exists, and `userName` ignores capital letters | Search by username before creating |
| A leaver still gets in | The app decides what `active` false means, and many apps do not cancel a session or token already issued; such a token works until its `exp` | How long the app's sessions last |
| Authenticator codes rejected | The code comes from the clock and typically changes every 30 seconds, so a wrong phone clock fails | Phone time settings |

## Eight questions for any integration

**Who issues** the proof, and for whom? **Who checks** it? **What shows it is fresh** (expiry times, one-time codes)? **What happens to a leaver**? **What is logged**, and for how long? **How do keys rotate**? **What if the IdP is down**: people already signed in to the app may keep working, new sign-ins fail. **How much damage** can a stolen token or key do?

## Triage walkthrough: Priya's ticket

Ticket 4821: "Priya clicks the Expense tile and gets: audience not valid. Two other finance users see it too; Marcus in Sales is fine in his own app."

<!-- diagram:priya-ticket -->
<div class="l08b-wrap" style="position:relative">
<input type="checkbox" id="l08b-pause" class="l08b-cb" /><label for="l08b-pause" class="l08b-btn"><span class="l08b-off">Pause animation</span><span class="l08b-on">Play animation</span></label>
<div class="l08b-box" style="overflow-x:auto">
<svg class="l08b-flow" viewBox="0 0 760 654" role="img" aria-labelledby="l08b-t l08b-d" style="width:760px;max-width:100%;min-width:699px;height:auto;display:block;margin:0 auto">
<title id="l08b-t">Ticket 4821, step by step</title>
<desc id="l08b-d">Five numbered steps for Priya's ticket. One: Priya retries in a private window and gets the same error, so it is not her browser. Two: three users and one app point at the app's setup, not at people. Three: you capture the login and decode it, and the Audience is https://app.example.com/saml/metadata. Four: the app's setup says its entity ID is https://app.example.com/saml, and the two differ. Five: you change nothing and hand the identity admin the decoded Audience, the entity ID and the time, with personal details removed; the admin changes one setting and retests. The diagram highlights each step in turn. It pauses when you hover over it, and the Pause animation control above it also pauses it.</desc>
<style>
svg.l08b-flow{--ink:light-dark(#000000,#ffffff)}
.l08b-box{fill:var(--panel);stroke:var(--border-strong);stroke-width:1.5}
.l08b-hot{fill:var(--panel);stroke:var(--accent);stroke-width:2.5}
.l08b-ttl{fill:var(--ink);font:600 15px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l08b-sub{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l08b-life{stroke:var(--border-strong);stroke-width:1.5;stroke-dasharray:4 5}
.l08b-front{stroke:var(--accent);stroke-width:2;fill:none}
.l08b-back{stroke:var(--muted);stroke-width:2;stroke-dasharray:7 5;fill:none}
.l08b-bad{stroke:var(--bad);stroke-width:2;fill:none}
.l08b-main{fill:var(--ink);font:600 13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l08b-badt{fill:var(--ink)}
.l08b-dim{fill:var(--ink);font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l08b-badge{fill:var(--accent)}
.l08b-b-back{fill:var(--muted)}
.l08b-b-bad{fill:var(--bad)}
.l08b-b-good{fill:var(--good)}
.l08b-bt{fill:var(--on-accent);font:700 12px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l08b-note{fill:var(--raised);stroke:var(--border-strong);stroke-width:1.5}
.l08b-note-good{fill:var(--good-bg);stroke:var(--good);stroke-width:1.5}
.l08b-note-bad{fill:var(--bad-bg);stroke:var(--bad);stroke-width:1.5}
.l08b-nt{fill:var(--ink);font:500 12.5px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;text-anchor:middle}
.l08b-pk{fill:var(--accent);opacity:0;filter:drop-shadow(0 0 5px var(--accent));animation-duration:26s;animation-timing-function:linear;animation-iteration-count:infinite}
.l08b-pk.l08b-pkback{fill:var(--muted);filter:drop-shadow(0 0 5px var(--muted))}
.l08b-pk.l08b-pkbad{fill:var(--bad);filter:drop-shadow(0 0 5px var(--bad))}
.l08b-wrap{margin:20px 0}
@media (min-width:801px){.l08b-wrap{margin-left:-44px;margin-right:-44px}}
.l08b-g rect,.l08b-g line,.l08b-g path:not(.l08b-gl){opacity:.5;animation-duration:26s;animation-timing-function:linear;animation-iteration-count:infinite}
svg.l08b-flow:hover .l08b-g rect,svg.l08b-flow:hover .l08b-g line,svg.l08b-flow:hover .l08b-g path:not(.l08b-gl),svg.l08b-flow:hover .l08b-pk{animation-play-state:paused}
.l08b-cb{position:absolute;opacity:0;width:1px;height:1px;margin:0}
.l08b-btn{display:inline-block;margin:0 0 8px;padding:4px 12px;border:1px solid var(--border-strong);border-radius:6px;background:var(--panel);color:var(--text);font:13px -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;cursor:pointer;user-select:none}
.l08b-btn:hover{background:var(--hover)}
.l08b-cb:focus-visible + .l08b-btn{outline:2px solid var(--accent);outline-offset:2px}
.l08b-cb:checked + .l08b-btn .l08b-off,.l08b-cb:not(:checked) + .l08b-btn .l08b-on{display:none}
.l08b-cb:checked ~ .l08b-box .l08b-g rect,.l08b-cb:checked ~ .l08b-box .l08b-g line,.l08b-cb:checked ~ .l08b-box .l08b-g path:not(.l08b-gl),.l08b-cb:checked ~ .l08b-box .l08b-pk{animation-play-state:paused}
@media (prefers-reduced-motion:reduce){.l08b-g rect,.l08b-g line,.l08b-g path:not(.l08b-gl){animation:none;opacity:1}.l08b-pk{animation:none;display:none}.l08b-btn{display:none}}
@keyframes l08b-g0{0%{opacity:1}23.077%{opacity:1}23.087%,100%{opacity:.5}}
@keyframes l08b-p0{0%,-0.01%{opacity:0;transform:translateX(0)}0%{opacity:1;transform:translateX(0)}18.462%{opacity:1;transform:translateX(146px)}23.077%{opacity:1;transform:translateX(146px)}23.087%,100%{opacity:0;transform:translateX(146px)}}
.l08b-g0 rect,.l08b-g0 line,.l08b-g0 path:not(.l08b-gl){animation-name:l08b-g0}.l08b-p0{animation-name:l08b-p0}
@keyframes l08b-g1{0%,23.067%{opacity:.5}23.077%{opacity:1}38.462%{opacity:1}38.472%,100%{opacity:.5}}
.l08b-g1 rect,.l08b-g1 line,.l08b-g1 path:not(.l08b-gl){animation-name:l08b-g1}
@keyframes l08b-g2{0%,38.452%{opacity:.5}38.462%{opacity:1}53.846%{opacity:1}53.856%,100%{opacity:.5}}
.l08b-g2 rect,.l08b-g2 line,.l08b-g2 path:not(.l08b-gl){animation-name:l08b-g2}
@keyframes l08b-g3{0%,53.836%{opacity:.5}53.846%{opacity:1}76.923%{opacity:1}76.933%,100%{opacity:.5}}
@keyframes l08b-p3{0%,53.836%{opacity:0;transform:translateX(0)}53.846%{opacity:1;transform:translateX(0)}72.308%{opacity:1;transform:translateX(-146px)}76.923%{opacity:1;transform:translateX(-146px)}76.933%,100%{opacity:0;transform:translateX(-146px)}}
.l08b-g3 rect,.l08b-g3 line,.l08b-g3 path:not(.l08b-gl){animation-name:l08b-g3}.l08b-p3{animation-name:l08b-p3}
@keyframes l08b-g4{0%,76.913%{opacity:.5}76.923%{opacity:1}100%{opacity:1}100.01%,100%{opacity:.5}}
@keyframes l08b-p4{0%,76.913%{opacity:0;transform:translateX(0)}76.923%{opacity:1;transform:translateX(0)}95.385%{opacity:1;transform:translateX(326px)}100%{opacity:1;transform:translateX(326px)}100.01%,100%{opacity:0;transform:translateX(326px)}}
.l08b-g4 rect,.l08b-g4 line,.l08b-g4 path:not(.l08b-gl){animation-name:l08b-g4}.l08b-p4{animation-name:l08b-p4}
</style>
<defs>
<marker id="l08b-m-front" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--accent)"/></marker>
<marker id="l08b-m-back" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker>
<marker id="l08b-m-bad" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--bad)"/></marker>
</defs>
<line class="l08b-life" x1="110" y1="72" x2="110" y2="602"/>
<line class="l08b-life" x1="290" y1="72" x2="290" y2="602"/>
<line class="l08b-life" x1="470" y1="72" x2="470" y2="602"/>
<line class="l08b-life" x1="650" y1="72" x2="650" y2="602"/>
<rect class="l08b-box" x="30" y="10" width="160" height="62" rx="10"/><text class="l08b-ttl" x="110" y="36">Priya</text><text class="l08b-sub" x="110" y="56">employee</text>
<rect class="l08b-box" x="210" y="10" width="160" height="62" rx="10"/><text class="l08b-ttl" x="290" y="36">You</text><text class="l08b-sub" x="290" y="56">help desk</text>
<rect class="l08b-box" x="390" y="10" width="160" height="62" rx="10"/><text class="l08b-ttl" x="470" y="36">App setup</text><text class="l08b-sub" x="470" y="56">the app's side</text>
<rect class="l08b-hot" x="570" y="10" width="160" height="62" rx="10"/><text class="l08b-ttl" x="650" y="36">Identity admin</text><text class="l08b-sub" x="650" y="56"></text>
<g class="l08b-g l08b-g0">
<text class="l08b-main" x="200" y="108">Reproduce: same error</text>
<text class="l08b-dim" x="200" y="124">in a private window</text>
<line class="l08b-front" x1="124" y1="138" x2="276" y2="138" marker-end="url(#l08b-m-front)"/>
<circle class="l08b-badge l08b-b-front" cx="110" cy="138" r="12"/><text class="l08b-bt" x="110" y="142.5">1</text>
</g>
<g class="l08b-g l08b-g1">
<rect class="l08b-note" x="186" y="172" width="208" height="65" rx="8"/>
<text class="l08b-nt" x="290" y="193">Scope: three users, one app</text>
<text class="l08b-nt" x="290" y="210">points at the app's setup,</text>
<text class="l08b-nt" x="290" y="227">not at people</text>
<circle class="l08b-badge l08b-b-plain" cx="186" cy="204" r="12"/><text class="l08b-bt" x="186" y="209.0">2</text>
</g>
<g class="l08b-g l08b-g2">
<rect class="l08b-note" x="153" y="265" width="274" height="48" rx="8"/>
<text class="l08b-nt" x="290" y="286">Capture and decode: Audience is</text>
<text class="l08b-nt" x="290" y="303">https://app.example.com/saml/metadata</text>
<circle class="l08b-badge l08b-b-plain" cx="153" cy="289" r="12"/><text class="l08b-bt" x="153" y="293.5">3</text>
</g>
<g class="l08b-g l08b-g3">
<text class="l08b-main" x="380" y="347">Compare: entity ID is</text>
<text class="l08b-dim" x="380" y="363">https://app.example.com/saml</text>
<line class="l08b-front" x1="456" y1="377" x2="304" y2="377" marker-end="url(#l08b-m-front)"/>
<circle class="l08b-badge l08b-b-front" cx="470" cy="377" r="12"/><text class="l08b-bt" x="470" y="381.5">4</text>
<rect class="l08b-note-bad" x="215" y="395" width="150" height="31" rx="8"/>
<text class="l08b-nt" x="290" y="416">They differ</text>
</g>
<g class="l08b-g l08b-g4">
<text class="l08b-main" x="470" y="460">Hand over: decoded Audience,</text>
<text class="l08b-dim" x="470" y="476">entity ID and time, no personal details</text>
<line class="l08b-front" x1="304" y1="490" x2="636" y2="490" marker-end="url(#l08b-m-front)"/>
<circle class="l08b-badge l08b-b-front" cx="290" cy="490" r="12"/><text class="l08b-bt" x="290" y="494.5">5</text>
<rect class="l08b-note-good" x="215" y="508" width="150" height="31" rx="8"/>
<text class="l08b-nt" x="290" y="529">You change nothing</text>
<rect class="l08b-note" x="569" y="508" width="162" height="48" rx="8"/>
<text class="l08b-nt" x="650" y="529">Changes one setting,</text>
<text class="l08b-nt" x="650" y="546">then retests</text>
</g>
<circle class="l08b-pk l08b-p0" cx="130" cy="138" r="5.5"/>
<circle class="l08b-pk l08b-p3" cx="450" cy="377" r="5.5"/>
<circle class="l08b-pk l08b-p4" cx="310" cy="490" r="5.5"/>
<line class="l08b-front" x1="40" y1="630" x2="70" y2="630"/>
<text class="l08b-dim" x="78" y="634" style="text-anchor:start">normal event</text>
<rect class="l08b-note-bad" x="188" y="622" width="22" height="16" rx="4"/>
<text class="l08b-dim" x="218" y="634" style="text-anchor:start">the mismatch</text>
<rect class="l08b-note-good" x="328" y="622" width="22" height="16" rx="4"/>
<text class="l08b-dim" x="358" y="634" style="text-anchor:start">what you do</text>
</svg>
</div>
</div>
<!-- /diagram:priya-ticket -->

The numbers match the numbered steps below, so each badge is one step of ticket 4821. Notice that you change nothing yourself: you hand the admin the two values that differ, plus the time, and the admin makes the one change.

1. **Reproduce**: Priya retries in a private window and gets the same error, so it is not her browser.
2. **Scope**: three users, one app. That points at the app's setup, not at people.
3. **Capture and decode**: you repeat the login with SAML-tracer and read the Audience: `https://app.example.com/saml/metadata`.
4. **Compare**: the app's setup says its entity ID is `https://app.example.com/saml`. They differ.
5. **Hand over**: you change nothing. You give the identity admin the decoded Audience, the entity ID, and the time, with personal details removed. The admin changes one setting and retests.

## Your task: read three sample artefacts

All artefacts are invented samples. I ran the decode command on 2026-10-06 (macOS, jq 1.7.1); output is real, and `now_utc` will differ for you.

```sh
T=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6InNhbXBsZS1rZXktMSJ9.eyJpc3MiOiJodHRwczovL2lkcC5leGFtcGxlLmNvbS9vYXV0aDIvc2FtcGxlIiwiYXVkIjoic2FtcGxlLWNsaWVudC1pZCIsInN1YiI6InVzZXItMDAwMSIsImlhdCI6MTc5MDAwMDAwMCwiZXhwIjoxNzkwMDAwMzAwLCJub25jZSI6InNhbXBsZS1ub25jZSJ9.ckGCV5aUn8_ZwBeTloXo0f8RbIphiOUgsMNSwTUXlLE
echo "$T" | jq -Rc 'split(".")[1] | gsub("-";"+") | gsub("_";"/") | @base64d | fromjson'
jq -nc '{exp_utc: (1790000300|todate), now_utc: (now|floor|todate)}'
# out: {"iss":"https://idp.example.com/oauth2/sample","aud":"sample-client-id","sub":"user-0001","iat":1790000000,"exp":1790000300,"nonce":"sample-nonce"}
# out: {"exp_utc":"2026-09-21T14:18:20Z","now_utc":"2026-10-06T05:23:23Z"}
```
1. The API answered 401 `invalid_token` for this token. Which field explains it? (`exp` is long before now: the token is expired. Ask for a new one.)
2. A SAML capture shows Audience `https://app.example.com/saml/metadata` while the sample app's entity ID is `https://app.example.com/saml`. What do you hand to the admin? (Both values; they do not match.)
3. On a mock server I ran (commands are in the intermediate version), a sample SCIM request to create `Alice@Example.com` returned `409 Conflict` with `"scimType": "uniqueness"`, and a look at the user list found `alice@example.com`. Is the server broken? (No: the account exists and `userName` ignores capitals. Link it, do not create it twice.)

Want to run the SAML and SCIM samples yourself? Switch to the intermediate level for the full commands.
