---
title: "Programming"
tags:
  - programming
  - development
  - coding
---

# :material-code-tags:{ .anim-rotate } Programming

Check these pages for language-specific notes:

- [Python](python.md)
- [Go](go.md)
- [Java](java.md)

## Other languages

### HTML / CSS

#### HTML header

``` html
<html lang="en">
```

-   Here `lang` is an 'attribute', with value `en`.
-   `html` is the tag.
-   `head` has metadata, one of which is `title` (to fill the tab bar).
-   `html` has tags for 'article', 'header', and 'figure' now!

#### CSS

-   Use classes to segregate your content. Call it with a leading '.' in css. e.g.

``` css
.site-nav-header { width: 300 px }
```

-   ID's on the other hand can only be used once per html page. use with
    leading '#' in css. e.g.

``` css
##main-title { color: green }
```

#### FORMS

``` html
<label for="nickname">Please enter your nickname</label>
<input type="text" id="nickname" name="nickname">
```

-   The label's `for` should match the input's `id`
-   The `name` is what is passed to the backend as a variable name
-   `input type` can be a lot of things, like 'email' or 'submit'

-   All of these: labels, inputs etc are inline-block elements and are
    therefore stacked horizontally.
-   To align them better, use div's, which are container tags that break
    up these horizontal elements into vertical stacks.

There are 3 groups of elements in the way the browser stacks them:

-   inline: span, em, strong (all treated horizontally)
-   block level: p, div, article (browser inserts CRLF)
-   inline block level : input, textarea (can be resized)

### tcl: xml parsing example

``` tcl
package require tdom
set dom [dom parse $XML]     
set recording [$dom documentElement]
set datamode [$recording firstChild]
set session [$datamode nextSibling]
$session attributes *
$session getAttribute session_id
set participant [$session nextSibling]
set dom [dom parse $XML]     
set recording [$dom documentElement]
```

## Other study notes

### TCP

-   Use `SO_REUSEADDR` when stopping/starting servers: the OS will keep a
    socket alive for ~4 minutes after it's closed in case it has to
    retransmit FINs/ACKs.
-   Deadlocks occur if the OS buffers fill up in both ends. e.g. client
    send blocks of data, server has a `recv(1024)` and processes and
    sends data (say, 1024), but client only has a recv of say, 10. Then
    his buffer gets filled up since he's getting a lot more data than he
    can handle. so the server's sends stop working. similarly the
    server's recv fills up &#x2026;
-   Either can call `socket.shutdown`, e.g. if you're a client who's
    finished sending data and wants to notify this. The connection stays
    open so he can continue getting data. `shutdown`'s flags will stop
    reads, writes, or both.
-   Address families: pretty much always `AF_INET`. `AF_UNIX` is for local
    file sockets. bluetooth etc also exist. Oh `AF_INET6` also exists.
-   Socket type: `SOCK_DGRAM` (2) and `SOCK_STREAM` (1). (each address
    family has its own udp/tcp equivalents under the dgram/stream types)
-   Last field is protocol which can be zeroed/ignored. `IPROTO_TCP` is
    6 and `IPROTO_UDP` is 17. but we can infer it from the socket type
    above so we don't need to set it each time.

-   To avoid v4/v6 and other binding confusions, use
    `getaddrinfo(host,port)` : it returns FTPCA (family, type, protocol,
    canonical name and address)

-   Use `socket.getservbyname(53)` to see port->service mappings.
-   Similarly `socket.gethostbyname('abc.com')` or `gethostbyaddr('1.2.3.4')`
-   So self ip address is `socket.gethostbyname(socket.getfqdn())`

### Unicode in DNS:

-   RFC 3492 specifies the IDNA codec that maps a unicode hostname to an
    ascii representation.
-   The lookup is performed for the encoded ascii string only.

### UTF-8

-   utf-8: 1-4 bytes. use setlocale() to switch encodings

### example of unicode encoding:

-   character "¢"= code point U+00A2 = 00000000 10100010 → 11000010
    10100010 → hexadecimal C2 A2
-   explanation: if the actual code is 00000000 10100010, then the
    representation starts with a 11 (to show that 2 bytes are needed to
    represent this character), followed by the data. The continuation
    bytes always start with a 10.

### example 2:

-   The following string contains 4 utf-8 characters:

    "\xD4\xBC\xF0\x9D\x90\x84\x45\xC6\xAC\x00"

-   D4 converted to Hex is 11010100 which tells us (from the first 2
    bits) that 2 bytes take up this character. similarly F0 == 11110000
    which takes 4 bytes to specify the next character, and so on.
-   Do not modify strings directly in C (the compiler may store multiple
    identical string literals in the same address, so modifying one will
    affect the other)

### Levenshtein Distance

-   Used in fuzzy searching (e.g. 'git lgo' which autocorrects and recommends 'log')
-   Used to measure the difference between two strings

### Algorithmic Complexity

<table border="2" cellspacing="0" cellpadding="6" rules="groups" frame="hsides">


<colgroup>
<col  class="org-left" />

<col  class="org-left" />

<col  class="org-left" />
</colgroup>
<thead>
<tr>
<th scope="col" class="org-left">Notation</th>
<th scope="col" class="org-left">Type</th>
<th scope="col" class="org-left">Example</th>
</tr>
</thead>

<tbody>
<tr>
<td class="org-left">O(1)</td>
<td class="org-left">Constant Time</td>
<td class="org-left">Dict Lookup</td>
</tr>


<tr>
<td class="org-left">O(lg n)</td>
<td class="org-left">Logarithmic</td>
<td class="org-left">Binary Search</td>
</tr>


<tr>
<td class="org-left">O(n)</td>
<td class="org-left">Linear</td>
<td class="org-left">Iterating over a list</td>
</tr>


<tr>
<td class="org-left">O(n log n)</td>
<td class="org-left">Log Linear</td>
<td class="org-left">Optimal sorting of arbitrary values</td>
</tr>


<tr>
<td class="org-left">O(n<sup>2</sup>)</td>
<td class="org-left">Quadratic</td>
<td class="org-left">Comparing *n* objects to each other</td>
</tr>


<tr>
<td class="org-left">O(n<sup>3</sup>)</td>
<td class="org-left">Cubic</td>
<td class="org-left">Floyd and Washall's algorithms</td>
</tr>


<tr>
<td class="org-left">O(nk)</td>
<td class="org-left">Polynomial</td>
<td class="org-left">*k* nested loops over *n*</td>
</tr>


<tr>
<td class="org-left">O(n!)</td>
<td class="org-left">Factorial</td>
<td class="org-left">Producing every ordering of *n* values</td>
</tr>
</tbody>
</table>


