# apt_listchanges

Installs [apt-listchanges](https://salsa.debian.org/debian/apt-listchanges)
and writes any configuration to `/etc/apt/listchanges.conf.d/ansible.conf`.
This file is read after the debconf-managed `/etc/apt/listchanges.conf`, so
its settings take precedence.

## Variables

`apt_listchanges.conf` maps the profiles `apt` and `cmdline` to dicts of
options. Option names, types and allowed values (e.g. `frontend`, `which`) are
validated against apt-listchanges(1). Custom profiles are not supported. An
empty `conf` (the default) removes the drop-in file.

    ansible-doc -t role leegarrett.debian.apt_listchanges

## Example

```yaml
- hosts: all
  roles:
    - role: leegarrett.debian.apt_listchanges
      vars:
        apt_listchanges:
          conf:
            apt:
              frontend: mail
              email_address: root
              which: both
              confirm: false
```
