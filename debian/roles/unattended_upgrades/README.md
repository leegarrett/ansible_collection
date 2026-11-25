# unattended_upgrades

Installs [unattended-upgrades](https://wiki.debian.org/UnattendedUpgrades) and
writes any configuration to `/etc/apt/apt.conf.d/52unattended-upgrades-local`.
This file is read after the packaged `50unattended-upgrades`, so its settings
take precedence.

## Variables

`unattended_upgrades.conf` is a dict of apt.conf options keyed by their full
name, covering both `Unattended-Upgrade::*` and the `APT::Periodic::*` keys
that schedule it. Option names, types and allowed values are validated.
Scalars become `Key "value";`. A list replaces the packaged list instead of
being appended to it (it is emitted with `#clear`). An empty `conf` (the
default) removes the drop-in file.

    ansible-doc -t role leegarrett.debian.unattended_upgrades

## Example

```yaml
- hosts: all
  roles:
    - role: leegarrett.debian.unattended_upgrades
      vars:
        unattended_upgrades:
          conf:
            Unattended-Upgrade::Automatic-Reboot: true
            Unattended-Upgrade::Automatic-Reboot-Time: "04:00"
            Unattended-Upgrade::Origins-Pattern:
              - origin=Debian,codename=${distro_codename},label=Debian
              - origin=Debian,codename=${distro_codename}-security,label=Debian-Security
```
