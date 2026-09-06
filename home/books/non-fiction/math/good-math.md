---
title: "Good Math"
tags:
  - books
  - math
  - programming
---

# :material-pencil:{ .anim-rotate } Good Math

*Full Title:* Good Math: A Geek's Guide to the Beauty of Numbers, Logic, and Computation

*Author*: Mark C. Chu-Carroll

Here are some notes I took while reading this book. Overall I felt it
was interesting, but there were large jumps in difficulty in some of
the later chapters.

## Continuous fractions 
This was the most fascinating part of the book for me. I hadn't heard of these before!

For example, the square root of 2 in decimal form is approximately
1.4142135623730951. But if you represent it as a continued fraction,
you get [1; 2, 2, 2, 2, 2, …]. All of the square roots of integers
that are nonperfect squares have repeated forms in continued
fractions.

Interesting how continuous fractions give a new and clean way of
looking at previously confusing numbers like sqrt 2 and other
irrational numbers. Some nice parallels with how multiplication was
hard in the Roman numeral system but drastically improved in tha
arabic system.


Another great example is `e`. If you render `e` as a continued
fraction, you get `e` = [2; 1, 2, 1, 1, 4, 1, 1, 6, 1, 1, 8, 1, 1, 10,
1, 1, 12, 1, ...]. In this and many other cases, continued fractions
reveal the underlying structure of the numbers.

## First Order Predicate Logic

This chapter was not easy. But the section on prolog looked
neat. Every statement is essentially a proof that the language
satisfies.  Now we're into CTL i.e computational tree logic maybe?

FOPL has no notion of time, so it's not easy to make logical
statements and assertions with it when there is a time context e.g
employee (me, Cisco, 2020) is cumbersome.

FOPL is interesting because it allows us to reason with statements and
prove things without knowing a thing about the actual context. The
proofs come purely through logic.

Set theory plus FOPL form the foundations of maths.

### FOPL summary

In first-order predicate logic, we talk about two kinds of things:
`predicates` and `objects`. Objects are the things that we can reason
about using the logic; predicates are the things that we use to reason
about objects.

A `predicate` is a statement that says something about some object or
objects. We’ll write predicates as either uppercase letters or as
words starting with an uppercase letter (A,B,Married), and we’ll
write objects in quotes. 

Every predicate is followed by a list of comma-separated objects (or
variables representing objects).  One very important restriction is
that predicates are not objects. That’s why this is
called first-order predicate logic: you can’t use a predicate to make
a statement about another predicate. So you can’t say something
like `Transitive(GreaterThan)`: that’s a second-order statement, which
isn’t expressible in first-order logic.  We can combine logical
statements using AND (written `∧`) and OR (`∨`). We can negate a statement
by prefixing it with not (written `¬`). And we can introduce a variable
to a statement using two logical quantifiers: for all possible values
, and for at least one value.

## Naive set theory

This is what Cantor used for his diagonal trick to measure different
sizes of infinities, is limited by things like Russel's paradox. If
you use FOPL to make theories about naive sets, you eventually hit a
contradiction that challenges the foundations of logic. In summary It
allows you to create logically inconsistent self referential sets. The
next chapter has a better alternative: axiomatic set theory.

## Axiomatic Set Theory

It uses axioms to give a consistent form of set theory based on some
axioms. The one in this book is Zermelo-Frankel set theory with
choice, commonly abbreviated as ZFC.

First we define a set by asserting that 2 sets are equal if you pair
their objects and those are equal. Ths gives us a mechanism to get and
compare elements, and defines a set and it's main operations.

Once we define an empty set, we automatically get a new one which is
the set containing the empty set. Then you define an enumeration axiom
that allows you to append 2 sets.

Then the default infinite set is created, out of which other infinite
sets are derived. This axiom carefully ensures that these sets are not
self referential, thus avoiding paradoxes.


A powerset of A is the set of all possible subsets of A.

Using a powerset axiom, we now provide the ability to take an infinite
set and build a second order set that's larger than it.

Anyway once you have the final 'axiom of choice', you have this set
theory combined with fopl to create all of maths. Integers come
naturally.  Axiom of pairing can be used to get the rational
numbers. Dedekind cuts can be used to get the reals. And so on.

*Todo* add a note on what a dedekind cut is. From what I remember, you
can define 2 sets, one that has all elements lesser than `sqrt(2)` and
one that has all elements greater. That gives a clear definition for
`sqrt(2)` itself.

## Continuum hypothesis

The first infinite set larger than aleph0 (set of natural numbers) has
a size equal to aleph0's powerset (the set of all subsets of aleph0),
and this is also the size of all the reals.

Unfortunately it is neither true or false. You can treat it as either
and all of zfc maths will still work.

Here we have a hypothesis that is not provable, whereas in Russel's
paradox we had an inconsistency.

## Group theory

Last bit went over my head :(

## Mechanical math

Haskell code doesn't help :(


