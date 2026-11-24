# needrestart

Installs [needrestart](https://github.com/liske/needrestart) and writes any
configuration to `/etc/needrestart/conf.d/ansible.conf`. This file is read
after the packaged `needrestart.conf`.

Supports Debian, Ubuntu and RHEL-family hosts. Facts must be gathered. On RHEL
the package comes from [EPEL](https://docs.fedoraproject.org/en-US/epel/),
which must already be enabled.

## Variables

`needrestart.conf` is a dict of `$nrconf` keys. Option names, types and
allowed values are validated. Values are converted to Perl: strings are
quoted, booleans become `1`/`0`, and lists and dicts become array and hash
refs. Regexes are given as plain strings. A list or dict replaces the packaged
default instead of being merged into it (e.g. setting `blacklist` drops the
packaged sudo and apt-get entries). An empty `conf` (the default) removes the
drop-in file.

    ansible-doc -t role leegarrett.system.needrestart

## Example

```yaml
- hosts: all
  roles:
    - role: leegarrett.system.needrestart
      vars:
        needrestart:
          conf:
            restart: a
            kernelhints: -1
```
