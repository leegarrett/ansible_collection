apt_kubernetes
==============

Configures the official Kubernetes APT repository (`pkgs.k8s.io`) via
`ansible.builtin.deb822_repository` and immediately runs `apt-get
update`. Other roles that need packages from this repository should
declare it as a dependency.

Role Variables
--------------

| Variable | Required | Default | Description |
|---|---|---|---|
| `apt_kubernetes.ver` | no | `"1.37"` | Kubernetes minor version for the repository URL (e.g. `"1.36"` → `https://pkgs.k8s.io/core:/stable:/v1.36/deb/`). |
| `apt_kubernetes.name` | no | `kubernetes` | Repo name, decides the file name below `/etc/apt/sources.list.d/`. |
| `apt_kubernetes.uris` | no | upstream repo for `ver` | Repo URIs. |
| `apt_kubernetes.types` | no | `[deb]` | Repo types, `deb` and/or `deb-src`. |
| `apt_kubernetes.suites` | no | `[/]` | Suites, `/` for the flat repo upstream publishes. |
| `apt_kubernetes.components` | no | `[]` | Components, empty for a flat repo. |
| `apt_kubernetes.enabled` | no | `true` | Whether apt uses the repo. |
| `apt_kubernetes.signed_by` | no | upstream key | ASCII armored OpenPGP key the repo is signed with. |
| `apt_kubernetes.validate_signed_by` | no | `true` | Lint `signed_by` with `sq cert lint` before adding the repo. Installs `sq` on the target. |

Dependencies
------------

None. `python3-debian` is installed on the target, `deb822_repository`
needs it. `sq` is installed too unless
`apt_kubernetes.validate_signed_by` is `false`.

Example Playbook
----------------

```yaml
- hosts: k8s_nodes
  roles:
    - role: apt_kubernetes
      vars:
        apt_kubernetes:
          ver: "1.33"
```

License
-------

AGPL-3.0

Author Information
------------------

Lee Garrett <lgarrett@rocketjump.eu>
