---
title: "Systemd"
tags:
  - linux
  - systemd
---

# :material-penguin:{ .anim-heart }Systemd

## Socket activation

Systemd has a neat little feature where a daemon can turn on whenever a
connection is made to it. Works with Unix and network sockets. [More details
here](http://0pointer.de/blog/projects/socket-activation.html). Essentially you
create a socket file alongside your service file. The advantage is that you
don't need to start your services in a specific order.

## Flush old logs in journalctl

By date or by size:

``` sh
    sudo journalctl --vacuum-time=2d
    sudo journalctl --vacuum-size=500M
```

## Tail journalctl

``` sh
journalctl -f
```

For a specific service:

``` sh
journalctl -u httpd -f
```

## Store logs on disk

(from <http://unix.stackexchange.com/questions/159221/how-display-log-messages-from-previous-boots-under-centos-7>)

On CentOS 7, you have to enable the persistent storage of log messages:

``` sh
# mkdir /var/log/journal
# systemd-tmpfiles --create --prefix /var/log/journal
# systemctl restart systemd-journald
```

Otherwise, the journal log messages are not retained between
boots. This is the default on Fedora 19+.


