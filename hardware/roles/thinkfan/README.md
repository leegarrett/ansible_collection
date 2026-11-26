# thinkfan

Installs [thinkfan](https://github.com/vmatare/thinkfan) and lm-sensors,
enables manual fan control in the `thinkpad_acpi` kernel module, writes
`/etc/thinkfan.yaml` and starts `thinkfan.service`.

Changes to the config file reload thinkfan, changes to the daemon arguments
restart it. The `thinkpad_acpi` option only takes effect once the module is
reloaded, usually on the next boot.

## Variables

`thinkfan.conf` is rendered verbatim as YAML to `/etc/thinkfan.yaml`, see
thinkfan.conf(5). There is no generic default, because sensors and limits
depend on the hardware: set `conf` or select a profile from
`thinkfan.profiles`. Settings in `thinkfan` win over any profile.

    ansible-doc -t role leegarrett.hardware.thinkfan

## Example

```yaml
- hosts: thinkpads
  roles:
    - role: leegarrett.hardware.thinkfan
      vars:
        thinkfan:
          daemon_args: "-b5"
          profiles:
            - thinkpad_t490
```
