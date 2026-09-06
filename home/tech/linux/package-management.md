---
title: "Package management"
tags:
  - linux
  - packaging
---

# :material-penguin:{ .anim-heart } Package management

## Sort RPMs by size

``` sh
rpm -qa --queryformat '%{size} %{name}\n' | sort -rn | more
```

## Extract rpm into current folder instead of installing:

``` sh
rpm2cpio boost-system-1.53.0-23.el7.x86_64.rpm | cpio -idmv
```

## Trace a binary or file to the RPM that installed it:

``` sh
yum whatprovides /usr/lib64/libdbus-c++-1.so.0
```

or this:

``` sh
rpm -qf /usr/lib64/libdbus-c++-1.so.0
```

## Yum/dnf revert

If a yum remove wiped out several packages, do this:

-   `dnf history` # note the id of the bad removal here
-   `dnf history undo 96`

yum/dnf will reinstall all the packages that were removed in that id.

## Dependencies of a package

This command shows what other packages need the queried package:

``` sh
repoquery --whatrequires libunwind
```

Another way, without using repoquery:

``` sh
rpm -q --whatrequires python-ipaddress
```

This command shows what other packages need to be installed for a queried package:

``` sh
yum deplist nginx
```

