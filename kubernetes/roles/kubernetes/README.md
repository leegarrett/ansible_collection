# kubernetes

Prepares a Debian/Ubuntu host for Kubernetes and brings it into a cluster
built with [`kubeadm`](https://kubernetes.io/docs/reference/setup-tools/kubeadm/).
The role initializes the cluster on one designated host and joins every
other host as an additional control-plane node, so every node runs its own
apiserver, etcd member and scheduler, and also takes ordinary workloads.

On each host the role:

- validates the subnet and node IP variables before touching anything (see
  below)
- disables swap (live, plus commenting out `swap` lines in `/etc/fstab`)
- installs the Kubernetes packages (`kubeadm`, `kubelet`, `kubectl`, …)
- loads the required kernel modules and applies the networking sysctls
- on the first control-plane host: writes
  `/etc/kubernetes/kubeadm-config.yaml` and runs `kubeadm init --config`
  with it
- on every other host: enables `kubelet`, uploads the control-plane
  certificates and creates a short-lived join token on the first control
  plane, writes `/etc/kubernetes/kubeadm-join-config.yaml` from them and
  runs `kubeadm join --config` with it
- maps `kubernetes.controlplane_endpoint` to the loopback in `/etc/hosts`,
  so the node reaches the API through its own apiserver
- registers the node with an explicit `--node-ip`, so it reports one
  InternalIP per address family the cluster runs (see below)
- advertises the apiserver on the node's address in the cluster's primary
  address family, instead of the address `kubeadm` picks from the default
  route
- labels the node with `topology.kubernetes.io/region` and
  `topology.kubernetes.io/zone`, when configured (see below)
- removes the `node-role.kubernetes.io/control-plane:NoSchedule` taint that
  `kubeadm` applies, so ordinary workloads can be scheduled. Every host is a
  control plane, so without this the cluster would have nowhere to schedule
  pods.
- includes the [`kubectl`](../kubectl/) role, grants the connecting user
  read access to `/etc/kubernetes/admin.conf` via an ACL and symlinks
  `~/.kube/config` to it
- optionally approves the node's kubelet serving certificate (see below)

`kubeadm init` runs with `--skip-phases=addon/kube-proxy`, so
[`kube-proxy`](https://kubernetes.io/docs/concepts/architecture/#kube-proxy)
is never deployed. The CNI is expected to provide its
[replacement](https://docs.cilium.io/en/stable/network/kubernetes/kubeproxy-free/#kubernetes-without-kube-proxy);
until one is installed, the cluster has no pod networking and no ClusterIP
routing.

## Requirements

- Debian/Ubuntu host
- The `ansible.utils`, `ansible.posix` and `kubernetes.core` collections on
  the controller
- `k8s_ip_addresses`, a dict keyed by `inventory_hostname` with `ipv4`
  and/or `ipv6` keys, from which `node_ip` and `controlplane_ip` default.
  Joining hosts need `controlplane_ip`, so either define it for the first
  control plane or set `kubernetes.controlplane_ip` directly.

The role installs `acl`, `cri-tools`, `procps` and `python3-kubernetes` on
every host on top of `kubernetes.packages`, as its own tasks need them.

## Dependencies

Declared in [meta/main.yaml](meta/main.yaml) and applied automatically:

- [`apt_kubernetes`](../apt_kubernetes/) — configures the Kubernetes APT repository
- [`containerd`](../containerd/) — installs and configures the CRI runtime

[`kubectl`](../kubectl/) is included from the tasks.

## Role Variables

All variables are nested under the `kubernetes` top-level key. See
[defaults/main.yaml](defaults/main.yaml) for default values and
[meta/argument_specs.yaml](meta/argument_specs.yaml) for the full schema.

| Variable | Type | Required | Default | Description |
|---|---|---|---|---|
| `kubernetes.controlplane_endpoint` | str | yes | — | Stable address of the cluster API, written to the kubeadm config as `controlPlaneEndpoint`. A `host` or `host:port`; the host part is pointed at the loopback in `/etc/hosts` on every node. |
| `kubernetes.controlplane` | str | yes | — | `inventory_hostname` of the first control-plane host. The host whose name matches gets `kubeadm init`; all others join it. |
| `kubernetes.controlplane_ip` | str | no | from `k8s_ip_addresses[controlplane]` | Address of the first control plane in the primary address family. Joining hosts point `controlplane_endpoint` at it until they have joined. |
| `kubernetes.cidr` | list | yes | `[10.69.0.0/16]` | Pod network CIDRs, written to the kubeadm config as `networking.podSubnet`. One entry per address family, primary family first. The CNI has to be configured with the same subnets, see below. |
| `kubernetes.service_cidr` | list | yes | `[10.96.0.0/12]` | CIDRs services get their ClusterIPs from, written to the kubeadm config as `networking.serviceSubnet`. Same shape as `cidr`. |
| `kubernetes.dns_service_ip` | str | yes | 10th address of the first `service_cidr` | ClusterIP of the cluster DNS service, written to the kubelet's `clusterDNS`. Stays single-valued even on a dual-stack cluster, see below. |
| `kubernetes.node_ip` | list | no | from `k8s_ip_addresses[inventory_hostname]` | Addresses the kubelet registers as this node's InternalIPs, passed as `--node-ip`. The first one is also the apiserver's `advertiseAddress`. |
| `kubernetes.region` | str | no | — | Value for the node's `topology.kubernetes.io/region` label, e.g. `FSN1`. |
| `kubernetes.zone` | str | no | — | Value for the node's `topology.kubernetes.io/zone` label, e.g. `FSN1-DC24`. |
| `kubernetes.node_labels` | dict | no | built from `region` and `zone` | Labels the kubelet sets on itself at registration. |
| `kubernetes.kubelet_extra_args` | list | no | `node-labels` and `node-ip` | Name/value pairs written to `nodeRegistration.kubeletExtraArgs`. Derived from `node_labels` and `node_ip`; override only to add other flags. |
| `kubernetes.server_tls_bootstrap` | bool | no | `false` | Make kubelets request their serving certificate from the cluster CA instead of self-signing one, see below. |
| `kubernetes.packages` | list | yes | `[kubeadm, kubectl, kubelet]` | APT packages to install on every host. |
| `kubernetes.kernel_modules` | list | no | `[br_netfilter, overlay]` | Kernel modules loaded via `/etc/modules-load.d/kubernetes.conf`. |
| `kubernetes.sysctl` | dict | no | see below | Sysctls written to `/etc/sysctl.d/kubernetes.conf`. |

### Subnets

`cidr` and `service_cidr` are lists holding **one CIDR per address family**.
A single-entry list is a single-stack cluster; two entries make it
dual-stack. The first entry of each is the cluster's primary family, and
both lists have to name their families in the same order — `kubeadm` derives
the primary family from them.

Before any host setup runs, the role asserts that every entry is a valid
CIDR, that no family appears twice, that `cidr` and `service_cidr` agree on
the family order, that an IPv6 `service_cidr` is `/108` or smaller, that pod
and service CIDRs do not overlap, that `dns_service_ip` lies inside the
primary `service_cidr`, and that a non-empty `node_ip` has one address per
family in `cidr`. Overriding only `service_cidr` moves `dns_service_ip`
along with it, since it defaults to that subnet's 10th address.

`dns_service_ip` stays a single address even on a dual-stack cluster:
`kubeadm` creates the `kube-dns` Service single-stack on the primary family,
so a second `clusterDNS` entry would point at an address nothing listens on.
Pods still get AAAA answers — only the DNS transport is IPv4.

Pod IPs are handed out by the CNI, not by `kubeadm`, so `kubernetes.cidr`
only records the intent — the CNI's own address pools have to be set to the
same subnets.

The IPv6 ranges are ULA rather than public: Hetzner routes an unrelated /64
to each server, so there is no contiguous public supernet that could serve
as a cluster CIDR. A `/56` pod CIDR against `kube-controller-manager`'s
default `/64` node mask yields 256 node CIDRs, so no
`node-cidr-mask-size-ipv6` override is needed.

`kubeadm init` reads the subnets once, at cluster creation. Changing them
afterwards does not reconfigure a running cluster — see Limitations.

### Default sysctls

```yaml
kubernetes:
  sysctl:
    net.bridge.bridge-nf-call-ip6tables: 1
    net.bridge.bridge-nf-call-iptables: 1
    net.ipv4.ip_forward: 1
    net.ipv6.conf.all.forwarding: 1
    net.netfilter.nf_conntrack_max: 1000000
```

IPv6 forwarding is on unconditionally, since the host routes pod traffic for
both families. Enabling it makes the kernel ignore router advertisements;
that is safe here because the hosts' netplan config writes Hetzner's
link-local default route statically with `on-link`.

### Control plane endpoint

`controlplane_endpoint` is baked into every kubeconfig `kubeadm` writes.
Since every host runs an apiserver, the role maps its host part to
`127.0.0.1` and/or `::1` (one per family in `cidr`) in a managed block in
`/etc/hosts`, so it works without resolving cluster-externally.

A joining host cannot use its own apiserver yet, so until `kubeadm join`
finishes the block points at `controlplane_ip` instead, and is switched to
the loopback afterwards.

### Topology labels

`region` and `zone` set the node's `topology.kubernetes.io/region` and
`topology.kubernetes.io/zone` labels, which the scheduler uses to spread
workloads across failure domains. The two are independent: either one on
its own is applied, and a label whose variable is undefined is left
untouched rather than removed.

They are applied twice:

- Once at registration, via `nodeRegistration.kubeletExtraArgs` in the
  kubeadm init/join config
- Once on every run via the Kubernetes API, delegated to the first control
  plane, since the kubelet cannot relabel an already registered node

Both labels are on kubelet's allowlist of self-settable labels, so the
`NodeRestriction` admission plugin accepts them.

### Node IPs

`node_ip` is what the kubelet registers as the node's InternalIPs. It
defaults to the `ipv4`/`ipv6` keys of `k8s_ip_addresses[inventory_hostname]`,
narrowed and ordered to match the families in `cidr` — so the same inventory
data that builds the firewalld cluster zone also drives `--node-ip`, and a
single-stack cluster never gets a flag for a family it cannot route. Where
`k8s_ip_addresses` has no entry for the host the list is empty, the flag is
left off and the kubelet picks an address itself.

It is passed as `node-ip` in `nodeRegistration.kubeletExtraArgs`, and its
first entry becomes `localAPIEndpoint.advertiseAddress`, since
`kube-apiserver` refuses to start on an address outside the primary service
CIDR's family.

### Kubelet serving certificates

With `kubernetes.server_tls_bootstrap: true` each kubelet requests
its serving certificate for port 10250 from the cluster CA via the
[TLS bootstrap](https://kubernetes.io/docs/reference/access-authn-authz/kubelet-tls-bootstrapping/)
instead of self-signing one. Clients such as `metrics-server` can then verify
the kubelet against the cluster CA rather than being run with
`--kubelet-insecure-tls`.

`kube-controller-manager` auto-approves only client CSRs, so
[tasks/kubelet_serving_certs.yaml](tasks/kubelet_serving_certs.yaml) waits
for each node's pending `kubernetes.io/kubelet-serving` CSR and approves it
from the first control plane. Nodes that already have a serving
certificate are skipped, as is check mode.

It is off by default: turning it on for an existing cluster needs the
`kubelet-config` ConfigMap patched and every kubelet restarted, which the role
does not do — `kubeadm init` reads this setting once, like the subnets.

## How the control plane is selected

The role decides each host's part by comparing its `inventory_hostname`
against `kubernetes.controlplane`. Set `kubernetes.controlplane` to one
host's inventory name and run the role against the whole group; that host
initializes the cluster and the rest join it as additional control planes.

Both `kubeadm init` and the join are skipped when already done: the role
checks for `/etc/kubernetes/controller-manager.conf` on the first control
plane and `/etc/kubernetes/pki/ca.crt` on the others.
`/etc/kubernetes/kubeadm-config.yaml` is likewise written only when absent.

## Example Playbook

```yaml
- hosts: k8s_lab
  roles:
    - role: leegarrett.kubernetes.kubernetes
      vars:
        kubernetes:
          controlplane: k8s-master-1
          controlplane_endpoint: k8s-api.example.org
```

`controlplane` and `controlplane_endpoint` are typically set once for the
whole group in `group_vars/`, with the remaining keys left at their defaults.

## Wiping a host

[tasks/wipe.yaml](tasks/wipe.yaml) tears a host back down: it runs
`kubeadm reset -f`, removes the Kubernetes packages and `containerd`,
deletes every file the role's templates created plus
`/etc/systemd/system/kubelet.service.d/`, drops the endpoint block from
`/etc/hosts`, and wipes `/var/lib/containerd`, `/etc/cni/`, the pod logs and
the user's `~/.kube/`. It is not part of `main.yaml`; include it explicitly
from a dedicated playbook when you want to reset a node.

## Files Managed

| Path | Description |
|---|---|
| `/etc/kubernetes/kubeadm-config.yaml` | Cluster, init and kubelet config for `kubeadm init`, written once (first control plane only) |
| `/etc/kubernetes/kubeadm-join-config.yaml` | Discovery token, certificate key and registration flags for `kubeadm join`, kept afterwards as a record (joining hosts only) |
| `/etc/modules-load.d/kubernetes.conf` | Kernel modules to load at boot |
| `/etc/sysctl.d/kubernetes.conf` | Kubernetes networking sysctls |
| `/etc/fstab` | `swap` entries commented out |
| `/etc/hosts` | Managed block mapping `controlplane_endpoint` |
| `~/.kube/config` | Symlink to `/etc/kubernetes/admin.conf` for the connecting user |

## Limitations

The role assumes a CNI that replaces `kube-proxy` and skips that addon
unconditionally; there is no variable to turn it back on. Installing the CNI
itself is not part of this role, which means a freshly bootstrapped cluster
stays `NotReady` until that runs.

**Dual-stack cannot be turned on for a running cluster.** `kubeadm upgrade`
refuses to change the pod and Service CIDRs, and this role writes
`/etc/kubernetes/kubeadm-config.yaml` only when it is absent, so an
initialized control plane never re-reads it. Adding an IPv6 family to an
existing cluster means wiping it ([tasks/wipe.yaml](tasks/wipe.yaml)) and
bootstrapping again. The same applies to `node_ip`, `node_labels` and
`kubelet_extra_args`, which `kubeadm` only reads at init/join time; only the
topology labels are reconciled on existing nodes.

The control plane itself stays IPv4-only: `kubeadm` leaves the API server at
`--bind-address=0.0.0.0`, so `controlplane_endpoint` must not gain an AAAA
record.

A failed `kubeadm join` is not rolled back; run `kubeadm reset -f` on the
host (or [tasks/wipe.yaml](tasks/wipe.yaml)) before retrying.

With `IPv6_rpfilter: strict` (the firewalld default on trixie) IPv6
reverse-path filtering applies to decapsulated pod traffic too. If
pod-to-pod IPv6 fails after enabling dual-stack, check
`nft list ruleset | grep fib` before looking anywhere else.

With `server_tls_bootstrap` enabled, the role approves kubelet serving CSRs
only while it runs. Certificates rotate roughly yearly, and nothing approves
the renewal CSRs — deploy e.g.
[`kubelet-csr-approver`](https://github.com/postfinance/kubelet-csr-approver)
for that.

## License

AGPL-3.0-or-later

## Author Information

Lee Garrett <lgarrett@rocketjump.eu>
