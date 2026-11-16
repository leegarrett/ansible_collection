# sops

Installs [`sops`](https://github.com/getsops/sops) from the upstream release
binary into `/usr/local/bin` on Linux hosts (amd64 only).

## Requirements

- Privilege escalation on the target host.

## Variables

See `ansible-doc -t role leegarrett.security.sops` for the full reference.
`sops.version` and `sops.sha256` reference the upstream version and sha256
checksum from upstream, so bump them together when updating.

## Example Playbook

```yaml
- hosts: workstations
  roles:
    - leegarrett.security.sops
```

## License

AGPL-3.0-or-later

## Author Information

Lee Garrett <lgarrett@rocketjump.eu>
