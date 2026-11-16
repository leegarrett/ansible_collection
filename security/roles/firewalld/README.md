# firewalld

Installs [firewalld](https://firewalld.org/), writes `firewalld.conf` and
templates the ruleset (zones, services and policies) into `/etc/firewalld`.
Supports Debian bookworm and trixie and Ubuntu 26.04 (resolute).

If cloud-init is present, the role disables it, as it deadlocks boot with
firewalld.

## Variables

Everything lives under the `firewalld` dict:

- `conf`: `firewalld.conf(5)` settings, merged over per-release defaults.
- `config_trees`: directory trees mirroring `/etc/firewalld` that hold the
  ruleset. By default, `target_templates/<target>/firewalld/etc/firewalld`
  beside the inventory directory, for the host, then each of its groups.

For the per-option reference:

    ansible-doc -t role leegarrett.security.firewalld

Overriding a single leaf without restating its siblings needs
`hash_behaviour = merge`, since all settings hang off the one `firewalld` dict.

## Example

    - hosts: servers
      roles:
        - role: leegarrett.security.firewalld
          vars:
            firewalld:
              conf:
                LogDenied: all

To open SSH on the public zone for every host in `servers`, ship
`target_templates/servers/firewalld/etc/firewalld/zones/public.xml.j2`:

    <?xml version="1.0" encoding="utf-8"?>
    <zone>
      <short>Public</short>
      <service name="ssh"/>
    </zone>

It is templated to `/etc/firewalld/zones/public.xml`.
