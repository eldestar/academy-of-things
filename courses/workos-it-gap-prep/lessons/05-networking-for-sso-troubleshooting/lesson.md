# Networking fundamentals for SSO troubleshooting

You know SAML from the IdP side. The posting asks for "DNS, HTTP, APIs, VPNs, firewalls", and your resume shows little of that, so this lesson maps each protocol layer to the SSO symptoms it produces. Facts checked 2026-10-03. Every block labelled **real output** was produced by commands run in this sandbox on 2026-10-03 against public hosts; yours will differ in IPs, TTLs and dates.

## Debug by layer

| Symptom | Layer to suspect | First command |
| --- | --- | --- |
| Custom domain stuck at "verifying" | DNS | `dig +noall +answer _acme-challenge.login.example.com TXT` (Okta-managed cert; `_oktaverification.login.example.com` for your own cert) |
| Browser warning, or app says "unable to verify the first certificate" | TLS chain, SNI, expiry | `openssl s_client -servername HOST -connect HOST:443` |
| Works in a private window, loops in the normal one | Cookies, redirects | Browser network log, preserve log on |
| `Assertion expired` or `not yet valid` | Clocks | Compare a server `Date` header with your clock |
| SP-initiated fails, IdP-initiated works | Cookies, proxy headers | Look at the ACS URL the app actually builds |
| SCIM or webhook never arrives | Firewall, timeout | Allowlist, then endpoint latency |

## DNS: TXT, CNAME, and resolvers that disagree

Okta's custom-domain guide: you must use a subdomain, never a root domain. With an Okta-managed certificate you add a TXT record at `_acme-challenge.<subdomain>` and a CNAME to Okta (Okta says one to five minutes, up to 24 hours). With your own certificate the TXT record is at `_oktaverification.<subdomain>` (10-15 minutes, up to 24 hours) and the CNAME follows. Some registrars want only the leading label (`_acme-challenge.login` or `_oktaverification`). Okta suggests checking the record with a DNS lookup, so do:

```sh
dig +noall +answer example.com TXT          # real output
example.com.   300 IN TXT "v=spf1 -all"
example.com.   300 IN TXT "_k2n1y4vw3qtb4skdx9e7dxt97qrmmq9"
dig +noall +answer www.github.com CNAME     # real output
www.github.com.   1885 IN CNAME github.com.
```

Things this output teaches. `example.com` carries two unrelated TXT records, one of them a verification-style token: a name can hold many TXT records, so check yours is *among* them. The same query returned them in opposite orders from `@1.1.1.1` and `@8.8.8.8`, so never script "first TXT record". The TTL (300 here) is how long a wrong cached answer survives, and `dig` through a caching resolver shows the remaining TTL, so it counts down between runs (the github CNAME showed 1885, later 1017). And the CNAME answer shows only the alias; ask the resolver you actually use, because corporate and VPN resolvers can answer differently from public ones.

Two Okta-specific traps from the same guide. With an Okta-managed certificate, Okta uses Let's Encrypt, so a CAA record must permit `letsencrypt.org` at first setup; if you add a CAA record later, Okta cannot renew the certificate. That is a certificate failure months after a DNS change nobody connected to Okta. The guide also states that Okta-managed certificates require removing network zones from the org; confirm that against your tenant before you rely on it.

JSON-friendly DNS, for scripting (**real output**, Cloudflare's DNS-over-HTTPS JSON endpoint):

```sh
curl -s -H 'accept: application/dns-json' 'https://cloudflare-dns.com/dns-query?name=example.com&type=TXT' | jq -c '[.Answer[]|{TTL,data}]'
[{"TTL":300,"data":"\"v=spf1 -all\""},{"TTL":300,"data":"\"_k2n1y4vw3qtb4skdx9e7dxt97qrmmq9\""}]
```

## TLS: chain, SNI, hostname

Three different failures look identical to a user. Real output for `example.com`:

```sh
echo | openssl s_client -connect example.com:443 -servername example.com | openssl x509 -noout -issuer -dates -ext subjectAltName
issuer=C=US, O=SSL Corporation, CN=Cloudflare TLS Issuing ECC CA 3
notBefore=Sep 26 22:49:11 2026 GMT
notAfter=Dec 25 22:56:35 2026 GMT
DNS:example.com, DNS:*.example.com
```

- **Chain.** `s_client` printed four depths (leaf at depth 0, a root at 3) and `Verification: OK`. A server that sends only the leaf fails clients that do not fetch intermediates. Okta's own-certificate path needs the public cert, the private key (2048, 3072 or 4096 bit) and the chain.
- **SNI.** With `-noservername` (OpenSSL 1.1.1+ otherwise sends SNI from the `-connect` hostname), this host refused the handshake: `SSL alert number 40` (handshake failure). A client that omits SNI can hit this on any host that requires it, and it surfaces as a generic connection failure; other hosts hand back a default certificate instead.
- **Hostname.** Asking for a bogus SNI name still returned the `example.com` certificate with `Verification: OK`, because `s_client` does not check the hostname by default. Adding `-verify_hostname wrong.example.org` produced `Verification error: hostname mismatch` and return code 62. A green `s_client` does not prove a name match.
- **Expiry.** `openssl x509 -noout -checkend 8640000` prints `Certificate will expire` and exits 1 for a 100-day horizon (this certificate has under 100 days left). Put that in a cron job against your SAML-facing hostnames. That watches TLS certificates only; also track the SAML signing-certificate expiry in each IdP's metadata, because AWS IAM ignores it.

## HTTP: proxies, cookies, clocks

**Proxy header rewriting.** AWS requires the assertion's `Recipient` to match the sign-in URL, and WorkOS's own debugging guide warns that the ACS URL must match exactly, down to http versus https. When a load balancer terminates TLS, an app that builds URLs from its own view sees `http`. `X-Forwarded-Proto` is a de-facto header and `Forwarded` is the RFC 7239 standard. A short local Python server (script in the lab) printed this (**real output**):

```
direct:        {"naive_acs":"http://127.0.0.1:18080/saml/acs","forwarded_aware_acs":"http://127.0.0.1:18080/saml/acs"}
via TLS proxy: {"naive_acs":"http://sso.example.com/saml/acs","forwarded_aware_acs":"https://sso.example.com/saml/acs"}
```

Behind the proxy the naive URL is `http` while the registered ACS is `https`, so they differ. Only honour these headers from your own proxy; clients can send them too. In practice (experience, not a vendor claim) the same http/https disagreement also makes redirect loops: the app redirects to https, the proxy forwards plain http, repeat.

**Cookies.** Per MDN, `SameSite=Lax` cookies are sent on cross-site requests only for top-level navigations with safe methods, so not on a cross-site POST. In Chromium-based browsers (Chrome 80+, Edge 86+) an unspecified `SameSite` defaults to Lax, with a looser rule that POSTs still carry cookies set within the last two minutes; Firefox and Safari do not default to Lax, so this failure is browser-specific. An IdP POSTing a SAML response to your ACS is a cross-site POST, so an SP that stores state in a default cookie can work for a fast login and fail when MFA takes three minutes (inference from those two facts; verify in your SP). The fix is `SameSite=None; Secure`. Separately, for self-hosted sign-in pages and apps that introspect the Okta session, Okta says third-party cookie restrictions can stop sign-in altogether and recommends a custom domain so apps and cookie issuer share a domain.

**Clock skew.** SAML conditions carry `NotBefore` and `NotOnOrAfter`. WorkOS's debugging guide says even a 2-3 minute drift can break authentication; tolerance is a per-SP library setting. NTP was blocked in this sandbox (`sntp` timed out), so compare HTTP `Date` headers, which is accurate to about a second (**real**: `skew_seconds(server-local)=0`).

## VPNs, firewalls and callbacks

- **Split tunnel versus network zones.** Okta zones are defined by IP, geography or ASN. If split tunnel sends Okta traffic out the home ISP instead of the corporate egress, Okta sees a different IP than your zone lists (inference). Check the client IP on the sign-in event in the System Log, not what you assume.
- **Allowlists.** Okta tells you to allow port 443 to its published IP list, "updated periodically". **Real output** from that file today: `jq 'keys|length'` gives 31 cells, `jq '[.[].ip_ranges[]]|length'` gives 5259 CIDRs, `us_cell_1` alone 485. Do not maintain that by hand; generate the rule from the file, on a schedule. The page also lists required domains and, on port 80, certificate-revocation hosts; the IP file excludes CloudFront. The page read for this lesson showed no per-traffic-type breakdown, and the file is organised by cell, so confirm what your org needs.
- **Webhooks.** Okta event hooks time out after 3 seconds with at most one retry, deliver at least once and can arrive out of order; dedupe on `eventId`. A slow endpoint behind a proxy looks like a firewall problem.

## Browser tooling

Chrome DevTools: tick **Preserve log** or redirects vanish across navigations. **Export HAR (sanitized)** drops `Cookie`, `Set-Cookie` and `Authorization`; the unsanitized option includes live session credentials, so never attach one to a vendor ticket. SAML-tracer (Firefox, Chrome and Edge, Alt+Shift+S) decodes SAML messages; treat its captures like credentials too.

## Your task

*Parts 1 and 2 were run in this sandbox. Part 3: written from the docs, not run against a live tenant.*

1. Save this as `acs_demo.py`, run `python3 acs_demo.py 18080 &`, then compare `curl -s 127.0.0.1:18080/ | jq -c .` with `curl -s -H 'Host: sso.example.com' -H 'X-Forwarded-Proto: https' -H 'X-Forwarded-Host: sso.example.com' 127.0.0.1:18080/ | jq -c .`

```python
import json, sys
from http.server import BaseHTTPRequestHandler, HTTPServer

class H(BaseHTTPRequestHandler):
    def do_GET(self):
        h = self.headers
        naive = f"http://{h['Host']}/saml/acs"                    # what a proxy-unaware app builds
        proto = h.get("X-Forwarded-Proto", "http")
        host = h.get("X-Forwarded-Host", h["Host"])
        aware = f"{proto}://{host}/saml/acs"                      # only safe if the proxy is trusted
        body = json.dumps({"naive_acs": naive, "forwarded_aware_acs": aware}).encode()
        self.send_response(200); self.send_header("Content-Type", "application/json"); self.end_headers()
        self.wfile.write(body)
    def log_message(self, *a): pass

HTTPServer(("127.0.0.1", int(sys.argv[1])), H).serve_forever()
```

2. Pick a hostname you own (never a customer's). Run the `dig`, `openssl` and `-checkend` commands against it and record the answering resolvers, TTLs, chain depth and days to expiry.
3. In a test org, break one thing on purpose (a wrong CNAME, a VM clock set 10 minutes off) and write the symptom you saw next to the table row it matches.
