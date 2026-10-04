# REST APIs, webhooks and auth flows

The posting asks for "comfort with REST APIs, webhooks, and authentication flows". Your resume lists all three, but as a consumer: Python against Slack and Google APIs. The gap is the receiving side: can you write the endpoint that trusts, dedupes, orders and survives webhooks? Facts about WorkOS, Okta and the RFCs were checked 2026-10-03.

## Two receivers, two trust models

Compare what each vendor's docs say about the receiving side:

- **Okta event hooks**: a one-time GET carries `x-okta-verification-challenge` and you echo it back. After that, each POST carries an `Authorization` header holding a secret string you chose at registration. That is a shared secret in a header, not a signature over the body. Okta delivers at least once, possibly out of order, with a 3-second timeout and at most one retry; 4xx responses are not retried.
- **WorkOS webhooks**: an HMAC signature over the body, in a `WorkOS-Signature` header. Delivery is retried up to 6 times with exponential backoff over 3 days in production. Staging retries for only a few minutes, so an endpoint that is down overnight in staging loses events unless you retry from the dashboard.

Different schemes, same duties: authenticate the sender, tolerate duplicates, tolerate disorder, answer fast.

## Verifying a WorkOS webhook

What the WorkOS docs specify for manual verification:

1. Read the `WorkOS-Signature` header: two values delimited by `,`, `t=` (issue time, milliseconds since epoch) and `v1=` (the hex HMAC-SHA256).
2. Compute HMAC-SHA256, keyed with your endpoint secret, over `t`, a literal `.`, and the request body as a UTF-8 string. Compare to `v1`.
3. Check that `t` is not too far from now, to blunt replay. The SDK `tolerance` parameter does this; its defaults are "usually 3-5 minutes".

What the docs do **not** specify, and what you add yourself: the comparison must be constant-time (`hmac.compare_digest`, not `==`). The docs say only "compare". The tolerance number is also your decision.

> The docs' prose says to pass the raw request body. Their JS snippet passes `await request.json()`, a parsed object. If your framework parses JSON before your handler runs and you re-serialise it, the bytes differ and verification fails on real traffic while passing in your unit test. Capture the raw body first, or confirm what your SDK version does with an object.

Other documented controls: HTTPS only, hostname must resolve to a public IP (private ranges are rejected when you save the endpoint), a fixed set of WorkOS source IPs listed in the docs (copy the live list, not one from a course), and an optional random token in the URL path.

## The demo: one scheme, nine cases

> Generic HMAC pattern, not WorkOS code. The `t=<ms>, v1=<hex>` header and the `t + "." + body` signed string mirror the documented WorkOS scheme. The 5-minute tolerance, the constant-time compare, and the in-memory dedupe and staleness check are this demo's choices; the docs recommend event-ID dedupe and `updated_at` comparison but do not give code. The secret is a placeholder. Stdlib only, run in a sandbox on 2026-10-03.

```python
import hmac, hashlib, json, time

SECRET, TOL_MS = b"whsec_demo_placeholder", 300_000   # tolerance is our choice, not a WorkOS number
now = lambda: int(time.time() * 1000)

def mac(secret, t, body): return hmac.new(secret, f"{t}.".encode() + body, hashlib.sha256).hexdigest()
def sign(body, secret=SECRET, t=None):
    t = t or now(); return f"t={t}, v1={mac(secret, t, body)}"

def verify(body, header):
    try:
        p = dict(x.strip().split("=", 1) for x in header.split(",")); t, got = int(p["t"]), p["v1"]
    except (KeyError, ValueError): return "reject: malformed header"
    if not hmac.compare_digest(mac(SECRET, t, body).encode(), got.encode()): return "reject: bad signature"
    return "ok" if abs(now() - t) <= TOL_MS else "reject: timestamp outside tolerance"

seen, store = set(), {}          # stand-ins for a UNIQUE(event_id) table and your user table
def handle(body, header):
    v = verify(body, header)
    if v != "ok": return v
    ev = json.loads(body); obj = ev["data"]
    if ev["id"] in seen: return "ok: duplicate event id, skipped"
    seen.add(ev["id"])
    if obj["id"] in store and store[obj["id"]]["updated_at"] >= obj["updated_at"]: return "ok: stale, not applied"
    store[obj["id"]] = obj; return "ok: applied"

ev = lambda i, u: json.dumps({"id": i, "data": {"id": "du_1", "updated_at": u}}).encode()
new, old = ev("event_2", "2026-01-02T00:00:00.000Z"), ev("event_1", "2026-01-01T00:00:00.000Z")
h_old = sign(new, t=now() - 600_000)
cases = [("valid", new, sign(new)), ("redelivery", new, sign(new)), ("older event, late", old, sign(old)),
         ("tampered body", new.replace(b"01-02", b"01-09"), sign(new)), ("replay, 10 min old", new, h_old),
         ("replay, t rewritten", new, f"t={now()}, {h_old.split(', ')[1]}"),
         ("wrong secret", new, sign(new, secret=b"other")), ("garbage header", new, "nonsense"),
         ("re-serialised JSON", json.dumps(json.loads(new), separators=(",", ":")).encode(), sign(new))]
for name, body, hdr in cases: print(f"{name:20}", handle(body, hdr))
```

Real output:

```
valid                ok: applied
redelivery           ok: duplicate event id, skipped
older event, late    ok: stale, not applied
tampered body        reject: bad signature
replay, 10 min old   reject: timestamp outside tolerance
replay, t rewritten  reject: bad signature
wrong secret         reject: bad signature
garbage header       reject: malformed header
re-serialised JSON   reject: bad signature
```

Read the two replay rows together. A captured request carries a perfectly valid signature, so only the timestamp check stops it. An attacker cannot refresh the timestamp, because `t` is inside the signed string. Drop either control and replay works. Row 9 is the production bug from the callout: same data, different bytes, rejected.

## At-least-once, out of order, and recovery

Per the WorkOS docs, duplicates happen, order is not guaranteed (its example is `dsync.group.created`, `dsync.user.created` and `dsync.group.user_added` arriving in any order), and a retried old event can land after a newer one. Each event carries the full object, so the handler is an upsert guarded by `updated_at`, plus a processed-event-ID log. Two failure modes the demo hides:

- **Dedupe and apply must be one transaction.** Record the ID first and crash before applying, and the retry is skipped forever. Apply first and crash before recording, and you apply twice. Use one database transaction with a unique constraint.
- **Side effects must not live in the event handler.** WorkOS recommends separating data handling from sending email or calling third parties, so a replay does not mail someone twice.

Acknowledge first, work later: queue the payload, return 200, process in a worker. Otherwise a slow handler turns an upstream spike into timeouts, which become retries, which become more load.

When you are down longer than the retry window, WorkOS offers a second path: the events API, cursor-paginated with `after`, with a `range_start` option. Event IDs match the webhook IDs. It returns events up to 90 days old, 30 days per request. For drift that events cannot explain, you diff against the state APIs, which means detecting deletions yourself.

## Calling vendor APIs politely

- **Pagination.** WorkOS list endpoints take `limit`, `order`, `after` and `before`, return `list_metadata.after`, and you loop until it is empty. Okta returns a `Link` header with `rel="next"`; its docs say to follow those URLs rather than build your own, because cursor formats may change.
- **Rate limits.** WorkOS: 6,000 requests per 60 seconds per API key by default, and Directory Users at 4 per second per directory. Per its docs, on a 429 honour `Retry-After` if present, otherwise back off exponentially with jitter. Okta reports `X-Rate-Limit-Limit`, `-Remaining` and `-Reset` (epoch seconds). Concurrent-limit 429s show 0 and 0, and the reset time is only a suggestion. Okta lists a tight-loop sync script as a root cause; use event hooks rather than polling.
- **Idempotency keys** make a retried write safe. Stripe documents an `Idempotency-Key` header; the IETF draft behind it is expired (revision 07). WorkOS's Audit Logs Create Event accepts an `Idempotency-Key` header (keys expire after 24 hours); no equivalent was found in the Okta API docs read for this lesson, so check each reference. If an API has none, make the write naturally idempotent: look up by external ID, then upsert.

## OAuth for automation, and where tokens live

- **Client credentials** (RFC 6749 section 4.4): no human involved, confidential clients only, and a refresh token SHOULD NOT be issued, so you just ask again. Okta's service apps use only this flow for scoped tokens, authenticated with a signed JWT (`private_key_jwt`) whose expiry may be at most one hour out. Super Admin grants the scopes.
- **Authorization code with PKCE** (RFC 7636): the right tool when the script acts as a person, such as a CLI an engineer runs. RFC 9700 says public clients MUST use PKCE, confidential clients should, and servers MUST support it. A headless CLI usually needs the device authorization grant (RFC 8628) instead.
- **Storage, judgment rather than spec.** Keep the access token in memory and renew it before `expires_in` rather than hard-coding a lifetime. Keep the private key or API key in a secrets manager, never in the repo or logs. Use one credential per automation so you can revoke one without breaking five.

## Your task

> Written but not run. Only the demo above was executed.

1. Wrap `handle` in a `http.server` endpoint. Read exactly `Content-Length` raw bytes, return 200 before processing, and test with `curl --data-binary`.
2. Replace the `seen` set with a SQLite table with a unique event ID, and make dedupe and apply one transaction.
3. Write a client that pages a local fake API and handles a 429 with `Retry-After`. Then make the fake omit the header and watch your jittered backoff take over.

Next: the interview lesson turns these into answers.
