---
title: "🔒 OpenSSL"
---

# 🔒 OpenSSL

Some non-openssl [security](security.md) notes are in a sibling page.

## Verify Public Cert, Private Key, CSR

-   Public Cert

``` sh
openssl x509 -noout -text -in server.crt
```

-   Private Key

``` sh
openssl rsa -noout -text -in server.key
```

-   CSR

``` sh
openssl req -text -noout -verify -in server.csr
```

## Verify if a cert and key are pairs

``` sh
openssl x509 -noout -modulus -in server.pem | openssl md5 ;\
openssl rsa -noout -modulus -in server.key | openssl md5
```

## Convert .cer to .pem

``` sh
openssl x509 -inform der -in certificate.cer -out certificate.pem
```

## Connect and verify

-   Connect to a remote host and see a whole lot of details:

``` sh
 openssl s_client -connect remote-hostname.com:443 \
 -msg -showcerts -verify 1 \
-CAfile allca.cer -cert myhostname.cer -key myhostname.key
```

-   View a remote host's certificate details:

``` sh
echo | \
openssl s_client  -connect remote-hostname.com:443 2>/dev/null | \
openssl x509 -text
```

## Generate a CSR

``` sh
openssl req -newkey rsa:2048 -nodes -out myhostname.csr -config myopenssl.cnf
```

For this a config file is needed. Fill it up with details like this:

``` sh
######################################################################################
[ req ]
default_bits = 2048
default_md = sha256
default_keyfile = myhostname.pem
distinguished_name = req_distinguished_name
prompt = no
req_extensions = v3_req # The extensions to add to a certificate request
[ req_distinguished_name ]
C=IN
ST=Karnataka
L=Bangalore
O=None
OU=None
CN=arunsr.in
[ v3_req ]
subjectAltName = @alternate_names
keyUsage = digitalSignature, keyEncipherment
[ alternate_names ]
DNS.1 = www.arunsr.in
DNS.2 = blog.arunsr.in
#######################################################################################
```

## Cipher regex check

If you're setting a regex to block or enable certain ciphers, here's a
quick way to verify what it expands to:

``` sh
$ openssl ciphers -V 'RC4-SHA:HIGH:!ADH'
RC4-SHA:DHE-RSA-AES256-SHA:DHE-DSS-AES256-SHA:AES256-SHA:DHE-RSA-AES128-SHA:DHE-DSS-AES128-SHA:AES128-SHA:EDH-RSA-DES-CBC3-SHA:EDH-DSS-DES-CBC3-SHA:DES-CBC3-SHA:DES-CBC3-MD5

$ openssl ciphers -V 'ALL:!aNULL:!ADH:!eNULL:!MEDIUM:!LOW!EXP:RC4+RSA:+HIGH'
DHE-RSA-AES256-SHA:DHE-DSS-AES256-SHA:AES256-SHA:DHE-RSA-AES128-SHA:DHE-DSS-AES128-SHA:AES128-SHA:EDH-RSA-DES-CBC3-SHA:EDH-DSS-DES-CBC3-SHA:DES-CBC3-SHA:DES-CBC3-MD5
```

## Convert between private key formats

Some private keys have 'BEGIN PRIVATE KEY' (NEW, PKCS8) and others
have 'BEGIN RSA PRIVATE KEY' (OLD, PKCS1). Here's how to convert
between them:

Newer versions of OpenSSL say BEGIN PRIVATE KEY because they contain
the private key + an OID that identifies the key type (this is known
as PKCS8 format). To get the old style key (known as either PKCS1 or
traditional OpenSSL format) you can do this:

``` sh
openssl rsa -in server.key -out server_new.key
```

Alternately, if you have a PKCS1 key and want PKCS8:

``` sh
openssl pkcs8 -topk8 -nocrypt -in privkey.pem
```

(from <https://stackoverflow.com/questions/17733536/how-to-convert-a-private-key-to-an-rsa-private-key>)

## Remove a passphrase from a private key

``` sh
openssl rsa -in privateKey.pem -out newPrivateKey.pem
```

## Create a self signed certificate and key

Note: Use at least 2048-bit RSA keys. RSA 1024 is considered insecure.

-   Create a private key - using RSA (2048 bit)

``` sh
openssl genrsa -out privkey.pem 2048
```

-   Or create a modern Elliptic Curve key (ED25519)

``` sh
openssl genpkey -algorithm ED25519 -out privkey.pem
```

-   Create a self signed certificate

``` sh
openssl req -new -x509 -key privkey.pem -out cacert.pem -days 1095
```


