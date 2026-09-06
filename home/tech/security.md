---
title: "Security"
tags:
  - security
  - linux
---

# :material-lock:{ .anim-flip } Security

## Query list of ciphers supported by a server

``` sh
nmap --script ssl-enum-ciphers -p 443 example.com
```

## Things that go in a certificate

```
Subject: CN     the certificate owner's common name
Subject: E      the certificate owner's email address
Subject: T      the certificate owner's locality
Subject: ST     the certificate owner's state of residence
Subject: O      the organization to which the certificate owner belongs
Subject: OU     the name of the organizational unit to which the certificate owner belongs
Subject: C      the certificate owner's country of residence
Subject: STREET the certificate owner's street address
Subject: ALL    the certificate owner's complete distinguished name
Serial  the certificate's serial number
SignatureAlg    the algorithm used by the Certificate Authority to sign the certificate
BeginDate       the date at which the certificate becomes valid
EndDate the date at which the certificate becomes invalid
PublicKey       the certificate's public key
FriendlyName    the certificate's friendly name
```

## selinux example:

``` sh
ls -Z file1
-rwxrw-r-- user1 group1 unconfined_u:object_r:user_home_t:s0 file1
```

-   SELinux contexts follow the SELinux user:role:type:level syntax.
-   Use the `ps -eZ` command to view the SELinux context for processes
-   and `id -Z` for users
-   `seinfo -r` (part of setools-console): shows all available user roles: such as guest, unconfined, webadm, sysadm, dbadm, etc.

also see `/etc/selinux/targeted/context/users`

## SELinux/Nginx error

`sudo cat /var/log/audit/audit.log | grep nginx | grep denied`
shows something like this:

```
type=AVC msg=audit(1445306182.317:301): avc:  denied  { name_connect } for  pid=5939 comm"nginx" dest=4374 scontext=system<sub>u</sub>:system<sub>r</sub>:httpd<sub>t</sub>:s0 tcontext=system<sub>u</sub>:object<sub>r</sub>:unreserved<sub>port</sub><sub>t</sub>:s0 tclass=tcp<sub>socket</sub>
```

Someone found that running the following commands fixed their issue:

``` sh
sudo cat /var/log/audit/audit.log | grep nginx | grep denied | audit2allow -M mynginx
sudo semodule -i mynginx.pp
```

Or something like this:

``` sh
chcon -Rt httpd_sys_content_t /srv/www/myapp/
```

..to change the security context of the directory recursively so nginx will be allowed to serve it. Followed by:

``` sh
setsebool -P httpd_can_network_connect 1
```

## SElinux Apache static html

-   Change the context of the file:

``` sh
sudo chcon -R -v -t httpd_sys_rw_content_t index.html
```

-   This might have happened because we copied a file from `~` to
    `/var/www`, which caused it to retain its original context.

## Nmap one liners

-   Port scan, os detection:

``` sh
nmap -sS -P0 -sV -O 192.168.0.58
```

-   All active IPs in a network

``` sh
nmap -sP 192.168.0.*
```

-   Ping a range of IPs

``` sh
nmap -sP 192.168.0.2-254
```

-   Find unused IPs in a subnet

``` sh
nmap -T4 -sP 192.168.0.0/24 && egrep "00:00:00:00:00:00" /proc/net/arp
```

## Make a password in linux (without adding the user)

-   `whois` package: provides `mkpasswd`

``` sh
mkpasswd --method=SHA-512
```

## IPtables and nftables

`iptables` is the classic firewall tool, but modern Linux distributions (Fedora, Debian, etc.) have moved to **`nftables`**.

### Port forwarding (iptables)
Use case: make tomcat on port 8443 listen on port 443.

``` sh
sudo iptables -t nat -A PREROUTING -i eth0 -p tcp --dport 443 -j REDIRECT --to-port 8443
```

### Port forwarding (nftables)
``` sh
nft add rule ip nat PREROUTING tcp dport 443 counter redirect to :8443
```

...

To view, the usual `-L` and `-F` won't show anything. Instead, use:

``` sh
iptables -L -t nat
```

``` sh
iptables -F -t nat
```

## Open firewall ports with firewalld

``` sh
firewall-cmd --permanent --add-port=5672/tcp
```

``` sh
firewall-cmd --reload
```

## Centos firewall commands

``` sh
firewall-cmd --state
firewall-cmd --get-zones
firewall-cmd --list-all-zones
firewall-cmd --get-default-zone
firewall-cmd --list-services  # currently enabled in this zone
firewall-cmd --get-services   # all
firewall-cmd --add-service=https --permanent
firewall-cmd --add-service=http --permanent
```

## ssh-agent

-   You start an ssh-agent by running something like:

``` sh
eval `ssh-agent`
```

-   You can then feed it keys, with ssh-add like this:

``` sh
ssh-add /home/test/.ssh/id_rsa
```
or, if your key is in the default location, you can just do:

``` sh
ssh-add
```

or just put this in `.bashrc`:

``` sh
if [ -z "$SSH_AUTH_SOCK" ] ; then
  eval `ssh-agent -s`
  ssh-add
fi
```

but this prompts for the passphrase the first time it is invoked. so do this instead:

``` sh
#!/usr/bin/expect -f
spawn ssh-add /home/user/.ssh/id_rsa
expect "Enter passphrase for /home/user/.ssh/id_rsa:"
send "passphrase\n";
interact
```

## Apache redirect http to https

```apache
<VirtualHost *:80>
   ServerName mysite.example.com
   DocumentRoot /var/www/html
   Redirect permanent / https://mysite.example.com/
</VirtualHost>
```

## Certbot (Let's Encrypt)

The `letsencrypt-auto` script is deprecated. Use **`certbot`** instead.

``` sh
sudo dnf install certbot python3-certbot-apache -y
sudo certbot --apache
```

- To renew:
``` sh
sudo certbot renew
```

## Components of a cipher suite

The algorithms that make up a typical cipher suite are the following:

-   *Key Exchange Algorithm* - dictates the manner by which symmetric keys
    will be exchanged;
-   *Authentication Algorithm* - dictates how server authentication and
    (if needed) client authentication will be carried out.
-   *Bulk Encryption Algorithm* - dictates which symmetric key algorithm
    will be used to encrypt the actual data; and
-   *Message Authentication Code (MAC) algorithm* - dictates the method
    the connection will use to carry out data integrity checks.

