# caddy

Installs [Caddy](https://caddyserver.com/) from the distribution and configures
it as a TLS-terminating reverse proxy. Each site with a public hostname gets a
certificate from an ACME CA (Let's Encrypt, falling back to ZeroSSL, unless
set otherwise). Caddy obtains and renews it by itself and redirects HTTP to
HTTPS.

Requires a Debian or Ubuntu target and privilege escalation. Each site's
hostname must resolve to the target, and ports 80 and 443 must be reachable
from the internet for the ACME challenges.

## Variables

Everything lives under the `caddy` dict:

- `sites` is the branch you normally set: one entry per hostname, each
  proxying to one upstream.
- `email` and `acme_ca` are global ACME settings that apply to every site. Set
  `acme_ca` to the Let's Encrypt staging directory while testing, to avoid
  hitting the production rate limits.

Read the documented options with `ansible-doc`:

    ansible-doc -t role leegarrett.web.caddy

Setting only `sites` and keeping the other defaults requires
`hash_behaviour = merge`. Under Ansible's default `replace` behaviour, pass the
whole `caddy` dict.

## Notes

- The packaged `/etc/caddy/Caddyfile` is replaced entirely.
- The caddy service is enabled and started.

## Example

```yaml
- hosts: vpn
  roles:
    - role: leegarrett.web.caddy
      vars:
        caddy:
          email: admin@example.org
          sites:
            - address: vpn.example.org
              upstream: 127.0.0.1:8888
```
