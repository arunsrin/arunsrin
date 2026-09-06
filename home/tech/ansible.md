---
title: "Ansible"
tags:
  - ansible
  - automation
---

# :simple-ansible:{ .anim-heart } Ansible

These are mostly notes from reading *Mastering Ansible*, by James Freeman and
Jesse Keating. I've used ansible quite a bit but wanted a structured
understanding of it.

## Setup

`pip install ansible` in a virtualenv is enough. Config is in `~/.ansible.cfg`.
Verify the critical paths with this:

```sh
~/code/learnansible via  v3.12.0 (.ans) ❯ ansible-inventory --version
ansible-inventory [core 2.16.x]
  config file = /home/arunsrin/.ansible.cfg
...
```

### Modern Ansible Tooling

While `ansible-playbook` is the classic way to run tasks, the modern ecosystem now prefers **Ansible Navigator** (`ansible-navigator`) for a more consistent, containerized execution environment and a rich TUI.

### Aside: Oracle OCI config

I created a `~/.oci/config` that looks like this:

```sh
~/code/learnansible via  v3.8.10 (.ans) ❯ cat ~/.oci/config
[DEFAULT]
user=ocid1.user.oc1..aaaaaaaa73r3a3b3aavxmq6qceqp5cmjx55jrdald3aqregmgitbz45rjssq
fingerprint=85:8f:6f:aa:0c:91:92:e6:60:4e:39:42:77:e2:1d:a1
tenancy=ocid1.tenancy.oc1..aaaaaaaak5ipjqoopteti3pa3yj7vblgu43v5fieaphqo6pw3f2eavpoflaa
region=ap-hyderabad-1
key_file=~/.oci/arunsrin.key
~/code/learnansible via  v3.8.10 (.ans) ❯
```

The public/private api keys were generated in my personal settings page.

Then I had to install the following plugins/SDKs:

```
ansible-galaxy collection install oracle.oci
pip install oci
```

With that, a dynamic inventory file can fetch stuff from Oracle cloud:

```
~/code/learnansible via  v3.8.10 (.ans) ❯ cat my.oci.yml
plugin: oracle.oci.oci
fetch_db_hosts: true
cache: yes
cache_plugin: jsonfile
cache_timeout: 7200
cache_connection: /tmp/oci_inventory
cache_prefix: oci
```

Verify with this:

```
~/code/learnansible via  v3.8.10 (.ans) ❯ ansible-inventory -i my.oci.yml --graph
[WARNING]: Invalid characters were found in group names but not replaced, use -vvvv to see details
@all:
  |--@Oracle-Tags#CreatedBy=gnu.arun_outlook.com:
  |  |--152.70.67.213
  |--@Oracle-Tags#CreatedOn=2021-09-01T12_53_44.343Z:
  |  |--152.70.67.213
  |--@TFLz_AP-HYDERABAD-1-AD-1:
  |  |--152.70.67.213
  |--@all_hosts:
  |  |--152.70.67.213
  |--@arunsrin:
  |  |--152.70.67.213
  |--@region_ap-hyderabad-1:
  |  |--152.70.67.213
  |--@ungrouped:
~/code/learnansible via  v3.8.10 (.ans) took 5s ❯
```

