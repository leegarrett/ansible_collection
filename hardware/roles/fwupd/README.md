# fwupd

Installs [fwupd](https://fwupd.org/), plus `udisks2` so it can find the ESP,
and writes `/etc/fwupd/fwupd.conf`. Supports Debian and Ubuntu. Facts must be
gathered.

The `update` entry point installs pending firmware updates with the
`leegarrett.hardware.fwupdmgr` module. It never reboots. Updates staged for the
next boot, such as UEFI capsules, are applied on the next reboot. To check
whether one is needed, look at `_fwupd_update.reboot_required` after the role
has run.

## Variables

`fwupd.conf` is a dict of INI sections, each one a dict of parameters, as
described in fwupd.conf(5). Values are written as given. The section is
rendered only if it has parameters. `fwupd.update` holds the options passed to
the module.

    ansible-doc -t role leegarrett.hardware.fwupd

## Example

```yaml
- hosts: all
  roles:
    - role: leegarrett.hardware.fwupd
      vars:
        fwupd:
          conf:
            fwupd:
              UpdateMotd: "false"

- hosts: all
  tasks:
    - name: Update firmware
      ansible.builtin.include_role:
        name: leegarrett.hardware.fwupd
        tasks_from: update
```
