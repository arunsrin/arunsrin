---
title: "Linux"
tags:
  - linux
  - sysadmin
  - os
---

# :material-penguin:{ .anim-rotate }Linux

My favourite OS. Been using it since 2004. Learnt the hard way, uphill
both ways. I used to borrow DVDs from the library at work and give it
a spin at home. I didn't have a working internet connection back then
so I'd have to take notes on the error message, research them the next
day at work, and fix it when I got back. Probably the most fruitful
time I've had to date.

I distro-hopped every few months, and my fondest memories are of
Slackware and, well, FreeBSD. I had a ton of fun with my Desktop:
setting up IPv6 tunnels, dynamic DNS, apache, squid, privoxy, and
generally playing with minimiastic window managers and the shell.

These days I stick with Fedora on my personal laptop and WSL-2 at 
work, and love both.

## dotfiles

My dotfiles are [here](https://github.com/arunsrin/dotfiles). I use
asdf to manage several packages, and stock ubuntu for the rest. The
repo has dotfiles for my vim/emacs setups, starship (for a nice
prompt), and a few other tools.

## Gnome

### Allow volume above 100%

From [here](https://www.reddit.com/r/Fedora/comments/v2d8yr/comment/kgar1ts/)

> You'll want to install the dconf-editor, navigate to
> `org.gnome.desktop.sound` and set `allow-volume-above-100-percent` to true

## General Linux

### Check process, thread, utilization and CPU attached to

`ps -mo pid,tid,%cpu,psr -p <process_id>`

### Check network connections made by a process with strace

`strace -f -e trace=network -o /tmp/strace.txt -s 10000 <cmd> <args>`

### Modern Networking: iproute2

The old `ifconfig`, `route`, and `netstat` commands are deprecated. Use the `ip` suite instead:
- `ip addr` - View IP addresses (replaces `ifconfig`).
- `ip link` - View/manage network interfaces.
- `ip route` - View/manage the routing table (replaces `route`).
- `ss -tulpn` - View listening ports (replaces `netstat -tulpn`).

### Centos 7 sources (LEGACY)

!!! warning
    CentOS 7 reached End of Life (EOL) on June 30, 2024. These notes are preserved for legacy maintenance only.

Clone their helper repo first:

``` sh
git clone  https://git.centos.org/git/centos-git-common.git
```

Go to their [RPM project](https://git.centos.org) and select a project
to clone. I'm picking `coreutils` here. This repo has a SPEC file and
the patches to the original source.

``` sh
git clone https://git.centos.org/r/rpms/coreutils.git
```

The master branch is always empty. Checkout their `c7` branch to see
the SPECS and SOURCES folders for Centos 7, and run the helper script
to fetch the source.

``` sh
git checkout c7
../centos-git-common/get_sources.sh
```

### dnsmasq custom dns server for a domain

Add a specific record like this in the dnsmasq configuration:

```
server=/mydomain.local/10.250.0.2
```

For everything else, dnsmasq will use the existing configuration in
`/etc/resolv.conf`.

More [here](https://serverfault.com/questions/872109/resolv-conf-multiple-dns-servers-with-specific-domains)

### diff and patch

``` sh
cp somepackage somepackage-new
# make changes in somepackage-new
diff -ruN somepackage somepackage-new > mychanges.patch
# give the patch to someone else, who can now do:
cd somepackage
patch -p1 < mychanges.patch
```

More information than you'll ever need
[here](http://lists.landley.net/pipermail/toybox-landley.net/2019-January/010049.html).

### ccache notes

Install from the repo as usual

``` sh
sudo yum install ccache -y
```

One way to set it up:

``` sh
bash-4.2 /bin$ cp ccache /usr/local/bin/
bash-4.2 /bin$ ln -s ccache /usr/local/bin/gcc
bash-4.2 /bin$ ln -s ccache /usr/local/bin/g++
bash-4.2 /bin$ ln -s ccache /usr/local/bin/cc
bash-4.2 /bin$ ln -s ccache /usr/local/bin/c++
```

### Change timezone in centos:

``` sh
ln -s /usr/share/zoneinfo/Asia/Kolkata /etc/localtime
```

For debian:

``` sh
timedatectl set-timezone Asia/Kolkata
```

### Install fonts in centos/linux:

System-wide : 

``` sh
mkdir -p /usr/share/fonts/greatvibes
```

User only : 

``` sh
mkdir ~/.fonts
```

Copy your font files in the appropriate folder and "register" them in the system with:

``` sh
fc-cache -f -v
```

### Linux date conversion (epoch to human readable)

Convert epoch time to human readable format:

``` sh
date -d @1445305686.222
```

### Howto add swap space:

``` sh
free
dd if=/dev/zero of=/var/swap.img bs=1024k count=1000
mkswap /var/swap.img
swapon /var/swap.img
free
```


### If df shows no disk space even after deleting files, check this output:

``` sh
sudo /usr/sbin/lsof | grep deleted
```

-   Space will not be freed for the files there.
-   Restart those offending daemons to actually free the space up.

If you don't have lsof, just use this:

``` sh
find /proc/*/fd -ls | grep  '(deleted)'
```

### Useful linux diagnostic commands:

``` sh
uptime
dmesg | tail
vmstat 1
mpstat -P ALL 1
pidstat 1
iostat -xz 1
free -m
sar -n DEV 1
sar -n TCP,ETCP 1
top # or use htop / btop for a better TUI
```

### GNU/Screen scrollback:

`Ctrl a Esc`
(then use `Ctrl b/Ctrl f/Ctrl u/Ctrl d` etc)
and `Esc` to end

### Quick fsck (solaris)

``` sh
fsck -Fy ufs /dev/rdsk/c1d0s5
```

### Debian - clean up orphaned files:

``` sh
aptitude  remove --purge $(deborphan)
```

### See filesystem usage:

``` sh
/usr/bin/du --total --summarize --human-readable --one-file-system
```

### GNU/Screen splitting windows

-   `C-a V or C-a |`     split the screen vertically
-   `C-a X`              remove/detach the current split
-   `C-a S`              split horizontally
-   `C-a tab`            cycle between windows

### Tmux keybindings

-   `Ctrl-b %` (Split the window vertically)
-   `Ctrl-b :` "split-window" (Split window horizontally)
-   `Ctrl-b o` (Goto next pane)
-   `Ctrl-b q` (Show pane numbers, when the numbers show up type the key to goto that pane)
-   `Ctrl-b {` (Move the current pane left)
-   `Ctrl-b }` (Move the current pane right)

And here's my .tmux.conf

``` sh
set -g prefix C-a
unbind C-b
bind C-a send-prefix

set -g default-terminal "xterm-256color"

set -g history-limit 10000
set -g set-titles-string "#T"

unbind %
bind | split-window -h
bind - split-window -v
```

### Colour in terminals

``` sh
    arunsrin@ARUNSRIN-G2CA5 MINGW64 ~
    $ printf "\033[32mhi\033[0m"
    hi
```

-   `\033` is Escape
-   So `Escape + 3 + 2 + m` tells the terminal that everything from this
    point onwards is in green.
-   And `Escape + [ + 0 + m` reverts it back to normal

-   These are some sequences:

```
Sequence   What it Does
ESC[1m     Bold, intensify foreground
ESC[4m     Underscore
ESC[5m     Blink
ESC[7m     Reverse video
ESC[0m     All attributes off
```

### Bash Stty: Coredump etc

``` sh
Ctrl \
```

or

``` sh
kill -SIGQUIT <pid>
```

Override it with:

``` sh
stty quit <some-binding>
```

Similarly for that age-old backspace not deleting a character problem:

``` sh
stty erase ^h
```

To see the current terminal capabilities, run:

``` sh
stty -a
```

### Fix for xargs errors when filenames contain spaces

-   `find` has a print0 option that uses null characters instead of \n as separators.
-   `xargs` has a -0 option that uses the same separator when working on the args. So:

``` sh
find . -name -print0 | xargs -0 ls -l
```

### Bash faster navigation with cdpath

``` sh
export CDPATH=:$HOME:$HOME/projects:$HOME/code/beech
```

-   cd'ing to a folder first looks at CWD, then rest of CDPATH

### Find

with date filters

-   `find . -ctime -3` # created in the past 3 days
-   `find . -ctime +3` # older than 3 days
-   `find . -ctime 3` # created exactly 3 days back
-   `find . -ctime +3 -ctime -5` # created 3 - 5 days back
-   `find . -newer /tmp/somefile` # see somefile's timestamp and show files newer than it
-   works great in conjunction with:
-   `touch 0607090016 /tmp/somefile` #i.e. 7th june, 9:00 am, 2016
-   `find . -maxdepth 1 -type d -ctime +38 -exec rm -rf  {} \;` delete all folders older than 38 days back.
-   don't use atime much: every directory access changes its atime, so when find traverses through it, the inode's atime entry gets updated.

### File formatting, wrapping etc

Huh, who knew this existed:

``` sh
cat <some-verbose-output> | fold -70
```

-   `fold -s` folds at whitespace

-   Also look at the `fmt` command, which seems similar to emacs'
    `fill-paragraph`.

-   `pr` gives a pretty display with margins, headers, and page numbers.

### Deleting files with odd names

There's more than one way. Here's one: find the inode with `ls -i`, then delete with:

``` sh
find -inum <inode-number> -exec rm -i {} \;
```

### See whitespace with cat

Use this:

``` sh
cat -v -t -e <somefile>
```

-   `-e`: Add a trailing `$` at the end of a line.
-   `-t`: Show tabs as `^I`

### Stat command: see inode information

The inode holds the address in the filesystem, access permissions, ctime/mtime etc

``` sh
    arunsrin@ARUNSRIN-G2CA5 MINGW64 ~
    $ stat ntuser.ini
      File: ‘ntuser.ini’
      Size: 20              Blocks: 1          IO Block: 65536  regular file
    Device: a4b221d6h/2763137494d   Inode: 562949953421373  Links: 1
    Access: (0644/-rw-r--r--)  Uid: (1233064/arunsrin)   Gid: (1049089/ UNKNOWN)
    Access: 2015-07-21 18:57:13.142410100 +0530
    Modify: 2010-11-21 08:20:53.336035000 +0530
    Change: 2016-06-06 09:18:05.239486700 +0530
     Birth: 2015-07-21 18:57:13.142410100 +0530
    
    arunsrin@ARUNSRIN-G2CA5 MINGW64 ~
    $
```

If the filename is odd and you can't paste it easily in the terminal, just try

``` sh
ls -il
```

### Bash debugging

Run the script with `-xv` in the shebang:

``` sh
#!/bin/bash -xv
# do something
```

### Bash suppress echo (for reading passwords)

In bash, while reading input from the user, if you want to suppress
the echo on the screen (for sensitive inputs like passwords), do this:

``` sh
stty -echo
read SECRETPASSWD
stty echo
```

### ngrep

Try this:

``` sh
sudo ngrep -d any <word> -q
```

`-d any` listens on any interface

`-q` is quiet mode so those `#`'s don't show.

### Pretty-print json

``` sh
cat somefile.json | python -m json.tool
```

### WSL passwd reset

From powershell, run this to directly login as the root user:

``` sh
wsl --user root
```

If you have more than one wsl distribution installed, list them with `wsl -l`
and exec into that with this:

``` sh
wsl -d Ubuntu-20.04 --user root
```

Then you can do the usual `passwd` or `passwd <user>` to reset that password.

