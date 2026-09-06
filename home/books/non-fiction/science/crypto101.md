---
title: "Crypto 101"
tags:
  - books
  - science
  - crypto
---

# :material-pencil:{ .anim-fade } Crypto 101

Notes from reading the excellent book at <https://www.crypto101.io/>

Other [security](../../../tech/security.md) notes.

## Block ciphers

`C = E(k, P)`

`k` and `P` are the key and plain text.

The plain text is broken up into blocks of length equal to the key's block size.

The same key is used to decrypt.

Most common one is AES. preceeded by DES.

AES was called Rijndael after its 2 developers. allows block sizes of 32, 128, 192 and 256.

### Drawbacks:

-   Message length must not exceed key length. If you want a larger message, use a stream cipher.
-   Needs a key exchange protocol to exchange the (albeit small) key in advance.

## AES

-   AES is a substitution-permutation network.
-   It requires separate keys for each round in the next steps.
-   From one master key, it derives keys for each round.

The key is divided into 4 byte columns. The key is rotated and each
byte is passed through an S-box (substitution box) that maps it to
something else.

Then the column is XORed with a round constant. Then finally the
output is XORed with the previous round key.

## DES/3DES

DES is no longer considered secure: tiny key size of 56 bits.

Brute forced in less than a day nowadays.

In 3DES, the input is encrypted, decrypted, then encrypted
again. Since 3 different keys are used, cryptanalysis is harder than
in DES. Still a poor choice.

## Stream Ciphers

Message can be longer than key size. Naive way is to just split the
message based on key length and repeatedly encrypt. This is what ECB
(Electronic Code Mode) is.

ECB is not great since identical messages will lead to identical
ciphertext and the attacker can divide his message into blocks to get
this information. The oracle attack below explains how.

## Oracle attack

By carefully crafting inputs and getting them encrypted, an attacker
can recover other ciphertext as well.

e.g. Start by sending a message that's a byte shorter than the key
length. The encrypted block will have his full message + one extra
byte from the rest of the message. Note this and repeat for the full
key length with all possible combinations for the last byte. The one
that matches the first attempt tells him what the first byte is. Then
repeat for the penultimate byte and so on.

## CBC - Cipher Block Chaining

Plain text blocks are XORed with the previous ciphertext block before
the current round of encryption.

An Initialization Vector (a random number) is picked up for the very
first block. The IV need not be secret and can just be added to the
ciphertext as plain text.

CBC is decent but its use in TLS 1.0 was not: see BEAST (Browser
Exploit Against SSL/TLS). The problem was that, instead of using a
random number for the IV, the previous ciphertext block was used as
the IV for the next message.

Don't use the IV as the key, although it sounds convenient. Pick a
different, strong, random number.

CBC Bit Flipping attacks: By carefully crafting junk in the middle of
a message, an attacker can manipulate the plaintext in the subsequent
block, since the stuff he's inserted is going to be encrypted and then
XORed with the next block.

## Padding

You can pad a message with zeroes except for cases where the data
itself ends with zeroes. So PKCS#5 and PKCS#7 are better alternatives
(and later CMS).

In them, you take the number of bytes left to pad and pad them with
that value.

e.g. in the message is 01 23 45 22 .. .. ..

there are 3 bytes left to pad (assuming a block size of 8 bytes). So the message becomes:

01 23 45 22 03 03 03

CBC has a padding attack as well :(

Done using a ciphertext to decrypt and a padding oracle (this takes a
ciphertext and tells the attacker if the padding was correct or not)

Timing (and other Side Channel) attacks: by timing how long it takes
for a failure to be reported, an attacker can interpret if it was
rejected up-front as a padding failure or down the line as something
else.

## Native Stream Ciphers

These are built from the ground up to be stream ciphers. A synchronous
stream cipher produces a stream of cipher text using a symmetric
secret key.

In asyc stream ciphers, previously produced ciphertext is used as an
input for subsequent rounds. Rare, not recommended.

RC4 is an example and is pretty weak. The block ciphers are better so
far, except for the newer generation (Salsa/ChaCha below).

RC4's source code was leaked. It belonged to RSA Security. It was much
faster than its competitor 3DES then. AES came after it with similar
speed and better security.

Modern ciphers combine a long term key with a nonce, so that the same
key generates different streams. In RC4 they just appended the nonce
to the key (since RC4 had a flexible key length), so attackers were
able to recover parts of the combined key (and eventually the whole).

WEP was affected by this attack because it used the nonce in a
similarly crude way.

## Salsa20

A newer stream cipher designed by DJB.

ChaCha is a variant with increased amount of diffusion per round,
while maintaining or improving performance.

No known attacks against either of these. They're pretty fast too.

With Salsa you can also jump directly to a specific part of the
ciphertext to decrypt. Which also means chunks can be parallelized and
decrypted independently.

It is also resistant to side channel attacks: every block has a fixed
number of constant time operations.

Both these are based on an ARX design (Add Rotate XOR).

## CTR Mode of Operation

Here, a nonce is used along with a counter that increments for every
block. The nonce and the key are run through a block cipher to
generate a continuous key stream. The plaintext is XORed with the
keystream to produce the ciphertext. XORing again produces the
plaintext back.

As long as you don't reuse the nonce, an attacker cannot try
multi-time pad attacks.

## Bit flipping attacks

Can be done on stream ciphers as well: an attacker can flip a few
ciphertext bits and affect subsequent plaintext bits. For stream
ciphers it affects the same bit itself, not ones in the subsequent
block as for block ciphers.

If authentication is done along with encryption, a recipient can
simply discard such bad messages.

## Key Exchange

Diffie Helmann is a nice symmetric way to do it. Alice encrypts a
public key with her private component. Bob does the same to the public
key with his own private component. Then they send each other this
information and run it through their own private components. Since the
order doesn't matter, public component + private Alice + private Bob
is the same as public component + private Bob + private Alice. So both
parties have a shared key.

But in an MITM, Eve can intercept Alice and Bob and send messages to
each end with her own private key, and decrypt it locally. So we need
to add authentication to the mix: is Bob actually Bob or might it be
Eve? That's where Public Key Encryption comes in.

## Public Key Encryption

### RSA

Really really slow, so we use it just to come up with a key that a
stream cipher will then use. Also, RSA can't encrypt anything larger
than its modulus (2048 or 4096) so it just about suffices for a
secret, not for the whole message.

### MD5/SHA-1

Do not use.

### SHA-2

Family comprising SHA-224, 256, 384, 512, 512/224 and
512/256. Use. Performance better than SHA-1, and better collision
resistance.

### Keccak

Standardized as the SHA-3 family: SHA3-224, 256, 384, 512. Different
family than SHA-2.

## Salts/Rainbow tables

Rainbow tables are large sorted tables of commonly used passwords. To
avoid this, keep a separate column in the table for a salt, and
generate a large (160 bits/32 bytes) cryptograpically random salt for
each row. If you use the same salt for the entire table, the attacker
can simply create a new rainbow table for the entire DB and compare it
with the entries there. If a salt is per-user, he would have to repeat
this n times. This is not good enough though.

Probably the best recommendation is to use a low entropy key
derivation function.

## Message Authentication Codes (MACs)

Check authenticity / integrity of message. Often called
'tags'. Similar to a checksum but uses a secret key and combines with
the message to produce the tag.

-   Authenticate and Encrypt - SSH
-   Authenticate then Encrypt - TLS
-   Encrypt then Authenticate - IPSec (best!)

See Moxie's Cryptographic Doom Principle for more. Essentially, if you
do any cryptographic operation on a message before checking the MAC,
the system is doomed. Both the other options require a decryption
phase before the MAC is verified.

Authenticate and Encrypt is bad because the tag authenticates the
plaintext and then sends it out. So identical messages will have
identical tags.

prefix-MAC: Simply prefix a key to the message and hash the whole
thing. Works well with Keccak but not so much with other hashing
algorithms. Vulnerable to padding attacks (with some hashing
algorithms).  HMAC: Hash-based MAC.

## Authenticated Encryption Modes

Composing authenticated and encryption separately is fraught with
peril. Here are some methods that implement both as a fundamental
component of the system.

AEAD - Authenticated Encryption with Associated Data

Consists of the message and the metadata of the message. Unlike, say,
email, where the headers are not encrypted so that mail servers can
route mails, in AEAD systems, the metadata (headers in this case) can
be authenticated as a whole along with the message.

GCM mode (and by extension GMAC) is one such mode.

## Signature Algorithms

Consist of:

-   key generation algorithm
-   signature generation algorithm
-   signature verification algorithm

e.g. DSA (Digital Signature Algorithm), PKCS #1 v 1.5 etc. Basically
use a private component to sign a message so that others can use the
public component to verify it.

## Key Derivation Functions

Derives one or more secrets from a single secret. e.g. PBKDF2, bcrypt,
scrypt and HKDF.

## Linux /dev/random vs /dev/urandom

/dev/random takes in noise into an entropy pool from the environment
(network, device drivers, keyboard etc) and returns a strong random
stream. But if the entropy pool runs out it will block. So use
/dev/urandom, which will start with a seed from /dev/random and yield
a cryptographically secure PRNG stream from it. 'technically' weaker
then random, but won't halt.

## Attacks on TLS

CRIME and BREACH: Experts used to recommend compressing the plaintext
before encrypting it. These attacks found a nasty way to use this when
TLS or HTTP compression was turned on.

