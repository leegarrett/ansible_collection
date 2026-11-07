# kubectl

Installs the [`kubectl`](https://kubernetes.io/docs/reference/kubectl/)
command-line client on Debian-family hosts, along with `bash-completion`. It
does not configure any kubeconfig — see the [`kube_user`](../kube_user/) role
for that.

## Requirements

- Privilege escalation on the target host.
- The Kubernetes APT repository, pulled in automatically as a role dependency.

## Variables

The role has none.

## Example Playbook

```yaml
- hosts: k8s
  roles:
    - kubectl
```

## License

AGPL-3.0

## Author Information

Lee Garrett <lgarrett@rocketjump.eu>
