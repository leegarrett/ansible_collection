# kube_user

Issues a personal admin kubeconfig for a
[Kubernetes](https://kubernetes.io/) cluster. The role has
[`kubeadm`](https://kubernetes.io/docs/reference/setup-tools/kubeadm/) mint a
client certificate on the control-plane node, binds the certificate's name to
a ClusterRole so it is actually authorized, and writes kubeadm's output
verbatim to every host it runs on. All settings live in one `kube_user` dict.

## Requirements

- `kube_user.controlplane` must name a host that holds the cluster CA under
  `/etc/kubernetes/` and a `kubeadm` config at
  `/etc/kubernetes/kubeadm-config.yaml`. The cluster-side tasks are delegated
  there, so the role can be applied to any host, including one outside the
  cluster.
- Privilege escalation on that host, to read the CA.
- A working kubeconfig for the delegated host's connecting user, since the
  ClusterRoleBinding is applied through it.
- `community.crypto` on the controller, which parses the expiry of the
  certificate the target already has.

## Variables

Everything is nested under the `kube_user` dict:

| Branch | Purpose |
|---|---|
| `controlplane`, `client_name` | The two required settings: which node mints the certificate, and the name to issue it for. |
| `cluster_role` | What that name is authorized as. |
| `validity_period`, `renew_before` | How long a certificate lasts, and how close to expiry a new one is minted. |
| `local_path` | Where the kubeconfig is written on each target, as the connecting user. |

Per-option reference:

    ansible-doc -t role -r /path/to/roles/k8s kube_user

Overriding a single key while keeping the rest of the defaults requires
`hash_behaviour = merge`.

## Notes

- The role is idempotent between renewals: because every `kubeadm` run mints a
  fresh certificate, it regenerates only when the certificate in the target's
  existing kubeconfig is missing or expiring within `renew_before`. Delete
  `local_path` to force a reissue, for instance after changing
  `validity_period`.
- The kubeconfig is whatever `kubeadm` emits, which points at the cluster's
  `controlPlaneEndpoint`. That name has to resolve to the API server from the
  target for the file to be usable.
- `local_path` defaults to `~/.kube/config` and is overwritten on renewal.
- The kubeconfig carries a private key, so the tasks handling it are `no_log`.

## Example Playbook

```yaml
- hosts: k8s
  roles:
    - role: kube_user
      vars:
        kube_user:
          controlplane: kube1
          client_name: alice
```

## License

AGPL-3.0

## Author Information

Lee Garrett <lgarrett@rocketjump.eu>
