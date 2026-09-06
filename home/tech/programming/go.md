---
title: "Go"
tags:
  - go
  - programming
---

# :simple-go:{ .anim-pulse } Go

Notes from the book *Learning Go*, by Jon Bodner.

## Setup, Environment

### Difference between `go get` and `go install`:

See [here](https://stackoverflow.com/questions/24878737/what-is-the-difference-between-go-get-and-go-install#24878851).
Basically `go get` downloads the source to $GOPATH/src along with the
dependencies, and the latter compiles.

`go install` is recommended. Ignore `go get`.

### Hey
[hey](https://github.com/rakyll) for load testing http services. Install with:

`go install github.com/rakyll/hey@latest`

### Vi

Install vim-go: it comes with a massive set of tools.

### goimports
[goimports](https://pkg.go.dev/golang.org/x/tools/cmd/goimports) for some neat stuff that gofmt doesn't do. Install with:

`go install golang.org/x/tools/cmd/goimports@latest`

And run with:

`goimports -l -w .`

Vi: Just save it.

### Linting with golint

Install: `go install golang.org/x/lint/golint@latest`

Run: `golint ./...`

Vi: `:GoLint`

### SA with govet

Run: `go vet ./...`

Vi: `:GoVet`

This does not catch subtle bugs around shadow variables. So consider installing `shadow` as well:

Install: `go install golang.org/x/tools/go/analysis/passes/shadow/cmd/shadow@latest`

Run: `shadow ./...`

### Combine golint, govet with golangci-lint

This tool runs 10 different linters by default and support dozens others.

Install: [see official docs](https://golangci-lint.run/usage/install/)

Run: `golangci-lint run`

### vim-go notes

- Code completion is with `Ctrl-x Ctrl-o`
- `:Tagbar` is bound to `F8`
- `:GoDef` is bound to `gd`
  - :`GoDefStack` shows you how deep you've jumped, `GoDefPop` or `Ctrl-T` just
  pops to the last hop

### Sample makefile

```
.DEFAULT_GOAL := build

fmt:
        go fmt ./...
.PHONY:fmt

lint: fmt
        golint ./...
.PHONY:lint

vet: fmt
        go vet ./...
        shadow ./...
.PHONY:vet

build: vet
        go build hello.go
.PHONY:build
```

## Basic Types

### Type Conversions

Very strict here unlike JS / python.  One can't just treat non-empty strings
like "asd" as true for example.  No other type can be converted to a bool, even
explicitly.  The way to do that is to use comparison operators (==, !=, >=,
<=).

e.g. `x == 0` will return `true` or `false`.

### var versus :=

Most verbose way:

`var x int = 10`

Since the default type of an integer is `int`, we can omit that:

`var x = 10`

And since the default value is 0, we can also do this:

`var x int`

Multiple variables can be declared like this:

`var x, y int = 10, 20`

Even if types differ:

`var x, y = 10, "hello"`

For even more in one go, do this:

``` go
var (
	x int
	y = 20
	z int = 30
	d, e = 50, "hello"
	f, g string
)
```

Inside a function, you can use `:=` when you want go to infer the type.

`var x = 10`

becomes

`x := 10`

Or

`x, y := 10, "Hello"`

And so on.. The main difference here is that you can reassign to existing
variables too.

Recommendations / Idioms: 

- Don't declare variables at the package level, especially if they change
later. Keep only immutable variables there, and the rest inside functions.
- Don't use `:=` with type conversions, just use `var` there.
- If initialization to 0 is expected, use `var x int` instead of `x := 0`.

### const

Only works at compile time, so can only be assigned to:

- Numeric literals
- `true` and `false`
- Strings
- Runes (A rune is a single unicode character I think)
- Other built-ins: complex, real, imag, len, cap
- Expressions that consist of operators and the preceding values

So there's no way of specifying that a value calculated at runtime is
immutable. Nor are there immutable arrays, slices, maps or structs.

!!!tip
    Keep a const untyped so you have more flexbility.

`const x = 10`

let's you later do this:

```go
var y int = x
var z float64 = x
var d byte = x
```

As you'd expect, doing something like `const x int64 = 0` can only let you
assign that const to another int64.

### Unused variables

Not applicable to const's since these are detected and stubbed out from the
final binary. For normal vars though, its a compilation error to declare a var
and not use it.

## Composite Types

### Arrays

Rigid, don't use directly.

`var x [3]int` // Default 0's

`var x = [3]int{10, 20, 30}`

Sparse arrays: 0's are filled for the positions not specified:

`var x = [12]int{1,5:4,6,10:100,15}` // this creates {1,0,0,0,0,4,6,0,0,0,100,15}

`var x = [...]int{10,20,30}` // tell go to fill in the size

`var x [2][3]int` // multi-dimensional. Poor matrix support, avoid.

Find the size with `len(arr)`. 

Limitations:

- The size is part of the type, so an `[3]int` is not the same type as a
`[4]int`. So you CANNOT use a variable to specify the size of an array, because
types must be resolved at compile time. Big limitation of arrays.
- One CANNOT use a type conversion to convert arrays of different sizes to
identical types. Because of this, you can't write a function that works with
arrays of unspecified sizes, nor can you assign arrays of different sizes to
the same variable.

Really just don't use this. Arrays are backing stores for slices and this is
what you'd want to use.

### Slices

Length is /not/ part of the type. You don't specify the size when declaring:

`var x = []int{10, 20, 30}` //Note that in an array you'd do [...] instead

Similarly:

`var x = []int{1, 5:4, 6, 10:100, 15}`

`var x [][]int`

Empty slice:

`var x []int` // Since no value is assigned, x is assigned `nil`

!!!note
    Slices aren't comparable with each other with `==`, `!=` etc. Only with `nil`.
    Use `reflect.DeepEqual` if you want to compare two slices.

Use `append` to grow a slice:

``` go
var x []int
x = append(x, 10)
x = append(x, 11, 12)
```

To flatten one slice and append its values to another, use `...`:

```go
y := []int{20, 30, 40}
x = append(x, y...)
```

!!!note
    Observe that we assign the value returned by `append`. This is because Go
    is call-by-value. Every time you pass a parameter to a function, Go makes a
    copy. So append works on the copy and returns it back to the caller. So we
    re-assign the new value to that variable.
    
#### capacity

The Go runtime will increase the size of a slice when the number of elements
exceeds the default allocation, e.g. by doubling it or increasing by 25%, based
on the number of elements that are already there.

The built-in function `cap` returns the current capacity of the slice, and
`make` is used to create a new slice.

#### make

Like malloc. Will create a slice of fixed capacity and length, and initialize
to 0.

`x := make([]int, 5)`

!!!warning
    You can NOT use `append` to populate contents after a `make` like this.
    Reason: `make` will zero fill the slice and append will add the new values
    to the end. `append` *always* increases the length of a slice.

To specify initial capacity as well:

`x := make([]int, 6, 10)`

`x := make([]int, 0, 10)` // 0 length but 10 capacity

Runtime panic if you initialize a slice with a variable for the capacity and it
turns out to be lesser than length. Or compile time if you do it with literals.

#### idiomatic way of declaring slices

- `var data []int` // if you expect it to stay nil. Has 0 length
- `var x = []int{}` // empty slice literal i.e. non-nil
- `data := []int{2, 4, 6, 8}` // if you feel the values aren't going to change
- Use `make` when you have a good idea of the size.
- When unsure, use a zero length slice with a specified capacity so that
`append` works easily.

#### slicing

Similar to python. But does NOT copy the data. You get two variables that share
the same data. This gets really messy when you `append` to a sliced slice :(
The sub-slice shares the capacity of the main slice, so unused capacity in the
original slice is used when you do the append.

!!!warning
    Never use `append` with subslices. If you have to, use it with a *full
    slice expression*, which includes a third arg that specifies the last
    position in the parent slice's capacity that's available of the subslice.
    E.g.
    
    `y := x[2:4:4]` //Subslice y does not share anything beyond the 4th
    position with the parent.

#### copy

Safe way of creating an independent slice.

```go
x := []int{1,2,3,4}
y := make([]int, 4}
num := copy(y, x) // Returns number of elements copied. Y is the target slice.
fmt.Println(y, num) // Prints [1 2 3 4] 4
```

### Strings, runes, bytes

UTF-8, unless specified.

`len()` gives you the raw byte length not the grapheme length.

`byte` is the underlying structure, `rune` is the UTF code point, and `string` is what the user sees.


### Maps

Make a map where key is a string, value is an int:

```go
	m0 := map[string]int{}
	m0["asd"] = 1
```

Set values up front:

```go
	m1 := map[string]int{
		"hello": 1,
		"world": 2,
	}
```

for the above, extract and test like this:

```go
	v, ok := m1["hello"]
	fmt.Println(v, ok)
    // Returns, 1 true
	v, ok := m1["does-not-exist"]
	fmt.Println(v, ok)
    // Returns, 0 false
```

i.e. Value stored in the map is `1` and there is indeed a value present for that map (stored in the `ok` variable)


`delete(m1, "hello")` deletes that key/value.

### Sets

Don't exist natively but you can make a map with bool values to
get a similar data structure.

```go
	myset := map[int]bool{}
	vals := []int{1, 3, 5, 7, 1, 10, 11, 3}

	for _, v := range vals {
		myset[v] = true
	}
```

Use third-party libraries for Union, Intersection, etc.

### Structs

```go
	type person struct {
		name  string
		empid int
	}
	var e1 person
	e1.name = "arun"
	e1.empid = 12345
    // or
	e2 := person{"sid", 5678}
```

#### Anonymous struct

```go
	pet := struct {
		name string
		age  int
	}{name: "shadow", age: 10}
```

!!!note
    Type conversions between 2 structs are ONLY possible if order and
    names and types all match.

## Blocks

Anything outside a function is in the *package* block.

Anything you call with an import from another file is in the
*file* block.

And things within functions are in their blocks.

There is also a *universe* block that contains all the built-in
types and functions like `true` and `int` and `make`.

!!!warning
    Variables with the same name in an inner scope are
    *shadowed*. So any change you make are not retained once Go
    moves back to the outer scope.

```go
	x := 10
	if x > 5 {
		fmt.Println(x)  // 10, from outer scope
		x := 5          // new shadow variable
		fmt.Println(x)  // 5
	}
	fmt.Println(x) // You'd want it to be 5, but it's 10
```

The use of `:=` makes it easy to miss this, which reuses
variables only in the current block.

Consider installing `shadow` which catches this kind of thing:

```sh
code/learninggo/ch04 via  v1.16.3 ❯ shadow blocks.go
/home/arunsrin/code/learninggo/ch04/blocks.go:9:3: declaration of "x" shadows declaration at line 6
code/learninggo/ch04 via  v1.16.3 ❯
```

### if

Fairly obvious. Also, let's you define a variable inside the if
condition that you can then use in the rest of the block.

### for

Simple, C-style:

```go
	for i := 0; i < 5; i++ {
		fmt.Println(i)
	}
```
- Must use `:=` to initiatlize, `var` will not work.
- No parens

Condition-only style:

```go
	for i > 0 {
		fmt.Println(i)
		i--
	}
```

Infinite style:

```go
	for {
		fmt.Println("loop forever")
	}
```

- Use with `break` and `continue`

for-range style:

```go
	x := []int{100, 200, 300}
	for i, v := range x {
		fmt.Println(i, v)
	}
```

- `i` gives the iteration, and `v` the value
- When looping through a map, `i` gives the key instead
- Use `_` if you don't plan to use that variable in the loop
- Iteration over maps is random, no fixed order is guaranteed
- If you loop over a string, each element will be a `rune`, not a `byte`
    - The `i` value will jump by that many bytes to indicate that a
  non-ascii UTF symbol was detected
- `for` copies `i` and `v` and gives it to you. So modifying it
will not modify the upstream value you're iterating through.

### switch

Example:

```go
	words := []string{"a", "cow", "gopher", "smile", "octopus",
		"anthropologist"}
	for _, word := range words {
		switch size := len(word); size {
		case 1, 2, 3, 4:
			fmt.Println(word, " is a short word")
		case 5:
			wordLen := len(word)
			fmt.Println(word, " is the right length: ", wordLen)
		case 6, 7, 8, 9:
		default:
			fmt.Println(word, " is a long word")
		}
	}
```

- No `break` needed
- Each switch case is a scope, introduce new variables there and
they will be accessible only in that case
- In an empty case, *nothing happens*. There is no fall-through
to the next case
    - Rather, use commas to combine multiple cases that have the
    same logic
- `break` in a switch case will only break out of that case. Use
labels to actually break out of the outer loop

### Blank switch

In the previous example, `size` compared with each `case`
statement, and, if equal, that case is executed. In a blank
switch, you could run any condition in the case, not just
equality

## Functions

- No named or optional functional parameters.

### Variadic functions

Exception is when it's at the end:

`func blah(base int, rest ...int)`

- Use it in the function as a normal slice
- It can be skipped or called with any number of args

```go
func main() {
	blah(1, 2)
	blah(1)
	lotsOfArgs := []int{2, 3, 4}
	blah(1, lotsOfArgs...) //Note trailing ... for slice
}

func blah(base int, rest ...int) {
	fmt.Println("Received this many rest args", len(rest))
}
```

### Mutliple return values

Example 

`func div(num int, denom int) (int, error) {...}`

Fairly common pattern to return the actual response followed by
an `error` type

!!!note
    Has to be assigned to each variable on the calling side, you
    can't just treat it as a tuple and assign to a single
    variable like in python

### Named return values

Example 

`func div(num int, denom int) (result int, err error) {...}`

Advantage is that you are pre-declaring that those variables are
present in the function and initialized to default values.

On the calling side, feel free to use any other name.

### Blank returns

Example

`return`

!!!warning
    Don't use!

It returns the last value of a named return variable.. not
idiomatic and prone to cause confusion.

### Passing functions

Here's a simple example:

```go
func main() {
	var opMap = map[string]func(int, int) int{
		"+": add,
		"-": sub,
	}
	opFunc := opMap["+"]
	res := opFunc(5, 10)
	fmt.Println(res)
}

func add(i int, j int) int { return i + j }
func sub(i int, j int) int { return i - j }
```

!!!warning
    The example above is pretty poor. You would have quite a bit
    more error correction in the real world

### Function Type Declarations

`type opFuncType func(int, int) int`

More to come later but it's essentially like above.

That would make the map in the above example much simpler:

`var opMap = map[string]opFuncType {...}`

### Anonymous functions

```go
	i := 10
	func(j int) {
		fmt.Println("inside anon function", j)
	}(i)
```

Useful while launching goroutines or with `defer`

### Closures

Functions inside functions. They can use and modify variables
from the outer function.

```go
	type Person struct {
		name string
		age  int
	}
	people := []Person{
		{"asha", 7},
		{"sid", 5},
	}

	fmt.Println(people)
	sort.Slice(people, func(i int, j int) bool {
		return people[i].age < people[j].age
	})
	fmt.Println(people)
```

Here, `sort.Slice()` gets a function with 2 parameters `i` and
`j` but it has access to `people` as well.

You can even return a function from another function:

```go
func main() {
	f1 := makeMult(10)
	fmt.Println(f1(20))
}

func makeMult(base int) func(int) int {
	return func(factor int) int {
		return base * factor
	}
}
```

!!!note
    All of above are *Higher-order functions*, i.e. those that
    take a function as a parameter, or as a return value

### defer

Here is a simple `cat` implementation. It uses `defer` to close
file handles. `defer` is used to run something at the end of a
function, whether it ran successfully or not.

```go
package main

import (
	"io"
	"log"
	"os"
)

func main() {
	// simple `cat` implementation
	if len(os.Args) < 2 {
		log.Fatal("No file specified")
	}
	f, err := os.Open(os.Args[1])
	if err != nil {
		log.Fatal(err)
	}
	defer f.Close()

	data := make([]byte, 2048)
	for {
		count, err := f.Read(data)
		os.Stdout.Write(data[:count])
		if err != nil {
			if err != io.EOF {
				log.Fatal(err)
			}
			break
		}
	}
}
```

Note that if that function that you defer returns some values,
there is no way to actually read and use them.

Another good pattern is to write your own cleanup function and
then pass it to defer. E.g. if interacting with a DB, you may
want to either commit or rollback everything at the end.

Another pattern is to return a closure function alongside the
usual content and error. That way the caller can call it
themselves in their defer.

Example:

```go
func getFile(n string) (f os.File*, func(), error) {...}
```

So that the caller can do this:

```go
    f, cleanup, err := getFile("/etc/passwd")
    // check for err
    defer cleanup()
    // do the rest
```

### call by value

Anything you pass as a parameter is copied. Making modifications
to it will NOT stick, if you pass a struct or int or string.

If you pass a map or slice, you can modify the content but not
the size.

## Pointers

Example:

```go
var y int32 = 10
pointerx := &y  //pointerx's content is now y's address
var pointerz *string  //nil pointer, doesn't point to anything
```

Differences from other languages:

- No memory management
- No pointer arithmetic

`&` is an address operator that returns the address of that variable.

`*` is the indirection operator. Using it returns the value in that address.
Called *derefencing*.

Example:

```go
	var x int = 10
	pointerY := &x
	var z int = x + *pointerY
	fmt.Println(z)
```

Always do a null check!

```go
	var nilPointer *int
	if nilPointer != nil {
		fmt.Println(*nilPointer) // panic here
	}
```

`new` creates a new null pointer, but is not used much: 

```go
    var x = new(int)
```

You cannot point to builtins like ints and strings directly. You
will need to assign them to a variable and then make a pointer of
that variable.

Pointers in structs are a pain for this reason, you cannot assign
a string or int directly to them.  A good pattern is to have a
helper function that basically takes each type and returns a
pointer to that type:

```go
func stringp(s string) *string {
	return &s
}
```

Use Pointers to indicate mutability in a function. Since go is
call by value, a copy is always made of the paramter passed to
the function, and any change you make inside are not going to
reflect on the outside.

The above note is for primitives, structs, and arrays. More to
come on maps and slices.

Anyway, a better pattern is to just return the modified content
rather than modify it via pointers.

Commonly used in json parsing though.

!!!note
    If you pass a nil pointer to a function, it cannot modify it.
    You can only a modify a pointer that has valid content.

### Json parsing

```go
	type person struct {
		Name string `json:"name"`
		Age  int    `json:"age"`
	}
	var f person
	err := json.Unmarshal(
		[]byte(`{"name":"arunsrin","age":38}`), &f)
	fmt.Println(f, err)
```

The json library expects an `interface{}` in the second parameter
since it cannot anticipate the type. So the value passed to it
*has* to be a pointer. The lack of generics has led to the above
pattern become a norm in this use case.

There is a perf *hit* if you use pointers for small data. Becomes
an advantage only for large structs (~mb).

### Maps vs slices

A map is internally implemented as a pointer to a struct. So when
passing maps to functions and modifying them inside, you would
see a change on the outside as well.

So avoid using maps, especially for public consumption.

Slices are more complicated when passed as parameters to
functions:

- Change in values are reflected
- But appending to a slice is not affected

This is because when passed to the function, a copy of the
*length*, *capacity* and *pointer* are made. So a change in
content is because of the pointer pointing to the same common
content. But an append results in an increase in length and
capacity of the copy and not the original.

!!!note
    Because of all the above it is simply best to assume that a
    slice is not modifiable.

### Using slices as buffers

A good pattern is to make a single slice of fixed size and use it
in a loop while processing I/O. This is better than allocating
memory for each chunk, which leads to the GC having to do a lot
of work.

Here is an example:

```go
package main

import (
	"fmt"
	"os"
)

func main() {
	file, _ := os.Open("/etc/passwd")
	defer file.Close()

	data := make([]byte, 100)
	for {
		count, err := file.Read(data)
		if err != nil {
			break
		}
		if count == 0 {
			break
		}
		process(data[:count])
	}
}

func process(d []byte) {
	fmt.Print(string(d))
}
```

As you can see, data is declared once and reused repeatedly when
it is passed to `process()`.

While the length cannot be modified, `process()` can change the
content that was sent to it.

## Types, methods, interfaces

An *abstract type* specifies what a type should do, not how it is
done.

A *concrete type* specifies what and how.

Here's a function attached to a struct:

```go
func main() {

	c := ComplexNumber{3.55, 10}
	fmt.Println(c.toString())

}

type ComplexNumber struct {
	Real      float32
	Imaginary float32
}

func (c ComplexNumber) toString() string {
	return fmt.Sprintf("%0.1f + %0.1f i", c.Real, c.Imaginary)
}
```

You can attach the same method name to different types. The bit
between `func` and the name `toString()` is called the *receiver*
spec. You should use a pointer receiver if you intend to mutate
it (or handle *nil* instanes). Otherwise use a simple value
receiver.

Also the function has to be in the same package level. You can't
take a type from some package and override with a function in
yours.

Modified version of the above with 1 pointer receiver and the
other normal receiver:

```go
func main() {

	c := ComplexNumber{3.55, 10}
	fmt.Println(c.toString())
	c.increment() //observe that you didn't have to do &c.increment() here. Go does it automatically
	fmt.Println(c.toString())

}

type ComplexNumber struct {
	Real      float32
	Imaginary float32
}

func (c ComplexNumber) toString() string {
	return fmt.Sprintf("%0.1f + %0.1f i", c.Real, c.Imaginary)
}

func (c *ComplexNumber) increment() {
	c.Real++
	c.Imaginary++
}
```

!!!note
    getters and setters are not idiomatic. Just access directly.

### iota

Equivalent of enums. Seems pretty crippled, ignore.

Initializes to 0 and auto-increments from there on.

```go
	type MailCategory int
	const (
		Uncategorized MailCategory = iota
		Personal
		Spam
		Social
		Advertisements
	)
	x := Spam
	fmt.Println(x)
```

### Inheritance

Not exactly. But you can *embed* a type in another. So the
former's methods can be accessed in the outer type seamlessly.

### Interfaces

Example:

```go
	type Stringer interface {
		String() string
	}
```

Here, an implementation must implement a `String()` method.

Idiom is to end the name with `er` e.g. `Stringer()`, `Closer`.

A concrete type does not need to declare that it implements a
particular interface, it implicitly happens. Like python's duck
typing.

!!note
    Idiom: Accept interfaces, return structs

### interfaces and nil

For an interface to be nil, both the type and the value must be
nil.

When the type is non-nil, it apparently is not straightforward to
tell if the value is nil. Reflection helps here.

### empty interfaces

They map to anything in go, and main use case is for open-ended
stuff like json parsing.

```go
    var i interface{} //empty interface
    i = 10
    i = "hello"
    i = struct {
      FirstName string
      LastName string
      } {"A", "S"}
```

So in the json parsing case you'd see something like this:

```go
    data := map[string]interface{}{}
```

The first `{}` is for making an empty interface, the second `{}`
is for instantiating a map instance.

### Type assertions and type switches

```go
type MyInt int

func main() {
	var i interface{}
	var mine MyInt = 20
	i = mine
	// i2 := i Fails in last line with error `(mismatched types interface {} and int)`
	i2 := i.(MyInt)
	fmt.Println(i2 + 1)
}
```

Basically here we tell that `i2` is of type `MyInt`.

This is a type *assertion* not a *conversion*. Happens only at
runtime unlike latter which is compile-type. So use the comma-ok
pattern to catch the failure.

```go
func doThings(i interface{}) {
	switch j := i.(type) {
	case nil:
		// i is nil, type of j is interface{}
	case int:
		// j is of type int
	case MyInt:
		// j is of type MyInt
	case io.Reader:
		// j is of type io.Reader
	case bool, rune:
		// i is either bool or rune, so j is of type inteface{}
	default:
		// no idea what i is, so j is of type interface{}
	}
}
```

People usually shadow the variable i.e. `i := i.(type)`

In the above we had some estimates of the types. If you don't know the type at all, use Reflection.

### WebApp example

Too long to print here. [Here](https://gist.github.com/arunsrin/030f0818a6ead6c55243c15f190fa682) it is.

## Errors

Always return an `error` as the last return value. Simple
example:

```go
func calcRemainderAndMod(num, denom int) (int, int, error) {
	if denom == 0 {
		return 0, 0, errors.New("denom is 0")
	}
	return num / denom, num % denom, nil
}
```

!!!note
    No capitalization, punctuation, newlines in error strings.


Reasons for returning instead of throwing:
- Simpler code paths
- Force developers to check and handle natively since all
variables must be read in go

### Alternate way

Rather than `errors.New("some message")`, one can also do this:

```go
  fmt.ErrorF("%d isn't even", i)
```

### Sentinel Errors

Their names start with `Err` by convention, and indicate that
no further processing is possible.

Example: the `zip` package has `zip.ErrFormat`.

Once declared, it is part of the public API of your package.
So use carefully, or just pick one that's already there.

Looks messy actually, just don't do it.

### Adding more info

Since the error interface is just a string:

```go
type error interface {
  Error() string
}
```

You can extend it quite easily like so:

```go
struct MyError {
  StatusCode int
  Message string
}
```

And use it in your code like this:

```go
  return nil, MyError{
    StatusCode: 400,
    Message: fmt.Sprintf("bad request %s", uid)
  }
```

### Wrapping errors

You can chain your information to a downstream error using
`fmt.Errorf`'s `%w` verb.

On the receiving side you can unwrap with `errors.Unwrap`.
But you would'nt usually do this. Instead, use `errors.Is`
and `errors.As`.

Once you wrap something, you can't compare and check if a
certain Sentinel Error occurred. This is where `errors.Is`
helps. It iterates throught the error chain and tells you if
a match is found.

```go
  if err != nil {
    if errors.Is(err, os.ErrNotExist) {
      fmt.Println("That file doesn't exist")
    }
  }
```

You can also implement `Is()` in your custom Error Type and
do your own pattern matching implementation.

`errors.As` lets you check if a returned error matches a certain type.

```go
err := AFunctionThatReturnsAnError()
var myErr MyErr
if errors.As(err, &myErr) {
  fmt.Println(myErr.Code)
}
```

Second argument sould either be a pointer to an error, or a
pointer to an interface.

Don't use this unless you know what you're doing.

### panic and recover

When a panic happens:
- current function exits immediately
- all its defers run
- then all the defers of the calling function run, and so on
- finally when main is reached, the program exits with a message and stacktrace

You can call panic in your code, usually with a string.

```go
func main() {
	doPanic("goodbyeee")
}

func doPanic(msg string) {
	panic(msg)
}
```

You can call a `recover` inside a defer to halt the panic and continue execution.

In the following example, division by zero does not kill the
program, it continues to the next iteration:

```go
func main() {
	for _, val := range []int{1, 2, 0, 6} {
		div60(val)
	}
}

func div60(i int) {
	defer func() {
		if v := recover(); v != nil {
			fmt.Println(v)
		}
	}()
	fmt.Println(60 / i)
}
```

## Modules, Packages, Imports

Core concepts: 

- repositories - where in VCS you'd store your code
- modules - root of a Go library or app
- packages - modules consist of one or more of these

Modules should be globally unique, like Java's packages.
Convention is to have the repo e.g.
`github.com/arunsrin/blah`

Have a `go.mod` in the root directory to declare a module.
Use the `go mod` command to manage this file.

```sh
learninggo/ch09/my1stmodule ❯ go mod init github.com/arunsrin/example01/v2
go: creating new go.mod: module github.com/arunsrin/example01/v2
learninggo/ch09/my1stmodule via  v1.16.5 ❯ cat go.mod
module github.com/arunsrin/example01/v2

go 1.16
learninggo/ch09/my1stmodule via  v1.16.5 ❯
```

A `require` section declares your dependencies. E.g.

```go
require (
    github.com/learning-go-book/formatter v0.0.0-20200921021027-5abc380940ae
    github.com/shopspring/decimal v1.2.0
)
```

A `replace` section let's you override a module's location,
and an `exclude` section prevents a specific version from
being used.

### Packages

Say you have 2 packages, `formatter` and `math` in 2 subfolders in your module. Use them with the full path in your `main.go` like so:


```go
import (
    "fmt"

    "github.com/learning-go-book/package_example/formatter"
    "github.com/learning-go-book/package_example/math"
)
```

!!!warning
        However tempting it may be, don't use relative paths.

Your packages should declare the package name as the first
line, e.g. `package formatter`. Usually this is same as your
directory name.

Use good naming conventions:
- Bad: `util.ExtractNames`, `util.FormatNames`
- Good: `extract.Names`, `format.Names`

### Good module conventions

- Create a `cmd/` directory, with one sub-folder for each
binary built from the module.
- All other go code go into packages inside a `pkg/`
directory.

### Overrides

Example: Both `crypto/rand` and `math/rand` exist. So the equivalent of python's `import blah as blah2` is:

```go
import (
    crand "crypto/rand"
    "encoding/binary"
    "fmt"
    "math/rand"
)
```

### godoc

Place the comment above the thing being documented, with no
new lines in between.

Before the package declaration: package-level comments.

### internal Packages

When defines as `internal`, everything exported by that
Package is only visible to other sibling packages.

### init Function

Avoid. A function called `init()` with no parameters and
return values. Gets run the first time a package is
referenced by another.

### Check available versions of a module

```sh
go list -m -versions github.com/learning-go-book/simpletax
```

To downgrade to a specific version:

```sh
go get github.com/learning-go-book/simpletax@v1.0.0
```

### Major versions

For all versions apart from 0 and 1, the module path must end
in `vN` where `N` is the major version. E.g.

`"github.com/learning-go-book/simpletax/v2"`

In the code itself you can do one of these 2:
- Create a sub-directory called `v2` or whatever and copy
your README, LICENSE fiiles.
- Create a branch called `v2` or keep version 2 in master and
create a branch called `v1` for the legacy version.

### Vendoring

Keep copies of dependencies inside your module.

`go mod vendor`

### Module Proxy Server

go's mirror. First tries there, and downloads and caches if
not present.

Google also maintains a *sum database* that has version
information. Protects from malicious version modifications.

Alternates to this default behaviour:
- Use a different proxy server like JFrog's [GoCenter](https://gocenter.io)
	- To do this,`export
GOPROXY="https://gocenter.io,direct"`
- Disable the behaviour: `export GOPROXY=direct`
- Run your own

#### Private proxy servers

Set `GOPRIVATE`:

`export GOPRIVATE=*.example.com,company.com/repo`

Anything matching the above will be downloaded directly.

## Standard Library

Useful stuff from the standard library

`strconv.Atoi`: convert `"5"` to `5`

From `math/rand`: `rand.Intn(10)` returns a random number between 0 and 10. Seed is fixed though so look deeper

`os.Args` like python's `sys.argv`

## Third Party

Useful stuff from the ecosystem. Search in this page for details.

- `go install github.com/rakyll/hey@latest`
- `go install golang.org/x/tools/cmd/goimports@latest`
- `go install golang.org/x/lint/golint@latest`
- `go install golang.org/x/tools/go/analysis/passes/shadow/cmd/shadow@latest`

The equivalent of pypi here is [pkg.go.dev](https://pkg.go.dev). It automatically indexes open-source go projects.

## References

- Learning Go, by Jon Bodner

### Queued

- [official code review comments](https://github.com/golang/go/wiki/CodeReviewComments)
- [Effective Go](https://golang.org/doc/effective_go)

- [Inside the Map implementation, video](https://www.youtube.com/watch?v=Tl7mi9QmLns)


