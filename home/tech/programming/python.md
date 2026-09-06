---
title: "Python"
tags:
  - python
  - programming
---

# :material-language-python:{ .anim-heart } Python

## pip: upgrade all packages in a virtual env

```sh
pip list --outdated --format=freeze | grep -v '^\-e' | cut -d = -f 1  | xargs -n1 pip install -U
```

## Modern Python (2026 edition)

I use Python heavily and keep up with the evolving ecosystem. Here are the current standard tools and libraries.

### ruff

The "new hotness" in the Python world. It's an extremely fast linter and formatter written in Rust that replaces `flake8`, `black`, `isort`, and more.

```sh
pip install ruff
ruff check .      # Linting
ruff format .     # Formatting
```

### black (Legacy Formatter)

- Auto-formats your files, like `go fmt`. Still widely used but being superseded by `ruff`.
- I just selected this as the formatter in vscode. For manual usage, just pip install and run:

```sh
filegen/app ❯ black main.py
reformatted main.py
All done! ✨ 🍰 ✨
1 file reformatted.
```

### poetry

- Creates its own virtualenv so don't install it in one. Instead do this:

```sh
pip install --user poetry
```

Usage:

```sh
poetry new some-project # initializes folder structure for src, tests, toml file
```
Or if you already have a project and just want to initialize the .toml file:

```sh
poetry init
```

The `pyproject.toml` structure conforms to [PEP-518](https://www.python.org/dev/peps/pep-0518/).

Then, activate the virtual env with:

```sh
poetry shell
```

For adding packages, the only way is with:

```sh
poetry add <package>
```

This will update the toml file as well. You can then lock dependencies with:

```sh
poetry lock
```

### wait-for-it

Run a command when a port is open. Example:

```sh
wait-for-it --service 0.0.0.0:8000 -- curl localhost:8000
```

## Debugging

Here's a 2 liner that drops you into a shell:

```sh
python3 -m pdb -c continue script.py
```

For setting breakpoints, do this:

```py
breakpoint()
# or this:
import pdb; pdb.set_trace()
# or this if you want a better shell:
import ipdb; ipdb.set_trace()
```

Get help with `help pdb`.

There is also something called *development* mode for some extra runtime checks, turn it on with one of these:

```sh
python -X dev app.py
# or
PYTHONDEVMODE=1 app.py
```

This gives better stack traces on receiving system signals or segfaults, deprecation warnings, unsafe GIL usage etc.

There is also something called *development* mode for some extra runtime checks, turn it on with one of these:

```sh
python -X dev app.py
# or
PYTHONDEVMODE=1 app.py
```

This gives better stack traces on receiving signals, deprecation warnings, unsafe GIL usage etc.

## See python paths

This shows the location of the user's site-packages folder, the `sys.path` contents, etc.

```sh
python3 -m site
```

## Merging dictionaries

Newer python versions:

```py
>>> {'a':1,'b':2} | {'b':20,'c':30}
{'a': 1, 'b': 20, 'c': 30}
```
Right most dict gets the value if there's a clash.

Alternative way, using `collections.ChainMap`:

```py
>>> import collections
>>> collections.ChainMap({'a':1,'b':2}, {'b':20,'c':30})
ChainMap({'a': 1, 'b': 2}, {'b': 20, 'c': 30})
>>>
```

In this case the left dict gets priority. ChainMap just uses the referenes so if the underlying
dicts change, ChainMap knows about it.

## Type Hints

Generic types: `tuple`, `list`, `dict`, `set`, `frozenset` etc. For dicts you need to use
`dict[KeyType, ValueType]`. There is also `typing.Any` if your return value is unknown, for
instance.

## map/filter/reduce

Map takes the function (in this case just squares your input), and applies it to the iterable (in
this case the `range`).

```py
list(map(lambda x: x**2, range(10)))
```

Filter takes an iterable and runs a function against each element one by one. e.g. to prevent even numbers:

```py
list(filter(lambda x:  x%2 == 0, range(10)))
```

Reduce is now in `functools`. It reduces an iterable to a single value. i.e. it takes `reduce(func,
[a, b, c, d])` and does this: `func(func(func(a, b), c), d)`. E.g to sum numbers in a range:

```py
from functools import reduce
reduce(lambda x, y: x + y, range(10))
```

Since these returns an iterator, you can call `next()` to get the next result.

## Concurrency

Best definition is from Leslie Lamport:

> "Two events are concurrent if neither can causally affect the other."

So, concurrency is a propery of a program or problem or algorithm, while
parallelism is one of the ways of achieving this.


### multithreading

- Use `Queue` for communication
- Use thread pools and throttling so you don't overload yourself (or
  the remote party)
- Don't print inside threads, send your output to a results queue and
  print in main() at the end

### multiprocessing

The in-built `multiprocessing` package has interesting tools for
sharing data:

- `Pipe` for simple socket-like 2 way communication. Has a `send()`,
  `recv()` etc.
- `Queue` which is just like the standard queue
- `sharedctypes` for C types in a dedicated pool of memory

You can replace `multiprocessing` with `multiprocessing.dummy` and you
write exactly the same code but with threads instead of processes in
the background.

### async

This is co-operative so someone must relinquish execution control so
that the next process can get a slice.1

You can feed a bunch of coroutines to `asyncio.gather()`. It returns a
single `future` object, which can then be run in the even loop.

Use `await asyncio.sleep()` instead of `time.sleep()` to yield control.

Use `concurrent.futures` to take a synchronous library and run it
under the hood in a multithreaded manner but by using async
patterns. It has a `ThreadPoolExecutor` and `ProcessPoolExecutor` to
do so. Once you `submit` a function to these, you will get back a
`Future` object, and you can get the actual result in
`Future.result()`. Instead of `run_in_loop` you would do a
`run_in_executor`.

## Event-Driven Programming

- Callback-based: 1:1 binding between the object that emits the event and the
  handler that executes some logic based on that event. e.g. GUI toolkits.
- Subject-based: Many subscribers can `register` to a Subject, which will then
  `notify` all subscribers whenever any event is triggered. one-to-many.
- Topic-based: Write to a topic, and forget about it. One or more handlers can
  subscribe to that topic. Completely decoupled.

## Metaprogramming

Useful packages:

- `inflection`
- `macropy3`
- `falcon`
- `hy`

Class decorators return a class instead of a function object, example
`@dataclass` and `@runtime_checkable`.


---

## Design patterns

### Observer:

-   Like a presence subscription. multiple obvservers get notified when
    a core object changes.
-   Also see @property to create setters/getters for attributes. That
    way when an attribute changes, we can make a call to update() and
    let the observers know.

### Strategy:

-   Different implementations hidden beneath a single
    abstraction. e.g. user calls sort() but does not care which
    algorithm is used.
-   Create different classes and implement `__call__`, so that when an
    object is created, that function is called automatically.

### Template:

-   Differing steps in separate classes, one controller.

## Unicode, and Encode vs Decode

-   `bytes.decode`: interpret a stream of bytes (from a file or the
    network) as unicode, with a passed charset like UTF-8 or latin-1.
-   `str.encode`: take a unicode string and convert it to bytes, to write
    to file or send over a network.
-   **deep breath** both byte strings and unicode have a method to convert
    to the other. byte.decode('utf-8') takes a byte stream and
    represents it as a UTF-8 string. utf.encode() takes a utf-8 string
    and represents it as a byte stream (to send out over a network, for
    example).
-   `encode()` accepts an arg that allows you to represent as ascii, but
    replace out-of-range characters with ???? or something else.
-   Python2: str: stream of bytes, unicode: unicode.
-   Python3: str: unicode, bytes: stream of bytes.
-   Python2 implicitly tries to change bytes to unicode and vice versa
    to be 'helpful'. Python3 doesn't.
-   A recommendation: bytes on the outside -> decode to utf-8 -> use
    unicode inside -> encode to bytes -> send out.
-   `IOBuffer` and `FileBuffer` are like dummy network/file interfaces
    (useful for tests?)
-   ISO-8859-1 aka Latin-1 is a single byte extension to ascii that
    supports a few extra symbols.

## Coverage usage

Run this:

``` sh
coverage run scriptname args
```

Results are stored in `.coverage`. If the script has different args,
backup `.coverage`, run again and then combine them:

``` sh
coverage combine .coverage.old .coverage
```

For a quick summary (`-m` specifies the missing lines):

``` sh
coverage report -m
```

For a report (`-d` specifies the dest folder):

``` sh
coverage html -d coverage_html
```

## Decorator example

``` py
def my_decorator(func):
    def wrapper(*args, **kwargs):
        # do pre-processing
        ret = func(*args, **kwargs)
        # do post-processing
        return ret
    return wrapper
```

i.e., return a function (wrapper) that calls func with its args, but
do your pre/post stuff within wrapper.

## Django notes

-   Change your models (in models.py).
-   Run `python manage.py makemigrations` to create migrations for those changes
-   Run `python manage.py migrate` to apply those changes to the database.

## Magic number

The python interpreter's magic number is found in:

``` py
importlib.util.MAGIC_NUMBER
```

.pyc file format:

`magic number | mtime | size | marshaled code object`

## Dunder methods

-   String/bytes representation

`__repr__, __str__, __format__, __bytes__`

-   Conversion to number

`__abs__, __bool__, __complex__, __int__, __float__, __hash__, __index__`

-   Emulating collections

`__len__, __getitem__, __setitem__, __delitem__, __contains__`

-   Iteration

`__iter__, __reversed__, __next__`

-   Emulating callables

`__call__`

-   Context management

`__enter__, __exit__`

-   Instance creation and destruction

`__new__, __init__, __del__`

-   Attribute management

`__getattr__, __getattribute__, __setattr__, __delattr__, __dir__`

-   Attribute descriptors

`__get__, __set__, __delete__`

-   Class services

`__prepare__, __instancecheck__, __subclasscheck__`

## Pickling

-   The last byte of a pickled file is a '.' Anything that follows it is ignored.
-   This would be a way to embed a jpeg or something to the end of a pickle file..??

## Staticmethod vs Classmethod

-   staticmethod: can be called directly from the class, without instantiating an object.
-   classmethod: exactly the same.
-   BUT: when a staticmethod is called from an object, the 'self'
    parameter is never passed, the way it is for classmethods and normal
    methods.

## Import files with hyphens

``` py
test_cmd = importlib.import_module('test-cmd', None)
```

