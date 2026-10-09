# containerd

Installs, configures, enables, and starts [containerd](https://containerd.io/) on Debian/Ubuntu hosts. Also installs and configures [crictl](https://github.com/kubernetes-sigs/cri-tools) for runtime debugging.

## Requirements

- Debian/Ubuntu host
- The `community.general` collection (for the `to_toml` filter)

## Role Variables

All variables are nested under `containerd` and `crictl` top-level keys. See [defaults/main.yaml](defaults/main.yaml) for default values and [meta/argument_specs.yaml](meta/argument_specs.yaml) for the full schema.

### `containerd`

| Variable | Type | Default | Description |
|---|---|---|---|
| `containerd.packages` | list | `[containerd]` | APT packages to install |
| `containerd.config` | dict or `null` | see below | Written verbatim to `/etc/containerd/config.toml` as TOML. Set to `null` to remove the file and use containerd's built-in defaults. |
| `containerd.config.version` | int | `3` | Config file format version |
| `containerd.config.plugins` | dict | see below | containerd plugin configuration |

### Generating a config starting point

To generate a full YAML representation of containerd's compiled-in defaults, run on any host with containerd and the `reserialize` package installed:

```sh
containerd config default | toml2yaml
```

This is useful as a starting point when you want to override specific settings — paste the output into `containerd.config` and trim what you don't need.

### Config merge caveat

Containerd merges your config file against its compiled-in defaults, but only shallowly per section. At the top level, omitted keys keep their compiled defaults. Inside a nested table (e.g. `plugins."io.containerd.cri.v1.runtime".containerd.runtimes.runc`), if you define the table at all, any keys you omit within it revert to **zero values**, not the compiled defaults.

In practice this means: if you only need to set `SystemdCgroup: true`, do not copy the entire runc block — only include the keys you actually want to change. Keys you omit from a nested table will be zeroed, which may differ from the compiled default.

### Default plugin config

The role's default enables systemd cgroup management via runc:

```yaml
containerd:
  config:
    plugins:
      "io.containerd.cri.v1.runtime":
        containerd:
          runtimes:
            runc:
              options:
                SystemdCgroup: true
```

### `crictl`

| Variable | Type | Default | Description |
|---|---|---|---|
| `crictl.config.debug` | bool | `false` | Enable verbose crictl output |
| `crictl.config.runtime-endpoint` | str | `unix:///run/containerd/containerd.sock` | CRI runtime socket |
| `crictl.config.image-endpoint` | str | same as `runtime-endpoint` | CRI image service socket |
| `crictl.config.timeout` | int | `10` | Request timeout in seconds |

The `runtime-endpoint` default is derived from `containerd.config.grpc.address` when set, otherwise falls back to `unix:///run/containerd/containerd.sock`.

## Example Playbook

Minimal usage with all defaults:

```yaml
- hosts: k8s_nodes
  roles:
    - role: leegarrett.kubernetes.containerd
```

Custom containerd socket path:

```yaml
- hosts: k8s_nodes
  vars:
    containerd:
      config:
        version: 3
        grpc:
          address: /run/containerd/containerd.sock
        plugins:
          "io.containerd.cri.v1.runtime":
            containerd:
              runtimes:
                runc:
                  options:
                    SystemdCgroup: true
  roles:
    - role: leegarrett.kubernetes.containerd
```

Remove containerd config (use built-in defaults):

```yaml
- hosts: k8s_nodes
  vars:
    containerd:
      config: null
  roles:
    - role: leegarrett.kubernetes.containerd
```

## Files Managed

| Path | Description |
|---|---|
| `/etc/containerd/config.toml` | containerd runtime config (absent when `containerd.config` is `null`) |
| `/etc/crictl.yaml` | crictl client config |
