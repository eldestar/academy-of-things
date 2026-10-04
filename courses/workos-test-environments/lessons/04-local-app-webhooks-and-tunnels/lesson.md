# A local service-provider app, webhooks and tunnels

You have built the IdP half of SAML and SCIM for years. This lesson builds the half you have never owned: the service provider that sends the user out, takes the callback, and receives signed webhooks. Facts checked 2026-10-03 against WorkOS docs, the `workos-node` v11.0.0 source and each tool's own docs. The webhook receiver below was run here with real output. The SSO app was **written from the docs, not run against a live tenant**.

## The SP half in 20 lines

`@workos-inc/node` was at 11.0.0 (published 2026-09-28) and needs Node >= 22.11.0. The SSO flow is two calls: `workos.sso.getAuthorizationUrl(...)` builds a `/sso/authorize` URL (synchronous, returns a string), and `workos.sso.getProfileAndToken({ code, clientId })` exchanges the code, which the docs say is valid for 10 minutes. Staging accepts `http://localhost` redirect URIs; production requires `https://`. The quick-start docs use the staging Test Organization id `org_test_idp`.

```js
// sp.mjs  -- NOT RUN.  npm i @workos-inc/node@11.0.0
import http from 'node:http'; import crypto from 'node:crypto';
import { WorkOS } from '@workos-inc/node';
const workos = new WorkOS(process.env.WORKOS_API_KEY);
const clientId = process.env.WORKOS_CLIENT_ID, org = process.env.WORKOS_ORG ?? 'org_test_idp';
const redirectUri = 'http://localhost:3001/callback', pending = new Set();
http.createServer(async (req, res) => {
  const url = new URL(req.url, 'http://localhost:3001'), q = url.searchParams;
  try {
    if (url.pathname === '/login') {
      const state = crypto.randomUUID(); pending.add(state);
      return res.writeHead(302, { Location: workos.sso.getAuthorizationUrl({ organization: org, clientId, redirectUri, state }) }).end();
    }
    if (url.pathname === '/callback') {
      if (q.get('error')) return res.writeHead(400).end(`${q.get('error')}: ${q.get('error_description')}`);
      if (!pending.delete(q.get('state'))) return res.writeHead(400).end('unknown state');
      const { profile } = await workos.sso.getProfileAndToken({ code: q.get('code'), clientId });
      if (profile.organizationId !== org) return res.writeHead(401).end('wrong organization'); // never trust the email domain
      console.log({ id: profile.id, idpId: profile.idpId, connectionId: profile.connectionId, orgId: profile.organizationId, email: profile.email });
      return res.end(`signed in as ${profile.email}`); // probe, not an app: no session cookie
    }
    res.writeHead(404).end();
  } catch (e) { console.error(e.message); res.writeHead(500).end('exchange failed'); }
}).listen(3001, 'localhost');
```

The browser carries the SSO redirects to `localhost`, so SSO needs no tunnel. Failure modes worth reproducing: failures arrive on your callback as `error` and `error_description` query parameters (documented codes include `organization_invalid`, `connection_unlinked`, `ambiguous_connection_selector`, `idp_initiated_sso_disabled`, `profile_not_allowed_outside_organization` and `server_error`). For `server_error` the docs send you to the Sessions tab on the connection page in the Dashboard. The WorkOS docs say to check `profile.organizationId`, because email-domain checks are unsafe when orgs may allow outside addresses. Two WorkOS pages disagree on IdP-initiated login: the Login Flows page says WorkOS redirects to a sign-in endpoint you configure under the application's Redirects, appending `connection_id`; the SSO quick start says the default redirect URI handles it. Which one your app gets is a setting to confirm, and the lab above would reject a state-less callback.

## Webhooks: verify the raw bytes

The signature is in the `WorkOS-Signature` header (web servers may lowercase it): `t=<ms since epoch>, v1=<hex>`. The HMAC-SHA256 key is the endpoint's signing secret, over the string `<t>.<raw body, utf-8>`. The SDK call is `workos.webhooks.constructEvent({ payload, sigHeader, secret })`. In the v11.0.0 source, `tolerance` defaults to 180000 ms and only rejects timestamps that are too old, and a non-string, non-binary `payload` is re-serialised with `JSON.stringify` before hashing. The docs' own JS sample passes `await request.json()`, which is exactly that trap. Pass the raw string or Buffer:

```js
const payload = Buffer.concat(chunks).toString('utf8'); // never a parsed object
const evt = await workos.webhooks.constructEvent({ payload, sigHeader: req.headers['workos-signature'], secret });
```

Delivery contract from the docs: answer 2xx fast and process async. Failed deliveries retry up to 6 times with backoff over 3 days in production, but only for several minutes in staging (the Dashboard lets you retry manually there). Order is not guaranteed, events can repeat, so dedupe on event id and upsert. A fixed IP list is published for allowlisting; copy it from the docs page, not from this lesson.

## Lab (ran locally): an HMAC receiver you can attack

Stdlib Python, loopback only. Save as `receiver.py`, run `WEBHOOK_SECRET=whsec_lab python3 receiver.py`.

```python
import hashlib, hmac, json, os, time
from http.server import BaseHTTPRequestHandler, HTTPServer
SECRET = os.environ["WEBHOOK_SECRET"].encode(); seen = set()  # in-memory dedupe; a DB table for real

def verify(raw: bytes, header: str) -> bool:
    try:
        p = dict(x.strip().split("=", 1) for x in header.split(","))
        if abs(time.time() * 1000 - int(p["t"])) > 180_000: return False  # 3 min like the SDK default, but stricter: also rejects future timestamps
        mac = hmac.new(SECRET, p["t"].encode() + b"." + raw, hashlib.sha256).hexdigest()
        return hmac.compare_digest(mac, p["v1"])
    except (KeyError, ValueError, TypeError): return False

class H(BaseHTTPRequestHandler):
    def do_POST(self):
        raw = self.rfile.read(int(self.headers.get("Content-Length", 0)))  # raw bytes, pre-parse
        if not verify(raw, self.headers.get("WorkOS-Signature", "")): return self.reply(400, "bad signature")
        evt = json.loads(raw); dup = evt["id"] in seen; seen.add(evt["id"])  # parse only after verifying
        self.reply(200, "duplicate ignored" if dup else "ok " + evt["event"])
    def reply(self, code, msg):
        self.send_response(code); self.end_headers(); self.wfile.write(msg.encode() + b"\n")
    log_message = lambda *a: None
HTTPServer(("127.0.0.1", 8765), H).serve_forever()  # the tunnel, not the bind address, exposes it
```

`send.sh` signs a body file and posts it (`./send.sh SECRET evt.json [SECONDS_OFFSET]`). It hashes the file with `cat` inside a brace group, not `$(cat ...)`: command substitution strips trailing newlines while `curl --data-binary` sends them, so an editor-saved body (which ends in a newline) would be signed differently from what is posted. A first version of this script had exactly that bug (a good request returned 400); it is fixed here and both newline-terminated and unterminated files now verify.

```bash
ts=$(python3 -c "import time;print(int(time.time()*1000)+${3:-0}*1000)")
sig=$({ printf '%s.' "$ts"; cat "$2"; } | openssl dgst -sha256 -hmac "$1" -hex | awk '{print $NF}')
curl -s -w ' [HTTP %{http_code}]\n' -X POST http://127.0.0.1:8765/webhooks -H "WorkOS-Signature: t=$ts, v1=$sig" --data-binary @"$2"
```

Real results, re-run with the fixed script (the receiver prints a message, then `send.sh` prints the status on a second line): a correctly signed `dsync.user.created` gave `ok dsync.user.created` then ` [HTTP 200]`; the same event id again gave `duplicate ignored` then ` [HTTP 200]`. These returned `bad signature` then ` [HTTP 400]`: wrong secret, a correctly signed body with a changed byte, no header, a non-ASCII `v1` value, a correctly signed request with the timestamp 600 seconds old, and a body signed raw but delivered re-serialised. In Node, `JSON.stringify(JSON.parse(raw))` turned `{"id": "x", "n": 1.0, "name": "Renée"}` into `{"id":"x","n":1,"name":"Renée"}` and changed the HMAC.

## Tunnels: only the webhook needs one

WorkOS rejects endpoint URLs that are not HTTPS or whose hostname resolves to private, link-local or loopback addresses, when you save. So `localhost` fails by design. Checked 2026-10-03:

- **ngrok free plan**: one auto-assigned dev domain (stable, so register once), 1 GB and 20,000 HTTP requests a month, up to 3 endpoints, request inspection and replay included. The browser interstitial applies to HTML traffic and the docs say it does not affect programmatic clients such as webhooks.
- **Cloudflare quick tunnel** (`cloudflared tunnel --url http://localhost:8765`): no account needed, temporary hostname that changes every run, 200 in-flight requests then `429`, no uptime guarantee, testing only. Its docs also offer `--allowed-mail` (email one-time PIN) but say it does not support non-interactive clients, so never enable it here: WorkOS cannot answer a PIN.
- **Tailscale Funnel**: beta, needs MagicDNS, HTTPS and a `funnel` node attribute in the tailnet policy, ports 443, 8443 or 10000, non-configurable bandwidth limits. On macOS the docs say Funnel requires one of the open-source Tailscale variants, not the App Store or standalone app.

Commands for the first two were not run here. Failure modes: a quick-tunnel restart changes the hostname, your registered endpoint now points at nothing and failures look like silence until staging gives up after minutes. Anyone with the URL can POST to it, which is why the HMAC check is the control, so tunnel only the receiver port and never the SSO app. A secret you pasted into a chat, ticket or screenshot while debugging is a leaked secret: rotate it (lesson 6).

## Register, test, replay, and Emulate

Register the HTTPS URL in the WorkOS Dashboard webhook settings (I did not verify the exact menu label; the docs show a "Webhooks UI" screenshot), subscribe only to the event types you consume, and copy the signing secret WorkOS generates for that endpoint into an environment variable. Endpoints and secrets are per environment, so staging and production never share one. On the endpoint detail page the **Send test event** button posts sample payloads for the types you subscribed to. To reconcile after an outage, `GET /events` lists events and requires an `events` type filter.

**WorkOS Emulate** (`github.com/workos/emulate`, `@workos/emulate` 0.14.0, release v0.14.0 dated 2026-09-24, Node >= 22.11) is an in-memory local fake of the WorkOS API on `localhost:4100` with default key `sk_test_default`. Per its README it signs webhooks like production, covers seeded SSO connections and directories, and has failure injection. It is not an IdP: `/sso/authorize` signs in whoever `login_hint` names, webhooks are fire-and-forget with a 5 second timeout and no retries, and nothing persists. Use it for fast CI and error-path tests; use the staging Test IdP (Dashboard Test SSO page: only four fixed scenarios, SP-initiated, IdP-initiated, guest domain and error response) and a real Okta org you control for protocol truth, including wrong-key and certificate-rotation tests. Pointing the Node SDK at it uses the `apiHostname`, `https` and `port` options visible in the v11.0.0 source, which I did not run.

## Your task

Done when you have: (1) `sp.mjs` reaching the staging Test Organization and logging a profile whose `organizationId` matches; (2) the receiver's 8 results above reproduced on your machine; (3) a tunnel URL registered, **Send test event** answered 200, with the delivery visible in your receiver log; (4) the tunnel stopped and the endpoint deleted or disabled afterwards, with the staging secret treated as burned.
