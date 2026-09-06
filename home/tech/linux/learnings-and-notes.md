---
title: "Learnings/Notes"
tags:
  - linux
  - tips
---

# :material-penguin:{ .anim-bounce } Learnings/Notes


## Linux's CFS: Completely Fair Scheduler

-   On a single cpu, the available cpu cycles are divided among all the
    threads in proportion to their weights.
-   The weight `= priority =` niceness.
-   Threads are organized in a runqueue (implemented as a red-black tree).
-   A thread exceeding its timeslice is pre-empted and the next one is given a slice.
-   In multicore systems, each core has its own runqueue.
-   But this may not always be fair (since one core may run one
    low-priority thread while the other may run several high-priority
    threads, inefficiently)
-   So linux has a load balancer that periodically keeps the queus in balance.
-   Load balancing is a costly operation (both computation and
    commuication operations are expensive) so it is kept at a minimum if
    possible.

## Memory layout in Linux

-   32-bit: 3:1 ratio: out of 4gb, 3gb is for users and 1gb for kernel
-   64-bit: 1:1: out of 128TB, 64TB is for users and 64 for kernel.
-   So the kernel memory starts at 0xffff80000000<snip>000 in 64-bit,
    and 0xc000000 in 32-bit.
-   For a user process, Stack size is 8mb by default (see ulimit -s).
-   Stack occupies top of the address space and grows down.
-   The botttom of the stack contains env variables, prog name and \*\*args
-   Below the stack is memmap which has stuff linked dynamically and
    mapped by the kernel at runtime.
-   Then is the heap.
-   Then there's bss/data/program text.
-   text is usually read-only.
-   stack and data are non-executable (to prevent (partially) overflows).

## Docker Notes:

-   apache mesos: get a lot of compute clusters looking like a single system.
-   Docker Trusted Registry: on-prem repository service
-   Machine: configures docker on cloud instances
-   Swarm: deploys containers in clusters. (Docker's version of Kubernetes)
-   Compose: use YAML templates ofr multiple application deployments.
-   Tutum - like compose for cloud deployment. New acquisition.
-   OpenStack Havana supports docker as a hypervisor.
-   `docker run -d` (detaches and runs as a daemon)
-   use `docker start -i asdasdas123 bash` to connect to an existing
    instance. (or actually attach).
-   use `docker exec` if you want another process in an existing
    container. better than attach since attach just reattaches to the
    original pid1 process.
-   `docker rename` renames an existing container. otherwise `--name` while starting.
-   `docker ps -a` shows non-running containers.
-   names are auto-generated if you don't specify them :)
-   =docker run &#x2013;name loopdate -d centos /bin/sh -c "while true; do date; sleep 3; done"=
-   (daemonize example)
-   `docker logs  --tail 0 -f loopdate`
-   (to see the live logs for the example above)
-   `docker cp /etc/hostname asdasd123132:/tmp`
-   `docker run --restart <etc>`: sets a policy to restart if it
    stops. doesn't start a new container, just restarts the same id.
-   NUMA - Non-Uniform Memory Access.
-   `/var/lib/docker/containers/<id>`
-   `/var/lib/docker/aufs/diff/<id>`: see the CopyOnWrite diffs between this instance and the base layers.
-   `docker diff <id>`: shows files changed in a container.
-   `docker inspect loopdate|less` : json metadata, e.g. ipaddress.
-   `docker history <image>` shows the history of commands used to build that image.
-   'latest' is a convention but need not be latest.. e.g. ubuntu sets
    'latest' to their LTS release 14.04, and not to bleeding edge.
-   creating images: either 'commit' an existing container, or specify a dockerfile.
-   you can save and package to tar file instead of pushing to a registry.
-   `docker images -a`: show intermediate images (these don't have tags)
-   `` docker rm `docker ps --no-trunc -aq` `` (remove everything)
-   sample commit command:
    `docker commit --change 'CMD ["/usr/sbin/httpd","-D","FOREGROUND"]'  --change 'ENV APACHE_RUN_USER www-data'  --change 'ENV APACHE_RUN_GROUP www-data' 26cb lab/websvr:v0.2`
-   do a `docker pull <image>` before use if you want to speed up your boxes.
-   docker registry is opensource, and v1.6+ is in go and supports parallel downloads.
-   registry:latest is 0.9, and is a python app. deprecated.
-   `docker run -p 5000:5000 -d registry:2` &#x2013;gives a web interface for registry v2.
-   `docker tag arun/myapache localhost:5000/myapache`, followed by a
    `push`: pushes myapache to the local registry.
-   `docker save/load`: tar a repo (i.e. image), including parent layers
    and tags and versions, for local circulation.
-   `docker export` is like save, but flattens the filesystem.
-   build a docker image from a dockerfile: docker build some/path
-   use `--link` to link two containers together (adds to each container's
    hosts file). newer versions have advanced networking: put associated
    containers in a single subnet , and allow them to talk to each
    other.

## Vagrant notes:

### setup:

-   `vagrant init`
-   `vagrant box add centos/7`
-   mention the same box in the vagrantfile

### start:

-   `vagrant up`
-   `vagrant ssh`

### stop:

-   `vagrant suspend` # save state and stop
-   `vagrant halt` # graceful shutdown
-   `vagrant destroy` # wipe out hd etc

## Ansible notes

-   Modules are wrappers for administration commands (like ping, apt, yum, copy, etc).
-   Always use these instead of shell exec since modules are idempotent:
    you specify the state you want to be in, and the commands are run
    appropriately.
-   A task contains a module to be run, along with Facts or conditions or anything else.
-   Handlers can do everything tasks can, and are triggered by tasks
    when conditions are met. e.g. 'start nginx' would be a handler
    called in 'install nginx'.
-   Roles organize multiple tasks in one coherent whole (e.g. installing
    nginx may require adding a repo, copying certs, installing the rpm
    and starting the server).
-   Roles are organized like this: files, handlers, meta, templates, tasks, vars.
-   Except files and templates, a main.yml file present in all other
    folders will be executed automatically.
-   Files have static files, e.g. httpd.conf, certs etc.
-   Handlers have triggers obviously
-   Meta has dependencies and other metadata. e.g. run the ssl role
    before starting the nginx role.
-   Templates are based on jinja2.
-   Variables have vars that are used to fill the templates.
-   Tasks have the main logic.
-   To run the whole role, just call the main yaml: `ansible-playbook -s main.yml`
-   Facts are metadata gathered by ansible on init: num<sub>processors</sub>,
    cores, interfaces, mounts etc. you can use these vars in your
    templates.
-   ansible-vault can be used to encrypt vars and files in a role.

## Linux ad-hoc daemonization

-   If a script is running in a terminal and you want to daemonize it, do this:
-   `Ctrl-Z` to suspend it
-   `bg` to make it a background job
-   `disown -h %job-id` where `job-id` is what bg returned. This removes
    the command from the shell's job list, so it won't get a SIGHUP when
    the terminal closes.

## linux ctime vs mtime

-   ctime is for inode, mtime is for contents
-   e.g. chmod changes ctime. `echo "asd">>file` changes mtime.

## soft vs hard links

### Hard links:

-   Two filenames in a folder pointing to the exact same inode.
-   There is no distinction between the link and the original.
-   This means you can delete one file and the other will still exist!
-   Cannot traverse filesystems. cannot hard link directories

### Soft links:

-   A new kind of file that has its own inode entry. the OS knows how to
    traverse from it to the parent.
-   No limitations.

-   When a user runs mkdir, along with creating a directory, mkdir
    internally creates a hard-link called '..' pointing to the
    parent. that's why cd .. takes you to the parent, and that way '..'
    doesn't take up space in the filesystem either. Similarly another
    hardlink called '.' is created inside that folder, linking to the
    folder itself in the parent.

i.e. if you have test/child:

``` sh
cd child
ls -ail
.   inode1  # child's inode
..  inode2  # parent's inode
cd ..
ls -ail
. inode2   # parent's inode
.. inode4  # parent's parent's inode
child inode1
```

