---
title: "Kubernetes"
tags:
  - kubernetes
  - containers
---

# :material-kubernetes:{ .anim-flip } Kubernetes

Some kubernetes overview links, with a focus on networking.

## Terminal Enhancements

### k9s

Get it [here](https://k9scli.io/). My go-to cluster navigator of choice. Very
vim-like in behavior.

### k3s / kind / minikube

For local development:
- **k3s**: Lightweight Kubernetes, great for IoT and Edge but also amazing for local labs.
- **kind**: Run Kubernetes inside Docker. Fast and reliable for CI/CD.

### Cilium and eBPF

Modern Kubernetes networking is moving towards **eBPF** for performance and security. **Cilium** is the leading CNI in this space, replacing traditional iptables-based kube-proxy in many environments.

## Books

- *Kubernetes in Action* by Marko Luksa. (Get the 2nd Edition for updated content).
- *Cloud Native Infrastructure with Azure* (or your cloud of choice).

## Links

- [Cilium: eBPF-based Networking](https://cilium.io/)
- [A guide to the k8s networking model](https://sookocheff.com/post/kubernetes/understanding-kubernetes-networking-model/) - Thoroughly detailed, best link of the lot.
- [Network Plugins](https://kubernetes.io/docs/concepts/extend-kubernetes/compute-storage-net/network-plugins/) - official docs.
- [Understanding k8s networking](https://kubernetes.io/docs/concepts/extend-kubernetes/compute-storage-net/network-plugins/)
- [Multi network configuration with Multus-CNI](http://dougbtv.com/nfvpe/2017/02/22/multus-cni/)
- [Ingress system](https://www.joyfulbikeshedding.com/blog/2018-03-26-studying-the-kubernetes-ingress-system.html)
- [Another k8s networking](https://cloudnativelabs.github.io/post/2017-04-18-kubernetes-networking/)
- [Another k8s networking link](https://dzone.com/articles/how-to-understand-and-setup-kubernetes-networking)

